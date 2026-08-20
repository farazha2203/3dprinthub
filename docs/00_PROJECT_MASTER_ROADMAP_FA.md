# 3DPrintHub — نقشه مادر پروژه، خواسته‌ها، معماری، خطاها و Guardهای جلوگیری از Regression

> **این فایل باید قبل از شروع هر فاز، Hotfix، تغییر UI، Migration، تغییر Sync یا Deploy خوانده شود.**
>
> هدف این سند روشن نگه‌داشتن مسیر پروژه، جلوگیری از کد تکراری/موازی، ثبت خطاها و روش رفعشان، و حفاظت از قابلیت‌های قبلی در هر ارتقا است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه جاری:** `epic/phase49-unified-product-slider-sync`  
**زبان اصلی پروژه:** Python / Django  
**ابزار اصلی اپراتور:** Windows Catalog Center  
**ابزار مدیریتی دوم:** Django Admin  
**Production:** تا عبور کامل Local QA و تأیید صریح کاربر ممنوع است.

---

## 1) قانون مادر تغییرات — Preserve Existing Behavior / Minimal Change

این قانون برای تمام توسعه‌های بعدی الزام‌آور است:

1. **تغییر جدید نباید قابلیت قبلی سالم را حذف، Replace یا بی‌اثر کند مگر درخواست صریح کاربر وجود داشته باشد.**
2. مسیر Mature موجود باید **Extend / Patch / Wrap** شود؛ مسیر موازی جدید فقط وقتی مجاز است که معماری موجود واقعاً پاسخگو نباشد و دلیل آن مستند شود.
3. برای رفع Bug، Root Cause همان Boundary/Contract/Module اصلاح می‌شود؛ کل UI/Model/Sync/Admin بازنویسی نمی‌شود.
4. رفتار Default قبلی حفظ می‌شود مگر درخواست جدید دقیقاً Default دیگری بخواهد. نمونه: محصولات قدیمی روی `pricing_strategy=legacy` باقی می‌مانند.
5. هر Task قبل از اجرا باید چهار چیز داشته باشد:

```text
Requested Delta  = دقیقاً چه چیزی باید تغییر کند
Touched Surfaces = فایل/مدل/رابط‌های لازم
Must-Not-Touch   = قابلیت‌های سالمی که نباید تغییر کنند
Regression Tests = تست‌هایی که حفظ رفتار قبلی را اثبات می‌کنند
```

6. هر Bugfix باید Regression Test داشته باشد؛ تستی که Bug واقعی را پیدا کرده برای سبزکردن CI حذف یا ضعیف نمی‌شود.
7. Migration در حالت عادی Additive-first است. حذف/rename destructive فقط در فاز مستقل، با Backup/Dry Run و تأیید صریح مجاز است.
8. `reset --hard`، حذف DB، `DROP`, `TRUNCATE`, حذف `.env`, media/private_media یا Catalog persistent data راه‌حل عادی خطای کد/Deploy نیست.
9. Source of Truth کد GitHub است؛ Patch دستی Windows/Host مبنای پروژه نیست.
10. Production فقط بعد از تأیید صریح Local/Visual/Data QA اجرا می‌شود.

---

## 2) ترتیب Source of Truth

هنگام اختلاف اطلاعات:

1. Migration state واقعی محیط موردنظر.
2. جدیدترین خروجی واقعی CI / Local Gate / Host Verification.
3. این فایل: `docs/00_PROJECT_MASTER_ROADMAP_FA.md`.
4. `PROJECT_CONTEXT.md`.
5. سند مخصوص جدیدترین Phase در `docs/`.
6. Runtime code + tests همان Feature.
7. اسناد تاریخی قدیمی‌تر.

اسناد مهم:
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

## 3) خواسته‌های اصلی کاربر — طبقه‌بندی‌شده

### 3.1) سیاست توسعه و تحویل

