# Phase49.3I.22 — Tk Main-Thread AI Bridge + Scrollable Product Rail

Updated: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Owner Evidence
Windows Product Workspace enters `(Not Responding)` after multiple AI buttons, including the 49.3I.21 link-grounded action. The right Product stages rail also clips lower controls on the owner's display and needs vertical scrolling.

## New Root Cause Found
The previous 210-second provider timeout was real, but it was not sufficient to explain the whole-window Windows freeze.

Multiple mature AI workers run network work on Python background threads and then call Tk APIs from those worker threads through patterns such as:

- `self.after(0, ...)`,
- progress callbacks that ultimately schedule Tk work,
- the 49.3I.21 worker calling `_source_for_ai()` even though that source builder can read Tk-backed variables.

Tk/Tcl owns one UI thread. Cross-thread Tcl marshalling can block/deadlock the worker and UI under Windows, especially with modal/progress windows. Therefore every Product AI button must use a single main-thread handoff contract.

## Implementation
### 1. Final Tk-thread bridge
`catalog_center/app/phase49_3i22_tk_thread_bridge.py`

- records the Product Workspace owning thread at construction,
- intercepts off-main `workspace.after(...)` calls without invoking Tcl,
- stores deferred UI callbacks in a Python-only heap,
- a 25 ms pump scheduled by the real Tk thread drains callbacks on the UI thread,
- supports cancellation tokens for deferred callbacks,
- snapshots `_source_for_ai()` on the main thread and gives workers deep-copied plain data,
- pre-snapshots 49.3I.21 link-grounded refresh before its worker starts,
- records bridge startup and callback failures in sanitized diagnostics.

The bridge is installed last in `phase49_3i_pricing_modes.py`, after 49.3I.18/19/20/21, so it protects existing AI actions instead of duplicating them.

### 2. Scrollable Product stages rail
`catalog_center/app/product_workspace_v87.py`

- the right rail is now hosted in a Canvas,
- a real vertical `ttk.Scrollbar` is always available,
- scrollregion follows later AI/readiness panels dynamically,
- mouse wheel scrolls the rail while the pointer is inside it,
- mature stage buttons and later appended panels retain the same rail parent contract.

## No Change
- no Django migration,
- no Catalog schema migration,
- no provider/model selection change,
- no Product DB reset,
- no pricing/publish/FTP/Bridge change,
- no Production deploy.

## Windows Acceptance
1. clean/ff-only pull the live feature branch,
2. compile the new bridge plus touched Product Workspace/composition modules,
3. run `test_phase49_3i22_tk_thread_bridge` and inherited 49.3I.21/20/19/18/17 tests,
4. run `launch.py --verify-only`,
5. open the same MakerWorld product and repeatedly execute the visible AI buttons,
6. confirm the window remains responsive while network requests run,
7. confirm progress/timeout/error UI continues updating,
8. confirm Stage rail has a visible vertical scrollbar and all lower controls are reachable,
9. if any AI action still fails, export/send the sanitized diagnostic JSON before closing Catalog Center.

## Diagnostics Paths
- explicit diagnostic bundle: `D:\projects\3DPrintHub\diagnostics\catalog-diagnostic-*.json`,
- persistent workflow logs: `D:\projects\3dprinthub-catalog-manager\logs\phase49_3f\YYYY-MM-DD\workflow-*.jsonl`.

Secrets/API keys must never be copied into diagnostics or chat.
