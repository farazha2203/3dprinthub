from __future__ import annotations

import copy
import re
import webbrowser
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_desktop_schema import (
    add_available_material_color,
    effective_filament_offer_price_per_gram,
    normalize_material_color_options,
)
from .phase49_3i36_stage_finalization import STAGE_LABELS, STAGE_ORDER, is_stage_locked, stage_locks
from .phase49_3i39_professional_commerce import (
    _integer,
    _number,
    offer_display,
    offer_key,
    offer_stock_grams,
)

PHASE = "49.3I.40"

COLOR_NAME_HEX = {
    "white": "#F5F5F5", "سفید": "#F5F5F5",
    "black": "#111111", "مشکی": "#111111", "سیاه": "#111111",
    "red": "#E53935", "قرمز": "#E53935",
    "pink": "#EC407A", "صورتی": "#EC407A",
    "blue": "#1E88E5", "آبی": "#1E88E5",
    "green": "#43A047", "سبز": "#43A047",
    "yellow": "#FDD835", "زرد": "#FDD835",
    "orange": "#FB8C00", "نارنجی": "#FB8C00",
    "purple": "#8E24AA", "بنفش": "#8E24AA",
    "gray": "#9E9E9E", "grey": "#9E9E9E", "خاکستری": "#9E9E9E", "طوسی": "#9E9E9E",
    "brown": "#795548", "قهوه‌ای": "#795548", "قهوه ای": "#795548",
    "gold": "#D4AF37", "golden": "#D4AF37", "طلایی": "#D4AF37",
    "silver": "#BDBDBD", "نقره‌ای": "#BDBDBD", "نقره ای": "#BDBDBD",
    "cyan": "#00ACC1", "فیروزه‌ای": "#00ACC1", "فیروزه ای": "#00ACC1",
    "beige": "#D7CCC8", "کرم": "#D7CCC8",
}


def color_preview_hex(offer: dict) -> str:
    explicit = str(offer.get("hex") or offer.get("hex_code") or "").strip()
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", explicit):
        return explicit.upper()
    name = str(offer.get("color") or offer.get("color_name") or "").strip().casefold()
    if name in COLOR_NAME_HEX:
        return COLOR_NAME_HEX[name]
    for token, value in COLOR_NAME_HEX.items():
        if token in name:
            return value
    return "#D9D9D9"


def merge_offer_scope(existing: list[dict], visible: list[dict], selected: list[dict]) -> list[dict]:
    """Replace only the visible company/material filter, preserving other brands."""
    current = normalize_material_color_options(existing or [])
    visible_keys = {offer_key(item) for item in normalize_material_color_options(visible or [])}
    selected_rows = normalize_material_color_options(selected or [])
    previous = {offer_key(item): item for item in current}
    kept = [copy.deepcopy(item) for item in current if offer_key(item) not in visible_keys]
    for item in selected_rows:
        old = previous.get(offer_key(item), {})
        item["fixed_product_price"] = _integer(old.get("fixed_product_price"), 0)
        kept.append(item)
    return normalize_material_color_options(kept)


def apply_product_fixed_prices(offers: list[dict], prices: dict[tuple[str, str, str], int]) -> list[dict]:
    output = []
    for item in normalize_material_color_options(offers or []):
        row = copy.deepcopy(item)
        key = offer_key(row)
        if key in prices:
            row["fixed_product_price"] = max(0, _integer(prices[key], 0))
        output.append(row)
    return normalize_material_color_options(output)


def filament_rate_calculation(item: dict) -> dict[str, float | str]:
    """Return the explicit final roll basis + per-gram rate; never invent FX."""
    roll_weight = max(1.0, float(_number(item.get("roll_weight_grams"), 1000)))
    sale_roll = max(0.0, float(_number(item.get("sale_price_per_roll"), 0)))
    usd_roll = max(0.0, float(_number(item.get("usd_price_per_roll"), 0)))
    fx = max(0.0, float(_number(item.get("usd_fx_rate_toman"), 0)))
    usd_toman = usd_roll * fx if usd_roll > 0 and fx > 0 else 0.0
    final_roll = max(sale_roll, usd_toman)
    if final_roll <= 0:
        basis = "نرخ فروش/دلار هنوز کامل نیست"
    elif usd_toman > sale_roll:
        basis = "دلار × نرخ ثبت‌شده"
    elif sale_roll > usd_toman:
        basis = "قیمت فروش هر رول"
    else:
        basis = "فروش رول = دلار × نرخ"
    return {
        "roll_weight_grams": roll_weight,
        "sale_roll_toman": sale_roll,
        "usd_roll_toman": usd_toman,
        "final_roll_toman": final_roll,
        "rate_per_gram": float(effective_filament_offer_price_per_gram({
            **dict(item or {}),
            "roll_weight_grams": roll_weight,
            "sale_price_per_roll": sale_roll,
            "usd_price_per_roll": usd_roll,
            "usd_fx_rate_toman": fx,
        })),
        "basis": basis,
    }


