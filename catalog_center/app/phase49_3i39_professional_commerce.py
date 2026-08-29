from __future__ import annotations

import copy
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_desktop_schema import (
    add_available_material_color,
    effective_filament_offer_price_per_gram,
    list_available_material_colors,
    normalize_material_color_options,
)
from .phase49_3i35_operator_ledger import (
    flatten_ledger_profiles,
    normalize_ledger_profile,
    normalize_production_row,
)
from .phase49_3i36_stage_finalization import is_stage_locked

PHASE = "49.3I.39"

PRICING_LABELS = {
    "fixed": "قیمت قطعی برای هر Filament",
    "dynamic": "قیمت فرمولی",
    "range": "بازه قیمت (فعلاً اختیاری)",
}
PRICING_BY_LABEL = {label: code for code, label in PRICING_LABELS.items()}


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


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _row_value(row, key, default=""):
    if row is None:
        return default
    try:
        return row[key] if key in row.keys() else default
    except Exception:
        return default


def offer_key(item: dict) -> tuple[str, str, str]:
    return (
        str(item.get("brand") or item.get("brand_name") or "").strip().casefold(),
        str(item.get("material") or item.get("material_name") or "").strip().casefold(),
        str(item.get("color") or item.get("color_name") or "").strip().casefold(),
    )


def offer_company(item: dict) -> str:
    return str(
        item.get("manufacturer")
        or item.get("manufacturer_name")
        or item.get("brand")
        or item.get("brand_name")
        or ""
    ).strip()


def offer_display(item: dict) -> str:
    brand = str(item.get("brand") or item.get("brand_name") or "").strip()
    material = str(item.get("material") or item.get("material_name") or "").strip()
    color = str(item.get("color") or item.get("color_name") or "").strip()
    return "-".join(part for part in (brand, material, color) if part) or "Filament بدون نام"


def offer_stock_grams(item: dict) -> float:
    return max(0.0, float(item.get("stock_roll_count") or 0)) * max(
        1.0, float(item.get("roll_weight_grams") or 1000)
    )


def formula_price_breakdown(
    offer: dict,
    production: dict,
    *,
    support_multiplier=1,
    assembly_fee=0,
) -> dict[str, int | float]:
    part = Decimal(str(_number(production.get("weight_grams"), 0)))
    support = Decimal(str(_number(production.get("support_weight_grams"), 0)))
    multiplier = Decimal(str(max(0.0, float(support_multiplier or 0))))
    minutes = Decimal(str(max(1, _integer(production.get("print_time_minutes"), 60))))
    charged = part + support * multiplier
    material_rate = Decimal(str(max(0.0, effective_filament_offer_price_per_gram(offer))))
    print_hourly = Decimal(str(_integer(offer.get("print_hourly_rate"), 0)))
    supervision_hourly = Decimal(str(_integer(offer.get("supervision_hourly_rate"), 0)))
    preheat_hours = Decimal(str(max(0.0, float(offer.get("preheat_hours") or 0))))
    preheat_hourly = Decimal(str(_integer(offer.get("preheat_hourly_rate"), 0)))

    material_cost = material_rate * charged
    print_cost = print_hourly * minutes / Decimal("60")
    supervision_cost = supervision_hourly * minutes / Decimal("60")
    preheat_cost = preheat_hours * preheat_hourly
    total = material_cost + print_cost + supervision_cost + preheat_cost + Decimal(str(_integer(assembly_fee, 0)))

    def money(value: Decimal) -> int:
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    return {
        "chargeable_grams": float(charged),
        "material_rate_per_gram": float(material_rate),
        "material_cost": money(material_cost),
        "print_cost": money(print_cost),
        "supervision_cost": money(supervision_cost),
        "preheat_cost": money(preheat_cost),
        "assembly_fee": _integer(assembly_fee, 0),
        "total": money(total),
    }


def pricing_summary_range(
    offers: list[dict],
    production_rows: list[dict],
    mode: str,
    *,
    support_multiplier=1,
    assembly_fee=0,
    price_min=0,
    price_max=0,
) -> dict[str, int]:
    """Return the exact visible final-price range without mutating Product data."""
    normalized_offers = normalize_material_color_options(offers or [])
    rows = [
        normalize_production_row(item)
        for item in (production_rows or [])
        if isinstance(item, dict) and _number(item.get("weight_grams"), 0) > 0
    ]
    mode = str(mode or "dynamic")
    totals: list[int] = []
    incomplete = 0

    if mode == "fixed":
        for item in normalized_offers:
            value = _integer(item.get("fixed_product_price"), 0)
            if value > 0:
                totals.append(value)
            else:
                incomplete += 1
    elif mode == "range":
        low = _integer(price_min, 0)
        high = _integer(price_max, low)
        if low > 0:
            totals.append(low)
        if high > 0 and high != low:
            totals.append(high)
    else:
        for item in normalized_offers:
            for production in rows:
                total = _integer(
                    formula_price_breakdown(
                        item,
                        production,
                        support_multiplier=support_multiplier,
                        assembly_fee=assembly_fee,
                    ).get("total"),
                    0,
                )
                if total > 0:
                    totals.append(total)

    return {
        "min": min(totals) if totals else 0,
        "max": max(totals) if totals else 0,
        "count": len(totals),
        "incomplete": incomplete,
    }


def validate_profile_identity(
    ledger: list[dict],
    *,
    name: str,
    size_label: str,
    length_cm,
    width_cm,
    height_cm,
    ignore_key: str = "",
) -> None:
    clean_name = str(name or "").strip()
    clean_size = str(size_label or "").strip()
    dims = tuple(round(float(_number(value, 0)), 3) for value in (length_cm, width_cm, height_cm))
    if not clean_name:
        raise ValueError("نام پروفایل لازم است.")
    if not clean_size:
        raise ValueError("سایز/عنوان پروفایل لازم است.")
    if not all(value > 0 for value in dims):
        raise ValueError("طول، عرض و ارتفاع واقعی قطعه باید بیشتر از صفر باشند.")

    for raw in ledger:
        item = normalize_ledger_profile(raw, 1)
        if str(item.get("key") or "") == str(ignore_key or ""):
            continue
        if str(item.get("name") or "").strip().casefold() == clean_name.casefold():
            raise ValueError(f"پروفایل با نام «{clean_name}» قبلاً ثبت شده است.")
        if str(item.get("size_label") or "").strip().casefold() == clean_size.casefold():
            raise ValueError(f"سایز «{clean_size}» قبلاً پروفایل دارد؛ سایز جدید باید متفاوت باشد.")
        item_dims = tuple(
            round(float(_number(item.get(key), 0)), 3)
            for key in ("part_length_cm", "part_width_cm", "part_height_cm")
        )
        if all(value > 0 for value in item_dims) and item_dims == dims:
            raise ValueError("پروفایلی با همین ابعاد قطعه قبلاً ثبت شده است.")


