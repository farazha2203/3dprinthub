from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "0", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        title_label = QLabel(title)
        title_label.setObjectName("Muted")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value) -> None:
        self.value_label.setText(str(value))


class StageStepper(QWidget):
    stageChanged = Signal(int)

    def __init__(self, stages: list[str], parent=None) -> None:
        super().__init__(parent)
        self.stages = list(stages)
        self._status: list[str] = ["missing"] * len(self.stages)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        legend = QLabel("❌ ناقص   •   ◌ کامل/منتظر تأیید   •   ✅ ثبت نهایی")
        legend.setObjectName("Muted")
        legend.setWordWrap(True)
        root.addWidget(legend)

        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        for index, label in enumerate(self.stages, start=1):
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, index - 1)
            self.list.addItem(item)
        root.addWidget(self.list)

        self.list.currentRowChanged.connect(self.stageChanged.emit)
        self._repaint_statuses()
        if self.stages:
            self.list.setCurrentRow(0)

    def _repaint_statuses(self) -> None:
        icons = {
            "missing": "❌",
            "ready": "◌",
            "finalized": "✅",
        }
        colors = {
            "missing": QColor("#b42318"),
            "ready": QColor("#8a6100"),
            "finalized": QColor("#117a55"),
        }
        for index, label in enumerate(self.stages):
            item = self.list.item(index)
            status = self._status[index] if index < len(self._status) else "missing"
            item.setText(f"{icons.get(status, '❌')}  {index + 1}. {label}")
            item.setForeground(colors.get(status, colors["missing"]))

    def set_statuses(self, statuses) -> None:
        mapped: list[str] = []
        for item in list(statuses or []):
            if isinstance(item, dict):
                value = str(item.get("status") or "missing")
            else:
                value = str(item or "missing")
            mapped.append(value if value in {"missing", "ready", "finalized"} else "missing")
        if len(mapped) < len(self.stages):
            mapped.extend(["missing"] * (len(self.stages) - len(mapped)))
        self._status = mapped[: len(self.stages)]
        self._repaint_statuses()

    def set_stage(self, index: int) -> None:
        if 0 <= index < len(self.stages):
            self.list.setCurrentRow(index)

    def current_stage(self) -> int:
        return max(0, self.list.currentRow())


class WizardFooter(QWidget):
    previousClicked = Signal()
    nextClicked = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 0)
        self.previous = QPushButton("مرحله قبل")
        self.next = QPushButton("مرحله بعد")
        self.next.setProperty("primary", True)
        layout.addWidget(self.previous)
        layout.addStretch(1)
        layout.addWidget(self.next)
        self.previous.clicked.connect(self.previousClicked.emit)
        self.next.clicked.connect(self.nextClicked.emit)

    def set_position(self, index: int, count: int) -> None:
        self.previous.setEnabled(index > 0)
        self.next.setText("پایان مسیر" if count and index >= count - 1 else "مرحله بعد")
