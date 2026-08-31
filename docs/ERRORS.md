# PROJECT ERROR KNOWLEDGE BASE

## ERR-49-082 — OpenRouter Product AI accepted media/tools-only models and could fall back to unconstrained text
**Date:** 2026-08-31  
**Environment:** owner Local Windows Qt6 foreground QA after Phase49.3I.42C3.

**Observed owner evidence:**
1. Provider test used `google/lyria-3-clip-preview` and the Structured Product JSON path received timed Persian song lyrics instead of a JSON object, ending in `JSONDecodeError`.
2. Product #309 with `cohere/north-mini-code:free`, source mode `link`, failed because `SEO Title فارسی` returned empty.
3. Product #309 with the same model, source mode `data`, failed because the Persian title was generic/invalid and did not preserve source identity.

The existing downstream content validators behaved correctly: they rejected empty SEO and generic Product identity before bad content could be saved.

**Root cause:**
- model suitability ranking did not use live output modality/product-purpose metadata;
- `tools` / `tool_choice` were incorrectly treated as equivalent to native `response_format` / Structured JSON support;
- a music/media model could therefore appear usable for Product text work;
- a tools-only coding model could receive an overly strong Product/JSON badge;
- OpenRouter Structured calls used a weaker `json_object` request and could fall back to prompt-only JSON when a model rejected `response_format`, allowing unconstrained prose/song/code output;
- active Product AI did not require a previously verified live OpenRouter model capability profile before execution.

**Correct fix:**
- classify live model input/output modalities and exclude non-text media/embedding/rerank/moderation models from Product filters;
- separate native Structured JSON support from tool-calling support;
- mark coding-specialist models as unsuitable for Persian Product SEO/content;
- Product recommendation/sort now prioritizes text-capable + native Structured + Persian quality, then free/cost;
- OpenRouter Structured Product calls use strict `json_schema` and `provider.require_parameters=true`;
- OpenRouter no longer falls back to prompt-only JSON when the required Structured contract is unsupported;
- Structured Product calls use latency-first routing while ordinary bulk/content paths retain their existing routing intent;
- saving an OpenRouter Product model requires a live loaded model catalogue entry and stores a non-secret capability snapshot;
- Product AI estimate/execute preflight rejects stale/unverified/incompatible OpenRouter models before the mature orchestrator runs;
- settings UI now distinguishes `JSON✓`, Tools-only, coding-specialist and non-text models, and Product filters hide non-text models.

**Regression coverage:**
- Lyria/music model is rejected as non-text Product model;
- `cohere/north-mini-code:free` is rejected as tools-only/code-specialized Product Structured candidate;
- OpenRouter Structured request carries strict JSON Schema + `require_parameters`;
- exact selected model remains preserved;
- simple connection test still performs no hidden model-catalog scan;
- mature Qt/Crawl/Filament/Profile/Stage/Single-AI/legacy launcher regressions remain green.

**Intermediate failed condition:** run `33398832365` failed only because an older 42B2 regression still expected Structured Product routing to use `throughput`. The runtime condition had intentionally changed to latency-first. The stale test was corrected rather than rerunning the same failing expectation unchanged.

**Final verified code checkpoint:** `0421bccff040ced53513625af95d05e0c8c27a9a`.
- `33399095190` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS;
- `33399095198` — Phase49.3I.17 Single Active AI CI — PASS;
- `33399095224` — Catalog Center Windows Portable Release — PASS.

**Rollback:** `backup/pre-err49-082-openrouter-product-model-gate-20260831` → `26761c81d04bbd74dc2c978b08e77f3250b0518b`.

**Safety:** no Django migration, no Catalog schema migration, no Product/media rewrite, no secret persistence, no Host/Production change, and no default launcher cutover.

**Prevention rule:** a Provider connection success is not a Product-model acceptance test. Product AI must require a text-capable model with verified native Structured JSON support and a real Persian Product probe; tool calling, free pricing or generic multilingual capability alone must never imply Product suitability.


## ERR-49-081 — Windows Playwright smoke probe was corrupted at the PowerShell/native `python -c` boundary
Status: `FIXED IN REPOSITORY / WINDOWS CI PASS / OWNER LOCAL RERUN NEXT`

Observed:
- owner Local was clean on the canonical branch and correctly advanced to `3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`;
- Catalog SQLite backup completed and source/backup SHA256 both matched `F0C1341C764074423A2214F0DFF80EEB9E1248DA69F5FE9470D1FDDA0B1A5422`;
- Python 3.12.10, PySide6 6.11.2, HTTPX 0.28.1, Protego and Playwright imports were healthy;
- the gate then stopped at the Playwright smoke marker with `NameError: name 'OK' is not defined`, and the retry produced the same class of error for `OK_AFTER_INSTALL`.

Root cause:
the Local runbook passed a multi-line Python here-string through the native-process `python -c` argument boundary. Windows PowerShell/native quoting transformed the quoted marker before Python evaluated it. The gate incorrectly classified this probe-code failure as a missing Chromium runtime and attempted an unnecessary browser install.

This was not evidence of a Qt acquisition/runtime defect. The Python traceback reached the marker line after `p.chromium.launch(headless=True)`, so the first browser launch itself had already succeeded.

