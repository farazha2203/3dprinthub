# CURRENT PROJECT STATE

## Continuation checkpoint — 2026-08-31 / ERR-49-082 OpenRouter Product Model Gate

Owner Local QA exposed a real model-selection/Structured-output defect after 42C3. The connection itself was healthy; inappropriate OpenRouter models were being accepted for Product work.

Final code checkpoint:
`0421bccff040ced53513625af95d05e0c8c27a9a`.

Fixed:
- media/audio/music/image/embedding/rerank models are excluded from Product model filters;
- Tools-only is no longer treated as Structured JSON;
- coding-specialist models are not recommended/accepted for Product Persian SEO/content;
- OpenRouter Product calls require strict JSON Schema + compatible endpoint parameters;
- prompt-only JSON fallback is disabled for OpenRouter Product Structured calls;
- verified model capability profile is persisted without secrets and required before Product AI estimate/execute;
- settings labels clearly expose Product-safe / JSON✓ / Tools-only / coding / non-text status.

Verification:
- Qt/Crawl/AI `33399095190` PASS;
- Single Active AI `33399095198` PASS;
- Windows Portable `33399095224` PASS.

Rollback:
`backup/pre-err49-082-openrouter-product-model-gate-20260831` → `26761c81d04bbd74dc2c978b08e77f3250b0518b`.

Exact next task:
owner Local clean ff-only pull of the final documentation HEAD, run the canonical 42C Local gate, then in Settings reload OpenRouter models, choose a Product-safe Text + JSON✓ model, run the Persian+JSON probe, save it, and re-run Product #309 Link/Data AI. Production remains untouched.


## Continuation checkpoint — 2026-08-31 / Phase49.3I.42C3 Add Product + AI Crawl parity

Source/code checkpoint: `ba3d1358d91aa78719f618630c290abf97ee8427`.

Requested legacy parity now present in Qt:
- explicit main route `افزودن محصولات / Crawl`;
- Add Product modes: Automatic, Search/Listing, Category URL, Site Crawl and Direct Product;
- preserved Classic Search-Link + browser continuation and stronger Hybrid structured-first discovery;
- source/query/start-URL, Product limit, per-Product image limit, image-download option, retry/reset/progress/run history;
- rich Product receive into the existing Catalog authority;
- one shared `AICore` / exact saved Provider+Model+secure key; no page-specific AI engine;
- live Provider model catalogue with free/Persian/Structured filters, provider pricing display and internal Persian suitability ranking;
- estimated per-run AI cost confirmation before stage/all-content execution;
- real Persian + structured Product JSON probe instead of connection-only success;
- diagnostic dialogs with Provider/Model/Product/Stage/Source context and copyable detailed error text.

Verification on exact code HEAD:
- `33394215803` — Phase49.3I.42C3 Qt6 Crawl + AI Runtime CI — PASS;
- `33394215742` — Phase49.3I.17 Single Active AI CI — PASS.

Safety:
- Django migration changed = NO;
- Production/Host touched = NO;
- default launcher changed = NO;
- Catalog authority remains the existing SQLite/database contracts;
- no CAPTCHA/auth/proxy bypass added.

Exact next task:
owner Local clean ff-only pull of the final documentation HEAD, run `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -LaunchApp`, then bounded foreground QA for Add Product/Crawl and OpenRouter structured Product execution. Do not deploy before owner Local acceptance.


Updated: 2026-08-31  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Primary Web/Commerce Release: `Phase50.A.2E + Phase49.3I.41 Bridge Extension — Central Filament Library Sync`  
Parallel Windows Track: `Phase49.3I.42C3 — Qt6 Add Product/Crawl parity + AI Provider diagnostics over 42C/3I.43–45`  
Status: `ERR-49-082 OPENROUTER PRODUCT MODEL GATE WINDOWS CI+PORTABLE PASS / OWNER LOCAL RETEST NEXT / PRODUCTION NOT TOUCHED`

## Current Windows Qt acquisition checkpoint — Phase49.3I.42C

Executable acquisition checkpoint:
`3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`.

Operational Local-gate commits:
- `71c55010bc900e8d3c1afd7cea71441193db68eb` — repository-owned guarded Local runner;
- `e6980fcfb2bdc72846e007e9d935290225dcb39e` — Windows CI syntax + Python-stdin guard; run `33386654632` PASS.

Implemented in Qt Operations:
- active Source selector;
- Listing/Search batch mode and direct single-Product mode;
- explicit Strategy selector:
  - `classic` = preserved old Search-Link + browser continuation path;
  - `hybrid` = structured-first HTTP/Sitemap intelligence with browser fallback only when needed;
- requested Product count and per-Product image cap;
- retry-failed option;
- start, safe-stop, failed-queue reset and refresh controls;
- worker-thread progress/status without blocking the Qt event loop;
- permanent queue/run history;
- rich Product receive into the existing Catalog authority.

Classic mode deliberately preserves the owner's mature behavior: the same Search/Listing URL is persisted in crawl state and later runs deepen browser discovery while terminal identities are skipped. The regression proves the first pass can collect `1001/1002` and the next pass over the same URL advances to `1003/1004`.

Hybrid mode reuses 3I.43–45:
`robots → pooled conditional HTTP → Sitemap/freshness/unseen ranking → structured HTML/JSON-LD/embedded data → DOM → Playwright fallback → mature source-specific fallback`.

Rich Product extraction persists source title/description, author, license, source category/tags/specs, source snapshot and selected image facts while respecting the requested image cap.

Verification already completed on the 42C code checkpoint:
- Qt/full-parity Windows job on `3f7038b...` PASS;
- Windows portable job on `3f7038b...` PASS;
- Single Active AI job on `3f7038b...` PASS;
- classic continuation, hybrid browser-avoidance, rich receive, listing-scoped queue and classic robots-denial regressions are present.

