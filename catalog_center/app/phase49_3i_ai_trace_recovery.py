from __future__ import annotations

import json
import re
import threading
import time
import tkinter as tk
import types
from tkinter import messagebox, ttk

from . import ai_providers
from . import phase49_3f_gemini_provider as gemini_provider
from . import phase49_3f_runtime_trace as runtime_trace
from .ai_providers import AIProviderClient
from .phase49_diagnostics import audit_event
from .phase49_3i_ai_refresh_completion import _is_generic_title


TITLE_WATCHDOG_MS = 90_000
TRACE_TEXT_LIMIT = 60_000
TRACE_LIST_LIMIT = 120
TRACE_DICT_LIMIT = 160

_PROGRESS_LOCK = threading.RLock()
_ACTIVE_PROGRESS: dict[int, object] = {}


def _safe_exists(widget) -> bool:
    try:
        return bool(widget is not None and widget.winfo_exists())
    except Exception:
        return False


def _snapshot(value, depth: int = 0):
    if depth >= 8:
        return "[depth limit]"
    if isinstance(value, dict):
        output = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= TRACE_DICT_LIMIT:
                output["..."] = f"[{len(value) - TRACE_DICT_LIMIT} more keys]"
                break
            output[str(key)] = _snapshot(item, depth + 1)
        return output
    if isinstance(value, (list, tuple)):
        items = [_snapshot(item, depth + 1) for item in list(value)[:TRACE_LIST_LIMIT]]
        if len(value) > TRACE_LIST_LIMIT:
            items.append(f"[{len(value) - TRACE_LIST_LIMIT} more items]")
        return items
    if isinstance(value, str):
        safe = runtime_trace._sanitize(value)
        return safe[:TRACE_TEXT_LIMIT] + ("... [truncated]" if len(safe) > TRACE_TEXT_LIMIT else "")
    return runtime_trace._sanitize(value)


def _pretty(value) -> str:
    safe = _snapshot(value)
    try:
        text = json.dumps(safe, ensure_ascii=False, indent=2, default=str)
    except Exception:
        text = str(safe)
    if len(text) > TRACE_TEXT_LIMIT:
        return text[:TRACE_TEXT_LIMIT] + "\n... [truncated]"
    return text


def _register_progress(progress) -> None:
    product_id = getattr(progress, "product_id", None)
    if product_id in (None, ""):
        return
    with _PROGRESS_LOCK:
        _ACTIVE_PROGRESS[int(product_id)] = progress


def _unregister_progress(progress) -> None:
    product_id = getattr(progress, "product_id", None)
    if product_id in (None, ""):
        return
    with _PROGRESS_LOCK:
        if _ACTIVE_PROGRESS.get(int(product_id)) is progress:
            _ACTIVE_PROGRESS.pop(int(product_id), None)


def _progress_for(product_id):
    if product_id in (None, ""):
        return None
    with _PROGRESS_LOCK:
        return _ACTIVE_PROGRESS.get(int(product_id))


def _dispatch(progress, method: str, payload) -> None:
    if progress is None:
        return
    parent = getattr(progress, "parent", None)
    root = getattr(parent, "app", None) or parent
    if root is None:
        return

    def apply(p=progress, name=method, value=payload):
        if not _safe_exists(getattr(p, "win", None)):
            return
        fn = getattr(p, name, None)
        if callable(fn):
            fn(value)

    try:
        root.after(0, apply)
    except Exception:
        pass


def _trace_request(product_id, *, provider: str, model: str, operation: str, endpoint: str, method: str, payload) -> None:
    detail = {
        "provider": provider,
        "model": model,
        "operation": operation,
        "endpoint": endpoint,
        "method": method,
        "payload": _snapshot(payload or {}),
    }
    runtime_trace.event(
        "ai-http",
        "request",
        product_id=product_id,
        provider=provider,
        model=model,
        detail=detail,
    )
    _dispatch(_progress_for(product_id), "append_request", detail)


def _trace_response(product_id, *, provider: str, model: str, operation: str, endpoint: str, response) -> None:
    detail = {
        "provider": provider,
        "model": model,
        "operation": operation,
        "endpoint": endpoint,
        "response": _snapshot(response),
    }
    runtime_trace.event(
        "ai-http",
        "response",
        product_id=product_id,
        provider=provider,
        model=model,
        detail=detail,
    )
    _dispatch(_progress_for(product_id), "append_response", detail)


