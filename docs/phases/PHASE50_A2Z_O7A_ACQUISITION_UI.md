# Phase50.A.2Z-O7A — MakerWorld Single Product / Search Acquisition UX

Status: GITHUB_UPDATED / EXACT_SHA_RUNTIME_LAUNCHED / OWNER_UAT_NEXT
Date: 2026-09-26
Branch: `wip/phase50-a2z-o7a-acquisition-ui-20260926`
Entry HEAD: `eba70a55bd6907564744f3805005cac1f7659531`
GitHub implementation commit: `4a7d2771f0b982db3deea5b5e48b058ea6c1882e`
Rollback branch: `backup/pre-o7a-acquisition-ui-20260926`

## Requested Delta

Owner requires the latest v8.9.11 Catalog Center acquisition page to expose two unambiguous workflows:
- one exact Product URL, e.g. MakerWorld `/en/models/...#profileId-...`;
- one Search/Listing workflow, accepting either the exact MakerWorld `/en/search/models?keyword=...` URL or a plain keyword;
- Source/Product refresh must belong to the Inventory workspace, not Search;
- proven acquisition methods remain available but low-frequency diagnostics belong under Advanced.

## Touched Surfaces

- `catalog_center/qt6/pages.py`
- `catalog_center/qt6/kernel.py`
- focused Operations/Crawl regression files only

## Must Not Touch

- v8.9.11 Product filters/categories and Product identity authority;
- O1 independent Instagram Post and Instagram Story actions;
- O6A1 automatic Story Product-link transport;
- pricing, Profile, Filament, Site ACK and Social receipt authority;
- Django schema, Host source, Production and provider objects.

## Implementation

- Outer Operations tabs are now: Inventory, Single Product, Search/Search-Link, History.
- Single Product preserves the exact supplied URL and uses the mature `run_single` path with adaptive failover enabled.
- Search preserves Preview/select/import and uses the mature `run_batch` path.
- MakerWorld keyword-only input resolves to `https://makerworld.com/en/search/models?keyword=<query>`.
- Product URLs pasted into Search are detected by the Source `model_url_pattern` contract, moved to Single Product, and never enter the listing crawler.
- Source refresh is physically owned by Inventory with independent Product/image limits.
- Browser method, Saved HTML and other proven compatibility controls remain under Advanced.
- Shared Source selector remains visible without duplicating Source authority.

## Verification

- Exact new O7A flow tests: 5/5 PASS.
- Related Operations/Crawl regression: 155/155 PASS.
- Phase50 broad regression: 147/147 PASS.
- Instagram/Buffer/Story focused regression: 65/65 PASS.
- Category provider bridge: 3/3 PASS.
- `py_compile`, `compileall`, `pip check`, `git diff --check`: PASS.
- Qt `RUN_QT.ps1 -VerifyOnly`: foundation/full-parity/operator-launcher PASS.

One unrelated Professional Commerce profile-identity test still fails identically on clean entry HEAD `eba70a55`; it is baseline debt and not an O7A regression.

## Safety / Rollback

Pre-continue dirty-diff backup:
`D:\projects\3dprinthub-backups\o7a-dirty-precontinue-20260926-224540\dirty-before-continue.diff`
SHA256: `F422FDA4C83A83D6C97EA249482D6C0942D3B270554338689D29C030EF8A5D74`.

No Product crawl was automatically started, no Instagram Post/Story was sent, no provider object was mutated, no Django migration was introduced, and Production/Host were untouched.

## GitHub / Runtime Acceptance

- Implementation commit `4a7d2771f0b982db3deea5b5e48b058ea6c1882e` pushed; Local=Remote 0/0.
- Fresh Catalog rollback: `D:\projects\3dprinthub-backups\phase50-o7a-runtime-20260926-231236\catalog-before-o7a-runtime.sqlite3`.
- Rollback SHA256: `d3e18fc9154562b47b7cbd1286bb0e279f61b80f8876650946efcc150581467a`.
- Source/backup quick_check=ok, page count 226078/226078, Products 962/962.
- Post-launch read-only counts remain Products=962 / Crawl=1178 / Receipts=539 and quick_check=ok.
- Exact-SHA Qt VerifyOnly PASS after push.
- Visible runtime is v8.9.11 from the O7A worktree; window title: `3DPrintHub Catalog Center v8.9.11 - Qt 6`.
- No obsolete v8.9.10 Catalog runtime is active.

## Exact Next Gate

Owner functional UAT: use one disposable direct MakerWorld Product URL and one MakerWorld Search URL. If a live Source method fails, patch only that acquisition boundary with a focused regression; do not alter Social/category/Product authority.