def merge_global_offer(product_offer: dict, global_offer: dict) -> dict:
    """Refresh operational rates without losing Product-specific fixed price."""
    merged = dict(product_offer or {})
    source = dict(global_offer or {})
    for key in (
        "material_name", "brand_name", "manufacturer_name", "color_name",
        "hex_code", "color_type", "secondary_hex", "tertiary_hex",
        "roll_weight_grams", "stock_roll_count", "purchase_price_per_roll",
        "sale_price_per_roll", "usd_price_per_roll", "usd_fx_rate_toman",
        "print_hourly_rate", "supervision_hourly_rate", "preheat_hours",
        "preheat_temperature_c", "preheat_hourly_rate", "filament_image_url",
    ):
        if key in source:
            merged[key] = source[key]
    normalized = normalize_material_color_options([{
        "material": merged.get("material") or merged.get("material_name"),
        "brand": merged.get("brand") or merged.get("brand_name"),
        "manufacturer": merged.get("manufacturer") or merged.get("manufacturer_name"),
        "color": merged.get("color") or merged.get("color_name"),
        "hex": merged.get("hex") or merged.get("hex_code"),
        "color_type": merged.get("color_type"),
        "secondary_hex": merged.get("secondary_hex"),
        "tertiary_hex": merged.get("tertiary_hex"),
        "roll_weight_grams": merged.get("roll_weight_grams"),
        "stock_roll_count": merged.get("stock_roll_count"),
        "purchase_price_per_roll": merged.get("purchase_price_per_roll"),
        "sale_price_per_roll": merged.get("sale_price_per_roll"),
        "usd_price_per_roll": merged.get("usd_price_per_roll"),
        "usd_fx_rate_toman": merged.get("usd_fx_rate_toman"),
        "print_hourly_rate": merged.get("print_hourly_rate"),
        "supervision_hourly_rate": merged.get("supervision_hourly_rate"),
        "preheat_hours": merged.get("preheat_hours"),
        "preheat_temperature_c": merged.get("preheat_temperature_c"),
        "preheat_hourly_rate": merged.get("preheat_hourly_rate"),
        "filament_image_url": merged.get("filament_image_url"),
        "fixed_product_price": product_offer.get("fixed_product_price", 0),
    }])
    return normalized[0] if normalized else {}


def resolve_pricing_offer_context(
    registered_offers: list[dict],
    global_inventory: list[dict],
    visible_selection: list[dict],
) -> tuple[list[dict], bool]:
    """Resolve fresh pricing facts and allow an unregistered visible selection as a draft preview."""
    registered = normalize_material_color_options(registered_offers or [])
    global_map = {
        offer_key(item): item
        for item in normalize_material_color_options(global_inventory or [])
    }
    refreshed = [
        merge_global_offer(item, global_map.get(offer_key(item), {}))
        if global_map.get(offer_key(item))
        else item
        for item in registered
    ]
    refreshed = normalize_material_color_options(refreshed)

    visible = normalize_material_color_options(visible_selection or [])
    if visible:
        registered_keys = {offer_key(item) for item in refreshed}
        if not refreshed or any(offer_key(item) not in registered_keys for item in visible):
            return visible, True
    return refreshed, False


