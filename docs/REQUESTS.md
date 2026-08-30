# OWNER REQUESTS

## REQ-49-079 — Full Legacy capability parity on Qt6 through an object-oriented application kernel
Status: `IN_PROGRESS / 42B1 GITHUB+WINDOWS CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Owner acceptance/feedback:
- Qt6 shell, menus and overall presentation direction are accepted;
- the text-only Qt Product list and read-only Wizard are not sufficient;
- all mature Catalog Center capabilities must be migrated rather than discarded;
- Products must again have folder/card-style image presentation and direct edit flow;
- every major subsystem must expose one reusable object-oriented Core/Engine owned by the application kernel;
- AI in particular must have one shared engine object used by every caller, not separate per-screen AI implementations;
- current mature Stage workflows, locks, history, image pipeline, Filament/pricing/Profile logic, crawl/discovery and publish contracts must be wrapped/reused rather than rewritten in parallel.

42B1 implementation:
- ApplicationKernel/CoreRegistry;
- Product/Image/Filament/Acquisition/Publish/AI cores;
- Qt Product gallery + local image preview;
- real Stage-1 title/category edit + explicit unlock;
- Stage-3 local image gallery;
- Qt CI `33319343447` PASS;
- Single Active AI `33319343464` PASS.

Next acceptance target is 42B2 Stage-2 full operator parity.


## REQ-49-078 — Apply new GUI/FastAPI/web-scraping books to the application and acquisition stack
Status: `IN_PROGRESS / ACQUISITION DELTA WINDOWS CI TESTED / OWNER LOCAL QA NEXT`

Requested:
- deeply review the newly supplied books;
- update development methods and commands using current best practices;
- improve speed, stability, quality and maintainability;
- improve web discovery/crawling/data extraction;
- update database structures where useful;
- keep a strong, comprehensive, wizard-driven desktop application.

Applied now:
- knowledge index for GUI/FastAPI/scraping;
- current official-doc verification for version-sensitive techniques;
- Phase49.3I.45 incremental Sitemap intelligence;
- Catalog discovery metadata ledger;
- freshness/unseen prioritization;
- preserved public/respectful acquisition policy.

Not interpreted as permission to:
- replace Django Production with FastAPI without an explicit architecture gate;
- bypass CAPTCHA/authentication/access controls;
- use proxy evasion;
- stress-test third-party websites;
- deploy before Local acceptance.


## REQ-49-077 — Modern comprehensive wizard desktop application from purchased Qt references
Status: `IN_PROGRESS / FOUNDATION WINDOWS CI TESTED / OWNER LOCAL PREVIEW NEXT`

Requested:
- study and apply the two purchased PyQt5 GUI references;
- upgrade the desktop application architecture, interaction patterns and visual quality;
- provide strong wizard flows, complete menus, explicit routes and predictable actions;
- add reusable patterns that reduce ad-hoc UI errors and blocking behavior;
- keep the application comprehensive rather than hiding capability behind ambiguous controls.

Implementation direction:
- source concepts are applied through current PySide6/Qt6;
- legacy mature business logic is reused rather than rewritten;
- parallel Qt preview first, cutover only after side-by-side acceptance;
- full migration is split into 42A–42E and cannot be called complete at foundation stage.

References summarized in `docs/references/PYTHON_QT_GUI_REFERENCE_NOTES.md`.


## REQ-49-076 — Central reusable Filament library and clear multi-select
Status: `IMPLEMENTED / GITHUB_UPDATED / OWNER LOCAL TEST NEXT / PRODUCTION NOT DEPLOYED`

Requested behavior:
- maintain roughly any number of Filaments globally rather than redefining them per Product;
- group by Filament/material type (PLA, PETG, etc.);
- select one or many with a visible checklist, with a separate box showing Product selections;
- no Ctrl/Shift dependency;
- remember/reuse manufacturer, brand and material values;
- allow normal Filament management from the main application;
- sync newly created/updated Filaments to Site with roll weight, stock and operational rates;
- keep Product-specific fixed pricing Product-owned;
- when a Product is duplicated by a path that copies its persisted Product fields, its saved Filament selection can rehydrate from the same Product-owned selection JSON.

Implementation: Phase49.3I.41. No new migration; local/Site verification is required before Production.


## REQ-49-075 — last Stage-2 fixes before website
Status: `IMPLEMENTED ON GITHUB / QUICK LOCAL RETEST NEXT / PRODUCTION NOT DEPLOYED`

Requested acceptance:
- a newly saved Filament immediately appears in the list and is selected;
- selected Filament edit uses the final live-rate editor;
- price preview uses the currently authoritative Filament facts and does not show zeros when rates are present;
- a newly selected Filament can be previewed before explicit Product registration, but attachment to Product remains an explicit action;
- range and formula modes must not be conflated;
- once these pass, move directly to website receive/sync.


## REQ-49-074 — restore final pricing result and use Filament terminology
Status: `IMPLEMENTED ON GITHUB / LOCAL RETEST NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- rate editor visibly shows the final calculated roll basis and rate per gram;
- Stage-2 pricing visibly shows the final amount/range without requiring the popup preview;
- formula result is based only on registered Filament facts + product weight/time/support + configured supervision/preheat/assembly;
- no hidden/default FX is invented;
- operator buttons/dialogs say `Filament`, not `Offer`;
- internal compatibility identifiers may remain `offer_*` and must not trigger a schema/API rename;
- after Local acceptance, website receiver must consume the same manufacturer/Filament/color/Profile/pricing facts.