def readiness_display(state: dict, row) -> dict:
    stages = state.get("stages") or {}
    data_defects = []
    pending_finalization = []
    for stage in STAGE_ORDER:
        info = stages.get(stage) or {}
        for item in info.get("missing_data") or []:
            data_defects.append(f"{STAGE_LABELS[stage]}: {item}")
        if bool(info.get("data_ready")) and not is_stage_locked(row, stage):
            pending_finalization.append(stage)
    return {
        "data_defects": data_defects,
        "data_defect_count": len(data_defects),
        "pending_finalization": pending_finalization,
        "pending_finalization_count": len(pending_finalization),
    }


class _CompletionProgressProxy:
    """Suppress cosmetic 100% until the final defect snapshot proves AI is done."""

    def __init__(self, dialog):
        self._dialog = dialog
        self.cancelled = dialog.cancelled
        self.held_terminal = None

    def event(self, *args, **kwargs):
        return self._dialog.event(*args, **kwargs)

    def set_progress(self, value, message=""):
        numeric = float(value or 0)
        if numeric >= 100:
            self.held_terminal = (numeric, message)
            return None
        return self._dialog.set_progress(numeric, message)

    def __getattr__(self, name):
        return getattr(self._dialog, name)


def install_completion_progress_truth() -> None:
    from . import phase49_3i39_completion_loop as completion

    if getattr(completion, "_phase49_3i40_progress_truth", False):
        return
    original = completion.repair_until_stable

    def repair_until_stable(app, product_id, dialog, **kwargs):
        proxy = _CompletionProgressProxy(dialog)
        result = original(app, product_id, proxy, **kwargs)
        final = dict(result.get("final") or {})
        remaining = int(
            result.get("scoped_ai_fixable_count", final.get("ai_fixable_count"))
            or 0
        )
        if remaining <= 0:
            dialog.set_progress(100, "بازبینی Scope انجام شد • نقص AI-قابل‌اصلاح صفر")
        else:
            dialog.set_progress(
                94,
                f"متوقف با {remaining} نقص AI-قابل‌اصلاح باقی‌مانده — 100٪ ثبت نشد",
            )
            dialog.event(
                "completion_not_100",
                f"{remaining} نقص AI-قابل‌اصلاح باقی مانده؛ عملیات 100٪ اعلام نشد.",
                {
                    "remaining_ai_fixable": final.get("ai_fixable") or {},
                    "remaining_data_defects": final.get("data_missing") or {},
                },
            )
        return result

    completion.repair_until_stable = repair_until_stable
    completion._phase49_3i40_progress_truth = True


def _find_label_frame(root, prefix: str):
    try:
        children = root.winfo_children()
    except Exception:
        return None
    for child in children:
        try:
            if isinstance(child, ttk.LabelFrame) and str(child.cget("text") or "").startswith(prefix):
                return child
        except Exception:
            pass
    return None