Correct fix:
- repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` now sends multi-line Python through stdin: `$Script | & $Py -`;
- Chromium installation is attempted only when the actual Playwright error explicitly reports a missing executable / `playwright install`;
- other probe failures stop without a blind reinstall;
- the Qt Windows workflow now parses the Local gate with PowerShell's parser and regression-tests the exact PowerShell → Python stdin boundary.

Implementation:
- `71c55010bc900e8d3c1afd7cea71441193db68eb` — resilient owner Local gate;
- `e6980fcfb2bdc72846e007e9d935290225dcb39e` — CI syntax/stdin guard;
- Single Active AI run `33386654622` PASS;
- Phase49.3I.42C workflow run `33386654632` PASS, including PowerShell parser validation, the exact PowerShell → Python stdin regression boundary, Qt/acquisition regressions and launcher guards.

Prevention:
- do not send multi-line Python containing nested quoting through `python -c` in Windows Local gates;
- use stdin or a repository script for multi-line Python;
- only install Playwright browsers when the failure is actually a missing-browser failure;
- a probe/quoting error must never be relabeled as a dependency error;
- do not repeat the failed inline command unchanged.

## ERR-49-080 — Qt42B2 rollout CI exposed generated-source and guessed-test-name defects
Status: `FIXED / FINAL WINDOWS CI PASS`

Observed:
1. run `33369083134` stopped at compile because `qt6/__init__.py` contained literal escaped-newline text and the Stage-5 saver missed an opening call parenthesis;
2. run `33369290159` then reached mature regressions but referenced nonexistent `tests.test_phase49_3i35_operator_ledger`;
3. run `33369521548` passed compile/Qt/Filament/Profile/Stage regressions but referenced nonexistent `tests.test_phase49_3i17_single_active_ai_runtime`.

Root cause:
- one generated source blob serialized newlines incorrectly and one generated call site lost punctuation;
- the aggregate Qt workflow guessed two unittest module names instead of verifying the real Repository test names / canonical Single Active AI workflow.

Failed conditions were not repeated unchanged.

Correct fixes:
- `74e95a943d3324f3d00b4e61bd9a265efcca4e3f`: fixed real newlines and Stage-5 call syntax;
- `d433395cabc8ed488431f3b873adc337acb7d6b6`: switched to existing `tests.test_phase49_3i35_operator_workflow`;
- `c3b0105eaa6c6141eb6d6d8463a96d547101564c`: switched to canonical `tests.test_epic49_phase49_3i17_single_active_ai_runtime`.

Verification:
- final Windows Qt run `33369749205` PASS with every job step successful;
- dedicated Single Active AI run `33369749123` PASS;
- compile, Qt parity, mature Filament/Profile/Stage/AI regressions, Qt launcher, legacy launcher and source guards all passed.

Rollback anchors:
- `backup/pre-phase49-3i42b2-full-legacy-parity-20260830` → `6260f94cee531124446cf1b3e19ce0d95554d594`;
- `backup/pre-err49-080-qt42b2-compile-hotfix-20260831` → `fc4edfd3ccab089ac242e84f291dd6454b85d7d7`.

Prevention:
- generated source blobs must compile before functional tests;
- workflow test module names must be verified from the actual Repository tree or canonical workflow, never inferred;
- a failed CI command is not rerun until its root condition changes.


## ERR-49-079 — Qt Local preview gate used an obsolete ExpectedHead
Status: `FIXED / PREVENTION RULE ADDED`

Observed:
- owner Local checkout started clean on the canonical branch at `92a3f4df...`;
- `git fetch` + `git pull --ff-only` correctly advanced Local to live GitHub `3d32c251...`;
- the old 42A runbook still expected historical `fde58f38...`;
- the guard stopped with `UNEXPECTED HEAD - STOP` before backup/install/compile/Qt launch.

Root cause:
the runbook pinned a previously valid 42A documentation HEAD while the same canonical branch had legitimately advanced through 3I.43–45.

Resolution:
- do not rerun the stale command;
- verify the live remote branch SHA first;
- only then use the current approved GitHub HEAD in the guarded Local pull/test command.

Prevention:
every Local/Host runbook that pins a commit must compare its expected SHA to the live GitHub branch before write/install/migration/test steps. A mismatch is a stale-runbook stop, not an application failure.


### ERR-49-078 — robots.txt unreachable policy was incorrectly treated as unavailable
**Date:** 2026-08-30  
**Environment:** Catalog Center 8.9.9 / Phase49.3I.43–45 public acquisition.

**Symptom/Risk:** the pre-fix `robots_policy()` generic exception path returned `allowed=True`. A robots 5xx/network failure could therefore be treated the same as a genuine robots 4xx-unavailable resource and allow acquisition while policy was temporarily unreachable.

**Root Cause:** robots resource states were collapsed into one catch-all branch instead of distinguishing unavailable, unreachable and rate-limited outcomes.

**Correct Fix:** commit `11379ca343c64c251e9c34dd907dffa5f7529e12` makes the robots gate explicit:
- genuine robots 4xx unavailable → `known=False`, `allowed=True`, status `unavailable`;
- HTTP 429 → `known=True`, `allowed=False`, status `rate_limited`;
- transient 5xx/network/transport failure → `known=True`, `allowed=False`, status `unreachable`;
- unexpected robots fetch/parse failure → conservative fail-closed `unreachable`.

Existing conditional-cache, Retry-After/cooldown and robots pacing behavior remain intact.

**Regression:** `tests/test_phase49_3i43_modern_acquisition_intelligence.py` now covers unreachable fail-closed, 4xx unavailable/non-blocking and 429 fail-closed states.

**Verification:** dedicated Windows workflow `33313008595` PASS on `846cb63038a79cfe450f5a60aa66e531cf6fe0de`, which contains this fix, plus all 3I.43/3I.45 modern acquisition tests and mature 3I.16/3I.38 acquisition regressions.

**Rollback:** `backup/pre-err49-078-rfc9309-robots-failclosed-20260830` → `3616bf222f394b769cb2e3198164d735fca5267b`.

**Prevention:** acquisition policy code must model unavailable, unreachable, rate-limited and explicitly denied states separately. A temporary network/server failure must never silently become permission.

### ERR-49-077 — Qt6 workflow referenced runner context before a runner/job existed
**Date:** 2026-08-30  
**Environment:** new Phase49.3I.42 GitHub Actions workflow.

**Symptom:** run `33299686593` failed immediately and contained zero jobs.

**Root Cause:** `runner.temp` was referenced in job-level `env`. The runner context is not available at that workflow evaluation boundary, so GitHub rejected the job before execution.

**Failed condition:** do not rerun the same workflow definition unchanged.

**Correct Fix:** keep only static `QT_QPA_PLATFORM=offscreen` in job env and resolve `CATALOG_DATA_ROOT` inside the Windows PowerShell step using `$env:RUNNER_TEMP` after the runner is created.

**Verification:** corrected run `33299745502` PASS across dependency install, compile, Qt tests, 3I.41 regression, offscreen launcher, legacy launcher guard and no-Tk source guard.

**Prevention:** GitHub contexts with runner lifecycle scope must be resolved at step runtime unless documentation explicitly permits their use at the earlier evaluation boundary.


### ERR-49-076 — Stage-2 multi-Filament selection was technically possible but operationally ambiguous
**Date:** 2026-08-29  
**Environment:** Catalog Center 8.9.8 / Stage 2 after ERR-49-075.

**Symptom:** an inventory with many Filaments could only be managed through an extended Treeview selection whose multi-select behavior depended on Ctrl/Shift. The operator could not clearly see the complete Product selection set, global Filament definition was mixed into Product editing, and repeated Products encouraged repeated manufacturer/material typing.

**Root Cause:** the older UI modeled global Filament inventory and per-Product assignment as one filtered table. The data model already had reusable global inventory, but the final operator surface did not expose that ownership boundary.

**Correct Fix:** Phase49.3I.41:
- global main-app Filament Library;
- grouped PLA/PETG/etc. rows;
- one-click child/group checklist;
- dedicated Product selected-Filament pane;
- reusable manufacturer/brand/material selectors;
- explicit Product commit;
- Product fixed-price preservation;
- Site Bridge Filament entity synchronization.

**Site consistency:** Save/update/deactivate uses authenticated Bridge Filament upsert. Local save remains successful if the Site is temporarily unreachable; status is reported truthfully and Sync All is available.

**Migration safety:** no new migration. The bridge endpoint depends on existing `store.0039` + `0040`; do not deploy to Production until actual Host migration state and backups are verified.

**Rollback:** `backup/pre-phase49-3i41-filament-library-sync-20260829` → `92a3f4dfcf64d5fedaf837eb9a37dac028cabd59`.

**Prevention:** global reference/master data must have a dedicated management surface; Product forms should select from it and separately display the Product-owned selection state rather than overload native multi-select keyboard semantics.


### ERR-49-075 — saved Filament hidden after save and price preview used stale/zero facts
**Date:** 2026-08-29  
**Environment:** Catalog Center 8.9.8 / Phase49.3I.40 after ERR-49-074 owner visual QA.

**Owner visual evidence:**
- a newly created Filament saved successfully but did not become visible in the current list;
- the main inventory row showed a valid sale rate (example owner evidence: `4,200 تومان/گرم`) while the price preview opened on a different/stale Filament and showed material/print/supervision/preheat/total as zero;
- the selected-Filament editor was still the older 3I.39 dialog (including the Product fixed-price field) instead of the final 3I.40 global Filament editor with live rate calculation;
- current mode could be `range`, while the popup still attempted formula-style component rows, which was misleading.

**Root Cause:**
1. `add_available_material_color()` wrote all operational fields but its immediate post-upsert SELECT omitted `print_hourly_rate`, `supervision_hourly_rate`, preheat fields and `filament_image_url`; a just-saved in-memory snapshot therefore lost those facts until a later full inventory reload.
2. `edit_selected_offer()` directly called the local 3I.39 `open_offer_editor` closure, bypassing the final 3I.40 method override.
3. after save, the current manufacturer/material filters were not switched to the saved Filament, so a valid new row could be hidden by the previous filter.
4. pricing preview/summary primarily used the persisted Product Filament snapshot; it did not refresh that snapshot from current global Filament facts and did not use an unregistered currently selected Filament as a draft preview.
5. `range` preview fell through to the formula table instead of explaining the active range mode.

**Correct Fix:**
- return the complete operational Filament row immediately after upsert;
- route selected-Filament editing through the final composed 3I.40 editor;
- after save, switch company/material filters to the saved Filament, refresh the list, select/focus/scroll to the exact row;
- resolve pricing from fresh global Filament facts while preserving Product-only fixed price;
- if the operator selects a not-yet-registered Filament, use it as a clearly marked draft price preview;
- make range preview show the stored range and explicitly instruct switching to formula mode for component calculation;
- keep the explicit `ثبت Filamentهای انتخابی روی محصول` boundary; saving a global Filament does not silently attach it to the Product.

**Code:** `38d030024463a2057a10ad338abff5b030eb7e50`, `ab5f35523cbd76c79ed81344be57eb6b7485b075`, `cb78cb3ceb771fab54fcb8876dcd080516dcd462`, ttk fix `93b6e5c017965e50e62052afea37bfb30a86cc9d`.

**Regressions:** `ed4784f3019b2cf48c212ea429cb1b67420cbc97`, `58aac85bfd4bc0875d21c107515c8050fe0ddf74`, `7e7f8fcf3c07b5aeae9bc59684cc6fac97699f2d`, `d8661288273834a98627a1ec257b838b4a4ab086`.

**Rollback:** `backup/pre-err49-075-filament-refresh-pricing-preview-20260829` → `d66c68f36d1fd3e4143d461bccd999046c4baaf7`.

**Verification status:** GitHub source/tests updated. Owner Local compile + focused/full regression + short foreground Stage-2 QA is required. Production untouched.

**Prevention:** any DB upsert helper used to hydrate UI state must return the same operational facts that a full list/read returns; final composed UI callbacks must delegate through the class method override rather than close over an earlier implementation.


### ERR-49-074 — final Stage-2 price/rate calculation disappeared from the visible operator surface
**Date:** 2026-08-29  
**Environment:** Catalog Center 8.9.8 / Phase49.3I.40 after owner acceptance of ERR-49-073.

**Owner evidence before change:** exact ERR-49-073 regressions 2/2 PASS, OpenRouter-only 4/4 PASS, full Windows stage regression 73/73 PASS, foreground launch PASS. The image Metadata refresh issue cleared and the owner reported the Product ready for publication. Remaining Stage-2 usability regression: the mature calculation logic still existed, but the always-visible final amount/rate result had been removed from the final 3I.39/3I.40 composition. The visible buttons also still said `Offer`, while the operator terminology requested is `Filament`.

**Root Cause:** Phase49.3I.39 retained `formula_price_breakdown()` and a popup preview, and 3I.40 retained the exact global filament-rate facts, but the final visible Stage-2 card no longer exposed the computed final amount continuously. User-facing labels inherited internal historical `offer_*` naming.

**Correct Fix:**
- restore an always-visible final price summary for fixed, formula and range modes;
- formula summary uses the existing exact material + print + supervision + preheat + assembly calculation across registered Filaments and valid production rows;
- global Filament editor now shows the live final roll basis and exact Toman/gram rate from explicit sale price versus USD × explicit FX; no FX is invented;
- visible buttons/dialogs/readiness say `Filament`, not `Offer`;
- retain internal `offer_*` function/schema/API identifiers for backward compatibility; no storage/schema rename;
- enlarge the Filament editor so the added calculation panel and action buttons remain visible.

**Code:** `9540558468cc75bf0248547e7440f3647eeb4cd3`, `0c795bc0b7084b2e175f47f34533aa596d90fb03`, `267dc565b25ca74f3971334b7ad37d5c919a98ac`, regressions `109aaea748e7750bb22295aedf94de34ce617d88` + `4efc5a8350a3e9fbb7ade41f1098bc9cb9c80a7c`, layout `e4c1f3345bf9416bde11b6b6c7c7d31f6cdfd09c`.

**Rollback:** `backup/pre-err49-074-filament-rate-final-display-20260829` → `954c0516661e6c70145d7f6f395b4e92ceeb40bd`.

**Must not touch:** Catalog DB schema, Product identity, image/SEO finalization, OpenRouter AI contract, crawler/acquisition, Django migrations, Production.

**Verification status:** GitHub code/regressions updated. Owner Local focused/full/foreground retest is required before starting the website receive/deploy batch.

**Prevention:** final UI composition tests must assert not only that pricing math exists, but that the operator can continuously see the authoritative result and the requested domain terminology.


### ERR-50-017 — Store 0040 CI froze Decimal string presentation instead of numeric value
**Date:** 2026-08-29  
**Environment:** GitHub Actions `Phase50 Variant2 + Profile Matrix CI`, migration `store.0040_phase50_filament_offer_operations`.

**Symptoms:** compile, Storefront JavaScript, Django check, `makemigrations --check --dry-run`, migration plan and full CI SQLite migration all passed, but the regression step had two failures:
- `preheat_hours`: expected string `24.00`, runtime serialization returned `24`,
- `current_stock_grams`: expected string `3000`, runtime serialization returned `3000.0000`.

**Root Cause:** tests asserted a presentation-specific Decimal string even though the business/API contract is the numeric value. Equivalent Decimal values can have different textual scales.

**Failed Attempt:** do not rerun workflow `33246706102` unchanged; the deterministic assertions would fail again.

**Correct Fix:** compare the Decimal facts numerically rather than freezing insignificant trailing-zero formatting.

**Verification:** fix commit `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`; Phase50 workflow `33246843145` PASS, including full migration through 0040 and 21 Store/Profile/Checkout/Offer regressions.

**Prevention:** only assert exact decimal string formatting when formatting itself is an explicit public contract. For numeric commerce facts, normalize/compare numerically.

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
- **ERR-49-037 — Product AI could wait 210 seconds with weak start diagnostics:** bounded provider timeout + request-start/success/error/timeout trace.
- **ERR-49-038 — worker crossed Tk/Tcl thread boundary:** queue worker completions to the Tk main thread and snapshot Tk state before worker start.
- **ERR-49-039 — AvalAI Product request contract mismatch:** exact saved model + schema-first structured output + deterministic source fetch.
- **ERR-49-040 — diagnostics call rejected provider/model kwargs:** provider/model belong in sanitized detail; provider HTTP trace uses the dedicated AI request logger.
- **ERR-49-041 — hidden startup provider model scans:** model discovery is process-lifetime operator-explicit only.
- **ERR-49-042 — non-text model accepted for Product content:** reject obvious audio/music/image/video/embedding/moderation routes.
- **ERR-49-043 — exact-link AI triggered layered save storm:** persist only prerequisites before background generation.
- **ERR-49-044 — diagnostics/Product writes shared SQLite transaction connection:** dedicated diagnostics connection + serialized common DB writes.
- **ERR-49-045 — finite runtime log rotation conflicted with cumulative troubleshooting:** append-only runtime logging.
- **ERR-49-046 — delayed old gallery callback restored horizontal layout:** patch the final delayed layout callback at the outer composition boundary.
- **ERR-49-047 — Product AI completion depended on hidden image downloads:** text AI and source-image network acquisition are separate boundaries.
- **ERR-49-048 — readiness locking conflicted with canonical stage order:** readiness blocks publish, not navigation.

### ERR-49-049 — Exact-link category lookup called nonexistent `Database.categories()`
Correct fix: compatibility bridge delegates to mature `App.get_all_categories()` provider.

### ERR-49-050 — Exact-link canonical title helper bound `current_title` twice
Correct fix: delegate with named arguments matching the mature signature.

### ERR-49-051 — Production Hero referenced internal imported-catalog media
Correct fix: public Hero uses Product-owned gallery/main media or safe remote fallback; never widen public routing to imported working-media.

### ERR-49-052 — Product Save/AI rebuilt the entire Products gallery and thumbnails
**Date:** 2026-08-26  
**Environment:** Windows Catalog Center with a large Product catalog.

**Symptoms:** pressing AI or editing a Product visibly refreshed the Products page; repeated actions became expensive with many cards/images.

**Root Cause:** mature `ProductStudio.save()` called global Product refresh/load methods even for silent Save; AI preflight reused silent Save and the Product Explorer rebuilt cards/thumbnails.

**Correct Fix:** Phase49.3I.29 defers global refresh and pages visible Products to 48 cards while retaining the full result set; Phase49.3I.31 batch refreshes once at the batch boundary.

**Prevention:** Product-scoped Save/AI must not rebuild the global Products Explorer. Batch may refresh once at completion.

### ERR-49-053 — Generic/silent Product Save could erase the canonical source URL
**Date:** 2026-08-26  
**Environment:** Windows Catalog Center Product Workspace.

**Symptom:** after pressing an apparently unrelated Product action, the saved Product source link disappeared.

**Root Cause:** mature `ProductStudio.save()` calculated the canonical link only as `source_url.get().strip() or spec_source_url.get().strip()`. When both mirrored UI controls were temporarily blank, generic/silent Save wrote an empty `source_url`, recomputed `normalized_url` and regenerated fingerprint from empty identity. Silent Save is reused by close, refetch, AI preflight, publish and layered Workspace actions.

**Important previous condition:** this was not a crawler/OpenRouter/AvalAI deletion. The destructive write happened at the common Save boundary.

**Correct Fix — Phase49.3I.32:**
- final Workspace Save wrapper after all older layers,
- explicit non-empty link edits remain valid,
- transient dual-blank UI state preserves an already stored DB source URL,
- resolved canonical URL is fed back into both controls before mature Save,
- post-save invariant restores `source_url`, `normalized_url` and fingerprint if any legacy layer still clears them,
- already damaged Products recover only an exact previously stored HTTP/HTTPS URL: `product_history` first, matching `discovered_urls(source_code, external_id)` second,
- recovery is local-only, uses no network and never guesses/reconstructs a URL,
- recovery is recorded in Product history/diagnostics.

**Verification:** targeted CI run `32996526852` PASS and packaged Windows run `32997106056` PASS.

**Prevention:** generic Save, silent Save, AI, close, refetch, image or publish-related flows are never destructive unlink operations. Clearing a canonical source URL requires a future explicit separately confirmed unlink action.

### ERR-49-054 — First Catalog Center 8.8.2 Windows release gate retained stale `8.8.1` test literal
**Date:** 2026-08-26  
**Environment:** GitHub Actions `Catalog Center Windows Portable Release`, run `32996526842`.

**Symptom:** Windows compile passed and all new Phase49.3I.32 source-link tests passed, but the regression stage failed after 112 tests with one failure: `Epic49OperatorUIContractTests.test_current_release_and_resilient_staged_exe_build_are_enabled` asserted `APP_VERSION == "8.8.1"` while runtime version was correctly `8.8.2`. Launcher/build/artifact steps were skipped because the gate stopped correctly.

**Root Cause:** a historical UI contract test hard-coded the previous release version instead of checking atomic release identity. The application/launcher/manifest/config had already moved to 8.8.2.

**Failed Attempt:** do not rerun `32996526842` unchanged; the failing condition was deterministic and unrelated to the source-link runtime fix.

**Correct Fix:** replace the stale literal with `APP_VERSION == PACKAGE_MANIFEST["version"]`; the dedicated launcher/config/version consistency test continues to verify the rest of the atomic release identity.

**Verification:** Windows rerun `32997106056` PASS on `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`: full regression, launcher composition, source-link invariant, one-file PyInstaller build/self-verify, release manifest/SHA256 and artifact upload all PASS. Public Release publication was intentionally skipped pending owner QA.

**Prevention:** release tests must compare canonical identity sources, not freeze a previous version literal. Version bumps are atomic across runtime, launcher, manifest, config and tests.


### ERR-49-055 — Generated portable release output made the Local gate block its own next run
**Date:** 2026-08-27  
**Environment:** canonical Windows checkout `D:\projects\3DPrintHub`.

**Symptom:** after a successful `-BuildExe` run, `catalog_center/release/` appeared as an untracked path. The next Phase49.3I.31-32 gate stopped at `WORKTREE DIRTY` before reaching `-LaunchApp`, so the new head was never actually launched.

**Root Cause:** `build_portable_exe.py` intentionally writes versioned EXE/manifest/SHA files under `catalog_center/release/<version>/`, but `.gitignore` ignored `build/` and `dist/` without ignoring the generated `catalog_center/release/` output. The gate correctly rejects real source dirt, but could not distinguish its own generated release output.

**Failed Attempt / Important distinction:** do not treat this log as an application startup crash. In the reported run the gate exited before the launcher step. Do not reset/stash/delete the generated EXE as a cleanup shortcut.

**Correct Fix:** add `/catalog_center/release/` to the repository `.gitignore` and regression-test that the generated release path stays excluded from Git status. Existing release files are preserved locally; no source/database/Production state is removed.

**Verification:** dedicated regression added in `catalog_center/tests/test_epic49_operator_workflow.py`; Windows CI run `33042158052` is the verification gate for the fix.

**Prevention:** any deterministic build/release output created inside the working tree must be explicitly ignored (or written outside the repository) before a clean-worktree gate depends on `git status`.


## RESOLVED PHASE50 / RELEASE INCIDENTS

### ERR-50-001 — Phase50 Admin CI used non-canonical Django environment names
Use `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`.

### ERR-50-002 — Dynamic ModelAdmin URL patch unstable at final URL boundary
Use explicit project-level routes wrapped by `admin.site.admin_view`.

### ERR-50-003 — Phase50/Catalog release identity mismatch class
Version identity is atomic across app version, launcher, manifest, config and tests; do not keep stale literal expectations.

### ERR-50-004 — Frozen portable verification assumed launcher source file
Frozen verification tests import/runtime contracts, not physical `.py` presence.

### ERR-50-005 — Admin media patch replaced mature list contract
Extend final mature ModelAdmin composition; preserve dependent list/edit/link invariants.

### ERR-50-006 — Unified Product Admin regression assumed stale `seo_status`
Correct fix: preserve mature Product list and assert current boundary-owned invariants. CI run `32941662288` PASS.

### ERR-50-007 — Production `git fetch --prune origin` left active branch remote-tracking ref stale
**Date:** 2026-08-26  
**Environment:** `/home/sfkilvrs/3dprinthub`.  
**Root Cause:** host `remote.origin.fetch` tracked only `+refs/tags/v0.33.0:refs/tags/v0.33.0`; normal fetch did not advance branch refs.  
**Correct Fix:** verify `git ls-remote`, explicitly fetch active branch to `FETCH_HEAD`, verify exact SHA/ancestry, ff-only merge.  
**Prevention:** never trust `origin/<branch>` on this host without checking refspec/upstream.

### ERR-50-008 — Legacy permanent Django filter column crushed modern Admin changelists
Keep native filter semantics but move node into an on-demand Velzon drawer; Product Admin CI `32955310832` PASS.

### ERR-50-009 — Velzon absolute footer and document-level active-menu scroll caused refresh flash/page jump
Correct fix: normal-flow footer, stable flex shell, 290px sidebar, internal sidebar/SimpleBar scrolling only. Admin CI `32958276378` PASS; deployed at `c283864290f9c989a9fcdf24ee8eef519560e917`.

### ERR-50-010 — cPanel Bash process substitution failed because `/dev/fd` was unavailable
Use Production Python or portable temp-file/pipeline enumeration; do not depend on `< <(...)` on this Host.

### ERR-50-011 — Variant API verifier executed JSON as Python source
Invoke `python - <json-path> ...` and parse data with `json.load`; JSON payloads are arguments/data, never executable source.

### ERR-50-012 — Profile Variant API treated `price_breakdown` callable as a dict
**Date:** 2026-08-27  
**Environment:** Phase50 Profile Matrix CI.

**Symptom:** `/store/api/variant-commerce-options/` raised `AttributeError: 'function' object has no attribute 'get'` when the Profile Matrix test requested the selected Variant price.

**Root Cause:** `ProductVariant.price_breakdown` is the mature callable pricing contract. The new API serialization boundary read the method object with `getattr(...)` but did not execute it before using `.get("unit_price")`.

**Failed condition:** do not rerun the failing Profile Matrix CI unchanged; the failure is deterministic at the API boundary.

**Correct Fix:** resolve `price_contract = variant.price_breakdown`, execute it when callable, then serialize the returned pricing dict. This preserves the canonical Phase50 pricing policy wrapper and avoids duplicating price logic in the endpoint.

**Verification:** Profile Matrix/Checkout CI run `33051311828` PASS; profile fixed-price API regression returns the expected Variant price.

**Prevention:** API serializers must execute mature no-argument domain contracts before reading their returned mapping; do not treat bound methods as data.

### ERR-50-013 — Saved-address checkout was rejected by the new shipping policy wrapper
**Date:** 2026-08-27  
**Environment:** Phase50 Checkout regression.

**Symptom:** checkout using a valid saved address returned HTTP 200 with form errors instead of the expected 302 success. Two immutable-checkout tests failed.

**Root Cause:** mature `CheckoutOperationsForm.clean()` intentionally returns early when `saved_address` is selected. The Phase50 commerce wrapper then validated `cleaned["address"]` / `postal_code` / location fields, which are empty in that mature saved-address flow.

**Correct Fix:** when `saved_address` exists, shipping scope/address/postal rules resolve province/county/city/address/postal code from that persisted address object; only new-address checkout uses raw cleaned form fields.

**Verification:** CI run `33051311828` PASS, including both immutable checkout tests and saved-address checkout redirect.

**Prevention:** wrappers around mature forms must honor the mature form's alternate data source/early-return semantics instead of assuming every field is populated in `cleaned_data`.

### ERR-50-014 — Downstream Profile state hid valid size/weight choices and could show another size's price
**Date:** 2026-08-27  
**Environment:** Storefront dependent Profile selector.

**Risk/Symptom:** after a customer changed size, the currently selected downstream weight/build could constrain the option list for an upstream dimension. Price badges for a weight were also calculated from every Product Variant with that weight, so a 150 g price from size 20 could appear while viewing size 30.

**Root Cause:** option rendering used the complete current state for every dimension and calculated option-price pools globally by dimension value.

**Correct Fix:** each dimension now filters only by selections that occur **before** it in the configured Profile hierarchy. Clicking an upstream option clears downstream state before choosing a valid canonical Variant. Weight/Profile price badges are computed from the upstream-scoped candidate pool.

**Verification:** dedicated Node behavior gate `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS` plus full Store run `33051311828` PASS. The gate proves size 30 exposes all of its 150/200/300 g rows and uses the size-30 price for 150 g.

**Prevention:** dependent option matrices are prefix trees: later selections never determine the availability or price of earlier-level options.

### ERR-50-015 — Windows portable workflow did not watch mature Product studio publish-gate files
**Date:** 2026-08-27  
**Environment:** GitHub Actions Windows portable release.

**Risk:** Profile Matrix publish-readiness fixes in `catalog_center/app/product_studio.py` and `catalog_center/app/epic49_product_studio.py` could pass targeted CI without automatically producing a fresh immutable Windows artifact.

**Root Cause:** `Catalog Center Windows Portable Release` path filters watched the newer 3I modules but omitted those two mature Product studio files even though the packaged application imports them.

**Correct Fix:** add both mature Product studio files to the Windows release workflow trigger.

**Verification:** Windows portable run `33051114515` PASS on `b3280dd67cd7772f337f6792036ea92d3f252747`; artifact ID `9637671099`; EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`.

