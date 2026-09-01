# Current continuation — 2026-09-01 / Phase49.3I.47 + ERR-49-088

Repository authority: `farazha2203/3dprinthub`  
Active development branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Exact Windows-CI-tested source: `36a710953276aae99fa668f477ad5569f8dc23ba`  
Owner Local gate: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` / `49.3I.47.2`  
Production: NOT TOUCHED.

Current owner gate:
- rerun 3I.47 Local acceptance after ff-only pulling the final documentation head;
- verify Product lifecycle workspaces, local thumbnails, sequential multi-select AI, all-image SEO numbering/metadata, Acquisition gallery/details workspaces and Profile/Pricing tabs;
- no Host/Production work before explicit owner acceptance.

Windows runner incident:
- ERR-49-088 fixed one non-ASCII line that broke Windows PowerShell 5.1 parsing;
- CI now enforces ASCII bytes + Windows PowerShell 5.1 parsing;
- Qt full parity run `33511403943` PASS; Single Active AI `33511403901` PASS.

Design authority:
- `docs/PROFESSIONAL_COMMERCE_DESIGN_ARCHITECTURE.md` is the current source-grounded standard for Storefront/Admin/Catalog Center IA, Persian typography, layout, effects, accessibility, SEO, performance and optional 3D presentation;
- current Django architecture remains authoritative.

---

# PROJECT_CONTEXT — 3DPrintHub

## Continuation checkpoint — 2026-09-01 / ERR-49-086 / Phase49.3I.46

Executable code checkpoint `a659155da4a4a41e01e926b2ac1263a1756c24e6` introduces real bounded Product/Crawl reads and restores the mature pre-Qt acquisition operator surface through the Qt Core boundary.

Current paging contract:
- Product Gallery 50 at a time;
- Product Table/Detail 20 at a time;
- Crawl inventory 100 at a time;
- more rows load incrementally on scroll;
- Product list SQL uses lightweight list columns instead of full Product payloads.

Restored acquisition choices/actions include Classic Isolated/Exact, Network Capture, Chrome Attached 9222, Saved HTML, Browser DOM/Public HTTP compatibility, normal manual Chrome profile, multi-source harvest, optional public file download and Source Refresh that preserves Persian/editorial/pricing decisions.

Windows evidence: `33500317538`, `33500317554`, `33500317788` PASS.
Rollback: `backup/pre-phase49-3i46-catalog-lazy-acquisition-parity-20260901`.
Production/Host/Django migrations untouched. Owner Local real-Catalog acceptance is next.


## Continuation checkpoint — 2026-08-31 / ERR-49-082

Code checkpoint `0421bccff040ced53513625af95d05e0c8c27a9a` fixes the owner-observed OpenRouter model-selection failure: media/music and tools-only coding models can no longer masquerade as Product Structured models. OpenRouter Product calls now require strict JSON Schema + compatible endpoints, and Product execution requires a verified saved model capability profile.

CI: `33399095190` Qt/Crawl/AI PASS; `33399095198` Single Active AI PASS; `33399095224` Windows Portable PASS.

Rollback: `backup/pre-err49-082-openrouter-product-model-gate-20260831` → `26761c81d04bbd74dc2c978b08e77f3250b0518b`.

Next: owner Local canonical gate, reload OpenRouter catalogue, select Product-safe Text + JSON✓ model, retest Product #309 Link/Data. Production/Host untouched.


## Continuation checkpoint — 2026-08-31 / Phase49.3I.42C3

Current code checkpoint: `ba3d1358d91aa78719f618630c290abf97ee8427`.
Qt Add Product/Crawl legacy parity plus AI Provider model ranking, pricing, structured Product probe, cost confirmation and diagnostic dialogs are implemented.

Windows evidence:
- `33394215803` Qt6 Crawl + AI Runtime CI PASS;
- `33394215742` Single Active AI CI PASS.

Next exact task is owner Local ff-only pull + repository-owned 42C gate + bounded foreground QA. Production/Host/Django migrations remain untouched.


## Continuation checkpoint — 2026-08-31 / Phase49.3I.42C

Qt acquisition code checkpoint: `3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`.

Qt Operations now has live Classic + Hybrid acquisition. Classic preserves the old owner workflow: give one Search/Listing URL, persist crawl state, skip terminal identities and continue deeper on later runs. Hybrid uses the mature 3I.43–45 robots-aware pooled HTTP/Sitemap/cache/freshness/unseen path and falls back to Playwright only when needed. Direct single-Product rich receive and bounded image receive are also active.

The code checkpoint passed Windows Qt/full-parity, portable and Single Active AI checks. Owner Local on exact `3f7038b...` passed repo/live-head, checksum-backed Catalog SQLite backup and dependency verification. It stopped before tests because the pasted multi-line Playwright `python -c` probe was corrupted by PowerShell/native quoting (ERR-49-081), not because of crawler/Chromium failure.

Canonical owner runner is now:
`RUN_PHASE49_3I42C_LOCAL_GATE.ps1`.

Gate implementation:
- `71c55010bc900e8d3c1afd7cea71441193db68eb`;
- CI stdin/syntax guard `e6980fcfb2bdc72846e007e9d935290225dcb39e`; Phase49.3I.42C Windows run `33386654632` PASS.

Rollback:
`backup/pre-phase49-3i42c2-pagination-crawl-intelligence-20260831` →
`3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`.

Next exact task: ff-only pull final GitHub head, run the repository-owned gate with `-LaunchApp`, then bounded 5-Product Classic twice on one Search URL and one 5-Product Hybrid run. Production/Host untouched.


## Continuation checkpoint — 2026-08-31 / Phase49.3I.42B2

Executable Qt source checkpoint: `c3b0105eaa6c6141eb6d6d8463a96d547101564c`.
Windows full-parity CI `33369749205` PASS; Single Active AI `33369749123` PASS.

Qt now has requested Product/Filament/Profile/Image/SEO/Source/Slider/AI Provider/Connection parity. One shared ApplicationKernel/AICore owns the Qt composition. This 42B2 checkpoint is superseded for Operations by Phase42C, where live Classic/Hybrid acquisition controls are now implemented. Legacy launcher is still the default fallback; owner Local foreground QA is mandatory before cutover. Production/Host untouched.


## Active continuation checkpoint — 2026-08-30

Windows Qt modernization is now at Phase49.3I.42B1. Source checkpoint `0b826dccabcb3d98d5f5b4cca6543d7547ff8773` adds the object-oriented ApplicationKernel/CoreRegistry, Product gallery/local image parity and the first real Stage-1 edit adapter. Qt CI `33319343447` and Single Active AI `33319343464` are PASS. Production remains untouched. Next exact task is owner Local 42B1 QA, then 42B2 complete Stage-2 Filament/pricing/Profile parity.


Updated: 2026-08-30  
Repository: `farazha2203/3dprinthub`  
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Epic: `Phase50 — Finance, Commerce & Admin Command Center`  
Current Web Subphase: `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
Parallel Windows Subphase: `49.3I.42C — Qt6 Acquisition Controls + 49.3I.45 Incremental Discovery Intelligence`  
Status: `QT42C CLASSIC+HYBRID CODE WINDOWS CI PASS / ERR-49-081 LOCAL GATE FIXED / OWNER FOREGROUND QA NEXT / PRODUCTION NOT DEPLOYED`

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