def _trace_error(product_id, *, provider: str, model: str, operation: str, endpoint: str, error_text: str) -> None:
    detail = {
        "provider": provider,
        "model": model,
        "operation": operation,
        "endpoint": endpoint,
        "error": str(error_text or ""),
    }
    runtime_trace.event(
        "ai-http",
        "error",
        status="error",
        product_id=product_id,
        provider=provider,
        model=model,
        message=str(error_text or ""),
        detail=detail,
    )
    _dispatch(_progress_for(product_id), "append_error", detail)


def _install_http_trace() -> None:
    if getattr(ai_providers, "_phase49_3i10_http_trace_installed", False):
        return

    original_json_request = ai_providers._json_request

    def traced_json_request(
        url: str,
        key: str,
        *,
        payload=None,
        method: str = "GET",
        timeout: int = 120,
        provider: str = "",
        model: str = "",
        operation: str = "",
        product_id=None,
    ):
        _trace_request(
            product_id,
            provider=provider,
            model=model,
            operation=operation or method.lower(),
            endpoint=url,
            method=method,
            payload=payload,
        )
        try:
            data = original_json_request(
                url,
                key,
                payload=payload,
                method=method,
                timeout=timeout,
                provider=provider,
                model=model,
                operation=operation,
                product_id=product_id,
            )
        except Exception as exc:
            _trace_error(
                product_id,
                provider=provider,
                model=model,
                operation=operation or method.lower(),
                endpoint=url,
                error_text=f"{type(exc).__name__}: {exc}",
            )
            raise
        _trace_response(
            product_id,
            provider=provider,
            model=model or str((data or {}).get("model") or ""),
            operation=operation or method.lower(),
            endpoint=url,
            response=data,
        )
        return data

    ai_providers._json_request = traced_json_request
    ai_providers._phase49_3i10_http_trace_installed = True

    if getattr(gemini_provider, "_phase49_3i10_http_trace_installed", False):
        return
    original_google_request = gemini_provider._google_request

    def traced_google_request(
        api_key: str,
        path: str,
        *,
        payload=None,
        method: str = "GET",
        timeout: int = 30,
        model: str = "",
        operation: str = "",
        product_id=None,
    ):
        endpoint = gemini_provider.GOOGLE_BASE.rstrip("/") + "/" + str(path).lstrip("/")
        _trace_request(
            product_id,
            provider="google",
            model=model,
            operation=operation or method.lower(),
            endpoint=endpoint,
            method=method,
            payload=payload,
        )
        try:
            data = original_google_request(
                api_key,
                path,
                payload=payload,
                method=method,
                timeout=timeout,
                model=model,
                operation=operation,
                product_id=product_id,
            )
        except Exception as exc:
            _trace_error(
                product_id,
                provider="google",
                model=model,
                operation=operation or method.lower(),
                endpoint=endpoint,
                error_text=f"{type(exc).__name__}: {exc}",
            )
            raise
        _trace_response(
            product_id,
            provider="google",
            model=model,
            operation=operation or method.lower(),
            endpoint=endpoint,
            response=data,
        )
        return data

    gemini_provider._google_request = traced_google_request
    gemini_provider._phase49_3i10_http_trace_installed = True


def _make_cell(value):
    return (lambda: value).__closure__[0]


def _freeze_exception_callback(callback):
    """Freeze exception closure cells before Python clears `except ... as exc`.

    Python deliberately clears the exception target when an except block exits.
    Tk callbacks scheduled with `after(..., lambda: ... exc ...)` therefore fail
    later with `NameError`. Only callbacks that actually close over an exception
    are copied; every other Tk callback is untouched.
    """
    if not isinstance(callback, types.FunctionType):
        return callback
    closure = callback.__closure__ or ()
    names = callback.__code__.co_freevars
    if not closure or len(closure) != len(names):
        return callback
    captured = []
    has_exception = False
    for name, cell in zip(names, closure):
        try:
            value = cell.cell_contents
        except ValueError:
            return callback
        captured.append(value)
        if isinstance(value, BaseException) and name in {"exc", "error", "exception"}:
            has_exception = True
    if not has_exception:
        return callback
    return types.FunctionType(
        callback.__code__,
        callback.__globals__,
        name=callback.__name__,
        argdefs=callback.__defaults__,
        closure=tuple(_make_cell(value) for value in captured),
    )


