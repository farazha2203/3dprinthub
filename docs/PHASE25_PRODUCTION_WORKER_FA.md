# فاز ۲۵ — Worker دائمی، اعلان و داشبورد عملیات لینک

## هدف

فاز ۲۴ صف دیتابیسی و Retry را ایجاد کرد، اما برای محیط Production هنوز Worker باید دستی اجرا می‌شد و مدیر دید متمرکزی از سلامت پردازش نداشت. فاز ۲۵ این فاصله را با Heartbeat، کنترل سراسری صف، سیاست مستقل هر منبع، اعلان مشتری و استقرار دائمی Worker پوشش می‌دهد.

## داشبورد مدیریت

مسیر Django Admin:

`/admin/store/linkanalysisoperationsdashboard/`

در این صفحه می‌توان:

- صف را متوقف یا فعال کرد.
- چند Job را فوراً پردازش کرد.
- قفل Workerهای منقضی را آزاد کرد.
- همه Jobهای ناموفق را دوباره وارد صف کرد.
- MakerWorld، Printables، Thingiverse، GrabCAD، لینک مستقیم یا تحلیل عمومی را جداگانه فعال/غیرفعال کرد.
- Heartbeat، PID، میزبان، نسخه Worker و آخرین خطا را دید.
- Jobها و Attemptهای اخیر را بررسی کرد.

## اجرای Worker در ویندوز

اجرای دستی دائمی:

```powershell
cd D:\projects\3DPrintHub
.\RUN_PHASE25_WORKER.ps1
```

نصب به‌صورت Scheduled Task در Startup ویندوز؛ PowerShell را با Run as administrator باز کنید:

```powershell
cd D:\projects\3DPrintHub
Set-ExecutionPolicy -Scope Process Bypass
.\INSTALL_PHASE25_WINDOWS_WORKER.ps1
```

حذف سرویس:

```powershell
.\UNINSTALL_PHASE25_WINDOWS_WORKER.ps1
```

لاگ Worker:

`logs/link-analysis-worker.log`

## اجرای Worker در Linux/systemd

فایل نمونه:

`deploy/systemd/3dprinthub-link-worker.service`

قبل از نصب، مسیر `/var/www/3dprinthub` و کاربر `www-data` را با سرور خود هماهنگ کنید:

```bash
sudo bash deploy/systemd/install_link_worker.sh /var/www/3dprinthub
sudo journalctl -u 3dprinthub-link-worker -f
```

## Health Check

فرمان محلی:

```powershell
python manage.py link_analysis_worker_health --json
```

Endpoint محافظت‌شده:

`/store/internal/link-worker-health/`

در `.env` یک Token تصادفی طولانی قرار دهید:

```env
LINK_WORKER_HEALTH_TOKEN=replace-with-a-long-random-secret
```

درخواست مانیتورینگ:

```bash
curl -H "X-Health-Token: replace-with-a-long-random-secret" https://3dprinthub.ir/store/internal/link-worker-health/
```

کد ۲۰۰ یعنی حداقل یک Worker زنده وجود دارد یا صف عمداً Pause شده است. کد ۵۰۳ یعنی Worker فعالی دیده نشده است.

## کنترل Adapterها

هر Adapter این تنظیمات را دارد:

- فعال یا غیرفعال
- توقف تا زمان مشخص
- اولویت جایگزین
- سقف Retry
- فاصله‌های Retry
- Timeout دریافت صفحه
- ذخیره یا عدم ذخیره تصویر Remote
- اعلان موفقیت یا شکست
- شمارنده موفقیت، شکست و خطاهای پیاپی

Job هنگام ثبت، Adapter خود را از روی Domain یا پسوند فایل تشخیص می‌دهد. Worker قبل از Claim دوباره سیاست Adapter را بررسی می‌کند؛ بنابراین غیرفعال‌کردن منبع بدون Restart Worker اثر می‌کند.

## اعلان مشتری

پس از تکمیل موفق، یک اعلان در پنل مشتری با لینک نتیجه تحلیل ساخته می‌شود. پس از شکست قطعی نیز اعلان بررسی دستی یا Retry ساخته می‌شود. هر نتیجه فقط یک بار اعلان می‌شود. ارسال ایمیل از تنظیمات صف قابل فعال‌سازی است و از SMTP موجود پروژه استفاده می‌کند.

## رفتار توقف صف

Pause سراسری Job جدیدی Claim نمی‌کند. Job در حال اجرا اجازه دارد سالم تمام شود. Resume بدون Restart Worker اجرا می‌شود.

## نکات Production

- فقط یک Task ویندوز با نام پیش‌فرض نصب کنید؛ اجرای چند Worker مجاز است ولی باید آگاهانه باشد.
- Health Token را داخل Git ثبت نکنید.
- روی Linux دسترسی نوشتن Worker را فقط به Media و Logs بدهید.
- مقدار Timeout هر Adapter را بیش از ۴۵ ثانیه قرار ندهید؛ سرویس آن را Clamp می‌کند.
- هشدار CKEditor 4 مستقل از Worker است و در Epic امنیت باید با CKEditor 5 جایگزین شود.
