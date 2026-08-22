# HOST / PRODUCTION CONSTRAINTS

Last Verified From Project Source of Truth: 2026-08-22. Re-verify actual host state read-only before deployment.

## Environment
Host Type: shared hosting / cPanel-style production environment
Application Runtime: Python/Django under Passenger/LiteSpeed pattern
Project Root: `/home/sfkilvrs/3dprinthub`
Venv: `/home/sfkilvrs/virtualenv/3dprinthub/3.12`
Database: MySQL `sfkilvrs_EmiAdmin_3dprinthub`
Static Base: `/home/sfkilvrs/public_html/static`
Media Base: `/home/sfkilvrs/public_html/media`
Private Media: `/home/sfkilvrs/3dprinthub/private_media`

## Restrictions / Rules
- Production source changes must never be edited permanently on host; deploy only committed GitHub code.
- Before migrations, verify `connection.vendor == 'mysql'` and exact DB name. SQLite fallback means STOP.
- `.env` may override default paths/settings; inspect effective runtime settings before deploy.
- `mysqldump`/backup must succeed before production schema migration. Missing/failed backup means STOP.
- Pending import files, media/private_media and `.env` are persistent data; do not delete/reset as a code-sync shortcut.
- Production deployment is forbidden until Local automated gate + visual/data QA + LOCAL PUBLISH E2E + explicit user approval.

## Restart
Correct Pattern:
```bash
mkdir -p tmp
touch tmp/restart.txt
```
Restart alone is not verification; follow with runtime verifier + HTTP smoke checks.

## Deployment Order
1. verify project root / branch / approved commit
2. verify clean/safe host state
3. backup `.env` and persistent pending import state
4. `manage.py check`
5. `makemigrations --check --dry-run`
6. verify MySQL vendor/name
7. database backup if migration needed
8. `migrate --plan`
9. approved migration only
10. `collectstatic --noinput`
11. Passenger restart
12. runtime and HTTP smoke verification
13. product/home/admin/cart/data/media verification
14. update docs

## Known Host-Specific Concerns
- In-memory realtime warning (`store.W026`) is not a production multi-process solution; Redis/polling strategy is a separate architecture task.
- CKEditor4 warning is technical/security debt and should not be silently suppressed.

Never assume Local Windows/SQLite behavior is valid on Production MySQL/Passenger.
