# Phase50.A.2K — Tympanus Slicebox + Filament UX

Date: 2026-09-17
Status: `LOCAL + RELEASE ACCEPTED / PRODUCTION BLOCKED BY 3DPRINTHUB TUNNEL`

## Owner scope
- Destroy the previous homepage Hero/Slider runtime and replace the whole box, background, controls and transition engine with the real Tympanus/Codrops Slicebox reference.
- Remove the redundant public Product filament gallery and keep the four-step order wizard.
- Add Select All / Clear All to Product/Profile filament selection in Windows Catalog Center.
- Make central Filament edit from Product/Profile load registered Brand/Material/Color lists.
- Surface material description, applications and sample parts in Windows and the Store order wizard.

## Accepted implementation
- Canonical feature commit: `71d34daae1571b4f46f05def91c86b1dcde173a6`.
- Production-based release: `release/phase50-a2k-tympanus-20260917 @ 84d1a87c4ea632823743b9cc1c5fe3ba81b08843`.
- Rollback source ref: `backup/pre-phase50-a2k-tympanus-filament-20260917`.
- Exact official Slicebox `jquery.slicebox.js` v1.1.0 is vendored; official/vendor SHA-256 is `246DA4F1AFD789CC1AEA2F410AE4CCCD321DDFD40485376C1406046EFFE7A92D`.
- A2I/A2J public Hero CSS/JS and Hero-only deploy runners are deleted from the active source tree.
## Local/release acceptance
- Modified Django Hero/Store suites: `50/50 PASS` on the Production-based release worktree.
- Windows Catalog filament/finalization suite: `18/18 PASS` with canonical `catalog_center` PYTHONPATH.
- `manage.py check`: PASS apart from existing CKEditor warning.
- `makemigrations --check --dry-run`: no changes.
- Canonical local `migrate --plan`: no planned operations.
- Qt launcher/foundation verification: PASS and modern Qt window relaunched after implementation.
- Store remains intentionally empty; no Product was republished by this phase.

## Destructive Hero-data contract
`phase50_a2k_reset_hero` is dry-run by default. Apply requires `--confirm RESET_HOMEPAGE_HERO`, deletes every existing `HomepageHeroSlide` row in one transaction and creates exactly four fresh safe source-backed slides for assets 119, 120, 135 and 136. Production execution requires a new verified MySQL + Hero rollback backup first.

## Production blocker
The approved loopback `127.0.0.1:22024` is currently unavailable. Windows `sshd` is Running/Automatic and port 22 is listening. OpenSSH evidence shows the last successful `PrintHubTunnel` authentication was 2026-09-15 from Host source `89.39.208.237` with the expected fingerprint; there have been no new `PrintHubTunnel` attempts after the 2026-09-17 sshd restart. Other project tunnels authenticate, so do not restart sshd or alter shared tunnel users. Production deploy remains blocked until the dedicated 3DPrintHub Host watchdog/tunnel is restored and authenticated health passes.

## Exact next step
Restore the repository-owned 3DPrintHub watchdog/forward, verify Host identity + clean `release/phase50-a2j-hero-20260915 @ 12e319ace1eb55c114d7117e1b5a2fa170b410ab`, verify real MySQL migration plan/readiness, take fresh rollback backups, fetch exact A2K release from GitHub, deploy, apply the confirmed Hero reset, collectstatic/restart, then verify public A2K DOM/static assets and absence of A2J runtime.
