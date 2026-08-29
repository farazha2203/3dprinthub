from __future__ import annotations

import threading
import tkinter as tk
from collections import defaultdict
from tkinter import messagebox, ttk

from .env_settings import env_value
from .epic49_desktop_schema import (
    add_available_material_color,
    deactivate_available_material_color,
    list_available_material_colors,
    normalize_material_color_options,
)
from .epic49_site_sync import list_filaments as list_site_filaments
from .epic49_site_sync import sync_filament as sync_site_filament
from .secure_secrets import get_secret
from .site_connection import SiteConnection
from .phase49_3i39_professional_commerce import (
    _integer,
    _number,
    offer_company,
    offer_display,
    offer_key,
    offer_stock_grams,
)
from .phase49_3i40_commerce_precision import filament_rate_calculation


def _active_inventory(db) -> list[dict]:
    rows = []
    for raw in list_available_material_colors(db):
        item = dict(raw)
        normalized = normalize_material_color_options([item])
        if not normalized:
            continue
        value = normalized[0]
        value["_row_id"] = int(item.get("id") or 0)
        value["_is_active"] = bool(item.get("is_active", 1))
        rows.append(value)
    rows.sort(
        key=lambda item: (
            str(item.get("material") or "").casefold(),
            str(item.get("brand") or "").casefold(),
            str(item.get("color") or "").casefold(),
        )
    )
    return rows


def _choice_lists(db) -> dict[str, list[str]]:
    inventory = _active_inventory(db)

    def unique(field):
        values = []
        seen = set()
        for item in inventory:
            value = str(item.get(field) or "").strip()
            if value and value.casefold() not in seen:
                seen.add(value.casefold())
                values.append(value)
        values.sort(key=str.casefold)
        return values

    return {
        "manufacturers": unique("manufacturer"),
        "brands": unique("brand"),
        "materials": unique("material"),
    }


def _bridge_connection(app) -> SiteConnection:
    token = ""
    entered = getattr(app, "_entered_bridge_token", None)
    if callable(entered):
        try:
            token = entered()
        except Exception:
            token = ""
    token = token or env_value("CATALOG_BRIDGE_TOKEN", "") or get_secret("bridge_token")
    site_var = getattr(app, "site_url", None)
    site_url = site_var.get().strip() if site_var is not None else ""
    site_url = site_url or env_value("CATALOG_SITE_URL", "") or str(app.db.setting("site_url", "") or "").strip()
    if not site_url or not token:
        raise ValueError("برای همگام‌سازی Filament، آدرس سایت و Bridge Token باید تنظیم شده باشند.")
    return SiteConnection(
        ftp_host="",
        ftp_port=21,
        ftp_user="",
        ftp_password="",
        remote_root="/",
        site_url=site_url,
        bridge_token=token,
    ).normalized()


def _sync_payload(item: dict) -> dict:
    normalized = normalize_material_color_options([item])
    if not normalized:
        return {}
    value = normalized[0]
    value["is_active"] = bool(item.get("_is_active", True))
    return value


def _status_set(owner, text: str) -> None:
    var = getattr(owner, "footer_status", None) or getattr(owner, "status", None)
    if var is not None:
        try:
            var.set(text)
        except Exception:
            pass


def _async_site_sync(owner, item: dict, on_done=None) -> None:
    app = getattr(owner, "app", owner)
    payload = _sync_payload(item)
    if not payload:
        return

    def work():
        try:
            cfg = _bridge_connection(app)
            result = sync_site_filament(cfg, payload, operator="catalog-center")
            error = None
        except Exception as exc:
            result = None
            error = exc

        def finish():
            key = offer_key(payload)
            status_map = getattr(app, "_phase49_3i41_site_status", None)
            if status_map is None:
                status_map = {}
                app._phase49_3i41_site_status = status_map
            if error is None:
                status_map[key] = "همگام"
                _status_set(owner, f"Filament «{offer_display(payload)}» محلی ذخیره و با سایت همگام شد.")
            else:
                status_map[key] = "خطای Sync"
                _status_set(
                    owner,
                    f"Filament محلی ذخیره شد؛ Sync سایت انجام نشد: {error}",
                )
            refresher = getattr(app, "_phase49_3i41_refresh_library", None)
            if callable(refresher):
                try:
                    refresher(select_key=key)
                except Exception:
                    pass
            if callable(on_done):
                on_done(result, error)

        try:
            app.after(0, finish)
        except Exception:
            finish()

    threading.Thread(target=work, daemon=True).start()


