from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QSortFilterProxyModel, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .models import FilamentFilterProxyModel, FilamentTableModel, ProductTableModel
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
    def __init__(self, db, open_product: Callable[[int], None], parent=None) -> None:
        super().__init__(parent)
        self.db = db
        self.open_product = open_product
        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "محصولات",
            "فهرست Model/View سبک برای جستجو و ورود مستقیم به مسیر ویزارد هر محصول.",
        ))

        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجو در عنوان، شناسه یا لینک…")
        refresh_btn = QPushButton("بروزرسانی")
        refresh_btn.clicked.connect(self.refresh)
        open_btn = QPushButton("بازکردن در ویزارد")
        open_btn.setProperty("primary", True)
        open_btn.clicked.connect(self._open_selected)
        bar.addWidget(self.search, 1)
        bar.addWidget(refresh_btn)
        bar.addWidget(open_btn)
        root.addLayout(bar)

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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(lambda _index: self._open_selected())
        root.addWidget(self.table, 1)

        self.search.textChanged.connect(self.proxy.setFilterFixedString)

    def refresh(self) -> None:
        self.model.refresh()

    def _open_selected(self) -> None:
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            return
        source_index = self.proxy.mapToSource(selection[0])
        product_id = self.model.product_id_at(source_index.row())
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
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
        self.proxy.set_material(material if material != "همه متریال‌ها" else "")
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

    def __init__(self, db, parent=None) -> None:
        super().__init__(parent)
        self.db = db
        self.product_id: int | None = None

        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "ویزارد حرفه‌ای محصول",
            "هفت مرحله ثابت، مسیر روشن، Back/Next قابل پیش‌بینی و نمایش وضعیت محصول در همان Workspace.",
        ))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        self.stepper = StageStepper(self.STAGES)
        self.stepper.setMinimumWidth(240)
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
        self.stage_notes: list[QPlainTextEdit] = []
        descriptions = [
            "عنوان فارسی، دسته‌بندی و هویت پایه محصول.",
            "انتخاب Filamentهای مرکزی، قیمت‌گذاری، وزن/زمان چاپ و Profileهای فروش.",
            "انتخاب تصاویر، تصویر اصلی، Alt و Metadata.",
            "توضیح کوتاه/کامل، Bulletهای فروش، کلیدواژه و SEO.",
            "لینک منبع، طراح، مجوز، مشخصات و داده‌های فنی.",
            "تصویر/عنوان/توضیح Slider، ترتیب و زمان‌بندی نمایش.",
            "Readiness نهایی، صف انتشار، Sync و رسید وضعیت سایت.",
        ]
        for stage, description in zip(self.STAGES, descriptions):
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
            self.stage_notes.append(note)
            self.stack.addWidget(page)
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

        material_count = 0
        try:
            import json
            material_count = len(json.loads(data.get("material_color_options_json") or "[]"))
        except Exception:
            material_count = 0
        image_count = 0
        try:
            import json
            image_count = len(json.loads(data.get("selected_images_json") or "[]"))
        except Exception:
            image_count = 0

        summaries = [
            f"عنوان: {data.get('title_fa') or '—'}\nدسته: {data.get('local_category_slug') or '—'}",
            f"Filamentهای ثبت‌شده: {material_count}\nقیمت: {data.get('final_price') or data.get('suggested_price') or 0:,}",
            f"تصاویر انتخاب‌شده: {image_count}\nتصویر اصلی: {data.get('primary_image_url') or '—'}",
            f"SEO Title: {data.get('seo_title_fa') or '—'}\nContent status: {data.get('content_status') or '—'}",
            f"Source URL: {data.get('source_url') or '—'}\nLicense: {data.get('license_name') or data.get('commercial_status') or '—'}",
            f"Slider: {'فعال' if data.get('homepage_slider_enabled') else 'غیرفعال'}\nSort: {data.get('homepage_slider_sort_order') or '—'}",
            f"Upload ready: {'بله' if data.get('upload_ready') else 'خیر'}\nServer status: {data.get('server_status') or '—'}",
        ]
        for note, summary in zip(self.stage_notes, summaries):
            note.setPlainText(summary)
        self.stepper.set_stage(0)

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
                f"- #{row['id']} {row['source_code']} / {row['mode']} / {row['status']} / {row['started_at']}"
            )
        self.summary.setPlainText("\n".join(lines))


class SettingsPage(QWidget):
    def __init__(self, db, parent=None) -> None:
        super().__init__(parent)
        self.db = db
        root = QVBoxLayout(self)
        root.addWidget(_title_block(
            "تنظیمات و وضعیت Runtime",
            "تنظیمات UI از QSettings و داده‌های کسب‌وکار از همان Catalog SQLite بالغ خوانده می‌شوند.",
        ))
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        self.path_label = QLabel(f"Catalog DB: {self.db.path}")
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.path_label)
        layout.addWidget(QLabel("Qt 6 shell عمداً تا پایان Acceptance جایگزین launch.py فعلی نشده است."))
        root.addWidget(card)
        root.addStretch(1)
