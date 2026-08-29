from __future__ import annotations

import getpass
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path
from urllib import request as urllib_request
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from PIL import Image

MAX_SOURCE_IMAGES = 10
IMAGE_METADATA_COLUMN = "image_metadata_json"
TRACKING_QUERY_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "source",
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


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


def _json_object(value) -> dict:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def canonical_image_url(url: str) -> str:
    value = str(url or "").strip()
    if value.startswith("local://"):
        return value
    parsed = urlsplit(value)
    query = [
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS
    ]
    return urlunsplit((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        urlencode(query),
        "",
    ))


def cap_unique_urls(urls, limit: int = MAX_SOURCE_IMAGES) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for raw in urls or []:
        value = str(raw or "").strip()
        if not value:
            continue
        key = canonical_image_url(value)
        if key in seen:
            continue
        seen.add(key)
        output.append(value)
        if len(output) >= max(1, min(MAX_SOURCE_IMAGES, int(limit or MAX_SOURCE_IMAGES))):
            break
    return output


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _dhash(path: Path) -> int | None:
    try:
        with Image.open(path) as image:
            image = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
            pixels = list(image.getdata())
    except Exception:
        return None
    value = 0
    for y in range(8):
        for x in range(8):
            value <<= 1
            value |= 1 if pixels[y * 9 + x] > pixels[y * 9 + x + 1] else 0
    return value


def _hamming(left: int | None, right: int | None) -> int:
    if left is None or right is None:
        return 64
    return (left ^ right).bit_count()


def _visual_fingerprint(path: Path) -> tuple[int | None, int, int, float] | None:
    """Conservative visual fingerprint used only after URL/SHA exact checks."""
    try:
        with Image.open(path) as image:
            width, height = image.size
            gray = image.convert("L")
            mean_luma = float(gray.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0)))
            compact = gray.resize((9, 8), Image.Resampling.LANCZOS)
            pixels = list(compact.getdata())
    except Exception:
        return None
    value = 0
    for y in range(8):
        for x in range(8):
            value <<= 1
            value |= 1 if pixels[y * 9 + x] > pixels[y * 9 + x + 1] else 0
    return value, int(width), int(height), mean_luma


def _looks_like_same_image(
    current: tuple[int | None, int, int, float] | None,
    previous: tuple[int | None, int, int, float] | None,
) -> bool:
    if current is None or previous is None:
        return False
    current_hash, current_w, current_h, current_mean = current
    previous_hash, previous_w, previous_h, previous_mean = previous
    return (
        current_w == previous_w
        and current_h == previous_h
        and abs(current_mean - previous_mean) <= 4.0
        and _hamming(current_hash, previous_hash) <= 2
    )


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    if IMAGE_METADATA_COLUMN not in columns:
        db.conn.execute(
            f"ALTER TABLE products ADD COLUMN {IMAGE_METADATA_COLUMN} "
            "TEXT NOT NULL DEFAULT '[]'"
        )
        db.conn.commit()


def _manifest_items(local_dir: Path, filename: str) -> list[dict]:
    path = Path(local_dir) / filename
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    items = payload.get("items") if isinstance(payload, dict) else []
    return [item for item in items or [] if isinstance(item, dict)]


def strict_source_local_image(row, url: str) -> str:
    """Resolve the original/cache image exactly, never a prior SEO derivative."""
    local_dir = Path(str(_row_value(row, "local_dir", "") or ""))
    if not local_dir:
        return ""
    url = str(url or "").strip()
    if not url:
        return ""

    if url.startswith("local://"):
        candidate = local_dir / "images" / url.split("local://", 1)[1]
        return str(candidate) if candidate.is_file() else ""

    extract_path = local_dir / "page_extract.json"
    if extract_path.is_file():
        try:
            payload = json.loads(extract_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        for item in payload.get("images") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("url") or "") != url:
                continue
            path = Path(str(item.get("local_file") or ""))
            if not path.is_absolute():
                path = (local_dir / path).resolve()
            if path.is_file():
                return str(path)

    suffix = Path(urlsplit(url).path).suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        suffix = ".jpg"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    for prefix in ("batch_", "phase49_3c_"):
        candidate = local_dir / "images" / f"{prefix}{digest}{suffix}"
        if candidate.is_file():
            return str(candidate)
    return ""


def strict_local_image(row, url: str) -> str:
    """Resolve an exact final/source image; never guess by list index."""
    local_dir = Path(str(_row_value(row, "local_dir", "") or ""))
    url = str(url or "").strip()
    if not local_dir or not url:
        return ""

    for item in _manifest_items(local_dir, "image_seo_manifest.json"):
        if str(item.get("source_url") or "") == url:
            path = Path(str(item.get("final_local_file") or ""))
            if path.is_file():
                return str(path)

    return strict_source_local_image(row, url)


def strict_existing_image_mapping(local_dir: Path, all_urls: list[str]) -> dict[str, Path]:
    local_dir = Path(local_dir)
    row = {"local_dir": str(local_dir)}
    mapping: dict[str, Path] = {}
    for url in all_urls:
        path = strict_local_image(row, url)
        if path:
            mapping[url] = Path(path)
    return mapping


def _ascii_slug(value: str, fallback: str = "product") -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug[:72] or fallback


def planned_seo_filename(row, index: int) -> str:
    source_title = str(_row_value(row, "source_title", "") or "")
    title_fa = str(_row_value(row, "title_fa", "") or "")
    product_id = str(_row_value(row, "id", "") or "item")
    base = _ascii_slug(source_title or title_fa, fallback=f"product-{product_id}")
    if "3d" not in base:
        base = f"{base}-3d-print"
    return f"{base}-{index:02d}.webp"


def _operator_name(db) -> str:
    try:
        value = str(db.setting("operator_name", "") or "").strip()
    except Exception:
        value = ""
    return (
        value
        or os.getenv("CATALOG_OPERATOR_NAME", "").strip()
        or getpass.getuser()
        or "operator"
    )


def _copyright_holder(row) -> tuple[str, str]:
    status = str(_row_value(row, "commercial_status", "review") or "review")
    creator = (
        str(_row_value(row, "author_name", "") or "").strip()
        or str(_row_value(row, "source_name", "") or "").strip()
        or str(_row_value(row, "source_code", "") or "").strip()
        or "Unknown creator"
    )
    if status == "owned":
        return "3DPrintHub", "3DPrintHub"
    if status == "public_domain":
        return creator, "Public Domain"
    return creator, creator


def _safe_alt(row, index: int, alts: list[str]) -> str:
    if index - 1 < len(alts):
        candidate = str(alts[index - 1] or "").strip()
        if candidate:
            return candidate[:220]
    title = (
        str(_row_value(row, "title_fa", "") or "").strip()
        or str(_row_value(row, "source_title", "") or "").strip()
        or "محصول چاپ سه‌بعدی"
    )
    return f"{title} - نمای {index}"[:220]


