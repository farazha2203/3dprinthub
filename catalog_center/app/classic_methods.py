from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any


def browser_candidates() -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = [
        {"label": "playwright-chromium"},
        {"label": "chrome-channel", "channel": "chrome"},
        {"label": "msedge-channel", "channel": "msedge"},
    ]

    for base in (
        os.environ.get("PROGRAMFILES"),
        os.environ.get("PROGRAMFILES(X86)"),
        os.environ.get("LOCALAPPDATA"),
    ):
        if not base:
            continue
        for label, executable in (
            (
                "chrome-executable",
                Path(base)
                / "Google"
                / "Chrome"
                / "Application"
                / "chrome.exe",
            ),
            (
                "edge-executable",
                Path(base)
                / "Microsoft"
                / "Edge"
                / "Application"
                / "msedge.exe",
            ),
        ):
            if executable.is_file():
                candidates.append(
                    {
                        "label": label,
                        "executable_path": str(executable),
                    }
                )
    return candidates


async def launch_fresh_browser(playwright, *, headed: bool = False):
    errors: list[str] = []

    for candidate in browser_candidates():
        kwargs: dict[str, Any] = {"headless": not headed}
        if candidate.get("channel"):
            kwargs["channel"] = candidate["channel"]
        if candidate.get("executable_path"):
            kwargs["executable_path"] = candidate["executable_path"]

        try:
            browser = await playwright.chromium.launch(**kwargs)
            return browser, candidate["label"]
        except Exception as error:
            errors.append(
                f"{candidate['label']}: "
                f"{type(error).__name__}: {error}"
            )

    raise RuntimeError(
        "No Chromium/Chrome/Edge browser could be launched. "
        + " | ".join(errors)
    )


def makerworld_model_id(url: str) -> str:
    match = re.search(
        r"/(?:[a-z]{2}/)?models/(\d+)",
        url,
        re.IGNORECASE,
    )
    return match.group(1) if match else ""


