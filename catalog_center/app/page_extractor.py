from __future__ import annotations

import asyncio
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlsplit

from PIL import Image

from .public_web_capture import build_public_capture_summary, same_site

MODEL_EXTENSIONS = {
    ".stl", ".3mf", ".obj", ".step", ".stp", ".iges", ".igs", ".dxf", ".zip", ".rar", ".7z"
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
BAD_IMAGE_TOKENS = {
    "logo", "avatar", "icon", "emoji", "favicon", "sprite", "placeholder", "loading",
    "badge", "payment", "flag", "social", "profile", "userpic", "advert", "banner"
}
WEIGHT_RE = re.compile(
    r"(?i)(?:estimated\s+)?(?:filament|material|model|part|print)?\s*(?:weight|used|usage|mass)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*(kg|g|gram|grams|oz|lb|lbs)\b"
)
PRINT_TIME_RE = re.compile(
    r"(?i)(?:print\s*time|printing\s*time|estimated\s*time)\s*[:\-]?\s*(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?"
)
DIMENSION_RE = re.compile(
    r"(?i)(?:dimensions?|size)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*[x×]\s*([0-9]+(?:\.[0-9]+)?)\s*[x×]\s*([0-9]+(?:\.[0-9]+)?)\s*(mm|cm|m|in|inch)?"
)
PRICE_RE = re.compile(r"(?i)(?:price\s*[:\-]?\s*)?([$€£]|USD|EUR|GBP)\s*([0-9][0-9,.]*)")


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _walk(node: Any):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _absolute(url: str, base: str) -> str:
    value = _clean_text(url)
    if not value or value.startswith(("data:", "blob:", "javascript:")):
        return ""
    return urljoin(base, value)


def _largest_srcset(srcset: str, base: str) -> str:
    best_url = ""
    best_score = -1.0
    for part in (srcset or "").split(","):
        chunk = part.strip()
        if not chunk:
            continue
        bits = chunk.split()
        candidate = _absolute(bits[0], base)
        if not candidate:
            continue
        score = 1.0
        if len(bits) > 1:
            descriptor = bits[1].lower()
            try:
                if descriptor.endswith("w"):
                    score = float(descriptor[:-1])
                elif descriptor.endswith("x"):
                    score = float(descriptor[:-1]) * 1000
            except ValueError:
                pass
        if score >= best_score:
            best_url = candidate
            best_score = score
    return best_url


def _canonical_image(url: str) -> str:
    parsed = urlsplit(url)
    # Preserve signed/query URLs for download, but remove fragment for dedupe.
    return parsed._replace(fragment="").geturl()


def _extract_json_ld(raw_scripts: Iterable[str]) -> list[Any]:
    output: list[Any] = []
    for raw in raw_scripts:
        raw = (raw or "").strip()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except Exception:
            continue
        output.append(parsed)
    return output


def _product_nodes(json_ld: list[Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for root in json_ld:
        for node in _walk(root):
            if not isinstance(node, dict):
                continue
            kind = node.get("@type")
            kinds = {str(v).lower() for v in _listify(kind)}
            if "product" in kinds or "3dmodel" in kinds:
                found.append(node)
    return found


def _first(nodes: Iterable[dict[str, Any]], key: str) -> Any:
    for node in nodes:
        value = node.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _extract_offer(nodes: list[dict[str, Any]]) -> tuple[float | None, str]:
    for node in nodes:
        for offer in _listify(node.get("offers")):
            if not isinstance(offer, dict):
                continue
            value = offer.get("price") or offer.get("lowPrice") or offer.get("highPrice")
            currency = _clean_text(offer.get("priceCurrency"))
            try:
                if value is not None:
                    return float(str(value).replace(",", "")), currency
            except ValueError:
                pass
    return None, ""


def _extract_weight(nodes: list[dict[str, Any]]) -> tuple[float | None, str]:
    for node in nodes:
        value = node.get("weight")
        if isinstance(value, dict):
            number = value.get("value")
            unit = _clean_text(value.get("unitCode") or value.get("unitText"))
        else:
            number, unit = value, ""
        try:
            if number not in (None, ""):
                return float(number), unit
        except (TypeError, ValueError):
            pass
    return None, ""


def _to_grams(value: float | None, unit: str) -> float | None:
    if value is None:
        return None
    u = (unit or "").lower()
    if u in {"kg", "kilogram", "kilograms", "kgm"}:
        return value * 1000
    if u in {"g", "gram", "grams", "grm"} or not u:
        return value
    if u in {"oz", "ounce", "ounces"}:
        return value * 28.349523125
    if u in {"lb", "lbs", "pound", "pounds"}:
        return value * 453.59237
    return value


def _image_value_to_urls(value: Any, base: str) -> list[str]:
    output: list[str] = []
    for item in _listify(value):
        if isinstance(item, str):
            url = _absolute(item, base)
        elif isinstance(item, dict):
            url = _absolute(item.get("contentUrl") or item.get("url") or "", base)
        else:
            url = ""
        if url:
            output.append(url)
    return output


def _score_image(item: dict[str, Any], title: str) -> float:
    url = item.get("url", "")
    alt = _clean_text(item.get("alt", "")).lower()
    source = item.get("source", "dom")
    width = int(item.get("naturalWidth") or item.get("width") or 0)
    height = int(item.get("naturalHeight") or item.get("height") or 0)
    score = float(item.get("score") or 0)
    if source == "jsonld":
        score += 150
    elif source == "og":
        score += 135
    elif source == "twitter":
        score += 125
    elif source == "network":
        score += 70
    elif source == "dom":
        score += 40
    if width and height:
        score += min(70, (width * height) / 100_000)
        if width < 180 or height < 180:
            score -= 90
    lower_url = url.lower()
    for token in BAD_IMAGE_TOKENS:
        if token in lower_url or token in alt:
            score -= 120
    title_words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if len(w) >= 4]
    if title_words and any(word in alt for word in title_words[:8]):
        score += 25
    suffix = Path(urlsplit(url).path).suffix.lower()
    if suffix == ".svg":
        score -= 300
    return score


@dataclass
class ExtractedImage:
    url: str
    source: str = "dom"
    alt: str = ""
    naturalWidth: int = 0
    naturalHeight: int = 0
    score: float = 0.0
    selected: bool = True
    local_file: str = ""


@dataclass
class ExtractedPage:
    source_url: str
    final_url: str
    source_title: str
    source_description: str
    author_name: str
    license_name: str
    license_url: str
    source_category: str
    source_categories: list[str]
    tags: list[str]
    source_price: float | None
    source_currency: str
    estimated_weight_grams: float | None
    estimated_print_minutes: float | None
    source_rating: float | None
    source_rating_count: int
    source_like_count: int
    source_download_count: int
    source_view_count: int
    source_published_at: str
    source_updated_at: str
    images: list[ExtractedImage]
    file_links: list[str]
    specs: dict[str, Any]
    body_text: str
    capture_summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["images"] = [asdict(image) for image in self.images]
        return data


def _number(value: Any, default: float | None = None) -> float | None:
    if isinstance(value, dict):
        value = value.get("value") or value.get("ratingValue") or value.get("userInteractionCount")
    if value in (None, ""):
        return default
    try:
        return float(str(value).replace(",", "").strip())
    except Exception:
        return default


def _int_number(value: Any) -> int:
    number = _number(value, 0.0)
    return int(number or 0)


def _extract_social_metrics(products: list[dict[str, Any]], network_json: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = {
        "rating": None, "rating_count": 0, "like_count": 0,
        "download_count": 0, "view_count": 0,
        "published_at": "", "updated_at": "",
    }
    for node in products:
        rating = node.get("aggregateRating") or node.get("review")
        if isinstance(rating, list):
            rating = next((x for x in rating if isinstance(x, dict)), None)
        if isinstance(rating, dict):
            candidate = _number(rating.get("ratingValue"))
            if candidate is not None and metrics["rating"] is None:
                metrics["rating"] = candidate
            metrics["rating_count"] = max(metrics["rating_count"], _int_number(rating.get("ratingCount") or rating.get("reviewCount")))
        metrics["published_at"] = metrics["published_at"] or _clean_text(node.get("datePublished") or node.get("uploadDate"))
        metrics["updated_at"] = metrics["updated_at"] or _clean_text(node.get("dateModified"))
        for stat in _listify(node.get("interactionStatistic")):
            if not isinstance(stat, dict):
                continue
            typ = stat.get("interactionType") or stat.get("@type") or ""
            if isinstance(typ, dict):
                typ = typ.get("@type") or typ.get("name") or ""
            typ = str(typ).lower()
            count = _int_number(stat.get("userInteractionCount") or stat.get("interactionCount"))
            if "like" in typ or "favorite" in typ:
                metrics["like_count"] = max(metrics["like_count"], count)
            if "download" in typ:
                metrics["download_count"] = max(metrics["download_count"], count)
            if "view" in typ or "watch" in typ:
                metrics["view_count"] = max(metrics["view_count"], count)

    key_map = {
        "ratingvalue": "rating", "averagerating": "rating", "rating": "rating",
        "ratingcount": "rating_count", "reviewcount": "rating_count",
        "likecount": "like_count", "likes": "like_count", "favoritecount": "like_count",
        "downloadcount": "download_count", "downloads": "download_count",
        "viewcount": "view_count", "views": "view_count",
    }
    for packet in network_json or []:
        data = packet.get("data") if isinstance(packet, dict) else None
        for node in _walk(data):
            if not isinstance(node, dict):
                continue
            for key, value in node.items():
                normalized = re.sub(r"[^a-z]", "", str(key).lower())
                target = key_map.get(normalized)
                if target == "rating":
                    candidate = _number(value)
                    if candidate is not None and 0 <= candidate <= 10 and metrics["rating"] is None:
                        metrics["rating"] = candidate
                elif target:
                    metrics[target] = max(int(metrics[target] or 0), _int_number(value))
                elif normalized in {"datepublished", "publishedat", "createdat", "createtime"} and not metrics["published_at"]:
                    if isinstance(value, str): metrics["published_at"] = value[:80]
                elif normalized in {"datemodified", "updatedat", "updatetime"} and not metrics["updated_at"]:
                    if isinstance(value, str): metrics["updated_at"] = value[:80]
    return metrics

def _candidate_text_from_json(roots: list[Any], keys: set[str], *, min_len: int = 1, max_len: int = 200000) -> str:
    candidates: list[str] = []
    for root in roots:
        for node in _walk(root):
            if not isinstance(node, dict):
                continue
            for key, value in node.items():
                normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
                if normalized not in keys:
                    continue
                if isinstance(value, str):
                    text = _clean_text(value)
                    if min_len <= len(text) <= max_len:
                        candidates.append(text)
    if not candidates:
        return ""
    candidates.sort(key=lambda x: (len(x) < 20, -len(x)))
    return candidates[0]


def _number_with_unit_from_json(roots: list[Any]) -> float | None:
    weight_keys = {"weight","weightgrams","weightgram","filamentweight","filamentused","materialweight","materialused","modelweight","printweight","mass"}
    unit_keys = {"weightunit","unit","unittext","unitcode"}
    for root in roots:
        for node in _walk(root):
            if not isinstance(node, dict):
                continue
            for key, value in node.items():
                normalized = re.sub(r"[^a-z]", "", str(key).lower())
                if normalized not in weight_keys:
                    continue
                if isinstance(value, dict):
                    num = value.get("value") or value.get("amount") or value.get("weight")
                    unit = value.get("unitText") or value.get("unitCode") or value.get("unit") or ""
                else:
                    num = value
                    unit = next((v for k,v in node.items() if re.sub(r"[^a-z]", "", str(k).lower()) in unit_keys), "")
                try:
                    number = float(str(num).replace(",", ""))
                except Exception:
                    continue
                if 0 < number < 100000:
                    return _to_grams(number, str(unit))
    return None


def _specs_from_json(roots: list[Any]) -> dict[str, Any]:
    specs: dict[str, Any] = {}
    interesting = {
        "material","materials","dimensions","dimension","size","layerheight","nozzlesize","printtime","printingtime",
        "filament","filamenttype","infill","supports","support","technology","printer","color","colour","weight","mass"
    }
    for root in roots:
        for node in _walk(root):
            if not isinstance(node, dict):
                continue
            for key, value in node.items():
                nk = re.sub(r"[^a-z]", "", str(key).lower())
                if nk not in interesting or isinstance(value, (dict, list)):
                    continue
                text = _clean_text(value)
                if text and len(text) <= 500:
                    specs.setdefault(str(key)[:120], text)
                if len(specs) >= 80:
                    return specs
    return specs


def parse_page_snapshot(snapshot: dict[str, Any]) -> ExtractedPage:
    final_url = snapshot.get("final_url") or snapshot.get("source_url") or ""
    json_ld = _extract_json_ld(snapshot.get("json_ld") or [])
    products = _product_nodes(json_ld)
    metas = snapshot.get("metas") or {}
    body_text = snapshot.get("body_text") or ""
    embedded_json = []
    for raw in snapshot.get("embedded_json") or []:
        try:
            embedded_json.append(json.loads(raw) if isinstance(raw, str) else raw)
        except Exception:
            continue
    network_roots = [p.get("data") for p in (snapshot.get("network_json") or []) if isinstance(p, dict) and p.get("data") is not None]
    rich_roots = [json_ld, embedded_json, network_roots]

    source_title = (_clean_text(_first(products, "name")) or _clean_text(metas.get("og:title"))
                    or _candidate_text_from_json(rich_roots,{"productname","modelname","title","name"},min_len=3,max_len=300)
                    or _clean_text(snapshot.get("title")))
    source_description = (
        _clean_text(_first(products, "description"))
        or _clean_text(metas.get("og:description"))
        or _clean_text(metas.get("description"))
        or _candidate_text_from_json(rich_roots,{"description","productdescription","modeldescription","summary","details"},min_len=20,max_len=100000)
    )
    author = _first(products, "brand") or _first(products, "manufacturer") or _first(products, "author")
    if isinstance(author, dict):
        author = author.get("name") or author.get("legalName") or ""
    author_name = _clean_text(author)
    source_category = _clean_text(_first(products, "category"))
    source_categories: list[str] = []
    if source_category:
        source_categories.append(source_category)
    for item in snapshot.get("breadcrumbs") or []:
        text = _clean_text(item)
        if text and text.lower() not in {"home", "خانه"} and text not in source_categories:
            source_categories.append(text)
    tags: list[str] = []
    for node in products:
        for value in _listify(node.get("keywords") or node.get("tags")):
            if isinstance(value, str):
                for part in re.split(r"[,|]", value):
                    part = _clean_text(part)
                    if part and part not in tags:
                        tags.append(part)
    for part in re.split(r"[,|]", _clean_text(metas.get("keywords"))):
        part = _clean_text(part)
        if part and part not in tags:
            tags.append(part)

    source_price, source_currency = _extract_offer(products)
    if source_price is None:
        meta_price = metas.get("product:price:amount") or metas.get("og:price:amount")
        try:
            source_price = float(str(meta_price).replace(",", "")) if meta_price not in (None, "") else None
        except ValueError:
            source_price = None
        source_currency = source_currency or _clean_text(metas.get("product:price:currency") or metas.get("og:price:currency"))
    if source_price is None:
        price_match = PRICE_RE.search(body_text[:100_000])
        if price_match:
            symbol, number = price_match.groups()
            try:
                source_price = float(number.replace(",", ""))
                source_currency = {"$": "USD", "€": "EUR", "£": "GBP"}.get(symbol, symbol.upper())
            except ValueError:
                pass

    weight_value, weight_unit = _extract_weight(products)
    estimated_weight_grams = _to_grams(weight_value, weight_unit)
    if estimated_weight_grams is None:
        estimated_weight_grams = _number_with_unit_from_json(rich_roots)
    if estimated_weight_grams is None:
        weight_match = WEIGHT_RE.search(body_text[:250_000])
        if weight_match:
            number, unit = weight_match.groups()
            estimated_weight_grams = _to_grams(float(number), unit)

    estimated_print_minutes = None
    time_match = PRINT_TIME_RE.search(body_text[:150_000])
    if time_match:
        hours = int(time_match.group(1) or 0)
        minutes = int(time_match.group(2) or 0)
        if hours or minutes:
            estimated_print_minutes = hours * 60 + minutes

    social = _extract_social_metrics(products, snapshot.get("network_json") or [])

    specs: dict[str, Any] = _specs_from_json(rich_roots)
    for row in snapshot.get("spec_rows") or []:
        if not isinstance(row, dict):
            continue
        key = _clean_text(row.get("key"))
        value = _clean_text(row.get("value"))
        if key and value and len(key) <= 160 and len(value) <= 1000:
            specs.setdefault(key, value)
    for row in snapshot.get("labeled_sections") or []:
        if isinstance(row, dict):
            key=_clean_text(row.get("heading")); value=_clean_text(row.get("text"))
            if key and value and len(key)<=120 and len(value)<=1200: specs.setdefault(key,value)
    dimensions_match = DIMENSION_RE.search(body_text[:250_000])
    if dimensions_match:
        a, b, c, unit = dimensions_match.groups()
        specs["dimensions"] = {"x": float(a), "y": float(b), "z": float(c), "unit": unit or ""}
    if source_price is not None:
        specs["source_price"] = source_price
        specs["source_currency"] = source_currency
    if estimated_weight_grams is not None:
        specs["estimated_weight_grams"] = estimated_weight_grams
    if estimated_print_minutes is not None:
        specs["estimated_print_minutes"] = estimated_print_minutes

    image_candidates: list[dict[str, Any]] = []
    for node in products:
        for url in _image_value_to_urls(node.get("image"), final_url):
            image_candidates.append({"url": url, "source": "jsonld", "score": 0})
    for key, source in (("og:image", "og"), ("twitter:image", "twitter"), ("twitter:image:src", "twitter")):
        if metas.get(key):
            image_candidates.append({"url": _absolute(metas[key], final_url), "source": source, "score": 0})
    for raw in snapshot.get("dom_images") or []:
        if not isinstance(raw, dict):
            continue
        srcset_best = _largest_srcset(raw.get("srcset") or "", final_url)
        candidates = [
            raw.get("currentSrc"), srcset_best, raw.get("src"), raw.get("dataSrc"), raw.get("dataOriginal"), raw.get("dataLazySrc")
        ]
        for candidate in candidates:
            url = _absolute(candidate or "", final_url)
            if not url:
                continue
            image_candidates.append({
                "url": url,
                "source": "dom",
                "alt": raw.get("alt") or "",
                "naturalWidth": raw.get("naturalWidth") or 0,
                "naturalHeight": raw.get("naturalHeight") or 0,
                "width": raw.get("width") or 0,
                "height": raw.get("height") or 0,
                "score": 0,
            })
    for raw in snapshot.get("picture_sources") or []:
        url = _largest_srcset(raw.get("srcset") or "", final_url) if isinstance(raw, dict) else ""
        if url:
            image_candidates.append({"url": url, "source": "dom", "score": 0})

    # Mine public JSON/XHR responses already delivered to the page. No auth/CAPTCHA bypass is attempted.
    for packet in snapshot.get("network_json") or []:
        data = packet.get("data") if isinstance(packet, dict) else None
        for node in _walk(data):
            if isinstance(node, str) and node.startswith(("http://", "https://")):
                suffix = Path(urlsplit(node).path).suffix.lower()
                if suffix in IMAGE_EXTENSIONS:
                    image_candidates.append({"url": node, "source": "network", "score": 35})
            elif isinstance(node, dict):
                for key, value in node.items():
                    lk = str(key).lower()
                    if isinstance(value, str) and value.startswith(("http://", "https://")):
                        suffix = Path(urlsplit(value).path).suffix.lower()
                        if suffix in IMAGE_EXTENSIONS or any(t in lk for t in ("image", "thumbnail", "preview", "cover")):
                            image_candidates.append({"url": value, "source": "network", "score": 45})

    dedup: dict[str, dict[str, Any]] = {}
    for item in image_candidates:
        url = item.get("url") or ""
        if not url:
            continue
        key = _canonical_image(url)
        item["score"] = _score_image(item, source_title)
        previous = dedup.get(key)
        if previous is None or item["score"] > previous["score"]:
            dedup[key] = item
    ranked = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)
    images = [
        ExtractedImage(
            url=item["url"],
            source=item.get("source", "dom"),
            alt=_clean_text(item.get("alt")),
            naturalWidth=int(item.get("naturalWidth") or 0),
            naturalHeight=int(item.get("naturalHeight") or 0),
            score=round(float(item.get("score") or 0), 2),
            selected=float(item.get("score") or 0) >= 10,
        )
        for item in ranked[:100]
        if float(item.get("score") or 0) > 0
    ]

    links: list[str] = []
    for item in snapshot.get("links") or []:
        href = item.get("href") if isinstance(item, dict) else str(item)
        absolute = _absolute(href or "", final_url)
        if not absolute:
            continue
        suffix = Path(urlsplit(absolute).path).suffix.lower()
        text = _clean_text(item.get("text") if isinstance(item, dict) else "").lower()
        if suffix in MODEL_EXTENSIONS or ("download" in text and suffix in MODEL_EXTENSIONS):
            links.append(absolute)
    for packet in snapshot.get("network_json") or []:
        data = packet.get("data") if isinstance(packet, dict) else None
        for node in _walk(data):
            if isinstance(node, str) and node.startswith(("http://", "https://")):
                if Path(urlsplit(node).path).suffix.lower() in MODEL_EXTENSIONS:
                    links.append(node)
    links = list(dict.fromkeys(links))[:150]

    license_name = ""
    license_url = ""
    for item in snapshot.get("links") or []:
        if not isinstance(item, dict):
            continue
        text = _clean_text(item.get("text")).lower()
        href = _absolute(item.get("href") or "", final_url)
        if "license" in text or "creative commons" in text:
            license_name = _clean_text(item.get("text"))
            license_url = href
            break

    return ExtractedPage(
        source_url=snapshot.get("source_url") or final_url,
        final_url=final_url,
        source_title=source_title,
        source_description=source_description,
        author_name=author_name,
        license_name=license_name,
        license_url=license_url,
        source_category=source_category,
        source_categories=source_categories[:30],
        tags=tags[:80],
        source_price=source_price,
        source_currency=source_currency,
        estimated_weight_grams=estimated_weight_grams,
        estimated_print_minutes=estimated_print_minutes,
        source_rating=social["rating"],
        source_rating_count=social["rating_count"],
        source_like_count=social["like_count"],
        source_download_count=social["download_count"],
        source_view_count=social["view_count"],
        source_published_at=social["published_at"],
        source_updated_at=social["updated_at"],
        images=images,
        file_links=links,
        specs=specs,
        body_text=body_text,
    )


async def _wait_for_page_stability(
    page,
    *,
    timeout_ms: int = 5000,
    stable_samples: int = 2,
    include_load_state: bool = True,
) -> None:
    """Wait for measurable document stability instead of a fixed blind sleep.

    Playwright already auto-waits for actions. For generic acquisition pages we
    additionally observe document size/text/image counts because there is no
    site-specific locator that is valid across all supported sources.
    """
    if include_load_state:
        try:
            await page.wait_for_load_state("load", timeout=min(2500, max(250, int(timeout_ms))))
        except Exception:
            pass

    deadline = asyncio.get_running_loop().time() + (max(250, int(timeout_ms)) / 1000.0)
    last_state = None
    stable = 0
    while asyncio.get_running_loop().time() < deadline:
        try:
            state = tuple(await page.evaluate(
                """() => [
                    document.readyState || '',
                    document.documentElement ? document.documentElement.scrollHeight : 0,
                    document.body ? (document.body.innerText || '').length : 0,
                    document.images ? document.images.length : 0
                ]"""
            ))
        except Exception:
            return
        if state == last_state and state and state[0] in {"interactive", "complete"}:
            stable += 1
            if stable >= max(1, int(stable_samples)):
                return
        else:
            stable = 0
            last_state = state
        await page.wait_for_timeout(180)


async def _scroll_lazy_content(page, *, max_rounds: int = 4) -> None:
    """Trigger bounded lazy loading and stop as soon as page growth settles."""
    previous = None
    for _ in range(max(1, int(max_rounds))):
        try:
            await page.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)")
            await _wait_for_page_stability(
                page,
                timeout_ms=1500,
                stable_samples=2,
                include_load_state=False,
            )
            state = tuple(await page.evaluate(
                """() => [
                    document.documentElement ? document.documentElement.scrollHeight : 0,
                    document.images ? document.images.length : 0
                ]"""
            ))
        except Exception:
            break
        if state == previous:
            break
        previous = state
    try:
        await page.evaluate("() => window.scrollTo(0, 0)")
        await _wait_for_page_stability(
            page,
            timeout_ms=700,
            stable_samples=1,
            include_load_state=False,
        )
    except Exception:
        pass


class RichPageExtractor:
    def __init__(self, profile_dir: Path, *, headed: bool = True):
        self.profile_dir = profile_dir
        self.headed = headed

    async def extract(self, url: str, output_dir: Path, *, download_images: bool = True, image_limit: int = 60) -> ExtractedPage:
        from playwright.async_api import async_playwright

        output_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as playwright:
            context = None
            errors: list[str] = []
            for channel in ("chrome", "msedge", "chromium"):
                try:
                    context = await playwright.chromium.launch_persistent_context(
                        user_data_dir=str(self.profile_dir),
                        channel=channel,
                        headless=not self.headed,
                        locale="en-US",
                        viewport={"width": 1440, "height": 1000},
                        accept_downloads=False,
                    )
                    break
                except Exception as exc:
                    errors.append(f"{channel}: {exc}")
            if context is None:
                raise RuntimeError("No browser available: " + " | ".join(errors))
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                network_json: list[dict[str, Any]] = []
                network_tasks: set[asyncio.Task] = set()

                async def capture_json(response):
                    try:
                        if len(network_json) >= 80 or response.status >= 400:
                            return
                        if not same_site(url, response.url):
                            return
                        ctype = (response.headers.get("content-type") or "").lower()
                        resource_type = str(response.request.resource_type or "").lower()
                        if "json" not in ctype and resource_type not in {"xhr", "fetch"}:
                            return
                        content_length = response.headers.get("content-length") or ""
                        try:
                            if content_length and int(content_length) > 2_000_000:
                                return
                        except Exception:
                            pass
                        raw = await response.body()
                        if not raw or len(raw) > 2_000_000:
                            return
                        data = json.loads(raw.decode("utf-8", errors="replace"))
                        network_json.append({
                            "url": response.url,
                            "status": int(response.status or 0),
                            "method": str(response.request.method or "GET"),
                            "resource_type": resource_type,
                            "content_type": ctype.split(";", 1)[0],
                            "body_bytes": len(raw),
                            "data": data,
                        })
                    except Exception:
                        return

                def schedule_capture(response):
                    task = asyncio.create_task(capture_json(response))
                    network_tasks.add(task)
                    task.add_done_callback(network_tasks.discard)

                page.on("response", schedule_capture)
                response = await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
                if response and response.status in (403, 429):
                    raise RuntimeError(f"HTTP {response.status}")

                await _wait_for_page_stability(page, timeout_ms=5000)
                await _scroll_lazy_content(page, max_rounds=4)

                if network_tasks:
                    _done, pending = await asyncio.wait(tuple(network_tasks), timeout=2.0)
                    for task in pending:
                        task.cancel()
                snapshot = await page.evaluate(
                    """() => {
                        const metas = {};
                        for (const el of document.querySelectorAll('meta[property], meta[name]')) {
                            const key = (el.getAttribute('property') || el.getAttribute('name') || '').toLowerCase();
                            const content = el.getAttribute('content') || '';
                            if (key && content && !(key in metas)) metas[key] = content;
                        }
                        const dom_images = Array.from(document.images).map(img => ({
                            currentSrc: img.currentSrc || '', src: img.src || '', srcset: img.srcset || '',
                            dataSrc: img.getAttribute('data-src') || '',
                            dataOriginal: img.getAttribute('data-original') || '',
                            dataLazySrc: img.getAttribute('data-lazy-src') || img.getAttribute('data-lazy') || '',
                            alt: img.alt || '', naturalWidth: img.naturalWidth || 0, naturalHeight: img.naturalHeight || 0,
                            width: Math.round(img.getBoundingClientRect().width || 0),
                            height: Math.round(img.getBoundingClientRect().height || 0)
                        }));
                        const picture_sources = Array.from(document.querySelectorAll('picture source[srcset], source[srcset]')).map(el => ({srcset: el.srcset || ''}));
                        const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                            href: a.href || '', text: (a.innerText || a.textContent || '').trim().slice(0, 300), download: a.getAttribute('download') || ''
                        }));
                        const json_ld = Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(s => s.textContent || '');
                        const embedded_json = Array.from(document.querySelectorAll('script[type="application/json"], script#__NEXT_DATA__, script[id*="__NEXT"], script[id*="NUXT"]')).map(s => s.textContent || '').filter(x => x && x.length < 2500000).slice(0, 40);
                        const breadcrumbs = Array.from(document.querySelectorAll(
                            '[aria-label*="breadcrumb" i] a, nav.breadcrumb a, .breadcrumb a, [class*="breadcrumb"] a, [class*="Breadcrumb"] a'
                        )).map(a => (a.innerText || a.textContent || '').trim()).filter(Boolean).slice(0, 40);
                        const spec_rows = [];
                        for (const tr of document.querySelectorAll('table tr')) {
                            const cells = Array.from(tr.querySelectorAll('th,td')).map(x => (x.innerText || x.textContent || '').trim());
                            if (cells.length >= 2 && cells[0] && cells[1]) spec_rows.push({key: cells[0], value: cells.slice(1).join(' | ')});
                        }
                        for (const dt of document.querySelectorAll('dl dt')) {
                            const dd = dt.nextElementSibling;
                            if (dd && dd.tagName && dd.tagName.toLowerCase() === 'dd') {
                                const key = (dt.innerText || dt.textContent || '').trim();
                                const value = (dd.innerText || dd.textContent || '').trim();
                                if (key && value) spec_rows.push({key, value});
                            }
                        }
                        return {
                            final_url: location.href,
                            title: document.title || '',
                            metas, dom_images, picture_sources, links, json_ld, embedded_json, breadcrumbs, spec_rows: spec_rows.slice(0, 120),
                            labeled_sections: Array.from(document.querySelectorAll('h1,h2,h3,h4')).slice(0,60).map(h => ({heading:(h.innerText||h.textContent||'').trim(), text:(h.nextElementSibling ? (h.nextElementSibling.innerText||h.nextElementSibling.textContent||'').trim() : '').slice(0,1600)})).filter(x=>x.heading&&x.text),
                            body_text: (document.body ? document.body.innerText : '').slice(0, 400000)
                        };
                    }"""
                )
                snapshot["network_json"] = network_json
                snapshot["source_url"] = url
                snapshot["http_status"] = int(response.status) if response else 0
                capture_summary = build_public_capture_summary(
                    url,
                    network_json,
                    json_ld_count=len(snapshot.get("json_ld") or []),
                    embedded_json_count=len(snapshot.get("embedded_json") or []),
                    breadcrumb_count=len(snapshot.get("breadcrumbs") or []),
                    spec_row_count=len(snapshot.get("spec_rows") or []),
                )
                extracted = parse_page_snapshot(snapshot)
                extracted.capture_summary = capture_summary
                (output_dir / "page_extract.json").write_text(
                    json.dumps(extracted.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
                )
                if download_images and extracted.images:
                    await self._download_images(context, extracted, output_dir, image_limit=image_limit)
                    (output_dir / "page_extract.json").write_text(
                        json.dumps(extracted.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                return extracted
            finally:
                await context.close()

    async def _download_images(self, context, extracted: ExtractedPage, output_dir: Path, *, image_limit: int = 60) -> None:
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        saved_index = 0
        for image in extracted.images:
            if saved_index >= max(1, image_limit):
                break
            if not image.selected:
                continue
            try:
                response = await context.request.get(
                    image.url,
                    headers={"Referer": extracted.final_url},
                    timeout=35_000,
                )
                if not response.ok:
                    continue
                content_type = (response.headers.get("content-type") or "").split(";", 1)[0].lower()
                if not content_type.startswith("image/"):
                    continue
                raw = await response.body()
                if not raw or len(raw) < 4_000 or len(raw) > 30_000_000:
                    continue
                suffix = {
                    "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
                    "image/gif": ".gif", "image/avif": ".avif"
                }.get(content_type) or Path(urlsplit(image.url).path).suffix.lower() or ".jpg"
                saved_index += 1
                target = image_dir / f"{saved_index:03d}{suffix if suffix in IMAGE_EXTENSIONS else '.jpg'}"
                target.write_bytes(raw)
                try:
                    with Image.open(target) as im:
                        width, height = im.size
                    if width < 160 or height < 160:
                        target.unlink(missing_ok=True)
                        saved_index -= 1
                        image.selected = False
                        continue
                    image.naturalWidth = image.naturalWidth or width
                    image.naturalHeight = image.naturalHeight or height
                except Exception:
                    pass
                image.local_file = str(target)
            except Exception:
                continue


def detect_source_code(url: str) -> str:
    host = urlsplit(url).netloc.lower().removeprefix("www.")
    if "makerworld.com" in host:
        return "makerworld"
    if "printables.com" in host:
        return "printables"
    if "thingiverse.com" in host:
        return "thingiverse"
    if "grabcad.com" in host:
        return "grabcad"
    safe = re.sub(r"[^a-z0-9]+", "_", host)[:48].strip("_") or "custom"
    return f"site_{safe}"


def detect_external_id(url: str, source_code: str) -> str:
    patterns = {
        "makerworld": r"/models/(\d+)",
        "printables": r"/model/(\d+)",
        "thingiverse": r"thing:(\d+)",
        "grabcad": r"/library/([^/?#]+)",
    }
    pattern = patterns.get(source_code)
    if pattern:
        match = re.search(pattern, url, re.I)
        if match:
            return match.group(1)
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


async def extract_direct_link(
    url: str,
    output_dir: Path,
    profile_dir: Path,
    *,
    headed: bool = True,
    download_images: bool = True,
    image_limit: int = 60,
) -> dict[str, Any]:
    extractor = RichPageExtractor(profile_dir, headed=headed)
    page = await extractor.extract(url, output_dir, download_images=download_images, image_limit=image_limit)
    source_code = detect_source_code(page.final_url or url)
    external_id = detect_external_id(page.final_url or url, source_code)
    selected_urls = [img.url for img in page.images if img.selected]
    all_urls = [img.url for img in page.images]
    local_files = [img.local_file for img in page.images if img.local_file]
    return {
        "source_code": source_code,
        "external_id": external_id,
        "source_url": page.final_url or url,
        "normalized_url": page.final_url or url,
        "source_title": page.source_title,
        "source_short_description": page.source_description[:500],
        "source_description": page.source_description,
        "author_name": page.author_name,
        "license_name": page.license_name,
        "license_url": page.license_url,
        "source_category": page.source_category,
        "source_categories_json": json.dumps(page.source_categories, ensure_ascii=False),
        "tags_json": json.dumps(page.tags, ensure_ascii=False),
        "images_json": json.dumps(all_urls, ensure_ascii=False),
        "selected_images_json": json.dumps(selected_urls, ensure_ascii=False),
        "primary_image_url": selected_urls[0] if selected_urls else (all_urls[0] if all_urls else ""),
        "file_links_json": json.dumps(page.file_links, ensure_ascii=False),
        "selected_file_links_json": json.dumps(page.file_links, ensure_ascii=False),
        "source_specs_json": json.dumps(page.specs, ensure_ascii=False),
        "source_snapshot_json": json.dumps(page.as_dict(), ensure_ascii=False),
        "source_price": page.source_price,
        "source_currency": page.source_currency,
        "estimated_weight_grams": page.estimated_weight_grams,
        "estimated_print_minutes": page.estimated_print_minutes,
        "source_rating": page.source_rating,
        "source_rating_count": page.source_rating_count,
        "source_like_count": page.source_like_count,
        "source_download_count": page.source_download_count,
        "source_view_count": page.source_view_count,
        "source_published_at": page.source_published_at,
        "source_updated_at": page.source_updated_at,
        "local_dir": str(output_dir),
        "downloaded_image_files": local_files,
    }
