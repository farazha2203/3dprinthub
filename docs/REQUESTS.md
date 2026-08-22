# OWNER REQUESTS

Last Updated: 2026-08-22

## Phase49.3H

### REQ-49H-001 — Unified SEO execution visibility
Status: GITHUB_UPDATED / CI SUCCESS / LOCAL QA PENDING
Request:
- every SEO-related button/action visibly shows execution/result/error state
- provider/model/request/tokens/cost/log information where available
- error/result remains recoverable and sanitized

### REQ-49H-002 — Per-product AI/SEO cost
Status: GITHUB_UPDATED / CI SUCCESS / LOCAL QA PENDING
Request:
- record cost spent editing/SEOing each product
- internal publish cost receipt
- real provider cost only; never invent unsupported cost

### REQ-49H-003 — Controlled image intake
Status: GITHUB_UPDATED / CI SUCCESS / LOCAL QA PENDING
Request:
- operator determines max images per product
- default 10; hard max 20
- limit applies to persisted/selected/downloaded images
- reaching the limit does not stop the multi-product workflow

## Phase49.3I

### REQ-49I-001 — Exact search URL discovery
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
- when owner supplies a MakerWorld search/listing URL, discovery must use that exact URL as the authoritative source
- example: `https://makerworld.com/en/search/models?keyword=cake+stand`
- expected candidates include source URLs such as MakerWorld model `2834255` and `2845731` when present on that result page
- do not silently replace supplied search URL with configured default popular/download listing

### REQ-49I-002 — Two-stage candidate review before full fetch
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
- Stage 1: discover lightweight candidates and obtain only one thumbnail + product name/basic source identity
- show candidate review list before expensive full extraction
- Stage 2: only operator-approved candidates receive full content/spec/text extraction and selected number of images
- image limit remains selectable 1..20

### REQ-49I-003 — Archive / not-needed candidate
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
- operator can select candidate and mark `آرشیو / لازم نیست`
- candidate becomes blocked/not-wanted without full extraction
- blocked identities must not be rediscovered/refetched unless explicitly restored
- no source record is destructively deleted

### REQ-49I-004 — Duplicate guard
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
- same source product must not be received twice
- guard by source code + external source id and normalized URL
- existing blocked/product identities are treated as known before full fetch

### REQ-49I-005 — Safe source text persistence
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
- scraped source textual fields should not persist Chinese/CJK or other unexpected script/font garbage
- URLs/source identity must remain exact and unchanged
- Persian editorial/AI `_fa` fields must remain Persian and are not filtered by this source-text rule
- no destructive mass rewrite of historical DB rows during this phase

### REQ-49I-006 — Lightweight products page
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
- main product/work list should primarily show thumbnail and product name
- remove/hide embedded giant parameter/editor surface from the list page
- provide one clear `صفحه محصول / ویرایش کامل` action
- all detailed edits continue in the existing Product Workspace

### REQ-49I-007 — Three explicit pricing modes
Status: GITHUB_UPDATED / CI SUCCESS / WINDOWS QA PENDING
Request:
1. exact/fixed: one exact amount, e.g. 1,200,000 toman
2. range: explicit min/max, e.g. 200,000–500,000 toman
3. formula/dynamic: grams/material rate + print time + supervision and configured pricing inputs
- range must not be conflated with formula pricing
- preserve existing Dynamic Variant price source of truth

## Phase49.3I Validation
- Dedicated 49.3I CI Run `32569551060` — SUCCESS
- Phase49.3H regression Run `32569551053` — SUCCESS
- Phase49.3G regression Run `32569551048` — SUCCESS
- Full Phase49 + Full Django Run `32569551034` — SUCCESS
- Runtime/base SHA validated: `9d462f1ec12b00727c96acf9d4f59b4723d676b4`
- Windows automated gate + visual/data QA remain required before Local Publish/acceptance.

## Preserved Requests From Prior Phases
- Workspace stages remain accessible; incomplete task is guided, not trapped.
- AI provider/model selectable and persistent with connection test.
- Image SEO operates only on selected product images and sends no image bytes/files/URLs to AI.
- AI tasks/provenance indicate what AI filled and allow operator manual override/disable.
- Local vs Production publish separation remains fail-closed.
- Source refresh preserves human edits.
- Production cannot be touched before Local approval.

## Change Rule
A new request does not authorize unrelated redesign. Implement approved delta with minimal changes and preserve mature behavior unless owner explicitly requests removal/replacement.
