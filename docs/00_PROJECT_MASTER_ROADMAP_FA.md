# 3DPrintHub — نقشه مادر پروژه، معماری، فازها، خطاها و مسیر بعدی

> **این فایل قبل از شروع هر Phase/Hotfix/UI change/Migration/Sync/Deploy باید خوانده شود.**  
> هدف: جلوگیری از کد موازی، حفظ قابلیت‌های سالم، ثبت Root Cause و روش حل، مشخص‌کردن مسیر نصب/DB/Host/Runner و معلوم‌بودن دقیق «الان کجاییم و قدم بعد چیست».

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**زبان اصلی:** Python / Django  
**ابزار اصلی اپراتور:** Windows Catalog Center  
**ابزار مدیریتی دوم:** Django Admin  
**Production:** قبل از Local QA + تأیید صریح کاربر ممنوع.

---

## 1) قانون مادر تغییرات

1. قابلیت سالم قبلی حذف/Replace نمی‌شود مگر درخواست صریح وجود داشته باشد.
2. مسیر Mature باید **Extend / Patch / Wrap** شود؛ معماری موازی فقط با دلیل فنی مستند.
3. Bug در همان Boundary/Contract/Module رفع می‌شود؛ UI/DB/Sync/Pricing کلی بازنویسی نمی‌شود.
4. Defaultهای قبلی حفظ می‌شوند؛ مثال: Product قدیمی روی `pricing_strategy=legacy` می‌ماند.
5. قبل از هر تغییر باید روشن باشد:

```text
Requested Delta
Touched Surfaces
Must-Not-Touch
Regression Tests
DB/Media/Secret/Production Safety
```

6. Bugfix بدون Regression Test کامل نیست.
7. تستی که Bug واقعی را گرفته حذف یا ضعیف نمی‌شود.
8. Migration عادی Additive-first است؛ destructive change فاز مستقل + Backup/Dry Run + تأیید می‌خواهد.
9. `git reset --hard`, `git clean -fd`, حذف DB، `.env`, media/private_media، Catalog persistent data، `DROP`, `TRUNCATE` Quick Fix نیست.
10. Source of Truth کد و Script و Docs، GitHub است؛ Windows/Host patch دستی مبنا نیست.
11. Production فقط بعد از Automated Local Gate + Manual Visual/Data QA + Local E2E + تأیید صریح کاربر.
12. Secret/API key/password/token در Git، diagnostic bundle یا SQLite audit ذخیره نمی‌شود.

---

## 2) Source of Truth و ترتیب اعتبار

هنگام اختلاف:

1. Migration/Data state واقعی همان محیط.
2. جدیدترین CI / Windows Local Gate / Host Verification output.
3. `docs/00_PROJECT_MASTER_ROADMAP_FA.md`.
4. `PROJECT_CONTEXT.md`.
5. جدیدترین Phase doc.
6. Runtime code + tests.
7. اسناد تاریخی قدیمی‌تر.

اسناد Canonical مهم:
- `PROJECT_CONTEXT.md`
- `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`
- `docs/EPIC49_UNIFIED_PRODUCT_SLIDER_SYNC.md`
- `docs/PHASE49_3A_PRODUCT_PUBLISH_READINESS.md`
- `docs/PHASE49_3B_GUIDED_AI_HERO_DIAGNOSTICS.md`
- `docs/PHASE49_3D_WORKFLOW_HARDENING.md`
- `docs/PHASE49_3F_PRODUCT_INTELLIGENCE_PRICING_AI_UX.md`
- `docs/PHASE49_3F1_WINDOWS_NATIVE_CAPTURE_HOTFIX.md`
- `docs/PHASE49_3G_WORKSPACE_USABILITY_AI_PROVENANCE.md`
- `docs/PHASE49_3G_FINAL_VALIDATION.md`
- `deploy/phase48-deploy.sh`
- `deploy/phase49-deploy.sh`

---

## 3) سیاست GitHub-first و تحویل Windows

مسیر اجباری:

```text
Change / Script / Test / Doc
→ GitHub Epic commit
→ GitHub CI
→ Windows git fetch/pull --ff-only
→ Run repository runner
→ Automated Local Gate
→ Manual Visual/Data QA
→ explicit user approval
→ Production backup/deploy
→ Production smoke/data checks
```

