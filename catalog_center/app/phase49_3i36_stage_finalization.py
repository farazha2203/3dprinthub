from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import tkinter as tk
from tkinter import messagebox, ttk

from .db import normalize_url
from .phase49_diagnostics import audit_event
from . import secure_secrets


PHASE = "49.3I.36"
LOCK_COLUMN = "operator_stage_locks_json"
STAGE_ORDER = ("quick", "commerce", "images", "content", "specs", "slider", "publish")
STAGE_LABELS = {
    "quick": "۱. اطلاعات پایه",
    "commerce": "۲. سفارش، قیمت و گزینه‌ها",
    "images": "۳. تصاویر",
    "content": "۴. محتوا و SEO",
    "specs": "۵. منبع و مجوز",
    "slider": "۶. اسلایدر صفحه اصلی",
    "publish": "۷. بررسی و انتشار",
}

QUICK_FIELDS = {
    "title_fa", "local_category_slug", "product_type", "dimensions", "use_case_class",
}
COMMERCE_FIELDS = {
    "material_price_per_gram", "suggested_price", "final_price", "price_is_final",
    "price_min", "price_max", "pricing_strategy", "support_cost_multiplier",
    "assembly_fee", "materials_json", "colors_json", "material_options_json",
    "color_options_json", "material_color_options_json", "availability_status",
    "stock_quantity", "lead_time_min_days", "lead_time_max_days", "has_3d_file",
    "fixed_price_material_name", "fixed_price_color_name",
}
IMAGE_FIELDS = {
    "images_json", "selected_images_json", "primary_image_url", "image_alt_texts_json",
    "image_metadata_json", "download_image_limit",
}
CONTENT_FIELDS = {
    "short_description_fa", "description_fa", "use_description", "categories_fa_json",
    "tags_fa_json", "hashtags_fa_json", "keywords_json", "seo_title_fa",
    "seo_description_fa", "sales_bullets_json", "social_caption_fa",
    "content_pack_json", "content_status", "translation_status", "seo_manual_approved",
}
SPECS_FIELDS = {
    "source_url", "normalized_url", "fingerprint", "source_title",
    "source_short_description", "source_description", "source_specs_json",
    "source_categories_json", "source_category", "source_name", "author_name",
    "license_name", "license_url", "commercial_status", "reference_only",
    "specs_fa_json", "technical_features_json", "technical_summary_fa",
    "source_review_manual_approved", "source_page_screenshot_path",
    "estimated_weight_grams", "estimated_print_minutes", "source_print_profiles_json",
    "source_like_count", "source_save_count", "source_download_count",
    "source_print_count", "source_boost_count", "source_rating", "source_rating_count",
}
PUBLISH_FIELDS = {
    # Operator publication choices are finalizable; runtime queue/ACK fields such
    # as upload_ready/workflow_status/server_status must remain writable by publish.
    "approved_for_sale", "publish_as_product", "publish_as_portfolio",
}


def _row_value(row, key, default=""):
    if row is None:
        return default
    try:
        return row[key] if key in row.keys() else default
    except Exception:
        try:
            return row.get(key, default)
        except Exception:
            return default


def _json_dict(value) -> dict:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    if LOCK_COLUMN not in columns:
        db.conn.execute(
            f"ALTER TABLE products ADD COLUMN {LOCK_COLUMN} TEXT NOT NULL DEFAULT '{{}}'"
        )
        db.conn.commit()


def stage_locks(row) -> dict:
    raw = _json_dict(_row_value(row, LOCK_COLUMN, "{}"))
    output = {}
    for stage in STAGE_ORDER:
        value = raw.get(stage)
        if isinstance(value, dict):
            output[stage] = {
                "locked": bool(value.get("locked")),
                "locked_at": str(value.get("locked_at") or ""),
            }
        elif value:
            output[stage] = {"locked": True, "locked_at": ""}
    return output


def is_stage_locked(row, stage: str) -> bool:
    return bool((stage_locks(row).get(str(stage)) or {}).get("locked"))


