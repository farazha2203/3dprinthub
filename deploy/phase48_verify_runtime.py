#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import traceback
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = Path("/home/sfkilvrs/3dprinthub")
sys.path.insert(0, str(PROJECT))
os.chdir(PROJECT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.conf import settings
from django.core.management import get_commands
from django.db import transaction
from django.test import Client
from django.urls import resolve

SITE = "https://3dprinthub.ir"


def request(url: str, token: str = ""):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            body = response.read(5000).decode("utf-8", errors="replace")
            return response.status, body
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(5000).decode("utf-8", errors="replace")


def local_home_traceback() -> None:
    print("=== LOCAL_DJANGO_HOME_TRACEBACK ===")
    client = Client(raise_request_exception=True)
    try:
        with transaction.atomic():
            try:
                response = client.get(
                    "/",
                    HTTP_HOST="3dprinthub.ir",
                    secure=True,
                )
                print(f"LOCAL_DJANGO_HOME_STATUS={response.status_code}")
            finally:
                # Any write accidentally caused by the GET is rolled back.
                transaction.set_rollback(True)
    except Exception:
        traceback.print_exc()


def main() -> int:
    token = str(getattr(settings, "CATALOG_BRIDGE_TOKEN", "") or "").strip()
    print(f"DJANGO_VERSION={django.get_version()}")
    print(f"CATALOG_BRIDGE_TOKEN_PRESENT={'YES' if len(token) >= 24 else 'NO'}")
    print(
        "PHASE37_COMMAND_REGISTERED="
        + ("YES" if "phase37_import_catalog_center" in get_commands() else "NO")
    )

    health = resolve("/api/catalog-bridge/v1/health/")
    import_route = resolve("/api/catalog-bridge/v1/import/")
    print(f"HEALTH_ROUTE={health.view_name}")
    print(f"IMPORT_ROUTE={import_route.view_name}")

    status, body = request(SITE + "/", "")
    print(f"HOME_HTTP_STATUS={status}")
    if status != 200:
        print("HOME_BODY_PREFIX=" + body[:800].replace("\n", " "))
        local_home_traceback()
        return 20

    health_status, health_body = request(
        SITE + "/api/catalog-bridge/v1/health/",
        token,
    )
    print(f"BRIDGE_HEALTH_HTTP_STATUS={health_status}")
    print("BRIDGE_HEALTH_BODY=" + health_body[:1500].replace("\n", " "))
    if health_status != 200:
        return 21
    try:
        payload = json.loads(health_body)
    except Exception:
        return 22
    if payload.get("schema_version") != "8.5":
        print("BRIDGE_SCHEMA_MISMATCH=YES")
        return 23

    print("PHASE48_RUNTIME_VERIFY=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
