# Phase50.A.2X — Server material parity hotfix

Status: **LOCAL_TESTED / GITHUB PROMOTION NEXT**
Date: 2026-09-21
Production baseline: `03042d0430ee6e688c992c875f12edc969df103d`
Branch: `wip/phase50-a2x-server-parity-20260921`

## Incident
Catalog Product #620 reached the Production receiver in batch `desktop_catalog_v85_20260921_160339` / UUID `8be482aa-5469-439d-bad3-6dcab3f9f8de`, but the transaction rolled back with `REPUBLISH_PARITY_MISMATCH`. Every reported mismatch was material-name case only: Desktop `pla/petg` versus canonical Store `PLA/PETG`.

The Store material resolver is already case-insensitive. Therefore parity must compare material identity with the same semantic rule while keeping Brand, Manufacturer, Color, stock state, numeric commerce fields, profile keys, media names/SHA and all other parity checks strict.

## Delta
- Add a material-only case-insensitive parity comparator.
- Keep all non-material scalar parity checks unchanged and strict.
- Carry the A2X authoritative SEO assignment onto the Production release lineage so stale Site SEO is not retained across Desktop re-publish.
- No migration and no schema change.

## Verification
- New regression proves lowercase expected material and canonical uppercase Store material pass parity.
- Existing extra-active-Variant failure regression still fails closed as intended.
- Existing profile-price parity regression remains green.
- Unified sync regression remains green.
- Focused Server gate: 6/6 PASS.
- Python compile, `git diff --check`, Django check and `makemigrations --check --dry-run`: PASS.

## Deployment gates
- [ ] Commit/push exact hotfix SHA and verify GitHub remote equality.
- [ ] Reverse-tunnel Host preflight: exact root/branch/HEAD/clean state/MySQL identity/no migration plan.
- [ ] Fresh source/env + MySQL rollback backup.
- [ ] Explicit fetch of the hotfix branch and ff-only deploy from GitHub.
- [ ] Passenger restart and HTTP/readiness verification.
- [ ] Controlled retry of #620 only after changed condition is live.
- [ ] Verify Product/media/Profile/Slider parity and close the incident.
