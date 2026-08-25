# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.24 — Runtime Observability + AvalAI URL Tools + Startup No-Network Guard`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA NEXT`
Production: `UNTOUCHED / NOT APPROVED`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → COMMIT/PUSH IF LOCAL CODE CHANGES → LOCAL PUBLISH E2E → OWNER APPROVAL → PRODUCTION BACKUP/DEPLOY/VERIFY`

## Immediate Business Priority
1. Windows acceptance of 49.3I.24 startup/no-network/hang diagnostics,
2. live AvalAI completion for MakerWorld product 2896217 with exact saved model and explicit URL evidence/fallback,
3. verify Product text-model capability guard and no false all-models-free UI,
4. regression 49.3I.22 UI responsiveness and 49.3I.21 bounded job/cancel path,
5. exactly one Local Publish E2E,
6. Local Store/Admin/Product/Media/SEO verification including canonical/meta/OG/JSON-LD/sitemap,
7. explicit owner approval,
8. read-only Production branch/path/venv/MySQL/backup/rollback verification,
9. deploy approved GitHub snapshot and verify Production,
10. then Store ZarinPal integration + Sandbox E2E.

## Phase49.3I Path
`Discovery Review → PS5.1 Guard → Gallery/AI First-Paint → Live Git Snapshot → Explorer/Routing → Selection Guard → Credential Persistence → Provider/Preview Recovery → Observable AI → SEO/Source → AI Trace → Provider Schema → Exact-Page UI/Image Fit → Paste/Batch Recovery → Mature Scan Restoration → Bulk Exact-Page Images/Add-to-Products → Resilient Acquisition → Single Active AI Runtime → Operator Editing/Bulk Metadata → Canonical Source Identity → Visible Operator Panels → Observable Link-Grounded AI → Tk Main-Thread AI Bridge + Scrollable Rail → AvalAI Exact Chat Contract → Runtime Observability + Explicit URL Tools + Startup No-Network Guard`.

## 49.3I.24
Owner diagnostic proved:
- AvalAI path could abort in diagnostics before HTTP because `audit_event` was called with unsupported Provider/Model kwargs,
- startup still generated hidden multi-provider `/models` traffic,
- successful Provider HTTP did not guarantee a Product-text-capable model (`Lyria` case),
- URL-in-chat did not mean page browsing (`num_sources_used=0` observed),
- successful AvalAI calls can legitimately take tens of seconds and need lifecycle/hang visibility.

Implemented:
- repair audit call contract,
- exact saved AvalAI model; no hidden Product `/models`,
- structured output `json_schema` first with bounded compatibility fallbacks,
- deterministic app-side source extraction plus explicit supported AvalAI URL tools when facts are sparse,
- Product non-text model filtering/guard,
- block hidden startup model-list network until first Tk idle,
- runtime lifecycle JSONL + UI heartbeat + all-thread hang dump,
- Dashboard Program/AI logs + safe GitHub-ready diagnostic bundle,
- remove misleading generic AvalAI `رایگان` labeling when pricing metadata is insufficient.

## Publish SEO Audit
Current release has the core SEO path: Persian content/image Alt import, meta title/description, focus keyword, OG, canonical, robots, Product/ProductGroup + Offer + Breadcrumb + Review/FAQ JSON-LD, safe public slug/legacy redirect and public `/sitemap.xml`. Dedicated Twitter title/description/image and `og:image:alt` are enhancement debt, not a blocker for the Catalog release gate.

## Database / Migration
Django migration: NONE. Catalog schema migration: NONE. Local SQLite is not copied into Production MySQL. Production untouched.

## Focused Windows Gate
Clean/ff-only pull live feature branch → compile 49.3I.24/23/composition → run 49.3I.24/23 plus inherited 49.3I.22/21/20/19/18 tests → `launch.py --verify-only` → launch → confirm Dashboard logs and no startup `/models` traffic → explicit model search still works → run link completion on MakerWorld 2896217 → verify explicit AvalAI URL tool or app-fetch fallback, `json_schema` request, no audit signature failure/no Product model scan → if UI stalls inspect safe hang-thread export. If PASS, exactly one Local Publish E2E and complete Local SEO/media/store verification.
