"""Static verification for the phase-20 Velzon admin integration."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "templates/admin/base.html",
    "templates/admin/partials/sidebar.html",
    "static/admin/velzon-admin.css",
    "static/admin/velzon-admin.js",
    "static/velzon/libs/choices.js/public/assets/scripts/choices.min.js",
    "static/velzon/libs/choices.js/public/assets/styles/choices.min.css",
    "static/velzon/libs/flatpickr/dist/flatpickr.min.js",
    "static/velzon/libs/flatpickr/dist/flatpickr.min.css",
    "static/velzon/libs/flatpickr/dist/l10n/fa.js",
)


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("Missing phase-20 files:\n- " + "\n- ".join(missing))

    base = (ROOT / "templates/admin/base.html").read_text(encoding="utf-8")
    sidebar = (ROOT / "templates/admin/partials/sidebar.html").read_text(encoding="utf-8")

    forbidden = (
        "velzon/js/app.js",
        "velzon/js/plugins.js",
        "/static/libs/choices.js",
        "/static/libs/flatpickr",
    )
    found = [token for token in forbidden if token in base]
    if found:
        raise SystemExit("Forbidden legacy references remain: " + ", ".join(found))

    ids = re.findall(r'\bid="([^"]+)"', sidebar)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise SystemExit("Duplicate sidebar IDs: " + ", ".join(duplicates))

    required_nodes = ("scrollbar", "two-column-menu", "navbar-nav")
    absent_nodes = [node for node in required_nodes if f'id="{node}"' not in sidebar]
    if absent_nodes:
        raise SystemExit("Missing required sidebar nodes: " + ", ".join(absent_nodes))

    print("Phase-20 admin static verification passed.")


if __name__ == "__main__":
    main()
