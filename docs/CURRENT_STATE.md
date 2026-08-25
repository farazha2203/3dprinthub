# CURRENT PROJECT STATE

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Base Epic: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.23 — AvalAI Exact Chat Contract + Publish SEO Audit`
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
49.3I.18 operator editing, 49.3I.19 canonical source identity, 49.3I.20 visible operator panels, 49.3I.21 bounded/link-grounded AI and 49.3I.22 Tk main-thread safety/scrollable rail are present on the feature branch.

Fresh owner evidence after 49.3I.22 shows the Workspace/scroll layout is usable, but `تکمیل همه اطلاعات بر اساس لینک محصول` still does not reliably produce the requested result although the same link works when used directly with AvalAI. The sample product has canonical source title `Ribbed cake stand, cookie platter` while the old Persian title remains a generic MakerWorld model-number title.

Repository inspection found a request-construction defect in the generic non-OpenAI structured path: normal Product AI re-entered model discovery, serialized Responses-style content wrappers into a chat string, and asked for schema-conforming JSON without actually including the schema. 49.3I.23 adds an AvalAI-only Product adapter that uses the exact saved model and a real Chat Completions `model + messages` contract with the actual JSON schema embedded in the system instruction.

## 49.3I.23 Implemented
- `phase49_3i23_avalai_chat_contract.py` applies only to product-bound AvalAI structured requests.
- exact saved AvalAI model is used; no hidden `/models` request before Product generation.
- source/operator text is sent as clear chat text rather than serializing Responses API wrapper objects.
- output JSON schema is included in the system message.
- `input_image` placeholder objects are not serialized into the AvalAI chat prompt.
- `response_format=json_object` is attempted first; unsupported-parameter fallback uses the same exact model/prompt without it.
- existing 49.3I.21 timeout/diagnostics and 49.3I.22 main-thread UI handoff remain in force.
- sanitized audit event `avalai_exact_chat_contract` records contract metadata only; no key/full prompt.
- focused regression test added for no model scan, exact model, schema presence, link/source grounding and compatibility fallback.

## Publish SEO Audit
Core Product publish SEO is already wired end-to-end in the repository:
- Catalog Persian title/content/image Alt fields are imported into Store data/media.
- SEO title/description map to Product meta fields.
- focus keyword, OG title/description, source attribution and hashtags are synchronized.
- Product detail emits canonical, robots, OG product metadata and image.
- Product/ProductGroup, Offer, Breadcrumb, Review and FAQ JSON-LD paths exist.
- `/sitemap.xml` is the public Django sitemap for products/categories/services/static pages.
- safe public slug and legacy redirect contract exists.

Non-blocking social-preview enhancement debt: dedicated `twitter:title`, `twitter:description`, `twitter:image` and `og:image:alt` are not emitted yet. `twitter:card` and core OG metadata already exist. This is not a blocker for the current Catalog publish gate.

## Database / Migration / Data Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- Local Catalog SQLite must NOT be copied/replaced into Production MySQL.
- Product data moves through the existing publish/bridge/import contract, not DB-file transfer.
- no reset/drop/truncate
- no media/history deletion
- no API key/token committed
- Production untouched

## Test Status
49.3I.23 code and focused regression tests are committed to GitHub. Windows execution has not yet been reported, therefore 49.3I.23 is not Local Tested or Accepted.

## Exact Next Task — Windows 49.3I.23 Gate
1. close Catalog Center,
2. verify clean worktree at `D:\projects\3DPrintHub`,
3. fetch/prune and ff-only pull the live feature branch,
4. verify Local HEAD equals fetched Remote HEAD,
5. compile 49.3I.23 + touched composition/49.3I.22/21 modules,
6. run focused 49.3I.23 test plus inherited 49.3I.22/21/20/19/18 tests,
7. run `catalog_center\launch.py --verify-only`,
8. open product 2896217 and run link-grounded full refresh,
9. verify Diagnostics shows `avalai_exact_chat_contract` then AvalAI structured chat request and no Product `/models` preflight,
10. verify received preview has real identity/non-generic Persian title and apply only after approval,
11. if failure remains, export sanitized diagnostics before closing the app.

## Release Gate After Windows PASS
- exactly one `LOCAL PUBLISH ONLY`,
- Local Store/Admin/Product/Media/SEO E2E including canonical/meta/OG/JSON-LD/sitemap,
- explicit owner approval,
- read-only Production project/branch/commit/venv/MySQL/backup/rollback verification,
- deploy only approved GitHub snapshot,
- Production HTTP/data/media/SEO verification.

## What Remains
- Windows 49.3I.23 automated + live AvalAI gate,
- one Local Publish E2E,
- owner acceptance,
- Production verification/deploy only after those pass.
