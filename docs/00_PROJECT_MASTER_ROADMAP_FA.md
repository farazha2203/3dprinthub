# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.16 — Resilient Acquisition Fallback + Cached Candidate Reuse`  
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
- Dirty Local/Host = STOP/INSPECT؛ reset/stash/delete Quick Fix ممنوع.
- Secret در Git/log/chat ذخیره نمی‌شود.
- SHA ثابت Chat مرجع Branch متحرک نیست؛ Remote بعد از fetch مرجع است.

## 2) مسیرهای ثبت‌شده
Windows: `D:\projects\3DPrintHub`; Catalog: `D:\projects\3DPrintHub\catalog_center`; venv: `D:\projects\3DPrintHub\.venv`; Catalog DATA: `D:\projects\3dprinthub-catalog-manager`; Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

Production: `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`; static `/home/sfkilvrs/public_html/static`; media `/home/sfkilvrs/public_html/media`; private media `/home/sfkilvrs/3dprinthub/private_media`.

## 3) Epic49 Path
`49.3A..49.3H → 49.3I Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse`.

## 4) معماری دریافت محصول — قرارداد فعلی
مسیر اصلی:
`Exact Search/Listing URL → تعداد محصول 10/20/30/50/100 → تعداد عکس 5/10/15/20 → کشف مقاوم → Stage محلی عکس‌ها → نمایش تعداد عکس → انتخاب → Add to Products / Archive → Product Workspace`.

Discovery fallback:
`locator-safe → HTTP/HTML → attached Chrome 9222 → cached candidate DB`.

Image fallback:
`locator-safe fresh → HTTP parser/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail`.

قواعد:
- خرابی یک روش باعث امتحان روش بعدی می‌شود.
- Candidateهای قبلاً کشف‌شده برای همان Listing قابل استفاده مجدد هستند.
- Manifest هر Candidate مسیرهای امتحان‌شده و روش موفق را ثبت می‌کند.
- حداقل یک عکس باید واقعاً Local Stage شده باشد تا Candidate قابل Add شود.
- خطای یک Candidate کل Batch را متوقف نمی‌کند.
- Rich Direct Full Fetch مسیر اصلی Bulk نیست.
- Product max=100، Image max=20.
- Archive/Block/dedupe و Mature controls حفظ می‌شوند.

## 5) Product Workspace / AI / Pricing
- تصاویر Workspace: contain-fit `228x171`.
- AI: request/response/error trace، watchdog عنوان 90s و All-Fields 210s، stale protection، schema validation، manual override protection.
- Pricing: Fixed / Range / Formula مستقل.
- Secretها فقط secure storage/environment.

## 6) Validation / Merge — 49.3I.16
PR `#62` MERGED.
- final PR head: `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`
- merge commit: `44216546162fead0b752d92cf6cae8d658f034f2`

SUCCESS:
- 49.3I.16 `32645660164`
- 49.3I `32645660154`
- 49.3I.15 `32645660045`
- 49.3I.14 `32645660071`
- 49.3H `32645660135`
- 49.3G `32645660118`
- Full Phase49 + Windows Catalog regressions + Full Django `32645660123`

Django migration: NONE. Catalog schema migration: NONE. Production: UNTOUCHED.

## 7) Windows Release Gate — مرحله جاری
1. Catalog Center بسته و worktree clean.
2. live fetch/prune + ff-only pull current Epic.
3. `RUN_PHASE49_3I16_FALLBACK_GATE.ps1 -LaunchApp`.
4. MakerWorld `cake+stand` با 10 محصول × 10 عکس.
5. خطای روش اول نباید Run را متوقف کند؛ fallback باید ادامه دهد.
6. اگر Live discovery شکست خورد Candidateهای ذخیره‌شده همان Listing استفاده شوند.
7. 2–3 مورد آماده → Add to Products بدون Direct Full Fetch.
8. یک مورد Archive/Block.
9. یک Product را باز و تصاویر را Verify کن.

## 8) Publish / Production Gate
بعد از PASS: دقیقاً یک `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → تأیید صریح مالک → verify read-only مسیر/branch/commit/venv/MySQL/backup/rollback روی Host → deploy فقط از GitHub → collectstatic/restart/smoke/data verification.

## 9) Next Product Phase — Store ZarinPal
پس از Deploy Catalog: Store checkout ZarinPal request/callback/verify، server-owned amount، idempotency، Authority match، server verify، duplicate-callback safety، حفظ bank transfer، Sandbox E2E و سپس یک پرداخت واقعی کم‌مبلغ با تأیید مالک.
