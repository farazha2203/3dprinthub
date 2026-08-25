# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.23 — AvalAI Exact Chat Contract + Publish SEO Audit`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → COMMIT/PUSH IF LOCAL CODE CHANGES → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. Windows acceptance of 49.3I.23 exact AvalAI request contract on product 2896217,
2. verify no Product `/models` preflight and correct non-generic Persian content preview/apply,
3. regression 49.3I.22 UI responsiveness/scroll rail and 49.3I.21 diagnostics/link grounding,
4. exactly one Local Publish E2E,
5. Local Store/Admin/Product/Media/SEO verification including canonical/meta/OG/JSON-LD/sitemap,
6. explicit owner approval,
7. read-only Production branch/path/venv/MySQL/backup/rollback verification,
8. deploy approved GitHub snapshot and verify Production,
9. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition → Single Active AI Runtime → Operator Editing/Bulk Metadata → Canonical Source Identity → Visible Operator Panels → Observable Link-Grounded AI → Tk Main-Thread AI Bridge + Scrollable Rail → AvalAI Exact Chat Contract + Publish SEO Audit`.

## 49.3I.23
Verified defect: Product-bound AvalAI structured generation still passed through generic model discovery and serialized Responses-style content wrappers as chat text; the prompt also did not include the actual required JSON schema.

Implemented:
- exact saved AvalAI model; no hidden Product `/models`,
- documented Chat Completions `model + messages` request through existing transport,
- real source/operator text payload rather than wrapper serialization,
- actual JSON schema included in the system instruction,
- no fake image placeholder serialization,
- same-model compatibility fallback for unsupported `response_format`,
- sanitized request-contract trace,
- focused regression test.

## Publish SEO Audit
Current release has the core SEO path: Persian content/image Alt import, meta title/description, focus keyword, OG, canonical, robots, Product/ProductGroup + Offer + Breadcrumb + Review/FAQ JSON-LD, safe public slug/legacy redirect and public `/sitemap.xml`. Dedicated Twitter title/description/image and `og:image:alt` are enhancement debt, not a blocker for the Catalog release gate.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Local SQLite is not copied into Production MySQL. Production untouched.

## Focused Windows Gate
Clean/ff-only pull live feature branch → compile 49.3I.23/composition → run 49.3I.23 plus inherited 49.3I.22/21/20/19/18 tests → `launch.py --verify-only` → run link completion on MakerWorld 2896217 → verify `avalai_exact_chat_contract` and no Product model scan → verify correct preview/apply. If PASS, exactly one Local Publish E2E and complete Local SEO/media/store verification.
