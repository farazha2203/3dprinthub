from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.version import APP_NAME, APP_VERSION, BUILD_ID


PRODUCT_BASENAME = "3DPrintHub-CatalogCenter"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024, ), b""):
            digest.update(chunk)
    return digest.hexdigest()


def numeric_version(version: str) -> tuple[int, int, int, int]:
    parts = []
    for token in str(version).split("."):
        try:
            parts.append(int(token))
        except ValueError:
            break
    parts = (parts + [0, 0, 0, 0])[:4]
    return tuple(parts)  # type: ignore[return-value]


def version_resource(path: Path) -> None:
    a, b, c, d = numeric_version(APP_VERSION)
    content = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({a}, {b}, {c}, {d}),
    prodvers=({a}, {b}, {c}, {d}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [
          StringStruct(u'CompanyName', u'3DPrintHub'),
          StringStruct(u'FileDescription', u'{APP_NAME} Portable'),
          StringStruct(u'FileVersion', u'{APP_VERSION}'),
          StringStruct(u'InternalName', u'{PRODUCT_BASENAME}'),
          StringStruct(u'LegalCopyright', u'3DPrintHub'),
          StringStruct(u'OriginalFilename', u'{PRODUCT_BASENAME}.exe'),
          StringStruct(u'ProductName', u'{APP_NAME}'),
          StringStruct(u'ProductVersion', u'{APP_VERSION}'),
          StringStruct(u'Comments', u'Build {BUILD_ID}')
        ]
      )
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    path.write_text(content, encoding="utf-8")


def make_icon(source: Path, target: Path) -> None:
    from PIL import Image

    image = Image.open(source).convert("RGBA")
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT.parent,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def _copy_with_locked_fallback(source: Path, preferred: Path, *, suffix: str) -> tuple[Path, bool]:
    try:
        shutil.copy2(source, preferred)
        return preferred, True
    except PermissionError:
        fallback = preferred.with_name(f"{preferred.stem}-{suffix}{preferred.suffix}")
        shutil.copy2(source, fallback)
        return fallback, False


def build(python: Path) -> Path:
    release_dir = ROOT / "release" / APP_VERSION
    build_dir = ROOT / "build" / "portable-exe"
    staging_dir = build_dir / "dist"
    release_dir.mkdir(parents=True, exist_ok=True)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    icon = build_dir / "brand_icon.ico"
    version_file = build_dir / "version_info.txt"
    make_icon(ROOT / "assets" / "brand_icon.png", icon)
    version_resource(version_file)

    versioned_name = f"{PRODUCT_BASENAME}-v{APP_VERSION}"
    cmd = [
        str(python), "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--noupx",
        "--name", versioned_name,
        "--distpath", str(staging_dir),
        "--workpath", str(build_dir / "work"),
        "--specpath", str(build_dir),
        "--paths", str(ROOT),
        "--add-data", f"{ROOT / 'assets'}{os.pathsep}assets",
        "--add-data", f"{ROOT / 'config.example.json'}{os.pathsep}.",
        "--add-data", f"{ROOT / '.env.example'}{os.pathsep}.",
        "--add-data", f"{ROOT / 'skills'}{os.pathsep}skills",
        "--hidden-import", "keyring.backends.Windows",
        "--collect-all", "playwright",
        "--icon", str(icon),
        "--version-file", str(version_file),
        str(ROOT / "portable_entry.py"),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)

    staged_exe = staging_dir / f"{versioned_name}.exe"
    if not staged_exe.is_file() or staged_exe.stat().st_size < 1_000_000:
        raise RuntimeError(f"Portable EXE was not created correctly: {staged_exe}")

    # Verify the exact staged binary before touching the release folder.
    with tempfile.TemporaryDirectory() as temporary:
        verify_file = Path(temporary) / "verify.json"
        env = os.environ.copy()
        env["CATALOG_VERIFY_OUTPUT"] = str(verify_file)
        result = subprocess.run(
            [str(staged_exe), "--portable-verify"],
            cwd=staging_dir,
            env=env,
            timeout=90,
            check=False,
        )
        if result.returncode != 0 or not verify_file.is_file():
            raise RuntimeError(f"Portable EXE verification failed with exit code {result.returncode}")
        verify = json.loads(verify_file.read_text(encoding="utf-8"))
        if verify.get("ok") is not True:
            raise RuntimeError(f"Portable EXE verification payload failed: {verify}")

    build_suffix = "build-" + "".join(ch for ch in BUILD_ID if ch.isalnum())
    preferred_versioned = release_dir / f"{versioned_name}.exe"
    versioned_exe, versioned_preferred = _copy_with_locked_fallback(
        staged_exe, preferred_versioned, suffix=build_suffix
    )

    stable_exe = release_dir / f"{PRODUCT_BASENAME}.exe"
    stable_updated = True
    try:
        shutil.copy2(staged_exe, stable_exe)
    except PermissionError:
        stable_updated = False

    versioned_sha = sha256(versioned_exe)
    staged_sha = sha256(staged_exe)
    if versioned_sha != staged_sha:
        raise RuntimeError("Released and verified EXE hashes differ")
    if stable_updated and sha256(stable_exe) != versioned_sha:
        raise RuntimeError("Versioned and stable EXE hashes differ")

    manifest = {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "build_id": BUILD_ID,
        "git_sha": git_sha(),
        "portable": True,
        "single_file": True,
        "installer_required": False,
        "python_required_on_target": False,
        "data_profile": r"%LOCALAPPDATA%\3DPrintHub\CatalogCenter",
        "profile_persists_across_releases": True,
        "connection_secrets": "Windows Credential Store",
        "versioned_exe": versioned_exe.name,
        "preferred_versioned_name_available": versioned_preferred,
        "stable_exe": stable_exe.name,
        "stable_exe_updated": stable_updated,
        "sha256": versioned_sha,
        "size_bytes": versioned_exe.stat().st_size,
    }
    (release_dir / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (release_dir / f"{versioned_exe.name}.sha256").write_text(
        f"{versioned_sha}  {versioned_exe.name}\n", encoding="ascii"
    )

    print(f"PORTABLE_EXE={versioned_exe}")
    print(f"PORTABLE_EXE_LATEST={stable_exe}")
    print(f"PORTABLE_EXE_SHA256={versioned_sha}")
    print(f"PORTABLE_EXE_SIZE={versioned_exe.stat().st_size}")
    print(f"PORTABLE_VERSIONED_PREFERRED={int(versioned_preferred)}")
    print(f"PORTABLE_STABLE_ALIAS_UPDATED={int(stable_updated)}")
    print(r"PORTABLE_DATA_PROFILE=%LOCALAPPDATA%\3DPrintHub\CatalogCenter")
    print("PORTABLE_SECRET_STORE=WINDOWS_CREDENTIAL_MANAGER")
    print("PORTABLE_EXE_VERIFY=OK")
    return versioned_exe


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    python = Path(args.python).resolve()
    if not python.is_file():
        raise SystemExit(f"Python not found: {python}")
    build(python)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
