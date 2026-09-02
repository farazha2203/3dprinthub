from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from store.epic49_catalog_profile import ensure_admin_catalog_profile
from store.models import Category, Product

from .model_policy import provider_key, resolve_product_model


def _profile(product: Product):
    try:
        return product.catalog_profile
    except Exception:
        return None


def _source_payload(product: Product) -> dict[str, Any]:
    profile = _profile(product)
    materials: list[str] = []
    colors: list[str] = []
    for variant in (
        product.variants.filter(is_active=True)
        .select_related("material", "color")
        .order_by("id")
    ):
        material = str(getattr(variant.material, "name", "") or "").strip()
        color = str(getattr(variant.color, "name", "") or "").strip()
        if material and material not in materials:
            materials.append(material)
        if color and color not in colors:
            colors.append(color)

    specs = {}
    if profile is not None and isinstance(profile.technical_features, dict):
        specs.update(profile.technical_features)
    if str(product.dimensions or "").strip():
        specs.setdefault("dimensions", str(product.dimensions).strip())

    tags = []
    for token in str(product.hashtags or "").replace(",", " ").split():
        value = token.strip().lstrip("#")
        if value and value not in tags:
            tags.append(value)

    return {
        "source_title": str(
            product.title_en or product.title or product.sku or ""
        ).strip(),
        "source_description": str(
            product.description_en
            or product.short_description_en
            or product.description
            or product.short_description
            or ""
        ).strip(),
        "source_categories": [str(product.category.name or "")],
        "source_category": str(product.category.name or ""),
        "source_specs": specs,
        "source_tags": tags,
        "author_name": str(product.source_attribution or "").strip(),
        "license_name": str(
            getattr(profile, "license_name", "") if profile else ""
        ).strip(),
        "estimated_weight_grams": None,
        "estimated_print_minutes": None,
        "selected_materials": materials,
        "selected_colors": colors,
    }


def build_site_product_proposal(product: Product) -> dict[str, Any]:
    # Import the transport-backed service only for an explicit AI Generate
    # request. Normal Django startup/admin/product traffic must not depend on
    # the optional provider HTTP client being importable.
    from catalog_center.app.openai_content import AIContentService

    selection = resolve_product_model()
    key = provider_key(selection.provider)
    categories = list(
        Category.objects.filter(is_active=True)
        .order_by("sort_order", "name")
        .values("slug", "name")
    )
    image_count = 1 + product.images.count() if product.main_image else product.images.count()
    service = AIContentService(
        key,
        model=selection.model,
        provider=selection.provider,
        product_id=int(product.pk),
    )
    content = service.enrich_product(
        _source_payload(product),
        categories,
        image_count=image_count,
        image_urls=[],
        mode="commerce",
    )
    # Provider/model are returned for operator diagnostics only. They are not
    # copied into public Product text or technical_notes.
    return {
        "provider": selection.provider,
        "model": selection.model,
        "free": selection.free,
        "pricing": dict(selection.pricing or {}),
        "selection_reason": selection.reason,
        "content": {
            key: value
            for key, value in dict(content or {}).items()
            if not str(key).startswith("_ai_")
        },
    }


def _spec_dict(content: dict[str, Any]) -> dict[str, str]:
    output: dict[str, str] = {}
    for item in content.get("specs_fa") or []:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()
        value = str(item.get("value") or "").strip()
        if key and value:
            output[key] = value
    return output


