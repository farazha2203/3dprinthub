from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .link_analysis_queue import claim_next_link_analysis_job, enqueue_link_analysis, process_link_analysis_job
from .link_intelligence import PermanentLinkAnalysisError
from .manual_review import ensure_manual_review, finish_review
from .models import (
    CustomerLinkAnalysis,
    CustomerNotification,
    LinkAnalysisManualReview,
)
from .realtime import operations_snapshot
from .services import notify


class Phase26ManualReviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase26-user", email="phase26@example.com", password="Pass123456"
        )
        self.other = get_user_model().objects.create_user(
            username="phase26-other", email="phase26-other@example.com", password="Pass123456"
        )
        self.analysis = CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url="https://example.com/model",
            normalized_url="https://example.com/model",
            source_domain="example.com",
            title="چرخ دنده فاز ۲۶",
        )

    def test_manual_review_is_deduplicated(self):
        first, created = ensure_manual_review(self.analysis, requested_by=self.user, customer_note="لطفاً بررسی شود")
        second, created_again = ensure_manual_review(self.analysis, requested_by=self.user, customer_note="توضیح تکمیلی")
        self.assertTrue(created)
        self.assertFalse(created_again)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(LinkAnalysisManualReview.objects.filter(analysis=self.analysis).count(), 1)

    def test_customer_can_request_review_only_for_own_analysis(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("store:external_link_manual_review", args=[self.analysis.public_token]),
            {"customer_note": "فایل برای قطعه خودرو است"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LinkAnalysisManualReview.objects.filter(analysis=self.analysis, requested_by=self.user).exists())
        self.client.force_login(self.other)
        response = self.client.post(reverse("store:external_link_manual_review", args=[self.analysis.public_token]))
        self.assertEqual(response.status_code, 404)

    @patch("store.services.notify")
    def test_finishing_review_notifies_owner_once(self, notify_mock):
        review, _ = ensure_manual_review(self.analysis, requested_by=self.user)
        finish_review(
            review,
            user=self.other,
            action="data_completed",
            note="اطلاعات بررسی و تکمیل شد.",
        )
        notify_mock.assert_called_once()
        finish_review(
            review,
            user=self.other,
            action="data_completed",
            note="ثبت دوباره نتیجه",
        )
        notify_mock.assert_called_once()

    @patch("store.link_analysis_queue.analyze_customer_link")
    def test_permanent_failure_creates_manual_review(self, analyze_mock):
        analyze_mock.side_effect = PermanentLinkAnalysisError("blocked by source")
        enqueue_link_analysis(self.analysis, max_attempts=1)
        job = claim_next_link_analysis_job(worker_id="phase26-test")
        result = process_link_analysis_job(job, worker_id="phase26-test")
        self.assertEqual(result.status, "failed")
        self.assertTrue(LinkAnalysisManualReview.objects.filter(analysis=self.analysis, reason="auto_failed").exists())


class Phase26RealtimeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="phase26-live", email="phase26-live@example.com", password="Pass123456"
        )

    @patch("store.realtime.publish_notification")
    def test_notification_creation_requests_realtime_publish(self, publish_mock):
        item = notify(self.user, "آماده شد", "تحلیل لینک کامل شد")
        self.assertIsInstance(item, CustomerNotification)
        publish_mock.assert_called_once_with(item.pk)

    def test_operations_snapshot_contains_manual_review_metrics(self):
        analysis = CustomerLinkAnalysis.objects.create(
            user=self.user,
            source_url="https://example.com/part",
            normalized_url="https://example.com/part",
            source_domain="example.com",
        )
        ensure_manual_review(analysis, requested_by=self.user)
        payload = operations_snapshot()
        self.assertEqual(payload["manual_review_pending"], 1)
        self.assertIn("active_workers", payload)

    def test_staff_snapshot_endpoint(self):
        staff = get_user_model().objects.create_superuser(
            username="phase26-admin", email="admin26@example.com", password="Pass123456"
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("store:link_operations_snapshot"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("queued", response.json())
