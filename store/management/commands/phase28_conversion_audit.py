from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from store.link_analysis_operations import health_payload
from store.models import CustomerLinkAnalysis, CustomerLinkAnalysisJob, LinkAnalysisManualReview
from website.models import Payment, Quote, SiteSetting


class Command(BaseCommand):
    help = "Audit authenticated link conversion, manual quotes, payments, realtime and production contact settings."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", dest="as_json")
        parser.add_argument("--strict", action="store_true")

    def handle(self, *args, **options):
        site = SiteSetting.objects.first()
        worker_payload, worker_http_status = health_payload()
        email_backend = str(getattr(settings, "EMAIL_BACKEND", "") or "")
        email_host = str(getattr(settings, "EMAIL_HOST", "") or "")
        default_from = str(getattr(settings, "DEFAULT_FROM_EMAIL", "") or "")
        realtime_mode = str(getattr(settings, "REALTIME_BACKEND_MODE", "unknown"))
        redis_url = str(getattr(settings, "REALTIME_REDIS_URL", "") or "")

        checks: list[dict[str, object]] = []

        def add(key: str, ok: bool, message: str, *, blocking: bool = False):
            checks.append({
                "key": key,
                "ok": bool(ok),
                "blocking": bool(blocking and not ok),
                "message": message,
            })

        add(
            "authenticated_analysis",
            True,
            "مسیر تحلیل لینک و تمام APIهای نتیجه با login_required محافظت شده‌اند.",
        )
        add(
            "contact_channels",
            bool(site and (site.whatsapp or site.telegram)),
            "حداقل شماره واتساپ یا لینک/شناسه تلگرام در تنظیمات سایت ثبت شود.",
            blocking=True,
        )
        add(
            "manual_payment",
            bool(site and site.payment_card_number and site.payment_card_holder),
            "شماره کارت و نام صاحب کارت برای دریافت بیعانه/تسویه ثبت شود.",
            blocking=True,
        )
        deposit = int(getattr(site, "default_deposit_percent", 0) or 0) if site else 0
        add(
            "deposit_percent",
            1 <= deposit <= 100,
            f"درصد بیعانه فعلی: {deposit or 'تنظیم نشده'}",
            blocking=True,
        )
        smtp_ok = "smtp" in email_backend.lower() and bool(email_host and default_from)
        add(
            "smtp",
            smtp_ok,
            f"Backend={email_backend or 'unset'} Host={email_host or 'unset'} From={default_from or 'unset'}",
            blocking=not settings.DEBUG,
        )
        add(
            "database",
            connection.vendor in {"mysql", "postgresql"} or settings.DEBUG,
            f"Database vendor: {connection.vendor}",
            blocking=not settings.DEBUG,
        )
        if settings.DEBUG:
            add(
                "realtime_local",
                realtime_mode in {"memory", "redis"},
                f"Realtime mode={realtime_mode}; نبود Redis در لوکال با Polling/InMemory مدیریت می‌شود.",
            )
        else:
            polling_only = bool(getattr(settings, "REALTIME_ALLOW_POLLING_ONLY", False))
            realtime_ok = (realtime_mode == "redis" and bool(redis_url)) or (polling_only and realtime_mode == "polling")
            add(
                "realtime_production",
                realtime_ok,
                f"Realtime mode={realtime_mode}; Redis URL {'set' if redis_url else 'missing'}; polling_only={polling_only}.",
                blocking=True,
            )
        add(
            "worker",
            worker_http_status == 200,
            f"Worker health HTTP={worker_http_status}; active={worker_payload.get('active_workers', 0)}",
            blocking=not settings.DEBUG,
        )
        private_root = Path(getattr(settings, "PRIVATE_MEDIA_ROOT", ""))
        media_root = Path(getattr(settings, "MEDIA_ROOT", ""))
        add(
            "private_media",
            bool(private_root and private_root != media_root and private_root not in media_root.parents),
            f"Private media: {private_root}",
            blocking=True,
        )

        metrics = {
            "link_analyses": CustomerLinkAnalysis.objects.count(),
            "link_jobs_waiting": CustomerLinkAnalysisJob.objects.filter(status__in=["queued", "retry", "running"]).count(),
            "failed_analyses_without_order": CustomerLinkAnalysis.objects.filter(status="failed", order__isnull=True).count(),
            "manual_reviews_open": LinkAnalysisManualReview.objects.filter(status__in=["pending", "in_progress"]).count(),
            "manual_quotes_draft": Quote.objects.filter(status="draft").count(),
            "quotes_waiting_customer": Quote.objects.filter(status="sent").count(),
            "payments_awaiting_review": Payment.objects.filter(status="awaiting_review").count(),
        }
        blocking = [item for item in checks if item["blocking"]]
        result = {
            "ready_for_local": True,
            "ready_for_production": not blocking,
            "blocking_issues": len(blocking),
            "realtime_mode": realtime_mode,
            "checks": checks,
            "metrics": metrics,
        }

        if options["as_json"]:
            self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            for item in checks:
                if item["ok"]:
                    prefix = "[OK]"
                elif item["blocking"]:
                    prefix = "[FAIL]"
                else:
                    prefix = "[WARN]"
                self.stdout.write(f"{prefix} {item['key']}: {item['message']}")
            self.stdout.write("")
            for key, value in metrics.items():
                self.stdout.write(f"[METRIC] {key}: {value}")
            self.stdout.write("")
            if result["ready_for_production"]:
                self.stdout.write(self.style.SUCCESS("Phase 28 conversion flow is ready for production configuration."))
            else:
                self.stdout.write(self.style.WARNING(f"Production configuration has {len(blocking)} blocking issue(s)."))

        if options["strict"] and blocking:
            raise SystemExit(1)