def field_stage(field: str) -> str:
    key = str(field or "")
    if key == LOCK_COLUMN:
        return ""
    if key.startswith("homepage_slider_"):
        return "slider"
    if key.startswith("sales_profile_") or key.startswith("sales_profiles_"):
        return "commerce"
    if key in QUICK_FIELDS:
        return "quick"
    if key in COMMERCE_FIELDS:
        return "commerce"
    if key in IMAGE_FIELDS:
        return "images"
    if key in CONTENT_FIELDS or key.startswith("seo_"):
        return "content"
    if key in SPECS_FIELDS or key.startswith("source_"):
        return "specs"
    if key in PUBLISH_FIELDS:
        return "publish"
    return ""


def filter_locked_updates(row, values: dict) -> tuple[dict, list[str]]:
    locks = stage_locks(row)
    kept = {}
    blocked = []
    for key, value in dict(values or {}).items():
        stage = field_stage(key)
        if stage and bool((locks.get(stage) or {}).get("locked")):
            blocked.append(key)
            continue
        kept[key] = value
    return kept, sorted(blocked)


def filter_ai_updates(row, values: dict) -> tuple[dict, list[str]]:
    """AI can edit only unlocked editorial/source/image/slider stages.

    Commerce/profile/material/price/stock and publish ownership is always operator-only,
    even before the operator finalizes those stages.
    """
    locks = stage_locks(row)
    kept = {}
    blocked = []
    for key, value in dict(values or {}).items():
        stage = field_stage(key)
        if stage in {"commerce", "publish"}:
            blocked.append(key)
            continue
        if stage and bool((locks.get(stage) or {}).get("locked")):
            blocked.append(key)
            continue
        kept[key] = value
    return kept, sorted(blocked)


def _has_persian(value) -> bool:
    return bool(re.search(r"[\u0600-\u06ff]", str(value or "")))


def content_manual_minimum(row) -> tuple[bool, list[str]]:
    missing = []
    title = str(_row_value(row, "title_fa", "") or "").strip()
    short = str(_row_value(row, "short_description_fa", "") or "").strip()
    long = str(_row_value(row, "description_fa", "") or "").strip()
    seo_title = str(_row_value(row, "seo_title_fa", "") or "").strip()
    seo_desc = str(_row_value(row, "seo_description_fa", "") or "").strip()
    if not title or not _has_persian(title):
        missing.append("عنوان فارسی واقعی")
    if not (short or long) or not _has_persian(short or long):
        missing.append("توضیح فارسی واقعی")
    if not seo_title or not _has_persian(seo_title):
        missing.append("SEO Title فارسی")
    if not seo_desc or not _has_persian(seo_desc):
        missing.append("SEO Description فارسی")
    return not missing, missing


def configure_readiness(readiness_module) -> None:
    if getattr(readiness_module, "_phase49_3i36_stage_finalization", False):
        return
    original = readiness_module.evaluate_readiness
    readiness_module.STAGE_LABELS.clear()
    readiness_module.STAGE_LABELS.update(STAGE_LABELS)

    def evaluate_readiness(row):
        state = original(row)
        stages = state.setdefault("stages", {})
        locks = stage_locks(row)
        ordered = {}
        for stage in STAGE_ORDER:
            current = dict(stages.get(stage) or {
                "label": STAGE_LABELS[stage],
                "ready": False,
                "missing": ["مرحله تعریف نشده"],
            })
            current["label"] = STAGE_LABELS[stage]
            data_ready = bool(current.get("ready"))
            original_missing = list(current.get("missing") or [])
            locked = bool((locks.get(stage) or {}).get("locked"))

            # Content may be manually finalized when the actual core Persian + SEO
            # fields are present even if a legacy detector still complains about
            # keyword/hashtag/Alt-derived heuristics. Legal/source gates are never bypassed.
            if stage == "content" and locked:
                manual_ok, manual_missing = content_manual_minimum(row)
                if manual_ok:
                    data_ready = True
                    original_missing = []
                elif manual_missing:
                    original_missing = manual_missing

            current["data_ready"] = data_ready
            current["finalized"] = locked
            current["locked"] = locked
            current["missing_data"] = list(original_missing)

            if not locked:
                current["ready"] = False
                current["missing"] = [
                    *original_missing,
                    "تأیید نهایی اپراتور (ثبت مرحله)",
                ]
            else:
                current["ready"] = data_ready
                current["missing"] = list(original_missing)
            ordered[stage] = current

        state["stages"] = ordered
        state["stage_locks"] = locks
        state["production_ready"] = all(bool(item.get("ready")) for item in ordered.values())
        state["missing"] = [
            f"{STAGE_LABELS[stage]}: {item}"
            for stage in STAGE_ORDER
            for item in ordered[stage].get("missing", [])
        ]
        return state

    readiness_module.evaluate_readiness = evaluate_readiness
    # 3I.25 imported evaluate_readiness by value before this final wrapper was
    # composed. Rebind that module-level reference so publication/next-stage
    # checks see the same finalized seven-stage state as the visible rail.
    try:
        from . import phase49_3i25_product_first_workflow as product_first
        product_first.evaluate_readiness = evaluate_readiness
    except Exception:
        pass
    readiness_module._phase49_3i36_stage_finalization = True


