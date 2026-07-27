from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.urls import NoReverseMatch, reverse

from django_smartbase_admin.admin.site import sb_admin_site


REQUIRED_APPS = (
    "django_smartbase_admin",
    "django_smartbase_admin.audit",
    "django_smartbase_admin.messaging",
    "easy_thumbnails",
    "widget_tweaks",
    "ckeditor",
    "ckeditor_uploader",
    "nested_admin",
    "django.contrib.postgres",
    "polymorphic",
    "filer",
    "django_htmx",
    "smartbase_admin_bridge.apps.SmartBaseAdminBridgeConfig",
)

REQUIRED_STATIC = (
    "sb_admin/dist/main.js",
    "sb_admin/dist/main_style.css",
    "sb_admin/dist/table.js",
    "sb_admin/dist/chart.js",
    "sb_admin/dist/dashboard_group.js",
    "sb_admin/dist/modal_view.js",
    "sb_admin/dist/permission_tree.js",
    "sb_admin/dist/tree_widget.js",
    "sb_admin/dist/tree_widget_style.css",
    "smartbase_admin_bridge/css/rtl.css",
    "sb_admin/images/logo.svg",
    "sb_admin/images/logo_light.svg",
)

REQUIRED_TEMPLATES = (
    "sb_admin/sb_admin_base_no_sidebar.html",
    "sb_admin/sb_admin_base.html",
    "sb_admin/actions/list.html",
    "sb_admin/actions/change_form.html",
    "sb_admin/actions/dashboard.html",
    "sb_admin/includes/components.html",
    "smartbase_admin_bridge/dashboard_overview.html",
)


class Command(BaseCommand):
    help = "Verify SmartBase Admin package, assets, templates and registrations."

    def handle(self, *args, **options):
        failures: list[str] = []

        try:
            package_version = version("django-smartbase-admin")
        except PackageNotFoundError:
            package_version = "not-installed"
            failures.append("django-smartbase-admin package is not installed")

        self.stdout.write(f"SmartBase version: {package_version}")
        self.stdout.write(f"Django DEBUG: {settings.DEBUG}")
        self.stdout.write(
            f"Registered SmartBase models: {len(sb_admin_site._registry)}"
        )

        installed = set(settings.INSTALLED_APPS)
        for app in REQUIRED_APPS:
            if app not in installed:
                failures.append(f"missing INSTALLED_APPS entry: {app}")

        for asset in REQUIRED_STATIC:
            found = finders.find(asset)
            if not found:
                failures.append(f"missing static asset: {asset}")
            else:
                self.stdout.write(f"STATIC OK: {asset}")

        for template in REQUIRED_TEMPLATES:
            try:
                get_template(template)
            except Exception as exc:
                failures.append(f"template {template}: {exc}")
            else:
                self.stdout.write(f"TEMPLATE OK: {template}")

        try:
            root_url = reverse("sb_admin:sb_admin_base")
            self.stdout.write(f"SmartBase root URL: {root_url}")
        except NoReverseMatch as exc:
            failures.append(f"SmartBase root URL is not registered: {exc}")

        if settings.DEBUG:
            try:
                components_url = reverse("sb_admin:components")
                self.stdout.write(
                    f"Components gallery URL: {components_url}"
                )
            except NoReverseMatch as exc:
                failures.append(f"components URL missing: {exc}")

        try:
            import django_smartbase_admin

            package_root = Path(django_smartbase_admin.__file__).resolve().parent
            static_root = package_root / "static" / "sb_admin"
            static_count = sum(1 for path in static_root.rglob("*") if path.is_file())
            self.stdout.write(f"Official package static files: {static_count}")
            if static_count < 600:
                failures.append(
                    f"official static asset count is too low: {static_count}"
                )
        except Exception as exc:
            failures.append(f"could not inspect package static files: {exc}")

        if not sb_admin_site._registry:
            failures.append("no project models are registered in sb_admin_site")

        if failures:
            for failure in failures:
                self.stderr.write(self.style.ERROR(f"FAIL: {failure}"))
            raise CommandError(
                f"SmartBase verification failed with {len(failures)} issue(s)."
            )

        self.stdout.write(self.style.SUCCESS("SMARTBASE VERIFY: OK"))
