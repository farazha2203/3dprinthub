from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin, urlsplit

from PIL import Image

from .crawler import download_public_file
from . import phase49_3c_image_pipeline as image_pipeline


IMAGE_SUFFIXES = {".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif"}
FORMAT_SUFFIX = {"WEBP": ".webp", "JPEG": ".jpg", "PNG": ".png", "AVIF": ".avif", "GIF": ".gif"}


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []
def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _absolute(site_url: str, value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.startswith(("https://", "http://")):
        return raw
    if raw.startswith("/") and str(site_url or "").strip():
        return urljoin(site_url.rstrip("/") + "/", raw.lstrip("/"))
    return ""


def _url_key(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parts = urlsplit(raw)
    if parts.scheme and parts.netloc:
        return f"{parts.scheme.casefold()}://{parts.netloc.casefold()}{parts.path}"
    return raw.casefold()
def selected_source_urls(row: dict[str, Any]) -> list[str]:
    """Return the operator-selected image identity in exact stored order."""
    canonical = [
        str(value or "").strip()
        for value in _json_list(row.get("images_json"))
        if str(value or "").strip()
    ]
    canonical_set = set(canonical)
    selected = [
        str(value or "").strip()
        for value in _json_list(row.get("selected_images_json"))
        if str(value or "").strip()
    ]
    outside = [value for value in selected if value not in canonical_set]
    if outside:
        raise RuntimeError(
            "Selected image authority drift: "
            + ", ".join(outside[:5])
        )
    return list(dict.fromkeys(selected))


def selected_local_media(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Resolve selected Product images to exact files inside this Product local_dir.

    This is the shared Product UI / Social local-media authority. Historical
    refetch sibling folders and identity-wide compatibility fallbacks are not
    allowed here.
    """
    selected = selected_source_urls(row)
    if not selected:
        return []

    raw_root = str(row.get("local_dir") or "").strip()
    if not raw_root:
        raise RuntimeError("Selected Product media has no local_dir.")
    local_dir = Path(raw_root).resolve()
    if not local_dir.is_dir():
        raise RuntimeError("Selected Product local_dir does not exist.")

    metadata = {
        str(item.get("source_url") or "").strip(): dict(item)
        for item in _json_list(row.get("image_metadata_json"))
        if isinstance(item, dict)
        and str(item.get("source_url") or "").strip()
    }

    output: list[dict[str, Any]] = []
    for index, source_url in enumerate(selected, 1):
        local_value = str(
            image_pipeline.strict_local_image(row, source_url) or ""
        ).strip()
        if not local_value:
            raise RuntimeError(
                f"Selected image {index} has no exact Local file."
            )
        path = Path(local_value).resolve()
        try:
            path.relative_to(local_dir)
        except ValueError as exc:
            raise RuntimeError(
                f"Selected image {index} escaped Product local_dir."
            ) from exc
        if not path.is_file():
            raise RuntimeError(
                f"Selected image {index} Local file is missing."
            )

        meta = metadata.get(source_url) or {}
        expected_sha = str(meta.get("final_sha256") or "").strip().lower()
        actual_sha = _sha256(path)
        final_value = str(meta.get("final_local_file") or "").strip()
        if final_value:
            try:
                final_path = Path(final_value).resolve()
                final_path.relative_to(local_dir)
            except Exception as exc:
                raise RuntimeError(
                    f"Selected image {index} final_local_file is outside Product local_dir."
                ) from exc
            if final_path.is_file():
                path = final_path
                actual_sha = _sha256(path)
        if expected_sha and actual_sha != expected_sha:
            raise RuntimeError(
                f"Selected image {index} SHA drift: "
                f"expected={expected_sha} actual={actual_sha}"
            )
        seo_name = str(
            meta.get("seo_filename")
            or meta.get("product_local_filename")
            or path.name
        ).strip()
        output.append({
            "index": index,
            "source_url": source_url,
            "local_path": str(path),
            "filename": path.name,
            "seo_filename": seo_name,
            "sha256": actual_sha,
        })
    return output


def align_public_media_to_selected(
    row: dict[str, Any],
    public_urls: list[str],
) -> list[str]:
    """Map public Site media to the exact selected Local Product image order."""
    selected = selected_local_media(row)
    if not selected:
        raise RuntimeError(
            "No selected Product image is available for Social publishing."
        )
    candidates = [
        str(value or "").strip()
        for value in public_urls or []
        if str(value or "").strip().startswith("https://")
    ]
    aligned: list[str] = []
    used: set[str] = set()
    for item in selected:
        names = {
            str(item.get("seo_filename") or "").casefold(),
            str(item.get("filename") or "").casefold(),
        }
        sha_prefix = str(item.get("sha256") or "").lower()[:12]
        matches: list[str] = []
        for url in candidates:
            if url in used:
                continue
            parsed = urlsplit(url)
            parts = [part for part in parsed.path.split("/") if part]
            basename = Path(parsed.path).name.casefold()
            parent = parts[-2].lower() if len(parts) >= 2 else ""
            if basename in names or (sha_prefix and parent == sha_prefix):
                matches.append(url)
        if len(matches) != 1:
            raise RuntimeError(
                "Public/Social media parity failed for selected image "
                f"{item['index']}: matches={len(matches)}"
            )
        chosen = matches[0]
        aligned.append(chosen)
        used.add(chosen)
    return aligned


def normalized_site_media(server: dict[str, Any] | None, site_url: str) -> list[dict[str, Any]]:
    server = dict(server or {})
    rows: list[dict[str, Any]] = []
    for raw in server.get("images") or []:
        if not isinstance(raw, dict):
            continue
        url = _absolute(site_url, raw.get("url") or raw.get("remote_url"))
        if not url:
            continue
        rows.append({
            "url": url,
            "alt": str(raw.get("alt") or "").strip(),
            "is_primary": bool(raw.get("is_primary")),
            "is_selected": bool(raw.get("is_selected", True)),
        })
    main = _absolute(site_url, server.get("main_image"))
    if main:
        rows.insert(0, {"url": main, "alt": "", "is_primary": True, "is_selected": True})
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = _url_key(row["url"])
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(row)
    return output
def _metadata_names(row: dict[str, Any]) -> set[str]:
    output: set[str] = set()
    for item in _json_list(row.get("image_metadata_json")):
        if not isinstance(item, dict):
            continue
        for key in ("seo_filename", "final_local_file"):
            value = str(item.get(key) or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
            if value:
                output.add(value.casefold())
    return output


def _site_media_represented(row: dict[str, Any], site_item: dict[str, Any]) -> bool:
    url = str(site_item.get("url") or "").strip()
    if not url:
        return True
    canonical = {
        _url_key(str(value or ""))
        for value in _json_list(row.get("images_json"))
        if str(value or "").strip()
    }
    if _url_key(url) in canonical:
        return True
    for item in _json_list(row.get("image_metadata_json")):
        if not isinstance(item, dict):
            continue
        recovered_from = str(item.get("site_recovered_from") or "").strip()
        if recovered_from and _url_key(recovered_from) == _url_key(url):
            return True
    basename = Path(urlsplit(url).path).name.casefold()
    return bool(basename and basename in _metadata_names(row))


def _safe_site_name(url: str, digest: str, suffix: str) -> str:
    source_name = Path(urlsplit(url).path).stem
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", source_name).strip("-._") or "image"
    return f"site-{digest[:12]}-{safe[:72]}{suffix}"


def _same_sha_file(local_dir: Path, digest: str) -> Path | None:
    for root in (local_dir / "seo_images", local_dir / "images"):
        if not root.is_dir():
            continue
        for path in root.iterdir():
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            try:
                if _sha256(path) == digest:
                    return path.resolve()
            except OSError:
                continue
    return None


def recover_site_media_candidates(
    db,
    image_core,
    product_id: int,
    server: dict[str, Any] | None,
    site_url: str,
    *,
    progress: Callable[[int, str], None] | None = None,
) -> dict[str, Any]:
    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError("محصول پیدا نشد.")
    before = dict(row_obj)
    site_media = normalized_site_media(server, site_url)
    raw_root = str(before.get("local_dir") or "").strip()
    if raw_root:
        local_dir = Path(raw_root).resolve()
    else:
        source = str(before.get("source_code") or "manual").strip() or "manual"
        external = str(before.get("external_id") or product_id).strip() or str(product_id)
        local_dir = (Path(db.path).resolve().parent / "collected" / source / external).resolve()
    image_dir = local_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    canonical = [str(value or "").strip() for value in _json_list(before.get("images_json")) if str(value or "").strip()]
    metadata = [dict(item) for item in _json_list(before.get("image_metadata_json")) if isinstance(item, dict)]
    recovered: list[str] = []
    represented: list[str] = []
    failures: list[dict[str, str]] = []
    total = max(1, len(site_media))

    for index, site_item in enumerate(site_media, 1):
        url = str(site_item.get("url") or "").strip()
        current_row = dict(db.product(int(product_id)) or before)
        current_row["images_json"] = json.dumps(canonical, ensure_ascii=False)
        current_row["image_metadata_json"] = json.dumps(metadata, ensure_ascii=False)
        if _site_media_represented(current_row, site_item):
            represented.append(url)
            continue
        if callable(progress):
            progress(15 + int(index / total * 55), f"دریافت رسانه سایت {index}/{len(site_media)}")
        suffix = Path(urlsplit(url).path).suffix.lower()
        if suffix not in IMAGE_SUFFIXES:
            suffix = ".webp"
        temp = image_dir / f".site-recovery-{hashlib.sha1(url.encode('utf-8')).hexdigest()[:12]}{suffix}"
        try:
            download_public_file(url, temp, max_bytes=20_000_000, referer=url)
            with Image.open(temp) as image:
                image_format = str(image.format or "").upper()
                width, height = int(image.width), int(image.height)
                image.verify()
            if width <= 0 or height <= 0:
                raise RuntimeError("Downloaded Site image has invalid dimensions")
            actual_suffix = FORMAT_SUFFIX.get(image_format, suffix if suffix in IMAGE_SUFFIXES else ".webp")
            digest = _sha256(temp)
            same = _same_sha_file(local_dir, digest)
            if same is not None and same != temp.resolve():
                temp.unlink(missing_ok=True)
                if same.parent.name.casefold() == "images":
                    pseudo = f"local://{same.name}"
                    if pseudo not in canonical:
                        canonical.append(pseudo)
                        recovered.append(pseudo)
                represented.append(url)
                continue
            final = (image_dir / _safe_site_name(url, digest, actual_suffix)).resolve()
            if final.parent != image_dir.resolve():
                raise RuntimeError("Unsafe Site media recovery target")
            if temp.resolve() != final:
                if final.exists() and _sha256(final) == digest:
                    temp.unlink(missing_ok=True)
                else:
                    shutil.move(str(temp), str(final))
            pseudo = f"local://{final.name}"
            if pseudo not in canonical:
                canonical.append(pseudo)
            if not any(str(item.get("source_url") or "") == pseudo for item in metadata):
                metadata.append({
                    "source_url": pseudo,
                    "alt_text": str(site_item.get("alt") or ""),
                    "metadata_ready": False,
                    "site_recovered_from": url,
                })
            recovered.append(pseudo)
        except Exception as exc:
            temp.unlink(missing_ok=True)
            failures.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})

    if recovered:
        db.update_product(int(product_id), {
            "local_dir": str(local_dir),
            "images_json": json.dumps(list(dict.fromkeys(canonical)), ensure_ascii=False),
            "image_metadata_json": json.dumps(metadata, ensure_ascii=False),
        })
        try:
            db.save_history(
                int(product_id),
                "a2w_site_media_recovery",
                before,
                dict(db.product(int(product_id))),
                f"Recovered {len(recovered)} Site media candidate(s) without changing Site selection.",
            )
        except Exception:
            pass
    return {"recovered": recovered, "represented": represented, "failures": failures, "site_media": site_media}
def media_truth_snapshot(
    db,
    image_core,
    product_id: int,
    *,
    server: dict[str, Any] | None = None,
    site_url: str = "",
    site_error: str = "",
    recovery: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError("محصول پیدا نشد.")
    row = dict(row_obj)
    canonical = [str(value or "").strip() for value in _json_list(row.get("images_json")) if str(value or "").strip()]
    selected = [str(value or "").strip() for value in _json_list(row.get("selected_images_json")) if str(value or "").strip()]
    primary = str(row.get("primary_image_url") or "").strip()
    local_items = image_core.current_local_items(int(product_id))
    site_media = normalized_site_media(server, site_url)
    outside = [value for value in selected if value not in set(canonical)]
    missing_local = [value for value in selected if not str(image_core.local_path_for_url(row, value) or "").strip()]
    selected_media_error = ""
    selected_local = []
    try:
        selected_local = selected_local_media(row)
    except Exception as exc:
        selected_media_error = f"{type(exc).__name__}: {exc}"
    source_host = urlsplit(str(row.get("source_url") or "")).netloc.casefold()
    source_links = [
        value for value in canonical
        if value.startswith(("https://", "http://"))
        and (not source_host or urlsplit(value).netloc.casefold() == source_host)
    ]
    unrepresented = [item["url"] for item in site_media if not _site_media_represented(row, item)]
    mismatches: list[str] = []
    if outside:
        mismatches.append(f"{len(outside)} انتخاب سایت خارج از authority دیتابیس است")
    if missing_local:
        mismatches.append(f"{len(missing_local)} انتخاب سایت فایل Local ندارد")
    if selected_media_error:
        mismatches.append("Selected media truth نامعتبر است: " + selected_media_error)
    if selected and primary not in selected:
        mismatches.append("تصویر اصلی داخل انتخاب ارسال سایت نیست")
    if server is not None and len(site_media) != len(selected):
        mismatches.append(f"تعداد Site={len(site_media)} با ارسال سایت Local={len(selected)} متفاوت است")
    if unrepresented:
        mismatches.append(f"{len(unrepresented)} رسانه Site هنوز candidate محلی ندارد")
    if site_error:
        mismatches.append("خواندن Site ناموفق بود")

    recovery = dict(recovery or {})
    return {
        "truth_sync": True,
        "product_id": int(product_id),
        "server_product_id": int(row.get("server_product_id") or 0),
        "local_revision": int(row.get("server_product_revision") or 0),
        "canonical_count": len(canonical),
        "selected_count": len(selected),
        "local_file_count": len(local_items),
        "selected_local_count": len(selected_local),
        "selected_media_error": selected_media_error,
        "selected_local_files": [
            str(item.get("local_path") or "")
            for item in selected_local
        ],
        "source_link_count": len(source_links),
        "site_media_count": len(site_media),
        "site_main_image": _absolute(site_url, (server or {}).get("main_image")),
        "site_error": str(site_error or ""),
        "selected_outside_authority": outside,
        "selected_missing_local": missing_local,
        "site_unrepresented": unrepresented,
        "recovered": list(recovery.get("recovered") or []),
        "recovery_failures": list(recovery.get("failures") or []),
        "mismatches": mismatches,
        "selected_urls": selected,
        "canonical_urls": canonical,
    }
