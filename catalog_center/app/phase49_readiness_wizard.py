from __future__ import annotations

import json
from tkinter import messagebox, ttk

from .phase49_dual_publish_desktop import LOCAL_BUTTON_TEXT, SITE_BUTTON_TEXT
from .v8_features import commercial_license_allows_publish


STAGE_LABELS = {
    "quick": "۱. اطلاعات پایه",
    "commerce": "۲. سفارش، قیمت و گزینه‌ها",
    "images": "۳. تصاویر",
    "content": "۴. محتوا و SEO",
    "specs": "۵. منبع و مجوز",
    "publish": "۶. بررسی و انتشار",
}


def _value(row, key: str, default=""):
    if row is None:
        return default
    try:
        value = row[key]
    except Exception:
        try:
            value = row.get(key, default)
        except Exception:
            return default
    return default if value is None else value


def _json_list(raw) -> list:
    if isinstance(raw, list):
        return raw
    try:
        value = json.loads(raw or "[]")
        return value if isinstance(value, list) else []
    except Exception:
        return []


def _unique_text(values) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for raw in values or []:
        text = str(raw or "").strip()
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def selected_material_names(row) -> list[str]:
    direct = _unique_text(_json_list(_value(row, "material_options_json", "[]")))
    if direct:
        return direct
    legacy = _json_list(_value(row, "material_color_options_json", "[]"))
    names = [item.get("material") for item in legacy if isinstance(item, dict)]
    return _unique_text(names or _json_list(_value(row, "materials_json", "[]")))


def selected_color_names(row) -> list[str]:
    direct = []
    for item in _json_list(_value(row, "color_options_json", "[]")):
        if isinstance(item, dict):
            direct.append(item.get("name") or item.get("color"))
        else:
            direct.append(item)
    direct = _unique_text(direct)
    if direct:
        return direct
    legacy = _json_list(_value(row, "material_color_options_json", "[]"))
    names = [item.get("color") for item in legacy if isinstance(item, dict)]
    return _unique_text(names or _json_list(_value(row, "colors_json", "[]")))


def build_sales_keywords(row, materials: list[str] | None = None, colors: list[str] | None = None) -> list[str]:
    title = str(_value(row, "title_fa", "") or "").strip()
    if not title:
        return []
    materials = materials if materials is not None else selected_material_names(row)
    colors = colors if colors is not None else selected_color_names(row)
    suggestions = [f"خرید {title}", f"سفارش {title}", f"قیمت {title}"]
    suggestions.extend(f"{title} {name}" for name in materials[:4])
    suggestions.extend(f"{title} {name}" for name in colors[:4])
    return _unique_text(suggestions)[:12]


