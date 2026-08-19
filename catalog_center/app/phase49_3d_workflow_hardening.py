from __future__ import annotations

import hashlib
import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .ai_providers import AIProviderClient
from .db import utc_now
from .phase49_3c_image_pipeline import finalize_selected_images
from .phase49_3c_persian_content import has_persian_editorial_text
from .phase49_diagnostics import audit_event
from .phase49_readiness_wizard import selected_color_names, selected_material_names
from . import secure_secrets


PROVIDER_ORDER = ("avalai", "openrouter", "openai")
AUTO_COLUMNS = {
    "ai_auto_prepare_hash": "TEXT NOT NULL DEFAULT ''",
    "ai_auto_prepare_status": "TEXT NOT NULL DEFAULT ''",
    "ai_auto_prepare_at": "TEXT NOT NULL DEFAULT ''",
}
GENERIC_FALLBACK_TITLES = {
    "محصول چاپ سه‌بعدی",
    "محصول سه‌بعدی",
}
MODEL_ALIASES = {
    "chatgpt": ("chatgpt", "gpt", "openai"),
    "gpt": ("gpt", "openai"),
    "claude": ("claude", "anthropic"),
    "gemini": ("gemini", "google"),
    "grok": ("grok", "x-ai", "xai"),
    "deepseek": ("deepseek",),
    "qwen": ("qwen", "alibaba"),
    "llama": ("llama", "meta"),
    "mistral": ("mistral",),
}


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


def _positive_int(value, default=0) -> int:
    try:
        return max(0, int(float(str(value if value not in (None, "") else default).replace(",", "").strip() or 0)))
    except Exception:
        return max(0, int(default or 0))


def normalize_price_range(price_min, price_max, fallback=0) -> tuple[int, int]:
    minimum = _positive_int(price_min, 0)
    maximum = _positive_int(price_max, 0)
    fallback = _positive_int(fallback, 0)
    if not minimum and not maximum and fallback:
        minimum = maximum = fallback
    elif minimum and not maximum:
        maximum = minimum
    elif maximum and not minimum:
        minimum = maximum
    if minimum and maximum and maximum < minimum:
        minimum, maximum = maximum, minimum
    return minimum, maximum


def clean_model_id(value: str) -> str:
    model = str(value or "").strip()
    if " • " in model:
        model = model.split(" • ", 1)[0].strip()
    return model


def _normalized_query(query: str) -> list[str]:
    value = str(query or "").strip().casefold()
    if not value:
        return []
    tokens = [token for token in value.replace("/", " ").replace("-", " ").split() if token]
    expanded: list[str] = []
    for token in tokens:
        aliases = MODEL_ALIASES.get(token, (token,))
        for alias in aliases:
            alias = alias.casefold()
            if alias not in expanded:
                expanded.append(alias)
    return expanded


def model_matches(query: str, item: dict) -> bool:
    tokens = _normalized_query(query)
    if not tokens:
        return True
    haystack = " ".join(
        [
            str(item.get("id") or ""),
            str(item.get("name") or ""),
            "free رایگان" if item.get("free") else "",
        ]
    ).casefold()
    raw = [token for token in str(query or "").strip().casefold().split() if token]
    if len(raw) <= 1:
        return any(token in haystack for token in tokens)
    for original in raw:
        aliases = MODEL_ALIASES.get(original, (original,))
        if not any(alias.casefold() in haystack for alias in aliases):
            return False
    return True


def ensure_schema(db) -> None:
    existing = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    for name, ddl in AUTO_COLUMNS.items():
        if name not in existing:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
    db.conn.commit()


def _has_persian_list(value, minimum=1) -> bool:
    values = _json_list(value)
    valid = [str(item or "").strip() for item in values if has_persian_editorial_text(item)]
    return len(valid) >= int(minimum)


def needs_auto_prepare(row) -> bool:
    if row is None:
        return False
    title = str(_row_value(row, "title_fa", "") or "").strip()
    if title in GENERIC_FALLBACK_TITLES or not has_persian_editorial_text(title):
        return True
    if str(_row_value(row, "translation_status", "") or "").strip() in {"pending", "needs_review"}:
        return True
    if str(_row_value(row, "content_status", "") or "").strip() in {"pending", "needs_review"}:
        return True
    for key in ("short_description_fa", "description_fa", "use_description", "seo_title_fa", "seo_description_fa"):
        if not has_persian_editorial_text(_row_value(row, key, "")):
            return True
    if not _has_persian_list(_row_value(row, "keywords_json", "[]"), minimum=3):
        return True
    if not _has_persian_list(_row_value(row, "tags_fa_json", "[]"), minimum=1):
        return True
    if not _has_persian_list(_row_value(row, "hashtags_fa_json", "[]"), minimum=1):
        return True
    # Once the operator has corrected every editorial field, an old fallback marker
    # inside content_pack_json must not force another paid AI request.
    return False


