# Python GUI + FastAPI + Web Acquisition — Engineering Reference

Updated: 2026-08-30

This document is the project-specific knowledge index extracted from the owner-supplied Python GUI, FastAPI, and web-scraping books and reconciled with current official documentation. It is not a reproduction of the books.

## Source set reviewed

### Desktop / GUI
- Wendell Andrade — *Essential Python Programming for GUI Development*.
- Katie Millie — *Python Desktop App Development with GUI*.
- Williams Asiedu — *Python GUI Development with PyQt: Mastering PyQt*.
- previously supplied PyQt5 references already indexed in `PYTHON_QT_GUI_REFERENCE_NOTES.md`.

### Modern web / FastAPI
- Bill Lubanovic — *FastAPI: Modern Python Web Development*; the full first-edition copy is the preferred supplied reference over the earlier raw/early-release copy.
- Malhar Lathkar — *High-Performance Web Apps with FastAPI*; the two supplied PDFs are duplicate/alternate renderings of the same book.

### Web acquisition / crawling
- Katharine Jarmul & Richard Lawson — *Python Web Scraping, Second Edition*.
- Ryan Mitchell — *Web Scraping with Python: Data Extraction from the Modern Web, Third Edition* (owner-supplied EPUB).
- Pradumna Milind Panditrao — *A Python Guide for Web Scraping*.

## Authority rule

Books provide architecture, techniques, trade-offs and tested historical examples. They are not copied blindly.

Before implementation, version-sensitive facts are checked against current official sources:
- Qt for Python / PySide6 docs,
- FastAPI docs,
- HTTPX docs,
- Playwright Python docs,
- Scrapy docs,
- RFC 9309 Robots Exclusion Protocol,
- Sitemaps protocol.

Older Selenium/WebKit/Tkinter/PyQt5 examples remain useful conceptually, but the project prefers current tools where the contract is stronger.

## Desktop application rules

The combined GUI references reinforce:
- user-centered task flows before widget placement;
- explicit event-driven design;
- layout managers rather than absolute coordinates;
- separation of data/model from presentation;
- input validation at the form boundary;
- reusable object-oriented widgets/components;
- accessibility, readable hierarchy and keyboard paths;
- themes/styles as a system rather than per-screen decoration;
- database access behind maintainable interfaces;
- background work outside the GUI event loop;
- unit/regression testing plus foreground visual QA;
- executable packaging as a reproducible release concern.

For 3DPrintHub, the current target remains PySide6 / Qt 6. The mature Tk runtime is not removed until side-by-side acceptance.

Current Qt-specific implementation direction:
- QMainWindow shell;
- QAction registry;
- QStackedWidget workflow;
- Model/View tables;
- QSplitter;
- QSettings;
- QThreadPool / QRunnable / signals;
- light/dark QSS;
- permanent RTL acceptance.

## FastAPI lessons applied without replacing Django

The FastAPI references strongly emphasize:
- API contracts as first-class interfaces;
- type hints and validated models;
- async for I/O-bound work, not blindly for CPU-bound work;
- layered Web / Service / Data architecture;
- dependency injection;
- explicit response models/status codes;
- modular routers for larger applications;
- authentication/authorization as separate concerns;
- tests at Web, Service, Data, integration and load levels;
- production observability: logging, metrics, tracing;
- caches/queues/workers where latency requires them.

3DPrintHub Production is an established Django application. These lessons are applied as architecture principles; Phase49 does **not** replace Django with FastAPI merely because FastAPI is fast.

If a future local/worker API is introduced, it must be justified by an explicit boundary and tested independently. No framework rewrite is implied by this reference set.

## Web acquisition strategy

### 1. Static/structured-first, browser only when needed
Preferred order:
1. robots policy;
2. conditional pooled HTTP;
3. declared Sitemap(s);
4. HTML structured data: JSON-LD, metadata, embedded JSON;
5. DOM parsing;
6. Playwright for dynamic/lazy content;
7. mature source-specific fallback.

This avoids paying browser startup/rendering cost when public structured data is already sufficient.

### 2. Respectful host behavior
Permanent rules:
- honor robots.txt;
- honor Retry-After;
- bounded retries only for transient failures;
- adaptive per-host pacing;
- bounded concurrency and connection pools;
- cache validators (ETag / Last-Modified);
- stale cache only as a clearly marked transient fallback;
- explicit user agent;
- no CAPTCHA bypass;
- no authentication bypass;
- no proxy evasion.

