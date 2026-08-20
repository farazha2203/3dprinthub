# 3DPrintHub — نقشه مادر پروژه، خواسته‌ها، معماری، خطاها و Guardهای جلوگیری از Regression

> **این فایل باید قبل از شروع هر فاز، Hotfix، تغییر UI، Migration، تغییر Sync یا Deploy خوانده شود.**
>
> هدف این سند این است که مسیر پروژه روشن بماند، کد تکراری و معماری موازی ساخته نشود، مشکلات حل‌شده دوباره برنگردند و هر تغییر فقط همان چیزی را که لازم است اصلاح کند بدون اینکه قابلیت‌های قبلی را از بین ببرد.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه جاری:** `epic/phase49-unified-product-slider-sync`  
**زبان اصلی پروژه:** Python / Django  
**ابزار اصلی اپراتور:** Windows Catalog Center  
**ابزار مدیریتی دوم:** Django Admin  
**Production:** تا عبور کامل Local QA و تأیید صریح کاربر ممنوع است.

---

## 1) قانون مادر تغییرات — Preserve Existing Behavior / Minimal Change

این قانون از این تاریخ برای تمام توسعه‌های بعدی الزام‌آور است:

1. **تغییر جدید نباید قابلیت قبلی سالم را حذف، Replace یا بی‌اثر کند مگر درخواست صریح کاربر وجود داشته باشد.**
2. اگر یک مسیر Mature از قبل وجود دارد، تغییر جدید باید آن را **Extend / Patch / Wrap** کند، نه اینکه یک مسیر موازی جدید بسازد.
3. برای رفع یک خطا، کل UI / Model / Sync / Admin بازنویسی نمی‌شود؛ Root Cause همان بخش اصلاح می‌شود.
4. اگر ارتباط بین دو بخش مشکل دارد، **Boundary/Contract/Sync** اصلاح می‌شود؛ کلیات معماری به هم ریخته نمی‌شود.
5. رفتار قبلی Default باقی می‌ماند مگر نیاز جدید دقیقاً Default جدید را طلب کند. نمونه: `pricing_strategy=legacy` برای کالاهای قدیمی به‌صورت پیش‌فرض حفظ شده است.
6. قبل از تغییر، باید مشخص شود:
   - دقیقاً چه چیزی باید تغییر کند؛
   - چه چیزهایی نباید تغییر کنند؛
   - کدام Contractها باید حفظ شوند؛
   - کدام تست‌ها از رفتار قبلی محافظت می‌کنند.
7. هر Bugfix باید Regression Test داشته باشد تا همان خطا دوباره برنگردد.
8. Migration ترجیحاً Additive است. حذف جدول/فیلد/داده فقط در فاز مستقل، Backup شده، مستند و با تأیید صریح مجاز است.
9. برای حل مشکل Deploy یا Migration، `reset --hard`، حذف DB، `DROP`, `TRUNCATE`, `DELETE FROM`, حذف media یا حذف `.env` راه‌حل محسوب نمی‌شود.
10. Source of Truth کد فقط GitHub است؛ Patch دستی روی Windows/Host مبنای پروژه نیست.

### قانون «همان تغییر، نه بیشتر»

هر Task باید یک Change Scope داشته باشد:

```text
Requested Delta: چه چیزی باید عوض شود
Touched Surfaces: فایل/مدل/رابط‌های لازم
Must-Not-Touch: قابلیت‌های سالم مرتبط که باید بدون تغییر بمانند
Regression Tests: تست‌هایی که اثبات می‌کنند قابلیت‌های قبلی حفظ شده‌اند
```

اگر برای یک تغییر کوچک نیاز به دست‌کاری گسترده دیده شد، ابتدا باید علت معماری آن ثابت شود؛ بازنویسی گسترده انتخاب پیش‌فرض نیست.

---

## 2) ترتیب Source of Truth هنگام اختلاف اطلاعات

در صورت اختلاف بین اسناد یا حافظه گفتگو، ترتیب اعتبار این است:

1. Migration state واقعی روی محیط موردنظر.
2. آخرین خروجی واقعی CI / Local Gate / Host Verification.
3. این فایل: `docs/00_PROJECT_MASTER_ROADMAP_FA.md`.
4. `PROJECT_CONTEXT.md`.
5. سند مخصوص آخرین Phase در `docs/`.
6. کد Runtime + تست‌های همان Feature.
7. اسناد تاریخی قدیمی‌تر.

اسناد مرجع مهم:

- `PROJECT_CONTEXT.md`
- `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`
- `docs/EPIC49_UNIFIED_PRODUCT_SLIDER_SYNC.md`
- `docs/PHASE49_3A_PRODUCT_PUBLISH_READINESS.md`
- `docs/PHASE49_3B_GUIDED_AI_HERO_DIAGNOSTICS.md`
- `docs/PHASE49_3D_WORKFLOW_HARDENING.md`
- `docs/PHASE49_3F_PRODUCT_INTELLIGENCE_PRICING_AI_UX.md`
- `deploy/phase48-deploy.sh`
- `deploy/phase49-deploy.sh`

