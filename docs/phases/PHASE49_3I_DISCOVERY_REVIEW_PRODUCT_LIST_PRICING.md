# Phase49.3I — Discovery Review + Product Explorer + Pricing + Observable AI

Updated: 2026-08-23
Branch: `epic/phase49-unified-product-slider-sync`
Current Hotfix: `49.3I.11`
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Goal
Provide a business-usable Catalog Center flow that discovers source products cheaply, previews before full acquisition, prepares Persian ecommerce/SEO content, supports explicit pricing, exposes every AI execution result/error, enforces exact provider schema contracts, protects manual edits and publishes only through verified Local/Production gates.

## Canonical State Machine
`Exact Search/Listing/Category URL → Preview Candidate → Approve/Archive → Approved Full Fetch → Product Workspace → LOCAL PUBLISH ONLY → Local Django E2E → Owner Approval → Production`

## Discovery / Full Fetch Contract
Preview contains only source identity/external id, source URL, basic title and one thumbnail. Product URL uses mature direct intake; Group/Category/Search/Listing uses Preview first. Approved Full Fetch uses the mature extractor only after approval. Image limit remains `1..20`, default `10`. Archive blocks rediscovery without Full Fetch.

## Provider / Credential Contract
Providers: AvalAI, OpenRouter, Google Gemini Direct, OpenAI Direct. Windows Credential Store/environment remains credential source of truth. API keys, FTP password and Bridge token stay outside Git/SQLite/log trace payloads.

## Observable AI Contract
Preserved from 49.3I.8–10:
- real All-Fields uses mature Task Center,
- immediate first-paint,
- scrollable `ارسالی / دریافتی / خطا-Diagnostics`,
- elapsed timer + Stop Waiting,
- 90-second title watchdog,
- 210-second full-AI watchdog,
- stale/cancelled late result cannot mutate product,
- explicit rerun refreshes AI-owned content while protecting manual overrides,
- title translation uses current Provider/Model and rejects generic output.

## 49.3I.11 — Provider Schema + Trace/Busy Runtime Recovery
### Owner Evidence
A real AvalAI response was semantically good but structurally wrong: `seo_title`/`seo_description` aliases were returned instead of `seo_title_fa`/`seo_description_fa`, `content_notes` was a string instead of an array, and required fields were missing. The provider had returned HTTP success, so the issue was not simply “AI did not answer”.

The same run showed the full provider model catalog in the trace and the operator reported a later Provider/Model change looked hung.

### Corrected Contract
- AvalAI/OpenRouter receive the real requested JSON Schema,
- strict schema response format is preferred when supported,
- the exact schema is always present in the provider instruction,
- bounded compatibility fallback: strict schema → `json_object` → no response format,
- syntactically valid provider JSON is still rejected unless required keys/types match,
- one automatic schema repair is allowed; a second failure becomes a precise visible error,
- explicit selected model is used directly,
- model list is cached within the client request window,
- duplicate model probes are reduced,
- `/models` trace is summarized as count + bounded sample,
- Stop Waiting/watchdog/stale abort releases Workspace busy state immediately,
- a new Provider/Model request may start immediately after abort,
- the old background response remains stale/non-applicable.

## Products Explorer / Pricing
Preserved:
- Product Workspace canonical detailed editor,
- Explorer visual/lightweight,
- selection-loop guard,
- Fixed / Range / Formula-Dynamic independent,
- Range never invokes Formula.

## Runtime / Test Surface — 49.3I.11
Added:
- `catalog_center/app/phase49_3i_schema_runtime_recovery.py`,
- `catalog_center/tests/test_epic49_phase49_3i_schema_runtime_recovery.py`.

Changed:
- `catalog_center/app/phase49_3i_local_qa_hotfix.py`,
- `RUN_PHASE49_3I_LOCAL_GATE.ps1` → v`49.3I.11`,
- `.github/workflows/phase49-3i-ci.yml`.

No Django migration and no Catalog schema migration.

## Final GitHub Validation — 49.3I.11
Implementation PR `#57`: MERGED.
Validated feature head: `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`.
Epic merge commit: `41d37d56437765119b9bb274037e9af7a5defbbe`.

Successful runs:
- Phase49.3I `32628666588` — SUCCESS,
- Phase49.3H `32628666600` — SUCCESS,
- Phase49.3G `32628666558` — SUCCESS,
- Full Phase49 + Full Django `32628666582` — SUCCESS.

Validation includes runner/ASCII/live-Git guard, exact owner malformed-response regression, strict schema delivery, one repair, model trace compaction, abort busy-release, stale-result safety, prior AI trace/refresh/source/SEO, Preview/provider/Explorer/pricing regressions, Django no-migration contract, Windows Catalog tests and Full Django suite.

## Database / Migration / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no reset/drop/truncate,
- no historical data/media rewrite,
- no credential storage change,
- Production untouched.

## Employee Release Acceptance Gate — NEXT
1. Catalog Center closed; Local worktree clean,
2. live fetch/prune + ff-only pull current Epic,
3. run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
4. verify runner `49.3I.11` + Git snapshot marker,
5. retry exact formerly failing AvalAI product/model,
6. verify exact required schema keys/types or one visible repair request,
7. verify model catalog trace is compact and UI responsive,
8. Stop Waiting → change Provider/Model → immediate new request; old response cannot apply,
9. verify title and All-Fields watchdogs/trace,
10. low-image warning/refetch,
11. MakerWorld Preview → Approve → Full Fetch,
12. Provider/model/FTP/Bridge persistence,
13. Product selection/open + Fixed/Range/Formula.

If these pass, employees may begin controlled Catalog data entry.

## Local Publish / Production Gate
After Windows acceptance: exactly one `LOCAL PUBLISH ONLY` → Local Django E2E → verify title/SEO/source/images/pricing/visibility → explicit owner acceptance. Only then verify host branch/path/MySQL/backup/rollback and deploy the approved GitHub snapshot.

## Payment Note
Phase30 ZarinPal covers accepted Quote payments. Normal Store cart checkout remains manual bank transfer; Store request/callback/verify integration + Sandbox E2E is the next urgent track after Catalog release QA.
