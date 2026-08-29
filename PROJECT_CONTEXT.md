# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-29  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Subphase: `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Subphase: `49.3I.40 — Commerce Precision + Offer Ownership + Readiness Truth / Catalog Center 8.9.8`  
Status: `8.9.8 BASELINE PASS / ERR-49-064 UI RECOVERED / ERR-49-065 SEO REFRESH HOTFIX GITHUB / OWNER LOCAL TEST NEXT / PRODUCTION NOT DEPLOYED`

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
- not claimed applied: `0036`, `0037`, `0038`, `0039`, `0040`.

Production remains on the stable baseline. Never infer that later migrations were applied from GitHub/CI.

## Owner SEO/readiness hotfix checkpoint — ERR-49-065

After ERR-49-064 made the professional Product Workspace visible, owner QA proved that AI-persisted Persian/SEO fields could remain shown as red/missing in cached readiness/help widgets. Source `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4` + regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26` now rehydrate from Catalog SQLite and make final readiness the last post-AI painter, with a short settle recheck. Rollback: `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`. Local targeted test/foreground retest pending; Production untouched.

## Owner visual-QA hotfix checkpoint — ERR-49-064

Canonical foreground 8.9.8 execution opened Product 63 and exposed a Tk geometry exception in the older 3I.35 wrapper before the visible 3I.39/3I.40 workspace could finish construction. The modern checkbox picker already owned the legacy material/color card with `grid`, while 3I.35 attempted to add obsolete Listbox actions with `pack`.

Hotfix source `aa37dcf916dfab71409738f7087a171daffe4a0a`, regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`, rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`. No DB/Host/Production change. Owner Local pull/test/foreground retest is the next gate.

## Approved Windows runtime candidate

Runtime/package snapshot:
`55139b909f214f33994d76bc1e6fdfd028b5d6c7`.

Catalog Center:
- version `8.9.8`,
- build `2026.08.29.2`,
- targeted 31–40 run `33247729316` PASS,
- Single Active AI run `33247815007` PASS,
- Windows Portable run `33247815027` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.8`,
- artifact ID `9713426658`,
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`,
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`.

3I.40 preserves 3I.38 acquisition behavior and adds:
- manufacturer → material → color Product Offer flow,
- filter-scoped registration that preserves other manufacturers,
- global filament stock/rates/preheat separated from Product-specific fixed price,
- exact Offer formula pricing and color image/HEX preview,
- production rows as weight/print-time/support authority,
- Profile identity/size/dimensions snapshot registration,
- readiness data defects separated from pending finalization,
- final 100% only when AI-fixable defects are zero,
- AI inputs remain Link / Saved-Crawled Data / Screenshot.

Canonical phase:
`docs/phases/PHASE49_3I40_COMMERCE_PRECISION_READINESS_TRUTH.md`.

## Approved Web/Store candidate

Phase50.A.2E now extends through:
`store.0040_phase50_filament_offer_operations`.

0040 adds:
- print hourly rate,
- supervision hourly rate,
- preheat hours/temperature/hourly cost,
- filament image URL.

Verification:
- initial `33246706102` failure was Decimal string-scale assertion only; migration plan/apply/no-drift passed,
- numeric assertion fix `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`,
- Phase50 run `33246843145` PASS,
- full CI SQLite migration through 0040 PASS,
- 21 Variant/Profile/Checkout/Offer regressions PASS.

Local owner DB state still requires fresh verification; previous Local evidence had 0039 applied. Before 0040 Local write: verify effective SQLite path, create checksum-verified backup, inspect plan, then apply/test.

Production remains untouched; only 0034/0035 are claimed applied from the last terminal audit.

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
