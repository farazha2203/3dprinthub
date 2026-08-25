# PROJECT ROADMAP

Updated: 2026-08-25
Repository: `farazha2203/3dprinthub`
Active Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current Epic: `Phase49 — Unified Product / Slider / Catalog Sync`
Current Phase: `49.3I`
Current Hotfix: `49.3I.29 — Structured Web Product Presentation`
Status: `PRODUCTION VERIFIED / FIRST NEW CATALOG PRODUCT PUBLISH NEXT`
Production Application Commit: `d27489f1c2e1d36e75fdadfa8ab24660d8bec720`

## Permanent Delivery Order
`READ DOCS → VERIFY STATE → CHECK ERRORS → IMPLEMENT ON GITHUB → WINDOWS PULL --FF-ONLY → LOCAL TEST → LOCAL PUBLISH/WEB E2E → OWNER APPROVAL → READ-ONLY HOST VERIFY → BACKUP → DEPLOY FROM GITHUB → PRODUCTION VERIFY → DOCUMENT`

## Completed Release Gate
- Local Web QA approved by owner.
- Production Host verified on MySQL `sfkilvrs_EmiAdmin_3dprinthub`.
- MySQL backup created before migrations.
- Approved GitHub application commit deployed.
- `store.0030..0033` and `website.0020..0023` migrated successfully.
- Post-migration plan is empty.
- `collectstatic` and Passenger restart completed.
- Home, Store and one public Product returned HTTP 200.
- Public Product sanitization passed: no raw Catalog Intelligence or internal AI/source-hash fields.
- Production worktree is clean after verified removal of four historical untracked host-only artifacts.

## Immediate Priority
1. Publish one newly prepared Product from Catalog Center using the official Site Publish/Bridge path.
2. Verify Product row/update, main image/gallery ownership, Persian content and structured Product facts on Production.
3. Verify canonical/meta/OG/schema/image Alt/source attribution.
4. Verify re-publish/update is idempotent and does not duplicate media/Product identity.
5. If this passes, mark Phase49.3I accepted.
6. Then proceed to the requested Store online payment phase (ZarinPal), preserving bank transfer.

## 49.3I.29 Acceptance Contract
- no public template renders raw `technical_notes`,
- only allowlisted customer facts are shown,
- internal AI/audit/runtime fields are not public,
- missing source placeholders are hidden,
- public web rendering performs no AI request,
- existing pricing/cart/media/SEO/source URL behavior is preserved.

## Production Warning Debt
- CKEditor4 warning remains open.
- In-memory realtime `store.W026` remains open for a later Redis/polling architecture phase.
- MySQL conditional unique-constraint warnings are known and non-blocking for this release.

## Next Release Gate
`Catalog Site Publish → Production Product/Media/SEO E2E → owner acceptance → Phase49.3I ACCEPTED → Store payment phase`.