def _install_tk_exception_callback_guard() -> None:
    if getattr(tk.Misc, "_phase49_3i10_exception_after_guard", False):
        return
    original_after = tk.Misc.after

    def after(self, ms, func=None, *args):
        if func is not None:
            func = _freeze_exception_callback(func)
        return original_after(self, ms, func, *args)

    tk.Misc.after = after
    tk.Misc._phase49_3i10_exception_after_guard = True


def _validate_title(title: str, source: str) -> str:
    value = " ".join(str(title or "").split()).strip()
    if not value:
        raise RuntimeError("هوش مصنوعی عنوان فارسی خالی برگرداند.")
    if _is_generic_title(value):
        raise RuntimeError(
            "هوش مصنوعی یک عنوان عمومی مثل «محصول چاپ سه‌بعدی» برگرداند. "
            "خروجی ثبت نشد؛ Provider/Model را عوض کن و دوباره ترجمه را بزن."
        )
    if not re.search(r"[\u0600-\u06ff]", value):
        raise RuntimeError("پاسخ عنوان فارسی معتبر ندارد؛ خروجی ثبت نشد.")
    if str(source or "").strip() and len(value) < 6:
        raise RuntimeError("عنوان ترجمه‌شده بیش از حد کوتاه است و هویت محصول را منتقل نمی‌کند.")
    return value


