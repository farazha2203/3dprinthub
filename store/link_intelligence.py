from __future__ import annotations

import ipaddress
import math
import mimetypes
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from website.models import Material, Order, Quote

from .catalog_importer import FILE_EXTENSIONS, PageMetadataParser, parse_print_page
from .catalog_site_adapters import get_source_adapter
from .catalog_site_adapters.base import CatalogCandidate
from .catalog_site_adapters.common import (
    all_values,
    best_description,
    best_images,
    best_title,
    extract_file_formats,
    extract_json_blobs,
    first_value,
    normalize_text,
    parse_duration_minutes,
    parse_html_document,
    parse_weight_grams,
    unique_urls,
)
from .catalog_sync import save_external_record
from .models import (
    CatalogRefreshRequest,
    CustomerLinkAnalysis,
    ImportedPrintAsset,
    PricingSetting,
)

USER_AGENT = "3DprintHub-LinkIntelligence/1.0 (+https://3dprinthub.ir)"
MAX_HTML_BYTES = 6 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_PORTS = {None, 80, 443}
class LinkAnalysisError(Exception):
    """Base exception for queue-aware link analysis failures."""

    transient = False


class TransientLinkAnalysisError(LinkAnalysisError):
    transient = True


class PermanentLinkAnalysisError(LinkAnalysisError):
    transient = False


ProgressCallback = Callable[[int, str, str], None]


def _notify_progress(callback: ProgressCallback | None, percent: int, stage: str, message: str) -> None:
    if callback is None:
        return
    try:
        callback(max(0, min(int(percent), 100)), str(stage or "")[:80], str(message or "")[:300])
    except Exception:
        # Progress reporting must never make the actual analysis fail.
        return


MATERIAL_ALIASES = {
    "PPS-CF": ("pps-cf", "pps cf", "pps carbon"),
    "PA-CF": ("pa-cf", "pa cf", "nylon carbon", "nylon-cf"),
    "PA": ("nylon", "polyamide", " pa "),
    "PETG-CF": ("petg-cf", "petg cf"),
    "PETG": ("petg",),
    "PLA-CF": ("pla-cf", "pla cf"),
    "PLA": ("pla", "polylactic"),
    "ABS": ("abs",),
    "ASA": ("asa",),
    "TPU": ("tpu", "flexible filament"),
    "PC": ("polycarbonate", " pc "),
    "PEEK": ("peek",),
    "RESIN": ("resin", "sla", "msla"),
}


def _normalize_host(hostname: str) -> str:
    try:
        return hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise ValidationError("دامنه لینک معتبر نیست.") from exc


