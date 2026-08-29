# PROJECT CHANGELOG


## 2026-08-29 — Catalog Center 8.9.8 Windows Stage Confirmation Recovery (ERR-49-068)
- owner rerun on `0191a07...`: exact prior failure PASS, focused 43-test set PASS, canonical foreground launch PASS;
- real Product 63 still exposed a Windows workflow deadlock: manually filled Stage 1 had no practical visible confirm path and the mature Next flow read persisted readiness before saving current widget values;
- historical comparison confirmed the old 3B footer Next/AI flow and later 3I.36 separate stage-finalization rail had become disconnected in the final visible composition;
- restored fixed footer `✅ تأیید و مرحله بعد →`, `✨ پرکردن ناقص‌ها با AI`, and `✏ اصلاح مرحله`;
- confirm now uses stage-specific persist/finalize before advancing and is reasserted after Wizard refreshes;
- rebound actual already-created legacy Tk AI buttons across the whole Workspace to final 3I.39 callbacks;
- exact source identity tokens may remain inside otherwise-Persian SEO/title/description; arbitrary Latin remains invalid;
- prevented an OpenRouter-shaped key from being sent to another Provider and stopped fallback Providers from inheriting the primary Provider model;
- fixed deferred exception callback by freezing redacted error text before scheduling;
- rollback `backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`;
- Production/Host/Django schema untouched; owner Local focused test + foreground Product 63 QA pending.



## 2026-08-29 — ERR-49-067 Locked-stage Test Fixture Alignment
- owner Local pulled `9f3b765...`, created checksum-verified Catalog SQLite backup, and passed Python compile;
- focused gate ran 43 tests with one deterministic error before foreground launch;
- failing test was the locked Quick/Content immutability regression, but its mocked `seo_description_fa` contained Latin `AI`;
- ERR-49-066 intentionally requires Persian-only SEO title/description, so runtime validation correctly rejected the stale mock before lock behavior was exercised;
- runtime checker remains strict; only the fixture wording was changed to fully Persian placeholders at `38cb415bc12d7ec08943809fd14f3478b3ddac1b`;
- rollback `backup/pre-err49-067-seven-stage-test-fixture-20260829` → `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`;
- Production untouched; owner Local rerun pending.



## 2026-08-29 — Catalog Center 8.9.8 Readiness Ownership / Checker Alignment (ERR-49-066)
- owner Local retest of `c679c66...` passed 12 targeted tests but real Product 63 still remained red after persisted AI content;
- audit proved the final repair loop classified 5 Content defects as AI-fixable, accepted a fallback response, then changed 0 fields and stalled;
- removed duplicate readiness ownership: Persian title is Quick-only; selected-image Alt is Images-only; Content owns descriptions/SEO/search text;
- added persisted source-identity-aware Persian validation for title/description while keeping SEO and keyword/tag/hashtag text Persian-only;
- made `_field_needs_fill()` use the same semantic rules as the readiness checker, including invalid non-empty lists;
- changed guided-wizard red stars/icons/Next gating to use `data_ready/missing_data`, keeping explicit operator finalization separate;
- rebound mature full-AI/link/current-stage aliases to final 3I.39 seven-stage repair authority;
- added focused regressions for stage ownership, source identity, checker/repair agreement, data-ready navigation and final AI entrypoint authority;
- rollback `backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`;
- no DB/schema/media/secret/Host/Production change; owner Local regression/foreground retest pending.



