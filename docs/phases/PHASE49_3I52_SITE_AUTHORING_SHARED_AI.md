# Phase49.3I.52 — Site Authoring Parity + Shared Host AI

Date: 2026-09-02

Status: `GITHUB_UPDATED / WINDOWS QT CI PASS / SITE ADMIN-BRIDGE CI PASS / PORTABLE PASS / OWNER LOCAL QA NEXT / PRODUCTION NOT TOUCHED`

Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Pre-phase rollback: `backup/pre-phase49-3i52-site-authoring-ai-parity-20260902` → `75d0960cabe1673f586103bae2e3216f71947012`.

## Requested delta
- Site must remain fully usable if the Windows application is unavailable.
- Admin must be able to add/edit Product, Product Profile, price strategy and Variants on the canonical Site database.
- Windows publish continues to map into the same Product/Profile/Variant tables; no duplicate commerce database.
- Site Product pages must continue consuming the same canonical pricing/profile/Filament facts.
- Host must get the same Structured + semantic-validated Persian Product AI method used by Catalog Center.
- Auto AI policy prefers a verified exact free Persian Structured model, then a verified low-cost model under an explicit budget.
- AI knowledge/policy must live in a root `ai/` folder so the method can be reused project-by-project.

## Must not touch
- no direct Production source edit;
- no Production migration/deploy before Local acceptance and Host read-only audit;
- no Secret in database/Git/logs;
- no hidden Provider switch after runtime selection;
- no variable OpenRouter router as final Product model;
- no AI changes to price, stock, material/color, license, factual dimensions/weight or publish state;
- no second Product/Profile/Variant database.

## Data ownership
Product content/SEO:
- Site Admin or Windows may edit through revision-aware canonical Product/Profile records.

Commerce facts:
- Product fixed price, ProductCatalogProfile pricing strategy/range, ProductVariant price engine, Material/Filament rates and inventory remain operator/business-engine owned.

AI:
- preview-first;
- apply only after explicit operator confirmation;
- content/SEO only.

## Test contract
- manual Site Product receives a canonical ProductCatalogProfile after save;
- fixed Product price mirrors into its canonical profile;
- Product Admin exposes profile edit surface and AI preview;
- AI proposal cannot mutate price/stock/license/publish state;
- Auto model policy rejects variable routers and non-Structured free models;
- Auto model policy selects an exact free model only after Persian Structured probe;
- no live AI key/network is required by CI.


## Implemented Site-authoring boundary
- Product Admin can create/edit Products when Windows Catalog Center is unavailable.
- The same canonical Product, ProductCatalogProfile, ProductVariant, Material/Filament and pricing engines remain authoritative.
- Manual Site Product save ensures one canonical ProductCatalogProfile; no second commerce database exists.
- Site Product page continues to read those same canonical Product/Profile/Variant facts.

## Shared Host AI
Root `ai/` contains the reusable policy/playbook and the 3DPrintHub Product adapter.
- Host secrets are environment-only.
- Windows may use the mature OS Credential Store.
- exact model override is honored only for a deterministic model id;
- variable OpenRouter routers are rejected for Product work;
- Auto selection evaluates text/Structured candidates, runs a Persian Structured probe, prefers verified free, then a bounded low-cost candidate;
- AI is Preview → explicit Apply;
- AI may update content/SEO only and cannot mutate operator-owned pricing, stock, material/color, license, production facts or publish state;
- existing operator technical facts win over an AI key collision.

## 3I.52B — Bidirectional Product sync
Rollback: `backup/pre-phase49-3i52b-bidirectional-site-sync-20260902` → `48290db404739f07e322a700b6baa71d6b801871`.

Bridge:
- Product serialization includes source name/code/url, category slug, pricing strategy, pricing inputs and technical summary;
- Product listing supports bounded `limit + offset` pagination;
- Product update accepts the matching Pricing/Profile fields under the existing optimistic revision contract.

Windows:
- Products exposes `↻ دریافت تغییرات سایت`;
- Site Products match Local by Desktop id, then server id, then source identity;
- a clean Local mirror accepts a newer Site revision;
- dirty/unpublished Local state plus a newer Site revision produces an explicit conflict and no overwrite;
- a Site-only Product becomes a Local `reference_only=1` mirror and cannot enter the mature publish queue until it has a real acquisition/source identity;
- accepted Site facts update Local content, SEO, pricing/Profile, availability/stock/lead time, technical summary/features/keywords and Slider mirror fields without rewriting raw acquisition identity/media ownership.

Publish:
- existing Products with `server_product_id` must pass a live Site revision check before Batch packaging;
- revision mismatch or failure to verify revision fails closed;
- first publish without a server Product id still follows the mature path;
- after the guard, Batch 8.5 → FTP → Bridge → Store/public HTTP verification is unchanged.

## 3I.52B verification
Exact tested source checkpoint: `6d19bed7659b9ca4cd54ff1ffd1323ec423bea6a`.

- `33619876564` — Qt6 full parity — PASS;
- `33619876411` — Windows Portable — PASS;
- `33619876317` — Single Active AI — PASS;
- `33619558467` — Product Admin/Bridge/migration — PASS on runtime-equivalent `d6450ca2...`;
- `33619558562` — Variant/Profile Matrix — PASS.

The only delta from `d6450ca2...` to `6d19bed...` is the isolated Windows test fixture.

## Known implementation error and correction
ERR-49-096:
- first new Qt test exposed a missing `utc_now` import;
- after that runtime correction, the remaining tests failed because the isolated orchestration fixture crossed the real Bridge settings/token validation boundary;
- the fixture now provides an isolated Bridge settings object while network Product results remain mocked;
- the production Bridge credential guard was not weakened;
- final full Qt parity passed.

## Database / Production safety
- new Django migration in 3I.52/3I.52B: NO;
- destructive Catalog migration: NO;
- Production MySQL write: NO;
- Host/Production source change: NO;
- Secret persistence change: NO;
- last verified Production app commit remains `c283864290f9c989a9fcdf24ee8eef519560e917`;
- last verified Production Store migration evidence remains only through `store.0035`;
- 3I.51 additive migration candidates remain pending and must be audited on Host before any deployment.

## Owner Local acceptance next
Canonical runner: `RUN_PHASE49_3I42C_LOCAL_GATE.ps1` version `49.3I.52.1`.

Acceptance must cover:
- existing 3I.51 Product/Crawl/Profile/Filament behavior;
- Site pull of a newer clean Product revision;
- protection of a dirty Local Product from a newer Site revision;
- Site-only non-publishable Local mirror;
- no unintended Product publish;
- checksum-verified backup of the real Catalog SQLite.

Production remains blocked until owner Local acceptance, read-only Host/MySQL/migration audit and fresh verified backups.