def auto_prepare_fingerprint(source: dict, row) -> str:
    payload = {
        "source_title": source.get("source_title") or "",
        "source_description": source.get("source_description") or "",
        "source_categories": source.get("source_categories") or [],
        "source_category": source.get("source_category") or "",
        "source_specs": source.get("source_specs") or {},
        "source_tags": source.get("source_tags") or [],
        "source_url": _row_value(row, "source_url", ""),
        "source_hash": _row_value(row, "source_hash", ""),
        "selected_materials": selected_material_names(row),
        "selected_colors": selected_color_names(row),
        "images": _json_list(_row_value(row, "selected_images_json", "[]"))[:10],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def similar_editorial_keywords(db, row, limit=24) -> list[str]:
    category = str(_row_value(row, "local_category_slug", "") or "").strip()
    product_id = _positive_int(_row_value(row, "id", 0), 0)
    if not category or category == "external-other":
        return []
    try:
        rows = db.conn.execute(
            """
            SELECT keywords_json, tags_fa_json
            FROM products
            WHERE local_category_slug=? AND id<>?
            ORDER BY updated_at DESC, id DESC
            LIMIT 30
            """,
            (category, product_id),
        ).fetchall()
    except Exception:
        return []
    output: list[str] = []
    seen: set[str] = set()
    for item in rows:
        for field in ("keywords_json", "tags_fa_json"):
            try:
                values = _json_list(item[field])
            except Exception:
                values = []
            for value in values:
                text = str(value or "").strip()
                key = text.casefold()
                if not text or key in seen or not has_persian_editorial_text(text):
                    continue
                seen.add(key)
                output.append(text)
                if len(output) >= int(limit):
                    return output
    return output


def _model_label(item: dict) -> str:
    model_id = str(item.get("id") or "")
    name = str(item.get("name") or model_id)
    free = " • رایگان" if item.get("free") else ""
    context = ""
    try:
        if item.get("context_length"):
            context = f" • ctx {int(item['context_length']):,}"
    except Exception:
        context = ""
    if name.casefold() == model_id.casefold():
        return f"{model_id}{free}{context}"
    return f"{name} — {model_id}{free}{context}"


def install_workspace(workspace_class, readiness_module=None) -> None:
    if getattr(workspace_class, "_phase49_3d_workflow_hardening_installed", False):
        return

    # Guided Wizard Stage 1 inherits a grid-managed quick_tab. The old Phase49.3B
    # add-on used pack() directly in that same parent, which raises TclError.
    def _phase49_3b_add_title_ai(self):
        if getattr(self, "_phase49_3d_title_ai_holder", None) is not None:
            return
        holder = ttk.LabelFrame(
            self.quick_tab,
            text="کمک هوش مصنوعی مرحله ۱",
            padding=8,
            style="Card.TLabelframe",
        )
        rows = []
        for child in self.quick_tab.grid_slaves():
            try:
                rows.append(int(child.grid_info().get("row", 0)))
            except Exception:
                pass
        target_row = (max(rows) + 1) if rows else 0
        holder.grid(row=target_row, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Button(
            holder,
            text="✨ ترجمه فقط عنوان فارسی",
            command=self.translate_title_only,
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Label(
            holder,
            text="فقط عنوان فارسی را تکمیل می‌کند؛ آماده‌سازی کامل AI به‌صورت کنترل‌شده هنگام بازشدن محصول انجام می‌شود.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=8)
        self._phase49_3d_title_ai_holder = holder

    workspace_class._phase49_3b_add_title_ai = _phase49_3b_add_title_ai

    original_init = workspace_class.__init__
    original_save = workspace_class.save
    original_local = getattr(workspace_class, "publish_to_local_computer", None)
    original_production = getattr(workspace_class, "publish_to_production_site", None)

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        try:
            self.after(900, self._phase49_3d_auto_prepare_on_open)
        except Exception:
            pass

    def save(self, silent=False):
        if not original_save(self, silent=silent):
            return False
        row = self.db.product(self.product_id)
        if row is None:
            return False
        fallback = _positive_int(_row_value(row, "final_price", 0) or _row_value(row, "suggested_price", 0), 0)
        minimum = self.price_min_var.get() if hasattr(self, "price_min_var") else _row_value(row, "price_min", 0)
        maximum = self.price_max_var.get() if hasattr(self, "price_max_var") else _row_value(row, "price_max", 0)
        minimum, maximum = normalize_price_range(minimum, maximum, fallback)
        self.db.update_product(self.product_id, {"price_min": minimum, "price_max": maximum})
        if hasattr(self, "price_min_var"):
            self.price_min_var.set(str(minimum))
        if hasattr(self, "price_max_var"):
            self.price_max_var.set(str(maximum))
        self.row = self.db.product(self.product_id)
        if not silent:
            self.footer_status.set(
                f"ذخیره شد • بازه قیمت {minimum:,} تا {maximum:,} تومان"
                if minimum
                else "ذخیره شد • قیمت هنوز تعیین نشده"
            )
        return True

    def _phase49_3d_auto_prepare_on_open(self):
        try:
            enabled = str(self.db.setting("ai_auto_prepare_on_open", "1") or "1").strip().lower()
        except Exception:
            enabled = "1"
        if enabled in {"0", "false", "off", "no"}:
            return
        if getattr(self, "_ai_busy", False):
            return
        row = self.db.product(self.product_id)
        if row is None:
            return
        try:
            source = dict(self._source_for_ai() or {})
        except Exception as exc:
            audit_event(
                "ai",
                "auto_prepare_skip",
                status="error",
                level="ERROR",
                product_id=self.product_id,
                message=f"source context failed: {exc}",
                source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
            )
            return
        digest = auto_prepare_fingerprint(source, row)
        last_hash = str(_row_value(row, "ai_auto_prepare_hash", "") or "")
        last_status = str(_row_value(row, "ai_auto_prepare_status", "") or "")
        if not needs_auto_prepare(row):
            if last_hash != digest or last_status != "already_ready":
                self.db.update_product(
                    self.product_id,
                    {
                        "ai_auto_prepare_hash": digest,
                        "ai_auto_prepare_status": "already_ready",
                        "ai_auto_prepare_at": utc_now(),
                    },
                )
            return
        if last_hash == digest and last_status in {"ok", "error", "running"}:
            if last_status == "error":
                self.footer_status.set("آماده‌سازی خودکار AI قبلاً خطا داده؛ از «هوش مصنوعی همین مرحله» برای Retry استفاده کن.")
            return

        provider = self.app._selected_ai_provider()
        key = self.app._ai_key(provider)
        model = clean_model_id(
            self.app.ai_model.get()
            or self.db.setting(f"ai_model_{provider}", "")
            or self.db.setting("ai_model", "")
        )
        if not key:
            self.footer_status.set("آماده‌سازی خودکار AI: Provider فعال API Key ندارد.")
            return
        if not model:
            self.footer_status.set("آماده‌سازی خودکار AI: ابتدا Provider و مدل فعال را در «هوش مصنوعی» ذخیره کن.")
            return

        source["selected_materials"] = selected_material_names(row)
        source["selected_colors"] = selected_color_names(row)
        similar_keywords = similar_editorial_keywords(self.db, row)
        source["similar_persian_keywords"] = similar_keywords
        source["source_tags"] = list(dict.fromkeys([
            *[str(x or "").strip() for x in (source.get("source_tags") or []) if str(x or "").strip()],
            *similar_keywords[:12],
        ]))
        images = self._json_list(_row_value(row, "selected_images_json", "[]") or _row_value(row, "images_json", "[]"))[:10]
        categories = self.app.get_all_categories()
        self._ai_busy = True
        self.db.update_product(
            self.product_id,
            {
                "ai_auto_prepare_hash": digest,
                "ai_auto_prepare_status": "running",
                "ai_auto_prepare_at": utc_now(),
            },
        )
        self.footer_status.set(f"{provider} / {model} در حال آماده‌سازی اولیه فارسی و SEO…")
        audit_event(
            "ai",
            "auto_prepare_start",
            product_id=self.product_id,
            message=f"provider={provider} model={model}",
            source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
        )

        def worker():
            try:
                from .openai_content import AIContentService
                pack = AIContentService(
                    key,
                    model,
                    provider,
                    product_id=self.product_id,
                ).enrich_product(
                    source,
                    categories,
                    image_count=len(images),
                    image_urls=images,
                    mode="commerce",
                )
                self.after(0, lambda pack=pack: done(pack, None))
            except Exception as exc:
                self.after(0, lambda exc=exc: done(None, exc))

        def done(pack, error):
            self._ai_busy = False
            if error is not None:
                self.db.update_product(
                    self.product_id,
                    {
                        "ai_auto_prepare_hash": digest,
                        "ai_auto_prepare_status": "error",
                        "ai_auto_prepare_at": utc_now(),
                    },
                )
                audit_event(
                    "ai",
                    "auto_prepare_error",
                    status="error",
                    level="ERROR",
                    product_id=self.product_id,
                    message=f"provider={provider} model={model}: {error}",
                    source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                )
                self.footer_status.set("آماده‌سازی اولیه AI ناموفق بود؛ جزئیات در لاگ برنامه ثبت شد.")
                return
            try:
                self.app._apply_ai_pack(self.product_id, pack, open_studio=False)
                self.db.update_product(
                    self.product_id,
                    {
                        "ai_auto_prepare_hash": digest,
                        "ai_auto_prepare_status": "ok",
                        "ai_auto_prepare_at": utc_now(),
                    },
                )
                self.reload()
                try:
                    self._phase49_3c_schedule_live()
                except Exception:
                    pass
                audit_event(
                    "ai",
                    "auto_prepare_success",
                    product_id=self.product_id,
                    message=f"provider={provider} model={model} similar_keywords={len(similar_keywords)}",
                    source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                )
                self.footer_status.set("آماده‌سازی اولیه AI انجام شد؛ متن فارسی، کاربرد و SEO را بازبینی کن.")
            except Exception as exc:
                self.db.update_product(
                    self.product_id,
                    {
                        "ai_auto_prepare_hash": digest,
                        "ai_auto_prepare_status": "error",
                        "ai_auto_prepare_at": utc_now(),
                    },
                )
                audit_event(
                    "ai",
                    "auto_prepare_apply_error",
                    status="error",
                    level="ERROR",
                    product_id=self.product_id,
                    message=str(exc),
                    source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                )
                self.footer_status.set("اعمال محتوای AI ناموفق بود؛ جزئیات در لاگ برنامه ثبت شد.")

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3d_publish_preflight(self, target="local"):
        if not self.save(silent=True):
            messagebox.showerror(
                "3DPrintHub — بررسی قبل از انتشار",
                "ذخیره محصول قبل از انتشار ناموفق بود.",
                parent=self,
            )
            return False
        try:
            state, snapshot = self._phase49_3c_state()
        except Exception as exc:
            messagebox.showerror(
                "3DPrintHub — بررسی قبل از انتشار",
                f"Readiness قابل محاسبه نیست:\n{type(exc).__name__}: {exc}",
                parent=self,
            )
            audit_event(
                "publish",
                "preflight_error",
                status="error",
                level="ERROR",
                product_id=self.product_id,
                message=str(exc),
                source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
            )
            return False

        image_stage = state.get("stages", {}).get("images") or {}
        image_missing = list(image_stage.get("missing") or [])
        selected = _json_list(snapshot.get("selected_images_json"))
        primary = str(snapshot.get("primary_image_url") or "").strip()
        core_image_missing = (
            not selected
            or not primary
            or any(
                item in {"تصویر اصلی", "حداقل یک تصویر انتخاب‌شده"}
                for item in image_missing
            )
        )
        if image_missing and not core_image_missing:
            try:
                self.footer_status.set("در حال نهایی‌سازی خودکار SEO/Metadata تصاویر قبل از انتشار…")
                finalize_selected_images(self.db, self.product_id)
                self.reload()
                state, snapshot = self._phase49_3c_state()
                audit_event(
                    "publish",
                    "auto_finalize_images",
                    product_id=self.product_id,
                    message=f"target={target}",
                    source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                )
            except Exception as exc:
                audit_event(
                    "publish",
                    "auto_finalize_images_error",
                    status="error",
                    level="ERROR",
                    product_id=self.product_id,
                    message=f"target={target}: {exc}",
                    source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                )
                messagebox.showerror(
                    "3DPrintHub — تصاویر آماده انتشار نیستند",
                    "نهایی‌سازی خودکار تصاویر ناموفق بود:\n\n"
                    f"{type(exc).__name__}: {exc}\n\n"
                    "هیچ ارسال Local/Production انجام نشد.",
                    parent=self,
                )
                return False

        if state.get("production_ready"):
            return True

        first = next(
            (
                key
                for key in getattr(readiness_module, "STAGE_ORDER", ()) or ()
                if not (state.get("stages", {}).get(key) or {}).get("ready", False)
            ),
            "images",
        )
        try:
            self.select_section(first)
        except Exception:
            pass
        missing = state.get("missing") or []
        detail = "\n".join(f"• {item}" for item in missing[:24]) or "• مورد ناقص نامشخص"
        audit_event(
            "publish",
            "preflight_blocked",
            status="blocked",
            level="WARNING",
            product_id=self.product_id,
            message=f"target={target}; missing={' | '.join(missing[:12])}",
            source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
        )
        messagebox.showwarning(
            "3DPrintHub — انتشار متوقف شد",
            "محصول هنوز آماده ارسال نیست. دلیل دقیق:\n\n"
            f"{detail}\n\n"
            "برنامه به اولین مرحله ناقص منتقل شد و هیچ Batch/FTP/Import اجرا نشد.",
            parent=self,
        )
        return False

    def publish_to_local_computer(self):
        if not self._phase49_3d_publish_preflight("local"):
            return False
        return original_local(self) if callable(original_local) else False

    def publish_to_production_site(self):
        if not self._phase49_3d_publish_preflight("production"):
            return False
        return original_production(self) if callable(original_production) else False

    workspace_class.__init__ = __init__
    workspace_class.save = save
    workspace_class._phase49_3d_auto_prepare_on_open = _phase49_3d_auto_prepare_on_open
    workspace_class._phase49_3d_publish_preflight = _phase49_3d_publish_preflight
    if callable(original_local):
        workspace_class.publish_to_local_computer = publish_to_local_computer
    if callable(original_production):
        workspace_class.publish_to_production_site = publish_to_production_site
    workspace_class._phase49_3d_workflow_hardening_installed = True


def install_ai_shell(app_class) -> None:
    if getattr(app_class, "_phase49_3d_ai_shell_installed", False):
        return

    original_init_state = app_class._init_ux87_settings_state
    original_build = app_class._build_ux87_ai_center

    def _init_ux87_settings_state(self):
        original_init_state(self)
        stored = str(self.db.setting("ai_provider", "auto") or "auto").strip().lower()
        active = stored if stored in PROVIDER_ORDER else "avalai"
        self._phase49_3d_active_provider = tk.StringVar(value=active)
        try:
            auto_value = int(str(self.db.setting("ai_auto_prepare_on_open", "1") or "1").strip().lower() not in {"0", "false", "off"})
        except Exception:
            auto_value = 1
        self._phase49_3d_auto_prepare_var = tk.IntVar(value=auto_value)
        self._phase49_3d_active_summary = tk.StringVar(value="")
        self._phase49_3d_model_cache = {provider: [] for provider in PROVIDER_ORDER}

    def _phase49_3d_provider_key(self, provider: str) -> str:
        entered = ""
        try:
            entered = self._ai_hub_key_vars[provider].get().strip()
        except Exception:
            entered = ""
        return entered or secure_secrets.get_provider_key(provider)

    def _phase49_3d_refresh_active_summary(self):
        provider = self._phase49_3d_active_provider.get().strip().lower()
        model = ""
        if provider in PROVIDER_ORDER:
            try:
                model = clean_model_id(self._ai_hub_model_vars[provider].get())
            except Exception:
                model = ""
        self._phase49_3d_active_summary.set(
            f"Provider فعال: {provider or '—'} • مدل فعال: {model or 'انتخاب نشده'}"
        )

    def _phase49_3d_save_active_ai(self):
        provider = self._phase49_3d_active_provider.get().strip().lower()
        if provider not in PROVIDER_ORDER:
            messagebox.showwarning("3DPrintHub", "یک Provider را با Radio انتخاب کن.", parent=self)
            return
        model = clean_model_id(self._ai_hub_model_vars[provider].get())
        if not model:
            messagebox.showwarning(
                "3DPrintHub",
                "ابتدا مدل را با «جستجو و انتخاب مدل» انتخاب کن.",
                parent=self,
            )
            return
        entered_key = ""
        try:
            entered_key = self._ai_hub_key_vars[provider].get().strip()
        except Exception:
            entered_key = ""
        try:
            if entered_key:
                secure_secrets.set_provider_key(provider, entered_key)
                self._ai_hub_key_vars[provider].set("")
            self._ai_hub_model_vars[provider].set(model)
            box = self._ai_hub_model_boxes.get(provider)
            if box is not None:
                box.set(model)
            self.ai_provider.set(provider)
            self.ai_model.set(model)
            self.db.set_setting("ai_provider", provider)
            self.db.set_setting("ai_model", model)
            self.db.set_setting(f"ai_model_{provider}", model)
            self.db.set_setting(
                "ai_auto_prepare_on_open",
                "1" if int(self._phase49_3d_auto_prepare_var.get()) else "0",
            )
            audit_event(
                "settings",
                "phase49_3d_active_ai_saved",
                message=f"provider={provider} model={model}",
                source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
            )
            self._phase49_3d_refresh_active_summary()
            self._ai_hub_status_vars[provider].set("✅ Provider و مدل فعال ذخیره شد")
            try:
                self._refresh_ux87_status()
            except Exception:
                pass
            messagebox.showinfo(
                "3DPrintHub — هوش مصنوعی",
                f"Provider فعال: {provider}\nمدل فعال: {model}\n\nتنظیمات برای درخواست‌های بعدی ذخیره شد.",
                parent=self,
            )
        except Exception as exc:
            audit_event(
                "settings",
                "phase49_3d_active_ai_save_error",
                status="error",
                level="ERROR",
                message=f"provider={provider} model={model}: {exc}",
                source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
            )
            messagebox.showerror("3DPrintHub", str(exc), parent=self)

    def _phase49_3d_test_active_ai(self):
        provider = self._phase49_3d_active_provider.get().strip().lower()
        if provider not in PROVIDER_ORDER:
            messagebox.showwarning("3DPrintHub", "ابتدا Provider فعال را انتخاب کن.", parent=self)
            return
        key = self._phase49_3d_provider_key(provider)
        model = clean_model_id(self._ai_hub_model_vars[provider].get())
        if not key:
            messagebox.showwarning("3DPrintHub", f"API Key برای {provider} تنظیم نشده است.", parent=self)
            return
        if not model:
            messagebox.showwarning("3DPrintHub", "مدل فعال انتخاب نشده است.", parent=self)
            return
        self._ai_hub_status_vars[provider].set(f"در حال تست {provider} / {model}…")

        def worker():
            try:
                result = AIProviderClient(provider, key, model).test_connection(model)
                self.after(0, lambda result=result: done(result, None))
            except Exception as exc:
                self.after(0, lambda exc=exc: done(None, exc))

        def done(result, error):
            if error is not None:
                self._ai_hub_status_vars[provider].set(f"❌ تست اتصال: {error}")
                audit_event(
                    "ai",
                    "phase49_3d_active_provider_test",
                    status="error",
                    level="ERROR",
                    message=f"provider={provider} model={model}: {error}",
                    source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                )
                messagebox.showerror("3DPrintHub — تست اتصال", str(error), parent=self)
                return
            actual = str(result.get("model") or model)
            count = int(result.get("models_count") or 0)
            sample = str(result.get("sample") or "")[:100]
            self._ai_hub_status_vars[provider].set(f"✅ اتصال موفق • {actual} • {count:,} مدل قابل مشاهده")
            audit_event(
                "ai",
                "phase49_3d_active_provider_test",
                message=f"provider={provider} model={actual} models={count}",
                source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
            )
            messagebox.showinfo(
                "3DPrintHub — تست اتصال موفق",
                f"Provider: {provider}\nModel: {actual}\nModels returned: {count:,}\nSample: {sample}",
                parent=self,
            )

        threading.Thread(target=worker, daemon=True).start()

    def _phase49_3d_open_model_picker(self, provider: str):
        provider = str(provider or "").strip().lower()
        if provider not in PROVIDER_ORDER:
            return
        key = self._phase49_3d_provider_key(provider)
        if not key:
            messagebox.showwarning(
                "3DPrintHub",
                f"ابتدا API Key مربوط به {provider} را در کارت خودش وارد/ذخیره کن.",
                parent=self,
            )
            return

        win = tk.Toplevel(self)
        win.title(f"انتخاب مدل هوش مصنوعی — {provider}")
        win.geometry("1080x720")
        win.transient(self)
        win.columnconfigure(0, weight=1)
        win.rowconfigure(2, weight=1)

        query = tk.StringVar(value="")
        free_only = tk.IntVar(value=0)
        count_var = tk.StringVar(value="در حال دریافت مدل‌ها…")
        search = ttk.Frame(win, padding=10)
        search.grid(row=0, column=0, sticky="ew")
        search.columnconfigure(1, weight=1)
        ttk.Label(search, text="جستجو").grid(row=0, column=0, padx=(0, 6))
        entry = ttk.Entry(search, textvariable=query)
        entry.grid(row=0, column=1, sticky="ew")
        ttk.Checkbutton(search, text="فقط مدل‌های رایگان", variable=free_only).grid(row=0, column=2, padx=8)
        ttk.Button(
            search,
            text="بروزرسانی از API",
            command=lambda: load_models(force=True),
        ).grid(row=0, column=3, padx=4)

        ttk.Label(
            win,
            text="نمونه جستجو: CHATGPT، GPT، Claude، Gemini، Grok، DeepSeek، Qwen، Llama یا بخشی از model_id",
            style="SubHeader.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=10)
        body = ttk.Frame(win, padding=(10, 6))
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        listbox = tk.Listbox(body, font=("Consolas", 10), exportselection=False)
        y = ttk.Scrollbar(body, orient="vertical", command=listbox.yview)
        x = ttk.Scrollbar(body, orient="horizontal", command=listbox.xview)
        listbox.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        listbox.grid(row=0, column=0, sticky="nsew")
        y.grid(row=0, column=1, sticky="ns")
        x.grid(row=1, column=0, sticky="ew")
        visible: list[dict] = []

        footer = ttk.Frame(win, padding=10)
        footer.grid(row=3, column=0, sticky="ew")
        ttk.Label(footer, textvariable=count_var).pack(side="left")
        ttk.Button(footer, text="انصراف", command=win.destroy).pack(side="right", padx=4)
        ttk.Button(
            footer,
            text="انتخاب این مدل",
            command=lambda: choose(),
            style="Success.TButton",
        ).pack(side="right", padx=4)

        def refresh_filter(*_args):
            source = list(self._phase49_3d_model_cache.get(provider) or [])
            filtered = [
                item
                for item in source
                if model_matches(query.get(), item) and (not free_only.get() or item.get("free"))
            ]
            visible[:] = filtered
            listbox.delete(0, "end")
            for item in filtered:
                listbox.insert("end", _model_label(item))
            count_var.set(
                f"{len(filtered):,} مدل نمایش داده می‌شود از {len(source):,} مدل دریافت‌شده"
            )

        def choose():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("3DPrintHub", "یک مدل را از فهرست انتخاب کن.", parent=win)
                return
            item = visible[int(selection[0])]
            model_id = clean_model_id(item.get("id"))
            self._ai_hub_model_vars[provider].set(model_id)
            box = self._ai_hub_model_boxes.get(provider)
            if box is not None:
                box.set(model_id)
            self._phase49_3d_active_provider.set(provider)
            self._phase49_3d_refresh_active_summary()
            self._ai_hub_status_vars[provider].set(f"مدل انتخاب‌شده: {model_id} • برای ثبت، «ذخیره Provider و مدل فعال» را بزن.")
            win.destroy()

        def load_models(force=False):
            cached = list(self._phase49_3d_model_cache.get(provider) or [])
            if cached and not force:
                refresh_filter()
                return
            count_var.set("در حال دریافت فهرست کامل مدل‌ها از API…")
            listbox.delete(0, "end")
            preferred = clean_model_id(self._ai_hub_model_vars[provider].get())

            def worker():
                try:
                    info = AIProviderClient(provider, key, preferred).list_model_info()
                    self.after(0, lambda info=info: loaded(info, None))
                except Exception as exc:
                    self.after(0, lambda exc=exc: loaded(None, exc))

            def loaded(info, error):
                if not win.winfo_exists():
                    return
                if error is not None:
                    count_var.set(f"خطا در دریافت مدل‌ها: {error}")
                    self._ai_hub_status_vars[provider].set(f"❌ دریافت مدل‌ها: {error}")
                    audit_event(
                        "ai",
                        "phase49_3d_model_list_error",
                        status="error",
                        level="ERROR",
                        message=f"provider={provider}: {error}",
                        source_file="catalog_center/app/phase49_3d_workflow_hardening.py",
                    )
                    return
                info = list(info or [])
                self._phase49_3d_model_cache[provider] = info
                raw_ids = [str(item.get("id") or "") for item in info if item.get("id")]
                box = self._ai_hub_model_boxes.get(provider)
                if box is not None:
                    box.configure(values=raw_ids)
                self._ai_hub_status_vars[provider].set(f"✅ {len(info):,} مدل از API دریافت شد")
                refresh_filter()

            threading.Thread(target=worker, daemon=True).start()

        query.trace_add("write", refresh_filter)
        free_only.trace_add("write", refresh_filter)
        listbox.bind("<Double-Button-1>", lambda _event: choose())
        entry.focus_set()
        load_models(force=False)

    def _build_ux87_ai_center(self):
        original_build(self)
        cards = []
        for child in self.ai_tab.winfo_children():
            if not isinstance(child, ttk.LabelFrame):
                continue
            try:
                label = str(child.cget("text") or "")
            except Exception:
                label = ""
            provider = next((p for p in PROVIDER_ORDER if p in label.casefold()), "")
            if not provider:
                if "AvalAI" in label:
                    provider = "avalai"
                elif "OpenRouter" in label:
                    provider = "openrouter"
                elif "OpenAI" in label:
                    provider = "openai"
            if provider:
                cards.append((provider, child))

        for provider, card in cards:
            tools = ttk.Frame(card)
            row = max(
                [int(child.grid_info().get("row", 0)) for child in card.grid_slaves()] or [0]
            ) + 1
            tools.grid(row=row, column=0, columnspan=3, sticky="ew", padx=4, pady=(6, 2))
            ttk.Radiobutton(
                tools,
                text="Provider فعال",
                value=provider,
                variable=self._phase49_3d_active_provider,
                command=self._phase49_3d_refresh_active_summary,
            ).pack(side="left", padx=3)
            ttk.Button(
                tools,
                text="🔎 جستجو و انتخاب مدل",
                command=lambda p=provider: self._phase49_3d_open_model_picker(p),
                style="Primary.TButton",
            ).pack(side="left", padx=3)
            box = self._ai_hub_model_boxes.get(provider)
            if box is not None:
                box.bind(
                    "<<ComboboxSelected>>",
                    lambda _event, p=provider: self._phase49_3d_normalize_legacy_model(p),
                    add="+",
                )

        controls = ttk.LabelFrame(
            self.ai_tab,
            text="Provider و مدل فعال برنامه",
            padding=10,
            style="Card.TLabelframe",
        )
        next_row = max(
            [int(child.grid_info().get("row", 0)) for child in self.ai_tab.grid_slaves()] or [0]
        ) + 1
        controls.grid(row=next_row, column=0, sticky="ew", pady=(8, 0))
        ttk.Label(controls, textvariable=self._phase49_3d_active_summary, style="SubHeader.TLabel").pack(side="left", padx=4)
        ttk.Checkbutton(
            controls,
            text="آماده‌سازی اولیه AI هنگام بازشدن محصول (فقط در صورت تغییر/نقص)",
            variable=self._phase49_3d_auto_prepare_var,
        ).pack(side="left", padx=10)
        ttk.Button(
            controls,
            text="ذخیره Provider و مدل فعال",
            command=self._phase49_3d_save_active_ai,
            style="Success.TButton",
        ).pack(side="right", padx=4)
        ttk.Button(
            controls,
            text="تست اتصال Provider/Model فعال",
            command=self._phase49_3d_test_active_ai,
            style="Primary.TButton",
        ).pack(side="right", padx=4)
        self._phase49_3d_refresh_active_summary()

    def _phase49_3d_normalize_legacy_model(self, provider: str):
        try:
            model = clean_model_id(self._ai_hub_model_vars[provider].get())
            self._ai_hub_model_vars[provider].set(model)
            self._phase49_3d_active_provider.set(provider)
            self._phase49_3d_refresh_active_summary()
        except Exception:
            pass

    app_class._init_ux87_settings_state = _init_ux87_settings_state
    app_class._build_ux87_ai_center = _build_ux87_ai_center
    app_class._phase49_3d_provider_key = _phase49_3d_provider_key
    app_class._phase49_3d_refresh_active_summary = _phase49_3d_refresh_active_summary
    app_class._phase49_3d_save_active_ai = _phase49_3d_save_active_ai
    app_class._phase49_3d_test_active_ai = _phase49_3d_test_active_ai
    app_class._phase49_3d_open_model_picker = _phase49_3d_open_model_picker
    app_class._phase49_3d_normalize_legacy_model = _phase49_3d_normalize_legacy_model
    app_class._phase49_3d_ai_shell_installed = True
