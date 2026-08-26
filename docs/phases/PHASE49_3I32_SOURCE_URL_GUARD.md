# Phase49.3I.32 — Canonical Product Source URL Guard

Updated: 2026-08-26
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`
Candidate: Catalog Center `8.8.2`, build `2026.08.26.2`
Status: `GITHUB CI TESTED / WINDOWS PORTABLE RELEASE GATE RUNNING`

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
GitHub Actions `Phase49.3I.31-32 Smart Link Bulk AI + Source Guard CI` run `32996526852` PASS on runtime snapshot `2ca69c4928333fc15247b99014a8fe77d781b50b`.
Coverage includes:
- both blank controls preserve an existing source URL,
- explicit primary URL edit is allowed,
- explicit secondary URL edit is allowed,
- never-linked Product remains empty rather than inventing a URL,
- exact pre-delete URL is recovered from Product history,
- exact discovered identity is used as local fallback,
- final Workspace save wrapper prevents the old destructive behavior,
- 49.3I.31 smart/batch AI, 49.3I.29 performance, single-active-AI and exact-link regressions remain green,
- Django check/migration-drift safety and launcher smoke pass in the targeted CI.

Windows one-file release workflow run `32996526842` is the remaining packaged-runtime gate at the time of this document update.

## Acceptance gate
1. Windows checkout must be clean and exactly match the approved GitHub head.
2. Run `catalog_center/RUN_PHASE49_3I31_SMART_AI_GATE.ps1` (now covering 3I.31 + 3I.32).
3. Open a Product whose link is populated; execute Save/AI/image/publish-related actions and verify the link remains.
4. Open the Product already affected by the bug; Save or run the smart AI action and verify the exact historical source link is recovered when local history exists.
5. Run OpenRouter/AvalAI exact-link AI smoke and batch selected-Product smoke.
6. Only after owner QA may the 8.8.2 release be published/accepted.
