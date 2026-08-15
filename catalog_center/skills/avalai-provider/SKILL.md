---
name: avalai-provider
description: Use AvalAI as an OpenAI-compatible AI provider in the 3DPrintHub Catalog Intelligence Windows application.
---

# AvalAI Provider

## Endpoint
- Base URL: `https://api.avalai.ir/v1`
- Models: authenticated `GET /v1/models`
- Prefer dynamic model discovery; never hard-code a model as the only choice.

## Secrets
1. `AVALAI_API_KEY` environment variable
2. Windows Credential Store
3. Local legacy file `D:\projects\3DPrintHub\APIKEY-AVAL.txt`

Never log, batch, upload, commit, or persist the raw key in SQLite.

## Workflow
1. Load key securely.
2. List accessible models.
3. Select user preference if accessible; otherwise select a compatible text model from the live list.
4. Run a tiny live response test.
5. For catalog content, request structured JSON output.
6. Record provider/model metadata, never the key.
7. If provider returns 403/model_not_found, refresh model list and choose an accessible model rather than retrying a forbidden hard-coded model.

## Content rules
- Never invent dimensions, weight, license, compatibility or source price.
- Generate Persian title, descriptions, translated specs, SEO, tags, hashtags and material recommendations separately from source facts.
- AI-generated estimates must be labeled as estimates and require operator review.
