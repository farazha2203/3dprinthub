# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Subphase:** `50.A.2B — Immutable Checkout/Profile/Shipping Snapshot`  
**Status:** `GITHUB CI TESTED / PRODUCTION MIGRATION AUDIT NEXT`  
**Backend:** Django / Python

## 1) قانون مادر
`READ DOCS → VERIFY REAL STATE → CHECK PREVIOUS ERRORS → IMPLEMENT ON GITHUB → CI/LOCAL GATE → HOST READ-ONLY VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFICATION → UPDATE DOCS`

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

## 3) Production baseline
Application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`.
Rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.
Applied: `store.0034_phase50_variant2_commerce`, `store.0035_phase50_sales_profiles`.
Not yet Production-applied: `store.0036_phase50_checkout_snapshot`.
Home/Store/Admin/Product/Variant API are healthy and public imported-working-media refs remain zero.

## 4) Phase50 deployed foundation
- Admin command center/Hero controls,
- Product gallery/lightbox,
- Variant2 size/build/weight/package schema (`0034`),
- Sales Profiles (`0035`),
- unified Product workspace,
- Product Admin 500 fix + business navigation,
- Velzon V2 full-width tables/on-demand filters,
- Admin shell stability with 290px sidebar/internal-only menu scroll,
- Storefront profile/size/build/weight/color/price selector using canonical ProductVariant.

## 5) Current GitHub-tested work — 50.A.2B
Migration `store.0036_phase50_checkout_snapshot` and `store/phase50_checkout_snapshot.py` implement immutable successful-checkout state.

### Item snapshot
- profile name/key/label,
- selection mode + customer-visible selection value,
- size/build/material/color/quality,
- final weight, packaging weight, effective shipping weight,
- print time,
- package dimensions.

### Order/shipping snapshot
- `insured_value`,
- normalized `shipping_quote_snapshot`,
- total effective shipping weight,
- ShippingMethod fallback source, destination, fee and per-line package facts.

### Important semantics
- explicit Variant shipping weight overrides calculated final+packaging weight,
- otherwise packaging is included,
- mature Phase6 coupon/VAT/inventory/address/notification/payment flow remains authoritative,
- successful checkout is finalized inside an outer atomic boundary,
- pending payment amount is synchronized with finalized total,
- no combined carton geometry is guessed,
- no Post/Tipax/Mahex API is called or claimed without verified official credentials/contracts,
- finalizer failure rolls DB writes back and restores the cart session.

CI: `Phase50 Variant2 Gallery CI` run `32966720475` PASS on `fba0631e60bce1f6e3f622317b70c2f7f35d978f`; compile, Django check, migration state/plan, migration through `0036`, Variant/gallery/selector and immutable checkout tests all PASS.

## 6) Next Production gate
1. Read-only verify Host HEAD/worktree/live GitHub SHA and exact MySQL DB.
2. Verify `0034/0035` applied, `0036` actual state and exact migration plan.
3. Verify disk/mysqldump; make fresh source/.env/MySQL backup and record rollback HEAD.
4. Explicit branch fetch to `FETCH_HEAD` per ERR-50-007 and verify ff-only ancestry.
5. Deploy approved GitHub target.
6. Recheck Django/migration state and apply only approved `store.0036_phase50_checkout_snapshot` if pending.
7. Passenger restart + Production schema/runtime/HTTP verification; never rewrite historical paid orders.
8. Update docs with Production commit/backup/migration state.

## 7) After 50.A.2B
- Product Engagement: Favorite/Save + counters + verified-purchased/paid buyer feedback.
- 50.A.3 Secure ZarinPal.
- 50.A.4 Torob Product API v3.
- 50.B–50.F Accounting Core → Treasury → Purchasing → Sales Accounting → Reports/Close.

## 8) Host prevention rules
- ERR-50-007: host fetch refspec is tag-only → live `ls-remote` + explicit branch fetch to `FETCH_HEAD`.
- ERR-50-010: avoid `/dev/fd` process substitution → Python/portable backup enumeration.
- ERR-50-011: parse JSON as data through `python -` + `json.load`.

## 9) Safety
No Production migration without exact MySQL vendor/name, exact plan, fresh verified backup and rollback. No public imported working-media. No guessed carrier/gateway endpoint. Purchased Velzon/font assets remain private.
