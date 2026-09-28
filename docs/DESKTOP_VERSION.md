# 3DPrintHub Desktop Version Registry

این فایل مرجع نسخه‌ی Desktop است. هر تغییر اجرایی Desktop باید با Build جدید، commit دقیق، تست‌های همان Build و وضعیت انتشار ثبت شود.

## آخرین Build تأییدشده

- Version: `v8.9.11`
- Build: `2026.09.28.1`
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`
- Branch: `wip/phase50-a2z-w5-manual-product-20260927`
- Launcher: `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1`
- Desktop shortcut: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk`
- Previous verified Build: `2026.09.27.22`

## Changes in Build 2026.09.28.1

- OpenRouter Image discovery and independent Image Model are active.
- One isolated Seedream 4.5 generation completed and was stored as a SQLite BLOB.
- No-invention prompt and request-fingerprint idempotency passed.
- Explicitly approved/selected SQLite revisions are handed off to existing Story/Post preparation.
- No canonical Catalog, Instagram, Host or Production mutation occurred.

## Version rules

1. Keep `APP_VERSION` for the product line and increase `BUILD_ID` for every executable behavior change.
2. Record the exact branch, commit, tests, backup and remaining gates here and in About history.
3. Never record secrets or Credential Store values.
4. Do not mark a Build released until Local tests, backup, regression and GitHub exact-SHA verification pass.
