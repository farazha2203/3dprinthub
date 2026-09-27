# Phase50.A2Z Phase E — Read-only Duplicate Audit

Date: 2026-09-27  
Repository: `D:\projects\3DPrintHub-a2z-a2r-converge`  
Branch: `wip/phase50-a2z-w5-manual-product-20260927`  
Canonical Catalog: `D:\projects\3dprinthub-catalog-manager\catalog.sqlite3`

## Safety boundary

SQLite was opened read-only with `mode=ro` and checked with `PRAGMA
quick_check`. No Product, Crawl, Candidate, receipt, media, provider, Host or
Production row was written. No merge, retire, delete, migration, crawl or
publish was attempted.

## Inventory

| Check | Result |
|---|---:|
| SQLite quick_check | `ok` |
| Products | 1076 |
| Product history rows | 4310 |
| Sync receipts | 539 |
| Discovered URLs | 1292 |
| Staging candidates | 626 |
| Products with published_at | 35 |
| Products with nonzero server_product_id | 26 |
| Products with selected media | 761 |
| Blocked Products | 204 |

## Identity duplicate groups

| Authority | Duplicate groups |
|---|---:|
| source_code + external_id | 0 |
| normalized_url | 0 |
| nonempty fingerprint | 0 |
| nonempty, nonzero server_product_id | 0 |

Conclusion: no authoritative duplicate group requires a survivor selection or
merge. Similar-looking cards are not duplicates without matching identity
evidence.

## Survivor scoring contract

For any future nonempty group, select the survivor in this order: published or
server-linked identity and verified receipt; history and sync-receipt
continuity; canonical selected media and local provenance; factual
Product/Profile/Filament/SEO completeness; newest authoritative revision; and
lowest stable local ID only as the final tie-breaker. Conflicting published
identities are a manual blocker, never an automatic merge.

## Rollback plan

Before any future merge: create a fresh integrity-checked Catalog backup and
SHA256; record quick_check, table counts and logical digests; produce a dry-run
survivor-to-retired mapping including every history/receipt/media/server
reference; obtain explicit owner acceptance; apply one bounded transaction with
an auditable merge receipt; then verify the result on an isolated clone.

Status: `LOCAL_TESTED / NO_MERGE_REQUIRED / WAITING_FOR_OWNER_ACCEPTANCE`.
