# PROJECT_CONTEXT — 3DPrintHub

> Snapshot عملیاتی Source of Truth. جزئیات کامل در `docs/00_PROJECT_MASTER_ROADMAP_FA.md` و Phase docs است. هنگام تعارض: **Migration state واقعی + جدیدترین CI/Local/Host output + این فایل** ملاک است.

## 1) مسیرهای دائمی

- Windows project root: `D:\projects\3DPrintHub`
- Windows virtualenv: `D:\projects\3DPrintHub\.venv`
- Windows Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- Catalog persistent/legacy data:
  - `D:\projects\3dprinthub_catalog_center`
  - `D:\projects\3dprinthub-catalog-manager`
- Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
- Windows backups: `D:\projects\3dprinthub-backups`
- GitHub: `farazha2203/3dprinthub`
- Active branch: `epic/phase49-unified-product-slider-sync`
- Production root: `/home/sfkilvrs/3dprinthub`
- Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Production MySQL DB: `sfkilvrs_EmiAdmin_3dprinthub`

## 2) قوانین غیرقابل نقض

مسیر اجباری تحویل:

`GitHub Epic → CI/Self-Test → Windows pull → Local backup/migrate/test → Visual/Data QA → explicit user approval → Production backup/deploy/migrate/collectstatic/restart → smoke tests`

قواعد:
- Production قبل از تأیید صریح Local دست نمی‌خورد.
- تغییر باید Minimal و موضعی باشد؛ قابلیت سالم موجود Replace نمی‌شود.
- مسیر Mature باید Extend/Patch/Wrap شود؛ duplicate architecture ممنوع مگر دلیل مستند.
- DB برای حل مشکل کد Reset نمی‌شود.
- `.env`, API keys, DB, media/private_media و Catalog persistent data حذف/Reset نمی‌شوند.
- Migration عادی Additive-first است؛ destructive change فاز مستقل می‌خواهد.
- Repair/Backfill حساس Backup + Dry Run دارد.
- Windows Catalog Center ابزار عملیاتی اصلی؛ Django Admin ابزار مدیریتی دوم.
- Python/Django زبان اصلی؛ PowerShell برای Windows operations.
- Secret/API Key/Password/Token داخل Git، SQLite audit یا diagnostic export ذخیره نمی‌شود.
- Source ابتدا روی GitHub Epic؛ Windows فقط Pull می‌کند.
- Script/ZIP/Hotfix خارج از GitHub Source of Truth مبنا نیست.
- Bugfix باید Regression Test داشته باشد؛ تستی که Bug واقعی را پیدا کرده حذف/ضعیف نمی‌شود.

Policy:
`docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`

Master roadmap:
`docs/00_PROJECT_MASTER_ROADMAP_FA.md`

