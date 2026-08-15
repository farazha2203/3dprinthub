from __future__ import annotations

import asyncio
import hashlib
import json
import random
import re
import time
from html import unescape
from pathlib import Path
from typing import Any, Iterable
from urllib import parse, request

from .db import normalize_url


MODEL_FILE_EXTENSIONS = {
    ".stl",
    ".3mf",
    ".obj",
    ".step",
    ".stp",
    ".iges",
    ".igs",
    ".dxf",
    ".zip",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}


class BlockedError(RuntimeError):
    pass


def public_http(url: str, timeout: int = 45) -> str:
    req = request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            if response.status in (403, 429):
                raise BlockedError(f"HTTP {response.status}")
            payload = response.read(12_000_001)
            if len(payload) > 12_000_000:
                raise RuntimeError("Response is larger than 12 MB.")
            return payload.decode("utf-8", "replace")
    except Exception as error:
        if "403" in str(error) or "429" in str(error):
            raise BlockedError(str(error)) from error
        raise


def unique_urls(values: Iterable[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        try:
            normalized = normalize_url(value)
        except Exception:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        output.append(value)
    return output


def extract_links(text: str, pattern: str):
    if not pattern:
        return []
    regex = re.compile(pattern, re.I)
    output = []
    for match in regex.finditer(text):
        url = unescape(match.group(0))
        external_id = match.groupdict().get("external_id", "")
        output.append((external_id, normalize_url(url)))
    seen = set()
    unique = []
    for item in output:
        if item[1] not in seen:
            seen.add(item[1])
            unique.append(item)
    return unique


def _walk_json(node: Any):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_json(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_json(value)


def _first_text(data: Any, names: set[str]) -> str:
    for node in _walk_json(data):
        if not isinstance(node, dict):
            continue
        for key, value in node.items():
            if key.lower() in names and isinstance(value, str):
                text = re.sub(r"\s+", " ", unescape(value)).strip()
                if text:
                    return text
    return ""


def _collect_urls(data: Any) -> list[str]:
    urls: list[str] = []
    for node in _walk_json(data):
        if isinstance(node, str) and node.startswith(("http://", "https://")):
            urls.append(unescape(node).replace("\\/", "/"))
    return unique_urls(urls)


def _json_ld(html_text: str) -> list[Any]:
    output = []
    pattern = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.I | re.S,
    )
    for match in pattern.finditer(html_text):
        try:
            output.append(json.loads(unescape(match.group(1)).strip()))
        except Exception:
            continue
    return output


def _next_data(html_text: str) -> dict:
    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html_text,
        re.I | re.S,
    )
    if not match:
        return {}
    try:
        return json.loads(unescape(match.group(1)).strip())
    except Exception:
        return {}


def _meta_content(html_text: str, key: str) -> str:
    patterns = [
        rf'<meta[^>]+property=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(key)}["\']',
        rf'<meta[^>]+name=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_text, re.I | re.S)
        if match:
            return re.sub(r"\s+", " ", unescape(match.group(1))).strip()
    return ""


def _number_from_data(data: Any, names: set[str]) -> float | None:
    for node in _walk_json(data):
        if not isinstance(node, dict):
            continue
        for key, value in node.items():
            if key.lower() not in names:
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if 0 < number < 10_000_000:
                return number
    return None


def _file_kind(url: str) -> str:
    path = parse.urlsplit(url).path.lower()
    suffix = Path(path).suffix
    if suffix in MODEL_FILE_EXTENSIONS:
        return "model"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    return ""


def parse_product(
    html_text: str,
    url: str,
    title_hint: str = "",
    dom_links: list[str] | None = None,
):
    json_ld = _json_ld(html_text)
    next_data = _next_data(html_text)
    combined = [json_ld, next_data]

    title = (
        _first_text(combined, {"name", "title", "modelname"})
        or _meta_content(html_text, "og:title")
        or title_hint
    )
    if not title:
        match = re.search(r"<title>(.*?)</title>", html_text, re.I | re.S)
        title = re.sub(r"\s+", " ", match.group(1)).strip() if match else ""

    description = (
        _first_text(
            combined,
            {
                "description",
                "descriptiontext",
                "modeldescription",
                "summary",
            },
        )
        or _meta_content(html_text, "og:description")
        or _meta_content(html_text, "description")
    )

    author = _first_text(
        combined,
        {"authorname", "creatorname", "username", "nickname"},
    )
    license_name = _first_text(
        combined,
        {"licensename", "license", "license_title"},
    )
    category = _first_text(
        combined,
        {"categoryname", "category", "categorytitle"},
    )

    all_urls = _collect_urls(combined)
    if dom_links:
        all_urls.extend(dom_links)
    all_urls = unique_urls(all_urls)

    og_image = _meta_content(html_text, "og:image")
    images = []
    if og_image:
        images.append(og_image)
    images.extend(url for url in all_urls if _file_kind(url) == "image")
    images = unique_urls(images)[:60]

    file_links = unique_urls(
        url for url in all_urls if _file_kind(url) == "model"
    )[:30]

    tags: list[str] = []
    for node in _walk_json(combined):
        if not isinstance(node, dict):
            continue
        for key, value in node.items():
            if key.lower() not in {"keywords", "tags", "taglist"}:
                continue
            if isinstance(value, str):
                tags.extend(
                    item.strip()
                    for item in re.split(r"[,|]", value)
                    if item.strip()
                )
            elif isinstance(value, list):
                tags.extend(str(item).strip() for item in value if str(item).strip())
    tags = list(dict.fromkeys(tags))[:50]

    weight = _number_from_data(
        combined,
        {
            "weight",
            "weightgram",
            "weightgrams",
            "filamentweight",
            "materialweight",
        },
    )
    minutes = _number_from_data(
        combined,
        {
            "printtime",
            "printminutes",
            "estimatedprintminutes",
            "durationminutes",
        },
    )

    return {
        "source_title": title,
        "source_short_description": description[:500],
        "source_description": description,
        "images_json": json.dumps(images, ensure_ascii=False),
        "primary_image_url": images[0] if images else "",
        "file_links_json": json.dumps(file_links, ensure_ascii=False),
        "tags_json": json.dumps(tags, ensure_ascii=False),
        "author_name": author,
        "license_name": license_name,
        "license_url": "",
        "source_category": category,
        "estimated_weight_grams": weight,
        "estimated_print_minutes": minutes,
    }


def parse_generic_product(html_text: str, url: str, title_hint=""):
    return parse_product(html_text, url, title_hint, [])


def download_public_file(
    url: str,
    target: Path,
    *,
    timeout: int = 90,
    max_bytes: int = 120_000_000,
    referer: str | None = None,
) -> Path:
    """Download one public file atomically with an optional product-page Referer."""
    target=Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    partial=target.with_name(target.name+".part")
    partial.unlink(missing_ok=True)
    req=request.Request(
        url,
        headers={
            "User-Agent":"Mozilla/5.0",
            "Referer":referer or url,
            "Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        },
    )
    total=0
    try:
        with request.urlopen(req,timeout=timeout) as response:
            if response.status in (403,429):
                raise BlockedError(f"HTTP {response.status}")
            content_length=int(response.headers.get("Content-Length") or 0)
            if content_length and content_length>max_bytes:
                raise RuntimeError("File is larger than configured limit.")
            with partial.open("wb") as handle:
                while True:
                    chunk=response.read(1024*1024)
                    if not chunk: break
                    total+=len(chunk)
                    if total>max_bytes:
                        raise RuntimeError("File is larger than configured limit.")
                    handle.write(chunk)
        if total<=0:
            raise RuntimeError("Downloaded file is empty.")
        partial.replace(target)
        return target
    except Exception:
        partial.unlink(missing_ok=True)
        raise


class BrowserSession:
    def __init__(
        self,
        profile_dir: Path,
        *,
        headed: bool = False,
        min_delay: float = 8.0,
        max_delay: float = 18.0,
    ) -> None:
        self.profile_dir = profile_dir
        self.headed = headed
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.playwright = None
        self.context = None
        self.page = None
        self.channel = ""

    async def __aenter__(self):
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        errors = []

        for channel in ("chrome", "msedge", "chromium"):
            try:
                self.context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=str(self.profile_dir),
                    channel=channel,
                    headless=not self.headed,
                    locale="en-US",
                    viewport={"width": 1440, "height": 1000},
                    accept_downloads=False,
                )
                self.channel = channel
                break
            except Exception as error:
                errors.append(f"{channel}: {error}")

        if self.context is None:
            await self.playwright.stop()
            raise RuntimeError("No browser available: " + " | ".join(errors))

        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.context is not None:
            await self.context.close()
        if self.playwright is not None:
            await self.playwright.stop()

    async def delay(self):
        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))

    async def fetch(
        self,
        url: str,
        *,
        scroll_rounds: int = 5,
        wait_ms: int = 3500,
    ) -> dict:
        assert self.page is not None
        response = await self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=90_000,
        )
        status = response.status if response else None
        if status in (403, 429):
            raise BlockedError(f"HTTP {status}")

        await self.page.wait_for_timeout(wait_ms)
        previous_height = 0
        for _ in range(max(0, scroll_rounds)):
            height = await self.page.evaluate(
                "() => document.documentElement.scrollHeight"
            )
            await self.page.evaluate(
                "() => window.scrollTo(0, document.documentElement.scrollHeight)"
            )
            await self.page.wait_for_timeout(1400)
            if height == previous_height:
                break
            previous_height = height

        hrefs = await self.page.locator("a[href]").evaluate_all(
            "(els) => els.map((el) => el.href).filter(Boolean)"
        )
        return {
            "html": await self.page.content(),
            "url": self.page.url,
            "title": await self.page.title(),
            "status": status,
            "hrefs": unique_urls(str(value) for value in hrefs),
        }

    async def discover(
        self,
        url: str,
        *,
        model_pattern: str = "",
        same_domain: bool = False,
        scroll_rounds: int = 6,
    ) -> list[tuple[str, str]]:
        result = await self.fetch(url, scroll_rounds=scroll_rounds)
        links = result["hrefs"]
        output: list[tuple[str, str]] = []

        if model_pattern:
            regex = re.compile(model_pattern, re.I)
            for link in links:
                match = regex.search(link)
                if not match:
                    continue
                output.append(
                    (
                        match.groupdict().get("external_id", ""),
                        normalize_url(match.group(0)),
                    )
                )
        else:
            base_domain = parse.urlsplit(url).netloc.lower()
            for link in links:
                parsed = parse.urlsplit(link)
                if parsed.scheme not in {"http", "https"}:
                    continue
                if same_domain and parsed.netloc.lower() != base_domain:
                    continue
                if any(
                    token in parsed.path.lower()
                    for token in (
                        "/model",
                        "/models",
                        "/thing:",
                        "/library/",
                        "/design/",
                        "/stl/",
                        "/3d-model/",
                    )
                ):
                    external_id = hashlib.sha1(
                        normalize_url(link).encode("utf-8")
                    ).hexdigest()[:16]
                    output.append((external_id, normalize_url(link)))

        seen = set()
        unique = []
        for item in output:
            if item[1] not in seen:
                seen.add(item[1])
                unique.append(item)
        return unique

    async def web_search(self, query: str, engine: str = "bing") -> list[str]:
        encoded = parse.quote_plus(query)
        if engine == "duckduckgo":
            url = f"https://duckduckgo.com/?q={encoded}"
        else:
            url = f"https://www.bing.com/search?q={encoded}"

        result = await self.fetch(url, scroll_rounds=2, wait_ms=2500)
        search_hosts = {
            "www.bing.com",
            "bing.com",
            "duckduckgo.com",
            "www.google.com",
            "google.com",
        }
        output = []
        for link in result["hrefs"]:
            parsed = parse.urlsplit(link)
            if parsed.scheme not in {"http", "https"}:
                continue
            if parsed.netloc.lower() in search_hosts:
                continue
            if any(
                token in link.lower()
                for token in (
                    "3d",
                    "stl",
                    "model",
                    "thingiverse",
                    "makerworld",
                    "printables",
                    "grabcad",
                    "cults3d",
                    "myminifactory",
                )
            ):
                output.append(link)
        return unique_urls(output)[:100]


async def browser_context(profile_dir: Path, headed=False):
    session = BrowserSession(profile_dir, headed=headed)
    await session.__aenter__()
    return session.playwright, session.context, session.channel


async def browser_fetch(
    url,
    profile_dir: Path,
    headed=False,
    scroll_rounds=5,
):
    async with BrowserSession(
        profile_dir,
        headed=headed,
        min_delay=0,
        max_delay=0,
    ) as session:
        result = await session.fetch(url, scroll_rounds=scroll_rounds)
        return (
            result["html"],
            result["url"],
            result["title"],
            result["status"],
        )


async def respectful_delay(min_s, max_s):
    await asyncio.sleep(random.uniform(min_s, max_s))
