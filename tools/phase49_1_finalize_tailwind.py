from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
BUNDLE = ROOT / "static" / "css" / "tailwind-production.css"
CDN = '<script src="https://cdn.tailwindcss.com"></script>'
LOCAL = '<link rel="stylesheet" href="{% static \'css/tailwind-production.css\' %}">'


def main() -> int:
    if not BUNDLE.is_file() or BUNDLE.stat().st_size < 20_000:
        raise RuntimeError(f"Production Tailwind bundle is missing or too small: {BUNDLE}")

    candidates: list[tuple[Path, str]] = []
    for path in sorted(TEMPLATES.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if CDN not in text:
            continue
        if "{% load static" not in text:
            raise RuntimeError(f"Template uses Tailwind CDN without loading Django static tag: {path}")
        candidates.append((path, text))

    for path, text in candidates:
        path.write_text(text.replace(CDN, LOCAL), encoding="utf-8", newline="\n")

    remaining = []
    for path in sorted(TEMPLATES.rglob("*.html")):
        if "cdn.tailwindcss.com" in path.read_text(encoding="utf-8"):
            remaining.append(path)
    if remaining:
        raise RuntimeError("Tailwind CDN remains in: " + ", ".join(str(path) for path in remaining))

    print(f"TAILWIND_BUNDLE={BUNDLE}")
    print(f"TAILWIND_BUNDLE_SIZE={BUNDLE.stat().st_size}")
    print(f"TAILWIND_TEMPLATES_REPLACED={len(candidates)}")
    for path, _text in candidates:
        print(f"TAILWIND_TEMPLATE={path.relative_to(ROOT).as_posix()}")
    print("PHASE49_1_TAILWIND_FINALIZE=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
