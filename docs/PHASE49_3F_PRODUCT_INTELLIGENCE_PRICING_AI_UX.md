# Phase49.3F — Product Intelligence + Dynamic Pricing + AI UX

## وضعیت جاری

- Runtime/Test baseline تأییدشده پیش از Documentation نهایی: `a207ad2c35dd8dbbd10457e0d2295ea8efbb9776`
- Runtime redaction fix commit: `60393e9cd294a8414c2b7945a3a11c54b391d8a1`
- Baseline regression-test commit: `03259f5072f8b902b190aa5bb86bc5b694632ab3`
- Final validation PR: `#35` — CI-only / do not merge
- Final CI Run: `32351795808`
- Final CI Job: `96372355769`
- Result: **SUCCESS**
- Windows Local Gate: **PENDING**
- Manual Windows QA: **PENDING**
- Production: **UNTOUCHED / NOT APPROVED / NOT DEPLOYED**

## هدف

این فاز از Visual QA واقعی Windows و صفحه Product Detail شروع شد. هدف، تبدیل Catalog Center از یک فرم فنی به Workflow شفاف، قابل عیب‌یابی و قابل اعتماد برای اپراتور است، بدون دست‌زدن به Production تا پایان Local QA.

## مشکلات واقعی مشاهده‌شده

1. Image SEO در 49.3E تصاویر منتخب را پیدا می‌کرد اما تا 4 URL تصویر را به AI می‌فرستاد؛ کند و غیرضروری بود.
2. Finalize منتخب‌ها می‌توانست `image_metadata_json` تصاویر خارج از انتخاب را از مجموعه نهایی حذف کند.
3. UI Providerها Scroll مناسب نداشت و Provider/Model/Save در مانیتور کوچک گم می‌شد.
4. Google Gemini Direct Provider مستقل وجود نداشت؛ انتخاب Gemini Lite/Flash-Lite مستقیم از Google AI Studio ممکن نبود.
5. AI action وضعیت اتصال/ارسال/دریافت را برای اپراتور شفاف نشان نمی‌داد.
6. File runtime trace مستقل برای تشخیص کندی/گیرکردن workflow وجود نداشت.
7. توضیحات فنی Product Detail می‌توانست خام/نامفهوم باشد و مسیر Source-grounded review لازم داشت.
8. `source_name/source_attribution` می‌توانست مقدارهایی مثل `Username` را در UI عمومی نشان دهد.
9. `ready_product` و `made_to_order` خام در Product Detail نمایش داده می‌شد.
10. Price range فقط نمایش عدد بود و موتور قیمت حرفه‌ای متریال/زمان/ساپورت/نظارت/Assembly را از Windows دریافت نمی‌کرد.
11. Final CI یک Regression امنیتی در Free-text Runtime Trace پیدا کرد: مقدار واقعی Bearer token بعد از Redaction عمومی `Authorization` باقی می‌ماند.

## قانون تغییر حداقلی این فاز

Phase49.3F مسیرهای Mature قبلی را Replace نمی‌کند:
- Product Workspace قبلی Extend می‌شود.
- Django Admin registry موجود Extend می‌شود.
- Pricing قدیمی با `legacy` حفظ می‌شود.
- Product/Hero/Bridge contract قبلی حفظ می‌شود.
- Image source/cache خارج از انتخاب حذف یا rewrite نمی‌شود.
- Secret storage موجود حفظ می‌شود و فقط Redaction اصلاح می‌شود.

هر Hotfix باید همان Root Cause را اصلاح کند و قابلیت unrelated را تغییر ندهد.

## قرارداد Image SEO جدید

### قانون قطعی

**هیچ Image bytes، فایل تصویر یا URL تصویر برای Task سئو تصاویر به AI ارسال نمی‌شود.**

AI فقط دریافت می‌کند:
- title/description/SEO facts محصول؛
- source specs متنی؛
- شماره Slot تصاویر منتخب؛
- Alt قبلی همان Slot در صورت وجود.

