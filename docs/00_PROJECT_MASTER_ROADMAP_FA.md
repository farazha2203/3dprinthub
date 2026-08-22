# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Migration/Data/Server و جدیدترین CI/Local/Host output بر متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**زبان اصلی:** Python / Django  
**اپراتور اصلی:** Windows Catalog Center  
**مدیریت دوم:** Django Admin  
**Production:** قبل از Local QA + Local Publish E2E + تأیید صریح کاربر ممنوع.

---

## 1) قانون مادر

مسیر اجباری:

```text
READ DOCS
→ VERIFY REAL STATE
→ CHECK PREVIOUS ERRORS
→ IMPLEMENT ON GITHUB
→ CI
→ WINDOWS PULL --FF-ONLY
→ LOCAL AUTOMATED GATE
→ MANUAL VISUAL/DATA QA
→ LOCAL PUBLISH E2E
→ EXPLICIT OWNER APPROVAL
→ PRODUCTION BACKUP/DEPLOY
→ PRODUCTION VERIFICATION
→ UPDATE DOCS
```

قواعد ثابت:
- قابلیت سالم Mature باید Extend/Patch/Wrap شود؛ بازنویسی موازی بدون دلیل ممنوع.
- Bugfix بدون Regression Test کامل نیست.
- Source Code دائمی روی Production ویرایش نمی‌شود.
- هیچ ZIP/Patch/PS1/Python/Source مستقل از Repository برای اجرا مبنا نیست.
- Dirty Local/Host = STOP/INSPECT؛ `reset --hard`, `git clean`, حذف DB/.env/media/persistent data Quick Fix نیست.
- Migration معمول Additive-first؛ destructive change فقط با Target/Backup/Rollback verified و Phase مستقل.
- Secret/API key/token/password در Git/log/audit/chat ذخیره نمی‌شود.

Policy: `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`.

---

## 2) مسیرهای واقعی ثبت‌شده

### Windows
```text
Project:             D:\projects\3DPrintHub
Venv:                D:\projects\3DPrintHub\.venv
Catalog Center:      D:\projects\3DPrintHub\catalog_center
Django SQLite:       D:\projects\3DPrintHub\db.sqlite3
Catalog persistent:  D:\projects\3dprinthub-catalog-manager
Catalog SQLite:      D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
Legacy retained:     D:\projects\3dprinthub_catalog_center
Backups:             D:\projects\3dprinthub-backups
```

### Production
```text
Project:       /home/sfkilvrs/3dprinthub
Venv:          /home/sfkilvrs/virtualenv/3dprinthub/3.12
Database:      MySQL sfkilvrs_EmiAdmin_3dprinthub
Static:        /home/sfkilvrs/public_html/static
Media:         /home/sfkilvrs/public_html/media
Private media: /home/sfkilvrs/3dprinthub/private_media
```

Production DB Guard:
- vendor باید `mysql` باشد.
- DB name باید دقیقاً production DB باشد.
- SQLite fallback در Production migration = STOP.
- قبل از Migration Production، backup واقعی الزامی است.

---

## 3) Epic49 Path

```text
49.2A
→ 49.2B
→ 49.2C
→ Epic49 Unified Product/Slider Sync
→ Persian Sales Hero
→ Dual Publish Targets
→ Desktop Options
→ 49.3A Readiness
→ 49.3B Guided AI / Hero / Diagnostics
→ 49.3C Operator Recovery
→ 49.3C-1 Persian Content Integrity
→ 49.3D Workflow Hardening
→ 49.3D.1 Windows Runner Hotfix
→ 49.3E AI Task Recovery
→ 49.3F Product Intelligence / Dynamic Pricing / AI UX
→ 49.3F Runtime Trace Redaction
→ 49.3F.1 Native stderr Capture Hotfix
→ 49.3G Workspace Usability + AI Provenance
→ 49.3H SEO Execution + AI Cost + Controlled Image Intake
→ 49.3I Discovery Review + Lightweight Product List + Explicit Pricing Modes
```

