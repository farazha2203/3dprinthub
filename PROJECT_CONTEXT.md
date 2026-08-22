# PROJECT_CONTEXT — 3DPrintHub

> Snapshot عملیاتی Source of Truth. برای جزئیات هر Phase به فایل Phase مربوطه و `docs/00_PROJECT_MASTER_ROADMAP_FA.md` مراجعه شود. هنگام تعارض: وضعیت واقعی محیط + جدیدترین CI/Local/Host output مقدم است.

## 1) Project / Git / Paths

- Repository: `farazha2203/3dprinthub`
- Active branch: `epic/phase49-unified-product-slider-sync`
- Windows project root: `D:\projects\3DPrintHub`
- Windows venv: `D:\projects\3DPrintHub\.venv`
- Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- Django local DB: `D:\projects\3DPrintHub\db.sqlite3`
- Catalog persistent root: `D:\projects\3dprinthub-catalog-manager`
- Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
- Legacy retained data: `D:\projects\3dprinthub_catalog_center`
- Backups: `D:\projects\3dprinthub-backups`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`

## 2) Mandatory Delivery Rule

`GitHub → CI → Windows pull --ff-only → repository Local Gate → Manual Visual/Data QA → LOCAL PUBLISH E2E → explicit owner approval → Production backup/deploy → Production verification`

Rules:
- no standalone Chat ZIP/patch/script/source delivery
- no permanent source editing on Production
- dirty Windows tree = STOP/INSPECT; no `reset --hard` / `git clean` shortcut
- no DB/.env/media/persistent-data reset for code sync
- secrets never stored in Git/log/audit/chat
- Production forbidden before explicit Local approval

Policy: `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`.

## 3) Current Epic / Phase

Epic chain:
`49.2A → 49.2B → 49.2C → Epic49 Unified → 49.3A → 49.3B → 49.3C → 49.3D/3D.1 → 49.3E → 49.3F/3F.1 → 49.3G → 49.3H → 49.3I`

Current Phase:
`Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes`

Status:
`GITHUB_UPDATED / CI SUCCESS / WINDOWS LOCAL QA PENDING`

Canonical active Phase doc:
`docs/phases/PHASE49_3I_DISCOVERY_REVIEW_PRODUCT_LIST_PRICING.md`

## 4) Catalog Center Baseline

- Version: `8.7.1`
- Build family: `2026.08.16.3`
- Canonical operator editor: Epic49 Product Workspace
- Canonical current runner: `D:\projects\3DPrintHub\RUN_PHASE49_3I_LOCAL_GATE.ps1`
- Runner version: `49.3I.0`
- Runner chain: `49.3I → 49.3H → 49.3G → 49.3F.1 → 49.3E → 49.3D/base gates`
- Local/Production publish targets remain separate and fail-closed.

## 5) Phase49.3H Protected Baseline

GitHub CI complete; Windows QA still pending and is chained by 49.3I runner.

Protected contracts:
- SEO/AI execution progress + persistent result/error visibility
- per-product AI/SEO cost ledger + internal publish receipt
- provider cost is recorded only when real/known; unsupported cost remains unknown
- image intake default 10 / hard max 20
- cap applies to persisted/selected/downloaded images
- Image SEO selected-only + text-only; image bytes/files/URLs are not sent to AI

49.3H validated Epic HEAD:
`e145d1e11619e36bd766788083bee59899a80cbb`

## 6) Phase49.3I Implemented Contract

### Discovery
- explicit operator search/listing HTTP(S) URL is authoritative
- MakerWorld `cake+stand` URL is no longer replaced by configured default listing
- Stage 1 Preview stores one thumbnail + title + source identity/link only
- Stage 2 full extraction runs only after explicit operator approval
- approved full fetch uses image limit 1..20
- archive/not-needed creates/preserves blocked identity without full extraction
- source code + external ID + normalized URL prevent duplicate/full-refetch of known/blocked identities

### Source Text Safety
- scraped source text is normalized before persistence
- CJK/Cyrillic/unexpected script/emoji garbage removed from source text
- URLs/source identity preserved exactly
- Persian `_fa` editorial/AI fields are not filtered
- no historical mass rewrite

### Products Page
- main work list is lightweight: thumbnail + product name
- detailed embedded editor hidden from list surface
- one `صفحه محصول / ویرایش کامل` action opens Product Workspace
- mature Product Workspace functionality remains intact

### Pricing
Three operator business modes:
1. `fixed`: exact final amount
2. `range`: explicit min/max consultation range
3. `dynamic`: formula/Variant engine

Dynamic Source of Truth remains `ProductVariant.price_breakdown()` / cached Variant price; Product Detail/Cart/Checkout do not get a parallel calculator.

## 7) Phase49.3I CI Incident + Fix

Initial CI-only PR #41 found a real issue:
`makemigrations --check --dry-run` proposed `store.0034_alter_productcatalogprofile_pricing_strategy`.

Root Cause:
- first 49.3I implementation mutated runtime Django field `choices` to add `range`
- `choices` are migration-state metadata

Correct Fix:
- do not mutate migration-owned choices
- existing `CharField(max_length=20)` stores raw `range`
- Windows exposes Fixed/Range/Formula
- server sync persists `pricing_strategy=range` + `price_mode=range`
- Django migration remains NONE

Canonical error record: `ERR-49-015` in `docs/ERRORS.md`.

## 8) Final GitHub Validation

Runtime/base SHA validated by PR #42:
`9d462f1ec12b00727c96acf9d4f59b4723d676b4`

CI:
- Phase49.3I dedicated Run `32569551060` — SUCCESS
- Phase49.3H regression Run `32569551053` — SUCCESS
- Phase49.3G regression Run `32569551048` — SUCCESS
- Full Phase49 + Full Django Run `32569551034` — SUCCESS
- PR #42 closed / not merged

The CI validated:
- runner contract
- compile
- exact URL / preview / approve / archive / duplicate guards
- source-text safety
- lightweight product list
- Fixed/Range/Dynamic contracts
- Django `check`
- `makemigrations --check --dry-run` = no changes
- migration plan
- launcher markers
- Phase49.3H and 49.3G regressions
- mature Epic49 regressions
- full Django suite

## 9) Database State

Important applied Windows migrations from prior phases:
- `store.0031` ✅
- `store.0032` ✅
- `website.0022` ✅
- `store.0033` ✅
- `website.0023` ✅

Phase49.3G:
- no Django migration
- local Catalog additive provenance columns only

Phase49.3I:
- no Django migration
- local Catalog additive candidate-review table only
- no drop/truncate/reset/delete

Production has not received Phase49.3C..49.3I deployment/migration changes.

## 10) AI / Diagnostics Protected Baseline

Canonical providers:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

Rules:
- raw model ID persisted, not decorated label
- active provider/model single source of truth
- keys from secure store/environment
- request ID/tokens/cost/log audited where supported
- Bearer/secret redaction regression-protected
- AI cannot fabricate price/license/inventory/material/color facts
- operator manual override/provenance remains protected

`$django-admin-expert`: no matching Plugin/Skill available in the current session; do not claim installed.

## 11) Known Open / Deferred Items

- Local `/api/v1/catalog/sitemap/` 404 remains a separate Root Cause task before complete Epic closure.
- CKEditor4 warning/debt is separate.
- Production realtime/Redis architecture warning is separate.
- Pillow `Image.getdata()` deprecation is non-blocking debt.
- Google membership credentials warning is expected when credentials are intentionally empty in CI.

## 12) Production Status

**UNTOUCHED / NOT APPROVED / NOT DEPLOYED for Phase49.3C..49.3I.**

Before any Production action re-verify:
- host project root
- current branch/commit
- clean/safe host state
- Python venv
- `connection.vendor == mysql`
- exact production DB name
- `.env`
- backup target/rollback
- migration plan

## 13) Exact Next Gate

```text
Windows D:\projects\3DPrintHub
→ git status --short
→ dirty? STOP / INSPECT
→ git fetch --prune origin
→ git switch epic/phase49-unified-product-slider-sync
→ git pull --ff-only origin epic/phase49-unified-product-slider-sync
→ verify pulled HEAD
→ run .\RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp
→ Automated Local PASS
→ MakerWorld cake+stand Preview QA
→ approve one candidate with image limit 10
→ archive one candidate
→ repeat search / verify duplicate+blocked guards
→ lightweight Products list QA
→ Fixed / Range / Formula pricing QA
→ one LOCAL PUBLISH ONLY
→ Local Django Product/Profile/Hero/Store/Admin verification
→ explicit owner approval
→ Production plan only after approval
```

Any new Local regression is fixed at its Root Cause on GitHub with a regression test; no manual Windows source patch.
