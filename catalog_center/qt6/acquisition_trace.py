from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.runtime_logging import redact


_LOCK = threading.Lock()


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        cleaned = redact(value)
        return cleaned[:2400] + "…" if len(cleaned) > 2400 else cleaned
    if isinstance(value, (int, float, bool, type(None))):
        return value
    cleaned = redact(value)
    return cleaned[:2400] + "…" if len(cleaned) > 2400 else cleaned


def log_path(db) -> Path:
    root = Path(db.path).resolve().parent / "logs" / "acquisition"
    root.mkdir(parents=True, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    return root / f"acquisition-{day}.jsonl"


def event(
    db,
    action: str,
    *,
    status: str = "info",
    source_code: str = "",
    external_id: str = "",
    url: str = "",
    method: str = "",
    message: str = "",
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": str(action or "event")[:100],
        "status": str(status or "info")[:32],
        "source_code": str(source_code or "")[:80],
        "external_id": str(external_id or "")[:160],
        "url": _sanitize(str(url or "")),
        "method": str(method or "")[:80],
        "message": _sanitize(str(message or "")),
        "detail": _sanitize(detail or {}),
    }
    path = log_path(db)
    with _LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return record


def recent_events(db, limit: int = 60) -> list[dict[str, Any]]:
    path = log_path(db)
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    output: list[dict[str, Any]] = []
    for raw in lines[-max(1, min(500, int(limit or 60))):]:
        try:
            item = json.loads(raw)
        except Exception:
            continue
        if isinstance(item, dict):
            output.append(item)
    return output
