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

from .ai_providers import AIProviderClient
from .phase49_diagnostics import audit_event, export_diagnostic_bundle, redact
from .phase49_3i23_avalai_chat_contract import product_text_model_reason


PHASE = "49.3I.24"
_HEARTBEAT_MS = 500
_LAG_WARN_SECONDS = 2.5
_HANG_DUMP_SECONDS = 8.0
_DUMP_COOLDOWN_SECONDS = 20.0
_TAIL_CHARS = 240_000


def _safe_line(value) -> str:
    try:
        return redact(json.dumps(value, ensure_ascii=False, default=str))
    except Exception:
        return redact(str(value))


def _tail(path: Path, limit: int = _TAIL_CHARS) -> str:
    try:
        if not path.is_file():
            return ""
        text = path.read_text(encoding="utf-8", errors="replace")
        return redact(text[-limit:])
    except Exception as exc:
        return f"<unable to read {path.name}: {redact(exc)}>"


def _install_ai_runtime_guards() -> None:
    """Prevent hidden startup network scans and reject obvious non-text models."""
    Client = AIProviderClient
    if getattr(Client, "_phase49_3i24_runtime_guards", False):
        return

    original_list = Client.list_model_info
    original_structured = Client.structured_response
    # Guard is enabled only by the real wrapped App constructor. Keeping it off
    # at import/install time prevents unrelated tests and explicit utilities from
    # inheriting a process-global network block before an App instance exists.
    Client._phase49_3i24_startup_guard = False
    Client._phase49_3i24_startup_block_count = 0
    guard_lock = threading.RLock()

    def list_model_info(self):
        if bool(getattr(Client, "_phase49_3i24_startup_guard", False)) and self.product_id is None:
            with guard_lock:
                Client._phase49_3i24_startup_block_count += 1
            return []
        info = original_list(self)
        if self.provider == "avalai":
            for item in info:
                item["free"] = str(item.get("id") or "").lower().endswith(":free")
        return info

    def structured_response(self, **kwargs):
        if self.product_id is not None:
            model = str(kwargs.get("preferred_model") or self.model or "").strip()
            rejection = product_text_model_reason(model)
            if rejection:
                raise RuntimeError(rejection)
        return original_structured(self, **kwargs)

    Client.list_model_info = list_model_info
    Client.structured_response = structured_response
    Client._phase49_3i24_runtime_guards = True

    try:
        from . import phase49_3d_workflow_hardening as hardening

        if not getattr(hardening, "_phase49_3i24_product_text_model_filter", False):
            original_matches = hardening.model_matches

            def model_matches(query: str, item: dict) -> bool:
                model_id = str((item or {}).get("id") or "")
                if product_text_model_reason(model_id):
                    return False
                return original_matches(query, item)

            hardening.model_matches = model_matches
            hardening._phase49_3i24_product_text_model_filter = True
    except Exception:
        pass


def install(app_class, data_root: str | Path) -> None:
    """Add first-launch-to-close observability without blocking Tk's UI thread."""
    if getattr(app_class, "_phase49_3i24_runtime_observability", False):
        return

    _install_ai_runtime_guards()
    data_root = Path(data_root)
    log_dir = data_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    session_path = log_dir / "catalog-runtime-session.jsonl"
    hang_path = log_dir / "catalog-hang-thread-dump.log"
    main_log_path = log_dir / "catalog-intelligence.log"

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

    def _release_startup_guard(self):
        blocked = int(getattr(AIProviderClient, "_phase49_3i24_startup_block_count", 0) or 0)
        AIProviderClient._phase49_3i24_startup_guard = False
        _runtime_write(self, "first_idle", blocked_hidden_model_scans=blocked)
        audit_event(
            "performance",
            "startup_first_idle",
            source_file=__file__,
            message=f"startup model scans blocked={blocked}",
            detail={"blocked_hidden_model_scans": blocked},
        )

    def __init__(self, *args, **kwargs):
        started = time.monotonic()
        # Scope no-network behavior to the actual construction window only.
        AIProviderClient._phase49_3i24_startup_guard = True
        AIProviderClient._phase49_3i24_startup_block_count = 0
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
            AIProviderClient._phase49_3i24_startup_guard = False
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
        self.after_idle(lambda: _release_startup_guard(self))
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

    def _export_github_diagnostic(self):
        try:
            product_id = getattr(self, "current_product", None)
            path = export_diagnostic_bundle(data_root, product_id=product_id)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["runtime_files"] = {
                "catalog_runtime_session_tail": _tail(session_path),
                "catalog_main_log_tail": _tail(main_log_path),
                "catalog_hang_thread_dump_tail": _tail(hang_path),
            }
            payload["runtime_state"] = {
                "active_threads": [thread.name for thread in threading.enumerate()],
                "startup_hidden_model_scans_blocked": int(
                    getattr(AIProviderClient, "_phase49_3i24_startup_block_count", 0) or 0
                ),
                "secrets_included": False,
            }
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            audit_event(
                "diagnostics",
                "github_ready_export",
                product_id=product_id,
                source_file=__file__,
                message=str(path),
            )
            messagebox.showinfo(
                "3DPrintHub — گزارش عیب‌یابی",
                f"گزارش امن برای ارسال در GitHub ساخته شد:\n{path}\n\nRuntime log و Thread dump نیز داخل همین JSON قرار گرفت.",
                parent=self,
            )
            try:
                if os.name == "nt":
                    os.startfile(str(path.parent))  # type: ignore[attr-defined]
            except Exception:
                pass
        except Exception as exc:
            messagebox.showerror("3DPrintHub — گزارش عیب‌یابی", str(exc), parent=self)

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
        ttk.Button(card, text="🤖 لاگ AI", command=self.open_phase49_ai_log).pack(side="left", padx=3)
        ttk.Button(
            card,
            text="🧰 ساخت گزارش امن برای GitHub",
            command=lambda: _export_github_diagnostic(self),
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(card, text="📂 پوشه لاگ", command=lambda: _open_log_folder(self)).pack(side="left", padx=3)

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
