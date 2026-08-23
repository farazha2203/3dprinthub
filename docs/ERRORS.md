# ERROR KNOWLEDGE BASE

Search this file before troubleshooting. Never repeat a failed action unchanged. Detailed incident transcripts remain in Git history; this file keeps the current operational root-cause/fix/prevention knowledge.

## RESOLVED / CANONICAL PHASE49 ERRORS

- **ERR-49-001 — Tk pack/grid collision:** one geometry manager per parent; use holder frames.
- **ERR-49-002 — delayed thumbnail callback after widget destruction:** verify widget lifetime before async UI mutation.
- **ERR-49-003 — destroyed ProductWorkspace used as messagebox parent:** async result must verify parent existence.
- **ERR-49-004 — missing optional shell attributes:** guarded access only.
- **ERR-49-005 — image SEO semantic signature false-stale:** normalize structured JSON before hashing.
- **ERR-49-006 — dynamic consultation flag overwritten:** downstream state uses contract-aware merge/OR.
- **ERR-49-007 — PS5.1 NativeCommandError despite exit 0:** native exit code is truth; harmless stderr is not automatic failure.
- **ERR-49-008 — trace Bearer redaction order leak:** mask Bearer credentials before generic authorization formatting.
- **ERR-49-009 — later phase installed inside older independent installer:** compose phases at launch/runtime root.
- **ERR-49-010 — Bridge main-image materialization failure:** target Media ownership is a publish prerequisite.
- **ERR-49-011 — test guessed `upsert_product()` return:** resolve persisted product by real identity after upsert.
- **ERR-49-012 — security test coupled to one mask format:** assert secret absence semantically.
- **ERR-49-013 — explicit MakerWorld Search URL ignored:** explicit valid operator URL is authoritative.
- **ERR-49-014 — discovery full-fetched before review:** Preview and acquisition were separated. Phase49.3I.15 later supersedes the one-thumbnail-only rule for the owner-approved exact-page bulk path.
- **ERR-49-015 — runtime pricing choices caused phantom migration:** never mutate migration-owned Django field metadata at runtime.
- **ERR-49-016 — PS5.1 runner encoding parse failure:** repository Windows runners are ASCII-only and CI-enforced.
- **ERR-49-017 — Products UI patch missed real UX87 boundary:** patch/test final visible composition boundary.
- **ERR-49-018 — AI progress painted after synchronous preflight:** first-paint before any blocking work.
- **ERR-49-019 — stale Chat-pinned HEAD:** live fetch + clean exact branch + ff-only + Local HEAD == fetched Remote HEAD.
- **ERR-49-020 — product images clipped into strips:** pixel image viewport must not use Tk text-unit width/height.
- **ERR-49-021 — page/group URL misclassified as Product:** configured source `model_url_pattern` is authoritative boundary.
- **ERR-49-022 — Treeview selection feedback loop froze Product open:** one-way selection sync + reentrancy/repeat-open guards.
- **ERR-49-023 — secure credentials looked lost:** hydrate visible widgets from Windows Credential Store/environment after startup/save.
- **ERR-49-024 — Preview embedded JS invalid escaping:** browser-side JavaScript escape bytes are regression-tested.
- **ERR-49-025 — Provider Hub keys/models missing visually:** hydrate real `_ai_hub_key_vars`, not legacy field only.
- **ERR-49-026 — visible All-Fields button bypassed Task Center:** exact visible button routes to mature bounded/observable AI path.
- **ERR-49-027 — All-Fields could not refresh AI-owned values / generic titles persisted:** refresh AI-owned fields, protect manual edits, reject generic titles.
- **ERR-49-028 — HTTP success followed by delayed Tk exception callback crash:** freeze exception values; title retry has trace + 90s watchdog.
- **ERR-49-029 — provider returned useful but wrong JSON schema / model trace looked hung:** exact provider schema + one repair + compact model trace + immediate busy release.
- **ERR-49-030 — exact-page discovery worked but final UX hid state/results:** mount at final UX87 boundary; visible progress/candidates; 228x171 contain-fit images.

