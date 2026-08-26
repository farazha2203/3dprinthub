# 3DPrintHub Chat Archive — Phase49/50 Admin, Commerce, Windows Catalog, Deploy & Roadmap

**Archived:** 2026-08-26 11:22 +03:30  
**Repository:** `farazha2203/3dprinthub`  
**Branch:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Purpose:** Preserve the full available project conversation context, owner requests, command evidence, deployment history, defects, design decisions, phase plan and immediate next steps for continuation in a new chat.

> Note: This archive is reconstructed from all conversation content available to the assistant in the active project context. Where the product conversation system had already compacted/skipped older raw turns, the preserved project summaries and exact operational evidence were incorporated instead of inventing missing verbatim text.

---

## 1. Permanent project workflow and owner rules

The owner established the following permanent execution rules for 3DPrintHub:

- Before any technical response, code change, install, migration, deploy, troubleshooting or executable command, read root `AGENTS.md`.
- Then read, at minimum:
  - `docs/CURRENT_STATE.md`
  - `docs/ROADMAP.md`
  - `docs/PATHS.md`
  - `docs/ERRORS.md`
  - `docs/HOST_CONSTRAINTS.md`
  - `docs/00_PROJECT_MASTER_ROADMAP_FA.md`
  - `PROJECT_CONTEXT.md`
  - active phase file under `docs/phases/`.
- GitHub/Repository is the permanent source of truth; chat memory is not sufficient.
- Never guess repository path, branch, commit, Python/Node versions, database, migrations, venv, service, domain, port, host path or deployment method.
- Verify before meaningful change:
  - correct repository/project,
  - current path,
  - `git status`,
  - current branch,
  - latest commit,
  - active phase/epic,
  - previous errors in `docs/ERRORS.md`,
  - Local/Host paths,
  - host constraints,
  - DB/migration state if relevant,
  - backup and rollback need.
- No permanent source code edits directly on Production.
- Development delivery rule:
  `READ DOCS → VERIFY STATE → CHECK PREVIOUS ERRORS → IMPLEMENT → TEST → COMMIT/PUSH → DEPLOY FROM GITHUB → VERIFY PRODUCTION → UPDATE DOCS`.
- No ZIP/patch/source/script delivery through chat for the project; source changes go through GitHub.
- Dirty worktree means stop and inspect; no blind reset/delete cleanup.
- Do not repeat a failed command unchanged unless its underlying condition changed.
- A phase is not complete just because code exists; required tests must pass.
- Sensitive DB/Git/filesystem/migration/deployment changes require verified target, backup and rollback.
- After meaningful changes update relevant docs, especially CURRENT_STATE, ROADMAP, CHANGELOG, ERRORS, REQUESTS and active phase.

The owner later clarified a practical workflow preference:
- Web development should be done against the hosted environment rather than repeatedly using the Windows machine for web QA, while still keeping GitHub as source of truth and avoiding permanent direct Production source edits.
- Windows Catalog Center remains the desktop-side runtime and should ultimately be built as an executable and versioned/released from GitHub.

---

## 2. Canonical project paths and environment

### Windows / Local
- Project root: `D:\projects\3DPrintHub`
- Catalog Center source: `D:\projects\3DPrintHub\catalog_center`
- venv: `D:\projects\3DPrintHub\.venv`
- Local Django DB: `D:\projects\3DPrintHub\db.sqlite3`
- Persistent Catalog root: `D:\projects\3dprinthub-catalog-manager`
- Persistent Catalog DB: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
- Legacy installed data retained under `D:\projects\3dprinthub_catalog_center`

### Production
- Project root: `/home/sfkilvrs/3dprinthub`
- venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- Database: MySQL `sfkilvrs_EmiAdmin_3dprinthub`
- Static: `/home/sfkilvrs/public_html/static`
- Media: `/home/sfkilvrs/public_html/media`
- Private media: `/home/sfkilvrs/3dprinthub/private_media`
- Domain: `https://3dprinthub.ir`
- Passenger restart pattern:
  `mkdir -p tmp && touch tmp/restart.txt`