## 2026-08-29 — Catalog Center 8.9.8 SEO Readiness Reconciliation Hotfix (ERR-49-065)
- owner QA confirmed the new professional Stage-2 / seven-stage workspace renders after ERR-49-064;
- seven-stage AI persisted Persian/SEO fields but some red readiness/help widgets remained stale after completion;
- added a post-AI reconciliation boundary that rehydrates the Product from Catalog SQLite, reloads the workspace, refreshes lock/guided-wizard/readiness surfaces, and leaves 3I.40 readiness as the final painter;
- the same reconciliation runs again after a short UI settle delay for both whole-product and single-stage repair;
- source `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4`;
- regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`;
- rollback `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`;
- no Provider/source/Offer/Profile/schema/Host/Production change; owner Local targeted test + foreground retest pending.



## 2026-08-29 — Catalog Center 8.9.8 Owner Visual-QA Hotfix (ERR-49-064)
- foreground owner QA on canonical `D:\\projects\\3DPrintHub` proved the correct 8.9.8 source/branch was running;
- opening Product 63 raised a Tk `pack`/`grid` geometry conflict in `phase49_3i35_operator_ledger.build_material_actions()`;
- the exception occurred before 3I.39/3I.40 ProductWorkspace wrappers completed, explaining why the owner still saw the older Stage-2/SEO UI;
- modern material/color picker presence now suppresses the obsolete 3I.35 Listbox action row instead of mounting it into the grid-managed legacy card;
- added executable regression proving no obsolete `ttk.Frame` mount occurs when the modern picker marker exists;
- source fix `aa37dcf916dfab71409738f7087a171daffe4a0a`;
- regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`;
- rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`;
- Production untouched; owner Local retest is the next gate.


## 2026-08-29 — Catalog Center 8.9.8 / Phase49.3I.40 + Store 0040
- preserved the mature 3I.38 Crawl/Direct Link/parser/image/file acquisition path and extended only the final Stage-2/readiness boundaries;
- Stage 2 now follows manufacturer → filament/material → color → Product Offer registration → pricing → production rows → Profile identity/dimensions;
- fixed multi-brand selection scope so registering eSUN/Bambu/other filtered Offers does not erase previously selected manufacturer Offers;
- separated global filament Offer inventory/rates/preheat from Product-specific fixed price per exact Offer;
- added Catalog color preview with explicit HEX/name fallback and optional filament image access;
- kept production weight/print-time/support in the upstream production rows; Profile identity remains name/size/actual dimensions with snapshot registration;
- hardened readiness UX to distinguish real missing data from complete data waiting for operator finalization;
- blocked cosmetic terminal 100% until final `ai_fixable_count == 0`; remaining AI defects stop below 100 and are reported;
- kept AI source authority at Link / Saved-Crawled Data / Screenshot; Repair is an operation, not another source;
- added Store migration `0040_phase50_filament_offer_operations` for hourly print/supervision, preheat hours/temperature/cost and filament image URL;
- first Store 0040 run `33246706102` failed on Decimal string representation only; migration plan/apply/no-drift had already passed;
- corrected tests to compare Decimal values numerically; Store run `33246843145` PASS with full SQLite migration through 0040 and 21 regressions;
- Catalog targeted run `33247729316` PASS;
- final Single Active AI run `33247815007` PASS;
- Windows Portable run `33247815027` PASS on `55139b909f214f33994d76bc1e6fdfd028b5d6c7`;
- Catalog Center `8.9.8` / build `2026.08.29.2`;
- artifact `3DPrintHub-CatalogCenter-v8.9.8`, ID `9713426658`;
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`;
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`;
- rollback branch `backup/pre-phase49-3i40-commerce-readiness-20260829` → `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`;
- Production untouched; owner Local SQLite 0040 + 31–40 visual/functional QA is next.


## 2026-08-27 — Catalog Center 8.9.6 / Phase49.3I.38
- preserved the mature Browser/Crawl/Parser/image/file receive pipeline and extended only its identity/continuation boundaries;
- added permanent crawled/received Product ledger UI over the existing `discovered_urls` authority;
- added persisted `crawl_listing_state` continuation cursor so repeated Listing scans go deeper instead of repeatedly stopping at the first fixed discovery window;
- verified the 100+next-100 contract: 100 previously collected identities are skipped and Products 101–200 become the next 100 pending entries;
- added `رد دائمی + حذف فایل‌ها و عکس‌های محلی`: local Product acquisition files are purged while source URL/external ID remain as a `rejected` tombstone;
- physical deletion is restricted to the Product directory below Catalog `collected/`; out-of-bound paths fail closed;
- fixed `ERR-49-062`: Direct Link now checks terminal rejected/blocked identity before browser/HTTP/image/file acquisition;
- fixed `ERR-49-063`: category/site crawl now persists bounded deeper scroll progress while keeping the mature `discover_classic()` implementation;
- explicit restore is required before a rejected identity can be received again;
- kept one Product AI engine with Link / Saved-Crawled Data / Screenshot inputs and the same configured Provider/Model/retry/fallback authority;
- added optional Stage write scope to the same resilient orchestrator;
- Products bulk Content/SEO now uses that same engine with Stage 4 scope rather than a separate AI path;
- added single-stage cleanup/completion; out-of-scope and finalized stages remain immutable;
- image-only scoped AI makes no Provider request when image SEO is already complete;
- runtime `c904193a7f0af9aad80365834ec3f0b856e77dc9`;
- Phase49.3I.31–38 run `33077213590` PASS with 84 tests;
- Single Active AI run `33077239617` PASS;
- Windows Portable run `33077239660` PASS;
- Catalog Center `8.9.6` / build `2026.08.27.8`;
- artifact `3DPrintHub-CatalogCenter-v8.9.6`, ID `9648474905`;
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`;
- artifact ZIP digest `sha256:13ae8582be09b71f90e607c2230075d875b7445f8a46b6462a9241edf9d52563`;
- browser smoke, portable self-verify and source URL preservation gate PASS;
- rollback branch `backup/pre-phase49-3i38-crawl-ledger-stage-ai-20260827` → `d1ed566a82d3818aa45a5c720df3e7efcb0044f3`;
- Production untouched; owner Local visual/functional 3I.38 QA remains the next gate.