## Current owner checkpoint — Phase49.3I.45

Latest executable/source checkpoint:
`846cb63038a79cfe450f5a60aa66e531cf6fe0de`.

The newly supplied GUI/FastAPI/web-scraping references were reviewed. Current official documentation was used to reject outdated framework-specific advice where appropriate.

3I.45 extends the already-tested 3I.43/44 acquisition layer with:
- incremental Sitemap metadata;
- newest Sitemap prioritization;
- unseen Product prioritization;
- persistent discovery observation history;
- generic custom-source model-path Sitemap discovery.

Windows CI `33313008595` PASS; Single Active AI `33313008558` PASS.

No Production/Host/Django migration change. New Catalog table is local additive metadata only.

Rollback:
`backup/pre-phase49-3i45-book-driven-discovery-intelligence-20260830` →
`3616bf222f394b769cb2e3198164d735fca5267b`.

Active phase:
`docs/phases/PHASE49_3I45_INCREMENTAL_DISCOVERY_INTELLIGENCE.md`.

Next: owner Local backup/regression/foreground acquisition QA.

## Current owner checkpoint — Phase49.3I.42

A parallel PySide6/Qt6 desktop presentation layer now exists and is Windows-CI tested. It applies the purchased PyQt5 reference patterns—QMainWindow, signals/actions, Model/View, QStackedWidget wizard, QSplitter, QSS, QSettings and thread-pool workers—without replacing the mature Tk business runtime.

