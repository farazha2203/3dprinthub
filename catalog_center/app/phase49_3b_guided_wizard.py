from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image, ImageFilter, ImageOps, ImageTk

from .ai_providers import AIProviderClient
from .phase49_diagnostics import audit_event


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
STAGE_HELP = {
    "quick": "برای ادامه: ★ عنوان فارسی، ★ گروه سایت و ★ نوع محصول را تکمیل کن. ترجمه فقط عنوان فارسی از همین مرحله قابل انجام است.",
    "commerce": "برای ادامه: ★ قیمت/حالت سفارش، ★ حداقل یک متریال و ★ حداقل یک رنگ را مشخص کن.",
    "images": "برای ادامه: ★ تصویر اصلی، ★ حداقل یک تصویر منتخب سایت و ★ Alt تصاویر لازم است.",
    "content": "برای ادامه: ★ توضیحات فارسی، ★ SEO Title/Description و ★ عبارت‌های هدف لازم است.",
    "specs": "برای ادامه: ★ لینک منبع و ★ وضعیت مجوز تجاری معتبر لازم است.",
    "slider": "اسلایدر اختیاری است. اگر فعالش کنی، ★ عنوان/توضیح/Alt/Focus/عکس Hero و تنظیم نمایش باید کامل باشند.",
    "publish": "گزارش نهایی را بررسی کن. Local Publish برای QA است؛ Production فقط وقتی همه Gateها سبز باشند فعال می‌شود.",
}

PRESENTATION = (
    ("product_fit", "نمایش کامل محصول"),
    ("full_bleed", "پر کردن کامل اسلایدر"),
    ("framed", "کادر محصول"),
    ("cinematic", "سینمایی با پس‌زمینه"),
)
PRESENTATION_CODE = {label: code for code, label in PRESENTATION}
PRESENTATION_LABEL = {code: label for code, label in PRESENTATION}
BACKGROUND = (
    ("solid", "رنگ ثابت"),
    ("blur", "Blur از خود تصویر"),
    ("gradient", "گرادیان"),
    ("image", "خود تصویر"),
)
BACKGROUND_CODE = {label: code for code, label in BACKGROUND}
BACKGROUND_LABEL = {code: label for code, label in BACKGROUND}

HERO_COLUMNS = {
    "homepage_slider_presentation_mode": "TEXT NOT NULL DEFAULT 'product_fit'",
    "homepage_slider_object_fit": "TEXT NOT NULL DEFAULT 'contain'",
    "homepage_slider_focal_position": "TEXT NOT NULL DEFAULT 'center'",
    "homepage_slider_image_scale_percent": "INTEGER NOT NULL DEFAULT 100",
    "homepage_slider_position_x_percent": "INTEGER NOT NULL DEFAULT 50",
    "homepage_slider_position_y_percent": "INTEGER NOT NULL DEFAULT 50",
    "homepage_slider_background_mode": "TEXT NOT NULL DEFAULT 'blur'",
    "homepage_slider_background_color": "TEXT NOT NULL DEFAULT '#071827'",
    "homepage_slider_background_blur_px": "INTEGER NOT NULL DEFAULT 18",
    "homepage_slider_desktop_max_width_percent": "INTEGER NOT NULL DEFAULT 78",
    "homepage_slider_desktop_max_height_percent": "INTEGER NOT NULL DEFAULT 88",
    "homepage_slider_mobile_max_width_percent": "INTEGER NOT NULL DEFAULT 92",
    "homepage_slider_mobile_max_height_percent": "INTEGER NOT NULL DEFAULT 72",
}


def _columns(db) -> set[str]:
    return {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}


def ensure_schema(db) -> None:
    existing = _columns(db)
    for name, ddl in HERO_COLUMNS.items():
        if name not in existing:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
    db.conn.commit()


def _value(row, key, default=""):
    if row is None:
        return default
    try:
        value = row[key]
    except Exception:
        return default
    return default if value is None else value


