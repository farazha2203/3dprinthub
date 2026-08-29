# Phase49.3I.40 — Commerce Precision, Offer Ownership and Readiness Truth

Updated: 2026-08-29  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Catalog Center: `8.9.8` / build `2026.08.29.2`  
Runtime/packaged candidate: `55139b909f214f33994d76bc1e6fdfd028b5d6c7`  
Status: `BASELINE CI PASS / ERR-49-070 OWNER 67/67 PASS BUT VISUAL FAIL / ERR-49-071 EXPLICIT STAGE CONFIRMATION FIX GITHUB / OWNER LOCAL RETEST NEXT / PRODUCTION UNTOUCHED`

## ERR-49-071 operator-confirmation truth and targeted UX rollback

Owner foreground acceptance on `d4da997...` invalidated the previous visual contract despite 67/67 automated PASS. Final phase truth is now:
- field population and operator confirmation are distinct;
- real missing Product data is `missing_data`;
- complete stages awaiting approval are `pending_finalization`, not defects;
- the rail uses `❌` for data-incomplete, `◌` for complete/waiting-confirmation and `✅` only after explicit confirmation;
- the stable operator action is an independent permanent `✅ ثبت و تأیید مرحله →` button, not a mutation of the legacy Next widget;
- Stage 1 returns to title/category only; existing product type/dimensions/use-case controls stay in Stage 2;
- the ERR-49-069/070 additive relocation panels are not mounted;
- explicit `external-other / سایر محصولات` is valid;
- title-only AI must pass through the same global one-Product-AI guard and OpenRouter-only path.

This changes no Stage-2 Offer/Profile/pricing business contract, crawler/acquisition, media, Django schema/migration or Production state.

Rollback: `backup/pre-err49-071-stage-confirm-rollback-20260829` → `d4da99744659d06ebe5c04fd69532cd0e03db3e8`.

## ERR-49-070 Stage-5 clean-schema/visible-contract correction

Owner Local gate on `382a34fa6e876dc7098c8152c98c7cb076d508e8` passed compile and the 4 OpenRouter-only contracts, then stopped the 67-test Windows suite before launch on two source omissions:
- clean temporary Catalog SQLite lacked `technical_summary_fa`;
- 3I.39 referenced `add_specs_contract_panel` / `refresh_specs_contract` but their implementations were absent.

The phase contract now includes one complete Stage-5 chain:
`clean schema -> visible Stage-5 controls -> persisted hydrate -> stage-specific save/finalize -> readiness`.

Visible Stage 5 now owns:
- source URL (existing top control),
- source/designer,
- Persian commercial-license selector,
- Persian technical summary,
- technical-features JSON.

The Persian selector is converted back to the canonical stored license code during Stage finalization. No Stage-2 commerce, crawler, media, Provider policy, Django schema, Host or Production boundary changed.

Rollback: `backup/pre-err49-070-stage5-schema-panel-20260829` -> `382a34fa6e876dc7098c8152c98c7cb076d508e8`.

Owner Local rerun of the same 67-test gate is mandatory.

## ERR-49-069 final Windows interaction contract

Owner foreground evidence on `3f43260...` passed compile + 60/60 focused tests but still reproduced a final-composition failure. The phase therefore adds these acceptance rules without changing Stage-2 commerce authority:

- every late/previously-captured guided-Wizard refresh must finish by restoring the final `✅ تأیید و مرحله بعد →` action;
- Stage confirmation persists the current Stage before checking readiness, finalizes only when that persisted state passes, then advances;
- Stage 1 visibly owns Product type, dimensions and use-case/class in addition to title/category;
- Stage 5 visibly owns source/designer, commercial license, technical summary and technical-features JSON;
- stage-specific persistence covers the restored Stage-1/5 controls;
- stage-scoped AI counts only defects in its requested Scope; whole-product AI retains global defect truth;
- only one Product AI job may be active in the application process;
- Product AI uses OpenRouter only. Primary is the exact saved OpenRouter model; optional resilience is `openrouter/free` on the same Provider/key. AvalAI, Google and OpenAI are excluded from Product-AI fallback;
- the existing Link / Saved-Crawled Data / Screenshot source contract is unchanged;
- Stage 2 Offer/Profile/pricing, acquisition and Store transport contracts remain unchanged.

Executable-code hotfix head: `136011971dea907ac777b3e66190dd27982a0c38`. Rollback: `backup/pre-err49-069-stage-contract-openrouter-only-20260829` → `3f43260db669b458a682f594b5d50eb5221b9ef3`. Owner Local retest is pending; Production untouched.

## Requested delta

Stage 2 must behave as one professional commerce workflow rather than duplicate pricing/profile forms:

1. manufacturer/company → filament/material → color → register Product Offer,
2. edit global Offer facts: stock, roll weight, purchase/sale/USD+explicit FX, hourly print/supervision, preheat hours/temperature/hourly cost and optional filament image/HEX,
3. pricing mode after Offer selection:
   - fixed price is Product-specific per exact Offer,
   - formula pricing consumes exact Offer facts and production time/weight,
   - range pricing remains available but is not the current operator focus,
4. production rows own product weight / print time / support weight,
5. Profile registration at the bottom owns only Profile identity + size label + actual part L/W/H; registering creates an immutable snapshot and later registrations must not mutate older Profiles,
6. same material/color across Bambu Lab/eSUN/other manufacturers remains distinct,
7. customer Storefront selects manufacturer → material → color and price/availability follows that exact selection,
8. color UI shows filament image when available, otherwise a swatch from explicit HEX or safe name fallback,
9. Link completion must report request/response/apply/readiness before/after and must never show 100% while AI-fixable defects remain,
10. stage data readiness and operator finalization are distinct states.

## Must-not-touch boundary

The mature acquisition path remains authoritative and was not replaced:
- browser/profile setup,
- listing/direct-link discovery,
- parser,
- image/file acquisition,
- `discovered_urls` identity ledger,
- rejection tombstones and continuation cursor from 3I.38,
- exact source URL preservation,
- one configured AI Provider/Model/key boundary,
- existing StoreOrder/Payment/Invoice/Coupon/VAT/inventory behavior.

3I.40 extends/wraps the final commerce/readiness boundary.

## Stage-2 Offer selection precision

`merge_offer_scope()` replaces only the currently visible manufacturer/material scope. Offers selected under other filters are preserved.

Example:
- register `Bambu Lab / PLA / White`,
- switch to `eSUN / PLA / Multicolor`,
- register the second scope,
- both Product Offers remain selected.

Deselecting the current filter removes only that visible scope and does not erase another manufacturer's Product Offer.

## Global Offer facts vs Product fixed price

Global filament facts belong to the exact manufacturer/material/color Offer:
- manufacturer / brand,
- material,
- color,
- HEX / optional filament image,
- roll weight,
- current stock,
- purchase price,
- sale price,
- USD price + explicit FX,
- print hourly rate,
- supervision hourly rate,
- preheat hours,
- preheat temperature,
- preheat hourly cost.

A fixed sale price for a Product using that Offer is a Product-owned value and is edited in a dedicated Product fixed-price editor. Changing it does not mutate the global roll/rate facts.

## Color preview

Operator and Storefront use:
1. filament image if configured where the surface supports it,
2. explicit valid HEX,
3. Persian/English color-name fallback,
4. neutral fallback if no color fact is known.

No hidden network fetch is required merely to open the Product workspace.

## Readiness truth

Stage rail separates:
- real missing data defects,
- complete data waiting for operator finalization,
- operator-finalized/locked stages.

The 3I.40 completion proxy suppresses internal cosmetic 100% events. Whole-product Final 100% requires global `ai_fixable_count == 0`; a deliberately stage-scoped run may complete at 100% when `scoped_ai_fixable_count == 0` even if unrelated Stages still contain defects.

If AI-fixable defects remain after bounded passes/retry/fallback:
- progress stops below 100 (94% contract),
- remaining AI-fixable defects are emitted in diagnostics,
- remaining data defects are emitted separately,
- the operator is not told the Product is complete.

AI source choices remain exactly:
- Link,
- Saved/Crawled Data,
- Screenshot.

Repair is an operation on the same engine, not a fourth source.

## Screenshot contract

Product-page screenshot selected for the Product/Site is the top viewport reference, not a full-page capture. Mature acquisition/browser internals remain unchanged.

## Store / Phase50 extension

Migration:
`store.0040_phase50_filament_offer_operations`

Adds to `MaterialColorOption`:
- `print_hourly_rate`,
- `supervision_hourly_rate`,
- `preheat_hours`,
- `preheat_temperature_c`,
- `preheat_hourly_rate`,
- `filament_image_url`.

The Store selector and Variant metadata keep exact manufacturer/material/color identity, stock, preheat and visual facts.

## Windows stage-confirmation recovery — ERR-49-068

Owner rerun after ERR-49-067 passed the full focused 43-test set and launched the canonical 8.9.8 source, but foreground Product 63 still demonstrated the user-facing deadlock: manually complete Stage 1 values could not become a usable confirmed/advanced step because the mature footer Next path evaluated persisted readiness before persisting the current UI, while the later 3I.36 `ثبت` action lived in a separate rail panel rather than the fixed bottom workflow the operator previously used.

