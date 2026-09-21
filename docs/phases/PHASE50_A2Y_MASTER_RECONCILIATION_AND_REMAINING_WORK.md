# Phase50.A.2Y — Master Reconciliation + Remaining Work Plan

Status: **IN_PROGRESS / DOCUMENTATION TRUTH FREEZE COMPLETE / CODE LINEAGE CONVERGENCE NEXT**
Date: 2026-09-21
Planning baseline (latest Windows lineage): `c86c66a11e2c62f8ca219bcb76abc19e5bfdcdbd`
Current Production/docs lineage: `e03bdd2b718fae3ce030df789c8b9db958d8d8ed`
Latest Windows worktree/shortcut source: `D:\projects\3DPrintHub-a2u-latest-windows`
Production Host source branch: `release/phase50-a2j-hero-20260915`

## Why A2Y exists
The project currently has two valid descendants of the same earlier baseline:
- the latest Windows/Product lineage through A2U -> A2V -> A2W -> A2X Slider at `c86c66a1...`;
- the Production Server parity/Hero persistence lineage through A2X Server at `e03bdd2b...`.

Neither branch is an ancestor of the other. Continuing feature work before reconciling them risks reintroducing the exact failure mode already seen in the project: fixing one subsystem by launching/deploying an older lineage and losing previously accepted Windows or Server behavior.

A2Y therefore becomes the only authoritative next engineering phase. Historical unchecked boxes in older ROADMAP sections are snapshots unless they are explicitly carried into this file.

## Repository/chat audit findings

### Confirmed complete and must not be repeated
- A2R manual card-transfer flow: Production accepted, receipt upload -> Admin review -> approval verified.
- A2S finance reconciliation/reviewer audit: Production accepted.
- A2U latest Windows recovery: latest image/gallery/SEO/screenshot lineage restored; Desktop shortcut currently targets the A2U worktree, whose HEAD has since advanced to A2X Slider.
- A2V image authority: same-identity Product media replacement and public byte parity verified.
- A2W W1/W2 media truth sync and authoritative selected-media replacement: accepted.
- A2W W3 Source Print Profile import and W4 material-family review: accepted.
- A2W W4.1 real data repair: #628 = 12x12x12 / 18x18x18 with all 16 active exact-family PLA offers; #625 keeps 5x5x5 on Profile 1 and owner-estimated 4x4x4 on Profile 2, both with all 16 PLA offers.
- A2X Server parity + Hero public-media persistence: Production verified. Product #620 -> Site Product #41 / Slider #17, revisions remain 1.
- Homepage current Production Hero HTTP/DOM/browser acceptance: canonical Product media, no public imported-working-media reference, no broken Hero image.
- #625 Instagram Feed + companion Story for its accepted revision already have successful receipts; do not repost an already represented revision.
- Store Reset was completed at the 2026-09-15 handoff milestone; old unchecked Store Reset lines are historical and must not be rerun as if still pending.

### Real open data gap proven now
Canonical Catalog SQLite currently contains 635 Products.
A2X Slider core fields are:
`image_url, title_fa, description_fa, alt_text, button_text, focus_keyword`.
Only 50 Products currently have all six fields populated; 585 Products are missing at least one. Slider membership is a separate manual checkbox and must remain operator-owned.

### Real open lineage gap proven now
Latest Windows A2X Slider branch:
`c86c66a11e2c62f8ca219bcb76abc19e5bfdcdbd`

Current Server/Production closure branch:
`e03bdd2b718fae3ce030df789c8b9db958d8d8ed`

Merge-base:
`b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`

The two heads must be converged before additional permanent feature work.

## Remaining phase order

### Phase50.A.2Y — Lineage Convergence + Truth Freeze
Status: **NEXT / IN_PROGRESS**

Required operations:
1. Create one convergence branch from the latest Windows lineage.
2. Bring in the Server parity + Hero persistence runtime changes from the Production lineage without reverting A2U/A2V/A2W/A2X Slider behavior.
3. Resolve only evidence-backed conflicts; no wholesale old-branch replacement.
4. Preserve current Product media authority, Source Profile/W4.1 behavior, Social v5, payment/manual-transfer code, Hero public-media boundary and Server republish parity.
5. Run Windows focused + broad regression, Qt VerifyOnly, Django focused Server parity/Hero tests, check/no-drift and diff-check.
6. Verify merged head contains no unintended migration/dependency/static delta.
7. Push exact convergence SHA and verify Local=GitHub.
8. Launch Qt from that exact SHA before any data backfill.
9. Only after acceptance, retarget the Desktop shortcut to the unified worktree/launcher.
10. Update CURRENT_STATE/ROADMAP/phase docs so this unified SHA becomes the sole forward development baseline.

