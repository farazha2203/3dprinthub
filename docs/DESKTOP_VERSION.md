# 3DPrintHub Desktop Version Registry

این فایل مرجع نسخه‌ی Desktop است. هر تغییر اجرایی Desktop باید با Build جدید، commit دقیق، تست‌های همان Build و وضعیت انتشار ثبت شود.

## آخرین Build همگام با GitHub (پذیرش نهایی Desktop در انتظار)

- Version: `v8.9.11`
- Build: `2026.09.29.1`
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`
- Branch: `wip/phase50-a2z-w5-manual-product-20260927`
- Launcher: `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1`
- Desktop shortcut: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk`
- Previous Build: `2026.09.28.1` (local candidate before this hotfix)
- Implementation commit: `83945715bbe50fb2588fc01abb68be363f308fe5` (Local=GitHub exact SHA PASS)

## Changes in Build 2026.09.29.1

- Fixed the exact-saved-model AI wrapper so explicit `model_info` is forwarded during provider discovery/connection testing; Product execution still uses the saved model and does not perform hidden model listing.
- W5C regression evidence is recorded in `docs/phases/PHASE50_A2Z_W5C_REGRESSION_EVIDENCE_20260929.md`.
- Focused ordered provider/Avalai/Story/Post tests: `37/37 PASS`; Python compile and diff-check PASS.
- The full suite was captured before this fix at 971 tests / 12 failures / 15 errors; 12 failures and 14 error events reproduce on the exact parent. One extra v84 interaction error was fixed and passed in the ordered focused run.
- Historical About entries retain exact Build IDs only where verified; Sep 27 records explicitly say the exact ID was not recorded rather than displaying the current Build ID.
- Isolated Qt VerifyOnly passed (`QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK`) on a disposable backup clone; backup `quick_check` and `integrity_check` passed. No canonical Catalog mutation.
- GitHub source gate passed; final foreground Desktop acceptance remains pending because the available Remote Desktop Commander exposes no screenshot/window-control API. No Instagram send, canonical Catalog mutation, Host or Production operation occurred.

## Changes in Build 2026.09.28.1 (previous build)

- OpenRouter Image discovery and independent Image Model are active.
- One isolated Seedream 4.5 generation completed and was stored as a SQLite BLOB.
- No-invention prompt and request-fingerprint idempotency passed.
- Explicitly approved/selected SQLite revisions are handed off to existing Story/Post preparation.
- No canonical Catalog, Instagram, Host or Production mutation occurred.

## Version rules

1. Keep `APP_VERSION` for the product line and increase `BUILD_ID` for every executable behavior change.
2. Record the exact branch, commit, tests, backup and remaining gates here and in About history.
3. Never record secrets or Credential Store values.
4. Do not mark a Build released until Local tests, backup, regression and GitHub exact-SHA verification pass.