def _assert_public_host(hostname: str) -> None:
    normalized = _normalize_host(hostname)
    if normalized in {"localhost", "localhost.localdomain"} or normalized.endswith(".local"):
        raise ValidationError("لینک‌های شبکه داخلی قابل تحلیل نیستند.")
    try:
        rows = socket.getaddrinfo(normalized, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise TransientLinkAnalysisError("دامنه لینک موقتاً قابل شناسایی نیست.") from exc
    addresses = {row[4][0] for row in rows if row and row[4]}
    if not addresses:
        raise ValidationError("دامنه لینک آدرس عمومی ندارد.")
    for raw in addresses:
        ip = ipaddress.ip_address(raw.split("%", 1)[0])
        if any((ip.is_private, ip.is_loopback, ip.is_link_local, ip.is_multicast, ip.is_reserved, ip.is_unspecified)):
            raise ValidationError("لینک به آدرس خصوصی یا رزروشده اشاره می‌کند.")


def normalize_public_url(raw_url: str, *, resolve_dns: bool = True) -> str:
    value = (raw_url or "").strip()
    if not value:
        raise ValidationError("لینک محصول را وارد کنید.")
    if "://" not in value:
        value = "https://" + value
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValidationError("فقط لینک‌های عمومی HTTP و HTTPS پذیرفته می‌شوند.")
    if parsed.username or parsed.password:
        raise ValidationError("لینک دارای نام کاربری یا رمز قابل قبول نیست.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValidationError("پورت لینک معتبر نیست.") from exc
    if port not in ALLOWED_PORTS:
        raise ValidationError("فقط پورت‌های عمومی وب قابل تحلیل هستند.")
    if resolve_dns:
        _assert_public_host(parsed.hostname)
    host = _normalize_host(parsed.hostname)
    netloc = host
    if port and port not in {80, 443}:
        netloc = f"{host}:{port}"
    path = parsed.path or "/"
    if host.endswith("printables.com"):
        parts = [part for part in path.split("/") if part]
        if len(parts) >= 3 and parts[0] == "model" and parts[-1] in {"related", "files", "makes", "comments"}:
            path = "/" + "/".join(parts[:-1])
    return urllib.parse.urlunsplit((parsed.scheme.lower(), netloc, path, parsed.query, ""))


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url = normalize_public_url(urllib.parse.urljoin(req.full_url, newurl))
        return super().redirect_request(req, fp, code, msg, headers, safe_url)


def _safe_fetch(url: str, *, max_bytes: int, accept: str, timeout: int = 20) -> tuple[bytes, str, str]:
    safe_url = normalize_public_url(url)
    opener = urllib.request.build_opener(_SafeRedirectHandler())
    request = urllib.request.Request(
        safe_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept,
            "Accept-Language": "fa,en-US;q=0.8,en;q=0.6",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with opener.open(request, timeout=max(5, min(timeout, 45))) as response:  # nosec B310 - URL and redirects are validated
            final_url = normalize_public_url(response.geturl())
            content_type = response.headers.get_content_type()
            payload = response.read(max_bytes + 1)
    except urllib.error.HTTPError as exc:
        status_code = int(getattr(exc, "code", 0) or 0)
        message = f"دریافت لینک با کد HTTP {status_code} ناموفق بود."
        if status_code in {408, 425, 429, 500, 502, 503, 504}:
            raise TransientLinkAnalysisError(message) from exc
        raise PermanentLinkAnalysisError(message) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise TransientLinkAnalysisError(f"دریافت لینک موقتاً ناموفق بود: {exc}") from exc
    if len(payload) > max_bytes:
        raise ValidationError("حجم پاسخ لینک بیشتر از سقف مجاز است.")
    return payload, content_type, final_url


def _page_text(raw_html: str) -> str:
    cleaned = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw_html, flags=re.I | re.S)
    cleaned = re.sub(r"<style\b[^>]*>.*?</style>", " ", cleaned, flags=re.I | re.S)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:100_000]


def _detect_material(text: str) -> str:
    normalized = f" {str(text or '').lower()} "
    for label, aliases in MATERIAL_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return label
    return ""


def _material_match(name: str) -> Material | None:
    if not name:
        return None
    candidates = Material.objects.filter(is_active=True)
    direct = candidates.filter(name__iexact=name).first()
    if direct:
        return direct
    normalized = name.lower().replace("-", " ")
    for material in candidates.order_by("sort_order", "name"):
        material_name = material.name.lower().replace("-", " ")
        if normalized in material_name or material_name in normalized:
            return material
    return None


def _extract_dimensions(text: str) -> str:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(mm|cm|in|inch|میلی\s*متر|سانتی\s*متر)",
        r"(\d+(?:\.\d+)?)\s*(mm|cm)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(mm|cm)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(mm|cm)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return " × ".join(part for part in match.groups() if part)[:120]
    return ""


def _candidate_numeric(values: list[Any], parser) -> tuple[Decimal | None, int | None]:
    weight = None
    minutes = None
    for value in values:
        if weight is None:
            parsed_weight = parse_weight_grams(value)
            if parsed_weight:
                weight = Decimal(str(parsed_weight)).quantize(Decimal("0.01"))
        if minutes is None:
            parsed_minutes = parse_duration_minutes(value)
            if parsed_minutes:
                minutes = int(parsed_minutes)
        if weight is not None and minutes is not None:
            break
    return weight, minutes


WEIGHT_DENSITY_G_CM3 = {
    "PLA": Decimal("1.24"), "PETG": Decimal("1.27"), "ABS": Decimal("1.04"),
    "ASA": Decimal("1.07"), "TPU": Decimal("1.20"), "PA": Decimal("1.15"),
    "PC": Decimal("1.20"), "PPS": Decimal("1.35"), "PCTG": Decimal("1.23"),
}


def _extract_contextual_weight(text: str) -> Decimal | None:
    normalized = normalize_text(text or "").lower().replace(",", "")
    labels = r"(?:filament(?:\s+used|\s+weight|\s+usage)?|material(?:\s+weight|\s+used)?|plastic\s+weight|model\s+weight|print\s+weight|وزن(?:\s+فیلامنت|\s+مدل|\s+قطعه)?|مصرف\s+فیلامنت)"
    patterns = [
        labels + r"[^0-9]{0,50}(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms|g|gram|grams|گرم|کیلوگرم)\b",
        r"(\d+(?:\.\d+)?)\s*(kg|kilogram|kilograms|g|gram|grams|گرم|کیلوگرم)\b[^\n]{0,45}" + labels,
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, re.I)
        if not match:
            continue
        amount = Decimal(match.group(1))
        unit = match.group(2)
        if unit in {"kg", "kilogram", "kilograms", "کیلوگرم"}:
            amount *= Decimal("1000")
        if Decimal("0") < amount < Decimal("100000"):
            return amount.quantize(Decimal("0.01"))
    return None


def _estimate_weight_from_filament_length(text: str, material_name: str) -> Decimal | None:
    normalized = normalize_text(text or "").lower().replace(",", "")
    match = re.search(
        r"(?:filament(?:\s+used|\s+length)|material\s+length|طول\s+فیلامنت|مصرف\s+فیلامنت)"
        r"[^0-9]{0,45}(\d+(?:\.\d+)?)\s*(mm|cm|m|meter|meters|متر|میلی\s*متر|سانتی\s*متر)\b",
        normalized,
        re.I,
    )
    if not match:
        return None
    length = Decimal(match.group(1))
    unit = match.group(2)
    if unit in {"m", "meter", "meters", "متر"}:
        length_mm = length * Decimal("1000")
    elif unit in {"cm", "سانتی متر", "سانتی‌متر"}:
        length_mm = length * Decimal("10")
    else:
        length_mm = length
    diameter_match = re.search(r"(?:filament\s+diameter|قطر\s+فیلامنت)[^0-9]{0,30}(1\.75|2\.85|3(?:\.0)?)\s*mm", normalized)
    diameter_mm = Decimal(diameter_match.group(1)) if diameter_match else Decimal("1.75")
    label = (material_name or "PLA").upper().replace("-CF", "").replace(" CF", "")
    density = next((value for key, value in WEIGHT_DENSITY_G_CM3.items() if key in label), Decimal("1.24"))
    radius = diameter_mm / Decimal("2")
    volume_cm3 = Decimal(str(math.pi)) * radius * radius * length_mm / Decimal("1000")
    grams = volume_cm3 * density
    if Decimal("0.1") < grams < Decimal("100000"):
        return grams.quantize(Decimal("0.01"))
    return None


def _extract_contextual_duration(text: str) -> int | None:
    normalized = normalize_text(text or "").lower().replace(",", "")
    labels = r"(?:print(?:ing)?\s*time|estimated\s+print\s*time|slicer\s*time|زمان\s+چاپ|مدت\s+چاپ)"
    patterns = [
        labels + r"[^0-9]{0,45}(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?|min|m|ساعت|دقیقه)\b",
        r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?|min|m|ساعت|دقیقه)\b[^\n]{0,40}" + labels,
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, re.I)
        if match:
            return int(parse_duration_minutes(f"{match.group(1)} {match.group(2)}") or 0) or None
    return None