def _global_offer_editor(workspace, offer=None):
    source = dict(offer or {})
    top = tk.Toplevel(workspace)
    top.title("Filament جهانی — سازنده / متریال / رنگ / نرخ / موجودی / پیش‌گرم")
    top.geometry("780x700")
    top.transient(workspace)
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
    }
    vars_ = {key: tk.StringVar(value=str(value)) for key, value in defaults.items()}
    fields = (
        ("manufacturer", "شرکت / سازنده"),
        ("brand", "برند"),
        ("material", "نوع فیلامنت / متریال"),
        ("color", "رنگ"),
        ("hex", "HEX رنگ"),
        ("image", "عکس فیلامنت (URL یا مسیر محلی اختیاری)"),
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
    for index, (key, label) in enumerate(fields):
        ttk.Label(body, text=label).grid(row=index, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(body, textvariable=vars_[key]).grid(row=index, column=1, sticky="ew", padx=4, pady=4)
    ttk.Label(
        body,
        text="قیمت قطعی محصول اینجا ثبت نمی‌شود؛ آن مبلغ فقط به همین محصول تعلق دارد و در بخش قیمت‌گذاری وارد می‌شود.",
        style="SubHeader.TLabel",
    ).grid(row=len(fields), column=0, columnspan=2, sticky="w", padx=4, pady=(8, 4))

    rate_box = ttk.LabelFrame(
        body,
        text="محاسبه نرخ نهایی Filament",
        padding=7,
    )
    rate_box.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 8))
    self_rate = tk.StringVar(value="")
    ttk.Label(
        rate_box,
        textvariable=self_rate,
        style="SubHeader.TLabel",
    ).pack(anchor="e")

    def refresh_rate_calculation(*_args):
        result = filament_rate_calculation({
            "roll_weight_grams": vars_["roll_weight"].get(),
            "sale_price_per_roll": vars_["sale"].get(),
            "usd_price_per_roll": vars_["usd"].get(),
            "usd_fx_rate_toman": vars_["fx"].get(),
        })
        final_roll = int(round(float(result["final_roll_toman"])))
        rate = float(result["rate_per_gram"])
        self_rate.set(
            f"مبلغ نهایی مبنای هر رول: {final_roll:,} تومان"
            f" • نرخ نهایی مصرف: {rate:,.0f} تومان/گرم"
            f" • مبنا: {result['basis']}"
        )

    for key in ("roll_weight", "sale", "usd", "fx"):
        vars_[key].trace_add("write", refresh_rate_calculation)
    refresh_rate_calculation()

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
                workspace.db,
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
        workspace._phase49_3i39_refresh_offer_filter()
        refresher = getattr(workspace, "_phase49_3i39_refresh_price_summary", None)
        if callable(refresher):
            refresher()
        workspace.footer_status.set(
            f"Filament جهانی «{offer_display(saved)}» ذخیره شد؛ قیمت قطعی این محصول دست‌نخورده است."
        )

    actions = ttk.Frame(body)
    actions.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="e", pady=(10, 0))
    ttk.Button(actions, text="انصراف", command=top.destroy).pack(side="right", padx=3)
    ttk.Button(actions, text="ذخیره Filament جهانی", command=save_offer, style="Success.TButton").pack(side="right", padx=3)


