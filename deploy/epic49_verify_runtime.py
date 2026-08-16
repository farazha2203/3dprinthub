from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.core.management import get_commands

from catalog_bridge.views import PUBLISH_CONTRACT, VERSION
from store.epic49_catalog_profile import ProductCatalogProfile
from store.models import ImportedPrintAsset
from store.sitemaps import ProductSitemap
from store.views import _product_queryset
from website.models import HomepageHeroSlide


BASE_URL = "https://3dprinthub.ir"


def encoded_url(url: str) -> str:
    parts = urlsplit(url)
    path = quote(parts.path, safe="/%:@-._~!$&'()*+,;=")
    query = quote(parts.query, safe="=&%:@-._~!$'()*+,;/?")
    return urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def fetch(url: str, *, expect_image: bool = False) -> tuple[int, str, int]:
    url = encoded_url(url)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "3DPrintHub-Epic49-Runtime/1.2",
            "Accept": "image/avif,image/webp,image/*,*/*;q=0.8" if expect_image else "text/html,*/*;q=0.8",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=25, context=ssl.create_default_context()) as response:
            body = response.read(64_000 if expect_image else 500_000)
            content_type = str(response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
            return int(response.status), content_type, len(body)
    except urllib.error.HTTPError as exc:
        return int(exc.code), str(exc.headers.get("Content-Type") or ""), 0
    except Exception as exc:
        print(f"HTTP_EXCEPTION URL={url} ERROR={type(exc).__name__}:{exc}")
        return 0, "", 0


def desktop_payload(asset) -> dict:
    payload = asset.source_payload or {}
    data = payload.get("desktop_catalog_v85") if isinstance(payload, dict) else {}
    return data if isinstance(data, dict) else {}


def safe_list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        result = json.loads(value or "[]")
        return result if isinstance(result, list) else []
    except Exception:
        return []


def safe_dict(value) -> dict:
    if isinstance(value, dict):
        return value
    try:
        result = json.loads(value or "{}")
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


def expected_slider_copy(data: dict, product) -> dict:
    content_pack = safe_dict(data.get("content_pack_json"))
    ai = content_pack.get("homepage_slider_seo") or {}
    if not isinstance(ai, dict):
        ai = {}
    alts = safe_list(data.get("image_alt_texts_json"))
    return {
        "title": str(
            data.get("homepage_slider_title_fa")
            or ai.get("title_fa")
            or data.get("title_fa")
            or product.title
            or ""
        ).strip()[:220],
        "description": str(
            data.get("homepage_slider_description_fa")
            or ai.get("description_fa")
            or data.get("short_description_fa")
            or data.get("seo_description_fa")
            or product.short_description
            or ""
        ).strip()[:480],
        "alt": str(
            data.get("homepage_slider_alt_text")
            or ai.get("image_alt_fa")
            or (alts[0] if alts else "")
            or data.get("title_fa")
            or product.title
            or ""
        ).strip()[:240],
        "button": str(
            data.get("homepage_slider_button_text")
            or ai.get("button_text_fa")
            or "مشاهده محصول"
        ).strip()[:80] or "مشاهده محصول",
        "focus": str(
            data.get("homepage_slider_focus_keyword")
            or ai.get("focus_keyword_fa")
            or ""
        ).strip()[:180],
    }


def is_ascii_slug(value: str) -> bool:
    try:
        str(value or "").encode("ascii")
        return bool(value) and "%" not in value and "/" not in value
    except UnicodeEncodeError:
        return False


def main() -> int:
    failures: list[str] = []
    print("=== EPIC49 FINAL PRODUCTION VERIFY ===")
    print(f"PROJECT_ROOT={ROOT}")
    print(f"DJANGO_VERSION={django.get_version()}")
    print(f"BRIDGE_VERSION={VERSION}")
    print(f"PUBLISH_CONTRACT={PUBLISH_CONTRACT}")

    if VERSION != "1.2.0":
        failures.append(f"bridge version is {VERSION}, expected 1.2.0")
    if PUBLISH_CONTRACT != "epic49-final":
        failures.append(f"publish contract is {PUBLISH_CONTRACT}")
    if "epic49_archive_failed_batches" not in get_commands():
        failures.append("epic49_archive_failed_batches command is not registered")
    if "epic49_backfill_server_catalog" not in get_commands():
        failures.append("epic49_backfill_server_catalog command is not registered")

    store_status, store_type, store_bytes = fetch(f"{BASE_URL}/store/?epic49=1")
    sitemap_status, sitemap_type, sitemap_bytes = fetch(f"{BASE_URL}/sitemap.xml?epic49=1")
    print(f"STORE_HTTP_STATUS={store_status} CONTENT_TYPE={store_type} BYTES={store_bytes}")
    print(f"SITEMAP_HTTP_STATUS={sitemap_status} CONTENT_TYPE={sitemap_type} BYTES={sitemap_bytes}")
    if store_status != 200:
        failures.append(f"store HTTP {store_status}")
    if sitemap_status != 200:
        failures.append(f"sitemap HTTP {sitemap_status}")

    visible_ids = set(_product_queryset().values_list("id", flat=True))
    assets = list(
        ImportedPrintAsset.objects.filter(
            product__isnull=False,
            product__is_active=True,
            product__category__is_active=True,
        )
        .select_related("product", "product__category")
        .prefetch_related("product__images", "product__variants__material", "product__variants__color")
        .order_by("product_id")
    )
    print(f"ACTIVE_IMPORTED_PRODUCTS={len(assets)}")

    for asset in assets:
        product = asset.product
        data = desktop_payload(asset)
        query_visible = product.pk in visible_ids
        profile = ProductCatalogProfile.objects.filter(product=product).first()
        profile_ok = profile is not None
        ascii_slug_ok = is_ascii_slug(product.slug)
        slug_match = bool(profile and product.slug == profile.public_slug)
        sitemap_path = ProductSitemap().location(product)
        sitemap_match = sitemap_path == product.get_absolute_url()

        product_url = urljoin(BASE_URL, product.get_absolute_url())
        product_status, product_type, product_bytes = fetch(product_url)
        fallback_url = f"{BASE_URL}/store/p/{product.pk}/"
        fallback_status, fallback_type, fallback_bytes = fetch(fallback_url)

        main_name = str(product.main_image.name or "")
        try:
            main_storage = bool(main_name and product.main_image.storage.exists(main_name))
        except Exception:
            main_storage = False
        main_url = urljoin(BASE_URL, product.main_image.url) if main_name else ""
        main_status, main_type, main_bytes = fetch(main_url, expect_image=True) if main_url else (0, "", 0)
        main_http_ok = main_status == 200 and main_type.startswith("image/") and main_bytes > 0

        gallery_failures = 0
        gallery_count = 0
        for image in product.images.all():
            gallery_count += 1
            name = str(image.image.name or "")
            try:
                exists = bool(name and image.image.storage.exists(name))
            except Exception:
                exists = False
            url = urljoin(BASE_URL, image.image.url) if name else ""
            status, content_type, size = fetch(url, expect_image=True) if url else (0, "", 0)
            ok = exists and status == 200 and content_type.startswith("image/") and size > 0
            print(
                f"GALLERY PRODUCT={product.pk} INDEX={gallery_count} STORAGE_EXISTS={int(exists)} "
                f"HTTP={status} CONTENT_TYPE={content_type or '-'} URL={url or '-'}"
            )
            if not ok:
                gallery_failures += 1

        selected_material_colors = safe_list(data.get("material_color_options_json"))
        active_operator_variants = list(
            product.variants.filter(is_active=True, code__startswith=f"EP49-{product.pk}-")
            .select_related("material", "color", "quality")
        )
        requested_price_min = int(data.get("price_min") or 0)
        requested_price_max = int(data.get("price_max") or requested_price_min or 0)
        profile_price_ok = bool(
            profile
            and (not requested_price_min or profile.price_min == requested_price_min)
            and (not requested_price_max or profile.price_max == requested_price_max)
        )
        seo_ok = bool(
            product.meta_title
            and product.meta_description
            and product.seo_focus_keyword
            and product.robots_index
            and product.robots_follow
        )

        print(
            f"PROFILE PRODUCT={product.pk} EXISTS={int(profile_ok)} ASCII_SLUG={int(ascii_slug_ok)} "
            f"SLUG_MATCH={int(slug_match)} SITEMAP_MATCH={int(sitemap_match)} "
            f"PRICE_OK={int(profile_price_ok)} SEO_OK={int(seo_ok)} "
            f"PUBLIC_SLUG={getattr(profile, 'public_slug', '-') if profile else '-'}"
        )
        print(
            f"OPERATOR_OPTIONS PRODUCT={product.pk} PRICE_MIN={requested_price_min} PRICE_MAX={requested_price_max} "
            f"REQUESTED_MATERIAL_COLORS={len(selected_material_colors)} ACTIVE_OPERATOR_VARIANTS={len(active_operator_variants)}"
        )
        for variant in active_operator_variants:
            print(
                f"VARIANT PRODUCT={product.pk} ID={variant.pk} MATERIAL={variant.material.name} "
                f"COLOR={variant.color.name if variant.color_id else '-'} QUALITY={variant.quality.name} "
                f"PRICE={variant.cached_unit_price}"
            )

        slider_requested = bool(data.get("homepage_slider_enabled"))
        slide = HomepageHeroSlide.objects.filter(asset=asset).order_by("id").first()
        slider_ok = True
        if slider_requested:
            expected_copy = expected_slider_copy(data, product)
            slider_copy_ok = bool(
                slide
                and str(slide.effective_title or "").strip()
                and str(slide.description or "").strip()
                and str(slide.effective_alt_text or "").strip()
                and str(slide.button_text or "").strip()
                and str(slide.effective_title or "").strip() == expected_copy["title"]
                and str(slide.description or "").strip() == expected_copy["description"]
                and str(slide.effective_alt_text or "").strip() == expected_copy["alt"]
                and str(slide.button_text or "").strip() == expected_copy["button"]
            )
            slider_ok = bool(
                slide
                and slide.is_active
                and slide.effective_image_url
                and slide.target_url == product.get_absolute_url()
                and slider_copy_ok
            )
            if slider_ok:
                slider_url = urljoin(BASE_URL, slide.effective_image_url)
                slider_status, slider_type, slider_bytes = fetch(slider_url, expect_image=True)
                slider_ok = slider_status == 200 and slider_type.startswith("image/") and slider_bytes > 0
                print(
                    f"SLIDER PRODUCT={product.pk} ACTIVE=1 COPY_OK={int(slider_copy_ok)} TARGET={slide.target_url} "
                    f"HTTP={slider_status} CONTENT_TYPE={slider_type or '-'} URL={slider_url} "
                    f"TITLE={slide.effective_title!r} ALT={slide.effective_alt_text!r} BUTTON={slide.button_text!r} "
                    f"FOCUS={expected_copy['focus']!r}"
                )
            else:
                print(
                    f"SLIDER PRODUCT={product.pk} ACTIVE=0/TARGET_OR_COPY_MISMATCH COPY_OK={int(slider_copy_ok)} "
                    f"HTTP=0 URL=-"
                )
        elif slide:
            print(f"SLIDER PRODUCT={product.pk} REQUESTED=0 ACTIVE={int(slide.is_active)} TARGET={slide.target_url}")

        print(
            f"PRODUCT={product.pk} QUERY_VISIBLE={int(query_visible)} PRODUCT_HTTP={product_status} "
            f"FALLBACK_HTTP={fallback_status} MAIN_STORAGE_EXISTS={int(main_storage)} MAIN_HTTP={main_status} "
            f"MAIN_CONTENT_TYPE={main_type or '-'} GALLERY={gallery_count} GALLERY_FAILED={gallery_failures} "
            f"URL={encoded_url(product_url)} FALLBACK_URL={fallback_url} MAIN_URL={main_url or '-'}"
        )

        if not query_visible:
            failures.append(f"product {product.pk} missing from Store queryset")
        if not profile_ok:
            failures.append(f"product {product.pk} missing ProductCatalogProfile")
        if not ascii_slug_ok:
            failures.append(f"product {product.pk} slug is not ASCII-safe: {product.slug!r}")
        if not slug_match:
            failures.append(f"product {product.pk} slug/profile mismatch")
        if not sitemap_match:
            failures.append(f"product {product.pk} sitemap URL differs from canonical URL")
        if not profile_price_ok:
            failures.append(f"product {product.pk} structured price range differs from desktop payload")
        if not seo_ok:
            failures.append(f"product {product.pk} SEO fields are incomplete")
        if product_status != 200:
            failures.append(f"product {product.pk} canonical page HTTP {product_status}")
        if fallback_status != 200:
            failures.append(f"product {product.pk} ID fallback HTTP {fallback_status}")
        if not main_storage:
            failures.append(f"product {product.pk} main image missing from storage")
        if not main_http_ok:
            failures.append(f"product {product.pk} main image HTTP invalid: {main_status} {main_type}")
        if gallery_failures:
            failures.append(f"product {product.pk} has {gallery_failures} broken gallery image(s)")
        if selected_material_colors and len(active_operator_variants) != len(selected_material_colors):
            failures.append(
                f"product {product.pk} requested {len(selected_material_colors)} material/color options but has {len(active_operator_variants)} active operator variants"
            )
        if requested_price_min and int(product.fixed_price or 0) != requested_price_min:
            failures.append(f"product {product.pk} fixed_price {product.fixed_price} != requested minimum {requested_price_min}")
        if slider_requested and not slider_ok:
            failures.append(f"product {product.pk} homepage slider image/link/copy is not publicly healthy")

    if failures:
        print("EPIC49_FAILURES_BEGIN")
        for failure in failures:
            print(f"FAIL={failure}")
        print("EPIC49_FAILURES_END")
        raise RuntimeError(f"Epic49 runtime verification failed with {len(failures)} issue(s).")

    print("EPIC49_WINDOWS_CONTRACT=READY")
    print("EPIC49_BRIDGE=OK")
    print("EPIC49_CATALOG_PROFILE=OK")
    print("EPIC49_ASCII_ROUTE=OK")
    print("EPIC49_MEDIA=OK")
    print("EPIC49_STORE=OK")
    print("EPIC49_OPERATOR_OPTIONS=OK")
    print("EPIC49_SLIDER=OK")
    print("EPIC49_SLIDER_SEO_COPY=OK")
    print("EPIC49_SEO=OK")
    print("EPIC49_SITEMAP=OK")
    print("EPIC49_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
