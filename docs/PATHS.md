# PROJECT PATHS AND ENVIRONMENTS

Last Verified: 2026-08-26 from Repository + owner Production verification. Re-verify actual Local/Host state again before operations.

## LOCAL / WINDOWS
OS: Windows / PowerShell
Project Root: `D:\projects\3DPrintHub`
Catalog Center Source: `D:\projects\3DPrintHub\catalog_center`
Venv: `D:\projects\3DPrintHub\.venv`
Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Persistent Catalog Root: `D:\projects\3dprinthub-catalog-manager`
Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Legacy Retained Data: `D:\projects\3dprinthub_catalog_center`
Backups: `D:\projects\3dprinthub-backups`
Runtime Logs: under persistent Catalog data root, including `logs\phase49_3f\YYYY-MM-DD\workflow-*.jsonl`
Canonical validated pre-49.3I Runner: `D:\projects\3DPrintHub\RUN_PHASE49_3H_LOCAL_GATE.ps1`

## GITHUB
Repository: `farazha2203/3dprinthub`
Active Development Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Admin V2 CI-tested runtime snapshot: `3687d0922959fca53f2118be6dacd32639159346`
Delivery: GitHub-first only; no standalone chat patches/scripts and no permanent direct Production source edits.

## PRODUCTION
Project Root: `/home/sfkilvrs/3dprinthub`
Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Database Engine: MySQL
Database Name: `sfkilvrs_EmiAdmin_3dprinthub`
Static Base: `/home/sfkilvrs/public_html/static`
Media Base: `/home/sfkilvrs/public_html/media`
Private Media: `/home/sfkilvrs/3dprinthub/private_media`
Passenger Restart Pattern: `mkdir -p tmp && touch tmp/restart.txt`
Current verified Production application commit: `bc7b97f9c63432b8105f52f61cf5cdae1369689b`
Latest verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`

## PRIVATE / PURCHASED ADMIN ASSETS
Velzon vendor assets are expected privately at runtime under `static/velzon_master/` and are intentionally gitignored in the public Repository. Public GitHub stores only project-owned Django/Velzon adapter CSS/JS/templates. Do not infer absence on Production from absence in the public Git tree; verify runtime/static files on the target host when relevant.

## DOMAIN
Main: `https://3dprinthub.ir`

## Safety
- Do not assume `.env` paths equal these defaults; inspect runtime settings before Production.
- Do not assume Local SQLite and Production MySQL behavior are identical.
- Dirty Local/Host worktree: STOP/INSPECT; no reset/delete shortcut.
- Before Production migration verify exact project root, branch, commit, Python venv, DB vendor/name, backup target and rollback.
- Current Production Git remote-tracking branch may be stale because `remote.origin.fetch` historically tracked only tag `v0.33.0`; per `ERR-50-007`, verify live branch with `git ls-remote` and explicitly fetch the branch to `FETCH_HEAD` before ff-only deploy unless refspec is deliberately corrected.
