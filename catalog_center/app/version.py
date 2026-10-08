from __future__ import annotations

from pathlib import Path


APP_NAME = "3DPrintHub Catalog Center"
APP_VERSION = "8.9.11"
BUILD_ID = "2026.10.04.2"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"
SOURCE_ROOT = Path(__file__).resolve().parents[1]

# Operator-visible release notes. Keep this tuple authoritative for the Qt
# About dialog so the active build explains both completed and pending work.
RELEASE_HISTORY = (
    {
        "date": "2026-10-04",
        "build": "2026.10.04.2",
        "status": "GALLERY IMAGE IDENTITY FIX / SCREENSHOT CAPTURE PRESERVED / 32 TARGETED TESTS PASS / QT VERIFYONLY PASS / VISIBLE UI PENDING",
        "done": "Root cause fixed across the media path: a legacy fixed-name MakerWorld acquisition screenshot was promoted/SEO-renamed as a Product image, then current_local_items rebuilt it from raw DB identities after gallery filtering; Feed also read raw media. That legacy acquisition evidence is excluded from the card/publish identity. The explicit operator Product Screenshot capture flow is preserved unchanged and timestamped operator screenshots remain visible/usable. Finalization does not silently rewrite canonical identities or delete files. Regression covers legacy renamed acquisition screenshot, exact card/delete/reopen byte identity, Site/Feed parity, preserved operator screenshot behavior, and all 20 real Product images.",
        "not_done": "The 32 current targeted tests protecting gallery identity, 20-image display/reopen and the existing operator screenshot flow pass, along with compileall, diff-check and Qt VerifyOnly on a fresh disposable empty Catalog. Read-only canonical Product #964 parity also passes: one visible image, one Site image and one Feed image resolve to identical source identity and SHA. Foreground Desktop acceptance remains pending because Computer Use exposes no targetable native app. No Product/media files were changed. No commit/push, Instagram send, Host, Production or deploy action occurred.",
        "next": "Obtain a targetable visible Desktop session for Build 2026.10.04.2 and run the operator select/delete/reopen check on a disposable Catalog without sending. Then review preserved W5 work before any exact-SHA GitHub gate.",
    },
    {
        "date": "2026-10-03",
        "build": "2026.10.03.2",
        "status": "GALLERY URL-TO-BYTES IDENTITY FIX / 44 RELATED TESTS PASS / QT VERIFYONLY PASS / VISUAL GATE OPEN",
        "done": "Gallery cards now come only from persisted Product image identities and resolve to the exact final local bytes used for publishing. Unreferenced numbered cache files are no longer appended as selectable local:// cards when exact URL mappings exist; same-Product persisted local-display aliases still resolve to their exact local file. Isolated regression proves card URL/path parity, one-image deletion and reload. Gallery/media tests: 33/33 and image recovery tests: 11/11 PASS; Qt VerifyOnly PASS.",
        "not_done": "Visible in-app selection/delete/reopen acceptance remains pending. Computer Use returns no native apps/windows. A disposable Temp Catalog used during candidate startup differs logically from the registered backup (Product #1075 image fields and Product #862 stage state); that copy is preserved for audit and is no longer an acceptance baseline. Canonical Catalog, Host, Production, Instagram, commit and push were not intentionally changed.",
        "next": "Use an observable foreground window with a fresh explicitly isolated Catalog to inspect actual card bytes, select/delete one image and reopen. Then finish W5C/Desktop and review preserved WIP before any GitHub gate.",
    },
    {
        "date": "2026-10-03",
        "build": "2026.10.03.1",
        "status": "GALLERY IDENTITY / 66 RELATED TESTS / QT VERIFYONLY PASS / VISUAL UI GATE OPEN",
        "done": "Product image cards now prefer the exact persisted Product URL-to-final-file mapping rather than pairing numbered downloader cache files by list position. Gallery loading retains all mapped Product images beyond five and keeps unmapped local files visibly local-only. Delete removes only the exact selected identity; a same-basename image or a local-display alias from another source/Product is not treated as a match. Legacy numbered-file fallback remains only where no exact URL mapping exists. Related gallery/media regression: 66/66 PASS; isolated Qt VerifyOnly PASS.",
        "not_done": "Visible isolated gallery card/select/delete/reopen acceptance is not confirmed: the candidate window could not be brought to the foreground clear of an unrelated terminal. Canonical Catalog, Host, Production, Instagram publishing, commit and push were not changed or performed. W5C/Desktop acceptance remains open.",
        "next": "Run visible isolated gallery smoke on this exact source Build and disposable Catalog copy: verify image bytes/count, select/delete only one candidate image, close/reopen. Do not touch the canonical Catalog or send to Instagram.",
    },
    {
        "date": "2026-09-30",
        "build": "2026.09.30.4",
        "status": "W5C STORY AUTO SEND RESTORED / EXPLICIT RESEND ENABLED / FOCUSED LOCAL TESTED",
        "done": "AI Popup Story explicitly selects the existing automatic Story route, overriding a saved manual Sticker preference only for this action; it does not require Buffer mobile notification. Removed the permanent same-Product/same-image receipt lock: each explicit send after the previous operation completes creates a new Buffer publication. Concurrent UI operation guard and provider-side ambiguous-outcome reconciliation remain. Link Sticker handoff stays a separate optional mode.",
        "not_done": "Focused Story/Post/Buffer/UI regression passed 40 tests (one imported helper deselected); compileall, diff-check, isolated VerifyOnly and Catalog/backup quick/integrity checks passed. Read-only comparison attributes the isolated Catalog SHA delta to four product_history rows for Product #862 (one product_viewed and three story_preview_generated); product rows, AI revisions and sync receipts are unchanged. No canonical Catalog write occurred. No real Story/Post was sent. Foreground popup acceptance and W5C/Desktop/GitHub gates remain open; candidate is uncommitted on base SHA 46497ccad3219300aea05a830c625086d79f789b.",
        "next": "Inspect Build .4 Popup in the visible isolated Desktop without sending. Then finish W5C gates and only afterward commit/push exact SHA. For a clickable native Link Sticker, use the separate explicit Buffer notification/manual Instagram flow; automatic Story itself remains available without it.",
    },
    {
        "date": "2026-09-30",
        "build": "2026.09.30.3",
        "status": "W5C STORY DELIVERY TRUTH / LINK STICKER HANDOFF / LOCAL TESTED",
        "done": "Fixed Story idempotency so a prior Story receipt for the same Site acknowledgement cannot suppress a different approved creative; exact same asset/strategy/tracking URL remains a no-op. 'Already sent' is no longer counted as a fresh publish. Link Sticker Stories now use Buffer notification handoff and remain pending until Instagram completion is reconciled with Buffer markedAsPublished plus an external link. Added a no-repost Buffer result reconciliation action. Focused Story/Post/Buffer regression 53 passed (one imported helper deselected); compileall, diff-check, isolated Qt VerifyOnly and clone/backup integrity checks pass.",
        "not_done": "Read-only Buffer readiness found no active member device. Therefore no Instagram Story or Link Sticker was sent or verified live. Computer Use exposed no native windows; visual Popup acceptance is pending. This is an uncommitted local candidate on base SHA 46497ccad3219300aea05a830c625086d79f789b; no push/deploy or canonical Catalog write occurred.",
        "next": "Connect an active Buffer mobile device, verify notification readiness, then visually inspect the isolated Desktop Popup. Only after separate action-time approval, send one controlled notification, finish Instagram Sticker → Link → exact Product URL → Share manually, and reconcile its provider receipt. Complete W5C visual/Desktop and GitHub exact-SHA gates afterward.",
    },
    {
        "date": "2026-09-30",
        "build": "2026.09.30.2",
        "status": "W5C AI STORY/POST SEND HANDOFF / LOCAL TESTING",
        "done": "AI Story and Post tabs now expose a send action for the exact AI revision only after approval and send preparation. It routes through the existing readiness, preflight and explicit confirmation flow. Buffer queued/sending is reported separately from provider-confirmed sent. Focused Popup/Instagram/Buffer regression 50/50 and isolated Qt VerifyOnly pass; isolated Catalog backup integrity checks pass.",
        "not_done": "This Computer Use session exposed no native apps/windows, so visual verification of the launched isolated build and popup remains pending. No real Instagram send, Host operation, Production change, commit or push was performed.",
        "next": "Obtain a targetable foreground desktop session and visually verify Build 2026.09.30.2 plus Popup send controls on the isolated Catalog. Keep final Send untouched; W5C/Desktop acceptance remains open.",
    },
    {
        "date": "2026-09-30",
        "build": "2026.09.30.1",
        "status": "W5C IMAGE AI / LOCAL TESTED / STORY BRAND CAMPAIGN",
        "done": "Story styles 1/2/3/6 have distinct premium brand-campaign art directions while favorite styles 4 (lifestyle) and 5 (controlled surreal) are preserved. Real generation includes the official logo and exact Persian Product copy/approved discount alongside the Product reference; Provider is pinned. Pricing distinguishes output and input units and ranks estimated total with two references. Focused social regression 44/44 PASS; live discovery found Seedream 5 Lite at about $0.035/image as the lowest compatible fixed-price endpoint after reference costs.",
        "not_done": "No paid generation has been run on the isolated Catalog, so visual quality and Persian glyph rendering remain unverified. Final Popup close/reopen, VerifyOnly and W5C/Desktop acceptance are pending. No Instagram send, Host or Production operation is enabled.",
        "next": "Refresh and save the endpoint only in the isolated Catalog, verify the estimated $0.035/image rate, then await approval before one generation. Verify SQLite BLOB, preview, reopen and idempotency.",
    },
    {
        "date": "2026-09-29",
        "build": "2026.09.29.2",
        "status": "W5C IMAGE AI UI WIRING / LOCAL TESTED PENDING REAL GENERATION",
        "done": "Connected the Story/Post Generate action to the independent OpenRouter Image API adapter. The selected style now supplies its English prompt direction and 9:16/4:5 ratio; the real reference MIME is preserved; returned bytes are saved as an unapproved SQLite BLOB with provider/cost/usage and request-fingerprint metadata. Identical requests reuse the saved revision. Mock preview is explicitly separate.",
        "not_done": "The old discovery code incorrectly treated the zero-cost input_image line as the output cost; this was corrected in Build 2026.09.29.3. Real one-image generation on the isolated acceptance Catalog, final popup close/reopen, VerifyOnly and regression closure remain pending. No Instagram send, Host or Production operation is enabled.",
        "next": "See current image-generation gate and isolated Catalog acceptance status in the latest About history entry.",
    },
    {
        "date": "2026-09-29",
        "build": "2026.09.29.1",
        "status": "W5C REGRESSION HOTFIX / LOCAL_TESTED / GITHUB GATE PENDING",
        "done": "Fixed the installed exact-saved-model wrapper to accept and forward explicit model_info during provider discovery/connection tests. Product execution still requires its saved model and never performs hidden model listing. The captured 971-test manifest identified 14 baseline error events also present on parent 00fd4d96 and one v84 interaction regression; 37 ordered provider/Avalai/Story/Post tests now pass after the fix.",
        "not_done": "The captured pre-fix full suite had 12 baseline-proven failures and 14 baseline error events plus the fixed v84 regression. The older 16-error count is not reproduced by the captured run. W5C/Desktop acceptance, Instagram send, Host and Production work remain incomplete/disabled.",
        "next": "Commit/push this locally tested candidate and verify its exact GitHub SHA. Final Desktop acceptance follows; do not send to Instagram or deploy.",
    },
    {
        "date": "2026-09-28",
        "build": "2026.09.28.1",
        "status": "W5 IMAGE AI / LOCAL_TESTED / ISOLATED GENERATION",
        "done": "OpenRouter image discovery found 59 reference-capable endpoints; Seedream 4.5 was selected at recorded cost 0. One isolated Product generation returned a 1,373,903-byte PNG, stored as a SQLite BLOB, and the same request fingerprint reused the same revision. Approved/selected revision handoff is connected to the existing Story/Post preparation path.",
        "not_done": "No canonical Catalog write, Instagram send, Host operation or Production deployment occurred. The isolated renderer smoke exposed a stale Product media URL fixture and was not retried unchanged.",
        "next": "Reconcile canonical-vs-backup SQLite byte provenance, baseline-proof the remaining full-suite failures, run isolated foreground smoke and final backup verification, then decide commit/push. Real sending remains disabled.",
    },
    {
        "date": "2026-09-27",
        "build": "2026.09.27 (exact ID not recorded)",
        "status": "W6 ACCEPTED / LOCAL + GITHUB",
        "done": "W6D passed Qt VerifyOnly, isolated foreground smoke, Video/Media/Social/Product regression, compileall and diff-check. Integrity backup passed quick_check/integrity_check; W6 range contains no Server/Host files.",
        "not_done": "No Host deploy, Production verification, Buffer API call, Reel publish or canonical Catalog mutation was performed.",
        "next": "Proceed to the next planned project phase after owner direction; W6 Source Video/Reel is closed locally and on GitHub.",
    },
    {
        "date": "2026-09-27",
        "build": "2026.09.27 (exact ID not recorded)",
        "status": "W6C / LOCAL_TESTED / HANDOFF_ONLY",
        "done": "Reel Preview is review-only; public HTTPS video, product URL, caption, AI disclosure and thumbnail offset are shown. Handoff is fail-closed until explicit operator approval and produces a Buffer draft/approval payload with Instagram type=reel.",
        "not_done": "No Buffer API call, Reel creation, Instagram publish, canonical Catalog write, Host or Production change was performed.",
        "next": "Run W6D full video/media/Social regression, compileall, diff-check, Qt VerifyOnly and isolated foreground smoke.",
    },
    {
        "date": "2026-09-27",
        "build": "2026.09.27 (exact ID not recorded)",
        "status": "W6B / LOCAL_TESTED / ISOLATED",
        "done": "Site video acceptance enforces bounded 512-byte–80MB media and binary MIME/extension agreement, copies Product-owned videos with checksum verification, and verifies public URL plus HTML video embedding in an isolated fixture.",
        "not_done": "No canonical Catalog write, real Site upload, Host/Production change, Reel handoff or Social publish was performed.",
        "next": "Run full W6 regression, compileall, diff-check, Qt VerifyOnly and isolated foreground smoke, then close the W6D GitHub gate.",
    },
    {
        "date": "2026-09-27",
        "build": "2026.09.27 (exact ID not recorded)",
        "status": "ACCEPTED / LOCAL_ONLY",
        "done": "Phase D is accepted locally: isolated Qt VerifyOnly/UI smoke passed, identity/media regression 19/19, Crawl/Acquisition regression 52/52, and the read-only duplicate audit found zero authoritative duplicate groups. S1 Story Preview remains locally tested.",
        "not_done": "No canonical Product/Catalog cleanup, duplicate merge, provider publish, Torob submission or Production SEO change was performed. Operator Link Sticker confirmation is not automated; Phase D related regression, Phase E/F, S1 AI/provider wiring, Google SEO audit, Torob discovery, W5 and W6 remain.",
        "next": "Run isolated foreground Qt VerifyOnly/UI smoke for the Story tab and real-photo previews; then continue Phase D related regression and the read-only duplicate audit.",
    },
    {
        "date": "2026-09-27",
        "build": "8.9.11 / 2026.09.20.1",
        "status": "BASELINE",
        "done": "W5 manual-product foundation remains preserved on the active checkout; no reset, stash, or deletion was used.",
        "not_done": "W5 acceptance and W6 source video/reel work are intentionally waiting behind Crawl/Dedupe/Staging recovery.",
        "next": "Return to W5 after phases A–F are accepted, then continue W6.",
    },
)


def version_lines() -> tuple[str, ...]:
    return (
        f"APP_VERSION={APP_VERSION}",
        f"BUILD_ID={BUILD_ID}",
        f"SOURCE_ROOT={SOURCE_ROOT}",
        f"MAIN_FILE={SOURCE_ROOT / 'app' / 'main.py'}",
    )


if __name__ == "__main__":
    print("\n".join(version_lines()))
