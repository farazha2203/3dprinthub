from __future__ import annotations

import json
import shutil
from pathlib import Path


LOCAL_SCREENSHOT_URL = "local://source-page-screenshot.png"


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def install_extractor(page_extractor_module) -> None:
    """Keep the 49.3I.26 screenshot URL resolvable by ProductStudio.

    ProductStudio resolves ``local://name`` relative to ``product.local_dir``.
    The primary 49.3I.26 acquisition wrapper stores the captured PNG under the
    image folder, so copy the same local-only screenshot to the Product root as
    the stable gallery reference. No remote/network behavior is changed here.
    """
    if getattr(page_extractor_module, "_phase49_3i26_screenshot_root_patch", False):
        return
    original = page_extractor_module.extract_direct_link

    async def extract_direct_link(url, output_dir, profile_dir, **kwargs):
        result = await original(url, output_dir, profile_dir, **kwargs)
        screenshot = Path(str(result.get("source_page_screenshot") or ""))
        local_dir = Path(str(result.get("local_dir") or output_dir))
        if screenshot.is_file():
            target = local_dir / "source-page-screenshot.png"
            if screenshot.resolve() != target.resolve():
                shutil.copy2(screenshot, target)
            urls = _json_list(result.get("images_json"))
            if LOCAL_SCREENSHOT_URL not in urls:
                urls.append(LOCAL_SCREENSHOT_URL)
            result["images_json"] = json.dumps(urls, ensure_ascii=False)
            result["source_page_screenshot"] = str(target)
        return result

    page_extractor_module.extract_direct_link = extract_direct_link
    page_extractor_module._phase49_3i26_screenshot_root_patch = True
