# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Base Epic:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.24 — Runtime Observability + AvalAI URL Tools + Startup No-Network Guard`  
**Status:** `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`  
**Windows Operator:** Catalog Center 8.7.1  
**Backend:** Django / Python  
**Production:** تا Windows QA + Local Publish E2E + تأیید صریح مالک ممنوع.

## Current Feature Override — 49.3I.24
قرارداد جاری نسبت به بخش‌های تاریخی پایین‌تر اولویت دارد:
- Product AI فقط Provider/Model ذخیره‌شده را استفاده می‌کند و Product `/models` پنهان ندارد.
- Startup قبل از first Tk idle نباید model-list network چند Provider را اجرا کند.
- URL داخل chat به‌تنهایی browsing محسوب نمی‌شود؛ exact-page app fetch/sanitize مرجع است و فقط tool پشتیبانی‌شده AvalAI می‌تواند evidence اضافه کند.
- AvalAI structured output از `json_schema` شروع می‌شود و compatibility fallback دارد.
- مدل‌های واضح غیرمتنی برای Product editorial AI رد می‌شوند.
- Dashboard لاگ Program/AI و safe diagnostic export دارد؛ heartbeat/hang watchdog برای کندی و Not Responding فعال است.
- ERR-49-040/041/042 و REQ-49I-031 رکوردهای جاری‌اند.
- هیچ Migration جدید و هیچ تغییر Production در این Hotfix وجود ندارد.

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
`49.3A..49.3H → 49.3I Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse → Single Active AI Runtime → Operator Editing → Canonical Source Identity → Visible Operator Panels → Observable Link Refresh → Tk Main-Thread Bridge → AvalAI Exact Contract → Runtime Observability/URL Tools/Startup Guard`.

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
### AI — قرارداد پایه حفظ‌شده
- فقط Provider/Model ذخیره‌شده توسط اپراتور مجاز است.
- Product AI حق انتخاب خودکار Provider دیگر بر اساس API Keyهای موجود را ندارد.
- Key فقط از secure slot همان Provider خوانده می‌شود.
- بازکردن Product هیچ درخواست AI پنهانی شروع نمی‌کند.
- Product AI قبل از تولید محتوا `/models` نمی‌خواند.
- Search Model و Test Connection در AI Settings همچنان صریح و Live هستند.
- workerهای AI از main-thread bridge برای Tk استفاده می‌کنند.
- request/response/error trace، timeout/cancel، stale-result و manual override حفظ شده‌اند.

### سایر قراردادها
- تصاویر Workspace: contain-fit `228x171`.
- Pricing: Fixed / Range / Formula مستقل.
- Secretها فقط secure storage/environment.

## 6) Validation / Merge — Historical Base
PR `#63` برای 49.3I.17 MERGED شد و CIهای ثبت‌شده آن موفق بودند. Feature branch فعلی 49.3I.18..24 هنوز Windows Local acceptance جدید می‌خواهد؛ نتیجه قدیمی Base به معنی PASS شدن Hotfix جاری نیست.

Django migration: NONE. Catalog schema migration: NONE. Production: UNTOUCHED.

## 7) Windows Release Gate — مرحله جاری
1. Catalog Center بسته و worktree clean.
2. live fetch/prune + ff-only pull Feature Branch و Local HEAD == Remote HEAD.
3. compile و focused regressionهای 49.3I.24/23/22/21/20/19/18.
4. `launch.py --verify-only`.
5. Startup سریع + Dashboard diagnostics و عدم `/models` خودکار.
6. Model Search صریح بعد از first idle.
7. Product 2896217: exact link completion با AvalAI، URL-tool شفاف یا app-fetch fallback، structured JSON، بدون audit signature error.
8. در کندی طولانی، thread dump و safe diagnostic export بررسی شود.
9. Close/Reopen معمولی بررسی شود.

## 8) Publish / Production Gate
بعد از PASS: دقیقاً یک `LOCAL PUBLISH ONLY` → Local Store/Admin/Product/Media/SEO E2E → تأیید صریح مالک → verify read-only مسیر/branch/commit/venv/MySQL/backup/rollback روی Host → deploy فقط از GitHub → collectstatic/restart/smoke/data verification.

## 9) Next Product Phase — Store ZarinPal
پس از Deploy Catalog: Store checkout ZarinPal request/callback/verify، server-owned amount، idempotency، Authority match، server verify، duplicate-callback safety، حفظ bank transfer، Sandbox E2E و سپس یک پرداخت واقعی کم‌مبلغ با تأیید مالک.
