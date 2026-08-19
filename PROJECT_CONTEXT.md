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
- Production root: `/home/sfkilvrs/3dprinthub`
- Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL DB: `sfkilvrs_EmiAdmin_3dprinthub`

## 2) قانون تحویل

مسیر اجباری:

`GitHub Epic → CI/Self-Test → Windows pull → Local backup/migration/test → Visual/Data QA → explicit user approval → Production backup → deploy/migrate/collectstatic/restart → smoke tests`

قواعد ثابت:
- Production قبل از تأیید Local دست نمی‌خورد.
- DB برای حل مشکل کد Reset نمی‌شود.
- `.env`, API keys, DB, media/private_media و Catalog Center data حفظ می‌شوند.
- Repair/Backfill ابتدا Dry Run + Backup.
- Windows Catalog Center ابزار اصلی کارمند است؛ Django Admin ابزار مدیریتی دوم و کامل است.
- Python/Django زبان پروژه؛ PowerShell برای عملیات Windows.
- Secret/API Key/Password/Token داخل Git/SQLite audit/export ذخیره نشود.
- تغییرات Source ابتدا مستقیم روی GitHub Epic ثبت می‌شوند؛ Windows فقط از GitHub Pull می‌کند و Patch دستی Source مبنا نیست.
- هر فاز باید Doc مستقل، تست و وضعیت Gate داشته باشد.

## 3) Branch و Epic جاری

Branch فعال:

`epic/phase49-unified-product-slider-sync`

