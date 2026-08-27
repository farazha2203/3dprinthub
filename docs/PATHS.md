# PROJECT PATHS AND ENVIRONMENTS

Last Verified: 2026-08-27 from Repository + prior owner Production verification. Re-verify actual Local/Host state again before operations.

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
Canonical current Local gate: `D:\projects\3DPrintHub\catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1`

## GITHUB
Repository: `farazha2203/3dprinthub`
Active Development Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Admin shell CI runtime: `27335832e90c35dd95bb8a686dd89d1efd46dc8f`
Current Store/Profile/Filament CI runtime: `d519a360e65b79db4b62af206b95f63c3539bc12`
Current Store/Profile/Filament CI run: `33059883188` PASS
Current Windows packaged runtime: `8d5e58a839c89eedbe258d9236889834fc02d9a9`
Catalog Center: `8.9.5` / build `2026.08.27.7`
Windows artifact ID: `9647216177`
Windows EXE SHA256: `4a3e15a3c475460c2dac035cedcd8ccebb40107fec6360b7be6a313f69186079`
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
