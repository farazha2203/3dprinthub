# CURRENT PROJECT STATE

Updated: 2026-08-26
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Release: `Phase50.A.1H Admin Shell Stability + Phase50.A.2A Storefront Sales Profile Selector`
Status: `GITHUB CI TESTED / HOST READ-ONLY VERIFY NEXT`

## Last documented Production state
The last terminal-verified Production application commit recorded in repository documentation is `bc7b97f9c63432b8105f52f61cf5cdae1369689b`. The owner subsequently supplied screenshots showing the newer Velzon V2 surface, but no terminal transcript proving the exact current host HEAD was supplied in that step. Therefore the actual host HEAD must be re-verified read-only before the next deployment and must not be guessed.

Last verified Production environment:
- root `/home/sfkilvrs/3dprinthub`,
- venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`,
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`,
- `store.0034_phase50_variant2_commerce` applied,
- `store.0035_phase50_sales_profiles` applied,
- no pending migration at last verification,
- Home/Store/Admin HTTP 200,
- public Home private imported-media refs = 0.

Known fresh rollback backup from the Product Admin/business-navigation deployment: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-125848`.

## Owner QA — current requested delta
Owner QA of the Velzon V2 Admin identified two shell defects and one unfinished Storefront surface:
1. during refresh/navigation, the Velzon footer line/text could appear across the viewport before settling,
2. opening/navigating the right Admin menu produced a visible page jump and the 250px menu remained too narrow for Persian labels,
3. Product page still exposed the old flat Variant select even though sales-profile/size/build/weight/color/price backend metadata already existed.

## Phase50.A.1H — Admin Shell Stability
Implemented on GitHub without schema changes:
- added `static/admin/phase50-admin-shell-stability.css`,
- Velzon footer is kept in normal document flow instead of vendor absolute positioning,
- Admin shell/content use a stable flex-column min-height contract,
- right operator sidebar width increased from Velzon's 250px default to 290px with improved Persian label spacing/readability,
- disabled broad shell geometry transitions that visually amplify navigation movement,
- replaced active-menu `scrollIntoView()` with explicit scrolling of the internal SimpleBar/sidebar scroll element only,
- V2 filter drawer/full-width table behavior remains intact.

Root cause and prevention are recorded as `ERR-50-009`.

Verification:
- GitHub Actions `Phase50 Product Admin Workspace CI` run `32958276378` PASS,
- Admin CI snapshot `27335832e90c35dd95bb8a686dd89d1efd46dc8f`,
- JavaScript syntax PASS,
- Django check PASS,
- migration drift NONE,
- CI SQLite migrations PASS,
- Product/representative Admin regressions PASS,
- no migration added.

## Phase50.A.2A — Storefront Sales Profile Selector
The backend contract already existed and is now surfaced on the customer Product page as progressive enhancement:
- Product selection modes remain authoritative: full profile list / size / weight / build / size→build / build→size,
- uses existing public endpoint `/store/api/variant-commerce-options/`,
- renders modern choices for the configured selection mode and available size/build/weight/material/color/quality dimensions,
- selected profile updates displayed profile price and summary facts including part/shipping weight, print time and package dimensions,
- keeps the mature native `variant-select` as a fallback,
- synchronizes the native Variant ID and dispatches the existing change event, so current price/cart logic and `AddToCartForm` remain authoritative,
- no duplicate Product/Profile/Variant state and no new migration.

Verification:
- GitHub Actions `Phase50 Variant2 Gallery CI` run `32958296546` PASS,
- Storefront selector CI snapshot `e3c57311c0c3980befeaf6012f3bb8fc502333bc`,
- Storefront JavaScript syntax PASS,
- Django check PASS,
- migration drift NONE,
- migration plan/CI migrations PASS,
- Variant2/gallery/profile-selector regression PASS.

## Scope boundary
This release makes the Product selector visible/usable and keeps the canonical Variant ID flowing into the mature cart path. Full immutable selected-profile snapshot completion, normalized carrier quotes, insured value and final shipping/delivery workflow remain subsequent Phase50.A.2 work and must not be claimed complete yet.

Known warnings remain CKEditor4 maintenance/security debt, `store.W026` in-memory realtime debt and MySQL conditional-constraint warnings.

## Exact next work
1. Run a read-only Host audit: actual branch/HEAD/worktree, live GitHub HEAD, fetch refspec, Python/Django, exact MySQL DB and `0034/0035`, migration drift/plan, private Velzon runtime assets and HTTP baseline.
2. If all gates are clean, compare actual host HEAD to the approved GitHub target, create fresh rollback/source/.env/MySQL backup, explicit verified branch fetch to `FETCH_HEAD`, no-migration gate, ff-only deploy, collectstatic and Passenger restart.
3. Production QA: footer must never cross the viewport during refresh; menu navigation must not scroll the document; sidebar must be 290px/readable; Product page must show profile-aware selectors and update the canonical Variant/price correctly.
4. Continue Phase50.A.2 checkout snapshot/shipping work, then Product engagement package (Favorite/Save + counters + verified-buyer review policy) according to owner priority.
