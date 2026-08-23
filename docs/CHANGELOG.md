# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.14 Restore Mature Scan Controls + Single-Product Route

### Owner Windows Evidence
Real Windows QA after 49.3I.13 found that healthy top acquisition actions had disappeared and a correct MakerWorld Product URL failed through the new manual single-product action with `RuntimeError: HTTP 403`.

### Root Cause — ERR-49-032
- 49.3I.12 explicitly hid mature top controls,
- the Preview layer shadowed `App87.start_scan`, so simply showing the old button would still invoke Preview,
- the new manual single-product action forced Rich Direct Intake / `RichPageExtractor`, while the mature BaseApp `start_scan/_scan_worker` still existed and was the previously working route.

### Fixed
- restored `شروع اسکن`, `توقف محترمانه`, `دریافت هوشمند از لینک`, `کشف جدیدها`,
- rebound visible `شروع اسکن` to original BaseApp mature scan worker,
- manual `دریافت محصول تکی` now validates Product URL then uses the same mature `mode=single` worker,
- Rich Direct intake remains optional,
- Preview/Approve/Archive/Paste/Candidate Error Detail preserved,
- no new crawler/extractor, migration, DB/media rewrite, credential change or Production action.

### Implementation CI Incident
The first targeted 49.3I.14 CI correctly failed because the initial MRO resolver selected an intermediate Preview override. The resolver was changed before a fresh run; the final CI set is green.

### Validation
PR #60 merged.
- final PR head `f12a25e1fe50fb16a03a1324c84912c830a2608e`,
- merge commit `124662cf2436dfcce245282b01b2da694802aa55`,
- Phase49.3I.14 `32636771174` SUCCESS,
- Phase49.3I `32636771071` SUCCESS,
- Phase49.3H `32636771154` SUCCESS,
- Phase49.3G `32636771049` SUCCESS,
- Full Phase49 + Full Django `32636771103` SUCCESS,
- Django migration NONE,
- Catalog schema migration NONE,
- Production untouched.

## 2026-08-23 — Phase49.3I.13 Windows URL Paste + Approved Batch Full-Fetch Recovery
- explicit Ctrl+V / Shift+Insert / right-click Paste / visible Paste action,
- approved batch reuses mature RichPageExtractor in background/headless mode,
- original direct-link headed setting restored after completion/cancel/error,
- selected candidate `last_error` exposed,
- PR #59 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.12 Exact-Page Operator + Single Product + Image Fit
- final UX87 exact-page Preview/live-state operator,
- separate Product URL action,
- candidate Treeview and 228x171 contain-fit image contract,
- PR #58 merged; all required CI success; no migration; Production untouched.

## Earlier Phase49.3I Foundations
Preserved:
- exact Search/Listing authority,
- Preview before Full Fetch,
- image limit default 10 / max 20,
- Product Explorer and Product Workspace routing,
- Fixed / Range / Formula independence,
- AI first-paint / Task Center / schema / trace / watchdog / stale-result safety,
- secure Provider/FTP/Bridge persistence,
- Windows PS5.1 ASCII runner,
- live fetched GitHub snapshot handoff,
- Local/Production publish separation.
