# PROJECT PATHS AND ENVIRONMENTS

Last Verified: 2026-08-22 from current project source-of-truth docs. Verify actual Local/Host state again before operations.

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
Canonical pre-49.3H Runner: `D:\projects\3DPrintHub\RUN_PHASE49_3G_LOCAL_GATE.ps1`

## GITHUB
Repository: `farazha2203/3dprinthub`
Development Branch: `epic/phase49-unified-product-slider-sync`
Pre-49.3H baseline: `e052829c7ed34e931f52affecd7a3b74e33dc5a1`
Delivery: GitHub-first only; no standalone chat patches/scripts.

## PRODUCTION
Project Root: `/home/sfkilvrs/3dprinthub`
Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Database Engine: MySQL
Database Name: `sfkilvrs_EmiAdmin_3dprinthub`
Static Base: `/home/sfkilvrs/public_html/static`
Media Base: `/home/sfkilvrs/public_html/media`
Private Media: `/home/sfkilvrs/3dprinthub/private_media`
Passenger Restart Pattern: `mkdir -p tmp && touch tmp/restart.txt`

## DOMAIN
Main: `https://3dprinthub.ir`

## Safety
- Do not assume `.env` paths equal these defaults; inspect runtime settings before Production.
- Do not assume Local SQLite and Production MySQL behavior are identical.
- Dirty Local worktree: STOP/INSPECT; no reset/delete shortcut.
- Before Production migration verify exact project root, branch, commit, Python venv, DB vendor/name, backup target and rollback.
