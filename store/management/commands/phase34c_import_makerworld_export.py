from __future__ import annotations

import hashlib
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from store.catalog_sync import save_external_record
from store.makerworld_next_data import extract_record
from store.management.commands.phase34b_import_makerworld import (
    resolve_makerworld_source,
)


def build_catalog_record(parsed: dict, source_url: str) -> dict:
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
            "standard digital file license",
        )
    )

    return {
        "source_url": source_url,
        "external_id": str(
            parsed.get("external_id")
            or parsed.get("model_id")
            or ""
        ),
        "title": parsed.get("title") or "MakerWorld model",
        "short_description": (
            parsed.get("description_text") or ""
        )[:500],
        "description": parsed.get("description_text") or "",
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
        "estimated_print_minutes": first_profile.get("print_time"),
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
            else "MakerWorld license requires operator review."
        ),
        "attribution_text": (
            f"{parsed.get('title') or ''} - "
            f"{creator.get('name') or 'MakerWorld'} - MakerWorld"
        ),
        "metrics": {
            "views_count": 0,
            "likes_count": metrics.get("likes") or 0,
            "downloads_count": metrics.get("downloads") or 0,
            "makes_count": metrics.get("prints") or 0,
            "comments_count": metrics.get("comments") or 0,
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


def import_manifest(manifest_path: Path):
    manifest_path = manifest_path.resolve()

    if not manifest_path.is_file():
        raise CommandError(
            f"Manifest file was not found: {manifest_path}"
        )

    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )
    if manifest.get("status") != "collected":
        raise CommandError("Manifest is not collected.")

    html_file = str(manifest.get("html_file") or "")
    source_url = str(
        manifest.get("final_url")
        or manifest.get("requested_url")
        or ""
    )

    html_path = manifest_path.parent / html_file
    if not html_path.is_file():
        raise CommandError(
            f"HTML file was not found: {html_path}"
        )

    raw_html = html_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    expected_hash = str(manifest.get("html_sha256") or "")
    actual_hash = hashlib.sha256(
        raw_html.encode("utf-8")
    ).hexdigest()

    if expected_hash and expected_hash != actual_hash:
        raise CommandError("HTML SHA256 mismatch.")

    parsed = extract_record(raw_html, source_url)
    source, policy = resolve_makerworld_source()
    record = build_catalog_record(parsed, source_url)

    saved_result = save_external_record(
        source=source,
        policy=policy,
        parsed=record,
    )

    if isinstance(saved_result, tuple):
        asset = saved_result[0]
    else:
        asset = saved_result

    return asset


class Command(BaseCommand):
    help = "Import one collected MakerWorld manifest."

    def add_arguments(self, parser):
        parser.add_argument("manifest_path")

    def handle(self, *args, **options):
        asset = import_manifest(
            Path(options["manifest_path"])
        )
        self.stdout.write(f"ASSET_ID={asset.pk}")
        self.stdout.write(f"TITLE={asset.title}")
        self.stdout.write(f"IMAGE_COUNT={asset.images.count()}")
        self.stdout.write(
            "PHASE34C_MAKERWORLD_EXPORT_IMPORT=OK"
        )
