from __future__ import annotations


def install() -> None:
    from django.db.models.signals import pre_save

    from store import epic49_catalog_profile as profile_module
    from store import epic49_publish_options as publish_module
    from store.phase49_persian_sales_copy import (
        build_product_sales_seo,
        build_slider_sales_copy,
        safe_persian_text,
    )

    if getattr(profile_module, "_phase49_persian_sales_installed", False):
        return

    def homepage_slider_seo(data: dict, product) -> dict:
        return build_slider_sales_copy(data, product=product)

    def slider_seo_from_data(data: dict, product) -> dict:
        resolved = build_slider_sales_copy(data, product=product)
        return {
            "title": resolved["title_fa"],
            "description": resolved["description_fa"],
            "alt": resolved["image_alt_fa"],
            "button": resolved["button_text_fa"],
            "focus": resolved["focus_keyword_fa"],
        }

    def sync_product_seo(product, asset, data: dict) -> None:
        resolved = build_product_sales_seo(data, product=product, asset=asset)
        product.meta_title = resolved["meta_title"] or product.meta_title
        product.meta_description = resolved["meta_description"] or product.meta_description
        product.seo_focus_keyword = resolved["focus_keyword"] or product.seo_focus_keyword
        product.og_title = resolved["meta_title"] or product.title
        product.og_description = resolved["meta_description"] or product.short_description
        product.editorial_source_url = str(data.get("source_url") or getattr(asset, "source_url", ""))[:1000]
        product.source_attribution = str(
            data.get("author_name")
            or getattr(asset, "author_name", "")
            or getattr(getattr(asset, "source", None), "name", "")
            or ""
        )[:220]
        product.hashtags = " ".join(resolved["hashtags"])
        product.canonical_url = ""
        product.save(
            update_fields=[
                "meta_title",
                "meta_description",
                "seo_focus_keyword",
                "og_title",
                "og_description",
                "editorial_source_url",
                "source_attribution",
                "hashtags",
                "canonical_url",
                "updated_at",
            ]
        )

    def normalize_profile_before_save(sender, instance, **_kwargs):
        """One save gate for Desktop, Bridge, Admin and Hero mirror writes."""
        try:
            product = instance.product
        except Exception:
            product = None

        asset = None
        desktop = {}
        if product is not None and getattr(product, "pk", None):
            try:
                from store.models import ImportedPrintAsset

                asset = ImportedPrintAsset.objects.filter(product_id=product.pk).order_by("id").first()
                if asset is not None:
                    payload = asset.source_payload or {}
                    if isinstance(payload, dict):
                        candidate = payload.get("desktop_catalog_v85") or {}
                        if isinstance(candidate, dict):
                            desktop = dict(candidate)
            except Exception:
                asset = None
                desktop = {}

        data = dict(desktop)
        field_map = {
            "homepage_slider_title_fa": 220,
            "homepage_slider_description_fa": 1200,
            "homepage_slider_alt_text": 240,
            "homepage_slider_button_text": 80,
            "homepage_slider_focus_keyword": 180,
        }
        for name, limit in field_map.items():
            value = safe_persian_text(getattr(instance, name, ""), limit=limit)
            if value:
                data[name] = value

        keywords = getattr(instance, "keywords", None)
        if keywords and "keywords_json" not in data:
            data["keywords_json"] = keywords

        resolved = build_slider_sales_copy(data, product=product, asset=asset)
        instance.homepage_slider_title_fa = resolved["title_fa"]
        instance.homepage_slider_description_fa = resolved["description_fa"]
        instance.homepage_slider_alt_text = resolved["image_alt_fa"]
        instance.homepage_slider_button_text = resolved["button_text_fa"]
        instance.homepage_slider_focus_keyword = resolved["focus_keyword_fa"]

    publish_module._homepage_slider_seo = homepage_slider_seo
    profile_module._slider_seo_from_data = slider_seo_from_data
    profile_module.sync_product_seo = sync_product_seo

    pre_save.connect(
        normalize_profile_before_save,
        sender=profile_module.ProductCatalogProfile,
        weak=False,
        dispatch_uid="phase49_persian_sales_profile_normalizer",
    )

    profile_module._phase49_persian_sales_installed = True