Current Phase:
**49.3I** — GitHub implementation + CI SUCCESS; Windows Local Gate/QA pending.

---

## 4) End-to-End Architecture

```text
Employee
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite
  ↓
Discovery Review / Product Workspace / Images / AI / SEO / Price / Hero
  ↓
Batch / Bridge
  ├─ Local Publish → Local Django SQLite
  └─ Production Publish → verified FTP/Bridge/Importer
                           ↓
                     Django Product
                     ProductCatalogProfile
                     HomepageHeroSlide
                           ↓
                     Store / Home / Cart / Checkout
```

Reverse sync:
`Django Admin edit → revision increment → Bridge → Windows refresh/compare`.

Protection:
- stale Windows write → revision conflict / fail-closed
- Product and Hero revisions independent
- `batch_uuid + source_hash` idempotency
- Local and Production targets separate

---

## 5) Protected Product Workspace Contracts

Canonical stages remain available and non-blocking for editing; Readiness guides the operator, Production Publish remains fail-closed.

Protected capabilities:
- Persian source/editor integrity
- Product SEO + Slider SEO separation
- exact selected-image identity
- Image SEO selected-only + text-only
- Material/Color options
- Hero media/effect/timing/revision
- AI provider/model persistence + diagnostics
- AI provenance/manual override
- Local Publish exact preflight
- server revision/idempotency

---

## 6) AI / Diagnostics Baseline

Providers:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

Rules:
- raw model ID persisted; decorated label not persisted
- active provider/model single source of truth
- API key only from secure store/environment
- request ID/tokens/cost logged where supported
- unknown provider cost is never invented
- Bearer/secret redaction regression-protected
- AI cannot invent legal/license/price/inventory/material/color facts
- operator-owned fields stay protected

`$django-admin-expert`: no matching Plugin/Skill available in this session; do not claim installed.

---

## 7) Image Contract — Phase49.3H+

Current canonical acquisition limit:
- default: **10**
- hard max: **20**
- operator chooses per product/intake
- cap applies to persisted/selected/downloaded images
- reaching cap moves workflow to next product; does not stop batch discovery

Image SEO privacy:
- selected images only
- no image bytes/files/URLs sent to AI
- slot→URL mapping local only
- unselected metadata preserved

---

## 8) Pricing Contract — Phase49.3I

Operator modes are explicitly separated:

### Fixed
Exact amount such as `1,200,000 تومان`.
- `price_min == price_max`
- final price true

### Range
Explicit range such as `200,000..500,000 تومان`.
- existing price-range/consultation behavior
- not formula pricing
- `pricing_strategy=range`
- `price_mode=range`

### Dynamic / Formula
Existing mature Variant engine:
- material grams/rates
- part/support weight + support multiplier
- print minutes/hourly rate
- supervision rate
- assembly/extras where configured

Dynamic Source of Truth remains:
`ProductVariant.price_breakdown()` + cached Variant unit price.

Acceptance baseline:
```text
PLA = 2,600,000/kg = 2,600/g
Part = 100g
Support = 50g × 2
Chargeable = 200g
Material = 520,000
Print = 3h × 150,000 = 450,000
Supervision = 3h × 50,000 = 150,000
Expected = 1,120,000 تومان before extras/shipping
```

Product Detail/Cart/Checkout نباید calculator موازی بسازند.

---

## 9) Phase49.3I Discovery Contract

Root Cause قدیمی:
`mode=search` لینک صریح اپراتور را نادیده می‌گرفت و `listing[:1]` پیش‌فرض را اسکن می‌کرد.

Contract جدید:
1. explicit HTTP(S) search/listing URL = authoritative.
2. Stage 1 فقط Preview Candidate:
   - one thumbnail
   - source title
   - external/source identity
   - product URL
