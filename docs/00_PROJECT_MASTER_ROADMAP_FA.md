# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. Source of Truth اصلی Repository/GitHub است. وضعیت واقعی Git/Database/Server/CI/Local output بر حافظه Chat و متن قدیمی مقدم است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `epic/phase49-unified-product-slider-sync`  
**Current Phase:** `49.3I`  
**Current Hotfix:** `49.3I.5 — Selection Loop Guard + Compact Product Metadata`  
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

قبل از هر Production operation:
- `docs/PATHS.md`
- `docs/HOST_CONSTRAINTS.md`
- DB vendor/name واقعی
- Backup
- Rollback
- Branch/Commit واقعی
باید دوباره Verify شوند.

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
```

Current status:
**49.3I.5 GitHub implementation + final CI SUCCESS; Windows rerun pending; Production untouched.**

---

## 4) معماری عملیاتی

```text
Operator
  ↓
Windows Catalog Center 8.7.1
  ↓
Persistent Catalog SQLite
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

### Discovery
- Explicit Search/Listing/Category URL authoritative.
- Preview Candidate first.
- یک thumbnail + identity/title در Preview.
- Full Fetch فقط Approved.
- image limit پیش‌فرض 10 / حداکثر 20.
- Archive/Not Needed بدون Full Fetch و با blocked identity.
- Dedupe: source + external id + normalized URL.
- Source text sanitation بدون آسیب به URL و Persian editorial fields.

### Product Workspace
- محل canonical همه ویرایش‌های جزئی/تجاری/SEO/قیمت/متریال.
- Products page نباید دوباره به فرم پارامترسنگین تبدیل شود.

### Products Explorer
کارت هر محصول:
- تصویر،
- نام،
- شماره Product ID،
- وضعیت،
- منبع،
- تعداد عکس،
- تاریخ اضافه‌شدن،
- وضعیت انتشار،
- دکمه Edit Product.

View:
- Extra Large,
- Large,
- Medium,
- Small,
- List.

Selection:
- Normal / Ctrl / Shift,
- Select All / Clear,
- Right-click context actions.

Safe queue removal:
- فقط `upload_ready=0`
- فقط `workflow_status=review`
- no delete/block/unpublish/Production.

### Source URL Routing
اگر Source دارای `model_url_pattern` باشد:
- Product URL match → Direct Product Intake.
- Valid non-product URL → Preview Candidate first.
- Full Fetch only after approval.

### Pricing
سه Mode مستقل:
- Fixed
- Range
- Formula/Dynamic

Range نباید Formula را اجرا کند.

### AI
- First paint قبل از synchronous preflight.
- mature 49.3H progress/result/error/cost ledger حفظ شود.
- Cost فقط اگر Provider/response معتبر ارائه کند؛ fabrication ممنوع.

---

## 6) 49.3I.5 — Root Cause و Fix

### ERR-49-022
Windows 49.3I.4 Automated Gate PASS شد، ولی Manual QA نشان داد انتخاب/بازکردن Product می‌تواند Freeze شود.

Root Cause:
```text
Explorer Card
→ hidden Treeview.selection_set()
→ <<TreeviewSelect>>
→ load_product()
→ _phase49_3i_select_product()
→ selection_set()
→ ...
```

Fix:
- card → Treeview فقط یک جهت event-producing است.
- re-entrancy guard.
- selection_set فقط در صورت تفاوت selection.
- load_product فقط state را Sync می‌کند و selection را دوباره نمی‌نویسد.
- Product Open repeat-click guard.
- Tk yield/paint قبل از ساخت Product Workspace.
- Regression Test با Fake Treeview که callback را از selection_set فوراً fire می‌کند و فقط یک write را قبول می‌کند.

هم‌زمان درخواست جدید اپراتور اجرا شد:
- compact metadata روی کارت،
- Persian filters شامل آماده انتشار/صف انتشار/منتشرشده،
- Persian sorts شامل جدیدترین/قدیمی‌ترین/آخرین بروزرسانی.

---

## 7) آخرین Validation واقعی

### Windows 49.3I.4
- HEAD: `7330ad6d79d8061998b1fa143051173b558cefbd`
- 137 Catalog tests PASS
- 419 Django tests PASS, 2 skipped
- Migration changes: NONE
- Production untouched
- Explorer visual rendering corrected
- Selection loop found in manual QA

### GitHub 49.3I.5
CI-only PR `#50`: CLOSED / NOT MERGED.
Runtime base: `cdaac6680ea8545f52ece15ecaa3ce0a575eabe9`.
Marker head: `57813f47f649bb2c415aa0fae1481f4a2561ce1d` — not merged.

Runs:
- Phase49.3I `32580222694` — SUCCESS
- Phase49.3H `32580222686` — SUCCESS
- Phase49.3G `32580222682` — SUCCESS
- Full Phase49 + Full Django `32580222683` — SUCCESS

Migration 49.3I.5: NONE.

---

## 8) Error Knowledge Base

قبل از Troubleshooting همیشه `docs/ERRORS.md` خوانده شود.

Latest relevant:
- ERR-49-017: UX87 composition boundary
- ERR-49-018: AI first-paint
- ERR-49-019: stale Chat SHA handoff
- ERR-49-020: clipped thumbnail Label
- ERR-49-021: Product-vs-Group URL routing
- ERR-49-022: hidden Treeview selection feedback loop

---

## 9) Gate بعدی Windows

قبل از Local Publish:
1. Catalog Center بسته باشد.
2. worktree clean.
3. fetch/prune.
4. pull --ff-only current Epic.
5. Runner v49.3I.5 with `-LaunchApp`.
6. select card → no freeze.
7. Edit Product → exactly one Workspace.
8. right-click Open → exactly one Workspace.
9. compact metadata readable.
10. Ready / Queue / Published filters.
11. Newest / Oldest / Last Updated sorts.
12. Explorer views + Ctrl/Shift + context action regression.
13. Product URL direct vs Group/Search Preview regression.
14. AI first-paint regression.
15. Fixed/Range/Formula regression.

اگر همه PASS شدند:
- یک LOCAL PUBLISH ONLY
- Local Django E2E
- verify product/image/pricing/provenance
- explicit owner approval

---

## 10) Production Gate

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

## 11) Exact Next Step

Windows باید آخرین Epic را با live Git snapshot guard دریافت کند و `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` نسخه 49.3I.5 را اجرا کند. اول interaction loop + metadata/filter/sort QA؛ هنوز Local Publish و Production ممنوع است.
