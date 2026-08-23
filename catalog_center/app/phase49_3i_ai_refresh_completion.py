from __future__ import annotations

import json
import time
import tkinter as tk
from tkinter import messagebox, ttk

from . import phase49_3f_runtime_trace as runtime_trace
from .epic49_desktop_schema import (
    list_available_material_colors,
    normalize_color_options,
    normalize_material_color_options,
    normalize_material_options,
)
from .phase49_3h_image_limits import normalize_image_limit
from .v8_features import commercial_license_allows_publish


DEFAULT_PRICE_TOMAN = 500_000
SOURCE_REFRESH_TIMEOUT_SECONDS = 90
GENERIC_TITLES = {
    "محصول چاپ سه بعدی",
    "محصول چاپ سه‌بعدی",
    "مدل چاپ سه بعدی",
    "مدل چاپ سه‌بعدی",
    "فایل چاپ سه بعدی",
    "فایل چاپ سه‌بعدی",
    "محصول سه بعدی",
    "محصول سه‌بعدی",
}

TEXT_FIELDS = {
    "title_fa": ("title_fa", "persian_content"),
    "short_description_fa": ("short_description_fa", "persian_content"),
    "description_fa": ("description_fa", "persian_content"),
    "use_description": ("use_description_fa", "persian_content"),
    "seo_title_fa": ("seo_title_fa", "product_seo"),
    "seo_description_fa": ("seo_description_fa", "product_seo"),
    "social_caption_fa": ("social_caption_fa", "product_seo"),
}

LIST_FIELDS = {
    "categories_fa_json": ("categories_fa", "persian_content"),
    "specs_fa_json": ("specs_fa", "persian_content"),
    "sales_bullets_json": ("sales_bullets", "persian_content"),
    "material_recommendations_json": ("material_recommendations", "materials"),
    "keywords_json": ("target_keywords_fa", "product_seo"),
    "tags_fa_json": ("tags_fa", "product_seo"),
    "hashtags_fa_json": ("hashtags_fa", "product_seo"),
    "image_alt_texts_json": ("image_alt_texts", "image_seo"),
}

SLIDER_FIELDS = {
    "homepage_slider_title_fa": "title_fa",
    "homepage_slider_description_fa": "description_fa",
    "homepage_slider_alt_text": "image_alt_fa",
    "homepage_slider_button_text": "button_text_fa",
    "homepage_slider_focus_keyword": "focus_keyword_fa",
}


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return row[key]
    except Exception:
        return default


def _json_value(value, default):
    if isinstance(value, type(default)):
        return value
    try:
        parsed = json.loads(value or json.dumps(default))
    except Exception:
        return default
    return parsed if isinstance(parsed, type(default)) else default


def _normal_text(value) -> str:
    return " ".join(str(value or "").replace("ي", "ی").replace("ك", "ک").split()).strip().casefold()


def _is_generic_title(value) -> bool:
    return _normal_text(value) in {_normal_text(item) for item in GENERIC_TITLES}


def _provenance(row) -> dict:
    return _json_value(_row_value(row, "ai_provenance_json", "{}"), {})


def _previous_pack(row) -> dict:
    return _json_value(_row_value(row, "content_pack_json", "{}"), {})


def _same_scalar(left, right) -> bool:
    return _normal_text(left) == _normal_text(right) and bool(_normal_text(left))


def _same_list(left, right) -> bool:
    left_value = _json_value(left, []) if isinstance(left, str) else list(left or [])
    right_value = list(right or []) if isinstance(right, list) else []
    return left_value == right_value and bool(left_value)


def _field_is_ai_owned(row, db_key: str, pack_key: str, group: str, *, list_field: bool = False) -> bool:
    current = _row_value(row, db_key, "")
    if list_field:
        if not _json_value(current, []):
            return True
    else:
        if not str(current or "").strip():
            return True
        if db_key == "title_fa" and _is_generic_title(current):
            return True

    record = _provenance(row).get(group)
    if isinstance(record, dict):
        fields = {str(item) for item in (record.get("fields") or [])}
        if (
            str(record.get("source") or "") == "ai"
            and not bool(record.get("manual_override"))
            and db_key in fields
        ):
            return True

    previous = _previous_pack(row)
    previous_value = previous.get(pack_key)
    if list_field:
        return _same_list(current, previous_value)
    return _same_scalar(current, previous_value)