@transaction.atomic
def apply_site_product_proposal(
    product: Product,
    proposal: dict[str, Any],
    *,
    actor: str = "admin",
) -> dict[str, Any]:
    content = dict((proposal or {}).get("content") or {})
    if not content:
        raise ValueError("AI proposal is empty.")

    # Deliberate safe boundary: AI may edit content/SEO only. Price, stock,
    # material/color choices, source/license truth and publish status remain
    # operator/business-engine owned.
    mapping = {
        "title": str(content.get("title_fa") or "").strip()[:220],
        "short_description": str(
            content.get("short_description_fa") or ""
        ).strip()[:350],
        "description": str(content.get("description_fa") or "").strip(),
        "meta_title": str(content.get("seo_title_fa") or "").strip()[:180],
        "meta_description": str(
            content.get("seo_description_fa") or ""
        ).replace("\n", " ").strip()[:320],
        "og_title": str(content.get("seo_title_fa") or "").strip()[:180],
        "og_description": str(
            content.get("seo_description_fa") or ""
        ).replace("\n", " ").strip()[:320],
    }
    keywords = [
        str(item or "").strip()
        for item in (content.get("target_keywords_fa") or [])
        if str(item or "").strip()
    ]
    hashtags = [
        str(item or "").strip()
        for item in (content.get("hashtags_fa") or [])
        if str(item or "").strip()
    ]
    if keywords:
        mapping["seo_focus_keyword"] = keywords[0][:180]
    if hashtags:
        mapping["hashtags"] = " ".join(hashtags)[:1000]

    changed_product: list[str] = []
    for field, value in mapping.items():
        if value and getattr(product, field) != value:
            setattr(product, field, value)
            changed_product.append(field)
    if changed_product:
        product.save(update_fields=[*changed_product, "updated_at"])

    profile = ensure_admin_catalog_profile(product, actor=actor, bump_revision=False)
    changed_profile: list[str] = []
    use_description = str(content.get("use_description_fa") or "").strip()
    specs = _spec_dict(content)
    slider = (
        dict(content.get("homepage_slider_seo") or {})
        if isinstance(content.get("homepage_slider_seo"), dict)
        else {}
    )

    existing_specs = (
        dict(profile.technical_features)
        if isinstance(profile.technical_features, dict)
        else {}
    )
    # AI may translate/add source-grounded labels, but an operator-entered fact
    # already present on the canonical Site profile always wins on key conflict.
    merged_specs = {**specs, **existing_specs}

    profile_values = {
        "use_description": use_description,
        "technical_features": merged_specs,
        "keywords": keywords,
        "homepage_slider_title_fa": str(slider.get("title_fa") or "").strip()[:220],
        "homepage_slider_description_fa": str(
            slider.get("description_fa") or ""
        ).strip()[:480],
        "homepage_slider_alt_text": str(
            slider.get("image_alt_fa") or ""
        ).strip()[:240],
        "homepage_slider_button_text": str(
            slider.get("button_text_fa") or ""
        ).strip()[:80],
        "homepage_slider_focus_keyword": str(
            slider.get("focus_keyword_fa") or ""
        ).strip()[:180],
    }
    technical_summary = " ".join(
        [
            use_description,
            *[
                str(item or "").strip()
                for item in (content.get("sales_bullets") or [])
                if str(item or "").strip()
            ][:3],
        ]
    ).strip()
    if hasattr(profile, "technical_summary_fa"):
        profile_values["technical_summary_fa"] = technical_summary

    for field, value in profile_values.items():
        if value in ("", [], {}) and field not in {"technical_features", "keywords"}:
            continue
        if getattr(profile, field, None) != value:
            setattr(profile, field, value)
            changed_profile.append(field)

    profile.sync_revision = max(1, int(profile.sync_revision or 1)) + 1
    profile.last_modified_source = "admin"
    profile.last_modified_by = str(actor or "admin")[:120]
    profile.last_synced_at = timezone.now()
    profile.save(
        update_fields=[
            *changed_profile,
            "sync_revision",
            "last_modified_source",
            "last_modified_by",
            "last_synced_at",
            "updated_at",
        ]
    )

    image_alts = [
        str(item or "").strip()
        for item in (content.get("image_alt_texts") or [])
        if str(item or "").strip()
    ]
    image_updates = 0
    for index, image in enumerate(product.images.order_by("sort_order", "id")):
        if index >= len(image_alts):
            break
        alt = image_alts[index][:220]
        if alt and image.alt_text != alt:
            image.alt_text = alt
            image.save(update_fields=["alt_text"])
            image_updates += 1

    return {
        "product_id": int(product.pk),
        "changed_product_fields": changed_product,
        "changed_profile_fields": changed_profile,
        "image_alt_updates": image_updates,
        "provider": str((proposal or {}).get("provider") or ""),
        "model": str((proposal or {}).get("model") or ""),
    }
