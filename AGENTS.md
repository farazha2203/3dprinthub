# PROJECT AGENT RULES

GitHub is the permanent source of truth. Do not rely only on chat history.
Before work, read `docs/CURRENT_STATE.md`, `docs/ROADMAP.md`, `docs/PATHS.md`, `docs/ERRORS.md`, `docs/HOST_CONSTRAINTS.md` and the active phase document.
Never guess paths, branch, commit, versions, database state, host configuration, installed software or previous fixes. Verify real state first and correct stale documentation.

## Mandatory workflow
GitHub -> Local pull -> Local tests -> Fix if needed -> Commit/Push -> Host pulls approved commit -> Deploy -> Production verification.
Do not deliver project ZIP/patch/source files through chat. Do not make permanent source changes directly on production.

## Before every change
Verify project/directory, `git status`, current branch, last commit, active Epic/Phase, Local/Host paths, relevant dependencies, previous related errors, database state when relevant, host constraints, backup and rollback needs.

## Error prevention
Before troubleshooting read `docs/ERRORS.md`. Do not repeat a failed solution unless its underlying condition changed. Record important errors with symptoms, root cause, failed attempts, correct fix, verification and prevention rule.

## Safety
Read `docs/PATHS.md` before Local/Host commands. Never assume Local and Host paths match. Before database changes verify engine, database, environment, migrations and backup need. Avoid destructive Git/database/filesystem actions without verified target and rollback plan.

## Testing
A feature is not complete because code was written. Run relevant framework, syntax, lint, type, unit, integration, database, migration, build, API, auth, smoke and health checks. Do not deploy after an unexplained important failure.

## Documentation
After meaningful work update relevant docs: CURRENT_STATE, ROADMAP, ERRORS, CHANGELOG, REQUESTS and active phase. Update PATHS, DATABASE, DEPLOYMENT or HOST_CONSTRAINTS whenever those areas change.

## Phase status
Use PLANNED, IN_PROGRESS, IMPLEMENTED, LOCAL_TESTED, GITHUB_UPDATED, DEPLOYED, PRODUCTION_VERIFIED, ACCEPTED, BLOCKED. Do not mark ACCEPTED before required tests pass.

At session end `docs/CURRENT_STATE.md` must show what changed, what passed/failed, current branch/approved commit, production commit, known issues, remaining work and exact next task.

READ -> VERIFY -> IMPLEMENT -> TEST -> DOCUMENT -> COMMIT -> PUSH -> DEPLOY -> VERIFY
