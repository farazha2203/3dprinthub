from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from .instagram_publish import canonical_site_payload
from .secure_secrets import get_secret

BUFFER_GRAPHQL_URL = "https://api.buffer.com"


@dataclass(frozen=True)
class BufferConfig:
    channel_id: str
    timeout: int = 30


def _request_graphql(token: str, query: str, *, variables=None, timeout: int = 30) -> dict[str, Any]:
    body = json.dumps({"query": query, "variables": variables or {}}, ensure_ascii=False).encode("utf-8")
    req = urllib_request.Request(
        BUFFER_GRAPHQL_URL,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=max(10, int(timeout))) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1600]
        raise RuntimeError(f"Buffer HTTP {exc.code}: {detail}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Buffer API returned an invalid JSON object")
    if data.get("errors"):
        raise RuntimeError(f"Buffer API error: {data['errors']}")
    payload = data.get("data")
    if not isinstance(payload, dict):
        raise RuntimeError("Buffer API response did not contain data")
    return payload


_CHANNEL_QUERY = """
query BufferInstagramChannel($id: ChannelId!) {
  channel(input: {id: $id}) {
    id name displayName service externalLink isDisconnected isLocked
  }
}
"""

_CREATE_POST_MUTATION = """
mutation CreateInstagramPost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id status externalLink } }
    ... on MutationError { message }
  }
}
"""


def _already_sent(db, product_id: int, fingerprint: str) -> bool:
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


def test_connection(cfg: BufferConfig) -> dict[str, Any]:
    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key is not configured in the secure secret store.")
    data = _request_graphql(token, _CHANNEL_QUERY, variables={"id": cfg.channel_id}, timeout=cfg.timeout)
    channel = data.get("channel")
    if not isinstance(channel, dict):
        raise RuntimeError("Buffer channel was not returned")
    if str(channel.get("service") or "").lower() != "instagram":
        raise RuntimeError("Configured Buffer channel is not an Instagram channel.")
    if bool(channel.get("isDisconnected")):
        raise RuntimeError("Buffer Instagram channel is disconnected.")
    if bool(channel.get("isLocked")):
        raise RuntimeError("Buffer Instagram channel is locked.")
    return {
        "id": str(channel.get("id") or ""),
        "name": str(channel.get("displayName") or channel.get("name") or ""),
        "service": "instagram",
        "external_link": str(channel.get("externalLink") or ""),
    }


def publish_product(db, product_id: int, cfg: BufferConfig, *, site_url: str) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    data = dict(row)
    payload = canonical_site_payload(data, site_url=site_url)
    fingerprint = str(data.get("server_ack_json") or "").strip()
    if _already_sent(db, int(product_id), fingerprint):
        raise RuntimeError("This public Product revision was already submitted to Instagram.")
    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key is not configured in the secure secret store.")

    assets: list[dict[str, Any]] = []
    alt_texts = list(payload.get("alt_texts") or [])
    for index, url in enumerate(payload["media_urls"]):
        image: dict[str, Any] = {"url": url}
        alt_text = alt_texts[index] if index < len(alt_texts) else ""
        if alt_text:
            image["metadata"] = {"altText": alt_text[:1000]}
        assets.append({"image": image})

    create_input = {
        "text": payload["caption"],
        "channelId": cfg.channel_id,
        "schedulingType": "automatic",
        "mode": "shareNow",
        "needsApproval": False,
        "saveToDraft": False,
        "source": "3dprinthub-windows",
        "assets": assets,
        "metadata": {
            "instagram": {
                "type": "post",
                "shouldShareToFeed": True,
                "link": payload["product_url"],
            }
        },
    }
    response = _request_graphql(token, _CREATE_POST_MUTATION, variables={"input": create_input}, timeout=cfg.timeout)
    result = response.get("createPost")
    if not isinstance(result, dict):
        raise RuntimeError("Buffer did not return createPost result")
    post = result.get("post")
    if not isinstance(post, dict):
        raise RuntimeError(str(result.get("message") or "Buffer post creation failed"))

    post_id = str(post.get("id") or "").strip()
    if not post_id:
        raise RuntimeError("Buffer did not return a post id")
    post_status = str(post.get("status") or "").strip().lower()
    receipt_status = "instagram_published" if post_status == "sent" else "instagram_submitted"
    receipt_payload = {
        "channel": "instagram",
        "provider": "buffer",
        "provider_post_id": post_id,
        "site_product_url": payload["product_url"],
        "media_urls": list(payload["media_urls"]),
        "caption": payload["caption"],
        "site_ack_fingerprint": fingerprint,
        "buffer_channel_id": cfg.channel_id,
        "buffer_status": post_status,
        "external_link": str(post.get("externalLink") or ""),
    }
    db.record_sync_receipt(int(product_id), f"instagram:buffer:{post_id}", receipt_status, server_id=post_id, payload=receipt_payload)
    return receipt_payload

