from __future__ import annotations

from django.urls import reverse


def install() -> None:
    """Install small runtime properties without rewriting mature model modules."""
    from store.models import Product
    from website.models import HomepageHeroSlide

    def target_url(self):
        """Resolve the current canonical store URL without trusting a stale relation cache.

        Catalog sync can replace a legacy/unicode slug with the ASCII public slug in the
        same request that creates or updates a homepage slide.  ``self.asset.product`` may
        already be cached with the previous slug, so always read the active Product by its
        id before generating the target URL.
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
        return reverse("store:external_catalog_detail", args=[self.asset_id])

    HomepageHeroSlide.target_url = property(target_url)
