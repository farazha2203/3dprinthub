# Epic 49 — Unified Product / SEO / Slider / Desktop / Bridge

## وضعیت

- Branch: `epic/phase49-unified-product-slider-sync`
- Code validation baseline: `8ad84577498072cf8c3d007d8bd259d6e3428cba`
- Final CI probe commit: `03b9df7c8f5a7ce8e8ad44b916cd626cc419818d`
- Final GitHub Actions run: `32129944811`
- Final GitHub Actions job: `95688635543`
- Final result: **SUCCESS**
- Production deployment: **NOT DEPLOYED**
- Windows local migration/visual acceptance: **PENDING**

این Epic زنجیره خطی Phase49 را روی `49.2A -> 49.2B -> 49.2C` یکپارچه می‌کند. Branchهای قبلی Merge موازی نشده‌اند؛ `phase49-2c` به‌صورت خطی شامل Foundations قبلی بود و Epic از همان HEAD ساخته شد تا Conflict مصنوعی ایجاد نشود.

---

## هدف کسب‌وکاری و Source of Truth

مدل عملیاتی مورد تأیید پروژه:

```text
کارمند
  ↓
Catalog Center ویندوز
  ↓
Product + Images + Product SEO + Hero SEO + Hero image + Effect/Timing
  ↓
Catalog Bridge (Bearer token)
  ↓
Django / Store / ProductCatalogProfile / HomepageHeroSlide
  ↓
سایت
```

و مسیر برگشت:

```text
Django Admin / Server
  ↓
Catalog Bridge read/update API
  ↓
Catalog Center Windows
```

**Windows ابزار اصلی کارمندهاست.** Django Admin ابزار مدیریتی دوم و کامل باقی می‌ماند. هیچ‌کدام دیتابیس یا مدل موازی جدا ندارند؛ هر دو یک قرارداد واحد را ویرایش می‌کنند.

۴۵ `ImportedPrintAsset` قدیمی موجود در SQLite توسعه که `Product=0` داشتند عمداً به Product تبدیل نشدند. این Epic آن داده‌های تاریخی/مرجع را به زور Publish نمی‌کند. Product باید از مسیر رسمی Windows Publish ساخته شود و Gateهای مجوز/تأیید/تصویر/دسته حفظ می‌شوند.

---

## SEO عمومی Product و SEO مستقل Hero

هر کالا دو مجموعه محتوای SEO دارد.

### Product SEO

- title / title_en
- short/full description
- meta title
- meta description
- focus keyword
- OG title / description
- tags / keywords / hashtags
- altهای عمومی تصاویر
- source attribution / editorial source

### Hero Slider SEO — مستقل از Product SEO

- `homepage_slider_title_fa`
- `homepage_slider_description_fa`
- `homepage_slider_alt_text`
- `homepage_slider_button_text`
- `homepage_slider_focus_keyword`
- تصویر انتخاب‌شده Hero
- ترتیب
- Effect
- Transition duration
- Display duration

Catalog Center 8.7.1 از قبل AI Pack مستقل `homepage_slider_seo` داشت و Epic همان قرارداد را حفظ/تکمیل می‌کند. اگر SEO اختصاصی Slider وجود داشته باشد همان اولویت دارد و فقط در حالت خالی از Product SEO fallback استفاده می‌شود.

---

## UI و آیکون‌ها

### Windows Catalog Center

Dependency گرافیکی جدید نصب نشده است. مسیر کاری موجود 8.7.1 حفظ شده و Epic به‌صورت Subclass روی آن قرار گرفته است.

نشانه‌های UI:

- 📦 Product
- 🖼 Images / Gallery
- 🔎 SEO
- 🎬 Homepage Slider
- ✨ AI content / Slider SEO
- 🌐 Server sync / Server slider manager
- ✅ Publish
- ⚠ Conflict / stale revision
- ↻ Refresh from server

در Product Workspace:

- انتخاب تصویری Hero از Gallery موجود
- عنوان/توضیح/Alt/Button/Focus Keyword اختصاصی Slider
- Effect selector
- Transition duration
- Display duration
- Server Product revision
- Server Hero revision
- `▶ پیش‌نمایش افکت` با تصاویر Local واقعی و Pillow
- `↻ دریافت نسخه فعلی این کالا از سایت`
- `🌐 مدیریت همه اسلایدرهای سایت`

فایل نهایی Workspace:

`catalog_center/app/product_workspace_epic49.py`

