from __future__ import annotations

import html
import json
import math
import os
import re
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "3DprintHub-CatalogBot/1.0 (+https://3dprinthub.ir)"


@dataclass(slots=True)
class CatalogCandidate:
    url: str
    external_id: str = ""
    summary: dict[str, Any] = field(default_factory=dict)


class LinkAndMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.metas: dict[str, str] = {}
        self.json_ld: list[Any] = []
        self._script_type = ""
        self._script_chunks: list[str] = []
        self.text_chunks: list[str] = []
        self._ignore_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): (value or "") for key, value in attrs}
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignore_depth += 1
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "meta":
            key = values.get("property") or values.get("name")
            content = values.get("content")
            if key and content:
                self.metas[key.lower()] = content
        if tag == "script":
            self._script_type = values.get("type", "").lower()
            self._script_chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            raw = "".join(self._script_chunks).strip()
            if raw and self._script_type == "application/ld+json":
                try:
                    self.json_ld.append(json.loads(raw))
                except (TypeError, ValueError, json.JSONDecodeError):
                    pass
            self._script_chunks = []
            self._script_type = ""
        if tag in {"script", "style", "noscript", "svg"} and self._ignore_depth:
            self._ignore_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._script_type:
            self._script_chunks.append(data)
        elif not self._ignore_depth:
            cleaned = " ".join(data.split())
            if cleaned:
                self.text_chunks.append(cleaned)


class CatalogHTTPClient:
    def __init__(
        self,
        *,
        headers: dict[str, str] | None = None,
        timeout: int = 20,
        delay_ms: int = 1000,
        max_bytes: int = 8_000_000,
    ) -> None:
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8,fa;q=0.5",
            **(headers or {}),
        }
        self.timeout = max(3, min(int(timeout or 20), 120))
        self.delay_seconds = max(0, int(delay_ms or 0)) / 1000
        self.max_bytes = max_bytes
        self._last_request_at = 0.0

    def _wait(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)

    def fetch_bytes(self, url: str, *, extra_headers: dict[str, str] | None = None) -> tuple[bytes, str]:
        self._wait()
        request = Request(url, headers={**self.headers, **(extra_headers or {})})
        with urlopen(request, timeout=self.timeout) as response:  # nosec B310 - domains are policy checked by caller
            content_type = response.headers.get_content_type()
            payload = response.read(self.max_bytes + 1)
        self._last_request_at = time.monotonic()
        if len(payload) > self.max_bytes:
            raise ValueError("پاسخ منبع از سقف حجم مجاز بزرگ‌تر است.")
        return payload, content_type

    def fetch_text(self, url: str, *, extra_headers: dict[str, str] | None = None) -> str:
        payload, _ = self.fetch_bytes(url, extra_headers=extra_headers)
        return payload.decode("utf-8", errors="replace")

    def fetch_json(self, url: str, *, extra_headers: dict[str, str] | None = None) -> Any:
        payload, _ = self.fetch_bytes(url, extra_headers=extra_headers)
        return json.loads(payload.decode("utf-8", errors="strict"))


def robots_allowed(url: str, *, user_agent: str = USER_AGENT, timeout: int = 10) -> bool:
    import urllib.robotparser

    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        request = Request(robots_url, headers={"User-Agent": user_agent})
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - URL derives from validated source
            text = response.read(512_001).decode("utf-8", errors="replace")
        parser.parse(text.splitlines())
    except Exception:
        return True
    return parser.can_fetch(user_agent, url)


def parse_html_document(raw_html: str) -> LinkAndMetaParser:
    parser = LinkAndMetaParser()
    parser.feed(raw_html)
    return parser


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value if item is not None)
    return " ".join(html.unescape(str(value)).replace("\u200c", " ").split()).strip()


def normalize_persian(value: str) -> str:
    table = str.maketrans({"ي": "ی", "ك": "ک", "ۀ": "ه", "ة": "ه", "ؤ": "و", "إ": "ا", "أ": "ا"})
    return normalize_text(value).translate(table).lower()


def safe_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return max(0, int(value))
    text = normalize_text(value).lower().replace(",", "")
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([kmb]?)", text)
    if not match:
        return 0
    number = float(match.group(1))
    multiplier = {"": 1, "k": 1_000, "m": 1_000_000, "b": 1_000_000_000}.get(match.group(2), 1)
    return max(0, int(number * multiplier))


