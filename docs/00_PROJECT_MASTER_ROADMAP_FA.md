# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.15 — Bulk Exact-Page Images + Add-to-Products`  
**Status:** `MERGED / ALL REQUIRED PR CI SUCCESS / WINDOWS QA PENDING`  
**Windows Operator:** Catalog Center 8.7.1  
**Backend:** Django / Python  
**Production:** تا Windows QA + Local Publish E2E + تأیید صریح مالک ممنوع.

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
- Mature behavior با Extend/Patch/Wrap اصلاح می‌شود.
- تغییر جدید حق خراب‌کردن مسیر سالم قدیمی را ندارد مگر قرارداد کسب‌وکار صریحاً تغییر کند.
- Bugfix بدون Regression Test کامل نیست.
- Source دائمی روی Production ویرایش نمی‌شود.
- ZIP/Patch/Source مستقل از GitHub مسیر تحویل نیست.
- Dirty Local/Host = STOP/INSPECT؛ reset/stash/delete Quick Fix ممنوع.
- Secret/API key/token/password در Git/log/chat/SQLite ذخیره نمی‌شود.
- SHA ثابت Chat مرجع Branch متحرک نیست؛ Remote بعد از fetch مرجع است.

## 2) مسیرهای ثبت‌شده

### Windows
```text
Project:             D:\projects\3DPrintHub
Venv:                D:\projects\3DPrintHub\.venv
Catalog Center:      D:\projects\3DPrintHub\catalog_center
Django SQLite:       D:\projects\3DPrintHub\db.sqlite3
Catalog persistent:  D:\projects\3dprinthub-catalog-manager
Catalog SQLite:      D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
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

## 3) Epic49 Path

```text
49.2A → 49.2B → 49.2C
→ Epic49 Unified Product/Slider Sync
→ 49.3A..49.3H
→ 49.3I Discovery Review/Product Explorer/Explicit Pricing
→ 49.3I.1 PS5.1 Encoding
→ 49.3I.2 Gallery/AI First-Paint
→ 49.3I.3 Live Git Snapshot
→ 49.3I.4 Explorer/URL Routing
→ 49.3I.5 Selection Guard
→ 49.3I.6 Credential Persistence
→ 49.3I.7 Preview/Provider Recovery
→ 49.3I.8 Observable All-Fields
→ 49.3I.9 AI Refresh/SEO
→ 49.3I.10 AI Trace
→ 49.3I.11 Provider Schema
→ 49.3I.12 Exact-Page UI/Image Fit
→ 49.3I.13 Paste/Batch Recovery
→ 49.3I.14 Mature Scan Restoration
→ 49.3I.15 Bulk Exact-Page Images/Add-to-Products
```

## 4) معماری دریافت محصول — قرارداد فعلی

### مسیر Mature سازگاری
```text
Top Source / Mode / Method / URL / Query
→ شروع اسکن
→ BaseApp mature start_scan/_scan_worker
→ Product Workspace
```

### مسیر اصلی کسب‌وکار Exact-Page
```text
Exact Search / Listing / Category URL
→ انتخاب تعداد محصول: 10/20/30/50/100
→ انتخاب تعداد عکس: 5/10/15/20
→ کشف لینک‌های همان صفحه
→ جمع‌آوری و Stage محلی تصاویر عمومی هر محصول با Classic browser helpers
→ نمایش تعداد عکس هر کاندیدا
→ انتخاب موارد موردنظر
→ اضافه کردن انتخاب‌شده‌ها به محصولات
→ موارد نامطلوب: Archive / Block
→ Product Workspace
```

در مسیر Exact-Page:
- `extract_direct_link` و Rich Direct Full Fetch جزو مسیر کسب‌وکار نیستند.
- Candidate image manifest زیر Catalog DATA ذخیره می‌شود؛ Candidate DB migration نداریم.
- حداقل یک تصویر باید واقعاً Local Stage شده باشد تا Candidate Ready/Addable شود.
- Add-to-Products از identity/title/source/images آماده‌شده Product review-state می‌سازد و شبکه را دوباره Full Fetch نمی‌کند.
- یک خطای محصول کل Batch را متوقف نمی‌کند.
- Stop بین محصولات رعایت می‌شود.
- Product max=100، Image max=20.

این تغییر با درخواست صریح مالک، قرارداد قدیمی one-thumbnail Preview→approved Full Fetch را فقط برای همین Exact-Page bulk flow جایگزین می‌کند.

## 5) Product Workspace / AI / Pricing
- تصاویر Workspace: viewport ثابت 228x171 و contain-fit.
- AI: request/response/error trace، watchdog عنوان 90s و All-Fields 210s، stale-result protection، schema validation، manual override protection.
- Pricing: Fixed / Range / Formula مستقل؛ Range Formula را اجرا نمی‌کند.
- Secretها فقط Windows Credential Store/environment.

## 6) Validation / Merge — 49.3I.15
PR `#61` MERGED.
- final PR head: `5f96d890b2e31e1f1d670c8afb716a1da4fc88d3`
- merge commit: `953f975e883e6dfcbf61097ac8d324d68d4ca678`

Final-head SUCCESS:
- 49.3I.15 `32641815323`
- 49.3I `32641815273`
- 49.3I.14 `32641815287`
- 49.3H `32641815289`
- 49.3G `32641815380`
- Full Phase49 + Windows Catalog regressions + Full Django `32641815270`

Django migration: NONE.  
Catalog candidate schema migration: NONE.  
Production: UNTOUCHED.

## 7) Windows Release Gate — مرحله جاری
1. Catalog Center بسته و worktree clean.
2. live fetch/prune + ff-only pull current Epic remote HEAD.
3. `RUN_PHASE49_3I15_BULK_GATE.ps1 -LaunchApp`.
4. MakerWorld exact Search URL را با 10 محصول × 10 عکس تست کن.
5. Progress و تعداد عکس Stage شده هر ردیف باید معلوم باشد.
6. 2–3 مورد آماده را انتخاب → `اضافه کردن انتخاب‌شده‌ها به محصولات`.
7. این عمل نباید per-product Direct Full Fetch بزند.
8. یک مورد را Archive/Block کن.
9. یک Product اضافه‌شده را باز و تصاویر را Verify کن.

در صورت PASS، کار عملیاتی می‌تواند 30/50/100 محصول و 10/20 عکس استفاده کند.

## 8) Publish / Production Gate
بعد از PASS:
- دقیقاً یک `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- تأیید صریح مالک,
- verify read-only مسیر/branch/commit/venv/MySQL/backup/rollback روی Host,
- deploy فقط از GitHub,
- collectstatic/restart/smoke/data verification,
- update docs.

## 9) Next Product Phase — Store ZarinPal
پس از Deploy Catalog:
- Store checkout ZarinPal request/callback/verify,
- server-owned amount,
- idempotency + Authority match + server verify,
- duplicate callback safety,
- bank transfer حفظ شود,
- Sandbox E2E، سپس یک پرداخت واقعی کم‌مبلغ با تأیید مالک.
