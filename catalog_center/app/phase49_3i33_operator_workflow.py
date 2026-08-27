from __future__ import annotations

import queue
import threading
from contextlib import contextmanager
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from .phase49_3i17_single_active_ai_runtime import active_ai_config
from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
from .phase49_3i33_ai_core import (
    AI_MODES,
    AI_MODE_BY_LABEL,
    OperationTelemetry,
    capture_source_screenshot,
    ensure_schema,
    positive,
    row_value,
    run_ai_mode,
)
from .phase49_diagnostics import audit_event, redact


PHASE = "49.3I.33"


def walk_widgets(root):
    for child in root.winfo_children():
        yield child
        yield from walk_widgets(child)


def hide_widget(widget):
    try:
        manager = widget.winfo_manager()
        if manager == "pack":
            widget.pack_forget()
        elif manager == "grid":
            widget.grid_remove()
        elif manager == "place":
            widget.place_forget()
    except Exception:
        pass


def hide_legacy_ai_buttons(root):
    for widget in walk_widgets(root):
        if not isinstance(widget, (ttk.Button, tk.Button)):
            continue
        try:
            text = str(widget.cget("text") or "")
        except Exception:
            continue
        if "ai" in text.casefold() or "هوش مصنوعی" in text:
            hide_widget(widget)


@contextmanager
def suppress_global_products_refresh(app):
    """Workspace persistence is local; global Products refresh is explicit-only."""
    if app is None:
        yield
        return
    names = (
        "refresh_products",
        "refresh_published",
        "load_product",
        "_phase49_3i29_mark_products_dirty",
        "_phase49_3i29_flush_products_refresh",
    )
    saved = {}
    for name in names:
        value = getattr(app, name, None)
        if value is None:
            continue
        saved[name] = value
        if name == "_phase49_3i29_flush_products_refresh":
            setattr(app, name, lambda *_args, **_kwargs: False)
        else:
            setattr(app, name, lambda *_args, **_kwargs: None)
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(app, name, value)


def fixed_price_from_row(row):
    strategy = str(row_value(row, "pricing_strategy", "") or "").strip().lower()
    minimum = positive(row_value(row, "price_min", None))
    maximum = positive(row_value(row, "price_max", None))
    final = positive(row_value(row, "final_price", None))
    is_final = bool(int(row_value(row, "price_is_final", 0) or 0))
    if strategy == "fixed":
        value = minimum or final
        return str(int(round(value))) if value else ""
    if is_final and minimum and maximum and abs(minimum - maximum) < 0.01:
        return str(int(round(final or minimum)))
    return ""


def image_file_info(path: str, url: str = "") -> str:
    candidate = Path(str(path or ""))
    name = candidate.name if candidate.is_file() else ""
    if not name and url:
        try:
            from urllib.parse import urlsplit
            name = Path(urlsplit(str(url)).path).name
        except Exception:
            name = ""
    if not candidate.is_file():
        prefix = f"{name} • " if name else ""
        return prefix + "فایل محلی موجود نیست • ابعاد/حجم پس از دریافت فایل نمایش داده می‌شود"
    size = candidate.stat().st_size
    try:
        with Image.open(candidate) as opened:
            width, height = opened.size
            fmt = str(opened.format or candidate.suffix.lstrip(".") or "image").upper()
        import math
        divisor = math.gcd(int(width), int(height)) or 1
        ratio = f"{width // divisor}:{height // divisor}"
        human = f"{size / 1048576:.2f} MB" if size >= 1048576 else f"{size / 1024:.0f} KB"
        prefix = f"{name} • " if name else ""
        return prefix + f"{width}×{height}px • نسبت {ratio} • {human} • {fmt}"
    except Exception:
        prefix = f"{name} • " if name else ""
        return prefix + f"{size / 1024:.0f} KB • خواندن ابعاد ناموفق"