Last Updated: 2026-08-29

Older detailed request history remains available in Git history. This file keeps active acceptance contracts.

## ERR-49-072 verification rule

The Stage-2 confirmation regression must use the same additive Catalog schemas as the real ProductWorkspace. Test-only schema setup may not be mistaken for a Product/runtime defect. After the fixture fix, rerun the full ERR-49-071 acceptance path before judging the visible Stage workflow.

## ERR-49-073 Images acceptance request

- Stage 3 must not require the operator to manually fight Metadata refresh after later Content/Source stages change.
- `ثبت و تأیید مرحله` on Images must finalize current SEO/Metadata and then confirm the Stage.
- If Images is already confirmed, pressing the same button may refresh deterministic Metadata without unlocking operator-approved selection.
- A confirmed image Stage remains protected from arbitrary AI/operator edits; manual Metadata overrides require `اصلاح مرحله`.
- Stale Metadata warnings must clear after successful deterministic rebuild.
- Do not change Stage-2 pricing/Profile/Offer behavior as part of this fix.

## ERR-49-071 owner acceptance request
Executable checkpoint: `6085ea70d1075c5a1abaca4b4b2efdebe1254829`. Stage-2 confirmation must persist the visible Product type/dimensions before it is marked confirmed.


- Restore the older Stage layout; do not place Product type/dimensions/use-case in Stage 1.
- Stage 1 must accept a deliberately selected `سایر محصولات` category.
- Every Stage must have one obvious permanent bottom `✅ ثبت و تأیید مرحله` action.
- Filled fields alone do not earn the final green check; `✅` appears after successful explicit confirmation.
- Clicking confirmation must persist the current UI first, validate it, confirm/lock the Stage, refresh the rail, then advance.
- Pending confirmation must not be counted as missing Product data.
- The legacy Next button must not be the authority because late wrappers repaint it.
- Title-only AI must obey the same global one-Product-AI-at-a-time/OpenRouter-only runtime guard.
- Preserve Stage-2 Offer/Profile/pricing, crawler/acquisition and current Product data.

## Preserved project contracts
- GitHub-first delivery; live branch/HEAD verification before Host operations.
- Product/SEO/media/Bridge security/idempotency and Product-owned public media remain intact.
- imported Catalog working-media is not a public Production namespace.
- healthy StoreOrder/Payment/Invoice/inventory/coupon/VAT behavior is extended rather than duplicated.
- no guessed carrier/gateway endpoint or tariff.


