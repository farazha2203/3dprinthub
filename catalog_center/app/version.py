from __future__ import annotations

from pathlib import Path


APP_NAME = "3DPrintHub Catalog Center"
APP_VERSION = "8.9.9"
BUILD_ID = "2026.08.30.3"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"
SOURCE_ROOT = Path(__file__).resolve().parents[1]


def version_lines() -> tuple[str, ...]:
    return (
        f"APP_VERSION={APP_VERSION}",
        f"BUILD_ID={BUILD_ID}",
        f"SOURCE_ROOT={SOURCE_ROOT}",
        f"MAIN_FILE={SOURCE_ROOT / 'app' / 'main.py'}",
    )


if __name__ == "__main__":
    print("\n".join(version_lines()))