- توسعه فازبه‌فاز، قابل ردگیری و تست‌شده باشد.
- هر تغییر ابتدا روی GitHub ثبت شود؛ Windows فقط Pull کند.
- Local کامل تست شود؛ سپس با تأیید صریح کاربر Production.
- مسیر نصب، DB، Host، خطاها، Root Cause، Fix، تست و وضعیت هر فاز در GitHub مستند شود.
- وقتی یک فاز خطا دارد، مشکل کامل حل شود و نیمه‌کاره رها نشود.
- هیچ ZIP/Script/Hotfix خارج از GitHub Source of Truth مبنای اجرا نباشد.

### 3.2) حفاظت قابلیت‌های قبلی

- پنل‌ها و Workflowهای سالم قبلی حفظ شوند.
- تغییر جدید فقط همان قسمت درخواستی را تغییر دهد.
- ارتباط بین ماژول‌ها اصلاح شود بدون به‌هم‌زدن کلیات معماری.
- DB، تصاویر، media، تنظیمات و داده‌های واقعی بدون دلیل Reset/Delete نشوند.
- Product، Hero، Pricing، Cart/Checkout و AI workflowهای موجود fork موازی نشوند.

### 3.3) Product Workspace / Wizard

Canonical workflow:
1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

الزامات:
- وضعیت کامل/ناقص واضح باشد.
- همه Stageها قابل مراجعه و اصلاح باشند؛ از 49.3E به بعد Readiness راهنما است، نه زندان.
- Local Publish از Production Publish کاملاً جدا باشد.
- Publish failure دلیل دقیق بدهد؛ Silent failure ممنوع.
- Production بدون Readiness کامل و تأیید صریح اجرا نشود.

### 3.4) AI Provider Hub

Providerهای Canonical:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

الزامات:
- تنظیم، Key، Model و Test هر Provider مستقل.
- Provider/Model فعال یک Source of Truth داشته باشد.
- Search/Filter مدل و raw model ID persistence.
- Balance فقط اگر Provider API واقعی دارد؛ عدد جعلی ممنوع.
- Request ID/token/cost در صورت پشتیبانی ثبت شود.
- API Key/Management Key/Admin Key در Git/SQLite diagnostic/export ثبت نشود.
- AvalAI/OpenRouter در rejection `response_format` یک fallback کنترل‌شده داشته باشند.

### 3.5) Image SEO / Metadata

- AI فقط درباره تصاویر انتخاب‌شده کار کند.
- **Image bytes، فایل تصویر و URL تصویر برای Image SEO به AI ارسال نشود.**
- Mapping Slot→URL فقط Local باشد.
- Metadata تصاویر انتخاب‌نشده حفظ شود.
- Exact identity استفاده شود؛ index guessing ممنوع.
- `download_image_limit` per-product حفظ شود؛ hard cap فعلی 10.
- Source/cache image به‌خاطر finalize حذف نشود.

### 3.6) Persian Content / SEO

- English source fallback برای Persian editorial ممنوع.
- Product SEO و Slider SEO مستقل بمانند.
- AI حق جعل قیمت، مجوز، ابعاد، موجودی، متریال یا رنگ را ندارد.
- raw codeهایی مانند `ready_product`, `made_to_order` و attribution داخلی مانند `Username` در Public UI/SEO/JSON-LD نمایش داده نشوند.

### 3.7) Hero / Slider

- Hero متصل به همان Product/Asset باشد.
- تصویر فقط از همان Asset/Product انتخاب شود.
- Effect/Timing قبلی حفظ شود.
- `product_fit + contain` Default امن Product.
- focal/scale/X/Y/background/blur/desktop/mobile controls حفظ شوند.
- Product Profile و Hero revision مستقل و conflict-safe باقی بمانند.

### 3.8) Pricing

Strategyها:
- `legacy`: رفتار قبلی بدون تغییر.
- `fixed`: قیمت قطعی اپراتور.
- `dynamic`: محاسباتی بر اساس Variant.

Source of Truth قیمت Dynamic همان `ProductVariant.price_breakdown()` و cache نهایی Variant است؛ Product Detail، Cart و Checkout نباید ماشین‌حساب موازی داشته باشند.

Acceptance ثابت:

```text
PLA = 2,600,000 تومان/kg = 2,600 تومان/g
Part = 100g
Support = 50g × multiplier 2
Chargeable = 200g
Material = 520,000
Print = 3h × 150,000 = 450,000
Supervision = 3h × 50,000 = 150,000
Expected before extras/shipping = 1,120,000 تومان
```

---

## 4) مسیر طی‌شده

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
→ 49.3F Product Intelligence / Dynamic Pricing / AI UX
→ 49.3F Runtime Trace Redaction Hotfix
```

### قابلیت‌های حفاظت‌شده که نباید Regression شوند

- Windows Catalog Center ابزار اصلی اپراتور.
- Django Admin ابزار مدیریتی دوم.
- Unified Product/Hero/Bridge contract.
- Product Revision و Hero Revision مستقل.
- stale Windows write → HTTP 409.
- `batch_uuid + source_hash` idempotency.
- Persian Hero + Effect/Timing.
- Material/Color operator options.
- Local/Production Publish separation.
- Readiness + exact blocker reasons.
- AI Provider Hub + persistent diagnostics.
- Exact image identity + unselected metadata preservation.
- Persian Content Guard.
- Price Range legacy compatibility + Dynamic pricing.
- Product Detail / Cart / Checkout price consistency.

---

## 5) معماری End-to-End

### مسیر اپراتور

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

اصل: اگر Sync ناقص است همان Contract Extend می‌شود؛ DB/Endpoint/Model موازی برای مفهوم موجود ساخته نمی‌شود.

---

## 6) Windows / Local Structure

```text
Project root:
D:\projects\3DPrintHub

Virtualenv:
D:\projects\3DPrintHub\.venv

Catalog Center source:
D:\projects\3DPrintHub\catalog_center

Django local DB:
D:\projects\3DPrintHub\db.sqlite3

Persistent Catalog:
D:\projects\3dprinthub-catalog-manager

Retained legacy persistent area:
D:\projects\3dprinthub_catalog_center

Catalog DB:
D:\projects\3dprinthub-catalog-manager\catalog.sqlite3

Backups:
D:\projects\3dprinthub-backups
```

Secrets: Windows Credential Store / Environment variables. Secret در Git/SQLite audit/diagnostic export ذخیره نمی‌شود.

Canonical runner فعلی:
`D:\projects\3DPrintHub\RUN_PHASE49_3F_LOCAL_GATE.ps1`

Chain:
`49.3F → 49.3E → 49.3D`

Runner باید exact remote Epic HEAD، clean worktree، backup، migration safety، tests و launcher markers را Fail-closed بررسی کند.

---

## 7) Production / Host Structure

```text
Project:
/home/sfkilvrs/3dprinthub

Python venv:
/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python

Production DB:
MySQL sfkilvrs_EmiAdmin_3dprinthub

Static default:
/home/sfkilvrs/public_html/static

Media default:
/home/sfkilvrs/public_html/media

