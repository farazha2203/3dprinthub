from __future__ import annotations

import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

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


BASE_URL = "https://3dprinthub.ir"


def fetch(url: str, *, expect_image: bool = False) -> tuple[int, str, int]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "3DPrintHub-Epic49-Runtime/1.0",
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
        .prefetch_related("product__images")
        .order_by("product_id")
    )
    print(f"ACTIVE_IMPORTED_PRODUCTS={len(assets)}")

    for asset in assets:
        product = asset.product
        query_visible = product.pk in visible_ids
        product_url = urljoin(BASE_URL, product.get_absolute_url())
        product_status, product_type, product_bytes = fetch(product_url)

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

        print(
            f"PRODUCT={product.pk} QUERY_VISIBLE={int(query_visible)} PRODUCT_HTTP={product_status} "
            f"MAIN_STORAGE_EXISTS={int(main_storage)} MAIN_HTTP={main_status} "
            f"MAIN_CONTENT_TYPE={main_type or '-'} GALLERY={gallery_count} GALLERY_FAILED={gallery_failures} "
            f"URL={product_url} MAIN_URL={main_url or '-'}"
        )

        if not query_visible:
            failures.append(f"product {product.pk} missing from Store queryset")
        if product_status != 200:
            failures.append(f"product {product.pk} page HTTP {product_status}")
        if not main_storage:
            failures.append(f"product {product.pk} main image missing from storage")
        if not main_http_ok:
            failures.append(f"product {product.pk} main image HTTP invalid: {main_status} {main_type}")
        if gallery_failures:
            failures.append(f"product {product.pk} has {gallery_failures} broken gallery image(s)")

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
    print("EPIC49_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
