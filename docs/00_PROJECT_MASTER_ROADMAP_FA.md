# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.14 — Restore Mature Scan Controls + Single-Product Route`  
**Windows Operator:** Catalog Center 8.7.1  
**Backend:** Django / Python  
**Production:** تا Windows QA + Local Publish E2E + تأیید صریح مالک پروژه ممنوع.

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

## 2) مسیرهای ثبت‌شده
Windows:
```text
Project:             D:\projects\3DPrintHub
Venv:                D:\projects\3DPrintHub\.venv
Catalog Center:      D:\projects\3DPrintHub\catalog_center
Django SQLite:       D:\projects\3DPrintHub\db.sqlite3
Catalog persistent:  D:\projects\3dprinthub-catalog-manager
Catalog SQLite:      D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
Backups:             D:\projects\3dprinthub-backups
```

Production:
```text
Project:       /home/sfkilvrs/3dprinthub
Venv:          /home/sfkilvrs/virtualenv/3dprinthub/3.12
Database:      MySQL sfkilvrs_EmiAdmin_3dprinthub
Static:        /home/sfkilvrs/public_html/static
Media:         /home/sfkilvrs/public_html/media
Private media: /home/sfkilvrs/3dprinthub/private_media
```

قبل از هر Production operation باید `docs/PATHS.md`، `docs/HOST_CONSTRAINTS.md`، DB vendor/name واقعی، Backup، Rollback و Branch/Commit واقعی دوباره Verify شوند.

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
→ 49.3I.1 ... 49.3I.13
→ 49.3I.14 Mature Scan Controls/Single-Product Route Restoration
```

Current status: **49.3I.14 merged; all required final PR-head CI SUCCESS; focused Windows release QA pending; Production untouched.**

## 4) معماری عملیاتی دریافت محصول
دو مسیر باید همزمان وجود داشته باشند.

Mature acquisition:
```text
Source / Mode / Method / URL / Query
→ شروع اسکن
→ Original BaseApp start_scan / _scan_worker
→ mature discovery/queue/classic collector
→ Product Workspace
```

Review acquisition:
```text
Exact Search/Listing/Category URL
→ Preview Candidate
→ Approve / Archive
→ Approved Full Fetch
→ Product Workspace
```

قانون دائمی: مسیر Review حق حذف، مخفی‌کردن یا Rebind کردن مسیر Mature را ندارد مگر با درخواست صریح مالک پروژه.

## 5) Phase49.3I.14
Windows QA بعد از 49.3I.13 نشان داد:
- `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها` Hide شده بودند,
- Preview layer متد `App87.start_scan` را هم جایگزین کرده بود,
- اکشن جدید `دریافت محصول تکی` Rich Direct Intake را اجباری می‌کرد و برای MakerWorld Product واقعی HTTP 403 داد.

Canonical error: `ERR-49-032`.

اصلاح:
- mature actions Restore,
- `شروع اسکن` → BaseApp mature worker,
- `دریافت محصول تکی` → validate Product URL → `mode=single` → همان mature worker,
- `دریافت هوشمند از لینک` همچنان Optional,
- Preview/Approve/Archive/Paste/Error Detail حفظ,
- crawler/extractor جدید اضافه نشده است.

## 6) Product Workspace / AI / Pricing Contracts
- images: viewport ثابت `228x171`, `ImageOps.contain`, بدون crop/stretch,
- AI: mature All-Fields Task Center, first-paint, sanitized trace, 90s/210s watchdog, stale-result safety, exact schema + one repair,
- pricing: Fixed / Range / Formula مستقل؛ Range هرگز Formula را اجرا نمی‌کند.

## 7) Latest Validation
PR #60: MERGED.
Final PR head: `f12a25e1fe50fb16a03a1324c84912c830a2608e`.
Merge commit: `124662cf2436dfcce245282b01b2da694802aa55`.

Runs:
- Phase49.3I.14 `32636771174` — SUCCESS
- Phase49.3I `32636771071` — SUCCESS
- Phase49.3H `32636771154` — SUCCESS
- Phase49.3G `32636771049` — SUCCESS
- Full Phase49 + Full Django `32636771103` — SUCCESS

Initial targeted CI correctly caught the resolver bug before final validation. Final CI is green.

Django migration: NONE.  
Catalog schema migration: NONE.  
Production: UNTOUCHED.

## 8) Employee Release Gate — Next
1. Catalog Center بسته باشد.
2. Local worktree clean.
3. live `git fetch --prune origin` + ff-only pull current Epic.
4. `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`.
5. mature top actions visible.
6. MakerWorld + `single` + `auto` + known Product URL → `شروع اسکن` mature route.
7. manual `دریافت محصول تکی` همان mature route و بدون اجبار Rich Direct 403.
8. exact-page Preview/Approve همچنان موجود.

اگر PASS شد:
- دقیقاً یک `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin E2E,
- verify title/SEO/source/images/pricing/visibility,
- explicit owner approval.

## 9) Production Gate
بعد از Windows QA + Local Publish E2E + تأیید صریح مالک:
1. read-only host state verify,
2. project root/branch/commit verify,
3. clean/safe host state,
4. `.env`/persistent data backup,
5. `manage.py check`,
6. `makemigrations --check --dry-run`,
7. verify MySQL vendor/name,
8. migration plan / backup if needed,
9. collectstatic,
10. Passenger restart,
11. HTTP/store/admin/product/media verification,
12. docs update.

## 10) Next Product Phase
After Catalog deploy: Store ZarinPal request/callback/verify + Sandbox E2E using mature Phase30 security semantics.

## Exact Next Step
Windows باید current Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp` را اجرا کند. بعد از PASS همین Focused QA، Local Publish E2E و سپس Production gate انجام می‌شود.
