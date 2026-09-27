from __future__ import annotations

from pathlib import Path


APP_NAME = "3DPrintHub Catalog Center"
APP_VERSION = "8.9.11"
BUILD_ID = "2026.09.27.22"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"
SOURCE_ROOT = Path(__file__).resolve().parents[1]

# Operator-visible release notes. Keep this tuple authoritative for the Qt
# About dialog so the active build explains both completed and pending work.
RELEASE_HISTORY = (
    {
        "date": "2026-09-27",
        "build": BUILD_ID,
        "status": "W6 ACCEPTED / LOCAL + GITHUB",
        "done": "W6D passed Qt VerifyOnly, isolated foreground smoke, Video/Media/Social/Product regression, compileall and diff-check. Integrity backup passed quick_check/integrity_check; W6 range contains no Server/Host files.",
        "not_done": "No Host deploy, Production verification, Buffer API call, Reel publish or canonical Catalog mutation was performed.",
        "next": "Proceed to the next planned project phase after owner direction; W6 Source Video/Reel is closed locally and on GitHub.",
    },
    {
        "date": "2026-09-27",
        "build": BUILD_ID,
        "status": "W6C / LOCAL_TESTED / HANDOFF_ONLY",
        "done": "Reel Preview is review-only; public HTTPS video, product URL, caption, AI disclosure and thumbnail offset are shown. Handoff is fail-closed until explicit operator approval and produces a Buffer draft/approval payload with Instagram type=reel.",
        "not_done": "No Buffer API call, Reel creation, Instagram publish, canonical Catalog write, Host or Production change was performed.",
        "next": "Run W6D full video/media/Social regression, compileall, diff-check, Qt VerifyOnly and isolated foreground smoke.",
    },
    {
        "date": "2026-09-27",
        "build": BUILD_ID,
        "status": "W6B / LOCAL_TESTED / ISOLATED",
        "done": "Site video acceptance enforces bounded 512-byte–80MB media and binary MIME/extension agreement, copies Product-owned videos with checksum verification, and verifies public URL plus HTML video embedding in an isolated fixture.",
        "not_done": "No canonical Catalog write, real Site upload, Host/Production change, Reel handoff or Social publish was performed.",
        "next": "Run full W6 regression, compileall, diff-check, Qt VerifyOnly and isolated foreground smoke, then close the W6D GitHub gate.",
    },
    {
        "date": "2026-09-27",
        "build": BUILD_ID,
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
