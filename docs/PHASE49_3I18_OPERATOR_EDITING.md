# Phase 49.3I.18 — Operator Editing, Bulk Image Metadata, Authoritative AI Rebuild

Status: implementation branch ready for Windows local gate.

Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`

## Additive scope only

This phase does not remove or replace the mature gallery, source acquisition, pricing, publishing, AI provider/model, or Phase 49.3I.13 URL paste recovery behavior.

### 1. Global clipboard/edit shortcuts

All editable Tk/Ttk text controls receive reliable Windows-style shortcuts:

- Ctrl+C — copy
- Ctrl+V — paste
- Ctrl+X — cut
- Ctrl+A — select all
- Shift+Insert — paste
- Ctrl+Insert — copy

A physical Windows keycode fallback is also installed so the shortcuts remain usable while the active keyboard layout is Persian. Disabled/readonly controls remain protected from cut/paste.

### 2. Bulk image operation panel

The Images section gets an additive bulk-operation panel for all selected site images. The operator can set:

- SEO filename prefix with automatic `-01`, `-02`, ... numbering
- per-image Title template
- per-image Alt template
- optional Caption template

Supported template tokens: `{title}`, `{n}`, `{n2}`, `{total}`.

The operation writes through the existing `image_metadata_json` / `image_alt_texts_json` contract and marks the changed metadata as operator overrides. The existing image finalizer remains the only component that writes final SEO image files.

### 3. Operator-authoritative Persian product name

The Content/SEO section gets a field named `نام فارسی صحیح و تأییدشده اپراتور` and two explicit actions:

- `جایگزینی نام در همه متن‌ها`: replaces the old/generated title in editable Persian content, SEO, lists, slider text and textual image metadata. Raw source URL/creator/source facts are not rewritten.
- `بازسازی کامل متن + SEO با AI`: explicitly regenerates Persian content, SEO, image Alt text and enabled slider copy using the operator-entered Persian name as the authoritative product identity.

For an explicit rebuild, the raw crawled source title is retained only as secondary reference text. It cannot override the operator-confirmed product identity. Price, inventory, source URL, and manual material/color selections are not overwritten.

Example acceptance case: a MakerWorld Cake Stand product can be corrected to the authoritative Persian title `استند کیک`; the rebuild must not keep or re-introduce a previous guessed object name into generated SEO/content.

## No schema/migration changes

This phase adds no database columns and no migration. It uses existing editable product fields and existing image metadata JSON structures.

## Local Windows gate

From repository root:

```powershell
$Repo = "D:\projects\3DPrintHub"
$Branch = "agent/phase49-3i18-operator-bulk-ai-rebuild"
Set-Location $Repo
git fetch --prune origin
git switch $Branch
git pull --ff-only origin $Branch

$Python = ".\.venv\Scripts\python.exe"
& $Python -m py_compile catalog_center\app\phase49_3i18_operator_editing.py catalog_center\app\phase49_3i_pricing_modes.py
Push-Location catalog_center
& "..\.venv\Scripts\python.exe" -m unittest tests.test_phase49_3i18_operator_editing -v
& "..\.venv\Scripts\python.exe" launch.py --verify-only
Pop-Location

git status --short --branch
```

## Manual acceptance gate

1. Open the application and verify Ctrl+C/Ctrl+V/Ctrl+X/Ctrl+A in main-app Entry/Text controls before opening a product.
2. Open a product and verify the same shortcuts in product fields and image metadata editor fields.
3. Select multiple site images, use `cake-stand` as filename prefix, apply bulk operation and verify `cake-stand-01.webp`, `cake-stand-02.webp`, ... metadata plus numbered Alt/Title values.
4. Enter `استند کیک` as authoritative Persian name and run `جایگزینی نام در همه متن‌ها`; confirm raw source URL/creator/license are unchanged.
5. Run `بازسازی کامل متن + SEO با AI`; confirm the rebuilt H1/SEO/descriptions/image Alt/active slider text describe `استند کیک` consistently and do not reintroduce the previous wrong object name.
6. Confirm pricing, inventory, selected material/color, source URL and publish controls retain their previous values.
