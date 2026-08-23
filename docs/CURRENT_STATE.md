# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.16 — Resilient Acquisition Fallback + Cached Candidate Reuse`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Windows QA of 49.3I.15 proved the exact MakerWorld candidate list could remain visible while a new bulk run aborted on `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`. This matched the historical embedded-JavaScript escaping failure class from ERR-49-024. The business requirement is now explicit: a single discovery/acquisition method failure must not destroy a previously working route or abort before alternate methods are tried.

Phase49.3I.16 is merged and adds bounded fallback ladders plus method tracing while preserving the 49.3I.15 bulk workflow:
`Exact Search/Listing URL → product/image limits → resilient discovery → resilient image staging → visible image count → select → Add to Products / Archive → Product Workspace`.

## Phase49.3I.16 Runtime Contract
Discovery order at the final runtime boundary:
1. locator-safe Playwright extraction with no embedded `evaluate_all`,
2. public HTTP/HTML link extraction,
3. attached Chrome 9222 locator-safe discovery when available,
4. reuse previously persisted candidates for the same source/listing URL.

Image acquisition order per candidate:
1. locator-safe fresh browser,
2. public HTTP HTML + existing parser/downloader,
3. mature Classic DOM collector,
4. attached Chrome 9222 locator-safe path when available,
5. listing-card thumbnail fallback.

Rules:
- a failed method records its error and the next method is tried,
- one candidate failure does not abort the remaining candidates,
- at least one image must actually be staged locally before readiness/Add-to-Products,
- candidate manifests record `discovery_trace`, `acquisition_trace`, `discovery_method`, and `acquisition_method`,
- the previously persisted correct candidate list can be reused if all live listing methods fail,
- no Rich Direct `extract_direct_link` dependency is reintroduced,
- 49.3I.15 product max 100 and image max 20 remain unchanged,
- Archive/Block/dedupe, Product Workspace, AI, pricing, publish, FTP/Bridge and credentials remain unchanged.

## GitHub / CI Validation
PR `#62` merged into the Epic branch.
- final PR head: `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`,
- merge commit: `44216546162fead0b752d92cf6cae8d658f034f2`.

Final-head workflows SUCCESS:
- Phase49.3I.16 Resilient Acquisition CI — `32645660164`,
- Phase49.3I Discovery Review Pricing CI — `32645660154`,
- Phase49.3I.15 Bulk Discovery Images CI — `32645660045`,
- Phase49.3I.14 Legacy Scan Restore CI — `32645660071`,
- Phase49.3H SEO Cost Image Limit CI — `32645660135`,
- Phase49.3G Workspace Usability CI — `32645660118`,
- Phase49 Epic Unified CI including Windows Catalog regressions + Full Django suite — `32645660123`.

Review hardening also removed the leak-prone Classic discovery fallback from the final discovery ladder and added cached-candidate reuse after all live methods fail.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE`,
- Catalog candidate schema migration: `NONE`,
- no DB reset/drop/truncate,
- no existing candidate/history/media deletion,
- no credential changes,
- Production untouched.

## Exact Next Task — Windows Focused Acceptance
1. close Catalog Center; Local worktree must be clean,
2. live fetch/prune + ff-only pull current Epic remote HEAD,
3. run `RUN_PHASE49_3I16_FALLBACK_GATE.ps1 -LaunchApp`, which chains all prior 49.3I gates,
4. test `https://makerworld.com/en/search/models?keyword=cake+stand` with `10 products × 10 images`,
5. run `کشف + دریافت تصاویر`; the run must not die on the first method error,
6. previously saved candidates may be reused automatically if live discovery methods fail,
7. verify per-row staged image counts; select 2–3 ready rows and Add to Products without Direct Full Fetch,
8. Archive one unwanted row,
9. open one added Product and verify staged images.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- explicit owner approval,
- read-only Production path/branch/venv/MySQL/backup/rollback verification,
- deploy approved GitHub snapshot only,
- Production HTTP/data/media verification.

## Next Product Phase
After Catalog Production verification: Store ZarinPal request/callback/verify + Sandbox E2E while retaining bank transfer.
