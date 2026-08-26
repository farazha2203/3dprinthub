# 3DPrintHub — Chat Archive

**Archived:** 2026-08-26 11:27 +03:30  
**Repository:** `farazha2203/3dprinthub`  
**Branch:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Scope:** continuation of Phase49 Catalog/Web stabilization through Phase50 Admin/commerce planning and implementation.

> This archive preserves the substantive conversation, owner requirements, implementation decisions, production evidence, commands, errors, release state, and next steps from this session. Secrets/tokens are intentionally not reproduced.

---

## 1. Product presentation / raw intelligence cleanup

Owner reported that public Product pages were showing an unstructured block containing MakerWorld source data plus raw Catalog Intelligence JSON such as estimated weight, material recommendations, SEO fields, sales bullets, social caption, source hashes, availability, materials/colors and keywords.

Owner requirement:
- public presentation must be readable and professional,
- raw JSON/internal AI fields must not be dumped to customers,
- AI-generated content should be organized into customer-readable sections,
- source/license information remains visible in a clear format.

The web Product presentation was subsequently structured and production deployment verified under the Phase49.3I.29/30 sequence.

---

## 2. Production deployment sequence and host cleanup

Initial production branch/state:
- Host: `/home/sfkilvrs/3dprinthub`
- Production branch initially `main`, later moved to `agent/phase49-3i18-operator-bulk-ai-rebuild`
- old host HEAD observed: `6660cf1d84d46ea8eeaf9246d1b86f6ed41082c7`
- approved Phase49 deployment commit: `d27489f1c2e1d36e75fdadfa8ab24660d8bec720`

First production audit/deploy attempt stopped because the worktree had known host-only untracked files:

```text
PHASE48_SERVER_BRIDGE_AUDIT.py
deploy/phase43-applied.json
smartbase_admin_bridge/sb_admin.py.broken_20260808_160314
store/test_phase43.py
```

A later deploy attempt failed while trying to establish tracking information for the feature branch. A subsequent attempt revealed a partially staged/indexed state from the prior failed tracking operation; deployment was stopped rather than forcing/resetting.

After correction, production was successfully deployed and verified at the approved snapshot. Production evidence included:
- MySQL verified,
- rollback backup created,
- Phase49 migrations applied,
- `collectstatic` completed,
- Passenger restarted,
- Home/Store/Product returned HTTP 200,
- Product presentation tests passed.

Known host-only files were then removed after verification that they were safe extras. Final host status:

```text
## agent/phase49-3i18-operator-bulk-ai-rebuild
PRODUCTION WORKTREE = CLEAN
HEAD=d27489f1c2e1d36e75fdadfa8ab24660d8bec720
```

Rollback backup retained:

```text
/home/sfkilvrs/3dprinthub-deploy-backups/20260825-150401
```

---

## 3. Catalog Bridge token / Windows Catalog launch / update workflow

Owner requested the Bridge Token and Windows execution/update instructions.

Security contract:
- the token is `CATALOG_BRIDGE_TOKEN`,
- it is used as `Authorization: Bearer ...`,
- secrets are never stored in Git/chat,
- the value is read directly from production Django settings and pasted into Catalog Center connection settings.

Bridge health endpoint:

```text
https://3dprinthub.ir/api/catalog-bridge/v1/health/
```

Windows canonical paths:

```text
Project: D:\projects\3DPrintHub
Catalog Center source: D:\projects\3DPrintHub\catalog_center
Venv: D:\projects\3DPrintHub\.venv
Persistent Catalog DB: D:\projects\3dprinthub-catalog-manager\catalog.sqlite3
```

Source launch command used:

```powershell
cd "D:\projects\3DPrintHub\catalog_center"
& "D:\projects\3DPrintHub\.venv\Scripts\python.exe" launch.py
```

GitHub-first update path retained; no public “patch download from website” endpoint was considered canonical.

---

## 4. Homepage Hero images missing only on Production

Owner screenshots showed:
- Local `127.0.0.1:8000` Hero rendered correctly,
- Production Hero text rendered but image area was blank/dark,
- Product detail page images were healthy.

Browser console showed 404s for paths such as:

```text
/media/store/imported-models/gallery/scallop-cake-stand-24cm-removable-base-3d-print-01.webp
/media/store/imported-models/gallery/ribbed-cake-stand-cookie-platter-3d-print-01.webp
```

Verified root cause:
- imported Catalog working images live under `store/imported-models/...`,
- Production intentionally exposes Product/category/SEO public media, not internal working-media,
- Local DEBUG served all media and hid the ownership problem,
- Hero was incorrectly preferring `ImportedPrintAssetImage.image.url`.

