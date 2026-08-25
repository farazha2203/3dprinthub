# Phase49.3I.24 — Runtime Observability + AvalAI URL Tools + Startup No-Network Guard

Updated: 2026-08-25  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`  
Production: `UNTOUCHED / NOT APPROVED`

## Owner Evidence
- Catalog Center can become slow or `(Not Responding)` during open/close and AI work.
- Product link completion with AvalAI failed with `audit_event() got an unexpected keyword argument 'provider'`.
- OpenRouter accepted `google/lyria-3-pro-preview` but returned music-token output instead of Product JSON.
- uploaded diagnostics show repeated provider `/models` traffic immediately after `app_start`.
- uploaded diagnostics show successful AvalAI Product calls taking roughly 18–52 seconds.
- AvalAI `grok-4.5` diagnostics reported `num_sources_used=0`, proving that putting a URL in ordinary chat did not mean the source was browsed.

## Verified Root Causes
1. 49.3I.23 passed unsupported `provider`/`model` keyword arguments to `audit_event`, aborting AvalAI before the real Product request.
2. legacy initialization paths could still query multiple Provider model catalogs during application construction, adding network work and bad-key noise to startup.
3. Product model selection did not exclude obvious non-text routes such as Lyria.
4. the UI had database/AI logs, but the Dashboard did not expose a first-class operator path for startup/hang diagnostics.
5. a normal chat message containing a URL is not a deterministic page-fetch contract. App-side fetch/sanitization remains authoritative; supported AvalAI tools may add explicit URL evidence.

## Implementation
### AvalAI Product Contract
- exact saved Provider/Model remains authoritative,
- no hidden Product `/models`,
- `json_schema` structured output first,
- fallback to `json_object`, then prompt-enforced JSON only if required,
- audit metadata uses the real `audit_event(... detail={provider, model, ...})` signature,
- obvious music/image/audio/embedding routes are rejected and filtered from the Product model picker,
- when extracted source facts are sparse:
  - supported Gemini routes may use explicit `urlContext`,
  - GPT-5 routes may use Responses `web_search`,
  - unsupported tool calls fall back to app-fetched/sanitized source facts without switching Provider/Model.

### Runtime / Performance Observability
- startup session JSONL begins before the wrapped App constructor,
- unhandled Python/thread exceptions are recorded with redaction,
- Tk heartbeat records recovered UI lag,
- a background watchdog writes all-thread `faulthandler` dumps after an extended UI heartbeat stall,
- hidden model-catalog scans during App construction are blocked until first Tk idle,
- explicit operator model search remains available after first idle,
- AvalAI models are not labeled `رایگان` merely because pricing metadata is absent/zero; only explicitly free-routed IDs are marked Free by this UI adapter.

### Dashboard
Dashboard now exposes:
- Program Log,
- AI Log,
- safe GitHub-ready diagnostic export,
- log folder.

The safe export includes redacted tails of the runtime session log, main Catalog log and hang thread dump in the existing diagnostic JSON.

## Data / Migration Safety
- Django migration: `NONE`
- Catalog schema migration: `NONE`
- no reset/drop/truncate
- no production deploy
- no API key/token/full Authorization header in diagnostic output

## Windows Acceptance Gate
1. close Catalog Center and verify clean Local worktree,
2. ff-only pull the live feature branch and verify Local HEAD == fetched Remote HEAD,
3. compile touched 49.3I.24/23/22/21 modules,
4. run focused 49.3I.24/23 plus inherited 49.3I.22/21/20/19/18 tests,
5. run `launch.py --verify-only`,
6. start the app and verify Dashboard log controls appear promptly,
7. verify startup no longer performs automatic Provider `/models` HTTP calls,
8. explicitly search models in AI Center and verify that operation still works,
9. verify Lyria/non-text models cannot be used for Product structured content,
10. run MakerWorld product 2896217 through `تکمیل همه اطلاعات بر اساس لینک محصول`,
11. verify no `audit_event provider` crash and no hidden Product model scan,
12. verify diagnostics show an explicit AvalAI URL tool when supported, or a visible fallback to app-fetched source facts,
13. if UI stalls for >8 seconds, verify hang thread dump persists and safe export includes it,
14. close/reopen normally and verify logs preserve the lifecycle.

After PASS: exactly one `LOCAL PUBLISH ONLY` + Local Store/Admin/Product/Media/SEO E2E. Production remains blocked until explicit owner approval and Host/MySQL/backup/rollback verification.