## REQ-50-028 — Professional Stage-2 Offer flow, Profile snapshot and truthful AI completion
Status: `IMPLEMENTED 49.3I.40 + STORE 0040 / BASELINE CI+PORTABLE PASS / ERR-49-069 STAGE-CONTRACT + OPENROUTER-ONLY HOTFIX GITHUB / OWNER LOCAL RETEST NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- Stage 2 order is manufacturer/company → filament/material → color → register Offer → professional pricing → production rows → Profile identity/dimensions,
- registering Offers in a new manufacturer/material filter preserves selected Offers from other filters,
- global Offer editor owns stock, roll weight, purchase/sale/USD+explicit FX, hourly print/supervision, preheat and filament image/HEX,
- Product fixed price is separate and can differ per exact manufacturer/material/color Offer without changing the global filament rate,
- formula pricing consumes exact Offer facts and production weight/time/support; preheat is optional and costs zero when absent,
- same material/color from Bambu Lab, eSUN or another manufacturer stays distinct through Desktop sync and Storefront selection,
- Storefront selection is manufacturer → material → color, with exact price and orderability after the selection is known,
- insufficient Offer/color stock prevents orderability,
- colors show filament image when available, otherwise explicit/fallback swatch,
- production weight/print-time/support rows are not duplicated in the bottom Profile identity form,
- Profile registration uses operator name + size + actual dimensions and creates an immutable snapshot; later Profiles may reuse the working form without mutating previous registered Profiles,
- duplicate Profile identity is rejected,
- Product screenshot selected for Site is the top viewport reference rather than full-page,
- full Link completion repairs AI-owned readiness defects stage-by-stage and reports request/response/apply/before/fixed/remaining state,
- 100% is forbidden while `ai_fixable_count > 0`,
- data-ready-but-not-finalized is not displayed as a data defect,
- each stage remains editable by default, can be finalized by the operator and must be explicitly returned to edit before later AI changes,
- AI sources are exactly Link / Saved-Crawled Data / Screenshot; Repair is an operation on the same engine,
- mature Crawl/Direct Link/parser/image/file receive behavior must remain unchanged,
- Store migration `0040_phase50_filament_offer_operations` reaches Production only after Local backup/migration/regression, owner visual acceptance and fresh Production MySQL backup/rollback verification.

Verification:
- Catalog targeted `33247729316` PASS,
- Single Active AI `33247815007` PASS,
- Windows Portable `33247815027` PASS on `55139b909f214f33994d76bc1e6fdfd028b5d6c7`,
- Store/0040 `33246843145` PASS,
- Production untouched.
- Owner foreground QA on 2026-08-29 exposed `ERR-49-064`: the obsolete 3I.35 Listbox action row mixed `pack` into the modern grid-managed material/color card and aborted ProductWorkspace before 3I.39/3I.40 visible UI construction.
- Follow-up owner QA exposed `ERR-49-065`: AI-persisted SEO fields must immediately reconcile the visible readiness/help widgets; fixed by DB rehydration + final post-AI readiness repaint without auto-finalizing operator stages.
- Owner retest exposed `ERR-49-066`: each displayed defect must have exactly one Stage owner, AI-fixable defects must map to an actual write path, Stage UI must turn complete from persisted `data_ready` without requiring finalization, and all mature full-AI actions must route through the same final checker/repair engine.
- ERR-49-067 fixture correction remains valid, but its interim all-Latin SEO prohibition was superseded by real Product 63 evidence: exact source identity tokens may remain beside Persian SEO text; unrelated Latin still fails.
- ERR-49-068 restores the owner-requested visible Windows flow: the current Stage must always expose `✅ تأیید و مرحله بعد` plus AI fill/edit controls; manual values are persisted before readiness is checked, and success advances to the next Stage.
- A visible legacy AI button must execute the same final 3I.39 engine as the new controls; class-method rebinding alone is not sufficient for Tk Buttons created earlier.
- Provider fallback must never reuse a key or model that belongs to another Provider.
- ERR-49-069 owner contract: Product AI is OpenRouter-only. The saved OpenRouter model is primary; the only optional fallback is `openrouter/free` with the same OpenRouter key. AvalAI/Google/OpenAI must not be invoked by Product AI.
- Stage-specific AI completion is judged only against the selected Stage; unrelated defects in other Stages must not trigger retries or false incomplete status.
- Only one Product AI job may run in the process at a time; another Product Workspace must be blocked until the active job finishes/cancels.
- Stage 1 must visibly expose Product type, dimensions and use-case/class. Stage 5 must visibly expose source/designer, commercial license, technical summary and technical features. Stage confirm must persist every owned visible field before readiness/finalization.
- A late/deferred legacy Wizard callback must never restore the old read-before-save Next action after final composition.
- Hotfix source `aa37dcf916dfab71409738f7087a171daffe4a0a` + regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`; owner Local retest remains required.

