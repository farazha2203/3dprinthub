# ERROR KNOWLEDGE BASE

Search this file before troubleshooting. Do not repeat a failed action unless its underlying condition changed. Older verbose incident reports remain in Git history; this file keeps the operational root cause, correct solution and prevention rule for each current Phase49 incident.

## RESOLVED ERRORS

### ERR-49-001 — Tkinter pack/grid collision in Product Workspace
Root Cause: sibling widgets mixed `pack()` and `grid()` under the same Tk parent.
Correct Solution: use one manager per parent; introduce a holder before switching manager inside children.
Prevention Rule: never mix pack/grid for siblings.

### ERR-49-002 — Thumbnail callback after widget destruction
Root Cause: delayed image callback targeted a destroyed/rebuilt widget.
Correct Solution: lifecycle-safe callbacks that verify the live target before UI mutation.
Prevention Rule: every delayed/thread→Tk callback must validate widget lifetime.

### ERR-49-003 — Destroyed ProductWorkspace used as messagebox parent
Root Cause: async completion ran after Workspace close.
Correct Solution: verify parent existence before dialog/UI update.
Prevention Rule: background results never assume the originating window still exists.

### ERR-49-004 — Missing `header_badge`
Root Cause: callback assumed a shell attribute existed in every runtime composition.
Correct Solution: use verified/guarded shell state.
Prevention Rule: UI patches must not depend on optional attributes without a guard.

### ERR-49-005 — Image SEO semantic signature false-stale
Root Cause: raw JSON representation was hashed rather than semantic normalized content.
Correct Solution: normalize structured JSON before hashing.
Prevention Rule: structured signatures hash semantics, not byte formatting.

### ERR-49-006 — Dynamic price consultation flag overwritten
Root Cause: later sync blindly overwrote an earlier pricing decision.
Correct Solution: preserve truth with contract-aware OR/merge semantics.
Prevention Rule: downstream layers must not erase earlier validated state.

### ERR-49-007 — Windows NativeCommandError after successful migrations
Root Cause: PowerShell 5.1 `$ErrorActionPreference='Stop'` treated harmless native stderr as terminating while exit code was 0.
Correct Solution: capture native output under Continue and use process exit code as truth.
Prevention Rule: do not infer native command failure from redirected stderr alone.

### ERR-49-008 — Runtime Trace inline Bearer token redaction leak
Root Cause: generic Authorization redaction ran before Bearer credential masking.
Correct Solution: mask Bearer credentials first, then generic secret patterns.
Prevention Rule: redaction order is a tested security contract.

### ERR-49-009 — Phase49.3G installed inside independent 49.3F installer
Root Cause: cross-phase composition leaked into an older independently tested installer.
Correct Solution: compose phases at the launch/composition root.
Prevention Rule: prior-phase installers remain independently valid.

### ERR-49-010 — Historical Bridge import main-image failure
Symptoms: `قبل از تبدیل، تصویر اصلی باید در Media ذخیره یا بارگذاری شود.`
Root Cause: primary image was not materialized into target Media before conversion.
Correct Solution: publish preflight must materialize the selected/primary image before import.
Prevention Rule: target Media ownership is a publish prerequisite.

### ERR-49-011 — CI fixture assumed `upsert_product()` returns product ID
Root Cause: test guessed a Database API return contract.
Correct Solution: upsert then resolve the persisted row by verified identity.
Prevention Rule: tests use real repository contracts, never inferred return values.

### ERR-49-012 — Redaction assertion coupled to display formatting
Root Cause: test expected one literal mask format rather than the security invariant.
Correct Solution: assert secret absence and masked Authorization semantically.
Prevention Rule: security tests validate no-leak invariants, not cosmetic mask text.

### ERR-49-013 — Explicit MakerWorld search URL ignored
Symptoms: operator supplied exact search URL but unrelated default listing was scanned.
Root Cause: search mode chose configured listing instead of explicit seed.
Correct Solution: a valid explicit HTTP(S) operator URL is authoritative.
Prevention Rule: never silently substitute a default discovery URL.

