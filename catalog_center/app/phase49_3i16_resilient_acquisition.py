from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

from . import phase49_3i15_bulk_discovery_images as bulk
from .classic_methods import (
    _download_context_images,
    discover_classic,
    launch_fresh_browser,
    makerworld_model_id,
)
from .crawler import download_public_file, extract_links, parse_product, public_http
from .phase49_3h_image_limits import normalize_image_limit
from .phase49_3i_discovery_review import candidates_from_dom_rows


PHASE = "49.3I.16"
DISCOVERY_METHODS = (
    "locator-safe",
    "classic-links",
    "http-html-links",
)
IMAGE_METHODS = (
    "locator-safe-fresh",
    "http-html-parse",
    "mature-classic-dom",
    "attached-chrome-locator",
    "listing-thumbnail",
)

_TRACE: dict[str, list[dict[str, Any]]] = {}


def _trace(key: str, stage: str, method: str, ok: bool, detail: str = "", *, found: int = 0, saved: int = 0) -> None:
    key = str(key or "").strip()
    if not key:
        return
    rows = _TRACE.setdefault(key, [])
    rows.append(
        {
            "stage": stage,
            "method": method,
            "ok": bool(ok),
            "detail": str(detail or "")[:1200],
            "found": int(found or 0),
            "saved": int(saved or 0),
        }
    )
    if len(rows) > 30:
        del rows[:-30]


def trace_for(key: str) -> list[dict[str, Any]]:
    return list(_TRACE.get(str(key or "").strip(), []))


def _best_srcset(value: str) -> str:
    best: tuple[float, str] | None = None
    for chunk in str(value or "").split(","):
        bits = chunk.strip().split()
        if not bits:
            continue
        score = 1.0
        if len(bits) > 1:
            token = bits[-1]
            try:
                if token.endswith("w"):
                    score = float(token[:-1])
                elif token.endswith("x"):
                    score = float(token[:-1]) * 1000.0
            except Exception:
                score = 1.0
        if best is None or score > best[0]:
            best = (score, bits[0])
    return best[1] if best else ""


def _normalize_image_url(base_url: str, value: str) -> str:
    value = str(value or "").strip()
    if not value or value.startswith(("data:", "blob:")):
        return ""
    full = urljoin(base_url, value)
    if not full.startswith(("http://", "https://")):
        return ""
    low = full.lower()
    bad = (
        "logo",
        "avatar",
        "favicon",
        "emoji",
        "sprite",
        "placeholder",
        "loading",
        "profile",
        "badge",
    )
    if any(token in low for token in bad):
        return ""
    return full


async def _image_from_locator(locator, base_url: str) -> str:
    try:
        if await locator.count() < 1:
            return ""
    except Exception:
        return ""
    for attr in ("srcset", "data-srcset"):
        try:
            value = await locator.get_attribute(attr, timeout=1200)
        except Exception:
            value = ""
        picked = _best_srcset(value or "")
        normalized = _normalize_image_url(base_url, picked)
        if normalized:
            return normalized
    for attr in ("src", "data-src", "data-original", "data-lazy-src", "data-image"):
        try:
            value = await locator.get_attribute(attr, timeout=1200)
        except Exception:
            value = ""
        normalized = _normalize_image_url(base_url, value or "")
        if normalized:
            return normalized
    return ""


async def locator_safe_image_urls(page, limit: int) -> list[str]:
    requested = normalize_image_limit(limit)
    images = page.locator("img")
    try:
        count = min(await images.count(), 1500)
    except Exception:
        count = 0
    output: list[str] = []
    seen: set[str] = set()
    for index in range(count):
        if len(output) >= requested:
            break
        value = await _image_from_locator(images.nth(index), page.url)
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


async def _scroll_without_embedded_js(page, rounds: int) -> None:
    for _ in range(max(0, int(rounds))):
        try:
            await page.mouse.wheel(0, 1600)
        except Exception:
            try:
                await page.keyboard.press("End")
            except Exception:
                return
        await page.wait_for_timeout(450)


