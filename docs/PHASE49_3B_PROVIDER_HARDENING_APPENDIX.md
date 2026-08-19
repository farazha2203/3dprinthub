# Phase49.3B — AI Provider / Diagnostics Hardening Appendix

Status: **CI GREEN / Windows live-provider + visual QA pending / Production untouched**

Branch:
`epic/phase49-unified-product-slider-sync`

Runtime hardening baseline:
`a8e74311f69db49f2131ea9df39560585568e262`

Final verification:
- Workflow: `Phase49 Epic Unified CI`
- Run: `32243798557`
- Job: `96039870389`
- Compile: PASS
- Django check + migration contract: PASS
- Phase49 behavioral/regression: PASS
- Windows Catalog Center: PASS
- Full Django suite: PASS

## 1. Why this appendix exists

The main Phase49.3B document already records the seven-stage wizard, Hero Media Studio, AI Provider Hub and persistent diagnostics. This appendix records the final provider-secret hardening and the exact final CI gate after the user's request for provider selection, cost visibility and diagnostic logging.

## 2. Static provider secret registry

`catalog_center/app/secure_secrets.py` now registers every supported provider directly, rather than relying on the Provider Hub UI to patch the registry at runtime.

Provider secrets:
- OpenAI → `OPENAI_API_KEY`
- AvalAI → `AVALAI_API_KEY`
- OpenRouter → `OPENROUTER_API_KEY`

Optional administrative secrets:
- OpenRouter credit/balance reporting → `OPENROUTER_MANAGEMENT_KEY`
- OpenAI organization cost reporting → `OPENAI_ADMIN_KEY`

All are stored through environment variables or Windows Credential Store. They are never persisted to Catalog Center SQLite audit tables.

The static mapping prevents a standalone call such as `get_provider_key("openrouter")` from accidentally falling back to `OPENAI_API_KEY` before the UI is installed.

## 3. Provider Hub contract

Each provider has an independent UI card:
- API key
- model selector
- dynamic model refresh
- live connection test
- provider-specific credit/cost action
- Activate button
- status text

OpenRouter models are read dynamically. Free entries are recognized via `:free`, zero pricing, and the `openrouter/free` router contract.

## 4. Structured-output compatibility

OpenAI Direct uses the Responses API strict JSON-schema path.

AvalAI and OpenRouter use OpenAI-compatible Chat Completions. The client first requests JSON-object mode; if the selected gateway/model rejects `response_format` with 400 / invalid_request / unsupported parameter semantics, it retries once without `response_format` and validates/parses returned JSON itself.

This is the guarded compatibility path for the AvalAI HTTP 400 regression observed during Windows QA.

## 5. Credit and cost semantics

The UI distinguishes balance from cost:

- AvalAI: provider user-credit endpoint can show remaining local-currency/unit balance and exchange rate.
- OpenRouter: account credit reporting uses an optional Management Key; model pricing/free flags come from model metadata.
- OpenAI Direct: ordinary request API keys are not presented as a remaining-credit source. Optional Admin Key data is labeled organization cost/spend, not balance.

Per-request log fields include:
- provider/model
- operation/endpoint
- request ID
- HTTP status
- duration
- prompt/completion/total tokens
- USD cost when provider returns it
- Toman estimate when a USD→Toman rate is configured
- provider-local exact cost when later resolved (e.g. AvalAI transaction lookup)

## 6. Persistent diagnostics

Catalog Center SQLite additive tables:
- `app_audit_log`
- `ai_request_log`

Program audit tracks changed field names, product ID, operator, source module/action, runtime callback errors and diagnostic exports.

AI diagnostics track the request lifecycle described above.

Secret redaction covers Authorization/Bearer, API key, password, token and secret forms before persistence/export.

Diagnostic JSON export is intentionally shareable for troubleshooting and contains no stored provider keys.

## 7. Final regression lock

`catalog_center/tests/test_phase49_3b_ai_diagnostics.py` now additionally asserts:
- OpenRouter is a first-class provider;
- `openrouter/free` is selected when applicable;
- AvalAI HTTP 400 structured-output retry removes `response_format` on the second attempt;
- OpenAI/AvalAI/OpenRouter environment key names are independent;
- OpenRouter Management Key and OpenAI Admin Key have fixed secret-store mappings;
- audit/AI logs persist metadata while redacting fake secrets;
- diagnostic export remains shareable JSON without secret values.

## 8. Production gate

No Production deployment, migration, collectstatic or restart was performed while completing this hardening.

Next gate is Windows Local QA with real operator keys:
1. pull Epic;
2. backup Django + Catalog Center persistent data;
3. apply pending additive `website.0022_phase49_hero_media_presentation` only after migration-plan verification;
4. `python launch.py --verify-only`;
5. inspect independent AvalAI/OpenRouter/OpenAI cards;
6. run live provider tests one provider at a time;
7. reproduce the previously failing AvalAI content-generation case;
8. inspect request log, cost and request ID;
9. export diagnostic bundle;
10. validate seven-stage product wizard and Hero Desktop/Mobile preview;
11. Local Publish one real product;
12. user approval before Production.
