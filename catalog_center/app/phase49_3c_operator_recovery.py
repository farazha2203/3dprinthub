from __future__ import annotations

import json
import tkinter as tk
from tkinter import messagebox, ttk

from .epic49_product_studio import LICENSE_LABEL_TO_CODE
from .phase49_3b_guided_wizard import STAGE_HELP, STAGE_LABELS, STAGE_ORDER
from .phase49_3c_image_pipeline import image_metadata_missing
from .product_studio import PRODUCT_TYPE_CODES


FIELD_STAGE = {
    "عنوان فارسی": "quick",
    "گروه سایت": "quick",
    "نوع محصول": "quick",
    "قیمت یا حالت سفارش": "commerce",
    "حداقل یک متریال": "commerce",
    "حداقل یک رنگ": "commerce",
    "تصویر اصلی": "images",
    "حداقل یک تصویر انتخاب‌شده": "images",
    "عنوان فارسی": "content",
    "توضیح فارسی": "content",
    "SEO Title فارسی": "content",
    "SEO Description فارسی": "content",
    "عبارت‌های هدف SEO": "content",
    "Alt تصویر": "content",
    "لینک منبع": "specs",
    "مجوز تجاری مجاز": "specs",
    "عنوان اسلایدر": "slider",
    "توضیح اسلایدر": "slider",
    "Alt اسلایدر": "slider",
    "عبارت هدف اسلایدر": "slider",
    "عکس اسلایدر": "slider",
    "تأیید برای فروش": "publish",
    "نوع انتشار محصول": "publish",
}

OPERATOR_ONLY_HINTS = {
    "قیمت یا حالت سفارش": "نیازمند اپراتور یا محاسبه قیمت از داده واقعی است.",
    "حداقل یک متریال": "متریال واقعی باید توسط اپراتور انتخاب شود؛ AI فقط پیشنهاد می‌دهد.",
    "حداقل یک رنگ": "رنگ واقعی باید توسط اپراتور انتخاب شود.",
    "مجوز تجاری مجاز": "مجوز باید از روی منبع و حق استفاده توسط اپراتور تأیید شود.",
    "تأیید برای فروش": "تأیید فروش تصمیم اپراتور است.",
    "نوع انتشار محصول": "نوع انتشار تصمیم اپراتور است.",
}


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _text(widget) -> str:
    try:
        return widget.get("1.0", "end").strip()
    except Exception:
        return ""


def _var(value, default=""):
    try:
        result = value.get()
    except Exception:
        return default
    return default if result is None else result


