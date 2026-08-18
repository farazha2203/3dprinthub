from __future__ import annotations

import json
import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_desktop_schema import (
    COLOR_TYPES,
    DEFAULT_MATERIALS,
    add_available_material_color,
    ensure_epic49_desktop_schema,
    list_available_material_colors,
    normalize_color_options,
    normalize_material_color_options,
    normalize_material_options,
)


COLOR_LABEL = dict(COLOR_TYPES)


def _unique_colors(rows: list[dict], legacy: list[dict]) -> list[dict]:
    output: list[dict] = []
    seen = set()
    for item in [*rows, *legacy]:
        name = str(item.get("color_name") or item.get("color") or item.get("name") or "").strip()
        if not name:
            continue
        kind = str(item.get("color_type") or "solid").strip().lower() or "solid"
        key = (name.casefold(), kind)
        if key in seen:
            continue
        seen.add(key)
        output.append({
            "name": name,
            "hex": str(item.get("hex_code") or item.get("hex") or "").strip(),
            "color_type": kind,
            "secondary_hex": str(item.get("secondary_hex") or "").strip(),
            "tertiary_hex": str(item.get("tertiary_hex") or "").strip(),
        })
    return output


def _selected_state_from_row(row) -> tuple[list[str], list[dict]]:
    materials = normalize_material_options(row["material_options_json"] if row is not None else "[]")
    colors = normalize_color_options(row["color_options_json"] if row is not None else "[]")
    legacy = normalize_material_color_options(row["material_color_options_json"] if row is not None else "[]")
    if not materials:
        materials = normalize_material_options([item["material"] for item in legacy])
    if not colors:
        colors = normalize_color_options([
            {
                "name": item["color"],
                "hex": item.get("hex", ""),
                "color_type": item.get("color_type", "solid"),
                "secondary_hex": item.get("secondary_hex", ""),
                "tertiary_hex": item.get("tertiary_hex", ""),
            }
            for item in legacy
        ])
    return materials, colors


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_material_color_picker_installed", False):
        return

    original_commerce_ui = workspace_class._commerce_ui
    original_reload = workspace_class.reload
    original_save = workspace_class.save

    def _commerce_ui(self):
        original_commerce_ui(self)
        ensure_epic49_desktop_schema(self.db)
        self.material_checkbox_vars: dict[str, tk.IntVar] = {}
        self.color_checkbox_vars: dict[tuple[str, str], tk.IntVar] = {}
        self._picker_color_defs: dict[tuple[str, str], dict] = {}

        # Reuse the existing commerce card so price fields remain exactly where
        # they were. Only the old extended Listbox/actions row is replaced.
        old_list = getattr(self, "material_color_list", None)
        panel = getattr(old_list, "master", None)
        if panel is None:
            panel = ttk.LabelFrame(
                self.commerce_tab,
                text="متریال‌ها و رنگ‌های قابل فروش",
                padding=10,
                style="Card.TLabelframe",
            )
            panel.grid(row=8, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        else:
            try:
                panel.configure(text="بازه قیمت + انتخاب تیک‌زدنی متریال و رنگ")
            except Exception:
                pass
            for child in list(panel.winfo_children()):
                try:
                    info = child.grid_info()
                    if int(info.get("row", -1)) == 2:
                        child.grid_remove()
                except Exception:
                    pass

        picker = ttk.Frame(panel, padding=(2, 4))
        picker.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
        picker.columnconfigure(0, weight=1)
        picker.columnconfigure(1, weight=2)

        materials_box = ttk.LabelFrame(picker, text="متریال‌ها — تیک بزن", padding=8)
        materials_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        colors_box = ttk.LabelFrame(picker, text="رنگ‌ها — تیک بزن", padding=8)
        colors_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self._epic49_materials_box = materials_box
        self._epic49_colors_box = colors_box

        tools = ttk.Frame(picker)
        tools.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(tools, text="＋ تعریف رنگ جدید", command=self._epic49_open_add_color_dialog, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(tools, text="↻ تازه‌سازی", command=self._epic49_refresh_option_picker).pack(side="left", padx=3)
        ttk.Label(
            tools,
            text="نوع رنگ: ساده، شفاف/شیشه‌ای، نیمه‌شفاف، متالیک، Silk، دو رنگ، چند رنگ یا گرادیانی. انتخاب‌ها به Batch و سایت منتقل می‌شوند.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=5)

        self._epic49_refresh_option_picker()

    def _epic49_refresh_option_picker(self):
        if not hasattr(self, "_epic49_materials_box"):
            return
        ensure_epic49_desktop_schema(self.db)
        row = self.db.product(self.product_id)
        selected_materials, selected_colors = _selected_state_from_row(row)
        selected_material_keys = {name.casefold() for name in selected_materials}
        selected_color_keys = {(item["name"].casefold(), item.get("color_type", "solid")) for item in selected_colors}

        inventory = list_available_material_colors(self.db)
        legacy = normalize_material_color_options(row["material_color_options_json"] if row is not None else "[]")
        materials = []
        seen_materials = set()
        for name in [*DEFAULT_MATERIALS, *selected_materials, *[str(item.get("material_name") or "") for item in inventory]]:
            value = str(name or "").strip()
            if not value or value.casefold() in seen_materials:
                continue
            seen_materials.add(value.casefold())
            materials.append(value)

        for child in self._epic49_materials_box.winfo_children():
            child.destroy()
        self.material_checkbox_vars = {}
        for index, name in enumerate(materials):
            var = tk.IntVar(value=1 if name.casefold() in selected_material_keys else 0)
            self.material_checkbox_vars[name] = var
            ttk.Checkbutton(self._epic49_materials_box, text=name, variable=var).grid(
                row=index // 3, column=index % 3, sticky="w", padx=5, pady=3
            )

        color_defs = _unique_colors(inventory, legacy)
        for item in selected_colors:
            key = (item["name"].casefold(), item.get("color_type", "solid"))
            if all((c["name"].casefold(), c.get("color_type", "solid")) != key for c in color_defs):
                color_defs.append(item)

        for child in self._epic49_colors_box.winfo_children():
            child.destroy()
        self.color_checkbox_vars = {}
        self._picker_color_defs = {}
        for index, item in enumerate(color_defs):
            key = (item["name"].casefold(), item.get("color_type", "solid"))
            self._picker_color_defs[key] = item
            var = tk.IntVar(value=1 if key in selected_color_keys else 0)
            self.color_checkbox_vars[key] = var
            kind = COLOR_LABEL.get(item.get("color_type", "solid"), item.get("color_type", "solid"))
            swatch = "/".join(x for x in [item.get("hex"), item.get("secondary_hex"), item.get("tertiary_hex")] if x)
            label = f"{item['name']}  •  {kind}" + (f"  {swatch}" if swatch else "")
            ttk.Checkbutton(self._epic49_colors_box, text=label, variable=var).grid(
                row=index // 2, column=index % 2, sticky="w", padx=5, pady=3
            )

        if not color_defs:
            ttk.Label(
                self._epic49_colors_box,
                text="هنوز رنگی تعریف نشده. ابتدا متریال‌ها را تیک بزن و «تعریف رنگ جدید» را بزن.",
                style="SubHeader.TLabel",
            ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

    def _epic49_open_add_color_dialog(self):
        selected_materials = [name for name, var in self.material_checkbox_vars.items() if var.get()]
        if not selected_materials:
            messagebox.showinfo("3DPrintHub", "ابتدا حداقل یک متریال را تیک بزن.", parent=self)
            return

        win = tk.Toplevel(self)
        win.title("تعریف رنگ برای متریال‌های انتخاب‌شده")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)
        body = ttk.Frame(win, padding=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        color_name = tk.StringVar(value="")
        color_type = tk.StringVar(value=COLOR_TYPES[0][1])
        hex1 = tk.StringVar(value="")
        hex2 = tk.StringVar(value="")
        hex3 = tk.StringVar(value="")

        ttk.Label(body, text="متریال‌ها").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(body, text="، ".join(selected_materials), style="SubHeader.TLabel", wraplength=520).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(body, text="نام رنگ").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(body, textvariable=color_name, width=46).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(body, text="نوع رنگ").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(body, textvariable=color_type, values=[label for _code, label in COLOR_TYPES], state="readonly", width=40).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(body, text="HEX اصلی").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(body, textvariable=hex1).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(body, text="HEX دوم (برای ترکیبی)").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(body, textvariable=hex2).grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(body, text="HEX سوم (اختیاری)").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(body, textvariable=hex3).grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        def save_color():
            name = color_name.get().strip()
            if not name:
                messagebox.showerror("3DPrintHub", "نام رنگ را وارد کن.", parent=win)
                return
            label_to_code = {label: code for code, label in COLOR_TYPES}
            kind = label_to_code.get(color_type.get(), "solid")
            try:
                for material in selected_materials:
                    add_available_material_color(
                        self.db,
                        material,
                        name,
                        hex1.get().strip(),
                        kind,
                        hex2.get().strip(),
                        hex3.get().strip(),
                    )
            except Exception as exc:
                messagebox.showerror("3DPrintHub", str(exc), parent=win)
                return
            win.destroy()
            self._epic49_refresh_option_picker()
            key = (name.casefold(), kind)
            if key in self.color_checkbox_vars:
                self.color_checkbox_vars[key].set(1)
            self.footer_status.set("رنگ جدید برای متریال‌های انتخاب‌شده تعریف و تیک شد")

        actions = ttk.Frame(body)
        actions.grid(row=6, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(actions, text="انصراف", command=win.destroy).pack(side="right", padx=3)
        ttk.Button(actions, text="ذخیره رنگ", command=save_color, style="Primary.TButton").pack(side="right", padx=3)

    def _selected_materials(self) -> list[str]:
        return [name for name, var in getattr(self, "material_checkbox_vars", {}).items() if var.get()]

    def _selected_colors(self) -> list[dict]:
        result = []
        for key, var in getattr(self, "color_checkbox_vars", {}).items():
            if not var.get():
                continue
            item = dict(self._picker_color_defs.get(key) or {})
            if item:
                result.append(item)
        return normalize_color_options(result)

    def _selected_material_colors(self):
        materials = self._selected_materials()
        colors = self._selected_colors()
        output = []
        for material in materials:
            for color in colors:
                # Keep the inventory table material-aware even though the UI
                # lets the operator tick materials and colors independently.
                add_available_material_color(
                    self.db,
                    material,
                    color["name"],
                    color.get("hex", ""),
                    color.get("color_type", "solid"),
                    color.get("secondary_hex", ""),
                    color.get("tertiary_hex", ""),
                )
                output.append({
                    "material": material,
                    "color": color["name"],
                    "hex": color.get("hex", ""),
                    "color_type": color.get("color_type", "solid"),
                    "secondary_hex": color.get("secondary_hex", ""),
                    "tertiary_hex": color.get("tertiary_hex", ""),
                })
        return normalize_material_color_options(output)

    def reload(self):
        original_reload(self)
        if hasattr(self, "_epic49_materials_box"):
            self._epic49_refresh_option_picker()

    def save(self, silent=False):
        ok = original_save(self, silent=True)
        if not ok:
            return False
        if hasattr(self, "material_checkbox_vars"):
            materials = self._selected_materials()
            colors = self._selected_colors()
            pairs = self._selected_material_colors()
            self.db.update_product(
                self.product_id,
                {
                    "material_options_json": json.dumps(materials, ensure_ascii=False),
                    "color_options_json": json.dumps(colors, ensure_ascii=False),
                    "material_color_options_json": json.dumps(pairs, ensure_ascii=False),
                },
            )
            self.row = self.db.product(self.product_id)
        if not silent:
            self.footer_status.set("محصول، متریال‌ها، رنگ‌ها، SEO و تنظیمات انتشار ذخیره شد")
        return True

    workspace_class._commerce_ui = _commerce_ui
    workspace_class._epic49_refresh_option_picker = _epic49_refresh_option_picker
    workspace_class._epic49_open_add_color_dialog = _epic49_open_add_color_dialog
    workspace_class._selected_materials = _selected_materials
    workspace_class._selected_colors = _selected_colors
    workspace_class._selected_material_colors = _selected_material_colors
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_material_color_picker_installed = True
