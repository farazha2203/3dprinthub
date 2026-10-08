## 2026-10-04 Product screenshot/media identity audit

- Desktop source remains `D:\projects\3DPrintHub-a2z-a2r-converge`, branch `wip/phase50-a2z-w5-manual-product-20260927`, base SHA/upstream `46497ccad3219300aea05a830c625086d79f789b`; Build `v8.9.11 / 2026.10.04.1` is local/uncommitted.
- Canonical Catalog remains `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`; opened with SQLite `mode=ro` only, `quick_check=ok`. Product #964 local media root: `D:\projects\3dprinthub-catalog-manager\collected\makerworld\2724780`. No data or media bytes changed.
- The Product row's old screenshot path names `images\source-page-screenshot-20261003-113023.png`, while the evidence bytes are archived under `source_originals`; the renamed identity is excluded in code without deleting evidence or product files.
- No new backup was required because the Catalog/media files were strictly read-only. Any future migration/cleanup of the real row requires a fresh integrity-checked SQLite/filesystem rollback first.

## 2026-10-03 Gallery fix — verified paths and rollback (Build v8.9.11 / 2026.10.03.1)
- Source is the same forward checkout used by requested Build `2026.09.30.4`: `D:\projects\3DPrintHub-a2z-a2r-converge`; branch `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`. This is an uncommitted successor candidate; prior `.4` runtime was not changed.
- Canonical Catalog: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`; not opened/written by this work. Registered isolated acceptance Catalog: `D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01\catalog.sqlite3`; quick_check/integrity_check `ok`, SHA256 `8573A5C9676C2D199CF3ECFA0D424693C9C4074996B9AFD31C7A1885FD718EB1`.
- Fresh rollback generated via SQLite backup: `D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01\catalog.pre-gallery-build-2026-10-03.sqlite3`; quick_check/integrity_check `ok`, SHA256 `EA11741EE4D7C29483A0B9EF53E9BAD0DF0AE20E094FB50238B23E319339DBAA`, size 994095104 bytes.
- Qt VerifyOnly used disposable root `C:\Users\Emad-PC\AppData\Local\Temp\3dprinthub-gallery-verifyonly-20261003` created from that backup, with verified interpreter `D:\projects\3DPrintHub\.venv\Scripts\python.exe`, `PYTHONPATH=D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center`, `CATALOG_DATA_ROOT` set to the disposable root; results `QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK`. The root is about 1 GB, integrity remains `ok`, post-launch SHA256 `3290EB56226ACC2CB3136C8872B1D9489A5A24FC26A517D1728AAE158676838F`.
- The disposable Temp copy is still present: exact-path cleanup was attempted but the execution tool blocked the operation. Do not switch to another deletion technique. No registered clone/canonical DB cleanup was attempted. UI target activation was obstructed by an unrelated terminal; visual acceptance remains pending.

## 2026-09-30 W5C Build .4 — automatic Story resend correction
- Active local source: `D:\projects\3DPrintHub-a2z-a2r-converge`; branch `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`; Build `v8.9.11 / 2026.09.30.4` is uncommitted.
- Canonical Catalog remains `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3` and was not written. Acceptance Catalog and rollback backup remain in `D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01\`; both passed quick_check/integrity_check after VerifyOnly.
- Normal Story path restored to automatic Buffer; same-creative sends are allowed as new explicit operations. This build has not been visually launched/accepted because Computer Use returned no targetable Windows apps.
- No Host/Production action; no commit/push. Exact next: visible isolated Popup smoke, then W5C/Desktop acceptance and GitHub exact-SHA gate.

## 2026-09-30 W5C Build .3 — Story notification/link isolation
- Forward source: `D:\projects\3DPrintHub-a2z-a2r-converge`, branch `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`; `.3` is still an uncommitted candidate.
- Canonical Catalog (read-only / no acceptance writes): `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.
- Writable isolated acceptance Catalog: `D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01\catalog.sqlite3`.
- Isolated pre-VerifyOnly rollback: `D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01\catalog.pre-popup-send-build-2026-09-30.sqlite3`; SHA256 `5CC5D7BE95DA8FFCFFB28DAC7E06803E789F04ED299957DD2515DE9041B2E381`; backup integrity checked before/after.
- Qt runtime interpreter: `D:\projects\3DPrintHub\.venv\Scripts\python.exe`; launch from the forward source with `PYTHONPATH=D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center` and `CATALOG_DATA_ROOT=D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01`.
- Do not use `catalog_center\RUN_QT.ps1 -VerifyOnly` for isolated acceptance: this checked-in wrapper hardcodes the canonical Catalog data root. Invoke the verified interpreter and `qt_launch.py --verify-only` with the isolated environment override, as done for Build `.3`.
- Build `.3` was launched from this forward checkout with `PYTHONPATH` and `CATALOG_DATA_ROOT` set for the isolated Catalog; local PID `11152` was confirmed running. Post-launch clone integrity remained OK and its SHA256 unchanged.
- Read-only acceptance clone delta: four `product_history` rows for Product #862 (one `product_viewed`, three `story_preview_generated`); Product, AI revision and `sync_receipts` counts unchanged, no send receipt. Computer Use inventory returned no native apps/windows. Remote Desktop Commander can inspect device/processes but not show/capture/control the Qt window; visual acceptance is still pending.