این کلاس از `ProductWorkspace871` ارث می‌برد و V87/V871 را جایگزین یا Fork نمی‌کند.

### Server Slider Manager در Windows

فایل:

`catalog_center/app/epic49_server_slider_manager.py`

قابلیت‌ها:

- دریافت تمام Sliderهای سایت
- ویرایش title/description/alt/focus/button
- انتخاب عکس فقط از Asset همان Product
- Effect / Transition / Display / Sort / Active
- نمایش Revision / last_modified_source / last_modified_by
- Save مستقیم روی Site از Bridge
- HTTP 409 → نمایش هشدار + بارگذاری نسخه جدید Server

### Django Admin

Master/Velzon و Remix Icons قبلی حفظ شده‌اند؛ کتابخانه UI جدید اضافه نشده است.

Hero Studio 49.2C همچنان شامل:

- Album Product Picker
- Image Album Picker
- Preview
- Edit existing slides
- Transition/Timing

Epic اضافه می‌کند:

- Revision/source/actor audit
- mirror بین Hero Admin و ProductCatalogProfile Admin
- تمام Slider SEO / Effect / Timing در ProductCatalogProfile Admin

---

## افکت‌های سینمایی

کدهای ثابت مشترک Windows/Server:

1. `cinematic_fade`
2. `wedding_dissolve`
3. `cinematic_zoom`
4. `ken_burns`
5. `soft_blur`
6. `cinematic_reveal`

Limits:

- Transition: 300..4000 ms
- Display: 2000..30000 ms
- Defaults: 1400 / 7000 ms

Frontend Hero 49.2C همچنان reduced-motion و mobile-safe fallback دارد.

---

## دیتابیس Django

### Migration Store

`store/migrations/0030_phase49_unified_sync_contract.py`

فقط AddField دارد و هیچ DROP/DELETE/TRUNCATE ندارد.

روی `ProductCatalogProfile` اضافه می‌کند:

- `homepage_slider_title_fa`
- `homepage_slider_description_fa`
- `homepage_slider_alt_text`
- `homepage_slider_button_text`
- `homepage_slider_focus_keyword`
- `homepage_slider_transition_effect`
- `homepage_slider_transition_duration_ms`
- `homepage_slider_display_duration_ms`
- `sync_revision`
- `last_modified_source`
- `last_modified_by`

### Migration Website

`website/migrations/0021_phase49_unified_hero_sync.py`

روی `HomepageHeroSlide` اضافه می‌کند:

- `sync_revision`
- `last_modified_source`
- `last_modified_by`

همه Additive هستند.

---

## دیتابیس Windows

`catalog_center/app/epic49_desktop_schema.py`

Schema installer فقط ستون غایب را با `ALTER TABLE products ADD COLUMN` اضافه می‌کند و repeat-safe است.

فیلدهای جدید Epic:

- `homepage_slider_transition_effect`
- `homepage_slider_transition_duration_ms`
- `homepage_slider_display_duration_ms`
- `server_product_id`
- `server_product_revision`
- `server_slider_id`
- `server_slider_revision`
- `server_updated_at`
- `last_sync_conflict`

فیلدهای Slider SEO از قبل وجود داشتند و حفظ شدند.

هیچ دیتای SQLite قبلی rewrite/delete نمی‌شود.

---

## Catalog Bridge 1.3.0

Bridge قدیمی حذف یا Fork نشده است.

Runtime version:

- Version: `1.3.0`
- Publish contract: `epic49-unified-v1`
- Auth: همان `Authorization: Bearer <CATALOG_BRIDGE_TOKEN>`
- compare: `hmac.compare_digest`

مسیرهای قدیمی که حفظ شدند:

- `GET /api/catalog-bridge/v1/health/`
- `POST /api/catalog-bridge/v1/import/`
- `GET /api/catalog-bridge/v1/diagnostics/<batch_name>/`

مسیرهای جدید:

- `GET /api/catalog-bridge/v1/products/`
- `GET /api/catalog-bridge/v1/products/<id>/`
- `POST /api/catalog-bridge/v1/products/<id>/sync/`
- `GET /api/catalog-bridge/v1/hero-slides/`
- `GET /api/catalog-bridge/v1/hero-slides/<id>/`
- `POST /api/catalog-bridge/v1/hero-slides/<id>/sync/`

Write endpoints Allow-list دارند؛ `setattr` آزاد روی payload ندارند.

Hero image ID فقط وقتی قبول می‌شود که `ImportedPrintAssetImage.asset_id == slide.asset_id`. عکس متعلق به Product دیگر رد می‌شود.