---

## 3) خواسته‌ها و الزامات کاربر — دسته‌بندی‌شده

### 3.1) سیاست توسعه و تحویل

- توسعه فازبه‌فاز، قابل ردگیری و تست‌شده باشد.
- هر فاز ابتدا روی GitHub ثبت شود.
- سپس Windows از GitHub Pull کند.
- Local کامل تست شود.
- فقط بعد از تأیید صریح Local، Production به‌روزرسانی شود.
- تمام تغییرات، علت، مسیر نصب، خطا، روش رفع خطا، DB و وضعیت پروژه در GitHub مستند شوند.
- هر قسمت تکمیل‌شده در سند فاز تیک بخورد.
- اگر یک مرحله خطا داد، Root Cause کامل رفع شود و مسیر نصفه رها نشود.
- فایل/اسکریپت جدا از GitHub Source of Truth نباشد.

### 3.2) اصل حفظ قابلیت‌های قبلی

- پنل‌ها و قابلیت‌های سالم قبلی حفظ شوند.
- تغییر جدید فقط همان قسمت درخواستی را تغییر دهد.
- ارتباط بین ماژول‌ها اصلاح شود بدون ایجاد معماری موازی.
- UI Mature موجود در صورت امکان Extend شود.
- مدل/DB قدیمی بدون دلیل Reset نشود.
- داده‌های واقعی کاربر، تصاویر، media و تنظیمات از بین نروند.

### 3.3) Product Workspace / Wizard

مدل کاری هدف:

1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

خواسته‌ها:
- مراحل واضح و قابل حرکت باشند.
- Requiredها ستاره‌دار و وضعیت کامل/ناقص مشخص باشد.
- Previous / Next وجود داشته باشد.
- اپراتور دلیل Publish Block را دقیق ببیند.
- Local Publish همیشه قابل تشخیص از Production Publish باشد.
- Production Publish بدون Readiness واقعی اجرا نشود.

### 3.4) AI Provider Hub

Providerهای موردنیاز:

- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

الزامات:
- هر Provider کارت/تنظیم مستقل داشته باشد.
- Provider و Model فعال واضح باشد.
- Search مدل، Free filter در صورت پشتیبانی و Model count وجود داشته باشد.
- فقط raw model ID ذخیره شود؛ Label نمایشی نباید به‌جای ID ذخیره شود.
- اعتبار/Balance فقط وقتی نمایش داده شود که API واقعی Provider آن را پشتیبانی می‌کند.
- هزینه هر Request در صورت امکان ذخیره شود؛ Toman/IRT از داده واقعی Provider یا نرخ تبدیل تنظیم‌شده محاسبه شود، نه عدد ساختگی.
- API Key/Management Key/Admin Key داخل Git/SQLite/Diagnostic export ثبت نشود.
- Test Connection دقیقاً Provider/Model فعال را تست کند.
- خطای AvalAI برای `response_format` با fallback کنترل‌شده مدیریت شود.

### 3.5) AI Diagnostics / Logging

لاگ باید قابل عیب‌یابی باشد و شامل اطلاعات زیر شود:

- Operator
- Workstation
- Session
- Product
- Provider
- Model
- Operation
- Endpoint/Request ID در صورت وجود
- HTTP status
- Duration
- Token/cost در صورت وجود
- فایل/ماژول/Action
- Success/Failure
- Error sanitized

اما Secret هرگز نباید وارد Log شود.

### 3.6) تصاویر و Image SEO

- AI فقط برای عکس‌های انتخاب‌شده همان محصول کار کند.
- عکس Binary، URL عکس یا فایل تصویر به AI فرستاده نشود؛ AI فقط ورودی Text/Facts بگیرد.
- Mapping بین Image slot و URL/File فقط Local باشد.
- Metadata عکس‌های انتخاب‌نشده دست‌نخورده بماند.
- Exact image identity استفاده شود و index guessing ممنوع باشد.
- انتخاب تعداد دانلود تصویر per-product حفظ شود.
- Hard cap فعلی 10 تصویر حفظ شود مگر تغییر صریح درخواست شود.
- Filename/Alt/Metadata SEO انسانی و قابل ردگیری باشند.

### 3.7) محتوای فارسی و SEO

- English source نباید به‌عنوان Persian fallback وارد فیلد فارسی شود.
- عنوان، توضیح، SEO title/description و Alt فارسی معتبر باشند.
- AI حق جعل قیمت، مجوز، ابعاد، موجودی، متریال یا رنگ را ندارد.
- Product SEO و Hero/Slider SEO مستقل بمانند.
- خروجی عمومی سایت نباید کدهای داخلی مانند `ready_product` یا `made_to_order` را نمایش دهد.
- Source attribution داخلی مانند `Username` نباید به مشتری نمایش داده شود.
- Structured Data / JSON-LD نیز باید خروجی تمیز و حرفه‌ای داشته باشد؛ فقط ظاهر HTML کافی نیست.