Dedicated Qt run `33299745502` PASS. Legacy launcher remains the default and passes its verify gate. No Production/Host/DB migration change.

Next owner gate: run the repository-owned Phase49.3I.42C Local gate, then bounded Classic/Hybrid real-source QA. Legacy remains available side by side until 42E cutover.

Active phase: `docs/phases/PHASE49_3I42_QT6_DESKTOP_MODERNIZATION.md`.

## Current owner checkpoint — Phase49.3I.41

The final Stage-2 UX now separates global Filament master data from Product assignment. Main Catalog Center owns a reusable grouped Filament Library; each Product owns a one-click checklist and a separate selected-Filament pane. Save/update/deactivate is synchronized through the existing authenticated Site Bridge into the canonical Store MaterialColorOption entity.

No new migration. Existing `store.0039/0040` are required on the Site before the new Bridge contract can run. Production is untouched and still requires Host read-only migration verification/backups.

Rollback: `backup/pre-phase49-3i41-filament-library-sync-20260829` → `92a3f4dfcf64d5fedaf837eb9a37dac028cabd59`.

Active phase: `docs/phases/PHASE49_3I41_FILAMENT_LIBRARY_SITE_SYNC.md`.

## Current owner checkpoint — ERR-49-075

Owner screenshots proved the final Stage-2 defects: saved Filament hidden by old filter, stale edit dialog, and zero/stale price preview. Root causes are now fixed at DB hydration + final callback + pricing-context boundaries. No schema/migration/Host/Production change. Rollback: `backup/pre-err49-075-filament-refresh-pricing-preview-20260829` → `d66c68f36d1fd3e4143d461bccd999046c4baaf7`.

One short Local QA remains. If it passes, website receive/sync becomes the active work immediately.

## Current owner checkpoint — ERR-49-074

Owner exact `954c051...` passed the ERR-49-073 Local gate: backup/checksum, compile, 2/2 exact image regressions, 4/4 OpenRouter-only, 73/73 full Windows stage suite and foreground QA. Image Metadata refresh is accepted fixed and the Product reached ready-for-publication state locally.

Current GitHub delta restores the missing continuously visible Stage-2 final price/rate and changes operator-facing `Offer` wording to `Filament`. Internal `offer_*` compatibility identifiers stay unchanged. No schema/migration/Host/Production change. Rollback: `backup/pre-err49-074-filament-rate-final-display-20260829` → `954c0516661e6c70145d7f6f395b4e92ceeb40bd`. Local retest is next; then website receive/sync.

## Current owner checkpoint — ERR-49-073

Owner exact `6d5897e...` passed the repaired Local gate: 7/7 exact regressions, 4/4 OpenRouter-only, 71/71 full Windows stage regression, then foreground launch. Stage confirmation is functioning except for the Images Metadata refresh loop. Root cause is derived image signatures being blocked by the already-confirmed image Stage lock after later Content/Source facts change. GitHub now permits only deterministic finalizer-owned image fields to refresh through the lock, finalizes on Stage-3 confirm and allows a confirmed Images Stage to refresh without unlock. Production untouched.

## Current owner checkpoint — ERR-49-072

Owner Local `34c65bc...` passed repo verification, backup and compile, then the new exact ERR-49-071 suite stopped on a test-only clean-schema omission: `price_min` was absent because the fixture did not initialize the real Epic49 desktop + 3F pricing schema layers. Fix `1307f4c438de184a930041d365976c2ce018bff8` aligns the fixture with ProductWorkspace construction. Production untouched; Local rerun is next.

## Current owner checkpoint — ERR-49-071
ERR-49-071 executable code/regression checkpoint: `6085ea70d1075c5a1abaca4b4b2efdebe1254829`. No current-head Actions run is attached; Local compile/regression/foreground acceptance is next.


