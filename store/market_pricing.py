from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import timedelta
from decimal import Decimal
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urlunparse

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from website.models import Material

from .models import (
    BambuFilamentCatalogItem,
    ExchangeRateProvider,
    ExchangeRateSnapshot,
    MarketPricingSetting,
    MaterialMarketPriceSnapshot,
)
from .source_monitoring import source_log, update_log

USER_AGENT = "3DprintHub-SourceMonitor/2.0 (+https://3dprinthub.ir)"
TGJU_ALLOWED_HOSTS = {"tgju.org", "www.tgju.org"}
BAMBU_ALLOWED_HOSTS = {"us.store.bambulab.com", "bambulab-us.myshopify.com"}
MAX_HTML_BYTES = 6 * 1024 * 1024
MAX_JSON_BYTES = 10 * 1024 * 1024

PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _decimal(value) -> Decimal:
    text = str(value).translate(PERSIAN_DIGITS).replace(",", "").replace("٬", "").strip()
    return Decimal(text)


def _safe_url(url: str, allowed_hosts: set[str]) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in allowed_hosts:
        raise ValidationError("دامنه یا پروتکل منبع مجاز نیست.")
    return url


def _request(url: str, *, timeout: int, accept: str, max_bytes: int):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept,
            "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.7,en;q=0.5",
            "Cache-Control": "no-cache",
        },
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValidationError("حجم پاسخ منبع بیش از حد مجاز است.")
        content_type = response.headers.get("Content-Type", "")
        charset = response.headers.get_content_charset() or "utf-8"
        status = getattr(response, "status", 200)
    return body.decode(charset, errors="replace"), {
        "http_status": status,
        "content_type": content_type,
        "final_url": final_url,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "bytes": len(body),
    }


def _request_json(url: str, *, timeout: int):
    text, meta = _request(url, timeout=timeout, accept="application/json,text/plain,*/*", max_bytes=MAX_JSON_BYTES)
    try:
        return json.loads(text), meta
    except json.JSONDecodeError as exc:
        raise ValidationError(f"پاسخ JSON معتبر نیست: {exc}") from exc


def _request_html(url: str, *, timeout: int):
    return _request(url, timeout=timeout, accept="text/html,application/xhtml+xml", max_bytes=MAX_HTML_BYTES)


def _html_to_text(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text).translate(PERSIAN_DIGITS)
    return re.sub(r"\s+", " ", text).strip()


def parse_tgju_dollar_html(html: str) -> dict:
    text = _html_to_text(html)
    current_patterns = [
        r"نرخ\s*فعلی\s*[:：]*\s*([0-9][0-9,٬]{3,})",
        r"در\s*حال\s*حاضر\s*قیمت\s*هر\s*دلار\s*([0-9][0-9,٬]{3,})\s*ریال",
    ]
    high_patterns = [
        r"بالاترین\s*قیمت\s*روز\s*([0-9][0-9,٬]{3,})",
        r"بالاترین\s*قیمتی[^0-9]{0,120}([0-9][0-9,٬]{3,})\s*ریال",
    ]

    def first_number(patterns):
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.I)
            if match:
                return int(_decimal(match.group(1)))
        return None

    current_rial = first_number(current_patterns)
    daily_high_rial = first_number(high_patterns)
    if not current_rial:
        raise ValidationError("نرخ فعلی دلار در صفحه TGJU پیدا نشد.")
    if current_rial < 100_000 or current_rial > 100_000_000:
        raise ValidationError("نرخ استخراج‌شده TGJU خارج از بازه منطقی است.")
    if not daily_high_rial or daily_high_rial < current_rial * Decimal("0.70"):
        daily_high_rial = current_rial
    current_toman = (Decimal(current_rial) / Decimal("10")).quantize(Decimal("0.01"))
    daily_high_toman = (Decimal(daily_high_rial) / Decimal("10")).quantize(Decimal("0.01"))
    return {
        "current_rial": current_rial,
        "daily_high_rial": daily_high_rial,
        "current_toman": current_toman,
        "daily_high_toman": max(current_toman, daily_high_toman),
    }


