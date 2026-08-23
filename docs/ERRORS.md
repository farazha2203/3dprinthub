# ERROR KNOWLEDGE BASE

Search this file before troubleshooting. Do not repeat a failed action unless its underlying condition changed. Detailed historical incident text remains in Git history; this file keeps the operational symptom/root-cause/fix/prevention knowledge needed for current development.

## RESOLVED ERRORS

### ERR-49-001 — Tkinter pack/grid collision in Product Workspace
Root Cause: sibling widgets mixed `pack()` and `grid()` under the same Tk parent.
Correct Solution: one geometry manager per parent; introduce a holder when needed.
Prevention: never mix pack/grid for siblings.

### ERR-49-002 — Thumbnail callback after widget destruction
Root Cause: delayed image callback targeted a destroyed/rebuilt widget.
Correct Solution: lifecycle-safe callbacks verify the live target before UI mutation.
Prevention: every delayed/thread→Tk callback validates widget lifetime.

### ERR-49-003 — Destroyed ProductWorkspace used as messagebox parent
Root Cause: async completion ran after Workspace close.
Correct Solution: verify parent existence before dialog/UI update.
Prevention: background results never assume originating window still exists.

### ERR-49-004 — Missing `header_badge`
Root Cause: callback assumed an optional shell attribute existed.
Correct Solution: guarded shell-state access.
Prevention: patches must not depend on optional attributes without guards.

### ERR-49-005 — Image SEO semantic signature false-stale
Root Cause: raw JSON representation was hashed instead of normalized semantics.
Correct Solution: normalize structured JSON before hashing.
Prevention: structured signatures hash semantics, not formatting.

### ERR-49-006 — Dynamic price consultation flag overwritten
Root Cause: later sync blindly overwrote an earlier pricing decision.
Correct Solution: contract-aware OR/merge semantics.
Prevention: downstream layers must not erase earlier validated state.

### ERR-49-007 — Windows NativeCommandError after successful migrations
Root Cause: PowerShell 5.1 treated harmless native stderr as terminating while exit code was zero.
Correct Solution: capture native output under Continue and use exit code as truth.
Prevention: do not infer native failure from stderr alone.

### ERR-49-008 — Runtime Trace inline Bearer token redaction leak
Root Cause: generic Authorization redaction ran before Bearer masking.
Correct Solution: mask Bearer credentials first.
Prevention: redaction order is a tested security contract.

### ERR-49-009 — Phase49.3G installed inside independent 49.3F installer
Root Cause: cross-phase composition leaked into an older independently tested installer.
Correct Solution: compose phases at launch/composition root.
Prevention: prior-phase installers remain independently valid.

### ERR-49-010 — Historical Bridge import main-image failure
Symptom: primary image was not materialized in target Media before conversion.
Correct Solution: publish preflight materializes selected/primary image first.
Prevention: target Media ownership is a publish prerequisite.

### ERR-49-011 — CI fixture assumed `upsert_product()` returns product ID
Root Cause: test guessed a DB API return contract.
Correct Solution: upsert then resolve persisted row by verified identity.
Prevention: tests use real repository contracts.

### ERR-49-012 — Redaction assertion coupled to display formatting
Root Cause: test expected one cosmetic mask format.
Correct Solution: assert secret absence and masked Authorization semantically.
Prevention: security tests validate no-leak invariants.

### ERR-49-013 — Explicit MakerWorld search URL ignored
Root Cause: search mode chose configured listing instead of explicit seed.
Correct Solution: valid explicit HTTP(S) operator URL is authoritative.
Prevention: never silently substitute a default discovery URL.

### ERR-49-014 — Discovery full-fetched before human review
Root Cause: URL discovery immediately entered full extraction.
Correct Solution: `Preview Candidate → Approve/Archive → Approved Full Fetch`.
Prevention: preview and acquisition are separate state transitions.

