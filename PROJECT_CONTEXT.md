# PROJECT_CONTEXT - 3DPrintHub

## Permanent paths

- Windows project root: `D:\projects\3DPrintHub`
- Production project root: `/home/sfkilvrs/3dprinthub`
- Repository: `farazha2203/3dprinthub`
- Production runtime: Python 3.12, Django, MySQL, cPanel Passenger
- Local runtime: Python 3.12, Django, SQLite

## Source-of-truth rule

After phase 32 baseline synchronization, GitHub `main` is the source of truth.
Normal delivery flow is:

`local tests -> GitHub branch -> reviewed main -> version tag -> production deployment`

Runtime data is never deployed through Git:

- `.env`
- MySQL data
- `db.sqlite3`
- `media`
- `private_media`
- `staticfiles`
- licensed font files
- licensed Velzon runtime files that are intentionally kept outside Git

## Completed recovery state

Phase 31 completed successfully:

- 2408 transferred fixture objects
- 51 fixture models
- 31 provinces
- 427 counties
- 1242 cities
- all business model counts matched at restore time
- MySQL and media backup created
- site and admin HTTP checks returned 200

The production catalog is live data and can grow after restore. Runtime models must
be audited with invariants and lower bounds, not exact fixture equality.

## Baseline safety fix

All post-save signal handlers that can run during `loaddata` must return when
`kwargs.get("raw")` is true. This prevents duplicate one-to-one rows during
fixture restoration.

## Current phase

Phase 33: automation deadlines, stale-run watchdog, operator stop controls, and
IRANSans enforcement across the management dashboard and sidebar.

## Required phase workflow

1. Read this file.
2. Fetch current GitHub main.
3. Create a dedicated phase branch.
4. Develop locally.
5. Run compile, Django check, migration check, targeted tests, and full tests.
6. Push only intended files.
7. Merge after successful validation.
8. Create an immutable version tag.
9. Back up production.
10. Deploy the exact tag.
11. Run migrations and collectstatic.
12. Run runtime verification and smoke tests.
13. Record the result here.
