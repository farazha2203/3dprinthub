# Phase49.3I.42 — Qt 6 Desktop Modernization

Updated: 2026-08-30  
Repository: `farazha2203/3dprinthub`  
Branch: `agent/phase49-3i18-operator-bulk-ai-rebuild`  
Status: `IN_PROGRESS / 42A OWNER VISUAL DIRECTION ACCEPTED / 42B1 GITHUB+WINDOWS CI TESTED / LEGACY RUNTIME PRESERVED / OWNER LOCAL PARITY QA NEXT / PRODUCTION NOT TOUCHED`

## Goal

Modernize Catalog Center from the mature Tkinter presentation layer into a maintainable Qt 6 desktop application without rewriting or destabilizing the proven Catalog, Crawl, AI, Product, Filament, Bridge, Publish and persistent-data contracts.

The new UI is based on the reusable application-design techniques in the two purchased PyQt5 references, but the implementation target is the current official Qt-for-Python generation: **PySide6 / Qt 6**.

The reference books are used for architecture and UX patterns, not copied source.

## Why Qt 6 / PySide6 instead of a new PyQt5 rewrite

The purchased books are PyQt5/Qt5 references and remain highly relevant for Qt concepts:
- QMainWindow application structure,
- signals/slots,
- layouts,
- actions/menus/toolbars,
- dialogs,
- QStackedWidget routing,
- Model/View,
- QSS/theming,
- resources,
- threading/processes,
- packaging.

For a new 2026 presentation layer, Phase49.3I.42 uses PySide6 instead of freezing the rewrite on Qt5. The legacy Tk runtime stays available until the Qt application passes side-by-side acceptance.

Pinned preview dependency:
`PySide6==6.11.2`.

## Non-negotiable migration rule

This is **not** a big-bang rewrite.

The proven business/data modules remain authoritative. The Qt layer consumes those contracts and is developed in parallel.

Default mature launcher remains:
`catalog_center/launch.py`.

Qt preview launcher:
`catalog_center/qt_launch.py`.

No Production deployment or default-launcher cutover is allowed until all Qt stages are accepted locally.

## 42A — Foundation — CI TESTED

Implemented:

### Application shell
- QMainWindow,
- permanent sidebar navigation,
- QStackedWidget route stack,
- menu bar,
- grouped quick-access toolbar,
- status bar,
- QSettings persistence for route/theme/window/splitter state,
- RTL application direction,
- light/dark QSS themes.

### Action architecture
A central Action Registry owns one semantic QAction per command. Menus, toolbar and command palette reuse the same QAction object. This prevents divergent duplicate commands and inconsistent shortcuts.

Current shortcuts:
- F5 refresh,
- Ctrl+1 dashboard,
- Ctrl+2 products,
- Ctrl+3 Product Wizard,
- Ctrl+4 Filaments,
- Ctrl+5 operations,
- Ctrl+K command palette,
- Ctrl+Shift+T theme,
- Ctrl+Q exit.

### Model/View
The first Qt models are:
- ProductTableModel,
- FilamentTableModel,
- FilamentFilterProxyModel.

The models use the mature Catalog SQLite and Epic49 Filament schema; no second data store is introduced.

### Wizard
A seven-stage QStackedWidget wizard shell maps the existing owner workflow:
1. title/category,
2. Filament/pricing/Profile,
3. images,
4. content/SEO,
5. source/license/specs,
6. homepage slider,
7. readiness/publish.

A stable StageStepper + previous/next footer makes the route explicit and predictable.

42A reads real selected Product facts. Owner accepted the visual shell direction in Local preview. 42B1 now provides the first real edit/image parity adapters; editing authority for the remaining Stages stays in the mature Workspace until each adapter is migrated and tested.

### Responsive long-running work contract
`qt6/workers.py` provides QThreadPool + QRunnable + Signal-based result/error/progress/finished transport.

Qt UI code must not call Tkinter.

This is the replacement direction for the historical Tk cross-thread workaround, not a second Tk bridge.

### Filament
Qt Filament list uses the global Phase49.3I.41 library and Model/View filtering by:
- material,
- manufacturer,
- brand,
- color.

It does not create a parallel Filament database.

## 42B — Full Product Wizard adapters — IN PROGRESS

### 42B1 — Application Kernel + first Legacy parity adapters — CI TESTED

Owner Local preview confirmed the shell/menu/navigation direction is good and identified the correct next requirement: functional parity with the mature Catalog Center.

Implemented:
- one `ApplicationKernel` composition root;
- one reusable object per core capability through `CoreRegistry`;
- ProductCore, ImageCore, FilamentCore, AcquisitionCore, PublishCore and one process-wide AICore;
- Qt pages consume these Core objects instead of creating page-specific engines;
- Product Explorer gains an icon/card gallery backed by local persisted Product images;
- Product detail preview and direct edit/Wizard route;
- Stage 1 is a real editor for title/category;
- finalized Quick Stage blocks writes until the operator explicitly selects `اصلاح مرحله`;
- Stage 3 renders actual local Product images;
- no network image fetch is introduced by Product gallery display;
- no mature Tk domain contract is removed.

