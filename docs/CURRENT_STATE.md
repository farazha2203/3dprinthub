# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.21 — Observable AI Jobs + Link-Grounded Full Refresh`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.18 operator editing, 49.3I.19 canonical source identity and 49.3I.20 visible operator panels are present on the feature branch. Windows operator QA now verified that source-title refresh can read the correct MakerWorld identity, but multiple AI actions can remain waiting for the provider and appear hung.

The observed Task Center ceiling was 03:30. Repository verification found `catalog_center/app/ai_providers.py` used a 210-second chat request timeout. This matches the observed wait exactly. The current root cause is therefore provider/network waiting and weak request observability, not a database field-edit permission denial.

49.3I.21 adds a global bounded provider guard, request start/finish/timeout diagnostics, URL grounding for AI content generation, and a new one-click link-based full refresh with preview/apply.

## Implemented 49.3I.21 Contract
- AI POST requests are bounded to a default maximum of 75 seconds (`CATALOG_AI_TIMEOUT_SECONDS`, constrained to 20..120 seconds).
- request-start is logged before the network call, so a stalled request has a visible last stage.
- timeout/error/success is logged with provider/model/operation/duration; secret redaction reuses `phase49_diagnostics`.
- `AIContentService.enrich_product` receives the source URL plus sanitized source facts whenever a URL is available.
- Product Workspace stage 4 gains `AI حرفه‌ای — تکمیل کامل از لینک + عیب‌یابی زنده`.
- new action `🌐 تکمیل همه اطلاعات بر اساس لینک محصول` performs source fetch → parse → canonical identity → AI request → received preview → explicit apply.
- apply updates the existing editable content/SEO/image-metadata fields through the mature 49.3I.18 apply path.
- source URL, price, stock and commercial/operator choices are not overwritten.
- the dialog has `توقف انتظار`; cancelled late results are ignored and must not update the product.
- Diagnostics bundle export remains local and redacted. No PAT/API key is required or allowed in project logs.

## Acceptance Fixture
Primary QA URL:
`https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?from=search#profileId-3236824`

Expected canonical source identity:
`Ribbed cake stand, cookie platter` or the normalized canonical equivalent.

The Persian product title must no longer remain a generic `مدل میکرورلد 2896217` after a successful link-grounded AI refresh.

## Files Added / Updated for 49.3I.21
- added `catalog_center/app/phase49_3i21_observable_ai_link_refresh.py`
- updated `catalog_center/app/phase49_3i_pricing_modes.py`
- added `catalog_center/tests/test_phase49_3i21_observable_ai_link_refresh.py`
- added `docs/phases/PHASE49_3I21_OBSERVABLE_AI_LINK_REFRESH.md`
- updated active project documentation.

## Database / Migration / Secret Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no reset/drop/truncate
- no media/history deletion
- no source URL rewrite
- no price/stock overwrite
- no API key/token committed
- existing redacted diagnostics tables are reused
- Production untouched

## Test Status
GitHub code and focused regression tests are committed. Windows Local execution has NOT yet been reported for 49.3I.21, so this phase is not Local Tested and not Accepted.

## Current Git State
Feature branch remote HEAD must be fetched live before Local QA. Do not rely on an older 49.3I.20 SHA from chat.

## Exact Next Task — Windows 49.3I.21 Gate
1. close Catalog Center,
2. verify clean worktree at `D:\projects\3DPrintHub`,
3. fetch/prune, switch to `agent/phase49-3i18-operator-bulk-ai-rebuild`, ff-only pull live remote HEAD,
4. verify Local HEAD equals fetched remote HEAD,
5. compile 49.3I.21 plus 49.3I.20/19/18 composition modules,
6. run 49.3I.21 focused tests and inherited 49.3I.20/19/18 + 49.3I.16/15/discovery regressions,
7. run `catalog_center\launch.py --verify-only`,
8. launch Catalog Center and verify the new stage-4 panel is visible,
9. open product 2896217 and run `تکمیل همه اطلاعات بر اساس لینک محصول`,
10. verify source fetch, AI request, received preview and explicit apply stages,
11. confirm content/SEO/image metadata update consistently only after approval,
12. test `توقف انتظار`; late response must not apply,
13. export Diagnostics and verify no key/token exists,
14. retest existing AI buttons and verify UI remains responsive and request-start/finish/timeout diagnostics identify the failing provider/model/operation.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- explicit owner approval,
- read-only Production path/branch/venv/MySQL/backup/rollback verification,
- deploy only the approved GitHub snapshot,
- Production HTTP/data/media verification.

## What Remains
- Windows automated gate,
- visual/data QA of all important AI entry points,
- one Local Publish E2E,
- owner acceptance,
- only then Production deploy/verification.

## Exact Next Step
Pull the live feature-branch HEAD onto the canonical Windows repo and run the 49.3I.21 Local acceptance gate. Production remains blocked.