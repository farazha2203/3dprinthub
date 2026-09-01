from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import QAbstractListModel, QModelIndex, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QImageReader, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate


STATUS_ROLE = int(Qt.ItemDataRole.UserRole) + 20

STATUS_COLORS = {
    "new": "#5DADE2",
    "working": "#F5B041",
    "published": "#27AE60",
    "rejected": "#C0392B",
    "archived": "#7F8C8D",
}


def product_lifecycle_status(row: dict[str, Any]) -> str:
    workflow = str(row.get("workflow_status") or "").strip().lower()
    if int(row.get("is_blocked") or 0) or workflow in {"blocked", "rejected"}:
        return "rejected"
    if workflow == "archived":
        return "archived"
    if (
        str(row.get("server_id") or "").strip()
        and workflow == "uploaded"
        and not int(row.get("needs_update") or 0)
    ):
        return "published"
    if (
        workflow == "review"
        and not str(row.get("server_id") or "").strip()
        and not str(row.get("title_fa") or "").strip()
    ):
        return "new"
    return "working"


def product_seo_ready(row: dict[str, Any]) -> bool:
    if not str(row.get("seo_title_fa") or "").strip():
        return False
    if not str(row.get("seo_description_fa") or "").strip():
        return False
    try:
        selected = json.loads(row.get("selected_images_json") or "[]")
    except Exception:
        selected = []
    try:
        metadata = json.loads(row.get("image_metadata_json") or "[]")
    except Exception:
        metadata = []
    if not selected:
        return False
    by_url = {
        str(item.get("source_url") or ""): item
        for item in metadata
        if isinstance(item, dict)
    }
    for url in selected:
        item = by_url.get(str(url or ""))
        if not item:
            return False
        if not item.get("metadata_ready"):
            return False
        if not str(item.get("seo_filename") or "").lower().endswith(".webp"):
            return False
    return True


class ProductStatusDelegate(QStyledItemDelegate):
    """Draw a lifecycle-colored border around every Product card."""

    def paint(self, painter: QPainter, option, index) -> None:
        super().paint(painter, option, index)
        status = str(index.data(STATUS_ROLE) or "working")
        color = QColor(STATUS_COLORS.get(status, STATUS_COLORS["working"]))
        painter.save()
        pen = QPen(color)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(option.rect.adjusted(2, 2, -2, -2), 8, 8)
        painter.restore()


class ProductGalleryModel(QAbstractListModel):
    """Folder-like Product Model/View backed by ProductCore and ImageCore."""

    SORTS = {
        "newest": lambda row: (-int(row.get("id") or 0),),
        "oldest": lambda row: (int(row.get("id") or 0),),
        "title_fa": lambda row: (str(row.get("title_fa") or "").casefold(), int(row.get("id") or 0)),
        "source_title": lambda row: (str(row.get("source_title") or "").casefold(), int(row.get("id") or 0)),
        "status": lambda row: (str(row.get("workflow_status") or "").casefold(), -int(row.get("id") or 0)),
    }

    def __init__(self, product_core, image_core, parent=None) -> None:
        super().__init__(parent)
        self.products = product_core
        self.images = image_core
        self.rows: list[dict[str, Any]] = []
        self._icons: dict[tuple[int, str], QIcon] = {}
        self._search = ""
        self._sort = "newest"
        self._filter_name = "all"
        self.refresh()

    def refresh(
        self,
        search: str | None = None,
        sort_key: str | None = None,
        filter_name: str | None = None,
    ) -> None:
        if search is not None:
            self._search = str(search or "")
        if sort_key is not None and sort_key in self.SORTS:
            self._sort = sort_key
        if filter_name is not None:
            self._filter_name = str(filter_name or "all")
        self.beginResetModel()
        rows = self.products.list(
            filter_name=self._filter_name,
            search=self._search,
        )
        rows.sort(key=self.SORTS.get(self._sort, self.SORTS["newest"]))
        self.rows = rows
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
        if role == STATUS_ROLE:
            return product_lifecycle_status(row)
        if role == Qt.ItemDataRole.DisplayRole:
            title = row.get("title_fa") or row.get("source_title") or "بدون عنوان"
            source = row.get("source_title") or ""
            lifecycle = product_lifecycle_status(row)
            status_icon = {
                "new": "🔵",
                "working": "🟠",
                "published": "🟢",
                "rejected": "🔴",
                "archived": "⚫",
            }.get(lifecycle, "🟠")
            seo = "SEO✓" if product_seo_ready(row) else "SEO…"
            if source and source != title:
                return f"{status_icon} {seo}  #{row.get('id', '')}  {title}\n{source}"
            return f"{status_icon} {seo}  #{row.get('id', '')}  {title}"
        if role == Qt.ItemDataRole.ToolTipRole:
            summary = (
                row.get("short_description_fa")
                or row.get("source_short_description")
                or row.get("description_fa")
                or ""
            )
            return (
                f"منبع: {row.get('source_name') or row.get('source_code') or '—'}\n"
                f"وضعیت: {row.get('workflow_status') or '—'}\n"
                f"چرخه: {product_lifecycle_status(row)}\n"
                f"SEO: {'نهایی' if product_seo_ready(row) else 'ناقص/درحال تکمیل'}\n"
                f"{str(summary)[:500]}"
            )
        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(285, 245)
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
                QSize(225, 165),
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
