## 2026-09-15 - 50.A.3 - Secure ZarinPal current API compatibility LOCAL_TESTED
The mature Phase30 quote-payment engine is retained as the security authority. Current live defaults now use `payment.zarinpal.com` v4 request/verify and StartPay; Verify sends only merchant ID, exact provider amount and Authority. Sandbox remains on `sandbox.zarinpal.com`. Production is still fail-closed: env toggle false, Site toggle false, Merchant ID absent, zero gateway rows.

Local acceptance: provider + online-payment suites 17/17 PASS, Django check, no migration drift, payment audit and diff-check PASS; Host outbound TLS to live/sandbox hosts PASS. Broad Store 6F/9E were reproduced identically on pre-change SHA `1a29e225...`, so they are documented baseline debt, not this delta. Dedicated runner is no-migration/no-DB-write/no-collectstatic/no-enable from exact Production `b1caeba...`.

Next: commit/push -> guarded reverse-tunnel deploy -> Production runtime/public verification -> implement REQ-50-010 StorePayment wiring into the same secure architecture before any merchant activation.

## 2026-09-15 ? Handoff baseline for next Phase50 work
Client handoff is Production-complete at exact clean `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`: guarded source deployment, empty imported Store, preserved master/source/Portfolio/Hero state and Hero 50.3.0 browser acceptance all PASS. Store reset is rollback-backed and must not be repeated. The next Finance/Commerce/Admin work must branch from this verified empty-Store baseline and preserve the existing StoreOrder/Payment/Invoice/accounting safety contracts.

# Phase50 - Finance, Commerce & Admin Command Center

Updated: 2026-09-15
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Current Subphase: `50.A.3 - Secure ZarinPal`
Status: `50.A.3 CURRENT-API COMPATIBILITY LOCAL_TESTED / COMMIT+PUSH+GUARDED DEPLOY NEXT / STOREPAYMENT WIRING NEXT`
Current verified Production application commit:
`b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`.

Current verified Production MySQL `sfkilvrs_EmiAdmin_3dprinthub` state:
- Store 0036-0042 applied;
- Website 0024 applied;
- authenticated publish-readiness `ready=true`, no blockers;
- Phase50.A.3 ZarinPal compatibility introduces no migration.

## 50.A.2G - Publish-ready Media + Professional Order Wizard
Windows Ready/Publish now requires finalized current SEO WebP artifacts with complete metadata/signature/SHA. Batch packaging carries the exact final filenames/bytes. Django import refreshes changed explicit media but skips identical byte content, keeping re-publish idempotent and visual revisions truthful. Manifest Desktop identity is available before canonical Profile sync.

Storefront keeps canonical size -> color -> material -> quality selection while adding visible progress, guidance, keyboard/touch behavior and desktop/tablet/mobile responsive presentation. ProductVariant/API remains the price/stock/facts authority and native Variant fallback remains available.

Local evidence: Catalog publish/media 10/10 PASS; Django import+Filament/Profile 16/16 PASS; Node 8/8 PASS; Playwright desktop/tablet/mobile/progress/keyboard/touch/cart/fallback/stock/ambiguity/>100 PASS; compile/check/no migration drift/diff check PASS.

Next: commit/push exact delta -> canonical clean-head Windows gate + app launch -> dedicated no-migration A2G Host deployment from exact Production baseline `7d0b3df...` -> one controlled Product Windows-to-Production acceptance before bulk.

## 50.A.2F — Guided Storefront Configurator

Customer selection is simplified to four visible steps: size → color → compatible material → print quality. This is progressive enhancement over the existing canonical ProductVariant/native select; it does not create a second price or availability authority.

Safety contract: upstream-prefix filtering, downstream invalidation, stock/orderability fail-closed, explicit final Variant choice on ambiguous duplicate paths, API-failure native fallback, server price/weight/time authority and no migration.

Local 2026-09-12 evidence: Node 8/8 PASS; focused Django Profile/Filament 15/15 PASS; Playwright real-browser PASS across desktop, 390px mobile, cart post, native fallback, stock, ambiguity and >100 Variant batching; `manage.py check` PASS with known CKEditor warning; `makemigrations --check --dry-run` reports no changes.
## 50.A.2E extension — Filament Offer operations / migration 0040

Migration:
`store.0040_phase50_filament_offer_operations`.

Adds exact manufacturer/material/color Offer operation facts:
- `print_hourly_rate`,
- `supervision_hourly_rate`,
- `preheat_hours`,
- `preheat_temperature_c`,
- `preheat_hourly_rate`,
- `filament_image_url`.

Commerce contract:
- same material/color from different manufacturers remains a distinct Offer,
- stock remains part of orderability,
- optional preheat contributes only when configured,
- fixed Product price remains Product/Offer-specific and does not mutate global filament inventory/rate facts,
- Store selector keeps manufacturer → material → color identity and exposes swatch/image/stock/preheat facts,
- no implicit FX or material identity is invented.

