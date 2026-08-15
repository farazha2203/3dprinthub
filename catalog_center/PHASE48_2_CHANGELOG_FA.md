# Phase48.2 — Batch Image Packaging Hotfix

مبنای این اصلاح: 3DPrintHub Catalog Intelligence v8.5.4

## علت
Batch می‌توانست URL تصویر داشته باشد ولی `local_image_files_json` خالی بماند و
Batch ناقص به FTP برسد. در سرور، تبدیل Product به دلیل نبود `preview_image` Fail می‌شد.

## اصلاح
- Materialize تمام تصاویر انتخاب‌شده قبل از Finalize شدن Batch.
- استفاده از صفحه محصول به عنوان Referer برای CDN تصاویر.
- دانلود Atomic با فایل `.part`.
- Cache قطعی بر اساس SHA256 URL.
- ساخت Batch ابتدا در `<batch>.building`.
- اعتبارسنجی اجباری Mapping و فایل‌های محلی.
- Rename اتمیک فقط پس از Validation موفق.
- Preflight مجدد قبل از اتصال FTP.
- خطای Fail-Closed با `IMAGE_NOT_PACKAGED`.
- Regression test مخصوص سناریوی MakerWorld محصول 16 / external_id 3130743.

## دیتابیس
Migration ندارد و Installer این فاز نباید `catalog.sqlite3` یا داده Production را تغییر دهد.