### 3. Crawling models
The supplied scraping references repeatedly separate crawling from extraction.

3DPrintHub therefore keeps:
- discovery URL identity/ledger;
- candidate review;
- Product collection;
- extraction;
- editorial/AI transformation;
- publish/sync
as different states.

A URL being discovered is not equivalent to a Product being trustworthy or publishable.

### 4. Sitemaps as incremental discovery metadata
Sitemap `lastmod` can be used as a freshness signal. It is not treated as proof that Product data changed.

Phase49.3I.45 adds:
- direct-child Sitemap XML parsing;
- `lastmod`, `changefreq`, and `priority` metadata storage;
- newest nested Sitemap documents first inside a bounded document budget;
- Catalog-unseen Products before already-known Products;
- direct URL `loc` only, so nested image/video `loc` values do not become Product URLs;
- generic model-path discovery for custom sources when no source-specific regex exists.

### 5. Dynamic sites
Current Playwright guidance favors condition/locator-driven waiting and built-in auto-waiting over fixed sleeps.

3DPrintHub keeps browser rendering as a fallback and uses bounded page-stability/lazy-content conditions. Long structural CSS/XPath chains are avoided when interactive automation is needed.

### 6. Caching and resumability
Book-derived requirements:
- never redownload unchanged content unnecessarily;
- cache HTTP representations with validators;
- keep durable crawl/discovery state;
- allow interrupted runs to continue from persisted identity/state;
- avoid duplicate Product acquisition.

Current implementation covers these through:
- `acquisition_http_cache`;
- permanent discovery/crawl ledgers;
- continuation cursor;
- `acquisition_discovery_observations`;
- Product/discovered URL uniqueness contracts.

### 7. Structured public endpoint observation
Browser network observation may reveal useful public JSON structure, but the project stores only:
- sanitized same-site endpoint identity;
- method/status/content type;
- bounded field-path schema;
- shape hash;
- body size.

Raw network payloads and credential-like query values are not persisted.

This is provenance/diagnostic intelligence, not an authorization bypass mechanism.

### 8. Parsing quality
Preferred extraction authority:
- explicit structured data and source-specific facts;
- stable semantic metadata;
- DOM tables/definition lists/breadcrumbs;
- bounded body-text heuristics only as a fallback.

Regex is useful for narrow identity patterns and text fallback, not as the only HTML parser.

### 9. Data quality
Raw acquisition and editorial output remain separate.

Source data must retain:
- source URL,
- source identity,
- acquisition method,
- HTTP/fetch evidence,
- quality score,
- structured provenance.

AI may transform/translate permitted editorial fields but must not fabricate missing source facts.

### 10. Concurrency
Concurrency is for I/O waiting. More concurrency is not automatically faster or safer.

Current policy:
- pooled HTTP;
- host-aware pacing;
- bounded requests;
- no uncontrolled same-host fan-out;
- UI/background separation;
- browser instances remain lifecycle-controlled.

## Techniques deliberately not adopted

The books include material on CAPTCHA solving, proxy rotation/evasion, TLS fingerprint mimicry and undocumented APIs.

These are not adopted as automatic project behavior.

3DPrintHub policy remains:
- public data only;
- no CAPTCHA bypass;
- no authentication bypass;
- no proxy evasion;
- no persistence of raw private/session network payloads.

## 2026 implementation mapping

### Already present before 3I.45
- HTTPX pooled async transport;
- per-host latency EWMA and adaptive pacing;
- robots + crawl/request rate policy;
- Retry-After delta and HTTP-date;
- bounded transient retry;
- ETag/Last-Modified conditional cache;
- stale-cache transient fallback;
- gzip Sitemap support;
- default Sitemap probes;
- Playwright condition-driven readiness;
- JSON-LD + embedded JSON + DOM/spec extraction;
- safe public endpoint shape provenance;
- acquisition quality and attempts telemetry.

### Added in 3I.45
- persistent incremental discovery observations;
- Sitemap freshness metadata;
- freshness-aware nested Sitemap order;
- unseen Product priority;
- custom-source model-path Sitemap heuristic;
- direct-child XML semantics.

## Future candidates

Only after current Local acceptance:
- operator-visible acquisition telemetry dashboard in the Qt shell;
- field-level extraction provenance where exact source selection can be proven;
- bounded maintenance/retention for historical acquisition telemetry;
- benchmark suite using local deterministic fixtures rather than live third-party sites;
- optional source adapters for stable documented public APIs.

No live-site stress benchmark should be used as a release gate.
