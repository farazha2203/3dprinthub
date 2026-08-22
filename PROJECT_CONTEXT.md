# PROJECT_CONTEXT — 3DPrintHub

> Snapshot عملیاتی Source of Truth. جزئیات Implementation در Phase docs و نقشه مادر `docs/00_PROJECT_MASTER_ROADMAP_FA.md` است. هنگام تعارض: **Migration state واقعی محیط + جدیدترین CI/Local/Host output + این فایل** ملاک است.

## 1) مسیرهای دائمی

- Windows project root: `D:\projects\3DPrintHub`
- Windows virtualenv: `D:\projects\3DPrintHub\.venv`
- Windows Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- Django local DB: `D:\projects\3DPrintHub\db.sqlite3`
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

مسیر تحویل اجباری:

`GitHub Epic → CI/Self-Test → Windows pull --ff-only → Local backup/test → Visual/Data QA → explicit user approval → Production backup/deploy/migrate/collectstatic/restart → smoke/data checks`

قواعد:
- Production قبل از تأیید صریح Local دست نمی‌خورد.
- Source ابتدا GitHub؛ Windows و Host فقط از GitHub نسخه تأییدشده را می‌گیرند.
- فایل/ZIP/Script/Hotfix خارج از Repository مبنای اجرا نیست.
- تغییر باید Minimal و موضعی باشد؛ مسیر Mature باید Extend/Patch/Wrap شود.
- DB برای حل مشکل کد Reset نمی‌شود.
- `reset --hard`, `git clean -fd`, `DROP`, `TRUNCATE`, حذف DB، `.env`, media/private_media و Catalog persistent data Quick Fix مجاز نیست.
- Migration عادی Additive-first است؛ destructive change فاز مستقل + Backup/Dry Run + تأیید می‌خواهد.
- Secret/API Key/Password/Token داخل Git، SQLite audit یا diagnostic export ذخیره نمی‌شود.
- Bugfix باید Regression Test داشته باشد؛ تست واقعی برای سبز کردن CI حذف یا ضعیف نمی‌شود.
- Windows Catalog Center ابزار اصلی اپراتور؛ Django Admin ابزار مدیریتی دوم.
- Python/Django زبان اصلی؛ PowerShell ابزار Windows operations.

Policy: `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`  
Master roadmap: `docs/00_PROJECT_MASTER_ROADMAP_FA.md`

## 3) زنجیره Epic جاری

`49.2A → 49.2B → 49.2C → Epic49 Unified → Persian Sales Hero → Dual Publish → Desktop Options → 49.3A Readiness → 49.3B Guided AI/Hero/Diagnostics → 49.3C Operator Recovery → 49.3C-1 Persian Integrity → 49.3D Workflow Hardening → 49.3D.1 Runner Hotfix → 49.3E AI Task Recovery → 49.3F Product Intelligence/Dynamic Pricing/AI UX → 49.3F Runtime Trace Redaction Hotfix → 49.3F.1 Windows Native stderr Capture Hotfix → 49.3G Workspace Usability + AI Autofill Provenance`

Ancestry خطی نگه‌داری می‌شود؛ Feature جدید داخل Installer مستقل فاز قبلی زنجیر نمی‌شود مگر همان Module صریحاً Composition Root باشد.

## 4) Catalog Center baseline

- Version: `8.7.1`
- Build family: `2026.08.16.3`
- Canonical operator workspace: Epic49 Product Workspace
- Current phase: `49.3G Workspace Usability + AI Autofill Provenance`
- Canonical Windows runner: `D:\projects\3DPrintHub\RUN_PHASE49_3G_LOCAL_GATE.ps1`
- Runner version: `49.3G.0`
- Runner chain: `49.3G → 49.3F.1 → 49.3E → 49.3D.1/base gates`
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

آخرین Windows migration state ثبت‌شده:
- `store.0031`: applied ✅
- `store.0032`: applied ✅
- `website.0022`: applied ✅
- `store.0033`: applied ✅
- `website.0023`: applied ✅

49.3G **Django Migration جدید ندارد**. فقط Catalog SQLite محلی به‌صورت Additive دو ستون عملیاتی دارد:
- `ai_provenance_json`
- `ai_disabled_groups_json`

این داده‌ها مالکیت AI/اپراتور Windows هستند و وارد Schema تجاری Production نشده‌اند.

