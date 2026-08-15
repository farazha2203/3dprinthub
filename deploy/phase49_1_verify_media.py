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

from django.conf import settings

from store.models import ImportedPrintAsset
from store.views import _product_queryset


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "3DPrintHub-Phase49.1-Media-Verify/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as response:
            return int(response.status), response.read(1000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(1000).decode("utf-8", "replace")


def main() -> int:
    base_url = "https://3dprinthub.ir"
    print("=== PHASE49.1 MEDIA RUNTIME VERIFY ===")
    print(f"PROJECT_ROOT={ROOT}")
    print(f"MEDIA_URL={settings.MEDIA_URL}")
    print(f"MEDIA_ROOT={Path(settings.MEDIA_ROOT).resolve()}")

    assets = list(
        ImportedPrintAsset.objects.filter(
            product__isnull=False,
            product__is_active=True,
            product__category__is_active=True,
        )
        .select_related("product", "product__category")
        .order_by("product_id")
    )
    visible_ids = set(_product_queryset().values_list("id", flat=True))
    failures: list[str] = []

    store_status, store_body = fetch(f"{base_url}/store/?phase49_1_media=1")
    print(f"STORE_HTTP_STATUS={store_status}")
    if store_status != 200:
        failures.append(f"/store/ HTTP {store_status}: {store_body[:250]}")

    for asset in assets:
        product = asset.product
        field = product.main_image
        name = str(getattr(field, "name", "") or "")
        try:
            storage_exists = bool(name and field.storage.exists(name))
        except Exception:
            storage_exists = False
        query_visible = product.pk in visible_ids
        url = urljoin(base_url, field.url) if name else ""
        status, body = fetch(url) if url else (0, "missing image url")
        try:
            path = field.path
        except Exception:
            path = "-"
        print(
            f"PRODUCT={product.pk} STORAGE_EXISTS={int(storage_exists)} "
            f"QUERY_VISIBLE={int(query_visible)} HTTP={status} NAME={name or '-'} PATH={path} URL={url or '-'}"
        )
        if not storage_exists:
            failures.append(f"product={product.pk} storage missing: {name}")
        if not query_visible:
            failures.append(f"product={product.pk} missing from store queryset")
        if status != 200:
            failures.append(f"product={product.pk} image HTTP {status}: {url} {body[:160]}")

    favicon_status, favicon_body = fetch(f"{base_url}/static/favicon/favicon.ico")
    print(f"FAVICON_HTTP_STATUS={favicon_status}")
    if favicon_status != 200:
        failures.append(f"favicon HTTP {favicon_status}: {favicon_body[:160]}")

    root_favicon_status, root_favicon_body = fetch(f"{base_url}/favicon.ico")
    print(f"ROOT_FAVICON_HTTP_STATUS={root_favicon_status}")
    if root_favicon_status not in {200, 301, 302}:
        failures.append(f"root favicon HTTP {root_favicon_status}: {root_favicon_body[:160]}")

    if failures:
        print("FAILURES_BEGIN")
        for failure in failures:
            print(failure)
        print("FAILURES_END")
        raise RuntimeError(f"Phase49.1 media verification has {len(failures)} failure(s).")

    print("PHASE49_1_MEDIA_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
