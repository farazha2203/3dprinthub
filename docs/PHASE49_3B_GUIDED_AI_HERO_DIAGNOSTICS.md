# Phase49.3B — Guided Publish Wizard + AI Provider Hub + Hero Media Studio + Diagnostics

Status: **GitHub CI GREEN / Windows live-provider and visual QA pending / Production untouched**

Branch:
`epic/phase49-unified-product-slider-sync`

Final tested runtime baseline before documentation:
`777ebf6596f2f839678d132ade638d91f9a7ed84`

Final CI:
- Run: `32241999276`
- Job: `96034394939`
- Compile: PASS
- Django check + migration contract: PASS
- Phase49 targeted Django/Bridge/Hero: PASS
- Windows Catalog Center tests: PASS
- Full Django suite: PASS

> Provider tests in CI are contract/mock tests. Live AvalAI/OpenRouter/OpenAI tests require the operator's real key on Windows and are a Local QA gate before production.

---

## 1. Goal

Phase49.3B turns Product Workspace into a guided publishing flow and removes three operational risks:

1. employees no longer need to guess which product fields block publishing;
2. Hero images can be framed consistently instead of becoming too large/cropped;
3. AI requests become provider-aware, cost-aware and diagnosable instead of failing with an opaque message box.

Production is not changed by this phase until Local Windows approval.

---

## 2. Seven-stage Product Wizard

Canonical stages:

1. `اطلاعات پایه`
2. `سفارش، قیمت و گزینه‌ها`
3. `تصاویر`
4. `محتوا و SEO`
5. `منبع و مجوز`
6. `اسلایدر صفحه اصلی`
7. `بررسی و انتشار`

Visual states:
- `✅` stage complete
- `❌ ★` current/incomplete required stage
- `🔒` future locked stage

Every stage has a fixed bottom navigation contract:
- `← مرحله قبل`
- `مرحله بعد برای انتشار →`
- final stage changes Next to `💾 ذخیره نهایی`

The Next button is disabled until the current stage's required fields pass Readiness.

Each stage displays human-readable requirements at the bottom. Missing required items are prefixed with `★`.

### Stage-specific AI

Stage 1 includes:
`✨ ترجمه فقط عنوان فارسی`

This structured request only returns `title_fa`; it must not silently rewrite price, descriptions or SEO.

Stage 4 owns full product content/SEO generation.

Stage 6 owns dedicated Slider SEO + media + effect/timing.

---

## 3. AI Provider Hub

The old single shared provider box is replaced by independent provider cards.

### AvalAI card
- independent API key
- model list/model selection
- live connection test
- credit/balance query
- request logging
- transaction cost lookup by request/request-transaction ID

AvalAI structured generation uses OpenAI-compatible Chat Completions. If a gateway/model rejects `response_format` with HTTP 400/invalid-request/unsupported-parameter semantics, the client retries once without `response_format` and validates/parses the returned JSON itself.

This is the compatibility path introduced for the reported AvalAI `HTTP 400 invalid_request` regression.

### OpenRouter card
- independent API key
- model metadata from Provider adapter
- free model detection (`:free` / free router contract)
- independent model selection
- live connection test
- request usage/cost logging
- optional Management Key for account credit query

### OpenAI Direct card
- independent API key
- model selection
- direct structured Responses API path
- live connection test
- optional Admin Key for organization cost reporting

An ordinary OpenAI API key is not presented as a remaining-balance source. The UI labels optional Admin-Key data as recent organization cost, not credit balance.

### Auto/provider selection

The active Product Workspace provider is explicit. `auto` only considers providers that actually have a usable key.

OpenRouter/AvalAI/OpenAI keys remain in Windows keyring/environment-compatible secret storage. They are not stored in SQLite audit logs.

---

## 4. AI cost model

`ai_request_log` stores:
- provider
- model
- operation
- endpoint
- request ID
- HTTP status
- duration
- prompt/completion/total tokens
- USD cost when returned
- IRT/Toman cost when available
- cost source
- product ID
- sanitized request/response summaries
- error text

Cost resolution priority:
1. exact provider-side local currency transaction cost when available (e.g. AvalAI lookup)
2. provider-returned USD request cost
3. approximate Toman conversion using the operator's configured USD→Toman rate

