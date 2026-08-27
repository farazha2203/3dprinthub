# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Subphase: `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Subphase: `49.3I.38 — Permanent Crawl Ledger + Reject/Purge + Stage-scoped AI / Catalog Center 8.9.6`  
Status: `8.9.6 GITHUB + WINDOWS PORTABLE PASS / OWNER LOCAL VISUAL 3I.38 QA NEXT / PRODUCTION NOT DEPLOYED`

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
`c904193a7f0af9aad80365834ec3f0b856e77dc9`.

Catalog Center:
- version `8.9.6`,
- build `2026.08.27.8`,
- targeted 31–38 run `33077213590` PASS with 84 tests,
- Single Active AI run `33077239617` PASS,
- Windows portable run `33077239660` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.6`,
- artifact ID `9648474905`,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`,
- artifact ZIP digest `sha256:13ae8582be09b71f90e607c2230075d875b7445f8a46b6462a9241edf9d52563`.

3I.38 preserves 3I.35–3I.37 and adds:
- permanent crawled/received Product identity ledger,
- persisted deeper Listing crawl cursor without replacing the mature discoverer,
- reject + safe local-file/image purge while retaining source URL/external-ID tombstone,
- Direct Link terminal identity check before browser/HTTP/image/file acquisition,
- explicit restore as the only path to receive a rejected identity again,
- one Product AI engine with Link / Saved-Crawled Data / Screenshot inputs,
- same engine for selected-Product Bulk Stage-4 SEO,
- explicit single-stage cleanup/completion with out-of-scope Stage immutability,
- no Provider request for image-only work when image SEO is already complete.

Canonical phase document:
`docs/phases/PHASE49_3I38_CRAWL_LEDGER_STAGE_AI.md`.

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
- `ERR-49-063`: fixed-depth category/site crawl repeatedly exposed the first discovery window → persisted bounded deeper-scroll cursor while retaining mature discoverer.
- `ERR-49-062`: Direct Link terminal identity was checked after acquisition → rejected/blocked identities now stop before browser/HTTP/image/file receive.
- `ERR-49-060`: 8.9.2 Product Workspace selected Profile callback called nonexistent `_profile_by_key` → 8.9.3 uses installed `_phase49_3i34_profile_by_key`; package CI PASS.
- `ERR-49-059`: foreground 8.9.1 startup failed because the 3I.35 AI settings panel used grid in the pack-managed Settings parent → outer panel now uses pack; 8.9.2 package CI PASS.
- `ERR-50-016`: support-weight runtime metadata mismatch tried to create fake 0040 → align runtime with migration 0039; no fake migration.
- `ERR-49-056`: Windows 8.9.1 gate had stale quick-price UI assertion + config 8.9.0 → align test/business contract and package version.

## Rollback anchors
Git:
- `backup/pre-phase49-3i38-crawl-ledger-stage-ai-20260827` → `d1ed566a82d3818aa45a5c720df3e7efcb0044f3`,
- `backup/pre-phase49-3i35-operator-ledger-20260827` → `ca9cc1160f407c0a78302ad75cb38396616aed52`,
- `backup/pre-phase49-3i35-integration-20260827` → `1b02d413be00c09631661eafaf252d011ad45d40`.

A fresh Production source/environment/MySQL backup is still mandatory before schema work.

## Exact next step
1. On `D:\projects\3DPrintHub`, verify correct repo, branch, clean worktree and live GitHub head.
2. Pull ff-only and run the current 31–38 Local gate.
3. Foreground launch Catalog Center 8.9.6.
4. Owner QA:
   - crawl/received ledger,
   - reject + purge on a disposable Product,
   - rejected Direct Link pre-download skip,
   - repeated Listing skips known identities and continues to new ones,
   - ordinary new Crawl/Direct/image/file receive remains healthy,
   - selected-Product Stage-4 SEO uses the mother AI source,
   - single-stage cleanup changes only the selected unlocked Stage,
   - locked Profile/Commerce/content rules remain intact.
5. Re-run local Django Store/Profile/Checkout regression; 3I.38 adds no Django migration.
6. Only after Local QA PASS: Host read-only branch/HEAD/worktree/live-remote/MySQL/migration-plan/disk/mysqldump audit.
7. Fresh Production source/environment/MySQL backups/checksums.
8. Deploy exact approved GitHub commit with explicit `FETCH_HEAD` per `ERR-50-007`.
9. Apply only read-only-verified pending migrations.
10. collectstatic, Passenger restart, Production HTTP/API/schema/order/private-media verification, then docs.

## Host constraints
- `ERR-50-007`: Production remote refspec is tag-only; verify live branch and explicit `FETCH_HEAD`.
- `ERR-50-010`: do not rely on cPanel `/dev/fd` process substitution.
- `ERR-50-011`: JSON is data; parse with `python -` + `json.load`.
