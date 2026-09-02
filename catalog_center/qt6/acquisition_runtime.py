from __future__ import annotations

import asyncio
import hashlib
import io
import json
import re
from pathlib import Path
from typing import Any, Callable
from urllib import request as urlrequest
from urllib.parse import urlsplit

from PIL import Image, ImageOps

from app.classic_methods import (
    collect_attached_chrome,
    collect_classic_exact,
    discover_classic,
    import_saved_html,
)
from app.crawler import (
    BlockedError,
    BrowserSession,
    download_public_file,
    parse_product,
    public_http,
)
from app.db import normalize_url, utc_now
from app.page_extractor import extract_direct_link
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.phase49_3h_image_limits import normalize_image_limit
from app.phase49_3i16_resilient_acquisition import collect_candidate_images_resilient
from app.phase49_3i38_crawl_ledger_stage_ai import (
    next_scroll_rounds,
    record_listing_progress,
    remember_ledger,
    terminal_identity_state,
)
from app.phase49_3i43_modern_acquisition_intelligence import (
    AccessDeniedError,
    ModernHttpClient,
    RateLimitedError,
    RobotsDeniedError,
    TransientHttpError,
    discover_conditional_http,
    ensure_schema as ensure_modern_schema,
    robots_policy,
)
from app.phase49_3i45_incremental_discovery_intelligence import (
    discover_sitemap_candidates_incremental,
    ensure_schema as ensure_incremental_schema,
)
from app.phase49_3i_discovery_review import (
    _source_defaults,
    candidate_by_identity,
    candidate_preview_cache_path,
    ensure_schema as ensure_candidate_schema,
    set_candidate_status,
    upsert_candidate,
)
from app.phase49_3i_preview_recovery import discover_preview_candidates_safe
from app.runtime_paths import data_root
from app.v8_features import (
    diff_summary,
    merge_refetch,
    product_diff,
    product_fingerprint,
    source_payload_hash,
)
from app.workflow import should_mark_needs_update

from .acquisition_trace import event as acquisition_event


Progress = Callable[[int, str], None] | None
ShouldStop = Callable[[], bool] | None

ADAPTIVE_COLLECTION_METHODS = (
    "rich",
    "network_capture",
    "classic_exact",
    "public_http",
    "chrome_attached",
)