def fetch_tgju_rate(url: str, *, timeout=12):
    _safe_url(url, TGJU_ALLOWED_HOSTS)
    html, meta = _request_html(url, timeout=timeout)
    _safe_url(meta["final_url"], TGJU_ALLOWED_HOSTS)
    parsed = parse_tgju_dollar_html(html)
    return parsed["current_toman"], {
        "source": "tgju_html",
        "current_rial": parsed["current_rial"],
        "daily_high_rial": parsed["daily_high_rial"],
        "daily_high_toman": str(parsed["daily_high_toman"]),
        "http": meta,
    }


def _json_path(payload, path: str):
    current = payload
    for key in (path or "").split("."):
        key = key.strip()
        if not key:
            continue
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            current = current[int(key)]
        else:
            raise KeyError(path)
    return current


def fetch_provider_rate(provider: ExchangeRateProvider):
    if provider.provider_type == "manual":
        if not provider.manual_sell_rate_toman:
            raise ValidationError("نرخ دستی این منبع وارد نشده است.")
        return Decimal(provider.manual_sell_rate_toman), {"source": "manual"}
    if provider.provider_type == "tgju_html":
        endpoint = provider.endpoint_url or MarketPricingSetting.load().tgju_profile_url
        return fetch_tgju_rate(endpoint, timeout=provider.timeout_seconds)
    if provider.provider_type == "bonbast":
        username = os.environ.get(provider.username_env or "BONBAST_USERNAME", "").strip()
        secret = os.environ.get(provider.secret_env or "BONBAST_API_KEY", "").strip()
        if not username or not secret:
            raise ValidationError("نام کاربری یا کلید Bonbast در متغیرهای محیطی تنظیم نشده است.")
        endpoint = provider.endpoint_url or f"https://bonbast.com/api/{username}"
        body = urllib.parse.urlencode({"hash": secret}).encode("utf-8")
        request = urllib.request.Request(endpoint, data=body, headers={"User-Agent": USER_AGENT}, method="POST")
        with urllib.request.urlopen(request, timeout=provider.timeout_seconds) as response:
            payload = json.loads(response.read(MAX_JSON_BYTES).decode("utf-8"))
    elif provider.provider_type == "generic_json":
        if not provider.endpoint_url:
            raise ValidationError("آدرس JSON API وارد نشده است.")
        payload, _meta = _request_json(provider.endpoint_url, timeout=provider.timeout_seconds)
    else:
        raise ValidationError("نوع منبع نرخ ارز پشتیبانی نمی‌شود.")
    value = _decimal(_json_path(payload, provider.json_sell_path))
    if provider.response_unit == "rial":
        value /= Decimal("10")
    value *= provider.multiplier
    if value <= 0:
        raise ValidationError("نرخ دریافت‌شده معتبر نیست.")
    return value.quantize(Decimal("0.01")), payload


def test_exchange_provider(provider: ExchangeRateProvider, *, actor=None):
    with source_log(source_key="tgju" if provider.provider_type == "tgju_html" else "fx", action="test", actor=actor) as log:
        update_log(log, stage="اتصال به منبع", progress=20, message=provider.name)
        rate, payload = fetch_provider_rate(provider)
        http = payload.get("http", {}) if isinstance(payload, dict) else {}
        update_log(
            log,
            stage="پارسر نرخ",
            progress=85,
            http_status=http.get("http_status"),
            records_found=1,
            details={"rate_toman": str(rate), "payload": payload},
            message=f"نرخ فعلی {rate:,.0f} تومان با موفقیت استخراج شد.",
        )
        return rate, payload, log


def refresh_fx_rates(*, now=None, actor=None):
    now = now or timezone.now()
    setting = MarketPricingSetting.load()
    errors, successes = [], []
    for provider in ExchangeRateProvider.objects.filter(is_active=True).order_by("priority", "id"):
        try:
            with source_log(source_key="tgju" if provider.provider_type == "tgju_html" else "fx", action="fetch_rate", actor=actor) as log:
                update_log(log, stage="دریافت نرخ", progress=25, message=provider.name)
                rate, payload = fetch_provider_rate(provider)
                snapshot = ExchangeRateSnapshot.objects.create(
                    provider=provider,
                    currency="USD",
                    sell_rate_toman=rate,
                    observed_at=now,
                    local_date=timezone.localdate(now),
                    raw_payload=payload if isinstance(payload, dict) else {"payload": payload},
                )
                provider.last_success_at = now
                provider.last_error = ""
                provider.save(update_fields=["last_success_at", "last_error"])
                http = payload.get("http", {}) if isinstance(payload, dict) else {}
                update_log(log, stage="ذخیره نرخ", progress=90, http_status=http.get("http_status"), records_found=1, records_saved=1, details={"rate_toman": str(rate), "payload": payload}, message=f"نرخ {rate:,.0f} تومان ثبت شد.")
                successes.append(snapshot)
        except Exception as exc:
            provider.last_error = f"{type(exc).__name__}: {exc}"[:2000]
            provider.save(update_fields=["last_error"])
            errors.append(f"{provider.name}: {exc}")
    if successes:
        setting.last_fx_refresh_at = now
    setting.last_error = "\n".join(errors[-20:])
    setting.save(update_fields=["last_fx_refresh_at", "last_error", "updated_at"])
    return successes


