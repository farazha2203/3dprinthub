from __future__ import annotations

import copy
import json
from decimal import Decimal
from uuid import uuid4

import tkinter as tk
from tkinter import messagebox, ttk

PHASE = "49.3I.34"

DESKTOP_COLUMNS = {
    "sales_profiles_json": "TEXT NOT NULL DEFAULT '[]'",
    "sales_profile_selection_mode": "TEXT NOT NULL DEFAULT 'size_weight'",
    "sales_profile_selector_label": "TEXT NOT NULL DEFAULT ''",
}

SELECTION_MODES = {
    "list": "فهرست کامل پروفایل‌ها",
    "size": "فقط سایز",
    "weight": "فقط وزن",
    "build": "فقط مدل ساخت",
    "size_build": "سایز ← مدل ساخت",
    "build_size": "مدل ساخت ← سایز",
    "size_weight": "سایز ← وزن",
    "weight_size": "وزن ← سایز",
    "size_weight_build": "سایز ← وزن ← مدل ساخت",
    "size_build_weight": "سایز ← مدل ساخت ← وزن",
}
MODE_BY_LABEL = {label: code for code, label in SELECTION_MODES.items()}

BUILD_PROFILES = {
    "standard": "استاندارد",
    "hollow": "توخالی / سبک",
    "reinforced": "تقویت‌شده",
    "solid": "توپر / سنگین",
    "custom": "سفارشی",
}
BUILD_BY_LABEL = {label: code for code, label in BUILD_PROFILES.items()}

STOCK_STATUSES = {
    "made_to_order": "تولید پس از سفارش",
    "in_stock": "آماده ارسال",
    "preorder": "پیش‌سفارش",
    "out_of_stock": "ناموجود",
}
STOCK_BY_LABEL = {label: code for code, label in STOCK_STATUSES.items()}


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    changed = False
    for name, ddl in DESKTOP_COLUMNS.items():
        if name not in columns:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
            changed = True
    if changed:
        db.conn.commit()


def _num(value, default=0):
    try:
        number = Decimal(str(value or default).replace(",", "").strip())
    except Exception:
        number = Decimal(str(default))
    return float(number) if number % 1 else int(number)


def _int(value, default=0):
    try:
        return max(0, int(float(str(value or default).replace(",", "").strip())))
    except Exception:
        return max(0, int(default))


def normalize_profile(item: dict, index: int = 1) -> dict:
    source = dict(item or {})
    key = str(source.get("key") or source.get("profile_key") or f"profile-{uuid4().hex[:10]}")[:80]
    build = str(source.get("build_profile") or "standard")
    if build not in BUILD_PROFILES:
        build = "standard"
    stock = str(source.get("stock_status") or "made_to_order")
    if stock not in STOCK_STATUSES:
        stock = "made_to_order"
    return {
        "key": key,
        "name": str(source.get("name") or f"پروفایل {index}")[:120],
        "description": str(source.get("description") or "")[:300],
        "size_label": str(source.get("size_label") or "")[:80],
        "weight_grams": _num(source.get("weight_grams") or source.get("final_weight_grams"), 0),
        "material_weight_grams": _num(source.get("material_weight_grams") or source.get("weight_grams"), 0),
        "print_time_minutes": max(1, _int(source.get("print_time_minutes"), 60)),
        "fixed_price": _int(source.get("fixed_price"), 0),
        "part_length_cm": _num(source.get("part_length_cm"), 0),
        "part_width_cm": _num(source.get("part_width_cm"), 0),
        "part_height_cm": _num(source.get("part_height_cm"), 0),
        "build_profile": build,
        "material": str(source.get("material") or "")[:120],
        "color": str(source.get("color") or "")[:120],
        "quality": str(source.get("quality") or "")[:120],
        "packaging_weight_grams": _num(source.get("packaging_weight_grams"), 0),
        "shipping_weight_grams": _num(source.get("shipping_weight_grams"), 0),
        "package_length_cm": _num(source.get("package_length_cm"), 0),
        "package_width_cm": _num(source.get("package_width_cm"), 0),
        "package_height_cm": _num(source.get("package_height_cm"), 0),
        "stock_status": stock,
        "stock_quantity": _int(source.get("stock_quantity"), 0),
        "track_inventory": bool(source.get("track_inventory", False)),
        "is_default": bool(source.get("is_default", index == 1)),
        "is_active": bool(source.get("is_active", True)),
        "sort_order": _int(source.get("sort_order"), index * 10),
    }