ممنوع:
- ارسال ZIP/PS1/Python/Hotfix جدا از Repository برای اجرا.
- کپی دستی Source روی Windows یا Host.
- Reset/Delete برای تمیزکردن Worktree.

Dirty Windows tree:
`STOP → inspect paths → preserve data → decide safe action`.

---

## 4) خواسته‌های اصلی محصول

### 4.1 Product Workspace / Wizard

Canonical stages:
1. اطلاعات پایه
2. سفارش، قیمت و گزینه‌ها
3. تصاویر
4. محتوا و SEO
5. منبع و مجوز
6. اسلایدر صفحه اصلی
7. بررسی و انتشار

Rule از 49.3E به بعد:
**Readiness راهنما است، نه زندان.** Stage ناقص باز هم قابل ورود و اصلاح است؛ Production Publish همچنان fail-closed.

### 4.2 AI Provider Hub

Providerهای Canonical:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

قواعد:
- Key/Model/Test هر Provider مستقل.
- Active Provider/Model یک Source of Truth.
- raw model ID persist؛ Label تزئینی persist نمی‌شود.
- Search/Filter مدل کامل.
- Balance فقط با API واقعی Provider.
- Request/tokens/cost در صورت پشتیبانی audit می‌شود.
- Secret در Git/diagnostic export ممنوع.

`$django-admin-expert`: در Session فعلی Plugin/Skill متناظر پیدا نشد؛ **unavailable in current session** ثبت می‌شود و نباید ادعای نصب شود.

### 4.3 Image SEO / Metadata

- فقط Selected images.
- **هیچ image bytes/file/image URL به AI ارسال نمی‌شود.**
- Slot→URL mapping فقط Local.
- unselected metadata Preserve.
- exact identity؛ index guessing ممنوع.
- `download_image_limit` per-product حفظ؛ hard cap فعلی 10.
- source/cache image در finalize حذف نمی‌شود.

### 4.4 Persian Content / SEO

- English source fallback به Persian editorial ممنوع.
- Product SEO و Slider SEO مستقل.
- AI حق جعل price/license/dimension/inventory/material/color ندارد.
- raw codeهای داخلی مانند `ready_product`, `made_to_order`, `Username` در Public UI/SEO/JSON-LD نمایش داده نمی‌شوند.

### 4.5 Hero / Slider

- Hero از همان Product/Asset.
- image ownership validate می‌شود.
- effect/timing حفظ.
- default امن `product_fit + contain`.
- focal/scale/X/Y/background/blur/desktop/mobile controls حفظ.
- Product Profile revision و Hero revision مستقل.

### 4.6 Pricing

Strategies:
- `legacy`
- `fixed`
- `dynamic`

Source of Truth قیمت Dynamic: `ProductVariant.price_breakdown()` و cached final Variant price.
Product Detail/Cart/Checkout ماشین‌حساب موازی ندارند.

Acceptance ثابت:

```text
PLA = 2,600,000 تومان/kg = 2,600 تومان/g
Part = 100g
Support = 50g × 2
Chargeable = 200g
Material = 520,000
Print = 3h × 150,000 = 450,000
Supervision = 3h × 50,000 = 150,000
Expected before extras/shipping = 1,120,000 تومان
```

---

## 5) مسیر طی‌شده Epic49

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
→ 49.3F.1 Windows Native stderr Capture Hotfix
→ 49.3G Workspace Usability + AI Autofill Provenance
```

Phase history جزئی در Phase docs و Git history حفظ شده است؛ این Roadmap وضعیت Consolidated فعلی را نگه می‌دارد.

---

## 6) معماری End-to-End

### Operator flow

```text
Employee
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite + Epic49 Product Workspace
  ↓
Product / Images / SEO / Material / Color / Price / Hero
  ↓
