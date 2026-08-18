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

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options/Workspace Repair`

Foundationها Merge موازی نشده‌اند؛ Epic روی یک ancestry خطی ساخته شده تا Conflict مصنوعی ایجاد نشود.

## 4) وضعیت Validation

### Epic49 Unified baseline
- CI Run: `32129944811` — SUCCESS

### Persian Sales Hero
- CI Run: `32143733191`
- Job: `95732323558` — SUCCESS

### Dual Publish Targets
- tested runtime baseline: `b14cdc6a3bcae016e373e5c7fcbf036bd0fcb029`
- CI Run: `32152308954`
- Job: `95760929653` — SUCCESS

### Desktop Options + Workspace Routing Repair — جدیدترین Gate
- runtime baseline قبل از documentation: `ec8c749cfdf8e019d0f93a4cd5fd74a86200bbb6`
- Final CI Run: `32158432992`
- Final Job: `95781188545`
- Result: **SUCCESS**

Gateهای نهایی:
- Compile: ✅
- Django check + migration contract: ✅
- Phase49 targeted behavioral/regression tests: ✅
- Windows Catalog Center tests: ✅
- Full Django suite: ✅

Warnings شناخته‌شده Failure نیستند:
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: realtime in-memory؛ برای cross-process production در صورت نیاز Redis.
- OAuth/credential dependent checks در CI ممکن است optional feature را disabled گزارش کنند.

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

قابلیت‌ها:
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

هر دو Additive هستند.

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

## 11) Desktop Options + Workspace Routing Repair — مرحله جاری

Doc کامل:
`docs/EPIC49_DESKTOP_OPTIONS_WORKSPACE_REPAIR.md`

### Root cause UI قدیمی

`launch.py` Workspace نهایی Epic را import می‌کرد، ولی `ux87_shell.py` یک alias قدیمی از `product_workspace_v87.ProductWorkspace` داشت و Product open همان کلاس قدیمی را instantiate می‌کرد.

Fix:

```python
ux87_shell.ProductWorkspace = ProductWorkspace
```

بنابراین Product double-click / Edit اکنون Workspace نهایی Epic را باز می‌کند و Patchهای Slider SEO، Dual Publish و Option Picker واقعاً در UI فعال هستند.

Marker:
`UX87_EPIC49_WORKSPACE_ROUTING=ENABLED`

### Material Picker

متریال مستقل Checkbox است.

Windows column:
`material_options_json`

Default choices:
PLA, PLA-CF, HT-PLA-GF, PETG, PET-CF, PETG-rCF08, ABS, ASA, PC-FR, TPU95, PA6-CF20, PA12-CF10, PPS-CF10.

### Rich Color Picker

رنگ مستقل Checkbox است.

Windows column:
`color_options_json`

Types:
- `solid` ساده
- `transparent` شفاف/شیشه‌ای
- `translucent` نیمه‌شفاف
- `metallic` متالیک
- `silk` ابریشمی
- `dual` دو رنگ
- `multicolor` چند رنگ
- `gradient` گرادیانی

Metadata:
- name
- main HEX
- secondary HEX
- tertiary HEX
- color type

Legacy `material_color_options_json` حذف نشده و به‌صورت derived compatibility payload نگه‌داری می‌شود.

### Windows SQLite

`catalog_center/app/epic49_desktop_schema.py`

Additive changes:
- `products.material_options_json`
- `products.color_options_json`
- `available_material_colors.color_type`
- `available_material_colors.secondary_hex`
- `available_material_colors.tertiary_hex`

### Django DB

Migration جدید:

`store.0031_phase49_rich_material_colors`

روی `MaterialColorOption`:
- color_type
- secondary_hex
- tertiary_hex

Migration فقط Additive؛ DROP/DELETE/TRUNCATE ندارد.

### Admin

`MaterialColorOptionAdmin`:
- color type filter/editor
- HEX 1/2/3
- gradient/multi swatch preview
- pricing + inventory حفظ شده.

## 12) Local historical data state

آخرین Audit قبل از اولین Product واقعی از مسیر جدید:
- Product = 0
- ImportedPrintAsset = 45
- linked Asset→Product = 0
- Hero slides = 2

Vesper/flexi-lizard legacy slides Assetهای قدیمی بدون Product کامل بودند. بعد از Persian sanitizer، متن خراب انگلیسی/Cookie حذف شد و در نبود محتوای فارسی جدید fallback عمومی فارسی دیده شد.

این 45 Asset نباید کورکورانه Product شوند. تست صحیح: **یک Product واقعی از Windows → Local Publish**.

## 13) Gate بعدی Local

1. بستن Catalog Center و runserver.
2. Pull آخرین Epic.
3. Backup:
   - Django `db.sqlite3`
   - Catalog Center persistent data/catalog SQLite.
4. `python manage.py check`
5. `python manage.py makemigrations --check --dry-run` → No changes detected.
6. `python manage.py migrate --plan`
7. انتظار migration جدید: `store.0031_phase49_rich_material_colors` (اگر هنوز Local اعمال نشده).
8. بعد از Verify/Backup: `python manage.py migrate store 0031`.
9. Django tests:
   - `store.test_phase49_rich_material_colors`
   - `store.test_epic49_operator_publish`
10. Windows tests:
   - `tests.test_epic49_material_color_picker`
   - `tests.test_epic49_studio_final`
11. `python launch.py --verify-only` و Verify markerها.
12. `python launch.py`.
13. Product واقعی را باز کن و Visual QA:
   - Slider SEO کامل.
   - Effect/Timing.
   - Local/Production buttons.
   - Material checkboxes.
   - Color checkboxes.
   - Transparent color.
   - Dual/multicolor HEX metadata.
   - Save/reopen persistence.
14. یک Product واقعی:
   - تولید Product SEO فارسی.
   - تولید Slider SEO مستقل.
   - انتخاب Hero image.
   - انتخاب material/colors.
   - `🧪 Local Publish`.
15. Verify Local Django:
   - Product created.
   - ProductCatalogProfile created.
   - rich variants/colors created.
   - HomepageHeroSlide created/updated.
   - Store/Home/Admin درست.
16. Visual/user approval.
17. فقط بعد از تأیید: Production plan.

## 14) Production status

**NOT DEPLOYED / NOT APPROVED YET.**

هیچ Migration/collectstatic/restart مربوط به `store.0031` یا Workspace Options در Production اجرا نشده است.