### ERR-49-014 — Discovery full-fetched before human review
Root Cause: URL discovery immediately entered full product extraction.
Correct Solution: `Preview Candidate → Approve/Archive → Approved Full Fetch`.
Prevention Rule: preview and acquisition are separate state transitions.

### ERR-49-015 — Runtime pricing choices created phantom Django migration
Root Cause: runtime code mutated Django field `choices`, which is migration state metadata.
Correct Solution: preserve migration-owned field metadata and persist the semantic raw value in the existing CharField.
Prevention Rule: model metadata changes are migration changes even without SQL type changes.

### ERR-49-016 — Phase49.3I runner parse failure on Windows PowerShell 5.1
Root Cause: BOM-less UTF-8 runner contained Persian/em-dash bytes and PS5.1 decoded them with legacy ANSI rules.
Correct Solution: canonical runner is ASCII-only and CI enforces it.
Prevention Rule: Windows PS5.1 runners keep an explicit tested encoding contract.

### ERR-49-017 — Products UI patch missed real UX87 composition boundary
Root Cause: UX87 called `super()._products_ui()` then `_modernize_products_page()`, bypassing the initial patch target.
Correct Solution: patch the real final shell composition boundary.
Prevention Rule: UI regression tests exercise the actual visible composition path.

### ERR-49-018 — AI progress created after synchronous preflight
Root Cause: save/preflight/source work ran before any visible progress paint.
Correct Solution: immediate first-paint then Tk `after()` handoff to the mature Task Center.
Prevention Rule: potentially blocking UI preflight starts only after feedback is painted.

### ERR-49-019 — Windows handoff used stale Chat-pinned HEAD
Root Cause: mutable Epic advanced after a fixed SHA was copied into Chat.
Correct Solution: live `git fetch --prune origin`, exact branch, clean worktree, Local HEAD equals fetched Remote HEAD; ff-only pull when behind.
Prevention Rule: fixed Chat SHA is audit information, never the mutable branch source of truth.

### ERR-49-020 — Product images clipped into thin strips
Root Cause: pixel PhotoImage assigned to a Label sized in text units.
Correct Solution: pixel-sized holder with unconstrained image Label.
Prevention Rule: do not size pixel image contracts through Tk text-unit width/height.

### ERR-49-021 — Group/category URL misclassified as direct product URL
Root Cause: guessed URL-shape heuristics replaced configured source regex.
Correct Solution: source `model_url_pattern` is authoritative Product-vs-Group boundary.
Prevention Rule: classify product identity from verified source configuration.

### ERR-49-022 — Hidden Treeview selection feedback loop froze Product open
Root Cause: selection callback wrote the same selection and recursively triggered itself.
Correct Solution: one-way event-producing sync + re-entrancy/repeat-open guards.
Prevention Rule: never mutate the same Tk selection from its own selection callback.

### ERR-49-023 — Secure credentials appeared lost because masked fields were not hydrated
Root Cause: secure backend persisted credentials but visible legacy fields were cleared/not rehydrated.
Correct Solution: hydrate from Windows Credential Store/environment after startup/save.
Prevention Rule: persistence tests target visible operator widgets as well as storage.

### ERR-49-024 — Preview `evaluate_all` JavaScript syntactically invalid
Symptoms: `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`.
Root Cause: Python string escaping turned intended JS `\n` into a literal newline inside a JS single-quoted string.
Correct Solution: raw Python JavaScript expression preserving browser-side escape bytes.
Prevention Rule: Python-embedded JS requires explicit escaping regression tests.

### ERR-49-025 — Real Provider Hub keys/model lists disappeared visually
Root Cause: 49.3I.6 hydrated legacy `ai_key`, while modern Provider cards use `_ai_hub_key_vars` and secure Save clears those widgets.
Correct Solution: hydrate real provider-card variables, rehydrate after Save, and background-load model catalogs through the mature provider client.
Prevention Rule: credential/model readiness tests target the real current Provider Hub controls.