def evaluate_readiness(row) -> dict:
    if row is None:
        return {"stages": {}, "production_ready": False, "missing": ["رکورد محصول پیدا نشد"]}

    title = str(_value(row, "title_fa", "") or "").strip()
    short_desc = str(_value(row, "short_description_fa", "") or "").strip()
    description = str(_value(row, "description_fa", "") or "").strip()
    category = str(_value(row, "local_category_slug", "") or "").strip()
    product_type = str(_value(row, "product_type", "ready_product") or "ready_product")
    source_url = str(_value(row, "source_url", "") or "").strip()

    selected_images = _json_list(_value(row, "selected_images_json", "[]"))
    primary_image = str(_value(row, "primary_image_url", "") or "").strip()
    materials = selected_material_names(row)
    colors = selected_color_names(row)

    price_values = []
    for key in ("final_price", "price_min", "price_max", "suggested_price"):
        try:
            price_values.append(float(str(_value(row, key, 0) or 0).replace(",", "")))
        except Exception:
            price_values.append(0)
    has_price = max(price_values or [0]) > 0 or product_type in {"portfolio", "custom_order"}

    seo_title = str(_value(row, "seo_title_fa", "") or "").strip()
    seo_description = str(_value(row, "seo_description_fa", "") or "").strip()
    keywords = _unique_text(_json_list(_value(row, "keywords_json", "[]")))
    alts = _unique_text(_json_list(_value(row, "image_alt_texts_json", "[]")))
    seo_manual_approved = bool(int(_value(row, "seo_manual_approved", 0) or 0))
    source_review_manual_approved = bool(int(_value(row, "source_review_manual_approved", 0) or 0))

    slider_enabled = bool(int(_value(row, "homepage_slider_enabled", 0) or 0))
    slider_fields = {
        "عنوان اسلایدر": str(_value(row, "homepage_slider_title_fa", "") or "").strip(),
        "توضیح اسلایدر": str(_value(row, "homepage_slider_description_fa", "") or "").strip(),
        "Alt اسلایدر": str(_value(row, "homepage_slider_alt_text", "") or "").strip(),
        "عبارت هدف اسلایدر": str(_value(row, "homepage_slider_focus_keyword", "") or "").strip(),
        "عکس اسلایدر": str(_value(row, "homepage_slider_image_url", "") or "").strip(),
    }

    approved = bool(int(_value(row, "approved_for_sale", 0) or 0))
    publish_product = bool(int(_value(row, "publish_as_product", 0) or 0)) or product_type == "portfolio"
    license_ok = commercial_license_allows_publish(str(_value(row, "commercial_status", "review") or "review"))

    stage_checks = {
        "quick": [
            ("عنوان فارسی", bool(title)),
            ("گروه سایت", bool(category and category != "external-other")),
            ("نوع محصول", bool(product_type)),
        ],
        "commerce": [
            ("قیمت یا حالت سفارش", has_price),
            ("حداقل یک متریال", bool(materials)),
            ("حداقل یک رنگ", bool(colors)),
        ],
        "images": [
            ("تصویر اصلی", bool(primary_image)),
            ("حداقل یک تصویر انتخاب‌شده", bool(selected_images)),
        ],
        "content": [
            ("عنوان فارسی", bool(title)),
            ("توضیح فارسی", bool(short_desc or description)),
            ("SEO Title فارسی", bool(seo_title) or seo_manual_approved),
            ("SEO Description فارسی", bool(seo_description) or seo_manual_approved),
            ("عبارت‌های هدف SEO", len(keywords) >= 3 or seo_manual_approved),
            ("Alt تصویر", bool(alts) or seo_manual_approved),
        ],
        "specs": [
            ("لینک منبع", bool(source_url)),
            ("مجوز تجاری مجاز", license_ok),
        ],
        "publish": [
            ("تأیید برای فروش", approved or product_type == "portfolio"),
            ("نوع انتشار محصول", publish_product),
        ],
    }
    if slider_enabled:
        stage_checks["publish"].extend((label, bool(value)) for label, value in slider_fields.items())

    stages = {}
    missing_all: list[str] = []
    for key, checks in stage_checks.items():
        missing = [label for label, ok in checks if not ok]
        stages[key] = {
            "label": STAGE_LABELS[key],
            "ready": not missing,
            "missing": missing,
        }
        missing_all.extend(f"{STAGE_LABELS[key]}: {item}" for item in missing)

    return {
        "stages": stages,
        "production_ready": all(item["ready"] for item in stages.values()),
        "missing": missing_all,
        "materials": materials,
        "colors": colors,
        "keywords": keywords,
        "slider_enabled": slider_enabled,
        "seo_manual_approved": seo_manual_approved,
        "source_review_manual_approved": source_review_manual_approved,
        "license_ok": license_ok,
    }


