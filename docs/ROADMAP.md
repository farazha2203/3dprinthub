# PROJECT ROADMAP

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Active Branch: `epic/phase49-unified-product-slider-sync`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.6 — Secure Credential Field Persistence`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI → WINDOWS PULL --FF-ONLY → LOCAL GATE → MANUAL QA → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Preserved Phase49 Foundations
- unified Product / Hero / Catalog synchronization,
- Product Workspace as canonical detailed editor,
- Persian content and SEO workflows,
- Product / Portfolio publish targets,
- AI provider/runtime/provenance/cost stack,
- image intake default 10 / hard max 20,
- Fixed / Range / Formula pricing,
- Local vs Production publish separation,
- GitHub-first Windows delivery and live fetched snapshot guard.

## Phase49.3I Progress
Implemented and preserved:
- explicit operator Search/Listing/Category URL is authoritative,
- Preview Candidate before Full Fetch,
- approved-only Full Fetch,
- archive/not-needed + blocked identity dedupe,
- source-text sanitation,
- visual Products Explorer,
- Explorer view modes/multi-select/context menu,
- selection feedback-loop guard,
- compact Product ID/state/source/image/date/publish metadata,
- Persian filters/sorts,
- source `model_url_pattern` Product-vs-Group routing,
- AI first paint,
- Windows PowerShell 5.1 ASCII runner,
- secure credential field hydration from Windows Credential Store.

## Windows QA Confirmed After 49.3I.5
Owner confirmed:
- Catalog Center launches after the 49.3I.5 handoff,
- Product link vs Group/Category/Search/sub-branch routing is fixed.

## Phase49.3I.6 — Secure Credential Field Persistence
Status: `FINAL CI SUCCESS / WINDOWS QA PENDING`

### Requested Delta
Credentials saved securely must not appear to vanish on the next save/restart/release. The stable secure location remains Windows Credential Store; passwords/tokens/API keys must not be moved into SQLite, Git, source files or logs.

### Verified Boundary
The secure backend already persisted and read credentials. The defect was operator-visible hydration: masked fields initialized without secure-store values and mature Save handlers cleared their widgets after secure persistence.

### Implemented Scope
1. Add `phase49_3i_secret_persistence.py` as an additive App87 shell layer.
2. Hydrate FTP password and Bridge token from secure storage at startup when empty.
3. Hydrate selected AI provider key from its secure provider entry.
4. Rehydrate masked fields after a successful mature Save clears them.
5. On Provider change, load that Provider's stored key.
6. Do not overwrite newly typed unsaved input during normal same-provider refresh.
7. Preserve explicit credential delete/clear behavior.
8. Keep all credentials out of SQLite/log/source/Git.
9. No schema migration and no Production action.

### Final Validation
CI-only PR `#51`: `CLOSED / NOT MERGED`.
Validated Epic base: `f1e92f8f42a6ed90bf1001dc14a15638828ee341`.
Marker head: `fa8e4bcf5f7795983434f7cfd34c88918273bae6` — not merged.

Successful runs:
- Phase49.3I: `32583277412` — SUCCESS.
- Phase49.3H: `32583277584` — SUCCESS.
- Phase49.3G: `32583277406` — SUCCESS.
- Full Phase49 + Full Django: `32583277418` — SUCCESS.

CI verified:
- runner v49.3I.6 / ASCII-only contract,
- live Git snapshot guard,
- secure credential startup/save/provider-switch tests,
- secure-store-only composition/source contract,
- previous Explorer/selection/routing regressions,
- Phase49.3H/3G regressions,
- Django checks,
- no migration drift,
- no destructive schema operations,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Must-Not-Touch
- Product Workspace detailed editor,
- existing secure backend semantics and explicit delete actions,
- 49.3I.5 selection-loop guard,
- Product-vs-Group routing,
- AI result/error/cost stack,
- image limit 10/20,
- Fixed / Range / Formula independence,
- Product/Hero revision/idempotency,
- Production DB/media/source,
- historical media,
- secrets in Git/log/SQLite.

## Windows Manual QA — NEXT
Windows must prove saved AI key, FTP password and Bridge token remain visibly present as masked values immediately after Save and after restart; switching AI provider restores that provider's saved key; live AI/FTP/Bridge tests consume the secure credentials; no secret appears in SQLite/logs/source. Existing link-routing, selection/open, AI progress and pricing regressions are rechecked.

## Local Publish Gate
Only after credential + remaining 49.3I manual QA passes:
- one `LOCAL PUBLISH ONLY`,
- Local Django E2E,
- verify product/image/pricing/provenance payload,
- no Production endpoint.

## Production Gate
Production remains blocked until Windows QA and Local Publish E2E pass and the owner explicitly approves Production. Before deploy, re-verify host branch/commit/path, MySQL vendor/name, backup and rollback.

## Immediate Next Step
Windows clean fast-forward-only pull of the live fetched Epic snapshot, then repository-owned v49.3I.6 local gate with `-LaunchApp` and secure credential persistence QA. No Production command yet.