def first_value(data: Any, keys: Iterable[str], default: Any = "") -> Any:
    wanted = {key.lower().replace("_", "") for key in keys}

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            for key, value in node.items():
                compact = str(key).lower().replace("_", "")
                if compact in wanted and value not in (None, "", [], {}):
                    return value
            for value in node.values():
                found = walk(value)
                if found not in (None, "", [], {}):
                    return found
        elif isinstance(node, list):
            for item in node:
                found = walk(item)
                if found not in (None, "", [], {}):
                    return found
        return None

    found = walk(data)
    return default if found in (None, "") else found


def all_values(data: Any, keys: Iterable[str]) -> list[Any]:
    wanted = {key.lower().replace("_", "") for key in keys}
    values: list[Any] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                compact = str(key).lower().replace("_", "")
                if compact in wanted and value not in (None, "", [], {}):
                    values.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return values


def extract_json_blobs(raw_html: str) -> list[Any]:
    parser = parse_html_document(raw_html)
    blobs = list(parser.json_ld)
    patterns = [
        r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        r'<script[^>]+type="application/json"[^>]*>(.*?)</script>',
        r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, raw_html, re.I | re.S):
            raw = html.unescape(match.group(1)).strip()
            try:
                blobs.append(json.loads(raw))
            except (ValueError, TypeError, json.JSONDecodeError):
                continue
    return blobs


def unique_urls(values: Iterable[Any], base_url: str = "") -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, dict):
            value = value.get("url") or value.get("contentUrl") or value.get("downloadUrl")
        if not isinstance(value, str):
            continue
        url = urljoin(base_url, value.strip())
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        seen.add(url)
        result.append(url)
    return result


def allowed_domain(url: str, domains: Iterable[str]) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    normalized = [domain.strip().lower().lstrip(".") for domain in domains if domain.strip()]
    return any(hostname == domain or hostname.endswith("." + domain) for domain in normalized)


def extract_external_id(url: str, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, url, re.I)
        if match:
            return match.group(1)
    path = urlparse(url).path.strip("/")
    return path.rsplit("/", 1)[-1][:150]


def extract_file_formats(values: Iterable[Any]) -> list[str]:
    formats: set[str] = set()
    known = {"stl", "3mf", "obj", "step", "stp", "iges", "igs", "f3d", "scad", "zip", "rar", "7z", "gcode", "amf", "ply"}
    for value in values:
        text = normalize_text(value).lower()
        for suffix in re.findall(r"\.([a-z0-9]{2,8})(?:\b|$)", text):
            if suffix in known:
                formats.add(suffix.upper())
        for token in re.findall(r"\b(?:stl|3mf|obj|step|stp|iges|igs|f3d|scad|zip|rar|7z|gcode|amf|ply)\b", text):
            formats.add(token.upper())
    return sorted(formats)


def parse_duration_minutes(value: Any) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        numeric = int(value)
        if 0 < numeric < 60 * 24 * 365:
            return numeric
    text = normalize_text(value).lower()
    iso = re.fullmatch(r"p(?:\d+d)?t(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", text, re.I)
    if iso:
        return int(iso.group(1) or 0) * 60 + int(iso.group(2) or 0) + math.ceil(int(iso.group(3) or 0) / 60)
    hours = re.search(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours|ساعت)", text)
    minutes = re.search(r"(\d+)\s*(?:m|min|mins|minute|minutes|دقیقه)", text)
    if hours or minutes:
        hour_minutes = int(round(float(hours.group(1)) * 60)) if hours else 0
        minute_value = int(minutes.group(1)) if minutes else 0
        return hour_minutes + minute_value
    colon = re.fullmatch(r"(\d{1,3}):(\d{2})(?::\d{2})?", text)
    if colon:
        return int(colon.group(1)) * 60 + int(colon.group(2))
    return None


def parse_weight_grams(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if 0 < number < 100_000 else None
    text = normalize_text(value).lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms|g|gram|grams|گرم|کیلوگرم)\b", text)
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2)
    if unit in {"kg", "kilogram", "kilograms", "کیلوگرم"}:
        amount *= 1000
    return amount if 0 < amount < 100_000 else None


