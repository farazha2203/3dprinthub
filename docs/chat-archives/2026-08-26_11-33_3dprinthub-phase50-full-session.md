# 3DPrintHub — Chat Archive

Date: 2026-08-26
Repository: farazha2203/3dprinthub
Branch: agent/phase49-3i18-operator-bulk-ai-rebuild

> This archive preserves the substantive content, decisions, requests, command outputs, incidents, fixes, deployments, and next-step agreements from the current ChatGPT development session as available in the conversation context.

## Session flow

### Catalog Center / exact-link / AI / operator workflow
The session continued Phase49.3I work around the Windows Catalog Center, exact-link acquisition, AI completion, source identity, product editing, image handling, SEO, and publishing. Important fixes already completed in the session included:

- category provider bridge after `Database.categories()` failure;
- canonical title helper call-contract fix;
- exact-link flow that fetches source text/data without sending product images/image URLs to AI;
- operator workflow, bulk actions, image gallery, source identity, SEO generation and observability;
- structured web product presentation replacing raw JSON-like technical notes;
- Production Hero media ownership fix so public Hero uses Product-owned public media rather than private imported working-media.

The Windows Catalog Center release line reached 8.8.1, with a GitHub Release and PyInstaller one-file executable. Browser/Playwright smoke and frozen-runtime validation were added to the release gate. Later source work also added original image dimensions to Product image cards; that delta is newer than the immutable 8.8.1 EXE and is intended for a later rebuild after smoke.

### Production deployment and cleanup
Production project root and environment were verified as:

- `/home/sfkilvrs/3dprinthub`
- Python venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- MySQL DB `sfkilvrs_EmiAdmin_3dprinthub`
- static `/home/sfkilvrs/public_html/static`
- media `/home/sfkilvrs/public_html/media`
- private media `/home/sfkilvrs/3dprinthub/private_media`

The host initially had known untracked files and deployment stopped safely. Those host-only files were verified, backed up, and later removed after successful deployment and verification. Production worktree was confirmed clean.

A Phase49 deployment succeeded with migrations, collectstatic, Passenger restart, HTTP smoke and Product presentation checks. Hero images initially failed on Production because `/media/store/imported-models/...` is intentionally private. The public Hero resolver was changed to Product-owned gallery/main media. This fix was tested and deployed successfully.

### Product presentation and storefront media
User reported Product page gallery requirements:

- large fixed image viewer;
- clicking thumbnails changes the main image;
- images fit fully rather than forced crop;
- clicking main image opens a larger/fullscreen view;
- mobile layout must keep product image visible and reduce oversized title/caption overlays.

Phase50.A.1B implemented contain-fit Product gallery, thumbnail switching and fullscreen lightbox.

### Admin parity / command center
User requested that website Admin provide the same practical commerce controls as the Windows application, including:

- add selected Product to Homepage Hero;
- remove selected Product from Hero;
- 5 random Products to Hero;
- 10 random Products to Hero;
- deactivate all Hero slides without deleting history;
- clear access to Product, pricing, selling, SEO, shipping, coupons, addresses and configuration.

Phase50.A Command Center and 50.A.1 Admin Storefront/Hero parity were implemented. Admin now includes a business-oriented command center and Hero quick controls.

### Imported model Admin image/data integrity
User screenshots showed broken previews in ImportedPrintAsset Admin and inside Hero Studio edit pages. Browser showed 404s for files such as:

- `jewelry-tree-box-3d-print-01.webp`
- `jewelry-tree-box-3d-print-02.webp`

Root cause: mature Admin/Hero Studio endpoints still emitted private imported working-media URLs. The fix preserves imported media as private and resolves Admin previews through Product-owned public media, with HTTP(S) source fallback when appropriate.

Imported model Admin was also expanded to surface useful completeness/status information while preserving mature Phase35 editing/actions.

### Homepage SEO and Product SEO
User emphasized SEO as a major priority for both Homepage and Products.

Repository review confirmed Product Admin has SEO fields and runtime consumption for:

- Focus Keyword;
- Meta Title;
- Meta Description;
- Canonical URL;
- Robots index/follow;
- OG Title;
- OG Description;
- OG Image;
- Product JSON-LD;
- FAQ JSON-LD.

Category and ServicePage also use SEO Admin support. Admin has SEO status scoring and Google-result preview. Homepage SiteSetting meta title/description remain canonical and were augmented with SEO health/audit. Hero-specific SEO fields include title, description, alt, CTA and focus keyword.