### ERR-49-015 — Runtime pricing choices created phantom Django migration
Root Cause: runtime code mutated migration-owned Django field `choices`.
Correct Solution: preserve field metadata; persist semantic value in existing field.
Prevention: model metadata changes are migration changes.

### ERR-49-016 — Phase49.3I runner parse failure on Windows PowerShell 5.1
Root Cause: BOM-less UTF-8 runner contained Persian/em-dash bytes decoded under legacy ANSI rules.
Correct Solution: canonical runner ASCII-only; CI enforces it.
Prevention: Windows PS5.1 runners keep explicit tested encoding contract.

### ERR-49-017 — Products UI patch missed real UX87 composition boundary
Root Cause: UX87 called `super()._products_ui()` then `_modernize_products_page()`, bypassing the initial patch target.
Correct Solution: patch the final visible shell boundary.
Prevention: UI tests exercise the actual visible composition path.

### ERR-49-018 — AI progress created after synchronous preflight
Root Cause: save/preflight/source work ran before progress first-paint.
Correct Solution: immediate first-paint then Tk `after()` handoff.
Prevention: blocking preflight starts only after visible feedback paints.

### ERR-49-019 — Windows handoff used stale Chat-pinned HEAD
Root Cause: mutable Epic advanced after a fixed SHA was copied into Chat.
Correct Solution: live fetch, exact branch, clean worktree, Local HEAD == fetched Remote HEAD, ff-only pull.
Prevention: Chat SHA is audit information, never mutable-branch source of truth.

### ERR-49-020 — Product images clipped into thin strips
Root Cause: pixel PhotoImage assigned to a Label sized in Tk text units.
Correct Solution: pixel viewport with unconstrained image Label.
Prevention: do not size pixel images through Tk text-unit width/height.

### ERR-49-021 — Group/category URL misclassified as direct product URL
Root Cause: guessed URL-shape heuristics replaced configured source regex.
Correct Solution: source `model_url_pattern` is authoritative Product-vs-Page boundary.
Prevention: classify product identity from verified source configuration.

### ERR-49-022 — Hidden Treeview selection feedback loop froze Product open
Root Cause: selection callback rewrote the same selection recursively.
Correct Solution: one-way event-producing sync plus re-entrancy/repeat-open guards.
Prevention: never mutate the same Tk selection from its own selection callback.

### ERR-49-023 — Secure credentials appeared lost because visible fields were not hydrated
Root Cause: secure backend persisted credentials but operator widgets were cleared/not rehydrated.
Correct Solution: hydrate Windows Credential Store/environment after startup/save.
Prevention: persistence tests target visible operator controls as well as storage.

### ERR-49-024 — Preview `evaluate_all` JavaScript syntactically invalid
Root Cause: Python escaping turned intended JS `\n` into a literal newline in a JS single-quoted string.
Correct Solution: preserve browser-side escape bytes.
Prevention: Python-embedded JS requires explicit escaping regression tests.

### ERR-49-025 — Real Provider Hub keys/model lists disappeared visually
Root Cause: legacy `ai_key` was hydrated while modern Provider cards use `_ai_hub_key_vars`.
Correct Solution: hydrate real provider-card variables and load model catalogs through mature client.
Prevention: readiness tests target current Provider Hub controls.

### ERR-49-026 — Bottom All-Fields AI bypassed mature Task Center
Root Cause: visible button still called legacy `generate_ai("commerce")`.
Correct Solution: route real All-Fields to mature Task Center with elapsed/Stop/210s watchdog/stale discard.
Prevention: tests exercise exact visible button after all composition layers.

### ERR-49-027 — All-Fields rerun could not refresh AI output and generic titles persisted
Root Cause: Task Center filled blanks only and did not distinguish manual vs AI-owned values.
Correct Solution: refresh AI-owned fields, protect proven manual edits, reject generic titles, preserve source/SEO grounding.
Prevention: explicit AI refresh tracks generated ownership and validates product identity.

