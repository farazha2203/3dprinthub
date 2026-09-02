from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.epic49_desktop_schema import (
    COLOR_BEHAVIORS,
    COLOR_FINISHES,
    effective_filament_offer_price_per_gram,
    normalize_palette_hexes,
)
from app.phase49_3i35_operator_ledger import normalize_ledger_profile


FIXED_PRICE_COLUMN = 12


def _configure_numeric(widget, *, width: int = 150):
    widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    widget.setButtonSymbols(
        widget.ButtonSymbols.NoButtons
    )
    widget.setAlignment(
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    widget.setMinimumWidth(width)
    widget.setAccelerated(True)
    widget.setKeyboardTracking(False)
    return widget


def _money_spin(maximum: int = 2_000_000_000) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(0, maximum)
    spin.setGroupSeparatorShown(True)
    return _configure_numeric(spin, width=175)


def _integer_spin(minimum: int, maximum: int, value: int = 0) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(minimum, maximum)
    spin.setValue(value)
    return _configure_numeric(spin, width=145)


def _float_spin(
    maximum: float,
    decimals: int = 2,
    step: float = 0.1,
) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0, maximum)
    spin.setDecimals(decimals)
    spin.setSingleStep(step)
    return _configure_numeric(spin, width=155)


def _offer_key(item: dict[str, Any]) -> tuple[str, str, str, str]:
    # Brand is the owner-facing identity authority. Manufacturer remains only
    # a hidden compatibility alias on old records/server snapshots.
    return (
        str(item.get("material") or item.get("material_name") or "").strip().casefold(),
        str(item.get("brand") or item.get("brand_name") or "").strip().casefold(),
        str(item.get("color") or item.get("color_name") or "").strip().casefold(),
        str(item.get("color_type") or "solid").strip().casefold(),
    )


def _readonly_item(value: Any) -> QTableWidgetItem:
    item = QTableWidgetItem(str(value))
    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
    return item


