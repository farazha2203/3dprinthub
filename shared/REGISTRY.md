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

| Django Engineering Playbook | farazha2203/asal | `shared/django/DJANGO_ENGINEERING_PLAYBOOK.md` | `a463575aaf56eba2d49abf2fb265d208185fe599` | Django 5.2/6.x reference | EXPERIMENTAL | Series 1 derived engineering standard. Verify destination Django/Python/DB/Host before adoption; no automatic upgrade. |
| Django Series 1 Book Index | farazha2203/asal | `shared/django/DJANGO_BOOKS_SERIES_1_INDEX.md` | `7d3d0eb8854e5fbe1043fa747ce8132e5d1bfefe` | Source metadata | EXPERIMENTAL | User archive `django1.zip`, SHA-256 `147df3ae2009133e2b237b924e25c9e832133db46f6dad0e9426c17450d24af1`; books themselves are not copied into GitHub. |
| Django Admin Excellence Blueprint | farazha2203/asal | `shared/django/DJANGO_ADMIN_EXCELLENCE_BLUEPRINT.md` | `4770ad7040ebaac54f202d61aa6f9848d89cb27d` | Django staff/admin UX | EXPERIMENTAL | Process-centric admin UX, guided setup, query/performance, security, audit and accessibility. Verify destination stack/host before adoption. |
| Django Shared Library Index | farazha2203/asal | `shared/django/LIBRARY.md` | `0759de8ec26d9e2ee847d509601d0520994a7059` | Cross-project knowledge | EXPERIMENTAL | Entry point for source archive names/hashes and all derived Django references. |
| Django Series 1 Technique Catalog | farazha2203/asal | `shared/django/DJANGO_TECHNIQUE_CATALOG.md` | `578c4b2fc9a567b095fe9a6470c59d499c6f5d36` | Cross-project Django patterns | EXPERIMENTAL | 100+ techniques tagged ADOPT_NOW / ADOPT_WHEN_NEEDED / VERSION_GATED; destination compatibility check required. |
