#!/usr/bin/env python3
"""Loopback-only authenticated command bridge for reverse SSH operations.

Transport only: this does not replace repository release/deploy gates.
The caller receives the same OS privileges as the account running this process.
"""
from __future__ import annotations

import argparse
import hmac
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

BRIDGE_VERSION = "1.0.0"
TOKEN_ENV = "OPERATOR_BRIDGE_TOKEN"
MAX_REQUEST_BYTES = 256 * 1024
MAX_COMMAND_CHARS = 64 * 1024
MAX_OUTPUT_BYTES = 8 * 1024 * 1024
MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 1200
TOKEN_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.end_headers()
    handler.wfile.write(body)


def is_loopback(address: str) -> bool:
    try:
        return ipaddress.ip_address(address).is_loopback
    except ValueError:
        return False


def path_within(base: Path, candidate: str) -> Path | None:
    try:
        resolved = Path(candidate).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    try:
        resolved.relative_to(base)
    except ValueError:
        return None
    return resolved


def authorized(handler: BaseHTTPRequestHandler) -> bool:
    expected = os.environ.get(TOKEN_ENV, "")
    supplied = handler.headers.get("Authorization", "")
    if not supplied.startswith("Bearer "):
        return False
    return hmac.compare_digest(supplied[7:].strip(), expected)


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "ReverseHostBridge/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # The default log contains method/path/status only; authorization headers are never logged.
        super().log_message(fmt, *args)

    @property
    def bridge(self) -> "BridgeServer":
        return self.server  # type: ignore[return-value]

    def do_GET(self) -> None:
        if self.path != "/health":
            json_response(self, 404, {"ok": False, "error": "not_found"})
            return
        if not authorized(self):
            json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return
        json_response(self, 200, {
            "ok": True,
            "version": BRIDGE_VERSION,
            "base": str(self.bridge.base),
            "pid": os.getpid(),
        })

    def do_POST(self) -> None:
        if self.path != "/exec":
            json_response(self, 404, {"ok": False, "error": "not_found"})
            return
        if not authorized(self):
            json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            json_response(self, 400, {"ok": False, "error": "invalid_content_length"})
            return
        if length <= 0 or length > MAX_REQUEST_BYTES:
            json_response(self, 413, {"ok": False, "error": "request_too_large"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            json_response(self, 400, {"ok": False, "error": "invalid_json"})
            return
        command = payload.get("command")
        if not isinstance(command, str) or not command.strip() or len(command) > MAX_COMMAND_CHARS:
            json_response(self, 400, {"ok": False, "error": "invalid_command"})
            return
        cwd_raw = payload.get("cwd")
        if cwd_raw is None:
            cwd = self.bridge.base
        elif isinstance(cwd_raw, str):
            cwd = path_within(self.bridge.base, cwd_raw)
            if cwd is None:
                json_response(self, 400, {"ok": False, "error": "cwd_outside_base"})
                return
        else:
            json_response(self, 400, {"ok": False, "error": "invalid_cwd"})
            return
        timeout_raw = payload.get("timeout", 120)
        if not isinstance(timeout_raw, int) or not MIN_TIMEOUT_SECONDS <= timeout_raw <= MAX_TIMEOUT_SECONDS:
            json_response(self, 400, {"ok": False, "error": "invalid_timeout"})
            return
        try:
            child_env = dict(os.environ)
            child_env.pop(TOKEN_ENV, None)
            completed = subprocess.run(
                ["/bin/bash", "-lc", command],
                cwd=str(cwd),
                capture_output=True,
                timeout=timeout_raw,
                check=False,
                env=child_env,
            )
            stdout = completed.stdout[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stderr = completed.stderr[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
            json_response(self, 200, {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "stdout_truncated": len(completed.stdout) > MAX_OUTPUT_BYTES,
                "stderr_truncated": len(completed.stderr) > MAX_OUTPUT_BYTES,
            })
        except subprocess.TimeoutExpired:
            json_response(self, 408, {"ok": False, "error": "timeout", "timeout": timeout_raw})


class BridgeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], handler: type[BaseHTTPRequestHandler], base: Path) -> None:
        self.base = base
        super().__init__(address, handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loopback-only authenticated operator bridge")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--base", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not is_loopback(args.host):
        raise SystemExit("bridge host must be loopback")
    if not 1024 <= args.port <= 65535:
        raise SystemExit("bridge port must be between 1024 and 65535")
    token = os.environ.get(TOKEN_ENV, "")
    if not TOKEN_PATTERN.fullmatch(token):
        raise SystemExit(f"{TOKEN_ENV} must be exactly 64 hexadecimal characters")
    base = Path(args.base).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise SystemExit("bridge base must be an existing directory")
    server = BridgeServer((args.host, args.port), BridgeHandler, base)
    print(f"REVERSE_HOST_BRIDGE_READY={args.host}:{args.port} BASE={base}", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