### 3.8) Hero / Homepage Slider

- Hero Studio مستقل ولی متصل به همان Product باقی بماند.
- تصویر Hero فقط از تصاویر همان Product/Asset انتخاب شود.
- Desktop/Mobile preview وجود داشته باشد.
- `contain/cover`, focal, scale, X/Y, background, blur و ابعاد Desktop/Mobile قابل کنترل باشند.
- Default امن Product: `product_fit + contain`.
- Effect/Timing قبلی حفظ شود.
- تغییر Admin و Windows با Revision مستقل Sync شود.

### 3.9) قیمت‌گذاری

سه Strategy فعلی باید حفظ شوند:

- `legacy`: موتور قدیمی و رفتار کالاهای قبلی
- `fixed`: قیمت نهایی اپراتور
- `dynamic`: محاسبه واقعی

Dynamic باید از یک Source of Truth استفاده کند:

```text
chargeable_material_grams = part_weight + support_weight * support_multiplier
material_cost = chargeable_material_grams * material_sale_price_per_gram
machine_cost = print_hourly_rate * billable_minutes / 60
supervision_cost = supervision_hourly_rate * billable_minutes / 60
unit_price = material + machine + supervision + assembly + accessory + post + fixed + color adjustment
```

ارسال/بسته‌بندی/مالیات در Checkout جدا باقی می‌مانند.

مثال Acceptance ثابت:

```text
PLA = 2,600,000 تومان / kg = 2,600 تومان / g
Part = 100g
Support = 50g × 2
Chargeable = 200g
Material = 520,000
Print = 3h × 150,000 = 450,000
Supervision = 3h × 50,000 = 150,000
Total before extras/shipping = 1,120,000 تومان
```

قیمت Product Detail، Cart و Checkout نباید از سه فرمول مختلف بیاید.

---

## 4) پیشنهادهای معماری/کاری برای جلوگیری از کد بیهوده

این موارد پیشنهاد توسعه‌ای هستند و باید در فازهای بعد رعایت شوند:

### 4.1) یک Source of Truth برای هر Business Rule

مثال:
- Price → `ProductVariant.price_breakdown()` / cached finalized value
- Product/Hero Sync → همان Bridge contract موجود
- Readiness → همان readiness engine
- Secret → Secure credential/env registry

نباید یک فرمول مشابه در Template، یک فرمول دیگر در Cart و یک فرمول سوم در Importer ساخته شود.

### 4.2) Contract Test در Boundaryها

Boundaryهای حساس:

```text
Windows SQLite → Batch
Batch → Django Importer
Django Product/Profile → Hero
Django Admin → Bridge
Bridge → Windows
Product Detail → Cart → Checkout
AI Provider → Structured Result → Operator Apply
```

هر تغییر در یکی از این Boundaryها باید حداقل یک Contract/Regression Test داشته باشد.

### 4.3) Additive-first Schema

در فاز عادی:
- AddField / AddColumn / AddIndex ترجیح دارد.
- حذف یا Rename destructive در همان فاز Feature انجام نشود.
- Backfill حساس باید Dry Run + Backup داشته باشد.

### 4.4) Incident Ledger

هر خطای مهم باید در همین سند با این قالب اضافه شود:

```text
Symptom
Root Cause
Fix
Regression Test
Do Not Repeat
Status
```

### 4.5) Release Gate واقعی

هیچ Feature با «کد نوشته شد» تمام‌شده محسوب نمی‌شود. Definition of Done در بخش انتهای همین سند آمده است.

---

## 5) مسیر طی‌شده پروژه

زنجیره جاری:

```text
49.2A
→ 49.2B
→ 49.2C
→ Epic49 Unified
→ Persian Sales Hero
→ Dual Publish
→ Desktop Options
→ 49.3A Readiness
→ 49.3B Guided AI/Hero/Diagnostics
→ 49.3C Operator Workflow Recovery
→ 49.3C-1 Persian Content Integrity
→ 49.3D Workflow Hardening
→ 49.3D.1 Windows Runner Hotfix
→ 49.3E AI Task Completion & Recovery
→ 49.3F Product Intelligence / Pricing / AI UX
```

### خلاصه قابلیت‌های مهمی که نباید Regression شوند

- Windows Catalog Center ابزار اصلی اپراتور باقی مانده است.
- Django Admin ابزار مدیریتی دوم و کامل باقی مانده است.
- Product و Hero روی یک Unified Contract هستند.
- Product Revision و Hero Revision مستقل هستند.
- stale write با HTTP 409 Conflict محافظت می‌شود.
- `batch_uuid + source_hash` از duplicate/re-import بی‌دلیل جلوگیری می‌کند.
- Hero effect/timing و Persian sales content حفظ شده است.
- Material/Color options واقعی اپراتور حفظ شده‌اند.
- Readiness قبل از Publish وجود دارد.
- Local و Production Publish از هم جدا هستند.
- AI Provider Hub مستقل و قابل عیب‌یابی است.
- Image identity exact و metadata preservation وجود دارد.
- Persian Content Guard وجود دارد.
- Price range قدیمی و Dynamic pricing جدید باید همزمان سازگار بمانند.

