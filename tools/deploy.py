from __future__ import annotations

import argparse
import ftplib
import getpass
import hashlib
import io
import json
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


class DeployError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise DeployError(f"Invalid JSON: {path}: {exc}") from exc


def render_token(value: str, mapping: dict[str, str]) -> str:
    for key, replacement in mapping.items():
        value = value.replace("{" + key + "}", replacement)
    return value


def run_preflight(manifest: dict[str, Any], project_root: Path) -> None:
    mapping = {
        "python": sys.executable,
        "project_root": str(project_root),
    }
    checks = manifest.get("preflight", [])
    print(f"PRECHECK_COUNT={len(checks)}")
    for index, check in enumerate(checks, start=1):
        name = check.get("name") or f"check_{index}"
        cmd = [render_token(str(x), mapping) for x in check["cmd"]]
        print(f"PRECHECK[{index}]={name}")
        result = subprocess.run(cmd, cwd=project_root, shell=False)
        if result.returncode != 0:
            print(f"PRECHECK_FAILED={name}")
            print("DEPLOY_ABORTED=1")
            raise DeployError(f"Preflight failed: {name} (exit {result.returncode})")
        print(f"PRECHECK_OK={name}")
    print("PRECHECK=OK")


@dataclass
class RemoteFile:
    exists: bool
    data: bytes | None
    sha256: str | None


