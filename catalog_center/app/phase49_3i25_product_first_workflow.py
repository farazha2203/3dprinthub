from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from types import SimpleNamespace
from typing import Any

from . import phase49_3i21_observable_ai_link_refresh as link_runtime
from .ai_providers import AIProviderClient
from .db import normalize_url
from .openai_content import AIContentService
from .phase49_3i18_operator_editing import _list
from .phase49_3i19_source_identity import canonical_source_title, is_generic_source_title
from .phase49_diagnostics import audit_event
from .phase49_readiness_wizard import evaluate_readiness, selected_color_names, selected_material_names


PHASE = "49.3I.25"
_EXPLICIT_MODEL_WINDOW_SECONDS = 180.0
_TEXT_FIRST_SECTIONS = [
    ("content", "۱. محتوا و SEO"),
    ("quick", "۲. اطلاعات پایه"),
    ("images", "۳. تصاویر"),
    ("commerce", "۴. سفارش، قیمت و گزینه‌ها"),
    ("specs", "۵. منبع و مجوز"),
    ("publish", "۶. بررسی و انتشار"),
]


def _row_value(row, key: str, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
    except Exception:
        value = default
    return default if value is None else value


def _positive_number(value):
    try:
        number = float(value)
    except Exception:
        return None
    return number if 0 < number < 10_000_000 else None


def normalized_source_facts(parsed: dict[str, Any], source_url: str) -> dict[str, Any]:
    facts = link_runtime.normalized_source_facts(parsed, source_url)
    for key in ("estimated_weight_grams", "estimated_print_minutes"):
        number = _positive_number((parsed or {}).get(key))
        if number is not None:
            facts[key] = number
    return facts


def makerworld_profile_weight_from_html(html: str, source_url: str):
    """Return the weight for the exact MakerWorld profile selected in the URL.

    MakerWorld profile links use ``#profileId-<instance id>``.  Prefer that exact
    instance instead of accepting an unrelated weight from another print profile.
    """
    match = re.search(r"profileId[-=](\d+)", str(source_url or ""), re.I)
    if not match or "makerworld.com" not in str(source_url or "").lower():
        return None
    target = match.group(1)
    try:
        from . import crawler
        data = crawler._next_data(html)  # existing parser boundary; read-only
        nodes = crawler._walk_json(data)
    except Exception:
        return None
    for node in nodes:
        if not isinstance(node, dict):
            continue
        identity = node.get("id") or node.get("profileId") or node.get("profile_id")
        if str(identity or "") != target:
            continue
        for key in ("weight", "weightGram", "weight_gram", "filamentWeight", "materialWeight"):
            value = _positive_number(node.get(key))
            if value is not None:
                return value
    return None


def _first_incomplete(state: dict) -> str:
    order = ("content", "quick", "images", "commerce", "specs", "publish")
    stages = state.get("stages") or {}
    return next((key for key in order if not (stages.get(key) or {}).get("ready", False)), "publish")


def _ai_fillable_missing(state: dict) -> bool:
    stages = state.get("stages") or {}
    for key in ("content", "quick"):
        missing = list((stages.get(key) or {}).get("missing") or [])
        if missing:
            return True
    return False


def _grant_explicit_model_discovery() -> None:
    AIProviderClient._phase49_3i25_explicit_model_until = time.monotonic() + _EXPLICIT_MODEL_WINDOW_SECONDS


def install_database(database_class) -> None:
    """Serialize the remaining shared Catalog connection operations per instance."""
    if getattr(database_class, "_phase49_3i25_connection_guard", False):
        return
    original_init = database_class.__init__

    def __init__(self, *args, **kwargs):
        self._phase49_3i25_db_lock = threading.RLock()
        original_init(self, *args, **kwargs)
        try:
            self.conn.execute("PRAGMA busy_timeout=30000")
        except Exception:
            pass

    database_class.__init__ = __init__
    for name in (
        "product", "source", "setting", "set_setting", "update_product",
        "save_history", "upsert_source", "status_counts",
    ):
        original = getattr(database_class, name, None)
        if not callable(original):
            continue

        def make_guarded(fn):
            def guarded(self, *args, **kwargs):
                lock = getattr(self, "_phase49_3i25_db_lock", None)
                if lock is None:
                    return fn(self, *args, **kwargs)
                with lock:
                    return fn(self, *args, **kwargs)
            return guarded

        setattr(database_class, name, make_guarded(original))
    database_class._phase49_3i25_connection_guard = True


def install_app(app_class) -> None:
    """Make model discovery operator-explicit for the lifetime of the process."""
    if getattr(app_class, "_phase49_3i25_explicit_ai_discovery", False):
        return

    Client = AIProviderClient
    if not getattr(Client, "_phase49_3i25_explicit_model_guard", False):
        original_list = Client.list_model_info

        def list_model_info(self):
            if self.product_id is None:
                until = float(getattr(Client, "_phase49_3i25_explicit_model_until", 0.0) or 0.0)
                if time.monotonic() > until:
                    Client._phase49_3i25_blocked_model_scans = int(
                        getattr(Client, "_phase49_3i25_blocked_model_scans", 0) or 0
                    ) + 1
                    audit_event(
                        "performance",
                        "hidden_model_scan_blocked",
                        status="blocked",
                        level="WARNING",
                        source_file=__file__,
                        message=f"provider={self.provider}; explicit operator action required",
                    )
                    return []
            return original_list(self)

        Client.list_model_info = list_model_info
        Client._phase49_3i25_explicit_model_until = 0.0
        Client._phase49_3i25_blocked_model_scans = 0
        Client._phase49_3i25_explicit_model_guard = True

    # These methods are only entered from visible operator buttons. Grant a short
    # window so their background worker can perform the requested /models call.
    for name in (
        "_phase49_3d_open_model_picker",
        "_phase49_3d_test_active_ai",
        "load_ai_models",
        "test_openai_api",
    ):
        original = getattr(app_class, name, None)
        if not callable(original) or getattr(original, "_phase49_3i25_explicit", False):
            continue

        def make_explicit(fn):
            def explicit(self, *args, **kwargs):
                _grant_explicit_model_discovery()
                return fn(self, *args, **kwargs)
            explicit._phase49_3i25_explicit = True
            return explicit

        setattr(app_class, name, make_explicit(original))

    app_class._phase49_3i25_explicit_ai_discovery = True


def configure_diagnostics_isolated(database, logger=None) -> None:
    """Move diagnostics writes off the Catalog connection without changing schema."""
    try:
        from . import phase49_diagnostics as diagnostics
        path = Path(getattr(database, "path"))
        conn = sqlite3.connect(path, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        proxy = SimpleNamespace(conn=conn, path=path)
        diagnostics._DB = proxy
        diagnostics._LOGGER = logger
        diagnostics.ensure_schema(proxy)
        audit_event(
            "runtime",
            "diagnostics_connection_isolated",
            source_file=__file__,
            message="diagnostics use a dedicated SQLite connection",
        )
    except Exception as exc:
        audit_event(
            "runtime",
            "diagnostics_connection_isolation_failed",
            status="error",
            level="ERROR",
            source_file=__file__,
            message=str(exc),
        )


def install_workspace(workspace_class, readiness_module=None) -> None:
    if getattr(workspace_class, "_phase49_3i25_product_first_workflow", False):
        return

    workspace_class.SECTION_LABELS = list(_TEXT_FIRST_SECTIONS)
    if readiness_module is not None:
        try:
            readiness_module.STAGE_LABELS.clear()
            readiness_module.STAGE_LABELS.update(dict(_TEXT_FIRST_SECTIONS))
        except Exception:
            pass

    original_init = workspace_class.__init__
    original_refresh_gallery = workspace_class.refresh_gallery
    original_local = getattr(workspace_class, "publish_to_local_computer", None)
    original_production = getattr(workspace_class, "publish_to_production_site", None)

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        self.gallery_page_size = 100
        self.gallery_page = 0
        _install_quick_link_action(self)
        _normalize_legacy_product_actions(self)
        _enable_all_stage_navigation(self)
        _install_gallery_mousewheel(self)
        try:
            self.refresh_gallery()
        except Exception:
            pass
        # Editorial identity/SEO is the first operator step because it supplies
        # title, descriptions, keywords and image text needed by later stages.
        try:
            self.select_section("content")
        except Exception:
            pass

    def refresh_gallery(self):
        self.gallery_page_size = 100
        self.gallery_page = 0
        result = original_refresh_gallery(self)
        frames = []
        try:
            for child in self.gallery_inner.winfo_children():
                if isinstance(child, ttk.Frame):
                    frames.append(child)
            for index, card in enumerate(frames):
                card.grid_configure(row=index // 5, column=index % 5)
            for col in range(5):
                self.gallery_inner.columnconfigure(col, weight=1, uniform="phase49_i25_gallery")
            self.gallery_page_info.set(f"نمایش همه {len(frames)} تصویر • ۵ تصویر در هر ردیف")
        except Exception:
            pass
        return result

    def link_refresh(self):
        return _run_link_refresh(self)

    def publish_local(self):
        if not _publication_gate_or_ai(self, "کامپیوتر"):
            return False
        return original_local(self) if callable(original_local) else False

    def publish_production(self):
        if not _publication_gate_or_ai(self, "سایت"):
            return False
        return original_production(self) if callable(original_production) else False

    workspace_class.__init__ = __init__
    workspace_class.refresh_gallery = refresh_gallery
    workspace_class._phase49_3i21_link_refresh = link_refresh
    if callable(original_local):
        workspace_class.publish_to_local_computer = publish_local
    if callable(original_production):
        workspace_class.publish_to_production_site = publish_production
        workspace_class.publish_now = publish_production
    workspace_class._phase49_3i25_product_first_workflow = True


def _install_quick_link_action(workspace) -> None:
    if getattr(workspace, "_phase49_3i25_quick_panel", None) is not None:
        return
    try:
        panel = ttk.LabelFrame(
            workspace.quick_tab,
            text="تکمیل هوشمند از منبع واقعی",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.grid(row=99, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        panel.columnconfigure(0, weight=1)
        ttk.Label(
            panel,
            text="لینک محصول خوانده می‌شود؛ عنوان، وزن موجود در منبع، محتوای فارسی، SEO و متن تصاویر یکجا تکمیل می‌شوند.",
            style="SubHeader.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=4)
        ttk.Button(
            panel,
            text="🌐 تکمیل همه اطلاعات بر اساس لینک محصول",
            command=workspace._phase49_3i21_link_refresh,
            style="Success.TButton",
        ).grid(row=0, column=1, padx=6)
        workspace._phase49_3i25_quick_panel = panel
    except Exception:
        pass


def _normalize_legacy_product_actions(workspace) -> None:
    replacements = {
        "ارسال دیتای محصول": "🌐 تکمیل همه اطلاعات بر اساس لینک محصول",
        "ارسال داده محصول": "🌐 تکمیل همه اطلاعات بر اساس لینک محصول",
        "تکمیل اطلاعات با AI": "🌐 تکمیل همه اطلاعات بر اساس لینک محصول",
    }
    try:
        for child in workspace._walk(workspace):
            if not isinstance(child, ttk.Button):
                continue
            text = str(child.cget("text") or "").strip()
            if text in replacements:
                child.configure(text=replacements[text], command=workspace._phase49_3i21_link_refresh)
    except Exception:
        pass


def _enable_all_stage_navigation(workspace) -> None:
    for button in getattr(workspace, "_section_buttons", {}).values():
        try:
            button.configure(state="normal")
        except Exception:
            pass


def _install_gallery_mousewheel(workspace) -> None:
    canvas = getattr(workspace, "gallery_canvas", None)
    if canvas is None:
        return

    def wheel(event):
        try:
            delta = int(getattr(event, "delta", 0) or 0)
            if delta:
                canvas.yview_scroll(-1 if delta > 0 else 1, "units")
                return "break"
        except Exception:
            return None
        return None

    try:
        canvas.bind("<MouseWheel>", wheel, add="+")
        workspace.gallery_inner.bind("<MouseWheel>", wheel, add="+")
    except Exception:
        pass


def _run_link_refresh(workspace):
    if bool(getattr(workspace, "_phase49_3i21_busy", False)) or bool(getattr(workspace, "_phase49_3i18_busy", False)) or bool(getattr(workspace, "_phase49_3i19_busy", False)):
        workspace.footer_status.set("یک عملیات AI دیگر در حال اجراست")
        return None

    row = workspace.db.product(workspace.product_id)
    if row is None:
        return None
    source_url = str(workspace.source_url.get() or _row_value(row, "source_url", "")).strip()
    if not source_url.startswith(("http://", "https://")):
        messagebox.showwarning("3DPrintHub", "لینک معتبر محصول وجود ندارد.", parent=workspace)
        return None

    # Do not call the layered Workspace save chain here. It caused a large series
    # of commits/UI refreshes before every AI request. Persist only a changed URL.
    if source_url != str(_row_value(row, "source_url", "") or "").strip():
        try:
            workspace.db.update_product(
                workspace.product_id,
                {"source_url": source_url, "normalized_url": normalize_url(source_url)},
            )
            row = workspace.db.product(workspace.product_id)
        except Exception as exc:
            messagebox.showerror("3DPrintHub — لینک محصول", str(exc), parent=workspace)
            return None

    try:
        provider, key, model = workspace._phase49_3e_provider()
        source_snapshot = dict(workspace._source_for_ai() or {})
    except Exception as exc:
        messagebox.showerror("3DPrintHub", str(exc), parent=workspace)
        return None

    selected = link_runtime.images.cap_unique_urls(_list(_row_value(row, "selected_images_json", "[]")))
    categories = workspace.app.get_all_categories()
    source_snapshot["selected_materials"] = selected_material_names(row)
    source_snapshot["selected_colors"] = selected_color_names(row)
    external_id = str(_row_value(row, "external_id", "") or "")

    workspace._phase49_3i21_busy = True
    dialog = link_runtime.ObservableJobDialog(workspace, "تکمیل همه اطلاعات بر اساس لینک محصول")
    workspace._phase49_3i21_job_dialog = dialog
    dialog.event("queued", "عملیات در صف اجرا قرار گرفت", {"url": source_url, "provider": provider, "model": model})

    def worker():
        try:
            if dialog.cancelled.is_set():
                return
            dialog.event("source_fetch", "در حال خواندن صفحه واقعی محصول…")
            from .crawler import parse_product, public_http
            html = public_http(source_url, 25)
            if dialog.cancelled.is_set():
                return
            parsed = parse_product(html, source_url, "", []) or {}
            profile_weight = makerworld_profile_weight_from_html(html, source_url)
            if profile_weight is not None:
                parsed["estimated_weight_grams"] = profile_weight
            facts = normalized_source_facts(parsed, source_url)
            source_title = canonical_source_title(
                str(parsed.get("source_title") or source_snapshot.get("source_title") or _row_value(row, "source_title", "")),
                source_url,
                external_id,
                candidates=(parsed.get("source_title") or "",),
            )
            if not source_title or is_generic_source_title(source_title, external_id):
                raise RuntimeError("عنوان واقعی و معتبر محصول از لینک منبع استخراج نشد")
            current_source = dict(source_snapshot)
            current_source.update({key: value for key, value in facts.items() if key != "source_url"})
            current_source["source_url"] = source_url
            current_source["source_title"] = source_title
            current_source["_grounded_source_facts"] = facts
            dialog.event(
                "source_ready",
                "اطلاعات منبع خوانده شد",
                {
                    "source_title": source_title,
                    "estimated_weight_grams": facts.get("estimated_weight_grams"),
                    "estimated_print_minutes": facts.get("estimated_print_minutes"),
                    "fact_keys": sorted(facts.keys()),
                    "images": len(selected),
                },
            )
            if dialog.cancelled.is_set():
                return
            dialog.event("ai_request", "لینک و داده واقعی منبع برای AI ارسال شد…", {"provider": provider, "model": model})
            pack = AIContentService(key, model, provider, product_id=workspace.product_id).enrich_product(
                current_source,
                categories,
                image_count=len(selected),
                image_urls=selected,
                mode="commerce",
            )
            if dialog.cancelled.is_set():
                return
            persian_title = link_runtime._clean_text(pack.get("title_fa") or "", 300)
            if not persian_title or is_generic_source_title(persian_title, external_id):
                raise RuntimeError("AI عنوان فارسی معتبر برنگرداند؛ هیچ تغییری اعمال نشد")
            preview = {
                "source_title": source_title,
                "title_fa": persian_title,
                "weight_grams": facts.get("estimated_weight_grams"),
                "seo_title_fa": pack.get("seo_title_fa"),
                "seo_description_fa": pack.get("seo_description_fa"),
                "short_description_fa": pack.get("short_description_fa"),
                "image_alt_count": len(pack.get("image_alt_texts") or []),
                "keywords": pack.get("target_keywords_fa") or [],
            }
            dialog.event("received", "پاسخ کامل AI دریافت شد؛ منتظر تأیید برای بروزرسانی فیلدهاست", preview)

            def confirm_apply():
                if dialog.cancelled.is_set():
                    workspace._phase49_3i21_busy = False
                    return
                yes = messagebox.askyesno(
                    "اعمال خروجی لینک + AI",
                    f"عنوان منبع: {source_title}\nعنوان فارسی جدید: {persian_title}\n"
                    f"وزن منبع: {facts.get('estimated_weight_grams') or '—'} گرم\n\n"
                    "محتوا، SEO، متن تصاویر و وزن معتبر منبع بروزرسانی شوند؟\n"
                    "قیمت، موجودی و انتخاب‌های تجاری دست‌نخورده می‌مانند.",
                    parent=dialog.top,
                )
                if not yes:
                    dialog.event("preview", "خروجی دریافت شد اما اپراتور اعمال تغییرات را لغو کرد")
                    workspace._phase49_3i21_busy = False
                    return
                dialog.event("applying", "در حال بروزرسانی فیلدهای محصول…")
                updates = {"source_title": source_title}
                weight = _positive_number(facts.get("estimated_weight_grams"))
                minutes = _positive_number(facts.get("estimated_print_minutes"))
                if weight is not None:
                    updates["estimated_weight_grams"] = weight
                if minutes is not None:
                    updates["estimated_print_minutes"] = minutes
                workspace.db.update_product(workspace.product_id, updates)
                workspace._phase49_3i18_apply_ai(pack, persian_title)
                if hasattr(workspace, "_phase49_3i19_source_title"):
                    workspace._phase49_3i19_source_title.set(source_title)
                if hasattr(workspace, "_phase49_3i18_title"):
                    workspace._phase49_3i18_title.set(persian_title)
                try:
                    workspace.reload()
                except Exception:
                    pass
                dialog.done("محتوا، SEO، تصاویر و داده معتبر منبع بروزرسانی شدند")
                workspace._phase49_3i21_busy = False

            workspace.after(0, confirm_apply)
        except Exception as exc:
            dialog.fail(exc)
            workspace.after(0, lambda: setattr(workspace, "_phase49_3i21_busy", False))

    threading.Thread(
        target=worker,
        daemon=True,
        name=f"catalog-ai-link-{workspace.product_id}",
    ).start()
    return None


def _publication_gate_or_ai(workspace, target_label: str) -> bool:
    row = workspace.db.product(workspace.product_id)
    state = evaluate_readiness(row)
    if state.get("production_ready"):
        return True
    missing = list(state.get("missing") or [])
    detail = "\n".join(f"• {item}" for item in missing[:24]) or "• مورد ناقص نامشخص"
    if _ai_fillable_missing(state):
        use_ai = messagebox.askyesno(
            "3DPrintHub — کسری‌های محصول",
            f"ارسال به {target_label} هنوز آماده نیست.\n\n{detail}\n\n"
            "برای تکمیل عنوان/محتوا/SEO و داده‌های قابل استخراج، «تکمیل همه اطلاعات بر اساس لینک محصول» اجرا شود؟",
            parent=workspace,
        )
        if use_ai:
            workspace._phase49_3i21_link_refresh()
            return False
    try:
        workspace.select_section(_first_incomplete(state))
    except Exception:
        pass
    messagebox.showwarning(
        "3DPrintHub — موارد ناقص",
        f"قبل از ارسال به {target_label} این موارد باقی مانده‌اند:\n\n{detail}\n\n"
        "می‌توانی آزادانه بین همه مراحل جابه‌جا شوی و موارد را تکمیل کنی.",
        parent=workspace,
    )
    return False
