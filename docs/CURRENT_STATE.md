# CURRENT PROJECT STATE

Updated: 2026-08-23
Repository: `farazha2203/3dprinthub`
Branch: `epic/phase49-unified-product-slider-sync`
Active Phase: `49.3I`
Active Hotfix: `49.3I.17 — Single Active AI Runtime`
Status: `MERGED / ALL REQUIRED CI SUCCESS / WINDOWS QA PENDING`
Production: `UNTOUCHED / NOT APPROVED`

## Current Position
Phase49.3I.16 acquisition fallback remains the canonical exact-page Catalog intake path and is unchanged by this hotfix.

Windows QA then exposed a separate Product Workspace AI blocker: the operator saved one Provider/Model in the AI Center, but legacy runtime resolution could still fall back to another configured provider, every Product AI run performed a `/models` request before the useful content request, Google could list models again, hidden AI-on-open was enabled by default, and a stale async Tk Listbox callback could raise `TclError: invalid command name ...listbox`. This combination explained the slow `در حال اتصال به هوش مصنوعی` stage, apparent multi-model/provider activity, request overlap and occasional UI hang.

Phase49.3I.17 is merged and makes Product AI deterministic and operator-driven.

## Phase49.3I.17 Runtime Contract
- the only Product AI identity is the Provider and Model explicitly saved by the operator,
- runtime reads `ai_provider` plus that provider's saved model from Catalog settings,
- API key is read only from the secure secret slot for that exact provider,
- cross-provider fallback is forbidden; `auto`/unsaved provider fails closed with an operator message,
- compatibility variables are synchronized to the saved identity so legacy title/AI call sites cannot drift,
- hidden AI-on-open is disabled; opening a Product Workspace starts no AI network request,
- normal Product AI no longer downloads `/models` before the useful request; the actual content request is the network test,
- Google Product AI with an exact saved model skips model-list preflight too,
- explicit AI Settings actions `Search model` and `Test connection` remain live network operations,
- stale destroyed-widget Tk callbacks such as `invalid command name ...listbox` are logged/suppressed instead of becoming a fatal Product Workspace popup,
- existing 49.3I.8–11 progress, trace, schema validation/repair, Stop Waiting, stale-result protection and manual-override protection remain.

## GitHub / CI Validation
PR `#63` merged into the Epic branch.
- final PR head: `2917a3db5225abac71fc3e80b64ad439acd7a4d0`,
- merge commit: `7f835f573b92e3aded6275c9421770c0c47d947a`.

Final runtime-head workflows SUCCESS:
- Phase49.3I.17 Single Active AI CI — `32649623837`,
- Phase49.3I Discovery Review Pricing CI — `32649623808`,
- Phase49.3I.16 Resilient Acquisition CI — `32649623695`,
- Phase49.3I.15 Bulk Discovery Images CI — `32649623705`,
- Phase49.3I.14 Legacy Scan Restore CI — `32649623679`,
- Phase49.3H SEO Cost Image Limit CI — `32649623825`,
- Phase49.3G Workspace Usability CI — `32649623755`,
- Phase49 Epic Unified CI including Windows Catalog regressions + Full Django suite — `32649623804`.

## Database / Migration / Media / Secret Safety
- Django migration: `NONE`,
- Catalog schema migration: `NONE`,
- no database reset/drop/truncate,
- no media/history deletion,
- no secret storage format change,
- no acquisition/pricing/publish/FTP/Bridge change,
- Production untouched.

## Exact Next Task — Windows Focused AI Acceptance
1. close Catalog Center; Local worktree must be clean,
2. live fetch/prune + ff-only pull current Epic remote HEAD,
3. run `RUN_PHASE49_3I17_SINGLE_AI_GATE.ps1 -LaunchApp`; it chains 49.3I.16 and every prior Phase49.3I regression gate,
4. in AI Center choose exactly one Provider and one Model and use `ذخیره Provider و مدل فعال`,
5. open a Product Workspace; verify no AI request starts automatically,
6. press the real All-Fields AI action once; trace must show only the saved Provider/Model and must not begin with a `/models` catalog request,
7. if the AI request fails or is stopped, the app must remain usable without Task Manager and no stale Listbox fatal popup may appear,
8. repeat with one different explicitly saved Provider/Model and confirm the next request uses only the newly saved pair.

## Release Gate After Windows PASS
- finish the already-focused Catalog acquisition QA if needed,
- exactly one `LOCAL PUBLISH ONLY`,
- Local Django Store/Admin/Product/Media/SEO E2E,
- explicit owner approval,
- read-only Production path/branch/venv/MySQL/backup/rollback verification,
- deploy only the approved GitHub snapshot,
- Production HTTP/data/media verification.

## Next Product Phase
After Catalog Production verification: Store ZarinPal request/callback/verify + Sandbox E2E while retaining bank transfer.
