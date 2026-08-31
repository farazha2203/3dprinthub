from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from app.classic_methods import discover_classic
from app.db import normalize_url
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
)
from app.phase49_3i45_incremental_discovery_intelligence import (
    discover_sitemap_candidates_incremental,
    ensure_schema as ensure_incremental_schema,
)
from app.phase49_3i_discovery_review import _source_defaults
from app.runtime_paths import data_root


Progress = Callable[[int, str], None] | None
ShouldStop = Callable[[], bool] | None


def _emit(progress: Progress, value: int, message: str) -> None:
    if callable(progress):
        progress(max(0, min(100, int(value))), str(message))


def _stopped(should_stop: ShouldStop) -> bool:
    return bool(callable(should_stop) and should_stop())


def _source_dict(row) -> dict[str, Any]:
    return dict(row) if row is not None else {}


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
                str(candidate.get("discovered_from") or listing_url),
            ):
                new_count += 1
            else:
                duplicate_count += 1

        if len(
            db.pending_urls(
                source_code,
                requested,
                include_failed=False,
            )
        ) >= requested:
            return {
                "new": new_count,
                "duplicates": duplicate_count,
            }

    # Classic fallback / explicit legacy mode.
    # 3I.38 remembers the prior listing depth so each rerun keeps moving
    # forward instead of restarting from the same first screen.
    stagnant = 0
    for round_no in range(1, 9):
        if _stopped(should_stop):
            break
        pending = len(
            db.pending_urls(
                source_code,
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


async def _collect_one(
    db,
    source_cfg: dict[str, Any],
    *,
    external_id: str,
    url: str,
    image_limit: int,
    local_dir: Path,
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

    result = await extract_direct_link(
        url,
        local_dir,
        profile_dir,
        headed=False,
        download_images=True,
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
        "acquisition_method": "qt42c-rich-page-extractor",
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
    progress: Progress = None,
    should_stop: ShouldStop = None,
) -> dict[str, Any]:
    requested = max(1, min(100, int(requested or 1)))
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

    run_id = db.create_run(
        source_code,
        "qt_listing",
        (
            "hybrid-http-sitemap-browser+rich-product"
            if strategy == "hybrid"
            else "classic-search-link+rich-product"
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

        rows = db.pending_urls(
            source_code,
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
                result = await _collect_one(
                    db,
                    source_cfg,
                    external_id=external_id,
                    url=url,
                    image_limit=image_limit,
                    local_dir=local_dir,
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


def run_batch(db, **kwargs) -> dict[str, Any]:
    return asyncio.run(run_batch_async(db, **kwargs))


async def run_single_async(
    db,
    *,
    source_code: str,
    product_url: str,
    image_limit: int = 5,
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
    result = await _collect_one(
        db,
        source_cfg,
        external_id=external_id,
        url=url,
        image_limit=image_limit,
        local_dir=local_dir,
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
