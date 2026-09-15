## 2026-09-15 ERR-49-146 current handoff constraint
The 3DPrintHub reverse-management watchdog is not currently executing; Windows loopback 22024 is closed. Host private state is reachable read-only by FTPS, but FTPS must not be used to upload permanent source and does not provide command execution. The Host tunnel key fingerprint still exactly matches Windows `printhubtunnel_authorized_keys`, so key replacement is forbidden. Do not use another project tunnel. Client-handoff deploy/reset may resume only after the 3DPrintHub cPanel cron/bootstrap is restored and authenticated bridge identity passes.

## 2026-09-14 current sales/Host execution boundary
Production is freshly verified clean at `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7`, MySQL `sfkilvrs_EmiAdmin_3dprinthub`, empty migration plan and publish readiness true. Live GitHub is `07772ca9247357ff63d2395eea9eed70780c9a68` and its stale-public lifecycle tests/CI pass, but the current remote-command safety layer rejects Host Git mutation. Treat this as an execution-channel boundary, not authorization to bypass GitHub-first governance. Read-only verification and verified backups remain allowed; permanent Production source must still move only from approved GitHub code through an authorized Host execution path.

## 2026-09-14 ERR-49-138 deploy constraint
Deploy stale-public cleanup only from exact clean Production baseline `70a74e6f21113ae6bc5ed1f679d1e57e4e5a8eb7` using `scripts/host/phase50_stale_public_orderability_deploy.sh`. No migration, dependency, DB migration/write step or collectstatic is permitted by the runner; Product state changes occur later only through the canonical Catalog import path.

## 2026-09-14 ERR-49-135 deployment constraint
Production application baseline for the orderability hotfix is exact clean `6569e5a9ec7e75da7185b851fc6eea82cd7fc0ea`. Deploy only through `scripts/host/phase50_orderable_publish_contract_deploy.sh` from a live GitHub target. The runner is no-migration/no-DB-write/no-collectstatic, requires empty migration plan/readiness, checksum-verifies source/.env rollback evidence, ff-only promotes, restarts Passenger, and proves known-good Site Products #16/#17 still contain an actually orderable Variant. #62/#84 are repaired only afterward through the Windows Catalog publish path; do not hand-edit their Production Variants.

## 2026-09-14 owner-license parity current Production constraint
Current Production source is `6569e5a9ec7e75da7185b851fc6eea82cd7fc0ea`, clean after the guarded no-migration owner-license deploy. The Host now treats explicit `source_license_owner_approved=1` as effective business approval while preserving raw source `commercial_status` evidence. Product #628/#634 strict public visibility and browser Cart wiring are verified. Future publication must still use current Catalog factual gates, fresh Local backup, authenticated receiver readiness, strict ACK/public verification, and bounded batches.

## 2026-09-14 A2I + Bridge current Production constraint

Current verified Production source is `44a7be91057c60891960fbb9d9b4f53780273c33`, clean after the combined A2I + ERR-49-125 promotion. MySQL remains `sfkilvrs_EmiAdmin_3dprinthub`; required migrations are applied and plan is empty; publish readiness is true. Verified rollback evidence is `/home/sfkilvrs/3dprinthub-deploy-backups/20260914-130234-phase50-a2i-bridge-hero`. Do not rerun the old Bridge-only `443d1b70` baseline runner. Future deployment planning must start from fresh read-only verification of this newer Host state.
## 2026-09-13 Reverse management E2E verified constraint

The 3DPrintHub shared Host is now manageable through the proven Asal pattern without inbound Host SSH: Host `89.39.208.237` opens outbound SSH/443 to Windows `37.255.236.184:443`; dedicated non-admin `PrintHubTunnel` exposes only Windows loopback `127.0.0.1:22024`, forwarding to authenticated Host bridge `127.0.0.1:22224`. Both bridge and tunnel background processes were verified alive. Tokens/private keys remain outside Git/chat.