def build_refresh_updates(row, pack: dict, *, scope: str, base_updates: dict | None = None) -> dict:
    """Refresh AI-owned/editorial values while preserving real manual overrides.

    The old task center intentionally filled only blanks. The all-fields operator
    action is different: a new Provider/Model selection must be able to regenerate
    earlier AI output. Values proven manual remain untouched.
    """
    updates = dict(base_updates or {})
    if str(scope or "all") == "images":
        return updates

    for db_key, (pack_key, group) in TEXT_FIELDS.items():
        value = str(pack.get(pack_key) or "").strip()
        if not value:
            continue
        if _field_is_ai_owned(row, db_key, pack_key, group):
            updates[db_key] = value

    for db_key, (pack_key, group) in LIST_FIELDS.items():
        value = pack.get(pack_key)
        if not isinstance(value, list) or not value:
            continue
        if _field_is_ai_owned(row, db_key, pack_key, group, list_field=True):
            updates[db_key] = json.dumps(value, ensure_ascii=False)

    slider = pack.get("homepage_slider_seo") if isinstance(pack.get("homepage_slider_seo"), dict) else {}
    if bool(int(_row_value(row, "homepage_slider_enabled", 0) or 0)):
        for db_key, pack_key in SLIDER_FIELDS.items():
            value = str(slider.get(pack_key) or "").strip()
            if not value:
                continue
            current = str(_row_value(row, db_key, "") or "").strip()
            previous_slider = _previous_pack(row).get("homepage_slider_seo")
            previous_slider = previous_slider if isinstance(previous_slider, dict) else {}
            if not current or _same_scalar(current, previous_slider.get(pack_key)):
                updates[db_key] = value

    # The latest pack is always the provenance anchor for the next refresh.
    updates["content_pack_json"] = json.dumps(pack, ensure_ascii=False)
    return updates


def _source_site_name(db, row) -> str:
    code = str(_row_value(row, "source_code", "") or "").strip()
    if not code:
        return ""
    try:
        source = db.source(code)
    except Exception:
        source = None
    if source is not None:
        try:
            name = str(source["name"] or "").strip()
        except Exception:
            name = ""
        if name:
            return name
    return code.replace("-", " ").title()


def _available_pair_for_pack(db, pack: dict) -> dict | None:
    inventory = list_available_material_colors(db)
    if not inventory:
        return None
    recommendations = []
    for item in pack.get("material_recommendations") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("material") or "").strip().casefold()
        if name:
            recommendations.append(name)
    for wanted in recommendations:
        for item in inventory:
            material = str(item.get("material_name") or "").strip()
            if material.casefold() == wanted or wanted in material.casefold() or material.casefold() in wanted:
                return item
    return inventory[0]