Private media fallback:
/home/sfkilvrs/3dprinthub/private_media
```

`.env` ممکن است Static/Media/Private paths را Override کند؛ قبل از Deploy Runtime settings واقعی خوانده شود.

### DB Guard

در `config/settings.py` اگر `DB_NAME` خالی باشد Django به SQLite fallback می‌کند. بنابراین Production migration فقط وقتی مجاز است که:

```text
connection.vendor == mysql
DB name == expected production DB
```

اگر Production ناخواسته SQLite دید، Deploy متوقف می‌شود.

### Passenger Restart

```bash
mkdir -p tmp
touch tmp/restart.txt
```

Restart بدون runtime verification و HTTP smoke test کافی نیست.

---

## 8) Runbook امن Production

فقط بعد از Local approval:

```text
1. git status / branch / exact expected HEAD
2. Backup .env
3. Backup pending imports
4. Django check
5. makemigrations --check --dry-run
6. Assert vendor=mysql + expected DB
7. mysqldump قبل از migration
8. migrate --plan
9. migrate --noinput
10. collectstatic --noinput
11. Passenger restart
12. runtime verifier
13. HTTP smoke tests
14. Product/Home/Admin/Cart checks مرتبط
15. DB/Data/Media safety check
16. ثبت نتیجه در docs + PROJECT_CONTEXT
```

`mysqldump` وجود نداشته باشد یا fail شود → Migration اجرا نمی‌شود. Password در command line/log چاپ نمی‌شود. `utf8mb4` حفظ می‌شود.

`deploy/phase48-deploy.sh` مسیر پایه اثبات‌شده است؛ `deploy/phase49-deploy.sh` آن را reuse می‌کند.

---

## 9) Error / Incident Ledger — خطاهای حل‌شده

### 9.1) Tkinter pack/grid collision

Symptom: `TclError: cannot use geometry manager pack ... already has slaves managed by grid`  
Root Cause: یک parent مشترک همزمان `grid` و `pack`.  
Fix: geometry manager همان parent حفظ شد؛ holder داخلی parent جدا دارد.  
Do Not Repeat: قبل از افزودن Widget، manager همان parent بررسی شود.  
Status: **FIXED + Regression test**.

### 9.2) AI model display label به‌جای raw ID

Root Cause: Label نمایشی می‌توانست persist شود.  
Fix: فقط raw model ID persist.  
Status: **FIXED + test**.

### 9.3) Silent Local Publish blocker

Root Cause: `notify=False` دلیل Readiness failure را پنهان می‌کرد.  
Fix: Save → Readiness → optional image finalize → Readiness → exact dialog/audit.  
Status: **FIXED**.

### 9.4) Image SEO false-stale

Root Cause: hash روی raw JSON serialization (`\uXXXX` در برابر UTF-8).  
Fix: semantic JSON normalize قبل از signature.  
Status: **FIXED + test**.

### 9.5) Image index guessing

Risk: ویرایش/حذف metadata تصویر اشتباه.  
Fix: exact URL/file/manifest identity.  
Status: **FIXED + tests**.

### 9.6) Test وابسته به runtime monkey patch

Root Cause: `inspect.getsource()` روی method wrapped و test-order dependency.  
Fix: Source contract از فایل canonical.  
Status: **FIXED**.

### 9.7) AvalAI HTTP400 روی `response_format`

Fix: یک retry بدون `response_format` + client-side JSON validation.  
Do Not Repeat: Provider capability-aware behavior.  
Status: **FIXED + test**.

### 9.8) `updated_at` به‌جای real source refresh

Fix: فقط تغییر `last_refetched_at` success محسوب می‌شود.  
Status: **FIXED + test**.

### 9.9) Price Range `consultation_required=True` overwrite

Root Cause: Phase43 state درست قبلی را دوباره False می‌کرد.  
Fix: True قبلی preserve؛ مرحله بعد فقط requirement اضافه می‌کند.  
Status: **FIXED + E2E test**.

### 9.10) raw codes / Username در Public output

Fix: Persian labels + filtering attribution داخلی در HTML/SEO contract.  
Status: **FIXED + public tests**.

### 9.11) Product/Cart price divergence risk

Fix: Variant cache finalization؛ Range از همان cached unit prices.  
Status: **GUARDED + tests**.

### 9.12) Windows temp SQLite file lock

Root Cause: test connection قبل از `TemporaryDirectory` cleanup بسته نمی‌شد.  
Fix: explicit `db.conn.close()` در `finally`.  
Status: **FIXED + CI**.

### 9.13) `sync_seo_reference_lists` ImportError در Launcher

Root Cause: runtime فایل، inner hook نصب‌شده روی Workspace را به‌اشتباه module-level symbol فرض کرده بود.  
Fix: callable workspace hook از `_phase49_sync_reference_lists` resolve می‌شود.  
Status: **FIXED + import regression test**.

### 9.14) Phase49.3F Runtime Trace inline Bearer secret leak

Failure قبلی:

```text
Authorization: Bearer very-secret-token
→ Authorization: *** very-secret-token ...
```

Root Cause: Pattern عمومی `authorization:<value>` قبل از Bearer pattern اجرا می‌شد و فقط کلمه `Bearer` را mask می‌کرد؛ credential واقعی tail باقی می‌ماند.

Fix:
- در `catalog_center/app/runtime_logging.py` اول `Bearer <credential>` Redact می‌شود، سپس generic secret-key pattern.
- Runtime Trace schema/JSONL/identity/AI Center/Pricing/DB/Publish تغییر نکرد.
- تست اصلی Phase49.3F حفظ شد و همان تست اکنون PASS است.
- `catalog_center/tests/test_v85_core.py` نیز direct Bearer regression دارد.

Commits:
- Fix: `60393e9cd294a8414c2b7945a3a11c54b391d8a1`
- Regression: `03259f5072f8b902b190aa5bb86bc5b694632ab3`

Status: **FIXED + FINAL CI VERIFIED**.

---

## 10) Host Errors / Do-Not-Repeat

- Production migration روی SQLite fallback ممنوع؛ vendor/name قبل از migration assert شود.
- Migration بدون DB backup ممنوع.
- `mysqldump` fail/missing → Deploy Stop.
- Python عمومی Host استفاده نشود؛ venv پروژه استفاده شود.
- تغییر Static → `collectstatic` فراموش نشود.
- Restart بدون runtime verify/HTTP smoke کافی نیست.
- Dirty host tree با `reset --hard` خودکار پاک نشود؛ منشأ تغییر بررسی شود.
- Warning با Failure اشتباه نشود.

Warnings شناخته‌شده:
- `3dprinthub.W001`: Google membership credentials خالی.
- `ckeditor.W001`: CKEditor4 security/maintenance debt.
- `store.W026`: in-memory realtime برای cross-process کافی نیست؛ Redis/polling strategy لازم است.
- Pillow `Image.getdata()` deprecation.

این Warningها بدهی‌های جدا هستند و بهانه بازنویسی unrelated نیستند.

---

## 11) Phase49.3F — Final GitHub CI State

Validated runtime/test baseline قبل از Documentation نهایی:
`a207ad2c35dd8dbbd10457e0d2295ea8efbb9776`

Validation-only PR:
`#35` — **Do Not Merge**.

