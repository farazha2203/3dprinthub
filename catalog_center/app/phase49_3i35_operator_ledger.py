from __future__ import annotations

import copy
import json
from decimal import Decimal
from uuid import uuid4

import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_desktop_schema import (
    add_available_material_color,
    effective_filament_offer_price_per_gram,
    list_available_material_colors,
    normalize_material_color_options,
)

PHASE = "49.3I.35"

LEDGER_COLUMNS = {
    "sales_profile_ledger_json": "TEXT NOT NULL DEFAULT '[]'",
    "seo_manual_approved": "INTEGER NOT NULL DEFAULT 0",
    "source_review_manual_approved": "INTEGER NOT NULL DEFAULT 0",
}


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    changed = False
    for name, ddl in LEDGER_COLUMNS.items():
        if name not in columns:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
            changed = True
    if changed:
        db.conn.commit()


def _row_value(row, key, default=""):
    if row is None:
        return default
    try:
        return row[key] if key in row.keys() else default
    except Exception:
        return default


def _json_list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _number(value, default=0):
    try:
        number = Decimal(str(value if value not in (None, "") else default).replace(",", "").strip())
    except Exception:
        number = Decimal(str(default))
    return float(number) if number % 1 else int(number)


def _integer(value, default=0) -> int:
    try:
        return max(0, int(float(str(value if value not in (None, "") else default).replace(",", "").strip())))
    except Exception:
        return max(0, int(default))


def normalize_production_row(item: dict | None = None) -> dict:
    source = dict(item or {})
    return {
        "weight_grams": _number(source.get("weight_grams"), 0),
        "print_time_minutes": max(1, _integer(source.get("print_time_minutes"), 60)),
        "support_weight_grams": _number(source.get("support_weight_grams"), 0),
    }


def normalize_ledger_profile(item: dict | None, index: int = 1) -> dict:
    source = dict(item or {})
    rows = [
        normalize_production_row(row)
        for row in _json_list(source.get("production_rows"))
        if isinstance(row, dict)
    ]
    if not rows:
        rows = [
            normalize_production_row(
                {
                    "weight_grams": source.get("weight_grams") or source.get("final_weight_grams"),
                    "print_time_minutes": source.get("print_time_minutes") or 60,
                    "support_weight_grams": source.get("support_weight_grams") or 0,
                }
            )
        ]
    materials = normalize_material_color_options(source.get("material_options") or source.get("material_color_options") or [])
    return {
        "key": str(source.get("key") or f"ledger-{uuid4().hex[:12]}")[:80],
        "name": str(source.get("name") or f"پروفایل {index}")[:120],
        "size_label": str(source.get("size_label") or "")[:80],
        "part_length_cm": _number(source.get("part_length_cm"), 0),
        "part_width_cm": _number(source.get("part_width_cm"), 0),
        "part_height_cm": _number(source.get("part_height_cm"), 0),
        "production_rows": rows,
        "material_options": materials,
        "pricing_strategy": str(source.get("pricing_strategy") or "dynamic")[:30],
        "price_min": _integer(source.get("price_min") or source.get("fixed_price"), 0),
        "price_max": _integer(source.get("price_max") or source.get("fixed_price"), 0),
        "support_cost_multiplier": _number(source.get("support_cost_multiplier"), 1),
        "assembly_fee": _integer(source.get("assembly_fee"), 0),
        "product_type": str(source.get("product_type") or "ready_product")[:40],
        "availability_status": str(source.get("availability_status") or "made_to_order")[:40],
        "stock_quantity": _integer(source.get("stock_quantity"), 0),
        "lead_time_min_days": _integer(source.get("lead_time_min_days"), 1),
        "lead_time_max_days": _integer(source.get("lead_time_max_days"), 3),
        "is_default": bool(source.get("is_default", index == 1)),
        "is_active": bool(source.get("is_active", True)),
        "sort_order": _integer(source.get("sort_order"), index * 10),
    }


def legacy_profiles_to_ledger(flat_profiles: list[dict]) -> list[dict]:
    output = []
    for index, item in enumerate(flat_profiles, 1):
        if not isinstance(item, dict):
            continue
        output.append(
            normalize_ledger_profile(
                {
                    **item,
                    "key": str(item.get("key") or f"legacy-{index}").split("--r", 1)[0],
                    "production_rows": [
                        {
                            "weight_grams": item.get("weight_grams") or item.get("final_weight_grams") or 0,
                            "print_time_minutes": item.get("print_time_minutes") or 60,
                            "support_weight_grams": item.get("support_weight_grams") or 0,
                        }
                    ],
                    "material_options": [
                        {
                            "material": item.get("material") or "",
                            "brand": item.get("brand") or item.get("brand_name") or "",
                            "manufacturer": item.get("manufacturer") or item.get("manufacturer_name") or "",
                            "color": item.get("color") or "",
                        }
                    ] if (item.get("material") or item.get("color")) else [],
                    "price_min": item.get("fixed_price") or 0,
                    "price_max": item.get("fixed_price") or 0,
                },
                index,
            )
        )
    seen = set()
    unique = []
    for item in output:
        key = item["key"]
        if key in seen:
            item["key"] = f"{key}-{uuid4().hex[:6]}"
        seen.add(item["key"])
        unique.append(item)
    return unique


