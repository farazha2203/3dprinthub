from __future__ import annotations

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import ProductVariant


@require_GET
def variant_commerce_options_view(request):
    raw_ids = str(request.GET.get("ids") or "")
    ids = []
    for token in raw_ids.split(","):
        token = token.strip()
        if token.isdigit():
            ids.append(int(token))
    ids = ids[:100]

    variants = (
        ProductVariant.objects.filter(
            pk__in=ids,
            is_active=True,
            product__is_active=True,
        )
        .select_related("product", "material", "quality", "color")
        .order_by("pk")
    )
    payload = {}
    for variant in variants:
        payload[str(variant.pk)] = {
            "size_label": str(getattr(variant, "size_label", "") or ""),
            "build_profile": str(getattr(variant, "build_profile", "standard") or "standard"),
            "build_profile_label": str(variant.get_build_profile_display()) if hasattr(variant, "get_build_profile_display") else "",
            "commerce_label": str(getattr(variant, "commerce_display_label", "") or ""),
            "packaging_weight_grams": str(getattr(variant, "packaging_weight_grams", 0) or 0),
            "effective_shipping_weight_grams": str(getattr(variant, "effective_shipping_weight_grams", 0) or 0),
            "package_length_cm": str(getattr(variant, "package_length_cm", 0) or 0),
            "package_width_cm": str(getattr(variant, "package_width_cm", 0) or 0),
            "package_height_cm": str(getattr(variant, "package_height_cm", 0) or 0),
        }
    return JsonResponse({"variants": payload})