## REQ-50-001 — Complete business finance/accounting system
Status: `REQUESTED / PHASE50 ACTIVE`
Full GL/subledger, Treasury, Purchasing/Sales accounting, customer/supplier statements and management reports integrated with Store/service/inventory/production/payments.

## REQ-50-002 — Complete and reorganize Django Admin
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Professional Velzon operator console with business navigation, full-width lists, on-demand filters, Persian controls, stable footer, no document jump and approximately 290px readable right sidebar.

## REQ-50-003 — Preserve healthy commerce while adding accounting
Status: `ACTIVE CONSTRAINT`
StoreOrder, StorePayment, invoices, inventory, coupon/VAT, Product/Profile/Variant history and payment security remain compatible.

## REQ-50-004 — Dynamic delivery price
Status: `50.A.2B–2D GITHUB CI TESTED / PRODUCTION MIGRATION CHAIN NEXT AFTER LOCAL QA`
Shipping calculation must use the chosen profile/product effective shipping weight, packaging weight/dimensions and destination. Current ShippingMethod/rate rules remain the explicit fallback. Post/Tipax/Mahex adapters are allowed only after verified official current contracts/credentials.

## REQ-50-005 — Coupon + VAT checkout
Status: `PRESERVED / INCLUDED IN 50.A.2B REGRESSION BOUNDARY`
Do not duplicate current Coupon/VAT logic; shipping snapshot finalization must preserve discount, packaging, tax and payment totals.

## REQ-50-006 — Phishing-resistant comprehensive payment
Status: `REQUESTED / 50.A.3 PLANNED`
Server-owned amount, DB locking, callback identity, exact Authority, server-to-server verification and idempotency; never collect/store card/PIN/CVV.

## REQ-50-008 — Variant 2.0 size/build/packaging parity
Status: `PRODUCTION VERIFIED FOUNDATION`
`store.0034` and `store.0035` are applied; customer selector uses canonical ProductVariant state.

## REQ-50-009 — Torob marketplace integration
Status: `REQUESTED / 50.A.4 PLANNED`
Official Product API v3 with stable Product/Profile grouping, price/availability and image-quality rules.

## REQ-50-010 — ZarinPal Store checkout activation
Status: `REQUESTED / 50.A.3 PLANNED`
Connect StorePayment to mature secure payment architecture before merchant activation.

## REQ-50-014 — Windows Product image pixel dimensions
Status: `SOURCE IMPLEMENTED / CI TESTED / INCLUDED IN NEXT OWNER-ACCEPTED EXE`
Each Product image card shows original width × height px.

## REQ-50-018 — Unified Product Admin workspace
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Product edit business order remains: `اطلاعات کالا | تصاویر | فروش و موجودی | پروفایل‌ها و سایز/وزن | قیمت‌گذاری | ارسال و بسته‌بندی | SEO | اسلایدر صفحه اول | منبع و لایسنس | همگام‌سازی ویندوز`.