### Main active branch in this session
`agent/phase49-3i18-operator-bulk-ai-rebuild`

---

## 3. Catalog Center / Phase49 completion context

The user repeatedly tested Catalog Center against MakerWorld search/model links and requested:

- Reliable extraction from MakerWorld exact Product URLs and listing/search URLs.
- No sending of Product images/image URLs to AI for text generation.
- AI should extract/translate/enrich textual Product information while preserving source identity.
- Product Workspace should show canonical staged workflow:
  1. Basic Info
  2. Commerce
  3. Images
  4. Content/SEO
  5. Source/License
  6. Slider
  7. Review/Publish
- Free navigation between stages; publish readiness should block publish, not navigation.
- Images vertically shown and operator-friendly.
- Product cards support selection and bulk operations.
- Discovery should default to 5 source images and maintain separate handling of source screenshot.
- Observable AI progress and no hidden provider/model scans.

Important Phase49 fixes captured during the session:

### 49.3I.27 category provider crash
Owner observed:
`AttributeError: 'Database' object has no attribute 'categories'`

Verified mature provider was `App.get_all_categories()`; a compatibility bridge was added instead of inventing a database categories API.

### 49.3I.28 canonical title contract crash
Owner observed:
`canonical_source_title() got multiple values for argument 'current_title'`

Cause was duplicate binding against mature helper signature. A compatibility adapter was added and focused regression test created.

### 49.3I.29 public Product presentation
The owner reported public Product pages displayed raw internal JSON/intelligence text, including source metadata, AI fields, pricing internals and structured notes. The public page was refactored into customer-readable sections and internal operational fields were hidden.

### 49.3I.30 Hero public-media ownership
Owner compared Local vs Production homepage Hero:
- Local showed Hero Product image correctly.
- Production showed Hero text but blank/dark image area.
- Browser console returned 404 for paths like:
  `/media/store/imported-models/gallery/...`

Root cause:
- imported Catalog working media lives under private/internal `store/imported-models/...`,
- Local DEBUG served broad media and masked the issue,
- Production intentionally only exposes Product/category/SEO public media,
- Hero Studio preferred `ImportedPrintAssetImage.image.url`.

Fix:
- public Hero resolves matching Product-owned gallery copy under `store/products/gallery/`,
- then Product main image,
- only remote source as final fallback,
- imported working-media namespace stays private.

The web release baseline became `web-v49.3I.30` at commit `6a551948dd700061f0f7ae0e586196eded75f5ec`.

---

## 4. Production deploy history from Phase49 to Phase50 baseline

The owner asked to send current web version to Production.

Initial host audit showed Production on `main` at:
`6660cf1d84d46ea8eeaf9246d1b86f6ed41082c7`
with four untracked host-only files:
- `PHASE48_SERVER_BRIDGE_AUDIT.py`
- `deploy/phase43-applied.json`
- `smartbase_admin_bridge/sb_admin.py.broken_20260808_160314`
- `store/test_phase43.py`

A first deploy attempt stopped because the worktree was dirty.

A second guarded deploy:
- verified tracked source clean,
- verified known host-only untracked set,
- fetched exact feature branch,
- verified forward deploy,
- verified MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- created file backup,
- created MySQL backup,
- then failed attempting to create a tracking branch due Git remote-tracking branch semantics.

A later continuation command had accidentally populated tracked changes in the index/worktree while still on `main`, causing a stop under `TRACKED FILES ARE DIRTY`. The workflow was corrected without reset/delete shortcuts.

Eventually Production successfully deployed the approved application version and later the known host-only extra files were removed. Owner output confirmed:

```text
===== BEFORE CLEANUP =====
## agent/phase49-3i18-operator-bulk-ai-rebuild
?? PHASE48_SERVER_BRIDGE_AUDIT.py
?? deploy/phase43-applied.json
?? smartbase_admin_bridge/sb_admin.py.broken_20260808_160314
?? store/test_phase43.py

===== AFTER CLEANUP =====
## agent/phase49-3i18-operator-bulk-ai-rebuild

========================================
PRODUCTION WORKTREE = CLEAN
HEAD=d27489f1c2e1d36e75fdadfa8ab24660d8bec720
========================================
```

A rollback backup from that deployment was retained under:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401`

Later web Phase49.3I.30 Hero fix was deployed and Production public pages were reported OK.

---

## 5. Bridge Token and Windows Catalog operation

The owner asked how to recover the Bridge Token after it appeared removed.

Verified bridge contract:
- setting: `CATALOG_BRIDGE_TOKEN`
- request header: `Authorization: Bearer ...`
- endpoints include `/api/catalog-bridge/v1/health/` and import path.

The assistant instructed the owner to read the effective token only from their own host terminal and not paste it into chat.

Catalog Center execution path on Windows:

```powershell
cd "D:\projects\3DPrintHub\catalog_center"
& "D:\projects\3DPrintHub\.venv\Scripts\python.exe" launch.py
```

Official source/update path remained GitHub → Local → installer/upgrade, not an unverified public patch endpoint from `3dprinthub.ir`.

The owner later requested the desktop application be compiled/versioned as a Windows executable.

Immutable Windows release created:
- Version: `8.8.1`
- Build ID: `2026.08.25.2`
- Release: `catalog-center-v8.8.1`
- Asset: `3DPrintHub-CatalogCenter-v8.8.1.exe`
- SHA256:
  `c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990`

Release gate included:
- 92 relevant Phase49 regression tests,
- canonical launcher composition,
- PyInstaller one-file/windowed build,
- frozen portable self-verification,
- frozen Playwright/Chrome-compatible browser smoke,
- manifest/SHA validation,
- immutable artifact and GitHub Release publication.

The owner later hit:

```text
RuntimeError: Launcher expected 8.8.0, but imported 8.8.1
```

This became ERR-50-003: version identity had been advanced in app/version but stale in launcher/manifest/config/tests. Version surfaces were aligned atomically.

A frozen verification issue became ERR-50-004: a one-file PyInstaller build cannot assume bundled `launch.py` exists as a physical source file; the verification was changed to import runtime contracts instead.

Later source changes added original image pixel dimensions to Product image cards; this delta is not yet in a newer immutable EXE beyond 8.8.1.

---

## 6. Owner feedback about public Product page and Hero/mobile UX

The owner supplied screenshots and requested:

### Product gallery behavior
- Large Product image area should be a fixed main viewer.
- Clicking any thumbnail should replace the main viewer image.
- The main image should fit fully inside the viewer instead of being cropped.
- Clicking the large image should open a larger/fullscreen view.

Implemented in Phase50.A.1B:
- contain-fit main viewer,
- thumbnail switching without page reload,
- fullscreen lightbox,
- previous/next,
- Escape and arrow-key navigation.

### Mobile homepage Hero
Owner said Product title/description obscured Product image on mobile and requested the title size roughly halved and caption card much smaller.

Phase50.A.1C:
- mobile Hero caption/title/buttons reduced,
- on very narrow phones the description is hidden but CTA remains,
- Product image visibility prioritized.

### Product image quality
Owner noted some homepage images were low quality and wanted admin control over image quality. Admin media integrity work added safe previews and dimensions; desktop Catalog source later shows original `W × H px` so operator can reject weak images before publish.

---

## 7. Business commerce priorities before full accounting

The owner asked for a full list of remaining requested work and emphasized these priorities:

- gateway/payment,
- accounting ledger / دفتر معین,
- payment/receipt system,
- purchase/sales system,
- professional Admin,
- customer panel preservation,
- addresses with Iran province/county/city,
- shipping fee calculation,
- VAT and coupon,
- secure anti-phishing payment,
- Torob integration,
- product variants/profiles,
- SEO.

Repository review confirmed existing mature foundations:

### Existing Store foundation
- `StoreOrder`
- `StoreOrderItem`
- `StorePayment`
- `StoreInvoice`
- shipment
- return request
- coupon
- inventory reservation/movements

### Existing service order/payment foundation
- Order → Quote → Payment
- deposit/full/balance payments
- manual receipt path
- immutable `PaymentLedgerEntry`

### Existing inventory/production foundation
- filament purchase
- purchase items
- filament spools
- weight movements
- material usage
- production jobs
- production cost
- business finance dashboard

### Existing affiliate foundation
- affiliate partner
- commission
- payout
- affiliate ledger

### Existing checkout calculations
The Store checkout already contained:
- subtotal,
- packaging fee,
- shipping,
- VAT,
- coupon discount,
- order weight.

### Existing payment security architecture
Service-payment engine already supported:
- server-owned amount,
- callback token,
- Authority matching,
- server-to-server verify,
- transaction lock,
- idempotency,
- ledger.

However Store checkout still needed to be unified with this mature secure gateway engine.

---

## 8. Phase50 roadmap established

The project formally moved to:

**Phase50 — Finance, Commerce & Admin Command Center**

Roadmap:

### 50.A — Admin and commerce operational completeness
- Admin command center
- Product/Hero/Admin parity
- Product Gallery
- Variant 2.0
- Product sales profiles
- shipping/delivery
- secure Store ZarinPal
- Torob

### 50.B — Accounting foundation
- Chart of accounts: کل / معین / تفصیلی
- fiscal periods
- balanced accounting vouchers
- immutable posting/reversal
- party/subledger
- document numbering

### 50.C — Treasury
- bank/cash accounts
- receipts/payments
- allocations
- refunds
- reconciliation

### 50.D — Purchasing / payables
- suppliers
- purchase orders
- purchase invoices
- receiving
- payables
- returns

### 50.E — Sales / receivables accounting
- Store/service receivables
- payment allocation
- tax/discount/shipping
- returns/refunds/credit notes

### 50.F — Reports / close
- GL/subledger
- trial balance
- statements
- AR/AP aging
- cashflow
- profitability
- VAT/tax
- period close

---

## 9. Phase50.A Admin Command Center

A business-oriented Admin entry point was implemented:

`/admin/command-center/`

Sections include:
- Sales
- Treasury
- Accounting/Ledgers
- Purchasing
- Inventory/Production
- Storefront/Checkout

Links are permission-aware and counters expose operational state.

The owner specifically requested Admin functionality matching desktop Catalog capabilities, including:
- add selected Product to homepage Hero,
- remove from Hero,
- add 5 random Products,
- add 10 random Products,
- deactivate all Hero slides without deleting history.

These actions were implemented and CI-tested.

The command center also surfaced:
- Products
- imported Catalog assets
- Hero
- coupons
- Shipping Methods
- Pricing Settings
- customer addresses
- Iran province/county/city data.

---

## 10. Product Variant 2.0 and Sales Profile requirement

The owner described realistic sellable Product cases, especially cake stands:

- sizes: 20 / 24 / 26 / 28 / 30 cm,
- for each size multiple construction/weight profiles:
  - light/hollow,
  - standard,
  - solid/heavy,
- each can differ by:
  - material weight,
  - final weight,
  - print time,
  - price,
  - packaging/shipping data,
  - stock.

Owner wanted a reusable profile concept:
- copy an existing profile,
- keep common material/color/quality/settings,
- change only weight/time/price or size,
- choose what customer selects by: size, weight, build type, or multi-step selection.

### Phase50.A.1B — Variant 2.0 foundation
Added:
- `size_label`
- build/fill profile
- packaging weight
- parcel dimensions
- StoreOrderItem snapshot columns
- effective shipping weight helper
- Variant uniqueness extended for size/build
- Admin exposure
- public Variant metadata endpoint

Migration:
`store.0034_phase50_variant2_commerce`

CI PASS and later Production deployment applied `0034` successfully.

### Phase50.A.1D — Sales Profiles
Implemented on GitHub:

Product-level selection mode:
- full list
- size
- weight
- build
- size → build
- build → size

ProductVariant fields:
- sales profile name
- stable profile key
- display order
- default flag

Profile key extends Variant identity so otherwise identical material/color/size/build rows may coexist with different weight/time/price.

Admin action:
`کپی پروفایل‌های فروش انتخاب‌شده`

This clones mature Variant settings and creates a new code/profile key while preserving source.

Migration:
`store.0035_phase50_sales_profiles`

GitHub Actions:
`Phase50 Sales Profiles Hero Admin CI`
run `32879712980` PASS on snapshot `405d2c1daa85828d1a0dc68210d201c85b6db7ba`.

At the time of this archive, repository docs still do not record `store.0035` as Production-applied.

---

## 11. Admin image/media defects from owner screenshots

The owner showed several Admin screenshots where images were broken:

- Hero Studio Product cards on:
  `/admin/website/homepageheroslide/4/change/`
- imported Product model list/details
- gallery rows inside imported model change page

Browser console included 404 for paths such as:
`jewelry-tree-box-3d-print-01.webp`
`jewelry-tree-box-3d-print-02.webp`

Root cause was similar to public Hero media issue:
- Admin preview endpoints still emitted private imported working-media URLs.

Phase50.A.1C safe ImportedPrintAsset Admin media resolver:
1. Product gallery filename match
2. Product main image
3. HTTP(S) source fallback

Private imported working-media remains private.

Phase50.A.1D final Hero Admin endpoint repair:
- Product browser thumbnails use Product-owned public media.
- album rows use matching Product gallery media.
- if no public match, row-specific remote HTTP(S) source can be used.
- no replacement Hero Admin JSON endpoint returns `/media/store/imported-models/...`.

---

## 12. Product Admin 500 and transient MySQL exhaustion incident

Owner screenshot showed:
`/admin/store/product/` → Server Error (500)

Host diagnostics initially failed with:
`OperationalError: (1040, 'Too many connections')`

A read-only audit was requested instead of repeating the same failing DB probes.

Owner output:

```text
HOST: nphost4.parsblog.com
USER: sfkilvrs
CURRENT HEAD=6a551948dd700061f0f7ae0e586196eded75f5ec
DB_CONN_MAX_AGE=60
USER PROCESS COUNT=6
2 lswsgi processes
visible ESTABLISHED_3306=0
CLOSE_WAIT_3306=0
HTTP:
200 https://3dprinthub.ir/
200 https://3dprinthub.ir/store/
200 https://3dprinthub.ir/admin/
200 https://3dprinthub.ir/admin/store/product/
```

This showed:
- Product Admin 500 had cleared,
- no persistent app-side connection storm was visible,
- too-many-connections incident was transient.

A later single-connection Django/MySQL audit output:

```text
DB_VENDOR= mysql
DB_NAME= sfkilvrs_EmiAdmin_3dprinthub
DB_HOST= localhost
CONN_MAX_AGE= 60
THREADS_CONNECTED= 26
MAX_CONNECTIONS= 151
CURRENT_USER_PROCESSLIST_COUNT= 3
STORE_0034_APPLIED= NO
MIGRATION_PLAN=NO_PENDING_MIGRATIONS
```

The apparent contradiction was explained:
- host was still on old source that did not contain migration 0034, so Django could not plan it.

A later guarded Phase50.A.1C deploy then:
- verified current branch/head,
- fetched exact GitHub target,
- backed up `.env`, pending imports and MySQL,
- fast-forwarded source,
- verified migration 0034 exists,
- checked exact migration plan,
- applied 0034,
- collectstatic,
- Passenger restart,
- HTTP smoke,
- public media safety checks.

Repository records owner-verified Production Phase50.A.1C at commit:
`5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`

Rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`

