from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QSortFilterProxyModel, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabBar,
    QTabWidget,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.db import utc_now
from app.phase49_3h_image_limits import HARD_MAX_IMAGE_LIMIT

from .diagnostics import show_diagnostic_error
from .models import (
    SORT_ROLE,
    FilamentFilterProxyModel,
    FilamentTableModel,
    ProductTableModel,
)
from .parity_dialogs import ColorPresetDialog, FilamentEditorDialog
from .product_explorer import (
    ProductGalleryModel,
    ProductStatusDelegate,
    product_lifecycle_status,
    product_seo_ready,
)
from .product_wizard import ProductWizardPage
from .settings_page import SettingsPage
from .widgets import MetricCard
from .workers import TaskPool, Worker


def _title_block(title: str, subtitle: str) -> QWidget:
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 8)
    title_label = QLabel(title)
    title_label.setStyleSheet("font-size: 22px; font-weight: 700;")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("Muted")
    subtitle_label.setWordWrap(True)
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    return box


class DashboardPage(QWidget):
    def __init__(self, db, navigate: Callable[[str], None], parent=None) -> None:
        super().__init__(parent)
        self.db = db
        self.navigate = navigate
        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "داشبورد عملیات",
            "وضعیت کاتالوگ، انتشار، خطاها و موجودی Filament در یک نگاه.",
        ))

        self.cards: dict[str, MetricCard] = {}
        grid = QGridLayout()
        specs = [
            ("total", "کل محصولات"),
            ("new_count", "جدید"),
            ("update_count", "نیازمند بروزرسانی"),
            ("queue_count", "صف انتشار"),
            ("published_count", "منتشرشده"),
            ("error_count", "خطا"),
            ("filaments", "Filament فعال"),
        ]
        for idx, (key, label) in enumerate(specs):
            card = MetricCard(label)
            self.cards[key] = card
            grid.addWidget(card, idx // 4, idx % 4)
        root.addLayout(grid)

        quick = QFrame()
        quick.setObjectName("Card")
        quick_layout = QHBoxLayout(quick)
        for label, key in (
            ("محصولات", "products"),
            ("ویزارد محصول", "wizard"),
            ("Filamentها", "filaments"),
            ("افزودن محصولات / Crawl", "operations"),
            ("تنظیمات", "settings"),
        ):
            button = QPushButton(label)
            if key == "wizard":
                button.setProperty("primary", True)
            button.clicked.connect(
                lambda _checked=False, route=key: self.navigate(route)
            )
            quick_layout.addWidget(button)
        quick_layout.addStretch(1)
        root.addWidget(quick)
        root.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        counts = self.db.status_counts()
        for key, card in self.cards.items():
            if key == "filaments":
                try:
                    count = int(self.db.conn.execute(
                        "SELECT COUNT(*) total FROM available_filament_offers WHERE is_active=1"
                    ).fetchone()["total"])
                except Exception:
                    count = 0
                card.set_value(count)
            else:
                card.set_value(counts.get(key, 0))


class ProductsPage(QWidget):
    def __init__(
        self,
        db,
        open_product: Callable[[int], None],
        parent=None,
        *,
        kernel=None,
        navigate: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent)
        if kernel is None:
            raise RuntimeError("ProductsPage requires ApplicationKernel")
        self.db = db
        self.kernel = kernel
        self.open_product = open_product
        self.navigate = navigate
        self.ai_pool = TaskPool()
        self.publish_pool = TaskPool()
        self.site_sync_pool = TaskPool()
        self._bulk_ai_worker: Worker | None = None
        self._bulk_publish_worker: Worker | None = None
        self._site_pull_worker: Worker | None = None

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "محصولات",
            "گالری تصویری + جدول قابل Sort با تصویر، تعداد عکس، توضیح و چرخه کامل محصول.",
        ))

        self.lifecycle_tabs = QTabBar()
        self.lifecycle_tabs.setExpanding(False)
        self.lifecycle_tabs.setDocumentMode(False)
        for label, code in (
            ("محصولات فعال", "all"),
            ("ارسال / منتشرشده", "published"),
            ("آرشیو شده", "archived"),
            ("حذف / رد شده", "blocked"),
        ):
            index = self.lifecycle_tabs.addTab(label)
            self.lifecycle_tabs.setTabData(index, code)
        root.addWidget(self.lifecycle_tabs)

        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجو در عنوان، توضیح، شناسه یا لینک…")
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("جدیدترین", "newest")
        self.sort_combo.addItem("قدیمی‌ترین", "oldest")
        self.sort_combo.addItem("عنوان فارسی", "title_fa")
        self.sort_combo.addItem("عنوان اصلی", "source_title")
        self.sort_combo.addItem("وضعیت", "status")

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("فعال‌ها", "all")
        self.filter_combo.addItem("جدید", "new")
        self.filter_combo.addItem("درحال انجام", "work_queue")
        self.filter_combo.addItem("ارسال/منتشرشده", "published")
        self.filter_combo.addItem("خطادار", "error")
        self.filter_combo.addItem("آرشیو", "archived")
        self.filter_combo.addItem("رد/حذف‌شده", "blocked")

        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh)
        self.pull_site_btn = QPushButton("↻ دریافت تغییرات سایت")
        self.pull_site_btn.setToolTip(
            "Productهای سایت را با Revision Guard به Windows می‌آورد؛ "
            "تغییرات Local منتشرنشده هرگز خودکار overwrite نمی‌شوند."
        )
        self.pull_site_btn.clicked.connect(self._pull_site_products)
        crawl_btn = QPushButton("➕ افزودن محصول / Crawl")
        crawl_btn.setProperty("success", True)
        crawl_btn.clicked.connect(
            lambda: self.navigate("operations")
            if self.navigate
            else None
        )
        edit_btn = QPushButton("ویرایش محصول")
        edit_btn.setProperty("primary", True)
        edit_btn.clicked.connect(self._open_selected)
        self.open_source_btn = QPushButton("🌐 باز کردن صفحه محصول")
        self.open_source_btn.setToolTip("صفحه منبع همان Product انتخاب‌شده را در مرورگر باز می‌کند.")
        self.open_source_btn.clicked.connect(self._open_source_selected)

        bar.addWidget(self.search, 1)
        bar.addWidget(QLabel("نمایش"))
        bar.addWidget(self.filter_combo)
        bar.addWidget(QLabel("مرتب‌سازی گالری"))
        bar.addWidget(self.sort_combo)
        bar.addWidget(refresh_btn)
        bar.addWidget(self.pull_site_btn)
        bar.addWidget(crawl_btn)
        bar.addWidget(self.open_source_btn)
        bar.addWidget(edit_btn)
        root.addLayout(bar)

        bulk_bar = QHBoxLayout()
        self.archive_btn = QPushButton("آرشیو انتخاب‌شده‌ها")
        self.remove_btn = QPushButton("حذف از محصولات / رد")
        self.restore_btn = QPushButton("بازیابی انتخاب‌شده‌ها")
        self.bulk_ai_source = QComboBox()
        for item in self.kernel.providers.source_modes():
            self.bulk_ai_source.addItem(item["label"], item["code"])
        link_index = self.bulk_ai_source.findData("link")
        if link_index >= 0:
            self.bulk_ai_source.setCurrentIndex(link_index)
        self.bulk_ai_btn = QPushButton("✨ AI تکمیل همه موارد انتخاب‌شده")
        self.bulk_ai_btn.setProperty("success", True)
        self.bulk_ai_status = QLabel("")
        self.bulk_ai_status.setObjectName("Muted")
        self.archive_btn.clicked.connect(self._archive_selected)
        self.remove_btn.clicked.connect(self._remove_selected)
        self.restore_btn.clicked.connect(self._restore_selected)
        self.bulk_ai_btn.clicked.connect(self._bulk_ai_selected)
        bulk_bar.addWidget(self.archive_btn)
        bulk_bar.addWidget(self.remove_btn)
        bulk_bar.addWidget(self.restore_btn)
        bulk_bar.addSpacing(12)
        bulk_bar.addWidget(QLabel("منبع AI"))
        bulk_bar.addWidget(self.bulk_ai_source)
        bulk_bar.addWidget(self.bulk_ai_btn)
        bulk_bar.addWidget(self.bulk_ai_status, 1)
        self.loaded_label = QLabel("")
        self.loaded_label.setObjectName("Muted")
        bulk_bar.addWidget(self.loaded_label)
        root.addLayout(bulk_bar)

        publish_bar = QHBoxLayout()
        publish_bar.addWidget(QLabel("انتشار سایت"))
        self.ready_publish_btn = QPushButton("✅ آماده انتشار انتخاب‌شده‌ها")
        self.ready_publish_btn.setToolTip(
            "همه Gateهای واقعی Product را بررسی می‌کند و فقط موارد کامل را وارد صف انتشار می‌کند."
        )
        self.bulk_publish_btn = QPushButton("🚀 انتشار انتخاب‌شده‌های آماده روی سایت")
        self.bulk_publish_btn.setProperty("primary", True)
        self.bulk_publish_btn.setToolTip(
            "فقط Productهای تیک‌خورده و آماده Batch می‌شوند؛ موفقیت بعد از Bridge و بررسی عمومی سایت ثبت می‌شود."
        )
        self.bulk_publish_status = QLabel("")
        self.bulk_publish_status.setObjectName("Muted")
        self.ready_publish_btn.clicked.connect(self._mark_ready_selected)
        self.bulk_publish_btn.clicked.connect(self._publish_selected)
        publish_bar.addWidget(self.ready_publish_btn)
        publish_bar.addWidget(self.bulk_publish_btn)
        publish_bar.addWidget(self.bulk_publish_status, 1)
        root.addLayout(publish_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.tabs = QTabWidget()

        self.gallery_model = ProductGalleryModel(
            self.kernel.products,
            self.kernel.images,
            self,
        )
        self.gallery = QListView()
        self.gallery.setModel(self.gallery_model)
        self.gallery.setItemDelegate(ProductStatusDelegate(self.gallery))
        self.gallery.setViewMode(QListView.ViewMode.IconMode)
        self.gallery.setResizeMode(QListView.ResizeMode.Adjust)
        self.gallery.setMovement(QListView.Movement.Static)
        self.gallery.setWrapping(True)
        self.gallery.setWordWrap(True)
        self.gallery.setUniformItemSizes(True)
        self.gallery.setLayoutMode(QListView.LayoutMode.Batched)
        self.gallery.setBatchSize(10)
        self.gallery.setIconSize(QSize(190, 125))
        self.gallery.setGridSize(QSize(235, 250))
        self.gallery.setSpacing(6)
        self.gallery.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.gallery.doubleClicked.connect(lambda _index: self._open_selected())
        self.gallery.selectionModel().selectionChanged.connect(
            lambda *_args: self._selection_changed()
        )

        self.model = ProductTableModel(db)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.table.doubleClicked.connect(lambda _index: self._open_selected())
        self.table.selectionModel().selectionChanged.connect(
            lambda *_args: self._selection_changed()
        )

        self.tabs.addTab(self.gallery, "گالری")
        self.tabs.addTab(self.table, "جدول قابل مرتب‌سازی")
        self.tabs.currentChanged.connect(lambda _index: self._tab_changed())
        self.gallery.verticalScrollBar().valueChanged.connect(
            lambda _value: self._fetch_gallery_if_needed()
        )
        self.table.verticalScrollBar().valueChanged.connect(
            lambda _value: self._fetch_table_if_needed()
        )
        self.gallery_model.rowsInserted.connect(lambda *_args: self._update_loaded_label())
        self.gallery_model.modelReset.connect(self._update_loaded_label)
        self.model.rowsInserted.connect(lambda *_args: self._update_loaded_label())
        self.model.modelReset.connect(self._update_loaded_label)
        splitter.addWidget(self.tabs)

        detail = QFrame()
        detail.setObjectName("Card")
        detail.setMinimumWidth(320)
        detail.setMaximumWidth(430)
        detail_layout = QVBoxLayout(detail)

        self.preview = QLabel("محصولی انتخاب نشده است")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(240)
        self.preview.setWordWrap(True)

        self.detail_title = QLabel("—")
        self.detail_title.setWordWrap(True)
        self.detail_title.setStyleSheet("font-size: 16px; font-weight: 700;")

        self.detail_source_title = QLabel("")
        self.detail_source_title.setWordWrap(True)
        self.detail_source_title.setObjectName("Muted")

        self.detail_description = QPlainTextEdit()
        self.detail_description.setReadOnly(True)
        self.detail_description.setMaximumHeight(170)

        self.detail_meta = QLabel("")
        self.detail_meta.setObjectName("Muted")
        self.detail_meta.setWordWrap(True)

        selected_title = QLabel("محصولات انتخاب‌شده برای عملیات گروهی")
        selected_title.setStyleSheet("font-weight:700;")
        self.selected_products = QListWidget()
        self.selected_products.setMaximumHeight(180)
        self.selected_products.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.selected_products.setToolTip(
            "این لیست دقیقاً همان Productهایی است که عملیات گروهی روی آن‌ها اجرا می‌شود."
        )

        detail_open_source = QPushButton("🌐 باز کردن صفحه منبع")
        detail_open_source.clicked.connect(self._open_source_selected)
        detail_edit = QPushButton("ویرایش کامل محصول")
        detail_edit.setProperty("primary", True)
        detail_edit.clicked.connect(self._open_selected)

        detail_layout.addWidget(self.preview)
        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.detail_source_title)
        detail_layout.addWidget(self.detail_description)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addWidget(selected_title)
        detail_layout.addWidget(self.selected_products)
        detail_layout.addStretch(1)
        detail_layout.addWidget(detail_open_source)
        detail_layout.addWidget(detail_edit)

        splitter.addWidget(detail)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        root.addWidget(splitter, 1)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(220)
        self._search_timer.timeout.connect(
            lambda: self._apply_search(self.search.text())
        )
        self.search.textChanged.connect(
            lambda _value: self._search_timer.start()
        )
        self.sort_combo.currentIndexChanged.connect(self._apply_gallery_sort)
        self.filter_combo.currentIndexChanged.connect(self._filter_combo_changed)
        self.lifecycle_tabs.currentChanged.connect(self._lifecycle_changed)
        self.refresh()

    def _current_product_filter(self) -> str:
        return str(
            self.filter_combo.currentData() or "all"
        ) if hasattr(self, "filter_combo") else "all"

    def _apply_search(self, value: str) -> None:
        value = str(value or "").strip()
        filter_name = self._current_product_filter()
        self.model.refresh(search=value, filter_name=filter_name)
        self.gallery_model.refresh(
            value,
            str(self.sort_combo.currentData() or "newest"),
            filter_name,
        )
        self._update_loaded_label()
        self._selection_changed()

    def _apply_gallery_sort(self) -> None:
        self.gallery_model.refresh(
            self.search.text().strip(),
            str(self.sort_combo.currentData() or "newest"),
            self._current_product_filter(),
        )
        self._update_loaded_label()

    def _filter_combo_changed(self) -> None:
        filter_name = self._current_product_filter()
        lifecycle_map = {
            "published": "published",
            "archived": "archived",
            "blocked": "blocked",
        }
        target = lifecycle_map.get(filter_name, "all")
        for index in range(self.lifecycle_tabs.count()):
            if str(self.lifecycle_tabs.tabData(index) or "") == target:
                if self.lifecycle_tabs.currentIndex() != index:
                    self.lifecycle_tabs.blockSignals(True)
                    self.lifecycle_tabs.setCurrentIndex(index)
                    self.lifecycle_tabs.blockSignals(False)
                break
        self.refresh()

    def _lifecycle_changed(self, index: int) -> None:
        target = str(self.lifecycle_tabs.tabData(index) or "all")
        combo_index = self.filter_combo.findData(target)
        if combo_index >= 0 and self.filter_combo.currentIndex() != combo_index:
            self.filter_combo.blockSignals(True)
            self.filter_combo.setCurrentIndex(combo_index)
            self.filter_combo.blockSignals(False)
        self.refresh()

    def _apply_product_filter(self) -> None:
        self._filter_combo_changed()

    def _tab_changed(self) -> None:
        self._selection_changed()
        self._update_loaded_label()

    def _selection_changed(self) -> None:
        self._refresh_selected_products()
        self._refresh_detail()

    def _refresh_selected_products(self) -> None:
        if not hasattr(self, "selected_products"):
            return
        ids = self._selected_product_ids()
        self.selected_products.clear()
        for product_id in ids:
            row = self.kernel.products.get(product_id) or {}
            title = (
                str(row.get("title_fa") or "").strip()
                or str(row.get("source_title") or "").strip()
                or f"Product #{product_id}"
            )
            if bool(int(row.get("ai_completed_once") or 0)):
                marker = "🤖 AI تکمیل شده"
                source = str(row.get("ai_completed_source_mode") or "").strip()
                if source:
                    marker += f" • {source}"
            else:
                marker = "○ AI اجرا نشده"
            item = QListWidgetItem(f"{title}\n{marker}")
            item.setData(Qt.ItemDataRole.UserRole, int(product_id))
            self.selected_products.addItem(item)

    def _fetch_gallery_if_needed(self) -> None:
        bar = self.gallery.verticalScrollBar()
        if bar.maximum() <= 0 or bar.value() >= max(0, bar.maximum() - 180):
            if self.gallery_model.canFetchMore():
                self.gallery_model.fetchMore()
                self._update_loaded_label()

    def _fetch_table_if_needed(self) -> None:
        bar = self.table.verticalScrollBar()
        if bar.maximum() <= 0 or bar.value() >= max(0, bar.maximum() - 12):
            if self.model.canFetchMore():
                self.model.fetchMore()
                self._update_loaded_label()

    def _update_loaded_label(self) -> None:
        if not hasattr(self, "loaded_label"):
            return
        self.loaded_label.setText(
            f"گالری {self.gallery_model.loaded_count:,} از {self.gallery_model.total_count:,}"
            f"  •  جدول {self.model.loaded_count:,} از {self.model.total_count:,}"
            "  •  اسکرول برای ادامه"
        )

    def refresh(self) -> None:
        filter_name = self._current_product_filter()
        search = self.search.text().strip() if hasattr(self, "search") else ""
        self.model.refresh(search=search, filter_name=filter_name)
        self.gallery_model.refresh(
            search,
            str(self.sort_combo.currentData() or "newest")
            if hasattr(self, "sort_combo")
            else "newest",
            filter_name,
        )
        self._update_loaded_label()
        self._refresh_detail()

    def _selected_product_ids(self) -> list[int]:
        values: list[int] = []
        if self.tabs.currentIndex() == 0:
            for index in self.gallery.selectedIndexes():
                product_id = self.gallery_model.product_id_at(index.row())
                if product_id is not None:
                    values.append(int(product_id))
        else:
            for index in self.table.selectionModel().selectedRows():
                product_id = self.model.product_id_at(index.row())
                if product_id is not None:
                    values.append(int(product_id))
        return sorted(set(values))

    def _selected_product_id(self) -> int | None:
        values = self._selected_product_ids()
        return values[0] if values else None

    def _archive_selected(self) -> None:
        product_ids = self._selected_product_ids()
        if not product_ids:
            QMessageBox.warning(self, "محصولات", "حداقل یک محصول را انتخاب کن.")
            return
        count = self.kernel.products.archive_many(product_ids)
        self.refresh()
        QMessageBox.information(
            self,
            "آرشیو",
            f"{count} محصول به آرشیو محلی منتقل شد.",
        )

    def _remove_selected(self) -> None:
        product_ids = self._selected_product_ids()
        if not product_ids:
            QMessageBox.warning(self, "محصولات", "حداقل یک محصول را انتخاب کن.")
            return
        answer = QMessageBox.question(
            self,
            "حذف از محصولات / رد",
            (
                f"{len(product_ids)} محصول رد شود؟\n\n"
                "لینک، عنوان، منبع، علت/زمان رد و فقط یک Thumbnail کوچک نگه داشته "
                "می‌شود. محتوای سنگین، قیمت‌ها، تصاویر کامل و پوشه دریافت‌شده پاک "
                "می‌شوند و Crawler همان هویت را دوباره وارد نمی‌کند.\n\n"
                "بازیابی بعدی یعنی آزادکردن هویت برای دریافت مجدد؛ دیتای سنگین قبلی "
                "برنمی‌گردد."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        count = self.kernel.products.remove_many(product_ids)
        self.refresh()
        QMessageBox.information(
            self,
            "رد/حذف",
            f"{count} محصول به وضعیت رد/حذف قابل‌بازیابی رفت.",
        )

    def _restore_selected(self) -> None:
        product_ids = self._selected_product_ids()
        if not product_ids:
            QMessageBox.warning(self, "محصولات", "حداقل یک محصول را انتخاب کن.")
            return
        count = self.kernel.products.restore_many(product_ids)
        self.refresh()
        QMessageBox.information(
            self,
            "بازیابی",
            f"{count} محصول بازیابی شد.",
        )

    def _mark_ready_selected(self) -> None:
        product_ids = self._selected_product_ids()
        if not product_ids:
            QMessageBox.warning(
                self,
                "آماده انتشار",
                "حداقل یک محصول را از گالری یا جدول انتخاب کن.",
            )
            return

        result = self.kernel.publish.mark_ready_many(product_ids)
        marked = int(result.get("marked") or 0)
        blocked = list(result.get("blocked") or [])
        self.refresh()

        detail = ""
        if blocked:
            lines = []
            for item in blocked[:8]:
                missing = "، ".join(list(item.get("missing") or [])[:3])
                lines.append(f"#{item.get('product_id')}: {missing}")
            detail = "\n\nموارد آماده‌نشده:\n" + "\n".join(lines)

        QMessageBox.information(
            self,
            "آمادگی انتشار",
            (
                f"{marked} محصول تیک «آماده انتشار» گرفت.\n"
                f"{len(blocked)} محصول به‌دلیل Gate ناقص وارد صف نشد."
                + detail
            ),
        )

    def _publish_selected(self) -> None:
        if self._bulk_publish_worker is not None:
            QMessageBox.information(
                self,
                "انتشار گروهی",
                "یک عملیات انتشار گروهی در حال اجرا است.",
            )
            return
        if self._bulk_ai_worker is not None:
            QMessageBox.information(
                self,
                "انتشار گروهی",
                "ابتدا عملیات AI گروهی جاری را تمام کن.",
            )
            return

        product_ids = self._selected_product_ids()
        if not product_ids:
            QMessageBox.warning(
                self,
                "انتشار گروهی",
                "حداقل یک محصول را انتخاب کن.",
            )
            return

        preflight = self.kernel.publish.preflight(product_ids)
        queued = list(preflight.get("queued_ids") or [])
        blocked = list(preflight.get("blocked") or [])
        ready_not_checked = sorted(
            set(preflight.get("publishable_ids") or []) - set(queued)
        )
        if not queued:
            message = (
                "هیچ Product انتخاب‌شده‌ای تیک «آماده انتشار» ندارد.\n\n"
                "ابتدا «آماده انتشار انتخاب‌شده‌ها» را بزن تا Gateها بررسی شوند."
            )
            if blocked:
                first = blocked[0]
                message += (
                    "\n\nنمونه نقص: #"
                    + str(first.get("product_id"))
                    + " • "
                    + "، ".join(list(first.get("missing") or [])[:4])
                )
            QMessageBox.warning(self, "انتشار گروهی", message)
            return

        answer = QMessageBox.question(
            self,
            "تأیید انتشار گروهی روی سایت",
            (
                f"محصول انتخاب‌شده: {len(product_ids)}\n"
                f"آماده و تیک‌خورده برای ارسال: {len(queued)}\n"
                f"کامل ولی بدون تیک آماده: {len(ready_not_checked)}\n"
                f"دارای نقص Gate: {len(blocked)}\n\n"
                "فقط Productهای آماده و تیک‌خورده Batch می‌شوند. "
                "بعد از FTP + Bridge + بررسی HTTP عمومی، موارد موفق خودکار "
                "به تب «ارسال / منتشرشده» منتقل می‌شوند.\n\n"
                "انتشار شروع شود؟"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.archive_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.restore_btn.setEnabled(False)
        self.bulk_ai_btn.setEnabled(False)
        self.ready_publish_btn.setEnabled(False)
        self.bulk_publish_btn.setEnabled(False)
        self.bulk_publish_status.setText(
            f"شروع انتشار {len(queued)} محصول…"
        )

        def job(progress):
            return self.kernel.publish.publish_many(
                product_ids,
                progress=progress,
            )

        worker = Worker(job)
        self._bulk_publish_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.bulk_publish_status.setText(
                f"{value}% • {message}"
            )
        )
        worker.signals.result.connect(self._bulk_publish_done)
        worker.signals.error.connect(self._bulk_publish_error)
        worker.signals.finished.connect(self._bulk_publish_finished)
        self.publish_pool.start(worker)

    def _bulk_publish_done(self, result=None) -> None:
        data = dict(result or {})
        published = int(data.get("published") or 0)
        failed = int(data.get("failed") or 0)
        skipped = int(data.get("skipped_count") or 0)
        self.bulk_publish_status.setText(
            f"✅ {published} منتشر • {failed} خطا • {skipped} رد Gate/بدون تیک"
        )

        if published:
            target = next(
                (
                    index
                    for index in range(self.lifecycle_tabs.count())
                    if str(self.lifecycle_tabs.tabData(index) or "") == "published"
                ),
                -1,
            )
            if target >= 0:
                self.lifecycle_tabs.setCurrentIndex(target)
            else:
                self.refresh()
        else:
            self.refresh()

        lines = []
        for item in list(data.get("items") or [])[:8]:
            if not item.get("ok"):
                lines.append(
                    f"#{item.get('product_id')}: "
                    f"{item.get('error') or item.get('status')}"
                )
        detail = ("\n\n" + "\n".join(lines)) if lines else ""
        QMessageBox.information(
            self,
            "نتیجه انتشار گروهی",
            (
                f"منتشرشده و HTTP-تأییدشده: {published}\n"
                f"ناموفق: {failed}\n"
                f"رد Gate / بدون تیک آماده: {skipped}\n"
                f"Batch: {data.get('batch_uuid') or '—'}"
                + detail
            ),
        )

    def _bulk_publish_error(self, detail: str) -> None:
        self.bulk_publish_status.setText("❌ انتشار گروهی ناموفق")
        self.refresh()
        show_diagnostic_error(
            self,
            "خطای انتشار گروهی سایت",
            detail,
            context={
                "product_count": len(self._selected_product_ids()),
                "publish_queue_count": len(self.kernel.publish.queue()),
            },
        )

    def _bulk_publish_finished(self) -> None:
        self._bulk_publish_worker = None
        self.archive_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.bulk_ai_btn.setEnabled(True)
        self.ready_publish_btn.setEnabled(True)
        self.bulk_publish_btn.setEnabled(True)

    def _pull_site_products(self) -> None:
        if self._site_pull_worker is not None:
            QMessageBox.information(
                self,
                "همگام‌سازی سایت",
                "دریافت تغییرات سایت هم‌اکنون در حال اجرا است.",
            )
            return
        self.pull_site_btn.setEnabled(False)
        self.bulk_publish_status.setText("در حال دریافت Productهای سایت…")

        def job(progress):
            return self.kernel.pull_site_products(progress=progress)

        worker = Worker(job)
        self._site_pull_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.bulk_publish_status.setText(
                f"{value}% • {message}"
            )
        )
        worker.signals.result.connect(self._site_pull_done)
        worker.signals.error.connect(self._site_pull_error)
        worker.signals.finished.connect(self._site_pull_finished)
        self.site_sync_pool.start(worker)

    def _site_pull_done(self, result=None) -> None:
        data = dict(result or {})
        self.refresh()
        self.bulk_publish_status.setText(
            "↻ Site Pull: "
            f"{int(data.get('created') or 0)} جدید • "
            f"{int(data.get('updated') or 0)} بروزشده • "
            f"{int(data.get('conflict_count') or 0)} تعارض"
        )
        details = []
        for item in list(data.get("conflicts") or [])[:6]:
            details.append(
                f"Local #{item.get('local_product_id')}: "
                f"Local r{item.get('local_revision')} / Site r{item.get('server_revision')}"
            )
        for item in list(data.get("failures") or [])[:4]:
            details.append(
                f"Site #{item.get('server_product_id')}: {item.get('error')}"
            )
        suffix = ("\n\n" + "\n".join(details)) if details else ""
        QMessageBox.information(
            self,
            "نتیجه دریافت تغییرات سایت",
            (
                f"Productهای بررسی‌شده: {int(data.get('requested') or 0)}\n"
                f"Mirror جدید: {int(data.get('created') or 0)}\n"
                f"بروزرسانی از سایت: {int(data.get('updated') or 0)}\n"
                f"بدون تغییر: {int(data.get('unchanged') or 0)}\n"
                f"تعارض محافظت‌شده: {int(data.get('conflict_count') or 0)}\n"
                f"خطا: {int(data.get('failed') or 0)}"
                + suffix
            ),
        )

    def _site_pull_error(self, detail: str) -> None:
        self.bulk_publish_status.setText("❌ دریافت تغییرات سایت ناموفق")
        show_diagnostic_error(
            self,
            "خطای دریافت Productهای سایت",
            detail,
            context={"operation": "site-product-pull"},
        )

    def _site_pull_finished(self) -> None:
        self._site_pull_worker = None
        self.pull_site_btn.setEnabled(True)

    def _bulk_ai_selected(self) -> None:
        if self._bulk_ai_worker is not None:
            QMessageBox.information(
                self,
                "AI گروهی",
                "یک عملیات AI گروهی در حال اجرا است.",
            )
            return
        product_ids = self._selected_product_ids()
        if not product_ids:
            QMessageBox.warning(
                self,
                "AI گروهی",
                "حداقل یک محصول را از گالری یا جدول انتخاب کن.",
            )
            return

        mode = str(self.bulk_ai_source.currentData() or "link")
        active = self.kernel.providers.active()
        quotes = []
        try:
            for product_id in product_ids:
                quotes.append(
                    self.kernel.providers.estimate_product_ai(
                        product_id,
                        mode,
                        target_stage=None,
                    )
                )
        except Exception as exc:
            QMessageBox.warning(self, "پیش‌بررسی AI گروهی", str(exc))
            return

        all_free = bool(quotes) and all(bool(item.get("free")) for item in quotes)
        all_known = bool(quotes) and all(bool(item.get("cost_known")) for item in quotes)
        if all_free:
            cost_text = "رایگان"
        elif all_known:
            usd = sum(float(item.get("estimated_usd") or 0) for item in quotes)
            toman = sum(float(item.get("estimated_toman") or 0) for item in quotes)
            cost_text = f"${usd:.6f}"
            if toman > 0:
                cost_text += f" • حدود {toman:,.0f} تومان"
        else:
            cost_text = "هزینه دقیق همه درخواست‌ها در Provider مشخص نیست"

        answer = QMessageBox.question(
            self,
            "تأیید AI گروهی",
            (
                f"تعداد محصولات: {len(product_ids)}\n"
                f"Provider: {active.get('provider') or '—'}\n"
                f"Model: {active.get('model') or '—'}\n"
                f"منبع: {self.bulk_ai_source.currentText()}\n"
                f"برآورد کل: {cost_text}\n\n"
                "همان «AI همه مراحل محتوایی» به‌صورت ترتیبی و با یک هسته "
                "واحد روی همه انتخاب‌ها اجرا شود؟"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.bulk_ai_btn.setEnabled(False)
        self.archive_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.restore_btn.setEnabled(False)
        self.ready_publish_btn.setEnabled(False)
        self.bulk_publish_btn.setEnabled(False)
        self.bulk_ai_status.setText(
            f"شروع AI گروهی برای {len(product_ids)} محصول…"
        )

        def job(progress):
            return self.kernel.complete_products_with_ai(
                product_ids,
                mode,
                progress=progress,
            )

        worker = Worker(job)
        self._bulk_ai_worker = worker
        worker.signals.progress.connect(
            lambda value, message: self.bulk_ai_status.setText(
                f"{value}% • {message}"
            )
        )
        worker.signals.result.connect(self._bulk_ai_done)
        worker.signals.error.connect(self._bulk_ai_error)
        worker.signals.finished.connect(self._bulk_ai_finished)
        self.ai_pool.start(worker)

    def _bulk_ai_done(self, result=None) -> None:
        data = dict(result or {})
        completed = int(data.get("completed") or 0)
        failed = int(data.get("failed") or 0)
        self.bulk_ai_status.setText(
            f"✅ {completed} تکمیل • {failed} خطا"
        )
        self.refresh()
        failures = list(data.get("failures") or [])
        detail = ""
        if failures:
            detail = "\n\n" + "\n".join(
                f"#{item.get('product_id')}: {item.get('error')}"
                for item in failures[:8]
            )
        QMessageBox.information(
            self,
            "AI گروهی",
            (
                f"{completed} محصول با همان موتور واحد Product AI پردازش شد.\n"
                f"{failed} مورد ناموفق بود."
                + detail
            ),
        )

    def _bulk_ai_error(self, detail: str) -> None:
        self.bulk_ai_status.setText("❌ AI گروهی ناموفق")
        active = self.kernel.providers.active()
        show_diagnostic_error(
            self,
            "خطای AI گروهی محصولات",
            detail,
            context={
                "provider": active.get("provider"),
                "model": active.get("model"),
                "source_mode": str(self.bulk_ai_source.currentData() or "link"),
                "product_count": len(self._selected_product_ids()),
            },
        )

    def _bulk_ai_finished(self) -> None:
        self._bulk_ai_worker = None
        self.bulk_ai_btn.setEnabled(True)
        self.archive_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.ready_publish_btn.setEnabled(True)
        self.bulk_publish_btn.setEnabled(True)

    def _refresh_detail(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None:
            self.preview.clear()
            self.preview.setText("محصولی انتخاب نشده است")
            self.detail_title.setText("—")
            self.detail_source_title.setText("")
            self.detail_description.setPlainText("")
            self.detail_meta.setText("")
            return

        row = self.kernel.products.get(product_id)
        if not row:
            return

        title = row.get("title_fa") or "بدون عنوان فارسی"
        source_title = row.get("source_title") or "—"
        self.detail_title.setText(f"#{product_id} — {title}")
        self.detail_source_title.setText(f"عنوان اصلی: {source_title}")
        self.detail_description.setPlainText(
            str(
                row.get("short_description_fa")
                or row.get("description_fa")
                or row.get("source_short_description")
                or row.get("source_description")
                or ""
            )
        )
        lifecycle = product_lifecycle_status(row)
        seo_text = "نهایی ✅" if product_seo_ready(row) else "ناقص/درحال تکمیل ⚠️"
        lifecycle_text = {
            "new": "جدید",
            "working": "درحال انجام",
            "published": "ارسال/منتشرشده",
            "rejected": "رد/حذف‌شده",
            "archived": "آرشیو",
        }.get(lifecycle, lifecycle)
        ai_text = "اجرا نشده"
        if bool(int(row.get("ai_completed_once") or 0)):
            ai_text = (
                f"تکمیل شده ✅ • {row.get('ai_completed_source_mode') or '—'}"
                f" • {row.get('ai_completed_provider') or '—'}"
                f" / {row.get('ai_completed_model') or '—'}"
            )
        rejected_lines = ""
        if lifecycle == "rejected":
            rejected_lines = (
                f"\nلینک نگهداری‌شده: {row.get('source_url') or '—'}"
                f"\nعلت رد: {row.get('blocked_reason') or '—'}"
                f"\nزمان رد: {row.get('blocked_at') or '—'}"
            )
        self.detail_meta.setText(
            f"منبع: {row.get('source_name') or row.get('source_code') or '—'}\n"
            f"وضعیت DB: {row.get('workflow_status') or '—'}\n"
            f"چرخه: {lifecycle_text}\n"
            f"تعداد تصاویر: {self.kernel.images.image_count(row)}\n"
            f"SEO: {seo_text}\n"
            f"AI: {ai_text}\n"
            f"دسته: {self.kernel.categories.label_for_slug(row.get('local_category_slug') or '')}\n"
            f"Server ID: {row.get('server_id') or '—'}"
            + rejected_lines
        )

        path = self.kernel.images.preferred_local_path(row)
        if not path:
            self.preview.clear()
            self.preview.setText("تصویر محلی قابل نمایش ندارد")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.preview.clear()
            self.preview.setText("خواندن تصویر محلی ناموفق بود")
            return

        self.preview.setPixmap(
            pixmap.scaled(
                355,
                265,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _open_source_selected(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None:
            QMessageBox.warning(self, "صفحه محصول", "یک محصول را انتخاب کن.")
            return
        row = self.kernel.products.get(product_id) or {}
        url = str(row.get("source_url") or "").strip()
        if not url.startswith(("http://", "https://")):
            QMessageBox.warning(self, "صفحه محصول", "لینک عمومی معتبر برای این محصول ثبت نشده است.")
            return
        if not QDesktopServices.openUrl(QUrl(url)):
            QMessageBox.warning(self, "صفحه محصول", "مرورگر سیستم نتوانست لینک محصول را باز کند.")

    def _open_selected(self) -> None:
        product_id = self._selected_product_id()
        if product_id is not None:
            self.open_product(product_id)


class FilamentsPage(QWidget):
    def __init__(self, db, parent=None, *, kernel=None) -> None:
        super().__init__(parent)
        if kernel is None:
            raise RuntimeError("FilamentsPage requires ApplicationKernel")
        self.db = db
        self.kernel = kernel
        self.site_pool = TaskPool()
        self._site_sync_worker: Worker | None = None

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "کتابخانه Filament",
            "چهار فضای مستقل برای فیلامنت‌ها، متریال‌ها، برندها و رنگ‌ها؛ متریال/برند/رنگ یک‌بار ساخته می‌شود و در ویرایش فیلامنت فقط انتخاب می‌گردد.",
        ))

        self.workspace_tabs = QTabWidget()
        self.workspace_tabs.setDocumentMode(False)
        root.addWidget(self.workspace_tabs, 1)

        # --------------------------------------------------------------
        # Filament inventory / pricing
        # --------------------------------------------------------------
        filament_page = QWidget()
        filament_layout = QVBoxLayout(filament_page)

        bar = QHBoxLayout()
        self.material = QComboBox()
        self.material.addItem("همه متریال‌ها")
        self.search = QLineEdit()
        self.search.setPlaceholderText("برند، رنگ، Finish یا متریال…")

        add_btn = QPushButton("فیلامنت جدید")
        add_btn.setProperty("primary", True)
        edit_btn = QPushButton("ویرایش فیلامنت")
        deactivate_btn = QPushButton("غیرفعال")
        self.site_sync_selected_btn = QPushButton("Sync انتخابی با سایت")
        self.site_sync_all_btn = QPushButton("Sync همه با سایت")
        self.site_sync_all_btn.setProperty("primary", True)
        refresh_btn = QPushButton("بروزرسانی")

        add_btn.clicked.connect(self._add_filament)
        edit_btn.clicked.connect(self._edit_filament)
        deactivate_btn.clicked.connect(self._deactivate_filament)
        self.site_sync_selected_btn.clicked.connect(self._sync_selected_site)
        self.site_sync_all_btn.clicked.connect(self._sync_all_site)
        refresh_btn.clicked.connect(self.refresh)

        bar.addWidget(QLabel("متریال"))
        bar.addWidget(self.material)
        bar.addWidget(self.search, 1)
        bar.addWidget(add_btn)
        bar.addWidget(edit_btn)
        bar.addWidget(deactivate_btn)
        bar.addWidget(self.site_sync_selected_btn)
        bar.addWidget(self.site_sync_all_btn)
        bar.addWidget(refresh_btn)
        filament_layout.addLayout(bar)

        self.site_sync_status = QLabel(
            "تغییرات Filament ابتدا در Catalog محلی ذخیره می‌شوند؛ Sync سایت از Bridge امن موجود استفاده می‌کند."
        )
        self.site_sync_status.setObjectName("Muted")
        self.site_sync_status.setWordWrap(True)
        filament_layout.addWidget(self.site_sync_status)

        self.model = FilamentTableModel(db)
        self.proxy = FilamentFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(90)
        header.setStretchLastSection(False)
        for column, width in enumerate(
            (145, 185, 245, 130, 120, 125, 145, 145, 130, 145)
        ):
            header.resizeSection(column, width)
        self.table.doubleClicked.connect(lambda _index: self._edit_filament())
        filament_layout.addWidget(self.table, 1)
        self.workspace_tabs.addTab(filament_page, "فیلامنت‌ها")

        # --------------------------------------------------------------
        # Material registry
        # --------------------------------------------------------------
        material_page = QWidget()
        material_layout = QVBoxLayout(material_page)
        material_hint = QLabel(
            "متریال مادر را یک‌بار تعریف کن. قیمت پایه هر کیلو و توضیح اختیاری "
            "برای مدیریت/SEO ثبت می‌شود؛ قیمت واقعی Filament همچنان از قیمت فروش رول ÷ وزن رول می‌آید."
        )
        material_hint.setWordWrap(True)
        material_hint.setObjectName("Muted")
        material_layout.addWidget(material_hint)

        material_actions = QHBoxLayout()
        add_material = QPushButton("➕ افزودن متریال")
        add_material.setProperty("primary", True)
        edit_material = QPushButton("ویرایش متریال")
        delete_material = QPushButton("حذف متریال بدون مصرف")
        add_material.clicked.connect(self._add_material)
        edit_material.clicked.connect(self._edit_material)
        delete_material.clicked.connect(self._delete_material)
        material_actions.addWidget(add_material)
        material_actions.addWidget(edit_material)
        material_actions.addWidget(delete_material)
        material_actions.addStretch(1)
        material_layout.addLayout(material_actions)

        self.material_table = QTableWidget(0, 3)
        self.material_table.setHorizontalHeaderLabels(
            ["نام متریال", "قیمت پایه هر کیلو (تومان)", "توضیح اختیاری"]
        )
        self.material_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.material_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.material_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.material_table.verticalHeader().setVisible(False)
        self.material_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.material_table.horizontalHeader().resizeSection(0, 220)
        self.material_table.horizontalHeader().resizeSection(1, 210)
        self.material_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.material_table.doubleClicked.connect(lambda _index: self._edit_material())
        material_layout.addWidget(self.material_table, 1)
        self.workspace_tabs.addTab(material_page, "متریال‌ها")

        # --------------------------------------------------------------
        # Brand registry
        # --------------------------------------------------------------
        brand_page = QWidget()
        brand_layout = QVBoxLayout(brand_page)
        brand_hint = QLabel(
            "برند شرکت/سازنده یک مرجع واحد است. برند را اینجا ثبت کن؛ سپس در فیلامنت جدید یا ویرایش فیلامنت انتخابش کن."
        )
        brand_hint.setWordWrap(True)
        brand_hint.setObjectName("Muted")
        brand_layout.addWidget(brand_hint)

        brand_actions = QHBoxLayout()
        add_brand = QPushButton("➕ افزودن برند")
        add_brand.setProperty("primary", True)
        edit_brand = QPushButton("ویرایش برند")
        delete_brand = QPushButton("حذف برند بدون مصرف")
        add_brand.clicked.connect(self._add_brand)
        edit_brand.clicked.connect(self._edit_brand)
        delete_brand.clicked.connect(self._delete_brand)
        brand_actions.addWidget(add_brand)
        brand_actions.addWidget(edit_brand)
        brand_actions.addWidget(delete_brand)
        brand_actions.addStretch(1)
        brand_layout.addLayout(brand_actions)

        self.brand_table = QTableWidget(0, 2)
        self.brand_table.setHorizontalHeaderLabels(["نام برند", "توضیح اختیاری"])
        self.brand_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.brand_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.brand_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.brand_table.verticalHeader().setVisible(False)
        self.brand_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.brand_table.horizontalHeader().resizeSection(0, 240)
        self.brand_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.brand_table.doubleClicked.connect(lambda _index: self._edit_brand())
        brand_layout.addWidget(self.brand_table, 1)
        self.workspace_tabs.addTab(brand_page, "برندها")

        # --------------------------------------------------------------
        # Reusable color / palette registry
        # --------------------------------------------------------------
        color_page = QWidget()
        color_layout = QVBoxLayout(color_page)
        color_hint = QLabel(
            "رنگ سایت را با Color Picker ویندوز بساز: تک‌رنگ، دو/چندرنگ، Gradient یا Color Shift و Finish مستقل. "
            "هر پالت حداکثر ۷ رنگ دارد و بعد در فیلامنت تخصیص داده می‌شود."
        )
        color_hint.setWordWrap(True)
        color_hint.setObjectName("Muted")
        color_layout.addWidget(color_hint)

        color_actions = QHBoxLayout()
        add_color = QPushButton("➕ رنگ جدید")
        add_color.setProperty("primary", True)
        edit_color = QPushButton("ویرایش رنگ")
        delete_color = QPushButton("حذف Preset سفارشی")
        add_color.clicked.connect(self._add_color)
        edit_color.clicked.connect(self._edit_color)
        delete_color.clicked.connect(self._delete_color)
        color_actions.addWidget(add_color)
        color_actions.addWidget(edit_color)
        color_actions.addWidget(delete_color)
        color_actions.addStretch(1)
        color_layout.addLayout(color_actions)

        self.color_table = QTableWidget(0, 4)
        self.color_table.setHorizontalHeaderLabels(
            ["نام رنگ", "رفتار", "Finish", "پالت HEX"]
        )
        self.color_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.color_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.color_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.color_table.verticalHeader().setVisible(False)
        self.color_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.color_table.horizontalHeader().resizeSection(0, 220)
        self.color_table.horizontalHeader().resizeSection(1, 150)
        self.color_table.horizontalHeader().resizeSection(2, 150)
        self.color_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        self.color_table.doubleClicked.connect(lambda _index: self._edit_color())
        color_layout.addWidget(self.color_table, 1)
        self.workspace_tabs.addTab(color_page, "رنگ‌ها")

        self.search.textChanged.connect(self._apply_filters)
        self.material.currentTextChanged.connect(self._apply_filters)
        self.refresh()

    def _reload_materials(self) -> None:
        current = self.material.currentText()
        self.material.blockSignals(True)
        self.material.clear()
        self.material.addItem("همه متریال‌ها")
        self.material.addItems(self.model.materials())
        index = self.material.findText(current)
        self.material.setCurrentIndex(index if index >= 0 else 0)
        self.material.blockSignals(False)

    def _apply_filters(self) -> None:
        query = self.search.text().strip()
        material = self.material.currentText().strip()
        self.proxy.set_material(
            material if material != "همه متریال‌ها" else ""
        )
        self.proxy.set_query(query)

    def _selected_row(self) -> dict | None:
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return None
        source_index = self.proxy.mapToSource(selected[0])
        return self.model.row_at(source_index.row())

    def _add_filament(self) -> None:
        dialog = FilamentEditorDialog(
            parent=self,
            filament_core=self.kernel.filaments,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        try:
            saved = self.kernel.filaments.save(dialog.values())
        except Exception as exc:
            QMessageBox.warning(self, "فیلامنت", str(exc))
            return
        self.refresh()
        enriched = self._filament_by_id(int(saved.get("id") or 0))
        if enriched:
            self._start_site_sync(
                [enriched],
                "Filament جدید محلی ذخیره شد؛ Sync سایت",
            )

    def _edit_filament(self) -> None:
        row = self._selected_row()
        if not row:
            QMessageBox.warning(self, "فیلامنت", "یک فیلامنت را انتخاب کن.")
            return
        dialog = FilamentEditorDialog(
            row,
            parent=self,
            filament_core=self.kernel.filaments,
        )
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        old_id = int(row.get("_row_id") or row.get("id") or 0)
        try:
            saved = self.kernel.filaments.save(
                dialog.values(),
                previous_row_id=old_id,
            )
        except Exception as exc:
            QMessageBox.warning(self, "فیلامنت", str(exc))
            return
        self.refresh()
        sync_rows: list[dict] = []
        new_id = int(saved.get("id") or 0)
        if old_id and new_id and old_id != new_id:
            old_payload = dict(row)
            old_payload["_site_active"] = False
            sync_rows.append(old_payload)
        enriched = self._filament_by_id(new_id)
        if enriched:
            sync_rows.append(enriched)
        if sync_rows:
            self._start_site_sync(
                sync_rows,
                "ویرایش Filament محلی ذخیره شد؛ Sync سایت",
            )

    def _deactivate_filament(self) -> None:
        row = self._selected_row()
        if not row:
            return
        if QMessageBox.question(
            self,
            "غیرفعال‌سازی",
            f"فیلامنت {row.get('material')} / {row.get('brand')} / {row.get('color')} غیرفعال شود؟",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.filaments.deactivate(
                int(row.get("_row_id") or row.get("id") or 0)
            )
        except Exception as exc:
            QMessageBox.warning(self, "فیلامنت", str(exc))
            return
        self.refresh()
        disabled = dict(row)
        disabled["_site_active"] = False
        self._start_site_sync(
            [disabled],
            "Filament محلی غیرفعال شد؛ Sync وضعیت سایت",
        )

    def _filament_by_id(self, row_id: int) -> dict | None:
        if int(row_id or 0) <= 0:
            return None
        return next(
            (
                dict(item)
                for item in self.kernel.filaments.list()
                if int(item.get("id") or 0) == int(row_id)
            ),
            None,
        )

    def _start_site_sync(self, rows: list[dict], label: str) -> None:
        payloads = [dict(item) for item in rows or [] if isinstance(item, dict)]
        if not payloads:
            self.site_sync_status.setText("Filament قابل Sync پیدا نشد.")
            return
        if self._site_sync_worker is not None:
            self.site_sync_status.setText(
                "یک Sync سایت در حال اجرا است؛ تغییر محلی ذخیره شد. پس از پایان «Sync همه با سایت» را بزن."
            )
            return

        def job(progress):
            return self.kernel.sync_filaments_with_site(
                payloads,
                progress=progress,
            )

        worker = Worker(job)
        self._site_sync_worker = worker
        self.site_sync_selected_btn.setEnabled(False)
        self.site_sync_all_btn.setEnabled(False)
        self.site_sync_status.setText(f"{label}…")
        worker.signals.progress.connect(
            lambda value, message: self.site_sync_status.setText(
                f"{value}% • {message}"
            )
        )
        worker.signals.result.connect(self._site_sync_done)
        worker.signals.error.connect(self._site_sync_error)
        worker.signals.finished.connect(self._site_sync_finished)
        self.site_pool.start(worker)

    def _site_sync_done(self, result=None) -> None:
        data = dict(result or {})
        synced = int(data.get("synced") or 0)
        failed = int(data.get("failed") or 0)
        self.site_sync_status.setText(
            f"✅ Sync سایت: {synced} موفق • {failed} خطا"
            if failed == 0
            else f"⚠️ Sync سایت: {synced} موفق • {failed} خطا؛ جزئیات در Retry بعدی حفظ می‌شود."
        )

    def _site_sync_error(self, detail: str) -> None:
        lines = [line.strip() for line in str(detail or "").splitlines() if line.strip()]
        short = lines[-1] if lines else "خطای نامشخص"
        self.site_sync_status.setText(
            f"⚠️ تغییر محلی محفوظ است؛ Sync سایت انجام نشد: {short}"
        )

    def _site_sync_finished(self) -> None:
        self._site_sync_worker = None
        self.site_sync_selected_btn.setEnabled(True)
        self.site_sync_all_btn.setEnabled(True)

    def _sync_selected_site(self) -> None:
        row = self._selected_row()
        if not row:
            QMessageBox.warning(self, "Sync سایت", "یک Filament را انتخاب کن.")
            return
        enriched = self._filament_by_id(
            int(row.get("_row_id") or row.get("id") or 0)
        ) or dict(row)
        self._start_site_sync([enriched], "Sync Filament انتخابی با سایت")

    def _sync_all_site(self) -> None:
        rows = self.kernel.filaments.list(include_inactive=True)
        if not rows:
            QMessageBox.information(self, "Sync سایت", "Filament برای Sync وجود ندارد.")
            return
        active_count = sum(1 for item in rows if bool(item.get("is_active", True)))
        inactive_count = len(rows) - active_count
        self._start_site_sync(
            rows,
            f"Sync کامل سایت: {active_count} فعال + {inactive_count} غیرفعال",
        )

    def _registry_sync_delta(
        self,
        before_rows: list[dict],
        *,
        field: str,
        new_name: str,
    ) -> list[dict]:
        target = str(new_name or "").strip().casefold()
        old_rows = [dict(item) for item in before_rows]
        active_after = [
            dict(item)
            for item in self.kernel.filaments.list()
            if str(item.get(field) or "").strip().casefold() == target
        ]
        old_names = {
            str(item.get(field) or "").strip().casefold()
            for item in old_rows
        }
        sync_rows: list[dict] = []
        if old_names and old_names != {target}:
            for item in old_rows:
                item["_site_active"] = False
                sync_rows.append(item)
        sync_rows.extend(active_after)
        return sync_rows

    def _reload_material_registry(self) -> None:
        records = self.kernel.filaments.material_records()
        self.material_table.setRowCount(len(records))
        for row_index, record in enumerate(records):
            values = [
                str(record.get("name") or ""),
                f"{int(record.get('price_per_kg') or 0):,}",
                str(record.get("description") or ""),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, dict(record))
                self.material_table.setItem(row_index, column, item)
            self.material_table.setRowHeight(row_index, 44)

    def _selected_material_record(self) -> dict | None:
        row = self.material_table.currentRow()
        if row < 0:
            return None
        item = self.material_table.item(row, 0)
        value = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        return dict(value) if isinstance(value, dict) else None

    def _material_editor(self, record: dict | None = None) -> None:
        current = dict(record or {})
        name, ok = QInputDialog.getText(
            self, "متریال", "نام متریال", text=str(current.get("name") or "")
        )
        if not ok:
            return
        description, ok = QInputDialog.getMultiLineText(
            self, "متریال", "توضیح اختیاری", str(current.get("description") or "")
        )
        if not ok:
            return
        price, ok = QInputDialog.getInt(
            self,
            "متریال",
            "قیمت پایه هر کیلو (تومان) — فقط مرجع متریال مادر",
            int(current.get("price_per_kg") or 0),
            0,
            2_000_000_000,
            1000,
        )
        if not ok:
            return
        previous_name = str(current.get("name") or "").strip()
        before_rows = [
            dict(item)
            for item in self.kernel.filaments.list()
            if str(item.get("material_name") or "").strip().casefold()
            == previous_name.casefold()
        ] if previous_name else []
        self.kernel.filaments.save_material(
            name,
            description,
            price,
            previous_name=previous_name,
        )
        self.refresh()
        sync_rows = self._registry_sync_delta(
            before_rows,
            field="material_name",
            new_name=name,
        )
        if sync_rows:
            self._start_site_sync(
                sync_rows,
                "متریال محلی بروزرسانی شد؛ Sync Filamentهای وابسته با سایت",
            )

    def _add_material(self) -> None:
        try:
            self._material_editor()
        except Exception as exc:
            QMessageBox.warning(self, "متریال", str(exc))

    def _edit_material(self) -> None:
        record = self._selected_material_record()
        if not record:
            QMessageBox.warning(self, "متریال", "یک متریال را انتخاب کن.")
            return
        try:
            self._material_editor(record)
        except Exception as exc:
            QMessageBox.warning(self, "متریال", str(exc))

    def _delete_material(self) -> None:
        record = self._selected_material_record()
        if not record:
            QMessageBox.warning(self, "متریال", "یک متریال را انتخاب کن.")
            return
        name = str(record.get("name") or "")
        if QMessageBox.question(self, "حذف متریال", f"متریال «{name}» حذف شود؟") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.filaments.delete_material(name)
        except Exception as exc:
            QMessageBox.warning(self, "متریال", str(exc))
            return
        self.refresh()

    def _reload_brands(self) -> None:
        records = self.kernel.filaments.brand_records()
        self.brand_table.setRowCount(len(records))
        for row_index, record in enumerate(records):
            values = [
                str(record.get("name") or ""),
                str(record.get("description") or ""),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, dict(record))
                self.brand_table.setItem(row_index, column, item)
            self.brand_table.setRowHeight(row_index, 44)

    def _selected_brand_record(self) -> dict | None:
        row = self.brand_table.currentRow()
        if row < 0:
            return None
        item = self.brand_table.item(row, 0)
        value = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        return dict(value) if isinstance(value, dict) else None

    def _brand_editor(self, record: dict | None = None) -> None:
        current = dict(record or {})
        name, ok = QInputDialog.getText(
            self, "برند", "نام برند", text=str(current.get("name") or "")
        )
        if not ok:
            return
        description, ok = QInputDialog.getMultiLineText(
            self, "برند", "توضیح اختیاری", str(current.get("description") or "")
        )
        if not ok:
            return
        previous_name = str(current.get("name") or "").strip()
        before_rows = [
            dict(item)
            for item in self.kernel.filaments.list()
            if str(item.get("brand_name") or "").strip().casefold()
            == previous_name.casefold()
        ] if previous_name else []
        self.kernel.filaments.save_brand(
            name,
            description,
            previous_name=previous_name,
        )
        self.refresh()
        sync_rows = self._registry_sync_delta(
            before_rows,
            field="brand_name",
            new_name=name,
        )
        if sync_rows:
            self._start_site_sync(
                sync_rows,
                "برند محلی بروزرسانی شد؛ Sync Filamentهای وابسته با سایت",
            )

    def _add_brand(self) -> None:
        try:
            self._brand_editor()
        except Exception as exc:
            QMessageBox.warning(self, "برند", str(exc))

    def _edit_brand(self) -> None:
        record = self._selected_brand_record()
        if not record:
            QMessageBox.warning(self, "برند", "یک برند را انتخاب کن.")
            return
        try:
            self._brand_editor(record)
        except Exception as exc:
            QMessageBox.warning(self, "برند", str(exc))

    def _delete_brand(self) -> None:
        record = self._selected_brand_record()
        if not record:
            QMessageBox.warning(self, "برند", "یک برند را انتخاب کن.")
            return
        name = str(record.get("name") or "")
        if QMessageBox.question(
            self,
            "حذف برند",
            f"برند «{name}» از کتابخانه ثبت‌شده حذف شود؟\nبرندِ در حال استفاده روی فیلامنت حذف نمی‌شود.",
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.kernel.filaments.delete_brand(name)
        except Exception as exc:
            QMessageBox.warning(self, "برند", str(exc))
            return
        self.refresh()

    def _reload_colors(self) -> None:
        presets = self.kernel.filaments.color_presets()
        self.color_table.setRowCount(len(presets))
        for row_index, preset in enumerate(presets):
            values = [
                str(preset.get("name") or ""),
                str(preset.get("color_type") or "solid"),
                str(preset.get("color_finish") or "matte"),
                "  →  ".join(str(value) for value in preset.get("palette_hexes") or []),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, dict(preset))
                self.color_table.setItem(row_index, column, item)
            self.color_table.setRowHeight(row_index, 42)

    def _selected_color_preset(self) -> dict | None:
        row = self.color_table.currentRow()
        if row < 0:
            return None
        item = self.color_table.item(row, 0)
        value = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        return dict(value) if isinstance(value, dict) else None

    def _add_color(self) -> None:
        dialog = ColorPresetDialog(parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        values = dialog.values()
        name = str(values.get("name") or "").strip()
        try:
            self.kernel.filaments.save_color_preset(values)
        except Exception as exc:
            QMessageBox.warning(self, "رنگ", str(exc))
            return
        self.refresh()
        affected = [
            dict(item)
            for item in self.kernel.filaments.list()
            if str(item.get("color_name") or "").strip().casefold()
            == name.casefold()
        ]
        if affected:
            self._start_site_sync(
                affected,
                "رنگ محلی ثبت شد؛ Sync Filamentهای وابسته با سایت",
            )

    def _edit_color(self) -> None:
        preset = self._selected_color_preset()
        if not preset:
            QMessageBox.warning(self, "رنگ", "یک رنگ را انتخاب کن.")
            return
        dialog = ColorPresetDialog(preset, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        previous_name = str(preset.get("name") or "").strip()
        before_rows = [
            dict(item)
            for item in self.kernel.filaments.list()
            if str(item.get("color_name") or "").strip().casefold()
            == previous_name.casefold()
        ]
        values = dialog.values()
        try:
            self.kernel.filaments.save_color_preset(
                values,
                previous_name=previous_name,
            )
        except Exception as exc:
            QMessageBox.warning(self, "رنگ", str(exc))
            return
        self.refresh()
        sync_rows = self._registry_sync_delta(
            before_rows,
            field="color_name",
            new_name=str(values.get("name") or ""),
        )
        if sync_rows:
            self._start_site_sync(
                sync_rows,
                "رنگ محلی بروزرسانی شد؛ Sync Filamentهای وابسته با سایت",
            )

    def _delete_color(self) -> None:
        preset = self._selected_color_preset()
        if not preset:
            QMessageBox.warning(self, "رنگ", "یک رنگ را انتخاب کن.")
            return
        name = str(preset.get("name") or "")
        if QMessageBox.question(
            self,
            "حذف Preset رنگ",
            f"Preset سفارشی «{name}» حذف شود؟\nفیلامنت‌های قبلی دست‌نخورده می‌مانند.",
        ) != QMessageBox.StandardButton.Yes:
            return
        self.kernel.filaments.delete_color_preset(name)
        self._reload_colors()

    def refresh(self) -> None:
        self.model.refresh()
        self._reload_materials()
        self._reload_material_registry()
        self._apply_filters()
        self._reload_brands()
        self._reload_colors()


class OperationsPage(QWidget):
    """Active Qt acquisition surface over mature 3I.38/43/45 collectors."""

    def __init__(
        self,
        db,
        parent=None,
        *,
        kernel=None,
        navigate: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent)
        if kernel is None:
            raise RuntimeError("OperationsPage requires ApplicationKernel")
        self.db = db
        self.kernel = kernel
        self.navigate = navigate
        self.pool = TaskPool()
        self._worker: Worker | None = None
        self._active_listing_url = ""
        self._active_source_code = ""
        self._active_run_started_at = ""
        self._live_product_progress: dict[str, str] = {}

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "دریافت و مدیریت محصولات سایت‌های مادر",
            "موجودی دائمی، دریافت جدید و History از هم جدا هستند تا هیچ کنترل بزرگی "
            "فضای مشاهده محصولات را نگیرد.",
        ))

        self.workspace_tabs = QTabWidget()
        self.workspace_tabs.setDocumentMode(False)
        root.addWidget(self.workspace_tabs, 1)

        # --------------------------------------------------------------
        # Tab 1: persistent inventory — the default operator workspace.
        # --------------------------------------------------------------
        inventory_page = QWidget()
        inventory_layout = QVBoxLayout(inventory_page)

        queue_card = QFrame()
        queue_card.setObjectName("Card")
        queue_layout = QVBoxLayout(queue_card)

        queue_header = QHBoxLayout()
        queue_header.addWidget(QLabel("موجودی دائمی Crawl / همه رکوردهای دیتابیس"))
        self.queue_filter = QComboBox()
        self.queue_filter.addItem("همه", "all")
        self.queue_filter.addItem("جدید", "new")
        self.queue_filter.addItem("Failed", "failed")
        self.queue_filter.addItem("دریافت‌شده", "collected")
        self.queue_filter.addItem("ردشده", "rejected")

        self.queue_view_mode = QComboBox()
        self.queue_view_mode.addItem("آیکون‌های بزرگ", "icons")
        self.queue_view_mode.addItem("جزئیات", "details")

        self.queue_open_btn = QPushButton("🌐 مشاهده صفحه محصول")
        self.queue_open_btn.setToolTip("صفحه اصلی Product انتخاب‌شده را در مرورگر باز می‌کند.")
        self.queue_collect_btn = QPushButton("افزودن به محصولات")
        self.queue_collect_btn.setToolTip(
            "همه رکوردهای انتخاب‌شده را دریافت/تطبیق می‌دهد و سپس صفحه محصولات را باز می‌کند."
        )
        self.queue_collect_btn.setProperty("primary", True)
        self.queue_collect_ai_btn = QPushButton("✨ افزودن + AI")
        self.queue_collect_ai_btn.setToolTip(
            "انتخاب‌شده‌ها را دریافت می‌کند و سپس ترجمه/SEO را با هسته واحد AI اجرا می‌کند."
        )
        self.queue_collect_ai_btn.setProperty("success", True)
        self.queue_reject_btn = QPushButton("رد / حذف")
        self.queue_restore_btn = QPushButton("بازگردانی به صف")
        self.queue_restore_btn.setToolTip(
            "فقط وضعیت rejected/failed را برای دریافت دوباره آزاد می‌کند؛ بازیابی داده/عکس دکمه جدا دارد."
        )
        self.queue_select_all_btn = QPushButton("انتخاب همه")
        self.queue_select_incomplete_btn = QPushButton("انتخاب ناقص‌ها")
        self.queue_select_incomplete_btn.setToolTip(
            "از رکوردهای لودشده، موارد بدون Product کامل، بدون عنوان/توضیح یا بدون عکس محلی را انتخاب می‌کند."
        )
        self.queue_clear_selection_btn = QPushButton("لغو انتخاب")
        self.queue_recover_image_limit = QComboBox()
        for count in (5, 10, 20):
            self.queue_recover_image_limit.addItem(f"{count} عکس", count)
        self.queue_recover_image_limit.setCurrentIndex(0)
        self.queue_recover_btn = QPushButton("بازیابی دیتا + عکس")
        self.queue_recover_btn.setProperty("success", True)
        self.queue_recover_btn.setToolTip(
            "برای همه انتخاب‌ها: اگر داده و تعداد عکس محلی کافی باشد همان را استفاده می‌کند؛ "
            "اگر ناقص باشد صفحه Product را دوباره می‌خواند و اطلاعات/عکس را امن بازیابی می‌کند."
        )
        self.queue_selected_label = QLabel("0 انتخاب‌شده")
        self.queue_selected_label.setObjectName("Muted")
        self.queue_loaded_label = QLabel("")
        self.queue_loaded_label.setObjectName("Muted")

        queue_header.addWidget(QLabel("فیلتر"))
        queue_header.addWidget(self.queue_filter)
        queue_header.addWidget(QLabel("نمایش"))
        queue_header.addWidget(self.queue_view_mode)
        queue_header.addWidget(self.queue_open_btn)
        queue_header.addStretch(1)
        queue_header.addWidget(self.queue_loaded_label)
        queue_layout.addLayout(queue_header)

        queue_select_actions = QHBoxLayout()
        queue_select_actions.addWidget(self.queue_select_all_btn)
        queue_select_actions.addWidget(self.queue_select_incomplete_btn)
        queue_select_actions.addWidget(self.queue_clear_selection_btn)
        queue_select_actions.addStretch(1)
        queue_select_actions.addWidget(self.queue_selected_label)
        queue_layout.addLayout(queue_select_actions)

        queue_data_actions = QHBoxLayout()
        queue_data_actions.addWidget(QLabel("تعداد عکس بازیابی"))
        queue_data_actions.addWidget(self.queue_recover_image_limit)
        queue_data_actions.addWidget(self.queue_recover_btn)
        queue_data_actions.addSpacing(12)
        queue_data_actions.addWidget(self.queue_collect_btn)
        queue_data_actions.addWidget(self.queue_collect_ai_btn)
        queue_data_actions.addWidget(self.queue_reject_btn)
        queue_data_actions.addWidget(self.queue_restore_btn)
        queue_data_actions.addStretch(1)
        queue_layout.addLayout(queue_data_actions)

        self.queue_views = QStackedWidget()

        self.queue_gallery = QListWidget()
        self.queue_gallery.setViewMode(QListWidget.ViewMode.IconMode)
        self.queue_gallery.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.queue_gallery.setMovement(QListWidget.Movement.Static)
        self.queue_gallery.setWrapping(True)
        self.queue_gallery.setWordWrap(True)
        self.queue_gallery.setIconSize(QSize(170, 118))
        self.queue_gallery.setGridSize(QSize(230, 235))
        self.queue_gallery.setSpacing(7)
        self.queue_gallery.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )

        self.queue_table = QTableWidget(0, 14)
        self.queue_table.setHorizontalHeaderLabels([
            "تصویر",
            "ID صف",
            "Source",
            "وضعیت",
            "Product ID",
            "عنوان",
            "توضیح",
            "عکس",
            "وزن g",
            "زمان چاپ",
            "ابعاد",
            "External ID",
            "Attempts",
            "URL / خطا",
        ])
        self.queue_table.setIconSize(QSize(70, 52))
        self.queue_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.queue_table.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self.queue_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.queue_table.verticalHeader().setVisible(False)
        self.queue_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.queue_table.horizontalHeader().setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.Stretch,
        )
        self.queue_table.horizontalHeader().setSectionResizeMode(
            13,
            QHeaderView.ResizeMode.Stretch,
        )

        self.queue_views.addWidget(self.queue_gallery)
        self.queue_views.addWidget(self.queue_table)
        queue_layout.addWidget(self.queue_views, 1)
        inventory_layout.addWidget(queue_card, 1)

        # --------------------------------------------------------------
        # Tab 2: receive / crawl controls.
        # --------------------------------------------------------------
        receive_page = QWidget()
        receive_layout = QVBoxLayout(receive_page)

        controls = QFrame()
        controls.setObjectName("Card")
        grid = QGridLayout(controls)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        self.source = QComboBox()
        self.mode = QComboBox()
        self.mode.addItem("Automatic — Listing پیش‌فرض Source", "automatic")
        self.mode.addItem("Search / Listing", "search")
        self.mode.addItem("Category URL", "category")
        self.mode.addItem("Site Crawl از لینک شروع", "site_crawl")
        self.mode.addItem("دریافت مستقیم یک Product", "single")
        search_mode_index = self.mode.findData("search")
        if search_mode_index >= 0:
            self.mode.setCurrentIndex(search_mode_index)

        self.strategy = QComboBox()
        self.strategy.addItem(
            "هوشمند پیشنهادی — HTTP/Sitemap + Browser",
            "hybrid",
        )
        self.strategy.addItem(
            "کلاسیک قدیمی — Search Link + Browser ادامه‌دار",
            "classic",
        )

        self.collection_method = QComboBox()
        for label, code in (
            ("Rich فعلی — DOM + JSON-LD + Embedded JSON + XHR", "rich"),
            ("Classic Isolated — روش قدیمی پایدار", "classic_isolated"),
            ("Classic Exact — HTML/DOM + Screenshot", "classic_exact"),
            ("Network Capture — XHR/Fetch JSON", "network_capture"),
            ("Chrome متصل 9222 — نشست مرورگر باز", "chrome_attached"),
            ("Saved HTML — فایل ذخیره‌شده", "saved_html"),
            ("Browser DOM — سازگاری نسخه قدیمی", "browser_dom"),
            ("Public HTTP — سازگاری نسخه قدیمی", "public_http"),
        ):
            self.collection_method.addItem(label, code)

        self.url = QLineEdit()
        self.url.setClearButtonEnabled(True)
        self.url.setPlaceholderText(
            "مثال: https://makerworld.com/en/search/models?keyword=cake+stand"
        )
        self.query = QLineEdit()
        self.query.setPlaceholderText("مثال: cake stand — برای Automatic/Search")
        self.source_hint = QLabel("")
        self.source_hint.setObjectName("Muted")
        self.source_hint.setWordWrap(True)

        self.download_images = QCheckBox("ذخیره تصاویر عمومی باکیفیت")
        self.download_images.setChecked(True)
        self.download_files = QCheckBox("دانلود فایل مستقیم عمومی مدل")
        self.download_files.setChecked(False)
        self.same_domain = QCheckBox("دانلود/خزش فایل فقط در همان دامنه")
        self.same_domain.setChecked(True)

        self.saved_html_path = QLineEdit()
        self.saved_html_path.setPlaceholderText(
            "برای روش Saved HTML فایل .html/.htm را انتخاب کن"
        )
        self.saved_html_browse = QPushButton("انتخاب HTML…")
        self.saved_html_browse.clicked.connect(self._browse_saved_html)

        self.domain_policy = QLabel(
            "خزش عمومی و robots-aware است؛ دورزدن Login/CAPTCHA/"
            "محدودیت دسترسی انجام نمی‌شود."
        )
        self.domain_policy.setObjectName("Muted")
        self.domain_policy.setWordWrap(True)

        self.requested = QSpinBox()
        self.requested.setRange(1, 500)
        self.requested.setValue(100)
        self.image_limit = QSpinBox()
        self.image_limit.setRange(1, HARD_MAX_IMAGE_LIMIT)
        self.image_limit.setValue(5)
        for spin in (self.requested, self.image_limit):
            spin.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.setMinimumWidth(112)
            spin.setMaximumWidth(150)
            spin.setStyleSheet(
                "QSpinBox { padding-left: 8px; padding-right: 28px; }"
            )
        self.retry_failed = QCheckBox("تلاش مجدد برای موارد Failed")

        self.start_btn = QPushButton("شروع دریافت")
        self.start_btn.setProperty("primary", True)
        self.start_btn.setToolTip(
            "Search/Listing فعلی را اجرا می‌کند؛ Preview محصولات ابتدا ظاهر می‌شود "
            "و سپس دریافت صفحه و عکس هر Product با پیشرفت جداگانه ادامه پیدا می‌کند."
        )
        self.stop_btn = QPushButton("توقف امن")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setToolTip("در مرز امن بعدی Crawl را متوقف می‌کند.")
        self.reset_failed_btn = QPushButton("بازگردانی Failed")
        self.reset_failed_btn.setToolTip("موارد Failed را برای تلاش مجدد به صف برمی‌گرداند.")
        self.queue_btn = QPushButton("موجودی Crawl")
        self.queue_btn.setToolTip("موجودی دائمی همه رکوردهای Crawl را باز می‌کند.")
        self.default_url_btn = QPushButton("لینک پیش‌فرض")
        self.default_url_btn.setToolTip(
            "Search/Listing پیش‌فرض Source انتخاب‌شده را در فیلد لینک می‌گذارد."
        )
        self.direct_btn = QPushButton("دریافت Product")
        self.direct_btn.setToolTip(
            "لینک فعلی را به‌عنوان یک صفحه Product مستقیم دریافت می‌کند."
        )
        self.login_profile_btn = QPushButton("Chrome پروفایل")
        self.login_profile_btn.setToolTip(
            "Chrome با پروفایل پایدار را برای ورود دستی مجاز باز می‌کند."
        )
        self.debug_chrome_btn = QPushButton("Chrome 9222")
        self.debug_chrome_btn.setToolTip(
            "Chrome متصل روی پورت 9222 را برای روش موجود باز می‌کند."
        )
        self.harvest_btn = QPushButton("🔎 کشف همه Sourceها")
        self.harvest_btn.setProperty("success", True)
        self.harvest_btn.setToolTip(
            "از Sourceهای فعال، محصولات جدید را به‌صورت محدود و robots-aware کشف می‌کند."
        )
        self.source_refresh_btn = QPushButton("♻ بروزرسانی Source")
        self.source_refresh_btn.setToolTip(
            "محصولات موجود Source انتخاب‌شده را بدون پاک کردن تصمیم‌های اپراتور دوباره می‌خواند."
        )
        self.refresh_btn = QPushButton("بروزرسانی")
        self.refresh_btn.setToolTip(
            "وضعیت صف، Run و نمایش فعلی را دوباره می‌خواند."
        )

        grid.addWidget(QLabel("سایت مادر / Source"), 0, 0)
        grid.addWidget(self.source, 0, 1)
        grid.addWidget(QLabel("نوع دریافت"), 0, 2)
        grid.addWidget(self.mode, 0, 3)
        grid.addWidget(QLabel("روش کشف"), 1, 0)
        grid.addWidget(self.strategy, 1, 1)
        grid.addWidget(QLabel("روش دریافت Product"), 1, 2)
        grid.addWidget(self.collection_method, 1, 3)
        grid.addWidget(QLabel("لینک گروه/محصول"), 2, 0)
        grid.addWidget(self.url, 2, 1, 1, 3)
        grid.addWidget(QLabel("عبارت جستجو"), 3, 0)
        grid.addWidget(self.query, 3, 1, 1, 3)
        grid.addWidget(QLabel("تعداد Product"), 4, 0)
        grid.addWidget(self.requested, 4, 1)
        grid.addWidget(QLabel("عکس باکیفیت برای هر Product"), 4, 2)
        grid.addWidget(self.image_limit, 4, 3)
        grid.addWidget(self.retry_failed, 5, 0)
        grid.addWidget(self.download_images, 5, 1)
        grid.addWidget(self.download_files, 5, 2)
        grid.addWidget(self.same_domain, 5, 3)
        grid.addWidget(QLabel("Saved HTML"), 6, 0)
        grid.addWidget(self.saved_html_path, 6, 1, 1, 2)
        grid.addWidget(self.saved_html_browse, 6, 3)
        grid.addWidget(self.source_hint, 7, 0, 1, 4)
        grid.addWidget(self.domain_policy, 8, 0, 1, 4)

        primary_actions = QHBoxLayout()
        for button in (
            self.start_btn,
            self.stop_btn,
            self.direct_btn,
        ):
            primary_actions.addWidget(button)
        primary_actions.addStretch(1)
        grid.addLayout(primary_actions, 9, 0, 1, 4)

        secondary_actions = QHBoxLayout()
        for button in (
            self.default_url_btn,
            self.queue_btn,
            self.refresh_btn,
        ):
            secondary_actions.addWidget(button)
        secondary_actions.addStretch(1)
        grid.addLayout(secondary_actions, 10, 0, 1, 4)

        receive_layout.addWidget(controls)

        tools_card = QFrame()
        tools_card.setObjectName("Card")
        tools_layout = QHBoxLayout(tools_card)
        tools_layout.addWidget(QLabel("ابزارهای Source / مرورگر"))
        for button in (
            self.login_profile_btn,
            self.debug_chrome_btn,
            self.harvest_btn,
            self.source_refresh_btn,
            self.reset_failed_btn,
        ):
            tools_layout.addWidget(button)
        tools_layout.addStretch(1)
        receive_layout.addWidget(tools_card)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status = QLabel("آماده")
        self.status.setObjectName("Muted")
        receive_layout.addWidget(self.progress)
        receive_layout.addWidget(self.status)

        live_card = QFrame()
        live_card.setObjectName("Card")
        live_layout = QVBoxLayout(live_card)
        live_header = QHBoxLayout()
        live_header.addWidget(QLabel("محصولات همین جستجو — Preview → دریافت کامل"))
        self.live_discovery_label = QLabel("هنوز Run شروع نشده است.")
        self.live_discovery_label.setObjectName("Muted")
        live_header.addStretch(1)
        live_header.addWidget(self.live_discovery_label)
        live_layout.addLayout(live_header)

        live_actions = QHBoxLayout()
        self.live_select_all_btn = QPushButton("انتخاب همه")
        self.live_clear_selection_btn = QPushButton("لغو انتخاب")
        self.live_add_btn = QPushButton("افزودن انتخابی")
        self.live_add_btn.setProperty("primary", True)
        self.live_add_btn.setToolTip(
            "همه Productهای انتخاب‌شده همین جستجو را دریافت/تطبیق می‌دهد "
            "و بعد صفحه محصولات را باز می‌کند."
        )
        self.live_reject_btn = QPushButton("حذف انتخابی")
        self.live_reject_btn.setToolTip(
            "کاندیداهای انتخاب‌شده همین جستجو را rejected می‌کند "
            "تا دوباره خودکار اضافه نشوند."
        )
        self.live_selected_label = QLabel("0 انتخاب‌شده")
        self.live_selected_label.setObjectName("Muted")
        live_actions.addWidget(self.live_select_all_btn)
        live_actions.addWidget(self.live_clear_selection_btn)
        live_actions.addWidget(self.live_add_btn)
        live_actions.addWidget(self.live_reject_btn)
        live_actions.addStretch(1)
        live_actions.addWidget(self.live_selected_label)
        live_layout.addLayout(live_actions)

        self.live_results = QListWidget()
        self.live_results.setViewMode(QListWidget.ViewMode.IconMode)
        self.live_results.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.live_results.setMovement(QListWidget.Movement.Static)
        self.live_results.setWrapping(True)
        self.live_results.setWordWrap(True)
        self.live_results.setIconSize(QSize(170, 118))
        self.live_results.setGridSize(QSize(235, 235))
        self.live_results.setSpacing(8)
        self.live_results.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self.live_results.setMinimumHeight(330)

        self.live_detail = QFrame()
        self.live_detail.setObjectName("Card")
        live_detail_layout = QVBoxLayout(self.live_detail)
        self.live_detail_title = QLabel("یک محصول را برای بازبینی انتخاب کن")
        self.live_detail_title.setStyleSheet(
            "font-size: 15px; font-weight: 700;"
        )
        self.live_detail_title.setWordWrap(True)
        self.live_detail_meta = QLabel(
            "Preview و سپس عکس‌های واقعی دریافت‌شده همین Product اینجا دیده می‌شوند."
        )
        self.live_detail_meta.setObjectName("Muted")
        self.live_detail_meta.setWordWrap(True)
        live_detail_layout.addWidget(self.live_detail_title)
        live_detail_layout.addWidget(self.live_detail_meta)

        self.live_detail_images = QListWidget()
        self.live_detail_images.setViewMode(QListWidget.ViewMode.IconMode)
        self.live_detail_images.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.live_detail_images.setMovement(QListWidget.Movement.Static)
        self.live_detail_images.setWrapping(True)
        self.live_detail_images.setWordWrap(True)
        self.live_detail_images.setIconSize(QSize(108, 78))
        self.live_detail_images.setGridSize(QSize(132, 122))
        self.live_detail_images.setSpacing(6)
        self.live_detail_images.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.live_detail_images.setMinimumHeight(245)
        live_detail_layout.addWidget(self.live_detail_images, 1)

        self.live_detail_url = QLineEdit()
        self.live_detail_url.setReadOnly(True)
        self.live_detail_url.setPlaceholderText("لینک صفحه Product")
        live_detail_layout.addWidget(self.live_detail_url)

        live_detail_actions = QHBoxLayout()
        self.live_detail_open_btn = QPushButton("صفحه منبع")
        self.live_detail_open_btn.clicked.connect(
            self._open_selected_live_source
        )
        self.live_detail_product_btn = QPushButton("نمایش در محصولات")
        self.live_detail_product_btn.setProperty("primary", True)
        self.live_detail_product_btn.clicked.connect(
            self._go_selected_live_product
        )
        self.live_detail_open_btn.setEnabled(False)
        self.live_detail_product_btn.setEnabled(False)
        live_detail_actions.addWidget(self.live_detail_open_btn)
        live_detail_actions.addWidget(self.live_detail_product_btn)
        live_detail_actions.addStretch(1)
        live_detail_layout.addLayout(live_detail_actions)

        live_splitter = QSplitter(Qt.Orientation.Horizontal)
        live_splitter.setChildrenCollapsible(False)
        live_splitter.addWidget(self.live_results)
        live_splitter.addWidget(self.live_detail)
        live_splitter.setStretchFactor(0, 3)
        live_splitter.setStretchFactor(1, 2)
        live_layout.addWidget(live_splitter, 1)
        receive_layout.addWidget(live_card, 1)
        receive_layout.addStretch(1)

        # --------------------------------------------------------------
        # Tab 3: run history / diagnostics.
        # --------------------------------------------------------------
        report_page = QWidget()
        report_layout = QVBoxLayout(report_page)
        report_header = QHBoxLayout()
        report_header.addWidget(QLabel("وضعیت Source، صف و Runهای اخیر"))
        report_refresh = QPushButton("بروزرسانی گزارش")
        report_refresh.clicked.connect(self.refresh)
        report_logs = QPushButton("پوشه لاگ Crawl")
        report_logs.setToolTip("لاگ روش‌های دریافت، کیفیت داده، تعداد عکس و علت Failover را باز می‌کند.")
        report_logs.clicked.connect(self._open_acquisition_logs)
        report_header.addStretch(1)
        report_header.addWidget(report_logs)
        report_header.addWidget(report_refresh)
        report_layout.addLayout(report_header)
        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        report_layout.addWidget(self.summary, 1)

        self.workspace_tabs.addTab(inventory_page, "موجودی محصولات")
        self.workspace_tabs.addTab(receive_page, "دریافت محصولات از لینک جستجو")
        self.workspace_tabs.addTab(report_page, "گزارش و History")
        self.workspace_tabs.setCurrentIndex(0)

        self._queue_rows_by_id: dict[int, dict] = {}
        self._queue_page_size = 100
        self._queue_offset = 0
        self._queue_total = 0
        self._live_refresh_timer = QTimer(self)
        self._live_refresh_timer.setSingleShot(True)
        self._live_refresh_timer.setInterval(160)
        self._live_refresh_timer.timeout.connect(self._refresh_live_discovery)

        self.queue_gallery.verticalScrollBar().valueChanged.connect(
            lambda _value: self._fetch_queue_if_needed()
        )
        self.queue_table.verticalScrollBar().valueChanged.connect(
            lambda _value: self._fetch_queue_if_needed()
        )
        self.queue_view_mode.currentIndexChanged.connect(
            self._queue_view_changed
        )
        self.queue_gallery.itemSelectionChanged.connect(
            self._update_queue_selection_label
        )
        self.queue_table.itemSelectionChanged.connect(
            self._update_queue_selection_label
        )
        self.queue_select_all_btn.clicked.connect(self._select_all_queue)
        self.queue_select_incomplete_btn.clicked.connect(self._select_incomplete_queue)
        self.queue_clear_selection_btn.clicked.connect(self._clear_queue_selection)

        self.mode.currentIndexChanged.connect(self._mode_changed)
        self.url.editingFinished.connect(self._sync_source_from_url)
        self.collection_method.currentIndexChanged.connect(self._method_changed)
        self.source.currentIndexChanged.connect(self._source_changed)
        self.start_btn.clicked.connect(self._start)
        self.stop_btn.clicked.connect(self._stop)
        self.reset_failed_btn.clicked.connect(self._reset_failed)
        self.queue_btn.clicked.connect(self._show_queue_inventory)
        self.default_url_btn.clicked.connect(self._fill_default_url)
        self.direct_btn.clicked.connect(self._direct_from_url)
        self.login_profile_btn.clicked.connect(self._setup_login_profile)
        self.debug_chrome_btn.clicked.connect(self._launch_debug_chrome)
        self.harvest_btn.clicked.connect(self._portfolio_harvest)
        self.source_refresh_btn.clicked.connect(self._refresh_source_products)
        self.refresh_btn.clicked.connect(self.refresh)
        self.queue_filter.currentIndexChanged.connect(
            lambda _index: self._populate_queue(reset=True)
        )
        self.queue_open_btn.clicked.connect(self._open_selected_queue_source)
        self.queue_collect_btn.clicked.connect(self._collect_selected_queue)
        self.queue_collect_ai_btn.clicked.connect(
            lambda: self._collect_selected_queue(run_ai=True)
        )
        self.queue_recover_btn.clicked.connect(self._recover_selected_queue)
        self.queue_gallery.itemDoubleClicked.connect(
            lambda _item: self._open_selected_queue_source()
        )
        self.queue_table.itemDoubleClicked.connect(
            lambda _item: self._open_selected_queue_source()
        )
        self.queue_reject_btn.clicked.connect(self._reject_selected_queue)
        self.queue_restore_btn.clicked.connect(self._restore_selected_queue)
        self.live_results.itemSelectionChanged.connect(
            self._update_live_selection_label
        )
        self.live_results.itemDoubleClicked.connect(
            lambda _item: self._open_selected_live_source()
        )
        self.live_select_all_btn.clicked.connect(self.live_results.selectAll)
        self.live_clear_selection_btn.clicked.connect(self.live_results.clearSelection)
        self.live_add_btn.clicked.connect(self._collect_selected_live)
        self.live_reject_btn.clicked.connect(self._reject_selected_live)

        self._reload_sources()
        self._mode_changed()
        self._method_changed()
        self._queue_view_changed()
        self.refresh()

    def _reload_sources(self) -> None:
        current = str(self.source.currentData() or "")
        self.source.clear()
        for row in self.kernel.acquisition.sources():
            self.source.addItem(
                str(row.get("name") or row.get("code") or ""),
                str(row.get("code") or ""),
            )
        index = self.source.findData(current)
        if index >= 0:
            self.source.setCurrentIndex(index)

    def _source_changed(self) -> None:
        source_code = str(
            self.source.currentData() or ""
        )
        details = self.kernel.acquisition.source_details(
            source_code
        )
        default = self.kernel.acquisition.default_listing_url(
            source_code,
            query=self.query.text().strip(),
        )
        self.source_hint.setText(
            f"Source: {details.get('name') or source_code or '—'} • "
            f"Listing پیش‌فرض: {default or 'ثبت نشده'}"
        )

    def _sync_source_from_url(self) -> None:
        detected = self.kernel.acquisition.detect_source_for_url(
            self.url.text().strip()
        )
        if not detected:
            return
        index = self.source.findData(detected)
        if index >= 0 and index != self.source.currentIndex():
            self.source.setCurrentIndex(index)
            self.source_hint.setText(
                f"✅ Source از روی لینک تشخیص داده شد: {self.source.currentText()}"
            )

    def _refresh_live_discovery(self) -> None:
        if not hasattr(self, "live_results"):
            return
        source_code = str(
            self._active_source_code
            or self.source.currentData()
            or ""
        )
        listing_url = str(self._active_listing_url or "")
        if not source_code or not listing_url:
            if self._worker is None:
                self.live_discovery_label.setText(
                    "هر جستجوی جدید این قسمت را پاک می‌کند و فقط محصولات همان لینک را نشان می‌دهد."
                )
            return

        rows = self.kernel.acquisition.current_review_items(
            source_code,
            listing_url,
            since=self._active_run_started_at,
            limit=max(20, int(self.requested.value())),
        )
        selected_external = {
            str(item.data(Qt.ItemDataRole.UserRole + 2) or "")
            for item in self.live_results.selectedItems()
        }

        self.live_results.setUpdatesEnabled(False)
        self.live_results.clear()
        imported = failed = waiting = 0
        try:
            for raw in rows:
                row = dict(raw)
                external_id = str(row.get("external_id") or "")
                queue_id = int(row.get("queue_id") or 0)
                product_id = int(row.get("product_id") or 0)
                status = str(
                    row.get("status")
                    or row.get("candidate_status")
                    or "review"
                )
                if product_id:
                    imported += 1
                elif status in {"failed", "rejected", "blocked"}:
                    failed += 1
                else:
                    waiting += 1

                title = (
                    row.get("product_title_fa")
                    or row.get("product_source_title")
                    or row.get("candidate_title")
                    or external_id
                    or "کاندیدا"
                )
                icon = self._queue_icon(row)
                image_count = self._queue_image_count(row)
                preview_path = self.kernel.acquisition.candidate_preview_path(
                    source_code,
                    external_id,
                )
                if image_count > 0:
                    image_text = f"{image_count} عکس دارد"
                elif preview_path:
                    image_text = "Preview: 1 عکس • دریافت کامل در صف"
                else:
                    image_text = "Preview بدون تصویر • دریافت کامل در صف"

                progress_text = self._live_product_progress.get(
                    external_id,
                    "",
                )
                lines = [
                    str(title),
                    f"{source_code} • {status}",
                    image_text,
                ]
                if progress_text:
                    lines.append(progress_text)
                item = QListWidgetItem("\n".join(lines))
                item.setIcon(icon)
                item.setData(Qt.ItemDataRole.UserRole, queue_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, product_id)
                item.setData(Qt.ItemDataRole.UserRole + 2, external_id)
                item.setData(
                    Qt.ItemDataRole.UserRole + 3,
                    str(row.get("url") or ""),
                )
                item.setToolTip(
                    f"External ID: {external_id}\n"
                    f"Queue: {queue_id or '—'}\n"
                    f"Product: {product_id or '—'}\n"
                    f"Status: {status}\n"
                    f"{row.get('url') or ''}"
                )
                self.live_results.addItem(item)
                if external_id in selected_external:
                    item.setSelected(True)
        finally:
            self.live_results.setUpdatesEnabled(True)

        self.live_discovery_label.setText(
            f"همین جستجو: {len(rows)} • دریافت‌شده: {imported} • "
            f"در انتظار: {waiting} • خطا/رد: {failed}"
        )
        self._update_live_selection_label()

    def _schedule_live_refresh(self) -> None:
        if hasattr(self, "_live_refresh_timer"):
            self._live_refresh_timer.start()

    def _fill_default_url(self) -> None:
        source_code = str(
            self.source.currentData() or ""
        )
        value = self.kernel.acquisition.default_listing_url(
            source_code,
            query=self.query.text().strip(),
        )
        if not value:
            QMessageBox.warning(
                self,
                "Source",
                "Listing پیش‌فرض برای این Source پیدا نشد.",
            )
            return
        self.url.setText(value)

    def _browse_saved_html(self) -> None:
        path, _selected = QFileDialog.getOpenFileName(
            self,
            "فایل HTML ذخیره‌شده",
            "",
            "HTML (*.html *.htm);;All files (*.*)",
        )
        if path:
            self.saved_html_path.setText(path)

    def _direct_from_url(self) -> None:
        index = self.mode.findData("single")
        if index >= 0:
            self.mode.setCurrentIndex(index)
        rich_index = self.collection_method.findData("rich")
        if rich_index >= 0:
            self.collection_method.setCurrentIndex(rich_index)
        self._start()

    def _method_changed(self) -> None:
        method = str(self.collection_method.currentData() or "rich")
        saved = method == "saved_html"
        self.saved_html_path.setEnabled(saved)
        self.saved_html_browse.setEnabled(saved)
        if saved:
            single_index = self.mode.findData("single")
            if single_index >= 0:
                self.mode.setCurrentIndex(single_index)
        if method != "rich":
            classic_index = self.strategy.findData("classic")
            if classic_index >= 0:
                self.strategy.setCurrentIndex(classic_index)
        self._mode_changed()

    def _mode_changed(self) -> None:
        mode = str(
            self.mode.currentData() or "automatic"
        )
        method = str(
            self.collection_method.currentData() or "rich"
        ) if hasattr(self, "collection_method") else "rich"
        batch = mode != "single"
        self.requested.setEnabled(batch)
        self.retry_failed.setEnabled(batch)
        self.strategy.setEnabled(batch and method == "rich")
        self.query.setEnabled(
            mode in {"automatic", "search"}
        )
        self.default_url_btn.setEnabled(batch)
        self.url.setPlaceholderText(
            (
                "لینک اختیاری؛ اگر خالی باشد Automatic/Search "
                "از Listing پیش‌فرض Source استفاده می‌کند"
            )
            if batch
            else "لینک مستقیم صفحه Product"
        )
        self._source_changed()

    def _start(self) -> None:
        if self._worker is not None:
            QMessageBox.information(
                self,
                "دریافت اطلاعات",
                "یک عملیات دریافت در حال اجرا است.",
            )
            return

        self._sync_source_from_url()
        source_code = str(
            self.source.currentData() or ""
        ).strip()
        url = self.url.text().strip()
        mode = str(
            self.mode.currentData() or "automatic"
        )
        query = self.query.text().strip()
        if not source_code:
            QMessageBox.warning(
                self,
                "دریافت اطلاعات",
                "یک Source فعال انتخاب کن.",
            )
            return
        if mode == "single":
            resolved_url = url
        else:
            try:
                resolved_url = (
                    self.kernel.acquisition.resolve_listing_url(
                        source_code,
                        operator_mode=mode,
                        explicit_url=url,
                        query=query,
                    )
                )
            except Exception as exc:
                QMessageBox.warning(
                    self,
                    "دریافت اطلاعات",
                    str(exc),
                )
                return
            if resolved_url != url:
                self.url.setText(resolved_url)

        if not resolved_url.startswith(
            ("http://", "https://")
        ):
            QMessageBox.warning(
                self,
                "دریافت اطلاعات",
                "لینک معتبر http/https وارد کن.",
            )
            return

        if mode != "single":
            self._active_listing_url = str(resolved_url)
            self._active_source_code = source_code
            self._active_run_started_at = utc_now()
            self._live_product_progress = {}
            self.live_results.clear()
            self.live_discovery_label.setText(
                "جستجوی جدید شروع شد؛ Preview محصولات همین لینک در حال ساخته‌شدن است…"
            )
            self._update_live_selection_label()
        else:
            self._active_listing_url = ""
            self._active_source_code = source_code
            self._active_run_started_at = utc_now()
            self._live_product_progress = {}
            self.live_results.clear()

        requested = self.requested.value()
        image_limit = self.image_limit.value()
        include_failed = self.retry_failed.isChecked()
        collection_method = str(
            self.collection_method.currentData() or "rich"
        )
        strategy = (
            str(self.strategy.currentData() or "hybrid")
            if collection_method == "rich"
            else "classic"
        )
        saved_html_path = self.saved_html_path.text().strip()
        if collection_method == "saved_html" and not saved_html_path:
            QMessageBox.warning(
                self,
                "Saved HTML",
                "فایل HTML ذخیره‌شده را انتخاب کن.",
            )
            return

        def job(progress):
            if mode == "single":
                return self.kernel.acquisition.run_single(
                    source_code=source_code,
                    product_url=resolved_url,
                    image_limit=image_limit,
                    collection_method=collection_method,
                    saved_html_path=saved_html_path,
                    download_images=self.download_images.isChecked(),
                    download_files=self.download_files.isChecked(),
                    same_domain_only=self.same_domain.isChecked(),
                    progress=progress,
                )
            return self.kernel.acquisition.run_batch(
                source_code=source_code,
                listing_url=resolved_url,
                requested=requested,
                image_limit=image_limit,
                include_failed=include_failed,
                strategy=strategy,
                operator_mode=mode,
                collection_method=collection_method,
                download_images=self.download_images.isChecked(),
                download_files=self.download_files.isChecked(),
                same_domain_only=self.same_domain.isChecked(),
                progress=progress,
            )

        worker = Worker(job)
        self._worker = worker
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText("شروع دریافت…")

        worker.signals.progress.connect(self._progress)
        worker.signals.result.connect(self._done)
        worker.signals.error.connect(self._error)
        worker.signals.finished.connect(self._finished)
        self.pool.start(worker)

    def _start_auxiliary_job(self, label: str, fn) -> None:
        if self._worker is not None:
            QMessageBox.information(
                self,
                label,
                "یک عملیات دریافت در حال اجرا است.",
            )
            return
        worker = Worker(fn)
        self._worker = worker
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(f"{label}…")
        worker.signals.progress.connect(self._progress)
        worker.signals.result.connect(self._done)
        worker.signals.error.connect(self._error)
        worker.signals.finished.connect(self._finished)
        self.pool.start(worker)

    def _setup_login_profile(self) -> None:
        source_code = str(self.source.currentData() or "").strip()
        seed = self.url.text().strip()
        if not source_code:
            QMessageBox.warning(self, "Chrome پروفایل", "یک Source انتخاب کن.")
            return

        def job(_progress):
            return self.kernel.acquisition.setup_login_profile(
                source_code=source_code,
                seed_url=seed,
            )

        self._start_auxiliary_job("Chrome پروفایل / ورود دستی", job)

    def _launch_debug_chrome(self) -> None:
        try:
            result = self.kernel.acquisition.launch_debug_chrome(
                seed_url=self.url.text().strip(),
            )
        except Exception as exc:
            show_diagnostic_error(
                self,
                "Chrome متصل 9222",
                f"{type(exc).__name__}: {exc}",
                context={"operation": "launch-debug-chrome"},
            )
            return
        self.status.setText(
            f"Chrome متصل باز شد — PID={result.get('pid')} • "
            f"CDP={result.get('cdp_url')}"
        )

    def _portfolio_harvest(self) -> None:
        requested = self.requested.value()
        image_limit = self.image_limit.value()

        def job(progress):
            return self.kernel.acquisition.portfolio_harvest(
                requested_per_source=requested,
                image_limit=image_limit,
                download_images=self.download_images.isChecked(),
                download_files=self.download_files.isChecked(),
                same_domain_only=self.same_domain.isChecked(),
                progress=progress,
            )

        self._start_auxiliary_job("کشف جدیدها از همه Sourceها", job)

    def _refresh_source_products(self) -> None:
        source_code = str(self.source.currentData() or "").strip()
        if not source_code:
            QMessageBox.warning(
                self,
                "بروزرسانی Source",
                "یک Source فعال انتخاب کن.",
            )
            return
        limit = self.requested.value()
        image_limit = self.image_limit.value()
        answer = QMessageBox.question(
            self,
            "بروزرسانی محصولات Source",
            (
                f"حداکثر {limit} محصول از {source_code} دوباره از منبع خوانده شوند؟\n"
                "تصمیم‌های ویرایشی، عنوان فارسی، قیمت و وضعیت‌های اپراتور حفظ می‌شوند."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        def job(progress):
            result = self.kernel.acquisition.refresh_source_products(
                source_code=source_code,
                limit=limit,
                image_limit=image_limit,
                download_images=self.download_images.isChecked(),
                progress=progress,
            )
            return {"operation": "source_refresh", **dict(result or {})}

        self._start_auxiliary_job("بروزرسانی محصولات Source", job)

    def _progress(self, value: int, message: str) -> None:
        self.progress.setValue(int(value))
        text = str(message or "")
        self.status.setText(text)

        if "ID=" in text:
            external_id = text.split("ID=", 1)[1].split("•", 1)[0].strip()
            if external_id:
                segments = [
                    part.strip()
                    for part in text.split("•")
                    if part.strip()
                ]
                compact = ""
                for position, part in enumerate(segments):
                    if part.startswith("ID="):
                        compact = " • ".join(
                            segments[position + 1 :]
                        ).strip()
                        break
                self._live_product_progress[external_id] = compact or text

        if (
            int(value) <= 25
            or "Preview" in text
            or "پیش‌نمایش" in text
            or "کشف" in text
            or "عکس " in text
            or "ذخیره شد" in text
        ):
            self._schedule_live_refresh()

        if (
            "کشف تمام شد" in text
            or "پیش‌نمایش:" in text
            or int(value) == 100
        ):
            self._populate_queue(reset=True)

    def _stop(self) -> None:
        self.kernel.acquisition.request_stop()
        self.stop_btn.setEnabled(False)
        self.status.setText(
            "درخواست توقف ثبت شد؛ عملیات جاری به مرز امن بعدی می‌رسد."
        )

    def _done(self, result) -> None:
        data = dict(result or {})
        self.progress.setValue(100)
        operation = str(data.get("operation") or "")
        if operation == "portfolio_harvest":
            self.status.setText(
                "✅ کشف چندمنبعی تمام شد — "
                f"Collected={data.get('collected', 0)} • "
                f"Failed={data.get('failed', 0)} • "
                f"New={data.get('discovered', 0)}"
            )
        elif operation == "source_refresh":
            self.status.setText(
                "✅ بروزرسانی Source تمام شد — "
                f"Changed={data.get('changed', 0)} • "
                f"Unchanged={data.get('unchanged', 0)} • "
                f"Failed={data.get('failed', 0)}"
            )
        elif operation == "login_profile":
            self.status.setText(
                "✅ Chrome پروفایل بسته شد و نشست مرورگر حفظ شد."
            )
        elif operation == "queue_recover":
            self.status.setText(
                "✅ بازیابی گروهی تمام شد — "
                f"محلیِ کافی={data.get('local_reused', 0)} • "
                f"بازیابی‌شده={data.get('recovered', 0)} • "
                f"ساخته‌شده={data.get('created', 0)} • "
                f"خطا={data.get('failed', 0)} • "
                f"دست‌نخورده={data.get('unattempted', 0)} • "
                f"روش={data.get('preferred_method') or '—'}"
            )
        elif operation in {"queue_collect", "queue_collect_ai"}:
            ai = dict(data.get("ai") or {})
            ai_completed = (
                ai.get("completed", 0)
                if operation == "queue_collect_ai"
                else 0
            )
            ai_failed = (
                ai.get("failed", 0)
                if operation == "queue_collect_ai"
                else 0
            )
            self.status.setText(
                "✅ انتقال انتخاب‌شده‌ها به محصولات تمام شد — "
                f"جدید={data.get('collected', 0)} • "
                f"قبلاً موجود={data.get('already_collected_count', 0)} • "
                f"AI={ai_completed} • "
                f"خطا={data.get('failed', 0) + ai_failed}"
            )
            if data.get("product_ids") and callable(self.navigate):
                QTimer.singleShot(
                    0,
                    lambda: self.navigate("products"),
                )
        elif data.get("already_collected"):
            self.status.setText(
                f"این Product قبلاً دریافت شده — ID {data.get('product_id') or '—'}"
            )
        else:
            self.status.setText(
                "✅ پایان دریافت — "
                f"Collected={data.get('collected', 1)} • "
                f"Failed={data.get('failed', 0)} • "
                f"New={data.get('discovered', 0)} • "
                f"Files={data.get('files_saved', 0)}"
            )
        self.refresh()
        self._refresh_live_discovery()

    def _error(self, detail: str) -> None:
        self.status.setText("❌ دریافت ناموفق")
        show_diagnostic_error(
            self,
            "خطای دریافت / Crawl",
            detail,
            context={
                "source": str(
                    self.source.currentData() or ""
                ),
                "mode": str(
                    self.mode.currentData() or ""
                ),
                "strategy": str(
                    self.strategy.currentData() or ""
                ),
                "collection_method": str(
                    self.collection_method.currentData() or ""
                ),
                "url": self.url.text().strip(),
            },
        )
        self.refresh()

    def _finished(self) -> None:
        self._worker = None
        self.start_btn.setEnabled(True)
        if hasattr(self, "queue_collect_btn"):
            self.queue_collect_btn.setEnabled(True)
        if hasattr(self, "queue_collect_ai_btn"):
            self.queue_collect_ai_btn.setEnabled(True)
        if hasattr(self, "queue_recover_btn"):
            self.queue_recover_btn.setEnabled(True)
        if hasattr(self, "queue_select_incomplete_btn"):
            self.queue_select_incomplete_btn.setEnabled(True)
        if hasattr(self, "queue_open_btn"):
            self.queue_open_btn.setEnabled(True)
        if hasattr(self, "live_add_btn"):
            self.live_add_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _reset_failed(self) -> None:
        source_code = str(self.source.currentData() or "")
        try:
            count = self.kernel.acquisition.reset_failed(source_code)
        except Exception as exc:
            QMessageBox.warning(
                self,
                "صف دریافت",
                str(exc),
            )
            return
        self.status.setText(f"{count} مورد Failed دوباره وارد صف شد.")
        self.refresh()

    def _queue_product_row(self, row: dict) -> dict:
        return {
            "id": row.get("product_id"),
            "source_code": row.get("source_code") or "",
            "external_id": row.get("external_id") or "",
            "title_fa": row.get("product_title_fa") or "",
            "source_title": row.get("product_source_title") or "",
            "short_description_fa": row.get("product_short_description_fa") or "",
            "description_fa": row.get("product_description_fa") or "",
            "source_short_description": (
                row.get("product_source_short_description") or ""
            ),
            "source_description": row.get("product_source_description") or "",
            "primary_image_url": row.get("product_primary_image_url") or "",
            "local_dir": row.get("product_local_dir") or "",
            "selected_images_json": (
                row.get("product_selected_images_json") or "[]"
            ),
            "images_json": row.get("product_images_json") or "[]",
            "image_metadata_json": (
                row.get("product_image_metadata_json") or "[]"
            ),
            "source_specs_json": row.get("product_source_specs_json") or "{}",
            "tags_json": row.get("product_tags_json") or "[]",
            "dimensions": row.get("product_dimensions") or "",
            "estimated_weight_grams": row.get("product_estimated_weight_grams") or 0,
            "estimated_print_minutes": row.get("product_estimated_print_minutes") or 0,
        }

    def _queue_description(self, row: dict) -> str:
        product = self._queue_product_row(row)
        value = (
            product.get("short_description_fa")
            or product.get("source_short_description")
            or product.get("description_fa")
            or product.get("source_description")
            or ""
        )
        return " ".join(str(value).split())

    def _queue_dimensions(self, row: dict) -> str:
        direct = str(row.get("product_dimensions") or "").strip()
        if direct:
            return direct
        try:
            specs = json.loads(str(row.get("product_source_specs_json") or "{}"))
        except Exception:
            specs = {}

        def find_dimensions(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if "dimension" in str(key or "").casefold() or str(key or "") == "ابعاد":
                        if isinstance(value, dict):
                            x = value.get("x")
                            y = value.get("y")
                            z = value.get("z")
                            if all(item not in (None, "") for item in (x, y, z)):
                                unit = str(value.get("unit") or value.get("units") or "").strip()
                                return f"{x} × {y} × {z} {unit}".strip()
                        text = str(value or "").strip()
                        if text:
                            return text
                    if isinstance(value, (dict, list)):
                        found = find_dimensions(value)
                        if found:
                            return found
            elif isinstance(node, list):
                for value in node:
                    found = find_dimensions(value)
                    if found:
                        return found
            return ""

        return str(find_dimensions(specs) or "")

    def _queue_technical_summary(self, row: dict) -> str:
        parts: list[str] = []
        weight = float(row.get("product_estimated_weight_grams") or 0)
        minutes = int(row.get("product_estimated_print_minutes") or 0)
        dimensions = self._queue_dimensions(row)
        if weight > 0:
            parts.append(f"⚖ {weight:g} g")
        if minutes > 0:
            hours, remainder = divmod(minutes, 60)
            parts.append(
                f"⏱ {hours}h {remainder}m" if hours else f"⏱ {remainder}m"
            )
        if dimensions:
            parts.append(f"📐 {dimensions}")
        try:
            tags = json.loads(str(row.get("product_tags_json") or "[]"))
        except Exception:
            tags = []
        if isinstance(tags, list) and tags:
            clean = [str(value).strip() for value in tags if str(value).strip()][:4]
            if clean:
                parts.append("🏷 " + "، ".join(clean))
        return " • ".join(parts)

    def _queue_local_identity_items(self, row: dict) -> list[str]:
        return self.kernel.images.identity_local_items(
            str(row.get("source_code") or ""),
            str(row.get("external_id") or ""),
            self._queue_product_row(row),
        )

    def _queue_image_count(self, row: dict) -> int:
        if row.get("product_id"):
            count = self.kernel.images.image_count(
                self._queue_product_row(row)
            )
            if count > 0:
                return count
        return len(self._queue_local_identity_items(row))

    def _queue_fallback_title_from_url(self, row: dict) -> str:
        url = str(
            row.get("url")
            or row.get("normalized_url")
            or ""
        ).strip()
        if not url:
            return ""
        try:
            path = QUrl(url).path().rstrip("/")
        except Exception:
            return ""
        slug = path.split("/")[-1] if path else ""
        external_id = str(row.get("external_id") or "").strip()
        if external_id and slug.startswith(external_id):
            slug = slug[len(external_id):].lstrip("-_")
        slug = slug.replace("-", " ").replace("_", " ")
        return " ".join(slug.split()).strip()

    def _queue_display_title(self, row: dict) -> str:
        value = (
            row.get("product_title_fa")
            or row.get("product_source_title")
            or row.get("candidate_title")
            or self._queue_fallback_title_from_url(row)
            or row.get("external_id")
            or "بدون عنوان دریافت‌شده"
        )
        if not row.get("product_id"):
            return f"{value} — کاندیدای کشف‌شده؛ هنوز دریافت نشده"
        return str(value)

    def _queue_is_incomplete(self, row: dict) -> bool:
        if not int(row.get("product_id") or 0):
            return True
        product = self._queue_product_row(row)
        has_title = bool(
            str(product.get("title_fa") or "").strip()
            or str(product.get("source_title") or "").strip()
        )
        has_description = bool(
            str(product.get("short_description_fa") or "").strip()
            or str(product.get("description_fa") or "").strip()
            or str(product.get("source_short_description") or "").strip()
            or str(product.get("source_description") or "").strip()
        )
        return (
            not has_title
            or not has_description
            or self._queue_image_count(row) <= 0
        )

    def _queue_icon(self, row: dict) -> QIcon:
        if row.get("product_id"):
            path = self.kernel.images.preferred_local_path(
                self._queue_product_row(row)
            )
            if path:
                return QIcon(path)
        identity_path = self.kernel.images.preferred_identity_local_path(
            str(row.get("source_code") or ""),
            str(row.get("external_id") or ""),
            self._queue_product_row(row),
        )
        if identity_path:
            return QIcon(identity_path)
        preview = self.kernel.acquisition.candidate_preview_path(
            str(row.get("source_code") or ""),
            str(row.get("external_id") or ""),
        )
        if preview:
            return QIcon(preview)
        return QIcon.fromTheme("image-x-generic")

    def _update_queue_selection_label(self) -> None:
        if hasattr(self, "queue_selected_label"):
            self.queue_selected_label.setText(
                f"{len(self._selected_queue_ids())} انتخاب‌شده"
            )

    def _select_all_queue(self) -> None:
        if self.queue_views.currentIndex() == 0:
            self.queue_gallery.selectAll()
        else:
            self.queue_table.selectAll()
        self._update_queue_selection_label()

    def _select_incomplete_queue(self) -> None:
        incomplete_ids = {
            int(queue_id)
            for queue_id, row in self._queue_rows_by_id.items()
            if int(queue_id) > 0 and self._queue_is_incomplete(dict(row))
        }
        if self.queue_views.currentIndex() == 0:
            self.queue_gallery.clearSelection()
            for index in range(self.queue_gallery.count()):
                item = self.queue_gallery.item(index)
                item.setSelected(
                    int(item.data(Qt.ItemDataRole.UserRole) or 0)
                    in incomplete_ids
                )
        else:
            self.queue_table.clearSelection()
            for row_index in range(self.queue_table.rowCount()):
                item = self.queue_table.item(row_index, 1)
                if item is None:
                    continue
                if int(item.data(Qt.ItemDataRole.UserRole) or 0) in incomplete_ids:
                    self.queue_table.selectRow(row_index)
        self._update_queue_selection_label()
        self.status.setText(
            f"{len(incomplete_ids)} رکورد ناقص از موارد لودشده انتخاب شد."
        )

    def _clear_queue_selection(self) -> None:
        if self.queue_views.currentIndex() == 0:
            self.queue_gallery.clearSelection()
        else:
            self.queue_table.clearSelection()
        self._update_queue_selection_label()

    def _update_live_selection_label(self) -> None:
        if hasattr(self, "live_selected_label"):
            self.live_selected_label.setText(
                f"{len(self.live_results.selectedItems())} انتخاب‌شده"
            )
        if hasattr(self, "live_detail_images"):
            self._refresh_live_detail()

    def _refresh_live_detail(self) -> None:
        self.live_detail_images.clear()
        selected = self._selected_live_records()
        if not selected:
            self.live_detail_title.setText(
                "یک محصول را برای بازبینی انتخاب کن"
            )
            self.live_detail_meta.setText(
                "Preview و سپس عکس‌های واقعی دریافت‌شده همین Product اینجا دیده می‌شوند."
            )
            self.live_detail_url.clear()
            self.live_detail_open_btn.setEnabled(False)
            self.live_detail_product_btn.setEnabled(False)
            return

        if len(selected) > 1:
            self.live_detail_title.setText(
                f"{len(selected)} محصول انتخاب شده"
            )
            self.live_detail_meta.setText(
                "برای مشاهده عکس‌های یک Product فقط همان مورد را انتخاب کن؛ "
                "افزودن/حذف گروهی برای همه انتخاب‌ها فعال است."
            )
            self.live_detail_url.clear()
            self.live_detail_open_btn.setEnabled(False)
            self.live_detail_product_btn.setEnabled(False)
            return

        record = selected[0]
        product_id = int(record.get("product_id") or 0)
        external_id = str(record.get("external_id") or "")
        source_code = str(
            self._active_source_code
            or self.source.currentData()
            or ""
        )
        url = str(record.get("url") or "").strip()
        self.live_detail_url.setText(url)
        self.live_detail_open_btn.setEnabled(
            url.startswith(("http://", "https://"))
        )

        if product_id > 0:
            row = self.db.product(product_id)
            data = dict(row) if row is not None else {}
            title = (
                data.get("title_fa")
                or data.get("source_title")
                or external_id
                or f"Product #{product_id}"
            )
            image_items = self.kernel.images.local_items(product_id)
            local_count = 0
            for image in image_items[:24]:
                slot = int(image.get("slot") or 0)
                path = str(image.get("path") or "")
                if path:
                    local_count += 1
                label = (
                    f"عکس {slot or self.live_detail_images.count() + 1}"
                )
                if image.get("primary"):
                    label += "\nاصلی"
                elif image.get("slider"):
                    label += "\nاسلایدر"
                item = QListWidgetItem(label)
                if path:
                    item.setIcon(QIcon(path))
                item.setToolTip(
                    f"{image.get('filename') or ''}\n"
                    f"{image.get('width') or 0}×{image.get('height') or 0}\n"
                    f"{image.get('url') or ''}"
                )
                self.live_detail_images.addItem(item)

            image_count = self.kernel.images.image_count(data)
            if self.live_detail_images.count() == 0:
                preferred = self.kernel.images.preferred_local_path(data)
                if preferred:
                    fallback_item = QListWidgetItem("تصویر محصول")
                    fallback_item.setIcon(QIcon(preferred))
                    self.live_detail_images.addItem(fallback_item)
                    local_count = max(local_count, 1)

            self.live_detail_title.setText(str(title))
            self.live_detail_meta.setText(
                f"{image_count} عکس دارد • {local_count} فایل محلی قابل نمایش • "
                f"Product #{product_id}"
            )
            self.live_detail_product_btn.setEnabled(
                callable(self.navigate)
            )
            return

        local_paths = self.kernel.images.identity_local_items(
            source_code,
            external_id,
        )
        if local_paths:
            for index, path in enumerate(local_paths[:24], 1):
                item = QListWidgetItem(f"عکس {index}")
                item.setIcon(QIcon(path))
                item.setToolTip(path)
                self.live_detail_images.addItem(item)
            self.live_detail_title.setText(
                external_id or "کاندیدای دارای فایل محلی"
            )
            self.live_detail_meta.setText(
                f"{len(local_paths)} عکس دارد • فایل‌های دانلودشده نسخه قبلی پیدا شد"
            )
            self.live_detail_product_btn.setEnabled(False)
            return

        preview = self.kernel.acquisition.candidate_preview_path(
            source_code,
            external_id,
        )
        if preview:
            item = QListWidgetItem("Preview کشف")
            item.setIcon(QIcon(preview))
            self.live_detail_images.addItem(item)
            preview_text = "۱ عکس Preview دارد"
        else:
            preview_text = "هنوز Preview تصویری ندارد"

        self.live_detail_title.setText(
            external_id or "کاندیدای کشف‌شده"
        )
        self.live_detail_meta.setText(
            f"{preview_text} • دریافت کامل صفحه و عکس‌ها هنوز در صف است."
        )
        self.live_detail_product_btn.setEnabled(False)

    def _go_selected_live_product(self) -> None:
        rows = self._selected_live_records()
        if len(rows) != 1:
            return
        if int(rows[0].get("product_id") or 0) <= 0:
            return
        if callable(self.navigate):
            self.navigate("products")

    def _selected_live_records(self) -> list[dict]:
        output = []
        for item in self.live_results.selectedItems():
            output.append({
                "queue_id": int(item.data(Qt.ItemDataRole.UserRole) or 0),
                "product_id": int(item.data(Qt.ItemDataRole.UserRole + 1) or 0),
                "external_id": str(item.data(Qt.ItemDataRole.UserRole + 2) or ""),
                "url": str(item.data(Qt.ItemDataRole.UserRole + 3) or ""),
            })
        return output

    def _open_selected_live_source(self) -> None:
        rows = self._selected_live_records()
        if not rows:
            return
        url = str(rows[0].get("url") or "")
        if url.startswith(("http://", "https://")):
            QDesktopServices.openUrl(QUrl(url))

    def _collect_selected_live(self) -> None:
        rows = self._selected_live_records()
        if not rows:
            QMessageBox.warning(
                self,
                "نتایج همین جستجو",
                "حداقل یک محصول را انتخاب کن.",
            )
            return
        queue_ids = [
            int(row["queue_id"])
            for row in rows
            if int(row.get("queue_id") or 0) > 0
        ]
        product_ids = [
            int(row["product_id"])
            for row in rows
            if int(row.get("product_id") or 0) > 0
        ]
        if not queue_ids:
            if product_ids and callable(self.navigate):
                self.status.setText(
                    f"{len(set(product_ids))} محصول انتخاب‌شده از قبل داخل محصولات هستند."
                )
                self.navigate("products")
                return
            QMessageBox.warning(
                self,
                "نتایج همین جستجو",
                "برای این انتخاب‌ها رکورد قابل دریافت در صف ساخته نشده است.",
            )
            return
        self._collect_queue_ids(
            queue_ids,
            run_ai=False,
            seed_product_ids=product_ids,
            origin_label="نتایج همین جستجو",
        )

    def _reject_selected_live(self) -> None:
        rows = self._selected_live_records()
        queue_ids = [
            int(row["queue_id"])
            for row in rows
            if int(row.get("queue_id") or 0) > 0
        ]
        if not queue_ids:
            QMessageBox.warning(
                self,
                "نتایج همین جستجو",
                "حداقل یک کاندیدای در صف را انتخاب کن.",
            )
            return
        count = self.kernel.acquisition.reject_queue_items(queue_ids)
        self.status.setText(f"{count} مورد انتخاب‌شده از همین جستجو رد شد.")
        self._populate_queue(reset=True)
        self._refresh_live_discovery()

    def _show_queue_inventory(self) -> None:
        self.workspace_tabs.setCurrentIndex(0)
        self.refresh()

    def _queue_view_changed(self) -> None:
        selected = self._selected_queue_ids()
        target = (
            0
            if str(self.queue_view_mode.currentData() or "icons") == "icons"
            else 1
        )
        self.queue_views.setCurrentIndex(target)
        self.queue_gallery.clearSelection()
        self.queue_table.clearSelection()
        if selected:
            if target == 0:
                for index in range(self.queue_gallery.count()):
                    item = self.queue_gallery.item(index)
                    item.setSelected(
                        int(item.data(Qt.ItemDataRole.UserRole) or 0)
                        in selected
                    )
            else:
                for row_index in range(self.queue_table.rowCount()):
                    item = self.queue_table.item(row_index, 1)
                    if item is not None:
                        self.queue_table.selectRow(row_index) if (
                            int(item.data(Qt.ItemDataRole.UserRole) or 0)
                            in selected
                        ) else None
        self._update_queue_selection_label()

    def _selected_queue_ids(self) -> list[int]:
        values: list[int] = []
        if hasattr(self, "queue_views") and self.queue_views.currentIndex() == 0:
            for item in self.queue_gallery.selectedItems():
                value = item.data(Qt.ItemDataRole.UserRole)
                if value is not None:
                    values.append(int(value))
        else:
            for index in self.queue_table.selectionModel().selectedRows():
                item = self.queue_table.item(index.row(), 1)
                if item is None:
                    continue
                value = item.data(Qt.ItemDataRole.UserRole)
                if value is not None:
                    values.append(int(value))
        return sorted(set(values))

    def _populate_queue(self, reset: bool = True) -> None:
        filter_name = str(
            self.queue_filter.currentData() or "all"
        ) if hasattr(self, "queue_filter") else "all"
        if reset:
            self._queue_offset = 0
            self._queue_total = self.kernel.acquisition.queue_count(
                "",
                filter_name,
            )
            self._queue_rows_by_id = {}
            self.queue_table.setRowCount(0)
            self.queue_gallery.clear()

        if self._queue_offset >= self._queue_total:
            self._update_queue_loaded_label()
            return

        rows = self.kernel.acquisition.queue_page(
            "",
            filter_name,
            limit=self._queue_page_size,
            offset=self._queue_offset,
        )
        if not rows:
            self._queue_total = self._queue_offset
            self._update_queue_loaded_label()
            return

        start_row = self.queue_table.rowCount()
        self.queue_table.setUpdatesEnabled(False)
        self.queue_gallery.setUpdatesEnabled(False)
        try:
            self.queue_table.setRowCount(start_row + len(rows))
            for relative_index, row in enumerate(rows):
                row = dict(row)
                row_index = start_row + relative_index
                queue_id = int(row.get("id") or 0)
                if queue_id:
                    self._queue_rows_by_id[queue_id] = row

                title = self._queue_display_title(row)
                description = self._queue_description(row)
                short_description = description
                if len(short_description) > 95:
                    short_description = short_description[:92].rstrip() + "…"
                image_count = self._queue_image_count(row)
                icon = self._queue_icon(row)
                status = str(row.get("status") or "")
                source = str(row.get("source_code") or "")

                gallery_item = QListWidgetItem()
                gallery_item.setData(Qt.ItemDataRole.UserRole, queue_id)
                gallery_item.setIcon(icon)
                technical_summary = self._queue_technical_summary(row)
                preview_path = self.kernel.acquisition.candidate_preview_path(
                    source,
                    str(row.get("external_id") or ""),
                )
                gallery_lines = [
                    str(title),
                    (
                        f"🖼 {image_count} عکس دارد • {source} • {status}"
                        if image_count > 0
                        else (
                            f"🖼 Preview: 1 عکس • {source} • {status}"
                            if preview_path
                            else f"🔗 {source} • {status} • Preview تصویر ندارد"
                        )
                    ),
                ]
                if technical_summary:
                    gallery_lines.append(technical_summary)
                if short_description:
                    gallery_lines.append(short_description)
                gallery_item.setText("\n".join(gallery_lines))
                gallery_item.setToolTip(
                    (
                        f"Queue #{queue_id}\n"
                        f"Product #{row.get('product_id') or '—'}\n"
                        f"Source: {source}\n"
                        f"Status: {status}\n"
                        f"Images: {image_count}\n\n"
                        f"{description[:800]}\n\n"
                        f"{row.get('url') or row.get('normalized_url') or ''}"
                    )
                )
                self.queue_gallery.addItem(gallery_item)

                url_or_error = str(
                    row.get("last_error")
                    or row.get("url")
                    or row.get("normalized_url")
                    or ""
                )
                image_item = QTableWidgetItem()
                image_item.setIcon(icon)
                image_item.setToolTip(
                    f"{image_count} تصویر محلی/ثبت‌شده"
                )
                image_item.setData(Qt.ItemDataRole.UserRole, queue_id)
                self.queue_table.setItem(row_index, 0, image_item)

                weight = float(row.get("product_estimated_weight_grams") or 0)
                minutes = int(row.get("product_estimated_print_minutes") or 0)
                dimensions = self._queue_dimensions(row)
                if minutes > 0:
                    hours, remainder = divmod(minutes, 60)
                    time_label = f"{hours}h {remainder}m" if hours else f"{remainder}m"
                else:
                    time_label = ""
                values = [
                    str(queue_id),
                    source,
                    status,
                    str(row.get("product_id") or ""),
                    str(title or ""),
                    short_description,
                    (
                        str(image_count)
                        if image_count > 0
                        else ("Preview 1" if preview_path else "")
                    ),
                    f"{weight:g}" if weight > 0 else "",
                    time_label,
                    dimensions,
                    str(row.get("external_id") or ""),
                    str(row.get("attempts") or 0),
                    url_or_error,
                ]
                for offset, value in enumerate(values, start=1):
                    item = QTableWidgetItem(value)
                    if offset == 1:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            queue_id,
                        )
                    if offset == 6 and description:
                        item.setToolTip(description[:1200])
                    if offset == 13:
                        item.setToolTip(url_or_error)
                    self.queue_table.setItem(row_index, offset, item)
                self.queue_table.setRowHeight(row_index, 64)
        finally:
            self.queue_table.setUpdatesEnabled(True)
            self.queue_gallery.setUpdatesEnabled(True)
        self._queue_offset += len(rows)
        self._update_queue_loaded_label()
        self._update_queue_selection_label()

    def _fetch_queue_if_needed(self) -> None:
        if self._queue_offset >= self._queue_total:
            return
        if self.queue_views.currentIndex() == 0:
            bar = self.queue_gallery.verticalScrollBar()
            threshold = 180
        else:
            bar = self.queue_table.verticalScrollBar()
            threshold = 12
        if bar.maximum() <= 0 or bar.value() >= max(0, bar.maximum() - threshold):
            self._populate_queue(reset=False)

    def _update_queue_loaded_label(self) -> None:
        if hasattr(self, "queue_loaded_label"):
            self.queue_loaded_label.setText(
                f"نمایش {self._queue_offset:,} از {self._queue_total:,} • اسکرول برای ادامه"
            )

    def _open_selected_queue_source(self) -> None:
        ids = self._selected_queue_ids()
        if not ids:
            QMessageBox.warning(self, "صف Crawl", "یک رکورد را انتخاب کن.")
            return
        row = self._queue_rows_by_id.get(ids[0]) or {}
        url = str(row.get("url") or row.get("normalized_url") or "").strip()
        if not url.startswith(("http://", "https://")):
            QMessageBox.warning(self, "صف Crawl", "این رکورد لینک عمومی معتبر ندارد.")
            return
        if not QDesktopServices.openUrl(QUrl(url)):
            QMessageBox.warning(self, "صف Crawl", "مرورگر سیستم نتوانست لینک را باز کند.")

    def _reject_selected_queue(self) -> None:
        ids = self._selected_queue_ids()
        if not ids:
            QMessageBox.warning(self, "صف Crawl", "حداقل یک رکورد را انتخاب کن.")
            return
        count = self.kernel.acquisition.reject_queue_items(ids)
        self.status.setText(f"{count} رکورد Crawl به وضعیت rejected رفت.")
        self.refresh()

    def _restore_selected_queue(self) -> None:
        ids = self._selected_queue_ids()
        if not ids:
            QMessageBox.warning(self, "صف Crawl", "حداقل یک رکورد را انتخاب کن.")
            return
        count = self.kernel.acquisition.restore_queue_items(ids)
        self.status.setText(f"{count} رکورد دوباره در صف new قرار گرفت.")
        self.refresh()

    def _recover_selected_queue(self) -> None:
        ids = self._selected_queue_ids()
        if not ids:
            QMessageBox.warning(
                self,
                "بازیابی گروهی",
                "حداقل یک رکورد را انتخاب کن.",
            )
            return
        if self._worker is not None:
            QMessageBox.information(
                self,
                "بازیابی گروهی",
                "یک عملیات دریافت در حال اجرا است.",
            )
            return

        rows = self.kernel.acquisition.queue_rows_by_ids(ids)
        if not rows:
            QMessageBox.warning(
                self,
                "بازیابی گروهی",
                "رکورد انتخاب‌شده در موجودی Crawl پیدا نشد.",
            )
            return

        image_limit = int(
            self.queue_recover_image_limit.currentData() or 5
        )
        answer = QMessageBox.question(
            self,
            "بازیابی دیتا و عکس محصولات",
            (
                f"{len(rows)} رکورد انتخاب شده است.\n"
                f"هدف عکس برای هر Product: {image_limit}\n\n"
                "اگر داده و فایل محلی کافی باشد از همان نسخه موجود استفاده می‌شود.\n"
                "اگر عنوان/توضیح/عکس ناقص باشد صفحه اصلی Product دوباره خوانده می‌شود.\n"
                "عنوان و توضیح فارسی اپراتور، قیمت و وضعیت انتشار بازنویسی نمی‌شوند.\n\n"
                "ادامه؟"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        def job(progress):
            local_reused = 0
            recovered = 0
            created = 0
            failed = 0
            errors: list[str] = []
            product_ids: list[int] = []
            total = max(1, len(rows))
            preferred_method = "rich"
            circuit_breaker = False
            unattempted = 0

            for index, raw in enumerate(rows, 1):
                if self.kernel.acquisition.should_stop():
                    break

                row = dict(raw)
                queue_id = int(row.get("id") or 0)
                source_code = str(row.get("source_code") or "").strip()
                external_id = str(row.get("external_id") or "").strip()
                product_url = str(
                    row.get("url")
                    or row.get("normalized_url")
                    or ""
                ).strip()
                product_id = int(row.get("product_id") or 0)

                if str(row.get("status") or "") == "rejected":
                    self.kernel.acquisition.restore_queue_items([queue_id])

                local_count = len(
                    self.kernel.images.identity_local_items(
                        source_code,
                        external_id,
                        self._queue_product_row(row),
                    )
                )

                if product_id > 0:
                    product_row = self.db.product(product_id)
                    product = dict(product_row) if product_row is not None else {}
                    has_title = bool(
                        str(product.get("title_fa") or "").strip()
                        or str(product.get("source_title") or "").strip()
                    )
                    has_description = bool(
                        str(product.get("short_description_fa") or "").strip()
                        or str(product.get("description_fa") or "").strip()
                        or str(product.get("source_short_description") or "").strip()
                        or str(product.get("source_description") or "").strip()
                    )
                    if (
                        has_title
                        and has_description
                        and local_count >= image_limit
                    ):
                        self.kernel.acquisition.mark_queue_collected([queue_id])
                        if product_id not in product_ids:
                            product_ids.append(product_id)
                        local_reused += 1
                        progress(
                            int(index / total * 100),
                            (
                                f"#{queue_id} • {index}/{total} • "
                                f"داده موجود + {local_count} عکس محلی استفاده شد"
                            ),
                        )
                        continue

                if (
                    not source_code
                    or not product_url.startswith(("http://", "https://"))
                ):
                    failed += 1
                    message = "Queue item has no valid public Product URL/source."
                    errors.append(f"#{queue_id}: {message}")
                    self.kernel.acquisition.mark_queue_failed(
                        [queue_id],
                        message,
                    )
                    circuit_breaker = True
                    unattempted = max(0, total - index)
                    progress(
                        min(99, int(index / total * 100)),
                        (
                            f"#{queue_id} • لینک معتبر ندارد؛ توقف حفاظتی. "
                            f"{unattempted} رکورد بعدی دست‌نخورده ماند."
                        ),
                    )
                    break

                base = int((index - 1) / total * 100)
                span = max(1, int(100 / total))

                def child_progress(value, message):
                    mapped = min(
                        99,
                        base + int(
                            max(0, min(100, int(value))) / 100 * span
                        ),
                    )
                    progress(
                        mapped,
                        f"#{queue_id} • {index}/{total} • {message}",
                    )

                try:
                    result = self.kernel.acquisition.run_single(
                        source_code=source_code,
                        product_url=product_url,
                        image_limit=image_limit,
                        collection_method=preferred_method,
                        download_images=True,
                        download_files=False,
                        same_domain_only=True,
                        progress=child_progress,
                        force_recover=True,
                        adaptive_fallback=True,
                    )
                    preferred_method = str(
                        result.get("selected_method") or preferred_method
                    )
                    new_product_id = int(result.get("product_id") or 0)
                    if new_product_id <= 0:
                        raise RuntimeError(
                            "Recovery finished without a Product id."
                        )
                    self.kernel.acquisition.mark_queue_collected([queue_id])
                    if new_product_id not in product_ids:
                        product_ids.append(new_product_id)
                    if product_id > 0 or result.get("recovered_existing"):
                        recovered += 1
                    else:
                        created += 1
                except Exception as exc:
                    failed += 1
                    message = f"{type(exc).__name__}: {exc}"
                    errors.append(f"#{queue_id}: {message}")
                    self.kernel.acquisition.mark_queue_failed(
                        [queue_id],
                        message,
                    )
                    circuit_breaker = True
                    unattempted = max(0, total - index)
                    progress(
                        min(99, int(index / total * 100)),
                        (
                            f"#{queue_id} • توقف حفاظتی؛ همه روش‌های واقعی ناموفق بودند. "
                            f"{unattempted} رکورد بعدی دست‌نخورده ماند."
                        ),
                    )
                    break

                progress(
                    int(index / total * 100),
                    f"پردازش بازیابی {index}/{total} • روش ترجیحی {preferred_method}",
                )

            return {
                "operation": "queue_recover",
                "local_reused": local_reused,
                "recovered": recovered,
                "created": created,
                "failed": failed,
                "product_ids": product_ids,
                "errors": errors[-20:],
                "stopped": self.kernel.acquisition.should_stop(),
                "circuit_breaker": circuit_breaker,
                "unattempted": unattempted,
                "preferred_method": preferred_method,
            }

        worker = Worker(job)
        self._worker = worker
        self.start_btn.setEnabled(False)
        self.queue_collect_btn.setEnabled(False)
        self.queue_collect_ai_btn.setEnabled(False)
        self.queue_recover_btn.setEnabled(False)
        self.queue_select_incomplete_btn.setEnabled(False)
        self.queue_open_btn.setEnabled(False)
        self.live_add_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(
            f"شروع بازیابی دیتا و عکس {len(rows)} رکورد…"
        )
        worker.signals.progress.connect(self._progress)
        worker.signals.result.connect(self._done)
        worker.signals.error.connect(self._error)
        worker.signals.finished.connect(self._finished)
        self.pool.start(worker)

    def _collect_selected_queue(self, *, run_ai: bool = False) -> None:
        ids = self._selected_queue_ids()
        if not ids:
            QMessageBox.warning(
                self,
                "صف Crawl",
                "حداقل یک رکورد را انتخاب کن.",
            )
            return
        self._collect_queue_ids(
            ids,
            run_ai=run_ai,
            origin_label="موجودی دائمی Crawl",
        )

    def _collect_queue_ids(
        self,
        ids: list[int],
        *,
        run_ai: bool = False,
        seed_product_ids: list[int] | None = None,
        origin_label: str = "صف Crawl",
    ) -> None:
        if self._worker is not None:
            QMessageBox.information(
                self,
                origin_label,
                "یک عملیات دریافت در حال اجرا است.",
            )
            return
        rows = self.kernel.acquisition.queue_rows_by_ids(ids)
        if not rows:
            QMessageBox.warning(
                self,
                origin_label,
                "رکورد انتخاب‌شده در صف پیدا نشد.",
            )
            return

        image_limit = self.image_limit.value()
        download_images = self.download_images.isChecked()
        seed_ids = sorted({
            int(value)
            for value in (seed_product_ids or [])
            if int(value) > 0
        })

        def job(progress):
            collected = 0
            failed = 0
            already = 0
            errors = []
            product_ids: list[int] = list(seed_ids)
            total = max(1, len(rows))
            for index, row in enumerate(rows, 1):
                queue_id = int(row.get("id") or 0)
                status = str(row.get("status") or "")
                existing_product_id = int(row.get("product_id") or 0)
                if status == "collected" and existing_product_id > 0:
                    if existing_product_id not in product_ids:
                        product_ids.append(existing_product_id)
                    already += 1
                    progress(
                        int(index / total * 100),
                        f"#{queue_id}: قبلاً داخل محصولات است.",
                    )
                    continue
                if status == "rejected":
                    self.kernel.acquisition.restore_queue_items([queue_id])
                source_code = str(row.get("source_code") or "").strip()
                product_url = str(
                    row.get("url")
                    or row.get("normalized_url")
                    or ""
                ).strip()
                if not source_code or not product_url.startswith(("http://", "https://")):
                    failed += 1
                    self.kernel.acquisition.mark_queue_failed(
                        [queue_id],
                        "Queue item has no valid public Product URL/source.",
                    )
                    continue

                base = int((index - 1) / total * 100)
                span = max(1, int(100 / total))

                def child_progress(value, message):
                    mapped = min(
                        99,
                        base + int(max(0, min(100, int(value))) / 100 * span),
                    )
                    progress(mapped, f"#{queue_id}: {message}")

                try:
                    result = self.kernel.acquisition.run_single(
                        source_code=source_code,
                        product_url=product_url,
                        image_limit=image_limit,
                        download_images=download_images,
                        progress=child_progress,
                    )
                    self.kernel.acquisition.mark_queue_collected([queue_id])
                    product_id = int(result.get("product_id") or 0)
                    if product_id > 0 and product_id not in product_ids:
                        product_ids.append(product_id)
                    if result.get("already_collected"):
                        already += 1
                    else:
                        collected += int(result.get("collected", 1) or 1)
                except Exception as exc:
                    failed += 1
                    errors.append(f"#{queue_id}: {exc}")
                    self.kernel.acquisition.mark_queue_failed(
                        [queue_id],
                        str(exc),
                    )
                progress(int(index / total * 100), f"پردازش {index}/{total}")

            ai_result = {}
            if run_ai and product_ids:
                progress(
                    88,
                    "شروع ترجمه/SEO انتخاب‌شده‌ها با همان هسته واحد AI…",
                )
                ai_result = self.kernel.complete_products_with_ai(
                    product_ids,
                    "link",
                    progress=lambda value, message: progress(
                        min(
                            99,
                            88 + int(max(0, min(100, int(value))) * 0.11),
                        ),
                        message,
                    ),
                )
            return {
                "operation": "queue_collect_ai" if run_ai else "queue_collect",
                "collected": collected,
                "failed": failed,
                "already_collected_count": already,
                "discovered": 0,
                "product_ids": product_ids,
                "ai": ai_result,
                "errors": errors[-10:],
            }

        worker = Worker(job)
        self._worker = worker
        self.start_btn.setEnabled(False)
        self.queue_collect_btn.setEnabled(False)
        self.queue_collect_ai_btn.setEnabled(False)
        self.queue_open_btn.setEnabled(False)
        self.live_add_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(
            f"شروع پردازش {len(rows)} انتخاب از {origin_label}…"
        )
        worker.signals.progress.connect(self._progress)
        worker.signals.result.connect(self._done)
        worker.signals.error.connect(self._error)
        worker.signals.finished.connect(self._finished)
        self.pool.start(worker)

    def _open_acquisition_logs(self) -> None:
        try:
            path = Path(self.kernel.acquisition.acquisition_log_path()).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
        except Exception as exc:
            QMessageBox.warning(self, "لاگ Crawl", str(exc))

    def refresh(self) -> None:
        self._reload_sources()
        source_code = str(self.source.currentData() or "")
        queue = self.kernel.acquisition.queue_counts(source_code)
        runs = self.kernel.acquisition.recent_runs(limit=12)
        acquisition_log = self.kernel.acquisition.acquisition_log_path()
        acquisition_events = self.kernel.acquisition.recent_acquisition_events(limit=24)

        lines = [
            "صف Source فعلی:",
            *[
                f"- {key}: {value}"
                for key, value in sorted(queue.items())
            ],
            "",
            "روش هوشمند: HTTP/Sitemap را اول امتحان می‌کند و فقط در صورت نیاز "
            "به Browser می‌رود. روش کلاسیک همان Search-Link قدیمی است و با "
            "crawl_listing_state هر بار عمیق‌تر ادامه می‌دهد.",
            "هویت‌های collected/rejected/blocked دوباره Crawl نمی‌شوند.",
            "",
            f"لاگ جزئیات Crawl: {acquisition_log}",
            "این لاگ برای هر Product روش، کیفیت داده، تعداد عکس محلی، Failover و علت شکست را ثبت می‌کند.",
            "",
            "آخرین تلاش‌های دریافت:",
        ]
        for event in acquisition_events[-12:]:
            detail = dict(event.get("detail") or {})
            quality = dict(detail.get("quality") or {})
            lines.append(
                "- "
                f"{event.get('status')} / {event.get('external_id') or '—'} / "
                f"{event.get('method') or '—'} / {event.get('action')} / "
                f"title={quality.get('title_ok', '—')} / "
                f"data={quality.get('data_signal', '—')} / "
                f"local_images={quality.get('local_images', detail.get('images_saved', '—'))} / "
                f"{event.get('message') or ''}"
            )
        lines.extend(["", "۱۲ Run آخر:"])
        for row in runs:
            lines.append(
                f"- #{row.get('id')} {row.get('source_code')} / "
                f"{row.get('mode')} / {row.get('status')} / "
                f"requested={row.get('requested_limit')} / "
                f"collected={row.get('collected_count')} / "
                f"failed={row.get('failed_count')}"
            )
        self.summary.setPlainText("\n".join(lines))
        self._populate_queue(reset=True)
        self._source_changed()

