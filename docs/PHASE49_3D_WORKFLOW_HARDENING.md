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

زیرساخت `price_min/price_max` از قبل در Desktop SQLite، Batch و `ProductCatalogProfile` وجود داشت و صفحه جزئیات سایت نیز Range را نمایش می‌داد؛ نقص اصلی نرمال‌سازی Save، نمایش Range روی کارت‌های Store و حفظ `consultation_required=True` بعد از import بود. بنابراین Django migration جدید ایجاد نشد.

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
- `phase49_3d_ai_ui_cleanup.py` مسیر Legacy «فعال کن» را فقط از UI حذف می‌کند تا Active Provider یک Source of Truth داشته باشد؛ دکمه‌های ذخیره Key، تست اتصال، اعتبار و هزینه حذف نمی‌شوند.

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

### 5.1 Semantic Image SEO Signature

CI یک Regression واقعی پیدا کرد: `image_seo_signature()` در 49.3C رشته خام JSON را Hash می‌کرد. قبل از Finalize، `json.dumps` ممکن بود حروف فارسی را `\uXXXX` ذخیره کند و Finalize همان لیست را با `ensure_ascii=False` بنویسد. داده از نظر معنا یکسان بود اما Hash عوض می‌شد و Metadata تازه بلافاصله stale می‌شد.

Fix:
- `phase49_3d_image_signature.py`
- فیلدهای JSON قبل از Hash parse/normalize می‌شوند.
- تفاوت serialization دیگر stale ایجاد نمی‌کند.
- تغییر واقعی SEO/Alt هنوز Signature را عوض و Stage تصاویر را قرمز می‌کند.

### 6. Price Range

Desktop Save:
- حداقل/حداکثر اگر معکوس باشند مرتب می‌شوند.
- اگر فقط یکی وارد شده باشد، مقدار دوم برابر همان می‌شود.
- اگر Range خالی ولی `final_price/suggested_price` وجود داشته باشد، Range ثابت از آن ساخته می‌شود.

Windows → Django E2E:
- تست واقعی با `price_min=650000` و `price_max=850000` وارد Batch می‌شود.
- بعد از `phase37_import_catalog_center`:
  - `Product.fixed_price = 650000`
  - `Product.price_is_final = False`
  - `Product.consultation_required = True`
  - `ProductCatalogProfile.price_min = 650000`
  - `ProductCatalogProfile.price_max = 850000`
  - `ProductCatalogProfile.price_mode = range`
- Re-import همان Batch idempotent است و Range باقی می‌ماند.

Server regression پیدا و رفع شد:
- `apply_price_range()` برای Range درست `consultation_required=True` می‌کرد.
- `apply_phase43_product_details()` بعداً آن را بر اساس `product_type/availability_status` دوباره False می‌کرد.
- اکنون `True` قبلی حفظ می‌شود و Phase43 فقط در صورت custom/quote آن را اضافه می‌کند، نه اینکه Range requirement را downgrade کند.

Public Store:
- `product_detail.html` Range را نمایش می‌دهد.
- `product_list.html` اگر `price_max > price_min` باشد، متن `بازه قیمت` و هر دو مقدار را نمایش می‌دهد.
- تست Public در برابر separatorهای عددی Locale-safe است؛ اصل contract روی `حداقل تا حداکثر تومان` بسته می‌شود.

### 7. Image Download Limit

درخواست کاربر این بود که اگر گزینه موجود است تغییر داده نشود.

وضعیت فعلی حفظ شد:
- per-product `download_image_limit` موجود است.
- مقدار انتخابی کمتر از hard cap محترم است.
- hard cap فاز 49.3C برابر 10 تصویر است.
- Regression test ثابت می‌کند انتخاب 5 → فقط 5 URL و انتخاب بالاتر از 10 → حداکثر 10.

### 8. Test isolation hardening

CI دوم نشان داد `test_epic49_readiness_wizard` از `inspect.getsource(AIContentService.enrich_product)` استفاده می‌کرد. Persian Guardها عمداً این Method را Runtime-wrap می‌کنند؛ بنابراین Full Discovery با اجرای منفرد نتیجه متفاوت داشت.

Fix:
- Source contract از فایل canonical `app/openai_content.py` خوانده می‌شود.
- Test دیگر به ترتیب Monkey-Patchهای runtime وابسته نیست.

## Files

- `catalog_center/app/phase49_3d_workflow_hardening.py`
- `catalog_center/app/phase49_3d_image_signature.py`
- `catalog_center/app/phase49_3d_ai_ui_cleanup.py`
- `catalog_center/app/openai_content.py`
- `catalog_center/launch.py`
- `catalog_center/tests/test_epic49_phase49_3d_workflow_hardening.py`
- `catalog_center/tests/test_epic49_phase49_3d_ai_ui_cleanup.py`
- `catalog_center/tests/test_epic49_phase49_3c_image_signature.py`
- `catalog_center/tests/test_epic49_readiness_wizard.py`
- `store/test_phase49_3d_price_range.py`
- `store/test_phase49_unified_import_e2e.py`
- `store/management/commands/phase37_import_catalog_center.py`
- `templates/store/product_list.html`
- `.github/workflows/phase49-epic-ci.yml`
- `PROJECT_CONTEXT.md`

