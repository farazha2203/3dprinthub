# راهنمای نصب فاز ۱۹: Velzon، چت، مدارک خصوصی و ورود گوگل

این نسخه روی پروژه فعلی 3DPrintHub نصب می‌شود و دیتابیس، رسانه‌ها، پنل مشتری، فروشگاه و سیستم قیمت‌گذاری موجود را جایگزین نمی‌کند.

## ۱. پشتیبان‌گیری قبل از نصب

از فایل `.env`، دیتابیس و پوشه‌های رسانه نسخه پشتیبان تهیه شود. فایل‌های حساس نباید داخل Git یا ZIP عمومی قرار بگیرند.

نمونه MySQL:

```bash
mysqldump -u DB_USER -p DB_NAME > 3dprinthub-before-phase19.sql
```

## ۲. نصب وابستگی‌ها

```bash
python -m pip install -r requirements.txt
```

نسخه پروژه روی Django 6.0.7 و django-allauth 65.18.0 تنظیم شده است.

## ۳. تنظیم متغیرهای محیطی

این مقادیر به `.env` سرور اضافه شوند:

```env
GOOGLE_OAUTH_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
DJANGO_SITE_ID=1
ACCOUNT_EMAIL_VERIFICATION=none
```

در Google Cloud Console یک OAuth Client از نوع Web application ساخته شود.

Authorized JavaScript origins:

```text
https://3dprinthub.ir
https://www.3dprinthub.ir
http://127.0.0.1:8000
```

Authorized redirect URIs:

```text
https://3dprinthub.ir/accounts/google/login/callback/
https://www.3dprinthub.ir/accounts/google/login/callback/
http://127.0.0.1:8000/accounts/google/login/callback/
```

## ۴. Migration و Static

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

در لوکال:

```bash
python manage.py check
python manage.py test website.test_phase19_support_google website.test_admin_velzon
```

## ۵. مجوز پوشه فایل‌های خصوصی

فایل‌های مدارک سفارش و پیوست چت در `private_media` قرار می‌گیرند و URL عمومی ندارند.

```bash
mkdir -p private_media
chmod 750 private_media
```

کاربر سرویس Python/WSGI باید اجازه خواندن و نوشتن در این پوشه را داشته باشد.

## ۶. راه‌اندازی مجدد

بعد از Migration و collectstatic، سرویس WSGI/Passenger/Gunicorn ری‌استارت شود. روش دقیق به نوع هاست بستگی دارد.

## ۷. تست پذیرش

- ورود ادمین و بازشدن کامل Sidebar همراه اسکرول
- ثبت سفارش با تصاویر زوایای مختلف و فایل PDF/STL
- نمایش Thumbnail تصاویر و پیش‌نمایش PDF در ادمین
- ارسال پیام مشتری از چت شناور و پنل مشتری
- پاسخ کارشناس از `مدیریت > گفت‌وگوهای پشتیبانی`
- ورود با گوگل و ساخته‌شدن خودکار پروفایل مشتری
- عدم دسترسی مشتری دیگر به چت و مدارک خصوصی

## بازگشت به نسخه قبل

کد نسخه قبل، دیتابیس Backup و پوشه‌های media/private_media بازیابی شوند. در صورت Rollback کد، Migration فاز ۱۹ فقط با آگاهی از حذف داده‌های چت و مدارک جدید برگشت داده شود.
