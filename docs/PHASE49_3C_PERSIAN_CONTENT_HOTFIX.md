# Phase49.3C-1 — Persian AI Content Integrity & Workspace Persistence

## هدف

رفع Regression مشاهده‌شده در Visual QA محصول واقعی که باعث می‌شد:

- عنوان فارسی/متن فارسی با متن انگلیسی منبع جایگزین شود.
- توضیح کوتاه فارسی پایدار نباشد.
- «توضیحات کاربرد محصول» خالی بماند.
- SEO Title/Description/Keywords/Tags/Hashtags/Alt فارسی نباشند.
- خروجی AI در DB وجود داشته باشد ولی در Tabهای Product Workspace نمایش داده نشود.
- تغییرات SEO در Workspace ذخیره نشوند.
- HTML توضیحات بدون کنترل وارد مسیر انتشار شود.

## Root Cause

### 1. Fallback انگلیسی
`phase49_3c_ai_recovery.py` وقتی خروجی AI ناقص بود، در بعضی مسیرها از `source_title` و `source_description` انگلیسی برای فیلدهای `_fa` استفاده می‌کرد. این رفتار از نظر schema معتبر بود ولی از نظر editorial غلط بود.

### 2. نبود `use_description_fa` در Structured Contract
`use_description` در Product موجود بود، اما AI Content Schema فیلد مستقل `use_description_fa` نداشت؛ بنابراین AI هیچ تعهدی برای تولید توضیح کاربرد محصول نداشت.

### 3. Workspace Reload/Save ناقص
Product Workspace واقعی از زنجیره `product_workspace_epic49 → product_workspace_v871 → product_workspace_v87 → epic49_product_studio_final` استفاده می‌کند. Tabهای SEO فیلدهای DB را داشتند، ولی Reload/Save عمومی همه این Widgetها را به‌صورت کامل round-trip نمی‌کرد. در نتیجه مقدار می‌توانست در DB باشد اما در Workspace خالی دیده شود، یا تغییر اپراتور به DB نرود.

### 4. نبود Language Gate
Structured Output صرفاً JSON/schema validity را کنترل می‌کرد؛ فارسی بودن محتوای editorial و SEO به‌عنوان Gate مستقل بررسی نمی‌شد.

## Repair Architecture

فایل جدید:

`catalog_center/app/phase49_3c_persian_content.py`

این ماژول بدون Migration جدید:

1. `use_description_fa` را به Structured Schema اضافه می‌کند.
2. خروجی AI را از نظر فارسی بودن فیلدهای editorial و SEO بررسی می‌کند.
3. در صورت انگلیسی/خالی بودن، یک Structured Repair Request با دستور صریح فارسی اجرا می‌کند.
4. در صورت Failure Provider، متن انگلیسی را هرگز به فیلد فارسی منتقل نمی‌کند.
5. Fallback فارسی محافظه‌کارانه می‌سازد و آن را `needs_review` نگه می‌دارد تا انتشار Silent انجام نشود.
6. `description_fa` را به HTML fragment محدود و sanitize می‌کند.
7. Workspace Reload را برای SEO/Tags/Hashtags/Keywords/Alt/Material Recommendations کامل می‌کند.
8. Workspace Save را برای همان فیلدها کامل می‌کند.
9. `use_description_fa → use_description` را Persist می‌کند.
10. Readiness را به Language Gate متصل می‌کند.
11. Snapshot زنده را برای `use_description` نیز به Widget فعلی متصل می‌کند.

## Persian Content Policy

فیلدهای زیر باید فارسی باشند:

- عنوان فارسی
- توضیح کوتاه فارسی
- توضیح کامل فارسی
- توضیحات کاربرد محصول
- SEO Title
- SEO Description
- Keywords
- Tags
- Hashtags
- Sales Bullets
- Social Caption
- Image Alt
- Slider SEO

کد فنی متریال مثل `PLA` و `PETG` در فیلدهای فنی/پیشنهاد متریال مجاز است، ولی نباید به‌عنوان عبارت جستجوی انگلیسی در SEO ساخته شود.

## HTML Contract

`description_fa` یک HTML fragment است و فقط این tagها اجازه دارند:

`p`, `br`, `strong`, `em`, `ul`, `ol`, `li`, `h3`, `h4`

موارد زیر حذف می‌شوند:

- script
- style
- iframe
- event handler
- URL جدید تولیدشده توسط AI
- attributeهای ناشناخته

اگر خروجی plain text باشد، به `<p>...</p>` تبدیل می‌شود.

این محدودسازی برای این است که HTML ذخیره‌شده از یک Provider یا منبع بیرونی مستقیماً وارد خروجی وب نشود. Django نیز باید HTML ذخیره‌شده را قبل از rendering به‌عنوان trusted content تلقی نکند مگر اینکه sanitize شده باشد.

## Readiness Contract

Content Stage تا وقتی این‌ها فارسی و غیرخالی نباشند سبز نمی‌شود:

- عنوان
- توضیح کوتاه
- توضیح کامل
- توضیحات کاربرد محصول
- SEO Title
- SEO Description
- Keywords
- Tags
- Hashtags

برای تصاویر انتخاب‌شده نیز تعداد Altهای فارسی باید حداقل برابر تعداد تصاویر انتخاب‌شده باشد.

## Tests

فایل جدید:

`catalog_center/tests/test_epic49_phase49_3c_persian_content.py`

پوشش:

- رد متن editorial انگلیسی
- جلوگیری از انتقال متن انگلیسی source به فیلد فارسی
- fallback فارسی
- وجود `use_description_fa` در schema بعد از install
- HTML sanitization
- HTML fragment generation
- فارسی بودن SEO fallback

## Migration

هیچ Django Migration جدیدی لازم نیست.

داده موجود Reset/Delete/Truncate نمی‌شود.

## Launch Markers

- `EPIC49_3C_PERSIAN_CONTENT_GUARD=ENABLED`
- `EPIC49_3C_PERSIAN_SEO=ENABLED`
- `EPIC49_3C_HTML_SANITIZATION=ENABLED`
- `EPIC49_3C_WORKSPACE_CONTENT_PERSISTENCE=ENABLED`

## QA Gate

Production همچنان ممنوع است.

Windows بعد از Pull باید این موارد را Verify کند:

1. Product واقعی را باز کند.
2. AI Global را اجرا کند.
3. عنوان/متن/توضیح کاربرد فارسی پر شود.
4. SEO Title/Description/Keywords/Tags/Hashtags فارسی باشند.
5. HTML توضیح کامل باقی بماند و tagهای مجاز را داشته باشد.
6. Save → Close/Reopen → همان مقادیر باقی بمانند.
7. تغییر دستی SEO → Save → Reopen → تغییر باقی بماند.
8. Readiness برای فیلد فارسی ناقص قرمز و برای تکمیل‌شده سبز باشد.
9. Local Publish هنوز قبل از تأیید نهایی کاربر انجام نشود.