Verification:
- code `0b826dccabcb3d98d5f5b4cca6543d7547ff8773`;
- Qt6 CI `33319343447` PASS;
- Single Active AI `33319343464` PASS.

42B1 is not full parity. Stage 2–7 editing, AI/Crawl operations and final cutover remain open.

### 42B2 — Next exact implementation target

Move the complete mature Stage-2 operator workflow behind the kernel:
- manufacturer/brand/material/color selection;
- global reusable Filament inventory;
- Product-specific fixed pricing;
- formula/range pricing;
- production rows;
- Profile create/edit/clone/delete;
- existing lock/history/finalization semantics;
- no duplicate pricing or Filament authority.

Port the complete operator forms to Qt widgets while calling the same mature persistence/domain functions:
- Stage 1 identity/category,
- Stage 2 grouped Filament checklist + Product-fixed pricing + Profile editor,
- image gallery/metadata,
- content/SEO forms,
- source/license/specification review,
- slider/media controls,
- readiness/publish confirmation.

Requirements:
- editable QComboBox for reusable master values,
- QSpinBox/QDoubleSpinBox for numeric values,
- QCheckBox/tri-state where hierarchical selection is needed,
- QSplitter for resizeable dense work areas,
- dedicated dialogs for focused edit/create operations,
- field validation before save,
- per-stage dirty state and explicit save/finalize state.

## 42C — Operations / AI / Acquisition

Move user-facing long tasks to Qt workers with:
- visible progress,
- cancellation where underlying contract supports it,
- start/end/error status,
- no GUI access from worker thread,
- single-active-AI guard preserved,
- no provider/secret contract rewrite,
- crawl/parser/image/file acquisition authority preserved.

## 42D — Design system / resources / accessibility

- compiled/static resource strategy for icons and application assets,
- consistent icon semantics,
- tooltips/status tips for non-obvious actions,
- keyboard navigation,
- high-DPI validation,
- RTL/LTR mixed-content validation,
- empty/loading/error states,
- destructive-action confirmation,
- reusable dialogs,
- full light/dark theme parity.

## 42E — Packaging / cutover

Before changing the default launcher:
- evaluate Qt-native deployment tooling against existing PyInstaller + Playwright constraints;
- produce a reproducible Windows artifact;
- verify frozen browser runtime, Credential Store and persistent data profile;
- side-by-side owner acceptance with the legacy executable;
- only then switch the default Windows release to Qt.

Rollback must remain trivial until cutover.

## Source-derived application principles

The purchased references are distilled into these project rules:
- use QMainWindow for an application shell with menu, toolbar, status and central workspace;
- make common commands discoverable but do not duplicate every action everywhere;
- group commands logically;
- disable unavailable commands instead of making navigation unexpectedly disappear;
- prefer layout managers to absolute positioning;
- use QStackedWidget for deterministic routed/wizard pages;
- use Model/View for scalable table/tree data instead of manually populating widget rows;
- use signals/slots to decouple user actions from effects;
- move slow work out of the GUI event loop;
- use QSS/theming and reusable widgets rather than per-screen ad-hoc styling;
- use focused dialogs for operations that should not crowd the main workflow;
- persist user UI state separately from business data.

## First CI evidence

Initial workflow definition failed before a job was created because a `runner.temp` expression was resolved at an invalid job-level context.

Run:
`33299686593` — FAILED before jobs.

Fix:
resolve `CATALOG_DATA_ROOT` inside the Windows PowerShell step after the runner exists.

Corrected run:
`33299745502` — PASS.

Verified on Windows / Python 3.12:
- PySide6 install,
- compileall,
- 3I.42 Qt foundation tests,
- 3I.41 Filament regression,
- offscreen Qt structural launcher,
- mature legacy launcher verify,
- no-Tk import guard inside `catalog_center/qt6`.

Existing Single Active AI CI on the corrected head also passed:
`33299745499`.

## Safety

No Django migration.  
No Catalog schema migration.  
No Production change.  
No Host change.  
No secret change.  
No media rewrite.  
No default launcher replacement.

Rollback anchor:
`backup/pre-phase49-3i42-qt6-desktop-foundation-20260830` →
`753539b0d76ccf0d185e35add458925628812a44`.

## Owner acceptance gate for 42A

Before 42B is declared complete, owner Local preview must verify:
- startup on the canonical Windows environment,
- RTL shell,
- navigation,
- products list,
- Filament list/filter,
- Product → Wizard routing,
- seven-stage navigation,
- command palette,
- light/dark theme,
- window/splitter state restore,
- legacy app still launches unchanged.

Production remains out of scope until the complete Qt migration reaches an explicit cutover gate.