---

## 6) معماری جاری — End-to-End

### مسیر اصلی اپراتور

```text
Employee
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite + Product Workspace
  ↓
Product / Images / SEO / Material / Color / Price / Hero
  ↓
Batch Builder
  ├─ Local Publish → Local Django SQLite
  └─ Production Publish → FTP/Bridge/Importer
                           ↓
                    Django Product
                    ProductCatalogProfile
                    HomepageHeroSlide
                           ↓
                    Store / Home / Cart / Checkout
```

### Reverse Sync

```text
Django Admin Edit
  ↓
Revision Increment
  ↓
Catalog Bridge
  ↓
Windows Refresh / Compare
```

اصل مهم: **مدل/Endpoint/DB موازی برای یک مفهوم موجود نسازیم.** اگر Sync ناقص است، همان Contract موجود Extend می‌شود.

---

## 7) ساختار Windows / Local

### مسیرها

```text
Project root:
D:\projects\3DPrintHub

Virtualenv:
D:\projects\3DPrintHub\.venv

Catalog Center source:
D:\projects\3DPrintHub\catalog_center

Django local DB:
D:\projects\3DPrintHub\db.sqlite3

Persistent Catalog data:
D:\projects\3dprinthub-catalog-manager

Legacy/persistent catalog area retained:
D:\projects\3dprinthub_catalog_center

Current Catalog DB used by Phase49.3F backup gate:
D:\projects\3dprinthub-catalog-manager\catalog.sqlite3

Backups:
D:\projects\3dprinthub-backups
```

### Secretها

- Windows Credential Store / Environment variables.
- Secretها در Git commit نمی‌شوند.
- Secretها در SQLite diagnostic/audit و export نباید ذخیره شوند.

### Runner جاری

```text
D:\projects\3DPrintHub\RUN_PHASE49_3F_LOCAL_GATE.ps1
```

Runner جدید، Gateهای قبلی را زنجیره می‌کند:

```text
49.3F → 49.3E → 49.3D
```

بنابراین Runner قدیمی مستقیم برای فاز جاری نباید جای Runner جدید استفاده شود.

---

## 8) ساختار Production / Host

### مسیرهای ثابت

```text
Project:
/home/sfkilvrs/3dprinthub

Python venv:
/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python

Production database:
MySQL: sfkilvrs_EmiAdmin_3dprinthub

Static default:
/home/sfkilvrs/public_html/static

Media default:
/home/sfkilvrs/public_html/media

Project private media default/fallback:
/home/sfkilvrs/3dprinthub/private_media
```

مقادیر نهایی `STATIC_ROOT`, `MEDIA_ROOT`, `PRIVATE_MEDIA_ROOT` ممکن است با `.env` Override شوند؛ قبل از Deploy باید Runtime settings واقعی خوانده شوند.

### انتخاب DB در Django

در `config/settings.py`:

- اگر `DB_NAME` تنظیم شده باشد → MySQL.
- اگر `DB_NAME` خالی باشد → fallback به `BASE_DIR/db.sqlite3`.

**قاعده Production:** قبل از Migration باید `connection.vendor == "mysql"` اثبات شود. اگر Production ناخواسته SQLite را می‌بیند، Migration متوقف می‌شود؛ نباید روی SQLite fallback ادامه داد.

### Passenger

Restart مورد استفاده:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

بعد از تغییر Python/Template/Static/Config، Deploy کامل باید Verification بعد از Restart داشته باشد.

---

## 9) Runbook امن Production

Production فقط بعد از Windows Local QA و تأیید صریح کاربر.

ترتیب استاندارد:

```text
1. git status / branch / expected HEAD
2. Backup .env
3. Backup pending imports
4. Django check
5. makemigrations --check --dry-run
6. Assert DB vendor = mysql
7. mysqldump before migrations
8. migrate --plan
9. migrate --noinput
10. collectstatic --noinput
11. Passenger restart
12. runtime verifier
13. HTTP smoke tests
14. Product/Home/Admin/Cart checks relevant to the phase
15. ثبت نتیجه در docs/PROJECT_CONTEXT
```

DB backup Production باید fail-closed باشد:
- `mysqldump` موجود نباشد → Deploy متوقف.
- dump fail شود → Migration اجرا نشود.
- Password در command line چاپ نشود.
- charset `utf8mb4` حفظ شود.

`deploy/phase48-deploy.sh` مسیر اثبات‌شده Backup/Migrate/Collectstatic/Restart است و `deploy/phase49-deploy.sh` همان مسیر را reuse می‌کند.