## 2026-09-30 W5C image AI isolation
- Forward source: D:\projects\3DPrintHub-a2z-a2r-converge; verify branch and HEAD before each delivery.
- Canonical Catalog (never acceptance-write): D:\projects\3dprinthub-catalog-manager\catalog.sqlite3.
- Writable isolated acceptance Catalog: D:\projects\3dprinthub-backups\phase50-w5c-desktop-acceptance-20260929-01\catalog.sqlite3; last read-only quick_check/integrity_check OK. Separate prewrite backup is recorded in previous W5C checkpoints.
- Qt dependency interpreter: D:\projects\3DPrintHub\.venv\Scripts\python.exe and pythonw.exe; launch forward repo source with PYTHONPATH=repo\catalog_center and CATALOG_DATA_ROOT=isolated clone.
- Build `.2` was launched from this source against the isolated Catalog. Remote Desktop Commander confirms the device/process but provides no screenshot/window controls; Computer Use inventory returned `apps: []`, so the UI is not visually confirmed by the tool.
- Pre-VerifyOnly backup in the same existing acceptance directory: `catalog.pre-popup-send-build-2026-09-30.sqlite3`; SHA256 is recorded in CURRENT_STATE. Both source clone and backup passed SQLite integrity checks.
- The Desktop `.lnk` and `.cmd` remain pointed at this forward checkout's `catalog_center\RUN_QT.ps1`; no shortcut or folder relocation was made.

## 2026-09-29 current operator and Host transport status
- Forward checkout: `D:\projects\3DPrintHub-a2z-a2r-converge`, branch `wip/phase50-a2z-w5-manual-product-20260927`; exact live HEAD is maintained in Git and must be reverified.
- Host transport remains only `Windows 127.0.0.1:22024 -> Host bridge 127.0.0.1:22224`, through `D:\projects\.chatgpt-gateway\project-host.ps1 -Project 3dprinthub`.
- Current observation: inbound Host SSH session reaches Windows `sshd`, but no 22024 reverse-forward listener exists and gateway health fails. This path is currently unusable; no Host identity is claimed. Do not use FTPS, browser, direct SSH or another project's tunnel as fallback.
- Persistence owner: Host cPanel one-minute watchdog invokes `scripts/host/phase50_reverse_tunnel_bootstrap.sh` under `flock`; inspect its live state only after the authorized forward is restored (or by approved owner break-glass).

---