Production هنوز Phase49.3C تا 49.3G را دریافت نکرده است.

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

## 7) Foundations حفاظت‌شده

- Public external catalog/Link Analyzer intake بازنشسته؛ historical rows حذف نشده‌اند.
- Velzon Django Corporate / RTL admin assets و Customer Portal حفظ شده‌اند.
- Hero Studio visual product/image picker، edit-existing، effect/timing و accessibility fallback حفظ شده‌اند.
- Product SEO و Slider SEO مستقل هستند.
- Local Publish دقیقاً Local؛ Production path جدا و fail-closed است.
- Material/Color operator options و rich color/multi-HEX حفظ شده‌اند.
- Readiness هفت‌مرحله‌ای راهنما است، نه قفل navigation.
- Exact image identity و unselected metadata preservation حفظ شده است.
- Persian Content Guard اجازه English fallback به فیلد فارسی نمی‌دهد.
- Dynamic pricing Source of Truth همان Variant pricing است؛ Product Detail/Cart/Checkout ماشین‌حساب موازی ندارند.

## 8) AI / Diagnostics baseline

Canonical AI providers:
1. AvalAI
2. OpenRouter
3. Google Gemini Direct
4. OpenAI Direct

- raw model ID persist می‌شود، نه Label نمایشی.
- active Provider/Model یک Source of Truth دارد.
- API Keyها در Secure Store/Environment هستند.
- Diagnostics شامل `app_audit_log`, `ai_request_log`, operator/workstation/session, provider/model/request ID/http/duration/tokens/cost است.
- Runtime trace path: `<persistent catalog data>/logs/phase49_3f/YYYY-MM-DD/workflow-<session>.jsonl`.
- Bearer/secret redaction regression-protected است.

`$django-admin-expert`: در Session فعلی Plugin/Skill متناظر پیدا نشد؛ **unavailable in current session** ثبت شده و هیچ ادعای نصب وجود ندارد.

## 9) Phase49.3C / 3D / 3E baseline

49.3C:
- live readiness + exact blocker reasons.
- image exact identity؛ hard cap 10.
- SEO WebP/metadata manifest.
- Persian-only editorial guard + sanitized HTML.

49.3D / 3D.1:
- Tkinter pack/grid collision رفع شد.
- searchable full AI model picker + active provider/model persistence.
- local publish exact preflight reasons.
- semantic image SEO signature.
- professional price range compatibility.
- PowerShell StrictMode array bug رفع شد.

49.3E:
- AI Task Center برای متن فارسی، Product SEO، Image SEO/Metadata، Material recommendation، Slider SEO.
- Manual Image Metadata Editor.
- همه Stageها قابل بازکردن؛ Production همچنان fail-closed.

Historical CI:
- 49.3D: Run `32271502234`, Job `96128806609` — SUCCESS.
- 49.3D.1: Run `32276195521`, Job `96144096195` — SUCCESS.
- 49.3E: Run `32280313257`, Job `96157285817` — SUCCESS.

## 10) Phase49.3F / 49.3F.1 baseline

Canonical doc: `docs/PHASE49_3F_PRODUCT_INTELLIGENCE_PRICING_AI_UX.md`  
Runner hotfix doc: `docs/PHASE49_3F1_WINDOWS_NATIVE_CAPTURE_HOTFIX.md`

Image SEO privacy contract:
- AI فقط روی Selected image slots کار می‌کند.
- Image bytes/file/image URL به AI ارسال نمی‌شود.
- Slot→URL mapping فقط Local است.
- Metadata تصاویر انتخاب‌نشده preserve می‌شود.

Dynamic Pricing:
- strategies: `legacy`, `fixed`, `dynamic`.
- Product Detail/Cart/Checkout از همان Variant price source استفاده می‌کنند.
- acceptance: `2,600,000/kg + 100g part + 50g support×2 + 3h×150k + 3h×50k = 1,120,000 تومان` before extras/shipping.

49.3F.1 Windows incident:
- `store.0033` و `website.0023` واقعاً با `OK` اعمال شدند.
- Failure بعد از Migration در `showmigrations ... 2>&1` زیر PowerShell 5.1 و `$ErrorActionPreference=Stop` بود.
- `Invoke-NativeCapture` خروجی stdout/stderr را با EAP موقت `Continue` می‌گیرد و native exit code را Source of Truth می‌کند.
- DB rollback/reset انجام نشد.