Phase49.3I.30 fix:
- Hero resolves matching Product-owned gallery media by filename,
- falls back to Product main image,
- remote source only as final fallback,
- never widens Production public routing for imported working media.

Web stable version was frozen/tagged as:

```text
web-v49.3I.30
```

---

## 5. Windows executable release

Catalog Center Windows build pipeline was moved to GitHub Actions / Windows runner.

Release work included:
- PyInstaller one-file/windowed build,
- runtime verification,
- Playwright/browser smoke in frozen executable,
- launcher composition verification,
- manifest/SHA validation,
- immutable GitHub Release asset.

A launcher mismatch was observed locally:

```text
RuntimeError: Launcher expected 8.8.0, but imported 8.8.1
```

Root cause:
- `app/version.py` moved to 8.8.1 while launcher/manifest/config/tests were still 8.8.0.

Fix:
- all release identity surfaces aligned atomically.

Final released Windows build:

```text
Catalog Center v8.8.1
Build: 2026.08.25.2
Asset: 3DPrintHub-CatalogCenter-v8.8.1.exe
SHA256: c32f37affcbd2c6ffacb803247daf804a490fecd7c8162bc37c2729a2197e990
```

Release gate passed 92 Phase49 regressions, canonical launcher verify, frozen self-verify, frozen browser smoke, artifact/release publication.

Remaining Windows requirement later added by owner:
- Product image cards must show original pixel dimensions (`W × H px`).
- source delta was implemented but a newer immutable EXE version should be released only after smoke.

---

## 6. Phase50 direction — business back-office before accounting

Owner requested continuation beyond Catalog toward:
- complete Django Admin,
- finance / ledger / receivables / payables,
- purchasing and sales,
- payment/receipt management,
- inventory/production,
- gateway activation,
- shipping,
- Torob marketplace.

Repository review showed mature foundations already exist:
- `StoreOrder`, `StoreOrderItem`, `StorePayment`, `StoreInvoice`, shipment, returns, coupons, reservation/movements,
- service `Order → Quote → Payment`,
- immutable `PaymentLedgerEntry`,
- filament purchase/spools/movements,
- production jobs/material usage/costs,
- affiliate commission/payout/ledger,
- existing ZarinPal service-payment engine.

Missing full accounting scope recorded as Phase50.B–F:
- chart of accounts کل / معین / تفصیلی,
- fiscal periods,
- balanced vouchers and debit/credit lines,
- posting/reversal,
- treasury: bank/cash/receipts/payments/refunds/reconciliation,
- suppliers/purchasing/payables,
- sales receivables/accounting,
- GL/subledger/trial balance/aging/cashflow/P&L/VAT/close.

---

## 7. Phase50.A Admin Command Center

Implemented `/admin/command-center/` to organize operational Admin by business function instead of raw model names.

Sections:
- Sales,
- Treasury,
- current Accounting/Ledgers,
- Purchasing/Supply,
- Inventory/Production,
- Storefront/Catalog/Checkout.

Admin now surfaces links/counters for existing real features rather than fake roadmap links.

Additional Admin parity work added:
- add selected Products to homepage Hero,
- remove selected Products from Hero,
- same operations for imported Catalog assets,
- quick controls: 5 random products, 10 random products, deactivate all Hero non-destructively,
- random selection restricted to active Product-backed assets with public-renderable media,
- links to Coupon, ShippingMethod, PricingSetting, StoreAddress and Iran location reference models.

---

## 8. Product page gallery requirement

Owner screenshot showed a large Product image and small thumbnails. Requirement:
- large frame remains stable,
- clicking thumbnail replaces main image,
- image should fit fully without destructive crop,
- click main image should open full-screen/lightbox,
- mobile-friendly behavior.

Phase50.A.1B implemented:
- contain-fit main image viewer,
- thumbnail swap without reload,
- accessible fullscreen lightbox,
- previous/next controls,
- ESC/arrow support.

---

## 9. Product Variant 2.0 — size/build/packaging

Owner explained real commercial examples such as cake stands with sizes:

```text
20 / 24 / 26 / 28 / 30 cm
```

and multiple construction/weight options per size:
- hollow/light,
- standard,
- solid/heavy.

Owner requirement:
- each configuration can have independent weight,
- independent print time,
- independent price,
- material/color may stay constant,
- the customer should select the proper commercial option.

Phase50.A.1B added to `ProductVariant`:
- `size_label`,
- build/fill profile,
- packaging weight,
- parcel length/width/height,
- shipping weight helper,
- uniqueness expanded to include size/build,
- matching order snapshot columns prepared.

