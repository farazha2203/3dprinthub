from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractListModel, QModelIndex, QSize, Qt
from PySide6.QtGui import QIcon, QImageReader, QPixmap


class ProductGalleryModel(QAbstractListModel):
    """Folder-like Product Model/View backed by ProductCore and ImageCore."""

    def __init__(self, product_core, image_core, parent=None) -> None:
        super().__init__(parent)
        self.products = product_core
        self.images = image_core
        self.rows: list[dict[str, Any]] = []
        self._icons: dict[tuple[int, str], QIcon] = {}
        self.refresh()

    def refresh(self, search: str = "") -> None:
        self.beginResetModel()
        self.rows = self.products.list(search=search)
        self._icons.clear()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.rows)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.rows)):
            return None
        row = self.rows[index.row()]

        if role == Qt.ItemDataRole.UserRole:
            return row
        if role == Qt.ItemDataRole.DisplayRole:
            title = row.get("title_fa") or row.get("source_title") or "بدون عنوان"
            return f"#{row.get('id', '')}  {title}"
        if role == Qt.ItemDataRole.ToolTipRole:
            return (
                f"منبع: {row.get('source_name') or row.get('source_code') or '—'}\n"
                f"وضعیت: {row.get('workflow_status') or '—'}"
            )
        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(270, 230)
        if role == Qt.ItemDataRole.DecorationRole:
            return self._icon_for_row(row)
        return None

    def _icon_for_row(self, row: dict[str, Any]) -> QIcon:
        product_id = int(row.get("id") or 0)
        path = self.images.preferred_local_path(row)
        key = (product_id, path)
        cached = self._icons.get(key)
        if cached is not None:
            return cached

        if not path:
            icon = QIcon.fromTheme("image-x-generic")
            self._icons[key] = icon
            return icon

        reader = QImageReader(path)
        reader.setAutoTransform(True)
        original = reader.size()
        if original.isValid():
            original.scale(
                QSize(220, 160),
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            reader.setScaledSize(original)
        image = reader.read()
        if image.isNull():
            icon = QIcon.fromTheme("image-x-generic")
        else:
            icon = QIcon(QPixmap.fromImage(image))
        self._icons[key] = icon
        return icon

    def product_id_at(self, row_index: int) -> int | None:
        if 0 <= row_index < len(self.rows):
            try:
                return int(self.rows[row_index]["id"])
            except Exception:
                return None
        return None
