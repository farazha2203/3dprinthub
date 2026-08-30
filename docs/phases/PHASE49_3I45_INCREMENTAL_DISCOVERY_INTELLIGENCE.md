# Phase49.3I.45 — Incremental Discovery Intelligence

Updated: 2026-08-30  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Status: `GITHUB_IMPLEMENTED + WINDOWS CI TESTED / OWNER LOCAL TEST NEXT / PRODUCTION NOT TOUCHED`

## Goal

Apply the newly supplied GUI, FastAPI and web-acquisition references to the existing 3DPrintHub architecture without rewriting healthy subsystems.

Phase49.3I.45 focuses on the highest-value missing acquisition capability after 3I.43/44: **incremental Sitemap intelligence and persistent discovery metadata**.

## Verified starting state

Pre-phase GitHub head:
`3616bf222f394b769cb2e3198164d735fca5267b`.

Existing 8.9.9 / 3I.43-44 already provided:
- pooled HTTPX acquisition;
- bounded timeouts/connections;
- conditional ETag/Last-Modified cache;
- robots policy;
- Retry-After;
- adaptive host pacing;
- bounded transient retries;
- stale-cache transient fallback;
- gzip Sitemap parsing;
- structured public endpoint shape provenance;
- Playwright dynamic fallback;
- JSON-LD/embedded/DOM extraction.

Dedicated 3I.43/44 run before this phase:
`33309211436` — PASS.

Rollback branch created before 3I.45:
`backup/pre-phase49-3i45-book-driven-discovery-intelligence-20260830` →
`3616bf222f394b769cb2e3198164d735fca5267b`.

## Requested delta

The owner supplied additional references covering:
- maintainable GUI/event-driven architecture;
- FastAPI async/layered/service/data/test patterns;
- crawler models;
- caching;
- concurrent downloads;
- dynamic content;
- storage;
- APIs;
- testing;
- incremental/resumable crawling.

The project delta is to incorporate the useful principles while keeping:
- Django Production;
- mature Catalog SQLite;
- existing crawler/parser/browser paths;
- existing AI/commerce/Filament contracts;
- access-control and web-safety policy.

## 3I.45 implementation

### New Catalog table

`acquisition_discovery_observations`

Fields:
- source code;
- normalized/source URL;
- discovery source;
- Sitemap URL;
- Sitemap lastmod;
- changefreq;
- priority;
- first seen;
- last seen;
- seen count.

This is metadata-only. It does not store HTML, raw JSON/XHR bodies, cookies, credentials or Product content.

### Incremental Sitemap parser

New source:
`catalog_center/app/phase49_3i45_incremental_discovery_intelligence.py`.

Behavior:
- XML parsed structurally, not by broad regex;
- only direct `url/loc` or `sitemap/loc` children count;
- nested media extension `loc` entries are ignored;
- `lastmod`, `changefreq`, `priority` captured;
- nested Sitemap index entries are ordered newest-first inside the bounded document budget;
- Catalog-unseen Products rank before already-known Products;
- source-specific Product URL regex remains preferred;
- custom sources without a regex may use a bounded model-path heuristic.

### Runtime composition

3I.45 installs after the proven 3I.43/44 acquisition layer.

It replaces only the Sitemap candidate planner. HTTP transport, robots, cache, browser, direct-link extraction and mature fallbacks remain the existing authorities.

### Configuration

New enabled policy flags:
- `incremental_sitemap_lastmod`;
- `persist_discovery_observations`;
- `prefer_unseen_products`.

Existing safety flags remain:
- `captcha_bypass=false`;
- `authentication_bypass=false`;
- `proxy_evasion=false`;
- `persist_raw_network_payloads=false`.

## Tests

New:
`tests/test_phase49_3i45_incremental_discovery_intelligence.py`.

Coverage:
- additive schema;
- metadata-only storage;
- nested media `loc` exclusion;
- lastmod/changefreq/priority parsing;
- observation upsert/seen-count;
- newest nested Sitemap prioritization;
- unseen Product prioritization;
- generic custom-source Sitemap heuristic.

Dedicated corrected acquisition workflow:
`33313008595` — PASS.

It verified on Windows / Python 3.12:
- dependency install;
- compile;
- all 3I.43 + 3I.45 acquisition tests;
- mature 3I.16 + 3I.38 acquisition regressions;
- launcher/version contract;
- 3I.43–45 release markers;
- policy guard.

Single Active AI workflow on the same code head:
`33313008558` — PASS.

## ERR-49-078 — robots policy state correction

During source review, a standards/safety gap was found in the 3I.43 robots gate: generic robots fetch failures were treated as unavailable and therefore allowed. Commit `11379ca343c64c251e9c34dd907dffa5f7529e12` separates the states.

Project policy now is:
- genuine robots 4xx unavailable: non-blocking;
- 429 rate-limit: fail closed;
- 5xx/network/transport unreachable: fail closed;
- unexpected robots fetch/parse failure: conservative fail closed.

The corrected behavior is covered by the 3I.43 test suite and is included in Windows acquisition run `33313008595` PASS.

## Book / current-doc mapping

Permanent engineering index:
`docs/references/PYTHON_GUI_FASTAPI_WEB_ACQUISITION_2026.md`.

Important decisions:
- PySide6/Qt6 stays the desktop modernization target;
- Django is not replaced by FastAPI;
- FastAPI's async/layer/service/data/test principles are adopted where useful;
- Playwright remains the dynamic-site tool rather than reviving WebKit/Selenium as the primary engine;
- Scrapy ideas such as AutoThrottle, cache, durable jobs and duplicate control are adopted selectively in the existing architecture rather than introducing a second crawler framework;
- RFC 9309/robots and public-data boundaries remain mandatory.

## Database safety

This phase changes only Catalog SQLite runtime schema through an additive `CREATE TABLE IF NOT EXISTS`.

No Django model or migration is changed.  
No Production MySQL schema is changed.  
No Host write is required.  
No Product/media deletion occurs.

Before owner Local foreground execution, make a fresh checksum-backed copy of:
`D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`.

## Must not touch

- Production;
- Host;
- Django migrations;
- Product/Order Store schema;
- Filament pricing/profile contracts;
- AI provider/key contracts;
- access-control bypass behavior;
- media selection/SEO ownership;
- default Qt/Tk cutover.

## Exact next gate

Owner Local:
1. close Catalog Center;
2. verify canonical repo/branch/clean worktree;
3. ff-only pull exact approved GitHub head;
4. backup Catalog SQLite + SHA256;
5. run 3I.43 + 3I.45 tests;
6. run mature acquisition regressions;
7. launcher `--verify-only`;
8. foreground test one real listing/Sitemap source;
9. confirm new Products are prioritized and no known Product is duplicated;
10. verify no unexpected high-rate requests or browser fallback when Sitemap/HTTP is sufficient.

Production deployment remains blocked.