Batch Builder / Bridge
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
Django Admin edit
→ revision increment
→ Catalog Bridge
→ Windows refresh/compare
```

Guards:
- stale Windows write → HTTP 409.
- Product/Hero revision مستقل.
- `batch_uuid + source_hash` idempotency.
- Bridge version `1.3.0`, contract `epic49-unified-v1`.
- legacy health/import/diagnostics حفظ شده‌اند.

---

## 7) Software / Runtime / Installation Paths

### Windows

```text
Project root:        D:\projects\3DPrintHub
Virtualenv:          D:\projects\3DPrintHub\.venv
Catalog source:      D:\projects\3DPrintHub\catalog_center
Django local DB:     D:\projects\3DPrintHub\db.sqlite3
Persistent Catalog: D:\projects\3dprinthub-catalog-manager
Legacy retained:    D:\projects\3dprinthub_catalog_center
Catalog DB:          D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
Backups:             D:\projects\3dprinthub-backups
```

Current Catalog Center:
- Version `8.7.1`
- Build family `2026.08.16.3`
- Python/Django project؛ requirements CI روی Python 3.12 / Django 6.0.7 validate شده است.
- Django SmartBase Admin و assets مدیریتی موجود حفظ شده‌اند.
- Pillow، Allauth، Channels و dependencies مطابق `requirements.txt` نصب می‌شوند.

Secrets:
- Windows Credential Store / Environment variables.
- Secret در Repository، diagnostic export یا audit JSON ممنوع.

Current canonical runner:
`D:\projects\3DPrintHub\RUN_PHASE49_3G_LOCAL_GATE.ps1`

Runner version:
`49.3G.0`

Runner chain:
`49.3G → 49.3F.1 → 49.3E → 49.3D/base gates`.

### Production

```text
Project:       /home/sfkilvrs/3dprinthub
Python venv:   /home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python
Database:      MySQL sfkilvrs_EmiAdmin_3dprinthub
Static base:   /home/sfkilvrs/public_html/static
Media base:    /home/sfkilvrs/public_html/media
Private media: /home/sfkilvrs/3dprinthub/private_media
```

`.env` ممکن است pathها را Override کند؛ Runtime settings واقعی قبل از Deploy خوانده می‌شود.

DB Guard:
- Production `connection.vendor == mysql`.
- DB name دقیقاً expected production DB.
- SQLite fallback در Production migration → STOP.

Passenger restart:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

Restart بدون Runtime verification + HTTP smoke test کافی نیست.

---

## 8) Database State

Django Epic migrations مهم:
- `store.0030_phase49_unified_sync_contract`
- `website.0020_phase49_2c_hero_studio`
- `website.0021_phase49_unified_hero_sync`
- `store.0031_phase49_rich_material_colors`
- `website.0022_phase49_hero_media_presentation`
- `store.0032_phase49_slider_media_profile`
- `store.0033_phase49_3f_pricing_intelligence`
- `website.0023_phase49_3f_material_runtime_rates`

Windows applied:
- `store.0031` ✅
- `store.0032` ✅
- `website.0022` ✅
- `store.0033` ✅
- `website.0023` ✅

49.3G Django Migration جدید ندارد.

Catalog SQLite local-only additive columns:
- `ai_provenance_json`
- `ai_disabled_groups_json`

علت local-only بودن: Provenance مالکیت AI/اپراتور Windows است و بدون نیاز تجاری وارد Production schema نمی‌شود.

Production هنوز migration/deploy مربوط به Phase49.3C تا 49.3G را دریافت نکرده است.

---

## 9) Runbook امن Production

فقط بعد از تأیید صریح Local:

```text
1. git status / branch / exact approved HEAD
2. backup .env
3. backup pending imports
4. manage.py check
5. makemigrations --check --dry-run
6. assert vendor=mysql + expected DB
7. mysqldump before migration
8. migrate --plan
9. migrate --noinput
10. collectstatic --noinput
11. Passenger restart
12. runtime verifier
13. HTTP smoke tests
14. Product/Home/Admin/Cart checks
15. DB/Data/Media safety verification
16. update phase docs + roadmap + context
```

`mysqldump` missing/fail → Migration ممنوع. Password در command line/log چاپ نمی‌شود. `utf8mb4` حفظ می‌شود.

---

## 10) قابلیت‌های حفاظت‌شده

- Windows Catalog Center ابزار اصلی.
- Django Admin ابزار دوم.
- Unified Product/Hero/Bridge contract.
- revision conflict guards.
- Persian Hero + effect/timing.
- Material/Color operator options.
- Local/Production Publish separation.
- exact Readiness blockers.
- AI Provider Hub + diagnostics.
- Exact image identity.
- Persian Content Guard.
- Price Range compatibility + Dynamic pricing.
- Product Detail/Cart/Checkout price consistency.
- selected-only text-only Image SEO.
- unselected image metadata preservation.

---

## 11) Incident / Error Ledger

### 11.1 Tkinter pack/grid collision
Symptom: `TclError: cannot use geometry manager pack ... already has slaves managed by grid`.  
Root Cause: pack/grid روی یک parent.  
Fix: manager parent حفظ؛ holder داخلی parent جدا.  
Status: **FIXED + test**.

### 11.2 AI decorated model ID
Risk: Label نمایشی به‌جای raw model ID persist شود.  
Fix: normalize/clean model ID.  
Status: **FIXED + test**.

### 11.3 Silent Local Publish blocker
Root Cause: `notify=False` دلیل Readiness failure را پنهان می‌کرد.  
Fix: Save → Readiness → safe optional image finalize → Readiness → exact dialog/audit.  
Status: **FIXED**.

### 11.4 Image SEO false stale
Root Cause: hash روی raw JSON serialization.  
Fix: semantic JSON normalization.  
Status: **FIXED + test**.

### 11.5 Image index guessing
Fix: exact URL/file/manifest identity.  
Status: **FIXED + tests**.

### 11.6 Test order / monkey patch leakage
Fix: Source contract از canonical file به‌جای wrapped method runtime.  
Status: **FIXED**.

### 11.7 AvalAI `response_format` rejection
Fix: capability-aware retry بدون `response_format` + client JSON validation.  
Status: **FIXED + test**.

### 11.8 Generic `updated_at` mistaken as source refresh
Fix: فقط تغییر واقعی `last_refetched_at` اجازه technical AI می‌دهد.  
Status: **FIXED + test**.

### 11.9 Price Range consultation overwrite
Root Cause: مرحله بعد True قبلی را False می‌کرد.  
Fix: True preserve؛ فقط requirement اضافه می‌شود.  
Status: **FIXED + E2E test**.

### 11.10 raw codes / Username public leak
Fix: Persian labels + filtering internal attribution.  
Status: **FIXED + public tests**.

### 11.11 Product/Cart pricing divergence
Fix: final Variant price cache Source of Truth.  
Status: **GUARDED + tests**.

### 11.12 Windows temp SQLite lock
Fix: explicit DB connection close in `finally`.  
Status: **FIXED**.

### 11.13 Launcher `sync_seo_reference_lists` ImportError
Fix: resolve callable workspace hook from `_phase49_sync_reference_lists`.  
Status: **FIXED + regression**.

### 11.14 Runtime Trace Bearer secret leak
Observed fake leak:
`Authorization: Bearer very-secret-token → Authorization: *** very-secret-token`.

Root Cause: generic auth pattern قبل از Bearer credential pattern.  
Fix: Bearer credential redaction اول، سپس generic secret-key redaction.  
Status: **FIXED + FINAL CI**.

### 11.15 Windows `showmigrations` NativeCommandError — Phase49.3F.1

واقعیت Local:
- `store.0033` → OK.
- `website.0023` → OK.
- crash بعد از migrations در Verify.

Root Cause:
- `$ErrorActionPreference="Stop"`.
- native stderr با `2>&1` مستقیم capture.
- `ckeditor.W001` warning با native exit 0 توسط Windows PowerShell به terminating error تبدیل شد.

Fix:
- Runner `49.3F.1`.
- `Invoke-NativeCapture` با EAP موقت `Continue`.
- success/failure فقط native exit code.
- self-test stderr warning + stdout + exit 0.

Do Not Repeat:
- Warning stderr را Failure فرض نکن.
- Migration موفق را به‌دلیل Verify failure rollback/reset نکن.

Status: **FIXED + FINAL CI VERIFIED**.

### 11.16 Phase49.3G Composition Boundary Regression

First probe:
Dedicated 3G PASS؛ Main Phase49 Windows test fail:
`AttributeError: type object 'Workspace' has no attribute 'reload'`.

Root Cause:
- 49.3G در `phase49_3f_source_refresh_guard.install()` زنجیر شده بود.
- Source Refresh 3F unit test عمداً Workspace stub مینیمال دارد.
- Feature فاز بعد نباید داخل Installer مستقل فاز قبلی Composition شود.

Fix:
- 3F Source Guard مستقل شد.
- 3G فقط در `catalog_center/launch.py` نصب می‌شود.
- order:
`49.3F Workspace → 49.3F Source Guard → 49.3G Workspace Usability → 49.3G Commerce Provenance`.
- regression test عدم import/chaining 3G در Source Guard را قفل می‌کند.

Do Not Repeat:
- Cross-phase composition در Composition Root/Launcher؛ نه داخل Installer مستقل قدیمی.

Status: **FIXED + FINAL CI VERIFIED**.

---

## 12) Phase49.3G — Workspace Usability + AI Autofill Provenance

Docs:
- `docs/PHASE49_3G_WORKSPACE_USABILITY_AI_PROVENANCE.md`
- `docs/PHASE49_3G_FINAL_VALIDATION.md`

Runtime:
- `catalog_center/app/phase49_3g_workspace_usability.py`
- `catalog_center/app/phase49_3g_commerce_provenance.py`
- `catalog_center/launch.py`

Tests:
- `catalog_center/tests/test_epic49_phase49_3g_workspace_usability.py`
- `catalog_center/tests/test_epic49_phase49_3g_commerce_provenance.py`

Runner/CI:
- `RUN_PHASE49_3G_LOCAL_GATE.ps1`
- `.github/workflows/phase49-3g-workspace-usability-ci.yml`

### 12.1 Workspace
- vertical scrollbar واقعی.
- mouse wheel سطح Workspace.
- Stage rail قابل دسترسی.
- Commerce compact؛ Pricing Engine بدون تغییر.

### 12.2 Gallery
- همان Gallery Mature.
- one-row horizontal thumbnail strip.
- horizontal scrollbar.
- selected/site/primary/slider/remove/open behavior حفظ.

### 12.3 AI Autofill
Canonical action:
`✨ تکمیل هوشمند محصول با AI`.

همان Task Center Mature استفاده می‌شود؛ Workflow موازی ساخته نشده.

AI allowed groups:
- `persian_content`
- `product_seo`
- `image_seo`
- `materials`
- `slider_seo`

Operator-owned always:
- fixed/final price
- sale approval
- inventory truth
- commercial/legal license
- Production Publish

### 12.4 Provenance / Manual Override
Local Catalog columns:
- `ai_provenance_json`
- `ai_disabled_groups_json`

States:
- `🤖 AI-owned`
- `✎ manual override / AI locked`
- `⛔ AI disabled`
- `○ no AI ownership`

Controls per group:
- `خاموش/روشن AI`
- `اجازه بازنویسی AI`

Manual edit + Save روی AI-owned group → `manual_override=true`; AI overwrite blocked تا operator release.

Commerce page نیز Materials Provenance panel دارد؛ Pricing/approval/license operator-owned می‌مانند.

### 12.5 Launcher markers

```text
EPIC49_3G_WORKSPACE_VERTICAL_SCROLL=ENABLED
EPIC49_3G_GALLERY_HORIZONTAL_SCROLL=ENABLED
EPIC49_3G_COMPACT_COMMERCE=ENABLED
EPIC49_3G_AI_AUTOFILL_PROVENANCE=ENABLED
EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED
EPIC49_3G_AI_DISABLE_PER_GROUP=ENABLED
EPIC49_3G_COMMERCE_PROVENANCE=ENABLED
EPIC49_3F_SELECTED_IMAGE_TEXT_ONLY_AI=ENABLED
ACTIVE_RELEASE_VERIFIED=OK
```

---

## 13) GitHub CI Baseline

### 49.3F final baseline
Run `32351795808`, Job `96372355769` — SUCCESS.  
Full Django: `415 PASS / 2 skipped`.

### 49.3F.1 runner hotfix
Run `32356959599`, Job `96388108683` — SUCCESS.  
Validation PR `#36`: closed / not merged.

