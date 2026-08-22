# ERROR KNOWLEDGE BASE

Search this file before troubleshooting. Do not repeat a failed action unless its underlying condition changed.

## RESOLVED ERRORS

### ERR-49-001 — Tkinter pack/grid collision in Product Workspace
Date: 2026-08-19
Environment: Windows Catalog Center
Related Phase: 49.3D
Symptoms: `TclError: cannot use geometry manager pack ... which already has slaves managed by grid`
Root Cause: an older guided-AI control used `pack()` directly in a tab whose children used `grid()`.
Correct Solution: add a dedicated holder/container using the parent geometry manager; children may use a different manager only inside that new holder.
Verification: regression tests + later Phase49 CI.
Prevention Rule: never mix `pack` and `grid` for siblings with the same Tk parent.

### ERR-49-002 — Thumbnail callback after widget destruction
Date: 2026-08-19
Environment: Windows Catalog Center
Symptoms: `TclError: invalid command name ...label` from async thumbnail callbacks.
Root Cause: delayed image callback targeted a destroyed/rebuilt widget.
Correct Solution: lifecycle-safe UI callbacks / avoid updating dead widget instances.
Prevention Rule: any delayed/thread->Tk callback must verify target lifecycle and marshal to active UI only.

### ERR-49-003 — Destroyed ProductWorkspace used as messagebox parent
Date: 2026-08-19
Environment: Windows Catalog Center
Symptoms: `TclError: bad window path name .!productworkspace`.
Root Cause: async callback completed after the Workspace was closed.
Prevention Rule: async UI completion must detect widget existence before dialog/update.

### ERR-49-004 — Missing `header_badge`
Date: 2026-08-19
Environment: Windows Catalog Center
Symptoms: `AttributeError: '_tkinter.tkapp' object has no attribute 'header_badge'`.
Root Cause: callback assumed a UI state variable existed in every shell configuration.
Prevention Rule: feature patches must use verified shell contracts / guarded attributes.

### ERR-49-005 — Image SEO semantic signature false-stale
Related Phase: 49.3D
Root Cause: raw JSON byte/string representation was hashed; escaped/unescaped Persian JSON was semantically equal but produced a different signature.
Correct Solution: normalize semantic JSON before hashing.
Prevention Rule: signatures for structured data must hash normalized semantic representation.

### ERR-49-006 — Dynamic price consultation flag overwritten
Related Phase: 49.3D/49.3F
Root Cause: a later product-details importer assignment overwrote `consultation_required=True` set by price range logic.
Correct Solution: preserve existing truth using OR semantics.
Prevention Rule: later sync stages must not blindly overwrite decisions made by an earlier contract layer.

### ERR-49-007 — Phase49.3F Windows NativeCommandError after successful migrations
Date: 2026-08-20
Environment: Windows PowerShell 5.1
Symptoms: migrations `store.0033` and `website.0023` applied OK, then runner aborted while capturing `showmigrations` output.
Root Cause: `$ErrorActionPreference='Stop'` + native stderr redirected with `2>&1`; harmless Django warning became terminating PowerShell error despite native exit code 0.
Correct Solution: `Invoke-NativeCapture` temporarily uses Continue for capture and treats native exit code as source of truth.
Prevention Rule: do not use raw `(& native.exe ... 2>&1)` under StrictMode/EAP Stop for success/failure decisions.

### ERR-49-008 — Runtime Trace inline Bearer token redaction leak
Related Phase: 49.3F
Root Cause: generic Authorization redaction ran before Bearer credential redaction and could leave token tail visible.
Correct Solution: redact Bearer credential first, then generic key/value patterns.
Prevention Rule: secret-redaction order is a security contract; keep regression tests.

### ERR-49-009 — Phase49.3G installed inside independent 49.3F Source Guard
Related Phase: 49.3G
Symptoms: full Phase49 regression failed on minimal Workspace stub missing `reload`.
Root Cause: cross-phase feature composition was chained inside an older independently tested installer.
Correct Solution: keep 3F installer independent and compose 3G only in `catalog_center/launch.py`.
Prevention Rule: cross-phase composition belongs in the composition root, not inside independent prior-phase installers.

### ERR-49-010 — Historical Bridge import main-image failure
Date: 2026-08-10/11
Environment: Desktop publish to Bridge
Symptoms: `ValidationError: ['قبل از تبدیل، تصویر اصلی باید در Media ذخیره یا بارگذاری شود.']`
Root Cause: product main image was not materialized into site Media before conversion/import.
Prevention Rule: Publish packaging/preflight must guarantee selected/primary image is materialized and owned by the target Media contract before import.

