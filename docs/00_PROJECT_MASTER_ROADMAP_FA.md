# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.11 — Provider Schema + Trace/Busy Runtime Recovery`  
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
```

Current status: **49.3I.11 GitHub CI SUCCESS; Windows release QA pending; Production untouched.**

---

## 4) معماری عملیاتی

```text
Operator
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite + Windows Credential Store
  ↓
Search/Listing Discovery Preview
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

Production هیچ‌وقت Source of Development نیست.

---

## 5) Discovery / Business Workflow

```text
Exact Search / Listing / Category URL
→ Preview Candidate
→ one thumbnail + basic identity/title/url
→ Operator Approve or Archive
→ Approved only: mature Full Fetch
→ selected image limit 1..20 (default 10)
→ Product Workspace
```

قواعد:
- لینک صریح اپراتور authoritative است.
- Source `model_url_pattern` مرز Product URL و Group/Search/Category است.
- Preview و Archive حق Full Fetch ندارند.
- Dedupe: source + external id + normalized URL.
- Source text sanitation بدون آسیب به URL/Persian editorial fields.

---

## 6) Provider / Secret Contract

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

## 7) AI Execution Contract — 49.3I.11

### Preserved from 49.3I.8–10
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
- source website remains publisher/source identity.

### 49.3I.11 / ERR-49-029
Owner trace proved AvalAI could return HTTP 200 + useful Persian content but violate the application schema (`seo_title` vs `seo_title_fa`, `seo_description` vs `seo_description_fa`, wrong `content_notes` type, missing required keys).

Fix:
- AvalAI/OpenRouter receive the real JSON Schema,
- strict schema format preferred and exact schema always included in prompt,
- bounded compatibility fallback,
- schema validation before persistence,
- one repair request for a schema-invalid valid JSON,
- second schema failure becomes a precise visible error,
- explicit selected model runs directly,
- model catalog cached within request window,
- duplicate model probes reduced,
- `/models` trace summarized to keep Tk responsive,
- Stop Waiting/watchdog/stale abort immediately releases Workspace busy flags,
- new Provider/Model request can start immediately,
- late old output remains stale/non-applicable.

---

## 8) Product Workspace / Explorer / Pricing

Preserved:
- Product Workspace = canonical detailed editor.
- Explorer = visual/lightweight browse/select/preview surface.
- selection feedback-loop guard.
- safe local queue actions.

Pricing modes مستقل:
- Fixed
- Range
- Formula/Dynamic

Range نباید Formula را اجرا کند.

---

## 9) Latest Validation

PR #57 merged after CI.
Validated feature head: `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`.
Epic merge commit: `41d37d56437765119b9bb274037e9af7a5defbbe`.

Runs:
- Phase49.3I `32628666588` — SUCCESS
- Phase49.3H `32628666600` — SUCCESS
- Phase49.3G `32628666558` — SUCCESS
- Full Phase49 + Full Django `32628666582` — SUCCESS

Verified runner 49.3I.11, ASCII/live-Git guard, compile, exact owner schema regression, strict provider schema, one repair, compact model trace, abort busy release, stale-result safety, prior AI/source/provider/Explorer/pricing/SEO regressions, no migration, Windows Catalog tests and Full Django suite.

Production: UNTOUCHED.

---

## 10) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.
Latest relevant: ERR-49-013 through ERR-49-029, especially 026/027/028/029 for current AI behavior.

---

## 11) Employee Release Gate — Today

1. Catalog Center بسته باشد.
2. worktree clean.
3. live `git fetch --prune origin` + ff-only pull current Epic.
4. Runner `49.3I.11` با `-LaunchApp`.
5. همان محصول/مدل AvalAI که قبلاً schema غلط داد دوباره اجرا شود.
6. schema exact یا حداکثر یک repair request دیده شود.
7. `/models` trace خلاصه باشد و UI responsive بماند.
8. Stop Waiting → تغییر Provider/Model → درخواست جدید فوراً قابل اجرا باشد.
9. پاسخ دیرهنگام قبلی نباید روی محصول اعمال شود.
10. title / All-Fields trace + watchdogها بررسی شوند.
11. low-image source refetch offer.
12. MakerWorld Preview → Approve → Full Fetch.
13. Provider/model/FTP/Bridge persistence.
14. Product open/selection + Fixed/Range/Formula.

اگر PASS شد کارمندها می‌توانند controlled Catalog data entry را شروع کنند.

بعد:
- دقیقاً یک `LOCAL PUBLISH ONLY`
- Local Django E2E
- verify title/SEO/source/images/pricing
- explicit owner approval

---

## 12) Payment Track

Phase30 ZarinPal برای Quote payment بالغ است، ولی Store cart checkout هنوز bank-transfer/manual-payment است. Store gateway request/callback/verify کامل نشده است.

Next urgent implementation after Catalog release:
- reuse mature ZarinPal security semantics,
- server-owned amount,
- idempotent Store payment attempt,
- Authority match,
- server-to-server Verify,
- duplicate callback safety,
- finalize inventory/order exactly once,
- keep manual bank transfer,
- Sandbox E2E before live activation,
- owner-approved low-value live test.

Current supported online provider: ZarinPal.

---

## 13) Exact Next Step

Windows باید current Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.11 را اجرا کند. تا قبل از Windows acceptance، Local Publish/Production/live payment ممنوع است.
