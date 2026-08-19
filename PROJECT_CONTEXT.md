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
- هر فاز باید Doc مستقل، Test، CI/Local Gate و checklist داشته باشد.

## 3) زنجیره Epic جاری

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics → 49.3C Operator Workflow Recovery → 49.3C-1 Persian Content Integrity → 49.3D Workflow Hardening`

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

آخرین Windows state ثبت‌شده قبل از 49.3D:
- `store.0031`: applied ✅
- `store.0032`: applied ✅
- `website.0022`: applied ✅

Phase49.3C / 49.3C-1 / 49.3D Django migration جدید ندارند. Desktop SQLite فقط additive schema دارد.

Warnings شناخته‌شده و غیر-Failure:
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: realtime in-memory؛ برای cross-process production در صورت نیاز Redis.

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

UX:
- `✅` complete
- `❌ ★` incomplete required
- `🔒` future locked
- Previous/Next
- Next تا تکمیل Requiredهای Stage disabled
- Final stage: Save + Local + Production Publish

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

Markers:
- `EPIC49_3C_PERSIAN_CONTENT_GUARD=ENABLED`
- `EPIC49_3C_PERSIAN_TRANSLATE_GUARD=ENABLED`
- `EPIC49_3C_PERSIAN_SEO=ENABLED`
- `EPIC49_3C_HTML_SANITIZATION=ENABLED`
- `EPIC49_3C_WORKSPACE_CONTENT_PERSISTENCE=ENABLED`

## 11) Phase49.3D — Workflow Hardening

Canonical doc:
`docs/PHASE49_3D_WORKFLOW_HARDENING.md`

### 11.1 Product Workspace TclError

Visual error:
`TclError: cannot use geometry manager pack inside ... which already has slaves managed by grid`

Root cause:
`quick_tab` grid-managed بود ولی Phase49.3B title-AI holder روی همان parent از `pack()` استفاده می‌کرد.

Fix:
- holder روی `quick_tab` فقط با `grid()`.
- داخل holder استفاده از `pack()` مجاز است چون parent متفاوت است.

### 11.2 Searchable AI Model Picker

برای AvalAI / OpenRouter / OpenAI:
- دریافت full `list_model_info()` بدون UI cap مصنوعی.
- Search زنده name/model_id.
- alias search: `CHATGPT/GPT`, Claude, Gemini, Grok, DeepSeek, Qwen, Llama, Mistral.
- Free-only filter.
- vertical/horizontal scroll.
- visible/total model count.
- double-click/select button.
- فقط raw model id persist می‌شود؛ label قیمت/رایگان ذخیره نمی‌شود.

### 11.3 Active Provider / Model

- Radio Button مستقل روی هر Provider.
- canonical action: `ذخیره Provider و مدل فعال`.
- persist:
  - `ai_provider`
  - `ai_model`
  - `ai_model_<provider>`
- live Test Connection روی دقیقاً Provider/Model فعال.
- typed API Key فقط Secure Secret Store.
- Legacy per-card button `فعال کن` از UI حذف شده تا دو Source of Truth وجود نداشته باشد.
- save-key/test/balance/cost controls قدیمی حفظ شده‌اند.

Files:
- `catalog_center/app/phase49_3d_workflow_hardening.py`
- `catalog_center/app/phase49_3d_ai_ui_cleanup.py`

### 11.4 Auto AI Prepare on Product Open

Desktop additive columns:
- `ai_auto_prepare_hash`
- `ai_auto_prepare_status`
- `ai_auto_prepare_at`

Behavior:
- setting: `ai_auto_prepare_on_open`.
- فقط اگر Persian editorial/SEO ناقص باشد اجرا می‌شود.
- fingerprint از Source facts + selected materials/colors/images ساخته می‌شود.
- همان fingerprint دوباره API مصرف نمی‌کند.
- auto failure loop/retry نمی‌شود؛ Retry دستی باقی است.
- موفقیت مستقیم Product fields را populate و Workspace را reload می‌کند.
- Similar Persian keywords از محصولات همان category فقط editorial hint هستند و حق Override facts ندارند.

AI حق جعل ندارد:
- price
- license
- dimensions
- stock
- selected color/material

### 11.5 Local/Production Publish Preflight

قبل از Publish:
1. Save.
2. Recalculate Readiness.
3. اگر فقط Image SEO/Metadata stale است و core image موجود است → auto finalize.
4. Recalculate.
5. اگر ناقص است:
   - first incomplete stage باز می‌شود.
   - missing reasons در Dialog نمایش داده می‌شوند.
   - `preflight_blocked` audit می‌شود.
   - هیچ Batch/FTP/Import اجرا نمی‌شود.

این مسیر مشکل «Local Publish → برگشت بی‌صدا به Images» را هدف گرفته است.

### 11.6 Semantic Image SEO Signature

CI Regression:
- 49.3C raw JSON string را hash می‌کرد.
- Persian JSON قبل/بعد `ensure_ascii=False` از نظر byte فرق داشت ولی معنای یکسان داشت.
- Metadata تازه بلافاصله stale می‌شد.

Fix:
`catalog_center/app/phase49_3d_image_signature.py`

- JSON fields قبل از hash parse/normalize می‌شوند.
- serialization-only change stale نمی‌کند.
- SEO/Alt واقعی تغییر کند → signature تغییر و Stage image دوباره قرمز می‌شود.

Marker:
`EPIC49_3D_SEMANTIC_IMAGE_SIGNATURE=ENABLED`

### 11.7 Professional Price Range

Desktop:
- `price_min`
- `price_max`
- max < min → swap.
- فقط یک طرف → دو طرف برابر.
- Range خالی + final/suggested → fixed range.

Windows→Batch→Django E2E validated:
- test input `650000..850000`.
- `Product.fixed_price = 650000`.
- `Product.price_is_final = False`.
- `Product.consultation_required = True`.
- `ProductCatalogProfile.price_min = 650000`.
- `ProductCatalogProfile.price_max = 850000`.
- `ProductCatalogProfile.price_mode = range`.
- re-import همان Batch idempotent و Range پایدار است.

Server bug found by CI:
- `apply_price_range()` consultation را True می‌کرد.
- `apply_phase43_product_details()` بعداً آن را False می‌کرد.
- Fix: True قبلی حفظ می‌شود؛ Phase43 دیگر Range requirement را downgrade نمی‌کند.

Public:
- Product Detail range موجود.
- Product List اکنون range کامل نشان می‌دهد.
- Public test روی عبارت `حداقل تا حداکثر تومان` Locale-safe است.

### 11.8 Image Download Limit

طبق درخواست کاربر رفتار موجود تغییر نکرد:
- per-product `download_image_limit` موجود است.
- انتخاب کمتر از 10 محترم است.
- hard cap 49.3C = 10.
- test: limit=5 → 5؛ limit>10 → max 10.

### 11.9 Test isolation fix

CI نشان داد `test_epic49_readiness_wizard` از runtime-patched method با `inspect.getsource()` استفاده می‌کرد و Full Discovery order-dependent بود.

Fix:
- contract از canonical `app/openai_content.py` خوانده می‌شود.
- اجرای منفرد و Discovery رفتار یکسان دارند.

## 12) Phase49.3D Final CI

Validated runtime HEAD:
`e3eb0969b79fef67dc235cdbd213655140a128e1`

CI Probe:
- PR `#31`.
- Base = validated runtime HEAD.
- Head `93180ae00fdf243074bcbbb3a3dcf00477887bef`.
- Probe فقط یک docs marker اضافه داشت.
- PR بسته شد و **Merge نشد**.

