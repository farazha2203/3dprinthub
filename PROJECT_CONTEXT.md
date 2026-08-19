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
- Migrationها ابتدا CI و Local.
- Repair/Backfill ابتدا Dry Run + Backup.
- Windows Catalog Center ابزار اصلی کارمند است؛ Django Admin ابزار مدیریتی دوم و کامل است.
- Python/Django زبان پروژه؛ PowerShell برای عملیات Windows.

## 3) Branch و زنجیره جاری

Branch فعال:

`epic/phase49-unified-product-slider-sync`

زنجیره خطی:

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options/Workspace Repair → Phase49.3A Publish Readiness`

Foundationها Merge موازی نشده‌اند؛ Epic روی یک ancestry خطی ساخته شده تا Conflict مصنوعی ایجاد نشود.

## 4) وضعیت Validation

### Epic49 Unified baseline
- CI Run: `32129944811` — SUCCESS

### Persian Sales Hero
- CI Run: `32143733191`
- Job: `95732323558` — SUCCESS

### Dual Publish Targets
- CI Run: `32152308954`
- Job: `95760929653` — SUCCESS

### Desktop Options + Workspace Routing Repair
- tested runtime baseline: `ec8c749cfdf8e019d0f93a4cd5fd74a86200bbb6`
- CI Run: `32158432992`
- Job: `95781188545` — SUCCESS

### Phase49.3A Product Publish Readiness — جدیدترین Gate
- CI Run: `32234579086`
- Job: `96011595438`
- Result: **SUCCESS**

Gateهای نهایی:
- Compile: ✅
- Django check + migration contract: ✅
- Phase49 targeted behavioral/regression tests: ✅
- Windows Catalog Center + Readiness Wizard tests: ✅
- Full Django suite: ✅

Warnings شناخته‌شده Failure نیستند:
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: realtime in-memory؛ برای cross-process production در صورت نیاز Redis.
- OAuth/credential-dependent checks در CI ممکن است optional feature را disabled گزارش کنند.

**Production برای تغییرات جاری Epic49 هنوز Deploy نشده است.**

## 5) Foundation 49.2A — Catalog / Store consolidation

مسیر فعال:

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

مدل:

```text
Employee → Windows Catalog Center
→ Product + Images + Product SEO + Slider SEO + Hero image + Effect/Timing
→ Catalog Bridge
→ Django Product / ProductCatalogProfile / HomepageHeroSlide
→ Store/Home
```

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

Public Hero دیگر raw English/Cookie/Consent/Tracking/HTML را نشان نمی‌دهد.

Source priority:
1. dedicated Slider Persian SEO
2. AI Slider Persian SEO
3. Product SEO فارسی Windows
4. Persian Imported/Product editorial
5. Persian Product fallback
6. Persian generic sales fallback

Focus keyword تراکنشی می‌شود؛ مثال:
`آباژور سه بعدی → خرید آباژور سه بعدی`

Hero UX:
- توضیح 2-line clamp + ellipsis.
- `نمایش بیشتر / بستن توضیحات`.
- autoplay هنگام خواندن متن کامل pause می‌شود.

Repair command:
- Dry run: `python manage.py phase49_repair_persian_sales_hero`
- Apply فقط بعد از Backup: `python manage.py phase49_repair_persian_sales_hero --apply`

## 10) Dual Publish Targets

Doc: `docs/EPIC49_DUAL_PUBLISH_TARGETS.md`

Windows Source/Developer:
- `🧪 انتشار آزمایشی روی کامپیوتر`
- `🌐 انتشار واقعی روی سایت اصلی`

Local path:
`build_batch → SQLite guard → phase37_import_catalog_center → D:\projects\3DPrintHub\db.sqlite3`

Local Guard:
- vendor دقیقاً SQLite.
- DB دقیقاً `D:\projects\3DPrintHub\db.sqlite3`.
- MySQL/SQLite دیگر/portable runtime block.
- Local path FTP/Bridge ندارد.
- Local IDs در production server IDs/revisions ذخیره نمی‌شوند.

Production path:
`build_batch → FTP → Bridge → Import → public HTTP verification → ACK`

Production دکمه دو confirmation و مقصد واضح دارد.

## 11) Desktop Options + Workspace Routing Repair

Doc: `docs/EPIC49_DESKTOP_OPTIONS_WORKSPACE_REPAIR.md`

Root cause UI قدیمی:
`ux87_shell.py` alias قدیمی `product_workspace_v87.ProductWorkspace` را نگه داشته بود.

Fix:

```python
ux87_shell.ProductWorkspace = ProductWorkspace
```

Marker:
`UX87_EPIC49_WORKSPACE_ROUTING=ENABLED`

Material Picker:
- متریال مستقل Checkbox.
- Windows: `material_options_json`.

Rich Color Picker:
- رنگ مستقل Checkbox.
- Windows: `color_options_json`.
- Types: `solid`, `transparent`, `translucent`, `metallic`, `silk`, `dual`, `multicolor`, `gradient`.
- Metadata: main/secondary/tertiary HEX.
- legacy `material_color_options_json` به‌صورت derived compatibility حفظ شده.

Windows SQLite additive:
- `products.material_options_json`
- `products.color_options_json`
- `available_material_colors.color_type`
- `available_material_colors.secondary_hex`
- `available_material_colors.tertiary_hex`

Django migration:
`store.0031_phase49_rich_material_colors`

روی `MaterialColorOption`:
- color_type
- secondary_hex
- tertiary_hex

Migration فقط Additive است.

## 12) Phase49.3A — Product Publish Readiness Wizard

Doc: `docs/PHASE49_3A_PRODUCT_PUBLISH_READINESS.md`

### هدف

هر Product در Windows یک Wizard وضعیت انتشار دارد. وضعیت از دیتای واقعی محاسبه می‌شود و صرفاً UI decoration نیست.

منوی سمت راست:
- `✅` مرحله کامل.
- `❌` مرحله ناقص.
- `مرحله بعد: ...` به اولین Stage ناقص می‌رود.
- `✨ پیشنهاد AI برای موارد ناقص`.
- `🧪 انتشار آزمایشی روی کامپیوتر`.
- `🌐 انتشار واقعی روی سایت اصلی`.

Stages:
1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. بررسی و انتشار

Production Publish فقط وقتی همه Gateهای لازم سبز باشند فعال می‌شود. Direct callback هم دوباره Readiness را بررسی می‌کند و قابل bypass نیست.

### Gateهای اصلی

اطلاعات پایه:
- عنوان فارسی
- گروه سایت معتبر
- نوع محصول

سفارش/گزینه‌ها:
- قیمت معتبر یا order/portfolio mode
- حداقل یک متریال واقعی
- حداقل یک رنگ واقعی

تصاویر:
- primary image
- حداقل یک selected image

Content/SEO:
- عنوان فارسی
- توضیح فارسی
- SEO Title فارسی
- SEO Description فارسی
- حداقل 3 عبارت هدف SEO
- Alt تصویر

منبع/مجوز:
- source URL
- مجوز تجاری قابل انتشار

Publish:
- approval
- publish type
- اگر Slider روشن است: Slider title/description/alt/focus/image نیز اجباری‌اند.

### SEO Editable Lists

- `materials_json` از Material checkbox واقعی Product sync می‌شود.
- `colors_json` از Color checkbox واقعی Product sync می‌شود.
- `keywords_json` بانک عبارت‌های هدف Search/Content است؛ برای meta-keywords منسوخ یا keyword stuffing نیست.
- اگر Keywords خالی باشد fallback فروش‌محور deterministic ساخته می‌شود.

نمونه:
- خرید گکو مفصلی سه بعدی
- سفارش گکو مفصلی سه بعدی
- قیمت گکو مفصلی سه بعدی
- گکو مفصلی سه بعدی PLA
- گکو مفصلی سه بعدی شفاف

AI schema:
- `target_keywords_fa` اضافه شده.
- `selected_materials` و `selected_colors` به Prompt می‌روند.
- AI حق اختراع Material/Color ندارد؛ فقط از انتخاب واقعی اپراتور استفاده می‌کند.

Markerها:
- `EPIC49_READINESS_WIZARD=ENABLED`
- `EPIC49_SEO_REFERENCE_SYNC=ENABLED`

### DB

Phase49.3A Migration جدید ندارد؛ Readiness Runtime-calculated است.
Migration قبلی Rich Color همچنان `store.0031_phase49_rich_material_colors` است.

### Validation

- CI Run: `32234579086`
- Job: `96011595438`
- Compile: PASS
- Migration Contract: PASS
- Targeted regression: PASS
- Windows Readiness tests: PASS
- Full Django suite: PASS

## 13) Local historical data state

آخرین Audit قبل از اولین Product واقعی از مسیر جدید:
- Product = 0
- ImportedPrintAsset = 45
- linked Asset→Product = 0
- Hero slides = 2

Vesper/flexi-lizard legacy slides Assetهای قدیمی بدون Product کامل بودند. بعد از Persian sanitizer، متن خراب انگلیسی/Cookie حذف شد و در نبود محتوای فارسی جدید fallback عمومی فارسی دیده شد.

این 45 Asset نباید کورکورانه Product شوند. تست صحیح: **یک Product واقعی از Windows → Local Publish**.

## 14) Gate بعدی Local

1. بستن Catalog Center و runserver.
2. Pull آخرین Epic.
3. Backup Django DB و Catalog Center persistent SQLite/data.
4. `python manage.py check`.
5. `python manage.py makemigrations --check --dry-run` → No changes detected.
6. `python manage.py showmigrations store` و `python manage.py migrate --plan`.
7. اگر `store.0031_phase49_rich_material_colors` هنوز Local اعمال نشده، فقط بعد از Backup/Verify اعمال شود.
8. Windows tests:
   - `tests.test_epic49_readiness_wizard`
   - `tests.test_epic49_material_color_picker`
   - `tests.test_epic49_studio_final`
9. `python launch.py --verify-only` و Verify markerهای Readiness/SEO reference/Dual Publish/Material Picker.
10. `python launch.py`.
11. Visual QA روی یک Product واقعی:
   - ✅/❌ کنار شش Stage.
   - دکمه Next Stage.
   - AI helper.
   - SEO Editable Lists: keywords/materials/colors populated.
   - Slider SEO + Effect/Timing.
   - Local/Production buttons در rail.
   - Production تا تکمیل Gateها disabled.
12. Product واقعی را کامل کن و فقط `🧪 Local Publish` را اجرا کن.
13. Verify Local Django: Product/Profile/rich colors/Hero/Store/Home/Admin.
14. Visual/user approval.
15. فقط بعد از تأیید: Production plan.

## 15) Production status

**NOT DEPLOYED / NOT APPROVED YET.**

هیچ deploy/migrate/collectstatic/restart مربوط به `store.0031`, Workspace Options یا Phase49.3A در Production اجرا نشده است.
