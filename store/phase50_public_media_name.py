from __future__ import annotations

import re
from pathlib import Path

from django.utils.text import slugify


_SAFE_BASENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def canonical_server_media_filename(
    data: dict,
    index: int,
    raw_name: str,
    *,
    default_suffix: str = ".webp",
) -> str:
    """Return a deterministic ASCII-safe basename for Server/Public media.

    Windows may keep an operator-approved Unicode SEO filename. The shared Host
    storage/public boundary uses ASCII-safe basenames so FTP/filesystem/HTTP
    layers never need to encode a raw Unicode filename. Editorial metadata,
    ALT/caption, source identity and media bytes remain unchanged.
    """

    original = Path(str(raw_name or "").replace("\\", "/")).name
    if original and original.isascii() and _SAFE_BASENAME_RE.fullmatch(original):
        return original

    suffix = Path(original).suffix.lower()
    if not suffix or not suffix.isascii() or not re.fullmatch(r"\.[a-z0-9]{2,8}", suffix):
        suffix = str(default_suffix or ".webp").lower()
        if not re.fullmatch(r"\.[a-z0-9]{2,8}", suffix):
            suffix = ".webp"

    source_title = str(
        data.get("source_title")
        or data.get("title_en")
        or data.get("source_name")
        or ""
    ).strip()
    base = slugify(source_title, allow_unicode=False).strip("-")
    if not base:
        identity = str(
            data.get("external_id")
            or data.get("desktop_product_id")
            or data.get("source_code")
            or "catalog"
        ).strip()
        token = slugify(identity, allow_unicode=False).strip("-") or "catalog"
        base = f"product-{token}"

    base = re.sub(r"[^a-z0-9-]+", "-", base.lower()).strip("-")
    base = re.sub(r"-{2,}", "-", base)[:58].rstrip("-") or "product"
    slot = max(1, int(index) + 1)
    return f"{base}-3d-print-{slot:02d}{suffix}"