### ERR-49-031 — Windows URL paste + approved batch browser flashing
**Symptom:** URL paste unreliable; approved multi-select opened/closed one visible browser per row; technical candidate error hidden.  
**Root Cause:** plain Entry lacked explicit Windows paste bindings; batch inherited interactive `direct_link.headed=true`; stored `last_error` was not exposed.  
**Correct Fix — 49.3I.13:** Ctrl+V/Shift+Insert/right-click/visible Paste; approved batch background mode with setting restoration; candidate error detail.  
**Prevention:** business-critical Windows text fields have tested paste UX; batch must not inherit manual headed-browser defaults; persisted per-item error must be operator-visible.

### ERR-49-032 — New Discovery UI hid mature scan controls and forced 403-prone single route
**Symptom:** healthy `شروع اسکن`, Stop, smart-link and discovery actions disappeared; new Product action on MakerWorld 400767 hit `HTTP 403`.  
**Root Cause:** 49.3I.12 hid healthy controls; Preview wrapper shadowed `App87.start_scan`; new Product action forced Rich Direct while mature BaseApp scan still existed.  
**Correct Fix — 49.3I.14:** restore mature controls; resolve deepest/original BaseApp scan worker; single compatibility action uses mature `mode=single`; Rich Direct remains optional; Preview/Paste/Archive preserved.  
**Implementation incident:** first MRO resolver still selected Preview; targeted CI failed, code changed, fresh CI passed.  
**Prevention:** new operator features are additive unless explicitly replacing old behavior; tests verify visibility **and routing**.

### ERR-49-033 — Exact-page links were correct but per-product Full Fetch remained the business blocker
**Date:** 2026-08-23  
**Environment:** Windows Catalog Center 8.7.1 after 49.3I.14  
**Owner evidence:** exact MakerWorld Search/Listing discovery returns the correct product links, but individual Product/Rich Direct/approved Full Fetch repeatedly fails or stalls. The owner needs bulk catalog entry now and explicitly requests not to route selected listing candidates through single-product Full Fetch.

**Verified architectural cause:**
- working exact-page discovery and failing per-product Direct extraction were coupled by the old acceptance flow,
- `approve_discovery_candidates()` still depended on a network Full Fetch per selected row,
- that coupling was unnecessary for the immediate business requirement: source identity/title + a controlled image set are enough to create a review-state Product and let Product Workspace/AI finish the rest.

**Correct Solution — Phase49.3I.15:**
- exact Search/Listing URL remains authoritative,
- operator selects product limit up to 100 and image limit up to 20,
- first discover links with the already-verified exact-page discovery,
- then collect staged public images per candidate using the mature Classic browser/image helpers (`launch_fresh_browser`, `_dom_image_urls`, `_download_context_images`),
- persist staged image metadata as JSON manifests under the existing Catalog DATA root, without candidate-table migration,
- show image count per candidate,
- selected rows use `اضافه کردن انتخاب‌شده‌ها به محصولات`, which creates/updates the local Product from staged identity/title/images **without calling `extract_direct_link` or another Rich Direct Full Fetch**,
- unwanted candidates continue to Archive/Block,
- existing/blocked dedupe remains,
- one candidate failure does not abort the rest; Stop is checked between candidates.

**Validation on runtime feature head `a7cb319c2723ae2f9cfe87a1a00c8b33e7fcf619`:**
- Phase49.3I.15 Run `32641268643` SUCCESS,
- Phase49.3I Run `32641268627` SUCCESS,
- Phase49.3I.14 Run `32641268644` SUCCESS,
- Phase49.3H Run `32641268659` SUCCESS,
- Phase49.3G Run `32641268651` SUCCESS,
- Full Phase49 + Full Django Run `32641268645` SUCCESS,
- Django migration NONE; Catalog candidate schema migration NONE; Production untouched.

**Prevention:** when a verified listing boundary already provides correct product identities, do not force a second fragile acquisition boundary merely to move an item into review. Separate **staging** from **deep enrichment** and make the network-intensive path optional when business requirements allow it.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Outside current release gate. Verify route/client contract before adding any duplicate endpoint.

### ERR-OPEN-002 — AI request cost may be unknown
Never invent cost; use provider response/verified lookup or mark unknown.

### ERR-OPEN-003 — Historical image-limit inconsistency
Canonical controlled limit is max 20; current bulk operator exposes 5/10/15/20.

## WARNING DEBT
- CKEditor4 security/maintenance warning.
- `store.W026`: in-memory realtime is not a production multi-process architecture; Redis/polling is separate debt.
- Pillow `Image.getdata()` deprecation.
- Google membership credential warning when intentionally unset in CI.
