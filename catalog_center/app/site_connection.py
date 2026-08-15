from __future__ import annotations

import ftplib
import json
import re
import socket
import ssl
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable
from urllib import error as urllib_error
from urllib import request as urllib_request

from .batch_packaging import validate_batch_package


Progress = Callable[[str], None]
BATCH_NAME = re.compile(r"^desktop_catalog_v85_[0-9]{8}_[0-9]{6}$")


@dataclass(frozen=True)
class SiteConnection:
    ftp_host: str
    ftp_port: int
    ftp_user: str
    ftp_password: str
    remote_root: str
    site_url: str
    bridge_token: str
    passive: bool = True
    timeout: int = 30

    def normalized(self) -> "SiteConnection":
        root = "/" + str(PurePosixPath("/" + (self.remote_root or "/").strip("/"))).strip("/")
        return SiteConnection(
            ftp_host=self.ftp_host.strip(),
            ftp_port=int(self.ftp_port),
            ftp_user=self.ftp_user.strip(),
            ftp_password=self.ftp_password,
            remote_root=root.rstrip("/") or "/",
            site_url=self.site_url.strip().rstrip("/"),
            bridge_token=self.bridge_token.strip(),
            passive=bool(self.passive),
            timeout=max(3, int(self.timeout)),
        )


def tcp_probe(host: str, port: int, timeout: int = 10) -> None:
    with socket.create_connection((host, int(port)), timeout=timeout):
        return


def connect_ftp(settings: SiteConnection) -> ftplib.FTP:
    cfg = settings.normalized()
    ftp = ftplib.FTP(timeout=cfg.timeout, encoding="utf-8")
    ftp.connect(cfg.ftp_host, cfg.ftp_port)
    ftp.login(cfg.ftp_user, cfg.ftp_password)
    ftp.set_pasv(cfg.passive)
    return ftp


def _ensure_remote_dir(ftp: ftplib.FTP, remote_dir: str) -> None:
    original = ftp.pwd()
    try:
        ftp.cwd("/")
        for part in PurePosixPath(remote_dir).parts:
            if part in {"", "/"}:
                continue
            try:
                ftp.cwd(part)
            except ftplib.error_perm as exc:
                if not str(exc).startswith("550"):
                    raise
                ftp.mkd(part)
                ftp.cwd(part)
    finally:
        ftp.cwd(original)


def test_ftp(settings: SiteConnection) -> dict[str, str | int | bool]:
    cfg = settings.normalized()
    ftp = connect_ftp(cfg)
    try:
        welcome = ftp.getwelcome() or ""
        ftp.cwd(cfg.remote_root)
        pwd = ftp.pwd()
        return {"ok": True, "host": cfg.ftp_host, "port": cfg.ftp_port, "remote_path": pwd, "welcome": welcome[:200]}
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def upload_batch(settings: SiteConnection, batch: Path, progress: Progress | None = None) -> dict[str, object]:
    cfg = settings.normalized()
    batch = Path(batch).resolve()
    manifest_path = batch / "batch_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Batch manifest not found: {manifest_path}")
    if not BATCH_NAME.fullmatch(batch.name):
        raise ValueError("Batch directory name is not valid for the v8.5 Bridge")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if str(manifest.get("schema_version") or "") != "8.5":
        raise ValueError("Batch manifest schema must be 8.5")
    if str(manifest.get("batch_name") or "") != batch.name:
        raise ValueError("Batch directory and manifest names do not match")
    if not str(manifest.get("batch_uuid") or "").strip():
        raise ValueError("Batch UUID is missing")

    # Phase48.2: reject broken image mappings before opening FTP.
    validate_batch_package(batch)

    remote_batch = str(PurePosixPath(cfg.remote_root) / "imports" / "desktop_catalog" / "pending" / batch.name)
    files = sorted(path for path in batch.rglob("*") if path.is_file())
    ftp = connect_ftp(cfg)
    uploaded = 0
    try:
        _ensure_remote_dir(ftp, remote_batch)
        for path in files:
            relative = path.relative_to(batch).as_posix()
            remote_file = str(PurePosixPath(remote_batch) / relative)
            _ensure_remote_dir(ftp, str(PurePosixPath(remote_file).parent))
            if progress:
                progress(f"FTP_UPLOAD {uploaded + 1}/{len(files)} {relative}")
            with path.open("rb") as handle:
                ftp.storbinary(f"STOR {remote_file}", handle, blocksize=128 * 1024)
            uploaded += 1
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    return {"remote_batch": remote_batch, "uploaded_files": uploaded, "total_files": len(files)}


def _json_request(url: str, token: str, payload: dict | None, timeout: int) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib_request.Request(url, data=body, headers=headers, method="GET" if body is None else "POST")
    context = ssl.create_default_context()
    try:
        with urllib_request.urlopen(req, timeout=timeout, context=context) as response:
            raw = response.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw or "{}")
            if not isinstance(parsed, dict):
                raise RuntimeError("Bridge response is not a JSON object")
            parsed.setdefault("http_status", response.status)
            return parsed
    except urllib_error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
        except Exception:
            detail = {"detail": raw[:2000]}
        raise RuntimeError(f"Bridge HTTP {exc.code}: {detail}") from exc


def test_bridge(settings: SiteConnection) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    return _json_request(f"{cfg.site_url}/api/catalog-bridge/v1/health/", cfg.bridge_token, None, cfg.timeout)


def import_batch(settings: SiteConnection, batch_name: str, batch_uuid: str) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    return _json_request(
        f"{cfg.site_url}/api/catalog-bridge/v1/import/",
        cfg.bridge_token,
        {"batch_name": batch_name, "batch_uuid": batch_uuid, "schema_version": "8.5"},
        max(60, cfg.timeout),
    )