async def discover_locator_safe(
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    scroll_rounds: int = 8,
    headed: bool = False,
) -> list[dict]:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser, _label = await launch_fresh_browser(playwright, headed=headed)
        try:
            context = await browser.new_context(
                locale="en-US",
                viewport={"width": 1440, "height": 1100},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
                ),
            )
            page = await context.new_page()
            response = await page.goto(listing_url, wait_until="domcontentloaded", timeout=45_000)
            if response and response.status in {403, 429}:
                raise RuntimeError(f"Discovery page returned HTTP {response.status}")
            await page.wait_for_timeout(2200)
            await _scroll_without_embedded_js(page, min(max(3, int(scroll_rounds)), 20))
            regex = re.compile(model_pattern, re.I)
            anchors = page.locator("a[href]")
            count = min(await anchors.count(), 3000)
            rows: list[dict[str, str]] = []
            seen: set[str] = set()
            for index in range(count):
                if len(rows) >= max(1, int(requested)):
                    break
                anchor = anchors.nth(index)
                try:
                    href = await anchor.get_attribute("href", timeout=1000)
                except Exception:
                    continue
                full = urljoin(page.url or listing_url, str(href or ""))
                match = regex.search(full)
                if not match:
                    continue
                matched = match.group(0)
                identity = matched.split("#", 1)[0]
                if identity in seen:
                    continue
                seen.add(identity)
                try:
                    text = (await anchor.inner_text(timeout=900) or "").strip()
                except Exception:
                    text = ""
                image = ""
                try:
                    image = await _image_from_locator(anchor.locator("img").first, page.url)
                except Exception:
                    image = ""
                if not image:
                    try:
                        image = await _image_from_locator(anchor.locator("xpath=..").locator("img").first, page.url)
                    except Exception:
                        image = ""
                rows.append({"href": matched, "text": text, "image": image})
            return candidates_from_dom_rows(rows, model_pattern, page.url or listing_url, source_code, requested)
        finally:
            await browser.close()


async def discover_classic_links_fallback(
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    scroll_rounds: int = 8,
    headed: bool = False,
) -> list[dict]:
    result = await discover_classic(
        listing_url,
        model_pattern=model_pattern,
        scroll_rounds=min(max(3, int(scroll_rounds)), 16),
        headed=headed,
    )
    rows = [
        {"href": url, "text": f"Model {external_id}", "image": ""}
        for external_id, url in (result.get("links") or [])[: max(1, int(requested))]
    ]
    return candidates_from_dom_rows(rows, model_pattern, result.get("final_url") or listing_url, source_code, requested)


async def discover_http_html_fallback(
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    **_kwargs,
) -> list[dict]:
    html = await asyncio.to_thread(public_http, listing_url, 20)
    rows = [
        {"href": url, "text": f"Model {external_id}", "image": ""}
        for external_id, url in extract_links(html, model_pattern)[: max(1, int(requested))]
    ]
    return candidates_from_dom_rows(rows, model_pattern, listing_url, source_code, requested)


async def discover_preview_candidates_resilient(*args, **kwargs) -> list[dict]:
    listing_url = str(args[0] if args else kwargs.get("listing_url") or "")
    attempts: list[str] = []
    methods = (
        ("locator-safe", discover_locator_safe),
        ("classic-links", discover_classic_links_fallback),
        ("http-html-links", discover_http_html_fallback),
    )
    for method, func in methods:
        try:
            result = await func(*args, **kwargs)
            if result:
                _trace(listing_url, "discovery", method, True, found=len(result))
                return result
            detail = "no candidates"
            attempts.append(f"{method}: {detail}")
            _trace(listing_url, "discovery", method, False, detail)
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            attempts.append(f"{method}: {detail}")
            _trace(listing_url, "discovery", method, False, detail)
    raise RuntimeError("All discovery methods failed | " + " | ".join(attempts))


