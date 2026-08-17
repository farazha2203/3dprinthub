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
        # Phase 49.2A retired the public external ready-model detail route.
        # A legacy hero asset without a live Product now lands on the active
        # store instead of generating a broken reverse()/404 target.
        return reverse("store:product_list")

    HomepageHeroSlide.target_url = property(target_url)
