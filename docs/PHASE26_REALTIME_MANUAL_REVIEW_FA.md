# فاز ۲۶: اعلان بلادرنگ و بررسی دستی لینک

## رفع خطاهای فاز ۲۵

`RUN_PHASE25_WORKER.ps1` دیگر Warningهای Django روی stderr را خطای PowerShell تلقی نمی‌کند. ملاک شکست فقط Exit Code فرایند Python است.

`INSTALL_PHASE25_WINDOWS_WORKER.ps1` دو حالت دارد:

- PowerShell ادمین: نصب SYSTEM هنگام Startup
- PowerShell عادی: نصب برای کاربر فعلی هنگام Logon

برای اجبار نصب سیستمی:

```powershell
& .\INSTALL_PHASE25_WINDOWS_WORKER.ps1 -Machine
```

برای نصب کاربر فعلی:

```powershell
& .\INSTALL_PHASE25_WINDOWS_WORKER.ps1 -CurrentUser
```

دستورهای `sudo` و `systemctl` فقط برای Linux هستند و در Windows نباید اجرا شوند.

## WebSocket

لوکال بدون Redis با InMemory Channel Layer و Polling fallback کار می‌کند. برای Production و ارتباط Worker با ASGI باید Redis تنظیم شود:

```env
REALTIME_REDIS_URL=redis://127.0.0.1:6379/1
```

اجرای Redis در Docker ویندوز:

```powershell
& .\START_PHASE26_REDIS_DOCKER.ps1
```

اجرای ASGI:

```powershell
& .\RUN_PHASE26_ASGI.ps1 -Port 8000
```

## صف بررسی دستی

تحلیل‌های شکست‌خورده خودکار وارد صف بررسی دستی می‌شوند. مشتری نیز از صفحه نتیجه می‌تواند درخواست بررسی ثبت کند. مدیریت از مسیر زیر انجام می‌شود:

```text
/admin/store/linkanalysismanualreview/
```

داشبورد عملیات نیز آمار بررسی دستی را زنده نمایش می‌دهد.
