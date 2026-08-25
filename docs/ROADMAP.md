# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.25 — Product-First Workflow + Persistent Diagnostics + Startup No-AI`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION VERIFY`

## Immediate Priority
1. Windows acceptance of startup/no-AI and responsiveness fixes.
2. Content/SEO-first Product flow with exact-link completion in Basic Info.
3. Exact source identity plus available exact-profile weight and Persian editorial content.
4. Five-column vertically scrollable image gallery and free stage navigation.
5. Publish missing-item list plus AI completion assistance.
6. Verify logs survive close/reopen and no SQLite transaction error returns.
7. One Local Publish E2E and owner acceptance before Production work.

## 49.3I.25 Acceptance Contract
- Stage 1 is Content/SEO; Basic Info is Stage 2.
- all stages can be opened even when previous ones are incomplete.
- Basic Info exposes the canonical exact-link completion action.
- exact-link preparation uses minimal persistence, not the layered full Product save pipeline.
- available source weight/print time is carried through; MakerWorld exact profile weight is preferred.
- Images shows all controlled images in a five-column vertical grid with existing card controls/metadata.
- startup does not call provider model lists or test connectivity; only explicit Search/Test may do so.
- AI network work stays background, observable and cancellable.
- diagnostics use a dedicated SQLite connection; old runtime/audit logs persist.
- publish preflight shows missing items and offers exact-link AI for AI-fillable gaps.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Existing diagnostic tables are reused. Local SQLite is not copied into Production MySQL. Production untouched.

## Focused Windows Gate
Clean/ff-only pull live feature branch → compile changed modules → run 49.3I.25 plus inherited 49.3I regression tests → run `launch.py --verify-only` → launch without automatic provider requests → reopen and verify historical logs remain → Product 151/2801606 exact-link completion → validate available source weight + Content/SEO + image text → validate responsive UI/no transaction error → validate five-column image scroll → validate publish missing/AI assist.

## Release Gate
Windows PASS → one Local Publish E2E → Local Store/Admin/Product/Media/SEO verification → explicit owner approval → read-only Production state verification → approved GitHub snapshot only → Production verification.
