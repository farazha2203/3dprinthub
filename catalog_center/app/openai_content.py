from __future__ import annotations

import json
from typing import Any

from .ai_providers import AIProviderClient, response_output_text

CONTENT_SCHEMA = {
    "type":"object","additionalProperties":False,
    "properties":{
        "title_fa":{"type":"string"},"short_description_fa":{"type":"string"},"description_fa":{"type":"string"},
        "categories_fa":{"type":"array","items":{"type":"string"}},
        "specs_fa":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{"key":{"type":"string"},"value":{"type":"string"}},"required":["key","value"]}},
        "tags_fa":{"type":"array","items":{"type":"string"}},
        "hashtags_fa":{"type":"array","items":{"type":"string"}},
        "suggested_category_slug":{"type":"string"},"category_confidence":{"type":"number","minimum":0,"maximum":1},
        "seo_title_fa":{"type":"string"},"seo_description_fa":{"type":"string"},
        "sales_bullets":{"type":"array","items":{"type":"string"},"maxItems":8},
        "social_caption_fa":{"type":"string"},"image_alt_texts":{"type":"array","items":{"type":"string"}},
        "content_notes":{"type":"array","items":{"type":"string"}},
        "use_case_class":{"type":"string"},
        "material_recommendations":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{
            "material":{"type":"string"},"score":{"type":"integer","minimum":0,"maximum":100},"recommended":{"type":"boolean"},"reason_fa":{"type":"string"}
        },"required":["material","score","recommended","reason_fa"]}}
    },
    "required":["title_fa","short_description_fa","description_fa","categories_fa","specs_fa","tags_fa","hashtags_fa","suggested_category_slug","category_confidence","seo_title_fa","seo_description_fa","sales_bullets","social_caption_fa","image_alt_texts","content_notes","use_case_class","material_recommendations"]
}

class AIContentService:
    def __init__(self, api_key:str, model:str="", provider:str="openai"):
        self.client=AIProviderClient(provider,api_key,model)
        self.model=model
        self.provider=provider

    def test_connection(self)->str:
        r=self.client.test_connection(self.model)
        return f"{r['provider_label']} connected | model={r['model']} | models={r['models_count']} | sample={r['sample']}"

    def list_models(self)->list[str]: return self.client.list_models()

    def enrich_product(self, source:dict[str,Any], local_categories:list[dict[str,str]], image_count:int=0, image_urls:list[str]|None=None, mode:str="commerce")->dict[str,Any]:
        payload={
            "source_title":source.get("source_title") or "","source_description":source.get("source_description") or "",
            "source_categories":source.get("source_categories") or [],"source_category":source.get("source_category") or "",
            "source_specs":source.get("source_specs") or {},"source_tags":source.get("source_tags") or [],
            "author_name":source.get("author_name") or "","license_name":source.get("license_name") or "",
            "source_price":source.get("source_price"),"source_currency":source.get("source_currency") or "",
            "estimated_weight_grams":source.get("estimated_weight_grams"),"estimated_print_minutes":source.get("estimated_print_minutes"),
            "image_count":image_count,"allowed_site_categories":[{"slug":x.get("slug",""),"name":x.get("name","")} for x in local_categories],
        }
        content=[{"type":"input_text","text":json.dumps(payload,ensure_ascii=False)}]
        for u in (image_urls or [])[:4]:
            if str(u).startswith(("http://","https://")): content.append({"type":"input_image","image_url":str(u),"detail":"auto"})
        strict_translate = mode == "translate" or (mode or "commerce").lower() == "translate"
        instructions=(
            ("You are a precise Persian technical translator. " if strict_translate else "") +
            "You are a Persian ecommerce content editor and catalog intelligence editor for 3DPrintHub, an Iranian professional 3D-printing ecommerce site. "
            "Never invent dimensions, weight, compatibility, license, source rating, file availability or price. Preserve engineering names and units. "
            "Translate all source specifications and category paths to natural Persian. Choose suggested_category_slug only from allowed_site_categories. "
            "Create useful non-spam SEO title/description, internal tags and Persian social hashtags. "
            "Classify the use case and recommend printable materials conservatively. Do not recommend expensive engineering materials such as PPS-CF for ordinary home decor unless source facts require high heat/chemical/mechanical performance. "
            "For automotive outdoor/high-heat parts prefer suitable heat/UV-capable choices; for flexible parts consider TPU; for gears/load/wear consider engineering nylons/composites when justified. "
            "Explain each recommendation briefly in Persian. Missing facts go in content_notes. "
            + ("Use faithful translation; do not add marketing claims. " if strict_translate else "Write persuasive but factual Persian ecommerce copy. ")
        )
        result,model=self.client.structured_response(instructions=instructions,input_content=content,schema=CONTENT_SCHEMA,schema_name="catalog_content_pack_v84",preferred_model=self.model)
        result["_ai_provider"]=self.provider; result["_ai_model"]=model
        return result

# compatibility
OpenAIContentService=AIContentService
