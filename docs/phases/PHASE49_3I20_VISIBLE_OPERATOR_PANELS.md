# Phase49.3I.20 — Visible Operator Panels

Updated: 2026-08-25  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Status: `IMPLEMENTED ON GITHUB / WINDOWS LOCAL QA REQUIRED`  
Production: `UNTOUCHED / NOT APPROVED`

## Trigger
Owner Windows QA showed that the 49.3I.18/49.3I.19 controls existed in source but were not visible in normal Product Workspace use. The additive panels were packed after large `fill="both", expand=True` gallery/content panes, so they could be pushed below the visible viewport.

## Requested Delta
Keep the existing 49.3I.18 and 49.3I.19 controls fully intact, but move their already-created panels ahead of expandable content so they are immediately visible when opening the relevant Product Workspace sections.

## Visible Order Contract
### Images
1. `عملیات گروهی همه تصاویر منتخب سایت`
2. existing image toolbar/gallery

### Content / SEO
1. `هویت واقعی محصول در منبع — قبل از ترجمه و SEO`
2. `اصلاح نام محصول و بازسازی متن / SEO`
3. existing content toolbar/editor

## Implementation
- new additive layout-only layer: `catalog_center/app/phase49_3i20_visible_operator_panels.py`,
- final same-phase composition in `catalog_center/app/phase49_3i_pricing_modes.py`, after 49.3I.18 and 49.3I.19 installers,
- no recreation of AI/metadata controls,
- no command replacement,
- no database/schema change,
- no pricing/publish/FTP/Bridge change.

## Regression Tests
`catalog_center/tests/test_phase49_3i20_visible_operator_panels.py` verifies:
- bulk image panel is moved before expandable image content,
- source identity panel is first in Content/SEO,
- manual identity/AI rebuild panel is immediately below it,
- missing panels are a safe no-op.

## Required Windows Gate
1. close Catalog Center,
2. verify clean `D:\projects\3DPrintHub` worktree,
3. fetch/switch/ff-only pull exact feature branch,
4. verify Local HEAD equals fetched remote HEAD,
5. `py_compile` the 49.3I.20 module and touched composition module,
6. run 49.3I.20 + 49.3I.19 + 49.3I.18 focused tests,
7. run inherited 49.3I.16/15/discovery regressions,
8. run `catalog_center\launch.py --verify-only`,
9. open a Product Workspace and visually verify the image bulk panel is immediately visible in stage 3,
10. open stage 4 and verify both source-identity and AI rebuild panels are immediately visible above the editor,
11. verify product `2896217` source repair and rebuild still work,
12. verify clipboard/bulk metadata/manual Persian title still work.

Do not deploy Production until the Local automated gate, visual/data QA, one Local Publish E2E, and explicit owner approval pass.
