from __future__ import annotations

import datetime as dt
import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from .db import normalize_url, utc_now
from .public_web_capture import same_site


PHASE = "49.3I.45"
OBSERVATION_TABLE = "acquisition_discovery_observations"
GENERIC_MODEL_PATH_TOKENS = (
    "/model/",
    "/models/",
    "/thing:",
    "/library/",
    "/design/",
    "/stl/",
    "/3d-model/",
)


@dataclass(frozen=True)
class SitemapEntry:
    loc: str
    lastmod: str = ""
    changefreq: str = ""
    priority: float | None = None


def _local_name(tag: str) -> str:
    return str(tag or "").rsplit("}", 1)[-1].lower()


def _direct_child_text(node, name: str) -> str:
    target = str(name or "").lower()
    for child in list(node):
        if _local_name(child.tag) == target:
            return str(child.text or "").strip()
    return ""


def _safe_priority(value: str) -> float | None:
    try:
        number = float(str(value or "").strip())
    except Exception:
        return None
    return max(0.0, min(1.0, number))


def _lastmod_epoch(value: str) -> float:
    text = str(value or "").strip()
    if not text:
        return 0.0
    try:
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = dt.datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc).timestamp()
    except Exception:
        return 0.0


def parse_sitemap_document(text: str) -> tuple[str, list[SitemapEntry]]:
    """Parse direct Sitemap children only.

    Direct-child parsing is deliberate: image/video/news extensions can contain
    their own nested <loc> elements and must not be mistaken for Product URLs.
    """

    root = ET.fromstring(str(text or ""))
    kind = _local_name(root.tag)
    if kind not in {"urlset", "sitemapindex"}:
        return kind, []

    output: list[SitemapEntry] = []
    for parent in list(root):
        expected = "url" if kind == "urlset" else "sitemap"
        if _local_name(parent.tag) != expected:
            continue
        loc = _direct_child_text(parent, "loc")
        if not loc.startswith(("http://", "https://")):
            continue
        output.append(
            SitemapEntry(
                loc=loc,
                lastmod=_direct_child_text(parent, "lastmod"),
                changefreq=_direct_child_text(parent, "changefreq"),
                priority=_safe_priority(_direct_child_text(parent, "priority")),
            )
        )
    return kind, output


def ensure_schema(db) -> None:
    """Add a bounded metadata ledger for incremental discovery.

    This table stores discovery facts only. It does not duplicate Product,
    candidate, HTTP-cache, or raw response bodies.
    """

    db.conn.executescript(
        f"""
        CREATE TABLE IF NOT EXISTS {OBSERVATION_TABLE}(
            source_code TEXT NOT NULL DEFAULT '',
            normalized_url TEXT NOT NULL,
            source_url TEXT NOT NULL,
            discovered_from TEXT NOT NULL DEFAULT '',
            sitemap_url TEXT NOT NULL DEFAULT '',
            sitemap_lastmod TEXT NOT NULL DEFAULT '',
            sitemap_changefreq TEXT NOT NULL DEFAULT '',
            sitemap_priority REAL,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            seen_count INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY(source_code, normalized_url)
        );
        CREATE INDEX IF NOT EXISTS ix_acquisition_discovery_lastmod
        ON {OBSERVATION_TABLE}(source_code, sitemap_lastmod DESC, last_seen_at DESC);
        CREATE INDEX IF NOT EXISTS ix_acquisition_discovery_seen
        ON {OBSERVATION_TABLE}(source_code, seen_count, last_seen_at DESC);
        """
    )
    db.conn.commit()


