from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

from .instagram_publish import canonical_site_payload
from .secure_secrets import get_secret
from .social_content_policy import highlight_target_for_product

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


_ACCOUNT_ORGS_QUERY = """
query BufferOrganizations {
  account { organizations { id name } }
}
"""

_RECENT_POSTS_QUERY = """
query BufferRecentPosts($org: OrganizationId!, $channel: ChannelId!) {
  posts(
    first: 30
    input: {
      organizationId: $org
      sort: [{field: createdAt, direction: desc}]
      filter: {status: [sent, sending, error], channelIds: [$channel]}
    }
  ) {
    edges {
      node {
        id status externalLink
        assets { source thumbnail }
      }
    }
  }
}
"""


def _receipt_for_revision(db, product_id: int, fingerprint: str, statuses: set[str]) -> dict[str, Any] | None:
    if not fingerprint:
        return None
    for receipt in db.sync_receipts(int(product_id), limit=160):
        if str(receipt["status"] or "") not in statuses:
            continue
        try:
            previous = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            previous = {}
        if str(previous.get("site_ack_fingerprint") or "") == fingerprint:
            return dict(previous)
    return None


def _reconcile_recent_asset(token: str, cfg: BufferConfig, asset_url: str) -> dict[str, Any] | None:
    try:
        account = _request_graphql(token, _ACCOUNT_ORGS_QUERY, timeout=cfg.timeout).get("account") or {}
        organizations = account.get("organizations") or []
    except Exception:
        return None
    for organization in organizations:
        org_id = str((organization or {}).get("id") or "").strip()
        if not org_id:
            continue
        try:
            data = _request_graphql(
                token,
                _RECENT_POSTS_QUERY,
                variables={"org": org_id, "channel": cfg.channel_id},
                timeout=cfg.timeout,
            )
        except Exception:
            continue
        for edge in (data.get("posts") or {}).get("edges") or []:
            node = (edge or {}).get("node") or {}
            urls = [
                str((asset or {}).get("source") or (asset or {}).get("thumbnail") or "")
                for asset in node.get("assets") or []
            ]
            if asset_url not in urls:
                continue
            status = str(node.get("status") or "").strip().lower()
            if status in {"sent", "sending"}:
                return {
                    "id": str(node.get("id") or ""),
                    "status": status,
                    "externalLink": str(node.get("externalLink") or ""),
                }
    return None

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


def publish_product(
    db,
    product_id: int,
    cfg: BufferConfig,
    *,
    site_url: str,
    media_urls_override: list[str] | None = None,
    media_host_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"Product {product_id} not found")
    data = dict(row)
    payload = canonical_site_payload(data, site_url=site_url)
    fingerprint = str(data.get("server_ack_json") or "").strip()
    existing_feed = _receipt_for_revision(
        db,
        int(product_id),
        fingerprint,
        {"instagram_published", "instagram_submitted"},
    )
    if existing_feed is not None:
        existing_feed["resume_status"] = "already_sent"
        return existing_feed
    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key is not configured in the secure secret store.")

    provider_media_urls = [
        str(value or "").strip()
        for value in (media_urls_override or payload["media_urls"])
        if str(value or "").strip()
    ]
    if not provider_media_urls:
        raise RuntimeError("No public media URLs are available for Buffer.")
    assets: list[dict[str, Any]] = []
    alt_texts = list(payload.get("alt_texts") or [])
    for index, url in enumerate(provider_media_urls):
        alt_text = alt_texts[index] if index < len(alt_texts) else ""
        if not str(alt_text or "").strip():
            raise RuntimeError(f"Alt Text تصویر {index + 1} خالی است؛ انتشار Instagram متوقف شد.")
        image: dict[str, Any] = {
            "url": url,
            "metadata": {"altText": str(alt_text)[:1000]},
        }
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
                "isAiGenerated": False,
                "link": payload["tracking_url"],
            }
        },
    }
    try:
        response = _request_graphql(
            token,
            _CREATE_POST_MUTATION,
            variables={"input": create_input},
            timeout=cfg.timeout,
        )
    except RuntimeError as exc:
        text = str(exc)
        if "502" not in text and "UPSTREAM_SERVER_ERROR" not in text:
            raise
        post = _reconcile_recent_asset(
            token,
            cfg,
            str(payload["media_urls"][0]),
        )
        if post is None:
            raise
    else:
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
        "tracking_url": payload["tracking_url"],
        "media_urls": list(provider_media_urls),
        "source_media_urls": list(payload["media_urls"]),
        "caption": payload["caption"],
        "alt_texts": list(payload.get("alt_texts") or []),
        "hashtags": list(payload.get("hashtags") or []),
        "social_policy_version": str(payload.get("social_policy_version") or ""),
        "site_ack_fingerprint": fingerprint,
        "buffer_channel_id": cfg.channel_id,
        "buffer_status": post_status,
        "external_link": str(post.get("externalLink") or ""),
        "media_host": str((media_host_meta or {}).get("host") or "site"),
        "media_host_branch": str((media_host_meta or {}).get("branch") or ""),
        "media_host_commit_sha": str((media_host_meta or {}).get("commit_sha") or ""),
    }
    db.record_sync_receipt(int(product_id), f"instagram:buffer:{post_id}", receipt_status, server_id=post_id, payload=receipt_payload)
    return receipt_payload

