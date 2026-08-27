# PROJECT_CONTEXT — 3DPrintHub

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Subphase: `50.A.2D — Product Profile Matrix + Dependent Storefront Selector`  
Parallel Windows Subphase: `49.3I.34 — Step-2 Product Profile Matrix / Catalog Center 8.9.0`  
Status: `GITHUB CI TESTED / WINDOWS PACKAGED CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`

## Operating rule
GitHub is permanent source of truth.

`READ DOCS → VERIFY REAL STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → UPDATE DOCS`.

No permanent Production source edits. Dirty Local/Host worktree means STOP/INSPECT.

## Canonical paths
Windows project: `D:\projects\3DPrintHub`  
Windows venv: `D:\projects\3DPrintHub\.venv`  
Catalog persistent DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`

Production root: `/home/sfkilvrs/3dprinthub`  
Production venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`  
Production DB: MySQL `sfkilvrs_EmiAdmin_3dprinthub`.

## Production baseline
Current verified Production app commit remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Latest verified rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

Last verified new-Phase50 migration state:
- applied: `store.0034`, `store.0035`,
- pending: `store.0036`,
- `store.0037` and `store.0038` were created after that Production verification and are therefore not claimed applied.

## Current Windows candidate — 49.3I.34
Catalog Center:
- version `8.9.0`,
- build `2026.08.27.2`,
- packaged snapshot `b3280dd67cd7772f337f6792036ea92d3f252747`,
- Windows workflow `33051114515` PASS,
- artifact ID `9637671099`,
- EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`.

Step 2 now owns a Product Profile Matrix:
- add/clone/delete/edit Profile,
- independent size, weight, price, time, actual part dimensions, build, material, color, quality, package and inventory settings,
- Profile JSON persists locally and travels through the existing batch/import boundary,
- profile/range minimum price satisfies mature publish readiness,
- existing source identity/AI/performance contracts remain preserved.

## Current Web candidate — 50.A.2D
Runtime snapshot:
`7d0a2a1125e8f38771ba325427d1efa8b8d07da6`.

Store/Profile CI:
`33051311828` PASS.

Key runtime:
- Desktop Profile rows idempotently upsert canonical ProductVariant rows,
- manual non-Desktop Variants are preserved,
- Product/Profile fixed-price policy uses canonical `ProductVariant.price_breakdown()`,
- customer hierarchy supports size→weight and configured deeper modes,
- each downstream choice is filtered only by previously selected upstream dimensions,
- weight/profile price badges are scoped to the active size/prefix,
- selected Profile is the Product detail price/facts authority,
- summary includes price, description, size, build, material, color, quality, final/shipping weight, part dimensions, print time and package dimensions,
- native Variant select remains fallback,
- duplicate material selector is not rendered beside canonical Profile selection.

CI proves:
- JS syntax,
- `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- Django check,
- no migration drift,
- migrations through `store.0038`,
- 15 Variant/Profile/Checkout regressions.

## Pending DB chain
Production must verify and then, only if still pending, apply:
`0036_phase50_checkout_snapshot → 0037_phase50_professional_commerce_policy → 0038_phase50_profile_matrix`.

A fresh MySQL/source/environment backup is mandatory before applying any of them.

## Host-specific constraints
- `ERR-50-007`: tag-only Host fetch refspec → live `ls-remote` + explicit branch fetch to `FETCH_HEAD` + ff-only.
- `ERR-50-010`: avoid cPanel `/dev/fd` process substitution.
- `ERR-50-011`: JSON smoke payload is data; parse with `python -` + `json.load`.

## Current corrected incidents
- `ERR-50-012`: execute callable Variant pricing contract in API.
- `ERR-50-013`: shipping policy resolves selected saved-address facts.
- `ERR-50-014`: prefix-only Profile hierarchy + size-scoped option prices.
- `ERR-50-015`: Windows release workflow watches mature Product studio files.

## Immediate next work
1. Pull exact current GitHub head onto clean canonical Windows checkout.
2. Run `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` with exact HEAD and `-LaunchApp`.
3. Owner QA multi-size/multi-weight Profile add/clone/edit/save/reopen.
4. Local Django regression and local SQLite migration only.
5. If Local PASS, run fresh read-only Host/MySQL audit.
6. Fresh backups.
7. Deploy exact approved GitHub commit via `FETCH_HEAD`, apply only verified pending `0036 → 0037 → 0038`, collectstatic/restart/verify.
8. Update Production documentation with exact deployed SHA, migration rows and backup path.