def build_live_snapshot(workspace, base_row) -> dict:
    """Merge visible, unsaved widgets over the database row for live readiness."""
    data = dict(base_row or {})
    if not data:
        return data

    title = str(_var(getattr(workspace, "content_title_fa", None), "") or "").strip()
    if not title:
        title = str(_var(getattr(workspace, "title_fa", None), "") or "").strip()
    data["title_fa"] = title

    category_name = str(_var(getattr(workspace, "category_var", None), "") or "").strip()
    app = getattr(workspace, "app", None)
    slug_map = getattr(app, "category_label_to_slug", {}) if app is not None else {}
    data["local_category_slug"] = slug_map.get(
        category_name,
        category_name or str(data.get("local_category_slug") or "external-other"),
    )

    product_type_label = str(_var(getattr(workspace, "product_type_var", None), "") or "")
    data["product_type"] = PRODUCT_TYPE_CODES.get(
        product_type_label,
        str(data.get("product_type") or "ready_product"),
    )

    for key, attr in (
        ("final_price", "final_price_var"),
        ("suggested_price", "suggested_price_var"),
        ("price_min", "price_min_var"),
        ("price_max", "price_max_var"),
    ):
        value = str(_var(getattr(workspace, attr, None), data.get(key, 0)) or "").replace(",", "").strip()
        try:
            data[key] = int(float(value or 0))
        except Exception:
            data[key] = 0

    if hasattr(workspace, "_selected_materials"):
        try:
            materials = list(workspace._selected_materials())
            data["material_options_json"] = json.dumps(materials, ensure_ascii=False)
            data["materials_json"] = json.dumps(materials, ensure_ascii=False)
        except Exception:
            pass
    if hasattr(workspace, "_selected_colors"):
        try:
            colors = list(workspace._selected_colors())
            data["color_options_json"] = json.dumps(colors, ensure_ascii=False)
            data["colors_json"] = json.dumps(
                [str(item.get("name") or "") for item in colors if isinstance(item, dict)],
                ensure_ascii=False,
            )
        except Exception:
            pass

    data["short_description_fa"] = _text(getattr(workspace, "content_short_fa", None))
    data["description_fa"] = _text(getattr(workspace, "content_desc_fa", None))
    data["seo_title_fa"] = str(_var(getattr(workspace, "content_seo_title", None), "") or "").strip()
    data["seo_description_fa"] = _text(getattr(workspace, "content_seo_desc", None))

    list_widgets = (
        ("keywords_json", "content_keywords"),
        ("image_alt_texts_json", "content_image_alts"),
        ("tags_fa_json", "content_tags_fa"),
        ("hashtags_fa_json", "content_hashtags_fa"),
        ("categories_fa_json", "content_categories_fa"),
        ("materials_json", "content_materials"),
        ("colors_json", "content_colors"),
    )
    for key, attr in list_widgets:
        widget = getattr(workspace, attr, None)
        if widget is None:
            continue
        values = [line.strip() for line in _text(widget).splitlines() if line.strip()]
        data[key] = json.dumps(values, ensure_ascii=False)

    if hasattr(workspace, "source_url"):
        data["source_url"] = str(_var(workspace.source_url, data.get("source_url", "")) or "").strip()
    if hasattr(workspace, "publish_license_label_var"):
        label = str(_var(workspace.publish_license_label_var, "") or "")
        data["commercial_status"] = LICENSE_LABEL_TO_CODE.get(
            label,
            str(_var(getattr(workspace, "license_var", None), data.get("commercial_status", "review")) or "review"),
        )
    elif hasattr(workspace, "license_var"):
        data["commercial_status"] = str(_var(workspace.license_var, data.get("commercial_status", "review")) or "review")

    if hasattr(workspace, "approved_var"):
        data["approved_for_sale"] = int(bool(_var(workspace.approved_var, data.get("approved_for_sale", 0))))
    if hasattr(workspace, "publish_product_var"):
        data["publish_as_product"] = int(bool(_var(workspace.publish_product_var, data.get("publish_as_product", 0))))
    if hasattr(workspace, "publish_portfolio_var"):
        data["publish_as_portfolio"] = int(bool(_var(workspace.publish_portfolio_var, data.get("publish_as_portfolio", 0))))

    slider_map = (
        ("homepage_slider_title_fa", "slider_title_fa_var"),
        ("homepage_slider_alt_text", "slider_alt_text_var"),
        ("homepage_slider_button_text", "slider_button_text_var"),
        ("homepage_slider_focus_keyword", "slider_focus_keyword_var"),
        ("homepage_slider_image_url", "slider_image_url_var"),
    )
    for key, attr in slider_map:
        if hasattr(workspace, attr):
            data[key] = str(_var(getattr(workspace, attr), data.get(key, "")) or "").strip()
    if hasattr(workspace, "slider_description_text"):
        data["homepage_slider_description_fa"] = _text(workspace.slider_description_text)
    if hasattr(workspace, "slider_enabled_var"):
        data["homepage_slider_enabled"] = int(bool(_var(workspace.slider_enabled_var, data.get("homepage_slider_enabled", 0))))

    current = workspace.db.product(workspace.product_id)
    if current is not None:
        for key in ("images_json", "selected_images_json", "primary_image_url", "image_metadata_json"):
            try:
                data[key] = current[key]
            except Exception:
                pass
    return data


