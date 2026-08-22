from __future__ import annotations

import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageOps, ImageTk

from .phase49_3i_discovery_review import is_http_url
from .phase49_3i_product_list import _local_thumbnail
from .workflow import STATUS_LABELS, image_count, product_state


VIEW_MODES = {
    "extra_large": {
        "label": "آیکن خیلی بزرگ",
        "thumb": (320, 235),
        "card": (348, 382),
    },
    "large": {
        "label": "آیکن بزرگ",
        "thumb": (260, 190),
        "card": (288, 338),
    },
    "medium": {
        "label": "آیکن متوسط",
        "thumb": (180, 132),
        "card": (208, 292),
    },
    "small": {
        "label": "آیکن کوچک",
        "thumb": (120, 88),
        "card": (164, 254),
    },
    "list": {
        "label": "لیست",
        "thumb": (82, 62),
        "card": (760, 104),
    },
}
DEFAULT_VIEW_MODE = "large"
VIEW_SETTING_KEY = "phase49_3i_product_view_mode"

FILTER_OPTIONS = (
    ("work_queue", "کارهای من"),
    ("new", "جدید"),
    ("needs_update", "نیازمند بروزرسانی"),
    ("without_images", "بدون تصویر"),
    ("without_content", "بدون محتوا"),
    ("ready", "آماده انتشار"),
    ("upload_queue", "صف انتشار"),
    ("published", "منتشرشده"),
    ("error", "خطادار"),
    ("all", "همه محصولات"),
)

SORT_OPTIONS = (
    ("priority", "اولویت کاری"),
    ("newest", "جدیدترین"),
    ("oldest", "قدیمی‌ترین"),
    ("updated", "آخرین بروزرسانی"),
    ("rating", "بیشترین امتیاز"),
    ("downloads", "بیشترین دانلود"),
)


def normalize_view_mode(value: str) -> str:
    key = str(value or "").strip().lower()
    return key if key in VIEW_MODES else DEFAULT_VIEW_MODE


def _option_label(options, key: str, fallback: str) -> str:
    key = str(key or "").strip()
    return next((label for value, label in options if value == key), fallback)


def _option_key(options, label: str, fallback: str) -> str:
    label = str(label or "").strip()
    return next((value for value, item_label in options if item_label == label), fallback)


def matches_source_product_url(url: str, model_pattern: str) -> bool:
    """Return True only when a source's own product regex matches the URL."""
    if not is_http_url(url):
        return False
    pattern = str(model_pattern or "").strip()
    if not pattern:
        return False
    try:
        return bool(re.search(pattern, str(url).strip(), flags=re.I))
    except re.error:
        return False


def _row_value(row, key: str, default=""):
    try:
        return row[key]
    except Exception:
        return default


def product_card_metadata(row, date_formatter=None) -> tuple[str, str]:
    """Compact operator metadata; Product Workspace remains the detailed editor."""
    product_id = int(_row_value(row, "id", 0) or 0)
    state = product_state(row)
    status = STATUS_LABELS.get(state, state or "نامشخص")
    source = str(_row_value(row, "source_name", "") or _row_value(row, "source_code", "") or "منبع نامشخص")
    images = image_count(row)

    created_raw = str(_row_value(row, "created_at", "") or "")
    if callable(date_formatter):
        try:
            created = str(date_formatter(created_raw) or created_raw)
        except Exception:
            created = created_raw
    else:
        created = created_raw[:10]
    created = created or "—"

    if state == "published":
        publish_label = "منتشرشده"
    elif state == "queued":
        publish_label = "در صف انتشار"
    elif state == "ready":
        publish_label = "آماده انتشار"
    elif state == "needs_update":
        publish_label = "نیازمند بروزرسانی"
    elif state == "error":
        publish_label = "خطای انتشار/همگام‌سازی"
    else:
        publish_label = "در حال تکمیل"

    line_one = f"#{product_id} • {status} • {source} • {images} عکس"
    line_two = f"افزوده: {created} • {publish_label}"
    return line_one, line_two


