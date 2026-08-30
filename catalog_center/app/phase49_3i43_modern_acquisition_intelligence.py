from __future__ import annotations

import asyncio
import datetime as dt
import gzip
import hashlib
import json
import re
import time
import zlib
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from .db import normalize_url, utc_now
from .public_web_capture import (
    build_public_capture_summary,
    same_site as public_same_site,
    sanitize_public_url,
    summarize_packet,
)
from .phase49_3i_discovery_review import candidates_from_dom_rows


PHASE = "49.3I.43"
USER_AGENT = "3DPrintHub-CatalogCenter/8.9.9"
CACHE_BODY_LIMIT = 6_000_000
TEXT_RESPONSE_LIMIT = 12_000_000
ROBOTS_LIMIT = 1_000_000
MAX_HTTP_ATTEMPTS = 3
TRANSIENT_STATUS_CODES = {408, 425, 500, 502, 503, 504}
HOST_MIN_DELAY_SECONDS = 0.15
HOST_MAX_DELAY_SECONDS = 8.0
HOST_TARGET_CONCURRENCY = 1.0

SENSITIVE_QUERY_KEYS = {
    "access_token", "api_key", "apikey", "auth", "authorization", "credential",
    "key", "password", "secret", "session", "signature", "sig", "token",
}

JSONISH_CONTENT_TYPES = (
    "application/json",
    "application/ld+json",
    "application/problem+json",
    "text/json",
)


class RobotsDeniedError(PermissionError):
    pass


class RateLimitedError(RuntimeError):
    def __init__(self, message: str, retry_after_seconds: int = 0) -> None:
        super().__init__(message)
        self.retry_after_seconds = max(0, int(retry_after_seconds or 0))


class AccessDeniedError(PermissionError):
    pass


class TransientHttpError(RuntimeError):
    def __init__(self, status_code: int, message: str, retry_after_seconds: int = 0) -> None:
        super().__init__(message)
        self.status_code = int(status_code or 0)
        self.retry_after_seconds = max(0, int(retry_after_seconds or 0))


@dataclass(frozen=True)
class FetchResult:
    url: str
    final_url: str
    status_code: int
    content_type: str
    text: str
    elapsed_ms: int
    bytes_received: int
    cache_hit: bool
    etag: str = ""
    last_modified: str = ""


@dataclass(frozen=True)
class RobotsPolicy:
    known: bool
    allowed: bool
    robots_url: str
    crawl_delay: float | None
    sitemaps: tuple[str, ...]
    detail: str = ""


def ensure_schema(db) -> None:
    """Install additive acquisition metadata without replacing mature Catalog tables."""
    db.conn.executescript(
        """
        PRAGMA busy_timeout=5000;

        CREATE TABLE IF NOT EXISTS acquisition_http_cache(
            normalized_url TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            final_url TEXT NOT NULL DEFAULT '',
            status_code INTEGER NOT NULL DEFAULT 0,
            content_type TEXT NOT NULL DEFAULT '',
            etag TEXT NOT NULL DEFAULT '',
            last_modified TEXT NOT NULL DEFAULT '',
            body_sha256 TEXT NOT NULL DEFAULT '',
            body_zlib BLOB,
            body_bytes INTEGER NOT NULL DEFAULT 0,
            fetched_epoch INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS acquisition_attempts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL DEFAULT '',
            normalized_url TEXT NOT NULL,
            method TEXT NOT NULL,
            status_code INTEGER NOT NULL DEFAULT 0,
            elapsed_ms INTEGER NOT NULL DEFAULT 0,
            bytes_received INTEGER NOT NULL DEFAULT 0,
            cache_hit INTEGER NOT NULL DEFAULT 0,
            outcome TEXT NOT NULL DEFAULT '',
            error TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ix_acquisition_attempt_source_created
        ON acquisition_attempts(source_code, created_at DESC);
        CREATE INDEX IF NOT EXISTS ix_acquisition_attempt_url_created
        ON acquisition_attempts(normalized_url, created_at DESC);

        CREATE TABLE IF NOT EXISTS source_endpoint_hints(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_code TEXT NOT NULL DEFAULT '',
            normalized_endpoint_url TEXT NOT NULL,
            endpoint_url TEXT NOT NULL,
            http_method TEXT NOT NULL DEFAULT 'GET',
            content_type TEXT NOT NULL DEFAULT '',
            discovered_from TEXT NOT NULL DEFAULT '',
            trust_score REAL NOT NULL DEFAULT 0,
            success_count INTEGER NOT NULL DEFAULT 0,
            failure_count INTEGER NOT NULL DEFAULT 0,
            last_status_code INTEGER NOT NULL DEFAULT 0,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            UNIQUE(source_code, normalized_endpoint_url, http_method)
        );
        CREATE INDEX IF NOT EXISTS ix_endpoint_hint_source_score
        ON source_endpoint_hints(source_code, trust_score DESC, last_seen_at DESC);

        CREATE TABLE IF NOT EXISTS source_capabilities(
            source_code TEXT PRIMARY KEY,
            robots_url TEXT NOT NULL DEFAULT '',
            robots_status TEXT NOT NULL DEFAULT '',
            robots_checked_at TEXT NOT NULL DEFAULT '',
            crawl_delay_seconds REAL,
            sitemaps_json TEXT NOT NULL DEFAULT '[]',
            supports_jsonld INTEGER NOT NULL DEFAULT 0,
            supports_embedded_json INTEGER NOT NULL DEFAULT 0,
            supports_public_json INTEGER NOT NULL DEFAULT 0,
            last_probe_at TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS acquisition_host_state(
            source_code TEXT NOT NULL DEFAULT '',
            hostname TEXT NOT NULL,
            request_count INTEGER NOT NULL DEFAULT 0,
            success_count INTEGER NOT NULL DEFAULT 0,
            error_count INTEGER NOT NULL DEFAULT 0,
            latency_ewma_ms REAL NOT NULL DEFAULT 0,
            delay_seconds REAL NOT NULL DEFAULT 0,
            last_status_code INTEGER NOT NULL DEFAULT 0,
            last_request_epoch REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(source_code, hostname)
        );
        CREATE INDEX IF NOT EXISTS ix_acquisition_host_updated
        ON acquisition_host_state(updated_at DESC);

        CREATE INDEX IF NOT EXISTS ix_discovered_source_status_updated
        ON discovered_urls(source_code, status, updated_at DESC);
        CREATE INDEX IF NOT EXISTS ix_scan_runs_source_started
        ON scan_runs(source_code, started_at DESC);
        CREATE INDEX IF NOT EXISTS ix_products_updated
        ON products(updated_at DESC, id DESC);
        CREATE INDEX IF NOT EXISTS ix_products_work_state
        ON products(is_blocked, upload_ready, needs_update, workflow_status, updated_at DESC);
        """
    )

    endpoint_columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(source_endpoint_hints)")}
    endpoint_additions = {
        "response_schema_json": "TEXT NOT NULL DEFAULT '[]'",
        "shape_hash": "TEXT NOT NULL DEFAULT ''",
        "body_bytes": "INTEGER NOT NULL DEFAULT 0",
        "observed_count": "INTEGER NOT NULL DEFAULT 0",
    }
    for name, ddl in endpoint_additions.items():
        if name not in endpoint_columns:
            db.conn.execute(f"ALTER TABLE source_endpoint_hints ADD COLUMN {name} {ddl}")

    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    additions = {
        "source_provenance_json": "TEXT NOT NULL DEFAULT '{}'",
        "acquisition_method": "TEXT NOT NULL DEFAULT ''",
        "acquisition_quality": "REAL NOT NULL DEFAULT 0",
        "source_last_http_status": "INTEGER",
        "source_last_fetch_ms": "INTEGER",
    }
    for name, ddl in additions.items():
        if name not in columns:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
    db.conn.commit()
    try:
        db.conn.execute("PRAGMA optimize")
    except Exception:
        pass