def image_seo_signature(row) -> str:
    payload = {
        key: _row_value(row, key, "")
        for key in (
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
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_image_metadata(row, url: str, local_file: Path, index: int, db) -> dict:
    alts = [str(x or "").strip() for x in _json_list(_row_value(row, "image_alt_texts_json", "[]"))]
    keywords = []
    for field in ("keywords_json", "tags_fa_json", "hashtags_fa_json"):
        for item in _json_list(_row_value(row, field, "[]")):
            text = str(item or "").strip().lstrip("#")
            if text and text.casefold() not in {x.casefold() for x in keywords}:
                keywords.append(text)
    title = (
        str(_row_value(row, "seo_title_fa", "") or "").strip()
        or str(_row_value(row, "title_fa", "") or "").strip()
        or str(_row_value(row, "source_title", "") or "").strip()
        or f"Product {_row_value(row, 'id', '')}"
    )
    caption = (
        str(_row_value(row, "short_description_fa", "") or "").strip()
        or str(_row_value(row, "seo_description_fa", "") or "").strip()
    )
    creator, copyright_holder = _copyright_holder(row)
    source_url = str(_row_value(row, "source_url", "") or "").strip()
    license_name = str(_row_value(row, "license_name", "") or "").strip()
    license_url = str(_row_value(row, "license_url", "") or "").strip()
    return {
        "image_id": hashlib.sha256(f"{canonical_image_url(url)}|{_sha256(local_file)}".encode("utf-8")).hexdigest()[:24],
        "source_url": url,
        "source_page_url": source_url,
        "original_filename": local_file.name,
        "seo_filename": planned_seo_filename(row, index),
        "alt_text": _safe_alt(row, index, alts),
        "title": title[:220],
        "caption": caption[:500],
        "keywords": keywords[:16],
        "creator": creator[:220],
        "copyright_holder": copyright_holder[:220],
        "publisher": "3DPrintHub",
        "editor": "3DPrintHub Catalog Center",
        "operator": _operator_name(db),
        "license_name": license_name[:220],
        "license_url": license_url,
        "credit_line": f"Creator: {creator} | Source: {source_url} | Publisher/Editor: 3DPrintHub",
        "original_sha256": _sha256(local_file),
        "metadata_version": "49.3C",
        "seo_signature": image_seo_signature(row),
    }


def _write_webp_with_metadata(source: Path, target: Path, metadata: dict) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.load()
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        exif = Image.Exif()
        exif[270] = metadata.get("caption") or metadata.get("alt_text") or ""
        exif[305] = "3DPrintHub Catalog Center"
        exif[315] = metadata.get("creator") or ""
        exif[33432] = metadata.get("copyright_holder") or ""
        try:
            exif[40091] = (metadata.get("title") or "").encode("utf-16le") + b"\x00\x00"
            exif[40094] = ("; ".join(metadata.get("keywords") or [])).encode("utf-16le") + b"\x00\x00"
        except Exception:
            pass
        kwargs = {"format": "WEBP", "quality": 92, "method": 6}
        try:
            kwargs["exif"] = exif.tobytes()
            image.save(target, **kwargs)
        except Exception:
            kwargs.pop("exif", None)
            image.save(target, **kwargs)


def _download_if_needed(row, url: str, local_dir: Path) -> Path | None:
    resolved = strict_source_local_image(row, url)
    if resolved:
        return Path(resolved)
    if not url.startswith(("http://", "https://")):
        return None
    cache = local_dir / "images"
    cache.mkdir(parents=True, exist_ok=True)
    suffix = Path(urlsplit(url).path).suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        suffix = ".jpg"
    target = cache / f"phase49_3c_{hashlib.sha256(url.encode('utf-8')).hexdigest()[:20]}{suffix}"
    req = urllib_request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": str(_row_value(row, "source_url", "") or url),
        },
    )
    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            raw = response.read(30_000_000)
        if len(raw) < 512:
            return None
        target.write_bytes(raw)
        with Image.open(target) as image:
            image.verify()
        return target
    except Exception:
        try:
            target.unlink(missing_ok=True)
        except Exception:
            pass
        return None


DERIVED_IMAGE_STATE_FIELDS = {
    "selected_images_json",
    "primary_image_url",
    "image_alt_texts_json",
    IMAGE_METADATA_COLUMN,
}


def _persist_derived_image_state(db, product_id: int, values: dict) -> None:
    """Persist deterministic image-finalizer output even after operator lock.

    The Stage lock protects operator/AI edits. SEO file regeneration is derived
    state from already-approved image selection + current product metadata, so
    it must be able to refresh signatures after later Content/Source stages
    change. Only the explicit derived-image whitelist may bypass the lock guard.
    """
    payload = dict(values or {})
    unknown = set(payload) - DERIVED_IMAGE_STATE_FIELDS
    if unknown:
        raise RuntimeError(
            "Derived image refresh attempted non-image fields: "
            + ", ".join(sorted(unknown))
        )
    raw_update = getattr(db, "_phase49_3i36_raw_update_product", None)
    if callable(raw_update):
        raw_update(int(product_id), payload)
        return
    db.update_product(int(product_id), payload)