## 3) زنجیره Epic جاری

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics → 49.3C Operator Recovery → 49.3C-1 Persian Integrity → 49.3D Workflow Hardening → 49.3D.1 Runner Hotfix → 49.3E AI Task Recovery → 49.3F Product Intelligence/Dynamic Pricing/AI UX → 49.3F Runtime Trace Redaction Hotfix`

Ancestry خطی نگه‌داری می‌شود تا Conflict مصنوعی ایجاد نشود.

## 4) Catalog Center baseline

- Version: `8.7.1`
- Build family: `2026.08.16.3`
- Canonical operator workspace: Epic49 Product Workspace
- Local/Production publish targets جدا و fail-closed هستند.

## 5) Migration state

Django migrations اصلی Epic:
- `store.0030_phase49_unified_sync_contract`
- `website.0020_phase49_2c_hero_studio`
- `website.0021_phase49_unified_hero_sync`
- `store.0031_phase49_rich_material_colors`
- `website.0022_phase49_hero_media_presentation`
- `store.0032_phase49_slider_media_profile`
- `store.0033_phase49_3f_pricing_intelligence`
- `website.0023_phase49_3f_material_runtime_rates`

آخرین Windows state ثبت‌شده قبل از اجرای Runner 49.3F:
- `store.0031`: applied ✅
- `store.0032`: applied ✅
- `website.0022`: applied ✅
- `store.0033`: **pending Local Gate**
- `website.0023`: **pending Local Gate**

CI ثابت کرده 0033 و 0023 **AddField-only** هستند. Production این فاز را هنوز دریافت نکرده است.

## 6) Unified Product / Hero architecture

Canonical flow:

`Employee → Windows Catalog Center → Batch/Bridge → Django Product + ProductCatalogProfile + HomepageHeroSlide → Store/Home/Cart/Checkout`

Reverse:

`Django Admin edit → revision increment → Bridge → Windows refresh/compare`

Protection:
- Product Profile و Hero revision مستقل.
- stale Windows write → HTTP 409.
- Admin edit revision را بالا می‌برد.
- `batch_uuid + source_hash` idempotency.
- Bridge version `1.3.0`, contract `epic49-unified-v1`.
- legacy health/import/diagnostics حفظ شده‌اند.

## 7) Foundations که نباید Regression شوند

### 49.2A
- Public external catalog/Link Analyzer intake بازنشسته.
- historical rows حذف نشده‌اند.
- external autosync پیش‌فرض خاموش.
- Material و USD/FX pricing حفظ شده.

### 49.2B / Admin design
- Velzon Django Corporate / Master RTL assets حفظ شده.
- Customer Portal drawer حفظ شده.
- Canonical logo: `static/img/brand/3dprinthublogo.png`.

### 49.2C Hero Studio
- visual Product/Image album picker.
- Edit existing slide بدون Delete/Recreate.
- per-slide effect/timing.
- mobile/reduced-motion fallback.

### Persian Sales / Dual Publish
- Product SEO و Slider SEO مستقل.
- Hero public raw English/Cookie/Consent/Tracking را fallback نمی‌کند.
- Local Publish دقیقاً Local SQLite؛ Production path جدا.

### Materials / Colors
- operator checkbox واقعی.
- rich color types + multi HEX.
- legacy JSON compatibility حفظ شده.

## 8) Phase49.3A/3B — Readiness / AI / Hero Media / Diagnostics

Canonical 7 stages:
1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

AI Providers اولیه:
- AvalAI
- OpenRouter
- OpenAI Direct

Hero Media:
- `product_fit`, `full_bleed`, `framed`, `cinematic`
- contain/cover, focal, scale, X/Y, background, blur
- desktop/mobile bounds
- default `product_fit + contain`

Diagnostics:
- `app_audit_log`
- `ai_request_log`
- operator/workstation/session identity
- provider/model/request ID/HTTP/duration/tokens/cost
- sanitized diagnostic bundle

Historical final CI 49.3B:
Run `32248104376`, Job `96052943408`, SUCCESS.

## 9) Phase49.3C / 3C-1

Operator Recovery:
- live readiness.
- exact missing-field reasons.
- fail-closed publish.
- exact image identity; no index guessing.
- hard cap 10 images.
- SEO WebP + metadata manifest.

Persian Integrity:
- English source به فیلد فارسی fallback نمی‌شود.
- Structured Persian repair/fallback.
- `description_fa` محدود/sanitized HTML.
- SEO/Tag/Hashtag/Keyword/Alt/Material Recommendation reload/save کامل.

## 10) Phase49.3D / 3D.1

Resolved:
- Tkinter pack/grid parent collision.
- searchable full AI model picker.
- active provider/model persistence.
- local publish exact preflight reasons.
- semantic image SEO signature.
- professional price range compatibility.
- PowerShell StrictMode array bug در Runner.

49.3D final CI:
Run `32271502234`, Job `96128806609`, SUCCESS.

49.3D.1 final CI:
Run `32276195521`, Job `96144096195`, SUCCESS.

## 11) Phase49.3E — AI Task Completion & Recovery

Rule جاری:
**Readiness راهنما است، نه زندان.**

- همه 7 Stage قابل بازکردن هستند.
- Stage قرمز یعنی ناقص، نه disabled.
- Local Preflight همیشه قابل اجرا برای نمایش blocker.
- Production همچنان fail-closed.

Task Center:
1. متن فارسی
2. SEO محصول
3. SEO/Metadata تصاویر
4. Material recommendation
5. Slider SEO

Manual Image Metadata Editor و structured AI guards حفظ شده‌اند.

Final CI:
Run `32280313257`, Job `96157285817`, SUCCESS.

## 12) Phase49.3F — Product Intelligence / Dynamic Pricing / AI UX

Canonical doc:
`docs/PHASE49_3F_PRODUCT_INTELLIGENCE_PRICING_AI_UX.md`

### Image SEO privacy contract

**هیچ Image bytes، فایل یا URL تصویر در Task Image SEO به AI ارسال نمی‌شود.**
AI فقط Product/SEO facts + selected slots + prior alt را می‌گیرد. Mapping URL فقط Local است.

Metadata تصاویر انتخاب‌نشده preserve می‌شود.

### AI Center

Canonical Provider order:
1. AvalAI
2. OpenRouter
3. Google Gemini Direct
4. OpenAI Direct

Google Gemini Direct:
- provider code `google`.
- key در `x-goog-api-key` Header، نه URL/log.
- `/models` و filter `generateContent`.
- real model ID persistence.
- Balance جعلی نمایش داده نمی‌شود.

AI Center scrollable است و active Provider/Model + Save/Test/Log controls sticky هستند.

### Runtime Trace

Path:
`<persistent catalog data>/logs/phase49_3f/YYYY-MM-DD/workflow-<session>.jsonl`

Record:
operator/workstation/session/product/provider/model/action/status/elapsed/sanitized detail.

### Source-grounded Technical AI

AI فقط بعد از تغییر واقعی `last_refetched_at` اجرا می‌شود؛ `updated_at` عمومی success نیست.

### Dynamic Pricing

Strategies:
- `legacy`
- `fixed`
- `dynamic`

Product Detail/Cart/Checkout از همان Variant price source استفاده می‌کنند.

Acceptance:
`2,600,000/kg + 100g part + 50g support×2 + 3h×150k + 3h×50k = 1,120,000 تومان before extras/shipping`.

### Public UX

- raw `ready_product`/`made_to_order` نمایش داده نمی‌شود.
- `Username` attribution عمومی نمایش داده نمی‌شود.
- Technical Summary فارسی.
- dynamic price breakdown شفاف.
- Fixed strategy internal dynamic components را به مشتری نشان نمی‌دهد.

## 13) Phase49.3F Runtime Trace Redaction Hotfix

Previous CI failure:
`test_runtime_trace_redacts_structured_and_inline_secrets`.

Observed fake leak:
`Authorization: *** very-secret-token ...`

Root Cause:
`runtime_logging.redact()` ابتدا generic `authorization:<value>` را اجرا می‌کرد و فقط `Bearer` را mask می‌کرد؛ credential tail باقی می‌ماند.

Minimal Fix:
- Bearer credential pattern قبل از generic secret-key pattern.
- Runtime Trace/JSONL/identity/AI Center/Pricing/DB/Publish untouched.
- original failing test unchanged.
- new direct baseline regression در `catalog_center/tests/test_v85_core.py`.

Commits:
- runtime fix: `60393e9cd294a8414c2b7945a3a11c54b391d8a1`
- regression: `03259f5072f8b902b190aa5bb86bc5b694632ab3`
- validated runtime/test baseline before final docs: `a207ad2c35dd8dbbd10457e0d2295ea8efbb9776`

Status: **FIXED + FINAL CI VERIFIED**.

## 14) Phase49.3F Final CI

Validation-only PR: `#35` — **Do Not Merge**.

