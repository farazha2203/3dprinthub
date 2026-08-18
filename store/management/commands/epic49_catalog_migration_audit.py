from __future__ import annotations

import json
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.utils.text import slugify

from store.models import ImportedPrintAsset, Product


TARGET_MIGRATIONS = (
    "0028_epic49_catalog_product_schema",
    "0029_epic49_catalog_product_backfill",
)


def _json_value(value, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


def _positive_int(value, default=0):
    try:
        normalized = str(value if value not in (None, "") else default).replace(",", "").strip()
        return max(0, int(float(normalized or 0)))
    except Exception:
        try:
            return max(0, int(default or 0))
        except Exception:
            return 0


def _base_slug(product) -> str:
    candidates = (
        getattr(product, "title_en", ""),
        getattr(product, "source_external_id", ""),
        getattr(product, "sku", ""),
    )
    for value in candidates:
        base = slugify(str(value or ""), allow_unicode=False).strip("-")
        if base:
            return base[:200]
    return f"product-{product.pk}"


def _desktop_data(asset) -> dict:
    payload = asset.source_payload or {}
    if not isinstance(payload, dict):
        return {}
    data = payload.get("desktop_catalog_v85")
    return data if isinstance(data, dict) else {}


def _product_changes(product, asset, proposed_slug: str) -> dict:
    data = _desktop_data(asset)
    keywords = _json_value(data.get("keywords_json"), [])
    tags_fa = _json_value(data.get("tags_fa_json"), [])
    hashtags = _json_value(data.get("hashtags_fa_json"), [])

    proposed = {
        "slug": proposed_slug,
        "canonical_url": "",
        "meta_title": str(
            data.get("seo_title_fa")
            or getattr(product, "meta_title", "")
            or getattr(product, "title", "")
        )[:180],
        "meta_description": str(
            data.get("seo_description_fa")
            or getattr(product, "meta_description", "")
            or getattr(product, "short_description", "")
        ).replace("\n", " ")[:320],
        "seo_focus_keyword": next(
            (str(item).strip() for item in [*keywords, *tags_fa] if str(item).strip()),
            getattr(product, "title", ""),
        )[:180],
        "og_title": str(
            data.get("seo_title_fa")
            or getattr(product, "meta_title", "")
            or getattr(product, "title", "")
        )[:180],
        "og_description": str(
            data.get("seo_description_fa")
            or getattr(product, "meta_description", "")
            or getattr(product, "short_description", "")
        ).replace("\n", " ")[:320],
        "editorial_source_url": str(
            data.get("source_url") or getattr(asset, "source_url", "")
        )[:1000],
        "source_attribution": str(
            data.get("author_name")
            or getattr(asset, "author_name", "")
            or getattr(asset.source, "name", "")
        )[:220],
        "hashtags": " ".join(str(item).strip() for item in hashtags if str(item).strip()),
        "robots_index": bool(getattr(product, "is_active", False)),
        "robots_follow": bool(getattr(product, "is_active", False)),
    }

    changes = {}
    for field, new_value in proposed.items():
        old_value = getattr(product, field, None)
        if old_value != new_value:
            changes[field] = {"before": old_value, "after": new_value}
    return changes


def _profile_preview(product, asset, proposed_slug: str) -> dict:
    data = _desktop_data(asset)
    fallback_price = _positive_int(
        getattr(product, "fixed_price", 0),
        getattr(asset, "fixed_print_price", 0),
    )
    minimum = _positive_int(data.get("price_min"), fallback_price)
    maximum = _positive_int(data.get("price_max"), minimum)
    if minimum and maximum and maximum < minimum:
        minimum, maximum = maximum, minimum

    options = _json_value(data.get("material_color_options_json"), [])
    availability = str(data.get("availability_status") or "made_to_order")
    if availability == "quote_required":
        price_mode = "quote"
    elif options:
        price_mode = "variant"
    elif maximum > minimum > 0:
        price_mode = "range"
    else:
        price_mode = "fixed"

    return {
        "public_slug": proposed_slug,
        "legacy_slug": str(getattr(product, "slug", "") or "")[:240],
        "desktop_product_id": _positive_int(data.get("desktop_product_id"), 0) or None,
        "product_type": str(data.get("product_type") or "ready_product")[:40],
        "availability_status": availability[:40],
        "stock_quantity": _positive_int(data.get("stock_quantity"), 0),
        "price_min": minimum,
        "price_max": maximum,
        "price_mode": price_mode,
        "homepage_slider_enabled": bool(data.get("homepage_slider_enabled")),
        "homepage_slider_sort_order": _positive_int(data.get("homepage_slider_sort_order"), 100),
    }


class Command(BaseCommand):
    help = (
        "Read-only audit for pending store.0028/0029. Reports catalog profile creation "
        "and Product slug/SEO changes without mutating the database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum detailed changed products to print; 0 means unlimited.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Print one machine-readable JSON document instead of text.",
        )

    def handle(self, *args, **options):
        limit = max(0, int(options["limit"] or 0))
        as_json = bool(options["as_json"])

        applied = set(
            MigrationRecorder.Migration.objects.filter(
                app="store",
                name__in=TARGET_MIGRATIONS,
            ).values_list("name", flat=True)
        )
        tables = set(connection.introspection.table_names())
        profile_table_exists = "store_productcatalogprofile" in tables

        profile_slug_owner = {}
        if profile_table_exists:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT product_id, public_slug FROM store_productcatalogprofile"
                )
                for product_id, public_slug in cursor.fetchall():
                    value = str(public_slug or "").strip()
                    if value:
                        profile_slug_owner[value] = int(product_id)

        product_slug_owners = defaultdict(set)
        for product_id, slug in Product.objects.values_list("id", "slug"):
            value = str(slug or "").strip()
            if value:
                product_slug_owners[value].add(int(product_id))

        assets = list(
            ImportedPrintAsset.objects.exclude(product_id=None)
            .select_related("product", "source")
            .order_by("pk")
        )

        rows = []
        field_change_counts = defaultdict(int)
        slug_change_count = 0

        for asset in assets:
            product = asset.product
            base = _base_slug(product)
            candidate = base
            counter = 1
            while True:
                profile_owner = profile_slug_owner.get(candidate)
                product_owners = product_slug_owners.get(candidate, set()) - {int(product.pk)}
                if (profile_owner in (None, int(product.pk))) and not product_owners:
                    break
                counter += 1
                suffix = f"-{counter}"
                candidate = f"{base[:220-len(suffix)]}{suffix}"

            # Mirror migration 0029 iteration: the chosen profile slug becomes reserved
            # before the next asset is evaluated.
            profile_slug_owner[candidate] = int(product.pk)

            changes = _product_changes(product, asset, candidate)
            for field in changes:
                field_change_counts[field] += 1
            if "slug" in changes:
                slug_change_count += 1

            rows.append(
                {
                    "asset_id": asset.pk,
                    "product_id": product.pk,
                    "sku": str(getattr(product, "sku", "") or ""),
                    "title": str(getattr(product, "title", "") or ""),
                    "profile": _profile_preview(product, asset, candidate),
                    "product_changes": changes,
                }
            )

        changed_rows = [row for row in rows if row["product_changes"]]
        summary = {
            "read_only": True,
            "db_vendor": connection.vendor,
            "store_0028_applied": TARGET_MIGRATIONS[0] in applied,
            "store_0029_applied": TARGET_MIGRATIONS[1] in applied,
            "profile_table_exists": profile_table_exists,
            "imported_assets_with_product": len(rows),
            "profiles_to_create_or_refresh": len(rows),
            "products_with_any_change": len(changed_rows),
            "products_with_slug_change": slug_change_count,
            "field_change_counts": dict(sorted(field_change_counts.items())),
        }

        if as_json:
            payload = {
                "summary": summary,
                "items": changed_rows if limit == 0 else changed_rows[:limit],
                "detail_limit": limit,
                "detail_truncated": bool(limit and len(changed_rows) > limit),
            }
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
            return

        self.stdout.write("EPIC49_CATALOG_MIGRATION_AUDIT")
        self.stdout.write("READ_ONLY=YES")
        self.stdout.write(f"DB_VENDOR={summary['db_vendor']}")
        self.stdout.write(f"STORE_0028_APPLIED={summary['store_0028_applied']}")
        self.stdout.write(f"STORE_0029_APPLIED={summary['store_0029_applied']}")
        self.stdout.write(f"PROFILE_TABLE_EXISTS={summary['profile_table_exists']}")
        self.stdout.write(f"IMPORTED_ASSETS_WITH_PRODUCT={len(rows)}")
        self.stdout.write(f"PROFILES_TO_CREATE_OR_REFRESH={len(rows)}")
        self.stdout.write(f"PRODUCTS_WITH_ANY_CHANGE={len(changed_rows)}")
        self.stdout.write(f"PRODUCTS_WITH_SLUG_CHANGE={slug_change_count}")
        self.stdout.write("FIELD_CHANGE_COUNTS=" + json.dumps(summary["field_change_counts"], ensure_ascii=False, sort_keys=True))

        detail_rows = changed_rows if limit == 0 else changed_rows[:limit]
        for index, row in enumerate(detail_rows, start=1):
            fields = ",".join(sorted(row["product_changes"])) or "none"
            slug_change = row["product_changes"].get("slug")
            slug_text = ""
            if slug_change:
                slug_text = f" | SLUG: {slug_change['before']} -> {slug_change['after']}"
            self.stdout.write(
                f"[{index}] PRODUCT={row['product_id']} ASSET={row['asset_id']} "
                f"SKU={row['sku']} | FIELDS={fields}{slug_text}"
            )

        if limit and len(changed_rows) > limit:
            self.stdout.write(f"DETAIL_TRUNCATED=YES ({limit}/{len(changed_rows)})")
        else:
            self.stdout.write("DETAIL_TRUNCATED=NO")
        self.stdout.write("AUDIT_DB_MUTATIONS=0")
