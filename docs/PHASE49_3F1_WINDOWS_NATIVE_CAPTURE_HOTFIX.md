# Phase49.3F.1 — Windows Native stderr Capture Hotfix

## وضعیت

- Scope: **Runner/CI/Documentation only**
- Runtime business logic: **UNCHANGED**
- Django models: **UNCHANGED**
- Migrations: **NO NEW MIGRATION**
- Pricing/AI/Workspace/Publish: **UNCHANGED**
- Production: **UNTOUCHED**
- CI final: **SUCCESS**
- Final CI Run: `32356959599`
- Final CI Job: `96388108683`
- CI probe PR: `#36` — **closed / not merged**

## Incident واقعی Windows — 2026-08-20

در اجرای `RUN_PHASE49_3F_LOCAL_GATE.ps1` روی Windows PowerShell، دو Migration فاز 49.3F با موفقیت اعمال شدند:

```text
Applying store.0033_phase49_3f_pricing_intelligence... OK
Applying website.0023_phase49_3f_material_runtime_rates... OK
```

پس از آن Runner هنگام Verify با `showmigrations` متوقف شد:

```text
python.exe : System check identified some issues:
...
NativeCommandError
```

این خطا **به معنی شکست Migration یا خرابی DB نبود**.

## Root Cause

Runner دارای این تنظیم سراسری بود:

```powershell
$ErrorActionPreference = "Stop"
```

و خروجی `showmigrations` به شکل زیر Capture می‌شد:

```powershell
$storeMigrations = (& $Py manage.py showmigrations store 2>&1) -join "`n"
```

در Windows PowerShell 5.1، متن native-process `stderr` می‌تواند به `ErrorRecord/NativeCommandError` تبدیل شود. Django Warning غیرکشنده `ckeditor.W001` روی stderr نوشته شد، در حالی که exit code فرمان صفر بود. به علت `ErrorActionPreference=Stop`، PowerShell قبل از بررسی `$LASTEXITCODE` Runner را متوقف کرد.

## Fix

Runner از `49.3F.0` به `49.3F.1` ارتقا یافت.

Helper جدید:

```powershell
Invoke-NativeCapture
```

قرارداد آن:

1. فقط در محدوده اجرای native command، `ErrorActionPreference` موقتاً `Continue` می‌شود.
2. stdout و stderr هر دو Capture می‌شوند.
3. مقدار قبلی `ErrorActionPreference` حتماً Restore می‌شود.
4. موفق/ناموفق بودن فرمان فقط با **native exit code** تعیین می‌شود.
5. exit code غیرصفر همچنان Fail-closed است و خروجی Captureشده در خطا ثبت می‌شود.
6. Warning روی stderr با exit code صفر نباید Gate را متوقف کند.

`showmigrations store` و `showmigrations website` اکنون از همین Helper استفاده می‌کنند.

## Regression Self-Test

Runner پارامتر زیر را دارد:

```powershell
-NativeCaptureSelfTest
```

این Self-Test یک native child process اجرا می‌کند که:

- روی stderr عمداً Warning می‌نویسد؛
- روی stdout marker می‌نویسد؛
- با exit code `0` خارج می‌شود.

انتظار:

```text
PHASE49_3F_NATIVE_CAPTURE_SELFTEST=OK
```

Workflow رسمی Phase49 نیز این Self-Test و Source Contract را اجرا می‌کند.

## CI hardening در زمان پیاده‌سازی

دو Failure اولیه Probe فقط ضعف خود تست CI را نشان دادند و قبل از تحویل Windows رفع شدند:

1. Self-Test روی Linux قبل از اجرا به `Join-Path D:\...` می‌رسید. Path initialization به assignment ساده و path-neutral تبدیل شد تا Self-Test قبل از Windows path validation قابل اجرا باشد.
2. Self-Test موفق بود و marker را با `Write-Host` چاپ می‌کرد، اما Workflow سعی می‌کرد marker را از pipeline capture بخواند. چون خود Self-Test stdout/stderr را داخلی validate می‌کند، CI اکنون نتیجه را با exit code Self-Test می‌سنجد.

این دو مورد هیچ تغییری در Runtime business logic یا DB ایجاد نکردند.

## Final CI Verification

Run نهایی:

```text
Run  = 32356959599
Job  = 96388108683
Result = SUCCESS
```

Gateهای نهایی:

- PowerShell runner syntax / array safety / native stderr self-test: **PASS**
- Python compile: **PASS**
- Django check / migration contract: **PASS**
- Phase49.3F additive migration safety: **PASS**
- Phase49 targeted behavioral regressions: **PASS**
- Windows Catalog Center Epic49 tests: **PASS**
- Full Django suite: **PASS**

PR موقت `#36` فقط برای مشاهده CI ساخته شد و بدون Merge بسته شد.

## Data Safety

- Migrationهای Local از قبل با موفقیت اعمال شده‌اند؛ rollback نمی‌شوند.
- اجرای مجدد Runner idempotent است؛ Django Migrationهای `[X]` را دوباره تخریبی اجرا نمی‌کند.
- هیچ `reset --hard`, DB reset, DROP/TRUNCATE/DELETE یا Media cleanup اضافه نشده است.
- Backupهای ایجادشده در اجرای قبلی حفظ می‌شوند.

## Warningهای مستقل

### `ckeditor.W001`

Technical debt مستقل است. Trigger مشاهده‌شده برای stderr بود، اما Root Cause Crash نبود. این Hotfix Warning را hide/silence نمی‌کند.

### `store.W026`

هشدار مستقل Realtime/Redis است و به این Hotfix ارتباط ندارد. باید در مسیر Production readiness جداگانه مدیریت شود.

## Do Not Repeat

- در Windows PowerShell، native stderr را زیر `ErrorActionPreference=Stop` مستقیماً با `2>&1` Capture نکن مگر lifecycle خطا کنترل شده باشد.
- Warning را با success/failure اشتباه نکن؛ **native exit code** مرجع نتیجه فرمان است.
- برای رفع این کلاس خطا Warningهای Django را خاموش نکن.
- Migration موفق را به علت Failure مرحله Verify rollback/reset نکن.
- Self-Test CI نباید قبل از platform-specific path validation به Windows-only drive access وابسته باشد.

## Next Gate

- [x] Root Cause identified
- [x] Runner 49.3F.1 implemented
- [x] CI contract/self-test added
- [x] Full GitHub CI verified
- [ ] Windows pull latest Epic
- [ ] Re-run `RUN_PHASE49_3F_LOCAL_GATE.ps1`
- [ ] Automated Local Gate PASS
- [ ] Manual QA
- [ ] Local Publish only
- [ ] Explicit user approval
- [ ] Production deploy