## REQ-50-019 — Modern Velzon Admin interaction surface
Status: `PRODUCTION VERIFIED / VISUAL QA CONTINUES`
Full-width list, on-demand filter drawer, modern table/search/actions, section navigation, stable footer and internal-only sidebar scrolling.

## REQ-50-020 — Product likes, saved/favorites, comments and verified-buyer reviews
Status: `REQUESTED / NEXT SCHEMA-BUSINESS PACKAGE AFTER 50.A.2B`
Preserve ProductLike/ProductComment/ProductReview. Add Favorite/Save if absent, engagement counters/Admin visibility and qualifying purchased/paid Product checks for buyer feedback. Dedicated migration/tests/backup required.

## REQ-50-021 — Customer Product profile/size/weight/color/price selector
Status: `PRODUCTION VERIFIED`
Customer Product view obeys list/size/weight/build/size→build/build→size selection, exposes available profile dimensions and price/facts, keeps canonical ProductVariant ID and native fallback, and reuses `/store/api/variant-commerce-options/`.

## REQ-50-022 — Immutable selected-profile checkout and shipping snapshot
Status: `IMPLEMENTED / GITHUB CI TESTED / PRODUCTION MIGRATION NEXT`
Acceptance:
- finalized order item freezes profile name/key/label and customer-visible selection mode/value,
- freezes size/build/material/color/quality, final weight, packaging weight, effective shipping weight, print time and package dimensions,
- Cart/checkout effective weight includes packaging when there is no explicit shipping-weight override,
- order freezes `insured_value` and normalized `shipping_quote_snapshot`,
- current ShippingMethod/rate rules remain fallback; no external carrier claim,
- combined parcel geometry is not invented,
- coupon/VAT/inventory/payment/notification behavior remains authoritative,
- snapshot remains immutable after later ProductVariant edits,
- migration `store.0036_phase50_checkout_snapshot` requires exact Production MySQL verification, fresh backup and rollback.

CI: `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`.

## REQ-50-023 — Fast Windows AI + exact-link grounding + selected-product batch AI
Status: `PRESERVED IN 8.9.0 / WINDOWS PACKAGED CI PASS / OWNER LOCAL QA PENDING`
Acceptance:
- Product edit/AI must not rebuild global Products gallery on every save/request,
- large catalog remains usable and older products are never discarded,
- exact saved mother AI Provider/Model/key controls Product AI including OpenRouter/AvalAI; no hidden fallback/model scan,
- normal Product AI factual payload contains only Product title + one bounded text body,
- exact source page facts are extracted first and organized under headings; unsupported facts are not invented,
- raw HTML/auth/cookies/secrets and unrelated price/stock/workflow state are excluded,
- main AI action completes Persian title/content/SEO and selected image alt/title/caption/metadata/finalization,
- selected Products support the same exact-link operation in batch,
- batch errors are isolated per Product, stop is operator-controlled and global Products refresh occurs once at batch end,
- Product price/stock/availability/business selections remain untouched by editorial AI,
- Windows regression + launcher + one-file build + frozen browser smoke must pass before Local owner QA.

Implementation: Phase49.3I.29 + 49.3I.31; version `8.8.2`, build `2026.08.26.2`. Targeted CI run `32996526852` PASS; Windows packaged run `32997106056` PASS on runtime snapshot `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`.

## REQ-50-024 — Product source link must never disappear from unrelated actions
Status: `IMPLEMENTED 49.3I.32 / TARGETED + PACKAGED WINDOWS CI PASS / OWNER QA PENDING`
Acceptance:
- Save, silent Save, AI, close, refetch, image actions and publish-related flows must not erase an already persisted canonical Product source URL merely because mirrored URL controls are temporarily blank,
- intentional non-empty URL edits remain supported,
- a missing URL is never guessed,
- a Product already damaged by the old bug should recover the exact previous HTTP/HTTPS URL from local Product history, or matching discovery identity when history is unavailable,
- recovery does not use the network and updates canonical `source_url`, `normalized_url` and fingerprint consistently,
- recovery is recorded in Product history/diagnostics,
- no Product price/stock/material/color/business state or AI provider/model is changed by this guard.

