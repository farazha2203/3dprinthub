from __future__ import annotations

import json

from .openai_content import AIContentService, CONTENT_SCHEMA


def _nonempty(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value not in (None, "")


def missing_commerce_fields(pack: dict, image_count: int = 0) -> list[str]:
    checks = {
        "title_fa": pack.get("title_fa"),
        "short_description_fa": pack.get("short_description_fa"),
        "description_fa": pack.get("description_fa"),
        "categories_fa": pack.get("categories_fa"),
        "tags_fa": pack.get("tags_fa"),
        "hashtags_fa": pack.get("hashtags_fa"),
        "target_keywords_fa": pack.get("target_keywords_fa"),
        "seo_title_fa": pack.get("seo_title_fa"),
        "seo_description_fa": pack.get("seo_description_fa"),
        "sales_bullets": pack.get("sales_bullets"),
        "social_caption_fa": pack.get("social_caption_fa"),
        "material_recommendations": pack.get("material_recommendations"),
        "homepage_slider_seo": pack.get("homepage_slider_seo"),
    }
    missing = [key for key, value in checks.items() if not _nonempty(value)]
    if len(pack.get("target_keywords_fa") or []) < 3 and "target_keywords_fa" not in missing:
        missing.append("target_keywords_fa")
    if image_count > 0 and len(pack.get("image_alt_texts") or []) < min(int(image_count), 10):
        missing.append("image_alt_texts")
    slider = pack.get("homepage_slider_seo")
    if isinstance(slider, dict):
        for key in ("title_fa", "description_fa", "image_alt_fa", "button_text_fa", "focus_keyword_fa"):
            if not str(slider.get(key) or "").strip():
                marker = f"homepage_slider_seo.{key}"
                if marker not in missing:
                    missing.append(marker)
    return missing


def _safe_text_list(values) -> list[str]:
    output: list[str] = []
    seen = set()
    for value in values or []:
        text = str(value or "").strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def _deterministic_fill(pack: dict, source: dict, image_count: int) -> dict:
    """Fill editorial derivatives only; factual operator fields are never invented."""
    result = dict(pack)
    title = str(result.get("title_fa") or source.get("source_title") or "محصول چاپ سه‌بعدی").strip()
    description = str(
        result.get("description_fa")
        or result.get("short_description_fa")
        or source.get("source_description")
        or title
    ).strip()
    short = str(result.get("short_description_fa") or "").strip() or description[:500]
    result["title_fa"] = title
    result["description_fa"] = description
    result["short_description_fa"] = short

    categories = _safe_text_list(result.get("categories_fa") or source.get("source_categories") or [])
    if not categories and source.get("source_category"):
        categories = [str(source.get("source_category")).strip()]
    result["categories_fa"] = categories

    keywords = _safe_text_list(result.get("target_keywords_fa") or [])
    if len(keywords) < 3:
        candidates = [f"خرید {title}", f"سفارش {title}", f"قیمت {title}"]
        candidates.extend(f"{title} {item}" for item in source.get("selected_materials") or [])
        keywords = _safe_text_list([*keywords, *candidates])[:12]
    result["target_keywords_fa"] = keywords

    tags = _safe_text_list(result.get("tags_fa") or [])
    if not tags:
        tags = _safe_text_list([title, *categories, *keywords[:4]])
    result["tags_fa"] = tags[:12]

    hashtags = _safe_text_list(result.get("hashtags_fa") or [])
    if not hashtags:
        hashtags = [
            "#" + "".join(ch for ch in tag.replace(" ", "_") if ch not in "#,;")
            for tag in tags[:8]
            if tag
        ]
    result["hashtags_fa"] = hashtags[:12]

    if not str(result.get("seo_title_fa") or "").strip():
        result["seo_title_fa"] = title[:180]
    if not str(result.get("seo_description_fa") or "").strip():
        result["seo_description_fa"] = short[:320]
    if not _safe_text_list(result.get("sales_bullets") or []):
        result["sales_bullets"] = [
            short[:220],
            "قابل سفارش برای چاپ سه‌بعدی بر اساس گزینه‌های تأییدشده اپراتور.",
        ]
    if not str(result.get("social_caption_fa") or "").strip():
        result["social_caption_fa"] = short

    alts = _safe_text_list(result.get("image_alt_texts") or [])
    for index in range(len(alts) + 1, min(max(0, int(image_count)), 10) + 1):
        alts.append(f"{title} - نمای {index}")
    result["image_alt_texts"] = alts[:10]

    recs = result.get("material_recommendations")
    if not isinstance(recs, list) or not recs:
        selected = _safe_text_list(source.get("selected_materials") or [])
        result["material_recommendations"] = [
            {
                "material": material,
                "score": 70,
                "recommended": True,
                "reason_fa": "این متریال توسط اپراتور برای این محصول انتخاب شده و به‌عنوان گزینه واقعی ثبت شده است.",
            }
            for material in selected[:8]
        ]

    slider = result.get("homepage_slider_seo")
    if not isinstance(slider, dict):
        slider = {}
    slider = dict(slider)
    slider.setdefault("title_fa", title[:120])
    slider.setdefault("description_fa", short[:220])
    slider.setdefault("image_alt_fa", alts[0] if alts else title)
    slider.setdefault("button_text_fa", "مشاهده محصول")
    slider.setdefault("focus_keyword_fa", keywords[0] if keywords else title)
    result["homepage_slider_seo"] = slider
    return result


def install() -> None:
    if getattr(AIContentService, "_phase49_3c_completeness_installed", False):
        return
    original = AIContentService.enrich_product

    def enrich_product(self, source, local_categories, image_count=0, image_urls=None, mode="commerce"):
        result = original(
            self,
            source,
            local_categories,
            image_count=image_count,
            image_urls=image_urls,
            mode=mode,
        )
        if str(mode or "commerce").lower() != "commerce":
            return result

        missing = missing_commerce_fields(result, image_count)
        if missing:
            repair_input = {
                "source": {
                    "source_title": source.get("source_title") or "",
                    "source_description": source.get("source_description") or "",
                    "source_categories": source.get("source_categories") or [],
                    "source_specs": source.get("source_specs") or {},
                    "selected_materials": source.get("selected_materials") or [],
                    "selected_colors": source.get("selected_colors") or [],
                    "image_count": min(max(0, int(image_count or 0)), 10),
                },
                "current_pack": result,
                "missing_or_empty_fields": missing,
            }
            instructions = (
                "Repair this Persian 3DPrintHub ecommerce content pack. Return the FULL object matching the schema. "
                "Keep correct existing fields and fill every listed missing editorial field with factual Persian content. "
                "Do not invent price, dimensions, stock, license, selected materials, selected colors, compatibility or performance claims. "
                "material_recommendations are suggestions only and may be inferred conservatively from the described use case. "
                "image_alt_texts must contain one concise non-spam Persian alt per requested image. "
                "tags_fa, hashtags_fa, target_keywords_fa, sales_bullets and material_recommendations must not be empty."
            )
            try:
                repaired, model = self.client.structured_response(
                    instructions=instructions,
                    input_content=[{"type": "input_text", "text": json.dumps(repair_input, ensure_ascii=False)}],
                    schema=CONTENT_SCHEMA,
                    schema_name="catalog_content_pack_v871_repair",
                    preferred_model=self.model,
                )
                for key in missing:
                    root = key.split(".", 1)[0]
                    if _nonempty(repaired.get(root)):
                        result[root] = repaired[root]
                result["_ai_model"] = model
            except Exception:
                pass

        result = _deterministic_fill(result, source, image_count)
        result["_ai_provider"] = self.provider
        result["_ai_model"] = result.get("_ai_model") or self.model
        result["_phase49_3c_missing_after_repair"] = missing_commerce_fields(result, image_count)
        return result

    AIContentService.enrich_product = enrich_product
    AIContentService._phase49_3c_completeness_installed = True