Final CI 49.3F.1:
- Run `32356959599`
- Job `96388108683`
- Overall SUCCESS.
- Validation PR `#36`: closed / not merged.

## 11) Phase49.3G — Workspace Usability + AI Autofill Provenance

Canonical docs:
- `docs/PHASE49_3G_WORKSPACE_USABILITY_AI_PROVENANCE.md`
- `docs/PHASE49_3G_FINAL_VALIDATION.md`

Runtime:
- `catalog_center/app/phase49_3g_workspace_usability.py`
- `catalog_center/app/phase49_3g_commerce_provenance.py`
- `catalog_center/launch.py`

Implemented:
- Workspace vertical scroll + visible scrollbar + mouse wheel.
- Stage rail بیرون viewport و قابل دسترسی.
- Commerce fields/rate table compact؛ Pricing Engine دست‌نخورده.
- Images Gallery یک ردیف افقی با horizontal scrollbar؛ actionهای selected/site/primary/slider/remove/open حفظ شده‌اند.
- Canonical action: `✨ تکمیل هوشمند محصول با AI` روی همان Task Center Mature.
- Provenance groups: `persian_content`, `product_seo`, `image_seo`, `materials`, `slider_seo`.
- per-group `خاموش/روشن AI` و `اجازه بازنویسی AI`.
- Manual edit + Save روی AI-owned field → `manual_override=true`; AI حق overwrite ندارد تا اپراتور صریحاً release کند.
- Commerce page برای Materials Provenance panel دارد.
- قیمت قطعی، تأیید فروش، موجودی، مجوز و Production همیشه operator-owned هستند.
- Image SEO privacy 49.3F بدون تغییر حفظ شده است.

Launcher markers:
- `EPIC49_3G_WORKSPACE_VERTICAL_SCROLL=ENABLED`
- `EPIC49_3G_GALLERY_HORIZONTAL_SCROLL=ENABLED`
- `EPIC49_3G_COMPACT_COMMERCE=ENABLED`
- `EPIC49_3G_AI_AUTOFILL_PROVENANCE=ENABLED`
- `EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED`
- `EPIC49_3G_AI_DISABLE_PER_GROUP=ENABLED`
- `EPIC49_3G_COMMERCE_PROVENANCE=ENABLED`

## 12) Phase49.3G composition-boundary incident

First 49.3G dedicated CI سبز بود ولی Main Phase49 Windows regression خطا گرفت:

`AttributeError: type object 'Workspace' has no attribute 'reload'`

Root Cause:
- نسخه اولیه 49.3G داخل `phase49_3f_source_refresh_guard.install()` زنجیر شده بود.
- تست مستقل Source Refresh 3F عمداً Workspace stub حداقلی دارد و نباید Feature فاز بعد روی آن نصب شود.

Fix صحیح:
- Source Refresh Guard 3F دوباره مستقل شد.
- Cross-phase composition فقط در `catalog_center/launch.py` انجام می‌شود.
- ترتیب واقعی:
  `49.3F Workspace → 49.3F Source Refresh Guard → 49.3G Workspace Usability → 49.3G Commerce Provenance`.
- Regression test قفل می‌کند که 3G دوباره داخل Installer مستقل 3F وارد نشود.

Do Not Repeat:
- Feature جدید را داخل Installer یک Module مستقل قدیمی زنجیر نکن اگر آن Module unit/contract مستقل دارد؛ Composition بین Phaseها در Launcher/Composition Root انجام شود.

## 13) Phase49.3G Final GitHub Validation

Runtime baseline تأییدشده قبل از docs-only commits:
`88c19d0ab9a5ed416479f65c30b8a6ed8cf0153d`

Dedicated 49.3G:
- Run `32561222101`
- Job `97002924663`
- PowerShell runner contract ✅
- Compile ✅
- dedicated tests ✅
- launcher markers ✅
- no Django migration drift ✅
- Overall **SUCCESS**

Full Phase49:
- Run `32561222090`
- Job `97002924583`
- PowerShell runner contract ✅
- Compile ✅
- Django check/migration contract ✅
- Phase49 behavioral/regression tests ✅
- Windows Catalog Center Epic49 ✅
- Full Django suite ✅
- Overall **SUCCESS**

Validation PR `#37`: **closed / not merged**.

## 14) Warnings شناخته‌شده

