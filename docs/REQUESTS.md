# OWNER REQUESTS

Last Updated: 2026-08-22

## Active — Phase49.3H

### REQ-49H-001 — Unified SEO execution visibility
Status: APPROVED / IN_PROGRESS
Request:
- every SEO-related button/action must visibly show what it is doing step by step
- show connection state, data preparation/send, response, validation, applied changes and final result
- success: progress window may close, but a result panel/drawer must remain available under the related section and log must be recorded
- error: result/error panel remains visible with sanitized error/log information and retry/open-log guidance

### REQ-49H-002 — Per-product AI/SEO cost
Status: APPROVED / IN_PROGRESS
Request:
- record cost spent editing/SEOing each product
- show cost before/at publish as an internal operational receipt
- use real provider cost when available; never invent unsupported cost

### REQ-49H-003 — Controlled image intake
Status: APPROVED / IN_PROGRESS
Request:
- operator determines max images per product during scan/intake
- examples: 10 or 20; do not fetch 100 images
- when limit is reached, continue to next product
- cap must apply to actual persisted/selected product images, not only downloaded files

## Preserved Requests From Prior Phases
- Workspace stages must remain accessible; incomplete task is guided, not trapped.
- AI provider/model selectable and persistent with connection test.
- Image SEO operates only on selected product images and sends no image bytes/files/URLs to AI.
- AI tasks/provenance must indicate what AI filled and allow operator manual override/disable.
- Dynamic/fixed pricing must remain intact.
- Source refresh must preserve human edits.
- Production cannot be touched before Local approval.

## Change Rule
A new request does not authorize unrelated redesign. Implement the approved delta with minimal changes and preserve mature behavior unless the owner explicitly requests removal/replacement.
