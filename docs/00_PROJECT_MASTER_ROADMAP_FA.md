# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.8 — Observable AI Execution Recovery`  
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
→ 49.3I.8 Observable AI Execution Recovery
```

Current status:
**49.3I.8 final GitHub CI SUCCESS; Windows interaction/source QA pending; Production untouched.**

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
Product Workspace
  ↓
Mature AI Task Center / Pricing / Image Pipeline
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

## 5) Discovery / Business Workflow

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
- Preview و Archive حق Full Fetch ندارند.
- Dedupe: source + external id + normalized URL.
- Source text sanitation بدون آسیب به URL و Persian editorial fields.

49.3I.7 `ERR-49-024` فقط Playwright Stage-1 Preview expression را اصلاح کرد؛ mature Direct/approved Full Fetch را بازنویسی نکرد. 49.3I.8 این قرارداد را حفظ و regression-test کرده است.

---

## 6) Secure Credentials + Provider Model Visibility

Source of Truth امن:
**Windows Credential Store / environment**.

Providerها:
- AvalAI
- OpenRouter
- Google Gemini Direct
- OpenAI Direct

49.3I.7 / `ERR-49-025`:
- real `_ai_hub_key_vars` را Hydrate می‌کند.
- بعد از mature secure Save فیلد Masked دوباره مقدار امن را نشان می‌دهد.
- FTP password + Bridge token حفظ می‌شوند.
- stored management/admin keys در secure store می‌مانند.
- Provider model catalogs با existing `AIProviderClient` / Google adapter background-load می‌شوند.
- Model ID combobox/cache/model picker از همان مسیر mature استفاده می‌کنند.
- Secret در SQLite/Git/source/log ذخیره نمی‌شود.

---

## 7) Observable AI Execution — ERR-49-026

### Windows Evidence
دکمه واقعی پایین Product Workspace یعنی `تکمیل هوشمند همه فیلدهای AI` حدود پنج دقیقه روی AvalAI content generation ماند و مسیر connection/send/receive/save/result برای اپراتور دیده نمی‌شد.

### Root Cause
Phase49.3C `_phase49_3c_all_ai()` هنوز legacy `ProductStudio.generate_ai("commerce")` را صدا می‌زد و mature `_phase49_3e_run_ai()` را bypass می‌کرد.

پس این دکمه واقعی از این قابلیت‌های موجود عبور نمی‌کرد:
- 49.3I First Paint،
- 49.3F connection/send/receive progress،
- 49.3H result/error/cost visibility.

### 49.3I.8 Fix
`catalog_center/app/phase49_3i_ai_execution_recovery.py`:
- real bottom All-Fields → `_phase49_3e_run_ai("all")`.
- non-Quick stage AI → mature Task Center؛ image scope حفظ می‌شود.
- Quick/title-only path حفظ می‌شود.
- AI client یا network worker دوم ساخته نمی‌شود.
- elapsed time همیشه در progress دیده می‌شود.
- `توقف انتظار` اضافه شده.
- watchdog اپراتوری 210 ثانیه است و با upper-bound فعلی یک AI request هماهنگ است.
- هر execution generation-tag دارد.
- Cancel/Timeout generation را stale می‌کند.
- Late stale result حق اعمال روی Product/Image ندارد.
- Error/Result visible می‌ماند و App بسته نمی‌شود.

Blocking HTTP worker force-kill نمی‌شود؛ اگر دیرتر تمام شود نتیجه آن بعد از Cancel/Timeout discard می‌شود.

---

## 8) Product Workspace / Explorer / Pricing

Preserved:
- Product Workspace محل canonical ویرایش‌های جزئی/تجاری/SEO/قیمت/متریال.
- Explorer visual/lightweight.
- کارت: تصویر، نام، Product ID، وضعیت، منبع، تعداد عکس، تاریخ اضافه‌شدن، وضعیت انتشار، Edit Product.
- View: Extra Large / Large / Medium / Small / List.
- Selection: Normal / Ctrl / Shift + Select All / Clear + context actions.
- selection feedback-loop guard.
- Safe queue removal فقط local queue state را تغییر می‌دهد.

Pricing modeها مستقل:
- Fixed
- Range
- Formula / Dynamic

Range نباید Formula را اجرا کند.

---

## 9) آخرین Validation واقعی

### GitHub 49.3I.8
CI-only PR `#53`: CLOSED / NOT MERGED.
Validated runtime base: `3fdab5dc4a56204b6370f72df04ec0956e8ba6ce`.
Marker head: `0d05d0fb25f02daa07df93f9cf47d2ea0333b8b8` — not merged.

Runs:
- Phase49.3I `32620646603` — SUCCESS
- Phase49.3H `32620646600` — SUCCESS
- Phase49.3G `32620646605` — SUCCESS
- Full Phase49 + Full Django `32620646657` — SUCCESS

Verified:
- Runner v49.3I.8 ASCII-only Windows PS5.1.
- live Git snapshot guard.
- exact visible All-Fields → mature Task Center routing.
- non-Quick stage routing + Quick path preservation.
- elapsed/watchdog/stale-result safety.
- no duplicate AI worker/client in recovery layer.
- Preview recovery remains active.
- Provider key/model visibility regressions.
- Explorer/selection/source-routing regressions.
- Django migration: NONE.
- Catalog schema migration: NONE.
- Full Django suite PASS.

Production: UNTOUCHED.

---

## 10) Error Knowledge Base

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
- ERR-49-026: real bottom All-Fields action bypassed mature Task Center

---

## 11) Gate بعدی Windows

قبل از Local Publish:
1. Catalog Center بسته باشد.
2. worktree clean.
3. `git fetch --prune origin`.
4. `git pull --ff-only` current Epic.
5. Runner v49.3I.8 با `-LaunchApp`.
6. دکمه **پایین** All-Fields AI باید First Paint فوری بدهد.
7. Progress باید connection → send → wait/receive → save → result/error را نشان دهد.
8. elapsed time + `توقف انتظار` visible باشد و UI responsive بماند.
9. Stop/210s timeout باید Late Result را non-applicable کند.
10. exact MakerWorld Search URL بدون `Locator.evaluate_all SyntaxError` Preview candidate بدهد.
11. Preview فقط one thumbnail/basic identity باشد.
12. یک Candidate با image limit=20 Approve شود؛ فقط بعد از Approval Full Fetch اجرا شود.
13. یک Candidate Archive شود؛ Full Fetch نشود.
14. Provider keys/model lists + FTP/Bridge حفظ شوند.
15. Product Open/Selection و Fixed/Range/Formula regression QA.

اگر همه PASS شدند:
- دقیقاً یک `LOCAL PUBLISH ONLY`
- Local Django E2E
- verify product/image/pricing/provenance
- explicit owner approval

---

## 12) Production Gate

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

## 13) Exact Next Step

Windows باید آخرین Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.8 را اجرا کند. تمرکز QA فعلی: real bottom AI execution visibility + MakerWorld Preview → Approve → mature Full Fetch. هنوز Local Publish و Production ممنوع است.
