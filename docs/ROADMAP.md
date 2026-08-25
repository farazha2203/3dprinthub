# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.26 — Unified Exact-Link Completion + Canonical Wizard + Vertical Gallery + Product Archive`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION VERIFY`

## Immediate Priority
1. Windows acceptance of 49.3I.26 final Product workflow and responsiveness.
2. Original 1..7 Product stage order with free navigation and publish-only readiness blocking.
3. One exact-link action for source facts + Persian Product content/SEO + image text metadata, with no image upload to AI.
4. 0–100% progress/current stage, 120-second AI ceiling and separate source-link recheck on timeout.
5. Five-column vertically scrollable Images layout that cannot be overwritten by old 49.3G horizontal callbacks.
6. Product bulk selection/archive/delete-block while preserving source identity against re-import.
7. New acquisition default five source images plus one non-selected full-page source screenshot.
8. Persistent logs/no hidden AI-on-startup regression check.
9. One Local Publish E2E and owner acceptance before Production work.

## 49.3I.26 Acceptance Contract
- Product stages are 1 Basic Info, 2 Commerce, 3 Images, 4 Content/SEO, 5 Source/License, 6 Slider, 7 Review/Publish.
- every stage is directly navigable even if another stage is incomplete.
- Basic Info exposes canonical exact-link completion.
- exact-link completion reads the real source, preserves available title/creator/category/description/weight/print time, then calls the saved Provider/Model.
- AI receives Product/source text facts only and `image_urls=[]`.
- one completion applies Product Persian content/SEO and selected-image filename/Alt/Title/Caption/Keywords.
- physical image finalization never starts source-image network downloads from the unified AI path; it runs only when selected source files are already local.
- job dialog shows determinate progress and stage; timeout ceiling is 120 seconds and timeout triggers a source URL health recheck.
- Images uses five cards/row with vertical y-scroll; older horizontal callback is overridden at the final boundary.
- Product Workspace has maximize/full-screen toggle.
- Products gallery supports per-card/group selection, archive and identity-preserving block/delete.
- archived Products are hidden from normal active Product queries; blocked Products remain in blocked identity history and are not rediscovered/reimported.
- new acquisition default image limit is 5, hard maximum stays 20.
- source-page screenshot is an extra local, non-selected gallery image.
- startup must not call provider `/models` or test connectivity without explicit operator Search/Test.
- old diagnostic/audit history remains preserved.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Existing `workflow_status`, `source_state` and blocked identity fields are reused. Local SQLite is not copied into Production MySQL. Production untouched.

## Focused Windows Gate
Clean/ff-only pull live feature HEAD → compile 49.3I.26 composition/modules → run 49.3I.26 plus inherited 49.3I regressions → `launch.py --verify-only` → launch at Basic Info without lock popup → free stage navigation → five-column vertical Images → exact-link 0–100% text-only AI completion → verify Product/SEO/image text metadata and no hidden image-network wait → default-5 acquisition + source screenshot → Product selection/archive/block → verify persistent logs and no startup provider scan.

## Release Gate
Windows PASS → one Local Publish E2E → Local Store/Admin/Product/Media/SEO verification → explicit owner approval → read-only Production state verification → approved GitHub snapshot only → Production verification.
