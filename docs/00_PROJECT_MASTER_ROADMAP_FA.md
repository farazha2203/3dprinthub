# 3DPrintHub — نقشه مادر پروژه، معماری، فازها و مسیر بعدی

> این فایل قبل از هر Phase/Hotfix/UI change/Migration/Sync/Deploy خوانده می‌شود. GitHub/Repository منبع اصلی حقیقت است.

**Repository:** `farazha2203/3dprinthub`  
**Branch توسعه:** `agent/phase49-3i18-operator-bulk-ai-rebuild`  
**Current Epic:** `Phase50 — Finance, Commerce & Admin Command Center`  
**Current Web Subphase:** `50.A.2E — Brand-aware Filament Offers + Immutable Filament Snapshot`  
**Parallel Windows Subphase:** `49.3I.40 — Commerce Precision + Offer Ownership + Readiness Truth / Catalog Center 8.9.8`  
**Status:** `8.9.8 BASELINE PASS / ERR-49-070 STAGE-5 SCHEMA + PANEL HOTFIX GITHUB / OWNER LOCAL RETEST NEXT / PRODUCTION BLOCKED`  
**Backend:** Django / Python

### Owner Local gate checkpoint — ERR-49-070

Gate جدید روی `382a34f...` کامپایل و 4 تست OpenRouter-only را PASS کرد اما قبل از Launch در مجموعه 67 تست دو نقص واقعی سورس را گرفت: ستون `technical_summary_fa` در دیتابیس تمیز Catalog ساخته نمی‌شد و توابع واقعی پنل کامل Stage 5 فقط فراخوانی شده بودند ولی تعریف نشده بودند. هر دو مورد همراه با Persist انتخاب فارسی مجوز و Regression مربوطه روی GitHub اصلاح شدند.

Rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`. مرحله بعد Pull و تکرار همان Gate محلی است؛ Production دست نخورده است.

### Owner Windows workflow checkpoint — ERR-49-069

روی Head دقیق `3f43260...` بکاپ Catalog با SHA256 ثبت شد، Compile PASS و 60/60 تست هدفمند PASS شد و سورس واقعی 8.9.8 در Foreground بالا آمد؛ با این حال UI واقعی هنوز نشان داد مشکل Final Composition باقی است. Callback قدیمی که قبل از نصب 3I.39 برای `after_idle` ثبت شده بود می‌توانست دوباره دکمه پایین را به `مرحله بعد برای انتشار` برگرداند. هم‌زمان Field ownership مرحله 1/5 ناقص بود، Stage AI نقص‌های مراحل دیگر را می‌شمرد، Productهای 63 و 295 هم‌زمان AI اجرا کردند و Fallback هنوز به AvalAI می‌رفت.

Hotfix اجرایی `136011971dea907ac777b3e66190dd27982a0c38`:
- Next قدیمی هم در نهایت به Confirm نهایی Delegate می‌کند و هر مسیر Legacy ابتدا Save می‌کند؛
- هر Refresh قدیمی در پایان Footer نهایی را دوباره Restore می‌کند؛
- Stage 1 نوع محصول، ابعاد و کاربری/کلاس را دوباره دارد و ذخیره می‌کند؛
- Stage 5 طراح/منبع، مجوز، خلاصه و ویژگی‌های فنی را دوباره دارد و ذخیره می‌کند؛
- Stage AI فقط Scope خودش را برای Completion حساب می‌کند؛
- هم‌زمانی Product AI در یک Process مسدود شده است؛
- Product AI فقط OpenRouter است: Model ذخیره‌شده اصلی + در صورت نیاز فقط `openrouter/free` با همان Key؛ AvalAI/Google/OpenAI fallback نیستند.

Rollback: `backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`. Local retest و QA تصویری Product 63/295 قبل از هر Production لازم است.

### Owner Windows workflow checkpoint — ERR-49-068

روی Head `0191a07...` تست قبلی و مجموعه 43 تست هدفمند کامل PASS شد و نسخه صحیح 8.9.8 در Foreground اجرا شد؛ بنابراین مشکل از Checkout/نسخه قدیمی نبود. QA واقعی Product 63 نشان داد خود Workflow ویندوز معیوب شده بود: فیلدهای Stage 1 می‌توانستند پر باشند ولی مسیر پایین صفحه قبل از Persist همان Stage، Readiness ذخیره‌شده را چک می‌کرد و کنترل `ثبت` نیز در پنل جداگانه Rail قرار گرفته بود. نتیجه برای اپراتور همان حالت «پر است ولی تیک نمی‌خورد و جلو نمی‌رود» بود.

Hotfix جدید پایین صفحه را دوباره مرجع عملیات می‌کند: `✅ تأیید و مرحله بعد` ابتدا Stage جاری را Persist/Finalize می‌کند، سپس جلو می‌رود؛ `✨ پرکردن ناقص‌ها با AI` و `✏ اصلاح مرحله` کنار آن هستند و Refresh آنها را پس نمی‌زند. Callback واقعی Buttonهای قدیمی AI نیز به موتور 3I.39 وصل شده است. هویت واقعی انگلیسی Source مثل `Flexi Gecko` در کنار متن فارسی مجاز است، اما لاتین نامرتبط رد می‌شود. Fallback دیگر Key/Model یک Provider را برای Provider دیگر استفاده نمی‌کند.

Rollback: `backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`. تست Local و QA Product 63 روی Head نهایی جدید لازم است؛ Production دست نخورده است.

### Owner Local test checkpoint — ERR-49-067

روی Head `9f3b765...` کامپایل PASS شد و از 43 تست هدفمند فقط یک Fixture قدیمی خطا داد: داخل Mock مربوط به `seo_description_fa` عبارت لاتین `AI` وجود داشت، درحالی‌که قرارداد جدید SEO را فارسی-only می‌خواهد. قانون Runtime تغییر نکرد؛ فقط Fixture در `38cb415bc12d7ec08943809fd14f3478b3ddac1b` اصلاح شد. Launch طبق Gate اجرا نشد. قدم بعدی Pull و تکرار همان تست‌هاست؛ Production دست نخورده است.

### Owner readiness/checker checkpoint — ERR-49-066

تست واقعی Product 63 نشان داد مشکل باقی‌مانده فقط Refresh نبود: Stage ownership، Checker، AI repair و علامت‌های Wizard قرارداد واحدی نداشتند. اکنون عنوان فارسی فقط متعلق به Stage 1، Alt تصاویر متعلق به Stage 3 و متن/SEO متعلق به Stage 4 است؛ Checker و Fixer از قواعد یکسان استفاده می‌کنند؛ Wizard برای تیک و ادامه از `data_ready` استفاده می‌کند و `ثبت` فقط Finalization است؛ مسیرهای قدیمی AI نیز به موتور نهایی 3I.39 متصل شده‌اند.

Rollback: `backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`. تست Local و QA foreground روی Head جدید هنوز لازم است؛ Production دست نخورده است.

### Owner SEO/readiness hotfix checkpoint — ERR-49-065

پس از رفع ERR-49-064 رابط حرفه‌ای 3I.39/3I.40 واقعاً نمایش داده شد، اما QA مالک نشان داد مقادیر SEO که AI در SQLite ذخیره کرده بود در بعضی Widgetهای قدیمی Readiness هنوز قرمز/ناقص نمایش داده می‌شد. Hotfix جدید پس از AI رکورد Product را از SQLite دوباره می‌خواند، Workspace/Lock/Wizard را Refresh می‌کند و Readiness نهایی 3I.40 را آخرین Painter قرار می‌دهد؛ یک Refresh کوتاهِ دوم نیز بعد از settle رابط انجام می‌شود.

Source: `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4`؛ Regression: `375961a1621c43f168b7c3fd76523c6d3c9c9a26`؛ Rollback: `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`. تست Local/Foreground هنوز لازم است؛ Production دست نخورده است.

### Owner visual-QA hotfix checkpoint — ERR-49-064

Canonical foreground 8.9.8 execution proved the correct source was running but ProductWorkspace stopped inside the older 3I.35 material action wrapper before 3I.39/3I.40 could render. The modern material/color picker is grid-managed; the obsolete 3I.35 action row used pack in the same parent.

Hotfix: `aa37dcf916dfab71409738f7087a171daffe4a0a` + regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`; rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`. Owner Local retest is required before Production work.

## Current verified checkpoint — 2026-08-29

- Catalog Center: `8.9.8` / build `2026.08.29.2`
- Runtime/package candidate: `55139b909f214f33994d76bc1e6fdfd028b5d6c7`
- Catalog 31–40 CI: `33247729316` PASS
- Single Active AI: `33247815007` PASS
- Windows Portable: `33247815027` PASS
- Artifact ID: `9713426658`
- EXE SHA256: `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`
- Store migration `0040_phase50_filament_offer_operations`: CI `33246843145` PASS through full SQLite migration and regressions.
- Last verified Production DB state remains only `0034/0035` applied; later migrations are not assumed.
- Next gate: owner Local backup + 0040 apply/regression + foreground 3I.40 visual QA.
- Canonical phase doc: `docs/phases/PHASE49_3I40_COMMERCE_PRECISION_READINESS_TRUTH.md`.

Older 3I.38/8.9.6 sections below are preserved as historical foundation and do not override this checkpoint.

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

Historical 3I.35 GitHub runtime (superseded by the Current verified checkpoint above):
- Catalog Center `8.9.1` / build `2026.08.27.3`,
- Windows runtime `2622818d898e19b745c61ff653b80c03d22288f1`,
- Windows run `33060047878` PASS; artifact `9641338334`; EXE SHA256 `3099b26713a460fbd55c1204ef750b37dbef542269b5520fd393526cd8c9476c`,
- Phase50 run `33059883188` PASS through migration `0039` and 16 regressions,
- historical pending chain at that checkpoint was `0036 → 0037 → 0038 → 0039`; current code also contains `0040`, and actual Production pending state must be freshly read-only verified.


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

## 5) Current Windows development — Phase49.3I.38
Catalog Center `8.9.6`, build `2026.08.27.8`.

Preserved mature foundations:
- Product Explorer paging and explicit-only global refresh,
- existing browser/profile/parser/image/file receive pipeline,
- mature `discovered_urls` identity ledger,
- Product source URL/history guard,
- registered Profile ledger and Store transport,
- material/brand/manufacturer/color offers,
- one configured AI Provider/Model/key boundary,
- one Link / Saved-Crawled Data / Screenshot Product AI engine,
- seven-stage readiness/finalization locks.

3I.38 adds:
- permanent visibility of crawled/received/rejected Product URLs in a dedicated ledger UI,
- Listing continuation cursor that moves deeper after old results instead of replacing the discoverer,
- exact behavior for repeated acquisition: old 100 identities skipped, next 100 new identities queued,
- operator `رد دائمی + حذف فایل‌ها و عکس‌های محلی`,
- deletion confined to the Product directory below Catalog `collected/`,
- source URL/external ID retained as a rejected tombstone,
- terminal Direct Link guard before browser/HTTP/image/file acquisition,
- explicit restore required before a rejected identity can be received again,
- same mother AI engine for selected-Product Bulk Content/SEO,
- single-stage cleanup/completion such as Stage 4 only,
- out-of-scope and finalized Stage immutability,
- image-only AI no-op when image SEO is already complete.

Windows verification:
- runtime snapshot `c904193a7f0af9aad80365834ec3f0b856e77dc9`,
- Phase49.3I.31–38 run `33077213590` PASS with 84 tests,
- Single Active AI run `33077239617` PASS,
- Windows Portable run `33077239660` PASS,
- artifact ID `9648474905`,
- EXE SHA256 `6490e4815f1e6e0d75f09c112bb6990041578616f170954f62fae037b98bd507`,
- owner automated Local Django DB/test evidence from the previous gate remains through `0039`,
- current next gate is owner visual/functional Local QA of 8.9.6 before any Host work.

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
1. Local Windows clean pull + exact final GitHub HEAD verify.
2. Run current `catalog_center\RUN_PHASE49_3I31_SMART_AI_GATE.ps1`.
3. Foreground owner QA of Catalog Center 8.9.6:
   - ordinary new Crawl/Direct/image/file receive remains healthy,
   - crawl ledger shows known identities,
   - reject/purge keeps tombstone and deletes only the Product collected folder,
   - repeated Listing skips old identities and continues deeper,
   - rejected Direct Link skips before acquisition,
   - Bulk Stage-4 SEO and single-stage cleanup use the same mother AI engine,
   - locked stages/Profile ledger remain intact.
4. Local Django/SQLite check/drift/Store/Profile/Checkout regression.
5. Read-only Host verify actual branch/HEAD/worktree/live remote SHA/Python/Django/MySQL/migration state.
6. Exact migration plan.
7. Disk + mysqldump verify.
8. Fresh tracked-source + environment + MySQL backup with checksums.
9. Explicit branch fetch to `FETCH_HEAD` per `ERR-50-007`; exact target + ff-only.
10. Deploy GitHub source.
11. Repeat Django check/drift/DB/plan.
12. Apply only actually pending verified migrations; last Production evidence still confirms only `0034` and `0035`.
13. collectstatic + Passenger restart.
14. Home/Store/Admin/Product/Profile API/Checkout/private-media verification.
15. Controlled new order and owner browser QA.
16. Update docs with exact Production SHA/backup/migrations.

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
