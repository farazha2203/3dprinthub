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
from store.models import ImportedPrintAsset
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
            "User-Agent": "3DPrintHub-Epic49-Runtime/1.1",
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

    store_status, store_type, store_bytes = fetch(f"{BASE_URL}/store/?epic49=1")
    print(f"STORE_HTTP_STATUS={store_status} CONTENT_TYPE={store_type} BYTES={store_bytes}")
    if store_status != 200:
        failures.append(f"store HTTP {store_status}")

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
        price_min = int(data.get("price_min") or 0)
        price_max = int(data.get("price_max") or price_min or 0)
        print(
            f"OPERATOR_OPTIONS PRODUCT={product.pk} PRICE_MIN={price_min} PRICE_MAX={price_max} "
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
            slider_ok = bool(slide and slide.is_active and slide.effective_image_url)
            if slider_ok:
                slider_url = urljoin(BASE_URL, slide.effective_image_url)
                slider_status, slider_type, slider_bytes = fetch(slider_url, expect_image=True)
                slider_ok = slider_status == 200 and slider_type.startswith("image/") and slider_bytes > 0
                print(
                    f"SLIDER PRODUCT={product.pk} ACTIVE=1 HTTP={slider_status} "
                    f"CONTENT_TYPE={slider_type or '-'} URL={slider_url}"
                )
            else:
                print(f"SLIDER PRODUCT={product.pk} ACTIVE=0 HTTP=0 URL=-")
        elif slide:
            print(f"SLIDER PRODUCT={product.pk} REQUESTED=0 ACTIVE={int(slide.is_active)}")

        print(
            f"PRODUCT={product.pk} QUERY_VISIBLE={int(query_visible)} PRODUCT_HTTP={product_status} "
            f"FALLBACK_HTTP={fallback_status} MAIN_STORAGE_EXISTS={int(main_storage)} MAIN_HTTP={main_status} "
            f"MAIN_CONTENT_TYPE={main_type or '-'} GALLERY={gallery_count} GALLERY_FAILED={gallery_failures} "
            f"URL={encoded_url(product_url)} FALLBACK_URL={fallback_url} MAIN_URL={main_url or '-'}"
        )

        if not query_visible:
            failures.append(f"product {product.pk} missing from Store queryset")
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
        if price_min and int(product.fixed_price or 0) != price_min:
            failures.append(f"product {product.pk} fixed_price {product.fixed_price} != requested minimum {price_min}")
        if slider_requested and not slider_ok:
            failures.append(f"product {product.pk} homepage slider is not publicly healthy")

    if failures:
        print("EPIC49_FAILURES_BEGIN")
        for failure in failures:
            print(f"FAIL={failure}")
        print("EPIC49_FAILURES_END")
        raise RuntimeError(f"Epic49 runtime verification failed with {len(failures)} issue(s).")

    print("EPIC49_WINDOWS_CONTRACT=READY")
    print("EPIC49_BRIDGE=OK")
    print("EPIC49_MEDIA=OK")
    print("EPIC49_STORE=OK")
    print("EPIC49_UNICODE_ROUTE=OK")
    print("EPIC49_OPERATOR_OPTIONS=OK")
    print("EPIC49_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
