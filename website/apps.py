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

        # Phase 49.2B: Store/Product-backed hero fallbacks and SEO prefill.
        from . import phase49_2b_hero_hotfix  # noqa: F401

        # Phase 49.2C: persistent album image relation, cinematic timing/effects,
        # product album browser and edit-friendly Admin Studio. Migration 0020 owns
        # the real database columns; this module installs the matching runtime fields.
        from . import phase49_2c_hero_studio  # noqa: F401

        # Phase 49.3B: product-friendly Hero media presentation. Migration 0022 owns
        # scale/background/max-size columns while this runtime extends the mature
        # HomepageHeroSlide model and Admin without rewriting the large models file.
        from . import phase49_3b_hero_media  # noqa: F401

        # Epic49 unified: optimistic revision + edit source/operator contract must
        # load after the Hero Studio so it can extend that already-registered admin.
        from . import phase49_unified_sync  # noqa: F401

        # Phase49.3B: after the unified Admin revision/mirror wrapper is installed,
        # mirror Hero fit/scale/background edits back to ProductCatalogProfile too.
        from . import phase49_3b_profile_media_mirror  # noqa: F401

        # Epic49 Persian Sales Hero: public Hero copy must come from approved Persian
        # Windows/Product SEO and never from English/raw source-cookie boilerplate.
        from . import phase49_persian_sales_hero  # noqa: F401

        # Phase49.3I.30: Production intentionally exposes Product-owned Store media,
        # not the ImportedPrintAsset working-gallery namespace. Resolve Hero images
        # to the Product-owned copy after all older Hero composition layers load.
        from . import phase49_3i30_hero_media_ownership  # noqa: F401

        # Phase50.A: organize mature Sales/Treasury/Finance/Purchasing/Admin surfaces
        # without introducing accounting schema or touching healthy commerce flows.
        from .phase50a_admin_command_center import install_admin_completeness
        install_admin_completeness()

        # Phase50.A.1: expose mature Product/Hero controls in Django Admin too.
        # No schema change: Windows and web-admin both operate on the same
        # Product/ImportedPrintAsset/HomepageHeroSlide contracts.
        from .phase50a_storefront_admin_parity import install_storefront_admin_parity
        install_storefront_admin_parity()

        # Phase50.A.1C: make existing homepage Title/Description and Hero SEO state
        # visible as one professional Admin audit surface. No duplicate SEO model.
        from .phase50_home_seo_admin import install as install_phase50_home_seo_admin
        install_phase50_home_seo_admin()

        # Register social-auth profile hooks only after Django has loaded apps.
        from . import checks, signals  # noqa: F401
