# Phase 49.3A — Product Publish Readiness Wizard

## هدف

این فاز برای جلوگیری از انتشار محصول ناقص و برای ساده‌کردن کار اپراتور Windows Catalog Center اجرا شد. وضعیت هر مرحله از روی دیتای واقعی Product محاسبه می‌شود و در منوی سمت راست Workspace با ✅ / ❌ نشان داده می‌شود.

## UI / آیکون‌ها

منوی راست Product Workspace:

- ✅ مرحله کامل
- ❌ مرحله ناقص
- `مرحله بعد: ...` برای رفتن به اولین مرحله ناقص
- `✨ پیشنهاد AI برای موارد ناقص`
- `🧪 انتشار آزمایشی روی کامپیوتر`
- `🌐 انتشار واقعی روی سایت اصلی`

کتابخانه آیکون جدید اضافه نشده است؛ UI از Tk/ttk موجود و Emoji status marker استفاده می‌کند.

## Readiness Engine

فایل:

`catalog_center/app/phase49_readiness_wizard.py`

Stageها:

1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. بررسی و انتشار

### اطلاعات پایه

Gateهای اصلی:

- عنوان فارسی
- گروه سایت معتبر
- نوع محصول

### سفارش، قیمت و گزینه‌ها

- قیمت معتبر یا حالت سفارش/نمونه‌کار
- حداقل یک متریال واقعی
- حداقل یک رنگ واقعی

### تصاویر

- تصویر اصلی
- حداقل یک تصویر انتخاب‌شده برای سایت

### محتوا و SEO

- عنوان فارسی
- توضیح فارسی
- SEO Title فارسی
- SEO Description فارسی
- حداقل 3 عبارت هدف SEO
- حداقل یک Alt تصویر

### منبع و مجوز

- URL منبع
- مجوز تجاری قابل انتشار

### بررسی و انتشار

- تأیید برای فروش
- نوع انتشار Product
- اگر Slider فعال باشد: عنوان، توضیح، Alt، Focus Keyword و عکس Slider نیز اجباری‌اند.

## Publish gating

Local Test در UI همیشه قابل مشاهده است و مسیر خودش را دارد. Production Publish فقط وقتی `production_ready=True` باشد فعال می‌شود.

اگر API/Callback مستقیم Production فراخوانی شود، Readiness Engine دوباره بررسی می‌شود و در صورت ناقص بودن عملیات متوقف و اپراتور به اولین Stage ناقص هدایت می‌شود.

## SEO — Editable Lists

سه لیست مورد سؤال اپراتور:

- کلمات کلیدی سایت
- متریال‌های محصول
- رنگ‌های محصول

رفتار جدید:

- متریال و رنگ از Checkboxهای واقعی Product می‌آیند؛ AI اجازه اختراع متریال/رنگ ندارد.
- `materials_json` و `colors_json` با انتخاب‌های واقعی همگام می‌شوند.
- اگر `keywords_json` خالی باشد، یک fallback فروش‌محور از عنوان + متریال + رنگ واقعی ساخته می‌شود.
- Meta Keywords قدیمی هدف نیست؛ این لیست به‌عنوان بانک عبارت‌های هدف برای SEO Title/Description، محتوا، Alt، Internal Search و برنامه‌ریزی محتوا استفاده می‌شود.

نمونه fallback:

- خرید گکو مفصلی سه بعدی
- سفارش گکو مفصلی سه بعدی
- قیمت گکو مفصلی سه بعدی
- گکو مفصلی سه بعدی PLA
- گکو مفصلی سه بعدی شفاف

## AI schema

فایل:

`catalog_center/app/openai_content.py`

افزوده شد:

- `target_keywords_fa`
- ورودی factual: `selected_materials`
- ورودی factual: `selected_colors`

AI باید 5 تا 12 عبارت هدف طبیعی و فروش‌محور پیشنهاد کند و فقط از Material/Color واقعی ورودی استفاده کند. `target_keywords_fa` برای keyword stuffing یا meta-keywords منسوخ استفاده نمی‌شود.

## AI Apply bridge

`install_app()` در `phase49_readiness_wizard.py` متد `_apply_ai_pack` را wrap می‌کند:

- عبارت‌های AI در `keywords_json` می‌نشینند.
- Material/Color واقعی Product در `materials_json/colors_json` می‌نشینند.
- اگر AI عبارت هدف نداد، fallback deterministic استفاده می‌شود.

## دکمه تکمیل هوشمند

`✨ پیشنهاد AI برای موارد ناقص`:

1. تغییرات فعلی را ذخیره می‌کند.
2. Material/Color/Keyword reference list را همگام می‌کند.
3. اگر Content/SEO هنوز ناقص باشد، AI Commerce workflow موجود را باز می‌کند.
4. اپراتور قبل از Apply خروجی AI را بررسی می‌کند.

اطلاعات دستی موجود بدون انتخاب اپراتور silently جایگزین نمی‌شوند.

## دیتابیس

Phase49.3A Migration جدید ندارد.

Readiness state Runtime-calculated است.

از دیتای پایدار موجود استفاده می‌شود:

- material_options_json
- color_options_json
- materials_json
- colors_json
- keywords_json
- SEO fields
- Slider SEO fields
- publish/license fields

Migration فعال قبلی Rich Color همچنان:

`store.0031_phase49_rich_material_colors`

## Launcher

`catalog_center/launch.py`

Install order:

1. Persian Sales
2. Dual Publish
3. Material/Color Picker
4. Readiness Wizard
5. UX87 route → final Epic49 ProductWorkspace

Markerها:

- `EPIC49_READINESS_WIZARD=ENABLED`
- `EPIC49_SEO_REFERENCE_SYNC=ENABLED`

## فایل‌های اصلی

- `catalog_center/app/phase49_readiness_wizard.py`
- `catalog_center/app/openai_content.py`
- `catalog_center/launch.py`
- `catalog_center/tests/test_epic49_readiness_wizard.py`
- `.github/workflows/phase49-epic-ci.yml`
- `docs/PHASE49_3A_PRODUCT_PUBLISH_READINESS.md`
- `PROJECT_CONTEXT.md`

## تست

Final Self-Test:

- GitHub Actions Run: `32234579086`
- Job: `96011595438`
- Result: SUCCESS

Gateها:

- Compile: PASS
- Django check / migration contract: PASS
- Phase49 targeted regression: PASS
- Windows Catalog Center including `test_epic49_readiness_wizard`: PASS
- Full Django suite: PASS

## Production

این فاز هنوز روی Production Deploy نشده است.

مسیر بعدی:

Windows Pull → Visual QA Wizard → یک Product واقعی → Local Publish → بررسی Django Local → تأیید کاربر → Production plan.