### ERR-49-026 — Bottom All-Fields AI bypassed mature Task Center
Symptoms: operator waited ~5 minutes with only a status string and no durable connection/send/receive/result view.
Root Cause: visible Phase49.3C button still called legacy `generate_ai("commerce")` instead of `_phase49_3e_run_ai()`.
Correct Solution: route real operator All-Fields/non-Quick actions to mature Task Center; add elapsed time, Stop Waiting, 210-second watchdog and generation-based stale-result discard.
Prevention Rule: tests must exercise the exact visible button command after all composition layers.

### ERR-49-027 — All-Fields rerun could not refresh AI output and generic titles persisted
Symptoms: specific source title could remain `محصول چاپ 3 بعدی`; changing Provider/Model and rerunning did not replace non-empty generated fields.
Root Cause: mature Task Center correctly filled blanks only, but explicit refresh had no distinction between manual and AI-owned values.
Correct Solution: 49.3I.9 refreshes AI-owned/previous-pack fields, protects proven manual overrides, rejects generic titles, strengthens source-grounded Persian/SEO prompt, optionally reuses mature image refetch, and re-applies publisher/SEO source attribution to real Product fields.
Prevention Rule: explicit AI refresh distinguishes generated state from manual ownership and validates product identity before persistence.

### ERR-49-028 — AI HTTP succeeded but delayed Tk error callback crashed; title retry had no full trace
Date: 2026-08-23
Environment: Windows Catalog Center 8.7.1 / Product Workspace / Provider Hub
Related Phase: 49.3I.10
Symptoms:
- operator could not tell what title request was sent, what was returned, or whether the provider/model failed,
- an AI request could return HTTP 200 but the UI then raised `NameError: cannot access free variable 'exc' where it is not associated with a value in enclosing scope`,
- title-only translation had no bounded progress/Stop Waiting/stale-result protection,
- an already populated but wrong Persian title made retry behavior ambiguous.
Verified Root Cause:
- delayed Tk callbacks used lambdas that closed over `except Exception as exc`; Python deliberately clears the exception target at the end of the except block, so the later Tk callback could dereference an empty closure cell,
- the quick title action had its own minimal background path rather than the mature observable AI progress contract,
- provider diagnostics logged request summaries but did not expose the actual sanitized payload/result to the operator.
Correct Solution — Phase49.3I.10:
- add `phase49_3i_ai_trace_recovery.py` at the final Workspace composition boundary,
- wrap the final AI progress UI with scrollable outgoing request / incoming response / error-diagnostics tabs,
- trace sanitized OpenAI-compatible and Google Gemini payloads/responses to the UI and existing Phase49 JSONL,
- never include API key/token/Authorization header in those trace details,
- replace title-only action with an explicit rerunnable current-Provider/Model flow,
- title watchdog = 90 seconds,
- Stop Waiting/timeout/workspace close invalidates generation; late result is discarded,
- reject generic/non-Persian/too-short title before DB write,
- install a narrow Tk `after()` exception-closure freezer that copies a live exception object before Python clears the original `exc` cell; unrelated callbacks remain unchanged.
Verification:
- implementation PR #56 merged,
- Phase49.3I Run `32626758096` SUCCESS,
- Phase49.3H Run `32626758114` SUCCESS,
- Phase49.3G Run `32626758134` SUCCESS,
- Full Phase49 + Full Django Run `32626758119` SUCCESS,
- dedicated `test_epic49_phase49_3i_ai_trace_recovery.py` PASS,
- Django migration NONE; Catalog schema migration NONE.
Prevention Rule:
- never schedule a delayed callback that references a raw `except ... as exc` target without binding/freezing its value,
- every operator AI action must expose a bounded, scrollable, sanitized request/result/error path and stale-result safety,
- a successful provider HTTP status is not sufficient acceptance; UI application/result state must also be observable and tested.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Status: OPEN / outside current 49.3I employee release gate.
Rule: verify route/client contract before adding any duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Status: mitigated by Phase49.3H.
Rule: never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image acquisition limit inconsistency
Status: runtime contract addressed; Windows QA remains.
Rule: default 10 / hard max 20 through the canonical normalizer.

## Warning Debt
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process architecture; Redis/polling remains separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
