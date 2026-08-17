import json

from django.apps import AppConfig
from django.utils.safestring import mark_safe


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

        # Phase 49.2A: older home-view generations still call the Phase 14 schema
        # helper before rendering. Replace that helper at runtime so a managed hero
        # slide can never reverse the retired external_catalog_detail route. The
        # public page keeps only the still-valid ProfessionalService schema.
        from . import views

        def _phase49_2a_presentation_schema(request, hero_assets, team_members):
            employees = [
                {
                    "@type": "Person",
                    "name": member.name,
                    "jobTitle": member.role,
                    "description": member.short_bio,
                }
                for member in team_members
            ]
            payload = {
                "@context": "https://schema.org",
                "@type": "ProfessionalService",
                "name": "3DprintHub.ir",
                "url": request.build_absolute_uri("/"),
                "employee": employees,
                "knowsAbout": [
                    "چاپ سه‌بعدی صنعتی",
                    "مهندسی معکوس",
                    "طراحی CAD",
                    "انتخاب متریال مهندسی",
                    "ساخت قطعات سفارشی",
                ],
            }
            return mark_safe(json.dumps(payload, ensure_ascii=False))

        views._phase14_presentation_schema = _phase49_2a_presentation_schema

        # Register social-auth profile hooks only after Django has loaded apps.
        from . import checks, signals  # noqa: F401
