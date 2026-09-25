from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from .secure_secrets import get_secret
from .social_content_policy import POLICY_VERSION, build_alt_texts, build_caption


@dataclass(frozen=True)
class InstagramConfig:
    account_id: str
    api_version: str = "v26.0"
    login_mode: str = "instagram"
    timeout: int = 30

    @property
    def graph_base(self) -> str:
        host = "graph.instagram.com" if self.login_mode == "instagram" else "graph.facebook.com"
        return f"https://{host}/{self.api_version.strip('/') or 'v26.0'}"


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _tracking_url(product_url: str, product_id: int) -> str:
    parsed = urllib_parse.urlsplit(product_url)
    blocked = {"utm_source", "utm_medium", "utm_campaign", "utm_content"}
    query = [
        (key, value)
        for key, value in urllib_parse.parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in blocked
    ]
    query.extend([
        ("utm_source", "instagram"),
        ("utm_medium", "social"),
        ("utm_campaign", "product_catalog"),
        ("utm_content", f"product-{int(product_id)}"),
    ])
    return urllib_parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib_parse.urlencode(query), parsed.fragment)
    )


def same_public_revision_already_published(db, product_id: int, fingerprint: str) -> bool:
    if not fingerprint:
        return False
    for receipt in db.sync_receipts(int(product_id), limit=80):
        if str(receipt["status"] or "") not in {"instagram_published", "instagram_submitted"}:
            continue
        try:
            previous = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            previous = {}
        if str(previous.get("site_ack_fingerprint") or "") == fingerprint:
            return True
    return False


def _request_json(url: str, token: str, *, payload: dict | None = None, timeout: int = 30) -> dict:
    body = None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if payload is not None:
        body = urllib_parse.urlencode({k: v for k, v in payload.items() if v is not None}).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib_request.Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urllib_request.urlopen(req, timeout=max(10, int(timeout))) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1600]
        raise RuntimeError(f"Instagram HTTP {exc.code}: {detail}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Instagram API returned an invalid JSON object")
    if data.get("error"):
        raise RuntimeError(f"Instagram API error: {data['error']}")
    return data


def canonical_site_payload(row: dict[str, Any], *, site_url: str) -> dict[str, Any]:
    ack = {}
    try:
        ack = json.loads(row.get("server_ack_json") or "{}")
    except Exception:
        ack = {}
    product_url = str(ack.get("product_url") or ack.get("public_product_url") or "").strip()
    if product_url.startswith("/"):
        product_url = site_url.rstrip("/") + product_url
    if not product_url.startswith("https://"):
        raise RuntimeError("محصول هنوز لینک عمومی HTTPS تأییدشده روی سایت ندارد.")
    if not bool(ack.get("public_http_ok", ack.get("visible_on_store", False))):
        raise RuntimeError("انتشار اینستاگرام فقط بعد از تأیید عمومی محصول روی سایت مجاز است.")

    media: list[str] = []
    main = str(
        ack.get("public_main_image_url")
        or ((ack.get("public_http_checks") or {}).get("main_image_url") if isinstance(ack.get("public_http_checks"), dict) else "")
        or ""
    ).strip()

    public_images = ack.get("public_images")
    if not isinstance(public_images, list):
        public_images = ack.get("images")
    if not isinstance(public_images, list):
        checks = ack.get("public_http_checks")
        checked_images = checks.get("images") if isinstance(checks, dict) else []
        checked_images = checked_images if isinstance(checked_images, list) else []
        slug = urllib_parse.urlparse(product_url).path.rstrip("/").split("/")[-1].casefold()
        owned = []
        for item in checked_images:
            url = str(item.get("url") if isinstance(item, dict) else item or "").strip()
            ok = bool(item.get("ok", True)) if isinstance(item, dict) else True
            if not ok or not url.startswith("https://"):
                continue
            path = urllib_parse.urlparse(url).path.casefold()
            if url == main or (slug and slug in path):
                owned.append(item)
        public_images = owned or checked_images

    for item in public_images:
        url = str(item.get("url") if isinstance(item, dict) else item or "").strip()
        ok = bool(item.get("ok", True)) if isinstance(item, dict) else True
        if ok and url.startswith("https://") and url not in media:
            media.append(url)
    if main.startswith("https://"):
        media = [main, *[url for url in media if url != main]]
    if not media:
        raise RuntimeError("هیچ تصویر عمومی HTTPS تأییدشده‌ای برای Instagram وجود ندارد.")

    from .phase50_a2w_media_sync import align_public_media_to_selected
    media = align_public_media_to_selected(row, media)

    public_videos = ack.get("public_videos")
    if not isinstance(public_videos, list):
        public_videos = ack.get("videos")
    video_urls = []
    for item in public_videos if isinstance(public_videos, list) else []:
        url = str(item.get("url") if isinstance(item, dict) else item or "").strip()
        ok = bool(item.get("ok", True)) if isinstance(item, dict) else True
        if ok and url.startswith("https://") and url not in video_urls:
            video_urls.append(url)

    title = str(row.get("seo_title_fa") or row.get("title_fa") or row.get("source_title") or "").strip()
    tracking_url = _tracking_url(product_url, int(row.get("id") or 0))
    source_product_url = str(
        row.get("source_url") or row.get("normalized_url") or ""
    ).strip()
    if not source_product_url.startswith(("https://", "http://")):
        source_product_url = ""
    media_urls = media[:10]
    caption, hashtags = build_caption(row, tracking_url)
    alt_texts = build_alt_texts(row, media_urls)
    media_manifest = ([{"type": "image", "url": url, "alt_text": alt_texts[index] if index < len(alt_texts) else ""}
                      for index, url in enumerate(media_urls)]
                     + [{"type": "video", "url": url, "alt_text": ""} for url in video_urls[:5]])
    return {
        "product_code": str(row.get("external_id") or row.get("sku") or row.get("id") or "").strip(),
        "product_url": product_url,
        "tracking_url": tracking_url,
        "source_product_url": source_product_url,
        "product_details": {
            "source_url": source_product_url,
            "order_url": tracking_url,
            "site_product_url": product_url,
        },
        "media_urls": media_urls,
        "video_urls": video_urls[:5],
        "media_manifest": media_manifest,
        "caption": caption,
        "alt_texts": alt_texts,
        "hashtags": hashtags,
        "title": title,
        "social_policy_version": POLICY_VERSION,
    }