def record_discovery_observation(
    db,
    *,
    source_code: str,
    url: str,
    discovered_from: str,
    sitemap_url: str,
    lastmod: str = "",
    changefreq: str = "",
    priority: float | None = None,
) -> bool:
    """Persist Sitemap discovery metadata and return whether it was unseen."""

    ensure_schema(db)
    normalized = normalize_url(url)
    existing = db.conn.execute(
        f"""
        SELECT seen_count FROM {OBSERVATION_TABLE}
        WHERE source_code=? AND normalized_url=?
        """,
        (str(source_code or ""), normalized),
    ).fetchone()
    now = utc_now()
    db.conn.execute(
        f"""
        INSERT INTO {OBSERVATION_TABLE}(
            source_code,normalized_url,source_url,discovered_from,sitemap_url,
            sitemap_lastmod,sitemap_changefreq,sitemap_priority,
            first_seen_at,last_seen_at,seen_count
        ) VALUES(?,?,?,?,?,?,?,?,?,?,1)
        ON CONFLICT(source_code,normalized_url) DO UPDATE SET
            source_url=excluded.source_url,
            discovered_from=excluded.discovered_from,
            sitemap_url=excluded.sitemap_url,
            sitemap_lastmod=CASE
                WHEN excluded.sitemap_lastmod<>'' THEN excluded.sitemap_lastmod
                ELSE {OBSERVATION_TABLE}.sitemap_lastmod
            END,
            sitemap_changefreq=CASE
                WHEN excluded.sitemap_changefreq<>'' THEN excluded.sitemap_changefreq
                ELSE {OBSERVATION_TABLE}.sitemap_changefreq
            END,
            sitemap_priority=COALESCE(excluded.sitemap_priority, {OBSERVATION_TABLE}.sitemap_priority),
            last_seen_at=excluded.last_seen_at,
            seen_count={OBSERVATION_TABLE}.seen_count + 1
        """,
        (
            str(source_code or ""),
            normalized,
            str(url or ""),
            str(discovered_from or ""),
            str(sitemap_url or ""),
            str(lastmod or "")[:80],
            str(changefreq or "")[:40],
            priority,
            now,
            now,
        ),
    )
    db.conn.commit()
    return existing is None


def _product_known(db, source_code: str, external_id: str, normalized_url: str) -> bool:
    row = db.conn.execute(
        """
        SELECT 1 FROM products
        WHERE source_code=?
          AND ((external_id<>'' AND external_id=?) OR normalized_url=?)
        LIMIT 1
        """,
        (str(source_code or ""), str(external_id or ""), str(normalized_url or "")),
    ).fetchone()
    return row is not None


def _candidate_identity(url: str, model_pattern: str) -> tuple[str, str] | None:
    normalized = normalize_url(url)
    if model_pattern:
        match = re.search(model_pattern, normalized, re.I)
        if not match:
            return None
        matched = normalize_url(match.group(0))
        external_id = (
            str(match.groupdict().get("external_id") or "").strip()
            or hashlib.sha1(matched.encode("utf-8")).hexdigest()[:16]
        )
        return external_id, matched

    path = (urlsplit(normalized).path or "").lower()
    if not any(token in path for token in GENERIC_MODEL_PATH_TOKENS):
        return None
    external_id = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]
    return external_id, normalized


def _generic_title(url: str, external_id: str) -> str:
    tail = (urlsplit(url).path or "").rstrip("/").rsplit("/", 1)[-1]
    tail = re.sub(r"[-_]+", " ", tail).strip()
    return tail[:280] if len(tail) >= 3 else f"3D model {external_id}"


