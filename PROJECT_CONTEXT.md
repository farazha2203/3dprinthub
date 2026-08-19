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

## 3) Branch و Epic جاری

Branch فعال:

`epic/phase49-unified-product-slider-sync`

زنجیره خطی:

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics → 49.3C Operator Workflow Recovery → 49.3C-1 Persian Content Integrity`

Foundationها Merge موازی نشده‌اند؛ Epic ancestry خطی است تا Conflict مصنوعی ایجاد نشود.

## 4) Validation تاریخی — Phase49.3B

Main doc:
`docs/PHASE49_3B_GUIDED_AI_HERO_DIAGNOSTICS.md`

Hardening appendix:
`docs/PHASE49_3B_PROVIDER_HARDENING_APPENDIX.md`

Final gapfix appendix:
`docs/PHASE49_3B_FINAL_GAPFIX_APPENDIX.md`

Windows launch import hotfix:
`docs/PHASE49_3B_WINDOWS_LAUNCH_IMPORT_HOTFIX.md`

Clean runtime/test baseline قبل از Documentation نهایی:
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
- Windows temp SQLite `WinError 32` در test cleanup شناسایی و روی GitHub fix شد.
- `phase49_3b_ai_product_runtime` ImportError برای symbol ناموجود `sync_seo_reference_lists` شناسایی و روی GitHub fix شد.

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
- `website.0022_phase49_hero_media_presentation` → presentation fields روی HomepageHeroSlide
- `store.0032_phase49_slider_media_profile` → همان contract روی ProductCatalogProfile

هر دو Migration فقط Additive هستند؛ DROP/DELETE/TRUNCATE/RESET ندارند.

دلیل `store.0032`:
تنظیمات قاب‌بندی Windows حتی وقتی `homepage_slider_enabled=False` است باید روی Product Profile ماندگار بماند و بعداً با فعال‌شدن Slider از بین نرود.

Sync contract:
`Windows → ProductCatalogProfile → HomepageHeroSlide → Home`

Reverse:
`ProductProfile Admin ↔ Hero Admin ↔ Bridge ↔ Windows`

Admin و Bridge همان Media fields را مدیریت می‌کنند؛ Hero model موازی ساخته نشده است.

Runtime ordering مهم:
Unified Sync ابتدا publish function را rebind می‌کند؛ Profile Media wrapper بعد از آن نصب می‌شود تا overwrite نشود.

## 15) Phase49.3B — AI Provider Hub

Providerها:
- AvalAI
- OpenRouter
- OpenAI Direct

هر Provider کارت مستقل دارد:
- API Key
- Model
- دریافت مدل‌ها
- live test
- اعتبار/هزینه
- Activate
- Status

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
- اگر gateway/model `response_format` را با HTTP400/invalid_request/unsupported رد کند، یک retry بدون `response_format` انجام و JSON سمت Client parse/validate می‌شود.

این مسیر Regression گزارش‌شده AvalAI `HTTP 400 invalid_request` را پوشش می‌دهد و تست اختصاصی دارد.

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

USD Provider costs با setting `ai_usd_to_toman` به تومان تبدیل و در SQLite **پایدار** می‌شوند؛ exact provider-local cost بر estimate اولویت دارد.

هیچ Balance یا Exact Cost بدون داده Provider ساخته نمی‌شود.

## 17) Phase49.3B — Program Log / Diagnostics / Audit identity

SQLite additive tables:
- `app_audit_log`
- `ai_request_log`

هر دو Log اکنون dedicated identity columns دارند:
- `operator`
- `workstation`
- `session_id`

Operator resolution:
1. Catalog setting `operator_name`
2. `CATALOG_OPERATOR_NAME`
3. Windows user

Workstation:
`COMPUTERNAME` یا hostname.

Session:
یک UUID برای هر اجرای Catalog Center.

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

Diagnostic UI:
- نام اپراتور + ذخیره
- workstation/session display
- `لاگ دیتابیسی برنامه`
- `درخواست‌های AI`
- `تکمیل هزینه AvalAI`
- `خروجی گزارش عیب‌یابی`
- Copy Details / Copy Request ID

Secret redaction covers Bearer/Authorization/API key/password/token/secret patterns.

Diagnostic bundle:
`<Catalog persistent data>/diagnostics/catalog-diagnostic-YYYYMMDD-HHMMSS.json`

این فایل برای ارسال جهت عیب‌یابی طراحی شده و Secret ذخیره نمی‌کند.

زنجیره قابل بررسی:
`operator → workstation → session → product → provider/model → operation → Request ID → HTTP → duration → tokens → cost → sanitized error`

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

علت شروع:
Visual QA واقعی نشان داد Stage-level readiness برای Operator کافی نیست و تعدادی از Editorial AI fieldها خالی می‌مانند؛ همچنین Thumbnail mapping قدیمی می‌توانست URL و local file را با index اشتباه نمایش دهد.

Root causeها:
1. Readiness عمدتاً از DB saved state خوانده می‌شد، نه Widgetهای unsaved.
2. Image local resolver در نبود exact mapping از sorted file index حدس می‌زد؛ بعد از primary reorder کارت می‌توانست عکس اشتباه نمایش دهد.
3. AI Schema fieldها را داشت، اما empty string/array می‌توانست به‌عنوان response معتبر عبور کند.

Implementation:
- `phase49_3c_operator_recovery.py`
  - live 180ms debounce.
  - Widget snapshot.
  - exact missing-field list.
  - Stage AI + Global AI.
  - Queue/Local/Production fail-closed.
- `phase49_3c_ai_recovery.py`
  - commerce completeness validation.
  - one structured repair request.
  - conservative deterministic editorial fallback.
  - factual price/license/material/color selection جعل نمی‌شود.
- `phase49_3c_image_pipeline.py`
  - max 10 source images.
  - canonical URL dedupe.
  - SHA-256 + conservative visual duplicate filtering (dHash + dimensions + mean luminance).
  - exact URL/file identity; no index fallback.
  - filename before/SEO filename display.
  - final WebP SEO images always regenerated from original/source cache, not prior lossy SEO derivatives.
  - unsaved operator edits are saved before image finalization.
  - creator/copyright/license/source/operator/publisher metadata.
  - third-party copyright preservation.
  - `seo_signature` stale metadata detection.

Desktop additive data:
- `products.image_metadata_json` با `ALTER TABLE ADD COLUMN`.
- No Django migration for 49.3C.
- Source/cache images حذف یا reset نمی‌شوند.
- Final files در `<product local_dir>/seo_images/`.
- Metadata canonical record: `image_seo_manifest.json`.

Batch:
- Final SEO filename حفظ می‌شود.
- نهایی‌سازی فایل دیگر نام انسانی را به `001.webp` برنمی‌گرداند.
- `image_metadata_json` داخل `desktop_editorial.json` و Imported Asset source payload می‌ماند.

Markers:
- `EPIC49_3C_LIVE_READINESS=ENABLED`
- `EPIC49_3C_STAGE_AI=ENABLED`
- `EPIC49_3C_IMAGE_ID_SAFE_DELETE=ENABLED`
- `EPIC49_3C_IMAGE_LIMIT_10=ENABLED`
- `EPIC49_3C_IMAGE_SEO_METADATA=ENABLED`
- `EPIC49_3C_AI_COMPLETENESS_RECOVERY=ENABLED`

Dedicated tests:
- `catalog_center/tests/test_epic49_phase49_3c_operator_recovery.py`
- `catalog_center/tests/test_epic49_phase49_3c_image_signature.py`

`image_signature` regression ثابت می‌کند بعد از Finalize، تغییر SEO/Alt/Attribution دوباره Image Stage را stale/قرمز می‌کند.

CI:
`.github/workflows/phase49-epic-ci.yml` new modules را compile می‌کند و test 49.3C را explicit + Epic49 discovery اجرا می‌کند.

## 19.1) Phase49.3C-1 — Persian AI Content Integrity & Workspace Persistence

Doc:
`docs/PHASE49_3C_PERSIAN_CONTENT_HOTFIX.md`

Visual QA جدید نشان داد Regression فقط در AI generation نیست؛ دو لایه مستقل وجود داشت:
1. fallback می‌توانست متن انگلیسی source را وارد فیلد `_fa` کند.
2. Product Workspace واقعی همه فیلدهای SEO را در Reload/Save round-trip نمی‌کرد.

Repair:
- `catalog_center/app/phase49_3c_persian_content.py`
- Structured Schema اکنون `use_description_fa` را نیز الزام می‌کند.
- تمام editorial/SEO fields فارسی Gate دارند.
- English source هیچ‌وقت fallback فارسی نمی‌شود.
- Provider در صورت خروجی غیر فارسی یک Structured Persian Repair می‌گیرد.
- Provider failure فقط fallback فارسی محافظه‌کارانه می‌سازد و `translation_status/content_status = needs_review` می‌شود؛ انتشار Silent مجاز نیست.
- `description_fa` به HTML fragment محدود و sanitize می‌شود.
- Workspace Reload فیلدهای SEO/Tag/Hashtag/Keyword/Alt/Material Recommendation را از DB برمی‌گرداند.
- Workspace Save همان فیلدها را دوباره در DB persist می‌کند.
- `use_description_fa` به `use_description` موجود در Product وصل می‌شود؛ Migration جدید لازم نیست.
- Readiness علاوه بر non-empty بودن، فارسی بودن Content/SEO را نیز بررسی می‌کند.
- Snapshot زنده `use_description` را از Widget فعلی می‌خواند.

فیلدهای SEO باید کاملاً فارسی باشند:
- SEO Title
- SEO Description
- Keywords
- Tags
- Hashtags
- Image Alt
- Slider SEO

کدهای فنی مانند `PLA/PETG` فقط در فیلدهای فنی/متریال مجازند و نباید به‌عنوان عبارت SEO انگلیسی تولید شوند.

HTML مجاز:
`p`, `br`, `strong`, `em`, `ul`, `ol`, `li`, `h3`, `h4`

HTML خطرناک/غیرمجاز:
`script`, `style`, `iframe`, event handlers و URL جدید تولیدشده توسط AI.

Dedicated test:
`catalog_center/tests/test_epic49_phase49_3c_persian_content.py`

Markers جدید:
- `EPIC49_3C_PERSIAN_CONTENT_GUARD=ENABLED`
- `EPIC49_3C_PERSIAN_SEO=ENABLED`
- `EPIC49_3C_HTML_SANITIZATION=ENABLED`
- `EPIC49_3C_WORKSPACE_CONTENT_PERSISTENCE=ENABLED`

Current implementation commits:
- Persian guard: `f95a86ff96ca7f3e540e93d4b37a9971b84948ab`
- Launcher activation: `cbc6e5e4121cd26078abdd0a3cdb5346c8d98c1c`
- Persian tests: `ec2a644f8b80b1b369623a65f04f1483a3be677c`
- Hotfix documentation: `a9afb8197855a7b73a0aa6fc606a090083a2c6fd`

Current checklist:
- [x] Persian AI/SEO guard implemented on GitHub.
- [x] `use_description_fa` added to structured contract at runtime.
- [x] Workspace SEO Reload/Save persistence repaired.
- [x] Persian language readiness gate added.
- [x] HTML fragment sanitization added.
- [x] Dedicated Persian regression tests committed.
- [x] Hotfix documentation committed.
- [ ] Final GitHub CI result verified for hotfix HEAD.
- [ ] Windows pull / compile / dedicated tests.
- [ ] `launch.py --verify-only` with new markers.
- [ ] Real Product AI Visual QA.
- [ ] Save/Reopen persistence QA.
- [ ] Image delete exact-identity QA.
- [ ] Image SEO/Metadata QA.
- [ ] Local Publish E2E.
- [ ] Explicit user approval.
- [ ] Production deploy.

## 20) Gate بعدی Windows Local — Phase49.3C / 49.3C-1

1. Catalog Center و Django runserver را برای Pull/initial tests ببند.
2. Pull آخرین `epic/phase49-unified-product-slider-sync`.
3. Verify exact HEAD اعلام‌شده پس از Final CI/docs.
4. Backup:
   - `D:\projects\3DPrintHub\db.sqlite3`
   - Catalog persistent SQLite/data.
5. Django migrations دوباره اعمال نشوند؛ Local فعلی:
   - `[X] store.0031`
   - `[X] store.0032`
   - `[X] website.0022`
6. `python manage.py check`.
7. `python manage.py makemigrations --check --dry-run` → `No changes detected`.
8. Phase49.3C/49.3C-1 Django migration ندارد؛ `migrate --plan` نباید migration جدید نشان دهد.
9. Windows dedicated:
   - `python -m unittest -v tests.test_epic49_phase49_3c_operator_recovery`
   - `python -m unittest -v tests.test_epic49_phase49_3c_image_signature`
   - `python -m unittest -v tests.test_epic49_phase49_3c_persian_content`
   - Phase49.3B regression modules.
   - Epic49 discovery.
10. `python launch.py --verify-only` و Markerهای 49.3B + 49.3C + Persian hotfix.
11. برنامه را باز کن و همان Fanart/Flexi product را تست کن:
   - Missing list از بدو Load.
   - قیمت/متن/checkbox → تغییر زنده قرمز/سبز.
   - AI همین مرحله.
   - Global AI.
   - عنوان فارسی، توضیح کوتاه، توضیح کامل و توضیحات کاربرد محصول.
   - SEO Title/Description/Keywords/Tags/Hashtags کاملاً فارسی.
   - HTML توضیح کامل با tagهای مجاز.
   - Save → Close/Reopen → همان محتوا باقی بماند.
   - تغییر دستی SEO → Save → Reopen → تغییر باقی بماند.
   - image filename current/SEO.
   - انتخاب یک عکس و حذف دقیق همان عکس.
   - max 10 image intake.
   - duplicate filtering.
   - SEO Finalize و Metadata.
   - تغییر SEO بعد از Finalize → stale Metadata دوباره قرمز.
12. فقط پس از همه Gateها یک `🧪 Local Publish`.
13. Verify Django Local Product/Profile/Hero/Store/Home/Admin.
14. Visual/user approval.
15. بعد از approval فقط Production plan اجرا شود.

## 21) Production status

**NOT DEPLOYED / NOT APPROVED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3C یا 49.3C-1 در Production اجرا نشده است.
`website.0022` و `store.0032` نیز طبق وضعیت ثبت‌شده هنوز فقط Local هستند و Production برای این Epic قبل از approval دست‌نخورده می‌ماند.
