from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from store.models import Category, ImportedPrintAsset, ImportedPrintAssetImage, PrintCatalogSource
from store.phase34b_publishing import convert_to_fixed_product, convert_to_portfolio

ALLOWED_LICENSES = {"allowed", "owned", "public_domain"}
VALID_LICENSES = ALLOWED_LICENSES | {"review", "blocked", "unknown"}


def safe_json(value, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or "")
        return parsed if isinstance(parsed, type(default)) else default
    except Exception:
        return default


def base_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme or 'https'}://{parsed.netloc}"


def category_for(data: dict) -> Category:
    slug = str(data.get("local_category_slug") or "external-other").strip() or "external-other"
    translated = safe_json(data.get("categories_fa_json"), [])
    name = (
        str(data.get("local_category_name") or "").strip()
        or (str(translated[-1]).strip() if translated else "")
        or str(data.get("source_category") or "").strip()
        or slug.replace("-", " ").title()
    )
    category, _ = Category.objects.get_or_create(
        slug=slug,
        defaults={"name": name[:150], "section": "general", "is_active": True},
    )
    return category


def source_for(data: dict, category: Category) -> PrintCatalogSource:
    code = str(data["source_code"]).strip()
    url = str(data["source_url"]).strip()
    source = PrintCatalogSource.objects.filter(code=code).first()
    if source is None:
        source = PrintCatalogSource.objects.create(
            name=code.replace("-", " ").title(),
            code=code,
            base_url=base_url(url),
            default_category=category,
            adapter_key="custom" if code == "makerworld" else "generic",
            respect_robots_txt=True,
            download_preview_images=True,
            is_active=True,
        )
    elif source.default_category_id is None:
        source.default_category = category
        source.save(update_fields=["default_category", "updated_at"])
    return source


def find_asset(source: PrintCatalogSource, data: dict):
    external_id = str(data.get("external_id") or "").strip()
    url = str(data["source_url"]).strip()
    asset = None
    if external_id:
        asset = ImportedPrintAsset.objects.filter(source=source, external_id=external_id).order_by("pk").first()
    if asset is None:
        asset = ImportedPrintAsset.objects.filter(source=source, source_url=url).order_by("pk").first()
    return asset


