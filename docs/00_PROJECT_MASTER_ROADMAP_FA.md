# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.6 — Secure Credential Field Persistence`  
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
- Secret/API key/token/password در Git/log/chat ذخیره نمی‌شود.
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
→ 49.3I.6 Secure Credential Field Persistence
```

Current status:
**49.3I.6 final GitHub CI SUCCESS; Windows secure-credential QA pending; Production untouched.**

---

## 4) معماری عملیاتی

```text
Operator
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite + Windows Credential Store
  ↓
Discovery Preview / Product Workspace / AI / Pricing / Image Pipeline
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

## 5) قراردادهای اصلی Phase49.3I

### Discovery / Routing
- Explicit Search/Listing/Category URL authoritative.
- Preview Candidate first.
- یک thumbnail + identity/title در Preview.
- Full Fetch فقط Approved.
- image limit پیش‌فرض 10 / حداکثر 20.
- Archive/Not Needed بدون Full Fetch و با blocked identity.
- Dedupe: source + external id + normalized URL.
- Source text sanitation بدون آسیب به URL و Persian editorial fields.
- Source `model_url_pattern` مرز Product URL و Group/Category/Search URL است.

Owner بعد از 49.3I.5 تأیید کرده مشکل لینک و زیرشاخه‌ها روی Windows درست شده است.

### Product Workspace / Explorer
- Product Workspace محل canonical همه ویرایش‌های جزئی/تجاری/SEO/قیمت/متریال است.
- Products Explorer visual/lightweight باقی می‌ماند.
- کارت شامل تصویر، نام، Product ID، وضعیت، منبع، تعداد عکس، تاریخ اضافه‌شدن، وضعیت انتشار و Edit Product است.
- View: Extra Large / Large / Medium / Small / List.
- Selection: Normal / Ctrl / Shift + Select All / Clear + right-click actions.
- Safe queue removal فقط `upload_ready=0` و `workflow_status=review`؛ no delete/block/unpublish/Production.

### Selection Stability — ERR-49-022
- card → hidden Treeview فقط یک جهت event-producing است.
- re-entrancy guard.
- selection_set فقط در صورت تفاوت selection.
- reverse Treeview callback فقط state را Sync می‌کند.
- Product Open repeat-click guard + Tk yield/paint.

### Secure Credentials — ERR-49-023
Source of truth امن:
**Windows Credential Store / environment**.

49.3I.6:
- FTP password و Bridge token را در Startup به فیلد Masked برمی‌گرداند.
- AI key مربوط به Provider انتخاب‌شده را Hydrate می‌کند.
- بعد از Save که Mature handler فیلد را پاک می‌کند، مقدار ذخیره‌شده امن دوباره Masked نمایش داده می‌شود.
- Provider switch کلید همان Provider را برمی‌گرداند.
- refresh معمول همان Provider، مقدار Unsaved جدید را overwrite نمی‌کند.
- Explicit delete/clear حفظ شده است.
- Secret در SQLite/Git/source/log/diagnostics ذخیره نمی‌شود.

### Pricing / AI
- Fixed / Range / Formula مستقل.
- Range نباید Formula را اجرا کند.
- AI First Paint قبل از synchronous preflight.
- mature 49.3H progress/result/error/cost stack حفظ می‌شود.
- Cost ساختگی ممنوع.

---

## 6) آخرین Validation واقعی

### Windows
- 49.3I.5 Launch موفق.
- owner تأیید کرده Product URL vs Group/Category/Search/sub-branch routing درست شده.
- 49.3I.6 هنوز روی Windows pull/test نشده است.

### GitHub 49.3I.6
CI-only PR `#51`: CLOSED / NOT MERGED.
Validated Epic base: `f1e92f8f42a6ed90bf1001dc14a15638828ee341`.
Marker head: `fa8e4bcf5f7795983434f7cfd34c88918273bae6` — not merged.

Runs:
- Phase49.3I `32583277412` — SUCCESS
- Phase49.3H `32583277584` — SUCCESS
- Phase49.3G `32583277406` — SUCCESS
- Full Phase49 + Full Django `32583277418` — SUCCESS

Migration 49.3I.6: NONE.
Production: UNTOUCHED.

---

## 7) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.

Latest relevant:
- ERR-49-017: UX87 composition boundary
- ERR-49-018: AI first-paint
- ERR-49-019: stale Chat SHA handoff
- ERR-49-020: clipped thumbnail Label
- ERR-49-021: Product-vs-Group URL routing
- ERR-49-022: hidden Treeview selection feedback loop
- ERR-49-023: secure credentials not hydrated into masked fields

---

## 8) Gate بعدی Windows

قبل از Local Publish:
1. Catalog Center بسته باشد.
2. worktree clean.
3. fetch/prune.
4. pull --ff-only current Epic.
5. Runner v49.3I.6 with `-LaunchApp`.
6. AI key بعد از Save باید Masked باقی بماند.
7. Restart باید AI key ذخیره‌شده را برگرداند.
8. Provider switch باید Key همان Provider را برگرداند.
9. FTP password + Bridge token بعد از Save/Restart باید Masked باقی بمانند.
10. AI/FTP/Bridge live tests باید با secure credentials کار کنند.
11. Selection/Open بدون Freeze.
12. Product URL direct vs Group/Search Preview regression.
13. AI first-paint regression.
14. Fixed/Range/Formula regression.

اگر همه PASS شدند:
- یک LOCAL PUBLISH ONLY
- Local Django E2E
- verify product/image/pricing/provenance
- explicit owner approval

---

## 9) Production Gate

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

## 10) Exact Next Step

Windows باید آخرین Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.6 را اجرا کند. تمرکز QA فعلی روی Secure Credential Save/Restart/Provider-Switch است؛ هنوز Local Publish و Production ممنوع است.
