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
Root Cause: search mode chose configured listing instead of explicit seed.
Correct Solution: a valid explicit HTTP(S) operator URL is authoritative.
Prevention Rule: never silently substitute a default discovery URL.

### ERR-49-014 — Discovery full-fetched before human review
Root Cause: URL discovery immediately entered full product extraction.
Correct Solution: `Preview Candidate → Approve/Archive → Approved Full Fetch`.
Prevention Rule: preview and acquisition are separate state transitions.

### ERR-49-015 — Runtime pricing choices created phantom Django migration
Root Cause: runtime code mutated Django field `choices`, which is migration-state metadata.
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
Root Cause: Python string escaping turned intended JS `\n` into a literal newline inside a JS single-quoted string.
Correct Solution: raw Python JavaScript expression preserving browser-side escape bytes.
Prevention Rule: Python-embedded JS requires explicit escaping regression tests.

### ERR-49-025 — Real Provider Hub keys/model lists disappeared visually
Root Cause: 49.3I.6 hydrated legacy `ai_key`, while modern Provider cards use `_ai_hub_key_vars` and secure Save clears those widgets.
Correct Solution: hydrate real provider-card variables, rehydrate after Save, and background-load model catalogs through the mature provider client.
Prevention Rule: credential/model readiness tests target the real current Provider Hub controls.

### ERR-49-026 — Bottom All-Fields AI bypassed mature Task Center
Root Cause: visible Phase49.3C button still called legacy `generate_ai("commerce")` instead of `_phase49_3e_run_ai()`.
Correct Solution: route real All-Fields/non-Quick actions to the mature Task Center; add elapsed time, Stop Waiting, 210-second watchdog and generation-based stale-result discard.
Prevention Rule: tests exercise the exact visible button command after all composition layers.

### ERR-49-027 — All-Fields rerun could not refresh AI output and generic titles persisted
Root Cause: mature Task Center filled blanks only; explicit refresh had no distinction between manual and AI-owned values.
Correct Solution: 49.3I.9 refreshes AI-owned/previous-pack fields, protects proven manual overrides, rejects generic titles, strengthens source-grounded Persian/SEO prompt, optionally reuses mature image refetch, and re-applies publisher/SEO source attribution.
Prevention Rule: explicit AI refresh distinguishes generated state from manual ownership and validates product identity before persistence.

### ERR-49-028 — AI HTTP succeeded but delayed Tk error callback crashed; title retry had no full trace
Date: 2026-08-23
Root Cause: delayed Tk callbacks captured `except ... as exc`, but Python clears that exception target when the block exits; title-only action also lacked full observable bounded execution.
Correct Solution: 49.3I.10 added scrollable sanitized request/response/error tabs, 90-second title watchdog, stale-result protection, explicit current-Provider/Model retry, generic-title validation and targeted exception-closure freezing.
Verification: PR #56 merged; Phase49.3I `32626758096`, 3H `32626758114`, 3G `32626758134`, Full Phase49 `32626758119` all SUCCESS; no migration.
Prevention Rule: delayed callbacks must freeze exception values; HTTP success alone is not acceptance—UI application/result state must also be observable.

### ERR-49-029 — Provider returned useful JSON but wrong schema; model trace and stale busy state looked hung
Date: 2026-08-23
Environment: Windows Catalog Center 8.7.1 / AvalAI / Product Workspace
Related Phase: 49.3I.11
Symptoms:
- AvalAI returned HTTP success and a semantically useful Persian product payload,
- returned aliases included `seo_title` / `seo_description` instead of required `seo_title_fa` / `seo_description_fa`,
- `content_notes` returned as a string while the Catalog schema requires an array,
- multiple required fields were missing, so the validator reported `SEO Title فارسی ... خالی برگشت`,
- the request/response console displayed the complete large `/models` payload and could make Tk appear frozen,
- after Stop Waiting/watchdog the Workspace could remain busy, blocking an immediate Provider/Model retry until the old worker returned.
Verified Root Cause:
- non-OpenAI `AIProviderClient.structured_response()` asked AvalAI/OpenRouter only for a generic `json_object`; it did not transmit the actual repository JSON Schema to those compatible gateways,
- 49.3I.10 traced the entire model catalog into a Tk `Text` widget on the UI thread,
- abort/stale paths marked the generation cancelled but did not immediately clear parent busy flags; stale apply wrappers could return before the mature `finally` that normally clears them.
Correct Solution — Phase49.3I.11:
- send the actual JSON Schema to AvalAI/OpenRouter using strict `json_schema` where supported,
- always include exact schema/property names/types in the system contract,
- compatibility fallback is bounded: strict schema → `json_object` → no response format,
- validate provider JSON against the required schema before application,
- if the first valid JSON violates schema, perform exactly one visible repair request carrying the invalid output plus validation errors; reject precisely if repair still fails,
- use an explicitly selected model directly for the current request,
- cache model information inside the client request window and avoid duplicate model-catalog probes,
- summarize `/models` trace as count + bounded sample instead of dumping the full catalog into Tk,
- on Stop Waiting/watchdog/stale abort, release `_phase49_3e_busy`, `_ai_busy`, source/start flags immediately so another Provider/Model run can start while the old network worker finishes in the background,
- late old output remains stale/non-applicable.
Verification:
- implementation PR #57 merged,
- validated feature head `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`,
- merge commit `41d37d56437765119b9bb274037e9af7a5defbbe`,
- Phase49.3I Run `32628666588` SUCCESS,
- Phase49.3H Run `32628666600` SUCCESS,
- Phase49.3G Run `32628666558` SUCCESS,
- Full Phase49 + Full Django Run `32628666582` SUCCESS,
- dedicated exact-owner-response/schema-repair/model-trace/busy-release tests PASS,
- Django migration NONE; Catalog schema migration NONE; Production untouched.
Prevention Rule:
- HTTP 200 + syntactically valid JSON is not enough; provider output must satisfy the exact application schema before persistence,
- never dump a full provider model catalog into the synchronous Tk display path,
- cancel/timeout/stale paths must release operator busy state immediately while separately preventing late-result mutation.

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
