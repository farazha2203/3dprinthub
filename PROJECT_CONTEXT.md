# PROJECT_CONTEXT — 3DPrintHub

> Source of Truth وضعیت جاری پروژه. جزئیات هر فاز در `docs/` نگه‌داری می‌شود. هنگام تعارض: **Migration state واقعی + جدیدترین CI/Local output + این فایل** ملاک است.

## 1) مسیرهای دائمی

- Windows project root: `D:\projects\3DPrintHub`
- Windows virtualenv: `D:\projects\3DPrintHub\.venv`
- Windows Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- Catalog Center persistent/legacy data:
  - `D:\projects\3dprinthub_catalog_center`
  - `D:\projects\3dprinthub-catalog-manager`
- Windows backups: `D:\projects\3dprinthub-backups`
- GitHub: `farazha2203/3dprinthub`
- Active branch: `epic/phase49-unified-product-slider-sync`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL DB: `sfkilvrs_EmiAdmin_3dprinthub`

## 2) قانون تحویل و حفاظت دیتا

مسیر اجباری:

`GitHub Epic → CI/Self-Test → Windows pull → Local backup/test → Visual/Data QA → explicit user approval → Production backup → deploy/migrate/collectstatic/restart → smoke tests`

قواعد ثابت:
- Production قبل از تأیید صریح Local دست نمی‌خورد.
- DB برای حل مشکل کد Reset نمی‌شود.
- `.env`, API keys, DB, media/private_media و Catalog Center persistent data حذف/Reset نمی‌شوند.
- Repair/Backfill حساس ابتدا Backup + Dry Run دارد.
- Windows Catalog Center ابزار عملیاتی اصلی کارمند است؛ Django Admin ابزار مدیریتی دوم و کامل است.
- Python/Django زبان اصلی پروژه؛ PowerShell برای عملیات Windows.
- Secret/API Key/Password/Token داخل Git، SQLite audit یا diagnostic export ذخیره نمی‌شود.
- Source ابتدا روی GitHub Epic ثبت می‌شود؛ Windows فقط Pull می‌کند و Patch دستی Source مبنا نیست.
- **هیچ Script/ZIP/Hotfix دانلودی خارج از GitHub برای Windows مبنا نیست.** Runnerها نیز باید داخل Repository Commit شوند.
- هر فاز باید Doc مستقل، Test، CI/Local Gate و checklist داشته باشد.

Git-only policy:
`docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`

