from __future__ import annotations

from PySide6.QtCore import QByteArray, QSettings, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .actions import ActionRegistry, ActionSpec
from .command_palette import CommandPalette
from .kernel import ApplicationKernel, build_kernel
from .pages import (
    DashboardPage,
    FilamentsPage,
    OperationsPage,
    ProductWizardPage,
    ProductsPage,
    SettingsPage,
)
from .theme import apply_theme
from .workers import TaskPool


NAV_ITEMS = (
    ("dashboard", "داشبورد"),
    ("products", "محصولات"),
    ("wizard", "ویزارد محصول"),
    ("filaments", "فیلامنت‌ها"),
    ("operations", "عملیات"),
    ("settings", "تنظیمات"),
)


class MainWindow(QMainWindow):
    def __init__(self, runtime, parent=None) -> None:
        super().__init__(parent)
        self.kernel = (
            runtime
            if isinstance(runtime, ApplicationKernel)
            else build_kernel(runtime)
        )
        self.db = self.kernel.db
        self.settings = QSettings("3DPrintHub", "CatalogCenterQt6")
        self.task_pool = TaskPool()
        self._route_to_index: dict[str, int] = {}
        self._route_to_nav_row: dict[str, int] = {}
        self._current_theme = str(self.settings.value("theme", "light"))

        self._build_window()
        self._build_actions()
        self._build_menu_and_toolbar()
        self._restore_ui_state()
        self.navigate(str(self.settings.value("route", "dashboard")))
        self.refresh_current_page()

    def _build_window(self) -> None:
        self.setWindowTitle("3DPrintHub Catalog Center — Qt 6")
        self.resize(1580, 940)
        self.setMinimumSize(1220, 760)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setChildrenCollapsible(False)
        self.main_splitter = splitter

        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(220)
        sidebar.setMaximumWidth(320)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 18, 14, 14)

        brand = QLabel("3DPrintHub")
        brand.setObjectName("BrandTitle")
        subtitle = QLabel("Catalog Center • Qt 6")
        subtitle.setObjectName("BrandSubtitle")
        side_layout.addWidget(brand)
        side_layout.addWidget(subtitle)

        self.nav = QListWidget()
        self.nav.setObjectName("Navigation")
        for row, (key, label) in enumerate(NAV_ITEMS):
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.nav.addItem(item)
            self._route_to_nav_row[key] = row
        self.nav.currentRowChanged.connect(self._navigate_from_sidebar)
        side_layout.addWidget(self.nav, 1)

        version_hint = QLabel(
            "Qt6 Legacy Parity\n"
            "Application Kernel فعال\n"
            "Legacy launcher حفظ شده"
        )
        version_hint.setObjectName("BrandSubtitle")
        version_hint.setWordWrap(True)
        side_layout.addWidget(version_hint)

        content_host = QWidget()
        content_layout = QVBoxLayout(content_host)
        content_layout.setContentsMargins(18, 16, 18, 16)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        self.dashboard_page = DashboardPage(self.db, self.navigate)
        self.products_page = ProductsPage(
            self.db,
            self.open_product,
            kernel=self.kernel,
        )
        self.wizard_page = ProductWizardPage(
            self.db,
            kernel=self.kernel,
        )
        self.filaments_page = FilamentsPage(
            self.db,
            kernel=self.kernel,
        )
        self.operations_page = OperationsPage(
            self.db,
            kernel=self.kernel,
        )
        self.settings_page = SettingsPage(
            self.db,
            kernel=self.kernel,
        )

        self._normalize_numeric_controls()

        for key, page in (
            ("dashboard", self.dashboard_page),
            ("products", self.products_page),
            ("wizard", self.wizard_page),
            ("filaments", self.filaments_page),
            ("operations", self.operations_page),
            ("settings", self.settings_page),
        ):
            self._route_to_index[key] = self.stack.addWidget(page)

        splitter.addWidget(sidebar)
        splitter.addWidget(content_host)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.status_message = QLabel("آماده")
        self.statusBar().addWidget(self.status_message, 1)

        self.status_db = QLabel(f"DB: {self.db.path.name}")
        self.statusBar().addPermanentWidget(self.status_db)

    def _normalize_numeric_controls(self) -> None:
        """Keep numeric editors readable in an RTL application.

        Qt/Windows otherwise places spin buttons over localized digits. Numeric
        input remains keyboard/mouse-wheel editable; broken +/- chrome is hidden.
        """
        for widget in self.findChildren(QAbstractSpinBox):
            widget.setButtonSymbols(
                QAbstractSpinBox.ButtonSymbols.NoButtons
            )
            widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            try:
                widget.lineEdit().setAlignment(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter
                )
            except Exception:
                pass
            widget.setMinimumWidth(max(100, widget.minimumWidth()))

    def _build_actions(self) -> None:
        self.actions = ActionRegistry(self)

        self.actions.register(
            ActionSpec(
                "refresh",
                "بروزرسانی",
                "F5",
                "بروزرسانی صفحه فعلی و داده‌های Model/View",
                toolbar=True,
            ),
            self.refresh_current_page,
        )
        self.actions.register(
            ActionSpec("dashboard", "داشبورد", "Ctrl+1", "رفتن به داشبورد"),
            lambda: self.navigate("dashboard"),
        )
        self.actions.register(
            ActionSpec("products", "محصولات", "Ctrl+2", "رفتن به محصولات"),
            lambda: self.navigate("products"),
        )
        self.actions.register(
            ActionSpec(
                "wizard",
                "ویزارد محصول",
                "Ctrl+3",
                "رفتن به ویرایش هفت‌مرحله‌ای محصول",
                toolbar=True,
            ),
            lambda: self.navigate("wizard"),
        )
        self.actions.register(
            ActionSpec(
                "filaments",
                "فیلامنت‌ها",
                "Ctrl+4",
                "رفتن به کتابخانه Filament",
                toolbar=True,
            ),
            lambda: self.navigate("filaments"),
        )
        self.actions.register(
            ActionSpec("operations", "عملیات", "Ctrl+5", "رفتن به مرکز عملیات"),
            lambda: self.navigate("operations"),
        )
        self.actions.register(
            ActionSpec(
                "settings",
                "تنظیمات",
                "Ctrl+6",
                "تنظیم Provider AI و اتصال سایت",
                toolbar=True,
            ),
            lambda: self.navigate("settings"),
        )
        self.actions.register(
            ActionSpec(
                "palette",
                "فرمان سریع",
                "Ctrl+K",
                "جستجوی فرمان‌های برنامه",
                toolbar=True,
            ),
            self.show_command_palette,
        )
        self.actions.register(
            ActionSpec(
                "theme",
                "تغییر پوسته",
                "Ctrl+Shift+T",
                "تغییر بین پوسته روشن و تیره",
            ),
            self.toggle_theme,
        )
        self.actions.register(
            ActionSpec(
                "about",
                "درباره نسخه Qt 6",
                "",
                "اطلاعات معماری رابط جدید",
            ),
            self.show_about,
        )
        self.actions.register(
            ActionSpec("exit", "خروج", "Ctrl+Q", "خروج از برنامه"),
            self.close,
        )

    def _build_menu_and_toolbar(self) -> None:
        file_menu = self.menuBar().addMenu("فایل")
        file_menu.addAction(self.actions.action("refresh"))
        file_menu.addSeparator()
        file_menu.addAction(self.actions.action("exit"))

        navigate_menu = self.menuBar().addMenu("مسیرها")
        for key in (
            "dashboard",
            "products",
            "wizard",
            "filaments",
            "operations",
            "settings",
        ):
            navigate_menu.addAction(self.actions.action(key))

        view_menu = self.menuBar().addMenu("نمایش")
        view_menu.addAction(self.actions.action("palette"))
        view_menu.addAction(self.actions.action("theme"))

        help_menu = self.menuBar().addMenu("راهنما")
        help_menu.addAction(self.actions.action("about"))

        toolbar = QToolBar("دسترسی سریع", self)
        toolbar.setMovable(False)
        for key in ("refresh", "wizard", "filaments", "settings", "palette"):
            toolbar.addAction(self.actions.action(key))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        self.toolbar = toolbar

    def _navigate_from_sidebar(self, row: int) -> None:
        if 0 <= row < self.nav.count():
            key = str(
                self.nav.item(row).data(Qt.ItemDataRole.UserRole)
            )
            self.navigate(key, update_sidebar=False)

    def navigate(self, key: str, *, update_sidebar: bool = True) -> None:
        key = key if key in self._route_to_index else "dashboard"
        self.stack.setCurrentIndex(self._route_to_index[key])

        if update_sidebar:
            target_row = self._route_to_nav_row.get(key, 0)
            if self.nav.currentRow() != target_row:
                self.nav.blockSignals(True)
                self.nav.setCurrentRow(target_row)
                self.nav.blockSignals(False)

        self.settings.setValue("route", key)
        self.status_message.setText(
            f"مسیر: {dict(NAV_ITEMS).get(key, key)}"
        )
        self.refresh_current_page()

    def current_route(self) -> str:
        index = self.stack.currentIndex()
        for key, value in self._route_to_index.items():
            if value == index:
                return key
        return "dashboard"

    def refresh_current_page(self) -> None:
        page = self.stack.currentWidget()
        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            refresh()

        self.status_message.setText(
            f"{dict(NAV_ITEMS).get(self.current_route(), self.current_route())} "
            "بروزرسانی شد"
        )

    def open_product(self, product_id: int) -> None:
        self.wizard_page.load_product(int(product_id))
        self.navigate("wizard")
        self.status_message.setText(
            f"محصول #{int(product_id)} در ویزارد باز شد"
        )

    def show_command_palette(self) -> None:
        dialog = CommandPalette(self.actions, self)
        dialog.exec()

    def toggle_theme(self) -> None:
        self._current_theme = (
            "dark" if self._current_theme == "light" else "light"
        )
        apply_theme(QApplication.instance(), self._current_theme)
        self.settings.setValue("theme", self._current_theme)
        self.status_message.setText(
            "پوسته تیره فعال شد"
            if self._current_theme == "dark"
            else "پوسته روشن فعال شد"
        )

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            "3DPrintHub Catalog Center — Qt 6",
            "Phase49.3I.42B2-B4 Candidate\n\n"
            "Qt6 Shell + shared Application Kernel + Filament CRUD + "
            "Profile Matrix + Images/SEO/Source/Slider editors + "
            "AI Provider Hub + Site Connection.\n\n"
            "Legacy launch.py تا پایان Acceptance و Cutover حفظ می‌شود.",
        )

    def _restore_ui_state(self) -> None:
        app = QApplication.instance()
        self._current_theme = apply_theme(app, self._current_theme)

        geometry = self.settings.value("geometry")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)

        splitter_state = self.settings.value("splitter")
        if isinstance(splitter_state, QByteArray):
            self.main_splitter.restoreState(splitter_state)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitter", self.main_splitter.saveState())
        self.settings.setValue("theme", self._current_theme)
        self.settings.sync()
        super().closeEvent(event)

    def structural_contract(self) -> dict[str, object]:
        kernel_contract = self.kernel.contract()
        return {
            "routes": tuple(self._route_to_index),
            "nav_count": self.nav.count(),
            "stack_count": self.stack.count(),
            "wizard_stages": self.wizard_page.stack.count(),
            "action_count": len(list(self.actions.items())),
            "threadpool_max": self.task_pool.max_threads,
            "theme": self._current_theme,
            "core_names": kernel_contract["cores"],
            "ai_single_engine": kernel_contract["ai_single_engine"],
            "ai_bound": kernel_contract["ai_bound"],
            "stage_authority_shared": kernel_contract["stage_authority_shared"],
        }