def install(workspace_class, phase49_3f_workspace_module) -> None:
    if getattr(workspace_class, "_phase49_3i10_ai_trace_recovery_installed", False):
        return

    _install_tk_exception_callback_guard()
    _install_http_trace()

    CurrentProgress = phase49_3f_workspace_module.AIProgress

    class TraceableAIProgress(CurrentProgress):
        def __init__(self, parent, title: str, product_id: int | None = None):
            super().__init__(parent, title, product_id)
            self._phase49_3i10_cancel_hook = None
            self._phase49_3i10_texts = {}
            try:
                self.win.geometry("940x720")
                self.win.minsize(760, 560)
                self.win.resizable(True, True)
            except Exception:
                pass
            self._phase49_3i10_build_trace_tabs()
            _register_progress(self)

        def _phase49_3i10_build_trace_tabs(self):
            if not _safe_exists(getattr(self, "win", None)):
                return
            holder = ttk.LabelFrame(self.win, text="جزئیات قابل بررسی — بدون API Key/Token", padding=6)
            holder.pack(side="bottom", fill="both", expand=True, padx=16, pady=(0, 10))
            notebook = ttk.Notebook(holder)
            notebook.pack(fill="both", expand=True)
            for key, label in (
                ("request", "ارسالی"),
                ("response", "دریافتی"),
                ("error", "خطا / Diagnostics"),
            ):
                tab = ttk.Frame(notebook)
                notebook.add(tab, text=label)
                tab.rowconfigure(0, weight=1)
                tab.columnconfigure(0, weight=1)
                text = tk.Text(tab, wrap="none", height=9, font=("Consolas", 9))
                ybar = ttk.Scrollbar(tab, orient="vertical", command=text.yview)
                xbar = ttk.Scrollbar(tab, orient="horizontal", command=text.xview)
                text.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
                text.grid(row=0, column=0, sticky="nsew")
                ybar.grid(row=0, column=1, sticky="ns")
                xbar.grid(row=1, column=0, sticky="ew")
                self._phase49_3i10_texts[key] = text
            self._phase49_3i10_notebook = notebook

        def _append_trace(self, key: str, payload):
            text = self._phase49_3i10_texts.get(key)
            if text is None or not _safe_exists(text):
                return
            stamp = time.strftime("%H:%M:%S")
            text.insert("end", f"[{stamp}]\n{_pretty(payload)}\n\n")
            text.see("end")

        def append_request(self, payload):
            self._append_trace("request", payload)

        def append_response(self, payload):
            self._append_trace("response", payload)

        def append_error(self, payload):
            self._append_trace("error", payload)

        def _phase49_3i8_cancel(self):
            result = super()._phase49_3i8_cancel()
            hook = getattr(self, "_phase49_3i10_cancel_hook", None)
            if callable(hook):
                try:
                    hook()
                except Exception:
                    pass
            return result

        def fail(self, message: str):
            self.append_error({"message": str(message or "")})
            return super().fail(message)

        def close(self):
            _unregister_progress(self)
            return super().close()

    phase49_3f_workspace_module.AIProgress = TraceableAIProgress

    def translate_title_only(self):
        if getattr(self, "_phase49_3i10_title_busy", False) or getattr(self, "_phase49_3e_busy", False) or getattr(self, "_ai_busy", False):
            try:
                self.footer_status.set("یک درخواست هوش مصنوعی در حال اجرا است؛ ابتدا همان عملیات را تمام یا متوقف کن.")
            except Exception:
                pass
            return None

        row = self.db.product(self.product_id)
        try:
            source = str(row["source_title"] or "").strip() if row is not None else ""
        except Exception:
            source = ""
        if not source:
            messagebox.showinfo("3DPrintHub", "عنوان منبع برای این محصول خالی است.", parent=self)
            return None

        provider = self.app._selected_ai_provider()
        key = self.app._ai_key(provider)
        model = str(self.app.ai_model.get() if hasattr(self.app, "ai_model") else "").strip()
        if not key:
            messagebox.showwarning(
                "3DPrintHub",
                f"API Key برای {provider} تنظیم نشده است. Provider/Model را تنظیم و دوباره تلاش کن.",
                parent=self,
            )
            return None

        instructions = (
            "Translate only the supplied 3D product title into one fluent, specific Persian ecommerce title. "
            "The source title is authoritative product identity. Preserve the concrete object, function/use, theme, "
            "character/franchise/model/proper names and meaningful style modifiers. Never replace a specific title "
            "with generic phrases such as محصول چاپ سه بعدی, مدل چاپ سه بعدی or فایل چاپ سه بعدی. "
            "Do not add claims, price, material, dimensions or marketing facts not present in the source title. "
            "Return only the requested JSON object."
        )
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {"title_fa": {"type": "string"}},
            "required": ["title_fa"],
        }
        logical_request = {
            "provider": provider,
            "requested_model": model,
            "operation": "title_fa_only",
            "instructions": instructions,
            "input_content": [{"type": "input_text", "text": source}],
            "schema": schema,
        }

        progress = phase49_3f_workspace_module.AIProgress(self, "ترجمه دوباره عنوان محصول", self.product_id)
        progress.append_request({"logical_request": logical_request})
        progress.step("آماده‌سازی ترجمه عنوان", f"Provider={provider} • Model={model or 'auto'}")
        progress.step("ارسال عنوان منبع به هوش مصنوعی", source)

        counter = int(getattr(self, "_phase49_3i10_title_generation_counter", 0) or 0) + 1
        self._phase49_3i10_title_generation_counter = counter
        self._phase49_3i10_title_active_generation = counter
        self._phase49_3i10_title_busy = True
        started = time.monotonic()
        timeout_id = {"value": None}

        runtime_trace.event(
            "ai",
            "phase49-3i10-title-start",
            product_id=self.product_id,
            provider=provider,
            model=model,
            detail={"generation": counter, "source_title": source, "watchdog_ms": TITLE_WATCHDOG_MS},
        )

        def clear_busy():
            self._phase49_3i10_title_busy = False
            if int(getattr(self, "_phase49_3i10_title_active_generation", 0) or 0) == counter:
                self._phase49_3i10_title_active_generation = 0

        def cancel_timeout():
            ident = timeout_id.get("value")
            if ident is not None:
                try:
                    self.after_cancel(ident)
                except Exception:
                    pass
                timeout_id["value"] = None

        def cancelled_by_operator():
            clear_busy()
            cancel_timeout()
            runtime_trace.event(
                "ai",
                "phase49-3i10-title-cancelled",
                status="blocked",
                product_id=self.product_id,
                provider=provider,
                model=model,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                detail={"generation": counter},
            )
            try:
                self.footer_status.set("ترجمه عنوان توسط اپراتور متوقف شد؛ پاسخ دیرهنگام روی محصول اعمال نمی‌شود.")
            except Exception:
                pass

        progress._phase49_3i10_cancel_hook = cancelled_by_operator

        def is_current() -> bool:
            if int(getattr(self, "_phase49_3i10_title_active_generation", 0) or 0) != counter:
                return False
            if getattr(progress, "_phase49_3i8_cancelled", False):
                return False
            return _safe_exists(self) and _safe_exists(getattr(progress, "win", None))

        def on_timeout():
            timeout_id["value"] = None
            if not is_current():
                return
            clear_busy()
            message = (
                "ترجمه عنوان تا ۹۰ ثانیه نتیجه قابل استفاده نداد. انتظار متوقف شد؛ "
                "اگر پاسخ شبکه دیرتر برسد روی محصول اعمال نمی‌شود. Provider/Model یا اتصال را بررسی کن."
            )
            if hasattr(progress, "_phase49_3i8_abort"):
                progress._phase49_3i8_abort(message, reason="title_watchdog_timeout")
            else:
                progress.fail(message)
            runtime_trace.event(
                "ai",
                "phase49-3i10-title-timeout",
                status="error",
                product_id=self.product_id,
                provider=provider,
                model=model,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                detail={"generation": counter, "watchdog_ms": TITLE_WATCHDOG_MS},
            )
            try:
                self.footer_status.set("ترجمه عنوان Timeout شد؛ محصول تغییر نکرد.")
            except Exception:
                pass

        timeout_id["value"] = self.after(TITLE_WATCHDOG_MS, on_timeout)

        def apply_success(title: str, used_model: str, result: dict):
            cancel_timeout()
            if not is_current():
                runtime_trace.event(
                    "ai",
                    "phase49-3i10-title-stale-result-discarded",
                    status="blocked",
                    product_id=self.product_id,
                    provider=provider,
                    model=used_model or model,
                    elapsed_ms=int((time.monotonic() - started) * 1000),
                    detail={"generation": counter},
                )
                return
            progress.step("پاسخ دریافت شد", f"Model={used_model or model}")
            progress.append_response({"validated_result": result, "title_fa": title})
            progress.step("اعتبارسنجی عنوان فارسی", "عنوان اختصاصی و فارسی معتبر است؛ در حال ثبت")
            self.db.update_product(
                self.product_id,
                {
                    "title_fa": title,
                    "translation_status": "done",
                    "ai_provider": provider,
                    "ai_model": used_model or model,
                },
            )
            audit_event(
                "ai",
                "title_translation",
                product_id=self.product_id,
                message=f"provider={provider} model={used_model or model}",
                detail={"source_title": source, "title_fa": title},
            )
            runtime_trace.event(
                "ai",
                "phase49-3i10-title-done",
                product_id=self.product_id,
                provider=provider,
                model=used_model or model,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                detail={"generation": counter, "source_title": source, "title_fa": title},
            )
            clear_busy()
            try:
                self.reload()
            except Exception:
                pass
            try:
                self.footer_status.set(f"عنوان فارسی با {used_model or model or provider} دوباره ترجمه و ثبت شد.")
            except Exception:
                pass
            progress.done("ترجمه عنوان با موفقیت ثبت شد", title)

        def apply_error(error_text: str):
            cancel_timeout()
            if not is_current():
                return
            clear_busy()
            progress.append_error({"error": error_text, "provider": provider, "model": model})
            progress.fail(error_text)
            runtime_trace.event(
                "ai",
                "phase49-3i10-title-error",
                status="error",
                product_id=self.product_id,
                provider=provider,
                model=model,
                elapsed_ms=int((time.monotonic() - started) * 1000),
                message=error_text,
                detail={"generation": counter, "source_title": source},
            )
            try:
                self.footer_status.set("ترجمه عنوان ناموفق بود؛ جزئیات دقیق در تب خطا و لاگ ثبت شده است.")
            except Exception:
                pass

        def worker():
            try:
                client = AIProviderClient(provider, key, model, product_id=self.product_id)
                result, used = client.structured_response(
                    instructions=instructions,
                    input_content=[{"type": "input_text", "text": source}],
                    schema=schema,
                    schema_name="title_fa_only_v2",
                    preferred_model=model,
                )
                title = _validate_title(str(result.get("title_fa") or ""), source)
                root = getattr(self, "app", None) or self
                root.after(0, lambda title=title, used=used, result=dict(result): apply_success(title, used, result))
            except Exception as exc:
                error_text = f"{type(exc).__name__}: {exc}"
                root = getattr(self, "app", None) or self
                try:
                    root.after(0, lambda error_text=error_text: apply_error(error_text))
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()
        return None

    workspace_class.translate_title_only = translate_title_only
    workspace_class._phase49_3i10_ai_trace_recovery_installed = True