Owner exact `d4da997...` achieved compile PASS, exact ERR-49-070 PASS, OpenRouter-only 4/4 PASS and 67/67 Windows stage PASS, but foreground visual QA still failed. The real cause is now isolated to final operator semantics/composition: confirmation was mixed into missing-data counts, green icons followed data fill instead of explicit approval, a deliberate `سایر محصولات` category was rejected, bad Stage-1 relocation UI was mounted, and the legacy Next/title-only Tk callbacks survived final composition.

Current GitHub delta restores historical stage layout, separates data defects from confirmation, creates an independent permanent `✅ ثبت و تأیید مرحله →` action and rebinds title-only AI into the global OpenRouter runtime guard. Rollback: `backup/pre-err49-071-stage-confirm-rollback-20260829` → `d4da99744659d06ebe5c04fd69532cd0e03db3e8`. Production untouched.

## Current owner checkpoint — ERR-49-070

Owner Local `382a34f...` passed compile and OpenRouter-only 4/4, then the 67-test Windows gate correctly stopped before launch. Clean Catalog SQLite lacked `technical_summary_fa`, and the Stage-5 builder names wired by 3I.39 had no actual implementations. GitHub now adds the clean schema column, real Stage-5 source/license/technical panel + hydration, visible Persian license persistence and focused regressions.

Rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`. Production untouched. Owner Local rerun is next.

## Current owner checkpoint — ERR-49-069

Owner Local exact `3f43260...` evidence is now: canonical repo/branch verified, fresh Catalog SQLite backup with SHA256 `5A6DB948ADACA81014DEDFA7FF117A0C4AF26364936575ACB15D21D632D4C321`, compile PASS, 60/60 focused tests PASS and foreground 8.9.8 launch PASS. The real UI still failed because a previously captured deferred Wizard refresh repainted the final footer, Stage ownership controls were split, scoped AI counted global defects, multiple Product AI jobs overlapped, and AvalAI remained an automatic fallback despite OpenRouter being active.

Executable hotfix `136011971dea907ac777b3e66190dd27982a0c38` now makes the footer/persist path authoritative even under late callbacks, restores complete Stage-1/5 visible ownership/persistence, makes single-stage AI Scope-aware, serializes Product AI jobs, and makes Product AI OpenRouter-only with optional same-Provider `openrouter/free` fallback.

Rollback: `backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`. No schema/Host/Production/media/secret-value change. Owner Local regression and foreground QA are next.

## Current owner checkpoint — ERR-49-068

Owner Local `0191a07...` gate now has strong evidence: the exact formerly failing test PASSed, the focused 43-test set PASSed, and the canonical foreground 8.9.8 runtime launched. Real Product 63 still exposed the Windows stage-confirmation defect. Manual/current UI values could be persisted by a later global Save, but the normal Stage workflow checked persisted readiness before a visible current-stage persist/confirm action, so it did not naturally become green/advance.

GitHub now restores a fixed bottom `✅ تأیید و مرحله بعد` path that persists/finalizes the current Stage first; adds adjacent AI fill/edit controls; keeps that footer authoritative across refreshes; rebinds actual legacy Tk callbacks to 3I.39; accepts exact source identity in Persian SEO; blocks cross-provider key/model reuse; and fixes the deferred exception closure.

Rollback: `backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`. New Local focused regression and foreground Product 63 QA are pending. Production untouched.

## Latest owner checkpoint — ERR-49-067

Owner Local gate on `9f3b765...` verified the canonical checkout, created a checksum-verified Catalog SQLite backup, passed compile, and ran 43 focused tests. One stale locked-stage fixture failed because its mock SEO description contained Latin `AI`, violating the newly explicit Persian-only SEO contract. Runtime behavior was not relaxed; fixture-only correction is `38cb415bc12d7ec08943809fd14f3478b3ddac1b`. Foreground launch did not run. Owner rerun is next; Production untouched.

## Current owner checkpoint — ERR-49-066

The owner completed the ERR-49-065 pull/test/foreground run: exact Local head matched `c679c66...`, 12 targeted tests passed, and the correct 8.9.8 runtime opened. Real Product 63 still failed readiness. Audit showed checker/stage/fixer disagreement and a legacy full-AI entrypoint bypass.

GitHub now aligns title/Alt/Content ownership, persisted Persian/source-identity validation, AI repair eligibility, data-ready Wizard progress and final 3I.39 AI entrypoint authority. Rollback: `backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`. Current-head Local regression and foreground QA are pending; Production untouched.

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
