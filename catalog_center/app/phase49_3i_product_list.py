from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from . import phase49_3c_image_pipeline as image_pipeline


HIDE_ACTION_TEXTS = {
    "ذخیره",
    "♻ بازیابی کامل",
    "بازیابی کامل",
    "🖼 گالری تصاویر",
    "مدیریت تصاویر",
    "🚀 استودیوی محصول",
    "ویرایش محصول",
    "✨ ترجمه فارسی",
    "ترجمه با AI",
    "✨ AI این محصول",
    "AI این محصول",
    "AI انتخاب‌شده‌ها",
    "AI همه نیازمندها",
    "قیمت انتخاب‌شده‌ها",
    "♻ بازیابی انتخاب‌شده‌ها",
    "بازیابی انتخاب‌شده‌ها",
    "استودیوی محتوا",
    "تاریخچه",
    "تأیید و صف انتشار",
    "🚀 ارسال همین محصول",
    "انتشار همین محصول",
    "🧾 گزارش ارسال",
    "گزارش انتشار",
    "محاسبه قیمت",
    "صفحه منبع",
    "مشخصات و فایل‌ها",
    "بلاک و انتقال",
}


def _walk(root):
    try:
        children = root.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield child
        yield from _walk(child)


def _json_list(value) -> list:
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _local_thumbnail(row) -> Path | None:
    urls = []
    primary = str(row["primary_image_url"] or "") if "primary_image_url" in row.keys() else ""
    if primary:
        urls.append(primary)
    for field in ("selected_images_json", "images_json"):
        if field in row.keys():
            for url in _json_list(row[field]):
                if url and url not in urls:
                    urls.append(str(url))
    for url in urls:
        try:
            path = image_pipeline.strict_local_image(row, url)
        except Exception:
            path = ""
        if path and Path(path).is_file():
            return Path(path)
    local_dir = Path(str(row["local_dir"] or "")) if "local_dir" in row.keys() else Path()
    image_dir = local_dir / "images"
    if image_dir.is_dir():
        for path in sorted(image_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}:
                return path
    return None


def install(app_class) -> None:
    if getattr(app_class, "_phase49_3i_product_list_installed", False):
        return

    original_products_ui = app_class._products_ui
    original_refresh = app_class.refresh_products

    def _products_ui(self):
        original_products_ui(self)
        style = ttk.Style(self)
        style.configure("Phase493IProduct.Treeview", rowheight=82)
        tree = getattr(self, "product_tree", None)
        if tree is not None:
            tree.configure(show="tree headings", displaycolumns=("en",), style="Phase493IProduct.Treeview", selectmode="browse")
            tree.heading("#0", text="تصویر")
            tree.column("#0", width=120, minwidth=100, stretch=False, anchor="center")
            tree.heading("en", text="نام محصول")
            tree.column("en", width=760, minwidth=320, stretch=True, anchor="w")

        # Keep the mature embedded editor widgets alive for old code paths but
        # remove that pane from the work-list surface. Product Workspace is the
        # canonical detailed editor from this phase onward.
        pane = next((child for child in self.products_tab.winfo_children() if isinstance(child, ttk.Panedwindow)), None)
        if pane is not None:
            panes = list(pane.panes())
            if len(panes) > 1:
                try:
                    pane.forget(panes[1])
                except Exception:
                    pass
            self._phase49_3i_product_pane = pane

        for widget in _walk(self.products_tab):
            if not isinstance(widget, ttk.Button):
                continue
            try:
                text = str(widget.cget("text") or "")
            except Exception:
                continue
            if text in HIDE_ACTION_TEXTS:
                try:
                    widget.pack_forget()
                except Exception:
                    try:
                        widget.grid_remove()
                    except Exception:
                        pass

        actions = ttk.Frame(self.products_tab)
        if pane is not None:
            try:
                actions.pack(fill="x", pady=(7, 2), before=pane)
            except Exception:
                actions.pack(fill="x", pady=(7, 2))
        else:
            actions.pack(fill="x", pady=(7, 2))
        ttk.Label(
            actions,
            text="لیست سبک محصولات — ویرایش جزئیات فقط در صفحه محصول",
            style="SubHeader.TLabel",
        ).pack(side="left")
        ttk.Button(
            actions,
            text="📄 صفحه محصول / ویرایش کامل",
            command=self._phase49_3i_open_selected_product,
            style="Success.TButton",
        ).pack(side="right", padx=4)
        self._phase49_3i_product_photos = {}

    def load_product(self, _event=None):
        tree = getattr(self, "product_tree", None)
        selection = tree.selection() if tree is not None else ()
        if not selection:
            return
        try:
            self.current_product = int(selection[0])
        except Exception:
            return
        row = self.db.product(self.current_product)
        if row is not None and hasattr(self, "status"):
            self.status.set(f"محصول #{self.current_product} انتخاب شد — برای ویرایش «صفحه محصول» را باز کن")

    def _phase49_3i_open_selected_product(self):
        tree = getattr(self, "product_tree", None)
        selection = tree.selection() if tree is not None else ()
        if selection:
            try:
                self.current_product = int(selection[0])
            except Exception:
                pass
        if not getattr(self, "current_product", None):
            messagebox.showwarning("3DPrintHub", "ابتدا یک محصول را انتخاب کن.", parent=self)
            return
        self.open_product_studio(self.current_product)

    def refresh_products(self):
        original_refresh(self)
        tree = getattr(self, "product_tree", None)
        if tree is None:
            return
        self._phase49_3i_product_photos = {}
        for iid in tree.get_children():
            try:
                product_id = int(iid)
            except Exception:
                continue
            row = self.db.product(product_id)
            if row is None:
                continue
            values = list(tree.item(iid, "values"))
            # Original columns: id,status,source,rating,images,received,refetch,sync,en,fa,price
            if len(values) > 8:
                values[8] = str(row["title_fa"] or row["source_title"] or f"Product #{product_id}")
                tree.item(iid, values=values)
            thumb = _local_thumbnail(row)
            if thumb is None:
                continue
            try:
                image = Image.open(thumb).convert("RGB")
                image.thumbnail((96, 68), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
            except Exception:
                continue
            self._phase49_3i_product_photos[product_id] = photo
            if tree.exists(iid):
                tree.item(iid, image=photo, text="")

    app_class._products_ui = _products_ui
    app_class.load_product = load_product
    app_class._phase49_3i_open_selected_product = _phase49_3i_open_selected_product
    app_class.refresh_products = refresh_products
    app_class._phase49_3i_product_list_installed = True
