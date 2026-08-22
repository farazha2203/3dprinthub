# Phase49.3G — Workspace Usability + AI Autofill Provenance

## وضعیت

- Branch: `epic/phase49-unified-product-slider-sync`
- Scope: **Windows Catalog Center Workspace UX + AI ownership/provenance**
- Pricing engine: **PRESERVED**
- Product/Hero/Bridge/Publish contracts: **PRESERVED**
- Django models/migrations: **NO NEW DJANGO MIGRATION**
- Production: **UNTOUCHED / NOT APPROVED**
- Windows Local/Visual QA: **PENDING**
- `$django-admin-expert`: در Session فعلی Plugin/Skill متناظر پیدا نشد؛ unavailable ثبت شده و هیچ ادعای نصب وجود ندارد.

---

## 1) Requested Delta — درخواست کاربر

مشکلات واقعی از اسکرین‌شات Windows:

1. صفحه Product Workspace به علت قد زیاد فرم‌ها قابل Scroll کامل نبود و پایین فرم سفارش/قیمت در دسترس نبود.
2. Boxها و جدول قیمت‌گذاری بیش از حد بلند و فشرده بودند.
3. Gallery تصاویر در Product Workspace با تعداد زیاد تصویر بد نمایش داده می‌شد و Navigation مناسب نداشت.
4. اپراتور یک دکمه واحد برای «پر کردن هوشمند محصول» می‌خواهد تا AI وظایف مجاز و ناقص را تکمیل کند.
5. باید روی خود بخش مشخص باشد که چه چیزی توسط AI تکمیل شده است.
6. اپراتور باید بتواند AI را برای هر گروه خاموش کند.
7. اگر اپراتور مقدار AI را دستی تغییر داد، AI دیگر حق overwrite نداشته باشد مگر اپراتور صریحاً اجازه بازنویسی بدهد.
8. Image SEO همچنان فقط برای تصاویر منتخب و بدون ارسال image bytes/file/image URL به AI باشد.

---

## 2) Must-Not-Touch

این فاز حق تغییر یا حذف این قراردادها را ندارد:

- `ProductVariant.price_breakdown()` و قیمت Fixed/Dynamic/Legacy.
- Product Detail == Cart/Checkout price source.
- Local/Production Publish separation.
- Production fail-closed.
- Product/Profile/Hero revision contract.
- Bridge idempotency و stale write guards.
- AI Provider Hub / Gemini Direct / Runtime Trace 49.3F.
- 49.3F selected-image **text-only** Image SEO.
- unselected image metadata preservation.
- Persian content guards.
- 7-stage Readiness navigation.
- Django/Admin/Host schemaهای تجاری موجود.

---

## 3) Root Cause — Workspace Scroll

Workspace Mature، `Notebook` را مستقیماً داخل `notebook_host` با `pack(fill="both", expand=True)` قرار می‌داد. خود Pageهای Commerce/Images از ترکیب `grid`/`pack` داخلی استفاده می‌کنند ولی **هیچ Scroll Controller سطح Workspace** وجود نداشت. وقتی Commerce با Dynamic Pricing/Material Rate بزرگ شد، ارتفاع موردنیاز از viewport مانیتور بیشتر شد و اپراتور به پایین صفحه دسترسی نداشت.

### Fix

49.3G همان Notebook موجود را حفظ می‌کند؛ Editor دوم یا Tab موازی ساخته نمی‌شود.

- Notebook از pack مستقیم همان host جدا می‌شود.
- در همان host با `place` کنترل می‌شود.
- Vertical scrollbar واقعی در کنار Workspace قرار می‌گیرد.
- `MouseWheel` صفحه را حرکت می‌دهد.
- `Text`, `Listbox`, `Treeview`, `Canvas` scroll داخلی خود را حفظ می‌کنند.
- تغییر Stage scroll را به بالای همان Page برمی‌گرداند.
- Rail سمت راست بیرون از content viewport باقی می‌ماند و قابل دسترسی است.

---

## 4) Root Cause — Gallery تصاویر

Gallery Mature:

- Canvas عمودی داشت.
- Cardها با Grid چندستونه چیده می‌شدند.
- در تعداد زیاد تصویر، Cardها فشرده/چندردیفه شده و مرور محصول سخت می‌شد.

### Fix

همان `gallery_canvas`, `gallery_inner`, cardها و actionهای موجود Preserve شده‌اند:

- Gallery به **یک ردیف افقی** تبدیل شده است.
- Thumbnail cardها min-width کنترل‌شده دارند.
- Horizontal scrollbar قابل مشاهده اضافه شده است.
- Mouse wheel داخل Gallery حرکت افقی می‌دهد.
- position افقی هنگام refresh تا حد ممکن حفظ می‌شود.
- selected/site/primary/slider/delete/open behavior قبلی دست‌نخورده است.

---

## 5) Compact Commerce

برای اینکه Workspace حتی قبل از Scroll هم خواناتر باشد:

- `use_description_text`: height 3
- `materials_text`: height 3
- `colors_text`: height 3
- `technical_features_text`: height 5
- `keywords_text`: height 5
- `material_rate_tree`: height 4
- Pricing panel padding کمتر
- rowهای Commerce دیگر بی‌دلیل expand نمی‌شوند.

این تغییر Presentation است؛ هیچ فرمول قیمت یا مقدار تجاری را تغییر نمی‌دهد.

---

## 6) AI Autofill — مسیر Mature، نه Workflow موازی

Action canonical:

```text
✨ تکمیل هوشمند محصول با AI
```

این دکمه Workflow جدید جدا نمی‌سازد؛ همان `phase49_3e_ai_task_center` و Provider/Model فعال 49.3F را اجرا می‌کند.

### AI می‌تواند روی Taskهای مجاز کار کند

- متن فارسی محصول
- SEO محصول
- SEO/Metadata تصاویر منتخب
- پیشنهاد متریال
- SEO اسلایدر فقط وقتی Slider فعال است

### AI حق ندارد خودکار تغییر دهد

- قیمت قطعی
- تأیید فروش
- موجودی واقعی
- مجوز تجاری/حقوقی
- Production Publish

Commerce page این Guard را صریحاً به اپراتور نمایش می‌دهد.

---

## 7) AI Provenance / Ownership

دو ستون Additive فقط در **Catalog SQLite محلی** ایجاد می‌شوند:

```text
ai_provenance_json
ai_disabled_groups_json
```

این‌ها Django migration نیستند چون Provenance، داده عملیاتی اپراتور Windows است و نباید بی‌دلیل وارد Schema تجاری Production شود.

Groupها:

```text
persian_content
product_seo
image_seo
materials
slider_seo
```

Provenance برای AI write موفق ثبت می‌کند:

- source=`ai`
- provider
- model
- timestamp
- changed fields
- semantic snapshot hash
- manual_override=false

UI وضعیت را به‌شکل قابل فهم نشان می‌دهد:

```text
🤖 توسط AI / Provider / Model
✎ ویرایش دستی؛ AI قفل
⛔ AI خاموش
○ هنوز مالکیت AI ثبت نشده
```

Task Center نیز suffix مالکیت را کنار وضعیت Task نشان می‌دهد.

---

## 8) Manual Override Guard

بعد از AI write یک semantic snapshot از همان گروه ذخیره می‌شود.

اگر اپراتور بعداً Save کند و مقدار گروه نسبت به snapshot عوض شده باشد:

```text
source = manual
manual_override = true
allow_ai_rewrite = false
```

از آن لحظه `build_ai_updates()` قبل از DB write، fieldهای همان گروه را از AI update حذف می‌کند.

فقط دکمه:

```text
اجازه بازنویسی AI
```

قفل را آگاهانه باز می‌کند.

دکمه:

```text
خاموش/روشن AI
```

گروه را مستقل در `ai_disabled_groups_json` فعال/غیرفعال می‌کند.

---

## 9) Commerce Provenance

در صفحه سفارش/قیمت یک Panel مستقل اضافه شده است:

```text
مالکیت AI در سفارش و قیمت
```

برای Group `materials` همان controls زیر وجود دارد:

- خاموش/روشن AI
- اجازه بازنویسی AI

و یک Guard visible:

```text
قیمت قطعی، تأیید فروش، موجودی، مجوز و Production همیشه اپراتوری هستند.
```

Module:
`catalog_center/app/phase49_3g_commerce_provenance.py`

این Module هیچ `final_price_var.set`, `approved_var.set`, `license_var.set` ندارد و Presentation-only است.

---

## 10) Image SEO Privacy — قرارداد 49.3F حفظ شد

Phase49.3G Image SEO engine جدید نمی‌سازد.

همچنان:

- فقط Selected image slots پردازش می‌شوند.
- `input_image` ارسال نمی‌شود.
- Image bytes/file ارسال نمی‌شود.
- Image URL به AI ارسال نمی‌شود.
- Mapping slot→URL فقط Local است.
- Metadata تصویر انتخاب‌نشده Preserve می‌شود.

Regression test این Contract را قفل می‌کند.

---

## 11) Composition Boundary Incident — Do Not Repeat

### Failure در اولین Main CI

Dedicated 49.3G CI سبز بود، ولی Main Phase49 در Windows Catalog regression fail شد.

### Root Cause

نسخه اولیه 49.3G را داخل:

`phase49_3f_source_refresh_guard.install()`

زنجیر کرده بود.

تست مستقل 49.3F Source Refresh عمداً یک Workspace stub حداقلی دارد که فقط contract همان Guard را تست می‌کند. نصب 3G داخل Module 3F باعث شد 3G روی stub فاقد `reload/save/...` نصب شود.

### Fix درست

- `phase49_3f_source_refresh_guard.py` دوباره مستقل شد.
- 49.3G فقط در `catalog_center/launch.py` و در **Composition Root واقعی** نصب می‌شود.
- ترتیب:

```text
49.3F Workspace
→ 49.3F Source Refresh Guard
→ 49.3G Workspace Usability
→ 49.3G Commerce Provenance
```

- Regression test قفل می‌کند که 3G دوباره داخل Source Guard 3F وارد نشود.

### Do Not Repeat

Feature جدید را داخل installer یک Module مستقل قدیمی زنجیر نکن اگر آن Module contract/unit-test مستقل دارد. Cross-phase composition باید در Launcher/Composition Root انجام شود.

---

## 12) Files

Runtime:

- `catalog_center/app/phase49_3g_workspace_usability.py`
- `catalog_center/app/phase49_3g_commerce_provenance.py`
- `catalog_center/launch.py`

Tests:

- `catalog_center/tests/test_epic49_phase49_3g_workspace_usability.py`
- `catalog_center/tests/test_epic49_phase49_3g_commerce_provenance.py`

CI/Windows:

- `.github/workflows/phase49-3g-workspace-usability-ci.yml`
- `RUN_PHASE49_3G_LOCAL_GATE.ps1`

---

## 13) Launcher markers

```text
EPIC49_3G_WORKSPACE_VERTICAL_SCROLL=ENABLED
EPIC49_3G_GALLERY_HORIZONTAL_SCROLL=ENABLED
EPIC49_3G_COMPACT_COMMERCE=ENABLED
EPIC49_3G_AI_AUTOFILL_PROVENANCE=ENABLED
EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED
EPIC49_3G_AI_DISABLE_PER_GROUP=ENABLED
EPIC49_3G_COMMERCE_PROVENANCE=ENABLED
```

Existing safety marker نیز باید بماند:

```text
EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED
ACTIVE_RELEASE_VERIFIED=OK
```