---

## Revision و Conflict Protection

هر Product Profile و Hero مستقل Revision دارد.

مثال:

```text
Windows knows Product revision = 4
Server current revision = 4
→ update accepted
→ revision = 5
```

اگر Admin در سایت ویرایش کرده باشد:

```text
Windows = 4
Server = 5
→ HTTP 409 Conflict
→ current server payload returned
→ employee must refresh/review
```

Admin Product save نیز Revision Profile را افزایش می‌دهد؛ بنابراین تغییر انسانی مدیر با Publish قدیمی Windows بی‌صدا overwrite نمی‌شود.

`last_modified_source` شامل `desktop` / `admin` است و `last_modified_by` operator/user را نگه می‌دارد.

---

## Idempotency

Importer رسمی در یک Batch ممکن است Asset را چند بار Save کند و Signal انتشار چند بار اجرا شود. Epic این خطر را با Idempotency Key می‌بندد:

`batch_uuid + source_hash`

اگر همان Batch دوباره اجرا شود:

- Product revision بی‌دلیل بالا نمی‌رود.
- Hero revision فقط در صورت تغییر واقعی state بالا می‌رود.
- Product/Hero duplicate ساخته نمی‌شود.

Batch جدید با Revision صحیح یک Revision واقعی ایجاد می‌کند.

---

## Mirror بین Adminها

### Hero Admin → ProductCatalogProfile

روی Save:

- enabled
- image
- sort
- title
- description
- alt
- button
- effect
- transition duration
- display duration
- revision/source/actor

Mirror می‌شوند.

Focus Keyword در Profile باقی می‌ماند چون Hero model فیلد جداگانه ندارد.

### ProductCatalogProfile Admin → Hero

اگر Asset/Product وجود داشته باشد، Hero موجود به‌روزرسانی می‌شود. اگر Slider Enabled باشد و Hero وجود نداشته باشد، Hero ساخته می‌شود. عکس فقط از Imageهای همان Asset resolve می‌شود.

---

## Windows ↔ Server client

فایل:

`catalog_center/app/epic49_site_sync.py`

قابلیت‌ها:

- list/get/update Product
- list/get/update Hero
- `BridgeConflictError` ساختاریافته
- refresh editable server fields into Windows
- raw internet source URL/payload روی Windows overwrite نمی‌شود
- ACK revisions در SQLite جذب می‌شوند

Upload/FTP قدیمی دست‌نخورده است؛ این Client فقط Management API را اضافه می‌کند.

---

## ACK enrichment

فایل:

`catalog_bridge/ack_enrichment.py`

ACK Import حالا علاوه بر داده قدیمی برمی‌گرداند:

- `server_product_id`
- `product_revision`
- `slider_id`
- `slider_revision`
- `sync_contract=epic49-unified-v1`

Windows بعد از Publish این Revisionها را ذخیره می‌کند.

---

## برند و favicon

Source of Truth برند عمومی:

`static/img/brand/3dprinthublogo.png`

Home و Store هر دو برای icon/apple-touch مستقیم به همین canonical asset اشاره می‌کنند.

Legacy favicon pack در `static/favicon/` حذف نشده است، اما دیگر Source of Truth برند محسوب نمی‌شود؛ چون از روی Repository قابل اثبات نبود که بعد از تأیید لوگوی نهایی دوباره از canonical logo ساخته شده باشد.

---

## تست‌ها

### Django / Server

- `store.test_phase49_unified_sync`
- `store.test_phase49_unified_import_e2e`
- `store.test_epic49_operator_publish`
- `store.test_phase49_1_frontend_contract`
- `catalog_bridge.test_phase49_unified_bridge`
- `catalog_bridge.tests.test_epic49_contract`
- `website.test_phase49_2c_hero_studio`
- `website.test_phase49_2b_hero_login_hotfix`
- `website.test_phase45_homepage_hero`

### End-to-End

`store/test_phase49_unified_import_e2e.py` یک Batch واقعی Schema 8.5 + Tiny GIF می‌سازد و Command رسمی:

`phase37_import_catalog_center`

را اجرا می‌کند و بررسی می‌کند:

- Asset
- Product
- ProductCatalogProfile
- Product SEO
- Hero SEO
- exact ImportedPrintAssetImage relation
- Effect/Timing
- Revision
- re-import idempotency

### Windows

- `catalog_center/tests/test_phase49_unified_desktop.py`
- تمام `test_*epic49*.py`
- legacy workspace tests به inheritance contract واقعی ارتقا یافتند.

