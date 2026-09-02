# ai — Shared AI Runtime / Playbook

این پوشه مرجع مشترک تجربه‌های AI پروژه است و عمداً از UI یا دیتابیس یک پروژه خاص مستقل نگه داشته می‌شود.

## قرارداد دائمی

1. Secret فقط از Environment/Secret Store خوانده می‌شود؛ API Key داخل Git، Django Admin، SQLite یا Log ذخیره نمی‌شود.
2. برای Product/SEO خروجی باید Structured JSON باشد و قبل از ذخیره Schema + Semantic validation انجام شود.
3. انتخاب مدل متغیر Router مثل `openrouter/free` یا `openrouter/auto*` به‌عنوان مدل Product نهایی ممنوع است.
4. اگر مدل صریح در Environment تنظیم شده باشد همان مدل استفاده می‌شود؛ تعویض مخفی مدل/Provider انجام نمی‌شود.
5. در حالت Auto، اول مدل رایگان text/Structured که Probe فارسی را Pass کند انتخاب می‌شود؛ اگر موجود نبود فقط مدل کم‌هزینه زیر Budget مجاز بررسی می‌شود.
6. AI حق ساختن Price، Stock، Dimensions، Weight، Material/Color، License، Compatibility یا Publish state را ندارد.
7. پیشنهاد AI ابتدا Preview می‌شود و اعمال آن نیاز به تأیید صریح اپراتور دارد.
8. Provider/Model diagnostics ممکن است در Admin/Audit دیده شود ولی نباید وارد متن عمومی Product شود.
9. یک Failure شبکه/Provider نباید به معنی Failure تمام مدل‌ها نمایش داده شود و retry بی‌نهایت ممنوع است.
10. هر پروژه Adapter دامنه خودش را دارد ولی Model Policy و Safety Contract باید مشترک بماند.

## Environment پیشنهادی

- `OPENROUTER_API_KEY` — انتخاب اول برای Free/Low-cost model discovery.
- `AI_SITE_PROVIDER=openrouter` — اختیاری؛ اگر خالی باشد Provider بر اساس Secret موجود انتخاب می‌شود.
- `AI_SITE_PRODUCT_MODEL=<exact-model-id>` — اختیاری؛ برای Pin کردن مدل.
- `AI_SITE_MAX_TOTAL_USD_PER_1M=2.0` — سقف مجموع Input+Output برای fallback پولی Auto.
- `AI_SITE_MODEL_CACHE_SECONDS=21600` — Cache انتخاب مدل در Process.
- `AI_SITE_MODEL_PROBE_LIMIT=4` — سقف Probe مدل‌ها.

## 3DPrintHub

- `ai/model_policy.py`: انتخاب دقیق Provider/Model با اولویت Free Persian Structured.
- `ai/product_content.py`: Adapter محصول 3DPrintHub.
- همان `catalog_center.app.ai_providers.AIProviderClient` و `AIContentService` بالغ Windows دوباره استفاده می‌شود؛ Provider جدید موازی ساخته نشده است.
- Host Admin فقط Content/SEO را با AI تغییر می‌دهد. Pricing/Stock/Material/Color/License همچنان تحت اختیار Business Engine/Operator است.

## اعمال برای پروژه‌های دیگر

این پوشه الگوی Canonical است، اما هیچ Repository دیگری بدون خواندن `AGENTS.md` و Verify کردن معماری همان پروژه تغییر داده نمی‌شود. برای هر پروژه:
1. همین Model Policy/Safety Contract reuse شود.
2. Adapter جداگانه برای Domain آن پروژه نوشته شود.
3. Secret names از Environment همان پروژه Map شوند.
4. Structured schema و semantic validators مخصوص Domain تعریف شوند.
5. CI با Provider mock و بدون Secret واقعی اجرا شود.
6. بعد از Local acceptance، Deploy از GitHub انجام شود.

این روش اجازه می‌دهد تجربه‌های این فاز به همه پروژه‌ها منتقل شوند بدون اینکه کد Business یک پروژه کورکورانه داخل پروژه دیگر کپی شود.
