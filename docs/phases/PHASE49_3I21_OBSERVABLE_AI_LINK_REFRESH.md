# Phase 49.3I.21 — Observable AI Jobs + Link-Grounded Full Refresh

Date: 2026-08-25
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Trigger
Windows operator QA showed that multiple AI actions could appear to hang while waiting on the provider. The Task Center showed `در حال اتصال به هوش مصنوعی...` with a 03:30 wait ceiling. Source-title repair itself worked, but combined source repair + AI rebuild and other AI actions could remain waiting.

## Verified Root Cause
`catalog_center/app/ai_providers.py` used a 210-second timeout for chat generation. This exactly matched the 03:30 UI ceiling. The failure mode is therefore provider/network waiting, not a database field-edit permission problem. Existing 49.3I.18/19 workers already run off the Tk main thread; the missing pieces were a shorter global provider ceiling, start/finish diagnostics, explicit operator cancellation semantics, and one authoritative link-grounded refresh flow.

## Implemented Contract
1. Provider POST requests are globally guarded by a bounded timeout. Default is 75 seconds and can be adjusted with `CATALOG_AI_TIMEOUT_SECONDS` within 20..120 seconds.
2. Every guarded request writes a start event before network wait and a finish/timeout/error event after it. Secrets are redacted by the existing diagnostics layer.
3. Existing `AIContentService.enrich_product` calls are link-grounded whenever `source_url` exists. The URL is sent together with sanitized source facts and an explicit no-guessing instruction.
4. Product Workspace stage 4 gains `AI حرفه‌ای — تکمیل کامل از لینک + عیب‌یابی زنده`.
5. New action `🌐 تکمیل همه اطلاعات بر اساس لینک محصول` performs:
   - source page fetch,
   - source parsing,
   - canonical source identity selection,
   - sanitized fact extraction,
   - AI generation using URL + facts + selected images/materials/colors,
   - received-data preview,
   - explicit operator confirmation,
   - one unified apply to editable content/SEO/image metadata.
6. Price, stock, source URL and commercial/operator choices are not overwritten by the new full-refresh action.
7. The observable dialog shows live stages and elapsed time, provides `توقف انتظار`, and refuses to apply late results after cancellation.
8. `Diagnostics` export uses the existing redacted diagnostic bundle. API keys/tokens must never be committed or pasted into diagnostics/GitHub.

## Files
- `catalog_center/app/phase49_3i21_observable_ai_link_refresh.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `catalog_center/tests/test_phase49_3i21_observable_ai_link_refresh.py`
- project documentation for 49.3I.21

## Database / Migration
- Django migration: `NONE`
- Catalog schema migration: `NONE` for this phase
- Existing diagnostics tables are reused; no destructive DB action.

## Windows Acceptance
1. compile touched modules,
2. run 49.3I.21 focused tests plus 49.3I.20/19/18 regressions,
3. run `catalog_center/launch.py --verify-only`,
4. open product `2896217`,
5. verify source identity is `Ribbed cake stand, cookie platter` or canonical equivalent,
6. run the new link-grounded full-refresh action,
7. confirm the dialog visibly advances through source fetch → AI request → received preview → apply,
8. confirm Persian title is no longer the generic model-number title,
9. confirm SEO/description/image metadata update only after operator confirmation,
10. test cancel while AI is waiting; late response must not update the product,
11. export Diagnostics and verify no API key/token appears,
12. rerun at least one existing AI entry point and confirm request-start/finish diagnostics are recorded and the UI remains responsive.

## Release Gate
No Production deploy until Windows automated gate, visual/data QA, one Local Publish E2E, and explicit owner approval all pass.