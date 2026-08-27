# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Web Subphase:** `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
**Parallel Windows Subphase:** `49.3I.35 — Operator Ledger + Resilient AI / Catalog Center 8.9.1`  
**Status:** `GITHUB CI TESTED / WINDOWS PACKAGED CI PASS / AUTOMATED LOCAL GATE PASS / OWNER VISUAL QA NEXT / PRODUCTION BLOCKED`  
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
- Database migration فقط بعد از Verify دقیق Engine/DB/Plan/Backup/Rollback اجرا می‌شود.

## 2) مسیرهای Canonical
Windows:
- root `D:\projects\3DPrintHub`
- venv `D:\projects\3DPrintHub\.venv`
- Catalog persistent root `D:\projects\3dprinthub-catalog-manager`
- Catalog SQLite `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`

Production:
- root `/home/sfkilvrs/3dprinthub`
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`
- static `/home/sfkilvrs/public_html/static`
- media `/home/sfkilvrs/public_html/media`
- private media `/home/sfkilvrs/3dprinthub/private_media`

## 3) Production baseline
Verified Production application commit:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Verified rollback backup:
`/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`.

Last verified Phase50 DB state:
- applied `store.0034`,
- applied `store.0035`,
- `store.0036` pending,
- `store.0037`, `store.0038` and `store.0039` were created after that verification and are not claimed applied.

Production remains on the prior stable release until Local QA + fresh Host audit/backup.

Current approved GitHub runtime:
- Catalog Center `8.9.1` / build `2026.08.27.3`,
- Windows runtime `2622818d898e19b745c61ff653b80c03d22288f1`,
- Windows run `33060047878` PASS; artifact `9641338334`; EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- Phase50 run `33059883188` PASS through migration `0039` and 16 regressions,
- pending Production chain is `0036 → 0037 → 0038 → 0039`, subject to fresh read-only MySQL verification.


## 4) Deployed foundation
- Admin command center/Hero controls,
- Product gallery/lightbox,
- Variant2 size/build/weight/package schema,
- Sales Profiles,
- unified Product Admin,
- Admin 500 fix + business navigation,
- Velzon V2 full-width lists/on-demand filters,
- stable footer / 290px sidebar / internal menu scroll,
- canonical Variant/Profile storefront selector,
- Product-owned public media boundary.

## 5) Current Windows development — Phase49.3I.35
Catalog Center `8.9.1`, build `2026.08.27.3`.

New Step-2 Profile Matrix:
- add Profile,
- clone Profile,
- delete/edit Profile,
- independent size/weight/price/print-time/part-dimensions/build/material/color/quality/package/stock values,
- selection modes including size→weight and 3-level combinations,
- exact Profile JSON persisted locally,
- exact Profile JSON transported through mature batch/import path,
- profile/range minimum accepted by mature publish gate.

Preserved:
- 48-card Product paging,
- explicit-only global Product refresh,
- exact saved AI provider/model/key,
- exact-link source grounding,
- canonical source-link guard,
- selected-product batch AI,
- image/source identity safety.

Windows verification:
- packaged snapshot `2622818d898e19b745c61ff653b80c03d22288f1`,
- workflow `33060047878` PASS,
- artifact ID `9641338334`,
- EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- owner automated Local gate PASS with 107 Catalog tests and Local SQLite through `0039`.

## 6) Current Web development — Phase50.A.2B → 2C → 2D

### 2B / `0036`
Immutable Profile/selection/shipping checkout snapshot.

### 2C / `0037`
Professional Product price-policy + per-Variant fixed price, shipping service/scope/fee semantics, Store payment-display settings and safe shipping presets.

### 2D / `0038`
Profile description + size↔weight modes + actual part dimensions + immutable ordered part dimensions.

Runtime profile sync:
- Desktop Profile becomes canonical ProductVariant,
- republish is idempotent,
- manual non-Desktop Variants remain intact,
- invalid mappings fail closed.

Storefront:
- selected Profile is the single price/facts authority,
- size/weight/build/material/color/quality dependent choices,
- options follow prefix hierarchy,
- weight/Profile prices are scoped to selected upstream size,
- professional Profile summary with part/shipping/package facts,
- native Variant fallback retained.

Web verification:
- runtime snapshot `7d0a2a1125e8f38771ba325427d1efa8b8d07da6`,
- CI run `33051311828` PASS,
- hierarchy behavior gate PASS,
- no migration drift,
- CI DB applies through `0038`,
- 15 Variant/Profile/Checkout tests PASS.

## 7) Current known corrected incidents
- `ERR-50-012`: execute callable price contract in Variant API.
- `ERR-50-013`: saved-address shipping policy validates persisted address.
- `ERR-50-014`: prefix-only selector dependency + size-scoped price badges.
- `ERR-50-015`: Windows packaging watches mature Product studio source boundaries.

## 8) Production gate
1. Local Windows clean pull + exact HEAD verify.
2. Run `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1` with exact HEAD and launch.
3. Owner QA multi-size/multi-weight Profile create/clone/edit/save/reopen + existing Product data/source link/AI/images.
4. Local Django/SQLite regression.
5. Read-only Host verify actual branch/HEAD/worktree/live remote SHA/Python/Django/MySQL/migration state.
6. Exact migration plan.
7. Disk + mysqldump verify.
8. Fresh tracked-source + environment + MySQL backup with checksums.
9. Explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`; exact target + ff-only.
10. Deploy GitHub source.
11. Repeat Django check/drift/DB/plan.
12. Apply only actually pending verified migrations, expected from last Production evidence as `0036 → 0037 → 0038 → 0039`.
13. collectstatic + Passenger restart.
14. Home/Store/Admin/Product/Profile API/Checkout/private-media verification.
15. Controlled new order using multi-size/multi-weight Profile.
16. Owner browser QA.
17. Update docs with exact Production SHA/backup/migrations.

## 9) بعد از 50.A.2D
- Product Engagement،
- Secure ZarinPal،
- Torob API،
- Accounting Core،
- Treasury،
- Purchasing/Payables،
- Sales/Receivables،
- Reports/Close.

## 10) Host prevention rules
- `ERR-50-007`: tag-only refspec → live `ls-remote` + explicit `FETCH_HEAD`.
- `ERR-50-010`: روی cPanel به `/dev/fd`/process substitution تکیه نکن.
- `ERR-50-011`: JSON داده است؛ با `python -` + `json.load` Verify شود.

## 11) Safety
No Production migration without exact MySQL vendor/name, exact plan, fresh verified backup and rollback. No public imported working-media. No guessed carrier/gateway endpoint. Purchased Velzon/font assets remain private.