# --- 3DPrintHub Instagram companion-story policy ---
_publish_feed_product = publish_product


def _story_already_sent(db, product_id: int, fingerprint: str) -> bool:
    if not fingerprint:
        return False
    for receipt in db.sync_receipts(int(product_id), limit=120):
        if str(receipt["status"] or "") not in {
            "instagram_story_published",
            "instagram_story_submitted",
            "instagram_story_notification_ready",
        }:
            continue
        try:
            previous = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            previous = {}
        if str(previous.get("site_ack_fingerprint") or "") == fingerprint:
            return True
    return False


def publish_story_for_product(
    db,
    product_id: int,
    cfg: BufferConfig,
    *,
    site_url: str,
    story_url_override: str = "",
    story_meta: dict[str, Any] | None = None,
    link_notification: bool = True,
) -> dict[str, Any]:
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
    story_url = str(story_url_override or "").strip()
    story_source = "generated_branded_story" if story_url.startswith("https://") else ""
    if not story_url.startswith("https://"):
        story_url = str(ack.get("instagram_story_url") or ack.get("social_story_url") or "").strip()
        story_source = "branded_story_asset" if story_url.startswith("https://") else ""
    if not story_url.startswith("https://"):
        story_url = str((payload.get("media_urls") or [""])[0]).strip()
        story_source = "product_media_fallback"
    if not story_url.startswith("https://"):
        raise RuntimeError("A public HTTPS Story asset is required for Buffer/Instagram.")

    image: dict[str, Any] = {"url": story_url}
    alt_texts = list(payload.get("alt_texts") or [])
    if alt_texts and alt_texts[0]:
        image["metadata"] = {"altText": str(alt_texts[0])[:1000]}

    ai_generated = bool(
        data.get("instagram_story_ai_generated")
        or data.get("social_ai_generated")
    )
    tracking_url = str(payload.get("tracking_url") or payload["product_url"])
    instagram_metadata: dict[str, Any] = {
        "type": "story",
        "shouldShareToFeed": False,
        "isAiGenerated": ai_generated,
        # Buffer can carry the tracked Product link, while the native
        # Instagram Story Link Sticker still requires notification handoff.
        "link": tracking_url,
    }
    scheduling_type = "automatic"
    if link_notification:
        scheduling_type = "notification"
        instagram_metadata["stickerFields"] = {
            "text": "لینک محصول",
            "other": f'Link Sticker: "لینک محصول" → {tracking_url}',
        }
    create_input = {
        "text": "",
        "channelId": cfg.channel_id,
        "schedulingType": scheduling_type,
        "mode": "shareNow",
        "needsApproval": False,
        "saveToDraft": False,
        "source": "3dprinthub-windows-companion-story",
        "assets": [{"image": image}],
        "metadata": {"instagram": instagram_metadata},
    }
    try:
        response = _request_graphql(
            token,
            _CREATE_POST_MUTATION,
            variables={"input": create_input},
            timeout=cfg.timeout,
        )
    except RuntimeError as exc:
        text = str(exc)
        if "502" not in text and "UPSTREAM_SERVER_ERROR" not in text:
            raise
        post = _reconcile_recent_asset(token, cfg, story_url)
        if post is None:
            raise
    else:
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
    if link_notification:
        receipt_status = "instagram_story_notification_ready"
    else:
        receipt_status = (
            "instagram_story_published"
            if provider_status == "sent"
            else "instagram_story_submitted"
        )
    receipt_payload = {
        "channel": "instagram_story",
        "provider": "buffer",
        "provider_post_id": story_id,
        "site_product_url": payload["product_url"],
        "tracking_url": tracking_url,
        "story_publish_mode": "notification" if link_notification else "automatic",
        "link_sticker_required": bool(link_notification),
        "link_sticker_label": "لینک محصول" if link_notification else "",
        "instagram_live_confirmed": (
            False if link_notification else provider_status == "sent"
        ),
        "story_asset_url": story_url,
        "story_asset_source": story_source,
        "story_style_id": str((story_meta or {}).get("style_id") or ""),
        "story_font_family": str((story_meta or {}).get("font_family") or ""),
        "story_width": int((story_meta or {}).get("width") or 0),
        "story_height": int((story_meta or {}).get("height") or 0),
        "media_host": str((story_meta or {}).get("provider_media_host") or "site"),
        "media_host_commit_sha": str(
            (story_meta or {}).get("provider_media_commit_sha") or ""
        ),
        "social_policy_version": str(payload.get("social_policy_version") or ""),
        "site_ack_fingerprint": fingerprint,
        "buffer_channel_id": cfg.channel_id,
        "buffer_status": provider_status,
        "highlight_target": highlight_target_for_product(data),
        "highlight_status": "operator_required",
        "external_link": str(post.get("externalLink") or ""),
    }
    db.record_sync_receipt(int(product_id), f"instagram:buffer:story:{story_id}", receipt_status, server_id=story_id, payload=receipt_payload)
    return receipt_payload


