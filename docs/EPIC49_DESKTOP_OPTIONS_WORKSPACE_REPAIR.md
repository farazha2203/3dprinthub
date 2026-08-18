# Epic49 — Desktop Product Options + Workspace Routing Repair

## وضعیت

- Branch: `epic/phase49-unified-product-slider-sync`
- هدف: یکسان‌کردن Workspace واقعی Windows با Epic49 نهایی و اضافه‌کردن انتخاب مستقل متریال/رنگ با پشتیبانی رنگ‌های خاص.
- Production: **هنوز Deploy نشده**.
- نتیجه CI نهایی: **SUCCESS**
  - Run: `32158432992`
  - Job: `95781188545`

## 1. مسئله واقعی که روی Windows دیده شد

در اسکرین‌شات کاربر Catalog Center نسخه 8.7.1 باز بود، اما Product Workspace هنوز UI قدیمی را نشان می‌داد:

- دکمه مبهم `انتشار روی سایت`
- Slider فقط enable/image/sort داشت
- بخش کامل SEO اختصاصی Hero دیده نمی‌شد
- `🧪 انتشار آزمایشی روی کامپیوتر` دیده نمی‌شد
- `🌐 انتشار واقعی روی سایت اصلی` دیده نمی‌شد
- متریال/رنگ هنوز Picker قدیمی ترکیبی بود.

### علت

`catalog_center/launch.py` کلاس نهایی `app.product_workspace_epic49.ProductWorkspace` را import می‌کرد، اما `catalog_center/app/ux87_shell.py` هنگام import خودش این alias قدیمی را نگه می‌داشت:

```python
from .product_workspace_v87 import ProductWorkspace
```

و `open_product_studio()` همان alias را instantiate می‌کرد. بنابراین داشبورد 8.7.1 فعال بود ولی بازکردن محصول به Workspace قدیمی 8.7 می‌رفت.

### رفع

در Launcher نهایی بعد از نصب Patchهای Epic:

```python
ux87_shell.ProductWorkspace = ProductWorkspace
```

ست می‌شود.

پس دوبارکلیک محصول، «ویرایش محصول» و callbackهای UX87 همگی همان Workspace نهایی Epic49 را باز می‌کنند.

Marker تشخیصی:

```text
UX87_EPIC49_WORKSPACE_ROUTING=ENABLED
```

## 2. UI متریال

متریال دیگر Pair اجباری متریال/رنگ نیست. اپراتور متریال‌ها را مستقل تیک می‌زند.

Default catalog:

- PLA
- PLA-CF
- HT-PLA-GF
- PETG
- PET-CF
- PETG-rCF08
- ABS
- ASA
- PC-FR
- TPU95
- PA6-CF20
- PA12-CF10
- PPS-CF10

فیلد Windows SQLite:

```text
material_options_json
```

## 3. UI رنگ

رنگ‌ها نیز مستقل تیک می‌خورند.

نوع‌های رنگ:

- `solid` — ساده
- `transparent` — شفاف / شیشه‌ای
- `translucent` — نیمه‌شفاف
- `metallic` — متالیک
- `silk` — Silk / ابریشمی
- `dual` — دو رنگ
- `multicolor` — چند رنگ
- `gradient` — گرادیانی

برای هر رنگ قابل ثبت است:

- نام رنگ
- HEX اصلی
- HEX دوم
- HEX سوم
- نوع رنگ

دکمه:

```text
＋ تعریف رنگ جدید
```

اگر چند متریال تیک خورده باشند، رنگ جدید برای همه همان متریال‌ها در inventory محلی تعریف می‌شود.

فیلد Windows SQLite:

```text
color_options_json
```

## 4. Backward Compatibility

فیلد قدیمی حذف نشده:

```text
material_color_options_json
```

هنگام Save، Windows از متریال‌ها و رنگ‌های مستقل یک payload سازگار pair می‌سازد. Server نیز اگر `material_options_json + color_options_json` وجود داشته باشند Pairهای Variant را از cross-product می‌سازد؛ اگر وجود نداشتند فرمت legacy را مصرف می‌کند.

هیچ داده قدیمی حذف نمی‌شود.

## 5. Windows SQLite schema

فایل:

```text
catalog_center/app/epic49_desktop_schema.py
```

تغییرات Additive:

### products

- `material_options_json`
- `color_options_json`
- `material_color_options_json` حفظ شده

### available_material_colors

- `color_type`
- `secondary_hex`
- `tertiary_hex`

Upgrade با `ALTER TABLE ADD COLUMN` فقط برای ستون غایب انجام می‌شود.

## 6. Django DB

Migration جدید:

```text
store.0031_phase49_rich_material_colors
```

Dependency:

```text
store.0030_phase49_unified_sync_contract
```

روی `MaterialColorOption` اضافه می‌شود:

