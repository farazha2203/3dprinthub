# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.24 — Runtime Observability + AvalAI URL Tools + Startup No-Network Guard`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.18 operator editing, 49.3I.19 canonical source identity, 49.3I.20 visible operator panels, 49.3I.21 bounded/link-grounded AI, 49.3I.22 Tk main-thread safety/scrollable rail and 49.3I.23 exact AvalAI Product adapter are present on the feature branch.

New owner evidence and the uploaded sanitized diagnostic exposed three additional release blockers before Local Publish:
- AvalAI Product generation aborted with `audit_event() got an unexpected keyword argument 'provider'`,
- application startup repeatedly triggered Provider `/models` calls before the operator requested them, including a wrong-provider key probe against OpenAI in some sessions,
- OpenRouter accepted `google/lyria-3-pro-preview` but returned non-JSON music output; HTTP success did not mean Product text capability.

The diagnostic also shows successful AvalAI generation can take roughly 18–52 seconds, and `grok-4.5` responses reported `num_sources_used=0`; therefore merely placing the MakerWorld URL in a normal chat prompt was not evidence that the page had been browsed.

## 49.3I.24 Implemented
### AvalAI request/runtime repair
- the invalid generic `audit_event(provider=..., model=...)` call is removed; Provider/Model now live in sanitized audit `detail`,
- Product-bound AvalAI keeps the exact saved Provider/Model and no hidden Product `/models`,
- structured output now prefers `json_schema`, falls back to `json_object`, then prompt-enforced JSON only when required,
- app-side exact-page fetch/sanitization remains the deterministic source of truth,
- when extracted source facts are sparse, supported AvalAI routes may add explicit URL evidence:
  - supported Gemini model families: Chat Completions `urlContext`,
  - GPT-5 family: Responses `web_search`,
  - unsupported/error tool routes fall back to app-fetched source facts without Provider/Model switching,
- obvious music/image/audio/embedding/moderation/video models are excluded from the Product model picker and rejected at structured generation boundary.

### Startup / performance observability
- final App shell records runtime lifecycle from constructor entry through close,
- rotating main log remains preserved,
- new runtime JSONL records constructor/first-idle/thread/unhandled/lag/close events,
- Tk heartbeat records recovered UI stalls,
- background watchdog writes all-thread `faulthandler` dumps when the UI heartbeat is stalled for an extended period,
- Provider model-list network calls during application construction are blocked until first Tk idle; explicit model search after first paint remains live,
- Dashboard now exposes Program Log, AI Log, log folder and a safe GitHub-ready diagnostic export,
- safe export appends redacted tails of runtime session log, main log and hang thread dump to the existing diagnostic JSON,
- AvalAI model rows are not labeled `رایگان` merely because generic pricing fields are zero/missing; only explicitly free-routed IDs are marked Free by the UI adapter.

## Root Cause / Performance Review
Observed high-value causes are now prioritized as:
1. hidden Provider model discovery during startup,
2. long external AI calls (18–52s observed),
3. prior Tk cross-thread callbacks (49.3I.22),
4. wrong/non-text model choice causing long useless calls,
5. repeated Product save/update groups as a secondary DB/UI cost to profile after the above blockers are removed.

The new hang dump is intentionally designed to identify any remaining synchronous UI/DB/image/refresh bottleneck instead of guessing.

## Publish SEO Audit — Preserved
Core Product publish SEO remains wired end-to-end: Persian title/content/image Alt, SEO title/description, focus keyword, OG title/description/image, canonical, robots, Product/ProductGroup + Offer + Breadcrumb + Review/FAQ JSON-LD, safe public slug/legacy redirect and `/sitemap.xml`.

Dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` remain optional social-preview enhancement debt, not the current release blocker.

## Database / Migration / Data Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- Local Catalog SQLite must NOT be copied/replaced into Production MySQL.
- no reset/drop/truncate
- no media/history deletion
- no API key/token committed
- Production untouched

## Test Status
49.3I.24 implementation and focused regression tests are committed to GitHub. No Windows execution result has been received yet, so the hotfix is not Local Tested or Accepted. No claim of CI/Local PASS is made.

## Exact Next Task — Windows 49.3I.24 Gate
1. close Catalog Center completely,
2. verify clean worktree at `D:\projects\3DPrintHub`,
3. fetch/prune and ff-only pull the live feature branch,
4. verify Local HEAD equals fetched Remote HEAD,
5. compile 49.3I.24/23 and inherited AI/Tk composition modules,
6. run focused 49.3I.24/23 plus inherited 49.3I.22/21/20/19/18 tests,
7. run `catalog_center\launch.py --verify-only`,
8. launch and verify Dashboard diagnostic card appears quickly,
9. verify startup performs no automatic Provider `/models` HTTP requests,
10. explicitly search models and verify post-first-idle model discovery still works,
11. open product 2896217 and run `تکمیل همه اطلاعات بر اساس لینک محصول`,
12. verify no `audit_event provider` failure, no hidden Product model scan and no non-text model route,
13. verify supported URL-tool evidence or explicit app-fetch fallback is visible in diagnostics,
14. if UI stalls, export the safe diagnostic and verify Thread dump/runtime tails are present,
15. close/reopen normally and verify lifecycle logs remain readable.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Store/Admin/Product/Media/SEO E2E including canonical/meta/OG/JSON-LD/sitemap,
- explicit owner approval,
- read-only Production project/branch/commit/venv/MySQL/backup/rollback verification,
- deploy only approved GitHub snapshot,
- Production HTTP/data/media/SEO verification.

## What Remains
- Windows 49.3I.24 automated + startup/hang + live AvalAI gate,
- one Local Publish E2E,
- owner acceptance,
- Production verification/deploy only after those pass.
