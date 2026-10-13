# Phase50.A2Z — Public social links and shared site footer

Date: 2026-10-13
Status: PRODUCTION_VERIFIED at runtime SHA `dd1d679a9033146849283a7851dceaa6396fa695`.

## Owner correction: existing footer and feedback visibility
- Do not add another footer. Keep the single shared `site-footer.html`.
- Scoped dark-background/light-text CSS is required because global light-theme overrides otherwise make the existing footer appear white and visually blend into the page.
- Hide the testimonials and order-reviews sections completely when their respective querysets are empty; render real feedback above the shared footer.
- Local regression covers empty/populated data and one-footer ordering. Runtime deployed and smoke-verified; rollback: `/home/sfkilvrs/3dprinthub-deploy-backups/20261013-180246-phase50-a2w-service-seo`.

## Requested delta
- Make the configured WhatsApp number a `wa.me` link and show Instagram in the desktop header, mobile menu, contact section, and a consistent footer. Prefer `SiteSetting.instagram`, then an Instagram URL from SEO `same_as`, then the already owner-verified `@3dprinthub_ir` Organization-schema profile.
- Render the same footer on Home, Store, authenticated customer-account pages, customer login/registration/password-reset pages, and customer order detail.
- Normalize Iranian WhatsApp numbers entered as local `09…`, international `+98…`, or international-prefix `0098…` without exposing or hard-coding a number.

## Touched surfaces
- `website/context_processors.py`
- `templates/website/partials/header.html`
- `templates/website/partials/contact.html`
- `templates/website/partials/site-footer.html`
- `templates/website/index.html`
- `templates/store/base.html`
- `templates/website/customer/account_base.html`
- Standalone customer login, registration, order-detail, and password-reset templates.
- `website/tests.py`
- A2W guarded deployment runner and public smoke/contract tests.

## Must not touch
- No social posting, Instagram API, credentials, Search Console, SEO metadata/schema, Product/catalog/media, orders, database rows, migrations, Host environment, or payment/shipping behavior.
- Preserve the A2W/A2Y SEO runtime and existing Production Host branch; promotion must be fast-forward from its exact verified SHA.

## Production read-only finding
- The current Host has a WhatsApp value in `SiteSetting`; its `SiteSetting.instagram` and SEO `same_as` fields are blank. The existing Organization schema already emits the owner-verified `https://www.instagram.com/3dprinthub_ir/` profile. The UI uses that established public identity as a fallback and performs no Host DB write.

## Local verification
- Home/social/footer focused regression: 8/8 PASS.
- Django check: PASS with existing CKEditor 4 support and in-memory channel-layer warnings.
- `makemigrations --check --dry-run`: no changes.
- Guarded runner contract: 7/7 PASS; Python compile, Bash syntax, and diff hygiene PASS.
- Production release SHA `d196edc6a3dffc54add147a9d4b4c7cf49b62895` passed guarded deploy. Exact Host rollback root: `/home/sfkilvrs/3dprinthub-deploy-backups/20261013-162447-phase50-a2w-service-seo`; source, `.env`, full MySQL backup, SHA256 and gzip validation passed.
- Runner output confirmed zero migrations, ff-only source promotion, Django checks with only pre-existing warnings, Passenger restart, clickable social/contact shell on Home and Store, and all eight service landing routes.
- No social posting, credential, Search Console, Product, order, media, or Production DB-data change occurred.

## Release and acceptance
- Host baseline: `f9d7968d0e157326bff3c060cfa67230432b91ac`, branch `release/phase50-a2j-hero-20260915`.
- GitHub release branch: `release/phase50-a2w-service-seo-20261010`.
- Deploy only with `scripts/host/phase50_a2w_service_seo_deploy.sh`, passing the fresh verified Host baseline as its second argument and the exact live GitHub release SHA as its first.
- `PRODUCTION_VERIFIED` after the runner's quota/reserve, MySQL identity, empty migration plan, verified source/env/database backup, fast-forward, restart, and live Home/Store social-link smoke all passed.
