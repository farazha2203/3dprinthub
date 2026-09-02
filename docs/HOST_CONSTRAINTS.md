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
