# Phase50.A.2Z-W5 — Social SEO + Commerce Discovery

Status: IN_PROGRESS / GITHUB_UPDATED (isolated real generation + SQLite BLOB + guarded Story/Post handoff; foreground Desktop acceptance pending)
Date: 2026-09-27
Branch: `wip/phase50-a2z-w5-manual-product-20260927`

## W5C regression classification — 2026-09-29

- One complete pre-fix full-suite manifest is retained outside the repository; sanitized event/test inventory and SHA256 are recorded in `PHASE50_A2Z_W5C_REGRESSION_EVIDENCE_20260929.md`.
- Captured result: 971 tests, 12 failures, 15 error events. All 12 failures are already parent-proven; the exact 14 legacy error events also reproduced on parent `00fd4d9600b4fddbfcbee1439c2e45ab02589e3b`.
- The remaining current-only event was `test_avalai_connection_falls_back_to_chat_completions`: the installed Phase49.3I.29 `choose_model` wrapper rejected explicit `model_info`. The wrapper now forwards explicit model info for non-Product discovery; Product-scoped saved-model and no-hidden-listing behavior remains intact.
- Ordered provider/Avalai/Story/Post regression after the patch: 37/37 PASS; Python compile and diff-check PASS. No full-suite rerun after the surgical change.
- The earlier recorded 16-error count is not reproduced in the full captured run; its unobserved extra event is not guessed. All events in the captured manifest are classified.
- Isolated Qt VerifyOnly passed on a disposable clone of the integrity-checked existing backup: `QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK`; clone SQLite checks passed before/after and the clone/artifacts were removed. Canonical Catalog was untouched.
- Final diff/source review, ordered 37-test regression, compileall, diff-check, isolated Qt VerifyOnly and backup-integrity review all pass. W5C source commit `83945715bbe50fb2588fc01abb68be363f308fe5` is pushed and exact Local=GitHub verified. W5C/Desktop is not ACCEPTED: full-suite baseline debt remains and final foreground acceptance is pending a targetable native Qt screenshot/window-control session. Earlier Popup smoke passed on isolated Catalog. Instagram send, Host/Production and deploy remain disabled.

Exact next: foreground Desktop acceptance on the exact GitHub SHA using isolated Catalog; available Remote Desktop Commander exposes process/file operations only. Following phase: close W5C/Desktop acceptance; real Instagram send remains separately gated.

## S1 implementation checkpoint — Build 2026.09.27.12

Status: `LOCAL_TESTED` (foreground Qt smoke pending).

- Added a dedicated Qt Story tab with four implementable template choices: Classic Gold/Navy Hero, Technical Blueprint, Editorial Classic, and Premium Conversion.
- Preview rendering is local-only and uses the selected Product's real media and canonical URL; no invented AI image is substituted.
- Added operator controls for actual-photo use, exact discount approval, and explicit `@handle` Mention validation.
- Template selection is included in the deterministic local revision key so previews cannot silently reuse another layout.
- Approval remains separate from generation; automatic publish stays unavailable until Preview approval and manual Sticker/Mention confirmation.
- Verified: Python compile and Social/Persian tests `12/12`; no Catalog/Host/Production/provider mutation.

Next gate: isolated writable Catalog + foreground Qt VerifyOnly/UI smoke, then Phase D related regression and read-only duplicate audit. No deploy before commit/push and exact-SHA release gate.

## Verification evidence — 2026-09-27

- Isolated writable Catalog Qt VerifyOnly: `QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK`.
- Direct UI smoke: ProductsPage contains `گالری`, `جدول قابل مرتب‌سازی`, and `Story — چهار Preview`.
- Phase D identity/media regression: `19/19 PASS`.
- Crawl/Acquisition regression: `52/52 PASS`.
- Canonical read-only audit: `quick_check=ok`, Products `1076`, Source+External ID duplicate groups `0`, normalized URL duplicate groups `0`, fingerprint duplicate groups `0`, valid nonzero server-linked duplicate groups `0`.
- No Catalog write, provider mutation, Host operation, Production deployment, or Instagram send occurred.

## AI revision popup gate — 2026-09-28

