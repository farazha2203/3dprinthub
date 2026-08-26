# Phase49.3I.31 — Smart Link + Bulk Product AI

Updated: 2026-08-26  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Windows candidate: `3DPrintHub Catalog Center 8.8.2` / build `2026.08.26.1`  
Status: `IMPLEMENTED ON GITHUB / FULL WINDOWS RELEASE GATE PENDING`

## Owner request
The Windows Catalog Center must remain responsive with a large Product catalog. The main AI action must complete the current Product from its exact real source link, produce Persian content/SEO, fix selected image SEO/metadata, and selected Products must support the same operation in a safe batch workflow. AI must not receive unrelated pricing/stock/internal business state.

## Preserved contracts
- exact saved mother AI Provider/Model/key remains authoritative for AvalAI, OpenRouter, Google and OpenAI,
- no hidden Product `/models` scan or cross-provider fallback,
- Product source/link identity remains canonical and listing/search URLs are rejected when a source model URL regex exists,
- Product price, stock, availability and operator business selections are not overwritten by this AI package,
- no Production schema migration is part of this Windows phase,
- all permanent source changes remain GitHub-first.

## Performance foundation — 49.3I.29
`catalog_center/app/phase49_3i29_windows_performance_ai.py` remains the performance base:
- Products Explorer renders at most 48 cards per page,
- all DB results remain available; pagination is presentation-only,
- ProductWorkspace Save/AI marks Products as dirty instead of rebuilding the global Products gallery,
- a global Products refresh is deferred rather than triggered per product edit,
- mother AI settings are applied at application runtime.

## 49.3I.31 exact-link AI pipeline
`catalog_center/app/phase49_3i31_smart_link_bulk_ai.py` installs one final execution boundary:

`exact product URL -> real page fetch -> parser -> canonical source title -> safe extracted facts -> one structured source text -> saved mother Provider/Model -> Persian content/SEO -> selected image metadata/finalization`

### AI payload contract
Only two product fact fields are transmitted:
- `source_title`
- `source_description`

`source_description` is one bounded factual text body with headings for any facts actually extracted from the product page, including description, category path, specs, tags, author/designer, license, source price/currency, weight/print time, source engagement/date IDs and other safe parsed product facts.

Excluded from that text boundary:
- raw HTML,
- cookies,
- request/auth headers,
- credentials/secrets,
- local stock/pricing/workflow state,
- local business IDs and unrelated operator state.

### Images
- up to four selected/fallback HTTP images may be attached to the multimodal request for responsiveness,
- AI alt text/title/caption/keywords are applied to all selected website images,
- existing `phase49_3c_image_pipeline.finalize_selected_images` remains the file/SEO finalizer,
- image-finalization errors do not roll back already generated Persian text/SEO; they are surfaced as a separate warning/audit event.

## Main Product AI button
The final ProductWorkspace routes are unified to the new smart AI operation:
- `_phase49_3e_run_all_ai`,
- `_phase49_3c_stage_ai`,
- `_phase49_3i21_link_refresh`.

Therefore the operator has one predictable action rather than separate inconsistent AI/link paths.

## Batch Products workflow
Products Explorer adds:
`AI گروهی از لینک برای محصولات انتخاب‌شده`

Contract:
- only explicitly selected Product IDs are processed,
- the mother Provider/Model/key is resolved once at start,
- each Product is independently grounded from its own exact source URL,
- one failed Product is logged and the remaining selected Products continue,
- operator can request stop after the current Product,
- no per-Product global Products refresh is executed,
- one global refresh occurs when the batch finishes/stops.

## Tests / release gate
Added:
- `catalog_center/tests/test_phase49_3i31_smart_link_bulk_ai.py`,
- `.github/workflows/phase49-3i31-smart-link-bulk-ai-ci.yml`,
- Phase31 + Phase29 tests to `.github/workflows/catalog-center-windows-release.yml`,
- launcher markers and 8.8.2 release identity.

Current limitation: commits written through the connected GitHub integration did not automatically create an Actions run for the new head. Therefore this phase is NOT accepted/released yet. Full Windows regression + launcher verify + PyInstaller frozen browser smoke + live exact-link employee QA are still required before `catalog-center-v8.8.2` is called final.

## Acceptance checklist
- [x] exact source link validation and grounded fetch implemented
- [x] extracted facts organized into one AI text field
- [x] title + text only product payload
- [x] mother AI Provider/Model/key preserved
- [x] OpenRouter uses same active-profile runtime contract
- [x] main AI action also updates selected image SEO/metadata
- [x] selected Product batch operation implemented
- [x] one final Products refresh after batch
- [x] 48-card Products pagination/deferred refresh preserved
- [x] 8.8.2 candidate identity aligned in source/launcher/manifest/config
- [ ] full repository Windows tests PASS
- [ ] one-file EXE build/self-verify PASS
- [ ] frozen browser smoke PASS
- [ ] live source + OpenRouter/AvalAI employee QA PASS
- [ ] final immutable GitHub Release published/verified