غیر-Failure:
- `3dprinthub.W001`: Google membership credentials خالی.
- `ckeditor.W001`: CKEditor4 technical/security debt.
- `store.W026`: in-memory realtime؛ multi-process Production به Redis/polling strategy نیاز دارد.
- Pillow `Image.getdata()` deprecation.

هیچ‌کدام blocker 49.3G نیستند و برای رفعشان معماری unrelated تغییر نمی‌کند.

## 15) Separate open technical item

Local logs قبلاً `GET /api/v1/catalog/sitemap/ → 404` نشان دادند. این defect با 49.3G یکی نیست و قبل از closure کامل Epic باید Root Cause Route/client contract آن بررسی شود؛ endpoint موازی بی‌دلیل ساخته نشود.

## 16) Gate فعلی — Windows Local Phase49.3G

Canonical runner:
`D:\projects\3DPrintHub\RUN_PHASE49_3G_LOCAL_GATE.ps1` — version `49.3G.0`.

Runner باید:
1. Gate کامل 49.3F.1 را chain کند.
2. project path/venv/source files را verify کند.
3. compile 49.3G را اجرا کند.
4. dedicated 49.3G tests را اجرا کند.
5. launcher markers را verify کند.
6. final Git worktree را clean بررسی کند.
7. هیچ Reset/Delete/Production action انجام ندهد.

Manual acceptance:
- Commerce/Product pages با mouse wheel و scrollbar عمودی کامل قابل پیمایش.
- Commerce compact و Pricing/Material rate usable.
- Gallery یک strip افقی با scrollbar؛ 12+ تصویر بدون فشردگی چندردیفه.
- selected/site/primary/slider/remove/open actionها سالم.
- Task Center ownership suffixهای AI/manual/disabled را نشان دهد.
- `تکمیل هوشمند محصول با AI` فقط فیلدهای خالی و مجاز را پر کند.
- AI هیچ‌وقت price approval/license/inventory/Production را خودکار تغییر ندهد.
- خاموش کردن یک group مانع تغییر همان group در اجرای بعدی شود.
- تغییر دستی AI-owned field + Save، group را Manual Override کند.
- `اجازه بازنویسی AI` تنها راه release قفل باشد.
- Image SEO selected-only + text-only باقی بماند؛ unselected metadata تغییر نکند.

## 17) Current checklist

- [x] Phase49.3D/3D.1 GitHub CI complete.
- [x] Phase49.3E GitHub CI complete.
- [x] Phase49.3F/3F.1 implementation + CI complete.
- [x] Windows `store.0033` / `website.0023` applied.
- [x] Phase49.3G implementation complete.
- [x] Phase49.3G composition regression Root Cause fixed + regression test.
- [x] Phase49.3G Dedicated CI SUCCESS — Run `32561222101`, Job `97002924663`.
- [x] Phase49 Full Regression SUCCESS — Run `32561222090`, Job `97002924583`.
- [x] Validation PR `#37` closed / not merged.
- [ ] Windows pull latest Epic.
- [ ] `RUN_PHASE49_3G_LOCAL_GATE.ps1` automated Local Gate PASS.
- [ ] Phase49.3G manual Workspace/Gallery/AI Provenance QA.
- [ ] Real-provider AI QA where credentials exist.
- [ ] One real **LOCAL PUBLISH ONLY** E2E.
- [ ] Local Django Product/Profile/Hero/Home/Store/Admin verification.
- [ ] Explicit user approval.
- [ ] Production deploy.

## 18) Production status

**NOT DEPLOYED / NOT APPROVED / UNTOUCHED.**

هیچ deploy/migrate/collectstatic/restart مربوط به Phase49.3C تا 49.3G در Production اجرا نشده است. Production فقط پس از Automated Local Gate + Manual Visual/Data QA + Local Publish E2E + تأیید صریح کاربر وارد برنامه Deploy می‌شود.

## 19) قدم بعدی دقیق

```text
GitHub latest Epic HEAD
→ Windows git status --short
→ dirty? STOP/INSPECT (no reset/delete)
→ git fetch --prune origin
→ switch epic/phase49-unified-product-slider-sync
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

اگر Windows Local Gate Regression جدیدی نشان دهد، فقط Root Cause همان مورد با Minimal Change + Regression Test روی GitHub اصلاح می‌شود؛ Windows patch دستی یا بازنویسی کلی معماری ممنوع است.