## 2026-09-26 O7A current Windows operator path
- Current forward Windows source worktree: `D:\projects\3DPrintHub-a2z-a2r-converge`.
- Current O7A branch: `wip/phase50-a2z-o7a-acquisition-ui-20260926`.
- Entry accepted lineage HEAD: `eba70a55bd6907564744f3805005cac1f7659531`.
- O7A GitHub implementation commit: `4a7d2771f0b982db3deea5b5e48b058ea6c1882e`.
- Catalog version remains v8.9.11 / build 2026.09.20.1.
- Shared Catalog authority remains `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.
- Repository launcher for O7A QA: `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1`.
- `D:\projects\3DprintHub` is an obsolete v8.9.10 worktree for current Windows UI development; do not select it by folder-name convention.
- Before future Windows Catalog edits, verify worktree list + APP_VERSION/BUILD_ID + branch/HEAD ancestry against this forward lineage.

## 2026-09-21 A2Y accepted unified paths
- Authoritative forward Local worktree: `D:\projects\3DPrintHub-a2y-converge`.
- Forward branch: `wip/phase50-a2y-lineage-convergence-20260921`.
- Accepted runtime-bearing merge SHA: `f9a9c203ae3a0a5665dbf884ce0c3e4bf761110b`.
- Merge parents: Windows/A2Y `c593eaf4...` + Server/Production closure `e03bdd2b...`; original merge-base `b1caeba0...`.
- Shared Catalog authority: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.
- Repository launcher: `D:\projects\3DPrintHub-a2y-converge\catalog_center\RUN_QT.ps1`.
- Desktop launchers: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk` and `.cmd`, both now target the unified launcher.
- Pre-cutover shortcut rollback: `D:\projects\3dprinthub-backups\phase50-a2y-shortcut-20260921-183438`.
- Old A2U worktree remains historical/rollback evidence; do not use it as the new forward launcher after A2Y acceptance.
- Dirty planning worktree `D:\projects\3DPrintHub-a2y-plan` remains untouched evidence and is not the forward runtime.
- Old primary clone `D:\projects\3DPrintHub` remains dirty/behind with pre-existing owner documentation work; do not reset/clean or silently promote it.
- A2Z may mutate Catalog only after a fresh integrity-checked backup under the normal backup root.

## 2026-09-21 A2Y reconciliation paths

## 2026-09-20 A2U current Windows operator paths
- Current Windows operator worktree: `D:\projects\3DPrintHub-a2u-latest-windows`.
- Branch: `wip/phase50-a2u-latest-windows-a2t-20260920`.
- Pushed source candidate: `d77dfd95f5d3a9a707f9ad03f2aacff9e69ac2e2`.
- Version: v8.9.11 / build 2026.09.20.1.
- Shared Catalog authority: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.
- Repository launcher: `D:\projects\3DPrintHub-a2u-latest-windows\catalog_center\RUN_QT.ps1`.
- Desktop launchers: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk` and `.cmd`.
- Shortcut rollback: `D:\projects\3dprinthub-backups\phase50-a2u-shortcut-20260920-210723`.
- Pre-reconcile Catalog rollback: `D:\projects\3dprinthub-backups\phase50-a2u-pre-reconcile-625-20260920-210357`.
- Do not retarget operator shortcuts to `D:\projects\3DPrintHub-a2t-windows`; that lineage lacks the latest Windows image-workspace ancestry.

## 2026-09-15 Product #628 re-entry acceptance paths
- Windows runtime/GitHub: `6e306e5353a6d6cd9d434894870839e533fa9622`.
- Fresh Catalog rollback: `D:\projects\3dprinthub-backups\product628-prepublish-20260915-135143\catalog-before-product628.sqlite3`.
- Fresh Production rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20260915-135005-product628-prepublish`.
- Accepted Batch: `desktop_catalog_v85_20260915_135231`, UUID `6b13e27b-c08a-446b-98d9-76260d906cca`.
- Catalog #628 -> Site Product #21 -> `/store/product/majestic-hydra-voronoi-art-sculpture/`.

## 2026-09-15 Phase50.A.3 ZarinPal compatibility paths
- Pre-change rollback branch: `backup/pre-phase50-a3-zarinpal-current-api-20260915` -> `1a29e22537a1471119d6b040eb7957b029c9c732`.
- Production baseline for this deploy: `b1caeba0f20e711b29dfa9e0ff92a2f5186fb08d`.
- Dedicated deploy runner: `scripts/host/phase50_zarinpal_current_api_deploy.sh`.
- Live defaults: `https://payment.zarinpal.com/pg/v4/payment/request.json`, `.../verify.json`, `https://payment.zarinpal.com/pg/StartPay/`.
- Sandbox host: `https://sandbox.zarinpal.com/` with the same v4 paths.
- Merchant credentials remain only in the existing Production secret boundary; no secret path/value is added to Git.

