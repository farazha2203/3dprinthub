from __future__ import annotations

from django.urls import reverse


def install() -> None:
    """Install small runtime properties without rewriting mature model modules."""
    from website.models import HomepageHeroSlide

    def target_url(self):
        try:
            product = self.asset.product
        except Exception:
            product = None
        if product is not None and getattr(product, "is_active", False):
            try:
                return product.get_absolute_url()
            except Exception:
                pass
        return reverse("store:external_catalog_detail", args=[self.asset_id])

    HomepageHeroSlide.target_url = property(target_url)
