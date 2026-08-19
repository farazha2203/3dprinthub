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

## 3) Branch و Epic جاری

Branch فعال:

`epic/phase49-unified-product-slider-sync`

زنجیره خطی:

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics`

Foundationها Merge موازی نشده‌اند؛ Epic ancestry خطی است تا Conflict مصنوعی ایجاد نشود.

## 4) جدیدترین Validation — Phase49.3B

Main doc:
`docs/PHASE49_3B_GUIDED_AI_HERO_DIAGNOSTICS.md`

Hardening appendix:
`docs/PHASE49_3B_PROVIDER_HARDENING_APPENDIX.md`

Runtime hardening baseline:
`a8e74311f69db49f2131ea9df39560585568e262`

Final CI:
- Run: `32243798557`
- Job: `96039870389`
- Compile: ✅
- Django check + migration contract: ✅
- Phase49 targeted behavioral/regression: ✅
- Windows Catalog Center tests: ✅
- Full Django suite: ✅

Live provider/visual QA هنوز روی Windows انجام نشده و Production untouched است.

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

## 14) Phase49.3B — Hero Media Studio

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

Django migration:
`website.0022_phase49_hero_media_presentation`

Migration فقط Additive است؛ DROP/DELETE/TRUNCATE/RESET ندارد.

Admin و Bridge همان Media fields را روی همان HomepageHeroSlide موجود مدیریت می‌کنند؛ Hero model موازی ساخته نشده است.

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

USD Provider costs با `ai_usd_to_toman` به تومان estimate می‌شوند؛ exact provider-local cost بر estimate اولویت دارد.

## 17) Phase49.3B — Program Log / Diagnostics

SQLite additive tables:
- `app_audit_log`
- `ai_request_log`

Audit tracks:
- operator
- timestamp
- product ID
- area/action/status
- changed field names
- module/source
- runtime errors

AI log tracks request lifecycle/cost/request ID.

Diagnostic UI:
- `لاگ دیتابیسی برنامه`
- `درخواست‌های AI`
- `تکمیل هزینه AvalAI`
- `خروجی گزارش عیب‌یابی`

Secret redaction covers Bearer/Authorization/API key/password/token/secret patterns.

Diagnostic bundle:
`<Catalog persistent data>/diagnostics/catalog-diagnostic-YYYYMMDD-HHMMSS.json`

این فایل برای ارسال جهت عیب‌یابی طراحی شده و Secret ذخیره نمی‌کند.

## 18) Local historical data state

آخرین Audit قبل از Product واقعی مسیر جدید:
- Product = 0
- ImportedPrintAsset = 45
- linked Asset→Product = 0
- Hero slides = 2

Legacy Vesper/flexi-lizard Assetهای قدیمی بودند. 45 Asset نباید کورکورانه Product شوند.

تست صحیح End-to-End:
**یک Product واقعی Windows → Local Publish → Django Product/Profile/Hero → Home/Admin**.

## 19) Gate بعدی Windows Local

1. بستن Catalog Center و runserver.
2. Pull آخرین Epic.
3. Backup Django DB و Catalog Center persistent SQLite/data.
4. `python manage.py check`.
5. `python manage.py makemigrations --check --dry-run`.
6. `python manage.py migrate --plan`.
7. اگر `store.0031` یا `website.0022` Local pending هستند، فقط بعد از Backup و Plan صحیح اعمال شوند.
8. Windows targeted tests + `python launch.py --verify-only`.
9. Verify markers:
   - `EPIC49_GUIDED_WIZARD_7_STAGE=ENABLED`
   - `EPIC49_HERO_MEDIA_STUDIO=ENABLED`
   - `EPIC49_AI_PROVIDER_HUB=ENABLED`
   - `EPIC49_OPENROUTER=ENABLED`
   - `EPIC49_AI_COST_TOMAN=ENABLED`
   - `EPIC49_PERSISTENT_DIAGNOSTICS=ENABLED`
   - `EPIC49_DIAGNOSTIC_LOG_UI=ENABLED`
10. باز کردن AI Center و تست AvalAI/OpenRouter/OpenAI هرکدام جدا با کلید واقعی Operator.
11. تست مجدد همان AvalAI content generation که قبلاً HTTP400 می‌داد.
12. بررسی Provider/Model/HTTP/Request ID/Tokens/Cost در AI log.
13. Diagnostic bundle export و بررسی shareability.
14. Wizard 7 Stage + Previous/Next/Stars/Locks.
15. Hero Desktop/Mobile preview و `product_fit + contain`.
16. تکمیل یک Product واقعی و فقط `🧪 Local Publish`.
17. Verify Local Store/Home/Admin/Product/Profile/Hero.
18. Visual/user approval.
19. فقط بعد از approval: Production backup/deploy plan.

## 20) Production status

**NOT DEPLOYED / NOT APPROVED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3B یا `website.0022` در Production اجرا نشده است.
