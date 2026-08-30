from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from .actions import ActionRegistry


class CommandPalette(QDialog):
    def __init__(self, registry: ActionRegistry, parent=None) -> None:
        super().__init__(parent)
        self.registry = registry
        self.setWindowTitle("فرمان سریع")
        self.setModal(True)
        self.resize(620, 420)

        root = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("نام فرمان را بنویس…")
        self.list = QListWidget()
        root.addWidget(self.search)
        root.addWidget(self.list, 1)

        self.search.textChanged.connect(self.refresh)
        self.search.returnPressed.connect(self.execute_current)
        self.list.itemDoubleClicked.connect(lambda _item: self.execute_current())
        self.refresh()
        self.search.setFocus(Qt.FocusReason.OtherFocusReason)

    def refresh(self) -> None:
        self.list.clear()
        for key, spec, action in self.registry.matching(self.search.text()):
            item = QListWidgetItem(spec.text)
            item.setData(Qt.ItemDataRole.UserRole, key)
            if spec.status_tip:
                item.setToolTip(spec.status_tip)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
            self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)

    def execute_current(self) -> None:
        item = self.list.currentItem()
        if item is None:
            return
        key = item.data(Qt.ItemDataRole.UserRole)
        action = self.registry.action(str(key))
        if action.isEnabled():
            action.trigger()
            self.accept()
