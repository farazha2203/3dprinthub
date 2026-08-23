from __future__ import annotations

import io
import re
import time
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageOps, ImageTk


CARD_VIEWPORT = (228, 171)
CARD_BACKGROUND = (246, 249, 252)


def classify_manual_url(url: str, model_pattern: str) -> str:
    value = str(url or "").strip()
    if not value.startswith(("http://", "https://")):
        return "invalid"
    pattern = str(model_pattern or "").strip()
    if pattern:
        try:
            if re.search(pattern, value, re.I):
                return "product"
        except re.error:
            return "invalid_pattern"
    return "page"


def fit_image_to_card(image: Image.Image, size: tuple[int, int] = CARD_VIEWPORT) -> Image.Image:
    """Contain the complete image inside one fixed pixel viewport without cropping."""
    width, height = int(size[0]), int(size[1])
    if width < 1 or height < 1:
        raise ValueError("Card viewport must be positive.")
    source = ImageOps.exif_transpose(image).convert("RGB")
    contained = ImageOps.contain(source, (width, height), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), CARD_BACKGROUND)
    left = max(0, (width - contained.width) // 2)
    top = max(0, (height - contained.height) // 2)
    canvas.paste(contained, (left, top))
    return canvas


def install_workspace(workspace_class) -> None:
    """Give every active Product Workspace gallery card the same pixel viewport."""
    if getattr(workspace_class, "_phase49_3i12_image_fit_installed", False):
        return

    def _apply_thumbnail(self, label, raw: bytes):
        try:
            if label is None or not bool(label.winfo_exists()):
                return
            image = Image.open(io.BytesIO(raw))
            fitted = fit_image_to_card(image)
            photo = ImageTk.PhotoImage(fitted)
            self._photos.append(photo)
            label.configure(image=photo, text="", anchor="center", padding=0)
        except Exception:
            try:
                if label is not None and bool(label.winfo_exists()):
                    label.configure(image="", text="فرمت تصویر قابل نمایش نیست")
            except Exception:
                pass

    workspace_class._apply_thumbnail = _apply_thumbnail
    workspace_class._phase49_3i12_image_fit_installed = True


def install_app(app_class, discovery_module) -> None:
    """Mount the Phase49.3I review UI at the real UX87 shell boundary.

    UX87 builds Discovery with ``super()._scan_ui()``. That bypasses a later
    App87 ``_scan_ui`` monkey-patch, so the Phase49.3I backend could scan the exact
    operator URL while its review panel was never visible. This installer wraps
    the final App87 ``_ui`` instead of duplicating the crawler.
    """
    if getattr(app_class, "_phase49_3i12_discovery_operator_installed", False):
        return

    original_ui = app_class._ui
    original_start_candidate = getattr(app_class, "start_candidate_discovery", None)
    original_direct = getattr(app_class, "start_direct_link_import", None)
    original_approve = getattr(app_class, "approve_discovery_candidates", None)

    def _walk(root):
        for child in root.winfo_children():
            yield child
            yield from _walk(child)

    def _set_state(self, state: str, text: str, detail: str = ""):
        colors = {
            "idle": ("#64748b", "#ffffff"),
            "active": ("#2563eb", "#ffffff"),
            "stop": ("#d97706", "#ffffff"),
            "done": ("#15803d", "#ffffff"),
            "error": ("#b91c1c", "#ffffff"),
        }
        bg, fg = colors.get(state, colors["idle"])
        badge = getattr(self, "_phase49_3i12_badge", None)
        if badge is not None:
            try:
                badge.configure(text=text, bg=bg, fg=fg)
            except Exception:
                pass
        var = getattr(self, "_phase49_3i12_detail", None)
        if var is not None:
            try:
                var.set(detail)
            except Exception:
                pass
        bar = getattr(self, "_phase49_3i12_progress", None)
        if bar is not None:
            try:
                if state == "active":
                    bar.start(12)
                else:
                    bar.stop()
            except Exception:
                pass

    def _latest_preview_result(self, source_code: str) -> str:
        try:
            for row in self.db.runs():
                if str(row["source_code"] or "") != str(source_code or ""):
                    continue
                if str(row["mode"] or "") != "preview":
                    continue
                return (
                    f"کاندیدا: {int(row['discovered_count'] or 0)} | "
                    f"خطا: {int(row['failed_count'] or 0)} | "
                    f"وضعیت: {row['status']}"
                )
        except Exception:
            pass
        return "نتیجه در لیست کاندیداها بروزرسانی شد."

    def _monitor_run(self, token: int):
        if int(getattr(self, "_phase49_3i12_run_token", 0) or 0) != int(token):
            return
        started = float(getattr(self, "_phase49_3i12_started", time.monotonic()))
        elapsed = max(0, int(time.monotonic() - started))
        elapsed_var = getattr(self, "_phase49_3i12_elapsed", None)
        if elapsed_var is not None:
            elapsed_var.set(f"زمان: {elapsed}s")

        if bool(getattr(self, "scan_running", False)):
            mode = str(getattr(self, "_phase49_3i12_run_kind", "page"))
            url = str(getattr(self, "_phase49_3i12_run_url", ""))
            stop_requested = bool(getattr(self, "_phase49_3i12_stop_requested", False))
            if stop_requested:
                _set_state(
                    self,
                    "stop",
                    "● درخواست توقف ثبت شد",
                    f"عملیات جاری در امن‌ترین نقطه متوقف می‌شود | {url}",
                )
            elif mode == "page":
                _set_state(
                    self,
                    "active",
                    "● در حال کشف لینک‌های صفحه",
                    f"مرورگر در حال بازکردن/اسکرول/خواندن همان URL است | {url}",
                )
            elif mode == "single":
                _set_state(
                    self,
                    "active",
                    "● در حال دریافت محصول تکی",
                    f"استخراج کامل همان Product URL در حال اجرا است | {url}",
                )
            else:
                _set_state(
                    self,
                    "active",
                    "● در حال دریافت کامل انتخاب‌شده‌ها",
                    "فقط کاندیداهای تأییدشده در حال Full Fetch هستند.",
                )
            self.after(500, lambda t=token: _monitor_run(self, t))
            return

        try:
            if hasattr(self, "refresh_discovery_candidates"):
                self.refresh_discovery_candidates()
        except Exception:
            pass
        kind = str(getattr(self, "_phase49_3i12_run_kind", ""))
        stopped = bool(getattr(self, "_phase49_3i12_stop_requested", False))
        if stopped:
            _set_state(self, "stop", "● عملیات متوقف/پایان یافت", "برای اجرای جدید دوباره دکمه موردنظر را بزنید.")
        elif kind == "page":
            source_code = str(getattr(self, "_phase49_3i12_source_code", ""))
            _set_state(self, "done", "● کشف صفحه پایان یافت", _latest_preview_result(self, source_code))
        elif kind == "single":
            _set_state(self, "done", "● دریافت محصول تکی پایان یافت", "محصول در بخش محصولات قابل بررسی است.")
        else:
            _set_state(self, "done", "● دریافت کامل پایان یافت", "نتیجه کاندیداهای تأییدشده بروزرسانی شد.")

    def _begin_monitor(self, kind: str, url: str):
        token = int(getattr(self, "_phase49_3i12_run_token", 0) or 0) + 1
        self._phase49_3i12_run_token = token
        self._phase49_3i12_run_kind = kind
        self._phase49_3i12_run_url = url
        self._phase49_3i12_started = time.monotonic()
        self._phase49_3i12_stop_requested = False
        if hasattr(self, "_phase49_3i12_elapsed"):
            self._phase49_3i12_elapsed.set("زمان: 0s")
        _set_state(self, "active", "● شروع عملیات", url)
        self.after(150, lambda t=token: _monitor_run(self, t))

    def _source_contract(self):
        code = self.source_map.get(self.source_var.get().strip(), self.source_var.get().strip())
        src = self.db.source(code)
        pattern = str(src["model_url_pattern"] or "") if src is not None else ""
        return code, src, pattern

    def start_exact_page_discovery(self):
        if bool(getattr(self, "scan_running", False)):
            _set_state(self, "active", "● یک عملیات در حال اجرا است", "ابتدا همان عملیات را متوقف یا تمام کنید.")
            return None
        url = self.seed_var.get().strip()
        code, src, pattern = _source_contract(self)
        if src is None:
            messagebox.showwarning("3DPrintHub", "ابتدا یک منبع معتبر انتخاب کنید.", parent=self)
            return None
        kind = classify_manual_url(url, pattern)
        if kind == "invalid":
            messagebox.showwarning("3DPrintHub", "یک URL کامل http/https وارد کنید.", parent=self)
            return None
        if kind == "invalid_pattern":
            messagebox.showerror("3DPrintHub", "Regex تشخیص Product URL برای این منبع معتبر نیست.", parent=self)
            return None
        if kind == "product":
            messagebox.showinfo(
                "3DPrintHub",
                "این URL یک محصول تکی است. برای آن از «دریافت محصول تکی» استفاده کنید؛ کشف صفحه فقط لینک‌های داخل Search/Listing/Category را Preview می‌کند.",
                parent=self,
            )
            return None
        self.mode_var.set("search")
        self._phase49_3i12_source_code = code
        _begin_monitor(self, "page", url)
        if callable(original_start_candidate):
            result = original_start_candidate(self)
            if not bool(getattr(self, "scan_running", False)):
                self.after(0, lambda t=self._phase49_3i12_run_token: _monitor_run(self, t))
            return result
        return None

    def start_single_product_manual(self):
        if bool(getattr(self, "scan_running", False)):
            _set_state(self, "active", "● یک عملیات در حال اجرا است", "ابتدا همان عملیات را متوقف یا تمام کنید.")
            return None
        url = self.seed_var.get().strip()
        code, src, pattern = _source_contract(self)
        if src is None:
            messagebox.showwarning("3DPrintHub", "ابتدا یک منبع معتبر انتخاب کنید.", parent=self)
            return None
        kind = classify_manual_url(url, pattern)
        if kind != "product":
            messagebox.showwarning(
                "3DPrintHub",
                "این URL مطابق Product URL همین منبع نیست. اگر Search/Listing/Category است از «کشف لینک‌های همین صفحه» استفاده کنید.",
                parent=self,
            )
            return None
        self.mode_var.set("single")
        self._phase49_3i12_source_code = code
        _begin_monitor(self, "single", url)
        if callable(original_direct):
            result = original_direct(self)
            if not bool(getattr(self, "scan_running", False)):
                self.after(0, lambda t=self._phase49_3i12_run_token: _monitor_run(self, t))
            return result
        return None

    def request_discovery_stop(self):
        if not bool(getattr(self, "scan_running", False)):
            _set_state(self, "idle", "● عملیات فعالی وجود ندارد", "")
            return None
        self.stop_requested = True
        self._phase49_3i12_stop_requested = True
        _set_state(
            self,
            "stop",
            "● درخواست توقف ثبت شد",
            "Worker اجباری Kill نمی‌شود؛ در امن‌ترین نقطه خروج می‌کند و نتیجه ناقص اعمال نمی‌شود.",
        )
        return None

    def approve_discovery_candidates(self):
        if bool(getattr(self, "scan_running", False)):
            _set_state(self, "active", "● یک عملیات در حال اجرا است", "قبل از Full Fetch منتظر پایان عملیات جاری بمانید.")
            return None
        selected = ()
        tree = getattr(self, "discovery_candidate_tree", None)
        if tree is not None:
            try:
                selected = tree.selection()
            except Exception:
                selected = ()
        _begin_monitor(self, "full", f"selected={len(selected)}")
        if callable(original_approve):
            result = original_approve(self)
            if not bool(getattr(self, "scan_running", False)):
                self.after(0, lambda t=self._phase49_3i12_run_token: _monitor_run(self, t))
            return result
        return None

    def _mount_operator_ui(self):
        scan_tab = getattr(self, "scan_tab", None)
        scan_log = getattr(self, "scan_log", None)
        if scan_tab is None or scan_log is None or getattr(self, "_phase49_3i12_operator_frame", None) is not None:
            return

        hidden = {
            "شروع اسکن",
            "توقف محترمانه",
            "دریافت هوشمند از لینک",
            "🔎 کشف جدیدها",
            "کشف جدیدها",
        }
        for widget in list(_walk(scan_tab)):
            if not isinstance(widget, ttk.Button):
                continue
            try:
                if str(widget.cget("text")) in hidden:
                    manager = widget.winfo_manager()
                    if manager == "pack":
                        widget.pack_forget()
                    elif manager == "grid":
                        widget.grid_remove()
            except Exception:
                pass

        try:
            scan_log.pack_forget()
            scan_log.configure(height=8, wrap="word")
        except Exception:
            pass

        operator = ttk.LabelFrame(
            scan_tab,
            text="دریافت دستی و وضعیت زنده",
            padding=8,
            style="Card.TLabelframe",
        )
        operator.pack(fill="x", pady=(5, 7))
        self._phase49_3i12_operator_frame = operator
        operator.columnconfigure(1, weight=1)

        ttk.Label(operator, text="URL دقیق").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=3)
        ttk.Entry(operator, textvariable=self.seed_var).grid(row=0, column=1, sticky="ew", padx=4, pady=3)
        actions = ttk.Frame(operator)
        actions.grid(row=0, column=2, sticky="e", padx=(6, 0))
        ttk.Button(
            actions,
            text="کشف لینک‌های همین صفحه",
            command=self.start_exact_page_discovery,
            style="Success.TButton",
        ).pack(side="left", padx=2)
        ttk.Button(
            actions,
            text="دریافت محصول تکی",
            command=self.start_single_product_manual,
            style="Primary.TButton",
        ).pack(side="left", padx=2)
        ttk.Button(actions, text="توقف", command=self.request_discovery_stop, style="Warning.TButton").pack(side="left", padx=2)

        status_row = ttk.Frame(operator)
        status_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 1))
        status_row.columnconfigure(2, weight=1)
        self._phase49_3i12_badge = tk.Label(
            status_row,
            text="● آماده",
            bg="#64748b",
            fg="#ffffff",
            padx=10,
            pady=4,
            font=("Tahoma", 9, "bold"),
        )
        self._phase49_3i12_badge.grid(row=0, column=0, sticky="w")
        self._phase49_3i12_elapsed = tk.StringVar(value="زمان: 0s")
        ttk.Label(status_row, textvariable=self._phase49_3i12_elapsed).grid(row=0, column=1, sticky="w", padx=8)
        self._phase49_3i12_detail = tk.StringVar(value="لینک صفحه را بده یا Product URL تکی وارد کن.")
        ttk.Label(status_row, textvariable=self._phase49_3i12_detail, style="SubHeader.TLabel", wraplength=780).grid(row=0, column=2, sticky="ew", padx=6)
        self._phase49_3i12_progress = ttk.Progressbar(status_row, mode="indeterminate", length=180)
        self._phase49_3i12_progress.grid(row=0, column=3, sticky="e", padx=(8, 0))

        review = ttk.LabelFrame(
            scan_tab,
            text="کاندیداهای همین صفحه — Preview فقط عنوان/شناسه/یک تصویر",
            padding=7,
            style="Card.TLabelframe",
        )
        review.pack(fill="both", expand=True, pady=(0, 6))
        toolbar = ttk.Frame(review)
        toolbar.pack(fill="x", pady=(0, 5))
        ttk.Button(toolbar, text="دریافت کامل انتخاب‌شده‌ها", command=self.approve_discovery_candidates, style="Success.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="آرشیو / لازم نیست", command=self.archive_discovery_candidates, style="Warning.TButton").pack(side="left", padx=2)
        ttk.Button(toolbar, text="باز کردن لینک انتخابی", command=self.open_discovery_candidate_url).pack(side="left", padx=2)
        ttk.Button(toolbar, text="تازه‌سازی کاندیداها", command=self.refresh_discovery_candidates).pack(side="left", padx=2)
        self._phase49_3i12_candidate_summary = tk.StringVar(value="")
        ttk.Label(toolbar, textvariable=self._phase49_3i12_candidate_summary, style="SubHeader.TLabel").pack(side="right", padx=4)

        columns = ("thumb", "status", "title", "source", "external", "url")
        tree = ttk.Treeview(review, columns=columns, show="headings", selectmode="extended", height=7)
        tree.heading("thumb", text="عکس")
        tree.heading("status", text="وضعیت")
        tree.heading("title", text="عنوان Preview")
        tree.heading("source", text="منبع")
        tree.heading("external", text="ID")
        tree.heading("url", text="URL")
        tree.column("thumb", width=86, minwidth=86, stretch=False, anchor="center")
        tree.column("status", width=110, minwidth=90, stretch=False, anchor="center")
        tree.column("title", width=330, minwidth=220, stretch=True, anchor="w")
        tree.column("source", width=100, minwidth=90, stretch=False, anchor="center")
        tree.column("external", width=115, minwidth=95, stretch=False, anchor="center")
        tree.column("url", width=430, minwidth=260, stretch=True, anchor="w")
        style = ttk.Style(self)
        style.configure("Phase493I12Candidate.Treeview", rowheight=72)
        tree.configure(style="Phase493I12Candidate.Treeview")
        ybar = ttk.Scrollbar(review, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(review, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.pack(side="left", fill="both", expand=True)
        ybar.pack(side="right", fill="y")
        xbar.pack(side="bottom", fill="x")
        tree.bind("<Double-1>", lambda _event: self.open_discovery_candidate_url())
        self.discovery_candidate_tree = tree
        self._phase49_3i_candidate_photos = {}
        self._phase49_3i_thumb_loading = set()

        try:
            scan_log.pack(fill="x", expand=False, pady=(3, 0))
        except Exception:
            pass
        try:
            self.refresh_discovery_candidates()
            rows = tree.get_children()
            self._phase49_3i12_candidate_summary.set(f"نمایش: {len(rows)}")
        except Exception:
            pass

    def _ui(self):
        result = original_ui(self)
        self._mount_phase49_3i12_operator_ui()
        return result

    app_class._ui = _ui
    app_class._mount_phase49_3i12_operator_ui = _mount_operator_ui
    app_class._phase49_3i12_set_state = _set_state
    app_class._phase49_3i12_monitor_run = _monitor_run
    app_class.start_exact_page_discovery = start_exact_page_discovery
    app_class.start_single_product_manual = start_single_product_manual
    app_class.request_discovery_stop = request_discovery_stop
    app_class.approve_discovery_candidates = approve_discovery_candidates
    app_class._phase49_3i12_discovery_operator_installed = True
