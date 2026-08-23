# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.13 — Windows URL Paste + Approved Batch Full-Fetch Recovery`  
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
→ 49.3I.6 Secure Credential Persistence
→ 49.3I.7 Preview/Provider Hub Recovery
→ 49.3I.8 Observable All-Fields AI
→ 49.3I.9 AI Refresh/SEO Source Completion
→ 49.3I.10 AI Trace/Safe Title Retry
→ 49.3I.11 Provider Schema/Trace/Busy Recovery
→ 49.3I.12 Exact-Page Operator/Single Product/Image Fit
→ 49.3I.13 Windows Paste/Approved Batch Full-Fetch Recovery
```

Current status: **49.3I.13 merged + all required GitHub CI SUCCESS; Windows release rerun pending; Production untouched.**

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
Visible Preview Discovery
  ↓
Candidate Review: one thumbnail + basic identity
  ↓
Approve / Archive
  ↓
Approved Batch Full Fetch
  ↓
Existing RichPageExtractor in background/headless mode
  ↓
Product Workspace
  ↓
AI Task Center / Exact Schema / Trace / Pricing / Image Pipeline
  ↓
LOCAL PUBLISH ONLY
  ↓
Local Django SQLite + Store/Admin E2E
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

Direct Product URL مسیر جداگانه دارد، با `model_url_pattern` Verify می‌شود و می‌تواند browser headed تنظیم‌شده را برای login/CAPTCHA recovery حفظ کند.

---

## 5) Discovery / Business Workflow — 49.3I.13

```text
Exact Search / Listing / Category URL
→ Paste by Ctrl+V / Shift+Insert / Right-click / Paste Link
→ "کشف لینک‌های همین صفحه"
→ Visible Running State
→ Preview Candidate
→ one thumbnail + basic identity/title/url
→ Operator Approve or Archive
→ Approved only: mature Full Fetch
→ Batch browser = background/headless
→ selected image limit 1..20 (default 10)
→ Product Workspace
```

Direct Product:
```text
Exact Product URL
→ model_url_pattern verified
→ "دریافت محصول تکی"
→ mature direct intake
→ configured headed behavior preserved
→ Product Workspace
```

قواعد:
- لینک صریح اپراتور authoritative است.
- Preview و Archive حق Full Fetch ندارند.
- Dedupe: source + external id + normalized URL.
- Candidate failure reason باید از `last_error` برای اپراتور قابل مشاهده باشد.
- approved batch نباید برای هر ردیف browser visible باز و بسته کند.
- original direct browser setting بعد از batch restore می‌شود.

---

## 6) Product Workspace / AI / Pricing Contracts

Images:
- viewport ثابت `228x171`,
- `ImageOps.contain` + letterbox,
- crop/stretch ممنوع.

AI:
- mature All-Fields Task Center,
- immediate first-paint,
- sanitized request/response/error trace,
- 90s title / 210s full-AI watchdog,
- stale-result safety,
- AI-owned refresh + manual override protection,
- exact provider JSON Schema + one repair,
- compact model trace,
- abort releases busy state immediately.

Pricing:
- Fixed,
- Range,
- Formula/Dynamic,
- Range هرگز Formula را اجرا نمی‌کند.

---

## 7) Latest Validation — 49.3I.13

PR #59 merged after CI.
Validated feature head: `b47793c42d807285efbd8d3e005f9979856c4878`.
Epic merge commit: `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`.

Runs:
- Phase49.3I `32633932308` — SUCCESS
- Phase49.3H `32633932302` — SUCCESS
- Phase49.3G `32633932340` — SUCCESS
- Full Phase49 + Full Django `32633932224` — SUCCESS

Verified:
- runner 49.3I.13,
- ASCII/live-Git guard,
- compile,
- Windows clipboard query preservation,
- approved-batch headless policy + original-setting restore,
- Candidate Error Detail contract,
- no duplicate crawler/extractor,
- prior Discovery/AI/provider/SEO/image/pricing regressions,
- no migration,
- Windows Catalog tests,
- Full Django suite.

Production: UNTOUCHED.

---

## 8) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.
Current Windows incident: **ERR-49-031**.

- ERR-49-019: fixed Chat SHA ممنوع؛ live fetched snapshot.
- ERR-49-020: pixel images must not use Tk text-unit sizing.
- ERR-49-030: final UX boundary must expose real discovery state.
- ERR-49-031: business-critical URL paste must be explicit; approved batch must not inherit interactive headed-browser default; persisted candidate error must be visible.

---

## 9) Employee Release Gate — Next

1. Catalog Center بسته باشد.
2. worktree clean.
3. live `git fetch --prune origin` + ff-only pull current Epic.
4. Runner `49.3I.13` با `-LaunchApp`.
5. چهار روش Paste روی URL تست شود.
6. exact MakerWorld `cake+stand` Search URL → Preview.
7. candidate links قبل از Full Fetch دیده شوند.
8. حداقل 2 candidate → Approve → Full Fetch؛ هیچ browser visible برای هر محصول باز نشود.
9. اگر row خطا شد `جزئیات خطای انتخابی` دلیل دقیق را نشان دهد.
10. Direct Product URL مستقل تست شود.
11. Stop/live state + image fit + AI/provider/model/image-limit/pricing regression.

اگر PASS شد کارمندها می‌توانند controlled Catalog data entry را شروع کنند.

بعد:
- دقیقاً یک `LOCAL PUBLISH ONLY`
- Local Django E2E
- verify title/SEO/source/images/pricing
- explicit owner approval

---

## 10) Production Gate

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

## 11) Next Product Phase — Store ZarinPal Checkout

Phase30 ZarinPal برای Quote payment بالغ است، ولی Store cart checkout هنوز bank-transfer/manual-payment است.

Next implementation after Catalog acceptance:
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

---

## 12) Exact Next Step

Windows باید current Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.13 را اجرا کند. Local Publish و Production تا PASS این rerun ممنوع است.