- Run `32351795808`
- Job `96372355769`
- PowerShell runner contract ✅
- Compile ✅
- Django check/migration contract ✅
- AddField-only migration safety ✅
- Targeted Django **69/69** ✅
- Phase49.3F Windows dedicated **7/7** ✅
- Phase49.3B Diagnostics **7/7** ✅
- Diagnostic identity **3/3** ✅
- Epic49 discovery **84/84** ✅
- Launcher markers ✅
- `ACTIVE_RELEASE_VERIFIED=OK` ✅
- Full Django **415 PASS / 2 skipped** ✅
- Overall **SUCCESS**

Main 49.3F markers:
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

## 15) Warnings شناخته‌شده

غیر-Failure:
- `3dprinthub.W001`: Google membership credentials خالی.
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: in-memory realtime؛ multi-process production به Redis/polling strategy نیاز دارد.
- Pillow `Image.getdata()` deprecation.

هیچ‌کدام blocker Hotfix 49.3F نیستند و برای رفعشان معماری unrelated تغییر نمی‌کند.

## 16) Separate open item

Local logs قبلاً `GET /api/v1/catalog/sitemap/ → 404` نشان دادند. این defect با Redaction/49.3F CI یکی نیست و نباید فراموش شود. قبل از closure کامل Epic باید Route/client contract آن بررسی شود؛ endpoint موازی بی‌دلیل ساخته نشود.