---

## 13. SEO implementation status requested by owner

The owner explicitly asked whether Product SEO settings from Windows/Catalog had been implemented in the site Admin and frontend.

Verified Product SEO fields in Django Admin:
- `seo_focus_keyword`
- `meta_title`
- `meta_description`
- `canonical_url`
- `robots_index`
- `robots_follow`
- `og_title`
- `og_description`
- `og_image`

Admin SEO behavior includes:
- SEO score/health indicator,
- Google/SERP preview.

Public Product page consumes actual Product SEO state:
- title
- meta description
- canonical
- robots index/follow
- Open Graph type/title/description/image
- Product JSON-LD
- FAQ JSON-LD

Store base includes:
- organization schema
- Google site verification
- Bing site verification
- Open Graph defaults
- Twitter card.

Homepage SEO operator controls were added to Admin around the existing canonical SiteSetting meta title/description rather than duplicating fields.

Remaining explicit SEO debt recorded:
- dedicated `twitter:title`
- `twitter:description`
- `twitter:image`
- `og:image:alt`

Core meta/OG/canonical/schema/sitemap are present.

---

## 14. Unified Product Admin Workspace request and implementation

Owner asked that all Product administration be professional, centralized and comparable to Windows Product Workspace.

Phase50.A.1E was implemented as a final additive Admin composition boundary.