Owner Local evidence on exact `3f7038b...`:
- repository/branch/live HEAD guard PASS;
- checksum-backed Catalog SQLite backup PASS;
- Python/dependency verification PASS;
- Local gate stopped before compile/tests only because of ERR-49-081 runbook quoting, not application code.

Rollback:
`backup/pre-phase49-3i42c2-pagination-crawl-intelligence-20260831` →
`3f7038b52723aa2b70cd12d4c1a617c50d0ad4d8`.

Exact next task:
pull the final GitHub head ff-only, run `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -LaunchApp`, then do bounded foreground QA: Classic with 5 Products twice on the same Search URL, then Hybrid with 5 Products. Production/Host/Django migrations remain untouched.

## Current Windows Qt checkpoint — Phase49.3I.42B2

Requested Product/Settings parity is implemented on the shared Qt kernel without replacing mature Catalog/AI/Filament/Profile/Stage authorities.

Executable/source checkpoint:
`c3b0105eaa6c6141eb6d6d8463a96d547101564c`

Implemented:
- Product gallery + sortable table with Persian title, original/source title and description;
- site category QComboBox plus custom category persistence;
- reusable Filament CRUD with manufacturer/brand/material/color/multicolor, stock, roll/rate, hourly and preheat facts;
- Profile Matrix with one size/profile × multiple production rows (part weight + support weight + print time) × many Filaments/colors/prices;
- Product-specific fixed Filament pricing plus dynamic/range pricing contracts;
- image selection/primary preview with pixel dimensions, file size and SEO metadata visibility;
- complete Persian Content/SEO editor;
- Source/author/license/commercial status/specification editor;
- complete Product-local homepage slider controls;
- seven-stage readiness truth: red cross = missing, pending marker = data-ready/unconfirmed, green check = finalized;
- one process-wide object-oriented `AICore`, reusing exact saved Provider/Model/key and mature Link/Saved Data/Screenshot source modes;
- Provider Hub for AvalAI/OpenRouter/Google Gemini/OpenAI with secure key, live model list/search, connection test and default Provider/Model;
- Site Connection settings for FTP + authenticated Bridge with Credential Store secrets;
- legacy `launch.py` preserved and verified healthy.

Verification:
- Phase49.3I.42B2 Windows run `33369749205` PASS end-to-end;
- dedicated Single Active AI run `33369749123` PASS;
- Qt foundation/full-parity tests, 3I.41 Filament, 3I.34/35/36/37/39 mature regressions, Single Active AI regression, Qt offscreen launcher, legacy launcher and no-Tk guard all PASS;
- Production touched = NO;
- Host touched = NO;
- Django migration changed = NO.

Boundary:
owner-requested Product/Edit/Filament/Profile/Image/SEO/Slider/AI/Settings parity remains implemented and CI-tested. Phase42C live acquisition controls are now migrated into Qt Operations through the shared ApplicationKernel/AcquisitionCore. Qt is still not the default launcher and cannot be marked ACCEPTED before owner Local foreground QA.

Rollback:
`backup/pre-phase49-3i42b2-full-legacy-parity-20260830` → `6260f94cee531124446cf1b3e19ce0d95554d594`.

Exact next task:
owner Local clean ff-only pull + repository-owned 42C gate + bounded Classic/Hybrid foreground acquisition QA. After acceptance continue 42D polish and 42E packaging/default-launcher cutover. Production remains blocked.

## Current source checkpoint — Phase49.3I.45

Executable/source checkpoint tested by the dedicated Windows acquisition CI:

`846cb63038a79cfe450f5a60aa66e531cf6fe0de`

Catalog Center:
- version `8.9.9`;
- build `2026.08.30.3`;
- Phase49.3I.43–45 Modern Acquisition run `33313008595` PASS;
- Single Active AI run `33313008558` PASS;
- Production touched = NO;
- Host touched = NO;
- Django migrations changed = NO;
- ERR-49-078 robots unreachable/rate-limit fail-closed fix `11379ca343c64c251e9c34dd907dffa5f7529e12` is included in the CI-tested checkpoint.

3I.45 adds one additive Catalog SQLite metadata table:
`acquisition_discovery_observations`.

It records URL discovery provenance and Sitemap freshness metadata only; no raw HTML/XHR/session payload is stored.

Rollback:
`backup/pre-phase49-3i45-book-driven-discovery-intelligence-20260830` →
`3616bf222f394b769cb2e3198164d735fca5267b`.

Canonical active phase doc:
`docs/phases/PHASE49_3I45_INCREMENTAL_DISCOVERY_INTELLIGENCE.md`.

Exact next gate: owner Local ff-only pull + checksum backup of Catalog SQLite + 3I.43/45 regressions + one foreground real-source acquisition QA. Production remains blocked.

## Exact code/runtime candidate

Current packaged/runtime candidate:

`55139b909f214f33994d76bc1e6fdfd028b5d6c7`