async def discover_sitemap_candidates_incremental(
    client,
    sitemap_urls: list[str] | tuple[str, ...],
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    max_documents: int = 12,
) -> list[dict[str, Any]]:
    """Discover Product candidates with Sitemap metadata and freshness ordering.

    Order is intentionally:
    1. Products not already in Catalog,
    2. newest trustworthy Sitemap lastmod,
    3. Sitemap priority,
    4. deterministic original discovery order.

    The crawler still honors the HTTP/robots/pacing behavior of ModernHttpClient.
    No authentication, CAPTCHA, proxy, or access-control bypass is introduced.
    """

    ensure_schema(client.db)
    requested = max(1, int(requested))
    document_cap = max(1, int(max_documents))
    scan_cap = max(200, requested * 12)

    queue: list[SitemapEntry] = [
        SitemapEntry(str(item))
        for item in sitemap_urls
        if str(item).startswith(("http://", "https://"))
    ]
    first_url = queue[0].loc if queue else ""
    seen_documents: set[str] = set()
    candidates: list[dict[str, Any]] = []
    sequence = 0

    while queue and len(seen_documents) < document_cap and len(candidates) < scan_cap:
        current = queue.pop(0)
        normalized_doc = normalize_url(current.loc)
        if normalized_doc in seen_documents:
            continue
        seen_documents.add(normalized_doc)

        try:
            fetched = await client.fetch_text(
                current.loc,
                method_label="sitemap-incremental",
                fresh_seconds=3600,
            )
            kind, entries = parse_sitemap_document(fetched.text)
        except Exception:
            continue

        if kind == "sitemapindex":
            nested = [
                item
                for item in entries
                if (not first_url or same_site(first_url, item.loc))
            ]
            nested.sort(
                key=lambda item: (_lastmod_epoch(item.lastmod), item.loc),
                reverse=True,
            )
            queue = nested + queue
            continue

        if kind != "urlset":
            continue

        for entry in entries:
            if first_url and not same_site(first_url, entry.loc):
                continue
            identity = _candidate_identity(entry.loc, model_pattern)
            if identity is None:
                continue
            external_id, normalized_url = identity
            is_first_observation = record_discovery_observation(
                client.db,
                source_code=source_code,
                url=normalized_url,
                discovered_from=first_url or current.loc,
                sitemap_url=current.loc,
                lastmod=entry.lastmod,
                changefreq=entry.changefreq,
                priority=entry.priority,
            )
            known = _product_known(client.db, source_code, external_id, normalized_url)
            sequence += 1
            candidates.append(
                {
                    "source_code": str(source_code or ""),
                    "external_id": external_id,
                    "source_url": normalized_url,
                    "source_title": _generic_title(normalized_url, external_id),
                    "thumbnail_url": "",
                    "discovered_from": current.loc,
                    "_known": bool(known),
                    "_first_observation": bool(is_first_observation),
                    "_lastmod_epoch": _lastmod_epoch(entry.lastmod),
                    "_sitemap_priority": float(entry.priority or 0.0),
                    "_sequence": sequence,
                }
            )
            if len(candidates) >= scan_cap:
                break

    candidates.sort(
        key=lambda item: (
            bool(item["_known"]),
            -float(item["_lastmod_epoch"]),
            -float(item["_sitemap_priority"]),
            int(item["_sequence"]),
        )
    )

    output: list[dict[str, Any]] = []
    seen_identity: set[tuple[str, str]] = set()
    for item in candidates:
        identity = (str(item["source_code"]), str(item["external_id"]))
        if identity in seen_identity:
            continue
        seen_identity.add(identity)
        output.append(
            {
                "source_code": item["source_code"],
                "external_id": item["external_id"],
                "source_url": item["source_url"],
                "source_title": item["source_title"],
                "thumbnail_url": item["thumbnail_url"],
                "discovered_from": item["discovered_from"],
            }
        )
        if len(output) >= requested:
            break
    return output


def observation_summary(db, source_code: str = "") -> dict[str, int]:
    ensure_schema(db)
    if source_code:
        row = db.conn.execute(
            f"""
            SELECT COUNT(*) total,
                   SUM(CASE WHEN seen_count=1 THEN 1 ELSE 0 END) first_seen,
                   SUM(CASE WHEN sitemap_lastmod<>'' THEN 1 ELSE 0 END) with_lastmod
            FROM {OBSERVATION_TABLE}
            WHERE source_code=?
            """,
            (str(source_code),),
        ).fetchone()
    else:
        row = db.conn.execute(
            f"""
            SELECT COUNT(*) total,
                   SUM(CASE WHEN seen_count=1 THEN 1 ELSE 0 END) first_seen,
                   SUM(CASE WHEN sitemap_lastmod<>'' THEN 1 ELSE 0 END) with_lastmod
            FROM {OBSERVATION_TABLE}
            """
        ).fetchone()
    return {
        "total": int(row["total"] or 0),
        "first_seen": int(row["first_seen"] or 0),
        "with_lastmod": int(row["with_lastmod"] or 0),
    }


def install_runtime(app, *, acquisition_module) -> None:
    """Install the 3I.45 Sitemap planner after the mature 3I.43/44 runtime."""

    ensure_schema(app.db)
    if getattr(acquisition_module, "_phase49_3i45_incremental_sitemap_installed", False):
        return

    acquisition_module.discover_sitemap_candidates = discover_sitemap_candidates_incremental
    acquisition_module._phase49_3i45_incremental_sitemap_installed = True
    app._phase49_3i45_incremental_discovery = True
