# Phase50.A2Z-W6 — Source Video + Reel

Status: `ACCEPTED / W6D_GITHUB_UPDATED`
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

## W6D final acceptance checkpoint — 2026-09-27

Status: `ACCEPTED` in Build `2026.09.27.22`.

- Qt `RUN_QT.ps1 -VerifyOnly`: PASS (`QT6_FOUNDATION_VERIFY=OK`,
  `QT6_42B2_FULL_PARITY_VERIFY=OK`, operator launcher PASS).
- Isolated foreground MainWindow smoke: PASS; Routes=6, Actions=11,
  WizardStages=7, using the integrity backup rather than the canonical DB.
- Video/Media/Social/Product regression: `49/49 PASS`; prior W6C combined
  regression: `55/55 PASS`.
- compileall and `git diff --check`: PASS.
- Backup `D:\projects\3dprinthub-backups\phase50-w6d-20260927-202858`:
  quick_check=ok, integrity_check=ok, Products=1076, SHA256
  `9a64e4ed834e9f98940f481649ca7e464371847cda7ea7d2c58ffa9f8d41e60c`.
- W6 range contains only Catalog/tests/docs. No Server/Host file was changed
  by W6; no Host deploy, Production mutation, provider API call or Reel
  publish occurred.

W6 is closed. The next phase is selected from the master roadmap by owner
direction; no deployment gate is pending for this Windows/Catalog-only delta.

## 2026-10-09 — Actual W5 Desktop carried accepted W6 format correction
Original W6D historical acceptance on 2026-09-27 covered local/source/Site motion-video and review-only Reel draft, not a real Reel publication. The unified branch corrected a genuine issue where GIF Site media was treated as Reel-compatible. The verified **daily owner Desktop launcher source** `D:\projects\3DPrintHub-a2z-a2r-converge` on branch `wip/phase50-a2z-w5-manual-product-20260927` now has exactly the same corrected Buffer source blob as tested unified GitHub `fd50b441`: Reel `prepare_reel_preview` and `build_reel_handoff_input` fail-closed for GIF/WebM/M4V, require valid HTTPS MP4/MOV, signed query URL supported; unrelated Story/Post controls untouched. 7 new + 34 Buffer/Story + 29 Instagram + 12 Site Video + 14 Media + 5 Revision cases = 101/101 PASS on actual owner-source checkout, py_compile and Qt VerifyOnly PASS. No live video conversion, Buffer draft/submission, Story/Post, DB/media or Host mutation. Current #536 stays review/Site rev2/GIF. Source-level guard affects new launches; no claim about old in-memory processes or packaged EXEs. Owner W5C UAT pending, and any real Reel release still requires separate provider/media/owner authorization gates.
