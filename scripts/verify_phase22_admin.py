from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(relative: str) -> Path:
    path = ROOT / relative
    if not path.is_file():
        fail(f"Missing required file: {relative}")
    return path


base = require_file("templates/admin/base.html").read_text(encoding="utf-8")
sidebar = require_file("templates/admin/partials/sidebar.html").read_text(encoding="utf-8")
css = require_file("static/admin/master-django.css").read_text(encoding="utf-8")
js = require_file("static/admin/master-django.js").read_text(encoding="utf-8")

for forbidden in (
    "velzon_master/js/app.js",
    "velzon_master/js/plugins.js",
    "static/libs/",
    "static/lang/",
    "static/images/flags/",
):
    if forbidden in base:
        fail(f"Forbidden legacy asset reference is still loaded: {forbidden}")

required_static = (
    "static/velzon_master/libs/simplebar/dist/simplebar.min.js",
    "static/velzon_master/libs/bootstrap/dist/js/bootstrap.bundle.min.js",
    "static/velzon_master/libs/choices.js/public/assets/scripts/choices.min.js",
    "static/velzon_master/libs/flatpickr/dist/flatpickr.min.js",
    "static/velzon_master/libs/flatpickr/dist/flatpickr.min.css",
    "static/velzon_master/libs/flatpickr/dist/l10n/fa.js",
    "static/fonts/iransans/IRANSansWeb_FaNum.woff",
)
for relative in required_static:
    require_file(relative)

if sidebar.count('id="scrollbar"') != 1:
    fail("Sidebar must contain exactly one #scrollbar container.")
if 'id="navbar-nav"' not in sidebar:
    fail("Sidebar navigation root #navbar-nav is missing.")
if "new window.SimpleBar(box" not in js:
    fail("Controlled SimpleBar initialization is missing.")
if "new window.SimpleBar(nav" in js or "new SimpleBar(nav" in js:
    fail("Nested SimpleBar initialization on #navbar-nav is forbidden.")

for marker in (
    ".app-menu.navbar-menu{position:fixed!important",
    "#scrollbar{flex:1 1 0!important",
    '.nav-link.menu-link[aria-expanded="true"]',
    ".menu-dropdown .nav-link.active",
):
    if marker not in css:
        fail(f"Required admin navigation CSS marker is missing: {marker}")

static_pattern = re.compile(r"\{%\s*static\s+['\"]([^'\"]+)['\"]\s*%\}")
for template in (ROOT / "templates" / "admin").rglob("*.html"):
    text = template.read_text(encoding="utf-8", errors="ignore")
    for match in static_pattern.finditer(text):
        relative = match.group(1)
        if relative.startswith(("admin/css/", "admin/img/")):
            continue
        if not (ROOT / "static" / relative).is_file():
            fail(f"Missing static reference {relative} in {template.relative_to(ROOT)}")

for script in ("APPLY_PHASE22.ps1", "PUBLISH_PHASE22_GITHUB.ps1"):
    data = require_file(script).read_bytes()
    if any(byte >= 128 for byte in data):
        fail(f"PowerShell script must stay ASCII to avoid Windows encoding failures: {script}")

print("Phase 22 admin/auth static verification passed.")