## 2026-09-15 permanent execution topology
- Local repository: `D:\projects\3DPrintHub`, operated through the connected Windows Remote Desktop device.
- Production operator path: Windows `127.0.0.1:22024` -> Host authenticated bridge `127.0.0.1:22224` -> `/home/sfkilvrs/3dprinthub`.
- Persistence authority: cPanel cron watchdog + `scripts/host/phase50_reverse_tunnel_bootstrap.sh`; other project tunnels are out of scope.

## 2026-09-15 Client handoff deploy paths
- Candidate GitHub commit before runner commit: `dd1e770abd26438021d9728a7ee616c89429e137`.
- Current verified Production source: `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`.
- Dedicated deploy runner: `scripts/host/phase50_client_handoff_deploy.sh`.
- Store reset backup helper: `scripts/host/phase50_store_reset_prepare.py`.
- Reverse operator loopback: `127.0.0.1:22024`; Host bridge loopback: `127.0.0.1:22224`.
- Production root/Python/MySQL/static remain `/home/sfkilvrs/3dprinthub`, `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`, `sfkilvrs_EmiAdmin_3dprinthub`, `/home/sfkilvrs/public_html/static`.

## 2026-09-14 Product #62 acceptance / stale-public pending paths
- Local/live GitHub source: `07772ca9247357ff63d2395eea9eed70780c9a68`.
- Current verified Production source: `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7` (clean).
- Product #62 canonical pre-write Catalog backup: `D:\projects\3dprinthub-backups\phase50-profile62-write-20260914-152628\catalog-before-profile62-write.sqlite3`.
- Product #62 Production prepublish MySQL backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-152920-product62-prepublish/database-before-3i53.sql.gz`.
- Stale-public source/env rollback bundle: `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-151721-phase50-stale-public-orderability`.
- Catalog #62 -> Host asset 140 -> Site Product 18 `/store/product/fanart-solidarity-bear/` -> orderable Variant 884.
- Catalog #84 -> Site Product 19 `/store/product/halloween-samhain-pumpkin-led-goth-tealight-holder/`; currently 0 orderable Variants.

## 2026-09-14 ERR-49-138
- Stale-public deploy runner: `scripts/host/phase50_stale_public_orderability_deploy.sh`.
- Rollback branch: `backup/pre-err49-138-stale-public-orderability-20260914` -> `70a74e6...`.
- Pre-repair Catalog backup: `D:\projects\3dprinthub-backups\phase50-profile-repair-preview-20260914-145936\catalog-before-profile-repair.sqlite3`.

## 2026-09-14 ERR-49-135 sales repair paths
- Production baseline before orderability hotfix: `6569e5a9ec7e75da7185b851fc6eea82cd7fc0ea`.
- Dedicated deploy runner: `scripts/host/phase50_orderable_publish_contract_deploy.sh`.
- Pre-refinalize backup retained: `D:\projects\3dprinthub-backups\phase50-image-refinalize-20260914-142031`.
- Pre-publish #62/#84 backup retained: `D:\projects\3dprinthub-backups\phase50-prepublish-62-84-20260914-142108`.
- Current Site mappings needing orderability repair: Catalog #62 -> Site #18; Catalog #84 -> Site #19.

## 2026-09-14 owner-license sales retry paths
- Current verified Production runtime: `6569e5a9ec7e75da7185b851fc6eea82cd7fc0ea`.
- Fresh canonical Catalog pre-retry backup: `D:\projects\3dprinthub-backups\phase50-owner-license-retry-20260914-141227\catalog.sqlite3`.
- Published Site Products: #16 `/store/product/majestic-hydra-voronoi-art-sculpture/`; #17 `/store/product/flexi-mini-seal/`.