Exact Product change-page section order:

1. `اطلاعات کالا`
2. `تصاویر`
3. `فروش و موجودی`
4. `پروفایل‌ها و سایز/وزن`
5. `قیمت‌گذاری`
6. `ارسال و بسته‌بندی`
7. `SEO`
8. `اسلایدر صفحه اول`
9. `منبع و لایسنس`
10. `همگام‌سازی ویندوز`
11. auxiliary `آمار و وضعیت`

Behavior:
- Product core fields stay on Product model.
- Product gallery and ProductVariant inlines are preserved.
- Product sales profile selection is surfaced.
- pricing links/summarizes existing ProductCatalogProfile pricing instead of duplicating pricing state.
- shipping summarizes Variant 2.0 weights/package dimensions.
- SEO exposes real Product focus/meta/canonical/robots/OpenGraph/schema fields and SERP preview.
- Hero section links slider configuration/Hero Studio.
- source/license combines Product source and Catalog commercial-license status.
- Windows sync surfaces Desktop ID, sync revision, last-modified source and last-sync metadata.

No new migration for 50.A.1E; it builds on 0034 and pending 0035.

CI:
`Phase50 Product Admin Workspace CI`
run `32941662288` PASS on snapshot `f34eaa3bbad965b2092279291ff8adf93f3d908e`.