Remaining SEO debt explicitly noted:

- dedicated `twitter:title`;
- `twitter:description`;
- `twitter:image`;
- `og:image:alt`.

### Variant 2.0 and Sales Profiles
User requested a professional reusable Product profile system for Products with multiple sizes/weights/build styles, e.g. a cake stand with multiple sizes and multiple weight/fill versions per size.

Phase50.A.1B added Variant 2.0 foundation:

- size label;
- build/fill profile;
- material;
- color;
- print quality;
- material weight;
- final weight;
- packaging weight;
- effective shipping weight;
- parcel length/width/height;
- print time;
- price inputs/overrides;
- stock/availability.

Migration `store.0034_phase50_variant2_commerce` was created and later successfully applied on Production after MySQL verification and backup.

User then requested reusable Sales Profiles where an operator can copy an existing profile and change only values such as weight, print time, size or price. Phase50.A.1D implemented:

- Product sales profile selection mode;
- optional selector label;
- ProductVariant profile name;
- stable profile key;
- display order;
- default profile flag;
- uniqueness extended with profile key so otherwise-identical size/material/color/build profiles can coexist with different weight/time/price;
- Admin action to copy selected Sales Profiles without changing the source profile;
- metadata endpoint exposes profile selector fields, price, weight, time and shipping/package data.

Selection modes supported:

- full profile list;
- size;
- weight;
- build/fill;
- size → build;
- build → size.

Migration for this phase: `store.0035_phase50_sales_profiles`.

### Hero Studio edit-page image fix
User reported broken Product/album images in URLs like:

`/admin/website/homepageheroslide/4/change/`

Phase50.A.1D also replaced the final Hero Admin JSON endpoint boundary so Product browser and gallery cards use Product-owned public media or safe remote source media and never private imported working-media URLs.

GitHub Actions `Phase50 Sales Profiles Hero Admin CI` run `32879712980` passed compile, Django check, migration checks/apply and focused Sales Profile/Hero Admin regressions.

### MySQL transient connection incident
A Production diagnostic hit:

`OperationalError: (1040, 'Too many connections')`

A later read-only audit showed:

- 2 lswsgi processes;
- no visible persistent own 3306 connections during shell audit;
- Home/Store/Admin/Product Admin HTTP 200;
- `DB_CONN_MAX_AGE=60`;
- MySQL `Threads_connected=26`;
- `max_connections=151`;
- current app DB user processlist count 3.

Conclusion: no evidence of a permanent 3DPrintHub connection storm; the earlier 1040 appeared transient/global. Deployment commands were adjusted to use `DB_CONN_MAX_AGE=0` for management/audit processes so command connections close immediately.

### Production Phase50.A.1C deployment
Production was verified at application commit:

`5c5c5e1e141fd3ff8df3c079abc55e4593feb41f`

with:

- MySQL correct;
- `store.0034` applied;
- migration plan clean;
- Home/Store/Admin/Product Admin/Imported Asset Admin/Hero Admin HTTP 200;
- no private imported-media references in public Home;
- rollback backup at `/home/sfkilvrs/3dprinthub-deploy-backups/20260825-205719`.

### Shipping / checkout requirements
User requested dynamic shipping calculation using Product weight + packaging and destination details, with Post, Tipax and Mahex when official APIs are verified.

Existing backend already includes:

- ShippingMethod fixed/weight rules;
- Coupon support;
- VAT;
- packaging fee;
- order weight calculation;
- StoreAddress;
- Iran Province/County/City reference data.

Planned Phase50.A.2:

- profile-aware Product selector in storefront;
- persist selected profile/size/build/package snapshots at checkout;
- effective Product + packaging shipping weight;
- parcel dimensions and insured value;
- normalized carrier quote contract;
- immutable shipping snapshot on order;
- Iran Post / Tipax / Mahex adapters only after verified official contracts/credentials;
- mature ShippingMethod fallback preserved.

### ZarinPal payment requirements
User requested ZarinPal activation and strong anti-phishing payment handling.

Existing service-payment engine already contains mature patterns:

- server-owned amount;
- random callback identity;
- exact Authority matching;
- server-to-server verify;
- idempotency;
- immutable/payment ledger behavior.

Phase50.A.3 plan:

- reuse this engine for StorePayment;
- trusted gateway-host allowlist;
- no collection/storage of card number, PIN or CVV;
- strict provider reference/Authority verification;
- reconciliation/audit;
- activate real Production Merchant only after Store checkout E2E is complete.

### Torob integration
User requested Torob integration. Planned Phase50.A.4 uses current official Torob Product API v3, including:

- stable Product/profile grouping;
- size/color/material/weight mapping;
- current price and availability;
- image-quality guards;
- official attribution/webhook/order tracking only after verified contract.

### Finance/accounting roadmap
User requested full accounting/business finance including:

- کل / معین / تفصیلی;
- accounting vouchers;
- balanced debit/credit entries;
- fiscal periods;
- immutable posting/reversal;
- bank/cash treasury;
- receipts/payments;
- refunds/reconciliation;
- suppliers and purchase orders/invoices;
- payables;
- sales receivables;
- tax/discount/shipping accounting;
- GL/subledger reports;
- trial balance;
- AR/AP aging;
- cashflow;
- profitability;
- VAT/tax reports;
- period close.

Current roadmap order agreed in session:

1. 50.A.1D Sales Profiles + Hero Admin media QA/deploy;
2. 50.A.2 Checkout & Delivery;
3. 50.A.3 Secure Store ZarinPal;
4. 50.A.4 Torob;
5. 50.B Accounting Core;
6. 50.C Treasury;
7. 50.D Purchasing & Payables;
8. 50.E Sales & Receivables Accounting;
9. 50.F Reports & Close.

### Admin product management parity
User asked whether Product Admin now includes Windows-like controls. Repository review confirmed the following are present across Product, ProductVariant and ProductCatalogProfile Admin surfaces:

- Product core info;
- inventory/sales state;
- pricing mode/range;
- pricing strategy and pricing inputs;
- technical/product intelligence;
- Product SEO fields and SEO preview;
- Homepage Hero publishing/SEO/effects;
- size/build/material/color/quality/weight/time/packaging Variant data;
- Sales Profile controls in Phase50.A.1D;
- Admin profile copy action.

Still desired as a UX improvement: consolidate these mature underlying models into a more unified Product Management screen/fieldsets resembling the Windows Product Workspace, without duplicating database ownership.

### Windows/site division of work
User stated the desired operating model going forward:

- website development/deployment work on the host flow, but committed through GitHub and deployed from GitHub rather than permanent direct Production source edits;
- Windows Catalog Center tested/run on the Windows computer;
- Windows application compiled/versioned as an executable release after smoke;
- website versioned/finalized independently;
- avoid duplicate implementation by using shared product/profile contracts between Windows and Server.

### Current repository state at archive time
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Latest branch HEAD observed before this archive: `8fbe3413cada1099745f4d17312b8eb519694379`
Current active subphase: `50.A.1D — Sales Profiles + Hero Admin Public Media`
Status in docs: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

### Current known technical debt / open items
- CKEditor4 maintenance/security warning;
- `store.W026` in-memory realtime not suitable for production multi-process; Redis/polling is separate debt;
- Pillow `Image.getdata()` deprecation;
- social meta additions listed above;
- Windows source image-dimension delta needs next immutable EXE rebuild after smoke;
- storefront Sales Profile selector and checkout snapshots are next;
- shipping carrier official API verification still required;
- Store ZarinPal E2E still required;
- Torob v3 integration still required;
- full accounting modules remain after commerce completion.

## Operational rules repeatedly enforced during session

- GitHub is source of truth.
- Read AGENTS/docs before technical changes.
- Verify branch/HEAD/path/DB/migrations/host state; do not guess.
- Dirty worktree means STOP/INSPECT.
- No permanent Production source edits.
- No destructive DB/filesystem/Git changes without verified target and rollback.
- Migration requires exact MySQL verification, migration plan and successful fresh backup.
- Do not repeat a failed command unchanged unless the underlying condition changed.
- Do not expose secrets in chat/Git/logs.
- Feature completion requires tests; do not label ACCEPTED only because code exists.
- Update CURRENT_STATE, ROADMAP, CHANGELOG, ERRORS, REQUESTS and active phase after meaningful work.

## User priority at end of session

The final priority sequence is to finish Product/Admin parity and Sales Profiles, then make storefront profile selection and checkout use the selected profile, calculate shipping from profile/package/destination, activate secure ZarinPal Store payment, integrate Torob, and only after commerce is stable continue with full accounting/treasury/purchasing/reporting.