def _safe_normalized_url(url: str) -> str:
    try:
        return normalize_url(url)
    except Exception:
        return str(url or "").strip()


def sanitize_endpoint_url(url: str) -> str:
    """Keep endpoint identity useful while never persisting credential-like query values."""
    parsed = urlsplit(str(url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    clean_query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.casefold() in SENSITIVE_QUERY_KEYS or any(
            token in key.casefold() for token in ("token", "secret", "signature", "password")
        ):
            clean_query.append((key, "<redacted>"))
        else:
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


def _same_site(left: str, right: str) -> bool:
    a = urlsplit(left).hostname or ""
    b = urlsplit(right).hostname or ""
    a = a.lower().lstrip(".")
    b = b.lower().lstrip(".")
    return bool(a and b and (a == b or a.endswith("." + b) or b.endswith("." + a)))


def _cache_row(db, url: str):
    return db.conn.execute(
        "SELECT * FROM acquisition_http_cache WHERE normalized_url=?",
        (_safe_normalized_url(url),),
    ).fetchone()


def _cached_text(row) -> str:
    if row is None or row["body_zlib"] is None:
        return ""
    try:
        return zlib.decompress(bytes(row["body_zlib"])).decode("utf-8", "replace")
    except Exception:
        return ""


def _store_cache(db, result: FetchResult, raw: bytes) -> None:
    if len(raw) > CACHE_BODY_LIMIT:
        compressed = None
    else:
        compressed = zlib.compress(raw, level=6)
    db.conn.execute(
        """
        INSERT INTO acquisition_http_cache(
            normalized_url,url,final_url,status_code,content_type,etag,last_modified,
            body_sha256,body_zlib,body_bytes,fetched_epoch,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(normalized_url) DO UPDATE SET
            url=excluded.url,
            final_url=excluded.final_url,
            status_code=excluded.status_code,
            content_type=excluded.content_type,
            etag=excluded.etag,
            last_modified=excluded.last_modified,
            body_sha256=excluded.body_sha256,
            body_zlib=CASE WHEN excluded.body_zlib IS NULL THEN acquisition_http_cache.body_zlib ELSE excluded.body_zlib END,
            body_bytes=excluded.body_bytes,
            fetched_epoch=excluded.fetched_epoch,
            updated_at=excluded.updated_at
        """,
        (
            _safe_normalized_url(result.url),
            result.url,
            result.final_url,
            result.status_code,
            result.content_type,
            result.etag,
            result.last_modified,
            hashlib.sha256(raw).hexdigest(),
            compressed,
            len(raw),
            int(time.time()),
            utc_now(),
        ),
    )
    db.conn.commit()


def record_attempt(
    db,
    source_code: str,
    url: str,
    method: str,
    *,
    status_code: int = 0,
    elapsed_ms: int = 0,
    bytes_received: int = 0,
    cache_hit: bool = False,
    outcome: str = "",
    error: str = "",
) -> None:
    db.conn.execute(
        """
        INSERT INTO acquisition_attempts(
            source_code,normalized_url,method,status_code,elapsed_ms,bytes_received,
            cache_hit,outcome,error,created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?)
        """,
        (
            str(source_code or ""),
            _safe_normalized_url(url),
            str(method or "")[:120],
            int(status_code or 0),
            max(0, int(elapsed_ms or 0)),
            max(0, int(bytes_received or 0)),
            int(bool(cache_hit)),
            str(outcome or "")[:120],
            str(error or "")[:2000],
            utc_now(),
        ),
    )
    db.conn.commit()


def _retry_after_seconds(value: str, *, now_epoch: float | None = None) -> int:
    """Parse RFC Retry-After delta-seconds or HTTP-date, bounded to one day."""
    value = str(value or "").strip()
    if not value:
        return 0
    try:
        return max(0, min(86400, int(float(value))))
    except Exception:
        pass
    try:
        target = parsedate_to_datetime(value)
        if target.tzinfo is None:
            target = target.replace(tzinfo=dt.timezone.utc)
        now = dt.datetime.fromtimestamp(
            float(time.time() if now_epoch is None else now_epoch),
            tz=dt.timezone.utc,
        )
        seconds = int((target.astimezone(dt.timezone.utc) - now).total_seconds())
        return max(0, min(86400, seconds))
    except Exception:
        return 0


class ModernHttpClient:
    """Pooled, bounded, cache-aware HTTP client for respectful public acquisition.

    The client keeps one AsyncClient per acquisition operation, applies
    per-host pacing, uses conditional requests, retries only transient failures,
    and never silently retries authorization, robots, or rate-limit denials.
    """

    def __init__(self, db, source_code: str = "") -> None:
        self.db = db
        self.source_code = str(source_code or "")
        self.client = None
        self._host_locks: dict[str, asyncio.Lock] = {}
        self._last_started: dict[str, float] = {}
        self._robots_min_delay: dict[str, float] = {}

    async def __aenter__(self):
        import httpx

        timeout = httpx.Timeout(connect=10.0, read=30.0, write=20.0, pool=10.0)
        limits = httpx.Limits(
            max_connections=12,
            max_keepalive_connections=6,
            keepalive_expiry=30.0,
        )
        transport = httpx.AsyncHTTPTransport(retries=1)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            transport=transport,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/json,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
                "Accept-Language": "en-US,en;q=0.8",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    def set_robots_delay(self, target_url: str, delay_seconds: float | None) -> None:
        host = (urlsplit(str(target_url or "")).hostname or "").lower()
        if not host or delay_seconds is None:
            return
        delay = max(0.0, min(HOST_MAX_DELAY_SECONDS, float(delay_seconds or 0)))
        previous = float(self._robots_min_delay.get(host) or 0)
        self._robots_min_delay[host] = max(previous, delay)

    def _host_row(self, hostname: str):
        return self.db.conn.execute(
            """
            SELECT * FROM acquisition_host_state
            WHERE source_code=? AND hostname=?
            """,
            (self.source_code, hostname),
        ).fetchone()

    async def _pace_host(self, url: str) -> tuple[str, float]:
        hostname = (urlsplit(str(url or "")).hostname or "").lower()
        if not hostname:
            return "", time.time()

        lock = self._host_locks.setdefault(hostname, asyncio.Lock())
        async with lock:
            row = self._host_row(hostname)
            adaptive = float(row["delay_seconds"] or 0) if row is not None else 0.0
            robots_min = float(self._robots_min_delay.get(hostname) or 0)
            delay = max(adaptive, robots_min)

            now = time.time()
            persisted_last = float(row["last_request_epoch"] or 0) if row is not None else 0.0
            local_last = float(self._last_started.get(hostname) or 0)
            last = max(persisted_last, local_last)
            remaining = (last + delay) - now
            if remaining > 0:
                await asyncio.sleep(min(HOST_MAX_DELAY_SECONDS, remaining))
            started_epoch = time.time()
            self._last_started[hostname] = started_epoch
            return hostname, started_epoch

    def _observe_host(
        self,
        hostname: str,
        *,
        started_epoch: float,
        status_code: int,
        elapsed_ms: int,
        success: bool,
    ) -> None:
        if not hostname:
            return
        row = self._host_row(hostname)
        previous_latency = float(row["latency_ewma_ms"] or 0) if row is not None else 0.0
        previous_delay = float(row["delay_seconds"] or 0) if row is not None else 0.0
        latency = max(1.0, float(elapsed_ms or 1))
        latency_ewma = latency if previous_latency <= 0 else (previous_latency * 0.75 + latency * 0.25)

        latency_target = max(
            HOST_MIN_DELAY_SECONDS,
            min(HOST_MAX_DELAY_SECONDS, (latency_ewma / 1000.0) / HOST_TARGET_CONCURRENCY),
        )
        if success and 200 <= int(status_code or 0) < 400:
            delay = latency_target if previous_delay <= 0 else (previous_delay * 0.65 + latency_target * 0.35)
        else:
            delay = max(
                previous_delay,
                min(HOST_MAX_DELAY_SECONDS, max(HOST_MIN_DELAY_SECONDS, latency_target * 1.5)),
            )

        now = utc_now()
        self.db.conn.execute(
            """
            INSERT INTO acquisition_host_state(
                source_code,hostname,request_count,success_count,error_count,
                latency_ewma_ms,delay_seconds,last_status_code,last_request_epoch,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(source_code,hostname) DO UPDATE SET
                request_count=acquisition_host_state.request_count + 1,
                success_count=acquisition_host_state.success_count + excluded.success_count,
                error_count=acquisition_host_state.error_count + excluded.error_count,
                latency_ewma_ms=excluded.latency_ewma_ms,
                delay_seconds=excluded.delay_seconds,
                last_status_code=excluded.last_status_code,
                last_request_epoch=excluded.last_request_epoch,
                updated_at=excluded.updated_at
            """,
            (
                self.source_code,
                hostname,
                1,
                1 if success else 0,
                0 if success else 1,
                latency_ewma,
                delay,
                int(status_code or 0),
                float(started_epoch or time.time()),
                now,
            ),
        )
        self.db.conn.commit()

    @staticmethod
    def _decode_wire_body(raw: bytes, url: str, content_type: str, max_bytes: int) -> tuple[bytes, str]:
        data = raw
        normalized_type = str(content_type or "").lower()
        is_gzip_file = data.startswith(b"\x1f\x8b") or urlsplit(str(url or "")).path.lower().endswith(".gz")
        if is_gzip_file and data.startswith(b"\x1f\x8b"):
            data = gzip.decompress(data)
            if len(data) > max(1, int(max_bytes)):
                raise RuntimeError(f"Decompressed response is larger than {max_bytes} bytes")
            if urlsplit(str(url or "")).path.lower().endswith((".xml.gz", ".xml.gzip")):
                normalized_type = "application/xml"
        return data, normalized_type

    async def fetch_text(
        self,
        url: str,
        *,
        method_label: str = "conditional-http",
        max_bytes: int = TEXT_RESPONSE_LIMIT,
        use_cache: bool = True,
        fresh_seconds: int = 0,
    ) -> FetchResult:
        if self.client is None:
            raise RuntimeError("ModernHttpClient must be used as an async context manager")

        import httpx

        cache = _cache_row(self.db, url) if use_cache else None
        if cache is not None and int(fresh_seconds or 0) > 0:
            age = max(0, int(time.time()) - int(cache["fetched_epoch"] or 0))
            cached = _cached_text(cache)
            if cached and age <= int(fresh_seconds):
                result = FetchResult(
                    url=url,
                    final_url=str(cache["final_url"] or url),
                    status_code=int(cache["status_code"] or 200),
                    content_type=str(cache["content_type"] or ""),
                    text=cached,
                    elapsed_ms=0,
                    bytes_received=0,
                    cache_hit=True,
                    etag=str(cache["etag"] or ""),
                    last_modified=str(cache["last_modified"] or ""),
                )
                record_attempt(
                    self.db,
                    self.source_code,
                    url,
                    method_label,
                    status_code=result.status_code,
                    cache_hit=True,
                    outcome="fresh_cache_hit",
                )
                return result

        headers: dict[str, str] = {}
        if cache is not None:
            if str(cache["etag"] or ""):
                headers["If-None-Match"] = str(cache["etag"])
            if str(cache["last_modified"] or ""):
                headers["If-Modified-Since"] = str(cache["last_modified"])

        last_exc: Exception | None = None
        transient_failure = False

        for attempt in range(1, MAX_HTTP_ATTEMPTS + 1):
            hostname, started_epoch = await self._pace_host(url)
            started = time.perf_counter()
            status_code = 0
            received = 0
            try:
                async with self.client.stream("GET", url, headers=headers) as response:
                    status_code = int(response.status_code)
                    elapsed_ms = int((time.perf_counter() - started) * 1000)

                    if status_code == 304 and cache is not None:
                        text = _cached_text(cache)
                        if text:
                            self._observe_host(
                                hostname,
                                started_epoch=started_epoch,
                                status_code=304,
                                elapsed_ms=elapsed_ms,
                                success=True,
                            )
                            result = FetchResult(
                                url=url,
                                final_url=str(cache["final_url"] or url),
                                status_code=int(cache["status_code"] or 200),
                                content_type=str(cache["content_type"] or ""),
                                text=text,
                                elapsed_ms=elapsed_ms,
                                bytes_received=0,
                                cache_hit=True,
                                etag=str(cache["etag"] or ""),
                                last_modified=str(cache["last_modified"] or ""),
                            )
                            record_attempt(
                                self.db,
                                self.source_code,
                                url,
                                method_label,
                                status_code=304,
                                elapsed_ms=elapsed_ms,
                                cache_hit=True,
                                outcome="not_modified_cache_hit",
                            )
                            return result

                    if status_code == 429:
                        retry_after = _retry_after_seconds(response.headers.get("retry-after", ""))
                        if self.source_code and retry_after:
                            try:
                                self.db.update_source_runtime(
                                    self.source_code,
                                    cooldown_until=int(time.time()) + retry_after,
                                    last_error=f"HTTP 429 retry-after={retry_after}s",
                                )
                            except Exception:
                                pass
                        raise RateLimitedError(f"HTTP 429 for {url}", retry_after)

                    if status_code in {401, 403}:
                        raise AccessDeniedError(f"HTTP {status_code} for {url}")

                    if status_code in TRANSIENT_STATUS_CODES:
                        retry_after = _retry_after_seconds(response.headers.get("retry-after", ""))
                        raise TransientHttpError(
                            status_code,
                            f"Transient HTTP {status_code} for {url}",
                            retry_after,
                        )

                    response.raise_for_status()
                    chunks: list[bytes] = []
                    async for chunk in response.aiter_bytes():
                        received += len(chunk)
                        if received > max(1, int(max_bytes)):
                            raise RuntimeError(f"Response is larger than {max_bytes} bytes")
                        chunks.append(chunk)

                    raw = b"".join(chunks)
                    content_type = (response.headers.get("content-type") or "").split(";", 1)[0].lower()
                    raw, content_type = self._decode_wire_body(raw, str(response.url), content_type, max_bytes)
                    encoding = response.encoding or "utf-8"
                    text = raw.decode(encoding, "replace")
                    result = FetchResult(
                        url=url,
                        final_url=str(response.url),
                        status_code=status_code,
                        content_type=content_type,
                        text=text,
                        elapsed_ms=elapsed_ms,
                        bytes_received=len(raw),
                        cache_hit=False,
                        etag=str(response.headers.get("etag") or ""),
                        last_modified=str(response.headers.get("last-modified") or ""),
                    )
                    if use_cache and content_type.startswith(
                        ("text/", "application/json", "application/xml", "application/xhtml")
                    ):
                        _store_cache(self.db, result, raw)
                    self._observe_host(
                        hostname,
                        started_epoch=started_epoch,
                        status_code=status_code,
                        elapsed_ms=elapsed_ms,
                        success=True,
                    )
                    record_attempt(
                        self.db,
                        self.source_code,
                        url,
                        method_label,
                        status_code=status_code,
                        elapsed_ms=elapsed_ms,
                        bytes_received=len(raw),
                        outcome="success",
                    )
                    return result

            except (RateLimitedError, AccessDeniedError) as exc:
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                self._observe_host(
                    hostname,
                    started_epoch=started_epoch,
                    status_code=status_code,
                    elapsed_ms=elapsed_ms,
                    success=False,
                )
                record_attempt(
                    self.db,
                    self.source_code,
                    url,
                    method_label,
                    status_code=status_code,
                    elapsed_ms=elapsed_ms,
                    bytes_received=received,
                    outcome="access_limited",
                    error=str(exc),
                )
                raise

            except (TransientHttpError, httpx.TransportError) as exc:
                transient_failure = True
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                last_exc = exc
                self._observe_host(
                    hostname,
                    started_epoch=started_epoch,
                    status_code=status_code,
                    elapsed_ms=elapsed_ms,
                    success=False,
                )
                can_retry = attempt < MAX_HTTP_ATTEMPTS
                retry_after = int(getattr(exc, "retry_after_seconds", 0) or 0)
                if retry_after > HOST_MAX_DELAY_SECONDS:
                    can_retry = False
                record_attempt(
                    self.db,
                    self.source_code,
                    url,
                    method_label,
                    status_code=status_code,
                    elapsed_ms=elapsed_ms,
                    bytes_received=received,
                    outcome="transient_retry" if can_retry else "transient_exhausted",
                    error=f"{type(exc).__name__}: {exc}",
                )
                if not can_retry:
                    break
                delay = float(retry_after) if retry_after else min(
                    HOST_MAX_DELAY_SECONDS,
                    0.35 * (2 ** (attempt - 1)),
                )
                if delay > 0:
                    await asyncio.sleep(delay)
                continue

            except Exception as exc:
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                last_exc = exc
                self._observe_host(
                    hostname,
                    started_epoch=started_epoch,
                    status_code=status_code,
                    elapsed_ms=elapsed_ms,
                    success=False,
                )
                record_attempt(
                    self.db,
                    self.source_code,
                    url,
                    method_label,
                    status_code=status_code,
                    elapsed_ms=elapsed_ms,
                    bytes_received=received,
                    outcome="failed",
                    error=f"{type(exc).__name__}: {exc}",
                )
                break

        if transient_failure and cache is not None:
            cached = _cached_text(cache)
            if cached:
                result = FetchResult(
                    url=url,
                    final_url=str(cache["final_url"] or url),
                    status_code=int(cache["status_code"] or 200),
                    content_type=str(cache["content_type"] or ""),
                    text=cached,
                    elapsed_ms=0,
                    bytes_received=0,
                    cache_hit=True,
                    etag=str(cache["etag"] or ""),
                    last_modified=str(cache["last_modified"] or ""),
                )
                record_attempt(
                    self.db,
                    self.source_code,
                    url,
                    method_label,
                    status_code=result.status_code,
                    cache_hit=True,
                    outcome="stale_cache_fallback",
                    error=f"{type(last_exc).__name__}: {last_exc}" if last_exc else "",
                )
                return result

        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"Acquisition failed without a result for {url}")


async def robots_policy(client: ModernHttpClient, target_url: str) -> RobotsPolicy:
    from protego import Protego

    parsed = urlsplit(target_url)
    robots_url = urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))
    try:
        fetched = await client.fetch_text(
            robots_url,
            method_label="robots",
            max_bytes=ROBOTS_LIMIT,
            use_cache=True,
            fresh_seconds=21600,
        )
        parser = Protego.parse(fetched.text)
        allowed = bool(parser.can_fetch(target_url, USER_AGENT))
        delay = parser.crawl_delay(USER_AGENT)
        request_rate = parser.request_rate(USER_AGENT)
        if request_rate is not None and getattr(request_rate, "requests", 0):
            rate_delay = float(getattr(request_rate, "seconds", 0) or 0) / float(request_rate.requests)
            delay = max(float(delay or 0), rate_delay)
        sitemaps = tuple(str(item) for item in parser.sitemaps)
        status = "allowed" if allowed else "denied"
        known = True
        detail = f"http={fetched.status_code}"
    except AccessDeniedError as exc:
        allowed = True
        delay = None
        sitemaps = ()
        status = "unavailable"
        known = False
        detail = str(exc)
    except Exception as exc:
        allowed = True
        delay = None
        sitemaps = ()
        status = "unavailable"
        known = False
        detail = f"{type(exc).__name__}: {exc}"

    source_code = client.source_code
    if source_code:
        client.db.conn.execute(
            """
            INSERT INTO source_capabilities(
                source_code,robots_url,robots_status,robots_checked_at,
                crawl_delay_seconds,sitemaps_json,last_probe_at
            ) VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(source_code) DO UPDATE SET
                robots_url=excluded.robots_url,
                robots_status=excluded.robots_status,
                robots_checked_at=excluded.robots_checked_at,
                crawl_delay_seconds=excluded.crawl_delay_seconds,
                sitemaps_json=excluded.sitemaps_json,
                last_probe_at=excluded.last_probe_at
            """,
            (
                source_code, robots_url, status, utc_now(),
                float(delay) if delay is not None else None,
                json.dumps(list(sitemaps), ensure_ascii=False),
                utc_now(),
            ),
        )
        client.db.conn.commit()

    if delay is not None:
        client.set_robots_delay(target_url, float(delay))

    return RobotsPolicy(
        known=known,
        allowed=allowed,
        robots_url=robots_url,
        crawl_delay=float(delay) if delay is not None else None,
        sitemaps=sitemaps,
        detail=detail,
    )


