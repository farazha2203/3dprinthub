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
**Symptom:** `AttributeError: 'Database' object has no attribute 'categories'`.  
**Root Cause:** mature category provider is `App.get_all_categories()`.  
**Correct Fix:** compatibility bridge delegates to the existing App provider.  
**Prevention:** verify mature provider APIs before adding wrappers.

### ERR-49-050 — Exact-link canonical title helper bound `current_title` twice
**Date:** 2026-08-25  
**Symptom:** `canonical_source_title() got multiple values for argument 'current_title'`.  
**Root Cause:** wrapper violated the mature helper signature.  
**Correct Fix:** delegate with named arguments in the correct positions.  
**Prevention:** regression-test exact call shapes for mature helper wrappers.

### ERR-49-051 — Production Hero referenced internal imported-catalog media and returned HTTP 404
**Date:** 2026-08-25  
**Root Cause:** Hero Studio emitted imported working-media URLs that Production intentionally does not serve publicly.  
**Correct Solution:** resolve public Hero media to Product-owned gallery/main image, with safe remote fallback only when needed.  
**Prevention:** public consumers must use public entity-owned media; never widen Production routing to imported working-media.

## RESOLVED PHASE50 / RELEASE INCIDENTS

### ERR-50-001 — Phase50 Admin CI used non-canonical Django environment names
Use exact project settings names `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`; do not infer generic names.

### ERR-50-002 — Dynamic ModelAdmin URL patch was unstable at final URL boundary
Use explicit project-level routes wrapped by `admin.site.admin_view` for late operational Admin endpoints.

### ERR-50-003 — Catalog Center 8.8.1 version identity mismatch
A version bump is atomic across app version, launcher, package manifest, example config and release tests.

### ERR-50-004 — Frozen portable verification assumed physical launcher source
Frozen verification must test import/runtime contracts, not physical `.py` presence.

### ERR-50-005 — Admin media patch replaced mature list contract
Extend final mature ModelAdmin composition; do not replace `list_display` without preserving dependent edit/link invariants.

### ERR-50-006 — Unified Product Admin regression assumed stale `seo_status`
**Date:** 2026-08-26  
**Root Cause:** test asserted an older intermediate Admin composition.  
**Correct Fix:** preserve mature Product list and assert current boundary-owned invariants.  
**Verification:** GitHub Actions run `32941662288` PASS.

### ERR-50-007 — Production `git fetch --prune origin` left active branch remote-tracking ref stale
**Date:** 2026-08-26  
**Environment:** Production host `/home/sfkilvrs/3dprinthub`.  
**Symptom:** pre-deploy `git ls-remote` correctly returned active GitHub branch HEAD `9cfbc54ed4196144864b5f4201976d8466a88134`, but after `git fetch --prune origin`, `origin/agent/phase49-3i18-operator-bulk-ai-rebuild` remained at `8fbe3413cada1099745f4d17312b8eb519694379`; deployment stopped before source mutation.

**Verified Root Cause:** host Git configuration had only this fetch refspec:
`+refs/tags/v0.33.0:refs/tags/v0.33.0`
and the active branch had no configured upstream. Therefore normal `git fetch --prune origin` did not fetch/update branch remote-tracking refs.

**Failed Attempt:** repeating `git fetch --prune origin` and trusting `origin/<branch>` would keep the same stale result because the refspec did not include branch heads.

**Correct Fix:** verify live GitHub HEAD with `git ls-remote`, then explicitly fetch `refs/heads/agent/phase49-3i18-operator-bulk-ai-rebuild` to `FETCH_HEAD`; verify exact SHA and fast-forward ancestry; deploy with ff-only merge from `FETCH_HEAD`.

**Verification:** explicit fetch returned the approved branch snapshot; fast-forward succeeded; Django check, migration drift, Product Admin runtime gate, collectstatic, Passenger restart and Production HTTP smoke all passed; final Production worktree was clean.

**Prevention:** before relying on `origin/<branch>` on Production, inspect `git config --get-all remote.origin.fetch` and branch upstream. If branch heads are not fetched, either correct the refspec deliberately or use explicit verified branch fetch to `FETCH_HEAD`. Never repeat a stale remote-tracking fetch unchanged.

### ERR-50-008 — Legacy permanent Django filter column crushed modern Admin changelists
**Date:** 2026-08-26  
**Environment:** owner QA of Production Admin at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.  
**Symptom:** Product changelist was HTTP 200 but visually poor: `#changelist-filter` stayed permanently visible as a narrow sticky column, squeezed the Product result table, required its own long vertical scroll, and exposed legacy English labels such as `FILTER`, `Show counts` and `Action`.

**Root Cause:** multiple historical presentation layers (`master-django.css` and the first Phase50 console CSS) both treated Django's native filter block as a permanent second changelist column. Server-side Admin tests verified renderability, but did not own the final browser composition boundary.

**Rejected Fix:** merely shrinking/restyling the filter column would preserve the same usability problem and continue competing with wide Product tables.

**Correct Fix:** preserve the native Django filter links/query semantics but move the existing `#changelist-filter` node at runtime into an on-demand off-canvas filter drawer. The default changelist becomes full-width. Add project-owned Velzon V2 CSS/JS for drawer/backdrop/reset/active count, Persian labels, modern search/actions/table/pagination, and long-form section navigation.

**Verification:** `node --check` PASS; GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS on code snapshot `3687d0922959fca53f2118be6dacd32639159346`; Django check, migration drift, CI migrations and focused Admin HTTP/static regressions all PASS. Production visual verification remains required after deployment.

**Prevention:** test both server-render contracts and the final composition adapter. Do not reserve permanent layout width for optional filters on wide operational tables. Purchased Velzon vendor assets remain private/gitignored; public GitHub contains only project-owned integration layers.

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
