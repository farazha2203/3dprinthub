from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QSortFilterProxyModel, QSize, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabBar,
    QTabWidget,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.phase49_3h_image_limits import HARD_MAX_IMAGE_LIMIT

from .diagnostics import show_diagnostic_error
from .models import (
    SORT_ROLE,
    FilamentFilterProxyModel,
    FilamentTableModel,
    ProductTableModel,
)
from .parity_dialogs import FilamentEditorDialog
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
        self._bulk_ai_worker: Worker | None = None

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

        bar.addWidget(self.search, 1)
        bar.addWidget(QLabel("نمایش"))
        bar.addWidget(self.filter_combo)
        bar.addWidget(QLabel("مرتب‌سازی گالری"))
        bar.addWidget(self.sort_combo)
        bar.addWidget(refresh_btn)
        bar.addWidget(crawl_btn)
        bar.addWidget(edit_btn)
        root.addLayout(bar)

        bulk_bar = QHBoxLayout()
        self.archive_btn = QPushButton("آرشیو انتخاب‌شده‌ها")
        self.remove_btn = QPushButton("حذف از محصولات / رد")
        self.restore_btn = QPushButton("بازیابی انتخاب‌شده‌ها")
        self.bulk_ai_source = QComboBox()
        for item in self.kernel.providers.source_modes():
            self.bulk_ai_source.addItem(item["label"], item["code"])
        data_index = self.bulk_ai_source.findData("data")
        if data_index >= 0:
            self.bulk_ai_source.setCurrentIndex(data_index)
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
            lambda *_args: self._refresh_detail()
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
            lambda *_args: self._refresh_detail()
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

        detail_edit = QPushButton("ویرایش کامل محصول")
        detail_edit.setProperty("primary", True)
        detail_edit.clicked.connect(self._open_selected)

        detail_layout.addWidget(self.preview)
        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.detail_source_title)
        detail_layout.addWidget(self.detail_description)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addStretch(1)
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
        self._refresh_detail()

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
        self._refresh_detail()
        self._update_loaded_label()

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
                f"{len(product_ids)} محصول از لیست فعال رد شود؟\n\n"
                "این عملیات Hard Delete نیست؛ رکورد به‌صورت Tombstone قابل‌بازیابی "
                "نگه داشته می‌شود و Crawler همان هویت را دوباره وارد نمی‌کند."
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

        mode = str(self.bulk_ai_source.currentData() or "data")
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
                "source_mode": str(self.bulk_ai_source.currentData() or "data"),
                "product_count": len(self._selected_product_ids()),
            },
        )

    def _bulk_ai_finished(self) -> None:
        self._bulk_ai_worker = None
        self.bulk_ai_btn.setEnabled(True)
        self.archive_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)

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
        self.detail_meta.setText(
            f"منبع: {row.get('source_name') or row.get('source_code') or '—'}\n"
            f"وضعیت DB: {row.get('workflow_status') or '—'}\n"
            f"چرخه: {lifecycle_text}\n"
            f"تعداد تصاویر: {self.kernel.images.image_count(row)}\n"
            f"SEO: {seo_text}\n"
            f"دسته: {self.kernel.categories.label_for_slug(row.get('local_category_slug') or '')}\n"
            f"Server ID: {row.get('server_id') or '—'}"
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

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "کتابخانه Filament",
            "افزودن/ویرایش/غیرفعال‌سازی با همان موجودی مرکزی و نرخ‌های نهایی Phase49.3I.41.",
        ))

        bar = QHBoxLayout()
        self.material = QComboBox()
        self.material.addItem("همه متریال‌ها")
        self.search = QLineEdit()
        self.search.setPlaceholderText("شرکت، برند، رنگ، متریال…")

        add_btn = QPushButton("فیلامنت جدید")
        add_btn.setProperty("primary", True)
        edit_btn = QPushButton("ویرایش فیلامنت")
        deactivate_btn = QPushButton("غیرفعال")
        refresh_btn = QPushButton("بروزرسانی")

        add_btn.clicked.connect(self._add_filament)
        edit_btn.clicked.connect(self._edit_filament)
        deactivate_btn.clicked.connect(self._deactivate_filament)
        refresh_btn.clicked.connect(self.refresh)

        bar.addWidget(QLabel("متریال"))
        bar.addWidget(self.material)
        bar.addWidget(self.search, 1)
        bar.addWidget(add_btn)
        bar.addWidget(edit_btn)
        bar.addWidget(deactivate_btn)
        bar.addWidget(refresh_btn)
        root.addLayout(bar)

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
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(lambda _index: self._edit_filament())
        root.addWidget(self.table, 1)

        self.search.textChanged.connect(self._apply_filters)
        self.material.currentTextChanged.connect(self._apply_filters)
        self._reload_materials()

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
        dialog = FilamentEditorDialog(parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        try:
            self.kernel.filaments.save(dialog.values())
        except Exception as exc:
            QMessageBox.warning(self, "فیلامنت", str(exc))
            return
        self.refresh()

    def _edit_filament(self) -> None:
        row = self._selected_row()
        if not row:
            QMessageBox.warning(self, "فیلامنت", "یک فیلامنت را انتخاب کن.")
            return
        dialog = FilamentEditorDialog(row, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        try:
            self.kernel.filaments.save(
                dialog.values(),
                previous_row_id=int(row.get("_row_id") or row.get("id") or 0),
            )
        except Exception as exc:
            QMessageBox.warning(self, "فیلامنت", str(exc))
            return
        self.refresh()

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

    def refresh(self) -> None:
        self.model.refresh()
        self._reload_materials()
        self._apply_filters()


class OperationsPage(QWidget):
    """Active Qt acquisition surface over mature 3I.38/43/45 collectors."""

    def __init__(self, db, parent=None, *, kernel=None) -> None:
        super().__init__(parent)
        if kernel is None:
            raise RuntimeError("OperationsPage requires ApplicationKernel")
        self.db = db
        self.kernel = kernel
        self.pool = TaskPool()
        self._worker: Worker | None = None

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "دریافت اطلاعات از سایت‌های مادر",
            "Search/Listing URL بده، تعداد Product و تعداد عکس هر Product را تعیین کن. "
            "Ledger دائمی محصولات قبلی را رد می‌کند؛ اجرای بعدی همان URL به بخش بعدی می‌رود.",
        ))

        controls = QFrame()
        controls.setObjectName("Card")
        grid = QGridLayout(controls)

        self.source = QComboBox()
        self.mode = QComboBox()
        self.mode.addItem(
            "Automatic — Listing پیش‌فرض Source",
            "automatic",
        )
        self.mode.addItem("Search / Listing", "search")
        self.mode.addItem("Category URL", "category")
        self.mode.addItem(
            "Site Crawl از لینک شروع",
            "site_crawl",
        )
        self.mode.addItem(
            "دریافت مستقیم یک Product",
            "single",
        )

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
        self.collection_method.addItem(
            "Rich فعلی — DOM + JSON-LD + Embedded JSON + XHR",
            "rich",
        )
        self.collection_method.addItem(
            "Classic Isolated — روش قدیمی پایدار",
            "classic_isolated",
        )
        self.collection_method.addItem(
            "Classic Exact — HTML/DOM + Screenshot",
            "classic_exact",
        )
        self.collection_method.addItem(
            "Network Capture — XHR/Fetch JSON",
            "network_capture",
        )
        self.collection_method.addItem(
            "Chrome متصل 9222 — نشست مرورگر باز",
            "chrome_attached",
        )
        self.collection_method.addItem(
            "Saved HTML — فایل ذخیره‌شده",
            "saved_html",
        )
        self.collection_method.addItem(
            "Browser DOM — سازگاری نسخه قدیمی",
            "browser_dom",
        )
        self.collection_method.addItem(
            "Public HTTP — سازگاری نسخه قدیمی",
            "public_http",
        )

        self.url = QLineEdit()
        self.url.setPlaceholderText(
            "مثال: https://makerworld.com/en/search/models?keyword=cake+stand"
        )
        self.query = QLineEdit()
        self.query.setPlaceholderText(
            "مثال: cake stand — برای Automatic/Search"
        )
        self.source_hint = QLabel("")
        self.source_hint.setObjectName("Muted")
        self.source_hint.setWordWrap(True)

        self.download_images = QCheckBox(
            "ذخیره تصاویر عمومی باکیفیت"
        )
        self.download_images.setChecked(True)
        self.download_files = QCheckBox(
            "دانلود فایل مستقیم عمومی مدل"
        )
        self.download_files.setChecked(False)
        self.same_domain = QCheckBox(
            "دانلود/خزش فایل فقط در همان دامنه"
        )
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

        self.retry_failed = QCheckBox("تلاش مجدد برای موارد Failed")
        self.start_btn = QPushButton("شروع دریافت")
        self.start_btn.setProperty("primary", True)
        self.stop_btn = QPushButton("توقف امن")
        self.stop_btn.setEnabled(False)
        self.reset_failed_btn = QPushButton(
            "بازگرداندن Failedها به صف"
        )
        self.queue_btn = QPushButton("نمایش وضعیت صف")
        self.default_url_btn = QPushButton(
            "لینک Search پیش‌فرض Source"
        )
        self.direct_btn = QPushButton(
            "دریافت هوشمند از لینک Product"
        )
        self.login_profile_btn = QPushButton("Chrome پروفایل / ورود دستی")
        self.debug_chrome_btn = QPushButton("Chrome متصل 9222")
        self.harvest_btn = QPushButton("🔎 کشف جدیدها از همه Sourceها")
        self.harvest_btn.setProperty("success", True)
        self.source_refresh_btn = QPushButton("♻ بروزرسانی محصولات Source")
        self.refresh_btn = QPushButton("بروزرسانی وضعیت")

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
        grid.addWidget(
            QLabel("عکس باکیفیت برای هر Product"),
            4,
            2,
        )
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

        actions = QHBoxLayout()
        actions.addWidget(self.start_btn)
        actions.addWidget(self.stop_btn)
        actions.addWidget(self.reset_failed_btn)
        actions.addWidget(self.queue_btn)
        actions.addWidget(self.default_url_btn)
        actions.addWidget(self.direct_btn)
        actions.addWidget(self.refresh_btn)
        actions.addStretch(1)
        grid.addLayout(actions, 9, 0, 1, 4)

        legacy_actions = QHBoxLayout()
        legacy_actions.addWidget(self.login_profile_btn)
        legacy_actions.addWidget(self.debug_chrome_btn)
        legacy_actions.addWidget(self.harvest_btn)
        legacy_actions.addWidget(self.source_refresh_btn)
        legacy_actions.addStretch(1)
        grid.addLayout(legacy_actions, 10, 0, 1, 4)
        root.addWidget(controls)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status = QLabel("آماده")
        self.status.setObjectName("Muted")
        root.addWidget(self.progress)
        root.addWidget(self.status)

        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setMaximumHeight(190)
        root.addWidget(self.summary)

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
        self.queue_collect_btn = QPushButton("افزودن انتخاب‌شده‌ها به محصولات")
        self.queue_collect_btn.setProperty("primary", True)
        self.queue_reject_btn = QPushButton("رد/حذف از صف")
        self.queue_restore_btn = QPushButton("بازگرداندن به صف")
        queue_header.addWidget(QLabel("فیلتر"))
        queue_header.addWidget(self.queue_filter)
        queue_header.addWidget(self.queue_collect_btn)
        queue_header.addWidget(self.queue_reject_btn)
        queue_header.addWidget(self.queue_restore_btn)
        self.queue_loaded_label = QLabel("")
        self.queue_loaded_label.setObjectName("Muted")
        queue_header.addStretch(1)
        queue_header.addWidget(self.queue_loaded_label)
        queue_layout.addLayout(queue_header)

        self.queue_table = QTableWidget(0, 8)
        self.queue_table.setHorizontalHeaderLabels([
            "ID صف",
            "Source",
            "وضعیت",
            "Product ID",
            "عنوان",
            "External ID",
            "Attempts",
            "URL / خطا",
        ])
        self.queue_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.queue_table.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.queue_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.queue_table.verticalHeader().setVisible(False)
        self.queue_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.queue_table.horizontalHeader().setSectionResizeMode(
            7,
            QHeaderView.ResizeMode.Stretch,
        )
        queue_layout.addWidget(self.queue_table, 1)
        root.addWidget(queue_card, 1)
        self._queue_rows_by_id: dict[int, dict] = {}
        self._queue_page_size = 100
        self._queue_offset = 0
        self._queue_total = 0
        self.queue_table.verticalScrollBar().valueChanged.connect(
            lambda _value: self._fetch_queue_if_needed()
        )

        self.mode.currentIndexChanged.connect(
            self._mode_changed
        )
        self.collection_method.currentIndexChanged.connect(
            self._method_changed
        )
        self.source.currentIndexChanged.connect(
            self._source_changed
        )
        self.start_btn.clicked.connect(self._start)
        self.stop_btn.clicked.connect(self._stop)
        self.reset_failed_btn.clicked.connect(
            self._reset_failed
        )
        self.queue_btn.clicked.connect(self.refresh)
        self.default_url_btn.clicked.connect(
            self._fill_default_url
        )
        self.direct_btn.clicked.connect(
            self._direct_from_url
        )
        self.login_profile_btn.clicked.connect(self._setup_login_profile)
        self.debug_chrome_btn.clicked.connect(self._launch_debug_chrome)
        self.harvest_btn.clicked.connect(self._portfolio_harvest)
        self.source_refresh_btn.clicked.connect(self._refresh_source_products)
        self.refresh_btn.clicked.connect(self.refresh)
        self.queue_filter.currentIndexChanged.connect(
            lambda _index: self._populate_queue(reset=True)
        )
        self.queue_collect_btn.clicked.connect(self._collect_selected_queue)
        self.queue_reject_btn.clicked.connect(self._reject_selected_queue)
        self.queue_restore_btn.clicked.connect(self._restore_selected_queue)
        self._reload_sources()
        self._mode_changed()
        self._method_changed()
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
        self.status.setText(str(message or ""))

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

    def _selected_queue_ids(self) -> list[int]:
        values = []
        for index in self.queue_table.selectionModel().selectedRows():
            item = self.queue_table.item(index.row(), 0)
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
        try:
            self.queue_table.setRowCount(start_row + len(rows))
            for relative_index, row in enumerate(rows):
                row_index = start_row + relative_index
                queue_id = int(row.get("id") or 0)
                if queue_id:
                    self._queue_rows_by_id[queue_id] = dict(row)
                title = (
                    row.get("product_title_fa")
                    or row.get("product_source_title")
                    or ""
                )
                url_or_error = str(
                    row.get("last_error")
                    or row.get("url")
                    or row.get("normalized_url")
                    or ""
                )
                values = [
                    str(queue_id),
                    str(row.get("source_code") or ""),
                    str(row.get("status") or ""),
                    str(row.get("product_id") or ""),
                    str(title or ""),
                    str(row.get("external_id") or ""),
                    str(row.get("attempts") or 0),
                    url_or_error,
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            queue_id,
                        )
                    self.queue_table.setItem(row_index, column, item)
        finally:
            self.queue_table.setUpdatesEnabled(True)
        self._queue_offset += len(rows)
        self._update_queue_loaded_label()

    def _fetch_queue_if_needed(self) -> None:
        if self._queue_offset >= self._queue_total:
            return
        bar = self.queue_table.verticalScrollBar()
        if bar.maximum() <= 0 or bar.value() >= max(0, bar.maximum() - 12):
            self._populate_queue(reset=False)

    def _update_queue_loaded_label(self) -> None:
        if hasattr(self, "queue_loaded_label"):
            self.queue_loaded_label.setText(
                f"نمایش {self._queue_offset:,} از {self._queue_total:,} • اسکرول برای ادامه"
            )

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

    def _collect_selected_queue(self) -> None:
        if self._worker is not None:
            QMessageBox.information(
                self,
                "صف Crawl",
                "یک عملیات دریافت در حال اجرا است.",
            )
            return
        ids = self._selected_queue_ids()
        if not ids:
            QMessageBox.warning(self, "صف Crawl", "حداقل یک رکورد را انتخاب کن.")
            return
        rows = [
            self._queue_rows_by_id[row_id]
            for row_id in ids
            if row_id in self._queue_rows_by_id
        ]
        if not rows:
            return

        image_limit = self.image_limit.value()
        download_images = self.download_images.isChecked()

        def job(progress):
            collected = 0
            failed = 0
            already = 0
            errors = []
            total = max(1, len(rows))
            for index, row in enumerate(rows, 1):
                queue_id = int(row.get("id") or 0)
                status = str(row.get("status") or "")
                if status == "collected" and row.get("product_id"):
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
            return {
                "collected": collected,
                "failed": failed,
                "already_collected_count": already,
                "discovered": 0,
                "errors": errors[-10:],
            }

        worker = Worker(job)
        self._worker = worker
        self.start_btn.setEnabled(False)
        self.queue_collect_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(
            f"شروع دریافت {len(rows)} رکورد انتخاب‌شده از موجودی دائمی Crawl…"
        )
        worker.signals.progress.connect(self._progress)
        worker.signals.result.connect(self._done)
        worker.signals.error.connect(self._error)
        worker.signals.finished.connect(self._finished)
        self.pool.start(worker)

    def refresh(self) -> None:
        self._reload_sources()
        source_code = str(self.source.currentData() or "")
        queue = self.kernel.acquisition.queue_counts(source_code)
        runs = self.kernel.acquisition.recent_runs(limit=12)

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
            "۱۲ Run آخر:",
        ]
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

