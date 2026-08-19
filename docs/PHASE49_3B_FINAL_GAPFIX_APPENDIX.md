# Phase49.3B — Final Gapfix Appendix

Status: **CI GREEN / Windows live-provider + visual QA pending / Production untouched**

Branch:
`epic/phase49-unified-product-slider-sync`

Clean runtime/test baseline before this documentation commit:
`c0ac5a9f98e157a5a50b6e1cf8021265a6246e28`

Final validation:
- Workflow: `Phase49 Epic Unified CI`
- Run: `32248104376`
- Job: `96052943408`
- Compile: PASS
- Django check + migration contract: PASS
- Phase49 targeted Django/Bridge/Hero/Profile tests: PASS
- Windows Catalog Center AI/Wizard/Diagnostics tests: PASS
- Full Django suite: PASS

> Live provider tests are intentionally a Windows Local QA gate because real AvalAI/OpenRouter/OpenAI credentials are not placed in GitHub CI.

---

## 1. What this appendix closes

The original Phase49.3B implementation already contained the seven-stage Wizard, Hero Media Studio, provider cards, OpenRouter support, AvalAI compatibility fallback and persistent diagnostic tables. The final gap audit found three remaining persistence/operational gaps:

1. Hero media framing values were durable on `HomepageHeroSlide`, but could be lost before a product was actually enabled in the homepage slider.
2. Program/AI logs had persistent rows but operator/workstation/session were not dedicated searchable columns.
3. Provider-returned USD request cost was visible in runtime UI but was not guaranteed to persist a Toman conversion in SQLite.

This appendix records the additive fixes for those three gaps.

---

## 2. Hero media presentation is now Product-profile persistent

New runtime module:
`store/phase49_3b_profile_media.py`

New additive Store migration:
`store.0032_phase49_slider_media_profile`

Dependency:
`store.0031_phase49_rich_material_colors`

Fields added to `ProductCatalogProfile`:
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

The migration is AddField-only. No DROP, DELETE, TRUNCATE, RESET, RunSQL or data rewrite.

Why this is needed:
A Windows operator can prepare the Hero framing while `homepage_slider_enabled=False`. Those values now remain attached to the product profile and are available later when the slide is enabled.

---

## 3. One media contract in Windows, Product Profile, Hero and Admin

Windows source of truth values remain the same Stage-6 fields.

Sync chain:

`Windows Product → Batch → ProductCatalogProfile → HomepageHeroSlide → Home`

Reverse editing:

`Django ProductCatalogProfile Admin ↔ HomepageHeroSlide Admin ↔ Bridge ↔ Windows`

New/extended modules:
- `store/phase49_3b_profile_media.py`
- `catalog_bridge/phase49_3b_profile_media_contract.py`
- `website/phase49_3b_profile_media_mirror.py`

Important runtime ordering fix:
`phase49_unified_sync` rebinds the mature publish function. Therefore profile-media persistence is installed **after** Unified Sync so the wrapper cannot be overwritten.

Product Profile Admin gets its own `اسلایدر صفحه اول — قاب‌بندی تصویر` fieldset.

The Bridge product profile payload now includes the media fields even when no active Hero exists.

---

## 4. AI providers remain separate first-class cards

Provider Center continues to expose independent cards for:
- AvalAI
- OpenRouter
- OpenAI Direct

Each card has its own API key/model/status/test/balance-cost controls. Keys remain in environment/Windows Credential Store and are never written to SQLite diagnostic logs.

### OpenRouter
- dynamic model list
- `openrouter/free` and `:free` detection
- optional Management Key for credit query
- provider pricing metadata

### AvalAI
- independent API key/model
- credit query when provider endpoint is available
- request ID and transaction-cost lookup
- structured-generation compatibility retry

### OpenAI Direct
- Responses API structured path
- optional Admin Key for organization cost reporting
- ordinary API key is not mislabeled as a remaining-balance source

---

## 5. AvalAI HTTP 400 regression hardening

Reported symptom:
`HTTP 400 / invalid_request`

The provider adapter now treats AvalAI/OpenRouter as OpenAI-compatible gateways rather than assuming every OpenAI parameter is supported.

Structured flow:
1. send Chat Completions with `response_format={"type":"json_object"}`
2. if provider/model returns 400 / invalid_request / unsupported / response_format / parameter semantics
3. retry once without `response_format`
4. parse JSON client-side
5. validate root object before applying content

Regression test:
`test_avalai_structured_400_retries_without_response_format`

This keeps strict structured output for OpenAI Direct while remaining compatible with gateways/models that reject that parameter.

---

## 6. Persistent operator/workstation/session identity

New module:
`catalog_center/app/phase49_diagnostics_identity.py`

Existing SQLite tables are upgraded additively:
- `app_audit_log`
- `ai_request_log`

New columns on both:
- `operator`
- `workstation`
- `session_id`

Operator resolution:
1. Catalog setting `operator_name`
2. `CATALOG_OPERATOR_NAME`
3. current Windows user

Workstation resolution:
1. `COMPUTERNAME`
2. hostname

Session:
one UUID per Catalog Center process/session.

No API key or password is stored in these identity columns.

---

## 7. Persistent Toman request cost

New rule:
If an AI log row contains `cost_usd`, no exact local cost, and `ai_usd_to_toman > 0`, SQLite persists:

`cost_irt = cost_usd × ai_usd_to_toman`

The cost source is marked with `usd_to_toman_rate`.

Priority remains:
1. exact provider-local transaction cost when available
2. provider-returned USD request cost
3. operator-configured USD→Toman conversion

The system does not fabricate a balance or an exact request price when the provider did not expose it.

---

## 8. Diagnostic UI improvements

New module:
`catalog_center/app/phase49_diagnostics_identity_ui.py`

Program Log now shows searchable columns for:
- operator
- workstation
- timestamp
- level
- area/action/status
- product ID
- source file/module
- message

AI Log shows:
- operator
- provider
- model
- operation
- HTTP
- status
- tokens
- cost (Toman if available; USD otherwise)
- Request ID

Actions include:
- refresh
- copy details
- copy Request ID
- export safe diagnostic bundle through the existing Diagnostic Center

The Runs/Logs page also has an operator-name editor and displays workstation/session.

---

## 9. Security and diagnostic sharing

Persistent diagnostics remain sanitized. Secret redaction covers Authorization/Bearer/API key/password/token/secret patterns and structured secret fields.

Diagnostic bundle is intended to be sent to support/assistant for troubleshooting without exposing stored credentials.

Expected debugging chain:

`operator → workstation → session → product → provider/model → operation → endpoint → request ID → HTTP → duration → tokens → cost → sanitized error/response summary`

---

## 10. Migration map for Local QA

Potential pending Local migrations for Phase49.3B:
- `website.0022_phase49_hero_media_presentation`
- `store.0032_phase49_slider_media_profile`

`store.0031_phase49_rich_material_colors` may already be applied from the previous phase; verify actual migration state before running anything.

Always:
1. backup Local Django SQLite and Catalog Center persistent data
2. `python manage.py check`
3. `python manage.py makemigrations --check --dry-run`
4. `python manage.py migrate --plan`
5. apply only expected pending migrations
6. run targeted tests
7. run Windows `launch.py --verify-only`
8. live-provider and visual QA
9. Local Publish one real product only
10. explicit user approval before Production

---

## 11. Final CI gate

CI trigger PR was temporary and must remain unmerged.

Final run validated the clean Epic runtime baseline (the PR head only added a one-line CI marker on the temporary branch):
- Run `32248104376`
- Job `96052943408`
- result: SUCCESS

Production remains untouched.
