# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.16 Resilient Acquisition Fallback + Cached Candidate Reuse

### Windows Evidence
A merged 49.3I.15 build still showed previously correct MakerWorld candidates, but a new exact-page run aborted on `Locator.evaluate_all: SyntaxError: Invalid or unexpected token` before image staging.

### Implemented
- replaced the single mandatory live discovery boundary at final runtime with an ordered ladder: locator-safe Playwright → public HTTP/HTML → attached Chrome 9222 → cached candidate DB,
- locator-safe discovery avoids embedded `evaluate_all`,
- reuses previously persisted candidates for the same source/listing URL when live discovery cannot re-read the page,
- image acquisition now falls through: locator-safe fresh → HTTP parse/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail,
- each failed/successful method is traced in candidate manifests,
- local staged image remains mandatory before readiness/Add-to-Products,
- one candidate failure remains isolated,
- no Rich Direct Full Fetch dependency was reintroduced,
- 49.3I.15 limits/Add-to-Products/Archive/Block and all AI/pricing/publish contracts remain unchanged.

### Review Hardening
Code review identified two risks in the first fallback design: the mature Classic discovery helper could leak a browser on its own exception path, and an all-live-method discovery failure could still terminate the listing. The final runtime discovery layer therefore skips that leak-prone discovery fallback and uses attached Chrome plus persisted-candidate reuse as the later boundaries.

### Validation / Merge
PR #62 merged into `epic/phase49-unified-product-slider-sync`.
- final PR head `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`,
- merge commit `44216546162fead0b752d92cf6cae8d658f034f2`.

Final-head SUCCESS:
- 49.3I.16 `32645660164`,
- 49.3I `32645660154`,
- 49.3I.15 `32645660045`,
- 49.3I.14 `32645660071`,
- 49.3H `32645660135`,
- 49.3G `32645660118`,
- Full Phase49 + Windows Catalog regressions + Full Django `32645660123`.

Django migration: NONE. Catalog schema migration: NONE. Production untouched.

## 2026-08-23 — Phase49.3I.15 Bulk Exact-Page Images + Add-to-Products
- product max 100 / image max 20,
- exact-page discovery + local image staging,
- no Rich Direct dependency in bulk flow,
- per-row staged image count,
- selected rows Add to Products without another network Full Fetch,
- local staging guard requires a real downloaded image,
- Archive/Block/dedupe and mature controls preserved,
- PR #61 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.14 Restore Mature Scan Controls + Single-Product Route
- restored mature top acquisition controls,
- compatibility single Product uses mature BaseApp scan path,
- Rich Direct remains optional,
- PR #60 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.13 Windows URL Paste + Batch Recovery
- explicit Windows paste actions,
- background batch behavior,
- selected candidate technical error exposed,
- PR #59 merged; all required CI success.

## Earlier Phase49.3I Foundations
Preserved: Product Workspace routing, contain-fit gallery, Fixed/Range/Formula independence, observable bounded AI, provider schema/trace, secure credentials, PS5.1 runner guard, live Git snapshot handoff, and Local/Production publish separation.
