# PROJECT_CONTEXT — 3DPrintHub

> این فایل Source of Truth مسیر جاری پروژه است. جزئیات فازها در `docs/` ثبت می‌شود. هنگام تعارض، وضعیت جاری این فایل + Migration state واقعی + جدیدترین خروجی تست ملاک است.

## 1) مسیرهای دائمی

- Windows project root: `D:\projects\3DPrintHub`
- Windows virtualenv: `D:\projects\3DPrintHub\.venv`
- Windows Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- Windows Catalog Center persistent/legacy data:
  - `D:\projects\3dprinthub_catalog_center`
  - `D:\projects\3dprinthub-catalog-manager`
- Windows rollback backups: `D:\projects\3dprinthub-backups`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production virtualenv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL DB: `sfkilvrs_EmiAdmin_3dprinthub`
- GitHub: `farazha2203/3dprinthub`

## 2) قانون تحویل

مسیر اجباری:

`GitHub Epic branch → Self-Test/CI → Windows pull → Local backup/migration/test → Visual/Data QA → explicit user approval → Production backup → Deploy → migrate/collectstatic/restart → smoke tests`

قواعد:

- Production قبل از تأیید Local دست نمی‌خورد.
- DB برای رفع مشکل کد Reset نمی‌شود.
- `.env`, API keys, MySQL, media, private_media و Catalog Center data حفظ می‌شوند.
- هر Migration قبل از Production روی Local/CI تست می‌شود.
- هر Repair/Backfill ابتدا Dry Run و Backup دارد.
- Windows ابزار اصلی کارمندهاست؛ Django Admin ابزار مدیریتی دوم و کامل باقی می‌ماند.

## 3) Branch فعال و زنجیره

Branch:

`epic/phase49-unified-product-slider-sync`

زنجیره خطی:

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish Targets`

Branchهای Foundation به‌صورت Merge موازی روی هم ریخته نشده‌اند تا Conflict مصنوعی ایجاد نشود.

## 4) وضعیت Validation جاری

### Epic49 Unified baseline

- Runtime baseline: `8ad84577498072cf8c3d007d8bd259d6e3428cba`
- CI Run: `32129944811`
- Result: SUCCESS

### Persian Sales Hero

- Final CI Run: `32143733191`
- Job: `95732323558`
- Result: SUCCESS

### Dual Publish Targets — جدیدترین Gate

Tested source baseline قبل از documentation:

`b14cdc6a3bcae016e373e5c7fcbf036bd0fcb029`

GitHub Actions:

- Run: `32152308954`
- Job: `95760929653`
- Result: **SUCCESS**

Gateها:

- Compile changed Python surfaces: ✅
- Django check/migration contract: ✅
- Phase49 unified behavioral/regression: ✅
- Windows Catalog Center tests: ✅
- Full Django suite: ✅

Warnings شناخته‌شده Failure نیستند:

- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: in-memory realtime؛ production cross-process در صورت نیاز Redis می‌خواهد.
- credential-dependent checks در CI ممکن است featureهای اختیاری را disabled گزارش کنند.

**Production برای Epic49 Unified / Persian Sales Hero / Dual Publish هنوز Deploy نشده است.**

## 5) Foundation 49.2A — Catalog / Store consolidation

مسیر فعال:

`Windows Catalog Center 8.7.1 → Catalog Bridge → ImportedPrintAsset → Product/ProductCatalogProfile → Store`

- Public external ready-model catalog/Link Analyzer بازنشسته شده است.
- historical data حذف نشده است.
- external autosync پیش‌فرض خاموش است.
- Material و USD/FX pricing حفظ شده‌اند.
- Catalog Center: `8.7.1`, build `2026.08.16.3`.

## 6) Foundation 49.2B — Master Admin + Customer Portal

- Design source فقط `master.zip` / Velzon Django Corporate 4.3.0.
- `interactive` ممنوع است.
- RTL Master assets: `static/velzon_master/`.
- IRANSans FaNum: 200/300/400/500/700/900.
- navy/graphite + metallic gold.
- Admin desktop login regression رفع شده است.
- Customer mobile drawer حفظ شده است.

### برند canonical

`static/img/brand/3dprinthublogo.png`

Approved SHA256:

`97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`

هیچ لوگوی جایگزین/بازطراحی‌شده نباید استفاده شود.

## 7) Foundation 49.2C — Hero Studio & Cinematic Slider

Doc:

`docs/PHASE49_2C_HERO_STUDIO.md`

قابلیت‌ها:

- Admin visual Product Album Picker.
- Image Album Picker بدون Save اولیه.
- `selected_asset_image` relation واقعی.
- Edit اسلاید موجود بدون Delete/Recreate.
- Effect/Timing per slide.
- mobile/reduced-motion fallback.

Effects:

- `cinematic_fade`
- `wedding_dissolve`
- `cinematic_zoom`
- `ken_burns`
- `soft_blur`
- `cinematic_reveal`

Migration:

`website.0020_phase49_2c_hero_studio`

Fields:

- selected_asset_image
- transition_effect
- transition_duration_ms
- display_duration_ms

## 8) Epic49 Unified Product / SEO / Slider / Desktop / Bridge

Doc:

`docs/EPIC49_UNIFIED_PRODUCT_SLIDER_SYNC.md`

مدل عملیاتی:

```text
Employee
  ↓
