from __future__ import annotations

import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify

from .models import Category, ImportedPrintAsset, Product, ProductVariant, PrintQuality
from .phase34b_translation import draft_persian_description, draft_persian_title


def ensure_persian_draft(asset: ImportedPrintAsset) -> ImportedPrintAsset:
    changed = []
    if not asset.source_title:
        asset.source_title = asset.title
        changed.append("source_title")
    if not asset.source_description:
        asset.source_description = asset.description
        changed.append("source_description")
    if not asset.persian_title:
        asset.persian_title = draft_persian_title(asset.title)
        changed.append("persian_title")
    if not asset.persian_short_description:
        asset.persian_short_description = (asset.persian_title or asset.title)[:500]
        changed.append("persian_short_description")
    if not asset.persian_description:
        asset.persian_description = draft_persian_description(asset.title, asset.description, asset.source.name)
        changed.append("persian_description")
    if changed:
        asset.save(update_fields=[*changed, "updated_at"])
    return asset


def _copy_image(field_file, target_field, filename: str) -> None:
    field_file.open("rb")
    try:
        target_field.save(filename, ContentFile(field_file.read()), save=False)
    finally:
        field_file.close()


def _desktop_payload(asset: ImportedPrintAsset) -> dict:
    payload = asset.source_payload or {}
    value = payload.get("desktop_catalog_v85") if isinstance(payload, dict) else {}
    return value if isinstance(value, dict) else {}


def _json_list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _resolved_category(asset: ImportedPrintAsset) -> Category | None:
    desktop = _desktop_payload(asset)
    slug = str(desktop.get("local_category_slug") or "").strip()
    if slug:
        category = Category.objects.filter(slug=slug).first()
        if category is not None:
            return category
    category = asset.source.default_category
    try:
        category = asset.metrics.target_category or category
    except Exception:
        pass
    return category


def _selected_asset_images(asset: ImportedPrintAsset) -> list:
    """Return exactly the images selected in the current desktop batch, in order.

    Older ImportedPrintAssetImage rows can remain in the database after a desktop
    re-edit.  The current batch payload is therefore the source of truth instead
    of blindly reusing every historical `is_selected=True` row.
    """

    selected_urls = [str(x or "").strip() for x in _json_list(_desktop_payload(asset).get("images_json")) if str(x or "").strip()]
    rows = list(asset.images.exclude(image="").order_by("sort_order", "id"))
    if selected_urls:
        by_url = {}
        for row in rows:
            by_url.setdefault(str(row.remote_url or ""), row)
        ordered = [by_url[url] for url in selected_urls if url in by_url]
        if ordered:
            return ordered
    return [row for row in rows if row.is_selected]


def _sync_product_images(product: Product, asset: ImportedPrintAsset) -> int:
    if not asset.preview_image:
        raise ValidationError("قبل از انتشار، تصویر اصلی باید در Media ذخیره شده باشد.")

    _copy_image(asset.preview_image, product.main_image, Path(asset.preview_image.name).name)
    # Imported catalog products are desktop-managed. Rebuild only their ProductImage
    # rows so the Store mirrors the *current* Windows selection. Django does not
    # delete the historical physical files here; this avoids destructive media loss.
    product.images.all().delete()
    count = 0
    for index, row in enumerate(_selected_asset_images(asset)):
        target = product.images.create(
            alt_text=row.alt_text or product.title,
            sort_order=index,
        )
        _copy_image(row.image, target.image, Path(row.image.name).name)
        target.save()
        count += 1
    return count


def _sync_product_fields(product: Product, asset: ImportedPrintAsset) -> None:
    category = _resolved_category(asset)
    if category is None:
        raise ValidationError("دسته مقصد محصول مشخص نشده است.")
    ensure_persian_draft(asset)

    product.category = category
    product.title = (asset.persian_title or asset.title)[:220]
    product.title_en = (asset.source_title or asset.title)[:220]
    product.short_description = (asset.persian_short_description or asset.short_description or asset.title)[:350]
    product.short_description_en = (asset.short_description or asset.source_title or asset.title)[:500]
    product.description = asset.persian_description or asset.description
    product.description_en = asset.source_description or asset.description
    product.source_url = asset.source_url
    product.source_name = asset.source.name
    product.source_external_id = asset.external_id
    product.order_mode = "fixed"
    product.fixed_price = asset.fixed_print_price
    product.price_is_final = asset.price_is_final
    product.price_note = asset.pricing_note
    product.consultation_required = not asset.price_is_final
    _sync_product_images(product, asset)
    product.save()


