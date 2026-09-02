from __future__ import annotations

from .classic_methods import launch_fresh_browser
from .phase49_3i_discovery_review import candidates_from_dom_rows


# IMPORTANT: this is a raw Python string. The JavaScript source must receive the
# two characters backslash+n inside its quoted string, not a literal newline.
# A literal newline inside a single-quoted JavaScript string caused
# Locator.evaluate_all: SyntaxError: Invalid or unexpected token on Windows QA.
PREVIEW_CARD_EVAL_JS = r"""els => els.map(a => {
    const host = a.closest('article, li, [class*="card"], [class*="model"], [class*="item"]') || a.parentElement || a;
    const img = (host && host.querySelector('img')) || a.querySelector('img');
    const source = host ? host.querySelector('picture source') : null;
    const styled = host ? host.querySelector('[style*="background-image"]') : null;
    return {
        href: a.href || '',
        text: ((a.innerText || '') + '\\n' + ((host && host.innerText) || '')).trim().slice(0, 900),
        image: img ? (img.currentSrc || '') : '',
        src: img ? (img.getAttribute('src') || '') : '',
        data_src: img ? (img.getAttribute('data-src') || '') : '',
        data_original: img ? (img.getAttribute('data-original') || '') : '',
        data_lazy_src: img ? (img.getAttribute('data-lazy-src') || '') : '',
        srcset: img ? (img.getAttribute('srcset') || '') : '',
        source_srcset: source ? (source.getAttribute('srcset') || '') : '',
        background: styled ? (styled.style.backgroundImage || '') : ''
    };
})"""


async def discover_preview_candidates_safe(
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    scroll_rounds: int = 8,
    headed: bool = False,
) -> list[dict]:
    """Collect lightweight listing cards only; never open product pages."""
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser, _browser_label = await launch_fresh_browser(playwright, headed=headed)
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
            response = await page.goto(
                listing_url,
                wait_until="domcontentloaded",
                timeout=90_000,
            )
            if response and response.status in {403, 429}:
                raise RuntimeError(f"Discovery page returned HTTP {response.status}")

            await page.wait_for_timeout(3500)
            previous_height = 0
            for _ in range(max(0, int(scroll_rounds))):
                height = await page.evaluate("() => document.documentElement.scrollHeight")
                await page.evaluate(
                    "() => window.scrollTo(0, document.documentElement.scrollHeight)"
                )
                await page.wait_for_timeout(1200)
                if height == previous_height:
                    break
                previous_height = height

            rows = await page.locator("a[href]").evaluate_all(PREVIEW_CARD_EVAL_JS)
            return candidates_from_dom_rows(
                rows,
                model_pattern,
                page.url or listing_url,
                source_code,
                requested,
            )
        finally:
            await browser.close()


def install() -> None:
    """Replace only the broken Stage-1 Preview browser expression.

    Mature direct-product/full-fetch code is intentionally untouched. The
    existing Phase49.3I review worker resolves its global function at runtime,
    so swapping this single boundary preserves Preview -> Approve -> Full Fetch.
    """
    from . import phase49_3i_discovery_review as discovery_review

    if getattr(discovery_review, "_phase49_3i_preview_recovery_installed", False):
        return
    discovery_review.discover_preview_candidates = discover_preview_candidates_safe
    discovery_review._phase49_3i_preview_recovery_installed = True
