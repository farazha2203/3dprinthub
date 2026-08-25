from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from .models import HomepageHeroSlide, SiteSetting


HOME_CANONICAL = "https://3dprinthub.ir/"


def _length_state(value: str, low: int, high: int) -> tuple[str, str]:
    size = len(str(value or "").strip())
    if low <= size <= high:
        return f"{size} کاراکتر", "#15803d"
    if size:
        return f"{size} کاراکتر — نیازمند بازبینی", "#b45309"
    return "خالی", "#b91c1c"


def install() -> None:
    site_admin = admin.site._registry.get(SiteSetting)
    if site_admin is None:
        return

    @admin.display(description="سلامت SEO صفحه اصلی")
    def homepage_seo_health(obj):
        if obj is None:
            return "—"
        title_text, title_color = _length_state(obj.meta_title, 30, 65)
        desc_text, desc_color = _length_state(obj.meta_description, 100, 170)
        return format_html(
            '<div style="line-height:1.9">'
            '<strong>Title:</strong> <span style="color:{}">{}</span><br>'
            '<strong>Description:</strong> <span style="color:{}">{}</span><br>'
            '<strong>Canonical:</strong> <code dir="ltr">{}</code>'
            '</div>',
            title_color,
            title_text,
            desc_color,
            desc_text,
            HOME_CANONICAL,
        )

    @admin.display(description="پیش‌نمایش نتیجه جستجو")
    def homepage_search_preview(obj):
        if obj is None:
            return "—"
        title = str(obj.meta_title or obj.brand_name or "3DPrintHub").strip()
        description = str(obj.meta_description or "").strip()
        return format_html(
            '<div dir="rtl" style="max-width:680px;padding:14px 16px;border:1px solid #dbe2ea;border-radius:14px;background:#fff">'
            '<div dir="ltr" style="font-size:12px;color:#166534">https://3dprinthub.ir/</div>'
            '<div style="font-size:20px;line-height:1.5;color:#1a0dab;margin:4px 0">{}</div>'
            '<div style="color:#4b5563;line-height:1.8">{}</div>'
            '</div>',
            title,
            description,
        )

    @admin.display(description="وضعیت اسلایدر و Alt تصاویر")
    def homepage_hero_seo_status(obj):
        active = HomepageHeroSlide.objects.filter(is_active=True)
        count = active.count()
        missing_alt = 0
        missing_title = 0
        for slide in active[:100]:
            if not str(getattr(slide, "effective_alt_text", "") or "").strip():
                missing_alt += 1
            if not str(getattr(slide, "effective_title", "") or "").strip():
                missing_title += 1
        color = "#15803d" if count and not missing_alt and not missing_title else "#b45309"
        return format_html(
            '<span style="color:{};font-weight:700">{} اسلاید فعال • {} بدون Alt • {} بدون عنوان</span>',
            color,
            count,
            missing_alt,
            missing_title,
        )

    site_admin.homepage_seo_health = homepage_seo_health
    site_admin.homepage_search_preview = homepage_search_preview
    site_admin.homepage_hero_seo_status = homepage_hero_seo_status

    readonly = list(getattr(site_admin, "readonly_fields", []) or [])
    for field in ("homepage_seo_health", "homepage_search_preview", "homepage_hero_seo_status"):
        if field not in readonly:
            readonly.append(field)
    site_admin.readonly_fields = readonly

    fieldsets = []
    replaced = False
    for title, options in getattr(site_admin, "fieldsets", ()):
        if title == "SEO":
            fieldsets.append((
                "SEO صفحه اصلی",
                {
                    "fields": (
                        "meta_title",
                        "meta_description",
                        "homepage_seo_health",
                        "homepage_search_preview",
                        "homepage_hero_seo_status",
                    ),
                    "description": (
                        "Title و Description صفحه اصلی از همین دو فیلد مدیریت می‌شوند. "
                        "عنوان/Alt/توضیح هر اسلاید از مدیریت اسلایدر و Product Catalog Profile کنترل می‌شود."
                    ),
                },
            ))
            replaced = True
        else:
            fieldsets.append((title, options))
    if not replaced:
        fieldsets.append((
            "SEO صفحه اصلی",
            {"fields": ("meta_title", "meta_description", "homepage_seo_health", "homepage_search_preview", "homepage_hero_seo_status")},
        ))
    site_admin.fieldsets = tuple(fieldsets)

    list_display = list(getattr(site_admin, "list_display", []) or [])
    if "homepage_seo_health" not in list_display:
        list_display.append("homepage_seo_health")
    site_admin.list_display = list_display