Final CI:

```text
Run: 32351795808
Job: 96372355769

PowerShell runner contract: PASS
Compile: PASS
Django check/migration contract: PASS
Phase49.3F AddField-only migration safety: PASS
Targeted Django: 69/69 PASS
Phase49.3F Windows dedicated: 7/7 PASS
Phase49.3B diagnostics regression: 7/7 PASS
Diagnostic identity: 3/3 PASS
Epic49 Windows discovery: 84/84 PASS
Launcher markers: PASS
ACTIVE_RELEASE_VERIFIED=OK
Full Django: 415 PASS / 2 skipped
Overall: SUCCESS
Production: UNTOUCHED
```

Markerهای اصلی:
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

**نتیجه:** blocker کدنویسی/CI فاز 49.3F بسته شده؛ فاز هنوز DONE نیست چون Windows Local/Manual QA و user approval باقی است.

---

## 12) Migration State

### قبلاً روی Windows اعمال‌شده
- `store.0031_phase49_rich_material_colors` ✅
- `store.0032_phase49_slider_media_profile` ✅
- `website.0022_phase49_hero_media_presentation` ✅

### Phase49.3F — Additive-only و در Local Gate فعلی باید بررسی/اعمال شوند
- `store.0033_phase49_3f_pricing_intelligence`
- `website.0023_phase49_3f_material_runtime_rates`

CI ثابت کرده هر دو فقط `AddField` هستند. Production هنوز این فاز را دریافت نکرده است.

---

## 13) مسیر باقی‌مانده — از همین نقطه

### Gate A — Windows Pull + Automated Local Gate

