# PROJECT ERROR KNOWLEDGE BASE

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