First run `32941533091` failed only because a new regression test incorrectly expected a stale `seo_status` list column. Mature behavior was preserved; the test was corrected. This is ERR-50-006.

At archive time branch HEAD was:
`be864b0adf6183d6aec6ee8d8e4d7fa285a109c6`

---

## 15. Shipping / delivery requirement

Owner requested shipping calculation based on:
- selected Product/profile,
- Product weight,
- packaging weight,
- package dimensions,
- origin/destination,
- province/county/city/postal code,
- shipment value.

Carrier targets:
- Iran Post
- Tipax
- Mahex

Architecture decision:
- create normalized `ShippingQuoteProvider` / carrier adapter contract,
- use official current API contracts/credentials only,
- do not guess endpoints,
- preserve mature `ShippingMethod` fixed/weight pricing as fallback,
- snapshot chosen quote into order so historical order does not change when tariffs later change.

Existing Store data already contains customer address and Iran province/county/city reference data.

Phase50.A.2 planned tasks:
- storefront profile-aware selector,
- persist selected profile/size/build/package snapshots in checkout,
- effective Product + packaging shipping weight,
- normalized carrier quote,
- immutable order shipping snapshot.

---

## 16. VAT, coupons and checkout

Owner requested VAT and discount code support in payment flow.

Verified existing backend foundation already includes:
- Coupon percentage/fixed discounts,
- min order,
- max discount,
- usage limits,
- validity dates,
- Product/category restrictions,
- VAT toggle/rate,
- packaging fee,
- shipping fee,
- order weight.