**Prevention:** immutable release workflows must watch every source boundary that materially changes the packaged runtime, including mature wrapped files.


### ERR-50-016 — `support_weight_grams` runtime metadata drifted from migration 0039
**Date:** 2026-08-27  
**Environment:** GitHub Actions `Phase50 Variant2 + Profile Matrix CI`, failed run `33059803005`.

**Symptom:** `python manage.py makemigrations --check --dry-run` proposed an unapproved `0040_alter_productvariant_support_weight_grams.py`.

**Root Cause:** the mature `phase49_3f_pricing` runtime contributes `ProductVariant.support_weight_grams` before the newer Phase50 filament runtime sees the model. The field shape matched migration 0039 except its `verbose_name` was `وزن ساپورت (گرم)`, while migration 0039 declared `وزن ساپورت مصرفی`. Django therefore detected model-state metadata drift.

**Failed condition:** the failing migration gate was not rerun unchanged and no fake 0040 migration was accepted.

**Correct Fix:** align the mature runtime-contributed field metadata exactly with migration `0039_phase50_filament_offer_pricing`; keep one schema field and one migration authority.

**Verification:** commit `d519a360e65b79db4b62af206b95f63c3539bc12`; Phase50 run `33059883188` PASS, including no migration drift, migration through 0039 and 16 Store/Profile/Checkout tests.