def install_database(database_class) -> None:
    if getattr(database_class, "_phase49_3i36_stage_lock_guard", False):
        return
    original_init = database_class.__init__
    original_update = database_class.update_product

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        ensure_schema(self)

    def raw_update(self, product_id, values):
        return original_update(self, product_id, values)

    def update_product(self, product_id, values):
        values = dict(values or {})
        if not values:
            return None
        ensure_schema(self)
        row = self.product(product_id)
        filtered, blocked = filter_locked_updates(row, values)
        if blocked:
            audit_event(
                "workflow",
                "stage_locked_write_blocked",
                status="blocked",
                level="WARNING",
                product_id=int(product_id),
                source_file=__file__,
                message="locked fields ignored",
                detail={"fields": blocked, "phase": PHASE},
            )
        if not filtered:
            return None
        return original_update(self, product_id, filtered)

    database_class.__init__ = __init__
    database_class.update_product = update_product
    database_class._phase49_3i36_raw_update_product = raw_update
    database_class._phase49_3i36_stage_lock_guard = True


def _get_var(workspace, name, default=""):
    var = getattr(workspace, name, None)
    try:
        return var.get()
    except Exception:
        return default


def _get_text(workspace, name, default=""):
    widget = getattr(workspace, name, None)
    if widget is None:
        return default
    try:
        return widget.get("1.0", "end").strip()
    except Exception:
        try:
            return workspace._text_get(widget)
        except Exception:
            return default


def _lines(text: str) -> list[str]:
    return [line.strip() for line in str(text or "").splitlines() if line.strip()]


