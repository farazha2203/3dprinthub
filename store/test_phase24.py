from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from website.models import Material

from .link_analysis_queue import (
    enqueue_link_analysis,
    process_link_analysis_queue,
    release_stale_link_analysis_jobs,
)
from .link_intelligence import TransientLinkAnalysisError
from .models import (
    CustomerLinkAnalysis,
    CustomerLinkAnalysisAttempt,
    CustomerLinkAnalysisJob,
    PricingSetting,
)


SAMPLE_HTML = b'''<!doctype html><html><head>
<meta property="og:site_name" content="Model Lab">
<meta property="og:title" content="PETG Functional Bracket">
<meta property="og:description" content="Strong PETG bracket for industrial use">
<meta property="og:image" content="https://cdn.example.com/bracket.jpg">
<script type="application/ld+json">{
  "@type":"Product","name":"PETG Functional Bracket","description":"Strong PETG bracket",
  "image":"https://cdn.example.com/bracket.jpg",
  "additionalProperty":[
    {"name":"Filament weight","value":"84 g"},
    {"name":"Print time","value":"2 h 30 min"},
    {"name":"Material","value":"PETG"}
  ]
}</script></head><body><a href="/downloads/bracket.stl">download</a></body></html>'''


class Phase24QueueTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase24-user",
            email="phase24@example.com",
            password="StrongPass123!",
        )
        Material.objects.create(
            name="PETG",
            price_per_kg=1_000_000,
            sale_price_per_gram=1200,
            main_usage="قطعات کاربردی",
            sample_parts="براکت",
            is_active=True,
        )
        PricingSetting.objects.update_or_create(
            pk=1,
            defaults={
                "default_hourly_rate": 120_000,
                "default_labor_percent": 25,
                "minimum_order_amount": 50_000,
                "packaging_fee": 20_000,
            },
        )

    def make_analysis(self, suffix="model"):
        return CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url=f"https://public.example.com/{suffix}",
            normalized_url=f"https://public.example.com/{suffix}",
            source_domain="public.example.com",
        )

    def test_enqueue_creates_single_idempotent_job(self):
        analysis = self.make_analysis("queued")
        first = enqueue_link_analysis(analysis)
        second = enqueue_link_analysis(analysis)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(CustomerLinkAnalysisJob.objects.count(), 1)
        self.assertEqual(first.status, "queued")

    def test_worker_completes_analysis_and_records_attempt(self):
        analysis = self.make_analysis("bracket")
        enqueue_link_analysis(analysis)

        def fake_fetch(url, *, max_bytes, accept, timeout=20):
            if "image/" in accept:
                return b"GIF89a", "image/gif", "https://cdn.example.com/bracket.jpg"
            return SAMPLE_HTML, "text/html", "https://public.example.com/bracket"

        with (
            patch("store.link_intelligence._assert_public_host"),
            patch("store.link_intelligence._safe_fetch", side_effect=fake_fetch),
            patch("store.link_intelligence._cache_primary_image"),
        ):
            processed = process_link_analysis_queue(limit=1, worker_id="test-worker")

        self.assertEqual(len(processed), 1)
        analysis.refresh_from_db()
        job = analysis.job
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.progress_percent, 100)
        self.assertEqual(analysis.status, "ready")
        self.assertGreater(analysis.estimated_price, 0)
        attempt = CustomerLinkAnalysisAttempt.objects.get(job=job)
        self.assertEqual(attempt.status, "success")
        self.assertGreaterEqual(attempt.duration_ms, 0)

    def test_transient_failure_is_retried_with_backoff(self):
        analysis = self.make_analysis("temporary")
        enqueue_link_analysis(analysis, max_attempts=3)
        with patch(
            "store.link_analysis_queue.analyze_customer_link",
            side_effect=TransientLinkAnalysisError("temporary upstream timeout"),
        ):
            process_link_analysis_queue(limit=1, worker_id="retry-worker")
        analysis.refresh_from_db()
        job = analysis.job
        self.assertEqual(job.status, "retry")
        self.assertEqual(job.attempt_count, 1)
        self.assertGreater(job.next_run_at, timezone.now())
        self.assertEqual(analysis.status, "pending")
        self.assertEqual(job.attempts.get().status, "transient_failure")

    def test_permanent_failure_stops_queue(self):
        analysis = self.make_analysis("invalid")
        enqueue_link_analysis(analysis, max_attempts=3)
        with patch(
            "store.link_analysis_queue.analyze_customer_link",
            side_effect=ValidationError("unsupported content"),
        ):
            process_link_analysis_queue(limit=1, worker_id="failure-worker")
        analysis.refresh_from_db()
        job = analysis.job
        self.assertEqual(job.status, "failed")
        self.assertEqual(job.attempt_count, 1)
        self.assertEqual(job.attempts.get().status, "permanent_failure")

    def test_stale_running_job_is_released(self):
        analysis = self.make_analysis("stale")
        job = enqueue_link_analysis(analysis)
        CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
            status="running",
            locked_at=timezone.now() - timedelta(minutes=30),
            worker_id="dead-worker",
            attempt_count=1,
        )
        attempt = CustomerLinkAnalysisAttempt.objects.create(
            job=job,
            attempt_number=1,
            status="running",
            worker_id="dead-worker",
            started_at=timezone.now() - timedelta(minutes=30),
        )
        self.assertEqual(release_stale_link_analysis_jobs(stale_minutes=10), 1)
        job.refresh_from_db()
        attempt.refresh_from_db()
        self.assertEqual(job.status, "retry")
        self.assertEqual(job.worker_id, "")
        self.assertEqual(attempt.status, "transient_failure")
        self.assertEqual(attempt.error_type, "StaleWorkerLock")

    def test_force_requeue_preserves_attempt_history_without_number_collision(self):
        analysis = self.make_analysis("force-requeue")
        job = enqueue_link_analysis(analysis)
        CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
            status="completed",
            attempt_count=1,
            progress_percent=100,
        )
        CustomerLinkAnalysisAttempt.objects.create(
            job=job,
            attempt_number=1,
            status="success",
            completed_at=timezone.now(),
        )
        job = enqueue_link_analysis(analysis, force=True)
        self.assertEqual(job.attempt_count, 0)

        with patch(
            "store.link_analysis_queue.analyze_customer_link",
            side_effect=lambda current, **kwargs: self._mark_ready(current),
        ):
            process_link_analysis_queue(limit=1, worker_id="force-worker")

        job.refresh_from_db()
        self.assertEqual(job.status, "completed")
        self.assertEqual(
            list(job.attempts.order_by("attempt_number").values_list("attempt_number", flat=True)),
            [1, 2],
        )

    @staticmethod
    def _mark_ready(analysis):
        analysis.status = "ready"
        analysis.save(update_fields=["status", "updated_at"])
        return analysis

    def test_status_api_is_private_and_reports_progress(self):
        analysis = self.make_analysis("status")
        job = enqueue_link_analysis(analysis)
        CustomerLinkAnalysisJob.objects.filter(pk=job.pk).update(
            progress_percent=42,
            progress_stage="parsing",
            progress_message="extracting",
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("store:external_link_analysis_status", args=[analysis.public_token]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["progress_percent"], 42)
        self.assertEqual(payload["job_status"], "queued")


class Phase24SubmissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase24-submit-user",
            email="phase24-submit@example.com",
            password="StrongPass123!",
        )

    def test_anonymous_submit_redirects_to_login_without_creating_analysis(self):
        response = self.client.post(
            reverse("store:external_link_analyzer"),
            {"source_url": "https://public.example.com/product"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("website:customer_login"), response.url)
        self.assertFalse(CustomerLinkAnalysis.objects.exists())

    def test_authenticated_submit_queues_without_running_remote_fetch_in_request(self):
        self.client.force_login(self.user)
        with patch(
            "store.link_intelligence._assert_public_host",
            side_effect=AssertionError("DNS must run in the worker, not in the web request"),
        ):
            response = self.client.post(
                reverse("store:external_link_analyzer"),
                {"source_url": "https://public.example.com/product"},
            )
        self.assertEqual(response.status_code, 302)
        analysis = CustomerLinkAnalysis.objects.get(user=self.user)
        self.assertEqual(analysis.status, "pending")
        self.assertEqual(analysis.job.status, "queued")
        self.assertEqual(CustomerLinkAnalysisAttempt.objects.count(), 0)