Catalog Center:
- version `8.9.8`,
- build `2026.08.29.2`,
- Phase49.3I.31–40 targeted run `33247729316` PASS,
- Single Active AI run `33247815007` PASS,
- Windows Portable run `33247815027` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.8`,
- artifact ID `9713426658`,
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`,
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`,
- browser/self-verify/source-URL/launcher/regression gates PASS,
- Production touched = NO.

### Phase49.3I.40 behavior verified in CI
- Stage 2 order is manufacturer → material/filament → color → Product Offer registration → pricing → production rows → Profile identity/dimensions,
- selected Offers from other manufacturers/filters are preserved when the current filter is registered,
- global filament stock/rates/preheat facts are separate from Product-specific fixed price per exact Offer,
- color preview uses image/explicit HEX/name fallback,
- Readiness separates real data defects from complete-but-not-finalized stages,
- AI terminal 100% is blocked unless final `ai_fixable_count == 0`,
- AI source authority remains Link / Saved-Crawled Data / Screenshot only,
- mature Crawl/Direct Link/parser/image/file acquisition remains the authority.

Canonical active phase doc:
`docs/phases/PHASE49_3I45_INCREMENTAL_DISCOVERY_INTELLIGENCE.md`.


## Current active delta — Phase49.3I.45 incremental discovery intelligence

The latest owner-supplied GUI/FastAPI/web-scraping references were reviewed and reconciled with current official Qt for Python, FastAPI, HTTPX, Playwright, Scrapy, RFC 9309 and Sitemap documentation.

Permanent knowledge index:
`docs/references/PYTHON_GUI_FASTAPI_WEB_ACQUISITION_2026.md`.

Implemented:
- structural Sitemap XML parsing;
- direct Product `loc` only;
- `lastmod`, `changefreq`, `priority` metadata;
- nested Sitemap freshness order inside a bounded document budget;
- unseen Catalog Products before already-known Products;
- persistent discovery observation ledger with first/last seen and seen count;
- custom-source model-path heuristic when no exact model regex exists;
- no CAPTCHA/auth/proxy bypass;
- no raw browser network payload persistence.

3I.43/44 pooled HTTP/cache/robots/retry/pacing/browser fallback remains the transport authority. Django Production remains unchanged.

Dedicated Windows CI `33313008595` PASS and Single Active AI `33313008558` PASS on executable source checkpoint `846cb63038a79cfe450f5a60aa66e531cf6fe0de`.

## Current active delta — Phase49.3I.42 Qt 6 desktop modernization

Two owner-purchased PyQt5 references were reviewed and converted into a project-specific GUI engineering index at `docs/references/PYTHON_QT_GUI_REFERENCE_NOTES.md`.

The new presentation target is current Qt for Python / PySide6, not a new Qt5 lock-in. A parallel Qt6 shell now exists without replacing the mature Tk launcher:
- `catalog_center/qt_launch.py`;
- `catalog_center/qt6/`;
- `catalog_center/requirements-qt6.txt` pinned to PySide6 6.11.2;
- QMainWindow + permanent navigation + QStackedWidget routing;
- centralized QAction registry and Ctrl+K command palette;
- menus/toolbars/statusbar;
- Model/View Product + Filament tables and proxy filtering;
- seven-stage Product Wizard shell;
- QSplitter, QSettings, RTL, light/dark QSS;
- QThreadPool/QRunnable Signal worker contract;
- no Tkinter imports inside the Qt presentation package.

Dedicated Windows CI run `33299745502` PASS: install, compile, Qt tests, Phase49.3I.41 regression, offscreen structural launch, legacy launcher verify and no-Tk guard. Existing Single Active AI CI `33299745499` also PASS.

The first workflow definition failed before creating a job (`33299686593`) because `runner.temp` was referenced at job-level evaluation; it was fixed by resolving the path inside the Windows step. The failed condition was not repeated unchanged.

No Django/Catalog migration, Host, Production, secrets, media or default launcher change.

Rollback: `backup/pre-phase49-3i42-qt6-desktop-foundation-20260830` → `753539b0d76ccf0d185e35add458925628812a44`.

Next exact task: owner Local 42C Classic/Hybrid acquisition QA through the repository-owned gate; keep the mature Catalog/AI/Crawl/Bridge/Pricing contracts and legacy launcher until cutover.

## Current active delta — Phase49.3I.41 central Filament library

Owner rejected the ambiguous Ctrl/Shift multi-select workflow for a real inventory of many Filaments. The final Windows design is now a global reusable Filament Library plus a Product checklist.

Implemented on GitHub:
- main sidebar page `فیلامنت‌ها`;
- reusable manufacturer/brand/material editable selectors;
- inventory grouped by material type (PLA/PETG/etc.);
- one-click checkbox semantics for individual Filaments and whole material groups;
- dedicated `انتخاب‌های این محصول` box;
- explicit Product selection save;
- Product fixed-price preservation across library refresh/checklist save;
- Stage-2 confirmation persists the same checklist draft before finalization;
- authenticated Bridge Filament GET/upsert endpoints;
- automatic Site sync after Filament Save/Product checklist commit;
- soft deactivate + Site inactive sync;
- all weight/stock/rate/preheat/image/color facts travel with the Filament.

No new migration was added. The Site endpoint relies on existing `store.0039` + `store.0040`. Production is still verified only through `store.0035`, therefore Production is untouched and deployment is blocked pending the normal read-only Host audit, backup and migration gate.

Rollback: `backup/pre-phase49-3i41-filament-library-sync-20260829` → `92a3f4dfcf64d5fedaf837eb9a37dac028cabd59`.

Owner Local compile/tests/foreground QA are next. Active phase: `docs/phases/PHASE49_3I41_FILAMENT_LIBRARY_SITE_SYNC.md`.

## Current Windows delta — ERR-49-075

Owner screenshots on the ERR-49-074 build exposed the last Stage-2 defects before moving to the website:
- newly saved Filament could remain hidden because the list kept the previous manufacturer/material filter;
- selected-Filament editing still used the old 3I.39 dialog and bypassed the final live-rate editor;
- immediate upsert return omitted hourly/preheat/image fields, allowing a just-edited Product snapshot to carry zeros;
- price preview could use a stale registered Filament instead of the fresh/current selection;
- range mode still opened a formula-style table.

GitHub now fixes all five at the source boundary. Saving a Filament moves the filters to that exact row and selects it; editing delegates to the final 3I.40 editor; pricing refreshes registered snapshots from the global Filament inventory while preserving Product fixed price; a new unregistered current selection can be previewed as a draft; range preview is truthful and no longer shows fake zero formula rows.

Rollback: `backup/pre-err49-075-filament-refresh-pricing-preview-20260829` → `d66c68f36d1fd3e4143d461bccd999046c4baaf7`.

No schema/migration/AI/image/Host/Production change. After a short Local Stage-2 verification, proceed directly to website receive/sync.

## Current Windows delta — ERR-49-074

Owner pulled exact `954c0516661e6c70145d7f6f395b4e92ceeb40bd`, created checksum-backed Catalog SQLite backup `D:\projects\3dprinthub-backups\err49-073-20260829-201331\catalog-before-err49-073-qa.sqlite3` (SHA256 `DA9CC61848CF41EED1674B0B9D6EBC1B8D53BA6CE700F6BCEF42A565CF8F18BC`), passed compile, 2/2 exact ERR-49-073 regressions, 4/4 OpenRouter-only and 73/73 full Windows stage regression, then foreground-launched 8.9.8. The image Metadata issue cleared and the owner reported the Product ready for publication.

The remaining requested Windows delta is Stage 2 only:
- restore the continuously visible final calculated amount that existed before;
- show the live final roll/rate calculation inside Filament rate editing;
- all operator-facing buttons/dialogs use `Filament`, never `Offer`;
- keep internal `offer_*` identifiers unchanged for compatibility.

GitHub implementation is complete; Local retest is next. Rollback: `backup/pre-err49-074-filament-rate-final-display-20260829` → `954c0516661e6c70145d7f6f395b4e92ceeb40bd`.

No Catalog/Django schema, migration, Product media, AI provider, Host or Production change. After this Local QA passes, the next work item is the website receive/sync path for the same Filament/Profile/pricing data.

## Current foreground blocker/fix — ERR-49-073

Owner Local `6d5897ecefc427c940c690daabc311f85cc6e044` passed exact regressions 7/7, OpenRouter-only 4/4, full Windows stage suite 71/71 and foreground launch. Explicit confirmation now works for the other Stages. The remaining foreground issue is isolated to Images: after Images was confirmed, later Content/SEO and Source/License changes made image Metadata signatures stale; deterministic SEO file regeneration ran, but the image Stage lock blocked the derived DB signature update, causing repeated `بروزرسانی Metadata تصویر 1/2` warnings.

GitHub now allows only deterministic image-finalizer fields to refresh through the lock, finalizes image Metadata during Stage-3 confirmation, permits re-confirming an already-locked image Stage to refresh derived Metadata, and blocks misleading manual override saves while locked.

Rollback: `backup/pre-err49-073-image-confirm-metadata-refresh-20260829` → `6d5897ecefc427c940c690daabc311f85cc6e044`.

Stage-2 pricing/Profile remains intentionally incomplete in owner QA and was not changed. Production untouched.

## Current Local gate/fix — ERR-49-072

Owner Local pulled exact `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`, verified the canonical branch, created a fresh checksum-backed Catalog SQLite backup, and passed compile. The new 7-test ERR-49-071 regression set then stopped on one fixture error before OpenRouter/full-suite/foreground launch: the clean temporary DB used by the new Stage-2 persistence test lacked `price_min`.

This is a test-fixture composition defect. Real ProductWorkspace initializes `epic49_desktop_schema` (price_min/price_max) and `phase49_3f_workspace` (pricing_strategy) before Stage-2 editing; the test helper initialized only minimal Database + Profile/Ledger schemas.

Fix `1307f4c438de184a930041d365976c2ce018bff8` makes the fixture follow the real runtime schema order. Rollback: `backup/pre-err49-072-commerce-test-schema-20260829` → `34c65bc9e39d851b4fd3f7e0d2d4ec9627aed5b9`.

No runtime application source, Product data, Django schema/migration, Host or Production change. Owner Local rerun is next.

## Current Windows blocker/fix — ERR-49-071

ERR-49-071 executable code/regression head: `6085ea70d1075c5a1abaca4b4b2efdebe1254829`. No current-head GitHub Actions run is attached; owner Local compile/regression/foreground verification is the next gate. Stage-2 confirmation now also persists its historically visible Product type and dimensions before the Stage lock is written.


Owner Local on exact `d4da99744659d06ebe5c04fd69532cd0e03db3e8` passed compile, the exact ERR-49-070 regressions, OpenRouter-only 4/4 and the full 67/67 Windows stage contract, then foreground-launched the real 8.9.8 source. Visual acceptance still failed: Stage 1 stayed red despite filled title/category, the rejected type/dimensions/use-case panel appeared there, the generic missing count inflated to 46 because pending confirmations were counted as missing data, and the bottom control was still the legacy Next instead of one explicit Stage confirmation action. The runtime trace also proved the title-only AI button could start Product 286 while Product 63 AI was still active.

ERR-49-071 is a targeted rollback of those bad UX decisions while preserving Stage-2 commerce and OpenRouter-only AI:
- Stage 1 is back to Persian title + site category; type/dimensions/use-case remain in Stage 2;
- the ERR-49-069 additive Stage-1/Stage-5 panels are no longer mounted;
- explicit `سایر محصولات / external-other` is a valid selected category;
- real data defects are separated from `pending_finalization`;
- `✅` means explicitly confirmed, `◌` means complete but waiting for confirmation;
- a dedicated independent footer button `✅ ثبت و تأیید مرحله →` persists, validates, confirms and advances;
- the legacy Next widget is hidden instead of repeatedly repainted;
- the visible title-only AI callback is rebound to the guarded OpenRouter Stage-1 runner.

Rollback: `backup/pre-err49-071-stage-confirm-rollback-20260829` → `d4da99744659d06ebe5c04fd69532cd0e03db3e8`.

Production/Host/Django migration/media/secret/Stage-2 commerce remain untouched. New owner Local regression + foreground QA is mandatory.

## Current Local gate/fix — ERR-49-070

Owner Local on `382a34fa6e876dc7098c8152c98c7cb076d508e8` passed compile and 4/4 OpenRouter-only tests. The full 67-test Windows contract then stopped before launch with exactly two deterministic defects: clean temporary Catalog DB lacked `technical_summary_fa`, and the Stage-5 builder methods referenced by 3I.39 had no implementation bodies.

GitHub now adds the clean schema field, implements the visible `منبع و مجوز کامل` panel inside Stage 5, hydrates designer/license/technical summary/features from SQLite, and persists the Persian license selector through the Stage-5 finalize path. Regressions cover clean schema and actual builder presence.

Rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`.