def persist_stage_from_ui(workspace, stage: str) -> None:
    """Persist only the requested stage. Never call the layered Workspace save chain."""
    row = workspace.db.product(int(workspace.product_id))
    if row is None:
        raise RuntimeError("محصول پیدا نشد.")
    values = {}

    if stage == "quick":
        from .product_studio import PRODUCT_TYPE_CODES
        title = str(_get_var(workspace, "content_title_fa") or _get_var(workspace, "title_fa") or "").strip()
        category_name = str(_get_var(workspace, "category_var") or "").strip()
        category_slug = getattr(workspace.app, "category_label_to_slug", {}).get(
            category_name, category_name or "external-other"
        )
        product_label = str(_get_var(workspace, "product_type_var") or "").strip()
        values.update({
            "title_fa": title,
            "local_category_slug": category_slug,
            "product_type": PRODUCT_TYPE_CODES.get(product_label, str(_row_value(row, "product_type", "ready_product"))),
            "dimensions": str(_get_var(workspace, "dimensions_var", _row_value(row, "dimensions", "")) or "").strip(),
            "use_case_class": str(_get_var(workspace, "use_case_class_var", _row_value(row, "use_case_class", "")) or "").strip(),
        })

    elif stage == "commerce":
        # Registered 3I.35 ledger is the commerce/profile authority.
        persist = getattr(workspace, "_phase49_3i35_persist_ledger", None)
        if callable(persist) and list(getattr(workspace, "_phase49_3i35_ledger", []) or []):
            persist()
        selected = getattr(workspace, "_phase49_3i35_selected_offers", None)
        commit_selected = getattr(workspace, "_phase49_3i35_commit_material_selection", None)
        if callable(selected) and callable(commit_selected):
            try:
                if selected():
                    commit_selected()
            except Exception:
                pass
        def number(name, default=0):
            raw = str(_get_var(workspace, name, default) or default).replace(",", "").strip()
            try:
                return int(float(raw))
            except Exception:
                return int(default)
        values.update({
            "price_min": max(0, number("price_min_var", _row_value(row, "price_min", 0))),
            "price_max": max(0, number("price_max_var", _row_value(row, "price_max", 0))),
            "stock_quantity": max(0, number("stock_var", _row_value(row, "stock_quantity", 0))),
            "lead_time_min_days": max(0, number("lead_min_var", _row_value(row, "lead_time_min_days", 1))),
            "lead_time_max_days": max(0, number("lead_max_var", _row_value(row, "lead_time_max_days", 3))),
        })
        strategy = str(_get_var(workspace, "pricing_strategy_var") or "").strip()
        if strategy in {"fixed", "range", "dynamic"}:
            values["pricing_strategy"] = strategy
        try:
            from .product_studio import AVAILABILITY_CODES
            availability = str(_get_var(workspace, "availability_var") or "").strip()
            if availability:
                values["availability_status"] = AVAILABILITY_CODES.get(
                    availability, str(_row_value(row, "availability_status", "made_to_order"))
                )
        except Exception:
            pass
        if hasattr(workspace, "has_3d_file_var"):
            values["has_3d_file"] = int(bool(_get_var(workspace, "has_3d_file_var", 0)))

    elif stage == "images":
        # Selection/upload/image editor actions already persist locally. Finalize only
        # acknowledges that durable image state; no gallery rebuild or download here.
        values = {}

    elif stage == "content":
        values.update({
            "short_description_fa": _get_text(workspace, "content_short_fa"),
            "description_fa": _get_text(workspace, "content_desc_fa"),
            "use_description": _get_text(workspace, "use_description_text"),
            "seo_title_fa": str(_get_var(workspace, "content_seo_title") or "").strip(),
            "seo_description_fa": _get_text(workspace, "content_seo_desc"),
            "social_caption_fa": _get_text(workspace, "content_social_caption"),
            "sales_bullets_json": json.dumps(_lines(_get_text(workspace, "content_sales_bullets")), ensure_ascii=False),
            "categories_fa_json": json.dumps(_lines(_get_text(workspace, "content_categories_fa")), ensure_ascii=False),
            "tags_fa_json": json.dumps(_lines(_get_text(workspace, "content_tags_fa")), ensure_ascii=False),
            "hashtags_fa_json": json.dumps(_lines(_get_text(workspace, "content_hashtags_fa")), ensure_ascii=False),
            "keywords_json": json.dumps(_lines(_get_text(workspace, "content_keywords")), ensure_ascii=False),
        })

    elif stage == "specs":
        source_url = str(_get_var(workspace, "source_url") or _get_var(workspace, "spec_source_url") or _row_value(row, "source_url", "")).strip()
        if source_url:
            values["source_url"] = source_url
            values["normalized_url"] = normalize_url(source_url)
        source_name = str(_get_var(workspace, "source_name_var") or "").strip()
        if source_name:
            values["source_name"] = source_name
        license_code = str(_get_var(workspace, "license_var") or _row_value(row, "commercial_status", "review")).strip()
        if license_code:
            values["commercial_status"] = license_code

        fa_specs = getattr(workspace, "fa_specs", None)
        if fa_specs is not None:
            raw = _get_text(workspace, "fa_specs", "")
            try:
                parsed = json.loads(raw or "{}")
                if not isinstance(parsed, dict):
                    raise ValueError("مشخصات فارسی باید JSON Object باشد.")
                values["specs_fa_json"] = json.dumps(parsed, ensure_ascii=False)
            except Exception as exc:
                raise ValueError(f"JSON مشخصات فارسی معتبر نیست: {exc}") from exc

        feature_widget = (
            "_phase49_3i39_spec_features"
            if hasattr(workspace, "_phase49_3i39_spec_features")
            else "technical_features_text"
        )
        if hasattr(workspace, feature_widget):
            raw = _get_text(workspace, feature_widget, "")
            try:
                parsed = json.loads(raw or "{}")
                if not isinstance(parsed, dict):
                    raise ValueError("ویژگی‌های فنی باید JSON Object باشد.")
                values["technical_features_json"] = json.dumps(parsed, ensure_ascii=False)
            except Exception as exc:
                raise ValueError(f"JSON ویژگی‌های فنی معتبر نیست: {exc}") from exc

        if hasattr(workspace, "_phase49_3i39_spec_summary"):
            values["technical_summary_fa"] = _get_text(
                workspace, "_phase49_3i39_spec_summary", ""
            )

    elif stage == "slider":
        media_values = getattr(workspace, "_phase49_3b_media_values", None)
        if callable(media_values):
            values.update(media_values())
        if hasattr(workspace, "slider_enabled_var"):
            values["homepage_slider_enabled"] = int(bool(_get_var(workspace, "slider_enabled_var", 0)))
        if hasattr(workspace, "slider_sort_var"):
            try:
                values["homepage_slider_sort_order"] = max(0, int(float(str(_get_var(workspace, "slider_sort_var", 100)).replace(",", ""))))
            except Exception:
                pass
        image_map = getattr(workspace, "_slider_image_map", {}) or {}
        image_label = str(_get_var(workspace, "slider_image_label_var") or "")
        if image_label in image_map:
            values["homepage_slider_image_url"] = image_map[image_label]
        for var_name, key in (
            ("slider_title_fa_var", "homepage_slider_title_fa"),
            ("slider_alt_text_var", "homepage_slider_alt_text"),
            ("slider_button_text_var", "homepage_slider_button_text"),
            ("slider_focus_keyword_var", "homepage_slider_focus_keyword"),
        ):
            if hasattr(workspace, var_name):
                values[key] = str(_get_var(workspace, var_name) or "").strip()
        if hasattr(workspace, "slider_description_text"):
            values["homepage_slider_description_fa"] = _get_text(workspace, "slider_description_text")

    elif stage == "publish":
        if hasattr(workspace, "approved_var"):
            values["approved_for_sale"] = int(bool(_get_var(workspace, "approved_var", 0)))
        if hasattr(workspace, "publish_product_var"):
            values["publish_as_product"] = int(bool(_get_var(workspace, "publish_product_var", 0)))
        if hasattr(workspace, "publish_portfolio_var"):
            values["publish_as_portfolio"] = int(bool(_get_var(workspace, "publish_portfolio_var", 0)))

    if values:
        workspace.db.update_product(int(workspace.product_id), values)
    workspace.row = workspace.db.product(int(workspace.product_id))