Final Windows interaction contract now requires:
1. the fixed footer always exposes `✅ تأیید و مرحله بعد →`,
2. clicking it persists only the current Stage through 3I.36, evaluates readiness, finalizes on success, then navigates to the next Stage,
3. the footer also exposes `✨ پرکردن ناقص‌ها با AI` and `✏ اصلاح مرحله`,
4. later Wizard refreshes must not replace the confirm command with the old read-before-save Next command,
5. already-created legacy Tk AI buttons are explicitly rebound across the full Workspace to the final 3I.39 engine,
6. real source identity tokens may remain beside Persian title/description/SEO text, while unrelated Latin remains invalid; keyword/tag/hashtag editorial lists remain Persian-controlled,
7. fallback key/model identity is Provider-specific,
8. deferred error callbacks freeze exception text before leaving the `except` scope.

Observed owner runtime evidence also showed the Provider path problem clearly: OpenRouter produced empty output, AvalAI generated structured output rejected by the over-strict identity rule, and an OpenRouter-shaped credential/model was later attempted as OpenAI and returned 401. Those cross-provider attempts are now filtered rather than treated as useful fallback.

Rollback:
`backup/pre-err49-068-windows-stage-confirm-20260829` → `0191a07f980d3cf5ba48ed1379a1c9da98c39e1b`.

No Stage-2 Offer/Profile pricing contract, crawler/parser, media file, Django schema/migration, Host or Production boundary changed. Owner Local regression + foreground Product 63 confirmation/AI test remains mandatory.

## Local regression fixture correction — ERR-49-067

Owner Local evidence after pulling `9f3b765...`:
- canonical branch/head verified,
- fresh Catalog SQLite backup + checksum created,
- Python compile PASS,
- focused suite: 43 tests, exactly 1 error,
- foreground launch correctly blocked by the gate.

The failing lock/immutability test used an invalid mock AI SEO description containing Latin `AI`. Since this phase now deliberately keeps SEO title/description Persian-only, validation correctly failed before lock behavior was reached. Runtime rules remain unchanged; the fixture alone was aligned at `38cb415bc12d7ec08943809fd14f3478b3ddac1b`.

Rollback: `backup/pre-err49-067-seven-stage-test-fixture-20260829` → `9f3b765e28f9b9adda1e7713dbc48c1255a52c1c`.

Owner must rerun the same focused gate on the current docs-final head before foreground Product 63 acceptance.

## Readiness ownership correction — ERR-49-066

Owner foreground evidence after ERR-49-065 proved that repaint synchronization alone was insufficient. The data had been persisted, but the contract still allowed one defect to be classified in a Stage that could not write its owning field, and the guided wizard treated operator finalization as data incompleteness.

Final readiness contract is now:
1. every required persisted field has one Stage owner,
2. `title_fa` belongs to Quick,
3. selected-image Alt belongs to Images,
4. descriptions/SEO/search phrases belong to Content,
5. a defect is AI-fixable only when the scoped AI path can write the same owning field,
6. title/description/SEO may preserve only exact source-identity Latin tokens beside Persian text; unrelated Latin fails, while keyword/tag/hashtag editorial lists remain Persian-controlled,
7. `data_ready` controls visible completion/navigation,
8. `locked/finalized` controls operator approval only,
9. mature visible AI buttons converge on the same 3I.39 seven-stage repair authority.

This preserves the requested rule that a correctly entered Stage 1 becomes visibly complete immediately without requiring operator finalization, while `ثبت` remains available to freeze the Stage.

Rollback:
`backup/pre-err49-066-readiness-checker-alignment-20260829` → `c679c66d8c6554ff14e5705b7eb3aada24495990`.

No commerce/Profile/Offer ownership, acquisition, schema, Host or Production boundary changed. Owner Local regression + foreground Product 63 verification remains mandatory.

## Owner SEO/readiness follow-up — ERR-49-065

After ERR-49-064, the professional 3I.39/3I.40 surface became visible. Owner QA then showed that seven-stage AI could persist complete Persian/SEO fields while older cached readiness/help widgets still displayed the previous red defects.

The final contract now includes post-AI persisted-state reconciliation:
- re-read the Product from Catalog SQLite,
- reload visible fields,
- refresh finalization/lock state,
- refresh the guided wizard,
- render final 3I.40 readiness last,
- repeat the readiness reconciliation after a short UI-settle delay.

This does not auto-finalize stages. Data-ready stages may become green/complete while still waiting for explicit operator `ثبت`. Commerce, license/legal and Publish remain operator-owned.

Git:
- source `b9eb9d74b0c0c0be49ca8d04a4333750e68e93f4`,
- regression `375961a1621c43f168b7c3fd76523c6d3c9c9a26`,
- rollback `backup/pre-err49-065-seo-post-ai-refresh-20260829` → `3edda5ffe98d8c37dd66e3e7fc0d6eab3ec6c554`.