## 2026-09-14 A2I + Bridge verified Production checkpoint
- Verified Production source: `44a7be91057c60891960fbb9d9b4f53780273c33` on canonical branch.
- Combined deploy runner: `scripts/host/phase50_a2i_bridge_hero_combined_deploy.sh`.
- Verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-130234-phase50-a2i-bridge-hero`.
- Production root/Python/MySQL/static/media paths are unchanged from the verified reverse-tunnel profile.
## 2026-09-19 Buffer provider-media compatibility paths
- Canonical source remains D:\projects\3DPrintHub; generated social binaries must not be committed to the canonical development branch.
- Dedicated Buffer social-assets worktree: D:\projects\3DPrintHub-social-assets.
- Dedicated public asset branch: social-assets-buffer.
- Current accepted #625 derivative revision: social_media/instagram/625/de334e0b160efee2/.
- Current verified social-assets remote head after deterministic manifest refresh: 6561dc3e2709ccc2d2651d576d1e744b35058891.
- Canonical Product media remains under https://3dprinthub.ir/media/p/...; provider-delivery URLs are separate audit fields and must never replace Product media/SEO identity.
- Local generated feed cache: %LOCALAPPDATA%\3DPrintHub\instagram\feed\<product>\<revision>\.
- Local Story cache: %LOCALAPPDATA%\3DPrintHub\CatalogCenter\social\stories\<product>\<revision>.png.

## 2026-09-13 Reverse tunnel E2E verified paths
- Current Production/Local/GitHub checkpoint at verification: `d7cf71dceca95e191a118336c7004683083278ee`.
- Windows operator loopback: `127.0.0.1:22024`; Host bridge loopback: `127.0.0.1:22224`.
- Windows public endpoint: `37.255.236.184:443`; Windows LAN SSH target: `192.168.0.23:22`; Host source IP: `89.39.208.237`.
- Windows tunnel identity: `PrintHubTunnel`; authorized key file is protected under `C:\ProgramData\ssh\printhubtunnel_authorized_keys`.
- Host private tunnel state: `/home/sfkilvrs/.config/reverse-host-bridge/3dprinthub/`; the FTPS account is chrooted so the same location appears in WinSCP as `/.config/reverse-host-bridge/3dprinthub/`.
- Protected Windows operator token file: `C:\Users\Emad-PC\AppData\Local\3DPrintHub\reverse-host-bridge\operator.token`; record path only, never token value.
- Production root `/home/sfkilvrs/3dprinthub`; Production Python `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`.
- Onboarding rollback evidence: `/home/sfkilvrs/3dprinthub-deploy-backups/20260913-094206-reverse-tunnel-onboarding`.

## 2026-09-13 Reverse tunnel operations paths
- Reference standard source: Asal branch `ops/reverse-tunnel-remote-management-20260912` / commit `7948a7c`.
- 3DPrintHub runbook: `docs/operations/REVERSE_TUNNEL_REMOTE_MANAGEMENT.md`.
- Operator scripts: `scripts/operator/reverse_host_bridge.py`, `start_reverse_host_bridge.sh`, `invoke_reverse_host_bridge.ps1`.
- Windows public endpoint: `37.255.236.184:443/tcp`; LAN SSH target `192.168.0.23:22`; project loopback `127.0.0.1:22024`.
- Windows tunnel account: `PrintHubTunnel`; authorized-key file under ProgramData SSH; key value remains outside docs/Git/chat.
- Windows firewall profile: `ChatGPT-ReverseTunnel-3DPrintHub`, source `89.39.208.237/32`, local `192.168.0.23:22`.
- Production project root remains `/home/sfkilvrs/3dprinthub`; bridge base is that verified root.
- Production bridge Python remains `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`; Host bridge loopback port is `22224`.
- Host private tunnel key and bridge token must live outside Git under the Host account; exact file locations are provisioned during first-use onboarding and then recorded without secret values.
## 2026-09-12 A2G current paths / Production baseline
- Current Host Git source (read-only FTPS verified 2026-09-13): `a320a0d346e4be573504978b23d197dc08f8bc2c`. Full A2G Production acceptance is still pending tunnel-based authenticated verification.
- Verified A2F backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260912-182234-phase50-a2f-storefront`.
- Production project: `/home/sfkilvrs/3dprinthub`; venv `/home/sfkilvrs/virtualenv/3dprinthub/3.12`; MySQL `sfkilvrs_EmiAdmin_3dprinthub`.
- Current A2G phase: `docs/phases/PHASE50_A2G_PUBLISH_MEDIA_ORDER_WIZARD.md`.
- A2G deploy runner: `scripts/host/phase50_a2g_publish_media_order_wizard_deploy.sh`.
- A2G source promotion already advanced Host from `7d0b3df...` to `a320a0d...`; do not rerun the old baseline deploy. Finish authenticated runtime/readiness/worktree acceptance after reverse tunnel onboarding.

