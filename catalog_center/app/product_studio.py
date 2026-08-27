from __future__ import annotations

import json
import os
import re
import shutil
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
import tkinter as tk
from urllib import request as urllib_request

from PIL import Image, ImageTk

from .db import normalize_url, utc_now
from .openai_content import OpenAIContentService
from .phase49_ui import (
    first_site_images, gallery_page, keep_only_gallery_urls,
    receipt_lines, remove_gallery_urls,
)
from .v8_features import commercial_license_allows_publish, product_fingerprint
from .workflow import pricing_suggestion, product_state, STATUS_LABELS
from .version import APP_VERSION

PRODUCT_TYPE_LABELS = {
    "ready_product": "محصول آماده",
    "portfolio": "نمونه‌کار",
    "custom_order": "سفارش سفارشی",
}
PRODUCT_TYPE_CODES = {label: code for code, label in PRODUCT_TYPE_LABELS.items()}
AVAILABILITY_LABELS = {
    "in_stock": "موجود",
    "made_to_order": "تولید پس از سفارش",
    "quote_required": "نیازمند استعلام",
    "unavailable": "ناموجود",
}
AVAILABILITY_CODES = {label: code for code, label in AVAILABILITY_LABELS.items()}


class ProductStudio(tk.Toplevel):
    """Fast editorial workstation for one product.

    The studio intentionally keeps source facts, AI suggestions and user approvals
    separate. It never publishes by itself; it prepares/queues a product for the
    existing server ACK workflow.
    """

    def __init__(self, app, product_id: int):
        super().__init__(app)
        self.app = app
        self.db = app.db
        self.product_id = int(product_id)
        self.row = self.db.product(self.product_id)
        if self.row is None:
            self.destroy()
            raise RuntimeError(f"Product {product_id} not found")
        self.title(f"استودیوی محصول | 3DPrintHub Catalog Intelligence v{APP_VERSION}")
        self.geometry("1480x920")
        self.minsize(1180, 760)
        self.configure(bg="#f2f5f8")
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._photos: list[ImageTk.PhotoImage] = []
        self._gallery_cards: list[dict] = []
        self._bulk_image_urls: set[str] = set()
        self.gallery_page = 0
        self.gallery_page_size = 40
        self._ai_busy = False
        self._build_ui()
        self.reload()

    # ---------- generic helpers ----------
    def _json_list(self, raw):
        if isinstance(raw, list):
            return raw
        try:
            value = json.loads(raw or "[]")
            return value if isinstance(value, list) else []
        except Exception:
            return []

    def _json_dict(self, raw):
        if isinstance(raw, dict):
            return raw
        try:
            value = json.loads(raw or "{}")
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def _float(self, value, default=None):
        try:
            text = str(value if value is not None else "").replace(",", "").strip()
            return float(text) if text else default
        except Exception:
            return default

    def _int(self, value, default=0):
        try:
            return int(float(str(value or "0").replace(",", "")))
        except Exception:
            return default

    def _text_set(self, widget: tk.Text, value: str):
        widget.delete("1.0", "end")
        widget.insert("1.0", value or "")

    def _text_get(self, widget: tk.Text) -> str:
        return widget.get("1.0", "end").strip()

    def close(self):
        try:
            self.save(silent=True)
        except Exception:
            pass
        self.destroy()

    # ---------- UI ----------
    def _build_ui(self):
        header = ttk.Frame(self, padding=(16, 12))
        header.pack(fill="x")
        left = ttk.Frame(header)
        left.pack(side="left", fill="x", expand=True)
        self.header_title = tk.StringVar(value="محصول")
        self.header_meta = tk.StringVar(value="")
        ttk.Label(left, textvariable=self.header_title, style="Header.TLabel").pack(anchor="w")
        ttk.Label(left, textvariable=self.header_meta, style="SubHeader.TLabel").pack(anchor="w", pady=(3, 0))

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="♻ بازیابی منبع", command=self.refetch, style="Warning.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="✨ ترجمه فارسی", command=lambda: self.generate_ai("translate"), style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="✨ تولید محتوای کامل", command=lambda: self.generate_ai("commerce"), style="Success.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="💰 قیمت پیشنهادی", command=self.calculate_price).pack(side="left", padx=3)
        ttk.Button(actions, text="🧾 گزارش ارسال", command=self.open_sync_log).pack(side="left", padx=3)
        ttk.Button(actions, text="🚀 ارسال همین محصول", command=self.publish_now, style="Success.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="💾 ذخیره", command=self.save).pack(side="left", padx=3)

        source_bar = ttk.Frame(self, padding=(16, 0, 16, 8))
        source_bar.pack(fill="x")
        ttk.Label(source_bar, text="لینک منبع:").pack(side="left")
        self.source_url = tk.StringVar()
        source_entry = ttk.Entry(source_bar, textvariable=self.source_url)
        source_entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(source_bar, text="باز کردن", command=self.open_source).pack(side="left", padx=3)
        ttk.Button(source_bar, text="کپی لینک", command=self.copy_source).pack(side="left", padx=3)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.quick_tab = ttk.Frame(self.nb, padding=12)
        self.commerce_tab = ttk.Frame(self.nb, padding=12)
        self.images_tab = ttk.Frame(self.nb, padding=10)
        self.content_tab = ttk.Frame(self.nb, padding=12)
        self.specs_tab = ttk.Frame(self.nb, padding=12)
        self.publish_tab = ttk.Frame(self.nb, padding=12)
        self.nb.add(self.quick_tab, text="انتشار سریع")
        self.nb.add(self.commerce_tab, text="اطلاعات محصول و سفارش")
        self.nb.add(self.images_tab, text="تصاویر")
        self.nb.add(self.content_tab, text="محتوا و ترجمه")
        self.nb.add(self.specs_tab, text="مشخصات منبع")
        self.nb.add(self.publish_tab, text="انتشار")
        self._quick_ui()
        self._commerce_ui()
        self._images_ui()
        self._content_ui()
        self._specs_ui()
        self._publish_ui()

        footer = ttk.Frame(self, padding=(12, 0, 12, 12))
        footer.pack(fill="x")
        self.footer_status = tk.StringVar(value="آماده")
        ttk.Label(footer, textvariable=self.footer_status, style="SubHeader.TLabel").pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="🚀 ارسال همین محصول", command=self.publish_now, style="Success.TButton").pack(side="right", padx=4)
        ttk.Button(footer, text="✅ آماده انتشار", command=self.queue_for_publish, style="Success.TButton").pack(side="right", padx=4)
        ttk.Button(footer, text="ذخیره", command=self.save).pack(side="right", padx=4)

    def _quick_ui(self):
        self.quick_tab.columnconfigure(1, weight=1)
        self.quick_tab.columnconfigure(3, weight=1)
        self.title_en = tk.StringVar()
        self.title_fa = tk.StringVar()
        self.category_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.material_price_var = tk.StringVar()
        self.suggested_price_var = tk.StringVar()
        self.final_price_var = tk.StringVar()
        self.license_var = tk.StringVar(value="review")
        self.approved_var = tk.IntVar(value=0)
        self.publish_product_var = tk.IntVar(value=1)
        self.publish_portfolio_var = tk.IntVar(value=0)

        ttk.Label(self.quick_tab, text="عنوان منبع").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(self.quick_tab, textvariable=self.title_en).grid(row=0, column=1, columnspan=3, sticky="ew", padx=6, pady=5)
        ttk.Label(self.quick_tab, text="عنوان فارسی").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(self.quick_tab, textvariable=self.title_fa).grid(row=1, column=1, columnspan=3, sticky="ew", padx=6, pady=5)

        ttk.Label(self.quick_tab, text="گروه سایت").grid(row=2, column=0, sticky="w", pady=5)
        cat_frame = ttk.Frame(self.quick_tab)
        cat_frame.grid(row=2, column=1, sticky="ew", padx=6, pady=5)
        cat_frame.columnconfigure(0, weight=1)
        self.category_box = ttk.Combobox(cat_frame, textvariable=self.category_var, state="readonly")
        self.category_box.grid(row=0, column=0, sticky="ew")
        ttk.Button(cat_frame, text="+ گروه جدید", command=self.add_category).grid(row=0, column=1, padx=(5, 0))
        ttk.Label(self.quick_tab, text="مجوز تجاری").grid(row=2, column=2, sticky="w", pady=5)
        ttk.Combobox(self.quick_tab, textvariable=self.license_var, state="readonly", values=["review", "allowed", "owned", "public_domain", "blocked", "unknown"]).grid(row=2, column=3, sticky="ew", padx=6, pady=5)

        for row_idx, (label, var) in enumerate([
            ("وزن تقریبی (گرم)", self.weight_var),
            ("قیمت ماده / گرم", self.material_price_var),
            ("قیمت پیشنهادی", self.suggested_price_var),
            ("قیمت نهایی", self.final_price_var),
        ], start=3):
            col = 0 if row_idx in (3, 5) else 2
            target_col = 1 if col == 0 else 3
            display_row = 3 if row_idx in (3, 4) else 4
            ttk.Label(self.quick_tab, text=label).grid(row=display_row, column=col, sticky="w", pady=5)
            ttk.Entry(self.quick_tab, textvariable=var).grid(row=display_row, column=target_col, sticky="ew", padx=6, pady=5)

        flags = ttk.LabelFrame(self.quick_tab, text="خروجی", padding=8, style="Card.TLabelframe")
        flags.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(8, 6))
        ttk.Checkbutton(flags, text="تأیید برای فروش", variable=self.approved_var).pack(side="left", padx=8)
        ttk.Checkbutton(flags, text="محصول فروشگاه", variable=self.publish_product_var).pack(side="left", padx=8)
        ttk.Checkbutton(flags, text="نمونه‌کار", variable=self.publish_portfolio_var).pack(side="left", padx=8)

        fast = ttk.LabelFrame(self.quick_tab, text="مسیر یک‌دقیقه‌ای", padding=10, style="Card.TLabelframe")
        fast.grid(row=6, column=0, columnspan=4, sticky="nsew", pady=(8, 0))
        fast.columnconfigure(1, weight=1)
        self.quick_checklist = tk.StringVar(value="")
        ttk.Label(fast, textvariable=self.quick_checklist, justify="left", wraplength=1000).grid(row=0, column=0, columnspan=4, sticky="ew")
        ttk.Button(fast, text="۱) تصاویر", command=lambda: self.nb.select(self.images_tab)).grid(row=1, column=0, padx=4, pady=8)
        ttk.Button(fast, text="۲) ترجمه + محتوا", command=lambda: self.generate_ai("commerce"), style="Primary.TButton").grid(row=1, column=1, padx=4, pady=8, sticky="ew")
        ttk.Button(fast, text="۳) قیمت", command=self.calculate_price).grid(row=1, column=2, padx=4, pady=8)
        ttk.Button(fast, text="۴) صف انتشار", command=self.queue_for_publish, style="Success.TButton").grid(row=1, column=3, padx=4, pady=8)

    def _images_ui(self):
        bar = ttk.Frame(self.images_tab)
        bar.pack(fill="x", pady=(0, 8))
        self.gallery_info = tk.StringVar(value="0 تصویر")
        self.gallery_page_info = tk.StringVar(value="صفحه 1 از 1")
        ttk.Label(bar, textvariable=self.gallery_info).pack(side="left")
        ttk.Label(bar, textvariable=self.gallery_page_info, style="SubHeader.TLabel").pack(side="left", padx=12)

        ttk.Button(bar, text="◀ صفحه قبل", command=lambda: self.change_gallery_page(-1)).pack(side="right", padx=2)
        ttk.Button(bar, text="صفحه بعد ▶", command=lambda: self.change_gallery_page(1)).pack(side="right", padx=2)
        ttk.Button(bar, text="۵ عکس اول برای سایت", command=self.keep_first_five_for_site, style="Success.TButton").pack(side="right", padx=3)
        ttk.Button(bar, text="فقط ۵ عکس اول بماند", command=self.keep_first_five_only, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Button(bar, text="+ عکس از فایل", command=self.add_local_images).pack(side="right", padx=3)
        ttk.Button(bar, text="+ عکس با URL", command=self.add_url_image).pack(side="right", padx=3)

        bulk = ttk.Frame(self.images_tab)
        bulk.pack(fill="x", pady=(0, 8))
        ttk.Button(bulk, text="انتخاب گروهی همه صفحه", command=lambda: self.bulk_select_page(True)).pack(side="left", padx=3)
        ttk.Button(bulk, text="پاک کردن انتخاب گروهی", command=lambda: self.bulk_select_page(False)).pack(side="left", padx=3)
        ttk.Button(bulk, text="حذف گروهی از محصول", command=self.bulk_remove_images, style="Danger.TButton").pack(side="left", padx=3)
        ttk.Button(bulk, text="فقط انتخاب‌شده‌های گروهی بماند", command=self.bulk_keep_only).pack(side="left", padx=3)
        ttk.Button(bulk, text="همه برای سایت", command=lambda: self.select_all_images(True)).pack(side="right", padx=3)
        ttk.Button(bulk, text="هیچکدام برای سایت", command=lambda: self.select_all_images(False)).pack(side="right", padx=3)
        ttk.Button(bulk, text="♻ تازه‌سازی", command=self.refresh_gallery).pack(side="right", padx=3)

        shell = ttk.Frame(self.images_tab)
        shell.pack(fill="both", expand=True)
        self.gallery_canvas = tk.Canvas(shell, bg="#f7fbff", highlightthickness=0)
        vbar = ttk.Scrollbar(shell, orient="vertical", command=self.gallery_canvas.yview)
        self.gallery_canvas.configure(yscrollcommand=vbar.set)
        self.gallery_canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        self.gallery_inner = ttk.Frame(self.gallery_canvas)
        self.gallery_window = self.gallery_canvas.create_window((0, 0), window=self.gallery_inner, anchor="nw")
        self.gallery_inner.bind("<Configure>", lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all")))
        self.gallery_canvas.bind("<Configure>", lambda e: self.gallery_canvas.itemconfigure(self.gallery_window, width=e.width))

    def _commerce_ui(self):
        frame = self.commerce_tab
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        self.product_type_var = tk.StringVar(value=PRODUCT_TYPE_LABELS["ready_product"])
        self.dimensions_var = tk.StringVar()
        self.availability_var = tk.StringVar(value=AVAILABILITY_LABELS["made_to_order"])
        self.stock_var = tk.StringVar(value="0")
        self.lead_min_var = tk.StringVar(value="1")
        self.lead_max_var = tk.StringVar(value="3")
        self.has_3d_file_var = tk.IntVar(value=0)
        self.source_name_var = tk.StringVar()

        ttk.Label(frame, text="نوع آیتم").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=self.product_type_var, state="readonly", values=list(PRODUCT_TYPE_CODES), width=24).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Label(frame, text="ابعاد").grid(row=0, column=2, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.dimensions_var).grid(row=0, column=3, sticky="ew", padx=6)

        ttk.Label(frame, text="وضعیت موجودی").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=self.availability_var, state="readonly", values=list(AVAILABILITY_CODES), width=24).grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Label(frame, text="تعداد موجودی").grid(row=1, column=2, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.stock_var).grid(row=1, column=3, sticky="ew", padx=6)

        ttk.Label(frame, text="آماده‌سازی از (روز)").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.lead_min_var).grid(row=2, column=1, sticky="ew", padx=6)
        ttk.Label(frame, text="آماده‌سازی تا (روز)").grid(row=2, column=2, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.lead_max_var).grid(row=2, column=3, sticky="ew", padx=6)

        ttk.Label(frame, text="نام منبع / طراح").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.source_name_var).grid(row=3, column=1, sticky="ew", padx=6)
        ttk.Checkbutton(frame, text="فایل سه‌بعدی موجود است", variable=self.has_3d_file_var).grid(row=3, column=3, sticky="w", padx=6)

        ttk.Label(frame, text="توضیح کاربرد").grid(row=4, column=0, sticky="nw", pady=5)
        self.use_description_text = tk.Text(frame, height=4, wrap="word")
        self.use_description_text.grid(row=4, column=1, columnspan=3, sticky="nsew", padx=6, pady=5)

        ttk.Label(frame, text="متریال‌ها (هر خط یک مورد)").grid(row=5, column=0, sticky="nw", pady=5)
        self.materials_text = tk.Text(frame, height=5, wrap="word")
        self.materials_text.grid(row=5, column=1, sticky="nsew", padx=6, pady=5)
        ttk.Label(frame, text="رنگ‌ها (هر خط یک مورد)").grid(row=5, column=2, sticky="nw", pady=5)
        self.colors_text = tk.Text(frame, height=5, wrap="word")
        self.colors_text.grid(row=5, column=3, sticky="nsew", padx=6, pady=5)

        ttk.Label(frame, text="ویژگی‌های فنی (JSON)").grid(row=6, column=0, sticky="nw", pady=5)
        self.technical_features_text = tk.Text(frame, height=8, wrap="word")
        self.technical_features_text.grid(row=6, column=1, sticky="nsew", padx=6, pady=5)
        ttk.Label(frame, text="کلمات کلیدی (هر خط یک مورد)").grid(row=6, column=2, sticky="nw", pady=5)
        self.keywords_text = tk.Text(frame, height=8, wrap="word")
        self.keywords_text.grid(row=6, column=3, sticky="nsew", padx=6, pady=5)
        frame.rowconfigure(6, weight=1)

    def _content_ui(self):
        toolbar = ttk.Frame(self.content_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="✨ ترجمه دقیق EN → FA", command=lambda: self.generate_ai("translate"), style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(toolbar, text="✨ تولید محتوای فروشگاهی", command=lambda: self.generate_ai("commerce"), style="Success.TButton").pack(side="left", padx=3)
        ttk.Button(toolbar, text="باز کردن استودیوی کامل SEO", command=lambda: self.app.open_content_studio(self.product_id)).pack(side="left", padx=3)
        self.ai_status = tk.StringVar(value="")
        ttk.Label(toolbar, textvariable=self.ai_status, style="SubHeader.TLabel").pack(side="right")

        pane = ttk.Panedwindow(self.content_tab, orient="horizontal")
        pane.pack(fill="both", expand=True)
        source = ttk.LabelFrame(pane, text="متن منبع", padding=8, style="Card.TLabelframe")
        persian = ttk.LabelFrame(pane, text="محتوای فارسی قابل ویرایش", padding=8, style="Card.TLabelframe")
        pane.add(source, weight=1)
        pane.add(persian, weight=1)

        ttk.Label(source, text="عنوان انگلیسی/اصلی").pack(anchor="w")
        self.content_source_title = tk.Text(source, height=3, wrap="word")
        self.content_source_title.pack(fill="x", pady=(2, 8))
        ttk.Label(source, text="توضیحات منبع").pack(anchor="w")
        self.content_source_desc = tk.Text(source, wrap="word")
        self.content_source_desc.pack(fill="both", expand=True, pady=(2, 0))

        ttk.Label(persian, text="عنوان فارسی").pack(anchor="w")
        self.content_title_fa = tk.StringVar()
        ttk.Entry(persian, textvariable=self.content_title_fa).pack(fill="x", pady=(2, 8))
        ttk.Label(persian, text="توضیح کوتاه فارسی").pack(anchor="w")
        self.content_short_fa = tk.Text(persian, height=5, wrap="word")
        self.content_short_fa.pack(fill="x", pady=(2, 8))
        ttk.Label(persian, text="توضیح کامل فارسی").pack(anchor="w")
        self.content_desc_fa = tk.Text(persian, wrap="word")
        self.content_desc_fa.pack(fill="both", expand=True, pady=(2, 8))
        ttk.Button(persian, text="ذخیره محتوای فارسی", command=self.save, style="Success.TButton").pack(anchor="e")

    def _specs_ui(self):
        top = ttk.Frame(self.specs_tab)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="URL منبع").pack(side="left")
        self.spec_source_url = tk.StringVar()
        ttk.Entry(top, textvariable=self.spec_source_url).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(top, text="باز کردن", command=self.open_source).pack(side="left")

        pane = ttk.Panedwindow(self.specs_tab, orient="horizontal")
        pane.pack(fill="both", expand=True)
        left = ttk.LabelFrame(pane, text="مشخصات استخراج‌شده", padding=8, style="Card.TLabelframe")
        right = ttk.LabelFrame(pane, text="ترجمه / مشخصات فارسی", padding=8, style="Card.TLabelframe")
        pane.add(left, weight=1)
        pane.add(right, weight=1)
        self.source_specs = tk.Text(left, wrap="word")
        self.source_specs.pack(fill="both", expand=True)
        self.fa_specs = tk.Text(right, wrap="word")
        self.fa_specs.pack(fill="both", expand=True)
        self.source_categories_label = tk.StringVar(value="")
        ttk.Label(left, textvariable=self.source_categories_label, wraplength=550, style="SubHeader.TLabel").pack(fill="x", pady=(6, 0))
        self.fa_categories_label = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.fa_categories_label, wraplength=550, style="SubHeader.TLabel").pack(fill="x", pady=(6, 0))

    def _publish_ui(self):
        self.publish_checklist = tk.StringVar(value="")
        ttk.Label(self.publish_tab, text="کنترل آماده‌بودن محصول", style="Header.TLabel").pack(anchor="w")
        ttk.Label(self.publish_tab, textvariable=self.publish_checklist, justify="left", wraplength=1150).pack(fill="x", pady=12)
        self.publish_source = tk.StringVar(value="")
        self.publish_server = tk.StringVar(value="")
        ttk.Label(self.publish_tab, textvariable=self.publish_source, style="SubHeader.TLabel").pack(anchor="w", pady=4)
        ttk.Label(self.publish_tab, textvariable=self.publish_server, style="SubHeader.TLabel").pack(anchor="w", pady=4)
        buttons = ttk.Frame(self.publish_tab)
        buttons.pack(fill="x", pady=18)
        ttk.Button(buttons, text="💾 ذخیره", command=self.save).pack(side="left", padx=4)
        ttk.Button(buttons, text="✅ تأیید و افزودن به صف انتشار", command=self.queue_for_publish, style="Success.TButton").pack(side="left", padx=4)
        ttk.Button(buttons, text="🚀 ارسال همین محصول به سایت", command=self.publish_now, style="Success.TButton").pack(side="left", padx=4)
        ttk.Button(buttons, text="🧾 گزارش ارسال", command=self.open_sync_log).pack(side="left", padx=4)
        ttk.Button(buttons, text="رفتن به صف انتشار", command=self.open_upload_tab, style="Primary.TButton").pack(side="left", padx=4)

    # ---------- loading / save ----------
    def reload(self):
        self.row = self.db.product(self.product_id)
        if self.row is None:
            return
        row = self.row
        self.header_title.set(row["title_fa"] or row["source_title"] or f"Product #{self.product_id}")
        state = product_state(row)
        rating = self.app._rating_text(row) if hasattr(self.app, "_rating_text") else "—"
        self.header_meta.set(
            f"{STATUS_LABELS.get(state, state)}  •  {row['source_code']}  •  {rating}  •  "
            f"عکس: {len(self._json_list(row['images_json']))}  •  دریافت: {self.app._date_short(row['created_at']) if hasattr(self.app, '_date_short') else row['created_at']}"
        )
        self.source_url.set(row["source_url"] or "")
        self.spec_source_url.set(row["source_url"] or "")
        self.title_en.set(row["source_title"] or "")
        self.title_fa.set(row["title_fa"] or "")
        self.content_title_fa.set(row["title_fa"] or "")
        self._text_set(self.content_source_title, row["source_title"] or "")
        self._text_set(self.content_source_desc, row["source_description"] or "")
        self._text_set(self.content_short_fa, row["short_description_fa"] or "")
        self._text_set(self.content_desc_fa, row["description_fa"] or "")
        self.weight_var.set("" if row["estimated_weight_grams"] is None else str(row["estimated_weight_grams"]))
        self.material_price_var.set(str(row["material_price_per_gram"] or ""))
        self.suggested_price_var.set(str(row["suggested_price"] or ""))
        self.final_price_var.set(str(row["final_price"] or ""))
        self.license_var.set(row["commercial_status"] or "review")
        self.approved_var.set(int(row["approved_for_sale"] or 0))
        product_flag=int(row["publish_as_product"] or 0)
        portfolio_flag=int(row["publish_as_portfolio"] or 0)
        if not product_flag and not portfolio_flag:
            product_flag=1
        self.publish_product_var.set(product_flag)
        self.publish_portfolio_var.set(portfolio_flag)
        self._refresh_categories(row["local_category_slug"] or "external-other")
        self._text_set(self.source_specs, json.dumps(self._json_dict(row["source_specs_json"]), ensure_ascii=False, indent=2))
        self._text_set(self.fa_specs, json.dumps(self._json_dict(row["specs_fa_json"]), ensure_ascii=False, indent=2))
        src_cats = self._json_list(row["source_categories_json"])
        fa_cats = self._json_list(row["categories_fa_json"])
        self.source_categories_label.set("دسته‌های منبع: " + (" > ".join(map(str, src_cats)) if src_cats else (row["source_category"] or "—")))
        self.fa_categories_label.set("ترجمه دسته‌ها: " + (" > ".join(map(str, fa_cats)) if fa_cats else "—"))
        self.publish_source.set(f"منبع: {row['source_url'] or '—'}")
        ack = self._json_dict(row["server_ack_json"] or "{}")
        visible = ack.get("visible_on_store")
        visible_text = " | فروشگاه: نمایش داده می‌شود" if visible is True else (" | فروشگاه: مخفی/ناموفق" if visible is False and ack else "")
        self.publish_server.set(f"Server ID: {row['server_id'] or '—'} | آخرین Sync: {row['last_synced_at'] or '—'}{visible_text}")
        self.product_type_var.set(PRODUCT_TYPE_LABELS.get(row["product_type"] or "ready_product", PRODUCT_TYPE_LABELS["ready_product"]))
        self.dimensions_var.set(row["dimensions"] or "")
        self.availability_var.set(AVAILABILITY_LABELS.get(row["availability_status"] or "made_to_order", AVAILABILITY_LABELS["made_to_order"]))
        self.stock_var.set(str(row["stock_quantity"] or 0))
        self.lead_min_var.set(str(row["lead_time_min_days"] or 1))
        self.lead_max_var.set(str(row["lead_time_max_days"] or 1))
        self.has_3d_file_var.set(int(row["has_3d_file"] or 0))
        self.source_name_var.set(row["source_name"] or row["author_name"] or "")
        self._text_set(self.use_description_text, row["use_description"] or "")
        self._text_set(self.materials_text, "\n".join(map(str, self._json_list(row["materials_json"]))))
        self._text_set(self.colors_text, "\n".join(map(str, self._json_list(row["colors_json"]))))
        self._text_set(self.technical_features_text, json.dumps(self._json_dict(row["technical_features_json"]), ensure_ascii=False, indent=2))
        self._text_set(self.keywords_text, "\n".join(map(str, self._json_list(row["keywords_json"]))))
        self.refresh_gallery()
        self.refresh_checklists()

    def _refresh_categories(self, current_slug: str):
        items = self.app.get_all_categories()
        labels = [x["name"] for x in items]
        self.category_box["values"] = labels
        slug_map = {x["slug"]: x["name"] for x in items}
        self.category_var.set(slug_map.get(current_slug, current_slug or (labels[0] if labels else "")))

    def save(self, silent=False):
        if self.row is None:
            return False
        category_name = self.category_var.get().strip()
        category_slug = self.app.category_label_to_slug.get(category_name, category_name or "external-other")
        source_url = self.source_url.get().strip() or self.spec_source_url.get().strip()
        title_fa = self.content_title_fa.get().strip() or self.title_fa.get().strip()
        desc_fa = self._text_get(self.content_desc_fa)
        short_fa = self._text_get(self.content_short_fa)
        try:
            specs_fa = json.loads(self._text_get(self.fa_specs) or "{}")
            if not isinstance(specs_fa, dict):
                raise ValueError("specs_fa must be an object")
        except Exception as exc:
            if not silent:
                messagebox.showerror("3DPrintHub", f"JSON مشخصات فارسی معتبر نیست:\n{exc}", parent=self)
            return False
        try:
            technical_features = json.loads(self._text_get(self.technical_features_text) or "{}")
            if not isinstance(technical_features, dict):
                raise ValueError("technical_features must be an object")
        except Exception as exc:
            if not silent:
                messagebox.showerror("3DPrintHub", f"JSON ویژگی‌های فنی معتبر نیست:\n{exc}", parent=self)
            return False
        lead_min = max(0, self._int(self.lead_min_var.get(), 0))
        lead_max = max(lead_min, self._int(self.lead_max_var.get(), lead_min))
        product_type = PRODUCT_TYPE_CODES.get(self.product_type_var.get(), "ready_product")
        publish_product = int(product_type != "portfolio")
        publish_portfolio = int(product_type == "portfolio")
        values = {
            "source_url": source_url,
            "normalized_url": normalize_url(source_url),
            "fingerprint": product_fingerprint(self.row["source_code"], self.row["external_id"], source_url),
            "source_title": self.title_en.get().strip(),
            "title_fa": title_fa,
            "short_description_fa": short_fa[:500],
            "description_fa": desc_fa,
            "local_category_slug": category_slug,
            "estimated_weight_grams": self._float(self.weight_var.get()),
            "material_price_per_gram": self._int(self.material_price_var.get()),
            "suggested_price": max(0, self._int(self.suggested_price_var.get())),
            "final_price": max(0, self._int(self.final_price_var.get())),
            "price_is_final": int(self._int(self.final_price_var.get()) > 0),
            "commercial_status": self.license_var.get() or "review",
            "approved_for_sale": int(self.approved_var.get()),
            "publish_as_product": publish_product,
            "publish_as_portfolio": publish_portfolio,
            "specs_fa_json": json.dumps(specs_fa, ensure_ascii=False),
            "product_type": product_type,
            "use_description": self._text_get(self.use_description_text),
            "dimensions": self.dimensions_var.get().strip(),
            "materials_json": json.dumps([x.strip() for x in self._text_get(self.materials_text).splitlines() if x.strip()], ensure_ascii=False),
            "colors_json": json.dumps([x.strip() for x in self._text_get(self.colors_text).splitlines() if x.strip()], ensure_ascii=False),
            "availability_status": AVAILABILITY_CODES.get(self.availability_var.get(), "made_to_order"),
            "stock_quantity": max(0, self._int(self.stock_var.get(), 0)),
            "lead_time_min_days": lead_min,
            "lead_time_max_days": lead_max,
            "has_3d_file": int(self.has_3d_file_var.get()),
            "source_name": self.source_name_var.get().strip(),
            "technical_features_json": json.dumps(technical_features, ensure_ascii=False),
            "keywords_json": json.dumps([x.strip() for x in self._text_get(self.keywords_text).splitlines() if x.strip()], ensure_ascii=False),
            "translation_status": "reviewed" if title_fa and desc_fa else "pending",
            "content_status": "ready" if title_fa and desc_fa else "pending",
        }
        before = dict(self.row)
        self.db.update_product(self.product_id, values)
        self.row = self.db.product(self.product_id)
        self.db.save_history(self.product_id, "studio_save", before, dict(self.row), "v8.5 product studio save")
        self.app.refresh_products()
        self.app.refresh_published()
        if self.app.current_product == self.product_id:
            self.app.load_product()
        self.refresh_checklists()
        if not silent:
            self.footer_status.set("ذخیره شد")
        return True

    # ---------- source / refetch ----------
    def open_source(self):
        url = self.source_url.get().strip()
        if url:
            webbrowser.open(url)

    def copy_source(self):
        url = self.source_url.get().strip()
        if not url:
            return
        self.clipboard_clear()
        self.clipboard_append(url)
        self.update()
        self.footer_status.set("لینک منبع کپی شد")

    def refetch(self):
        self.save(silent=True)
        self.app.current_product = self.product_id
        self.app.refetch_current_product()
        self.footer_status.set("بازیابی منبع شروع شد؛ پس از پایان، استودیو را Refresh کنید")
        self.after(1500, self.reload)

    # ---------- categories ----------
    def add_category(self):
        result = self.app.add_custom_category_dialog(parent=self)
        if result:
            slug, name = result
            self._refresh_categories(slug)
            self.category_var.set(name)
            self.footer_status.set(f"گروه «{name}» اضافه شد")

    # ---------- price ----------
    def calculate_price(self):
        weight = self._float(self.weight_var.get())
        material = self._float(self.material_price_var.get())
        if not weight or not material:
            messagebox.showwarning("3DPrintHub", "وزن تقریبی و قیمت ماده به ازای هر گرم را وارد کنید.", parent=self)
            return
        minutes = self.row["estimated_print_minutes"] if self.row else None
        price = pricing_suggestion(weight, material, minutes)
        self.suggested_price_var.set(str(price))
        if not self.final_price_var.get().strip():
            self.final_price_var.set(str(price))
        self.footer_status.set(f"قیمت پیشنهادی: {price:,} تومان")
        self.refresh_checklists()

    # ---------- image gallery ----------
    def _resolve_local(self, row, url: str, index: int) -> str:
        local_dir = Path(row["local_dir"] or "")
        if not local_dir:
            return ""
        if url.startswith("local://"):
            candidate = local_dir / "images" / url.split("local://", 1)[1]
            return str(candidate) if candidate.is_file() else ""
        manifest = local_dir / "page_extract.json"
        if manifest.is_file():
            try:
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                for item in payload.get("images", []):
                    if isinstance(item, dict) and item.get("url") == url:
                        p = Path(item.get("local_file") or "")
                        if p.is_file():
                            return str(p)
            except Exception:
                pass
        files = sorted((local_dir / "images").glob("*")) if (local_dir / "images").is_dir() else []
        if index < len(files) and files[index].is_file():
            return str(files[index])
        return ""

    def refresh_gallery(self):
        self.row = self.db.product(self.product_id)
        if self.row is None:
            return
        for child in self.gallery_inner.winfo_children():
            child.destroy()
        self._gallery_cards.clear()
        self._photos.clear()
        urls = self._json_list(self.row["images_json"])
        selected = set(self._json_list(self.row["selected_images_json"]))
        if not selected and urls:
            selected = set(urls)
        primary = self.row["primary_image_url"] or (urls[0] if urls else "")
        page = gallery_page(len(urls), self.gallery_page, self.gallery_page_size)
        self.gallery_page = page.page
        self.gallery_info.set(f"{len(urls)} تصویر • {len(selected)} انتخاب‌شده برای سایت • {len(self._bulk_image_urls)} انتخاب گروهی")
        self.gallery_page_info.set(f"صفحه {page.page + 1} از {page.total_pages} • نمایش {page.start + 1 if urls else 0} تا {page.end}")
        if not urls:
            ttk.Label(self.gallery_inner, text="هنوز تصویر واقعی برای این محصول ذخیره نشده است. بازیابی کامل را اجرا کن یا عکس اضافه کن.", style="SubHeader.TLabel").grid(row=0, column=0, padx=20, pady=30)
            return
        cols = 4
        for offset, url in enumerate(urls[page.start:page.end]):
            index = page.start + offset
            card = ttk.Frame(self.gallery_inner, padding=7, style="Card.TFrame")
            card.grid(row=offset // cols, column=offset % cols, padx=7, pady=7, sticky="n")
            bulk_var = tk.IntVar(value=1 if url in self._bulk_image_urls else 0)
            ttk.Checkbutton(
                card,
                text=f"انتخاب گروهی • #{index + 1}",
                variable=bulk_var,
                command=lambda u=url, v=bulk_var: self._set_bulk_image(u, bool(v.get())),
            ).pack(fill="x")
            image_label = ttk.Label(card, text=f"تصویر {index + 1}", anchor="center")
            image_label.pack(fill="both")
            status = tk.StringVar(value=("★ اصلی" if url == primary else "") + ("  ✓ سایت" if url in selected else "  ✗ خارج از سایت"))
            ttk.Label(card, textvariable=status, style="SubHeader.TLabel").pack(fill="x", pady=(4, 2))
            buttons1 = ttk.Frame(card)
            buttons1.pack(fill="x", pady=2)
            ttk.Button(buttons1, text="★ اصلی", command=lambda u=url: self.set_primary(u)).pack(side="left", padx=2)
            ttk.Button(buttons1, text=("حذف از سایت" if url in selected else "انتخاب سایت"), command=lambda u=url: self.toggle_selected(u)).pack(side="left", padx=2)
            buttons2 = ttk.Frame(card)
            buttons2.pack(fill="x", pady=2)
            ttk.Button(buttons2, text="باز کردن", command=lambda u=url: self.open_image(u)).pack(side="left", padx=2)
            ttk.Button(buttons2, text="حذف", command=lambda u=url: self.remove_image(u)).pack(side="left", padx=2)
            local = self._resolve_local(self.row, url, index)
            meta = {"url": url, "selected": url in selected, "primary": url == primary, "label": image_label, "status": status, "local": local}
            self._gallery_cards.append(meta)
            self._load_thumbnail(meta)
        for col in range(cols):
            self.gallery_inner.columnconfigure(col, weight=1)

    def change_gallery_page(self, delta: int):
        row = self.db.product(self.product_id)
        urls = self._json_list(row["images_json"]) if row else []
        current = gallery_page(len(urls), self.gallery_page, self.gallery_page_size)
        self.gallery_page = max(0, min(current.total_pages - 1, current.page + int(delta)))
        self.refresh_gallery()

    def _set_bulk_image(self, url: str, flag: bool):
        if flag:
            self._bulk_image_urls.add(url)
        else:
            self._bulk_image_urls.discard(url)
        self.gallery_info.set(
            f"{len(self._json_list(self.db.product(self.product_id)['images_json']))} تصویر • {len(self._bulk_image_urls)} انتخاب گروهی"
        )

    def bulk_select_page(self, flag: bool):
        row = self.db.product(self.product_id)
        urls = self._json_list(row["images_json"]) if row else []
        page = gallery_page(len(urls), self.gallery_page, self.gallery_page_size)
        page_urls = urls[page.start:page.end]
        if flag:
            self._bulk_image_urls.update(page_urls)
        else:
            self._bulk_image_urls.difference_update(page_urls)
        self.refresh_gallery()

    def keep_first_five_for_site(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        urls = self._json_list(row["images_json"])
        selected = first_site_images(urls, 5, row["primary_image_url"] or "")
        primary = selected[0] if selected else ""
        self._persist_images(urls, selected, primary)
        self.footer_status.set(f"{len(selected)} تصویر اول برای سایت انتخاب شد")

    def keep_first_five_only(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        urls = self._json_list(row["images_json"])
        keep = first_site_images(urls, 5, row["primary_image_url"] or "")
        if len(urls) <= len(keep):
            self._persist_images(urls, keep, keep[0] if keep else "")
            self.footer_status.set("محصول بیش از ۵ تصویر نداشت")
            return
        remove_count = len(urls) - len(keep)
        if not messagebox.askyesno(
            "3DPrintHub",
            f"فقط {len(keep)} تصویر اول باقی بماند و {remove_count} تصویر دیگر از لیست محصول حذف شود؟\n\nفایل‌های Cache فیزیکی پاک نمی‌شوند.",
            parent=self,
        ):
            return
        self._bulk_image_urls.clear()
        self.gallery_page = 0
        self._persist_images(keep, keep, keep[0] if keep else "")
        self.footer_status.set(f"فقط {len(keep)} تصویر در محصول باقی ماند")

    def bulk_remove_images(self):
        if not self._bulk_image_urls:
            messagebox.showwarning("3DPrintHub", "ابتدا تصاویر موردنظر را با «انتخاب گروهی» مشخص کنید.", parent=self)
            return
        if not messagebox.askyesno("3DPrintHub", f"{len(self._bulk_image_urls)} تصویر از لیست محصول حذف شود؟ فایل‌های Cache پاک نمی‌شوند.", parent=self):
            return
        row = self.db.product(self.product_id)
        urls, selected, primary = remove_gallery_urls(
            self._json_list(row["images_json"]),
            self._json_list(row["selected_images_json"]),
            row["primary_image_url"] or "",
            self._bulk_image_urls,
        )
        self._bulk_image_urls.clear()
        self._persist_images(urls, selected, primary)
        self.footer_status.set("حذف گروهی تصاویر انجام شد")

    def bulk_keep_only(self):
        if not self._bulk_image_urls:
            messagebox.showwarning("3DPrintHub", "برای نگه‌داشتن گروهی، ابتدا چند تصویر را انتخاب کنید.", parent=self)
            return
        if not messagebox.askyesno("3DPrintHub", f"فقط {len(self._bulk_image_urls)} تصویر انتخاب‌شده در محصول باقی بماند؟", parent=self):
            return
        row = self.db.product(self.product_id)
        urls, selected, primary = keep_only_gallery_urls(
            self._json_list(row["images_json"]),
            self._json_list(row["selected_images_json"]),
            row["primary_image_url"] or "",
            self._bulk_image_urls,
        )
        self._bulk_image_urls.intersection_update(urls)
        self.gallery_page = 0
        self._persist_images(urls, selected, primary)
        self.footer_status.set("فقط تصاویر انتخاب‌شده نگه داشته شدند")

    def _load_thumbnail(self, meta):
        label = meta["label"]
        local = meta.get("local") or ""
        url = meta["url"]
        if local and Path(local).is_file():
            try:
                self._apply_thumbnail(label, Path(local).read_bytes())
                return
            except Exception:
                pass
        if not url.startswith(("http://", "https://")):
            label.configure(text="تصویر محلی پیدا نشد")
            return
        label.configure(text="در حال بارگذاری...")
        source_url = self.source_url.get().strip()
        def worker():
            try:
                req = urllib_request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": source_url})
                with urllib_request.urlopen(req, timeout=25) as response:
                    raw = response.read(15_000_000)
                self.after(0, lambda: self._apply_thumbnail(label, raw))
            except Exception:
                self.after(0, lambda: label.configure(text="پیش‌نمایش ناموفق"))
        threading.Thread(target=worker, daemon=True).start()

    def _apply_thumbnail(self, label, raw: bytes):
        try:
            import io
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            image.thumbnail((210, 155), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self._photos.append(photo)
            label.configure(image=photo, text="")
        except Exception:
            label.configure(text="فرمت تصویر قابل نمایش نیست")

    def _persist_images(self, urls, selected, primary):
        urls = list(dict.fromkeys([u for u in urls if u]))
        selected = [u for u in dict.fromkeys(selected) if u in urls]
        if primary not in urls:
            primary = selected[0] if selected else (urls[0] if urls else "")
        if primary:
            if primary not in selected:
                selected.insert(0, primary)
            urls = [primary] + [u for u in urls if u != primary]
            selected = [primary] + [u for u in selected if u != primary]
        self.db.update_product(self.product_id, {
            "images_json": json.dumps(urls, ensure_ascii=False),
            "selected_images_json": json.dumps(selected, ensure_ascii=False),
            "primary_image_url": primary,
        })
        self.app.refresh_products()
        if self.app.current_product == self.product_id:
            self.app.load_product()
        self.refresh_gallery()
        self.refresh_checklists()

    def set_primary(self, url):
        row = self.db.product(self.product_id)
        urls = self._json_list(row["images_json"])
        selected = self._json_list(row["selected_images_json"])
        if url not in selected:
            selected.append(url)
        self._persist_images(urls, selected, url)
        self.footer_status.set("تصویر اصلی تغییر کرد")

    def toggle_selected(self, url):
        row = self.db.product(self.product_id)
        urls = self._json_list(row["images_json"])
        selected = self._json_list(row["selected_images_json"])
        if url in selected:
            selected = [u for u in selected if u != url]
        else:
            selected.append(url)
        self._persist_images(urls, selected, row["primary_image_url"] or "")

    def select_all_images(self, flag: bool):
        row = self.db.product(self.product_id)
        urls = self._json_list(row["images_json"])
        self._persist_images(urls, urls if flag else [], row["primary_image_url"] or "")

    def remove_image(self, url):
        if not messagebox.askyesno("3DPrintHub", "این تصویر از محصول حذف شود؟ فایل محلی فقط از لیست محصول حذف می‌شود.", parent=self):
            return
        row = self.db.product(self.product_id)
        urls = [u for u in self._json_list(row["images_json"]) if u != url]
        selected = [u for u in self._json_list(row["selected_images_json"]) if u != url]
        primary = row["primary_image_url"] if row["primary_image_url"] != url else ""
        self._persist_images(urls, selected, primary)

    def open_image(self, url):
        if url.startswith(("http://", "https://")):
            webbrowser.open(url)
            return
        if url.startswith("local://"):
            row = self.db.product(self.product_id)
            path = Path(row["local_dir"] or "") / "images" / url.split("local://", 1)[1]
            if path.is_file():
                try:
                    os.startfile(str(path))
                except Exception:
                    pass

    def add_local_images(self):
        paths = filedialog.askopenfilenames(parent=self, title="افزودن تصاویر محصول", filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.gif *.avif"), ("All files", "*.*")])
        if not paths:
            return
        row = self.db.product(self.product_id)
        local_dir = Path(row["local_dir"] or (self.app.DATA if hasattr(self.app, "DATA") else Path.cwd()))
        if not row["local_dir"]:
            local_dir = Path(self.app.DATA if hasattr(self.app, "DATA") else Path.cwd()) / "collected" / row["source_code"] / row["external_id"]
        target = local_dir / "images"
        target.mkdir(parents=True, exist_ok=True)
        urls = self._json_list(row["images_json"])
        selected = self._json_list(row["selected_images_json"])
        for src in paths:
            srcp = Path(src)
            stamp = int(time.time() * 1000)
            name = f"manual_{stamp}_{srcp.name}"
            dst = target / name
            shutil.copy2(srcp, dst)
            pseudo = f"local://{name}"
            urls.append(pseudo)
            selected.append(pseudo)
            time.sleep(0.002)
        self.db.update_product(self.product_id, {"local_dir": str(local_dir), "images_json": json.dumps(list(dict.fromkeys(urls)), ensure_ascii=False), "selected_images_json": json.dumps(list(dict.fromkeys(selected)), ensure_ascii=False)})
        self.reload()

    def add_url_image(self):
        url = simpledialog.askstring("افزودن عکس", "URL کامل تصویر را وارد کنید:", parent=self)
        if not url:
            return
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            messagebox.showwarning("3DPrintHub", "URL باید با http:// یا https:// شروع شود.", parent=self)
            return
        row = self.db.product(self.product_id)
        urls = self._json_list(row["images_json"])
        selected = self._json_list(row["selected_images_json"])
        if url not in urls:
            urls.append(url)
        if url not in selected:
            selected.append(url)
        self._persist_images(urls, selected, row["primary_image_url"] or url)

    # ---------- AI ----------
    def _source_for_ai(self):
        row = self.db.product(self.product_id)
        return self.app._source_context_for_ai(row)

    def generate_ai(self, mode: str):
        if self._ai_busy:
            return
        self.save(silent=True)
        key = self.app._openai_key()
        if not key:
            messagebox.showwarning("3DPrintHub", "OpenAI API Key تنظیم نشده است. از تب تنظیمات وارد و تستش کنید.", parent=self)
            return
        row = self.db.product(self.product_id)
        images = self._json_list(row["selected_images_json"] or row["images_json"])
        model = self.app.openai_model.get().strip()
        provider = self.app._selected_ai_provider()
        categories = self.app.get_all_categories()
        self._ai_busy = True
        self.ai_status.set(f"{provider} در حال ترجمه..." if mode == "translate" else f"{provider} در حال تولید محتوا...")
        self.footer_status.set(self.ai_status.get())

        def worker():
            try:
                pack = OpenAIContentService(key, model, provider).enrich_product(
                    self._source_for_ai(), categories, image_count=len(images), image_urls=images, mode=mode
                )
                self.after(0, lambda: self.preview_ai_pack(pack, mode))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("OpenAI", str(exc), parent=self))
                self.after(0, lambda: self.ai_status.set("خطا در OpenAI"))
            finally:
                self.after(0, lambda: setattr(self, "_ai_busy", False))
        threading.Thread(target=worker, daemon=True).start()

    def preview_ai_pack(self, pack: dict, mode: str):
        self.ai_status.set("پیشنهاد AI آماده است؛ بررسی و تأیید کنید")
        win = tk.Toplevel(self)
        win.title("پیش‌نمایش ترجمه و محتوای OpenAI")
        win.geometry("1180x820")
        win.transient(self)
        top = ttk.Frame(win, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="پیشنهاد OpenAI - قبل از اعمال قابل ویرایش", style="Header.TLabel").pack(anchor="w")
        ttk.Label(top, text="هیچ داده‌ای تا زدن «تأیید و اعمال» روی محصول نوشته نمی‌شود.", style="SubHeader.TLabel").pack(anchor="w")

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=12, pady=8)
        content = ttk.Frame(nb, padding=10)
        tech = ttk.Frame(nb, padding=10)
        seo = ttk.Frame(nb, padding=10)
        nb.add(content, text="محتوا")
        nb.add(tech, text="دسته و مشخصات")
        nb.add(seo, text="SEO و فروش")

        title = tk.StringVar(value=pack.get("title_fa") or "")
        ttk.Label(content, text="عنوان فارسی").pack(anchor="w")
        ttk.Entry(content, textvariable=title).pack(fill="x", pady=(2, 8))
        short = tk.Text(content, height=5, wrap="word")
        short.pack(fill="x", pady=4)
        short.insert("1.0", pack.get("short_description_fa") or "")
        desc = tk.Text(content, wrap="word")
        desc.pack(fill="both", expand=True, pady=4)
        desc.insert("1.0", pack.get("description_fa") or "")

        cats = tk.Text(tech, height=7, wrap="word")
        cats.pack(fill="x", pady=4)
        cats.insert("1.0", "\n".join(pack.get("categories_fa") or []))
        specs = tk.Text(tech, wrap="word")
        specs.pack(fill="both", expand=True, pady=4)
        specs_data = pack.get("specs_fa") or []
        if isinstance(specs_data, list):
            specs_data = {str(x.get("key") or ""): str(x.get("value") or "") for x in specs_data if isinstance(x, dict) and x.get("key")}
        specs.insert("1.0", json.dumps(specs_data if isinstance(specs_data, dict) else {}, ensure_ascii=False, indent=2))
        suggestion = tk.StringVar(value=pack.get("suggested_category_slug") or "")
        ttk.Label(tech, text=f"گروه پیشنهادی سایت: {suggestion.get() or '—'} | اطمینان: {float(pack.get('category_confidence') or 0)*100:.0f}%").pack(anchor="w", pady=5)

        seo_title = tk.StringVar(value=pack.get("seo_title_fa") or "")
        ttk.Label(seo, text="SEO Title").pack(anchor="w")
        ttk.Entry(seo, textvariable=seo_title).pack(fill="x", pady=(2, 8))
        seo_desc = tk.Text(seo, height=6, wrap="word")
        seo_desc.pack(fill="x", pady=4)
        seo_desc.insert("1.0", pack.get("seo_description_fa") or "")
        bullets = tk.Text(seo, height=8, wrap="word")
        bullets.pack(fill="x", pady=4)
        bullets.insert("1.0", "\n".join(pack.get("sales_bullets") or []))
        social = tk.Text(seo, height=8, wrap="word")
        social.pack(fill="both", expand=True, pady=4)
        social.insert("1.0", pack.get("social_caption_fa") or "")

        def apply_pack():
            try:
                spec_obj = json.loads(specs.get("1.0", "end").strip() or "{}")
                if not isinstance(spec_obj, dict):
                    raise ValueError("مشخصات باید JSON Object باشد")
            except Exception as exc:
                messagebox.showerror("3DPrintHub", f"مشخصات فارسی معتبر نیست:\n{exc}", parent=win)
                return
            edited = dict(pack)
            edited.update({
                "title_fa": title.get().strip(),
                "short_description_fa": short.get("1.0", "end").strip(),
                "description_fa": desc.get("1.0", "end").strip(),
                "categories_fa": [x.strip() for x in cats.get("1.0", "end").splitlines() if x.strip()],
                "specs_fa": [{"key": k, "value": str(v)} for k, v in spec_obj.items()],
                "seo_title_fa": seo_title.get().strip(),
                "seo_description_fa": seo_desc.get("1.0", "end").strip(),
                "sales_bullets": [x.strip() for x in bullets.get("1.0", "end").splitlines() if x.strip()],
                "social_caption_fa": social.get("1.0", "end").strip(),
            })
            self.app._apply_ai_pack(self.product_id, edited, open_studio=False)
            suggested_slug = edited.get("suggested_category_slug") or ""
            if suggested_slug and suggested_slug in self.app.category_slug_to_label:
                self.db.update_product(self.product_id, {"local_category_slug": suggested_slug})
            self.reload()
            self.nb.select(self.quick_tab)
            self.footer_status.set("ترجمه و محتوای OpenAI تأیید و اعمال شد")
            win.destroy()

        footer = ttk.Frame(win, padding=12)
        footer.pack(fill="x")
        ttk.Button(footer, text="تأیید و اعمال", command=apply_pack, style="Success.TButton").pack(side="right", padx=4)
        ttk.Button(footer, text="انصراف", command=win.destroy).pack(side="right", padx=4)

    # ---------- publish ----------
    def _checklist(self):
        row = self.db.product(self.product_id)
        selected = self._json_list(row["selected_images_json"])
        price = int(row["final_price"] or row["suggested_price"] or (row["price_min"] if "price_min" in row.keys() else 0) or 0)
        checks = [
            ("تصویر انتخاب‌شده", bool(selected)),
            ("تصویر اصلی", bool(row["primary_image_url"])),
            ("عنوان فارسی", bool((row["title_fa"] or "").strip())),
            ("توضیحات فارسی", bool((row["description_fa"] or "").strip())),
            ("گروه سایت", bool((row["local_category_slug"] or "").strip() and row["local_category_slug"] != "external-other")),
            ("قیمت یا حالت سفارش", price > 0 or row["product_type"] in {"portfolio", "custom_order"}),
            ("مجوز تجاری مجاز", commercial_license_allows_publish(row["commercial_status"])),
        ]
        return checks

    def refresh_checklists(self):
        # Save fields in-memory only through explicit save; checklist reflects database state.
        checks = self._checklist()
        lines = [("✅" if ok else "⬜") + " " + label for label, ok in checks]
        complete = all(ok for _, ok in checks)
        suffix = "\n\nآماده صف انتشار است." if complete else "\n\nموارد ناقص را تکمیل کن؛ انتشار فقط پس از تأیید تو انجام می‌شود."
        text = "   ".join(lines) + suffix
        self.quick_checklist.set(text)
        self.publish_checklist.set(text)

    def queue_for_publish(self, notify=True):
        if not self.save(silent=True):
            return False
        row = self.db.product(self.product_id)
        selected = self._json_list(row["selected_images_json"])
        missing = []
        if not selected:
            missing.append("حداقل یک تصویر انتخاب‌شده")
        if not (row["title_fa"] or row["source_title"]):
            missing.append("عنوان")
        if not (row["description_fa"] or "").strip():
            missing.append("توضیحات فارسی")
        if not (row["local_category_slug"] or "").strip() or row["local_category_slug"] == "external-other":
            missing.append("گروه سایت")
        if row["product_type"] == "ready_product" and int(row["final_price"] or row["suggested_price"] or (row["price_min"] if "price_min" in row.keys() else 0) or 0) <= 0:
            missing.append("قیمت")
        if not commercial_license_allows_publish(row["commercial_status"]):
            missing.append("مجوز تجاری مجاز (allowed / owned / public_domain)")
        if missing:
            messagebox.showwarning("3DPrintHub", "برای انتشار این موارد ناقص است:\n- " + "\n- ".join(missing), parent=self)
            return False
        fp = row["fingerprint"] or product_fingerprint(row["source_code"], row["external_id"], row["source_url"])
        dup = self.db.find_duplicate(row["source_code"], row["external_id"], normalize_url(row["source_url"]), fp, exclude_id=self.product_id)
        if dup:
            messagebox.showerror("3DPrintHub", f"محصول تکراری شناسایی شد: #{dup['id']}", parent=self)
            return False
        approved = int(self.approved_var.get())
        if row["product_type"] != "portfolio" and not approved:
            approved = 1 if messagebox.askyesno("3DPrintHub", "این محصول برای فروش تأیید نشده است. همین حالا برای فروش تأیید شود؟", parent=self) else 0
            self.approved_var.set(approved)
            if not approved:
                return False
        self.db.update_product(self.product_id, {
            "upload_ready": 1,
            "workflow_status": "approved",
            "publish_as_product": int(row["product_type"] != "portfolio"),
            "publish_as_portfolio": int(row["product_type"] == "portfolio"),
            "approved_for_sale": approved,
            "fingerprint": fp,
            "product_sync_error": "",
        })
        self.app.refresh_products()
        self.app.refresh_upload_queue()
        self.reload()
        self.footer_status.set("محصول آماده ارسال است")
        if notify:
            messagebox.showinfo("3DPrintHub", "محصول آماده است و به صف انتشار اضافه شد.\nبعد از ACK سایت به «منتشرشده‌ها» منتقل می‌شود.", parent=self)
        return True

    def publish_now(self):
        if not self.queue_for_publish(notify=False):
            return
        self.footer_status.set("در حال ارسال همین محصول به سایت...")
        self.app.publish_product_now(self.product_id, parent=self)

    def open_sync_log(self):
        win = tk.Toplevel(self)
        win.title(f"گزارش ارسال محصول #{self.product_id}")
        win.geometry("1040x720")
        win.transient(self)
        top = ttk.Frame(win, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="گزارش Windows → FTP → Bridge → Import → Store", style="Header.TLabel").pack(side="left")
        text = tk.Text(win, wrap="word", font=("Consolas", 10))
        text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def refresh():
            row = self.db.product(self.product_id)
            receipts = self.db.sync_receipts(self.product_id, limit=30)
            text.delete("1.0", "end")
            text.insert("1.0", receipt_lines(row, receipts))
            text.see("1.0")

        def fetch_server_log():
            current=self.app.current_product
            try:
                self.app.current_product=self.product_id
                self.app.open_current_publish_log()
            finally:
                self.app.current_product=current
        ttk.Button(top, text="تازه‌سازی", command=refresh).pack(side="right", padx=3)
        ttk.Button(top, text="لاگ سرور/کامل", command=fetch_server_log).pack(side="right", padx=3)
        ttk.Button(top, text="باز کردن پوشه لاگ", command=self.app.open_log_folder).pack(side="right", padx=3)
        try:
            ack = self._json_dict((self.db.product(self.product_id)["server_ack_json"] or "{}"))
            product_url = str(ack.get("product_url") or "")
        except Exception:
            product_url = ""
        if product_url:
            ttk.Button(top, text="باز کردن محصول در سایت", command=lambda: webbrowser.open(self.app.site_url.get().rstrip("/") + product_url)).pack(side="right", padx=3)
        refresh()

    def open_upload_tab(self):
        self.app.main_notebook.select(self.app.upload_tab)
        self.app.refresh_upload_queue()
        self.lift()
