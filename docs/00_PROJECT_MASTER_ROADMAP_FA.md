# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.14 — Restore Mature Scan Controls + Single-Product Route`  
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
- افزودن UI جدید مجوز Hide/Replace/Rebind کردن رفتار سالم قبلی نیست.
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
→ 49.3I.13 Windows Paste/Approved Batch Recovery
→ 49.3I.14 Mature Scan Controls/Single-Product Route Restoration
```

Current status: **49.3I.14 implemented on PR #60; all required feature-head CI SUCCESS; focused Windows release QA pending; Production untouched.**

---

## 4) معماری عملیاتی دریافت محصول

دو مسیر باید همزمان وجود داشته باشند:

### Mature acquisition path
```text
Operator
  ↓
Top Source / Mode / Method / URL / Query controls
  ↓
شروع اسکن
  ↓
Original BaseApp start_scan / _scan_worker
  ↓
Mature discovery/queue/classic collector
  ↓
Product Workspace
```

### Review path
```text
Exact Search/Listing/Category URL
  ↓
Visible Preview Discovery
  ↓
Candidate Review: one thumbnail + basic identity
  ↓
Approve / Archive
  ↓
Approved Full Fetch
  ↓
Product Workspace
```

قانون دائمی: مسیر دوم حق حذف، مخفی‌کردن یا Rebind کردن مسیر اول را ندارد مگر با درخواست صریح مالک پروژه.

---

## 5) 49.3I.14 — علت و قرارداد اصلاح

Windows QA بعد از 49.3I.13 نشان داد:
- `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها` در 49.3I.12 عمداً Hide شده بودند.
- Preview layer متد `App87.start_scan` را هم جایگزین کرده بود؛ بنابراین صرفاً Visible کردن دکمه کافی نبود.
- اکشن جدید `دریافت محصول تکی` به اجبار Rich Direct Intake را اجرا می‌کرد و برای MakerWorld Product واقعی `400767` خطای `RuntimeError: HTTP 403` داد.
- مسیر Mature BaseApp هنوز در Repository موجود بود و همان مسیری است که مالک قبلاً سالم گزارش کرده بود.

اصلاح 49.3I.14:
- actionهای Mature بالا Restore می‌شوند.
- `شروع اسکن` به BaseApp mature worker وصل می‌شود.
- اکشن جدید `دریافت محصول تکی` بعد از Product URL validation، `mode=single` می‌گذارد و همان mature worker را اجرا می‌کند.
- `دریافت هوشمند از لینک` همچنان به‌صورت Optional جداگانه باقی می‌ماند.
- Preview/Approve/Archive/Paste/Error Detail حفظ می‌شوند.
- crawler/extractor جدید ساخته نشده است.

Canonical error: `ERR-49-032`.

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

## 7) Latest Validation — 49.3I.14 Feature Runtime

PR #60: OPEN at documentation time.
Runtime fix commit: `bb6f456b50c1e12bbf6fc5c6b6cc3289f35ee6c8`.

Runs:
- Phase49.3I.14 Legacy Scan Restore `32636391530` — SUCCESS
- Phase49.3I `32636391489` — SUCCESS
- Phase49.3H `32636391571` — SUCCESS
- Phase49.3G `32636391563` — SUCCESS
- Full Phase49 + Full Django `32636391518` — SUCCESS

Initial targeted CI correctly caught a resolver bug (`preview-started` selected instead of `legacy-started`). The failed command was not repeated unchanged; code changed to resolve the deepest project `start_scan`, then fresh CI passed.

Verified:
- mature scan route resolution,
- manual single-product route through mature worker,
- preserved legacy action contract,
- Preview/Approve/Paste regressions,
- compile,
- Windows PowerShell safety gate,
- Django check/no-migration,
- Windows Catalog Epic49 tests,
- Full Django suite.

Django migration: NONE.  
Catalog schema migration: NONE.  
Production: UNTOUCHED.

---

## 8) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.
Current incident: **ERR-49-032**.

Permanent prevention rule:
- New controls are additive.
- Healthy mature acquisition actions remain visible and correctly routed.
- Regression tests must verify both button visibility/label and the actual command path.

---

## 9) Focused Employee Release Gate — Next

بعد از Merge PR #60:
1. Catalog Center کاملاً بسته باشد.
2. Local worktree clean.
3. live `git fetch --prune origin` + ff-only pull current Epic.
4. `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`.
5. mature top acquisition actions دیده شوند.
6. MakerWorld + `single` + `auto` + Product URL واقعی → `شروع اسکن` و mature worker.
7. همان URL با `دریافت محصول تکی` → همان mature worker؛ Rich Direct HTTP-403 اجباری نباشد.
8. exact-page Preview/Approve همچنان موجود باشد.

این QA عمداً Focused است؛ ویژگی‌های بی‌ربط دوباره بازطراحی یا تست گسترده نمی‌شوند مگر regression جدید دیده شود.

اگر PASS شد:
- دقیقاً یک `LOCAL PUBLISH ONLY`
- Local Django Store/Admin E2E
- verify title/SEO/source/images/pricing/visibility
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

بعد از Merge PR #60، Windows باید current Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp` را اجرا کند. Local Publish و Production تا PASS این focused regression gate ممنوع است.
