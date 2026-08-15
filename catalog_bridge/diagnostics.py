from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def diagnostics_root(pending_root: Path) -> Path:
    root = Path(pending_root).resolve().parent / "diagnostics"
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except OSError:
        pass
    return root


def diagnostic_path(pending_root: Path, batch_name: str) -> Path:
    return diagnostics_root(pending_root) / f"{batch_name}.json"


def write_import_diagnostic(
    pending_root: Path,
    batch_name: str,
    *,
    batch_uuid: str = "",
    status: str,
    ack: dict | None = None,
    command_error: str = "",
    stdout: str = "",
    stderr: str = "",
    detail: str = "",
) -> Path:
    """Persist a secret-free, structured import diagnostic atomically."""

    target = diagnostic_path(pending_root, batch_name)
    payload = {
        "version": "49.0",
        "created_at": _utc_now(),
        "batch_name": str(batch_name or ""),
        "batch_uuid": str(batch_uuid or ""),
        "status": str(status or ""),
        "detail": str(detail or "")[:4000],
        "command_error": str(command_error or "")[:4000],
        "stdout_tail": str(stdout or "")[-8000:],
        "stderr_tail": str(stderr or "")[-8000:],
        "ack": ack if isinstance(ack, dict) else None,
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.chmod(temp_name, 0o600)
        except OSError:
            pass
        os.replace(temp_name, target)
    finally:
        try:
            Path(temp_name).unlink()
        except FileNotFoundError:
            pass
    return target
