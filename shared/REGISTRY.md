# Shared Implementation Registry
Track reusable capabilities to avoid rebuilding from zero.

| Capability | Source Repo | Source Path | Source Commit | Stack | Status | Notes |
|---|---|---|---|---|---|---|
| Auth/Login | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Search all projects first |
| reCAPTCHA/Bot Protection | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Secure fallback |
| SMS/OTP | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Provider adapter |
| Telegram | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Webhook/polling |
| WhatsApp | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Approved API |
| AI Provider Layer | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Reusable abstraction |
| Guided Setup/Wizard | TBD | TBD | TBD | TBD | AUDIT_REQUIRED | Dependency-aware |

Statuses: EXPERIMENTAL / VERIFIED / CANONICAL / DEPRECATED. Record exact source commit and compatibility notes.

## UI/UX Shared Engineering Library

- Type: derivative shared design/UX knowledge (no source PDFs committed)
- Path: `docs/library/ui-ux/`
- Index: `docs/library/ui-ux/UI_UX_LIBRARY_INDEX_FA.md`
- Source manifest: `docs/library/ui-ux/UI_UX_SOURCE_MANIFEST_2026-08-29_FA.md`
- Playbook: `docs/library/ui-ux/UI_UX_ENGINEERING_PLAYBOOK_FA.md`
- Adoption checklist: `docs/library/ui-ux/UI_UX_PROJECT_ADOPTION_CHECKLIST_FA.md`
- Topic map: `docs/library/ui-ux/UI_UX_SOURCE_TOPIC_MAP_FA.md`
- Corpus: owner-provided uiux1.zip, 14 PDFs / 2411 pages; derivative summaries/rules only.
- Use before meaningful UI/UX, frontend, admin, dashboard, form, wizard, navigation, table/card or design-system changes.
- Maturity: SHARED / DOCUMENTATION / REQUIRED BY AGENTS

## Shared Engineering Reference Library

- Type: derivative cross-project engineering knowledge; no copyrighted source PDFs committed.
- Path: `docs/library/engineering/ENGINEERING_REFERENCE_LIBRARY_FA.md`
- Scope: PowerShell/Windows automation, Django ORM/performance, web/app/API security, AI-enabled React/Next.js applications, MySQL and editor-security references.
- Primary sources currently include Afsal MS (Django ORM, 2026), Malcolm McDonald (web app security, 2024), Harwood/Price (web security, 2024), Thomas Lee (PowerShell 7), Theo Despoudis (AI-enhanced web apps, 2026), plus legacy/foundational security references.
- Public companion code registered in the library: `Apress/Mastering-Django-ORM`, `doctordns/Wiley20`, `Generative-AI-Web-Apps/Code`.
- Use rule: real repository/runtime state and current official docs always outrank book examples.
- Security rule: current OWASP/framework/vendor guidance is mandatory for production decisions.
- PowerShell rule: never paste Bash heredoc syntax into native PowerShell; use PowerShell here-strings and verify native-command exit codes.
- Maturity: SHARED / DOCUMENTATION / REQUIRED DISCOVERY VIA AGENTS + REGISTRY.

## Shared Web Engineering Library — 2026-09-01

- Type: derivative cross-project web engineering knowledge; no source PDFs committed.
- Canonical local path: `docs/library/engineering/WEB_ENGINEERING_LIBRARY_2026-09-01_FA.md`.
- Verified corpus: 10 owner-provided PDFs / 4819 pages.
- Frontend additions: **React in Depth** (2024), **Modern Web Applications with Next.JS** (2023), **3D Web Development with Three.js and Next.js** (2025).
- Also covers: AI-enabled React/Next apps, Django ORM/performance, PowerShell automation, current + foundational web security.
- Source locator policy: exact owner File Library filename is recorded in the library; copyrighted PDFs are not committed.
- Visual design companion: `docs/library/ui-ux/UI_UX_LIBRARY_INDEX_FA.md`.
- Rule: actual runtime/lockfile/DB/host + official version docs > book examples.
- Three.js/WebGL: use only after value/performance/SEO/accessibility gate.
- React performance: measure with profiler before memoization/rearchitecture.
- Next.js: verify actual project version/rendering model before version-specific APIs.
- Security: current OWASP/framework/vendor guidance is authoritative.
- Maturity: SHARED / DOCUMENTATION / CROSS-PROJECT REQUIRED DISCOVERY.