**Prevention:** when a later formal migration owns a field that an older runtime layer may dynamically contribute first, field metadata (`type/max_digits/decimal_places/default/null/blank/verbose_name`) must remain identical. Always gate with `makemigrations --check --dry-run` before Production.

### ERR-49-056 — Catalog Center 8.9.1 Windows gate retained stale quick-price and package-version expectations
**Date:** 2026-08-27  
**Environment:** GitHub Actions `Catalog Center Windows Portable Release`, failed run `33059799929`.

**Symptoms:**
- `test_phase49_3i33_operator_workflow` still required the removed `قیمت قطعی فروش (تومان)` quick-page authority,
- `test_v854_launcher` detected `config.example.json.package_version = 8.9.0` while Manifest/App/Launcher were already 8.9.1.

**Root Cause:** the 3I.35 redesign intentionally moved price/weight/Profile authority out of the quick page, but the older UI contract test still asserted the retired control. The release bump also updated App/Manifest/Launcher before the example config version.

**Failed condition:** the failing Windows command was not rerun unchanged.

**Correct Fix:** update the test to assert the new invariant — quick-page fixed-price authority is absent and price/weight/Profile live only in the order/pricing/options stage — and align `config.example.json.package_version` to 8.9.1.

**Verification:** exact runtime snapshot `2622818d898e19b745c61ff653b80c03d22288f1`; Windows run `33060047878` PASS through regression, launcher, source URL guard, one-file EXE, browser smoke, self verify and artifact SHA.

**Prevention:** a Catalog version bump is an atomic contract across `app/version.py`, `launch.py`, `PACKAGE_MANIFEST.json`, `config.example.json` and launcher tests. Contract tests must represent current business ownership, not require intentionally retired UI controls.


### ERR-49-057 — PowerShell multiline `python -c` DB probe stripped Python quotes in Local owner gate
**Date:** 2026-08-27  
**Environment:** canonical Windows checkout `D:\projects\3DPrintHub`, owner Local QA wrapper at branch HEAD `35ab63105f30fdca42518d5273a424a3200977e3`.

**Symptom:** Local owner gate passed repository verification, live GitHub verification and Catalog SQLite backup, then failed before any new migration with:
`SyntaxError: unterminated string literal` while executing the embedded Python DB detector. The received Python text had lost quote characters around mapping keys/strings (for example `db.get(ENGINE)` instead of `db.get("ENGINE")`).

**Root Cause:** a PowerShell expandable multiline here-string was passed directly as a native `python -c` argument. Native argument quoting/serialization changed the embedded Python quoting. This is a wrapper/command transport defect, not a Django/database/schema failure.

**Failed condition:** do not repeat the same multiline `& $Py -c @"..."@` probe unchanged.

**Correct Fix:** feed a single-quoted PowerShell here-string to Python standard input (`... | & $Py -`) or use a simple one-line command whose quoting is unambiguous. Continue from the failed DB-verification boundary after re-verifying exact branch/head/clean worktree. Create a fresh backup of the effective Local Django SQLite file before applying any pending migration.

**Safety:** the failed owner run stopped before its migration stage, therefore that failed run did not apply `0039`. An earlier Local run at `ca9cc116...` had already applied `0034..0038` and passed 15 Store/Profile/Checkout tests.

**Prevention:** Windows operational runbooks must not pass nontrivial multiline Python source as an expandable native `-c` argument. Prefer stdin with a single-quoted here-string for read-only probes.


### ERR-49-058 — Local gate `CATALOG_CENTER_LAUNCHED=YES` did not prove visible owner UI launch
**Date:** 2026-08-27  
**Environment:** Windows owner Local QA, Catalog Center 8.9.1.

**Symptom:** automated gate ended with `CATALOG_CENTER_LAUNCHED=YES`, but the owner did not see the new UI and could not perform visual acceptance.

**Root Cause:** `RUN_PHASE49_3I31_SMART_AI_GATE.ps1 -LaunchApp` uses PowerShell `Start-Process`, which starts Catalog Center as a detached process and immediately prints the launch marker. The marker proves the process-start command was issued; it does not prove the window was visible/focused or that owner visual QA occurred.

**Correct Fix:** for owner visual QA, launch the exact GitHub-synced source in the foreground with the canonical venv Python and `launch.py --debug`. Keep the terminal attached so startup/runtime errors remain visible. The 3I.35 UI is inside the Product workspace/order-pricing-options surface, not a replacement for the home screen.

**Prevention:** do not use `CATALOG_CENTER_LAUNCHED=YES` as evidence of visual acceptance. Automated launch verification and owner-visible UI QA are separate gates.


### ERR-49-059 — 3I.35 AI resilience panel mixed `grid` into the pack-managed Settings parent
**Date:** 2026-08-27  
**Environment:** owner foreground Local launch of Catalog Center 8.9.1 on `D:\projects\3DPrintHub`.

**Symptom:** foreground `launch.py --debug` reached real application initialization and then aborted before any window became usable with:
`_tkinter.TclError: cannot use geometry manager grid inside ...!frame10 which already has slaves managed by pack`.

**Root Cause:** UX87 `settings_tab` is a pack-managed parent. Phase49.3I.35 created the new “پایداری AI گروهی — تنظیمات مادر” LabelFrame directly under `settings_tab` but called `panel.grid(...)`. This violated the existing `ERR-49-001` rule: one geometry manager per parent.

**Correct Fix:** keep the outer 3I.35 AI settings panel on the parent’s existing manager with `panel.pack(fill="x", padx=8, pady=8)`. Internal controls may continue using `grid` because they are children of the panel, not siblings in `settings_tab`.

**Regression:** `test_ai_resilience_settings_respects_pack_managed_settings_tab` asserts the outer panel uses `pack` and that the old direct `panel.grid(row=50,...)` contract does not return.

