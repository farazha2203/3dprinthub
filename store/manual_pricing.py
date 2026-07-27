from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import LinkAnalysisManualReview


@transaction.atomic
def apply_manual_review_pricing(review: LinkAnalysisManualReview, *, operator=None) -> LinkAnalysisManualReview:
    """Lock operator-confirmed pricing inputs onto a customer link analysis."""
    review = (
        LinkAnalysisManualReview.objects.select_for_update()
        .select_related("analysis", "operator_material")
        .get(pk=review.pk)
    )
    if not review.operator_pricing_complete:
        raise ValidationError("برای اعلام قیمت، متریال، وزن و زمان واقعی چاپ را کامل کنید.")

    analysis = review.analysis
    specs = dict(analysis.technical_specs or {})
    specs.update(dict(review.operator_specs or {}))
    specs.update({
        "weight_source_kind": "operator_verified",
        "print_time_source_kind": "operator_verified",
        "operator_manual_review_id": review.pk,
        "operator_verified_at": timezone.now().isoformat(),
    })
    analysis.material = review.operator_material
    analysis.detected_material_name = review.operator_material.name
    analysis.estimated_weight_grams = review.operator_weight_grams
    analysis.estimated_print_minutes = review.operator_print_minutes
    analysis.technical_specs = specs
    analysis.status = "ready"
    analysis.error_message = ""
    analysis.save(update_fields=[
        "material", "detected_material_name", "estimated_weight_grams",
        "estimated_print_minutes", "technical_specs", "status",
        "error_message", "updated_at",
    ])

    from .link_intelligence import calculate_link_estimate
    calculate_link_estimate(analysis)
    if review.operator_price_override:
        quantity = max(int(analysis.quantity or 1), 1)
        final_price = int(review.operator_price_override) * quantity
        analysis.estimated_price = final_price
        analysis.estimated_price_min = final_price
        analysis.estimated_price_max = final_price
        analysis.estimate_confidence = Decimal("100")
        breakdown = dict(analysis.estimate_breakdown or {})
        breakdown.update({
            "operator_price_override": int(review.operator_price_override),
            "quantity": quantity,
            "total": final_price,
            "pricing_locked": True,
        })
        analysis.estimate_breakdown = breakdown
        analysis.save(update_fields=[
            "estimated_price", "estimated_price_min", "estimated_price_max",
            "estimate_confidence", "estimate_breakdown", "updated_at",
        ])

    from .manual_review import finish_review
    return finish_review(
        review,
        user=operator or review.assigned_to,
        action="data_completed",
        note=(
            f"وزن {review.operator_weight_grams} گرم و زمان واقعی {review.operator_print_minutes} دقیقه "
            "توسط اپراتور تأیید شد و قیمت قطعی قابل مشاهده است."
        ),
        status="resolved",
    )
