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
    """Incremental Product table: 20 rows first, then fetch-on-scroll."""

    PAGE_SIZE = 20
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
    SORT_COLUMNS = {
        0: "id",
        1: "title_fa",
        2: "source_title",
        4: "source_name",
        5: "workflow_status",
        6: "server_id",
        7: "product_sync_error",
    }

    def __init__(self, db) -> None:
        super().__init__()
        self.db = db
        self.rows: list[dict[str, Any]] = []
        self._search = ""
        self._filter_name = "all"
        self._sort_column = 0
        self._sort_order = Qt.SortOrder.DescendingOrder
        self.total_count = 0
        self.refresh()

    @property
    def loaded_count(self) -> int:
        return len(self.rows)

    def _sort_request(self) -> tuple[str, bool]:
        column = self.SORT_COLUMNS.get(self._sort_column, "id")
        return (
            f"column:{column}",
            self._sort_order == Qt.SortOrder.DescendingOrder,
        )

    def refresh(
        self,
        search: str | None = None,
        filter_name: str | None = None,
    ) -> None:
        if search is not None:
            self._search = str(search or "")
        if filter_name is not None:
            self._filter_name = str(filter_name or "all")
        sort_key, descending = self._sort_request()
        self.beginResetModel()
        self.total_count = int(
            self.db.product_count(
                filter_name=self._filter_name,
                search=self._search,
            )
        )
        self.rows = [
            dict(row)
            for row in self.db.product_page(
                filter_name=self._filter_name,
                search=self._search,
                sort_key=sort_key,
                descending=descending,
                limit=self.PAGE_SIZE,
                offset=0,
            )
        ]
        self.endResetModel()

    def canFetchMore(self, parent=QModelIndex()) -> bool:  # noqa: N802
        return not parent.isValid() and len(self.rows) < self.total_count

    def fetchMore(self, parent=QModelIndex()) -> None:  # noqa: N802
        if parent.isValid() or not self.canFetchMore(parent):
            return
        sort_key, descending = self._sort_request()
        page = [
            dict(row)
            for row in self.db.product_page(
                filter_name=self._filter_name,
                search=self._search,
                sort_key=sort_key,
                descending=descending,
                limit=self.PAGE_SIZE,
                offset=len(self.rows),
            )
        ]
        if not page:
            self.total_count = len(self.rows)
            return
        first = len(self.rows)
        last = first + len(page) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        self.rows.extend(page)
        self.endInsertRows()

    def sort(self, column: int, order=Qt.SortOrder.AscendingOrder) -> None:  # noqa: N802
        if not (0 <= int(column) < len(self.headers)):
            return
        self._sort_column = int(column)
        self._sort_order = order
        self.refresh()

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
            (
                "منتشرشده"
                if (
                    str(row.get("server_id") or "").strip()
                    and str(row.get("workflow_status") or "").strip().lower() == "uploaded"
                    and not int(row.get("needs_update") or 0)
                )
                else ("آماده انتشار" if int(row.get("upload_ready") or 0) else "—")
            ),
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
        "برند",
        "رنگ / Finish",
        "رفتار رنگ",
        "وزن رول",
        "موجودی kg",
        "قیمت خرید رول",
        "قیمت فروش رول",
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
                str(item.get("brand") or "").casefold(),
                str(item.get("color") or "").casefold(),
                str(item.get("color_finish") or "").casefold(),
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
        color_label = str(row.get("color") or "—")
        finish = str(row.get("color_finish") or "matte")
        behavior = str(row.get("color_type") or "solid")
        return (
            row.get("material") or "—",
            row.get("brand") or "—",
            f"{color_label} / {finish}",
            behavior,
            f"{float(row.get('roll_weight_grams') or 0):g} g",
            f"{filament_stock_grams(row) / 1000:g}",
            f"{int(float(row.get('purchase_price_per_roll') or 0)):,}",
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
            if index.column() in {4, 5, 6, 7, 8}:
                numeric = (
                    float(row.get("roll_weight_grams") or 0),
                    filament_stock_grams(row) / 1000,
                    float(row.get("purchase_price_per_roll") or 0),
                    float(row.get("sale_price_per_roll") or 0),
                    float(effective_filament_offer_price_per_gram(row)),
                )
                return numeric[{4: 0, 5: 1, 6: 2, 7: 3, 8: 4}[index.column()]]
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
    """Filter by material plus free text across brand/color/finish."""

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
            for key in (
                "material",
                "brand",
                "color",
                "color_type",
                "color_finish",
            )
        ).casefold()
        return all(token in haystack for token in self.query.split() if token)