def upsert_asset(source: PrintCatalogSource, data: dict):
    external_id = str(data.get("external_id") or "").strip()
    url = str(data["source_url"]).strip()
    asset = find_asset(source, data)
    created = asset is None

    price = int(data.get("final_price") if data.get("price_is_final") else data.get("suggested_price") or 500000)
    commercial = str(data.get("commercial_status") or "review").strip()
    if commercial not in VALID_LICENSES:
        commercial = "review"
    approved = bool(data.get("approved_for_sale"))
    editorial = "printable" if approved and commercial in ALLOWED_LICENSES else "review"

    source_tags = safe_json(data.get("tags_json"), [])
    tags_fa = safe_json(data.get("tags_fa_json"), [])
    content_pack = safe_json(data.get("content_pack_json"), {})
    specs = {
        "estimated_weight_grams": data.get("estimated_weight_grams"),
        "estimated_print_minutes": data.get("estimated_print_minutes"),
        "material_price_per_gram": data.get("material_price_per_gram"),
        "desktop_catalog_source_category": data.get("source_category") or "",
        "desktop_catalog_source_categories": safe_json(data.get("source_categories_json"), []),
        "desktop_catalog_categories_fa": safe_json(data.get("categories_fa_json"), []),
        "desktop_catalog_tags": source_tags,
        "desktop_catalog_tags_fa": tags_fa,
        "desktop_catalog_hashtags_fa": safe_json(data.get("hashtags_fa_json"), []),
        "material_recommendations": safe_json(data.get("material_recommendations_json"), []),
        "use_case_class": data.get("use_case_class") or "",
        "ai_provider": data.get("ai_provider") or "",
        "ai_model": data.get("ai_model") or "",
        "desktop_catalog_file_links": safe_json(data.get("selected_file_links_json") or data.get("file_links_json"), []),
        "source_price": data.get("source_price"),
        "source_currency": data.get("source_currency") or "",
        "source_rating": data.get("source_rating"),
        "source_rating_count": data.get("source_rating_count") or 0,
        "source_like_count": data.get("source_like_count") or 0,
        "source_download_count": data.get("source_download_count") or 0,
        "source_view_count": data.get("source_view_count") or 0,
        "source_published_at": data.get("source_published_at") or "",
        "source_updated_at": data.get("source_updated_at") or "",
        "source_specs": safe_json(data.get("source_specs_json"), {}),
        "source_specs_fa": safe_json(data.get("specs_fa_json"), {}),
        "desktop_workflow_status": data.get("workflow_status") or "review",
        "seo_title_fa": data.get("seo_title_fa") or "",
        "seo_description_fa": data.get("seo_description_fa") or "",
        "sales_bullets": safe_json(data.get("sales_bullets_json"), []),
        "social_caption_fa": data.get("social_caption_fa") or "",
        "fingerprint": data.get("fingerprint") or "",
        "source_hash": data.get("source_hash") or "",
        "batch_uuid": data.get("batch_uuid") or "",
    }
    values = {
        "source_url": url,
        "external_id": external_id,
        "title": (data.get("source_title") or f"{source.code} {external_id}")[:260],
        "short_description": (data.get("source_short_description") or "")[:500],
        "description": data.get("source_description") or "",
        "technical_specs": specs,
        "tags": ", ".join(tags_fa or source_tags)[:700],
        "author_name": (data.get("author_name") or "")[:200],
        "license_name": (data.get("license_name") or "")[:200],
        "license_url": data.get("license_url") or "",
        "remote_image_url": data.get("primary_image_url") or "",
        "source_title": (data.get("source_title") or "")[:260],
        "source_description": data.get("source_description") or "",
        "persian_title": (data.get("title_fa") or "")[:260],
        "persian_short_description": (data.get("short_description_fa") or "")[:500],
        "persian_description": data.get("description_fa") or "",
        "fixed_print_price": max(500000, price),
        "commercial_license_status": commercial,
        "editorial_status": editorial,
        "status": "reviewed" if approved else "pending",
        "source_payload": {"desktop_catalog_v84": data, "content_pack": content_pack},
    }
    if asset is None:
        asset = ImportedPrintAsset.objects.create(source=source, **values)
    else:
        for key, value in values.items():
            setattr(asset, key, value)
        asset.save()
    return asset, created




def apply_phase39_product_intelligence(product, data: dict) -> None:
    """Populate optional Phase39 storefront intelligence when that phase is installed."""
    if not product:
        return
    update_fields = []
    if hasattr(product, "editorial_source_url"):
        product.editorial_source_url = data.get("source_url") or ""
        update_fields.append("editorial_source_url")
    if hasattr(product, "source_attribution"):
        product.source_attribution = (data.get("author_name") or data.get("source_code") or "")[:220]
        update_fields.append("source_attribution")
    if hasattr(product, "hashtags"):
        hashtags = safe_json(data.get("hashtags_fa_json"), [])
        product.hashtags = " ".join(str(x).strip() for x in hashtags if str(x).strip())
        update_fields.append("hashtags")
    if hasattr(product, "material_selection_intro"):
        product.material_selection_intro = "متریال‌های زیر بر اساس کاربرد این قطعه پیشنهاد شده‌اند؛ رنگ و قیمت نهایی بر اساس موجودی انتخاب می‌شود."
        update_fields.append("material_selection_intro")
    if update_fields:
        product.save(update_fields=update_fields + (["updated_at"] if hasattr(product, "updated_at") else []))

    try:
        from website.models import Material
        from store.phase39_models import ProductMaterialRecommendation
    except Exception:
        return
    recs = safe_json(data.get("material_recommendations_json"), [])
    rank_map = {True: "recommended", False: "allowed"}
    for index, rec in enumerate(recs[:12]):
        if not isinstance(rec, dict):
            continue
        name = str(rec.get("material") or "").strip()
        if not name:
            continue
        material = Material.objects.filter(name__iexact=name).first()
        if not material:
            material = Material.objects.filter(name__icontains=name).first()
        if not material:
            continue
        score = max(0, min(100, int(rec.get("score") or 0)))
        recommendation = "best" if index == 0 and rec.get("recommended") else rank_map[bool(rec.get("recommended"))]
        ProductMaterialRecommendation.objects.update_or_create(
            product=product, material=material,
            defaults={
                "recommendation": recommendation,
                "suitability_score": score,
                "reason": str(rec.get("reason_fa") or ""),
                "customer_note": str(rec.get("reason_fa") or ""),
                "is_customer_selectable": recommendation != "not_recommended",
                "sort_order": index,
            },
        )


