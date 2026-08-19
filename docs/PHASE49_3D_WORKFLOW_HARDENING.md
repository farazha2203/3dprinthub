# Phase49.3D — Product Workspace / AI Provider / Local Publish / Price Range Hardening

## هدف

این فاز از Visual QA واقعی Windows شروع شد و شش Regression/نیاز عملیاتی را یکجا و بدون دست‌کاری Production برطرف می‌کند:

1. خطای `TclError: cannot use geometry manager pack ... already has slaves managed by grid` هنگام بازشدن Product Workspace.
2. انتخاب سخت مدل‌های AI در Providerهایی که صدها مدل برمی‌گردانند.
3. نبود Search/Filter مدل، Provider فعال واضح و ذخیره پایدار Provider+Model.
4. Local Publish که در صورت Readiness failure به Stage تصاویر برمی‌گشت ولی دلیل واضح نمایش نمی‌داد.
5. نیاز به قیمت حرفه‌ای به شکل حداقل/حداکثر وقتی زمان چاپ دقیق مشخص نیست.
6. آماده‌سازی اولیه خودکار AI برای ترجمه فارسی، کاربرد محصول و SEO بدون مصرف تکراری بی‌دلیل API.

Production در این فاز تا زمان Windows Local QA و تأیید صریح کاربر ممنوع است.

## Root causeهای تأییدشده

### Workspace layout

`product_studio._quick_ui()` از `grid()` روی `quick_tab` استفاده می‌کند، اما Phase49.3B برای پنل «ترجمه فقط عنوان» مستقیماً روی همان parent از `pack()` استفاده می‌کرد. Tkinter اجازه ترکیب `pack` و `grid` در یک parent مشترک را نمی‌دهد.

### AI model selection

Provider Hub فقط یک `ttk.Combobox` ساده داشت. API می‌توانست صدها مدل برگرداند، اما Search/Filter، شمارنده، فیلتر رایگان و Model Picker مستقل وجود نداشت. همچنین Label تزئینی مدل مثل `model-id • رایگان` می‌توانست در برخی مسیرها به‌جای model id خام persist شود.

### Silent Local Publish

Local Publish از `queue_for_publish(notify=False)` استفاده می‌کرد. اگر Save باعث stale شدن Image SEO metadata یا Readiness failure می‌شد، مرحله ناقص انتخاب می‌شد ولی پیام دلیل نمایش داده نمی‌شد.

### Price range

زیرساخت `price_min/price_max` از قبل در Desktop SQLite، Batch و `ProductCatalogProfile` وجود داشت و صفحه جزئیات سایت نیز Range را نمایش می‌داد؛ نقص اصلی نرمال‌سازی Save و نمایش Range روی کارت‌های Store بود. بنابراین Django migration جدید ایجاد نشد.

## Implementation

### 1. `catalog_center/app/phase49_3d_workflow_hardening.py`

- Stage 1 title-AI panel اکنون در parent grid-managed با `grid()` ساخته می‌شود.
- Desktop additive fields:
  - `ai_auto_prepare_hash`
  - `ai_auto_prepare_status`
  - `ai_auto_prepare_at`
- هیچ Reset/Delete روی SQLite انجام نمی‌شود.

### 2. Searchable AI Model Picker

برای AvalAI / OpenRouter / OpenAI:

- فهرست کامل `list_model_info()` Provider دریافت می‌شود؛ UI سقف مصنوعی روی تعداد مدل ندارد.
- Search زنده روی `name` و `model_id`.
- Aliasهای جستجو:
  - `CHATGPT` / `GPT` → GPT/OpenAI models
  - Claude
  - Gemini
  - Grok
  - DeepSeek
  - Qwen
  - Llama
  - Mistral
- فیلتر «فقط مدل‌های رایگان».
- شمارنده `مدل نمایش داده‌شده / کل مدل دریافت‌شده`.
- Double-click یا دکمه انتخاب، model id خام را ذخیره می‌کند.

### 3. Active Provider + Model

- Radio Button مستقل برای هر Provider.
- دکمه صریح `ذخیره Provider و مدل فعال`.
- ذخیره پایدار:
  - `ai_provider`
  - `ai_model`
  - `ai_model_<provider>`
- API Key تایپ‌شده فقط در Secure Secret Store ذخیره می‌شود؛ داخل Git/SQLite audit قرار نمی‌گیرد.
- Test Connection فعال دقیقاً با همان Provider/Model انتخابی اجرا می‌شود و تعداد مدل‌های Provider را گزارش می‌کند.

### 4. Auto AI Prepare on Product Open

وقتی Product Workspace باز می‌شود و گزینه فعال باشد:

- اگر محتوای فارسی/SEO کامل است، درخواست AI ارسال نمی‌شود.
- اگر ناقص است، Source fingerprint ساخته می‌شود.
- فقط وقتی Source/Relevant facts تغییر کرده یا هنوز برای این fingerprint پردازش نشده، AI اجرا می‌شود.
- Fail همان fingerprint خودکار Loop نمی‌شود تا API credit بی‌دلیل مصرف نشود؛ Retry دستی ممکن است.
- خروجی موفق مستقیم در فیلدهای Product اعمال و Workspace reload می‌شود.
- `similar_editorial_keywords` از محصولات Reviewشده همان category جمع می‌شود و فقط به‌عنوان editorial hint به AI داده می‌شود؛ این Keywords اجازه Override واقعیت محصول را ندارند.