def flatten_ledger_profiles(ledger: list[dict]) -> list[dict]:
    flat: list[dict] = []
    for p_index, raw_profile in enumerate(ledger, 1):
        profile = normalize_ledger_profile(raw_profile, p_index)
        if not profile["is_active"]:
            continue
        materials = profile["material_options"] or [{}]
        fixed = 0
        if profile["pricing_strategy"] == "fixed":
            low = _integer(profile.get("price_min"), 0)
            high = _integer(profile.get("price_max"), low)
            if low > 0 and (high <= 0 or high == low):
                fixed = low
        for r_index, production in enumerate(profile["production_rows"], 1):
            row = normalize_production_row(production)
            for m_index, offer in enumerate(materials, 1):
                weight = _number(row["weight_grams"], 0)
                support = _number(row["support_weight_grams"], 0)
                brand = str(offer.get("brand") or offer.get("brand_name") or "").strip()
                color = str(offer.get("color") or offer.get("color_name") or "").strip()
                material = str(offer.get("material") or offer.get("material_name") or "").strip()
                suffix = f"r{r_index}-m{m_index}"
                label_bits = [profile["name"]]
                if weight:
                    label_bits.append(f"{weight:g} گرم" if isinstance(weight, float) else f"{weight} گرم")
                if brand:
                    label_bits.append(brand)
                if color:
                    label_bits.append(color)
                flat.append(
                    {
                        "key": f"{profile['key']}--{suffix}"[:80],
                        "name": " • ".join(label_bits)[:120],
                        "description": "",
                        "size_label": profile["size_label"],
                        "weight_grams": weight,
                        "material_weight_grams": _number(weight + support, 0),
                        "support_weight_grams": support,
                        "print_time_minutes": row["print_time_minutes"],
                        "build_profile": "standard",
                        "material": material,
                        "brand": brand,
                        "manufacturer": str(offer.get("manufacturer") or offer.get("manufacturer_name") or "")[:120],
                        "color": color,
                        "quality": "",
                        "roll_weight_grams": _integer(offer.get("roll_weight_grams"), 1000),
                        "stock_roll_count": _number(offer.get("stock_roll_count"), 0),
                        "purchase_price_per_roll": _integer(offer.get("purchase_price_per_roll"), 0),
                        "sale_price_per_roll": _integer(offer.get("sale_price_per_roll"), 0),
                        "usd_price_per_roll": _number(offer.get("usd_price_per_roll"), 0),
                        "usd_fx_rate_toman": _number(offer.get("usd_fx_rate_toman"), 0),
                        "print_hourly_rate": _integer(offer.get("print_hourly_rate"), 0),
                        "supervision_hourly_rate": _integer(offer.get("supervision_hourly_rate"), 0),
                        "preheat_hours": _number(offer.get("preheat_hours"), 0),
                        "preheat_temperature_c": _number(offer.get("preheat_temperature_c"), 0),
                        "preheat_hourly_rate": _integer(offer.get("preheat_hourly_rate"), 0),
                        "filament_image_url": str(offer.get("filament_image_url") or "")[:500],
                        "part_length_cm": profile["part_length_cm"],
                        "part_width_cm": profile["part_width_cm"],
                        "part_height_cm": profile["part_height_cm"],
                        "fixed_price": (
                            (
                                _integer(offer.get("fixed_product_price"), 0)
                                or fixed
                            )
                            if profile["pricing_strategy"] == "fixed"
                            else 0
                        ),
                        "stock_status": profile["availability_status"] if profile["availability_status"] in {
                            "made_to_order", "in_stock", "preorder", "out_of_stock"
                        } else "made_to_order",
                        "stock_quantity": profile["stock_quantity"],
                        "track_inventory": bool(profile["stock_quantity"] > 0),
                        "is_default": bool(profile["is_default"] and r_index == 1 and m_index == 1),
                        "is_active": True,
                        "sort_order": profile["sort_order"] * 100 + r_index * 10 + m_index,
                    }
                )
    return flat


