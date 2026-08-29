# Phase49.3I.41 — Central Filament Library + Grouped Product Checklist + Site Sync

Updated: 2026-08-29  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Status: `IMPLEMENTED / GITHUB_UPDATED / OWNER LOCAL TEST NEXT / PRODUCTION NOT DEPLOYED`

## Problem

Stage 2 had technically supported an extended Treeview selection, but the operator workflow did not scale to a real inventory of many Filaments:
- selecting several rows depended on Windows Ctrl/Shift behavior and was not visually obvious;
- currently selected Filaments were not shown in a dedicated persistent selection box;
- manufacturer/brand/material values were repeatedly typed even though they are global inventory facts;
- global Filament definition and Product assignment lived in the same dense Stage-2 surface;
- a Filament saved in Catalog Center was not a first-class independently synchronized Site entity.

The operator requirement is a reusable global Filament library and a Product checklist, not a per-Product redefinition form.

## Requested contract

1. Define a Filament once and reuse it across Products.
2. Keep manufacturer, brand and material history reusable in editable selectors.
3. Group inventory by material type, e.g. PLA, PETG, ABS.
4. Select one or many Filaments with one-click checklist semantics; no Ctrl/Shift requirement.
5. Show a separate `انتخاب‌های این محصول` box that always reflects the current Product draft.
6. Clicking a material group toggles all Filaments in that group.
7. Product assignment remains explicit through `ثبت انتخاب‌ها روی این محصول`.
8. Product-specific fixed price remains Product-owned and must survive global inventory refresh/checklist saves.
9. New/Edit Filament belongs to the main Catalog Center navigation under `فیلامنت‌ها`; Product Stage 2 links to that library.
10. Every Filament Save and Product Filament commit attempts Bridge sync to the Site.
11. Weight, stock, roll price, USD/FX, print/supervision rates, preheat, image and color metadata travel with the Filament.
12. Local Save is not rolled back merely because Site sync is unavailable; the operator receives a truthful sync status.
13. Deactivation is soft locally and is synchronized as `is_active=false` to Site.
14. Existing mature Product publish, image, crawl, AI, profile and revision contracts remain intact.

## Windows design

### Main application — Filament Library

New sidebar page: `فیلامنت‌ها`.

The page provides:
- grouped rows by material type;
- search by material/brand/manufacturer/color;
- New / Edit / Deactivate / Refresh;
- explicit `Sync همه با سایت`;
- roll weight, current stock, sale price, effective price per gram, preheat and Site sync status.

The editor reuses known values:
- manufacturer,
- brand,
- material.

These fields are editable Comboboxes: an existing value can be selected or a new value typed.

Color semantics are preserved:
- `color_type`,
- primary HEX,
- secondary HEX,
- tertiary HEX,
- optional Filament image.

The live rate calculator shows the final roll basis and effective price per gram.

### Product Stage 2 — grouped checklist

The old manufacturer/material filtered Treeview and Ctrl/Shift guidance are hidden by the final composition layer.

The replacement has two panes:
- `Filamentهای موجود — تفکیک بر اساس نوع`
- `انتخاب‌های این محصول`

Checkbox states:
- `☐` not selected,
- `☑` selected,
- `◩` partially selected material group.

Single-click behavior:
- child row toggles one exact brand/material/color Filament;
- material group row toggles the entire group.

The draft selection is visible before persistence. Stage-2 footer confirmation persists the same Phase49.3I.41 checklist before readiness/finalization, so the operator cannot visually select one set while confirming another.

## Product pricing authority

Global Filament operational facts are refreshed from the central library by exact:
`manufacturer/brand + material + color`.

Product-specific fixed prices are preserved when checklist selections are re-saved.

Formula preview uses the current checklist draft, including newly selected/deselected Filaments, so the price preview and the visible selection cannot diverge.

## Site Bridge contract

New authenticated routes, reusing the existing Catalog Bridge bearer token:

- `GET /api/catalog-bridge/v1/filaments/`
- `POST /api/catalog-bridge/v1/filaments/sync/`

Contract: `phase49-filament-library-v1`.

Server identity:
- Material,
- brand,
- color.

Server stores/updates the existing `store.phase39_models.MaterialColorOption` entity and existing Phase50 fields.

No new Django migration is introduced by 3I.41. It depends on the already-existing:
- `store.0039_phase50_filament_offer_pricing`
- `store.0040_phase50_filament_offer_operations`.

Production is currently not claimed to have 0039/0040 applied. Production deployment therefore remains blocked until Host read-only migration verification, backup and the normal approved migration/deploy gate.

## Safety / must-not-touch

This phase does not replace:
- crawler/direct-link acquisition,
- image/file acquisition,
- AI provider contract,
- Product revision/slider revision synchronization,
- Product profile snapshots,
- Store checkout/order snapshots,
- existing Product publish Batch path.

No secrets are stored in Git or Filament payloads.

## Rollback

`backup/pre-phase49-3i41-filament-library-sync-20260829` → `92a3f4dfcf64d5fedaf837eb9a37dac028cabd59`.

## Required Local verification

Before acceptance:
- clean canonical Windows checkout and exact GitHub head;
- fresh Catalog SQLite backup;
- verify intended Local Django DB and migration state;
- apply only actually pending `store.0040` locally if 0039 is already applied and the migration plan is exact;
- Catalog compile and Phase49.3I.36/39/40/41 regressions;
- Django Bridge/Filament/Store tests;
- foreground Catalog Center visual QA;
- local Bridge sync QA.

## Owner visual acceptance

The owner should be able to:
- see all existing Filaments grouped as PLA/PETG/etc.;
- select multiple rows without keyboard modifiers;
- see all chosen Filaments in the Product selection box;
- toggle a whole material group;
- create one Filament in the main library and then select it from any Product;
- reuse known manufacturer/brand/material values without retyping;
- preserve Product fixed prices when changing the global Filament library;
- see stock/weight/rates sync to the Site after Bridge verification.

Only after this passes should Host deployment begin.