def build_completion_defaults(db, app, row, pack: dict) -> dict:
    """Build factual/local defaults needed by readiness without inventing source facts."""
    updates: dict = {}

    source_name = _source_site_name(db, row)
    if source_name and str(_row_value(row, "source_name", "") or "").strip() != source_name:
        updates["source_name"] = source_name

    current_category = str(_row_value(row, "local_category_slug", "") or "").strip()
    suggested = str(pack.get("suggested_category_slug") or "").strip()
    confidence = float(pack.get("category_confidence") or 0)
    category_map = getattr(app, "category_slug_to_label", {}) or {}
    previous_suggested = str(_previous_pack(row).get("suggested_category_slug") or "").strip()
    category_ai_owned = not current_category or current_category == "external-other" or (
        previous_suggested and current_category == previous_suggested
    )
    if category_ai_owned and suggested and suggested in category_map and confidence >= 0.55:
        updates["local_category_slug"] = suggested
        updates["ai_suggested_category_slug"] = suggested
        updates["ai_confidence"] = confidence

    images = [str(item or "").strip() for item in _json_value(_row_value(row, "images_json", "[]"), []) if str(item or "").strip()]
    selected = [str(item or "").strip() for item in _json_value(_row_value(row, "selected_images_json", "[]"), []) if str(item or "").strip()]
    desired = normalize_image_limit(_row_value(row, "download_image_limit", 10))
    if images and not selected:
        selected = images[:desired]
        updates["selected_images_json"] = json.dumps(selected, ensure_ascii=False)
    primary = str(_row_value(row, "primary_image_url", "") or "").strip()
    if not primary and (selected or images):
        updates["primary_image_url"] = (selected or images)[0]

    suggested_price = int(float(_row_value(row, "suggested_price", 0) or 0))
    if suggested_price <= 0:
        suggested_price = DEFAULT_PRICE_TOMAN
        updates["suggested_price"] = suggested_price
    try:
        price_min = int(float(_row_value(row, "price_min", 0) or 0))
    except Exception:
        price_min = 0
    try:
        price_max = int(float(_row_value(row, "price_max", 0) or 0))
    except Exception:
        price_max = 0
    if price_min <= 0:
        updates["price_min"] = suggested_price
    if price_max <= 0:
        updates["price_max"] = suggested_price

    materials = normalize_material_options(_row_value(row, "material_options_json", "[]"))
    colors = normalize_color_options(_row_value(row, "color_options_json", "[]"))
    if not materials or not colors:
        pair = _available_pair_for_pack(db, pack)
        if pair:
            material = str(pair.get("material_name") or "").strip()
            color = {
                "name": str(pair.get("color_name") or "").strip(),
                "hex": str(pair.get("hex_code") or "").strip(),
                "color_type": str(pair.get("color_type") or "solid").strip(),
                "secondary_hex": str(pair.get("secondary_hex") or "").strip(),
                "tertiary_hex": str(pair.get("tertiary_hex") or "").strip(),
            }
            legacy = normalize_material_color_options([{
                "material": material,
                "color": color["name"],
                "hex": color["hex"],
                "color_type": color["color_type"],
                "secondary_hex": color["secondary_hex"],
                "tertiary_hex": color["tertiary_hex"],
            }])
            if not materials and material:
                updates["material_options_json"] = json.dumps([material], ensure_ascii=False)
                updates["materials_json"] = json.dumps([material], ensure_ascii=False)
            if not colors and color["name"]:
                updates["color_options_json"] = json.dumps([color], ensure_ascii=False)
                updates["colors_json"] = json.dumps([color["name"]], ensure_ascii=False)
            if legacy:
                updates["material_color_options_json"] = json.dumps(legacy, ensure_ascii=False)

    product_type = str(_row_value(row, "product_type", "") or "").strip() or "ready_product"
    if not str(_row_value(row, "product_type", "") or "").strip():
        updates["product_type"] = product_type
    if product_type != "portfolio" and not bool(int(_row_value(row, "publish_as_product", 0) or 0)):
        updates["publish_as_product"] = 1
        updates["publish_as_portfolio"] = 0

    return updates


