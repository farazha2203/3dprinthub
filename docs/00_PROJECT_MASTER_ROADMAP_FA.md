# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.12 — Observable Exact-Page Discovery + Single-Product Intake + Workspace Image Fit`  
**Windows Operator:** Catalog Center 8.7.1  
**Backend:** Django / Python  
**Production:** تا Windows QA + Local Publish E2E + تأیید صریح مالک پروژه ممنوع.

---

## 1) قانون مادر

```text
READ DOCS
→ VERIFY REAL STATE
→ CHECK PREVIOUS ERRORS
→ IMPLEMENT ON GITHUB
→ CI
→ WINDOWS PULL --FF-ONLY
→ LOCAL AUTOMATED GATE
→ MANUAL VISUAL/DATA/INTERACTION QA
→ LOCAL PUBLISH E2E
→ EXPLICIT OWNER APPROVAL
→ PRODUCTION BACKUP/DEPLOY
→ PRODUCTION VERIFICATION
→ UPDATE DOCS
```

قواعد ثابت:
- Mature behavior با Extend/Patch/Wrap اصلاح می‌شود؛ بازنویسی موازی بدون دلیل ممنوع.
- Bugfix بدون Regression Test کامل نیست.
- Source دائمی روی Production ویرایش نمی‌شود.
- ZIP/Patch/Source مستقل از GitHub مسیر تحویل نیست.
- Dirty Local/Host = STOP/INSPECT؛ reset/stash/delete Quick Fix ممنوع.
- Migrationها Additive-first؛ destructive فقط با Target/Backup/Rollback verified.
- Secret/API key/token/password در Git/log/chat/SQLite ذخیره نمی‌شود.
- SHA ثابت Chat Source of Truth Branch متحرک نیست؛ Snapshot بعد از `git fetch` واقعی Verify می‌شود.

Policy: `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`.

---

## 2) مسیرهای ثبت‌شده

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

قبل از هر Production operation باید `docs/PATHS.md`، `docs/HOST_CONSTRAINTS.md`، DB vendor/name واقعی، Backup، Rollback و Branch/Commit واقعی دوباره Verify شوند.

---

## 3) Epic49 Path

```text
49.2A → 49.2B → 49.2C
→ Epic49 Unified Product/Slider Sync
→ Persian Sales Hero
→ Dual Publish Targets
→ Desktop Options
→ 49.3A Readiness
→ 49.3B Guided AI/Hero/Diagnostics
→ 49.3C Operator Recovery
→ 49.3D Workflow Hardening
→ 49.3E AI Task Recovery
→ 49.3F Product Intelligence/Dynamic Pricing/AI UX
→ 49.3G Workspace Usability/AI Provenance
→ 49.3H SEO Execution/AI Cost/Controlled Image Intake
→ 49.3I Discovery Review/Product Explorer/Explicit Pricing
→ 49.3I.1 Windows PS5.1 Encoding Guard
→ 49.3I.2 Real UX87 Gallery/AI First-Paint
→ 49.3I.3 Live GitHub Snapshot Guard
→ 49.3I.4 Explorer/Source URL Routing
→ 49.3I.5 Selection Loop Guard/Compact Metadata
→ 49.3I.6 Initial Secure Credential Persistence
→ 49.3I.7 Preview/Provider Hub Recovery
→ 49.3I.8 Observable All-Fields AI
→ 49.3I.9 AI Refresh/SEO Source Completion
→ 49.3I.10 AI Trace/Safe Title Retry
→ 49.3I.11 Provider Schema/Trace/Busy Runtime Recovery
→ 49.3I.12 Observable Exact-Page Discovery/Single Product/Image Fit
```

Current status: **49.3I.12 merged + all required GitHub CI SUCCESS; Windows release QA pending; Production untouched.**

---

## 4) معماری عملیاتی

```text
Operator
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite + Windows Credential Store
  ↓
Exact Search/Listing/Category URL
  ↓
Visible Preview Discovery (live state/progress/elapsed/current URL)
  ↓
Candidate Review: one thumbnail + basic identity
  ↓
Approve / Archive
  ↓
Approved Full Fetch (mature extractor)
  ↓
Product Workspace
  ↓
Mature AI Task Center / Exact Schema Adapter / Trace Console / Pricing / Image Pipeline
  ↓
LOCAL PUBLISH ONLY
  ↓
Local Django SQLite
  ↓
Local Store/Admin/E2E Verification
  ↓
Explicit Owner Approval
  ↓
GitHub-approved Commit
  ↓
Production Host pulls from GitHub
  ↓
MySQL + Passenger/LiteSpeed
  ↓
Production Verification
```

Direct Product URL مسیر جداگانه دارد و با `model_url_pattern` منبع Verify می‌شود.

Production هیچ‌وقت Source of Development نیست.

---

## 5) Discovery / Business Workflow — 49.3I.12

```text
Exact Search / Listing / Category URL
→ "کشف لینک‌های همین صفحه"
→ Visible Running State
→ Preview Candidate
→ one thumbnail + basic identity/title/url
→ Operator Approve or Archive
→ Approved only: mature Full Fetch
→ selected image limit 1..20 (default 10)
→ Product Workspace
```

Direct Product:
```text
Exact Product URL
→ model_url_pattern verified
→ "دریافت محصول تکی"
→ mature direct intake
→ Product Workspace
```

قواعد:
- لینک صریح اپراتور authoritative است.
- Source `model_url_pattern` مرز Product URL و Group/Search/Category است.
- Preview و Archive حق Full Fetch ندارند.
- Dedupe: source + external id + normalized URL.
- Source text sanitation بدون آسیب به URL/Persian editorial fields.
- Worker state باید برای اپراتور observable باشد: running/stopping/done + elapsed + target.