class FilamentEditorDialog(QDialog):
    """Professional global Filament inventory / color / pricing editor."""

    PRESETS = (
        ("انتخاب پالت آماده…", []),
        ("صورتی پاستیلی", ["#F7C9D9"]),
        ("آبی پاستیلی", ["#BDD7F2"]),
        ("سبز پاستیلی", ["#C7E7D2"]),
        ("کرم / Ivory", ["#F2E8CF"]),
        ("سفید", ["#F7F7F7"]),
        ("مشکی", ["#161616"]),
        ("قرمز + آبی", ["#D92D20", "#2563EB"]),
        ("هفت‌رنگ", ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#06B6D4", "#3B82F6", "#A855F7"]),
    )

    def __init__(self, row: dict[str, Any] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.row = dict(row or {})
        self._palette: list[str] = []
        self._image_path = str(self.row.get("filament_image_path") or "").strip()
        self.setWindowTitle("فیلامنت — هویت، رنگ، موجودی و قیمت")
        self.resize(980, 820)
        self.setMinimumSize(860, 700)

        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        identity = QGroupBox("هویت و نمایش رنگ")
        form = QFormLayout(identity)
        self.brand = QLineEdit()
        self.material = QLineEdit()
        self.color = QLineEdit()

        self.color_type = QComboBox()
        for code, label in COLOR_BEHAVIORS:
            self.color_type.addItem(label, code)

        self.color_finish = QComboBox()
        for code, label in COLOR_FINISHES:
            self.color_finish.addItem(label, code)

        self.preset = QComboBox()
        for label, values in self.PRESETS:
            self.preset.addItem(label, list(values))
        self.preset.currentIndexChanged.connect(self._preset_changed)

        palette_host = QWidget()
        palette_layout = QHBoxLayout(palette_host)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        self.palette_buttons: list[QPushButton] = []
        for index in range(7):
            button = QPushButton(f"رنگ {index + 1}")
            button.setMinimumWidth(82)
            button.clicked.connect(
                lambda _checked=False, slot=index: self._pick_color(slot)
            )
            self.palette_buttons.append(button)
            palette_layout.addWidget(button)
        palette_layout.addStretch(1)

        form.addRow("برند", self.brand)
        form.addRow("متریال", self.material)
        form.addRow("نام رنگ", self.color)
        form.addRow("رفتار رنگ", self.color_type)
        form.addRow("نوع سطح / Finish", self.color_finish)
        form.addRow("پالت آماده", self.preset)
        form.addRow("رنگ‌های سایت (حداکثر ۷)", palette_host)
        self.tabs.addTab(identity, "هویت و رنگ")

        inventory = QGroupBox("موجودی و قیمت رول")
        grid = QGridLayout(inventory)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        self.roll_weight = _float_spin(100_000, decimals=1, step=50)
        self.stock_weight = _float_spin(100_000_000, decimals=3, step=100)
        self.stock_unit = QComboBox()
        self.stock_unit.addItem("گرم", "g")
        self.stock_unit.addItem("کیلوگرم", "kg")
        stock_box = QWidget()
        stock_layout = QHBoxLayout(stock_box)
        stock_layout.setContentsMargins(0, 0, 0, 0)
        stock_layout.addWidget(self.stock_weight, 1)
        stock_layout.addWidget(self.stock_unit)

        self.purchase_roll = _money_spin()
        self.sale_roll = _money_spin()
        self.print_hourly = _money_spin()
        self.supervision_hourly = _money_spin()
        self.preheat_hours = _float_spin(240, decimals=2, step=0.25)
        self.preheat_temp = _float_spin(500, decimals=1, step=5)
        self.preheat_hourly = _money_spin()

        rows = (
            ("وزن هر رول (گرم)", self.roll_weight),
            ("موجودی", stock_box),
            ("قیمت خرید رول (تومان)", self.purchase_roll),
            ("قیمت فروش رول (تومان)", self.sale_roll),
            ("هزینه ساعتی چاپ", self.print_hourly),
            ("هزینه ساعتی نظارت", self.supervision_hourly),
            ("مدت پیش‌گرم (ساعت)", self.preheat_hours),
            ("دمای پیش‌گرم °C", self.preheat_temp),
            ("هزینه ساعتی پیش‌گرم", self.preheat_hourly),
        )
        for index, (label, widget) in enumerate(rows):
            row_index = index // 2
            col = (index % 2) * 2
            grid.addWidget(QLabel(label), row_index, col)
            grid.addWidget(widget, row_index, col + 1)

        self.rate_label = QLabel()
        self.rate_label.setWordWrap(True)
        self.rate_label.setStyleSheet(
            "font-size:14px;font-weight:700;padding:10px;"
        )
        grid.addWidget(self.rate_label, 5, 0, 1, 4)
        self.tabs.addTab(inventory, "موجودی و قیمت")

        image_group = QGroupBox("تصویر فیلامنت")
        image_layout = QVBoxLayout(image_group)
        image_hint = QLabel(
            "یک عکس واقعی از رول/رنگ انتخاب کن. برنامه نسخه WebP سبک را در "
            "دیتای دائمی Catalog نگه می‌دارد؛ فایل اصلی جابه‌جا نمی‌شود."
        )
        image_hint.setWordWrap(True)
        image_hint.setObjectName("Muted")
        image_layout.addWidget(image_hint)

        self.image_preview = QLabel("تصویری انتخاب نشده است")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(300)
        self.image_preview.setStyleSheet(
            "border:1px solid #cbd5e1;border-radius:10px;padding:12px;"
        )
        image_layout.addWidget(self.image_preview, 1)

        image_actions = QHBoxLayout()
        choose_image = QPushButton("بارگذاری / انتخاب عکس فیلامنت")
        clear_image = QPushButton("حذف انتخاب عکس")
        choose_image.setProperty("primary", True)
        choose_image.clicked.connect(self._choose_image)
        clear_image.clicked.connect(self._clear_image)
        image_actions.addWidget(choose_image)
        image_actions.addWidget(clear_image)
        image_actions.addStretch(1)
        image_layout.addLayout(image_actions)
        self.tabs.addTab(image_group, "تصویر فیلامنت")

        for widget in (
            self.roll_weight,
            self.stock_weight,
            self.sale_roll,
            self.print_hourly,
            self.supervision_hourly,
            self.preheat_hours,
            self.preheat_hourly,
        ):
            widget.valueChanged.connect(self._refresh_rate)
        self.stock_unit.currentIndexChanged.connect(self._refresh_rate)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(
            "ذخیره فیلامنت"
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._load()
        self._refresh_palette_buttons()
        self._refresh_image_preview()
        self._refresh_rate()

    def _load(self) -> None:
        row = self.row
        self.brand.setText(
            str(
                row.get("brand")
                or row.get("brand_name")
                or row.get("manufacturer")
                or row.get("manufacturer_name")
                or ""
            )
        )
        self.material.setText(
            str(row.get("material") or row.get("material_name") or "")
        )
        self.color.setText(str(row.get("color") or row.get("color_name") or ""))

        code = str(row.get("color_type") or "solid")
        index = self.color_type.findData(code)
        self.color_type.setCurrentIndex(index if index >= 0 else 0)

        finish = str(row.get("color_finish") or "matte")
        index = self.color_finish.findData(finish)
        self.color_finish.setCurrentIndex(index if index >= 0 else 0)

        self._palette = normalize_palette_hexes(
            row.get("palette_hexes") or row.get("palette_hex_json") or [],
            row.get("hex") or row.get("hex_code") or "",
            row.get("secondary_hex") or "",
            row.get("tertiary_hex") or "",
        )

        weight = float(row.get("roll_weight_grams") or 1000)
        self.roll_weight.setValue(weight)
        stock_grams = float(row.get("stock_roll_count") or 0) * weight
        if stock_grams >= 1000:
            self.stock_unit.setCurrentIndex(self.stock_unit.findData("kg"))
            self.stock_weight.setValue(stock_grams / 1000)
        else:
            self.stock_unit.setCurrentIndex(self.stock_unit.findData("g"))
            self.stock_weight.setValue(stock_grams)

        self.purchase_roll.setValue(
            int(float(row.get("purchase_price_per_roll") or 0))
        )
        self.sale_roll.setValue(int(float(row.get("sale_price_per_roll") or 0)))
        self.print_hourly.setValue(int(float(row.get("print_hourly_rate") or 0)))
        self.supervision_hourly.setValue(
            int(float(row.get("supervision_hourly_rate") or 0))
        )
        self.preheat_hours.setValue(float(row.get("preheat_hours") or 0))
        self.preheat_temp.setValue(float(row.get("preheat_temperature_c") or 0))
        self.preheat_hourly.setValue(
            int(float(row.get("preheat_hourly_rate") or 0))
        )

    def _preset_changed(self, index: int) -> None:
        values = self.preset.itemData(index)
        if isinstance(values, list) and values:
            self._palette = normalize_palette_hexes(values)
            self._refresh_palette_buttons()

    def _pick_color(self, slot: int) -> None:
        initial = (
            self._palette[slot]
            if 0 <= slot < len(self._palette)
            else "#FFFFFF"
        )
        chosen = QColorDialog.getColor(
            QColor(initial),
            self,
            f"انتخاب رنگ {slot + 1}",
        )
        if not chosen.isValid():
            return
        while len(self._palette) <= slot:
            self._palette.append("")
        self._palette[slot] = chosen.name().upper()
        self._palette = normalize_palette_hexes(self._palette)
        self._refresh_palette_buttons()

    def _refresh_palette_buttons(self) -> None:
        for index, button in enumerate(self.palette_buttons):
            value = self._palette[index] if index < len(self._palette) else ""
            button.setText(value or f"رنگ {index + 1}")
            if value:
                color = QColor(value)
                text = "#111827" if color.lightness() > 150 else "#FFFFFF"
                button.setStyleSheet(
                    f"background:{value};color:{text};font-weight:700;"
                )
            else:
                button.setStyleSheet("")

    def _choose_image(self) -> None:
        path, _selected = QFileDialog.getOpenFileName(
            self,
            "انتخاب تصویر فیلامنت",
            str(Path(self._image_path).parent)
            if self._image_path
            else "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff);;All files (*.*)",
        )
        if path:
            self._image_path = path
            self._refresh_image_preview()

    def _clear_image(self) -> None:
        self._image_path = ""
        self._refresh_image_preview()

    def _refresh_image_preview(self) -> None:
        self.image_preview.clear()
        if not self._image_path or not Path(self._image_path).is_file():
            self.image_preview.setText("تصویری انتخاب نشده است")
            return
        pixmap = QPixmap(self._image_path)
        if pixmap.isNull():
            self.image_preview.setText("خواندن تصویر ناموفق بود")
            return
        self.image_preview.setPixmap(
            pixmap.scaled(
                520,
                320,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _stock_grams(self) -> float:
        value = max(0.0, float(self.stock_weight.value()))
        return value * 1000 if self.stock_unit.currentData() == "kg" else value

    def _refresh_rate(self) -> None:
        weight = max(1.0, float(self.roll_weight.value()))
        sale = max(0.0, float(self.sale_roll.value()))
        rate = sale / weight if sale > 0 else 0
        stock_grams = self._stock_grams()
        self.rate_label.setText(
            f"قیمت خودکار هر گرم: {rate:,.0f} تومان"
            f"   •   موجودی: {stock_grams:,.0f} g / {stock_grams / 1000:,.3f} kg"
            f"   •   معادل رول: {stock_grams / weight:,.3f}"
        )

    def _accept(self) -> None:
        if not self.brand.text().strip():
            QMessageBox.warning(self, "فیلامنت", "برند الزامی است.")
            return
        if not self.material.text().strip():
            QMessageBox.warning(self, "فیلامنت", "نام متریال الزامی است.")
            return
        if not self.color.text().strip():
            QMessageBox.warning(self, "فیلامنت", "نام رنگ الزامی است.")
            return
        if not self._palette:
            QMessageBox.warning(
                self,
                "فیلامنت",
                "حداقل یک رنگ از پالت انتخاب کن.",
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        brand = self.brand.text().strip()
        roll_weight = max(1.0, float(self.roll_weight.value()))
        stock_grams = self._stock_grams()
        palette = normalize_palette_hexes(self._palette)
        return {
            "manufacturer": brand,
            "brand": brand,
            "material": self.material.text().strip(),
            "color": self.color.text().strip(),
            "color_type": self.color_type.currentData(),
            "color_finish": self.color_finish.currentData(),
            "palette_hexes": palette,
            "hex": palette[0] if palette else "",
            "secondary_hex": palette[1] if len(palette) > 1 else "",
            "tertiary_hex": palette[2] if len(palette) > 2 else "",
            "filament_image_path": self._image_path,
            "roll_weight_grams": roll_weight,
            "stock_roll_count": stock_grams / roll_weight,
            "purchase_price_per_roll": self.purchase_roll.value(),
            "sale_price_per_roll": self.sale_roll.value(),
            "print_hourly_rate": self.print_hourly.value(),
            "supervision_hourly_rate": self.supervision_hourly.value(),
            "preheat_hours": self.preheat_hours.value(),
            "preheat_temperature_c": self.preheat_temp.value(),
            "preheat_hourly_rate": self.preheat_hourly.value(),
        }


class ProfileEditorDialog(QDialog):
    """One size/profile owns many production rows and many reusable Filaments."""

    def __init__(
        self,
        filament_rows: list[dict[str, Any]],
        profile: dict[str, Any] | None = None,
        parent=None,
        *,
        filament_core=None,
    ) -> None:
        super().__init__(parent)
        self.filament_core = filament_core
        self.filaments = [dict(item) for item in filament_rows]
        self.original = normalize_ledger_profile(profile or {}, 1)
        self.setWindowTitle("پروفایل تولید و قیمت")
        self.resize(1240, 860)
        self.setMinimumSize(980, 700)

        root = QVBoxLayout(self)
        self.profile_tabs = QTabWidget()
        self.profile_tabs.setDocumentMode(False)
        root.addWidget(self.profile_tabs, 1)

        identity = QGroupBox("هویت سایز / پروفایل")
        form = QGridLayout(identity)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)

        self.name = QLineEdit()
        self.size_label = QLineEdit()
        self.length = _float_spin(100_000, 2, 0.1)
        self.width = _float_spin(100_000, 2, 0.1)
        self.height = _float_spin(100_000, 2, 0.1)
        self.strategy = QComboBox()
        self.strategy.addItem("فرمولی / داینامیک", "dynamic")
        self.strategy.addItem("قیمت قطعی برای هر فیلامنت", "fixed")
        self.strategy.addItem("بازه قیمت", "range")
        self.price_min = _money_spin()
        self.price_max = _money_spin()
        self.support_multiplier = _float_spin(20, 2, 0.1)
        self.assembly_fee = _money_spin()

        fields = [
            ("نام پروفایل", self.name),
            ("سایز", self.size_label),
            ("طول واقعی cm", self.length),
            ("عرض واقعی cm", self.width),
            ("ارتفاع واقعی cm", self.height),
            ("روش قیمت", self.strategy),
            ("حداقل قیمت", self.price_min),
            ("حداکثر قیمت", self.price_max),
            ("ضریب هزینه ساپورت", self.support_multiplier),
            ("هزینه مونتاژ", self.assembly_fee),
        ]
        for index, (label, widget) in enumerate(fields):
            row = index // 2
            col = (index % 2) * 2
            form.addWidget(QLabel(label), row, col)
            form.addWidget(widget, row, col + 1)
        self.profile_tabs.addTab(identity, "پروفایل و روش قیمت")

        production_group = QGroupBox("وزن‌های تولید همین سایز")
        production_layout = QVBoxLayout(production_group)
        self.production = QTableWidget(0, 3)
        self.production.setHorizontalHeaderLabels(
            ("وزن قطعه (g)", "وزن ساپورت (g)", "زمان چاپ (دقیقه)")
        )
        self.production.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.production.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.production.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.production.verticalHeader().setDefaultSectionSize(42)
        production_layout.addWidget(self.production)

        production_actions = QHBoxLayout()
        add_row = QPushButton("افزودن وزن/زمان")
        remove_row = QPushButton("حذف ردیف")
        add_row.clicked.connect(lambda: self._add_production_row())
        remove_row.clicked.connect(self._remove_production_row)
        production_actions.addWidget(add_row)
        production_actions.addWidget(remove_row)
        production_actions.addStretch(1)
        production_layout.addLayout(production_actions)
        self.production.setMinimumHeight(430)
        self.profile_tabs.addTab(production_group, "وزن و زمان تولید")

        filament_group = QGroupBox("فیلامنت‌های قابل چاپ با این سایز")
        filament_layout = QVBoxLayout(filament_group)
        hint = QLabel(
            "قیمت، موجودی و هزینه‌های ساعتی از کتابخانه مرکزی Filament می‌آیند. "
            "فیلامنت انتخابی را همین‌جا ویرایش کن؛ تغییر روی رکورد مرکزی ذخیره می‌شود."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        filament_layout.addWidget(hint)

        self.filament_table = QTableWidget(0, 13)
        self.filament_table.setHorizontalHeaderLabels(
            (
                "انتخاب",
                "متریال",
                "برند",
                "رنگ",
                "موجودی kg",
                "فروش رول",
                "تومان/گرم",
                "چاپ/ساعت",
                "نظارت/ساعت",
                "پیش‌گرم h",
                "دمای پیش‌گرم",
                "پیش‌گرم/ساعت",
                "قیمت قطعی محصول",
            )
        )
        self.filament_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.filament_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.filament_table.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.filament_table.verticalHeader().setDefaultSectionSize(42)
        header = self.filament_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setMinimumSectionSize(80)
        header.setStretchLastSection(False)
        for column, width in enumerate(
            (72, 130, 150, 190, 105, 130, 115, 115, 115, 95, 105, 120, 165)
        ):
            header.resizeSection(column, width)
        self.filament_table.cellDoubleClicked.connect(
            self._filament_double_clicked
        )
        filament_layout.addWidget(self.filament_table)

        filament_actions = QHBoxLayout()
        self.edit_filament_btn = QPushButton(
            "ویرایش قیمت / موجودی / هزینه‌های فیلامنت انتخابی"
        )
        self.edit_filament_btn.setProperty("primary", True)
        self.edit_filament_btn.setEnabled(self.filament_core is not None)
        self.edit_filament_btn.clicked.connect(self._edit_global_filament)
        filament_actions.addWidget(self.edit_filament_btn)
        filament_actions.addStretch(1)
        filament_layout.addLayout(filament_actions)
        self.filament_table.setMinimumHeight(470)
        self.profile_tabs.addTab(
            filament_group,
            "فیلامنت، رنگ و قیمت قطعی",
        )

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        root.addWidget(self.summary_label)

        self.strategy.currentIndexChanged.connect(self._refresh_mode)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("ثبت پروفایل")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._load()
        self._refresh_mode()
        self._refresh_summary()

    def _load(self) -> None:
        p = self.original
        self.name.setText(str(p.get("name") or ""))
        self.size_label.setText(str(p.get("size_label") or ""))
        self.length.setValue(float(p.get("part_length_cm") or 0))
        self.width.setValue(float(p.get("part_width_cm") or 0))
        self.height.setValue(float(p.get("part_height_cm") or 0))
        index = self.strategy.findData(
            str(p.get("pricing_strategy") or "dynamic")
        )
        self.strategy.setCurrentIndex(index if index >= 0 else 0)
        self.price_min.setValue(int(float(p.get("price_min") or 0)))
        self.price_max.setValue(int(float(p.get("price_max") or 0)))
        self.support_multiplier.setValue(
            float(p.get("support_cost_multiplier") or 1)
        )
        self.assembly_fee.setValue(int(float(p.get("assembly_fee") or 0)))

        rows = [
            dict(item)
            for item in (p.get("production_rows") or [])
            if isinstance(item, dict)
        ]
        if not rows:
            rows = [
                {
                    "weight_grams": 0,
                    "support_weight_grams": 0,
                    "print_time_minutes": 60,
                }
            ]
        for row in rows:
            self._add_production_row(row)

        selected_map = {
            _offer_key(item): dict(item)
            for item in (p.get("material_options") or [])
            if isinstance(item, dict)
        }
        self._populate_filaments(selected_map)

    def _populate_filaments(
        self,
        selected_map: dict[tuple[str, str, str, str], dict[str, Any]],
    ) -> None:
        self.filament_table.setRowCount(len(self.filaments))
        for row_index, offer in enumerate(self.filaments):
            key = _offer_key(offer)
            selected = selected_map.get(key)

            check = QTableWidgetItem()
            check.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
            check.setCheckState(
                Qt.CheckState.Checked
                if selected is not None
                else Qt.CheckState.Unchecked
            )
            check.setData(Qt.ItemDataRole.UserRole, deepcopy(offer))
            self.filament_table.setItem(row_index, 0, check)

            stock_kg = (
                float(offer.get("stock_roll_count") or 0)
                * float(offer.get("roll_weight_grams") or 0)
                / 1000
            )
            values = (
                offer.get("material") or offer.get("material_name") or "—",
                offer.get("brand") or offer.get("brand_name") or "—",
                (
                    f"{offer.get('color') or offer.get('color_name') or '—'}"
                    f" / {offer.get('color_finish') or 'matte'}"
                ),
                f"{stock_kg:g}",
                f"{int(float(offer.get('sale_price_per_roll') or 0)):,}",
                f"{effective_filament_offer_price_per_gram(offer):,.0f}",
                f"{int(float(offer.get('print_hourly_rate') or 0)):,}",
                f"{int(float(offer.get('supervision_hourly_rate') or 0)):,}",
                f"{float(offer.get('preheat_hours') or 0):g}",
                f"{float(offer.get('preheat_temperature_c') or 0):g} °C",
                f"{int(float(offer.get('preheat_hourly_rate') or 0)):,}",
            )
            for offset, value in enumerate(values, 1):
                self.filament_table.setItem(
                    row_index,
                    offset,
                    _readonly_item(value),
                )

            fixed = _money_spin()
            fixed.setValue(
                int(float((selected or offer).get("fixed_product_price") or 0))
            )
            fixed.valueChanged.connect(
                lambda _value: self._refresh_summary()
            )
            self.filament_table.setCellWidget(
                row_index,
                FIXED_PRICE_COLUMN,
                fixed,
            )

        self._refresh_mode()

    def _add_production_row(
        self,
        data: dict[str, Any] | None = None,
    ) -> None:
        data = dict(data or {})
        row = self.production.rowCount()
        self.production.insertRow(row)

        weight = _float_spin(100_000, decimals=2, step=1)
        support = _float_spin(100_000, decimals=2, step=1)
        minutes = _integer_spin(1, 100_000, 60)
        weight.setValue(float(data.get("weight_grams") or 0))
        support.setValue(float(data.get("support_weight_grams") or 0))
        minutes.setValue(
            max(1, int(float(data.get("print_time_minutes") or 60)))
        )

        for widget in (weight, support, minutes):
            widget.valueChanged.connect(
                lambda _value: self._refresh_summary()
            )

        self.production.setCellWidget(row, 0, weight)
        self.production.setCellWidget(row, 1, support)
        self.production.setCellWidget(row, 2, minutes)

    def _remove_production_row(self) -> None:
        row = self.production.currentRow()
        if row >= 0:
            self.production.removeRow(row)
        self._refresh_summary()

    def _production_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in range(self.production.rowCount()):
            weight_widget = self.production.cellWidget(row, 0)
            support_widget = self.production.cellWidget(row, 1)
            minutes_widget = self.production.cellWidget(row, 2)
            if not isinstance(weight_widget, QDoubleSpinBox):
                continue
            if not isinstance(support_widget, QDoubleSpinBox):
                continue
            if not isinstance(minutes_widget, QSpinBox):
                continue
            weight = float(weight_widget.value())
            if weight <= 0:
                continue
            rows.append(
                {
                    "weight_grams": weight,
                    "support_weight_grams": max(
                        0.0,
                        float(support_widget.value()),
                    ),
                    "print_time_minutes": max(
                        1,
                        int(minutes_widget.value()),
                    ),
                }
            )
        return rows

    def _selected_filaments(self) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for row in range(self.filament_table.rowCount()):
            check = self.filament_table.item(row, 0)
            if (
                check is None
                or check.checkState() != Qt.CheckState.Checked
            ):
                continue
            offer = dict(check.data(Qt.ItemDataRole.UserRole) or {})
            fixed = self.filament_table.cellWidget(
                row,
                FIXED_PRICE_COLUMN,
            )
            offer["fixed_product_price"] = (
                int(fixed.value()) if isinstance(fixed, QSpinBox) else 0
            )
            output.append(offer)
        return output

    def _selected_filament_row(
        self,
    ) -> tuple[int, dict[str, Any]] | None:
        row = self.filament_table.currentRow()
        if row < 0:
            return None
        check = self.filament_table.item(row, 0)
        if check is None:
            return None
        offer = dict(check.data(Qt.ItemDataRole.UserRole) or {})
        return row, offer

    def _filament_double_clicked(
        self,
        row: int,
        column: int,
    ) -> None:
        if column == FIXED_PRICE_COLUMN:
            return
        self.filament_table.setCurrentCell(row, max(0, column))
        self._edit_global_filament()

    def _edit_global_filament(self) -> None:
        if self.filament_core is None:
            QMessageBox.information(
                self,
                "فیلامنت",
                "ویرایش مرکزی Filament در این Runtime در دسترس نیست.",
            )
            return
        selected = self._selected_filament_row()
        if selected is None:
            QMessageBox.warning(
                self,
                "فیلامنت",
                "یک ردیف فیلامنت را انتخاب کن.",
            )
            return

        _row_index, offer = selected
        old_key = _offer_key(offer)
        selected_map = {
            _offer_key(item): dict(item)
            for item in self._selected_filaments()
        }
        dialog = FilamentEditorDialog(offer, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        try:
            saved = dict(
                self.filament_core.save(
                    dialog.values(),
                    previous_row_id=int(
                        offer.get("id")
                        or offer.get("_row_id")
                        or 0
                    ),
                )
            )
        except Exception as exc:
            QMessageBox.warning(
                self,
                "ویرایش فیلامنت",
                str(exc),
            )
            return

        previous_selected = selected_map.pop(old_key, None)
        if previous_selected is not None:
            saved["fixed_product_price"] = int(
                float(
                    previous_selected.get("fixed_product_price")
                    or 0
                )
            )
            selected_map[_offer_key(saved)] = saved

        self.filaments = [
            dict(item)
            for item in self.filament_core.list()
        ]
        self._populate_filaments(selected_map)
        self._refresh_summary()

    def _refresh_mode(self) -> None:
        mode = str(self.strategy.currentData() or "dynamic")
        self.price_min.setEnabled(mode == "range")
        self.price_max.setEnabled(mode == "range")
        for row in range(self.filament_table.rowCount()):
            widget = self.filament_table.cellWidget(
                row,
                FIXED_PRICE_COLUMN,
            )
            if widget is not None:
                widget.setEnabled(mode == "fixed")
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        production_count = len(self._production_rows())
        filament_count = len(self._selected_filaments())
        combinations = production_count * filament_count
        mode_label = self.strategy.currentText()
        self.summary_label.setText(
            f"این سایز: {production_count} وزن/زمان × "
            f"{filament_count} فیلامنت = {combinations} حالت تولید/قیمت"
            f"   •   روش قیمت: {mode_label}"
        )

    def _accept(self) -> None:
        if not self.name.text().strip():
            QMessageBox.warning(
                self,
                "پروفایل",
                "نام پروفایل الزامی است.",
            )
            return
        if not self.size_label.text().strip():
            QMessageBox.warning(
                self,
                "پروفایل",
                "سایز پروفایل الزامی است.",
            )
            return
        if min(
            self.length.value(),
            self.width.value(),
            self.height.value(),
        ) <= 0:
            QMessageBox.warning(
                self,
                "پروفایل",
                "طول، عرض و ارتفاع واقعی باید بیشتر از صفر باشند.",
            )
            return
        if not self._production_rows():
            QMessageBox.warning(
                self,
                "پروفایل",
                "حداقل یک وزن/زمان چاپ معتبر لازم است.",
            )
            return
        if not self._selected_filaments():
            QMessageBox.warning(
                self,
                "پروفایل",
                "حداقل یک فیلامنت برای این سایز انتخاب کن.",
            )
            return
        if self.strategy.currentData() == "fixed":
            missing = [
                row
                for row in range(self.filament_table.rowCount())
                if self.filament_table.item(row, 0)
                and self.filament_table.item(
                    row,
                    0,
                ).checkState()
                == Qt.CheckState.Checked
                and isinstance(
                    self.filament_table.cellWidget(
                        row,
                        FIXED_PRICE_COLUMN,
                    ),
                    QSpinBox,
                )
                and self.filament_table.cellWidget(
                    row,
                    FIXED_PRICE_COLUMN,
                ).value()
                <= 0
            ]
            if missing:
                QMessageBox.warning(
                    self,
                    "پروفایل",
                    "در حالت قیمت قطعی، برای همه فیلامنت‌های انتخابی "
                    "قیمت همین محصول را وارد کن.",
                )
                return
        self.accept()

    def values(self) -> dict[str, Any]:
        result = dict(self.original)
        result.update(
            {
                "name": self.name.text().strip(),
                "size_label": self.size_label.text().strip(),
                "part_length_cm": self.length.value(),
                "part_width_cm": self.width.value(),
                "part_height_cm": self.height.value(),
                "production_rows": self._production_rows(),
                "material_options": self._selected_filaments(),
                "pricing_strategy": str(
                    self.strategy.currentData()
                    or "dynamic"
                ),
                "price_min": self.price_min.value(),
                "price_max": self.price_max.value(),
                "support_cost_multiplier": self.support_multiplier.value(),
                "assembly_fee": self.assembly_fee.value(),
            }
        )
        return normalize_ledger_profile(result, 1)
