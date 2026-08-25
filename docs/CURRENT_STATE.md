# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.26 — Unified Exact-Link Completion + Canonical Wizard + Vertical Gallery + Product Archive`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Owner Evidence Driving 49.3I.26
Windows visual QA after 49.3I.25 showed:
- the Content/SEO-first experiment caused a startup lock dialog and still forced Basic Info prerequisites, so the original 1..7 stage order is preferred,
- the older 49.3G horizontal-gallery callback ran after 49.3I.25 and overwrote the intended five-column vertical image layout,
- exact-link completion filled Product content but Image SEO/Metadata still required a second AI action,
- the image finalizer could enter network download work; the 2026-08-25 diagnostic captured an 8.110s UI-hang sample with a worker blocked in SSL/HTTP under `phase49_3c_image_pipeline._download_if_needed -> finalize_selected_images`,
- operator needs percentage/current-stage visibility and a two-minute AI ceiling,
- Product cards need bulk selection/archive/delete-block actions while blocked source identity must continue preventing re-import,
- new acquisition should default to five source images and retain a full-page source screenshot as an extra local gallery item.

The uploaded diagnostic also contains older retained sessions with hidden `/models` 401s and AvalAI cost-lookup 429s. Historical logs are intentionally preserved, so timestamps/session IDs must be used before attributing an old event to the current build.

## 49.3I.26 Implemented on GitHub
- Canonical Product stage order restored: Basic Info → Commerce → Images → Content/SEO → Source/License → Slider → Review/Publish.
- All stage buttons remain directly navigable even while readiness is incomplete; readiness still blocks publish, not operator navigation.
- Product opens on Basic Info; the startup Content-first lock popup is removed at the final composition boundary.
- Exact-link completion uses a determinate 0–100% progress bar with explicit stages: queued, source fetch, source ready, AI request, received, preview, apply, image metadata, complete.
- AI request ceiling is 120 seconds for this operator workflow.
- If AI times out, the source URL is rechecked separately and the dialog reports whether source retrieval is healthy versus provider response failure.
- AI receives textual Product/source facts only; selected image URLs/files are not sent to AI.
- Exact-link completion fills Persian Product content/SEO and generates image filename/Alt/Title/Caption/Keywords from the same Product result in one workflow.
- Image physical SEO finalization is attempted only when every selected source image already exists locally. The unified AI path does not start network image downloads merely to finalize metadata.
- Existing 49.3C image metadata/manifest contract remains authoritative for true `metadata_ready` state.
- Final Workspace composition overrides the older 49.3G horizontal gallery: five image cards per row, vertical Canvas scrolling, no horizontal gallery navigation as the primary interaction.
- Product Workspace header receives a maximize/full-screen toggle.
- Products gallery receives per-card selection plus select-all-visible, clear-selection, bulk archive and bulk delete/block controls.
- Archive is non-destructive local Catalog state (`workflow_status=archived`); it does not unpublish a live site Product automatically.
- Delete/block uses the existing `block_product` identity-preserving contract; source URL/external identity remains so discovery/import will not reacquire the Product.
- Published/previously-synced Product cards use a white border treatment.
- New acquisition default image count changed from 10 to 5 while the hard operator maximum remains 20.
- Approved full acquisition adds a headless full-page source screenshot as `local://source-page-screenshot.png`; it is an extra non-selected gallery reference and does not consume the normal five selected source-image slots.
- Persistent diagnostics/log retention and startup no-hidden-AI contracts from 49.3I.25 remain in force.

## Database / Migration / Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- archive reuses existing `workflow_status` / `source_state`
- delete uses existing `is_blocked` identity retention
- no reset/drop/truncate
- no Product/media/history physical deletion
- no API key/token committed
- Local Catalog SQLite is never copied to Production MySQL
- Production untouched

## Verification Status
GitHub implementation, focused tests and Windows runner are committed. No Windows execution result has been reported for 49.3I.26 yet. Do not mark this hotfix accepted or deployable until the Local gate and visual/runtime QA pass.

## Exact Next Task — Windows 49.3I.26 Gate
1. close Catalog Center and verify Local worktree clean,
2. fetch/prune and ff-only pull the live feature branch,
3. verify Local HEAD equals fetched Remote HEAD,
4. run `catalog_center\RUN_PHASE49_3I26_OPERATOR_COMPLETION_GATE.ps1` with the verified final HEAD,
5. launch and verify Product starts at Stage 1 Basic Info with original 1..7 numbering and no lock popup,
6. verify every stage can be opened even with missing data,
7. verify Images renders five cards per row and scrolls vertically; no delayed 49.3G callback restores horizontal layout,
8. verify maximize/full-screen button,
9. run exact-link completion once: progress percentage/stages visible, timeout says 120s, no image URL is sent to AI, Product text/SEO plus image text metadata update together,
10. if all selected image files are local, verify image SEO files/metadata become ready without a second AI request; if a local file is missing, verify it is reported/deferred instead of causing a hidden network-image wait,
11. verify new acquisition defaults to 5 images and adds source-page screenshot as an extra non-selected image,
12. verify Products gallery selection, bulk archive and identity-preserving delete/block,
13. reopen application and verify old/new diagnostics remain; no startup AI connection/model scan is triggered,
14. create a fresh safe diagnostic if any lag/hang/error occurs.

## Release Gate After Windows PASS
Exactly one `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → explicit owner approval → read-only Production path/branch/commit/venv/MySQL/backup/rollback verification → deploy approved GitHub snapshot only → Production HTTP/data/media/SEO verification.

## What Remains
Windows 49.3I.26 automated + visual/runtime gate, one Local Publish E2E, owner acceptance, then Production verification/deploy. Store ZarinPal remains after Catalog Production verification.
