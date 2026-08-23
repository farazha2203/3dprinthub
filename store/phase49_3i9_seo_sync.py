from __future__ import annotations

import json


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def apply_catalog_seo_to_product(product, asset, data: dict) -> list[str]:
    """Map verified desktop editorial/SEO fields onto the public Product model."""
    if product is None:
        return []
    updates: list[str] = []

    # `source_name` means the publishing/source website (e.g. MakerWorld), not
    # the individual designer. The creator remains available separately on the
    # imported asset and image metadata.
    source_name = str(
        data.get("source_name")
        or getattr(getattr(asset, "source", None), "name", "")
        or data.get("source_code")
        or ""
    ).strip()
    source_url = str(data.get("source_url") or getattr(asset, "source_url", "") or "").strip()
    seo_title = str(data.get("seo_title_fa") or "").strip()
    seo_description = str(data.get("seo_description_fa") or "").strip()
    keywords = [
        str(item or "").strip()
        for item in _json_list(data.get("keywords_json"))
        if str(item or "").strip()
    ]

    assignments = (
        ("source_name", source_name[:120]),
        ("source_attribution", source_name[:220]),
        ("editorial_source_url", source_url),
        ("meta_title", seo_title[:180]),
        ("meta_description", seo_description[:320]),
        ("og_title", seo_title[:180]),
        ("og_description", seo_description[:320]),
        ("seo_focus_keyword", (keywords[0] if keywords else "")[:180]),
    )
    for field, value in assignments:
        if not value or not hasattr(product, field):
            continue
        if getattr(product, field, None) != value:
            setattr(product, field, value)
            updates.append(field)

    if updates:
        save_fields = list(
            dict.fromkeys(
                updates + (["updated_at"] if hasattr(product, "updated_at") else [])
            )
        )
        product.save(update_fields=save_fields)
    return updates


def install() -> None:
    """Extend mature conversion/visibility boundaries; never create a parallel importer."""
    from . import phase34b_publishing as publishing
    from . import phase49_catalog_visibility as visibility_module

    if getattr(publishing, "_phase49_3i9_seo_sync_installed", False):
        return

    original_convert = publishing.convert_to_fixed_product
    original_visibility = visibility_module.publish_catalog_product_to_store

    def convert_to_fixed_product(asset):
        product = original_convert(asset)
        payload = publishing._desktop_payload(asset)
        apply_catalog_seo_to_product(product, asset, payload)
        return product

    def publish_catalog_product_to_store(product, asset, data):
        result = original_visibility(product, asset, data)
        # Phase37 applies additional intelligence/details between conversion and
        # visibility. Reapply publisher/meta fields here so no legacy author/source
        # compatibility layer can overwrite the final public values.
        apply_catalog_seo_to_product(product, asset, data or publishing._desktop_payload(asset))
        return result

    publishing.convert_to_fixed_product = convert_to_fixed_product
    visibility_module.publish_catalog_product_to_store = publish_catalog_product_to_store
    publishing._phase49_3i9_seo_sync_installed = True
    visibility_module._phase49_3i9_seo_sync_installed = True