No Host/Production/Django schema/Stage-2 Offer/Profile/media/secret change. Owner Local rerun is next.

## Current Windows blocker/fix — ERR-49-069

Owner Local pulled exact `3f43260db669b458a682f594b5d50eb5221b9ef3`, created checksum-verified Catalog SQLite backup `D:\projects\3dprinthub-backups\err49-068-20260829-174512\catalog-before-err49-068-qa.sqlite3` (SHA256 `5A6DB948ADACA81014DEDFA7FF117A0C4AF26364936575ACB15D21D632D4C321`), passed compile and **60/60** focused tests, and launched the canonical 8.9.8 source. The real foreground UI nevertheless reproduced the remaining defect, proving it is a final-composition/runtime problem rather than wrong checkout or stale tests.

Observed runtime facts:
- footer was repainted back to old `مرحله بعد برای انتشار →` after 3I.39 had installed the new actions;
- Stage 1 could become data-complete but still not naturally confirm/advance;
- Product type/dimensions/use-case were not all visible in their Quick owner stage;
- source/license/technical fields were split away from Stage 5 ownership;
- stage-scoped AI counted unrelated global defects and falsely reported remaining defects after its own Scope was complete;
- Product 63 and Product 295 AI jobs overlapped;
- saved active Provider was OpenRouter, but resilience still fell back to AvalAI.

ERR-49-069 executable-code hotfix head is `136011971dea907ac777b3e66190dd27982a0c38` (later branch commits are documentation only until the next code change). It now:
- makes even late/captured Wizard refreshes finish by restoring `✅ تأیید و مرحله بعد →`;
- makes legacy Next persist before readiness and delegate to final stage confirmation;
- restores Stage-1 `نوع محصول / ابعاد / کاربری` controls and persistence;
- restores Stage-5 `طراح / مجوز / خلاصه فنی / ویژگی‌های فنی` controls and persistence;
- routes legacy title AI through the final Stage-1 engine;
- makes single-stage AI completion/progress Scope-aware;
- blocks concurrent Product AI jobs across Product Workspaces;
- makes Product AI OpenRouter-only: saved OpenRouter model first, optional `openrouter/free` second; **no AvalAI/Google/OpenAI fallback**.

Rollback:
`backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`.

No Django schema/migration, Host, Production, Product media or secure-key-value change. Owner Local pull + focused regression + foreground Product 63/295 QA is mandatory before acceptance.

## Current Windows blocker/fix — ERR-49-068

Owner reran the corrected ERR-49-067 gate on exact head `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`: the exact previously failing regression PASSed, the full focused set ran 43/43 PASS, worktree/head verification PASSed, and foreground Catalog Center 8.9.8 launched from the canonical source.

Real Product 63 QA then proved the current Windows workflow itself still had a stage-confirmation regression:
- Stage 1 could be visibly filled/manually edited but did not become a usable confirmed step;
- the expected visible bottom confirmation control was absent from the practical workflow;
- the older Next flow checked persisted readiness before persisting the current widget values;
- 3I.36 `ثبت` existed in a separate rail panel but was not a reliable visible operator path in the current composition;
- already-created legacy Tk AI buttons could retain old callbacks even after class aliases were replaced.

The same trace also exposed secondary AI/runtime issues: legitimate `Flexi Gecko` source identity was rejected inside SEO; an OpenRouter-shaped key/model was attempted under OpenAI fallback; and a deferred callback captured the cleared `exc` variable.

ERR-49-068 is now on GitHub:
- fixed footer: `✅ تأیید و مرحله بعد →` persists/finalizes the current Stage before advancing,
- adjacent `✨ پرکردن ناقص‌ها با AI` and `✏ اصلاح مرحله`,
- footer confirm authority is restored after every Wizard refresh,
- visible legacy AI buttons are rebound across the entire Workspace to final 3I.39 execution,
- exact source-title identity is allowed inside otherwise-Persian title/description/SEO; unrelated Latin remains invalid,
- cross-provider key reuse is blocked and fallback models must be provider-specific,
- deferred exception text is frozen before scheduling.

Rollback:
`backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`.

No schema/migration, Product media, Host or Production change. GitHub source/regressions are updated; owner Local pull + focused tests + foreground Product 63 confirmation/AI QA is the next gate.

## Latest Local gate — ERR-49-067 fixture-only stop

Owner pulled exact head `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c` on the canonical Windows checkout and created a fresh Catalog SQLite backup:
`D:\projects\3dprinthub-backups\err49-066-20260829-170052\catalog-before-err49-066-qa.sqlite3`
with SHA256 `AE475E39040B8BF8F7BEF7B13D3176F2B83BBA956E2121D53CC2F5CC087F185F`.