def _can_finalize(stage: str, state: dict, row) -> tuple[bool, list[str]]:
    current = (state.get("stages") or {}).get(stage) or {}
    if stage == "content":
        return content_manual_minimum(row)
    missing = list(current.get("missing_data") or current.get("missing") or [])
    # Never let manual finalization bypass source/license or publish safety.
    return bool(current.get("data_ready")), missing


def install_workspace(workspace_class, readiness_module) -> None:
    if getattr(workspace_class, "_phase49_3i36_stage_finalization", False):
        return
    configure_readiness(readiness_module)
    original_init = workspace_class.__init__
    original_reload = workspace_class.reload

    def __init__(self, app, product_id):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        ensure_schema(app.db)
        self._phase49_3i36_status_vars = {}
        self._phase49_3i36_build_lock_panel()
        self._phase49_3i36_refresh_locks()

    def build_lock_panel(self):
        buttons = getattr(self, "_section_buttons", {}) or {}
        if not buttons:
            return
        rail = next(iter(buttons.values())).master
        panel = ttk.LabelFrame(
            rail,
            text="ثبت نهایی مراحل — AI فقط مراحل باز را ویرایش می‌کند",
            padding=6,
            style="Card.TLabelframe",
        )
        panel.pack(fill="x", pady=(10, 4))
        for stage in STAGE_ORDER:
            row = ttk.Frame(panel)
            row.pack(fill="x", pady=2)
            status = tk.StringVar(value="")
            self._phase49_3i36_status_vars[stage] = status
            ttk.Label(row, text=STAGE_LABELS[stage], width=24).pack(side="right")
            ttk.Button(
                row,
                text="ثبت",
                width=7,
                command=lambda s=stage: self._phase49_3i36_finalize_stage(s),
                style="Success.TButton",
            ).pack(side="right", padx=2)
            ttk.Button(
                row,
                text="اصلاح",
                width=7,
                command=lambda s=stage: self._phase49_3i36_unlock_stage(s),
            ).pack(side="right", padx=2)
            ttk.Label(row, textvariable=status, style="SubHeader.TLabel").pack(side="left", padx=2)
        self._phase49_3i36_lock_panel = panel

    def refresh_locks(self):
        row = self.db.product(int(self.product_id))
        locks = stage_locks(row)
        state = readiness_module.evaluate_readiness(row)
        for stage, variable in (getattr(self, "_phase49_3i36_status_vars", {}) or {}).items():
            locked = bool((locks.get(stage) or {}).get("locked"))
            data_ready = bool(((state.get("stages") or {}).get(stage) or {}).get("data_ready"))
            if locked:
                variable.set("🔒 نهایی")
            elif data_ready or (stage == "content" and content_manual_minimum(row)[0]):
                variable.set("✅ کامل؛ منتظر ثبت")
            else:
                variable.set("⚪ ناقص/باز")
        try:
            self._phase49_refresh_readiness()
        except Exception:
            pass
        try:
            self._phase49_3b_refresh_wizard()
        except Exception:
            pass

    def finalize_stage(self, stage: str):
        stage = str(stage)
        if stage not in STAGE_ORDER:
            return False
        row_before = self.db.product(int(self.product_id))
        if is_stage_locked(row_before, stage):
            self.footer_status.set(f"{STAGE_LABELS[stage]} قبلاً نهایی شده؛ برای تغییر ابتدا «اصلاح» را بزن.")
            return True
        try:
            persist_stage_from_ui(self, stage)
        except Exception as exc:
            messagebox.showerror("ثبت مرحله", f"ثبت اطلاعات همین مرحله ناموفق بود:\n{exc}", parent=self)
            return False
        row = self.db.product(int(self.product_id))
        state = readiness_module.evaluate_readiness(row)
        allowed, missing = _can_finalize(stage, state, row)
        if not allowed:
            messagebox.showwarning(
                "ثبت مرحله",
                f"{STAGE_LABELS[stage]} هنوز برای ثبت نهایی آماده نیست:\n\n- "
                + "\n- ".join(missing[:12]),
                parent=self,
            )
            self._phase49_3i36_refresh_locks()
            return False

        locks = stage_locks(row)
        locks[stage] = {
            "locked": True,
            "locked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        values = {LOCK_COLUMN: json.dumps(locks, ensure_ascii=False)}
        if stage == "content":
            values["seo_manual_approved"] = 1
        if stage == "specs":
            values["source_review_manual_approved"] = 1
        self.db.update_product(int(self.product_id), values)
        audit_event(
            "workflow", "stage_finalized", product_id=int(self.product_id),
            source_file=__file__, message=stage, detail={"stage": stage, "phase": PHASE},
        )
        self._phase49_3i36_refresh_locks()
        self.footer_status.set(f"🔒 {STAGE_LABELS[stage]} ثبت نهایی شد؛ AI و Saveهای بعدی حق تغییر آن را ندارند.")
        return True

    def unlock_stage(self, stage: str):
        stage = str(stage)
        if stage not in STAGE_ORDER:
            return False
        row = self.db.product(int(self.product_id))
        if not is_stage_locked(row, stage):
            self.footer_status.set(f"{STAGE_LABELS[stage]} همین حالا در حالت اصلاح است.")
            return True
        if not messagebox.askyesno(
            "اصلاح مرحله",
            f"قفل «{STAGE_LABELS[stage]}» باز شود؟\nتا ثبت دوباره، اپراتور و AI فقط در محدوده مجاز این مرحله می‌توانند آن را تغییر دهند.",
            parent=self,
        ):
            return False
        locks = stage_locks(row)
        locks.pop(stage, None)
        # Unlock first. The manual-approval field belongs to the stage itself and
        # would correctly be blocked while the old lock is still active.
        self.db.update_product(
            int(self.product_id),
            {LOCK_COLUMN: json.dumps(locks, ensure_ascii=False)},
        )
        if stage == "content":
            self.db.update_product(int(self.product_id), {"seo_manual_approved": 0})
        if stage == "specs":
            self.db.update_product(int(self.product_id), {"source_review_manual_approved": 0})
        audit_event(
            "workflow", "stage_unlocked", product_id=int(self.product_id),
            source_file=__file__, message=stage, detail={"stage": stage, "phase": PHASE},
        )
        self._phase49_3i36_refresh_locks()
        self.footer_status.set(f"✏️ {STAGE_LABELS[stage]} برای اصلاح باز شد.")
        return True

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "_phase49_3i36_status_vars"):
            refresh_locks(self)
        return result

    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class._phase49_3i36_build_lock_panel = build_lock_panel
    workspace_class._phase49_3i36_refresh_locks = refresh_locks
    workspace_class._phase49_3i36_finalize_stage = finalize_stage
    workspace_class._phase49_3i36_unlock_stage = unlock_stage
    workspace_class._phase49_3i36_stage_finalization = True