## 2026-09-12 Production/FTPS/deploy paths — live reverified

- Explicit FTPS endpoint verified from owner Windows: `nphost4.parsblog.com:21` with TLS; account home maps to `/home/sfkilvrs` and exposes canonical project `/home/sfkilvrs/3dprinthub`.
- Production Git branch ref read from Host: `agent/phase49-3i18-operator-bulk-ai-rebuild` → `e12fdaf281f7e08013e54c7cf936f8275127ab2b`.
- Verified 53G current-partial backup evidence: `/home/sfkilvrs/3dprinthub-deploy-backups/20260910-131314-phase49-3i53g-partial`.
- New Phase50.A.2F no-migration deploy runner: `scripts/host/phase50_a2f_storefront_production_deploy.sh`.
- Current deploy baseline expected by that runner: `e12fdaf281f7e08013e54c7cf936f8275127ab2b`.
- Production receiver endpoint `https://3dprinthub.ir/api/catalog-bridge/v1/publish-readiness/` was authenticated from Windows Credential Store and returned `ready=true` with no blockers on 2026-09-12.

Historical path sections below remain evidence for earlier recovery stages but their “expected current Host source” values are not current.

## Phase49.3I.53G partial MySQL recovery paths — 2026-09-02
Production partial-recovery runner: `scripts/host/phase49_3i53_partial_0039_resume.sh`.
Original verified rollback set: `/home/sfkilvrs/3dprinthub-deploy-backups/20260902-211013-phase49-3i53`.
Fresh verified pre-migration DB backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260902-212529-phase49-3i53-resume/database-before-3i53.sql.gz`.
53G creates a new current-partial backup below:
`/home/sfkilvrs/3dprinthub-deploy-backups/<timestamp>-phase49-3i53g-partial`.
Expected current Host source before 53G recovery: `5f6c13ab879558cb66db3e316e0522c5e5783ae0`.
Exact tested 53G recovery checkpoint: `66e940e6e659f86e3783d78d091b3ff00acbf5aa`.

## Phase49.3I.53D backup helper — 2026-09-02
Production MySQL backup helper in Repository: `scripts/host/phase49_3i53_mysql_backup.py`.
Failed evidence backup root retained: `/home/sfkilvrs/3dprinthub-deploy-backups/20260902-203857-phase49-3i53`.
Its `database-before-3i53.sql.gz` is NOT a valid gzip restore artifact and must not be reused.
Current backup-fix checkpoint: `3b6254bf7700bb26b4af63d21e31e56e7700877c`.

## Phase49.3I.53C verified Production paths — 2026-09-02
Host audit effective paths:
- Static: `/home/sfkilvrs/public_html/static`;
- Media: `/home/sfkilvrs/3dprinthub/media`;
- Private Media: `/home/sfkilvrs/3dprinthub/private_media`;
- Bridge pending: `/home/sfkilvrs/3dprinthub/imports/desktop_catalog/pending`;
- deploy backups: `/home/sfkilvrs/3dprinthub-deploy-backups/<timestamp>-phase49-3i53`;
- Production deploy runner: `scripts/host/phase49_3i53_production_deploy.sh`.

Verified Host baseline: `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.
Rollback branch: `rollback/phase49-3i53-predeploy-host-198fa8e-20260902`.
Deploy-runner checkpoint: `5c5f087ae26e78c106984cf3c92e9b322537f203`.

## Phase49.3I.53B Host evidence — 2026-09-02
Verified Host project Python: `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python`.
System `python3`: unavailable in the login shell.
Actual read-only Host HEAD observed: `198fa8e41ea4f4d87eb287ba69c91076acc78d62`.
Untracked Host evidence currently blocking clean-worktree gate: `/home/sfkilvrs/3dprinthub/ls-output.txt`; SHA256 `8e01c07fcdf242fdc9be7de5a3a9b86cd7f0244e37ace629bc22d10ac1bee738`.
Updated audit runner contract: `scripts/host/phase49_3i53_production_readonly_audit.sh <target-sha> <verified-host-head>`.

