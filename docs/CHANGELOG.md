# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.15 Bulk Exact-Page Images + Add-to-Products

### Owner Business Acceptance Change
Exact MakerWorld Search/Listing discovery is working and returns correct product links, but per-product Direct/Full Fetch remains the operational bottleneck. Owner explicitly requested that exact-page discovery become the acquisition path itself: choose up to 100 products, choose up to 20 images/product, stage images, show image count, select wanted rows, Add to Products, Archive unwanted.

### Implemented
- product presets 10/20/30/50/100 with hard max 100,
- image presets 5/10/15/20 with hard max 20,
- reuse verified `discover_preview_candidates` for exact-page links,
- reuse mature Classic browser/image helpers for staged public images,
- no Rich Direct `extract_direct_link` dependency in the new bulk flow,
- JSON candidate image manifests under existing persistent Catalog DATA; no candidate DB migration,
- per-row image-count column and live progress,
- `اضافه کردن انتخاب‌شده‌ها به محصولات` materializes staged source identity/title/images into review-state Products without another network Full Fetch,
- Archive/Block, existing-product dedupe, safe Stop and per-candidate error isolation preserved,
- mature 49.3I.14 controls, AI/provider/SEO/pricing/publish/FTP/Bridge/credentials untouched.

### Validation
Runtime feature head before documentation-only commits: `a7cb319c2723ae2f9cfe87a1a00c8b33e7fcf619`.
PR #61.
- Phase49.3I.15 `32641268643` SUCCESS,
- Phase49.3I `32641268627` SUCCESS,
- Phase49.3I.14 `32641268644` SUCCESS,
- Phase49.3H `32641268659` SUCCESS,
- Phase49.3G `32641268651` SUCCESS,
- Full Phase49 + Full Django `32641268645` SUCCESS,
- Django migration NONE,
- Catalog candidate schema migration NONE,
- Production untouched.

The older one-thumbnail Preview→approved Full Fetch contract remains historical/compatible but is explicitly superseded for the owner-approved exact-page bulk business path.

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
- manual `دریافت محصول تکی` validates Product URL then uses the same mature `mode=single` worker,
- Rich Direct intake remains optional,
- Preview/Approve/Archive/Paste/Candidate Error Detail preserved,
- no new crawler/extractor, migration, DB/media rewrite, credential change or Production action.

### Validation
PR #60 merged; all required CI success; Django/Catalog migration NONE; Production untouched.

## 2026-08-23 — Phase49.3I.13 Windows URL Paste + Approved Batch Full-Fetch Recovery
- explicit Ctrl+V / Shift+Insert / right-click Paste / visible Paste action,
- approved batch background/headless recovery,
- selected candidate `last_error` exposed,
- PR #59 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.12 Exact-Page Operator + Single Product + Image Fit
- final UX87 exact-page operator/live state,
- separate Product URL action,
- candidate Treeview and 228x171 contain-fit image contract,
- PR #58 merged; all required CI success; no migration; Production untouched.

## Earlier Phase49.3I Foundations
Preserved:
- exact Search/Listing authority,
- image hard max 20,
- Product Explorer and Product Workspace routing,
- Fixed / Range / Formula independence,
- AI first-paint / Task Center / schema / trace / watchdog / stale-result safety,
- secure Provider/FTP/Bridge persistence,
- Windows PS5.1 ASCII runner,
- live fetched GitHub snapshot handoff,
- Local/Production publish separation.