def _hide(widget):
    if widget is None:
        return
    try:
        manager = widget.winfo_manager()
        if manager == "grid":
            widget.grid_remove()
        elif manager == "pack":
            widget.pack_forget()
        elif manager == "place":
            widget.place_forget()
    except Exception:
        pass


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i39_professional_commerce", False):
        return

    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_save = workspace_class.save

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        self._phase49_3i39_selected_product_offers = []
        self._phase49_3i39_offer_vars = {}
        self._phase49_3i39_working_offer_rows = []
        self._phase49_3i39_profile_edit_key = ""
        self._phase49_3i39_build_ui()
        self._phase49_3i39_reload()

    def build_ui(self):
        # Hide only obsolete UI compositions. Data and methods remain available
        # for compatibility/migrations; the new card is the final visible Stage-2.
        picker_box = getattr(self, "_epic49_materials_box", None)
        if picker_box is not None:
            try:
                _hide(picker_box.master.master)
            except Exception:
                pass
        _hide(getattr(self, "_phase49_3f_pricing_panel", None))
        _hide(getattr(self, "_phase49_3i35_panel", None))
        _hide(getattr(self, "_phase49_3i34_panel", None))

        panel = ttk.LabelFrame(
            self.commerce_tab,
            text="مرحله ۲ حرفه‌ای — فیلامنت → قیمت‌گذاری → وزن/زمان → پروفایل",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.grid(row=70, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        panel.columnconfigure(0, weight=1)

        # 1) Offer hierarchy
        offers = ttk.LabelFrame(
            panel,
            text="۱) شرکت سازنده → نوع فیلامنت → رنگ / موجودی / نرخ",
            padding=8,
        )
        offers.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        offers.columnconfigure(0, weight=1)
        toolbar = ttk.Frame(offers)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self._phase49_3i39_company_var = tk.StringVar()
        self._phase49_3i39_material_var = tk.StringVar()
        ttk.Label(toolbar, text="شرکت/سازنده").pack(side="right", padx=3)
        company = ttk.Combobox(toolbar, textvariable=self._phase49_3i39_company_var, state="readonly", width=25)
        company.pack(side="right", padx=3)
        ttk.Label(toolbar, text="فیلامنت").pack(side="right", padx=(12, 3))
        material = ttk.Combobox(toolbar, textvariable=self._phase49_3i39_material_var, state="readonly", width=28)
        material.pack(side="right", padx=3)
        company.bind("<<ComboboxSelected>>", lambda _e: self._phase49_3i39_refresh_offer_filter())
        material.bind("<<ComboboxSelected>>", lambda _e: self._phase49_3i39_refresh_offer_filter())
        self._phase49_3i39_company_box = company
        self._phase49_3i39_material_box = material

        self._phase49_3i39_offer_tree = ttk.Treeview(
            offers,
            columns=("selected", "offer", "color", "stock", "rate", "preheat", "fixed"),
            show="headings",
            height=7,
            selectmode="extended",
        )
        for key, label, width in (
            ("selected", "روی محصول", 80),
            ("offer", "برند / فیلامنت", 220),
            ("color", "رنگ", 190),
            ("stock", "موجودی", 100),
            ("rate", "نرخ فروش/g", 110),
            ("preheat", "پیش‌گرم", 130),
            ("fixed", "قیمت قطعی محصول", 150),
        ):
            self._phase49_3i39_offer_tree.heading(key, text=label)
            self._phase49_3i39_offer_tree.column(key, width=width, anchor="center")
        self._phase49_3i39_offer_tree.grid(row=1, column=0, sticky="nsew")
        offers.rowconfigure(1, weight=1)

        offer_actions = ttk.Frame(offers)
        offer_actions.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(
            offer_actions,
            text="＋ تعریف Filament جدید",
            command=lambda: self._phase49_3i39_open_offer_editor(None),
            style="Primary.TButton",
        ).pack(side="right", padx=3)
        ttk.Button(
            offer_actions,
            text="✏ ویرایش Filament انتخابی",
            command=self._phase49_3i39_edit_selected_offer,
        ).pack(side="right", padx=3)
        ttk.Button(
            offer_actions,
            text="✓ ثبت Filamentهای انتخابی روی محصول",
            command=self._phase49_3i39_commit_selected_offers,
            style="Success.TButton",
        ).pack(side="right", padx=3)
        ttk.Label(
            offer_actions,
            text="Ctrl/Shift برای انتخاب چند رنگ. نرخ و موجودی متعلق به همان برند+فیلامنت+رنگ است.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

        # 2) Pricing mode
        pricing = ttk.LabelFrame(panel, text="۲) قیمت‌گذاری", padding=8)
        pricing.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self._phase49_3i39_pricing_label_var = tk.StringVar(
            value=PRICING_LABELS.get(
                str(getattr(getattr(self, "pricing_strategy_var", None), "get", lambda: "dynamic")()),
                PRICING_LABELS["dynamic"],
            )
        )
        ttk.Label(pricing, text="روش قیمت").pack(side="right", padx=3)
        pricing_box = ttk.Combobox(
            pricing,
            textvariable=self._phase49_3i39_pricing_label_var,
            values=list(PRICING_LABELS.values()),
            state="readonly",
            width=32,
        )
        pricing_box.pack(side="right", padx=3)
        pricing_box.bind("<<ComboboxSelected>>", lambda _e: self._phase49_3i39_pricing_changed())
        ttk.Button(
            pricing,
            text="🧮 پیش‌نمایش قیمت Filamentها",
            command=self._phase49_3i39_preview_prices,
            style="Success.TButton",
        ).pack(side="right", padx=8)
        self._phase49_3i39_pricing_hint = tk.StringVar()
        ttk.Label(pricing, textvariable=self._phase49_3i39_pricing_hint, style="SubHeader.TLabel").pack(side="left", padx=5)

        summary = ttk.Frame(pricing)
        summary.pack(side="bottom", fill="x", pady=(7, 0))
        ttk.Separator(summary, orient="horizontal").pack(fill="x", pady=(0, 5))
        self._phase49_3i39_price_summary_var = tk.StringVar(
            value="مبلغ نهایی: برای محاسبه، Filament و وزن/زمان چاپ را ثبت کن."
        )
        ttk.Label(
            summary,
            textvariable=self._phase49_3i39_price_summary_var,
            style="SubHeader.TLabel",
        ).pack(anchor="e")

        # 3) Common production rows
        production = ttk.LabelFrame(
            panel,
            text="۳) وزن / زمان چاپ / ساپورت — برای هر سایز پروفایل، مستقل از برند و رنگ",
            padding=8,
        )
        production.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        production.columnconfigure(0, weight=1)
        self._phase49_3i39_production_host = ttk.Frame(production)
        self._phase49_3i39_production_host.grid(row=0, column=0, sticky="ew")
        for col in (1, 3, 5):
            self._phase49_3i39_production_host.columnconfigure(col, weight=1)
        headers = ("ردیف", "وزن قطعه (گرم)", "زمان چاپ (دقیقه)", "وزن ساپورت (گرم)")
        for col, label in enumerate(headers):
            ttk.Label(
                self._phase49_3i39_production_host,
                text=label,
                font=("Tahoma", 9, "bold"),
            ).grid(row=0, column=col, sticky="w", padx=4, pady=2)
        prod_actions = ttk.Frame(production)
        prod_actions.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        ttk.Button(prod_actions, text="+ ردیف", command=self._phase49_3i39_add_production_row).pack(side="right", padx=3)
        ttk.Button(prod_actions, text="− حذف آخرین", command=self._phase49_3i39_remove_production_row).pack(side="right", padx=3)
        self._phase49_3i39_consumption_var = tk.StringVar()
        ttk.Label(prod_actions, textvariable=self._phase49_3i39_consumption_var, style="SubHeader.TLabel").pack(side="left", padx=5)
        self._phase49_3i39_production_rows = []

        # 4) Profile identity only
        profiles = ttk.LabelFrame(
            panel,
            text="۴) پروفایل فروش — فقط نام، سایز و ابعاد قطعه",
            padding=8,
        )
        profiles.grid(row=3, column=0, sticky="nsew")
        profiles.columnconfigure(0, weight=1)
        form = ttk.Frame(profiles)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        vars_and_labels = (
            (self._phase49_3i35_profile_name_var, "نام پروفایل", 22),
            (self._phase49_3i35_profile_size_var, "سایز", 14),
            (self._phase49_3i35_profile_length_var, "طول cm", 10),
            (self._phase49_3i35_profile_width_var, "عرض cm", 10),
            (self._phase49_3i35_profile_height_var, "ارتفاع cm", 10),
        )
        for var, label, width in vars_and_labels:
            ttk.Label(form, text=label).pack(side="right", padx=(8, 2))
            ttk.Entry(form, textvariable=var, width=width).pack(side="right", padx=2)
        ttk.Button(
            form,
            text="✓ ذخیره پروفایل جدید",
            command=self._phase49_3i39_register_profile,
            style="Success.TButton",
        ).pack(side="right", padx=(12, 3))

        self._phase49_3i39_profile_tree = ttk.Treeview(
            profiles,
            columns=("name", "size", "dims", "variants"),
            show="headings",
            height=6,
            selectmode="browse",
        )
        for key, label, width in (
            ("name", "پروفایل", 220),
            ("size", "سایز", 120),
            ("dims", "ابعاد قطعه", 240),
            ("variants", "ترکیب‌های سفارش", 140),
        ):
            self._phase49_3i39_profile_tree.heading(key, text=label)
            self._phase49_3i39_profile_tree.column(key, width=width, anchor="center")
        self._phase49_3i39_profile_tree.grid(row=1, column=0, sticky="nsew")
        profiles.rowconfigure(1, weight=1)
        profile_actions = ttk.Frame(profiles)
        profile_actions.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        ttk.Button(profile_actions, text="بارگذاری برای اصلاح", command=self._phase49_3i39_load_profile).pack(side="right", padx=3)
        ttk.Button(profile_actions, text="اعمال اصلاح روی انتخابی", command=self._phase49_3i39_update_profile, style="Primary.TButton").pack(side="right", padx=3)
        ttk.Button(profile_actions, text="حذف انتخابی", command=self._phase49_3i39_delete_profile, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Label(
            profile_actions,
            text="ذخیره پروفایل جدید فرم بالا را پاک نمی‌کند؛ پروفایل قبلی فقط با «اعمال اصلاح» تغییر می‌کند.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)

        self._phase49_3i39_panel = panel

    def global_offers(self):
        return [dict(item) for item in list_available_material_colors(self.db)]

    def product_offers(self):
        row = self.db.product(int(self.product_id))
        return normalize_material_color_options(_row_value(row, "material_color_options_json", "[]"))

    def refresh_offer_filter(self):
        inventory = global_offers(self)
        companies = []
        for item in inventory:
            company = offer_company(item)
            if company and company not in companies:
                companies.append(company)
        companies.sort(key=str.casefold)
        self._phase49_3i39_company_box.configure(values=companies)
        company = str(self._phase49_3i39_company_var.get() or "")
        if companies and company not in companies:
            company = companies[0]
            self._phase49_3i39_company_var.set(company)

        filtered_company = [item for item in inventory if offer_company(item) == company] if company else inventory
        materials = []
        for item in filtered_company:
            value = str(item.get("material_name") or "").strip()
            if value and value not in materials:
                materials.append(value)
        materials.sort(key=str.casefold)
        self._phase49_3i39_material_box.configure(values=materials)
        material = str(self._phase49_3i39_material_var.get() or "")
        if materials and material not in materials:
            material = materials[0]
            self._phase49_3i39_material_var.set(material)

        selected_keys = {offer_key(item) for item in self._phase49_3i39_selected_product_offers}
        tree = self._phase49_3i39_offer_tree
        for iid in tree.get_children():
            tree.delete(iid)
        self._phase49_3i39_working_offer_rows = []
        for item in inventory:
            if company and offer_company(item) != company:
                continue
            if material and str(item.get("material_name") or "") != material:
                continue
            normalized = normalize_material_color_options([item])
            if not normalized:
                continue
            offer = normalized[0]
            # Preserve per-product fixed price in the display.
            existing = next((x for x in self._phase49_3i39_selected_product_offers if offer_key(x) == offer_key(offer)), None)
            if existing:
                offer["fixed_product_price"] = _integer(existing.get("fixed_product_price"), 0)
            self._phase49_3i39_working_offer_rows.append(offer)
            hex_value = str(offer.get("hex") or "").strip()
            color_label = str(offer.get("color") or "")
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_value):
                color_label = f"■ {color_label}  {hex_value}"
            stock_kg = offer_stock_grams(offer) / 1000.0
            rate = effective_filament_offer_price_per_gram(offer)
            preheat = ""
            if float(offer.get("preheat_hours") or 0) > 0:
                preheat = f"{offer.get('preheat_hours')}h / {offer.get('preheat_temperature_c') or 0}°C"
            iid = str(len(self._phase49_3i39_working_offer_rows) - 1)
            tree.insert(
                "", "end", iid=iid,
                values=(
                    "✓" if offer_key(offer) in selected_keys else "",
                    f"{offer.get('brand') or '—'} / {offer.get('material') or '—'}",
                    color_label,
                    f"{stock_kg:g} kg",
                    f"{rate:,.0f}",
                    preheat or "—",
                    f"{_integer(offer.get('fixed_product_price'), 0):,}" if _integer(offer.get("fixed_product_price"), 0) else "—",
                ),
            )
            if offer_key(offer) in selected_keys:
                tree.selection_add(iid)

    def selected_inventory_offers(self):
        output = []
        for iid in self._phase49_3i39_offer_tree.selection():
            try:
                output.append(copy.deepcopy(self._phase49_3i39_working_offer_rows[int(iid)]))
            except Exception:
                continue
        return normalize_material_color_options(output)

    def open_offer_editor(self, offer=None):
        source = dict(offer or {})
        top = tk.Toplevel(self)
        top.title("Filament — سازنده / متریال / رنگ / نرخ / موجودی / پیش‌گرم")
        top.geometry("760x720")
        top.transient(self)
        top.grab_set()
        body = ttk.Frame(top, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        defaults = {
            "manufacturer": source.get("manufacturer") or source.get("manufacturer_name") or "",
            "brand": source.get("brand") or source.get("brand_name") or "",
            "material": source.get("material") or source.get("material_name") or "PLA",
            "color": source.get("color") or source.get("color_name") or "",
            "hex": source.get("hex") or source.get("hex_code") or "",
            "image": source.get("filament_image_url") or "",
            "roll_weight": source.get("roll_weight_grams") or 1000,
            "stock_kg": offer_stock_grams(source) / 1000.0 if source else 0,
            "purchase": source.get("purchase_price_per_roll") or 0,
            "sale": source.get("sale_price_per_roll") or 0,
            "usd": source.get("usd_price_per_roll") or 0,
            "fx": source.get("usd_fx_rate_toman") or 0,
            "print_hourly": source.get("print_hourly_rate") or 0,
            "supervision": source.get("supervision_hourly_rate") or 0,
            "preheat_hours": source.get("preheat_hours") or 0,
            "preheat_temp": source.get("preheat_temperature_c") or 0,
            "preheat_hourly": source.get("preheat_hourly_rate") or 0,
            "fixed_product": source.get("fixed_product_price") or 0,
        }
        vars_ = {key: tk.StringVar(value=str(value)) for key, value in defaults.items()}
        fields = (
            ("manufacturer", "شرکت / سازنده"),
            ("brand", "برند"),
            ("material", "نوع فیلامنت / متریال"),
            ("color", "رنگ"),
            ("hex", "HEX رنگ"),
            ("image", "عکس فیلامنت (URL اختیاری)"),
            ("roll_weight", "وزن هر رول (گرم)"),
            ("stock_kg", "موجودی فعلی (کیلوگرم)"),
            ("purchase", "قیمت خرید هر رول"),
            ("sale", "قیمت فروش هر رول"),
            ("usd", "قیمت دلاری هر رول"),
            ("fx", "نرخ دلار ثبت‌شده"),
            ("print_hourly", "نرخ ساعت چاپ"),
            ("supervision", "نرخ ساعت نظارت"),
            ("preheat_hours", "ساعت پیش‌گرم"),
            ("preheat_temp", "دمای پیش‌گرم °C"),
            ("preheat_hourly", "هزینه ساعتی پیش‌گرم"),
            ("fixed_product", "قیمت قطعی همین محصول برای این Filament"),
        )
        for index, (key, label) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=index, column=0, sticky="w", padx=4, pady=4)
            ttk.Entry(body, textvariable=vars_[key]).grid(row=index, column=1, sticky="ew", padx=4, pady=4)

        def save_offer():
            material = vars_["material"].get().strip()
            color = vars_["color"].get().strip()
            brand = vars_["brand"].get().strip()
            manufacturer = vars_["manufacturer"].get().strip()
            if not brand:
                brand = manufacturer
            if not manufacturer:
                manufacturer = brand
            if not material or not color or not brand:
                messagebox.showwarning("Filament", "برند/شرکت، متریال و رنگ الزامی هستند.", parent=top)
                return
            roll_weight = max(1, _integer(vars_["roll_weight"].get(), 1000))
            stock_kg = max(0.0, float(_number(vars_["stock_kg"].get(), 0)))
            stock_rolls = stock_kg * 1000.0 / roll_weight
            try:
                saved = add_available_material_color(
                    self.db,
                    material,
                    color,
                    vars_["hex"].get().strip(),
                    brand_name=brand,
                    manufacturer_name=manufacturer,
                    roll_weight_grams=roll_weight,
                    stock_roll_count=stock_rolls,
                    purchase_price_per_roll=_integer(vars_["purchase"].get(), 0),
                    sale_price_per_roll=_integer(vars_["sale"].get(), 0),
                    usd_price_per_roll=_number(vars_["usd"].get(), 0),
                    usd_fx_rate_toman=_number(vars_["fx"].get(), 0),
                    print_hourly_rate=_integer(vars_["print_hourly"].get(), 0),
                    supervision_hourly_rate=_integer(vars_["supervision"].get(), 0),
                    preheat_hours=_number(vars_["preheat_hours"].get(), 0),
                    preheat_temperature_c=_number(vars_["preheat_temp"].get(), 0),
                    preheat_hourly_rate=_integer(vars_["preheat_hourly"].get(), 0),
                    filament_image_url=vars_["image"].get().strip(),
                )
            except Exception as exc:
                messagebox.showerror("Filament", str(exc), parent=top)
                return

            normalized = normalize_material_color_options([{
                **saved,
                "fixed_product_price": _integer(vars_["fixed_product"].get(), 0),
            }])
            if normalized:
                new_offer = normalized[0]
                was_selected = any(
                    offer_key(item) == offer_key(source)
                    for item in self._phase49_3i39_selected_product_offers
                ) if source else False
                if was_selected:
                    for idx, item in enumerate(self._phase49_3i39_selected_product_offers):
                        if offer_key(item) == offer_key(source):
                            self._phase49_3i39_selected_product_offers[idx] = new_offer
                            break
            top.destroy()
            self._phase49_3i39_refresh_offer_filter()
            self.footer_status.set(f"Filament «{offer_display(normalized[0] if normalized else saved)}» ذخیره شد.")

        actions = ttk.Frame(body)
        actions.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(actions, text="انصراف", command=top.destroy).pack(side="right", padx=3)
        ttk.Button(actions, text="ذخیره Filament", command=save_offer, style="Success.TButton").pack(side="right", padx=3)

    def edit_selected_offer(self):
        selected = self._phase49_3i39_offer_tree.selection()
        if len(selected) != 1:
            messagebox.showinfo("Filament", "برای ویرایش دقیقاً یک Filament را انتخاب کن.", parent=self)
            return
        try:
            offer = self._phase49_3i39_working_offer_rows[int(selected[0])]
        except Exception:
            return
        self._phase49_3i39_open_offer_editor(offer)

    def commit_selected_offers(self):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            self.footer_status.set("مرحله ۲ نهایی است؛ برای تغییر Filament ابتدا «اصلاح» را بزن.")
            return False
        selected = selected_inventory_offers(self)
        if not selected:
            messagebox.showwarning("Filament", "حداقل یک Filament را انتخاب کن.", parent=self)
            return False

        # Preserve any Product-specific fixed prices already stored.
        current_map = {offer_key(item): item for item in self._phase49_3i39_selected_product_offers}
        merged = []
        for item in selected:
            previous = current_map.get(offer_key(item), {})
            item["fixed_product_price"] = _integer(previous.get("fixed_product_price"), 0)
            merged.append(item)
        self._phase49_3i39_selected_product_offers = normalize_material_color_options(merged)
        return persist_selected_offers(self, propagate_profiles=True)

    def persist_selected_offers(self, propagate_profiles=True):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            self.footer_status.set("مرحله ۲ نهایی است؛ برای تغییر Filament ابتدا «اصلاح» را بزن.")
            return False
        offers = normalize_material_color_options(self._phase49_3i39_selected_product_offers)
        materials = list(dict.fromkeys(item["material"] for item in offers if item.get("material")))
        colors = list(dict.fromkeys(item["color"] for item in offers if item.get("color")))
        self.db.update_product(
            int(self.product_id),
            {
                "material_color_options_json": json.dumps(offers, ensure_ascii=False),
                "materials_json": json.dumps(materials, ensure_ascii=False),
                "colors_json": json.dumps(colors, ensure_ascii=False),
                "material_options_json": json.dumps(materials, ensure_ascii=False),
                "color_options_json": json.dumps(
                    [
                        {
                            "name": item.get("color") or "",
                            "hex": item.get("hex") or "",
                            "color_type": item.get("color_type") or "solid",
                            "secondary_hex": item.get("secondary_hex") or "",
                            "tertiary_hex": item.get("tertiary_hex") or "",
                        }
                        for item in offers
                    ],
                    ensure_ascii=False,
                ),
            },
        )
        if propagate_profiles and getattr(self, "_phase49_3i35_ledger", None):
            for profile in self._phase49_3i35_ledger:
                profile["material_options"] = copy.deepcopy(offers)
            persist_ledger(self)
        self.row = self.db.product(int(self.product_id))
        refresh_offer_filter(self)
        refresh_price_summary(self)
        self.footer_status.set(f"{len(offers)} Filament روی محصول ثبت شد • برند/رنگ/نرخ/موجودی حفظ شد")
        return True

    def pricing_changed(self):
        mode = PRICING_BY_LABEL.get(self._phase49_3i39_pricing_label_var.get(), "dynamic")
        if hasattr(self, "pricing_strategy_var"):
            self.pricing_strategy_var.set(mode)
        hint = {
            "fixed": "برای هر Filament در «ویرایش Filament» قیمت قطعی همین محصول را وارد کن.",
            "dynamic": "قیمت = متریال + ساعت چاپ + نظارت + پیش‌گرم + اسمبلی.",
            "range": "فعلاً اختیاری؛ حداقل/حداکثر قدیمی حفظ می‌شود.",
        }[mode]
        self._phase49_3i39_pricing_hint.set(hint)
        refresh_price_summary(self)

    def pricing_offer_context(self):
        draft_getter = getattr(self, "_phase49_3i41_selected_draft_offers", None)
        visible = draft_getter() if callable(draft_getter) else selected_inventory_offers(self)
        offers, draft = resolve_pricing_offer_context(
            getattr(self, "_phase49_3i39_selected_product_offers", []) or [],
            global_offers(self),
            visible,
        )
        return offers, draft

    def refresh_price_summary(self):
        label = getattr(self, "_phase49_3i39_price_summary_var", None)
        if label is None:
            return
        offers, draft = pricing_offer_context(self)
        rows = production_values(self)
        mode = PRICING_BY_LABEL.get(
            self._phase49_3i39_pricing_label_var.get(), "dynamic"
        )
        support_multiplier = getattr(
            getattr(self, "support_cost_multiplier_var", None),
            "get",
            lambda: 1,
        )()
        assembly_fee = getattr(
            getattr(self, "assembly_fee_var", None),
            "get",
            lambda: 0,
        )()
        price_min = getattr(
            getattr(self, "price_min_var", None),
            "get",
            lambda: 0,
        )()
        price_max = getattr(
            getattr(self, "price_max_var", None),
            "get",
            lambda: price_min,
        )()
        result = pricing_summary_range(
            offers,
            rows,
            mode,
            support_multiplier=support_multiplier,
            assembly_fee=assembly_fee,
            price_min=price_min,
            price_max=price_max,
        )

        if mode == "fixed":
            if not offers:
                label.set("مبلغ نهایی قطعی: ابتدا Filamentها را روی محصول ثبت کن.")
                return
            if result["count"] <= 0:
                label.set("مبلغ نهایی قطعی: برای Filamentهای انتخابی هنوز قیمت ثبت نشده.")
                return
            prefix = "مبلغ نهایی قطعی"
        elif mode == "range":
            if result["count"] <= 0:
                label.set("مبلغ نهایی بازه: حداقل/حداکثر هنوز ثبت نشده.")
                return
            prefix = "مبلغ نهایی بازه"
        else:
            if not offers:
                label.set("مبلغ نهایی محاسباتی: ابتدا Filamentها را روی محصول ثبت کن.")
                return
            if not rows:
                label.set("مبلغ نهایی محاسباتی: حداقل یک وزن/زمان چاپ وارد کن.")
                return
            if result["count"] <= 0:
                label.set("مبلغ نهایی محاسباتی: نرخ‌های Filament هنوز صفر/ناقص هستند.")
                return
            prefix = "مبلغ نهایی محاسباتی"

        low = int(result["min"])
        high = int(result["max"])
        amount = f"{low:,} تومان" if low == high else f"{low:,} تا {high:,} تومان"
        suffix = f" • {result['count']} ترکیب"
        if result["incomplete"]:
            suffix += f" • {result['incomplete']} Filament بدون قیمت قطعی"
        if draft:
            suffix += " • پیش‌نمایش انتخاب فعلی؛ برای نهایی‌شدن آن را روی محصول ثبت کن"
        label.set(f"{prefix}: {amount}{suffix} • ارسال جداگانه")

    def add_production_row(self, values=None):
        values = normalize_production_row(values or {})
        row_no = len(self._phase49_3i39_production_rows) + 1
        vars_ = {
            "weight_grams": tk.StringVar(value=str(values.get("weight_grams") or "")),
            "print_time_minutes": tk.StringVar(value=str(values.get("print_time_minutes") or "")),
            "support_weight_grams": tk.StringVar(value=str(values.get("support_weight_grams") or "")),
        }
        grid_row = row_no
        ttk.Label(self._phase49_3i39_production_host, text=str(row_no)).grid(row=grid_row, column=0, padx=4, pady=2)
        ttk.Entry(self._phase49_3i39_production_host, textvariable=vars_["weight_grams"]).grid(row=grid_row, column=1, sticky="ew", padx=4, pady=2)
        ttk.Label(self._phase49_3i39_production_host, text="گرم").grid(row=grid_row, column=2, padx=2)
        ttk.Entry(self._phase49_3i39_production_host, textvariable=vars_["print_time_minutes"]).grid(row=grid_row, column=3, sticky="ew", padx=4, pady=2)
        ttk.Label(self._phase49_3i39_production_host, text="دقیقه").grid(row=grid_row, column=4, padx=2)
        ttk.Entry(self._phase49_3i39_production_host, textvariable=vars_["support_weight_grams"]).grid(row=grid_row, column=5, sticky="ew", padx=4, pady=2)
        self._phase49_3i39_production_rows.append(vars_)
        self._phase49_3i35_production_rows = self._phase49_3i39_production_rows
        for var in vars_.values():
            var.trace_add("write", lambda *_a: self._phase49_3i39_refresh_consumption())
        refresh_consumption(self)

    def remove_production_row(self):
        if len(self._phase49_3i39_production_rows) <= 1:
            return
        index = len(self._phase49_3i39_production_rows)
        self._phase49_3i39_production_rows.pop()
        for child in self._phase49_3i39_production_host.grid_slaves(row=index):
            child.destroy()
        self._phase49_3i35_production_rows = self._phase49_3i39_production_rows
        refresh_consumption(self)

    def production_values(self):
        result = []
        for vars_ in self._phase49_3i39_production_rows:
            weight = _number(vars_["weight_grams"].get(), 0)
            if weight <= 0:
                continue
            result.append(normalize_production_row({
                "weight_grams": weight,
                "print_time_minutes": vars_["print_time_minutes"].get() or 60,
                "support_weight_grams": vars_["support_weight_grams"].get() or 0,
            }))
        return result

    def set_production_values(self, rows):
        for child in list(self._phase49_3i39_production_host.winfo_children()):
            try:
                if int(child.grid_info().get("row", 0)) > 0:
                    child.destroy()
            except Exception:
                pass
        self._phase49_3i39_production_rows = []
        for item in [x for x in (rows or []) if isinstance(x, dict)]:
            add_production_row(self, item)
        if not self._phase49_3i39_production_rows:
            add_production_row(self, {})
        self._phase49_3i35_production_rows = self._phase49_3i39_production_rows
        refresh_consumption(self)

    def refresh_consumption(self):
        rows = production_values(self)
        total = [
            _number(item.get("weight_grams"), 0) + _number(item.get("support_weight_grams"), 0)
            for item in rows
        ]
        self._phase49_3i39_consumption_var.set(
            "مصرف فیلامنت: " + " / ".join(f"{value:g}g" for value in total)
            if total else "حداقل یک وزن قطعه لازم است"
        )
        if rows:
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
        refresh_price_summary(self)

    def current_profile_snapshot(self, key="", name=None):
        rows = production_values(self)
        if not rows:
            raise ValueError("حداقل یک ردیف وزن/زمان چاپ معتبر در بخش بالا لازم است.")
        offers = normalize_material_color_options(self._phase49_3i39_selected_product_offers)
        if not offers:
            raise ValueError("ابتدا Filamentها را انتخاب و روی محصول ثبت کن.")
        strategy = PRICING_BY_LABEL.get(self._phase49_3i39_pricing_label_var.get(), "dynamic")
        if strategy == "fixed":
            missing = [offer_display(item) for item in offers if _integer(item.get("fixed_product_price"), 0) <= 0]
            if missing:
                raise ValueError("برای حالت قیمت قطعی، قیمت این Filamentها خالی است: " + "، ".join(missing[:5]))
        return normalize_ledger_profile({
            "key": key or f"ledger-{uuid4().hex[:12]}",
            "name": name if name is not None else self._phase49_3i35_profile_name_var.get(),
            "size_label": self._phase49_3i35_profile_size_var.get(),
            "part_length_cm": self._phase49_3i35_profile_length_var.get(),
            "part_width_cm": self._phase49_3i35_profile_width_var.get(),
            "part_height_cm": self._phase49_3i35_profile_height_var.get(),
            "production_rows": rows,
            "material_options": copy.deepcopy(offers),
            "pricing_strategy": strategy,
            "price_min": getattr(getattr(self, "price_min_var", None), "get", lambda: 0)(),
            "price_max": getattr(getattr(self, "price_max_var", None), "get", lambda: 0)(),
            "support_cost_multiplier": getattr(getattr(self, "support_cost_multiplier_var", None), "get", lambda: 1)(),
            "assembly_fee": getattr(getattr(self, "assembly_fee_var", None), "get", lambda: 0)(),
            "product_type": getattr(getattr(self, "product_type_var", None), "get", lambda: "ready_product")(),
            "availability_status": getattr(getattr(self, "availability_var", None), "get", lambda: "made_to_order")(),
            "stock_quantity": 0,
            "lead_time_min_days": getattr(getattr(self, "lead_min_var", None), "get", lambda: 1)(),
            "lead_time_max_days": getattr(getattr(self, "lead_max_var", None), "get", lambda: 3)(),
            "sort_order": (len(self._phase49_3i35_ledger) + 1) * 10,
        }, len(self._phase49_3i35_ledger) + 1)

    def persist_ledger(self):
        offers = normalize_material_color_options(self._phase49_3i39_selected_product_offers)
        for profile in self._phase49_3i35_ledger:
            profile["material_options"] = copy.deepcopy(offers)
        flat = flatten_ledger_profiles(self._phase49_3i35_ledger)
        prices = [_integer(item.get("fixed_price"), 0) for item in flat if _integer(item.get("fixed_price"), 0) > 0]
        values = {
            "sales_profile_ledger_json": json.dumps(self._phase49_3i35_ledger, ensure_ascii=False),
            "sales_profiles_json": json.dumps(flat, ensure_ascii=False),
            "sales_profile_selection_mode": "size_weight",
            "sales_profile_selector_label": "سایز/پروفایل را انتخاب کنید؛ سپس برند، فیلامنت و رنگ",
        }
        if prices:
            values["price_min"] = min(prices)
            values["price_max"] = max(prices)
        self.db.update_product(int(self.product_id), values)
        self.row = self.db.product(int(self.product_id))
        refresh_profile_tree(self)
        return flat

    def refresh_profile_tree(self):
        tree = self._phase49_3i39_profile_tree
        for iid in tree.get_children():
            tree.delete(iid)
        offers = max(1, len(self._phase49_3i39_selected_product_offers))
        for profile in self._phase49_3i35_ledger:
            dims = " × ".join(
                f"{_number(profile.get(key), 0):g}"
                for key in ("part_length_cm", "part_width_cm", "part_height_cm")
            )
            variants = len(profile.get("production_rows") or []) * offers
            tree.insert(
                "", "end", iid=str(profile["key"]),
                values=(
                    ("★ " if profile.get("is_default") else "") + str(profile.get("name") or ""),
                    profile.get("size_label") or "—",
                    f"{dims} cm",
                    variants,
                ),
            )

    def register_profile(self):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            self.footer_status.set("مرحله ۲ نهایی است؛ برای تغییر پروفایل ابتدا «اصلاح» را بزن.")
            return False
        try:
            validate_profile_identity(
                self._phase49_3i35_ledger,
                name=self._phase49_3i35_profile_name_var.get(),
                size_label=self._phase49_3i35_profile_size_var.get(),
                length_cm=self._phase49_3i35_profile_length_var.get(),
                width_cm=self._phase49_3i35_profile_width_var.get(),
                height_cm=self._phase49_3i35_profile_height_var.get(),
            )
            snapshot = current_profile_snapshot(self)
        except Exception as exc:
            messagebox.showwarning("پروفایل فروش", str(exc), parent=self)
            return False
        if not self._phase49_3i35_ledger:
            snapshot["is_default"] = True
        self._phase49_3i35_ledger.append(snapshot)
        persist_ledger(self)
        self._phase49_3i39_profile_edit_key = ""
        self.footer_status.set(
            f"پروفایل «{snapshot['name']}» ثبت شد؛ فرم بالا بدون تغییر باقی ماند و پروفایل قبلی دست‌نخورده است."
        )
        return True

    def selected_profile(self):
        selection = self._phase49_3i39_profile_tree.selection()
        if not selection:
            return None
        key = str(selection[0])
        return next((item for item in self._phase49_3i35_ledger if str(item.get("key")) == key), None)

    def load_profile(self):
        profile = selected_profile(self)
        if profile is None:
            messagebox.showinfo("پروفایل", "یک پروفایل را انتخاب کن.", parent=self)
            return
        profile = normalize_ledger_profile(profile, 1)
        self._phase49_3i35_profile_name_var.set(profile["name"])
        self._phase49_3i35_profile_size_var.set(profile["size_label"])
        self._phase49_3i35_profile_length_var.set(str(profile.get("part_length_cm") or ""))
        self._phase49_3i35_profile_width_var.set(str(profile.get("part_width_cm") or ""))
        self._phase49_3i35_profile_height_var.set(str(profile.get("part_height_cm") or ""))
        set_production_values(self, profile.get("production_rows") or [])
        self._phase49_3i39_profile_edit_key = profile["key"]
        self.footer_status.set("پروفایل برای اصلاح بارگذاری شد؛ اصل Snapshot تا زدن «اعمال اصلاح» تغییر نمی‌کند.")

    def update_profile(self):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            self.footer_status.set("مرحله ۲ نهایی است؛ برای تغییر پروفایل ابتدا «اصلاح» را بزن.")
            return False
        profile = selected_profile(self)
        if profile is None:
            messagebox.showinfo("پروفایل", "یک پروفایل را انتخاب کن.", parent=self)
            return False
        try:
            validate_profile_identity(
                self._phase49_3i35_ledger,
                name=self._phase49_3i35_profile_name_var.get(),
                size_label=self._phase49_3i35_profile_size_var.get(),
                length_cm=self._phase49_3i35_profile_length_var.get(),
                width_cm=self._phase49_3i35_profile_width_var.get(),
                height_cm=self._phase49_3i35_profile_height_var.get(),
                ignore_key=str(profile.get("key") or ""),
            )
            updated = current_profile_snapshot(
                self,
                str(profile["key"]),
                name=self._phase49_3i35_profile_name_var.get(),
            )
        except Exception as exc:
            messagebox.showwarning("پروفایل", str(exc), parent=self)
            return False
        updated["is_default"] = bool(profile.get("is_default"))
        updated["sort_order"] = profile.get("sort_order", 10)
        index = self._phase49_3i35_ledger.index(profile)
        self._phase49_3i35_ledger[index] = updated
        persist_ledger(self)
        self.footer_status.set(f"فقط پروفایل «{updated['name']}» اصلاح شد.")
        return True

    def delete_profile(self):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            self.footer_status.set("مرحله ۲ نهایی است؛ برای تغییر پروفایل ابتدا «اصلاح» را بزن.")
            return False
        profile = selected_profile(self)
        if profile is None:
            return
        if not messagebox.askyesno("حذف پروفایل", f"پروفایل «{profile.get('name')}» حذف شود؟", parent=self):
            return
        self._phase49_3i35_ledger = [x for x in self._phase49_3i35_ledger if x["key"] != profile["key"]]
        if self._phase49_3i35_ledger and not any(x.get("is_default") for x in self._phase49_3i35_ledger):
            self._phase49_3i35_ledger[0]["is_default"] = True
        persist_ledger(self)

    def preview_prices(self):
        offers, draft = pricing_offer_context(self)
        rows = production_values(self)
        mode = PRICING_BY_LABEL.get(self._phase49_3i39_pricing_label_var.get(), "dynamic")

        if mode == "range":
            result = pricing_summary_range(
                offers,
                rows,
                "range",
                price_min=getattr(getattr(self, "price_min_var", None), "get", lambda: 0)(),
                price_max=getattr(getattr(self, "price_max_var", None), "get", lambda: 0)(),
            )
            if result["count"] <= 0:
                messagebox.showinfo(
                    "پیش‌نمایش بازه قیمت",
                    "برای حالت «بازه قیمت» هنوز حداقل/حداکثر معتبر ثبت نشده است. "
                    "اگر محاسبه بر اساس نرخ Filament می‌خواهی، روش قیمت را روی «قیمت فرمولی» بگذار.",
                    parent=self,
                )
                return
            low = int(result["min"])
            high = int(result["max"])
            amount = f"{low:,} تومان" if low == high else f"{low:,} تا {high:,} تومان"
            messagebox.showinfo(
                "پیش‌نمایش بازه قیمت",
                f"مبلغ نهایی بازه: {amount}\n\n"
                "در حالت بازه، اجزای متریال/چاپ/نظارت محاسبه نمی‌شوند. "
                "برای محاسبه واقعی بر اساس نرخ Filament، «قیمت فرمولی» را انتخاب کن.",
                parent=self,
            )
            return

        if not offers or not rows:
            messagebox.showinfo(
                "قیمت",
                "ابتدا یک Filament را انتخاب/ثبت کن و حداقل یک وزن/زمان چاپ معتبر وارد کن.",
                parent=self,
            )
            return

        win = tk.Toplevel(self)
        title_mode = "قطعی" if mode == "fixed" else "فرمولی"
        win.title(f"پیش‌نمایش قیمت {title_mode} بر اساس Filament واقعی")
        win.geometry("1180x560")
        win.transient(self)
        tree = ttk.Treeview(
            win,
            columns=("offer", "row", "material", "print", "supervision", "preheat", "total", "stock"),
            show="headings",
        )
        for key, label_text, width in (
            ("offer", "Filament", 240), ("row", "وزن/زمان", 130),
            ("material", "متریال", 110), ("print", "چاپ", 100),
            ("supervision", "نظارت", 100), ("preheat", "پیش‌گرم", 100),
            ("total", "قیمت", 120), ("stock", "موجودی", 100),
        ):
            tree.heading(key, text=label_text)
            tree.column(key, width=width, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        support_multiplier = getattr(getattr(self, "support_cost_multiplier_var", None), "get", lambda: 1)()
        assembly_fee = getattr(getattr(self, "assembly_fee_var", None), "get", lambda: 0)()
        for offer in offers:
            for index, row in enumerate(rows, 1):
                if mode == "fixed":
                    breakdown = {
                        "material_cost": 0, "print_cost": 0, "supervision_cost": 0,
                        "preheat_cost": 0, "total": _integer(offer.get("fixed_product_price"), 0),
                    }
                else:
                    breakdown = formula_price_breakdown(
                        offer, row,
                        support_multiplier=support_multiplier,
                        assembly_fee=assembly_fee,
                    )
                tree.insert("", "end", values=(
                    offer_display(offer),
                    f"{row['weight_grams']}g / {row['print_time_minutes']}min",
                    f"{breakdown['material_cost']:,}",
                    f"{breakdown['print_cost']:,}",
                    f"{breakdown['supervision_cost']:,}",
                    f"{breakdown['preheat_cost']:,}",
                    f"{breakdown['total']:,}",
                    f"{offer_stock_grams(offer)/1000:g}kg",
                ))
        if draft:
            ttk.Label(
                win,
                text="این پیش‌نمایش از Filament انتخاب‌شده فعلی است؛ برای نهایی‌شدن روی محصول «ثبت Filamentهای انتخابی» را بزن.",
                style="SubHeader.TLabel",
            ).pack(fill="x", padx=10, pady=(0, 8))


    def reload_final(self):
        row = self.db.product(int(self.product_id))
        global_map = {offer_key(item): item for item in global_offers(self)}
        persisted = normalize_material_color_options(_row_value(row, "material_color_options_json", "[]"))
        refreshed = []
        for item in persisted:
            global_item = global_map.get(offer_key(item))
            refreshed.append(merge_global_offer(item, global_item) if global_item else item)
        self._phase49_3i39_selected_product_offers = normalize_material_color_options(refreshed)

        strategy = str(_row_value(row, "pricing_strategy", "dynamic") or "dynamic")
        if strategy not in PRICING_LABELS:
            strategy = "dynamic"
        self._phase49_3i39_pricing_label_var.set(PRICING_LABELS[strategy])
        pricing_changed(self)

        ledger = [
            normalize_ledger_profile(item, index + 1)
            for index, item in enumerate(_json_list(_row_value(row, "sales_profile_ledger_json", "[]")))
            if isinstance(item, dict)
        ]
        self._phase49_3i35_ledger = ledger
        if ledger:
            last = ledger[-1]
            set_production_values(self, last.get("production_rows") or [])
        else:
            # Seed from current working pricing fields without creating a profile.
            seed = {
                "weight_grams": getattr(getattr(self, "part_weight_grams_var", None), "get", lambda: "")(),
                "print_time_minutes": getattr(getattr(self, "standard_print_minutes_var", None), "get", lambda: "60")(),
                "support_weight_grams": getattr(getattr(self, "support_weight_grams_var", None), "get", lambda: "0")(),
            }
            set_production_values(self, [seed])
        refresh_offer_filter(self)
        refresh_profile_tree(self)
        refresh_price_summary(self)

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "_phase49_3i39_panel"):
            reload_final(self)
        return result

    def save(self, silent=False):
        # Synchronize the new working state into mature hidden variables before
        # the old save chain runs, then re-assert the final authoritative values.
        pricing_changed(self)
        self._phase49_3i35_production_rows = self._phase49_3i39_production_rows
        result = original_save(self, silent=True)
        if not result:
            return False
        persist_selected_offers(self, propagate_profiles=True)
        self.db.update_product(
            int(self.product_id),
            {"pricing_strategy": PRICING_BY_LABEL.get(self._phase49_3i39_pricing_label_var.get(), "dynamic")},
        )
        self.row = self.db.product(int(self.product_id))
        if not silent:
            self.footer_status.set("مرحله ۲ حرفه‌ای ذخیره شد؛ Filament/قیمت/Profile روی مسیر واحد هستند.")
        return True

    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_3i39_build_ui = build_ui
    workspace_class._phase49_3i39_global_offers = global_offers
    workspace_class._phase49_3i39_product_offers = product_offers
    workspace_class._phase49_3i39_refresh_offer_filter = refresh_offer_filter
    workspace_class._phase49_3i39_selected_inventory_offers = selected_inventory_offers
    workspace_class._phase49_3i39_open_offer_editor = open_offer_editor
    workspace_class._phase49_3i39_edit_selected_offer = edit_selected_offer
    workspace_class._phase49_3i39_commit_selected_offers = commit_selected_offers
    workspace_class._phase49_3i39_persist_selected_offers = persist_selected_offers
    workspace_class._phase49_3i39_pricing_changed = pricing_changed
    workspace_class._phase49_3i39_pricing_offer_context = pricing_offer_context
    workspace_class._phase49_3i39_refresh_price_summary = refresh_price_summary
    workspace_class._phase49_3i39_add_production_row = add_production_row
    workspace_class._phase49_3i39_remove_production_row = remove_production_row
    workspace_class._phase49_3i39_production_values = production_values
    workspace_class._phase49_3i39_set_production_values = set_production_values
    workspace_class._phase49_3i39_refresh_consumption = refresh_consumption
    workspace_class._phase49_3i39_current_profile_snapshot = current_profile_snapshot
    workspace_class._phase49_3i39_persist_ledger = persist_ledger
    workspace_class._phase49_3i39_refresh_profile_tree = refresh_profile_tree
    workspace_class._phase49_3i39_register_profile = register_profile
    workspace_class._phase49_3i39_selected_profile = selected_profile
    workspace_class._phase49_3i39_load_profile = load_profile
    workspace_class._phase49_3i39_update_profile = update_profile
    workspace_class._phase49_3i39_delete_profile = delete_profile
    workspace_class._phase49_3i39_preview_prices = preview_prices
    workspace_class._phase49_3i39_reload = reload_final
    workspace_class._phase49_3i39_professional_commerce = True
