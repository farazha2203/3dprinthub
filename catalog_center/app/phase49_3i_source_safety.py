from __future__ import annotations

from .phase49_3i_discovery_review import sanitize_source_payload, sanitize_source_text


def _sanitize_page(page) -> None:
    for name, limit in (
        ("source_title", 500),
        ("source_description", None),
        ("author_name", 500),
        ("license_name", 500),
        ("source_category", 500),
    ):
        if hasattr(page, name):
            setattr(page, name, sanitize_source_text(getattr(page, name, ""), limit))
    if hasattr(page, "source_categories"):
        page.source_categories = [sanitize_source_text(item, 500) for item in list(page.source_categories or [])]
        page.source_categories = [item for item in page.source_categories if item]
    if hasattr(page, "tags"):
        page.tags = [sanitize_source_text(item, 300) for item in list(page.tags or [])]
        page.tags = [item for item in page.tags if item]
    if hasattr(page, "specs") and isinstance(page.specs, dict):
        cleaned = {}
        for key, value in page.specs.items():
            safe_key = sanitize_source_text(key, 300) or "field"
            safe_value = value if not isinstance(value, str) else sanitize_source_text(value, 1000)
            if safe_key and safe_value not in ("", None):
                cleaned[safe_key] = safe_value
        page.specs = cleaned


def install(page_extractor_module, crawler_module) -> None:
    if getattr(page_extractor_module, "_phase49_3i_source_safety_installed", False):
        return

    original_extract = page_extractor_module.RichPageExtractor.extract
    original_direct = page_extractor_module.extract_direct_link
    original_parse = crawler_module.parse_product

    async def extract(self, *args, **kwargs):
        page = await original_extract(self, *args, **kwargs)
        _sanitize_page(page)
        return page

    async def extract_direct_link(*args, **kwargs):
        result = await original_direct(*args, **kwargs)
        return sanitize_source_payload(result)

    def parse_product(*args, **kwargs):
        result = original_parse(*args, **kwargs)
        return sanitize_source_payload(result)

    page_extractor_module.RichPageExtractor.extract = extract
    page_extractor_module.extract_direct_link = extract_direct_link
    crawler_module.parse_product = parse_product
    page_extractor_module._phase49_3i_source_safety_installed = True
