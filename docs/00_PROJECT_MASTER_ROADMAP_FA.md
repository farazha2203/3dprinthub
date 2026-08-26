# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.1H Admin Shell Stability + 50.A.2A Storefront Sales Profile Selector`  
**Status:** `GITHUB CI TESTED / HOST READ-ONLY VERIFY NEXT`  
**Backend:** Django / Python

## 1) قانون مادر
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → OWNER QA → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFICATION → UPDATE DOCS`

قواعد ثابت:
- Mature behavior با Extend/Patch/Wrap اصلاح می‌شود.
- Bugfix بدون Regression Test کامل نیست.
- Source دائمی روی Production ویرایش نمی‌شود.
- Dirty Local/Host = STOP/INSPECT.
- Secret در Git/log/chat ذخیره نمی‌شود.
- Remote زنده مرجع Branch است؛ SHA حدس زده نمی‌شود.
- Assetهای خریداری‌شده/private پوسته و فونت در Repository عمومی منتشر نمی‌شوند.

## 2) مسیرهای ثبت‌شده
Windows: `D:\projects\3DPrintHub`; venv `D:\projects\3DPrintHub\.venv`.
Production: `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`; static `/home/sfkilvrs/public_html/static`; media `/home/sfkilvrs/public_html/media`; private media `/home/sfkilvrs/3dprinthub/private_media`.

## 3) Production evidence boundary
Last terminal-verified Production application HEAD recorded in docs is `bc7b97f9c63432b8105f52f61cf5cdae1369689b`, with `store.0034` and `store.0035` applied and rollback backup `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

Later owner screenshots show newer Velzon V2 visuals but no terminal transcript proving current host HEAD. Therefore the next operation starts with a read-only Host audit; no Production baseline is guessed.

## 4) Phase50 completed/deployed foundation
- Admin command center + Hero controls,
- Product gallery/lightbox,
- Variant2 size/build/weight/package + StoreOrderItem snapshots (`store.0034`),
- Sales Profiles + Hero public-media resolver (`store.0035`),
- unified Product workspace,
- Product Admin 500 fix + business navigation,
- Product-owned public media contract preserved.

## 5) Current GitHub-tested work
### 50.A.1G — Velzon Operator Surface V2
Full-width changelists, on-demand filter drawer, Persian controls, modern Velzon search/actions/results/pagination, long-form section navigation. Initial V2 CI run `32955310832` PASS on `3687d0922959fca53f2118be6dacd32639159346`.

### 50.A.1H — Admin Shell Stability
Owner QA found footer flash/mid-page placement, page jump on menu navigation and narrow right sidebar.

Implemented:
- footer normal/static flow instead of Velzon absolute positioning,
- stable flex/min-height Admin shell,
- 290px right sidebar with improved Persian readability,
- no broad shell geometry transition,
- active menu scroll constrained to internal SimpleBar/sidebar; document `scrollIntoView` removed,
- no migration.

CI: `Phase50 Product Admin Workspace CI` run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`.

### 50.A.2A — Storefront Sales Profile Selector
Existing Product/ProductVariant profile backend is now surfaced to customers:
- list / size / weight / build / size→build / build→size modes,
- available size/build/weight/material/color/quality controls,
- selected profile price/weight/time/package summary,
- canonical ProductVariant ID synced into mature native select/cart contract,
- native select fallback retained,
- existing `/store/api/variant-commerce-options/` reused,
- no migration.

CI: `Phase50 Variant2 Gallery CI` run `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.

### 50.A.2B — Checkout/Delivery completion — NEXT
- explicit immutable selected-profile/customer-choice order snapshot where required,
- effective product + packaging shipping weight,
- parcel dimensions / insured value,
- normalized carrier quote + immutable order snapshot,
- Post/Tipax/Mahex only after verified official credentials/contracts,
- ShippingMethod fallback preserved.

### Product Engagement — OWNER REQUESTED
Favorite/Save + Product counters + verified-purchase buyer review policy in a separate schema/migration/test/backup package, preserving ProductLike/ProductComment/ProductReview.

### 50.A.3 — Secure Store Payment
Server-owned amount, exact callback/verify/idempotency and trusted gateway-host allowlist; never card/PIN/CVV storage.

### 50.A.4 — Torob
Current official Product API v3 with stable Product/Profile identity, current price/availability and image-quality contract.

### 50.B–50.F
Accounting Core → Treasury → Purchasing → Sales Accounting → Reports/Close.

## 6) Current release gate
1. Host read-only verify actual root/branch/HEAD/worktree/refspec/MySQL/0034/0035/private Velzon assets/HTTP.
2. Verify target is a clean fast-forward with no migration-file delta.
3. Fresh source/.env/MySQL backup and rollback HEAD.
4. Explicit branch fetch to `FETCH_HEAD` per ERR-50-007.
5. ff-only deploy; Django check/model drift/empty migration plan; no `migrate` for this batch.
6. collectstatic + Passenger restart.
7. Home/Store/Admin/new static/private-media checks.
8. Owner QA: footer stable on refresh, no document jump, 290px sidebar readable, Product selector/price/cart synchronization correct.

## 7) Safety
No schema migration without exact MySQL vendor/name, migration plan, fresh verified backup and rollback. No public imported working-media. No guessed carrier/gateway API. Purchased Velzon/font assets remain private.