## Phase49.3I.53 Site/Host paths — 2026-09-02
Production read-only audit runner in Repository: `scripts/host/phase49_3i53_production_readonly_audit.sh`.
Site receiver readiness endpoint after deploy: `https://3dprinthub.ir/api/catalog-bridge/v1/publish-readiness/`.
The runner is executed from the verified GitHub commit without permanently editing Production source during the audit.

Current 3I.53 final code checkpoint: `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`.
Current 3I.53 Site/Product Admin run: `33652584032` PASS.
Current 3I.53 Qt run: `33653229142` PASS.
Current 3I.53 Portable run: `33653229400` PASS.
Current Windows packaged runtime: `62ce5c3393a888cc1a027e4ca6bbb88f189bc845`.
Windows artifact ID: `9855771656`.
Windows EXE SHA256: `a6bebd3c10a56aac1c65a58d5ffb1029382e98c7b0782a4b034a315e60c2f1ed`.

# PROJECT PATHS AND ENVIRONMENTS

Last Verified: 2026-09-02 from Repository + GitHub Actions + prior owner Production verification. Re-verify actual Local/Host state again before operations.

## LOCAL / WINDOWS
OS: Windows / PowerShell
Project Root: `D:\projects\3DPrintHub`
Catalog Center Source: `D:\projects\3DPrintHub\catalog_center`
Mature Tk Launcher: `D:\projects\3DPrintHub\catalog_center\launch.py`
Parallel Qt6 Preview Launcher: `D:\projects\3DPrintHub\catalog_center\qt_launch.py`
Qt6 Presentation Package: `D:\projects\3DPrintHub\catalog_center\qt6`
Qt6 Preview Requirements: `D:\projects\3DPrintHub\catalog_center\requirements-qt6.txt`
Venv: `D:\projects\3DPrintHub\.venv`
Django DB: `D:\projects\3DPrintHub\db.sqlite3`
Persistent Catalog Root: `D:\projects\3dprinthub-catalog-manager`
Catalog SQLite: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`
Canonical downloaded Product images: `D:\projects\3dprinthub-catalog-manager\collected\<source_code>\<external_id>\images`
Canonical finalized SEO images: `D:\projects\3dprinthub-catalog-manager\collected\<source_code>\<external_id>\seo_images`
Historical mature refetch folders below the same Source directory: `<external_id>_refresh_latest`, `<external_id>_refetch_<timestamp>`, `<external_id>_bulk_refetch_<timestamp>` (read-only image compatibility)
Legacy Installed Application Root (retained/read-only fallback): `D:\projects\3dprinthub_catalog_center`
Backups: `D:\projects\3dprinthub-backups`
Runtime Logs: under persistent Catalog data root, including `logs\phase49_3f\YYYY-MM-DD\workflow-*.jsonl` and acquisition diagnostics `logs\acquisition\acquisition-YYYY-MM-DD.jsonl`
Canonical validated pre-49.3I Runner: `D:\projects\3DPrintHub\RUN_PHASE49_3H_LOCAL_GATE.ps1`
Canonical current Local gate: `D:\projects\3DPrintHub\RUN_PHASE49_3I42C_LOCAL_GATE.ps1` (`49.3I.52.2`)
Crawl ledger continuation table: Catalog SQLite `crawl_listing_state` (additive; mature `discovered_urls` remains identity ledger)
Rejected Product physical purge boundary: only under persistent Catalog `collected\` root; source URL/external ID tombstone stays in Catalog SQLite.

## GITHUB
Repository: `farazha2203/3dprinthub`
Active Development Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Current 3I.52G runtime/CI checkpoint: `bf1fafdb38233a23e13a5715ffac72f772412005`
Current 3I.52G Qt run: `33644903042` PASS
Current 3I.52G Portable run: `33644902962` PASS
Current Admin shell CI runtime: `27335832e90c35dd95bb8a686dd89d1efd46dc8f`
Current Store/Profile/Filament CI runtime: `d519a360e65b79db4b62af206b95f63c3539bc12`
Current Store/Profile/Filament CI run: `33059883188` PASS
Current Windows packaged runtime: `bf1fafdb38233a23e13a5715ffac72f772412005`
Catalog Center: `8.9.10` / build `2026.09.02.1`
Windows artifact ID: `9852476786`
Windows EXE SHA256: `f3e0bce9e5d3b40317b5fd37cff8a5fc6ff1d5a2cef6f5b1bf84dc6f6699c310`
Last owner Local automated gate: PASS at local head `2cdb356fca6d6c4c4bcd0edf203acf8e24bab2b9`; Local Django SQLite is through `store.0039`; backup `D:\projects\3dprinthub-backups\phase49-3i35-resume-20260827-142404\django-local-before-0039.sqlite3`.
Delivery: GitHub-first only; no standalone chat patches/scripts and no permanent direct Production source edits.

## PRODUCTION
Project Root: `/home/sfkilvrs/3dprinthub`
Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Python: 3.12.13
Django: 6.0.7
Database Engine: MySQL
Database Name: `sfkilvrs_EmiAdmin_3dprinthub`
Static Base: `/home/sfkilvrs/public_html/static`
Media Base: `/home/sfkilvrs/public_html/media`
Private Media: `/home/sfkilvrs/3dprinthub/private_media`
Passenger Restart Pattern: `mkdir -p tmp && touch tmp/restart.txt`
Current verified Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`
Latest verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`
Previous incomplete pre-deploy audit backup retained for evidence: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143245`

