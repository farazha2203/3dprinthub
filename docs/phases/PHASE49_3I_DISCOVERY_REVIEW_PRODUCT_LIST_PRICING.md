# Phase49.3I — Discovery Review + Product Explorer + Pricing + AI Refresh

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.9`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Provide a business-usable Catalog Center flow that discovers source products cheaply, previews candidates before full acquisition, prepares Persian ecommerce/SEO content, supports explicit pricing, protects manual edits, and publishes through Local/Production gates only after verification.

## Canonical State Machine
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace → LOCAL PUBLISH ONLY → Local Django E2E → Owner Approval → Production`

## Preview / Full Fetch Contract
Preview contains only:
- source identity / external id,
- source URL,
- basic title,
- one thumbnail.

Preview must not:
- enter every product page,
- download all images,
- invoke Production.

Approved Full Fetch uses the mature source extractor only after operator approval. Image limit remains `1..20`, default `10`.

Archive keeps minimal blocked identity and prevents rediscovery until restore; it does not Full Fetch.

## URL Routing
Configured source `model_url_pattern` is authoritative:
- real Product URL → mature direct intake,
- valid Group/Category/Search/Listing/sub-branch → Preview first.

## AI Provider Hub
Current cards:
- AvalAI,
- OpenRouter,
- Google Gemini Direct,
- OpenAI Direct.

Windows Credential Store/environment remains credential source of truth. Real Provider-card key hydration, model catalog loading, FTP password and Bridge token persistence remain protected by 49.3I.7+ regression tests.

## Observable AI Execution
49.3I.8 corrected the real bottom All-Fields button so it uses the mature Task Center rather than legacy `generate_ai("commerce")`.

Preserved runtime guarantees:
- immediate progress first-paint,
- connection/send/wait/receive/save/result-error visibility,
- elapsed timer,
- Stop Waiting,
- 210-second operator watchdog,
- cancel/timeout makes late result stale/non-applicable,
- no duplicate AI client/network worker.

## 49.3I.9 — AI Refresh + SEO/Source Completion
### Owner Request
When the operator changes AI Provider/Model and presses `تکمیل هوشمند همه فیلدهای AI`, generated content must be regenerated where appropriate. A previous generic title such as `محصول چاپ سه بعدی` must not remain merely because the field is non-empty.

### Corrected Contract
- explicit All-Fields rerun refreshes AI-owned/previous-pack/generated fields,
- real manual operator overrides remain protected,
- known generic Persian titles are considered refreshable,
- newly generated generic product titles are rejected rather than silently saved,
- prompt requires product-specific Persian translation and ecommerce/SEO copy grounded in source facts,
- important source title identity/use/theme terms must not collapse into generic 3D-print boilerplate,
- source website is stored as publisher/source identity,
- designer/author remains separate factual source data,
- desktop SEO/source attribution is applied to real Django Product meta/OG/source fields after mature conversion/visibility layers,
- if images are below selected image limit, All-Fields may offer the existing mature source refetch first,
- readiness defaults may use local factual defaults only,
- missing price may receive local fallback `500000` Toman for preparation only,
- material/color defaults come only from active local inventory,
- commercial-license and sale approval remain explicit operator confirmations.

## Products Explorer / Pricing
Preserved:
- Product Workspace is canonical detailed editor,
- Explorer is visual/lightweight,
- selection-loop guard,
- safe local queue actions,
- Fixed / Range / Formula-Dynamic modes remain independent,
- Range never invokes Formula.

## Runtime / Test Surface — 49.3I.9
Added/extended runtime includes:
- `catalog_center/app/phase49_3i_ai_refresh_completion.py`,
- `store/phase49_3i9_seo_sync.py`,
- dedicated Catalog/Django regression tests,
- launcher/runtime composition updates,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.9`,
- Phase49.3I CI contract updates.

No Django migration and no Catalog schema migration were introduced.

## Final GitHub Validation — 49.3I.9
CI-only PR `#55`: `CLOSED / NOT MERGED`.
Validated runtime base: `390c1aba9aaf5282f44a1ec97955af4e987100ba`.
Marker head: `0e58324bfc87e39299b81b1fbe65f9cce21ec91e` — not merged.

Successful runs:
- Phase49.3I `32623618842` — SUCCESS,
- Phase49.3H `32623618854` — SUCCESS,
- Phase49.3G `32623618950` — SUCCESS,
- Full Phase49 + Full Django `32623618792` — SUCCESS.

Validation includes:
- runner v49.3I.9 / ASCII-only Windows PS5.1,
- live Git snapshot guard,
- compile,
- AI refresh/manual-override contract,
- generic-title rejection,
- image preflight/refetch behavior,
- publisher/source mapping,
- Product SEO meta/OG/source mapping,
- prior Preview/provider/Explorer/pricing regressions,
- Django no-migration contract,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no historical data/media rewrite,
- no credential storage change,
- Production untouched.

## Employee Release Acceptance Gate — NEXT
1. close Catalog Center,
2. require clean Local worktree,
3. fetch/prune + ff-only pull current Epic,
4. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.9` + Git snapshot marker,
6. test one known product with bottom All-Fields AI,
7. verify product-specific Persian title + SEO and Provider/Model rerun behavior,
8. verify low-image warning/refetch,
9. verify MakerWorld Preview → Approve → Full Fetch,
10. verify Provider/model/FTP/Bridge credentials,
11. verify Product selection/open and Fixed/Range/Formula.

If these pass, employees may begin Catalog data entry. Production publishing remains gated separately.

## Local Publish Gate
After Windows acceptance:
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify title/SEO/source/images/pricing/visibility in Local Store/Admin,
- explicit owner acceptance.

## Production Gate
Before deploy:
- read-only host verification,
- exact branch/commit/path,
- MySQL vendor/name,
- `.env` effective settings without leaking secrets,
- backup + rollback,
- GitHub pull only,
- checks/migration plan/static/restart,
- HTTP/admin/store/product/cart verification.

## Payment Note
Phase30 online payment currently covers accepted Quote payments through ZarinPal. The normal Store cart checkout still exposes only bank transfer and redirects to manual-payment flow, so live Store gateway activation is a separate urgent implementation/test gate before real customer card payments.
