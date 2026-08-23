from __future__ import annotations

from urllib.parse import urljoin

from . import phase49_3i15_bulk_discovery_images as bulk
from . import phase49_3i16_resilient_acquisition as recovery
from .db import normalize_url
from .phase49_3i_discovery_review import candidate_rows, candidates_from_dom_rows


_ACTIVE_DB = None


async def discover_attached_locator_safe(
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    scroll_rounds: int = 8,
    **_kwargs,
) -> list[dict]:
    if not await recovery._cdp_available():
        raise RuntimeError("Chrome 9222 is not available")

    import re
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(
            "http://127.0.0.1:9222",
            timeout=5000,
        )
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        page = await context.new_page()
        try:
            response = await page.goto(
                listing_url,
                wait_until="domcontentloaded",
                timeout=35_000,
            )
            if response and response.status in {403, 429}:
                raise RuntimeError(f"Discovery page returned HTTP {response.status}")
            await page.wait_for_timeout(1400)
            await recovery._scroll_without_embedded_js(
                page,
                min(max(3, int(scroll_rounds)), 16),
            )
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
                    href = await anchor.get_attribute("href", timeout=900)
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
                    text = (await anchor.inner_text(timeout=800) or "").strip()
                except Exception:
                    text = ""
                image = ""
                try:
                    image = await recovery._image_from_locator(
                        anchor.locator("img").first,
                        page.url,
                    )
                except Exception:
                    image = ""
                if not image:
                    try:
                        image = await recovery._image_from_locator(
                            anchor.locator("xpath=..").locator("img").first,
                            page.url,
                        )
                    except Exception:
                        image = ""
                rows.append({"href": matched, "text": text, "image": image})
            return candidates_from_dom_rows(
                rows,
                model_pattern,
                page.url or listing_url,
                source_code,
                requested,
            )
        finally:
            try:
                await page.close()
            except Exception:
                pass


def cached_candidates(
    listing_url: str,
    *,
    source_code: str,
    requested: int,
) -> list[dict]:
    if _ACTIVE_DB is None:
        return []
    try:
        wanted = normalize_url(listing_url)
    except Exception:
        wanted = str(listing_url or "").strip()
    output: list[dict] = []
    for row in candidate_rows(_ACTIVE_DB, limit=1200):
        if str(row["source_code"] or "") != str(source_code or ""):
            continue
        discovered_from = str(row["discovered_from"] or "")
        try:
            discovered_norm = normalize_url(discovered_from)
        except Exception:
            discovered_norm = discovered_from
        if wanted and discovered_norm != wanted:
            continue
        output.append(
            {
                "source_code": str(row["source_code"] or ""),
                "external_id": str(row["external_id"] or ""),
                "source_url": str(row["source_url"] or ""),
                "source_title": str(row["source_title"] or ""),
                "thumbnail_url": str(row["thumbnail_url"] or ""),
                "discovered_from": discovered_from or listing_url,
            }
        )
        if len(output) >= max(1, int(requested)):
            break
    return output


async def discover_preview_candidates_hardened(*args, **kwargs) -> list[dict]:
    listing_url = str(args[0] if args else kwargs.get("listing_url") or "")
    source_code = str(kwargs.get("source_code") or "")
    requested = int(kwargs.get("requested") or 1)
    attempts: list[str] = []
    methods = (
        ("locator-safe", recovery.discover_locator_safe),
        ("http-html-links", recovery.discover_http_html_fallback),
        ("attached-chrome-listing", discover_attached_locator_safe),
    )
    for method, func in methods:
        try:
            result = await func(*args, **kwargs)
            if result:
                recovery._trace(
                    listing_url,
                    "discovery",
                    method,
                    True,
                    found=len(result),
                )
                return result
            detail = "no candidates"
            attempts.append(f"{method}: {detail}")
            recovery._trace(listing_url, "discovery", method, False, detail)
        except Exception as exc:
            detail = f"{type(exc).__name__}: {exc}"
            attempts.append(f"{method}: {detail}")
            recovery._trace(listing_url, "discovery", method, False, detail)

    cached = cached_candidates(
        listing_url,
        source_code=source_code,
        requested=requested,
    )
    if cached:
        recovery._trace(
            listing_url,
            "discovery",
            "cached-candidate-db",
            True,
            "reused previously discovered candidates after live methods failed",
            found=len(cached),
        )
        return cached

    recovery._trace(
        listing_url,
        "discovery",
        "cached-candidate-db",
        False,
        "no matching previously discovered candidates",
    )
    raise RuntimeError(
        "All live discovery methods failed and no cached candidates are available | "
        + " | ".join(attempts)
    )


def install(app_class) -> None:
    global _ACTIVE_DB

    if getattr(app_class, "_phase49_3i16_review_hardening_installed", False):
        return

    original_start = app_class.start_bulk_page_discovery

    def start_bulk_page_discovery(self, *args, **kwargs):
        global _ACTIVE_DB
        _ACTIVE_DB = self.db
        return original_start(self, *args, **kwargs)

    app_class.start_bulk_page_discovery = start_bulk_page_discovery
    app_class.start_exact_page_discovery = start_bulk_page_discovery

    recovery.DISCOVERY_METHODS = (
        "locator-safe",
        "http-html-links",
        "attached-chrome-listing",
        "cached-candidate-db",
    )
    recovery.discover_preview_candidates_resilient = discover_preview_candidates_hardened
    bulk.discover_preview_candidates = discover_preview_candidates_hardened
    app_class._phase49_3i16_review_hardening_installed = True
