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
    channel_id: str = ""
    timeout: int = 30
    mode: str = "shareNow"


def _graphql(token: str, query: str, variables: dict[str, Any] | None = None, *, timeout: int = 30) -> dict[str, Any]:
    body = json.dumps({"query": query, "variables": variables or {}}, ensure_ascii=False).encode("utf-8")
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
            payload = json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1600]
        raise RuntimeError(f"Buffer HTTP {exc.code}: {detail}") from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"Buffer network error: {exc.reason}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Buffer API returned an invalid JSON object")
    if payload.get("errors"):
        raise RuntimeError(f"Buffer GraphQL error: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise RuntimeError("Buffer GraphQL response does not contain data")
    return data


def _token() -> str:
    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key is not configured in Windows Credential Store.")
    return token


def discover_instagram_channels(*, timeout: int = 30) -> list[dict[str, Any]]:
    token = _token()
    account = _graphql(
        token,
        """
        query BufferOrganizations {
          account {
            organizations { id name }
          }
        }
        """,
        timeout=timeout,
    )
    organizations = list((account.get("account") or {}).get("organizations") or [])
    output: list[dict[str, Any]] = []
    for organization in organizations:
        organization_id = str(organization.get("id") or "").strip()
        if not organization_id:
            continue
        data = _graphql(
            token,
            """
            query BufferChannels($organizationId: OrganizationId!) {
              channels(input: { organizationId: $organizationId }) {
                id
                name
                displayName
                service
                externalLink
                isLocked
                isDisconnected
              }
            }
            """,
            {"organizationId": organization_id},
            timeout=timeout,
        )
        for channel in list(data.get("channels") or []):
            if str(channel.get("service") or "").lower() != "instagram":
                continue
            item = dict(channel)
            item["organization_id"] = organization_id
            item["organization_name"] = str(organization.get("name") or "")
            output.append(item)
    return output


def resolve_instagram_channel(cfg: BufferConfig) -> dict[str, Any]:
    token = _token()
    channel_id = str(cfg.channel_id or "").strip()
    if channel_id:
        data = _graphql(
            token,
            """
            query BufferChannel($id: ChannelId!) {
              channel(input: { id: $id }) {
                id
                name
                displayName
                service
                externalLink
                isLocked
                isDisconnected
              }
            }
            """,
            {"id": channel_id},
            timeout=cfg.timeout,
        )
        channel = dict(data.get("channel") or {})
        if str(channel.get("service") or "").lower() != "instagram":
            raise RuntimeError("Configured Buffer channel is not an Instagram channel.")
        if bool(channel.get("isLocked")) or bool(channel.get("isDisconnected")):
            raise RuntimeError("Configured Buffer Instagram channel is locked or disconnected.")
        return channel

    channels = [
        item
        for item in discover_instagram_channels(timeout=cfg.timeout)
        if not bool(item.get("isLocked")) and not bool(item.get("isDisconnected"))
    ]
    if len(channels) == 1:
        return channels[0]
    if not channels:
        raise RuntimeError("No connected and active Instagram channel was found in Buffer.")
    choices = ", ".join(
        f"{item.get('displayName') or item.get('name') or 'Instagram'} [{item.get('id')}]"
        for item in channels[:8]
    )
    raise RuntimeError("More than one Instagram channel exists in Buffer; configure Buffer Channel ID: " + choices)


def test_connection(cfg: BufferConfig) -> dict[str, Any]:
    channel = resolve_instagram_channel(cfg)
    return {
        "id": str(channel.get("id") or ""),
        "name": str(channel.get("displayName") or channel.get("name") or "Instagram"),
        "service": str(channel.get("service") or ""),
        "external_link": str(channel.get("externalLink") or ""),
    }


def _already_published(db, product_id: int, fingerprint: str) -> bool:
    for receipt in db.sync_receipts(int(product_id), limit=60):
        if str(receipt["status"] or "") != "buffer_instagram_published":
            continue
        try:
            previous = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            previous = {}
        if str(previous.get("site_ack_fingerprint") or "") == fingerprint:
            return True
    return False


def publish_product(db, product_id: int, cfg: BufferConfig, *, site_url: str) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    data = dict(row)
    payload = canonical_site_payload(data, site_url=site_url, utm_source="instagram", utm_medium="social", utm_campaign="product")
    fingerprint = str(data.get("server_ack_json") or "").strip()
    if _already_published(db, int(product_id), fingerprint):
        raise RuntimeError("This public Product revision was already published to Instagram through Buffer.")

    channel = resolve_instagram_channel(cfg)
    token = _token()
    media_urls = list(payload["media_urls"])
    alt_texts = list(payload["alt_texts"])
    title = str(payload.get("title") or "Product").strip() or "Product"
    assets = []
    for index, url in enumerate(media_urls):
        alt = (alt_texts[index] if index < len(alt_texts) else "").strip() or title
        assets.append({"image": {"url": url, "metadata": {"altText": alt[:1000]}}})

    post_type = "carousel" if len(assets) > 1 else "post"
    variables = {
        "input": {
            "text": payload["caption"],
            "channelId": str(channel.get("id") or ""),
            "schedulingType": "automatic",
            "mode": str(cfg.mode or "shareNow"),
            "assets": assets,
            "metadata": {
                "instagram": {
                    "type": post_type,
                    "shouldShareToFeed": True,
                    "link": payload["tracking_url"],
                }
            },
        }
    }
    result = _graphql(
        token,
        """
        mutation CreateInstagramPost($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post { id text externalLink }
            }
            ... on MutationError { message }
          }
        }
        """,
        variables,
        timeout=cfg.timeout,
    )
    created = dict(result.get("createPost") or {})
    message = str(created.get("message") or "").strip()
    if message and not created.get("post"):
        raise RuntimeError(f"Buffer createPost failed: {message}")
    post = dict(created.get("post") or {})
    post_id = str(post.get("id") or "").strip()
    if not post_id:
        raise RuntimeError("Buffer did not return a Post ID")

    receipt_payload = {
        "channel": "instagram",
        "provider": "buffer",
        "provider_post_id": post_id,
        "buffer_post_id": post_id,
        "external_link": str(post.get("externalLink") or ""),
        "buffer_channel_id": str(channel.get("id") or ""),
        "site_product_url": payload["product_url"],
        "tracking_url": payload["tracking_url"],
        "media_urls": media_urls,
        "caption": payload["caption"],
        "site_ack_fingerprint": fingerprint,
    }
    db.record_sync_receipt(
        int(product_id),
        f"buffer-instagram:{post_id}",
        "buffer_instagram_published",
        server_id=post_id,
        payload=receipt_payload,
    )
    return receipt_payload