Verification:
- initial 0040 workflow `33246706102` reached successful no-drift/migration-plan/migration-apply gates but two regression assertions froze insignificant Decimal string scale,
- corrected numeric assertions at `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`,
- workflow `33246843145` PASS: compile, JS, selector behavior, Django check, no drift, plan, full CI SQLite migration through 0040 and 21 regressions.

Production:
- last terminal-verified Production still has only `0034` and `0035` claimed applied,
- `0036 → 0037 → 0038 → 0039 → 0040` is only a possible pending chain and must be freshly verified read-only on MySQL before any write,
- owner Local 0040 backup/apply/regression + 3I.40 visual QA is required before Host work.

## Preserved foundation
- Product/Catalog/Bridge/Hero public media is Product-owned; imported Catalog working-media remains private.
- Product, ProductCatalogProfile and ProductVariant remain authoritative.
- mature Phase6 Checkout, Coupon/VAT, StoreOrder/StorePayment/StoreInvoice, inventory reservation, addresses and notifications remain authoritative.
- no permanent Production source edits.
- purchased/private Velzon/font assets remain private/gitignored.
- Admin shell footer/290px sidebar/internal menu scroll and initial Storefront Profile selector remain Production verified at `c283864...`.

## 50.A.2B — Immutable Checkout/Profile/Shipping Snapshot
Migration:
`store.0036_phase50_checkout_snapshot`.

Adds immutable order state for:
- profile name/key/label,
- selection mode/value,
- final/effective shipping weight,
- print time,
- insured value and normalized shipping quote.

Reuses `0034` item size/build/package fields.

Runtime:
- wraps mature checkout rather than replacing it,
- successful checkout finalizes inside an outer transaction,
- packaging weight participates in shipping weight unless explicit shipping override exists,
- Coupon/VAT/inventory/payment/notification logic remains authoritative,
- no combined carton geometry or external carrier quote is invented.

## 50.A.2C — Professional Commerce Policy
Migration:
`store.0037_phase50_professional_commerce_policy`.

Adds:
- Product pricing policy: formula/product fixed/profile fixed/profile+material/profile+material+color,
- Product sales notice,
- optional strict color-stock enforcement,
- ProductVariant fixed price override,
- shipping service type/scope/fee mode/address/postal/customer notice,
- StorePaymentSettings,
- safe shipping presets with Post/Tipax disabled by default until operator configuration.

Runtime bug fixed:
- saved-address checkout now validates shipping policy against the actual persisted address rather than empty new-address form fields (`ERR-50-013`).

## 50.A.2D — Product Profile Matrix
Migration:
`store.0038_phase50_profile_matrix`.

### Requested delta
A single Product may have many customer-selectable production Profiles, for example:
- size 20 cm → 100 g / 150 g / 200 g,
- size 30 cm → 150 g / 200 g / 300 g,
- optionally deeper build/material/color/quality combinations.

Every Profile is a real orderable Variant with its own price and production/shipping facts.

### Windows / Catalog contract
Phase49.3I.34 adds a Step-2 Profile editor:
- + new Profile,
- clone selected Profile,
- delete Profile,
- edit Profile,
- one default Profile,
- active/inactive and sort order.

Per Profile:
- name/description/key,
- size label,
- final/material weight,
- print time,
- fixed price,
- actual part L/W/H,
- build profile,
- material/color/quality,
- packaging/shipping weights,
- package L/W/H,
- stock mode/quantity.

The Product-owned Profile list persists as `sales_profiles_json` in Catalog SQLite and is included in the mature editorial batch payload.

### Django / Store contract
Desktop-managed Profiles are synchronized into canonical `ProductVariant` rows:
- stable `sales_profile_key` identifies a Profile,
- collision-safe Desktop-managed Variant codes,
- republish updates existing Profile rows,
- removed Desktop Profiles are deactivated only inside the Desktop-managed namespace,
- unrelated manual server Variants remain untouched,
- first/explicit default Profile is preserved,
- invalid stock/material/quality/color state fails closed instead of silently inventing a mapping.

Product is switched to Variant order mode and Profile pricing policy when Profile fixed prices exist.

### Storefront contract
Supported Profile modes:
- list,
- size,
- weight,
- build,
- size→build,
- build→size,
- size→weight,
- weight→size,
- size→weight→build,
- size→build→weight.

The selected Profile is the single displayed price/facts authority.

Professional Profile summary includes:
- Profile name/description,
- price,
- size,
- build,
- material/color/quality,
- final weight,
- actual part dimensions,
- effective shipping weight,
- print time,
- package dimensions.

Dependent selector semantics:
- each option group is filtered only by the choices before it,
- downstream selections never hide valid upstream options,
- changing size clears/re-resolves downstream state to a valid canonical Variant,
- weight/Profile price badges are calculated only from the active upstream prefix,
- native Variant select remains the fallback contract.