AI برمی‌گرداند:
- `slot`
- `alt_text`
- `title`
- `caption`
- `keywords`

Mapping Slot→URL فقط داخل Windows انجام می‌شود.

### حفاظت تصاویر انتخاب‌نشده

`phase49_3f_selected_image_ai.py`:
- AI override فقط روی selected URLها merge می‌شود.
- `finalize_selected_images()` wrap شده است.
- Metadata رکوردهای خارج از انتخاب قبل از Finalize حفظ و بعد از rebuild منتخب‌ها restore می‌شود.
- Source/cache image خارج از انتخاب حذف یا rewrite نمی‌شود.

## AI Progress UX

هر workflow AI دارای Popup مرحله‌ای است:

1. `🔌 در حال اتصال به هوش مصنوعی…`
2. `✅ اتصال برقرار شد` یا خطای صریح
3. `📤 داده متنی ارسال شد`
4. `📥 پاسخ دریافت شد`
5. `💾 داده اعتبارسنجی/ذخیره شد`
6. مرحله نهایی Task

Connection probe: **30 seconds maximum**.

Failure موفقیت جعلی نشان نمی‌دهد و در DB diagnostics + runtime trace ثبت می‌شود.

## AI Provider Center

Canonical Provider order:
1. AvalAI
2. OpenRouter
3. Google Gemini Direct
4. OpenAI Direct

### Google Gemini Direct

Provider code: `google`

Endpoint base:
`https://generativelanguage.googleapis.com/v1beta`

Security:
- API key با `x-goog-api-key` Header ارسال می‌شود.
- API key در URL endpoint/log قرار نمی‌گیرد.
- secret registry: `GOOGLE_GEMINI_API_KEY` / Windows Credential Store.

Model picker:
- `/models` از Google API.
- فقط مدل‌های دارای `generateContent` نمایش داده می‌شوند.
- search در Model ID/Display Name.
- Gemini Flash-Lite/Lite در صورت موجودبودن برای API key قابل انتخاب است.
- مدل واقعی انتخاب‌شده persist می‌شود.

Structured response:
- JSON MIME + responseSchema در صورت پشتیبانی.
- در rejection سازگار، یک retry با JSON MIME و client-side validation.

Balance:
Google AI Studio standard API key مانده اعتبار قابل اتکا از این API ارائه نمی‌دهد؛ سیستم Balance جعلی نشان نمی‌دهد.

### Scrollable/sticky UX

AI Center:
- sticky top bar: Provider فعال + Model فعال.
- Save active Provider/model همیشه در دید.
- Test 30s همیشه در دید.
- Open Log Folder همیشه در دید.
- Provider cards داخل Canvas با vertical + horizontal scrolling.

## Runtime Trace

Path:
`<persistent catalog data>/logs/phase49_3f/YYYY-MM-DD/workflow-<session>.jsonl`

هر record:
- UTC timestamp / epoch_ms
- session_id
- operator
- workstation
- area/action/status
- product_id
- provider/model
- elapsed_ms
- sanitized message/detail

Redaction:
- Authorization/Bearer
- password
- token/access_token/refresh_token
- api key
- secret
- management/admin key
- nested structured secret keys

هیچ API secret نباید در Diagnostic share باقی بماند.

### Runtime Trace Redaction Hotfix — Root Cause و Fix

Failure واقعی CI قبلی:

```text
Authorization: Bearer very-secret-token
```

Redactor مرکزی ابتدا Pattern عمومی `authorization:<value>` را اجرا می‌کرد. در این رشته، مقدار عمومی فقط کلمه `Bearer` تشخیص داده می‌شد؛ سپس Pattern دوم دیگر عبارت `Bearer <credential>` را نمی‌دید و Credential واقعی باقی می‌ماند.

