# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.14 — Restore Mature Scan Controls + Single-Product Route`
Status: `GITHUB_UPDATED / PR #60 MERGED / ALL REQUIRED CI SUCCESS / FOCUSED WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Real Windows QA after 49.3I.13 exposed the final Catalog release blocker:
- Phase49.3I.12 had hidden healthy mature controls including `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک` and `کشف جدیدها`,
- the earlier Preview layer had shadowed `App87.start_scan`, so simply showing the old button would still call Preview instead of the mature collector,
- the new manual `دریافت محصول تکی` forced Rich Direct Intake / `RichPageExtractor`; a correct MakerWorld product URL returned `RuntimeError: HTTP 403` while the mature top scan path had previously worked.

Canonical incident: `ERR-49-032`.

## Phase49.3I.14 Final Delta
PR #60 is merged. The fix is intentionally narrow:
- restore the mature top action set,
- bind visible `شروع اسکن` to the original BaseApp mature `start_scan/_scan_worker`,
- route manual `دریافت محصول تکی` through the same mature `mode=single` scan path after Product URL validation,
- keep `دریافت هوشمند از لینک` as an optional separate Rich Direct tool,
- preserve exact-page Preview / Approve / Archive / Paste / Candidate Error Detail,
- preserve AI/provider/pricing/SEO/publish/FTP/Bridge behavior,
- add no new crawler/extractor.

## Validation
Final PR head: `f12a25e1fe50fb16a03a1324c84912c830a2608e`.
Merge commit: `124662cf2436dfcce245282b01b2da694802aa55`.

Successful workflows on the final PR head:
- Phase49.3I.14 Legacy Scan Restore `32636771174` — SUCCESS,
- Phase49.3I `32636771071` — SUCCESS,
- Phase49.3H `32636771154` — SUCCESS,
- Phase49.3G `32636771049` — SUCCESS,
- Full Phase49 + Full Django `32636771103` — SUCCESS.

An earlier targeted CI run correctly caught an MRO resolver defect (`preview-started` instead of `legacy-started`). The resolver was changed before fresh CI; the final CI set above is green.

## Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no DB reset/drop/truncate,
- no candidate/history/media rewrite/delete,
- no credential changes,
- Production untouched.

## Focused Windows Gate — NEXT
1. close Catalog Center completely,
2. require clean Local worktree,
3. live `git fetch --prune origin` + `git pull --ff-only` current Epic,
4. run `RUN_PHASE49_3I14_HOTFIX_GATE.ps1 -LaunchApp`,
5. confirm mature top controls are visible,
6. MakerWorld + `single` + `auto` + the known Product URL → `شروع اسکن` must use mature acquisition,
7. new `دریافت محصول تکی` must use that same mature route and must not force the Rich Direct 403 path,
8. confirm exact-page Preview/Approve remains present.

Do not broaden QA again unless one of these focused contracts fails.

## After Windows PASS
Immediately run exactly one `LOCAL PUBLISH ONLY` + Local Django Store/Admin E2E, verify title/SEO/source/images/pricing/visibility, obtain explicit owner approval, then re-verify Production branch/path/MySQL/backup/rollback and deploy the approved GitHub snapshot.

## Next Product Phase
After Catalog acceptance/deploy, proceed to normal Store ZarinPal checkout request/callback/verify + Sandbox E2E.