def effective_fx_rates(*, now=None):
    now = now or timezone.now()
    latest = ExchangeRateSnapshot.objects.filter(currency="USD").order_by("-observed_at", "-id").first()
    if latest is None:
        return None, None
    today = timezone.localdate(now)
    snapshots = list(ExchangeRateSnapshot.objects.filter(currency="USD", local_date=today).order_by("-sell_rate_toman"))
    candidates = [latest.sell_rate_toman]
    for snap in snapshots:
        candidates.append(snap.sell_rate_toman)
        raw_high = (snap.raw_payload or {}).get("daily_high_toman")
        if raw_high not in (None, ""):
            try:
                candidates.append(_decimal(raw_high))
            except Exception:
                pass
    return latest.sell_rate_toman, max(candidates)


def ensure_fx_fresh(*, now=None):
    now = now or timezone.now()
    setting = MarketPricingSetting.load()
    if not setting.enabled or not setting.refresh_fx_on_public_request:
        return effective_fx_rates(now=now)
    stale_before = now - timedelta(minutes=max(setting.refresh_fx_minutes, 1))
    if setting.last_fx_refresh_at and setting.last_fx_refresh_at >= stale_before:
        return effective_fx_rates(now=now)
    if cache.add("phase11:refresh-fx", "1", timeout=90):
        try:
            refresh_fx_rates(now=now)
            refresh_material_market_prices(refresh_bambu=False, now=now)
        except Exception:
            pass
        finally:
            cache.delete("phase11:refresh-fx")
    return effective_fx_rates(now=now)


class _BambuLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._href = None
        self._text = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href", "")
            if "/products/" in href:
                self._href = href
                self._text = []
    def handle_data(self, data):
        if self._href:
            self._text.append(data)
    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href:
            self.links.append((self._href, re.sub(r"\s+", " ", " ".join(self._text)).strip()))
            self._href = None
            self._text = []



BAMBU_COLLECTION_FALLBACKS = (
    "https://us.store.bambulab.com/collections/all-filaments/",
    "https://us.store.bambulab.com/collections/bambu-lab-3d-printer-filament",
    "https://us.store.bambulab.com/collections/bambu-filament-bundle-discount/",
)

FILAMENT_TITLE_TOKENS = (
    "pla", "petg", "abs", "asa", "tpu", "pa6", "paht", "pet-cf", "pc", "pva",
    "filament", "support for pla", "support for pa", "support for pet",
)
FILAMENT_EXCLUDE_TOKENS = (
    "reusable spool", "led backlight", "printer", "hotend", "build plate", "ams ",
)


def _collection_json_url(collection_url: str) -> str:
    parsed = urlparse(collection_url)
    path = parsed.path.rstrip("/") + "/products.json"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "limit=250", ""))


def _shopify_price(value) -> Decimal:
    """Normalize both Shopify products.json decimal prices and product.js cent prices."""
    raw = _decimal(value)
    if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
        if raw > Decimal("1000"):
            raw = raw / Decimal("100")
    return raw.quantize(Decimal("0.01"))


def _is_filament_title(title: str, product_type: str = "", tags=None) -> bool:
    haystack = " ".join([title or "", product_type or "", " ".join(tags or [])]).lower()
    if any(token in haystack for token in FILAMENT_EXCLUDE_TOKENS):
        return False
    return any(token in haystack for token in FILAMENT_TITLE_TOKENS)


