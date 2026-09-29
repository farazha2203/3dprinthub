# W5C full-suite manifest and baseline comparison — 2026-09-29

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
- Next: W5C exact-SHA GitHub gate. Do not mark W5C/Desktop ACCEPTED before Local=GitHub exact-SHA verification.
- Following phase: final Desktop acceptance. Real Instagram send and deploy remain disabled.
