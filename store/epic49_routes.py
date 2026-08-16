from __future__ import annotations

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from .converters import UnicodeSlugConverter
from .epic49_catalog_profile import ProductCatalogProfile
from .models import Product
from .views import product_detail_view


def product_detail_compat_view(request, slug: str):
    """Serve the stable ASCII slug and permanently redirect known legacy slugs."""
    normalized = UnicodeSlugConverter().to_python(str(slug or ""))
    product = Product.objects.filter(
        slug=normalized,
        is_active=True,
        category__is_active=True,
    ).first()
    if product is not None:
        return product_detail_view(request, product.slug)

    profile = (
        ProductCatalogProfile.objects.filter(
            legacy_slug=normalized,
            product__is_active=True,
            product__category__is_active=True,
        )
        .select_related("product")
        .order_by("pk")
        .first()
    )
    if profile is not None:
        return redirect(profile.product.get_absolute_url(), permanent=True)
    raise Http404("Product not found")


def product_detail_by_id_view(request, pk: int):
    """Stable public fallback for operational verification and legacy links."""
    product = get_object_or_404(Product, pk=pk, is_active=True, category__is_active=True)
    return product_detail_view(request, product.slug)
