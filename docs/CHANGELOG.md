# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.15 Bulk Exact-Page Images + Add-to-Products

### Owner Business Acceptance Change
Exact MakerWorld Search/Listing discovery is working and returns correct product links, while per-product Direct/Full Fetch repeatedly blocked operations. Owner explicitly requested that exact-page discovery become the business acquisition path: choose up to 100 products, choose up to 20 images/product, stage images, show image count, select wanted rows, Add to Products, Archive unwanted.

### Implemented
- product presets 10/20/30/50/100 with hard max 100,
- image presets 5/10/15/20 with hard max 20,
- reuse verified `discover_preview_candidates` for exact-page links,
- reuse mature Classic browser/image helpers for public image acquisition,
- local staging guard requires at least one successfully downloaded image before readiness/Add-to-Products,
- no Rich Direct `extract_direct_link` dependency in the new bulk flow,
- JSON candidate image manifests under existing persistent Catalog DATA; no candidate DB migration,
- per-row staged image count and live progress,
- `اضافه کردن انتخاب‌شده‌ها به محصولات` materializes staged source identity/title/images into review-state Products without another network Full Fetch,
- Archive/Block, existing-product dedupe, safe Stop and per-candidate error isolation preserved,
- mature 49.3I.14 controls, AI/provider/SEO/pricing/publish/FTP/Bridge/credentials untouched.

### Final GitHub Validation / Merge
PR #61 merged into `epic/phase49-unified-product-slider-sync`.
- final PR head `5f96d890b2e31e1f1d670c8afb716a1da4fc88d3`,
- merge commit `953f975e883e6dfcbf61097ac8d324d68d4ca678`.

Final-head required workflows all SUCCESS:
- Phase49.3I.15 `32641815323`,
- Phase49.3I `32641815273`,
- Phase49.3I.14 `32641815287`,
- Phase49.3H `32641815289`,
- Phase49.3G `32641815380`,
- Full Phase49 + Windows Catalog regressions + Full Django `32641815270`.

Additional review verification:
- repository-root `manage.py` is present and validates the CI working-directory choice,
- staging guard fail-closes candidates when URLs are visible but no local image download succeeds.

Django migration: NONE.  
Catalog candidate schema migration: NONE.  
Production: untouched.  
Next gate: focused Windows 10×10 QA, then exactly one Local Publish E2E.

The older one-thumbnail Preview→approved Full Fetch contract remains historical/compatible but is explicitly superseded for the owner-approved exact-page bulk business path.

## 2026-08-23 — Phase49.3I.14 Restore Mature Scan Controls + Single-Product Route
- restored mature top acquisition controls,
- routed manual Product compatibility action through original mature BaseApp scan path,
- Rich Direct remains optional,
- PR #60 merged; all required CI success; no migration; Production untouched.

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
