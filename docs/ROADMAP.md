# PROJECT ROADMAP

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.4 — Explorer Product Gallery + Source URL Routing`

> Historical phase detail remains available in Git history and the phase documents. This roadmap is the operational forward path and acceptance gate for the active Epic.

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Phase49 Progress
### Completed and preserved foundations
- Phase49 unified product import/publish and slider synchronization.
- Persian sales/product workspace.
- dual Product / Portfolio publish targets.
- material/color handling.
- readiness wizard and local publish preflight.
- AI provider/runtime recovery.
- image pipeline, local image ownership and image SEO metadata.
- Phase49.3D workspace hardening and semantic image signatures.
- Phase49.3E AI task center and operator image controls.
- Phase49.3F provider/runtime/provenance/dynamic pricing foundations.
- Phase49.3G workspace usability, commerce provenance and manual-override guard.
- Phase49.3H SEO execution console, result/error drawer, AI cost ledger and image limit default 10 / hard max 20.

### Phase49.3I core — implemented and previously CI-validated
- explicit operator Search/Listing URL is authoritative.
- Preview Candidate before Full Fetch.
- approved-only Full Fetch.
- archive/not-needed identity block/dedupe.
- scraped source text safety.
- lightweight Products gallery.
- Product Workspace remains canonical detailed editor.
- Fixed / Range / Formula pricing modes.
- AI progress first paint before synchronous preflight.
- Windows PowerShell 5.1 ASCII-only runner contract.
- live fetched GitHub snapshot handoff; no stale Chat-pinned SHA.

## Phase49.3I.4 — Explorer Product Gallery + Source URL Routing
Status: `GITHUB IMPLEMENTED / FINAL CI PENDING / WINDOWS QA PENDING`

### Scope
1. Fix clipped/thin product thumbnail regression (`ERR-49-020`).
2. Keep image/name/Edit Product as the only product-card content.
3. Add Explorer-style view switching:
   - Extra Large Icons,
   - Large Icons,
   - Medium Icons,
   - Small Icons,
   - List.
4. Persist view preference in existing local Catalog settings.
5. Add normal/Ctrl/Shift product selection.
6. Add Select All / Clear Selection and selected count.
7. Add right-click context menu.
8. Right-click Remove From Publish Queue must use safe local queue semantics only.
9. Fix Product URL versus Group/Category/Search URL classification (`ERR-49-021`) by using the configured source `model_url_pattern` as the authoritative product identity boundary.
10. Preserve Preview-first acquisition for non-product URLs.

### Must-Not-Touch
- Product Workspace detailed editor.
- Phase49.3H AI progress/result/error/cost behavior.
- image default 10 / hard max 20.
- Preview → Approve → Full Fetch state machine.
- archive/blocked dedupe.
- Fixed / Range / Formula independence.
- product revision/idempotency.
- slider revision/idempotency.
- production DB/media/source.
- historical local media.
- secrets.
- 49.3I.3 live Git snapshot guard.

### Automated Gate
Before Windows handoff all must pass:
- Phase49.3I dedicated CI.
- Phase49.3H regression CI.
- Phase49.3G regression CI.
- Full Phase49 + Full Django CI.
- PowerShell runner v49.3I.4 ASCII-only contract.
- `makemigrations --check --dry-run` = no changes.
- no destructive schema operations.

### Windows Manual QA Gate
After GitHub CI success:
1. clean worktree.
2. fetch/prune.
3. `pull --ff-only` current Epic.
4. run repository-owned `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`.
5. verify `PHASE49_3I_GIT_SNAPSHOT=OK` and runner `49.3I.4`.
6. Products thumbnails must occupy the full image area; no thin strip.
7. switch all five Explorer view modes.
8. Ctrl-click and Shift-click selection.
9. right-click selected products.
10. Remove From Publish Queue must not delete product data and must not touch Production.
11. normal image click opens large local preview.
12. Edit Product opens canonical Product Workspace.
13. real source Product URL routes direct.
14. real source Group/Category/Search URL routes Preview first.
15. approve only selected candidate for Full Fetch.
16. image limit <=20.
17. AI first-paint/progress regression QA.
18. Fixed / Range / Formula pricing regression QA.

### Local Publish Gate
Only after Explorer + routing visual/data QA passes:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- no Production endpoint.

### Production Gate
Production remains blocked until:
- automated CI success,
- Windows local gate success,
- manual visual/data QA success,
- LOCAL PUBLISH E2E success,
- explicit owner acceptance,
- verified production DB/vendor/path/branch/commit,
- backup + rollback readiness.

## Immediate Next Step
Run final CI validation for 49.3I.4. If successful, close the CI-only probe without merge, sync final docs, then issue the live-snapshot Windows pull/local-gate instructions. No Production commands before that.