### ERR-49-011 — Phase49.3H CI fixture assumed `upsert_product()` returns product ID
Date: 2026-08-22
Related Phase: 49.3H
Symptoms: dedicated tests failed with `TypeError: int() argument ... not 'NoneType'`.
Root Cause: new test fixture guessed a return-value contract not guaranteed by the actual Database API.
Correct Solution: perform upsert, then resolve the row by verified source identity and read its DB id.
Prevention Rule: tests must use actual repository method contracts; do not infer return values.

### ERR-49-012 — Phase49.3H redaction assertion coupled to display format
Date: 2026-08-22
Related Phase: 49.3H
Symptoms: safe output `Authorization: *** ***` failed a test expecting literal `Bearer ***`.
Root Cause: test asserted one formatting representation instead of the security invariant.
Correct Solution: assert original secret is absent and Authorization is masked; do not weaken runtime redaction.
Prevention Rule: security tests assert semantic invariants plus leak absence, not incidental mask formatting.

### ERR-49-013 — Explicit MakerWorld search URL ignored in search mode
Date: 2026-08-22
Environment: Windows Catalog Center discovery
Related Phase: 49.3I
Symptoms: owner supplied `https://makerworld.com/en/search/models?keyword=cake+stand` but unrelated products were collected.
Verified Root Cause: `main.py::_scan_worker` selected `target_templates=listing[:1]` for `mode == "search"`, so the explicit `seed` search URL was ignored and the configured default MakerWorld listing was scanned instead.
Correct Solution: explicit HTTP(S) seed/listing URL is authoritative. Discovery first creates review candidates; full product extraction occurs only after operator approval.
Verification: Phase49.3I dedicated CI Run `32569551060` + full Phase49 Run `32569551034`.
Prevention Rule: never silently substitute a configured discovery URL when an operator supplied an explicit valid URL. Regression-test exact target selection.

### ERR-49-014 — Discovery performed full extraction before human review
Date: 2026-08-22
Related Phase: 49.3I
Symptoms: discovery immediately downloaded/parsed full products and many images, wasting time and producing unwanted catalog rows.
Verified Root Cause: after URL discovery `_scan_worker` immediately iterated `pending_urls` and called full collection/parse.
Correct Solution: split discovery into Preview Candidate and Approved Full Fetch states; archive/not-needed creates only blocked identity.
Verification: Phase49.3I dedicated CI Run `32569551060`.
Prevention Rule: discovery and acquisition are separate state transitions; preview must not call the full extractor.

### ERR-49-015 — Runtime pricing choices created a phantom Django migration
Date: 2026-08-22
Related Phase: 49.3I
Environment: GitHub CI / Django migration contract
Symptoms: initial Phase49.3I PR #41 passed Catalog tests but `makemigrations --check --dry-run` proposed `store/migrations/0034_alter_productcatalogprofile_pricing_strategy.py`.
Root Cause: the first range implementation mutated `ProductCatalogProfile.pricing_strategy` runtime `choices`. Django field choices are migration state metadata, so the apparently runtime-only change was detected as `AlterField`.
Failed Attempt: treating a runtime `field.choices` mutation as schema/migration-neutral.
Correct Solution: keep migration-owned 49.3F field choices unchanged; persist semantic raw value `range` in the existing `CharField(max_length=20)`; Windows exposes the three operator modes and server sync stores `pricing_strategy=range` + `price_mode=range` without changing field metadata.
Verification: replacement PR #42; dedicated 49.3I Run `32569551060` SUCCESS; Full Phase49/Django Run `32569551034` SUCCESS; `makemigrations --check --dry-run` reports no changes.
Prevention Rule: changing Django field metadata such as `choices` is migration state even if the SQL column type does not change. If a semantic value is intentionally schema-free, do not mutate migration-owned model field metadata.

