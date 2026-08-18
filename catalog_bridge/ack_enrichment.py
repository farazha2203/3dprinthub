from __future__ import annotations

from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import Product
from website.models import HomepageHeroSlide


def enrich_import_ack(ack):
    if not isinstance(ack, dict):
        return ack
    for item in ack.get("items") or []:
        if not isinstance(item, dict):
            continue
        raw_product_id = item.get("product_id") or item.get("server_product_id")
        try:
            product_id = int(raw_product_id or 0)
        except Exception:
            product_id = 0
        if not product_id:
            continue
        product = Product.objects.filter(pk=product_id).first()
        if product is None:
            continue
        profile = ProductCatalogProfile.objects.filter(product=product).first()
        item["server_product_id"] = product.pk
        item["product_revision"] = int(getattr(profile, "sync_revision", 0) or 0)
        asset = None
        try:
            asset = product.imported_source_asset
        except Exception:
            pass
        slide = None
        if asset is not None:
            slide = HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()
        item["slider_id"] = getattr(slide, "pk", None)
        item["slider_revision"] = int(getattr(slide, "sync_revision", 0) or 0)
    ack["sync_contract"] = "epic49-unified-v1"
    return ack