## 2026-08-27 — Catalog Center 8.9.5 / Phase49.3I.37
- added one persisted Product AI source mode: Link / Saved Data / Screenshot;
- replaced visible per-run Product AI modes with one missing-only seven-stage orchestrator shared by single and selected-Product bulk runs;
- separated stage data completion (`✅`) from operator finalization (`🔒`) and persisted finalization locks in Catalog SQLite;
- AI now skips finalized stages and never owns Profile/price/material/color/brand/stock/publication fields;
- fixed `ERR-49-061`: both `sales_profile_ledger_json` and legacy `sales_profiles_json` are protected by the Commerce lock;
- unified Persian identity/SEO validation; `Twistmas Tree` is normalized to `درخت کریسمس اسپیرال`, with mixed Cyrillic/unrelated Latin SEO contamination rejected;
- kept image rename/WebP generation deterministic and separate from AI; AI image ownership is SEO metadata only when missing;
- upgraded Product-page Screenshot to a selected site image with SEO/metadata and preserved `source_page_url`;
- runtime `8d5e58a839c89eedbe258d9236889834fc02d9a9`; targeted run `33074245603` PASS (77 tests); Single Active AI `33074245489` PASS; Windows run `33074245604` PASS;
- artifact ID `9647216177`; EXE SHA256 `4a3e15a3c475460c2dac035cedcd8ccebb40107fec6360b7be6a313f69186079`;
- Production untouched; owner Local visual 3I.37 acceptance remains the next gate.