def _augment_image_stage(state: dict, snapshot: dict) -> dict:
    stages = state.setdefault("stages", {})
    image = stages.get("images")
    if not image:
        return state
    missing = list(image.get("missing") or [])
    selected = _json_list(snapshot.get("selected_images_json"))
    if len(selected) > 10:
        missing.append("حداکثر ۱۰ تصویر برای سایت")
    for label in image_metadata_missing(snapshot):
        if label not in missing:
            missing.append(label)
    image["missing"] = missing
    image["ready"] = not missing
    all_missing = []
    for key in STAGE_ORDER:
        stage = stages.get(key) or {}
        label = stage.get("label") or STAGE_LABELS.get(key, key)
        all_missing.extend(f"{label}: {item}" for item in stage.get("missing") or [])
    state["missing"] = all_missing
    state["production_ready"] = all(
        bool((stages.get(key) or {}).get("ready"))
        for key in STAGE_ORDER
        if key in stages
    )
    return state


def install(workspace_class, readiness_module) -> None:
    if getattr(workspace_class, "_phase49_3c_operator_recovery_installed", False):
        return

    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_save = workspace_class.save
    original_readiness = getattr(workspace_class, "_phase49_refresh_readiness", None)
    original_guided_refresh = getattr(workspace_class, "_phase49_3b_refresh_wizard", None)
    original_queue = workspace_class.queue_for_publish

    def __init__(self, app, product_id: int):
        self._phase49_3c_after_id = None
        self._phase49_3c_trace_tokens = []
        original_init(self, app, product_id)
        self._phase49_3c_add_assistant_bar()
        self._phase49_3c_add_missing_panel()
        self._phase49_3c_bind_live_fields()
        self.after(50, self._phase49_3c_refresh_live)

    def _phase49_3c_add_assistant_bar(self):
        children = list(self.winfo_children())
        old_footer = children[-1] if children else None
        bar = ttk.LabelFrame(
            self,
            text="دستیار هوشمند اپراتور",
            padding=(12, 7),
            style="Card.TLabelframe",
        )
        kwargs = {"fill": "x", "padx": 12, "pady": (0, 6)}
        if old_footer is not None:
            kwargs["before"] = old_footer
        bar.pack(**kwargs)
        self._phase49_3c_ai_context = tk.StringVar(value="AI همین مرحله")
        ttk.Label(
            bar,
            textvariable=self._phase49_3c_ai_context,
            style="SubHeader.TLabel",
        ).pack(side="right", padx=8)
        ttk.Button(
            bar,
            text="✨ دستیار AI همین مرحله",
            command=self._phase49_3c_stage_ai,
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            bar,
            text="✨ تکمیل هوشمند همه فیلدهای AI",
            command=self._phase49_3c_all_ai,
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            bar,
            text="🖼 نهایی‌سازی SEO تصاویر",
            command=self.phase49_3c_finalize_images,
        ).pack(side="left", padx=3)

    def _phase49_3c_add_missing_panel(self):
        buttons = getattr(self, "_section_buttons", {})
        if not buttons:
            return
        rail = next(iter(buttons.values())).master
        frame = tk.Frame(
            rail,
            bg="#0b2238",
            highlightbackground="#29445e",
            highlightthickness=1,
        )
        frame.pack(fill="x", pady=(10, 4))
        tk.Label(
            frame,
            text="موارد ناقص زنده",
            bg="#0b2238",
            fg="#f6d77a",
            font=("Tahoma", 9, "bold"),
        ).pack(anchor="e", padx=6, pady=(5, 2))
        self._phase49_3c_missing = tk.Listbox(
            frame,
            height=7,
            bg="#102c46",
            fg="#ffffff",
            selectbackground="#c99a2e",
            selectforeground="#071827",
            bd=0,
            highlightthickness=0,
            font=("Tahoma", 8),
        )
        self._phase49_3c_missing.pack(fill="x", padx=5, pady=(0, 5))
        self._phase49_3c_missing.bind(
            "<Double-Button-1>",
            lambda _event: self._phase49_3c_focus_missing(),
        )
        self._phase49_3c_missing_records = []

    def _phase49_3c_collect_variables(self):
        seen = set()
        for value in self.__dict__.values():
            candidates = []
            if isinstance(value, tk.Variable):
                candidates = [value]
            elif isinstance(value, dict):
                candidates = [item for item in value.values() if isinstance(item, tk.Variable)]
            elif isinstance(value, (list, tuple)):
                candidates = [item for item in value if isinstance(item, tk.Variable)]
            for var in candidates:
                marker = str(var)
                if marker in seen:
                    continue
                seen.add(marker)
                yield var

    def _phase49_3c_bind_live_fields(self):
        for var in self._phase49_3c_collect_variables():
            try:
                token = var.trace_add(
                    "write",
                    lambda *_args, self=self: self._phase49_3c_schedule_live(),
                )
                self._phase49_3c_trace_tokens.append((var, token))
            except Exception:
                pass

        def walk(widget):
            for child in widget.winfo_children():
                yield child
                yield from walk(child)

        for widget in walk(self):
            if isinstance(widget, (tk.Text, tk.Entry, ttk.Entry)):
                try:
                    widget.bind(
                        "<KeyRelease>",
                        lambda _event, self=self: self._phase49_3c_schedule_live(),
                        add="+",
                    )
                except Exception:
                    pass
            if isinstance(widget, ttk.Combobox):
                try:
                    widget.bind(
                        "<<ComboboxSelected>>",
                        lambda _event, self=self: self._phase49_3c_schedule_live(),
                        add="+",
                    )
                except Exception:
                    pass
            if isinstance(widget, (ttk.Checkbutton, tk.Checkbutton)):
                try:
                    widget.bind(
                        "<ButtonRelease-1>",
                        lambda _event, self=self: self.after(10, self._phase49_3c_schedule_live),
                        add="+",
                    )
                except Exception:
                    pass

    def _phase49_3c_schedule_live(self):
        try:
            if self._phase49_3c_after_id is not None:
                self.after_cancel(self._phase49_3c_after_id)
        except Exception:
            pass
        try:
            self._phase49_3c_after_id = self.after(180, self._phase49_3c_refresh_live)
        except Exception:
            self._phase49_3c_after_id = None

    def _phase49_3c_state(self):
        row = self.db.product(self.product_id)
        snapshot = build_live_snapshot(self, row)
        state = readiness_module.evaluate_readiness(snapshot)
        state = _augment_image_stage(state, snapshot)
        return state, snapshot

    def _phase49_refresh_readiness(self):
        if hasattr(self, "_phase49_3c_missing"):
            state, _snapshot = self._phase49_3c_state()
            self._phase49_readiness_state = state
            return state
        if original_readiness is not None:
            return original_readiness(self)
        return None

    def _phase49_3c_refresh_live(self):
        self._phase49_3c_after_id = None
        if not self.winfo_exists():
            return
        try:
            state, _snapshot = self._phase49_3c_state()
        except Exception:
            return
        self._phase49_readiness_state = state
        current = self._phase49_3b_current_key(default="quick")
        current_stage = state.get("stages", {}).get(current) or {"ready": False, "missing": []}

        if hasattr(self, "_phase49_3b_help_var"):
            self._phase49_3b_help_var.set(STAGE_HELP.get(current, ""))
        if hasattr(self, "_phase49_3b_required_var"):
            missing = current_stage.get("missing") or []
            self._phase49_3b_required_var.set(
                "" if not missing else "★ الزامی برای ادامه: " + " • ".join(missing[:8])
            )

        index = STAGE_ORDER.index(current) if current in STAGE_ORDER else 0
        first_incomplete = next(
            (
                idx
                for idx, key in enumerate(STAGE_ORDER)
                if not (state.get("stages", {}).get(key) or {}).get("ready", False)
            ),
            len(STAGE_ORDER),
        )
        for idx, key in enumerate(STAGE_ORDER):
            button = getattr(self, "_section_buttons", {}).get(key)
            if button is None:
                continue
            ready = bool((state.get("stages", {}).get(key) or {}).get("ready"))
            icon = "✅" if ready else ("🔒" if idx > first_incomplete else "❌ ★")
            try:
                button.configure(
                    text=f"{icon} {STAGE_LABELS[key]}",
                    state="disabled" if idx > max(first_incomplete, index) else "normal",
                )
            except Exception:
                pass

        if hasattr(self, "_phase49_3b_prev"):
            self._phase49_3b_prev.configure(state="disabled" if index == 0 else "normal")
        if hasattr(self, "_phase49_3b_next"):
            if index == len(STAGE_ORDER) - 1:
                self._phase49_3b_next.configure(
                    text="💾 ذخیره نهایی",
                    state="normal",
                    command=lambda: self.save(),
                )
            else:
                self._phase49_3b_next.configure(
                    text="مرحله بعد برای انتشار →",
                    state="normal" if current_stage.get("ready") else "disabled",
                    command=self._phase49_3b_go_next,
                )

        if hasattr(self, "_phase49_readiness_summary"):
            if state.get("production_ready"):
                self._phase49_readiness_summary.set("✅ محصول آماده انتشار است")
            else:
                total = sum(
                    len((stage or {}).get("missing") or [])
                    for stage in state.get("stages", {}).values()
                )
                self._phase49_readiness_summary.set(f"❌ آماده Production نیست • {total} مورد ناقص")
        if hasattr(self, "_phase49_readiness_missing"):
            missing = current_stage.get("missing") or []
            self._phase49_readiness_missing.set(
                "همین مرحله کامل است."
                if not missing
                else " • ".join(missing[:3])
            )

        publish_ready = bool(state.get("production_ready"))
        for attr in ("_phase49_site_button", "_phase49_local_button"):
            button = getattr(self, attr, None)
            if button is not None:
                try:
                    button.state(["!disabled"] if publish_ready else ["disabled"])
                except Exception:
                    pass

        self._phase49_3c_missing_records = []
        if hasattr(self, "_phase49_3c_missing"):
            self._phase49_3c_missing.delete(0, "end")
            for key in STAGE_ORDER:
                stage = state.get("stages", {}).get(key) or {}
                for label in stage.get("missing") or []:
                    text = f"{STAGE_LABELS[key]} ← {label}"
                    if label in OPERATOR_ONLY_HINTS:
                        text += " • اپراتور"
                    self._phase49_3c_missing.insert("end", text)
                    self._phase49_3c_missing_records.append((key, label))
            if not self._phase49_3c_missing_records:
                self._phase49_3c_missing.insert("end", "✅ همه موارد اجباری کامل است")

        if hasattr(self, "_phase49_3c_ai_context"):
            stage_label = STAGE_LABELS.get(current, current)
            operator_missing = [
                label
                for label in current_stage.get("missing") or []
                if label in OPERATOR_ONLY_HINTS
            ]
            suffix = (
                " • موارد اپراتوری: " + "، ".join(operator_missing[:2])
                if operator_missing
                else ""
            )
            self._phase49_3c_ai_context.set(f"دستیار فعال برای {stage_label}{suffix}")

    def _phase49_3b_refresh_wizard(self):
        if hasattr(self, "_phase49_3c_missing"):
            self._phase49_3c_refresh_live()
            return
        if original_guided_refresh is not None:
            return original_guided_refresh(self)

    def _phase49_3c_focus_missing(self):
        if not getattr(self, "_phase49_3c_missing_records", None):
            return
        selection = self._phase49_3c_missing.curselection()
        if not selection:
            return
        stage, label = self._phase49_3c_missing_records[int(selection[0])]
        try:
            self.select_section(stage)
        except Exception:
            pass
        focus_targets = {
            "گروه سایت": "category_box",
            "توضیح فارسی": "content_short_fa",
            "SEO Description فارسی": "content_seo_desc",
            "Alt تصویر": "content_image_alts",
            "لینک منبع": "source_url",
        }
        target = getattr(self, focus_targets.get(label, ""), None)
        if isinstance(target, tk.Variable):
            target = None
        if target is not None:
            try:
                target.focus_set()
            except Exception:
                pass
        hint = OPERATOR_ONLY_HINTS.get(label)
        if hint:
            self.footer_status.set(f"{label}: {hint}")

    def _phase49_3c_stage_ai(self):
        current = self._phase49_3b_current_key(default="quick")
        if current == "quick":
            return self.translate_title_only()
        if current == "images":
            row = self.db.product(self.product_id)
            alts = _json_list(row["image_alt_texts_json"] if row is not None and "image_alt_texts_json" in row.keys() else "[]")
            if alts:
                return self.phase49_3c_finalize_images()
            self.footer_status.set("AI ابتدا Alt/SEO/تگ‌های تصاویر را می‌سازد؛ بعد نهایی‌سازی SEO تصاویر را بزن.")
            return self.generate_ai("commerce")
        if current in {"commerce", "content", "specs", "slider"}:
            self.footer_status.set(
                "AI فقط داده‌های قابل استنتاج را پیشنهاد می‌دهد؛ قیمت، مجوز، رنگ و انتخاب متریال واقعی جعل نمی‌شوند."
            )
            return self.generate_ai("commerce")
        return self.generate_ai("commerce")

    def _phase49_3c_all_ai(self):
        self.footer_status.set(
            "پکیج کامل AI در حال تولید است: عنوان، توضیح کوتاه/کامل، تگ، هشتگ، SEO، فروش، Alt و پیشنهاد متریال."
        )
        return self.generate_ai("commerce")

    def queue_for_publish(self, notify=True):
        try:
            self.save(silent=True)
        except Exception:
            pass
        state, _snapshot = self._phase49_3c_state()
        self._phase49_readiness_state = state
        if not state.get("production_ready"):
            first = next(
                (
                    key
                    for key in STAGE_ORDER
                    if not (state.get("stages", {}).get(key) or {}).get("ready", False)
                ),
                "publish",
            )
            try:
                self.select_section(first)
            except Exception:
                pass
            if notify:
                missing = state.get("missing") or []
                messagebox.showwarning(
                    "3DPrintHub — محصول هنوز کامل نیست",
                    "انتشار/صف متوقف شد. موارد ناقص:\n\n- "
                    + "\n- ".join(missing[:16]),
                    parent=self,
                )
            self._phase49_3c_refresh_live()
            return False
        return original_queue(self, notify=notify)

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "_phase49_3c_missing"):
            self._phase49_3c_schedule_live()
        return result

    def save(self, silent=False):
        ok = original_save(self, silent=silent)
        if ok and hasattr(self, "_phase49_3c_missing"):
            self._phase49_3c_schedule_live()
        return ok

    workspace_class.__init__ = __init__
    workspace_class._phase49_3c_add_assistant_bar = _phase49_3c_add_assistant_bar
    workspace_class._phase49_3c_add_missing_panel = _phase49_3c_add_missing_panel
    workspace_class._phase49_3c_collect_variables = _phase49_3c_collect_variables
    workspace_class._phase49_3c_bind_live_fields = _phase49_3c_bind_live_fields
    workspace_class._phase49_3c_schedule_live = _phase49_3c_schedule_live
    workspace_class._phase49_3c_state = _phase49_3c_state
    workspace_class._phase49_refresh_readiness = _phase49_refresh_readiness
    workspace_class._phase49_3c_refresh_live = _phase49_3c_refresh_live
    workspace_class._phase49_3b_refresh_wizard = _phase49_3b_refresh_wizard
    workspace_class._phase49_3c_focus_missing = _phase49_3c_focus_missing
    workspace_class._phase49_3c_stage_ai = _phase49_3c_stage_ai
    workspace_class._phase49_3c_all_ai = _phase49_3c_all_ai
    workspace_class.queue_for_publish = queue_for_publish
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_3c_operator_recovery_installed = True