---

## 10) خطاهای تاریخی و روش جلوگیری از تکرار

### 10.1) Tkinter: مخلوط شدن `pack()` و `grid()`

**Symptom**

```text
TclError: cannot use geometry manager pack inside ... which already has slaves managed by grid
```

**Root Cause:** یک parent مشترک (`quick_tab`) همزمان childهای `grid` و `pack` داشت.

**Fix:** روی یک parent فقط یک geometry manager؛ holder جدا می‌تواند داخل parent خودش manager دیگری داشته باشد.

**Do Not Repeat:** هنگام افزودن Widget جدید، geometry manager همان parent را ابتدا بررسی کن.

**Status:** FIXED + Regression test.

### 10.2) ذخیره Label مدل AI به‌جای raw model ID

**Root Cause:** Label مثل `model-id • رایگان` می‌توانست به‌جای ID واقعی persist شود.

**Fix:** فقط raw model ID ذخیره می‌شود؛ label فقط UI است.

**Do Not Repeat:** Display value و persisted value را یکی فرض نکن.

**Status:** FIXED + Regression test.

### 10.3) Local Publish بی‌صدا به Stage ناقص برمی‌گشت

**Root Cause:** مسیر `queue_for_publish(notify=False)` دلیل Readiness failure را به اپراتور نشان نمی‌داد.

**Fix:** Save → recompute readiness → optional image finalize → recompute → block publish + exact reasons + audit log.

**Do Not Repeat:** هیچ Publish path نباید Readiness را bypass یا failure را silent کند.

**Status:** FIXED.

### 10.4) Image SEO بلافاصله stale می‌شد

**Root Cause:** Hash روی JSON raw زده می‌شد؛ `\uXXXX` و UTF-8 فارسی از نظر معنا یکسان ولی از نظر رشته متفاوت بودند.

**Fix:** JSON قبل از signature parse/normalize می‌شود.

**Do Not Repeat:** Semantic state را از serialization خام Hash نکن.

**Status:** FIXED + Regression test.

### 10.5) Image mapping با index guessing

**Risk:** حذف/ویرایش metadata عکس اشتباه در صورت تغییر ترتیب تصاویر.

**Fix:** Exact URL/file/manifest identity؛ index guessing ممنوع.

**Status:** FIXED + Regression tests.

### 10.6) Test وابسته به Monkey Patch runtime

**Root Cause:** `inspect.getsource()` روی Method runtime-wrapped نتیجه را وابسته به ترتیب اجرای test می‌کرد.

**Fix:** Source contract از فایل canonical خوانده می‌شود.

**Do Not Repeat:** Source contract test نباید به ترتیب import/patch وابسته باشد.

**Status:** FIXED.

### 10.7) AvalAI HTTP 400 روی Structured Output

**Root Cause:** بعضی Gateway/Modelها `response_format` را قبول نمی‌کنند.

**Fix:** یک Retry کنترل‌شده بدون `response_format` + parse/validation سمت Client.

**Do Not Repeat:** OpenAI/AvalAI/OpenRouter را با یک Structured API فرض نکن؛ Provider capability-aware باش.

**Status:** FIXED + test.

### 10.8) `updated_at` به اشتباه Source Refresh موفق محسوب می‌شد

**Root Cause:** تغییر عادی Product state می‌توانست AI technical flow را تحریک کند.

**Fix:** فقط تغییر واقعی `last_refetched_at` success محسوب می‌شود.

**Do Not Repeat:** Generic record timestamp را جای source freshness استفاده نکن.

**Status:** FIXED + test.

### 10.9) `consultation_required=True` بعد از Import دوباره False می‌شد

**Root Cause:** `apply_price_range()` مقدار درست را set می‌کرد و Phase43 بعداً آن را downgrade می‌کرد.

**Fix:** state قبلی True حفظ می‌شود؛ مرحله بعد فقط requirement اضافه می‌کند، نه حذف.

**Do Not Repeat:** Post-processing نباید تصمیم قبلی business rule را بدون Contract مشخص overwrite کند.

**Status:** FIXED + E2E regression.

### 10.10) کدهای داخلی در JSON-LD عمومی

**Symptom:** ظاهر صفحه فارسی بود ولی Structured Data هنوز `ready_product` و `made_to_order` منتشر می‌کرد.

**Root Cause:** Template visible از Label فارسی استفاده می‌کرد ولی SEO serializer از raw field.

**Fix:** JSON-LD هم از Persian runtime labels استفاده می‌کند.

**Do Not Repeat:** فقط HTML را تست نکن؛ Source/JSON-LD/SEO نیز جزو Public Contract است.

**Status:** FIXED در Phase49.3F CI iteration.

### 10.11) نمایش `Username` در صفحه عمومی Product

**Root Cause:** attribution داخلی source وارد Public Template شده بود.