def _extract_links_from_html(html: str, pattern: str) -> list[tuple[str, str]]:
    if not pattern:
        return []
    regex = re.compile(pattern, re.I)
    output: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in regex.finditer(html or ""):
        url = match.group(0).replace("\\/", "/").replace("&amp;", "&")
        url = url.rstrip("\\")
        try:
            normalized = normalize_url(url)
        except Exception:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        external_id = str(match.groupdict().get("external_id") or "")
        output.append((external_id, normalized))
    return output


async def discover_sitemap_candidates(
    client: ModernHttpClient,
    sitemap_urls: list[str] | tuple[str, ...],
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
    max_documents: int = 12,
) -> list[dict]:
    """Read public XML sitemap/urlset documents with bounded same-site recursion."""
    queue = [str(item) for item in sitemap_urls if str(item).startswith(("http://", "https://"))]
    seen_docs: set[str] = set()
    rows: list[dict[str, str]] = []
    requested = max(1, int(requested))
    first_url = queue[0] if queue else ""

    while queue and len(seen_docs) < max(1, int(max_documents)) and len(rows) < requested:
        sitemap_url = queue.pop(0)
        normalized_doc = _safe_normalized_url(sitemap_url)
        if normalized_doc in seen_docs:
            continue
        seen_docs.add(normalized_doc)
        try:
            fetched = await client.fetch_text(
                sitemap_url,
                method_label="sitemap",
                max_bytes=TEXT_RESPONSE_LIMIT,
                use_cache=True,
                fresh_seconds=3600,
            )
            root = ET.fromstring(fetched.text)
        except Exception:
            continue

        root_name = str(root.tag).lower()
        locations = [
            str(child.text or "").strip()
            for item in list(root)
            for child in list(item)
            if str(child.tag).lower().endswith("loc") and str(child.text or "").strip()
        ]
        if root_name.endswith("sitemapindex"):
            for candidate in locations:
                if candidate.startswith(("http://", "https://")) and (
                    not first_url or _same_site(first_url, candidate)
                ):
                    queue.append(candidate)
            continue

        for candidate in locations:
            if not candidate.startswith(("http://", "https://")):
                continue
            pairs = _extract_links_from_html(candidate, model_pattern)
            if not pairs:
                continue
            external_id, normalized_url = pairs[0]
            rows.append({
                "href": normalized_url,
                "text": f"Model {external_id}" if external_id else "",
                "image": "",
            })
            if len(rows) >= requested:
                break

    if not rows:
        return []
    return candidates_from_dom_rows(
        rows,
        model_pattern,
        first_url or "",
        source_code,
        requested,
    )


