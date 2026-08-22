from __future__ import annotations

import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageOps, ImageTk

from .phase49_3i_discovery_review import is_http_url
from .phase49_3i_product_list import _local_thumbnail


VIEW_MODES = {
    "extra_large": {
        "label": "آیکن خیلی بزرگ",
        "thumb": (320, 235),
        "card": (348, 332),
    },
    "large": {
        "label": "آیکن بزرگ",
        "thumb": (260, 190),
        "card": (288, 286),
    },
    "medium": {
        "label": "آیکن متوسط",
        "thumb": (180, 132),
        "card": (208, 226),
    },
    "small": {
        "label": "آیکن کوچک",
        "thumb": (120, 88),
        "card": (150, 184),
    },
    "list": {
        "label": "لیست",
        "thumb": (72, 54),
        "card": (700, 78),
    },
}
DEFAULT_VIEW_MODE = "large"
VIEW_SETTING_KEY = "phase49_3i_product_view_mode"


def normalize_view_mode(value: str) -> str:
    key = str(value or "").strip().lower()
    return key if key in VIEW_MODES else DEFAULT_VIEW_MODE


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
    """Add Windows-Explorer-like product browsing without replacing mature flows."""
    if getattr(app_class, "_phase49_3i_explorer_hotfix_installed", False):
        return

    original_modernize = app_class._modernize_products_page
    original_direct_link = app_class.start_direct_link_import

    def _modernize_products_page(self):
        original_modernize(self)

        self._phase49_3i_selected_products = set()
        self._phase49_3i_last_selected_id = None
        self._phase49_3i_product_order = []
        self._phase49_3i_gallery_card_by_id = {}
        self._phase49_3i_gallery_mode = normalize_view_mode(
            self.db.setting(VIEW_SETTING_KEY, DEFAULT_VIEW_MODE)
        )

        shell = getattr(getattr(self, "_phase49_3i_gallery_canvas", None), "master", None)
        toolbar = ttk.Frame(self.products_tab)
        if shell is not None:
            toolbar.pack(fill="x", pady=(0, 7), before=shell)
        else:
            toolbar.pack(fill="x", pady=(0, 7))

        ttk.Label(toolbar, text="نمایش:").pack(side="right", padx=(6, 2))
        labels = [VIEW_MODES[key]["label"] for key in VIEW_MODES]
        current_label = VIEW_MODES[self._phase49_3i_gallery_mode]["label"]
        self._phase49_3i_view_label = tk.StringVar(value=current_label)
        view_combo = ttk.Combobox(
            toolbar,
            textvariable=self._phase49_3i_view_label,
            values=labels,
            state="readonly",
            width=18,
        )
        view_combo.pack(side="right", padx=3)
        view_combo.bind("<<ComboboxSelected>>", self._phase49_3i_change_view)

        ttk.Button(
            toolbar,
            text="انتخاب همه",
            command=self._phase49_3i_select_all_products,
        ).pack(side="right", padx=3)
        ttk.Button(
            toolbar,
            text="لغو انتخاب",
            command=self._phase49_3i_clear_selection,
        ).pack(side="right", padx=3)
        self._phase49_3i_selected_count = tk.StringVar(value="0 انتخاب")
        ttk.Label(toolbar, textvariable=self._phase49_3i_selected_count).pack(side="right", padx=10)

        self._phase49_3i_context_menu = tk.Menu(self, tearoff=False)
        self.after_idle(self._phase49_3i_render_gallery)

    def _phase49_3i_current_view(self):
        return VIEW_MODES[normalize_view_mode(getattr(self, "_phase49_3i_gallery_mode", DEFAULT_VIEW_MODE))]

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

            title_label = tk.Label(
                card,
                text=title,
                bg="white",
                fg="#071827",
                font=("Tahoma", 10, "bold"),
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
                edit_button.pack(side="left", padx=(0, 8))
                title_label.configure(wraplength=720)
                title_label.pack(side="right", fill="both", expand=True, padx=10)
            else:
                image_holder.pack(anchor="center")
                title_label.configure(wraplength=max(110, card_w - 20))
                title_label.pack(fill="x", pady=(7, 5))
                edit_button.pack(fill="x", side="bottom")

            self._phase49_3i_bind_selectable(card, product_id)
            self._phase49_3i_bind_selectable(image_holder, product_id, preview=True)
            self._phase49_3i_bind_selectable(image_label, product_id, preview=True)
            self._phase49_3i_bind_selectable(title_label, product_id)

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
    app_class._phase49_3i_current_view = _phase49_3i_current_view
    app_class._phase49_3i_change_view = _phase49_3i_change_view
    app_class._phase49_3i_gallery_resize = _phase49_3i_gallery_resize
    app_class._phase49_3i_layout_cards = _phase49_3i_layout_cards
    app_class._phase49_3i_update_selection_visuals = _phase49_3i_update_selection_visuals
    app_class._phase49_3i_select_click = _phase49_3i_select_click
    app_class._phase49_3i_select_all_products = _phase49_3i_select_all_products
    app_class._phase49_3i_clear_selection = _phase49_3i_clear_selection
    app_class._phase49_3i_remove_selected_from_publish_queue = _phase49_3i_remove_selected_from_publish_queue
    app_class._phase49_3i_show_context_menu = _phase49_3i_show_context_menu
    app_class._phase49_3i_bind_selectable = _phase49_3i_bind_selectable
    app_class._phase49_3i_render_gallery = _phase49_3i_render_gallery
    app_class._phase49_3i_load_next_thumbnail = _phase49_3i_load_next_thumbnail
    app_class.start_direct_link_import = start_direct_link_import
    app_class._phase49_3i_explorer_hotfix_installed = True
