from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QSortFilterProxyModel, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .kernel import build_kernel
from .models import FilamentFilterProxyModel, FilamentTableModel, ProductTableModel
from .product_explorer import ProductGalleryModel
from .widgets import MetricCard, StageStepper, WizardFooter


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
            ("عملیات", "operations"),
            ("تنظیمات", "settings"),
        ):
            button = QPushButton(label)
            if key == "wizard":
                button.setProperty("primary", True)
            button.clicked.connect(lambda _checked=False, route=key: self.navigate(route))
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
    ) -> None:
        super().__init__(parent)
        self.db = db
        self.kernel = kernel or build_kernel(db)
        self.open_product = open_product

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "محصولات",
            "نمای گالری مانند پوشه‌های ویندوز با تصویر واقعی محلی، جستجو و ورود مستقیم به ویرایش محصول.",
        ))

        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجو در عنوان، شناسه یا لینک…")
        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh)
        edit_btn = QPushButton("ویرایش محصول")
        edit_btn.clicked.connect(self._open_selected)
        open_btn = QPushButton("بازکردن در ویزارد")
        open_btn.setProperty("primary", True)
        open_btn.clicked.connect(self._open_selected)
        bar.addWidget(self.search, 1)
        bar.addWidget(refresh_btn)
        bar.addWidget(edit_btn)
        bar.addWidget(open_btn)
        root.addLayout(bar)

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
        self.gallery.setViewMode(QListView.ViewMode.IconMode)
        self.gallery.setResizeMode(QListView.ResizeMode.Adjust)
        self.gallery.setMovement(QListView.Movement.Static)
        self.gallery.setWrapping(True)
        self.gallery.setWordWrap(True)
        self.gallery.setUniformItemSizes(True)
        self.gallery.setIconSize(QSize(220, 160))
        self.gallery.setGridSize(QSize(270, 230))
        self.gallery.setSpacing(8)
        self.gallery.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.gallery.doubleClicked.connect(lambda _index: self._open_selected())
        self.gallery.selectionModel().selectionChanged.connect(
            lambda *_args: self._refresh_detail()
        )

        self.model = ProductTableModel(db)
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(lambda _index: self._open_selected())
        self.table.selectionModel().selectionChanged.connect(
            lambda *_args: self._refresh_detail()
        )

        self.tabs.addTab(self.gallery, "گالری")
        self.tabs.addTab(self.table, "جدول")
        self.tabs.currentChanged.connect(lambda _index: self._refresh_detail())
        splitter.addWidget(self.tabs)

        detail = QFrame()
        detail.setObjectName("Card")
        detail.setMinimumWidth(300)
        detail.setMaximumWidth(400)
        detail_layout = QVBoxLayout(detail)

        self.preview = QLabel("محصولی انتخاب نشده است")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(230)
        self.preview.setWordWrap(True)

        self.detail_title = QLabel("—")
        self.detail_title.setWordWrap(True)
        self.detail_title.setStyleSheet("font-size: 16px; font-weight: 700;")

        self.detail_meta = QLabel("")
        self.detail_meta.setObjectName("Muted")
        self.detail_meta.setWordWrap(True)

        detail_edit = QPushButton("ویرایش محصول")
        detail_edit.setProperty("primary", True)
        detail_edit.clicked.connect(self._open_selected)

        detail_layout.addWidget(self.preview)
        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addStretch(1)
        detail_layout.addWidget(detail_edit)

        splitter.addWidget(detail)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        root.addWidget(splitter, 1)

        self.search.textChanged.connect(self._apply_search)
        self.refresh()

    def _apply_search(self, value: str) -> None:
        self.proxy.setFilterFixedString(value)
        self.gallery_model.refresh(value)
        self._refresh_detail()

    def refresh(self) -> None:
        self.model.refresh()
        query = self.search.text().strip() if hasattr(self, "search") else ""
        self.gallery_model.refresh(query)
        self._refresh_detail()

    def _selected_product_id(self) -> int | None:
        if self.tabs.currentIndex() == 0:
            indexes = self.gallery.selectedIndexes()
            return (
                self.gallery_model.product_id_at(indexes[0].row())
                if indexes
                else None
            )
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            return None
        source_index = self.proxy.mapToSource(selection[0])
        return self.model.product_id_at(source_index.row())

    def _refresh_detail(self) -> None:
        product_id = self._selected_product_id()
        if product_id is None:
            self.preview.clear()
            self.preview.setText("محصولی انتخاب نشده است")
            self.detail_title.setText("—")
            self.detail_meta.setText("")
            return

        row = self.kernel.products.get(product_id)
        if not row:
            return

        title = row.get("title_fa") or row.get("source_title") or "بدون عنوان"
        self.detail_title.setText(f"#{product_id} — {title}")
        self.detail_meta.setText(
            f"منبع: {row.get('source_name') or row.get('source_code') or '—'}\n"
            f"وضعیت: {row.get('workflow_status') or '—'}\n"
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
                340,
                250,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _open_selected(self) -> None:
        product_id = self._selected_product_id()
        if product_id is not None:
            self.open_product(product_id)


class FilamentsPage(QWidget):
    def __init__(self, db, parent=None) -> None:
        super().__init__(parent)
        self.db = db
        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "کتابخانه Filament",
            "نمای Model/View از موجودی مرکزی؛ فیلتر متریال و جستجوی سریع بدون وابستگی به Ctrl/Shift.",
        ))

        bar = QHBoxLayout()
        self.material = QComboBox()
        self.material.addItem("همه متریال‌ها")
        self.search = QLineEdit()
        self.search.setPlaceholderText("شرکت، برند، رنگ، متریال…")
        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh)
        bar.addWidget(QLabel("متریال"))
        bar.addWidget(self.material)
        bar.addWidget(self.search, 1)
        bar.addWidget(refresh_btn)
        root.addLayout(bar)

        self.model = FilamentTableModel(db)
        self.proxy = FilamentFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
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

    def refresh(self) -> None:
        self.model.refresh()
        self._reload_materials()
        self._apply_filters()