The UI never invents a provider balance. Unsupported balance APIs are displayed as unavailable with a reason.

---

## 5. Persistent diagnostic and audit log

Catalog Center SQLite gains additive internal tables:

### `app_audit_log`
Tracks:
- timestamp
- level
- area
- action
- status
- product ID
- source module/file
- operator-safe message
- sanitized structured detail

### `ai_request_log`
Tracks request/response execution metadata listed above.

Hooks cover:
- Product DB updates (changed field names, not sensitive raw values)
- Product history events
- AI request success/failure
- Tk callback exceptions
- runtime startup
- diagnostic exports

The Windows navigation item `گزارش و خطا` is renamed to `لاگ برنامه`.

New Log Center actions:
- `لاگ دیتابیسی برنامه`
- `درخواست‌های AI`
- `تکمیل هزینه AvalAI`
- `خروجی گزارش عیب‌یابی`

Diagnostic export path:
`<Catalog persistent data>/diagnostics/catalog-diagnostic-YYYYMMDD-HHMMSS.json`

The export is intended to be shareable for support/debugging.

### Secret redaction

Redaction covers:
- Bearer tokens
- Authorization headers
- API keys
- password/token/secret JSON fields
- `key=value` secret forms

A CI regression test intentionally injects fake secrets and asserts they never appear in persisted/exported logs.

---

## 6. Hero Media Studio — Windows

Stage 6 is a dedicated `اسلایدر صفحه اصلی` page.

Content fields reuse the mature Slider variables:
- enabled
- selected Hero image
- sort order
- title FA
- description FA
- image Alt
- button text
- focus keyword
- effect
- transition duration
- display duration

New persistent media controls:
- `presentation_mode`
  - `product_fit` — نمایش کامل محصول
  - `full_bleed` — پر کردن کامل اسلایدر
  - `framed` — کادر محصول
  - `cinematic` — سینمایی با پس‌زمینه
- `object_fit`: contain/cover
- focal position
- image scale percent
- X position percent
- Y position percent
- background mode: solid/blur/gradient/image
- background color
- background blur px
- desktop max width/height percent
- mobile max width/height percent

Default product-safe presentation is `product_fit + contain`.

The Windows workspace includes a local `Desktop/Mobile` preview using the selected local Hero image.

---

## 7. Windows SQLite Hero columns

Added additively to `products` by `phase49_3b_guided_wizard.ensure_schema()`:

- `homepage_slider_presentation_mode`
- `homepage_slider_object_fit`
- `homepage_slider_focal_position`
- `homepage_slider_image_scale_percent`
- `homepage_slider_position_x_percent`
- `homepage_slider_position_y_percent`
- `homepage_slider_background_mode`
- `homepage_slider_background_color`
- `homepage_slider_background_blur_px`
- `homepage_slider_desktop_max_width_percent`
- `homepage_slider_desktop_max_height_percent`
- `homepage_slider_mobile_max_width_percent`
- `homepage_slider_mobile_max_height_percent`

No product rows are deleted or reset.

---

## 8. Django database migration

New migration:
`website.0022_phase49_hero_media_presentation`

Adds to `HomepageHeroSlide`:
- `presentation_mode`
- `image_scale_percent`
- `image_position_x_percent`
- `image_position_y_percent`
- `background_mode`
- `background_color`
- `background_blur_px`
- `desktop_max_width_percent`
- `desktop_max_height_percent`
- `mobile_max_width_percent`
- `mobile_max_height_percent`

Migration is additive only.
No DROP/DELETE/TRUNCATE/RESET.

Runtime validators and migration state are aligned; CI `makemigrations --check --dry-run` is green.

---

## 9. Django Admin Hero media

The existing HomepageHeroSlide Admin `۲. تصویر Hero` fieldset now also exposes:
- presentation mode
- object fit/focal
- scale
- X/Y position
- background mode/color/blur
- desktop/mobile max dimensions

The settings remain editable from either Windows or Django Admin.

---

## 10. Desktop → Django media sync

Existing `store.epic49_publish_options.apply_homepage_slider()` remains the mature creation/update path.

`store.phase49_3b_hero_media_sync` wraps it additively:
1. mature publish creates/updates the same slide
2. media presentation values are validated/bounded
3. the same HomepageHeroSlide is updated

