# Epic49 — Persian Sales Hero Hotfix

## وضعیت

- Branch: `epic/phase49-unified-product-slider-sync`
- Final runtime HEAD before documentation: `dc1699d5e78563205dbac66f219f765601055456`
- Final CI probe PR: #19 (temporary, do not merge)
- GitHub Actions run: `32143733191`
- GitHub Actions job: `95732323558`
- Result: **SUCCESS**
- Production: **NOT TOUCHED**
- New Django migration in this hotfix: **NONE**

## مسئله‌ای که حل شد

در Hero صفحه اصلی رکوردهای قدیمی می‌توانستند عنوان خام انگلیسی مثل `Vesper – Sculptural Bedside Lamp` و متن Cookie/Consent/Tracking سایت منبع را نمایش دهند. علت این بود که fallbackهای قدیمی `title_override`, `description`, `asset.title` و `asset.description` را بدون قرارداد فارسی/Boilerplate به خروجی عمومی راه می‌دادند.

هدف نهایی:

1. UI عمومی سایت فارسی باشد.
2. Source of Truth کارمند همان داده فارسی و SEO ساخته‌شده در Catalog Center Windows باشد.
3. SEO عمومی Product و SEO مستقل Hero هر دو نیت فروش/خرید داشته باشند.
4. Raw source HTML/Cookie/Privacy boilerplate هرگز وارد Hero عمومی یا Slider Profile نشود.
5. توضیح Hero در حالت عادی حداکثر دو خط باشد و با کلیک متن کامل باز شود.

## قرارداد Source of Truth

### عنوان Hero

اولویت:

1. `homepage_slider_title_fa` از Windows
2. AI `homepage_slider_seo.title_fa`
3. `seo_title_fa`
4. `title_fa`
5. `ImportedPrintAsset.persian_title`
6. عنوان فارسی Product
7. fallback فارسی عمومی

`source_title` و عنوان خام انگلیسی منبع در این Resolver مجاز نیستند.

### توضیح Hero

اولویت:

1. `homepage_slider_description_fa`
2. AI Slider description
3. `short_description_fa`
4. `seo_description_fa`
5. `description_fa`
6. `persian_short_description`
7. `persian_description`
8. Product short description فارسی
9. fallback فروش فارسی

`source_description`, Cookie/Consent/Privacy و HTML خام به خروجی عمومی راه ندارند.

### Group / Badge Hero

فقط موارد فارسی پذیرفته می‌شوند:

1. Category فارسی Product
2. Segment display فارسی Metrics
3. `محصول منتخب`

نام انگلیسی Source مثل MakerWorld دیگر fallback عمومی نیست.

### Alt Hero

اولویت:

1. `homepage_slider_alt_text`
2. AI Slider image alt
3. altهای فارسی Windows
4. fallback فارسی با نیت `خرید و سفارش چاپ سه‌بعدی`

### Focus Keyword فروش

Keyword باید نیت تراکنشی داشته باشد. اگر عبارت فارسی شامل یکی از این intentها باشد همان حفظ می‌شود:

- خرید
- سفارش
- قیمت
- فروش
- تهیه
- ثبت سفارش

در غیر این صورت `خرید ` به ابتدای Keyword اضافه می‌شود.

مثال:

`آباژور سه بعدی` → `خرید آباژور سه بعدی`

## Product SEO فروش

`sync_product_seo()` در Runtime Epic به Resolver فارسی فروش متصل شده است:

- Meta title فارسی
- Meta description فارسی
- Focus keyword فروش
- OG title/description فارسی
- tags/hashtags فارسی در صورت وجود
- Source attribution همچنان برای Audit داخلی حفظ می‌شود ولی متن خام منبع به Meta copy عمومی تبدیل نمی‌شود.

## Sanitizer مشترک

فایل:

`store/phase49_persian_sales_copy.py`

قابلیت‌ها:

- HTML entity decode
- حذف `<script>/<style>`
- حذف tagها و `<br>`
- whitespace normalization
- تشخیص فارسی
- رد Cookie/Privacy/Tracking boilerplate
- تولید sales-intent focus keyword
- Resolver مشترک Product SEO و Slider SEO

Boilerplateهای ردشونده شامل نمونه‌هایی مثل:

- Cookie Settings
- We use cookies
- tracking technologies
- personalized content
- targeted ads
- manage your preferences
- privacy policy
- terms and conditions

## Profile save gate

فایل:

`store/phase49_persian_sales_runtime.py`

یک `pre_save` روی `ProductCatalogProfile` نصب شده است. بنابراین فرقی ندارد Slider SEO از کجا وارد شود:

- Windows import
- Catalog Bridge management API
- Django Admin
- Hero → Profile mirror

قبل از Save، title/description/alt/button/focus به قرارداد فارسی فروش Normalize می‌شوند.

این تصمیم مهم است چون صرفاً Sanitizer کردن صفحه Home کافی نبود؛ یک Bridge/Employee client قدیمی هم نباید بتواند Profile انگلیسی را ذخیره کند.

## Public Hero runtime

فایل:

`website/phase49_persian_sales_hero.py`

این Runtime:

- `effective_title`
- `effective_description`
- `effective_group_title`
- `effective_alt_text`
- `effective_button_text`

را فقط با explicit field فارسی یا Resolver فارسی تولید می‌کند.

همچنین `hero_suggestions` قدیمی 49.2B را Rebind می‌کند تا Admin Hero Studio هم همان Source of Truth را ببیند.

یک `pre_save` نیز رکورد Hero قدیمی با title/description/group/alt/button ناسالم را هنگام Save ترمیم می‌کند.

## Windows Catalog Center

فایل:

`catalog_center/app/phase49_persian_sales_desktop.py`