---

## 14) Validation history

### First probe — boundary bug caught before Windows

PR `#37` validation-only / Do Not Merge.

Dedicated 3G:
- Run `32560710057`
- Job `97001716989`
- SUCCESS

Main Phase49:
- Run `32560710088`
- Job `97001717026`
- FAILURE in Windows Catalog regression
- Root cause: bad 3G→3F Source Guard composition boundary
- Full Django skipped because prior gate failed.

### Second probe — boundary fix

Dedicated 3G:
- Run `32560880689`
- Job `97002113015`
- SUCCESS

Main Phase49:
- Run `32560880675`
- Job `97002113079`
- SUCCESS through Full Django

### Final runtime probe — includes Commerce Provenance

Dedicated 3G:
- Run `32561222101`
- Job `97002924663`
- **SUCCESS**

Main Phase49:
- Run `32561222090`
- Job `97002924583`
- Final conclusion: **PENDING WHILE THIS DOCUMENT WAS CREATED**
- At document creation: PowerShell/Compile/Django/Migration/Targeted/Windows Epic49 all PASS; Full Django still running.

---

## 15) Windows Runner

Canonical:

`D:\projects\3DPrintHub\RUN_PHASE49_3G_LOCAL_GATE.ps1`

Version:

`49.3G.0`

Chain:

```text
49.3G
→ full 49.3F.1 gate
→ 49.3E
→ 49.3D.1
```

Runner:

- Production را لمس نمی‌کند.
- migration جدید Django اجرا نمی‌کند.
- 49.3F migration state را از Base Gate verify می‌کند.
- 3G source/test files را verify می‌کند.
- compile 3G را اجرا می‌کند.
- dedicated tests را اجرا می‌کند.
- launcher markers را verify می‌کند.
- clean git status نهایی را enforce می‌کند.

---

## 16) Manual Windows Acceptance — هنوز انجام نشده

- [ ] Scroll عمودی Commerce/Product با Mouse Wheel و scrollbar قابل مشاهده.
- [ ] Stage rail در طول Scroll قابل دسترسی بماند.
- [ ] Pricing/Commerce compact و پایین صفحه قابل دسترسی باشد.
- [ ] Images یک ردیف افقی با scrollbar باشد.
- [ ] تمام actionهای قبلی Card تصویر سالم باشند.
- [ ] دکمه `✨ تکمیل هوشمند محصول با AI` دیده و قابل اجرا باشد.
- [ ] AI فقط Taskهای ناقص و مجاز را پر کند.
- [ ] Task Center مالکیت AI/manual/disabled را نشان دهد.
- [ ] صفحه Content/Images/Slider Provenance panel داشته باشد.
- [ ] Commerce برای Material AI Provenance panel داشته باشد.
- [ ] یک Group خاموش شود و اجرای AI آن را تغییر ندهد.
- [ ] یک field AI دستی تغییر + Save شود و Group به Manual override تبدیل شود.
- [ ] AI دوباره Manual override را overwrite نکند.
- [ ] `اجازه بازنویسی AI` قفل را صریحاً آزاد کند.
- [ ] Image SEO فقط Selected و Text-only بماند.
- [ ] unselected image metadata تغییر نکند.
- [ ] قیمت/مجوز/تأیید فروش/Production به‌صورت خودکار توسط AI تغییر نکند.
- [ ] فقط بعد از QA، یک `LOCAL PUBLISH ONLY` واقعی اجرا شود.
- [ ] Production تا تأیید صریح کاربر دست‌نخورده بماند.

---

## 17) Current state

```text
Implementation: COMPLETE
Dedicated 49.3G CI: SUCCESS
Main Phase49 regression before final commerce addition: SUCCESS
Final Main Phase49 regression: Full Django still running at documentation time
Windows 49.3G Local Gate: PENDING
Manual Visual/Data QA: PENDING
Local Publish: PENDING
Production: UNTOUCHED
```
