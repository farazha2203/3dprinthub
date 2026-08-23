from __future__ import annotations

import json
import re
from typing import Any

from .ai_providers import AIProviderClient, response_output_text

SLIDER_SEO_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title_fa": {"type": "string"},
        "description_fa": {"type": "string"},
        "image_alt_fa": {"type": "string"},
        "button_text_fa": {"type": "string"},
        "focus_keyword_fa": {"type": "string"},
    },
    "required": [
        "title_fa",
        "description_fa",
        "image_alt_fa",
        "button_text_fa",
        "focus_keyword_fa",
    ],
}

CONTENT_SCHEMA = {
    "type":"object","additionalProperties":False,
    "properties":{
        "title_fa":{"type":"string"},"short_description_fa":{"type":"string"},"description_fa":{"type":"string"},
        "use_description_fa":{"type":"string"},
        "categories_fa":{"type":"array","items":{"type":"string"}},
        "specs_fa":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{"key":{"type":"string"},"value":{"type":"string"}},"required":["key","value"]}},
        "tags_fa":{"type":"array","items":{"type":"string"}},
        "hashtags_fa":{"type":"array","items":{"type":"string"}},
        "target_keywords_fa":{"type":"array","items":{"type":"string"},"maxItems":12},
        "suggested_category_slug":{"type":"string"},"category_confidence":{"type":"number","minimum":0,"maximum":1},
        "seo_title_fa":{"type":"string"},"seo_description_fa":{"type":"string"},
        "sales_bullets":{"type":"array","items":{"type":"string"},"maxItems":8},
        "social_caption_fa":{"type":"string"},"image_alt_texts":{"type":"array","items":{"type":"string"}},
        "content_notes":{"type":"array","items":{"type":"string"}},
        "use_case_class":{"type":"string"},
        "material_recommendations":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
            "material":{"type":"string"},"score":{"type":"integer","minimum":0,"maximum":100},"recommended":{"type":"boolean"},"reason_fa":{"type":"string"}
        },"required":["material","score","recommended","reason_fa"]}},
        "homepage_slider_seo": SLIDER_SEO_SCHEMA,
    },
    "required":["title_fa","short_description_fa","description_fa","use_description_fa","categories_fa","specs_fa","tags_fa","hashtags_fa","target_keywords_fa","suggested_category_slug","category_confidence","seo_title_fa","seo_description_fa","sales_bullets","social_caption_fa","image_alt_texts","content_notes","use_case_class","material_recommendations","homepage_slider_seo"]
}

_GENERIC_TITLE_KEYS = {
    "محصول چاپ سه بعدی",
    "محصول چاپ سه‌بعدی",
    "مدل چاپ سه بعدی",
    "مدل چاپ سه‌بعدی",
    "فایل چاپ سه بعدی",
    "فایل چاپ سه‌بعدی",
    "محصول سه بعدی",
    "محصول سه‌بعدی",
}


def _normalize_title(value: str) -> str:
    return " ".join(str(value or "").replace("ي", "ی").replace("ك", "ک").replace("‌", " ").split()).casefold()


def validate_content_pack(result: dict[str, Any], source_title: str = "") -> dict[str, Any]:
    """Reject generic/empty AI output before it can downgrade a product page."""
    title = str(result.get("title_fa") or "").strip()
    normalized = _normalize_title(title)
    generic = {_normalize_title(item) for item in _GENERIC_TITLE_KEYS}
    if not title or normalized in generic:
        raise RuntimeError(
            "هوش مصنوعی عنوان فارسی عمومی/نامعتبر برگرداند. عنوان باید هویت واقعی محصول را از عنوان منبع حفظ کند؛ Provider/Model را بررسی و دوباره اجرا کن."
        )
    if not re.search(r"[\u0600-\u06ff]", title):
        raise RuntimeError("عنوان فارسی تولیدشده فاقد متن فارسی معتبر است.")
    if str(source_title or "").strip() and len(title) < 6:
        raise RuntimeError("عنوان فارسی تولیدشده بیش از حد کوتاه است و هویت محصول را منتقل نمی‌کند.")
    for key, label in (
        ("seo_title_fa", "SEO Title"),
        ("seo_description_fa", "SEO Description"),
    ):
        value = str(result.get(key) or "").strip()
        if not value:
            raise RuntimeError(f"{label} فارسی توسط هوش مصنوعی خالی برگشت.")
    return result