def open_filament_editor(owner, offer=None, *, on_saved=None):
    source = dict(offer or {})
    db = owner.db
    choices = _choice_lists(db)

    top = tk.Toplevel(owner)
    top.title("کتابخانه Filament — تعریف / ویرایش")
    top.geometry("820x780")
    top.transient(owner)
    top.grab_set()

    body = ttk.Frame(top, padding=14)
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
    }
    vars_ = {key: tk.StringVar(value=str(value)) for key, value in defaults.items()}

    ttk.Label(
        body,
        text="شرکت، برند و نوع Filamentهای قبلی از کتابخانه قابل انتخاب‌اند؛ برای مقدار جدید همانجا تایپ کن.",
        style="SubHeader.TLabel",
    ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

    fields = (
        ("manufacturer", "شرکت / سازنده"),
        ("brand", "برند"),
        ("material", "نوع Filament / متریال"),
        ("color", "رنگ"),
        ("hex", "HEX رنگ"),
        ("image", "عکس Filament (URL اختیاری)"),
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
    )
    combo_values = {
        "manufacturer": choices["manufacturers"],
        "brand": choices["brands"],
        "material": choices["materials"],
    }
    for index, (key, label) in enumerate(fields, start=1):
        ttk.Label(body, text=label).grid(row=index, column=0, sticky="w", padx=4, pady=4)
        if key in combo_values:
            widget = ttk.Combobox(
                body,
                textvariable=vars_[key],
                values=combo_values[key],
                state="normal",
            )
        else:
            widget = ttk.Entry(body, textvariable=vars_[key])
        widget.grid(row=index, column=1, sticky="ew", padx=4, pady=4)

    rate_box = ttk.LabelFrame(body, text="محاسبه زنده نرخ نهایی Filament", padding=10)
    rate_box.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew", pady=(10, 4))
    rate_box.columnconfigure(1, weight=1)
    final_roll_var = tk.StringVar()
    rate_per_gram_var = tk.StringVar()
    basis_var = tk.StringVar()

    ttk.Label(rate_box, text="مبلغ نهایی مبنای هر رول").grid(row=0, column=0, sticky="w", padx=4, pady=3)
    ttk.Label(rate_box, textvariable=final_roll_var, font=("Tahoma", 10, "bold")).grid(row=0, column=1, sticky="e", padx=4)
    ttk.Label(rate_box, text="نرخ نهایی مصرف").grid(row=1, column=0, sticky="w", padx=4, pady=3)
    ttk.Label(rate_box, textvariable=rate_per_gram_var, font=("Tahoma", 10, "bold")).grid(row=1, column=1, sticky="e", padx=4)
    ttk.Label(rate_box, textvariable=basis_var, style="SubHeader.TLabel").grid(row=2, column=0, columnspan=2, sticky="e", padx=4)

    def refresh_rate(*_args):
        result = filament_rate_calculation({
            "roll_weight_grams": vars_["roll_weight"].get(),
            "sale_price_per_roll": vars_["sale"].get(),
            "usd_price_per_roll": vars_["usd"].get(),
            "usd_fx_rate_toman": vars_["fx"].get(),
        })
        final_roll_var.set(f"{int(result['final_roll_toman']):,} تومان")
        rate_per_gram_var.set(f"{float(result['rate_per_gram']):,.0f} تومان / گرم")
        basis_var.set(f"مبنای محاسبه: {result['basis']}")

    for key in ("roll_weight", "sale", "usd", "fx"):
        vars_[key].trace_add("write", refresh_rate)
    refresh_rate()

    def save():
        material = vars_["material"].get().strip()
        color = vars_["color"].get().strip()
        brand = vars_["brand"].get().strip()
        manufacturer = vars_["manufacturer"].get().strip()
        if not brand:
            brand = manufacturer
        if not manufacturer:
            manufacturer = brand
        if not material or not color or not brand:
            messagebox.showwarning(
                "Filament",
                "شرکت/برند، نوع Filament و رنگ الزامی هستند.",
                parent=top,
            )
            return

        roll_weight = max(1, _integer(vars_["roll_weight"].get(), 1000))
        stock_kg = max(0.0, float(_number(vars_["stock_kg"].get(), 0)))
        stock_rolls = stock_kg * 1000.0 / roll_weight

        try:
            saved = add_available_material_color(
                db,
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

        top.destroy()
        normalized = _active_inventory(db)
        target = next(
            (item for item in normalized if offer_key(item) == offer_key(saved)),
            normalize_material_color_options([saved])[0] if normalize_material_color_options([saved]) else dict(saved),
        )
        _status_set(owner, f"Filament «{offer_display(target)}» ذخیره شد؛ Sync سایت در حال انجام است.")
        if callable(on_saved):
            on_saved(target)
        _async_site_sync(owner, target)

    actions = ttk.Frame(body)
    actions.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="e", pady=(10, 0))
    ttk.Button(actions, text="انصراف", command=top.destroy).pack(side="right", padx=3)
    ttk.Button(actions, text="ذخیره Filament", command=save, style="Success.TButton").pack(side="right", padx=3)
    return top


def _material_groups(inventory: list[dict]) -> dict[str, list[dict]]:
    groups = defaultdict(list)
    for item in inventory:
        groups[str(item.get("material") or "سایر").strip() or "سایر"].append(item)
    return dict(sorted(groups.items(), key=lambda pair: pair[0].casefold()))


def _format_preheat(item: dict) -> str:
    hours = float(item.get("preheat_hours") or 0)
    temp = float(item.get("preheat_temperature_c") or 0)
    if hours <= 0:
        return "—"
    return f"{hours:g}h / {temp:g}°C"


def _format_rate(item: dict) -> str:
    result = filament_rate_calculation(item)
    return f"{float(result['rate_per_gram']):,.0f}"


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i41_filament_library_app", False):
        return

    def build_library(self):
        ttk.Label(self.filaments_tab, text="کتابخانه مرکزی Filament", style="UX87Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.filaments_tab,
            text="هر Filament یک‌بار تعریف می‌شود؛ همه محصولات از همین کتابخانه انتخاب می‌کنند و Save آن به‌صورت خودکار به سایت Sync می‌شود.",
            style="UX87Muted.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        bar = ttk.Frame(self.filaments_tab)
        bar.pack(fill="x", pady=(0, 8))
        self._phase49_3i41_search_var = tk.StringVar()
        ttk.Label(bar, text="جستجو").pack(side="right", padx=3)
        search = ttk.Entry(bar, textvariable=self._phase49_3i41_search_var, width=28)
        search.pack(side="right", padx=3)
        search.bind("<KeyRelease>", lambda _e: self._phase49_3i41_refresh_library())
        ttk.Button(bar, text="Filament جدید", command=lambda: self._phase49_3i41_open_editor(None), style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(bar, text="ویرایش انتخابی", command=self._phase49_3i41_edit_selected).pack(side="left", padx=3)
        ttk.Button(bar, text="غیرفعال‌کردن انتخابی", command=self._phase49_3i41_deactivate_selected, style="Danger.TButton").pack(side="left", padx=3)
        ttk.Button(bar, text="Sync همه با سایت", command=self._phase49_3i41_sync_all, style="Success.TButton").pack(side="left", padx=3)
        ttk.Button(bar, text="بروزرسانی", command=self._phase49_3i41_refresh_library).pack(side="left", padx=3)

        self._phase49_3i41_library_status = tk.StringVar(value="")
        ttk.Label(
            self.filaments_tab,
            textvariable=self._phase49_3i41_library_status,
            style="UX87Muted.TLabel",
        ).pack(fill="x", pady=(0, 5))

        tree = ttk.Treeview(
            self.filaments_tab,
            columns=("brand", "color", "roll", "stock", "sale", "rate", "preheat", "site"),
            show="tree headings",
            selectmode="browse",
            height=24,
        )
        tree.heading("#0", text="نوع Filament")
        tree.column("#0", width=180, anchor="w")
        for key, label, width in (
            ("brand", "شرکت / برند", 220),
            ("color", "رنگ", 150),
            ("roll", "وزن رول", 100),
            ("stock", "موجودی", 100),
            ("sale", "فروش رول", 120),
            ("rate", "تومان/گرم", 110),
            ("preheat", "پیش‌گرم", 120),
            ("site", "سایت", 100),
        ):
            tree.heading(key, text=label)
            tree.column(key, width=width, anchor="center")
        tree.pack(fill="both", expand=True)
        self._phase49_3i41_library_tree = tree
        self._phase49_3i41_library_rows = {}
        self._phase49_3i41_site_status = getattr(self, "_phase49_3i41_site_status", {})
        self._phase49_3i41_refresh_library()

    def refresh_library(self, select_key=None):
        tree = getattr(self, "_phase49_3i41_library_tree", None)
        if tree is None:
            return
        search_var = getattr(self, "_phase49_3i41_search_var", None)
        query = str(search_var.get() if search_var is not None else "").strip().casefold()
        for iid in tree.get_children():
            tree.delete(iid)
        inventory = [
            item for item in _active_inventory(self.db)
            if not query
            or query in str(item.get("material") or "").casefold()
            or query in str(item.get("brand") or "").casefold()
            or query in str(item.get("manufacturer") or "").casefold()
            or query in str(item.get("color") or "").casefold()
        ]
        self._phase49_3i41_library_rows = {}
        groups = _material_groups(inventory)
        for group_index, (material, items) in enumerate(groups.items()):
            parent = f"mat::{group_index}"
            tree.insert("", "end", iid=parent, text=f"{material} ({len(items)})", open=True)
            for item in items:
                key = offer_key(item)
                iid = f"fil::{item.get('_row_id') or len(self._phase49_3i41_library_rows)+1}"
                self._phase49_3i41_library_rows[iid] = item
                site_state = self._phase49_3i41_site_status.get(key, "—")
                tree.insert(
                    parent,
                    "end",
                    iid=iid,
                    text=material,
                    values=(
                        f"{offer_company(item)} / {item.get('brand') or '—'}",
                        item.get("color") or "—",
                        f"{float(item.get('roll_weight_grams') or 0):g}g",
                        f"{offer_stock_grams(item)/1000:g}kg",
                        f"{_integer(item.get('sale_price_per_roll'), 0):,}",
                        _format_rate(item),
                        _format_preheat(item),
                        site_state,
                    ),
                )
                if select_key is not None and key == select_key:
                    tree.selection_set(iid)
                    tree.focus(iid)
                    tree.see(iid)
        self._phase49_3i41_library_status.set(
            f"{len(inventory)} Filament فعال در {len(groups)} گروه متریال"
        )

    def selected_library_item(self):
        tree = getattr(self, "_phase49_3i41_library_tree", None)
        if tree is None or not tree.selection():
            return None
        return self._phase49_3i41_library_rows.get(str(tree.selection()[0]))

    def open_editor(self, offer=None):
        def after_saved(saved):
            self._phase49_3i41_refresh_library(select_key=offer_key(saved))
        return open_filament_editor(self, offer, on_saved=after_saved)

    def edit_selected(self):
        item = selected_library_item(self)
        if item is None:
            messagebox.showinfo("Filament", "یک Filament را انتخاب کن.", parent=self)
            return
        open_editor(self, item)

    def deactivate_selected(self):
        item = selected_library_item(self)
        if item is None:
            messagebox.showinfo("Filament", "یک Filament را انتخاب کن.", parent=self)
            return
        if not messagebox.askyesno(
            "Filament",
            f"«{offer_display(item)}» غیرفعال شود؟\nرکورد حذف نمی‌شود و برای تاریخچه باقی می‌ماند.",
            parent=self,
        ):
            return
        deactivate_available_material_color(self.db, int(item.get("_row_id") or 0))
        refresh_library(self)
        _status_set(self, "Filament غیرفعال شد؛ حذف دائمی انجام نشد.")

    def sync_all(self):
        inventory = _active_inventory(self.db)
        if not inventory:
            return
        self._phase49_3i41_library_status.set(f"Sync {len(inventory)} Filament با سایت…")

        def work():
            ok = 0
            failed = []
            try:
                cfg = _bridge_connection(self)
            except Exception as exc:
                failed = [str(exc)]
                cfg = None
            if cfg is not None:
                for item in inventory:
                    try:
                        sync_site_filament(cfg, _sync_payload(item), operator="catalog-center")
                        ok += 1
                    except Exception as exc:
                        failed.append(f"{offer_display(item)}: {exc}")
            try:
                remote_count = len(list_site_filaments(cfg)) if cfg is not None else 0
            except Exception:
                remote_count = 0

            def finish():
                if not failed:
                    for item in inventory:
                        self._phase49_3i41_site_status[offer_key(item)] = "همگام"
                    self._phase49_3i41_library_status.set(
                        f"Sync کامل: {ok}/{len(inventory)} • سایت {remote_count} Filament فعال گزارش کرد"
                    )
                else:
                    self._phase49_3i41_library_status.set(
                        f"Sync: {ok}/{len(inventory)} موفق • {len(failed)} خطا"
                    )
                refresh_library(self)
            self.after(0, finish)

        threading.Thread(target=work, daemon=True).start()

    app_class._build_phase49_3i41_filament_library = build_library
    app_class._phase49_3i41_refresh_library = refresh_library
    app_class._phase49_3i41_selected_library_item = selected_library_item
    app_class._phase49_3i41_open_editor = open_editor
    app_class._phase49_3i41_edit_selected = edit_selected
    app_class._phase49_3i41_deactivate_selected = deactivate_selected
    app_class._phase49_3i41_sync_all = sync_all
    app_class._phase49_3i41_filament_library_app = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i41_filament_checklist", False):
        return

    original_init = workspace_class.__init__
    original_reload = workspace_class.reload

    def build_checklist(self):
        old_tree = getattr(self, "_phase49_3i39_offer_tree", None)
        if old_tree is None:
            return
        host = old_tree.master
        for child in list(host.winfo_children()):
            try:
                manager = child.winfo_manager()
                if manager == "grid":
                    child.grid_remove()
                elif manager == "pack":
                    child.pack_forget()
            except Exception:
                pass

        root = ttk.Frame(host)
        root.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(1, weight=1)
        host.columnconfigure(0, weight=1)
        host.rowconfigure(0, weight=1)

        ttk.Label(
            root,
            text="با یک کلیک Filament را انتخاب/لغو کن. روی نام گروه PLA/PETG کلیک کن تا کل همان گروه انتخاب یا پاک شود.",
            style="SubHeader.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        library = ttk.LabelFrame(root, text="Filamentهای موجود — تفکیک بر اساس نوع", padding=6)
        library.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        library.rowconfigure(0, weight=1)
        library.columnconfigure(0, weight=1)

        tree = ttk.Treeview(
            library,
            columns=("check", "brand", "color", "stock", "rate", "preheat"),
            show="tree headings",
            selectmode="none",
            height=10,
        )
        tree.heading("#0", text="نوع Filament")
        tree.column("#0", width=170, anchor="w")
        for key, label, width in (
            ("check", "انتخاب", 70),
            ("brand", "شرکت / برند", 180),
            ("color", "رنگ", 130),
            ("stock", "موجودی", 90),
            ("rate", "تومان/گرم", 100),
            ("preheat", "پیش‌گرم", 110),
        ):
            tree.heading(key, text=label)
            tree.column(key, width=width, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(library, orient="vertical", command=tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scroll.set)

        selected_box = ttk.LabelFrame(root, text="انتخاب‌های این محصول", padding=6)
        selected_box.grid(row=1, column=1, sticky="nsew")
        selected_box.rowconfigure(0, weight=1)
        selected_box.columnconfigure(0, weight=1)
        selected = ttk.Treeview(
            selected_box,
            columns=("material", "brand", "color", "stock", "rate"),
            show="headings",
            height=10,
            selectmode="none",
        )
        for key, label, width in (
            ("material", "نوع", 90),
            ("brand", "برند", 130),
            ("color", "رنگ", 110),
            ("stock", "موجودی", 85),
            ("rate", "تومان/گرم", 95),
        ):
            selected.heading(key, text=label)
            selected.column(key, width=width, anchor="center")
        selected.grid(row=0, column=0, sticky="nsew")
        selected_scroll = ttk.Scrollbar(selected_box, orient="vertical", command=selected.yview)
        selected_scroll.grid(row=0, column=1, sticky="ns")
        selected.configure(yscrollcommand=selected_scroll.set)

        actions = ttk.Frame(root)
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(
            actions,
            text="✓ ثبت انتخاب‌ها روی این محصول",
            command=self._phase49_3i41_commit_checklist,
            style="Success.TButton",
        ).pack(side="right", padx=3)
        ttk.Button(
            actions,
            text="پاک کردن همه انتخاب‌ها",
            command=self._phase49_3i41_clear_checklist,
        ).pack(side="right", padx=3)
        ttk.Button(
            actions,
            text="مدیریت / تعریف Filament در کتابخانه اصلی",
            command=self._phase49_3i41_open_main_library,
            style="Primary.TButton",
        ).pack(side="right", padx=3)
        self._phase49_3i41_selection_status = tk.StringVar()
        ttk.Label(actions, textvariable=self._phase49_3i41_selection_status, style="SubHeader.TLabel").pack(side="left", padx=5)

        self._phase49_3i41_tree = tree
        self._phase49_3i41_selected_tree = selected
        self._phase49_3i41_iid_to_offer = {}
        self._phase49_3i41_group_children = {}
        self._phase49_3i41_draft_keys = {
            offer_key(item)
            for item in getattr(self, "_phase49_3i39_selected_product_offers", []) or []
        }

        tree.bind("<Button-1>", self._phase49_3i41_tree_click)
        self._phase49_3i41_refresh_checklist()

    def refresh_checklist(self):
        tree = getattr(self, "_phase49_3i41_tree", None)
        selected_tree = getattr(self, "_phase49_3i41_selected_tree", None)
        if tree is None or selected_tree is None:
            return
        inventory = _active_inventory(self.db)
        self._phase49_3i41_inventory = inventory
        valid_keys = {offer_key(item) for item in inventory}
        persisted_keys = {
            offer_key(item)
            for item in getattr(self, "_phase49_3i39_selected_product_offers", []) or []
        }
        if not hasattr(self, "_phase49_3i41_draft_keys"):
            self._phase49_3i41_draft_keys = set(persisted_keys)
        self._phase49_3i41_draft_keys = {
            key for key in self._phase49_3i41_draft_keys if key in valid_keys
        }

        for iid in tree.get_children():
            tree.delete(iid)
        self._phase49_3i41_iid_to_offer = {}
        self._phase49_3i41_group_children = {}

        groups = _material_groups(inventory)
        for group_index, (material, items) in enumerate(groups.items()):
            parent = f"mat::{group_index}"
            child_ids = []
            selected_count = sum(1 for item in items if offer_key(item) in self._phase49_3i41_draft_keys)
            if selected_count == len(items) and items:
                group_mark = "☑"
            elif selected_count:
                group_mark = "◩"
            else:
                group_mark = "☐"
            tree.insert(
                "",
                "end",
                iid=parent,
                text=f"{material} ({len(items)})",
                values=(group_mark, "", "", "", "", ""),
                open=True,
            )
            for index, item in enumerate(items):
                iid = f"fil::{group_index}::{index}"
                child_ids.append(iid)
                self._phase49_3i41_iid_to_offer[iid] = item
                checked = offer_key(item) in self._phase49_3i41_draft_keys
                tree.insert(
                    parent,
                    "end",
                    iid=iid,
                    text="",
                    values=(
                        "☑" if checked else "☐",
                        f"{offer_company(item)} / {item.get('brand') or '—'}",
                        item.get("color") or "—",
                        f"{offer_stock_grams(item)/1000:g}kg",
                        _format_rate(item),
                        _format_preheat(item),
                    ),
                )
            self._phase49_3i41_group_children[parent] = child_ids

        for iid in selected_tree.get_children():
            selected_tree.delete(iid)
        chosen = [item for item in inventory if offer_key(item) in self._phase49_3i41_draft_keys]
        for index, item in enumerate(chosen):
            selected_tree.insert(
                "",
                "end",
                iid=f"sel::{index}",
                values=(
                    item.get("material") or "—",
                    item.get("brand") or offer_company(item) or "—",
                    item.get("color") or "—",
                    f"{offer_stock_grams(item)/1000:g}kg",
                    _format_rate(item),
                ),
            )
        self._phase49_3i41_selection_status.set(
            f"{len(chosen)} Filament انتخاب شده • ثبت‌شده روی محصول: {len(persisted_keys)}"
        )

    def tree_click(self, event):
        tree = getattr(self, "_phase49_3i41_tree", None)
        if tree is None:
            return
        iid = tree.identify_row(event.y)
        if not iid:
            return
        if iid.startswith("mat::"):
            children = self._phase49_3i41_group_children.get(iid, [])
            keys = {
                offer_key(self._phase49_3i41_iid_to_offer[child])
                for child in children
                if child in self._phase49_3i41_iid_to_offer
            }
            if keys and keys.issubset(self._phase49_3i41_draft_keys):
                self._phase49_3i41_draft_keys.difference_update(keys)
            else:
                self._phase49_3i41_draft_keys.update(keys)
        else:
            item = self._phase49_3i41_iid_to_offer.get(iid)
            if item is None:
                return
            key = offer_key(item)
            if key in self._phase49_3i41_draft_keys:
                self._phase49_3i41_draft_keys.remove(key)
            else:
                self._phase49_3i41_draft_keys.add(key)
        refresh_checklist(self)
        refresher = getattr(self, "_phase49_3i39_refresh_price_summary", None)
        if callable(refresher):
            refresher()
        return "break"

    def selected_draft_offers(self):
        inventory = getattr(self, "_phase49_3i41_inventory", None) or _active_inventory(self.db)
        return [
            item for item in inventory
            if offer_key(item) in getattr(self, "_phase49_3i41_draft_keys", set())
        ]

    def commit_checklist(self):
        if not getattr(self, "_phase49_3i41_draft_keys", set()):
            messagebox.showwarning(
                "Filament",
                "حداقل یک Filament را از چک‌لیست انتخاب کن.",
                parent=self,
            )
            return False
        self._phase49_3i39_selected_product_offers = selected_draft_offers(self)
        ok = self._phase49_3i39_persist_selected_offers(propagate_profiles=True)
        if ok:
            refresh_checklist(self)
            self.footer_status.set(
                f"{len(self._phase49_3i39_selected_product_offers)} Filament روی محصول ثبت شد؛ Sync سایت در حال انجام است."
            )
            for item in self._phase49_3i39_selected_product_offers:
                _async_site_sync(self, item)
        return ok

    def clear_checklist(self):
        self._phase49_3i41_draft_keys = set()
        refresh_checklist(self)
        refresher = getattr(self, "_phase49_3i39_refresh_price_summary", None)
        if callable(refresher):
            refresher()

    def open_main_library(self):
        app = getattr(self, "app", None)
        if app is None:
            return
        try:
            app.show_ux87_page("filaments")
            app.lift()
            app.focus_force()
        except Exception:
            pass
        self.footer_status.set("کتابخانه مرکزی Filament در پنجره اصلی باز شد.")

    def open_editor(self, offer=None):
        def after_saved(_saved):
            refresh_checklist(self)
        return open_filament_editor(self, offer, on_saved=after_saved)

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        build_checklist(self)

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "_phase49_3i41_tree"):
            self._phase49_3i41_draft_keys = {
                offer_key(item)
                for item in getattr(self, "_phase49_3i39_selected_product_offers", []) or []
            }
            refresh_checklist(self)
        return result

    workspace_class._phase49_3i41_build_checklist = build_checklist
    workspace_class._phase49_3i41_refresh_checklist = refresh_checklist
    workspace_class._phase49_3i41_tree_click = tree_click
    workspace_class._phase49_3i41_selected_draft_offers = selected_draft_offers
    workspace_class._phase49_3i41_commit_checklist = commit_checklist
    workspace_class._phase49_3i41_clear_checklist = clear_checklist
    workspace_class._phase49_3i41_open_main_library = open_main_library
    workspace_class._phase49_3i39_open_offer_editor = open_editor
    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class._phase49_3i41_filament_checklist = True
