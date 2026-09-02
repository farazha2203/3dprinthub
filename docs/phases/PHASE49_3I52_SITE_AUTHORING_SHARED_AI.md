# Phase49.3I.52 — Site Authoring Parity + Shared Host AI

Date: 2026-09-02

Status: `IN_PROGRESS / SOURCE IMPLEMENTATION STARTED / CI NEXT / PRODUCTION NOT TOUCHED`

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