Verification: targeted run `32996526852` PASS; packaged Windows run `32997106056` PASS. Remaining acceptance is Local owner QA of a healthy linked Product, the already affected Product, OpenRouter/AvalAI live exact-link AI and selected-Product batch behavior.

## REQ-50-025 — Product Profile Matrix shared by Windows and Storefront
Status: `IMPLEMENTED 49.3I.34 + 50.A.2D / GITHUB CI TESTED / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- Product Step 2 can add a Profile or clone the selected Profile so Profile 2 initially equals Profile 1 and then diverges safely,
- each Profile owns its own size, final/material weight, price, print time, actual part dimensions, build mode, material, color, quality, package weight/dimensions, stock/default/sort state,
- examples such as size 20 with 100/150/200 g and size 30 with 150/200/300 g are represented as separate real orderable ProductVariants,
- customer selection supports size→weight and deeper configured hierarchies,
- selecting a size shows only valid downstream options for that size,
- later selections never hide valid upstream choices,
- price badges for a weight/profile are scoped to the selected upstream size/choices,
- selected Profile is the single Product detail price/facts authority,
- the same Desktop profile payload is persisted and transported through the existing Catalog batch boundary; no separate hidden Store dataset,
- manual server-side Variants outside the Desktop-managed namespace are preserved,
- selected Profile part dimensions and existing shipping/package facts are frozen on successful checkout,
- Profile content and Storefront presentation remain safe when JS/API progressive enhancement is unavailable,
- Production migration chain is verified and backed up before any schema write.

Verification:
- Windows Catalog Center 8.9.0 build `2026.08.27.2`, workflow `33051114515` PASS on `b3280dd67cd7772f337f6792036ea92d3f252747`; artifact ID `9637671099`, EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`,
- Web runtime snapshot `7d0a2a1125e8f38771ba325427d1efa8b8d07da6`, Profile Matrix CI `33051311828` PASS, 15 Store/Profile/Checkout tests PASS and `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- pending Production migrations: `0036 → 0037 → 0038` subject to fresh read-only MySQL verify + backup.


## REQ-50-026 — Operator-ledger Profiles, resilient AI and brand-aware filament offers
Status: `IMPLEMENTED 49.3I.35 + 50.A.2E / SUPERSEDED BY CATALOG 8.9.6 QA TRACK / PRODUCTION NOT DEPLOYED`

Acceptance:
- Product Step 2 uses the upper controls as a working form and registered Profiles as the transport/publish authority,
- registering a Profile snapshots current fields; new Profile can load the latest snapshot without mutating older Profiles,
- Profile production supports multiple `weight | print time | support weight` rows,
- quick/basic Product page no longer owns fixed price/weight/Profile authority,
- material/color has select-all, clear and local-register actions without global Product-list refresh,
- material offers preserve material + brand + manufacturer + color + roll weight + stock rolls + purchase/sale/USD/FX facts,
- customer sale-rate uses the highest positive explicit sale basis; FX is never guessed,
- same material/color from different brands remains distinguishable and orderable,
- synchronized roll stock participates in color availability when no real spool rows exist,
- AI dialog exposes preflight/progress/send/wait/reply/apply state, retries up to the configured attempt count and uses only explicit configured fallbacks,
- bulk AI isolates Product errors and does not refresh the complete Products list per item,
- editorial AI does not own material/color,
- manual SEO review can accept complete actual Persian SEO without another AI call,
- manual source review cannot bypass invalid commercial-license policy,
- support weight + filament brand/manufacturer freeze into historical StoreOrderItem snapshots,
- migration `0039` reaches Production only after exact MySQL verification, fresh backup and rollback.

Verification:
- Store run `33059883188` PASS through migration `0039` and 16 regressions,
- Smart/Profile 31–35 run `33060613937` PASS,
- Single-AI run `33060613914` PASS,
- Windows portable run `33060047878` PASS,
- Catalog Center `8.9.1` / build `2026.08.27.3`,
- artifact ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- Owner Local automated gate: PASS at `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`; Local SQLite `0039` applied; 16 Store regressions + 107 Catalog tests PASS; Production untouched,
- 8.9.1 foreground launch then exposed `ERR-49-059` before visible UI; 8.9.2 fixes the pack/grid parent collision,
- 8.9.2 startup hotfix run `33066468014` PASS, but owner Product Workspace QA then exposed `ERR-49-060`,
- 8.9.3 fixes `ERR-49-060` by using the installed namespaced Profile lookup,
- 8.9.3 run `33067618679` PASS; artifact `9644438652`; EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`.

