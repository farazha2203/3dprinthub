from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path
from typing import Any

from .db import utc_now

_DB = None
_LOGGER = None
_LOCK = threading.RLock()

_SECRET_RE = re.compile(
    r"(?i)(authorization|api[_ -]?key|password|token|secret)(\s*[:=]\s*)([^\s,;\"']+)"
)
_BEARER_RE = re.compile(r"(?i)(bearer\s+)([a-z0-9._~+/=-]+)")


def redact(value: Any) -> str:
    text = str(value if value is not None else "")
    text = _SECRET_RE.sub(r"\1\2***", text)
    text = _BEARER_RE.sub(r"\1***", text)
    return text


def _json_safe(value: Any, limit: int = 16000) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        text = str(value)
    return redact(text)[:limit]


def ensure_schema(db) -> None:
    with _LOCK:
        db.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_audit_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'INFO',
                area TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT '',
                product_id INTEGER,
                source_file TEXT NOT NULL DEFAULT '',
                message TEXT NOT NULL DEFAULT '',
                detail_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS ix_app_audit_created
                ON app_audit_log(id DESC);
            CREATE INDEX IF NOT EXISTS ix_app_audit_product
                ON app_audit_log(product_id, id DESC);

            CREATE TABLE IF NOT EXISTS ai_request_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                provider TEXT NOT NULL DEFAULT '',
                model TEXT NOT NULL DEFAULT '',
                operation TEXT NOT NULL DEFAULT '',
                endpoint TEXT NOT NULL DEFAULT '',
                request_id TEXT NOT NULL DEFAULT '',
                http_status INTEGER,
                status TEXT NOT NULL DEFAULT '',
                duration_ms INTEGER NOT NULL DEFAULT 0,
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                completion_tokens INTEGER NOT NULL DEFAULT 0,
                total_tokens INTEGER NOT NULL DEFAULT 0,
                cost_usd REAL,
                cost_irt REAL,
                cost_source TEXT NOT NULL DEFAULT '',
                product_id INTEGER,
                request_summary TEXT NOT NULL DEFAULT '',
                response_summary TEXT NOT NULL DEFAULT '',
                error_text TEXT NOT NULL DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS ix_ai_request_created
                ON ai_request_log(id DESC);
            CREATE INDEX IF NOT EXISTS ix_ai_request_provider
                ON ai_request_log(provider, id DESC);
            CREATE INDEX IF NOT EXISTS ix_ai_request_request_id
                ON ai_request_log(request_id);
            """
        )
        db.conn.commit()


def configure(db, logger=None) -> None:
    global _DB, _LOGGER
    _DB = db
    _LOGGER = logger
    ensure_schema(db)


def audit_event(
    area: str,
    action: str,
    *,
    status: str = "ok",
    level: str = "INFO",
    product_id: int | None = None,
    source_file: str = "",
    message: str = "",
    detail: Any = None,
) -> None:
    if _LOGGER is not None:
        try:
            log_fn = getattr(_LOGGER, str(level).lower(), _LOGGER.info)
            log_fn("AUDIT area=%s action=%s status=%s product=%s message=%s", area, action, status, product_id, redact(message))
        except Exception:
            pass
    if _DB is None:
        return
    try:
        with _LOCK:
            ensure_schema(_DB)
            _DB.conn.execute(
                """
                INSERT INTO app_audit_log(
                    created_at, level, area, action, status, product_id,
                    source_file, message, detail_json
                ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    utc_now(), str(level or "INFO").upper(), str(area or ""),
                    str(action or ""), str(status or ""), product_id,
                    str(source_file or "")[:800], redact(message)[:4000],
                    _json_safe(detail or {}),
                ),
            )
            _DB.conn.commit()
    except Exception:
        pass