**Verification:** targeted Phase49.3I.31–35 run `33066472847` PASS; Single Active AI run on the final release head PASS; Windows one-file run `33066468014` PASS on runtime `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`, including compile, Phase49 regression, launcher composition, source URL guard, one-file build/self-verify, manifest/SHA and artifact upload.

**Release:** Catalog Center `8.9.2` / build `2026.08.27.4`; artifact `9643957471`; EXE SHA256 `fac29fc610215cfc4115fcdb4c005fc69f99c3e6569b44c501d63ec82d6ba257`.

**Prevention:** any additive UI layer must inspect the final visible parent’s existing geometry manager before mounting widgets. A launch marker or `--verify-only` does not replace foreground owner startup QA.


### ERR-49-060 — Profile Matrix selection callback called an unbound short-name helper
**Date:** 2026-08-27  
**Environment:** owner foreground Local QA of Catalog Center 8.9.2 after `ERR-49-059` startup geometry fix.

**Symptom:** Catalog Center 8.9.2 itself started successfully, but opening real Products 305 and 303 emitted repeated Tk callback failures and prevented the Profile/Order workspace from becoming usable:
`AttributeError: 'ProductWorkspace' object has no attribute '_profile_by_key'`.

**Evidence:** owner diagnostic generated at local 14:54:17 showed 8.9.2/build 2026.08.27.4 startup success, Product Workspace open events for 305 and 303, then four repeated callback failures at 14:53:54 and 14:54:00. The current-session hidden-model-scan warnings are expected safeguards, not this failure.

**Root Cause:** `phase49_3i34_profile_matrix.install_workspace()` defined local helper `_profile_by_key` but installed it on the wrapped class only as `_phase49_3i34_profile_by_key`. `_load_selected()` incorrectly called `self._profile_by_key(key)`, a name never installed on `ProductWorkspace`. Other Profile Matrix call sites already used the correct namespaced method.

**Correct Fix:** change the selected-profile lookup to `self._phase49_3i34_profile_by_key(key)`. No schema, Product data, Store migration or Host behavior changed.

**Regression:** `test_selected_profile_loader_uses_installed_namespaced_lookup` installs the real 3I.34 wrapper on a minimal class and executes the selected-profile loader without Tk; the old call raises and the corrected namespaced binding succeeds.

**Verification:** targeted Phase49.3I.31–35 run `33067612565` PASS; final-head Single Active AI run `33067618639` PASS; Windows one-file run `33067618679` PASS on runtime `9637829a255a1d09800bc062c2f049cf5d92b585`, including full Phase49 regression, launcher composition, source URL guard, one-file build/self-verify, manifest/SHA and artifact upload.

**Release:** Catalog Center `8.9.3` / build `2026.08.27.5`; artifact `9644438652`; EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`; artifact ZIP digest `sha256:216b62072fd95a0a4d292b28ce99605fd60f3e4d9622d06987d6fe5b434e6141`.

**Rollback anchor:** `backup/pre-err49-060-profile-matrix-bind-fix-20260827` → `6f9334705c74a65d47473580944d79d61d501293`.

**Prevention:** nested UI helper methods must be called through the exact namespaced attribute actually installed on the final wrapped class. Static presence tests are insufficient for wrapped callback binding; execute callback contracts on a minimal installed class.

### ERR-49-061 — Commerce lock protected ledger JSON but missed legacy plural Profile transport
**Date:** 2026-08-27  
**Environment:** Phase49.3I.36/3I.37 Catalog Center regression gate.

**Symptom:** the finalized-Commerce regression showed `sales_profile_ledger_json` stayed protected while the mature legacy transport `sales_profiles_json` could still be overwritten to `[]` after the Commerce stage was locked. This matched the owner-visible risk that a later AI/Save path could make previously registered Profiles disappear.

**Root Cause:** the stage ownership mapper recognized fields beginning with `sales_profile_`, but the older transport is plural `sales_profiles_json`; that key did not match the prefix and therefore escaped the Commerce write lock.

**Failed condition:** do not weaken the lock regression or treat only the newest ledger field as authoritative persistence protection. Both mature transports remain part of the current synchronization path.

**Correct Fix:** classify both `sales_profile_` and `sales_profiles_` prefixes as Commerce-owned. The final `Database.update_product()` guard now blocks both transports while Stage 2 is finalized.

**Regression:** `test_stage_field_ownership_keeps_profile_and_slider_separate` asserts both transports map to Commerce, and `test_finalized_commerce_protects_registered_profile_ledger` proves both remain unchanged under the lock.

**Verification:** Phase49.3I.31–37 run `33074245603` PASS with 77 tests; Single Active AI run `33074245489` PASS; Windows Portable run `33074245604` PASS on runtime `8d5e58a839c89eedbe258d9236889834fc02d9a9`.

**Prevention:** write-scope/lock mappings must cover every mature alias/transport that can persist the same business object, not only the newest authoritative field name.

### ERR-49-062 — Rejected/blocked Direct Link identity was checked only after acquisition
**Date:** 2026-08-27  
**Environment:** Catalog Center Direct Link import.

**Symptom/Risk:** a Product that was already blocked/rejected could still enter `extract_direct_link()` and reopen browser/HTTP/image acquisition. The later DB upsert guard could prevent the Product record from becoming active, but local images/files might already have been downloaded again.

**Root Cause:** terminal Product identity was enforced at the persistence boundary, not at the network/binary acquisition boundary.

**Correct Fix:** resolve source code + external ID, query the permanent crawl/Product tombstone with `terminal_identity_state()`, and return before `extract_direct_link()` for terminal states. Successful Direct Link acquisition records `collected` in the mature discovery ledger.

**Regression:** 3I.38 static execution-order regression asserts the terminal identity check occurs before the Direct Link extractor; reject/purge integration proves a rejected identity remains terminal.

**Verification:** Phase49.3I.31–38 run `33077213590` PASS with 84 tests; Single Active AI `33077239617` PASS; Windows Portable `33077239660` PASS on runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`.

**Prevention:** any permanent skip/block/reject decision must be evaluated before browser, HTTP, image or file acquisition—not only before DB persistence.

### ERR-49-063 — Category/site crawl repeatedly exposed the same fixed first discovery window
**Date:** 2026-08-27  
**Environment:** Catalog Center category/site crawl.

**Symptom/Risk:** `category/site_crawl` used one discovery pass with a fixed `scroll_rounds=8`. Although `discovered_urls` correctly rejected already-known Product identities, re-running the same Listing could repeatedly rediscover the first visible set instead of moving deeper to new Products.

**Root Cause:** deduplication was durable but Listing traversal depth was not. The mature discoverer had no persisted continuation state.

**Correct Fix:** keep `discover_classic()` unchanged and add a separate `crawl_listing_state` cursor. Same-Listing runs progress 8 → 16 → 24 … up to 96 scroll rounds. Every discovered identity still passes through the existing `add_discovered()` ledger, and four consecutive deeper no-growth attempts stop the current run.

**Regression:** the 3I.38 tests prove 100 previously collected IDs are skipped while 101–200 become the next 100 pending items, and prove the continuation cursor advances across runs.

**Verification:** Phase49.3I.31–38 run `33077213590` PASS; Windows Portable `33077239660` PASS.

**Prevention:** keep Product identity dedupe and Listing traversal progress as separate durable concerns; never replace a healthy parser/downloader just to continue past previously seen results.


### ERR-49-064 — 3I.35 legacy material actions aborted ProductWorkspace before 3I.39/3I.40 UI
**Date:** 2026-08-29  
**Environment:** owner foreground Local QA, Catalog Center 8.9.8 / build 2026.08.29.2, canonical checkout `D:\\projects\\3DPrintHub`.

**Symptom:** the owner opened a real Product Workspace and still saw the older Stage-2/SEO surface even though launcher verification printed every 3I.39/3I.40 feature marker. Foreground diagnostics then raised:
`TclError: cannot use geometry manager pack inside ...!labelframe which already has slaves managed by grid`.

**Root Cause:** `phase49_material_color_picker` had already replaced the mature material/color Listbox surface with a grid-managed checkbox picker. During the later 3I.35 wrapper, `build_material_actions()` still treated the obsolete `material_color_list` parent as an active pack-managed host and tried to mount another Frame with `pack`. ProductWorkspace construction stopped inside the 3I.35 constructor, so the already-created older widgets remained visible while 3I.39 Professional Commerce and 3I.40 Commerce Precision never reached their UI-build steps.

**Failed condition:** do not interpret launcher feature markers or the 8.9.8 title as proof that the final wrapped ProductWorkspace constructor completed. A callback exception after partial construction can leave an older surface visible.

**Correct Fix:** when the modern checkbox picker is installed (`_epic49_materials_box` exists), 3I.35 now skips mounting the obsolete Listbox action row entirely. The 3I.35 business methods/data remain intact, and 3I.39 remains the final visible Stage-2 authority.

**Regression:** `test_operator_ledger_skips_obsolete_listbox_actions_when_modern_picker_is_installed` installs the real 3I.35 wrapper on a minimal workspace and proves no `ttk.Frame` is created for the obsolete action row when the modern picker marker exists.

**Git hotfix:** source fix `aa37dcf916dfab71409738f7087a171daffe4a0a`; regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`.

**Rollback anchor:** `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`.

**Verification status:** GitHub source/regression update complete. Owner Local ff-only pull + targeted tests + foreground ProductWorkspace retest are still required before this incident is marked fully verified. Production untouched.

**Prevention:** every additive wrapper must inspect whether the surface it is extending is still the active visible generation. Never mount legacy controls into a parent that a newer layer has already replaced; and do not use feature-marker prints as a substitute for successful final constructor completion.


### ERR-49-065 — AI filled SEO fields but stale readiness/UI still showed them as missing
**Date:** 2026-08-29  
**Environment:** owner foreground Local QA after ERR-49-064, Catalog Center 8.9.8 / Phase49.3I.40.

**Symptom:** the seven-stage AI completed and persisted Persian/SEO fields, but the Product Workspace still showed red/missing SEO items and stale stage icons. The owner correctly observed that the Product appeared to need a post-AI refresh before publish readiness reflected the saved fields.

**Root Cause:** the 3I.39 completion worker queued a generic `reload()` and one lock refresh after the AI loop. Multiple mature wrappers keep cached readiness/help state; the older guided-wizard painter could repaint its cached `ready/missing` state after the final 3I.40 data-readiness renderer. Persisted SQLite values were therefore newer than some visible readiness widgets.

**Correct Fix:** add one explicit post-AI reconciliation boundary that rehydrates the Product row from SQLite, reloads the workspace, refreshes stage locks and the guided wizard, and deliberately leaves the final `_phase49_refresh_readiness` call as the last painter. Run the same reconciliation again after a short UI-settle delay. Apply this to both whole-product and single-stage repair completion paths.

**Scope:** no Provider/model/source semantics, no AI field ownership, no Commerce/Profile/Offer mutation, no auto-finalization, no migration/schema, no Host or Production change.

**Git hotfix:** source `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4`; regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`.

