from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .link_analysis_operations import (
    health_payload,
    register_worker,
    resolve_adapter_key,
    touch_worker,
)
from .link_analysis_queue import (
    claim_next_link_analysis_job,
    enqueue_link_analysis,
    process_link_analysis_job,
)
from .models import (
    CustomerLinkAnalysis,
    CustomerLinkAnalysisJob,
    CustomerNotification,
    LinkAnalysisAdapterPolicy,
    LinkAnalysisQueueControl,
    LinkAnalysisWorkerHeartbeat,
)


class Phase25AdapterPolicyTests(TestCase):
    def test_adapter_resolution(self):
        self.assertEqual(resolve_adapter_key(source_url="https://makerworld.com/en/models/1"), "makerworld")
        self.assertEqual(resolve_adapter_key(source_url="https://cdn.example.com/gear.stl"), "direct_file")
        self.assertEqual(resolve_adapter_key(source_url="https://example.com/product/gear"), "generic")

    def test_disabled_adapter_does_not_get_claimed(self):
        analysis = CustomerLinkAnalysis.objects.create(
            source_url="https://makerworld.com/en/models/1",
            normalized_url="https://makerworld.com/en/models/1",
            source_domain="makerworld.com",
        )
        job = enqueue_link_analysis(analysis)
        LinkAnalysisAdapterPolicy.objects.filter(adapter_key="makerworld").update(is_enabled=False)
        self.assertIsNone(claim_next_link_analysis_job(worker_id="test-worker"))
        job.refresh_from_db()
        self.assertEqual(job.progress_stage, "adapter_paused")


class Phase25QueueControlTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="phase25-user", email="p25@example.com", password="Pass123456")
        self.analysis = CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url="https://example.com/model",
            normalized_url="https://example.com/model",
            source_domain="example.com",
            title="چرخ دنده تست",
        )

    def test_global_pause_blocks_claim(self):
        enqueue_link_analysis(self.analysis)
        control = LinkAnalysisQueueControl.load()
        control.is_paused = True
        control.pause_reason = "maintenance"
        control.save()
        self.assertIsNone(claim_next_link_analysis_job(worker_id="test-worker"))

    @patch("store.link_analysis_queue.analyze_customer_link")
    def test_success_sends_customer_notification_once(self, analyze_mock):
        def fake_analyze(analysis, **kwargs):
            analysis.status = "ready"
            analysis.title = "چرخ دنده آماده"
            analysis.save(update_fields=["status", "title", "updated_at"])
            return analysis

        analyze_mock.side_effect = fake_analyze
        job = enqueue_link_analysis(self.analysis)
        claimed = claim_next_link_analysis_job(worker_id="test-worker")
        result = process_link_analysis_job(claimed, worker_id="test-worker")
        self.assertEqual(result.status, "completed")
        self.assertEqual(CustomerNotification.objects.filter(user=self.user, title__icontains="آماده").count(), 1)
        result = process_link_analysis_job(result, worker_id="test-worker")
        self.assertEqual(CustomerNotification.objects.filter(user=self.user, title__icontains="آماده").count(), 1)


class Phase25WorkerHealthTests(TestCase):
    def test_worker_heartbeat_and_health(self):
        heartbeat = register_worker("worker:test")
        touch_worker(heartbeat, status="idle", loop_increment=1)
        payload, status_code = health_payload()
        self.assertEqual(status_code, 200)
        self.assertGreaterEqual(payload["active_workers"], 1)

    def test_stale_worker_is_not_healthy(self):
        heartbeat = register_worker("worker:stale")
        LinkAnalysisWorkerHeartbeat.objects.filter(pk=heartbeat.pk).update(
            last_seen_at=timezone.now() - timedelta(minutes=10),
            status="running",
        )
        payload, status_code = health_payload()
        self.assertEqual(status_code, 503)
        self.assertEqual(payload["active_workers"], 0)

    @override_settings(LINK_WORKER_HEALTH_TOKEN="secret-health-token")
    def test_health_endpoint_requires_token(self):
        response = self.client.get(reverse("store:link_worker_health"))
        self.assertEqual(response.status_code, 404)
        heartbeat = register_worker("worker:http")
        touch_worker(heartbeat, status="idle")
        response = self.client.get(
            reverse("store:link_worker_health"),
            HTTP_X_HEALTH_TOKEN="secret-health-token",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
