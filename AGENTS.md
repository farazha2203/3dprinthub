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

## CROSS-PROJECT SHARED CORE RULES

These rules are mandatory for all projects owned by this account.

### Guided UI, setup order and dependency visibility
Every important admin option, button, setting, wizard, integration, configuration page, data-entry section or operational action must explain:
1. What it does.
2. Where its result appears or is used.
3. Why it exists.
4. What prerequisites must exist first.
5. What data must be entered.
6. How to configure it.
7. What happens after Save/Run/Enable.
8. Dependencies on earlier steps/modules.
9. How to verify success.
10. Common missing prerequisites/errors.

When steps depend on each other, present them as a numbered workflow/wizard. A later step must not silently run when required earlier data is missing; show the missing requirement and the action/path to complete it.

Dashboards and main admin pages should report real useful data and setup progress (counts, configured entities, records, missing setup, integration/health status, pending work). Never use hard-coded placeholder counts as operational status.

### Authentication and security
Review authentication and sensitive forms. Where bot/abuse protection is appropriate, use reCAPTCHA or the project-approved equivalent, but never make Google a single point of failure.

If Google/reCAPTCHA/Google Login is blocked, filtered, unavailable or fails, use a secure approved fallback appropriate to the project, such as SMS OTP or username/password with rate limiting, lockout/brute-force protection and secure recovery. Never bypass authentication merely because Google is unavailable.

Document login methods, fallback order, provider configuration, environment variables, rate limits, audit/logging, failure/recovery behavior and tests. Never commit secrets/tokens/passwords/private keys.

### Shared code first
Before implementing or upgrading a capability, inspect:
- this repository's `shared/` folder,
- `shared/REGISTRY.md`,
- relevant implementations in the owner's other GitHub repositories.

Common reusable areas include authentication/login, SMS/OTP, Telegram, WhatsApp, AI providers, API clients, admin UI, guided setup, workers, crawlers, file handling, logging, retry/idempotency, security, data sync, deployment helpers and monitoring.

Prefer a proven implementation over rebuilding from zero, but never copy blindly. Before reuse verify source repo/path/commit, runtime/framework compatibility, security assumptions, DB/schema dependencies, environment variables and external providers. Adapt, test locally, then document the reusable pattern in `shared/REGISTRY.md`.

When a broadly useful fix or stronger implementation is discovered in one project, update the shared knowledge/registry so all projects can reuse it where compatible.

### SMS, Telegram and WhatsApp
Use provider/service adapters instead of scattering provider-specific logic through business code.

For SMS document configuration, templates/sender, OTP flow, retry/timeout, delivery logging, rate limits, fallback strategy if supported and tests.

For Telegram/WhatsApp document approved API method, authentication, webhook/polling architecture as applicable, retries, idempotency, media handling, rate limits, logs, failure behavior and tests.

### AI shared-core
AI integrations should use reusable provider/service abstractions when practical. Record provider/model purpose, configuration, request/response contract, structured output rules, retries/timeouts, rate/cost controls, logging, privacy/data rules, prompt/version strategy, fallback, tests and known fixes.

When AI code becomes stronger in one project, generalize the reusable improvement and update `shared/REGISTRY.md` for other projects. Never copy project-specific secrets/private data/business-only prompts blindly.

### Mandatory execution sequence
READ DOCS -> VERIFY REAL STATE -> CHECK ERRORS -> SEARCH SHARED/OTHER REPOS -> PLAN DEPENDENCIES -> IMPLEMENT -> LOCAL TEST -> DOCUMENT -> COMMIT/PUSH -> DEPLOY FROM GITHUB -> PRODUCTION VERIFY

## UI/UX Shared Library

Before any meaningful UI/UX, Frontend, Admin, Dashboard, Form, Wizard,
Navigation, Table/Card, Empty/Loading/Error state or design-system change, read:
- `docs/library/ui-ux/UI_UX_LIBRARY_INDEX_FA.md`
- `docs/library/ui-ux/UI_UX_ENGINEERING_PLAYBOOK_FA.md`
- `docs/library/ui-ux/UI_UX_PROJECT_ADOPTION_CHECKLIST_FA.md`
- `docs/library/ui-ux/UI_UX_SOURCE_TOPIC_MAP_FA.md`
- `docs/library/ui-ux/UI_UX_SOURCE_MANIFEST_2026-08-29_FA.md`

Rules:
- task/usability/accessibility before decoration;
- preserve the project-specific design system and verified constraints;
- verify RTL/LTR, responsive behavior, keyboard/focus, contrast and loading/empty/error/success states;
- use real operational data, not placeholder status;
- source PDFs/books must not be committed; only derivative project knowledge is stored.
