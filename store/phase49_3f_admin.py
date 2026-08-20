from __future__ import annotations

from django.contrib import admin

from .epic49_catalog_profile import ProductCatalogProfile


def _append_once(items, *names):
    output = list(items or [])
    for name in names:
        if name not in output:
            output.append(name)
    return output


def install() -> None:
    """Extend mature Admin registrations without replacing their implementations."""
    from website.models import Material

    # Product Catalog Profile admin is registered by epic49_catalog_admin.
    profile_admin = admin.site._registry.get(ProductCatalogProfile)
    if profile_admin is not None and not getattr(profile_admin, "_phase49_3f_admin_installed", False):
        profile_admin.list_display = _append_once(
            profile_admin.list_display,
            "pricing_strategy",
            "technical_summary_fa",
        )
        profile_admin.list_filter = _append_once(profile_admin.list_filter, "pricing_strategy")
        fieldsets = list(profile_admin.fieldsets or [])
        if not any(str(title) == "قیمت‌گذاری هوشمند 49.3F" for title, _opts in fieldsets):
            price_index = next(
                (index + 1 for index, (title, _opts) in enumerate(fieldsets) if str(title) == "قیمت"),
                3,
            )
            fieldsets.insert(
                price_index,
                (
                    "قیمت‌گذاری هوشمند 49.3F",
                    {
                        "fields": ["pricing_strategy", "pricing_inputs"],
                        "description": (
                            "قیمت قطعی یا محاسباتی محصول. pricing_inputs Snapshot ورودی‌های Catalog Center "
                            "مانند وزن قطعه/ساپورت، کیفیت‌ها و نرخ‌های ثبت‌شده را نگه می‌دارد."
                        ),
                    },
                ),
            )
        if not any(str(title) == "هوش فنی محصول 49.3F" for title, _opts in fieldsets):
            info_index = next(
                (index + 1 for index, (title, _opts) in enumerate(fieldsets) if str(title) == "اطلاعات فنی و SEO"),
                len(fieldsets),
            )
            fieldsets.insert(
                info_index,
                (
                    "هوش فنی محصول 49.3F",
                    {"fields": ["technical_summary_fa"]},
                ),
            )
        profile_admin.fieldsets = fieldsets
        profile_admin._phase49_3f_admin_installed = True

    # Material admin keeps the existing admin form, and adds the two runtime
    # rates directly to the list so an operator can keep costs current quickly.
    material_admin = admin.site._registry.get(Material)
    if material_admin is not None and not getattr(material_admin, "_phase49_3f_admin_installed", False):
        material_admin.list_display = _append_once(
            material_admin.list_display,
            "print_hourly_rate_toman",
            "supervision_hourly_rate_toman",
        )
        material_admin.list_editable = _append_once(
            material_admin.list_editable,
            "print_hourly_rate_toman",
            "supervision_hourly_rate_toman",
        )
        material_admin._phase49_3f_admin_installed = True