### 49.3G final Runtime validation
Runtime baseline قبل از docs-only commits:
`88c19d0ab9a5ed416479f65c30b8a6ed8cf0153d`.

Dedicated 49.3G:
- Run `32561222101`
- Job `97002924663`
- Runner contract PASS
- Compile PASS
- dedicated tests PASS
- launcher markers PASS
- no Django migration drift PASS
- Overall **SUCCESS**

Full Phase49:
- Run `32561222090`
- Job `97002924583`
- PowerShell contract PASS
- Compile PASS
- Django check/migration contract PASS
- Phase49 regressions PASS
- Windows Catalog Center Epic49 PASS
- Full Django suite PASS
- Overall **SUCCESS**

Validation PR `#37`: **closed / not merged**.

---

## 14) Warningهای شناخته‌شده

Non-blocking:
- `3dprinthub.W001`: Google membership credentials خالی.
- `ckeditor.W001`: CKEditor4 security/maintenance debt.
- `store.W026`: in-memory realtime؛ multi-process Production نیازمند Redis/polling architecture تصمیم‌گیری‌شده است.
- Pillow `Image.getdata()` deprecation.

این موارد Scope مستقل دارند؛ بهانه بازنویسی unrelated نیستند.

---

## 15) Separate Open Technical Items

### `/api/v1/catalog/sitemap/` → 404 Local
قبلاً در Local runserver دیده شده. احتمال stale client endpoint یا route mismatch.  
قبل از closure کامل Epic باید Root Cause بررسی شود؛ endpoint موازی بدون دلیل ساخته نشود.

