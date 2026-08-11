from __future__ import annotations

import re
import time
from urllib.error import HTTPError
from urllib.parse import urldefrag
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.catalog_site_adapters import get_source_adapter
from store.catalog_site_adapters.common import CatalogCandidate
from store.catalog_sync import save_external_record
from store.makerworld_next_data import extract_record
from store.models import (
    CatalogSourcePolicy,
    Category,
    PrintCatalogSource,
)


MAKERWORLD_URL_RE = re.compile(
    r"/(?:[a-z]{2}/)?models/(?P<model_id>\d+)(?:[-/?#]|$)",
    re.IGNORECASE,
)

BROWSER_HEADER_PROFILES = (
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9,fa;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Referer": "https://makerworld.com/en",
    },
    {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8",
        "Referer": "https://makerworld.com/",
    },
)


@transaction.atomic
def resolve_makerworld_source() -> tuple[PrintCatalogSource, CatalogSourcePolicy]:
    source = PrintCatalogSource.objects.filter(code="makerworld").first()

    if source is None:
        policy = (
            CatalogSourcePolicy.objects
            .select_related("source")
            .filter(source_kind="makerworld")
            .order_by("pk")
            .first()
        )
        source = policy.source if policy is not None else None

    category, _ = Category.objects.get_or_create(
        slug="external-other",
        defaults={
            "name": "سایر مدل‌های آماده",
            "section": "general",
            "description": "مدل‌های خارجی بررسی‌شده و آماده سفارش چاپ",
            "is_active": True,
        },
    )

    if source is None:
        source = PrintCatalogSource.objects.create(
            name="MakerWorld",
            code="makerworld",
            base_url="https://makerworld.com/en",
            allowed_domains="makerworld.com,makerworld.bblmw.com",
            adapter_key="custom",
            default_category=category,
            request_headers={},
            request_timeout_seconds=45,
            respect_robots_txt=True,
            download_preview_images=False,
            store_private_download_url=True,
            license_note=(
                "مجوز استاندارد MakerWorld برای فروش چاپ فیزیکی کافی نیست؛ "
                "فقط مجوز تجاری صریح قابل تأیید است."
            ),
            is_active=True,
        )
    else:
        changed_fields: list[str] = []

        if source.adapter_key != "custom":
            source.adapter_key = "custom"
            changed_fields.append("adapter_key")
        if not source.is_active:
            source.is_active = True
            changed_fields.append("is_active")
        if source.default_category_id is None:
            source.default_category = category
            changed_fields.append("default_category")

        source.request_headers = {
            **(source.request_headers or {}),
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.7",
            "Referer": "https://makerworld.com/en",
        }
        changed_fields.append("request_headers")

        if changed_fields:
            source.save(update_fields=changed_fields + ["updated_at"])

    policy, _ = CatalogSourcePolicy.objects.update_or_create(
        source=source,
        defaults={
            "source_kind": "makerworld",
            "discovery_mode": "public_html",
            "public_display_policy": "licensed_only",
            "is_active": True,
        },
    )
    return source, policy


def fetch_public_html(url: str, timeout: int) -> tuple[str, int]:
    errors: list[str] = []

    for attempt, headers in enumerate(BROWSER_HEADER_PROFILES, start=1):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:  # nosec B310
                payload = response.read(8_000_001)
                if len(payload) > 8_000_000:
                    raise ValueError("MakerWorld response exceeded 8 MB.")
                return payload.decode("utf-8", errors="replace"), attempt
        except HTTPError as error:
            errors.append(f"attempt {attempt}: HTTP {error.code}")
            if error.code not in {403, 429}:
                raise
        except Exception as error:
            errors.append(
                f"attempt {attempt}: {type(error).__name__}: {error}"
            )

        time.sleep(min(2 * attempt, 4))

    raise CommandError(
        "MakerWorld public page fetch failed after browser-header retries: "
        + " | ".join(errors)
    )


