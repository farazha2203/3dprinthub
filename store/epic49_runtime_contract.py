from __future__ import annotations

from django.urls import reverse


def install() -> None:
    """Install small runtime properties without rewriting mature model modules."""
    from store.models import Product
    from website.models import HomepageHeroSlide

    def target_url(self):
        """Resolve the canonical active Store URL without trusting stale relation cache.

        Catalog Center may replace a legacy/unicode slug with the ASCII public slug in
        the same request that creates/updates a homepage slide.  Read Product by id so
        a cached relation cannot emit the previous slug.  Phase 49.2A retired the
        external ready-model detail route, therefore a legacy slide without an active
        Product falls back to the live Store list instead of a removed route.
        """
        try:
            product_id = getattr(self.asset, "product_id", None)
        except Exception:
            product_id = None
        if product_id:
            try:
                product = Product.objects.filter(pk=product_id, is_active=True).first()
            except Exception:
                product = None
            if product is not None:
                try:
                    return product.get_absolute_url()
                except Exception:
                    pass
        return reverse("store:product_list")

    HomepageHeroSlide.target_url = property(target_url)
