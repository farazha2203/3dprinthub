from __future__ import annotations

from django.db.models import Q

from .models import ImportedPrintAsset, Product


def deactivate_unretained_products_for_source(source) -> int:
    """Hide products whose upstream source was disabled and no local asset is retained."""
    asset_ids = (
        ImportedPrintAsset.objects.filter(source=source, product__isnull=False)
        .exclude(
            Q(keep_public_when_source_disabled=True)
            | Q(archive_status__in=["downloaded", "archived", "ordered"])
            | (Q(archived_model_file__isnull=False) & ~Q(archived_model_file=""))
            | (Q(product__model_file__isnull=False) & ~Q(product__model_file=""))
        )
        .values_list("product_id", flat=True)
    )
    return Product.objects.filter(pk__in=asset_ids).update(is_active=False, robots_index=False)


def enforce_source_lifecycle(source) -> int:
    try:
        policy_enabled = bool(source.sync_policy.is_active and source.sync_policy.public_reference_enabled)
    except Exception:
        policy_enabled = True
    if source.is_active and policy_enabled:
        return 0
    return deactivate_unretained_products_for_source(source)