def offer_price_preview(item: dict, production: dict) -> int:
    per_gram = Decimal(str(effective_filament_offer_price_per_gram(item) or 0))
    grams = Decimal(str(_number(production.get("weight_grams"), 0))) + Decimal(
        str(_number(production.get("support_weight_grams"), 0))
    )
    return max(0, int(per_gram * grams))


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i35_operator_ledger", False):
        return

    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_save = workspace_class.save
    original_selected_materials = getattr(workspace_class, "_selected_material_colors", None)

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        ensure_schema(app.db)
        self._phase49_3i35_ledger = []
        self._phase49_3i35_edit_key = ""
        self._phase49_3i35_profile_name_var = tk.StringVar(value="پروفایل ۱")
        self._phase49_3i35_profile_size_var = tk.StringVar(value="")
        self._phase49_3i35_profile_length_var = tk.StringVar(value="")
        self._phase49_3i35_profile_width_var = tk.StringVar(value="")
        self._phase49_3i35_profile_height_var = tk.StringVar(value="")
        self._phase49_3i35_production_rows = []
        self._phase49_3i35_build_production_matrix()
        self._phase49_3i35_build_material_actions()
        self._phase49_3i35_build_ledger_ui()
        self.reload()

    def selected_offers(self):
        output = []
        rows = list(getattr(self, "_material_color_rows", []) or [])
        widget = getattr(self, "material_color_list", None)
        if widget is None:
            return []
        for raw_index in widget.curselection():
            try:
                item = dict(rows[int(raw_index)])
            except Exception:
                continue
            output.append(
                {
                    "material": str(item.get("material_name") or "").strip(),
                    "brand": str(item.get("brand_name") or "").strip(),
                    "manufacturer": str(item.get("manufacturer_name") or "").strip(),
                    "color": str(item.get("color_name") or "").strip(),
                    "hex": str(item.get("hex_code") or "").strip(),
                    "color_type": str(item.get("color_type") or "solid"),
                    "secondary_hex": str(item.get("secondary_hex") or ""),
                    "tertiary_hex": str(item.get("tertiary_hex") or ""),
                    "roll_weight_grams": _integer(item.get("roll_weight_grams"), 1000),
                    "stock_roll_count": _number(item.get("stock_roll_count"), 0),
                    "purchase_price_per_roll": _integer(item.get("purchase_price_per_roll"), 0),
                    "sale_price_per_roll": _integer(item.get("sale_price_per_roll"), 0),
                    "usd_price_per_roll": _number(item.get("usd_price_per_roll"), 0),
                    "usd_fx_rate_toman": _number(item.get("usd_fx_rate_toman"), 0),
                    "print_hourly_rate": _integer(item.get("print_hourly_rate"), 0),
                    "supervision_hourly_rate": _integer(item.get("supervision_hourly_rate"), 0),
                    "preheat_hours": _number(item.get("preheat_hours"), 0),
                    "preheat_temperature_c": _number(item.get("preheat_temperature_c"), 0),
                    "preheat_hourly_rate": _integer(item.get("preheat_hourly_rate"), 0),
                    "filament_image_url": str(item.get("filament_image_url") or ""),
                    "fixed_product_price": _integer(item.get("fixed_product_price"), 0),
                }
            )
        return normalize_material_color_options(output)

    def _selected_material_colors(self):
        return selected_offers(self)

    def build_material_actions(self):
        # The modern material/color picker (Phase49 material_color_picker) owns
        # this surface and already uses grid inside the legacy commerce card.
        # 3I.39 replaces/hides that card with the professional Offer workflow,
        # so mounting the obsolete Listbox actions here is both unnecessary and
        # unsafe: using pack in the grid-managed parent aborts ProductWorkspace
        # construction before 3I.39/3I.40 can build their visible UI.
        if getattr(self, "_epic49_materials_box", None) is not None:
            return
        widget = getattr(self, "material_color_list", None)
        if widget is None:
            return
        host = widget.master
        actions = ttk.Frame(host)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(
            actions,
            text="✓ همه متریال/رنگ‌ها",
            command=lambda: (widget.selection_set(0, "end"), self.footer_status.set("همه متریال/رنگ‌ها انتخاب شدند")),
        ).pack(side="right", padx=3)
        ttk.Button(
            actions,
            text="پاک کردن انتخاب",
            command=lambda: widget.selection_clear(0, "end"),
        ).pack(side="right", padx=3)
        ttk.Button(
            actions,
            text="ثبت انتخاب‌ها روی همین محصول",
            command=self._phase49_3i35_commit_material_selection,
            style="Success.TButton",
        ).pack(side="right", padx=3)
        self._phase49_3i35_material_actions = actions

    def commit_material_selection(self):
        selected = selected_offers(self)
        materials = []
        colors = []
        for item in selected:
            if item["material"] and item["material"] not in materials:
                materials.append(item["material"])
            if item["color"] and item["color"] not in colors:
                colors.append(item["color"])
        self.db.update_product(
            int(self.product_id),
            {
                "material_color_options_json": json.dumps(selected, ensure_ascii=False),
                "materials_json": json.dumps(materials, ensure_ascii=False),
                "colors_json": json.dumps(colors, ensure_ascii=False),
            },
        )
        self.row = self.db.product(int(self.product_id))
        refresher = getattr(self, "_phase49_refresh_readiness", None)
        if callable(refresher):
            refresher()
        self.footer_status.set(
            f"{len(selected)} متریال/رنگ محلی ثبت شد • Save کلی و Refresh محصولات انجام نشد"
        )
        return True

    def build_production_matrix(self):
        panel = getattr(self, "_phase49_3f_pricing_panel", None)
        if panel is None:
            return
        for child in list(panel.winfo_children()):
            try:
                row = int(child.grid_info().get("row", -1))
            except Exception:
                continue
            if row in {2, 3, 4}:
                child.grid_remove()

        frame = ttk.LabelFrame(
            panel,
            text="وزن / زمان چاپ / ساپورت — ورودی مشترک Snapshot پروفایل",
            padding=7,
            style="Card.TLabelframe",
        )
        frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=4, pady=5)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(5, weight=1)

        headers = ("ردیف", "وزن قطعه (گرم)", "زمان چاپ (دقیقه)", "وزن ساپورت (گرم)")
        for col, text in enumerate(headers):
            ttk.Label(frame, text=text, font=("Tahoma", 9, "bold")).grid(
                row=0, column=col, sticky="w", padx=4, pady=2
            )

        rows_host = ttk.Frame(frame)
        rows_host.grid(row=1, column=0, columnspan=6, sticky="ew")
        rows_host.columnconfigure(1, weight=1)
        rows_host.columnconfigure(3, weight=1)
        rows_host.columnconfigure(5, weight=1)
        self._phase49_3i35_production_host = rows_host

        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, columnspan=6, sticky="ew", pady=(5, 0))
        ttk.Button(
            actions,
            text="+ ردیف وزن/زمان جدید",
            command=lambda: self._phase49_3i35_add_production_row({}),
        ).pack(side="right", padx=3)
        ttk.Button(
            actions,
            text="− حذف آخرین ردیف",
            command=self._phase49_3i35_remove_production_row,
        ).pack(side="right", padx=3)
        self._phase49_3i35_consumption_var = tk.StringVar(value="")
        ttk.Label(
            actions,
            textvariable=self._phase49_3i35_consumption_var,
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

        seed = {
            "weight_grams": getattr(getattr(self, "part_weight_grams_var", None), "get", lambda: "")(),
            "print_time_minutes": getattr(getattr(self, "standard_print_minutes_var", None), "get", lambda: "60")(),
            "support_weight_grams": getattr(getattr(self, "support_weight_grams_var", None), "get", lambda: "0")(),
        }
        self._phase49_3i35_add_production_row(seed)
        self._phase49_3i35_add_production_row({})
        self._phase49_3i35_add_production_row({})
        self._phase49_3i35_production_frame = frame

    def add_production_row(self, values=None):
        values = normalize_production_row(values or {})
        index = len(self._phase49_3i35_production_rows)
        vars_ = {
            "weight_grams": tk.StringVar(value=str(values["weight_grams"] or "")),
            "print_time_minutes": tk.StringVar(value=str(values["print_time_minutes"] if values["weight_grams"] else "")),
            "support_weight_grams": tk.StringVar(value=str(values["support_weight_grams"] or "")),
        }
        row_no = index + 1
        ttk.Label(self._phase49_3i35_production_host, text=str(row_no)).grid(row=index, column=0, padx=4, pady=2)
        ttk.Entry(self._phase49_3i35_production_host, textvariable=vars_["weight_grams"]).grid(row=index, column=1, sticky="ew", padx=4, pady=2)
        ttk.Label(self._phase49_3i35_production_host, text="گرم").grid(row=index, column=2, padx=(0, 6))
        ttk.Entry(self._phase49_3i35_production_host, textvariable=vars_["print_time_minutes"]).grid(row=index, column=3, sticky="ew", padx=4, pady=2)
        ttk.Label(self._phase49_3i35_production_host, text="دقیقه").grid(row=index, column=4, padx=(0, 6))
        ttk.Entry(self._phase49_3i35_production_host, textvariable=vars_["support_weight_grams"]).grid(row=index, column=5, sticky="ew", padx=4, pady=2)
        self._phase49_3i35_production_rows.append(vars_)
        for var in vars_.values():
            var.trace_add("write", lambda *_args: self._phase49_3i35_refresh_consumption())
        self._phase49_3i35_refresh_consumption()

    def remove_production_row(self):
        if len(self._phase49_3i35_production_rows) <= 1:
            return
        index = len(self._phase49_3i35_production_rows) - 1
        self._phase49_3i35_production_rows.pop()
        for child in list(self._phase49_3i35_production_host.grid_slaves(row=index)):
            child.destroy()
        self._phase49_3i35_refresh_consumption()

    def production_values(self):
        output = []
        for vars_ in self._phase49_3i35_production_rows:
            weight = _number(vars_["weight_grams"].get(), 0)
            if weight <= 0:
                continue
            output.append(
                normalize_production_row(
                    {
                        "weight_grams": weight,
                        "print_time_minutes": vars_["print_time_minutes"].get() or 60,
                        "support_weight_grams": vars_["support_weight_grams"].get() or 0,
                    }
                )
            )
        return output

    def set_production_values(self, values):
        while self._phase49_3i35_production_rows:
            self._phase49_3i35_production_rows.pop()
        for child in list(self._phase49_3i35_production_host.winfo_children()):
            child.destroy()
        rows = [normalize_production_row(item) for item in values if isinstance(item, dict)]
        if not rows:
            rows = [normalize_production_row({})]
        for item in rows:
            add_production_row(self, item)
        while len(self._phase49_3i35_production_rows) < 3:
            add_production_row(self, {})
        self._phase49_3i35_refresh_consumption()

    def refresh_consumption(self):
        rows = production_values(self)
        if not rows:
            self._phase49_3i35_consumption_var.set("حداقل یک ردیف وزن لازم است")
            return
        totals = [
            _number(item["weight_grams"], 0) + _number(item["support_weight_grams"], 0)
            for item in rows
        ]
        self._phase49_3i35_consumption_var.set(
            "مصرف فیلامنت ردیف‌ها: " + " / ".join(f"{value:g}g" if isinstance(value, float) else f"{value}g" for value in totals)
        )
        first = rows[0]
        for attr, value in (
            ("part_weight_grams_var", first["weight_grams"]),
            ("support_weight_grams_var", first["support_weight_grams"]),
            ("standard_print_minutes_var", first["print_time_minutes"]),
        ):
            var = getattr(self, attr, None)
            if var is not None:
                try:
                    var.set(str(value))
                except Exception:
                    pass

    def build_ledger_ui(self):
        old = getattr(self, "_phase49_3i34_panel", None)
        if old is not None:
            try:
                old.grid_remove()
            except Exception:
                pass
        panel = ttk.LabelFrame(
            self.commerce_tab,
            text="ثبت پروفایل‌ها — هر ردیف یک Snapshot مستقل از فرم بالا",
            padding=9,
            style="Card.TLabelframe",
        )
        panel.grid(row=60, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        panel.columnconfigure(0, weight=1)

        draft = ttk.Frame(panel)
        draft.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        ttk.Label(draft, text="نام پروفایل").pack(side="right", padx=3)
        ttk.Entry(draft, textvariable=self._phase49_3i35_profile_name_var, width=24).pack(side="right", padx=3)
        ttk.Label(draft, text="سایز").pack(side="right", padx=(12, 3))
        ttk.Entry(draft, textvariable=self._phase49_3i35_profile_size_var, width=18).pack(side="right", padx=3)
        ttk.Button(
            draft,
            text="ثبت پروفایل از فرم بالا",
            command=self._phase49_3i35_register_profile,
            style="Success.TButton",
        ).pack(side="right", padx=(12, 3))
        ttk.Button(
            draft,
            text="پروفایل جدید از آخرین",
            command=self._phase49_3i35_new_from_last,
        ).pack(side="right", padx=3)

        tree = ttk.Treeview(
            panel,
            columns=("name", "size", "rows", "materials", "price"),
            show="headings",
            height=8,
            selectmode="browse",
        )
        for key, label, width in (
            ("name", "پروفایل", 210),
            ("size", "سایز", 110),
            ("rows", "ردیف‌های وزن/زمان", 150),
            ("materials", "متریال/برند/رنگ", 300),
            ("price", "سیاست قیمت", 160),
        ):
            tree.heading(key, text=label)
            tree.column(key, width=width, anchor="center")
        tree.grid(row=1, column=0, sticky="nsew")
        panel.rowconfigure(1, weight=1)
        self._phase49_3i35_tree = tree

        actions = ttk.Frame(panel)
        actions.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(actions, text="بارگذاری انتخابی در فرم بالا", command=self._phase49_3i35_load_selected).pack(side="right", padx=3)
        ttk.Button(actions, text="به‌روزرسانی فقط پروفایل انتخابی", command=self._phase49_3i35_update_selected, style="Primary.TButton").pack(side="right", padx=3)
        ttk.Button(actions, text="حذف پروفایل انتخابی", command=self._phase49_3i35_delete_selected, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Label(
            actions,
            text="تغییر فرم بالا، پروفایل‌های ثبت‌شده را عوض نمی‌کند؛ فقط ثبت/به‌روزرسانی صریح Snapshot را تغییر می‌دهد.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)
        self._phase49_3i35_panel = panel

    def current_snapshot(self, key="", *, name=None):
        rows = production_values(self)
        if not rows:
            raise ValueError("حداقل یک ردیف وزن/زمان چاپ معتبر لازم است.")
        selected = selected_offers(self)
        price_min = _integer(getattr(getattr(self, "price_min_var", None), "get", lambda: 0)(), 0)
        price_max = _integer(getattr(getattr(self, "price_max_var", None), "get", lambda: price_min)(), price_min)
        strategy = str(getattr(getattr(self, "pricing_strategy_var", None), "get", lambda: "dynamic")() or "dynamic")
        return normalize_ledger_profile(
            {
                "key": key or f"ledger-{uuid4().hex[:12]}",
                "name": name if name is not None else self._phase49_3i35_profile_name_var.get(),
                "size_label": self._phase49_3i35_profile_size_var.get(),
                "part_length_cm": self._phase49_3i35_profile_length_var.get(),
                "part_width_cm": self._phase49_3i35_profile_width_var.get(),
                "part_height_cm": self._phase49_3i35_profile_height_var.get(),
                "production_rows": rows,
                "material_options": selected,
                "pricing_strategy": strategy,
                "price_min": price_min,
                "price_max": price_max,
                "support_cost_multiplier": getattr(getattr(self, "support_cost_multiplier_var", None), "get", lambda: 1)(),
                "assembly_fee": getattr(getattr(self, "assembly_fee_var", None), "get", lambda: 0)(),
                "product_type": getattr(getattr(self, "product_type_var", None), "get", lambda: "ready_product")(),
                "availability_status": getattr(getattr(self, "availability_var", None), "get", lambda: "made_to_order")(),
                "stock_quantity": getattr(getattr(self, "stock_var", None), "get", lambda: 0)(),
                "lead_time_min_days": getattr(getattr(self, "lead_min_var", None), "get", lambda: 1)(),
                "lead_time_max_days": getattr(getattr(self, "lead_max_var", None), "get", lambda: 3)(),
                "sort_order": (len(self._phase49_3i35_ledger) + 1) * 10,
            },
            len(self._phase49_3i35_ledger) + 1,
        )

    def persist_ledger(self):
        flat = flatten_ledger_profiles(self._phase49_3i35_ledger)
        values = {
            "sales_profile_ledger_json": json.dumps(self._phase49_3i35_ledger, ensure_ascii=False),
            "sales_profiles_json": json.dumps(flat, ensure_ascii=False),
            "sales_profile_selection_mode": "size_weight",
            "sales_profile_selector_label": "ابتدا سایز و سپس وزن/گزینه ساخت را انتخاب کنید",
        }
        prices = [
            _integer(item.get("fixed_price"), 0)
            for item in flat
            if _integer(item.get("fixed_price"), 0) > 0
        ]
        if prices:
            values["price_min"] = min(prices)
            values["price_max"] = max(prices)
        self.db.update_product(int(self.product_id), values)
        self.row = self.db.product(int(self.product_id))
        return flat

    def refresh_ledger_tree(self, select_key=""):
        tree = self._phase49_3i35_tree
        for iid in tree.get_children():
            tree.delete(iid)
        for index, profile in enumerate(self._phase49_3i35_ledger, 1):
            materials = []
            for item in profile.get("material_options") or []:
                label = " / ".join(
                    part for part in (
                        str(item.get("material") or ""),
                        str(item.get("brand") or ""),
                        str(item.get("color") or ""),
                    ) if part
                )
                if label and label not in materials:
                    materials.append(label)
            strategy = str(profile.get("pricing_strategy") or "dynamic")
            pmin = _integer(profile.get("price_min"), 0)
            pmax = _integer(profile.get("price_max"), pmin)
            if strategy == "fixed" and pmin:
                price_label = f"{pmin:,}" if pmin == pmax else f"{pmin:,}–{pmax:,}"
            else:
                price_label = "محاسباتی"
            tree.insert(
                "",
                "end",
                iid=profile["key"],
                values=(
                    ("★ " if profile.get("is_default") else "") + str(profile.get("name") or f"پروفایل {index}"),
                    profile.get("size_label") or "—",
                    len(profile.get("production_rows") or []),
                    " | ".join(materials[:4]) or "طبق انتخاب فرم",
                    price_label,
                ),
            )
        wanted = select_key if select_key in tree.get_children() else ""
        if wanted:
            tree.selection_set(wanted)
            tree.focus(wanted)
            tree.see(wanted)

    def register_profile(self):
        try:
            snapshot = current_snapshot(self)
        except Exception as exc:
            messagebox.showwarning("ثبت پروفایل", str(exc), parent=self)
            return False
        if not snapshot["name"].strip():
            messagebox.showwarning("ثبت پروفایل", "نام پروفایل لازم است.", parent=self)
            return False
        if not snapshot["size_label"].strip():
            messagebox.showwarning("ثبت پروفایل", "سایز پروفایل لازم است.", parent=self)
            return False
        if not self._phase49_3i35_ledger:
            snapshot["is_default"] = True
        self._phase49_3i35_ledger.append(snapshot)
        persist_ledger(self)
        refresh_ledger_tree(self, snapshot["key"])
        self._phase49_3i35_edit_key = ""
        self.footer_status.set(
            f"پروفایل «{snapshot['name']}» Snapshot شد • فرم بالا و لیست محصولات Refresh نشد"
        )
        return True

    def new_from_last(self):
        source = self._phase49_3i35_ledger[-1] if self._phase49_3i35_ledger else None
        if source:
            apply_snapshot_to_draft(self, copy.deepcopy(source))
        self._phase49_3i35_edit_key = ""
        self._phase49_3i35_profile_name_var.set(f"پروفایل {len(self._phase49_3i35_ledger) + 1}")
        self.footer_status.set("دیتای آخرین پروفایل در فرم بالا بارگذاری شد؛ برای ساخت ردیف جدید نام/سایز را تغییر بده و ثبت کن")

    def selected_profile(self):
        selection = self._phase49_3i35_tree.selection()
        if not selection:
            return None
        key = str(selection[0])
        return next((item for item in self._phase49_3i35_ledger if item.get("key") == key), None)

    def load_selected(self):
        profile = selected_profile(self)
        if profile is None:
            messagebox.showinfo("پروفایل", "یک پروفایل را انتخاب کن.", parent=self)
            return
        apply_snapshot_to_draft(self, profile)
        self._phase49_3i35_edit_key = profile["key"]
        self.footer_status.set("Snapshot انتخابی در فرم بالا بارگذاری شد؛ تا «به‌روزرسانی» نزنی اصل ردیف تغییر نمی‌کند")

    def update_selected(self):
        profile = selected_profile(self)
        if profile is None:
            messagebox.showinfo("پروفایل", "یک پروفایل را انتخاب کن.", parent=self)
            return False
        try:
            updated = current_snapshot(self, profile["key"], name=self._phase49_3i35_profile_name_var.get())
        except Exception as exc:
            messagebox.showwarning("پروفایل", str(exc), parent=self)
            return False
        updated["is_default"] = bool(profile.get("is_default"))
        updated["sort_order"] = profile.get("sort_order", 10)
        index = self._phase49_3i35_ledger.index(profile)
        self._phase49_3i35_ledger[index] = updated
        persist_ledger(self)
        refresh_ledger_tree(self, updated["key"])
        self.footer_status.set(f"فقط پروفایل «{updated['name']}» به‌روزرسانی شد")
        return True

    def delete_selected(self):
        profile = selected_profile(self)
        if profile is None:
            return
        if not messagebox.askyesno("حذف پروفایل", f"پروفایل «{profile.get('name')}» حذف شود؟", parent=self):
            return
        self._phase49_3i35_ledger = [item for item in self._phase49_3i35_ledger if item["key"] != profile["key"]]
        if self._phase49_3i35_ledger and not any(item.get("is_default") for item in self._phase49_3i35_ledger):
            self._phase49_3i35_ledger[0]["is_default"] = True
        persist_ledger(self)
        refresh_ledger_tree(self)
        self._phase49_3i35_edit_key = ""
        self.footer_status.set("پروفایل انتخابی حذف شد؛ سایر Snapshotها تغییر نکردند")

    def apply_snapshot_to_draft(self, profile):
        profile = normalize_ledger_profile(profile, 1)
        self._phase49_3i35_profile_name_var.set(profile["name"])
        self._phase49_3i35_profile_size_var.set(profile["size_label"])
        self._phase49_3i35_profile_length_var.set(str(profile.get("part_length_cm") or ""))
        self._phase49_3i35_profile_width_var.set(str(profile.get("part_width_cm") or ""))
        self._phase49_3i35_profile_height_var.set(str(profile.get("part_height_cm") or ""))
        set_production_values(self, profile["production_rows"])
        for attr, value in (
            ("price_min_var", profile["price_min"]),
            ("price_max_var", profile["price_max"]),
            ("pricing_strategy_var", profile["pricing_strategy"]),
            ("support_cost_multiplier_var", profile["support_cost_multiplier"]),
            ("assembly_fee_var", profile["assembly_fee"]),
        ):
            var = getattr(self, attr, None)
            if var is not None:
                try:
                    var.set(str(value))
                except Exception:
                    pass
        target = {
            (
                str(item.get("material") or "").casefold(),
                str(item.get("brand") or "").casefold(),
                str(item.get("color") or "").casefold(),
            )
            for item in profile["material_options"]
        }
        widget = getattr(self, "material_color_list", None)
        rows = list(getattr(self, "_material_color_rows", []) or [])
        if widget is not None:
            widget.selection_clear(0, "end")
            for index, item in enumerate(rows):
                key = (
                    str(item.get("material_name") or "").casefold(),
                    str(item.get("brand_name") or "").casefold(),
                    str(item.get("color_name") or "").casefold(),
                )
                if key in target:
                    widget.selection_set(index)
        refresh_consumption(self)

    def reload(self):
        result = original_reload(self)
        if not hasattr(self, "_phase49_3i35_tree"):
            return result
        ensure_schema(self.db)
        row = self.db.product(int(self.product_id))
        raw_ledger = _json_list(_row_value(row, "sales_profile_ledger_json", "[]"))
        ledger = [
            normalize_ledger_profile(item, index + 1)
            for index, item in enumerate(raw_ledger)
            if isinstance(item, dict)
        ]
        if not ledger:
            legacy = [
                item for item in _json_list(_row_value(row, "sales_profiles_json", "[]"))
                if isinstance(item, dict)
            ]
            ledger = legacy_profiles_to_ledger(legacy)
            if ledger:
                self._phase49_3i35_ledger = ledger
                persist_ledger(self)
        self._phase49_3i35_ledger = ledger
        refresh_ledger_tree(self)
        if ledger and not self._phase49_3i35_edit_key:
            apply_snapshot_to_draft(self, ledger[-1])
        old = getattr(self, "_phase49_3i34_panel", None)
        if old is not None:
            try:
                old.grid_remove()
            except Exception:
                pass
        return result

    def save(self, silent=False):
        ensure_schema(self.db)
        flat = flatten_ledger_profiles(self._phase49_3i35_ledger)
        if self._phase49_3i35_ledger:
            self._phase49_3i34_profiles = flat
            self._phase49_3i34_selected_key = ""
            self.db.update_product(
                int(self.product_id),
                {
                    "sales_profile_ledger_json": json.dumps(self._phase49_3i35_ledger, ensure_ascii=False),
                    "sales_profiles_json": json.dumps(flat, ensure_ascii=False),
                },
            )
        refresh_consumption(self)
        return original_save(self, silent=silent)

    def add_filament_offer_dialog(self):
        top = tk.Toplevel(self)
        top.title("تعریف متریال / برند / رنگ / موجودی")
        top.transient(self)
        top.grab_set()
        fields = [
            ("material", "متریال", "PLA"),
            ("brand", "برند", "Bambu Lab"),
            ("manufacturer", "کارخانه / سازنده", ""),
            ("color", "رنگ", "سفید مات"),
            ("hex", "HEX", ""),
            ("roll_weight", "وزن هر رول (گرم)", "1000"),
            ("stock_rolls", "موجودی (تعداد رول)", "1"),
            ("purchase", "قیمت خرید هر رول (تومان)", "0"),
            ("sale", "قیمت فروش هر رول (تومان)", "0"),
            ("usd", "قیمت دلاری هر رول", "0"),
            ("fx", "نرخ دلار ثبت‌شده (تومان)", "0"),
        ]
        vars_ = {}
        body = ttk.Frame(top, padding=12)
        body.pack(fill="both", expand=True)
        for row_index, (key, label, default) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=row_index, column=0, sticky="w", padx=4, pady=4)
            var = tk.StringVar(value=default)
            vars_[key] = var
            ttk.Entry(body, textvariable=var, width=38).grid(row=row_index, column=1, sticky="ew", padx=4, pady=4)
        body.columnconfigure(1, weight=1)
        result = {"saved": False}

        def do_save():
            try:
                created = add_available_material_color(
                    self.db,
                    vars_["material"].get(),
                    vars_["color"].get(),
                    vars_["hex"].get(),
                    brand_name=vars_["brand"].get(),
                    manufacturer_name=vars_["manufacturer"].get(),
                    roll_weight_grams=_integer(vars_["roll_weight"].get(), 1000),
                    stock_roll_count=_number(vars_["stock_rolls"].get(), 0),
                    purchase_price_per_roll=_integer(vars_["purchase"].get(), 0),
                    sale_price_per_roll=_integer(vars_["sale"].get(), 0),
                    usd_price_per_roll=_number(vars_["usd"].get(), 0),
                    usd_fx_rate_toman=_number(vars_["fx"].get(), 0),
                )
            except Exception as exc:
                messagebox.showerror("متریال", str(exc), parent=top)
                return
            result["saved"] = True
            result["id"] = int(created["id"])
            top.destroy()

        buttons = ttk.Frame(body)
        buttons.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(buttons, text="ثبت", command=do_save, style="Success.TButton").pack(side="right", padx=3)
        ttk.Button(buttons, text="انصراف", command=top.destroy).pack(side="right", padx=3)
        ttk.Label(
            body,
            text="نرخ مصرف = بزرگ‌ترِ «فروش هر رول ÷ وزن رول» و «قیمت دلاری × نرخ دلار ثبت‌شده ÷ وزن رول». نرخ دلار حدس زده نمی‌شود.",
            style="SubHeader.TLabel",
            wraplength=650,
        ).grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.wait_window(top)
        if result.get("saved"):
            self._refresh_material_inventory()
            for index, item in enumerate(getattr(self, "_material_color_rows", []) or []):
                if int(item.get("id") or 0) == int(result["id"]):
                    self.material_color_list.selection_set(index)
                    self.material_color_list.see(index)
                    break
            self.footer_status.set("متریال/برند/رنگ ثبت و انتخاب شد؛ برای نگهداری انتخاب روی محصول «ثبت انتخاب‌ها» را بزن")
        return result.get("saved", False)

    # Final composition: the old add-color button still resolves this method name.
    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._selected_material_colors = _selected_material_colors
    workspace_class._add_material_color = add_filament_offer_dialog
    workspace_class._phase49_3i35_selected_offers = selected_offers
    workspace_class._phase49_3i35_build_material_actions = build_material_actions
    workspace_class._phase49_3i35_commit_material_selection = commit_material_selection
    workspace_class._phase49_3i35_build_production_matrix = build_production_matrix
    workspace_class._phase49_3i35_add_production_row = add_production_row
    workspace_class._phase49_3i35_remove_production_row = remove_production_row
    workspace_class._phase49_3i35_production_values = production_values
    workspace_class._phase49_3i35_set_production_values = set_production_values
    workspace_class._phase49_3i35_refresh_consumption = refresh_consumption
    workspace_class._phase49_3i35_build_ledger_ui = build_ledger_ui
    workspace_class._phase49_3i35_current_snapshot = current_snapshot
    workspace_class._phase49_3i35_persist_ledger = persist_ledger
    workspace_class._phase49_3i35_refresh_ledger_tree = refresh_ledger_tree
    workspace_class._phase49_3i35_register_profile = register_profile
    workspace_class._phase49_3i35_new_from_last = new_from_last
    workspace_class._phase49_3i35_selected_profile = selected_profile
    workspace_class._phase49_3i35_load_selected = load_selected
    workspace_class._phase49_3i35_update_selected = update_selected
    workspace_class._phase49_3i35_delete_selected = delete_selected
    workspace_class._phase49_3i35_apply_snapshot_to_draft = apply_snapshot_to_draft
    workspace_class._phase49_3i35_operator_ledger = True
