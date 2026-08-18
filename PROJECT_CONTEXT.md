# PROJECT_CONTEXT — 3DPrintHub

> این فایل Source of Truth مسیر جاری پروژه است. جزئیات تاریخی هر فاز در `docs/` نگه‌داری می‌شود. هنگام تعارض، وضعیت جاری این فایل + Migration state واقعی + خروجی تست جدیدتر ملاک است.

## 1) مسیرهای دائمی

- Windows project root: `D:\projects\3DPrintHub`
- Windows virtualenv: `D:\projects\3DPrintHub\.venv`
- Windows Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- Windows Catalog Center runtime/data legacy paths:
  - `D:\projects\3dprinthub_catalog_center`
  - `D:\projects\3dprinthub-catalog-manager`
- Windows rollback backups: `D:\projects\3dprinthub-backups`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production virtualenv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL DB: `sfkilvrs_EmiAdmin_3dprinthub`
- GitHub: `farazha2203/3dprinthub`

## 2) قانون تحویل

مسیر اجباری:

`GitHub Epic branch → Self-Test/CI → Windows pull → Local DB backup/migration/test → Visual QA → explicit user approval → Production DB/media backup → Deploy → migrate/collectstatic/restart → smoke tests`

قواعد:

- Production قبل از تأیید Local دست نمی‌خورد.
- DB برای حل مشکل کد Reset نمی‌شود.
- `.env`, API keys, MySQL, media, private_media, Catalog Center data حفظ می‌شوند.
- هر Migration قبل از Production باید روی Local/CI تست شده باشد.
- هر عملیات Repair/Backfill ابتدا Dry Run/Backup دارد.

## 3) Branch فعال

`epic/phase49-unified-product-slider-sync`

این Branch زنجیره خطی Phase49 را یکپارچه کرده است:

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero Hotfix`

Branchهای Foundation به‌صورت Merge موازی روی هم ریخته نشده‌اند؛ Epic از آخرین زنجیره خطی ساخته شد تا Conflict مصنوعی ایجاد نشود.

## 4) وضعیت فعلی Validation

### Epic49 Unified baseline

Baseline Runtime قبلی که Full CI سبز داشت:

`8ad84577498072cf8c3d007d8bd259d6e3428cba`

Run:

`32129944811`

### Persian Sales Hero Hotfix — validation جدید

آخرین Runtime commit پیش از documentation:

`dc1699d5e78563205dbac66f219f765601055456`

Final GitHub Actions:

- Run: `32143733191`
- Job: `95732323558`
- Result: **SUCCESS**

Gateها:

- Compile changed Python surfaces: ✅
- Django check: ✅
- `makemigrations --check --dry-run`: ✅ No changes detected
- Migration contract/plan: ✅
- Phase49 targeted Django/Bridge/Hero tests: ✅
- Windows Catalog Center Epic49 tests: ✅
- Full Django suite: ✅

Warnings فعلی Failure نیستند:

- `3dprinthub.W001`: Google membership در CI به‌دلیل credentials خالی disabled است.
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: in-memory realtime؛ برای cross-process production در صورت نیاز Redis تنظیم شود.

**Production در Epic49 Unified و Persian Sales Hero Hotfix هنوز Deploy نشده است.**

## 5) Foundation 49.2A — Catalog/Store consolidation

مسیر فعال محصول:

`Windows Catalog Center 8.7.1 → Catalog Bridge → ImportedPrintAsset → Product/ProductCatalogProfile → Store`

- Public external ready-model catalog/Link Analyzer intake بازنشسته شده و نباید برای پاس‌شدن تست قدیمی برگردد.
- historical data حذف نشده است.
- external autosync به‌صورت پیش‌فرض خاموش است.
- Material و USD/FX pricing حفظ شده‌اند.
- Catalog Center version: `8.7.1`
- build: `2026.08.16.3`

## 6) Foundation 49.2B — Master Admin + Customer Portal

- Design source: `master.zip` (Velzon Django Corporate 4.3.0) فقط.
- `interactive` رد شده و نباید استفاده شود.
- Master RTL assets: `static/velzon_master/`
- IRANSans FaNum six weights: 200/300/400/500/700/900.
- Admin/customer navy/graphite + metallic gold design system.
- Desktop Admin login 460px regression رفع شده است.
- Customer Portal mobile drawer حفظ شده است.

### برند canonical

فایل:

`static/img/brand/3dprinthublogo.png`

Approved SHA256:

`97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`

هیچ لوگوی جایگزین/بازطراحی‌شده نباید جای این فایل استفاده شود.

## 7) Foundation 49.2C — Hero Studio & Cinematic Slider

سند:

`docs/PHASE49_2C_HERO_STUDIO.md`

قابلیت‌ها:

- Admin visual Product Album Picker
- Image Album Picker بدون Save اولیه
- `selected_asset_image` relation واقعی
- ویرایش Slide موجود بدون Delete/Recreate
- Effect/Timing per slide
- mobile/reduced-motion behavior

Effects:

1. `cinematic_fade`
2. `wedding_dissolve`
3. `cinematic_zoom`
4. `ken_burns`
5. `soft_blur`
6. `cinematic_reveal`

Migration:

`website.0020_phase49_2c_hero_studio`

Persistent fields:

- selected_asset_image
- transition_effect
- transition_duration_ms
- display_duration_ms

Migration فقط Additive است.

## 8) Epic49 Unified Product / SEO / Slider / Desktop / Bridge

سند کامل:

`docs/EPIC49_UNIFIED_PRODUCT_SLIDER_SYNC.md`

مدل عملیاتی:

```text
Employee
  ↓
