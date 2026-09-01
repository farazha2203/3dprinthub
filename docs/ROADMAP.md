# ROADMAP

Updated: 2026-09-01

## Current Windows/Desktop track — Phase49.3I.47

Status: `IMPLEMENTED + WINDOWS CI PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT DEPLOYED`.

Current code checkpoint: `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`.
Canonical phase: `docs/phases/PHASE49_3I47_QT_WORKSPACE_IMAGE_BULK_AI_SITE_IA.md`.
Rollback: `backup/pre-phase49-3i47-owner-workspace-20260901` → `ecfd9260c168140757781bb672eb57c77bcc4ee3`.

### Completed in 49.3I.46
- Product Gallery bounded SQL paging: initial 50 + incremental fetch.
- Product Table/Detail bounded SQL paging: initial 20 + incremental fetch.
- Crawl inventory bounded paging: initial 100 + incremental fetch.
- lightweight Product list projection, SQL-backed search/sort/filter and planner indexes.
- mature pre-Qt acquisition methods restored through headless Core/runtime.

### Completed in 49.3I.47
- Products reorganized into active, sent/published, archived and rejected/deleted lifecycle workspaces.
- legacy/local Product thumbnail fallback for old records without modern URL mapping.
- Product cards expose description excerpt + image count.
- sequential multi-select `AI تکمیل همه موارد` through one shared AICore and shared single-Product finalization path.
- every selected Product image receives consistent SEO metadata and unique numbered WebP filenames (`-01`, `-02`, `-03`, ...).
- Add Product/Crawl split into focused inventory/receive/history workspaces.
- Crawl inventory gains Windows-like gallery/image and details/table views with Product preview facts.
- Profile/Pricing split into three full-height task tabs with production/filament rows no longer clipped by nested scrolling.
- Django Admin adopts shared accessible task tabs for Product sales/source/SEO, pricing, material/color rates, site settings and quotes.
- Storefront Product information adopts progressive accessible tabs while preserving existing Variant/Profile/pricing authority.

### Verification
Qt/Desktop on `9984e3bb9ab5ff293ad275ecbe86dba3a96db4b1`:
- `33506242569` — `qt6-full-parity-windows` — PASS.
- `33506242669` — `phase49-3i17` — PASS.

Admin on `ef215ba09044cd421302f9057bf3c1565b99ef1e`:
- `33505851712` — `product-admin-workspace` — PASS.
- `33505851749` — `phase49-3i17` — PASS.

Storefront on `f4beec484f060063d00de4a5753a135a020cfea1`:
- `33506122579` — `phase50-variant2-gallery` — PASS.
- `33506122534` — `phase49-3i17` — PASS.

## Immediate acceptance gate
1. Owner clean ff-only pull on `D:\projects\3DPrintHub` to the final docs HEAD.
2. Run repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -ExpectedHead <final-head> -LaunchApp`; runner version is `49.3I.47.1` and backs up/checksums the real Catalog SQLite before QA.
3. Verify four Product lifecycle tabs, old thumbnails, card description/image count and sequential Bulk AI on disposable Products.
4. Verify one disposable Product with at least three images produces consistent SEO metadata and distinct numbered SEO files for every image.
5. Verify Add Product/Crawl three workspaces plus Gallery/Details inventory views and bounded scroll continuation.
6. Verify Profile/Pricing three full-height tabs and all production/filament rows.
7. Record owner Local foreground evidence.
8. Do not deploy Production from this gate.

## Next engineering slice after owner acceptance
- remaining Catalog stability work: worker/read connection discipline, serialized/batched writes, bulk discovery persistence, query auditor/slow-query health and resume/soak testing;
- Phase42D visual/accessibility polish based on real owner QA;
- re-ingest `webdesign1.zip` when the attachment is readable, register source-supported typography/layout/effects/SEO principles, then apply only grounded refinements;
- only later evaluate 42E default-launcher/package cutover.

## Web / Admin track
Current Admin/Storefront information architecture is implemented and CI-tested but not Production-deployed. Any later Host work must start with read-only verification of root/branch/HEAD/worktree/live SHA/Python/Django/MySQL/migration state, followed by exact migration plan, fresh backups/checksums and deploy only from the owner-approved GitHub commit.

Last verified Production application commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`.
Last verified Production migration evidence remains only `store.0034` and `store.0035`; no later migration is assumed applied.

Historical roadmap checkpoints remain available in Git history and dedicated `docs/phases/` documents.