### ERR-49-016 — Phase49.3I runner parse failure on Windows PowerShell 5.1
Date: 2026-08-22
Related Phase: 49.3I runner hotfix
Environment: Windows PowerShell 5.1
Symptoms: `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` failed before execution with multiple `Unexpected token ')'` parser errors around the manual QA lines; Persian labels appeared as mojibake such as `Ø...`.
Verified Root Cause: the GitHub runner was stored as UTF-8 without BOM but contained Persian text and an em dash. Windows PowerShell 5.1 uses legacy ANSI decoding for BOM-less script files. The UTF-8 bytes were decoded as mojibake; the em-dash byte sequence produced a smart-quote character that PowerShell treats as a string delimiter, terminating a string early and causing the later `)`/`<` parse errors.
Correct Solution: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.1` is ASCII-only and CI rejects non-ASCII bytes.
Verification: CI-only PR #44; Phase49.3I `32570978818`, 49.3H `32570978800`, 49.3G `32570978829`, Full Phase49 `32570978799` SUCCESS.
Prevention Rule: canonical Windows PowerShell 5.1 runners must remain ASCII-only or carry a separately verified encoding contract.

### ERR-49-017 — Phase49.3I Products UI patch missed the real UX87 composition boundary
Date: 2026-08-22
Related Phase: 49.3I
Symptoms: Products page still showed the legacy parameter/editor surface and no intended image-card gallery.
Verified Root Cause: UX87 `_ui()` explicitly calls `super()._products_ui()` then `_modernize_products_page()`, bypassing the original patch target.
Correct Solution: patch the real `_modernize_products_page` boundary, keep mature backend hidden, render local image gallery.
Verification: CI-only PR #46; all Phase49 CI SUCCESS.
Prevention Rule: UI patch tests must verify the real shell composition boundary.

### ERR-49-018 — AI progress window was created after synchronous preflight work
Date: 2026-08-22
Related Phase: 49.3I
Symptoms: full AI autofill looked frozen before progress appeared.
Root Cause: synchronous save/preflight/source preparation ran before progress construction.
Correct Solution: immediate lightweight first-paint, then Tk `after()` handoff to mature 49.3H progress/result/error/cost stack.
Prevention Rule: synchronous UI-thread preflight must not begin before visible feedback is painted.

### ERR-49-019 — Windows handoff failed because Chat-pinned Expected HEAD became stale
Date: 2026-08-22
Environment: Windows PowerShell / GitHub handoff
Root Cause: mutable branch advanced after a fixed SHA was copied into Chat.
Correct Solution: live `git fetch --prune origin`, exact branch, clean worktree, Local HEAD equals fetched Remote Epic HEAD; ff-only pull if behind.
Prevention Rule: never use a Chat-pinned SHA as sole source of truth for a mutable branch.

### ERR-49-020 — Product images were clipped into thin horizontal strips
Date: 2026-08-22
Environment: Windows Catalog Center Products gallery
Root Cause: a 260x190 PhotoImage was assigned to a `tk.Label(width=32,height=12)` where width/height were text-unit dimensions.
Correct Solution: pixel-sized holder frame + unconstrained image Label.
Prevention Rule: pixel image contracts must not be sized through Tk text-unit Label dimensions.

### ERR-49-021 — Group/category URLs could be misclassified as direct product links
Date: 2026-08-22
Environment: Windows Catalog Center discovery/direct-link intake
Root Cause: finite URL-shape heuristics were used instead of configured source `model_url_pattern`.
Correct Solution: only URLs matching the source product regex may take direct intake; other valid source URLs go Preview-first.
Prevention Rule: classify product identity from verified source product pattern, not guessed listing paths.

### ERR-49-022 — Hidden Treeview selection feedback loop froze Product open/preview
Date: 2026-08-22
Environment: Windows Catalog Center Products Explorer
Root Cause: card selection wrote Treeview selection; `<<TreeviewSelect>>` called `load_product`; compatibility callback wrote selection again.
Correct Solution: one-way event-producing sync, re-entrancy guard, state-only reverse callback, repeat-open guard.
Prevention Rule: never write the same Tk selection from its own selection callback.

### ERR-49-023 — Secure credentials appeared lost because masked fields were not hydrated
Date: 2026-08-22
Environment: Windows Catalog Center UX87
Related Phase: 49.3I.6
Symptoms: FTP password, Bridge token and legacy AI key looked empty after save/restart.
Root Cause: secure backend worked, but masked fields did not mirror persisted Windows Credential Store values and mature Save handlers cleared widgets.
Correct Solution: hydrate legacy connection/AI fields from secure storage at startup and after Save.
Failed Condition Discovered Later: Phase49.3I.6 covered the legacy single AI key field but not the real Phase49.3F per-provider `_ai_hub_key_vars`; see `ERR-49-025`.
Prevention Rule: persistence tests must target the real current operator widgets, not only legacy compatibility fields.

### ERR-49-024 — Preview Candidate evaluate_all JavaScript became syntactically invalid
Date: 2026-08-22
Environment: Windows Catalog Center / MakerWorld Preview
Related Phase: 49.3I.7
Symptoms: exact MakerWorld search URL routed correctly to Preview, but every attempt failed with `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`; `candidates=0 failed=1 full_fetch=0`.
Verified Root Cause: `phase49_3i_discovery_review.py` passed a normal Python triple-quoted JavaScript expression containing `+'\n'+` source text. Python converted that escape into a literal line break before Playwright evaluated it, leaving a raw newline inside a JavaScript single-quoted string. Playwright correctly rejected the invalid browser-context expression.
Evidence: owner screenshot showed the error at `UtilityScript.evaluate`; repository inspection found the exact expression. Official Playwright contract states `locator.evaluate_all(expression)` executes the supplied JavaScript expression in page context.
Correct Solution: Phase49.3I.7 installs a narrow Stage-1 Preview recovery using a raw Python JavaScript string so the browser receives the two characters backslash+n. It reuses the existing `candidates_from_dom_rows()` lightweight parser and does not call mature full-product extraction.
Preserved Mature Path: `classic_methods.discover_classic` and `collect_classic_exact` are not rewritten; Direct Product and approved Full Fetch remain their existing mature paths.
Verification: `test_epic49_phase49_3i_preview_recovery.py`, Phase49.3I CI and Full Phase49 regression CI, then Windows real MakerWorld Preview QA.
Prevention Rule: any Python-embedded JavaScript passed to Playwright must have an explicit escaping contract and a regression test for the exact browser expression; never assume Python string escaping preserves JavaScript source bytes.

### ERR-49-025 — 49.3I.6 hydrated the legacy AI field but real Provider Hub keys still disappeared visually
Date: 2026-08-22
Environment: Windows Catalog Center AI Center
Related Phase: 49.3I.7
Symptoms: AvalAI/OpenRouter/OpenAI/Google provider-card API Key fields appeared empty again after restart/update; model picker then behaved as if the Provider had no key, so live model lists were not visible.
Verified Root Cause: the modern Phase49.3F AI Center uses per-provider `_ai_hub_key_vars`. `phase49_3i_secret_persistence.py` 49.3I.6 only hydrated legacy `ai_key`, FTP password and Bridge token. Meanwhile the mature provider save handlers stored the key in Windows Credential Store and intentionally cleared `_ai_hub_key_vars[provider]`. Therefore secure runtime fallback could still work while the real visible Provider cards were empty.
Correct Solution: Phase49.3I.7 hydrates every real provider-card key variable from Windows Credential Store, also rehydrates OpenRouter management/OpenAI admin masked fields, and restores the card immediately after mature secure Save clears it. It also background-loads model catalogs for configured providers into the existing Model ID combobox/cache using the mature `AIProviderClient.list_model_info()` path.
Provider API Contract: AvalAI uses its authenticated `/v1/models`; OpenRouter uses `/api/v1/models`; existing OpenAI/Google adapters remain preserved.
Secret Safety: credentials remain only in Windows Credential Store/environment; no secret is written to SQLite, Git, source, diagnostics or logs.
Verification: expanded `test_epic49_phase49_3i_secret_persistence.py`, secure composition contract, provider model-cache/combobox tests, Phase49.3I/3H/3G/full CI, then Windows restart/model-list QA.
Prevention Rule: credential persistence and model-list readiness must be regression-tested against the real active Provider Hub state variables and save handlers after all composition layers are installed.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Status: OPEN / outside Phase49.3I
Rule: investigate route/client contract before Epic closure; do not add duplicate endpoint without root-cause verification.

### ERR-OPEN-002 — AI request cost may be unknown
Status: mitigated by Phase49.3H
Rule: never invent a cost. Use provider response or verified provider cost lookup; otherwise mark unknown.

### ERR-OPEN-003 — Historical image acquisition limit inconsistency
Status: runtime contract addressed by Phase49.3H; Windows pull/QA pending
Rule: canonical normalizer is default 10 / hard max 20 across new intake/refetch/persisted-selected flows.

## Warning Debt (not current blockers)
- `ckeditor.W001`: CKEditor4 security/maintenance debt.
- `store.W026`: in-memory realtime not suitable for multi-process production without Redis/polling strategy.
- Pillow `Image.getdata()` deprecation.
- Google membership credentials warning when intentionally unset in CI.
