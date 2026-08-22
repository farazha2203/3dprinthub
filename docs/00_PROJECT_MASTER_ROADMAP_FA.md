# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.7 — Preview + Provider Hub Recovery`  
**Windows Operator:** Catalog Center 8.7.1  
**Backend:** Django / Python  
**Production:** تا Local QA + Local Publish E2E + تأیید صریح مالک پروژه ممنوع.

---

## 1) قانون مادر

```text
READ DOCS
→ VERIFY REAL STATE
→ CHECK PREVIOUS ERRORS
→ IMPLEMENT ON GITHUB
→ CI
→ WINDOWS PULL --FF-ONLY
→ LOCAL AUTOMATED GATE
→ MANUAL VISUAL/DATA/INTERACTION QA
→ LOCAL PUBLISH E2E
→ EXPLICIT OWNER APPROVAL
→ PRODUCTION BACKUP/DEPLOY
→ PRODUCTION VERIFICATION
→ UPDATE DOCS
```

قواعد ثابت:
- Mature behavior باید Extend/Patch/Wrap شود؛ بازنویسی موازی بدون دلیل ممنوع.
- Bugfix بدون Regression Test کامل نیست.
- Source Code دائمی روی Production ویرایش نمی‌شود.
- ZIP/Patch/Source مستقل از Repository مسیر تحویل نیست.
- Dirty Local/Host = STOP/INSPECT؛ reset/stash/delete Quick Fix ممنوع.
- Migrationها Additive-first؛ destructive فقط با Target/Backup/Rollback verified.
- Secret/API key/token/password در Git/log/chat/SQLite ذخیره نمی‌شود.
- SHA ثابت در Chat Source of Truth یک Branch متحرک نیست؛ Snapshot باید بعد از `git fetch` واقعی از `origin/<branch>` Verify شود.

Policy: `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`.

---

## 2) مسیرهای ثبت‌شده

### Windows
```text
Project:             D:\projects\3DPrintHub
Venv:                D:\projects\3DPrintHub\.venv
Catalog Center:      D:\projects\3DPrintHub\catalog_center
Django SQLite:       D:\projects\3DPrintHub\db.sqlite3
Catalog persistent:  D:\projects\3dprinthub-catalog-manager
Catalog SQLite:      D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
Legacy retained:     D:\projects\3dprinthub_catalog_center
Backups:             D:\projects\3dprinthub-backups
```

### Production
```text
Project:       /home/sfkilvrs/3dprinthub
Venv:          /home/sfkilvrs/virtualenv/3dprinthub/3.12
Database:      MySQL sfkilvrs_EmiAdmin_3dprinthub
Static:        /home/sfkilvrs/public_html/static
Media:         /home/sfkilvrs/public_html/media
Private media: /home/sfkilvrs/3dprinthub/private_media
```

قبل از هر Production operation باید `docs/PATHS.md`، `docs/HOST_CONSTRAINTS.md`، DB vendor/name واقعی، Backup، Rollback و Branch/Commit واقعی دوباره Verify شوند.

---

## 3) Epic49 Path

```text
49.2A
→ 49.2B
→ 49.2C
→ Epic49 Unified Product/Slider Sync
→ Persian Sales Hero
→ Dual Publish Targets
→ Desktop Options
→ 49.3A Readiness
→ 49.3B Guided AI / Hero / Diagnostics
→ 49.3C Operator Recovery
→ 49.3C-1 Persian Content Integrity
→ 49.3D Workflow Hardening
→ 49.3D.1 Windows Runner Hotfix
→ 49.3E AI Task Recovery
→ 49.3F Product Intelligence / Dynamic Pricing / AI UX
→ 49.3F Runtime Trace Redaction
→ 49.3F.1 Native stderr Capture Hotfix
→ 49.3G Workspace Usability + AI Provenance
→ 49.3H SEO Execution + AI Cost + Controlled Image Intake
→ 49.3I Discovery Review + Product Gallery + Explicit Pricing
→ 49.3I.1 Windows PowerShell 5.1 Encoding Guard
→ 49.3I.2 Real UX87 Product Gallery + AI First-Paint
→ 49.3I.3 Live GitHub Snapshot Handoff Guard
→ 49.3I.4 Explorer Product Gallery + Source URL Routing
→ 49.3I.5 Selection Loop Guard + Compact Product Metadata
→ 49.3I.6 Initial Secure Credential Field Persistence
→ 49.3I.7 Preview + Provider Hub Recovery
```