- [ ] Catalog Center/Django processهای مربوط بسته شوند.
- [ ] `git status --short` خالی باشد؛ dirty tree → Stop/Inspect، نه Reset.
- [ ] Fetch/Switch/Pull exact Epic با `--ff-only`.
- [ ] اجرای `RUN_PHASE49_3F_LOCAL_GATE.ps1` از Repository.
- [ ] Backup Local Django DB و Catalog DB ساخته شود.
- [ ] `store.0033` و `website.0023` Additive apply/verify شوند.
- [ ] Focused + regression + launcher + full local suite PASS شود.

### Gate B — Manual Windows QA

- [ ] AI Center vertical/horizontal scroll + sticky Provider/Model/Save/Test/Log.
- [ ] Gemini Direct با real key: list/search/select/save/test.
- [ ] AvalAI/OpenRouter/OpenAI sanity test در صورت real key.
- [ ] AI progress states و 30s connection timeout.
- [ ] Image SEO روی 1–2 تصویر منتخب؛ هیچ image/file/url به AI نرود.
- [ ] metadata تصاویر انتخاب‌نشده حفظ شود.
- [ ] Runtime JSONL واقعی بررسی شود؛ هیچ API secret باقی نماند.
- [ ] source technical AI فقط بعد از تغییر واقعی `last_refetched_at`.
- [ ] Dynamic price example = **1,120,000 تومان** قبل از extras/shipping.
- [ ] quality duration و assembly تغییر قیمت را درست منعکس کنند.
- [ ] Product public: Persian labels / no Username / no raw codes.
- [ ] Product Detail price == Cart/Checkout unit price.
- [ ] Hero/Admin/reverse-sync regression بررسی شود.

### Gate C — One Real Local Publish

- [ ] فقط یک Product واقعی.
- [ ] **LOCAL PUBLISH ONLY**؛ Production Publish استفاده نشود.
- [ ] Django Local Product/Profile/Hero/Home/Store/Admin verify شود.

### Gate D — User Approval

- [ ] تأیید صریح Visual/Data/Local E2E.

### Gate E — Production

فقط بعد از Gate D:
- exact HEAD check
- `.env`/pending/DB backup
- assert MySQL
- migration plan
- migrate
- collectstatic
- Passenger restart
- runtime verify
- smoke tests
- DB/Data/Media safety verification
- docs/context final update

---

## 14) Separate Open Technical Items — غیر از blocker 49.3F

این موارد نباید گم شوند ولی نباید با Hotfix فعلی قاطی شوند:

### `/api/v1/catalog/sitemap/` → 404 در Local runserver

قبلاً در Local logs مشاهده شده است. احتمالاً stale client endpoint یا mismatch route است. این مورد **blocker Redaction/49.3F CI نیست** اما قبل از بسته‌شدن کامل Epic باید Root Cause آن بررسی شود و اگر Route واقعاً لازم است همان contract اصلاح شود؛ Endpoint موازی بی‌دلیل ساخته نشود.

### CKEditor4

`ckeditor.W001` بدهی امنیتی/maintenance مستقل است. ارتقا/جایگزینی باید فاز جدا با بررسی licensing/UI compatibility باشد.

### Realtime

`store.W026`: برای multi-process Production، Redis/polling architecture باید مطابق Host واقعی تصمیم‌گیری شود؛ تغییر عجولانه unrelated ممنوع.

---

## 15) نقشه کدهای اصلی

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
catalog_center/app/runtime_logging.py
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

### CI / Runner / Deploy

```text
.github/workflows/phase49-epic-ci.yml
RUN_PHASE49_3D_LOCAL_GATE.ps1
RUN_PHASE49_3E_LOCAL_GATE.ps1
RUN_PHASE49_3F_LOCAL_GATE.ps1
deploy/phase48-deploy.sh
deploy/phase49-deploy.sh
deploy/epic49_backup_database.py
deploy/epic49_verify_runtime.py
```

---

## 16) Checklist اجباری قبل/بعد از هر تغییر

### قبل
- [ ] Requested Delta مشخص.
- [ ] Existing code/feature خوانده شده.
- [ ] Duplicate solution جست‌وجو شده.
- [ ] Must-Not-Touch مشخص.
- [ ] DB/Media/Secret/Production safety مشخص.
- [ ] Migration در صورت نیاز Additive-first.
- [ ] Boundaryهای متاثر مشخص.
- [ ] Regression test تعریف شده.