Authenticated identity and repository audit proved Production is `sfkilvrs@nphost4.parsblog.com`, root `/home/sfkilvrs/3dprinthub`, clean branch `agent/phase49-3i18-operator-bulk-ai-rebuild`, source `d7cf71dceca95e191a118336c7004683083278ee`. MySQL/migration/readiness/public HTTP gates pass. This transport authorizes remote diagnostics and guarded repository-owned operations; it does NOT authorize permanent direct Production source edits or bypass GitHub-first, backup, migration-plan or rollback rules.

Windows caveat: running `sshd -t` from a non-elevated process can return 255 because protected OpenSSH host private keys are unreadable to that process even while the Windows `sshd` service is healthy. Do not classify that return code alone as config failure; use elevated validation or verify service/listener/Event Log evidence. FTPS is account-chrooted: `/` maps to `/home/sfkilvrs`, so private Host state is `/.config/...` in WinSCP.

If the reverse tunnel dies, first verify current Local/GitHub/Host identities and protected state, then reuse `scripts/host/phase50_reverse_tunnel_bootstrap.sh`; do not broaden the Windows firewall or expose the Host bridge publicly.

## 2026-09-13 Reverse Host management transport constraint

3DPrintHub adopts the proven Asal shared-cPanel reverse-management pattern. Windows is prepared with dedicated non-admin `PrintHubTunnel`, project loopback `127.0.0.1:22024`, and source-restricted firewall access only from Host `89.39.208.237/32` to LAN SSH target `192.168.0.23:22`. Public Windows endpoint is `37.255.236.184:443/tcp`.

The Host does not require inbound sshd. It runs the authenticated command bridge only on `127.0.0.1:22224`, then opens outbound SSH/443 to Windows with remote forward `127.0.0.1:22024 -> Host 127.0.0.1:22224`. Bridge token and tunnel private key remain outside Git/chat.

Repository onboarding runner: `scripts/host/phase50_reverse_tunnel_bootstrap.sh`. It performs no migration, DB write, Git deploy, collectstatic or Passenger restart. Current Host source was reverified read-only on 2026-09-13 as `a320a0d346e4be573504978b23d197dc08f8bc2c`; public Home/Store and A2G JS/CSS are HTTP 200. Full A2G acceptance still requires authenticated Bridge/readiness and exact Host identity/worktree verification after the tunnel is live.

## 2026-09-12 Phase50.A.2G current Production constraint
Production is A2F-verified at exact source `7d0b3df03c3657106ebaf86d5f9123ba262495a5`; MySQL receiver is ready with Store 0036-0042 + Website 0024 applied. A2G promotion must start from that exact clean Host baseline, use live `git ls-remote` + explicit branch fetch/FETCH_HEAD + ff-only merge, prove no migration/requirements/settings delta and an empty migration plan, create verified source/environment/static rollback evidence, then collectstatic/restart/HTTP+Bridge verify. A2G introduces no migration.

Repository runner: `scripts/host/phase50_a2g_publish_media_order_wizard_deploy.sh`; its local bash syntax, no-migrate check and exact target-delta contract PASS. Do not reuse the older A2F runner as if its `e12fdaf...` starting guard were current. The cPanel parent shell strict-mode rule remains: use a subshell, never global interactive `set -e`.

## 2026-09-12 cPanel interactive-shell strict-mode constraint
Do not paste `set -e` or `set -Eeuo pipefail` directly into the parent cPanel interactive shell. A deliberate fail-closed status will terminate that shell and the web UI will show Reconnect. Wrap strict bootstrap logic in a subshell `( ... )`; repository deploy runners remain child Bash processes and may keep strict mode.

## 2026-09-12 Recovery complete / current deployment constraint

Live evidence supersedes the older “partial 0039” state below. Production source is `e12fdaf281f7e08013e54c7cf936f8275127ab2b`; authenticated publish-readiness on MySQL reports Store 0036–0042 and Website 0024 applied, complete required schema, `ready=true`, and no blockers. Do not rerun the 53F or 53G recovery runners against this recovered state.

