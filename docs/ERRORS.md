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
Failed Condition: CI parsed the Unicode text correctly under modern `pwsh` on Linux, so syntax-only CI did not reproduce this Windows PowerShell 5.1 encoding boundary.
Correct Solution: `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.1` is ASCII-only. Manual QA guidance in the runner uses ASCII text; Persian UI/docs remain unchanged. `.github/workflows/phase49-3i-ci.yml` now rejects any non-ASCII byte in the Windows runner before parsing it.
Verification: CI-only PR #44 closed without merge; Phase49.3I Run `32570978818` SUCCESS; Phase49.3H Run `32570978800` SUCCESS; Phase49.3G Run `32570978829` SUCCESS; Full Phase49/Django Run `32570978799` SUCCESS.
Prevention Rule: repository `.ps1` files intended for Windows PowerShell 5.1 must either have a validated BOM/encoding contract or remain ASCII-only. For canonical Local Gate runners, enforce ASCII-only bytes in CI so GitHub UTF-8 storage cannot become a legacy-decoding parse failure.

### ERR-49-017 — Phase49.3I Products UI patch missed the real UX87 composition boundary
Date: 2026-08-22
Related Phase: 49.3I Local QA regression hotfix
Environment: Windows Catalog Center 8.7.1
Symptoms: Products page still showed the legacy parameter/editor surface and no intended image-card gallery. The owner expected large product images, product name and one edit action only.
Verified Root Cause: `phase49_3i_product_list.py` wrapped `App87._products_ui`, but `ux87_shell.CatalogCenterApp87._ui()` explicitly calls `super()._products_ui()` and then `self._modernize_products_page()`. Therefore the 49.3I `_products_ui` wrapper was bypassed by the real shell construction path.
Failed Condition: the original regression test only asserted source-string presence and did not verify the actual UX87 composition call path.
Correct Solution: wrap the real `App87._modernize_products_page` boundary; keep the mature Treeview/editor alive but hide the complete legacy Panedwindow; render a responsive local-only card gallery with 260x190 thumbnails, product name, one Edit Product action, vertical scrolling and click-to-large-preview. Thumbnail loading is batched through Tk `after()` to avoid a large synchronous render stall.
Verification: CI-only PR #46; Phase49.3I Run `32573421461` SUCCESS; Phase49.3H Run `32573421431` SUCCESS; Phase49.3G Run `32573421523` SUCCESS; Full Phase49/Django Run `32573421439` SUCCESS.
Prevention Rule: UI patch tests must verify the real shell composition boundary, not only the target method's source patterns. If a shell explicitly calls `super().method()`, patching the subclass override of that method is ineffective.

### ERR-49-018 — AI progress window was created after synchronous preflight work
Date: 2026-08-22
Related Phase: 49.3I Local QA regression hotfix / protected 49.3H execution console
Environment: Windows Catalog Center Product Workspace
Symptoms: clicking full AI autofill appeared to hang briefly before any progress UI became visible, even though the network call itself ran in a worker thread.
Verified Root Cause: the mature 49.3F `_phase49_3e_run_ai` performs `save(silent=True)`, row/source/material/color/category preparation and other synchronous preflight work before constructing `AIProgress`. The Tk event loop therefore had no progress window to paint during that preflight interval.
Correct Solution: add an additive first-paint handoff at the composition root. A lightweight startup progress window is created immediately, the existing flow is scheduled via Tk `after(80)`, and when the real 49.3H `AIProgress` is constructed it replaces the startup window. Existing provider/model/network worker, result/error drawer, cost ledger and audit behavior are not duplicated or replaced.
Verification: CI-only PR #46; Phase49.3I Run `32573421461` SUCCESS; Full Phase49/Django Run `32573421439` SUCCESS.
Prevention Rule: any user-triggered operation with synchronous UI-thread preflight must paint immediate feedback before starting that preflight; network threading alone is not sufficient UX responsiveness.

### ERR-49-019 — Windows handoff failed because Chat-pinned Expected HEAD became stale
Date: 2026-08-22
Environment: Windows PowerShell / GitHub handoff
Related Phase: 49.3I.3 handoff guard
Symptoms: Windows clean-worktree fetch and `git pull --ff-only` succeeded, updating Local from `fee6a5f...` to real remote HEAD `53e9216ae84a3e167481253da44760179c751051`, but the Chat-provided preflight then failed because it still required `789edf8652ad8a09641afedd5e959c63822800c7`.
Verified Root Cause: the handoff command pinned a mutable branch to a SHA copied into Chat. After that SHA was issued, additional repository documentation commits advanced the Epic branch. The local pull correctly followed GitHub, but the stale Chat constant incorrectly treated the newer valid branch HEAD as an error. This also violated the existing `docs/GIT_ONLY_WINDOWS_DELIVERY_POLICY.md`, which already required resolving Remote Epic HEAD after fetch rather than hardcoding an old SHA.
Evidence: GitHub comparison `97674a82acc97e1a623b76084b60344cfa93142b..53e9216ae84a3e167481253da44760179c751051` contains only `PROJECT_CONTEXT.md` and `docs/*`; no runtime, runner, migration, database or media file changed in those seven post-validation commits.
Failed Attempt: reusing a fixed `$ExpectedHead` from Chat as the source of truth for a branch that could advance before the operator executed the command.
Correct Solution: repository runner v`49.3I.3` performs a live `git fetch --prune origin`, requires the exact Epic branch, verifies clean worktree, reads `origin/epic/phase49-unified-product-slider-sync` after that fetch, and requires Local HEAD to equal that fetched remote snapshot. If they differ, it fails with a `git pull --ff-only` instruction and must be rerun. No reset/stash/delete shortcut is used.
Verification: CI-only PR #48 closed without merge. Validated Epic base `7117510f173f45a3d8c806e46fb0476cbaeba115`. Phase49.3I Run `32575765467` SUCCESS; Phase49.3H Run `32575765515` SUCCESS; Phase49.3G Run `32575765544` SUCCESS; Full Phase49 + Full Django Run `32575765457` SUCCESS. CI verifies runner version `49.3I.3`, ASCII-only compatibility, live fetch guard, expected branch guard, fetched remote-ref guard and `PHASE49_3I_GIT_SNAPSHOT=OK`.
Prevention Rule: never use a Chat-pinned SHA as the sole Windows handoff truth for a mutable development branch. Pin the fetched remote snapshot inside the same local execution, then verify Local HEAD equals that snapshot; repository CI must protect the handoff contract.

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Status: OPEN / outside Phase49.3I
Rule: investigate route/client contract before Epic closure; do not add duplicate endpoint without root-cause verification.

### ERR-OPEN-002 — AI request cost may be unknown
Status: mitigated by Phase49.3H
Evidence: historical AI request logs include tokens/request IDs but provider cost may not be available.
Rule: never invent a cost. Use provider response or verified provider cost lookup; otherwise mark unknown.

### ERR-OPEN-003 — Historical image acquisition limit inconsistency
Status: runtime contract addressed by Phase49.3H; Windows pull/QA pending
Rule: canonical normalizer is default 10 / hard max 20 across new intake/refetch/persisted-selected flows.

## Warning Debt (not current blockers)
- `ckeditor.W001`: CKEditor4 security/maintenance debt.
- `store.W026`: in-memory realtime not suitable for multi-process production without Redis/polling strategy.
- Pillow `Image.getdata()` deprecation.
- Google membership credentials warning when intentionally unset in CI.