async def discover_conditional_http(
    client: ModernHttpClient,
    listing_url: str,
    *,
    source_code: str,
    model_pattern: str,
    requested: int,
) -> list[dict]:
    policy = await robots_policy(client, listing_url)
    if policy.known and not policy.allowed:
        record_attempt(
            client.db, source_code, listing_url, "robots-gate",
            outcome="denied", error="robots.txt denies this URL",
        )
        raise RobotsDeniedError(f"robots.txt denies acquisition for {listing_url}")

    fetched = await client.fetch_text(
        listing_url,
        method_label="conditional-http-links",
        fresh_seconds=30,
    )
    pairs = _extract_links_from_html(fetched.text, model_pattern)
    rows = [
        {"href": url, "text": f"Model {external_id}" if external_id else "", "image": ""}
        for external_id, url in pairs[: max(1, int(requested))]
    ]
    if rows:
        return candidates_from_dom_rows(
            rows,
            model_pattern,
            fetched.final_url or listing_url,
            source_code,
            requested,
        )

    parsed = urlsplit(listing_url)
    rootish = (parsed.path or "/") in {"", "/"} and not parsed.query
    sitemapish = "sitemap" in (parsed.path or "").lower() or (parsed.path or "").lower().endswith(".xml")
    sitemap_urls: list[str] = []
    if sitemapish:
        sitemap_urls.append(listing_url)
    elif rootish:
        sitemap_urls.extend(policy.sitemaps)
        if not sitemap_urls:
            origin = urlunsplit((parsed.scheme, parsed.netloc, "", "", "")).rstrip("/")
            sitemap_urls.extend([
                origin + "/sitemap.xml",
                origin + "/sitemap_index.xml",
                origin + "/sitemap-index.xml",
            ])

    if sitemap_urls:
        return await discover_sitemap_candidates(
            client,
            sitemap_urls,
            source_code=source_code,
            model_pattern=model_pattern,
            requested=requested,
        )
    return []


