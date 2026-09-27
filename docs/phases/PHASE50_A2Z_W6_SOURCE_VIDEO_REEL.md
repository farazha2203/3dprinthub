# Phase50.A2Z-W6 — Source Video + Reel

Status: `IN_PROGRESS / W6C_LOCAL_TESTED`
Date: 2026-09-27  
Branch: `wip/phase50-a2z-w5-manual-product-20260927`  
Start commit: `48b7bfd123c1c537e78f73a654292211318423fd`

## Scope

W6 extends the existing canonical motion-media authority:

- `video_links_json` — discovered Source links with provenance;
- `selected_video_links_json` — operator-selected Source links;
- `local_video_files_json` — bounded local files with safe ownership/checksum;
- Site Product video presentation and public verification;
- supported Social Reel/Story handoff only after provider capability is
  verified.

No private Instagram API, guessed provider capability, fake clickable state, or
automatic Reel completion claim is allowed.

## Baseline evidence

- Source video extraction/serialization, MakerWorld animated GIF discovery,
  same-domain bounded download, local persistence, Site copy/checksum and public
  video verification: `16/16 PASS` across the existing video/reacquire/crawl
  suites.
- Current Product Wizard already exposes Source/local video truth in Stage 3.
- Buffer Feed/Story remains image-based; Reel/video Social delivery is not yet
  claimed complete.
- No Catalog, Provider, Host or Production mutation occurred in this W6 start.

## Ordered microphases

### W6A — Source video truth and operator review

Trace Source discovery → selected link → bounded local download → checksum →
Product/Wizard preview. Add explicit status/reason for missing, blocked,
unsupported, duplicate or failed video without changing Product identity.

### W6B — Site video acceptance

Verify Product-owned video copy, MIME/size limits, public URL, HTML embedding,
canonical Product identity and rollback on an isolated Catalog/site fixture.

### W6C — Reel handoff contract

Research and verify the supported provider's current Reel contract. Build
Preview → operator approval → handoff status; keep image Story/Post contracts
unchanged. Do not send real media before explicit approval.

### W6D — Full acceptance / GitHub gate

Run video/media/Product/Social regression, compileall, diff-check, Qt VerifyOnly,
isolated foreground smoke, integrity backup, source/server delta audit, then
commit/push and verify Local=Remote. Host deploy is conditional on a verified
Server delta and explicit release gate.

## Immediate next task

Implement W6A review/status visibility on an isolated Catalog, then add focused
tests for idempotent video selection, duplicate URL handling, MIME/size failure
reasons and no accidental Reel/Post/Story publish.

## W6A implementation checkpoint — 2026-09-27

Status: `LOCAL_TESTED` in Build `2026.09.27.19`.

- Source video candidates are normalized and deduped by canonical URL before
  download/selection.
- Product Wizard Stage 3 now exposes an operator-checkable Source video list
  backed by `selected_video_links_json`.
- Repeated selection is idempotent and does not create duplicate identities.
- Cross-domain, unsupported-extension and download-failure reasons are
  classified before a file is accepted; bounded download remains unchanged.
- Video/reacquire/crawl regression: `18/18 PASS`.
- No Reel, Post or Story publish and no canonical Catalog/Host/Production
  mutation occurred.

Next exact phase: W6B isolated Site video acceptance, including MIME/size,
public URL, HTML embedding and rollback verification.

## W6B implementation checkpoint — 2026-09-27

Status: `LOCAL_TESTED` in Build `2026.09.27.20`.

- Site copy retains the Product-owned `videos/` root and rejects path escape,
  unsupported suffixes, files below 512 bytes or above 80MB.
- Binary signatures must agree with the declared media type: GIF magic for
  `.gif`, `ftyp` for MP4/M4V/MOV, and EBML for WebM.
- Destination size and SHA256 are verified after copy.
- Isolated public verification covers the declared public URL and actual
  `<video><source>` HTML embedding while keeping image checks separate.
- Focused W6 video suite: `11/11 PASS`, including MIME mismatch and undersize
  rejection.
- No real Site/Host/Production, Reel, Post or Story mutation occurred.

Exact next phase: W6C Reel handoff contract research and Preview → operator
approval → handoff status, with image Story/Post contracts unchanged.

## W6C implementation checkpoint — 2026-09-27

Status: `LOCAL_TESTED` in Build `2026.09.27.21`.

- Official Buffer contract was checked: video assets use a publicly accessible
  URL; Instagram metadata supports `type=reel`; video thumbnail selection uses
  a frame offset and custom video thumbnail images are not used.
- `prepare_reel_preview` is review-only and requires a public HTTPS video URL.
- `build_reel_handoff_input` fails closed until explicit operator approval and
  emits a draft/approval payload only; it does not call Buffer.
- Focused Buffer/Social suite: `17/17 PASS`.
- No Buffer API call, Instagram publish, Catalog, Host or Production mutation.

Exact next phase: W6D full video/media/Social regression, compileall,
diff-check, Qt VerifyOnly, isolated foreground smoke, integrity backup and
GitHub gate.
