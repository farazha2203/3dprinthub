from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from .instagram_publish import (
    canonical_site_payload,
    same_public_revision_already_published,
)
from .secure_secrets import get_secret


BUFFER_GRAPHQL_URL = "https://api.buffer.com"


@dataclass(frozen=True)
class BufferConfig:
    channel_id: str
    timeout: int = 30


def _request_graphql(
    token: str,
    query: str,
    *,
    variables: dict[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    body = json.dumps(
        {"query": query, "variables": variables or {}},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib_request.Request(
        BUFFER_GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
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
    id
    name
    displayName
    service
    externalLink
  }
}
"""

_CREATE_POST_MUTATION = """
mutation CreateInstagramPost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess {
      post {
        id
        status
        externalLink
      }
    }
    ... on MutationError {
      message
    }
  }
}
"""


def test_connection(cfg: BufferConfig) -> dict[str, Any]:
    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key در Windows Credential Store ذخیره نشده است.")
    data = _request_graphql(
        token,
        _CHANNEL_QUERY,
        variables={"id": cfg.channel_id},
        timeout=cfg.timeout,
    )
    channel = data.get("channel")
    if not isinstance(channel, dict):
        raise RuntimeError("Buffer channel was not returned")
    service = str(channel.get("service") or "").lower()
    if service != "instagram":
        raise RuntimeError("Buffer Channel انتخاب‌شده مربوط به Instagram نیست.")
    return {
        "id": str(channel.get("id") or ""),
        "name": str(channel.get("displayName") or channel.get("name") or ""),
        "service": service,
        "external_link": str(channel.get("externalLink") or ""),
    }


def publish_product(
    db,
    product_id: int,
    cfg: BufferConfig,
    *,
    site_url: str,
) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    data = dict(row)
    payload = canonical_site_payload(data, site_url=site_url)
    fingerprint = str(data.get("server_ack_json") or "").strip()
    if same_public_revision_already_published(db, int(product_id), fingerprint):
        raise RuntimeError("این نسخه عمومی محصول قبلاً برای Instagram ارسال شده است.")

    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key در Windows Credential Store ذخیره نشده است.")

    media_urls = list(payload["media_urls"])
    alt_texts = list(payload["alt_texts"])
    assets: list[dict[str, Any]] = []
    for index, url in enumerate(media_urls):
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
        "metadata": {"instagram": {"type": "post", "shouldShareToFeed": True}},
    }
    response = _request_graphql(
        token,
        _CREATE_POST_MUTATION,
        variables={"input": create_input},
        timeout=cfg.timeout,
    )
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
        "media_id": "",
        "site_product_url": payload["product_url"],
        "tracking_url": payload["tracking_url"],
        "media_urls": media_urls,
        "caption": payload["caption"],
        "site_ack_fingerprint": fingerprint,
        "buffer_channel_id": cfg.channel_id,
        "buffer_status": post_status,
        "external_link": str(post.get("externalLink") or ""),
    }
    db.record_sync_receipt(
        int(product_id),
        f"instagram:buffer:{post_id}",
        receipt_status,
        server_id=post_id,
        payload=receipt_payload,
    )
    return receipt_payload
