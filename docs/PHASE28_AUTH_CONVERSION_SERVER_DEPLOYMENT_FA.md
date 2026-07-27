# فاز ۲۸ — تبدیل لینک به سفارش، بیعانه و استقرار سرور

## هدف

این فاز مسیر کاربر را از «دیدن یک مدل» تا «درخواست قیمت، تأیید پیش‌فاکتور و ثبت رسید بیعانه» کامل می‌کند. تحلیل لینک فقط برای مشتری واردشده فعال است و نبود وزن، فایل یا مشخصات مانع ثبت درخواست قیمت کارشناسی نمی‌شود.

## جریان مشتری

1. مشتری وارد حساب می‌شود.
2. لینک محصول را ثبت می‌کند.
3. Job تحلیل در صف قرار می‌گیرد.
4. سیستم نام، تصاویر، توضیحات، فرمت‌ها، متریال، وزن و زمان چاپ را تا حد امکان استخراج می‌کند.
5. اگر وزن مستقیم پیدا نشود، از طول فیلامنت و قطر آن وزن تقریبی محاسبه می‌شود.
6. در هر وضعیت، مشتری می‌تواند درخواست قیمت کارشناسی ثبت کند.
7. سفارش و پیش‌فاکتور پیش‌نویس ساخته می‌شود.
8. مدیر مبلغ، متریال، زمان چاپ، هزینه‌ها و درصد بیعانه را نهایی می‌کند و پیش‌فاکتور را روی «ارسال‌شده» می‌گذارد.
9. مشتری پیش‌فاکتور را تأیید می‌کند.
10. مشتری رسید بیعانه، پرداخت کامل یا مانده را ثبت می‌کند.
11. واحد مالی رسید را تأیید یا رد می‌کند. تصویر رسید خارج از Media عمومی و در PRIVATE_MEDIA_ROOT نگهداری می‌شود و فقط کاربر Staff از مسیر محافظت‌شده به آن دسترسی دارد.

## کانال‌های مشاوره

شماره واتساپ، لینک/شناسه تلگرام، شماره کارت، نام صاحب کارت و درصد پیش‌فرض بیعانه از پنل مدیریت در SiteSetting تنظیم می‌شوند. دکمه مشاوره زیر تصاویر کاتالوگ خارجی، محصولات فروشگاه، صفحه جزئیات، نتیجه تحلیل و اسلایدر صفحه اول نمایش داده می‌شود. گزینه «پشتیبانی سایت» نیز لینک و نام محصول را داخل فرم چت مشتری آماده می‌کند تا کاربر فقط پیام را ارسال کند.

## خطای Redis در لوکال

اگر REALTIME_REDIS_URL تنظیم باشد ولی Redis اجرا نشود، در حالت DEBUG سیستم به InMemory/Polling برمی‌گردد و Tracebackهای تکراری تولید نمی‌کند. تحلیل خودکار همچنان به Worker نیاز دارد:

```powershell
& ".\RUN_PHASE25_WORKER.ps1"
```

یا اجرای یکپارچه لوکال:

```powershell
& ".\START_PHASE28_LOCAL.ps1"
```

برای اجرای Redis با Docker:

```powershell
& ".\START_PHASE28_LOCAL.ps1" -StartRedisDocker
```

## تفاوت SFTP و SMTP

- SFTP/SSH: انتقال فایل و اتصال Visual Studio Code به سرور.
- SMTP: ارسال ایمیل بازیابی رمز، اعلان و پیام‌های سامانه.

وجود اتصال VS Code به سرور، به معنی تنظیم‌بودن SMTP نیست. تست واقعی ایمیل:

```bash
python manage.py test_smtp_delivery --to your-email@example.com
```

## نصب لوکال

```powershell
cd D:\projects\3DPrintHub
Set-ExecutionPolicy -Scope Process Bypass
& ".\APPLY_PHASE28.ps1"
```

برای اجرای Audit:

```powershell
python manage.py phase28_conversion_audit
python manage.py deployment_readiness_check
```

## استقرار روی cPanel / Passenger

### ۱. قبل از آپلود

از این موارد Backup بگیر:

- دیتابیس MySQL
- `.env`
- `media/`
- `private_media/`
- Migrationهای تولیدشده محلی

در پنل مدیریت، صف تحلیل لینک را Pause کن. اگر Cron مربوط به Worker فعال است، موقتاً غیرفعالش کن. در cPanel بخش Setup Python App روی Stop App بزن.

### ۲. فایل‌هایی که نباید جایگزین شوند

این موارد محلی یا محرمانه‌اند و نباید از کامپیوتر روی سرور کپی شوند:

```text
.env
.venv/
db.sqlite3
media/
private_media/
staticfiles/
logs/
tmp/
__pycache__/
```

Patch فاز ۲۸ فقط کد و Migration را منتقل می‌کند و برای بروزرسانی سرور مناسب‌تر از Full ZIP است.

### ۳. آپلود

از VS Code SFTP یا File Manager، محتوای Patch را در Application Root پروژه Extract و Replace کن. مسیر نمونه فعلی پروژه ممکن است این باشد:

```text
/home/sfkilvrs/public_html
```

مسیر واقعی را از cPanel > Setup Python App > Application root بردار.