class Command(BaseCommand):
    help = (
        "Import or refresh one public MakerWorld model using browser-like "
        "HTTP headers and the Phase 34B parser."
    )

    def add_arguments(self, parser):
        parser.add_argument("url")

    def handle(self, *args, **options):
        source_url, _fragment = urldefrag(str(options["url"]).strip())
        match = MAKERWORLD_URL_RE.search(source_url)

        if not match:
            raise CommandError("A public MakerWorld model URL is required.")

        source, policy = resolve_makerworld_source()
        timeout = max(10, int(source.request_timeout_seconds or 45))

        try:
            raw_html, attempt = fetch_public_html(source_url, timeout)
            parsed = extract_record(raw_html, source_url)

            adapter = get_source_adapter(source, policy)
            candidate = CatalogCandidate(
                url=source_url,
                external_id=match.group("model_id"),
            )

            record = adapter.fetch_record_from_parsed_data(
                candidate,
                parsed,
            ) if hasattr(adapter, "fetch_record_from_parsed_data") else None

            if record is None:
                record = adapter.fetch_record(
                    candidate,
                    hydrate_files=False,
                    raw_html=raw_html,
                ) if "raw_html" in adapter.fetch_record.__code__.co_varnames else None

            if record is None:
                # Build the record through the existing adapter logic without
                # issuing another HTTP request.
                license_data = parsed.get("license") or {}
                creator = parsed.get("creator") or {}
                metrics = parsed.get("metrics") or {}
                instances = parsed.get("instances") or []
                first_profile = instances[0] if instances else {}
                image_rows = parsed.get("images") or []
                image_urls = [
                    row.get("url")
                    for row in image_rows
                    if isinstance(row, dict) and row.get("url")
                ]
                license_name = str(
                    license_data.get("name")
                    or license_data.get("title")
                    or ""
                )
                license_text = str(
                    license_data.get("description") or ""
                )
                lowered = (license_name + " " + license_text).lower()
                commercial_allowed = any(
                    token in lowered
                    for token in (
                        "commercial use allowed",
                        "commercial use permitted",
                        "cc0",
                        "public domain",
                        "cc by",
                    )
                ) and not any(
                    token in lowered
                    for token in (
                        "non-commercial",
                        "noncommercial",
                        "no commercial",
                        "not for commercial",
                    )
                )

                record = {
                    "source_url": source_url,
                    "external_id": (
                        parsed.get("external_id")
                        or candidate.external_id
                    ),
                    "title": (
                        parsed.get("title")
                        or candidate.external_id
                    ),
                    "short_description": (
                        parsed.get("description_text") or ""
                    )[:500],
                    "description": (
                        parsed.get("description_text") or ""
                    ),
                    "author_name": creator.get("name") or "",
                    "creator_url": (
                        f"https://makerworld.com/en/@{creator.get('name')}"
                        if creator.get("name")
                        else ""
                    ),
                    "license_name": license_name,
                    "license_url": source_url,
                    "license_text": license_text,
                    "tags": parsed.get("tags") or [],
                    "source_category": " / ".join(
                        parsed.get("categories") or []
                    ),
                    "images": image_urls,
                    "image_records": image_rows,
                    "file_links": [],
                    "file_formats": (
                        ["3MF"] if parsed.get("is_printable") else []
                    ),
                    "estimated_weight_grams": first_profile.get("weight"),
                    "estimated_print_minutes": first_profile.get(
                        "print_time"
                    ),
                    "estimate_source": (
                        "makerworld_profile" if first_profile else ""
                    ),
                    "commercial_use_allowed": commercial_allowed,
                    "license_review_status": (
                        "allowed" if commercial_allowed else "manual"
                    ),
                    "blocked_reason": (
                        ""
                        if commercial_allowed
                        else (
                            "مجوز MakerWorld نیازمند بررسی و تأیید "
                            "اپراتور است."
                        )
                    ),
                    "attribution_text": (
                        f"{parsed.get('title') or ''} — "
                        f"{creator.get('name') or 'MakerWorld'} — "
                        "MakerWorld"
                    ),
                    "metrics": {
                        "views_count": 0,
                        "likes_count": metrics.get("likes") or 0,
                        "downloads_count": (
                            metrics.get("downloads") or 0
                        ),
                        "makes_count": metrics.get("prints") or 0,
                        "comments_count": (
                            metrics.get("comments") or 0
                        ),
                        "rating": None,
                    },
                    "technical_specs": {
                        "model_id": parsed.get("model_id"),
                        "default_instance_id": parsed.get(
                            "default_instance_id"
                        ),
                        "categories": parsed.get("categories") or [],
                        "instances": instances,
                        "image_records": image_rows,
                        "is_printable": parsed.get("is_printable"),
                        "is_official": parsed.get("is_official"),
                        "is_exclusive": parsed.get("is_exclusive"),
                    },
                    "raw_payload": parsed,
                }

            asset, _metrics = save_external_record(
                source=source,
                policy=policy,
                parsed=record,
            )
        except CommandError:
            raise
        except Exception as error:
            raise CommandError(
                f"MakerWorld import failed: {type(error).__name__}: {error}"
            ) from error

        self.stdout.write(f"HTTP_PROFILE_ATTEMPT={attempt}")
        self.stdout.write(f"SOURCE_ID={source.pk}")
        self.stdout.write(f"ASSET_ID={asset.pk}")
        self.stdout.write(f"TITLE={asset.title}")
        self.stdout.write(f"IMAGE_COUNT={asset.images.count()}")
        self.stdout.write("PHASE34B_MAKERWORLD_IMPORT=OK")
