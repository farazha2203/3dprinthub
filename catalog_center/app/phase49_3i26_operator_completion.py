from __future__ import annotations

import json
import os
import re
import shutil
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any

from . import phase49_3c_image_pipeline as images
from . import phase49_3i21_observable_ai_link_refresh as link_runtime
from . import phase49_3i25_product_first_workflow as phase25
from .db import normalize_url, utc_now
from .openai_content import AIContentService
from .phase49_3i18_operator_editing import _list, ai_updates
from .phase49_3i19_source_identity import canonical_source_title
from .phase49_diagnostics import audit_event, redact
from .phase49_readiness_wizard import selected_color_names, selected_material_names

PHASE = "49.3I.26"
AI_TIMEOUT_SECONDS = 120
DEFAULT_IMAGE_LIMIT = 5
CANONICAL_STAGE_ORDER = (
    "quick", "commerce", "images", "content", "specs", "slider", "publish",
)
CANONICAL_STAGE_LABELS = {
    "quick": "۱. اطلاعات پایه",
    "commerce": "۲. سفارش، قیمت و گزینه‌ها",
    "images": "۳. تصاویر",
    "content": "۴. محتوا و SEO",
    "specs": "۵. منبع و مجوز",
    "slider": "۶. اسلایدر صفحه اصلی",
    "publish": "۷. بررسی و انتشار",
}
WORKSPACE_SECTIONS = [
    ("quick", CANONICAL_STAGE_LABELS["quick"]),
    ("commerce", CANONICAL_STAGE_LABELS["commerce"]),
    ("images", CANONICAL_STAGE_LABELS["images"]),
    ("content", CANONICAL_STAGE_LABELS["content"]),
    ("specs", CANONICAL_STAGE_LABELS["specs"]),
    ("publish", CANONICAL_STAGE_LABELS["publish"]),
]
PROGRESS = {
    "queued": 3,
    "source_fetch": 12,
    "source_ready": 30,
    "ai_request": 40,
    "source_recheck": 55,
    "received": 72,
    "preview": 78,
    "applying": 84,
    "image_metadata": 92,
    "completed": 100,
}


