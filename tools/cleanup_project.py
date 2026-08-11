from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Iterable

PROTECTED_TOP_LEVEL = {
    ".git",
    ".venv",
    ".env",
    "db.sqlite3",
    "media",
    "private_media",
    "static",
    "config",
    "store",
    "website",
    "templates",
    "smartbase_admin_bridge",
    "tools",
    "scripts",
    "deploy",
}

JUNK_TOP_LEVEL_DIRS = {
    ".phase-backups",
    "_local_backups",
    "patches",
    "staticfiles",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "build",
    "dist",
}

ROOT_JUNK_PATTERNS = (
    "*.zip",
    "Pasted text*.txt",
    "PHASE*_PATCH_MANIFEST.json",
    "PHASE*_VERIFICATION_REPORT.json",
    "PHASE*_VERIFICATION_REPORT.txt",
    "PHASE*_HOTFIX_REPORT.json",
    "PHASE*_REPORT.json",
    "PHASE*_DELETE_PATHS.txt",
    "PHASE*_BROWSER_TEST.json",
    "PHASE*_APPLIED.txt",
    "README_PHASE*.txt",
    "README_PHASE*.md",
    "*_HOTFIX_README_FA.md",
    "SMARTBASE-ADMIN-INSTALLATION.txt",
    "file_structure.txt",
    "requirements.bad.txt~",
    "APPLY_PHASE*.ps1",
    "PUBLISH_PHASE*.ps1",
    "RESTORE_PHASE*.ps1",
    "INSTALL_PHASE*.ps1",
    "UNINSTALL_PHASE*.ps1",
    "START_PHASE*.ps1",
    "STOP_PHASE*.ps1",
    "RUN_PHASE*.ps1",
    "fix_*.py",
    "rollback_*.py",
    "seed_*.py",
    "*.bak",
    "*.bak_*",
    "*.tmp",
    "*.orig",
    "*.rej",
    "*~",
)

RECURSIVE_JUNK_FILE_PATTERNS = (
    "*.pyc",
    "*.pyo",
    "*.tmp",
    "*.orig",
    "*.rej",
    "*.bak",
    "*.bak_*",
    "*~",
)

TEXT_EXTENSIONS = {
    ".py", ".html", ".css", ".js", ".json", ".md", ".txt", ".yml", ".yaml", ".toml", ".ini", ".sh", ".ps1"
}

FORBIDDEN_PACKAGE_PARTS = {
    ".git", ".venv", "venv", "env", "virtualenv", "__pycache__", "staticfiles", "media", "private_media",
    ".phase-backups", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"
}