Owner Local targeted test and foreground same-product SEO retest remain required.

## Owner visual-QA incident — ERR-49-064

The first foreground owner run against the canonical 8.9.8 source proved that launcher composition markers alone were insufficient. ProductWorkspace construction stopped inside the older 3I.35 wrapper before this phase's visible 3I.39/3I.40 UI could be created.

Observed exception:
`TclError: cannot use geometry manager pack inside ...!labelframe which already has slaves managed by grid`.

Cause:
- `phase49_material_color_picker` had already installed the modern grid-managed checkbox picker,
- `phase49_3i35_operator_ledger.build_material_actions()` still tried to mount an obsolete Listbox action row with `pack` into that same legacy parent,
- the constructor aborted before 3I.39 Professional Commerce and 3I.40 Precision UI builders completed.

Hotfix contract:
- when `_epic49_materials_box` exists, the obsolete 3I.35 Listbox action row is not mounted,
- 3I.35 ledger/data methods remain intact,
- 3I.39/3I.40 remain the final visible Commerce surface,
- no database, migration, crawl, image, AI-provider, secret or Production boundary is changed.

Git:
- source `aa37dcf916dfab71409738f7087a171daffe4a0a`,
- regression `9a3ebd43b22a50ac1447b90cae159dcffb1ed451`,
- rollback `backup/pre-err49-064-stage2-geometry-20260829` → `c62df9dd1bbfee4cfa915beed6f9523efaa4937f`.

Owner Local foreground verification is required before the phase can return to its normal 31–40 acceptance sequence.

## Verification

Catalog/Windows:
- Phase49.3I.31–40 targeted run `33247729316`: PASS,
- Single Active AI run `33247815007`: PASS on final packaged candidate,
- Windows Portable run `33247815027`: PASS,
- runtime/package SHA `55139b909f214f33994d76bc1e6fdfd028b5d6c7`,
- version `8.9.8`,
- build `2026.08.29.2`,
- artifact `3DPrintHub-CatalogCenter-v8.9.8`,
- artifact ID `9713426658`,
- artifact digest `sha256:776eebb4daa1039119721697988508558991c6c4ccd6a2b1cca8b50b6f3b57a2`,
- EXE SHA256 `2be8be49e05575cb20ea12f061d006935df070ec9abb0f87e4f00e4151d5f02a`,
- compile/regression/launcher/source-URL/self-verify/browser/SHA gates PASS.

Store/0040:
- first workflow `33246706102` failed only because two tests froze Decimal string presentation (`24.00` vs `24`, `3000` vs `3000.0000`); migration plan/apply and no-drift checks had already passed,
- corrected numeric comparison at `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`,
- Phase50 Variant2/Profile Matrix run `33246843145`: PASS,
- compile, Storefront JavaScript, selector behavior, Django check, no migration drift, migration plan, full CI SQLite migration and 21 Store/Profile/Checkout/Offer regressions PASS.

## Rollback

Source rollback branch:
`backup/pre-phase49-3i40-commerce-readiness-20260829` → `b59c93cf37dcb66d3e97f61d2669df6e1d1644a4`.

A fresh Local SQLite backup is mandatory before applying 0040 locally. A fresh Production source/environment/MySQL backup remains mandatory before any Host migration/deploy.

## Production

Production was not touched.

Last terminal-verified Production application:
`c283864290f9c989a9fcdf24ee8eef519560e917`.

Last verified Production migration state:
- applied `store.0034`,
- applied `store.0035`,
- `0036..0040` are not claimed applied without a new read-only Host verification.

## Exact next step

Owner Local acceptance:
1. verify canonical Local checkout, origin, branch and clean worktree,
2. ff-only pull the live GitHub head,
3. verify effective Django DB is the intended Local SQLite DB,
4. create checksum-verified pre-0040 SQLite backup,
5. verify 0039 applied / 0040 pending, inspect exact 0040 plan, apply 0040 locally,
6. run Store/Profile/Checkout/Offer regressions,
7. run the current 31–40 Catalog gate,
8. launch `catalog_center/launch.py --debug` in foreground,
9. visually test manufacturer → material → color registration, multi-brand preservation, per-Offer Product fixed price, formula/preheat, Profile identity/dimensions, swatch/image, truthful AI readiness and top-viewport screenshot,
10. verify ordinary Direct Link/Crawl/image/file acquisition remains healthy.

Only after owner Local QA PASS:
Host read-only audit → fresh backups → explicit `FETCH_HEAD` deployment → apply only actually pending migrations → collectstatic → Passenger restart → Production verification.