### ERR-49-028 — AI HTTP succeeded but delayed Tk callback crashed; title retry lacked full trace
Root Cause: delayed callback captured an exception target Python later clears; title-only action lacked bounded observable execution.
Correct Solution: freeze exception values, scrollable sanitized trace, current Provider/Model retry, 90s title watchdog, stale discard.
Prevention: HTTP success is not UI acceptance; delayed callbacks freeze values.

### ERR-49-029 — Provider useful JSON had wrong schema; model trace/busy state looked hung
Root Cause: compatible gateways received generic `json_object` rather than exact Catalog schema; huge model catalog was rendered; abort did not release all busy flags.
Correct Solution: exact JSON Schema + one repair, compact model trace, immediate busy release, stale-result protection.
Prevention: HTTP 200 + valid JSON is insufficient without exact application schema.

### ERR-49-030 — Exact-page discovery succeeded but UX87 did not expose review/live state
Root Cause: patch targeted a method bypassed by final UX87 `_ui`; candidate renderer/image viewport contracts also needed final-boundary composition.
Correct Solution: mount operator at final UX87 `_ui`, reuse mature candidate Treeview, show live state, separate direct product action, 228x171 contain-fit images.
Prevention: patch final visible composition boundary and reuse mature contracts.

### ERR-49-031 — Windows URL paste failed and approved batch flashed one browser per candidate
Date: 2026-08-23
Environment: Windows Catalog Center 8.7.1 / Phase49.3I.12
Symptoms:
- exact URL field did not reliably accept Paste, forcing manual typing,
- MakerWorld Preview rows and product URLs were correct,
- selecting multiple candidates and running approved Full Fetch opened/closed roughly one visible browser window per selected row,
- some rows ended as `failed`, but the operator could not directly see the persisted technical reason.
Verified Root Cause:
- the 49.3I.12 exact URL control was a plain `ttk.Entry` with no explicit Ctrl+V/Shift+Insert/right-click paste contract, while other operator fields already had explicit paste handlers,
- mature approved Full Fetch invokes RichPageExtractor once per selected candidate and inherited `direct_link.headed=true`, therefore each selected row legitimately created a visible persistent browser context,
- candidate `last_error` was already stored but not surfaced in the final operator panel.
Correct Solution — Phase49.3I.13:
- explicit Ctrl+V / Ctrl+V uppercase / Shift+Insert bindings,
- right-click Paste menu and visible `چسباندن لینک` button,
- approved batch only temporarily forces the existing RichPageExtractor to background/headless mode,
- original direct-link headed setting is restored after batch completion/cancel/error,
- separate single-product intake keeps its configured headed behavior,
- `جزئیات خطای انتخابی` shows persisted `last_error`,
- no second crawler/extractor and no Preview/Approve semantic change.
Verification:
- PR #59 merged,
- feature head `b47793c42d807285efbd8d3e005f9979856c4878`,
- merge commit `3ad097fb3c5ccd2aed82b2dab38f3c8951e00e51`,
- Phase49.3I Run `32633932308` SUCCESS,
- Phase49.3H Run `32633932302` SUCCESS,
- Phase49.3G Run `32633932340` SUCCESS,
- Full Phase49 + Full Django Run `32633932224` SUCCESS,
- Django migration NONE; Catalog schema migration NONE; Production untouched.
Prevention:
- Windows operator text fields that are business-critical must have explicit tested paste UX,
- batch acquisition must not inherit an interactive headed-browser default intended for manual single-item/login recovery,
- persisted per-item failure reason must be reachable from the operator surface.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Status: OPEN / outside current 49.3I release gate.
Rule: verify route/client contract before adding duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Status: mitigated by Phase49.3H.
Rule: never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image acquisition limit inconsistency
Status: runtime contract addressed; Windows QA remains.
Rule: default 10 / hard max 20 through canonical normalizer.

## Warning Debt
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process architecture; Redis/polling remains separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