## 2026-08-27 — Catalog Center 8.9.3 Profile Workspace Binding Hotfix
- owner 8.9.2 diagnostic confirmed startup success, then Product 305/303 open callbacks failed with `AttributeError: ProductWorkspace has no attribute _profile_by_key`,
- recorded as `ERR-49-060`,
- fixed 3I.34 selected Profile loader to call installed namespaced `_phase49_3i34_profile_by_key`,
- added executable non-Tk wrapper-binding regression,
- backup anchor `backup/pre-err49-060-profile-matrix-bind-fix-20260827` → `6f9334705c74a65d47473580944d79d61d501293`,
- bumped release atomically to Catalog Center `8.9.3` / build `2026.08.27.5`,
- targeted run `33067612565` PASS,
- Single Active AI run `33067618639` PASS,
- Windows portable run `33067618679` PASS on `9637829a255a1d09800bc062c2f049cf5d92b585`,
- artifact `3DPrintHub-CatalogCenter-v8.9.3`, ID `9644438652`,
- EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`,
- artifact ZIP digest `sha256:216b62072fd95a0a4d292b28ce99605fd60f3e4d9622d06987d6fe5b434e6141`,
- Production untouched; owner foreground Product Workspace QA remains required.


## 2026-08-27 — Catalog Center 8.9.2 Visible Startup Hotfix
- owner foreground 8.9.1 launch exposed a real Tk startup failure: 3I.35 AI-resilience settings used `grid` directly inside UX87 `settings_tab`, whose existing children use `pack`,
- root cause matches permanent `ERR-49-001`; incident recorded as `ERR-49-059`,
- fixed only the outer AI-resilience panel to `pack(fill="x", padx=8, pady=8)`; internal panel controls remain grid-managed safely,
- added regression `test_ai_resilience_settings_respects_pack_managed_settings_tab`,
- bumped release atomically to Catalog Center `8.9.2` / build `2026.08.27.4`,
- targeted 31–35 run `33066472847` PASS,
- Windows portable run `33066468014` PASS on `9bd9d0b4cd070a35c82c6ecefd6f6b3027b20284`,
- artifact `3DPrintHub-CatalogCenter-v8.9.2`, ID `9643957471`,
- EXE SHA256 `fac29fc610215cfc4115fcdb4c005fc69f99c3e6569b44c501d63ec82d6ba257`,
- artifact ZIP digest `sha256:78a371693563b3293d7b49e39e5acd8dbf3032be9f6fee1b5252fffc5a29d0fb`,
- Production untouched; owner foreground visual QA remains required.


## 2026-08-27 — Owner Local 3I.35 / 50.A.2E Automated Gate PASS
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
- next gate is manual owner visual/functional QA; no Host/Production operation performed.


## 2026-08-27 — Local Owner Gate PowerShell DB Probe Runbook Fix
- owner Local checkout fast-forwarded cleanly to `35ab63105f30fdca42518d5273a424a3200977e3`,
- packaged-runtime/tooling ancestry and Catalog SQLite backup passed,
- the wrapper stopped before any new migration because multiline PowerShell `python -c` quoting corrupted the embedded Python DB detector,
- recorded as `ERR-49-057`; this is a command-transport defect, not a Django/schema failure,
- resume procedure now uses a single-quoted PowerShell here-string piped to Python stdin, then backs up the effective Local Django SQLite DB before migration,
- Production remains untouched.


## 2026-08-27 — Phase49.3I.35 / Phase50.A.2E — Operator Ledger, Resilient AI and Brand-aware Filament
- Catalog Center bumped to `8.9.1`, build `2026.08.27.3`,
- replaced duplicate Profile editing surface with accounting-style registered Profile ledger while preserving the mature 3I.34 transport,
- working form now registers independent Profile snapshots; new Profile can load the latest snapshot safely,
- production rows now model Product weight, print time and support weight,
- quick/basic Product page no longer owns fixed-price/weight/Profile authority,
- material/color UI adds select-all and local-register without full Products refresh,
- added material + brand + manufacturer + color + roll stock/purchase/sale/USD/explicit FX offer facts,
- dynamic formula pricing consumes effective brand/color sale rate; FX is never guessed,
- added observable AI preflight/progress/retry/failover and per-Product bulk isolation,
- added manual SEO readiness and source-review controls without commercial-license bypass,
- migration `0039_phase50_filament_offer_pricing` adds brand-aware offer fields, Variant support weight and immutable order support/brand/manufacturer snapshots,
- Storefront distinguishes same material/color across brands and exposes brand/manufacturer/support in selected Profile/API,
- fixed migration metadata drift `ERR-50-016` without creating a fake 0040,
- fixed stale 8.9.0 config + retired quick-price test contract `ERR-49-056`,
- Phase50 run `33059883188` PASS: no migration drift, clean CI migration through `0039`, 16 regressions PASS,
- Smart/Profile 31–35 run `33060613937` PASS,
- Single-AI run `33060613914` PASS,
- Windows portable run `33060047878` PASS on runtime `2622818d898e19b745c61ff653b80c03d22288f1`,
- artifact `3DPrintHub-CatalogCenter-v8.9.1`, ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- Production remains unchanged at `c283864290f9c989a9fcdf24ee8eef519560e917`; last verified DB has `0034/0035` only and owner Local QA is required before any `0036 → 0037 → 0038 → 0039` Production work.


## 2026-08-27 — Product Profile Matrix 49.3I.34 / 50.A.2D — GitHub CI Tested
- Catalog Center 8.9.0 build 2026.08.27.2 now has a Step-2 Product Profile Matrix with add/clone/delete/edit profile workflow,
- every profile can independently own size, final/material weight, fixed price, print time, part dimensions, build, material, color, quality, package facts, stock/default/sort state,
- Desktop profile JSON travels through the mature batch/import boundary and idempotently becomes canonical Django ProductVariant rows; unrelated manual Variants are preserved,
- added compound customer modes including size→weight and 3-level size/weight/build flows,
- migration `0037` adds professional pricing/shipping/payment policy; migration `0038` adds profile descriptions, size↔weight modes and actual part dimensions with immutable order-item snapshot dimensions,
- Storefront selected Profile is the single product price/facts authority; navy/gold presentation aligns with the Catalog Center visual language,
- fixed Variant API callable price-contract bug (ERR-50-012),
- fixed saved-address checkout rejection in the shipping policy wrapper (ERR-50-013),
- fixed dependent selector hierarchy so downstream state cannot hide upstream choices and weight/profile prices are scoped to the selected size (ERR-50-014),
- added dedicated Node behavior gate `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- Web CI `33051311828` PASS on runtime snapshot `7d0a2a1125e8f38771ba325427d1efa8b8d07da6`; migrations through `0038` and 15 Store/Profile/Checkout tests PASS,
- Windows release trigger now watches mature Product studio files (ERR-50-015),
- Windows portable run `33051114515` PASS on `b3280dd67cd7772f337f6792036ea92d3f252747`; artifact ID `9637671099`; EXE SHA256 `32aed719e6d374447fc4b05f09a30fe12f0ce4dc05e570382f2e74036044900c`,
- Production remains unchanged at `c283864290f9c989a9fcdf24ee8eef519560e917`; Local owner QA + fresh Host/MySQL audit/backup are required before the pending `0036 → 0037 → 0038` chain.


