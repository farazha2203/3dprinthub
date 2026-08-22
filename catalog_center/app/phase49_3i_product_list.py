from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageOps, ImageTk

from . import phase49_3c_image_pipeline as image_pipeline


PRODUCT_CARD_FIELDS = ("thumbnail", "title", "edit")
PRODUCT_THUMBNAIL_SIZE = (260, 190)
PRODUCT_PREVIEW_SIZE = (1000, 720)


def _json_list(value) -> list:
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _local_thumbnail(row) -> Path | None:
    """Resolve a product image from local persisted data only; never fetch network data."""
    urls: list[str] = []
    primary = str(row["primary_image_url"] or "") if "primary_image_url" in row.keys() else ""
    if primary:
        urls.append(primary)
    for field in ("selected_images_json", "images_json"):
        if field not in row.keys():
            continue
        for url in _json_list(row[field]):
            text = str(url or "").strip()
            if text and text not in urls:
                urls.append(text)

    for url in urls:
        try:
            path = image_pipeline.strict_local_image(row, url)
        except Exception:
            path = ""
        if path and Path(path).is_file():
            return Path(path)

    local_text = str(row["local_dir"] or "").strip() if "local_dir" in row.keys() else ""
    if not local_text:
        return None
    local_dir = Path(local_text)

    manifest = local_dir / "page_extract.json"
    if manifest.is_file():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        for item in payload.get("images", []) if isinstance(payload, dict) else []:
            if not isinstance(item, dict):
                continue
            candidate = str(item.get("local_file") or "").strip()
            if candidate and Path(candidate).is_file():
                return Path(candidate)

    image_dir = local_dir / "images"
    if image_dir.is_dir():
        for path in sorted(image_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
                return path
    return None


def _card_photo(path: Path):
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail(PRODUCT_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", PRODUCT_THUMBNAIL_SIZE, "white")
        x = max(0, (PRODUCT_THUMBNAIL_SIZE[0] - image.width) // 2)
        y = max(0, (PRODUCT_THUMBNAIL_SIZE[1] - image.height) // 2)
        canvas.paste(image, (x, y))
    return ImageTk.PhotoImage(canvas)


def _preview_photo(path: Path):
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        image.thumbnail(PRODUCT_PREVIEW_SIZE, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)


def install(app_class) -> None:
    """Replace the UX87 products surface with image/name/edit cards.

    The legacy Treeview/editor stays alive but hidden so old selection/filter/sync
    contracts remain available. UX87 builds the page through
    `_modernize_products_page`, therefore the patch belongs on that real shell
    boundary rather than `_products_ui`.
    """
    if getattr(app_class, "_phase49_3i_product_list_installed", False):
        return

    original_modernize = app_class._modernize_products_page
    original_refresh = app_class.refresh_products

    def _modernize_products_page(self):
        original_modernize(self)

        # The base `_products_ui` creates the mature editor and hidden Treeview.
        # Keep them alive for compatibility but remove the entire legacy pane from
        # the operator surface. Detailed edits belong only to Product Workspace.
        pane = next(
            (child for child in self.products_tab.winfo_children() if isinstance(child, ttk.Panedwindow)),
            None,
        )
        if pane is not None:
            try:
                pane.pack_forget()
            except Exception:
                pass
        self._phase49_3i_legacy_product_pane = pane

        # Hide publish/bulk/more/edit toolbar actions from the Products list.
        # Filter/search/sort/refresh controls remain useful for the gallery.
        for child in self.products_tab.winfo_children():
            if not isinstance(child, ttk.Frame):
                continue
            for widget in child.winfo_children():
                if isinstance(widget, ttk.Menubutton):
                    try:
                        widget.pack_forget()
                    except Exception:
                        pass
                    continue
                if not isinstance(widget, ttk.Button):
                    continue
                try:
                    text = str(widget.cget("text") or "")
                except Exception:
                    text = ""
                if text and text != "بروزرسانی":
                    try:
                        widget.pack_forget()
                    except Exception:
                        pass

        header = ttk.Frame(self.products_tab)
        header.pack(fill="x", pady=(5, 7))
        ttk.Label(
            header,
            text="گالری محصولات — برای جزئیات و ویرایش، صفحه محصول را باز کنید",
            style="SubHeader.TLabel",
        ).pack(side="right")

        shell = ttk.Frame(self.products_tab)
        shell.pack(fill="both", expand=True)
        shell.rowconfigure(0, weight=1)
        shell.columnconfigure(0, weight=1)

        canvas = tk.Canvas(shell, highlightthickness=0, bg="#f4f7fa")
        ybar = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=ybar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")

        inner = tk.Frame(canvas, bg="#f4f7fa")
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: self._phase49_3i_gallery_resize(e.width))

        def wheel(event):
            delta = 0
            if getattr(event, "num", None) == 4:
                delta = -1
            elif getattr(event, "num", None) == 5:
                delta = 1
            elif getattr(event, "delta", 0):
                delta = -1 if event.delta > 0 else 1
            if delta:
                canvas.yview_scroll(delta * 3, "units")
                return "break"
            return None

        canvas.bind("<MouseWheel>", wheel)
        canvas.bind("<Button-4>", wheel)
        canvas.bind("<Button-5>", wheel)

        self._phase49_3i_gallery_canvas = canvas
        self._phase49_3i_gallery_inner = inner
        self._phase49_3i_gallery_window = window_id
        self._phase49_3i_gallery_cards = []
        self._phase49_3i_gallery_photos = {}
        self._phase49_3i_gallery_load_queue = []
        self._phase49_3i_gallery_load_generation = 0
        self._phase49_3i_gallery_columns = 1
        self._phase49_3i_preview_window = None
        self._phase49_3i_preview_photo = None
        self.after_idle(self.refresh_products)

    def _phase49_3i_gallery_resize(self, width: int):
        canvas = getattr(self, "_phase49_3i_gallery_canvas", None)
        inner = getattr(self, "_phase49_3i_gallery_inner", None)
        if canvas is None or inner is None:
            return
        width = max(300, int(width or 0))
        try:
            canvas.itemconfigure(self._phase49_3i_gallery_window, width=width)
        except Exception:
            pass
        columns = max(1, width // 305)
        if columns != getattr(self, "_phase49_3i_gallery_columns", 1):
            self._phase49_3i_gallery_columns = columns
            self._phase49_3i_layout_cards()

    def _phase49_3i_layout_cards(self):
        inner = getattr(self, "_phase49_3i_gallery_inner", None)
        if inner is None:
            return
        columns = max(1, int(getattr(self, "_phase49_3i_gallery_columns", 1)))
        for col in range(columns):
            try:
                inner.columnconfigure(col, weight=1, uniform="phase49_3i_product_card")
            except Exception:
                pass
        for index, card in enumerate(list(getattr(self, "_phase49_3i_gallery_cards", []) or [])):
            try:
                card.grid_forget()
                card.grid(row=index // columns, column=index % columns, sticky="n", padx=8, pady=8)
            except Exception:
                pass

    def _phase49_3i_select_product(self, product_id: int):
        self.current_product = int(product_id)
        tree = getattr(self, "product_tree", None)
        iid = str(product_id)
        if tree is not None and tree.exists(iid):
            try:
                tree.selection_set(iid)
                tree.focus(iid)
            except Exception:
                pass
        if hasattr(self, "status"):
            self.status.set(f"محصول #{product_id} انتخاب شد")

    def _phase49_3i_open_product(self, product_id: int):
        self._phase49_3i_select_product(product_id)
        return self.open_product_studio(product_id)

    def _phase49_3i_open_image_preview(self, product_id: int):
        row = self.db.product(int(product_id))
        if row is None:
            return
        path = _local_thumbnail(row)
        if path is None:
            messagebox.showinfo("3DPrintHub", "برای این محصول هنوز تصویر محلی قابل نمایش وجود ندارد.", parent=self)
            return
        try:
            photo = _preview_photo(path)
        except Exception as exc:
            messagebox.showerror("3DPrintHub", f"نمایش تصویر ناموفق بود: {exc}", parent=self)
            return
        try:
            if self._phase49_3i_preview_window is not None and self._phase49_3i_preview_window.winfo_exists():
                self._phase49_3i_preview_window.destroy()
        except Exception:
            pass
        win = tk.Toplevel(self)
        win.title(str(row["title_fa"] or row["source_title"] or f"Product #{product_id}"))
        win.geometry("1080x800")
        label = ttk.Label(win, image=photo, anchor="center")
        label.pack(fill="both", expand=True, padx=12, pady=12)
        self._phase49_3i_preview_window = win
        self._phase49_3i_preview_photo = photo

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

        iids = list(tree.get_children())
        if not iids:
            tk.Label(
                inner,
                text="محصولی برای نمایش در این فیلتر وجود ندارد.",
                bg="#f4f7fa",
                fg="#64748b",
                font=("Tahoma", 11),
                pady=30,
            ).grid(row=0, column=0, sticky="ew")
            return

        for iid in iids:
            try:
                product_id = int(iid)
            except Exception:
                continue
            row = self.db.product(product_id)
            if row is None:
                continue
            title = str(row["title_fa"] or row["source_title"] or f"Product #{product_id}").strip()

            card = tk.Frame(
                inner,
                bg="white",
                width=284,
                height=278,
                highlightbackground="#dbe3ea",
                highlightthickness=1,
                padx=10,
                pady=10,
            )
            card.grid_propagate(False)
            image_label = tk.Label(
                card,
                text="در حال بارگذاری تصویر...",
                bg="#eef2f7",
                fg="#64748b",
                width=32,
                height=12,
                cursor="hand2",
            )
            image_label.pack(fill="x")
            image_label.bind("<Button-1>", lambda _e, pid=product_id: self._phase49_3i_open_image_preview(pid))

            title_label = tk.Label(
                card,
                text=title,
                bg="white",
                fg="#071827",
                font=("Tahoma", 10, "bold"),
                wraplength=255,
                justify="right",
                anchor="e",
            )
            title_label.pack(fill="x", pady=(8, 7))

            ttk.Button(
                card,
                text="ویرایش محصول",
                command=lambda pid=product_id: self._phase49_3i_open_product(pid),
                style="Primary.TButton",
            ).pack(fill="x")

            self._phase49_3i_gallery_cards.append(card)
            self._phase49_3i_gallery_load_queue.append((generation, product_id, image_label))

        self._phase49_3i_layout_cards()
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
                photo = _card_photo(path)
                self._phase49_3i_gallery_photos[product_id] = photo
                label.configure(image=photo, text="")
        except Exception:
            try:
                label.configure(text="تصویر قابل نمایش نیست", image="")
            except Exception:
                pass
        if queue:
            self.after(8, self._phase49_3i_load_next_thumbnail)

    def refresh_products(self):
        result = original_refresh(self)
        if hasattr(self, "_phase49_3i_gallery_inner"):
            self.after_idle(self._phase49_3i_render_gallery)
        return result

    # Selection from the hidden legacy Treeview remains a compatibility path.
    def load_product(self, _event=None):
        tree = getattr(self, "product_tree", None)
        selection = tree.selection() if tree is not None else ()
        if not selection:
            return
        try:
            self._phase49_3i_select_product(int(selection[0]))
        except Exception:
            return

    app_class._modernize_products_page = _modernize_products_page
    app_class.refresh_products = refresh_products
    app_class.load_product = load_product
    app_class._phase49_3i_gallery_resize = _phase49_3i_gallery_resize
    app_class._phase49_3i_layout_cards = _phase49_3i_layout_cards
    app_class._phase49_3i_select_product = _phase49_3i_select_product
    app_class._phase49_3i_open_product = _phase49_3i_open_product
    app_class._phase49_3i_open_image_preview = _phase49_3i_open_image_preview
    app_class._phase49_3i_render_gallery = _phase49_3i_render_gallery
    app_class._phase49_3i_load_next_thumbnail = _phase49_3i_load_next_thumbnail
    app_class._phase49_3i_product_list_installed = True

    # Compose same-phase operator-shell hotfixes only after the mature 49.3I
    # gallery contract exists. Older phase installers remain independent.
    from .phase49_3i_explorer_hotfix import install as install_explorer_hotfix
    from .phase49_3i_secret_persistence import install as install_secret_persistence

    install_explorer_hotfix(app_class)
    install_secret_persistence(app_class)