class AIContentService:
    def __init__(self, api_key:str, model:str="", provider:str="openai", product_id:int|None=None):
        self.client=AIProviderClient(provider,api_key,model,product_id=product_id)
        self.model=model
        self.provider=provider
        self.product_id=product_id

    def test_connection(self)->str:
        r=self.client.test_connection(self.model)
        return f"{r['provider_label']} connected | model={r['model']} | models={r['models_count']} | sample={r['sample']}"

    def list_models(self)->list[str]: return self.client.list_models()

    def enrich_product(self, source:dict[str,Any], local_categories:list[dict[str,str]], image_count:int=0, image_urls:list[str]|None=None, mode:str="commerce")->dict[str,Any]:
        payload={
            "source_title":source.get("source_title") or "","source_description":source.get("source_description") or "",
            "source_categories":source.get("source_categories") or [],"source_category":source.get("source_category") or "",
            "source_specs":source.get("source_specs") or {},"source_tags":source.get("source_tags") or [],
            "similar_persian_keywords":source.get("similar_persian_keywords") or [],
            "author_name":source.get("author_name") or "","license_name":source.get("license_name") or "",
            "source_price":source.get("source_price"),"source_currency":source.get("source_currency") or "",
            "estimated_weight_grams":source.get("estimated_weight_grams"),"estimated_print_minutes":source.get("estimated_print_minutes"),
            "selected_materials":source.get("selected_materials") or [],
            "selected_colors":source.get("selected_colors") or [],
            "image_count":image_count,"allowed_site_categories":[{"slug":x.get("slug",""),"name":x.get("name","")} for x in local_categories],
        }
        content=[{"type":"input_text","text":json.dumps(payload,ensure_ascii=False)}]
        for u in (image_urls or [])[:4]:
            if str(u).startswith(("http://","https://")): content.append({"type":"input_image","image_url":str(u),"detail":"auto"})
        strict_translate = mode == "translate" or (mode or "commerce").lower() == "translate"
        instructions=(
            ("You are a precise Persian technical translator. " if strict_translate else "") +
            "You are a senior Persian ecommerce and technical SEO editor for 3DPrintHub, an Iranian professional 3D-printing ecommerce site. "
            "SOURCE TITLE IS AUTHORITATIVE PRODUCT IDENTITY. title_fa must faithfully translate the concrete object, use, theme/character/style, and meaningful modifiers from source_title into natural Persian. "
            "Never replace a specific source title with generic phrases such as 'محصول چاپ سه‌بعدی', 'مدل چاپ سه‌بعدی', 'فایل چاپ سه‌بعدی' or equivalent vague wording. Keep meaningful proper names such as character/franchise/model names when translation would lose identity. "
            "The visible Persian H1, SEO title, SEO description, headings and image alt text must all describe the same real product consistently. "
            "Never invent dimensions, weight, compatibility, license, source rating, file availability, price, material or color. Preserve engineering names and units. "
            "Translate all source specifications and category paths to natural Persian. Choose suggested_category_slug only from allowed_site_categories. "
            "use_description_fa must explain the real use of this exact product from source facts, not a generic 3D-printing description. "
            "Create a unique, descriptive and concise SEO title that leads with the real product/topic and reads naturally for a human. Do not keyword-stuff or repeat boilerplate across products. "
            "Create a page-specific SEO description that accurately summarizes this exact product and useful purchase/use context; do not output a comma-separated keyword list. "
            "When target_keywords_fa is supported, suggest 5 to 12 natural Persian commercial/search-intent phrases suitable for product SEO and internal content planning; prefer phrases containing buying, ordering, price, product type, use case, and only the selected_materials/selected_colors that are explicitly present in the input. Never use target_keywords_fa as obsolete HTML meta-keywords stuffing. "
            "similar_persian_keywords are editorial hints collected from previously reviewed products in the same local category. Reuse or adapt only phrases that are semantically relevant to this product; never treat them as product facts, never copy irrelevant phrases, and never let them override the current source facts. "
            "selected_materials and selected_colors are factual operator selections. You may use them in SEO phrases when relevant, but never add a material or color that is not present in those lists. "
            "Image alt texts must be concise, factual Persian descriptions of this product/angle and must not be keyword lists. "
            "Always create homepage_slider_seo as a separate homepage hero content pack: title_fa must be concise and factual, description_fa must be a short useful Persian summary, image_alt_fa must accurately describe the product/image without keyword stuffing, button_text_fa must be a short action label, and focus_keyword_fa must be one natural target phrase. "
            "For homepage_slider_seo avoid price, availability, performance or technical claims unless they are explicitly supported by source facts. Do not duplicate the full product SEO text; write compact hero copy suitable for an H2, a short paragraph, image alt text and an internal product link on the homepage. "
            "Classify the use case and recommend printable materials conservatively. Do not recommend expensive engineering materials such as PPS-CF for ordinary home decor unless source facts require high heat/chemical/mechanical performance. "
            "For automotive outdoor/high-heat parts prefer suitable heat/UV-capable choices; for flexible parts consider TPU; for gears/load/wear consider engineering nylons/composites when justified. "
            "Explain each recommendation briefly in Persian. Missing facts go in content_notes. "
            + ("Use faithful translation; do not add marketing claims. " if strict_translate else "Write persuasive but factual Persian ecommerce copy. ")
        )
        result,model=self.client.structured_response(instructions=instructions,input_content=content,schema=CONTENT_SCHEMA,schema_name="catalog_content_pack_v871",preferred_model=self.model)
        validate_content_pack(result, payload["source_title"])
        result["_ai_provider"]=self.provider; result["_ai_model"]=model
        return result

# compatibility
OpenAIContentService=AIContentService