**Fix:** source internal attribution از نمایش مشتری حذف شد.

**Do Not Repeat:** Internal operator/source identity را Public presentation فرض نکن.

**Status:** FIXED + public test.

### 10.12) اختلاف Cache قیمت و Range نمایش سایت

**Risk:** Product Detail یک عدد و Cart/Checkout عدد دیگر نشان دهد.

**Fix:** بعد از profile sync، active variantها دوباره محاسبه و `price_min/max` از همان `cached_unit_price` نهایی می‌شوند.

**Do Not Repeat:** Range را از منبعی جدا از Cart price تولید نکن.

**Status:** Guarded in 49.3F.

---

## 11) خطاهای Host که نباید دوباره تکرار شوند

### 11.1) اجرای Migration روی DB اشتباه

Production باید MySQL باشد. اگر `DB_NAME`/env اشتباه باشد Django ممکن است به SQLite fallback کند.

**Guard:** قبل از backup/migration `connection.vendor` و database name بررسی شود.

### 11.2) Migration بدون Backup

ممنوع. Backup DB قبل از `migrate` شرط است.

### 11.3) ادامه Deploy وقتی `mysqldump` وجود ندارد یا fail شده

ممنوع. Deploy باید قبل از Migration stop شود.

### 11.4) استفاده از Python اشتباه Host

همیشه Python پروژه:

```text
/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python
```

استفاده از `python` عمومی shell می‌تواند dependency/settings متفاوت بدهد.

### 11.5) فراموش کردن `collectstatic`

اگر CSS/JS/static تغییر کرده، فقط Pull + Restart کافی نیست. `collectstatic --noinput` باید در Deploy path باشد.

### 11.6) Restart بدون Verify

بعد از `touch tmp/restart.txt` باید runtime verifier و HTTP smoke test اجرا شود.

### 11.7) Dirty Working Tree روی Host

قبل از Deploy باید Source tracked clean باشد. برای حل dirty state، `reset --hard` خودکار نزن؛ ابتدا منشأ فایل تغییرکرده مشخص شود.

### 11.8) Warning را با Failure اشتباه نکن

Warningهای شناخته‌شده فعلی:

- `3dprinthub.W001`: Google membership بدون credentials غیرفعال است.
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: in-memory realtime برای cross-process کافی نیست؛ Redis یا polling strategy لازم است.
- Pillow `Image.getdata()` deprecation: بدهی refactor آینده، نه Failure فعلی.

این Warningها باید مستند باشند، ولی نباید برای «رفع Warning» قابلیت‌های unrelated ناگهانی بازنویسی شوند.

---

## 12) خطای باز فعلی — Phase49.3F

### وضعیت آخرین CI شناخته‌شده

```text
Run: 32346200148
Job: 96355362243

PowerShell runner contract: PASS
Compile: PASS
Django check: PASS
makemigrations --check: PASS
Migration plan: PASS
49.3F AddField-only safety: PASS
Targeted Django tests: 69/69 PASS
Windows Catalog Center tests: FAIL
Full Django suite: SKIPPED because Windows step failed
Production: UNTOUCHED
```

### Failure باز

Test:

```text
tests.test_phase49_3f_product_intelligence
Phase493FRuntimeTraceTests.test_runtime_trace_redacts_structured_and_inline_secrets
```

Observed leak در fake test data:

```text
Authorization: *** very-secret-token *** secret=***
```

Structured fields مانند `api_key` و `refresh_token` درست Redact شده‌اند، اما token داخل متن آزاد `message` هنوز کامل حذف نشده است.

### Root Cause فعلی

`phase49_3f_runtime_trace._sanitize(str)` به `runtime_logging.redact()` متکی است. Redactor مرکزی بعضی الگوها را mask می‌کند ولی شکل آزاد Authorization در این تست، tail secret را باقی می‌گذارد.

### Fix موردنیاز

- **فقط Redaction رشته‌ای** را اصلاح کنیم.
- ساختار Runtime Trace، مسیر فایل، identity fields و JSONL format را تغییر ندهیم.
- تست فعلی ضعیف یا حذف نشود.
- تست‌های قبلی Diagnostics نیز دوباره اجرا شوند تا Redaction جدید Regression ایجاد نکند.

**Status:** OPEN — blocker CI نهایی 49.3F.

---

## 13) مسیر باقی‌مانده — از همین نقطه

### Gate A — بستن Failure فعلی

- [ ] اصلاح حداقلی inline Authorization/Bearer secret redaction.
- [ ] اجرای focused Runtime Trace test.
- [ ] اجرای Diagnostics secret tests قدیمی.
- [ ] اجرای Windows Phase49 tests.

### Gate B — CI نهایی

- [ ] CI Targeted Django سبز.
- [ ] Windows Catalog Center سبز.
- [ ] Launcher markers سبز.
- [ ] Full Django suite سبز.
- [ ] شماره Run/Job/Commit نهایی در همین سند و `PROJECT_CONTEXT.md` ثبت شود.

