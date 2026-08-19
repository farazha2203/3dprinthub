# Phase49.3C — Operator Workflow Recovery + AI Autofill + Image SEO Pipeline

تاریخ: 2026-08-19  
Branch: `epic/phase49-unified-product-slider-sync`

## 1) هدف

این فاز برای Repair جریان واقعی اپراتور بعد از Phase49.3B ایجاد شد؛ هدف ساخت Feature موازی یا Workspace جدید نیست.

مسیر رسمی همچنان:

`Windows Catalog Center → Product Workspace → Local Publish → Django Product/Profile/Hero → Store/Home → پس از تأیید → Production`

اهداف:

- Readiness زنده و قابل فهم در همان لحظه ویرایش.
- نمایش نام دقیق فیلد ناقص، نه فقط نام Stage.
- دستیار AI در تمام مراحل + دکمه تکمیل کل فیلدهای AI.
- بازگردانی کامل خروجی‌های AI: short description, tags, hashtags, keywords, SEO, sales bullets, social caption, image alts, material recommendations, slider SEO.
- رفع حذف ظاهراً اشتباه عکس.
- حداکثر 10 عکس از دریافت مستقیم سایت.
- جلوگیری از URL duplicate و حذف exact/perceptual duplicate از انتخاب نهایی.
- نمایش filename فعلی و filename نهایی SEO.
- ساخت نسخه WebP نهایی با Metadata بازسازی‌شده و Attribution صحیح.
- Fail-Closed کردن Queue / Local / Production وقتی Gateهای واقعی ناقص‌اند.
- حفظ کامل Cache/source images و DBهای قبلی؛ هیچ Reset انجام نمی‌شود.

## 2) Root Causeهای قطعی

### 2.1 Readiness از DB قدیمی خوانده می‌شد

Phase49.3A/3B عمدتاً Readiness را هنگام `reload`, `save`, `select_section` از SQLite محاسبه می‌کرد.

نتیجه:

- اپراتور قیمت/عنوان/SEO را روی فرم تغییر می‌داد.
- تا Save/Reload، State قدیمی باقی می‌ماند.
- Sidebar بلافاصله سبز/قرمز نمی‌شد.
- Operator نمی‌فهمید دقیقاً کدام فیلد مانع ادامه است.

Repair:

- `catalog_center/app/phase49_3c_operator_recovery.py`
- snapshot زنده از Widgetهای فعلی روی DB row merge می‌شود.
- `StringVar/IntVar`, `Entry`, `Text`, `Combobox`, `Checkbutton` observe می‌شوند.
- debounce = 180ms.
- Readiness بدون Save از مقادیر روی فرم محاسبه می‌شود.

### 2.2 حذف عکس اشتباه در واقع Visual Identity mismatch بود

Callback کارت تصویر URL همان کارت را درست نگه می‌داشت؛ مشکل اصلی mapping Thumbnail بود.

کد Legacy وقتی URL mapping دقیق نداشت، fallback می‌کرد به:

`sorted(local_dir/images/*)[index]`

از طرف دیگر Primary image می‌توانست URL order را جابه‌جا کند.

نتیجه:

- Card متعلق به URL-B بود.
- Thumbnail فایل A با index روی همان Card نمایش داده می‌شد.
- Operator تصور می‌کرد A را انتخاب کرده است.
- حذف واقعی URL-B انجام می‌شد.

Repair:

- index fallback برای Phase49.3C ممنوع است.
- resolver فقط Exact Identity می‌پذیرد:
  1. `image_seo_manifest.json`
  2. exact `page_extract.json URL → local_file`
  3. exact `local://filename`
  4. deterministic URL-hash cache
- اگر exact mapping پیدا نشود، فایل حدس زده نمی‌شود.

### 2.3 AI Schema فیلدها را داشت ولی empty result قابل عبور بود

Schema قبلی هنوز این فیلدها را داشت:

- `short_description_fa`
- `tags_fa`
- `hashtags_fa`
- `target_keywords_fa`
- `seo_title_fa`
- `seo_description_fa`
- `sales_bullets`
- `social_caption_fa`
- `image_alt_texts`
- `material_recommendations`
- `homepage_slider_seo`

همچنین `_apply_ai_pack` آن‌ها را در DB می‌نوشت.

Regression اصلی این بود که Provider می‌توانست key را با مقدار empty array/string برگرداند و Workflow آن را موفق تلقی کند.

Repair:

- `catalog_center/app/phase49_3c_ai_recovery.py`
- خروجی Commerce بعد از Provider validate می‌شود.
- اگر Editorial field خالی باشد یک structured repair request انجام می‌شود.
- اگر Provider repair هم Fail شود، فقط Editorial derivativeهای امن deterministic تکمیل می‌شوند.
- قیمت، مجوز، ابعاد، stock، selected material/color و performance claim هرگز ساخته نمی‌شوند.
- Material Recommendation suggestion است و selection واقعی محصول را تغییر نمی‌دهد.

## 3) Live Readiness Contract

هر تغییر فرم با debounce کوتاه بررسی می‌شود.

Stageها:

1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

State:

- `✅` کامل
- `❌ ★` اولین Stage ناقص
- `🔒` Stage آینده

پنل جدید:

`موارد ناقص زنده`

مثال:

- `۲. سفارش، قیمت و گزینه‌ها ← قیمت یا حالت سفارش • اپراتور`
- `۳. تصاویر ← Alt تصویر 1`
- `۴. محتوا و SEO ← SEO Description فارسی`
- `۵. منبع و مجوز ← مجوز تجاری مجاز • اپراتور`

Double click روی Missing item Operator را به Stage مربوط هدایت می‌کند.

## 4) AI Operator Assistant

Toolbar همیشه در Product Workspace دیده می‌شود:

- `✨ دستیار AI همین مرحله`
- `✨ تکمیل هوشمند همه فیلدهای AI`
- `🖼 نهایی‌سازی SEO تصاویر`

### رفتار Stage-aware

- Stage 1 → Title-only translation.
- Stage 2 → Commerce AI؛ اما قیمت/material/color واقعی را جعل نمی‌کند.
- Stage 3 → اگر Altها وجود دارند Image Finalize؛ اگر ندارند Commerce AI برای Image SEO/Alt اجرا می‌شود.
- Stage 4 → Full ecommerce/content/SEO.
- Stage 5 → AI editorial help؛ license تصمیم Operator می‌ماند.
- Stage 6 → Slider/Hero SEO + content pack.
- Stage 7 → Completion assistant؛ Publish فقط بعد از Gate سبز.

Global AI خروجی را قبل از Apply از مسیر Preview موجود عبور می‌دهد؛ Manual content silent overwrite نمی‌شود.

## 5) AI Completeness Recovery

Commerce pack باید در نهایت این سطوح را بدون empty value تحویل دهد، وقتی از نظر Editorial قابل تولید است:

- title
- short description
- full description
- categories
- tags
- hashtags
- 3+ target keywords
- SEO title/description
- sales bullets
- social caption
- image alts (تا 10 تصویر)
- material recommendations
- slider SEO

Fallback محافظه‌کار:

- اگر Material واقعی انتخاب شده، recommendation می‌تواند همان گزینه واقعی را توضیح دهد.
- اگر هیچ Material واقعی انتخاب نشده و Provider repair شکست بخورد، `PLA` فقط به‌صورت `recommended=False` و «پیشنهاد عمومی اولیه برای بررسی اپراتور» ثبت می‌شود؛ Material selection واقعی تغییر نمی‌کند.

## 6) Image Intake Contract

حداکثر:

`MAX_SOURCE_IMAGES = 10`

Direct extractor در Runtime حتی اگر UI/Legacy مقدار 60/80 بدهد آن را به 10 clamp می‌کند.

Dedupe:

1. Canonical URL dedupe قبل از نگه‌داری result.
2. SHA-256 exact file duplicate.
3. Conservative dHash visual duplicate برای فایل‌هایی که قبلاً دانلود شده‌اند.

Duplicate cache فیزیکی برای حفظ forensic/source data حذف نمی‌شود؛ فقط از Product selection/final output کنار گذاشته می‌شود.

## 7) Image Identity / Delete Safety

Stable identity از source URL + content SHA ساخته می‌شود.

Phase49.3C هیچ local file را فقط از روی index حدس نمی‌زند.

نتیجه مورد انتظار QA:

- عکس A را تیک بزن.
- همان Thumbnail/filename A باید در confirmation و selection باشد.
- حذف فقط source URL مربوط به A را از Product حذف می‌کند.
- Cache فیزیکی پاک نمی‌شود.

## 8) Image SEO Finalization

فایل‌های Source/Cache دست‌نخورده می‌مانند.

برای Final selected images یک نسخه جدید ساخته می‌شود:

`<product local_dir>/seo_images/`

نام نمونه:

`fanart-solidarity-bear-3d-print-01.webp`

به‌جای:

`001.webp`

هر Card نمایش می‌دهد:

- `فایل فعلی`
- `نام SEO`

### Metadata rebuild

Final image دوباره Encode می‌شود؛ Metadata قدیمی فایل Final carry-forward نمی‌شود.

Metadata نهایی شامل:

- image_id
- source URL
- source page URL
- original filename
- SEO filename
- alt
- title
- caption
- keywords/tags
- creator
- copyright holder
- publisher
- editor
- operator
- license name/url
- credit line
- original/final SHA-256
- metadata version
- SEO signature

WebP EXIF-compatible metadata نیز با Pillow نوشته می‌شود؛ JSON manifest همچنان canonical audit record است.

Manifest:

`image_seo_manifest.json`

Desktop DB additive column:

`image_metadata_json`

این تغییر فقط SQLite Desktop است و توسط `ALTER TABLE ADD COLUMN` انجام می‌شود؛ Django migration جدید ندارد.

## 9) Copyright / Attribution Safety

Rule:

- `owned` → Copyright holder = `3DPrintHub`.
- `public_domain` → `Public Domain`.
- Third-party/allowed/review → Creator/Source مالکیت اصلی حفظ می‌شود.
- `3DPrintHub` فقط Publisher/Editor ثبت می‌شود.