Thus roadmap direction is to improve integration/presentation and avoid duplicating pricing logic.

---

## 17. ZarinPal secure Store payment

Owner requested enabling ZarinPal now and insisted on phishing-resistant payment security.

Existing service-payment engine is mature and should be reused for Store checkout.

Security contract:
- amount calculated and owned by server,
- random callback identity,
- exact Authority/reference matching,
- server-to-server verify,
- DB transaction lock,
- idempotency,
- immutable/auditable ledger,
- trusted gateway redirect-host allowlist,
- never collect or store card number, CVV, PIN.

Configuration support includes:
- `PAYMENT_GATEWAY_ENABLED`
- provider
- timeout
- ZarinPal Merchant ID
- Access Token
- Sandbox/Production
- currency
- request/verify/startpay URLs.

StorePayment already has fields suited for gateway integration such as authority/ref/idempotency/raw response, but Store checkout was still not fully unified with the secure service-payment gateway path.

Phase50.A.3:
- unify Store checkout with mature payment engine,
- activate real Production merchant only after complete Store E2E verification,
- later secure refund/reconciliation path.

No secrets should be pasted into chat or committed.

---

## 18. Torob integration

Owner wants `3dprinthub.ir` connected to Torob.

Target architecture is official current Torob Product API v3, with:
- stable Product/Profile grouping,
- variant size/color/material/weight mapping,
- current price and availability,
- image quality validation,
- stable identifiers/page uniqueness,
- eventual official attribution/webhook/order-tracking integration.

Torob should be implemented after Product profiles, selector, shipping and secure payment foundations are stable so catalog/price/availability reflect real sellable variants.

---

## 19. Accounting / treasury / purchasing requirements still remaining

Owner asked for full business financial system including:

### Accounting core
- coding tree / chart of accounts
- کل
- معین
- تفصیلی
- fiscal periods
- accounting vouchers
- debit/credit lines
- balanced posting
- immutable posting/reversal
- numbering
- party/subledger

### Treasury
- banks
- cash boxes
- receipts
- payments
- customer receipts
- supplier payments
- allocations
- refunds
- bank reconciliation

### Purchasing
- supplier master
- purchase orders
- purchase invoices
- purchase items
- general purchases beyond filament
- receiving
- payables
- supplier statements
- purchase returns

### Sales accounting
- Store/service receivables
- payment allocation
- sales invoices
- VAT
- discounts
- shipping
- returns/refunds
- credit notes

### Reports
- journal
- general ledger
- subsidiary ledger
- party statements
- customer/supplier balances
- trial balance
- AR/AP aging
- profit/loss
- cashflow
- project profitability
- VAT/tax
- period close

Existing PaymentLedgerEntry, StorePayment, StoreOrder, filament purchase, production and affiliate ledger foundations should be integrated instead of replaced.

---

## 20. Exact current state at archive time

Source of truth docs on 2026-08-26 report:

### Current release/subphase
`Phase50.A.1E — Unified Product Admin Workspace`

### Branch
`agent/phase49-3i18-operator-bulk-ai-rebuild`

### Branch HEAD at archive check
`be864b0adf6183d6aec6ee8d8e4d7fa285a109c6`

### Production verified baseline
`5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`

### Production migration state recorded
- `store.0034_phase50_variant2_commerce` = applied
- `store.0035_phase50_sales_profiles` = not yet recorded as Production-applied

### Windows release
- immutable 8.8.1 still latest released EXE
- newer source includes image-dimension delta not yet released as a newer executable

### CI
50.A.1D:
- `Phase50 Sales Profiles Hero Admin CI`
- run `32879712980` PASS