def duplicate_profile(item: dict, index: int) -> dict:
    clone = normalize_profile(copy.deepcopy(item), index)
    clone["key"] = f"profile-{uuid4().hex[:12]}"
    clone["name"] = (str(clone.get("name") or f"پروفایل {index}") + " - کپی")[:120]
    clone["is_default"] = False
    clone["sort_order"] = max(index * 10, _int(clone.get("sort_order"), 0) + 10)
    return clone


def profile_price_range(profiles: list[dict]) -> tuple[int, int]:
    prices = sorted(_int(item.get("fixed_price"), 0) for item in profiles if _int(item.get("fixed_price"), 0) > 0)
    return (prices[0], prices[-1]) if prices else (0, 0)


def seed_profile_from_row(row) -> dict:
    price = _int(row["final_price"] if "final_price" in row.keys() else 0, 0)
    if not price and "price_min" in row.keys():
        price = _int(row["price_min"], 0)
    weight = row["estimated_weight_grams"] if "estimated_weight_grams" in row.keys() else 0
    minutes = row["estimated_print_minutes"] if "estimated_print_minutes" in row.keys() else 60
    return normalize_profile(
        {
            "key": f"profile-{uuid4().hex[:12]}",
            "name": "پروفایل ۱",
            "weight_grams": weight,
            "material_weight_grams": weight,
            "print_time_minutes": minutes or 60,
            "fixed_price": price,
            "is_default": True,
            "sort_order": 10,
        },
        1,
    )


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i34_profile_matrix", False):
        return

    original_init = workspace_class.__init__
    original_save = workspace_class.save
    original_reload = workspace_class.reload

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        self._phase49_3i34_profiles = []
        self._phase49_3i34_selected_key = ""
        self._phase49_3i34_vars = {}
        self._phase49_3i34_quick_price_widgets = [
            widget
            for widget in self.quick_tab.winfo_children()
            if widget.winfo_manager() == "grid" and int(widget.grid_info().get("row", -1)) == 3
        ]
        self._phase49_3i34_build_ui()
        self.reload()

    def _build_ui(self):
        frame = self.commerce_tab
        panel = ttk.LabelFrame(
            frame,
            text="پروفایل‌های قابل سفارش — سایز / وزن / قیمت / مشخصات مستقل",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.grid(row=60, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        panel.columnconfigure(0, weight=1)
        panel.columnconfigure(1, weight=2)

        top = ttk.Frame(panel)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self._phase49_3i34_mode_var = tk.StringVar(value=SELECTION_MODES["size_weight"])
        self._phase49_3i34_selector_label_var = tk.StringVar(value="")
        ttk.Label(top, text="روش انتخاب مشتری").pack(side="right", padx=4)
        ttk.Combobox(
            top,
            textvariable=self._phase49_3i34_mode_var,
            values=list(SELECTION_MODES.values()),
            state="readonly",
            width=28,
        ).pack(side="right", padx=4)
        ttk.Label(top, text="عنوان روی سایت").pack(side="right", padx=(16, 4))
        ttk.Entry(top, textvariable=self._phase49_3i34_selector_label_var, width=34).pack(side="right", padx=4)
        ttk.Label(
            top,
            text="مثال: ابتدا سایز ۳۰ سانتی را انتخاب کن؛ سپس فقط وزن‌های همان سایز نمایش داده می‌شوند.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=4)

        left = ttk.Frame(panel)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        right = ttk.Frame(panel)
        right.grid(row=1, column=1, sticky="nsew")
        panel.rowconfigure(1, weight=1)

        self._phase49_3i34_tree = ttk.Treeview(
            left,
            columns=("name", "size", "weight", "price", "time"),
            show="headings",
            height=12,
            selectmode="browse",
        )
        for key, title, width in (
            ("name", "پروفایل", 150),
            ("size", "سایز", 90),
            ("weight", "وزن", 80),
            ("price", "قیمت", 105),
            ("time", "زمان چاپ", 80),
        ):
            self._phase49_3i34_tree.heading(key, text=title)
            self._phase49_3i34_tree.column(key, width=width, anchor="center")
        self._phase49_3i34_tree.pack(fill="both", expand=True)
        self._phase49_3i34_tree.bind("<<TreeviewSelect>>", lambda _e: self._phase49_3i34_load_selected())

        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(6, 0))
        ttk.Button(actions, text="+ پروفایل جدید", command=self._phase49_3i34_add_profile, style="Primary.TButton").pack(side="right", padx=2)
        ttk.Button(actions, text="کپی پروفایل انتخابی", command=self._phase49_3i34_clone_profile).pack(side="right", padx=2)
        ttk.Button(actions, text="حذف پروفایل", command=self._phase49_3i34_delete_profile, style="Danger.TButton").pack(side="right", padx=2)

        fields = [
            ("name", "نام پروفایل", "entry"),
            ("size_label", "سایز / عنوان ابعاد", "entry"),
            ("weight_grams", "وزن نهایی (گرم)", "entry"),
            ("material_weight_grams", "وزن متریال مصرفی (گرم)", "entry"),
            ("print_time_minutes", "زمان چاپ (دقیقه)", "entry"),
            ("fixed_price", "قیمت قطعی (تومان)", "entry"),
            ("part_length_cm", "طول قطعه (cm)", "entry"),
            ("part_width_cm", "عرض قطعه (cm)", "entry"),
            ("part_height_cm", "ارتفاع قطعه (cm)", "entry"),
            ("build_profile", "مدل ساخت", "build"),
            ("material", "متریال", "entry"),
            ("color", "رنگ", "entry"),
            ("quality", "کیفیت چاپ", "entry"),
            ("packaging_weight_grams", "وزن بسته‌بندی (گرم)", "entry"),
            ("shipping_weight_grams", "وزن ارسال Override (گرم)", "entry"),
            ("package_length_cm", "طول بسته (cm)", "entry"),
            ("package_width_cm", "عرض بسته (cm)", "entry"),
            ("package_height_cm", "ارتفاع بسته (cm)", "entry"),
            ("stock_status", "وضعیت موجودی", "stock"),
            ("stock_quantity", "موجودی عددی", "entry"),
            ("sort_order", "ترتیب نمایش", "entry"),
            ("description", "توضیح کوتاه پروفایل", "entry"),
        ]
        for idx, (key, label, kind) in enumerate(fields):
            row = idx // 2
            col = (idx % 2) * 2
            ttk.Label(right, text=label).grid(row=row, column=col, sticky="w", padx=4, pady=3)
            var = tk.StringVar()
            self._phase49_3i34_vars[key] = var
            if kind == "build":
                widget = ttk.Combobox(right, textvariable=var, values=list(BUILD_PROFILES.values()), state="readonly")
            elif kind == "stock":
                widget = ttk.Combobox(right, textvariable=var, values=list(STOCK_STATUSES.values()), state="readonly")
            else:
                widget = ttk.Entry(right, textvariable=var)
            widget.grid(row=row, column=col + 1, sticky="ew", padx=4, pady=3)
        right.columnconfigure(1, weight=1)
        right.columnconfigure(3, weight=1)

        flags_row = (len(fields) + 1) // 2
        self._phase49_3i34_default_var = tk.IntVar(value=0)
        self._phase49_3i34_active_var = tk.IntVar(value=1)
        self._phase49_3i34_track_var = tk.IntVar(value=0)
        ttk.Checkbutton(right, text="پروفایل پیش‌فرض", variable=self._phase49_3i34_default_var).grid(row=flags_row, column=0, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Checkbutton(right, text="فعال", variable=self._phase49_3i34_active_var).grid(row=flags_row, column=2, sticky="w", padx=4, pady=4)
        ttk.Checkbutton(right, text="کنترل موجودی عددی", variable=self._phase49_3i34_track_var).grid(row=flags_row, column=3, sticky="w", padx=4, pady=4)
        ttk.Button(
            right,
            text="ثبت تغییرات همین پروفایل",
            command=self._phase49_3i34_commit_editor,
            style="Success.TButton",
        ).grid(row=flags_row + 1, column=0, columnspan=4, sticky="ew", padx=4, pady=(8, 3))
        self._phase49_3i34_panel = panel

    def _profile_by_key(self, key):
        return next((item for item in self._phase49_3i34_profiles if item.get("key") == key), None)

    def _refresh_tree(self, select_key=""):
        tree = self._phase49_3i34_tree
        for iid in tree.get_children():
            tree.delete(iid)
        for index, item in enumerate(self._phase49_3i34_profiles, 1):
            key = str(item["key"])
            label = str(item.get("name") or f"پروفایل {index}")
            if item.get("is_default"):
                label = "★ " + label
            tree.insert(
                "",
                "end",
                iid=key,
                values=(
                    label,
                    item.get("size_label") or "—",
                    f"{item.get('weight_grams') or 0:g} g" if isinstance(item.get("weight_grams"), float) else f"{item.get('weight_grams') or 0} g",
                    f"{_int(item.get('fixed_price'), 0):,}",
                    f"{_int(item.get('print_time_minutes'), 0)} min",
                ),
            )
        wanted = select_key if select_key in tree.get_children() else (tree.get_children()[0] if tree.get_children() else "")
        if wanted:
            tree.selection_set(wanted)
            tree.focus(wanted)
            tree.see(wanted)
            self._phase49_3i34_selected_key = wanted
            self._phase49_3i34_load_selected()
        self._phase49_3i34_sync_quick_price_visibility()

    def _load_selected(self):
        selected = self._phase49_3i34_tree.selection()
        if not selected:
            return
        key = str(selected[0])
        item = self._profile_by_key(key)
        if item is None:
            return
        self._phase49_3i34_selected_key = key
        for field, var in self._phase49_3i34_vars.items():
            value = item.get(field, "")
            if field == "build_profile":
                value = BUILD_PROFILES.get(str(value), BUILD_PROFILES["standard"])
            elif field == "stock_status":
                value = STOCK_STATUSES.get(str(value), STOCK_STATUSES["made_to_order"])
            var.set(str(value if value is not None else ""))
        self._phase49_3i34_default_var.set(int(bool(item.get("is_default"))))
        self._phase49_3i34_active_var.set(int(bool(item.get("is_active", True))))
        self._phase49_3i34_track_var.set(int(bool(item.get("track_inventory", False))))

    def _editor_payload(self, key):
        v = self._phase49_3i34_vars
        return normalize_profile(
            {
                "key": key,
                "name": v["name"].get(),
                "description": v["description"].get(),
                "size_label": v["size_label"].get(),
                "weight_grams": v["weight_grams"].get(),
                "material_weight_grams": v["material_weight_grams"].get(),
                "print_time_minutes": v["print_time_minutes"].get(),
                "fixed_price": v["fixed_price"].get(),
                "part_length_cm": v["part_length_cm"].get(),
                "part_width_cm": v["part_width_cm"].get(),
                "part_height_cm": v["part_height_cm"].get(),
                "build_profile": BUILD_BY_LABEL.get(v["build_profile"].get(), "standard"),
                "material": v["material"].get(),
                "color": v["color"].get(),
                "quality": v["quality"].get(),
                "packaging_weight_grams": v["packaging_weight_grams"].get(),
                "shipping_weight_grams": v["shipping_weight_grams"].get(),
                "package_length_cm": v["package_length_cm"].get(),
                "package_width_cm": v["package_width_cm"].get(),
                "package_height_cm": v["package_height_cm"].get(),
                "stock_status": STOCK_BY_LABEL.get(v["stock_status"].get(), "made_to_order"),
                "stock_quantity": v["stock_quantity"].get(),
                "sort_order": v["sort_order"].get(),
                "is_default": bool(self._phase49_3i34_default_var.get()),
                "is_active": bool(self._phase49_3i34_active_var.get()),
                "track_inventory": bool(self._phase49_3i34_track_var.get()),
            },
            1,
        )

    def _commit_editor(self, quiet=False):
        key = str(self._phase49_3i34_selected_key or "")
        if not key:
            return True
        current = self._phase49_3i34_profile_by_key(key)
        if current is None:
            return True
        try:
            updated = self._phase49_3i34_editor_payload(key)
        except Exception as exc:
            if not quiet:
                messagebox.showerror("3DPrintHub", f"مقادیر پروفایل معتبر نیست:\n{exc}", parent=self)
            return False
        if updated["weight_grams"] <= 0:
            if not quiet:
                messagebox.showwarning("پروفایل محصول", "وزن نهایی پروفایل باید بیشتر از صفر باشد.", parent=self)
            return False
        if updated["is_default"]:
            for item in self._phase49_3i34_profiles:
                item["is_default"] = item["key"] == key
        index = self._phase49_3i34_profiles.index(current)
        self._phase49_3i34_profiles[index] = updated
        self._phase49_3i34_refresh_tree(key)
        return True

    def _add_profile(self):
        if self._phase49_3i34_selected_key and not self._phase49_3i34_commit_editor(quiet=True):
            return
        new = normalize_profile({"name": f"پروفایل {len(self._phase49_3i34_profiles) + 1}", "key": f"profile-{uuid4().hex[:12]}", "sort_order": (len(self._phase49_3i34_profiles)+1)*10}, len(self._phase49_3i34_profiles) + 1)
        self._phase49_3i34_profiles.append(new)
        self._phase49_3i34_refresh_tree(new["key"])

    def _clone_profile(self):
        if not self._phase49_3i34_selected_key:
            messagebox.showinfo("پروفایل محصول", "ابتدا یک پروفایل را انتخاب کنید.", parent=self)
            return
        if not self._phase49_3i34_commit_editor(quiet=True):
            return
        source = self._phase49_3i34_profile_by_key(self._phase49_3i34_selected_key)
        if source is None:
            return
        clone = duplicate_profile(source, len(self._phase49_3i34_profiles) + 1)
        self._phase49_3i34_profiles.append(clone)
        self._phase49_3i34_refresh_tree(clone["key"])

    def _delete_profile(self):
        key = str(self._phase49_3i34_selected_key or "")
        if not key:
            return
        if len(self._phase49_3i34_profiles) <= 1:
            messagebox.showwarning("پروفایل محصول", "حداقل یک پروفایل باید باقی بماند.", parent=self)
            return
        if not messagebox.askyesno("پروفایل محصول", "این پروفایل حذف شود؟", parent=self):
            return
        self._phase49_3i34_profiles = [item for item in self._phase49_3i34_profiles if item["key"] != key]
        if not any(item.get("is_default") for item in self._phase49_3i34_profiles):
            self._phase49_3i34_profiles[0]["is_default"] = True
        self._phase49_3i34_selected_key = ""
        self._phase49_3i34_refresh_tree()

    def _sync_quick_price_visibility(self):
        has_profiles = bool(self._phase49_3i34_profiles)
        for widget in self._phase49_3i34_quick_price_widgets:
            try:
                if has_profiles:
                    widget.grid_remove()
                else:
                    widget.grid()
            except Exception:
                pass

    def reload(self):
        ensure_schema(self.db)
        result = original_reload(self)
        row = self.db.product(self.product_id)
        if row is None or not hasattr(self, "_phase49_3i34_tree"):
            return result
        try:
            raw = json.loads(row["sales_profiles_json"] or "[]")
        except Exception:
            raw = []
        profiles = [normalize_profile(item, index + 1) for index, item in enumerate(raw) if isinstance(item, dict)]
        if not profiles:
            profiles = [seed_profile_from_row(row)]
        if not any(item.get("is_default") for item in profiles):
            profiles[0]["is_default"] = True
        self._phase49_3i34_profiles = profiles
        mode = str(row["sales_profile_selection_mode"] or "size_weight")
        self._phase49_3i34_mode_var.set(SELECTION_MODES.get(mode, SELECTION_MODES["size_weight"]))
        self._phase49_3i34_selector_label_var.set(str(row["sales_profile_selector_label"] or ""))
        self._phase49_3i34_refresh_tree(profiles[0]["key"])
        return result

    def save(self, silent=False):
        if hasattr(self, "_phase49_3i34_tree") and not self._phase49_3i34_commit_editor(quiet=silent):
            return False
        if not original_save(self, silent=True):
            return False
        profiles = [normalize_profile(item, index + 1) for index, item in enumerate(self._phase49_3i34_profiles)]
        active_profiles = [item for item in profiles if item.get("is_active", True)]
        if not active_profiles:
            if not silent:
                messagebox.showwarning("پروفایل محصول", "حداقل یک پروفایل فعال برای فروش لازم است.", parent=self)
            return False
        mode = MODE_BY_LABEL.get(self._phase49_3i34_mode_var.get(), "size_weight")
        seen_keys = set()
        for index, item in enumerate(active_profiles, 1):
            key = str(item.get("key") or "")
            if not key or key in seen_keys:
                if not silent:
                    messagebox.showwarning("پروفایل محصول", f"کلید پروفایل #{index} خالی یا تکراری است.", parent=self)
                return False
            seen_keys.add(key)
            if "weight" in mode and _num(item.get("weight_grams"), 0) <= 0:
                if not silent:
                    messagebox.showwarning("پروفایل محصول", f"وزن «{item.get('name') or index}» برای روش انتخاب فعلی لازم است.", parent=self)
                return False
            if "size" in mode and not str(item.get("size_label") or "").strip():
                if not silent:
                    messagebox.showwarning("پروفایل محصول", f"سایز «{item.get('name') or index}» برای روش انتخاب فعلی لازم است.", parent=self)
                return False
        if profiles:
            defaults = [item for item in profiles if item.get("is_default")]
            if not defaults:
                profiles[0]["is_default"] = True
            elif len(defaults) > 1:
                seen = False
                for item in profiles:
                    if item.get("is_default") and not seen:
                        seen = True
                    elif item.get("is_default"):
                        item["is_default"] = False
        low, high = profile_price_range(active_profiles)
        values = {
            "sales_profiles_json": json.dumps(profiles, ensure_ascii=False),
            "sales_profile_selection_mode": mode,
            "sales_profile_selector_label": self._phase49_3i34_selector_label_var.get().strip(),
        }
        if low:
            values.update({
                "price_min": low,
                "price_max": high,
                "final_price": low if low == high else 0,
                "price_is_final": 1,
                "pricing_strategy": "range" if high > low else "fixed",
            })
        self.db.update_product(self.product_id, values)
        self.row = self.db.product(self.product_id)
        self._phase49_3i34_sync_quick_price_visibility()
        if not silent:
            self.footer_status.set(f"{len(profiles)} پروفایل محلی ثبت شد • لیست محصولات Refresh نشد")
        return True

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i34_build_ui = _build_ui
    workspace_class._phase49_3i34_profile_by_key = _profile_by_key
    workspace_class._phase49_3i34_refresh_tree = _refresh_tree
    workspace_class._phase49_3i34_load_selected = _load_selected
    workspace_class._phase49_3i34_editor_payload = _editor_payload
    workspace_class._phase49_3i34_commit_editor = _commit_editor
    workspace_class._phase49_3i34_add_profile = _add_profile
    workspace_class._phase49_3i34_clone_profile = _clone_profile
    workspace_class._phase49_3i34_delete_profile = _delete_profile
    workspace_class._phase49_3i34_sync_quick_price_visibility = _sync_quick_price_visibility
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_3i34_profile_matrix = True
