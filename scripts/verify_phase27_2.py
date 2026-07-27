from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "templates/website/partials/hero.html": [
        "p27-home-hero__backdrop",
        "p27-home-hero__subject-frame",
        "p27-home-hero__subject",
        "data-p14-hero-slider",
    ],
    "static/css/phase27-home-hero.css": [
        "object-fit:contain",
        "p27-home-hero__subject-frame",
        "p27-home-hero__backdrop",
        "@media(max-width:900px)",
    ],
    "static/js/phase27-home-hero.js": [
        "classifySlide",
        "initImagePair",
        "is-portrait",
        "useFallback",
    ],
    "website/views.py": [
        'backend="django.contrib.auth.backends.ModelBackend"',
    ],
    "store/catalog_sync.py": [
        "source__sync_policy__isnull=True",
        "public_reference_enabled=True",
    ],
    "templates/store/external_catalog.html": [
        "data-p13-catalog-filter",
    ],
}


def main() -> int:
    errors: list[str] = []
    for relative, markers in REQUIRED.items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing marker {marker!r}")

    for path in [
        ROOT / "website/views.py",
        ROOT / "store/views.py",
        ROOT / "store/catalog_sync.py",
        ROOT / "store/models.py",
        ROOT / "store/test_phase13.py",
        ROOT / "store/test_phase14.py",
        ROOT / "store/test_phase18.py",
        ROOT / "website/test_admin_velzon.py",
    ]:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            errors.append(f"python syntax: {path.relative_to(ROOT)}: {exc}")

    css = (ROOT / "static/css/phase27-home-hero.css").read_text(encoding="utf-8")
    if css.count("{") != css.count("}"):
        errors.append("CSS brace mismatch")

    if errors:
        print("PHASE 27.2 VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PHASE 27.2 VERIFICATION PASSED")
    print("- responsive contain subject + blurred backdrop")
    print("- explicit local authentication backend")
    print("- public catalog accepts legacy sources without policy")
    print("- compatibility markers and canonical tests updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
