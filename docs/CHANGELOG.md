# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-22 — Phase49.3I.7 Preview + Provider Hub Recovery

### Windows QA Input
- URL routing to MakerWorld Search/Group Preview was correct.
- Preview failed before producing candidates with `Locator.evaluate_all: SyntaxError: Invalid or unexpected token`.
- real Phase49.3F AvalAI/OpenRouter/other Provider-card API Key fields still appeared empty after update/restart.
- Provider model lists were therefore not reliably visible to the operator.

### Root Causes
- `ERR-49-024`: Python string escaping converted the intended JavaScript `\n` escape into a literal newline inside a single-quoted browser expression passed to Playwright `evaluate_all()`.
- `ERR-49-025`: 49.3I.6 hydrated legacy `ai_key` but the actual modern Provider Hub uses `_ai_hub_key_vars`; mature Provider Save securely persisted the key and then cleared those real widget variables.

### Fixed — Preview
- added `catalog_center/app/phase49_3i_preview_recovery.py`.
- raw Python JavaScript string preserves valid browser-side escaping.
- existing `candidates_from_dom_rows()` remains the Stage-1 lightweight parser.
- no Direct Product or Full Fetch function is called by the recovery layer.
- mature `classic_methods.discover_classic` / `collect_classic_exact` remain untouched.
- business flow preserved: Search → one-thumbnail/basic-identity Preview → Approve → Full Fetch → selected image limit 1..20.

### Fixed — AI Provider Hub
- real AvalAI/OpenRouter/OpenAI/Google `_ai_hub_key_vars` hydrate from Windows Credential Store.
- Provider fields rehydrate after mature secure Save clears them.
- OpenRouter management/OpenAI admin masked fields hydrate when stored.
- FTP password + Bridge token secure hydration remains preserved.
- configured Provider model catalogs background-load through the existing `AIProviderClient.list_model_info()` path.
- existing Model ID combobox/cache and manual model picker/API refresh remain authoritative.
- no secret is written to SQLite/Git/source/logs.

### Tests / Runner / CI
- added `test_epic49_phase49_3i_preview_recovery.py`.
- expanded `test_epic49_phase49_3i_secret_persistence.py` for real Provider Hub variables and model catalog visibility.
- runner upgraded to `RUN_PHASE49_3I_LOCAL_GATE.ps1` v49.3I.7; still ASCII-only for Windows PowerShell 5.1 and live-Git-snapshot guarded.
- CI-only PR #52 closed without merge.
- validated runtime base `4e0b1b7f0f8934a03ab74037bdce5f9abe55b425`.
- marker head `5097f45f069e40af64d452ffaa8cd07399a977f2` not merged.
- Phase49.3I Run `32585956198` — SUCCESS.
- Phase49.3H Run `32585956149` — SUCCESS.
- Phase49.3G Run `32585956156` — SUCCESS.
- Full Phase49 + Full Django Run `32585956155` — SUCCESS.
- Django migration: NONE.
- Catalog schema migration: NONE.
- Production untouched / not approved.

### Next Gate
- Windows ff-only pull current Epic,
- run v49.3I.7 Local Gate with `-LaunchApp`,
- verify secure keys/tokens after restart,
- verify Provider model lists load visibly,
- verify exact MakerWorld Preview works and remains lightweight,
- approve one candidate with image limit 20 and confirm Full Fetch starts only after approval,
- Local Publish remains blocked until manual QA passes.

## 2026-08-22 — Phase49.3I.6 Secure Credential Field Persistence

### Changed
- initial secure-field hydration layer added for legacy AI key, FTP password and Bridge token.
- Windows Credential Store/environment remained source of truth.
- CI-only PR #51 closed without merge.
- Phase49.3I `32583277412`, 49.3H `32583277584`, 49.3G `32583277406`, Full Phase49 `32583277418` all SUCCESS.
- later Windows QA proved modern Provider Hub variables were not covered; superseded by 49.3I.7 / `ERR-49-025`.

## 2026-08-22 — Phase49.3I.5 Selection Loop Guard + Compact Product Metadata

### Changed
- fixed hidden Treeview selection feedback loop (`ERR-49-022`).
- compact Product ID/state/source/image/date/publish metadata added.
- Persian filter/sort controls restored.
- CI-only PR #50 closed without merge; all required Phase49 CI SUCCESS.
- no migration; Production untouched.

## 2026-08-22 — Phase49.3I.4 Explorer Product Gallery + Source URL Routing

### Changed
- fixed clipped thumbnail receiver (`ERR-49-020`).
- added Explorer view modes/multi-select/context actions.
- source `model_url_pattern` became authoritative Product-vs-Group routing boundary (`ERR-49-021`).
- non-product source URLs route Preview-first.
- no migration; Production untouched.

## 2026-08-22 — Earlier Phase49.3I Foundations

Preserved:
- exact Search/Listing URL authority (`ERR-49-013`),
- Preview before Full Fetch (`ERR-49-014`),
- image limit default 10 / hard max 20,
- AI first-paint (`ERR-49-018`),
- Fixed / Range / Formula independence,
- Windows PowerShell ASCII runner guard (`ERR-49-016`),
- live fetched GitHub snapshot handoff (`ERR-49-019`),
- Product Workspace as canonical detailed editor,
- Local/Production publish separation.