def finalize_selected_images(db, product_id: int) -> dict:
    ensure_schema(db)
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    selected = cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
    if not selected:
        raise RuntimeError("حداقل یک تصویر برای سایت انتخاب کن.")

    local_dir = Path(str(_row_value(row, "local_dir", "") or ""))
    if not local_dir:
        raise RuntimeError("پوشه محلی محصول مشخص نیست.")
    seo_dir = local_dir / "seo_images"

    kept_urls: list[str] = []
    items: list[dict] = []
    seen_sha: set[str] = set()
    seen_visual: list[tuple[int | None, int, int, float]] = []
    duplicate_count = 0
    unresolved: list[str] = []

    for source_url in selected:
        source = _download_if_needed(row, source_url, local_dir)
        if source is None or not source.is_file():
            unresolved.append(source_url)
            continue
        sha = _sha256(source)
        visual = _visual_fingerprint(source)
        if sha in seen_sha or any(_looks_like_same_image(visual, old) for old in seen_visual):
            duplicate_count += 1
            continue
        seen_sha.add(sha)
        if visual is not None:
            seen_visual.append(visual)
        index = len(items) + 1
        metadata = build_image_metadata(row, source_url, source, index, db)
        target = seo_dir / metadata["seo_filename"]
        _write_webp_with_metadata(source, target, metadata)
        metadata["final_local_file"] = str(target)
        metadata["final_sha256"] = _sha256(target)
        metadata["metadata_ready"] = True
        items.append(metadata)
        kept_urls.append(source_url)
        if len(items) >= MAX_SOURCE_IMAGES:
            break

    if unresolved:
        raise RuntimeError(
            "فایل محلی این تصاویر پیدا/دریافت نشد: " + ", ".join(unresolved[:3])
        )
    if not items:
        raise RuntimeError("هیچ تصویر یکتای معتبری برای نهایی‌سازی باقی نماند.")

    primary = str(_row_value(row, "primary_image_url", "") or "")
    if primary not in kept_urls:
        primary = kept_urls[0]
    if primary in kept_urls and kept_urls[0] != primary:
        kept_urls = [primary] + [url for url in kept_urls if url != primary]
        by_url = {item["source_url"]: item for item in items}
        items = [by_url[url] for url in kept_urls if url in by_url]
        regenerated: list[dict] = []
        for index, item in enumerate(items, start=1):
            old = Path(item["final_local_file"])
            source = Path(strict_source_local_image(row, item["source_url"]) or old)
            if not source.is_file():
                source = old
            item = dict(item)
            item["seo_filename"] = planned_seo_filename(row, index)
            target = seo_dir / item["seo_filename"]
            _write_webp_with_metadata(source, target, item)
            item["final_local_file"] = str(target)
            item["final_sha256"] = _sha256(target)
            regenerated.append(item)
        items = regenerated

    alts = [item["alt_text"] for item in items]
    manifest = {
        "schema": "phase49.3c-image-seo-v1",
        "product_id": int(product_id),
        "max_images": MAX_SOURCE_IMAGES,
        "items": items,
    }
    (local_dir / "image_seo_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _persist_derived_image_state(
        db,
        int(product_id),
        {
            "selected_images_json": json.dumps(kept_urls, ensure_ascii=False),
            "primary_image_url": primary,
            "image_alt_texts_json": json.dumps(alts, ensure_ascii=False),
            IMAGE_METADATA_COLUMN: json.dumps(items, ensure_ascii=False),
        },
    )
    try:
        from .phase49_diagnostics import audit_event
        audit_event(
            "images",
            "seo_finalize",
            product_id=int(product_id),
            message=f"kept={len(items)} duplicates={duplicate_count}",
            source_file="catalog_center/app/phase49_3c_image_pipeline.py",
            detail={"kept": len(items), "duplicates": duplicate_count},
        )
    except Exception:
        pass
    return {
        "kept": len(items),
        "duplicates": duplicate_count,
        "items": items,
        "primary": primary,
    }


def image_metadata_missing(row) -> list[str]:
    selected = cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
    items = _json_list(_row_value(row, IMAGE_METADATA_COLUMN, "[]"))
    by_url = {
        str(item.get("source_url") or ""): item
        for item in items
        if isinstance(item, dict)
    }
    current_signature = image_seo_signature(row)
    missing: list[str] = []
    for index, url in enumerate(selected, start=1):
        meta = by_url.get(url) or {}
        if not str(meta.get("seo_filename") or "").strip():
            missing.append(f"نام SEO تصویر {index}")
        if not str(meta.get("alt_text") or "").strip():
            missing.append(f"Alt تصویر {index}")
        if not str(meta.get("creator") or "").strip():
            missing.append(f"Creator تصویر {index}")
        if not str(meta.get("source_page_url") or "").strip():
            missing.append(f"منبع تصویر {index}")
        if not bool(meta.get("metadata_ready")):
            missing.append(f"Metadata تصویر {index}")
        elif str(meta.get("seo_signature") or "") != current_signature:
            missing.append(f"بروزرسانی Metadata تصویر {index}")
    return missing


