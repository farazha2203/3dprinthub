# Epic49 — Dual Publish Targets (Local Test / Production)

## وضعیت

- Branch: `epic/phase49-unified-product-slider-sync`
- Scope: Windows Catalog Center 8.7.1 / Epic49 Unified
- Migration: **NONE**
- Production deployment: **NOT DEPLOYED**
- Local real-data E2E: **PENDING USER WINDOWS QA**
- GitHub Actions self-test:
  - Run: `32152308954`
  - Job: `95760929653`
  - Result: **SUCCESS**

تمام Gateهای Compile، Django check/migration contract، Phase49 regression، Windows tests و Full Django Suite سبز شده‌اند.

---

## هدف

در Product Workspace مقصد انتشار باید برای کارمند/مدیر کاملاً صریح و اشتباه‌ناپذیر باشد:

```text
🧪 انتشار آزمایشی روی کامپیوتر
    ↓
Standard v8.5 Batch
    ↓
Django Local Import
    ↓
D:\projects\3DPrintHub\db.sqlite3
```

و مستقل از آن:

```text
🌐 انتشار واقعی روی سایت اصلی
    ↓
Standard v8.5 Batch
    ↓
FTP
    ↓
Catalog Bridge
    ↓
Production Django / Store / Hero
```

هیچ Batch format موازی ساخته نشده است. هر دو مسیر همان Batch رسمی 8.5 را استفاده می‌کنند.

---

## UI / آیکون‌ها

Dependency آیکون یا UI جدید نصب نشده است.

### دکمه Local

`🧪 انتشار آزمایشی روی کامپیوتر`

کارکرد:

- فقط برای محیط Source/Developer.
- Product Workspace همان checklist واقعی انتشار را اجرا می‌کند.
- Batch رسمی 8.5 برای همان Product ساخته می‌شود.
- هیچ FTP اجرا نمی‌شود.
- هیچ HTTP request به Catalog Bridge اجرا نمی‌شود.
- Importer رسمی Django مستقیماً روی Local اجرا می‌شود.

### دکمه Production

`🌐 انتشار واقعی روی سایت اصلی`

کارکرد:

- مسیر واقعی فعلی FTP + Catalog Bridge را حفظ می‌کند.
- دامنه/URL مقصد در UI نمایش داده می‌شود.
- دو Confirmation مستقل دارد:
  1. نمایش URL واقعی و هشدار تغییر Production.
  2. تأیید نهایی Product ID + host و عبارت صریح «این Local Test نیست».

### دکمه‌های Legacy

هر کنترل قدیمی با متن:

`🚀 ارسال همین محصول`

در Workspace نهایی به متن Production واضح تبدیل می‌شود تا مقصد مبهم نباشد.

---

## فایل‌های پیاده‌سازی

### Local runtime

`catalog_center/app/epic49_local_publish.py`

وظایف:

- resolve کردن Repository Local.
- verify کردن `manage.py`.
- بررسی دیتابیس Django قبل از Import.
- اجرای Importer رسمی v8.5.
- parse کردن `CATALOG_ACK_JSON`.
- reject کردن import ناقص/failed.

### Windows UI patch

`catalog_center/app/phase49_dual_publish_desktop.py`

وظایف:

- اضافه‌کردن دو مقصد واضح Local / Production.
- rename کردن Legacy publish controls.
- Local publish workflow.
- Production double confirmation.
- sync receiptهای Local.
- جلوگیری از ترکیب Local IDs با Production state.

### Launcher

`catalog_center/launch.py`

Markerهای جدید:

- `EPIC49_DUAL_PUBLISH_TARGETS=ENABLED`
- `EPIC49_LOCAL_PUBLISH_SQLITE_GUARD=ENABLED`

---

## Local SQLite Safety Gate

قبل از Import، دکمه Local یک Preflight واقعی با همان Python Runtime اجرا می‌کند:

```text
python manage.py shell -c <DB probe>
```

و دو Marker را می‌خواند:

- `EPIC49_LOCAL_DB_VENDOR`
- `EPIC49_LOCAL_DB_NAME`

شرایط لازم:

1. vendor باید دقیقاً `sqlite` باشد.
2. database file باید دقیقاً Local DB مورد انتظار باشد:

`D:\projects\3DPrintHub\db.sqlite3`

اگر Environment به MySQL/Production یا یک SQLite دیگر اشاره کند:

`LOCAL PUBLISH BLOCKED`

پس دکمه Local نمی‌تواند به‌طور اتفاقی Production DB را هدف بگیرد.

Environment overrideهای توسعه‌ای فقط در صورت نیاز:

- `CATALOG_LOCAL_DJANGO_ROOT`
- `CATALOG_LOCAL_DJANGO_DB`
- `CATALOG_LOCAL_SITE_URL`

Default Local URL:

`http://127.0.0.1:8000`

---

## Import Local

دکمه Local همان Command رسمی Server را اجرا می‌کند:

```text
python manage.py phase37_import_catalog_center <batch> --continue-on-error
```

پس تست Local همان مسیر واقعی زیر را پوشش می‌دهد:

```text
Windows editorial data
→ v8.5 batch
→ ImportedPrintAsset
→ ImportedPrintAssetImage
→ Product (when publish gates pass)
→ ProductCatalogProfile
→ HomepageHeroSlide
→ Store/Home
```

این مسیر Mock یا Importer جایگزین ندارد.

---

## Publication gates حفظ‌شده

قبل از هر دو مقصد، Product Studio همان Gateهای قبلی را بررسی می‌کند:

- selected image
- primary image
- Persian title
- Persian description
- valid site category
- price/order mode
- commercial license allowed
- duplicate protection
- approved for sale

Local Test Gateها را دور نمی‌زند.

---

## Local ACK و Production State Isolation

Local Import ACK برای QA خوانده می‌شود، اما Local IDs نباید در فیلدهای Production Windows ذخیره شوند.

پس بعد از Local import:

- `server_id` تولیدی overwrite نمی‌شود.
- `server_product_revision` تولیدی overwrite نمی‌شود.
- `server_slider_revision` تولیدی overwrite نمی‌شود.
- Product Windows به حالت `approved + upload_ready=1` بازمی‌گردد تا بعداً جداگانه با دکمه Production منتشر شود.

Receipt statusهای Local:

- `desktop_local_batch_ready`
- `desktop_local_imported`
- `desktop_local_import_review`
- `desktop_local_import_failed`

Receiptها `target=local_django` دارند و با Production receipts قابل تفکیک هستند.

---

## Production path

Production button از مسیر موجود استفاده می‌کند:

```text
self.app.publish_product_now(product_id)
```

و سپس:

```text
build_batch
→ upload_last_batch
→ FTP upload
→ Catalog Bridge import
→ public HTTP verification
→ ACK
```

این Hotfix منطق FTP/Bridge قدیمی را Fork نکرده است.

---

## Portable / Employee build policy

Local publish helper اگر `sys.frozen` باشد اجرای Local را Block می‌کند.

هدف معماری:

- Developer source build: Local + Production.
- Employee Portable EXE: Production operational path؛ Local Test فقط ابزار توسعه است.

**نکته وضعیت فعلی:** `portable_entry.py` هنوز برای UI جدید Dual Publish نهایی/Build نشده است. Portable employee release باید فقط بعد از QA واقعی Local روی Windows همسان‌سازی، build و verify شود. تا آن زمان ادعا نمی‌شود که EXE کارمندان این UI جدید را دارد.

---

## دیتابیس

این تغییر **هیچ Migration جدیدی ندارد**.

- Django schema: بدون تغییر.
- Windows SQLite schema: بدون تغییر جدید برای Dual Publish.
- Production DB: دست‌نخورده.

Migrationهای قبلی Epic همچنان:

- `store.0030_phase49_unified_sync_contract`
- `website.0021_phase49_unified_hero_sync`

هستند.

---

## تست‌ها

فایل:

`catalog_center/tests/test_epic49_dual_publish.py`

موارد قفل‌شده:

1. Local preflight فقط SQLite مورد انتظار را قبول می‌کند.
2. MySQL را Block می‌کند.
3. SQLite غیرمنتظره را Block می‌کند.
4. Frozen/Portable runtime را برای Local Block می‌کند.
5. Local import فقط از `phase37_import_catalog_center` استفاده می‌کند.
6. Local helper dependency به FTP/Bridge uploader ندارد.
7. UI هر دو مقصد را به‌صورت صریح دارد.
8. Production دو Confirmation دارد.
9. Production همچنان `publish_product_now` رسمی را استفاده می‌کند.
10. Launcher Markerهای Dual Publish را اعلام می‌کند.

### CI

Run: `32152308954`

Job: `95760929653`

Result: **SUCCESS**

Gateها:

- Compile changed Python surfaces ✅
- Django checks/migration contract ✅
- Phase49 unified behavioral/regression ✅
- Windows Catalog Center tests ✅
- Full Django suite ✅

---

## Rollback

Dual Publish additive است.

Rollback کدی:

- remove نصب `phase49_dual_publish_desktop.install` از Launcher.
- Workspace قبلی Epic/Persian Sales بدون تغییر ساختاری باقی می‌ماند.

هیچ DB rollback/migration لازم نیست.

---

## Gate بعدی

1. Pull آخرین Epic روی `D:\projects\3DPrintHub`.
2. `launch.py --verify-only`.
3. اجرای Catalog Center Source/Developer.
4. انتخاب یک Product واقعی.
5. تولید/بازبینی Product SEO فارسی.
6. تولید/بازبینی Slider SEO فارسی مستقل.
7. انتخاب Slider image + effect/timing.
8. کلیک فقط روی `🧪 انتشار آزمایشی روی کامپیوتر`.
9. Verify Product/Profile/Hero روی `127.0.0.1:8000`.
10. Visual QA و Data QA.
11. تا قبل از تأیید User، دکمه Production استفاده نشود.
12. بعد از Local acceptance: Portable employee build alignment و سپس Production deployment plan.
