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
- **ERR-49-011 — test guessed upsert return contract:** resolve persisted product by real identity.
- **ERR-49-012 — security test coupled to one mask format:** assert secret absence semantically.
- **ERR-49-013 — explicit MakerWorld Search URL ignored:** explicit valid operator URL is authoritative.
- **ERR-49-014 — discovery full-fetched before review:** Preview and acquisition are separate.
- **ERR-49-015 — runtime pricing choices caused phantom migration:** never mutate migration-owned Django field metadata at runtime.
- **ERR-49-016 — PS5.1 runner encoding failure:** Windows runners are ASCII-only and CI-enforced.
- **ERR-49-017 — Products UI patch missed real UX87 boundary:** patch/test final visible composition boundary.
- **ERR-49-018 — AI progress painted after blocking preflight:** first-paint before blocking work.
- **ERR-49-019 — stale Chat-pinned HEAD:** live fetch + clean exact branch + ff-only + Local HEAD == Remote HEAD.
- **ERR-49-020 — product images clipped:** pixel viewport must not use Tk text-unit dimensions.
- **ERR-49-021 — page/group URL misclassified as Product:** source model URL pattern is authoritative.
- **ERR-49-022 — Treeview selection feedback loop:** one-way selection sync + reentrancy guards.
- **ERR-49-023 — secure credentials looked lost:** hydrate real visible controls from secure storage.
- **ERR-49-024 — Preview embedded JS invalid escaping:** embedded browser JavaScript escaping is regression-tested.
- **ERR-49-025 — Provider Hub keys/models missing visually:** hydrate current Provider Hub widgets.
- **ERR-49-026 — visible All-Fields bypassed Task Center:** exact visible action routes to bounded observable AI.
- **ERR-49-027 — AI rerun could not refresh generated fields:** refresh AI-owned values, preserve manual edits, reject generic titles.
- **ERR-49-028 — HTTP success then delayed Tk callback crash:** freeze exception values; bounded trace/watchdog.
- **ERR-49-029 — provider JSON schema mismatch / busy state:** exact schema + one repair + immediate abort release.
- **ERR-49-030 — exact-page discovery worked but UI hid state/results:** final UX87 boundary + live state + contain-fit images.
- **ERR-49-031 — Windows URL paste + batch browser flashing:** explicit paste, headless batch, visible per-candidate error.
- **ERR-49-032 — new UI hid mature scan controls and forced 403-prone route:** restore mature controls; optional paths additive.
- **ERR-49-033 — correct listing links still depended on fragile per-product Full Fetch:** bulk staging/Add-to-Products removes Rich Direct dependency.
- **ERR-49-034 — Locator.evaluate_all SyntaxError aborted discovery:** resilient discovery/image fallback ladder; never one technique as sole gate.
- **ERR-49-035 — Product AI mixed saved identity with provider fallback/model probes:** exactly one saved Provider/Model/key; no hidden model scan or AI-on-open.
- **ERR-49-036 — generic discovery title poisoned Product identity/SEO:** canonical source identity before persistence and before AI.
- **ERR-49-037 — Product AI could wait 210 seconds with weak start diagnostics:** 49.3I.21 bounded provider timeout + request-start/success/error/timeout trace.

### ERR-49-038 — Background AI workers crossed the Tk/Tcl thread boundary and could freeze Product Workspace
**Date:** 2026-08-25  
**Environment:** Windows Catalog Center 8.7.1, feature branch `agent/phase49-3i18-operator-bulk-ai-rebuild`.  
**Owner evidence:** after pressing multiple AI actions the entire Product Workspace title changed to `(Not Responding)` and often required force-close. The behavior remained after the 49.3I.21 HTTP timeout reduction. The right Product rail also clipped lower readiness/AI controls.

**Verified Additional Root Cause:** mature AI workers correctly background network work but several paths then called Tk/Tcl through worker-originated `self.after(...)`; 49.3I.21 also read Tk-backed source state inside its worker. Tk owns one UI thread, so this could block/deadlock Windows UI.

**Correct Solution — Phase49.3I.22:** one final Product Workspace Tk-thread bridge queues worker UI callbacks in Python and drains them on the main thread; Tk-backed source is snapshotted before worker start; right Product rail is a Canvas + vertical Scrollbar.

**Verification status:** implementation/focused tests committed; Windows Local gate required. No migration. Production untouched.

**Prevention:** no worker thread may call Tk/Tcl directly/indirectly; worker completion/error/progress must use the main-thread handoff queue and Tk-backed input must be snapshotted before worker start.

### ERR-49-039 — AvalAI Product request did not match the exact saved-model Chat Completions contract
**Date:** 2026-08-25  
**Owner evidence:** exact MakerWorld product URL works directly in AvalAI, while Catalog Center's link-grounded completion did not reliably produce/apply content; canonical English source identity was correct but old generic Persian identity remained.

**Verified Root Cause:**
- generic `structured_response()` called `choose_model()` and therefore could issue a hidden `/models` request before normal Product generation,
- Responses-style `input_text`/`input_image` wrapper objects were JSON-serialized into one chat user string,
- the prompt demanded a response matching a schema but did not include the actual JSON schema,
- image placeholder objects could consequently be sent as textual wrappers rather than a valid AvalAI multimodal contract,
- this contradicted the existing Product AI rule: exact saved Provider/Model, no hidden model discovery.

**Correct Solution — Phase49.3I.23:**
- add an AvalAI-only Product structured adapter,
- use exact saved model directly,
- send normal `/chat/completions` `model + messages`,
- send only real text/source/operator facts in the user message,
- include the exact output JSON schema in the system instruction,
- do not serialize image placeholder objects,
- preserve bounded timeout/diagnostics/Tk handoff,
- fallback only for unsupported `response_format`, keeping identical exact model/prompt,
- log only sanitized contract metadata.

**Verification status:** code and focused test committed; Windows live AvalAI gate pending. No migration. Production untouched.

**Prevention:** Product-bound provider adapters must have contract tests asserting exact saved model, no hidden discovery, exact request shape, source grounding, output schema visibility and no secret/pseudo-media leakage.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside current release gate. Public SEO sitemap is `/sitemap.xml`; verify internal route/client contract before adding a duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled limit is max 20; current bulk operator exposes 5/10/15/20.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process solution; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
- Social preview enhancement: dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` are not yet emitted; core meta/OG/canonical/schema/sitemap are present.
