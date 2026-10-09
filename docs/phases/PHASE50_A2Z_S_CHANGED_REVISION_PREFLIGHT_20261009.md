# Phase50.A2Z-S — Changed-Revision Social Go-Live Read-Only Preflight

Date: 2026-10-09
Status: IN_PROGRESS / READONLY_PROVIDER_VERIFIED / EXTERNAL_ACTION_BLOCKED

## Source of truth and protection
- Verified unified Local=GitHub `merge/phase50-a2z-a2u-lineage-20261009` at `b29c09700e7f518d341f2f5ab38628816ca335f8`; this branch has no configured git tracking upstream, so explicit `git ls-remote origin refs/heads/merge/...` was used instead. Clean before audit.
- Real active owner Windows checkout `D:\projects\3DPrintHub-a2z-a2r-converge` branch `wip/phase50-a2z-w5-manual-product-20260927`, Local=GitHub clean `2946a6cb34827bcb0c6d5f9cea0f724692a9a58a`. Desktop shortcut points to its existing RUN_QT.ps1; not changed.
- Production Host via dedicated 3DPrintHub-only bridge read-only: clean `0277018726cf02e565ba83eb724cfbf8acc523fb` on `release/phase50-a2j-hero-20260915`. No Host deployment in this audit.
- Canonical SQLite `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` opened strictly as URI `mode=ro`; 1076 Products, no data mutation. Protected full rollback `D:\projects\3dprinthub-backups\phase50-a2r-social-identity-20261009\catalog-before-a2r-social.sqlite3` must remain untouched (1,222,283,264 bytes; SHA256 c87fb9cc64d74d93760d5191b6b172a9a419ce3059c01425b197346bf033f6bd).
- Requested Delta: evidence-backed inventory and live provider status verification for next Social wave; MUST NOT send Feed/Story/Reel, mutate original Catalog/Product media, modify owner desktop launcher or deploy Host.

## Live Buffer Instagram evidence (only GraphQL queries, no mutations)
- Configured saved Buffer channel ID matches across 5 inspected receipt candidates. Authenticated channel query PASS, service=Instagram, not disconnected or locked.
- Current `hasActiveMemberDevice=false`. This ONLY blocks optional `native_sticker_notification`/manual clickable Link Sticker flow; actual DB key `instagram_story_link_mode` is unset, and the current code defaults to historically accepted `bio_shop_grid` automatic Story. `instagram_companion_story_enabled=1`, `buffer_media_host=github_raw`. Never conflate provider `metadata.instagram.link` with proven native Instagram Link Sticker; mobile is needed for notification handoff.
- Historical provider `sent` with external link present: Product #536 Feed and Story from Site rev1; Product #309 Feed and Story rev2; Product #301 Feed rev2; Product #625 Feed and Story rev8 (current Site revision13); Product #609 Feed rev2 (current Site revision3). Query is read-only `_POST_STATE_QUERY` by saved provider post IDs; not merely bounded recent-post list.
- #609 historical `instagram_story_notification_ready` receipt from rev2 has **live Buffer provider status `error` and no external link**. It was not an actual Story publication (previously documented ERR-49-220). Do not blindly retry; native mobile handoff needs device and explicit owner approval.
- Product #536 persisted commercial_status=review but `source_license_owner_approved=1`, `approved_for_sale=1`, `is_blocked=0`: under current code it passes the owner-approved license override. `review` alone must not be reported as forbidden. Site Product #48 current revision2, historical Feed and Story receipts only rev1. Never repost rev1; changed-revision send remains owner decision.
- Actual #536 Site Product URL GET 200 text/html, owned public motion media GET 200 image/gif, Content-Length=12,778,636 bytes. Local GIF SHA256 `6f980225578d6afc94375ffc53848ca95440119f060f97f84dd3b2702fb056c6`, 720x960 px, 65 frames, 6500ms. This is valid Site motion media, **not** an Instagram-compatible MP4/MOV Reel. No ffmpeg/ffprobe executable on current PATH; do not fabricate a Reel or transcode original media in this read-only phase.

## Complete current-Catalog Social inventory
Computed on all 1076 Products using positive Site ACK Product/revision and current production `canonical_site_payload`+selected media authority, and semantic `same_site_revision` for local receipts:
- 48 Products have a positive Site Product/revision and `public_http_ok`. All 48 meet existing licensed or explicit owner-approved and sales-unblocked criteria. This is not a blanket approval to send.
- 45/48 have a valid selected public Social image/ALT preview.
- Among those 45: 35 have a recorded Feed submitted/published for exactly the **current Site revision**; 4 have a historical Feed for a different revision but no current-revision receipt; 6 have no Feed receipt at all. 20 have a recorded same-revision Story receipt. Treat all these as audit counts, not real external Instagram publication proofs: current-revision local receipt can be 'submitted', and Story states may be provider error until checked.
- Exactly three current Site ACK Products fail mandatory exact selected-image media parity (no safe auto-send):
  - **#273** Site Product35 rev1: selected three SEO filenames but 4 public owner-slug image basenames have inserted suffixes; first selected image `matches=0`. Public checks also include unrelated-Product URLs. Requires verified canonical local-vs-Site selected-media reconciliation, not fuzzy name matching.
  - **#303** Site Product24 rev1: selected image1 `twistmas-tree-3d-print-01.webp` matches **two different public URLs**; current resolver correctly refuses `matches=2`. Requires independent immutable URL/image SHA and canonical ownership proof before reconciling, not arbitrary first match.
  - **#965** Site Product78 rev1: public check list includes six URLs from several products; first selected filename matches, but the second selected image is not retained by current conservative owner-slug filter (selected2 `matches=0`). Must confirm exact public image ownership/ACK rather than widen filter to unrelated media.
- Site/Instagram product media truth is intentionally fail-closed. No Product re-import, photo deletion/relabeling, Site revision or original ACK edit. Any repair needs scoped backup of Catalog and Site, test/commit GitHub, controlled same-identity Product refresh and independent current public byte/SHA verification. Do not send until exact selected images are proven.

## Tests and gates
- Existing unified-source test suites (no writes to canonical DB): Buffer 34/34, Direct Instagram 29/29, social provider receipt reconciliation 3/3, social readiness controls 9/9, W6 Reel format guard 7/7 = **82 distinct PASS**.
- Provider responses for historical post IDs were read-only `BufferPostState` queries. No createPost, Site publish, Story, Reel, Provider mutation, mobile login or Production changes.
- W5C remains `NATIVE_QT_AUTOMATED_VISUAL_VERIFIED / OWNER_FOREGROUND_UAT_PENDING`, notwithstanding earlier 2/2 native Qt and real Product #1074 acceptance tests. Must not mark W5C owner-accepted without owner confirmation.

## Remaining and exact next phase operations
1. Owner manually confirms W5C gallery selection/scroll/reopen on familiar daily Desktop Product without deleting or sending; capture actual signoff or defect.
2. A2Z-S scope: choose the exact candidate Product/revision. Read-only revalidate current Site ACK, images/ALT, commercial approval override, Feed/Story receipt and exact Buffer post state; three parity errors must be repaired individually with isolated test/source and Catalog+Host rollback verified.
3. For native Link Sticker, connect Buffer mobile account and enable notifications, confirm `hasActiveMemberDevice=true` and a test notification in owner UI; default `bio_shop_grid` automatic mode is distinct and does not prove a clickable Story sticker.
4. For Reel, obtain/produce true H.264 MP4/MOV, independent MIME/codec/duration/aspect/size and public HTTPS file verification (Product #536 GIF alone insufficient). No video transport or live provider claim yet.
5. Only after exact candidate operator approval and clean provider/media gates, backup the current Catalog, run local/Qt and status checks, issue **one deliberate idempotent send** and verify final live Buffer/Instagram receipt and external link. Host code deploy only if a verified Server delta exists, with account-quota headroom and full MySQL/source/env rollback from GitHub.
6. Next owner-selected master phase: A2Z-C Dynamic Shipping or A3 Secure Checkout (both separate architecture and controlled Production release gates). Do not silently start or complete them.

**This checkpoint only reports readiness. No external publication authorization has been inferred.**
