# PHASE50.A.2P — Buffer Provider-Compatible Media Host + Receipt Reconciliation

Status: LOCAL_TESTED / REAL ACCEPTANCE PASS / GITHUB UPDATE NEXT
Date: 2026-09-19

## Goal
Make the successful Product -> Site -> Instagram path repeatable for future Products. Canonical Product media stays owned by 3DPrintHub; Buffer receives only provider-compatible social derivatives through a media host it can actually fetch.

## Real acceptance evidence
Product #625 / Site Product #39 revision 8 is the accepted reference.
- Site Product identity preserved at #39.
- Product #39 has exactly 3 active CC-P39 Variants, 0 active legacy Variants and 2 current ProductImages.
- Feed Buffer post id: 6aaed28f6e039ccbc8221fa8.
- Feed status reconciled to sent without repost; public Instagram link: https://www.instagram.com/p/DdepEh3if0N/
- Story Buffer post id: 6aaed29a7fcdd8931977c3f1.
- Story status sent; public Instagram link: https://www.instagram.com/stories/3dprinthub_ir/3989806967019651799
- Story style: 3dprinthub_instagram_gold_navy_v2_iransans, 1080x1920.
- Highlight target: اسباب بازی; final Highlight placement remains operator_required because Buffer exposes no Highlight mutation.

## ERR-49-183 boundary
The Buffer-only PNG derivatives hosted on 3dprinthub.ir were valid owner-side HTTP 200 image/png with stable Content-Length/cache headers, but Buffer rejected both as unreadable. The same bytes mirrored to raw.githubusercontent.com were accepted immediately and both Feed + Story reached sent. The current site origin is fronted by BitNinja-WafPro/Caddy, but the exact remote blocking rule is not proven without provider/origin request logs. Treat this as a Buffer-to-origin reachability/media-host compatibility boundary, not a Product media, SEO, format or Buffer-auth failure.

## Runtime design
- New buffer_media_host setting: github_raw (verified default) or site.
- github_raw mirrors only generated social PNG derivatives into the dedicated social-assets-buffer Git branch/worktree.
- Canonical Product WebP media and SEO filenames remain untouched.
- Every social asset mirror is deterministic per Site ACK revision and carries source URL + SHA256 manifest evidence.
- Dedicated worktree must be clean and on the exact social-assets-buffer branch; unrelated changes fail closed.
- GitHub branch head must match the pushed remote head before returned URLs are accepted.
- Every provider URL is HTTP image-verified before Buffer submission.
- Feed receipt records provider media host/branch/commit while retaining canonical Site source_media_urls.
- Submitted -> sent reconciliation is read-only against Buffer and appends final receipt evidence without creating another post.

## Local/real gates
- Fresh Catalog rollback before A2P runtime data changes: pre-a2p-social-host-runtime-20260919-220004; integrity OK.
- Real automated rehost path PASS; current media branch head 6561dc3e2709ccc2d2651d576d1e744b35058891.
- Real Feed receipt reconciled to instagram_published without repost.
- Social focused + broader regression 31/31 PASS.
- Python compile, `git diff --check` and Qt VerifyOnly PASS.
- No Site schema/migration change.

## Next gate
Commit/push exact Windows A2P candidate -> verify live GitHub SHA -> relaunch exact tested Qt runtime. Do not create another #625 Feed/Story for revision 8. Then proceed to remaining Phase50 finance/payment/admin closure and bounded Product publication.