Exit gate:
- one clean GitHub head contains both latest Windows and current Server/Production fixes;
- exact-sha Qt launches;
- all retained regression gates pass;
- no Production mutation is needed merely to complete source convergence.

### Phase50.A.2Z — Catalog Data Completion + Windows Operator Acceptance
Status: **PLANNED AFTER A2Y**

Required operations:
1. Fresh integrity-checked Catalog SQLite backup.
2. Run Slider SEO/media backfill for all Products while preserving every `homepage_slider_enabled` checkbox.
3. Prefer existing saved content packs; do not spend a new AI request when authoritative generated Slider content already exists.
4. For genuinely missing content, use the single configured Product AI authority and keep technical facts fail-closed.
5. Recount all 635 Products and require Slider core completeness or an explicit blocked reason per Product.
6. Verify real Qt samples including #620/#625/#628.
7. Re-verify Filament operator flows: new Filament appears immediately, selected/all Site sync, all-active reconciliation, bulk edit selected/all for price/rates/preheat/time/temperature, and exact-family default selection.
8. Preserve owner defaults and 1kg stock policy where already established; do not reinitialize accepted Catalog facts blindly.
9. Re-run Stage-3 image workspace acceptance: 3x3, usable scroll, multi-select edit/delete, filenames, screenshot, SEO fix/rename and exact `ارسال سایت` membership.
10. Audit public Site acquisition surfaces against the owner contract: no customer-facing direct marketplace/source acquisition workflow; only approved back-office source ingestion and the existing material/USD data jobs remain where intended.
11. Fresh backup then one controlled same-identity Product republish from the unified runtime; verify complete field/media/Profile/Variant/Slider replacement and unchanged Product identity.

Exit gate:
- Slider completeness is real-data accepted;
- latest Windows UI/Filament/Image functionality is accepted from the unified SHA;
- one controlled re-publish proves the whole Windows snapshot contract.

### Phase50.A.2Z-S — Social Go-Live / Changed-Revision Automation
Status: **PLANNED**

Required operations:
- Site publish/public verification must succeed before Social begins.
- One Feed + companion Story per new/changed accepted revision, with duplicate guard.
- Use the exact public Site-selected media set, Primary first; preserve ALT/SEO metadata.
- Caption: factual Product copy, bounded relevant hashtags, tracked Product URL and nationwide-Iran shipping copy; never claim free printing/download unless factually true.
- Story: approved 1080x1920 Gold/Navy IRANSans presentation and Product-link notification/Link Sticker handoff.
- Auto-derive approved category Highlight target; official Buffer limitation means final Add-to-Highlight remains an operator Instagram UI action.
- Never repost protected existing receipts such as #625, #309 or #301 unless the Product revision/media authority genuinely changes.
- Audit/finalize profile logo and Highlight icon set already requested by owner.

### Phase50.A.2Z-W5 — Manual / Self-Produced Product
Status: **PLANNED**

First-class Product creation without a source marketplace:
- operator title/notes/media;
- normal Profile/Filament controls;
- optional source/reference link;
- AI may create Persian content/SEO from operator description + images;
- AI must not invent weight/time/dimensions/material/license;
- uses the same readiness, Site publish, media, Social and revision contracts.

### Phase50.A.2Z-W6 — Source Video + Reel
Status: **PLANNED**
- source video discovery/download with provenance;
- Product video presentation on Site;
- Social Reel/Story handoff through supported provider contracts;
- no private Instagram API or invented completion state.

### Phase50.A.2Z-C — Dynamic Shipping Provider Activation
Status: **PLANNED**
- retain current ShippingMethod/rate rules as fallback;
- verify current official Post/Tipax/Mahex contracts/credentials before adapter work;
- quote from selected Profile effective shipping weight + package facts + destination;
- freeze chosen quote/service in immutable order snapshot;
- browser/order UAT and finance reconciliation.