# --- 3DPrintHub Instagram companion-story policy ---
_publish_feed_product = publish_product


def _story_already_sent(db, product_id: int, fingerprint: str) -> bool:
    if not fingerprint:
        return False
    for receipt in db.sync_receipts(int(product_id), limit=120):
        if str(receipt["status"] or "") not in {"instagram_story_published", "instagram_story_submitted"}:
            continue
        try:
            previous = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            previous = {}
        if str(previous.get("site_ack_fingerprint") or "") == fingerprint:
            return True
    return False


def publish_story_for_product(db, product_id: int, cfg: BufferConfig, *, site_url: str) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    data = dict(row)
    payload = canonical_site_payload(data, site_url=site_url)
    fingerprint = str(data.get("server_ack_json") or "").strip()
    if _story_already_sent(db, int(product_id), fingerprint):
        return {"status": "already_sent", "site_product_url": payload["product_url"]}

    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key is not configured in the secure secret store.")

    ack = {}
    try:
        ack = json.loads(data.get("server_ack_json") or "{}")
    except Exception:
        ack = {}
    story_url = str(ack.get("instagram_story_url") or ack.get("social_story_url") or "").strip()
    story_source = "branded_story_asset" if story_url.startswith("https://") else "product_media_fallback"
    if not story_url.startswith("https://"):
        story_url = str((payload.get("media_urls") or [""])[0]).strip()
    if not story_url.startswith("https://"):
        raise RuntimeError("A public HTTPS Story asset is required for Buffer/Instagram.")

    image: dict[str, Any] = {"url": story_url}
    alt_texts = list(payload.get("alt_texts") or [])
    if alt_texts and alt_texts[0]:
        image["metadata"] = {"altText": str(alt_texts[0])[:1000]}

    ai_generated = bool(data.get("instagram_story_ai_generated") or data.get("social_ai_generated"))
    create_input = {
        "text": "",
        "channelId": cfg.channel_id,
        "schedulingType": "automatic",
        "mode": "shareNow",
        "needsApproval": False,
        "saveToDraft": False,
        "source": "3dprinthub-windows-companion-story",
        "assets": [{"image": image}],
        "metadata": {
            "instagram": {
                "type": "story",
                "shouldShareToFeed": False,
                "isAiGenerated": ai_generated,
            }
        },
    }
    response = _request_graphql(token, _CREATE_POST_MUTATION, variables={"input": create_input}, timeout=cfg.timeout)
    result = response.get("createPost")
    if not isinstance(result, dict):
        raise RuntimeError("Buffer did not return createPost result for Story")
    post = result.get("post")
    if not isinstance(post, dict):
        raise RuntimeError(str(result.get("message") or "Buffer Story creation failed"))
    story_id = str(post.get("id") or "").strip()
    if not story_id:
        raise RuntimeError("Buffer did not return a Story post id")
    provider_status = str(post.get("status") or "").strip().lower()
    receipt_status = "instagram_story_published" if provider_status == "sent" else "instagram_story_submitted"
    receipt_payload = {
        "channel": "instagram_story",
        "provider": "buffer",
        "provider_post_id": story_id,
        "site_product_url": payload["product_url"],
        "tracking_url": payload.get("tracking_url") or payload["product_url"],
        "story_asset_url": story_url,
        "story_asset_source": story_source,
        "site_ack_fingerprint": fingerprint,
        "buffer_channel_id": cfg.channel_id,
        "buffer_status": provider_status,
        "highlight_target": str(data.get("instagram_highlight") or data.get("social_highlight") or "").strip(),
        "highlight_status": "operator_required",
        "external_link": str(post.get("externalLink") or ""),
    }
    db.record_sync_receipt(int(product_id), f"instagram:buffer:story:{story_id}", receipt_status, server_id=story_id, payload=receipt_payload)
    return receipt_payload


def publish_product(db, product_id: int, cfg: BufferConfig, *, site_url: str, companion_story: bool | None = None) -> dict[str, Any]:
    feed = _publish_feed_product(db, product_id, cfg, site_url=site_url)
    if companion_story is None:
        if hasattr(db, "setting"):
            raw = str(db.setting("instagram_companion_story_enabled", "1") or "1").strip().lower()
            companion_story = raw not in {"0", "false", "no", "off"}
        else:
            companion_story = False
    if not companion_story:
        return feed
    try:
        feed["companion_story"] = publish_story_for_product(db, product_id, cfg, site_url=site_url)
    except Exception as exc:
        feed["companion_story"] = {"status": "failed", "error": str(exc)}
        try:
            db.record_sync_receipt(
                int(product_id),
                f"instagram:buffer:story-failed:{feed.get('provider_post_id') or product_id}",
                "instagram_story_failed",
                server_id=str(feed.get("provider_post_id") or ""),
                payload={"provider": "buffer", "error": str(exc), "feed_post_id": feed.get("provider_post_id") or ""},
            )
        except Exception:
            pass
    return feed