Current status:
**49.3I.7 final GitHub CI SUCCESS; Windows QA pending; Production untouched.**

---

## 4) معماری عملیاتی

```text
Operator
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite + Windows Credential Store
  ↓
Search/Listing Discovery Preview
  ↓
Approve / Archive
  ↓
Approved Full Fetch (mature extractor)
  ↓
Product Workspace / AI / Pricing / Image Pipeline
  ↓
LOCAL PUBLISH ONLY
  ↓
Local Django SQLite
  ↓
Local Store/Admin/E2E Verification
  ↓
Explicit Owner Approval
  ↓
GitHub-approved Commit
  ↓
Production Host pulls from GitHub
  ↓
MySQL + Passenger/LiteSpeed
  ↓
Production Verification
```

Production هیچ‌وقت مستقیماً Source of Development نیست.

---

## 5) قرارداد Discovery / Business Workflow

Workflow canonical:

```text
Exact Search / Listing / Category URL
→ Preview Candidate
→ one thumbnail + basic identity/title/url
→ Operator Approve or Archive
→ Approved only: mature Full Fetch
→ selected image limit 1..20 (default 10)
→ Product Workspace
```

قواعد:
- لینک صریح اپراتور authoritative است.
- Source `model_url_pattern` مرز Product URL و Group/Category/Search/sub-branch است.
- Product URL → mature Direct Product intake.
- Non-product URL → Preview first.
- Preview حق Full Fetch ندارد.
- Archive/Not Needed حق Full Fetch ندارد.
- Dedupe: source + external id + normalized URL.
- Source text sanitation بدون آسیب به URL و Persian editorial fields.

Owner قبلاً تأیید کرده Product-vs-Group/sub-branch routing روی Windows درست شده است.

---

## 6) 49.3I.7 Preview Recovery — ERR-49-024

Windows log واقعی:
- `PHASE49_3I_URL_ROUTE=preview_listing`
- exact MakerWorld target درست بود.
- `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`
- `candidates=0 failed=1 full_fetch=0`

Root Cause:
- Stage-1 Preview یک JavaScript expression را داخل Python normal triple-quoted string ساخته بود.
- escape مورد انتظار JavaScript برای `\n` قبل از Playwright به literal newline تبدیل شد.
- Browser یک newline نامعتبر داخل JavaScript single-quoted string دریافت کرد.

Fix:
- `catalog_center/app/phase49_3i_preview_recovery.py`
- raw Python JavaScript string با escape صحیح.
- reuse از `candidates_from_dom_rows()`.
- فقط Preview boundary عوض شده است.
- `classic_methods.discover_classic` و `collect_classic_exact` و mature Direct/Full Fetch دست نخورده‌اند.

Prevention:
- هر JavaScript embedded در Python که به Playwright داده می‌شود باید regression test روی source escaping داشته باشد.

---

## 7) Secure Credentials + AI Provider Hub — ERR-49-023 / ERR-49-025

Secure Source of Truth:
**Windows Credential Store / environment**.

Providerهای فعلی:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

49.3I.6 فقط legacy `ai_key` + FTP password + Bridge token را Hydrate کرد و Windows QA نشان داد real Provider cards هنوز کامل پوشش داده نشده‌اند.

49.3I.7:
- real `_ai_hub_key_vars` هر Provider را از secure store Hydrate می‌کند.
- mature Provider Save اگر widget را clear کند، مقدار secure دوباره Masked نمایش داده می‌شود.
- FTP password + Bridge token hydration حفظ شده.
- stored OpenRouter management/OpenAI admin fields نیز Masked hydrate می‌شوند.
- Unsaved non-empty input overwrite نمی‌شود.
- Secret در SQLite/Git/source/log ذخیره نمی‌شود.

### Provider Model Visibility
Existing mature `AIProviderClient` / Google adapter authoritative باقی می‌ماند.

49.3I.7 برای Providerهایی که key امن دارند:
- model catalog را background-load می‌کند.
- existing Model ID combobox/cache/status را پر می‌کند.
- manual model picker / API refresh را حفظ می‌کند.

هیچ AI client موازی جدیدی ساخته نشده است.

---

## 8) Product Workspace / Explorer

