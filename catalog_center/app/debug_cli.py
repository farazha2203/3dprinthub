from __future__ import annotations

import argparse
import json
import socket
from pathlib import Path

from .db import Database
from .secure_secrets import get_secret, secret_source
from .site_connection import SiteConnection, tcp_probe, test_bridge, test_ftp
from .version import APP_VERSION


DEFAULT_DATA = Path(r"D:\projects\3dprinthub-catalog-manager")


def emit(key: str, value) -> None:
    print(f"{key}={value}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="3DPrintHub Catalog Intelligence diagnostics")
    parser.add_argument("--connections", action="store_true")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    db_path = args.data_root / "catalog.sqlite3"
    emit("CATALOG_VERSION", APP_VERSION)
    emit("SOURCE_ROOT", Path(__file__).resolve().parents[1])
    emit("DATABASE_PATH", db_path)
    emit("LOG_PATH", args.data_root / "logs" / "catalog-intelligence.log")
    db = Database(db_path)
    try:
        integrity = db.conn.execute("PRAGMA integrity_check").fetchone()[0]
        emit("SQLITE_INTEGRITY", integrity)
        emit("SQLITE_SCHEMA_VERSION", 7)
        host = db.setting("ftp_host", "ftp.3dprinthub.ir")
        port = int(db.setting("ftp_port", "21"))
        user = db.setting("ftp_user", "sfkilvrs")
        remote = db.setting("ftp_remote_root", "/3dprinthub")
        site = db.setting("site_url", "https://3dprinthub.ir")
        emit("FTP_TARGET", f"{host}:{port}")
        emit("FTP_REMOTE_ROOT", remote)
        emit("SITE_URL", site)
        emit("FTP_PASSWORD_SOURCE", secret_source("ftp_password"))
        emit("BRIDGE_TOKEN_SOURCE", secret_source("bridge_token"))
        addresses = sorted({row[4][0] for row in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)})
        emit("DNS_ADDRESSES", ",".join(addresses))
        tcp_probe(host, port, timeout=10)
        emit("FTP_TCP", "OK")
        if args.connections:
            cfg = SiteConnection(
                ftp_host=host, ftp_port=port, ftp_user=user,
                ftp_password=get_secret("ftp_password"), remote_root=remote,
                site_url=site, bridge_token=get_secret("bridge_token"),
            )
            emit("FTP_LOGIN", json.dumps(test_ftp(cfg), ensure_ascii=False))
            emit("BRIDGE_HEALTH", json.dumps(test_bridge(cfg), ensure_ascii=False))
    finally:
        db.close()
    emit("CATALOG_DEBUG_PREFLIGHT", "OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
