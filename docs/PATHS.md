## Phase49.3I.53B Host evidence — 2026-09-02
Verified Host project Python: `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`.
System `python3`: unavailable in the login shell.
Actual read-only Host HEAD observed: `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.
Untracked Host evidence currently blocking clean-worktree gate: `/home/sfkilvrs/3dprinthub/ls-output.txt`; SHA256 `8e01c07fcdf242fdc9be7de5a3a9b86cd7f0244e37ace629bc22d10ac1bee738`.
Updated audit runner contract: `scripts/host/phase49_3i53_production_readonly_audit.sh <target-sha> <verified-host-head>`.

## Phase49.3I.53 Site/Host paths — 2026-09-02
Production read-only audit runner in Repository: `scripts/host/phase49_3i53_production_readonly_audit.sh`.
Site receiver readiness endpoint after deploy: `https://3dprinthub.ir/api/catalog-bridge/v1/publish-readiness/`.
The runner is executed from the verified GitHub commit without permanently editing Production source during the audit.

Current 3I.53 final code checkpoint: `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`.
Current 3I.53 Site/Product Admin run: `33652584032` PASS.
Current 3I.53 Qt run: `33653229142` PASS.
Current 3I.53 Portable run: `33653229400` PASS.
Current Windows packaged runtime: `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`.
Windows artifact ID: `9855771656`.
Windows EXE SHA256: `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`.

# PROJECT PATHS AND ENVIRONMENTS

Last Verified: 2026-09-02 from Repository + GitHub Actions + prior owner Production verification. Re-verify actual Local/Host state again before operations.

## LOCAL / WINDOWS
OS: Windows / PowerShell
Project Root: `D:\projects\3DPrintHub`
Catalog Center Source: `D:\projects\3DPrintHub\catalog_center`
Mature Tk Launcher: `D:\projects\3DPrintHub\catalog_center\launch.py`
Parallel Qt6 Preview Launcher: `D:\projects\3DPrintHub\catalog_center\qt_launch.py`
Qt6 Presentation Package: `D:\projects\3DPrintHub\catalog_center\qt6`
Qt6 Preview Requirements: `D:\projects\3DPrintHub\catalog_center\requirements-qt6.txt`
Venv: `D:\projects\3DPrintHub\.venv`
Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Persistent Catalog Root: `D:\projects\3dprinthub-catalog-manager`
Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Canonical downloaded Product images: `D:\projects\3dprinthub-catalog-manager\collected\<source_code>\<external_id>\images`
Canonical finalized SEO images: `D:\projects\3dprinthub-catalog-manager\collected\<source_code>\<external_id>\seo_images`
Historical mature refetch folders below the same Source directory: `<external_id>_refresh_latest`, `<external_id>_refetch_<timestamp>`, `<external_id>_bulk_refetch_<timestamp>` (read-only image compatibility)
Legacy Installed Application Root (retained/read-only fallback): `D:\projects\3dprinthub_catalog_center`
Backups: `D:\projects\3dprinthub-backups`
Runtime Logs: under persistent Catalog data root, including `logs\phase49_3f\YYYY-MM-DD\workflow-*.jsonl` and acquisition diagnostics `logs\acquisition\acquisition-YYYY-MM-DD.jsonl`
Canonical validated pre-49.3I Runner: `D:\projects\3DPrintHub\RUN_PHASE49_3H_LOCAL_GATE.ps1`
Canonical current Local gate: `D:\projects\3DPrintHub\RUN_PHASE49_3I42C_LOCAL_GATE.ps1` (`49.3I.52.2`)
Crawl ledger continuation table: Catalog SQLite `crawl_listing_state` (additive; mature `discovered_urls` remains identity ledger)
Rejected Product physical purge boundary: only under persistent Catalog `collected\` root; source URL/external ID tombstone stays in Catalog SQLite.

## GITHUB
Repository: `farazha2203/3dprinthub`
Active Development Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current 3I.52G runtime/CI checkpoint: `bf1fafdb38233a23e13a5715ffac72f772412005`
Current 3I.52G Qt run: `33644903042` PASS
Current 3I.52G Portable run: `33644902962` PASS
Current Admin shell CI runtime: `27335832e90c35dd95bb8a686dd89d1efd46dc8f`
Current Store/Profile/Filament CI runtime: `d519a360e65b79db4b62af206b95f63c3539bc12`
Current Store/Profile/Filament CI run: `33059883188` PASS
Current Windows packaged runtime: `bf1fafdb38233a23e13a5715ffac72f772412005`
Catalog Center: `8.9.10` / build `2026.09.02.1`
Windows artifact ID: `9852476786`
Windows EXE SHA256: `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`
Last owner Local automated gate: PASS at local head `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`; Local Django SQLite is through `store.0039`; backup `D:\projects\3dprinthub-backups\phase49-3i35-resume-20260827-142404\django-local-before-0039.sqlite3`.
Delivery: GitHub-first only; no standalone chat patches/scripts and no permanent direct Production source edits.

## PRODUCTION
Project Root: `/home/sfkilvrs/3dprinthub`
Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Python: 3.12.13
Django: 6.0.7
Database Engine: MySQL
Database Name: `sfkilvrs_EmiAdmin_3dprinthub`
Static Base: `/home/sfkilvrs/public_html/static`
Media Base: `/home/sfkilvrs/public_html/media`
Private Media: `/home/sfkilvrs/3dprinthub/private_media`
Passenger Restart Pattern: `mkdir -p tmp && touch tmp/restart.txt`
Current verified Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`
Latest verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`
Previous incomplete pre-deploy audit backup retained for evidence: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143245`

## PRIVATE / PURCHASED ADMIN ASSETS
Velzon vendor assets are expected privately at runtime under `static/velzon_master/` and are intentionally gitignored in the public Repository. Production verification confirmed required Bootstrap RTL, app RTL, layout.js and Bootstrap bundle files are present. Public GitHub stores only project-owned Django/Velzon adapter CSS/JS/templates.

## DOMAIN
Main: `https://3dprinthub.ir`

## Production Git caveat
The current Host `remote.origin.fetch` still tracks only `+refs/tags/v0.33.0:refs/tags/v0.33.0`; normal `git fetch origin` does not update the active branch remote-tracking ref. Per `ERR-50-007`, verify the live branch with `git ls-remote` and explicitly fetch `refs/heads/agent/phase49-3i18-operator-bulk-ai-rebuild` to `FETCH_HEAD`, then verify SHA/ancestry and use ff-only merge.

## Production shell caveat
This cPanel environment did not provide a reliable `/dev/fd` path for Bash process substitution during deployment backup. Per `ERR-50-010`, avoid `< <(...)` in Production deployment scripts; use the Production Python runtime or portable temporary-file approaches for enumeration/copy operations.

## Safety
- Do not assume `.env` paths equal defaults; inspect runtime settings before Production operations.
- Do not assume Local SQLite and Production MySQL behavior are identical.
- Dirty Local/Host worktree: STOP/INSPECT; no reset/delete shortcut.
- Before Production migration verify exact project root, branch, commit, Python venv, DB vendor/name, backup target and rollback.
- JSON/API smoke payloads are data, not executable source; use `python - <args>` and explicit `json.load` when verifying endpoint responses.