async def discover_classic(
    listing_url: str,
    *,
    model_pattern: str,
    scroll_rounds: int = 8,
    headed: bool = False,
) -> dict:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser, browser_label = await launch_fresh_browser(
            playwright,
            headed=headed,
        )
        context = await browser.new_context(
            locale="en-US",
            viewport={"width": 1440, "height": 1100},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        response = await page.goto(
            listing_url,
            wait_until="domcontentloaded",
            timeout=90_000,
        )
        await page.wait_for_timeout(5000)

        previous_height = 0
        for _ in range(max(0, scroll_rounds)):
            height = await page.evaluate(
                "() => document.documentElement.scrollHeight"
            )
            await page.evaluate(
                "() => window.scrollTo(0, document.documentElement.scrollHeight)"
            )
            await page.wait_for_timeout(1800)
            if height == previous_height:
                break
            previous_height = height

        hrefs = await page.locator("a[href]").evaluate_all(
            "(els) => els.map((el) => el.href).filter(Boolean)"
        )

        regex = re.compile(model_pattern, re.I)
        links: list[tuple[str, str]] = []
        seen: set[str] = set()

        for href in hrefs:
            if not isinstance(href, str):
                continue
            match = regex.search(href)
            if not match:
                continue
            original_url = match.group(0)
            external_id = (
                match.groupdict().get("external_id")
                or makerworld_model_id(original_url)
                or hashlib.sha1(original_url.encode("utf-8")).hexdigest()[:16]
            )
            identity = f"{external_id}:{original_url.split('#', 1)[0]}"
            if identity in seen:
                continue
            seen.add(identity)
            links.append((external_id, original_url))

        result = {
            "browser": browser_label,
            "http_status": response.status if response else None,
            "final_url": page.url,
            "title": await page.title(),
            "links": links,
        }
        await browser.close()
        return result


def _image_suffix(url: str, content_type: str = "") -> str:
    content_type=(content_type or "").split(";",1)[0].lower()
    mapping={
        "image/jpeg":".jpg", "image/png":".png", "image/webp":".webp",
        "image/gif":".gif", "image/avif":".avif",
    }
    if content_type in mapping:
        return mapping[content_type]
    suffix=Path(__import__("urllib.parse").parse.urlsplit(url).path).suffix.lower()
    return suffix if suffix in {".jpg",".jpeg",".png",".webp",".gif",".avif"} else ".jpg"


async def _dom_image_urls(page) -> list[str]:
    """Return likely product/gallery images from the live DOM, not screenshots."""
    try:
        rows=await page.locator("img").evaluate_all(
            """els => els.map(el => {
                const r=el.getBoundingClientRect();
                return {
                    currentSrc: el.currentSrc || '', src: el.src || '', srcset: el.srcset || '',
                    dataSrc: el.getAttribute('data-src') || el.getAttribute('data-original') || el.getAttribute('data-lazy-src') || '',
                    alt: el.alt || '', nw: el.naturalWidth || 0, nh: el.naturalHeight || 0,
                    w: Math.round(r.width || 0), h: Math.round(r.height || 0)
                };
            })"""
        )
    except Exception:
        rows=[]
    bad=("logo","avatar","icon","emoji","favicon","sprite","placeholder","loading","badge","social","profile","banner")
    output=[]; seen=set()
    for row in rows:
        if not isinstance(row,dict):continue
        candidates=[]
        srcset=row.get("srcset") or ""
        if srcset:
            parts=[]
            for chunk in srcset.split(","):
                bits=chunk.strip().split()
                if not bits:continue
                score=1
                if len(bits)>1:
                    try:
                        score=float(bits[1][:-1])*(1000 if bits[1].endswith("x") else 1)
                    except Exception:pass
                parts.append((score,bits[0]))
            if parts:candidates.append(max(parts,key=lambda x:x[0])[1])
        candidates.extend([row.get("currentSrc"),row.get("dataSrc"),row.get("src")])
        width=max(int(row.get("nw") or 0),int(row.get("w") or 0))
        height=max(int(row.get("nh") or 0),int(row.get("h") or 0))
        alt=str(row.get("alt") or "").lower()
        for value in candidates:
            if not isinstance(value,str) or not value.startswith(("http://","https://")):continue
            lower=value.lower()
            if value in seen or any(token in lower or token in alt for token in bad):continue
            if width and height and (width<160 or height<160):continue
            if lower.split("?",1)[0].endswith(".svg"):continue
            seen.add(value); output.append(value)
    return output[:100]


async def _download_context_images(context, urls: list[str], output_dir: Path, referer: str, limit: int = 60) -> list[str]:
    image_dir=output_dir/"images"
    saved=[]
    for idx,url in enumerate(urls[:limit],start=1):
        try:
            response=await context.request.get(url,headers={"Referer":referer},timeout=30_000)
            if not response.ok:
                continue
            body=await response.body()
            if not body or len(body)>20_000_000:
                continue
            content_type=response.headers.get("content-type","")
            if not content_type.lower().startswith("image/"):
                continue
            image_dir.mkdir(parents=True,exist_ok=True)
            target=image_dir/f"{idx:02d}{_image_suffix(url,content_type)}"
            target.write_bytes(body)
            saved.append(str(target))
        except Exception:
            continue
    return saved


async def collect_classic_exact(
    url: str,
    output_dir: Path,
    *,
    headed: bool = False,
    capture_network: bool = False,
    download_images: bool = False,
) -> dict:
    from playwright.async_api import async_playwright

    output_dir.mkdir(parents=True, exist_ok=True)
    model_id = makerworld_model_id(url) or hashlib.sha1(
        url.encode("utf-8")
    ).hexdigest()[:16]
    stamp = time.strftime("%Y%m%d_%H%M%S")
    base_name = f"model_{model_id}_{stamp}"

    html_path = output_dir / f"{base_name}.html"
    screenshot_path = output_dir / f"{base_name}.png"
    manifest_path = output_dir / f"{base_name}.json"
    network_dir = output_dir / "network_json"
    network_rows: list[dict] = []

    async with async_playwright() as playwright:
        browser, browser_label = await launch_fresh_browser(
            playwright,
            headed=headed,
        )
        context = await browser.new_context(
            locale="en-US",
            viewport={"width": 1440, "height": 1100},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        async def capture_response(response):
            if not capture_network:
                return
            try:
                content_type = (
                    response.headers.get("content-type", "")
                    .split(";", 1)[0]
                    .lower()
                )
                resource_type = response.request.resource_type
                if (
                    content_type == "application/json"
                    or resource_type in {"xhr", "fetch"}
                ):
                    body = await response.body()
                    if len(body) > 8_000_000:
                        return
                    network_dir.mkdir(parents=True, exist_ok=True)
                    digest = hashlib.sha1(
                        response.url.encode("utf-8")
                    ).hexdigest()[:16]
                    target = network_dir / f"{len(network_rows)+1:03d}_{digest}.json"
                    try:
                        parsed = json.loads(body.decode("utf-8", "replace"))
                        target.write_text(
                            json.dumps(parsed, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                    except Exception:
                        target.write_bytes(body)
                    network_rows.append(
                        {
                            "url": response.url,
                            "status": response.status,
                            "content_type": content_type,
                            "file": target.name,
                        }
                    )
            except Exception:
                return

        if capture_network:
            page.on(
                "response",
                lambda response: asyncio.create_task(
                    capture_response(response)
                ),
            )

        response_status = None
        navigation_error = ""

        try:
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=90_000,
            )
            response_status = response.status if response else None
            await page.wait_for_timeout(7000)
        except Exception as error:
            navigation_error = f"{type(error).__name__}: {error}"

        html = await page.content()
        title = await page.title()
        final_url = page.url
        dom_image_urls = await _dom_image_urls(page)
        downloaded_images = (
            await _download_context_images(context, dom_image_urls, output_dir, final_url)
            if download_images else []
        )
        next_data_count = await page.locator(
            "script#__NEXT_DATA__"
        ).count()

        if response_status in (403, 429):
            await browser.close()
            raise PermissionError(f"HTTP {response_status}")

        if next_data_count < 1 and "makerworld.com" in url.lower():
            await browser.close()
            raise RuntimeError(
                "__NEXT_DATA__ was not found on MakerWorld page."
            )

        html_path.write_text(
            html,
            encoding="utf-8",
            newline="\n",
        )
        await page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        digest = hashlib.sha256(
            html.encode("utf-8")
        ).hexdigest()

        manifest = {
            "source": "makerworld"
            if "makerworld.com" in url.lower()
            else "generic",
            "browser": browser_label,
            "requested_url": url,
            "final_url": final_url,
            "model_id": model_id,
            "title": title,
            "http_status": response_status,
            "navigation_error": navigation_error,
            "html_file": html_path.name,
            "screenshot_file": screenshot_path.name,
            "html_sha256": digest,
            "next_data_found": bool(next_data_count),
            "network_capture": network_rows,
            "dom_image_urls": dom_image_urls,
            "downloaded_images": downloaded_images,
            "collected_at": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(),
            ),
        }
        manifest_path.write_text(
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        await browser.close()
        return {
            **manifest,
            "manifest_path": str(manifest_path),
            "html_path": str(html_path),
            "screenshot_path": str(screenshot_path),
        }


async def collect_attached_chrome(
    url: str,
    output_dir: Path,
    *,
    cdp_url: str = "http://127.0.0.1:9222",
    capture_network: bool = True,
    download_images: bool = False,
) -> dict:
    from playwright.async_api import async_playwright

    output_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(cdp_url)
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        page = await context.new_page()

        network_rows: list[dict] = []
        network_dir = output_dir / "network_json"

        async def capture_response(response):
            try:
                content_type = (
                    response.headers.get("content-type", "")
                    .split(";", 1)[0]
                    .lower()
                )
                if (
                    content_type == "application/json"
                    or response.request.resource_type in {"xhr", "fetch"}
                ):
                    body = await response.body()
                    if len(body) > 8_000_000:
                        return
                    network_dir.mkdir(parents=True, exist_ok=True)
                    target = network_dir / (
                        f"{len(network_rows)+1:03d}_"
                        f"{hashlib.sha1(response.url.encode()).hexdigest()[:16]}.json"
                    )
                    target.write_bytes(body)
                    network_rows.append(
                        {
                            "url": response.url,
                            "status": response.status,
                            "file": target.name,
                        }
                    )
            except Exception:
                return

        if capture_network:
            page.on(
                "response",
                lambda response: asyncio.create_task(
                    capture_response(response)
                ),
            )

        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=90_000,
        )
        await page.wait_for_timeout(7000)
        html = await page.content()
        dom_image_urls = await _dom_image_urls(page)
        downloaded_images = (
            await _download_context_images(context, dom_image_urls, output_dir, page.url)
            if download_images else []
        )
        model_id = makerworld_model_id(url) or hashlib.sha1(
            url.encode()
        ).hexdigest()[:16]
        stamp = time.strftime("%Y%m%d_%H%M%S")
        html_path = output_dir / f"attached_{model_id}_{stamp}.html"
        screenshot_path = output_dir / f"attached_{model_id}_{stamp}.png"
        manifest_path = output_dir / f"attached_{model_id}_{stamp}.json"

        html_path.write_text(html, encoding="utf-8", newline="\n")
        await page.screenshot(path=str(screenshot_path), full_page=True)

        manifest = {
            "source": "makerworld"
            if "makerworld.com" in url.lower()
            else "generic",
            "browser": "attached-chrome-cdp",
            "requested_url": url,
            "final_url": page.url,
            "model_id": model_id,
            "title": await page.title(),
            "http_status": response.status if response else None,
            "html_file": html_path.name,
            "screenshot_file": screenshot_path.name,
            "html_sha256": hashlib.sha256(
                html.encode("utf-8")
            ).hexdigest(),
            "network_capture": network_rows,
            "dom_image_urls": dom_image_urls,
            "downloaded_images": downloaded_images,
            "collected_at": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(),
            ),
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        await page.close()
        return {
            **manifest,
            "manifest_path": str(manifest_path),
            "html_path": str(html_path),
            "screenshot_path": str(screenshot_path),
        }


def import_saved_html(
    html_file: Path,
    source_url: str,
    output_dir: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    html = html_file.read_text(
        encoding="utf-8",
        errors="replace",
    )
    model_id = makerworld_model_id(source_url) or hashlib.sha1(
        source_url.encode("utf-8")
    ).hexdigest()[:16]
    stamp = time.strftime("%Y%m%d_%H%M%S")
    copied_html = output_dir / f"saved_{model_id}_{stamp}.html"
    manifest_path = output_dir / f"saved_{model_id}_{stamp}.json"
    copied_html.write_text(html, encoding="utf-8", newline="\n")
    title_match = re.search(
        r"<title>(.*?)</title>",
        html,
        re.I | re.S,
    )
    title = (
        re.sub(r"\s+", " ", title_match.group(1)).strip()
        if title_match
        else ""
    )
    manifest = {
        "source": "makerworld"
        if "makerworld.com" in source_url.lower()
        else "generic",
        "browser": "saved-html",
        "requested_url": source_url,
        "final_url": source_url,
        "model_id": model_id,
        "title": title,
        "http_status": None,
        "html_file": copied_html.name,
        "screenshot_file": "",
        "html_sha256": hashlib.sha256(
            html.encode("utf-8")
        ).hexdigest(),
        "network_capture": [],
        "collected_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        **manifest,
        "manifest_path": str(manifest_path),
        "html_path": str(copied_html),
        "screenshot_path": "",
    }
