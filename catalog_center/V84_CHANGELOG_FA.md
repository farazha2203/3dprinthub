# 3DPrintHub Catalog Intelligence v8.4.1

## اصلاحات ایمنی انتشار 8.4.1
- جلوگیری از صف و Export محصول با مجوز `review`، `blocked` یا `unknown`.
- Published شدن فقط با ACK دارای شناسه واقعی Product/Portfolio درخواستی.
- حفظ ترتیب دقیق تصویر محلی و URL در Batch برای جلوگیری از اتصال تصویر اشتباه.
- اعتبارسنجی نسخه Schema و جلوگیری از خروج مسیر Editorial از پوشه Batch.

## AI Provider
- AvalAI + OpenAI Direct + Auto
- مدل ثابت حذف شد؛ مدل‌های واقعی Key از `/v1/models` دریافت می‌شوند.
- خواندن امن `APIKEY-AVAL.txt` و `APIKEY.txt` از `D:\projects\3DPrintHub`.
- انتقال Secret به Windows Credential Store.
- `LIVE_AI_TEST.ps1` برای تست واقعی مدل، ترجمه، محتوا، SEO و پیشنهاد متریال.

## استخراج
- خواندن JSON-LD، embedded JSON/Next data، OpenGraph، DOM و public XHR/JSON.
- بازیابی بهتر title/description/weight/specifications/categories/images/files.
- هیچ bypass برای CAPTCHA یا fingerprinting انجام نمی‌شود.

## تولید محتوا
- عنوان، توضیح کوتاه/کامل، مشخصات فارسی، دسته‌ها، Tag، SEO، Alt، کپشن و هشتگ.
- پیشنهاد متریال با use-case و دلیل؛ جلوگیری از پیشنهاد متریال Overkill مثل PPS-CF برای دکور عادی.
- هشتگ و پیشنهاد متریال داخل Content Studio قابل مشاهده/ویرایش است.

## اتصال سایت
- Batch schema 8.4 و ACK.
- Optional bridge با Phase39: source URL، hashtags و material recommendation روی Product سایت اعمال می‌شوند.