def _walk(widget):
    yield widget
    try:
        children = widget.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield from _walk(child)


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_readiness_ai_installed", False):
        return
    original_apply = app_class._apply_ai_pack

    def _apply_ai_pack(self, product_id, pack, open_studio=True):
        result = original_apply(self, product_id, pack, open_studio=open_studio)
        row = self.db.product(product_id)
        if row is None:
            return result
        materials = selected_material_names(row)
        colors = selected_color_names(row)
        ai_keywords = _unique_text(pack.get("target_keywords_fa") or []) if isinstance(pack, dict) else []
        current_keywords = _unique_text(_json_list(_value(row, "keywords_json", "[]")))
        keywords = ai_keywords or current_keywords or build_sales_keywords(row, materials, colors)
        updates = {
            "materials_json": json.dumps(materials, ensure_ascii=False),
            "colors_json": json.dumps(colors, ensure_ascii=False),
            "keywords_json": json.dumps(keywords[:12], ensure_ascii=False),
        }
        self.db.update_product(product_id, updates)
        return result

    app_class._apply_ai_pack = _apply_ai_pack
    app_class._phase49_readiness_ai_installed = True


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_readiness_wizard_installed", False):
        return

    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_save = workspace_class.save
    original_refresh_checklists = workspace_class.refresh_checklists
    original_source_for_ai = workspace_class._source_for_ai
    original_production = workspace_class.publish_to_production_site

    def __init__(self, app, product_id: int):
        original_init(self, app, product_id)
        self._phase49_build_readiness_rail()
        self._phase49_sync_reference_lists(update_widgets=True)
        self._phase49_refresh_readiness()

    def _phase49_build_readiness_rail(self):
        buttons = getattr(self, "_section_buttons", {})
        if not buttons:
            return
        rail = next(iter(buttons.values())).master
        ttk.Separator(rail, orient="horizontal").pack(fill="x", pady=(12, 8))
        self._phase49_readiness_summary = self._tk_string("در حال بررسی…")
        self._phase49_readiness_missing = self._tk_string("")
        ttk.Label(rail, text="آمادگی انتشار", style="SubHeader.TLabel").pack(anchor="e")
        ttk.Label(
            rail,
            textvariable=self._phase49_readiness_summary,
            justify="right",
            wraplength=185,
        ).pack(fill="x", pady=(4, 2))
        ttk.Label(
            rail,
            textvariable=self._phase49_readiness_missing,
            justify="right",
            wraplength=185,
            style="SubHeader.TLabel",
        ).pack(fill="x", pady=(0, 7))
        self._phase49_next_button = ttk.Button(
            rail,
            text="مرحله بعد",
            command=self._phase49_go_next,
            style="Primary.TButton",
        )
        self._phase49_next_button.pack(fill="x", pady=2)
        ttk.Button(
            rail,
            text="✨ پیشنهاد AI برای موارد ناقص",
            command=self._phase49_complete_missing,
            style="Primary.TButton",
        ).pack(fill="x", pady=2)
        self._phase49_local_button = ttk.Button(
            rail,
            text=LOCAL_BUTTON_TEXT,
            command=self.publish_to_local_computer,
            style="Primary.TButton",
        )
        self._phase49_local_button.pack(fill="x", pady=(8, 2))
        self._phase49_site_button = ttk.Button(
            rail,
            text=SITE_BUTTON_TEXT,
            command=self.publish_to_production_site,
            style="Publish.TButton",
        )
        self._phase49_site_button.pack(fill="x", pady=2)

    def _tk_string(self, value=""):
        import tkinter as tk
        return tk.StringVar(value=value)

    def _phase49_sync_reference_lists(self, update_widgets=False):
        row = self.db.product(self.product_id)
        if row is None:
            return
        materials = selected_material_names(row)
        colors = selected_color_names(row)
        keywords = _unique_text(_json_list(_value(row, "keywords_json", "[]")))
        if not keywords:
            keywords = build_sales_keywords(row, materials, colors)
        updates = {}
        if materials and _unique_text(_json_list(_value(row, "materials_json", "[]"))) != materials:
            updates["materials_json"] = json.dumps(materials, ensure_ascii=False)
        if colors and _unique_text(_json_list(_value(row, "colors_json", "[]"))) != colors:
            updates["colors_json"] = json.dumps(colors, ensure_ascii=False)
        if keywords and _unique_text(_json_list(_value(row, "keywords_json", "[]"))) != keywords:
            updates["keywords_json"] = json.dumps(keywords[:12], ensure_ascii=False)
        if updates:
            self.db.update_product(self.product_id, updates)
            row = self.db.product(self.product_id)
        if update_widgets:
            mapping = (
                ("content_materials", materials),
                ("content_colors", colors),
                ("content_keywords", keywords[:12]),
            )
            for attr, values in mapping:
                widget = getattr(self, attr, None)
                if widget is not None:
                    try:
                        self._text_set(widget, "\n".join(values))
                    except Exception:
                        pass

    def _phase49_refresh_readiness(self):
        if not hasattr(self, "_phase49_readiness_summary"):
            return
        self._phase49_sync_reference_lists(update_widgets=False)
        row = self.db.product(self.product_id)
        state = evaluate_readiness(row)
        self._phase49_readiness_state = state
        buttons = getattr(self, "_section_buttons", {})
        for key, button in buttons.items():
            stage = state["stages"].get(key, {"ready": False, "label": STAGE_LABELS.get(key, key)})
            icon = "✅" if stage["ready"] else "❌"
            try:
                button.configure(text=f"{icon} {stage['label']}")
            except Exception:
                pass
        if state["production_ready"]:
            self._phase49_readiness_summary.set("✅ محصول آماده انتشار روی سایت اصلی است")
            self._phase49_readiness_missing.set("همه Gateهای اجباری سبز هستند.")
        else:
            count = len(state["missing"])
            first = state["missing"][:3]
            self._phase49_readiness_summary.set(f"❌ آماده Production نیست • {count} مورد ناقص")
            self._phase49_readiness_missing.set("\n".join(first) + ("\n…" if count > 3 else ""))
        first_incomplete = next((key for key, stage in state["stages"].items() if not stage["ready"]), None)
        if first_incomplete:
            self._phase49_next_button.configure(text=f"مرحله بعد: {STAGE_LABELS[first_incomplete]}")
        else:
            self._phase49_next_button.configure(text="✅ همه مراحل کامل — بررسی انتشار")
        if state["production_ready"]:
            self._phase49_site_button.state(["!disabled"])
        else:
            self._phase49_site_button.state(["disabled"])
        for widget in _walk(self):
            try:
                if str(widget.cget("text") or "") == SITE_BUTTON_TEXT and widget is not self._phase49_site_button:
                    widget.state(["!disabled"] if state["production_ready"] else ["disabled"])
            except Exception:
                pass

    def _phase49_go_next(self):
        state = getattr(self, "_phase49_readiness_state", None) or evaluate_readiness(self.db.product(self.product_id))
        target = next((key for key, stage in state["stages"].items() if not stage["ready"]), "publish")
        self.select_section(target)

    def _phase49_complete_missing(self):
        # AI completion must never persist the whole Product Workspace. The
        # operator may have unrelated commerce/profile edits in memory.
        self._phase49_sync_reference_lists(update_widgets=False)
        state = evaluate_readiness(self.db.product(self.product_id))
        content_missing = not state["stages"].get("content", {}).get("ready", False)
        if content_missing:
            self.select_section("content")
            messagebox.showinfo(
                "3DPrintHub — تکمیل هوشمند",
                "متریال و رنگ از انتخاب‌های واقعی محصول همگام شدند و عبارت‌های هدف اولیه ساخته شدند.\n\n"
                "حالا AI برای محتوای فارسی و SEO پیشنهاد می‌دهد؛ قبل از اعمال می‌توانی خروجی را بررسی کنی.",
                parent=self,
            )
            self.generate_ai("commerce")
        else:
            messagebox.showinfo(
                "3DPrintHub — تکمیل هوشمند",
                "لیست متریال، رنگ و عبارت‌های هدف SEO با داده واقعی محصول همگام شدند. بخش محتوای اصلی در حال حاضر کامل است.",
                parent=self,
            )
        self._phase49_refresh_readiness()

    def _source_for_ai(self):
        source = dict(original_source_for_ai(self) or {})
        row = self.db.product(self.product_id)
        source["selected_materials"] = selected_material_names(row)
        source["selected_colors"] = selected_color_names(row)
        return source

    def reload(self):
        original_reload(self)
        self._phase49_sync_reference_lists(update_widgets=True)
        self._phase49_refresh_readiness()

    def save(self, silent=False):
        ok = original_save(self, silent=True)
        if not ok:
            return False
        self._phase49_sync_reference_lists(update_widgets=True)
        self._phase49_refresh_readiness()
        if not silent:
            self.footer_status.set("ذخیره شد • وضعیت آمادگی انتشار بروزرسانی شد")
        return True

    def refresh_checklists(self):
        original_refresh_checklists(self)
        self._phase49_refresh_readiness()

    def publish_to_production_site(self):
        try:
            self.save(silent=True)
        except Exception:
            pass
        state = evaluate_readiness(self.db.product(self.product_id))
        if not state["production_ready"]:
            first = next((key for key, stage in state["stages"].items() if not stage["ready"]), "publish")
            self.select_section(first)
            messagebox.showwarning(
                "3DPrintHub — محصول آماده Production نیست",
                "برای انتشار روی سایت اصلی ابتدا این موارد را تکمیل کن:\n\n- " + "\n- ".join(state["missing"][:12]),
                parent=self,
            )
            self._phase49_refresh_readiness()
            return
        return original_production(self)

    workspace_class.__init__ = __init__
    workspace_class._phase49_build_readiness_rail = _phase49_build_readiness_rail
    workspace_class._tk_string = _tk_string
    workspace_class._phase49_sync_reference_lists = _phase49_sync_reference_lists
    workspace_class._phase49_refresh_readiness = _phase49_refresh_readiness
    workspace_class._phase49_go_next = _phase49_go_next
    workspace_class._phase49_complete_missing = _phase49_complete_missing
    workspace_class._source_for_ai = _source_for_ai
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class.refresh_checklists = refresh_checklists
    workspace_class.publish_to_production_site = publish_to_production_site
    workspace_class.publish_now = publish_to_production_site
    workspace_class._phase49_readiness_wizard_installed = True
