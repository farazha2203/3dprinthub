# DEPLOYMENT RUNBOOK

Production code must come from GitHub.

## Standard Flow
GitHub -> Local Pull -> Local Tests -> Fix -> Commit/Push -> Approved Commit -> Host Pull -> Deploy -> Verify

## Local Precheck
`git status`
`git branch --show-current`
`git log -1 --oneline`
Approved Commit:

## Production Precheck
Verify server, path, branch, working tree, backup need and migration need.

## Update
Use `git fetch --prune origin` and `git pull --ff-only` on the correct branch. Install dependencies, migrate, build or restart only when required.

## Verify
Confirm deployed commit, health/HTTP/API, database connection, critical user flow and logs.

## Rollback
Previous Known Good Commit:
Database Backup:
Rollback Procedure:
