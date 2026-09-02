from __future__ import annotations

import ftplib
import html
import json
import re
import socket
import ssl
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urljoin, urlsplit

from .batch_packaging import validate_batch_package


Progress = Callable[[str], None]
BATCH_NAME = re.compile(r"^desktop_catalog_v85_[0-9]{8}_[0-9]{6}$")
STORE_MEDIA_RE = re.compile(
    r"(?:src|href)=[\"']([^\"']*/media/store/products/[^\"']+)[\"']",
    re.IGNORECASE,
)


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
        return {
            "ok": True,
            "host": cfg.ftp_host,
            "port": cfg.ftp_port,
            "remote_path": pwd,
            "welcome": welcome[:200],
        }
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

    # Phase48.2 / Epic49: reject broken image mappings before opening FTP.
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
    return {
        "remote_batch": remote_batch,
        "uploaded_files": uploaded,
        "total_files": len(files),
    }


def _json_request(url: str, token: str, payload: dict | None, timeout: int) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib_request.Request(
        url,
        data=body,
        headers=headers,
        method="GET" if body is None else "POST",
    )
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


def _absolute_public_url(cfg: SiteConnection, value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    url = urljoin(cfg.site_url.rstrip("/") + "/", value)
    expected = urlsplit(cfg.site_url)
    actual = urlsplit(url)
    if actual.scheme not in {"http", "https"} or actual.netloc.lower() != expected.netloc.lower():
        raise ValueError("Public verification URL must stay on the configured site host")
    return url


def _public_get(cfg: SiteConnection, value: str, *, expect_image: bool = False, attempts: int = 3) -> dict:
    url = _absolute_public_url(cfg, value)
    if not url:
        return {"ok": False, "url": "", "http_status": 0, "content_type": "", "error": "empty URL", "body": b""}

    last_error = ""
    for attempt in range(max(1, int(attempts))):
        req = urllib_request.Request(
            url,
            headers={
                "Accept": "image/avif,image/webp,image/*,*/*;q=0.8" if expect_image else "text/html,application/xhtml+xml,*/*;q=0.8",
                "User-Agent": "3DPrintHub-Catalog-Epic49/1.0",
                "Cache-Control": "no-cache",
            },
            method="GET",
        )
        try:
            with urllib_request.urlopen(req, timeout=max(10, cfg.timeout), context=ssl.create_default_context()) as response:
                body = response.read(2_000_000 if not expect_image else 64_000)
                status = int(response.status)
                content_type = str(response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
                ok = status == 200 and bool(body)
                if expect_image:
                    ok = ok and content_type.startswith("image/")
                else:
                    ok = ok and (content_type in {"text/html", "application/xhtml+xml"} or body.lstrip().startswith(b"<"))
                return {
                    "ok": bool(ok),
                    "url": response.geturl(),
                    "http_status": status,
                    "content_type": content_type,
                    "bytes_sampled": len(body),
                    "error": "" if ok else "unexpected public response",
                    "body": body,
                }
        except urllib_error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(1.2 * (attempt + 1))
    return {
        "ok": False,
        "url": url,
        "http_status": 0,
        "content_type": "",
        "bytes_sampled": 0,
        "error": last_error or "public verification failed",
        "body": b"",
    }


def verify_publish_item(settings: SiteConnection, item: dict, *, max_images: int = 6) -> dict:
    """Verify the actual public Product page and media after Bridge import.

    Bridge/database success alone is not enough for Epic49. The desktop confirms
    that the public product page is HTTP 200, extracts the Store product media
    rendered in that page, and checks the images themselves over HTTPS.
    """

    cfg = settings.normalized()
    product_path = str(item.get("product_url") or "").strip()
    page = _public_get(cfg, product_path, expect_image=False)
    page_body = page.pop("body", b"")
    result = {
        "ok": False,
        "product": page,
        "images": [],
        "main_image_url": "",
        "error": "",
    }
    if not page.get("ok"):
        result["error"] = f"PRODUCT_HTTP_FAILED: {page.get('error') or page.get('http_status')}"
        return result

    text = page_body.decode("utf-8", errors="replace")
    discovered = []
    for raw in STORE_MEDIA_RE.findall(text):
        candidate = html.unescape(str(raw or "").strip())
        if candidate and candidate not in discovered:
            discovered.append(candidate)
        if len(discovered) >= max(1, int(max_images)):
            break
    if not discovered:
        result["error"] = "PRODUCT_MEDIA_NOT_FOUND_IN_PUBLIC_HTML"
        return result

    checks = []
    for candidate in discovered:
        check = _public_get(cfg, candidate, expect_image=True)
        check.pop("body", None)
        checks.append(check)
    result["images"] = checks
    result["main_image_url"] = checks[0].get("url") if checks else ""
    result["ok"] = bool(checks and all(check.get("ok") for check in checks))
    if not result["ok"]:
        bad = next((check for check in checks if not check.get("ok")), {})
        result["error"] = f"PRODUCT_MEDIA_HTTP_FAILED: {bad.get('url') or '-'} {bad.get('error') or bad.get('http_status')}"
    return result


def _augment_ack_with_public_verification(cfg: SiteConnection, ack: dict) -> dict:
    for item in ack.get("items") or []:
        if not isinstance(item, dict):
            continue
        if item.get("visible_on_store") is not True or not item.get("product_url"):
            continue
        verification = verify_publish_item(cfg, item)
        item["public_http_checks"] = verification
        item["public_http_ok"] = bool(verification.get("ok"))
        item["public_product_http_status"] = int((verification.get("product") or {}).get("http_status") or 0)
        item["public_main_image_url"] = str(verification.get("main_image_url") or "")
        main_check = (verification.get("images") or [{}])[0] if verification.get("images") else {}
        item["public_main_image_http_status"] = int(main_check.get("http_status") or 0)
        if not item["public_http_ok"] and not item.get("error"):
            item["error"] = verification.get("error") or "PUBLIC_HTTP_VERIFY_FAILED"
    return ack


def test_publish_readiness(settings: SiteConnection) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    return _json_request(
        f"{cfg.site_url}/api/catalog-bridge/v1/publish-readiness/",
        cfg.bridge_token,
        None,
        cfg.timeout,
    )


def test_bridge(settings: SiteConnection) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    return _json_request(
        f"{cfg.site_url}/api/catalog-bridge/v1/health/",
        cfg.bridge_token,
        None,
        cfg.timeout,
    )


def import_batch(settings: SiteConnection, batch_name: str, batch_uuid: str) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    ack = _json_request(
        f"{cfg.site_url}/api/catalog-bridge/v1/import/",
        cfg.bridge_token,
        {"batch_name": batch_name, "batch_uuid": batch_uuid, "schema_version": "8.5"},
        max(60, cfg.timeout),
    )
    return _augment_ack_with_public_verification(cfg, ack)


def get_batch_diagnostic(settings: SiteConnection, batch_name: str) -> dict:
    cfg = settings.normalized()
    if not cfg.bridge_token:
        raise ValueError("Bridge token is empty")
    if not BATCH_NAME.fullmatch(str(batch_name or "")):
        raise ValueError("Batch name is not valid for diagnostics")
    return _json_request(
        f"{cfg.site_url}/api/catalog-bridge/v1/diagnostics/{batch_name}/",
        cfg.bridge_token,
        None,
        cfg.timeout,
    )
