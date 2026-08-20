from __future__ import annotations

import json
from typing import Any

IMAGE_TEXT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "slot": {"type": "integer", "minimum": 1},
                    "alt_text": {"type": "string"},
                    "title": {"type": "string"},
                    "caption": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
                },
                "required": ["slot", "alt_text", "title", "caption", "keywords"],
            },
        }
    },
    "required": ["items"],
}

AI_OVERRIDE_FIELDS = ("alt_text", "title", "caption", "keywords")


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        value = row.get(key, default)
    else:
        try:
            value = row[key]
        except Exception:
            value = default
    return default if value is None else value


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def selected_image_text_payload(row, selected_urls: list[str]) -> dict[str, Any]:
    """Build a text-only payload. Image URL/binary/file content is intentionally absent."""
    existing_alts = [str(x or "").strip() for x in _json_list(_row_value(row, "image_alt_texts_json", "[]"))]
    return {
        "product": {
            "title_fa": str(_row_value(row, "title_fa", "") or ""),
            "source_title": str(_row_value(row, "source_title", "") or ""),
            "short_description_fa": str(_row_value(row, "short_description_fa", "") or ""),
            "description_fa": str(_row_value(row, "description_fa", "") or ""),
            "seo_title_fa": str(_row_value(row, "seo_title_fa", "") or ""),
            "seo_description_fa": str(_row_value(row, "seo_description_fa", "") or ""),
            "keywords": _json_list(_row_value(row, "keywords_json", "[]")),
            "tags": _json_list(_row_value(row, "tags_fa_json", "[]")),
            "hashtags": _json_list(_row_value(row, "hashtags_fa_json", "[]")),
            "source_specs": _row_value(row, "source_specs_json", "{}"),
        },
        "selected_image_slots": [
            {
                "slot": index,
                "existing_alt": existing_alts[index - 1] if index - 1 < len(existing_alts) else "",
            }
            for index, _url in enumerate(selected_urls, 1)
        ],
        "selected_count": len(selected_urls),
        "privacy_contract": "No image bytes, image URLs or image files are sent to the model.",
    }


def generate_selected_image_text(service, row, selected_urls: list[str]) -> dict:
    if not selected_urls:
        return {"items": [], "_ai_provider": service.provider, "_ai_model": service.model}
    payload = selected_image_text_payload(row, selected_urls)
    instructions = (
        "You are the Persian image metadata editor for 3DPrintHub. "
        "You DO NOT see the images. You receive only verified product text and numbered selected-image slots. "
        "Write concise factual Persian alt/title/caption/keywords for ONLY those selected slots. "
        "Never claim a visible detail that is not supported by the supplied product facts. "
        "Never invent creator, copyright, license, dimensions, material, color or source. "
        "Do not create fields for unselected images. Return exactly one JSON object matching the schema."
    )
    result, model = service.client.structured_response(
        instructions=instructions,
        input_content=[{"type": "input_text", "text": json.dumps(payload, ensure_ascii=False, default=str)}],
        schema=IMAGE_TEXT_SCHEMA,
        schema_name="selected_image_metadata_text_v493f",
        preferred_model=service.model,
    )
    allowed_slots = set(range(1, len(selected_urls) + 1))
    clean_items = []
    seen = set()
    for item in result.get("items") or []:
        if not isinstance(item, dict):
            continue
        try:
            slot = int(item.get("slot") or 0)
        except Exception:
            continue
        if slot not in allowed_slots or slot in seen:
            continue
        seen.add(slot)
        clean_items.append({
            "slot": slot,
            "alt_text": str(item.get("alt_text") or "").strip()[:220],
            "title": str(item.get("title") or "").strip()[:220],
            "caption": str(item.get("caption") or "").strip()[:500],
            "keywords": [str(x or "").strip().lstrip("#")[:80] for x in (item.get("keywords") or []) if str(x or "").strip()][:10],
        })
    clean_items.sort(key=lambda x: x["slot"])
    return {"items": clean_items, "_ai_provider": service.provider, "_ai_model": model}


def merge_selected_metadata(existing_items: list, selected_urls: list[str], ai_pack: dict) -> list[dict]:
    """Update only selected URL records; preserve every unselected metadata row byte-for-byte semantically."""
    output = [dict(item) for item in existing_items if isinstance(item, dict)]
    by_url = {str(item.get("source_url") or ""): item for item in output if item.get("source_url")}
    result_by_slot = {
        int(item.get("slot") or 0): item
        for item in (ai_pack.get("items") or [])
        if isinstance(item, dict) and int(item.get("slot") or 0) > 0
    }
    for slot, url in enumerate(selected_urls, 1):
        url = str(url or "").strip()
        if not url:
            continue
        target = by_url.get(url)
        if target is None:
            target = {"source_url": url}
            output.append(target)
            by_url[url] = target
        generated = result_by_slot.get(slot) or {}
        fields = []
        for field in AI_OVERRIDE_FIELDS:
            value = generated.get(field)
            if field == "keywords":
                value = [str(x or "").strip() for x in (value or []) if str(x or "").strip()]
            if value not in (None, "", []):
                target[field] = value
                fields.append(field)
        if fields:
            target["_ai_override_fields"] = sorted(set(target.get("_ai_override_fields") or []) | set(fields))
    return output


def install_image_pipeline_override(image_pipeline) -> None:
    if getattr(image_pipeline, "_phase49_3f_selected_ai_override_installed", False):
        return
    original = image_pipeline.build_image_metadata

    def build_image_metadata(row, url, local_file, index, db):
        base = original(row, url, local_file, index, db)
        existing = next(
            (
                item for item in _json_list(_row_value(row, image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
                if isinstance(item, dict) and str(item.get("source_url") or "") == str(url or "")
            ),
            {},
        )
        allowed = set(existing.get("_ai_override_fields") or [])
        for field in AI_OVERRIDE_FIELDS:
            if field in allowed and existing.get(field) not in (None, "", []):
                base[field] = existing[field]
        if allowed:
            base["_ai_override_fields"] = sorted(allowed)
        return base

    image_pipeline.build_image_metadata = build_image_metadata
    image_pipeline._phase49_3f_selected_ai_override_installed = True