def license_decision(source_kind: str, license_name: str, raw_text: str = "") -> tuple[bool | None, str, str]:
    text = normalize_text(f"{license_name} {raw_text}").lower()
    compact = re.sub(r"[^a-z0-9]+", "-", text)

    if source_kind == "grabcad":
        return False, "blocked", "شرایط عمومی GrabCAD برای این گردش‌کار فقط استفاده مرجع داخلی را مجاز می‌داند."

    blocked_markers = [
        "non-commercial", "noncommercial", "cc-by-nc", "cc by-nc", "cc by nc",
        "personal use", "standard digital file license",
    ]
    if any(marker in text or marker.replace(" ", "-") in compact for marker in blocked_markers):
        return False, "blocked", "مجوز منبع فروش چاپ فیزیکی را صریحاً مجاز نمی‌داند."

    allowed_markers = [
        "cc0", "pd0", "public domain", "creative commons zero", "creative commons attribution",
        "cc by ", "cc-by-", "cc by-sa", "cc-by-sa", "attribution-sharealike",
        "cc by-nd", "cc-by-nd", "attribution-noderivatives", "attribution-no derivatives",
        "commercial use allowed", "commercial license included",
    ]
    if any(marker in text or marker.replace(" ", "-") in compact for marker in allowed_markers):
        if any(marker in text or marker.replace(" ", "-") in compact for marker in (
            "cc by-nd", "cc-by-nd", "attribution-noderivatives", "attribution-no derivatives"
        )):
            return True, "allowed", "مجوز تجاری است، اما مدل باید بدون تغییر چاپ شود و انتساب منبع حفظ گردد."
        return True, "allowed", "مجوز به‌صورت خودکار تجاری تشخیص داده شد؛ بررسی نهایی ادمین همچنان لازم است."

    if source_kind == "makerworld" and "commercial license" in text:
        return None, "manual", "وجود گزینه مجوز تجاری تشخیص داده شد، اما قرارداد دقیق سازنده باید دستی بررسی شود."

    return None, "manual", "مجوز برای فروش چاپ فیزیکی صریح نیست و باید توسط ادمین بررسی شود."


def meta_value(parser: LinkAndMetaParser, *keys: str) -> str:
    for key in keys:
        value = parser.metas.get(key.lower())
        if value:
            return normalize_text(value)
    return ""


def best_title(parser: LinkAndMetaParser, blobs: list[Any]) -> str:
    return normalize_text(
        first_value(blobs, ["name", "headline", "title"], "")
        or meta_value(parser, "og:title", "twitter:title")
    )


def best_description(parser: LinkAndMetaParser, blobs: list[Any]) -> str:
    return normalize_text(
        first_value(blobs, ["description", "caption"], "")
        or meta_value(parser, "og:description", "description", "twitter:description")
    )


def best_images(parser: LinkAndMetaParser, blobs: list[Any], base_url: str) -> list[str]:
    values: list[Any] = [
        meta_value(parser, "og:image", "twitter:image", "twitter:image:src"),
        *all_values(blobs, ["image", "images", "imageUrl", "thumbnail", "thumbnailUrl", "cover", "coverUrl"]),
    ]
    flattened: list[Any] = []
    for value in values:
        if isinstance(value, list):
            flattened.extend(value)
        else:
            flattened.append(value)
    return unique_urls(flattened, base_url)


def link_discovery(raw_html: str, base_url: str, pattern: re.Pattern[str], limit: int) -> list[CatalogCandidate]:
    parser = parse_html_document(raw_html)
    output: list[CatalogCandidate] = []
    seen: set[str] = set()
    for href in parser.links:
        url = urljoin(base_url, href).split("#", 1)[0]
        if url in seen:
            continue
        match = pattern.search(urlparse(url).path)
        if not match:
            continue
        seen.add(url)
        output.append(CatalogCandidate(url=url, external_id=match.group(1)))
        if len(output) >= limit:
            break
    return output


def flatten_json_lists(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("results", "items", "data", "hits", "things", "models"):
            item = value.get(key)
            if isinstance(item, list):
                return item
            if isinstance(item, dict):
                nested = flatten_json_lists(item)
                if nested:
                    return nested
    return []