---

## 6) Product Workspace Image Contract — 49.3I.12

- Product Workspace همچنان editor اصلی است.
- کارت تصویر باید pixel contract داشته باشد، نه Tk text-unit sizing.
- viewport ثابت: `228x171`.
- `ImageOps.contain` + letterbox.
- crop/stretch ممنوع.
- landscape و portrait باید در viewport یکسان و قابل مقایسه نمایش داده شوند.

---

## 7) Provider / Secret Contract

Source of Truth امن: **Windows Credential Store / environment**.

Providers:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

- real Provider-card fields hydrate securely,
- model catalogs load through mature adapters,
- FTP password + Bridge token preserve secure persistence,
- Secret در SQLite/Git/source/log trace payload ذخیره نمی‌شود.

---

## 8) AI Execution Contract — Preserved Through 49.3I.12

- real bottom All-Fields uses mature Task Center,
- immediate first-paint,
- scrollable sanitized request / response / diagnostics tabs,
- elapsed timer + Stop Waiting,
- title watchdog 90s,
- All-Fields watchdog 210s,
- cancel/timeout stale-result discard,
- explicit rerun refreshes AI-owned fields but protects proven manual overrides,
- generic product titles rejected,
- source-grounded Persian ecommerce/SEO content,
- AvalAI/OpenRouter receive actual JSON Schema,
- exact schema validation before persistence,
- one bounded repair request,
- compact `/models` trace,
- Stop Waiting/watchdog/stale abort immediately releases busy state,
- late old output remains stale/non-applicable.

---

## 9) Product Explorer / Pricing

Preserved:
- Explorer = visual/lightweight browse/select/preview surface.
- Product Workspace = canonical detailed editor.
- selection feedback-loop guard.
- safe local queue actions.

Pricing modes مستقل:
- Fixed
- Range
- Formula/Dynamic

Range نباید Formula را اجرا کند.

---

## 10) Latest Validation — 49.3I.12

PR #58 merged after CI.
Validated feature head: `2a9442055d33777f675ccd3ebe11de8419bfb2b3`.
Epic merge commit: `24d5b8fdddb97fbcc4c07efa7d6f1d78a0ffb225`.

Runs:
- Phase49.3I `32631604990` — SUCCESS
- Phase49.3H `32631604930` — SUCCESS
- Phase49.3G `32631604945` — SUCCESS
- Full Phase49 + Full Django `32631604928` — SUCCESS

Verified:
- runner 49.3I.12,
- ASCII/live-Git guard,
- compile,
- exact-page/product URL classification,
- UX87 final composition-boundary mounting,
- candidate Treeview mature renderer compatibility,
- live status/stop contracts,
- 228x171 contain image fit,
- prior AI schema/trace/refresh/manual override/source/provider/Explorer/pricing/SEO regressions,
- no migration,
- Windows Catalog tests,
- Full Django suite.

Production: UNTOUCHED.

---

## 11) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.
Latest relevant: ERR-49-013 through ERR-49-030, especially:
- 017: wrong visible UX composition boundary,
- 020: pixel image vs text-unit sizing,
- 026–029: AI execution/schema/trace behavior,
- 030: exact-page discovery backend success but missing visible operator state.

---

## 12) Employee Release Gate — Today

1. Catalog Center بسته باشد.
2. worktree clean.
3. live `git fetch --prune origin` + ff-only pull current Epic.
4. Runner `49.3I.12` با `-LaunchApp`.
5. exact MakerWorld `cake+stand` Search URL با دکمه exact-page.
6. badge/progress/elapsed/current URL دیده شود.
7. candidate links قبل از Full Fetch دیده شوند.
8. یک candidate → Approve → Full Fetch.
9. یک Product URL واقعی → single-product intake.
10. Stop feedback دیده شود.
11. Product Workspace images → portrait/landscape equal 228x171 contain cards.
12. AI/provider/model/image-limit/pricing regression.

اگر PASS شد کارمندها می‌توانند controlled Catalog data entry را شروع کنند.

بعد:
- دقیقاً یک `LOCAL PUBLISH ONLY`
- Local Django E2E
- verify title/SEO/source/images/pricing
- explicit owner approval

---

## 13) Production Gate

بعد از Windows QA + Local Publish E2E + تأیید صریح مالک:
1. read-only host state verify,
2. project root/branch/commit verify,
3. clean/safe host state,
4. `.env`/persistent import state backup,
5. `manage.py check`,
6. `makemigrations --check --dry-run`,
7. verify `connection.vendor == mysql` + exact DB name,
8. migration plan,
9. backup before migration if any,
10. collectstatic,
11. Passenger restart,
12. HTTP/store/admin/product/media smoke/data verification,
13. docs update.

---

## 14) Next Product Phase — Store ZarinPal Checkout

Phase30 ZarinPal برای Quote payment بالغ است، ولی Store cart checkout هنوز bank-transfer/manual-payment است.

Next urgent implementation after Catalog acceptance:
- reuse mature ZarinPal security semantics,
- server-owned amount,
- idempotent Store payment attempt,
- Authority match,
- server-to-server Verify,
- duplicate callback safety,
- finalize inventory/order exactly once,
- keep manual bank transfer,
- Sandbox E2E before live activation,
- secrets outside Git,
- owner-approved low-value live test.

Current supported online provider: ZarinPal.

---

## 15) Exact Next Step

Windows باید current Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.12 را اجرا کند. اگر PASS شد، بدون ایجاد Hotfix جدید یک Local Publish E2E انجام می‌شود؛ بعد از تأیید مالک وارد Production gate و سپس Store ZarinPal phase می‌شویم.