### Gate C — Windows Local Gate

- [ ] `git fetch/pull` از Epic.
- [ ] اجرای canonical `RUN_PHASE49_3F_LOCAL_GATE.ps1`.
- [ ] Backup Local Django DB و Catalog DB ساخته شود.
- [ ] migration 0033/0023 فقط Additive اعمال شود.
- [ ] Local automated gate کامل PASS شود.

### Gate D — Manual Windows QA

- [ ] AI Center scroll/sticky controls.
- [ ] Gemini Direct با Key واقعی + model list.
- [ ] AvalAI/OpenRouter/OpenAI sanity test در صورت key واقعی.
- [ ] AI progress states و 30s connection timeout.
- [ ] Image SEO فقط 1–2 عکس انتخاب‌شده؛ هیچ image/file/url به AI نرود.
- [ ] Metadata عکس انتخاب‌نشده حفظ شود.
- [ ] Runtime log بدون هیچ secret.
- [ ] Source refetch + technical AI فقط بعد از `last_refetched_at` واقعی.
- [ ] Dynamic pricing example = 1,120,000 تومان قبل از extras/shipping.
- [ ] Product public Persian labels / no Username / no raw codes.
- [ ] یک Product واقعی **LOCAL PUBLISH ONLY**.
- [ ] Product Detail price == Cart unit price == Checkout unit source.
- [ ] Hero / Admin / reverse sync regression بررسی شود.

### Gate E — تأیید کاربر

- [ ] تأیید صریح Local/Visual/Data QA.

### Gate F — Production

فقط بعد از Gate E:

- [ ] Host exact HEAD check.
- [ ] Production `.env` / pending / DB backup.
- [ ] assert MySQL.
- [ ] migration plan.
- [ ] migrate.
- [ ] collectstatic.
- [ ] Passenger restart.
- [ ] runtime verify.
- [ ] smoke tests.
- [ ] DB/Data/Media safety verification.
- [ ] سند فاز و این فایل با نتیجه نهایی Update شوند.

---

## 14) نقشه کدهای اصلی مرتبط با مسیر جاری

### Windows Catalog Center

```text
catalog_center/launch.py
catalog_center/app/product_workspace_epic49.py
catalog_center/app/phase49_readiness_wizard.py
catalog_center/app/phase49_3b_guided_wizard.py
catalog_center/app/phase49_ai_provider_hub.py
catalog_center/app/phase49_3b_ai_product_runtime.py
catalog_center/app/phase49_3c_image_pipeline.py
catalog_center/app/phase49_3c_persian_content.py
catalog_center/app/phase49_3d_workflow_hardening.py
catalog_center/app/phase49_3e_ai_task_center.py
catalog_center/app/phase49_3f_gemini_provider.py
catalog_center/app/phase49_3f_ai_experience.py
catalog_center/app/phase49_3f_selected_image_ai.py
catalog_center/app/phase49_3f_product_intelligence.py
catalog_center/app/phase49_3f_runtime_trace.py
catalog_center/app/phase49_3f_source_refresh_guard.py
catalog_center/app/ai_providers.py
catalog_center/app/openai_content.py
```

### Django / Store / Pricing

```text
store/epic49_catalog_profile.py
store/phase49_unified_sync.py
store/phase49_3b_profile_media.py
store/phase49_3b_hero_media_sync.py
store/phase49_3f_pricing.py
store/phase49_3f_pricing_finalize.py
store/phase49_3f_admin.py
store/templatetags/store_seo.py
templates/store/product_detail.html
templates/store/product_list.html
```

### Bridge / Hero

```text
catalog_bridge/
website/phase49_unified_sync.py
website/phase49_3b_hero_media.py
website/phase49_3b_profile_media_mirror.py
templates/website/partials/hero.html
```

### Migrationهای جاری Phase49.3F

```text
store/migrations/0033_phase49_3f_pricing_intelligence.py
website/migrations/0023_phase49_3f_material_runtime_rates.py
```

### CI / Runner

```text
.github/workflows/phase49-epic-ci.yml
RUN_PHASE49_3D_LOCAL_GATE.ps1
RUN_PHASE49_3E_LOCAL_GATE.ps1
RUN_PHASE49_3F_LOCAL_GATE.ps1
```

### Production

```text
deploy/phase48-deploy.sh
deploy/phase49-deploy.sh
deploy/epic49_backup_database.py
deploy/epic49_verify_runtime.py
```

---

## 15) Checklist اجباری قبل از هر تغییر جدید

