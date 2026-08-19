# Phase49.3D — Windows Runner StrictMode Array Hotfix

## مشاهده واقعی Windows

در اولین اجرای `RUN_PHASE49_3D_LOCAL_GATE.ps1` روی Windows، Gate قبل از رسیدن به Backup/Testها در Step 01 متوقف شد:

```text
The property 'Count' cannot be found on this object.
At RUN_PHASE49_3D_LOCAL_GATE.ps1:64
if ($projectProcesses.Count -gt 0)
FullyQualifiedErrorId : PropertyNotFoundStrict
```

## Root Cause

Runner با `Set-StrictMode -Version Latest` اجرا می‌شود.

کد اولیه:

```powershell
$projectProcesses = @()
$projectProcesses = Get-CimInstance Win32_Process | Where-Object { ... }
if ($projectProcesses.Count -gt 0) { ... }
```

مقداردهی دوم، Array اولیه را تضمین نمی‌کند. Pipeline پاورشل بسته به تعداد نتیجه می‌تواند `$null`، یک Scalar object یا Array برگرداند. در StrictMode دسترسی به `.Count` روی Scalar فاقد آن property خطا می‌دهد.

## Fix

Runner version:

```text
49.3D.1
```

Process collection اکنون همیشه Array-normalized است:

```powershell
$projectProcesses = @(
    Get-CimInstance Win32_Process | Where-Object { ... }
)

if (@($projectProcesses).Count -gt 0) { ... }
```

در catch نیز مقدار دوباره `@()` می‌شود.

این رفتار سه حالت را پوشش می‌دهد:
- صفر Process
- دقیقاً یک Process
- چند Process

## CI Gap و Fix

علت عبور این Regression از CI این بود که Runner PowerShell قبلاً در workflow رسمی Parse/Test نمی‌شد.

به `.github/workflows/phase49-epic-ci.yml` یک Step جدید اضافه شد:

```text
PowerShell runner syntax and array-safety contract
```

این Step:
- کل Runner را با PowerShell parser Parse می‌کند.
- وجود Runner marker `49.3D.1` را بررسی می‌کند.
- Array normalization را contract-check می‌کند.
- حالت صفر/یک/چند آیتم را تست می‌کند.

## Git-only delivery

هیچ Patch دستی روی Windows مجاز نیست.

مسیر اصلاح:

`GitHub commit → Windows git pull → run repository runner`

Canonical file:

`D:\projects\3DPrintHub\RUN_PHASE49_3D_LOCAL_GATE.ps1`

## Data / Production Safety

این Hotfix:
- هیچ Django migration ندارد.
- هیچ DB reset/delete ندارد.
- هیچ media/catalog data را تغییر نمی‌دهد.
- Production را لمس نمی‌کند.

## Gate

- [x] Root cause از خروجی واقعی Windows مشخص شد.
- [x] Runner array-safe شد.
- [x] Runner version marker اضافه شد.
- [x] PowerShell CI contract اضافه شد.
- [ ] GitHub CI جدید تأیید شود.
- [ ] Windows pull و اجرای مجدد Runner.
- [ ] ادامه Phase49.3D Local QA.
- [ ] Production فقط بعد از تأیید صریح Local.
