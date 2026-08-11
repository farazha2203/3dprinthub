from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ImportedPrintAsset
from .phase34b_translation import draft_persian_description, draft_persian_title

DEFAULT_PROVISIONAL_PRICE = 500_000
PRICE_MULTIPLIER = Decimal("5")
ROUNDING = 10_000


def _round_up(value: int, step: int = ROUNDING) -> int:
    return ((max(0, int(value)) + step - 1) // step) * step


def _weight_grams(asset: ImportedPrintAsset) -> Decimal:
    try:
        if getattr(asset, "metrics", None) and asset.metrics.estimated_weight_grams:
            return Decimal(str(asset.metrics.estimated_weight_grams))
    except Exception:
        pass
    specs = asset.technical_specs or {}
    value = specs.get("estimated_weight_grams") or specs.get("weight_grams") or 0
    try:
        return max(Decimal("0"), Decimal(str(value)))
    except Exception:
        return Decimal("0")


def _default_sale_price_per_gram() -> Decimal:
    from website.models import Material
    rows = Material.objects.filter(is_active=True).order_by("sort_order", "id")
    for material in rows:
        for value in (
            getattr(material, "public_sale_price_per_gram", 0),
            getattr(material, "sale_price_per_gram", 0),
        ):
            try:
                if value and Decimal(str(value)) > 0:
                    return Decimal(str(value))
            except Exception:
                pass
        value = getattr(material, "price_per_kg", 0)
        if value:
            return Decimal(str(value)) / Decimal("1000")
    return Decimal("0")


def calculate_provisional_price(asset: ImportedPrintAsset) -> tuple[int, int, str]:
    weight = _weight_grams(asset)
    price_per_gram = _default_sale_price_per_gram()
    material_cost = int((weight * price_per_gram).quantize(Decimal("1"))) if weight and price_per_gram else 0
    formula_price = int((weight * price_per_gram * PRICE_MULTIPLIER).quantize(Decimal("1"))) if material_cost else 0
    final = _round_up(max(DEFAULT_PROVISIONAL_PRICE, formula_price))
    if formula_price:
        note = (
            f"علی‌الحساب: {weight.normalize()} گرم × {price_per_gram.normalize()} تومان × ضریب ۵؛ "
            "کف قیمت ۵۰۰٬۰۰۰ تومان. قیمت نهایی پس از بررسی اپراتور قطعی می‌شود."
        )
    else:
        note = "علی‌الحساب با کف ۵۰۰٬۰۰۰ تومان؛ وزن یا قیمت متریال کامل نیست و اپراتور باید قیمت نهایی را ثبت کند."
    return final, material_cost, note


def apply_provisional_price(asset: ImportedPrintAsset, *, force: bool = False) -> ImportedPrintAsset:
    if asset.price_is_final and not force:
        return asset
    price, material_cost, note = calculate_provisional_price(asset)
    asset.fixed_print_price = price
    asset.estimated_material_cost = material_cost
    asset.price_status = "estimated"
    asset.price_is_final = False
    asset.pricing_note = note
    asset.save(update_fields=[
        "fixed_print_price", "estimated_material_cost", "price_status",
        "price_is_final", "pricing_note", "updated_at",
    ])
    return asset


def _google_translate(text: str, *, target: str = "fa") -> str:
    key = os.getenv("GOOGLE_TRANSLATE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GOOGLE_TRANSLATE_API_KEY is not configured")
    endpoint = "https://translation.googleapis.com/language/translate/v2?" + urllib.parse.urlencode({"key": key})
    payload = json.dumps({"q": text, "target": target, "format": "text"}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
        data = json.loads(response.read().decode("utf-8"))
    return str(data["data"]["translations"][0]["translatedText"]).strip()


def translate_asset(asset: ImportedPrintAsset, *, force: bool = False) -> ImportedPrintAsset:
    source_title = asset.source_title or asset.title
    source_short = asset.short_description or source_title
    source_description = asset.source_description or asset.description or source_short
    provider = "local-draft"
    status = "draft"
    try:
        title_fa = _google_translate(source_title)
        short_fa = _google_translate(source_short)
        description_fa = _google_translate(source_description)
        provider = "google-cloud-v2"
        status = "translated"
    except Exception:
        title_fa = draft_persian_title(source_title)
        short_fa = draft_persian_title(source_short)[:500]
        description_fa = draft_persian_description(source_title, source_description, asset.source.name)
    if force or not asset.persian_title:
        asset.persian_title = title_fa[:260]
    if force or not asset.persian_short_description:
        asset.persian_short_description = short_fa[:500]
    if force or not asset.persian_description:
        asset.persian_description = description_fa
    asset.translation_status = status
    asset.translation_provider = provider
    asset.translated_at = timezone.now()
    asset.save(update_fields=[
        "persian_title", "persian_short_description", "persian_description",
        "translation_status", "translation_provider", "translated_at", "updated_at",
    ])
    return asset


@transaction.atomic
def prepare_asset(asset: ImportedPrintAsset, *, force_translation: bool = False) -> ImportedPrintAsset:
    translate_asset(asset, force=force_translation)
    apply_provisional_price(asset)
    return asset


def mark_price_final(asset: ImportedPrintAsset) -> ImportedPrintAsset:
    if not asset.fixed_print_price:
        raise ValidationError("قبل از قطعی‌کردن، قیمت را وارد کنید.")
    asset.price_is_final = True
    asset.price_status = "final"
    asset.pricing_note = "قیمت توسط اپراتور بررسی و قطعی شده است."
    asset.save(update_fields=["price_is_final", "price_status", "pricing_note", "updated_at"])
    return asset