### Phase50.A.3 — Secure Store ZarinPal
Status: **IN_PROGRESS FOUNDATION / STORE WIRING PENDING**
- current ZarinPal v4 compatibility must be revalidated when this phase executes;
- keep the mature server-owned amount, Authority, callback identity, server-to-server verify and idempotency authority;
- connect canonical StorePayment checkout to that authority;
- Sandbox with legitimate Merchant ID first;
- payment audit + finance reconciliation + rollback-grade UAT;
- Live enable only after explicit owner approval and Production verification.

### Phase50.A.4 — Torob
Status: **PLANNED**
- current official Torob Product API contract must be verified at execution time;
- publish only real sellable Product/Profile price/availability/media;
- stable Product identity and update/delete behavior;
- no flattened fake Variant data;
- observability + retry/idempotency + Production acceptance.

### Phase50.B.1 — Authentication + Customer Account Closure
Status: **PLANNED / PRIOR BUG NOT CONFIRMED CLOSED**
- Production Google OAuth callback must finish a real authenticated session instead of returning to Login.
- Local username/email/password login must remain healthy.
- Customer profile/account/order/history surfaces must be audited end-to-end.
- New users remain non-admin/default-customer unless explicitly promoted.
- Add browser regression for login/logout/session persistence and protected customer pages.

### Phase50.B.2 — Product Engagement
Status: **PLANNED**
- Product Like;
- Save/Favorite;
- Comment;
- verified-buyer Review qualification;
- counters, moderation/Admin visibility and customer history;
- additive migration only after backup/rollback gate.

### Phase50.B.3 — Customer Telegram Bot + Mini App
Status: **PLANNED / OPERATOR NOTIFICATIONS EXIST BUT CUSTOMER BOT NOT ACCEPTED**
- distinguish existing operator Telegram alerts from the requested customer-facing Bot/Mini App;
- link Telegram identity to the same Site customer/account authority, never a parallel customer DB;
- expose safe account/order status, Product links and support handoff based on existing permissions;
- Mini App authentication/session must map to canonical customer identity and order visibility;
- secrets/webhook configuration remain outside Git and need rollback/audit gates;
- real Telegram UAT for login/link/order visibility/support, plus duplicate/replay/idempotency tests;
- Production enable only after B1 authentication/customer-account closure is accepted.

### Phase50.C.1 — Accounting Core
Status: **PLANNED**
- chart/accounts + balanced journal/ledger;
- bridge current Store/service/inventory/payment/production events into accounting without creating conflicting business authorities;
- immutable posted entries and audit trail.

### Phase50.C.2 — Treasury
Status: **PLANNED**
- bank/cash accounts;
- receipts/payments/transfers;
- payment reconciliation;
- treasury reports and controls.

### Phase50.C.3 — Purchasing / Payables
Status: **PLANNED**
- suppliers, purchase flow, AP, inventory/cost integration and supplier statements.

### Phase50.C.4 — Sales / Receivables
Status: **PLANNED**
- invoice/AR integration, customer statements, payment allocation, aging and profitability links.

### Phase50.C.5 — Reports / Close
Status: **PLANNED**
- management P&L/cash/inventory/product profitability;
- period close/reopen controls;
- reconciliation and audit reports.

### Phase50.D.1 — Final Windows Package + Full UAT / Release
Status: **PLANNED**
- full Windows repository tests;
- Qt/package/one-file release gate where still applicable;
- final Desktop shortcut;
- soak/resume/large-catalog performance;
- Store/Auth/Payment/Shipping/Social/Customer/Telegram/Admin end-to-end Production UAT;
- clean logs/console;
- rollback retention audit;
- final CURRENT_STATE/ROADMAP/CHANGELOG/ERRORS/REQUESTS closure.

## Historical roadmap rule
Older ROADMAP sections are retained as evidence. An unchecked historical item is **not** automatically a current task. It becomes current only if this master plan carries it forward or a fresh read-only audit proves the behavior still missing.

## Required status-report format from now on
Every development report must end with:
1. **Current phase + status**
2. **What was completed and verified**
3. **What remains in this phase**
4. **Exact next phase**
5. **Exact ordered operations for that next phase**
6. **Required tests/backup/deploy/Production verification gates**
7. **The phase immediately after that**, so the owner always sees the forward sequence.

## Exact next task
**Phase50.A.2Y — Lineage Convergence.**
No new feature work, no Catalog mutation and no Production deployment comes before the latest Windows `c86c66a1...` and Server/Production `e03bdd2b...` lineages are reconciled into one tested GitHub head.