Preserved:
- Product Workspace محل canonical ویرایش‌های جزئی/تجاری/SEO/قیمت/متریال.
- Explorer visual/lightweight.
- کارت: تصویر، نام، Product ID، وضعیت، منبع، تعداد عکس، تاریخ اضافه‌شدن، وضعیت انتشار، Edit Product.
- View: Extra Large / Large / Medium / Small / List.
- Selection: Normal / Ctrl / Shift + Select All / Clear + context actions.
- Safe queue removal فقط `upload_ready=0` و `workflow_status=review`.
- no delete/block/unpublish/Production.
- selection feedback-loop guard حفظ شده.

---

## 9) Pricing / AI Execution

Pricing modeها مستقل:
- Fixed
- Range
- Formula / Dynamic

Range نباید Formula را اجرا کند.

AI:
- First Paint قبل از synchronous preflight.
- mature 49.3H progress/result/error/cost stack حفظ می‌شود.
- Provider cost ساختگی ممنوع.

---

## 10) آخرین Validation واقعی

### GitHub 49.3I.7
CI-only PR `#52`: CLOSED / NOT MERGED.
Validated runtime base: `4e0b1b7f0f8934a03ab74037bdce5f9abe55b425`.
Marker head: `5097f45f069e40af64d452ffaa8cd07399a977f2` — not merged.

Runs:
- Phase49.3I `32585956198` — SUCCESS
- Phase49.3H `32585956149` — SUCCESS
- Phase49.3G `32585956156` — SUCCESS
- Full Phase49 + Full Django `32585956155` — SUCCESS

Verified:
- Runner v49.3I.7 ASCII-only Windows PS5.1.
- live Git snapshot guard.
- Preview JS escaping.
- Preview layer no full-fetch calls.
- real Provider Hub secure hydration.
- Provider model catalog loading/cache/combobox.
- prior Explorer/selection/routing regressions.
- Django migration: NONE.
- Catalog schema migration: NONE.
- Full Django suite PASS.

Post-validation commits are documentation-only.
Production: UNTOUCHED.

---

## 11) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.

Latest relevant:
- ERR-49-013: exact Search URL ignored
- ERR-49-014: Full Fetch before Preview approval
- ERR-49-018: AI first-paint
- ERR-49-019: stale Chat SHA
- ERR-49-020: clipped thumbnails
- ERR-49-021: Product-vs-Group routing
- ERR-49-022: Treeview selection loop
- ERR-49-023: initial secure-field hydration gap
- ERR-49-024: Preview Playwright JavaScript escape regression
- ERR-49-025: real Provider Hub key/model visibility gap

---

## 12) Gate بعدی Windows

قبل از Local Publish:
1. Catalog Center بسته باشد.
2. worktree clean.
3. `git fetch --prune origin`.
4. `git pull --ff-only` current Epic.
5. Runner v49.3I.7 با `-LaunchApp`.
6. FTP password + Bridge token بعد از Save/Restart Masked باقی بمانند.
7. AvalAI/OpenRouter saved key در real Provider cards بعد از Restart Masked دیده شوند.
8. Provider model lists داخل برنامه load و selectable باشند.
9. exact MakerWorld Search URL بدون `Locator.evaluate_all SyntaxError` Preview candidate بدهد.
10. Preview فقط one thumbnail/basic identity باشد.
11. یک Candidate با image limit=20 Approve شود؛ فقط بعد از Approval Full Fetch اجرا شود.
12. یک Candidate Archive شود؛ Full Fetch نشود.
13. Direct Product URL mature path همچنان کار کند.
14. Product Open / AI first-paint / Fixed-Range-Formula regression QA.

اگر همه PASS شدند:
- دقیقاً یک `LOCAL PUBLISH ONLY`
- Local Django E2E
- verify product/image/pricing/provenance
- explicit owner approval

---

## 13) Production Gate

Production فعلاً `UNTOUCHED / NOT APPROVED` است.

قبل از Deploy:
- owner approval صریح،
- Host read-only state verify،
- branch/commit verify،
- MySQL vendor/name verify،
- backup + rollback verify،
- GitHub pull only،
- deploy،
- production verification،
- docs final update.

---

## 14) Exact Next Step

Windows باید آخرین Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.7 را اجرا کند. تمرکز QA: secure Provider cards + model lists + exact MakerWorld Preview → Approve → Full Fetch. هنوز Local Publish و Production ممنوع است.
