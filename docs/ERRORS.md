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
- that older function contains multiline Python-embedded JavaScript passed to Playwright `evaluate_all`, matching ERR-49-024,
- failure happened before candidate image staging,
- a single-method dependency contradicted the owner requirement that a failed route fall through to known alternatives.

**Correct Solution — Phase49.3I.16:**
- discovery ladder `locator-safe Playwright → public HTTP/HTML → attached Chrome 9222 → cached candidate DB`,
- per-candidate image ladder `locator-safe fresh → HTTP parser/downloader → mature Classic DOM → attached Chrome 9222 → listing thumbnail`,
- each failed method is traced and the next one is tried,
- cached correct candidates for the same listing may be reused,
- real local image staging remains required,
- no Rich Direct dependency returns.

**Verification:** PR `#62` merged; all 49.3I.16/49.3I/49.3I.15/49.3I.14/49.3H/49.3G/Full Phase49 + Full Django workflows passed. No migration. Production untouched.

**Prevention:** never make one browser/parser technique the only gate when equivalent verified methods or persisted results exist.

### ERR-49-035 — Product AI mixed saved identity with legacy provider fallback and redundant model-catalog probes
**Date:** 2026-08-23  
**Environment:** Windows Catalog Center 8.7.1 after 49.3I.16.  
**Owner evidence:** operator selected and saved one Provider/Model in AI Center, but Product AI often stayed at `در حال اتصال به هوش مصنوعی`, appeared to enumerate many models/providers, sometimes required Task Manager termination, and one async callback raised `TclError: invalid command name ...listbox`.

**Verified Root Cause:**
- legacy `App._selected_ai_provider()` only treated AvalAI/OpenAI as explicit and otherwise scanned configured keys, so saved OpenRouter/Google could drift to a different provider,
- Product Task Center and title paths still consumed that legacy resolver,
- every Product AI run called `probe_connection()` before useful work; the 49.3I.11 probe downloaded the provider model catalog,
- Google Product AI could list models again before the content request,
- `ai_auto_prepare_on_open` defaulted to enabled and could start a hidden request about 900 ms after opening an incomplete product while the operator also started a manual request,
- a delayed Tk callback could touch a destroyed Listbox and promote a stale UI callback into a fatal dialog.

**Correct Solution — Phase49.3I.17:**
- Product AI identity comes only from saved `ai_provider` + that provider's saved model,
- secure key is read only for that exact provider and a cross-provider request is rejected,
- `auto`/unsaved provider fails closed instead of selecting whichever key happens to exist,
- hidden AI-on-open is disabled; Product AI runs only after explicit operator action,
- Product-bound `probe_connection` is a local exact-model preflight and does not request `/models`; actual content generation is the network test,
- Google Product-bound exact model bypasses `_google_model_info` before generation,
- Settings Model Search / explicit connection test remain live,
- stale `invalid command name` Tk callbacks are logged/suppressed and busy flags are released,
- existing observable request/response/error trace, schema repair, watchdog/Stop Waiting and stale-result guards are preserved.

**Verification:**
- PR `#63` merged; final runtime head `2917a3db5225abac71fc3e80b64ad439acd7a4d0`; merge `7f835f573b92e3aded6275c9421770c0c47d947a`,
- Phase49.3I.17 `32649623837` SUCCESS,
- Phase49.3I `32649623808` SUCCESS,
- Phase49.3I.16 `32649623695` SUCCESS,
- Phase49.3I.15 `32649623705` SUCCESS,
- Phase49.3I.14 `32649623679` SUCCESS,
- Phase49.3H `32649623825` SUCCESS,
- Phase49.3G `32649623755` SUCCESS,
- Full Phase49 + Windows Catalog regressions + Full Django `32649623804` SUCCESS,
- Django migration NONE; Catalog schema migration NONE; Production untouched.

**Prevention:** Product AI must never infer provider from available secrets or enumerate model catalogs during normal generation. Persist one active identity, use it exactly, keep discovery/test network calls explicit, and never start hidden AI work on Product open.

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
