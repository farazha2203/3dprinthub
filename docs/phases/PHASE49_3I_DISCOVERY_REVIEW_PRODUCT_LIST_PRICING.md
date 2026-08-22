# Phase49.3I — Discovery Review + Product Gallery + Explicit Pricing Modes

Status: `GITHUB_UPDATED / 49.3I.3 CI SUCCESS / WINDOWS LOCAL RERUN PENDING`
Approved: 2026-08-22
Branch: `epic/phase49-unified-product-slider-sync`
Canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.3`
Production: `UNTOUCHED / NOT APPROVED`

## Scope
Phase49.3I owns:
1. exact operator Search/Listing URL discovery,
2. Preview → Approve → Full Fetch acquisition,
3. Archive/Blocked + duplicate guards,
4. safe scraped source text,
5. Products page gallery/routing to Product Workspace,
6. Fixed / Range / Formula pricing modes,
7. Local QA regression fixes required to make the approved 49.3H/49.3I UI contracts actually usable on Windows,
8. deterministic GitHub→Windows handoff that does not depend on a stale Chat-pinned SHA.

## A. Exact Search / Listing Contract
- explicit HTTP(S) listing/search seed is authoritative.
- MakerWorld example: `https://makerworld.com/en/search/models?keyword=cake+stand`.
- configured popular/download listings cannot silently replace an explicit operator URL.
- candidates deduplicate by source identity and normalized URL.
- regression fixtures include MakerWorld IDs `2834255` and `2845731`.

## B. Two-Stage Acquisition
### Preview
- discover candidate model links,
- one representative thumbnail,
- source title/basic identity,
- local review candidate state only,
- no full content/spec/image/file extraction.

### Approved Full Fetch
- operator selects candidate,
- image limit `1..20`, default 10,
- full extraction only after approval,
- persisted/selected/downloaded image cap enforced by Phase49.3H.

### Archive / Not Needed
- no full extraction,
- minimal blocked identity preserved,
- same source cannot be re-fetched until explicit restore.

## C. Source Text Safety
- Unicode NFKC normalization,
- Latin/English technical text and common punctuation preserved,
- CJK/Cyrillic/unexpected script/emoji/control garbage removed from scraped source text,
- URL/source identifiers preserved exactly,
- Persian `_fa` editorial/AI fields are not filtered,
- no historical mass rewrite.

## D. Products Gallery — Local QA Corrected Contract
Owner requirement:
- Products page must be a visual gallery, not a parameter-heavy editor/table.
- each product item shows only product image, product name and one Edit Product action.
- clicking image opens a larger preview.
- all detailed editing occurs in Product Workspace.

### Local QA Regression — ERR-49-017
Symptom:
- intended image gallery did not appear,
- legacy parameter/editor surface remained visible.

Verified Root Cause:
- first 49.3I implementation wrapped `App87._products_ui`.
- real UX87 `_ui()` explicitly calls `super()._products_ui()` and then `self._modernize_products_page()`.
- therefore the 49.3I override was bypassed by the real shell composition path.

Correct Fix:
- wrap `App87._modernize_products_page`, the actual UX87 boundary.
- preserve mature Treeview/editor widgets for compatibility but hide the entire legacy Panedwindow.
- render responsive vertically scrollable gallery cards.
- card contract: `thumbnail`, `title`, `edit` only.
- thumbnail size: 260x190.
- click thumbnail → local large preview up to 1000x720.
- local image resolution: strict local mapping → `page_extract.json` → `local_dir/images`.
- no list-time network image fetch.
- thumbnail loading is batched with Tk `after()` to reduce UI stalls.

## E. AI Progress First-Paint — Local QA Corrected Contract
Owner requirement:
- full AI autofill must immediately show progress,
- then show connection/send/receive/save stages,
- success leaves result/log drawer,
- errors remain visible with sanitized details.

### Local QA Regression — ERR-49-018
Symptom:
- full autofill appeared to hang before progress UI appeared.