class ProductWizardPage(QWidget):
    STAGES = [
        "عنوان و دسته‌بندی",
        "Filament، قیمت و Profile",
        "تصاویر",
        "محتوا و SEO",
        "منبع، مجوز و مشخصات",
        "اسلایدر صفحه اول",
        "آماده‌سازی و انتشار",
    ]

    def __init__(self, db, parent=None, *, kernel=None) -> None:
        super().__init__(parent)
        self.db = db
        self.kernel = kernel or build_kernel(db)
        self.product_id: int | None = None

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "ویزارد حرفه‌ای محصول",
            "هفت مرحله ثابت؛ قابلیت‌های Legacy مرحله‌به‌مرحله روی همان هسته و همان SQLite به Qt منتقل می‌شوند.",
        ))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.stepper = StageStepper(self.STAGES)
        self.stepper.setMinimumWidth(245)
        splitter.addWidget(self.stepper)

        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)

        self.product_label = QLabel("هیچ محصولی انتخاب نشده است.")
        self.product_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.product_meta = QLabel("")
        self.product_meta.setObjectName("Muted")
        self.product_meta.setWordWrap(True)
        workspace_layout.addWidget(self.product_label)
        workspace_layout.addWidget(self.product_meta)

        self.stack = QStackedWidget()
        self.stage_notes: list[QPlainTextEdit | None] = []

        self._build_identity_stage()
        self._build_summary_stage(
            self.STAGES[1],
            "انتخاب Filamentهای مرکزی، قیمت‌گذاری، وزن/زمان چاپ و Profileهای فروش.",
        )
        self._build_images_stage()
        self._build_summary_stage(
            self.STAGES[3],
            "توضیح کوتاه/کامل، Bulletهای فروش، کلیدواژه و SEO.",
        )
        self._build_summary_stage(
            self.STAGES[4],
            "لینک منبع، طراح، مجوز، مشخصات و داده‌های فنی.",
        )
        self._build_summary_stage(
            self.STAGES[5],
            "تصویر/عنوان/توضیح Slider، ترتیب و زمان‌بندی نمایش.",
        )
        self._build_summary_stage(
            self.STAGES[6],
            "Readiness نهایی، صف انتشار، Sync و رسید وضعیت سایت.",
        )

        workspace_layout.addWidget(self.stack, 1)

        self.footer = WizardFooter()
        workspace_layout.addWidget(self.footer)

        splitter.addWidget(workspace)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        self.stepper.stageChanged.connect(self._set_stage)
        self.footer.previousClicked.connect(lambda: self._move(-1))
        self.footer.nextClicked.connect(lambda: self._move(1))
        self._set_stage(0)

    def _build_identity_stage(self) -> None:
        page = QFrame()
        page.setObjectName("Card")
        layout = QVBoxLayout(page)

        label = QLabel(self.STAGES[0])
        label.setStyleSheet("font-size: 18px; font-weight: 700;")
        hint = QLabel(
            "عنوان فارسی و دسته پایه محصول. ذخیره از Core مشترک انجام می‌شود و Stage lock حفظ می‌شود."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        layout.addWidget(label)
        layout.addWidget(hint)

        form = QFormLayout()
        self.title_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("مثال: home-decor یا external-other")
        form.addRow("عنوان فارسی", self.title_edit)
        form.addRow("دسته سایت", self.category_edit)
        layout.addLayout(form)

        self.stage1_note = QPlainTextEdit()
        self.stage1_note.setReadOnly(True)
        layout.addWidget(self.stage1_note, 1)

        actions = QHBoxLayout()
        self.stage1_save = QPushButton("ثبت تغییرات عنوان و دسته")
        self.stage1_save.setProperty("primary", True)
        self.stage1_save.clicked.connect(lambda: self._save_stage1(notify=True))

        self.stage1_unlock = QPushButton("اصلاح مرحله")
        self.stage1_unlock.clicked.connect(self._unlock_stage1)

        actions.addWidget(self.stage1_save)
        actions.addWidget(self.stage1_unlock)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.stack.addWidget(page)
        self.stage_notes.append(self.stage1_note)

    def _build_summary_stage(self, stage: str, description: str) -> None:
        page = QFrame()
        page.setObjectName("Card")
        layout = QVBoxLayout(page)

        label = QLabel(stage)
        label.setStyleSheet("font-size: 18px; font-weight: 700;")
        hint = QLabel(description)
        hint.setWordWrap(True)
        hint.setObjectName("Muted")

        note = QPlainTextEdit()
        note.setReadOnly(True)
        note.setPlaceholderText("خلاصه وضعیت این مرحله برای محصول انتخابی")

        layout.addWidget(label)
        layout.addWidget(hint)
        layout.addWidget(note, 1)

        self.stack.addWidget(page)
        self.stage_notes.append(note)

    def _build_images_stage(self) -> None:
        page = QFrame()
        page.setObjectName("Card")
        layout = QVBoxLayout(page)

        label = QLabel(self.STAGES[2])
        label.setStyleSheet("font-size: 18px; font-weight: 700;")
        hint = QLabel(
            "تصاویر محلی واقعی همین Product نمایش داده می‌شوند؛ هیچ Fetch شبکه‌ای برای Preview انجام نمی‌شود."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")

        self.image_list = QListWidget()
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_list.setMovement(QListWidget.Movement.Static)
        self.image_list.setWrapping(True)
        self.image_list.setWordWrap(True)
        self.image_list.setIconSize(QSize(180, 130))
        self.image_list.setGridSize(QSize(220, 190))
        self.image_list.setSpacing(8)

        self.stage3_note = QPlainTextEdit()
        self.stage3_note.setReadOnly(True)
        self.stage3_note.setMaximumHeight(95)

        layout.addWidget(label)
        layout.addWidget(hint)
        layout.addWidget(self.image_list, 1)
        layout.addWidget(self.stage3_note)

        self.stack.addWidget(page)
        self.stage_notes.append(self.stage3_note)

    def load_product(self, product_id: int) -> None:
        row = self.db.product(int(product_id))
        if row is None:
            self.product_id = None
            self.product_label.setText("محصول پیدا نشد.")
            self.product_meta.setText("")
            return

        self.product_id = int(product_id)
        data = dict(row)
        title = data.get("title_fa") or data.get("source_title") or "بدون عنوان"

        self.product_label.setText(f"#{product_id} — {title}")
        self.product_meta.setText(
            f"منبع: {data.get('source_name') or data.get('source_code') or '—'}"
            f"  •  وضعیت: {data.get('workflow_status') or '—'}"
            f"  •  Server ID: {data.get('server_id') or '—'}"
        )

        self.title_edit.setText(str(data.get("title_fa") or ""))
        self.category_edit.setText(str(data.get("local_category_slug") or ""))

        locked = self.kernel.products.is_stage_locked(product_id, "quick")
        self.title_edit.setEnabled(not locked)
        self.category_edit.setEnabled(not locked)
        self.stage1_save.setEnabled(not locked)
        self.stage1_unlock.setEnabled(locked)

        import json

        try:
            material_count = len(
                json.loads(data.get("material_color_options_json") or "[]")
            )
        except Exception:
            material_count = 0

        try:
            image_count = len(
                json.loads(data.get("selected_images_json") or "[]")
            )
        except Exception:
            image_count = 0

        summaries = [
            (
                f"عنوان: {data.get('title_fa') or '—'}\n"
                f"دسته: {data.get('local_category_slug') or '—'}\n"
                f"وضعیت ویرایش: {'ثبت نهایی؛ برای تغییر اصلاح مرحله را بزن' if locked else 'قابل ویرایش'}"
            ),
            (
                f"Filamentهای ثبت‌شده: {material_count}\n"
                f"قیمت: {data.get('final_price') or data.get('suggested_price') or 0:,}"
            ),
            (
                f"تصاویر انتخاب‌شده: {image_count}\n"
                f"تصویر اصلی: {data.get('primary_image_url') or '—'}"
            ),
            (
                f"SEO Title: {data.get('seo_title_fa') or '—'}\n"
                f"Content status: {data.get('content_status') or '—'}"
            ),
            (
                f"Source URL: {data.get('source_url') or '—'}\n"
                f"License: {data.get('license_name') or data.get('commercial_status') or '—'}"
            ),
            (
                f"Slider: {'فعال' if data.get('homepage_slider_enabled') else 'غیرفعال'}\n"
                f"Sort: {data.get('homepage_slider_sort_order') or '—'}"
            ),
            (
                f"Upload ready: {'بله' if data.get('upload_ready') else 'خیر'}\n"
                f"Server status: {data.get('server_status') or '—'}"
            ),
        ]

        for note, summary in zip(self.stage_notes, summaries):
            if note is not None:
                note.setPlainText(summary)

        self._refresh_images_stage()
        self.stepper.set_stage(0)

    def _refresh_images_stage(self) -> None:
        self.image_list.clear()
        if self.product_id is None:
            return

        items = self.kernel.images.local_items(self.product_id)
        if not items:
            placeholder = QListWidgetItem("تصویر محلی قابل نمایش وجود ندارد")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.image_list.addItem(placeholder)
            return

        for index, item in enumerate(items, 1):
            label_bits = [f"تصویر {index}"]
            if item["primary"] == "1":
                label_bits.append("اصلی")
            if item["selected"] == "1":
                label_bits.append("انتخاب‌شده")

            pixmap = QPixmap(item["path"])
            icon = QIcon()
            if not pixmap.isNull():
                icon = QIcon(
                    pixmap.scaled(
                        180,
                        130,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

            widget_item = QListWidgetItem(icon, " • ".join(label_bits))
            widget_item.setToolTip(item["path"])
            widget_item.setData(Qt.ItemDataRole.UserRole, item)
            self.image_list.addItem(widget_item)

    def _save_stage1(self, *, notify: bool = False) -> bool:
        if self.product_id is None:
            if notify:
                QMessageBox.warning(self, "3DPrintHub", "ابتدا یک محصول را انتخاب کن.")
            return False

        title = self.title_edit.text().strip()
        category = self.category_edit.text().strip()
        if not title or not category:
            if notify:
                QMessageBox.warning(
                    self,
                    "3DPrintHub",
                    "عنوان فارسی و دسته سایت هر دو باید مقدار داشته باشند.",
                )
            return False

        try:
            updated = self.kernel.products.update_operator_fields(
                self.product_id,
                {
                    "title_fa": title,
                    "local_category_slug": category,
                },
            )
        except Exception as exc:
            if notify:
                QMessageBox.warning(self, "3DPrintHub", str(exc))
            return False

        self.product_label.setText(
            f"#{self.product_id} — {updated.get('title_fa') or title}"
        )
        self.stage1_note.setPlainText(
            f"عنوان: {updated.get('title_fa') or '—'}\n"
            f"دسته: {updated.get('local_category_slug') or '—'}\n"
            "وضعیت ویرایش: قابل ویرایش"
        )
        if notify:
            QMessageBox.information(self, "3DPrintHub", "تغییرات مرحله اول ذخیره شد.")
        return True

    def _unlock_stage1(self) -> None:
        if self.product_id is None:
            return
        try:
            self.kernel.products.unlock_stage_for_edit(self.product_id, "quick")
        except Exception as exc:
            QMessageBox.warning(self, "3DPrintHub", str(exc))
            return
        self.load_product(self.product_id)

    def _set_stage(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            self.footer.set_position(index, self.stack.count())

    def _move(self, delta: int) -> None:
        current = self.stack.currentIndex()
        target = max(0, min(self.stack.count() - 1, current + int(delta)))
        self.stepper.set_stage(target)


class OperationsPage(QWidget):
    def __init__(self, db, parent=None) -> None:
        super().__init__(parent)
        self.db = db
        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "مرکز عملیات",
            "صف‌ها، Runها و کارهای طولانی باید بیرون از UI thread اجرا شوند و نتیجه از Signal به رابط برگردد.",
        ))

        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        root.addWidget(self.summary, 1)

        refresh = QPushButton("بروزرسانی وضعیت")
        refresh.clicked.connect(self.refresh)
        root.addWidget(refresh)
        self.refresh()

    def refresh(self) -> None:
        queue = self.db.queue_counts()
        runs = self.db.runs(limit=10)
        lines = ["صف کشف/دریافت:"]
        for key, value in sorted(queue.items()):
            lines.append(f"- {key}: {value}")
        lines.append("")
        lines.append("۱۰ Run آخر:")
        for row in runs:
            lines.append(
                f"- #{row['id']} {row['source_code']} / "
                f"{row['mode']} / {row['status']} / {row['started_at']}"
            )
        self.summary.setPlainText("\n".join(lines))


class SettingsPage(QWidget):
    def __init__(self, db, parent=None, *, kernel=None) -> None:
        super().__init__(parent)
        self.db = db
        self.kernel = kernel or build_kernel(db)

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "تنظیمات و وضعیت Runtime",
            "UI از QSettings و منطق برنامه از Application Kernel و Coreهای اشتراکی استفاده می‌کند.",
        ))

        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)

        self.path_label = QLabel(f"Catalog DB: {self.db.path}")
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.path_label)

        core_names = "، ".join(self.kernel.registry.names())
        self.core_label = QLabel(f"هسته‌های فعال: {core_names}")
        self.core_label.setWordWrap(True)
        layout.addWidget(self.core_label)

        ai_state = "متصل" if self.kernel.ai.available else "Adapter در انتظار 42C"
        self.ai_label = QLabel(f"AI Core: {ai_state}")
        self.ai_label.setWordWrap(True)
        layout.addWidget(self.ai_label)

        layout.addWidget(QLabel(
            "Legacy launch.py تا پایان مهاجرت و Acceptance حفظ می‌شود؛ "
            "Qt منطق کسب‌وکار موازی ایجاد نمی‌کند."
        ))

        root.addWidget(card)
        root.addStretch(1)