def _normalize_bambu_product(product: dict, base_url: str) -> dict | None:
    handle = str(product.get("handle") or "").strip()
    title = str(product.get("title") or "").strip()
    product_type = str(product.get("product_type") or product.get("type") or "")[:120]
    tags = product.get("tags") or []
    if isinstance(tags, str):
        tags = [part.strip() for part in tags.split(",") if part.strip()]
    if not handle or not title or not _is_filament_title(title, product_type, tags):
        return None
    variants = product.get("variants") or []
    prices = []
    available = False
    clean_variants = []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        try:
            price = _shopify_price(variant.get("price"))
        except Exception:
            continue
        if not (Decimal("1") <= price <= Decimal("1000")):
            continue
        prices.append(price)
        is_available = bool(variant.get("available", True))
        available = available or is_available
        clean_variants.append({
            "id": variant.get("id"),
            "title": variant.get("title") or variant.get("name"),
            "price": str(price),
            "available": is_available,
            "sku": variant.get("sku"),
        })
    if not prices:
        try:
            candidate = _shopify_price(product.get("price"))
            if Decimal("1") <= candidate <= Decimal("1000"):
                prices.append(candidate)
        except Exception:
            pass
    if not prices:
        return None
    images = product.get("images") or []
    image_url = ""
    if images:
        first = images[0]
        image_url = first.get("src", "") if isinstance(first, dict) else str(first)
    if not image_url and isinstance(product.get("featured_image"), str):
        image_url = product["featured_image"]
    return {
        "external_id": str(product.get("id") or handle),
        "handle": handle,
        "title": title,
        "product_url": urljoin(base_url, f"/products/{handle}"),
        "image_url": image_url,
        "vendor": str(product.get("vendor") or "Bambu Lab")[:120],
        "product_type": product_type or "Filament",
        "tags": tags,
        "min_price_usd": min(prices),
        "max_price_usd": max(prices),
        "conservative_price_usd": max(prices),
        "available": available or not variants,
        "variants": clean_variants,
        "raw_payload": product,
    }


def _extract_bambu_handles(html: str, base_url: str) -> list[tuple[str, str]]:
    decoded = unescape(html).replace("\\/", "/")
    patterns = [
        r'href=["\'](?:https?://[^"\']+)?(?:/en)?/products/([a-z0-9][a-z0-9-]+)[^"\']*["\']',
        r'"(?:url|href|handle)"\s*:\s*"(?:https?://[^"/]+)?(?:/en)?/products/([a-z0-9][a-z0-9-]+)',
        r'(?:/en)?/products/([a-z0-9][a-z0-9-]+)',
    ]
    handles = []
    seen = set()
    for pattern in patterns:
        for match in re.finditer(pattern, decoded, flags=re.I):
            handle = match.group(1).lower().strip("-/")
            if handle and handle not in seen:
                seen.add(handle)
                handles.append((handle, urljoin(base_url, f"/products/{handle}")))
    return handles


def _product_js_url(product_url: str) -> str:
    parsed = urlparse(product_url)
    match = re.search(r"/products/([^/?#]+)", parsed.path)
    if not match:
        raise ValidationError("Handle محصول Bambu از لینک استخراج نشد.")
    return urlunparse((parsed.scheme, parsed.netloc, f"/products/{match.group(1)}.js", "", "", ""))


def _fallback_bambu_html_records(html: str, base_url: str) -> list[dict]:
    output = []
    for handle, absolute in _extract_bambu_handles(html, base_url):
        pos = html.lower().find(handle.lower())
        nearby = html[max(0, pos - 500):pos + 5000] if pos >= 0 else ""
        prices = []
        for value in re.findall(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)", nearby)[:20]:
            try:
                price = _decimal(value)
            except Exception:
                continue
            if Decimal("1") <= price <= Decimal("1000"):
                prices.append(price)
        title_match = re.search(rf"(?:<h[23][^>]*>|title[\"']?\s*[:=]\s*[\"'])\s*([^<\"']*{re.escape(handle.split('-')[0])}[^<\"']*)", nearby, re.I)
        title = normalize_bambu_title = (unescape(title_match.group(1)).strip() if title_match else handle.replace("-", " ").title())
        if not _is_filament_title(normalize_bambu_title):
            continue
        if prices:
            output.append({
                "external_id": handle,
                "handle": handle,
                "title": normalize_bambu_title[:220],
                "product_url": absolute,
                "image_url": "",
                "vendor": "Bambu Lab",
                "product_type": "Filament",
                "tags": [],
                "min_price_usd": min(prices),
                "max_price_usd": max(prices),
                "conservative_price_usd": max(prices),
                "available": True,
                "variants": [],
                "raw_payload": {"parser": "collection_html", "prices": [str(p) for p in prices]},
            })
    return output