### CKEditor4
Upgrade/replace فقط در Phase مستقل با licensing/UI compatibility review.

### Realtime
Redis/polling solution باید مطابق محدودیت واقعی Host طراحی شود؛ تغییر عجولانه ممنوع.

---

## 16) نقشه کدهای اصلی

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
catalog_center/app/phase49_3g_workspace_usability.py
catalog_center/app/phase49_3g_commerce_provenance.py
catalog_center/app/runtime_logging.py
catalog_center/app/ai_providers.py
catalog_center/app/openai_content.py
```

### Django / Pricing

```text
store/epic49_catalog_profile.py
store/phase49_unified_sync.py
store/phase49_3b_profile_media.py
store/phase49_3b_hero_media_sync.py
store/phase49_3f_pricing.py
store/phase49_3f_pricing_finalize.py
store/phase49_3f_admin.py
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
.github/workflows/phase49-3g-workspace-usability-ci.yml
RUN_PHASE49_3D_LOCAL_GATE.ps1
RUN_PHASE49_3E_LOCAL_GATE.ps1
RUN_PHASE49_3F_LOCAL_GATE.ps1
RUN_PHASE49_3G_LOCAL_GATE.ps1
deploy/phase48-deploy.sh
deploy/phase49-deploy.sh
deploy/epic49_backup_database.py
deploy/epic49_verify_runtime.py
```

---

## 17) Current Gate — Windows Phase49.3G

Canonical runner:
`D:\projects\3DPrintHub\RUN_PHASE49_3G_LOCAL_GATE.ps1`  
Version: `49.3G.0`.

### Gate A — Pull / Automated
- [ ] Catalog Center/Django project processها بسته.
- [ ] `git status --short` خالی؛ dirty → Stop/Inspect.
- [ ] `git fetch --prune origin`.
- [ ] switch `epic/phase49-unified-product-slider-sync`.
- [ ] `git pull --ff-only`.
- [ ] verify runner 49.3G.0.
- [ ] execute repository runner.
- [ ] 49.3F.1 chain PASS.
- [ ] compile + 49.3G dedicated tests PASS.
- [ ] launcher markers PASS.
- [ ] final git safety PASS.

### Gate B — Manual Workspace QA
- [ ] Product/Commerce vertical scroll و mouse wheel.
- [ ] Commerce compact و rates/pricing usable.
- [ ] Gallery horizontal strip + scrollbar با 12+ image.
- [ ] selected/site/primary/slider/remove/open سالم.
- [ ] Task Center AI/manual/disabled ownership status.
- [ ] Smart Autofill فقط missing/allowed fields.
- [ ] Disable one group → rerun → no change همان group.
- [ ] Manual edit AI-owned field + Save → manual override lock.
- [ ] release فقط با `اجازه بازنویسی AI`.
- [ ] price/approval/inventory/license/Production توسط AI تغییر نکند.
- [ ] Image SEO selected-only + text-only؛ unselected metadata preserve.

### Gate C — Existing 49.3F acceptance
- [ ] real Provider/model test where credentials exist.
- [ ] Runtime log contains no secret.
- [ ] source technical AI only after real `last_refetched_at`.
- [ ] dynamic price example = `1,120,000 تومان` before extras/shipping.
- [ ] Product Detail == Cart/Checkout unit price.
- [ ] Persian public labels / no Username / no raw code.

### Gate D — One real Local Publish
- [ ] یک Product واقعی.
- [ ] **LOCAL PUBLISH ONLY**.
- [ ] Local Django Product/Profile/Hero/Home/Store/Admin verify.

### Gate E — User Approval
- [ ] explicit Visual/Data/E2E approval.

### Gate F — Production
فقط بعد از E؛ طبق Runbook Production.

---

## 18) Definition of Done

```text
Code complete
+ Focused tests green
+ Regression tests green
+ Full CI green
+ Migration safety verified
+ Windows Local Gate green
+ Manual Visual/Data QA green
+ User explicit approval
+ Production backup/deploy when production-bound
+ Production smoke/data checks green
+ Docs/Roadmap/Context updated
```

در غیر این صورت Phase وضعیت `PENDING LOCAL QA` یا `IN PROGRESS` دارد.

---

## 19) Current Status — 2026-08-22

**Phase:** `49.3G Workspace Usability + AI Autofill Provenance`  
**GitHub implementation:** COMPLETE ✅  
**Composition regression:** FIXED + REGRESSION TEST ✅  
**Dedicated CI:** Run `32561222101`, Job `97002924663` — SUCCESS ✅  
**Full Phase49 CI:** Run `32561222090`, Job `97002924583` — SUCCESS ✅  
**Validation PR #37:** CLOSED / NOT MERGED ✅  
**Django Migration new in 49.3G:** NONE ✅  
**Windows current runner:** `RUN_PHASE49_3G_LOCAL_GATE.ps1` v`49.3G.0` ✅  
**Windows Automated 49.3G Gate:** PENDING  
**Manual Workspace/Gallery/Provenance QA:** PENDING  
**One real Local Publish:** PENDING  
**Explicit user approval for Production:** PENDING  
**Production:** **UNTOUCHED / NOT APPROVED**

### قدم بعدی دقیق

```text
GitHub latest Epic HEAD
→ Windows git status --short
→ if dirty: STOP + INSPECT
→ git fetch --prune origin
→ git switch epic/phase49-unified-product-slider-sync
→ git pull --ff-only
→ verify RUN_PHASE49_3G_LOCAL_GATE.ps1 = 49.3G.0
→ run .\RUN_PHASE49_3G_LOCAL_GATE.ps1 -LaunchApp
→ Automated Local PASS
→ Manual Workspace/Gallery/AI Provenance QA
→ one real LOCAL PUBLISH ONLY
→ Local Django E2E
→ explicit user approval
→ Production plan/deploy
```

---

## 20) قانون نگهداری این سند

در پایان هر Phase/Hotfix مهم این موارد باید به‌روز شوند:
1. مسیر طی‌شده.
2. Software/path/DB state در صورت تغییر.
3. Incident/Error Ledger.
4. Current Status.
5. Remaining Path.
6. Runtime baseline و CI Run/Job/result.
7. Windows Local Gate result.
8. Production result.

Phase docs جزئیات Implementation را نگه می‌دارند؛ این فایل نقشه Consolidated پروژه و `PROJECT_CONTEXT.md` Snapshot عملیاتی کوتاه‌تر است.
