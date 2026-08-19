# Phase49.3E — AI Task Completion & Recovery Workflow

## شروع فاز

این فاز از Visual QA واقعی Windows شروع شد. اپراتور در Stage تصاویر محصول «خرس همبستگی آگاهی از سرطان پستان» با چند نقص تصویر روبه‌رو شد، اما UI فقط نقص را نمایش می‌داد و مسیر مستقیمی برای رفع آن نداشت. هم‌زمان Stageهای بعد از اولین نقص Disable می‌شدند و کاربر عملاً در Workflow گیر می‌کرد.

هدف 49.3E این است که Readiness از یک «دیوار» به یک «راهنمای تکمیل» تبدیل شود.

Production تا پایان Windows Local QA و تأیید صریح کاربر ممنوع است.

## Root Causeهای تأییدشده

### 1. Image Readiness بدون Recovery Action

`phase49_3c_image_pipeline.image_metadata_missing()` برای هر تصویر منتخب این موارد را کنترل می‌کند:

- نام SEO تصویر
- Alt تصویر
- Creator
- صفحه منبع
- Metadata ready/stale

اما Stage تصاویر فقط دو رفتار داشت:

- اگر Alt وجود داشت → Finalize تصاویر
- اگر Alt وجود نداشت → اجرای AI Commerce عمومی

بعد از AI Commerce، Task مستقلی برای تکمیل/بررسی Image SEO وجود نداشت. بنابراین اپراتور می‌توانست نقص را ببیند ولی مسیر روشن برای اصلاح آن نداشته باشد.

### 2. Navigation به‌عنوان Lock استفاده شده بود

در Live Readiness، Stageهای بعد از اولین نقص `disabled` می‌شدند. این رفتار برای Guided Wizard مناسب نبود چون اپراتور باید همیشه بتواند به هر مرحله برگردد، داده را بررسی کند و اصلاح انجام دهد.

در 49.3E:

- همه 7 Stage همیشه قابل بازکردن هستند.
- قرمز بودن فقط یعنی Stage ناقص است.
- `مرحله بعد` همچنان با Requiredهای Stage جاری Gate می‌شود.
- Production همچنان Fail-closed است.

### 3. AI وظایف محوله را به‌عنوان Task قابل مشاهده نداشت

AI از قبل می‌توانست این خروجی‌ها را تولید کند:

- متن فارسی
- SEO محصول
- Tags / Hashtags / Search keywords
- Image Alt
- Material recommendations
- Slider SEO

اما UI وضعیت این وظایف را مستقل نشان نمی‌داد. بنابراین ممکن بود اپراتور نداند کدام خروجی واقعاً کامل شده و کدام خروجی خالی/نامعتبر باقی مانده است.

### 4. Manual Escape Hatch برای Image Metadata وجود نداشت

Image pipeline می‌تواند Metadata واقعی فایل را بسازد، اما اگر Creator/Source/Alt یا نام SEO نیاز به اصلاح دستی داشت، Editor اختصاصی وجود نداشت.

## مدل Task جدید

Rail سمت راست یک بخش جدید دارد:

`وظایف هوش مصنوعی و SEO`

Taskهای Canonical:

1. `متن فارسی محصول`
2. `سئو محصول`
3. `سئو و متادیتای تصاویر`
4. `پیشنهاد متریال AI`
5. `سئو اسلایدر`

Stateها:

- `✅ done` — داده واقعی و معتبر موجود است.
- `❌ missing` — AI/اپراتور هنوز باید آن را کامل کند.
- `➖ skipped` — قابلیت مربوطه فعال نیست و Task الزامی نیست؛ مثال: Slider خاموش است.

سبزشدن Task فقط از روی state واقعی Product/File محاسبه می‌شود و صرفاً به معنی «درخواست AI موفق بود» نیست.

## AI Task Orchestrator

فایل:

`catalog_center/app/phase49_3e_ai_task_center.py`

### رفتار

- `✨ انجام وظایف ناقص AI` پکیج کامل AI را تولید می‌کند.
- فقط فیلدهای خالی/ناقص قابل‌استنتاج نوشته می‌شوند.
- داده دستی موجود Silent overwrite نمی‌شود.
- قیمت، مجوز، ابعاد، موجودی، رنگ انتخابی و متریال واقعی همچنان توسط AI جعل نمی‌شوند.
- بعد از Apply، Taskها دوباره از DB/File محاسبه می‌شوند.
- اگر Task باقی بماند، UI دقیقاً نام آن و موارد ناقصش را نشان می‌دهد.

## Image AI SEO

در Stage تصاویر و Stage 4 یک Action مستقل وجود دارد:

`✨ تکمیل AI سئو تصاویر`

این Action بر اساس:

- عنوان فارسی محصول
- توضیح کوتاه/کامل
- SEO Title/Description
- Keywords/Tags/Hashtags
- Source URL
- Author/Designer
- License
- تصاویر منتخب واقعی

موارد قابل‌استنتاج را تکمیل می‌کند و سپس `finalize_selected_images()` را اجرا می‌کند.

خروجی Final Image Metadata شامل:

- `image_id`
- `source_url`
- `source_page_url`
- `original_filename`
- `seo_filename`
- `alt_text`
- `title`
- `caption`
- `keywords`
- `creator`
- `copyright_holder`
- `publisher`
- `editor`
- `operator`
- `license_name`
- `license_url`
- `credit_line`
- source/final SHA256
- SEO signature