**Regression:** `test_post_ai_refresh_rehydrates_db_and_leaves_final_readiness_as_last_painter` verifies DB rehydration and that final readiness is the last UI painter after reload/lock/wizard refresh.

**Rollback anchor:** `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`.

**Verification status:** Owner Local pulled `c679c66d8c6554ff14e5705b7eb3aada24495990`; the 3I.39/3I.40 targeted set passed 12/12 and foreground 8.9.8 launched correctly. The visible bug nevertheless persisted. The repaint fix is retained, but it was insufficient because a deeper checker/stage-ownership mismatch remained; see ERR-49-066. Production untouched.

**Prevention:** after background AI writes, do not assume one generic reload synchronizes every wrapped readiness surface. Rehydrate from persisted state and define one final painter for the visible readiness contract; then verify the checker and fixer use the same stage/field semantics.


### ERR-49-066 — Readiness checker, stage ownership and AI repair disagreed
**Date:** 2026-08-29  
**Environment:** owner foreground Local QA on `c679c66d8c6554ff14e5705b7eb3aada24495990`, Catalog Center 8.9.8 / Phase49.3I.40.

**Owner evidence:** Local fast-forward and 12 targeted tests passed, then the real Product 63 run proved the remaining defect. The first visible full-AI action still executed the older 3I.31 path and persisted title/content/SEO/image fields. The later 3I.39 readiness loop reported `7` data defects / `5` AI-fixable defects, scoped only Stage 4, accepted a fallback AvalAI response, then reported `0` defects fixed and stalled with the same `5` AI-fixable defects.

**Root Causes:**
1. `title_fa` was checked in both Quick and Content even though final field ownership assigns it to Quick.
2. image Alt was checked in Content even though final field ownership assigns it to Images.
3. the persisted Persian readiness checker rejected every Latin character, while the title/description AI path legitimately permits the true source identity (for example `Flexi Gecko`) beside Persian text.
4. non-empty but invalid keyword/tag/hashtag lists were reported by readiness but `_field_needs_fill()` treated them as complete because it only used blank-value repair logic.
5. the guided wizard painted/navigation-gated on `ready` (operator-finalized) instead of `data_ready` (actual data completeness), so Stage 1 could remain X/★ even with all required values present.
6. some visible mature AI buttons still resolved to the older 3I.31/3E execution path rather than the final 3I.39 checker/repair authority.

**Correct Fix:**
- one authoritative readiness owner per field: title → Quick, Alt → Images, SEO/content fields → Content;
- persisted title/description may contain only Latin tokens that are actual tokens of `source_title`; SEO title/description and SEO keyword/tag/hashtag lists remain Persian-only;
- `_field_needs_fill()` now uses the same semantic checks as readiness, including non-empty invalid lists;
- guided-wizard red stars, Next gating and stage icons use `data_ready/missing_data` when available; operator `ثبت` remains a separate finalization lock;
- final 3I.39 installation rebinds mature full-AI/link/current-stage entry points to the same seven-stage repair engine.

**Touched surfaces:** `phase49_readiness_wizard.py`, `phase49_3c_persian_content.py`, `phase49_3b_guided_wizard.py`, `phase49_3i37_seven_stage_ai.py`, `phase49_3i39_completion_loop.py`, plus focused regressions.

**Must not touch:** Product Offer/Profile/pricing ownership, crawler/parser/download, source URL guard, Provider secrets/configuration, image binaries, Django schema/migrations, Host and Production.

**Git changes:**
- checker/source-identity alignment `3b4ad0c8741f794ee5c338e5ddba8971bf9c3487`,
- single field/stage ownership `2fff3f7edfecb2d6a0acc6c3d52c14817b177e82`,
- Persian defect ownership `046191ac562ecce878dfab263f4f6255d5f12bcf`,
- data-ready guided wizard `11dfefdbb02a6281c1b6a6721cbf254785e2e216`,
- checker/fixer agreement `39fcd2f9e335a57d76079f6f18ebaad3ac406f97`,
- final AI entrypoint authority `b9ef5f1f6d887520c1613f09cbcf947fc1058e12`,
- regressions `5a14318e52244fd0b9de8de15daafe03e204c5fb`, `b5f1a9d50435c04fc382e4783355f23e64987823`, `7c047c834163235455e24a58eb43c134b4ccecc0`, `8bb6e1f7b30039f709b627d3a5aaa7691ec004c3`, `7874dd2d63a8a8e51bd5d9f72668332e9d7c7861`.

**Rollback anchor:** `backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`.

**Verification status:** GitHub source/regressions updated. No GitHub Actions run is attached yet to the current code head; owner Local targeted regression + foreground Product 63 retest is required before acceptance. Production untouched.

**Prevention:** a readiness defect must map to exactly one owning Stage and to at least one executable repair path when labeled AI-fixable. UI completion indicators must distinguish persisted data completeness from operator finalization.


### ERR-49-067 — Locked-stage regression fixture violated the new Persian SEO contract
**Date:** 2026-08-29  
**Environment:** owner Local ERR-49-066 focused gate on `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`.

**Symptom:** compile passed, then the 43-test focused suite stopped with exactly one error in `test_locked_quick_and_content_are_not_rewritten_by_orchestrator`. The exception occurred before the lock assertion path:
`RuntimeError: خروجی AI برای seo_description_fa باید SEO فارسی باشد و متن لاتین نداشته باشد.`

**Root Cause:** ERR-49-066 intentionally strengthened the production SEO contract so `seo_title_fa` and `seo_description_fa` cannot contain Latin text. The older regression fixture still mocked its generated SEO description as `توضیح فارسی AI درباره ...`. The literal Latin token `AI` made the mock payload invalid, so validation correctly rejected it before the test could reach the behavior it was actually intended to verify: locked Quick/Content stages are not rewritten.

**Correct Fix:** keep the stricter runtime contract unchanged and repair only the stale test fixture. Replace the mock Latin `AI` wording with fully Persian generated-content placeholders. This preserves the purpose of the regression and avoids weakening real SEO validation merely to satisfy a stale fixture.

**Git:** test-fixture correction `38cb415bc12d7ec08943809fd14f3478b3ddac1b`.

**Rollback anchor:** `backup/pre-err49-067-seven-stage-test-fixture-20260829` → `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`.

**Verification status:** owner Local evidence before the correction: repository/branch/head verified, Catalog SQLite backup created with SHA256 `AE475E39040B8BF8F7BEF7B13D3176F2B83BBA956E2121D53CC2F5CC087F185F`, compile PASS, 43 focused tests ran with 1 deterministic fixture error, foreground launch correctly did not run. Owner must ff-only pull the corrected head and rerun the same focused gate; do not rerun the failed head unchanged. Production untouched.

**Superseded detail:** the fixture-only correction itself remains valid, but the interim assumption that SEO title/description must reject every Latin token was too strict for real product identity. Owner runtime evidence immediately after this gate showed legitimate source identity such as `Flexi Gecko` being rejected. ERR-49-068 replaces that rule with: Persian SEO may preserve exact Latin tokens from `source_title`; unrelated Latin remains invalid.

**Prevention:** regression fixtures that feed production validators must themselves satisfy the current production contract unless the test explicitly verifies rejection. A lock/immutability test must use a valid AI payload so validation does not mask the behavior under test.


### ERR-49-068 — Windows stage confirmation deadlock + stale Tk callbacks + AI fallback identity mismatch
**Date:** 2026-08-29  
**Environment:** owner foreground Windows QA on exact Local head `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`, Catalog Center 8.9.8 / build 2026.08.29.2 / Product 63.

**Owner evidence:** the corrected ERR-49-067 gate passed the previously failing test and then all 43 focused tests. The canonical source launched successfully. In the real Product Workspace, Stage 1 fields could be visibly complete or manually edited but the Stage stayed unconfirmed/red, the expected bottom confirmation control was not available in the visible workflow, and the operator could not naturally advance. The same runtime trace also showed:
- initial readiness `6` data defects / `4` AI-fixable,
- OpenRouter returned no output text on repeated attempts,
- AvalAI returned structured output but legitimate source identity in SEO was rejected, then one request timed out,
- an OpenRouter-shaped key/model was later attempted under the OpenAI fallback and received HTTP 401,
- the failure UI then raised `cannot access free variable 'exc' where it is not associated with a value in enclosing scope`,
- a later explicit Product save persisted many fields successfully, proving the database write path itself was alive.

**Historical comparison:** the original 3B guided wizard commit `eb865e78c70b862f51e6918dee074c8bb9c0536f` had a persistent footer Next action and visible AI helper. 3I.36 commit `8d6e9ca1bee40da3ffbd57ec328ef77de451c781` introduced separate stage finalization/locking and moved `ثبت` into a seven-row rail panel. The mature 3B Next path still evaluated readiness before its later `save(silent=True)`; once readiness depended on persisted stage data/finalization, manual widget edits could never pass the pre-save gate. In current layout the rail finalization panel was not a reliable visible operator control, producing a practical deadlock.

**Root Causes:**
1. Manual stage progression evaluated persisted readiness before persisting current UI values.
2. Stage finalization existed only in the separate 3I.36 rail panel; the fixed footer no longer provided the old obvious confirm/advance workflow.
3. Older Tk Buttons captured bound callback objects when they were created. Later 3I.39 class alias reassignment did not change those already-created widget commands; the rebind scan covered only Content, not the whole Workspace.
4. SEO validation rejected every Latin token instead of allowing the exact real source identity tokens already present in `source_title`.
5. fallback candidate construction could reuse a key/model belonging to another Provider. The observed OpenAI attempt used an OpenRouter-shaped key and an OpenRouter/Nvidia model.
6. a deferred lambda closed over `exc` from an `except` block; Python clears that exception binding after the block, causing the secondary UI error.

