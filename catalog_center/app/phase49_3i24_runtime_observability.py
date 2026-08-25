from __future__ import annotations

import faulthandler
import json
import os
import sys
import threading
import time
import traceback
from pathlib import Path
from tkinter import messagebox, ttk

from .phase49_diagnostics import audit_event, redact


PHASE = "49.3I.24"
_HEARTBEAT_MS = 500
_LAG_WARN_SECONDS = 2.5
_HANG_DUMP_SECONDS = 8.0
_DUMP_COOLDOWN_SECONDS = 20.0


def _safe_line(value) -> str:
    try:
        return redact(json.dumps(value, ensure_ascii=False, default=str))
    except Exception:
        return redact(str(value))


def install(app_class, data_root: str | Path) -> None:
    """Add first-launch-to-close observability without blocking Tk's UI thread."""
    if getattr(app_class, "_phase49_3i24_runtime_observability", False):
        return

    data_root = Path(data_root)
    log_dir = data_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    session_path = log_dir / "catalog-runtime-session.jsonl"
    hang_path = log_dir / "catalog-hang-thread-dump.log"

    original_init = app_class.__init__
    original_dashboard = app_class._build_ux87_dashboard
    original_close = getattr(app_class, "on_close", None)

    def _runtime_write(self, action: str, **detail):
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "monotonic": round(time.monotonic(), 3),
            "action": action,
            "thread": threading.current_thread().name,
            "detail": detail,
        }
        try:
            with self._phase49_3i24_runtime_lock:
                with session_path.open("a", encoding="utf-8") as handle:
                    handle.write(_safe_line(row) + "\n")
        except Exception:
            pass

    def _install_exception_hooks(self):
        previous_sys = sys.excepthook
        previous_thread = getattr(threading, "excepthook", None)

        def sys_hook(exc_type, exc_value, exc_tb):
            _runtime_write(
                self,
                "unhandled_exception",
                error=f"{exc_type.__name__}: {exc_value}",
                traceback="".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
            )
            if previous_sys:
                previous_sys(exc_type, exc_value, exc_tb)

        def thread_hook(args):
            _runtime_write(
                self,
                "thread_exception",
                thread=getattr(args.thread, "name", ""),
                error=f"{args.exc_type.__name__}: {args.exc_value}",
                traceback="".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)),
            )
            if previous_thread:
                previous_thread(args)

        sys.excepthook = sys_hook
        if hasattr(threading, "excepthook"):
            threading.excepthook = thread_hook
        self._phase49_3i24_previous_sys_hook = previous_sys
        self._phase49_3i24_previous_thread_hook = previous_thread

    def _start_watchdog(self):
        def watchdog():
            while not self._phase49_3i24_watchdog_stop.wait(1.0):
                lag = time.monotonic() - self._phase49_3i24_last_pulse
                if lag < _HANG_DUMP_SECONDS:
                    continue
                now = time.monotonic()
                if now - self._phase49_3i24_last_dump < _DUMP_COOLDOWN_SECONDS:
                    continue
                self._phase49_3i24_last_dump = now
                _runtime_write(self, "ui_hang_detected", lag_seconds=round(lag, 3))
                try:
                    with self._phase49_3i24_dump_lock:
                        with hang_path.open("a", encoding="utf-8") as handle:
                            handle.write(
                                f"\n===== UI HANG {time.strftime('%Y-%m-%d %H:%M:%S')} lag={lag:.3f}s =====\n"
                            )
                            faulthandler.dump_traceback(file=handle, all_threads=True)
                            handle.flush()
                except Exception as exc:
                    _runtime_write(self, "hang_dump_failed", error=str(exc))

        threading.Thread(target=watchdog, name="CatalogHangWatchdog", daemon=True).start()

    def _heartbeat(self):
        now = time.monotonic()
        gap = now - self._phase49_3i24_last_pulse
        self._phase49_3i24_last_pulse = now
        if gap >= _LAG_WARN_SECONDS:
            _runtime_write(self, "ui_lag_recovered", lag_seconds=round(gap, 3))
            audit_event(
                "performance",
                "ui_lag",
                status="warning",
                level="WARNING",
                source_file=__file__,
                message=f"Tk heartbeat gap {gap:.3f}s",
                detail={"lag_seconds": round(gap, 3)},
            )
        try:
            self.after(_HEARTBEAT_MS, self._phase49_3i24_heartbeat)
        except Exception:
            pass

    def __init__(self, *args, **kwargs):
        started = time.monotonic()
        self._phase49_3i24_runtime_lock = threading.RLock()
        self._phase49_3i24_dump_lock = threading.RLock()
        self._phase49_3i24_watchdog_stop = threading.Event()
        self._phase49_3i24_last_pulse = time.monotonic()
        self._phase49_3i24_last_dump = 0.0
        self._phase49_3i24_runtime_session_path = session_path
        self._phase49_3i24_hang_path = hang_path
        _runtime_write(
            self,
            "app_constructor_enter",
            pid=os.getpid(),
            python=sys.version.split()[0],
            cwd=os.getcwd(),
            source=str(Path(__file__).resolve()),
        )
        try:
            original_init(self, *args, **kwargs)
        except Exception as exc:
            _runtime_write(
                self,
                "app_constructor_failed",
                duration_ms=int((time.monotonic() - started) * 1000),
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            raise
        _runtime_write(
            self,
            "app_constructor_ready",
            duration_ms=int((time.monotonic() - started) * 1000),
            main_thread=threading.get_ident(),
        )
        _install_exception_hooks(self)
        self._phase49_3i24_heartbeat = lambda: _heartbeat(self)
        self.after(_HEARTBEAT_MS, self._phase49_3i24_heartbeat)
        _start_watchdog(self)

    def _open_log_folder(self):
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            if os.name == "nt":
                os.startfile(str(log_dir))  # type: ignore[attr-defined]
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(log_dir)])
        except Exception as exc:
            messagebox.showerror("3DPrintHub — لاگ", str(exc), parent=self)

    def _build_ux87_dashboard(self):
        original_dashboard(self)
        card = ttk.LabelFrame(
            self.dashboard_tab,
            text="لاگ و عیب‌یابی برنامه — از شروع تا بسته‌شدن",
            padding=12,
            style="Card.TLabelframe",
        )
        card.pack(fill="x", pady=(12, 0))
        ttk.Label(
            card,
            text="Startup، کندی UI، Thread hang، خطاهای Tk و درخواست‌های AI ثبت می‌شوند. گزارش خروجی Secretها را حذف می‌کند.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=8)
        ttk.Button(
            card,
            text="📋 لاگ برنامه",
            command=self.open_phase49_app_log,
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            card,
            text="🤖 لاگ AI",
            command=self.open_phase49_ai_log,
        ).pack(side="left", padx=3)
        ttk.Button(
            card,
            text="🧰 ساخت گزارش امن برای GitHub",
            command=self.export_phase49_diagnostics,
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            card,
            text="📂 پوشه لاگ",
            command=lambda: _open_log_folder(self),
        ).pack(side="left", padx=3)

    def on_close(self):
        _runtime_write(
            self,
            "app_close_requested",
            live_threads=[thread.name for thread in threading.enumerate()],
        )
        self._phase49_3i24_watchdog_stop.set()
        if original_close is not None:
            return original_close(self)
        try:
            self.destroy()
        except Exception:
            pass

    app_class.__init__ = __init__
    app_class._build_ux87_dashboard = _build_ux87_dashboard
    app_class.on_close = on_close
    app_class._phase49_3i24_runtime_observability = True