50.A.1E:
- `Phase50 Product Admin Workspace CI`
- run `32941662288` PASS

### Known warnings/debt
- CKEditor4 maintenance/security debt
- `store.W026` in-memory realtime multi-process limitation
- Pillow deprecation warning
- optional Google credential warning when unset
- remaining social preview tags noted above

---

## 21. Immediate next execution plan

Before any Production mutation:
1. read project docs again,
2. verify actual host root/branch/HEAD/worktree,
3. verify live GitHub branch HEAD,
4. verify MySQL vendor/name,
5. verify actual migration state of 0034/0035,
6. if 0035 is pending, take fresh successful MySQL backup and preserve rollback commit,
7. inspect exact migration plan,
8. deploy committed GitHub source only,
9. apply only approved pending migration,
10. collectstatic,
11. Passenger restart,
12. HTTP + Admin/Product/Hero/media smoke,
13. manual owner QA of unified Product Admin and Sales Profiles.

Then continue:
- Product profile selector on storefront,
- immutable checkout profile snapshot,
- Shipping/Delivery providers and fallback,
- secure Store ZarinPal,
- Torob Product API v3,
- Accounting core → Treasury → Purchasing → Sales accounting → Reports.

---

## 22. Owner acceptance/UX priorities to preserve

- Do not regress healthy customer panel developed earlier.
- Product Admin should be professional and expose all Product commerce/SEO/Hero/source/sync controls clearly.
- Desktop and Web should share one coherent Product/Profile contract instead of divergent duplicate settings.
- Images in Admin and public Hero/Product must resolve only to appropriate public Product media; imported working media remains private.
- Product page must provide a professional contain-fit gallery/lightbox.
- Mobile Hero must prioritize Product visibility over large caption blocks.
- Multiple Product sizes/weights/builds need reusable profiles and fast copy/edit.
- Customer-facing selector should reflect Product-specific selection criterion.
- Shipping should use selected profile's real weight/package data.
- Coupon/VAT/shipping need clear checkout presentation.
- Payment must be server-verified/idempotent and resistant to fake callback/phishing patterns.
- Torob integration must be based on official current API and real sellable Product/Profile data.
- SEO must be operator-manageable and actually rendered into public pages, not merely stored.
- Windows app should remain a final compiled/versioned executable after source/manual smoke.

---

## 23. Relevant recorded errors in this session

- ERR-49-049: nonexistent `Database.categories()` call; use mature App category provider.
- ERR-49-050: canonical title helper duplicate `current_title` binding.
- ERR-49-051: public Hero referenced private imported media in Production.
- ERR-50-001: CI guessed wrong Django env variable names.
- ERR-50-002: dynamic ModelAdmin URL patch not stable at final Admin URL boundary.
- ERR-50-003: Catalog Center 8.8.1 app version advanced while release metadata stayed 8.8.0.
- ERR-50-004: frozen portable verification assumed physical launcher source file.
- ERR-50-005: Admin media patch replaced mature `list_display` while old editable/link contracts remained.
- ERR-50-006: Product Admin regression test assumed stale `seo_status` list column.
- transient MySQL 1040 `Too many connections` event was investigated and later not reproduced as a persistent app connection storm.

---

## 24. End-of-chat continuation marker

The most recent owner question before this archive asked whether:
- Product Admin contains Product settings, price settings, sales settings and SEO similar to Windows,
- Product SEO settings are actually implemented on the site.

Repository verification answered:
- yes, Product core/commerce/pricing/Profile/Hero/source/sync/SEO are substantially present,
- Phase50.A.1E unifies the Product Admin workspace into the exact business sequence requested,
- real Product SEO fields are consumed by public Product pages,
- remaining social-specific tags are tracked debt,
- 50.A.1D/1E are CI-tested but need Production deployment/QA according to the current repository state,
- next roadmap remains profile-aware Store selector/checkout → shipping → secure Store ZarinPal → Torob → accounting.

This file is intended to let a new chat continue without relying on chat memory alone.