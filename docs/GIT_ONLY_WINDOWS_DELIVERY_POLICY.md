# Git-only Windows Delivery Policy — 3DPrintHub

## قانون ثابت تحویل از این فاز به بعد

برای پروژه 3DPrintHub هیچ فایل اجرایی، PowerShell، Python، Hotfix، Patch، ZIP یا Script به‌صورت دانلود جداگانه به کاربر تحویل داده نمی‌شود.

Source of Truth فقط Repository است:

`farazha2203/3dprinthub`

Branch توسعه جاری:

`epic/phase49-unified-product-slider-sync`

مسیر تحویل اجباری:

`Change/Script/Test/Doc → GitHub commit → GitHub CI → Windows git fetch/pull → run file from repository → Local QA → explicit approval → Production`

## قوانین Windows

- Windows هیچ Source patch دستی دریافت نمی‌کند.
- فایل لازم باید اول در GitHub Commit شده باشد.
- کاربر روی `D:\projects\3DPrintHub` فقط از GitHub Pull می‌کند.
- Runnerها نیز داخل Repository قرار می‌گیرند و از همان Project root اجرا می‌شوند.
- اگر Working Tree کثیف باشد هیچ `reset --hard`، delete یا overwrite خودکار مجاز نیست.
- `.env`، DB، media و Catalog persistent data هرگز برای همگام‌سازی کد حذف/Reset نمی‌شوند.

## Phase49.3D runner

Canonical runner:

`RUN_PHASE49_3D_LOCAL_GATE.ps1`

این Runner باید بعد از Pull از این مسیر اجرا شود:

`D:\projects\3DPrintHub\RUN_PHASE49_3D_LOCAL_GATE.ps1`

Runner Remote Epic HEAD را بعد از `git fetch` خودش Resolve می‌کند و SHA قدیمی را Hardcode نمی‌کند.

## Production

Production فقط بعد از Local QA و تأیید صریح کاربر اجرا می‌شود.
