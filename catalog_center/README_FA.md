# 3DPrintHub Catalog Intelligence v8.5.4

نسخه v8.5 مرکز دریافت، بازبینی، ترجمه، تولید محتوا، SEO، پیشنهاد متریال و انتشار گروهی محصول است. انتشار سایت در این نسخه با FTP واقعی روی پورت 21 و Bridge امن HTTPS انجام می‌شود و هیچ SSH/SFTP در Desktop وجود ندارد.

## نصب یا ارتقا

برنامه را کامل ببندید، ZIP را باز کنید و `INSTALL_AND_RUN.ps1` را اجرا کنید. این فایل ابتدا `v8.5.4` را نصب و صحت نسخه و مسیر سورس را بررسی می‌کند، سپس همان نسخه نصب‌شده را اجرا می‌کند. نصب‌کننده قبل از تعویض سورس، از برنامه فعلی و دیتابیس SQLite با روش امن SQLite Backup نسخه پشتیبان می‌گیرد. دیتابیس در مسیر مستقل خودش باقی می‌ماند و اطلاعات قبلی حذف یا جایگزین نمی‌شوند.

لانچر نسخه `v8.5.4` همیشه فایل `launch.py` را با مسیر مطلق اجرا می‌کند. بنابراین حتی اگر PowerShell داخل پوشه‌ای قدیمی مانند `3dprinthub_catalog_center_v8_5_1_test` باشد، پکیج `app` نسخه قدیمی نمی‌تواند برنامه نصب‌شده را سایه بیندازد.

مسیر برنامه پس از نصب:

`D:\projects\3dprinthub_catalog_center`

مسیر Backupها:

`D:\projects\3dprinthub-backups`

Rollback فقط در صورت نیاز:

```powershell
Set-Location "D:\projects\3dprinthub_catalog_center"
& "D:\projects\3DPrintHub\.venv\Scripts\python.exe" "D:\projects\3dprinthub_catalog_center\app\upgrade.py" --rollback
```

Rollback آخرین نسخه پشتیبان ثبت‌شده را برمی‌گرداند.

## کنترل نسخه فعال

پیش از بازشدن پنجره، `RUN.ps1` باید این سه مقدار را چاپ کند:

```text
ACTIVE_VERSION=8.5.4
ACTIVE_BUILD=2026.08.10.2
ACTIVE_SOURCE=D:\projects\3dprinthub_catalog_center
```

همین مسیر فایل فعال و Build داخل سربرگ سرمه‌ای/طلایی برنامه نیز نمایش داده می‌شود.

## اتصال سایت

در تب تنظیمات، Host، Port، Username، Password، مسیر FTP، آدرس سایت و Bridge Token را وارد کنید. برای Bridge Token می‌توانید از `Ctrl+V`، `Shift+Insert`، راست‌کلیک و گزینه «چسباندن»، یا دکمه «چسباندن توکن» استفاده کنید. برنامه هم خود توکن و هم خط کامل `CATALOG_BRIDGE_TOKEN=...` را می‌پذیرد و فقط مقدار بعد از `=` را ذخیره می‌کند. دکمه «نمایش/مخفی» برای کنترل مقدار واردشده در دسترس است. Password و Token فقط در Windows Credential Store ذخیره می‌شوند و وارد SQLite یا Log نمی‌شوند. قبل از انتشار، دکمه‌های «تست اتصال FTP» و «تست Bridge سایت» را اجرا کنید.

## عیب‌یابی PowerShell

`RUN_DEBUG.ps1` مسیر برنامه، نسخه، SQLite، DNS، TCP پورت 21، ورود FTP، سلامت Bridge و تمام خطاهای Python را در PowerShell و پوشه `D:\projects\3dprinthub-catalog-manager\logs` ثبت می‌کند. اطلاعات حساس ماسک می‌شوند.

## کالاهای بلاک‌شده

«بلاک و انتقال» رکورد را حذف نمی‌کند. کالا از فهرست‌های عادی، AI، بازیابی منبع، صف انتشار و Batch خارج می‌شود و در تب مستقل کالاهای بلاک‌شده قابل بازگردانی است.

## مسیر داده اصلی
دیتابیس برنامه مستقل از پوشه برنامه است:

`D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`

## AI
Providerهای قابل انتخاب:
- `auto` — ابتدا AvalAI، سپس OpenAI Direct
- `avalai` — `https://api.avalai.ir/v1`
- `openai` — `https://api.openai.com/v1`

مدل Hard-code نشده است. دکمه «دریافت مدل‌ها» لیست مدل‌های قابل دسترس همان API Key را می‌گیرد.

کلیدها می‌توانند از این منابع خوانده شوند:
1. Environment Variable
2. Windows Credential Store
3. `D:\projects\3DPrintHub\APIKEY-AVAL.txt`
4. `D:\projects\3DPrintHub\APIKEY.txt`

Secret در SQLite، Batch و Log ذخیره نمی‌شود.

### تست آفلاین/قراردادی
```powershell
& "D:\projects\3dprinthub_catalog_center\SELF_TEST.ps1"
```

### تست زنده AvalAI/OpenAI
این تست از اعتبار API واقعی استفاده می‌کند:
```powershell
& "D:\projects\3dprinthub_catalog_center\LIVE_AI_TEST.ps1" -Provider avalai
```

## جریان یک محصول
1. لینک بده یا از منبع کشف کن.
2. بازیابی کامل: عنوان، توضیح، تصاویر، فایل‌ها، دسته، وزن، مشخصات.
3. تصاویر را انتخاب و Primary تعیین کن.
4. AI: ترجمه + محتوای فروشگاهی + SEO + هشتگ + پیشنهاد متریال.
5. وزن و قیمت نهایی را بازبینی کن.
6. گروه سایت را انتخاب کن.
7. مجوز را بررسی کن.
8. محصول را به صف Upload بفرست.
9. فقط اگر ACK سایت شناسه واقعی Product/Portfolio درخواستی را برگرداند، Desktop آن را Published می‌کند.

مجوز انتشار فقط یکی از این سه وضعیت است: `allowed`، `owned` یا `public_domain`.
وضعیت‌های `review`، `blocked` و `unknown` وارد Batch انتشار نمی‌شوند.

## استخراج از سایت
زنجیره استخراج:
- adapter اختصاصی سایت
- JSON-LD Product
- embedded JSON / Next.js data
- OpenGraph/meta
- DOM واقعی بعد از JavaScript
- breadcrumb/specification tables
- تصاویر lazy/srcset
- public JSON/XHR که خود صفحه دریافت می‌کند
- فایل‌های عمومی قابل مشاهده

برنامه CAPTCHA را دور نمی‌زند و fingerprint/stealth bypass انجام نمی‌دهد. در صورت Login، کاربر می‌تواند در Browser واقعی Login کند.

## Phase39
Importer v8.5 اگر Phase39 روی سایت نصب باشد، به‌صورت اختیاری هشتگ، لینک منبع و پیشنهادهای متریال AI را به Product سایت منتقل می‌کند و جزئیات سفارش نسخه 8.5 را نیز بدون Migration جدید در اطلاعات فنی محصول نگه می‌دارد.