Fix حداقلی:
- در `catalog_center/app/runtime_logging.py` Pattern مربوط به `Bearer <credential>` قبل از Pattern عمومی secret-key اجرا می‌شود.
- ساختار JSONL، Runtime Trace، identity، Provider، Pricing، DB و Publish تغییر نکرده‌اند.
- تست اصلی Phase49.3F ضعیف/حذف نشد.
- یک Regression Test پایه نیز به `catalog_center/tests/test_v85_core.py` اضافه شد تا `Authorization: Bearer <token>` همیشه کامل Redact شود.

Do Not Repeat:
- Redaction pattern order یک Security Contract است.
- تست امنیتی برای سبزکردن CI نباید relax شود.
- Structured secret redaction و Free-text secret redaction هر دو باید تست مستقل داشته باشند.

Status: **FIXED + CI VERIFIED**.

## Source-grounded Technical Intelligence

Action:
`♻ بازخوانی منبع + ✨ ساخت توضیحات فنی با AI`

Sequence:
1. Save editor state.
2. Start real source refetch.
3. Wait for **`last_refetched_at` change only**.
4. تغییر `updated_at` معمولی success حساب نمی‌شود.
5. Source timeout: 60s؛ در timeout AI اجرا نمی‌شود.
6. بعد از refetch واقعی، extracted text/spec facts به AI داده می‌شود.
7. هیچ تصویر برای این Task ارسال نمی‌شود.
8. AI خروجی فارسی قابل فهم می‌سازد.
9. Operator review قبل از save نهایی.

## Pricing Architecture

### اصل

Product Detail، Cart و Checkout از همان `ProductVariant.price_breakdown()` استفاده می‌کنند. ماشین‌حساب موازی جدا ساخته نشده است.

### Strategy

`ProductCatalogProfile.pricing_strategy`:
- `legacy`: رفتار قبلی بدون تغییر
- `fixed`: قیمت قطعی اپراتور
- `dynamic`: قیمت محاسباتی بر اساس Variant

محصولات قبلی default=`legacy` هستند و خودکار به فرمول جدید مهاجرت نمی‌کنند.

### Dynamic Formula

```text
chargeable_material_grams = part_weight + support_weight * support_cost_multiplier
material_cost = chargeable_material_grams * material_sale_price_per_gram

billable_print_minutes = round_up(
    max(actual_print_minutes, minimum_billable_minutes),
    billing_increment_minutes
)

machine_cost = print_hourly_rate * billable_print_minutes / 60
supervision_cost = supervision_hourly_rate * billable_print_minutes / 60

unit_price_before_discount =
    material_cost
    + machine_cost
    + supervision_cost
    + assembly_cost
    + accessory_sale
    + post_processing_fee
    + fixed_fee
    + color_adjustment
```

Shipping/packaging/tax طبق Checkout موجود و جدا محاسبه می‌شود.

### مثال Acceptance عددی

PLA سفید مات:
- 2,600,000 تومان / kg = 2,600 تومان/g
- part = 100g
- support = 50g
- support multiplier = 2
- actual material = 150g
- chargeable material = 200g
- material = 520,000 تومان
- print = 3h × 150,000 = 450,000 تومان
- supervision = 3h × 50,000 = 150,000 تومان
- assembly/extras = 0

Expected before shipping/extras:
**1,120,000 تومان**

این مقدار با Django test قفل شده است.

### Quality duration

Windows `pricing_inputs_json` می‌تواند چند quality profile داشته باشد؛ مثال:
- Standard = 180 min
- Fine = 360 min

Variant هر quality زمان و قیمت خودش را دارد.

### Material runtime rates

Material:
- `price_per_kg`
- `print_hourly_rate_toman`
- `supervision_hourly_rate_toman`

Windows table:
`material_pricing_rates`

Operator می‌تواند نرخ‌های مواد/چاپ/نظارت را به‌روز کند.

### Assembly

`assembly_fee_override` per Variant؛ default = 0.
BOM assembly rate قبلی همچنان fallback mature engine است.

## Django Schema

