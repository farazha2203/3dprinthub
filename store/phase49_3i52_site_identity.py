from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from .epic49_catalog_profile import ProductCatalogProfile
from .models import Product


def _normalized_url(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        parts = urlsplit(text)
    except Exception:
        return text.rstrip("/").casefold()
    if not parts.scheme or not parts.netloc:
        return text.rstrip("/").casefold()
    return urlunsplit(
        (
            parts.scheme.casefold(),
            parts.netloc.casefold(),
            parts.path.rstrip("/"),
            parts.query,
            "",
        )
    )


def _source_names(asset) -> set[str]:
    source = getattr(asset, "source", None)
    values = {
        str(getattr(source, "name", "") or "").strip().casefold(),
        str(getattr(source, "code", "") or "").strip().casefold(),
    }
    return {value for value in values if value}


def _candidate_products(asset, data: dict) -> list[Product]:
    url = _normalized_url(
        data.get("source_url") or getattr(asset, "source_url", "")
    )
    external_id = str(
        data.get("external_id") or getattr(asset, "external_id", "") or ""
    ).strip()
    source_names = _source_names(asset)

    # URL is the strongest Site-side identity because it includes the source
    # namespace. Use an exact normalized comparison instead of fuzzy matching.
    url_matches: list[Product] = []
    if url:
        for product in Product.objects.exclude(source_url="").order_by("pk"):
            if _normalized_url(product.source_url) == url:
                url_matches.append(product)
        if len(url_matches) > 1:
            raise ValidationError(
                "بیش از یک Product سایت با همین Source URL وجود دارد؛ "
                "تطبیق Desktop متوقف شد تا Merge اشتباه انجام نشود."
            )
        if len(url_matches) == 1:
            product = url_matches[0]
            existing_external = str(
                getattr(product, "source_external_id", "") or ""
            ).strip()
            if (
                external_id
                and existing_external
                and existing_external.casefold() != external_id.casefold()
            ):
                raise ValidationError(
                    "Source URL با Product سایت تطبیق دارد اما External ID متفاوت است؛ "
                    "قبل از Import هویت منبع را اصلاح کن."
                )
            return [product]

    # External IDs are source-scoped. Never match on the number alone unless
    # the Product also carries a compatible source name/code.
    if external_id and source_names:
        source_query = Q()
        for name in source_names:
            source_query |= Q(source_name__iexact=name)
        matches = list(
            Product.objects.filter(
                source_external_id__iexact=external_id
            )
            .filter(source_query)
            .order_by("pk")
        )
        if len(matches) > 1:
            raise ValidationError(
                "External ID/Source به چند Product سایت می‌خورد؛ "
                "تطبیق Desktop مبهم است و عمداً متوقف شد."
            )
        return matches

    return []


@transaction.atomic
def reconcile_asset_product_identity(
    asset,
    data: dict,
    *,
    desktop_product_id=None,
):
    """Link an imported Desktop asset to one unambiguous Site Product.

    The function never rewrites Product content/pricing. It only establishes
    canonical identity so the mature converter updates that Product in place
    instead of creating a duplicate. Any ambiguity or conflicting Desktop ID
    fails closed.
    """
    product = getattr(asset, "product", None)
    if product is None:
        matches = _candidate_products(asset, data)
        product = matches[0] if len(matches) == 1 else None

    if product is None:
        return None

    incoming_desktop_id = 0
    try:
        incoming_desktop_id = int(
            desktop_product_id
            or data.get("desktop_product_id")
            or 0
        )
    except Exception:
        incoming_desktop_id = 0

    profile = ProductCatalogProfile.objects.filter(product=product).first()
    if (
        profile is not None
        and incoming_desktop_id > 0
        and profile.desktop_product_id
        and int(profile.desktop_product_id) != incoming_desktop_id
    ):
        raise ValidationError(
            "این Product سایت قبلاً به Desktop Product دیگری متصل شده است؛ "
            "برای جلوگیری از Merge اشتباه Import متوقف شد."
        )

    if getattr(asset, "product_id", None) != product.pk:
        asset.product = product
        asset.save(update_fields=["product", "updated_at"])

    if profile is not None and incoming_desktop_id > 0 and not profile.desktop_product_id:
        profile.desktop_product_id = incoming_desktop_id
        profile.last_modified_source = "desktop-link"
        profile.last_modified_by = "catalog-import"
        profile.save(
            update_fields=[
                "desktop_product_id",
                "last_modified_source",
                "last_modified_by",
                "updated_at",
            ]
        )

    return product
