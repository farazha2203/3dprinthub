# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.2 Checkout & Delivery`  
**Status:** `50.A.1H + 50.A.2A PRODUCTION_VERIFIED / OWNER VISUAL QA NEXT / 50.A.2B NEXT`  
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

## 3) Production baseline — verified 2026-08-26
Application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.
Rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

Verified:
- Python 3.12.13 / Django 6.0.7,
- MySQL exact DB `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- migration drift NONE / migration plan empty / no migration executed,
- clean worktree,
- Home/Store/Admin/Product/new static HTTP 200,
- Product selector HTML/native fallback/API PASS,
- Home private imported-media refs 0.

## 4) Phase50 completed/deployed foundation
- Admin command center + Hero controls,
- Product gallery/lightbox,
- Variant2 size/build/weight/package + StoreOrderItem snapshots (`store.0034`),
- Sales Profiles + Hero public-media resolver (`store.0035`),
- unified Product workspace,
- Product Admin 500 fix + business navigation,
- Product-owned public media contract,
- Velzon V2 full-width tables and on-demand filter drawer.

## 5) Current Production-verified work
### 50.A.1H — Admin Shell Stability — PRODUCTION VERIFIED
Implemented/deployed:
- footer normal/static flow instead of Velzon absolute positioning,
- stable flex/min-height Admin shell,
- 290px right sidebar with improved Persian readability,
- no broad geometry transitions,
- active-menu scroll constrained to internal SimpleBar/sidebar; document `scrollIntoView` removed,
- no migration.

CI: `Phase50 Product Admin Workspace CI` run `32958276378` PASS on `27335832e90c35dd95bb8a686dd89d1efd46dc8f`.
Owner browser visual QA remains before ACCEPTED.

### 50.A.2A — Storefront Sales Profile Selector — PRODUCTION VERIFIED
Implemented/deployed:
- existing Product/ProductVariant profile backend surfaced to customers,
- list / size / weight / build / size→build / build→size modes,
- available size/build/weight/material/color/quality controls,
- selected profile price/weight/time/package summary,
- canonical ProductVariant ID synced into mature native select/cart contract,
- native select fallback retained,
- existing `/store/api/variant-commerce-options/` reused,
- no migration.

CI: `Phase50 Variant2 Gallery CI` run `32958296546` PASS on `e3c57311c0c3980befeaf6012f3bb8fc502333bc`.
Production Product/Variant API verification PASS. Owner browser interaction QA remains before ACCEPTED.

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

## 6) Production deployment rules learned
- `ERR-50-007`: Host `remote.origin.fetch` tracks only tag `v0.33.0`; verify live branch and explicitly fetch to `FETCH_HEAD`, then verify ancestry and ff-only merge.
- `ERR-50-010`: this cPanel shell cannot rely on `/dev/fd` process substitution; use Python or portable file handling.
- `ERR-50-011`: JSON/API smoke payloads are data; verifier pattern is `python - <args>` + explicit `json.load`, never `python <json-file>`.

## 7) Current next gate
1. Owner Ctrl+F5/browser QA of Admin footer refresh stability, menu no-jump behavior and 290px sidebar.
2. Owner QA of Product profile/size/weight/color/price selector and price/cart synchronization.
3. If visual QA passes, mark 50.A.1H and 50.A.2A ACCEPTED.
4. Start 50.A.2B with GitHub-first implementation/tests; any schema change requires exact MySQL plan + fresh backup + rollback.
5. Continue Product Engagement → ZarinPal → Torob → accounting.

## 8) Safety
No schema migration without exact MySQL vendor/name, migration plan, fresh verified backup and rollback. No public imported working-media. No guessed carrier/gateway API. Purchased Velzon/font assets remain private.