Workspace نهایی Epic Patch می‌شود و قابلیت‌های 8.7.1 حفظ می‌شوند.

قواعد:

- `source_title/source_description` انگلیسی fallback Slider نیستند.
- Slider fields در reload/save فارسی Normalize می‌شوند.
- Product SEO فارسی Windows fallback Slider است.
- در نبود فارسی، fallback فروش فارسی استفاده می‌شود؛ Cookie/English raw source استفاده نمی‌شود.

Marker Launcher:

`EPIC49_PERSIAN_SALES_HERO=ENABLED`

هم launcher عادی و هم `portable_entry.py` این Patch را نصب می‌کنند.

## Hero UI دوخطی + Expand

Template:

`templates/website/partials/hero.html`

CSS:

`static/css/phase49_2c-hero-effects.css`

JS:

`static/js/phase49_2c-home-hero.js`

رفتار:

- full description در DOM و قابل خواندن باقی می‌ماند.
- حالت بسته: `-webkit-line-clamp: 2` + ellipsis.
- کنترل `نمایش بیشتر` دارد.
- کلیک → full text.
- متن کنترل به `بستن توضیحات` تغییر می‌کند.
- `aria-expanded` برای Accessibility.
- در حالت باز autoplay Hero متوقف می‌شود.
- هنگام بستن autoplay ادامه می‌یابد.
- هنگام تغییر Slide حالت expanded reset می‌شود.
- cinematic effects و reduced-motion قبلی حفظ شده‌اند.

## Repair داده‌های قدیمی

Command:

`python manage.py phase49_repair_persian_sales_hero`

به‌صورت پیش‌فرض **DRY_RUN** است و دیتابیس را تغییر نمی‌دهد.

برای اعمال فقط بعد از Backup/بررسی خروجی:

`python manage.py phase49_repair_persian_sales_hero --apply`

موارد قابل ترمیم:

- Hero title
- Hero description
- Hero group
- Hero alt
- Hero button
- ProductCatalogProfile Slider title
- description
- alt
- button
- focus keyword

هیچ Product/Image/Price/Delete در این Command انجام نمی‌شود.

## دیتابیس

این Hotfix Migration جدید ندارد.

Schemaهای Persistent همچنان از Epic اصلی هستند:

- `store.0030_phase49_unified_sync_contract`
- `website.0021_phase49_unified_hero_sync`

Hotfix فقط Runtime validation/normalization و repair command اضافه می‌کند.

## تست‌ها

### تست مستقیم مشکل Vesper/Cookie

`website.test_phase49_persian_sales_hero`

ورودی تست شامل همان الگوی خراب است:

- English Vesper title
- Cookie/Consent/Tracking HTML

و ثابت می‌کند:

- Cookie رد می‌شود.
- Windows Slider Persian SEO اولویت دارد.
- English legacy override برنده نمی‌شود.
- Group انگلیسی Source برنده نمی‌شود.
- Alt فارسی فروش است.
- Focus keyword خرید-محور است.
- دوخط/Expand در Template/CSS/JS فعال است.

### Windows tests

`catalog_center/tests/test_phase49_persian_sales_slider.py`

ثابت می‌کند:

- raw English/Cookie fallback نیست.
- Product SEO فارسی Slider را تغذیه می‌کند.
- launcher Patch فعال است.

### E2E

`store.test_phase49_unified_import_e2e`

Batch واقعی تست اکنون Slider SEO مستقل فارسی دارد و زنجیره زیر را بررسی می‌کند:

Windows batch → Importer → Product → ProductCatalogProfile → HomepageHeroSlide → image relation → cinematic settings → revision/idempotency

## خطاهایی که Self-Test گرفت و رفع شدند

Self-Testهای میانی عمداً نگه داشته شدند تا Regressionها قبل از Local دیده شوند:

1. ترتیب fallback: `product.title` قبل از `asset.persian_title` بود → اصلاح شد؛ داده فارسی Windows/Imported Asset جلوتر است.
2. Focus Keyword عمومی مثل `چراغ دکوراتیو` sales intent نداشت → به `خرید چراغ دکوراتیو` Normalize شد.
3. Bridge test fixtures انگلیسی بودند → به Contract فارسی واقعی ارتقا داده شدند؛ Revision/409 behavior دست نخورده ماند.
4. E2E fixture Focus عمومی بود → Batch E2E به Slider SEO مستقل فارسی/فروش ارتقا یافت.
5. Full Suite دو Contract قدیمی هنوز انتظار `آباژور سه بعدی` داشتند → expectation به `خرید آباژور سه بعدی` ارتقا یافت؛ Runtime عقب‌گرد نکرد.

## Validation نهایی

Final CI:

- Run: `32143733191`
- Job: `95732323558`

نتیجه:

- Compile changed Python surfaces: **SUCCESS**
- Django check + makemigrations contract + migrate plan: **SUCCESS**
- Phase49 targeted Django/Bridge/Hero suite: **SUCCESS**
- Windows Catalog Center Epic49 suite: **SUCCESS**
- Full Django suite: **SUCCESS**

Production در طول این Hotfix دست نخورده است.

## Gate بعدی

1. Windows Pull آخرین Epic.
2. `makemigrations --check --dry-run` باید No changes detected باشد.
3. اجرای تست مستقیم Persian Sales Hero و Windows.
4. اجرای Repair Command در حالت Dry Run.
5. بررسی خروجی و Backup دیتابیس Local.
6. Apply repair روی Local.
7. Restart runserver + hard refresh.
8. Visual QA:
   - Hero فارسی
   - Cookie/HTML حذف
   - badge فارسی
   - دو خط + ellipsis
   - click expand/collapse
   - title/alt/focus فروش‌محور
9. فقط بعد از تأیید Local، Production backup/deploy بررسی می‌شود.
