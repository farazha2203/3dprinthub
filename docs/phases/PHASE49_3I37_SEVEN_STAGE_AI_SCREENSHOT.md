# Phase49.3I.37 — Seven-stage AI Orchestrator, Operator Finalization and Screenshot-to-Site SEO

Updated: 2026-08-27  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Catalog Center: `8.9.5` / build `2026.08.27.7`  
Tested runtime SHA: `8d5e58a839c89eedbe258d9236889834fc02d9a9`  
Status: `GITHUB CI + WINDOWS PORTABLE PASS / OWNER LOCAL VISUAL QA NEXT / PRODUCTION UNTOUCHED`

## Goal

Finish the owner-requested Product workflow without allowing AI or generic Save actions to erase operator work.

The canonical seven stages remain:

1. اطلاعات پایه,
2. سفارش، قیمت و گزینه‌ها,
3. تصاویر,
4. محتوا و SEO,
5. منبع و مجوز,
6. اسلایدر صفحه اصلی,
7. بررسی و انتشار.

Each stage now has two separate states:
- **data complete**: shown as `✅ کامل؛ منتظر ثبت` when readiness rules are satisfied,
- **operator finalized**: shown as `🔒 نهایی` only after the operator presses `ثبت`.

AI may make a data-complete stage green/check-ready, but AI never creates the operator finalization lock.

## Durable stage lock contract

`phase49_3i36_stage_finalization.py` persists `operator_stage_locks_json` in Catalog SQLite.

- `ثبت` persists the stage lock.
- `اصلاح` explicitly removes that lock.
- the final `Database.update_product()` wrapper blocks every field owned by a locked stage.
- both Profile transports are Commerce-owned and protected:
  - `sales_profile_ledger_json`,
  - `sales_profiles_json`.
- AI never owns Profile, price, material/color, filament brand, stock or publish approval even when those stages are unlocked.
- source/license policy cannot be bypassed by a manual SEO/content approval.

The legacy plural `sales_profiles_json` transport missing the Commerce classification was exposed by the new regression gate and fixed before release. See `ERR-49-061`.

## One persisted AI source mode

Settings now has one mother Product translation/SEO source:

- `link` — لینک واقعی محصول,
- `data` — دیتای ذخیره‌شده محصول,
- `screenshot` — اسکرین‌شات صفحه محصول.

The setting key is `ai_product_source_mode`.

Single-Product and selected-Product Bulk AI both use this same persisted source authority. The older per-run four-mode selector is no longer the visible operator boundary.

"Repair" is no longer a fourth source of truth. The orchestrator uses the configured source and fills only missing/invalid fields in unlocked stages.

## Seven-stage AI orchestrator

`phase49_3i37_seven_stage_ai.py` is the final Product AI UX/runtime boundary.

For a successful Product attempt it:
1. resolves the configured source once,
2. generates one structured editorial Content Pack,
3. validates the Persian identity/SEO contract,
4. applies only missing/invalid fields stage by stage,
5. re-evaluates readiness after each stage,
6. skips every locked stage,
7. reports `✅` when data is complete,
8. leaves operator-only gaps visible instead of inventing values.

Commerce and Publish are review-only for AI:
- no Profile write,
- no price write,
- no material/color/brand write,
- no stock write,
- no sale/publication approval.

Existing 3I.35 preflight/retry/configured fallback behavior remains the provider execution policy.

## Persian translation and SEO quality

The owner log showed that Product 303 could receive a semantic title in one run and then a transliterated/mixed-language SEO identity in another. 3I.37 therefore validates Product identity and Persian SEO as one contract.

For source `Twistmas Tree` the canonical Product identity is:
`درخت کریسمس اسپیرال`.

The guard rejects/repairs:
- `تویست‌ماس تری` as the Product identity,
- an SEO title that reintroduces the English/transliterated identity,
- Cyrillic contamination,
- unrelated free-floating Latin prose in the key Persian SEO fields.

Real brand/model/technical tokens are still allowed where justified.

Material recommendations and internal category reassignment remain outside AI business authority.

## Image AI ownership

Image operations are intentionally split:

- deterministic image tools own file rename / SEO filename / WebP generation / embedded metadata,
- AI may supply image Alt/Title/Caption/keywords only when image SEO is incomplete,
- if selected image SEO is already complete, no image AI request is required,
- image stage lock blocks AI and Screenshot mutation.

When content/SEO is also being repaired, image metadata finalization is deferred until the final content signature is stable. This prevents the old immediate-stale metadata problem.

## Screenshot → site image contract

The Product Images panel action is now:
`📸 اسکرین‌شات + افزودن به تصاویر سایت`.

On click:
- the real Product source page is captured with the existing browser acquisition path,
- the PNG is stored under the Product local image area,
- it is added to `images_json`,
- it is added to `selected_images_json`,
- an existing primary image is preserved; Screenshot becomes primary only when no primary exists,
- deterministic image finalization generates the WebP/SEO metadata,
- the image metadata preserves `source_page_url` pointing to the original Product page,
- a full selected-image list still guarantees the Screenshot is included by dropping only the final non-Screenshot slot when necessary,
- locked Images stage fails closed until the operator presses `اصلاح`.

The batch editorial transport already carries `image_metadata_json` and the Product source URL, so this uses the mature publish path instead of introducing a separate upload protocol.

## Verification

Tested runtime SHA:
`8d5e58a839c89eedbe258d9236889834fc02d9a9`

Targeted:
- workflow: `Phase49.3I.31-37 Stage Finalization + Operator Ledger CI`,
- run: `33074245603`,
- result: PASS,
- 77 tests PASS,
- 3I.36 lock regressions PASS,
- 3I.37 source/orchestrator/SEO/Screenshot regressions PASS,
- final composition/launcher markers PASS.

Single Active AI:
- run `33074245489`,
- result PASS.

Windows Portable:
- run `33074245604`,
- result PASS,
- version `8.9.5`,
- build `2026.08.27.7`,
- artifact `3DPrintHub-CatalogCenter-v8.9.5`,
- artifact ID `9647216177`,
- EXE size `65,494,809` bytes,
- EXE SHA256 `4a3e15a3c475460c2dac035cedcd8ccebb40107fec6360b7be6a313f69186079`,
- artifact ZIP digest `sha256:393b4464a9503fd4fabd75b5f81c1621c0736b0dbe1f2d0c7df92c22c414ab34`,
- browser smoke PASS,
- portable self verify PASS,
- source URL preservation gate PASS.

Known non-blocking warning debt:
- Pillow `Image.getdata()` deprecation,
- one historical ResourceWarning in a source-reading test.

## Rollback

Git rollback branch before 3I.37:
`backup/pre-phase49-3i37-seven-stage-ai-screenshot-20260827` → `fa2922f01eb901aa981f80e7b3fc605acf60904d`.

Earlier 3I.36 rollback:
`backup/pre-phase49-3i36-stage-finalization-locks-20260827` → `a380f83406607d0da4db0aa2a029146edba19f30`.

These are source rollback anchors only. Production backup requirements remain unchanged.

## Production state

Production was not touched.

Last terminal-verified Production application remains:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified Production Phase50 migration state remains only:
- `store.0034_phase50_variant2_commerce`,
- `store.0035_phase50_sales_profiles`.

Do not infer that `0036..0039` are applied without a fresh Host read-only audit.

## Exact next step

Owner Local visual/functional QA on canonical Windows checkout is required before Host audit.

Required acceptance:
- Settings shows exactly Link / Saved Data / Screenshot source modes and persists after restart.
- Product AI surface shows one seven-stage missing-only action.
- Product 303 / Twistmas title and SEO stay semantic Persian.
- each completed stage shows `✅`; pressing `ثبت` changes it to `🔒`.
- AI rerun leaves locked Quick/Content/Profile/Commerce unchanged.
- `اصلاح` reopens only the chosen stage.
- registered Profiles survive every AI run.
- Screenshot action adds a visible selected site image, keeps existing primary when present, generates SEO metadata and preserves the source-page link.
- image rename remains a separate deterministic image action.
- Bulk selected Products use the same persisted source mode and do not globally rebuild Products Explorer.

Only after this owner QA PASS:
Host read-only verify → fresh backups → explicit `FETCH_HEAD` deploy → actual pending migration plan/apply → collectstatic → Passenger restart → Production verification.