## 17) Gate فعلی — Windows Local Phase49.3F

Canonical runner:
`D:\projects\3DPrintHub\RUN_PHASE49_3F_LOCAL_GATE.ps1`

Runner version: `49.3F.0`.

ترتیب:
1. Catalog Center/Django project processها بسته.
2. `git status --short` خالی؛ dirty → Stop/Inspect.
3. `git fetch --prune origin`.
4. switch Epic.
5. `git pull --ff-only origin epic/phase49-unified-product-slider-sync`.
6. Runner 49.3F اجرا شود.
7. Runner backup Local Django DB و Catalog DB می‌سازد.
8. 0033/0023 additive migration apply/verify.
9. compile/Django/Windows/launcher/full suite.
10. Manual QA.

Manual acceptance:
- AI Center scroll/sticky controls.
- Gemini Direct real model list/search/select/save/test.
- provider connection states + 30s timeout.
- selected Image SEO بدون image/file/url transmission.
- unselected metadata preservation.
- Runtime log بدون secret.
- source technical AI فقط بعد از `last_refetched_at`.
- pricing **1,120,000 تومان** acceptance.
- quality duration/assembly variation.
- یک Product واقعی **LOCAL PUBLISH ONLY**.
- Product public Persian labels/no Username/no raw codes.
- Product Detail == Cart/Checkout unit price.
- Local Product/Profile/Hero/Home/Admin verification.

سپس explicit user approval؛ قبل از آن Production ممنوع.

## 18) Current checklist

- [x] Phase49.3D runtime/CI complete.
- [x] Phase49.3D.1 runner hotfix CI complete.
- [x] Phase49.3E AI Task Center/recovery CI complete.
- [x] Phase49.3F Product Intelligence/Dynamic Pricing implementation complete.
- [x] Phase49.3F AddField-only migration contract CI verified.
- [x] Runtime Trace inline Bearer leak fixed.
- [x] Redaction baseline regression added.
- [x] Phase49.3F Final GitHub CI SUCCESS — Run `32351795808`, Job `96372355769`.
- [ ] Windows Pull + `RUN_PHASE49_3F_LOCAL_GATE.ps1`.
- [ ] Phase49.3F Local migrations 0033/0023 applied/verified.
- [ ] Real-provider AI QA.
- [ ] Image SEO privacy/metadata QA.
- [ ] Runtime log real-secret QA.
- [ ] Dynamic pricing manual acceptance.
- [ ] One real Local Publish E2E.
- [ ] Local Django end-to-end verification.
- [ ] Explicit user approval.
- [ ] Production deploy.

## 19) Production status

**NOT DEPLOYED / NOT APPROVED / UNTOUCHED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3C تا 49.3F در Production اجرا نشده است. Production تا پایان Windows Local QA و تأیید صریح کاربر دست‌نخورده می‌ماند.

## 20) قدم بعدی دقیق

```text
GitHub exact Epic HEAD
→ Windows pull --ff-only
→ RUN_PHASE49_3F_LOCAL_GATE.ps1
→ automated Local PASS
→ manual AI/Image/Pricing/Product QA
→ one real LOCAL PUBLISH ONLY
→ Local Django E2E
→ explicit user approval
→ Production plan/deploy
```

اگر Windows Local Gate Regression جدیدی نشان دهد، فقط Root Cause همان مورد با Minimal Change + Regression Test اصلاح می‌شود؛ کلیات معماری دوباره نوشته نمی‌شود.
