from __future__ import annotations

import base64
import json
import ssl
from dataclasses import dataclass
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlencode

from .site_connection import SiteConnection


@dataclass
class BridgeConflictError(RuntimeError):
    payload: dict

    def __str__(self):
        entity = self.payload.get("entity") or "record"
        current = self.payload.get("current_revision")
        expected = self.payload.get("expected_revision")
        return f"نسخه سایت جدیدتر است: {entity} (local={expected}, server={current})"


def _request(settings: SiteConnection, path: str, payload: dict | None = None, *, timeout: int | None = None) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    url = cfg.site_url.rstrip("/") + "/api/catalog-bridge/v1/" + path.lstrip("/")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {cfg.bridge_token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib_request.Request(url, data=body, headers=headers, method="GET" if body is None else "POST")
    try:
        with urllib_request.urlopen(req, timeout=timeout or cfg.timeout, context=ssl.create_default_context()) as response:
            parsed = json.loads(response.read().decode("utf-8", errors="replace") or "{}")
            if not isinstance(parsed, dict):
                raise RuntimeError("Bridge response is not a JSON object")
            parsed.setdefault("http_status", int(response.status))
            return parsed
    except urllib_error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw or "{}")
        except Exception:
            detail = {"detail": raw[:2000]}
        if exc.code == 409 and isinstance(detail, dict):
            raise BridgeConflictError(detail) from exc
        raise RuntimeError(f"Bridge HTTP {exc.code}: {detail}") from exc


def list_products(settings: SiteConnection, query: str = "", limit: int = 100) -> list[dict]:
    params = urlencode({"q": str(query or ""), "limit": max(1, min(200, int(limit)))})
    data = _request(settings, f"products/?{params}")
    return list(data.get("items") or [])


def get_product(settings: SiteConnection, product_id: int) -> dict:
    data = _request(settings, f"products/{int(product_id)}/")
    return dict(data.get("product") or {})


def update_product(settings: SiteConnection, product_id: int, expected_revision: int, *, product=None, profile=None, operator="desktop") -> dict:
    return _request(
        settings,
        f"products/{int(product_id)}/sync/",
        {
            "expected_revision": int(expected_revision or 0),
            "operator": str(operator or "desktop")[:120],
            "product": dict(product or {}),
            "profile": dict(profile or {}),
        },
        timeout=max(30, settings.timeout),
    )


def list_filaments(settings: SiteConnection, query: str = "", material: str = "") -> list[dict]:
    params = urlencode({
        "q": str(query or ""),
        "material": str(material or ""),
        "limit": 500,
    })
    data = _request(settings, f"filaments/?{params}")
    return list(data.get("items") or [])


def sync_filament(settings: SiteConnection, filament: dict, *, operator="desktop") -> dict:
    payload = dict(filament or {})
    image_path = str(payload.pop("filament_image_path", "") or "").strip()
    if image_path:
        source = Path(image_path).expanduser()
        if source.is_file():
            raw = source.read_bytes()
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError(
                    "Filament image is larger than the 2 MB Bridge limit"
                )
            payload["filament_image_base64"] = base64.b64encode(raw).decode("ascii")
            payload["filament_image_name"] = source.name[:180]
        else:
            raise ValueError("Filament image path does not exist")
    return _request(
        settings,
        "filaments/sync/",
        {
            "operator": str(operator or "desktop")[:120],
            "filament": payload,
        },
        timeout=max(30, settings.timeout),
    )


def list_hero_slides(settings: SiteConnection) -> list[dict]:
    data = _request(settings, "hero-slides/")
    return list(data.get("items") or [])


def get_hero_slide(settings: SiteConnection, slide_id: int) -> dict:
    data = _request(settings, f"hero-slides/{int(slide_id)}/")
    return dict(data.get("slide") or {})


def update_hero_slide(settings: SiteConnection, slide_id: int, expected_revision: int, slide: dict, *, operator="desktop") -> dict:
    return _request(
        settings,
        f"hero-slides/{int(slide_id)}/sync/",
        {
            "expected_revision": int(expected_revision or 0),
            "operator": str(operator or "desktop")[:120],
            "slide": dict(slide or {}),
        },
        timeout=max(30, settings.timeout),
    )


def apply_server_product_to_local(db, local_product_id: int, server: dict) -> None:
    """Persist editable server fields; immutable/raw internet source data stays local."""
    profile = server.get("profile") if isinstance(server.get("profile"), dict) else {}
    values = {
        "server_product_id": int(server.get("id") or 0),
        "server_product_revision": int(profile.get("sync_revision") or 0),
        "server_slider_id": int(server.get("hero_slide_id") or 0),
        "server_slider_revision": int(server.get("hero_revision") or 0),
        "server_updated_at": str(server.get("updated_at") or ""),
        "last_sync_conflict": "",
        "title_fa": str(server.get("title") or ""),
        "short_description_fa": str(server.get("short_description") or ""),
        "description_fa": str(server.get("description") or ""),
        "seo_title_fa": str(server.get("meta_title") or ""),
        "seo_description_fa": str(server.get("meta_description") or ""),
        "homepage_slider_enabled": int(bool(profile.get("homepage_slider_enabled"))),
        "homepage_slider_image_url": str(profile.get("homepage_slider_image_url") or ""),
        "homepage_slider_sort_order": int(profile.get("homepage_slider_sort_order") or 100),
        "homepage_slider_title_fa": str(profile.get("homepage_slider_title_fa") or ""),
        "homepage_slider_description_fa": str(profile.get("homepage_slider_description_fa") or ""),
        "homepage_slider_alt_text": str(profile.get("homepage_slider_alt_text") or ""),
        "homepage_slider_button_text": str(profile.get("homepage_slider_button_text") or "مشاهده محصول"),
        "homepage_slider_focus_keyword": str(profile.get("homepage_slider_focus_keyword") or ""),
        "homepage_slider_transition_effect": str(profile.get("homepage_slider_transition_effect") or "cinematic_fade"),
        "homepage_slider_transition_duration_ms": int(profile.get("homepage_slider_transition_duration_ms") or 1400),
        "homepage_slider_display_duration_ms": int(profile.get("homepage_slider_display_duration_ms") or 7000),
    }
    db.update_product(int(local_product_id), values)


def absorb_ack_revisions(db, local_product_id: int, item: dict) -> None:
    values = {
        "server_product_id": int(item.get("server_product_id") or item.get("product_id") or 0),
        "server_product_revision": int(item.get("product_revision") or 0),
        "server_slider_id": int(item.get("slider_id") or 0),
        "server_slider_revision": int(item.get("slider_revision") or 0),
        "last_sync_conflict": "",
    }
    db.update_product(int(local_product_id), values)
