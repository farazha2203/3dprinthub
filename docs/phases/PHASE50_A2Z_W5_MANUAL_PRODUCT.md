# Phase50.A.2Z-W5 — Manual / Self-Produced Product

Status: ACTIVE / W5A FOUNDATION NEXT
Date: 2026-09-27
Branch: `wip/phase50-a2z-w5-manual-product-20260927`
Entry HEAD: `c9676820117cb41f8fa0f6c25e8249ca78600efc`
Rollback ref: `backup/pre-a2z-w5-manual-product-20260927`

## Forward blocking work before W5 continuation

The owner-requested Crawl/Staging recovery is being completed first on the same
W5 checkout. Phase A is currently `IN_PROGRESS / LOCAL_TESTED`: the Qt live
acquisition panel distinguishes Preview/review, queued, downloading,
completed, skipped/duplicate, and failed candidates and shows skip/error reasons.
This is UI-only; the canonical Catalog remains untouched. The required order is
A visibility -> B hard unique quota -> C promotion gate -> D duplicate
prevention -> E read-only duplicate audit/safe merge -> F full regression and
desktop acceptance, then return to W5A.

Phase B is now `LOCAL_TESTED`: discovery uses a bounded over-fetch probe so
known/published/blocked/duplicate identities cannot consume the requested new
Product quota, while persistence remains capped at the requested number of new
unique identities. Isolated duplicate-first-page acceptance and Qt VerifyOnly
remain required before B is `ACCEPTED`.

The Product image-truth hotfix is `LOCAL_TESTED` in Build `2026.09.27.8`.
Gallery reconstruction now prefers exact source URLs (including query variants),
normalizes legacy `local-display://` aliases, excludes stale uncanonical files
from a canonical gallery, and collapses aliases that resolve to one physical
file. Product #1076 was verified read-only on an isolated Catalog with exactly
four canonical cards (01–04) and no stale 05 card; focused image/media tests are
`41/41`. Canonical Catalog, Host, and Production were not changed.

Phase D identity hardening is now `LOCAL_TESTED` in Build `2026.09.27.9`.
`Database.upsert_product` returns the authoritative existing row when a
non-empty Product fingerprint or `server_product_id` is already owned locally,
preventing a second Product across acquisition/site-mirror paths. The focused
identity regression is `10/10`; full related regression and the read-only
duplicate audit remain before Phase D acceptance. No canonical Catalog write or
duplicate merge has been performed.

Phase D is now `ACCEPTED / LOCAL_ONLY` in Build `2026.09.27.13`: isolated Qt
VerifyOnly/UI smoke passed; identity/media regression is `19/19`; Crawl/
Acquisition regression is `52/52`; and the canonical read-only audit found zero
duplicate groups for Source+External ID, normalized URL, fingerprint, or valid
nonzero server-linked identity. Phase E report and rollback plan are recorded
in `docs/PHASE50_A2Z_PHASE_E_DUPLICATE_AUDIT_20260927.md`. No merge or delete
was performed.

## Phase F gate — 2026-09-27

Status: `IN_PROGRESS / BLOCKED_BY_W5_TESTS`.

The selected full Crawl/Product/Media/Social/UI suite ran `161` tests: `159
PASS`, one failure and one error in `test_phase50_a2z_w5_manual_product.py`.
The failure expects an old scalar `added == 1` contract while the current
manual-image API returns a list of added identities. The error patches an
instance method on the slotted `ApplicationKernel`, which is read-only. These
are W5 test/fixture contract issues, not a Catalog or Production failure.

Independent gates passed: compileall using a writable pycache prefix,
diff-check, final isolated Qt VerifyOnly (`QT6_FOUNDATION_VERIFY=OK` and
`QT6_42B2_FULL_PARITY_VERIFY=OK`), and direct Story-tab UI smoke. Canonical
Catalog SHA256 and size were identical before/after, so no Catalog mutation
occurred. Phase F acceptance is withheld until the two W5 tests are corrected
and the full suite is green. No commit/push/deploy has occurred.

## Objective

Add a first-class operator-created Product path for items designed/produced locally without a marketplace identity. Reuse the accepted Product Wizard, Profile/Filament, image, readiness, Site same-identity publish, revision and independent Instagram Post/Story authorities. Do not create a second Product model or a parallel publishing pipeline.

## Owner/master requirements

- operator title, notes and media;
- normal Profile/Filament controls;
- optional external reference link;
- AI may create Persian content/SEO from operator description and images;
- AI must never invent weight, print time, dimensions, material or license;
- existing readiness, Site media/Profile/Variant, Social receipt and revision contracts remain authoritative.

## Identity contract

- Manual Product source authority is `source_code=manual`.
- Generate one immutable local external identity `manual-<uuid>`; never reuse title as identity.
- Internal canonical identity URL is a non-network `manual://product/<external_id>` URI.
- Optional HTTP(S) reference is provenance only, never Product identity and never a Crawl input.
- Manual Products must never enter `discovered_urls` or Add Product/Crawl discovery.
## Data/provenance contract

- Operator title is factual operator input and may seed both source title and visible title exactly as entered.
- Operator notes are factual operator input and may seed the saved-data AI context.
- Reference URL is stored in existing source provenance JSON; no Catalog schema migration is required.
- Product media is copied through the mature Product-local ImageCore path and selected for Site using the existing image authority.
- License/author/technical values start empty unless the operator explicitly enters them later.
- No default weight/time/dimensions/material/license values are fabricated.
- Manual Products open immediately in the existing seven-stage Product Wizard.

