# Phase49.3I.32 — Canonical Product Source URL Guard

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Candidate: Catalog Center `8.8.2`, build `2026.08.26.2`
Status: `PACKAGED WINDOWS CI PASS / OWNER LOCAL QA NEXT`

## Requested delta
An operator reported that pressing an unrelated Product action could erase the saved Product source link. Existing Product/AI/publish/image behavior must remain intact; only accidental source-identity loss is corrected.

## Root cause
The mature `ProductStudio.save()` treated the two mirrored URL controls (`source_url` and `spec_source_url`) as the only authority. If both controls were temporarily blank, any generic or silent Save wrote an empty `source_url`, then recomputed `normalized_url` and `fingerprint` from that empty value. Silent Save is reused by close/refetch/AI/publish and layered Workspace actions, so an unrelated button could destroy source identity.

## Implementation
`catalog_center/app/phase49_3i32_source_url_guard.py` is composed as the final Workspace-save wrapper after 49.3I.31.

Rules:
- an explicit non-empty edit in the main URL field may replace the existing URL,
- an explicit non-empty edit in the secondary/spec URL field may replace the existing URL when the main field is unchanged,
- if both mirrored controls are blank, an existing canonical DB URL is preserved,
- no missing URL is invented,
- before the mature layered Save runs, the resolved canonical URL is fed back to both controls,
- after Save, a defensive postcondition restores canonical `source_url`, `normalized_url` and `fingerprint` if any legacy layer still managed to erase them,
- Product history and diagnostics record recovery/preservation without logging secrets.

## Repair of products already damaged by the old bug
If the current Product has an empty URL and both UI fields are blank, the guard performs local-only exact recovery in this order:
1. latest Product `product_history` snapshots (`before_json` first),
2. matching `discovered_urls` identity using the same `source_code` + `external_id`.

Only an exact existing HTTP/HTTPS URL is reused. No network request, guessed URL or reconstructed MakerWorld link is used. The recovered canonical identity is written back with normalized URL/fingerprint and a `source_url_recovered` history event.

## Must-not-touch
- no Django/Production schema change,
- no Host deploy,
- no AI provider/model fallback change,
- no Product price/stock/material/color mutation,
- no image selection behavior replacement,
- no automatic public release before owner/local acceptance.

## Verification
Targeted CI:
- `Phase49.3I.31-32 Smart Link Bulk AI + Source Guard CI` run `32996526852` PASS on `2ca69c4928333fc15247b99014a8fe77d781b50b`,
- preserve/edit/recovery tests PASS,
- smart/batch AI, performance, single-active-AI, exact-link, Django safety and launcher smoke PASS.

Packaged Windows gate:
- first run `32996526842` reached the full Windows regression suite and failed only because legacy `tests.test_epic49_operator_workflow` still asserted the literal version `8.8.1`; all new 3I.32 tests had already passed,
- the stale literal was replaced by an atomic runtime-version == package-manifest-version contract,
- rerun `32997106056` PASS on source/runtime snapshot `5208aa4dd3b070e9a7c7c6d6dde9b60569879631`,
- compile PASS,
- full Phase49 regression gate PASS,
- launcher composition PASS,
- source URL invariant PASS,
- one-file PyInstaller build/self-verify PASS,
- release manifest + SHA256 verification PASS,
- immutable Windows artifact upload PASS,
- Actions artifact `3DPrintHub-CatalogCenter-v8.8.2`, artifact ID `9617048629`, created successfully,
- publish step skipped intentionally because GitHub Release publication is manual-only until owner QA.

## Acceptance gate
1. Windows checkout must be clean and exactly match the current approved GitHub head.
2. Run `catalog_center/RUN_PHASE49_3I31_SMART_AI_GATE.ps1` (covers 3I.31 + 3I.32).
3. Open a Product whose link is populated; execute Save/AI/image/publish-related actions and verify the link remains.
4. Open the Product already affected by the bug; Save or run the smart AI action and verify the exact historical source link is recovered when local history/discovery evidence exists.
5. Run OpenRouter/AvalAI exact-link AI smoke and batch selected-Product smoke.
6. Only after owner QA may the 8.8.2 release be explicitly published/accepted.

## 2026-08-27 Local gate launch hotfix
A successful prior `-BuildExe` generated `catalog_center/release/`, but that path was not ignored. The next gate therefore stopped at the clean-worktree preflight before reaching `-LaunchApp`; this log is not evidence of a runtime startup crash. `/catalog_center/release/` is now ignored and regression-tested. Windows packaged CI `33042158052` PASS on `1a490fecb5a22b855c4f10a12bb74f04a28c57b9`; owner Local pull/relaunch is next.

