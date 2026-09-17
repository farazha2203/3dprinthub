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
