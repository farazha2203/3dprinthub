# بازگردانی ظاهر فاز ۲۶

این Hotfix ظاهر فرانت، پنل مشتری و داشبورد مدیریت را به فایل‌های فاز ۲۵ برمی‌گرداند، اما مدل‌ها، Migration، Worker، WebSocket، صف بررسی دستی و APIهای فاز ۲۶ را حذف نمی‌کند.

علت خرابی، استفاده از بسته کامل `full_no_fonts` و حذف ۱۰۵ فایل فونت در زمان جایگزینی کامل پروژه بود. همچنین Daphne از ابتدای `INSTALLED_APPS` اجرا می‌شد و Runserver معمولی را تغییر می‌داد.

## اجرا

```powershell
cd D:\projects\3DPrintHub
Set-ExecutionPolicy -Scope Process Bypass
& ".\RESTORE_PHASE26_APPEARANCE.ps1"
```

اگر فایل‌های فونت حذف شده باشند، ZIP کامل فاز ۲۵ یا `3DPrintHub.zip` اصلی را کنار اسکریپت قرار دهید. همچنین می‌توان مسیر آن را صریح داد:

```powershell
& ".\RESTORE_PHASE26_APPEARANCE.ps1" -SourceArchive "D:\Downloads\3DPrintHub_phase25_production_link_worker_full.zip"
```

پس از موفقیت:

```powershell
python manage.py runserver
```

برای اجرای ASGI و WebSocket فقط به‌صورت آگاهانه از `RUN_PHASE26_ASGI.ps1` استفاده شود.