async def collect_locator_safe_fresh(
    url: str,
    output_dir: Path,
    *,
    image_limit: int,
    referer: str = "",
    headed: bool = False,
) -> dict:
    from playwright.async_api import async_playwright

    requested = normalize_image_limit(image_limit)
    output_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser, browser_label = await launch_fresh_browser(playwright, headed=headed)
        try:
            context = await browser.new_context(
                locale="en-US",
                viewport={"width": 1440, "height": 1100},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
                ),
            )
            page = await context.new_page()
            if referer:
                try:
                    await page.set_extra_http_headers({"Referer": referer})
                except Exception:
                    pass
            response = await page.goto(url, wait_until="domcontentloaded", timeout=35_000)
            status = response.status if response else None
            if status in {403, 429}:
                raise PermissionError(f"HTTP {status}")
            await page.wait_for_timeout(1800)
            await _scroll_without_embedded_js(page, 4)
            image_urls = await locator_safe_image_urls(page, requested)
            downloaded = await _download_context_images(
                context,
                image_urls,
                output_dir,
                page.url or url,
                limit=requested,
            )
            return {
                "browser": browser_label,
                "http_status": status,
                "final_url": page.url or url,
                "image_urls": image_urls,
                "downloaded_images": downloaded[:requested],
                "acquisition_method": "locator-safe-fresh",
            }
        finally:
            await browser.close()


def _suffix_for_image(url: str) -> str:
    suffix = Path(urlsplit(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"} else ".jpg"


async def collect_http_html_parse(
    url: str,
    output_dir: Path,
    *,
    image_limit: int,
    referer: str = "",
    **_kwargs,
) -> dict:
    requested = normalize_image_limit(image_limit)
    html = await asyncio.to_thread(public_http, url, 20)
    parsed = parse_product(html, url, "", [])
    try:
        image_urls = json.loads(parsed.get("images_json") or "[]")
    except Exception:
        image_urls = []
    image_urls = [str(item).strip() for item in image_urls if str(item).strip()][:requested]
    downloaded: list[str] = []
    image_dir = Path(output_dir) / "images"
    for index, image_url in enumerate(image_urls, start=1):
        target = image_dir / f"fallback_http_{index:02d}{_suffix_for_image(image_url)}"
        try:
            saved = await asyncio.to_thread(
                download_public_file,
                image_url,
                target,
                timeout=25,
                max_bytes=25_000_000,
                referer=referer or url,
            )
            downloaded.append(str(saved))
        except Exception:
            continue
    return {
        "browser": "public-http-html",
        "http_status": 200 if html else None,
        "final_url": url,
        "image_urls": image_urls,
        "downloaded_images": downloaded,
        "acquisition_method": "http-html-parse",
    }


async def _cdp_available() -> bool:
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection("127.0.0.1", 9222), timeout=0.8)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return True
    except Exception:
        return False


async def collect_attached_locator(
    url: str,
    output_dir: Path,
    *,
    image_limit: int,
    referer: str = "",
    **_kwargs,
) -> dict:
    if not await _cdp_available():
        raise RuntimeError("Chrome 9222 is not available")
    from playwright.async_api import async_playwright

    requested = normalize_image_limit(image_limit)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=5000)
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        page = await context.new_page()
        try:
            if referer:
                try:
                    await page.set_extra_http_headers({"Referer": referer})
                except Exception:
                    pass
            response = await page.goto(url, wait_until="domcontentloaded", timeout=35_000)
            status = response.status if response else None
            if status in {403, 429}:
                raise PermissionError(f"HTTP {status}")
            await page.wait_for_timeout(1600)
            await _scroll_without_embedded_js(page, 4)
            image_urls = await locator_safe_image_urls(page, requested)
            downloaded = await _download_context_images(
                context,
                image_urls,
                output_dir,
                page.url or url,
                limit=requested,
            )
            return {
                "browser": "attached-chrome-9222-locator",
                "http_status": status,
                "final_url": page.url or url,
                "image_urls": image_urls,
                "downloaded_images": downloaded[:requested],
                "acquisition_method": "attached-chrome-locator",
            }
        finally:
            try:
                await page.close()
            except Exception:
                pass


