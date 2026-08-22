# PROJECT ROADMAP

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.7 — Preview + Provider Hub Recovery`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Preserved Phase49 Foundations
- unified Product / Hero / Catalog synchronization,
- Product Workspace as canonical detailed editor,
- Persian content and SEO workflows,
- Product / Portfolio publish targets,
- AI provider/runtime/provenance/cost stack,
- image intake default 10 / hard max 20,
- Fixed / Range / Formula pricing,
- visual Products Explorer,
- Local vs Production publish separation,
- live fetched GitHub snapshot handoff.

## Phase49.3I Completed Foundations
- exact operator Search/Listing/Category URL authoritative,
- Preview Candidate before Full Fetch,
- approved-only Full Fetch,
- archive/not-needed + blocked identity dedupe,
- source-text sanitation,
- Product URL vs Group/Search routing by source `model_url_pattern`,
- Explorer views/multi-select/context actions,
- selection-loop guard,
- compact metadata + Persian filter/sort,
- AI first-paint,
- secure Windows Credential Store backend.

## Windows QA Evidence Before 49.3I.7
Confirmed:
- Catalog Center launches,
- Product-vs-Group/Category/Search/sub-branch routing is fixed.

New regressions:
1. MakerWorld Preview failed with `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`.
2. Real Phase49.3F AI Provider cards still showed saved keys as empty and model lists were not visible/loaded as expected.

## Phase49.3I.7 — Preview + Provider Hub Recovery
### Scope
1. Fix only the new Stage-1 Preview browser-evaluation boundary (`ERR-49-024`).
2. Preserve mature `classic_methods.discover_classic` / `collect_classic_exact` and direct/full extraction.
3. Keep business workflow:
   `Search → Preview one thumbnail/basic identity per candidate → Approve → Full Fetch → image limit 1..20`.
4. Hydrate the real `_ai_hub_key_vars` for AvalAI/OpenRouter/OpenAI/Google from Windows Credential Store (`ERR-49-025`).
5. Rehydrate Provider cards after mature secure Save clears them.
6. Preserve FTP password/Bridge token persistence.
7. Background-load configured Provider model catalogs into existing Model ID combobox/cache.
8. Preserve manual model picker/API refresh.
9. Keep all secrets out of SQLite/Git/source/logs.

### Web/API Contract Verified
- Playwright `locator.evaluate_all(expression)` runs supplied JavaScript in page context; the expression must therefore be valid JavaScript after Python string processing.
- AvalAI supports authenticated `GET https://api.avalai.ir/v1/models` and a public models endpoint.
- OpenRouter supports `GET /api/v1/models` with Bearer auth and model sorting/filtering.
- existing `AIProviderClient` already implements the provider model path; 49.3I.7 reuses it rather than creating another client.

## Final GitHub Validation
CI-only PR `#52`: `CLOSED / NOT MERGED`.
Validated runtime base: `4e0b1b7f0f8934a03ab74037bdce5f9abe55b425`.
Marker head: `5097f45f069e40af64d452ffaa8cd07399a977f2` — not merged.

Successful runs:
- Phase49.3I: `32585956198` — SUCCESS.
- Phase49.3H: `32585956149` — SUCCESS.
- Phase49.3G: `32585956156` — SUCCESS.
- Full Phase49 + Full Django: `32585956155` — SUCCESS.

Django migration: `NONE`.
Catalog schema migration: `NONE`.
Post-validation branch changes are documentation-only.

## Must-Not-Touch
- Product Workspace detailed editor,
- mature source full extraction,
- Preview → Approve → Full Fetch state machine,
- image limit default 10 / hard max 20,
- selection-loop guard,
- Product-vs-Group routing,
- AI result/error/cost stack,
- Fixed / Range / Formula independence,
- Product/Hero revision/idempotency,
- Production DB/media/source,
- secrets in Git/log/SQLite.

## Windows Manual QA — NEXT
1. clean worktree and close Catalog Center,
2. fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.7` + Git snapshot marker,
5. verify FTP/Bridge secrets remain masked after Save/restart,
6. verify AvalAI/OpenRouter keys stay masked in the real Provider cards,
7. verify configured Provider model lists load and are selectable,
8. run exact MakerWorld search URL and verify Preview candidates appear without JS syntax error,
9. verify Preview is lightweight only,
10. approve one candidate with image limit 20 and verify Full Fetch starts only after approval,
11. archive another and verify no full fetch,
12. regression-check direct Product URL, Product open responsiveness, AI first-paint and pricing modes.

## Local Publish Gate
Only after all 49.3I.7 Windows QA passes:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- no Production endpoint.

## Production Gate
Blocked until Windows QA + Local Publish E2E + explicit owner approval. Before deployment re-verify host branch/commit/path, MySQL vendor/name, backup, rollback and host constraints.

## Immediate Next Step
Windows live GitHub snapshot pull and repository-owned 49.3I.7 Local Gate. No manual Local source patch and no Production command.