زنجیره خطی:

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics → 49.3C Operator Workflow Recovery → 49.3C-1 Persian Content Integrity → 49.3D Workflow Hardening`

Foundationها Merge موازی نشده‌اند؛ Epic ancestry خطی است تا Conflict مصنوعی ایجاد نشود.

## 4) Validation تاریخی — Phase49.3B

Docs:
- `docs/PHASE49_3B_GUIDED_AI_HERO_DIAGNOSTICS.md`
- `docs/PHASE49_3B_PROVIDER_HARDENING_APPENDIX.md`
- `docs/PHASE49_3B_FINAL_GAPFIX_APPENDIX.md`
- `docs/PHASE49_3B_WINDOWS_LAUNCH_IMPORT_HOTFIX.md`

Clean runtime/test baseline تاریخی:
`c0ac5a9f98e157a5a50b6e1cf8021265a6246e28`

Final CI تاریخی:
- Run: `32248104376`
- Job: `96052943408`
- Compile: ✅
- Django check + migration contract: ✅
- Phase49 targeted Django/Bridge/Hero/Profile: ✅
- Windows Catalog Center AI/Wizard/Diagnostics: ✅
- Full Django suite: ✅

Windows local output قبل از 49.3C:
- `store.0031`: applied.
- `store.0032`: applied.
- `website.0022`: applied.
- Targeted Django: 45 tests ✅.
- Full Django: 406 tests ✅, 2 skipped.
- Epic49 discovery: 48 tests ✅.
- Windows temp SQLite `WinError 32` در test cleanup شناسایی و fix شد.
- `phase49_3b_ai_product_runtime` ImportError برای symbol ناموجود `sync_seo_reference_lists` شناسایی و fix شد.

Warnings شناخته‌شده Failure نیستند:
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: realtime in-memory؛ برای cross-process production در صورت نیاز Redis.

## 5) Foundation 49.2A — Catalog / Store consolidation

مسیر اصلی:

`Windows Catalog Center 8.7.1 → Catalog Bridge → ImportedPrintAsset → Product/ProductCatalogProfile → Store`

- Public external catalog/Link Analyzer intake بازنشسته شده.
- historical rows حذف نشده‌اند.
- external autosync پیش‌فرض خاموش.
- Material و USD/FX pricing حفظ شده.
- Catalog Center: `8.7.1`, build `2026.08.16.3`.

## 6) Foundation 49.2B — Master Admin + Customer Portal

- Design source فقط `master.zip` / Velzon Django Corporate 4.3.0.
- `interactive` ممنوع.
- Master RTL assets: `static/velzon_master/`.
- IRANSans FaNum: 200/300/400/500/700/900.
- navy/graphite + metallic gold.
- Desktop Admin login regression رفع شده.
- Customer Portal drawer حفظ شده.

Canonical brand:
`static/img/brand/3dprinthublogo.png`

Approved SHA256:
`97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`

هیچ لوگوی جایگزین/بازطراحی‌شده استفاده نشود.

## 7) Foundation 49.2C — Hero Studio

Doc: `docs/PHASE49_2C_HERO_STUDIO.md`

- visual Product Album Picker در Admin.
- Image Album بدون Save اولیه.
- `selected_asset_image` relation واقعی.
- Edit Slide بدون Delete/Recreate.
- per-slide Effect/Timing.
- mobile/reduced-motion fallback.

Effects:
`cinematic_fade`, `wedding_dissolve`, `cinematic_zoom`, `ken_burns`, `soft_blur`, `cinematic_reveal`

Migration:
`website.0020_phase49_2c_hero_studio`

## 8) Epic49 Unified Product / SEO / Slider / Sync

Doc: `docs/EPIC49_UNIFIED_PRODUCT_SLIDER_SYNC.md`

Model:

`Employee → Windows → Product + Images + Product SEO + Slider SEO + Hero → Bridge → Django Product/Profile/Hero → Store/Home`

Reverse sync:
`Django Admin edit → revision increment → Bridge → Windows refresh/compare`

Conflict Protection:
- Product Profile و Hero revision مستقل.
- stale Windows write → HTTP 409.
- Admin edit revision را بالا می‌برد.
- `batch_uuid + source_hash` برای idempotency.

Migrations:
- `store.0030_phase49_unified_sync_contract`
- `website.0021_phase49_unified_hero_sync`

Catalog Bridge:
- version `1.3.0`
- contract `epic49-unified-v1`
- legacy `health/import/diagnostics` حفظ شده.
- products + hero list/detail/sync اضافه شده.
- Bearer token فعلی حفظ شده.

## 9) Persian Sales Hero

Doc: `docs/EPIC49_PERSIAN_SALES_HERO_HOTFIX.md`

Public Hero raw English/Cookie/Consent/Tracking/HTML را نشان نمی‌دهد.

Priority:
1. Slider Persian SEO
2. AI Slider Persian SEO
3. Product SEO فارسی Windows
4. Persian Imported/Product editorial
5. Persian Product fallback
6. Persian generic sales fallback

Focus keyword فروش‌محور است؛ مثال:
`آباژور سه بعدی → خرید آباژور سه بعدی`

Hero UX:
- 2-line clamp + ellipsis.
- `نمایش بیشتر / بستن توضیحات`.
- autoplay هنگام متن کامل pause می‌شود.

## 10) Dual Publish Targets

Doc: `docs/EPIC49_DUAL_PUBLISH_TARGETS.md`

Windows Source/Developer:
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

## 11) Desktop Options / Workspace Routing / Rich Colors

Doc: `docs/EPIC49_DESKTOP_OPTIONS_WORKSPACE_REPAIR.md`

Root cause UI قدیمی:
`ux87_shell.py` alias قدیمی Workspace را نگه داشته بود.

Fix:
`ux87_shell.ProductWorkspace = ProductWorkspace`

Material Picker:
- Checkbox مستقل.
- Windows: `material_options_json`.

Rich Color Picker:
- Checkbox مستقل.
- Windows: `color_options_json`.
- types: `solid`, `transparent`, `translucent`, `metallic`, `silk`, `dual`, `multicolor`, `gradient`.
- main/secondary/tertiary HEX.
- legacy compatibility JSON حفظ شده.

Django migration:
`store.0031_phase49_rich_material_colors`

## 12) Phase49.3A — Product Publish Readiness

Doc: `docs/PHASE49_3A_PRODUCT_PUBLISH_READINESS.md`

49.3A Readiness Runtime-calculated است و Migration جدا ندارد.

Readiness بررسی می‌کند:
- اطلاعات پایه
- قیمت/سفارش/متریال/رنگ
- تصاویر
- محتوا و SEO
- منبع/مجوز
- publish requirements

SEO Editable Lists:
- Material/Color از انتخاب واقعی Operator sync می‌شود.
- Keyword bank برای Search/Content/SEO intent است، نه HTML meta-keywords stuffing.
- AI حق اختراع Material/Color ندارد.

49.3A CI historical:
- Run `32234579086`
- Job `96011595438`
- SUCCESS

## 13) Phase49.3B — Guided Publish Wizard

Canonical stages:
1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

UX:
- `✅` complete
- `❌ ★` incomplete required
- `🔒` future locked
- Previous/`مرحله بعد برای انتشار` پایین هر Stage.
- Final stage: Save + Local Publish + Production Publish.
- Next تا تکمیل Requiredهای همان Stage disabled است.

AI stage-specific:
- Stage 1: فقط ترجمه عنوان فارسی.
- Stage 4: full ecommerce content + sales SEO.
- Stage 6: Slider SEO + media.

## 14) Phase49.3B — Hero Media Studio + Product Profile persistence

Windows Stage 6 persistent controls:
- presentation: `product_fit`, `full_bleed`, `framed`, `cinematic`
- contain/cover
- focal position
- image scale
- X/Y position
- background: solid/blur/gradient/image
- background color / blur px
- desktop max width/height
- mobile max width/height

Default product-safe:
`product_fit + contain`

Windows Desktop/Mobile preview موجود است.

Django migrations:
- `website.0022_phase49_hero_media_presentation`
- `store.0032_phase49_slider_media_profile`

هر دو Migration فقط Additive هستند؛ DROP/DELETE/TRUNCATE/RESET ندارند.

Sync contract:
`Windows → ProductCatalogProfile → HomepageHeroSlide → Home`

Reverse:
`ProductProfile Admin ↔ Hero Admin ↔ Bridge ↔ Windows`

## 15) Phase49.3B — AI Provider Hub

Providerها:
- AvalAI
- OpenRouter
- OpenAI Direct

Secret registry ثابت:
- `OPENAI_API_KEY`
- `AVALAI_API_KEY`
- `OPENROUTER_API_KEY`
- optional `OPENROUTER_MANAGEMENT_KEY`
- optional `OPENAI_ADMIN_KEY`

Secretها فقط Environment/Windows Credential Store؛ داخل SQLite/Git/diagnostic export ذخیره نمی‌شوند.

Structured output:
- OpenAI: Responses API + strict JSON schema.
- AvalAI/OpenRouter: Chat Completions.
- اگر gateway/model `response_format` را رد کند، یک retry بدون `response_format` و client-side JSON validation انجام می‌شود.

OpenRouter model list dynamic است و Free Router/Free models را تشخیص می‌دهد.

## 16) Phase49.3B — AI cost / balance

`ai_request_log` نگه می‌دارد:
- provider/model
- operation/endpoint
- request ID
- HTTP status
- duration
- tokens
- USD cost
- Toman/IRT cost estimate/exact provider local cost
- product ID
- sanitized summaries/error

Semantics:
- AvalAI: provider credit + local currency/exchange-rate when available.
- OpenRouter: optional Management Key for credits; model pricing metadata.
- OpenAI: ordinary key به‌عنوان remaining balance نمایش داده نمی‌شود؛ optional Admin Key فقط cost/spend report است.

USD Provider costs با setting `ai_usd_to_toman` به تومان تبدیل و در SQLite پایدار می‌شوند؛ exact provider-local cost بر estimate اولویت دارد.

## 17) Program Log / Diagnostics / Audit identity

SQLite additive tables:
- `app_audit_log`
- `ai_request_log`

Dedicated identity columns:
- `operator`
- `workstation`
- `session_id`

Audit tracks:
- operator/workstation/session
- timestamp
- product ID
- area/action/status
- changed field names
- module/source file
- runtime errors

AI log tracks:
- operator/provider/model/operation
- request lifecycle
- HTTP/Request ID
- token usage
- USD/Toman cost
- sanitized error/response summary

Diagnostic bundle:
`<Catalog persistent data>/diagnostics/catalog-diagnostic-YYYYMMDD-HHMMSS.json`

Secret redaction covers Bearer/Authorization/API key/password/token/secret patterns.

## 18) Local historical data state

آخرین Audit قبل از Product واقعی مسیر جدید:
- Product = 0
- ImportedPrintAsset = 45
- linked Asset→Product = 0
- Hero slides = 2

Legacy Vesper/flexi-lizard Assetهای قدیمی بودند. 45 Asset نباید کورکورانه Product شوند.

تست صحیح End-to-End:
**یک Product واقعی Windows → Local Publish → Django Product/Profile/Hero → Home/Admin**.

## 19) Phase49.3C — Operator Workflow Recovery + AI Autofill + Image SEO

Doc:
`docs/PHASE49_3C_OPERATOR_WORKFLOW_RECOVERY.md`

Root causeها:
1. Readiness عمدتاً از DB saved state خوانده می‌شد، نه Widgetهای unsaved.
2. Image local resolver در نبود exact mapping از sorted file index حدس می‌زد.
3. AI Schema fieldها را داشت، اما empty string/array می‌توانست valid عبور کند.

Implementation:
- `phase49_3c_operator_recovery.py`: live debounce + Widget snapshot + exact missing list + fail-closed publish.
- `phase49_3c_ai_recovery.py`: completeness validation + structured repair + conservative fallback.
- `phase49_3c_image_pipeline.py`: max 10 source images، canonical URL dedupe، SHA/dHash duplicate filtering، exact identity، SEO WebP/metadata، stale signature detection.

Desktop additive data:
- `products.image_metadata_json` با `ALTER TABLE ADD COLUMN`.
- No Django migration for 49.3C.
- Source/cache images حذف یا reset نمی‌شوند.
- Final files در `<product local_dir>/seo_images/`.
- Metadata canonical record: `image_seo_manifest.json`.

Markers:
- `EPIC49_3C_LIVE_READINESS=ENABLED`
- `EPIC49_3C_STAGE_AI=ENABLED`
- `EPIC49_3C_IMAGE_ID_SAFE_DELETE=ENABLED`
- `EPIC49_3C_IMAGE_LIMIT_10=ENABLED`
- `EPIC49_3C_IMAGE_SEO_METADATA=ENABLED`
- `EPIC49_3C_AI_COMPLETENESS_RECOVERY=ENABLED`

## 19.1) Phase49.3C-1 — Persian AI Content Integrity & Workspace Persistence

Docs:
- `docs/PHASE49_3C_PERSIAN_CONTENT_HOTFIX.md`
- `docs/PHASE49_3C_PERSIAN_TRANSLATION_GUARD.md`

Repair:
- English source دیگر fallback فارسی نمی‌شود.
- `use_description_fa` در Structured Contract اجباری و به `use_description` موجود وصل شده.
- همه Editorial/SEO fields فارسی Gate دارند.
- Provider در خروجی غیر فارسی Structured Persian Repair می‌گیرد.
- fallback فارسی محافظه‌کارانه `needs_review` می‌شود.
- `description_fa` HTML fragment محدود/sanitize می‌شود.
- Workspace Reload/Save برای SEO/Tag/Hashtag/Keyword/Alt/Material Recommendation کامل شد.
- Translation workflow نیز Guard فارسی جدا دارد.

HTML مجاز:
`p`, `br`, `strong`, `em`, `ul`, `ol`, `li`, `h3`, `h4`

Markers:
- `EPIC49_3C_PERSIAN_CONTENT_GUARD=ENABLED`
- `EPIC49_3C_PERSIAN_TRANSLATE_GUARD=ENABLED`
- `EPIC49_3C_PERSIAN_SEO=ENABLED`
- `EPIC49_3C_HTML_SANITIZATION=ENABLED`
- `EPIC49_3C_WORKSPACE_CONTENT_PERSISTENCE=ENABLED`

## 20) Phase49.3D — Workflow Hardening

Doc:
`docs/PHASE49_3D_WORKFLOW_HARDENING.md`

Visual QA جدید مشکلات زیر را تأیید کرد:
1. Product Workspace در بدو بازشدن `TclError pack/grid` می‌داد.
2. Provider Hub برای صدها مدل Search/Filter حرفه‌ای نداشت.
3. Provider/Model فعال با Radio و ذخیره یکپارچه واضح نبود.
4. Local Publish در Readiness failure می‌توانست فقط به Images برگردد و دلیل را نشان ندهد.
5. قیمت محصول با زمان چاپ نامشخص باید Range حرفه‌ای داشته باشد.
6. Product Open به Auto Prepare کنترل‌شده AI نیاز داشت.

### 20.1 Workspace geometry fix

Root cause:
`quick_tab` از `grid()` استفاده می‌کند ولی Phase49.3B title-AI panel روی همان parent از `pack()` استفاده کرده بود.

Fix:
- Title-AI holder روی `quick_tab` فقط با `grid()` ساخته می‌شود.
- Widgetهای داخلی holder می‌توانند `pack()` داشته باشند چون parent متفاوت است.

### 20.2 Searchable AI Model Picker

Providerها:
- AvalAI
- OpenRouter
- OpenAI

قابلیت‌ها:
- فهرست کامل مدل‌های Provider بدون cap مصنوعی UI.
- Search زنده روی name و model id.
- Alias `CHATGPT/GPT`, `Claude`, `Gemini`, `Grok`, `DeepSeek`, `Qwen`, `Llama`, `Mistral`.
- فیلتر فقط مدل‌های رایگان.
- Scroll عمودی/افقی.
- شمارنده visible/total.
- انتخاب با Double Click یا Button.
- فقط raw model id persist می‌شود؛ label تزئینی `• رایگان/قیمت` ذخیره نمی‌شود.

### 20.3 Active Provider / Model

- Radio Button روی هر Provider.
- `ذخیره Provider و مدل فعال`.
- Persist:
  - `ai_provider`
  - `ai_model`
  - `ai_model_<provider>`
- live Test Connection دقیقاً با Provider/Model فعال.
- typed API Key در Secure Secret Store ذخیره می‌شود، نه SQLite/Git log.

### 20.4 Auto AI Prepare on Product Open

Desktop additive columns:
- `ai_auto_prepare_hash`
- `ai_auto_prepare_status`
- `ai_auto_prepare_at`

Behavior:
- default setting `ai_auto_prepare_on_open=1` قابل خاموش‌کردن است.
- فقط اگر فارسی/SEO ناقص باشد اجرا می‌شود.
- Source fingerprint از source facts + selected material/color/images ساخته می‌شود.
- همان fingerprint دوباره API مصرف نمی‌کند.
- Failure خودکار loop/retry نمی‌شود؛ Retry دستی باقی است.
- موفقیت مستقیم به Product اعمال و Workspace reload می‌شود.
- Similar Persian keywords از محصولات همان category فقط به‌عنوان editorial hint به AI داده می‌شود و حق Override facts ندارد.

### 20.5 Local/Production Publish Preflight

قبل از ارسال:
1. Save.
2. Recalculate readiness.
3. اگر فقط SEO/Metadata تصاویر stale باشد، auto finalize تصاویر.
4. Recalculate readiness.
5. اگر ناقص است:
   - Stage اول ناقص باز می‌شود.
   - Missing reasons در Dialog نمایش داده می‌شود.
   - `preflight_blocked` در Audit ثبت می‌شود.
   - هیچ Batch/FTP/Import اجرا نمی‌شود.

این Fix مسیر «کلیک Local Publish → برگشت بی‌صدا به Images» را هدف می‌گیرد.

### 20.6 Professional Price Range

زیرساخت موجود حفظ شد:
- Windows: `price_min`, `price_max`.
- Batch: تمام editorial fields منتقل می‌شوند.
- Django: `ProductCatalogProfile.price_min/price_max/price_mode`.
- Product Detail: Range موجود بود.
- Product List: اکنون Range کامل را نمایش می‌دهد.
- Structured Product schema تاریخی از قبل AggregateOffer low/high را پشتیبانی می‌کرد.

Desktop Save normalization:
- max < min → swap.
- فقط یک طرف → دو طرف برابر.
- Range خالی + final/suggested price → fixed range.

No Django migration required.

### 20.7 Image Download Limit

طبق درخواست کاربر رفتار موجود تغییر نکرد:
- per-product `download_image_limit` موجود است.
- انتخاب کمتر از 10 محترم است.
- hard cap 49.3C = 10.
- Regression test: limit=5 → 5؛ limit>10 → حداکثر 10.

### 20.8 Environment note — django-admin-expert

قبل از اجرای فاز Plugin directory برای `django-admin-expert` بررسی شد. Plugin/Skill مستقلی با همین نام در Session فعلی موجود نبود و نتایج Search نامرتبط بودند. بنابراین Plugin اشتباه نصب نشد و ادعای نصب نیز نمی‌شود. Django/Admin این فاز با Source واقعی Repo و تست‌های Django validate می‌شود.

### 20.9 Files / tests

Runtime:
- `catalog_center/app/phase49_3d_workflow_hardening.py`
- `catalog_center/app/openai_content.py`
- `catalog_center/launch.py`
- `templates/store/product_list.html`

Tests:
- `catalog_center/tests/test_epic49_phase49_3d_workflow_hardening.py`
- `store/test_phase49_3d_price_range.py`

CI:
- `.github/workflows/phase49-epic-ci.yml`

Markers:
- `EPIC49_3D_WORKSPACE_LAYOUT_FIX=ENABLED`
- `EPIC49_3D_AI_MODEL_PICKER=ENABLED`
- `EPIC49_3D_ACTIVE_PROVIDER_PERSISTENCE=ENABLED`
- `EPIC49_3D_AUTO_AI_PREPARE=ENABLED`
- `EPIC49_3D_LOCAL_PUBLISH_PREFLIGHT=ENABLED`
- `EPIC49_3D_PRICE_RANGE_CONTRACT=ENABLED`
- `EPIC49_3D_IMAGE_LIMIT_PRESERVED=ENABLED`

Current checklist:
- [x] Root cause pack/grid مشخص شد.
- [x] Workspace grid-safe repair committed.
- [x] Searchable AI Model Picker committed.
- [x] Radio Provider + persistent Provider/Model committed.
- [x] Active Provider live Test Connection committed.
- [x] Auto AI Prepare + fingerprint committed.
- [x] Similar Persian keyword hint contract committed.
- [x] Explicit Local/Production publish preflight committed.
- [x] Price range list/detail contract committed.
- [x] Image-limit behavior preserved/tested.
- [x] CI workflow updated.
- [x] Dedicated phase documentation committed.
- [ ] Final GitHub CI verified for final 49.3D HEAD.
- [ ] Windows pull / backup / compile / tests.
- [ ] `launch.py --verify-only`.
- [ ] Product Workspace opens without TclError.
- [ ] Live AI model search/provider/model persistence/test QA.
- [ ] Real Product Auto AI Prepare QA.
- [ ] Local Publish E2E.
- [ ] Explicit user approval.
- [ ] Production deploy.

## 21) Gate بعدی Windows Local — Phase49.3D

1. Catalog Center و Django runserver را ببند.
2. Pull آخرین `epic/phase49-unified-product-slider-sync`.
3. Verify exact HEAD اعلام‌شده بعد از Final CI/docs.
4. Backup:
   - `D:\projects\3DPrintHub\db.sqlite3`
   - `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
   - persistent Catalog data folders بدون حذف.
