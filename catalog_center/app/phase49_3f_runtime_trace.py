from __future__ import annotations

import getpass
import json
import os
import socket
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .runtime_logging import redact

_LOCK = threading.Lock()
_ROOT: Path | None = None
_SESSION = uuid.uuid4().hex
_OPERATOR = ""
_WORKSTATION = ""

SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "api-key",
    "password",
    "secret",
    "token",
    "bridge_token",
    "access_token",
    "refresh_token",
    "management_key",
    "admin_key",
}


def configure(data_root: str | Path, *, operator: str = "", workstation: str = "") -> Path:
    global _ROOT, _OPERATOR, _WORKSTATION
    _OPERATOR = str(operator or os.getenv("CATALOG_OPERATOR_NAME") or getpass.getuser() or "operator")[:120]
    _WORKSTATION = str(workstation or os.getenv("COMPUTERNAME") or socket.gethostname() or "workstation")[:120]
    day = datetime.now().strftime("%Y-%m-%d")
    _ROOT = Path(data_root) / "logs" / "phase49_3f" / day
    _ROOT.mkdir(parents=True, exist_ok=True)
    return current_log_path()


def current_log_path() -> Path:
    root = _ROOT or (Path(r"D:\projects\3dprinthub-catalog-manager") / "logs" / "phase49_3f" / datetime.now().strftime("%Y-%m-%d"))
    return root / f"workflow-{_SESSION}.jsonl"


def log_folder() -> Path:
    return current_log_path().parent


def _sanitize(value: Any):
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in {item.replace("-", "_") for item in SENSITIVE_KEYS} or any(
                token in normalized for token in ("password", "token", "secret", "api_key", "authorization")
            ):
                output[str(key)] = "***REDACTED***"
            else:
                output[str(key)] = _sanitize(item)
        return output
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        text = redact(value)
        return text[:4000] + "…" if len(text) > 4000 else text
    if isinstance(value, (int, float, bool, type(None))):
        return value
    text = redact(value)
    return text[:4000] + "…" if len(text) > 4000 else text


def event(
    area: str,
    action: str,
    *,
    status: str = "info",
    product_id: int | None = None,
    provider: str = "",
    model: str = "",
    elapsed_ms: int | None = None,
    message: str = "",
    detail: dict | None = None,
) -> dict:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "epoch_ms": int(time.time() * 1000),
        "session_id": _SESSION,
        "operator": _OPERATOR,
        "workstation": _WORKSTATION,
        "area": str(area or "runtime")[:80],
        "action": str(action or "event")[:120],
        "status": str(status or "info")[:40],
        "product_id": int(product_id) if product_id not in (None, "") else None,
        "provider": str(provider or "")[:60],
        "model": str(model or "")[:180],
        "elapsed_ms": int(elapsed_ms) if elapsed_ms is not None else None,
        "message": _sanitize(str(message or ""))[:2000],
        "detail": _sanitize(detail or {}),
    }
    path = current_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return record


class Span:
    def __init__(self, area: str, action: str, **meta):
        self.area = area
        self.action = action
        self.meta = meta
        self.started = 0.0

    def __enter__(self):
        self.started = time.perf_counter()
        event(self.area, self.action + ":start", **self.meta)
        return self

    def __exit__(self, exc_type, exc, _tb):
        elapsed = int((time.perf_counter() - self.started) * 1000)
        if exc is None:
            event(self.area, self.action + ":done", elapsed_ms=elapsed, **self.meta)
        else:
            event(
                self.area,
                self.action + ":error",
                status="error",
                elapsed_ms=elapsed,
                message=f"{exc_type.__name__}: {exc}",
                **self.meta,
            )
        return False
