# Phase49.3B — Windows Launch Import + SQLite Handle Hotfix

Date: 2026-08-19
Branch: `epic/phase49-unified-product-slider-sync`

## Trigger

Windows Local QA after applying the additive migrations:

- `store.0032_phase49_slider_media_profile` ✅
- `website.0022_phase49_hero_media_presentation` ✅
- targeted Django suite: 45/45 ✅
- full Django suite: 406 tests, 2 skipped ✅
- Epic49 discovery suite: 48/48 ✅

Two Windows-only/local integration defects were then observed:

1. `python launch.py --verify-only` failed while importing `phase49_3b_ai_product_runtime.py` because it imported a nonexistent module-level symbol named `sync_seo_reference_lists` from `phase49_readiness_wizard.py`.
2. `tests.test_phase49_unified_desktop` left a temporary SQLite connection open. Windows therefore could not delete `catalog.sqlite3` when `TemporaryDirectory` cleaned up and raised `WinError 32`.

## Root cause

### AI runtime import

Phase49.3A installs `_phase49_sync_reference_lists` dynamically on the workspace class inside `install(workspace_class)`. It never exported a module-level `sync_seo_reference_lists` function.

Phase49.3B incorrectly imported that nonexistent symbol during launcher startup. Because `launch.py` imports the runtime before entering verify mode, the entire launcher/verification gate was blocked.

### Windows temporary SQLite

The unified desktop schema test created an SQLite connection in a temporary directory but did not explicitly close it before the directory context exited. POSIX platforms may allow unlinking an open file; Windows does not.

## Fix

### `catalog_center/app/phase49_3b_ai_product_runtime.py`

- removed the invalid `sync_seo_reference_lists` import.
- added `_sync_reference_lists(workspace)`.
- the helper resolves the installed workspace hook with `getattr(workspace, "_phase49_sync_reference_lists", None)`.
- the hook is called with `update_widgets=True` when available.
- failure of this convenience synchronization remains non-fatal and does not block the AI workflow.

### `catalog_center/tests/test_phase49_3b_ai_diagnostics.py`

Added an import regression test so CI/local tests now import `app.phase49_3b_ai_product_runtime` directly and verify its installer/sync helper are callable.

### `catalog_center/tests/test_phase49_unified_desktop.py`

- `_DB.close()` added.
- temporary SQLite connection is closed in `finally` before `TemporaryDirectory` cleanup.
- keeps the test platform-correct on Windows.

## Data safety

No model or migration changes.
No DB reset/backfill/delete.
No change to API keys, `.env`, media, private media, or persistent Catalog Center databases.
Production untouched.

## Required re-validation on Windows

After pulling the hotfix:

```powershell
cd "D:\projects\3DPrintHub\catalog_center"
python -m unittest -v tests.test_phase49_unified_desktop
python -m unittest -v tests.test_phase49_3b_ai_diagnostics
python -m unittest -v tests.test_phase49_3b_guided_wizard
python launch.py --verify-only
```

Expected:

- all three unittest commands `OK`.
- no `WinError 32`.
- no `ImportError: sync_seo_reference_lists`.
- launcher prints all Phase49.3B markers and `ACTIVE_RELEASE_VERIFIED=OK`.

Only after that should normal `python launch.py` and visual Product Workspace QA continue.
Production remains disabled until explicit Local approval.
