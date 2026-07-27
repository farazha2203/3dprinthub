from __future__ import annotations

import json
import mimetypes
import re
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    ImportedPrintAsset,
    ImportedPrintAssetImage,
    PrintCatalogImportJob,
    PrintCatalogSource,
    Product,
)

USER_AGENT = "3DprintHubCatalogBot/1.0"
MAX_HTML_BYTES = 5 * 1024 * 1024
MAX_IMAGE_BYTES = 12 * 1024 * 1024
FILE_EXTENSIONS = {
    ".stl", ".3mf", ".obj", ".step", ".stp", ".iges", ".igs",
    ".zip", ".rar", ".7z", ".blend", ".fbx", ".gcode",
}


class PageMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.links: list[str] = []
        self.images: list[str] = []
        self.json_ld_chunks: list[str] = []
        self._in_title = False
        self._title_parts: list[str] = []
        self._in_json_ld = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = {str(k).lower(): str(v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (data.get("property") or data.get("name") or data.get("itemprop") or "").lower()
            content = data.get("content", "").strip()
            if key and content:
                self.meta[key] = content
        elif tag == "a" and data.get("href"):
            self.links.append(data["href"].strip())
        elif tag == "img" and (data.get("src") or data.get("data-src")):
            self.images.append((data.get("src") or data.get("data-src") or "").strip())
        elif tag == "script" and "ld+json" in data.get("type", "").lower():
            self._in_json_ld = True
            self._json_parts = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self._in_json_ld = False
            chunk = "".join(self._json_parts).strip()
            if chunk:
                self.json_ld_chunks.append(chunk)
            self._json_parts = []

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)
        if self._in_json_ld:
            self._json_parts.append(data)

    @property
    def title(self):
        return " ".join("".join(self._title_parts).split())


def _flatten_json_ld(value):
    if isinstance(value, list):
        for item in value:
            yield from _flatten_json_ld(item)
    elif isinstance(value, dict):
        graph = value.get("@graph")
        if graph:
            yield from _flatten_json_ld(graph)
        yield value


def _absolute(base_url: str, candidate: str) -> str:
    if not candidate:
        return ""
    return urllib.parse.urljoin(base_url, candidate.strip())


def _first_text(*values):
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_images(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(_extract_images(item))
        return result
    if isinstance(value, dict):
        return _extract_images(value.get("url") or value.get("contentUrl") or "")
    return []


def _file_format(url: str) -> str:
    suffix = Path(urllib.parse.urlparse(url).path).suffix.lower().lstrip(".")
    return suffix.upper() if suffix else ""


def parse_print_page(html: str, page_url: str) -> dict:
    parser = PageMetadataParser()
    parser.feed(html)

    json_objects = []
    for chunk in parser.json_ld_chunks:
        try:
            parsed = json.loads(chunk)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        json_objects.extend(_flatten_json_ld(parsed))

    preferred = None
    for obj in json_objects:
        type_value = obj.get("@type")
        types = type_value if isinstance(type_value, list) else [type_value]
        if any(t in {"Product", "CreativeWork", "3DModel", "DigitalDocument", "Thing"} for t in types):
            preferred = obj
            break
    preferred = preferred or (json_objects[0] if json_objects else {})

    title = _first_text(
        parser.meta.get("og:title"),
        parser.meta.get("twitter:title"),
        preferred.get("name") if isinstance(preferred, dict) else "",
        parser.title,
    )
    description = _first_text(
        parser.meta.get("og:description"),
        parser.meta.get("description"),
        parser.meta.get("twitter:description"),
        preferred.get("description") if isinstance(preferred, dict) else "",
    )

    image_candidates = []
    image_candidates.extend(_extract_images(preferred.get("image") if isinstance(preferred, dict) else None))
    image_candidates.extend([
        parser.meta.get("og:image", ""),
        parser.meta.get("twitter:image", ""),
    ])
    image_candidates.extend(parser.images[:10])
    images = []
    for value in image_candidates:
        url = _absolute(page_url, value)
        if url and url not in images:
            images.append(url)

    download_candidates = []
    if isinstance(preferred, dict):
        for key in ("contentUrl", "downloadUrl", "fileUrl", "url"):
            value = preferred.get(key)
            if isinstance(value, str):
                download_candidates.append(value)
        encoding = preferred.get("encoding")
        if isinstance(encoding, dict):
            for key in ("contentUrl", "url"):
                if encoding.get(key):
                    download_candidates.append(encoding[key])
        elif isinstance(encoding, list):
            for item in encoding:
                if isinstance(item, dict):
                    download_candidates.extend([item.get("contentUrl", ""), item.get("url", "")])
    download_candidates.extend(parser.links)

    download_url = ""
    for value in download_candidates:
        absolute = _absolute(page_url, value)
        suffix = Path(urllib.parse.urlparse(absolute).path).suffix.lower()
        if suffix in FILE_EXTENSIONS:
            download_url = absolute
            break

    author = ""
    license_value = ""
    external_id = ""
    technical_specs = {}
    if isinstance(preferred, dict):
        author_value = preferred.get("author") or preferred.get("creator")
        if isinstance(author_value, dict):
            author = _first_text(author_value.get("name"), author_value.get("url"))
        elif isinstance(author_value, str):
            author = author_value
        license_value = _first_text(preferred.get("license"), preferred.get("usageInfo"))
        external_id = str(preferred.get("sku") or preferred.get("productID") or preferred.get("identifier") or "")
        properties = preferred.get("additionalProperty")
        if isinstance(properties, list):
            for item in properties:
                if isinstance(item, dict) and item.get("name"):
                    technical_specs[str(item["name"])] = item.get("value", "")

    keywords = _first_text(parser.meta.get("keywords"), preferred.get("keywords") if isinstance(preferred, dict) else "")
    return {
        "title": title or "فایل آماده چاپ بدون عنوان",
        "short_description": description[:500],
        "description": description,
        "images": images,
        "download_url": download_url,
        "file_format": _file_format(download_url),
        "author_name": author,
        "license_name": license_value,
        "license_url": license_value if license_value.startswith(("http://", "https://")) else "",
        "external_id": external_id,
        "tags": keywords[:700],
        "technical_specs": technical_specs,
        "raw_json_ld": preferred if isinstance(preferred, dict) else {},
    }


def _source_domains(source: PrintCatalogSource) -> set[str]:
    values = [part.strip().lower() for part in source.allowed_domains.split(",") if part.strip()]
    if not values:
        host = urllib.parse.urlparse(source.base_url).hostname or ""
        if host:
            values = [host.lower()]
    return {value.removeprefix("www.") for value in values}


def validate_source_url(source: PrintCatalogSource, url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValidationError("آدرس منبع معتبر نیست.")
    host = parsed.hostname.lower().lstrip("www.")
    allowed = _source_domains(source)
    if not any(host == domain or host.endswith("." + domain) for domain in allowed):
        raise ValidationError("دامنه آدرس با دامنه‌های مجاز این منبع مطابقت ندارد.")


def _fetch_bytes(source: PrintCatalogSource, url: str, *, max_bytes: int) -> tuple[bytes, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,image/*;q=0.8,*/*;q=0.5"}
    headers.update({str(k): str(v) for k, v in (source.request_headers or {}).items()})
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=source.request_timeout_seconds) as response:
        content_type = response.headers.get_content_type()
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValidationError("حجم پاسخ منبع بیشتر از حد مجاز است.")
    return data, content_type


def _robots_allowed(source: PrintCatalogSource, url: str) -> bool:
    if not source.respect_robots_txt:
        return True
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        data, _content_type = _fetch_bytes(source, robots_url, max_bytes=512 * 1024)
        parser.parse(data.decode("utf-8", errors="replace").splitlines())
    except Exception:
        # A missing or temporarily unavailable robots file is treated as no
        # explicit restriction. Source/domain validation still applies.
        return True
    return parser.can_fetch(USER_AGENT, url)


def _safe_slug(title: str, source_url: str) -> str:
    base = slugify(title, allow_unicode=True)[:220] or "imported-model"
    existing = ImportedPrintAsset.objects.filter(slug=base).exclude(source_url=source_url).exists()
    if not existing:
        return base
    token = abs(hash(source_url)) % 10_000_000
    return f"{base}-{token}"


def _download_image(source: PrintCatalogSource, image_url: str, asset: ImportedPrintAsset, *, gallery=False):
    data, content_type = _fetch_bytes(source, image_url, max_bytes=MAX_IMAGE_BYTES)
    if not content_type.startswith("image/"):
        raise ValidationError("فایل دریافت‌شده تصویر نیست.")
    extension = mimetypes.guess_extension(content_type) or Path(urllib.parse.urlparse(image_url).path).suffix or ".jpg"
    filename = f"{slugify(asset.title, allow_unicode=False) or 'model'}-{abs(hash(image_url)) % 100000}{extension}"
    if gallery:
        obj = ImportedPrintAssetImage(asset=asset, remote_url=image_url, alt_text=asset.title)
        obj.image.save(filename, ContentFile(data), save=True)
        return obj
    asset.preview_image.save(filename, ContentFile(data), save=True)
    return asset


@transaction.atomic
def import_single_url(source: PrintCatalogSource, url: str, *, actor=None, job=None) -> ImportedPrintAsset:
    validate_source_url(source, url)
    if not source.is_active:
        raise ValidationError("این منبع غیرفعال است.")
    if not _robots_allowed(source, url):
        raise ValidationError("طبق robots.txt اجازه دریافت این صفحه وجود ندارد.")

    if job is None:
        job = PrintCatalogImportJob.objects.create(source=source, source_url=url, created_by=actor)
    job.status = "running"
    job.started_at = timezone.now()
    job.log = "شروع دریافت صفحه"
    job.save(update_fields=["status", "started_at", "log"])

    try:
        data, content_type = _fetch_bytes(source, url, max_bytes=MAX_HTML_BYTES)
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValidationError("صفحه منبع HTML نیست.")
        html = data.decode("utf-8", errors="replace")
        if source.adapter_key == "custom":
            from .catalog_adapters import get_adapter

            adapter = get_adapter(source.code)
            if adapter is None:
                raise ValidationError(
                    "برای این منبع آداپتور اختصاصی ثبت نشده است. "
                    "فایل آداپتور را در store/catalog_site_adapters ایجاد کنید."
                )
            parsed = adapter.parse(html, url, source)
        else:
            parsed = parse_print_page(html, url)

        asset, _ = ImportedPrintAsset.objects.update_or_create(
            source=source,
            source_url=url,
            defaults={
                "external_id": parsed["external_id"],
                "title": parsed["title"],
                "slug": _safe_slug(parsed["title"], url),
                "short_description": parsed["short_description"],
                "description": parsed["description"],
                "technical_specs": parsed["technical_specs"],
                "tags": parsed["tags"],
                "author_name": parsed["author_name"],
                "license_name": parsed["license_name"],
                "license_url": parsed["license_url"],
                "remote_image_url": parsed["images"][0] if parsed["images"] else "",
                "private_download_url": parsed["download_url"] if source.store_private_download_url else "",
                "file_format": parsed["file_format"],
                "source_payload": parsed["raw_json_ld"],
            },
        )

        if source.download_preview_images and parsed["images"] and not asset.preview_image:
            try:
                _download_image(source, parsed["images"][0], asset)
            except Exception as image_error:
                job.log += f"\nهشدار تصویر اصلی: {image_error}"
        for index, image_url in enumerate(parsed["images"][1:5], start=1):
            if asset.images.filter(remote_url=image_url).exists():
                continue
            if source.download_preview_images:
                try:
                    image = _download_image(source, image_url, asset, gallery=True)
                    image.sort_order = index
                    image.save(update_fields=["sort_order"])
                except Exception as image_error:
                    job.log += f"\nهشدار تصویر {index}: {image_error}"
            else:
                ImportedPrintAssetImage.objects.create(
                    asset=asset,
                    remote_url=image_url,
                    alt_text=asset.title,
                    sort_order=index,
                )

        job.status = "success"
        job.result_asset = asset
        job.finished_at = timezone.now()
        job.log += "\nواردسازی با موفقیت انجام شد."
        job.save(update_fields=["status", "result_asset", "finished_at", "log"])
        return asset
    except Exception as error:
        job.status = "failed"
        job.finished_at = timezone.now()
        job.log = (job.log + f"\nخطا: {error}").strip()
        job.save(update_fields=["status", "finished_at", "log"])
        raise


def convert_asset_to_product(asset: ImportedPrintAsset) -> Product:
    if asset.product_id:
        return asset.product
    if not asset.source.default_category_id:
        raise ValidationError("برای منبع، دسته پیش‌فرض محصول تعیین نشده است.")
    if not asset.preview_image:
        raise ValidationError("قبل از تبدیل، تصویر اصلی فایل را ذخیره یا بارگذاری کنید.")

    sku = f"IMP-{asset.source.code.upper()[:12]}-{asset.pk:06d}"
    product_slug = slugify(asset.title, allow_unicode=True)[:220] or f"imported-{asset.pk}"
    suffix = 1
    original_slug = product_slug
    while Product.objects.filter(slug=product_slug).exists():
        suffix += 1
        product_slug = f"{original_slug}-{suffix}"

    product = Product(
        category=asset.source.default_category,
        title=asset.title,
        slug=product_slug,
        sku=sku,
        short_description=asset.short_description or asset.description[:350] or asset.title,
        description=asset.description or asset.short_description or asset.title,
        technical_notes=(
            f"طراح/ناشر: {asset.author_name or '-'}\n"
            f"مجوز: {asset.license_name or 'نیازمند بررسی'}\n"
            f"صفحه منبع: {asset.source_url}\n\n"
            f"{json.dumps(asset.technical_specs, ensure_ascii=False, indent=2) if asset.technical_specs else ''}"
        ).strip(),
        is_active=False,
    )
    product.main_image.save(Path(asset.preview_image.name).name, asset.preview_image.file, save=False)
    product.save()

    for image in asset.images.filter(image__isnull=False).order_by("sort_order", "id"):
        target = product.images.create(alt_text=image.alt_text or product.title, sort_order=image.sort_order)
        target.image.save(Path(image.image.name).name, image.image.file, save=True)

    asset.product = product
    asset.status = "converted"
    asset.save(update_fields=["product", "status", "updated_at"])
    return product