Catalog Center Windows
  ↓
Product + Images + Product SEO + Hero SEO + Hero Image + Effect/Timing
  ↓
Catalog Bridge
  ↓
Django Product / ProductCatalogProfile / HomepageHeroSlide
  ↓
Public Store/Home
```

و برگشت:

```text
Django Admin / Server edit
  ↓
Revision increment
  ↓
Catalog Bridge
  ↓
Windows refresh / compare
```

Windows ابزار اصلی کارمند است؛ Admin سایت ابزار مدیریتی دوم و کامل است.

### Conflict Protection

- Product profile و Hero revision مستقل دارند.
- Stale Windows update روی Server جدید → HTTP 409.
- مدیر سایت اگر Product/Hero را Edit کند Revision بالا می‌رود.
- Employee باید Refresh/Review کند و تغییر مدیر silently overwrite نمی‌شود.

Idempotency:

`batch_uuid + source_hash`

اجرای دوباره همان Batch revision بی‌دلیل بالا نمی‌برد و duplicate Product/Hero نمی‌سازد.

## 9) Epic49 Django DB contract

### Store

Migration:

`store.0030_phase49_unified_sync_contract`

روی `ProductCatalogProfile`:

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

روی `HomepageHeroSlide`:

- sync_revision
- last_modified_source
- last_modified_by

هر دو Migration Additive هستند؛ DROP/DELETE/TRUNCATE ندارند.

### Store 0028/0029 history

Local audit قبلی نشان داد قبل از اجرای Backfill:

- Imported assets linked to Product: 0
- Products with changes: 0
- Products with slug changes: 0

پس `store.0028` و `store.0029` روی Local قبلاً بدون Product mutation اعمال شدند. Production state باید قبل از deploy جداگانه Verify شود و از Local فرض نشود.

## 10) Windows DB contract

Module:

`catalog_center/app/epic49_desktop_schema.py`

Additive SQLite columns:

- homepage_slider_transition_effect
- homepage_slider_transition_duration_ms
- homepage_slider_display_duration_ms
- server_product_id
- server_product_revision
- server_slider_id
- server_slider_revision
- server_updated_at
- last_sync_conflict

Slider SEO fields از قبل در 8.7.1 وجود داشتند و حفظ شدند.

## 11) Catalog Bridge 1.3

Contract:

- version: `1.3.0`
- publish contract: `epic49-unified-v1`
- Auth: existing Bearer token + constant-time compare.

Legacy endpoints حفظ شده‌اند:

- health
- import
- diagnostics

Unified endpoints:

- products list/detail/sync
- hero-slides list/detail/sync

Write API allow-list دارد. Hero image فقط اگر متعلق به همان Asset باشد پذیرفته می‌شود.

ACK Import شامل server product/slider ID + revisions است تا Windows state sync شود.

## 12) Persian Sales Hero Hotfix — مرحله جاری

سند کامل:

`docs/EPIC49_PERSIAN_SALES_HERO_HOTFIX.md`

### مسئله

Hero قدیمی می‌توانست این نوع داده را عمومی کند:

- English source title مثل `Vesper – Sculptural Bedside Lamp`
- Cookie/Consent/Tracking text
- HTML boilerplate
- English source name در badge

### Source of Truth جدید

Public Hero اول داده فارسی تاییدشده Windows را می‌گیرد:

1. dedicated Slider Persian SEO
2. AI Slider Persian SEO
3. Product SEO فارسی Windows
4. Product editorial فارسی Windows/Imported Asset
5. Persian Product fallback
6. Persian generic sales fallback

Raw source English title/description fallback عمومی نیست.

### Sanitizer

`store/phase49_persian_sales_copy.py`

- HTML/BR/script/style cleanup
- Persian validation
- Cookie/Privacy/Tracking blacklist
- shared Slider/Product sales resolver
- sales-intent keyword normalization

### SEO فروش

Focus Keyword اگر intent تراکنشی نداشته باشد تبدیل می‌شود:

`آباژور سه بعدی` → `خرید آباژور سه بعدی`

Intentهای پذیرفته‌شده:

- خرید
- سفارش
- قیمت
- فروش
- تهیه
- ثبت سفارش

Product meta/OG و Slider alt/focus نیز از قرارداد فارسی فروش استفاده می‌کنند.

### Profile global save gate

`store/phase49_persian_sales_runtime.py`

`ProductCatalogProfile` قبل از Save normalize می‌شود، مستقل از اینکه ورودی از:

- Windows import
- Bridge
- Admin
- Hero mirror

آمده باشد.

### Public Hero runtime

`website/phase49_persian_sales_hero.py`

فارسی‌بودن را روی:

- title
- description
- group/badge
- alt
- button

enforce می‌کند.

### Windows runtime

`catalog_center/app/phase49_persian_sales_desktop.py`

- source_title/source_description raw fallback نیستند.
- reload/save Slider fields را فارسی normalize می‌کند.
- launcher و portable هر دو Patch را نصب می‌کنند.
- Marker: `EPIC49_PERSIAN_SALES_HERO=ENABLED`.

### Hero description UX

Default:

- حداکثر 2 خط
- ellipsis
- `نمایش بیشتر`

On click:

- full description
- `بستن توضیحات`
- aria-expanded
- autoplay pause while reading

Slide change state را reset می‌کند.

Files:

- `templates/website/partials/hero.html`
- `static/css/phase49_2c-hero-effects.css`
- `static/js/phase49_2c-home-hero.js`

## 13) Legacy data repair

Command:

`python manage.py phase49_repair_persian_sales_hero`

Default: **DRY_RUN**

Apply فقط بعد از Review/Backup:

`python manage.py phase49_repair_persian_sales_hero --apply`

قابل ترمیم:

- Hero title/description/group/alt/button
- Profile slider title/description/alt/button/focus

Command Product/Image/Price را حذف/تغییر ساختاری نمی‌دهد.

این Hotfix Migration جدید ندارد.

## 14) تست‌های Persian Sales Hero

Server:

`website.test_phase49_persian_sales_hero`

Exact regression input دارد:

- Vesper English title
- Cookie Settings/Consent/Tracking HTML

Windows:

`catalog_center/tests/test_phase49_persian_sales_slider.py`

E2E:

`store.test_phase49_unified_import_e2e`

Batch E2E دارای Slider SEO فارسی مستقل + sales focus + image/effect/timing/revision است.

## 15) خطاهای مهمی که CI گرفت و علت رفع

1. Product title قبل از `asset.persian_title` fallback می‌شد → Windows/Imported Persian precedence اصلاح شد.
2. focus عمومی مثل `چراغ دکوراتیو` intent فروش نداشت → `خرید چراغ دکوراتیو` شد.
3. Bridge test fixtures انگلیسی بودند → fixture فارسی شد؛ Revision/409 contract ثابت ماند.
4. E2E test focus عمومی بود → Batch E2E به SEO فروش واقعی ارتقا یافت.
5. دو Full Suite contract قدیمی انتظار `آباژور سه بعدی` داشتند → expectation به `خرید آباژور سه بعدی` ارتقا یافت؛ Runtime عقب‌گرد نکرد.

## 16) وضعیت برند و Frontend

Canonical public brand:

`static/img/brand/3dprinthublogo.png`

Approved SHA256:

`97ec202678e386387fa9ebe2c6055fa45967d1f341d40dbc5f2d9e980b873cec`

Legacy favicon pack حذف نشده ولی Source of Truth برند نیست مگر دوباره از canonical logo تأییدشده تولید/verify شود.

## 17) Gate بعدی Local

1. Pull آخرین `epic/phase49-unified-product-slider-sync`.
2. Verify clean worktree.
3. `python manage.py check`.
4. `python manage.py makemigrations --check --dry-run` → No changes detected.
5. targeted Persian Hero + Windows tests.
6. `python manage.py phase49_repair_persian_sales_hero` → Dry Run.
7. Review affected Hero/Profile rows.
8. Local DB backup.
9. Apply repair only after output accepted.
10. Restart runserver + Ctrl+Shift+R.
11. Visual QA: Persian title/badge/description/alt behavior, no Cookie/HTML, 2-line ellipsis, click expand/collapse.
12. User explicit approval.
13. Only then prepare Production backup/migration/deploy plan.

## 18) Production status

**NOT DEPLOYED / NOT APPROVED YET.**

هیچ Migration/Repair/collectstatic/restart مربوط به Epic49 Unified یا Persian Sales Hero Hotfix روی Production از این مسیر انجام نشده است.