### بعد
- [ ] Compile/Syntax PASS.
- [ ] Focused tests PASS.
- [ ] Regression tests PASS.
- [ ] `manage.py check` فقط warningهای شناخته‌شده یا clean.
- [ ] `makemigrations --check --dry-run` مطابق انتظار.
- [ ] Migration safety PASS.
- [ ] CI full PASS.
- [ ] Docs/PROJECT_CONTEXT/Master Roadmap update.
- [ ] Windows Local Gate PASS.
- [ ] Visual/Data QA PASS.
- [ ] explicit approval قبل از Production.

---

## 17) عملیات ممنوع به‌عنوان Quick Fix

بدون فاز مستقل و تأیید صریح:
- `git reset --hard` / `git clean -fd` برای پنهان‌کردن مشکل.
- حذف Django/Catalog DB.
- حذف `.env` یا media/private_media.
- `DROP TABLE` / `TRUNCATE`.
- حذف Product/Asset تاریخی برای سبزشدن migration.
- ساخت DB جدید فقط برای سبزشدن test.
- ساخت Endpoint/Model/Pricing/AI workflow موازی وقتی مسیر Mature قابل Extend است.
- حذف/تضعیف تستی که Regression واقعی را پیدا کرده.

---

## 18) Definition of Done

یک فاز فقط وقتی DONE است که:

```text
Code complete
+ Focused tests green
+ Regression tests green
+ CI full green
+ Migration safety verified
+ Windows Local Gate green
+ Manual Visual/Data QA green
+ User explicit approval
+ Production backup/deploy if production-bound
+ Production smoke/data checks green
+ Docs/roadmap/context updated
```

در غیر این صورت وضعیت `IN PROGRESS` یا `BLOCKED/PENDING LOCAL QA` است.

---

## 19) Current Status — 2026-08-20

**Phase:** `49.3F Product Intelligence / Dynamic Pricing / AI UX`  
**GitHub code/CI blocker:** بسته شده ✅  
**Final CI:** Run `32351795808`, Job `96372355769` — SUCCESS ✅  
**Runtime Trace Bearer leak:** FIXED + regression-covered ✅  
**Targeted Django:** 69/69 ✅  
**Phase49.3F Windows:** 7/7 ✅  
**Epic49 discovery:** 84/84 ✅  
**Full Django:** 415 PASS / 2 skipped ✅  
**Launcher:** `ACTIVE_RELEASE_VERIFIED=OK` ✅  
**Windows Local 49.3F Gate:** PENDING  
**Manual QA / one real Local Publish:** PENDING  
**Production:** **UNTOUCHED / NOT APPROVED**

### قدم بعدی دقیق

```text
GitHub exact Epic HEAD
→ Windows pull --ff-only
→ RUN_PHASE49_3F_LOCAL_GATE.ps1
→ Local automated PASS
→ Manual AI/Image/Pricing/Product QA
→ one real LOCAL PUBLISH ONLY
→ Local Django E2E
→ explicit user approval
→ Production plan/deploy
```

در این نقطه **کد جدید برای Hotfix Redaction لازم نیست** مگر Windows Local Gate Regression تازه‌ای نشان دهد. اگر Regression جدیدی ظاهر شد، فقط Root Cause همان مورد با Minimal Change + Regression Test اصلاح می‌شود.

---

## 20) قانون نگهداری این سند

در پایان هر Phase/Hotfix مهم باید حداقل این موارد به‌روز شوند:

1. مسیر طی‌شده.
2. Incident/Error Ledger.
3. Current Status.
4. Remaining Path.
5. Final code/test baseline.
6. CI Run/Job/result.
7. Local Gate result.
8. Production result.

این فایل نقشه مادر است؛ Phase docs جزئیات implementation را نگه می‌دارند و `PROJECT_CONTEXT.md` Snapshot عملیاتی کوتاه‌تر را نگه می‌دارد.
