# Phase50.A2S — Qt Post-tab visual parity

Status: `IMPLEMENTED / FOCUSED_TESTED / RUNTIME-RELAUNCH BLOCKED`
Date: 2026-09-28

## Requested Delta

Make the already-committed, deterministic Post-composer contract visible in the
actual Qt6 Catalog Center runtime.  The earlier implementation lived only in
the retained Tk compatibility surface (`catalog_center/app/main.py`), while
the production desktop launcher starts `catalog_center/qt_launch.py`.

## Touched Surfaces

- Qt Product Wizard, stage 4 (`محتوا و SEO`)
- Existing deterministic `app.post_composer` helper
- Focused Qt Post-tab structural regression

## Must Not Touch

- No provider request, OpenRouter network call, Publish, Buffer, Instagram,
  Site, Host, database migration, or Production operation.
- Existing owner-dirty A2R documentation is preserved and not reconciled by
  this phase.

## Finite Checklist

- [x] 1. Verify the actual launcher/runtime and identify the Tk/Qt mismatch.
- [x] 2. Add the Post tab to the active Qt stage-4 surface.
- [x] 3. Bind twelve styles, metadata fields, local mock and revision history.
- [x] 4. Add a Qt structural smoke regression.
- [ ] 5. Run focused tests, Qt verify-only, compile and diff check.
- [ ] 6. Perform foreground visual QA through available Computer Use.
- [ ] 7. Document evidence and prepare a clean commit scope.

## Exact Restart Point

The code and focused tests are ready.  Close the already-running Catalog Center
only after any unsaved operator work has been saved, then launch the current
checkout through `catalog_center/RUN_QT.ps1`.  Run `RUN_QT.ps1 -VerifyOnly`
only after that close/relaunch boundary: its kernel schema guard correctly
refuses the currently open/readonly SQLite database.  Foreground QA is valid
only when Computer Use exposes the native Catalog Center window; a
launcher/process probe is not a substitute for visual acceptance.

## Evidence — 2026-09-28

- Actual runtime verified: `RUN_QT.ps1` starts `qt_launch.py`, not the retained
  Tk `app/main.py` surface where the initial Post implementation existed.
- Qt Post surface now provides 12 style radios, editable caption/link/mention
  controls, the deterministic local Mock action, and persistence through
  `content_pack_json` plus a separate `post_revision` history event.
- Focused regression: `catalog_center.tests.test_post_composer` and
  `catalog_center.tests.test_qt_post_tab` — 4/4 PASS.
- Syntax parse without bytecode writes: PASS. `git diff --check`: PASS.
- The normal `compileall` and Qt verify-only attempted while the old GUI process
  was open and failed to write their cache/schema state. This is a runtime lock
  gate, not a source failure; it must not be bypassed by killing the GUI or
  forcing SQLite writes.
