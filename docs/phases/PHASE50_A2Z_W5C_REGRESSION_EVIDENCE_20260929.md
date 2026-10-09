# W5C full-suite manifest and baseline comparison — 2026-09-29

## 2026-10-04 — Product photo identity (Build 2026.10.04.2)

- Status: `LOCAL_TESTED / VERIFYONLY_PASS / VISIBLE_UI_PENDING`; checkout `D:\projects\3DPrintHub-a2z-a2r-converge`, branch `wip/phase50-a2z-w5-manual-product-20260927`, base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`; no commit/push.
- Root cause: a legacy fixed-name acquisition screenshot was promoted/renamed as Product media; Stage-3 gallery reconstruction and Feed resolver independently read raw canonical image identities and bypassed earlier filtering.
- Fix: preserve the explicit operator Screenshot-to-Product feature and its timestamped gallery item. Exclude only the legacy acquisition-evidence identity from the affected gallery/publish resolution. No canonical identity rewrite or evidence-file deletion.
- Verification after restoring the operator Screenshot feature: targeted suite `32/32 PASS` (22 capture/flow, 8 gallery/screenshot, 1 Site-media gate, 1 twenty-image Product Wizard display/reopen); compileall, diff-check and Qt VerifyOnly on fresh temporary empty Catalog pass. Read-only Product #964 Gallery/Site/Feed resolver identity and SHA parity passes. Foreground visual selection/delete/reopen is pending; no canonical Catalog, Host, Production or Instagram mutation.

## 2026-10-03 — Product gallery identity correction (Build 2026.10.03.2)

- Status: `LOCAL_TESTED / QT_VERIFYONLY_PASS / VISIBLE_UI_PENDING`; same forward checkout/branch as W5C; base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`; no commit/push.
- Root cause: when exact Product URL mappings were available, the gallery still appended unreferenced numbered downloader-cache files as selectable `local://` identities. Those ghost cards could shift operator selection/deletion away from the persisted image identity. Corrected cards to come from persisted Product image identities and exact URL→final-file resolution; persisted same-Product local-display aliases remain validated.
- Regression mutates numbered cache bytes after finalization, proves each visible card path equals the exact publish path, removes one remote URL identity, and confirms only the sibling remains after reload. Gallery/media tests `33/33 PASS`; image recovery tests `11/11 PASS`; compileall, isolated Qt VerifyOnly, SQLite quick_check/integrity_check PASS.
- A disposable Temp Catalog used during candidate startup differs logically from its registered backup (Product #1075 image fields and Product #862 stage state); preserved for audit and no longer an acceptance baseline. No canonical Catalog, Host, Production, or Instagram action. Next: visible card/select/delete/reopen smoke on a fresh isolated Catalog. W5C/Desktop and GitHub gates remain open.

## 2026-09-30 — Restore automatic Story and explicit resend behavior (Build 2026.09.30.4)

- Cause: Build .3's AI Popup set `require_link_sticker=True`, unintentionally requiring Buffer mobile notification for every Story; exact-asset receipt dedupe also prevented intentional repeat publication.
- Correction: Popup now explicitly selects the prior automatic Story publisher even when a manual Sticker setting is stored; native Sticker notification remains separate. An intentional send after completion creates a fresh Buffer post even for the same Product/image; active-worker guard prevents concurrent duplicate clicks.
- Test: Story/Post/Buffer/UI `40 passed, 1 imported helper deselected`, including repeat publication and automatic readiness with no active mobile device.
- Verification: compileall, diff-check, isolated Qt VerifyOnly and clone/backup quick/integrity checks pass. Read-only audit attributes clone delta to four Product #862 `product_history` events (one view and three Story previews); Product rows, AI revisions and sync receipts unchanged, no send receipt. No real Story/Post, canonical Catalog write, Host, Production, commit or push.
- Remaining: visible Desktop Popup smoke/close-reopen; Computer Use currently exposes `apps: []`; then W5C and exact GitHub SHA gate.

## 2026-09-30 — Story delivery truth and native Link Sticker handoff (Build 2026.09.30.3)

- Status: `LOCAL_TESTED / FOREGROUND_ACCEPTANCE_BLOCKED / GITHUB_GATE_PENDING`; base HEAD/upstream `46497ccad3219300aea05a830c625086d79f789b`, dirty W5 candidate preserved; no commit/push.
- Defect proven: prior receipt keyed by Site ACK suppressed a different AI Story creative and was reported as success. Product #862 receipt #539 was old; selected revision #11 had no matching send receipt.
- Fix: exact Story asset/strategy/tracking-URL dedupe; duplicate is not fresh publish. Link Sticker Story uses Buffer notification and exact URL reminder, then operator must finish Sticker → Link → paste URL → Share in Instagram. Notification remains pending; receipt reconciliation never reposts and requires Buffer `markedAsPublished` and external-link evidence.
- Buffer read-only readiness: `hasActiveMemberDevice=false`; therefore the new notification flow is intentionally blocked until a mobile device and push notifications are connected. No real Story/Post or notification was sent.
- Verification: `53 passed, 1 imported helper deselected`; `compileall`, `git diff --check`, isolated Qt VerifyOnly (`QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK`), isolated Catalog and backup quick/integrity checks PASS. Backup SHA256 `5CC5D7BE95DA8FFCFFB28DAC7E06803E789F04ED299957DD2515DE9041B2E381`; post-VerifyOnly clone SHA256 `470f67ef9c12b3fa3587407355341611d22660faffa9186ae8d2ad06a8810744`. Canonical Catalog untouched.
- Computer Use returned no native apps/windows; Remote Desktop Commander provides process/file only. Foreground Popup and close/reopen acceptance remains pending. No Host/Production delta, commit or deployment.
- Next exact: connect Buffer mobile device and verify readiness; obtain targetable desktop, inspect Build `.3` Story/Post Popup, then (only after separate action-time approval) do one controlled notification/manual Link Sticker completion/reconciliation. Complete W5C/Desktop acceptance and exact GitHub SHA gate. Do not close W5C or claim a live link before these gates.

## 2026-09-30 — Popup send handoff / queued-status correction (IN_PROGRESS)

- Build candidate: v8.9.11 / `2026.09.30.2`; forward branch remains `wip/phase50-a2z-w5-manual-product-20260927`; base HEAD `46497ccad3219300aea05a830c625086d79f789b`, pre-existing dirty W5 files preserved.
- AI Story/Post popup now has a send button enabled only for real AI-generated, approved, selected revisions. Callback routes `post` to feed and `story` to Story using only the revision Product ID and the existing guarded workflow.
- Buffer `sending` now increments `submitted`, not `published`; only `sent`/explicit live confirmation increments `published`. Read-only runtime evidence included one Story published receipt and one Post receipt in `sending`; no provider error receipt was found, so the Post was not declared failed or successful.
- Focused Popup/Instagram/Buffer regression 50/50 PASS; py_compile, diff-check, isolated Qt VerifyOnly and isolated Catalog/backup integrity PASS. No real send, canonical Catalog write, Host or Production operation.
- Computer Use returned no native apps/windows after launching the candidate against the isolated Catalog, so visual Build/Popup verification remains pending. Do not click Send or deploy.
- Recheck on 2026-09-30: Remote Desktop Commander device is online and confirms a running Qt process, but has no screenshot/window-control capability; Computer Use again returns `apps: []`. Focused 50-test suite was rerun and passed; local HEAD still equals upstream base, candidate remains uncommitted.
- Next: obtain targetable foreground desktop and verify both popup send buttons; then continue W5C/Desktop gate without real publication.

Status: `IMPLEMENTED / FOCUSED_TESTED / W5C_DESKTOP_PENDING`.

## 2026-09-30 — Image AI / premium Story continuation (IN_PROGRESS)

- Owner request: restyle 1/2/3/6, preserve favorites #4 lifestyle and #5 surreal, and ensure Generate actually calls OpenRouter Image API rather than Mock.
- Candidate Build 2026.09.30.1; current forward HEAD remains 46497ccad3219300aea05a830c625086d79f789b with uncommitted work. Real request sends product and official logo reference, pinned provider, style/aspect and factual Persian copy/optional explicit discount. Result is an unapproved SQLite BLOB.
- Discovery-only: 22 compatible endpoints. Seedream 5 Lite / seed estimated ~$0.035/image including two free refs is currently cheapest fixed-rate compatible; Qwen Image 3 / alibaba ~$0.036. No image generation executed.
- Focused regression 45/45; py_compile/diff-check PASS. Persian typography and visual image quality remain unverified.
- Isolated Catalog checks: quick_check and integrity_check OK; path/hash are in CURRENT_STATE/PATHS. Canonical Catalog was not written. Native UI process was launched but Computer Use inventory did not expose a targetable window; no visual Popup acceptance claimed.
- Next: native Popup acceptance and isolated endpoint save; stop at explicit $0.035 estimate pending action-time billing approval. Then one controlled image, verify BLOB/Preview/reopen/idempotency, Qt VerifyOnly and exact-SHA GitHub gate. Existing full-suite baseline remains 12 failures + 14 errors parent-proven; W5C/Desktop not accepted. No Instagram/Host/Production/deploy.

Status: `MANIFEST_CAPTURED / ONE REGRESSION FIXED / BASELINE DEBT DISPOSITIONED / FINAL GATES PENDING`.

## Run identity

- Current source before the fix: branch `wip/phase50-a2z-w5-manual-product-20260927`, HEAD `5963cf52c0888a8a77e61091c5e4296a59ffb7d3`.
- Parent comparison: `00fd4d9600b4fddbfcbee1439c2e45ab02589e3b`.
- Command: `python -m unittest discover -s tests -p 'test*.py' -v` from `catalog_center`.
- Python: `3.12.10` from the verified workstation project venv.
- Full verbose log (stored outside the repository): `C:\Users\Emad-PC\AppData\Local\Temp\3dprinthub-w5c-full-regression-20260929.log`.
- Log SHA256: `68EB2C764744B7F0741A65CB08BCFA492A5EF301A64E99C5D43BD0EBF5C33EE3`.
- Result before the code fix: `Ran 971 tests`; `12 failures, 15 errors`.

## Failure manifest

The following 12 failures were already parent-proven by the prior exact-parent regression record (`docs/ERRORS.md`, ERR-50-IMAGE-003):

1. `test_portable_exe_activates_and_verifies_unified_workspace` — `test_epic49_editable_studio`
2. `test_normalizers_keep_backward_compatibility_and_rich_metadata` — `test_epic49_material_color_picker`
3. `test_transparent_and_multicolor_metadata_roundtrip` — `test_epic49_material_color_picker`
4. `test_profile_identity_rejects_duplicate_name_size_and_dimensions` — `test_phase49_3i39_professional_commerce`
5. `test_image_stage_uses_four_compact_column_cards_with_size_and_seo_facts` — `test_phase49_3i42b_core_parity`
6. `test_main_window_reports_full_parity_contract` — `test_phase49_3i42b_core_parity`
7. `test_legacy_numbered_images_render_real_files_not_sixty_placeholders` — `test_phase49_3i47_qt_workspace_image_bulk_ai`
8. `test_wheel_over_large_preview_scrolls_gallery_and_window_stays_shrinkable` — `test_phase49_3i47_qt_workspace_image_bulk_ai`
9. `test_filament_brand_palette_finish_image_and_roll_price_are_authoritative` — `test_phase49_3i48_owner_filament_site_foundation`
10. `test_product_image_stage_is_large_compact_single_row_and_source_link_fixed` — `test_phase49_3i51_windows_site_finalization`
11. `test_openai_content_supports_translate_and_commerce_modes` — `test_v83_core`
12. `test_sidebar_contains_every_operational_center` — `test_v87_ux_rebuild`

## Error-event manifest and classification

Fourteen of the fifteen pre-fix error events reproduced when the exact listed test cases were invoked against parent `00fd4d9600b4fddbfcbee1439c2e45ab02589e3b`. These are baseline events, not caused by W5:

- `test_aggregate_known_unknown_and_nonbillable_requests` — `test_epic49_phase49_3h_cost_ledger` — SQLite temporary Catalog teardown `PermissionError`.
- `test_avalai_cost_parser_requires_explicit_currency_semantics` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_publish_receipt_freezes_internal_product_cost_snapshot` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_error_text_is_redacted_before_persistence_and_display` — `test_epic49_phase49_3h_seo_execution` — SQLite temporary Catalog teardown `PermissionError`.
- `test_persistent_result_contains_steps_cost_and_changed_fields` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_source_contract_has_result_drawer_and_error_keeps_progress_open` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_audit_and_ai_logs_are_persistent_and_secrets_redacted` — `test_phase49_3b_ai_diagnostics` — SQLite temporary Catalog teardown `PermissionError`.
- `test_diagnostic_bundle_is_shareable_json_without_secret` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_identity_columns_are_populated_for_app_and_ai_rows` — `test_phase49_3b_diagnostics_identity` — baseline error event (reported twice in the suite output, including teardown).
- `test_launch_contract_exposes_identity_markers` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_session_snapshot_is_shareable_without_secret` — same module — SQLite temporary Catalog teardown `PermissionError`.
- `test_v7_columns_and_upload_queue` — `test_v7_core` — baseline assertion `1 != 0`.
- `test_product_fields_and_blocking_schema_exist` — `test_v85_core` — baseline fixture `AttributeError` (`self.temp` absent).

The sole current-only event was:

- `test_avalai_connection_falls_back_to_chat_completions` — `test_v84_core` — `TypeError` because the global Phase49.3I.29 `AIProviderClient.choose_model` wrapper rejected the newer explicit keyword `model_info` passed by `test_connection()` after another test installed the wrapper.

Root cause was verified in `app/phase49_3i29_windows_performance_ai.py`. The wrapper was changed to accept keyword-only `model_info` and forward it to the original chooser only in non-Product discovery. Product-scoped execution still requires its exact saved model and cannot fall back to hidden `/models` listing.

Post-fix ordered regression ran `tests.test_epic49_phase49_3i29_windows_performance_ai`, `tests.test_v84_core`, `tests.test_phase49_3i23_avalai_chat_contract`, `tests.test_social_ai_design`, and `tests.test_social_ai_popup_smoke`: `37/37 PASS`. Python compile and `git diff --check` passed. The full suite was not rerun after the fix.

The earlier document count `12 failures / 16 errors` is not reproduced by this complete captured run. The one additional historical event has no retrievable test identity and is deliberately left unguessed; the captured manifest itself has no remaining unclassified event.

## Safety and next gates

- No Catalog/database/media, credential, Host, Production, Instagram, tunnel or service state changed.
- No test log containing raw output is committed; only this sanitized manifest is in Git.
- Isolated Qt VerifyOnly passed: `QT6_FOUNDATION_VERIFY=OK`, `QT6_42B2_FULL_PARITY_VERIFY=OK` on a disposable clone of the checked backup; clone `quick_check` and `integrity_check` passed before and after. The exact temporary clone/artifacts were removed; canonical Catalog was untouched.
- Backup integrity passed for `D:\projects\3dprinthub-backups\phase50-social-ai-sqlite-20260928-01\catalog-before-social-ai.sqlite3`: 979,947,520 bytes; `quick_check=ok`, `integrity_check=ok`.
- Final source/docs review, ordered 37-test gate, compileall and diff-check passed after documentation closure.
- GitHub gate passed: commit `83945715bbe50fb2588fc01abb68be363f308fe5`, Local=GitHub exact SHA.
- Next: final foreground Desktop acceptance on this SHA with isolated Catalog. Do not mark W5C/Desktop ACCEPTED before that gate.
- Following phase: final Desktop acceptance. Real Instagram send and deploy remain disabled.

## 2026-10-09 — Post-latest SEO lineage merge gallery gate
In isolated merged branch `merge/phase50-a2z-a2u-lineage-20261009`, selected-media truth `test_phase50_a2z_o2e_media_truth.py` 14/14 PASS and official Qt VerifyOnly (foundation/full parity/operator launcher) PASS. The owner Desktop shortcut remains on original accepted W5 source; no UI select/delete clicks on a disposable Catalog were possible with available current desktop interface. **W5C VISUAL ACCEPTANCE REMAINS OPEN**, notwithstanding headless tests. Retain documented rollback clone, do not delete any Product image or claim manual card selection/reopen success. Next: targetable GUI + disposable verified Catalog clone, then confirm exact visible card/files selected/published, one scoped delete/reload, no unintended media/DB change. Following: W6 Video/Reel.

## 2026-10-09 — Native Windows Qt QTest Gallery Evidence (source merged `09fd3b6e`)
Earlier W5C visual blocker narrowed: Remote Desktop Commander has file/process and Qt renderer access, but not a direct human GUI screen-control UI. Built `catalog_center/tests/test_phase50_w5c_visual_qt_roundtrip.py`: actually instantiates current `ProductWizardPage`, displays Stage 3 with a synthetic Product, uses `QTest.mouseClick` on visible thumbnails and toolbar, records widget PNG screenshots, asserts original colors/identity, deletes two of four via acknowledged command and checks both Product URL state and Site media resolver exact path parity after close/reopen. Second case creates 20 image cards, scrolls to the 20th thumbnail and clicks it while all 20 original image sources remain present.
- Native Windows QPA `2/2 PASS`, screenshots 01_before through 06_twenty_last were opened and visually reviewed: correct distinct images and Persian labels; 4→2→2 (reopened), scroll to bottom and twentieth checkbox.
- Offscreen Qt CI mode `2/2 PASS`, but offscreen typography shows placeholder boxes (ERR-50-056), so offscreen screenshots are not typography acceptance.
- Other W5C media-truth 14/14 PASS, official Qt VerifyOnly PASS and py_compile/diff-check PASS.
- Read-only live Catalog still 1076 Products, #536 Site revision2 and unchanged two historic Instagram receipt counts. Fresh 1.22GB disposable real Catalog clone used only for 4-image synthetic Product (now 1077 QA Products), its pre-test SHA `42f6876f87c4c32fa480f5159c2395d4edb818c4cc0438714f2c9918bd04037f`, `PRAGMA quick_check=ok`; historical protected backup c87fb9cc... unchanged. Source Catalog/media/Host and social providers were never modified.
- W5C STATUS **LOCAL_TESTED / NATIVE_QT_AUTOMATED_VISUAL_VERIFIED / OWNER_FOREGROUND_UAT_PENDING**; do not mark `ACCEPTED` until operator verifies real Desktop gallery on their selected non-production Product and confirms behavior. This is a concrete improvement over old headless-only W5C proof, but is not a user-clicked desktop signoff.
- Next: checkpoint to exact GitHub SHA; request/obtain owner foreground visual acceptance or connect actual window control. Only then W6 Product Video/Reel.

2026-10-09 final QA checkpoint GitHub SHA `9fcd898963c07d4eb78990d8b6711d9e1b4576f1`; visual-image/Qt automated acceptance evidence published as source test and internal six screenshots, not installed app or owner signoff. Status GITHUB_UPDATED / NATIVE_QT_AUTOMATED_VISUAL_VERIFIED / OWNER_FOREGROUND_UAT_PENDING. Next owner confirms in daily Qt app; W6 source video/Reel immediately after.

## 2026-10-09 — Real owner Desktop source W5C visual test on Product #1074 (NO DELETE)
The actual Desktop `.lnk` and `.cmd` point to `D:\projects\3DPrintHub-a2z-a2r-converge\catalog_center\RUN_QT.ps1` on Windows W5 branch GitHub-equal SHA `8a8b23bc78b52e145c2b77702bac76ae15a88720`. Five exact code blobs for Stage 3 Qt Product Wizard/Gallery/Kernel/media publish resolver/Qt launch match the unified GitHub source; `RUN_QT.ps1` SHA256 matches `CAA8EBA15BCFE23A6B01D53CDF41A6F57089F2259373F012AFC384053F50E65B`. There is no galllery runtime patch missing from Desktop; **skip cutover**, preserve all shortcuts and backup opportunity for future actual changes.
Used approved **separate** 1.22GB QA Catalog clone with real Product #1074 five finalized WebP images, never canonical DB for GUI actions. Invoked actual daily source `ProductWizardPage` native Windows Qt, loaded real Product and Stage 3, visually inspected `QWidget.grab` snapshots before/two selected/after reopen. Actual `QTest.mouseClick` on two image thumbnails selected only bulk edit checks; `selected_images_json` Site sending stayed all five and media source mapping SHA256 equaled actual publisher. Page reopened showing 5 unchanged photo identities and same Site selections. Original files unchanged; no Delete, no Send, no Provider calls. Snapshots located `D:\projects\3dprinthub-backups\phase50-w5c-visual-20261009-1300\evidence\actual-daily-source-real-product\01-real-product-before.png` through `03-real-product-reopened.png` were opened and reviewed: all five native previews and Persian text rendered.
Official daily `RUN_QT.ps1 -VerifyOnly` PASS Qt Foundation/Full Parity/Operator. Read-only Product #1074 Catalog image fields equal between canonical and QA; 1076 canonical Product count (QA 1077 from previous synthetic acceptance Product). This satisfies **native automated visual verification on actual daily source**, but owner hands-on daily Desktop GUI `ACCEPTED` remains PENDING. No Host Production deploy nor new Instagram publication, and no unneeded Windows shortcut change. Next get owner's user-facing gallery acceptance; then phase W6 after gate.