def ai_request_event(
    *,
    provider: str,
    model: str,
    operation: str,
    endpoint: str,
    request_id: str = "",
    http_status: int | None = None,
    status: str = "ok",
    duration_ms: int = 0,
    usage: dict[str, Any] | None = None,
    cost_usd: float | None = None,
    cost_irt: float | None = None,
    cost_source: str = "",
    product_id: int | None = None,
    request_summary: Any = None,
    response_summary: Any = None,
    error_text: str = "",
) -> None:
    usage = usage or {}
    prompt = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    completion = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    total = int(usage.get("total_tokens") or (prompt + completion) or 0)
    if _DB is not None:
        try:
            with _LOCK:
                ensure_schema(_DB)
                _DB.conn.execute(
                    """
                    INSERT INTO ai_request_log(
                        created_at, provider, model, operation, endpoint, request_id,
                        http_status, status, duration_ms, prompt_tokens,
                        completion_tokens, total_tokens, cost_usd, cost_irt,
                        cost_source, product_id, request_summary, response_summary,
                        error_text
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        utc_now(), provider, model, operation, endpoint,
                        str(request_id or "")[:240], http_status, status,
                        int(duration_ms or 0), prompt, completion, total,
                        cost_usd, cost_irt, str(cost_source or "")[:120],
                        product_id, _json_safe(request_summary or {}, 12000),
                        _json_safe(response_summary or {}, 12000),
                        redact(error_text)[:8000],
                    ),
                )
                _DB.conn.commit()
        except Exception:
            pass
    audit_event(
        "ai",
        operation or "request",
        status=status,
        level="ERROR" if status != "ok" else "INFO",
        product_id=product_id,
        source_file="catalog_center/app/ai_providers.py",
        message=(
            f"{provider}/{model} HTTP={http_status or '—'} request_id={request_id or '—'} "
            f"tokens={total} cost_usd={cost_usd if cost_usd is not None else '—'}"
        ),
        detail={"endpoint": endpoint, "duration_ms": duration_ms, "error": redact(error_text)},
    )


def recent_app_events(limit: int = 300) -> list[dict[str, Any]]:
    if _DB is None:
        return []
    ensure_schema(_DB)
    rows = _DB.conn.execute(
        "SELECT * FROM app_audit_log ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 5000)),)
    ).fetchall()
    return [dict(row) for row in rows]


def recent_ai_requests(limit: int = 300) -> list[dict[str, Any]]:
    if _DB is None:
        return []
    ensure_schema(_DB)
    rows = _DB.conn.execute(
        "SELECT * FROM ai_request_log ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 5000)),)
    ).fetchall()
    return [dict(row) for row in rows]


def update_ai_cost(request_id: str, *, cost_usd: float | None = None, cost_irt: float | None = None, cost_source: str = "") -> int:
    if _DB is None or not str(request_id or "").strip():
        return 0
    ensure_schema(_DB)
    with _LOCK:
        cursor = _DB.conn.execute(
            """
            UPDATE ai_request_log
               SET cost_usd=COALESCE(?, cost_usd),
                   cost_irt=COALESCE(?, cost_irt),
                   cost_source=CASE WHEN ?<>'' THEN ? ELSE cost_source END
             WHERE request_id=?
            """,
            (cost_usd, cost_irt, cost_source, cost_source, request_id),
        )
        _DB.conn.commit()
        return int(cursor.rowcount or 0)


def export_diagnostic_bundle(root: str | Path, *, product_id: int | None = None) -> Path:
    root = Path(root)
    target_dir = root / "diagnostics"
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = target_dir / f"catalog-diagnostic-{stamp}.json"
    app_events = recent_app_events(1000)
    ai_events = recent_ai_requests(1000)
    if product_id is not None:
        app_events = [row for row in app_events if row.get("product_id") in {None, product_id}]
        ai_events = [row for row in ai_events if row.get("product_id") in {None, product_id}]
    payload = {
        "generated_at": utc_now(),
        "product_id": product_id,
        "app_events": app_events,
        "ai_requests": ai_events,
        "note": "Secrets are redacted. Share this file for troubleshooting.",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    audit_event("diagnostics", "export", message=str(path), product_id=product_id)
    return path
