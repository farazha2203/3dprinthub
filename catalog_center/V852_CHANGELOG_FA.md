# 3DPrintHub Catalog Intelligence v8.5.2

- اصلاح نصب‌کننده ویندوز: اجرای مستقیم `app\upgrade.py` با مسیر مطلق برای جلوگیری از خطای `No module named app.upgrade`.
- افزودن تست رگرسیون برای استقلال نصب‌کننده از پوشه جاری PowerShell و Python import path.
- رفع قفل `catalog.sqlite3` آزمایشی در ویندوز با بستن قطعی تمام Connectionهای SQLite در تست Upgrade.
- حفظ تمام اصلاحات خروج امن و آزادسازی فایل لاگ نسخه `8.5.1`.
- افزودن لوگوی افقی و آیکن رسمی 3DPrintHub.ir به رابط و Build ویندوز.
- افزودن نصب/ارتقای اتمیک با Backup امن SQLite و Rollback خودکار.
- اعتبارسنجی نام Batch، Schema `8.5`، UUID و Manifest پیش از FTP Upload.
- حفظ دیتابیس محلی، Windows Credential Store و Bridge نصب‌شده بدون Migration جدید.