def _row_value(row, key: str, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
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


def _valid_http_url(value: str) -> bool:
    return str(value or "").strip().lower().startswith(("http://", "https://"))


def install_progress_dialog() -> None:
    Dialog = link_runtime.ObservableJobDialog
    if getattr(Dialog, "_phase49_3i26_progress", False):
        return
    original_init = Dialog.__init__
    original_event = Dialog.event
    original_done = Dialog.done

    def __init__(self, workspace, title: str):
        original_init(self, workspace, title)
        try:
            self.progress.stop()
            self.progress.configure(mode="determinate", maximum=100, value=0)
            self.percent = tk.StringVar(value="۰٪")
            holder = self.progress.master
            ttk.Label(holder, textvariable=self.percent, font=("Tahoma", 9, "bold")).pack(anchor="e", padx=10, pady=(2, 0))
        except Exception:
            self.percent = None

    def event(self, stage: str, message: str, payload: Any = None):
        percent = int(PROGRESS.get(str(stage), 0) or 0)
        if percent:
            def render_progress():
                try:
                    if self.top.winfo_exists():
                        self.progress.configure(value=percent)
                        if self.percent is not None:
                            self.percent.set(f"{percent}٪")
                except Exception:
                    pass
            self.workspace.after(0, render_progress)
        return original_event(self, stage, message, payload)

    def done(self, message: str):
        def render_progress():
            try:
                if self.top.winfo_exists():
                    self.progress.configure(value=100)
                    if self.percent is not None:
                        self.percent.set("100٪")
            except Exception:
                pass
        self.workspace.after(0, render_progress)
        return original_done(self, message)

    Dialog.__init__ = __init__
    Dialog.event = event
    Dialog.done = done
    Dialog._phase49_3i26_progress = True


def _restore_stage_contract(workspace_class, readiness_module=None) -> None:
    workspace_class.SECTION_LABELS = list(WORKSPACE_SECTIONS)
    if readiness_module is not None:
        try:
            readiness_module.STAGE_LABELS.clear()
            readiness_module.STAGE_LABELS.update(CANONICAL_STAGE_LABELS)
        except Exception:
            pass
    try:
        from . import phase49_3b_guided_wizard as guided
        guided.STAGE_ORDER = tuple(CANONICAL_STAGE_ORDER)
        guided.STAGE_LABELS.clear()
        guided.STAGE_LABELS.update(CANONICAL_STAGE_LABELS)
    except Exception:
        pass


def _page_map(workspace) -> dict[str, Any]:
    return {
        "quick": getattr(workspace, "quick_tab", None),
        "commerce": getattr(workspace, "commerce_tab", None),
        "images": getattr(workspace, "images_tab", None),
        "content": getattr(workspace, "content_tab", None),
        "specs": getattr(workspace, "specs_tab", None),
        "slider": getattr(workspace, "slider_tab", None),
        "publish": getattr(workspace, "publish_tab", None),
    }


def _open_stage_unlocked(workspace, key: str):
    page = _page_map(workspace).get(key)
    if page is None:
        return
    try:
        workspace.nb.select(page)
    except Exception:
        return
    for stage_key, button in getattr(workspace, "_section_buttons", {}).items():
        active = stage_key == key
        try:
            button.configure(
                state="normal",
                bg="#c99a2e" if active else "#0b2238",
                fg="#071827" if active else "#d9e4ee",
                activebackground="#d8ad49" if active else "#123452",
            )
        except Exception:
            pass
    try:
        workspace.after_idle(workspace._phase49_3b_refresh_wizard)
    except Exception:
        pass


def _force_unlocked_wizard(workspace) -> None:
    original = getattr(workspace, "_phase49_3b_refresh_wizard", None)
    if not callable(original) or getattr(workspace, "_phase49_3i26_wizard_wrapped", False):
        return

    def refresh():
        try:
            original()
        finally:
            for button in getattr(workspace, "_section_buttons", {}).values():
                try:
                    button.configure(state="normal")
                except Exception:
                    pass
            try:
                workspace._phase49_3b_next.configure(state="normal")
            except Exception:
                pass

    workspace._phase49_3b_refresh_wizard = refresh
    workspace._phase49_3i26_wizard_wrapped = True


def _toggle_maximized(workspace):
    try:
        current = str(workspace.state())
        workspace.state("normal" if current == "zoomed" else "zoomed")
    except Exception:
        try:
            workspace.attributes("-zoomed", not bool(workspace.attributes("-zoomed")))
        except Exception:
            pass


def _add_maximize_button(workspace):
    if getattr(workspace, "_phase49_3i26_max_button", None) is not None:
        return
    header = None
    for child in workspace.winfo_children():
        try:
            if isinstance(child, tk.Frame) and str(child.cget("bg")) == "#071827":
                header = child
                break
        except Exception:
            continue
    if header is None:
        return
    actions = None
    for child in header.winfo_children():
        try:
            if isinstance(child, tk.Frame) and str(child.pack_info().get("side")) == "right":
                actions = child
                break
        except Exception:
            continue
    if actions is None:
        actions = header
    button = ttk.Button(actions, text="⛶ تمام صفحه", command=lambda: _toggle_maximized(workspace))
    try:
        button.pack(side="left", padx=3)
    except Exception:
        return
    workspace._phase49_3i26_max_button = button


def _vertical_gallery_layout(workspace):
    inner = getattr(workspace, "gallery_inner", None)
    canvas = getattr(workspace, "gallery_canvas", None)
    if inner is None or canvas is None:
        return
    cards = list(getattr(workspace, "_gallery_cards", []) or [])
    for child in list(inner.winfo_children()):
        try:
            if isinstance(child, ttk.Frame):
                child.grid_forget()
        except Exception:
            pass
    for col in range(5):
        try:
            inner.columnconfigure(col, weight=1, uniform="phase49_i26_gallery", minsize=0)
        except Exception:
            pass
    for index, meta in enumerate(cards):
        label = meta.get("label") if isinstance(meta, dict) else None
        card = getattr(label, "master", None) if label is not None else None
        if card is None:
            continue
        try:
            card.grid(row=index // 5, column=index % 5, padx=5, pady=5, sticky="n")
        except Exception:
            pass
    try:
        canvas.configure(xscrollcommand="")
        canvas.xview_moveto(0)
        canvas.itemconfigure(workspace.gallery_window, width=max(1, int(canvas.winfo_width())))
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    except Exception:
        pass
    hbar = getattr(workspace, "_phase49_3g_gallery_hbar", None)
    if hbar is not None:
        try:
            hbar.grid_remove()
        except Exception:
            pass
    try:
        workspace.gallery_page_info.set(f"نمایش همه {len(cards)} تصویر • ۵ تصویر در هر ردیف • اسکرول عمودی")
    except Exception:
        pass


def _install_gallery_behavior(workspace):
    canvas = getattr(workspace, "gallery_canvas", None)
    if canvas is None:
        return
    try:
        canvas.bind("<Configure>", lambda event: (
            canvas.itemconfigure(workspace.gallery_window, width=max(1, int(event.width))),
            workspace.after_idle(lambda: _vertical_gallery_layout(workspace)),
        ), add="+")
    except Exception:
        pass

    def wheel(event):
        delta = 0
        if getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        elif getattr(event, "delta", 0):
            delta = -1 if event.delta > 0 else 1
        if delta:
            try:
                canvas.yview_scroll(delta * 3, "units")
            except Exception:
                pass
            return "break"
        return None

    try:
        canvas.bind("<MouseWheel>", wheel)
        canvas.bind("<Button-4>", wheel)
        canvas.bind("<Button-5>", wheel)
    except Exception:
        pass


def _source_updates(parsed: dict[str, Any], source_url: str, canonical_title: str, facts: dict[str, Any]) -> dict[str, Any]:
    updates: dict[str, Any] = {
        "source_url": source_url,
        "normalized_url": normalize_url(source_url),
        "source_title": canonical_title,
    }
    for key in (
        "estimated_weight_grams", "estimated_print_minutes", "author_name",
        "license_name", "license_url", "source_description", "source_short_description",
    ):
        value = parsed.get(key)
        if value not in (None, "", [], {}):
            updates[key] = value
    if facts.get("estimated_weight_grams") not in (None, ""):
        updates["estimated_weight_grams"] = facts["estimated_weight_grams"]
    if facts.get("estimated_print_minutes") not in (None, ""):
        updates["estimated_print_minutes"] = facts["estimated_print_minutes"]
    return updates


def _build_local_image_metadata(row, updates: dict[str, Any], pack: dict[str, Any]) -> tuple[list[dict], list[str]]:
    selected = images.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")), 20)
    existing = {
        str(item.get("source_url") or ""): dict(item)
        for item in _json_list(_row_value(row, images.IMAGE_METADATA_COLUMN, "[]"))
        if isinstance(item, dict)
    }
    alts = _json_list(updates.get("image_alt_texts_json", "[]"))
    keywords = _json_list(updates.get("keywords_json", "[]"))
    title = str(updates.get("seo_title_fa") or updates.get("title_fa") or _row_value(row, "title_fa", "") or "محصول چاپ سه‌بعدی").strip()
    caption = str(updates.get("short_description_fa") or updates.get("seo_description_fa") or "").strip()
    creator = str(_row_value(row, "author_name", "") or _row_value(row, "source_name", "") or _row_value(row, "source_code", "") or "Unknown creator").strip()
    source_url = str(_row_value(row, "source_url", "") or "").strip()
    license_name = str(_row_value(row, "license_name", "") or "").strip()
    license_url = str(_row_value(row, "license_url", "") or "").strip()
    metadata: list[dict] = []
    missing_local: list[str] = []
    for index, url in enumerate(selected, start=1):
        item = existing.get(url, {"source_url": url})
        item["source_url"] = url
        item["source_page_url"] = source_url
        item["seo_filename"] = str(item.get("seo_filename") or images.planned_seo_filename(row, index))
        item["alt_text"] = str(alts[index - 1] if index - 1 < len(alts) and alts[index - 1] else f"{updates.get('title_fa') or title} - تصویر {index}")[:220]
        item["title"] = title[:220]
        item["caption"] = caption[:500]
        item["keywords"] = [str(x).strip().lstrip("#") for x in keywords if str(x).strip()][:16]
        item["creator"] = creator[:220]
        item["copyright_holder"] = str(item.get("copyright_holder") or creator)[:220]
        item["publisher"] = "3DPrintHub"
        item["editor"] = "3DPrintHub Catalog Center"
        item["license_name"] = license_name[:220]
        item["license_url"] = license_url
        item["credit_line"] = f"Creator: {creator} | Source: {source_url} | Publisher/Editor: 3DPrintHub"
        item["metadata_ready"] = False
        item["seo_signature"] = ""
        metadata.append(item)
        if not images.strict_source_local_image(row, url):
            missing_local.append(url)
    return metadata, missing_local


def _apply_unified_result(workspace, parsed: dict[str, Any], source_url: str, facts: dict[str, Any], canonical_title: str, pack: dict[str, Any], dialog) -> None:
    row = workspace.db.product(workspace.product_id)
    persian_title = str(pack.get("title_fa") or "").strip()
    if not persian_title:
        raise RuntimeError("AI عنوان فارسی معتبر برنگرداند.")
    source_updates = _source_updates(parsed, source_url, canonical_title, facts)
    workspace.db.update_product(workspace.product_id, source_updates)
    row = workspace.db.product(workspace.product_id)
    updates = ai_updates(row, pack, persian_title)
    suggested_slug = str(pack.get("suggested_category_slug") or "").strip()
    allowed = {str(item.get("slug") or "") for item in workspace.db.categories()} if hasattr(workspace.db, "categories") else set()
    if suggested_slug and suggested_slug in allowed:
        updates["local_category_slug"] = suggested_slug
    metadata, missing_local = _build_local_image_metadata(row, updates, pack)
    if metadata:
        updates[images.IMAGE_METADATA_COLUMN] = json.dumps(metadata, ensure_ascii=False)
    dialog.event("image_metadata", "متن و SEO تصاویر از اطلاعات محصول ساخته شد؛ هیچ تصویر به AI ارسال نشد.", {
        "selected_images": len(metadata), "local_files_missing": len(missing_local),
    })
    workspace.db.update_product(workspace.product_id, updates)

    finalized = False
    if metadata and not missing_local:
        try:
            images.finalize_selected_images(workspace.db, workspace.product_id)
            finalized = True
        except Exception as exc:
            audit_event(
                "images", "unified_local_finalize_failed", status="warning", level="WARNING",
                product_id=workspace.product_id, source_file=__file__, message=redact(exc),
            )
    elif missing_local:
        audit_event(
            "images", "unified_local_finalize_deferred", status="warning", level="WARNING",
            product_id=workspace.product_id, source_file=__file__,
            message=f"{len(missing_local)} selected image(s) have no local source; no network image download attempted by AI completion",
        )
    workspace.reload()
    try:
        workspace._phase49_3e_refresh_tasks()
    except Exception:
        pass
    suffix = " و فایل‌های SEO محلی نهایی شد" if finalized else "؛ متن متای تصاویر ذخیره شد"
    workspace.footer_status.set(f"تکمیل یکپارچه محصول انجام شد{suffix}")


def _run_unified_link_refresh(workspace):
    if bool(getattr(workspace, "_phase49_3i26_busy", False)):
        workspace.footer_status.set("یک عملیات تکمیل محصول در حال اجراست")
        return
    source_url = str(getattr(workspace, "source_url", tk.StringVar()).get() or "").strip()
    if not _valid_http_url(source_url):
        messagebox.showwarning("3DPrintHub", "لینک واقعی محصول معتبر نیست.", parent=workspace)
        return
    try:
        provider, key, model = workspace._phase49_3e_provider()
    except Exception as exc:
        messagebox.showerror("3DPrintHub", str(exc), parent=workspace)
        return
    row = workspace.db.product(workspace.product_id)
    selected = images.cap_unique_urls(_json_list(_row_value(row, "selected_images_json", "[]")), 20)
    categories = [dict(item) for item in workspace.db.categories()]
    try:
        selected_materials = selected_material_names(row)
    except Exception:
        selected_materials = []
    try:
        selected_colors = selected_color_names(row)
    except Exception:
        selected_colors = []
    workspace._phase49_3i26_busy = True
    dialog = link_runtime.ObservableJobDialog(workspace, "تکمیل همه اطلاعات بر اساس لینک محصول")
    dialog.event("queued", "مرحله ۱/۷ — درخواست آماده شد؛ داده قبلی تا تأیید نهایی تغییر نمی‌کند.", {
        "provider": provider, "model": model, "source_url": source_url,
        "images_sent_to_ai": 0, "timeout_seconds": AI_TIMEOUT_SECONDS,
    })

    def worker():
        try:
            from . import crawler
            dialog.event("source_fetch", "مرحله ۲/۷ — در حال خواندن لینک واقعی محصول و اطلاعات نوشتاری منبع…")
            html = crawler.public_http(source_url, 30)
            if dialog.cancelled.is_set():
                return
            parsed = crawler.parse_product(html, source_url) or {}
            exact_weight = phase25.makerworld_profile_weight_from_html(html, source_url)
            if exact_weight is not None:
                parsed["estimated_weight_grams"] = exact_weight
            facts = phase25.normalized_source_facts(parsed, source_url)
            canonical_title = canonical_source_title(
                source_url,
                str(parsed.get("external_id") or _row_value(row, "external_id", "") or ""),
                candidates=[parsed.get("source_title")],
                current_title=str(_row_value(row, "source_title", "") or ""),
            )
            if not canonical_title:
                raise RuntimeError("عنوان واقعی محصول از لینک قابل تشخیص نبود.")
            dialog.event("source_ready", "مرحله ۳/۷ — لینک خوانده شد؛ عنوان/سازنده/گروه/توضیحات/وزن/زمان چاپ استخراج شد.", {
                "source_title": canonical_title,
                "author_name": facts.get("author_name") or "",
                "source_category": facts.get("source_category") or "",
                "estimated_weight_grams": facts.get("estimated_weight_grams"),
                "estimated_print_minutes": facts.get("estimated_print_minutes"),
            })
            current_source = {
                "source_title": canonical_title,
                "source_description": str(parsed.get("source_description") or facts.get("source_description") or ""),
                "source_categories": parsed.get("source_categories") or parsed.get("source_categories_json") or [],
                "source_category": parsed.get("source_category") or "",
                "source_specs": parsed.get("source_specs") or parsed.get("source_specs_json") or {},
                "source_tags": parsed.get("source_tags") or parsed.get("tags") or [],
                "author_name": parsed.get("author_name") or "",
                "license_name": parsed.get("license_name") or "",
                "source_price": parsed.get("source_price"),
                "source_currency": parsed.get("source_currency") or "",
                "estimated_weight_grams": facts.get("estimated_weight_grams"),
                "estimated_print_minutes": facts.get("estimated_print_minutes"),
                "source_url": source_url,
                "selected_materials": selected_materials,
                "selected_colors": selected_colors,
                "_grounded_source_facts": facts,
            }
            dialog.event("ai_request", "مرحله ۴/۷ — اطلاعات نوشتاری محصول برای AI ارسال شد؛ تصاویر ارسال نمی‌شوند.", {
                "provider": provider, "model": model, "images_sent_to_ai": 0,
            })
            service = AIContentService(key, model=model, provider=provider, product_id=workspace.product_id)
            pack = service.enrich_product(
                current_source,
                categories,
                image_count=len(selected),
                image_urls=[],
                mode="commerce",
            )
            if dialog.cancelled.is_set():
                return
            dialog.event("received", "مرحله ۵/۷ — پاسخ AI دریافت و اعتبارسنجی شد.", {
                "title_fa": pack.get("title_fa") or "",
                "seo_title_fa": pack.get("seo_title_fa") or "",
                "image_alt_count": len(pack.get("image_alt_texts") or []),
            })

            def preview_and_apply():
                if dialog.cancelled.is_set() or not workspace.winfo_exists():
                    return
                dialog.event("preview", "مرحله ۶/۷ — پیش‌نمایش آماده است؛ با تأیید، تمام متن/SEO/متای تصاویر یک‌جا اعمال می‌شود.")
                summary = (
                    f"عنوان منبع: {canonical_title}\n"
                    f"عنوان فارسی: {pack.get('title_fa') or ''}\n"
                    f"سازنده: {facts.get('author_name') or '—'}\n"
                    f"گروه منبع: {facts.get('source_category') or '—'}\n"
                    f"وزن: {facts.get('estimated_weight_grams') or '—'} گرم\n"
                    f"زمان چاپ: {facts.get('estimated_print_minutes') or '—'} دقیقه\n"
                    f"SEO Title: {pack.get('seo_title_fa') or ''}\n"
                    f"Alt تصاویر: {len(pack.get('image_alt_texts') or [])}\n\n"
                    "تصاویر به AI ارسال نشده‌اند. فقط متن SEO/Metadata تصاویر بر اساس همین محصول ساخته می‌شود.\n\n"
                    "این اطلاعات روی محصول اعمال شود؟"
                )
                if not messagebox.askyesno("پیش‌نمایش تکمیل محصول", summary, parent=dialog.top):
                    workspace._phase49_3i26_busy = False
                    dialog.cancel()
                    return
                dialog.event("applying", "مرحله ۷/۷ — در حال اعمال یکپارچه اطلاعات محصول، SEO و متای تصاویر…")
                try:
                    _apply_unified_result(workspace, parsed, source_url, facts, canonical_title, pack, dialog)
                    dialog.done("تکمیل کامل محصول انجام شد — 100٪")
                except Exception as exc:
                    dialog.fail(exc)
                finally:
                    workspace._phase49_3i26_busy = False

            workspace.after(0, preview_and_apply)
        except Exception as exc:
            text = str(exc)
            try:
                if "timeout" in text.casefold() or "مهلت" in text:
                    dialog.event("source_recheck", "پاسخ AI نرسید؛ لینک منبع دوباره بررسی می‌شود تا مشکل منبع از Provider جدا شود.")
                    from . import crawler
                    retry_html = crawler.public_http(source_url, 20)
                    retry = crawler.parse_product(retry_html, source_url) or {}
                    dialog.event("source_recheck", "لینک منبع سالم است؛ مشکل در پاسخ AI/Provider بوده است.", {
                        "source_title": retry.get("source_title") or "", "source_bytes": len(retry_html or ""),
                    })
            except Exception as source_exc:
                dialog.event("source_recheck", "بازخوانی مجدد لینک منبع هم ناموفق بود.", {"error": redact(source_exc)})
            workspace.after(0, lambda e=exc: dialog.fail(e))
            workspace.after(0, lambda: setattr(workspace, "_phase49_3i26_busy", False))

    threading.Thread(target=worker, daemon=True).start()


def install_workspace(workspace_class, readiness_module=None) -> None:
    if getattr(workspace_class, "_phase49_3i26_operator_completion", False):
        return
    os.environ["CATALOG_AI_TIMEOUT_SECONDS"] = str(AI_TIMEOUT_SECONDS)
    install_progress_dialog()
    _restore_stage_contract(workspace_class, readiness_module)

    original_init = workspace_class.__init__
    original_refresh_gallery = workspace_class.refresh_gallery

    def select_section(self, key: str):
        _open_stage_unlocked(self, key)

    def refresh_gallery(self):
        self.gallery_page_size = 1000
        self.gallery_page = 0
        result = original_refresh_gallery(self)
        self.after_idle(lambda: _vertical_gallery_layout(self))
        return result

    def vertical_3g_layout(self, preserve_fraction=None):
        _vertical_gallery_layout(self)

    def __init__(self, app, product_id):
        self._phase49_3i26_busy = False
        original_init(self, app, product_id)
        _force_unlocked_wizard(self)
        self.select_section("quick")
        self.gallery_page_size = 1000
        self.gallery_page = 0
        _install_gallery_behavior(self)
        _add_maximize_button(self)
        self.after_idle(lambda: self.refresh_gallery())

    workspace_class.select_section = select_section
    workspace_class.refresh_gallery = refresh_gallery
    workspace_class._phase49_3g_layout_gallery_cards = vertical_3g_layout
    workspace_class._phase49_3i21_link_refresh = lambda self: _run_unified_link_refresh(self)
    workspace_class.__init__ = __init__
    workspace_class._phase49_3i26_operator_completion = True


def _archive_product(db, product_id: int) -> None:
    before = db.product(int(product_id))
    if before is None:
        return
    db.update_product(int(product_id), {
        "workflow_status": "archived",
        "source_state": "archived",
        "upload_ready": 0,
        "needs_update": 0,
    })
    try:
        db.save_history(int(product_id), "archived", dict(before), dict(db.product(int(product_id))), "Archived from Products gallery")
    except Exception:
        pass


def _restore_archive(db, product_id: int) -> None:
    before = db.product(int(product_id))
    if before is None:
        return
    db.update_product(int(product_id), {
        "workflow_status": "review" if not str(_row_value(before, "server_id", "")) else "uploaded",
        "source_state": "active",
        "upload_ready": 0,
    })
    try:
        db.save_history(int(product_id), "archive_restored", dict(before), dict(db.product(int(product_id))), "Restored from Products archive")
    except Exception:
        pass


def install_database(database_class) -> None:
    if getattr(database_class, "_phase49_3i26_archive_contract", False):
        return
    original_products = database_class.products

    def products(self, filter_name="all", source_code="", search=""):
        rows = original_products(self, filter_name=filter_name if filter_name != "archived" else "all", source_code=source_code, search=search)
        if filter_name == "archived":
            return [row for row in self.conn.execute(
                "SELECT * FROM products WHERE is_blocked=0 AND workflow_status='archived' ORDER BY updated_at DESC,id DESC"
            ) if (not source_code or row["source_code"] == source_code) and (not search or search.casefold() in " ".join(str(row[k] or "") for k in ("source_title", "title_fa", "external_id", "source_url")).casefold())]
        return [row for row in rows if str(_row_value(row, "workflow_status", "")) != "archived"]

    database_class.products = products
    database_class.archive_product = _archive_product
    database_class.restore_archived_product = _restore_archive
    database_class._phase49_3i26_archive_contract = True


def _selected_product_ids(app) -> list[int]:
    return sorted(int(x) for x in getattr(app, "_phase49_3i26_product_selection", set()) or set())


def _refresh_product_selection(app):
    try:
        app._phase49_3i26_selection_label.set(f"{len(_selected_product_ids(app))} محصول انتخاب شده")
    except Exception:
        pass


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i26_product_archive_ui", False):
        return
    original_modernize = app_class._modernize_products_page
    original_render = app_class._phase49_3i_render_gallery

    def _modernize_products_page(self):
        original_modernize(self)
        self._phase49_3i26_product_selection = set()
        shell = getattr(getattr(self, "_phase49_3i_gallery_canvas", None), "master", None)
        if shell is None:
            return
        bar = ttk.LabelFrame(self.products_tab, text="انتخاب گروهی / آرشیو محصولات", padding=7, style="Card.TLabelframe")
        try:
            bar.pack(fill="x", pady=(0, 7), before=shell)
        except Exception:
            bar.pack(fill="x", pady=(0, 7))
        self._phase49_3i26_selection_label = tk.StringVar(value="0 محصول انتخاب شده")
        ttk.Label(bar, textvariable=self._phase49_3i26_selection_label).pack(side="right", padx=6)
        ttk.Button(bar, text="انتخاب همه دیده‌شده", command=self._phase49_3i26_select_visible).pack(side="left", padx=3)
        ttk.Button(bar, text="پاک‌کردن انتخاب", command=self._phase49_3i26_clear_selection).pack(side="left", padx=3)
        ttk.Button(bar, text="آرشیو انتخاب‌شده‌ها", command=self._phase49_3i26_archive_selected, style="Warning.TButton").pack(side="left", padx=3)
        ttk.Button(bar, text="حذف/بلاک انتخاب‌شده‌ها", command=self._phase49_3i26_block_selected, style="Danger.TButton").pack(side="left", padx=3)

    def _phase49_3i_render_gallery(self):
        result = original_render(self)
        tree = getattr(self, "product_tree", None)
        cards = list(getattr(self, "_phase49_3i_gallery_cards", []) or [])
        iids = list(tree.get_children()) if tree is not None else []
        for card, iid in zip(cards, iids):
            try:
                product_id = int(iid)
            except Exception:
                continue
            row = self.db.product(product_id)
            if row is None:
                continue
            published_or_edited = bool(str(_row_value(row, "server_id", "") or "").strip())
            try:
                card.configure(highlightbackground="white" if published_or_edited else "#dbe3ea")
            except Exception:
                pass
            var = tk.IntVar(value=1 if product_id in self._phase49_3i26_product_selection else 0)
            check = tk.Checkbutton(
                card, text="انتخاب محصول", variable=var, bg="white", anchor="e",
                command=lambda pid=product_id, v=var: self._phase49_3i26_toggle_product(pid, bool(v.get())),
            )
            check.pack(fill="x", pady=(5, 0))
        return result

    def toggle(self, product_id: int, selected: bool):
        if selected:
            self._phase49_3i26_product_selection.add(int(product_id))
        else:
            self._phase49_3i26_product_selection.discard(int(product_id))
        _refresh_product_selection(self)

    def select_visible(self):
        tree = getattr(self, "product_tree", None)
        if tree is not None:
            for iid in tree.get_children():
                try:
                    self._phase49_3i26_product_selection.add(int(iid))
                except Exception:
                    pass
        _refresh_product_selection(self)
        self._phase49_3i_render_gallery()

    def clear_selection(self):
        self._phase49_3i26_product_selection.clear()
        _refresh_product_selection(self)
        self._phase49_3i_render_gallery()

    def archive_selected(self):
        ids = _selected_product_ids(self)
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا محصول‌ها را انتخاب کن.", parent=self)
            return
        if not messagebox.askyesno("آرشیو محصولات", f"{len(ids)} محصول از فهرست فعال آرشیو شوند؟\nاین کار محصول منتشرشده را از سایت حذف نمی‌کند.", parent=self):
            return
        for product_id in ids:
            self.db.archive_product(product_id)
        self._phase49_3i26_product_selection.clear()
        self.refresh_products()
        _refresh_product_selection(self)

    def block_selected(self):
        ids = _selected_product_ids(self)
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا محصول‌ها را انتخاب کن.", parent=self)
            return
        if not messagebox.askyesno(
            "حذف / جلوگیری از دریافت مجدد",
            f"{len(ids)} محصول از Catalog فعال حذف و بلاک شوند؟\nهویت و لینک منبع نگه داشته می‌شود تا دوباره دریافت نشوند. فایل‌های فیزیکی پاک نمی‌شوند.",
            parent=self,
        ):
            return
        for product_id in ids:
            self.db.block_product(product_id, "Operator removed product; source identity retained to prevent re-import")
        self._phase49_3i26_product_selection.clear()
        self.refresh_products()
        try:
            self.refresh_blocked()
        except Exception:
            pass
        _refresh_product_selection(self)

    app_class._modernize_products_page = _modernize_products_page
    app_class._phase49_3i_render_gallery = _phase49_3i_render_gallery
    app_class._phase49_3i26_toggle_product = toggle
    app_class._phase49_3i26_select_visible = select_visible
    app_class._phase49_3i26_clear_selection = clear_selection
    app_class._phase49_3i26_archive_selected = archive_selected
    app_class._phase49_3i26_block_selected = block_selected
    app_class._phase49_3i26_product_archive_ui = True


def install_extractor(page_extractor_module) -> None:
    """Default new acquisitions to five source images and add one page screenshot.

    The screenshot is local-only and is appended after the normal source-image cap,
    so five source photos remain the default selection while the screenshot is an
    extra non-selected gallery reference.
    """
    if getattr(page_extractor_module, "_phase49_3i26_screenshot", False):
        return
    original = page_extractor_module.extract_direct_link

    async def extract_direct_link(url, output_dir, profile_dir, *, headed=True, download_images=True, image_limit=DEFAULT_IMAGE_LIMIT):
        limit = DEFAULT_IMAGE_LIMIT if image_limit in (None, "") else int(image_limit)
        result = await original(
            url, output_dir, profile_dir,
            headed=headed, download_images=download_images, image_limit=limit,
        )
        try:
            from .classic_methods import collect_classic_exact
            capture_dir = Path(output_dir) / "source_page_capture"
            capture = await collect_classic_exact(url, capture_dir, headed=False, download_images=False)
            screenshot = Path(str(capture.get("screenshot_path") or ""))
            if screenshot.is_file():
                image_dir = Path(output_dir) / "images"
                image_dir.mkdir(parents=True, exist_ok=True)
                target = image_dir / "source-page-screenshot.png"
                shutil.copy2(screenshot, target)
                local_url = "local://source-page-screenshot.png"
                urls = _json_list(result.get("images_json"))
                if local_url not in urls:
                    urls.append(local_url)
                result["images_json"] = json.dumps(urls, ensure_ascii=False)
                result["source_page_screenshot"] = str(target)
        except Exception as exc:
            audit_event(
                "acquisition", "source_page_screenshot_failed", status="warning", level="WARNING",
                source_file=__file__, message=redact(exc), detail={"url": url},
            )
        return result

    page_extractor_module.extract_direct_link = extract_direct_link
    page_extractor_module._phase49_3i26_screenshot = True