def _fetch_bambu_product_record(product_url: str, *, timeout: int):
    _safe_url(product_url, BAMBU_ALLOWED_HOSTS)
    js_url = _product_js_url(product_url)
    try:
        payload, meta = _request_json(js_url, timeout=timeout)
        _safe_url(meta["final_url"], BAMBU_ALLOWED_HOSTS)
        record = _normalize_bambu_product(payload, product_url)
        if record:
            record["raw_payload"] = {"mode": "product_js", "payload": payload}
            return record, {"mode": "product_js", "http": meta, "url": js_url}
    except Exception as exc:
        js_error = f"{type(exc).__name__}: {exc}"
    else:
        js_error = "product.js بدون قیمت معتبر"

    html, meta = _request_html(product_url, timeout=timeout)
    _safe_url(meta["final_url"], BAMBU_ALLOWED_HOSTS)
    prices = _extract_jsonld_prices(html)
    if not prices:
        prices = [_decimal(value) for value in re.findall(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)\s*USD", html, flags=re.I)]
    prices = [price for price in prices if Decimal("1") <= price <= Decimal("1000")]
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    title = _html_to_text(title_match.group(1)) if title_match else urlparse(product_url).path.rsplit("/", 1)[-1].replace("-", " ").title()
    if not prices or not _is_filament_title(title):
        raise ValidationError(f"قیمت معتبر محصول Bambu پیدا نشد. product.js: {js_error}")
    handle = _extract_handle(product_url)
    record = {
        "external_id": handle,
        "handle": handle,
        "title": title[:220],
        "product_url": product_url,
        "image_url": "",
        "vendor": "Bambu Lab",
        "product_type": "Filament",
        "tags": [],
        "min_price_usd": min(prices),
        "max_price_usd": max(prices),
        "conservative_price_usd": max(prices),
        "available": True,
        "variants": [],
        "raw_payload": {"mode": "product_html", "prices": [str(p) for p in prices], "product_js_error": js_error},
    }
    return record, {"mode": "product_html", "http": meta, "product_js_error": js_error}


def _candidate_collection_urls(configured_url: str) -> list[str]:
    urls = []
    for url in (configured_url, *BAMBU_COLLECTION_FALLBACKS):
        clean = (url or "").strip()
        if clean and clean not in urls:
            urls.append(clean)
    return urls


def fetch_bambu_collection(collection_url: str, *, timeout=20, max_products=250):
    errors = []
    for candidate_url in _candidate_collection_urls(collection_url):
        _safe_url(candidate_url, BAMBU_ALLOWED_HOSTS)
        json_url = _collection_json_url(candidate_url)
        try:
            payload, meta = _request_json(json_url, timeout=timeout)
            _safe_url(meta["final_url"], BAMBU_ALLOWED_HOSTS)
            records = [_normalize_bambu_product(item, candidate_url) for item in payload.get("products", [])]
            records = [item for item in records if item][:max_products]
            if records:
                return records, {"mode": "collection_products_json", "http": meta, "json_url": json_url, "collection_url": candidate_url}
        except Exception as exc:
            errors.append(f"{candidate_url} JSON: {type(exc).__name__}: {exc}")

        try:
            html, meta = _request_html(candidate_url, timeout=timeout)
            _safe_url(meta["final_url"], BAMBU_ALLOWED_HOSTS)
            handles = _extract_bambu_handles(html, candidate_url)
            if not handles:
                errors.append(f"{candidate_url} HTML: هیچ لینک محصولی پیدا نشد")
                continue
            records = []
            product_errors = []
            for index, (_handle, product_url) in enumerate(handles[:max_products], start=1):
                try:
                    record, _product_meta = _fetch_bambu_product_record(product_url, timeout=timeout)
                    if record and record["handle"] not in {item["handle"] for item in records}:
                        records.append(record)
                except Exception as exc:
                    product_errors.append(f"{product_url}: {type(exc).__name__}: {exc}")
                if index < min(len(handles), max_products):
                    time.sleep(0.12)
            if records:
                return records, {
                    "mode": "collection_html_product_js",
                    "http": meta,
                    "collection_url": candidate_url,
                    "discovered_handles": len(handles),
                    "product_errors": product_errors[-20:],
                    "fallback_errors": errors[-10:],
                }
            basic = _fallback_bambu_html_records(html, candidate_url)[:max_products]
            if basic:
                return basic, {"mode": "collection_html_prices", "http": meta, "collection_url": candidate_url, "fallback_errors": errors[-10:]}
            errors.extend(product_errors[-10:])
        except Exception as exc:
            errors.append(f"{candidate_url} HTML: {type(exc).__name__}: {exc}")

    raise ValidationError("هیچ محصول Bambu استخراج نشد. جزئیات: " + " | ".join(errors[-12:]))


def test_bambu_collection(*, actor=None):
    setting = MarketPricingSetting.load()
    with source_log(source_key="bambu", action="test", actor=actor) as log:
        update_log(log, stage="اتصال به مجموعه", progress=15, message=setting.bambu_collection_url)
        records, meta = fetch_bambu_collection(
            setting.bambu_collection_url,
            timeout=setting.source_timeout_seconds,
            max_products=8,
        )
        update_log(
            log,
            stage="تحلیل محصولات",
            progress=90,
            http_status=meta.get("http", {}).get("http_status"),
            records_found=len(records),
            details={"mode": meta.get("mode"), "collection_url": meta.get("collection_url"), "sample": records[:3], "errors": meta.get("fallback_errors", [])},
            message=f"{len(records)} محصول قابل تحلیل پیدا شد؛ روش {meta.get('mode')}.",
        )
        return records, meta, log


@transaction.atomic
def sync_bambu_collection(*, actor=None, now=None):
    now = now or timezone.now()
    setting = MarketPricingSetting.load()
    with source_log(source_key="bambu", action="sync", actor=actor) as log:
        update_log(log, stage="دریافت مجموعه", progress=10, message=setting.bambu_collection_url)
        records, meta = fetch_bambu_collection(setting.bambu_collection_url, timeout=setting.source_timeout_seconds)
        update_log(log, stage="ذخیره محصولات", progress=55, http_status=meta.get("http", {}).get("http_status"), records_found=len(records), details={"mode": meta.get("mode"), "collection_url": meta.get("collection_url"), "errors": meta.get("fallback_errors", [])})
        saved = updated = 0
        seen = []
        total = max(len(records), 1)
        for index, record in enumerate(records, start=1):
            seen.append(record["handle"])
            _obj, created = BambuFilamentCatalogItem.objects.update_or_create(
                handle=record["handle"],
                defaults={**record, "last_seen_at": now, "is_active": True},
            )
            saved += int(created)
            updated += int(not created)
            if index % 10 == 0 or index == total:
                update_log(log, stage=f"ذخیره محصول {index} از {total}", progress=min(92, 55 + int(index / total * 35)), records_saved=saved, records_updated=updated)
        BambuFilamentCatalogItem.objects.exclude(handle__in=seen).update(is_active=False)
        setting.last_bambu_catalog_sync_at = now
        if meta.get("collection_url") and setting.bambu_collection_url != meta["collection_url"]:
            setting.bambu_collection_url = meta["collection_url"]
            setting.save(update_fields=["last_bambu_catalog_sync_at", "bambu_collection_url", "updated_at"])
        else:
            setting.save(update_fields=["last_bambu_catalog_sync_at", "updated_at"])
        update_log(log, stage="تکمیل فهرست", progress=95, records_saved=saved, records_updated=updated, details={"mode": meta.get("mode"), "products": len(records), "collection_url": meta.get("collection_url")}, message=f"{len(records)} محصول؛ جدید {saved}، بروزشده {updated}.")
        return records, log

def _extract_handle(url: str) -> str:
    match = re.search(r"/products/([^/?#]+)", url or "")
    return match.group(1) if match else ""


def _normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def cached_bambu_price_for_material(material: Material):
    handle = _extract_handle(getattr(material, "bambu_product_url", ""))
    item = None
    if handle:
        item = BambuFilamentCatalogItem.objects.filter(handle=handle, is_active=True).first()
    if item is None:
        target = _normalized_name(material.name)
        for candidate in BambuFilamentCatalogItem.objects.filter(is_active=True):
            if _normalized_name(candidate.title) == target:
                item = candidate
                break
    return item


def _extract_jsonld_prices(html: str):
    prices = []
    blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, flags=re.I | re.S)
    for block in blocks:
        try:
            payload = json.loads(unescape(block).strip())
        except Exception:
            continue
        nodes = payload if isinstance(payload, list) else [payload]
        for node in list(nodes):
            if not isinstance(node, dict):
                continue
            if isinstance(node.get("@graph"), list):
                nodes.extend(node["@graph"])
            offers = node.get("offers")
            offers = offers if isinstance(offers, list) else [offers]
            for offer in offers:
                if isinstance(offer, dict):
                    for key in ("price", "highPrice", "lowPrice"):
                        if offer.get(key) not in (None, ""):
                            try: prices.append(_decimal(offer[key]))
                            except Exception: pass
    return prices