def install_workspace(workspace_class) -> None:
    install_completion_progress_truth()
    if getattr(workspace_class, "_phase49_3i40_commerce_precision", False):
        return

    original_init = workspace_class.__init__
    original_refresh_readiness = getattr(workspace_class, "_phase49_refresh_readiness", None)

    def commit_selected_offers(self):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            self.footer_status.set("مرحله ۲ نهایی است؛ برای تغییر Filament ابتدا «اصلاح» را بزن.")
            return False
        selected = self._phase49_3i39_selected_inventory_offers()
        visible = list(getattr(self, "_phase49_3i39_working_offer_rows", []) or [])
        existing = list(getattr(self, "_phase49_3i39_selected_product_offers", []) or [])
        merged = merge_offer_scope(existing, visible, selected)
        if not merged:
            messagebox.showwarning("Filament", "محصول باید حداقل یک Filament ثبت‌شده داشته باشد.", parent=self)
            return False
        self._phase49_3i39_selected_product_offers = merged
        ok = self._phase49_3i39_persist_selected_offers(propagate_profiles=True)
        if ok:
            outside = len(merged) - len(selected)
            self.footer_status.set(
                f"{len(merged)} Filament روی محصول ثبت است • {len(selected)} در فیلتر فعلی • {max(0, outside)} از برند/فیلترهای دیگر حفظ شد"
            )
        return ok

    def open_offer_editor(self, offer=None):
        return _global_offer_editor(self, offer)

    def open_fixed_price_editor(self):
        if is_stage_locked(self.db.product(int(self.product_id)), "commerce"):
            messagebox.showwarning("قیمت قطعی", "مرحله ۲ نهایی است؛ ابتدا «اصلاح» را بزن.", parent=self)
            return
        offers = normalize_material_color_options(
            getattr(self, "_phase49_3i39_selected_product_offers", []) or []
        )
        if not offers:
            messagebox.showinfo("قیمت قطعی", "ابتدا Filamentهای برند/متریال/رنگ را روی محصول ثبت کن.", parent=self)
            return
        top = tk.Toplevel(self)
        top.title("قیمت قطعی Filamentهای همین محصول")
        top.geometry("860x620")
        top.transient(self)
        top.grab_set()
        host = ttk.Frame(top, padding=12)
        host.pack(fill="both", expand=True)
        ttk.Label(
            host,
            text="این مبلغ فقط برای همین محصول + همین برند/فیلامنت/رنگ است و نرخ جهانی فیلامنت را تغییر نمی‌دهد.",
            style="SubHeader.TLabel",
        ).pack(fill="x", pady=(0, 8))
        canvas = tk.Canvas(host, highlightthickness=0)
        scroll = ttk.Scrollbar(host, orient="vertical", command=canvas.yview)
        body = ttk.Frame(canvas)
        body.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        vars_ = {}
        for index, offer in enumerate(offers):
            row = ttk.Frame(body, padding=(4, 5))
            row.grid(row=index, column=0, sticky="ew")
            body.columnconfigure(0, weight=1)
            swatch = tk.Canvas(row, width=28, height=28, highlightthickness=1, highlightbackground="#888")
            swatch.pack(side="right", padx=4)
            swatch.create_rectangle(0, 0, 28, 28, fill=color_preview_hex(offer), outline="")
            ttk.Label(row, text=offer_display(offer), width=44).pack(side="right", padx=5)
            var = tk.StringVar(value=str(_integer(offer.get("fixed_product_price"), 0) or ""))
            vars_[offer_key(offer)] = var
            ttk.Label(row, text="قیمت قطعی (تومان)").pack(side="right", padx=(12, 3))
            ttk.Entry(row, textvariable=var, width=20).pack(side="right", padx=3)
        actions = ttk.Frame(top, padding=10)
        actions.pack(fill="x")

        def save_prices():
            prices = {key: _integer(var.get(), 0) for key, var in vars_.items()}
            updated = apply_product_fixed_prices(offers, prices)
            self._phase49_3i39_selected_product_offers = updated
            if not self._phase49_3i39_persist_selected_offers(propagate_profiles=True):
                return
            top.destroy()
            self._phase49_3i39_refresh_offer_filter()
            refresher = getattr(self, "_phase49_3i39_refresh_price_summary", None)
            if callable(refresher):
                refresher()
            self.footer_status.set("قیمت قطعی هر Filament فقط برای همین محصول ذخیره شد.")

        ttk.Button(actions, text="انصراف", command=top.destroy).pack(side="right", padx=3)
        ttk.Button(actions, text="✓ ذخیره قیمت‌های قطعی محصول", command=save_prices, style="Success.TButton").pack(side="right", padx=3)

    def refresh_offer_preview(self):
        canvas = getattr(self, "_phase49_3i40_color_canvas", None)
        label = getattr(self, "_phase49_3i40_offer_preview_var", None)
        image_button = getattr(self, "_phase49_3i40_image_button", None)
        tree = getattr(self, "_phase49_3i39_offer_tree", None)
        if canvas is None or label is None or tree is None:
            return
        selection = tree.selection()
        if not selection:
            label.set("یک رنگ/Filament را انتخاب کن؛ Preview اینجا نمایش داده می‌شود.")
            canvas.delete("all")
            canvas.create_rectangle(0, 0, 52, 52, fill="#D9D9D9", outline="")
            if image_button is not None:
                image_button.state(["disabled"])
            return
        try:
            offer = self._phase49_3i39_working_offer_rows[int(selection[0])]
        except Exception:
            return
        color = color_preview_hex(offer)
        canvas.delete("all")
        canvas.create_rectangle(0, 0, 52, 52, fill=color, outline="")
        stock = offer_stock_grams(offer) / 1000.0
        label.set(f"{offer_display(offer)} • {color} • موجودی {stock:g} kg")
        image_url = str(offer.get("filament_image_url") or "").strip()
        self._phase49_3i40_image_url = image_url
        if image_button is not None:
            image_button.state(["!disabled"] if image_url else ["disabled"])

    def open_offer_image(self):
        value = str(getattr(self, "_phase49_3i40_image_url", "") or "").strip()
        if not value:
            return
        if value.startswith(("http://", "https://")):
            webbrowser.open(value)
            return
        path = Path(value.replace("file://", "", 1))
        if path.is_file():
            try:
                webbrowser.open(path.resolve().as_uri())
            except Exception:
                pass

    def refresh_readiness(self):
        if callable(original_refresh_readiness):
            original_refresh_readiness(self)
        if not hasattr(self, "_phase49_readiness_summary"):
            return
        from . import phase49_readiness_wizard as readiness
        row = self.db.product(int(self.product_id))
        state = readiness.evaluate_readiness(row)
        self._phase49_readiness_state = state
        display = readiness_display(state, row)
        defects = display["data_defects"]
        pending = display["pending_finalization"]
        buttons = getattr(self, "_section_buttons", {})
        locks = stage_locks(row)
        for stage, button in buttons.items():
            info = (state.get("stages") or {}).get(stage) or {}
            data_ready = bool(info.get("data_ready"))
            locked = bool((locks.get(stage) or {}).get("locked"))
            icon = "✅" if locked and data_ready else ("◌" if data_ready else "❌")
            try:
                button.configure(text=f"{icon} {STAGE_LABELS.get(stage, stage)}")
            except Exception:
                pass
        if state.get("production_ready"):
            self._phase49_readiness_summary.set("✅ محصول آماده انتشار روی سایت اصلی است")
            self._phase49_readiness_missing.set("همه نقص‌های داده رفع و همه Stageها ثبت نهایی شده‌اند.")
        else:
            self._phase49_readiness_summary.set(
                f"نقص داده: {len(defects)} • منتظر ثبت و تأیید: {len(pending)}"
            )
            lines = defects[:4]
            if pending:
                lines.append(
                    "◌ کامل ولی منتظر ثبت و تأیید: "
                    + "، ".join(STAGE_LABELS[s] for s in pending[:3])
                    + ("…" if len(pending) > 3 else "")
                )
            self._phase49_readiness_missing.set("\n".join(lines) + ("\n…" if len(defects) > 4 else ""))

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        panel = getattr(self, "_phase49_3i39_panel", None)
        if panel is not None:
            pricing = _find_label_frame(panel, "۲)")
            if pricing is not None:
                ttk.Button(
                    pricing,
                    text="✏ قیمت قطعی Filamentهای همین محصول",
                    command=self._phase49_3i40_open_fixed_price_editor,
                    style="Primary.TButton",
                ).pack(side="right", padx=6)
        tree = getattr(self, "_phase49_3i39_offer_tree", None)
        if tree is not None:
            parent = tree.master
            preview = ttk.Frame(parent, padding=(4, 6))
            preview.grid(row=3, column=0, sticky="ew")
            self._phase49_3i40_color_canvas = tk.Canvas(
                preview, width=52, height=52, highlightthickness=1, highlightbackground="#888"
            )
            self._phase49_3i40_color_canvas.pack(side="right", padx=6)
            self._phase49_3i40_offer_preview_var = tk.StringVar(
                value="یک رنگ/Filament را انتخاب کن؛ Preview اینجا نمایش داده می‌شود."
            )
            ttk.Label(
                preview, textvariable=self._phase49_3i40_offer_preview_var, style="SubHeader.TLabel"
            ).pack(side="right", padx=5)
            self._phase49_3i40_image_button = ttk.Button(
                preview,
                text="🖼 باز کردن عکس فیلامنت",
                command=self._phase49_3i40_open_offer_image,
            )
            self._phase49_3i40_image_button.pack(side="left", padx=5)
            self._phase49_3i40_image_button.state(["disabled"])
            tree.bind(
                "<<TreeviewSelect>>",
                lambda _e: self._phase49_3i40_refresh_offer_preview(),
                add="+",
            )
            self._phase49_3i40_refresh_offer_preview()
        self._phase49_refresh_readiness()

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i39_commit_selected_offers = commit_selected_offers
    workspace_class._phase49_3i39_open_offer_editor = open_offer_editor
    workspace_class._phase49_3i40_open_fixed_price_editor = open_fixed_price_editor
    workspace_class._phase49_3i40_refresh_offer_preview = refresh_offer_preview
    workspace_class._phase49_3i40_open_offer_image = open_offer_image
    workspace_class._phase49_refresh_readiness = refresh_readiness
    workspace_class._phase49_3i40_commerce_precision = True
