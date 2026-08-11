# گزارش خطاها و قواعد اجرای فاز 34B — 3DPrintHub

تاریخ ثبت: 2026-08-03

## مسیرهای قطعی پروژه

- سورس توسعه:
  `D:\projects\3DPrintHub`

- آینه فقط‌خواندنی هاست:
  `D:\projects\3dprinthub-houst`

- پروژه Production:
  `/home/sfkilvrs/3dprinthub`

- GitHub:
  `farazha2203/3dprinthub`

## نتیجه Environment Map

- Development files: 4190
- Host mirror files: 406
- Same: 32
- Different: 37
- Development only: 4121
- Host only: 337
- Status: `ENVIRONMENT_MAP_COMPLETE=OK`

این اختلاف زیاد به‌تنهایی خطا نیست. پوشه توسعه شامل فایل‌های بیشتری است و آینه هاست فقط سورس انتخاب‌شده Production را دارد. برای Deploy فقط فایل‌های فاز و مسیرهای مجاز بررسی می‌شوند؛ کل دو پوشه روی هم کپی نمی‌شوند.

---

## خطا 1 — استفاده از متغیر `$Host`

### پیام

`Cannot overwrite variable Host because it is read-only or constant.`

### علت

PowerShell متغیر داخلی و فقط‌خواندنی `$Host` دارد و حروف بزرگ و کوچک را یکسان می‌بیند. بنابراین `$host` نیز قابل استفاده به‌عنوان متغیر معمولی نیست.

### اصلاح

نام متغیر به این موارد تغییر کرد:

- `$DevelopmentFiles`
- `$HostFiles`

### قانون آینده

در اسکریپت‌های PowerShell از نام‌های زیر به‌عنوان متغیر استفاده نشود:

- `$Host`
- `$Error`
- `$PID`
- `$HOME`
- `$PROFILE`
- `$PSVersionTable`
- `$LASTEXITCODE`

---

## خطا 2 — ناسازگاری `String.Contains` با PowerShell 5.1

### پیام

`Cannot find an overload for "Contains" and the argument count: "2".`

### علت

نسخه قدیمی .NET روی Windows PowerShell 5.1 متد زیر را پشتیبانی نمی‌کند:

`String.Contains(value, StringComparison)`

### اصلاح

با این روش سازگار جایگزین شد:

`String.IndexOf(value, StringComparison) -ge 0`

### قانون آینده

تمام اسکریپت‌های PowerShell باید با Windows PowerShell 5.1 سازگار باشند. قبل از تحویل نباید از APIهای فقط PowerShell 7 یا .NET جدید استفاده شود.

---

## خطا 3 — استفاده از `GetRelativePath`

### پیام

`System.IO.Path does not contain a method named GetRelativePath.`

### علت

`Path.GetRelativePath` در نسخه .NET سیستم موجود نبود.

### اصلاح

مسیر نسبی با `Substring` و حذف جداکننده ابتدایی محاسبه شد.

### قانون آینده

در PowerShell 5.1 از `Path.GetRelativePath` استفاده نشود.

---

## خطا 4 — خراب‌شدن متن فارسی داخل PowerShell

### پیام

`Unexpected token` همراه با حروف خراب‌شده مانند `Ø®Ø±...`

### علت

فایل PowerShell با Encoding ناسازگار ذخیره شده بود.

### اصلاح

تمام اسکریپت‌های عملیاتی PowerShell و Bash فقط با متن ASCII/English ساخته شدند.

### قانون آینده

- پیام‌های داخل `.ps1` و `.sh` فقط انگلیسی باشند.
- فایل‌های PowerShell با ASCII یا UTF-8 BOM کنترل‌شده ذخیره شوند.
- متن فارسی فقط در مستندات Markdown باشد.

---

## خطا 5 — اتصال پروژه محلی به MySQL Production

### پیام

`Can't connect to MySQL server on 'localhost'`

### علت

فایل `.env` محلی، پروژه ویندوز را به MySQL تنظیم کرده بود؛ اما MySQL محلی اجرا نمی‌شد.

### اصلاح موردنیاز

تست فازها فقط در Worktree جدا و با `.env` آزمایشی SQLite انجام شود.

### قانون آینده

- `.env` اصلی پروژه برای تست فاز تغییر نکند.
- Worktree هر فاز `.env` مستقل داشته باشد.
- پایگاه داده تست محلی SQLite باشد.
- تنظیمات Production فقط روی هاست استفاده شود.