## REQ-50-027 — Permanent crawl ledger, reject/purge tombstones and one stage-scoped AI engine
Status: `IMPLEMENTED 49.3I.38 / GITHUB CI + WINDOWS PORTABLE PASS / OWNER LOCAL VISUAL QA NEXT / PRODUCTION NOT DEPLOYED`

Acceptance:
- healthy existing Browser/Crawl/Parser/image/file receive behavior is preserved and extended rather than replaced,
- every crawled/received Product identity remains durably known in the Catalog ledger,
- previously collected/rejected/blocked Product links do not become new receive work when the same source/listing is scanned again,
- a repeated Listing can continue deeper after already-known results so requesting another 100 Products can skip the first known 100 and queue the next 100 new identities,
- operator can permanently reject an unwanted Product, remove its local acquired files/images and still retain source URL/external ID as a rejection tombstone,
- physical purge is restricted to the Product directory below the canonical Catalog `collected/` root and fails closed outside that boundary,
- rejected/blocked Direct Link identities are checked before Browser/HTTP/image/file acquisition,
- explicit operator restore is the only action that permits a rejected identity to be received again,
- Product AI has one configured engine/Provider/Model/retry/fallback authority,
- Product AI source mode remains exactly Link / Saved-Crawled Data / Screenshot,
- selected-Product Bulk Content/SEO calls the same mother orchestrator rather than a separate AI implementation,
- a single Product can explicitly clean/complete only one selected unlocked Stage,
- Stage 4 cleanup may replace/clean Content/SEO but cannot change Profile, price, material, Source, images, slider or other out-of-scope stages,
- finalized/locked stages are immutable until the operator presses `اصلاح`,
- Commerce and Publish remain operator-owned,
- image-only AI work does not call a Provider when image SEO/metadata is already complete,
- no full Products Explorer rebuild occurs per Product during bulk AI.

Verification:
- runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`,
- Catalog Center `8.9.6` / build `2026.08.27.8`,
- Phase49.3I.31–38 run `33077213590` PASS with 84 tests,
- Single Active AI run `33077239617` PASS,
- Windows Portable run `33077239660` PASS,
- artifact `3DPrintHub-CatalogCenter-v8.9.6`, ID `9648474905`,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`,
- source URL preservation, portable self-verify and browser smoke PASS,
- Production touched = NO.

Rollback:
- `backup/pre-phase49-3i38-crawl-ledger-stage-ai-20260827` → `d1ed566a82d3818aa45a5c720df3e7efcb0044f3`.

Current remaining acceptance:
- owner Local visual/functional QA on the final GitHub docs head,
- then and only then Host read-only audit/backups/deploy/Production verification.

## Change rule
New work extends/wraps mature behavior and must pass CI/Local gate before Production. No schema migration reaches Production without exact MySQL verification, migration plan, successful backup and rollback target. Production uses explicit live branch fetch to `FETCH_HEAD` because host remote-tracking refspec is stale/tag-only. Avoid `/dev/fd` process substitution on this cPanel host.

- ERR-49-070 completes the Stage-5 request end-to-end: clean Catalog DBs must contain `technical_summary_fa`, Stage 5 must visibly show source/designer + Persian license + technical summary + technical-features JSON, and the exact visible license selector must persist through stage confirmation.
