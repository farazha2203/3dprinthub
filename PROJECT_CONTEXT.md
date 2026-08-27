# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Subphase: `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Subphase: `49.3I.35 — Operator Ledger + Resilient AI / Catalog Center 8.9.1`  
Status: `GITHUB CI + WINDOWS ONE-FILE PACKAGE PASS / AUTOMATED LOCAL GATE PASS / OWNER VISUAL QA NEXT / PRODUCTION NOT DEPLOYED`

## Operating rule
GitHub is permanent source of truth.

`READ DOCS → VERIFY REAL STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → UPDATE DOCS`.

No permanent Production source edits. Dirty Local/Host worktree means STOP/INSPECT.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`  
Windows venv: `D:\projects\3DPrintHub\.venv`  
Catalog persistent root: `D:\projects\3dprinthub-catalog-manager`  
Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`

Production root: `/home/sfkilvrs/3dprinthub`  
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`  
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`  
Static: `/home/sfkilvrs/public_html/static`  
Media: `/home/sfkilvrs/public_html/media`  
Private media: `/home/sfkilvrs/3dprinthub/private_media`

## Production baseline — last terminal verified
Application commit:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Latest verified rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

Last verified Phase50 migration state:
- applied: `store.0034_phase50_variant2_commerce`,
- applied: `store.0035_phase50_sales_profiles`,
- not claimed applied: `0036`, `0037`, `0038`, `0039`.

Production remains on the stable baseline. Never infer that later migrations were applied from GitHub/CI.

## Approved Windows runtime candidate
Application runtime snapshot:
`2622818d898e19b745c61ff653b80c03d22288f1`.

Latest test-tooling head before documentation finalization:
`b9c4d8d5f94c61c536736a1a828eff809f8e109d`.
Only the local 31–35 gate/workflow changed after the packaged application runtime; no packaged application module changed.

Catalog Center:
- version `8.9.1`,
- build `2026.08.27.3`,
- Smart/Profile 31–35 run `33060613937` PASS,
- Single-AI run `33060613914` PASS,
- Windows portable run `33060047878` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.1`,
- artifact ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- public Release publication skipped/manual until owner Local QA.

3I.35 owns:
- registered Product Profile ledger over the mature 3I.34 transport,
- temporary working form → independent Profile snapshots,
- multiple weight/time/support production rows,
- material/brand/manufacturer/color roll offers and local Product selection commit,
- effective explicit sale-rate calculation,
- visible AI preflight/progress/retries/configured fallback,
- bulk Product isolation,
- manual SEO/source readiness review,
- existing source identity/link/history protections.

Canonical phase document:
`docs/phases/PHASE49_3I35_OPERATOR_LEDGER_RESILIENT_AI_FILAMENT.md`.

## Approved Web/Store candidate
Phase50.A.2E extends 2B–2D with:
- migration `store.0039_phase50_filament_offer_pricing`,
- brand/manufacturer/roll/pricing/FX MaterialColorOption facts,
- ProductVariant support weight,
- immutable StoreOrderItem support weight + filament brand/manufacturer,
- brand-distinct Storefront material selection,
- formula pricing from effective brand/color sale rate,
- spool-first then roll-snapshot stock availability.

Verification:
- Phase50 run `33059883188` PASS,
- no migration drift,
- clean CI SQLite migration through `0039`,
- 16 Variant/Profile/Checkout tests PASS.

## Owner Local automated acceptance
- owner Local root `D:\\projects\\3DPrintHub` verified exact repository/branch and clean worktree,
- Local fast-forwarded to `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`,
- effective Local Django DB verified as SQLite `D:\\projects\\3DPrintHub\\db.sqlite3`,
- fresh pre-0039 DB backup `D:\\projects\\3dprinthub-backups\\phase49-3i35-resume-20260827-142404\\django-local-before-0039.sqlite3` with matching SHA256,
- `store.0038` verified applied and `store.0039` verified pending before write,
- exact `0039_phase50_filament_offer_pricing` plan inspected, then `0039` applied successfully,
- 16 Store/Profile/Checkout regressions PASS,
- post-migration `makemigrations --check --dry-run` = no changes detected,
- Catalog Center 31–35 Local gate PASS with 107 tests, source URL invariant PASS, launcher verify PASS,
- Catalog Center `8.9.1` / build `2026.08.27.3` launched successfully,
- Production touched = NO.

Manual operator/visual QA is the only remaining Local acceptance gate before Host read-only audit.

## Resolved current incidents
- `ERR-50-016`: support-weight runtime metadata mismatch tried to create fake 0040 → align runtime with migration 0039; no fake migration.
- `ERR-49-056`: Windows 8.9.1 gate had stale quick-price UI assertion + config 8.9.0 → align test/business contract and package version.

## Rollback anchors
Git:
- `backup/pre-phase49-3i35-operator-ledger-20260827` → `ca9cc1160f407c0a78302ad75cb38396616aed52`,
- `backup/pre-phase49-3i35-integration-20260827` → `1b02d413be00c09631661eafaf252d011ad45d40`.

A fresh Production source/environment/MySQL backup is still mandatory before schema work.

## Exact next step
1. On `D:\projects\3DPrintHub`, verify correct repo, branch, clean worktree and live GitHub head.
2. Pull ff-only.
3. Run `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` against the exact live head with `-LaunchApp`.
4. Owner visual/functional QA:
   - Profile ledger registration/load/new-from-last,
   - multiple weight/time/support rows,
   - Bambu/eSUN same material/color distinction,
   - roll stock and formula/fixed price,
   - AI visible progress/retry/fallback,
   - manual SEO/source review,
   - source URL/images remain intact,
   - no global Products refresh on local step actions.
5. Run local Django Store regressions and local SQLite migrations only.
6. Only after Local QA PASS: Host read-only branch/HEAD/worktree/remote/MySQL/migration-plan/disk/mysqldump audit.
7. Fresh Production backups/checksums.
8. Deploy exact approved GitHub commit with explicit `FETCH_HEAD` per `ERR-50-007`.
9. Apply only the read-only-verified pending chain, expected today as `0036 → 0037 → 0038 → 0039`.
10. collectstatic, Passenger restart, Production HTTP/API/schema/order/private-media verification, then docs.

## Host constraints
- `ERR-50-007`: Production remote refspec is tag-only; verify live branch and explicit `FETCH_HEAD`.
- `ERR-50-010`: do not rely on cPanel `/dev/fd` process substitution.
- `ERR-50-011`: JSON is data; parse with `python -` + `json.load`.
