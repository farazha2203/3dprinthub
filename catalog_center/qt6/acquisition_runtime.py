from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from app.classic_methods import (
    collect_attached_chrome,
    collect_classic_exact,
    discover_classic,
    import_saved_html,
)
from app.crawler import BrowserSession, download_public_file, parse_product
from app.db import normalize_url, utc_now
from app.page_extractor import extract_direct_link
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.phase49_3h_image_limits import normalize_image_limit
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
from app.phase49_3i_discovery_review import _source_defaults
from app.runtime_paths import data_root
from app.v8_features import (
    diff_summary,
    merge_refetch,
    product_diff,
    product_fingerprint,
    source_payload_hash,
)
from app.workflow import should_mark_needs_update


Progress = Callable[[int, str], None] | None
ShouldStop = Callable[[], bool] | None


def _emit(progress: Progress, value: int, message: str) -> None:
    if callable(progress):
        progress(max(0, min(100, int(value))), str(message))


def _stopped(should_stop: ShouldStop) -> bool:
    return bool(callable(should_stop) and should_stop())


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
        except (RobotsDeniedError, RateLimitedError, AccessDeniedError):
            raise
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
) -> dict[str, Any]:
    """Collect one Product with the richest existing project extractor.

    The RichPageExtractor already combines:
    - rendered DOM;
    - JSON-LD;
    - embedded Next/Nuxt JSON;
    - bounded same-site XHR/fetch JSON;
    - breadcrumbs/spec tables;
    - scored high-quality Product images.

    We intentionally reuse that mature authority instead of maintaining a
    second weaker parser in Qt.
    """

    # Product acquisition writes mature Epic49 Catalog fields such as
    # download_image_limit and slider/profile columns. Fresh/test Catalog DBs
    # must receive the same additive desktop schema before any upsert.
    ensure_epic49_desktop_schema(db)
    ensure_modern_schema(db)
    ensure_incremental_schema(db)

    source_code = str(source_cfg.get("code") or "")
    profile_dir = data_root() / "browser_profiles" / "qt42c-rich"

    product_crawl_delay = await _browser_robots_gate(
        db,
        source_code,
        url,
    )
    if product_crawl_delay > 0:
        await asyncio.sleep(min(30.0, product_crawl_delay))

    result = await extract_direct_link(
        url,
        local_dir,
        profile_dir,
        headed=False,
        download_images=bool(download_images),
        image_limit=image_limit,
    )

    try:
        all_images = json.loads(result.get("images_json") or "[]")
    except Exception:
        all_images = []
    try:
        selected_images = json.loads(
            result.get("selected_images_json") or "[]"
        )
    except Exception:
        selected_images = []

    # Operator requested N Product images, not N downloaded files plus dozens
    # of unresolved remote placeholders. Keep the complete evidence inside
    # source_snapshot_json while Product image state stays bounded and usable.
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
        # Discovery identity stays authoritative even if a redirected page is
        # recognized by the generic extractor under a slightly different code.
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

    # Database.upsert_product() is intentionally a write boundary and does not
    # return the inserted/updated id for normal rows. Resolve the authoritative
    # identity after the upsert instead of guessing from the method return.
    downloaded_model_files = (
        _download_public_model_files(
            payload,
            local_dir,
            referer=payload["source_url"],
            same_domain_only=bool(same_domain_only),
        )
        if download_files
        else []
    )
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

    saved_files = [
        str(path)
        for path in result.get("downloaded_image_files") or []
        if str(path or "").strip()
    ]
    return {
        "product_id": product_id,
        "source_title": str(result.get("source_title") or ""),
        "images_found": len(ordered),
        "images_saved": min(len(saved_files), image_limit),
        "files_saved": len(downloaded_model_files),
        "acquisition_method": "qt42c-rich-page-extractor",
    }


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
) -> dict[str, Any]:
    """Headless adapter for the proven pre-Qt acquisition methods.

    The old Tk surface is not called. It used collect_classic_exact for
    classic_isolated/classic_exact/browser_dom/public_http, optionally enabled
    network capture, supported attached Chrome, and imported saved HTML. We
    preserve those semantics while persisting through the modern Catalog DB.
    """
    ensure_epic49_desktop_schema(db)
    ensure_modern_schema(db)
    ensure_incremental_schema(db)
    source_code = str(source_cfg.get("code") or "")
    method = str(collection_method or "classic_exact").strip().lower()
    aliases = {
        "classic_isolated": "classic_exact",
        "browser_dom": "classic_exact",
        "public_http": "classic_exact",
    }
    method = aliases.get(method, method)
    if method not in {"classic_exact", "network_capture", "chrome_attached", "saved_html"}:
        raise ValueError(f"روش Legacy ناشناخته است: {collection_method}")

    local_dir.mkdir(parents=True, exist_ok=True)
    if method == "saved_html":
        html_path = Path(str(saved_html_path or ""))
        if not html_path.is_file():
            raise ValueError("برای Saved HTML یک فایل HTML معتبر انتخاب کن.")
        result = import_saved_html(html_path, url, local_dir)
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
    parsed = parse_product(
        html,
        str(result.get("final_url") or url),
        str(result.get("title") or ""),
        list(result.get("dom_image_urls") or []),
    )
    images = _cap_product_images(parsed, image_limit)
    parsed["selected_images_json"] = json.dumps(images, ensure_ascii=False)
    parsed["selected_file_links_json"] = parsed.get("file_links_json") or "[]"
    downloaded_images = [
        str(value)
        for value in (result.get("downloaded_images") or [])
        if str(value or "").strip()
    ]
    if downloaded_images:
        _write_local_mapping(
            local_dir,
            list(result.get("dom_image_urls") or images),
            downloaded_images,
        )

    payload = {
        **_source_defaults(source_cfg, image_limit),
        **parsed,
        "source_code": source_code,
        "external_id": external_id,
        "source_url": str(result.get("final_url") or url),
        "local_dir": str(local_dir),
        "download_image_limit": image_limit,
        "source_snapshot_json": json.dumps(
            {"legacy_manifest": {k: v for k, v in dict(result).items() if k not in {"html_path"}}},
            ensure_ascii=False,
            default=str,
        ),
        "acquisition_method": f"qt46-legacy-{method}",
    }
    downloaded_model_files = (
        _download_public_model_files(
            payload,
            local_dir,
            referer=payload["source_url"],
            same_domain_only=bool(same_domain_only),
        )
        if download_files
        else []
    )
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
    return {
        "product_id": product_id,
        "source_title": str(parsed.get("source_title") or ""),
        "images_found": len(images),
        "images_saved": min(len(downloaded_images), image_limit),
        "files_saved": len(downloaded_model_files),
        "acquisition_method": f"qt46-legacy-{method}",
    }


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
    operator_mode = str(
        operator_mode or "search"
    ).strip().lower()
    if operator_mode not in {
        "automatic",
        "search",
        "category",
        "site_crawl",
        "listing",
    }:
        raise ValueError(
            "نوع دریافت گروهی نامعتبر است."
        )

    run_id = db.create_run(
        source_code,
        f"qt_{operator_mode}",
        (
            f"{strategy}-discovery+{collection_method}-product"
        ),
        requested,
    )
    discovered = collected = duplicates = failed = 0
    failures: list[str] = []

    try:
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
            }

        total = len(rows)
        for index, row in enumerate(rows, 1):
            if _stopped(should_stop):
                break

            external_id = str(row["external_id"] or row["id"])
            url = str(row["url"] or "")
            local_dir = (
                data_root()
                / "collected"
                / source_code
                / external_id
            )
            _emit(
                progress,
                24 + int((index - 1) / max(1, total) * 72),
                f"دریافت صفحه محصول {index}/{total} — {url}",
            )
            try:
                if collection_method == "rich":
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
                    )
                else:
                    result = await _collect_one_legacy(
                        db,
                        source_cfg,
                        external_id=external_id,
                        url=url,
                        image_limit=image_limit,
                        local_dir=local_dir,
                        collection_method=collection_method,
                        download_images=bool(download_images),
                        download_files=bool(download_files),
                        same_domain_only=bool(same_domain_only),
                    )
                db.mark_url(int(row["id"]), "collected")
                collected += 1
                _emit(
                    progress,
                    24 + int(index / max(1, total) * 72),
                    f"#{index}: {result['source_title'] or external_id} — "
                    f"{result['images_saved']}/{image_limit} عکس ذخیره شد",
                )
            except PermissionError as exc:
                db.mark_url(int(row["id"]), "failed", str(exc))
                failed += 1
                failures.append(f"{url}: {exc}")
                # A block/rate denial is not retried aggressively.
                break
            except Exception as exc:
                db.mark_url(int(row["id"]), "failed", str(exc))
                failed += 1
                failures.append(f"{url}: {type(exc).__name__}: {exc}")
                # Continue to the next independent Product; failed identities
                # remain visible/retriable through the queue.
                continue

            if index < total:
                await asyncio.sleep(0.8)

        stopped = _stopped(should_stop)
        status = "stopped" if stopped else ("completed" if collected or not failed else "failed")
        message = (
            f"Qt acquisition: collected={collected}, failed={failed}, "
            f"new={discovered}, duplicates={duplicates}"
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
        _emit(progress, 100, message)
        return {
            "run_id": run_id,
            "discovered": discovered,
            "collected": collected,
            "duplicates": duplicates,
            "failed": failed,
            "stopped": stopped,
            "failures": failures[:12],
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
    """Refetch source-owned Products while preserving operator decisions."""
    source_row = db.source(str(source_code or ""))
    if source_row is None:
        raise ValueError("Source انتخاب‌شده پیدا نشد.")
    source_cfg = _source_dict(source_row)
    rows = db.product_page(
        filter_name="all",
        source_code=source_code,
        sort_key="newest",
        limit=max(1, min(500, int(limit or 20))),
        offset=0,
    )
    changed = unchanged = failed = 0
    total = len(rows)
    for index, lite in enumerate(rows, 1):
        if _stopped(should_stop):
            break
        row = db.product(int(lite["id"]))
        if row is None:
            continue
        try:
            url = str(row["source_url"] or "")
            external_id = str(row["external_id"] or row["id"])
            _emit(
                progress,
                int((index - 1) / max(1, total) * 95),
                f"بروزرسانی {index}/{total} — {url}",
            )
            delay = await _browser_robots_gate(db, source_code, url)
            if delay > 0:
                await asyncio.sleep(min(30.0, delay))
            output = data_root() / "collected" / source_code / f"{external_id}_refresh_latest"
            result = await extract_direct_link(
                url,
                output,
                data_root() / "browser_profiles" / source_code,
                headed=False,
                download_images=bool(download_images),
                image_limit=normalize_image_limit(image_limit),
            )
            try:
                images = json.loads(result.get("images_json") or "[]")
            except Exception:
                images = []
            images = [str(value) for value in images[: normalize_image_limit(image_limit)]]
            fresh = {
                **_source_defaults(source_cfg, normalize_image_limit(image_limit)),
                **{k: v for k, v in dict(result).items() if k != "downloaded_image_files"},
                "source_code": source_code,
                "external_id": external_id,
                "source_url": str(result.get("source_url") or url),
                "local_dir": str(output),
                "images_json": json.dumps(images, ensure_ascii=False),
                "selected_images_json": json.dumps(images, ensure_ascii=False),
                "primary_image_url": images[0] if images else "",
                "last_refetched_at": utc_now(),
                "source_state": "active",
            }
            fresh["fingerprint"] = product_fingerprint(
                source_code,
                external_id,
                fresh["source_url"],
            )
            fresh["source_hash"] = source_payload_hash(fresh)
            fresh["needs_update"] = (
                1
                if should_mark_needs_update(row, fresh["source_hash"])
                else int(row["needs_update"] or 0)
            )
            fresh["content_status"] = (
                "stale"
                if fresh["needs_update"]
                else str(row["content_status"] or "pending")
            )
            diff = product_diff(dict(row), fresh)
            if not diff:
                unchanged += 1
                continue
            before = dict(row)
            merged = merge_refetch(row, fresh)
            allowed = set(row.keys()) - {"id", "created_at", "updated_at"}
            db.update_product(
                int(row["id"]),
                {key: value for key, value in merged.items() if key in allowed},
            )
            db.save_history(
                int(row["id"]),
                "source_refresh",
                before,
                dict(db.product(int(row["id"]))),
                diff_summary(diff),
            )
            changed += 1
        except Exception:
            failed += 1
            continue
    _emit(
        progress,
        100,
        f"بروزرسانی Source تمام شد — changed={changed}, unchanged={unchanged}, failed={failed}",
    )
    return {
        "source_code": source_code,
        "changed": changed,
        "unchanged": unchanged,
        "failed": failed,
        "stopped": _stopped(should_stop),
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
) -> dict[str, Any]:
    source_row = db.source(source_code)
    if source_row is None:
        raise ValueError("Source انتخاب‌شده پیدا نشد.")
    source_cfg = _source_dict(source_row)
    image_limit = normalize_image_limit(image_limit)
    external_id, url = _product_identity(source_cfg, product_url)
    if terminal_identity_state(db, source_code, external_id, url):
        existing = db.conn.execute(
            """
            SELECT id FROM products
            WHERE source_code=?
              AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
            ORDER BY id DESC LIMIT 1
            """,
            (source_code, external_id, url),
        ).fetchone()
        return {
            "product_id": int(existing["id"]) if existing else 0,
            "already_collected": True,
        }

    _emit(progress, 5, "دریافت مستقیم صفحه محصول…")
    local_dir = data_root() / "collected" / source_code / external_id
    method = str(collection_method or "rich").strip().lower()
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


async def recover_product_images_async(
    db,
    product_id: int,
    *,
    image_limit: int = 10,
    progress: Progress = None,
) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError("محصول پیدا نشد.")
    data = dict(row)
    source_cfg = _source_dict(db.source(str(data.get("source_code") or "")))
    if not source_cfg:
        raise RuntimeError("Source محصول پیدا نشد.")
    source_url = str(data.get("source_url") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        raise RuntimeError("لینک منبع محصول معتبر نیست.")

    external_id = str(data.get("external_id") or "").strip()
    if not external_id:
        external_id, _ = _product_identity(source_cfg, source_url)
    local_dir = Path(str(data.get("local_dir") or "") or (
        data_root() / "collected" / str(data.get("source_code") or "source") / external_id
    ))
    _emit(progress, 5, "بازیابی تصاویر باکیفیت از صفحه اصلی محصول…")
    result = await _collect_one(
        db,
        source_cfg,
        external_id=external_id,
        url=source_url,
        image_limit=normalize_image_limit(image_limit),
        local_dir=local_dir,
    )
    _emit(progress, 100, f"{result['images_saved']} تصویر ذخیره شد.")
    return result


def recover_product_images(db, product_id: int, **kwargs) -> dict[str, Any]:
    return asyncio.run(
        recover_product_images_async(
            db,
            int(product_id),
            **kwargs,
        )
    )
