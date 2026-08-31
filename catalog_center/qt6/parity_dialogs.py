from __future__ import annotations

from copy import deepcopy
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.epic49_desktop_schema import effective_filament_offer_price_per_gram
from app.phase49_3i35_operator_ledger import normalize_ledger_profile


def _money_spin(maximum: int = 2_000_000_000) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(0, maximum)
    spin.setGroupSeparatorShown(True)
    return spin


def _float_spin(maximum: float, decimals: int = 2, step: float = 0.1) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0, maximum)
    spin.setDecimals(decimals)
    spin.setSingleStep(step)
    return spin


def _offer_key(item: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(item.get("material") or item.get("material_name") or "").strip().casefold(),
        str(item.get("brand") or item.get("brand_name") or "").strip().casefold(),
        str(item.get("manufacturer") or item.get("manufacturer_name") or "").strip().casefold(),
        str(item.get("color") or item.get("color_name") or "").strip().casefold(),
    )


class FilamentEditorDialog(QDialog):
    """Full Phase49.3I.41 Filament editor, expressed with Qt widgets."""

    def __init__(self, row: dict[str, Any] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.row = dict(row or {})
        self.setWindowTitle("فیلامنت")
        self.resize(760, 720)

        root = QVBoxLayout(self)

        identity = QGroupBox("هویت فیلامنت")
        identity_form = QFormLayout(identity)
        self.manufacturer = QLineEdit()
        self.brand = QLineEdit()
        self.material = QLineEdit()
        self.color = QLineEdit()
        self.color_type = QComboBox()
        self.color_type.addItem("تک‌رنگ", "solid")
        self.color_type.addItem("دو‌رنگ", "dual")
        self.color_type.addItem("سه‌رنگ", "triple")
        self.hex_code = QLineEdit()
        self.secondary_hex = QLineEdit()
        self.tertiary_hex = QLineEdit()
        self.image_url = QLineEdit()

        identity_form.addRow("شرکت / Manufacturer", self.manufacturer)
        identity_form.addRow("برند", self.brand)
        identity_form.addRow("متریال", self.material)
        identity_form.addRow("رنگ", self.color)
        identity_form.addRow("نوع رنگ", self.color_type)
        identity_form.addRow("HEX اصلی", self.hex_code)
        identity_form.addRow("HEX دوم", self.secondary_hex)
        identity_form.addRow("HEX سوم", self.tertiary_hex)
        identity_form.addRow("تصویر فیلامنت", self.image_url)
        root.addWidget(identity)

        inventory = QGroupBox("موجودی و نرخ")
        grid = QGridLayout(inventory)
        self.roll_weight = _float_spin(100_000, decimals=1, step=50)
        self.stock_rolls = _float_spin(100_000, decimals=3, step=0.25)
        self.purchase_roll = _money_spin()
        self.sale_roll = _money_spin()
        self.usd_roll = _float_spin(1_000_000, decimals=2, step=1)
        self.usd_fx = _float_spin(10_000_000, decimals=2, step=100)
        self.print_hourly = _money_spin()
        self.supervision_hourly = _money_spin()
        self.preheat_hours = _float_spin(240, decimals=2, step=0.25)
        self.preheat_temp = _float_spin(500, decimals=1, step=5)
        self.preheat_hourly = _money_spin()

        labels = [
            ("وزن رول (g)", self.roll_weight),
            ("موجودی (تعداد رول)", self.stock_rolls),
            ("قیمت خرید رول (تومان)", self.purchase_roll),
            ("قیمت فروش رول (تومان)", self.sale_roll),
            ("قیمت دلاری رول", self.usd_roll),
            ("نرخ دلار صریح (تومان)", self.usd_fx),
            ("نرخ ساعتی چاپ", self.print_hourly),
            ("نرخ ساعتی نظارت", self.supervision_hourly),
            ("ساعت پیش‌گرم", self.preheat_hours),
            ("دمای پیش‌گرم °C", self.preheat_temp),
            ("نرخ ساعتی پیش‌گرم", self.preheat_hourly),
        ]
        for index, (label, widget) in enumerate(labels):
            row_index = index // 2
            col = (index % 2) * 2
            grid.addWidget(QLabel(label), row_index, col)
            grid.addWidget(widget, row_index, col + 1)

        self.rate_label = QLabel()
        self.rate_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        grid.addWidget(self.rate_label, 6, 0, 1, 4)
        root.addWidget(inventory)

        for widget in (
            self.roll_weight,
            self.sale_roll,
            self.usd_roll,
            self.usd_fx,
        ):
            widget.valueChanged.connect(self._refresh_rate)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("ذخیره فیلامنت")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._load()
        self._refresh_rate()

    def _load(self) -> None:
        row = self.row
        self.manufacturer.setText(str(row.get("manufacturer") or row.get("manufacturer_name") or ""))
        self.brand.setText(str(row.get("brand") or row.get("brand_name") or ""))
        self.material.setText(str(row.get("material") or row.get("material_name") or ""))
        self.color.setText(str(row.get("color") or row.get("color_name") or ""))
        code = str(row.get("color_type") or "solid")
        index = self.color_type.findData(code)
        self.color_type.setCurrentIndex(index if index >= 0 else 0)
        self.hex_code.setText(str(row.get("hex") or row.get("hex_code") or ""))
        self.secondary_hex.setText(str(row.get("secondary_hex") or ""))
        self.tertiary_hex.setText(str(row.get("tertiary_hex") or ""))
        self.image_url.setText(str(row.get("filament_image_url") or ""))

        self.roll_weight.setValue(float(row.get("roll_weight_grams") or 1000))
        self.stock_rolls.setValue(float(row.get("stock_roll_count") or 0))
        self.purchase_roll.setValue(int(float(row.get("purchase_price_per_roll") or 0)))
        self.sale_roll.setValue(int(float(row.get("sale_price_per_roll") or 0)))
        self.usd_roll.setValue(float(row.get("usd_price_per_roll") or 0))
        self.usd_fx.setValue(float(row.get("usd_fx_rate_toman") or 0))
        self.print_hourly.setValue(int(float(row.get("print_hourly_rate") or 0)))
        self.supervision_hourly.setValue(int(float(row.get("supervision_hourly_rate") or 0)))
        self.preheat_hours.setValue(float(row.get("preheat_hours") or 0))
        self.preheat_temp.setValue(float(row.get("preheat_temperature_c") or 0))
        self.preheat_hourly.setValue(int(float(row.get("preheat_hourly_rate") or 0)))

    def _refresh_rate(self) -> None:
        weight = max(1.0, self.roll_weight.value())
        sale = float(self.sale_roll.value())
        if sale <= 0 and self.usd_roll.value() > 0 and self.usd_fx.value() > 0:
            sale = self.usd_roll.value() * self.usd_fx.value()
        rate = sale / weight if sale > 0 else 0
        stock_kg = self.stock_rolls.value() * weight / 1000
        self.rate_label.setText(
            f"نرخ مؤثر: {rate:,.0f} تومان/گرم   •   موجودی وزنی: {stock_kg:,.3f} kg"
        )

    def _accept(self) -> None:
        if not self.material.text().strip():
            QMessageBox.warning(self, "فیلامنت", "نام متریال الزامی است.")
            return
        if not self.color.text().strip():
            QMessageBox.warning(self, "فیلامنت", "نام رنگ الزامی است.")
            return
        self.accept()

    def values(self) -> dict[str, Any]:
        return {
            "manufacturer": self.manufacturer.text().strip(),
            "brand": self.brand.text().strip(),
            "material": self.material.text().strip(),
            "color": self.color.text().strip(),
            "color_type": self.color_type.currentData(),
            "hex": self.hex_code.text().strip(),
            "secondary_hex": self.secondary_hex.text().strip(),
            "tertiary_hex": self.tertiary_hex.text().strip(),
            "filament_image_url": self.image_url.text().strip(),
            "roll_weight_grams": self.roll_weight.value(),
            "stock_roll_count": self.stock_rolls.value(),
            "purchase_price_per_roll": self.purchase_roll.value(),
            "sale_price_per_roll": self.sale_roll.value(),
            "usd_price_per_roll": self.usd_roll.value(),
            "usd_fx_rate_toman": self.usd_fx.value(),
            "print_hourly_rate": self.print_hourly.value(),
            "supervision_hourly_rate": self.supervision_hourly.value(),
            "preheat_hours": self.preheat_hours.value(),
            "preheat_temperature_c": self.preheat_temp.value(),
            "preheat_hourly_rate": self.preheat_hourly.value(),
        }


class ProfileEditorDialog(QDialog):
    """One size/profile can own many production rows and many Filament offers."""

    def __init__(
        self,
        filament_rows: list[dict[str, Any]],
        profile: dict[str, Any] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.filaments = [dict(item) for item in filament_rows]
        self.original = normalize_ledger_profile(profile or {}, 1)
        self.setWindowTitle("پروفایل تولید و قیمت")
        self.resize(1180, 850)

        root = QVBoxLayout(self)

        identity = QGroupBox("هویت سایز / پروفایل")
        form = QGridLayout(identity)
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
        root.addWidget(identity)

        production_group = QGroupBox("وزن‌های تولید همین سایز")
        production_layout = QVBoxLayout(production_group)
        self.production = QTableWidget(0, 3)
        self.production.setHorizontalHeaderLabels(
            ("وزن قطعه (g)", "وزن ساپورت (g)", "زمان چاپ (دقیقه)")
        )
        self.production.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.production.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
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
        root.addWidget(production_group)

        filament_group = QGroupBox("فیلامنت‌های قابل چاپ با این سایز")
        filament_layout = QVBoxLayout(filament_group)
        self.filament_table = QTableWidget(0, 8)
        self.filament_table.setHorizontalHeaderLabels(
            (
                "انتخاب",
                "متریال",
                "شرکت",
                "برند",
                "رنگ",
                "موجودی رول",
                "تومان/گرم",
                "قیمت قطعی همین محصول",
            )
        )
        self.filament_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        filament_layout.addWidget(self.filament_table)
        root.addWidget(filament_group, 1)

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        root.addWidget(self.summary_label)

        self.strategy.currentIndexChanged.connect(self._refresh_mode)
        self.production.itemChanged.connect(lambda _item: self._refresh_summary())

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("ثبت پروفایل")
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
        index = self.strategy.findData(str(p.get("pricing_strategy") or "dynamic"))
        self.strategy.setCurrentIndex(index if index >= 0 else 0)
        self.price_min.setValue(int(float(p.get("price_min") or 0)))
        self.price_max.setValue(int(float(p.get("price_max") or 0)))
        self.support_multiplier.setValue(float(p.get("support_cost_multiplier") or 1))
        self.assembly_fee.setValue(int(float(p.get("assembly_fee") or 0)))

        rows = [
            dict(item)
            for item in (p.get("production_rows") or [])
            if isinstance(item, dict)
        ]
        if not rows:
            rows = [{"weight_grams": 0, "support_weight_grams": 0, "print_time_minutes": 60}]
        for row in rows:
            self._add_production_row(row)

        selected_map = {
            _offer_key(item): dict(item)
            for item in (p.get("material_options") or [])
            if isinstance(item, dict)
        }
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
                Qt.CheckState.Checked if selected is not None else Qt.CheckState.Unchecked
            )
            check.setData(Qt.ItemDataRole.UserRole, deepcopy(offer))
            self.filament_table.setItem(row_index, 0, check)

            values = (
                offer.get("material") or offer.get("material_name") or "—",
                offer.get("manufacturer") or offer.get("manufacturer_name") or "—",
                offer.get("brand") or offer.get("brand_name") or "—",
                offer.get("color") or offer.get("color_name") or "—",
                f"{float(offer.get('stock_roll_count') or 0):g}",
                f"{effective_filament_offer_price_per_gram(offer):,.0f}",
            )
            for offset, value in enumerate(values, 1):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.filament_table.setItem(row_index, offset, item)

            fixed = _money_spin()
            fixed.setValue(int(float((selected or offer).get("fixed_product_price") or 0)))
            fixed.valueChanged.connect(lambda _value: self._refresh_summary())
            self.filament_table.setCellWidget(row_index, 7, fixed)

    def _add_production_row(self, data: dict[str, Any] | None = None) -> None:
        data = dict(data or {})
        row = self.production.rowCount()
        self.production.insertRow(row)
        values = (
            float(data.get("weight_grams") or 0),
            float(data.get("support_weight_grams") or 0),
            int(float(data.get("print_time_minutes") or 60)),
        )
        for col, value in enumerate(values):
            self.production.setItem(row, col, QTableWidgetItem(str(value)))

    def _remove_production_row(self) -> None:
        row = self.production.currentRow()
        if row >= 0:
            self.production.removeRow(row)
        self._refresh_summary()

    def _production_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in range(self.production.rowCount()):
            try:
                weight = float((self.production.item(row, 0).text() or "0").replace(",", ""))
                support = float((self.production.item(row, 1).text() or "0").replace(",", ""))
                minutes = int(float((self.production.item(row, 2).text() or "0").replace(",", "")))
            except Exception:
                continue
            if weight <= 0:
                continue
            rows.append({
                "weight_grams": weight,
                "support_weight_grams": max(0.0, support),
                "print_time_minutes": max(1, minutes),
            })
        return rows

    def _selected_filaments(self) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for row in range(self.filament_table.rowCount()):
            check = self.filament_table.item(row, 0)
            if check is None or check.checkState() != Qt.CheckState.Checked:
                continue
            offer = dict(check.data(Qt.ItemDataRole.UserRole) or {})
            fixed = self.filament_table.cellWidget(row, 7)
            offer["fixed_product_price"] = int(fixed.value()) if isinstance(fixed, QSpinBox) else 0
            output.append(offer)
        return output

    def _refresh_mode(self) -> None:
        mode = str(self.strategy.currentData() or "dynamic")
        self.price_min.setEnabled(mode == "range")
        self.price_max.setEnabled(mode == "range")
        for row in range(self.filament_table.rowCount()):
            widget = self.filament_table.cellWidget(row, 7)
            if widget is not None:
                widget.setEnabled(mode == "fixed")
        self._refresh_summary()

    def _refresh_summary(self) -> None:
        production_count = len(self._production_rows())
        filament_count = len(self._selected_filaments())
        combinations = production_count * filament_count
        self.summary_label.setText(
            f"این سایز: {production_count} وزن/زمان × {filament_count} فیلامنت = "
            f"{combinations} حالت تولید/قیمت"
        )

    def _accept(self) -> None:
        if not self.name.text().strip():
            QMessageBox.warning(self, "پروفایل", "نام پروفایل الزامی است.")
            return
        if not self.size_label.text().strip():
            QMessageBox.warning(self, "پروفایل", "سایز پروفایل الزامی است.")
            return
        if min(self.length.value(), self.width.value(), self.height.value()) <= 0:
            QMessageBox.warning(self, "پروفایل", "طول، عرض و ارتفاع واقعی باید بیشتر از صفر باشند.")
            return
        if not self._production_rows():
            QMessageBox.warning(self, "پروفایل", "حداقل یک وزن/زمان چاپ معتبر لازم است.")
            return
        if not self._selected_filaments():
            QMessageBox.warning(self, "پروفایل", "حداقل یک فیلامنت برای این سایز انتخاب کن.")
            return
        if self.strategy.currentData() == "fixed":
            missing = [
                row
                for row in range(self.filament_table.rowCount())
                if self.filament_table.item(row, 0)
                and self.filament_table.item(row, 0).checkState() == Qt.CheckState.Checked
                and isinstance(self.filament_table.cellWidget(row, 7), QSpinBox)
                and self.filament_table.cellWidget(row, 7).value() <= 0
            ]
            if missing:
                QMessageBox.warning(
                    self,
                    "پروفایل",
                    "در حالت قیمت قطعی، برای همه فیلامنت‌های انتخابی قیمت همین محصول را وارد کن.",
                )
                return
        self.accept()

    def values(self) -> dict[str, Any]:
        result = dict(self.original)
        result.update({
            "name": self.name.text().strip(),
            "size_label": self.size_label.text().strip(),
            "part_length_cm": self.length.value(),
            "part_width_cm": self.width.value(),
            "part_height_cm": self.height.value(),
            "production_rows": self._production_rows(),
            "material_options": self._selected_filaments(),
            "pricing_strategy": str(self.strategy.currentData() or "dynamic"),
            "price_min": self.price_min.value(),
            "price_max": self.price_max.value(),
            "support_cost_multiplier": self.support_multiplier.value(),
            "assembly_fee": self.assembly_fee.value(),
        })
        return normalize_ledger_profile(result, 1)
