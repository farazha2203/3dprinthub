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
**Date:** 2026-08-25  
**Symptom:** `AttributeError: 'Database' object has no attribute 'categories'` before exact-link source/AI work began.  
**Root Cause:** the mature category provider is `App.get_all_categories()`; Catalog `Database` intentionally has no categories repository API.  
**Correct Fix:** final workspace compatibility bridge delegates category retrieval to the existing App provider.  
**Prevention:** never infer repository APIs from convenience naming; verify the mature provider boundary before adding a compatibility call.

### ERR-49-050 — Exact-link canonical title helper bound `current_title` twice
**Date:** 2026-08-25  
**Symptom:** `canonical_source_title() got multiple values for argument 'current_title'`.  
**Root Cause:** the wrapper passed source URL as positional `current_title` and also passed `current_title=` explicitly, violating the mature 49.3I.19 signature.  
**Correct Fix:** compatibility adapter delegates to the mature signature with named arguments in the correct positions.  
**Prevention:** when wrapping mature helpers, regression-test the exact call shape that failed in owner QA.

### ERR-49-051 — Production Hero referenced internal imported-catalog media and returned HTTP 404
**Date:** 2026-08-25  
**Environment:** Production Passenger/LiteSpeed, non-DEBUG media routing.  
**Owner Evidence:** first real Catalog Site Publish produced a healthy Product page, but homepage Hero text rendered over a blank/dark area. Browser console showed 404 for `/media/store/imported-models/gallery/...`; Local `127.0.0.1:8000` rendered the same slide correctly.

**Verified Root Cause:** `ImportedPrintAssetImage.image` is stored under `store/imported-models/gallery/`, which is a Catalog working-media namespace. Production intentionally serves public Store media only (`store/products`, `store/categories`, `store/seo`), while DEBUG serves all media. The mature Hero Studio preferred `selected_asset_image.image.url`, so Local hid the ownership mismatch and Production correctly rejected the internal path.

**Correct Solution — Phase49.3I.30:** keep the imported image relation for editor/audit identity, but resolve public Hero media to the matching Product-owned gallery copy by filename; fall back to Product main image; use remote source only when no Product-owned public media exists. Do not expand Production routing to expose imported working media.

**Prevention:** every public media consumer must resolve to the target public entity's owned media namespace. A database FileField URL is not automatically a public URL in Production.

## RESOLVED PHASE50 / RELEASE INCIDENTS

### ERR-50-001 — Phase50 Admin CI used non-canonical Django environment names
**Date:** 2026-08-25  
**Symptom:** first CI run stopped at `manage.py check` with `DJANGO_SECRET_KEY must be configured`; a later run returned HTTPS 301 responses where test expectations required direct 200/302 behavior.  
**Root Cause:** the new workflow guessed generic `SECRET_KEY` and `DEBUG` environment names instead of reading `config/settings.py`, which uses `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` and `DJANGO_ALLOWED_HOSTS`.  
**Failed Attempt:** repeating the workflow with generic environment variables would not change Django's effective settings.  
**Correct Fix:** use the exact names consumed by project settings and run the CI test environment with `DJANGO_DEBUG=1`.  
**Verification:** `manage.py check`, migration dry-run and focused Phase50 Admin tests passed in GitHub Actions.  
**Prevention:** CI/runtime configuration names are repository contracts; never infer them from Django defaults or another project.

### ERR-50-002 — Dynamic ModelAdmin URL patch was not stable at the actual Admin URL boundary
**Date:** 2026-08-25  
**Symptom:** Hero quick-action reverse lookups failed with `NoReverseMatch` even though actions were attached to the ModelAdmin class.  
**Root Cause:** patching `ModelAdmin.get_urls()` after the mature Admin composition had already occurred did not guarantee those names existed in the final resolver used by the running project.  
**Failed Attempt:** adding more reverse calls against the dynamically patched Admin namespace would preserve the same boundary mismatch.  
**Correct Fix:** expose explicit project-level routes in `config/urls.py`, wrap each with `admin.site.admin_view`, keep mutations POST-only, and link the Admin template to those stable named routes.  
**Verification:** focused Admin route/action tests passed in GitHub Actions.  
**Prevention:** for late runtime Admin extensions, patch visual/actions at the Admin boundary but register new operational routes at a stable URL composition boundary unless registration order is proven by tests.

### ERR-50-003 — Catalog Center 8.8.1 app version advanced while release metadata remained 8.8.0
**Date:** 2026-08-25  
**Symptom:** Local launch failed with `Launcher expected 8.8.0, but imported 8.8.1`; the first 8.8.1 Windows release CI also failed two version-contract tests.  
**Root Cause:** `app/version.py` was advanced to 8.8.1 while `launch.py`, `PACKAGE_MANIFEST.json`, `config.example.json` and one regression assertion still declared 8.8.0.  
**Failed Attempt:** running the stale launcher or repeating the release workflow unchanged could never produce a valid 8.8.1 release.  
**Correct Fix:** align all release identity surfaces with `APP_VERSION=8.8.1` and keep the manifest/config/launcher contract test as a release gate.  
**Verification:** the next Windows run passed all 92 regression tests and canonical launcher verification.  
**Prevention:** a Windows version bump is atomic across app version, launcher expected version, package manifest, example config and release tests.