## 3) زنجیره Epic جاری

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics → 49.3C Operator Workflow Recovery → 49.3C-1 Persian Content Integrity → 49.3D Workflow Hardening → 49.3D.1 Windows Runner Hotfix → 49.3E AI Task Completion & Recovery`

Foundationها موازی Merge نشده‌اند؛ ancestry خطی نگه‌داری می‌شود تا Conflict مصنوعی ایجاد نشود.

## 4) Baseline و Migration state

Catalog Center:
- Version: `8.7.1`
- Build family: `2026.08.16.3`

Django migrations مرتبط با Epic:
- `store.0030_phase49_unified_sync_contract`
- `website.0020_phase49_2c_hero_studio`
- `website.0021_phase49_unified_hero_sync`
- `store.0031_phase49_rich_material_colors`
- `website.0022_phase49_hero_media_presentation`
- `store.0032_phase49_slider_media_profile`

آخرین Windows state ثبت‌شده:
- `store.0031`: applied ✅
- `store.0032`: applied ✅
- `website.0022`: applied ✅

Phase49.3C / 49.3C-1 / 49.3D / 49.3D.1 / 49.3E Django migration جدید ندارند. Desktop SQLite تغییرات این بازه فقط additive/runtime-safe است.

Warnings شناخته‌شده و غیر-Failure:
- `3dprinthub.W001`: Google membership credentials اگر خالی باشد قابلیت Google disabled می‌ماند.
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: realtime in-memory؛ برای cross-process production در صورت نیاز Redis.
- Pillow `Image.getdata()` deprecation برای refactor آینده؛ Failure فعلی نیست.

## 5) Foundations — Catalog / Admin / Hero / Unified Sync

Canonical catalog flow:
`Windows Catalog Center 8.7.1 → Catalog Bridge → ImportedPrintAsset → Product/ProductCatalogProfile → Store`

49.2A:
- Public external catalog/Link Analyzer intake بازنشسته شده.
- historical rows حذف نشده‌اند.
- external autosync پیش‌فرض خاموش.
- Material و USD/FX pricing حفظ شده.

49.2B:
- Design source فقط `master.zip` / Velzon Django Corporate 4.3.0.
- `interactive` ممنوع.
- Master RTL assets: `static/velzon_master/`.
- IRANSans FaNum: 200/300/400/500/700/900.
- navy/graphite + metallic gold.
- Customer Portal drawer حفظ شده.
- Canonical brand: `static/img/brand/3dprinthublogo.png`
- Approved logo SHA256: `97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`

49.2C Hero Studio:
- visual Product Album Picker در Admin.
- Edit Slide بدون Delete/Recreate.
- per-slide Effect/Timing.
- mobile/reduced-motion fallback.
- Effects: `cinematic_fade`, `wedding_dissolve`, `cinematic_zoom`, `ken_burns`, `soft_blur`, `cinematic_reveal`.

Unified model:
`Employee → Windows → Product + Images + Product SEO + Slider SEO + Hero → Bridge → Django Product/Profile/Hero → Store/Home`

Reverse sync:
`Django Admin edit → revision increment → Bridge → Windows refresh/compare`

Conflict protection:
- Product Profile و Hero revision مستقل.
- stale Windows write → HTTP 409.
- Admin edit revision را بالا می‌برد.
- `batch_uuid + source_hash` برای idempotency.

Catalog Bridge:
- version `1.3.0`
- contract `epic49-unified-v1`
- legacy health/import/diagnostics حفظ شده.
- products + hero list/detail/sync اضافه شده.
- Bearer token فعلی حفظ شده.

## 6) Persian Sales Hero + Dual Publish

Docs:
- `docs/EPIC49_PERSIAN_SALES_HERO_HOTFIX.md`
- `docs/EPIC49_DUAL_PUBLISH_TARGETS.md`

Public Hero raw English/Cookie/Consent/Tracking/HTML را نمایش نمی‌دهد.

Persian priority:
1. Slider Persian SEO
2. AI Slider Persian SEO
3. Product SEO فارسی Windows
4. Persian Imported/Product editorial
5. Persian Product fallback
6. Persian generic sales fallback

Windows Publish targets:
- `🧪 انتشار آزمایشی روی کامپیوتر`
- `🌐 انتشار واقعی روی سایت اصلی`

Local:
`build_batch → SQLite guard → phase37_import_catalog_center → D:\projects\3DPrintHub\db.sqlite3`

Local Guard:
- vendor دقیقاً SQLite.
- DB دقیقاً project local DB.
- MySQL/SQLite دیگر/portable runtime block.
- FTP/Bridge ندارد.
- Local IDs با Production IDs/Revisions قاطی نمی‌شوند.

Production:
`build_batch → FTP → Bridge → Import → public verification → ACK`

Production دو confirmation و مقصد واضح دارد.

## 7) Desktop Materials / Colors / Workspace Routing

Doc: `docs/EPIC49_DESKTOP_OPTIONS_WORKSPACE_REPAIR.md`

Workspace routing:
`ux87_shell.ProductWorkspace = ProductWorkspace`

Material:
- Checkbox مستقل.
- Windows: `material_options_json`.

Color:
- Windows: `color_options_json`.
- types: `solid`, `transparent`, `translucent`, `metallic`, `silk`, `dual`, `multicolor`, `gradient`.
- main/secondary/tertiary HEX.
- legacy compatibility JSON حفظ شده.

## 8) Phase49.3A / 49.3B — Readiness + Guided Wizard + Hero Media + AI Hub

Docs:
- `docs/PHASE49_3A_PRODUCT_PUBLISH_READINESS.md`
- `docs/PHASE49_3B_GUIDED_AI_HERO_DIAGNOSTICS.md`
- `docs/PHASE49_3B_PROVIDER_HARDENING_APPENDIX.md`
- `docs/PHASE49_3B_FINAL_GAPFIX_APPENDIX.md`
- `docs/PHASE49_3B_WINDOWS_LAUNCH_IMPORT_HOTFIX.md`

Canonical 7 stages:
1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

49.3B UX تاریخی:
- `✅` complete
- `❌ ★` incomplete required
- Previous/Next
- Next تا تکمیل Requiredهای Stage disabled
- Final stage: Save + Local + Production Publish

> از Phase49.3E به بعد Stage navigation دیگر قفل نمی‌شود؛ بخش 13 این فایل ملاک رفتار جاری است.

AI stage-specific:
- Stage 1: فقط عنوان فارسی.
- Stage 4: ecommerce content + Persian sales SEO.
- Stage 6: Slider SEO + media.

Hero Media:
- presentation: `product_fit`, `full_bleed`, `framed`, `cinematic`
- contain/cover
- focal position
- scale / X / Y
- background: solid/blur/gradient/image
- desktop/mobile max dimensions
- default: `product_fit + contain`

AI Providers:
- AvalAI
- OpenRouter
- OpenAI Direct

Secret registry:
- `OPENAI_API_KEY`
- `AVALAI_API_KEY`
- `OPENROUTER_API_KEY`
- optional `OPENROUTER_MANAGEMENT_KEY`
- optional `OPENAI_ADMIN_KEY`

Structured output:
- OpenAI: Responses API + strict schema.
- AvalAI/OpenRouter: Chat Completions.
- unsupported `response_format` → one retry without it + client-side JSON validation.

Diagnostics:
- `app_audit_log`
- `ai_request_log`
- operator/workstation/session identity
- provider/model/operation/request ID/HTTP/duration/tokens/USD/Toman cost
- sanitized error/response
- diagnostic bundle: `<Catalog persistent data>/diagnostics/catalog-diagnostic-YYYYMMDD-HHMMSS.json`

Historical Phase49.3B final CI:
- Run `32248104376`
- Job `96052943408`
- SUCCESS

## 9) Phase49.3C — Operator Workflow Recovery + Image SEO

Doc: `docs/PHASE49_3C_OPERATOR_WORKFLOW_RECOVERY.md`

Runtime:
- live readiness with 180ms debounce.
- Widget snapshot برای unsaved fields.
- exact missing-field list.
- stage AI + global AI.
- fail-closed queue/local/production.
- AI completeness validation/repair/fallback.
- exact image URL/file identity; no index guessing.
- source image max hard cap = 10.
- canonical URL dedupe.
- SHA + conservative visual duplicate filtering.
- SEO WebP output.
- creator/copyright/license/source/operator/publisher metadata.
- stale metadata signature.

Desktop additive field:
- `products.image_metadata_json`

Files:
- final SEO images: `<product local_dir>/seo_images/`
- manifest: `image_seo_manifest.json`

## 10) Phase49.3C-1 — Persian Content Integrity

Docs:
- `docs/PHASE49_3C_PERSIAN_CONTENT_HOTFIX.md`
- `docs/PHASE49_3C_PERSIAN_TRANSLATION_GUARD.md`

Rules:
- English source دیگر fallback فارسی نمی‌شود.
- `use_description_fa` در Structured AI contract اجباری و به `use_description` وصل است.
- Editorial/SEO fields باید فارسی باشند.
- خروجی غیر فارسی → Structured Persian Repair.
- Repair failure → English به فیلد فارسی کپی نمی‌شود؛ fallback فارسی محافظه‌کارانه + `needs_review`.
- `description_fa` HTML محدود و sanitize می‌شود.
- Workspace Reload/Save برای SEO/Tag/Hashtag/Keyword/Alt/Material Recommendation کامل است.
- Translation workflow Guard مستقل دارد.

HTML مجاز:
`p`, `br`, `strong`, `em`, `ul`, `ol`, `li`, `h3`, `h4`

## 11) Phase49.3D — Workflow Hardening

Canonical doc:
`docs/PHASE49_3D_WORKFLOW_HARDENING.md`

### Workspace TclError

Visual error:
`TclError: cannot use geometry manager pack inside ... which already has slaves managed by grid`

Root cause:
`quick_tab` grid-managed بود ولی Phase49.3B title-AI holder روی همان parent از `pack()` استفاده می‌کرد.

Fix:
- holder روی `quick_tab` فقط با `grid()`.
- داخل holder استفاده از `pack()` مجاز است چون parent متفاوت است.

### Searchable AI Model Picker

برای AvalAI / OpenRouter / OpenAI:
- دریافت full `list_model_info()` بدون UI cap مصنوعی.
- Search زنده name/model_id.
- alias search: `CHATGPT/GPT`, Claude, Gemini, Grok, DeepSeek, Qwen, Llama, Mistral.
- Free-only filter.
- vertical/horizontal scroll.
- visible/total model count.
- double-click/select button.
- فقط raw model id persist می‌شود؛ label قیمت/رایگان ذخیره نمی‌شود.

### Active Provider / Model

- Radio Button مستقل روی هر Provider.
- canonical action: `ذخیره Provider و مدل فعال`.
- persist: `ai_provider`, `ai_model`, `ai_model_<provider>`.
- live Test Connection روی دقیقاً Provider/Model فعال.
- typed API Key فقط Secure Secret Store.
- Legacy per-card `فعال کن` از UI حذف شده.

### Auto AI Prepare

Desktop additive columns:
- `ai_auto_prepare_hash`
- `ai_auto_prepare_status`
- `ai_auto_prepare_at`

Behavior:
- فقط اگر Persian editorial/SEO ناقص باشد اجرا می‌شود.
- fingerprint از Source facts + selected materials/colors/images.
- همان fingerprint دوباره API مصرف نمی‌کند.
- auto failure loop نمی‌شود؛ Retry دستی باقی است.
- AI حق جعل price/license/dimensions/stock/selected color/material ندارد.

### Publish Preflight

قبل از Publish:
1. Save.
2. Recalculate Readiness.
3. اگر فقط Image SEO/Metadata stale است و core image موجود است → auto finalize.
4. Recalculate.
5. اگر ناقص است: Stage/Reason واضح + Audit؛ هیچ Batch/FTP/Import اجرا نمی‌شود.

### Semantic Image SEO Signature

- JSON semantic normalize قبل از hash.
- serialization-only change stale نمی‌کند.
- تغییر واقعی SEO/Alt → Stage تصاویر دوباره نیازمند refresh می‌شود.

### Professional Price Range

Desktop:
- `price_min`, `price_max`
- max < min → swap
- فقط یک طرف → دو طرف برابر
- Range خالی + final/suggested → fixed range

Windows→Batch→Django validated:
- Product.fixed_price = minimum
- Product.price_is_final = False برای Range
- Product.consultation_required = True برای Range
- ProductCatalogProfile.price_min/max
- ProductCatalogProfile.price_mode = `range`
- re-import idempotent

Public Store List/Detail هر دو Range را نمایش می‌دهند.

Image download limit:
- per-product `download_image_limit`
- انتخاب کمتر از 10 محترم است.
- hard cap = 10.

Phase49.3D final CI:
- Run `32271502234`
- Job `96128806609`
- SUCCESS

## 12) Phase49.3D.1 — Windows Runner StrictMode Hotfix

Doc:
`docs/PHASE49_3D_WINDOWS_RUNNER_ARRAY_HOTFIX.md`

Windows failure واقعی:
`PropertyNotFoundStrict` روی `$projectProcesses.Count`.

Root cause:
PowerShell Pipeline در StrictMode برای صفر/یک/چند نتیجه نوع یکسان تضمین نمی‌کرد.

Fix:
- Runner version `49.3D.1`.
- process pipeline داخل `@(...)`.
- check: `@($projectProcesses).Count`.
- CI اکنون خود PowerShell Runner را Parse/contract-test می‌کند.

Final CI:
- Run `32276195521`
- Job `96144096195`
- PowerShell contract ✅
- Compile/Django/Windows/Full Django ✅

Canonical runner:
`RUN_PHASE49_3D_LOCAL_GATE.ps1`

## 13) Phase49.3E — AI Task Completion & Recovery

Canonical doc:
`docs/PHASE49_3E_AI_TASK_COMPLETION_RECOVERY.md`

Trigger:
Visual QA واقعی نشان داد Stage تصاویر می‌تواند خطاهای `SEO filename / Alt / Creator / Metadata` را نمایش دهد ولی اپراتور مسیر مستقیمی برای رفع آن ندارد و Stageهای دیگر نیز بعد از اولین نقص قفل می‌شوند.

### اصل جدید Readiness

**Readiness راهنما است، نه زندان.**

- همه 7 Stage همیشه قابل بازکردن و اصلاح هستند؛ چه سبز چه قرمز.
- قرمز یعنی ناقص، نه disabled.
- Next فقط Requiredهای Stage جاری را Gate می‌کند.
- Local Publish همیشه برای Preflight قابل کلیک است تا blocker را توضیح دهد.
- Production همچنان Fail-closed و نیازمند Readiness کامل + تأیید صریح کاربر است.

### AI/SEO Task Center

Rail سمت راست Taskهای مستقل دارد:
1. متن فارسی محصول
2. سئو محصول
3. سئو و متادیتای تصاویر
4. پیشنهاد متریال AI
5. سئو اسلایدر

State:
- `✅ done` = داده واقعی معتبر موجود است.
- `❌ missing` = ناقص و قابل تکمیل توسط AI/اپراتور.
- `➖ skipped` = قابلیت مربوطه فعال نیست؛ مثال Slider خاموش.

سبزشدن بر اساس DB/File state محاسبه می‌شود، نه صرفاً HTTP success از AI.

### Image AI SEO

Actions:
- Stage تصاویر: `✨ تکمیل AI سئو تصاویر`
- Stage 4: `🖼 سئو تصاویر با AI`
- `🖼 نهایی‌سازی فایل‌های SEO`

AI از facts واقعی Product/Source استفاده می‌کند و سپس `finalize_selected_images()` اجرا می‌شود.

Image metadata contract:
- image_id
- source/source page
- original filename
- SEO filename
- Persian Alt
- Title/Caption/Keywords
- Creator
- Copyright holder
- Publisher/Editor/Operator
- License
- Credit line
- source/final SHA256
- SEO signature

### Manual Image Metadata Editor

Action:
`✏ ویرایش دستی متادیتای تصاویر`

Editable:
- SEO filename
- Alt فارسی
- Image Title
- Caption
- Keywords
- Creator/Designer
- Source page
- License name/url

Safety:
- copyright holder مستقیماً جعل/override نمی‌شود.
- operator override فقط برای fieldهای مجاز حفظ می‌شود.
- Save → rebuild SEO WebP از Source/Cache اصلی.
- Source image حذف نمی‌شود.

### Structured AI Contract

File:
`catalog_center/app/phase49_3e_ai_contract.py`

- `specs_fa_json` list-of-object باقی می‌ماند.
- `material_recommendations_json` list-of-object واقعی است.
- stringified dict معتبر حساب نمی‌شود.
- Material Task فقط با `material/score/recommended/reason_fa` معتبر سبز می‌شود.

### Slider Task

- Slider off → `➖ skipped`.
- Slider on → Title/Description/Alt/Focus Keyword/Image required.
- AI می‌تواند Copy/SEO قابل‌استنتاج را بسازد.

### Audit

Events:
- `task_center_start`
- `task_center_error`
- `task_center_complete`
- `ai_seo_finalize_error`
- `operator_metadata_override`

Secret/API key ثبت نمی‌شود.

### 49.3E GitHub CI

CI Probe:
- PR `#33`
- Base Epic runtime/doc HEAD: `749606576561a500985632827b54c3b1b8a589a5`
- Probe فقط docs marker داشت.
- PR بسته شد و Merge نشد.