def _extract_labeled_print_specs(specs: dict[str, Any]) -> tuple[Decimal | None, int | None]:
    """Read only values whose own label explicitly means print weight/time."""
    weight = None
    minutes = None
    for raw_label, raw_value in (specs or {}).items():
        label = normalize_text(raw_label).lower().replace("_", " ").replace("-", " ")
        if weight is None and re.search(
            r"(?:filament|material|model|print|part|plastic)\s*(?:used\s*)?weight|"
            r"(?:وزن\s*(?:فیلامنت|مدل|قطعه)?|مصرف\s*وزنی\s*فیلامنت)",
            label,
            re.I,
        ):
            value = parse_weight_grams(raw_value)
            if value:
                weight = Decimal(str(value)).quantize(Decimal("0.01"))
        if minutes is None and re.search(
            r"(?:print(?:ing)?|slicer)\s*(?:estimated\s*)?(?:time|duration)|"
            r"(?:زمان|مدت)\s*چاپ",
            label,
            re.I,
        ):
            value = parse_duration_minutes(raw_value)
            if value:
                minutes = int(value)
    return weight, minutes


def billable_print_minutes(actual_minutes: int | Decimal, pricing: PricingSetting | None = None) -> int:
    pricing = pricing or PricingSetting.load()
    actual = max(int(actual_minutes or 0), 0)
    minimum = max(int(pricing.minimum_billable_minutes or 1), 1)
    increment = max(int(pricing.billing_increment_minutes or 1), 1)
    if actual <= 0:
        return 0
    rounded = int(math.ceil(actual / increment) * increment)
    return max(minimum, rounded)


def _extract_image_specs(raw_html: str) -> dict[str, Any]:
    specs: dict[str, Any] = {}
    tags = re.findall(r"<img\b[^>]*>", raw_html or "", re.I)
    if tags:
        specs["image_count_detected"] = len(tags)
    alts: list[str] = []
    dimensions: list[str] = []
    for tag in tags[:40]:
        alt_match = re.search(r'\balt=["\']([^"\']+)["\']', tag, re.I)
        if alt_match:
            alt = normalize_text(alt_match.group(1))
            if alt and alt not in alts:
                alts.append(alt[:180])
        width_match = re.search(r'\bwidth=["\']?(\d{2,5})', tag, re.I)
        height_match = re.search(r'\bheight=["\']?(\d{2,5})', tag, re.I)
        if width_match and height_match:
            value = f"{width_match.group(1)}×{height_match.group(1)} px"
            if value not in dimensions:
                dimensions.append(value)
    if alts:
        specs["image_alt_samples"] = alts[:8]
    if dimensions:
        specs["image_dimension_samples"] = dimensions[:8]
    return specs


def _cache_primary_image(analysis: CustomerLinkAnalysis) -> None:
    if analysis.cached_image or not analysis.image_url:
        return
    try:
        payload, content_type, final_url = _safe_fetch(
            analysis.image_url,
            max_bytes=MAX_IMAGE_BYTES,
            accept="image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            timeout=18,
        )
        if not content_type.startswith("image/"):
            return
        suffix = mimetypes.guess_extension(content_type) or Path(urllib.parse.urlsplit(final_url).path).suffix or ".jpg"
        filename = f"link-{analysis.public_token.hex[:16]}{suffix}"
        analysis.cached_image.save(filename, ContentFile(payload), save=False)
    except Exception as exc:
        warnings = list(analysis.analysis_warnings or [])
        warnings.append(f"ذخیره تصویر محلی ممکن نشد: {exc}")
        analysis.analysis_warnings = warnings[-20:]


