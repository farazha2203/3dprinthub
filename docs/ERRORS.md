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

**Verified Additional Root Cause:**
- mature Task Center and Product AI code correctly runs network work in background Python threads,
- several worker paths then call `self.after(0, ...)` from those worker threads,
- progress helpers also eventually reach Tk through that worker-originated `after`,
- 49.3I.18/19 rebuild workers use the same callback pattern,
- 49.3I.21 additionally called `_source_for_ai()` from its worker although source building can read Tk-backed variables,
- Tk/Tcl has one owning UI thread; cross-thread Tcl marshalling can block/deadlock Windows UI even when the HTTP request itself is on a worker.

**Correct Solution — Phase49.3I.22:**
- install one final Product Workspace Tk-thread bridge after all existing AI layers,
- record the owning Tk thread,
- off-main `workspace.after(...)` must never invoke Tcl; enqueue a plain Python callback instead,
- a pump scheduled by the Tk main thread drains the queue every 25 ms and executes callbacks on that thread,
- support cancellation tokens for deferred callbacks,
- snapshot `_source_for_ai()` on the main thread and return deep-copied plain data to workers,
- pre-snapshot 49.3I.21 link refresh before worker start,
- keep network/AI work backgrounded and preserve existing Provider/model/business logic,
- rebuild Product right rail as Canvas + vertical Scrollbar so appended AI/readiness panels remain reachable.

**Verification status:** implementation and focused test code are committed on the feature branch. Canonical Windows Local gate is still required. No migration. Production untouched.

**Prevention:** no Python worker thread may call any Tk/Tcl API directly or indirectly. Worker completion/error/progress must use a Python-only handoff queue drained by the main UI thread. Any Tk-backed input required by a worker must be snapshotted before the worker starts.

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