def start_runtime_sampler(app):
    if getattr(app, "_phase49_3i33_sampler_started", False):
        return
    app._phase49_3i33_sampler_started = True
    try:
        import psutil
        psutil.Process().cpu_percent(None)
    except Exception:
        return

    def sample():
        try:
            import psutil
            process = psutil.Process()
            net = psutil.net_io_counters()
            audit_event(
                "performance",
                "phase49_3i33_runtime_sample",
                source_file=__file__,
                message="Catalog Center runtime sample",
                detail={
                    "process_cpu_percent": float(process.cpu_percent(None)),
                    "process_rss_mb": round(process.memory_info().rss / 1048576, 1),
                    "process_threads": int(process.num_threads()),
                    "system_ram_percent": float(psutil.virtual_memory().percent),
                    "system_net_sent_bytes": int(net.bytes_sent),
                    "system_net_recv_bytes": int(net.bytes_recv),
                    "network_scope": "system totals; operation spans log deltas",
                },
            )
        except Exception:
            pass
        try:
            app.after(15000, sample)
        except Exception:
            pass

    app.after(15000, sample)


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i33_operator_workflow", False):
        return

    original_init = app_class.__init__
    original_modernize = getattr(app_class, "_modernize_products_page", None)
    original_render = getattr(app_class, "_phase49_3i_render_gallery", None)

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        ensure_schema(self.db)
        self._phase49_3i33_ui_queue = queue.Queue()

        def pump_ui():
            while True:
                try:
                    callback = self._phase49_3i33_ui_queue.get_nowait()
                except queue.Empty:
                    break
                try:
                    callback()
                except Exception as exc:
                    audit_event(
                        "ui", "phase49_3i33_deferred_callback_error",
                        status="error", level="ERROR", source_file=__file__,
                        message=redact(exc),
                    )
            try:
                self.after(30, pump_ui)
            except Exception:
                pass

        self.after(30, pump_ui)
        start_runtime_sampler(self)

    def post_ui(self, callback):
        self._phase49_3i33_ui_queue.put(callback)

    def modernize_products_page(self):
        if callable(original_modernize):
            original_modernize(self)
        hide_legacy_ai_buttons(self.products_tab)
        panel = ttk.LabelFrame(
            self.products_tab,
            text="ترجمه و SEO گروهی محصولات انتخاب‌شده",
            padding=7,
            style="Card.TLabelframe",
        )
        shell = getattr(getattr(self, "_phase49_3i_gallery_canvas", None), "master", None)
        try:
            panel.pack(fill="x", pady=(0, 7), before=shell)
        except Exception:
            panel.pack(fill="x", pady=(0, 7))
        self._phase49_3i33_bulk_mode = tk.StringVar(value=AI_MODES["link"])
        ttk.Combobox(
            panel,
            textvariable=self._phase49_3i33_bulk_mode,
            values=list(AI_MODES.values()),
            state="readonly",
            width=42,
        ).pack(side="right", padx=5)
        ttk.Button(
            panel,
            text="اجرای ترجمه/SEO روی انتخاب‌شده‌ها",
            command=self._phase49_3i33_bulk_run,
            style="Success.TButton",
        ).pack(side="right", padx=5)
        ttk.Label(
            panel,
            text="هر محصول جدا پردازش می‌شود؛ خطای یک محصول بقیه را متوقف نمی‌کند و کل لیست Refresh نمی‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

    def render_gallery(self):
        result = original_render(self) if callable(original_render) else None
        visible = list(getattr(self, "_phase49_3i29_visible_product_ids", []) or [])
        cards = list(getattr(self, "_phase49_3i_gallery_cards", []) or [])
        mapping = {}
        for product_id, card in zip(visible, cards):
            title_label = None
            image_label = None
            for child in card.winfo_children():
                if not isinstance(child, tk.Label):
                    continue
                try:
                    if int(child.cget("wraplength") or 0) > 0:
                        title_label = child
                    elif image_label is None:
                        image_label = child
                except Exception:
                    if image_label is None:
                        image_label = child
            mapping[int(product_id)] = {"card": card, "title": title_label, "image": image_label}
        self._phase49_3i33_card_map = mapping
        return result

    def update_product_card(self, product_id: int):
        slot = getattr(self, "_phase49_3i33_card_map", {}).get(int(product_id))
        if not slot:
            return False
        row = self.db.product(int(product_id))
        if row is None:
            return False
        title = str(row_value(row, "title_fa", "") or row_value(row, "source_title", "") or f"Product #{product_id}")
        try:
            if slot["title"] is not None:
                slot["title"].configure(text=title)
            slot["card"].configure(
                highlightbackground="white"
                if str(row_value(row, "server_id", "") or "").strip()
                else "#dbe3ea"
            )
        except Exception:
            pass
        try:
            from .phase49_3i_product_list import _card_photo, _local_thumbnail
            path = _local_thumbnail(row)
            if path is not None and slot["image"] is not None:
                photo = _card_photo(path)
                self._phase49_3i_gallery_photos[int(product_id)] = photo
                slot["image"].configure(image=photo, text="")
        except Exception:
            pass
        return True

    def selected_product_ids(self):
        ids = set()
        for name in ("_phase49_3i26_product_selection", "_phase49_3i_selected_products"):
            for item in getattr(self, name, set()) or set():
                try:
                    ids.add(int(item))
                except Exception:
                    pass
        return sorted(ids)

    def bulk_run(self):
        if getattr(self, "_phase49_3i33_bulk_busy", False):
            return
        ids = selected_product_ids(self)
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا چند محصول را از لیست انتخاب کن.", parent=self)
            return
        mode = AI_MODE_BY_LABEL.get(str(self._phase49_3i33_bulk_mode.get() or ""), "link")
        try:
            provider, key, model = active_ai_config(self, require_key=True)
        except Exception as exc:
            messagebox.showerror("تنظیمات هوش مصنوعی", str(exc), parent=self)
            return

        self._phase49_3i33_bulk_busy = True
        dialog = ObservableJobDialog(self, f"{AI_MODES[mode]} — {len(ids)} محصول")
        span = OperationTelemetry(f"bulk-ai-{mode}")

        def worker():
            ok = 0
            failed = 0
            try:
                for index, product_id in enumerate(ids, 1):
                    if dialog.cancelled.is_set():
                        break
                    dialog.event("product", f"{index}/{len(ids)} — محصول #{product_id}")
                    try:
                        result = run_ai_mode(self, product_id, mode, provider, key, model)
                        ok += 1
                        self._phase49_3i33_post_ui(
                            lambda pid=product_id: self._phase49_3i33_update_product_card(pid)
                        )
                        dialog.event("done", f"#{product_id}: {result.get('title_fa') or 'انجام شد'}")
                    except Exception as exc:
                        failed += 1
                        dialog.event("error", f"#{product_id}: {redact(exc)}")
                dialog.done(f"پایان — {ok} موفق • {failed} خطا • لیست کامل Refresh نشد")
                span.finish("ok" if failed == 0 else "partial", {"success": ok, "failed": failed, "count": len(ids)})
            except Exception as exc:
                span.finish("error", {"error": redact(exc)})
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_bulk_busy", False))

        threading.Thread(target=worker, daemon=True, name="catalog-3i33-bulk-ai").start()

    def no_auto_flush(self):
        return False

    app_class.__init__ = __init__
    if callable(original_modernize):
        app_class._modernize_products_page = modernize_products_page
    if callable(original_render):
        app_class._phase49_3i_render_gallery = render_gallery
    app_class._phase49_3i33_update_product_card = update_product_card
    app_class._phase49_3i33_post_ui = post_ui
    app_class._phase49_3i33_bulk_run = bulk_run
    app_class._phase49_3i29_flush_products_refresh = no_auto_flush
    app_class._phase49_3i33_operator_workflow = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i33_operator_workflow", False):
        return

    original_init = workspace_class.__init__
    original_save = workspace_class.save
    original_close = workspace_class.close
    original_gallery = workspace_class.refresh_gallery
    original_apply_thumbnail = workspace_class._apply_thumbnail
    original_pricing_state = getattr(workspace_class, "_phase49_3f_refresh_pricing_state", None)

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        row = app.db.product(int(product_id))
        self._phase49_3i33_quick_fixed_price = tk.StringVar(value=fixed_price_from_row(row))
        self._phase49_3i33_ai_busy = False
        hide_legacy_ai_buttons(self)
        install_quick_price(self)
        install_ai_panel(self)
        install_image_panel(self)
        install_final_panel(self)
        self.refresh_gallery()

    def install_quick_price(self):
        for widget in list(self.quick_tab.winfo_children()):
            try:
                row = int(widget.grid_info().get("row", -1))
            except Exception:
                continue
            if row in {3, 4}:
                hide_widget(widget)
        ttk.Label(
            self.quick_tab,
            text="قیمت قطعی فروش (تومان)",
            font=("Tahoma", 10, "bold"),
        ).grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(
            self.quick_tab,
            textvariable=self._phase49_3i33_quick_fixed_price,
        ).grid(row=3, column=1, sticky="ew", padx=6, pady=5)
        ttk.Label(
            self.quick_tab,
            text="فقط قیمت قطعی. وزن، نرخ متریال و قیمت پیشنهادی در مرحله «سفارش، قیمت و گزینه‌ها» مدیریت می‌شوند.",
            style="SubHeader.TLabel",
        ).grid(row=3, column=2, columnspan=2, sticky="w", padx=6, pady=5)

    def install_ai_panel(self):
        panel = ttk.LabelFrame(
            self.content_tab,
            text="مرکز هوش مصنوعی محصول — مسیرهای نهایی",
            padding=8,
            style="Card.TLabelframe",
        )
        children = list(self.content_tab.winfo_children())
        try:
            panel.pack(fill="x", pady=(0, 8), before=children[0] if children else None)
        except Exception:
            panel.pack(fill="x", pady=(0, 8))
        for mode in ("link", "data", "screenshot", "repair"):
            ttk.Button(
                panel,
                text=AI_MODES[mode],
                command=lambda selected=mode: self._phase49_3i33_run_ai(selected),
                style="Success.TButton" if mode == "link" else ("Warning.TButton" if mode == "repair" else "TButton"),
            ).pack(side="right", padx=4)
        ttk.Label(
            panel,
            text="متریال و رنگ به AI سپرده نمی‌شوند. هر مسیر متن فارسی، SEO و Metadata تصاویر منتخب را تکمیل می‌کند.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

    def install_image_panel(self):
        panel = ttk.LabelFrame(
            self.images_tab,
            text="مرجع صفحه محصول و مشخصات فایل تصاویر",
            padding=7,
            style="Card.TLabelframe",
        )
        children = list(self.images_tab.winfo_children())
        try:
            panel.pack(fill="x", pady=(0, 8), before=children[0] if children else None)
        except Exception:
            panel.pack(fill="x", pady=(0, 8))
        ttk.Button(
            panel,
            text="دریافت اسکرین‌شات از صفحه محصول",
            command=self._phase49_3i33_capture_screenshot,
            style="Primary.TButton",
        ).pack(side="right", padx=4)
        ttk.Label(
            panel,
            text="اسکرین‌شات مرجع به گالری محلی اضافه می‌شود و خودکار برای سایت انتخاب نمی‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

    def install_final_panel(self):
        panel = ttk.LabelFrame(
            self.publish_tab,
            text="ثبت نهایی Workspace",
            padding=7,
            style="Card.TLabelframe",
        )
        panel.pack(fill="x", pady=(8, 0))
        ttk.Button(
            panel,
            text="ثبت نهایی محصول و بروزرسانی همان کارت",
            command=self._phase49_3i33_final_commit,
            style="Success.TButton",
        ).pack(side="right", padx=4)
        ttk.Label(
            panel,
            text="ذخیره هر مرحله فقط SQLite محلی را ثبت می‌کند؛ لیست کامل فقط با Refresh دستی بازسازی می‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

    def pricing_state(self):
        result = original_pricing_state(self) if callable(original_pricing_state) else None
        variable = getattr(self, "_phase49_3i33_quick_fixed_price", None)
        mode_var = getattr(self, "pricing_strategy_var", None)
        if variable is not None and mode_var is not None:
            mode = str(mode_var.get() or "dynamic")
            if mode != "fixed":
                variable.set("")
            elif not str(variable.get() or "").strip():
                row = self.db.product(int(self.product_id))
                variable.set(fixed_price_from_row(row))
        return result

    def save(self, silent=False):
        fixed_text = str(self._phase49_3i33_quick_fixed_price.get() or "").replace(",", "").strip()
        if fixed_text:
            try:
                fixed = int(float(fixed_text))
            except Exception:
                if not silent:
                    messagebox.showwarning("3DPrintHub", "قیمت قطعی باید عدد معتبر تومان باشد.", parent=self)
                return False
            if fixed <= 0:
                if not silent:
                    messagebox.showwarning("3DPrintHub", "قیمت قطعی باید بیشتر از صفر باشد.", parent=self)
                return False
            self.final_price_var.set(str(fixed))
            if hasattr(self, "price_min_var"):
                self.price_min_var.set(str(fixed))
            if hasattr(self, "price_max_var"):
                self.price_max_var.set(str(fixed))
            if hasattr(self, "pricing_strategy_var"):
                self.pricing_strategy_var.set("fixed")
                refresh_state = getattr(self, "_phase49_3f_refresh_pricing_state", None)
                if callable(refresh_state):
                    refresh_state()

        span = OperationTelemetry("workspace-local-save", int(self.product_id))
        try:
            with suppress_global_products_refresh(self.app):
                result = original_save(self, silent=True)
            span.finish("ok" if result else "error")
        except Exception:
            span.finish("error")
            raise
        if result and not silent:
            self.footer_status.set("مرحله در دیتابیس محلی ثبت شد • لیست محصولات Refresh نشد")
        return result

    def close(self):
        with suppress_global_products_refresh(self.app):
            return original_close(self)

    def final_commit(self):
        if not self.save(silent=True):
            return False
        updater = getattr(self.app, "_phase49_3i33_update_product_card", None)
        if callable(updater):
            updater(int(self.product_id))
        self.footer_status.set("ثبت نهایی انجام شد • فقط کارت همین محصول بروزرسانی شد")
        return True

    def capture_screenshot_ui(self):
        if getattr(self, "_phase49_3i33_screenshot_busy", False):
            return
        self._phase49_3i33_screenshot_busy = True
        dialog = ObservableJobDialog(self, "دریافت اسکرین‌شات صفحه محصول")
        span = OperationTelemetry("source-screenshot", int(self.product_id))

        def worker():
            try:
                dialog.event("capture", "مرورگر در حال دریافت صفحه واقعی محصول است…")
                target = capture_source_screenshot(self.app, int(self.product_id))
                dialog.done(f"اسکرین‌شات ذخیره شد: {target.name}")
                span.finish("ok", {"bytes": target.stat().st_size})
                self.after(0, self.refresh_gallery)
            except Exception as exc:
                span.finish("error", {"error": redact(exc)})
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_screenshot_busy", False))

        threading.Thread(target=worker, daemon=True, name="catalog-3i33-screenshot").start()

    def run_ai_ui(self, mode: str):
        if self._phase49_3i33_ai_busy:
            self.footer_status.set("یک عملیات هوش مصنوعی در حال اجرا است.")
            return
        try:
            provider, key, model = active_ai_config(self.app, require_key=True)
        except Exception as exc:
            messagebox.showerror("تنظیمات هوش مصنوعی", str(exc), parent=self)
            return

        self._phase49_3i33_ai_busy = True
        dialog = ObservableJobDialog(self, AI_MODES.get(mode, "هوش مصنوعی"))
        span = OperationTelemetry(f"product-ai-{mode}", int(self.product_id))

        def worker():
            try:
                dialog.event("start", f"Provider={provider} • Model={model} • Mode={mode}")
                result = run_ai_mode(self.app, int(self.product_id), mode, provider, key, model)
                dialog.done(f"انجام شد: {result.get('title_fa') or ''}")
                span.finish("ok", {"mode": mode, "changed_fields": result.get("changed_fields")})

                def complete_ui():
                    self.reload()
                    updater = getattr(self.app, "_phase49_3i33_update_product_card", None)
                    if callable(updater):
                        updater(int(self.product_id))

                self.after(0, complete_ui)
            except Exception as exc:
                span.finish("error", {"mode": mode, "error": redact(exc)})
                dialog.fail(exc)
                self.after(0, lambda error=exc: self.footer_status.set(f"AI ناموفق: {redact(error)}"))
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_ai_busy", False))

        threading.Thread(target=worker, daemon=True, name=f"catalog-3i33-ai-{mode}").start()

    def apply_thumbnail(self, label, raw: bytes):
        try:
            import io
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            image.thumbnail((300, 220), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self._photos.append(photo)
            label.configure(image=photo, text="")
        except Exception:
            return original_apply_thumbnail(self, label, raw)

    def refresh_gallery(self):
        result = original_gallery(self)
        cards = list(getattr(self, "_gallery_cards", []) or [])
        for index, meta in enumerate(cards):
            label = meta.get("label")
            if label is None:
                continue
            try:
                card = label.master
                card.grid_configure(row=index // 3, column=index % 3, sticky="nsew", padx=7, pady=7)
                ttk.Label(
                    card,
                    text=image_file_info(str(meta.get("local") or ""), str(meta.get("url") or "")),
                    style="SubHeader.TLabel",
                    wraplength=235,
                    justify="center",
                ).pack(fill="x", pady=(3, 3))
            except Exception:
                pass
        try:
            for column in range(3):
                self.gallery_inner.columnconfigure(column, weight=1)
            self.gallery_inner.columnconfigure(3, weight=0)
        except Exception:
            pass
        return result

    def wrap_local_action(name: str):
        original = getattr(workspace_class, name, None)
        if not callable(original):
            return

        def local_action(self, *args, **kwargs):
            with suppress_global_products_refresh(self.app):
                result = original(self, *args, **kwargs)
            updater = getattr(self.app, "_phase49_3i33_update_product_card", None)
            if callable(updater) and result is not False:
                try:
                    updater(int(self.product_id))
                except Exception:
                    pass
            return result

        setattr(workspace_class, name, local_action)

    workspace_class.__init__ = __init__
    workspace_class.save = save
    if callable(original_pricing_state):
        workspace_class._phase49_3f_refresh_pricing_state = pricing_state
    workspace_class.close = close
    workspace_class.refresh_gallery = refresh_gallery
    workspace_class._apply_thumbnail = apply_thumbnail
    workspace_class._phase49_3i33_final_commit = final_commit
    workspace_class._phase49_3i33_capture_screenshot = capture_screenshot_ui
    workspace_class._phase49_3i33_run_ai = run_ai_ui

    for action_name in (
        "_persist_images",
        "queue_for_publish",
        "publish_to_local_computer",
        "publish_to_production_site",
    ):
        wrap_local_action(action_name)

    workspace_class._phase49_3i33_operator_workflow = True