No parallel Hero model or duplicate publish path is created.

---

## 11. Catalog Bridge media contract

Existing Hero read/detail/sync endpoints are extended; no parallel endpoint is introduced.

`catalog_bridge.phase49_3b_media_contract`:
- extends slide serialization with media fields
- accepts media fields on existing Hero sync
- preserves Bearer auth, revision and 409 conflict semantics

Windows `ServerSliderManager` gains `تنظیم قاب تصویر Hero` for an existing server slide and uses the same revision-aware Bridge update.

---

## 12. Public Hero rendering

`templates/website/partials/hero.html` loads:
`static/css/phase49_3b-hero-media.css`

Each slide renders CSS/data variables for:
- presentation
- background
- blur
- scale
- X/Y
- desktop/mobile bounds

Presentation behavior:
- product_fit: contained product inside controlled max bounds
- full_bleed: cover/full-frame behavior
- framed: contained product with visual frame/shadow
- cinematic: product with background treatment/shadow

The existing Phase49.2C cinematic transition engine remains intact.
The Persian Sales Hero copy/2-line expandable description remains intact.

---

## 13. Files introduced/updated

New major files:
- `catalog_center/app/phase49_diagnostics.py`
- `catalog_center/app/phase49_diagnostics_ui.py`
- `catalog_center/app/phase49_ai_provider_hub.py`
- `catalog_center/app/phase49_3b_ai_product_runtime.py`
- `catalog_center/app/phase49_3b_ai_runtime_patch.py`
- `catalog_center/app/phase49_3b_guided_wizard.py`
- `catalog_center/app/phase49_3b_server_slider_media.py`
- `catalog_center/tests/test_phase49_3b_ai_diagnostics.py`
- `catalog_center/tests/test_phase49_3b_guided_wizard.py`
- `website/migrations/0022_phase49_hero_media_presentation.py`
- `website/phase49_3b_hero_media.py`
- `website/test_phase49_3b_hero_media.py`
- `store/phase49_3b_hero_media_sync.py`
- `catalog_bridge/phase49_3b_media_contract.py`
- `static/css/phase49_3b-hero-media.css`

Updated integration files include:
- `catalog_center/launch.py`
- `catalog_center/app/ai_providers.py`
- `catalog_center/app/openai_content.py`
- `website/apps.py`
- `store/apps.py`
- `catalog_bridge/apps.py`
- `templates/website/partials/hero.html`
- `.github/workflows/phase49-epic-ci.yml`
- `.env.example` (names only, no real keys)

---

## 14. Test history

First Phase49.3B CI exposed a real secret-redaction defect:
- Bearer tail and quoted JSON secret values could remain visible in one pattern.
- runtime sanitizer was fixed; the test was not weakened.

Final tested baseline:
`777ebf6596f2f839678d132ade638d91f9a7ed84`

Final CI:
- Run `32241999276`
- Job `96034394939`
- all steps SUCCESS.

---

## 15. Local gate

Before Windows visual/live AI QA:
1. pull Epic
2. backup Django SQLite and Catalog Center persistent data
3. `python manage.py check`
4. `python manage.py makemigrations --check --dry-run`
5. `python manage.py migrate --plan`
6. expect `website.0022_phase49_hero_media_presentation` if not yet applied
7. apply only after backup
8. run targeted Phase49.3B Django + Windows tests
9. `python launch.py --verify-only`
10. launch Windows app
11. visually test seven stages/locks/previous/next/stars
12. test each AI card with real key separately
13. test AvalAI content generation that previously returned HTTP400
14. test OpenRouter model list + one free model if currently available to the account
15. inspect AI request log / cost / Request ID
16. export a diagnostic bundle
17. test Hero Desktop/Mobile preview
18. Local Publish one real product only
19. verify Store/Home/Admin locally
20. explicit user approval required before Production.

---

## 16. Portable/employee release

The source/developer Windows runtime is the current Local QA target.
The final employee Portable/EXE packaging remains a separate gate after Local visual/live-provider approval. Local-test publishing must not be unintentionally exposed as a production employee action.

---

## 17. Production

**NOT DEPLOYED / NOT APPROVED.**

Do not run production migration `website.0022`, collectstatic or restart until Local QA and explicit user approval.
