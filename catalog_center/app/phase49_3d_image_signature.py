from __future__ import annotations

import hashlib
import json

from . import phase49_3c_image_pipeline as image_pipeline


JSON_SEMANTIC_FIELDS = {
    "keywords_json",
    "tags_fa_json",
    "hashtags_fa_json",
    "image_alt_texts_json",
}
SIGNATURE_FIELDS = (
    "title_fa",
    "source_title",
    "short_description_fa",
    "seo_title_fa",
    "seo_description_fa",
    "keywords_json",
    "tags_fa_json",
    "hashtags_fa_json",
    "image_alt_texts_json",
    "author_name",
    "source_name",
    "source_url",
    "license_name",
    "license_url",
    "commercial_status",
)


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


def _semantic_json(value):
    if isinstance(value, (list, dict)):
        return value
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return parsed if isinstance(parsed, (list, dict)) else []


def semantic_image_seo_signature(row) -> str:
    """Hash image-SEO inputs by semantic value, not JSON serialization bytes.

    Phase49.3C previously hashed raw JSON strings. A finalize operation rewrites
    Persian arrays with ``ensure_ascii=False``; semantically identical values then
    produced a different hash and immediately marked freshly generated image
    metadata as stale. Normalizing JSON fields before hashing removes that false
    positive while still invalidating metadata after a real SEO/Alt change.
    """
    payload = {}
    for key in SIGNATURE_FIELDS:
        value = _row_value(row, key, "")
        payload[key] = _semantic_json(value) if key in JSON_SEMANTIC_FIELDS else value
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def install() -> None:
    if getattr(image_pipeline, "_phase49_3d_semantic_signature_installed", False):
        return
    image_pipeline.image_seo_signature = semantic_image_seo_signature
    image_pipeline._phase49_3d_semantic_signature_installed = True