Migration:

```text
store.0034_phase50_variant2_commerce
```

Production migration later applied successfully after MySQL verification/backup.

---

## 10. Sales Profile model requested by owner

Owner refined Variant 2.0 into a reusable “sales profile” concept:
- duplicate an existing profile,
- keep all existing material/color/quality/package settings,
- change only weight/print time/price or size,
- choose what the customer uses as the selection criterion.

Examples:

```text
Profile 1: 20cm / standard / PLA white / 180g / 4h10 / price A
Profile 2: copy / 20cm / hollow / 120g / 3h05 / price B
Profile 3: copy / 20cm / solid / 310g / 6h30 / price C
Profile 4: 24cm / standard / 260g / 5h20 / price D
```

Product-level customer selection modes requested/implemented:
- full profile list,
- size,
- weight,
- build type,
- size → build,
- build → size.

Phase50.A.1D implementation:
- Product `sales_profile_selection_mode`,
- optional selector label,
- ProductVariant `sales_profile_name`, stable key, default flag, display order,
- profile key participates in uniqueness so otherwise-identical size/material/color/build variants can coexist with different weights/times/prices,
- Admin action `کپی پروفایل‌های فروش انتخاب‌شده`,
- Variant endpoint exposes profile label/key/default/order plus weight/time/price/shipping metadata.

Migration:

```text
store.0035_phase50_sales_profiles
```

GitHub CI:

```text
Phase50 Sales Profiles Hero Admin CI
Run: 32879712980
PASS
```

---

## 11. Admin imported-model images and data quality

Owner screenshots showed:
- imported model list missing/broken thumbnails,
- imported model detail had private working-media references,
- data view was incomplete,
- browser 404s for imported gallery images.

Phase50.A.1C implemented:
- safe Admin preview resolver:
  Product gallery filename match → Product main image → remote HTTP(S) source fallback,
- imported working-media remains private,
- mature Phase35 list editing/actions preserved,
- completeness indicator added,
- imported image inline shows original image dimensions.

An initial Admin patch caused Django Admin invariant errors because it replaced mature `list_display` while existing `list_editable`/`list_display_links` referenced removed columns. This was fixed by extending rather than replacing the mature Admin contract.

Recorded as:

```text
ERR-50-005
```

Corrected CI passed:

```text
Phase50 Admin Media Mobile CI
Run: 32875771848
PASS
```

---

## 12. Hero Admin Studio image bug

Owner specifically reported the Hero slide change page:

```text
/admin/website/homepageheroslide/4/change/
```

The top Product browser cards and “gallery images for this product” showed broken images.

Root cause:
- public Hero rendering had already been fixed,
- but legacy Hero Studio JSON endpoints still emitted private `store/imported-models/...` URLs.

Phase50.A.1D fix:
- Hero Admin Product browser uses Product-owned public media,
- album/gallery rows use matching Product gallery image,
- if no public match, row-specific remote HTTP(S) source may be used,
- private imported working-media is never returned by the replacement Admin JSON endpoints,
- selected image IDs/SEO suggestions/cinematic settings remain compatible.

---

## 13. Mobile homepage Hero

Owner screenshot showed mobile Hero text/caption covering too much of the product image.

Requirement:
- title font roughly half/smaller,
- caption card significantly smaller,
- product image must remain visible,
- CTA stays usable.

Phase50.A.1C:
- compact mobile Hero override,
- smaller caption/title/button footprint,
- description hidden on very narrow phones while CTA is retained.

---

## 14. Homepage SEO and Product SEO

Owner repeatedly emphasized strong SEO and requested SEO controls in Admin equivalent to Catalog intelligence.

Current Product SEO Admin includes:
- Focus Keyword,
- Meta Title,
- Meta Description,
- Canonical URL,
- Robots index/follow,
- OG Title,
- OG Description,
- OG Image,
- SEO score/health,
- Google SERP preview.

These fields are not decorative; Product page consumes:
- SEO title,
- meta description,
- canonical,
- robots,
- OG product metadata,
- Product JSON-LD,
- FAQ JSON-LD.

Store base also includes:
- Organization schema,
- Google/Bing verification,
- default OG,
- Twitter card.

Homepage SiteSetting keeps canonical `meta_title` / `meta_description`; Phase50.A.1C adds Admin length health, SERP preview and Hero Alt/title audit.

Remaining SEO debt explicitly noted:
- `twitter:title`,
- `twitter:description`,
- `twitter:image`,
- `og:image:alt`.

---

## 15. Admin parity with Windows Product Workspace

