# CURRENT PROJECT STATE

Updated: 2026-08-22
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.6 — Secure Credential Field Persistence`
Status: `GITHUB UPDATED / FINAL CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Windows already pulled and launched Phase49.3I.5 successfully. The owner confirmed that Product URL vs Group/Category/Search/sub-branch intake is corrected locally.

The remaining newly reported issue was credential UX persistence: FTP password, Bridge token and AI API key fields appeared empty after save/restart even though the secure backend already persisted credentials.

Phase49.3I.6 fixes that operator-visible hydration lifecycle and has now passed final GitHub CI. Windows has not yet pulled/tested 49.3I.6.

## Verified Root Cause — ERR-49-023
The secure backend stores credentials in Windows Credential Store under the stable service name `3DPrintHub Catalog Intelligence`, and runtime accessors already fall back to that secure store.

The UX87 shell did not mirror that persisted state:
- AI key field initialized empty,
- FTP password did not hydrate from Credential Store,
- Bridge token did not hydrate from Credential Store,
- mature Save handlers intentionally cleared those widgets after secure persistence.

Therefore the credentials could remain securely available to runtime while the UI looked as if they had disappeared.

## Phase49.3I.6 Implemented Delta
New additive module:
`catalog_center/app/phase49_3i_secret_persistence.py`

Behavior:
- Windows Credential Store/environment remains the secret source of truth,
- startup rehydrates FTP password and Bridge token into masked UI fields,
- startup rehydrates the selected AI provider key into the masked AI field,
- successful secure Save rehydrates fields after mature handlers clear them,
- switching AI provider loads that provider's stored key,
- routine same-provider refresh does not overwrite an unsaved newly-entered key,
- explicit clear/delete remains authoritative,
- no secret is written to SQLite, Git, source, diagnostics or logs.

Same-phase composition is attached after the mature 49.3I Product Explorer installer. Older independent phase installers remain untouched.

## Regression Coverage
`catalog_center/tests/test_epic49_phase49_3i_secret_persistence.py` verifies:
- startup hydration from secure APIs,
- post-save rehydration,
- provider-specific key switching,
- preservation of unsaved same-provider input,
- absence of SQLite/log/file secret persistence calls.

Canonical runner is `RUN_PHASE49_3I_LOCAL_GATE.ps1` v`49.3I.6`, ASCII-only for Windows PowerShell 5.1, with live fetched GitHub snapshot verification and marker:
`PHASE49_3I_SECRET_PERSISTENCE=ENABLED`.

## Final GitHub Validation — 49.3I.6
CI-only PR: `#51`
State: `CLOSED / NOT MERGED`
Validated Epic base: `f1e92f8f42a6ed90bf1001dc14a15638828ee341`
CI marker head: `fa8e4bcf5f7795983434f7cfd34c88918273bae6` — not merged.

Successful workflows:
- Phase49.3I Discovery Review Pricing CI — Run `32583277412` — SUCCESS.
- Phase49.3H SEO Cost Image Limit CI — Run `32583277584` — SUCCESS.
- Phase49.3G Workspace Usability CI — Run `32583277406` — SUCCESS.
- Phase49 Epic Unified CI / Full Django — Run `32583277418` — SUCCESS.

Validated inside CI:
- runner v49.3I.6 and Windows PowerShell 5.1 ASCII-only contract,
- live fetched Git snapshot guard,
- Python compile,
- dedicated credential hydration/persistence tests,
- secure-store-only composition/source contract,
- previous 49.3I Explorer/selection/routing regressions,
- Phase49.3H/3G regressions,
- Django checks,
- `makemigrations --check --dry-run` = no changes,
- no destructive schema operations,
- Windows Catalog Epic49 tests,
- Full Django suite.

## Windows QA Already Confirmed
- Catalog Center 49.3I.5 launches successfully.
- Product URL vs Group/Category/Search/sub-branch routing is corrected.

## Windows QA Required Now
1. close Catalog Center,
2. verify clean worktree,
3. fetch/prune and fast-forward-only pull current Epic,
4. run repository-owned `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp`,
5. verify Runner `49.3I.6` and `PHASE49_3I_GIT_SNAPSHOT=OK`,
6. save AI key and verify the masked field stays populated,
7. restart and verify the AI key is restored masked,
8. switch AI provider and verify that provider's stored key is restored masked,
9. save FTP password + Bridge token and verify both stay populated masked,
10. restart and verify both restore,
11. verify live AI/FTP/Bridge tests use the secure stored credentials,
12. recheck Product selection/open responsiveness and link routing,
13. recheck AI first-paint/progress,
14. recheck Fixed / Range / Formula pricing.

## Database / Migration / Media / Secret Safety
- Django schema change for 49.3I.6: `NONE` — CI verified.
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

## Local Publish Gate
Do NOT perform Local Publish until credential persistence plus remaining 49.3I visual/data/regression QA passes. Then perform exactly one `LOCAL PUBLISH ONLY` + Local Django E2E before any owner Production approval.

## Exact Next Task
Windows: clean fast-forward-only pull of the live fetched Epic snapshot, then run `RUN_PHASE49_3I_LOCAL_GATE.ps1 -LaunchApp` and verify secure masked credential persistence across Save/restart/provider switch. Do not patch Local source manually and do not touch Production.