Compile passed. The focused suite ran 43 tests and stopped on exactly one deterministic regression-fixture error. The locked-stage test fed `seo_description_fa` containing the Latin token `AI`, while ERR-49-066 deliberately made SEO title/description Persian-only. Runtime validation therefore rejected the mock payload before the test reached its lock/immutability assertion.

The production checker was not loosened. Only the stale fixture was corrected at `38cb415bc12d7ec08943809fd14f3478b3ddac1b`. Rollback: `backup/pre-err49-067-seven-stage-test-fixture-20260829` → `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`.

Next gate: owner ff-only pull current docs-final head, rerun the same focused 43-test gate, and only on PASS launch Product 63 in foreground. Production remains untouched.

## Current owner blocker — ERR-49-066 checker/stage ownership mismatch

Owner Local retest of `c679c66d8c6554ff14e5705b7eb3aada24495990` proved the prior repaint fix was not the remaining root cause: 12/12 targeted tests passed and the correct 8.9.8 foreground runtime launched, but Product 63 still showed completed inputs as red/missing.

The foreground audit isolated the contract failure:
- an older visible 3I.31 full-AI action still ran and persisted Persian/SEO/image fields,
- the final readiness loop then saw 7 data defects / 5 AI-fixable,
- it scoped Stage 4 Content/SEO,
- a valid fallback Provider response was accepted,
- but no Product field update followed and the loop reported 0 defects fixed / 5 still AI-fixable.

The new GitHub hotfix aligns the whole chain:
- one field owner: `title_fa → quick`, image Alt → `images`, editorial/SEO → `content`,
- persisted title/description may preserve only exact Latin source-identity tokens; SEO/list fields remain Persian-only,
- AI repair uses the same semantic checker as readiness, including non-empty invalid keyword/tag/hashtag lists,
- guided Wizard uses `data_ready/missing_data` for red stars, stage icons and Next gating rather than operator-finalization `ready`,
- final 3I.39 class aliases route mature full-AI/link/current-stage actions through the same seven-stage repair engine.

Rollback:
`backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`.

GitHub code/regressions are updated; no current-head Actions run is attached yet. Owner Local targeted tests + foreground Product 63 retest are the next gate. No DB/schema/media/secret/Host/Production change.

## Owner SEO/readiness reconciliation hotfix — ERR-49-065

After the ERR-49-064 geometry hotfix, the owner confirmed the professional 3I.39/3I.40 Product Workspace is now visible. The next foreground test exposed a narrower SEO/readiness problem: seven-stage AI filled the Persian/SEO fields, but red/missing readiness widgets remained stale.

Root cause: AI persisted the new fields, then the wrapped UI refresh chain allowed older guided-wizard cached state to repaint after the final 3I.40 readiness renderer.

Git hotfix:
- source `b9eb9d74b0c0be49ca8d04a4333750e68e93f4`,
- regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`,
- rollback `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`.

Behavior: whole-product and single-stage AI completion now rehydrate the Product from SQLite, reload, refresh lock/wizard/readiness surfaces, and run final readiness last again after a short settle delay. This changes only post-AI UI reconciliation; no AI Provider/source ownership, Offer/Profile, schema, Host or Production behavior changed.

Verification status: GitHub updated; owner Local targeted tests and foreground SEO retest are next. No Production work is allowed before that pass.

## Owner foreground 8.9.8 blocker — ERR-49-064

Owner foreground execution on the canonical checkout/branch/head proved the correct 8.9.8 source was running, but opening Product 63 raised a real Tk callback exception before 3I.39/3I.40 could finish ProductWorkspace construction:

`TclError: cannot use geometry manager pack inside ...!labelframe which already has slaves managed by grid`.

The traceback terminates in `phase49_3i35_operator_ledger.build_material_actions()`. The modern material/color checkbox picker had already converted that legacy commerce card to a grid-managed surface; the 3I.35 layer then attempted to mount obsolete Listbox actions with `pack`. This explains why the owner saw the older Stage-2/SEO UI despite 3I.39/3I.40 launcher markers: construction stopped part-way through the wrapper chain.

Hotfix:
- source commit `aa37dcf916dfab71409738f7087a171daffe4a0a`,
- regression commit `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`,
- rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`,
- modern picker now suppresses only the obsolete 3I.35 Listbox action row; 3I.35 data/business methods remain and 3I.39 stays the final visible Stage-2 authority,
- no DB/schema/media/secret/Production change.

Verification is not yet complete: owner must ff-only pull the current branch, run the targeted 3I.35/3I.40 tests and foreground-open the same Product Workspace. Production remains blocked.

### Phase50 / Store extension through 0040
Migration:
`store.0040_phase50_filament_offer_operations`.

Adds exact Offer operation facts:
- print hourly rate,
- supervision hourly rate,
- preheat hours/temperature/hourly cost,
- optional filament image URL.

Verification:
- first 0040 run `33246706102` exposed only Decimal string-format assertions; migration plan/apply and no-drift gates had passed,
- corrected tests at `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`,
- Phase50 Variant2/Profile Matrix run `33246843145` PASS,
- full CI SQLite migration through `0040` PASS,
- 21 Store/Profile/Checkout/Offer regressions PASS.

Production migration state is unchanged from the last terminal verification: only `0034` and `0035` are claimed applied. `0036..0040` require fresh Host read-only verification before any Production write.

## Owner Local automated acceptance — PASS

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

Only manual/visual operator acceptance remains before Host read-only audit. Automated Local acceptance is complete; this does not count as Production approval by itself.