Owner asked whether Admin now has the same Product controls as Windows:
- product settings,
- pricing,
- sales,
- SEO,
- slider,
- color/material/weight/size.

Current architecture:
- Product Admin: main product information and SEO,
- ProductVariant Admin/inline: material/color/quality/size/build/weight/time/price/stock/package,
- ProductCatalogProfile Admin: product type/availability/price mode/price range/technical/SEO and homepage slider fields,
- Phase49.3F Admin: pricing strategy/inputs and material runtime rates,
- Phase50.A.1D: sales profile settings and copy profile.

Owner’s desired next refinement:
- make the Admin feel like one professional Product command center with logical sections such as:

```text
اطلاعات کالا
تصاویر
فروش و موجودی
پروفایل‌ها و سایز/وزن
قیمت‌گذاری
ارسال و بسته‌بندی
SEO
اسلایدر صفحه اول
منبع و لایسنس
همگام‌سازی ویندوز
```

Data ownership should remain the mature models; UI should consolidate navigation/editing rather than duplicate models.

---

## 16. Checkout, VAT, Coupon and Shipping requirements

Repository review confirmed backend foundations already exist:
- Coupon validation,
- VAT,
- packaging fee,
- shipping fee,
- order weight,
- fixed/weight-rule ShippingMethod.

Owner requested next expansion:
- shipping uses Product + packaging weight,
- package dimensions,
- insured/value amount,
- origin/destination province/county/city/postal code,
- live carrier quote where official APIs exist,
- Post / Tipax / Mahex,
- fallback to internal weight rules when live carrier fails.

No carrier endpoint should be guessed; official current contracts/credentials must be verified before live integration.

Planned adapter architecture:

```text
ShippingQuoteProvider
IranPostProvider
TipaxProvider
MahexProvider
WeightRuleFallbackProvider
```

Order stores immutable shipping quote snapshot so later tariff changes do not rewrite historical orders.

---

## 17. ZarinPal secure payment

Owner wants ZarinPal activated now and a phishing-resistant payment flow.

Existing mature service-payment engine already includes:
- server-owned amount,
- random callback identity,
- Authority matching,
- server-to-server verification,
- transaction locking,
- idempotency,
- immutable ledger.

Store payment model already has gateway-related fields but Store checkout still needed to be unified with the mature gateway engine.

Planned Phase50.A.3:
- reuse the secure service-payment architecture for `StorePayment`,
- trusted redirect-host allowlist,
- never collect/store card number, PIN or CVV,
- exact provider/Authority verification,
- reconciliation/audit,
- safe refund flow later.

Production environment supports variables such as:

```text
PAYMENT_GATEWAY_ENABLED
PAYMENT_GATEWAY_PROVIDER=zarinpal
ZARINPAL_MERCHANT_ID
ZARINPAL_ACCESS_TOKEN
ZARINPAL_SANDBOX
ZARINPAL_CURRENCY
```

Secrets are intentionally not archived here.

---

## 18. Torob integration requirement

Owner wants the store connected to Torob.

Planned Phase50.A.4:
- current official Torob Product API v3,
- stable Product/profile grouping,
- per-profile/variant size/color/material/weight,
- current price and availability,
- image-quality rules,
- official order attribution/webhook contract after verification.

Sales Profile architecture was deliberately designed before Torob so Torob can publish real commercial variants rather than a flattened product.

---

## 19. Production MySQL “Too many connections” incident

During a read-only host reconciliation, Django DB commands failed with:

```text
OperationalError: (1040, 'Too many connections')
```

Project `.env` showed:

```text
DB_CONN_MAX_AGE=60
```

A no-DB audit then showed:
- only 2 `lswsgi` processes,
- no visible 3306 established connections from account at that instant,
- Home/Store/Admin/Product Admin all HTTP 200,
- ample memory/disk.

A later single-connection MySQL audit showed:

```text
THREADS_CONNECTED=26
MAX_CONNECTIONS=151
CURRENT_USER_PROCESSLIST_COUNT=3
```

Conclusion:
- prior 1040 event was transient/shared-host saturation, not evidence of a persistent app-level connection storm.

Audit also confirmed:

```text
DB_VENDOR=mysql
DB_NAME=sfkilvrs_EmiAdmin_3dprinthub
store.0034 applied = NO at old host source
migration plan = no pending because source did not yet contain 0034
```

After source deployment, Phase50.A.1C deployment applied `store.0034` successfully and production smoke passed.

---

## 20. Phase50.A.1C production baseline

Repository source-of-truth later recorded owner deployment success at:

```text
5c5c5e1e141fd3ff8df3c079abc55e4593feb41f
```

Production state:
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- final migration plan clean,
- Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin HTTP 200,
- no public Home reference to `/media/store/imported-models/`,
- rollback backup:

```text
/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719
```

---

## 21. Phase50.A.1D current GitHub state

Current active subphase:

```text
Phase50.A.1D — Sales Profiles + Hero Admin Public Media
```

CI-tested implementation includes:
- Product sales-profile selection mode,
- ProductVariant profile name/key/default/order,
- copy-profile Admin action,
- profile metadata endpoint,
- Hero Admin public-media fix,
- migration `store.0035_phase50_sales_profiles`.

CI:

```text
Phase50 Sales Profiles Hero Admin CI
Run 32879712980
PASS
```

Branch HEAD at archive time:

```text
8fbe3413cada1099745f4d17312b8eb519694379
```

Production had not yet been documented as upgraded to `0035` at archive time; next production gate requires read-only host verification, fresh MySQL backup, exact migration plan, deploy from GitHub, apply only `store.0035`, collectstatic, Passenger restart and manual QA.

---

## 22. Immediate roadmap after Phase50.A.1D

### 50.A.2 — Checkout & Delivery
- profile-aware customer selector,
- persist selected profile/size/build/package snapshots,
- effective product + packaging shipping weight,
- package dimensions / insured value,
- carrier quote contract + immutable snapshot,
- Post/Tipax/Mahex only with verified official APIs,
- mature ShippingMethod fallback.

### 50.A.3 — Secure Store ZarinPal
- server-owned amount,
- callback identity,
- exact Authority,
- server-to-server verify,
- idempotency,
- trusted gateway host allowlist,
- no card/PIN/CVV capture,
- audit/reconciliation.

### 50.A.4 — Torob
- Product API v3,
- Product/profile grouping,
- variant metadata,
- price/availability/images,
- attribution/webhooks after official verification.

### 50.B — Accounting Core
- کل / معین / تفصیلی,
- fiscal periods,
- balanced vouchers,
- posting/reversal,
- party/subledger.

### 50.C — Treasury
- bank/cash,
- receipts/payments,
- allocations,
- refunds,
- reconciliation.

### 50.D — Purchasing
- suppliers,
- purchase orders/invoices,
- receiving,
- payables,
- returns.

### 50.E — Sales Accounting
- receivables,
- payment allocation,
- tax/discount/shipping,
- returns/refunds/credit notes.

### 50.F — Reports & Close
- GL/subledger,
- trial balance,
- customer/supplier statements,
- AR/AP aging,
- cashflow,
- profitability,
- VAT/tax,
- fiscal close.

---

## 23. Permanent owner workflow and constraints reiterated throughout session

- GitHub is the permanent source of truth.
- Read `AGENTS.md` and required docs before technical changes.
- No permanent source edits directly on Production.
- No ZIP/patch/source delivery through chat.
- Verify real branch/HEAD/path/DB/migration state before commands.
- Dirty worktree = STOP/INSPECT; no reset/delete shortcut.
- Check `docs/ERRORS.md` before retrying failed operations.
- No destructive DB/migration/filesystem operation without verified backup and rollback.
- Production schema migration requires MySQL vendor/name, exact migration plan and successful `mysqldump`.
- Changes are implemented/committed on GitHub, tested via CI/Local as applicable, then deployed from GitHub and production-verified.
- Windows Catalog Center remains a separate executable release track; web development and Windows application should share stable contracts without duplicating business data models.

---

## 24. Related known warning/debt items

- CKEditor4 maintenance/security warning.
- `store.W026`: in-memory realtime is not multi-process Production-grade; Redis/polling remains separate debt.
- Pillow deprecation around `Image.getdata()`.
- Google membership credential warning when intentionally absent in CI.
- Social SEO enhancements still open: dedicated Twitter title/description/image and `og:image:alt`.

---

## 25. Session end state

**Repository:** `farazha2203/3dprinthub`  
**Branch:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**GitHub HEAD at archive creation:** `8fbe3413cada1099745f4d17312b8eb519694379`  
**Production documented baseline:** Phase50.A.1C at `5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`, MySQL `store.0034` applied.  
**Current code phase:** Phase50.A.1D Sales Profiles + Hero Admin Public Media, CI green, Production deploy/QA next.  
**Windows release:** Catalog Center v8.8.1 immutable release; newer source has image-dimension delta awaiting next executable release after smoke.  
**Next functional priority:** unify Product Admin/Profiles → storefront profile selector → checkout/shipping → secure Store ZarinPal → Torob → accounting core.