def install(workspace_class, task_center_module) -> None:
    if getattr(workspace_class, "_phase49_3i9_ai_refresh_completion_installed", False):
        return

    original_build_updates = task_center_module.build_ai_updates
    original_all_ai = getattr(workspace_class, "_phase49_3c_all_ai", None)
    original_apply_result = getattr(workspace_class, "_phase49_3e_apply_ai_result", None)

    def build_ai_updates(row, pack: dict, *, scope: str = "all"):
        base = original_build_updates(row, pack, scope=scope)
        return build_refresh_updates(row, pack, scope=scope, base_updates=base)

    task_center_module.build_ai_updates = build_ai_updates

    def _phase49_3i9_close_image_refresh(self):
        win = getattr(self, "_phase49_3i9_image_refresh_win", None)
        bar = getattr(self, "_phase49_3i9_image_refresh_bar", None)
        if bar is not None:
            try:
                bar.stop()
            except Exception:
                pass
        try:
            if win is not None and win.winfo_exists():
                win.destroy()
        except Exception:
            pass
        self._phase49_3i9_image_refresh_win = None
        self._phase49_3i9_image_refresh_bar = None

    def _phase49_3i9_show_image_refresh(self, current: int, target: int):
        self._phase49_3i9_close_image_refresh()
        win = tk.Toplevel(self)
        win.title("3DPrintHub - تکمیل تصاویر منبع")
        win.geometry("570x210")
        win.resizable(False, False)
        win.transient(self)
        win.protocol("WM_DELETE_WINDOW", lambda: None)
        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="بازیابی تصاویر قبل از تکمیل هوشمند", font=("Tahoma", 12, "bold")).pack(anchor="w")
        ttk.Label(
            body,
            text=f"محصول اکنون {current} تصویر دارد. در حال بازیابی از لینک مرجع تا سقف {target} تصویر...",
            wraplength=520,
        ).pack(anchor="w", pady=(12, 8))
        bar = ttk.Progressbar(body, mode="indeterminate")
        bar.pack(fill="x", pady=8)
        bar.start(12)
        ttk.Label(
            body,
            text="پس از پایان بازیابی منبع، همان درخواست تکمیل هوشمند به Provider/Model فعال ارسال می‌شود.",
            style="SubHeader.TLabel",
            wraplength=520,
        ).pack(anchor="w")
        self._phase49_3i9_image_refresh_win = win
        self._phase49_3i9_image_refresh_bar = bar
        try:
            win.update_idletasks()
            win.lift()
        except Exception:
            pass

    def _phase49_3i9_continue_all_ai(self):
        self._phase49_3i9_preflight_busy = False
        return original_all_ai(self) if callable(original_all_ai) else None

    def _phase49_3i9_offer_image_refresh(self):
        if getattr(self, "_phase49_3i9_preflight_busy", False):
            try:
                self.footer_status.set("پیش‌بررسی تصاویر/منبع در حال اجرا است.")
            except Exception:
                pass
            return None

        try:
            self.save(silent=True)
        except Exception:
            pass
        row = self.db.product(self.product_id)
        if row is None:
            return _phase49_3i9_continue_all_ai(self)

        source_name = _source_site_name(self.db, row)
        if source_name and str(_row_value(row, "source_name", "") or "").strip() != source_name:
            self.db.update_product(self.product_id, {"source_name": source_name})
            row = self.db.product(self.product_id)

        images = [str(item or "").strip() for item in _json_value(_row_value(row, "images_json", "[]"), []) if str(item or "").strip()]
        try:
            widget_limit = self.product_image_limit_var.get() if hasattr(self, "product_image_limit_var") else _row_value(row, "download_image_limit", 10)
        except Exception:
            widget_limit = _row_value(row, "download_image_limit", 10)
        desired = normalize_image_limit(widget_limit)
        source_url = str(_row_value(row, "source_url", "") or "").strip()
        can_refetch = bool(source_url.startswith(("http://", "https://")) and hasattr(self, "refetch"))

        if len(images) >= desired or not can_refetch:
            return _phase49_3i9_continue_all_ai(self)

        if not messagebox.askyesno(
            "3DPrintHub - تصاویر محصول کم است",
            f"این محصول {len(images)} تصویر دارد و سقف انتخابی شما {desired} است.\n\n"
            f"قبل از اجرای هوش مصنوعی، از لینک مرجع تلاش شود تصاویر بیشتری تا سقف {desired} دریافت شود؟",
            parent=self,
        ):
            return _phase49_3i9_continue_all_ai(self)

        self._phase49_3i9_preflight_busy = True
        previous_marker = str(_row_value(row, "last_refetched_at", "") or "")
        previous_count = len(images)
        started = time.monotonic()
        try:
            if hasattr(self, "product_image_limit_var"):
                self.product_image_limit_var.set(str(desired))
            self._phase49_3i9_show_image_refresh(previous_count, desired)
            runtime_trace.event(
                "source",
                "phase49-3i9-image-preflight-start",
                product_id=self.product_id,
                detail={"current": previous_count, "target": desired, "source_url": source_url},
            )
            self.refetch()
        except Exception as exc:
            self._phase49_3i9_close_image_refresh()
            self._phase49_3i9_preflight_busy = False
            messagebox.showerror("3DPrintHub - بازیابی تصاویر", str(exc), parent=self)
            return None

        def poll():
            current = self.db.product(self.product_id)
            marker = str(_row_value(current, "last_refetched_at", "") or "")
            current_images = [str(item or "").strip() for item in _json_value(_row_value(current, "images_json", "[]"), []) if str(item or "").strip()]
            if marker != previous_marker or len(current_images) > previous_count:
                elapsed_ms = int((time.monotonic() - started) * 1000)
                runtime_trace.event(
                    "source",
                    "phase49-3i9-image-preflight-complete",
                    product_id=self.product_id,
                    elapsed_ms=elapsed_ms,
                    detail={"before": previous_count, "after": len(current_images), "target": desired},
                )
                self._phase49_3i9_close_image_refresh()
                try:
                    self.reload()
                except Exception:
                    pass
                return _phase49_3i9_continue_all_ai(self)

            if time.monotonic() - started >= SOURCE_REFRESH_TIMEOUT_SECONDS:
                self._phase49_3i9_close_image_refresh()
                self._phase49_3i9_preflight_busy = False
                runtime_trace.event(
                    "source",
                    "phase49-3i9-image-preflight-timeout",
                    status="error",
                    product_id=self.product_id,
                    detail={"before": previous_count, "target": desired},
                )
                if messagebox.askyesno(
                    "3DPrintHub - بازیابی تصاویر کامل نشد",
                    "بازیابی منبع تا ۹۰ ثانیه کامل نشد.\n\nهوش مصنوعی با تصاویر فعلی ادامه دهد؟",
                    parent=self,
                ):
                    return _phase49_3i9_continue_all_ai(self)
                return None
            self.after(750, poll)

        self.after(750, poll)
        return None

    def _phase49_3c_all_ai(self):
        return self._phase49_3i9_offer_image_refresh()

    def _phase49_3i9_confirm_operator_gates(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        updates = {}
        source_name = str(_row_value(row, "source_name", "") or _source_site_name(self.db, row) or "منبع").strip()
        license_status = str(_row_value(row, "commercial_status", "review") or "review")
        if not commercial_license_allows_publish(license_status):
            license_name = str(_row_value(row, "license_name", "") or "ثبت نشده").strip()
            approved_license = messagebox.askyesno(
                "تأیید اپراتور - مجوز تجاری",
                f"برای سبز شدن Gate مجوز، خودت باید حق فروش تجاری را تأیید کنی.\n\n"
                f"ناشر/منبع: {source_name}\nمجوز استخراج‌شده: {license_name}\n\n"
                "آیا مجوز/حق استفاده این محصول را بررسی کرده‌ای و فروش تجاری آن را تأیید می‌کنی؟\n"
                "این تأیید فقط در Catalog محلی ثبت می‌شود و چیزی را روی Production منتشر نمی‌کند.",
                parent=self,
            )
            if approved_license:
                updates["commercial_status"] = "allowed"

        product_type = str(_row_value(row, "product_type", "ready_product") or "ready_product")
        approved = bool(int(_row_value(row, "approved_for_sale", 0) or 0))
        if product_type != "portfolio" and not approved:
            if messagebox.askyesno(
                "تأیید اپراتور - آماده فروش",
                "تمام داده‌های قابل تکمیل آماده شده‌اند. این محصول در Catalog محلی برای فروش تأیید شود؟\n\n"
                "این کار فقط تیک آماده‌سازی/صف محلی را کامل می‌کند و انتشار Production انجام نمی‌دهد.",
                parent=self,
            ):
                updates.update({
                    "approved_for_sale": 1,
                    "publish_as_product": 1,
                    "publish_as_portfolio": 0,
                })

        if updates:
            self.db.update_product(self.product_id, updates)
            try:
                self.reload()
            except Exception:
                pass
            try:
                self._phase49_3c_refresh_live()
            except Exception:
                pass
            try:
                self._phase49_3e_refresh_tasks()
            except Exception:
                pass

    def _phase49_3e_apply_ai_result(self, pack: dict, scope: str):
        if str(scope or "all") != "images":
            row = self.db.product(self.product_id)
            if row is not None:
                defaults = build_completion_defaults(self.db, self.app, row, pack)
                if defaults:
                    self.db.update_product(self.product_id, defaults)
        result = original_apply_result(self, pack, scope) if callable(original_apply_result) else None
        if str(scope or "all") != "images":
            try:
                self.after(120, self._phase49_3i9_confirm_operator_gates)
            except Exception:
                pass
        return result

    workspace_class._phase49_3i9_close_image_refresh = _phase49_3i9_close_image_refresh
    workspace_class._phase49_3i9_show_image_refresh = _phase49_3i9_show_image_refresh
    workspace_class._phase49_3i9_continue_all_ai = _phase49_3i9_continue_all_ai
    workspace_class._phase49_3i9_offer_image_refresh = _phase49_3i9_offer_image_refresh
    workspace_class._phase49_3i9_confirm_operator_gates = _phase49_3i9_confirm_operator_gates
    workspace_class._phase49_3c_all_ai = _phase49_3c_all_ai
    if callable(original_apply_result):
        workspace_class._phase49_3e_apply_ai_result = _phase49_3e_apply_ai_result
    workspace_class._phase49_3i9_ai_refresh_completion_installed = True
