# 3DPrintHub Desktop Version Registry

این فایل مرجع نسخه‌ی Desktop است. هر تغییر اجرایی Desktop باید با Build جدید، commit دقیق، تست‌های همان Build و وضعیت انتشار ثبت شود.

## وضعیت جاری — Local candidate (2026-10-03)

## وضعیت جاری — Local candidate (2026-10-04)

- نسخه: `v8.9.11`, Build `2026.10.04.2` — اصلاح هویت پایدار عکس در گالری/انتشار؛ مسیر Screenshot عمدی اپراتور بدون تغییر حفظ شده است.
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`; branch: `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`; local/uncommitted.
- Verification: 32 targeted regressions, including all-20-image grid and reopen; compileall, diff-check, fresh temporary empty-Catalog Qt VerifyOnly PASS; read-only Product #964 Gallery/Site/Feed SHA parity PASS.
- وضعیت پذیرش: foreground visual select/delete/reopen هنوز انجام نشده؛ no Catalog write, Host/Production, Instagram, commit/push or deploy.

## وضعیت جاری قبلی — Local candidate (2026-10-03)

- نسخه: `v8.9.11`, Build `2026.10.03.2` — گالری فقط از هویت‌های ثبت‌شدهٔ Product کارت می‌سازد؛ فایل‌های کش شماره‌دارِ باقی‌مانده کارت محلی/قابل‌حذفِ جعلی ایجاد نمی‌کنند. Alias محلی که صریحاً در Product ذخیره شده باشد حفظ می‌شود.
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`; branch: `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD/upstream: `46497ccad3219300aea05a830c625086d79f789b`; uncommitted.
- Verification: gallery/media `33/33`, image recovery `11/11`, compileall, isolated Qt VerifyOnly PASS. Visual UI acceptance pending.
- کلون موقت قبلی نسبت به backup تفاوت منطقی دارد و برای پذیرش تمیز استفاده نمی‌شود؛ canonical Catalog untouched. No commit/push/deploy.

- نسخه: `v8.9.11`, Build `2026.10.03.1` — اصلاح گالری عکس؛ uncommitted روی همان lineage نسخهٔ Build `2026.09.30.4`.
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`; branch: `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD/upstream: `46497ccad3219300aea05a830c625086d79f789b`.
- اصلاح: کارت هر عکس از نگاشت دقیق URL محصول به فایل نهایی استفاده می‌کند، فایل‌های کش شماره‌دار را با ترتیب فهرست جفت نمی‌کند، همهٔ عکس‌های محصول را نگه می‌دارد و حذف را به همان URL/هویت انتخاب‌شده محدود می‌کند.
- آزمون مرتبط: 66/66 پاس؛ compileall/diff-check و Qt VerifyOnly ایزوله نیز پاس شدند. smoke دیداری Gallery هنوز تأیید نشده چون پنجرهٔ candidate در foreground قابل‌مشاهده قرار نگرفت. Catalog اصلی، Host و Production تغییر نکرده‌اند.
- W5C و Desktop acceptance باز است؛ هنوز commit/push نشده.

## وضعیت جاری — Local candidate (2026-09-30)

- نسخه: `v8.9.11`, Build `2026.09.30.4` — تغییرات محلی و هنوز commit/push نشده.
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`; branch: `wip/phase50-a2z-w5-manual-product-20260927`.
- Base HEAD و upstream پیش از این candidate: `46497ccad3219300aea05a830c625086d79f789b`؛ فایل‌های dirty قبلی W5 حفظ شده‌اند.
- تغییر: مسیر خودکار Story قبلی در Popup بازیابی شد و این دکمه حتی تنظیم ذخیره‌شده‌ی Sticker دستی را نادیده می‌گیرد. ارسال مجدد عمدی همان Product/تصویر پس از پایان عملیات مجاز است؛ فقط ارسال هم‌زمان قفل می‌شود.
- آزمون‌ها: Story/Post/Buffer/UI `40 passed, 1 helper deselected`; `compileall`، `git diff --check`، VerifyOnly و سلامت clone/backup پاس شدند. ممیزی read-only اختلاف Hash را به چهار رویداد `product_history` برای Product #862 (یک بازدید و سه پیش‌نمایش Story) نسبت داد؛ Products، AI revisions و sync receipts تغییر نکردند.
- گیت باز: هیچ ارسال واقعی انجام نشده. Computer Use پنجره‌ی native قابل‌کنترل برنگرداند (`apps: []`)، پس بازبینی دیداری Popup و پذیرش Desktop باز است.
- هیچ Catalog اصلی، Host، Production یا GitHub write تغییر نکرده است. Build `.3` هنوز Runtime منتشرشده محسوب نمی‌شود.

## آخرین Build موجود روی branch در GitHub (پذیرش نهایی Desktop در انتظار)

- Build ثبت‌شده در source: `v8.9.11 / 2026.09.29.1`.
- Branch: `wip/phase50-a2z-w5-manual-product-20260927`; exact live GitHub branch SHA: `46497ccad3219300aea05a830c625086d79f789b` (read-only `git ls-remote` verified 2026-09-30).
- `git show` همان SHA تأیید می‌کند Build ID آن commit `2026.09.29.1` است. Build `.3` بالا فقط local candidate است و هنوز روی GitHub نیست.

## آخرین Build همگام با GitHub (پذیرش نهایی Desktop در انتظار)

- Version: `v8.9.11`
- Build: `2026.09.29.1`
- Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`
- Branch: `wip/phase50-a2z-w5-manual-product-20260927`
- Launcher: `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1`
- Desktop shortcut: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk`
- Previous Build: `2026.09.28.1` (local candidate before this hotfix)
- Implementation commit: `46497ccad3219300aea05a830c625086d79f789b` (exact branch SHA checked against live GitHub; historical gate reference `83945715bbe50fb2588fc01abb68be363f308fe5`)

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
