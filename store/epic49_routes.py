from __future__ import annotations

from django.shortcuts import get_object_or_404

from .models import Product
from .views import product_detail_view


def product_detail_by_id_view(request, pk: int):
    """Stable public fallback for operational verification and legacy links."""
    product = get_object_or_404(Product, pk=pk, is_active=True, category__is_active=True)
    return product_detail_view(request, product.slug)