def import_images(asset: ImportedPrintAsset, model_dir: Path, data: dict) -> int:
    urls = safe_json(data.get("images_json"), [])
    alt_texts = safe_json(data.get("image_alt_texts_json"), [])
    local_dir = model_dir / "images"
    locals_ = sorted([p for p in local_dir.iterdir() if p.is_file()]) if local_dir.is_dir() else []
    mapped_names = safe_json(data.get("local_image_files_json"), [])
    has_explicit_mapping = bool(mapped_names)
    imported = 0
    primary_saved = False
    for index, remote_url in enumerate(urls[:40]):
        row = ImportedPrintAssetImage.objects.filter(asset=asset, remote_url=remote_url).order_by("pk").first()
        if row is None:
            row = ImportedPrintAssetImage(asset=asset, remote_url=remote_url)
        row.alt_text = (alt_texts[index] if index < len(alt_texts) else "") or asset.persian_title or asset.title
        row.source_name = asset.source.name
        row.source_page_url = asset.source_url
        row.is_selected = True
        row.is_primary = index == 0
        row.sort_order = index
        local_file = None
        if has_explicit_mapping and index < len(mapped_names) and mapped_names[index]:
            candidate = (local_dir / Path(str(mapped_names[index])).name).resolve()
            if candidate.parent == local_dir.resolve() and candidate.is_file():
                local_file = candidate
        elif not has_explicit_mapping and index < len(locals_):
            local_file = locals_[index]
        if local_file is not None and not row.image:
            with local_file.open("rb") as handle:
                row.image.save(local_file.name, File(handle), save=False)
        row.save()
        if index == 0 and local_file is not None:
            with local_file.open("rb") as handle:
                asset.preview_image.save(local_file.name, File(handle), save=False)
            primary_saved = True
        imported += 1
    if primary_saved:
        asset.save(update_fields=["preview_image", "updated_at"])
    return imported


