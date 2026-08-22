# PROJECT_CONTEXT — 3DPrintHub

> Operational Source of Truth snapshot. Repository/GitHub is authoritative. When documentation conflicts with real environment state, latest verified CI/Windows/Host output and actual migration/data state win.

## 1) Project / Git / Paths
- Repository: `farazha2203/3dprinthub`
- Active branch: `epic/phase49-unified-product-slider-sync`
- Windows root: `D:\projects\3DPrintHub`
- Windows venv: `D:\projects\3DPrintHub\.venv`
- Catalog Center: `D:\projects\3DPrintHub\catalog_center`
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
- dirty Windows tree = STOP/INSPECT; no reset/delete shortcut
- no DB/.env/media/persistent-data reset for code sync
- secrets never stored in Git/log/audit/chat
- Production forbidden before explicit Local approval

Policy: `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`.

## 3) Current Epic / Phase
Epic chain:
`49.2A → 49.2B → 49.2C → Epic49 Unified → 49.3A → 49.3B → 49.3C → 49.3D/3D.1 → 49.3E → 49.3F/3F.1 → 49.3G → 49.3H → 49.3I`

Current phase:
`Phase49.3I — Discovery Review Queue + Product List Simplification + Explicit Pricing Modes`

Current hotfix:
`49.3I.1 — Windows PowerShell 5.1 Runner Encoding`

Status:
`GITHUB_UPDATED / HOTFIX CI SUCCESS / WINDOWS LOCAL RERUN PENDING`

Canonical phase doc:
`docs/phases/PHASE49_3I_DISCOVERY_REVIEW_PRODUCT_LIST_PRICING.md`

## 4) Catalog Center Baseline
- Version: `8.7.1`
- Build family: `2026.08.16.3`
- Canonical operator editor: Epic49 Product Workspace
- Canonical runner: `D:\projects\3DPrintHub\RUN_PHASE49_3I_LOCAL_GATE.ps1`
- Runner version: `49.3I.1`
- Runner encoding contract: `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`
- Runner chain: `49.3I → 49.3H → 49.3G → 49.3F.1 → 49.3E → 49.3D/base gates`
- Local/Production publish targets are separate and fail-closed.

## 5) Phase49.3I Functional Contract
Discovery:
- explicit operator HTTP(S) search/listing URL is authoritative
- Stage 1 Preview stores one thumbnail + title + source identity/link only
- Stage 2 full extraction occurs only after operator approval
- approved full fetch uses image limit 1..20; default 10, hard max 20
- archive/not-needed creates/preserves blocked identity without full extraction
- source code + external ID + normalized URL prevent duplicate full fetch

Source text safety:
- scraped source text is normalized before persistence
- CJK/Cyrillic/unexpected scripts and emoji are removed from source text
- URLs/source identity remain exact
- Persian editorial/AI `_fa` fields remain Persian
- no historical mass rewrite

Products page:
- main work list is lightweight: thumbnail + product name
- detailed embedded editor is hidden on the list surface
- full editing routes to Product Workspace

Pricing:
1. `fixed` — exact final amount
2. `range` — explicit min/max consultation range
3. `dynamic` — existing Variant formula engine

Dynamic Source of Truth remains `ProductVariant.price_breakdown()` / cached Variant unit price.

## 6) Phase49.3H Protected Baseline
- SEO/AI execution progress + persistent result/error visibility
- per-product AI/SEO cost ledger + internal publish receipt
- unsupported provider cost remains unknown; never invented
- image default 10 / hard max 20
- Image SEO selected-only + text-only; no image bytes/files/URLs sent to AI

## 7) CI Incident — Phantom Migration
Initial 49.3I PR #41 proposed `store.0034_alter_productcatalogprofile_pricing_strategy` because runtime code mutated Django field `choices`.

Correct fix:
- do not mutate migration-owned field metadata
- existing CharField stores raw semantic value `range`
- server sync stores `pricing_strategy=range` + `price_mode=range`
- no new migration

