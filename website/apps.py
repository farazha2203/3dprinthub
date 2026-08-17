from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "website"

    def ready(self):
        # Phase 49.2A: the public order flow no longer accepts external ready-catalog
        # models. Historical records remain valid; only new customer intake is disabled.
        from .models import OrderIntakeDetail

        OrderIntakeDetail.REQUEST_MODE_CHOICES = [
            choice
            for choice in OrderIntakeDetail.REQUEST_MODE_CHOICES
            if choice[0] != "ready_catalog"
        ]

        # Register social-auth profile hooks only after Django has loaded apps.
        from . import checks, signals  # noqa: F401
