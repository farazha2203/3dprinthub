from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtGui import QAction, QKeySequence


@dataclass(frozen=True)
class ActionSpec:
    key: str
    text: str
    shortcut: str = ""
    status_tip: str = ""
    toolbar: bool = False


class ActionRegistry:
    """Own each semantic QAction once and reuse that exact object.

    The book-derived rule is intentional: common actions may appear in a toolbar
    and a menu, but they should not be recreated under different labels/icons.
    """

    def __init__(self, parent) -> None:
        self.parent = parent
        self._actions: dict[str, QAction] = {}
        self._specs: dict[str, ActionSpec] = {}

    def register(self, spec: ActionSpec, callback: Callable[[], None]) -> QAction:
        if spec.key in self._actions:
            raise KeyError(f"duplicate action key: {spec.key}")
        action = QAction(spec.text, self.parent)
        if spec.shortcut:
            action.setShortcut(QKeySequence(spec.shortcut))
        if spec.status_tip:
            action.setStatusTip(spec.status_tip)
            action.setToolTip(spec.status_tip)
        action.triggered.connect(callback)
        self._actions[spec.key] = action
        self._specs[spec.key] = spec
        return action

    def action(self, key: str) -> QAction:
        return self._actions[key]

    def spec(self, key: str) -> ActionSpec:
        return self._specs[key]

    def items(self):
        for key in self._actions:
            yield key, self._specs[key], self._actions[key]

    def matching(self, query: str):
        needle = str(query or "").strip().casefold()
        rows = list(self.items())
        if not needle:
            return rows
        return [
            row for row in rows
            if needle in row[0].casefold()
            or needle in row[1].text.casefold()
            or needle in row[1].status_tip.casefold()
        ]