For Phase50.A.2F use only `scripts/host/phase50_a2f_storefront_production_deploy.sh`. It is intentionally no-migration and must fail closed unless Host branch/head/worktree match the verified baseline, the live GitHub target is exact and fast-forward, the reviewed target contains no migration/requirements/settings delta, the current MigrationExecutor plan is empty, and receiver readiness is already true. It creates source/environment/static backups before source promotion and does not write the database.

FTPS is suitable for read-only evidence/file inspection but is not an approved replacement for GitHub-first source deployment. No permanent source file may be uploaded directly to Production over FTP/FTPS. Deployment still requires the cPanel shell/Git path so the Host can explicit-fetch `FETCH_HEAD`, ff-only merge, collectstatic, restart Passenger and run verification.

## Phase49.3I.53G MySQL partial-migration constraint — 2026-09-02

Current Production must be treated as partial DB migration state:
- source HEAD expected `5f6c13ab879558cb66db3e316e0522c5e5783ae0`;
- Website 0024 + Store 0037/0038 applied;
- Store 0039 not recorded and failed mid-DDL;
- Store 0040–0042 pending;
- httpx 0.28.1 is installed in Production venv;
- collectstatic and Passenger restart for this release have not yet completed.

Do not:
- rerun the old 53F resume;
- fake 0039;
- manually drop duplicate columns;
- manually mark migration rows;
- restore an older DB over the partial state without a new decision.

Use only `scripts/host/phase49_3i53_partial_0039_resume.sh`. It must first reverify old rollback artifacts, then prove exact partial recorder/schema shape and take a fresh partial-state MySQL backup before any corrected migration is applied.

ProductVariant support_weight_grams is physically owned historically by 0033. Corrected 0039 aligns state via AlterField instead of AddField. Real-MySQL focused CI for AddFieldIfMissing passed in workflow `33666085743`.

## Phase49.3I.53F dependency/source-promotion constraint — 2026-09-02

Current Host source is no longer the predeploy baseline. Owner output proves `git merge --ff-only` completed to `b372586ab60234ec3faf3ce0624e07766db6ecce` before Django startup failed.

Therefore:
- do NOT rerun `phase49_3i53_production_deploy.sh` expecting baseline `198fa8e...`;
- use `scripts/host/phase49_3i53_postmerge_resume.sh` for this exact recovery state;
- verified rollback backup is `/home/sfkilvrs/3dprinthub-deploy-backups/20260902-211013-phase49-3i53`;
- DB is still pre-migration;
- target requirement delta from original baseline includes exact `httpx==0.28.1`;
- runtime dependency reconciliation must happen before target AI use;
- Site bootstrap itself must not require optional provider transport imports.

The resume runner must reverify rollback hashes/gzip/bundle before any new DB mutation, then create a fresh pre-migration DB dump after dependency recovery and before migration.

## Phase49.3I.53E Python helper import constraint — 2026-09-02

A Python helper executed from `/home/sfkilvrs/3dprinthub-deploy-backups/<timestamp>/` must not rely on cwd for importing the Django project. The deploy runner now passes:
`PHASE49_PROJECT_ROOT=/home/sfkilvrs/3dprinthub`.

The helper validates:
- `/home/sfkilvrs/3dprinthub/manage.py`;
- `/home/sfkilvrs/3dprinthub/config/__init__.py`;
and inserts that root into `sys.path` before `django.setup()`.

The failed `20260902-204716-phase49-3i53` backup directory is evidence only. Retry must use a fresh timestamped backup root.

## Phase49.3I.53D backup compression constraint — 2026-09-02

Do not treat a filename ending in `.gz` as a verified MySQL backup. The failed 20260902-203857 artifact demonstrated that attaching a child process directly to a Python `gzip.GzipFile` file descriptor writes raw bytes and bypasses the codec.

Current Production deploy must use `scripts/host/phase49_3i53_mysql_backup.py` through the repository deploy runner. Required success evidence before any source merge:
- helper prints `DATABASE_BACKUP_GZIP=VALID`;
- shell `gzip -t` passes;
- SHA256 manifest passes;
- runner prints `PREDEPLOY_BACKUP_VERIFIED=YES`.

