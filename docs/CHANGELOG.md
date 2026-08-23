# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.10 AI Trace + Safe Title Retry Recovery

### Owner Runtime Evidence
- title translation could appear to fail even after the AI provider returned HTTP 200,
- operator could not see the exact request/result/error path for title retry,
- wrong Persian title needed to be explicitly regenerated with a newly selected Provider/Model,
- long/failed AI operations needed a safe stop without closing the app,
- high-volume diagnostics needed scrollbars.

### Root Cause — ERR-49-028
- delayed Tk callbacks captured `except Exception as exc` directly; Python clears the exception target after leaving the except block, so the later callback could raise `NameError: cannot access free variable 'exc'`,
- title-only translation had a separate minimal background path without mature trace/watchdog/stale-result safety,
- existing provider diagnostics stored summaries but did not expose sanitized outgoing/incoming payloads to the operator.

### Fixed
- added `catalog_center/app/phase49_3i_ai_trace_recovery.py`,
- final AI progress dialog now contains scrollable `ارسالی`, `دریافتی`, and `خطا / Diagnostics` tabs,
- vertical and horizontal scrollbars added for large request/result/error content,
- OpenAI-compatible and Google Gemini HTTP payload/result tracing is shown and written to existing Phase49 JSONL diagnostics,
- API keys/tokens/Authorization headers remain excluded/redacted,
- explicit title retry always uses current Provider/Model even when old `title_fa` is non-empty,
- title-only watchdog is 90 seconds,
- Stop Waiting/timeout/workspace close makes title generation stale; late result cannot modify the product,
- generic/non-Persian/too-short title output is rejected before persistence,
- targeted Tk `after()` exception-closure freezing prevents delayed `exc` callbacks from dereferencing a cleared closure,
- existing 210-second All-Fields watchdog and 49.3I.9 AI refresh/manual override/source/SEO contracts preserved,
- no second AI client/crawler/importer introduced.

### CI / Merge
- implementation PR #56 merged after all required workflows passed,
- validated feature head `8d1f6e02d6f722b8f047f5d7f7763a5a42516191`,
- merge commit `256c130f179aaa4253898b0d5ec1ce2696ac4bb5`,
- Phase49.3I `32626758096` SUCCESS,
- Phase49.3H `32626758114` SUCCESS,
- Phase49.3G `32626758134` SUCCESS,
- Full Phase49 + Full Django `32626758119` SUCCESS,
- Django migration NONE,
- Catalog schema migration NONE,
- Production untouched.

### Next Gate
Windows ff-only pull current Epic → runner 49.3I.10 → wrong-title retry/request-response diagnostics → provider/network/Stop Waiting/timeout checks → All-Fields trace → MakerWorld/source/pricing/credential regressions. Only after this passes: one Local Publish E2E, owner approval, then Production release.

## 2026-08-23 — Phase49.3I.9 AI Refresh + SEO/Source Completion

### Root Cause — ERR-49-027
Explicit All-Fields refresh had no distinction between operator-authored values and stale/AI-owned values; generic placeholders could therefore be treated as complete.

### Fixed
- explicit All-Fields rerun refreshes AI-owned/generated fields,
- manual overrides remain protected,
- generic titles rejected,
- source-grounded Persian/SEO prompt,
- low-image mature source refetch offer,
- local readiness defaults without fabricating source facts,
- source website mapped as publisher/source,
- Product meta/OG/source fields receive desktop SEO/source payload,
- license/sale approval remains explicit operator decision.

### Validation
CI-only PR #55 closed without merge; validated runtime `390c1aba9aaf5282f44a1ec97955af4e987100ba`; Phase49.3I/3H/3G and Full Django all SUCCESS; no migration; Production untouched.

## 2026-08-23 — Phase49.3I.8 Observable AI Execution Recovery
- real bottom All-Fields button routed to mature Task Center (`ERR-49-026`),
- immediate first-paint preserved,
- elapsed timer + Stop Waiting + 210-second stale-result watchdog,
- no duplicate AI client/network worker,
- all required CI SUCCESS; no migration; Production untouched.

## 2026-08-22 — Phase49.3I.7 Preview + Provider Hub Recovery
- fixed MakerWorld Preview JS escaping (`ERR-49-024`),
- real Provider-card key hydration/model auto-load (`ERR-49-025`),
- FTP/Bridge persistence preserved,
- all required CI SUCCESS; no migration; Production untouched.

## 2026-08-22 — Phase49.3I.6 Secure Credential Field Persistence
Initial secure hydration for legacy AI/FTP/Bridge fields; later superseded by 49.3I.7 for real Provider Hub variables.

## 2026-08-22 — Phase49.3I.5 Selection Loop Guard + Compact Product Metadata
Fixed hidden Treeview selection feedback loop (`ERR-49-022`) and restored compact Product metadata/filters/sorts.

## 2026-08-22 — Phase49.3I.4 Explorer Product Gallery + Source URL Routing
Fixed clipped thumbnails (`ERR-49-020`); added Explorer views/multi-select/context actions; made source `model_url_pattern` authoritative (`ERR-49-021`).

## 2026-08-22 — Earlier Phase49.3I Foundations
Preserved exact Search URL authority (`ERR-49-013`), Preview before Full Fetch (`ERR-49-014`), default image limit 10/hard max 20, AI first-paint (`ERR-49-018`), Fixed/Range/Formula independence, PS5.1 ASCII runner (`ERR-49-016`), live fetched Git snapshot handoff (`ERR-49-019`), Product Workspace canonical editing, and Local/Production publish separation.

## Payment Discovery — 2026-08-23
Phase30 ZarinPal is mature for accepted Quote payments. Normal Store checkout remains bank-transfer/manual-payment only, so Storefront request/callback/verify integration is the next urgent implementation after Catalog release QA. Live Store payment must not be enabled by toggling existing Quote payment settings alone.