**Correct Fix:**
- restore a persistent visible footer action `✅ تأیید و مرحله بعد →` that calls the 3I.36 stage-specific persist/finalize method first and advances only after success;
- add adjacent visible `✨ پرکردن ناقص‌ها با AI` and `✏ اصلاح مرحله` actions;
- wrap the mature Wizard refresh so later refreshes cannot silently replace the fixed confirm command/text with the old read-before-save Next behavior;
- rebind actual already-created legacy AI buttons across the whole Workspace to the final 3I.39 engine rather than relying only on class aliases;
- allow exact Latin tokens from `source_title` in Persian title/description/SEO fields while continuing to reject unrelated Latin; keyword/tag/hashtag lists remain Persian editorial text;
- skip positively identifiable cross-provider keys and require fallback models to be saved for that exact Provider rather than inheriting the primary model;
- freeze the redacted exception text before scheduling the deferred footer callback.

**Git changes:**
- source-aware SEO readiness `7e4fbd198af0252bb83f613a984e1bf675237158`,
- source-aware AI SEO validator/repair `e0e08c668acbed3cbb084b82728994ee3e22299d`,
- visible footer confirm/AI/edit + deferred exception fix `6ece94c2c8a9431517ee08c0ffd131863e844d0c`,
- actual legacy Tk button rebind `d0514357907a96c96edc4151cc845dd08f2a1bfc`,
- footer authority retained after Wizard refresh `d461ab981b7ce490fb24c68ac8ea92c39a8046fa`,
- cross-provider key guard `0856868ea057b2cc9f0081ceeef723df4fd95702`,
- provider-specific fallback model guard `c1746545f0fb8c591f01591c91487d9c721bbcc6`,
- regressions `8d31f0dd011028c407eb609e3a58b5e03e6430ce`, `21913aa409757e1b3a9b41136d434fc498801dc0`, `ef6b2f033cd4d0aac359df0497bd8e593ed9d2bc`, `3822d407438b21a1bccd9484805fe937bf789b51`, `e184e629d3ac55a62c1f501d1ab684bc8c212701`, `dbe10616c691292e4e74358a08a9de2d43fdf333`, `4d6426f8f2a4ea01643bb763cf00a2dae3947e3f`.

**Rollback anchor:** `backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`.

**Touched surfaces:** Windows Catalog Center stage footer/navigation, 3I.39 AI button routing, Persian/source-identity readiness and repair validation, fallback candidate safety, focused tests and documentation.

**Must not touch:** Stage-2 Offer/Profile/pricing ownership, crawler/parser/download identity, Product media binaries, Django schema/migrations, Production Host, secure key values themselves.

**Verification status:** GitHub hotfix/regressions are committed. The last owner Local runtime at `0191a07...` passed 43 focused tests but predates this ERR-49-068 delta. Current hotfix requires a new Local pull, compile/regression gate and foreground Product 63 QA. Production untouched.

**Prevention:** a visible Windows workflow must have an executable persist → validate → confirm → advance path in the same viewport; do not make progress depend on an off-screen/secondary control. Tk widget commands created before later wrappers must be explicitly rebound at the final visible composition boundary. Provider fallbacks must keep key and model identities provider-specific.


### ERR-49-069 — late Wizard repaint, incomplete stage ownership UI and AvalAI fallback after 60/60 Local PASS
**Date:** 2026-08-29  
**Environment:** owner foreground Windows QA on exact Local head `3f43260db669b458a682f594b5d50eb5221b9ef3`, Catalog Center 8.9.8 / build 2026.08.29.2.

**Owner evidence:** the ERR-49-068 Local gate verified the canonical checkout, created backup `D:\projects\3dprinthub-backups\err49-068-20260829-174512\catalog-before-err49-068-qa.sqlite3` with SHA256 `5A6DB948ADACA81014DEDFA7FF117A0C4AF26364936575ACB15D21D632D4C321`, passed compile and 60/60 focused tests, then launched the exact 8.9.8 source. Real Product 63/295 QA still showed:
- the visible footer reverted to the old `مرحله بعد برای انتشار →` action after final composition,
- Stage 1 could be data-complete yet stay practically unconfirmed/not advance,
- Stage-1-owned Product type/dimensions/use-case controls were not all visible in Stage 1,
- Stage-5-owned source/license/technical controls were split across older Stage 2/7 surfaces,
- Stage-specific AI reported global defects from unrelated Stages, so a completed Stage 1 run could still claim 4 AI-fixable defects remained,
- Product 63 and Product 295 AI jobs overlapped,
- despite OpenRouter being the saved active Provider, resilient fallback still invoked AvalAI,
- OpenRouter primary model was intermittently 404/403/no-text but also produced valid 3–5k-token responses, so the correct policy is same-Provider fallback rather than changing Provider automatically.

**Root Causes:**
1. `phase49_3i26_operator_completion` scheduled an `after_idle` callback that captured the older `_phase49_3b_refresh_wizard` before 3I.39 finished installing. That late callback could repaint the footer after 3I.39 had configured it.
2. The old 3B Next handler still had a read-before-save fallback path. Rebinding the visible Button alone was therefore insufficient.
3. Canonical field ownership and visible stage composition had drifted: Quick owns `product_type/dimensions/use_case_class`, but those controls lived in the older Commerce form; Specs owns source/license/technical fields, but some controls remained elsewhere.
4. `persist_stage_from_ui()` did not persist every field declared/visible for Quick and Specs.
5. `repair_until_stable()` used global `ai_fixable_count` for stage-scoped completion, causing false retry/stall/incomplete reporting from defects outside the requested Stage.
6. AI busy state was per Workspace, allowing concurrent Product AI jobs in the same process.
7. 3I.35 resilience still treated AvalAI/Google/OpenAI as Product-AI fallback candidates even when the owner explicitly selected OpenRouter.

**Correct Fix:**
- make the base guided refresh itself call the final 3I.39 footer-sync hook, so even already-captured old callbacks finish by restoring `✅ تأیید و مرحله بعد →`;
- make legacy `_phase49_3b_go_next` delegate to final stage confirmation and, for any legacy-only fallback, persist before readiness evaluation;
- route the old title-only button through final Stage-1 AI when 3I.39 exists and freeze legacy exception text before deferred Tk callbacks;
- restore an additive Stage-1 identity panel with Product type, dimensions and use-case/class; persist all Quick-owned fields both in stage-specific finalization and normal Workspace Save;
- restore an additive Stage-5 panel for source/designer, commercial license, Persian technical summary and technical-features JSON; persist those fields before finalization and keep compatibility editors synchronized;
- make repair counts, terminal messages and 3I.40 progress scope-aware for single-stage AI while retaining global truth for whole-product AI;
- add one process/app-level Product-AI runtime guard so another Product Workspace cannot start a second Product AI job until the first finishes/cancels;
- make Product AI **OpenRouter-only**: exact saved OpenRouter model is Primary; optional fallback is only `openrouter/free` with the same OpenRouter key. AvalAI/Google/OpenAI are not Product-AI fallbacks. No model is guessed or silently changed.

**Git changes:** source changes begin at `3ea7033bfe46d892d72d96eb47cbe3e7c02b63d8` and currently extend through `136011971dea907ac777b3e66190dd27982a0c38`; focused regression updates are included in the same branch history.

**Rollback anchor:** `backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`.

**Touched surfaces:** Windows Catalog stage footer/navigation, Stage 1 and Stage 5 operator controls/persistence, stage-scoped AI completion accounting, Product-AI concurrency guard, Product-AI Provider resilience, focused tests/documentation.

**Must not touch:** Stage-2 Offer/Profile pricing authority, crawler/parser/acquisition identity, Product media binaries, secure key values, Django schema/migrations, Host or Production.

**Verification status:** owner Local evidence on the rollback head is 60/60 PASS and foreground failure reproduced. ERR-49-069 source/tests are committed on GitHub but **have not yet been pulled/tested on the owner Windows checkout**. Production remains untouched.

**Prevention:** final visible composition must be tested against deferred callbacks, not only class method aliases. Every Stage must have a single ownership table that matches visible controls, stage-specific persistence and readiness. Stage-scoped AI must judge only its Scope. Product-AI Provider policy is explicit and must not silently cross providers.



### ERR-49-070 — clean Stage-5 schema/panel gap exposed by owner Local gate
**Date:** 2026-08-29

Owner Local on `382a34fa6e876dc7098c8152c98c7cb076d508e8` passed compile and the 4 OpenRouter-only tests, then the 67-test Windows contract stopped before launch with:
- `sqlite3.OperationalError: no such column: technical_summary_fa` on a clean temporary Catalog DB;
- missing Stage-5 visible contract text. Source review confirmed `add_specs_contract_panel` and `refresh_specs_contract` were referenced/assigned but not implemented.

Root cause:
1. `technical_summary_fa` became Stage-5 authority without being added to the canonical clean Catalog schema.
2. ERR-49-069 wired Stage-5 builder names without their function bodies.
3. Stage-specific finalization needed to translate the visible Persian license label to the stored license code.

Fix:
- add `technical_summary_fa` to Catalog self-schema;
- implement `منبع و مجوز کامل` in `specs_tab` with source/designer, Persian license selector, technical summary, and technical-features JSON;
- hydrate those controls from SQLite;
- persist the Persian license selector through `LICENSE_LABEL_TO_CODE`;
- extend regressions for clean schema and builder presence.

Git: `0da7ffead4401a6080226de1dbfc229176973af9`, `b84c33605fd22b32a3602707b84367f1ad431b04`, `db5948c23f8a7b55898e9aa42f4b4b6e587caf67`, `d0ddbc61820bca2b0222f1773de7cafd0c26cafa`, `1b2ed24dd67729855dda3714700f570f28c5619f`.

Rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`.

Verification: GitHub updated; owner Local rerun pending. Production untouched.

Prevention: a new Stage-owned field must land together in clean schema, upgrade path, visible control, stage persistence and regression coverage.


### ERR-49-071 — 67/67 PASS but Stage confirmation UX still broken and false missing count exploded
**Executable checkpoint:** `6085ea70d1075c5a1abaca4b4b2efdebe1254829`. Stage-2 confirmation persists visible Product type/dimensions before locking. No current-head Actions run is attached; owner Local verification remains pending.

**Date:** 2026-08-29  
**Environment:** owner foreground Windows QA on exact Local head `d4da99744659d06ebe5c04fd69532cd0e03db3e8`, Catalog Center 8.9.8 / build 2026.08.29.2.

**Owner evidence:** repository/branch/head verification PASS; fresh Catalog backup `D:\projects\3dprinthub-backups\err49-070-20260829-185545\catalog-before-err49-070-qa.sqlite3` with SHA256 `C1538C91C9F9E2173E7CA4E28B3F60DFCC1E38449A276F96845BC065CE689033`; compile PASS; exact two ERR-49-070 regressions PASS; OpenRouter-only 4/4 PASS; full Windows stage contract 67/67 PASS; foreground launch PASS. Visual QA nevertheless failed.

Observed UI/runtime:
- Stage 1 title and category were visibly filled but the rail still showed a red X and did not provide the simple explicit confirmation path the operator expects.
- ERR-49-069 had inserted `نوع محصول / ابعاد / کاربری` into Stage 1 even though those controls historically belong to the commerce/order surface; the owner explicitly rejected this relocation.
- explicit category `سایر محصولات` maps to `external-other`, but readiness treated that exact selected category as missing.
- every unlocked Stage appended `تأیید نهایی اپراتور (ثبت مرحله)` into its generic missing list; older/base readiness UI then counted pending confirmations as product-data defects, inflating the visible missing count to dozens.
- the visual rail used data completeness as a green check in some layers while the requested contract is: complete data may be pending, but the green check appears only after explicit `ثبت و تأیید`.
- the visible legacy Next button continued to be repainted by older layers, so rebinding that same widget remained fragile.
- while Product 63 Product-AI was still running, the visible title-only action on Product 286 started a second direct OpenRouter request. The title-only Tk callback had been created before the final runtime guard and was not included in the actual-widget rebind sweep.

**Root Cause:**
1. ERR-49-066 changed guided progress from confirmed `ready` to raw `data_ready`, which made visual completion semantics diverge from the operator's explicit approval workflow.
2. ERR-49-069 incorrectly moved Product type/dimensions/use-case into Stage 1 instead of preserving the historical visible stage layout.
3. 3I.36 and 3I.39 mixed operator-finalization markers into `state["missing"]`, so a confirmation workflow was reported as missing Product data.
4. Stage-1 category validation treated `external-other` as a placeholder even when `سایر محصولات` was a deliberate operator selection.
5. The final footer tried to mutate the legacy Next widget instead of owning an independent confirmation widget, allowing late callbacks to repaint it.
6. The title-only button retained a direct legacy callback and bypassed the app-level Product-AI runtime guard.

**Correct Fix — targeted rollback of the bad UX, not a broad source rollback:**
- restore Stage 1 to the historical visible responsibility: Persian title + site category; remove mounting of the added type/dimensions/use-case panel;
- keep Product type/dimensions/use-case in the existing Stage-2 commerce surface;
- stop mounting the added Stage-5 panel from ERR-49-070; retain the historical source/license surface and keep the additive DB column harmless;
- treat any explicit non-empty category, including `external-other / سایر محصولات`, as a valid Stage-1 category;
- separate real `missing_data` from `pending_finalization`; pending confirmation must never inflate the missing-data count;
- green `✅` means the Stage is data-complete **and explicitly confirmed**; data-complete but unconfirmed is `◌`;
- hide the repaint-prone legacy Next widget and create an independent permanent bottom action `✅ ثبت و تأیید مرحله →`; clicking it persists the current Stage, validates, writes the Stage lock, refreshes the rail, then advances;
- keep `✨ پرکردن ناقص‌ها با AI` and `✏ اصلاح مرحله` adjacent to the new confirmation action;
- rebind the actual visible `ترجمه فقط عنوان فارسی` Tk button to the same final Stage-1 AI runner so the app-level one-Product-AI-at-a-time guard and OpenRouter-only policy apply.

**Git source/test sequence:** starts at `a6f4d9d34d9a3963f34da7fe62fd206f0cd3364c` and currently extends through `950824d4104a7c0585ce417e9e57a498d5e2f4cf` before documentation commits.

**Rollback anchor:** `backup/pre-err49-071-stage-confirm-rollback-20260829` → `d4da99744659d06ebe5c04fd69532cd0e03db3e8`.

**Touched surfaces:** Windows guided Stage rail, Stage-1 readiness/category rule, stage ownership map/persistence, bottom confirmation controls, base/final readiness summaries, actual-widget AI callback rebinding, focused regressions and documentation.

**Must not touch:** Stage-2 Offer/Profile/pricing implementation itself, OpenRouter-only Provider policy, crawler/parser/acquisition, Product media binaries, secure key values, Django schema/migrations, Host or Production.

**Verification status:** owner proved the pre-fix head had 67/67 automated PASS but failed visual acceptance. ERR-49-071 code/regressions are on GitHub; new Local pull/test/foreground acceptance is mandatory. Production untouched.

**Prevention:** a visual acceptance gate must test the exact operator meaning of icons/actions, not just data persistence. A green Stage check is an explicit business-state transition and must not be inferred from field population. Pending approval and missing data are separate domains. Final-composition controls that must survive old callbacks should own independent widgets rather than repeatedly mutating legacy widgets.


### ERR-49-072 — new Stage-2 regression fixture used an incomplete clean Catalog schema
**Date:** 2026-08-29  
**Environment:** owner Local Windows, exact branch/head `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`, ERR-49-071 gate.

**Owner evidence:** canonical repo/branch/head PASS; fresh real Catalog SQLite backup created at `D:\projects\3dprinthub-backups\err49-071-20260829-193034\catalog-before-err49-071-qa.sqlite3` with SHA256 `0FA06AF7884F005A8820A420DBDC6C42B883E836A554F9C315E1D559854362F0`; changed-source compile PASS. The exact 7-test ERR-49-071 set stopped on one deterministic error before OpenRouter/full-suite/foreground launch:
`sqlite3.OperationalError: no such column: price_min`
inside `test_commerce_stage_persists_visible_product_type_and_dimensions`.

**Root Cause:** the new test reused the minimal `Database` bootstrap plus Profile/Ledger schema only. That fixture did not initialize the two real ProductWorkspace commerce schema layers:
- `epic49_desktop_schema.ensure_epic49_desktop_schema()` owns `price_min / price_max`;
- `phase49_3f_workspace.ensure_schema()` owns `pricing_strategy`.
The real ProductWorkspace initializes those schemas before Stage-2 editing, so this was a regression-fixture composition error, not evidence that the owner's existing Catalog database lost commerce columns.

**Failed condition:** do not rerun the same ERR-49-071 command on `34c65bc...`; its fixture is known incomplete.

**Correct Fix:** make the Stage-finalization test helper initialize the same Epic49 desktop + 3F pricing schemas as real ProductWorkspace construction before Profile/Ledger schemas. No runtime application source, Product data, Django schema/migration, Host or Production behavior is changed.

**Source/test fix:** `1307f4c438de184a930041d365976c2ce018bff8`.

**Rollback:** `backup/pre-err49-072-commerce-test-schema-20260829` → `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`.

**Verification status:** GitHub updated; no current-head GitHub Actions run is attached. Owner must ff-only pull the new docs-final head, rerun the changed exact regression gate, then OpenRouter/full Windows suite, and foreground launch only if all pass. Production untouched.

**Prevention:** any clean temporary Catalog DB test that exercises a mature Workspace layer must initialize the same schema composition that the runtime initializes; do not assume the minimal `Database._init()` contains every additive Epic49/3F column.


### ERR-49-073 — image Stage confirms, then downstream Content/Source makes Metadata look stale while lock blocks refresh
**Date:** 2026-08-29  
**Environment:** owner Windows foreground QA on exact `6d5897ecefc427c940c690daabc311f85cc6e044`, Catalog Center 8.9.8 / build 2026.08.29.2.

**Owner verification before defect:** exact ERR-49-071/072 regressions 7/7 PASS, OpenRouter-only 4/4 PASS, full Windows stage suite 71/71 PASS, foreground launch PASS. Stage 1/Content/Source/Slider confirmation worked. Owner intentionally left Stage-2 price/profile incomplete.

**Observed image defect:** Stage 3 could be finalized, but after later Content/SEO and Source/License stages changed, the image task surface reported `Metadata تصویر 1/2 • بروزرسانی Metadata`. The runtime repeatedly logged `stage_locked_write_blocked` around successful `images seo_finalize` events. Manual Metadata editor could also attempt a save against the already-confirmed image Stage.

**Root Cause:** image SEO signature intentionally includes later Product SEO/source facts. After those later stages change, deterministic image files are regenerated with the new facts, but `finalize_selected_images()` persisted its derived `image_metadata_json / image_alt_texts_json / selected_images_json / primary_image_url` through the normal guarded Product update. Because Images was already locked, the lock guard discarded those derived DB updates. Files were rebuilt, but the persisted signature stayed old, so the UI continuously reported stale Metadata. This is not a missing image-selection problem and not an AI-provider problem.

**Correct Fix:**
- add a strict derived-image persistence boundary that may use the existing raw DB updater only for the four finalizer-owned image fields;
- keep Stage lock protection for arbitrary operator/AI edits;
- when first confirming Images, run deterministic image finalization before readiness/lock;
- when Images is already confirmed and the owner presses `ثبت و تأیید مرحله` again, rebuild current SEO/Metadata under the derived-state exception and keep the Stage confirmed;
- in the final manual Metadata editor, block manual override saves while Images is locked and instruct the operator to use `اصلاح مرحله` for real edits; for stale derived Metadata, use Confirm or `نهایی‌سازی فایل‌های SEO`.

**Git changes:** derived refresh `b3eab828db5b09d1ac3a94fad4abdaa511e3c208`; image-confirm refresh `a1776471c773be3cdb221070d9b8f543d6701986`; locked editor guard `a97cf94772bb4422e5aa68fa2bed171f5a830ccf`; locked-image refresh regression `10b4dcd65407754deacc9bed45276623971f4dd9`; image-confirm finalization regression `b807cf837af6b6f46ca16149fec1acc031f4f890`.

**Rollback:** `backup/pre-err49-073-image-confirm-metadata-refresh-20260829` → `6d5897ecefc427c940c690daabc311f85cc6e044`.

**Must not touch:** Stage-2 pricing/Profile/Offer logic, OpenRouter-only AI, image selection itself, crawler/acquisition, secure keys, Django schema/migrations, Host/Production.

**Verification status:** code/regressions on GitHub; owner Local rerun required. Production untouched.

**Prevention:** distinguish immutable operator choices from deterministic derived artifacts. A Stage lock may block editing the approved inputs, but must not prevent the system from refreshing derived fingerprints/files when downstream authoritative metadata changes.

## OPEN / SEPARATE ITEMS
### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside current release gate. Public SEO sitemap is `/sitemap.xml`; verify internal route/client contract before adding duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled hard maximum is 20. New acquisition defaults to 5.

### ERR-OPEN-004 — Historical Product Admin 500
Resolved and Production verified; do not treat as open without fresh evidence.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process solution; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
- Social preview enhancement: dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` remain open; core meta/OG/canonical/schema/sitemap are present.