### `store.0033_phase49_3f_pricing_intelligence`
AddField only:
- ProductCatalogProfile.pricing_strategy
- ProductCatalogProfile.pricing_inputs
- ProductCatalogProfile.technical_summary_fa
- ProductVariant.part_weight_grams
- ProductVariant.support_weight_grams
- ProductVariant.support_cost_multiplier
- ProductVariant.supervision_hourly_rate_override

### `website.0023_phase49_3f_material_runtime_rates`
AddField only:
- Material.print_hourly_rate_toman
- Material.supervision_hourly_rate_toman

Forbidden destructive operations are CI-gated.

## Django Admin

`store/phase49_3f_admin.py` mature admin registrations را replace نمی‌کند؛ registry موجود را extend می‌کند.

ProductCatalogProfile Admin:
- pricing_strategy
- pricing_inputs
- technical_summary_fa

Material Admin list/edit:
- price_per_kg
- print_hourly_rate_toman
- supervision_hourly_rate_toman

## Public Product Detail

49.3F:
- title/summary compactتر.
- raw `ready_product`/`made_to_order` حذف و Persian label استفاده می‌شود.
- مقدارهایی مثل `Username` به عنوان attribution عمومی نمایش داده نمی‌شوند.
- Source link در صورت مجازبودن generic label دارد.
- Technical Summary بالای جزئیات خام نمایش داده می‌شود.
- fixed price به عنوان قیمت قطعی واضح است.
- dynamic range از همان cached Variant prices استخراج می‌شود.
- Variant selection breakdown: material / machine / supervision / assembly+extras / total.
- Fixed strategy internal dynamic components را به مشتری نشان نمی‌دهد.
- Cart/Checkout همان unit price را مصرف می‌کنند.

## Price cache finalization

Publish flow ممکن است Variant را قبل از final profile strategy بسازد. `phase49_3f_pricing_finalize.py` بعد از final `sync_catalog_profile()`:
- active variants را دوباره recalculate می‌کند؛
- `price_min/price_max` را از همان cached unit prices می‌سازد؛
- fixed→price_mode fixed؛ dynamic→variant؛
- legacy untouched.

## Automated Tests

Django:
`store/test_phase49_3f_pricing.py`
- exact 1,120,000 dynamic formula
- fixed strategy
- legacy compatibility
- Persian labels
- public page no Username/raw codes
- Admin extension
- migration AddField-only safety

Windows:
`catalog_center/tests/test_phase49_3f_product_intelligence.py`
- text-only selected image payload
- no selected image URL in model input
- selected-only metadata merge
- unselected metadata preserved
- Google first-class provider
- Google generateContent model filtering
- runtime trace secret redaction
- source refresh guard based only on last_refetched_at

Base logging regression:
`catalog_center/tests/test_v85_core.py`
- `Authorization: Bearer <credential>` must remove the credential completely.
- ordinary non-sensitive context such as HTTP/status information remains available for diagnostics.

## Canonical Windows Runner

`RUN_PHASE49_3F_LOCAL_GATE.ps1`

Version:
`49.3F.0`

Chain:
`49.3F → 49.3E → 49.3D`

49.3F adds:
- second pre-migration DB backup
- source presence
- compile
- Django check/makemigrations/plan
- destructive migration scan
- targeted apply 0033/0023
- Phase49.3F Django tests
- Phase49.3F Windows tests
- launcher marker verification
- full Django suite
- final clean Git safety

No reset/delete/production action is present.

## Final CI — Redaction Hotfix Verified

Validation-only PR: `#35` — do not merge.