Catalog Center Windows
  ↓
Product + Images + Product SEO + Hero SEO + Hero image + Effect/Timing
  ↓
Catalog Bridge
  ↓
Django Product / ProductCatalogProfile / HomepageHeroSlide
  ↓
Public Store/Home
```

و برگشت:

```text
Django Admin edit
  ↓
Revision increment
  ↓
Catalog Bridge
  ↓
Windows refresh / compare
```

### Conflict Protection

- Product Profile و Hero revision مستقل دارند.
- stale Windows update → HTTP 409.
- Admin edit → revision increment.
- Employee باید Refresh/Review کند؛ تغییر مدیر silently overwrite نمی‌شود.

Idempotency:

`batch_uuid + source_hash`

همان Batch duplicate Product/Hero و revision اضافی نمی‌سازد.

## 9) Django DB contract

### Store

Migration:

`store.0030_phase49_unified_sync_contract`

`ProductCatalogProfile` fields:

- homepage_slider_title_fa
- homepage_slider_description_fa
- homepage_slider_alt_text
- homepage_slider_button_text
- homepage_slider_focus_keyword
- homepage_slider_transition_effect
- homepage_slider_transition_duration_ms
- homepage_slider_display_duration_ms
- sync_revision
- last_modified_source
- last_modified_by

### Website

Migration:

`website.0021_phase49_unified_hero_sync`

`HomepageHeroSlide` fields:

- sync_revision
- last_modified_source
- last_modified_by

Migrationها Additive هستند و DROP/DELETE/TRUNCATE ندارند.

### Store 0028/0029 history

Local audit قبل از Backfill نشان داده بود:

- linked Imported assets: 0
- Products with changes: 0
- Products with slug changes: 0

پس Local 0028/0029 بدون Product mutation اعمال شدند. Production state مستقل Verify می‌شود.

## 10) Windows DB contract

Module:

`catalog_center/app/epic49_desktop_schema.py`

Additive columns:

- homepage_slider_transition_effect
- homepage_slider_transition_duration_ms
- homepage_slider_display_duration_ms
- server_product_id
- server_product_revision
- server_slider_id
- server_slider_revision
- server_updated_at
- last_sync_conflict

Slider SEO fields از 8.7.1 وجود داشتند.

## 11) Catalog Bridge 1.3

- version: `1.3.0`
- publish contract: `epic49-unified-v1`
- Auth: existing Bearer token + constant-time compare.

Legacy endpoints:

- health
- import
- diagnostics

Unified endpoints:

- products list/detail/sync
- hero-slides list/detail/sync

Write API allow-list دارد. Hero image فقط اگر متعلق به همان Asset باشد پذیرفته می‌شود. ACK شامل Product/Hero IDs و revisions است.

## 12) Persian Sales Hero

Doc:

`docs/EPIC49_PERSIAN_SALES_HERO_HOTFIX.md`

### Problem fixed

Public Hero دیگر raw English source / Cookie / Consent / Tracking / HTML boilerplate را نمایش نمی‌دهد.

Source priority:

1. dedicated Slider Persian SEO
2. AI Slider Persian SEO
3. Product SEO فارسی Windows
4. Product editorial فارسی Windows/Imported Asset
5. Persian Product fallback
6. Persian generic sales fallback

Raw `source_title/source_description` fallback عمومی نیست.

### Sanitizer

`store/phase49_persian_sales_copy.py`

- HTML/script/style cleanup.
- Persian validation.
- Cookie/Privacy/Tracking blacklist.
- Product/Slider sales resolver.
- sales-intent focus normalization.

Focus مثال:

`آباژور سه بعدی` → `خرید آباژور سه بعدی`

Intentهای معتبر:

- خرید
- سفارش
- قیمت
- فروش
- تهیه
- ثبت سفارش

### Runtime gates

- `store/phase49_persian_sales_runtime.py`: ProductCatalogProfile global pre-save normalization.
- `website/phase49_persian_sales_hero.py`: Hero title/description/group/alt/button Persian public contract.
- `catalog_center/app/phase49_persian_sales_desktop.py`: Windows Slider fields never use raw English source fallback.

### Hero description UX

- default 2-line clamp + ellipsis.
- `نمایش بیشتر` / `بستن توضیحات`.
- autoplay paused while full text is open.

### Legacy repair

Dry run:

`python manage.py phase49_repair_persian_sales_hero`

Apply only after backup/review:

`python manage.py phase49_repair_persian_sales_hero --apply`

No migration in this hotfix.

## 13) Dual Publish Targets — مرحله جاری Local QA

Doc:

`docs/EPIC49_DUAL_PUBLISH_TARGETS.md`

### UI

Source/Developer Product Workspace دو مقصد صریح دارد:

- `🧪 انتشار آزمایشی روی کامپیوتر`
- `🌐 انتشار واقعی روی سایت اصلی`

Legacy `🚀 ارسال همین محصول` در Workspace نهایی به Production label واضح تبدیل می‌شود.

### Local Test path

```text
Windows Product Workspace
→ official build_batch(product_ids=[id])
→ standard schema 8.5 batch
→ SQLite safety preflight
→ phase37_import_catalog_center
→ Local Django DB
→ Store / Hero on 127.0.0.1
```

فایل‌ها:

- `catalog_center/app/epic49_local_publish.py`
- `catalog_center/app/phase49_dual_publish_desktop.py`

### Local Safety Gate

Local button باید ثابت کند:

- DB vendor دقیقاً `sqlite` است.
- DB file دقیقاً `D:\projects\3DPrintHub\db.sqlite3` است.

MySQL یا SQLite دیگر → `LOCAL PUBLISH BLOCKED`.

Local مسیر FTP/Bridge ندارد و از Importer رسمی Server استفاده می‌کند.

### Local state isolation

Local ACK برای QA استفاده می‌شود ولی Local IDs داخل Production `server_id/server_revision` ذخیره نمی‌شوند.

بعد از Local test Windows row به:

- `workflow_status=approved`
- `upload_ready=1`

برمی‌گردد تا Production publish یک عملیات جدا باشد.

Receiptهای Local:

- desktop_local_batch_ready
- desktop_local_imported
- desktop_local_import_review
- desktop_local_import_failed

### Production button

Production همچنان مسیر رسمی:

`build_batch → FTP → Catalog Bridge → Import → public HTTP verification → ACK`

را استفاده می‌کند و دو Confirmation با URL/host مقصد دارد.

### Portable / Employee status

Local helper در `sys.frozen` اجرای Local را Block می‌کند.

**اما UI Dual Publish در `portable_entry.py` هنوز نهایی و Build نشده است.** نسخه Portable کارمندان فقط بعد از تأیید Local real-data E2E همسان‌سازی و Build می‌شود. نباید قبل از آن ادعا شود EXE جدید آماده است.

### Migration

Dual Publish Migration جدید ندارد.

### CI

- Run: `32152308954`
- Job: `95760929653`
- Result: SUCCESS

## 14) وضعیت داده Local تاریخی

آخرین Audit قبل از Product واقعی جدید:

- `Product = 0`
- `ImportedPrintAsset = 45`
- linked Asset→Product = 0
- Hero slides = 2

Heroهای قدیمی Vesper / flexi lizard به Assetهای قدیمی بدون Product کامل متصل بودند. بعد از Persian sanitizer متن Cookie/English حذف شد ولی به‌دلیل نبود Slider SEO فارسی جدید، fallback عمومی فارسی دیده شد.

این 45 Asset نباید با Backfill کورکورانه Product شوند. تست واقعی باید از Windows Publish جدید عبور کند.

## 15) Gate بعدی — Real-data Local E2E

1. Pull آخرین Epic روی `D:\projects\3DPrintHub`.
2. Verify clean worktree.
3. `python manage.py check`.
4. `python manage.py makemigrations --check --dry-run` → No changes detected.
5. Windows `tests.test_epic49_dual_publish`.
6. `launch.py --verify-only` و Markerهای Dual Publish.
7. Start Django Local runserver.
8. بازکردن یک Product واقعی در Windows.
9. تولید/بازبینی Product SEO فارسی.
10. تولید/بازبینی Slider SEO مستقل فارسی.
11. انتخاب Slider image + effect/timing.
12. تکمیل publish gates: image/category/price/license/approval.
13. کلیک فقط روی `🧪 انتشار آزمایشی روی کامپیوتر`.
14. Verify Product/Asset/Profile/Hero روی Local DB.
15. Visual QA روی Store/Home/Admin.
16. بررسی اینکه Hero متن اختصاصی Windows را نشان می‌دهد، نه generic fallback.
17. User explicit approval.
18. سپس Portable employee build alignment.
19. فقط بعد از آن Production backup/deploy plan.

## 16) Production status

**NOT DEPLOYED / NOT APPROVED YET.**

هیچ deploy/migrate/repair/collectstatic/restart مربوط به Epic49 Unified، Persian Sales Hero یا Dual Publish از این مسیر روی Production انجام نشده است.