Final CI:
- Run `32280313257`
- Job `96157285817`
- PowerShell runner 49.3D + 49.3E contract: ✅
- Compile: ✅
- Django check + migration contract: ✅
- Phase49 targeted: ✅ — 62 tests
- Windows explicit tests: ✅
- Phase49.3E dedicated: ✅ — 8/8
- `launch.py --verify-only` + 49.3E markers: ✅
- Epic49 discovery: ✅ — 84 tests
- Full Django: ✅ — 408 tests, 2 skipped
- Overall: **SUCCESS**

Canonical Windows runner:
`RUN_PHASE49_3E_LOCAL_GATE.ps1`

Runner version:
`49.3E.0`

## 14) Environment note — django-admin-expert

طبق سیاست پروژه، Plugin directory برای `django-admin-expert` بررسی شد. Plugin/Skill مستقلی با همین نام در Session فعلی موجود نبود و نتایج Search نامرتبط بودند. Plugin اشتباه نصب نشد و ادعای نصب نیز نمی‌شود. Django/Admin validation بر اساس Source واقعی Repository و Django tests انجام می‌شود.

## 15) Gate بعدی — Windows Local Phase49.3E

1. Catalog Center و Django runserver بسته باشند.
2. `git status --short` باید خالی باشد؛ در غیر این صورت Stop و بررسی.
3. Fetch/Switch/Pull Epic با `--ff-only`.
4. اجرای Runner از **داخل Repository**:
   `D:\projects\3DPrintHub\RUN_PHASE49_3E_LOCAL_GATE.ps1`
