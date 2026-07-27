from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from website.models import SiteSetting


class Command(BaseCommand):
    help = "Audit production deployment requirements without changing data."

    def add_arguments(self, parser):
        parser.add_argument("--json", action="store_true", dest="as_json")
        parser.add_argument("--strict", action="store_true")

    def handle(self, *args, **options):
        checks: list[dict[str, str]] = []

        def add(key: str, ok: bool, message: str, level: str = "error") -> None:
            status = "ok" if ok else level
            checks.append({"key": key, "status": status, "message": message})

        add("debug", not settings.DEBUG, "DJANGO_DEBUG باید در سرور صفر باشد.")
        add(
            "secret_key",
            bool(settings.SECRET_KEY and "unsafe-development" not in settings.SECRET_KEY),
            "DJANGO_SECRET_KEY باید طولانی، تصادفی و خارج از سورس باشد.",
        )
        add(
            "allowed_hosts",
            bool(settings.ALLOWED_HOSTS) and "*" not in settings.ALLOWED_HOSTS,
            "DJANGO_ALLOWED_HOSTS باید دامنه‌های واقعی را داشته باشد و شامل * نباشد.",
        )
        add(
            "csrf_origins",
            any(str(origin).startswith("https://") for origin in settings.CSRF_TRUSTED_ORIGINS),
            "DJANGO_CSRF_TRUSTED_ORIGINS باید دامنه HTTPS تولید را شامل شود.",
        )
        add(
            "database",
            connection.vendor not in {"sqlite", "unknown"},
            f"پایگاه داده فعلی {connection.vendor} است؛ برای Production از MySQL یا PostgreSQL استفاده شود.",
        )
        smtp_configured = (
            "smtp" in str(settings.EMAIL_BACKEND).lower()
            and bool(getattr(settings, "EMAIL_HOST", ""))
            and bool(getattr(settings, "DEFAULT_FROM_EMAIL", ""))
        )
        add(
            "email",
            smtp_configured,
            "SMTP واقعی برای بازیابی رمز و اعلان‌ها تنظیم شود؛ سپس test_smtp_delivery اجرا شود.",
        )
        add(
            "google_oauth",
            bool(getattr(settings, "GOOGLE_OAUTH_ENABLED", False)),
            "Client ID و Secret گوگل در محیط تولید تنظیم شوند.",
            level="warning",
        )
        realtime_mode = getattr(settings, "REALTIME_BACKEND_MODE", "")
        polling_only = bool(getattr(settings, "REALTIME_ALLOW_POLLING_ONLY", False))
        add(
            "redis",
            realtime_mode == "redis" or (polling_only and realtime_mode == "polling"),
            "برای VPS از Redis استفاده شود؛ روی Passenger/cPanel حالت Polling باید صریحاً فعال باشد.",
        )
        add(
            "worker_health_token",
            len(getattr(settings, "LINK_WORKER_HEALTH_TOKEN", "")) >= 24,
            "LINK_WORKER_HEALTH_TOKEN حداقل ۲۴ کاراکتر تصادفی باشد.",
        )

        gateway_enabled = bool(getattr(settings, "PAYMENT_GATEWAY_ENABLED", False))
        try:
            site_setting = SiteSetting.objects.first()
        except Exception:
            site_setting = None
        if gateway_enabled:
            add(
                "payment_merchant",
                bool(getattr(settings, "ZARINPAL_MERCHANT_ID", "")),
                "ZARINPAL_MERCHANT_ID باید فقط در .env سرور تنظیم شود.",
            )
            add(
                "payment_site_toggle",
                bool(site_setting and site_setting.online_payment_enabled),
                "پس از تست Sandbox، درگاه آنلاین باید در تنظیمات سایت نیز فعال شود.",
            )
            add(
                "payment_currency",
                getattr(settings, "ZARINPAL_CURRENCY", "IRT") in {"IRT", "IRR"},
                "واحد درگاه باید IRT یا IRR باشد.",
            )
            add(
                "payment_live_mode",
                not bool(getattr(settings, "ZARINPAL_SANDBOX", False)),
                "برای دریافت وجه واقعی، ZARINPAL_SANDBOX باید صفر باشد.",
            )
        else:
            add(
                "payment_gateway",
                False,
                "پرداخت آنلاین هنوز غیرفعال است؛ برای Staging قابل قبول و برای افتتاح تجاری نیازمند فعال‌سازی پس از تست است.",
                level="warning",
            )

        static_root = Path(settings.STATIC_ROOT)
        media_root = Path(settings.MEDIA_ROOT)
        private_root = Path(settings.PRIVATE_MEDIA_ROOT)
        add("static_root", static_root.is_absolute(), f"STATIC_ROOT: {static_root}")
        add("media_root", media_root.is_absolute(), f"MEDIA_ROOT: {media_root}")
        add(
            "private_media",
            private_root.is_absolute() and private_root != media_root and private_root not in media_root.parents,
            f"PRIVATE_MEDIA_ROOT باید جدا از مسیر عمومی Media باشد: {private_root}",
        )

        try:
            executor = MigrationExecutor(connection)
            pending = executor.migration_plan(executor.loader.graph.leaf_nodes())
            add("migrations", not pending, f"{len(pending)} Migration در انتظار اجرا است.")
        except Exception as exc:  # pragma: no cover - depends on deployment database
            add("migrations", False, f"بررسی Migration ممکن نشد: {type(exc).__name__}: {exc}")

        try:
            site = Site.objects.get(pk=settings.SITE_ID)
            valid_domain = bool(site.domain and site.domain not in {"example.com", "localhost"})
            add("django_site", valid_domain, f"دامنه django.contrib.sites: {site.domain}")
        except Exception as exc:
            add("django_site", False, f"رکورد Site قابل بررسی نیست: {type(exc).__name__}: {exc}")

        errors = [item for item in checks if item["status"] == "error"]
        warnings = [item for item in checks if item["status"] == "warning"]
        result = {
            "ready": not errors,
            "errors": len(errors),
            "warnings": len(warnings),
            "checks": checks,
        }

        if options["as_json"]:
            self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            symbols = {"ok": "[OK]", "warning": "[WARN]", "error": "[FAIL]"}
            for item in checks:
                self.stdout.write(f"{symbols[item['status']]} {item['key']}: {item['message']}")
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS("Production readiness checks passed.")
                if result["ready"]
                else self.style.WARNING(
                    f"Deployment is not ready: {len(errors)} blocking issue(s), {len(warnings)} warning(s)."
                )
            )

        if options["strict"] and errors:
            raise SystemExit(1)
