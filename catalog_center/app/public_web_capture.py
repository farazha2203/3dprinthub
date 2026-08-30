from __future__ import annotations

import hashlib
import json
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SENSITIVE_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "credential",
    "key",
    "password",
    "secret",
    "session",
    "signature",
    "sig",
    "token",
}


def same_site(left: str, right: str) -> bool:
    """Return True for the same host or parent/subdomain relationship."""
    a = (urlsplit(str(left or "")).hostname or "").lower().lstrip(".")
    b = (urlsplit(str(right or "")).hostname or "").lower().lstrip(".")
    return bool(a and b and (a == b or a.endswith("." + b) or b.endswith("." + a)))


def sanitize_public_url(url: str) -> str:
    """Keep a useful public endpoint identity without persisting credential-like query values."""
    parsed = urlsplit(str(url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    clean_query: list[tuple[str, str]] = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        folded = key.casefold()
        if folded in SENSITIVE_QUERY_KEYS or any(
            token in folded for token in ("token", "secret", "signature", "password", "credential")
        ):
            value = "<redacted>"
        clean_query.append((key, value))
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "/",
            urlencode(clean_query, doseq=True),
            "",
        )
    )


def _shape_paths(value: Any, *, max_depth: int = 4, max_paths: int = 120) -> list[str]:
    """Describe JSON structure only; never copy scalar values into provenance."""
    paths: list[str] = []
    seen: set[str] = set()

    def visit(node: Any, prefix: str, depth: int) -> None:
        if len(paths) >= max_paths or depth > max_depth:
            return
        if isinstance(node, dict):
            for key in sorted(node, key=lambda item: str(item).casefold()):
                name = str(key)[:120]
                path = f"{prefix}.{name}" if prefix else name
                if path not in seen:
                    seen.add(path)
                    paths.append(path)
                    if len(paths) >= max_paths:
                        return
                visit(node.get(key), path, depth + 1)
        elif isinstance(node, list) and node:
            visit(node[0], f"{prefix}[]" if prefix else "[]", depth + 1)

    visit(value, "", 0)
    return paths


def summarize_packet(source_url: str, packet: dict[str, Any]) -> dict[str, Any] | None:
    raw_url = str(packet.get("url") or "")
    if not raw_url.startswith(("http://", "https://")) or not same_site(source_url, raw_url):
        return None

    content_type = str(packet.get("content_type") or "").lower().split(";", 1)[0]
    resource_type = str(packet.get("resource_type") or "").lower()
    if "json" not in content_type and resource_type not in {"xhr", "fetch"}:
        return None

    clean_url = sanitize_public_url(raw_url)
    if not clean_url:
        return None

    data = packet.get("data")
    paths = _shape_paths(data)
    shape_payload = json.dumps(paths, ensure_ascii=True, separators=(",", ":"))
    shape_hash = hashlib.sha256(shape_payload.encode("utf-8")).hexdigest()[:24]

    return {
        "url": clean_url,
        "status": int(packet.get("status") or 0),
        "method": str(packet.get("method") or "GET").upper()[:12],
        "resource_type": resource_type[:40],
        "content_type": content_type[:120],
        "body_bytes": max(0, int(packet.get("body_bytes") or 0)),
        "response_schema": paths,
        "shape_hash": shape_hash,
    }


def build_public_capture_summary(
    source_url: str,
    packets: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    json_ld_count: int = 0,
    embedded_json_count: int = 0,
    breadcrumb_count: int = 0,
    spec_row_count: int = 0,
) -> dict[str, Any]:
    """Persist bounded public structure/provenance, never raw XHR/Fetch payloads."""
    endpoint_hints: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for packet in packets or ():
        if not isinstance(packet, dict):
            continue
        summary = summarize_packet(source_url, packet)
        if summary is None:
            continue
        key = (
            str(summary["url"]),
            str(summary["method"]),
            str(summary["shape_hash"]),
        )
        if key in seen:
            continue
        seen.add(key)
        endpoint_hints.append(summary)
        if len(endpoint_hints) >= 40:
            break

    return {
        "json_ld_count": max(0, int(json_ld_count or 0)),
        "embedded_json_count": max(0, int(embedded_json_count or 0)),
        "network_json_count": len(endpoint_hints),
        "breadcrumb_count": max(0, int(breadcrumb_count or 0)),
        "spec_row_count": max(0, int(spec_row_count or 0)),
        "endpoint_hints": endpoint_hints,
        "raw_network_payload_persisted": False,
    }
