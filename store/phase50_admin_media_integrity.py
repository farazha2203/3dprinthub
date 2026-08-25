from __future__ import annotations

from pathlib import PurePosixPath

from django.contrib import admin
from django.utils.html import format_html

from .models import ImportedPrintAsset, ImportedPrintAssetImage, Product


def _extend(current, additions):
    result = list(current or [])
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def _basename(field_file) -> str:
    try:
        return PurePosixPath(str(field_file.name or "")).name
    except Exception:
        return ""


def _http_url(value) -> str:
    text = str(value or "").strip()
    return text if text.startswith(("https://", "http://")) else ""


def _product_gallery_match(product: Product | None, filename: str) -> str:
    if product is None or not filename:
        return ""
    try:
        for row in product.images.all():
            if _basename(row.image) == filename and row.image:
                return str(row.image.url or "")
    except Exception:
        return ""
    return ""


def _product_main_url(product: Product | None) -> str:
    if product is None:
        return ""
    try:
        return str(product.main_image.url or "") if product.main_image else ""
    except Exception:
        return ""


def public_asset_image(asset: ImportedPrintAsset | None) -> tuple[str, str]:
    """Resolve an Admin preview without exposing imported working-media paths."""
    if asset is None:
        return "", "ناموجود"
    product = getattr(asset, "product", None)
    filename = _basename(getattr(asset, "preview_image", None))
    matched = _product_gallery_match(product, filename)
    if matched:
        return matched, "گالری عمومی محصول"
    main = _product_main_url(product)
    if main:
        return main, "تصویر اصلی محصول"
    remote = _http_url(getattr(asset, "remote_image_url", ""))
    if remote:
        return remote, "تصویر منبع"
    try:
        first = asset.images.order_by("sort_order", "id").first()
    except Exception:
        first = None
    if first is not None:
        return public_imported_image(first)
    return "", "ناموجود"


def public_imported_image(row: ImportedPrintAssetImage | None) -> tuple[str, str]:
    if row is None:
        return "", "ناموجود"
    asset = getattr(row, "asset", None)
    product = getattr(asset, "product", None) if asset is not None else None
    filename = _basename(getattr(row, "image", None))
    matched = _product_gallery_match(product, filename)
    if matched:
        return matched, "گالری عمومی محصول"
    main = _product_main_url(product)
    if main:
        return main, "تصویر اصلی محصول"
    remote = _http_url(getattr(row, "remote_url", ""))
    if remote:
        return remote, "تصویر منبع"
    return "", "ناموجود"


def _preview_html(url: str, source: str, *, width: int = 110, height: int = 82):
    if not url:
        return format_html('<span style="color:#b91c1c;font-weight:700">پیش‌نمایش عمومی ندارد</span>')
    return format_html(
        '<a href="{}" target="_blank" rel="noopener" style="display:inline-grid;gap:4px;text-decoration:none">'
        '<img src="{}" alt="پیش‌نمایش" loading="lazy" style="width:{}px;height:{}px;object-fit:contain;background:#f8fafc;border:1px solid #dbe2ea;border-radius:10px">'
        '<small style="color:#64748b">{}</small></a>',
        url,
        url,
        width,
        height,
        source,
    )


def install() -> None:
    asset_admin = admin.site._registry.get(ImportedPrintAsset)
    if asset_admin is None:
        return

    @admin.display(description="پیش‌نمایش امن")
    def safe_preview(obj):
        url, source = public_asset_image(obj)
        return _preview_html(url, source)

    @admin.display(description="وضعیت داده")
    def completeness(obj):
        checks = [
            bool(str(getattr(obj, "persian_title", "") or getattr(obj, "title", "")).strip()),
            bool(str(getattr(obj, "persian_description", "") or getattr(obj, "description", "")).strip()),
            bool(getattr(obj, "product_id", None)),
            bool(public_asset_image(obj)[0]),
        ]
        score = sum(1 for value in checks if value)
        color = "#15803d" if score == 4 else ("#b45309" if score >= 2 else "#b91c1c")
        return format_html('<strong style="color:{}">{}/4</strong>', color, score)

    asset_admin.safe_preview = safe_preview
    asset_admin.completeness = completeness

    # Preserve Phase35 list_editable/list_display_links exactly; only add the two
    # new informational columns around the mature operational columns.
    display = list(getattr(asset_admin, "list_display", []) or [])
    if "safe_preview" not in display:
        display.insert(0, "safe_preview")
    if "completeness" not in display:
        if "imported_at" in display:
            display.insert(display.index("imported_at"), "completeness")
        else:
            display.append("completeness")
    asset_admin.list_display = display

    asset_admin.list_filter = _extend(
        getattr(asset_admin, "list_filter", []),
        ["translation_status", "price_status", "commercial_license_status", "editorial_status"],
    )
    asset_admin.search_fields = _extend(
        getattr(asset_admin, "search_fields", []),
        ["persian_title", "persian_short_description", "source_title"],
    )
    asset_admin.readonly_fields = _extend(
        getattr(asset_admin, "readonly_fields", []),
        ["safe_preview", "completeness"],
    )
    asset_admin.list_per_page = 40

    # Keep every mature Phase35 field, action and pricing control; add a compact
    # health panel as the first fieldset instead of replacing the editor.
    existing_fieldsets = list(getattr(asset_admin, "fieldsets", ()) or ())
    if not any(title == "سلامت رسانه و داده" for title, _options in existing_fieldsets):
        existing_fieldsets.insert(
            0,
            (
                "سلامت رسانه و داده",
                {
                    "fields": ("safe_preview", "completeness"),
                    "description": "پیش‌نمایش فقط از رسانه عمومی Product یا URL منبع استفاده می‌کند؛ فایل‌های working-media کاتالوگ عمداً عمومی نمی‌شوند.",
                },
            ),
        )
    asset_admin.fieldsets = tuple(existing_fieldsets)

    for inline in getattr(asset_admin, "inlines", ()):
        if getattr(inline, "model", None) is not ImportedPrintAssetImage:
            continue

        @admin.display(description="پیش‌نمایش عمومی")
        def inline_safe_preview(obj):
            url, source = public_imported_image(obj)
            return _preview_html(url, source, width=140, height=105)

        @admin.display(description="ابعاد منبع")
        def source_dimensions(obj):
            if not obj:
                return "—"
            width = int(getattr(obj, "source_width", 0) or 0)
            height = int(getattr(obj, "source_height", 0) or 0)
            return f"{width} × {height} px" if width and height else "ثبت نشده"

        inline.safe_preview = inline_safe_preview
        inline.source_dimensions = source_dimensions
        inline.fields = [
            "safe_preview", "source_dimensions", "image", "remote_url", "alt_text",
            "is_selected", "is_primary", "sort_order",
        ]
        inline.readonly_fields = _extend(
            getattr(inline, "readonly_fields", []),
            ["safe_preview", "source_dimensions"],
        )
        inline.extra = 0