## AI contract

- Manual Product AI always uses saved operator data, never the internal `manual://` identity as a network fetch.
- Whole-product AI scope is editorial only: Quick/Content/Slider; Commerce/Specs/Publish remain operator/factual.
- Image-stage smart repair remains local/deterministic.
- Manual Specs AI is fail-closed: no visual estimation is permitted to become Product facts.
- If optional image understanding is used, it may describe visible appearance/use only and cannot write technical fields.

## Microphases

### W5A — Creation / UI / media foundation
- ProductCore manual creation boundary + immutable identity/provenance.
- Products-page `محصول دستی` dialog: title, notes, category, optional reference link, optional images.
- Existing ImageCore copies selected local images.
- Open the created Product in Product Wizard.
- Reference button opens only the explicit external reference URL.

### W5B — Manual AI safety
- Force saved-data mode for manual Products.
- Restrict whole-product AI to editorial stages.
- Block technical/spec estimation/write paths for manual Products.
- Add focused no-invention regressions.
### W5C — acceptance / GitHub gate
- focused + related Product/Wizard/Image/Profile/Filament/AI/Site/Social regression;
- py_compile/compileall, diff-check, Qt VerifyOnly;
- fresh integrity-checked Catalog rollback before any real canonical manual Product acceptance;
- isolated real Product creation/media/open/edit acceptance first;
- only then one bounded canonical owner acceptance if needed;
- selective commit/push and Local=Remote proof;
- Windows-only unless source audit proves a Server delta.

## Must not touch

- existing marketplace Product identities/Crawl ledger;
- Product categories taxonomy authority;
- Profile/Filament pricing formulas or stock authority;
- Site same-identity revision semantics;
- Slider membership;
- existing Instagram Post/Story receipt truth;
- Production Host unless a later verified Server delta requires it.

## Success criteria

A manually created Product can be entered from Products, receives a stable non-marketplace identity, accepts operator media, opens the mature Product Wizard, uses normal Profiles/Filaments/readiness/publish/Social flows, and cannot acquire guessed technical facts through AI.

## Immediately following phase

Phase50.A.2Z-W6 — Source Video + Reel.

## Phase F acceptance — 2026-09-27

Status: `ACCEPTED / LOCAL_ONLY`.

The two W5 test contracts were corrected without changing runtime behavior.
Focused W5 tests passed `7/7`; the full selected Crawl/Product/Media/Social/UI
suite passed `161/161`; compileall, diff-check, final isolated Qt VerifyOnly and
Story-tab UI smoke passed. The canonical Catalog remained byte/hash unchanged.
No commit, push, deploy, Host or Production mutation occurred.

Next: continue W5 manual-product acceptance, then W6 source video/reel. Any
Host deployment still requires the GitHub commit/push and exact-SHA gates.

## W5B manual AI safety — 2026-09-27

Status: `LOCAL_TESTED` in Build `2026.09.27.16`.

- Saved operator data is the only Manual Product AI context.
- Whole-product AI is restricted to editorial stages `quick`, `content`, and
  `slider`.
- Specs, Commerce, Publish and production estimation paths are fail-closed for
  Manual Products.
- Visual AI schema has no technical/license fact fields; no weight, dimensions,
  print time, material, filament or license can be invented from an image.
- Direct no-invention/manual-identity tests: `4/4 PASS`.
- No provider, canonical Catalog, Host or Production mutation occurred.

Next exact phase: W5C acceptance and GitHub gate. W6 Source Video/Reel starts
only after W5C is accepted.

## W5C acceptance / GitHub gate — 2026-09-27

Status: `LOCAL_TESTED / READY_FOR_GITHUB_GATE` in Build `2026.09.27.17`.

- Related W5 acceptance: `46/46 PASS`.
- Compileall and diff-check: `PASS`.
- Final isolated Qt VerifyOnly: `QT6_FOUNDATION_VERIFY=OK`,
  `QT6_42B2_FULL_PARITY_VERIFY=OK`.
- Isolated Manual Product create/media/Products/Wizard acceptance: `PASS`.
- Fresh backup: `quick_check=ok`, SHA256
  `9a64e4ed834e9f98940f481649ca7e464371847cda7ea7d2c58ffa9f8d41e60c`, size
  `975294464`.
- Source/Server delta audit: zero Server/static/migration/Host files.
- No canonical Product, Provider, Host or Production mutation occurred.

Next: commit/push this preserved W5 worktree and verify exact Local=Remote.
No Host deploy is required for this Windows/catalog/docs-only change. W6
Source Video/Reel begins after the GitHub gate is verified.

## W5A isolated acceptance — 2026-09-27

Status: `LOCAL_TESTED` in Build `2026.09.27.15`.

- Related W5/Product/Wizard/Profile/Filament/Image/Social tests: `46/46 PASS`.
- Isolated writable Catalog smoke: manual Product creation, real local image
  copy through ImageCore, Products-page entry, and seven-stage Wizard load all
  passed.
- Identity verified as immutable `source_code=manual` + `manual-*` external ID;
  manual rows in `discovered_urls` remained zero.
- Canonical Catalog, Host, Production and provider state were not changed.

Next exact phase: W5B manual AI safety — saved-data-only editorial AI,
technical/spec no-invention guard, and focused regression. W6 remains after W5.
