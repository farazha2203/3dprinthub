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

**Symptoms:**
- pressing AI or performing a Product edit visibly refreshed the Products page,
- repeated edits/AI calls became progressively expensive with many Product cards/images,
- AI appeared slow before/after the provider request because unrelated UI work was executed.

**Root Cause:** mature `ProductStudio.save()` called `app.refresh_products()`, `app.refresh_published()` and `app.load_product()` even for `save(silent=True)`. Product AI paths invoked silent save as preflight, while the Product Explorer renderer destroyed/rebuilt every visible card and requeued thumbnails. This coupled product-scoped writes to a global gallery rebuild.

**Correct Fix:**
- Phase49.3I.29 makes Workspace save/AI set a dirty marker while temporarily deferring global `refresh_products`/`refresh_published`/`load_product`,
- Products presentation is paged to 48 cards while retaining the complete SQLite/Treeview result set,
- Product AI uses the exact mother Provider/Model without hidden per-request model-list scans,
- Phase49.3I.31 batch processing never refreshes globally per item and performs one final Products refresh only after the selected-product batch finishes/stops.

**Prevention Rule:** product-scoped Save/AI must not rebuild the global Products Explorer. Batch operations may refresh the Products Explorer once at the explicit batch boundary. Performance tests must assert bounded presentation and deferred refresh contracts.

**Release status:** implemented in candidate 8.8.2; targeted 49.3I.31-32 CI PASS, Windows packaged/live QA still required before acceptance.

### ERR-49-053 — Generic/silent Product Save could erase the canonical source URL
**Date:** 2026-08-26  
**Environment:** Windows Catalog Center Product Workspace.

**Symptom:** after pressing an apparently unrelated Product action, the saved Product source link disappeared.

**Root Cause:** mature `ProductStudio.save()` calculated the canonical link only as `source_url.get().strip() or spec_source_url.get().strip()`. When both mirrored UI controls were temporarily blank, generic/silent Save wrote an empty `source_url`, recomputed `normalized_url` from the empty value and regenerated the Product fingerprint from the empty identity. Silent Save is reused by close, refetch, AI preflight, publish and layered Workspace actions, so the visible triggering button did not need to be a link-edit action.

**Important previous condition:** this was not a crawler/OpenRouter/AvalAI deletion. The destructive write happened at the common Save boundary before/around those feature-specific flows.

**Correct Fix — Phase49.3I.32:**
- compose a final Workspace Save wrapper after all older layers,
- resolve explicit non-empty edits first, but when both mirrored URL controls are blank preserve an already stored DB source URL,
- feed the resolved canonical URL back into both controls before entering the mature Save chain,
- enforce a post-save invariant that restores `source_url`, `normalized_url` and fingerprint if any legacy layer still clears them,
- for Products already damaged by the old bug, recover only an exact previously persisted HTTP/HTTPS URL: latest `product_history` snapshots first, matching `discovered_urls(source_code, external_id)` second,
- recovery is local-only, uses no network and never guesses/reconstructs a URL,
- record recovery in Product history/diagnostics.

**Regression coverage:** `tests.test_phase49_3i32_source_url_guard` proves: both blank controls preserve an existing URL; explicit main/spec edits remain valid; a never-linked Product stays blank; the exact pre-delete URL is recovered from history; matching discovery identity is the fallback; the final Workspace wrapper blocks the old destructive Save behavior.

**Verification:** GitHub Actions `Phase49.3I.31-32 Smart Link Bulk AI + Source Guard CI` run `32996526852` PASS on `2ca69c4928333fc15247b99014a8fe77d781b50b`.

**Prevention Rule:** generic Save, silent Save, AI, close, refetch, image or publish-related flows may never be destructive source-unlink operations. Clearing a persisted canonical Product source URL requires a future explicit, separately confirmed unlink operation; transient empty UI state is never authority to destroy source identity.

## RESOLVED PHASE50 / RELEASE INCIDENTS

### ERR-50-001 — Phase50 Admin CI used non-canonical Django environment names
Use `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`.

### ERR-50-002 — Dynamic ModelAdmin URL patch unstable at final URL boundary
Use explicit project-level routes wrapped by `admin.site.admin_view`.