Verified Root Cause:
- mature 49.3F `_phase49_3e_run_ai` performs synchronous `save(silent=True)` and preflight/source/material/category preparation before constructing `AIProgress`.
- network was already threaded, but there was no visible window during synchronous preflight.

Correct Fix:
- additive module `catalog_center/app/phase49_3i_local_qa_hotfix.py`.
- paint lightweight startup progress immediately.
- schedule mature flow with Tk `after(80)` to yield one paint cycle.
- when mature 49.3H `AIProgress` is created, it closes/replaces startup progress.
- existing Provider/Model selection, network worker, AI request, result/error drawer, cost ledger and runtime audit remain unchanged.
- no second AI request/network worker is introduced.

## F. Explicit Pricing Modes
1. `fixed` — exact final price; min=max.
2. `range` — operator min/max consultation range; not formula pricing.
3. `dynamic` — existing ProductVariant formula based on material, grams, print time, supervision and configured extras.

Server contract:
- semantic `range` stored in existing CharField without mutating Django field choices,
- `price_mode=range`,
- only `dynamic` uses formula engine,
- no new Django migration.

## G. Runner / Windows Compatibility
- canonical runner: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.3`.
- ASCII-only marker: `ASCII_ONLY_FOR_WINDOWS_POWERSHELL_5_1`.
- CI rejects any non-ASCII runner byte before PowerShell parse.
- chains full Phase49.3H/49.3G/49.3F... gates.
- includes Product gallery + AI first-paint regression tests.
- Production action prohibited.

Historical runner incident: `ERR-49-016`.

## H. GitHub Snapshot Handoff — ERR-49-019 / 49.3I.3
### Symptom
Windows was clean and on the correct Epic branch. `git fetch --prune origin` and `git pull --ff-only` succeeded, advancing Local from `fee6a5f...` to current GitHub HEAD `53e9216ae84a3e167481253da44760179c751051`. The Chat preflight then failed because it still pinned obsolete `$ExpectedHead=789edf8652ad8a09641afedd5e959c63822800c7`.

### Verified Root Cause
A SHA copied into Chat was treated as a permanent handoff target while the development branch was still allowed to advance. Later documentation commits moved the branch after that Chat response. GitHub and Local behaved correctly; the stale Chat constant was the failed contract. The existing Git-only Windows policy already required resolving the Remote Epic HEAD after fetch, so the failed Chat preflight also violated an existing repository rule.

GitHub compare from validated base `97674a82acc97e1a623b76084b60344cfa93142b` to Windows-pulled `53e9216...` shows seven post-validation commits and only `PROJECT_CONTEXT.md` + `docs/*`. No runtime, runner, migration, DB, media or production surface changed in those seven commits.

### Permanent Fix
Runner v49.3I.3 now performs its own handoff safety check before tests:
1. clean worktree required,
2. exact Epic branch required,
3. live `git fetch --prune origin`,
4. resolve fetched `origin/epic/phase49-unified-product-slider-sync`,
5. require Local HEAD == fetched Remote HEAD,
6. mismatch fails closed with `git pull --ff-only` instruction,
7. rerun the same repository gate after pull.

The handoff no longer uses a Chat-pinned SHA as sole source of truth.

CI adds source-contract assertions for runner version 49.3I.3, expected branch, live fetch, fetched remote ref and `PHASE49_3I_GIT_SNAPSHOT=OK`.

## Runtime Files
- `catalog_center/app/phase49_3i_discovery_review.py`
- `catalog_center/app/phase49_3i_source_safety.py`
- `catalog_center/app/phase49_3i_product_list.py`
- `catalog_center/app/phase49_3i_local_qa_hotfix.py`
- `catalog_center/app/phase49_3i_pricing_modes.py`
- `store/phase49_3i_pricing_modes.py`
- `catalog_center/launch.py`
- `store/apps.py`
- `RUN_PHASE49_3I_LOCAL_GATE.ps1`
- `.github/workflows/phase49-3i-ci.yml`

## Database Safety
- Django migration for Phase49.3I / 49.3I.3: NONE.
- Candidate review table: local Catalog SQLite additive only.
- Product gallery and AI first-paint fixes: UI/runtime sequencing only.
- 49.3I.3 handoff fix changes Git safety runner/CI/docs only.
- no reset/drop/truncate/delete.
- no historical row/media rewrite.
- Production DB/source untouched.

## GitHub Verification
### Original Phase49.3I
- PR #42 closed / not merged.
- 49.3I `32569551060` SUCCESS.
- 49.3H `32569551053` SUCCESS.
- 49.3G `32569551048` SUCCESS.
- Full Phase49/Django `32569551034` SUCCESS.

### PowerShell runner encoding hotfix
- PR #44 closed / not merged.
- 49.3I `32570978818` SUCCESS.
- 49.3H `32570978800` SUCCESS.
- 49.3G `32570978829` SUCCESS.
- Full Phase49/Django `32570978799` SUCCESS.

### Local QA Gallery + AI Progress regression hotfix
- PR #46 closed / not merged.
- validated runtime base before docs closure: `bf51fff1000bfcc6561712a243cb13e48001123c`.
- 49.3I `32573421461` SUCCESS.
- 49.3H `32573421431` SUCCESS.
- 49.3G `32573421523` SUCCESS.
- Full Phase49 + Full Django `32573421439` SUCCESS.

### Docs-Closed Final Validation
- PR #47 closed / not merged.
- exact validated Epic base: `97674a82acc97e1a623b76084b60344cfa93142b`.
- marker head `0530181f1b4f2fcedadbdc0cc34251c43f2b1f3b` not merged.
- 49.3I `32573779531` SUCCESS.
- 49.3H `32573779534` SUCCESS.
- 49.3G `32573779548` SUCCESS.
- Full Phase49 + Full Django `32573779528` SUCCESS.

### 49.3I.3 Git Handoff Guard
- PR #48 closed / not merged.
- exact validated Epic base: `7117510f173f45a3d8c806e46fb0476cbaeba115`.
- probe marker head `fc400359442efef336b445a72d60002f78eab916` not merged.
- 49.3I `32575765467` SUCCESS.
- 49.3H `32575765515` SUCCESS.
- 49.3G `32575765544` SUCCESS.
- Full Phase49 + Full Django `32575765457` SUCCESS.

## Must Not Regress
- Phase49.3H SEO execution progress/result/error console and AI cost ledger,
- immediate AI startup feedback,
- selected-image text-only AI privacy,
- image intake default 10 / hard max 20,
- product gallery image/name/edit-only surface,
- Product Workspace detailed editor,
- AI provenance/manual override,
- ProductVariant Dynamic price source of truth,
- Local/Production publish separation,
- Product/Hero revision/idempotency,
- Persian content integrity,
- secret redaction,
- Windows PowerShell 5.1 ASCII runner contract,
- live fetched GitHub snapshot handoff guard.

## Remaining Acceptance Gates
1. Windows clean worktree,
2. fetch/pull `--ff-only` current Epic branch,
3. run repository runner v49.3I.3 with `-LaunchApp`,
4. runner must emit `PHASE49_3I_GIT_SNAPSHOT=OK`,
5. Products gallery visual QA + large image preview,
6. full AI autofill immediate progress → mature progress/result drawer QA,
7. MakerWorld cake+stand Preview/Approve/Archive/Dedupe QA,
8. image limit QA,
9. Fixed / Range / Formula QA,
10. one LOCAL PUBLISH ONLY + Local Django E2E,
11. explicit owner approval,
12. only then Production plan/deploy.

## Delivery Gate
49.3I.3 handoff guard has passed CI. Production remains forbidden. Next gate is Windows Local rerun from the current Epic branch using repository-owned runner v49.3I.3; no manual Windows source patch and no stale Chat-pinned Expected HEAD.
