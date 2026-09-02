from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def human_bytes(value: int) -> str:
    size = max(0, int(value or 0))
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.2f} MB"


class ImageCard(QFrame):
    deleteRequested = Signal(str)
    seoRequested = Signal(str)
    selectionChanged = Signal()
    primaryChanged = Signal(str)
    sliderChanged = Signal(str)

    def __init__(self, item: dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self.item = dict(item)
        self.setObjectName("ImageCard")
        self.setMinimumWidth(300)
        self.setMaximumWidth(380)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(250, 190)
        self.preview.setMaximumHeight(235)
        path = str(self.item.get("path") or "")
        pixmap = QPixmap(path) if path else QPixmap()
        if pixmap.isNull():
            self.preview.setText("⚠ تصویر محلی دریافت نشده")
            self.preview.setObjectName("MissingImage")
        else:
            self.preview.setPixmap(
                pixmap.scaled(
                    330,
                    225,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        root.addWidget(self.preview)

        top = QHBoxLayout()
        self.selected = QCheckBox("انتخاب")
        self.selected.setChecked(bool(self.item.get("selected")))
        self.primary = QRadioButton("اصلی")
        self.primary.setAutoExclusive(False)
        self.primary.setChecked(bool(self.item.get("primary")))
        self.slider = QRadioButton("اسلایدر")
        self.slider.setAutoExclusive(False)
        self.slider.setChecked(bool(self.item.get("slider")))
        top.addWidget(self.selected)
        top.addWidget(self.primary)
        top.addWidget(self.slider)
        root.addLayout(top)

        filename = str(self.item.get("filename") or "")
        if not filename:
            filename = str(self.item.get("url") or "").rsplit("/", 1)[-1][:55]
        self.filename = QLabel(filename or "بدون نام فایل")
        self.filename.setWordWrap(True)
        self.filename.setToolTip(str(self.item.get("url") or ""))
        root.addWidget(self.filename)

        width = int(self.item.get("width") or 0)
        height = int(self.item.get("height") or 0)
        downloaded = bool(self.item.get("downloaded"))
        facts = (
            f"{width}×{height} px • {human_bytes(int(self.item.get('bytes') or 0))}"
            if downloaded
            else "فایل محلی: موجود نیست"
        )
        self.facts = QLabel(facts)
        self.facts.setObjectName("Muted")
        root.addWidget(self.facts)

        alt = str(self.item.get("alt_text") or "").strip()
        self.alt = QLabel(f"Alt: {alt or '—'}")
        self.alt.setWordWrap(True)
        self.alt.setObjectName("Muted")
        root.addWidget(self.alt)

        actions = QHBoxLayout()
        seo = QPushButton("SEO")
        delete = QPushButton("حذف")
        seo.clicked.connect(
            lambda: self.seoRequested.emit(str(self.item.get("url") or ""))
        )
        delete.clicked.connect(
            lambda: self.deleteRequested.emit(str(self.item.get("url") or ""))
        )
        actions.addWidget(seo)
        actions.addWidget(delete)
        actions.addStretch(1)
        root.addLayout(actions)

        # QCheckBox.toggled emits bool, while the gallery contract is a
        # zero-argument semantic notification. Consume the Qt payload here.
        self.selected.toggled.connect(
            lambda _checked=False: self.selectionChanged.emit()
        )
        self.primary.toggled.connect(
            lambda checked: (
                self.primaryChanged.emit(str(self.item.get("url") or ""))
                if checked
                else None
            )
        )
        self.slider.toggled.connect(
            lambda checked: (
                self.sliderChanged.emit(str(self.item.get("url") or ""))
                if checked
                else None
            )
        )


class ProductImageGrid(QWidget):
    """Old-style visual gallery: four columns, rows continue until images end."""

    deleteRequested = Signal(str)
    seoRequested = Signal(str)
    primaryChanged = Signal(str)
    sliderChanged = Signal(str)
    selectionChanged = Signal()

    def __init__(self, parent=None, *, columns: int = 4) -> None:
        super().__init__(parent)
        self.columns = max(3, min(4, int(columns)))
        self.cards: list[ImageCard] = []
        self._primary_sync = False
        self._slider_sync = False
        self._missing_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.summary = QLabel("0 تصویر")
        self.summary.setObjectName("Muted")
        root.addWidget(self.summary)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.host = QWidget()
        self.grid = QGridLayout(self.host)
        self.grid.setContentsMargins(2, 2, 2, 2)
        self.grid.setSpacing(10)
        self.scroll.setWidget(self.host)
        root.addWidget(self.scroll, 1)

    def clear(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.cards.clear()
        self.summary.setText("0 تصویر")

    def set_items(self, items: list[dict[str, Any]]) -> None:
        self.clear()
        missing = 0
        for index, raw in enumerate(items or []):
            item = dict(raw)
            if not item.get("downloaded"):
                missing += 1
            card = ImageCard(item, self.host)
            card.deleteRequested.connect(self.deleteRequested.emit)
            card.seoRequested.connect(self.seoRequested.emit)
            card.selectionChanged.connect(self._selection_changed)
            card.primaryChanged.connect(self._primary_changed)
            card.sliderChanged.connect(self._slider_changed)
            self.cards.append(card)
            self.grid.addWidget(
                card,
                index // self.columns,
                index % self.columns,
                alignment=Qt.AlignmentFlag.AlignTop,
            )
        for column in range(self.columns):
            self.grid.setColumnStretch(column, 1)
        self.grid.setRowStretch(
            max(0, (len(self.cards) + self.columns - 1) // self.columns),
            1,
        )
        self._missing_count = missing
        self._update_summary()

    def _selection_changed(self) -> None:
        self._update_summary()
        self.selectionChanged.emit()

    def _update_summary(self) -> None:
        selected = sum(1 for card in self.cards if card.selected.isChecked())
        self.summary.setText(
            f"{len(self.cards)} تصویر • {selected} انتخاب‌شده • "
            f"{self._missing_count} تصویر بدون فایل محلی"
        )

    def _primary_changed(self, url: str) -> None:
        if self._primary_sync:
            return
        self._primary_sync = True
        try:
            for card in self.cards:
                if str(card.item.get("url") or "") != url:
                    card.primary.setChecked(False)
            self.primaryChanged.emit(url)
        finally:
            self._primary_sync = False

    def _slider_changed(self, url: str) -> None:
        if self._slider_sync:
            return
        self._slider_sync = True
        try:
            for card in self.cards:
                if str(card.item.get("url") or "") != url:
                    card.slider.setChecked(False)
            self.sliderChanged.emit(url)
        finally:
            self._slider_sync = False

    def selected_urls(self) -> list[str]:
        return [
            str(card.item.get("url") or "")
            for card in self.cards
            if card.selected.isChecked()
        ]

    def primary_url(self) -> str:
        for card in self.cards:
            if card.primary.isChecked():
                return str(card.item.get("url") or "")
        return ""

    def slider_url(self) -> str:
        for card in self.cards:
            if card.slider.isChecked():
                return str(card.item.get("url") or "")
        return ""

    def set_all_selected(self, checked: bool) -> None:
        for card in self.cards:
            card.selected.setChecked(bool(checked))

    def item_for_url(self, url: str) -> dict[str, Any] | None:
        for card in self.cards:
            if str(card.item.get("url") or "") == str(url or ""):
                return dict(card.item)
        return None


class ImageSeoDialog(QDialog):
    """Single/bulk operator SEO editor for selected image metadata."""

    def __init__(
        self,
        items: list[dict[str, Any]],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.items = [dict(item) for item in items or []]
        self.bulk = len(self.items) > 1
        self.setWindowTitle(
            "ویرایش گروهی SEO تصاویر"
            if self.bulk
            else "ویرایش SEO تصویر"
        )
        self.resize(760, 620)

        root = QVBoxLayout(self)
        info = QLabel(
            f"{len(self.items)} تصویر انتخاب شده. "
            + (
                "فقط فیلدهایی که «اعمال» دارند روی همه تصاویر نوشته می‌شوند."
                if self.bulk
                else "Metadata این تصویر را دقیق ویرایش کن."
            )
        )
        info.setWordWrap(True)
        info.setObjectName("Muted")
        root.addWidget(info)

        form = QFormLayout()
        first = self.items[0] if self.items else {}

        self.alt_apply = QCheckBox("اعمال")
        self.alt_apply.setChecked(True)
        self.alt = QLineEdit(str(first.get("alt_text") or "") if not self.bulk else "")
        form.addRow(self.alt_apply, self.alt)

        self.title_apply = QCheckBox("اعمال")
        self.title_apply.setChecked(True)
        self.title = QLineEdit(str(first.get("seo_title") or "") if not self.bulk else "")
        form.addRow(self.title_apply, self.title)

        self.caption_apply = QCheckBox("اعمال")
        self.caption_apply.setChecked(True)
        self.caption = QPlainTextEdit(
            str(first.get("caption") or "") if not self.bulk else ""
        )
        self.caption.setMaximumHeight(120)
        form.addRow(self.caption_apply, self.caption)

        self.keywords_apply = QCheckBox("اعمال")
        self.keywords_apply.setChecked(True)
        self.keywords = QPlainTextEdit(
            "\n".join(str(x) for x in (first.get("keywords") or []))
            if not self.bulk
            else ""
        )
        self.keywords.setMaximumHeight(120)
        form.addRow(self.keywords_apply, self.keywords)

        self.filename_apply = QCheckBox("اعمال نام فایل SEO")
        self.filename_apply.setChecked(not self.bulk)
        self.filename_apply.setEnabled(not self.bulk)
        self.filename = QLineEdit(
            str(first.get("planned_filename") or "") if not self.bulk else ""
        )
        self.filename.setEnabled(not self.bulk)
        form.addRow(self.filename_apply, self.filename)

        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("ذخیره SEO")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("انصراف")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        output: dict[str, Any] = {}
        if self.alt_apply.isChecked():
            output["alt_text"] = self.alt.text().strip()
        if self.title_apply.isChecked():
            output["title"] = self.title.text().strip()
        if self.caption_apply.isChecked():
            output["caption"] = self.caption.toPlainText().strip()
        if self.keywords_apply.isChecked():
            output["keywords"] = [
                token.strip().lstrip("#")
                for token in self.keywords.toPlainText().replace(",", "\n").splitlines()
                if token.strip()
            ]
        if self.filename_apply.isChecked() and not self.bulk:
            output["seo_filename"] = self.filename.text().strip()
        return output
