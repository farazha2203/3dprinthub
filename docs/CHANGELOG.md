# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.11 Provider Schema + Trace/Busy Runtime Recovery

### Owner Windows Evidence
The AI trace showed AvalAI `gemini-3.5-flash-lite` returned HTTP success and useful Persian content, including a good product-specific `title_fa`, but the JSON contract did not match the repository schema:
- `seo_title` instead of `seo_title_fa`,
- `seo_description` instead of `seo_description_fa`,
- `content_notes` as a string instead of an array,
- other required fields missing/incomplete.

The same trace showed the full `/models` provider catalog being rendered in the Tk diagnostics pane. After changing/stopping AI, the Workspace could also remain busy until the old worker returned.

### Root Cause — ERR-49-029
- AvalAI/OpenRouter `structured_response()` requested generic `json_object` but did not send the actual Catalog JSON Schema to the compatible gateway.
- 49.3I.10 traced full model catalogs into Tk `Text`, adding avoidable UI work.
- Stop Waiting/watchdog made a generation stale but did not immediately release all parent busy flags; stale wrappers could return before mature cleanup.

### Fixed
- real JSON Schema sent to AvalAI/OpenRouter with strict schema response format where supported,
- exact schema/property/type contract also embedded in prompt,
- bounded fallback: strict schema → JSON object → compatibility mode,
- exact schema validation before apply,
- one automatic visible repair request for schema-invalid JSON, then fail precisely,
- explicit selected model used directly,
- model information cached within request window; duplicate model probes reduced,
- model-list trace compacted to count + bounded sample,
- Stop Waiting/watchdog/stale abort immediately releases busy/start/source flags,
- late old result remains stale and cannot mutate product,
- 90s title and 210s full-AI guards preserved,
- no parallel AI client/crawler architecture introduced.

### Validation
PR #57 merged.
- feature head `9bdcfb3c7997cc9570d2d94e1bafd4f7bfad5651`,
- merge commit `41d37d56437765119b9bb274037e9af7a5defbbe`,
- Phase49.3I Run `32628666588` SUCCESS,
- Phase49.3H Run `32628666600` SUCCESS,
- Phase49.3G Run `32628666558` SUCCESS,
- Full Phase49 + Full Django Run `32628666582` SUCCESS,
- Django migration NONE,
- Catalog schema migration NONE,
- Production untouched.

## 2026-08-23 — Phase49.3I.10 AI Trace + Safe Title Retry Recovery
- added scrollable sanitized outgoing/incoming/error tabs,
- fixed delayed Tk exception callback closure bug,
- title retry always uses current Provider/Model,
- title-only 90-second watchdog + stale-result protection,
- generic/non-Persian/too-short title validation,
- PR #56 merged; all required CI success; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.9 AI Refresh + SEO/Source Completion
- explicit All-Fields rerun refreshes AI-owned fields while protecting real manual overrides,
- generic titles rejected,
- source-grounded Persian ecommerce/SEO prompt,
- low-image mature refetch offer,
- publisher/source and final Product SEO/source fields preserved,
- no migration; Production untouched.

## 2026-08-23 — Phase49.3I.8 Observable AI Execution Recovery
- real bottom All-Fields routed into mature Task Center,
- elapsed timer + Stop Waiting + 210-second stale-result guard,
- no duplicate AI client/network worker.

## 2026-08-22 — Phase49.3I.7 Preview + Provider Hub Recovery
- fixed MakerWorld Preview JavaScript escape regression,
- real Provider-card credentials/model lists rehydrated securely,
- FTP/Bridge persistence preserved.

## 2026-08-22 — Earlier Phase49.3I Foundations
Preserved:
- exact Search/Listing authority,
- Preview before Full Fetch,
- image limit default 10 / max 20,
- visual Product Explorer,
- selection-loop guard,
- Fixed / Range / Formula independence,
- AI first-paint,
- Windows PS5.1 ASCII runner,
- live fetched GitHub snapshot handoff,
- Local/Production publish separation.
