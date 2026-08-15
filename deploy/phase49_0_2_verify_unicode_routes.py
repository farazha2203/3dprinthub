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

from django.urls import resolve

from store.models import ImportedPrintAsset
from store.views import _product_queryset


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "3DPrintHub-Phase49.0.2-Verify/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as response:
            return int(response.status), response.read(1000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(1000).decode("utf-8", "replace")


def main() -> int:
    base_url = "https://3dprinthub.ir"
    print("=== PHASE49.0.2 UNICODE ROUTE RUNTIME VERIFY ===")
    print(f"PROJECT_ROOT={ROOT}")
    print(f"DJANGO_VERSION={django.get_version()}")

    products = list(
        ImportedPrintAsset.objects.filter(
            product__isnull=False,
            product__is_active=True,
            product__category__is_active=True,
        )
        .select_related("product", "product__category")
        .order_by("product_id")
    )
    print(f"ACTIVE_IMPORTED_PRODUCTS={len(products)}")

    visible_ids = set(_product_queryset().values_list("id", flat=True))
    failures: list[str] = []

    store_status, store_body = fetch(f"{base_url}/store/?phase49_0_2_verify=1")
    print(f"STORE_HTTP_STATUS={store_status}")
    if store_status != 200:
        failures.append(f"/store/ HTTP {store_status}: {store_body[:300]}")

    for asset in products:
        product = asset.product
        try:
            path = product.get_absolute_url()
            match = resolve(path)
            route_ok = match.view_name == "store:product_detail"
        except Exception as exc:
            failures.append(f"product={product.pk} reverse/resolve failed: {type(exc).__name__}: {exc}")
            print(f"PRODUCT={product.pk} ROUTE=FAILED ERROR={type(exc).__name__}:{exc}")
            continue

        query_visible = product.pk in visible_ids
        url = urljoin(base_url, path)
        status, body = fetch(url)
        print(
            f"PRODUCT={product.pk} ROUTE_OK={int(route_ok)} "
            f"QUERY_VISIBLE={int(query_visible)} HTTP={status} PATH={path}"
        )
        if not route_ok:
            failures.append(f"product={product.pk} wrong route {match.view_name}")
        if not query_visible:
            failures.append(f"product={product.pk} missing from store queryset")
        if status != 200:
            failures.append(f"product={product.pk} HTTP {status}: {body[:300]}")

    if failures:
        print("FAILURES_BEGIN")
        for item in failures:
            print(item)
        print("FAILURES_END")
        raise RuntimeError(f"Phase49.0.2 runtime verification has {len(failures)} failure(s).")

    print("PHASE49_0_2_UNICODE_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