def calculate_link_estimate(analysis: CustomerLinkAnalysis, *, save: bool = True) -> CustomerLinkAnalysis:
    if not analysis.has_authoritative_pricing_inputs:
        analysis.estimated_price = 0
        analysis.estimated_price_min = 0
        analysis.estimated_price_max = 0
        analysis.estimate_confidence = Decimal("0")
        analysis.estimate_breakdown = {}
        if save:
            analysis.save(update_fields=[
                "estimated_price", "estimated_price_min", "estimated_price_max",
                "estimate_confidence", "estimate_breakdown", "updated_at",
            ])
        return analysis

    pricing = PricingSetting.load()
    material = analysis.material
    sale_per_gram = Decimal(
        getattr(material, "public_sale_price_per_gram", 0)
        or getattr(material, "effective_sale_price_per_gram", 0)
        or getattr(material, "sale_price_per_gram", 0)
        or getattr(material, "price_per_gram", 0)
        or (Decimal(getattr(material, "price_per_kg", 0) or 0) / Decimal("1000"))
    )
    quantity = max(int(analysis.quantity or 1), 1)
    weight = Decimal(analysis.estimated_weight_grams)
    actual_minutes = int(analysis.estimated_print_minutes)
    billable_minutes = billable_print_minutes(actual_minutes, pricing)
    minutes = Decimal(billable_minutes)
    material_cost = sale_per_gram * weight * quantity
    machine_cost = Decimal(pricing.default_hourly_rate) * minutes / Decimal("60") * quantity
    labor_cost = (material_cost + machine_cost) * Decimal(pricing.default_labor_percent) / Decimal("100")
    packaging = Decimal(pricing.packaging_fee or 0)
    subtotal = material_cost + machine_cost + labor_cost + packaging
    minimum_order = Decimal(pricing.minimum_order_amount or 0)
    minimum_adjustment = max(minimum_order - subtotal, Decimal("0"))
    total = subtotal + minimum_adjustment

    if analysis.pricing_locked:
        confidence = Decimal("100")
        tolerance = Decimal("0")
    else:
        confidence = Decimal("35")
        confidence += Decimal("25") if analysis.estimated_weight_grams else 0
        confidence += Decimal("25") if analysis.estimated_print_minutes else 0
        confidence += Decimal("10") if analysis.detected_material_name else Decimal("5")
        confidence = min(confidence, Decimal("95"))
        tolerance = Decimal("12") if confidence >= 85 else (Decimal("20") if confidence >= 65 else Decimal("30"))

    rounded_total = int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    price_min = int((total * (Decimal("1") - tolerance / Decimal("100"))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    price_max = int((total * (Decimal("1") + tolerance / Decimal("100"))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    analysis.estimated_price = rounded_total
    analysis.estimated_price_min = max(price_min, 0)
    analysis.estimated_price_max = max(price_max, rounded_total)
    analysis.estimate_confidence = confidence
    analysis.estimate_breakdown = {
        "currency": "تومان",
        "quantity": quantity,
        "material": material.name,
        "material_sale_per_gram": str(sale_per_gram.quantize(Decimal("0.01"))),
        "material_cost": int(material_cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "machine_hourly_rate": int(pricing.default_hourly_rate),
        "actual_print_minutes": actual_minutes,
        "billable_print_minutes": billable_minutes,
        "minimum_billable_minutes": int(pricing.minimum_billable_minutes),
        "billing_increment_minutes": int(pricing.billing_increment_minutes),
        "machine_cost": int(machine_cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "labor_percent": str(pricing.default_labor_percent),
        "labor_cost": int(labor_cost.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "packaging": int(packaging),
        "minimum_order_adjustment": int(minimum_adjustment.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "subtotal": int(subtotal.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
        "total": rounded_total,
        "tolerance_percent": str(tolerance),
        "pricing_locked": bool(analysis.pricing_locked),
    }
    if save:
        analysis.save(update_fields=[
            "estimated_price", "estimated_price_min", "estimated_price_max",
            "estimate_confidence", "estimate_breakdown", "updated_at",
        ])
    return analysis


def _analyze_direct_file_reference(analysis: CustomerLinkAnalysis, safe_url: str) -> CustomerLinkAnalysis | None:
    suffix = Path(urllib.parse.urlsplit(safe_url).path).suffix.lower()
    if suffix not in FILE_EXTENSIONS:
        return None
    filename = urllib.parse.unquote(Path(urllib.parse.urlsplit(safe_url).path).name)
    title = re.sub(r"[-_]+", " ", Path(filename).stem).strip() or "فایل سه‌بعدی"
    domain = urllib.parse.urlsplit(safe_url).hostname or ""
    analysis.normalized_url = safe_url
    analysis.source_domain = domain[:255]
    analysis.source_name = domain.removeprefix("www.")[:255]
    analysis.title = title[:300]
    analysis.short_description = "لینک مستقیم فایل سه‌بعدی توسط مشتری ثبت شده است؛ مشخصات چاپ باید تکمیل شود."
    analysis.file_formats = [suffix.lstrip(".").upper()]
    analysis.file_links = [safe_url]
    analysis.source_payload = {"final_url": safe_url, "direct_file_reference": True}
    analysis.analysis_warnings = [
        "برای حفظ امنیت و کنترل حجم، فایل در مرحله تحلیل خودکار دانلود نشد.",
        "وزن، زمان چاپ و متریال باید پس از بررسی فایل یا توسط مشتری تکمیل شود.",
    ]
    analysis.status = "needs_input"
    analysis.analyzed_at = timezone.now()
    analysis.save()
    return analysis


def _apply_verified_catalog_snapshot(analysis: CustomerLinkAnalysis, asset: ImportedPrintAsset) -> CustomerLinkAnalysis | None:
    try:
        review = asset.pricing_review
    except Exception:
        return None
    if not review.is_complete:
        return None
    specs = dict(asset.technical_specs or {})
    specs.update({
        "weight_source_kind": "operator_verified",
        "print_time_source_kind": "operator_verified",
        "operator_pricing_review_id": review.pk,
        "catalog_snapshot_used": True,
    })
    analysis.normalized_url = asset.source_url
    analysis.source_domain = urllib.parse.urlsplit(asset.source_url).hostname or analysis.source_domain
    analysis.source_name = asset.source.name
    analysis.title = asset.title
    analysis.short_description = asset.short_description
    analysis.description = asset.description
    analysis.author_name = asset.author_name
    analysis.image_url = asset.catalog_image_url
    analysis.image_urls = list(asset.metrics.image_urls or ([asset.catalog_image_url] if asset.catalog_image_url else []))
    analysis.tags = [item.strip() for item in re.split(r"[,;|]", asset.tags or "") if item.strip()]
    analysis.technical_specs = specs
    analysis.file_formats = list(asset.metrics.file_formats or ([asset.file_format] if asset.file_format else []))
    analysis.file_links = list(asset.metrics.file_links or [])
    analysis.detected_material_name = review.material.name
    analysis.material = review.material
    analysis.estimated_weight_grams = review.weight_grams
    analysis.estimated_print_minutes = review.print_minutes
    analysis.related_asset = asset
    analysis.status = "ready"
    analysis.error_message = ""
    analysis.analyzed_at = timezone.now()
    analysis.analysis_warnings = ["قیمت‌گذاری از مشخصات تأییدشده اپراتور و نرخ روز متریال انجام شد."]
    analysis.save()
    calculate_link_estimate(analysis)
    if review.price_override:
        quantity = max(int(analysis.quantity or 1), 1)
        final_price = int(review.price_override) * quantity
        analysis.estimated_price = final_price
        analysis.estimated_price_min = final_price
        analysis.estimated_price_max = final_price
        analysis.estimate_confidence = Decimal("100")
        breakdown = dict(analysis.estimate_breakdown or {})
        breakdown.update({"operator_price_override": int(review.price_override), "total": final_price, "pricing_locked": True})
        analysis.estimate_breakdown = breakdown
        analysis.save(update_fields=[
            "estimated_price", "estimated_price_min", "estimated_price_max",
            "estimate_confidence", "estimate_breakdown", "updated_at",
        ])
    return analysis


def analyze_customer_link(
    analysis: CustomerLinkAnalysis,
    *,
    progress_callback: ProgressCallback | None = None,
    raise_errors: bool = False,
    request_timeout_seconds: int = 20,
    cache_remote_images: bool = True,
) -> CustomerLinkAnalysis:
    _notify_progress(progress_callback, 2, "starting", "آماده‌سازی تحلیل لینک")
    analysis.status = "processing"
    analysis.error_message = ""
    analysis.save(update_fields=["status", "error_message", "updated_at"])
    try:
        _notify_progress(progress_callback, 8, "validating", "اعتبارسنجی امنیتی آدرس و دامنه")
        safe_source_url = normalize_public_url(analysis.source_url)
        direct_result = _analyze_direct_file_reference(analysis, safe_source_url)
        if direct_result is not None:
            _notify_progress(progress_callback, 100, "completed", "لینک مستقیم فایل ثبت شد؛ مشخصات چاپ باید تکمیل شود")
            return direct_result
        verified_asset = (
            ImportedPrintAsset.objects.select_related(
                "source", "metrics", "pricing_review", "pricing_review__material"
            ).filter(source_url=safe_source_url).first()
        )
        verified_result = _apply_verified_catalog_snapshot(analysis, verified_asset) if verified_asset else None
        if verified_result is not None:
            _notify_progress(progress_callback, 100, "completed", "مشخصات قطعی آرشیو داخلی و قیمت روز بازیابی شد")
            return verified_result
        _notify_progress(progress_callback, 18, "fetching", "دریافت امن صفحه منبع")
        payload, content_type, final_url = _safe_fetch(
            analysis.source_url,
            max_bytes=MAX_HTML_BYTES,
            accept="text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
            timeout=max(5, min(int(request_timeout_seconds or 20), 45)),
        )
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValidationError("لینک ارسالی یک صفحه HTML قابل تحلیل نیست.")
        _notify_progress(progress_callback, 34, "parsing", "استخراج عنوان، توضیحات و داده‌های ساختاریافته")
        html = payload.decode("utf-8", errors="replace")
        parsed = parse_print_page(html, final_url)
        parser = PageMetadataParser()
        parser.feed(html)
        rich_parser = parse_html_document(html)
        rich_blobs = extract_json_blobs(html)
        visible_text = _page_text(html)
        source_domain = urllib.parse.urlsplit(final_url).hostname or ""
        source_name = (
            parser.meta.get("og:site_name")
            or rich_parser.metas.get("og:site_name")
            or source_domain.removeprefix("www.")
        )

        rich_title = best_title(rich_parser, rich_blobs)
        rich_description = best_description(rich_parser, rich_blobs)
        if (not parsed.get("title") or parsed.get("title") == "فایل آماده چاپ بدون عنوان") and rich_title:
            parsed["title"] = rich_title
        if not parsed.get("description") and rich_description:
            parsed["description"] = rich_description
            parsed["short_description"] = rich_description[:500]

        _notify_progress(progress_callback, 50, "media", "شناسایی تصاویر و لینک‌های فایل")
        image_urls = unique_urls([
            *(parsed.get("images", []) or []),
            *best_images(rich_parser, rich_blobs, final_url),
        ], final_url)[:20]
        all_links = [urllib.parse.urljoin(final_url, href) for href in [*parser.links, *rich_parser.links]]
        file_links = []
        for url in all_links:
            suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
            if suffix in FILE_EXTENSIONS and url.startswith(("http://", "https://")) and url not in file_links:
                file_links.append(url)
        blob_file_values = all_values(
            rich_blobs,
            ["downloadUrl", "contentUrl", "fileUrl", "fileURL", "filename", "fileName", "files", "modelUrl"],
        )
        for url in unique_urls(blob_file_values, final_url):
            suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
            if suffix in FILE_EXTENSIONS and url not in file_links:
                file_links.append(url)
        if parsed.get("download_url") and parsed["download_url"] not in file_links:
            file_links.insert(0, parsed["download_url"])
        file_formats = extract_file_formats([*file_links, *blob_file_values, parsed.get("file_format"), visible_text])

        specs = dict(parsed.get("technical_specs") or {})
        for key, value in _extract_image_specs(html).items():
            specs.setdefault(key, value)
        for alias, label in (
            ("dimensions", "dimensions"),
            ("layerHeight", "layer_height"),
            ("infill", "infill"),
            ("nozzle", "nozzle"),
            ("printer", "printer"),
            ("category", "category"),
        ):
            value = first_value(rich_blobs, [alias], "")
            if value not in (None, "") and label not in specs:
                specs[label] = normalize_text(value)[:300]
        labeled_weight, labeled_minutes = _extract_labeled_print_specs(specs)
        explicit_weight_values = all_values(
            rich_blobs,
            [
                "filamentWeight", "filamentWeightGrams", "filamentUsedWeight", "materialWeight",
                "materialWeightGrams", "weightGrams", "modelWeight", "printWeight", "plasticWeight",
                "estimatedWeightGrams", "totalFilamentWeight", "slicedModelWeight",
            ],
        )
        explicit_time_values = all_values(
            rich_blobs,
            ["printTime", "printingTime", "printDuration", "estimatedPrintTime", "slicerTime", "printingDuration"],
        )
        weight = labeled_weight or next((Decimal(str(value)).quantize(Decimal("0.01")) for raw in explicit_weight_values
                       if (value := parse_weight_grams(raw))), None)
        minutes = labeled_minutes or next((int(value) for raw in explicit_time_values
                        if (value := parse_duration_minutes(raw))), None)
        weight_source = "source_explicit" if weight is not None else "unknown"
        time_source = "source_explicit" if minutes is not None else "unknown"
        if weight is None:
            weight = _extract_contextual_weight(visible_text)
            if weight is not None:
                weight_source = "source_explicit"
        if minutes is None:
            minutes = _extract_contextual_duration(visible_text)
            if minutes is not None:
                time_source = "source_explicit"
        tags_raw = parsed.get("tags") or first_value(rich_blobs, ["keywords", "tags", "tagNames"], "") or ""
        if isinstance(tags_raw, (list, tuple, set)):
            tags = [normalize_text(item.get("name") if isinstance(item, dict) else item) for item in tags_raw]
            tags = [item for item in tags if item][:50]
        else:
            tags = [item.strip() for item in re.split(r"[,;|]", str(tags_raw)) if item.strip()][:50]
        author_value = first_value(rich_blobs, ["author", "creator", "designer", "seller", "username"], "")
        if isinstance(author_value, dict):
            rich_author = normalize_text(author_value.get("name") or author_value.get("username") or author_value.get("displayName"))
        else:
            rich_author = normalize_text(author_value)
        combined = " ".join([
            parsed.get("title") or "",
            parsed.get("description") or "",
            " ".join(tags),
            " ".join(str(value) for value in specs.values()),
        ])
        material_name = _detect_material(combined)
        material = _material_match(material_name)
        if weight is None:
            weight = _estimate_weight_from_filament_length(visible_text, material_name)
            if weight is not None:
                weight_source = "filament_inferred"
                specs.setdefault("weight_estimation_method", "برآورد از طول فیلامنت، قطر ۱.۷۵ میلی‌متر و چگالی تقریبی متریال")
        dimensions = _extract_dimensions(combined + " " + visible_text)
        if dimensions and "dimensions" not in specs:
            specs["dimensions"] = dimensions

        title = (parsed.get("title") or "").strip()
        if not title or title == "فایل آماده چاپ بدون عنوان":
            path_name = urllib.parse.unquote(urllib.parse.urlsplit(final_url).path.rstrip("/").rsplit("/", 1)[-1])
            title = re.sub(r"[-_]+", " ", path_name).strip().title() or source_name

        related_asset = (
            ImportedPrintAsset.objects.select_related("metrics", "source")
            .filter(source_url=final_url)
            .first()
        )
        if related_asset:
            related_metrics = related_asset.metrics
            if not image_urls and related_asset.catalog_image_url:
                image_urls = [related_asset.catalog_image_url]
            if not file_formats:
                file_formats = list(related_metrics.file_formats or [])
            trusted_related = str(related_metrics.estimate_source or "") in {
                "operator_verified", "source_profile", "source_explicit"
            }
            if trusted_related and weight is None:
                weight = related_metrics.estimated_weight_grams
                if weight is not None:
                    weight_source = "operator_verified" if related_metrics.estimate_source == "operator_verified" else "source_profile"
            if trusted_related and minutes is None:
                minutes = related_metrics.estimated_print_minutes
                if minutes is not None:
                    time_source = "operator_verified" if related_metrics.estimate_source == "operator_verified" else "source_profile"
            if not specs:
                specs = dict(related_asset.technical_specs or {})
            if not tags and related_asset.tags:
                tags = [item.strip() for item in re.split(r"[,;|]", related_asset.tags) if item.strip()][:50]
            if not material_name:
                material_name = _detect_material(" ".join([related_asset.title, related_asset.description, related_asset.tags]))
                material = _material_match(material_name)
            if not title or title == "فایل آماده چاپ بدون عنوان":
                title = related_asset.title

        _notify_progress(progress_callback, 68, "normalizing", "یکپارچه‌سازی مشخصات قابل استفاده")
        analysis.normalized_url = final_url
        analysis.source_domain = source_domain[:255]
        analysis.source_name = source_name[:255]
        analysis.title = title[:300]
        analysis.short_description = str(parsed.get("short_description") or "")[:700]
        analysis.description = str(parsed.get("description") or "")
        analysis.author_name = str(parsed.get("author_name") or rich_author or "")[:220]
        analysis.image_urls = image_urls
        analysis.image_url = image_urls[0] if image_urls else ""
        analysis.tags = tags
        analysis.technical_specs = specs
        analysis.file_formats = file_formats
        analysis.file_links = file_links[:100]
        specs["weight_source_kind"] = weight_source
        specs["print_time_source_kind"] = time_source
        analysis.source_payload = {
            "json_ld": parsed.get("raw_json_ld") or {},
            "embedded_json_objects": len(rich_blobs),
            "content_type": content_type,
            "final_url": final_url,
            "has_download_reference": bool(file_links),
            "weight_source": weight_source,
            "print_time_source": time_source,
            "image_count": len(image_urls),
        }
        analysis.detected_material_name = material_name
        analysis.material = material
        analysis.estimated_weight_grams = weight
        analysis.estimated_print_minutes = minutes
        analysis.related_asset = related_asset
        analysis.analysis_warnings = []
        if not image_urls:
            analysis.analysis_warnings.append("تصویر قابل استفاده از صفحه استخراج نشد.")
        if not file_links:
            analysis.analysis_warnings.append("لینک مستقیم فایل سه‌بعدی پیدا نشد؛ صفحه منبع همچنان برای بررسی حفظ شد.")
        if weight is None:
            analysis.analysis_warnings.append("وزن مدل از صفحه قابل استخراج نبود.")
        elif weight_source == "filament_inferred":
            analysis.analysis_warnings.append("وزن از طول فیلامنت و چگالی تقریبی متریال برآورد شده و باید پیش از پرداخت نهایی تأیید شود.")
        if minutes is None:
            analysis.analysis_warnings.append("زمان چاپ از صفحه قابل استخراج نبود.")
        if material is None:
            analysis.analysis_warnings.append("متریال قابل تطبیق با فهرست متریال‌های سایت پیدا نشد.")
        analysis.status = "ready" if analysis.has_authoritative_pricing_inputs else ("needs_input" if title else "partial")
        analysis.analyzed_at = timezone.now()
        _notify_progress(progress_callback, 80, "saving", "ذخیره اطلاعات استخراج‌شده")
        analysis.save()

        # Image caching is optional. A broken or blocked remote image must not
        # turn a successfully parsed product page into a failed analysis.
        _notify_progress(progress_callback, 87, "image", "ذخیره نسخه محلی تصویر اصلی در صورت امکان")
        try:
            if cache_remote_images:
                _cache_primary_image(analysis)
        except Exception as image_cache_error:
            warnings = list(analysis.analysis_warnings or [])
            warnings.append(f"ذخیره تصویر محلی ممکن نشد: {image_cache_error}")
            analysis.analysis_warnings = warnings[-20:]
            analysis.cached_image = None
        try:
            image_update_fields = ["analysis_warnings", "updated_at"]
            if analysis.cached_image:
                image_update_fields.insert(0, "cached_image")
            analysis.save(update_fields=image_update_fields)
        except Exception as image_save_error:
            warnings = list(analysis.analysis_warnings or [])
            warnings.append(f"ثبت تصویر محلی ممکن نشد: {image_save_error}")
            analysis.analysis_warnings = warnings[-20:]
            analysis.cached_image = None
            analysis.save(update_fields=["analysis_warnings", "updated_at"])

        _notify_progress(progress_callback, 94, "estimating", "محاسبه برآورد قیمت بر اساس اطلاعات موجود")
        calculate_link_estimate(analysis)
        if not analysis.has_authoritative_pricing_inputs:
            from .manual_review import ensure_manual_review
            from .operator_notifications import notify_manual_review
            review, _ = ensure_manual_review(analysis=analysis, job=None, reason="incomplete_data", customer_note="وزن یا زمان چاپ معتبر از منبع دریافت نشد؛ قیمت‌گذاری اپراتور لازم است.")
            notify_manual_review(review)
        _notify_progress(progress_callback, 100, "completed", "تحلیل لینک تکمیل شد")
        return analysis
    except Exception as exc:
        analysis.status = "failed"
        analysis.error_message = str(exc)
        analysis.analyzed_at = timezone.now()
        analysis.save(update_fields=["status", "error_message", "analyzed_at", "updated_at"])
        _notify_progress(progress_callback, 100, "failed", "تحلیل لینک ناموفق بود")
        if raise_errors:
            raise
        return analysis


def analysis_owned_by(analysis: CustomerLinkAnalysis, request) -> bool:
    if request.user.is_authenticated:
        if request.user.is_staff or analysis.user_id == request.user.id:
            return True
        pending_token = str(request.session.get("pending_link_analysis_token") or "")
        same_session = bool(analysis.session_key and analysis.session_key == request.session.session_key)
        if analysis.user_id is None and (same_session or pending_token == str(analysis.public_token)):
            analysis.user = request.user
            analysis.save(update_fields=["user", "updated_at"])
            if pending_token == str(analysis.public_token):
                request.session.pop("pending_link_analysis_token", None)
            return True
        return False
    return bool(analysis.session_key and analysis.session_key == request.session.session_key)


@transaction.atomic
def create_order_from_analysis(
    analysis: CustomerLinkAnalysis,
    *,
    user,
    full_name: str,
    phone: str,
) -> Order:
    if not user or not user.is_authenticated:
        raise PermissionDenied("برای ادامه سفارش باید وارد حساب کاربری شوید.")
    if analysis.user_id and analysis.user_id != user.id and not user.is_staff:
        raise PermissionDenied("این تحلیل متعلق به حساب شما نیست.")
    calculate_link_estimate(analysis)
    if not analysis.can_estimate or not analysis.estimated_price:
        raise ValidationError("برای ساخت پیش‌فاکتور باید متریال، وزن و زمان چاپ مشخص باشند.")
    if analysis.order_id:
        return analysis.order

    parts = [part for part in (full_name or "").strip().split() if part]
    first_name = parts[0] if parts else (user.first_name or "مشتری")
    last_name = " ".join(parts[1:]) if len(parts) > 1 else (user.last_name or "")
    from website.models import SiteSetting
    pricing = PricingSetting.load()
    site_settings = SiteSetting.objects.first()
    deposit_percent = Decimal(str(getattr(site_settings, "default_deposit_percent", 30) or 30))
    breakdown = analysis.estimate_breakdown or {}
    order = Order.objects.create(
        customer=user,
        first_name=first_name[:100],
        last_name=last_name[:100],
        phone=phone[:20],
        service_type="3d_print",
        material=analysis.material,
        quantity=max(int(analysis.quantity or 1), 1),
        description=(
            f"سفارش چاپ از لینک خارجی: {analysis.title or analysis.source_name}\n"
            f"منبع: {analysis.normalized_url}\n"
            f"سایت منبع: {analysis.source_name or analysis.source_domain}\n"
            f"فرمت‌های شناسایی‌شده: {', '.join(analysis.file_formats or []) or 'نامشخص'}\n"
            f"توضیحات: {analysis.short_description or analysis.description[:800]}"
        ),
        status="quoted",
    )
    tolerance = Decimal(str(breakdown.get("tolerance_percent") or "20"))
    Quote.objects.create(
        order=order,
        price_tolerance_percent=tolerance,
        material=analysis.material,
        weight_grams=analysis.estimated_weight_grams,
        print_time_minutes=int(analysis.estimated_print_minutes),
        machine_hourly_rate=int(pricing.default_hourly_rate),
        minimum_billable_minutes=int(pricing.minimum_billable_minutes),
        billing_increment_minutes=int(pricing.billing_increment_minutes),
        labor_fee=int(breakdown.get("labor_cost") or 0),
        post_processing_fee=int(breakdown.get("packaging") or 0) + int(breakdown.get("minimum_order_adjustment") or 0),
        customer_note=(
            "وزن و زمان چاپ توسط اپراتور تأیید شده و قیمت بر اساس نرخ روز متریال و پله زمانی تنظیم‌شده محاسبه شده است."
            if analysis.pricing_locked else
            "این مبلغ بر اساس داده صریح صفحه منبع محاسبه شده است و پیش از شروع تولید توسط اپراتور کنترل می‌شود."
        ),
        admin_note=f"Created from CustomerLinkAnalysis #{analysis.pk}: {analysis.normalized_url}",
        status="sent",
        deposit_percent=deposit_percent,
    )
    analysis.user = user
    analysis.order = order
    analysis.status = "converted"
    analysis.save(update_fields=["user", "order", "status", "updated_at"])
    return order


@transaction.atomic
def create_manual_quote_request_from_analysis(
    analysis: CustomerLinkAnalysis,
    *,
    user,
    full_name: str,
    phone: str,
    quantity: int = 1,
    desired_material=None,
    customer_note: str = "",
) -> Order:
    if not user or not user.is_authenticated:
        raise PermissionDenied("برای درخواست قیمت باید وارد حساب کاربری شوید.")
    if analysis.user_id and analysis.user_id != user.id and not user.is_staff:
        raise PermissionDenied("این تحلیل متعلق به حساب شما نیست.")
    if analysis.order_id:
        return analysis.order

    from website.models import SiteSetting

    parts = [part for part in (full_name or "").strip().split() if part]
    first_name = parts[0] if parts else (user.first_name or "مشتری")
    last_name = " ".join(parts[1:]) if len(parts) > 1 else (user.last_name or "")
    quantity = max(int(quantity or 1), 1)
    chosen_material = desired_material or analysis.material
    settings_row = SiteSetting.objects.first()
    deposit_percent = Decimal(str(getattr(settings_row, "default_deposit_percent", 30) or 30))
    pricing = PricingSetting.load()
    note = (customer_note or "").strip()

    order = Order.objects.create(
        customer=user,
        first_name=first_name[:100],
        last_name=last_name[:100],
        phone=phone[:20],
        service_type="3d_print",
        material=chosen_material,
        quantity=quantity,
        description=(
            f"درخواست قیمت دستی برای لینک خارجی: {analysis.title or analysis.source_name or analysis.source_domain}\n"
            f"منبع: {analysis.normalized_url}\n"
            f"وضعیت تحلیل: {analysis.get_status_display()}\n"
            f"وزن استخراج‌شده: {analysis.estimated_weight_grams or 'نامشخص'} گرم\n"
            f"زمان چاپ استخراج‌شده: {analysis.estimated_print_minutes or 'نامشخص'} دقیقه\n"
            f"توضیحات مشتری: {note or 'ثبت نشده'}"
        ),
        status="reviewing",
    )
    Quote.objects.create(
        order=order,
        material=chosen_material,
        weight_grams=analysis.estimated_weight_grams or 0,
        print_time_minutes=int(analysis.estimated_print_minutes or 0),
        machine_hourly_rate=int(pricing.default_hourly_rate),
        minimum_billable_minutes=int(pricing.minimum_billable_minutes),
        billing_increment_minutes=int(pricing.billing_increment_minutes),
        customer_note="درخواست شما برای قیمت‌گذاری کارشناسی ثبت شده است. مبلغ و بیعانه پس از بررسی فایل یا لینک اعلام می‌شود.",
        admin_note=f"Manual quote from CustomerLinkAnalysis #{analysis.pk}: {analysis.normalized_url}\nCustomer note: {note}",
        status="draft",
        deposit_percent=deposit_percent,
    )
    analysis.user = user
    analysis.order = order
    analysis.save(update_fields=["user", "order", "updated_at"])
    from .manual_review import ensure_manual_review
    from .operator_notifications import notify_manual_review
    review, _ = ensure_manual_review(
        analysis=analysis,
        requested_by=user,
        reason="customer_request",
        customer_note=note or "مشتری درخواست قیمت کارشناسی ثبت کرده است.",
        priority=200,
    )
    transaction.on_commit(lambda review=review: notify_manual_review(review))
    return order


def enqueue_catalog_refresh(asset: ImportedPrintAsset, *, user=None, session_key: str = "", note: str = "") -> CatalogRefreshRequest:
    pending = CatalogRefreshRequest.objects.filter(asset=asset, status__in=["pending", "running"]).first()
    if pending:
        return pending
    return CatalogRefreshRequest.objects.create(
        asset=asset,
        requested_by=user if getattr(user, "is_authenticated", False) else None,
        session_key=session_key or "",
        customer_note=(note or "")[:500],
    )


def process_catalog_refresh_requests(*, limit: int = 5, request_ids=None) -> list[CatalogRefreshRequest]:
    processed: list[CatalogRefreshRequest] = []
    queryset = CatalogRefreshRequest.objects.select_related("asset", "asset__source").filter(status="pending")
    if request_ids is not None:
        queryset = queryset.filter(pk__in=list(request_ids))
    for request_obj in queryset.order_by("requested_at")[: max(int(limit), 1)]:
        claimed = CatalogRefreshRequest.objects.filter(pk=request_obj.pk, status="pending").update(status="running")
        if not claimed:
            continue
        request_obj.status = "running"
        try:
            asset = request_obj.asset
            policy = asset.source.sync_policy
            adapter = get_source_adapter(asset.source, policy)
            parsed = adapter.fetch_record(
                CatalogCandidate(url=asset.source_url, external_id=asset.external_id),
                hydrate_files=True,
            )
            refreshed_asset, _metrics = save_external_record(source=asset.source, policy=policy, parsed=parsed, rank=0)
            request_obj.status = "completed"
            request_obj.result_summary = (
                f"اطلاعات بروزرسانی شد؛ عنوان: {refreshed_asset.title}، "
                f"تصاویر: {len(refreshed_asset.metrics.image_urls or [])}، "
                f"فرمت‌ها: {', '.join(refreshed_asset.metrics.file_formats or []) or 'نامشخص'}"
            )
        except Exception as exc:
            request_obj.status = "failed"
            request_obj.result_summary = f"{type(exc).__name__}: {exc}"
        request_obj.processed_at = timezone.now()
        request_obj.save(update_fields=["status", "result_summary", "processed_at"])
        processed.append(request_obj)
    return processed