- `color_type`
- `secondary_hex`
- `tertiary_hex`

`hex_code` باقی می‌ماند.

Migration فقط Additive است؛ DROP/DELETE/TRUNCATE ندارد.

## 7. Server Import / Variant Contract

فایل:

```text
store/epic49_publish_options.py
```

Server ابتدا قرارداد جدید را بررسی می‌کند:

```text
material_options_json
color_options_json
```

سپس Variantهای سازگار می‌سازد و metadata رنگ را روی `MaterialColorOption` نگه می‌دارد.

فرمت قدیمی `material_color_options_json` همچنان پشتیبانی می‌شود.

## 8. Django Admin

`MaterialColorOptionAdmin` اکنون این موارد را نمایش/ویرایش می‌کند:

- متریال
- نام رنگ
- نوع رنگ
- HEX اصلی/دوم/سوم
- قیمت اختصاصی هر گرم
- موجودی
- فعال/غیرفعال

برای رنگ دو/چند/گرادیانی Preview به‌صورت swatch گرادیانی نمایش داده می‌شود.

## 9. ارتباط با Slider SEO و Dual Publish

با Routing repair، Product Workspace واقعی اکنون همان کلاسی است که این Patchها روی آن نصب می‌شوند:

- Persian Sales Hero
- Slider SEO 8.7.1
- Effect/Timing
- Dual Publish Targets
- Material/Color Picker

Markerها:

```text
HOMEPAGE_SLIDER_SEO_V871=ENABLED
EPIC49_DUAL_PUBLISH_TARGETS=ENABLED
EPIC49_LOCAL_PUBLISH_SQLITE_GUARD=ENABLED
EPIC49_MATERIAL_COLOR_PICKER=ENABLED
UX87_EPIC49_WORKSPACE_ROUTING=ENABLED
```

## 10. آیکون‌ها / UI

Windows/Tkinter dependency جدید نصب نشده است. UI با همان ttk/Workspace موجود ساخته شده.

نمادهای عملیاتی:

- `🧪` انتشار Local
- `🌐` انتشار Production
- `＋` تعریف رنگ
- `↻` تازه‌سازی
- Checkbox برای Material/Color

Django Admin از همان Master/Remix Icon contract موجود استفاده می‌کند؛ کتابخانه جدید اضافه نشده است.

## 11. تست‌ها

Windows:

```text
catalog_center/tests/test_epic49_material_color_picker.py
catalog_center/tests/test_epic49_studio_final.py
```

Django:

```text
store/test_phase49_rich_material_colors.py
store/test_epic49_operator_publish.py
```

CI نهایی:

```text
Run 32158432992
Job 95781188545
```

Gateها:

- Compile: ✅
- Django check/migration contract: ✅
- Phase49 targeted behavioral/regression: ✅
- Windows Catalog Center tests: ✅
- Full Django suite: ✅

## 12. خطاهای CI و رفع

### Run اول

تست legacy فقط `{material,color,hex}` را انتظار داشت.

رفع: تست به metadata جدید `color_type/secondary_hex/tertiary_hex` ارتقا یافت؛ Runtime عقب‌گرد نکرد.

### Run دوم

Windows legacy contract دنبال literal `app.ux87_shell` بود، درحالی‌که Launcher واقعی `from app import ux87_shell` داشت.

رفع: تست سخت‌گیرتر شد و اکنون خود Routing واقعی زیر را الزام می‌کند:

```python
ux87_shell.ProductWorkspace = ProductWorkspace
```

### Run سوم

تمام Gateها سبز شدند.

## 13. Gate Local بعدی

1. Pull آخرین Epic روی Windows.
2. Backup SQLite Django + Catalog Center data.
3. `python manage.py check`
4. `python manage.py makemigrations --check --dry-run`
5. `python manage.py migrate --plan`
6. اگر فقط migration مورد انتظار pending بود: `python manage.py migrate store 0031`
7. تست Django rich colors.
8. تست Windows routing/picker.
9. `python launch.py --verify-only`
10. بازکردن واقعی Product Workspace.
11. Visual QA: Slider SEO + Dual Publish + Material/Color checkboxes.
12. یک Product واقعی → تولید محتوای فارسی → انتخاب Hero → Local Publish.
13. تأیید Store/Hero/Admin روی `127.0.0.1`.
14. فقط بعد از تأیید صریح کاربر Production.

## 14. Rollback

قبل از migration Local/Production از DB backup گرفته می‌شود.

برای کد، برگشت به Commit قبل از این subphase Workspace را به قرارداد قبلی برمی‌گرداند. Migration 0031 داده قبلی را حذف نمی‌کند؛ در Rollback Production از DB backup استفاده می‌شود و migration reverse بدون برنامه Backup انجام نمی‌شود.
