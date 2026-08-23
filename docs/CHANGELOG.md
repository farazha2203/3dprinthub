# PROJECT CHANGELOG

Record meaningful changes only. Older detailed entries remain available in Git history.

## 2026-08-23 — Phase49.3I.9 AI Refresh + SEO/Source Completion

### Owner QA Input
- a specific MakerWorld source title could remain translated as generic `محصول چاپ سه بعدی`,
- changing AI Provider/Model and pressing All-Fields again did not refresh already-populated AI output,
- source website/publisher identity and final storefront SEO fields needed to survive all mature post-conversion layers,
- owner requested low-image warning/refetch before full AI completion.

### Root Cause — ERR-49-027
- mature Task Center deliberately filled only missing fields,
- there was no distinction between operator-authored values and stale/AI-owned values during an explicit All-Fields refresh,
- generic legacy placeholders were treated as completed,
- older import intelligence could overwrite source attribution after conversion.

### Fixed
- explicit All-Fields rerun refreshes AI-owned/previous-pack/generated fields,
- real manual overrides remain protected,
- generic Persian product titles are refreshable and new generic AI titles are rejected,
- Persian ecommerce/SEO prompt is more source-grounded and product-specific,
- low-image products may offer the existing mature source refetch before AI,
- factual/local readiness defaults can be filled without inventing source facts,
- missing price may receive local preparation fallback `500000` Toman,
- source website is publisher/source identity; designer remains separate,
- desktop SEO/source data is re-applied to real Django Product meta/OG/source fields after mature conversion/visibility layers,
- commercial-license and sale approval remain explicit operator confirmations.

### Final CI
- CI-only PR #55 closed without merge,
- validated runtime base `390c1aba9aaf5282f44a1ec97955af4e987100ba`,
- marker `0e58324bfc87e39299b81b1fbe65f9cce21ec91e` not merged,
- Phase49.3I `32623618842` SUCCESS,
- Phase49.3H `32623618854` SUCCESS,
- Phase49.3G `32623618950` SUCCESS,
- Full Phase49 + Full Django `32623618792` SUCCESS,
- Django migration NONE,
- Catalog schema migration NONE,
- Production untouched.

### Release Readiness / Payment Discovery
Owner requested an operational handoff to employees today and online payments.
Repository review confirmed:
- employee Catalog release is waiting only on Windows 49.3I.9/manual QA + Local Publish E2E/owner approval for Production,
- Phase30 ZarinPal is mature for accepted Quote payments,
- normal Store cart checkout still exposes only bank transfer and redirects to manual payment,
- StorePayment has a semantic `gateway` method but Store request/callback/verify wiring is not completed.

The Storefront online-payment bridge is therefore tracked as the next urgent implementation. Live Store payment must not be enabled merely by toggling existing Quote payment settings.

## 2026-08-23 — Phase49.3I.8 Observable AI Execution Recovery

### Root Cause — ERR-49-026
The exact bottom Product Workspace All-Fields button still used legacy `ProductStudio.generate_ai("commerce")`, bypassing mature Task Center observability.

### Fixed
- real bottom All-Fields → mature `_phase49_3e_run_ai("all")`,
- non-Quick stage AI → mature Task Center,
- immediate first-paint preserved,
- elapsed timer + Stop Waiting,
- 210-second operator watchdog,
- late cancelled/timed-out result discarded,
- no duplicate AI client/network worker.

### Validation
CI-only PR #53 closed without merge; Phase49.3I/3H/3G and Full Phase49 + Full Django all SUCCESS. Django migration NONE. Production untouched.

## 2026-08-22 — Phase49.3I.7 Preview + Provider Hub Recovery
- fixed MakerWorld Preview browser JavaScript escaping (`ERR-49-024`),
- real Provider-card keys hydrate from Windows Credential Store,
- Provider model catalogs background-load through mature adapters,
- FTP/Bridge persistence preserved,
- no secret in SQLite/Git/source/logs,
- all required CI SUCCESS, no migration, Production untouched.

## 2026-08-22 — Phase49.3I.6 Secure Credential Field Persistence
- initial secure hydration for legacy AI/FTP/Bridge fields,
- later superseded by 49.3I.7 for real Provider Hub variables.

## 2026-08-22 — Phase49.3I.5 Selection Loop Guard + Compact Product Metadata
- fixed hidden Treeview selection feedback loop (`ERR-49-022`),
- compact Product metadata/filters/sorts preserved.

## 2026-08-22 — Phase49.3I.4 Explorer Product Gallery + Source URL Routing
- fixed clipped thumbnails (`ERR-49-020`),
- Explorer view modes/multi-select/context actions,
- source `model_url_pattern` became authoritative Product-vs-Group routing (`ERR-49-021`).

## 2026-08-22 — Earlier Phase49.3I Foundations
Preserved:
- exact Search/Listing authority (`ERR-49-013`),
- Preview before Full Fetch (`ERR-49-014`),
- image limit default 10 / hard max 20,
- AI first-paint (`ERR-49-018`),
- Fixed / Range / Formula independence,
- Windows PowerShell ASCII runner guard (`ERR-49-016`),
- live fetched GitHub snapshot handoff (`ERR-49-019`),
- Product Workspace as canonical detailed editor,
- Local/Production publish separation.