def _bounded(value, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(float(str(value if value is not None else default).replace(",", "")))
    except Exception:
        parsed = default
    return min(maximum, max(minimum, parsed))


def _stage_data_ready(stage: dict | None) -> bool:
    stage = dict(stage or {})
    if "data_ready" in stage:
        return bool(stage.get("data_ready"))
    return bool(stage.get("ready"))


def _stage_data_missing(stage: dict | None) -> list[str]:
    stage = dict(stage or {})
    if "missing_data" in stage:
        return list(stage.get("missing_data") or [])
    return [
        str(item)
        for item in (stage.get("missing") or [])
        if str(item) != "تأیید نهایی اپراتور (ثبت مرحله)"
    ]


def configure_readiness(readiness_module) -> None:
    """Upgrade Phase49.3A evaluation from six stages to the seven-stage wizard."""
    readiness_module.STAGE_LABELS.clear()
    readiness_module.STAGE_LABELS.update(STAGE_LABELS)
    original = readiness_module.evaluate_readiness

    def evaluate_readiness(row):
        state = original(row)
        stages = state.get("stages", {})
        slider_enabled = bool(int(_value(row, "homepage_slider_enabled", 0) or 0)) if row is not None else False
        # Phase49.3A kept slider requirements in publish. Move them into their own stage.
        slider_labels = {"عنوان اسلایدر", "توضیح اسلایدر", "Alt اسلایدر", "عبارت هدف اسلایدر", "عکس اسلایدر"}
        publish = stages.get("publish", {"ready": False, "missing": []})
        publish_missing = [item for item in publish.get("missing", []) if item not in slider_labels]
        publish["missing"] = publish_missing
        publish["ready"] = not publish_missing
        publish["label"] = STAGE_LABELS["publish"]
        stages["publish"] = publish

        slider_missing = []
        if slider_enabled:
            checks = [
                ("عنوان اسلایدر", bool(str(_value(row, "homepage_slider_title_fa", "")).strip())),
                ("توضیح اسلایدر", bool(str(_value(row, "homepage_slider_description_fa", "")).strip())),
                ("Alt اسلایدر", bool(str(_value(row, "homepage_slider_alt_text", "")).strip())),
                ("عبارت هدف اسلایدر", bool(str(_value(row, "homepage_slider_focus_keyword", "")).strip())),
                ("عکس اسلایدر", bool(str(_value(row, "homepage_slider_image_url", "")).strip())),
                ("حالت نمایش عکس", bool(str(_value(row, "homepage_slider_presentation_mode", "product_fit")).strip())),
            ]
            slider_missing = [label for label, ok in checks if not ok]
        stages["slider"] = {
            "label": STAGE_LABELS["slider"],
            "ready": not slider_missing,
            "missing": slider_missing,
        }
        # Rebuild in canonical order so UI locking is deterministic.
        ordered = {key: stages.get(key, {"label": STAGE_LABELS[key], "ready": False, "missing": ["مرحله تعریف نشده"]}) for key in STAGE_ORDER}
        state["stages"] = ordered
        state["production_ready"] = all(item["ready"] for item in ordered.values())
        state["missing"] = [f"{STAGE_LABELS[key]}: {item}" for key in STAGE_ORDER for item in ordered[key]["missing"]]
        state["slider_enabled"] = slider_enabled
        return state

    readiness_module.evaluate_readiness = evaluate_readiness


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3b_guided_installed", False):
        return
    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_save = workspace_class.save
    original_select = workspace_class.select_section

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        self._phase49_3b_add_slider_stage()
        self._phase49_3b_add_footer()
        self._phase49_3b_add_title_ai()
        self._phase49_3b_load_media()
        self._phase49_3b_refresh_wizard()

    def _phase49_3b_add_slider_stage(self):
        if hasattr(self, "slider_tab"):
            return
        self.slider_tab = ttk.Frame(self.nb, padding=14)
        publish_index = self.nb.index(self.publish_tab)
        self.nb.insert(publish_index, self.slider_tab, text=STAGE_LABELS["slider"])

        # Hide the old slider blocks from final Publish; values are reused below.
        for child in list(self.publish_tab.winfo_children()):
            try:
                title = str(child.cget("text")) if isinstance(child, ttk.LabelFrame) else ""
            except Exception:
                title = ""
            if "اسلایدر" in title or "افکت سینمایی" in title:
                try:
                    child.pack_forget()
                except Exception:
                    try:
                        child.grid_remove()
                    except Exception:
                        pass

        rail = next(iter(self._section_buttons.values())).master
        button = tk.Button(
            rail,
            text=STAGE_LABELS["slider"],
            command=lambda: self.select_section("slider"),
            anchor="e",
            relief="flat",
            bd=0,
            bg="#0b2238",
            fg="#d9e4ee",
            activebackground="#123452",
            activeforeground="white",
            font=("Tahoma", 10, "bold"),
            padx=10,
            pady=9,
            cursor="hand2",
        )
        button.pack(fill="x", pady=2, before=self._section_buttons["publish"])
        rebuilt = {}
        for key in STAGE_ORDER:
            rebuilt[key] = button if key == "slider" else self._section_buttons[key]
        self._section_buttons = rebuilt

        ttk.Label(self.slider_tab, text="استودیوی اسلایدر صفحه اصلی", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            self.slider_tab,
            text="SEO اسلایدر، عکس Hero و نحوه قاب‌بندی محصول را اینجا تنظیم کن. برای کالای معمولی «نمایش کامل محصول» پیشنهاد می‌شود.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        general = ttk.LabelFrame(self.slider_tab, text="محتوا و انتشار در اسلایدر", padding=10, style="Card.TLabelframe")
        general.pack(fill="x", pady=5)
        general.columnconfigure(1, weight=1)
        ttk.Checkbutton(general, text="نمایش این محصول در اسلایدر صفحه اصلی", variable=self.slider_enabled_var).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Label(general, text="تصویر انتخاب‌شده").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(general, textvariable=self.slider_image_label_var, style="SubHeader.TLabel").grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(general, text="ترتیب").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(general, textvariable=self.slider_sort_var, width=12).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(general, text="عنوان کوتاه اسلایدر ★").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(general, textvariable=self.slider_title_fa_var).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(general, text="توضیح کوتاه اسلایدر ★").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        old_description = ""
        try:
            old_description = self._text_get(self.slider_description_text)
        except Exception:
            pass
        self.slider_description_text = tk.Text(general, height=4, wrap="word", undo=True)
        self.slider_description_text.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self._text_set(self.slider_description_text, old_description)
        ttk.Label(general, text="Alt تصویر ★").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(general, textvariable=self.slider_alt_text_var).grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        line = ttk.Frame(general)
        line.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        line.columnconfigure(1, weight=1); line.columnconfigure(3, weight=1)
        ttk.Label(line, text="متن دکمه").grid(row=0, column=0)
        ttk.Entry(line, textvariable=self.slider_button_text_var).grid(row=0, column=1, sticky="ew", padx=(5, 15))
        ttk.Label(line, text="Focus Keyword ★").grid(row=0, column=2)
        ttk.Entry(line, textvariable=self.slider_focus_keyword_var).grid(row=0, column=3, sticky="ew", padx=5)
        actions = ttk.Frame(general)
        actions.grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(actions, text="✨ تولید SEO اسلایدر با AI", command=lambda: self.generate_ai("commerce"), style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="پرکردن از محصول", command=self.fill_slider_copy_from_product).pack(side="left", padx=3)
        ttk.Button(actions, text="رفتن به گالری و انتخاب عکس", command=lambda: self.select_section("images")).pack(side="left", padx=3)

        media = ttk.LabelFrame(self.slider_tab, text="قاب‌بندی و نمایش تصویر Hero", padding=10, style="Card.TLabelframe")
        media.pack(fill="x", pady=5)
        for col in (1, 3, 5): media.columnconfigure(col, weight=1)
        self.hero_presentation_var = tk.StringVar(value=PRESENTATION_LABEL["product_fit"])
        self.hero_fit_var = tk.StringVar(value="contain")
        self.hero_focal_var = tk.StringVar(value="center")
        self.hero_scale_var = tk.StringVar(value="100")
        self.hero_x_var = tk.StringVar(value="50")
        self.hero_y_var = tk.StringVar(value="50")
        self.hero_background_var = tk.StringVar(value=BACKGROUND_LABEL["blur"])
        self.hero_background_color_var = tk.StringVar(value="#071827")
        self.hero_blur_var = tk.StringVar(value="18")
        self.hero_desktop_w_var = tk.StringVar(value="78")
        self.hero_desktop_h_var = tk.StringVar(value="88")
        self.hero_mobile_w_var = tk.StringVar(value="92")
        self.hero_mobile_h_var = tk.StringVar(value="72")

        ttk.Label(media, text="حالت ارائه").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Combobox(media, textvariable=self.hero_presentation_var, values=[x[1] for x in PRESENTATION], state="readonly").grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Label(media, text="Object Fit").grid(row=0, column=2, sticky="w", padx=4)
        ttk.Combobox(media, textvariable=self.hero_fit_var, values=["contain", "cover"], state="readonly", width=12).grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Label(media, text="نقطه تمرکز").grid(row=0, column=4, sticky="w", padx=4)
        ttk.Combobox(media, textvariable=self.hero_focal_var, values=["center", "top", "bottom", "left", "right"], state="readonly", width=12).grid(row=0, column=5, sticky="ew", padx=4)
        controls = [
            (1, "مقیاس %", self.hero_scale_var, 60, 140), (2, "موقعیت X %", self.hero_x_var, 0, 100),
            (3, "موقعیت Y %", self.hero_y_var, 0, 100), (4, "Blur px", self.hero_blur_var, 0, 60),
        ]
        for row_index, label, var, low, high in controls:
            ttk.Label(media, text=label).grid(row=row_index, column=0, sticky="w", padx=4, pady=4)
            ttk.Scale(media, from_=low, to=high, variable=var, orient="horizontal").grid(row=row_index, column=1, columnspan=2, sticky="ew", padx=4)
            ttk.Entry(media, textvariable=var, width=8).grid(row=row_index, column=3, sticky="w", padx=4)
        ttk.Label(media, text="پس‌زمینه").grid(row=1, column=4, sticky="w", padx=4)
        ttk.Combobox(media, textvariable=self.hero_background_var, values=[x[1] for x in BACKGROUND], state="readonly").grid(row=1, column=5, sticky="ew", padx=4)
        ttk.Label(media, text="رنگ پس‌زمینه").grid(row=2, column=4, sticky="w", padx=4)
        ttk.Entry(media, textvariable=self.hero_background_color_var).grid(row=2, column=5, sticky="ew", padx=4)
        ttk.Label(media, text="Desktop max W/H %").grid(row=3, column=4, sticky="w", padx=4)
        dbox = ttk.Frame(media); dbox.grid(row=3, column=5, sticky="ew")
        ttk.Entry(dbox, textvariable=self.hero_desktop_w_var, width=7).pack(side="left")
        ttk.Entry(dbox, textvariable=self.hero_desktop_h_var, width=7).pack(side="left", padx=4)
        ttk.Label(media, text="Mobile max W/H %").grid(row=4, column=4, sticky="w", padx=4)
        mbox = ttk.Frame(media); mbox.grid(row=4, column=5, sticky="ew")
        ttk.Entry(mbox, textvariable=self.hero_mobile_w_var, width=7).pack(side="left")
        ttk.Entry(mbox, textvariable=self.hero_mobile_h_var, width=7).pack(side="left", padx=4)
        preview = ttk.Frame(media)
        preview.grid(row=5, column=0, columnspan=6, sticky="ew", pady=(8, 0))
        ttk.Button(preview, text="🖥 پیش‌نمایش Desktop/Mobile", command=self.preview_hero_media, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Button(preview, text="▶ پیش‌نمایش Transition", command=self.preview_slider_effect).pack(side="left", padx=3)

        cinema = ttk.LabelFrame(self.slider_tab, text="افکت و زمان‌بندی", padding=10, style="Card.TLabelframe")
        cinema.pack(fill="x", pady=5)
        ttk.Label(cinema, text="افکت").pack(side="left", padx=4)
        ttk.Combobox(cinema, textvariable=self.slider_effect_var, values=list(getattr(self, "slider_effect_var", tk.StringVar()).get() and [] or []), width=25)
        # Reuse the already-created variables and EFFECT labels from Epic49 UI.
        from .epic49_server_slider_manager import EFFECTS
        ttk.Combobox(cinema, textvariable=self.slider_effect_var, values=[label for _code, label in EFFECTS], state="readonly", width=28).pack(side="left", padx=4)
        ttk.Label(cinema, text="Transition ms").pack(side="left", padx=(12, 4))
        ttk.Entry(cinema, textvariable=self.slider_transition_ms_var, width=9).pack(side="left")
        ttk.Label(cinema, text="Display ms").pack(side="left", padx=(12, 4))
        ttk.Entry(cinema, textvariable=self.slider_display_ms_var, width=9).pack(side="left")

    def _phase49_3b_add_footer(self):
        children = list(self.winfo_children())
        old_footer = children[-1] if children else None
        bar = ttk.LabelFrame(self, text="راهنمای مرحله", padding=(12, 7), style="Card.TLabelframe")
        kwargs = {"fill": "x", "padx": 12, "pady": (0, 6)}
        if old_footer is not None:
            kwargs["before"] = old_footer
        bar.pack(**kwargs)
        self._phase49_3b_help_var = tk.StringVar(value="")
        self._phase49_3b_required_var = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self._phase49_3b_help_var, wraplength=980, justify="right", style="SubHeader.TLabel").pack(side="right", fill="x", expand=True, padx=8)
        nav = ttk.Frame(bar); nav.pack(side="left")
        self._phase49_3b_prev = ttk.Button(nav, text="← مرحله قبل", command=self._phase49_3b_go_prev)
        self._phase49_3b_prev.pack(side="left", padx=3)
        self._phase49_3b_next = ttk.Button(nav, text="مرحله بعد برای انتشار →", command=self._phase49_3b_go_next, style="Primary.TButton")
        self._phase49_3b_next.pack(side="left", padx=3)
        ttk.Label(bar, textvariable=self._phase49_3b_required_var, foreground="#b91c1c", wraplength=480).pack(side="bottom", anchor="e", pady=(4, 0))

    def _phase49_3b_add_title_ai(self):
        holder = ttk.LabelFrame(self.quick_tab, text="کمک هوش مصنوعی مرحله ۱", padding=8, style="Card.TLabelframe")
        holder.pack(fill="x", pady=(8, 0))
        ttk.Button(holder, text="✨ ترجمه فقط عنوان فارسی", command=self.translate_title_only, style="Primary.TButton").pack(side="left", padx=3)
        ttk.Label(holder, text="فقط title_fa را تکمیل می‌کند و توضیحات/SEO/قیمت را تغییر نمی‌دهد.", style="SubHeader.TLabel").pack(side="left", padx=8)

    def translate_title_only(self):
        # Mature Windows composition routes every Product-AI action through the
        # final stage engine (OpenRouter-only + single-job guard). This also
        # catches Tk Buttons that captured this legacy callable before 3I.39.
        final_runner = getattr(self, "_phase49_3i39_run_stage_ai", None)
        if callable(final_runner):
            return final_runner("quick")

        row = self.db.product(self.product_id)
        source = str(_value(row, "source_title", "") or "").strip()
        if not source:
            messagebox.showinfo("3DPrintHub", "عنوان منبع خالی است.", parent=self); return
        provider = self.app._selected_ai_provider()
        key = self.app._ai_key(provider)
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {provider} تنظیم نشده است.", parent=self); return
        model = self.app.ai_model.get().strip()
        self.footer_status.set(f"ترجمه عنوان با {provider}…")
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {"title_fa": {"type": "string"}}, "required": ["title_fa"],
        }
        def work():
            client = AIProviderClient(provider, key, model, product_id=self.product_id)
            result, used = client.structured_response(
                instructions="Translate only the supplied 3D product title to fluent semantic Persian; transliteration of generic English words is forbidden. Twistmas Tree means a twisted/spiral Christmas tree and should be rendered as «درخت کریسمس اسپیرال» or a faithful Persian semantic equivalent. Preserve only true brand/model identifiers. Do not add marketing claims.",
                input_content=[{"type": "input_text", "text": source}],
                schema=schema, schema_name="title_fa_only", preferred_model=model,
            )
            return str(result.get("title_fa") or "").strip(), used
        def runner():
            try:
                title, used = work()
                if not title: raise RuntimeError("AI عنوان فارسی خالی برگرداند.")
                from .phase49_3i33_ai_core import title_quality_guard
                title_quality_guard(source, title)
                self.db.update_product(self.product_id, {"title_fa": title, "ai_provider": provider, "ai_model": used})
                audit_event("ai", "title_only", product_id=self.product_id, message=f"provider={provider} model={used}")
                self.after(0, lambda: (self.reload(), self._phase49_3b_refresh_wizard(), self.footer_status.set("عنوان فارسی ترجمه شد")))
            except Exception as exc:
                error_text = str(exc)
                self.after(
                    0,
                    lambda message=error_text: messagebox.showerror(
                        "3DPrintHub",
                        f"ترجمه عنوان ناموفق بود:\n{message}",
                        parent=self,
                    ),
                )
        threading.Thread(target=runner, daemon=True).start()

    def _phase49_3b_load_media(self):
        row = self.db.product(self.product_id)
        if row is None or not hasattr(self, "hero_presentation_var"): return
        self.hero_presentation_var.set(PRESENTATION_LABEL.get(str(_value(row, "homepage_slider_presentation_mode", "product_fit")), PRESENTATION_LABEL["product_fit"]))
        self.hero_fit_var.set(str(_value(row, "homepage_slider_object_fit", "contain")))
        self.hero_focal_var.set(str(_value(row, "homepage_slider_focal_position", "center")))
        self.hero_scale_var.set(str(_bounded(_value(row, "homepage_slider_image_scale_percent", 100), 100, 60, 140)))
        self.hero_x_var.set(str(_bounded(_value(row, "homepage_slider_position_x_percent", 50), 50, 0, 100)))
        self.hero_y_var.set(str(_bounded(_value(row, "homepage_slider_position_y_percent", 50), 50, 0, 100)))
        self.hero_background_var.set(BACKGROUND_LABEL.get(str(_value(row, "homepage_slider_background_mode", "blur")), BACKGROUND_LABEL["blur"]))
        self.hero_background_color_var.set(str(_value(row, "homepage_slider_background_color", "#071827")))
        self.hero_blur_var.set(str(_bounded(_value(row, "homepage_slider_background_blur_px", 18), 18, 0, 60)))
        self.hero_desktop_w_var.set(str(_bounded(_value(row, "homepage_slider_desktop_max_width_percent", 78), 78, 30, 100)))
        self.hero_desktop_h_var.set(str(_bounded(_value(row, "homepage_slider_desktop_max_height_percent", 88), 88, 30, 100)))
        self.hero_mobile_w_var.set(str(_bounded(_value(row, "homepage_slider_mobile_max_width_percent", 92), 92, 30, 100)))
        self.hero_mobile_h_var.set(str(_bounded(_value(row, "homepage_slider_mobile_max_height_percent", 72), 72, 30, 100)))

    def _phase49_3b_media_values(self):
        presentation = PRESENTATION_CODE.get(self.hero_presentation_var.get(), "product_fit")
        fit = self.hero_fit_var.get().strip() if self.hero_fit_var.get().strip() in {"contain", "cover"} else ("cover" if presentation == "full_bleed" else "contain")
        return {
            "homepage_slider_presentation_mode": presentation,
            "homepage_slider_object_fit": fit,
            "homepage_slider_focal_position": self.hero_focal_var.get().strip() or "center",
            "homepage_slider_image_scale_percent": _bounded(self.hero_scale_var.get(), 100, 60, 140),
            "homepage_slider_position_x_percent": _bounded(self.hero_x_var.get(), 50, 0, 100),
            "homepage_slider_position_y_percent": _bounded(self.hero_y_var.get(), 50, 0, 100),
            "homepage_slider_background_mode": BACKGROUND_CODE.get(self.hero_background_var.get(), "blur"),
            "homepage_slider_background_color": self.hero_background_color_var.get().strip()[:24] or "#071827",
            "homepage_slider_background_blur_px": _bounded(self.hero_blur_var.get(), 18, 0, 60),
            "homepage_slider_desktop_max_width_percent": _bounded(self.hero_desktop_w_var.get(), 78, 30, 100),
            "homepage_slider_desktop_max_height_percent": _bounded(self.hero_desktop_h_var.get(), 88, 30, 100),
            "homepage_slider_mobile_max_width_percent": _bounded(self.hero_mobile_w_var.get(), 92, 30, 100),
            "homepage_slider_mobile_max_height_percent": _bounded(self.hero_mobile_h_var.get(), 72, 30, 100),
        }

    def reload(self):
        original_reload(self)
        if hasattr(self, "hero_presentation_var"):
            self._phase49_3b_load_media()
            self._phase49_3b_refresh_wizard()

    def save(self, silent=False):
        ok = original_save(self, silent=True)
        if not ok: return False
        if hasattr(self, "hero_presentation_var"):
            self.db.update_product(self.product_id, self._phase49_3b_media_values())
        if hasattr(self, "_phase49_3b_help_var"):
            self._phase49_3b_refresh_wizard()
        if not silent: self.footer_status.set("تمام اطلاعات مرحله و تنظیمات Hero ذخیره شد")
        return True

    def select_section(self, key: str):
        if key == "slider" and hasattr(self, "slider_tab"):
            target = self.slider_tab
        else:
            target = None
        # Lock future steps based on the first incomplete stage, but always allow going back.
        state = getattr(self, "_phase49_readiness_state", None)
        if state and key in STAGE_ORDER:
            first_incomplete = next((i for i, stage_key in enumerate(STAGE_ORDER) if not _stage_data_ready(state["stages"].get(stage_key, {}))), len(STAGE_ORDER) - 1)
            current = self._phase49_3b_current_key(default="quick")
            current_index = STAGE_ORDER.index(current)
            requested = STAGE_ORDER.index(key)
            max_allowed = max(current_index, first_incomplete)
            if requested > max_allowed:
                messagebox.showinfo("3DPrintHub", "این مرحله هنوز قفل است. ابتدا مرحله قبلی را کامل کن.", parent=self)
                return
        if target is not None:
            self.nb.select(target)
            for stage_key, button in self._section_buttons.items():
                active = stage_key == key
                button.configure(bg="#c99a2e" if active else "#0b2238", fg="#071827" if active else "#d9e4ee")
        else:
            original_select(self, key)
        self._phase49_3b_refresh_wizard()

    def _phase49_3b_current_key(self, default="quick"):
        try:
            selected = self.nb.select()
            mapping = {
                str(self.quick_tab): "quick", str(self.commerce_tab): "commerce", str(self.images_tab): "images",
                str(self.content_tab): "content", str(self.specs_tab): "specs", str(self.slider_tab): "slider", str(self.publish_tab): "publish",
            }
            return mapping.get(str(selected), default)
        except Exception:
            return default

    def _phase49_3b_refresh_wizard(self):
        if not hasattr(self, "_phase49_readiness_state") or not hasattr(self, "_phase49_3b_help_var"): return
        try:
            self._phase49_refresh_readiness()
        except Exception:
            pass
        state = getattr(self, "_phase49_readiness_state", {})
        current = self._phase49_3b_current_key()
        stage = state.get("stages", {}).get(current, {"ready": False, "missing": []})
        self._phase49_3b_help_var.set(STAGE_HELP[current])
        missing = _stage_data_missing(stage)
        self._phase49_3b_required_var.set("" if not missing else "★ الزامی برای ادامه: " + " • ".join(missing))
        index = STAGE_ORDER.index(current)
        self._phase49_3b_prev.configure(state="disabled" if index == 0 else "normal")
        if index == len(STAGE_ORDER) - 1:
            self._phase49_3b_next.configure(text="💾 ذخیره نهایی", state="normal", command=lambda: self.save())
        else:
            self._phase49_3b_next.configure(text="مرحله بعد برای انتشار →", state="normal" if _stage_data_ready(stage) else "disabled", command=self._phase49_3b_go_next)
        first_incomplete = next((i for i, key in enumerate(STAGE_ORDER) if not _stage_data_ready(state.get("stages", {}).get(key, {}))), len(STAGE_ORDER))
        for idx, key in enumerate(STAGE_ORDER):
            button = self._section_buttons.get(key)
            if button is None: continue
            data_ready = _stage_data_ready(state.get("stages", {}).get(key, {}))
            icon = "✅" if data_ready else ("🔒" if idx > first_incomplete else "❌ ★")
            try:
                button.configure(text=f"{icon} {STAGE_LABELS[key]}", state="disabled" if idx > max(first_incomplete, index) else "normal")
            except Exception:
                pass

        # Final mature Windows layers may replace the navigation action with
        # persist -> validate -> finalize -> advance. Older callbacks can be
        # captured before those layers finish installing, so the base painter
        # must always give the final layer one last chance to restore its button.
        final_sync = getattr(self, "_phase49_3i39_sync_footer_actions", None)
        if callable(final_sync):
            try:
                final_sync()
            except Exception:
                pass

    def _phase49_3b_go_prev(self):
        current = self._phase49_3b_current_key(); index = STAGE_ORDER.index(current)
        if index > 0: self.select_section(STAGE_ORDER[index - 1])

    def _phase49_3b_go_next(self):
        # On the mature seven-stage workspace the authoritative action is the
        # 3I.39/3I.36 confirm path. Delegate even if an older Tk button captured
        # this method before the final footer was rebound.
        confirm = getattr(self, "_phase49_3i39_confirm_current_stage", None)
        if callable(confirm):
            return confirm()

        current = self._phase49_3b_current_key(); index = STAGE_ORDER.index(current)
        # Legacy fallback must persist current UI before reading readiness.
        # The previous read-before-save order trapped valid manual edits.
        if not self.save(silent=True):
            return False
        self._phase49_3b_refresh_wizard()
        state = getattr(self, "_phase49_readiness_state", {})
        if not _stage_data_ready(state.get("stages", {}).get(current, {})):
            return False
        if index < len(STAGE_ORDER) - 1:
            self.select_section(STAGE_ORDER[index + 1])
        return True

    def _preview_image_path(self):
        selected_url = str(_value(self.db.product(self.product_id), "homepage_slider_image_url", "") or "")
        cards = list(getattr(self, "_gallery_cards", []) or [])
        ordered = sorted(cards, key=lambda item: 0 if item.get("url") == selected_url else 1)
        for item in ordered:
            local = str(item.get("local") or "").strip()
            if local and Path(local).is_file(): return local
        return ""

    def preview_hero_media(self):
        path = self._preview_image_path()
        if not path:
            messagebox.showinfo("3DPrintHub", "ابتدا عکس Hero را از گالری انتخاب کن و مطمئن شو فایل محلی موجود است.", parent=self); return
        try: source = Image.open(path).convert("RGB")
        except Exception as exc: messagebox.showerror("3DPrintHub", str(exc), parent=self); return
        values = self._phase49_3b_media_values()
        def render(size, max_w, max_h):
            w, h = size; bg_mode = values["homepage_slider_background_mode"]
            if bg_mode in {"blur", "image"}:
                bg = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS)
                if bg_mode == "blur": bg = bg.filter(ImageFilter.GaussianBlur(values["homepage_slider_background_blur_px"]))
                bg = Image.blend(bg, Image.new("RGB", size, values["homepage_slider_background_color"]), 0.22)
            elif bg_mode == "gradient":
                bg = Image.new("RGB", size, values["homepage_slider_background_color"])
                overlay = Image.new("RGB", size, "#243447"); bg = Image.blend(bg, overlay, 0.38)
            else: bg = Image.new("RGB", size, values["homepage_slider_background_color"])
            fit = values["homepage_slider_object_fit"]
            if fit == "cover": foreground = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS)
            else:
                box_w = int(w * max_w / 100); box_h = int(h * max_h / 100)
                foreground = source.copy(); foreground.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
                scale = values["homepage_slider_image_scale_percent"] / 100
                foreground = foreground.resize((max(1, int(foreground.width * scale)), max(1, int(foreground.height * scale))), Image.Resampling.LANCZOS)
                x = int((w - foreground.width) * values["homepage_slider_position_x_percent"] / 100)
                y = int((h - foreground.height) * values["homepage_slider_position_y_percent"] / 100)
                bg.paste(foreground, (x, y))
                foreground = bg
            if values["homepage_slider_presentation_mode"] == "framed":
                border = 10; frame = Image.new("RGB", size, "#071827"); inner = foreground.resize((w - border*2, h - border*2)); frame.paste(inner, (border, border)); foreground = frame
            return foreground
        desktop = render((960, 540), values["homepage_slider_desktop_max_width_percent"], values["homepage_slider_desktop_max_height_percent"])
        mobile = render((390, 640), values["homepage_slider_mobile_max_width_percent"], values["homepage_slider_mobile_max_height_percent"])
        win = tk.Toplevel(self); win.title("پیش‌نمایش Hero — Desktop / Mobile"); win.configure(bg="#071827")
        d = ImageTk.PhotoImage(desktop); m = ImageTk.PhotoImage(mobile)
        win._photos = (d, m)
        tk.Label(win, image=d, bg="#071827").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(win, image=m, bg="#071827").grid(row=0, column=1, padx=10, pady=10)
        tk.Label(win, text="Desktop", bg="#071827", fg="white").grid(row=1, column=0)
        tk.Label(win, text="Mobile", bg="#071827", fg="white").grid(row=1, column=1)

    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class.select_section = select_section
    for name, func in list(locals().items()):
        if name.startswith("_phase49_3b_") or name in {"translate_title_only", "preview_hero_media"}:
            if callable(func): setattr(workspace_class, name, func)
    workspace_class._phase49_3b_guided_installed = True
