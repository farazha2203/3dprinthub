from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import PurePosixPath

FORBIDDEN_PREFIXES = (
    ".phase-backups/",
    ".venv/",
    "venv/",
    "env/",
    "media/",
    "private_media/",
    "staticfiles/",
    "static/velzon/",
    "static/velzon_master/",
    "static/fonts/",
)
FORBIDDEN_SUFFIXES = (
    ".zip",
    ".sqlite3",
    ".log",
    ".pem",
    ".key",
    ".crt",
)
FORBIDDEN_BASENAMES = {".env", "db.sqlite3", "db.sqlite3-journal"}
TEXT_SUFFIXES = {
    ".py", ".html", ".css", ".js", ".json", ".md", ".txt", ".yml",
    ".yaml", ".toml", ".ini", ".cfg", ".ps1", ".sh", ".xml", ".svg",
}
SECRET_PATTERNS = (
    ("Mapbox access token", re.compile(r"\b(?:pk|sk)\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("Telegram bot token", re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}\b")),
    ("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip())
    return proc


def staged_files() -> list[str]:
    raw = run_git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").stdout
    return [item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item]


def is_forbidden(path: str) -> str | None:
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()
    if lowered.startswith(FORBIDDEN_PREFIXES):
        return "forbidden runtime, backup, font, or vendor path"
    if lowered.endswith(FORBIDDEN_SUFFIXES):
        return "forbidden binary, secret, database, or archive suffix"
    if PurePosixPath(normalized).name.lower() in FORBIDDEN_BASENAMES:
        return "forbidden runtime or secret file"
    if normalized.startswith("PHASE") and (
        normalized.endswith("_PATCH_MANIFEST.json")
        or "_VERIFICATION_REPORT" in normalized
        or normalized.endswith("_DELETE_PATHS.txt")
    ):
        return "generated local phase artifact"
    return None


def staged_blob(path: str) -> bytes:
    return run_git("show", f":{path}").stdout


def main() -> int:
    files = staged_files()
    violations: list[dict[str, object]] = []

    for path in files:
        reason = is_forbidden(path)
        if reason:
            violations.append({"path": path, "reason": reason})
            continue

        suffix = PurePosixPath(path).suffix.lower()
        if suffix not in TEXT_SUFFIXES:
            continue
        data = staged_blob(path)
        if len(data) > 5 * 1024 * 1024:
            continue
        text = data.decode("utf-8", "replace")
        for line_number, line in enumerate(text.splitlines(), 1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        {"path": path, "line": line_number, "reason": label}
                    )

    result = {
        "staged_files": len(files),
        "violations": violations,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if violations:
        print("PHASE30_RELEASE_SCAN=FAILED", file=sys.stderr)
        return 1
    print("PHASE30_RELEASE_SCAN=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