3. هیچ full extraction قبل از approval.
4. Stage 2 فقط approved candidate را کامل دریافت می‌کند.
5. image limit 1..20 اعمال می‌شود.
6. Archive/Not Needed = blocked identity without full fetch.
7. existing/blocked identity = duplicate guard before full fetch.

MakerWorld regression examples:
- `2834255`
- `2845731`
- search URL: `https://makerworld.com/en/search/models?keyword=cake+stand`

---

## 10) Source Text Safety — Phase49.3I

روی scraped/source text قبل از persistence:
- Unicode normalization
- Latin/English/digits/common punctuation/technical symbols retained
- CJK/Cyrillic/unexpected scripts/emoji removed
- URL/source identity unchanged
- Persian `_fa` editorial fields untouched
- no historical mass rewrite

---

## 11) Product List — Phase49.3I

Main work list:
- lightweight thumbnail + display name
- embedded giant detailed editor hidden from work-list surface
- canonical action: `صفحه محصول / ویرایش کامل`
- all detailed editing remains in Product Workspace
- compatibility code/DB/workflow preserved

---

## 12) Database / Migration State

Important applied Windows migrations:
- `store.0031` ✅
- `store.0032` ✅
- `website.0022` ✅
- `store.0033` ✅
- `website.0023` ✅

49.3G:
- no Django migration
- local additive AI provenance columns

49.3H:
- no Django migration

49.3I:
- no Django migration
- local additive Candidate Review table only
- no reset/drop/truncate/delete

Production Phase49.3C..49.3I remains not deployed/not approved.

---

## 13) Phase49.3I CI Incident

Initial CI-only PR #41:
- new Catalog tests PASS
- Django migration gate FAIL
- proposed `store.0034_alter_productcatalogprofile_pricing_strategy`

Root Cause:
- first range implementation mutated Django runtime field `choices`
- Django choices are migration-state metadata

Correct Fix:
- do not mutate migration-owned choices
- existing `CharField(max_length=20)` stores raw semantic `range`
- Windows exposes operator modes
- server sync persists range semantics without model metadata mutation

Prevention:
Django field metadata changes are migration state even if SQL column type stays unchanged.

Recorded as `ERR-49-015`.

---

## 14) Final Phase49.3I GitHub Validation

Runtime/base SHA:
`9d462f1ec12b00727c96acf9d4f59b4723d676b4`

CI-only final PR #42: closed / not merged.

Runs:
- Phase49.3I dedicated `32569551060` — SUCCESS
- Phase49.3H regression `32569551053` — SUCCESS
- Phase49.3G regression `32569551048` — SUCCESS
- Full Phase49 + Full Django `32569551034` — SUCCESS

Validated:
- runner syntax/chain/Production guard
- compile
- exact search URL
- preview/no-full-fetch
- approve/archive/dedupe
- source text safety
- lightweight product list
- Fixed/Range/Dynamic pricing
- Django check + no migration drift
- launcher markers
- existing 49.3H / 49.3G protections
- full Epic49 regressions
- full Django suite

---

## 15) Canonical Runners / CI

```text
RUN_PHASE49_3D_LOCAL_GATE.ps1
RUN_PHASE49_3E_LOCAL_GATE.ps1
RUN_PHASE49_3F_LOCAL_GATE.ps1
RUN_PHASE49_3G_LOCAL_GATE.ps1
RUN_PHASE49_3H_LOCAL_GATE.ps1
RUN_PHASE49_3I_LOCAL_GATE.ps1
```

Current runner:
`D:\projects\3DPrintHub\RUN_PHASE49_3I_LOCAL_GATE.ps1`
Version: `49.3I.0`

Runner chain:
`49.3I → 49.3H → 49.3G → 49.3F.1 → 49.3E → 49.3D/base gates`.

CI:
- `.github/workflows/phase49-epic-ci.yml`
- `.github/workflows/phase49-3g-workspace-usability-ci.yml`
- `.github/workflows/phase49-3h-ci.yml`
- `.github/workflows/phase49-3i-ci.yml`