The invalid `20260902-203857-phase49-3i53/database-before-3i53.sql.gz` is evidence only, not a restore backup. A retry must create a fresh timestamped backup root.

## Phase49.3I.53C audited deploy constraints — 2026-09-02

Verified Production before deploy:
- HEAD `198fa8e41ea4f4d87eb287ba69c91076acc78d62`;
- tracked/index worktree clean;
- Python 3.12.13 / Django 6.0.7 via project venv;
- MySQL `sfkilvrs_EmiAdmin_3dprinthub`;
- Store 0036 and Website 0023 applied;
- exact pending receiver chain Store 0037–0042 + Website 0024;
- Bridge token configured; active Material=13, PrintQuality=5;
- disk/inode headroom healthy; mysqldump available.

Use only `scripts/host/phase49_3i53_production_deploy.sh` for this promotion. It enforces the mature Host caveats:
- live branch verified by `git ls-remote`;
- explicit branch fetch to `FETCH_HEAD`;
- ff-only merge only;
- no process substitution;
- Production venv Python only;
- exact MySQL vendor/name before backup;
- checksum-verified database/source/environment/pending backups before migration;
- exact migration delta and MigrationExecutor plan;
- collectstatic without `--clear`;
- Passenger restart via `tmp/restart.txt`;
- authenticated Bridge health/readiness plus public home/store verification after restart.

Do not manually pre-run the pending migrations. Do not reset Host to the older documented c283 baseline. Do not delete persistent Media/Private/Pending data as a deployment shortcut.

## Phase49.3I.53B Host evidence correction — 2026-09-02

New verified Host facts:
- system/login-shell `python3` is not available;
- use `/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python` for project Python probes;
- actual Host HEAD observed read-only is `198fa8e41ea4f4d87eb287ba69c91076acc78d62`;
- tracked worktree/index were clean, but `ls-output.txt` is an untracked old evidence/output file and must be inspected/preserved before clearing the repo;
- do not reset to stale documented `c283864...`; GitHub comparison shows current Host HEAD is 23 commits ahead on the same ancestry chain.

The Production read-only audit now takes:
`phase49_3i53_production_readonly_audit.sh <live-target-sha> <verified-current-host-head>`.

Strict clean-worktree remains mandatory before deployment. Untracked operational evidence should be moved reversibly outside the repository with hash verification rather than deleted blindly.

## Phase49.3I.53 receiver/deploy constraint — 2026-09-02

Before any new Product-receiver deployment, run the repository-owned read-only audit:
`scripts/host/phase49_3i53_production_readonly_audit.sh`.

The audit must prove:
- exact Host root/repository/current HEAD and clean worktree;
- live GitHub target SHA;
- Production Python/Django;
- effective DB vendor `mysql` and exact database `sfkilvrs_EmiAdmin_3dprinthub`;
- `manage.py check`, `makemigrations --check --dry-run`, actual `showmigrations store website`, and `migrate --plan`;
- effective Static/Media/Private/Pending paths;
- Bridge token configured state without printing the secret;
- active Material/PrintQuality prerequisites;
- relevant receiver schema evidence;
- disk/inodes and `mysqldump` availability.

A passing script means only **read-only pre-deploy evidence is complete**. It does not authorize migration by itself. Because 0037/0041/0042 contain data operations, a fresh verified MySQL dump and rollback source/environment backups are mandatory before deployment/migration.

The Desktop receiver-readiness endpoint is a second fail-closed gate: even after Bridge health succeeds, Product FTP/upload must not start unless the live Site reports `ready=true`.

# HOST / PRODUCTION CONSTRAINTS

Last Verified From Project Source of Truth: 2026-08-26.

