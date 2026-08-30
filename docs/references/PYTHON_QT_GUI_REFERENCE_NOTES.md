# Python Qt GUI Reference Notes for 3DPrintHub

Updated: 2026-08-30

These notes summarize the project-relevant ideas extracted from the owner's two purchased PyQt5 references. They are an original engineering index, not a copy of the books.

## References

1. Martin Fitzpatrick — *Create GUI Applications with Python & Qt5*.
2. *Python GUI Applications using PyQt5* — hands-on reference supplied by the owner.

## Topic → 3DPrintHub application map

### Application shell
Reference topics:
- QApplication/event loop,
- QMainWindow,
- windows,
- status bar,
- menu bar,
- toolbar.

3DPrintHub:
- one stable QMainWindow shell,
- route stack in the center,
- persistent sidebar,
- grouped toolbar for frequent commands,
- status bar for current operation/DB state.

### Signals / slots
Reference topics:
- widget signals,
- custom slots,
- state propagation,
- custom signals.

3DPrintHub:
- user action emits/dispatches intent;
- domain operation is separate from the widget;
- worker completion reports back through signals;
- UI thread owns widgets.

### Layouts / responsive structure
Reference topics:
- QVBoxLayout,
- QHBoxLayout,
- QGridLayout,
- QStackedLayout/QStackedWidget,
- QSplitter.

3DPrintHub:
- no new absolute-positioned production UI;
- QStackedWidget is route/wizard authority;
- QSplitter for dense Product/Filament/Image workspaces;
- Grid/Form layouts for operator input.

### Widgets / forms
Reference topics:
- QLineEdit,
- QComboBox,
- QListWidget,
- QCheckBox,
- QRadioButton,
- QSpinBox,
- QDoubleSpinBox,
- QProgressBar,
- QTextEdit,
- QTabWidget.

3DPrintHub:
- editable ComboBoxes for reusable company/brand/material values;
- numeric controls for weights/rates/times;
- hierarchical check states for Filament groups;
- progress controls for crawl/AI/publish;
- tabs only when they represent peer subviews rather than workflow stages.

### Actions / menus / discoverability
Reference topics:
- QAction,
- shortcuts,
- grouped menus,
- toolbars,
- status tips.

Project rule:
- one semantic QAction per command;
- reuse the same QAction in menu/toolbar;
- toolbar only for common commands;
- stable logical menu hierarchy;
- unavailable action disabled, not mysteriously removed.

### Dialogs
Reference topics:
- QDialog,
- input/file/color/font/message dialogs.

3DPrintHub:
- focused Filament create/edit,
- selected-image metadata,
- provider diagnostics,
- confirmation/review,
- file/source selection;
- do not overload the main Product page with every editor.

### Qt Designer / resources
Reference topics:
- Qt Designer,
- QRC/QResource,
- compiled resources.

3DPrintHub:
- reusable components can be Designer-authored where it helps iteration;
- application icons/resources must have deterministic packaged paths;
- resource strategy is part of 42D before final executable cutover.

### QSS / themes
Reference topics:
- styles,
- palettes,
- icons,
- QSS and sub-controls.

3DPrintHub:
- global design tokens/QSS,
- light/dark parity,
- no large accumulation of per-widget inline styles,
- consistent selected/disabled/error/success states.

### Model/View
Reference topics:
- QListView/QTableView/QTreeView,
- QAbstractTableModel,
- tabular data,
- SQL models.

3DPrintHub:
- Product/Filament/Queue/Run lists use Model/View,
- view state is not the database,
- filters use proxy models,
- large inventories should not be recreated as hundreds of independent widgets.

### Concurrency / processes
Reference topics:
- threads/processes,
- QThreadPool/QRunnable,
- worker signals,
- QProcess/external commands.

3DPrintHub:
- network/AI/crawl/publish never blocks GUI event loop;
- worker thread never manipulates widgets directly;
- result/progress/error/finished return by signals;
- QProcess is preferred where real-time external-process communication is useful.

### Data / SQL
Reference topics:
- SQLite/remote SQL connectivity,
- QTableView + SQL models.

3DPrintHub:
- mature Catalog Database/domain repository remains authority;
- Qt UI must not create a second application database;
- direct Qt SQL models are optional for read-heavy views, but business writes should stay behind existing audited domain contracts.

### Plotting / dashboard
Reference topics:
- PyQtGraph,
- Matplotlib.

3DPrintHub future:
- operational throughput,
- AI cost,
- crawl success/failure,
- publish latency,
- Filament stock/cost trends.
Use plots only when they improve decisions; not as decoration.

### Distribution
Reference topics:
- packaging/distribution.

3DPrintHub:
- final Qt artifact must preserve persistent user data, Credential Store, Playwright/browser runtime and immutable release evidence;
- packaging approach is changed only after side-by-side validation.

## Permanent design rules

1. Workflow stages are explicit and stable.
2. Main navigation stays visible.
3. Same command = same QAction/shortcut/meaning.
4. No long-running operation on the GUI thread.
5. No UI framework state as business-data authority.
6. Model/View for scalable collections.
7. Focused dialogs for complex secondary edits.
8. Stable error/loading/empty/success states.
9. Keyboard + mouse paths.
10. RTL is a first-class acceptance gate.
11. New UI must consume mature services instead of duplicating crawlers, AI, sync or pricing logic.
12. Default launcher switches only after complete side-by-side acceptance.
