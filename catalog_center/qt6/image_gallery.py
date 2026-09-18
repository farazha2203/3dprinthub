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
    QSizePolicy,
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


class ClickableImageLabel(QLabel):
    clicked = Signal()
    wheelRequested = Signal(int)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def wheelEvent(self, event) -> None:
        delta = int(event.pixelDelta().y() or event.angleDelta().y())
        if delta:
            self.wheelRequested.emit(delta)
            event.accept()
            return
        event.ignore()


class ImageCard(QFrame):
    deleteRequested = Signal(str)
    seoRequested = Signal(str)
    moveEarlierRequested = Signal(str)
    moveLaterRequested = Signal(str)
    selectionChanged = Signal()
    operationSelectionChanged = Signal()
    scrollRequested = Signal(int)
    primaryChanged = Signal(str)
    sliderChanged = Signal(str)

    def __init__(
        self,
        item: dict[str, Any],
        parent=None,
        *,
        large: bool = False,
    ) -> None:
        super().__init__(parent)
        self.item = dict(item)
        self.large = bool(large)
        self.setObjectName("ImageCard")
        self.setMinimumWidth(300 if self.large else 220)
        self.setMaximumWidth(520 if self.large else 300)
        self.setMinimumHeight(206 if self.large else 405)
        self.setMaximumHeight(206 if self.large else 16777215)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(4 if self.large else 6, 4 if self.large else 6, 4 if self.large else 6, 4 if self.large else 6)
        root.setSpacing(2 if self.large else 4)

        self.preview = ClickableImageLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.large:
            self.preview.setMinimumSize(260, 90)
            self.preview.setMaximumHeight(94)
        else:
            self.preview.setMinimumSize(190, 145)
            self.preview.setMaximumHeight(180)
        path = str(self.item.get("path") or "")
        pixmap = QPixmap(path) if path else QPixmap()
        if pixmap.isNull():
            self.preview.setText("⚠ تصویر محلی دریافت نشده")
            self.preview.setObjectName("MissingImage")
        else:
            preview_width, preview_height = (
                (420, 92) if self.large else (255, 170)
            )
            self.preview.setPixmap(
                pixmap.scaled(
                    preview_width,
                    preview_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        root.addWidget(self.preview)

        self.options_label = QLabel("\u06af\u0632\u06cc\u0646\u0647\u200c\u0647\u0627\u06cc \u062a\u0635\u0648\u06cc\u0631")
        self.options_label.setStyleSheet("font-size: 9px; font-weight: 700;")
        self.options_label.setVisible(not self.large)
        if not self.large:
            root.addWidget(self.options_label)

        top = QHBoxLayout()
        top.setSpacing(6)
        self.bulk_selected = QCheckBox("انتخاب")
        self.bulk_selected.setChecked(False)
        self.selected = QCheckBox("در سایت")
        self.selected.setChecked(bool(self.item.get("selected")))
        self.primary = QRadioButton("اصلی")
        self.primary.setAutoExclusive(False)
        self.primary.setChecked(bool(self.item.get("primary")))
        self.slider = QRadioButton("اسلایدر")
        self.slider.setAutoExclusive(False)
        self.slider.setChecked(bool(self.item.get("slider")))
        for control in (self.bulk_selected, self.selected, self.primary, self.slider):
            font = control.font()
            font.setPointSize(7 if self.large else 9)
            control.setFont(font)
            if self.large:
                control.setMaximumHeight(20)
        top.addWidget(self.bulk_selected)
        top.addWidget(self.selected)
        top.addWidget(self.primary)
        top.addWidget(self.slider)
        top.addStretch(1)
        root.addLayout(top)

        source_filename = str(self.item.get("filename") or "")
        if not source_filename:
            source_filename = str(self.item.get("url") or "").rsplit("/", 1)[-1][:55]
        seo_filename = str(self.item.get("planned_filename") or "").strip()
        self.filename = QLabel(seo_filename or source_filename or "بدون نام SEO")
        self.filename.setWordWrap(False)
        self.filename.setToolTip(
            f"نام SEO: {seo_filename or '—'}\nفایل منبع: {source_filename or '—'}"
        )
        seo_font = self.filename.font()
        seo_font.setPointSize(8 if self.large else 10)
        seo_font.setBold(True)
        self.filename.setFont(seo_font)
        root.addWidget(self.filename)

        self.source_filename = QLabel(f"فایل منبع: {source_filename or '—'}")
        self.source_filename.setObjectName("Muted")
        self.source_filename.setWordWrap(False)
        self.source_filename.setToolTip(source_filename)
        source_font = self.source_filename.font()
        source_font.setPointSize(7 if self.large else 8)
        self.source_filename.setFont(source_font)
        if not self.large:
            root.addWidget(self.source_filename)

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
        facts_font = self.facts.font()
        facts_font.setPointSize(7 if self.large else facts_font.pointSize())
        self.facts.setFont(facts_font)
        if not self.large:
            root.addWidget(self.facts)

        alt = str(self.item.get("alt_text") or "").strip()
        self.alt = QLabel(f"Alt: {alt or '—'}")
        self.alt.setWordWrap(False)
        self.alt.setToolTip(alt)
        self.alt.setObjectName("Muted")
        alt_font = self.alt.font()
        alt_font.setPointSize(7 if self.large else alt_font.pointSize())
        self.alt.setFont(alt_font)
        if self.large:
            meta = QHBoxLayout()
            meta.setSpacing(6)
            meta.addWidget(self.source_filename, 2)
            meta.addWidget(self.facts, 1)
            self.alt.setVisible(False)
            root.addLayout(meta)
        else:
            root.addWidget(self.alt)

        order_actions = QHBoxLayout()
        self.move_earlier = QPushButton("قبلی")
        self.move_later = QPushButton("بعدی")
        self.move_earlier.setToolTip("این تصویر را یک جایگاه زودتر قرار بده")
        self.move_later.setToolTip("این تصویر را یک جایگاه دیرتر قرار بده")
        self.move_earlier.clicked.connect(
            lambda: self.moveEarlierRequested.emit(str(self.item.get("url") or ""))
        )
        self.move_later.clicked.connect(
            lambda: self.moveLaterRequested.emit(str(self.item.get("url") or ""))
        )
        if not self.large:
            order_actions.addWidget(self.move_earlier)
            order_actions.addWidget(self.move_later)
            order_actions.addStretch(1)
            root.addLayout(order_actions)

        actions = QHBoxLayout()
        seo = QPushButton("SEO")
        delete = QPushButton("حذف")
        seo.clicked.connect(
            lambda: self.seoRequested.emit(str(self.item.get("url") or ""))
        )
        delete.clicked.connect(
            lambda: self.deleteRequested.emit(str(self.item.get("url") or ""))
        )
        for button in (self.move_earlier, self.move_later, seo, delete):
            font = button.font()
            font.setPointSize(7 if self.large else 9)
            button.setFont(font)
            button.setMaximumHeight(22 if self.large else 28)
        if self.large:
            actions.addWidget(self.move_earlier)
            actions.addWidget(self.move_later)
        actions.addWidget(seo)
        actions.addWidget(delete)
        actions.addStretch(1)
        root.addLayout(actions)

        self.preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.preview.setToolTip(
            "برای انتخاب/لغو انتخاب این تصویر در عملیات گروهی کلیک کن؛ "
            "اسکرول ماوس روی خود عکس هم گالری را حرکت می‌دهد."
        )
        self.preview.clicked.connect(self._toggle_operation_selection)
        self.preview.wheelRequested.connect(self.scrollRequested.emit)

        if bool(self.item.get("display_only")):
            self.bulk_selected.setEnabled(False)
            self.selected.setEnabled(False)
            self.primary.setEnabled(False)
            self.slider.setEnabled(False)
            self.move_earlier.setEnabled(False)
            self.move_later.setEnabled(False)
            seo.setEnabled(False)
            delete.setEnabled(False)

        # QCheckBox.toggled emits bool, while the gallery contract is a
        # zero-argument semantic notification. Consume the Qt payload here.
        self.bulk_selected.toggled.connect(
            lambda _checked=False: self.operationSelectionChanged.emit()
        )
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

    def _toggle_operation_selection(self) -> None:
        if self.bulk_selected.isEnabled():
            self.bulk_selected.toggle()


class ProductImageGrid(QWidget):
    """Scrollable Product gallery with configurable large review cards."""

    deleteRequested = Signal(str)
    seoRequested = Signal(str)
    moveEarlierRequested = Signal(str)
    moveLaterRequested = Signal(str)
    primaryChanged = Signal(str)
    sliderChanged = Signal(str)
    selectionChanged = Signal()
    operationSelectionChanged = Signal()

    def __init__(
        self,
        parent=None,
        *,
        columns: int = 4,
        large_cards: bool = False,
    ) -> None:
        super().__init__(parent)
        self.columns = max(2, min(4, int(columns)))
        self.large_cards = bool(large_cards)
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
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
            if self.large_cards
            else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.host = QWidget()
        self.host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.grid = QGridLayout(self.host)
        self.grid.setContentsMargins(4, 4, 10, 12)
        self.grid.setSpacing(6 if self.large_cards else 12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.host)
        self.scroll.verticalScrollBar().setFixedWidth(18)
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
            card = ImageCard(
                item,
                self.host,
                large=self.large_cards,
            )
            card.deleteRequested.connect(self.deleteRequested.emit)
            card.seoRequested.connect(self.seoRequested.emit)
            card.moveEarlierRequested.connect(self.moveEarlierRequested.emit)
            card.moveLaterRequested.connect(self.moveLaterRequested.emit)
            card.selectionChanged.connect(self._selection_changed)
            card.operationSelectionChanged.connect(self._operation_selection_changed)
            card.scrollRequested.connect(self._scroll_requested)
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
        rows = max(1, (len(self.cards) + self.columns - 1) // self.columns)
        # Stage-3 must retain enough scrollable canvas for four review rows,
        # even when a Product currently has fewer (or zero) images. This keeps
        # lower-row filename/actions reachable and avoids a dead-end viewport.
        minimum_rows = 4 if self.large_cards else 1
        scroll_rows = max(rows, minimum_rows)
        card_height = 206 if self.large_cards else 430
        self.host.setMinimumHeight(
            scroll_rows * card_height
            + max(0, scroll_rows - 1) * self.grid.spacing()
        )
        self._missing_count = missing
        self._update_summary()
        self._refresh_move_controls()

    def _selection_changed(self) -> None:
        self._update_summary()
        self._refresh_move_controls()
        self.selectionChanged.emit()

    def _operation_selection_changed(self) -> None:
        self._update_summary()
        self.operationSelectionChanged.emit()

    def _scroll_requested(self, delta: int) -> None:
        bar = self.scroll.verticalScrollBar()
        if not delta or bar.maximum() <= bar.minimum():
            return
        if abs(delta) >= 120:
            distance = (float(delta) / 120.0) * max(1, bar.singleStep()) * 3
        else:
            distance = float(delta)
        bar.setValue(bar.value() - int(round(distance)))

    def _refresh_move_controls(self) -> None:
        movable = [
            card
            for card in self.cards
            if (
                card.selected.isChecked()
                and not bool(card.item.get("display_only"))
                and not card.primary.isChecked()
            )
        ]
        positions = {id(card): index for index, card in enumerate(movable)}
        for card in self.cards:
            index = positions.get(id(card))
            if index is None:
                card.move_earlier.setEnabled(False)
                card.move_later.setEnabled(False)
                continue
            card.move_earlier.setEnabled(index > 0)
            card.move_later.setEnabled(index < len(movable) - 1)

    def _update_summary(self) -> None:
        site_selected = sum(1 for card in self.cards if card.selected.isChecked())
        operation_selected = sum(
            1 for card in self.cards if card.bulk_selected.isChecked()
        )
        self.summary.setText(
            f"{len(self.cards)} تصویر • {operation_selected} انتخاب عملیاتی • "
            f"{site_selected} انتخاب‌شده در سایت • "
            f"{self._missing_count} بدون فایل محلی"
        )

    def _primary_changed(self, url: str) -> None:
        if self._primary_sync:
            return
        self._primary_sync = True
        try:
            for card in self.cards:
                if str(card.item.get("url") or "") != url:
                    card.primary.setChecked(False)
            self._refresh_move_controls()
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

    def operation_urls(self) -> list[str]:
        return [
            str(card.item.get("url") or "")
            for card in self.cards
            if (
                card.bulk_selected.isChecked()
                and not bool(card.item.get("display_only"))
            )
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
            if card.selected.isEnabled():
                card.selected.setChecked(bool(checked))

    def set_all_operation_selected(self, checked: bool) -> None:
        for card in self.cards:
            if card.bulk_selected.isEnabled():
                card.bulk_selected.setChecked(bool(checked))

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