## 2026-08-27 — Catalog Center Local Gate Self-Dirty Hotfix
- root cause of the reported “does not come up” log was not a startup exception: the gate stopped before `-LaunchApp` because a prior portable build left untracked `catalog_center/release/` output,
- added `/catalog_center/release/` to `.gitignore` without deleting existing local EXEs/manifests,
- added regression coverage so generated portable output stays outside Git status,
- Windows portable CI run `33042158052` PASS on `1a490fecb5a22b855c4f10a12bb74f04a28c57b9`; one-file build/self-verify and artifact upload PASS; release publication remains manual pending owner QA.

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-26 — Phase49.3I.32 Canonical Product Source URL Guard — Packaged Windows CI PASS
- root cause confirmed in mature `ProductStudio.save()`: both mirrored URL controls could be temporarily blank and generic/silent Save would overwrite `source_url`, `normalized_url` and fingerprint with empty identity,
- silent Save is reused by close/refetch/AI/publish/layered Workspace actions, explaining why an unrelated button could appear to delete the Product link,
- added final additive `phase49_3i32_source_url_guard.py` after 49.3I.31; existing canonical URL is fed into both URL controls before the mature Save chain when both are blank,
- explicit non-empty main/spec URL edits remain supported,
- defensive post-save invariant restores canonical URL/normalized URL/fingerprint if a legacy layer still erases it,
- already damaged Products can recover the exact prior HTTP/HTTPS source URL locally from Product history, with matching `discovered_urls(source_code, external_id)` as fallback; no network or guessed/reconstructed URL,
- recovery is recorded in Product history/diagnostics,
- Catalog Center candidate remains `8.8.2`, build `2026.08.26.2`,
- targeted Phase49.3I.31-32 CI run `32996526852` PASS on `2ca69c4928333fc15247b99014a8fe77d781b50b`,
- first Windows packaged run `32996526842` failed only on one stale legacy test literal expecting 8.8.1; new source-link tests were already PASS,
- replaced stale release literal with runtime-version == package-manifest-version contract,
- Windows packaged rerun `32997106056` PASS on `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`: full regression, launcher composition, source URL invariant, one-file EXE build/self-verify, release-manifest/SHA256 verification and immutable artifact upload PASS,
- Actions artifact `3DPrintHub-CatalogCenter-v8.8.2` created as artifact ID `9617048629`,
- automatic public release publication disabled; release is explicit/manual only after owner Local QA.