class AcquisitionQualityError(RuntimeError):
    def __init__(self, message: str, metrics: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.metrics = dict(metrics or {})


class AcquisitionMethodsExhausted(RuntimeError):
    def __init__(self, attempts: list[dict[str, str]]) -> None:
        self.attempts = list(attempts)
        summary = " | ".join(
            f"{row.get('method')}: {row.get('error')}"
            for row in self.attempts
        )
        super().__init__("All distinct Product acquisition methods failed | " + summary)


def _emit(progress: Progress, value: int, message: str) -> None:
    if callable(progress):
        progress(max(0, min(100, int(value))), str(message))


def _stopped(should_stop: ShouldStop) -> bool:
    return bool(callable(should_stop) and should_stop())


def _json_count(value: Any, expected: type) -> int:
    if isinstance(value, expected):
        return len(value)
    try:
        parsed = json.loads(value or ("{}" if expected is dict else "[]"))
    except Exception:
        return 0
    return len(parsed) if isinstance(parsed, expected) else 0


def _json_urls(value: Any) -> list[str]:
    if isinstance(value, list):
        raw = value
    else:
        try:
            raw = json.loads(value or "[]")
        except Exception:
            raw = []
    output: list[str] = []
    for item in raw if isinstance(raw, list) else []:
        if isinstance(item, dict):
            candidate = str(item.get("url") or item.get("source_url") or "").strip()
        else:
            candidate = str(item or "").strip()
        if candidate and candidate not in output:
            output.append(candidate)
    return output


def _local_image_files(local_dir: Path) -> list[str]:
    allowed = {".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif", ".bmp", ".tif", ".tiff"}
    output: list[str] = []
    seen: set[str] = set()
    for root in (Path(local_dir) / "seo_images", Path(local_dir) / "images"):
        if not root.is_dir():
            continue
        try:
            children = sorted(root.iterdir(), key=lambda item: item.name.casefold())
        except OSError:
            continue
        for child in children:
            if not child.is_file() or child.suffix.lower() not in allowed:
                continue
            try:
                value = str(child.resolve())
            except OSError:
                continue
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            output.append(value)
    return output


def _meaningful_source_title(value: Any, external_id: str) -> bool:
    text = " ".join(str(value or "").split()).strip()
    if len(text) < 3:
        return False
    folded = text.casefold()
    identity = str(external_id or "").strip().casefold()
    if identity and folded in {identity, f"model {identity}", f"product {identity}"}:
        return False
    if re.fullmatch(r"[#\s\-_]*\d+[\s\-_]*", text):
        return False
    if "کاندیدای کشف‌شده" in text:
        return False
    return True


def _acquisition_quality_metrics(
    payload: dict[str, Any],
    *,
    local_dir: Path,
    external_id: str,
) -> dict[str, Any]:
    title = " ".join(str(payload.get("source_title") or "").split()).strip()
    description = " ".join(
        str(
            payload.get("source_description")
            or payload.get("source_short_description")
            or ""
        ).split()
    ).strip()
    image_urls = _json_urls(payload.get("selected_images_json"))
    for value in _json_urls(payload.get("images_json")):
        if value not in image_urls:
            image_urls.append(value)
    local_images = _local_image_files(local_dir)
    metrics = {
        "title": title[:220],
        "title_ok": _meaningful_source_title(title, external_id),
        "description_chars": len(description),
        "tags_count": _json_count(payload.get("tags_json"), list),
        "specs_count": _json_count(payload.get("source_specs_json"), dict),
        "category_present": bool(str(payload.get("source_category") or "").strip()),
        "author_present": bool(str(payload.get("author_name") or "").strip()),
        "image_urls_found": len(image_urls),
        "local_images": len(local_images),
    }
    metrics["data_signal"] = bool(
        metrics["description_chars"] >= 12
        or metrics["tags_count"] > 0
        or metrics["specs_count"] > 0
        or metrics["category_present"]
        or metrics["author_present"]
        or metrics["image_urls_found"] > 0
    )
    return metrics


def _assert_acquisition_quality(
    payload: dict[str, Any],
    *,
    local_dir: Path,
    external_id: str,
    require_image: bool,
) -> dict[str, Any]:
    metrics = _acquisition_quality_metrics(
        payload,
        local_dir=local_dir,
        external_id=external_id,
    )
    if not metrics["title_ok"]:
        raise AcquisitionQualityError(
            "Source page returned no meaningful Product title.",
            metrics,
        )
    if not metrics["data_signal"]:
        raise AcquisitionQualityError(
            "Source page returned a title but no usable Product data signals.",
            metrics,
        )
    if require_image and int(metrics["local_images"] or 0) <= 0:
        raise AcquisitionQualityError(
            "Source data was readable but no usable local Product image was acquired.",
            metrics,
        )
    return metrics


def _listing_referer(db, source_code: str, external_id: str, fallback: str) -> str:
    try:
        row = db.conn.execute(
            """
            SELECT discovered_from
            FROM discovered_urls
            WHERE source_code=? COLLATE NOCASE AND external_id=?
            ORDER BY id DESC LIMIT 1
            """,
            (str(source_code or ""), str(external_id or "")),
        ).fetchone()
        value = str(row["discovered_from"] or "").strip() if row is not None else ""
        if value.startswith(("http://", "https://")):
            return value
    except Exception:
        pass
    return str(fallback or "")


def _adaptive_method_order(preferred: str) -> tuple[str, ...]:
    aliases = {
        "classic_isolated": "classic_exact",
        "browser_dom": "classic_exact",
    }
    first = aliases.get(str(preferred or "").strip().lower(), str(preferred or "").strip().lower())
    if first == "saved_html":
        return ("saved_html",)
    if first not in ADAPTIVE_COLLECTION_METHODS:
        first = "rich"
    ordered = [first]
    for method in ADAPTIVE_COLLECTION_METHODS:
        if method not in ordered:
            ordered.append(method)
    return tuple(ordered)


async def _supplement_product_images_if_needed(
    db,
    source_code: str,
    external_id: str,
    product_url: str,
    local_dir: Path,
    payload: dict[str, Any],
    *,
    image_limit: int,
    download_images: bool,
) -> dict[str, Any]:
    if not download_images or _local_image_files(local_dir):
        return {"method": "", "downloaded": [], "urls": [], "error": ""}
    referer = _listing_referer(db, source_code, external_id, product_url)
    try:
        fallback = await collect_candidate_images_resilient(
            product_url,
            local_dir,
            image_limit=image_limit,
            referer=referer,
            headed=False,
        )
    except Exception as exc:
        return {
            "method": "",
            "downloaded": [],
            "urls": [],
            "error": f"{type(exc).__name__}: {exc}",
        }

    urls = [
        str(value).strip()
        for value in (fallback.get("image_urls") or [])
        if str(value or "").strip()
    ]
    downloaded = [
        str(value).strip()
        for value in (fallback.get("downloaded_images") or [])
        if str(value or "").strip()
    ]
    if downloaded:
        ordered = _json_urls(payload.get("selected_images_json"))
        for value in [*_json_urls(payload.get("images_json")), *urls]:
            if value and value not in ordered:
                ordered.append(value)
            if len(ordered) >= image_limit:
                break
        payload["images_json"] = json.dumps(ordered, ensure_ascii=False)
        payload["selected_images_json"] = json.dumps(ordered, ensure_ascii=False)
        payload["primary_image_url"] = ordered[0] if ordered else ""
    return {
        "method": str(fallback.get("acquisition_method") or ""),
        "downloaded": downloaded,
        "urls": urls,
        "error": "",
    }


async def _download_public_http_images(
    image_urls: list[str],
    local_dir: Path,
    *,
    referer: str,
    image_limit: int,
) -> list[str]:
    image_dir = Path(local_dir) / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    output: list[str] = []
    for index, image_url in enumerate(image_urls[: max(1, int(image_limit))], 1):
        suffix = Path(urlsplit(image_url).path).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
            suffix = ".jpg"
        target = image_dir / f"public_http_{index:03d}{suffix}"
        try:
            saved = await asyncio.to_thread(
                download_public_file,
                image_url,
                target,
                timeout=25,
                max_bytes=30_000_000,
                referer=referer,
            )
        except Exception:
            continue
        output.append(str(saved))
    return output


def _same_listing(left: str, right: str) -> bool:
    try:
        return normalize_url(str(left or "")) == normalize_url(str(right or ""))
    except Exception:
        return str(left or "").strip() == str(right or "").strip()


def _pending_for_listing(
    db,
    source_code: str,
    listing_url: str,
    limit: int,
    *,
    include_failed: bool = False,
):
    """Return a bounded queue page owned by the current Listing URL.

    New Qt runs persist the exact discovered_from value, so the fast indexed
    equality path normally answers the request. A bounded compatibility scan is
    retained for older rows whose tracking/query normalization differs.
    """
    statuses = ("new", "failed") if include_failed else ("new",)
    placeholders = ",".join("?" for _ in statuses)
    bounded_limit = max(1, int(limit or 1))
    exact = list(
        db.conn.execute(
            f"""
            SELECT *
            FROM discovered_urls
            WHERE source_code=?
              AND status IN ({placeholders})
              AND discovered_from=?
            ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END, id
            LIMIT ?
            """,
            (str(source_code or ""), *statuses, str(listing_url or ""), bounded_limit),
        )
    )
    if len(exact) >= bounded_limit:
        return exact[:bounded_limit]

    seen = {int(row["id"]) for row in exact}
    compatibility_limit = max(200, min(5000, bounded_limit * 12))
    fallback = list(
        db.conn.execute(
            f"""
            SELECT *
            FROM discovered_urls
            WHERE source_code=?
              AND status IN ({placeholders})
              AND discovered_from<>?
            ORDER BY id DESC
            LIMIT ?
            """,
            (str(source_code or ""), *statuses, str(listing_url or ""), compatibility_limit),
        )
    )
    output = list(exact)
    for row in fallback:
        if int(row["id"]) in seen:
            continue
        if not _same_listing(str(row["discovered_from"] or ""), listing_url):
            continue
        output.append(row)
        if len(output) >= bounded_limit:
            break
    return output[:bounded_limit]


def _source_dict(row) -> dict[str, Any]:
    return dict(row) if row is not None else {}


async def _browser_robots_gate(
    db,
    source_code: str,
    target_url: str,
) -> float:
    """Apply the same RFC9309/429 fail-closed contract before Browser work."""

    async with ModernHttpClient(db, str(source_code or "")) as client:
        policy = await robots_policy(client, target_url)
    if policy.known and not policy.allowed:
        raise RobotsDeniedError(
            f"robots.txt does not permit browser acquisition for {target_url}: "
            f"{policy.detail or 'denied'}"
        )
    return max(0.0, float(policy.crawl_delay or 0.0))


def _product_identity(source_cfg: dict[str, Any], url: str) -> tuple[str, str]:
    pattern = str(source_cfg.get("model_url_pattern") or "").strip()
    if pattern:
        match = re.search(pattern, str(url or ""), re.I)
        if match:
            matched = str(match.group(0) or url)
            external_id = str(match.groupdict().get("external_id") or "").strip()
            if not external_id:
                external_id = hashlib.sha1(matched.encode("utf-8")).hexdigest()[:16]
            return external_id, matched
    clean = str(url or "").split("#", 1)[0]
    return hashlib.sha1(clean.encode("utf-8")).hexdigest()[:16], clean


def _cap_product_images(parsed: dict[str, Any], limit: int) -> list[str]:
    try:
        raw = json.loads(parsed.get("images_json") or "[]")
    except Exception:
        raw = []
    images: list[str] = []
    for item in raw if isinstance(raw, list) else []:
        value = str(item or "").strip()
        if value and value not in images:
            images.append(value)
        if len(images) >= limit:
            break
    parsed["images_json"] = json.dumps(images, ensure_ascii=False)
    parsed["primary_image_url"] = images[0] if images else ""
    return images


def _write_local_mapping(
    local_dir: Path,
    dom_urls: list[str],
    downloaded_paths: list[str],
) -> None:
    """Bridge classic numeric image files to the strict Phase49.3C resolver."""
    items: list[dict[str, str]] = []
    for raw_path in downloaded_paths:
        path = Path(str(raw_path or ""))
        if not path.is_file():
            continue
        match = re.match(r"^(\d+)", path.stem)
        if not match:
            continue
        index = int(match.group(1)) - 1
        if not (0 <= index < len(dom_urls)):
            continue
        items.append({
            "url": str(dom_urls[index]),
            "local_file": str(path),
        })
    payload = {
        "schema": "qt42c-classic-image-map-v1",
        "images": items,
    }
    (local_dir / "page_extract.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def _discover_listing(
    db,
    source_cfg: dict[str, Any],
    listing_url: str,
    requested: int,
    *,
    strategy: str = "hybrid",
    progress: Progress = None,
    should_stop: ShouldStop = None,
) -> dict[str, int]:
    """Discover Product identities from one Search/Listing URL.

    hybrid:
        Modern conditional HTTP / Sitemap first, then the mature Browser
        listing explorer if more unseen identities are still needed.

    classic:
        Preserve the older owner-approved workflow: feed one Search/Listing
        link and keep scrolling progressively deeper on subsequent runs.
    """

    strategy = str(strategy or "hybrid").strip().lower()
    if strategy not in {"hybrid", "classic"}:
        raise ValueError("Discovery strategy must be hybrid or classic")

    source_code = str(source_cfg.get("code") or "").strip()
    model_pattern = str(source_cfg.get("model_url_pattern") or "").strip()
    new_count = 0
    duplicate_count = 0

    ensure_modern_schema(db)
    ensure_incremental_schema(db)

    from app import phase49_3i43_modern_acquisition_intelligence as modern
    modern.discover_sitemap_candidates = discover_sitemap_candidates_incremental

    if strategy == "hybrid":
        _emit(progress, 4, "کشف هوشمند از HTTP / Sitemap…")
        modern_candidates: list[dict[str, Any]] = []
        try:
            async with ModernHttpClient(db, source_code) as client:
                modern_candidates = await discover_conditional_http(
                    client,
                    listing_url,
                    source_code=source_code,
                    model_pattern=model_pattern,
                    requested=requested,
                )
        except (RobotsDeniedError, RateLimitedError):
            raise
        except AccessDeniedError as exc:
            # A public listing can reject plain HTTP while still being usable
            # through the existing browser collector. Do not repeat the same
            # blocked HTTP request; continue once into the mature browser path,
            # which performs its own robots gate before navigation.
            modern_candidates = []
            _emit(
                progress,
                5,
                f"HTTP listing blocked ({exc}); switching to robots-gated Browser fallback…",
            )
        except TransientHttpError:
            modern_candidates = []
        except Exception:
            modern_candidates = []

        for candidate in modern_candidates:
            if _stopped(should_stop):
                break
            external_id = str(candidate.get("external_id") or "").strip()
            url = str(
                candidate.get("source_url")
                or candidate.get("href")
                or ""
            ).strip()
            if not external_id or not url:
                continue
            if terminal_identity_state(db, source_code, external_id, url):
                duplicate_count += 1
                continue
            if db.add_discovered(
                source_code,
                external_id,
                url,
                listing_url,
            ):
                new_count += 1
            else:
                duplicate_count += 1

        if len(
            _pending_for_listing(
                db,
                source_code,
                listing_url,
                requested,
                include_failed=False,
            )
        ) >= requested:
            return {
                "new": new_count,
                "duplicates": duplicate_count,
            }

    # Classic fallback / explicit legacy mode.
    # Browser work never bypasses robots policy merely because the operator
    # selected the historical Search-Link workflow.
    browser_crawl_delay = await _browser_robots_gate(
        db,
        source_code,
        listing_url,
    )

    # 3I.38 remembers the prior listing depth so each rerun keeps moving
    # forward instead of restarting from the same first screen.
    stagnant = 0
    for round_no in range(1, 9):
        if _stopped(should_stop):
            break
        pending = len(
            _pending_for_listing(
                db,
                source_code,
                listing_url,
                requested,
                include_failed=False,
            )
        )
        if pending >= requested:
            break

        scroll_rounds = next_scroll_rounds(
            db,
            source_code,
            listing_url,
            default_rounds=8,
            step=8,
            maximum=96,
        )
        label = "کشف کلاسیک" if strategy == "classic" else "Fallback Browser"
        _emit(
            progress,
            min(22, 6 + round_no * 2),
            f"{label} — عمق {scroll_rounds} / جدید {new_count}",
        )

        if browser_crawl_delay > 0:
            await asyncio.sleep(min(30.0, browser_crawl_delay))
        result = await discover_classic(
            listing_url,
            model_pattern=model_pattern,
            scroll_rounds=scroll_rounds,
            headed=False,
        )
        new_this_round = 0
        for external_id, url in result.get("links") or []:
            if terminal_identity_state(
                db,
                source_code,
                external_id,
                url,
            ):
                duplicate_count += 1
                continue
            if db.add_discovered(
                source_code,
                external_id,
                url,
                listing_url,
            ):
                new_count += 1
                new_this_round += 1
            else:
                duplicate_count += 1

        record_listing_progress(
            db,
            source_code,
            listing_url,
            scroll_rounds=scroll_rounds,
            found_count=len(result.get("links") or []),
            new_count=new_this_round,
        )
        stagnant = stagnant + 1 if new_this_round <= 0 else 0
        if stagnant >= 2:
            break

    return {
        "new": new_count,
        "duplicates": duplicate_count,
    }


def _iter_public_file_urls(payload: dict[str, Any]) -> list[str]:
    output: list[str] = []
    for field in ("selected_file_links_json", "file_links_json"):
        try:
            raw = json.loads(payload.get(field) or "[]")
        except Exception:
            raw = []
        for item in raw if isinstance(raw, list) else []:
            if isinstance(item, dict):
                value = str(item.get("url") or item.get("href") or "").strip()
            else:
                value = str(item or "").strip()
            if value.startswith(("http://", "https://")) and value not in output:
                output.append(value)
    return output


def _download_public_model_files(
    payload: dict[str, Any],
    local_dir: Path,
    *,
    referer: str,
    same_domain_only: bool = True,
    limit: int = 12,
) -> list[str]:
    from urllib.parse import unquote, urlsplit

    saved: list[str] = []
    referer_host = urlsplit(str(referer or "")).netloc.lower()
    target_dir = Path(local_dir) / "files"
    for index, url in enumerate(_iter_public_file_urls(payload)[: max(1, int(limit))], 1):
        parsed = urlsplit(url)
        if same_domain_only and referer_host and parsed.netloc.lower() != referer_host:
            continue
        raw_name = unquote(Path(parsed.path).name) or f"file-{index:02d}.bin"
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", raw_name).strip(".-")
        if not safe_name:
            safe_name = f"file-{index:02d}.bin"
        target = target_dir / f"{index:02d}-{safe_name[:140]}"
        try:
            saved.append(
                str(
                    download_public_file(
                        url,
                        target,
                        max_bytes=120_000_000,
                        referer=referer,
                    )
                )
            )
        except Exception:
            # Optional public file download must never invalidate an otherwise
            # healthy Product acquisition. The source file links stay persisted.
            continue
    return saved


async def _collect_one(
    db,
    source_cfg: dict[str, Any],
    *,
    external_id: str,
    url: str,
    image_limit: int,
    local_dir: Path,
    download_images: bool = True,
    download_files: bool = False,
    same_domain_only: bool = True,
    image_progress: Callable[[int, int, str], None] | None = None,
    validate_quality: bool = False,
    require_usable_image: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    """Collect one Product with the richest existing project extractor."""
    ensure_epic49_desktop_schema(db)
    ensure_modern_schema(db)
    ensure_incremental_schema(db)

    source_code = str(source_cfg.get("code") or "")
    profile_dir = data_root() / "browser_profiles" / "qt42c-rich"

    product_crawl_delay = await _browser_robots_gate(db, source_code, url)
    if product_crawl_delay > 0:
        await asyncio.sleep(min(30.0, product_crawl_delay))

    result = await extract_direct_link(
        url,
        local_dir,
        profile_dir,
        headed=False,
        download_images=bool(download_images),
        image_limit=image_limit,
        image_progress=image_progress,
    )

    image_fallback = await _supplement_product_images_if_needed(
        db,
        source_code,
        external_id,
        url,
        local_dir,
        result,
        image_limit=image_limit,
        download_images=bool(download_images),
    )

    try:
        all_images = json.loads(result.get("images_json") or "[]")
    except Exception:
        all_images = []
    try:
        selected_images = json.loads(result.get("selected_images_json") or "[]")
    except Exception:
        selected_images = []

    ordered: list[str] = []
    for raw in [*(selected_images or []), *(all_images or [])]:
        value = str(raw or "").strip()
        if value and value not in ordered:
            ordered.append(value)
        if len(ordered) >= image_limit:
            break

    defaults = _source_defaults(source_cfg, image_limit)
    payload: dict[str, Any] = {
        **defaults,
        **{
            key: value
            for key, value in dict(result or {}).items()
            if key != "downloaded_image_files"
        },
        "source_code": source_code,
        "external_id": external_id,
        "source_url": str(result.get("source_url") or url),
        "local_dir": str(local_dir),
        "images_json": json.dumps(ordered, ensure_ascii=False),
        "selected_images_json": json.dumps(ordered, ensure_ascii=False),
        "primary_image_url": ordered[0] if ordered else "",
        "download_image_limit": image_limit,
        "acquisition_method": "qt42c-rich-page-extractor",
    }

    metrics = _acquisition_quality_metrics(
        payload,
        local_dir=local_dir,
        external_id=external_id,
    )
    if validate_quality:
        metrics = _assert_acquisition_quality(
            payload,
            local_dir=local_dir,
            external_id=external_id,
            require_image=bool(require_usable_image),
        )

    downloaded_model_files = (
        _download_public_model_files(
            payload,
            local_dir,
            referer=payload["source_url"],
            same_domain_only=bool(same_domain_only),
        )
        if download_files and persist
        else []
    )

    product_id = 0
    if persist:
        db.upsert_product(payload)
        normalized = normalize_url(payload["source_url"])
        product_row = db.conn.execute(
            """
            SELECT id
            FROM products
            WHERE source_code=?
              AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
            ORDER BY id DESC
            LIMIT 1
            """,
            (source_code, external_id, normalized),
        ).fetchone()
        if product_row is None:
            raise RuntimeError(
                "Product acquisition upsert completed but authoritative Catalog identity "
                "could not be resolved."
            )
        product_id = int(product_row["id"])
        remember_ledger(
            db,
            source_code,
            external_id,
            payload["source_url"],
            status="collected",
            discovered_from=url,
            force=False,
        )

    saved_files = _local_image_files(local_dir)
    output = {
        "product_id": product_id,
        "source_title": str(result.get("source_title") or ""),
        "images_found": int(metrics.get("image_urls_found") or len(ordered)),
        "images_saved": min(len(saved_files), image_limit),
        "files_saved": len(downloaded_model_files),
        "acquisition_method": "qt42c-rich-page-extractor",
        "selected_method": "rich",
        "image_fallback_method": str(image_fallback.get("method") or ""),
        "quality": metrics,
    }
    if not persist:
        output["source_payload"] = payload
    return output

async def _collect_one_legacy(
    db,
    source_cfg: dict[str, Any],
    *,
    external_id: str,
    url: str,
    image_limit: int,
    local_dir: Path,
    collection_method: str,
    download_images: bool = True,
    download_files: bool = False,
    same_domain_only: bool = True,
    saved_html_path: str = "",
    validate_quality: bool = False,
    require_usable_image: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    """Headless adapter for the distinct mature pre-Qt acquisition methods."""
    ensure_epic49_desktop_schema(db)
    ensure_modern_schema(db)
    ensure_incremental_schema(db)
    source_code = str(source_cfg.get("code") or "")
    requested_method = str(collection_method or "classic_exact").strip().lower()
    aliases = {
        "classic_isolated": "classic_exact",
        "browser_dom": "classic_exact",
    }
    method = aliases.get(requested_method, requested_method)
    if method not in {
        "classic_exact", "network_capture", "chrome_attached",
        "saved_html", "public_http",
    }:
        raise ValueError(f"روش Legacy ناشناخته است: {collection_method}")

    local_dir.mkdir(parents=True, exist_ok=True)
    downloaded_images: list[str] = []
    dom_image_urls: list[str] = []

    if method == "saved_html":
        html_path = Path(str(saved_html_path or ""))
        if not html_path.is_file():
            raise ValueError("برای Saved HTML یک فایل HTML معتبر انتخاب کن.")
        result = import_saved_html(html_path, url, local_dir)
        html = Path(result["html_path"]).read_text(encoding="utf-8", errors="replace")
        parsed = parse_product(
            html,
            str(result.get("final_url") or url),
            str(result.get("title") or ""),
            [],
        )
    elif method == "public_http":
        crawl_delay = await _browser_robots_gate(db, source_code, url)
        if crawl_delay > 0:
            await asyncio.sleep(min(30.0, crawl_delay))
        html = await asyncio.to_thread(public_http, url, 30)
        result = {
            "final_url": url,
            "title": "",
            "dom_image_urls": [],
            "downloaded_images": [],
        }
        parsed = parse_product(html, url, "", [])
        public_images = _cap_product_images(parsed, image_limit)
        if download_images and public_images:
            downloaded_images = await _download_public_http_images(
                public_images,
                local_dir,
                referer=url,
                image_limit=image_limit,
            )
    else:
        crawl_delay = await _browser_robots_gate(db, source_code, url)
        if crawl_delay > 0:
            await asyncio.sleep(min(30.0, crawl_delay))
        if method == "chrome_attached":
            result = await collect_attached_chrome(
                url,
                local_dir,
                capture_network=True,
                download_images=bool(download_images),
            )
        else:
            result = await collect_classic_exact(
                url,
                local_dir,
                headed=False,
                capture_network=(method == "network_capture"),
                download_images=bool(download_images),
                image_limit=image_limit,
            )
        html = Path(result["html_path"]).read_text(encoding="utf-8", errors="replace")
        dom_image_urls = list(result.get("dom_image_urls") or [])
        parsed = parse_product(
            html,
            str(result.get("final_url") or url),
            str(result.get("title") or ""),
            dom_image_urls,
        )
        downloaded_images = [
            str(value)
            for value in (result.get("downloaded_images") or [])
            if str(value or "").strip()
        ]
        if downloaded_images:
            _write_local_mapping(local_dir, dom_image_urls, downloaded_images)

    images = _cap_product_images(parsed, image_limit)
    parsed["selected_images_json"] = json.dumps(images, ensure_ascii=False)
    parsed["selected_file_links_json"] = parsed.get("file_links_json") or "[]"

    image_fallback = await _supplement_product_images_if_needed(
        db,
        source_code,
        external_id,
        url,
        local_dir,
        parsed,
        image_limit=image_limit,
        download_images=bool(download_images),
    )
    for value in image_fallback.get("downloaded") or []:
        text = str(value or "").strip()
        if text and text not in downloaded_images:
            downloaded_images.append(text)

    images = _cap_product_images(parsed, image_limit)
    parsed["selected_images_json"] = json.dumps(images, ensure_ascii=False)

    payload = {
        **_source_defaults(source_cfg, image_limit),
        **parsed,
        "source_code": source_code,
        "external_id": external_id,
        "source_url": str(result.get("final_url") or url),
        "local_dir": str(local_dir),
        "download_image_limit": image_limit,
        "source_snapshot_json": json.dumps(
            {
                "legacy_manifest": {
                    key: value
                    for key, value in dict(result).items()
                    if key not in {"html_path"}
                }
            },
            ensure_ascii=False,
            default=str,
        ),
        "acquisition_method": f"qt52g-{method}",
    }

    metrics = _acquisition_quality_metrics(
        payload,
        local_dir=local_dir,
        external_id=external_id,
    )
    if validate_quality:
        metrics = _assert_acquisition_quality(
            payload,
            local_dir=local_dir,
            external_id=external_id,
            require_image=bool(require_usable_image),
        )

    downloaded_model_files = (
        _download_public_model_files(
            payload,
            local_dir,
            referer=payload["source_url"],
            same_domain_only=bool(same_domain_only),
        )
        if download_files and persist
        else []
    )

    product_id = 0
    if persist:
        db.upsert_product(payload)
        normalized = normalize_url(payload["source_url"])
        product_row = db.conn.execute(
            """
            SELECT id FROM products
            WHERE source_code=?
              AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
            ORDER BY id DESC LIMIT 1
            """,
            (source_code, external_id, normalized),
        ).fetchone()
        if product_row is None:
            raise RuntimeError("Legacy acquisition completed but Product identity was not persisted.")
        product_id = int(product_row["id"])
        remember_ledger(
            db,
            source_code,
            external_id,
            payload["source_url"],
            status="collected",
            discovered_from=("saved_html" if method == "saved_html" else url),
            force=False,
        )

    output = {
        "product_id": product_id,
        "source_title": str(parsed.get("source_title") or ""),
        "images_found": int(metrics.get("image_urls_found") or len(images)),
        "images_saved": min(len(_local_image_files(local_dir)), image_limit),
        "files_saved": len(downloaded_model_files),
        "acquisition_method": f"qt52g-{method}",
        "selected_method": method,
        "image_fallback_method": str(image_fallback.get("method") or ""),
        "quality": metrics,
    }
    if not persist:
        output["source_payload"] = payload
    return output


async def _collect_one_adaptive(
    db,
    source_cfg: dict[str, Any],
    *,
    external_id: str,
    url: str,
    image_limit: int,
    local_dir: Path,
    preferred_method: str = "rich",
    download_images: bool = True,
    download_files: bool = False,
    same_domain_only: bool = True,
    saved_html_path: str = "",
    image_progress: Callable[[int, int, str], None] | None = None,
    progress: Progress = None,
    operation: str = "product_acquisition",
    persist: bool = True,
) -> dict[str, Any]:
    attempts: list[dict[str, str]] = []
    order = _adaptive_method_order(preferred_method)
    for position, method in enumerate(order, 1):
        _emit(
            progress,
            min(94, 8 + position * 3),
            f"ID={external_id} • روش {position}/{len(order)}: {method}",
        )
        acquisition_event(
            db,
            "method_attempt",
            status="start",
            source_code=str(source_cfg.get("code") or ""),
            external_id=external_id,
            url=url,
            method=method,
            detail={
                "operation": operation,
                "position": position,
                "method_order": list(order),
                "image_limit": int(image_limit),
                "download_images": bool(download_images),
            },
        )
        try:
            if method == "rich":
                result = await _collect_one(
                    db,
                    source_cfg,
                    external_id=external_id,
                    url=url,
                    image_limit=image_limit,
                    local_dir=local_dir,
                    download_images=bool(download_images),
                    download_files=bool(download_files),
                    same_domain_only=bool(same_domain_only),
                    image_progress=image_progress,
                    validate_quality=True,
                    require_usable_image=bool(download_images),
                    persist=bool(persist),
                )
            else:
                result = await _collect_one_legacy(
                    db,
                    source_cfg,
                    external_id=external_id,
                    url=url,
                    image_limit=image_limit,
                    local_dir=local_dir,
                    collection_method=method,
                    download_images=bool(download_images),
                    download_files=bool(download_files),
                    same_domain_only=bool(same_domain_only),
                    saved_html_path=saved_html_path,
                    validate_quality=True,
                    require_usable_image=bool(download_images),
                    persist=bool(persist),
                )
            result = dict(result or {})
            result["selected_method"] = method
            result["attempted_methods"] = [
                *[row["method"] for row in attempts],
                method,
            ]
            result["fallback_used"] = bool(attempts)
            acquisition_event(
                db,
                "method_selected",
                status="success",
                source_code=str(source_cfg.get("code") or ""),
                external_id=external_id,
                url=url,
                method=method,
                detail={
                    "operation": operation,
                    "quality": dict(result.get("quality") or {}),
                    "images_found": int(result.get("images_found") or 0),
                    "images_saved": int(result.get("images_saved") or 0),
                    "image_fallback_method": str(result.get("image_fallback_method") or ""),
                    "attempted_methods": result["attempted_methods"],
                },
            )
            _emit(
                progress,
                95,
                f"ID={external_id} • روش موفق: {method} • "
                f"عکس محلی {result.get('images_saved', 0)}/{image_limit}",
            )
            return result
        except (RobotsDeniedError, RateLimitedError) as exc:
            acquisition_event(
                db,
                "method_policy_stop",
                status="error",
                source_code=str(source_cfg.get("code") or ""),
                external_id=external_id,
                url=url,
                method=method,
                message=f"{type(exc).__name__}: {exc}",
                detail={"operation": operation},
            )
            raise
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            metrics = dict(getattr(exc, "metrics", {}) or {})
            attempts.append({"method": method, "error": detail})
            acquisition_event(
                db,
                "method_failed",
                status="error",
                source_code=str(source_cfg.get("code") or ""),
                external_id=external_id,
                url=url,
                method=method,
                message=detail,
                detail={
                    "operation": operation,
                    "quality": metrics,
                    "next_method": order[position] if position < len(order) else "",
                },
            )
            _emit(
                progress,
                min(94, 8 + position * 3),
                f"ID={external_id} • {method} ناموفق؛ "
                + ("روش بعدی…" if position < len(order) else "روش دیگری باقی نمانده"),
            )
            continue

    acquisition_event(
        db,
        "all_methods_failed",
        status="error",
        source_code=str(source_cfg.get("code") or ""),
        external_id=external_id,
        url=url,
        method="",
        message="All distinct Product acquisition methods failed.",
        detail={"operation": operation, "attempts": attempts},
    )
    raise AcquisitionMethodsExhausted(attempts)

def _cache_candidate_thumbnail(candidate: dict[str, Any]) -> str:
    url = str(candidate.get("thumbnail_url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return ""
    target = candidate_preview_cache_path(
        str(candidate.get("source_code") or ""),
        str(candidate.get("external_id") or ""),
    )
    if target.is_file() and target.stat().st_size > 0:
        return str(target)
    request = urlrequest.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": str(
                candidate.get("discovered_from")
                or candidate.get("source_url")
                or ""
            ),
        },
    )
    try:
        with urlrequest.urlopen(request, timeout=8) as response:
            content_type = str(response.headers.get("Content-Type") or "").lower()
            if content_type and not content_type.startswith("image/"):
                return ""
            raw = response.read(5_000_001)
        if not raw or len(raw) > 5_000_000:
            return ""
        with Image.open(io.BytesIO(raw)) as image:
            prepared = ImageOps.exif_transpose(image).convert("RGB")
            prepared.thumbnail((720, 540), Image.Resampling.LANCZOS)
            temp = target.with_suffix(".tmp.jpg")
            prepared.save(temp, format="JPEG", quality=86, optimize=True)
            temp.replace(target)
        return str(target)
    except Exception:
        return ""

async def _preview_listing_candidates(
    db,
    source_cfg: dict[str, Any],
    listing_url: str,
    requested: int,
    *,
    progress: Progress = None,
    should_stop: ShouldStop = None,
) -> dict[str, Any]:
    """Restore the mature Preview-first UX without replacing the crawler."""
    ensure_candidate_schema(db)
    source_code = str(source_cfg.get("code") or "")
    model_pattern = str(source_cfg.get("model_url_pattern") or "")
    delay = await _browser_robots_gate(db, source_code, listing_url)
    if delay > 0:
        await asyncio.sleep(min(30.0, delay))
    _emit(progress, 2, "پیش‌نمایش لیست: عنوان و تصویر کارت‌های محصول در حال خواندن است…")
    try:
        candidates = await discover_preview_candidates_safe(
            listing_url,
            source_code=source_code,
            model_pattern=model_pattern,
            requested=max(1, min(500, int(requested or 1))),
            scroll_rounds=8,
            headed=False,
        )
    except (RobotsDeniedError, RateLimitedError):
        raise
    except Exception as exc:
        _emit(
            progress,
            4,
            "پیش‌نمایش تصویری در دسترس نبود؛ کشف اصلی بدون تکرار Preview ادامه دارد "
            f"({type(exc).__name__}).",
        )
        return {"previewed": 0, "new": 0, "duplicates": 0, "thumbs": 0}

    new_count = duplicate_count = 0
    prepared: list[dict[str, Any]] = []
    for candidate in candidates:
        if _stopped(should_stop):
            break
        item = dict(candidate)
        item["discovered_from"] = listing_url
        upsert_candidate(db, item)
        if terminal_identity_state(
            db,
            source_code,
            str(item.get("external_id") or ""),
            str(item.get("source_url") or ""),
        ):
            duplicate_count += 1
        elif db.add_discovered(
            source_code,
            str(item.get("external_id") or ""),
            str(item.get("source_url") or ""),
            listing_url,
        ):
            new_count += 1
        else:
            duplicate_count += 1
        prepared.append(item)

    _emit(
        progress,
        8,
        f"پیش‌نمایش: {len(prepared)} محصول پیدا شد؛ تصاویر Preview در حال آماده‌سازی است.",
    )

    semaphore = asyncio.Semaphore(10)
    thumb_count = 0

    async def cache_one(item):
        async with semaphore:
            if _stopped(should_stop):
                return ""
            return await asyncio.to_thread(_cache_candidate_thumbnail, item)

    thumbnail_candidates = [
        item for item in prepared
        if str(item.get("thumbnail_url") or "").startswith(("http://", "https://"))
    ][: min(150, max(1, int(requested or 1)))]
    tasks = [asyncio.create_task(cache_one(item)) for item in thumbnail_candidates]
    if tasks:
        completed = 0
        for task in asyncio.as_completed(tasks):
            try:
                if await task:
                    thumb_count += 1
            except Exception:
                pass
            completed += 1
            if completed == len(tasks) or completed % 8 == 0:
                _emit(
                    progress,
                    min(18, 8 + int(completed / max(1, len(tasks)) * 10)),
                    f"Preview تصویر {completed}/{len(tasks)} • آماده {thumb_count}",
                )

    return {
        "previewed": len(prepared),
        "new": new_count,
        "duplicates": duplicate_count,
        "thumbs": thumb_count,
    }

def _mark_candidate_result(
    db,
    source_code: str,
    external_id: str,
    status: str,
    *,
    product_id: int | None = None,
    error: str = "",
) -> None:
    try:
        candidate = candidate_by_identity(db, source_code, external_id)
        if candidate is not None:
            set_candidate_status(
                db,
                int(candidate["id"]),
                status,
                product_id=product_id,
                error=error,
            )
    except Exception:
        return

async def run_batch_async(
    db,
    *,
    source_code: str,
    listing_url: str,
    requested: int = 100,
    image_limit: int = 5,
    include_failed: bool = False,
    strategy: str = "hybrid",
    operator_mode: str = "search",
    download_images: bool = True,
    download_files: bool = False,
    same_domain_only: bool = True,
    collection_method: str = "rich",
    progress: Progress = None,
    should_stop: ShouldStop = None,
) -> dict[str, Any]:
    requested = max(1, min(500, int(requested or 1)))
    image_limit = normalize_image_limit(image_limit)
    listing_url = str(listing_url or "").strip()
    if not listing_url.startswith(("http://", "https://")):
        raise ValueError("لینک Search/Listing معتبر وارد کن.")

    source_row = db.source(source_code)
    if source_row is None:
        raise ValueError("سایت مادر انتخاب‌شده در تنظیمات Source وجود ندارد.")
    source_cfg = _source_dict(source_row)
    if not int(source_cfg.get("enabled") or 0):
        raise RuntimeError("Source انتخاب‌شده غیرفعال است.")

    strategy = str(strategy or "hybrid").strip().lower()
    if strategy not in {"hybrid", "classic"}:
        raise ValueError("روش Crawl نامعتبر است.")
    collection_method = str(collection_method or "rich").strip().lower()
    allowed_collection = {
        "rich", "classic_isolated", "classic_exact", "network_capture",
        "chrome_attached", "browser_dom", "public_http",
    }
    if collection_method not in allowed_collection:
        raise ValueError("روش دریافت Product نامعتبر است.")
    operator_mode = str(operator_mode or "search").strip().lower()
    if operator_mode not in {"automatic", "search", "category", "site_crawl", "listing"}:
        raise ValueError("نوع دریافت گروهی نامعتبر است.")

    run_id = db.create_run(
        source_code,
        f"qt_{operator_mode}",
        f"{strategy}-discovery+adaptive-{collection_method}-product",
        requested,
    )
    discovered = collected = duplicates = failed = 0
    failures: list[str] = []
    circuit_breaker = False
    unattempted = 0
    preferred_method = collection_method

    acquisition_event(
        db,
        "batch_start",
        status="start",
        source_code=source_code,
        url=listing_url,
        method=preferred_method,
        detail={
            "requested": requested,
            "image_limit": image_limit,
            "strategy": strategy,
            "operator_mode": operator_mode,
        },
    )

    try:
        preview = await _preview_listing_candidates(
            db,
            source_cfg,
            listing_url,
            requested,
            progress=progress,
            should_stop=should_stop,
        )
        discovered += int(preview.get("new") or 0)
        duplicates += int(preview.get("duplicates") or 0)

        pending_after_preview = len(
            _pending_for_listing(
                db,
                source_code,
                listing_url,
                requested,
                include_failed=bool(include_failed),
            )
        )
        if pending_after_preview < requested and not _stopped(should_stop):
            discovery = await _discover_listing(
                db,
                source_cfg,
                listing_url,
                requested,
                strategy=strategy,
                progress=progress,
                should_stop=should_stop,
            )
            discovered += int(discovery["new"])
            duplicates += int(discovery["duplicates"])
        _emit(
            progress,
            23,
            f"کشف تمام شد — {discovered} مورد جدید / {duplicates} تکراری؛ "
            "دریافت Product با Failover تطبیقی شروع می‌شود.",
        )

        rows = _pending_for_listing(
            db,
            source_code,
            listing_url,
            requested,
            include_failed=bool(include_failed),
        )
        if not rows:
            _emit(progress, 100, "مورد جدیدی برای دریافت پیدا نشد.")
            db.finish_run(
                run_id,
                status="completed",
                discovered_count=discovered,
                collected_count=0,
                duplicate_count=duplicates,
                failed_count=0,
                message="No new pending product identity.",
            )
            return {
                "run_id": run_id,
                "discovered": discovered,
                "collected": 0,
                "duplicates": duplicates,
                "failed": 0,
                "stopped": False,
                "circuit_breaker": False,
                "unattempted": 0,
                "preferred_method": preferred_method,
            }

        total = len(rows)
        for index, row in enumerate(rows, 1):
            if _stopped(should_stop):
                break

            external_id = str(row["external_id"] or row["id"])
            url = str(row["url"] or "")
            local_dir = data_root() / "collected" / source_code / external_id
            _emit(
                progress,
                24 + int((index - 1) / max(1, total) * 72),
                f"محصول {index}/{total} • ID={external_id} • "
                f"شروع با روش {preferred_method}",
            )

            def image_progress(saved: int, target: int, _image_url: str) -> None:
                fraction = min(1.0, max(0.0, float(saved) / max(1, int(target))))
                overall = 24 + int(((index - 1) + fraction) / max(1, total) * 72)
                _emit(
                    progress,
                    overall,
                    f"محصول {index}/{total} • ID={external_id} • عکس {saved}/{target}",
                )

            try:
                result = await _collect_one_adaptive(
                    db,
                    source_cfg,
                    external_id=external_id,
                    url=url,
                    image_limit=image_limit,
                    local_dir=local_dir,
                    preferred_method=preferred_method,
                    download_images=bool(download_images),
                    download_files=bool(download_files),
                    same_domain_only=bool(same_domain_only),
                    image_progress=image_progress,
                    progress=progress,
                    operation="batch_product",
                    persist=True,
                )
                preferred_method = str(result.get("selected_method") or preferred_method)
                db.mark_url(int(row["id"]), "collected")
                _mark_candidate_result(
                    db,
                    source_code,
                    external_id,
                    "imported",
                    product_id=int(result.get("product_id") or 0) or None,
                )
                collected += 1
                _emit(
                    progress,
                    24 + int(index / max(1, total) * 72),
                    f"محصول {index}/{total} • ID={external_id} • "
                    f"روش {preferred_method} • {result.get('images_saved', 0)}/{image_limit} عکس محلی",
                )
            except (RobotsDeniedError, RateLimitedError, PermissionError) as exc:
                db.mark_url(int(row["id"]), "failed", str(exc))
                _mark_candidate_result(db, source_code, external_id, "failed", error=str(exc))
                failed += 1
                failures.append(f"{url}: {type(exc).__name__}: {exc}")
                circuit_breaker = True
                unattempted = max(0, total - index)
                break
            except Exception as exc:
                message = f"{type(exc).__name__}: {exc}"
                db.mark_url(int(row["id"]), "failed", message)
                _mark_candidate_result(db, source_code, external_id, "failed", error=message)
                failed += 1
                failures.append(f"{url}: {message}")
                circuit_breaker = True
                unattempted = max(0, total - index)
                _emit(
                    progress,
                    min(99, 24 + int(index / max(1, total) * 72)),
                    f"توقف حفاظتی روی ID={external_id}: همه روش‌های واقعی ناموفق بودند؛ "
                    f"{unattempted} مورد بعدی دست‌نخورده ماند.",
                )
                break

            if index < total:
                await asyncio.sleep(0.8)

        stopped = _stopped(should_stop)
        status = "stopped" if stopped else (
            "failed" if circuit_breaker and not collected else "completed"
        )
        message = (
            f"Qt acquisition: collected={collected}, failed={failed}, "
            f"new={discovered}, duplicates={duplicates}, "
            f"circuit_breaker={int(circuit_breaker)}, unattempted={unattempted}, "
            f"preferred_method={preferred_method}"
        )
        db.finish_run(
            run_id,
            status=status,
            discovered_count=discovered,
            collected_count=collected,
            duplicate_count=duplicates,
            failed_count=failed,
            message=message,
        )
        acquisition_event(
            db,
            "batch_done",
            status="error" if circuit_breaker else "success",
            source_code=source_code,
            url=listing_url,
            method=preferred_method,
            message=message,
            detail={
                "collected": collected,
                "failed": failed,
                "unattempted": unattempted,
                "circuit_breaker": circuit_breaker,
            },
        )
        _emit(progress, 100, message)
        return {
            "run_id": run_id,
            "discovered": discovered,
            "collected": collected,
            "duplicates": duplicates,
            "failed": failed,
            "stopped": stopped,
            "failures": failures[:12],
            "circuit_breaker": circuit_breaker,
            "unattempted": unattempted,
            "preferred_method": preferred_method,
        }
    except Exception as exc:
        db.finish_run(
            run_id,
            status="failed",
            discovered_count=discovered,
            collected_count=collected,
            duplicate_count=duplicates,
            failed_count=failed + 1,
            message=str(exc),
        )
        acquisition_event(
            db,
            "batch_error",
            status="error",
            source_code=source_code,
            url=listing_url,
            method=preferred_method,
            message=f"{type(exc).__name__}: {exc}",
        )
        raise

async def refresh_source_products_async(
    db,
    *,
    source_code: str,
    limit: int = 20,
    image_limit: int = 10,
    download_images: bool = True,
    progress: Progress = None,
    should_stop: ShouldStop = None,
) -> dict[str, Any]:
    """Safely refresh source-owned Products with adaptive method failover."""
    source_row = db.source(str(source_code or ""))
    if source_row is None:
        raise ValueError("Source انتخاب‌شده پیدا نشد.")
    rows = db.product_page(
        filter_name="all",
        source_code=source_code,
        sort_key="newest",
        limit=max(1, min(500, int(limit or 20))),
        offset=0,
    )
    changed = unchanged = failed = 0
    total = len(rows)
    preferred_method = "rich"
    circuit_breaker = False
    unattempted = 0

    for index, lite in enumerate(rows, 1):
        if _stopped(should_stop):
            break
        row = db.product(int(lite["id"]))
        if row is None:
            continue
        try:
            _emit(
                progress,
                int((index - 1) / max(1, total) * 95),
                f"بروزرسانی {index}/{total} • Product #{int(row['id'])} • روش {preferred_method}",
            )
            result = await refetch_product_from_source_async(
                db,
                int(row["id"]),
                image_limit=image_limit,
                download_images=bool(download_images),
                progress=progress,
                preferred_method=preferred_method,
                adaptive_fallback=True,
            )
            preferred_method = str(result.get("selected_method") or preferred_method)
            if bool(result.get("changed")):
                changed += 1
            else:
                unchanged += 1
        except (RobotsDeniedError, RateLimitedError, PermissionError):
            failed += 1
            circuit_breaker = True
            unattempted = max(0, total - index)
            break
        except Exception as exc:
            failed += 1
            circuit_breaker = True
            unattempted = max(0, total - index)
            acquisition_event(
                db,
                "source_refresh_stop",
                status="error",
                source_code=source_code,
                method=preferred_method,
                message=f"{type(exc).__name__}: {exc}",
                detail={"product_id": int(row["id"]), "unattempted": unattempted},
            )
            break

    _emit(
        progress,
        100,
        f"بروزرسانی Source تمام شد — changed={changed}, unchanged={unchanged}, "
        f"failed={failed}, unattempted={unattempted}, method={preferred_method}",
    )
    return {
        "source_code": source_code,
        "changed": changed,
        "unchanged": unchanged,
        "failed": failed,
        "stopped": _stopped(should_stop),
        "circuit_breaker": circuit_breaker,
        "unattempted": unattempted,
        "preferred_method": preferred_method,
    }

def refresh_source_products(db, **kwargs) -> dict[str, Any]:
    return asyncio.run(refresh_source_products_async(db, **kwargs))


def run_batch(db, **kwargs) -> dict[str, Any]:
    return asyncio.run(run_batch_async(db, **kwargs))


async def run_single_async(
    db,
    *,
    source_code: str,
    product_url: str,
    image_limit: int = 5,
    download_images: bool = True,
    download_files: bool = False,
    same_domain_only: bool = True,
    collection_method: str = "rich",
    saved_html_path: str = "",
    progress: Progress = None,
    force_recover: bool = False,
    adaptive_fallback: bool = False,
) -> dict[str, Any]:
    source_row = db.source(source_code)
    if source_row is None:
        raise ValueError("Source انتخاب‌شده پیدا نشد.")
    source_cfg = _source_dict(source_row)
    image_limit = normalize_image_limit(image_limit)
    external_id, url = _product_identity(source_cfg, product_url)
    normalized = normalize_url(url)
    existing = db.conn.execute(
        """
        SELECT id, is_blocked
        FROM products
        WHERE source_code = ? COLLATE NOCASE
          AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
        ORDER BY id DESC LIMIT 1
        """,
        (source_code, external_id, normalized),
    ).fetchone()

    if force_recover and existing is not None:
        if int(existing["is_blocked"] or 0):
            raise RuntimeError(
                "Product is rejected/blocked. Restore it before source recovery."
            )
        recovered = await refetch_product_from_source_async(
            db,
            int(existing["id"]),
            image_limit=image_limit,
            download_images=bool(download_images),
            progress=progress,
            preferred_method=collection_method,
            adaptive_fallback=bool(adaptive_fallback),
        )
        return {
            **dict(recovered or {}),
            "already_collected": True,
            "recovered_existing": True,
        }

    if not force_recover and terminal_identity_state(
        db,
        source_code,
        external_id,
        url,
    ):
        return {
            "product_id": int(existing["id"]) if existing else 0,
            "already_collected": True,
        }

    _emit(progress, 5, f"دریافت مستقیم صفحه محصول • ID={external_id}")
    local_dir = data_root() / "collected" / source_code / external_id
    method = str(collection_method or "rich").strip().lower()

    def image_progress(saved: int, target: int, _image_url: str) -> None:
        _emit(
            progress,
            min(92, 8 + int(saved / max(1, target) * 84)),
            f"ID={external_id} • عکس {saved}/{target}",
        )

    if adaptive_fallback:
        result = await _collect_one_adaptive(
            db,
            source_cfg,
            external_id=external_id,
            url=url,
            image_limit=image_limit,
            local_dir=local_dir,
            preferred_method=method,
            download_images=bool(download_images),
            download_files=bool(download_files),
            same_domain_only=bool(same_domain_only),
            saved_html_path=saved_html_path,
            image_progress=image_progress,
            progress=progress,
            operation="single_recovery" if force_recover else "single_product",
            persist=True,
        )
    elif method == "rich":
        result = await _collect_one(
            db,
            source_cfg,
            external_id=external_id,
            url=url,
            image_limit=image_limit,
            local_dir=local_dir,
            download_images=bool(download_images),
            download_files=bool(download_files),
            same_domain_only=bool(same_domain_only),
            image_progress=image_progress,
        )
    else:
        result = await _collect_one_legacy(
            db,
            source_cfg,
            external_id=external_id,
            url=url,
            image_limit=image_limit,
            local_dir=local_dir,
            collection_method=method,
            download_images=bool(download_images),
            download_files=bool(download_files),
            same_domain_only=bool(same_domain_only),
            saved_html_path=saved_html_path,
        )
    _emit(progress, 100, "محصول و تصاویر دریافت شد.")
    return result

def run_single(db, **kwargs) -> dict[str, Any]:
    return asyncio.run(run_single_async(db, **kwargs))


async def refetch_product_from_source_async(
    db,
    product_id: int,
    *,
    image_limit: int = 10,
    download_images: bool = True,
    progress: Progress = None,
    preferred_method: str = "rich",
    adaptive_fallback: bool = False,
) -> dict[str, Any]:
    """Re-fetch source facts/images without overwriting operator work."""
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError("محصول پیدا نشد.")
    old = dict(row)
    source_code = str(old.get("source_code") or "")
    source_cfg = _source_dict(db.source(source_code))
    if not source_cfg:
        raise RuntimeError("Source محصول پیدا نشد.")
    source_url = str(old.get("source_url") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        raise RuntimeError("لینک منبع محصول معتبر نیست.")

    image_limit = normalize_image_limit(image_limit)
    external_id = str(old.get("external_id") or "").strip()
    if not external_id:
        external_id, _ = _product_identity(source_cfg, source_url)

    _emit(progress, 3, "بازیابی امن داده و تصاویر از صفحه اصلی محصول…")
    output = data_root() / "collected" / source_code / f"{external_id}_refresh_latest"

    def image_progress(saved: int, target: int, _image_url: str) -> None:
        _emit(
            progress,
            min(88, 12 + int(saved / max(1, target) * 76)),
            f"بازیابی تصویر {saved}/{target}",
        )

    if adaptive_fallback:
        result = await _collect_one_adaptive(
            db,
            source_cfg,
            external_id=external_id,
            url=source_url,
            image_limit=image_limit,
            local_dir=output,
            preferred_method=preferred_method,
            download_images=bool(download_images),
            download_files=False,
            same_domain_only=True,
            image_progress=image_progress,
            progress=progress,
            operation="source_refetch",
            persist=False,
        )
    else:
        result = await _collect_one(
            db,
            source_cfg,
            external_id=external_id,
            url=source_url,
            image_limit=image_limit,
            local_dir=output,
            download_images=bool(download_images),
            download_files=False,
            same_domain_only=True,
            image_progress=image_progress,
            persist=False,
        )

    fresh = dict(result.get("source_payload") or {})
    if not fresh:
        raise RuntimeError("Source recovery returned no source payload.")
    fresh["last_refetched_at"] = utc_now()
    fresh["source_state"] = "active"
    fresh["fingerprint"] = product_fingerprint(
        source_code,
        external_id,
        str(fresh.get("source_url") or source_url),
    )
    fresh["source_hash"] = source_payload_hash(fresh)
    fresh["needs_update"] = (
        1
        if should_mark_needs_update(row, fresh["source_hash"])
        else int(old.get("needs_update") or 0)
    )
    fresh["content_status"] = (
        "stale"
        if fresh["needs_update"]
        else str(old.get("content_status") or "pending")
    )

    diff = product_diff(old, fresh)
    merged = merge_refetch(row, fresh)
    allowed = set(row.keys()) - {"id", "created_at", "updated_at"}
    db.update_product(
        int(product_id),
        {key: value for key, value in merged.items() if key in allowed},
    )
    after = dict(db.product(int(product_id)))
    db.save_history(
        int(product_id),
        "source_product_recovery",
        old,
        after,
        diff_summary(diff),
    )
    _emit(
        progress,
        100,
        f"بازیابی کامل شد • روش {result.get('selected_method') or preferred_method} • "
        f"{result.get('images_saved', 0)}/{image_limit} عکس محلی",
    )
    return {
        "product_id": int(product_id),
        "changed": bool(diff) or str(old.get("local_dir") or "") != str(output),
        "diff": diff,
        "images_found": int(result.get("images_found") or 0),
        "images_saved": int(result.get("images_saved") or 0),
        "source_title": str(fresh.get("source_title") or ""),
        "selected_method": str(result.get("selected_method") or preferred_method),
        "attempted_methods": list(result.get("attempted_methods") or []),
        "fallback_used": bool(result.get("fallback_used")),
        "image_fallback_method": str(result.get("image_fallback_method") or ""),
        "quality": dict(result.get("quality") or {}),
    }

def refetch_product_from_source(db, product_id: int, **kwargs) -> dict[str, Any]:
    return asyncio.run(
        refetch_product_from_source_async(
            db,
            int(product_id),
            **kwargs,
        )
    )

async def recover_product_images_async(
    db,
    product_id: int,
    *,
    image_limit: int = 10,
    progress: Progress = None,
) -> dict[str, Any]:
    # Compatibility name retained for old callers. The implementation is now
    # the safe mature source-refetch merge, so image recovery can also restore
    # source-owned title/spec/tag/weight/time facts without clobbering operator
    # price/Profile/Filament/SEO/publish decisions.
    return await refetch_product_from_source_async(
        db,
        int(product_id),
        image_limit=image_limit,
        download_images=True,
        progress=progress,
        preferred_method="rich",
        adaptive_fallback=True,
    )


def recover_product_images(db, product_id: int, **kwargs) -> dict[str, Any]:
    return asyncio.run(
        recover_product_images_async(
            db,
            int(product_id),
            **kwargs,
        )
    )
