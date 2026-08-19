from __future__ import annotations

import logging

from .openai_content import AIContentService
from .phase49_3c_persian_content import (
    _generic_persian_pack,
    _language_invalid_fields,
    _repair_with_provider,
)


def install() -> None:
    if getattr(AIContentService, "_phase49_3c_persian_translate_guard_installed", False):
        return
    original = AIContentService.enrich_product
    logger = logging.getLogger("3dprinthub.phase49_3c.persian.translate")

    def enrich_product(self, source, local_categories, image_count=0, image_urls=None, mode="commerce"):
        result = original(
            self,
            source,
            local_categories,
            image_count=image_count,
            image_urls=image_urls,
            mode=mode,
        )
        if str(mode or "").lower() != "translate":
            return result
        missing = _language_invalid_fields(result, image_count)
        if missing:
            try:
                repaired, model = _repair_with_provider(self, source, result, missing, image_count)
                if isinstance(repaired, dict):
                    for key in missing:
                        root = key.split(".", 1)[0]
                        if repaired.get(root):
                            result[root] = repaired[root]
                    result["_ai_model"] = model
                    result["_phase49_3c_persian_translate_repair"] = True
            except Exception as exc:
                logger.exception("AI_PERSIAN_TRANSLATE_REPAIR_FAILED provider=%s model=%s", self.provider, self.model)
                result["_phase49_3c_persian_translate_repair_error"] = f"{type(exc).__name__}: {exc}"
        result = _generic_persian_pack(result, image_count)
        result["_phase49_3c_persian_translate_invalid_after_repair"] = _language_invalid_fields(result, image_count)
        return result

    AIContentService.enrich_product = enrich_product
    AIContentService._phase49_3c_persian_translate_guard_installed = True