class FTPClient:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.ftp: ftplib.FTP | ftplib.FTP_TLS | None = None

    def __enter__(self) -> "FTPClient":
        protocol = str(self.config.get("protocol", "ftp")).lower()
        secure = bool(self.config.get("secure", False))
        host = self.config.get("host")
        port = int(self.config.get("port") or (21 if protocol in {"ftp", "ftps"} else 21))
        username = self.config.get("username")
        password = self.config.get("password") or os.getenv("DEPLOY_FTP_PASSWORD")
        if not password:
            password = getpass.getpass("FTP password: ")
        timeout = max(10, int(self.config.get("connectTimeout", 30000)) // 1000)

        if protocol not in {"ftp", "ftps"}:
            raise DeployError(
                f"This deploy tool currently supports FTP/FTPS. Config protocol is {protocol!r}."
            )

        if protocol == "ftps" or secure:
            ftp = ftplib.FTP_TLS(timeout=timeout)
            ftp.connect(host, port)
            ftp.login(username, password)
            ftp.prot_p()
        else:
            ftp = ftplib.FTP(timeout=timeout)
            ftp.connect(host, port)
            ftp.login(username, password)
        ftp.set_pasv(True)
        self.ftp = ftp
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.ftp is None:
            return
        try:
            self.ftp.quit()
        except Exception:
            try:
                self.ftp.close()
            except Exception:
                pass

    @property
    def conn(self) -> ftplib.FTP | ftplib.FTP_TLS:
        if self.ftp is None:
            raise DeployError("FTP is not connected")
        return self.ftp

    def read(self, remote_path: str) -> RemoteFile:
        buf = io.BytesIO()
        try:
            self.conn.retrbinary(f"RETR {remote_path}", buf.write)
        except ftplib.error_perm as exc:
            if str(exc).startswith("550"):
                return RemoteFile(False, None, None)
            raise
        data = buf.getvalue()
        return RemoteFile(True, data, sha256_bytes(data))

    def ensure_dir(self, remote_dir: str) -> None:
        remote_dir = posixpath.normpath(remote_dir)
        if remote_dir in {"", ".", "/"}:
            return
        absolute = remote_dir.startswith("/")
        parts = [p for p in remote_dir.split("/") if p]
        current = "/" if absolute else ""
        for part in parts:
            current = posixpath.join(current, part)
            try:
                self.conn.mkd(current)
            except ftplib.error_perm as exc:
                # 550 commonly means it already exists. Verify by trying cwd then return.
                if not str(exc).startswith("550"):
                    raise

    def upload_bytes(self, remote_path: str, data: bytes) -> None:
        self.ensure_dir(posixpath.dirname(remote_path))
        self.conn.storbinary(f"STOR {remote_path}", io.BytesIO(data), blocksize=1024 * 256)

    def delete_if_exists(self, remote_path: str) -> None:
        try:
            self.conn.delete(remote_path)
        except ftplib.error_perm as exc:
            if not str(exc).startswith("550"):
                raise

    def rename(self, old: str, new: str) -> None:
        self.conn.rename(old, new)




def verify_expected_hashes(manifest: dict[str, Any], project_root: Path) -> None:
    expected = manifest.get("expected_sha256", {})
    if not expected:
        return
    for rel, wanted in expected.items():
        rel_norm = str(rel).replace("\\", "/").lstrip("/")
        path = project_root / Path(rel_norm)
        if not path.is_file():
            raise DeployError(f"Expected local file missing: {path}")
        actual = sha256_file(path).lower()
        if actual != str(wanted).lower():
            raise DeployError(
                f"Local release hash mismatch for {rel_norm}: expected {wanted}, got {actual}"
            )
        print(f"LOCAL_RELEASE_HASH_OK {rel_norm}")
    print("LOCAL_RELEASE_HASHES=OK")

def relative_files(manifest: dict[str, Any]) -> list[str]:
    files = []
    seen = set()
    for item in manifest.get("files", []):
        rel = str(item).replace("\\", "/").lstrip("/")
        if not rel or rel in seen:
            continue
        if ".." in Path(rel).parts:
            raise DeployError(f"Unsafe manifest path: {rel}")
        files.append(rel)
        seen.add(rel)
    if not files:
        raise DeployError("Manifest contains no files")
    return files


def resolve_paths(manifest_path: Path, manifest: dict[str, Any]) -> tuple[Path, Path]:
    base = manifest_path.parent
    project_root = Path(manifest.get("project_root", "."))
    if not project_root.is_absolute():
        project_root = (base / project_root).resolve()
    config_path = Path(manifest.get("connection_config", ".vscode/sftp.json"))
    if not config_path.is_absolute():
        config_path = (base / config_path).resolve()
    return project_root, config_path


def backup_remote(backup_root: Path, rel: str, remote: RemoteFile) -> None:
    if not remote.exists or remote.data is None:
        return
    target = backup_root / Path(rel)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(remote.data)


def deploy_one(
    ftp: FTPClient,
    local_path: Path,
    remote_path: str,
    rel: str,
    remote: RemoteFile,
    backup_root: Path,
    stamp: str,
) -> None:
    local_data = local_path.read_bytes()
    local_hash = sha256_bytes(local_data)
    backup_remote(backup_root, rel, remote)

    temp_path = remote_path + f".__uploading__.{stamp}"
    old_path = remote_path + f".__previous__.{stamp}"

    ftp.delete_if_exists(temp_path)
    ftp.delete_if_exists(old_path)
    ftp.upload_bytes(temp_path, local_data)
    temp_remote = ftp.read(temp_path)
    if not temp_remote.exists or temp_remote.sha256 != local_hash:
        ftp.delete_if_exists(temp_path)
        raise DeployError(f"Remote temp hash mismatch: {rel}")

    moved_old = False
    try:
        if remote.exists:
            ftp.rename(remote_path, old_path)
            moved_old = True
        ftp.rename(temp_path, remote_path)
        final_remote = ftp.read(remote_path)
        if not final_remote.exists or final_remote.sha256 != local_hash:
            raise DeployError(f"Remote final hash mismatch: {rel}")
        if moved_old:
            ftp.delete_if_exists(old_path)
    except Exception:
        try:
            ftp.delete_if_exists(temp_path)
        except Exception:
            pass
        if moved_old:
            try:
                ftp.delete_if_exists(remote_path)
                ftp.rename(old_path, remote_path)
                print(f"ROLLBACK_OK={rel}")
            except Exception as rollback_exc:
                print(f"ROLLBACK_FAILED={rel}: {rollback_exc}")
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="3DPrintHub manifest-based FTP deploy")
    parser.add_argument("--manifest", required=True, help="Path to deployment manifest JSON")
    parser.add_argument("--apply", action="store_true", help="Upload changed files after preflight")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip local checks (not recommended)")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    manifest = load_json(manifest_path)
    project_root, config_path = resolve_paths(manifest_path, manifest)
    if not project_root.exists():
        raise DeployError(f"Project root not found: {project_root}")
    if not config_path.exists():
        raise DeployError(f"Connection config not found: {config_path}")

    files = relative_files(manifest)
    for rel in files:
        if not (project_root / Path(rel)).is_file():
            raise DeployError(f"Manifest source file missing: {project_root / Path(rel)}")

    verify_expected_hashes(manifest, project_root)

    print(f"DEPLOY_NAME={manifest.get('name', manifest_path.stem)}")
    print(f"PROJECT_ROOT={project_root}")
    print(f"MANIFEST_FILES={len(files)}")

    if not args.skip_preflight:
        run_preflight(manifest, project_root)

    conn_config = load_json(config_path)
    if isinstance(conn_config, list):
        profile_name = manifest.get("connection_name")
        matches = [x for x in conn_config if x.get("name") == profile_name]
        if not matches:
            raise DeployError(f"Connection profile not found: {profile_name}")
        conn_config = matches[0]

    remote_root = str(manifest.get("remote_root") or conn_config.get("remotePath") or "/").rstrip("/")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_base = Path(manifest.get("backup_root") or (project_root / ".deploy-backups"))
    if not backup_base.is_absolute():
        backup_base = (manifest_path.parent / backup_base).resolve()
    backup_root = backup_base / str(manifest.get("name", manifest_path.stem)) / stamp

    changed: list[tuple[str, Path, str, RemoteFile, str]] = []
    unchanged = 0
    missing = 0

    with FTPClient(conn_config) as ftp:
        for rel in files:
            local_path = project_root / Path(rel)
            local_hash = sha256_file(local_path)
            remote_path = posixpath.join(remote_root, rel)
            remote = ftp.read(remote_path)
            if remote.exists and remote.sha256 == local_hash:
                unchanged += 1
                print(f"REMOTE_SAME {rel}")
                continue
            if not remote.exists:
                missing += 1
                status = "REMOTE_MISSING"
            else:
                status = "REMOTE_CHANGED"
            print(f"{status} {rel}")
            changed.append((rel, local_path, remote_path, remote, local_hash))

        print(f"REMOTE_SAME_COUNT={unchanged}")
        print(f"REMOTE_MISSING_COUNT={missing}")
        print(f"UPLOAD_COUNT={len(changed)}")

        if not args.apply:
            print("DRY_RUN=OK")
            print("NEXT=rerun_with_--apply")
            return 0

        if not changed:
            print("NOTHING_TO_UPLOAD=1")
            print("DEPLOY_UPLOAD=OK")
            return 0

        uploaded = 0
        for rel, local_path, remote_path, remote, _local_hash in changed:
            print(f"UPLOAD_START {rel}")
            deploy_one(ftp, local_path, remote_path, rel, remote, backup_root, stamp)
            uploaded += 1
            print(f"UPLOAD_OK {rel}")

    print(f"LOCAL_REMOTE_BACKUP={backup_root}")
    print(f"FILES_UPLOADED={uploaded}")
    print("FILES_FAILED=0")
    print("DEPLOY_UPLOAD=OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DeployError as exc:
        print(f"DEPLOY_ERROR={exc}", file=sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print("DEPLOY_ABORTED_BY_USER=1", file=sys.stderr)
        raise SystemExit(130)