SECRET_PATTERNS = (
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b")),
    ("OpenAI key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("Mapbox token", re.compile(r"\b(?:pk|sk)\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")),
    ("Telegram bot token", re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}\b")),
    ("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)


def run_git(project: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=project,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
    return result


def normalize_rel(path: Path, project: Path) -> str:
    return path.relative_to(project).as_posix()


def path_size(path: Path) -> int:
    if path.is_symlink():
        return 0
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file() and not item.is_symlink():
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return total


def format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


def matches_any(name: str, patterns: Iterable[str]) -> bool:
    lowered = name.lower()
    return any(fnmatch.fnmatch(lowered, pattern.lower()) for pattern in patterns)


def is_phase_workspace(name: str) -> bool:
    return bool(re.fullmatch(r"phase\d+(?:[_-].+)?", name, flags=re.IGNORECASE))


def tracked_set(project: Path) -> set[str]:
    raw = run_git(project, "ls-files", "-z").stdout
    return {item.replace("\\", "/") for item in raw.split("\0") if item}


def has_tracked_descendant(rel: str, tracked: set[str]) -> bool:
    prefix = rel.rstrip("/") + "/"
    return rel in tracked or any(item.startswith(prefix) for item in tracked)


def source_references_legacy_velzon(project: Path) -> list[str]:
    references: list[str] = []
    excluded_roots = {
        project / "static" / "velzon",
        project / "static" / "velzon_master",
        project / "staticfiles",
        project / ".git",
        project / ".venv",
        project / "media",
        project / "private_media",
    }
    needle_patterns = ("velzon/", "'velzon/", '"velzon/')
    for path in project.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(root == path or root in path.parents for root in excluded_roots):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(needle in text for needle in needle_patterns):
            references.append(normalize_rel(path, project))
    return sorted(set(references))


def collect_candidates(project: Path, tracked: set[str]) -> tuple[list[Path], dict[str, object]]:
    candidates: set[Path] = set()
    notes: dict[str, object] = {}

    for child in project.iterdir():
        rel = child.name
        if rel in PROTECTED_TOP_LEVEL:
            continue
        if child.is_dir() and (child.name in JUNK_TOP_LEVEL_DIRS or is_phase_workspace(child.name)):
            if not has_tracked_descendant(rel, tracked):
                candidates.add(child)
        elif child.is_file() and matches_any(child.name, ROOT_JUNK_PATTERNS):
            if rel not in tracked:
                candidates.add(child)

    for path in project.rglob("__pycache__"):
        if path.is_dir() and ".git" not in path.parts and ".venv" not in path.parts:
            rel = normalize_rel(path, project)
            if not has_tracked_descendant(rel, tracked):
                candidates.add(path)

    for path in project.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        rel = normalize_rel(path, project)
        if rel in tracked:
            continue
        if matches_any(path.name, RECURSIVE_JUNK_FILE_PATTERNS):
            candidates.add(path)

    legacy_velzon = project / "static" / "velzon"
    if legacy_velzon.exists():
        refs = source_references_legacy_velzon(project)
        notes["legacy_velzon_references"] = refs
        rel = normalize_rel(legacy_velzon, project)
        if not refs and not has_tracked_descendant(rel, tracked):
            candidates.add(legacy_velzon)
        else:
            notes["legacy_velzon_preserved"] = True

    # Avoid moving descendants when their parent is already selected.
    ordered = sorted(candidates, key=lambda p: (len(p.parts), str(p).lower()))
    compact: list[Path] = []
    for path in ordered:
        if any(parent == path or parent in path.parents for parent in compact):
            continue
        compact.append(path)
    return compact, notes


def move_to_quarantine(project: Path, candidates: list[Path], quarantine: Path) -> list[dict[str, object]]:
    moved: list[dict[str, object]] = []
    for source in candidates:
        if not source.exists():
            continue
        rel = source.relative_to(project)
        destination = quarantine / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        size = path_size(source)
        shutil.move(str(source), str(destination))
        moved.append({"path": rel.as_posix(), "bytes": size, "size": format_bytes(size)})
    return moved


def extract_static_references(project: Path) -> set[str]:
    refs: set[str] = set()
    static_tag = re.compile(r"\{\%\s*static\s+['\"]([^'\"]+)['\"]")
    quoted_static = re.compile(r"['\"]((?:velzon_master|velzon|fonts)/[^'\"]+)['\"]")
    roots = [project / "templates", project / "smartbase_admin_bridge", project / "config", project / "store", project / "website"]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in static_tag.finditer(text):
                value = match.group(1).replace("\\", "/").lstrip("/")
                if value.startswith(("velzon_master/", "velzon/", "fonts/")):
                    refs.add(value)
            for match in quoted_static.finditer(text):
                refs.add(match.group(1).replace("\\", "/").lstrip("/"))

    verifier = project / "scripts" / "verify_phase30_runtime_assets.py"
    if verifier.is_file():
        text = verifier.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"['\"]static/((?:velzon_master|velzon|fonts)/[^'\"]+)['\"]", text):
            refs.add(match.group(1).replace("\\", "/"))

    # IRANSans is a licensed private asset used by the public CSS.
    iransans = project / "static" / "fonts" / "iransans"
    if iransans.is_dir():
        for path in iransans.rglob("*"):
            if path.is_file():
                refs.add(path.relative_to(project / "static").as_posix())
    return refs


def css_dependencies(static_root: Path, initial: set[str]) -> set[str]:
    selected = set(initial)
    queue = list(initial)
    url_re = re.compile(r"url\((?:['\"])?([^)'\"]+)(?:['\"])?\)", re.IGNORECASE)
    while queue:
        rel = queue.pop()
        source = static_root / rel
        if not source.is_file() or source.suffix.lower() != ".css":
            continue
        try:
            text = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in url_re.finditer(text):
            value = match.group(1).strip()
            if not value or value.startswith(("data:", "http://", "https://", "#")):
                continue
            resolved = (source.parent / value.split("?", 1)[0].split("#", 1)[0]).resolve()
            try:
                dep_rel = resolved.relative_to(static_root.resolve()).as_posix()
            except ValueError:
                continue
            if dep_rel not in selected and resolved.is_file():
                selected.add(dep_rel)
                queue.append(dep_rel)
    return selected


def safe_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def scan_secrets(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"type": label, "path": path.relative_to(root).as_posix()})
    return findings


def build_host_package(project: Path, tracked: set[str], output_dir: Path, timestamp: str) -> dict[str, object]:
    stage = output_dir / f"host_package_stage_{timestamp}"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    copied_tracked = 0
    skipped_tracked: list[str] = []
    for rel in sorted(tracked):
        parts = Path(rel).parts
        if any(part in FORBIDDEN_PACKAGE_PARTS for part in parts):
            skipped_tracked.append(rel)
            continue
        if rel in {".env", "db.sqlite3"} or rel.lower().endswith((".pyc", ".pyo")):
            skipped_tracked.append(rel)
            continue
        source = project / rel
        if source.is_file():
            safe_copy(source, stage / rel)
            copied_tracked += 1

    private_refs = extract_static_references(project)
    private_refs = css_dependencies(project / "static", private_refs)
    copied_private: list[str] = []
    missing_private: list[str] = []
    for rel in sorted(private_refs):
        source = project / "static" / rel
        if source.is_file():
            safe_copy(source, stage / "static" / rel)
            copied_private.append(rel)
        else:
            missing_private.append(rel)

    instructions = f"""3DPrintHub Phase 30 - clean host upload package\n\nBuilt: {dt.datetime.now().isoformat(timespec='seconds')}\nGit branch: {run_git(project, 'branch', '--show-current').stdout.strip()}\nGit commit: {run_git(project, 'rev-parse', 'HEAD').stdout.strip()}\n\nIMPORTANT:\n- Do not overwrite the server .env file.\n- Do not overwrite the server database or media/private_media directories.\n- Extract this package into /home/sfkilvrs/3dprinthub\n- Keep PAYMENT_GATEWAY_ENABLED=0 until Sandbox callback testing succeeds.\n\nAfter upload:\ncd /home/sfkilvrs/3dprinthub\n/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/pip install -r requirements.txt\n/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python scripts/verify_phase30_runtime_assets.py\n/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python manage.py migrate --noinput\n/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python manage.py collectstatic --noinput\n/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python manage.py phase30_payment_audit\nmkdir -p tmp && touch tmp/restart.txt\n"""
    (stage / "HOST_UPLOAD_INSTRUCTIONS.txt").write_text(instructions, encoding="utf-8")

    if missing_private:
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError(
            "Required private runtime assets are missing; host package was not created: "
            + ", ".join(missing_private)
        )

    secret_findings = scan_secrets(stage)
    if secret_findings:
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError("Secret-like values detected in host package: " + json.dumps(secret_findings, ensure_ascii=False))

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"3DPrintHub_phase30_HOST_UPLOAD_CLEAN_{timestamp}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as archive:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(stage).as_posix())

    package_files = sum(1 for p in stage.rglob("*") if p.is_file())
    package_size = zip_path.stat().st_size
    shutil.rmtree(stage, ignore_errors=True)
    return {
        "zip_path": str(zip_path),
        "files": package_files,
        "bytes": package_size,
        "size": format_bytes(package_size),
        "tracked_files_copied": copied_tracked,
        "private_runtime_files_copied": len(copied_private),
        "private_runtime_files": copied_private,
        "missing_private_runtime_files": missing_private,
        "skipped_tracked_files": skipped_tracked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely clean 3DPrintHub local artifacts and build a host upload package.")
    parser.add_argument("--project", default=r"D:\projects\3DPrintHub")
    parser.add_argument("--apply", action="store_true", help="Move detected junk to a reversible quarantine outside the project.")
    parser.add_argument("--build-host-package", action="store_true")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    required = [project / "manage.py", project / "config" / "settings.py", project / ".git"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Not a valid 3DPrintHub Git checkout. Missing: " + ", ".join(missing))

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    tracked = tracked_set(project)
    candidates, notes = collect_candidates(project, tracked)
    candidate_rows = [
        {
            "path": normalize_rel(path, project),
            "bytes": path_size(path),
            "size": format_bytes(path_size(path)),
        }
        for path in candidates
    ]
    total_candidate_bytes = sum(int(row["bytes"]) for row in candidate_rows)

    project_parent = project.parent
    quarantine = project_parent / "_3DPrintHub_cleanup_quarantine" / timestamp
    report_dir = project_parent / "_3DPrintHub_cleanup_reports"
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else project_parent / "_3DPrintHub_host_releases"

    result: dict[str, object] = {
        "project": str(project),
        "timestamp": timestamp,
        "git_branch": run_git(project, "branch", "--show-current").stdout.strip(),
        "git_commit": run_git(project, "rev-parse", "HEAD").stdout.strip(),
        "tracked_files": len(tracked),
        "mode": "apply" if args.apply else "audit-only",
        "candidate_count": len(candidate_rows),
        "candidate_bytes": total_candidate_bytes,
        "candidate_size": format_bytes(total_candidate_bytes),
        "candidates": candidate_rows,
        "notes": notes,
        "protected": sorted(PROTECTED_TOP_LEVEL),
    }

    if args.apply:
        quarantine.mkdir(parents=True, exist_ok=True)
        moved = move_to_quarantine(project, candidates, quarantine)
        result["quarantine"] = str(quarantine)
        result["moved"] = moved
        result["moved_count"] = len(moved)
        result["moved_bytes"] = sum(int(row["bytes"]) for row in moved)
        result["moved_size"] = format_bytes(int(result["moved_bytes"]))
    else:
        result["quarantine"] = None
        result["moved"] = []

    if args.build_host_package:
        result["host_package"] = build_host_package(project, tracked, output_dir, timestamp)

    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"cleanup_report_{timestamp}.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("3DPRINTHUB_CLEANUP=OK")
    print(f"project: {project}")
    print(f"mode: {result['mode']}")
    print(f"cleanup_candidates: {len(candidate_rows)}")
    print(f"cleanup_candidate_size: {format_bytes(total_candidate_bytes)}")
    if args.apply:
        print(f"moved_to_quarantine: {result.get('moved_count', 0)}")
        print(f"quarantine: {quarantine}")
    if args.build_host_package:
        package = result["host_package"]
        assert isinstance(package, dict)
        print(f"host_package: {package['zip_path']}")
        print(f"host_package_files: {package['files']}")
        print(f"host_package_size: {package['size']}")
        if package["missing_private_runtime_files"]:
            print("WARNING: missing private runtime files:")
            for item in package["missing_private_runtime_files"]:
                print(f"  - {item}")
    print(f"report: {report_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - CLI must produce one actionable error.
        print(f"3DPRINTHUB_CLEANUP=FAILED\n{exc}", file=sys.stderr)
        raise SystemExit(1)