### Real isolated Image AI generation checkpoint — Build 2026.09.28.1

- OpenRouter discovery returned 59 reference-capable endpoints. Selected `bytedance-seed/seedream-4.5` / provider `seed` with recorded cost `0`.
- Product 609 local reference generation succeeded: PNG `1,373,903` bytes, stored in isolated SQLite revision `#5`.
- No-invention prompt and request-fingerprint idempotency passed; the repeated request reused the same revision.
- Explicit approval + selection is now the only route that materializes a SQLite revision for the existing Story/Post preparation boundary.
- Direct renderer smoke initially stopped on a strict stale local-media URL fixture; the selected-revision path now bypasses that obsolete resolver while the legacy renderer remains unchanged. No provider send was touched.
- Focused Social/Video/Media/Product regression passed `119/119`; compileall, diff-check and Qt VerifyOnly passed. The full 971-test suite is not accepted: `14 failures / 15 errors` remain from baseline teardown/resource and unrelated stale assertions.
- Baseline update: the rerun of the full suite is `12 failures / 16 errors`; all 12 failures reproduce unchanged on parent `00fd4d96`, and the selected legacy error group reproduces there as well. The count changed because the verbose rerun exposed the exact current discovery manifest; this does not alter the Social/AI focused gate.
- Popup/Design automated smoke remains `10/10 PASS`. Native Qt foreground Popup smoke is now verified on 2026-09-29 using Remote Desktop Commander against the writable isolated clone: open, load/render saved SQLite Revision #4, close, reopen, and reload the same image; six Story and six Post style RadioButtons verified. The earlier Computer Use limitation is obsolete. This closes the Popup smoke only, not W5C/Desktop acceptance.
- Canonical Catalog `quick_check=ok` and `integrity_check=ok`; the byte SHA differs from the pre-generation backup, but read-only hashes/counts for all 23 user tables, page count and freelist are identical. This is recorded as SQLite physical-byte/checkpoint variance, not a proven logical data delta.
- Next ordered gates: classify the two remaining full-suite errors individually against current and parent manifests without repeating the unchanged full command → run only changed-condition probes → final W5C evidence review and exact-SHA/local=remote gate. Popup smoke and isolated backup integrity gates are complete. Real Instagram send and deploy remain disabled.

### Prior popup gate

### Independent Image AI adapter checkpoint — 2026-09-28

- Added reference-capable OpenRouter image endpoint discovery and a separate Image Model setting; Text AI model selection is not used for image generation.
- Added a pure reference-image generation adapter and stable request fingerprinting. Generated bytes are persisted as SQLite BLOB revisions and reused on repeated requests.
- Focused adapter/popup tests passed `9/9`; compileall and diff-check passed.
- Real generation is intentionally pending: canonical read-only settings has no saved `social_image_model`, and the exact runtime credential read is `Not configured`. No provider request, canonical Catalog write, Instagram send, Host or Production change occurred.
- Next gate: save/verify Image Model and secure key in active v8.9.11 runtime → one isolated generation → BLOB/no-invention/idempotency acceptance → approved revision handoff to existing Story/Post route → commit/push.

### Prior popup gate

- Added SQLite-backed `social_ai_revisions` BLOB storage and approval/selected-for-publish state.
- Isolated Popup smoke passed `40/40`: six Story styles, six Post styles, image render, save, approve, prepare-for-send, close and reopen.
- Related Video/Media/Social/Product regression passed `83/83`; compileall, isolated Qt VerifyOnly and diff-check passed.
- Canonical backup: `D:\projects\3dprinthub-backups\phase50-social-ai-sqlite-20260928-01\catalog-before-social-ai.sqlite3`, `quick_check=ok`, Products=1076, SHA256 `B58DB7716E8D810CF9A6CFAC48F74ECDF88797BCC7D639D7BC5864A1E2613B77`.
- OpenRouter discovery was fail-closed because the existing secure secret boundary reports `Not configured`; no key, model request, generation or publish occurred.

Exact next gate: save/verify an ordinary OpenRouter API key in the active v8.9.11 runtime, run discovery-only, record the cheapest compatible endpoint and cost, then perform a separately approved isolated generation test. HTTP 401 `User not found` is now explicitly classified as credential rejection. The current send path remains unchanged and real publication is blocked.