Canonical error: `ERR-49-015`.

## 8) Windows Incident — Runner Encoding
Windows first delivery from validated HEAD `91f39681e2008c29d0ec7bc06794b935d794b33e`:
- clean worktree verified
- Git fetch/switch/pull succeeded
- Local/Remote HEAD matched
- repository runner existed
- runner then failed before execution with `Unexpected token ')'` and mojibake Persian text

Root Cause:
- runner was UTF-8 without BOM and contained Persian strings + em dash
- Windows PowerShell 5.1 decoded BOM-less script using legacy ANSI semantics
- em-dash bytes became mojibake containing a smart quote interpreted as a PowerShell string delimiter
- modern Linux `pwsh` syntax CI did not reproduce the legacy decode boundary

Correct fix:
- runner v`49.3I.1` is ASCII-only
- CI reads raw bytes and fails on any byte `>127`
- CI verifies marker `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`
- no application/DB/Production behavior changed

Canonical error: `ERR-49-016`.

## 9) Hotfix GitHub Validation
CI-only PR #44: **CLOSED / NOT MERGED**.
Validated runner-hotfix runtime/base SHA:
`451bcb9e264b847259a6ea0414550e4f80afa250`

SUCCESS:
- Phase49.3I Run `32570978818`
- Phase49.3H Run `32570978800`
- Phase49.3G Run `32570978829`
- Full Phase49 + Full Django Run `32570978799`

The validation covered raw-byte runner encoding, PowerShell parse/chain/Production guard, Phase49.3I dedicated tests, Django check/migration contract, mature Phase49 regressions and full Django suite.

## 10) Database State / Safety
Important Windows migrations from prior phases:
- `store.0031` applied
- `store.0032` applied
- `website.0022` applied
- `store.0033` applied
- `website.0023` applied

Phase49.3G:
- no Django migration
- local Catalog additive AI provenance columns only

Phase49.3I:
- no Django migration
- local Catalog additive candidate-review table only

Runner hotfix:
- no DB change
- no migration
- no reset/drop/truncate/delete
- no media/history rewrite

Production has not received Phase49.3C..49.3I deployment changes.

## 11) AI / Diagnostics Protected Baseline
Providers:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

Rules:
- raw model ID persisted, not decorated label
- active provider/model single source of truth
- keys only from secure store/environment
- request ID/tokens/cost/log audited where supported
- Bearer/secret redaction regression-protected
- AI cannot fabricate price/license/inventory/material/color facts
- operator manual override/provenance remains protected

`$django-admin-expert`: no matching Plugin/Skill available in the current session; do not claim installed.

## 12) Known Open / Deferred Items
- Local `/api/v1/catalog/sitemap/` 404 remains a separate Root Cause task before complete Epic closure.
- CKEditor4 warning/debt is separate.
- Production realtime/Redis architecture warning is separate.
- Pillow `Image.getdata()` deprecation is non-blocking debt.
- Google membership credentials warning is expected when intentionally unset in CI.

## 13) Production Status
**UNTOUCHED / NOT APPROVED / NOT DEPLOYED for Phase49.3C..49.3I.**

Before Production re-verify host root, branch/commit, safe worktree, Python venv, MySQL vendor/name, `.env`, backup target/rollback and migration plan.

## 14) Exact Next Gate
```text
final docs-closed GitHub validation
→ Windows D:\projects\3DPrintHub
→ git status --short
→ dirty? STOP / INSPECT
→ git fetch --prune origin
→ git switch epic/phase49-unified-product-slider-sync
→ git pull --ff-only origin epic/phase49-unified-product-slider-sync
→ verify exact validated HEAD
→ verify RUN_PHASE49_3I_LOCAL_GATE.ps1 v49.3I.1
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

Any new Local regression is fixed at its Root Cause on GitHub with a regression test. No manual Windows source patch.
