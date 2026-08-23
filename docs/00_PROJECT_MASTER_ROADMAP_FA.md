# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.17 — Single Active AI Runtime`  
**Status:** `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`  
**Windows Operator:** Catalog Center 8.7.1  
**Backend:** Django / Python  
**Production:** تا Windows QA + Local Publish E2E + تأیید صریح مالک ممنوع.

## 1) قانون مادر
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL AUTOMATED GATE → MANUAL QA → LOCAL PUBLISH E2E → EXPLICIT OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY → PRODUCTION VERIFICATION → UPDATE DOCS`

قواعد ثابت:
- Mature behavior با Extend/Patch/Wrap اصلاح می‌شود.
- تغییر جدید حق خراب‌کردن مسیر سالم قبلی را ندارد.
- Bugfix بدون Regression Test کامل نیست.
- Source دائمی روی Production ویرایش نمی‌شود.
- Dirty Local/Host = STOP/INSPECT؛ reset/stash/delete ممنوع.
- Secret در Git/log/chat ذخیره نمی‌شود.
- SHA ثابت Chat مرجع Branch متحرک نیست؛ Remote بعد از fetch مرجع است.

## 2) مسیرهای ثبت‌شده
Windows: `D:\projects\3DPrintHub`; Catalog: `D:\projects\3DPrintHub\catalog_center`; venv: `D:\projects\3DPrintHub\.venv`; Catalog DATA: `D:\projects\3dprinthub-catalog-manager`; Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

Production: `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`; static `/home/sfkilvrs/public_html/static`; media `/home/sfkilvrs/public_html/media`; private media `/home/sfkilvrs/3dprinthub/private_media`.

## 3) Epic49 Path
`49.3A..49.3H → 49.3I Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse → Single Active AI Runtime`.

## 4) معماری دریافت محصول — قرارداد فعلی
مسیر اصلی:
`Exact Search/Listing URL → تعداد محصول تا 100 → تعداد عکس تا 20 → کشف مقاوم → Stage محلی عکس‌ها → نمایش تعداد عکس → انتخاب → Add to Products / Archive → Product Workspace`.

Discovery fallback: `locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`.
Image fallback: `locator-safe → HTTP → mature Classic DOM → attached Chrome 9222 → listing thumbnail`.

قواعد:
- خرابی یک روش باعث امتحان روش بعدی می‌شود.
- Candidateهای قبلاً کشف‌شده برای همان Listing قابل استفاده مجدد هستند.
- حداقل یک عکس باید واقعاً Local Stage شده باشد تا Candidate قابل Add شود.
- خطای یک Candidate کل Batch را متوقف نمی‌کند.
- Rich Direct Full Fetch مسیر اصلی Bulk نیست.

## 5) Product Workspace / AI / Pricing
### AI — قرارداد 49.3I.17
- فقط Provider/Model ذخیره‌شده توسط اپراتور مجاز است.
- Product AI حق انتخاب خودکار Provider دیگر بر اساس API Keyهای موجود را ندارد.
- Key فقط از secure slot همان Provider خوانده می‌شود.
- بازکردن Product هیچ درخواست AI پنهانی شروع نمی‌کند.
- Product AI قبل از تولید محتوا `/models` نمی‌خواند؛ درخواست واقعی محتوا تست اتصال هم هست.
- Google با Model دقیق ذخیره‌شده model list اضافه نمی‌خواند.
- Search Model و Test Connection در AI Settings همچنان صریح و Live هستند.
- خطای stale Tk مثل `invalid command name ...listbox` نباید برنامه را ببندد یا Busy دائمی ایجاد کند.
- request/response/error trace، schema repair، title watchdog 90s، All-Fields watchdog 210s، Stop Waiting، stale-result و manual override حفظ شده‌اند.

### سایر قراردادها
- تصاویر Workspace: contain-fit `228x171`.
- Pricing: Fixed / Range / Formula مستقل.
- Secretها فقط secure storage/environment.

## 6) Validation / Merge — 49.3I.17
PR `#63` MERGED.
- final runtime head: `2917a3db5225abac71fc3e80b64ad439acd7a4d0`
- merge commit: `7f835f573b92e3aded6275c9421770c0c47d947a`

SUCCESS:
- 49.3I.17 `32649623837`
- 49.3I `32649623808`
- 49.3I.16 `32649623695`
- 49.3I.15 `32649623705`
- 49.3I.14 `32649623679`
- 49.3H `32649623825`
- 49.3G `32649623755`
- Full Phase49 + Windows Catalog regressions + Full Django `32649623804`

Django migration: NONE. Catalog schema migration: NONE. Production: UNTOUCHED.

## 7) Windows Release Gate — مرحله جاری
1. Catalog Center بسته و worktree clean.
2. live fetch/prune + ff-only pull current Epic.
3. `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1 -LaunchApp`.
4. در AI Center فقط یک Provider/Model را انتخاب و Active Save کن.
5. Product Workspace را باز کن؛ هیچ AI پنهانی نباید شروع شود.
6. All-Fields را یک‌بار اجرا کن؛ Trace فقط همان Provider/Model را نشان دهد و قبل از Request اصلی `/models` نباشد.
7. Stop/Failure نباید برنامه را هنگ یا نیازمند Task Manager کند.
8. در صورت نیاز یک Provider/Model دیگر را ذخیره و یک بار Verify کن که فقط همان Pair جدید استفاده می‌شود.
9. Acquisition کوتاه 49.3I.16 را در صورت باقی‌ماندن Verify کن.

## 8) Publish / Production Gate
بعد از PASS: دقیقاً یک `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → تأیید صریح مالک → verify read-only مسیر/branch/commit/venv/MySQL/backup/rollback روی Host → deploy فقط از GitHub → collectstatic/restart/smoke/data verification.

## 9) Next Product Phase — Store ZarinPal
پس از Deploy Catalog: Store checkout ZarinPal request/callback/verify، server-owned amount، idempotency، Authority match، server verify، duplicate-callback safety، حفظ bank transfer، Sandbox E2E و سپس یک پرداخت واقعی کم‌مبلغ با تأیید مالک.
