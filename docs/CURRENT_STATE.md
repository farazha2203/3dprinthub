# CURRENT PROJECT STATE

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.6 — Secure Credential Field Persistence`
Status: `GITHUB IMPLEMENTED / FINAL CI PENDING / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Windows pulled and launched Phase49.3I.5 successfully. The owner confirmed that the Product URL vs Group/Category/Search/sub-branch intake problem is now corrected locally.

The next Windows QA finding is credential UX persistence: FTP password, Bridge token and AI API key fields appear empty again after save/restart even though the project contract says secrets must remain stable between releases.

Repository inspection proved this is an operator-visible hydration/lifecycle defect, not a reason to move secrets into SQLite or source files.

## Verified Root Cause — ERR-49-023
The secure backend already stores credentials in Windows Credential Store under the stable service name `3DPrintHub Catalog Intelligence` and runtime accessors already fall back to that store.

However the UX87 shell initializes several masked fields from environment/new input only:
- AI key field starts empty,
- FTP password field does not hydrate from Credential Store,
- Bridge token field does not hydrate from Credential Store.

The mature save handlers then intentionally clear those fields after writing the secrets securely. Runtime calls may still work because `_ai_key()` / `_site_connection()` fall back to the secure store, but the UI looks as if the credentials disappeared.

## Phase49.3I.6 Implemented Delta
New additive module:
`catalog_center/app/phase49_3i_secret_persistence.py`

Behavior:
- Windows Credential Store/environment remains the only secret source of truth,
- startup rehydrates FTP password and Bridge token into masked UI fields,
- startup rehydrates the selected AI provider key into the masked AI field,
- successful secure Save rehydrates fields after mature handlers clear them,
- switching AI provider loads that provider's stored key into the masked field,
- routine source/status refresh does not overwrite an unsaved newly-entered key for the same provider,
- explicit clear/delete actions remain authoritative,
- no secret is written to SQLite, Git, source, diagnostics or logs.

Same-phase composition is attached after the mature 49.3I Product Explorer installer. Older independent phase installers remain untouched.

## Regression Coverage Added
`catalog_center/tests/test_epic49_phase49_3i_secret_persistence.py` verifies:
- startup hydration from secure APIs,
- post-save rehydration,
- provider-specific key switching,
- preservation of unsaved same-provider input,
- absence of SQLite/log/file secret persistence calls.

Canonical runner is upgraded to `49.3I.6` and now requires/compiles/tests the new module and prints `PHASE49_3I_SECRET_PERSISTENCE=ENABLED`.

Phase49.3I CI now checks:
- runner 49.3I.6 + ASCII-only Windows PowerShell 5.1 contract,
- secure module/test presence,
- composition after mature Product Explorer,
- secure-store-only source contract,
- prior 49.3I/3H/3G regressions,
- Django no-new-migration and destructive-schema guards.

## Windows QA Already Confirmed
- Catalog Center 49.3I.5 launches successfully.
- Product URL vs Group/Category/Search/sub-branch routing is corrected.

Still pending:
- credential persistence QA,
- AI first-paint/progress regression QA,
- Fixed / Range / Formula pricing regression QA,
- LOCAL PUBLISH ONLY + Local Django E2E.

## Database / Migration / Media / Secret Safety
- Django schema change for 49.3I.6: `NONE` intended; final CI pending.
- Catalog schema change: `NONE`.
- no DB reset/drop/truncate.
- no media rewrite/delete.
- secrets remain outside SQLite/Git/logs.
- Production DB/media/source untouched.

## Preserved Contracts
- 49.3I.5 selection-loop guard and compact metadata,
- Explorer view modes/multi-select/context menu,
- Product Workspace detailed editor,
- Product-vs-Group routing by source `model_url_pattern`,
- Preview → Approve → Full Fetch,
- archive/blocked duplicate guards,
- image default 10 / hard max 20,
- AI progress/result/error/cost stack,
- Fixed / Range / Formula independence,
- Local/Production publish separation,
- live fetched GitHub snapshot handoff.

## Exact Next Task
Complete final GitHub CI validation for 49.3I.6. Only after all required workflows succeed and documentation is closed should Windows fast-forward pull the current Epic and run the repository-owned `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` for masked credential persistence QA. Do not patch Local source manually and do not touch Production.
