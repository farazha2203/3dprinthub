from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.urls import reverse, resolve

from store.models import ImportedPrintAsset
from store.views import _product_queryset


def fetch(url: str, *, token: str = "") -> tuple[int, str]:
    headers = {"Accept": "application/json,text/html;q=0.9,*/*;q=0.8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as response:
            return int(response.status), response.read(20000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(20000).decode("utf-8", "replace")


def main() -> int:
    base_url = "https://3dprinthub.ir"
    token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "").strip()

    print("=== PHASE49 RUNTIME VERIFY ===")
    print(f"DJANGO_VERSION={django.get_version()}")
    print(f"GIT_ROOT={Path(settings.BASE_DIR)}")
    print(f"CATALOG_BRIDGE_TOKEN_PRESENT={'YES' if token else 'NO'}")

    health_path = reverse("catalog_bridge:health")
    diag_path = reverse(
        "catalog_bridge:diagnostic",
        kwargs={"batch_name": "desktop_catalog_v85_20260815_140000"},
    )
    print(f"HEALTH_ROUTE={resolve(health_path).view_name}")
    print(f"DIAGNOSTIC_ROUTE={resolve(diag_path).view_name}")

    assets = ImportedPrintAsset.objects.filter(product__isnull=False).select_related("product", "product__category")
    imported_products = assets.count()
    active_imported = assets.filter(product__is_active=True, product__category__is_active=True).count()
    inactive_imported = assets.filter(product__is_active=False).count()
    active_ids = list(
        assets.filter(product__is_active=True, product__category__is_active=True)
        .values_list("product_id", flat=True)
        .distinct()
    )
    store_visible = _product_queryset().filter(pk__in=active_ids).count() if active_ids else 0

    print(f"IMPORTED_PRODUCTS={imported_products}")
    print(f"ACTIVE_IMPORTED_PRODUCTS={active_imported}")
    print(f"INACTIVE_IMPORTED_PRODUCTS={inactive_imported}")
    print(f"STORE_QUERY_VISIBLE_IMPORTED={store_visible}")

    if imported_products and active_imported == 0:
        raise RuntimeError("No imported catalog product is active after Phase49 reconciliation.")
    if active_ids and store_visible != len(set(active_ids)):
        raise RuntimeError(
            f"Store queryset visibility mismatch: active={len(set(active_ids))} visible={store_visible}"
        )

    store_status, store_body = fetch(f"{base_url}/store/?phase49_verify=1")
    print(f"STORE_HTTP_STATUS={store_status}")
    if store_status != 200:
        raise RuntimeError(f"Live /store/ returned HTTP {store_status}: {store_body[:500]}")

    if not token:
        raise RuntimeError("CATALOG_BRIDGE_TOKEN is missing.")
    health_status, health_body = fetch(f"{base_url}{health_path}", token=token)
    print(f"BRIDGE_HEALTH_HTTP_STATUS={health_status}")
    if health_status != 200:
        raise RuntimeError(f"Bridge health returned HTTP {health_status}: {health_body[:500]}")
    health = json.loads(health_body or "{}")
    print(f"BRIDGE_VERSION={health.get('version')}")
    print(f"BRIDGE_SCHEMA={health.get('schema_version')}")
    if str(health.get("schema_version") or "") != "8.5":
        raise RuntimeError("Bridge schema is not 8.5.")

    diagnostics_root = Path(settings.CATALOG_BRIDGE_PENDING_ROOT).resolve().parent / "diagnostics"
    diagnostics = sorted(diagnostics_root.glob("desktop_catalog_v85_*.json"), key=lambda p: p.stat().st_mtime, reverse=True) if diagnostics_root.is_dir() else []
    print(f"DIAGNOSTIC_FILES={len(diagnostics)}")
    if diagnostics:
        latest = diagnostics[0]
        diag_status, diag_body = fetch(f"{base_url}/api/catalog-bridge/v1/diagnostics/{latest.stem}/", token=token)
        print(f"LATEST_DIAGNOSTIC={latest.name}")
        print(f"DIAGNOSTIC_HTTP_STATUS={diag_status}")
        if diag_status != 200:
            raise RuntimeError(f"Diagnostic endpoint returned HTTP {diag_status}: {diag_body[:500]}")

    print("PHASE49_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