### ERR-50-004 — Frozen 8.8.1 portable verification blocked on a physical launcher source-file assumption
**Date:** 2026-08-25  
**Symptom:** PyInstaller produced `3DPrintHub-CatalogCenter-v8.8.1.exe`, but `--portable-verify` remained alive until the 90-second build timeout and the runner killed the orphan process.  
**Root Cause:** the newer portable verification tried to read a physical `launch.py` beside `portable_entry.py`. In a one-file/windowed PyInstaller runtime Python modules are bundled/importable but are not guaranteed to exist as ordinary source files; an unhandled frozen GUI exception can remain behind a windowed error dialog, causing the parent smoke runner to time out.  
**Failed Attempt:** increasing the timeout or repeating the same frozen verification would preserve the source-file assumption.  
**Correct Fix:** validate the bundled canonical launcher by importing `launch.EXPECTED_VERSION` and `launch.main`, requiring `EXPECTED_VERSION == APP_VERSION` and a callable canonical entrypoint; do not read `launch.py` from the extraction filesystem.  
**Verification:** Windows release run passed frozen self-verification, frozen Playwright/browser smoke, SHA256/manifest validation, artifact upload and GitHub Release publication for `catalog-center-v8.8.1`.  
**Prevention:** frozen-runtime verification must test import/runtime contracts, never assume bundled Python modules are present as physical `.py` source files.

### ERR-50-005 — Admin media patch replaced mature `list_display` but left Phase35 editable/link contracts active
**Date:** 2026-08-25  
**Symptom:** first `Phase50 Admin Media Mobile CI` stopped at `manage.py check` with `admin.E111` for `source_title_admin` and `admin.E122` for `editorial_status`, `fixed_print_price` and `price_is_final`.  
**Root Cause:** the initial safe-preview patch replaced the ImportedPrintAsset `list_display`, while mature Phase35 still owned `list_display_links` and `list_editable` pointing to columns removed by that replacement.  
**Failed Attempt:** repeating CI or selectively deleting those mature edit contracts would regress the existing professional catalog editor.  
**Correct Fix:** preserve the mature Phase35 `list_display`, `list_display_links`, `list_editable`, actions and fieldsets; insert only readonly `safe_preview` and `completeness` columns plus a compact health fieldset.  
**Verification:** corrected CI run `32875771848` passed Django check, migration dry-run/migrate, Admin/mobile/SEO regressions and Windows image-dimension regression.  
**Prevention:** late Admin parity patches must extend the final composed ModelAdmin contract rather than replacing list/fieldsets without carrying dependent `list_editable` and `list_display_links` invariants.

### ERR-50-006 — Unified Product Admin regression assumed a stale `seo_status` list column
**Date:** 2026-08-26  
**Symptom:** first `Phase50 Product Admin Workspace CI` run `32941533091` passed compile, Django check, migration drift and SQLite migration apply, then failed one test because `seo_status` was not in the final Product `list_display`.  
**Root Cause:** the new regression test asserted an intermediate/older SEO list-column composition instead of the actual mature Product Admin list after later sales/commerce extensions. SEO remained available through the real Product SEO fieldset and `seo_preview`.  
**Failed Attempt:** re-adding a stale list column just to satisfy the test would couple the new Product workspace to an obsolete intermediate Admin composition.  
**Correct Fix:** preserve the actual mature Product list and align the test with its owned invariants (`minimum_price`, `price_is_final`, sales-profile selection and `seo_preview`).  
**Verification:** corrected run `32941662288` PASS: compile, Django check, no migration drift, SQLite migrations through `store.0035`, unified Product Admin regressions and gate marker all passed.  
**Prevention:** regression tests for late Admin composition must assert final behavior/invariants owned by the active boundary, not stale columns from an earlier composition layer.

## OPEN / SEPARATE ITEMS
### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside the current release gate. Public SEO sitemap is `/sitemap.xml`; verify internal route/client contract before adding a duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled hard maximum is 20. New acquisition defaults to 5.

### ERR-OPEN-004 — Historical Product Admin 500
The 2026-08-25 Production `/admin/store/product/` 500 was later cleared in owner deployment/smoke verification. Keep historical evidence in Git history; do not treat it as a currently open blocker without fresh evidence.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process solution; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
- Social preview enhancement: dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` are not yet emitted; core meta/OG/canonical/schema/sitemap are present.
