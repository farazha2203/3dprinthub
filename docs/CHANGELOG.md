# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.13 Windows URL Paste + Approved Batch Full-Fetch Recovery

### Owner Windows Evidence
49.3I.12 correctly displayed MakerWorld candidate images/titles/IDs/URLs, but real Windows QA found:
- exact URL field could not be pasted into reliably and required typing,
- selecting multiple candidates then `دریافت کامل انتخاب‌شده‌ها` opened/closed approximately one visible browser per selected candidate,
- some selected candidates ended in `خطا`, while their displayed source URLs were correct,
- persisted technical candidate errors were not directly visible in the operator surface.

### Root Cause — ERR-49-031
- final 49.3I.12 URL field was a plain `ttk.Entry` without explicit Windows paste bindings/context menu,
- approved batch reused the mature RichPageExtractor but inherited `direct_link.headed=true`; because Full Fetch invokes the extractor once per selected candidate, each row produced a visible persistent browser context,
- `last_error` already existed in candidate storage but had no direct operator viewer.

### Fixed
- Ctrl+V / Ctrl+V uppercase / Shift+Insert / right-click Paste,
- visible `چسباندن لینک` action,
- approved batch only: temporarily force existing RichPageExtractor to background/headless mode,
- restore original direct-link headed setting after batch completion/cancel/error,
- direct single-product intake remains unchanged for login/CAPTCHA recovery,
- visible `جزئیات خطای انتخابی` backed by persisted `last_error`,
- runner upgraded to `49.3I.13`,
- dedicated regression tests and CI contracts added,
- no new crawler/extractor, migration, DB reset, media rewrite or Production change.

### Validation
PR #59 merged.
- feature head `b47793c42d807285efbd8d3e005f9979856c4878`,
- merge commit `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`,
- Phase49.3I Run `32633932308` SUCCESS,
- Phase49.3H Run `32633932302` SUCCESS,
- Phase49.3G Run `32633932340` SUCCESS,
- Full Phase49 + Full Django Run `32633932224` SUCCESS,
- Django migration NONE,
- Catalog schema migration NONE,
- Production untouched.

## 2026-08-23 — Phase49.3I.12 Observable Exact-Page Discovery + Single-Product Intake + Workspace Image Fit

### Owner Windows Evidence
The owner-provided Catalog screenshot showed the exact MakerWorld Search URL was already used as `PREVIEW_TARGET` and the run completed with `candidates=20`, `failed=0`, `full_fetch=0`. Therefore the crawler/search backend was not the primary failure. The operator-facing UX still did not clearly expose candidate results, live running state, stop state, elapsed time or the current URL, and direct Product URL intake was not separated from Search/Listing discovery. Product Workspace image fitting was also visually unstable.

### Root Cause — ERR-49-030
- UX87 builds Discovery inside final `_ui()` using `super()._scan_ui()`, so the later Phase49.3I `_scan_ui` patch could be bypassed at the visible shell boundary even while backend discovery methods were active.
- the visible candidate Treeview needed to reuse the mature thumbnail/status/title/source/external/url contract.
- image cards needed ERR-49-020's fixed-pixel viewport rule applied at the final Product Workspace thumbnail boundary.

### Fixed
- new Phase49.3I.12 operator UI mounted at final UX87 `_ui` boundary,
- exact Search/Listing/Category page discovery action,
- separate manual direct Product URL intake validated by source `model_url_pattern`,
- visible running/stopping/done badge, progress, elapsed time, active URL/detail and Stop feedback,
- candidate Treeview runtime bridge preserving mature thumbnail + identity renderer,
- Preview remains one thumbnail/basic identity and `full_fetch=0` until approval,
- approved Full Fetch still uses mature extractor path,
- Product Workspace thumbnails now render in fixed `228x171` pixel `ImageOps.contain` letterboxed viewports without crop/stretch,
- no parallel crawler/extractor or credential/publish rewrite introduced.

### Validation
PR #58 merged.
- feature head `2a9442055d33777f675ccd3ebe11de8419bfb2b3`,
- merge commit `24d5b8fdddb97fbcc4c07efa7d6f1d78a0ffb225`,
- Phase49.3I Run `32631604990` SUCCESS,
- Phase49.3H Run `32631604930` SUCCESS,
- Phase49.3G Run `32631604945` SUCCESS,
- Full Phase49 + Full Django Run `32631604928` SUCCESS,
- Django migration NONE,
- Catalog schema migration NONE,
- Production untouched.

## 2026-08-23 — Phase49.3I.11 Provider Schema + Trace/Busy Runtime Recovery
- real JSON Schema delivery to AvalAI/OpenRouter,
- exact provider schema validation before persistence,
- one bounded repair request,
- compact model catalog trace,
- immediate busy-state release on Stop Waiting/watchdog,
- stale late-result protection,
- PR #57 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.10 AI Trace + Safe Title Retry Recovery
- added scrollable sanitized outgoing/incoming/error tabs,
- fixed delayed Tk exception callback closure bug,
- title retry always uses current Provider/Model,
- title-only 90-second watchdog + stale-result protection,
- generic/non-Persian/too-short title validation,
- PR #56 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Earlier Phase49.3I Foundations
Preserved:
- exact Search/Listing authority,
- Preview before Full Fetch,
- image limit default 10 / max 20,
- visual Product Explorer,
- selection-loop guard,
- Fixed / Range / Formula independence,
- AI first-paint,
- Windows PS5.1 ASCII runner,
- live fetched GitHub snapshot handoff,
- Local/Production publish separation.
