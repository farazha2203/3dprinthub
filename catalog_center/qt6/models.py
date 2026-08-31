from __future__ import annotations

import re
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt

from app.epic49_desktop_schema import (
    effective_filament_offer_price_per_gram,
    list_available_material_colors,
    normalize_material_color_options,
)

SORT_ROLE = int(Qt.ItemDataRole.UserRole) + 1


def filament_stock_grams(row: dict[str, Any]) -> float:
    try:
        return max(0.0, float(row.get("stock_roll_count") or 0)) * max(
            1.0, float(row.get("roll_weight_grams") or 1000)
        )
    except Exception:
        return 0.0


def _summary(row: dict[str, Any]) -> str:
    for key in (
        "short_description_fa",
        "source_short_description",
        "description_fa",
        "source_description",
    ):
        text = re.sub(r"\s+", " ", str(row.get(key) or "")).strip()
        if text:
            return text[:220]
    return ""


class ProductTableModel(QAbstractTableModel):
    headers = (
        "ID",
        "عنوان فارسی",
        "عنوان اصلی / انگلیسی",
        "توضیح",
        "منبع",
        "وضعیت",
        "انتشار",
        "خطا",
    )

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

    def _values(self, row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            int(row.get("id") or 0),
            row.get("title_fa") or "",
            row.get("source_title") or "",
            _summary(row),
            row.get("source_name") or row.get("source_code") or "—",
            row.get("workflow_status") or "—",
            "بله" if row.get("server_id") else "خیر",
            row.get("product_sync_error") or "",
        )

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.rows)):
            return None
        row = self.rows[index.row()]
        if role == Qt.ItemDataRole.UserRole:
            return row
        values = self._values(row)
        if role == SORT_ROLE:
            return values[index.column()]
        if role == Qt.ItemDataRole.ToolTipRole and index.column() == 3:
            return str(row.get("description_fa") or row.get("source_description") or "")
        if role != Qt.ItemDataRole.DisplayRole:
            return None
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
        "متریال",
        "شرکت",
        "برند",
        "رنگ",
        "وزن رول",
        "موجودی kg",
        "فروش رول",
        "تومان/گرم",
        "پیش‌گرم",
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
                item["id"] = int(raw["id"])
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

    def _values(self, row: dict[str, Any]) -> tuple[Any, ...]:
        rate_per_gram = effective_filament_offer_price_per_gram(row)
        hours = float(row.get("preheat_hours") or 0)
        temp = float(row.get("preheat_temperature_c") or 0)
        preheat = "—" if hours <= 0 else f"{hours:g}h / {temp:g}°C"
        return (
            row.get("material") or "—",
            row.get("manufacturer") or "—",
            row.get("brand") or "—",
            row.get("color") or "—",
            f"{float(row.get('roll_weight_grams') or 0):g} g",
            f"{filament_stock_grams(row) / 1000:g}",
            f"{int(float(row.get('sale_price_per_roll') or 0)):,}",
            f"{float(rate_per_gram):,.0f}",
            preheat,
        )

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.rows)):
            return None
        row = self.rows[index.row()]
        if role == Qt.ItemDataRole.UserRole:
            return row
        values = self._values(row)
        if role == SORT_ROLE:
            if index.column() in {4, 5, 6, 7}:
                numeric = (
                    float(row.get("roll_weight_grams") or 0),
                    filament_stock_grams(row) / 1000,
                    float(row.get("sale_price_per_roll") or 0),
                    float(effective_filament_offer_price_per_gram(row)),
                )
                return numeric[{4: 0, 5: 1, 6: 2, 7: 3}[index.column()]]
            return values[index.column()]
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        return str(values[index.column()])

    def materials(self) -> list[str]:
        return sorted(
            {
                str(row.get("material") or "").strip()
                for row in self.rows
                if row.get("material")
            },
            key=str.casefold,
        )

    def row_at(self, row_index: int) -> dict[str, Any] | None:
        if 0 <= row_index < len(self.rows):
            return dict(self.rows[row_index])
        return None


class FilamentFilterProxyModel(QSortFilterProxyModel):
    """Filter by material plus free text across material/manufacturer/brand/color."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.material = ""
        self.query = ""
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortRole(SORT_ROLE)

    def set_material(self, value: str) -> None:
        self.material = str(value or "").strip().casefold()
        self.invalidateFilter()

    def set_query(self, value: str) -> None:
        self.query = str(value or "").strip().casefold()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        source = self.sourceModel()
        if source is None or not hasattr(source, "rows"):
            return True
        try:
            row = source.rows[source_row]
        except Exception:
            return False
        if self.material and str(row.get("material") or "").strip().casefold() != self.material:
            return False
        if not self.query:
            return True
        haystack = " ".join(
            str(row.get(key) or "")
            for key in ("material", "manufacturer", "brand", "color")
        ).casefold()
        return all(token in haystack for token in self.query.split() if token)