### ERR-50-003 — Catalog Center 8.8.1 version identity mismatch
Version bump is atomic across app version, launcher, manifest, config and release tests.

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
**Correct Fix:** verify `git ls-remote`, explicitly fetch `refs/heads/agent/phase49-3i18-operator-bulk-ai-rebuild` to `FETCH_HEAD`, verify exact SHA/ancestry, ff-only merge.  
**Prevention:** never trust `origin/<branch>` on this host without checking refspec/upstream.

### ERR-50-008 — Legacy permanent Django filter column crushed modern Admin changelists
**Date:** 2026-08-26  
**Symptom:** `#changelist-filter` permanently occupied a narrow sticky column and squeezed Product results.  
**Root Cause:** historical adapter CSS layers both reserved layout width for the native filter block.  
**Correct Fix:** keep native filter semantics but move the node into an on-demand Velzon drawer; full-width results remain default.  
**Verification:** Product Admin CI run `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

### ERR-50-009 — Velzon absolute footer and document-level active-menu scroll caused refresh flash/page jump
**Date:** 2026-08-26  
**Environment:** owner QA of the Velzon V2 Admin.

**Symptoms:**
- during refresh/navigation the footer text/line could appear across the visible page before settling,
- clicking/navigating Admin menu items felt like the entire page jumped,
- the default 250px right sidebar made long Persian labels difficult to read.

**Root Cause:** Velzon 4.3.0 absolute footer assumptions + Django/SimpleBar dynamic layout + project `scrollIntoView({behavior:'smooth'})` on the active menu + default 250px sidebar.

**Correct Fix:** normal-flow footer, stable flex shell, 290px sidebar, no broad geometry transitions, active link centered by internal sidebar/SimpleBar `scrollTop` only.

**Verification:** Admin CI run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`; deployed at `c283864290f9c989a9fcdf24ee8eef519560e917`. Owner browser visual QA remains before ACCEPTED.

### ERR-50-010 — cPanel Bash process substitution failed because `/dev/fd` was unavailable
**Date:** 2026-08-26  
**Environment:** Production deployment backup step.

**Symptom:** `.env*` backup loop using `done < <(find ... -print0)` stopped with `bash: /dev/fd/63: No such file or directory`.

**Root Cause:** this cPanel/shared-host shell does not provide a reliable `/dev/fd` process-substitution path in the deployment execution context.

**Failed attempt:** Bash process substitution for enumerating environment files. The deployment stopped before fetch/merge/migration/restart, leaving Production unchanged.

**Correct Fix:** enumerate `Path.rglob('.env*')` and copy files using the verified Production Python runtime; avoid `/dev/fd` dependency.

**Verification:** recovery deployment created 8 environment backups and completed source/MySQL backup successfully at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

**Prevention:** Production scripts for this host must avoid process substitution and `/dev/fd`; use Python or portable temporary files/pipelines instead.

### ERR-50-011 — Variant API verifier executed JSON as Python source
**Date:** 2026-08-26  
**Environment:** post-deploy Production verification.

**Symptom:** valid API JSON caused `NameError: name 'false' is not defined`.

**Root Cause:** verifier invoked `python <variant-api.json> ...`, making Python execute the JSON file as source code. JSON booleans (`false`) are not Python literals.

**Failed attempt:** treating the JSON path as the Python script argument.

**Correct Fix:** invoke `python - <json-path> <variant-id>` and parse the supplied JSON file with `json.load` from the heredoc/stdin Python program.

**Verification:** final Production read-only verify returned `VARIANT_API=PASS`, Product ID 1, selection mode `size_build`, profile `استاندارد`, build `standard`, material `PLA`, price `2131170`, final/shipping weight `1.00`, and `FINAL_PRODUCTION_VERIFY=PASS`.

**Prevention:** verifier data files are arguments, never executable source; parse JSON explicitly and include a regression/smoke contract for endpoint schema.

## OPEN / SEPARATE ITEMS
### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside current release gate. Public SEO sitemap is `/sitemap.xml`; verify internal route/client contract before adding a duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled hard maximum is 20. New acquisition defaults to 5.

### ERR-OPEN-004 — Historical Product Admin 500
Resolved and Production verified; do not treat as currently open without fresh evidence.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process solution; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
- Social preview enhancement: dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` remain open; core meta/OG/canonical/schema/sitemap are present.