def _filter_manifest_after_extract(data: dict) -> dict:
    local_dir = Path(str(data.get("local_dir") or ""))
    urls = cap_unique_urls(_json_list(data.get("images_json")))
    selected = [
        url for url in cap_unique_urls(_json_list(data.get("selected_images_json")))
        if url in urls
    ]
    if not selected:
        selected = list(urls)

    manifest_path = local_dir / "page_extract.json"
    payload = {}
    if manifest_path.is_file():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    image_rows = [
        item for item in payload.get("images") or []
        if isinstance(item, dict) and str(item.get("url") or "") in urls
    ]

    exact_seen: set[str] = set()
    visual_seen: list[tuple[int | None, int, int, float]] = []
    duplicate_urls: set[str] = set()
    downloaded_files: list[str] = []
    for item in image_rows:
        local = Path(str(item.get("local_file") or ""))
        if not local.is_file():
            continue
        sha = _sha256(local)
        visual = _visual_fingerprint(local)
        if sha in exact_seen or any(_looks_like_same_image(visual, old) for old in visual_seen):
            duplicate_urls.add(str(item.get("url") or ""))
            continue
        exact_seen.add(sha)
        if visual is not None:
            visual_seen.append(visual)
        downloaded_files.append(str(local))

    if duplicate_urls:
        urls = [url for url in urls if url not in duplicate_urls]
        selected = [url for url in selected if url not in duplicate_urls]
        image_rows = [
            item for item in image_rows
            if str(item.get("url") or "") not in duplicate_urls
        ]
    urls = urls[:MAX_SOURCE_IMAGES]
    selected = [url for url in selected if url in urls][:MAX_SOURCE_IMAGES]
    if not selected:
        selected = list(urls)

    data["images_json"] = json.dumps(urls, ensure_ascii=False)
    data["selected_images_json"] = json.dumps(selected, ensure_ascii=False)
    data["primary_image_url"] = selected[0] if selected else (urls[0] if urls else "")
    data["downloaded_image_files"] = downloaded_files[:MAX_SOURCE_IMAGES]
    if payload:
        payload["images"] = [
            item for item in image_rows
            if str(item.get("url") or "") in urls
        ][:MAX_SOURCE_IMAGES]
        manifest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return data


def install_extractor_patch(page_extractor_module):
    if getattr(page_extractor_module, "_phase49_3c_image_cap_installed", False):
        return page_extractor_module.extract_direct_link
    original = page_extractor_module.extract_direct_link

    async def extract_direct_link(
        url,
        output_dir,
        profile_dir,
        *,
        headed=True,
        download_images=True,
        image_limit=MAX_SOURCE_IMAGES,
    ):
        data = await original(
            url,
            output_dir,
            profile_dir,
            headed=headed,
            download_images=download_images,
            image_limit=min(MAX_SOURCE_IMAGES, max(1, int(image_limit or MAX_SOURCE_IMAGES))),
        )
        return _filter_manifest_after_extract(data)

    page_extractor_module.extract_direct_link = extract_direct_link
    page_extractor_module._phase49_3c_image_cap_installed = True
    return extract_direct_link


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3c_image_pipeline_installed", False):
        return
    original_init = workspace_class.__init__
    original_refresh_gallery = workspace_class.refresh_gallery

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)

    def _resolve_local(self, row, url: str, index: int) -> str:
        return strict_local_image(row, url)

    def refresh_gallery(self):
        original_refresh_gallery(self)
        row = self.db.product(self.product_id)
        if row is None:
            return
        items = _json_list(_row_value(row, IMAGE_METADATA_COLUMN, "[]"))
        by_url = {
            str(item.get("source_url") or ""): item
            for item in items
            if isinstance(item, dict)
        }
        for index, meta in enumerate(getattr(self, "_gallery_cards", []) or [], start=1):
            url = str(meta.get("url") or "")
            exact = strict_local_image(row, url)
            if exact:
                meta["local"] = exact
            info = by_url.get(url) or {}
            original_name = Path(exact).name if exact else Path(urlsplit(url).path).name or "—"
            seo_name = str(info.get("seo_filename") or planned_seo_filename(row, index))
            card = getattr(meta.get("label"), "master", None)
            if card is not None:
                label = getattr(meta.get("label"), "_phase49_3c_names_label", None)
                if label is None:
                    import tkinter.ttk as ttk
                    label = ttk.Label(
                        card,
                        text="",
                        style="SubHeader.TLabel",
                        justify="left",
                        wraplength=215,
                    )
                    label.pack(fill="x", pady=(2, 3))
                    meta["label"]._phase49_3c_names_label = label
                label.configure(text=f"فایل فعلی: {original_name}\nنام SEO: {seo_name}")

    def phase49_3c_finalize_images(self):
        from tkinter import messagebox
        if not messagebox.askyesno(
            "3DPrintHub",
            "تصاویر انتخاب‌شده نهایی‌سازی SEO شوند؟\n\n"
            "حداکثر ۱۰ تصویر یکتا نگه داشته می‌شود؛ Cache و فایل‌های منبع حذف نمی‌شوند. "
            "نسخه WebP جدید با نام SEO و Metadata صحیح ساخته می‌شود.",
            parent=self,
        ):
            return
        try:
            self.save(silent=True)
        except Exception:
            pass
        try:
            result = finalize_selected_images(self.db, self.product_id)
        except Exception as exc:
            messagebox.showerror("3DPrintHub", f"نهایی‌سازی تصاویر ناموفق بود:\n{exc}", parent=self)
            return
        self.reload()
        try:
            self._phase49_3c_schedule_live()
        except Exception:
            pass
        self.footer_status.set(
            f"SEO تصاویر کامل شد: {result['kept']} تصویر • تکراری حذف‌شده از انتخاب: {result['duplicates']}"
        )

    workspace_class.__init__ = __init__
    workspace_class._resolve_local = _resolve_local
    workspace_class.refresh_gallery = refresh_gallery
    workspace_class.phase49_3c_finalize_images = phase49_3c_finalize_images
    workspace_class._phase49_3c_image_pipeline_installed = True


