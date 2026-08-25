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
- **ERR-49-014 — discovery full-fetched before review:** Preview and acquisition are separate.
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
- **ERR-49-033 — correct listing links still depended on fragile per-product Full Fetch:** bulk staging/Add-to-Products removes Rich Direct dependency.

### ERR-49-034 — Locator JavaScript failure aborted bulk acquisition
**Root cause:** one browser/parser technique remained a mandatory gate.  
**Solution:** 49.3I.16 discovery/image fallback ladders + cached candidate reuse.  
**Prevention:** a failed equivalent technique must fall through to the next verified method.

### ERR-49-035 — Product AI mixed saved identity with legacy provider fallback / redundant model probes
**Root cause:** legacy provider resolution, model-list probes and hidden AI-on-open could conflict with the explicitly saved Provider/Model.  
**Solution:** 49.3I.17 single active Provider/Model/key, no hidden Product AI, no normal `/models` preflight, stale Tk callback protection.  
**Prevention:** Product AI must use exactly the saved identity and explicit operator execution.

### ERR-49-036 — Generic discovery title poisoned Product identity and downstream AI/SEO
**Owner evidence:** MakerWorld product `2896217-ribbed-cake-stand-cookie-platter` persisted a generic model-number identity and AI generated matching generic Persian content.  
**Root cause:** link-only fallback placeholder crossed the candidate/Product identity boundary.  
**Solution:** 49.3I.19 rejects generic placeholders, prefers exact page title and uses MakerWorld URL slug as deterministic fallback; canonicalization occurs before persistence and before AI.  
**Prevention:** crawler placeholders must never become authoritative Product identity.

### ERR-49-037 — AI actions appeared frozen because generation waited up to 210 seconds without an early request-start boundary
**Date:** 2026-08-25  
**Environment:** Windows Catalog Center 8.7.1 feature QA on `agent/phase49-3i18-operator-bulk-ai-rebuild`.  
**Owner evidence:** `تکمیل هوشمند همه فیلدها با AI`, source-title + full AI rebuild, image SEO and other AI actions could remain at `در حال اتصال به هوش مصنوعی`; the visible Task Center ceiling was 03:30. Source-title reread itself succeeded.

**Verified Root Cause:**
- `catalog_center/app/ai_providers.py` used `timeout=210` for chat generation,
- 210 seconds is exactly 03:30,
- existing 49.3I.18/49.3I.19 generation code already used daemon worker threads, so the Product DB did not need an extra field-write permission to explain the wait,
- diagnostics were strongest after response/error but did not provide one central request-start boundary for every guarded provider call,
- a very long provider/network wait therefore looked like an application hang.

**Correct Solution — Phase49.3I.21:**
- install one global provider guard around AI JSON requests,
- default POST ceiling 75 seconds, environment override `CATALOG_AI_TIMEOUT_SECONDS` constrained to 20..120 seconds,
- write request-start before waiting and finish/error/timeout afterward,
- preserve secret redaction,
- add a visible link-grounded job dialog with elapsed time/stages/cancel/report,
- cancelled late link-refresh response is ignored and busy state is released,
- add one exact-link full-refresh path that fetches/parses the source, canonicalizes identity, sends URL + sanitized facts to AI, previews the result, and applies only after operator confirmation.

**Verification status:** GitHub implementation and regression tests are committed; canonical Windows Local gate is required before acceptance. No migration. Production untouched.

**Prevention:** every external AI request must be bounded, emit a start event before network wait, expose its active Provider/Model/operation, support stale-result rejection, and never use an opaque multi-minute network wait as normal Product Workspace behavior.

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