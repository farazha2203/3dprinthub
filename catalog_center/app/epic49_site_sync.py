from __future__ import annotations

import base64
import json
import ssl
from dataclasses import dataclass
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlencode

from .db import utc_now
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


def list_products(
    settings: SiteConnection,
    query: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    params = urlencode({
        "q": str(query or ""),
        "limit": max(1, min(200, int(limit))),
        "offset": max(0, int(offset or 0)),
    })
    data = _request(settings, f"products/?{params}")
    return list(data.get("items") or [])


def list_all_products(
    settings: SiteConnection,
    query: str = "",
    *,
    page_size: int = 200,
    max_items: int = 5000,
) -> list[dict]:
    page_size = max(1, min(200, int(page_size or 200)))
    max_items = max(page_size, min(20_000, int(max_items or 5000)))
    output: list[dict] = []
    offset = 0
    while len(output) < max_items:
        page = list_products(
            settings,
            query,
            min(page_size, max_items - len(output)),
            offset=offset,
        )
        if not page:
            break
        output.extend(dict(item) for item in page if isinstance(item, dict))
        offset += len(page)
        if len(page) < page_size:
            break
    return output


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
    """Pull editable Site fields into one existing Local mirror.

    Raw acquisition/source identity and local media files remain Local-owned.
    Site Admin owns current canonical content/profile facts after its revision
    is explicitly accepted by the caller.
    """
    profile = server.get("profile") if isinstance(server.get("profile"), dict) else {}
    price_min = max(0, int(profile.get("price_min") or 0))
    price_max = max(0, int(profile.get("price_max") or price_min))
    price_mode = str(profile.get("price_mode") or "fixed")
    strategy = str(profile.get("pricing_strategy") or "legacy").strip().lower()
    if strategy not in {"legacy", "fixed", "dynamic"}:
        strategy = "legacy"
    fixed_price = (
        price_min
        if price_min > 0 and price_min == price_max and price_mode == "fixed"
        else 0
    )
    values = {
        "server_product_id": int(server.get("id") or 0),
        "server_product_revision": int(profile.get("sync_revision") or 0),
        "server_slider_id": int(server.get("hero_slide_id") or 0),
        "server_slider_revision": int(server.get("hero_revision") or 0),
        "server_updated_at": str(server.get("updated_at") or ""),
        "last_sync_conflict": "",
        "last_synced_at": utc_now(),
        "server_status": "updated",
        "product_sync_error": "",
        "upload_ready": 0,
        "needs_update": 0,
        "title_fa": str(server.get("title") or ""),
        "short_description_fa": str(server.get("short_description") or ""),
        "description_fa": str(server.get("description") or ""),
        "seo_title_fa": str(server.get("meta_title") or ""),
        "seo_description_fa": str(server.get("meta_description") or ""),
        "product_type": str(profile.get("product_type") or "ready_product"),
        "use_description": str(profile.get("use_description") or ""),
        "availability_status": str(profile.get("availability_status") or "made_to_order"),
        "stock_quantity": max(0, int(profile.get("stock_quantity") or 0)),
        "lead_time_min_days": max(0, int(profile.get("lead_time_min_days") or 0)),
        "lead_time_max_days": max(0, int(profile.get("lead_time_max_days") or 0)),
        "has_3d_file": int(bool(profile.get("has_3d_file"))),
        "license_name": str(profile.get("license_name") or ""),
        "license_url": str(profile.get("license_url") or ""),
        "technical_features_json": json.dumps(
            profile.get("technical_features")
            if isinstance(profile.get("technical_features"), dict)
            else {},
            ensure_ascii=False,
        ),
        "keywords_json": json.dumps(
            profile.get("keywords")
            if isinstance(profile.get("keywords"), list)
            else [],
            ensure_ascii=False,
        ),
        "price_min": price_min,
        "price_max": max(price_min, price_max),
        "pricing_strategy": strategy,
        "pricing_inputs_json": json.dumps(
            profile.get("pricing_inputs")
            if isinstance(profile.get("pricing_inputs"), dict)
            else {},
            ensure_ascii=False,
        ),
        "technical_summary_fa": str(profile.get("technical_summary_fa") or ""),
        "final_price": fixed_price,
        "price_is_final": int(bool(fixed_price)),
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
        "homepage_slider_presentation_mode": str(profile.get("homepage_slider_presentation_mode") or "product_fit"),
        "homepage_slider_object_fit": str(profile.get("homepage_slider_object_fit") or "contain"),
        "homepage_slider_focal_position": str(profile.get("homepage_slider_focal_position") or "center"),
        "homepage_slider_image_scale_percent": int(profile.get("homepage_slider_image_scale_percent") or 100),
        "homepage_slider_position_x_percent": int(profile.get("homepage_slider_position_x_percent") or 50),
        "homepage_slider_position_y_percent": int(profile.get("homepage_slider_position_y_percent") or 50),
        "homepage_slider_background_mode": str(profile.get("homepage_slider_background_mode") or "blur"),
        "homepage_slider_background_color": str(profile.get("homepage_slider_background_color") or "#071827"),
        "homepage_slider_background_blur_px": int(profile.get("homepage_slider_background_blur_px") or 18),
        "homepage_slider_desktop_max_width_percent": int(profile.get("homepage_slider_desktop_max_width_percent") or 78),
        "homepage_slider_desktop_max_height_percent": int(profile.get("homepage_slider_desktop_max_height_percent") or 88),
        "homepage_slider_mobile_max_width_percent": int(profile.get("homepage_slider_mobile_max_width_percent") or 92),
        "homepage_slider_mobile_max_height_percent": int(profile.get("homepage_slider_mobile_max_height_percent") or 72),
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
