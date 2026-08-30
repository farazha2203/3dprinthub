from __future__ import annotations

import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    progress = Signal(int, str)
    finished = Signal()


class Worker(QRunnable):
    """Generic QRunnable for slow I/O/CPU orchestration outside the GUI thread."""

    def __init__(self, fn: Callable[..., Any], *args, **kwargs) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = dict(kwargs)
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.kwargs.setdefault(
                "progress",
                lambda value, message="": self.signals.progress.emit(
                    max(0, min(100, int(value))), str(message or "")
                ),
            )
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            self.signals.error.emit(traceback.format_exc())
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class TaskPool:
    def __init__(self) -> None:
        self.pool = QThreadPool.globalInstance()

    @property
    def max_threads(self) -> int:
        return int(self.pool.maxThreadCount())

    def start(self, worker: Worker) -> Worker:
        self.pool.start(worker)
        return worker