هیچ Third-party image به‌اشتباه Copyright اختصاصی 3DPrintHub نمی‌گیرد.

## 10) SEO Signature / Stale Metadata Protection

Metadata هر تصویر `seo_signature` دارد.

Signature از این ورودی‌ها ساخته می‌شود:

- title/source title
- short description
- SEO title/description
- keywords
- tags
- hashtags
- image alts
- author/source
- source URL
- license
- commercial status

اگر بعداً یکی از این‌ها تغییر کند:

`بروزرسانی Metadata تصویر N`

دوباره به Missing list می‌رود و Stage Images قرمز می‌شود تا Finalize مجدد انجام شود.

## 11) Batch / Django Media

`image_metadata_json` چون جزو Desktop product row است داخل `desktop_editorial.json` منتقل می‌شود و در Imported Asset source payload حفظ می‌شود.

Batch image copy برای Phase49.3C SEO filename را حفظ می‌کند؛ دیگر Final SEO image به `001.webp` برگردانده نمی‌شود.

Django `ProductImage.alt_text` همچنان از Image Alt contract موجود تغذیه می‌شود و bytes تصویر Final شامل Metadata بازسازی‌شده است.

## 12) Publish Fail-Closed

49.3C فقط UI indicator نیست.

`queue_for_publish()` اکنون قبل از Queue/Local/Production:

1. Save امن انجام می‌دهد.
2. Full live readiness را دوباره محاسبه می‌کند.
3. Image Metadata gate را نیز بررسی می‌کند.
4. اگر ناقص باشد Publish/Queue متوقف می‌شود.
5. Missing list دقیق نمایش داده می‌شود.

Local/Production buttons تا Full Readiness سبز Disabled می‌مانند.

## 13) فایل‌های این فاز

New:

- `catalog_center/app/phase49_3c_operator_recovery.py`
- `catalog_center/app/phase49_3c_ai_recovery.py`
- `catalog_center/app/phase49_3c_image_pipeline.py`
- `catalog_center/tests/test_epic49_phase49_3c_operator_recovery.py`
- `docs/PHASE49_3C_OPERATOR_WORKFLOW_RECOVERY.md`

Updated:

- `catalog_center/launch.py`
- `.github/workflows/phase49-epic-ci.yml`
- `PROJECT_CONTEXT.md`

## 14) Runtime markers

`launch.py --verify-only` باید این‌ها را چاپ کند:

- `EPIC49_3C_LIVE_READINESS=ENABLED`
- `EPIC49_3C_STAGE_AI=ENABLED`
- `EPIC49_3C_IMAGE_ID_SAFE_DELETE=ENABLED`
- `EPIC49_3C_IMAGE_LIMIT_10=ENABLED`
- `EPIC49_3C_IMAGE_SEO_METADATA=ENABLED`
- `EPIC49_3C_AI_COMPLETENESS_RECOVERY=ENABLED`
- `ACTIVE_RELEASE_VERIFIED=OK`

## 15) Regression tests

Dedicated module:

`tests.test_epic49_phase49_3c_operator_recovery`

Gateها:

- URL cap = 10.
- canonical duplicate URL حذف می‌شود.
- exact URL→file mapping مستقل از ترتیب فایل‌ها.
- missing URL هرگز به index fallback وصل نمی‌شود.
- SEO filename انسانی و غیرعددی.
- duplicate bytes در Finalize فقط یک خروجی می‌دهد.
- Source images حذف نمی‌شوند.
- Third-party copyright به 3DPrintHub تبدیل نمی‌شود.
- AI fallback short/tags/hashtags/SEO/sales/alts/material recommendations را خالی نمی‌گذارد.
- AI factual price/license جعل نمی‌کند.
- Live debounce/missing panel/stage AI/global AI contract.
- Runtime markers.

CI workflow این تست را Explicit و دوباره داخل Epic49 discovery اجرا می‌کند.

## 16) وضعیت Checklist

- [x] Root causes مشخص شد.
- [x] Live readiness implementation.
- [x] Exact image identity resolver.
- [x] Image intake max 10.
- [x] Exact + visual duplicate filtering.
- [x] Image SEO filename + metadata pipeline.
- [x] Copyright/Attribution safety.
- [x] SEO signature stale protection.
- [x] AI completeness repair.
- [x] Stage AI + Global AI controls.
- [x] Publish fail-closed contract.
- [x] Dedicated regression tests added.
- [x] CI contract updated.
- [ ] GitHub CI final result verified for final Phase49.3C HEAD.
- [ ] Windows pull + dedicated tests.
- [ ] Windows `launch.py --verify-only`.
- [ ] Visual QA on real Fanart/Flexi product.
- [ ] Real AI Provider QA.
- [ ] Image delete identity QA.
- [ ] Image SEO filename/metadata QA.
- [ ] Local Publish E2E.
- [ ] User approval.
- [ ] Production deployment.

## 17) Production status

**NOT DEPLOYED / NOT APPROVED.**

Phase49.3C هیچ Production DB/migrate/collectstatic/restart/deploy اجرا نکرده است.