Final CI:
- Run `32271502234`
- Job `96128806609`
- Checkout/Dependencies: ✅
- Compile changed Python surfaces: ✅
- Django check + `makemigrations --check --dry-run` + migrate plan: ✅
- Phase49 targeted Django/Bridge/Hero/Profile: ✅
- Windows→Batch→Django price-range E2E: ✅
- Public Store list/detail range: ✅
- Windows Catalog Center explicit tests: ✅
- Phase49.3C Persian/Translation/Image regression tests: ✅
- Phase49.3D workflow/AI UI tests: ✅
- Epic49 unittest discovery: ✅
- Full Django suite: ✅
- Overall: **SUCCESS**

CI Failهایی که قبل از Final success ریشه‌ای حل شدند:
1. Locale-specific price separator assertion.
2. Raw JSON image signature false-stale.
3. Runtime monkey-patch order-dependent readiness test.
4. Phase43 consultation overwrite after range sync.

## 13) Phase49.3D checklist

- [x] Workspace geometry root cause/fix.
- [x] Searchable full AI Model Picker.
- [x] Radio Provider + persistent Provider/Model.
- [x] Legacy AI `فعال کن` removed from canonical UI.
- [x] Exact Provider/Model Test Connection.
- [x] Auto AI Prepare + fingerprint.
- [x] Similar Persian keyword hints.
- [x] Persian content/application/SEO guards inherited from 49.3C-1.
- [x] Explicit Publish Preflight/Error dialog/Audit.
- [x] Auto image metadata finalization.
- [x] Semantic image signature.
- [x] Desktop min/max price normalization.
- [x] Windows→Batch→Django Product/Profile Range E2E.
- [x] Store List/Detail range.
- [x] Range consultation requirement preserved.
- [x] Image download limit preserved/tested.
- [x] CI workflow updated.
- [x] Final GitHub CI SUCCESS.
- [ ] Windows pull/backup/compile/tests.
- [ ] Product Workspace visual open without TclError.
- [ ] Live Provider model list/search/select/save/restart/test QA.
- [ ] Real Product Auto AI Prepare QA.
- [ ] Local Publish E2E.
- [ ] Local Django Product/Profile/Hero/Store/Home/Admin verification.
- [ ] Explicit user approval.
- [ ] Production deploy.

