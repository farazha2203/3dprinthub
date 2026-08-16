from __future__ import annotations

import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .epic49_desktop_schema import (
    add_available_material_color,
    deactivate_available_material_color,
    ensure_epic49_desktop_schema,
    list_available_material_colors,
    normalize_material_color_options,
)
from .epic49_product_studio import (
    LICENSE_CODE_TO_LABEL,
    LICENSE_LABEL_TO_CODE,
    ProductStudio as EditableProductStudio,
)


class ProductStudio(EditableProductStudio):
    """Epic49 final Windows studio.

    Adds the operator-facing controls that must travel with a product all the way
    to the public Store: per-product download limit, local images, price range,
    material/color choices and homepage slider selection.
    """

    def __init__(self, app, product_id: int):
        ensure_epic49_desktop_schema(app.db)
        self._material_color_rows: list[dict] = []
        self._slider_image_map: dict[str, str] = {}
        super().__init__(app, product_id)

    def _content_ui(self):
        super()._content_ui()
        legacy = ttk.Frame(self.content_tab)
        legacy.pack(fill="x", pady=(6, 0))
        ttk.Button(
            legacy,
            text="باز کردن استودیوی کامل SEO",
            command=lambda: self.app.open_content_studio(self.product_id),
        ).pack(side="right")

    # ---------- images ----------
    def _images_ui(self):
        super()._images_ui()
        current_children = self.images_tab.winfo_children()
        tools = ttk.LabelFrame(
            self.images_tab,
            text="کنترل دریافت و تصاویر دستی این محصول",
            padding=8,
            style="Card.TLabelframe",
        )
        pack_kwargs = {"fill": "x", "pady": (0, 8)}
        if current_children:
            pack_kwargs["before"] = current_children[0]
        tools.pack(**pack_kwargs)
        self.product_image_limit_var = tk.StringVar(value="10")
        ttk.Label(tools, text="حداکثر تعداد عکس در هر بازیابی").pack(side="left", padx=(0, 5))
        ttk.Spinbox(
            tools,
            from_=1,
            to=100,
            textvariable=self.product_image_limit_var,
            width=6,
        ).pack(side="left", padx=(0, 12))
        ttk.Button(
            tools,
            text="♻ بازیابی با همین سقف",
            command=self.refetch,
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            tools,
            text="＋ افزودن عکس از کامپیوتر",
            command=self.add_local_images,
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Label(
            tools,
            text="عکس دستی داخل دیتای پایدار برنامه کپی می‌شود و همراه Batch به سایت می‌رود.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=6)

    def refetch(self):
        try:
            limit = max(1, min(100, int(float(self.product_image_limit_var.get() or 10))))
        except Exception:
            limit = 10
        self.product_image_limit_var.set(str(limit))
        self.db.update_product(self.product_id, {"download_image_limit": limit})
        old_value = None
        try:
            if hasattr(self.app, "direct_image_limit"):
                old_value = self.app.direct_image_limit.get()
                self.app.direct_image_limit.set(limit)
            super().refetch()
        finally:
            if old_value is not None:
                try:
                    self.app.direct_image_limit.set(old_value)
                except Exception:
                    pass

    # ---------- commerce / stock choices ----------
    def _commerce_ui(self):
        super()._commerce_ui()
        panel = ttk.LabelFrame(
            self.commerce_tab,
            text="قیمت و متریال/رنگ قابل فروش از همین برنامه",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.pack(fill="both", expand=False, pady=(10, 0))

        price = ttk.Frame(panel)
        price.pack(fill="x", pady=(0, 8))
        self.price_min_var = tk.StringVar(value="0")
        self.price_max_var = tk.StringVar(value="0")
        ttk.Label(price, text="حداقل قیمت (تومان)").pack(side="left")
        ttk.Entry(price, textvariable=self.price_min_var, width=18).pack(side="left", padx=(5, 16))
        ttk.Label(price, text="حداکثر قیمت (تومان)").pack(side="left")
        ttk.Entry(price, textvariable=self.price_max_var, width=18).pack(side="left", padx=(5, 16))
        ttk.Label(
            price,
            text="اگر فقط یک قیمت داری، حداقل و حداکثر را برابر بگذار.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

        body = ttk.Frame(panel)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(body)
        right.pack(side="right", fill="y", padx=(8, 0))

        ttk.Label(left, text="متریال/رنگ‌های موجود — برای این محصول چند مورد را انتخاب کن").pack(anchor="w")
        self.material_color_list = tk.Listbox(
            left,
            selectmode="extended",
            exportselection=False,
            height=8,
            font=("Tahoma", 10),
        )
        self.material_color_list.pack(fill="both", expand=True, pady=(4, 0))
        ttk.Button(right, text="＋ افزودن متریال/رنگ", command=self._add_material_color).pack(fill="x", pady=2)
        ttk.Button(right, text="− حذف از فهرست موجود", command=self._deactivate_material_colors, style="Danger.TButton").pack(fill="x", pady=2)
        ttk.Button(right, text="↻ تازه‌سازی فهرست", command=self._refresh_material_inventory).pack(fill="x", pady=2)
        ttk.Label(
            right,
            text="مثال:\nPLA / صورتی\nPLA / سبز\nPETG / مشکی",
            justify="left",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(8, 0))

    def _refresh_material_inventory(self):
        if not hasattr(self, "material_color_list"):
            return
        row = self.db.product(self.product_id)
        selected = normalize_material_color_options(
            row["material_color_options_json"] if row is not None else "[]"
        )
        selected_keys = {(x["material"].casefold(), x["color"].casefold()) for x in selected}
        self._material_color_rows = list_available_material_colors(self.db)
        self.material_color_list.delete(0, "end")
        for index, item in enumerate(self._material_color_rows):
            suffix = f"  {item['hex_code']}" if item.get("hex_code") else ""
            self.material_color_list.insert("end", f"{item['material_name']}  /  {item['color_name']}{suffix}")
            key = (str(item["material_name"]).casefold(), str(item["color_name"]).casefold())
            if key in selected_keys:
                self.material_color_list.selection_set(index)

    def _add_material_color(self):
        material = simpledialog.askstring(
            "متریال موجود",
            "نام متریال را وارد کن (مثلاً PLA، PETG، ABS، PPS-CF):",
            parent=self,
        )
        if material is None:
            return
        color = simpledialog.askstring(
            "رنگ موجود",
            f"رنگ موجود برای {material.strip()} را وارد کن (مثلاً صورتی):",
            parent=self,
        )
        if color is None:
            return
        hex_code = simpledialog.askstring(
            "کد رنگ اختیاری",
            "اگر کد HEX را می‌دانی وارد کن؛ در غیر این صورت خالی بگذار:",
            parent=self,
        )
        try:
            created = add_available_material_color(self.db, material, color, hex_code or "")
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self)
            return
        self._refresh_material_inventory()
        for index, item in enumerate(self._material_color_rows):
            if int(item["id"]) == int(created["id"]):
                self.material_color_list.selection_set(index)
                self.material_color_list.see(index)
                break
        self.footer_status.set("متریال/رنگ اضافه شد و برای این محصول انتخاب شد")

    def _deactivate_material_colors(self):
        indexes = list(self.material_color_list.curselection())
        if not indexes:
            messagebox.showinfo("3DPrintHub", "حداقل یک متریال/رنگ را انتخاب کن.", parent=self)
            return
        if not messagebox.askyesno(
            "3DPrintHub",
            "موارد انتخاب‌شده از فهرست موجودی برنامه غیرفعال شوند؟ محصولات قبلی و اطلاعات سایت حذف نمی‌شوند.",
            parent=self,
        ):
            return
        for index in indexes:
            deactivate_available_material_color(self.db, int(self._material_color_rows[index]["id"]))
        self._refresh_material_inventory()

    def _selected_material_colors(self) -> list[dict]:
        output = []
        for index in self.material_color_list.curselection() if hasattr(self, "material_color_list") else ():
            item = self._material_color_rows[int(index)]
            output.append({
                "material": str(item["material_name"]).strip(),
                "color": str(item["color_name"]).strip(),
                "hex": str(item.get("hex_code") or "").strip(),
            })
        return normalize_material_color_options(output)

    # ---------- publish / homepage slider ----------
    def _publish_ui(self):
        super()._publish_ui()
        slider = ttk.LabelFrame(
            self.publish_tab,
            text="اسلایدر صفحه اصلی",
            padding=10,
            style="Card.TLabelframe",
        )
        slider.pack(fill="x", pady=(8, 0))
        self.slider_enabled_var = tk.IntVar(value=0)
        self.slider_image_label_var = tk.StringVar(value="")
        self.slider_sort_var = tk.StringVar(value="100")
        ttk.Checkbutton(
            slider,
            text="نمایش این محصول در اسلایدر صفحه اصلی",
            variable=self.slider_enabled_var,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Label(slider, text="عکس اسلایدر").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.slider_image_box = ttk.Combobox(
            slider,
            textvariable=self.slider_image_label_var,
            state="readonly",
            width=72,
        )
        self.slider_image_box.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(slider, text="ترتیب نمایش").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(slider, from_=0, to=10000, textvariable=self.slider_sort_var, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(
            slider,
            text="عکس از بین تصاویر انتخاب‌شده همین محصول است؛ فایل محلی هم بعد از Publish به Media سایت منتقل می‌شود.",
            style="SubHeader.TLabel",
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        slider.columnconfigure(1, weight=1)

    def _refresh_slider_images(self):
        if not hasattr(self, "slider_image_box"):
            return
        row = self.db.product(self.product_id)
        if row is None:
            return
        urls = self._json_list(row["selected_images_json"] or row["images_json"])
        if not urls and row["primary_image_url"]:
            urls = [row["primary_image_url"]]
        mapping = {}
        for index, raw in enumerate(urls, 1):
            url = str(raw or "").strip()
            if not url:
                continue
            if url.startswith("local://"):
                short = Path(url.split("local://", 1)[1]).name
            else:
                short = Path(url.split("?", 1)[0]).name or url
            label = f"{index:02d} — {short[:80]}"
            mapping[label] = url
        self._slider_image_map = mapping
        labels = list(mapping)
        self.slider_image_box.configure(values=labels)
        wanted = str(row["homepage_slider_image_url"] or "").strip()
        chosen = next((label for label, url in mapping.items() if url == wanted), "")
        if not chosen and labels:
            chosen = labels[0]
        self.slider_image_label_var.set(chosen)

    # ---------- sync controls ----------
    def _reconcile_license_controls(self) -> str:
        if not hasattr(self, "publish_license_label_var"):
            return self.license_var.get() or "review"

        row = self.db.product(self.product_id)
        database_code = (row["commercial_status"] if row is not None else "review") or "review"
        quick_code = self.license_var.get() or database_code
        publish_code = LICENSE_LABEL_TO_CODE.get(
            self.publish_license_label_var.get(), database_code
        )

        if quick_code == publish_code:
            chosen = quick_code
        elif quick_code != database_code and publish_code == database_code:
            chosen = quick_code
        elif publish_code != database_code and quick_code == database_code:
            chosen = publish_code
        else:
            chosen = quick_code

        if chosen not in LICENSE_CODE_TO_LABEL:
            chosen = "review"
        self.license_var.set(chosen)
        self.publish_license_label_var.set(LICENSE_CODE_TO_LABEL[chosen])
        return chosen

    def reload(self):
        ensure_epic49_desktop_schema(self.db)
        super().reload()
        row = self.db.product(self.product_id)
        if row is None:
            return
        if hasattr(self, "product_image_limit_var"):
            self.product_image_limit_var.set(str(max(1, int(row["download_image_limit"] or 10))))
        if hasattr(self, "price_min_var"):
            fallback = int(row["final_price"] or row["suggested_price"] or 0)
            price_min = int(row["price_min"] or fallback or 0)
            price_max = int(row["price_max"] or price_min or 0)
            self.price_min_var.set(str(price_min))
            self.price_max_var.set(str(price_max))
        if hasattr(self, "slider_enabled_var"):
            self.slider_enabled_var.set(int(row["homepage_slider_enabled"] or 0))
            self.slider_sort_var.set(str(int(row["homepage_slider_sort_order"] or 100)))
        self._refresh_material_inventory()
        self._refresh_slider_images()

    def save(self, silent=False):
        self._reconcile_license_controls()
        try:
            image_limit = max(1, min(100, int(float(self.product_image_limit_var.get() or 10)))) if hasattr(self, "product_image_limit_var") else 10
            price_min = max(0, int(float(str(self.price_min_var.get() or "0").replace(",", "")))) if hasattr(self, "price_min_var") else 0
            price_max = max(0, int(float(str(self.price_max_var.get() or "0").replace(",", "")))) if hasattr(self, "price_max_var") else 0
            slider_sort = max(0, int(float(self.slider_sort_var.get() or 100))) if hasattr(self, "slider_sort_var") else 100
        except Exception:
            if not silent:
                messagebox.showerror("3DPrintHub", "مقادیر تعداد عکس، قیمت یا ترتیب اسلایدر عددی نیستند.", parent=self)
            return False
        if price_min and price_max and price_max < price_min:
            if not silent:
                messagebox.showerror("3DPrintHub", "حداکثر قیمت نمی‌تواند از حداقل قیمت کمتر باشد.", parent=self)
            return False
        if price_min and not price_max:
            price_max = price_min
        if price_max and not price_min:
            price_min = price_max

        selected_options = self._selected_material_colors()
        if selected_options and hasattr(self, "materials_text") and hasattr(self, "colors_text"):
            materials = list(dict.fromkeys(item["material"] for item in selected_options))
            colors = list(dict.fromkeys(item["color"] for item in selected_options))
            self._text_set(self.materials_text, "\n".join(materials))
            self._text_set(self.colors_text, "\n".join(colors))

        if not super().save(silent=True):
            return False

        slider_url = ""
        if hasattr(self, "slider_image_label_var"):
            slider_url = self._slider_image_map.get(self.slider_image_label_var.get(), "")
        values = {
            "download_image_limit": image_limit,
            "price_min": price_min,
            "price_max": price_max,
            "material_color_options_json": json.dumps(selected_options, ensure_ascii=False),
            "homepage_slider_enabled": int(self.slider_enabled_var.get()) if hasattr(self, "slider_enabled_var") else 0,
            "homepage_slider_image_url": slider_url,
            "homepage_slider_sort_order": slider_sort,
        }
        self.db.update_product(self.product_id, values)
        self.row = self.db.product(self.product_id)
        if self.app.current_product == self.product_id:
            try:
                self.app.load_product()
            except Exception:
                pass
        self.refresh_checklists()
        if not silent:
            self.footer_status.set("همه تنظیمات محصول، قیمت، متریال/رنگ و انتشار ذخیره شد")
        return True
