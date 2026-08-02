from datetime import timedelta
import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .automation_watchdog import (
    expire_stale_automation,
    stop_catalog_run,
    stop_source_log,
)
from .catalog_site_adapters.common import CatalogCandidate
from .catalog_sync import sync_catalog_source
from .models import (
    CatalogSourcePolicy,
    CatalogSyncRun,
    ExternalSourceFetchLog,
    PrintCatalogSource,
)
from .source_monitoring import source_log, update_log


class Phase33AutomationWatchdogTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="phase33-admin",
            email="phase33@example.com",
            password="test-password-123",
        )
        self.source = PrintCatalogSource.objects.create(
            name="Phase 33 Source",
            code="phase33-source",
            base_url="https://example.com/",
            allowed_domains="example.com",
            request_timeout_seconds=2,
        )
        CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="custom",
            public_display_policy="source_link_only",
            discovery_mode="public_html",
        )

    def test_stale_source_log_is_finalized(self):
        now = timezone.now()
        log = ExternalSourceFetchLog.objects.create(
            source_key="bambu",
            action="sync",
            status="running",
            started_at=now - timedelta(hours=2),
            heartbeat_at=now - timedelta(hours=2),
            deadline_at=now - timedelta(minutes=1),
        )
        summary = expire_stale_automation(now=now)
        log.refresh_from_db()
        self.assertEqual(summary["source_stopped"], 1)
        self.assertEqual(log.status, "failed")
        self.assertEqual(log.current_stage, "deadline_exceeded")
        self.assertEqual(log.progress_percent, 100)
        self.assertIsNotNone(log.finished_at)

    def test_operator_can_cancel_source_log(self):
        now = timezone.now()
        log = ExternalSourceFetchLog.objects.create(
            source_key="printables",
            action="sync",
            status="running",
            started_at=now,
            heartbeat_at=now,
            deadline_at=now + timedelta(hours=1),
        )
        changed = stop_source_log(
            log,
            reason="OperatorCancelled: test",
            actor=self.user,
            now=now,
        )
        log.refresh_from_db()
        self.assertTrue(changed)
        self.assertEqual(log.status, "cancelled")
        self.assertIsNotNone(log.cancelled_at)

    def test_stale_catalog_run_is_finalized(self):
        now = timezone.now()
        run = CatalogSyncRun.objects.create(
            source=self.source,
            status="running",
            requested_limit=10,
            started_at=now - timedelta(hours=3),
            heartbeat_at=now - timedelta(hours=3),
            deadline_at=now - timedelta(minutes=1),
        )
        summary = expire_stale_automation(now=now)
        run.refresh_from_db()
        self.assertEqual(summary["catalog_stopped"], 1)
        self.assertEqual(run.status, "failed")
        self.assertIsNotNone(run.finished_at)

    def test_operator_can_cancel_catalog_run(self):
        now = timezone.now()
        run = CatalogSyncRun.objects.create(
            source=self.source,
            status="queued",
            requested_limit=10,
            deadline_at=now + timedelta(minutes=30),
        )
        changed = stop_catalog_run(
            run,
            reason="OperatorCancelled: test",
            actor=self.user,
            now=now,
        )
        run.refresh_from_db()
        self.assertTrue(changed)
        self.assertEqual(run.status, "cancelled")
        self.assertIsNotNone(run.cancelled_at)

    @mock.patch.dict(os.environ, {"AUTOMATION_TGJU_TEST_TIMEOUT_MINUTES": ""})
    @override_settings(AUTOMATION_SOURCE_TIMEOUTS={"tgju:test": 3})
    def test_source_context_sets_deadline_and_heartbeat(self):
        with source_log(source_key="tgju", action="test", actor=self.user) as log:
            update_log(log, stage="network", progress=50, records_found=1)
        log.refresh_from_db()
        self.assertEqual(log.status, "success")
        self.assertEqual(log.progress_percent, 100)
        self.assertIsNotNone(log.deadline_at)
        self.assertIsNotNone(log.heartbeat_at)
        self.assertIsNotNone(log.finished_at)
        self.assertEqual(log.details.get("timeout_minutes"), 3)

    def test_partial_sync_status_is_not_overwritten_by_persisted_running_state(self):
        class FakeAdapter:
            def discover(self, *, limit, sort_mode):
                return [
                    CatalogCandidate(
                        url="https://example.com/models/partial-status",
                        external_id="partial-status",
                        summary={
                            "title": "Partial Status Model",
                            "images": ["https://example.com/partial.jpg"],
                        },
                    )
                ]

            def fetch_record(self, candidate, *, hydrate_files=False):
                raise RuntimeError("detail endpoint blocked")

        with mock.patch(
            "store.catalog_sync.get_source_adapter",
            return_value=FakeAdapter(),
        ):
            run = sync_catalog_source(source=self.source, requested_limit=1)

        run.refresh_from_db()
        self.assertEqual(run.status, "partial")
        self.assertEqual(run.imported_count, 1)
        self.assertEqual(run.failed_count, 1)
        self.assertIsNotNone(run.finished_at)

    def test_admin_watchdog_endpoint_requires_post_and_stops_stale_rows(self):
        self.client.force_login(self.user)
        now = timezone.now()
        log = ExternalSourceFetchLog.objects.create(
            source_key="bambu",
            action="sync",
            status="running",
            started_at=now - timedelta(hours=2),
            deadline_at=now - timedelta(minutes=1),
        )
        url = reverse("admin:store_catalogautomationdashboard_stop_stale")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        log.refresh_from_db()
        self.assertEqual(log.status, "running")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        log.refresh_from_db()
        self.assertEqual(log.status, "failed")


class Phase33AdminTypographyTests(TestCase):
    def test_admin_font_css_exists_and_targets_sidebar(self):
        path = finders.find("admin/master-django.css")
        self.assertTrue(path)
        content = open(path, encoding="utf-8").read()
        self.assertIn('font-family:"IRANSans"', content)
        self.assertIn(".app-menu .navbar-nav .nav-link", content)
        self.assertIn("/static/fonts/iransans/IRANSansWeb_FaNum.woff", content)

    def test_smartbase_font_css_exists(self):
        path = finders.find("smartbase_admin_bridge/css/rtl.css")
        self.assertTrue(path)
        content = open(path, encoding="utf-8").read()
        self.assertIn("#main-navigation", content)
        self.assertIn('font-family:"IRANSans"', content)