### Detached launch note — visual QA not yet completed
The owner automated gate emitted `CATALOG_CENTER_LAUNCHED=YES`, but the owner did not see the new UI. The gate uses detached PowerShell `Start-Process`; therefore this marker is not evidence of visible/manual acceptance. Per `ERR-49-058`, the next action is a foreground `launch.py --debug` run from the canonical Local checkout and visual verification inside the Product workspace/order-pricing-options stage. Production remains blocked.

## Owner foreground startup incident — fixed in 8.9.2

Owner foreground launch of 8.9.1 exposed a real startup blocker after automated gates: 3I.35 mounted an AI settings panel with `grid` directly into the pack-managed UX87 `settings_tab`, causing Tk `TclError` before the window became usable. This is recorded as `ERR-49-059`.

The runtime fix changes only the outer panel geometry to `pack`, preserving internal panel layout and all previous AI/Profile behavior. Regression and Windows package CI now PASS on runtime `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`. Owner must now pull the documentation-final head and run foreground `launch.py --debug`; visual acceptance is still open. Production remains untouched.

## Owner foreground Product Workspace incident — fixed in 8.9.3

8.9.2 confirmed the application startup geometry fix, but owner diagnostics exposed a second real Visual-QA blocker when Products 305/303 were opened: Profile Matrix selection called an unbound short helper `self._profile_by_key`. This is `ERR-49-060`.

8.9.3 changes the call to the actually installed namespaced method `self._phase49_3i34_profile_by_key`, adds an executable wrapper-binding regression, and passes targeted/Single-AI/Windows package gates on runtime `9637829a255a1d09800bc062c2f049cf5d92b585`.

That 8.9.3 checkpoint is historical and was superseded by 3I.37/3I.38. The current owner gate is Catalog Center 8.9.6 visual/functional QA. Production remains untouched.

## What is implemented now

### Phase49.3I.35 — Windows operator workflow
- 3I.35 is composed through the established `phase49_3i_pricing_modes.py` boundary; no parallel launcher-only patch.
- the old duplicate 3I.34 Profile panel is hidden.
- the upper Product controls are temporary working state.
- `ثبت پروفایل از فرم بالا` creates an independent registered Profile snapshot.
- `پروفایل جدید از آخرین` loads the latest snapshot into working state so the operator can rename/change size/price/options and register another Profile.
- registered Profile ledger is the synchronization/publish authority, not transient controls.
- multiple production rows per Profile support:
  - Product weight,
  - print time,
  - support weight.
- quick/basic Product page no longer owns fixed price/weight/Profile authority.
- material/color section has:
  - select all,
  - clear selection,
  - local register selection on current Product,
  - no full Products refresh for that local action.
- material offer carries:
  - material,
  - brand,
  - manufacturer/factory,
  - color,
  - roll weight,
  - roll stock,
  - purchase price,
  - sale price,
  - USD price,
  - explicit FX rate.
- effective customer filament rate uses the highest positive explicit sale basis and never guesses FX.
- source URL guard/history/recovery and existing extraction logic are preserved.

### Resilient Product AI
The mature 3I.33 AI pipeline remains the editorial execution authority and 3I.35 wraps it with observability/resilience:
- live provider/model preflight,
- progress 0–100,
- visible send/wait/reply/apply events,
- up to configured retry count per provider (default 3),
- explicit configured fallback providers only,
- optional `openrouter/free` only when configured,
- selected-Product bulk processing with isolated per-Product failures,
- no global Products-page refresh after every Product,
- cancel remains operator-controlled.

Supported Product AI modes:
- link-grounded Persian translation + SEO,
- saved Product data → Persian translation + SEO,
- Product-page screenshot/vision → extracted facts + Persian SEO,
- repair/fill missing editorial data.

Editorial AI does not own material/color.

### Manual readiness
- SEO stage can be manually approved when actual Persian title/description are complete but a detector is stale.
- source/license can fill from existing local facts.
- source fields can be repaired by AI.
- source review can be manually acknowledged.
- manual review cannot bypass invalid/non-commercial license policy.

### Phase50.A.2E — Store brand-aware filament bridge
Migration:
`store.0039_phase50_filament_offer_pricing`.

Adds:
- MaterialColorOption brand/manufacturer/roll/pricing/FX facts,
- `ProductVariant.support_weight_grams`,
- `StoreOrderItem.support_weight_grams`,
- `StoreOrderItem.filament_brand_name`,
- `StoreOrderItem.filament_manufacturer_name`.

Store behavior:
- Desktop Profile sync creates/updates brand-aware MaterialColorOption facts.
- same material/color from different brands remains distinct.
- formula pricing consumes `effective_sale_price_per_gram`.
- current color stock uses matching real spool remaining grams first; otherwise synchronized roll-count × roll-weight snapshot.
- Variant API returns brand/manufacturer/support.
- Product Profile selector/summary shows brand/manufacturer/support.
- successful checkout freezes support/brand/manufacturer into historical order items.

## Errors found and fixed in this development batch

### ERR-50-016
First Phase50 run `33059803005` stopped at migration drift and proposed an unapproved fake `0040_alter_productvariant_support_weight_grams`.

Root cause:
mature 3F runtime contributed the same field before 0039, but its `verbose_name` differed from migration 0039.

Fix:
align runtime field metadata to migration 0039. No 0040 created.

Verification:
Phase50 run `33059883188` PASS.

### ERR-49-056
First 8.9.1 Windows candidate run `33059799929` had two stale release-contract failures:
- old 3I.33 test still required retired quick-page `قیمت قطعی فروش`,
- `config.example.json.package_version` remained 8.9.0.

Fix:
- test now enforces the requested single pricing authority and absence of quick-page fixed-price control,
- example config aligned to 8.9.1.

Verification:
Windows run `33060047878` PASS.

No failed CI command was repeated unchanged.

## Production state — last terminal verified

