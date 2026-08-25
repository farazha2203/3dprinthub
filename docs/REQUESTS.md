# OWNER REQUESTS

Last Updated: 2026-08-25

Older detailed request history remains available in Git history. This file keeps the active acceptance contracts.

## Preserved Core Contracts
- REQ-49H-001: AI/SEO execution/result/error visibility with sanitized diagnostics.
- REQ-49H-002: real provider-supported cost only; never invent unknown cost.
- REQ-49H-003: image intake default 10 / hard max 20.
- REQ-49I-001: explicit Search/Listing URL is authoritative.
- REQ-49I-003: Archive/Not Needed blocks rediscovery without destructive deletion.
- REQ-49I-004: dedupe by source + external id + normalized URL.
- REQ-49I-006: Product Workspace remains canonical editor.
- REQ-49I-007: Fixed / Range / Formula remain independent.
- REQ-49I-009: Windows delivery uses live fetched GitHub snapshot, clean branch and ff-only pull.
- REQ-49I-014: Provider/FTP/Bridge secure persistence.
- REQ-49I-016..019: observable AI, rerun generated values, sanitized trace, exact schema and bounded watchdog.
- REQ-49I-022: bulk exact-page image acquisition + Add-to-Products.
- REQ-49I-023: resilient acquisition fallback + persistent method trace.
- REQ-49I-024: exactly one saved Provider/Model/key path for Product AI; no hidden fallback/model scan/AI-on-open.
- REQ-49I-025: source title must be canonical before translation/SEO.
- REQ-49I-026: operator controls must be visibly reachable in normal Workspace use.

## REQ-49I-027 — AI actions must not look frozen and must be diagnosable
Status: `IMPLEMENTED / SUPERSEDED IN PART BY 49.3I.22 WINDOWS QA`
- provider requests are bounded and observable,
- request start/success/error/timeout are sanitized,
- Stop/Cancel blocks late apply,
- diagnostics can be exported locally,
- no GitHub PAT/API key is stored in logs.

49.3I.21 solved the long provider wait boundary, but fresh Windows evidence showed a separate Tk cross-thread freeze class; REQ-49I-029 below is now part of the same acceptance gate.

## REQ-49I-028 — Complete all editable product information from the exact Product URL
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`
- action `تکمیل همه اطلاعات بر اساس لینک محصول`,
- exact source URL authoritative,
- source fetch/parse + canonical identity before AI,
- AI receives URL + sanitized facts + selected media/material/color context,
- visible source → AI → preview → apply lifecycle,
- no Product update before operator confirmation,
- unified Persian content/SEO/image metadata apply,
- price/stock/source URL/commercial choices not overwritten,
- failed/cancelled request preserves old Product data.

Primary fixture:
`https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?from=search#profileId-3236824`

## REQ-49I-029 — Every Product AI worker must be Tk-main-thread safe
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Owner evidence: Product Workspace becomes Windows `(Not Responding)` after AI actions and may require force-close even when the visible AI panels and source title are correct.

Acceptance:
- background network/AI work may remain on Python worker threads,
- no worker thread may directly call Tk/Tcl,
- worker `after(...)` handoffs must be serialized through a Python-only queue and executed by a pump owned by the Tk main thread,
- Tk-backed source variables must be snapshotted on the main thread before worker access,
- the same contract must protect Task Center, image AI, all-fields AI, manual-name rebuild, source+AI rebuild and link-grounded refresh,
- errors/cancellation/stale-result behavior remains observable and sanitized,
- no duplicate Provider/model or AI business path is introduced.

Implementation: `phase49_3i22_tk_thread_bridge.py`, installed at the final Product Workspace composition boundary.

## REQ-49I-030 — Product stages rail must scroll vertically
Status: `IMPLEMENTED ON FEATURE BRANCH / WINDOWS LOCAL QA REQUIRED`

Acceptance:
- all Product stage/readiness/AI controls remain reachable on shorter Windows displays,
- a visible vertical scrollbar exists,
- later panels appended by mature phases participate in the same scrollregion,
- mouse wheel scrolls the rail when the pointer is over it,
- stage navigation semantics remain unchanged.

Implementation: Canvas + `ttk.Scrollbar` host in `product_workspace_v87.py`.

## Operational Release Request
### REQ-REL-001 — Hand Catalog Center to employees and deploy approved release
Status: `BLOCKED BY 49.3I.22 WINDOWS QA + ONE LOCAL PUBLISH E2E + OWNER APPROVAL`

After approval: verify Host/branch/MySQL/backup/rollback and deploy only the approved GitHub snapshot.

## Next Product Request
### REQ-PAY-001 — Normal Store checkout must support online payment
Status: `REQUESTED / AFTER CATALOG DEPLOY`
- reuse mature Phase30 ZarinPal security semantics,
- server owns/recomputes amount,
- idempotent attempt identity,
- stored Authority must match callback,
- server-to-server Verify before paid,
- duplicate callback cannot double-finalize order/inventory,
- bank transfer remains available,
- Sandbox E2E before live activation,
- secrets only in secure configuration.

## Canonical Windows Gate
Run 49.3I.22 focused tests + inherited 49.3I.21/20/19/18/17 regressions, then acquisition baseline gates. Production remains untouched until PASS + Local Publish E2E + owner approval.

## Change Rule
New requests do not authorize unrelated redesign. Extend/Patch/Wrap mature behavior and regression-test the exact active operator/store boundary.
