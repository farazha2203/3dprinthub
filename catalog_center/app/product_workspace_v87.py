from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .epic49_product_studio_final import ProductStudio as Epic49ProductStudio
from .version import APP_VERSION


class ProductWorkspace(Epic49ProductStudio):
    """Single official product workspace for Catalog Center 8.7.

    All legacy editing/publishing capability is preserved, but duplicate fast paths
    are hidden and the operator follows one six-step workflow.
    """

    SECTION_LABELS = [
        ("quick", "۱. اطلاعات پایه"),
        ("commerce", "۲. سفارش و قیمت"),
        ("images", "۳. تصاویر"),
        ("content", "۴. محتوا و SEO"),
        ("specs", "۵. منبع و فایل"),
        ("publish", "۶. بررسی و انتشار"),
    ]

    def __init__(self, app, product_id: int):
        super().__init__(app, product_id)
        self.title(f"Product Workspace | 3DPrintHub Catalog Center {APP_VERSION}")
        self.geometry("1540x940")
        self.minsize(1240, 780)

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.layout("Workspace87.TNotebook.Tab", [])
        except Exception:
            pass
        style.configure("Workspace87.TNotebook", borderwidth=0, background="#f4f7fa")

        header = tk.Frame(self, bg="#071827", padx=18, pady=12)
        header.pack(fill="x")
        title_box = tk.Frame(header, bg="#071827")
        title_box.pack(side="left", fill="x", expand=True)
        self.header_title = tk.StringVar(value="محصول")
        self.header_meta = tk.StringVar(value="")
        tk.Label(title_box, textvariable=self.header_title, bg="#071827", fg="white", font=("Tahoma", 17, "bold")).pack(anchor="w")
        tk.Label(title_box, textvariable=self.header_meta, bg="#071827", fg="#b9c8d6", font=("Tahoma", 9)).pack(anchor="w", pady=(3, 0))

        actions = tk.Frame(header, bg="#071827")
        actions.pack(side="right")
        ttk.Button(actions, text="ذخیره", command=self.save, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="گزارش انتشار", command=self.open_sync_log).pack(side="left", padx=3)
        ttk.Button(actions, text="انتشار روی سایت", command=self.publish_now, style="Publish.TButton").pack(side="left", padx=3)

        source_bar = ttk.Frame(self, padding=(16, 8, 16, 8))
        source_bar.pack(fill="x")
        ttk.Label(source_bar, text="منبع محصول").pack(side="left")
        self.source_url = tk.StringVar()
        ttk.Entry(source_bar, textvariable=self.source_url).pack(side="left", fill="x", expand=True, padx=7)
        ttk.Button(source_bar, text="باز کردن منبع", command=self.open_source).pack(side="left", padx=3)
        ttk.Button(source_bar, text="کپی لینک", command=self.copy_source).pack(side="left", padx=3)

        body = ttk.Frame(self, padding=(12, 0, 12, 8))
        body.pack(fill="both", expand=True)

        # The stage rail can grow after later phases append readiness/AI panels.
        # Keep it in a real vertical Canvas+Scrollbar so no control becomes
        # unreachable on 780/900px-height Windows displays.
        rail_host = tk.Frame(body, bg="#0b2238", width=228)
        rail_host.pack(side="right", fill="y", padx=(8, 0))
        rail_host.pack_propagate(False)
        rail_canvas = tk.Canvas(
            rail_host,
            bg="#0b2238",
            highlightthickness=0,
            bd=0,
            relief="flat",
            takefocus=0,
        )
        rail_scroll = ttk.Scrollbar(rail_host, orient="vertical", command=rail_canvas.yview)
        rail_canvas.configure(yscrollcommand=rail_scroll.set)
        rail_scroll.pack(side="right", fill="y")
        rail_canvas.pack(side="left", fill="both", expand=True)
        rail = tk.Frame(rail_canvas, bg="#0b2238", padx=8, pady=10)
        rail_window = rail_canvas.create_window((0, 0), window=rail, anchor="nw")

        def _sync_rail_scrollregion(_event=None):
            try:
                rail_canvas.configure(scrollregion=rail_canvas.bbox("all"))
            except Exception:
                pass

        def _sync_rail_width(event):
            try:
                rail_canvas.itemconfigure(rail_window, width=max(1, int(event.width)))
            except Exception:
                pass
            _sync_rail_scrollregion()

        def _rail_mousewheel(event):
            try:
                pointer = self.winfo_containing(*self.winfo_pointerxy())
                current = pointer
                inside = False
                while current is not None:
                    if current in {rail, rail_canvas, rail_host}:
                        inside = True
                        break
                    current = getattr(current, "master", None)
                if not inside:
                    return None
                delta = int(getattr(event, "delta", 0) or 0)
                if delta:
                    rail_canvas.yview_scroll(-1 if delta > 0 else 1, "units")
                    return "break"
            except Exception:
                return None
            return None

        rail.bind("<Configure>", _sync_rail_scrollregion, add="+")
        rail_canvas.bind("<Configure>", _sync_rail_width, add="+")
        self.bind("<MouseWheel>", _rail_mousewheel, add="+")
        self._workspace_rail_host = rail_host
        self._workspace_rail_canvas = rail_canvas
        self._workspace_rail_scrollbar = rail_scroll
        self._workspace_rail = rail

        content = ttk.Frame(body)
        content.pack(side="left", fill="both", expand=True)

        self.nb = ttk.Notebook(content, style="Workspace87.TNotebook")
        self.nb.pack(fill="both", expand=True)
        self.quick_tab = ttk.Frame(self.nb, padding=14)
        self.commerce_tab = ttk.Frame(self.nb, padding=14)
        self.images_tab = ttk.Frame(self.nb, padding=12)
        self.content_tab = ttk.Frame(self.nb, padding=14)
        self.specs_tab = ttk.Frame(self.nb, padding=14)
        self.publish_tab = ttk.Frame(self.nb, padding=14)
        pages = {
            "quick": self.quick_tab,
            "commerce": self.commerce_tab,
            "images": self.images_tab,
            "content": self.content_tab,
            "specs": self.specs_tab,
            "publish": self.publish_tab,
        }
        for key, label in self.SECTION_LABELS:
            self.nb.add(pages[key], text=label)

        tk.Label(rail, text="مراحل محصول", bg="#0b2238", fg="#f6d77a", font=("Tahoma", 11, "bold")).pack(anchor="e", pady=(0, 8))
        self._section_buttons = {}
        for key, label in self.SECTION_LABELS:
            button = tk.Button(
                rail,
                text=label,
                command=lambda k=key: self.select_section(k),
                anchor="e",
                relief="flat",
                bd=0,
                bg="#0b2238",
                fg="#d9e4ee",
                activebackground="#123452",
                activeforeground="white",
                font=("Tahoma", 10, "bold"),
                padx=10,
                pady=9,
                cursor="hand2",
            )
            button.pack(fill="x", pady=2)
            self._section_buttons[key] = button

        ttk.Separator(rail, orient="horizontal").pack(fill="x", pady=10)
        tk.Label(
            rail,
            text="تمام اطلاعات این Workspace\nدر دیتای پایدار برنامه ذخیره می‌شود.",
            bg="#0b2238",
            fg="#91a4b5",
            justify="right",
            font=("Tahoma", 9),
        ).pack(anchor="e")

        self._quick_ui()
        self._commerce_ui()
        self._images_ui()
        self._content_ui()
        self._specs_ui()
        self._publish_ui()
        self._remove_duplicate_legacy_actions()
        self._normalize_button_labels()
        _sync_rail_scrollregion()

        footer = ttk.Frame(self, padding=(12, 4, 12, 10))
        footer.pack(fill="x")
        self.footer_status = tk.StringVar(value="آماده")
        ttk.Label(footer, textvariable=self.footer_status, style="SubHeader.TLabel").pack(side="left", fill="x", expand=True)
        ttk.Button(footer, text="ذخیره", command=self.save).pack(side="right", padx=3)
        ttk.Button(footer, text="آماده‌سازی انتشار", command=self.queue_for_publish, style="Success.TButton").pack(side="right", padx=3)
        ttk.Button(footer, text="انتشار روی سایت", command=self.publish_now, style="Publish.TButton").pack(side="right", padx=3)
        self.select_section("quick")

    def _commerce_ui(self):
        # Skip the 8.6 final wrapper here: it appended a pack-managed panel to a
        # grid-managed parent, which can raise a TclError at runtime. Build the base
        # commerce editor, then append all Epic49 controls with grid only.
        super(Epic49ProductStudio, self)._commerce_ui()
        frame = self.commerce_tab
        self.price_min_var = tk.StringVar(value="0")
        self.price_max_var = tk.StringVar(value="0")

        panel = ttk.LabelFrame(
            frame,
            text="بازه قیمت و متریال/رنگ قابل فروش",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.grid(row=7, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        panel.columnconfigure(1, weight=1)
        panel.columnconfigure(3, weight=1)
        panel.rowconfigure(2, weight=1)

        ttk.Label(panel, text="حداقل قیمت (تومان)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(panel, textvariable=self.price_min_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(panel, text="حداکثر قیمت (تومان)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(panel, textvariable=self.price_max_var).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        ttk.Label(
            panel,
            text="برای قیمت ثابت، حداقل و حداکثر را برابر قرار بده.",
            style="SubHeader.TLabel",
        ).grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 6))

        self.material_color_list = tk.Listbox(
            panel,
            selectmode="extended",
            exportselection=False,
            height=7,
            font=("Tahoma", 10),
        )
        self.material_color_list.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        actions = ttk.Frame(panel)
        actions.grid(row=2, column=3, sticky="nsew", padx=5, pady=5)
        ttk.Button(actions, text="افزودن متریال/رنگ", command=self._add_material_color, style="Primary.TButton").pack(fill="x", pady=2)
        ttk.Button(actions, text="غیرفعال‌کردن انتخاب‌شده", command=self._deactivate_material_colors, style="Danger.TButton").pack(fill="x", pady=2)
        ttk.Button(actions, text="تازه‌سازی فهرست", command=self._refresh_material_inventory).pack(fill="x", pady=2)
        ttk.Label(actions, text="نمونه:\nPLA / صورتی\nPETG / مشکی", style="SubHeader.TLabel", justify="left").pack(anchor="w", pady=(8, 0))
        frame.rowconfigure(6, weight=1)
        frame.rowconfigure(7, weight=1)

    def select_section(self, key: str):
        page_map = {
            "quick": self.quick_tab,
            "commerce": self.commerce_tab,
            "images": self.images_tab,
            "content": self.content_tab,
            "specs": self.specs_tab,
            "publish": self.publish_tab,
        }
        page = page_map.get(key, self.quick_tab)
        self.nb.select(page)
        for section, button in getattr(self, "_section_buttons", {}).items():
            active = section == key
            button.configure(
                bg="#c99a2e" if active else "#0b2238",
                fg="#071827" if active else "#d9e4ee",
                activebackground="#d8ad49" if active else "#123452",
            )

    def _remove_duplicate_legacy_actions(self):
        for child in self.quick_tab.winfo_children():
            try:
                if isinstance(child, ttk.LabelFrame) and str(child.cget("text")) == "مسیر یک‌دقیقه‌ای":
                    child.grid_remove()
            except Exception:
                pass
        for child in self._walk(self.content_tab):
            if isinstance(child, ttk.Button):
                try:
                    if "استودیوی کامل SEO" in str(child.cget("text")):
                        child.pack_forget()
                except Exception:
                    pass

    def _walk(self, root):
        for child in root.winfo_children():
            yield child
            yield from self._walk(child)

    def _normalize_button_labels(self):
        replacements = {
            "♻ بازیابی با همین سقف": "بازیابی با سقف انتخابی",
            "＋ افزودن عکس از کامپیوتر": "افزودن عکس از کامپیوتر",
            "✨ ترجمه دقیق EN → FA": "ترجمه با هوش مصنوعی",
            "✨ تولید محتوای فروشگاهی": "تولید محتوای فروشگاهی",
            "💾 ذخیره همه تغییرات": "ذخیره همه تغییرات",
            "💾 ذخیره تنظیمات انتشار": "ذخیره تنظیمات انتشار",
            "🚀 ارسال همین محصول به سایت": "انتشار همین محصول روی سایت",
            "🧾 گزارش ارسال": "گزارش انتشار",
        }
        for child in self._walk(self):
            if not isinstance(child, ttk.Button):
                continue
            try:
                text = str(child.cget("text"))
                if text in replacements:
                    child.configure(text=replacements[text])
            except Exception:
                pass