---

## خطا 6 — Branch محلی واگرا با `origin/main`

### پیام

`Not possible to fast-forward, aborting.`

### علت

شاخه `main` محلی و GitHub تاریخچه متفاوت داشتند.

### اصلاح

فازها از Worktree جدید بر پایه `origin/main` ساخته می‌شوند و مستقیماً روی `main` محلی قدیمی توسعه داده نمی‌شوند.

### قانون آینده

مسیر استاندارد:

1. `git fetch origin`
2. ساخت Worktree از `origin/main`
3. ساخت Branch فاز
4. تست
5. Commit و Push
6. Merge و Tag

---

## خطا 7 — اجرای تست فازی که هنوز ساخته نشده بود

### پیام

`ModuleNotFoundError: No module named 'store.test_phase34b'`

### علت

قبل از ساخت کد واقعی فاز 34B، دستور تست اعلام شده بود.

### قانون آینده

هیچ دستور زیر قبل از وجود واقعی فایل‌ها ارائه نشود:

- Migration
- تست اختصاصی
- Merge
- Tag
- Deploy

فایل‌های فاز باید قبل از دستور اجرا داخل Payload موجود و با Preflight کنترل شوند.

---

## خطا 8 — نبودن `rsync` روی هاست اشتراکی

### پیام

`STOP: required command not found: rsync`

### علت

هاست اشتراکی ابزار `rsync` نداشت.

### اصلاح

Deploy با Python استاندارد و Copy کنترل‌شده بدون `rsync` نوشته شد.

### قانون آینده

اسکریپت Deploy هاست نباید به ابزارهای زیر وابسته باشد مگر ابتدا وجودشان کنترل شود:

- rsync
- sudo
- systemctl
- supervisorctl
- docker

---

## خطا 9 — Migration Drift فاز 33

### پیام

Django قصد ساخت Migration برای کاهش طول URLها و حذف Index داشت.

### علت

Payload فاز 33 سه تعریف Model قدیمی‌تر از Migrationهای رسمی را بازگردانده بود.

### اصلاح

- `ImportedPrintAsset.source_url = 1000`
- `CatalogSeedURL.url = 1200`
- `CustomerLinkAnalysis.normalized_url` با `db_index=True`

### قانون آینده

قبل از اجرای `makemigrations --check` باید تعریف مدل‌ها با آخرین Migration رسمی تطبیق داده شود. Migration جدید نباید صرفاً برای پنهان‌کردن Drift ساخته شود.

---

## خطا 10 — بازگشت وضعیت Sync از `partial` به `running`

### علت

`refresh_from_db()` وضعیت نهایی محاسبه‌شده را با مقدار قدیمی دیتابیس جایگزین می‌کرد.

### اصلاح

وضعیت لغو با Query فقط‌خواندنی بررسی شد و وضعیت نهایی حفظ شد.

### قانون آینده

بعد از محاسبه وضعیت نهایی Job، از `refresh_from_db(fields=["status"])` استفاده نشود مگر عمداً قصد بازنویسی وضعیت وجود داشته باشد.

---

# قواعد ثابت اجرای فازهای بعدی

1. آینه هاست فقط‌خواندنی است.
2. توسعه فقط داخل Worktree بر پایه `origin/main` انجام می‌شود.
3. هر فاز باید Preflight داشته باشد.
4. همه اسکریپت‌های عملیاتی ASCII باشند.
5. سازگاری Windows PowerShell 5.1 اجباری است.
6. تست محلی با SQLite مستقل انجام شود.
7. هیچ Commit یا Push قبل از موفقیت کامل تست‌ها انجام نشود.
8. Deploy فقط از Tag مشخص GitHub انجام شود.
9. قبل از Deploy، Backup سورس و MySQL اجباری است.
10. بعد از Deploy، آینه هاست تازه و Environment Map دوباره ساخته شود.
11. `.env`، Media، Private Media و فایل‌های Runtime هیچ‌وقت با Git جایگزین نشوند.
12. هر فاز پس از پایان باید در `PROJECT_CONTEXT.md` و این گزارش ثبت شود.

# مرحله بعد

اجرای محلی فاز 34B با:

`RUN_PHASE34B_LOCAL.ps1`

فقط پس از مشاهده نتیجه زیر اجازه ورود به GitHub دارد:

`PHASE34B_LOCAL_TESTS_AND_PUSH=OK`