### ۴. فعال‌کردن محیط مجازی

دستور دقیق فعال‌سازی را cPanel در صفحه Python App نمایش می‌دهد. نمونه:

```bash
source /home/USERNAME/virtualenv/APP_ROOT/3.12/bin/activate
cd /home/USERNAME/APP_ROOT
```

### ۵. اعمال تغییرات

```bash
python -m pip install -r requirements.txt
python manage.py makemigrations store website --check --dry-run
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check
python manage.py test store.test_phase28 website.test_phase28_payment --keepdb
python manage.py phase28_conversion_audit
python manage.py deployment_readiness_check
```

یا:

```bash
bash APPLY_PHASE28_SERVER.sh /home/USERNAME/APP_ROOT
```

اگر `makemigrations --check` خطا داد، Migration تولیدشده روی ویندوز را نیز آپلود کن؛ روی سرور Migration جدید و ناشناخته نساز مگر بعد از بررسی Diff.

### ۶. تنظیم Site و دامنه

```bash
python manage.py shell -c "from django.contrib.sites.models import Site; Site.objects.update_or_create(pk=1, defaults={'domain':'3dprinthub.ir','name':'3DPrintHub'})"
```

### ۷. تنظیمات `.env` در Passenger بدون Redis

اگر هاست اشتراکی Redis یا Process دائمی ندارد:

```env
DJANGO_DEBUG=0
REALTIME_REDIS_URL=
REALTIME_ALLOW_POLLING_ONLY=1
REALTIME_REDIS_AUTO_FALLBACK=1
REALTIME_POLL_FALLBACK_SECONDS=5
```

در این حالت اعلان زنده با Polling کار می‌کند.

### ۸. Cron برای صف تحلیل لینک

مسیر Python محیط مجازی را در Cron مشخص کن:

```cron
* * * * * PYTHON_BIN=/home/USERNAME/virtualenv/APP_ROOT/3.12/bin/python /home/USERNAME/APP_ROOT/deploy/cpanel/run_phase28_queue_cron.sh
```

Script از `flock` استفاده می‌کند تا دو Worker هم‌زمان اجرا نشوند. اگر cPanel حداقل فاصله ۵ دقیقه دارد، همان فاصله را انتخاب کن؛ فقط زمان انتظار مشتری بیشتر می‌شود.

### ۹. Restart

در cPanel روی Restart App بزن یا:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

سپس Cron را فعال و صف تحلیل را Resume کن.

## استقرار روی VPS لینوکس

### توقف سرویس‌ها

```bash
sudo systemctl stop 3dprinthub-link-worker
sudo systemctl stop 3dprinthub-asgi
```

### اعمال کد

```bash
cd /var/www/3dprinthub
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy
python manage.py test store.test_phase28 website.test_phase28_payment --keepdb
python manage.py phase28_conversion_audit --strict
python manage.py deployment_readiness_check --strict
```

### تنظیم Production

```env
DJANGO_DEBUG=0
REALTIME_REDIS_URL=redis://127.0.0.1:6379/1
REALTIME_ALLOW_POLLING_ONLY=0
REALTIME_REDIS_AUTO_FALLBACK=0
LINK_WORKER_HEALTH_TOKEN=یک-رشته-تصادفی-طولانی
```

### شروع سرویس‌ها

```bash
sudo systemctl daemon-reload
sudo systemctl start 3dprinthub-asgi
sudo systemctl start 3dprinthub-link-worker
sudo systemctl status 3dprinthub-asgi --no-pager
sudo systemctl status 3dprinthub-link-worker --no-pager
```

## تنظیمات اجباری پنل مدیریت

در SiteSetting وارد کن:

- شماره واتساپ با کد کشور
- لینک یا شناسه تلگرام
- شماره کارت
- نام صاحب کارت
- درصد بیعانه، مثلاً ۳۰٪
- ایمیل، تلفن و آدرس

پیش‌فاکتور کارشناسی ابتدا Draft است. مدیر بعد از قیمت‌گذاری، Status را روی Sent می‌گذارد تا مشتری بتواند تأیید و پرداخت کند.

## وضعیت آمادگی انتشار

- Staging: بعد از پاس‌شدن تست‌ها و Audit قابل آپلود است.
- انتشار عمومی با پرداخت دستی: بعد از تنظیم دیتابیس Production، SMTP، دامنه، Backup، Worker/Cron و SiteSetting قابل استفاده است.
- پرداخت خودکار درگاه: هنوز فاز بعدی است؛ فاز ۲۸ ثبت رسید کارت‌به‌کارت و تأیید دستی را پوشش می‌دهد.

## مراحل اصلی باقی‌مانده

1. فاز ۲۹: درگاه پرداخت واقعی، Callback، Idempotency، Refund و مغایرت مالی.
2. فاز ۳۰: امنیت Production شامل CKEditor 5، MFA، Rate Limit، CSP و اسکن فایل.
3. فاز ۳۱: عملیات تولید شامل دستگاه‌ها، ظرفیت، تقویم چاپ، QC و ضایعات.
4. فاز ۳۲: مانیتورینگ، Backup/Restore، Performance، CDN و آماده‌سازی افتتاح عمومی.
