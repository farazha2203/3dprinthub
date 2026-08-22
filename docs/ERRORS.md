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

## OPEN / SEPARATE ITEMS

### ERR-OPEN-001 — Local `/api/v1/catalog/sitemap/` returns 404
Status: OPEN / outside Phase49.3H
Rule: investigate route/client contract before Epic closure; do not add duplicate endpoint without root-cause verification.

### ERR-OPEN-002 — AI request cost may be unknown
Status: OPEN, addressed by Phase49.3H
Evidence: historical AI request logs include tokens/request IDs but `cost_usd=—` for some AvalAI calls.
Rule: never invent a cost. Use provider response or verified provider cost lookup; otherwise mark unknown.

### ERR-OPEN-003 — Image acquisition limit inconsistent
Status: OPEN, addressed by Phase49.3H
Current observed behavior: main UI default can be 60 and per-product controls allow up to 100, while prior project policy expected a much tighter cap.
Rule: one canonical image-limit normalizer must cap all intake/refetch/persisted-selected flows.

## Warning Debt (not current blockers)
- `ckeditor.W001`: CKEditor4 security/maintenance debt.
- `store.W026`: in-memory realtime not suitable for multi-process production without Redis/polling strategy.
- Pillow `Image.getdata()` deprecation.
- Google membership credentials warning when intentionally unset in CI.