def _wait_container(cfg: InstagramConfig, token: str, container_id: str) -> None:
    deadline = time.monotonic() + 120
    url = f"{cfg.graph_base}/{container_id}?fields=status_code,status"
    while time.monotonic() < deadline:
        status = _request_json(url, token, timeout=cfg.timeout)
        code = str(status.get("status_code") or "").upper()
        if code == "FINISHED":
            return
        if code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Instagram container failed: {status.get('status') or code}")
        time.sleep(2)
    raise TimeoutError("Instagram media container did not become ready in time")


def _create_image_container(cfg: InstagramConfig, token: str, url: str, *, alt_text: str = "", caption: str = "", carousel: bool = False) -> str:
    payload: dict[str, Any] = {"image_url": url}
    if carousel:
        payload["is_carousel_item"] = "true"
    else:
        if caption:
            payload["caption"] = caption
        if alt_text:
            payload["alt_text"] = alt_text[:1000]
    result = _request_json(f"{cfg.graph_base}/{cfg.account_id}/media", token, payload=payload, timeout=cfg.timeout)
    container_id = str(result.get("id") or "").strip()
    if not container_id:
        raise RuntimeError("Instagram did not return a media container id")
    _wait_container(cfg, token, container_id)
    return container_id


def publish_product(db, product_id: int, cfg: InstagramConfig, *, site_url: str) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    data = dict(row)
    payload = canonical_site_payload(data, site_url=site_url)
    fingerprint = str(data.get("server_ack_json") or "").strip()
    for receipt in db.sync_receipts(int(product_id), limit=40):
        if str(receipt["status"] or "") != "instagram_published":
            continue
        try:
            previous = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            previous = {}
        if str(previous.get("site_ack_fingerprint") or "") == fingerprint:
            raise RuntimeError("این نسخه عمومی محصول قبلاً روی Instagram منتشر شده است.")

    token = get_secret("instagram_access_token")
    if not token:
        raise RuntimeError("Instagram Access Token در Windows Credential Store تنظیم نشده است.")
    media_urls = list(payload["media_urls"])
    alt_texts = list(payload["alt_texts"])
    if len(media_urls) == 1:
        creation_id = _create_image_container(cfg, token, media_urls[0], alt_text=(alt_texts[0] if alt_texts else ""), caption=payload["caption"])
    else:
        children = [
            _create_image_container(cfg, token, url, alt_text=(alt_texts[index] if index < len(alt_texts) else ""), carousel=True)
            for index, url in enumerate(media_urls)
        ]
        result = _request_json(
            f"{cfg.graph_base}/{cfg.account_id}/media",
            token,
            payload={"media_type": "CAROUSEL", "children": ",".join(children), "caption": payload["caption"]},
            timeout=cfg.timeout,
        )
        creation_id = str(result.get("id") or "").strip()
        if not creation_id:
            raise RuntimeError("Instagram did not return the carousel container id")
        _wait_container(cfg, token, creation_id)

    published = _request_json(
        f"{cfg.graph_base}/{cfg.account_id}/media_publish",
        token,
        payload={"creation_id": creation_id},
        timeout=max(30, cfg.timeout),
    )
    media_id = str(published.get("id") or "").strip()
    if not media_id:
        raise RuntimeError("Instagram did not return the published media id")
    receipt_payload = {
        "channel": "instagram",
        "media_id": media_id,
        "creation_id": creation_id,
        "site_product_url": payload["product_url"],
        "tracking_url": payload["tracking_url"],
        "media_urls": media_urls,
        "caption": payload["caption"],
        "alt_texts": list(payload.get("alt_texts") or []),
        "hashtags": list(payload.get("hashtags") or []),
        "social_policy_version": str(payload.get("social_policy_version") or ""),
        "site_ack_fingerprint": fingerprint,
        "api_version": cfg.api_version,
        "login_mode": cfg.login_mode,
    }
    db.record_sync_receipt(
        int(product_id),
        f"instagram:{creation_id}",
        "instagram_published",
        server_id=media_id,
        payload=receipt_payload,
    )
    return receipt_payload


def test_connection(cfg: InstagramConfig) -> dict[str, Any]:
    token = get_secret("instagram_access_token")
    if not token:
        raise RuntimeError("Instagram Access Token تنظیم نشده است.")
    result = _request_json(
        f"{cfg.graph_base}/{cfg.account_id}?fields=id,username,account_type",
        token,
        timeout=cfg.timeout,
    )
    return {
        "id": str(result.get("id") or ""),
        "username": str(result.get("username") or ""),
        "account_type": str(result.get("account_type") or ""),
    }