## 14) Environment note — django-admin-expert

طبق سیاست پروژه، قبل از Phase49.3D Plugin directory برای `django-admin-expert` بررسی شد. Plugin/Skill مستقلی با همین نام در Session فعلی موجود نبود و نتایج Search نامرتبط بودند. بنابراین Plugin اشتباه نصب نشد و ادعای نصب نیز نمی‌شود. Django/Admin این فاز بر اساس Source واقعی Repository و Django tests validate شده است.

## 15) Gate بعدی — Windows Local

1. Catalog Center و Django runserver را ببند.
2. `git status` باید clean باشد؛ هیچ reset/delete خودکار انجام نشود.
3. Fetch/Switch/Pull `epic/phase49-unified-product-slider-sync` با `--ff-only`.
4. Backup:
   - `D:\projects\3DPrintHub\db.sqlite3`
   - `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
   - persistent catalog data
5. `python manage.py check`.
6. `python manage.py makemigrations --check --dry-run` → No changes detected.
7. `python manage.py migrate --plan` → Phase49.3D migration جدید نداشته باشد.
8. Django targeted:
   - `store.test_phase49_3d_price_range`
   - `store.test_phase49_unified_import_e2e`
9. Catalog targeted:
   - `tests.test_epic49_phase49_3d_workflow_hardening`
   - `tests.test_epic49_phase49_3d_ai_ui_cleanup`
   - `tests.test_epic49_phase49_3c_image_signature`
   - Persian/Translate/Operator/Guided/Diagnostics regressions
   - Epic49 discovery
10. `python launch.py --verify-only` و Markerهای 49.3D.
11. Visual QA Product Workspace بدون TclError.
12. AI Center live QA:
   - Radio Provider
   - Search `CHATGPT`/GPT/Claude/etc.
   - visible/total model count
   - free filter
   - raw model select
   - save Provider+Model
   - restart persistence
   - Test Connection
13. Real Product Auto Prepare QA.
14. Price min/max Save/Reopen.
15. image limit=5 QA.
16. Local Publish؛ blocker باید Dialog واضح بدهد و metadata stale باید auto-finalize شود.
17. Verify Local Product/Profile/Hero/Store/Home/Admin.
18. explicit user approval.
19. فقط بعد از approval Production plan.

## 16) Production status

**NOT DEPLOYED / NOT APPROVED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3C، 49.3C-1 یا 49.3D در Production اجرا نشده است. Production تا پایان Windows Local QA و تأیید صریح کاربر دست‌نخورده می‌ماند.
