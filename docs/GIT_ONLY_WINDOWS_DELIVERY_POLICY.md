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
- اگر Working Tree کثیف باشد هیچ `reset --hard`، `git clean`, stash خودکار، delete یا overwrite خودکار مجاز نیست؛ STOP/INSPECT.
- `.env`، DB، media و Catalog persistent data هرگز برای همگام‌سازی کد حذف/Reset نمی‌شوند.

## Git Snapshot Handoff Rule

این Rule برای تمام Runnerهای تحویل Windows دائمی است، نه فقط یک Phase خاص:

1. روی Branch صحیح و Worktree تمیز باش.
2. `git fetch --prune origin` را در همان handoff اجرا کن.
3. Remote HEAD را از `origin/<current-development-branch>` بعد از همان fetch Resolve کن.
4. Local HEAD باید با همان fetched Remote HEAD برابر باشد.
5. اگر Local عقب است فقط `git pull --ff-only` مجاز است و سپس Runner دوباره اجرا می‌شود.
6. SHA نوشته‌شده در Chat، سند، پیام قبلی یا حافظه نباید به‌تنهایی جای fetched Remote snapshot را بگیرد؛ Branch ممکن است بعداً جلو رفته باشد.
7. اگر Runtime بعد از آخرین CI تغییر کرده باشد، قبل از Windows QA باید CI تازه انجام شود.
8. هیچ mismatch با reset/delete/force حل نمی‌شود؛ Root Cause بررسی می‌شود.

این Policy قبلاً در قرارداد Phase49.3D نیز وجود داشت؛ Incident `ERR-49-019` زمانی رخ داد که یک Chat preflight برخلاف همین Rule از `$ExpectedHead` ثابت استفاده کرد.

## Current Phase49.3I Runner

Canonical runner:

`RUN_PHASE49_3I_LOCAL_GATE.ps1`

Current version:

`49.3I.3`

مسیر اجرا:

`D:\projects\3DPrintHub\RUN_PHASE49_3I_LOCAL_GATE.ps1`

Runner v49.3I.3:
- exact Epic branch را Verify می‌کند؛
- clean worktree را Verify می‌کند؛
- `git fetch --prune origin` اجرا می‌کند؛
- fetched Remote Epic HEAD را Resolve می‌کند؛
- `Local HEAD == Remote HEAD` را الزام می‌کند؛
- marker `PHASE49_3I_GIT_SNAPSHOT=OK` فقط بعد از این تطبیق صادر می‌شود؛
- Windows PowerShell 5.1 ASCII-only contract را حفظ می‌کند.

Historical Phase49.3D runner نیز قرارداد Remote HEAD resolution بدون hardcoded stale SHA را داشت.

## Production

Production فقط بعد از Local automated gate، Manual Visual/Data QA، LOCAL PUBLISH E2E و تأیید صریح کاربر اجرا می‌شود.