- [ ] درخواست کاربر را به یک Delta دقیق تبدیل کرده‌ام.
- [ ] فایل‌ها/ماژول‌های موجود مربوط را قبل از کدنویسی خوانده‌ام.
- [ ] بررسی کرده‌ام قابلیت مشابه قبلاً وجود دارد یا نه.
- [ ] مسیر Mature را Extend می‌کنم، نه اینکه Duplicate بسازم.
- [ ] `Must-Not-Touch`ها مشخص شده‌اند.
- [ ] DB/Media/Secret/Production safety مشخص است.
- [ ] اگر Migration نیاز است، Additive-first طراحی شده.
- [ ] Regression test قابلیت قبلی در نظر گرفته شده.
- [ ] Sync boundaryهای متاثر مشخص شده‌اند.
- [ ] هیچ Secret در test fixture/log/export واقعی وارد نمی‌شود.
- [ ] Production در این مرحله لازم نیست مگر Local قبلاً صریح تأیید شده باشد.

---

## 16) Checklist بعد از هر تغییر

- [ ] Compile/Syntax PASS.
- [ ] Focused tests PASS.
- [ ] Regression tests قبلی PASS.
- [ ] `manage.py check` PASS یا فقط warningهای شناخته‌شده.
- [ ] `makemigrations --check --dry-run` نتیجه مورد انتظار.
- [ ] Migration safety بررسی شده.
- [ ] CI کامل PASS.
- [ ] Git working tree موردنظر clean.
- [ ] `PROJECT_CONTEXT.md` و Phase doc Update شده.
- [ ] این Master Roadmap در بخش Current Status / Error Ledger / Remaining Path Update شده.
- [ ] Local Gate اجرا شده.
- [ ] Visual/Data QA اجرا شده.
- [ ] فقط بعد از تأیید صریح → Production.

---

## 17) عملیات ممنوع به‌عنوان «راه‌حل سریع»

بدون فاز مستقل و تأیید صریح:

- `git reset --hard` روی فایل‌های ناشناخته/کاربر.
- `git clean -fd` برای رفع Deploy.
- حذف `db.sqlite3`.
- حذف Catalog SQLite.
- حذف `.env`.
- حذف `media/` یا `private_media/`.
- `DROP TABLE`.
- `TRUNCATE`.
- حذف Product/Asset تاریخی برای حل migration.
- ساخت DB جدید فقط برای اینکه migration سبز شود.
- ساخت Endpoint/Model/Price Engine/AI workflow موازی وقتی مسیر موجود قابل Extend است.
- حذف تستی که Bug واقعی را پیدا کرده فقط برای سبز کردن CI.
- تبدیل Warning شناخته‌شده به بازنویسی unrelated.

---

## 18) Definition of Done هر فاز

یک فاز فقط وقتی **DONE** است که همه موارد زیر برقرار باشند:

```text
Code complete
+ Focused tests green
+ Regression tests green
+ CI full green
+ Migration safety verified
+ Windows Local Gate green
+ Manual visual/data QA green
+ User explicit approval
+ Production backup/deploy (اگر فاز production-bound است)
+ Production smoke/data checks green
+ Docs/roadmap/context updated
```

اگر هر کدام ناقص باشد، وضعیت باید `IN PROGRESS` یا `BLOCKED` ثبت شود، نه DONE.

---

## 19) وضعیت جاری پروژه در زمان ایجاد این فایل

**Phase فعال:** `49.3F Product Intelligence / Dynamic Pricing / AI UX`  
**Development branch:** `epic/phase49-unified-product-slider-sync`  
**Django targeted suite:** 69/69 PASS در Run `32346200148`  
**Current blocker:** Runtime Trace inline secret redaction  
**Windows CI:** FAILED روی همان Redaction test  
**Full Django suite در Run جاری:** به‌علت Windows failure اجرا نشده  
**Local 49.3F final gate:** هنوز پس از CI نهایی لازم است  
**Production:** **UNTOUCHED / NOT APPROVED**

### قدم بعدی دقیق

**نه بازنویسی AI Center، نه تغییر قیمت، نه تغییر DB.**  
قدم بعدی فقط:

```text
Fix inline secret redaction
→ keep current log schema intact
→ keep current tests intact
→ rerun Windows diagnostics + Phase49 CI
→ full suite
→ update docs
→ Windows Local Gate
```

این همان اصل «اصلاح ارتباط/Root Cause بدون به‌هم‌زدن کلیات» است.

---

## 20) قانون نگهداری این سند

از این فاز به بعد، در پایان هر Phase یا Hotfix مهم باید حداقل این چهار قسمت Update شوند:

1. `مسیر طی‌شده پروژه`
2. `خطاهای تاریخی / Error Ledger`
3. `خطای باز فعلی / Current Status`
4. `مسیر باقی‌مانده`

برای CI نهایی نیز باید ثبت شود:

```text
Final commit SHA
CI Run ID
CI Job ID
Targeted result
Windows result
Full suite result
Local Gate result
Production result
```

هدف این سند صرفاً گزارش نیست؛ **Guard مهندسی پروژه است تا توسعه بعدی بر پایه وضعیت واقعی انجام شود و کدهای حل‌شده دوباره از نو یا به شکل موازی ساخته نشوند.**