async def collect_listing_thumbnail(
    product_url: str,
    output_dir: Path,
    *,
    image_limit: int,
    referer: str = "",
    **_kwargs,
) -> dict:
    if not referer or not referer.startswith(("http://", "https://")):
        raise RuntimeError("Listing referer is unavailable")
    from playwright.async_api import async_playwright

    target_model = makerworld_model_id(product_url)
    requested = normalize_image_limit(image_limit)
    async with async_playwright() as playwright:
        browser, label = await launch_fresh_browser(playwright, headed=False)
        try:
            context = await browser.new_context(locale="en-US", viewport={"width": 1440, "height": 1100})
            page = await context.new_page()
            response = await page.goto(referer, wait_until="domcontentloaded", timeout=35_000)
            if response and response.status in {403, 429}:
                raise PermissionError(f"HTTP {response.status}")
            await page.wait_for_timeout(1500)
            await _scroll_without_embedded_js(page, 3)
            anchors = page.locator("a[href]")
            count = min(await anchors.count(), 2500)
            image_url = ""
            for index in range(count):
                anchor = anchors.nth(index)
                try:
                    href = urljoin(page.url, str(await anchor.get_attribute("href", timeout=800) or ""))
                except Exception:
                    continue
                if target_model:
                    if makerworld_model_id(href) != target_model:
                        continue
                elif product_url.split("#", 1)[0] not in href:
                    continue
                image_url = await _image_from_locator(anchor.locator("img").first, page.url)
                if not image_url:
                    try:
                        image_url = await _image_from_locator(anchor.locator("xpath=..").locator("img").first, page.url)
                    except Exception:
                        image_url = ""
                if image_url:
                    break
            if not image_url:
                raise RuntimeError("No listing thumbnail matched the product")
            downloaded = await _download_context_images(
                context,
                [image_url],
                output_dir,
                referer,
                limit=1,
            )
            return {
                "browser": label,
                "http_status": response.status if response else None,
                "final_url": product_url,
                "image_urls": [image_url] if downloaded else [],
                "downloaded_images": downloaded[:1],
                "acquisition_method": "listing-thumbnail",
                "requested_images": requested,
            }
        finally:
            await browser.close()


async def collect_candidate_images_resilient(
    url: str,
    output_dir: Path,
    *,
    image_limit: int,
    referer: str = "",
    headed: bool = False,
) -> dict:
    original_collect = getattr(collect_candidate_images_resilient, "_original_collect", None)
    methods = [
        ("locator-safe-fresh", collect_locator_safe_fresh),
        ("http-html-parse", collect_http_html_parse),
    ]
    if original_collect is not None:
        methods.append(("mature-classic-dom", original_collect))
    methods.extend(
        [
            ("attached-chrome-locator", collect_attached_locator),
            ("listing-thumbnail", collect_listing_thumbnail),
        ]
    )
    errors: list[str] = []
    requested = normalize_image_limit(image_limit)
    for method, func in methods:
        try:
            result = await func(
                url,
                output_dir,
                image_limit=requested,
                referer=referer,
                headed=headed,
            )
            found = len(result.get("image_urls") or [])
            saved = len(result.get("downloaded_images") or [])
            if saved > 0:
                result = dict(result)
                result["acquisition_method"] = method
                _trace(url, "images", method, True, found=found, saved=saved)
                return result
            detail = f"no staged local images (found={found})"
            errors.append(f"{method}: {detail}")
            _trace(url, "images", method, False, detail, found=found, saved=saved)
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            errors.append(f"{method}: {detail}")
            _trace(url, "images", method, False, detail)
    raise RuntimeError("All image acquisition methods failed | " + " | ".join(errors))


def install() -> None:
    if getattr(bulk, "_phase49_3i16_resilient_acquisition_installed", False):
        return

    original_collect = bulk.collect_candidate_images
    original_write_manifest = bulk.write_candidate_manifest
    collect_candidate_images_resilient._original_collect = original_collect

    def write_candidate_manifest(*args, **kwargs):
        path = original_write_manifest(*args, **kwargs)
        try:
            candidate = args[1] if len(args) > 1 else kwargs.get("candidate") or {}
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            source_url = str(candidate.get("source_url") or "")
            discovered_from = str(candidate.get("discovered_from") or "")
            payload["acquisition_trace"] = trace_for(source_url)
            payload["discovery_trace"] = trace_for(discovered_from)
            successes = [row for row in payload["acquisition_trace"] if row.get("ok")]
            payload["acquisition_method"] = successes[-1]["method"] if successes else ""
            discovery_successes = [row for row in payload["discovery_trace"] if row.get("ok")]
            payload["discovery_method"] = discovery_successes[-1]["method"] if discovery_successes else ""
            Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        return path

    bulk.discover_preview_candidates = discover_preview_candidates_resilient
    bulk.collect_candidate_images = collect_candidate_images_resilient
    bulk.write_candidate_manifest = write_candidate_manifest
    bulk._phase49_3i16_resilient_acquisition_installed = True
