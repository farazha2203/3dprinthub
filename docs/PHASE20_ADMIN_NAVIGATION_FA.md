# فاز ۲۰ — بازسازی پوسته مدیریت Velzon

## هدف

این فاز مشکل دیده‌نشدن همه منوها و زیرمنوها، از کار افتادن اسکرول Sidebar، خرابی برخی فهرست‌های Django Admin و خطاهای 404 مربوط به Choices و Flatpickr را برطرف می‌کند.

## علت‌های اصلی خرابی

1. فایل عمومی `velzon/js/plugins.js` مسیر کتابخانه‌ها را از `/static/libs/...` می‌ساخت، درحالی‌که دارایی‌های پروژه در `/static/velzon/libs/...` قرار دارند.
2. فایل کامل دموی `velzon/js/app.js` به Customizer و عناصر متعدد صفحات نمونه وابسته است و برای پوسته سفارشی Django Admin پایدار نیست.
3. رفتار منو هم‌زمان توسط اسکریپت اصلی Velzon و اسکریپت اختصاصی پنل کنترل می‌شد.
4. Sidebar به یک SimpleBar قطعی و یک محاسبه ارتفاع پایدار نیاز داشت.
5. چیدمان جدول‌های Django و فیلتر سمت کناری با CSS خام Velzon هم‌پوشانی داشت.

## راهکار اجراشده

- CSS اصلی RTL و کتابخانه‌های اصلی Velzon حفظ شدند.
- `app.js` و `plugins.js` از پوسته مدیریت حذف شدند و فایل‌ها از پروژه پاک نشده‌اند.
- رفتارهای لازم در `static/admin/velzon-admin.js` به‌صورت کنترل‌شده پیاده‌سازی شد:
  - SimpleBar یکتا
  - باز و بسته‌شدن زیرمنوها
  - بازکردن خودکار مسیر فعال
  - جست‌وجوی منو
  - حالت کوچک Sidebar
  - منوی موبایل و Overlay
  - تغییر تم و Fullscreen
  - Choices و Flatpickr فقط روی عناصر درخواست‌کننده
- تمام منوهای تجاری موجود پروژه به Sidebar اضافه و دسته‌بندی شدند.
- IRANSans روی پنل مدیریت اعمال و import فونت‌های Google از CSSهای بارگذاری‌شده حذف شد.
- فایل‌های Choices و Flatpickr از سورس اصلی `master.zip` به Namespace صحیح Velzon منتقل شدند.
- Source Mapهای CSS اضافه شدند تا خطاهای 404 کنسول حذف شوند.

## تست‌های انجام‌شده

- بررسی نحوی JavaScript با `node --check`
- Compile تمام ماژول‌های Python
- بررسی توازن تگ‌های Django Template
- بررسی تکراری‌نبودن IDهای Sidebar
- تست Chromium در وضوح دسکتاپ و موبایل:
  - فعال‌شدن SimpleBar
  - `scrollHeight` بیشتر از `clientHeight`
  - بازشدن زیرمنو و صحیح‌شدن `aria-expanded`
  - فیلتر منو با عبارت «قیمت»
  - تغییر اندازه Sidebar در دسکتاپ
  - باز و بسته‌شدن منوی موبایل و Overlay
  - نبود خطای JavaScript صفحه

## دستورات اجرا روی ویندوز

```powershell
cd D:\projects\3DprintHub
.venv\Scripts\activate
python manage.py collectstatic --noinput
python manage.py check
python manage.py runserver
```

پس از اجرا، مرورگر را با `Ctrl + F5` تازه‌سازی کنید. در صورت وجود Static قدیمی روی سرور، پوشه خروجی `STATIC_ROOT` باید با `collectstatic` مجدداً ساخته شود.

## نکته درباره `/api/engagement/summary/`

این رشته در سورس فعلی پروژه و دارایی‌های فاز ۲۰ وجود ندارد. درخواست 404 ثبت‌شده برای آن از کد فاز ۲۰ تولید نمی‌شود و به احتمال زیاد از Cache/Static قدیمی یا اسکریپت نسخه قبلی مرورگر است. پس از `collectstatic` و Hard Refresh باید دوباره بررسی شود.