5. Runner ابتدا Gate کامل 49.3D را اجرا می‌کند؛ Backup/Compile/Django/Windows/Full suite.
6. سپس 49.3E compile/test/markers را اجرا می‌کند.
7. Visual QA همان محصول واقعی:
   - همه 7 Stage clickable باشند.
   - Task Center ظاهر شود.
   - Stage تصاویر سه Action AI/manual/finalize داشته باشد.
   - `✨ تکمیل AI سئو تصاویر` با Provider واقعی اجرا شود.
   - SEO filename/Alt/Creator/Source/Metadata از حالت خطا خارج شوند اگر facts کافی باشد.
   - اگر چیزی باقی ماند، Manual Editor دقیقاً همان مورد را قابل اصلاح کند.
   - Save دستی باید WebP Metadata را واقعاً rebuild کند.
   - Slider off → Task skipped؛ Slider on → Task required.
   - AI manual data را overwrite نکند.
8. Local Publish فقط بعد از تکمیل واقعی تست شود؛ blocker باید Dialog واضح بدهد.
9. Verify Local Django Product/Profile/Hero/Store/Home/Admin.
10. Explicit user approval.
11. فقط بعد از approval: Production plan/deploy.

## 16) Current checklist

- [x] Phase49.3D runtime/CI complete.
- [x] Phase49.3D.1 Windows runner bug fixed + CI-covered.
- [x] Phase49.3E root cause identified from Windows visual QA.
- [x] AI/SEO Task Center implemented.
- [x] Image AI SEO implemented.
- [x] Manual Image Metadata Editor implemented.
- [x] Non-blocking stage navigation implemented.
- [x] Local preflight made accessible.
- [x] Structured AI data guard implemented.
- [x] Phase49.3E Git-only runner committed.
- [x] Phase49.3E GitHub CI SUCCESS — Run `32280313257`, Job `96157285817`.
- [ ] Windows Pull + automated 49.3E gate.
- [ ] Real-provider Image AI QA.
- [ ] Manual image metadata QA.
- [ ] Local Publish E2E.
- [ ] Local Django end-to-end verification.
- [ ] Explicit user approval.
- [ ] Production deploy.

## 17) Production status

**NOT DEPLOYED / NOT APPROVED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3C، 49.3C-1، 49.3D، 49.3D.1 یا 49.3E در Production اجرا نشده است. Production تا پایان Windows Local QA و تأیید صریح کاربر دست‌نخورده می‌ماند.