def reconcile_product_receipts(
    db,
    product_id: int,
    cfg: BufferConfig,
) -> dict[str, Any]:
    """Append final receipt evidence when Buffer has moved a submitted post to sent."""

    row_obj = db.product(int(product_id))
    if row_obj is None:
        raise RuntimeError(f"Product {product_id} not found")
    row = dict(row_obj)
    fingerprint = str(row.get("server_ack_json") or "").strip()
    token = get_secret("buffer_api_key")
    if not token:
        raise RuntimeError("Buffer API Key is not configured in the secure secret store.")

    receipts = list(db.sync_receipts(int(product_id), limit=160))
    final_statuses = {
        "instagram_submitted": "instagram_published",
        "instagram_story_submitted": "instagram_story_published",
    }
    already_final: set[tuple[str, str]] = set()
    parsed: list[tuple[Any, dict[str, Any]]] = []
    for receipt in receipts:
        try:
            payload = json.loads(receipt["payload_json"] or "{}")
        except Exception:
            payload = {}
        parsed.append((receipt, payload))
        status = str(receipt["status"] or "")
        if status in final_statuses.values():
            already_final.add((status, str(payload.get("site_ack_fingerprint") or "")))

    reconciled: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    for receipt, payload in parsed:
        status = str(receipt["status"] or "")
        final_status = final_statuses.get(status)
        if not final_status:
            continue
        if fingerprint and str(payload.get("site_ack_fingerprint") or "") != fingerprint:
            continue
        if (final_status, fingerprint) in already_final:
            continue

        if status == "instagram_submitted":
            urls = [
                str(value or "").strip()
                for value in payload.get("media_urls") or []
                if str(value or "").strip()
            ]
            asset_url = urls[0] if urls else ""
        else:
            asset_url = str(payload.get("story_asset_url") or "").strip()
        if not asset_url:
            pending.append({"status": status, "reason": "asset_url_missing"})
            continue

        post = _reconcile_recent_asset(token, cfg, asset_url)
        if not post or str(post.get("status") or "").lower() != "sent":
            pending.append(
                {
                    "status": status,
                    "provider_post_id": str((post or {}).get("id") or ""),
                    "provider_status": str((post or {}).get("status") or ""),
                }
            )
            continue

        final_payload = {
            **payload,
            "provider_post_id": str(post.get("id") or payload.get("provider_post_id") or ""),
            "buffer_status": "sent",
            "external_link": str(post.get("externalLink") or payload.get("external_link") or ""),
            "reconciled_from_receipt_id": int(receipt["id"] or 0),
            "reconciled_without_repost": True,
        }
        provider_id = str(final_payload.get("provider_post_id") or "")
        db.record_sync_receipt(
            int(product_id),
            f"instagram:buffer:reconcile:{provider_id}",
            final_status,
            server_id=provider_id,
            payload=final_payload,
        )
        already_final.add((final_status, fingerprint))
        reconciled.append(
            {
                "status": final_status,
                "provider_post_id": provider_id,
                "external_link": final_payload["external_link"],
            }
        )

    return {
        "product_id": int(product_id),
        "reconciled": reconciled,
        "pending": pending,
    }