def hydrate_ai_state(app) -> None:
    """Restore visible AI settings from durable local stores with zero network calls."""
    provider = str(app.db.setting("ai_provider", "") or "").strip().lower()
    if provider:
        try:
            app.ai_provider.set(provider)
        except Exception:
            pass
        active = getattr(app, "_phase49_3d_active_provider", None)
        try:
            if active is not None:
                active.set(provider)
        except Exception:
            pass

    model_vars = getattr(app, "_ai_hub_model_vars", {}) or {}
    key_vars = getattr(app, "_ai_hub_key_vars", {}) or {}
    for name, variable in model_vars.items():
        stored = str(app.db.setting(f"ai_model_{name}", "") or "").strip()
        if stored:
            try:
                variable.set(stored)
            except Exception:
                pass
    if provider:
        model = str(
            app.db.setting(f"ai_model_{provider}", "")
            or app.db.setting("ai_model", "")
            or ""
        ).strip()
        if model:
            try:
                app.ai_model.set(model)
            except Exception:
                pass
            variable = model_vars.get(provider)
            try:
                if variable is not None:
                    variable.set(model)
            except Exception:
                pass

    for name, variable in key_vars.items():
        try:
            current = str(variable.get() or "").strip()
        except Exception:
            current = ""
        if current:
            continue
        try:
            secret = str(secure_secrets.get_provider_key(name) or "").strip()
        except Exception:
            secret = ""
        if secret:
            try:
                variable.set(secret)
            except Exception:
                pass

    audit_event(
        "settings", "ai_state_hydrated_no_network", source_file=__file__,
        message=f"provider={provider or 'unset'}", detail={"phase": PHASE, "network": False},
    )


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i36_ai_state_hydration", False):
        return
    original_init = app_class.__init__
    original_refresh_source = getattr(app_class, "_refresh_ai_key_source", None)

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        hydrate_ai_state(self)

    def refresh_ai_key_source(self):
        result = original_refresh_source(self) if callable(original_refresh_source) else None
        hydrate_ai_state(self)
        return result

    app_class.__init__ = __init__
    if callable(original_refresh_source):
        app_class._refresh_ai_key_source = refresh_ai_key_source
    app_class._phase49_3i36_hydrate_ai_state = hydrate_ai_state
    app_class._phase49_3i36_ai_state_hydration = True
