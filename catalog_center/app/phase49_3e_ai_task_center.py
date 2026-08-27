from __future__ import annotations

import json
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.parse import urlsplit

from . import phase49_3c_image_pipeline as image_pipeline
from .openai_content import AIContentService
from .phase49_3c_persian_content import has_persian_editorial_text
from .phase49_diagnostics import audit_event
from .phase49_readiness_wizard import selected_color_names, selected_material_names


AI_TASKS = (
    ("persian_content", "متن فارسی محصول", "content"),
    ("product_seo", "سئو محصول", "content"),
    ("image_seo", "سئو و متادیتای تصاویر", "images"),
    ("materials", "پیشنهاد متریال AI", "commerce"),
    ("slider_seo", "سئو اسلایدر", "slider"),
)

OVERRIDE_FIELDS = (
    "seo_filename",
    "alt_text",
    "title",
    "caption",
    "keywords",
    "creator",
    "source_page_url",
    "license_name",
    "license_url",
)


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        value = row.get(key, default)
    else:
        try:
            value = row[key]
        except Exception:
            value = default
    return default if value is None else value


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _nonempty(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value not in (None, "")


def _persian_list_ready(value, minimum: int = 1) -> bool:
    values = _json_list(value)
    return len(values) >= minimum and all(has_persian_editorial_text(item) for item in values)


def evaluate_ai_tasks(row) -> list[dict]:
    selected = image_pipeline.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
    tasks: list[dict] = []

    content_missing = []
    for label, key in (
        ("عنوان فارسی", "title_fa"),
        ("توضیح کوتاه فارسی", "short_description_fa"),
        ("توضیح کامل فارسی", "description_fa"),
        ("توضیح کاربرد محصول", "use_description"),
    ):
        if not has_persian_editorial_text(_row_value(row, key, "")):
            content_missing.append(label)
    tasks.append({
        "key": "persian_content",
        "label": "متن فارسی محصول",
        "stage": "content",
        "status": "done" if not content_missing else "missing",
        "missing": content_missing,
    })

    seo_missing = []
    if not has_persian_editorial_text(_row_value(row, "seo_title_fa", "")):
        seo_missing.append("SEO Title فارسی")
    if not has_persian_editorial_text(_row_value(row, "seo_description_fa", "")):
        seo_missing.append("SEO Description فارسی")
    if not _persian_list_ready(_row_value(row, "keywords_json", "[]"), minimum=3):
        seo_missing.append("عبارت‌های هدف SEO")
    if not _persian_list_ready(_row_value(row, "tags_fa_json", "[]")):
        seo_missing.append("تگ‌های فارسی")
    if not _persian_list_ready(_row_value(row, "hashtags_fa_json", "[]")):
        seo_missing.append("هشتگ‌های فارسی")
    tasks.append({
        "key": "product_seo",
        "label": "سئو محصول",
        "stage": "content",
        "status": "done" if not seo_missing else "missing",
        "missing": seo_missing,
    })

    image_missing = []
    if not selected:
        image_missing.append("حداقل یک تصویر برای سایت")
    else:
        alts = [str(item or "").strip() for item in _json_list(_row_value(row, "image_alt_texts_json", "[]"))]
        if len(alts) < len(selected) or any(not has_persian_editorial_text(item) for item in alts[: len(selected)]):
            image_missing.append("Alt فارسی همه تصاویر")
        image_missing.extend(image_pipeline.image_metadata_missing(row))
    image_missing = list(dict.fromkeys(image_missing))
    tasks.append({
        "key": "image_seo",
        "label": "سئو و متادیتای تصاویر",
        "stage": "images",
        "status": "done" if not image_missing else "missing",
        "missing": image_missing,
    })

    material_recs = _json_list(_row_value(row, "material_recommendations_json", "[]"))
    material_missing = [] if material_recs else ["پیشنهاد متریال AI"]
    tasks.append({
        "key": "materials",
        "label": "پیشنهاد متریال AI",
        "stage": "commerce",
        "status": "done" if not material_missing else "missing",
        "missing": material_missing,
    })

    slider_enabled = bool(int(_row_value(row, "homepage_slider_enabled", 0) or 0))
    slider_missing = []
    if slider_enabled:
        for label, key in (
            ("عنوان اسلایدر", "homepage_slider_title_fa"),
            ("توضیح اسلایدر", "homepage_slider_description_fa"),
            ("Alt اسلایدر", "homepage_slider_alt_text"),
            ("عبارت هدف اسلایدر", "homepage_slider_focus_keyword"),
        ):
            if not has_persian_editorial_text(_row_value(row, key, "")):
                slider_missing.append(label)
        if not str(_row_value(row, "homepage_slider_image_url", "") or "").strip():
            slider_missing.append("عکس اسلایدر")
    tasks.append({
        "key": "slider_seo",
        "label": "سئو اسلایدر",
        "stage": "slider",
        "status": "skipped" if not slider_enabled else ("done" if not slider_missing else "missing"),
        "missing": slider_missing,
    })
    return tasks


def build_ai_updates(row, pack: dict, *, scope: str = "all") -> dict:
    """Return only missing editorial fields; manual/operator values are never overwritten."""
    updates: dict = {}

    def put_text(db_key: str, pack_key: str, *, require_persian: bool = True):
        if str(_row_value(row, db_key, "") or "").strip():
            return
        value = str(pack.get(pack_key) or "").strip()
        if value and (not require_persian or has_persian_editorial_text(value)):
            updates[db_key] = value

    def put_list(db_key: str, pack_key: str, *, minimum: int = 1):
        if _json_list(_row_value(row, db_key, "[]")):
            return
        values = [str(item or "").strip() for item in (pack.get(pack_key) or []) if str(item or "").strip()]
        if len(values) >= minimum:
            updates[db_key] = json.dumps(values, ensure_ascii=False)

    image_scope = str(scope or "all") == "images"
    if not image_scope:
        put_text("title_fa", "title_fa")
        put_text("short_description_fa", "short_description_fa")
        put_text("description_fa", "description_fa")
        put_text("use_description", "use_description_fa")
        put_list("categories_fa_json", "categories_fa")
        put_list("specs_fa_json", "specs_fa")
        put_list("sales_bullets_json", "sales_bullets")
        put_text("social_caption_fa", "social_caption_fa")
        # Material/filament selection is operator-owned in 3I.35+.

    # Product SEO is also an input to image SEO metadata, so images scope may fill it when absent.
    put_text("seo_title_fa", "seo_title_fa")
    put_text("seo_description_fa", "seo_description_fa")
    put_list("keywords_json", "target_keywords_fa", minimum=3)
    put_list("tags_fa_json", "tags_fa")
    put_list("hashtags_fa_json", "hashtags_fa")
    put_list("image_alt_texts_json", "image_alt_texts")

    slider_enabled = bool(int(_row_value(row, "homepage_slider_enabled", 0) or 0))
    slider = pack.get("homepage_slider_seo") if isinstance(pack.get("homepage_slider_seo"), dict) else {}
    if not image_scope and slider_enabled:
        for db_key, pack_key in (
            ("homepage_slider_title_fa", "title_fa"),
            ("homepage_slider_description_fa", "description_fa"),
            ("homepage_slider_alt_text", "image_alt_fa"),
            ("homepage_slider_button_text", "button_text_fa"),
            ("homepage_slider_focus_keyword", "focus_keyword_fa"),
        ):
            if not str(_row_value(row, db_key, "") or "").strip():
                value = str(slider.get(pack_key) or "").strip()
                if value:
                    updates[db_key] = value
        if not str(_row_value(row, "homepage_slider_image_url", "") or "").strip():
            primary = str(_row_value(row, "primary_image_url", "") or "").strip()
            selected = _json_list(_row_value(row, "selected_images_json", "[]"))
            image_url = primary or (str(selected[0]) if selected else "")
            if image_url:
                updates["homepage_slider_image_url"] = image_url

    if not image_scope:
        try:
            updates["content_pack_json"] = json.dumps(pack, ensure_ascii=False)
        except Exception:
            pass
    return updates


def _safe_seo_filename(value: str, fallback: str) -> str:
    name = str(value or "").strip().lower()
    if name.endswith(".webp"):
        name = name[:-5]
    name = re.sub(r"[^a-z0-9]+", "-", name).strip("-")[:100]
    if not name:
        fallback_stem = Path(str(fallback or "product-image.webp")).stem.lower()
        name = re.sub(r"[^a-z0-9]+", "-", fallback_stem).strip("-")[:100] or "product-image"
    return name + ".webp"


def merge_operator_overrides(base: dict, existing: dict) -> dict:
    result = dict(base or {})
    fields = [field for field in (existing.get("operator_override_fields") or []) if field in OVERRIDE_FIELDS]
    for field in fields:
        value = existing.get(field)
        if field == "keywords":
            value = [str(item or "").strip() for item in (value or []) if str(item or "").strip()]
        if value not in (None, "", []):
            result[field] = value
    if fields:
        result["operator_override_fields"] = fields
        result["operator_override"] = True
    return result


def install(workspace_class, readiness_module) -> None:
    if getattr(workspace_class, "_phase49_3e_task_center_installed", False):
        return

    if not getattr(image_pipeline, "_phase49_3e_override_support_installed", False):
        original_build_metadata = image_pipeline.build_image_metadata

        def build_image_metadata(row, url, local_file, index, db):
            base = original_build_metadata(row, url, local_file, index, db)
            existing_items = _json_list(_row_value(row, image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
            existing = next(
                (
                    item for item in existing_items
                    if isinstance(item, dict) and str(item.get("source_url") or "") == str(url or "")
                ),
                {},
            )
            return merge_operator_overrides(base, existing)

        image_pipeline.build_image_metadata = build_image_metadata
        image_pipeline._phase49_3e_override_support_installed = True

    original_init = workspace_class.__init__
    original_live_refresh = getattr(workspace_class, "_phase49_3c_refresh_live", None)
    original_stage_ai = getattr(workspace_class, "_phase49_3c_stage_ai", None)

    def __init__(self, app, product_id: int):
        self._phase49_3e_busy = False
        self._phase49_3e_last_error = ""
        original_init(self, app, product_id)
        self._phase49_3e_add_image_tools()
        self._phase49_3e_add_content_image_action()
        self._phase49_3e_add_task_panel()
        self.after(80, self._phase49_3e_refresh_tasks)

    def _phase49_3e_add_image_tools(self):
        if not hasattr(self, "images_tab"):
            return
        children = list(self.images_tab.winfo_children())
        before = children[-1] if children else None
        frame = ttk.LabelFrame(
            self.images_tab,
            text="هوش مصنوعی و SEO تصاویر",
            padding=8,
            style="Card.TLabelframe",
        )
        kwargs = {"fill": "x", "pady": (0, 8)}
        if before is not None:
            kwargs["before"] = before
        frame.pack(**kwargs)
        self._phase49_3e_image_status = tk.StringVar(value="وضعیت سئو تصاویر در حال بررسی است…")
        ttk.Label(frame, textvariable=self._phase49_3e_image_status, style="SubHeader.TLabel").pack(side="right", padx=6)
        ttk.Button(
            frame,
            text="✨ تکمیل AI سئو تصاویر",
            command=self._phase49_3e_image_ai,
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            frame,
            text="✏ ویرایش دستی متادیتای تصاویر",
            command=self._phase49_3e_open_image_editor,
        ).pack(side="left", padx=3)
        ttk.Button(
            frame,
            text="🖼 نهایی‌سازی فایل‌های SEO",
            command=self.phase49_3c_finalize_images,
        ).pack(side="left", padx=3)

    def _phase49_3e_add_content_image_action(self):
        if not hasattr(self, "content_tab"):
            return
        children = list(self.content_tab.winfo_children())
        toolbar = children[0] if children and isinstance(children[0], ttk.Frame) else None
        if toolbar is not None:
            ttk.Button(
                toolbar,
                text="🖼 سئو تصاویر با AI",
                command=self._phase49_3e_image_ai,
            ).pack(side="left", padx=3)

    def _phase49_3e_add_task_panel(self):
        buttons = getattr(self, "_section_buttons", {})
        if not buttons:
            return
        rail = next(iter(buttons.values())).master
        frame = tk.Frame(rail, bg="#0b2238", highlightbackground="#29445e", highlightthickness=1)
        frame.pack(fill="x", pady=(6, 4))
        tk.Label(
            frame,
            text="وظایف هوش مصنوعی و SEO",
            bg="#0b2238",
            fg="#f6d77a",
            font=("Tahoma", 9, "bold"),
        ).pack(anchor="e", padx=6, pady=(5, 2))
        self._phase49_3e_tasks = tk.Listbox(
            frame,
            height=6,
            bg="#102c46",
            fg="#ffffff",
            selectbackground="#c99a2e",
            selectforeground="#071827",
            bd=0,
            highlightthickness=0,
            font=("Tahoma", 8),
        )
        self._phase49_3e_tasks.pack(fill="x", padx=5, pady=(0, 4))
        self._phase49_3e_tasks.bind("<Double-Button-1>", lambda _event: self._phase49_3e_guide_selected_task())
        actions = ttk.Frame(frame)
        actions.pack(fill="x", padx=4, pady=(0, 5))
        ttk.Button(
            actions,
            text="✨ انجام وظایف ناقص AI",
            command=self._phase49_3e_run_all_ai,
            style="Success.TButton",
        ).pack(fill="x", pady=2)
        ttk.Button(
            actions,
            text="راهنمای تکمیل دستی",
            command=self._phase49_3e_guide_selected_task,
        ).pack(fill="x", pady=2)
        self._phase49_3e_task_records = []

    def _phase49_3e_refresh_tasks(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        tasks = evaluate_ai_tasks(row)
        self._phase49_3e_task_records = tasks
        if hasattr(self, "_phase49_3e_tasks"):
            self._phase49_3e_tasks.delete(0, "end")
            for task in tasks:
                icon = "✅" if task["status"] == "done" else ("➖" if task["status"] == "skipped" else "❌")
                suffix = "" if not task["missing"] else " • " + "، ".join(task["missing"][:2])
                self._phase49_3e_tasks.insert("end", f"{icon} {task['label']}{suffix}")
        image_task = next((task for task in tasks if task["key"] == "image_seo"), None)
        if hasattr(self, "_phase49_3e_image_status") and image_task:
            if image_task["status"] == "done":
                self._phase49_3e_image_status.set("✅ سئو و Metadata همه تصاویر منتخب کامل است")
            else:
                self._phase49_3e_image_status.set("❌ " + " • ".join(image_task["missing"][:3]))

        # Navigation is never a prison: all stages remain editable. Only Next/Production stay gated.
        for button in getattr(self, "_section_buttons", {}).values():
            try:
                button.configure(state="normal")
            except Exception:
                pass
        local_button = getattr(self, "_phase49_local_button", None)
        if local_button is not None:
            try:
                local_button.state(["!disabled"])
            except Exception:
                pass

    def _phase49_3c_refresh_live(self):
        if original_live_refresh is not None:
            original_live_refresh(self)
        if hasattr(self, "_phase49_3e_task_records"):
            self._phase49_3e_refresh_tasks()

    def _phase49_3c_stage_ai(self):
        current = self._phase49_3b_current_key(default="quick")
        if current == "images":
            return self._phase49_3e_image_ai()
        if original_stage_ai is not None:
            return original_stage_ai(self)
        return self._phase49_3e_run_all_ai()

    def _phase49_3e_provider(self):
        provider = self.app._selected_ai_provider()
        key = self.app._ai_key(provider)
        model = str(self.app.ai_model.get() if hasattr(self.app, "ai_model") else "").strip()
        return provider, key, model

    def _phase49_3e_run_ai(self, scope: str):
        if self._phase49_3e_busy or getattr(self, "_ai_busy", False):
            self.footer_status.set("یک درخواست هوش مصنوعی در حال اجرا است.")
            return
        provider, key, model = self._phase49_3e_provider()
        if not key:
            messagebox.showwarning(
                "3DPrintHub",
                f"API Key برای {provider} تنظیم نشده است. ابتدا Provider/Model فعال را در بخش هوش مصنوعی تنظیم و تست کن.",
                parent=self,
            )
            return
        # Product AI reads the last durable Product state; it must not commit
        # unrelated UI/profile/commerce fields before the request.
        row = self.db.product(self.product_id)
        images = image_pipeline.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
        source = dict(self._source_for_ai() or {})
        source["selected_materials"] = selected_material_names(row)
        source["selected_colors"] = selected_color_names(row)
        categories = self.app.get_all_categories()
        self._phase49_3e_busy = True
        self.footer_status.set(
            "در حال تکمیل سئو و متادیتای تصاویر…" if scope == "images" else "در حال انجام وظایف ناقص هوش مصنوعی…"
        )
        audit_event(
            "ai",
            "task_center_start",
            product_id=self.product_id,
            message=f"scope={scope} provider={provider} model={model}",
            source_file="catalog_center/app/phase49_3e_ai_task_center.py",
        )

        def worker():
            try:
                pack = AIContentService(key, model, provider, product_id=self.product_id).enrich_product(
                    source,
                    categories,
                    image_count=len(images),
                    image_urls=images,
                    mode="commerce",
                )
                self.after(0, lambda: self._phase49_3e_apply_ai_result(pack, scope))
            except Exception as exc:
                self._phase49_3e_last_error = f"{type(exc).__name__}: {exc}"
                audit_event(
                    "ai",
                    "task_center_error",
                    product_id=self.product_id,
                    status="error",
                    level="ERROR",
                    message=f"scope={scope} provider={provider} model={model}: {exc}",
                    source_file="catalog_center/app/phase49_3e_ai_task_center.py",
                )
                self.after(0, lambda: messagebox.showerror("خطای دستیار هوش مصنوعی", str(exc), parent=self))
                self.after(0, lambda: self.footer_status.set("AI نتوانست وظیفه را کامل کند؛ مورد قرمز را باز کن یا از تکمیل دستی استفاده کن."))
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3e_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3e_run_all_ai(self):
        return self._phase49_3e_run_ai("all")

    def _phase49_3e_image_ai(self):
        return self._phase49_3e_run_ai("images")

    def _phase49_3e_apply_ai_result(self, pack: dict, scope: str):
        row = self.db.product(self.product_id)
        if row is None:
            return
        updates = build_ai_updates(row, pack, scope=scope)
        if updates:
            self.db.update_product(self.product_id, updates)
        finalize_error = ""
        row_after = self.db.product(self.product_id)
        selected = image_pipeline.cap_unique_urls(_json_list(_row_value(row_after, "selected_images_json", "[]")))
        if selected:
            try:
                image_pipeline.finalize_selected_images(self.db, self.product_id)
            except Exception as exc:
                finalize_error = f"{type(exc).__name__}: {exc}"
                audit_event(
                    "images",
                    "ai_seo_finalize_error",
                    product_id=self.product_id,
                    status="error",
                    level="ERROR",
                    message=finalize_error,
                    source_file="catalog_center/app/phase49_3e_ai_task_center.py",
                )
        try:
            self.reload()
        except Exception:
            pass
        self._phase49_3e_refresh_tasks()
        current = self.db.product(self.product_id)
        tasks = evaluate_ai_tasks(current)
        remaining = [task for task in tasks if task["status"] == "missing"]
        audit_event(
            "ai",
            "task_center_complete",
            product_id=self.product_id,
            message=f"scope={scope} changed={','.join(sorted(updates))} remaining={len(remaining)}",
            source_file="catalog_center/app/phase49_3e_ai_task_center.py",
            detail={"scope": scope, "changed_fields": sorted(updates), "remaining": [task["key"] for task in remaining]},
        )
        if finalize_error:
            messagebox.showwarning(
                "3DPrintHub — AI انجام شد، تصویر نیاز به بررسی دارد",
                "محتوای قابل‌تولید توسط AI ثبت شد، اما نهایی‌سازی فایل تصویر کامل نشد:\n\n"
                + finalize_error
                + "\n\nاز «ویرایش دستی متادیتای تصاویر» استفاده کن و سپس نهایی‌سازی را بزن.",
                parent=self,
            )
        elif remaining:
            missing_text = []
            for task in remaining[:5]:
                missing_text.append(f"{task['label']}: " + "، ".join(task["missing"][:4]))
            messagebox.showwarning(
                "3DPrintHub — برخی وظایف هنوز ناقص‌اند",
                "AI هر چیزی را که از داده واقعی قابل تکمیل بود انجام داد. موارد باقی‌مانده:\n\n- "
                + "\n- ".join(missing_text)
                + "\n\nروی Task قرمز دوبار کلیک کن یا «راهنمای تکمیل دستی» را بزن.",
                parent=self,
            )
        else:
            messagebox.showinfo("3DPrintHub", "✅ تمام وظایف AI/SEO قابل‌اجرا برای این محصول کامل شد.", parent=self)

    def _phase49_3e_selected_task(self):
        records = getattr(self, "_phase49_3e_task_records", []) or []
        widget = getattr(self, "_phase49_3e_tasks", None)
        if not records:
            return None
        if widget is None:
            return records[0]
        selection = widget.curselection()
        return records[int(selection[0])] if selection else next((task for task in records if task["status"] == "missing"), records[0])

    def _phase49_3e_guide_selected_task(self):
        task = self._phase49_3e_selected_task()
        if not task:
            return
        if task["key"] == "image_seo":
            self.select_section("images")
            if task["missing"]:
                self.footer_status.set("سئو تصاویر ناقص است؛ AI تصاویر یا ویرایش دستی Metadata را اجرا کن.")
            return self._phase49_3e_open_image_editor()
        try:
            self.select_section(task["stage"])
        except Exception:
            pass
        if task["status"] == "skipped":
            self.footer_status.set(f"{task['label']} اختیاری است و چون قابلیت مربوطه فعال نیست، نیاز به تکمیل ندارد.")
            return
        message = (
            f"{task['label']}\n\n"
            + ("موارد ناقص:\n- " + "\n- ".join(task["missing"]) if task["missing"] else "این وظیفه کامل است.")
            + "\n\nAI فقط فیلدهای خالی قابل‌استنتاج را پر می‌کند و داده دستی را overwrite نمی‌کند."
        )
        messagebox.showinfo("راهنمای تکمیل", message, parent=self)

    def _phase49_3e_open_image_editor(self):
        row = self.db.product(self.product_id)
        selected = image_pipeline.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")))
        if not selected:
            messagebox.showwarning("3DPrintHub", "ابتدا حداقل یک تصویر را برای سایت انتخاب کن.", parent=self)
            return
        items = _json_list(_row_value(row, image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
        by_url = {str(item.get("source_url") or ""): dict(item) for item in items if isinstance(item, dict)}

        win = tk.Toplevel(self)
        win.title("ویرایش دستی SEO و Metadata تصاویر")
        win.geometry("920x720")
        win.transient(self)
        outer = ttk.Frame(win, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="SEO و Metadata تصویر — تکمیل دستی اپراتور", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="مقادیر ثبت‌شده اپراتور در نهایی‌سازی بعدی حفظ می‌شوند. Creator/Source/License را فقط بر اساس منبع واقعی وارد کن.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(2, 8))

        index_var = tk.StringVar()
        labels = []
        for idx, url in enumerate(selected, start=1):
            meta = by_url.get(url) or {}
            filename = str(meta.get("seo_filename") or Path(urlsplit(url).path).name or f"image-{idx}")
            labels.append(f"{idx}. {filename}")
        selector = ttk.Combobox(outer, textvariable=index_var, values=labels, state="readonly")
        selector.pack(fill="x", pady=(0, 8))

        form = ttk.Frame(outer)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)
        vars_ = {key: tk.StringVar() for key in ("seo_filename", "alt_text", "title", "creator", "source_page_url", "license_name", "license_url")}
        rows = (
            ("نام فایل SEO", "seo_filename"),
            ("Alt فارسی", "alt_text"),
            ("Title تصویر", "title"),
            ("Creator / طراح", "creator"),
            ("صفحه منبع", "source_page_url"),
            ("نام مجوز", "license_name"),
            ("لینک مجوز", "license_url"),
        )
        for r, (label, key) in enumerate(rows):
            ttk.Label(form, text=label).grid(row=r, column=0, sticky="w", padx=4, pady=4)
            ttk.Entry(form, textvariable=vars_[key]).grid(row=r, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(form, text="Caption فارسی").grid(row=7, column=0, sticky="nw", padx=4, pady=4)
        caption = tk.Text(form, height=5, wrap="word")
        caption.grid(row=7, column=1, sticky="nsew", padx=4, pady=4)
        ttk.Label(form, text="Keywords تصویر (هر خط یک مورد)").grid(row=8, column=0, sticky="nw", padx=4, pady=4)
        keywords = tk.Text(form, height=6, wrap="word")
        keywords.grid(row=8, column=1, sticky="nsew", padx=4, pady=4)
        form.rowconfigure(7, weight=1)
        form.rowconfigure(8, weight=1)
        current_index = {"value": 0}

        def defaults_for(url: str, idx: int) -> dict:
            meta = by_url.get(url) or {}
            title = str(_row_value(row, "seo_title_fa", "") or _row_value(row, "title_fa", "") or "محصول چاپ سه‌بعدی")
            alts = _json_list(_row_value(row, "image_alt_texts_json", "[]"))
            return {
                "seo_filename": str(meta.get("seo_filename") or image_pipeline.planned_seo_filename(row, idx + 1)),
                "alt_text": str(meta.get("alt_text") or (alts[idx] if idx < len(alts) else f"{title} - نمای {idx + 1}")),
                "title": str(meta.get("title") or title),
                "caption": str(meta.get("caption") or _row_value(row, "short_description_fa", "") or _row_value(row, "seo_description_fa", "")),
                "keywords": meta.get("keywords") or _json_list(_row_value(row, "keywords_json", "[]")),
                "creator": str(meta.get("creator") or _row_value(row, "author_name", "") or _row_value(row, "source_name", "") or _row_value(row, "source_code", "")),
                "source_page_url": str(meta.get("source_page_url") or _row_value(row, "source_url", "")),
                "license_name": str(meta.get("license_name") or _row_value(row, "license_name", "")),
                "license_url": str(meta.get("license_url") or _row_value(row, "license_url", "")),
            }

        def load_index(idx: int):
            idx = max(0, min(len(selected) - 1, idx))
            current_index["value"] = idx
            data = defaults_for(selected[idx], idx)
            for key, var in vars_.items():
                var.set(str(data.get(key) or ""))
            caption.delete("1.0", "end"); caption.insert("1.0", str(data.get("caption") or ""))
            keywords.delete("1.0", "end"); keywords.insert("1.0", "\n".join(str(item) for item in (data.get("keywords") or [])))
            index_var.set(labels[idx])

        def save_current(close_after=False):
            idx = current_index["value"]
            url = selected[idx]
            existing = dict(by_url.get(url) or {})
            existing.update({
                "source_url": url,
                "seo_filename": _safe_seo_filename(vars_["seo_filename"].get(), image_pipeline.planned_seo_filename(row, idx + 1)),
                "alt_text": vars_["alt_text"].get().strip(),
                "title": vars_["title"].get().strip(),
                "caption": caption.get("1.0", "end").strip(),
                "keywords": [line.strip() for line in keywords.get("1.0", "end").splitlines() if line.strip()],
                "creator": vars_["creator"].get().strip(),
                "source_page_url": vars_["source_page_url"].get().strip(),
                "license_name": vars_["license_name"].get().strip(),
                "license_url": vars_["license_url"].get().strip(),
                "operator_override_fields": list(OVERRIDE_FIELDS),
                "operator_override": True,
                "metadata_ready": False,
                "seo_signature": "",
            })
            by_url[url] = existing
            merged = [by_url.get(item_url) or {"source_url": item_url} for item_url in selected]
            self.db.update_product(self.product_id, {image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(merged, ensure_ascii=False)})
            try:
                image_pipeline.finalize_selected_images(self.db, self.product_id)
            except Exception as exc:
                messagebox.showerror(
                    "3DPrintHub",
                    f"اطلاعات دستی ذخیره شد، اما ساخت فایل نهایی هنوز خطا دارد:\n{exc}",
                    parent=win,
                )
                return
            audit_event(
                "images",
                "operator_metadata_override",
                product_id=self.product_id,
                message=f"image={idx + 1} source={url}",
                source_file="catalog_center/app/phase49_3e_ai_task_center.py",
            )
            self.reload()
            self._phase49_3e_refresh_tasks()
            if close_after:
                win.destroy()
            else:
                messagebox.showinfo("3DPrintHub", "✅ Metadata تصویر ذخیره و فایل SEO دوباره ساخته شد.", parent=win)

        def on_select(_event=None):
            try:
                idx = labels.index(index_var.get())
            except ValueError:
                idx = 0
            load_index(idx)

        selector.bind("<<ComboboxSelected>>", on_select)
        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Button(footer, text="ذخیره و بازسازی فایل SEO", command=lambda: save_current(False), style="Success.TButton").pack(side="right", padx=3)
        ttk.Button(footer, text="ذخیره و بستن", command=lambda: save_current(True)).pack(side="right", padx=3)
        ttk.Button(footer, text="بستن", command=win.destroy).pack(side="right", padx=3)
        load_index(0)

    workspace_class.__init__ = __init__
    workspace_class._phase49_3e_add_image_tools = _phase49_3e_add_image_tools
    workspace_class._phase49_3e_add_content_image_action = _phase49_3e_add_content_image_action
    workspace_class._phase49_3e_add_task_panel = _phase49_3e_add_task_panel
    workspace_class._phase49_3e_refresh_tasks = _phase49_3e_refresh_tasks
    workspace_class._phase49_3c_refresh_live = _phase49_3c_refresh_live
    workspace_class._phase49_3c_stage_ai = _phase49_3c_stage_ai
    workspace_class._phase49_3e_provider = _phase49_3e_provider
    workspace_class._phase49_3e_run_ai = _phase49_3e_run_ai
    workspace_class._phase49_3e_run_all_ai = _phase49_3e_run_all_ai
    workspace_class._phase49_3e_image_ai = _phase49_3e_image_ai
    workspace_class._phase49_3e_apply_ai_result = _phase49_3e_apply_ai_result
    workspace_class._phase49_3e_selected_task = _phase49_3e_selected_task
    workspace_class._phase49_3e_guide_selected_task = _phase49_3e_guide_selected_task
    workspace_class._phase49_3e_open_image_editor = _phase49_3e_open_image_editor
    workspace_class._phase49_3e_task_center_installed = True