## 2026-08-26 — Catalog Center 8.8.2 Smart Link + Batch AI — GitHub Candidate
- Phase49.3I.29 Windows performance base: 48-card Product presentation paging, full SQLite result preservation, deferred global Product refresh and exact saved mother Provider/Model execution without hidden Product model scans,
- Phase49.3I.31 unified Product AI: exact Product URL validation/fetch, canonical source identity, safe source facts flattened into one heading-structured text body, Persian content/SEO and selected-image metadata/finalization,
- normal Product AI transmits only `source_title` + one `source_description` text field; raw HTML, auth/cookies/secrets and unrelated pricing/stock/workflow state stay local,
- main Product AI/link actions converge on the same grounded runtime boundary,
- Products Explorer supports selected-product batch AI using each Product's own exact source URL, isolated per-item errors/cancel and one global Products refresh at batch end,
- mother AI settings remain authoritative for AvalAI/OpenRouter/Google/OpenAI; no cross-provider fallback.

## 2026-08-26 — Phase50.A.2B Immutable Checkout/Profile/Shipping Snapshot — GitHub CI Tested
- added migration `store.0036_phase50_checkout_snapshot`,
- StoreOrderItem immutable profile/selection/final-weight/shipping-weight/print-time snapshots,
- existing `0034` size/build/packaging-weight/package-dimension snapshots populated during successful checkout,
- StoreOrder `insured_value` + normalized `shipping_quote_snapshot`,
- mature Phase6 validation/coupon/inventory/address/notifications/payment remains authoritative,
- checkout finalization uses outer atomic boundary, effective shipping weight and ShippingMethod fallback without inventing external carrier contracts,
- integration regressions prove snapshot immutability and payment/shipping synchronization,
- `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`,
- Production remains at `c283864290f9c989a9fcdf24ee8eef519560e917`; `0036` not yet applied.

## 2026-08-26 — Phase50.A.1H + Phase50.A.2A Production Verified
- Production fast-forwarded to `c283864290f9c989a9fcdf24ee8eef519560e917`,
- rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`,
- MySQL `store.0034` + `0035` applied; no new migration executed,
- Admin shell stability and Storefront sales-profile selector deployed and verified,
- Home/Store/Admin/Product/static/Variant API healthy; public Home private imported-media refs = 0.

### Deployment-verifier incidents
- cPanel `/dev/fd` process-substitution failure corrected with Python enumeration (`ERR-50-010`),
- JSON verifier execution mistake corrected with `python - <json-path> ...` + `json.load` (`ERR-50-011`).

## 2026-08-26 — Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Profile Selector
- Admin CI `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- Storefront CI `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

## 2026-08-26 — Phase50.A.1G Velzon Operator Surface V2
- on-demand filter drawer/full-width lists,
- CI `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

## 2026-08-26 — Phase50.A.1F Business Admin Navigation / Product Admin 500 Fix — Production Verified
- fixed Product changelist SafeString numeric-formatting 500,
- deployed/verified at `bc7b97f9c63432b8105f52f61cf5cdae1369689b`.

## 2026-08-26 — Phase50.A.1E Production Deployment Verified
- deployed `9cfbc54ed4196144864b5f4201976d8466a88134`,
- backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-114327`,
- `0034`/`0035` applied; HTTP/private-media gates PASS.

## 2026-08-26 — Phase50.A.1E Unified Product Admin Workspace
- business-ordered Product workspace preserving mature Product/Profile/Variant/SEO contracts,
- CI `32941662288` PASS on `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

## 2026-08-25 — Phase50.A.1C Admin Media / Mobile / SEO / Windows Dimensions
- safe ImportedPrintAsset Admin public-media resolver, compact mobile Hero, homepage SEO audit and Windows image dimensions; CI PASS.

## 2026-08-25 — Phase50.A.1B Product Gallery + Variant 2.0 Foundation
- Product gallery/lightbox, Variant2 size/build/package fields, StoreOrderItem snapshots, `store.0034`; CI PASS.

## 2026-08-25 — Catalog Center Windows v8.8.1 Final Portable Release
- released `3DPrintHub-CatalogCenter-v8.8.1.exe`, build `2026.08.25.2`, SHA256 `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`.

## 2026-08-25 — Phase50.A.1 Admin Storefront / Hero Parity
- Product/imported-asset Hero controls and Storefront/Coupon/Shipping/Pricing/address Admin surfaces.

## 2026-08-25 — Phase50.A Admin Command Center
- authenticated `/admin/command-center/` organized around Sales, Treasury, Accounting/Ledgers, Purchasing and Inventory/Production.

## 2026-08-25 — Phase49.3I Production closeout
- Product-owned public Hero media, structured web Product presentation and verified Production deploy; imported Catalog working-media remained private.
