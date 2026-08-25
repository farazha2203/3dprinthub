# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.22 — Tk Main-Thread AI Bridge + Scrollable Product Rail`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → COMMIT/PUSH IF LOCAL CODE CHANGES → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. Windows acceptance of 49.3I.22 UI-thread safety across every Product AI button,
2. verify the right Product rail scrolls and exposes all readiness/AI controls,
3. regression acceptance of 49.3I.21 bounded diagnostics + link-grounded full refresh,
4. regression acceptance of 49.3I.20/19/18/17 and acquisition gates,
5. exactly one Local Publish E2E,
6. explicit owner approval,
7. verify Production branch/path/venv/MySQL/backup/rollback,
8. deploy approved GitHub snapshot and verify Production,
9. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition → Single Active AI Runtime → Operator Editing/Bulk Metadata → Canonical Source Identity → Visible Operator Panels → Observable Link-Grounded AI → Tk Main-Thread AI Bridge + Scrollable Rail`.

## 49.3I.22 — Tk Main-Thread AI Bridge + Scrollable Product Rail
Fresh owner evidence after 49.3I.21 showed a full Windows `(Not Responding)` state, not merely a slow provider response.

Repository inspection found mature AI workers calling Tk handoff paths from worker threads. 49.3I.22 therefore establishes one final UI-thread boundary:
- workers keep network/AI work off the Tk thread,
- off-main `workspace.after(...)` is queued without calling Tcl,
- a main-thread 25 ms pump executes UI callbacks,
- Tk-backed Product source state is snapshotted on the main thread,
- existing Task Center/image/all-fields/manual/source/link AI paths inherit the same protection,
- Product stages rail uses Canvas + vertical Scrollbar and dynamically includes later readiness/AI panels.

## Preserved 49.3I.21
- provider POST default max 75s with bounded override,
- request-start/success/error/timeout diagnostics,
- secret redaction,
- exact Product URL grounding,
- one-click link-based source fetch → AI → preview → explicit apply,
- Stop/Cancel prevents late apply.

## Preserved Earlier Contracts
- 49.3I.20 visible operator panels,
- 49.3I.19 canonical source identity,
- 49.3I.18 clipboard/bulk metadata/operator-authoritative Persian identity,
- 49.3I.17 exactly one saved Provider/Model/key path,
- 49.3I.16 resilient acquisition and Add-to-Products contracts.

## Database / Migration
Django migration: NONE.
Catalog schema migration: NONE.
Production untouched.

## Focused Windows Gate
1. clean worktree + live fetch/ff-only feature branch,
2. verify Local HEAD equals fetched Remote HEAD,
3. compile 49.3I.22 + Product Workspace + composition modules,
4. run 49.3I.22/21/20/19/18/17 focused tests,
5. run inherited acquisition regressions and `launch.py --verify-only`,
6. launch the same MakerWorld product,
7. execute all-fields AI, image AI, source+AI rebuild, manual-authoritative rebuild and link-grounded full refresh,
8. window must remain responsive while requests execute,
9. progress/error/timeout controls must continue updating,
10. vertical Product rail scrollbar must reach every lower control,
11. if any action fails, export `D:\projects\3DPrintHub\diagnostics\catalog-diagnostic-*.json` and latest persistent workflow JSONL before closing the app.

If PASS, proceed to exactly one Local Publish E2E and then owner-approved Production gate.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.