def _endpoint_score(packet: dict[str, Any]) -> float:
    content_type = str(packet.get("content_type") or "").lower()
    resource_type = str(packet.get("resource_type") or "").lower()
    status = int(packet.get("status") or 0)
    score = 0.0
    if any(token in content_type for token in ("json", "graphql")):
        score += 50
    if resource_type in {"xhr", "fetch"}:
        score += 30
    if 200 <= status < 300:
        score += 15
    method = str(packet.get("method") or "GET").upper()
    if method == "GET":
        score += 5
    return min(100.0, score)


def record_endpoint_hints(
    db,
    source_code: str,
    source_url: str,
    snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    """Persist endpoint identity and response shape, never raw observed JSON bodies."""
    ensure_schema(db)
    output: list[dict[str, Any]] = []

    capture = snapshot.get("capture_summary") if isinstance(snapshot, dict) else None
    packets: list[dict[str, Any]] = []
    if isinstance(capture, dict):
        for item in capture.get("endpoint_hints") or []:
            if isinstance(item, dict):
                packets.append(dict(item))

    # Compatibility for older persisted snapshots and tests. Raw payloads are
    # summarized immediately and are never written into source_endpoint_hints.
    if not packets:
        for raw in snapshot.get("network_json") or []:
            if not isinstance(raw, dict):
                continue
            summary = summarize_packet(source_url, raw)
            if summary is not None:
                packets.append(summary)

    for packet in packets[:40]:
        clean_url = sanitize_public_url(str(packet.get("url") or ""))
        if not clean_url or not public_same_site(source_url, clean_url):
            continue

        method = str(packet.get("method") or "GET").upper()[:12]
        status = int(packet.get("status") or 0)
        content_type = str(packet.get("content_type") or "").lower()[:120]
        resource_type = str(packet.get("resource_type") or "").lower()[:40]
        response_schema = [
            str(item)[:300]
            for item in (packet.get("response_schema") or [])
            if str(item or "").strip()
        ][:120]
        shape_hash = str(packet.get("shape_hash") or "")[:64]
        body_bytes = max(0, int(packet.get("body_bytes") or 0))
        score = _endpoint_score({
            "content_type": content_type,
            "resource_type": resource_type,
            "status": status,
            "method": method,
        })
        normalized = _safe_normalized_url(clean_url)
        now = utc_now()
        db.conn.execute(
            """
            INSERT INTO source_endpoint_hints(
                source_code,normalized_endpoint_url,endpoint_url,http_method,content_type,
                discovered_from,trust_score,success_count,failure_count,last_status_code,
                first_seen_at,last_seen_at,response_schema_json,shape_hash,body_bytes,observed_count
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)
            ON CONFLICT(source_code,normalized_endpoint_url,http_method) DO UPDATE SET
                endpoint_url=excluded.endpoint_url,
                content_type=excluded.content_type,
                discovered_from=excluded.discovered_from,
                trust_score=MAX(source_endpoint_hints.trust_score, excluded.trust_score),
                success_count=source_endpoint_hints.success_count + excluded.success_count,
                failure_count=source_endpoint_hints.failure_count + excluded.failure_count,
                last_status_code=excluded.last_status_code,
                last_seen_at=excluded.last_seen_at,
                response_schema_json=CASE
                    WHEN excluded.response_schema_json<>'[]' THEN excluded.response_schema_json
                    ELSE source_endpoint_hints.response_schema_json
                END,
                shape_hash=CASE
                    WHEN excluded.shape_hash<>'' THEN excluded.shape_hash
                    ELSE source_endpoint_hints.shape_hash
                END,
                body_bytes=MAX(source_endpoint_hints.body_bytes, excluded.body_bytes),
                observed_count=source_endpoint_hints.observed_count + 1
            """,
            (
                str(source_code or ""),
                normalized,
                clean_url,
                method,
                content_type,
                "playwright-public-shape-observed",
                score,
                1 if 200 <= status < 400 else 0,
                1 if status >= 400 else 0,
                status,
                now,
                now,
                json.dumps(response_schema, ensure_ascii=False),
                shape_hash,
                body_bytes,
            ),
        )
        output.append({
            "url": clean_url,
            "method": method,
            "content_type": content_type,
            "status": status,
            "trust_score": score,
            "response_schema": response_schema,
            "shape_hash": shape_hash,
            "body_bytes": body_bytes,
        })

    db.conn.commit()
    if source_code and output:
        db.conn.execute(
            """
            INSERT INTO source_capabilities(source_code,supports_public_json,last_probe_at)
            VALUES(?,1,?)
            ON CONFLICT(source_code) DO UPDATE SET
                supports_public_json=1,
                last_probe_at=excluded.last_probe_at
            """,
            (str(source_code), utc_now()),
        )
        db.conn.commit()
    return output


def acquisition_quality(result: dict[str, Any]) -> float:
    score = 0.0
    if str(result.get("source_title") or "").strip():
        score += 25
    if len(str(result.get("source_description") or "").strip()) >= 40:
        score += 20
    try:
        images = json.loads(result.get("images_json") or "[]")
    except Exception:
        images = []
    if images:
        score += 20
    try:
        specs = json.loads(result.get("source_specs_json") or "{}")
    except Exception:
        specs = {}
    if specs:
        score += 15
    if str(result.get("author_name") or "").strip():
        score += 5
    if str(result.get("license_name") or "").strip():
        score += 5
    if any(int(result.get(key) or 0) > 0 for key in ("source_like_count", "source_download_count", "source_view_count")):
        score += 10
    return min(100.0, score)


def build_provenance(result: dict[str, Any], endpoint_hints: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        snapshot = json.loads(result.get("source_snapshot_json") or "{}")
    except Exception:
        snapshot = {}
    capture = snapshot.get("capture_summary") if isinstance(snapshot, dict) else {}
    if not isinstance(capture, dict):
        capture = {}
    return {
        "phase": PHASE,
        "acquisition_method": "playwright-rich-network-observed",
        "quality_score": acquisition_quality(result),
        "source_url": str(result.get("source_url") or ""),
        "snapshot_signals": {
            "json_ld_count": int(capture.get("json_ld_count") or 0),
            "embedded_json_count": int(capture.get("embedded_json_count") or 0),
            "network_json_count": int(capture.get("network_json_count") or len(endpoint_hints)),
            "breadcrumb_count": int(capture.get("breadcrumb_count") or 0),
            "spec_row_count": int(capture.get("spec_row_count") or 0),
            "raw_network_payload_persisted": bool(capture.get("raw_network_payload_persisted", False)),
        },
        "endpoint_hints": endpoint_hints[:40],
        "policy": {
            "public_data_only": True,
            "captcha_bypass": False,
            "authentication_bypass": False,
            "proxy_evasion": False,
            "raw_network_payload_persisted": False,
        },
        "recorded_at": utc_now(),
    }


def install_runtime(app, *, bulk_module, app_module) -> None:
    """Install final additive acquisition boundary after mature 3I.16/3I.38 composition."""
    ensure_schema(app.db)

    if not getattr(bulk_module, "_phase49_3i43_modern_discovery_installed", False):
        previous_discover = bulk_module.discover_preview_candidates

        async def discover_preview_candidates_modern(*args, **kwargs):
            listing_url = str(args[0] if args else kwargs.get("listing_url") or "")
            source_code = str(kwargs.get("source_code") or "")
            model_pattern = str(kwargs.get("model_pattern") or "")
            requested = max(1, int(kwargs.get("requested") or 1))
            try:
                async with ModernHttpClient(app.db, source_code) as client:
                    result = await discover_conditional_http(
                        client,
                        listing_url,
                        source_code=source_code,
                        model_pattern=model_pattern,
                        requested=requested,
                    )
                if result:
                    record_attempt(
                        app.db, source_code, listing_url, "modern-discovery-plan",
                        outcome="conditional_http_success",
                    )
                    return result
            except RobotsDeniedError:
                raise
            except RateLimitedError:
                raise
            except Exception as exc:
                record_attempt(
                    app.db, source_code, listing_url, "modern-discovery-plan",
                    outcome="fallback_to_mature",
                    error=f"{type(exc).__name__}: {exc}",
                )

            result = await previous_discover(*args, **kwargs)
            record_attempt(
                app.db, source_code, listing_url, "modern-discovery-plan",
                outcome="mature_resilient_success" if result else "mature_resilient_empty",
            )
            return result

        bulk_module.discover_preview_candidates = discover_preview_candidates_modern
        bulk_module._phase49_3i43_modern_discovery_installed = True

    if not getattr(app_module, "_phase49_3i43_direct_link_installed", False):
        previous_direct = app_module.extract_direct_link

        async def extract_direct_link_modern(*args, **kwargs):
            started = time.perf_counter()
            result = await previous_direct(*args, **kwargs)
            source_code = str(result.get("source_code") or "")
            source_url = str(result.get("source_url") or (args[0] if args else ""))
            try:
                snapshot = json.loads(result.get("source_snapshot_json") or "{}")
            except Exception:
                snapshot = {}
            hints = record_endpoint_hints(app.db, source_code, source_url, snapshot)
            quality = acquisition_quality(result)
            result = dict(result)
            result["acquisition_method"] = "playwright-rich-network-observed"
            result["acquisition_quality"] = quality
            result["source_provenance_json"] = json.dumps(
                build_provenance(result, hints),
                ensure_ascii=False,
            )
            result["source_last_http_status"] = int(snapshot.get("http_status") or 0) or None
            result["source_last_fetch_ms"] = int((time.perf_counter() - started) * 1000)
            return result

        app_module.extract_direct_link = extract_direct_link_modern
        app_module._phase49_3i43_direct_link_installed = True

    app._phase49_3i43_modern_acquisition = True