---

## 16) Known Separate/Open Items

- `/api/v1/catalog/sitemap/` local 404: investigate route/client Root Cause before final Epic closure.
- CKEditor4 warning/debt: separate scope.
- `store.W026` realtime/in-memory warning: production architecture scope.
- Pillow `Image.getdata()` deprecation: non-blocking debt.
- Google membership credentials warning: expected when credentials intentionally absent in CI.

---

## 17) Current Gate — Windows Phase49.3I

### Gate A — Git / Automated
- [ ] close running project processes if runner reports conflict
- [ ] `git status --short` empty; dirty → STOP/INSPECT
- [ ] `git fetch --prune origin`
- [ ] switch Epic branch
- [ ] `git pull --ff-only`
- [ ] verify exact expected HEAD
- [ ] run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`
- [ ] chained previous gates PASS
- [ ] dedicated 49.3I tests PASS
- [ ] Django no-migration gate PASS
- [ ] final worktree clean

### Gate B — Manual Discovery QA
- [ ] MakerWorld Search mode + exact `cake+stand` URL
- [ ] Candidate list relevant to cake stand
- [ ] before approval only one thumbnail/basic identity; no full row fetch
- [ ] approve one candidate with image limit 10; persisted/selected/downloaded <=10
- [ ] archive another candidate; blocked without full fetch
- [ ] repeat same search; imported/blocked identities do not full-fetch again
- [ ] source text no CJK/unexpected script; URLs exact; Persian editorial untouched

### Gate C — UI/Pricing QA
- [ ] Products page lightweight image + name
- [ ] Product Workspace opens via one clear action
- [ ] Fixed example `1,200,000`
- [ ] Range example `200,000..500,000`
- [ ] Formula pricing uses mature dynamic engine
- [ ] 49.3H cost/result/image-limit protections still work
- [ ] 49.3G manual override/provenance still works

### Gate D — Local E2E
- [ ] one real **LOCAL PUBLISH ONLY**
- [ ] Local Django Product/Profile/Hero/Home/Store/Admin verify

### Gate E — Owner Approval
- [ ] explicit user approval

### Gate F — Production
Only after Gate E with verified host state + backup + rollback + MySQL checks.

---

## 18) Current Status — 2026-08-22

**Phase:** 49.3I  
**GitHub implementation:** COMPLETE ✅  
**Dedicated CI:** SUCCESS ✅  
**Full Phase49/Django CI:** SUCCESS ✅  
**Django migration 49.3I:** NONE ✅  
**CI migration bug:** ROOT CAUSE FIXED + REGRESSION ✅  
**Canonical runner:** `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.0 ✅  
**Windows Automated Gate:** PENDING  
**Manual Discovery/Product/Pricing QA:** PENDING  
**Local Publish E2E:** PENDING  
**Owner Production approval:** PENDING  
**Production:** UNTOUCHED / NOT APPROVED

### قدم بعدی دقیق

```text
Windows D:\projects\3DPrintHub
→ git status --short
→ dirty? STOP/INSPECT
→ git fetch --prune origin
→ git switch epic/phase49-unified-product-slider-sync
→ git pull --ff-only origin epic/phase49-unified-product-slider-sync
→ verify pulled HEAD
→ .\RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp
→ Automated Local PASS
→ Manual MakerWorld/Archive/Dedupe/Product/Pricing QA
→ one LOCAL PUBLISH ONLY
→ Local Django E2E
→ explicit owner approval
→ Production plan
```

---

## 19) Definition of Done

A Phase is not complete merely because code exists.

```text
Code + regression tests
+ focused CI
+ full regression CI
+ migration safety
+ Windows Local automated gate
+ Manual Visual/Data QA
+ Local E2E
+ explicit owner approval
+ Production backup/deploy/verification when production-bound
+ documentation closure
```

Until Windows/Local acceptance, Phase49.3I status remains `WINDOWS QA PENDING`.