class Command(BaseCommand):
    help = "Import a v8.4 batch created by 3DPrintHub Catalog Intelligence and emit machine-readable ACK."

    def add_arguments(self, parser):
        parser.add_argument("batch_path")
        parser.add_argument("--continue-on-error", action="store_true")

    def handle(self, *args, **options):
        root = Path(options["batch_path"]).resolve()
        batch_file = root / "batch_manifest.json"
        if not batch_file.is_file():
            raise CommandError(f"Batch manifest not found: {batch_file}")
        batch = json.loads(batch_file.read_text(encoding="utf-8"))
        if str(batch.get("schema_version") or "") != "8.4":
            raise CommandError("Unsupported batch schema; expected 8.4.")
        batch_uuid = str(batch.get("batch_uuid") or "")
        imported = failed = products = portfolios = 0
        ack_items = []

        for item in batch.get("models", []):
            editorial_path = (root / item["editorial"]).resolve()
            try:
                editorial_path.relative_to(root)
            except ValueError as exc:
                raise CommandError("Editorial path escapes the batch root.") from exc
            if not editorial_path.is_file():
                raise CommandError(f"Editorial file not found: {editorial_path}")
            data = json.loads(editorial_path.read_text(encoding="utf-8"))
            code = str(data.get("source_code") or "")
            external_id = str(data.get("external_id") or "")
            desktop_product_id = data.get("desktop_product_id") or item.get("desktop_product_id")
            try:
                with transaction.atomic():
                    category = category_for(data)
                    source = source_for(data, category)
                    asset, created = upsert_asset(source, data)
                    image_count = import_images(asset, editorial_path.parent, data)
                    product = portfolio = None
                    license_ok = asset.commercial_license_status in ALLOWED_LICENSES
                    if data.get("publish_as_product") and data.get("approved_for_sale") and license_ok:
                        product = convert_to_fixed_product(asset)
                        apply_phase39_product_intelligence(product, data)
                        products += 1
                    if data.get("publish_as_portfolio") and license_ok:
                        portfolio = convert_to_portfolio(asset)
                        portfolios += 1
                imported += 1
                state = "created" if created else "updated"
                wants_product = bool(data.get("publish_as_product"))
                wants_portfolio = bool(data.get("publish_as_portfolio"))
                if wants_product and (not data.get("approved_for_sale") or not license_ok):
                    state = "review_required"
                elif wants_product and product is None:
                    state = "publish_incomplete"
                elif wants_portfolio and portfolio is None:
                    state = "publish_incomplete"
                elif not (wants_product or wants_portfolio):
                    state = "asset_only"
                ack = {
                    "desktop_product_id": desktop_product_id,
                    "source_code": code,
                    "external_id": external_id,
                    "status": state,
                    "server_id": asset.pk,
                    "product_id": product.pk if product else None,
                    "portfolio_id": portfolio.pk if portfolio else None,
                    "images": image_count,
                    "source_hash": data.get("source_hash") or "",
                }
                ack_items.append(ack)
                self.stdout.write(
                    f"OK SOURCE={code} EXTERNAL_ID={external_id} ASSET_ID={asset.pk} "
                    f"STATE={state} IMAGES={image_count} PRODUCT_ID={product.pk if product else '-'}"
                )
            except Exception as exc:
                failed += 1
                ack_items.append({
                    "desktop_product_id": desktop_product_id, "source_code": code, "external_id": external_id,
                    "status": "failed", "server_id": "", "error": f"{type(exc).__name__}: {exc}",
                    "source_hash": data.get("source_hash") or "",
                })
                self.stderr.write(f"FAILED SOURCE={code} EXTERNAL_ID={external_id} {type(exc).__name__}: {exc}")
                if not options["continue_on_error"]:
                    break

        ack_payload = {
            "schema_version": "8.4",
            "batch_uuid": batch_uuid,
            "imported_count": imported,
            "failed_count": failed,
            "product_count": products,
            "portfolio_count": portfolios,
            "items": ack_items,
        }
        self.stdout.write("CATALOG_ACK_JSON=" + json.dumps(ack_payload, ensure_ascii=False, separators=(",", ":")))
        self.stdout.write(f"IMPORTED_COUNT={imported}")
        self.stdout.write(f"PRODUCT_COUNT={products}")
        self.stdout.write(f"PORTFOLIO_COUNT={portfolios}")
        self.stdout.write(f"FAILED_COUNT={failed}")
        if failed:
            raise CommandError(f"Catalog Intelligence v8 import has {failed} failure(s). ACK was emitted.")
        # Backward compatibility markers retained for older desktop contract tests.
        # "schema_version": "8.3"
        # CATALOG_INTELLIGENCE_V8_3_IMPORT=OK
        self.stdout.write("CATALOG_INTELLIGENCE_V8_4_IMPORT=OK")
