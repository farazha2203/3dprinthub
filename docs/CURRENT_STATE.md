# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.22 — Tk Main-Thread AI Bridge + Scrollable Product Rail`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.18 operator editing, 49.3I.19 canonical source identity, 49.3I.20 visible operator panels and 49.3I.21 bounded/link-grounded AI are present on the feature branch.

Fresh Windows evidence shows Product Workspace itself enters `(Not Responding)` after multiple AI actions. The visible Stage-4 controls are now present, but the right stages rail clips lower panels on the owner display.

Repository inspection found a second root cause beyond the earlier 210-second provider timeout: several mature AI workers call Tk/Tcl from Python worker threads through `self.after(...)`, progress callbacks, and in 49.3I.21 an off-thread `_source_for_ai()` read. Tk owns one UI thread; cross-thread Tcl marshalling can block the whole Windows window. 49.3I.22 installs a final main-thread handoff contract for all existing Product AI actions and makes the right rail truly scrollable.

## 49.3I.22 Implemented
- `phase49_3i22_tk_thread_bridge.py` records the Product Workspace owning thread.
- off-main `workspace.after(...)` never calls Tk/Tcl; it enqueues a plain Python callback.
- a 25 ms pump scheduled on the real Tk thread drains queued callbacks on the main thread.
- deferred `after_cancel` tokens are supported.
- `_source_for_ai()` is snapshotted on the main thread and workers receive a deep-copied plain dict.
- 49.3I.21 link-grounded refresh pre-captures the source snapshot before its worker starts.
- the bridge is installed after 49.3I.18/19/20/21 so existing AI buttons are protected without duplicate business logic.
- `product_workspace_v87.py` now hosts the right Product stages rail in a Canvas with a real vertical Scrollbar and pointer-aware mouse-wheel scrolling.
- later readiness/AI panels appended to the rail automatically expand its scrollregion.

## Relevant Root-Cause Evidence
- the old 210-second HTTP ceiling was real and remains bounded by 49.3I.21,
- `phase49_3e_ai_task_center.py` and `phase49_3f_workspace.py` use worker threads followed by `self.after(0, ...)`,
- 49.3I.18/19 rebuild workers also use the same callback pattern,
- 49.3I.21 additionally called `_source_for_ai()` inside its worker,
- therefore provider timeout alone could not guarantee UI responsiveness.

## Diagnostics
Sanitized diagnostic bundle:
`D:\projects\3DPrintHub\diagnostics\catalog-diagnostic-*.json`

Persistent workflow logs:
`D:\projects\3dprinthub-catalog-manager\logs\phase49_3f\YYYY-MM-DD\workflow-*.jsonl`

Secrets/API keys must not be copied into logs or chat.

## Database / Migration / Production Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no reset/drop/truncate
- no media/history deletion
- no Provider/Model identity change
- no pricing/publish/FTP/Bridge behavior change
- no Production deploy

## Files Added / Updated for 49.3I.22
- added `catalog_center/app/phase49_3i22_tk_thread_bridge.py`
- updated `catalog_center/app/phase49_3i_pricing_modes.py`
- updated `catalog_center/app/product_workspace_v87.py`
- added `catalog_center/tests/test_phase49_3i22_tk_thread_bridge.py`
- added `docs/phases/PHASE49_3I22_TK_THREAD_AND_SCROLL_RAIL.md`
- project documentation updated for the new root cause and Windows gate.

## Test Status
Focused regression test code is committed, but canonical Windows Local execution has not yet been reported. 49.3I.22 is therefore not marked Local Tested or Accepted.

## Exact Next Task — Windows 49.3I.22 Gate
1. close Catalog Center,
2. verify clean worktree at `D:\projects\3DPrintHub`,
3. fetch/prune and ff-only pull the live feature branch,
4. verify Local HEAD equals fetched Remote HEAD,
5. compile 49.3I.22 plus touched Product Workspace/composition modules,
6. run 49.3I.22 and inherited 49.3I.21/20/19/18/17 focused tests,
7. run `catalog_center\launch.py --verify-only`,
8. launch the same Product Workspace and repeatedly test `تکمیل هوشمند همه فیلدها`, image AI, source+AI rebuild and link-grounded full refresh,
9. verify the window remains responsive and progress/timeout/errors continue to update,
10. verify the right rail scrollbar reaches every lower Product/AI/readiness control,
11. if any action still fails, export the diagnostic JSON and collect the latest workflow JSONL before closing the app.

## Release Gate
Windows PASS → exactly one Local Publish E2E → explicit owner approval → Production read-only verification/backup/rollback → deploy only approved GitHub snapshot → Production verification.

## What Remains
- canonical Windows automated + visual gate,
- diagnostic review if any AI path still fails,
- Local Publish E2E,
- owner acceptance,
- only then Production.