## Launcher markers

- `EPIC49_3D_WORKSPACE_LAYOUT_FIX=ENABLED`
- `EPIC49_3D_AI_MODEL_PICKER=ENABLED`
- `EPIC49_3D_ACTIVE_PROVIDER_PERSISTENCE=ENABLED`
- `EPIC49_3D_AI_LEGACY_ACTIVATE_REMOVED=ENABLED`
- `EPIC49_3D_AUTO_AI_PREPARE=ENABLED`
- `EPIC49_3D_LOCAL_PUBLISH_PREFLIGHT=ENABLED`
- `EPIC49_3D_PRICE_RANGE_CONTRACT=ENABLED`
- `EPIC49_3D_IMAGE_LIMIT_PRESERVED=ENABLED`
- `EPIC49_3D_SEMANTIC_IMAGE_SIGNATURE=ENABLED`

## Environment note — django-admin-expert

طبق سیاست پروژه، قبل از این فاز Plugin directory برای `django-admin-expert` بررسی شد. Plugin/Skill مستقلی با همین نام در Session فعلی موجود نبود و نتیجه‌های Search نامرتبط بودند؛ بنابراین هیچ Plugin اشتباهی نصب نشد و ادعای نصب نیز ثبت نمی‌شود. Django/Admin validation بر اساس Source واقعی همین Repository و تست‌های Django انجام می‌شود.

## CI history / Root-cause closure

در مسیر فاز، CI فقط برای «سبزکردن ظاهری» Retry نشد؛ هر Fail بررسی شد:

1. Public Price Range test ابتدا separator عددی ثابت انتظار داشت؛ Runtime Range درست بود. Test Locale-safe شد.
2. Image Metadata بلافاصله stale می‌شد؛ Root cause raw JSON serialization hash بود. Runtime semantic signature اضافه شد.
3. Readiness test در Full Discovery order-dependent بود؛ Test از runtime-wrapped method به canonical source contract منتقل شد.
4. Price Range E2E نشان داد `consultation_required=True` بعداً توسط Phase43 downgrade می‌شود؛ Runtime import fix شد.

Final validated runtime HEAD:
`e3eb0969b79fef67dc235cdbd213655140a128e1`

Final CI Probe:
- PR `#31` — closed, **not merged**.
- Probe Head `93180ae00fdf243074bcbbb3a3dcf00477887bef` = exact runtime tree + one temporary docs marker.
- Run `32271502234`
- Job `96128806609`
- Compile changed Python surfaces: ✅
- Django checks + migration contract: ✅
- Phase49 targeted Django / import E2E / public range tests: ✅
- Windows Catalog Center explicit tests + Epic49 discovery: ✅
- Full Django suite: ✅
- Overall: **SUCCESS**

## Gate

- [x] Root cause Workspace geometry manager مشخص شد.
- [x] Grid-safe Workspace repair پیاده‌سازی شد.
- [x] Searchable full model picker پیاده‌سازی شد.
- [x] Provider radio + persistent Provider/Model پیاده‌سازی شد.
- [x] Legacy `فعال کن` از مسیر UI canonical حذف شد.
- [x] Active Provider/Model live connection test پیاده‌سازی شد.
- [x] Auto AI prepare با source fingerprint پیاده‌سازی شد.
- [x] Similar Persian keyword hints اضافه شد.
- [x] Local Publish explicit preflight/error reporting پیاده‌سازی شد.
- [x] Auto image metadata finalization در publish preflight اضافه شد.
- [x] Semantic Image Signature regression رفع شد.
- [x] Desktop price range normalization پیاده‌سازی شد.
- [x] Windows→Batch→Django Product/Profile Range E2E تست شد.
- [x] Store list/detail price range contract تست شد.
- [x] Range consultation requirement حفظ می‌شود.
- [x] Image download limit behavior بدون تغییر عملکرد اصلی پوشش تست دارد.
- [x] Test order-dependence رفع شد.
- [x] Dedicated Windows + Django tests به CI اضافه شد.
- [x] Final GitHub CI برای Runtime HEAD verified.
- [ ] Windows pull/backup/compile/tests.
- [ ] Product Workspace visual open بدون TclError.
- [ ] Live Provider model list/search/test QA.
- [ ] Auto AI prepare real-product QA.
- [ ] Local Publish E2E.
- [ ] Explicit user approval.
- [ ] Production deploy.

## Production

**NOT DEPLOYED / NOT APPROVED.**