### Final CI

Workflow:

`.github/workflows/phase49-epic-ci.yml`

Final run:

- Run: `32129944811`
- Job: `95688635543`
- Result: **SUCCESS**

Gateها:

1. dependencies
2. isolated CI runtime directories
3. Python compile
4. Django `check`
5. `makemigrations --check --dry-run`
6. `migrate --plan`
7. targeted Phase49 behavioral/regression
8. Windows Epic49 tests
9. **Full Django test suite**

همه Success شدند.

---

## خطاهایی که در Self-Test پیدا و رفع شدند

### 1. Legacy Windows tests وابسته به نام فایل Workspace قدیمی

علت: تست به `product_workspace_v87` hard-code شده بود.

رفع: تست سخت‌گیرتر شد و inheritance واقعی را بررسی می‌کند:

`Epic49 -> V871 -> V87`

هیچ marker جعلی برای پاس‌شدن تست اضافه نشد.

### 2. Full Suite روی CI سعی می‌کرد در `/home/sfkilvrs/...` Media بنویسد

علت: default production `MEDIA_ROOT` در Runner.

رفع: فقط CI از `/tmp/3dprinthub-ci/...` استفاده می‌کند. `config/settings.py` Production تغییر نکرد.

### 3. Legacy Bridge test انتظار `1.2.0 / epic49-final`

رفع: Contract test به نسخه واقعی `1.3.0 / epic49-unified-v1` ارتقا یافت و علاوه بر آن حفظ routeهای قدیمی + routeهای جدید را بررسی می‌کند.

### 4. Legacy Hero test انتظار لینک مستقیم Product داخل Template

قدیمی:

`slide.asset.product.get_absolute_url`

Contract صحیح:

`{{ slide.target_url }}`

Runtime Product فعال را به `get_absolute_url()` و Product غیرفعال را به Store list می‌برد. External Catalog بازنشسته‌شده ممنوع است.

### 5. Legacy favicon test انتظار `favicon/favicon.ico`

برند تأییدشده جدید canonical است. Home/Store مستقیم `img/brand/3dprinthublogo.png` را استفاده می‌کنند؛ favicon قدیمی فقط Legacy pack است و حذف نشده.

---

## فایل‌های کلیدی Epic

Server:

- `store/epic49_catalog_profile.py`
- `store/phase49_unified_sync.py`
- `store/epic49_catalog_admin.py`
- `store/migrations/0030_phase49_unified_sync_contract.py`
- `website/phase49_unified_sync.py`
- `website/migrations/0021_phase49_unified_hero_sync.py`
- `catalog_bridge/unified_views.py`
- `catalog_bridge/ack_enrichment.py`
- `catalog_bridge/urls.py`
- `catalog_bridge/apps.py`

Windows:

- `catalog_center/app/epic49_desktop_schema.py`
- `catalog_center/app/epic49_site_sync.py`
- `catalog_center/app/epic49_server_slider_manager.py`
- `catalog_center/app/product_workspace_epic49.py`
- `catalog_center/launch.py`
- `catalog_center/portable_entry.py`

Tests:

- `store/test_phase49_unified_sync.py`
- `store/test_phase49_unified_import_e2e.py`
- `catalog_bridge/test_phase49_unified_bridge.py`
- `catalog_center/tests/test_phase49_unified_desktop.py`
- upgraded legacy contracts listed above.

---

## Windows install/update path — next gate

After explicit handoff, local Windows must:

1. verify clean worktree
2. fetch/switch Epic branch
3. make SQLite/data backups
4. `python manage.py check`
5. `python manage.py makemigrations --check --dry-run`
6. inspect `python manage.py migrate --plan`
7. apply only tracked migrations 0030/0021 and any already-tracked prerequisite if expected
8. run targeted tests
9. run Store/Website/Catalog Bridge/full suite
10. run Catalog Center verify/tests
11. visual QA Windows Product Workspace + Server Slider Manager + Admin + Home Hero
12. one real local E2E employee workflow
13. explicit approval

Only after that: production backup/deploy/migration/collectstatic/restart/smoke.

---

## Production gate

**Production is intentionally untouched.**

Before deployment:

- local Windows migration/tests green
- visual QA approved
- explicit user approval
- production MySQL backup
- media/private media backup strategy confirmed
- `migrate --plan` reviewed on host
- exact Epic commit recorded

No reset/drop/truncate is an acceptable deployment fix.
