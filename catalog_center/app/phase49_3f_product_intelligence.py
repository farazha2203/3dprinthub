from __future__ import annotations

import json

TECHNICAL_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "technical_summary_fa": {"type": "string"},
        "use_description_fa": {"type": "string"},
        "technical_features": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
            "maxItems": 16,
        },
        "operator_notes": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
    },
    "required": ["technical_summary_fa", "use_description_fa", "technical_features", "operator_notes"],
}


def build_source_facts(row, source: dict) -> dict:
    def value(key, default=""):
        if isinstance(row, dict):
            return row.get(key, default)
        try:
            return row[key]
        except Exception:
            return default

    facts = {
        "source_url": str(value("source_url", "") or ""),
        "source_title": source.get("source_title") or value("source_title", ""),
        "source_description": source.get("source_description") or value("source_description", ""),
        "source_specs": source.get("source_specs") or value("source_specs_json", "{}"),
        "source_categories": source.get("source_categories") or [],
        "source_tags": source.get("source_tags") or [],
        "author_name": source.get("author_name") or value("author_name", ""),
        "license_name": source.get("license_name") or value("license_name", ""),
        "estimated_weight_grams": source.get("estimated_weight_grams") or value("estimated_weight_grams", ""),
        "estimated_print_minutes": source.get("estimated_print_minutes") or value("estimated_print_minutes", ""),
        "existing_title_fa": value("title_fa", ""),
        "existing_short_fa": value("short_description_fa", ""),
    }
    # This is a traceable textual source contract; image URL/binary is excluded.
    return facts


def generate_technical_intelligence(service, row, source: dict) -> dict:
    facts = build_source_facts(row, source)
    instructions = (
        "You are a Persian technical catalog editor for 3DPrintHub. "
        "Use ONLY the verified source facts supplied by the application. The source URL is provenance, not permission to invent or browse unavailable facts. "
        "Turn raw maker/designer text into a concise, useful and customer-friendly Persian technical explanation. "
        "Do not repeat cookies, usernames, social boilerplate, tracking text or meaningless source labels. "
        "Do not invent dimensions, weight, print time, material, compatibility, license, safety, performance or commercial rights. "
        "technical_features must contain only facts supported by source_specs/source_description. If a fact is unclear, put the uncertainty in operator_notes instead of guessing. "
        "use_description_fa should explain practical use in natural Persian. technical_summary_fa should be compact but comprehensive, suitable for the public Product Detail page."
    )
    result, model = service.client.structured_response(
        instructions=instructions,
        input_content=[{"type": "input_text", "text": json.dumps(facts, ensure_ascii=False, default=str)}],
        schema=TECHNICAL_SCHEMA,
        schema_name="source_grounded_product_intelligence_v493f",
        preferred_model=service.model,
    )
    features = []
    for item in result.get("technical_features") or []:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()[:120]
        value = str(item.get("value") or "").strip()[:500]
        if key and value:
            features.append({"key": key, "value": value})
    return {
        "technical_summary_fa": str(result.get("technical_summary_fa") or "").strip(),
        "use_description_fa": str(result.get("use_description_fa") or "").strip(),
        "technical_features": features,
        "operator_notes": [str(x or "").strip() for x in (result.get("operator_notes") or []) if str(x or "").strip()],
        "_ai_provider": service.provider,
        "_ai_model": model,
    }
