from __future__ import annotations

import json
from typing import Any

DEFAULT_IMAGE_LIMIT = 5
HARD_MAX_IMAGE_LIMIT = 20


def normalize_image_limit(value: Any, default: int = DEFAULT_IMAGE_LIMIT) -> int:
    """Canonical operator image limit for every Phase49.3H intake/refetch path."""
    try:
        number = int(float(value))
    except Exception:
        number = int(default)
    return max(1, min(HARD_MAX_IMAGE_LIMIT, number))


def cap_sequence(values, limit: Any = DEFAULT_IMAGE_LIMIT) -> list:
    cap = normalize_image_limit(limit)
    return list(values or [])[:cap]


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def cap_extracted_page_images(page, limit: Any) -> None:
    """Keep only the product-image candidates allowed for this extraction.

    This is applied to a *new/refetched extraction result*. It never deletes
    historical files or old DB rows merely because the global cap changed.
    """
    cap = normalize_image_limit(limit)
    images = list(getattr(page, "images", []) or [])
    selected = [item for item in images if bool(getattr(item, "selected", True))]
    fallback = [item for item in images if item not in selected]
    kept = (selected + fallback)[:cap]
    try:
        page.images[:] = kept
    except Exception:
        page.images = kept


def cap_direct_result(result: dict, limit: Any) -> dict:
    """Cap the persisted product image contract, not only downloaded files."""
    output = dict(result or {})
    cap = normalize_image_limit(limit)
    all_urls = cap_sequence(_json_list(output.get("images_json")), cap)
    selected_urls = [url for url in _json_list(output.get("selected_images_json")) if url in set(all_urls)]
    selected_urls = cap_sequence(selected_urls, cap)
    downloaded = cap_sequence(output.get("downloaded_image_files") or [], cap)
    output["images_json"] = json.dumps(all_urls, ensure_ascii=False)
    output["selected_images_json"] = json.dumps(selected_urls, ensure_ascii=False)
    output["downloaded_image_files"] = downloaded
    primary = str(output.get("primary_image_url") or "").strip()
    if primary not in all_urls:
        output["primary_image_url"] = selected_urls[0] if selected_urls else (all_urls[0] if all_urls else "")
    try:
        snapshot = json.loads(output.get("source_snapshot_json") or "{}")
    except Exception:
        snapshot = {}
    if isinstance(snapshot, dict) and isinstance(snapshot.get("images"), list):
        snapshot["images"] = snapshot["images"][:cap]
        output["source_snapshot_json"] = json.dumps(snapshot, ensure_ascii=False)
    return output


def install_extractor(page_extractor_module, image_pipeline_module) -> None:
    if getattr(page_extractor_module, "_phase49_3h_image_limits_installed", False):
        return

    # The old Phase49.3C contract capped selected-image helpers at 10. 49.3H is
    # an explicitly approved contract change: operator may choose up to 20.
    original_cap_unique = image_pipeline_module.cap_unique_urls
    image_pipeline_module.MAX_SOURCE_IMAGES = HARD_MAX_IMAGE_LIMIT

    def cap_unique_urls(urls, limit=HARD_MAX_IMAGE_LIMIT):
        return original_cap_unique(urls, normalize_image_limit(limit, HARD_MAX_IMAGE_LIMIT))

    image_pipeline_module.cap_unique_urls = cap_unique_urls

    original_extract = page_extractor_module.RichPageExtractor.extract
    original_download = page_extractor_module.RichPageExtractor._download_images
    original_direct = page_extractor_module.extract_direct_link

    async def extract(self, url, output_dir, *, download_images=True, image_limit=DEFAULT_IMAGE_LIMIT):
        limit = normalize_image_limit(image_limit)
        page = await original_extract(
            self,
            url,
            output_dir,
            download_images=download_images,
            image_limit=limit,
        )
        cap_extracted_page_images(page, limit)
        # Rewrite the extractor snapshot after capping so a new extraction never
        # persists 60/100 discovered product images behind the UI limit.
        try:
            path = output_dir / "page_extract.json"
            path.write_text(json.dumps(page.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        return page

    async def _download_images(self, context, extracted, output_dir, *, image_limit=DEFAULT_IMAGE_LIMIT):
        return await original_download(
            self,
            context,
            extracted,
            output_dir,
            image_limit=normalize_image_limit(image_limit),
        )

    async def extract_direct_link(
        url,
        output_dir,
        profile_dir,
        *,
        headed=True,
        download_images=True,
        image_limit=DEFAULT_IMAGE_LIMIT,
    ):
        limit = normalize_image_limit(image_limit)
        result = await original_direct(
            url,
            output_dir,
            profile_dir,
            headed=headed,
            download_images=download_images,
            image_limit=limit,
        )
        return cap_direct_result(result, limit)

    page_extractor_module.RichPageExtractor.extract = extract
    page_extractor_module.RichPageExtractor._download_images = _download_images
    page_extractor_module.extract_direct_link = extract_direct_link
    page_extractor_module._phase49_3h_image_limits_installed = True


def _walk(root):
    try:
        children = root.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield child
        yield from _walk(child)


def _limit_spinbox(root, variable) -> None:
    expected = str(variable)
    for widget in _walk(root):
        try:
            if widget.winfo_class() not in {"TSpinbox", "Spinbox"}:
                continue
            if str(widget.cget("textvariable")) != expected:
                continue
            widget.configure(from_=1, to=HARD_MAX_IMAGE_LIMIT)
        except Exception:
            continue


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3h_image_limit_ui_installed", False):
        return
    original_scan_ui = app_class._scan_ui

    def _scan_ui(self):
        result = original_scan_ui(self)
        if hasattr(self, "direct_image_limit"):
            self.direct_image_limit.set(normalize_image_limit(self.direct_image_limit.get()))
            _limit_spinbox(getattr(self, "scan_tab", self), self.direct_image_limit)
        return result

    app_class._scan_ui = _scan_ui
    app_class._phase49_3h_image_limit_ui_installed = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3h_image_limit_workspace_installed", False):
        return
    original_images_ui = workspace_class._images_ui
    original_refetch = workspace_class.refetch
    original_reload = workspace_class.reload

    def _images_ui(self):
        result = original_images_ui(self)
        if hasattr(self, "product_image_limit_var"):
            self.product_image_limit_var.set(normalize_image_limit(self.product_image_limit_var.get()))
            _limit_spinbox(getattr(self, "images_tab", self), self.product_image_limit_var)
        return result

    def refetch(self):
        if hasattr(self, "product_image_limit_var"):
            self.product_image_limit_var.set(normalize_image_limit(self.product_image_limit_var.get()))
        return original_refetch(self)

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "product_image_limit_var"):
            self.product_image_limit_var.set(normalize_image_limit(self.product_image_limit_var.get()))
            _limit_spinbox(getattr(self, "images_tab", self), self.product_image_limit_var)
        return result

    workspace_class._images_ui = _images_ui
    workspace_class.refetch = refetch
    workspace_class.reload = reload
    workspace_class._phase49_3h_image_limit_workspace_installed = True