def publish_product(
    db,
    product_id: int,
    cfg: BufferConfig,
    *,
    site_url: str,
    companion_story: bool | None = None,
    story_link_notification: bool | None = None,
    story_asset_url: str = "",
    story_meta: dict[str, Any] | None = None,
    feed_asset_urls: list[str] | None = None,
    media_host_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    feed = _publish_feed_product(
        db,
        product_id,
        cfg,
        site_url=site_url,
        media_urls_override=feed_asset_urls,
        media_host_meta=media_host_meta,
    )
    if companion_story is None:
        if hasattr(db, "setting"):
            raw = str(db.setting("instagram_companion_story_enabled", "1") or "1").strip().lower()
            companion_story = raw not in {"0", "false", "no", "off"}
        else:
            companion_story = False
    if not companion_story:
        return feed
    if story_link_notification is None:
        if hasattr(db, "setting"):
            raw = str(
                db.setting("instagram_story_clickable_link_enabled", "1") or "1"
            ).strip().lower()
            story_link_notification = raw not in {"0", "false", "no", "off"}
        else:
            story_link_notification = True
    try:
        feed["companion_story"] = publish_story_for_product(
            db,
            product_id,
            cfg,
            site_url=site_url,
            story_url_override=story_asset_url,
            story_meta=story_meta,
            link_notification=bool(story_link_notification),
        )
    except Exception as exc:
        error_payload = {
            "provider": "buffer",
            "error": str(exc),
            "feed_post_id": feed.get("provider_post_id") or "",
            "story_asset_url": story_asset_url,
        }
        try:
            db.record_sync_receipt(
                int(product_id),
                f"instagram:buffer:story-failed:{feed.get('provider_post_id') or product_id}",
                "instagram_story_failed",
                server_id=str(feed.get("provider_post_id") or ""),
                payload=error_payload,
            )
        except Exception:
            pass
        raise RuntimeError(
            "Feed Instagram ثبت شد اما Story همراه کامل نشد؛ Retry فقط Story را تکمیل می‌کند: "
            + str(exc)
        ) from exc
    return feed
