# فاز ۲۱ — نصب کامل Velzon Master روی پنل مدیریت

در این فاز Assetهای اصلی `master.zip` بدون تغییر در `static/velzon_master/` نصب شده‌اند.
پوسته Django Admin از ابتدا بر اساس ساختار اصلی Velzon بازسازی شده و فقط فایل‌های `master-django.css/js` نقش اتصال به ساختار فرم و جدول Django را دارند.

## اجرا
```powershell
cd D:\projects\3DPrintHub
.venv\Scripts\activate
python manage.py collectstatic --noinput
python manage.py check
python manage.py runserver
```
مرورگر را با `Ctrl+F5` تازه‌سازی کنید.

## فایل‌های اصلی
- `templates/admin/base.html`
- `templates/admin/partials/sidebar.html`
- `templates/admin/partials/topbar.html`
- `static/velzon_master/`
- `static/admin/master-django.css`
- `static/admin/master-django.js`