## PRIVATE / PURCHASED ADMIN ASSETS
Velzon vendor assets are expected privately at runtime under `static/velzon_master/` and are intentionally gitignored in the public Repository. Production verification confirmed required Bootstrap RTL, app RTL, layout.js and Bootstrap bundle files are present. Public GitHub stores only project-owned Django/Velzon adapter CSS/JS/templates.

## DOMAIN
Main: `https://3dprinthub.ir`

## Production Git caveat
The current Host `remote.origin.fetch` still tracks only `+refs/tags/v0.33.0:refs/tags/v0.33.0`; normal `git fetch origin` does not update the active branch remote-tracking ref. Per `ERR-50-007`, verify the live branch with `git ls-remote` and explicitly fetch `refs/heads/agent/phase49-3i18-operator-bulk-ai-rebuild` to `FETCH_HEAD`, then verify SHA/ancestry and use ff-only merge.

## Production shell caveat
This cPanel environment did not provide a reliable `/dev/fd` path for Bash process substitution during deployment backup. Per `ERR-50-010`, avoid `< <(...)` in Production deployment scripts; use the Production Python runtime or portable temporary-file approaches for enumeration/copy operations.

## Safety
- Do not assume `.env` paths equal defaults; inspect runtime settings before Production operations.
- Do not assume Local SQLite and Production MySQL behavior are identical.
- Dirty Local/Host worktree: STOP/INSPECT; no reset/delete shortcut.
- Before Production migration verify exact project root, branch, commit, Python venv, DB vendor/name, backup target and rollback.
- JSON/API smoke payloads are data, not executable source; use `python - <args>` and explicit `json.load` when verifying endpoint responses.


## 2026-10-08 — Canonical Windows paths after worktree cleanup

Current Windows runtime/source: `D:\projects\3DPrintHub-a2z-a2r-converge` (Catalog Center v8.9.11 / Build 2026.10.04.2).

Canonical Git anchor/shared venv: `D:\projects\3DPrintHub`; do not remove while the current runtime remains a linked Git worktree and `RUN_QT.ps1` uses its `.venv`.

Persistent Catalog/data root: `D:\projects\3dprinthub-catalog-manager`.

Current Buffer/social provider asset worktree: `D:\projects\3DPrintHub-a2z-a2r-converge-social-assets`.

Rollback/backups root: `D:\projects\3dprinthub-backups`; cleanup rollback evidence: `worktree-cleanup-20261008-193657`.

Desktop shortcut: `C:\Users\Emad-PC\Desktop\3DPrintHub Catalog Center.lnk` -> PowerShell -> `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1`.

Historical runtime/release/Slicebox/Social worktree folders removed on 2026-10-08 are no longer valid execution paths. Recreate from Git branches/rollback evidence only if explicitly needed.
