from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
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
    QPlainTextEdit,
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

    def __init__(
        self,
        row: dict[str, Any] | None = None,
        parent=None,
        *,
        filament_core=None,
    ) -> None:
        super().__init__(parent)
        self.filament_core = filament_core
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
        self.brand_library = QComboBox()
        self.brand_library.addItem("انتخاب برند ثبت‌شده…", "")
        self.material_library = QComboBox()
        self.material_library.addItem("انتخاب متریال ثبت‌شده…", "")
        if self.filament_core is not None:
            for value in self.filament_core.brands():
                self.brand_library.addItem(str(value), str(value))
            for value in self.filament_core.materials():
                self.material_library.addItem(str(value), str(value))

        self.color = QLineEdit()
        self.color.setReadOnly(True)
        self.filament_description = QPlainTextEdit()
        self.filament_description.setPlaceholderText(
            "توضیح اختیاری فیلامنت برای مدیریت و SEO سایت"
        )
        self.filament_description.setMaximumHeight(105)
        self.color_library = QComboBox()
        self.color_library.addItem("انتخاب رنگ ثبت‌شده…", None)
        if self.filament_core is not None:
            for preset in self.filament_core.color_presets():
                self.color_library.addItem(str(preset.get("name") or ""), dict(preset))
        self.color_library.currentIndexChanged.connect(self._color_library_changed)

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

        form.addRow("برند", self.brand_library)
        form.addRow("متریال", self.material_library)
        form.addRow("رنگ", self.color_library)
        form.addRow("نام رنگ تخصیص‌یافته", self.color)
        form.addRow("توضیح اختیاری Filament", self.filament_description)
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
        brand_value = str(
            row.get("brand")
            or row.get("brand_name")
            or row.get("manufacturer")
            or row.get("manufacturer_name")
            or ""
        ).strip()
        material_value = str(
            row.get("material") or row.get("material_name") or ""
        ).strip()
        for combo, value in (
            (self.brand_library, brand_value),
            (self.material_library, material_value),
        ):
            if value and combo.findData(value) < 0:
                combo.addItem(value, value)
            index = combo.findData(value)
            combo.setCurrentIndex(index if index >= 0 else 0)

        color_value = str(row.get("color") or row.get("color_name") or "").strip()
        self.color.setText(color_value)
        self.filament_description.setPlainText(
            str(row.get("description") or row.get("filament_description") or "")
        )
        if color_value:
            for preset_index in range(self.color_library.count()):
                preset = self.color_library.itemData(preset_index)
                if (
                    isinstance(preset, dict)
                    and str(preset.get("name") or "").strip().casefold()
                    == color_value.casefold()
                ):
                    self.color_library.setCurrentIndex(preset_index)
                    break

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

    def _color_library_changed(self, index: int) -> None:
        preset = self.color_library.itemData(index)
        if not isinstance(preset, dict):
            return
        name = str(preset.get("name") or "").strip()
        if name:
            self.color.setText(name)
        kind = str(preset.get("color_type") or "solid")
        kind_index = self.color_type.findData(kind)
        if kind_index >= 0:
            self.color_type.setCurrentIndex(kind_index)
        finish = str(preset.get("color_finish") or "matte")
        finish_index = self.color_finish.findData(finish)
        if finish_index >= 0:
            self.color_finish.setCurrentIndex(finish_index)
        palette = normalize_palette_hexes(preset.get("palette_hexes") or [])
        if palette:
            self._palette = palette
            self._refresh_palette_buttons()

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
        if not str(self.brand_library.currentData() or "").strip():
            QMessageBox.warning(self, "فیلامنت", "برند را از تب برندها تعریف و انتخاب کن.")
            return
        if not str(self.material_library.currentData() or "").strip():
            QMessageBox.warning(self, "فیلامنت", "متریال را از تب متریال‌ها تعریف و انتخاب کن.")
            return
        if not self.color.text().strip():
            QMessageBox.warning(self, "فیلامنت", "رنگ را از تب رنگ‌ها تعریف و انتخاب کن.")
            return
        if not self._palette:
            QMessageBox.warning(
                self,
                "فیلامنت",
                "حداقل یک رنگ از پالت ثبت‌شده انتخاب کن.",
            )
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        brand = str(self.brand_library.currentData() or "").strip()
        roll_weight = max(1.0, float(self.roll_weight.value()))
        stock_grams = self._stock_grams()
        palette = normalize_palette_hexes(self._palette)
        return {
            "manufacturer": brand,
            "brand": brand,
            "material": str(self.material_library.currentData() or "").strip(),
            "color": self.color.text().strip(),
            "description": self.filament_description.toPlainText().strip(),
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


class ColorPresetDialog(QDialog):
    """Reusable site-facing color identity without Filament pricing fields."""

    def __init__(self, preset: dict[str, Any] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.original = dict(preset or {})
        self._palette = normalize_palette_hexes(self.original.get("palette_hexes") or [])
        self.setWindowTitle("رنگ — پالت، رفتار و Finish")
        self.resize(760, 360)

        root = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit(str(self.original.get("name") or ""))
        self.color_type = QComboBox()
        for code, label in COLOR_BEHAVIORS:
            self.color_type.addItem(label, code)
        self.color_finish = QComboBox()
        for code, label in COLOR_FINISHES:
            self.color_finish.addItem(label, code)

        kind = str(self.original.get("color_type") or "solid")
        index = self.color_type.findData(kind)
        self.color_type.setCurrentIndex(index if index >= 0 else 0)
        finish = str(self.original.get("color_finish") or "matte")
        index = self.color_finish.findData(finish)
        self.color_finish.setCurrentIndex(index if index >= 0 else 0)

        palette_host = QWidget()
        palette_layout = QHBoxLayout(palette_host)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        self.palette_buttons: list[QPushButton] = []
        for slot in range(7):
            button = QPushButton(f"رنگ {slot + 1}")
            button.setMinimumWidth(82)
            button.clicked.connect(
                lambda _checked=False, index=slot: self._pick_color(index)
            )
            self.palette_buttons.append(button)
            palette_layout.addWidget(button)
        palette_layout.addStretch(1)

        form.addRow("نام رنگ", self.name)
        form.addRow("رفتار رنگ", self.color_type)
        form.addRow("Finish", self.color_finish)
        form.addRow("پالت سایت (حداکثر ۷)", palette_host)
        root.addLayout(form)

        hint = QLabel(
            "برای تک‌رنگ یک خانه، برای دو/چندرنگ چند خانه و برای Gradient/Color Shift "
            "ترتیب رنگ‌ها را از ابتدا تا انتها انتخاب کن."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        root.addWidget(hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("ذخیره رنگ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._refresh_palette_buttons()

    def _pick_color(self, slot: int) -> None:
        initial = self._palette[slot] if slot < len(self._palette) else "#FFFFFF"
        chosen = QColorDialog.getColor(QColor(initial), self, f"انتخاب رنگ {slot + 1}")
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

    def _accept(self) -> None:
        if not self.name.text().strip():
            QMessageBox.warning(self, "رنگ", "نام رنگ الزامی است.")
            return
        if not self._palette:
            QMessageBox.warning(self, "رنگ", "حداقل یک رنگ از Color Picker انتخاب کن.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "name": self.name.text().strip(),
            "color_type": str(self.color_type.currentData() or "solid"),
            "color_finish": str(self.color_finish.currentData() or "matte"),
            "palette_hexes": normalize_palette_hexes(self._palette),
        }


class FilamentBulkRatesDialog(QDialog):
    """Apply only explicitly enabled operational rates to many Filaments."""

    def __init__(self, count: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("ویرایش گروهی هزینه و پیش‌گرم Filament")
        self.resize(720, 430)
        root = QVBoxLayout(self)
        hint = QLabel(
            f"{max(0, int(count))} Filament در این عملیات هستند. "
            "فقط ردیف‌هایی که تیک «اعمال» دارند تغییر می‌کنند؛ هویت، رنگ، موجودی و قیمت رول دست‌نخورده می‌ماند."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        root.addWidget(hint)

        grid = QGridLayout()
        grid.addWidget(QLabel("اعمال"), 0, 0)
        grid.addWidget(QLabel("فیلد"), 0, 1)
        grid.addWidget(QLabel("مقدار جدید"), 0, 2)
        self._fields: dict[str, tuple[QCheckBox, QWidget]] = {}

        rows = (
            ("print_hourly_rate", "هزینه ساعتی چاپ (تومان)", _money_spin()),
            ("supervision_hourly_rate", "هزینه ساعتی نظارت (تومان)", _money_spin()),
            ("preheat_hours", "مدت پیش‌گرم (ساعت)", _float_spin(240, 2, 0.25)),
            ("preheat_temperature_c", "دمای پیش‌گرم °C", _float_spin(500, 1, 5)),
            ("preheat_hourly_rate", "هزینه ساعتی پیش‌گرم (تومان)", _money_spin()),
        )
        for row_index, (key, label, widget) in enumerate(rows, 1):
            enabled = QCheckBox()
            enabled.toggled.connect(widget.setEnabled)
            widget.setEnabled(False)
            grid.addWidget(enabled, row_index, 0)
            grid.addWidget(QLabel(label), row_index, 1)
            grid.addWidget(widget, row_index, 2)
            self._fields[key] = (enabled, widget)
        root.addLayout(grid)
        root.addStretch(1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("اعمال گروهی")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _accept(self) -> None:
        if not self.values():
            QMessageBox.warning(self, "ویرایش گروهی", "حداقل یک فیلد را برای اعمال انتخاب کن.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, (enabled, widget) in self._fields.items():
            if not enabled.isChecked():
                continue
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                output[key] = widget.value()
        return output


class FilamentBulkIdentityDialog(QDialog):
    """Repair only the explicit Brand identity for selected Filament rows."""

    def __init__(
        self,
        brands: list[str],
        count: int,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("تکمیل برند Filamentهای انتخابی")
        self.resize(620, 250)

        root = QVBoxLayout(self)
        hint = QLabel(
            f"{max(0, int(count))} Filament انتخاب شده است. "
            "این عملیات فقط Brand/Manufacturer را از کتابخانه ثبت‌شده اعمال می‌کند؛ "
            "متریال، رنگ، قیمت، موجودی و تنظیمات چاپ تغییر نمی‌کنند."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Muted")
        root.addWidget(hint)

        form = QFormLayout()
        self.brand = QComboBox()
        self.brand.addItem("برند ثبت‌شده را انتخاب کن…", "")
        for value in brands or []:
            name = str(value or "").strip()
            if name:
                self.brand.addItem(name, name)
        form.addRow("Brand", self.brand)
        root.addLayout(form)

        warning = QLabel(
            "برای جلوگیری از ثبت اطلاعات نادرست، برنامه Brand را حدس نمی‌زند. "
            "اگر برند موردنظر در فهرست نیست، ابتدا از تب «برندها» آن را بساز."
        )
        warning.setWordWrap(True)
        warning.setObjectName("Muted")
        root.addWidget(warning)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("اعمال Brand")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _accept(self) -> None:
        if not self.selected_brand():
            QMessageBox.warning(self, "تکمیل Brand", "یک Brand ثبت‌شده را انتخاب کن.")
            return
        self.accept()

    def selected_brand(self) -> str:
        return str(self.brand.currentData() or "").strip()


class SourceFilamentMappingDialog(QDialog):
    """Read-only W4 Source-slot to real Local Filament/pricing review."""

    MATCH_LABELS = {
        "exact_hex": "Exact HEX",
        "distance_only": "HEX فاصله‌ای - فقط Review",
        "no_local_hex": "HEX محلی ثبت نشده",
    }

    def __init__(self, preview: dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.preview = dict(preview or {})
        self.setWindowTitle("W4 - تطبیق Source Filament با موجودی محلی")
        self.resize(1480, 880)
        self.setMinimumSize(1080, 680)

        root = QVBoxLayout(self)
        summary = QLabel(
            "این صفحه فقط Preview است؛ هیچ Profile، قیمت، Stage Lock یا Site state "
            "را تغییر نمی‌دهد. تطبیق رنگ فقط از HEX/Palette ثبت‌شده محلی استفاده می‌کند."
        )
        summary.setWordWrap(True)
        summary.setStyleSheet("font-size:14px;font-weight:700;padding:8px;")
        root.addWidget(summary)

        stats = QLabel(
            f"{int(self.preview.get('profile_count') or 0)} Profile • "
            f"{int(self.preview.get('slot_count') or 0)} Source slot • "
            f"{int(self.preview.get('candidate_count') or 0)} Local candidate • "
            f"Exact HEX: {int(self.preview.get('exact_hex_candidate_count') or 0)} • "
            f"HEX قابل مقایسه: {int(self.preview.get('distance_only_candidate_count') or 0)} • "
            f"بدون HEX محلی: {int(self.preview.get('no_local_hex_candidate_count') or 0)}"
        )
        stats.setObjectName("Muted")
        stats.setWordWrap(True)
        root.addWidget(stats)

        note = QLabel(
            "برای Profile چندرنگ، ردیف‌ها به ازای هر Source slot جدا هستند. "
            "هزینه material هر slot با وزن factual همان slot محاسبه می‌شود؛ "
            "قیمت نهایی ترکیبی تا انتخاب واقعی offerها تولید نمی‌شود. "
            "نام فارسی رنگ هرگز به HEX حدس زده نمی‌شود."
        )
        note.setObjectName("Muted")
        note.setWordWrap(True)
        root.addWidget(note)

        self.table = QTableWidget(0, 13)
        self.table.setHorizontalHeaderLabels(
            (
                "Source Profile",
                "Slot",
                "Source",
                "HEX Source",
                "مصرف g",
                "برند Local",
                "رنگ Local",
                "HEX Local",
                "وضعیت رنگ",
                "موجودی kg",
                "فروش رول",
                "هزینه material slot",
                "قیمت کل Single",
            )
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setHorizontalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(False)
        widths = (220, 60, 95, 105, 85, 130, 190, 105, 170, 95, 120, 150, 150)
        for column, width in enumerate(widths):
            header.resizeSection(column, width)
        self.table.verticalHeader().setDefaultSectionSize(38)
        root.addWidget(self.table, 1)

        rows: list[tuple] = []
        for profile in self.preview.get("profiles") or []:
            if not isinstance(profile, dict):
                continue
            profile_name = str(profile.get("profile_name") or "")
            single_slot = bool(profile.get("single_slot"))
            for slot in profile.get("slots") or []:
                if not isinstance(slot, dict):
                    continue
                for candidate in slot.get("candidates") or []:
                    if not isinstance(candidate, dict):
                        continue
                    offer = dict(candidate.get("offer") or {})
                    palette = [
                        str(value)
                        for value in (offer.get("explicit_palette_hexes") or [])
                        if str(value)
                    ]
                    stock_kg = (
                        float(offer.get("stock_roll_count") or 0)
                        * float(offer.get("roll_weight_grams") or 0)
                        / 1000.0
                    )
                    total = candidate.get("single_slot_profile_total")
                    rows.append(
                        (
                            profile_name,
                            int(slot.get("slot_index") or 0),
                            str(slot.get("source_material") or ""),
                            str(slot.get("source_hex") or "—"),
                            f"{float(slot.get('used_grams') or 0):g}",
                            str(offer.get("brand") or "—"),
                            str(offer.get("color") or "—"),
                            ", ".join(palette) if palette else "—",
                            self.MATCH_LABELS.get(
                                str(candidate.get("color_match") or ""),
                                str(candidate.get("color_match") or "—"),
                            ),
                            f"{stock_kg:g}",
                            f"{int(float(offer.get('sale_price_per_roll') or 0)):,}",
                            f"{int(candidate.get('slot_material_cost') or 0):,}",
                            (
                                f"{int(total):,}"
                                if single_slot and total
                                else "—"
                            ),
                        )
                    )

        self.table.setRowCount(len(rows))
        for row_index, values in enumerate(rows):
            for column, value in enumerate(values):
                self.table.setItem(
                    row_index,
                    column,
                    _readonly_item(value),
                )

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.clicked.connect(self.close)
        root.addWidget(buttons)


class ProfileEditorDialog(QDialog):
    """One size/profile owns many production rows and many reusable Filaments."""

    def __init__(
        self,
        filament_rows: list[dict[str, Any]],
        profile: dict[str, Any] | None = None,
        parent=None,
        *,
        filament_core=None,
        recommended_materials: list[str] | None = None,
        recommendation_reason: str = "",
    ) -> None:
        super().__init__(parent)
        self.filament_core = filament_core
        self.recommended_materials = {
            str(item or "").strip().casefold()
            for item in (recommended_materials or [])
            if str(item or "").strip()
        }
        self.recommendation_reason = str(recommendation_reason or "").strip()
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
        for widget in (self.length, self.width, self.height):
            widget.setSpecialValueText("نامشخص")
            widget.setToolTip(
                "صفر یعنی این محور هنوز از Source یا اپراتور مشخص نشده است."
            )
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
        self.dimension_hint = QLabel()
        self.dimension_hint.setObjectName("Muted")
        self.dimension_hint.setWordWrap(True)
        form.addWidget(self.dimension_hint, 5, 0, 1, 4)
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
        select_all_filaments = QPushButton("انتخاب همه فیلامنت‌ها")
        clear_all_filaments = QPushButton("لغو انتخاب همه")
        smart_filaments = QPushButton("انتخاب هوشمند متریال مناسب محصول")
        smart_filaments.setProperty("primary", True)
        smart_filaments.setEnabled(bool(self.recommended_materials))
        smart_filaments.setToolTip(
            self.recommendation_reason
            or "پیشنهاد بر اساس نوع/کاربرد محصول و خواص متریال‌های ثبت‌شده"
        )
        select_all_filaments.clicked.connect(lambda: self._set_all_filaments_checked(True))
        clear_all_filaments.clicked.connect(lambda: self._set_all_filaments_checked(False))
        smart_filaments.clicked.connect(self._select_recommended_filaments)
        filament_actions.addWidget(select_all_filaments)
        filament_actions.addWidget(clear_all_filaments)
        filament_actions.addWidget(smart_filaments)
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
        dimension_source = str(p.get("dimension_source") or "").strip()
        known_axes = [
            axis
            for axis in (p.get("dimension_known_axes") or [])
            if axis in {"length", "width", "height"}
        ]
        if dimension_source:
            axis_labels = {
                "length": "طول",
                "width": "عرض",
                "height": "ارتفاع",
            }
            known_text = "، ".join(
                axis_labels[axis] for axis in known_axes
            ) or "—"
            label = str(p.get("dimension_label") or "").strip()
            evidence = str(p.get("dimension_evidence") or "").strip()
            source_label = (
                "تخمینی اپراتور"
                if bool(p.get("dimension_is_estimated"))
                else "Source factual"
            )
            self.dimension_hint.setText(
                f"ابعاد: {source_label}"
                f"{' • ' + label if label else ''}"
                f" • محورهای ثبت‌شده: {known_text}"
                f"{' • ' + evidence if evidence else ''}"
            )
        else:
            self.dimension_hint.setText(
                "برای پروفایل دستی، طول/عرض/ارتفاع باید کامل ثبت شوند."
            )
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

    def _set_all_filaments_checked(self, checked: bool) -> None:
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for row in range(self.filament_table.rowCount()):
            item = self.filament_table.item(row, 0)
            if item is not None:
                item.setCheckState(state)
        self._refresh_summary()

    def _select_recommended_filaments(self) -> None:
        if not self.recommended_materials:
            QMessageBox.information(
                self,
                "انتخاب هوشمند متریال",
                "برای این محصول پیشنهاد متریال آماده نشده است.",
            )
            return
        selected_count = 0
        for row in range(self.filament_table.rowCount()):
            item = self.filament_table.item(row, 0)
            if item is None:
                continue
            offer = dict(item.data(Qt.ItemDataRole.UserRole) or {})
            material = str(
                offer.get("material") or offer.get("material_name") or ""
            ).strip().casefold()
            checked = material in self.recommended_materials
            item.setCheckState(
                Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            )
            selected_count += int(checked)
        self._refresh_summary()
        QMessageBox.information(
            self,
            "انتخاب هوشمند متریال",
            f"{selected_count} Filament از متریال‌های مناسب انتخاب شد.\n"
            + (self.recommendation_reason or ""),
        )

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
        dialog = FilamentEditorDialog(offer, parent=self, filament_core=self.filament_core)
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
        dimension_values = {
            "length": float(self.length.value()),
            "width": float(self.width.value()),
            "height": float(self.height.value()),
        }
        dimension_source = str(
            self.original.get("dimension_source") or ""
        ).strip()
        known_axes = {
            axis
            for axis in (self.original.get("dimension_known_axes") or [])
            if axis in {"length", "width", "height"}
        }
        partial_source_allowed = (
            dimension_source in {"source_description", "mixed"}
            and bool(known_axes)
            and all(dimension_values[axis] > 0 for axis in known_axes)
        )
        if (
            not partial_source_allowed
            and min(dimension_values.values()) <= 0
        ):
            QMessageBox.warning(
                self,
                "پروفایل",
                "برای پروفایل دستی طول، عرض و ارتفاع باید بیشتر از صفر باشند. "
                "در پروفایل Source فقط محورهای factual می‌توانند ناقص بمانند.",
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