def _photo_for_size(path: Path, size: tuple[int, int]):
    width, height = size
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (width, height), "white")
        x = max(0, (width - image.width) // 2)
        y = max(0, (height - image.height) // 2)
        canvas.paste(image, (x, y))
    return ImageTk.PhotoImage(canvas)


def install(app_class) -> None:
    """Add Explorer browsing while preserving mature Catalog and Workspace flows."""
    if getattr(app_class, "_phase49_3i_explorer_hotfix_installed", False):
        return

    original_modernize = app_class._modernize_products_page
    original_direct_link = app_class.start_direct_link_import
    original_refresh_products = app_class.refresh_products

    def _hide_legacy_raw_filter_bar(self):
        filter_var = str(getattr(self, "product_filter", ""))
        sort_var = str(getattr(self, "product_sort", ""))
        for child in self.products_tab.winfo_children():
            if not isinstance(child, ttk.Frame):
                continue
            combo_vars = set()
            for widget in child.winfo_children():
                if not isinstance(widget, ttk.Combobox):
                    continue
                try:
                    combo_vars.add(str(widget.cget("textvariable") or ""))
                except Exception:
                    pass
            if filter_var in combo_vars or sort_var in combo_vars:
                try:
                    child.pack_forget()
                except Exception:
                    try:
                        child.grid_remove()
                    except Exception:
                        pass

    def _modernize_products_page(self):
        original_modernize(self)

        self._phase49_3i_selected_products = set()
        self._phase49_3i_last_selected_id = None
        self._phase49_3i_product_order = []
        self._phase49_3i_gallery_card_by_id = {}
        self._phase49_3i_syncing_tree_selection = False
        self._phase49_3i_opening_product = False
        self._phase49_3i_gallery_mode = normalize_view_mode(
            self.db.setting(VIEW_SETTING_KEY, DEFAULT_VIEW_MODE)
        )

        self._hide_legacy_raw_filter_bar()

        shell = getattr(getattr(self, "_phase49_3i_gallery_canvas", None), "master", None)
        toolbar = ttk.Frame(self.products_tab)
        if shell is not None:
            toolbar.pack(fill="x", pady=(0, 7), before=shell)
        else:
            toolbar.pack(fill="x", pady=(0, 7))

        ttk.Label(toolbar, text="فیلتر:").pack(side="right", padx=(6, 2))
        current_filter = str(getattr(self, "product_filter", tk.StringVar(value="work_queue")).get() or "work_queue")
        self._phase49_3i_filter_label = tk.StringVar(
            value=_option_label(FILTER_OPTIONS, current_filter, "کارهای من")
        )
        filter_combo = ttk.Combobox(
            toolbar,
            textvariable=self._phase49_3i_filter_label,
            values=[label for _key, label in FILTER_OPTIONS],
            state="readonly",
            width=19,
        )
        filter_combo.pack(side="right", padx=3)
        filter_combo.bind("<<ComboboxSelected>>", self._phase49_3i_change_filter)

        ttk.Label(toolbar, text="جستجو:").pack(side="right", padx=(8, 2))
        search = ttk.Entry(toolbar, textvariable=self.product_search, width=22)
        search.pack(side="right", padx=3)
        search.bind("<Return>", lambda _event: self.refresh_products())

        ttk.Label(toolbar, text="مرتب‌سازی:").pack(side="right", padx=(8, 2))
        current_sort = str(getattr(self, "product_sort", tk.StringVar(value="priority")).get() or "priority")
        self._phase49_3i_sort_label = tk.StringVar(
            value=_option_label(SORT_OPTIONS, current_sort, "اولویت کاری")
        )
        sort_combo = ttk.Combobox(
            toolbar,
            textvariable=self._phase49_3i_sort_label,
            values=[label for _key, label in SORT_OPTIONS],
            state="readonly",
            width=18,
        )
        sort_combo.pack(side="right", padx=3)
        sort_combo.bind("<<ComboboxSelected>>", self._phase49_3i_change_sort)

        ttk.Label(toolbar, text="نمایش:").pack(side="right", padx=(8, 2))
        labels = [VIEW_MODES[key]["label"] for key in VIEW_MODES]
        current_label = VIEW_MODES[self._phase49_3i_gallery_mode]["label"]
        self._phase49_3i_view_label = tk.StringVar(value=current_label)
        view_combo = ttk.Combobox(
            toolbar,
            textvariable=self._phase49_3i_view_label,
            values=labels,
            state="readonly",
            width=16,
        )
        view_combo.pack(side="right", padx=3)
        view_combo.bind("<<ComboboxSelected>>", self._phase49_3i_change_view)

        ttk.Button(toolbar, text="بروزرسانی", command=self.refresh_products).pack(side="right", padx=4)
        ttk.Button(toolbar, text="انتخاب همه", command=self._phase49_3i_select_all_products).pack(side="left", padx=3)
        ttk.Button(toolbar, text="لغو انتخاب", command=self._phase49_3i_clear_selection).pack(side="left", padx=3)
        self._phase49_3i_selected_count = tk.StringVar(value="0 انتخاب")
        ttk.Label(toolbar, textvariable=self._phase49_3i_selected_count).pack(side="left", padx=10)

        self._phase49_3i_context_menu = tk.Menu(self, tearoff=False)
        self.after_idle(self._phase49_3i_render_gallery)

    def _phase49_3i_current_view(self):
        return VIEW_MODES[normalize_view_mode(getattr(self, "_phase49_3i_gallery_mode", DEFAULT_VIEW_MODE))]

    def _phase49_3i_change_filter(self, _event=None):
        key = _option_key(FILTER_OPTIONS, self._phase49_3i_filter_label.get(), "work_queue")
        self.product_filter.set(key)
        self.refresh_products()

    def _phase49_3i_change_sort(self, _event=None):
        key = _option_key(SORT_OPTIONS, self._phase49_3i_sort_label.get(), "priority")
        self.product_sort.set(key)
        self.refresh_products()

    def _phase49_3i_change_view(self, _event=None):
        label = str(getattr(self, "_phase49_3i_view_label", tk.StringVar()).get() or "")
        key = next((name for name, cfg in VIEW_MODES.items() if cfg["label"] == label), DEFAULT_VIEW_MODE)
        self._phase49_3i_gallery_mode = key
        self.db.set_setting(VIEW_SETTING_KEY, key)
        self._phase49_3i_gallery_resize(
            getattr(getattr(self, "_phase49_3i_gallery_canvas", None), "winfo_width", lambda: 900)()
        )
        self._phase49_3i_render_gallery()

    def _phase49_3i_gallery_resize(self, width: int):
        canvas = getattr(self, "_phase49_3i_gallery_canvas", None)
        if canvas is None:
            return
        width = max(300, int(width or 0))
        try:
            canvas.itemconfigure(self._phase49_3i_gallery_window, width=width)
        except Exception:
            pass
        view = self._phase49_3i_current_view()
        if getattr(self, "_phase49_3i_gallery_mode", DEFAULT_VIEW_MODE) == "list":
            columns = 1
        else:
            columns = max(1, width // (int(view["card"][0]) + 18))
        if columns != getattr(self, "_phase49_3i_gallery_columns", 1):
            self._phase49_3i_gallery_columns = columns
            self._phase49_3i_layout_cards()

    def _phase49_3i_layout_cards(self):
        inner = getattr(self, "_phase49_3i_gallery_inner", None)
        if inner is None:
            return
        columns = max(1, int(getattr(self, "_phase49_3i_gallery_columns", 1)))
        mode = getattr(self, "_phase49_3i_gallery_mode", DEFAULT_VIEW_MODE)
        for col in range(max(columns, 1)):
            try:
                inner.columnconfigure(col, weight=1, uniform="phase49_3i_product_card")
            except Exception:
                pass
        for index, card in enumerate(list(getattr(self, "_phase49_3i_gallery_cards", []) or [])):
            try:
                card.grid_forget()
                if mode == "list":
                    card.grid(row=index, column=0, sticky="ew", padx=8, pady=4)
                else:
                    card.grid(row=index // columns, column=index % columns, sticky="n", padx=8, pady=8)
            except Exception:
                pass

    def _phase49_3i_update_selection_visuals(self):
        selected = set(getattr(self, "_phase49_3i_selected_products", set()) or set())
        cards = dict(getattr(self, "_phase49_3i_gallery_card_by_id", {}) or {})
        for product_id, card in cards.items():
            try:
                if product_id in selected:
                    card.configure(highlightbackground="#2563eb", highlightthickness=2)
                else:
                    card.configure(highlightbackground="#dbe3ea", highlightthickness=1)
            except Exception:
                pass
        count_var = getattr(self, "_phase49_3i_selected_count", None)
        if count_var is not None:
            count_var.set(f"{len(selected)} انتخاب")

    def _phase49_3i_select_product(self, product_id: int):
        """One-way card -> hidden Treeview sync with a re-entrancy guard."""
        product_id = int(product_id)
        self.current_product = product_id
        tree = getattr(self, "product_tree", None)
        iid = str(product_id)
        if tree is not None and tree.exists(iid):
            try:
                current = tuple(str(item) for item in tree.selection())
            except Exception:
                current = ()
            if current != (iid,):
                self._phase49_3i_syncing_tree_selection = True
                try:
                    tree.selection_set(iid)
                    tree.focus(iid)
                finally:
                    self._phase49_3i_syncing_tree_selection = False
        if hasattr(self, "status"):
            self.status.set(f"محصول #{product_id} انتخاب شد")

    def load_product(self, _event=None):
        """Hidden Treeview -> card state is one-way; never selection_set again."""
        if getattr(self, "_phase49_3i_syncing_tree_selection", False):
            return
        tree = getattr(self, "product_tree", None)
        selection = tree.selection() if tree is not None else ()
        if not selection:
            return
        try:
            product_id = int(selection[0])
        except Exception:
            return
        self.current_product = product_id
        if hasattr(self, "_phase49_3i_selected_products"):
            self._phase49_3i_selected_products = {product_id}
            self._phase49_3i_last_selected_id = product_id
            self._phase49_3i_update_selection_visuals()
        if hasattr(self, "status"):
            self.status.set(f"محصول #{product_id} انتخاب شد")

    def _phase49_3i_open_product(self, product_id: int):
        """Prevent repeated open clicks and yield one Tk frame before Workspace construction."""
        product_id = int(product_id)
        if getattr(self, "_phase49_3i_opening_product", False):
            return
        self._phase49_3i_select_product(product_id)
        self._phase49_3i_opening_product = True
        if hasattr(self, "status"):
            self.status.set(f"در حال باز کردن محصول #{product_id}...")
        try:
            self.update_idletasks()
        except Exception:
            pass

        def open_now():
            try:
                self.open_product_studio(product_id)
            finally:
                self._phase49_3i_opening_product = False
                if hasattr(self, "status"):
                    self.status.set(f"محصول #{product_id} باز شد")

        self.after(20, open_now)

    def _phase49_3i_select_click(self, event, product_id: int, *, preview: bool = False):
        product_id = int(product_id)
        state = int(getattr(event, "state", 0) or 0)
        ctrl = bool(state & 0x0004)
        shift = bool(state & 0x0001)
        selected = set(getattr(self, "_phase49_3i_selected_products", set()) or set())
        order = list(getattr(self, "_phase49_3i_product_order", []) or [])
        last = getattr(self, "_phase49_3i_last_selected_id", None)

        if shift and last in order and product_id in order:
            start, end = sorted((order.index(last), order.index(product_id)))
            range_ids = set(order[start : end + 1])
            selected = (selected | range_ids) if ctrl else range_ids
        elif ctrl:
            if product_id in selected:
                selected.remove(product_id)
            else:
                selected.add(product_id)
        else:
            selected = {product_id}

        self._phase49_3i_selected_products = selected
        self._phase49_3i_last_selected_id = product_id
        self._phase49_3i_select_product(product_id)
        self._phase49_3i_update_selection_visuals()

        if preview and not ctrl and not shift:
            self._phase49_3i_open_image_preview(product_id)
        return "break"

    def _phase49_3i_select_all_products(self):
        self._phase49_3i_selected_products = set(getattr(self, "_phase49_3i_product_order", []) or [])
        self._phase49_3i_update_selection_visuals()

    def _phase49_3i_clear_selection(self):
        self._phase49_3i_selected_products = set()
        self._phase49_3i_last_selected_id = None
        self._phase49_3i_update_selection_visuals()

    def _phase49_3i_remove_selected_from_publish_queue(self):
        ids = sorted(set(getattr(self, "_phase49_3i_selected_products", set()) or set()))
        if not ids:
            return
        if not messagebox.askyesno(
            "حذف از صف انتشار",
            f"{len(ids)} محصول از صف انتشار محلی خارج شود؟\n\nاین کار محصول را حذف نمی‌کند و چیزی را از سایت Production پاک نمی‌کند.",
            parent=self,
        ):
            return
        for product_id in ids:
            self.db.update_product(int(product_id), {"upload_ready": 0, "workflow_status": "review"})
        if hasattr(self, "refresh_upload_queue"):
            self.refresh_upload_queue()
        self.refresh_products()
        if hasattr(self, "status"):
            self.status.set(f"{len(ids)} محصول از صف انتشار محلی خارج شد")

    def _phase49_3i_show_context_menu(self, event, product_id: int):
        product_id = int(product_id)
        selected = set(getattr(self, "_phase49_3i_selected_products", set()) or set())
        if product_id not in selected:
            self._phase49_3i_selected_products = {product_id}
            self._phase49_3i_last_selected_id = product_id
            self._phase49_3i_select_product(product_id)
            self._phase49_3i_update_selection_visuals()
            selected = {product_id}

        menu = getattr(self, "_phase49_3i_context_menu", None)
        if menu is None:
            return "break"
        menu.delete(0, "end")
        menu.add_command(label="باز کردن محصول", command=lambda: self._phase49_3i_open_product(product_id))
        menu.add_command(label="پیش‌نمایش تصویر", command=lambda: self._phase49_3i_open_image_preview(product_id))
        menu.add_separator()
        menu.add_command(
            label=f"حذف از صف انتشار ({len(selected)})",
            command=self._phase49_3i_remove_selected_from_publish_queue,
        )
        menu.add_separator()
        menu.add_command(label="انتخاب همه", command=self._phase49_3i_select_all_products)
        menu.add_command(label="لغو انتخاب", command=self._phase49_3i_clear_selection)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return "break"

    def _phase49_3i_bind_selectable(self, widget, product_id: int, *, preview: bool = False):
        widget.bind(
            "<Button-1>",
            lambda event, pid=product_id, do_preview=preview: self._phase49_3i_select_click(
                event, pid, preview=do_preview
            ),
        )
        widget.bind(
            "<Button-3>",
            lambda event, pid=product_id: self._phase49_3i_show_context_menu(event, pid),
        )

    def _phase49_3i_apply_post_sort(self):
        if str(getattr(self, "product_sort", tk.StringVar(value="priority")).get() or "") != "oldest":
            return
        tree = getattr(self, "product_tree", None)
        if tree is None:
            return
        items = list(tree.get_children())

        def created_key(iid):
            try:
                row = self.db.product(int(iid))
                return str(row["created_at"] or "") if row is not None else ""
            except Exception:
                return ""

        items.sort(key=created_key)
        for index, iid in enumerate(items):
            try:
                tree.move(iid, "", index)
            except Exception:
                pass

    def refresh_products(self):
        result = original_refresh_products(self)
        self._phase49_3i_apply_post_sort()
        if hasattr(self, "_update_dashboard"):
            self._update_dashboard()
        if hasattr(self, "_refresh_ux87_dashboard"):
            self._refresh_ux87_dashboard()
        return result

    def _phase49_3i_render_gallery(self):
        inner = getattr(self, "_phase49_3i_gallery_inner", None)
        tree = getattr(self, "product_tree", None)
        if inner is None or tree is None:
            return

        self._phase49_3i_gallery_load_generation += 1
        generation = self._phase49_3i_gallery_load_generation
        self._phase49_3i_gallery_load_queue = []
        self._phase49_3i_gallery_photos = {}
        for child in inner.winfo_children():
            child.destroy()
        self._phase49_3i_gallery_cards = []
        self._phase49_3i_gallery_card_by_id = {}

        iids = list(tree.get_children())
        product_ids = []
        for iid in iids:
            try:
                product_ids.append(int(iid))
            except Exception:
                continue
        self._phase49_3i_product_order = product_ids
        self._phase49_3i_selected_products = set(getattr(self, "_phase49_3i_selected_products", set())) & set(product_ids)

        if not product_ids:
            tk.Label(
                inner,
                text="محصولی برای نمایش در این فیلتر وجود ندارد.",
                bg="#f4f7fa",
                fg="#64748b",
                font=("Tahoma", 11),
                pady=30,
            ).grid(row=0, column=0, sticky="ew")
            self._phase49_3i_update_selection_visuals()
            return

        view = self._phase49_3i_current_view()
        thumb_w, thumb_h = view["thumb"]
        card_w, card_h = view["card"]
        mode = getattr(self, "_phase49_3i_gallery_mode", DEFAULT_VIEW_MODE)

        for product_id in product_ids:
            row = self.db.product(product_id)
            if row is None:
                continue
            title = str(row["title_fa"] or row["source_title"] or f"Product #{product_id}").strip()
            date_formatter = getattr(self, "_date_short", None)
            meta_one, meta_two = product_card_metadata(row, date_formatter)

            card = tk.Frame(
                inner,
                bg="white",
                width=card_w,
                height=card_h,
                highlightbackground="#dbe3ea",
                highlightthickness=1,
                padx=8,
                pady=8,
                cursor="arrow",
            )
            card.grid_propagate(False)
            card.pack_propagate(False)

            image_holder = tk.Frame(card, width=thumb_w, height=thumb_h, bg="#eef2f7")
            image_holder.pack_propagate(False)
            image_label = tk.Label(
                image_holder,
                text="در حال بارگذاری تصویر...",
                bg="#eef2f7",
                fg="#64748b",
                cursor="hand2",
                anchor="center",
            )
            image_label.pack(fill="both", expand=True)
            image_label._phase49_thumb_size = (thumb_w, thumb_h)

            text_box = tk.Frame(card, bg="white")
            title_label = tk.Label(
                text_box,
                text=title,
                bg="white",
                fg="#071827",
                font=("Tahoma", 10, "bold"),
                justify="right",
                anchor="e",
                cursor="arrow",
            )
            meta_label = tk.Label(
                text_box,
                text=f"{meta_one}\n{meta_two}",
                bg="white",
                fg="#64748b",
                font=("Tahoma", 8),
                justify="right",
                anchor="e",
                cursor="arrow",
            )

            edit_button = ttk.Button(
                card,
                text="ویرایش محصول",
                command=lambda pid=product_id: self._phase49_3i_open_product(pid),
                style="Primary.TButton",
            )

            if mode == "list":
                image_holder.pack(side="right", padx=(8, 0))
                edit_button.pack(side="left", padx=(0, 8), pady=8)
                text_box.pack(side="right", fill="both", expand=True, padx=10)
                title_label.configure(wraplength=620)
                title_label.pack(fill="x", pady=(7, 2))
                meta_label.configure(wraplength=620)
                meta_label.pack(fill="x", pady=(0, 4))
            else:
                image_holder.pack(anchor="center")
                text_box.pack(fill="x", pady=(5, 2))
                title_label.configure(wraplength=max(110, card_w - 20))
                title_label.pack(fill="x", pady=(2, 2))
                meta_label.configure(wraplength=max(110, card_w - 20))
                meta_label.pack(fill="x", pady=(0, 2))
                edit_button.pack(fill="x", side="bottom")

            self._phase49_3i_bind_selectable(card, product_id)
            self._phase49_3i_bind_selectable(image_holder, product_id, preview=True)
            self._phase49_3i_bind_selectable(image_label, product_id, preview=True)
            self._phase49_3i_bind_selectable(text_box, product_id)
            self._phase49_3i_bind_selectable(title_label, product_id)
            self._phase49_3i_bind_selectable(meta_label, product_id)

            self._phase49_3i_gallery_cards.append(card)
            self._phase49_3i_gallery_card_by_id[product_id] = card
            self._phase49_3i_gallery_load_queue.append((generation, product_id, image_label))

        self._phase49_3i_layout_cards()
        self._phase49_3i_update_selection_visuals()
        self.after(10, self._phase49_3i_load_next_thumbnail)

    def _phase49_3i_load_next_thumbnail(self):
        queue = getattr(self, "_phase49_3i_gallery_load_queue", None)
        if not queue:
            return
        generation, product_id, label = queue.pop(0)
        if generation != getattr(self, "_phase49_3i_gallery_load_generation", -1):
            return
        try:
            if not label.winfo_exists():
                raise RuntimeError("card destroyed")
            row = self.db.product(product_id)
            path = _local_thumbnail(row) if row is not None else None
            if path is None:
                label.configure(text="بدون تصویر محلی", image="")
            else:
                size = tuple(getattr(label, "_phase49_thumb_size", VIEW_MODES[DEFAULT_VIEW_MODE]["thumb"]))
                photo = _photo_for_size(path, size)
                self._phase49_3i_gallery_photos[product_id] = photo
                label.configure(image=photo, text="")
        except Exception:
            try:
                label.configure(text="تصویر قابل نمایش نیست", image="")
            except Exception:
                pass
        if queue:
            self.after(8, self._phase49_3i_load_next_thumbnail)

    def start_direct_link_import(self):
        url = self.seed_var.get().strip() if hasattr(self, "seed_var") else ""
        code = self.source_map.get(self.source_var.get(), "") if hasattr(self, "source_map") else ""
        source = self.db.source(code) if code else None
        pattern = str(source["model_url_pattern"] or "").strip() if source is not None else ""

        if is_http_url(url) and pattern:
            if matches_source_product_url(url, pattern):
                if hasattr(self, "log"):
                    self.log(f"PHASE49_3I_URL_ROUTE=direct_product source={code} url={url}")
                return original_direct_link(self)
            if hasattr(self, "log"):
                self.log(f"PHASE49_3I_URL_ROUTE=preview_listing source={code} url={url}")
            return self.start_candidate_discovery()

        return original_direct_link(self)

    app_class._modernize_products_page = _modernize_products_page
    app_class._hide_legacy_raw_filter_bar = _hide_legacy_raw_filter_bar
    app_class._phase49_3i_current_view = _phase49_3i_current_view
    app_class._phase49_3i_change_filter = _phase49_3i_change_filter
    app_class._phase49_3i_change_sort = _phase49_3i_change_sort
    app_class._phase49_3i_change_view = _phase49_3i_change_view
    app_class._phase49_3i_gallery_resize = _phase49_3i_gallery_resize
    app_class._phase49_3i_layout_cards = _phase49_3i_layout_cards
    app_class._phase49_3i_update_selection_visuals = _phase49_3i_update_selection_visuals
    app_class._phase49_3i_select_product = _phase49_3i_select_product
    app_class.load_product = load_product
    app_class._phase49_3i_open_product = _phase49_3i_open_product
    app_class._phase49_3i_select_click = _phase49_3i_select_click
    app_class._phase49_3i_select_all_products = _phase49_3i_select_all_products
    app_class._phase49_3i_clear_selection = _phase49_3i_clear_selection
    app_class._phase49_3i_remove_selected_from_publish_queue = _phase49_3i_remove_selected_from_publish_queue
    app_class._phase49_3i_show_context_menu = _phase49_3i_show_context_menu
    app_class._phase49_3i_bind_selectable = _phase49_3i_bind_selectable
    app_class._phase49_3i_apply_post_sort = _phase49_3i_apply_post_sort
    app_class.refresh_products = refresh_products
    app_class._phase49_3i_render_gallery = _phase49_3i_render_gallery
    app_class._phase49_3i_load_next_thumbnail = _phase49_3i_load_next_thumbnail
    app_class.start_direct_link_import = start_direct_link_import
    app_class._phase49_3i_explorer_hotfix_installed = True
