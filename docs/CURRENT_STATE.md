# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase50.A.1G — Velzon Operator Surface V2`
Status: `GITHUB CI TESTED / PRODUCTION DEPLOY NEXT`

## Production verified state
Production is currently verified at commit `bc7b97f9c63432b8105f52f61cf5cdae1369689b` on the active branch.

Verified Production environment:
- project root `/home/sfkilvrs/3dprinthub`,
- Python venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- migration plan empty,
- Product Admin real changelist HTTP/render gate PASS,
- Home/Store/Admin login HTTP 200,
- public Home private imported-media refs = 0,
- Production worktree clean.

Fresh rollback backup for the `bc7b97f` deployment exists at `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848` and contains a verified MySQL dump.

## Owner QA after `bc7b97f`
Owner visual QA confirmed that the Product Admin 500 is fixed and the business navigation is active, but exposed a remaining visual/interaction defect on Django changelist pages: the legacy `#changelist-filter` remained permanently visible as a narrow sticky column, squeezed the result table, and retained old Django labels/controls. The owner requested a substantially more modern, professional Velzon experience across Admin rather than another small CSS patch.

The owner re-supplied `master.zip`. The package was reviewed as Velzon Django Corporate `4.3.0` / Bootstrap `5.3.6`. Purchased vendor assets remain private and gitignored under `static/velzon_master/`; the public repository contains only project-owned adapter/integration code.

## Phase50.A.1G — Velzon Operator Surface V2
Implemented on GitHub as a final additive presentation layer over the mature Django Admin/Velzon shell:
- `static/admin/phase50-admin-console-v2.css`,
- `static/admin/phase50-admin-console-v2.js`,
- `templates/admin/base.html` loads the V2 assets,
- expanded Admin HTTP/static regression tests,
- CI now also performs `node --check` on the new JavaScript.

Visible behavior:
- changelists use the full content width instead of reserving a permanent filter column,
- native Django filters are preserved functionally but moved into an on-demand off-canvas/drawer opened by a `فیلترها` button,
- filter backdrop/close/Escape/reset and active-filter count are supported,
- legacy English Filter/Search/Action labels are normalized for the Persian operator UI,
- search toolbar, bulk actions, result table and pagination are card-based Velzon surfaces,
- result table has modern sticky headers, row hover and contained horizontal scrolling only when required,
- long Product/change forms gain a sticky horizontal section navigator and card fieldsets,
- existing Admin permissions/actions/models remain authoritative; no business or schema state is duplicated.

## Verification
GitHub Actions `Phase50 Product Admin Workspace CI` run `32955310832` PASS on runtime snapshot `3687d0922959fca53f2118be6dacd32639159346`:
- Python compile PASS,
- Admin V2 JavaScript syntax validation PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- unified Product Admin and representative Admin HTTP regressions PASS,
- no schema migration added.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt, and MySQL conditional-constraint warnings.

## Exact next work
1. Deploy the CI-tested Admin V2 snapshot from GitHub to Production with explicit verified `FETCH_HEAD` because of `ERR-50-007`, fresh rollback backup, no-migration gate, collectstatic and Passenger restart.
2. Production visual QA: Product changelist must have no permanent filter column; `فیلترها` opens only on demand; Product edit page must show the section navigator; representative Admin list/change pages must remain usable on desktop/mobile.
3. After Admin V2 acceptance, continue the requested Product engagement package separately: real Favorite/Save model, Product like/save/review/comment counters, and verified-purchase-only review policy with its own migration/tests/backup.
4. Then continue `Phase50.A.2 — Checkout & Delivery`.