Production application commit remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified Production:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`,
- Python 3.12.13 / Django 6.0.7,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- `store.0036_phase50_checkout_snapshot` not Production-applied at last verify,
- `store.0037_phase50_professional_commerce_policy` not claimed applied,
- `store.0038_phase50_profile_matrix` not claimed applied,
- `store.0039_phase50_filament_offer_pricing` not claimed applied,
- Home/Store/Admin/Product/Variant API healthy at last Production verify,
- public imported working-media exposure = 0.

No Production deploy, migration, collectstatic or restart was performed during 3I.35/50.A.2E development.

Last verified Production rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

A **fresh** Production source + environment + MySQL backup is mandatory before the next deployment.

Expected pending schema chain, subject to fresh read-only MySQL verification:
1. `store.0036_phase50_checkout_snapshot`
2. `store.0037_phase50_professional_commerce_policy`
3. `store.0038_phase50_profile_matrix`
4. `store.0039_phase50_filament_offer_pricing`

CI proves that chain on SQLite; it does not prove the current Production MySQL migration table.

## Backup / rollback

Git safety anchors:
- `backup/pre-phase49-3i35-operator-ledger-20260827` → `ca9cc1160f407c0a78302ad75cb38396616aed52`
- `backup/pre-phase49-3i35-integration-20260827` → `1b02d413be00c09631661eafaf252d011ad45d40`

These are source rollback anchors only.

## Exact next work

### 1. Owner Local Windows 3I.38 gate
Canonical root:
`D:\projects\3DPrintHub`.

Required preflight:
- verify exact repository,
- branch `agent/phase49-3i18-operator-bulk-ai-rebuild`,
- clean worktree,
- live GitHub branch head,
- ff-only pull,
- run current `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1`.

Owner visual/functional QA on 8.9.6:
- crawl/received ledger opens and shows known URLs/statuses,
- a disposable Product can be rejected + local files/images purged while source URL/external ID remain as a rejected tombstone,
- deletion cannot escape the Catalog `collected\` root,
- rerunning the same Listing skips previously collected/rejected identities and continues to newer Products,
- ordinary new Product Crawl/Direct Link/image/file receive still works,
- Direct Link to a rejected Product skips before receive/download,
- selected-Product bulk Content/SEO uses the same mother AI source mode,
- single Product can clean/complete only Stage 4 without changing Profile/price/source/images/slider,
- locked stages remain unchanged until explicit `اصلاح`,
- image-only complete SEO does not spend an AI request,
- existing 3I.35 Profile/filament behavior remains healthy.

### 2. Local Django/Store regression
Local SQLite is already owner-verified through `store.0039` from the prior gate. Re-verify:
- effective DB path,
- fresh backup if any schema write becomes necessary,
- `django check`,
- `makemigrations --check --dry-run`,
- Store/Profile/Checkout regressions.
3I.38 itself adds only Catalog SQLite state and no Django migration.

### 3. Only after owner Local QA PASS
Perform read-only Host audit:
- project root,
- branch/current HEAD,
- clean worktree,
- live GitHub branch SHA,
- exact Python/Django,
- exact MySQL DB,
- actual `0034..0039` migration rows,
- exact migration plan,
- disk space,
- `mysqldump` availability.

Then create fresh tracked-source + environment + MySQL backups/checksums and record rollback HEAD.

### 4. Production deploy
Deploy only the owner-approved GitHub head:
- explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`,
- verify exact SHA + ff-only ancestry,
- re-run Django checks/drift/DB/plan,
- apply only actually pending approved migrations,
- collectstatic,
- Passenger restart,
- Home/Store/Admin/Product/Profile API/Checkout/static/private-media/order verification,
- update docs with exact Production SHA/migrations/backup.

## Owner Local QA checkpoint — 2026-08-27 PowerShell DB-probe stop

Owner terminal evidence on canonical Windows root `D:\projects\3DPrintHub`:
- branch `agent/phase49-3i18-operator-bulk-ai-rebuild`,
- Local fast-forwarded successfully to `35ab63105f30fdca42518d5273a424a3200977e3`,
- worktree clean before the owner gate,
- live GitHub SHA matched that target,
- packaged runtime/tooling ancestry checks PASS,
- fresh Catalog SQLite backup created at `D:\projects\3dprinthub-backups\phase49-3i35-20260827-133859\catalog.sqlite3`,
- owner gate then stopped at the read-only Django DB detector because multiline PowerShell `python -c` quoting corrupted the Python source,
- this failed run stopped **before** Local Django migration execution; no new migration was applied by this failed run.

Earlier owner evidence on `ca9cc1160f407c0a78302ad75cb38396616aed52`:
- Local SQLite migration through `store.0038` PASS,
- 15 Store/Profile/Checkout tests PASS,
- post-migration drift check PASS,
- Catalog 49.3I.31–34 gate PASS.

Current correction:
- `ERR-49-057` records the wrapper defect,
- historical 3I.35 DB-probe correction completed; the current Catalog gate is 31–38 and Local Django SQLite was subsequently verified through `0039`.

## Related docs
- `docs/phases/PHASE49_3I38_CRAWL_LEDGER_STAGE_AI.md`
- `docs/phases/PHASE49_3I37_SEVEN_STAGE_AI_SCREENSHOT.md`
- `docs/phases/PHASE49_3I35_OPERATOR_LEDGER_RESILIENT_AI_FILAMENT.md`
- `docs/phases/PHASE50_FINANCE_ADMIN_COMMAND_CENTER.md`
- `docs/ERRORS.md`
- `docs/REQUESTS.md`
- `docs/ROADMAP.md`
- `PROJECT_CONTEXT.md`

Production remains blocked until owner Local QA passes.