AI همچنان حق جعل این موارد را ندارد:
- قیمت
- مجوز
- ابعاد
- موجودی
- رنگ انتخاب‌شده
- متریال انتخاب‌شده

### 5. Local/Production Publish Preflight

قبل از هر Publish:

1. Save واقعی.
2. Readiness دوباره از state ذخیره‌شده محاسبه می‌شود.
3. اگر فقط Image SEO/Metadata stale باشد و تصویر اصلی/منتخب واقعی موجود باشد، `finalize_selected_images()` یک‌بار خودکار اجرا می‌شود.
4. Readiness دوباره محاسبه می‌شود.
5. اگر هنوز ناقص باشد:
   - هیچ Batch/FTP/Import اجرا نمی‌شود.
   - دقیقاً اولین Stage ناقص باز می‌شود.
   - تمام Missing reasonهای مهم در Dialog نمایش داده می‌شود.
   - `preflight_blocked` در Audit Log ثبت می‌شود.

بنابراین Local Publish دیگر نباید بی‌صدا فقط به تصاویر برگردد.

### 6. Price Range

Desktop Save:
- حداقل/حداکثر اگر معکوس باشند مرتب می‌شوند.
- اگر فقط یکی وارد شده باشد، مقدار دوم برابر همان می‌شود.
- اگر Range خالی ولی `final_price/suggested_price` وجود داشته باشد، Range ثابت از آن ساخته می‌شود.

Server:
- `ProductCatalogProfile.price_min/price_max/price_mode` موجود و حفظ شده است.
- `product_detail.html` قبلاً Range را نمایش می‌داد.
- `product_list.html` اکنون اگر `price_max > price_min` باشد، متن `بازه قیمت` و هر دو مقدار را نمایش می‌دهد.
- `store/test_phase49_3d_price_range.py` List و Detail را تست می‌کند.

### 7. Image Download Limit

درخواست کاربر این بود که اگر گزینه موجود است تغییر داده نشود.

وضعیت فعلی حفظ شد:
- per-product `download_image_limit` موجود است.
- مقدار انتخابی کمتر از hard cap محترم است.
- hard cap فاز 49.3C برابر 10 تصویر است.
- Regression test ثابت می‌کند انتخاب 5 → فقط 5 URL و انتخاب بالاتر از 10 → حداکثر 10.

## Files

- `catalog_center/app/phase49_3d_workflow_hardening.py`
- `catalog_center/app/openai_content.py`
- `catalog_center/launch.py`
- `catalog_center/tests/test_epic49_phase49_3d_workflow_hardening.py`
- `store/test_phase49_3d_price_range.py`
- `templates/store/product_list.html`
- `.github/workflows/phase49-epic-ci.yml`
- `PROJECT_CONTEXT.md`

## Launcher markers

- `EPIC49_3D_WORKSPACE_LAYOUT_FIX=ENABLED`
- `EPIC49_3D_AI_MODEL_PICKER=ENABLED`
- `EPIC49_3D_ACTIVE_PROVIDER_PERSISTENCE=ENABLED`
- `EPIC49_3D_AUTO_AI_PREPARE=ENABLED`
- `EPIC49_3D_LOCAL_PUBLISH_PREFLIGHT=ENABLED`
- `EPIC49_3D_PRICE_RANGE_CONTRACT=ENABLED`
- `EPIC49_3D_IMAGE_LIMIT_PRESERVED=ENABLED`

## Environment note — django-admin-expert

طبق سیاست پروژه، قبل از این فاز Plugin directory برای `django-admin-expert` بررسی شد. Plugin/Skill مستقلی با همین نام در Session فعلی موجود نبود و نتیجه‌های Search نامرتبط بودند؛ بنابراین هیچ Plugin اشتباهی نصب نشد و ادعای نصب نیز ثبت نمی‌شود. Django/Admin validation بر اساس Source واقعی همین Repository و تست‌های Django انجام می‌شود.

## Gate

- [x] Root cause Workspace geometry manager مشخص شد.
- [x] Grid-safe Workspace repair پیاده‌سازی شد.
- [x] Searchable full model picker پیاده‌سازی شد.
- [x] Provider radio + persistent Provider/Model پیاده‌سازی شد.
- [x] Active Provider/Model live connection test پیاده‌سازی شد.
- [x] Auto AI prepare با source fingerprint پیاده‌سازی شد.
- [x] Similar Persian keyword hints اضافه شد.
- [x] Local Publish explicit preflight/error reporting پیاده‌سازی شد.
- [x] Auto image metadata finalization در publish preflight اضافه شد.
- [x] Desktop price range normalization پیاده‌سازی شد.
- [x] Store list/detail price range contract تست شد.
- [x] Image download limit behavior بدون تغییر عملکرد اصلی پوشش تست دارد.
- [x] Dedicated Windows + Django tests به CI اضافه شد.
- [ ] Final GitHub CI برای HEAD نهایی verified.
- [ ] Windows pull/backup/compile/tests.
- [ ] Product Workspace visual open بدون TclError.
- [ ] Live Provider model list/search/test QA.
- [ ] Auto AI prepare real-product QA.
- [ ] Local Publish E2E.
- [ ] Explicit user approval.
- [ ] Production deploy.

## Production

**NOT DEPLOYED / NOT APPROVED.**
