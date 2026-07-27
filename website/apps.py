from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "website"

    def ready(self):
        # Register social-auth profile hooks only after Django has loaded apps.
        from . import checks, signals  # noqa: F401