def install_base_app(app_module) -> None:
    """Patch legacy preview/batch globals without changing persistent data."""
    if getattr(app_module, "_phase49_3c_image_base_installed", False):
        return
    from . import batch_packaging, page_extractor

    wrapped_extract = install_extractor_patch(page_extractor)
    app_module.extract_direct_link = wrapped_extract

    batch_packaging.existing_image_mapping = strict_existing_image_mapping

    original_copy = batch_packaging.copy_images_into_model

    def copy_images_into_model(selected_pairs, model_dir):
        image_target = Path(model_dir) / "images"
        image_target.mkdir(parents=True, exist_ok=True)
        used: set[str] = set()
        names: list[str] = []
        for index, (_url, local_file) in enumerate(selected_pairs, start=1):
            local_file = Path(local_file)
            suffix = local_file.suffix.lower() if local_file.suffix.lower() in IMAGE_SUFFIXES else ".webp"
            stem = re.sub(r"[^a-zA-Z0-9-]+", "-", local_file.stem).strip("-").lower()
            if not stem or stem.startswith(("001", "002", "003", "batch-")):
                stem = f"product-image-{index:02d}"
            name = f"{stem}{suffix}"
            counter = 1
            while name.casefold() in used:
                counter += 1
                name = f"{stem}-{counter}{suffix}"
            used.add(name.casefold())
            target = image_target / name
            import shutil
            shutil.copy2(local_file, target)
            if not target.is_file() or target.stat().st_size < 256:
                raise batch_packaging.BatchImagePackagingError(
                    f"IMAGE_NOT_PACKAGED: copied batch image is invalid: {target}"
                )
            names.append(name)
        return names

    batch_packaging.copy_images_into_model = copy_images_into_model
    app_module.copy_images_into_model = copy_images_into_model

    original_prepare = app_module.App.prepare_product_gallery

    def prepare_product_gallery(self, row):
        original_prepare(self, row)
        changed = False
        for item in getattr(self, "_preview_items", []) or []:
            url = str(item.get("url") or "")
            if not url:
                continue
            exact = strict_local_image(row, url)
            if item.get("local") != exact:
                item["local"] = exact
                changed = True
        if changed:
            self._preview_local = [
                Path(item["local"])
                for item in self._preview_items
                if item.get("local")
            ]
            self.render_inline_gallery()
            self.show_preview_image()

    app_module.App.prepare_product_gallery = prepare_product_gallery

    original_init = app_module.App.__init__

    def app_init(self, *args, **kwargs):
        result = original_init(self, *args, **kwargs)
        try:
            ensure_schema(self.db)
            if hasattr(self, "direct_image_limit"):
                self.direct_image_limit.set(str(MAX_SOURCE_IMAGES))
        except Exception:
            pass
        return result

    app_module.App.__init__ = app_init
    app_module._phase49_3c_image_base_installed = True