def fetch_bambu_usd_price(url: str, *, timeout=12):
    _safe_url(url, BAMBU_ALLOWED_HOSTS)
    handle = _extract_handle(url)
    if handle:
        item = BambuFilamentCatalogItem.objects.filter(handle=handle, is_active=True).first()
        if item:
            return item.conservative_price_usd, {"mode": "catalog_cache", "handle": handle, "min": str(item.min_price_usd), "max": str(item.max_price_usd)}
    html, meta = _request_html(url, timeout=timeout)
    _safe_url(meta["final_url"], BAMBU_ALLOWED_HOSTS)
    prices = _extract_jsonld_prices(html)
    if not prices:
        prices = [_decimal(value) for value in re.findall(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)\s*USD", html, flags=re.I)]
    prices = [p for p in prices if Decimal("1") <= p <= Decimal("1000")]
    if not prices:
        raise ValidationError("قیمت دلاری معتبر در صفحه رسمی Bambu پیدا نشد.")
    return max(prices).quantize(Decimal("0.01")), {"mode": "product_html", "found_prices": [str(p) for p in sorted(set(prices))], "http": meta}


def _round_up(value: Decimal, step: int) -> int:
    step = max(int(step or 1), 1)
    return int(math.ceil(float(value) / step) * step)


@transaction.atomic
def calculate_material_market_price(material: Material, *, fx_current, fx_daily_high, bambu_usd_price=None, now=None):
    now = now or timezone.now()
    setting = MarketPricingSetting.load()
    usd_price = _decimal(bambu_usd_price if bambu_usd_price is not None else material.market_bambu_usd_price)
    if usd_price <= 0:
        raise ValidationError("قیمت دلاری متریال مشخص نیست.")
    weight = _decimal(material.bambu_reference_weight_grams or 1000)
    if weight <= 0:
        raise ValidationError("وزن مرجع متریال معتبر نیست.")
    fx_used = _decimal(fx_daily_high if setting.use_daily_high_fx else fx_current)
    import_percent = material.market_import_cost_percent if material.market_import_cost_percent is not None else setting.default_import_cost_percent
    margin_percent = material.market_margin_percent if material.market_margin_percent is not None else setting.default_margin_percent
    landed_roll = usd_price * fx_used * (Decimal("1") + _decimal(import_percent) / Decimal("100"))
    cost_per_gram = landed_roll / weight
    sale_per_gram = _round_up(cost_per_gram * (Decimal("1") + _decimal(margin_percent) / Decimal("100")), setting.price_rounding_toman)
    material.market_bambu_usd_price = usd_price
    material.market_fx_daily_high_toman = fx_daily_high
    material.market_cost_price_per_gram = cost_per_gram.quantize(Decimal("0.01"))
    material.market_sale_price_per_gram = sale_per_gram
    material.market_price_updated_at = now
    material.save(update_fields=["market_bambu_usd_price", "market_fx_daily_high_toman", "market_cost_price_per_gram", "market_sale_price_per_gram", "market_price_updated_at"])
    return MaterialMarketPriceSnapshot.objects.create(
        material=material, bambu_usd_price=usd_price, fx_current_toman=fx_current,
        fx_daily_high_toman=fx_daily_high, cost_per_gram_toman=cost_per_gram,
        sale_per_gram_toman=sale_per_gram, observed_at=now,
        raw_payload={"import_percent": str(import_percent), "margin_percent": str(margin_percent), "weight_grams": str(weight), "fx_policy": "daily_high" if setting.use_daily_high_fx else "current"},
    )


def refresh_material_market_prices(*, refresh_bambu=True, now=None, actor=None):
    now = now or timezone.now()
    setting = MarketPricingSetting.load()
    if refresh_bambu:
        try:
            sync_bambu_collection(actor=actor, now=now)
        except Exception as exc:
            setting.last_error = f"Bambu collection: {type(exc).__name__}: {exc}"[:4000]
            setting.save(update_fields=["last_error", "updated_at"])
    fx_current, fx_high = effective_fx_rates(now=now)
    if not fx_current:
        raise ValidationError("هیچ نرخ دلار معتبری ثبت نشده است.")
    results, errors = [], []
    for material in Material.objects.filter(is_active=True, market_pricing_enabled=True):
        try:
            usd_price = material.market_bambu_usd_price
            raw = {}
            item = cached_bambu_price_for_material(material) if refresh_bambu else None
            if item:
                usd_price = item.conservative_price_usd
                raw = {"mode": "catalog_cache", "handle": item.handle, "min": str(item.min_price_usd), "max": str(item.max_price_usd)}
            elif refresh_bambu and material.bambu_product_url:
                usd_price, raw = fetch_bambu_usd_price(material.bambu_product_url, timeout=setting.source_timeout_seconds)
            snapshot = calculate_material_market_price(material, fx_current=fx_current, fx_daily_high=fx_high, bambu_usd_price=usd_price, now=now)
            if raw:
                snapshot.raw_payload.update({"bambu": raw})
                snapshot.save(update_fields=["raw_payload"])
            results.append(snapshot)
        except Exception as exc:
            errors.append(f"{material.name}: {type(exc).__name__}: {exc}")
    if refresh_bambu and results:
        setting.last_bambu_refresh_at = now
    setting.last_error = "\n".join(errors[-30:]) if errors else ""
    setting.save(update_fields=["last_bambu_refresh_at", "last_error", "updated_at"])
    return results, errors

# BEGIN PHASE 16 BAMBU PRICE HISTORY SYNC
from decimal import Decimal as _phase16_Decimal

from .models import BambuFilamentPriceHistory as _phase16_BambuFilamentPriceHistory


def _phase16_record_bambu_price_history(records, *, observed_at=None, source_mode=""):
    observed_at = observed_at or timezone.now()
    created = 0
    changed = 0
    for record in records:
        handle = str(record.get("handle") or "").strip()
        if not handle:
            continue
        item = BambuFilamentCatalogItem.objects.filter(handle=handle).first()
        if item is None:
            continue
        previous_row = (
            _phase16_BambuFilamentPriceHistory.objects.filter(item=item)
            .order_by("-observed_at", "-id")
            .first()
        )
        previous_price = (
            previous_row.conservative_price_usd
            if previous_row is not None
            else None
        )
        current_price = item.conservative_price_usd
        delta = (
            current_price - previous_price
            if previous_price is not None
            else _phase16_Decimal("0")
        )
        delta_percent = _phase16_Decimal("0")
        if previous_price not in (None, _phase16_Decimal("0")):
            delta_percent = (delta / previous_price) * _phase16_Decimal("100")
        is_changed = previous_price is not None and delta != 0
        _phase16_BambuFilamentPriceHistory.objects.create(
            item=item,
            observed_at=observed_at,
            min_price_usd=item.min_price_usd,
            max_price_usd=item.max_price_usd,
            conservative_price_usd=current_price,
            previous_conservative_price_usd=previous_price,
            delta_usd=delta,
            delta_percent=delta_percent,
            available=item.available,
            changed=is_changed,
            source_mode=source_mode or "sync",
            variants=item.variants or [],
        )
        created += 1
        changed += int(is_changed)
    return {"created": created, "changed": changed}


_phase16_original_sync_bambu_collection = sync_bambu_collection


@transaction.atomic
def sync_bambu_collection(*, actor=None, now=None):
    observed_at = now or timezone.now()
    records, log = _phase16_original_sync_bambu_collection(
        actor=actor,
        now=observed_at,
    )
    source_mode = ""
    try:
        source_mode = str((log.details or {}).get("mode") or "")
    except Exception:
        source_mode = ""
    history_result = _phase16_record_bambu_price_history(
        records,
        observed_at=observed_at,
        source_mode=source_mode,
    )
    try:
        details = dict(log.details or {})
        details["price_history"] = history_result
        log.details = details
        log.message = (
            f"{log.message} تاریخچه قیمت: {history_result['created']}، "
            f"تغییرکرده: {history_result['changed']}."
        ).strip()
        log.save(update_fields=["details", "message", "updated_at"])
    except Exception:
        pass
    return records, log
# END PHASE 16 BAMBU PRICE HISTORY SYNC
