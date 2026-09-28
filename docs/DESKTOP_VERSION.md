# 3DPrintHub Desktop Version Registry

این فایل مرجع ثبت‌شده‌ی نسخه‌ی واقعی Desktop است. هر تغییر قابل‌انتشار در برنامه‌ی ویندوزی باید با افزایش `Build` و ثبت یک ورودی جدید در همین فایل انجام شود. تغییرات مستنداتی که رفتار برنامه را عوض نمی‌کنند، نسخه‌ی نرم‌افزار را افزایش نمی‌دهند.

## آخرین نسخه‌ی تأییدشده Desktop

- Version: `v8.9.11`
- Build: `2026.09.27.22`
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`
- Branch: `wip/phase50-a2z-w5-manual-product-20260927`
- Launcher: `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1`
- Desktop shortcut: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk`
- Shortcut target verification: PASS on `2026-09-28`
- Version source verification: `catalog_center/app/version.py` → `APP_VERSION=8.9.11`, `BUILD_ID=2026.09.27.22`

## وضعیت checkout فعلی این Repository

- Current checkout: `D:\projects\3DPrintHub`
- Current branch: `wip/phase50-a2l-owner-qa-20260917`
- Current source version: `v8.9.10`, Build `2026.09.02.1`
- این checkout نسخه‌ی آخر Desktop نیست و نباید برای تغییرات W5/Social AI استفاده شود.
- Worktree هنگام ثبت این رجیستری dirty بود؛ تغییرات قبلی آن دست‌نخورده باقی مانده‌اند.

## قرارداد افزایش نسخه

1. قبل از هر تغییر اجرایی، `Repository`, branch, `HEAD` و مسیر Shortcut دوباره verify می‌شوند.
2. تغییرات واقعی Desktop با `Build` جدید ثبت می‌شوند؛ مقدار `APP_VERSION` فقط هنگام تغییر نسخه‌ی محصول افزایش می‌یابد.
3. هر ورودی باید مسیر Repository، branch، commit، تغییرات اصلی، تست‌های موفق و وضعیت Production را ثبت کند.
4. مقدارهای secret، token، Credential Store یا محتوای کلید هرگز در این فایل ثبت نمی‌شوند.
5. ثبت در GitHub فقط پس از تست Local و commit/push همان تغییر انجام می‌شود.

## تاریخچه

### 2026-09-28 — Registry initialization

- Registered latest verified Windows Desktop as `v8.9.11 — Build 2026.09.27.22`.
- Verified the Desktop shortcut points to the `a2z-a2r-converge` Qt launcher.
- No application source, Catalog, Host, Production or secret data was changed by this registry entry.
