# ERR-49-084 — Product AI Link fallback + verified apply

Date: 2026-08-31  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Tested code checkpoint: `0c67fa30493d100b99ec37314586e0491ecbcda5`  
Rollback: `backup/pre-err49-084-ai-link-fallback-apply-verify-20260831` → `4802f8ba0ca7920f6ee047ebd4ffb57e45025d0a`  
Production/Host touched: NO  
Django/Catalog migration changed: NO

## Owner evidence

Product #309, Stage 1 `quick`, source mode `link`:
- `openrouter/auto-beta` failed at `crawler.public_http` with HTTP 403;
- exact `openai/gpt-oss-20b` failed at the exact same call;
- both failures happened inside `resolve_source → live_source_for_ai` before Product content was sent to OpenRouter.

The owner also reported a second failure mode: AI could return data but the expected Product fields were not visibly applied.

## Root cause

The Qt `AICore` called the mature orchestrator directly, but Link source resolution still had a strict single path: live public HTTP. There was no fallback to already persisted Crawl/Product facts for an explicit blocked response. Separately, stage apply accounting treated a successful `update_product` call as sufficient and did not re-read the DB to prove persistence. The variable-router detector also missed `openrouter/auto-beta`.

## Fix

1. Link mode attempts live evidence once.
2. `BlockedError` (403/429) is not blindly retried.
3. If persisted Product facts have a valid source title, the AI run continues with that evidence and records `requested=link`, `effective=data`.
4. If persisted evidence is insufficient, an explicit source-data error is raised.
5. Locked/no-work scoped stages exit before source or Provider execution.
6. Every normal AI stage write is re-read and compared field-by-field; non-persisted updates raise an error.
7. Qt reports the Link→saved-data fallback.
8. all `openrouter/auto*` variants are rejected as deterministic Product defaults.

## Regression proof

New tests prove:
- blocked Link fallback reaches the generator and persists Stage-1 Persian title;
- locked Stage 1 makes zero source/generator calls;
- a no-op DB write cannot be reported as success;
- `openrouter/auto-beta` is rejected like `openrouter/auto`.

Final CI on code checkpoint:
- `33409112402` — Qt6 Crawl + AI Runtime — PASS;
- `33409112322` — Single Active AI — PASS;
- `33409112381` — Stage/Commerce — PASS;
- `33409112367` — Windows Portable build/self-verify/artifact upload — PASS.

## Next owner Local acceptance

Close Catalog Center, clean ff-only pull the final GitHub documentation HEAD, run the repository-owned `RUN_PHASE49_3I42C_LOCAL_GATE.ps1 -LaunchApp`, then retest Product #309 Stage 1 with an exact Product-safe OpenRouter model.

Expected:
- no terminal MakerWorld 403;
- if direct Link is blocked, UI says saved data was used;
- title/content change is actually visible after DB reload;
- if DB persistence fails, execution reports an error rather than success;
- no operator-owned commerce/Filament/stock/publish field is changed.

No Production deploy is approved before this foreground acceptance.