### Checkout snapshot extension
`0038` adds immutable part L/W/H fields to StoreOrderItem. A later ProductVariant edit cannot mutate the ordered Profile dimensions.

## 50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot
Migration:
`store.0039_phase50_filament_offer_pricing`.

Adds to `MaterialColorOption`:
- filament brand,
- manufacturer/factory,
- roll weight,
- synchronized roll-count stock snapshot,
- purchase price per roll,
- sale price per roll,
- USD price per roll,
- explicit USD/Toman FX snapshot.

Adds:
- `ProductVariant.support_weight_grams`,
- immutable `StoreOrderItem.support_weight_grams`,
- immutable `StoreOrderItem.filament_brand_name`,
- immutable `StoreOrderItem.filament_manufacturer_name`.

Pricing/stock semantics:
- effective offer rate is the highest positive explicit sale basis,
- USD pricing participates only with an explicitly stored FX rate,
- current stock uses matching real spool remaining grams first, then roll-count × roll-weight snapshot,
- purchase price is stored for inventory/accounting and does not silently become customer sale price.

Storefront/checkout:
- same material/color with different brands remains a distinct customer choice,
- selected Profile summary/API include brand/manufacturer/support facts,
- successful checkout freezes those facts so later stock/brand edits cannot mutate old orders.

Verification:
- run `33059883188` PASS,
- no migration drift,
- migration through `0039` PASS on clean CI SQLite,
- 16 Store/Profile/Checkout tests PASS.

## Verification

### Web runtime
Snapshot:
`7d0a2a1125e8f38771ba325427d1efa8b8d07da6`.

GitHub Actions:
`Phase50 Variant2 + Profile Matrix CI` run `33051311828` PASS.

Gates:
- touched Python compile PASS,
- Storefront JS syntax PASS,
- `PHASE50_PROFILE_SELECTOR_HIERARCHY=PASS`,
- Django check PASS with known warning debt only,
- no model/migration drift,
- CI migration through `0038` PASS,
- 15 Variant/Profile/Checkout tests PASS.

### Windows runtime
Catalog Center:
- version `8.9.3`,
- build `2026.08.27.5`,
- packaged snapshot `9637829a255a1d09800bc062c2f049cf5d92b585`,
- workflow `33067618679` PASS,
- artifact ID `9644438652`,
- EXE SHA256 `fd525fad977f592dc62e68fc3a4310bba98c7ed9689c5101cbdc35589fef7bed`.

Public GitHub Release remains manual-only after owner Local QA.

### Owner Local automated gate
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

## Resolved incidents in this subphase
- `ERR-50-012`: API executed bound pricing contract incorrectly → call canonical `price_breakdown()`.
- `ERR-50-013`: saved-address checkout rejected by wrapper → resolve persisted address facts.
- `ERR-50-014`: selector downstream state constrained upstream choices / cross-size price badge → prefix filtering and upstream-scoped price pool.
- `ERR-50-015`: packaged Windows workflow omitted mature Product studio trigger paths → watch both files.

## Must-not-touch
- historical paid orders,
- mature Coupon/VAT logic,
- inventory reservation,
- public/private media boundary,
- secrets,
- external Post/Tipax pricing without verified official contract/credentials,
- purchased/private Velzon/font assets,
- manual non-Desktop ProductVariants.

## Production deployment gate
1. Owner Local Windows and Django QA on the exact current GitHub head.
2. Read-only verify Host branch/HEAD/worktree/live remote SHA.
3. Verify exact effective MySQL DB and actual `0034..0039` migration rows.
4. Run exact migration plan and stop on any unapproved operation.
5. Verify disk and `mysqldump`.
6. Fresh tracked-source + `.env*` + MySQL backup, gzip/checksum, rollback HEAD.
7. Explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`; verify exact target and ff-only ancestry.
8. Deploy source from GitHub.
9. Re-run Django check/drift/DB/plan.
10. Apply only verified pending chain `0036 → 0037 → 0038 → 0039`.
11. `collectstatic --noinput`.
12. Passenger restart.
13. Verify Home/Store/Admin/Product/Profile API/Checkout/static/private-media.
14. Controlled new-order QA with one multi-size/multi-weight Product; do not rewrite old orders.
15. Owner visual QA.
16. Update Production docs with exact deployed SHA, backup path and migration rows.

## Following Phase50 work
After 50.A.2D Production verification:
- Product Engagement,
- Secure ZarinPal,
- Torob Product API,
- Accounting/Treasury/Purchasing/Sales/Reports.

## Canonical host constraints
- `ERR-50-007`: tag-only fetch refspec → live branch + explicit `FETCH_HEAD`.
- `ERR-50-010`: no reliable cPanel `/dev/fd` process substitution.
- `ERR-50-011`: JSON is data; verify with `python -` + `json.load`.
