from __future__ import annotations

import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify

from .models import ImportedPrintAsset, Product, ProductVariant, PrintQuality
from .phase34b_translation import draft_persian_description, draft_persian_title


def ensure_persian_draft(asset: ImportedPrintAsset) -> ImportedPrintAsset:
    changed=[]
    if not asset.source_title:
        asset.source_title=asset.title
        changed.append("source_title")
    if not asset.source_description:
        asset.source_description=asset.description
        changed.append("source_description")
    if not asset.persian_title:
        asset.persian_title=draft_persian_title(asset.title)
        changed.append("persian_title")
    if not asset.persian_short_description:
        asset.persian_short_description=(asset.persian_title or asset.title)[:500]
        changed.append("persian_short_description")
    if not asset.persian_description:
        asset.persian_description=draft_persian_description(asset.title, asset.description, asset.source.name)
        changed.append("persian_description")
    if changed:
        asset.save(update_fields=[*changed,"updated_at"])
    return asset


def _copy_image(field_file, target_field, filename: str) -> None:
    field_file.open("rb")
    try:
        target_field.save(filename, ContentFile(field_file.read()), save=False)
    finally:
        field_file.close()


@transaction.atomic
def convert_to_fixed_product(asset: ImportedPrintAsset) -> Product:
    asset=ImportedPrintAsset.objects.select_for_update().select_related("source__default_category","product").get(pk=asset.pk)
    if asset.product_id:
        return asset.product
    if not asset.can_convert_to_fixed_product:
        raise ValidationError("برای تبدیل به محصول، قیمت ثابت و مجوز تجاری تأییدشده لازم است.")
    if not asset.preview_image:
        raise ValidationError("قبل از تبدیل، تصویر اصلی باید در Media ذخیره یا بارگذاری شود.")
    category=asset.source.default_category
    try:
        category=asset.metrics.target_category or category
    except Exception:
        pass
    if category is None:
        raise ValidationError("دسته مقصد محصول مشخص نشده است.")
    ensure_persian_draft(asset)
    base_slug=slugify(asset.persian_title or asset.title,allow_unicode=True)[:220] or f"makerworld-{asset.pk}"
    slug=base_slug
    counter=1
    while Product.objects.filter(slug=slug).exists():
        counter+=1
        slug=f"{base_slug}-{counter}"
    product=Product(
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
            f"{json.dumps(asset.technical_specs or {},ensure_ascii=False,indent=2)}"
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
    _copy_image(asset.preview_image,product.main_image,Path(asset.preview_image.name).name)
    product.save()
    from website.models import Material
    material = Material.objects.filter(is_active=True).order_by("sort_order", "id").first()
    quality = PrintQuality.objects.filter(is_active=True).order_by("sort_order", "id").first()
    if material is None or quality is None:
        raise ValidationError("برای سفارش مستقیم، حداقل یک متریال و یک کیفیت چاپ فعال لازم است.")
    specs = asset.technical_specs or {}
    weight = specs.get("estimated_weight_grams") or 1
    minutes = specs.get("estimated_print_minutes") or 60
    ProductVariant.objects.create(
        product=product,
        material=material,
        quality=quality,
        code=f"MW-FIX-{asset.pk:07d}-DEFAULT",
        material_weight_grams=weight,
        final_weight_grams=weight,
        shipping_weight_grams=weight,
        print_time_minutes=max(1, int(minutes)),
        fixed_fee=asset.fixed_print_price,
        cached_unit_price=asset.fixed_print_price,
        lead_time_min_days=max(1, product.fixed_delivery_days),
        lead_time_max_days=max(1, product.fixed_delivery_days),
        stock_status="made_to_order",
        is_active=True,
    )
    for row in asset.images.filter(is_selected=True,image__isnull=False).exclude(image="").order_by("sort_order","id"):
        target=product.images.create(alt_text=row.alt_text or product.title,sort_order=row.sort_order)
        _copy_image(row.image,target.image,Path(row.image.name).name)
        target.save()
    asset.product=product
    asset.status="converted"
    asset.editorial_status="product"
    asset.save(update_fields=["product","status","editorial_status","updated_at"])
    return product


@transaction.atomic
def convert_to_portfolio(asset: ImportedPrintAsset):
    from website.models import PortfolioItem
    asset=ImportedPrintAsset.objects.select_for_update().select_related("portfolio_item").get(pk=asset.pk)
    if asset.portfolio_item_id:
        return asset.portfolio_item
    if not asset.preview_image:
        raise ValidationError("برای ساخت نمونه‌کار حداقل یک تصویر محلی لازم است.")
    ensure_persian_draft(asset)
    item=PortfolioItem(
        title=(asset.persian_title or asset.title)[:200],
        category="چاپ سه‌بعدی",
        description=asset.persian_description or asset.description,
        is_active=False,
    )
    _copy_image(asset.preview_image,item.image,Path(asset.preview_image.name).name)
    item.save()
    asset.portfolio_item=item
    asset.editorial_status="portfolio"
    asset.save(update_fields=["portfolio_item","editorial_status","updated_at"])
    return item
