from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from .models import (
    CatalogPricingReview,
    CustomerLinkAnalysis,
    ImportedPrintAssetPrintProfile,
    PricingSetting,
)


def material_sale_per_gram(material) -> Decimal:
    return Decimal(
        getattr(material, "public_sale_price_per_gram", 0)
        or getattr(material, "effective_sale_price_per_gram", 0)
        or getattr(material, "sale_price_per_gram", 0)
        or getattr(material, "price_per_gram", 0)
        or (Decimal(getattr(material, "price_per_kg", 0) or 0) / Decimal("1000"))
    )


def billable_minutes(actual_minutes: int, pricing: PricingSetting | None = None) -> int:
    import math
    pricing = pricing or PricingSetting.load()
    actual = max(int(actual_minutes or 0), 0)
    if not actual:
        return 0
    minimum = max(int(pricing.minimum_billable_minutes or 1), 1)
    increment = max(int(pricing.billing_increment_minutes or 1), 1)
    return max(minimum, int(math.ceil(actual / increment) * increment))


def calculate_verified_price(review: CatalogPricingReview, *, quantity: int = 1) -> dict:
    if not review.is_complete:
        return {"total": 0, "billable_minutes": 0}
    if review.price_override:
        return {
            "total": int(review.price_override) * max(int(quantity or 1), 1),
            "billable_minutes": billable_minutes(review.print_minutes),
            "override": True,
        }
    pricing = PricingSetting.load()
    quantity = max(int(quantity or 1), 1)
    weight = Decimal(review.weight_grams)
    sale_per_gram = material_sale_per_gram(review.material)
    billable = billable_minutes(review.print_minutes, pricing)
    material_cost = sale_per_gram * weight * quantity
    machine_cost = Decimal(pricing.default_hourly_rate) * Decimal(billable) / Decimal("60") * quantity
    labor_cost = (material_cost + machine_cost) * Decimal(pricing.default_labor_percent) / Decimal("100")
    packaging = Decimal(pricing.packaging_fee or 0)
    subtotal = material_cost + machine_cost + labor_cost + packaging
    minimum_adjustment = max(Decimal(pricing.minimum_order_amount or 0) - subtotal, Decimal("0"))
    total = subtotal + minimum_adjustment
    return {
        "total": int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "material_cost": int(material_cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "machine_cost": int(machine_cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "labor_cost": int(labor_cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "packaging": int(packaging),
        "minimum_order_adjustment": int(minimum_adjustment.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "billable_minutes": billable,
        "actual_minutes": int(review.print_minutes),
        "material_sale_per_gram": str(sale_per_gram.quantize(Decimal("0.01"))),
        "override": False,
    }


@transaction.atomic
def apply_verified_catalog_pricing(review: CatalogPricingReview) -> CatalogPricingReview:
    review = CatalogPricingReview.objects.select_for_update().select_related("asset", "material").get(pk=review.pk)
    if review.status != "verified":
        return review
    if not review.material_id or not review.weight_grams or not review.print_minutes:
        review.status = "pending"
        review.verified_at = None
        review.save(update_fields=["status", "verified_at", "updated_at"])
        return review

    review.verified_at = review.verified_at or timezone.now()
    review.save(update_fields=["verified_at", "updated_at"])
    asset = review.asset
    metrics = asset.metrics
    metrics.estimated_weight_grams = review.weight_grams
    metrics.estimated_print_minutes = review.print_minutes
    metrics.estimate_source = "operator_verified"
    metrics.save(update_fields=["estimated_weight_grams", "estimated_print_minutes", "estimate_source", "last_synced_at"])
    ImportedPrintAssetPrintProfile.objects.update_or_create(
        asset=asset,
        source_key="operator-verified",
        defaults={
            "profile_name": "پروفایل تأییدشده اپراتور",
            "weight_grams": review.weight_grams,
            "print_minutes": review.print_minutes,
            "material": review.material.name,
            "is_manual": True,
            "is_active": True,
            "source_payload": {"review_id": review.pk, "verified_at": review.verified_at.isoformat()},
        },
    )

    from .link_intelligence import calculate_link_estimate
    for analysis in CustomerLinkAnalysis.objects.filter(related_asset=asset).select_related("material"):
        specs = dict(analysis.technical_specs or {})
        specs["weight_source_kind"] = "operator_verified"
        specs["print_time_source_kind"] = "operator_verified"
        specs["operator_pricing_review_id"] = review.pk
        analysis.technical_specs = specs
        analysis.material = review.material
        analysis.estimated_weight_grams = review.weight_grams
        analysis.estimated_print_minutes = review.print_minutes
        analysis.status = "ready"
        analysis.save(update_fields=[
            "technical_specs", "material", "estimated_weight_grams", "estimated_print_minutes", "status", "updated_at"
        ])
        calculate_link_estimate(analysis)
        if review.price_override:
            analysis.estimated_price = int(review.price_override) * max(int(analysis.quantity or 1), 1)
            analysis.estimated_price_min = analysis.estimated_price
            analysis.estimated_price_max = analysis.estimated_price
            analysis.estimate_confidence = Decimal("100")
            breakdown = dict(analysis.estimate_breakdown or {})
            breakdown["operator_price_override"] = int(review.price_override)
            breakdown["total"] = analysis.estimated_price
            analysis.estimate_breakdown = breakdown
            analysis.save(update_fields=[
                "estimated_price", "estimated_price_min", "estimated_price_max", "estimate_confidence", "estimate_breakdown", "updated_at"
            ])
    return review