## Manual Image Metadata Editor

Action:

`✏ ویرایش دستی متادیتای تصاویر`

برای هر تصویر منتخب اپراتور می‌تواند این موارد را اصلاح کند:

- SEO filename
- Alt فارسی
- Image Title
- Caption
- Image Keywords
- Creator / Designer
- Source page
- License name
- License URL

### Safety

- `copyright_holder` مستقیماً قابل جعل/override نیست.
- Operator override فقط برای فیلدهای صریح ثبت‌شده حفظ می‌شود.
- بعد از Save، فایل SEO دوباره از Source/Cache اصلی ساخته می‌شود.
- UI فقط سبز نمی‌شود؛ Metadata واقعی فایل WebP دوباره نوشته می‌شود.
- Source/Cache اصلی حذف نمی‌شود.

## Structured AI Contract

فایل:

`catalog_center/app/phase49_3e_ai_contract.py`

هدف:

- `specs_fa_json` باید list of object `{key,value}` بماند.
- `material_recommendations_json` باید list of object باشد و stringified dict معتبر حساب نشود.
- Material Task فقط وقتی سبز می‌شود که ساختار واقعی `material / score / recommended / reason_fa` معتبر باشد.

این Guard از «سبز شدن ظاهری با داده خراب» جلوگیری می‌کند.

## Slider SEO Task

- Slider خاموش → `➖ سئو اسلایدر` و هیچ blocker ندارد.
- Slider روشن → Title/Description/Alt/Focus Keyword/Image الزامی می‌شوند.
- AI می‌تواند Copy/SEO قابل‌استنتاج را بسازد.
- تصویر Slider از Primary/Selected image واقعی قابل پرشدن است.

## Navigation / No Dead End

از 49.3E:

- همه Stage buttonها همیشه clickable هستند.
- Stage قرمز برای اصلاح باز می‌شود.
- Stage سبز نیز برای بازبینی/ویرایش باز می‌ماند.
- Next فقط با Requiredهای Stage جاری Gate می‌شود.
- Local Publish button برای Preflight قابل دسترس می‌ماند تا blocker را توضیح دهد.
- Production همچنان تا Readiness کامل و تأیید صریح کاربر مسدود است.

## Audit / Diagnostics

Task Center این Eventها را ثبت می‌کند:

- `task_center_start`
- `task_center_error`
- `task_center_complete`
- `ai_seo_finalize_error`
- `operator_metadata_override`

Secret/API Key در Log/SQLite audit ثبت نمی‌شود.

## Data / Migration

Phase49.3E:

- Django migration جدید ندارد.
- Desktop DB destructive migration ندارد.
- schema موجود `image_metadata_json` را استفاده می‌کند.
- DB reset/delete ندارد.
- media/source cache را حذف نمی‌کند.

## Files

- `catalog_center/app/phase49_3e_ai_task_center.py`
- `catalog_center/app/phase49_3e_ai_contract.py`
- `catalog_center/tests/test_epic49_phase49_3e_ai_task_center.py`
- `catalog_center/launch.py`
- `RUN_PHASE49_3E_LOCAL_GATE.ps1`
- `.github/workflows/phase49-epic-ci.yml`
- `PROJECT_CONTEXT.md`

## Launcher Markers

- `EPIC49_3E_AI_TASK_CENTER=ENABLED`
- `EPIC49_3E_IMAGE_AI_SEO=ENABLED`
- `EPIC49_3E_OPERATOR_IMAGE_EDITOR=ENABLED`
- `EPIC49_3E_NON_BLOCKING_STAGE_NAV=ENABLED`
- `EPIC49_3E_LOCAL_PREFLIGHT_ALWAYS_ACCESSIBLE=ENABLED`

## Tests

Dedicated test verifies:

- Image Task قرمز می‌ماند تا Alt + Metadata کامل باشد.
- Slider خاموش → skipped.
- Slider روشن → required.
- AI مقدار دستی موجود را overwrite نمی‌کند.
- Specs/Material recommendations ساختار Object واقعی حفظ می‌کنند.
- stringified fake material object Task را سبز نمی‌کند.
- Operator override فقط فیلدهای مجاز را نگه می‌دارد.
- SEO filename نمی‌تواند Path دلخواه ایجاد کند.

## Gate

- [x] Root Cause از Visual QA واقعی مشخص شد.
- [x] AI/SEO Task Center پیاده‌سازی شد.
- [x] Image AI SEO action پیاده‌سازی شد.
- [x] Manual Image Metadata Editor پیاده‌سازی شد.
- [x] Operator override persistence اضافه شد.
- [x] Structured AI contract اضافه شد.
- [x] Navigation از حالت dead-end خارج شد.
- [x] Local Publish برای Preflight قابل دسترس شد.
- [x] Dedicated tests نوشته شد.
- [x] Git-only Windows runner ساخته شد.
- [ ] Final GitHub CI verified.
- [ ] Windows pull + local automated gate.
- [ ] Visual QA همان محصول واقعی.
- [ ] Image AI SEO real-provider QA.
- [ ] Manual metadata save/rebuild QA.
- [ ] Local Publish E2E.
- [ ] Local Django Product/Profile/Store/Hero/Admin verification.
- [ ] explicit user approval.
- [ ] Production deploy.

## Production

**NOT DEPLOYED / NOT APPROVED.**