S1 is locally tested. The next gate belongs to Phase D evidence closure and then Phase E: generate a read-only duplicate report with authoritative survivor scoring, receipt/history/media preservation checks, and a verified rollback plan. Destructive merge remains explicitly blocked until owner acceptance.

## Scope

Define and implement a verified content/distribution contract for Instagram
Post and Story, then audit Google ecommerce SEO and discover the official Torob
merchant-feed/onboarding contract. This phase is downstream of the current
Crawl/Dedupe/Staging work and must not bypass Product readiness or Site
identity.

## Verified research findings

- A canonical Product URL in a Story asset or caption is not by itself an
  interactive link. The operator/provider route must prove a real Instagram
  Link Sticker or another Meta-supported clickable-link capability.
- The current project already preserves the canonical public Product URL in the
  Buffer Story metadata route. This remains useful attribution/fallback data,
  but the UI must distinguish `clickable_link_confirmed` from
  `canonical_url_attached` and must not claim a clickable sticker when it was
  not confirmed.
- Instagram API publishing requires a Professional account; current Meta
  documentation distinguishes Business/Creator access and has separate Story
  limitations. No live publish or token change is authorized by this phase.
- Google recommends Product/Offer structured data on purchasable product pages,
  canonical product URLs, valid price/availability, and sitemap submission.
  Product variants require stable variant/product-group identities. JSON-LD
  should be present in initial HTML where feasible, not only injected late by
  JavaScript.
- No authoritative public Torob feed/API contract was found in the allowed web
  search. Torob connection is therefore discovery-only until the owner provides
  or authorizes access to the actual merchant panel/feed contract.

## Implementation slices

### S1 — Social content contract

- Create a deterministic AI content pack for Post and Story with separate
  fields: hook, factual product benefit, technical specifications, use case,
  CTA, hashtags, alt text, canonical URL, UTM/referrer metadata, and prohibited
  claims.
- Generate from authoritative Product fields only; AI must not invent weight,
  material, dimensions, availability, pricing, license or performance.
- Keep human review/edit/approve before publish and store prompt/model/content
  revision evidence in the existing history/receipt path.

S1 foundation is implemented locally in `app/social_content_policy.py` as
`build_ai_social_pack`. It returns separate Post and Story payloads, reviewed
Product-fact provenance, technical facts, alt text, canonical URL, CTA and an
explicit `clickable_link_confirmed` / `manual_handoff_required` state. Direct
Persian content tests pass `6/6`. UI preview/review wiring and provider dry-run
remain; no real publish occurred.

The Qt Products page now exposes `🧷 آماده‌سازی Story دستی`. For selected
Products it renders the local Story asset with `publish_to_site=False`, copies
the exact canonical Product URL to the operator Clipboard, and shows the
suggested Sticker label `مشاهده و سفارش`. The UI reports image ready, URL ready,
manual Sticker required and clickable confirmation pending. It does not call
Buffer, Instagram or FTP.

## Story generation style contract

This is now the default production design contract for future Story generation:

1. **Classic Gold/Navy Hero** — premium/decorative Products.
2. **Technical Blueprint** — technical, automotive and utility Products.
3. **Editorial Classic** — special, decorative and lifestyle Products.
4. **Premium Conversion** — sales-focused campaigns and clear CTA.

The selected template is determined from the Product category/use-case, while
the real Product image remains the visual subject. The renderer extracts a
bounded dominant-color palette from the Product media and harmonizes accents,
frame and CTA with it; it must not invent a different Product or claim an
unverified color/material. All templates remain 1080×1920, use the approved
IRANSans/brand typography, keep copy minimal, and reserve the native Instagram
Link Sticker safe area.

### Approved variants

- **Normal Story:** Product name, one short factual promotional line, CTA,
  canonical URL and manual Link Sticker handoff.
- **Discount Story:** only when an operator-approved active discount exists;
  displays the exact percentage and validity window, never an AI-invented
  price/percentage. The discount must be consistent with the authoritative
  commerce data.
