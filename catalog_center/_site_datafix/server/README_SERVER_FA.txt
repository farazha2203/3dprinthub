3DPrintHub Phase 43.1.0 — Catalog Metrics Data Fix

هدف
===
اصلاح امن داده‌های زمان چاپ MakerWorld که مقدار خام print_time بر حسب ثانیه
به اشتباه مستقیماً داخل estimated_print_minutes ذخیره شده است.

قواعد ایمنی
===========
- هیچ Migration اجرا نمی‌شود.
- هیچ flush یا loaddata اجرا نمی‌شود.
- هیچ رکوردی فقط با حدس تغییر نمی‌کند.
- فقط وقتی اصلاح انجام می‌شود که مقدار فعلی estimated_print_minutes دقیقاً
  با یک print_time خام MakerWorld تطبیق داشته باشد.
- قبل از Apply از همان ردیف‌هایی که قرار است تغییر کنند Backup JSON گرفته می‌شود.
- Rollback از همان Backup پشتیبانی می‌شود.
- اجرای پیش‌فرض Dry-run است.

مسیر Production
===============
/home/sfkilvrs/3dprinthub

Python Production
=================
/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python

اجرا روی هاست
=============
1) ZIP سرور را آپلود و Extract کنید.
2) ابتدا Dry-run:

bash INSTALL_PHASE43_DATAFIX_SERVER.sh --dry-run

3) بعد از بررسی خروجی، Apply:

bash INSTALL_PHASE43_DATAFIX_SERVER.sh --apply

Rollback
========
در زمان Apply مسیر Backup چاپ می‌شود. برای بازگردانی:

/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python   phase43_catalog_metrics_datafix.py   --project-root /home/sfkilvrs/3dprinthub   --rollback /PATH/TO/catalog_metrics_before.json

نکته
====
این بسته Phase43 Catalog Bridge را نصب نمی‌کند؛ وظیفه این بسته فقط اصلاح امن
داده‌های Catalog Metrics موجود سایت است.
