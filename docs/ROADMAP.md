# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.21 — Observable AI Jobs + Link-Grounded Full Refresh`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → COMMIT/PUSH IF LOCAL CODE CHANGES → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. Windows acceptance of 49.3I.21 AI timeout/diagnostics/link-grounded full refresh,
2. regression acceptance of 49.3I.20 visible panels,
3. regression acceptance of 49.3I.19 source identity and 49.3I.18 operator/bulk metadata,
4. chain 49.3I.17 and acquisition gates,
5. exactly one Local Publish E2E,
6. explicit owner approval,
7. verify Production branch/path/venv/MySQL/backup/rollback,
8. deploy approved GitHub snapshot and verify Production,
9. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition Fallback/Cached Reuse → Single Active AI Runtime → Operator Editing/Bulk Metadata → Canonical Source Identity Before AI → Visible Operator Panels → Observable AI Jobs + Link-Grounded Full Refresh`.

## 49.3I.21 — Observable AI Jobs + Link-Grounded Full Refresh
Repository verification found the generation path had a 210-second provider timeout, matching the 03:30 operator-visible wait. 49.3I.21 hardens this boundary instead of treating the symptom as a DB field-permission problem.

Implemented contract:
- global bounded provider POST timeout; default 75s, environment override 20..120s,
- request-start / success / error / timeout diagnostics before and after network calls,
- existing secret redaction retained,
- AI content generation receives product URL plus sanitized source facts,
- new Product Workspace action `تکمیل همه اطلاعات بر اساس لینک محصول`,
- stages: source fetch → parse → canonical identity → AI request → received preview → explicit apply,
- one unified apply path updates editable Persian content, SEO fields and image metadata,
- price, stock, source URL and operator commercial choices remain protected,
- explicit `توقف انتظار`; cancelled late result must not be applied,
- local Diagnostics bundle export for deterministic troubleshooting.

Acceptance fixture:
`2896217-ribbed-cake-stand-cookie-platter` must retain the exact source identity and, after a successful approved refresh, must not keep the generic Persian title `مدل میکرورلد 2896217`.

## Preserved Previous Contracts
### 49.3I.20
Visible Stage 3 bulk-image controls and Stage 4 source-identity/operator-AI panels stay above expandable editor/gallery content.

### 49.3I.19
Valid exact-page/source title is authoritative; generic model-number titles are rejected; MakerWorld URL slug remains deterministic fallback.

### 49.3I.18
Global clipboard support, bulk image filename/Alt/Title/Caption operations, operator-authoritative Persian title and full AI rebuild remain intact.

### 49.3I.17
One saved Provider/Model/key path; no hidden provider fallback and no hidden AI request on Product Workspace open.

### Acquisition
49.3I.16 resilient source/image acquisition, archive/block/dedupe, image caps and Add-to-Products contracts remain intact.

## Database / Migration
Django migration: NONE.
Catalog schema migration: NONE.
Existing diagnostics tables are reused.
Production untouched.

## Focused Windows Gate
1. clean worktree + live fetch/ff-only feature branch,
2. verify Local HEAD equals fetched Remote HEAD,
3. compile 49.3I.21 and composition modules,
4. run 49.3I.21/20/19/18 tests plus 49.3I.16/15/discovery regressions,
5. run `launch.py --verify-only`,
6. verify new Stage 4 link-grounded AI panel,
7. open product 2896217 and run full refresh from link,
8. observe source-fetched → AI-request → received-preview → apply stages,
9. confirm correct Persian identity/content/SEO/image metadata after explicit approval,
10. test cancellation during provider wait and confirm no late apply,
11. export Diagnostics and confirm no API key/token is present,
12. retest legacy AI buttons; UI must remain responsive and diagnostics must expose provider/model/operation/timeout,
13. chain previous 49.3I acceptance gates.

If PASS, proceed to exactly one Local Publish E2E and then owner-approved Production gate.

## Next Product Phase
After Catalog Production verification: Store checkout ZarinPal request/callback/verify, Sandbox E2E, then one owner-approved low-value live payment while bank transfer remains available.