5. `python manage.py check`.
6. `python manage.py makemigrations --check --dry-run` → `No changes detected`.
7. `python manage.py migrate --plan` → Phase49.3D migration جدید ندارد.
8. Dedicated tests:
   - `python manage.py test store.test_phase49_3d_price_range -v 2`
   - `cd catalog_center`
   - `python -m unittest -v tests.test_epic49_phase49_3d_workflow_hardening`
   - 49.3C/Persian regressions.
   - Epic49 discovery.
9. `python launch.py --verify-only` و Markerهای 49.3D.
10. Product Workspace را باز کن:
   - هیچ TclError pack/grid نباشد.
   - Auto Prepare فقط در صورت نقص/Source change اجرا شود.
11. AI Center:
   - Radio Provider.
   - Model Search؛ `CHATGPT`/GPT/Claude/etc.
   - تعداد مدل واقعی Provider دیده شود.
   - raw model id انتخاب و persist شود.
   - Save → Restart → همان Provider/Model باقی بماند.
   - Test Connection موفق/خطادار با پیام واضح و Audit.
12. Price Range:
   - min/max وارد و Save/Reopen.
   - Batch editorial هر دو مقدار.
   - Local Store list/detail هر دو مقدار.
13. Image download limit:
   - انتخاب 5 → بیش از 5 دانلود نشود.
14. Local Publish:
   - stale image metadata → auto finalize.
   - blocker واقعی → Dialog صریح.
   - Ready کامل → فقط Local Publish.
15. Verify Local Django Product/Profile/Hero/Store/Home/Admin.
16. Visual/user approval.
17. فقط بعد از approval Production plan.

## 22) Production status

**NOT DEPLOYED / NOT APPROVED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3C، 49.3C-1 یا 49.3D در Production اجرا نشده است.
`website.0022` و `store.0032` نیز طبق وضعیت ثبت‌شده هنوز فقط Local هستند و Production برای این Epic قبل از approval دست‌نخورده می‌ماند.