def _ensure_default_variant(product: Product, asset: ImportedPrintAsset) -> ProductVariant:
    code = f"MW-FIX-{asset.pk:07d}-DEFAULT"
    specs = asset.technical_specs or {}
    weight = specs.get("estimated_weight_grams") or 1
    minutes = max(1, int(specs.get("estimated_print_minutes") or 60))
    variant = ProductVariant.objects.filter(code=code).first()
    if variant is not None:
        variant.product = product
        variant.material_weight_grams = weight
        variant.final_weight_grams = weight
        variant.shipping_weight_grams = weight
        variant.print_time_minutes = minutes
        variant.fixed_fee = asset.fixed_print_price
        variant.cached_unit_price = asset.fixed_print_price
        variant.lead_time_min_days = max(1, product.fixed_delivery_days)
        variant.lead_time_max_days = max(1, product.fixed_delivery_days)
        variant.stock_status = "made_to_order"
        variant.is_active = True
        variant.save()
        return variant

    from website.models import Material

    material = Material.objects.filter(is_active=True).order_by("sort_order", "id").first()
    quality = PrintQuality.objects.filter(is_active=True).order_by("sort_order", "id").first()
    if material is None or quality is None:
        raise ValidationError("برای سفارش مستقیم، حداقل یک متریال و یک کیفیت چاپ فعال لازم است.")
    return ProductVariant.objects.create(
        product=product,
        material=material,
        quality=quality,
        code=code,
        material_weight_grams=weight,
        final_weight_grams=weight,
        shipping_weight_grams=weight,
        print_time_minutes=minutes,
        fixed_fee=asset.fixed_print_price,
        cached_unit_price=asset.fixed_print_price,
        lead_time_min_days=max(1, product.fixed_delivery_days),
        lead_time_max_days=max(1, product.fixed_delivery_days),
        stock_status="made_to_order",
        is_active=True,
    )


@transaction.atomic
def convert_to_fixed_product(asset: ImportedPrintAsset) -> Product:
    asset = (
        ImportedPrintAsset.objects.select_for_update()
        .select_related("source__default_category", "product")
        .get(pk=asset.pk)
    )
    if not asset.can_convert_to_fixed_product:
        raise ValidationError("برای تبدیل به محصول، قیمت ثابت و مجوز تجاری تأییدشده لازم است.")
    if not asset.preview_image:
        raise ValidationError("قبل از تبدیل، تصویر اصلی باید در Media ذخیره یا بارگذاری شود.")

    category = _resolved_category(asset)
    if category is None:
        raise ValidationError("دسته مقصد محصول مشخص نشده است.")
    ensure_persian_draft(asset)

    if asset.product_id:
        product = asset.product
        _sync_product_fields(product, asset)
        _ensure_default_variant(product, asset)
        asset.status = "converted"
        asset.editorial_status = "product"
        asset.save(update_fields=["status", "editorial_status", "updated_at"])
        return product

    base_slug = slugify(asset.persian_title or asset.title, allow_unicode=True)[:220] or f"makerworld-{asset.pk}"
    slug = base_slug
    counter = 1
    while Product.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"
    product = Product(
        category=category,
        title=(asset.persian_title or asset.title)[:220],
        title_en=(asset.source_title or asset.title)[:220],
        slug=slug,
        sku=f"MW-FIX-{asset.pk:07d}",
        short_description=(asset.persian_short_description or asset.short_description or asset.title)[:350],
        short_description_en=(asset.short_description or asset.source_title or asset.title)[:500],
        description=asset.persian_description or asset.description,
        description_en=asset.source_description or asset.description,
        source_url=asset.source_url,
        source_name=asset.source.name,
        source_external_id=asset.external_id,
        technical_notes=(
            f"منبع: {asset.source.name}\nصفحه اصلی: {asset.source_url}\n"
            f"طراح: {asset.author_name or '-'}\nمجوز: {asset.license_name or '-'}\n"
            f"مدرک مجوز تجاری: {asset.commercial_license_source or '-'}\n\n"
            f"{json.dumps(asset.technical_specs or {}, ensure_ascii=False, indent=2)}"
        ),
        is_active=False,
        robots_index=False,
        robots_follow=False,
        order_mode="fixed",
        fixed_price=asset.fixed_print_price,
        price_is_final=asset.price_is_final,
        price_note=asset.pricing_note,
        consultation_required=not asset.price_is_final,
    )
    _copy_image(asset.preview_image, product.main_image, Path(asset.preview_image.name).name)
    product.save()
    _ensure_default_variant(product, asset)

    for index, row in enumerate(_selected_asset_images(asset)):
        target = product.images.create(
            alt_text=row.alt_text or product.title,
            sort_order=index,
        )
        _copy_image(row.image, target.image, Path(row.image.name).name)
        target.save()

    asset.product = product
    asset.status = "converted"
    asset.editorial_status = "product"
    asset.save(update_fields=["product", "status", "editorial_status", "updated_at"])
    return product


@transaction.atomic
def convert_to_portfolio(asset: ImportedPrintAsset):
    from website.models import PortfolioItem

    asset = ImportedPrintAsset.objects.select_for_update().select_related("portfolio_item").get(pk=asset.pk)
    if asset.portfolio_item_id:
        return asset.portfolio_item
    if not asset.preview_image:
        raise ValidationError("برای ساخت نمونه‌کار حداقل یک تصویر محلی لازم است.")
    ensure_persian_draft(asset)
    item = PortfolioItem(
        title=(asset.persian_title or asset.title)[:200],
        category="چاپ سه‌بعدی",
        description=asset.persian_description or asset.description,
        is_active=False,
    )
    _copy_image(asset.preview_image, item.image, Path(asset.preview_image.name).name)
    item.save()
    asset.portfolio_item = item
    asset.editorial_status = "portfolio"
    asset.save(update_fields=["portfolio_item", "editorial_status", "updated_at"])
    return item