## Environment
Host Type: shared hosting / cPanel-style production environment
Application Runtime: Python/Django under Passenger/LiteSpeed pattern
Project Root: `/home/sfkilvrs/3dprinthub`
Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Python: 3.12.13
Django: 6.0.7
Database: MySQL `sfkilvrs_EmiAdmin_3dprinthub`
Static Base: `/home/sfkilvrs/public_html/static`
Media Base: `/home/sfkilvrs/public_html/media`
Private Media: `/home/sfkilvrs/3dprinthub/private_media`
Current verified Production application commit: `c283864290f9c989a9fcdf24ee8eef519560e917`
Latest verified rollback backup: `/home/sfkilvrs/3dprinthub-deploy-backups/20260826-143650`

## Restrictions / Rules
- Production source changes must never be edited permanently on host; deploy only committed GitHub code.
- Before migrations, verify `connection.vendor == 'mysql'` and exact DB name. SQLite fallback means STOP.
- `.env` may override default paths/settings; inspect effective runtime settings before deploy.
- `mysqldump`/backup must succeed before Production schema migration. Missing/failed backup means STOP.
- Pending import files, media/private_media and `.env` are persistent data; do not delete/reset as a code-sync shortcut.
- Production deployment is forbidden until the required CI/Local gates and owner approval for that batch are complete.
- Purchased/private Velzon assets and fonts stay out of the public Repository and must be verified on the target Host when relevant.
- Dirty Host worktree means STOP/INSPECT; do not reset/stash/delete as a cleanup shortcut.

## Git fetch constraint — ERR-50-007
Current Host `remote.origin.fetch` tracks only `+refs/tags/v0.33.0:refs/tags/v0.33.0`. Therefore:
1. verify live branch SHA with `git ls-remote origin refs/heads/<branch>`,
2. explicitly fetch the exact branch with `git fetch --no-tags origin refs/heads/<branch>`,
3. read the fetched commit from `FETCH_HEAD`,
4. verify exact SHA + fast-forward ancestry,
5. use `git merge --ff-only "$FETCH_HEAD_SHA"`.
Do not trust stale `origin/<branch>` on this Host unless the refspec is deliberately corrected and re-verified.

## Shell portability constraint — ERR-50-010
This cPanel execution environment did not provide reliable `/dev/fd` support for Bash process substitution (`< <(...)`). Deployment scripts must avoid `/dev/fd`/process-substitution dependencies. Use the Production Python runtime for file enumeration/copy, or a portable temporary-file/pipeline approach.

## Verifier data constraint — ERR-50-011
API/JSON smoke payloads are data files, not Python scripts. When a heredoc Python verifier also needs file arguments, use `python - <json-path> ...` and parse with `json.load`. Never invoke `python <json-file>`.

## Restart
Correct Pattern:
```bash
mkdir -p tmp
touch tmp/restart.txt
```
Restart alone is not verification; follow with runtime verifier + HTTP/static/data smoke checks.

## Deployment Order
1. verify project root / branch / current Production HEAD / approved GitHub target
2. verify clean Host state
3. verify live branch SHA and explicit `FETCH_HEAD` path
4. `manage.py check`
5. `makemigrations --check --dry-run`
6. verify exact MySQL vendor/name and relevant applied migrations
7. `migrate --plan`
8. create fresh tracked-source + environment + MySQL backups and checksums
9. verify target fast-forward ancestry and migration-file delta
10. ff-only deploy from verified `FETCH_HEAD`
11. repeat Django/model/migration-plan gates; run only explicitly approved migration(s), otherwise no `migrate`
12. `collectstatic --noinput`
13. Passenger restart
14. runtime + HTTP + new static + Product/API/private-media verification
15. owner browser QA
16. update Repository documentation

## Known Host-Specific Concerns
- In-memory realtime warning (`store.W026`) is not a production multi-process solution; Redis/polling strategy is a separate architecture task.
- CKEditor4 warning is technical/security debt and should not be silently suppressed.
- MySQL conditional unique-constraint warnings are known; do not infer a new migration failure from those warnings alone.

Never assume Local Windows/SQLite behavior is valid on Production MySQL/Passenger.
