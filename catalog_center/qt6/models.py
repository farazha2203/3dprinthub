from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from app.epic49_desktop_schema import (
    list_available_material_colors,
    normalize_material_color_options,
)
from app.phase49_3i39_professional_commerce import offer_stock_grams
from app.phase49_3i40_commerce_precision import filament_rate_calculation


class ProductTableModel(QAbstractTableModel):
    headers = ("ID", "عنوان", "منبع", "وضعیت", "انتشار", "خطا")

    def __init__(self, db) -> None:
        super().__init__()
        self.db = db
        self.rows: list[dict[str, Any]] = []
        self.refresh()

    def refresh(self, search: str = "") -> None:
        self.beginResetModel()
        self.rows = [dict(row) for row in self.db.products(search=search)]
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.headers):
            return self.headers[section]
        return section + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.rows)):
            return None
        row = self.rows[index.row()]
        if role == Qt.ItemDataRole.UserRole:
            return row
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        values = (
            row.get("id", ""),
            row.get("title_fa") or row.get("source_title") or "بدون عنوان",
            row.get("source_name") or row.get("source_code") or "—",
            row.get("workflow_status") or "—",
            "بله" if row.get("server_id") else "خیر",
            row.get("product_sync_error") or "",
        )
        return str(values[index.column()])

    def product_id_at(self, row_index: int) -> int | None:
        if 0 <= row_index < len(self.rows):
            try:
                return int(self.rows[row_index]["id"])
            except Exception:
                return None
        return None


class FilamentTableModel(QAbstractTableModel):
    headers = (
        "متریال", "شرکت", "برند", "رنگ", "وزن رول",
        "موجودی kg", "فروش رول", "تومان/گرم", "پیش‌گرم",
    )

    def __init__(self, db) -> None:
        super().__init__()
        self.db = db
        self.rows: list[dict[str, Any]] = []
        self.refresh()

    def refresh(self) -> None:
        items: list[dict[str, Any]] = []
        for raw in list_available_material_colors(self.db):
            normalized = normalize_material_color_options([dict(raw)])
            if normalized:
                item = dict(normalized[0])
                item["_row_id"] = int(raw["id"])
                items.append(item)
        items.sort(
            key=lambda item: (
                str(item.get("material") or "").casefold(),
                str(item.get("manufacturer") or "").casefold(),
                str(item.get("brand") or "").casefold(),
                str(item.get("color") or "").casefold(),
            )
        )
        self.beginResetModel()
        self.rows = items
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.headers)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(self.headers):
            return self.headers[section]
        return section + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.rows)):
            return None
        row = self.rows[index.row()]
        if role == Qt.ItemDataRole.UserRole:
            return row
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        rate = filament_rate_calculation(row)
        hours = float(row.get("preheat_hours") or 0)
        temp = float(row.get("preheat_temperature_c") or 0)
        preheat = "—" if hours <= 0 else f"{hours:g}h / {temp:g}°C"
        values = (
            row.get("material") or "—",
            row.get("manufacturer") or "—",
            row.get("brand") or "—",
            row.get("color") or "—",
            f"{float(row.get('roll_weight_grams') or 0):g} g",
            f"{offer_stock_grams(row) / 1000:g}",
            f"{int(float(row.get('sale_price_per_roll') or 0)):,}",
            f"{float(rate['rate_per_gram']):,.0f}",
            preheat,
        )
        return str(values[index.column()])

    def materials(self) -> list[str]:
        return sorted(
            {str(row.get("material") or "").strip() for row in self.rows if row.get("material")},
            key=str.casefold,
        )