- **Mention Story:** accepts an operator-entered Instagram handle, validates
  the `@handle` shape, and prepares it for native Mention insertion. The
  handle is not treated as a clickable Product URL and is never inferred by AI.

Each variant must record template number, palette source, Product image
identity, discount approval state, mention handle, canonical URL and
`clickable_link_confirmed` separately. No provider publish is implied by asset
generation.

## AI generation cost and approval contract

- Story generation uses the lowest-cost configured AI model that passes the
  current quality gates for Persian text, structured output and image/style
  adherence. The app must choose from live provider/model metadata or an
  operator-approved cost table; it must not hard-code a vendor or invent a
  price.
- Use a two-step pipeline: low-cost structured copy/prompt planning first, then
  image generation only when the selected template requires a rendered asset.
  Reuse the same Product image and cached revision whenever inputs are
  unchanged so retries do not spend again.
- Prompts must include the exact Product identity, allowed factual fields,
  selected template, palette constraints, text limits, Link Sticker safe area,
  discount/mention fields and a strict prohibition on invented facts. AI output
  is a draft, not a publish authorization.
- Every Story must pass `Preview → operator approve/edit → manual Link Sticker
  and Mention/discount confirmation → send`. The send action is disabled until
  the Preview is explicitly approved. Rejected or edited previews remain
  traceable by revision and are never silently replaced.
- The Preview must show the final 1080×1920 asset, Product name, canonical URL,
  CTA, template number, palette source, discount text if any, Mention handle if
  any, and the exact manual Instagram steps. It must clearly show whether the
  link is merely prepared or clickable-confirmed.

### S2 — Clickable Story link gate

- Add provider capability/readiness fields separating canonical URL attachment,
  native Link Sticker requested, sticker confirmed, and manual handoff needed.
- Produce a mobile/native handoff package when the provider cannot prove a
  clickable sticker; include the exact canonical URL and suggested sticker
  label, without claiming automatic clickability.
- Add idempotent receipts and a post-publish verification checklist for URL,
  product identity and link-click metrics where the provider exposes them.

### S3 — Google technical SEO audit

- Read-only audit of product canonical tags, indexability, robots, sitemap,
  breadcrumb, Organization, Product/Offer, ProductGroup/variants, shipping,
  returns, image URLs and price/availability consistency.
- Implement only after the audit proves the exact Django templates/routes and
  current production boundary. Validate with Rich Results/URL Inspection on a
  small controlled sample before broader release.
- Add a Merchant Center feed only if the site/business eligibility and actual
  product data contract are verified.

### S4 — Torob discovery gate

- Identify the official merchant onboarding method, accepted feed format,
  required fields, update cadence, canonical URL rules and order/stock model
  from the real merchant panel or owner-provided official documentation.
- Build an isolated feed exporter and validator first. No submission, pricing,
  inventory, order or production mutation occurs in discovery.

## Required gates

1. Local contract/unit tests for AI content safety, factual-field provenance,
   URL identity and idempotent receipts.
2. Isolated Post/Story dry-run with no provider publish.
3. Isolated clickable-link capability test; manual fallback is a valid result.
4. Read-only Google SEO audit and structured-data validation on sample URLs.
5. Torob feed contract evidence before any connector implementation.
6. GitHub commit/push, then only if Server/static/template delta exists, Host
   compatibility and guarded deploy gates. No direct Production edits.

## Not allowed in this phase

- No real Instagram Post/Story publish.
- No token/secret disclosure or credential replacement.
- No Torob submission, order sync or inventory mutation.
- No Catalog canonical data cleanup.
- No Host/Production change before exact GitHub release gates.

## Sources

- https://developers.google.com/search/docs/appearance/structured-data/merchant-listing
- https://developers.google.com/search/docs/appearance/structured-data/product
- https://developers.google.com/search/docs/appearance/structured-data/product-variants
- https://developers.google.com/search/docs/specialty/ecommerce/share-your-product-data-with-google
- https://developers.google.com/search/docs/specialty/ecommerce/help-google-understand-your-ecommerce-site-structure
- Meta/Instagram platform documentation was checked for Content Publishing and
  Story capability boundaries; the project must treat provider-reported
  clickability as an acceptance fact, not infer it from an attached URL.
