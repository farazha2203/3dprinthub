# ERROR KNOWLEDGE BASE

Search this file before troubleshooting. Never repeat a failed action unchanged. Detailed incident transcripts remain in Git history; this file keeps the current operational root-cause/fix/prevention knowledge.

## RESOLVED / CANONICAL PHASE49 ERRORS

- **ERR-49-001 — Tk pack/grid collision:** one geometry manager per parent; use holder frames.
- **ERR-49-002 — delayed thumbnail callback after widget destruction:** verify widget lifetime before async UI mutation.
- **ERR-49-003 — destroyed ProductWorkspace used as messagebox parent:** async result must verify parent existence.
- **ERR-49-004 — missing optional shell attributes:** guarded access only.
- **ERR-49-005 — image SEO semantic signature false-stale:** normalize structured JSON before hashing.
- **ERR-49-006 — dynamic consultation flag overwritten:** downstream state uses contract-aware merge/OR.
- **ERR-49-007 — PS5.1 NativeCommandError despite exit 0:** native exit code is truth.
- **ERR-49-008 — trace Bearer redaction order leak:** mask Bearer credentials first.
- **ERR-49-009 — later phase installed inside older independent installer:** compose phases at launch/runtime root.
- **ERR-49-010 — Bridge main-image materialization failure:** target Media ownership is a publish prerequisite.
- **ERR-49-011 — test guessed `upsert_product()` return:** resolve persisted product by real identity after upsert.
- **ERR-49-012 — security test coupled to one mask format:** assert secret absence semantically.
- **ERR-49-013 — explicit MakerWorld Search URL ignored:** explicit valid operator URL is authoritative.
- **ERR-49-014 — discovery full-fetched before review:** Preview and acquisition are separate; 49.3I.15 supersedes this for owner-approved bulk path.
- **ERR-49-015 — runtime pricing choices caused phantom migration:** never mutate migration-owned Django field metadata at runtime.
- **ERR-49-016 — PS5.1 runner encoding failure:** Windows runners are ASCII-only and CI-enforced.
- **ERR-49-017 — Products UI patch missed real UX87 boundary:** patch/test final visible composition boundary.
- **ERR-49-018 — AI progress painted after blocking preflight:** first-paint before blocking work.
- **ERR-49-019 — stale Chat-pinned HEAD:** live fetch + clean exact branch + ff-only + Local HEAD == fetched Remote HEAD.
- **ERR-49-020 — product images clipped:** pixel viewport must not use Tk text-unit dimensions.
- **ERR-49-021 — page/group URL misclassified as Product:** source `model_url_pattern` is authoritative.
- **ERR-49-022 — Treeview selection feedback loop:** one-way selection sync + reentrancy guards.
- **ERR-49-023 — secure credentials looked lost:** hydrate real visible controls from secure storage.
- **ERR-49-024 — Preview embedded JS invalid escaping:** embedded browser JavaScript escaping is a regression-tested boundary.
- **ERR-49-025 — Provider Hub keys/models missing visually:** hydrate current Provider Hub widgets.
- **ERR-49-026 — visible All-Fields bypassed Task Center:** exact visible action routes to bounded observable AI.
- **ERR-49-027 — AI rerun could not refresh generated fields:** refresh AI-owned values, preserve manual edits, reject generic titles.
- **ERR-49-028 — HTTP success then delayed Tk exception callback crash:** freeze exception values; bounded trace/watchdog.
- **ERR-49-029 — provider JSON schema mismatch / busy state:** exact schema + one repair + immediate abort release.
- **ERR-49-030 — exact-page discovery worked but UI hid state/results:** final UX87 boundary + live state + contain-fit images.
- **ERR-49-031 — Windows URL paste + batch browser flashing:** explicit paste, headless batch, visible per-candidate error.
- **ERR-49-032 — new UI hid mature scan controls and forced 403-prone single route:** restore mature controls; optional paths are additive.
- **ERR-49-033 — correct listing links still depended on fragile per-product Full Fetch:** 49.3I.15 bulk staging/Add-to-Products removes Rich Direct dependency.

### ERR-49-034 — Bulk exact-page run aborted on `Locator.evaluate_all` SyntaxError instead of trying known alternatives
**Date:** 2026-08-23  
**Environment:** Windows Catalog Center 8.7.1 after merged 49.3I.15.  
**Owner evidence:** the MakerWorld `cake+stand` candidate rows from an earlier successful discovery were still visibly correct, but a new `کشف + دریافت تصاویر` run ended immediately with `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`; counters showed discovery zero / error one.

**Verified Root Cause:**
- the 49.3I.15 bulk worker still called the older `discover_preview_candidates()` as one mandatory discovery boundary,
- that older function contains multiline Python-embedded JavaScript passed to Playwright `evaluate_all`, matching the already known ERR-49-024 escaping failure class,
- failure happened before candidate image staging, so the program did not exploit other available acquisition methods or the already-persisted correct candidate rows,
- a single-method dependency contradicted the owner requirement that a failed route must fall through to other known methods.

**Correct Solution — Phase49.3I.16:**
- final discovery ladder is `locator-safe Playwright → public HTTP/HTML → attached Chrome 9222 → cached candidate DB`,
- new locator-safe discovery contains no embedded `evaluate_all`,
- if every live listing method fails, previously persisted candidates for the same `source_code + discovered_from URL` are reused,
- per-candidate image ladder is `locator-safe fresh → HTTP HTML/parser/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail`,
- each failed method records a trace and the next method is tried,
- image readiness still requires a real local staged file,
- `discovery_trace`, `acquisition_trace`, `discovery_method`, `acquisition_method` are persisted in candidate manifests,
- no Rich Direct Full Fetch dependency is reintroduced.

**Review Hardening:**
- review identified that the initial Classic discovery fallback could leak a browser on errors and that an all-method listing failure could still terminate the run,
- the final runtime discovery layer therefore does not route through that leak-prone Classic discovery fallback,
- attached Chrome + persisted-candidate reuse provide the final recovery boundaries.

**Verification:**
- PR `#62` merged; final head `8f4fbe6d0264f673d0e6564a4ed1e383db023ab6`; merge `44216546162fead0b752d92cf6cae8d658f034f2`,
- 49.3I.16 `32645660164` SUCCESS,
- 49.3I `32645660154` SUCCESS,
- 49.3I.15 `32645660045` SUCCESS,
- 49.3I.14 `32645660071` SUCCESS,
- 49.3H `32645660135` SUCCESS,
- 49.3G `32645660118` SUCCESS,
- Full Phase49 + Windows Catalog regressions + Full Django `32645660123` SUCCESS,
- Django migration NONE; Catalog schema migration NONE; Production untouched.

**Prevention:** never make one browser/parser technique the only gate when equivalent verified methods or persisted results exist. Record the method, fail over explicitly, and preserve previously successful discovery data.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside current release gate. Verify route/client contract before adding a duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled limit is max 20; current bulk operator exposes 5/10/15/20.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process solution; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