Final CI:
- Run: `32351795808`
- Job: `96372355769`
- PowerShell runner contract: [x]
- Compile: [x]
- Django check: [x]
- `makemigrations --check --dry-run`: [x]
- Migration AddField-only gate: [x]
- Targeted Django: [x] **69/69 PASS**
- Phase49.3F Windows dedicated: [x] **7/7 PASS**
- Existing Phase49.3B diagnostics: [x] **7/7 PASS**
- Diagnostic identity: [x] **3/3 PASS**
- Epic49 Windows discovery: [x] **84/84 PASS**
- Launcher markers: [x]
- `ACTIVE_RELEASE_VERIFIED=OK`: [x]
- Full Django: [x] **415 PASS, 2 skipped**
- Overall SUCCESS: [x]

Markerهای اصلی 49.3F که در Final CI تأیید شدند:
- `EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED`
- `EPIC49_3F_UNSELECTED_IMAGE_METADATA_PRESERVED=ENABLED`
- `EPIC49_3F_AI_PROGRESS_TIMEOUT=ENABLED`
- `EPIC49_3F_SCROLLABLE_AI_CENTER=ENABLED`
- `EPIC49_3F_GOOGLE_GEMINI_DIRECT=ENABLED`
- `EPIC49_3F_RUNTIME_TRACE=ENABLED`
- `EPIC49_3F_SOURCE_GROUNDED_TECHNICAL_AI=ENABLED`
- `EPIC49_3F_DYNAMIC_PRICING=ENABLED`
- `AI_PROFILE_MIGRATION=PRESERVED`
- `HOST_PROFILE_MIGRATION=PRESERVED`
- `ACTIVE_RELEASE_VERIFIED=OK`

Warnings غیر-Failure در CI:
- `3dprinthub.W001`: Google membership credentials خالی است.
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: in-memory realtime برای multi-process production کافی نیست.
- Pillow `Image.getdata()` deprecation برای refactor آینده.

هیچ‌کدام blocker این Hotfix نیستند و برای رفعشان هیچ معماری unrelated در این فاز بازنویسی نمی‌شود.

## Windows Manual Acceptance after automated PASS

- [ ] Pull دقیق Epic روی `D:\projects\3DPrintHub`.
- [ ] اجرای `RUN_PHASE49_3F_LOCAL_GATE.ps1` از Repository.
- [ ] Local backup Django DB + Catalog DB توسط Runner.
- [ ] migration `store.0033` و `website.0023` روی Local فقط به‌صورت Additive اعمال/تأیید شوند.
- [ ] AI Center scrolling/sticky controls.
- [ ] Gemini Direct model list/search/select/save/test با real key.
- [ ] selected Image SEO: هیچ image/file/url به AI ارسال نشود و فقط metadata تصاویر منتخب تغییر کند.
- [ ] unselected metadata survives.
- [ ] Runtime log folder وجود داشته باشد و هیچ secret واقعی در آن نباشد.
- [ ] source refetch + technical AI review فقط بعد از تغییر واقعی `last_refetched_at`.
- [ ] pricing rate editing + **1,120,000 تومان** acceptance preview.
- [ ] alternate quality duration changes price.
- [ ] assembly default 0 / editable.
- [ ] یک Product واقعی **LOCAL PUBLISH ONLY**.
- [ ] Product Detail Persian labels / no Username / compact copy / technical summary.
- [ ] Product Detail unit price == Cart/Checkout unit price.
- [ ] Local Django Product/Profile/Hero/Home/Admin verification.
- [ ] explicit user approval.
- [ ] Production deploy فقط بعد از approval.

## مسیر بعدی

کدنویسی Hotfix فعلی تمام و CI-verified است. مرحله بعد:

```text
Windows pull exact Epic HEAD
→ RUN_PHASE49_3F_LOCAL_GATE.ps1
→ automated Local PASS
→ manual AI/Image/Pricing/Product QA
→ one real LOCAL PUBLISH ONLY
→ Local Django E2E verify
→ explicit user approval
→ Production plan/deploy
```

تا قبل از تأیید صریح Local، هیچ `deploy/migrate/collectstatic/restart` مربوط به Phase49.3F روی Production اجرا نمی‌شود.

## Production

**UNTOUCHED / NOT APPROVED / NOT DEPLOYED.**
