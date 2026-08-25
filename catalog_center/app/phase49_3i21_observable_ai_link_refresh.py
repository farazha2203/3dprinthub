from __future__ import annotations

import json
import os
import socket
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Callable

from . import ai_providers
from . import phase49_3c_image_pipeline as images
from .openai_content import AIContentService
from .phase49_3i18_operator_editing import _list, _v
from .phase49_3i19_source_identity import canonical_source_title, is_generic_source_title
from .phase49_diagnostics import audit_event, export_diagnostic_bundle, redact
from .phase49_readiness_wizard import selected_color_names, selected_material_names

PHASE = "49.3I.21"
DEFAULT_AI_TIMEOUT_SECONDS = 75
MIN_AI_TIMEOUT_SECONDS = 20
MAX_AI_TIMEOUT_SECONDS = 120
PANEL_TITLE = "AI حرفه‌ای — تکمیل کامل از لینک + عیب‌یابی زنده"


def configured_ai_timeout_seconds() -> int:
    raw = str(os.environ.get("CATALOG_AI_TIMEOUT_SECONDS", DEFAULT_AI_TIMEOUT_SECONDS) or "").strip()
    try:
        value = int(raw)
    except Exception:
        value = DEFAULT_AI_TIMEOUT_SECONDS
    return max(MIN_AI_TIMEOUT_SECONDS, min(MAX_AI_TIMEOUT_SECONDS, value))


def _row_value(row, key: str, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
    except Exception:
        value = default
    return default if value is None else value


def _clean_text(value: Any, limit: int = 12000) -> str:
    return " ".join(str(value or "").split())[:limit]


def _safe_fact(value: Any, limit: int = 5000):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return _clean_text(value, limit) if isinstance(value, str) else value
    if isinstance(value, list):
        return [_safe_fact(item, 1000) for item in value[:40]]
    if isinstance(value, dict):
        return {str(k)[:120]: _safe_fact(v, 1500) for k, v in list(value.items())[:60]}
    return _clean_text(value, limit)


def normalized_source_facts(parsed: dict[str, Any], source_url: str) -> dict[str, Any]:
    """Keep only source facts that are useful for content generation.

    This deliberately excludes credentials/cookies/headers/raw HTML. It is also a
    pure function so the link-grounding contract can be regression-tested without
    network access.
    """
    parsed = dict(parsed or {})
    allowed = (
        "source_title", "source_description", "source_category", "source_categories",
        "source_specs", "source_tags", "author_name", "license_name", "source_price",
        "source_currency", "external_id", "model_id", "profile_id", "download_count",
        "like_count", "print_count", "published_at", "updated_at",
    )
    facts = {key: _safe_fact(parsed.get(key)) for key in allowed if parsed.get(key) not in (None, "", [], {})}
    facts["source_url"] = str(source_url or "").strip()[:2000]
    return facts


def grounded_description(source_description: str, source_url: str, facts: dict[str, Any]) -> str:
    compact = json.dumps(facts or {}, ensure_ascii=False, separators=(",", ":"), default=str)
    return (
        "مرجع قطعی این درخواست همان صفحه محصول زیر است. هویت محصول را از این لینک و داده‌های استخراج‌شده حفظ کن؛ "
        "اگر داده‌ای در منبع نیست حدس نزن.\n"
        f"SOURCE_URL: {str(source_url or '').strip()}\n"
        f"SOURCE_FACTS_JSON: {compact[:14000]}\n\n"
        f"SOURCE_DESCRIPTION: {str(source_description or '').strip()}"
    ).strip()


def _install_provider_guard() -> None:
    if getattr(ai_providers, "_phase49_3i21_provider_guard", False):
        return
    original = ai_providers._json_request

    def guarded_json_request(
        url: str,
        key: str,
        *,
        payload: dict[str, Any] | None = None,
        method: str = "GET",
        timeout: int = 120,
        provider: str = "",
        model: str = "",
        operation: str = "",
        product_id: int | None = None,
    ) -> dict[str, Any]:
        requested = int(timeout or DEFAULT_AI_TIMEOUT_SECONDS)
        effective = min(requested, configured_ai_timeout_seconds()) if method.upper() != "GET" else min(requested, 45)
        effective = max(MIN_AI_TIMEOUT_SECONDS, effective)
        started = time.perf_counter()
        audit_event(
            "ai",
            "request_start",
            status="running",
            product_id=product_id,
            source_file=__file__,
            message=f"{provider}/{model} {operation or method.lower()} started; timeout={effective}s",
            detail={"endpoint": url, "method": method, "payload_keys": sorted((payload or {}).keys()), "timeout_seconds": effective},
        )
        try:
            result = original(
                url,
                key,
                payload=payload,
                method=method,
                timeout=effective,
                provider=provider,
                model=model,
                operation=operation,
                product_id=product_id,
            )
            audit_event(
                "ai",
                "request_finish",
                status="ok",
                product_id=product_id,
                source_file=__file__,
                message=f"{provider}/{model} {operation or method.lower()} completed",
                detail={"duration_ms": int((time.perf_counter() - started) * 1000)},
            )
            return result
        except (TimeoutError, socket.timeout) as exc:
            elapsed = int((time.perf_counter() - started) * 1000)
            audit_event(
                "ai",
                "request_timeout",
                status="timeout",
                level="ERROR",
                product_id=product_id,
                source_file=__file__,
                message=f"AI request exceeded {effective}s: {redact(exc)}",
                detail={"duration_ms": elapsed, "timeout_seconds": effective, "endpoint": url},
            )
            raise RuntimeError(
                f"پاسخ AI در مهلت {effective} ثانیه دریافت نشد. برنامه قفل نشده؛ درخواست متوقف شد. "
                "Diagnostics را باز کن تا Provider/Model/مرحله دقیق مشخص باشد."
            ) from exc
        except Exception as exc:
            audit_event(
                "ai",
                "request_finish",
                status="error",
                level="ERROR",
                product_id=product_id,
                source_file=__file__,
                message=redact(exc),
                detail={"duration_ms": int((time.perf_counter() - started) * 1000), "endpoint": url},
            )
            raise

    ai_providers._json_request = guarded_json_request
    ai_providers._phase49_3i21_provider_guard = True


def _install_content_grounding() -> None:
    if getattr(AIContentService, "_phase49_3i21_link_grounding", False):
        return
    original = AIContentService.enrich_product

    def enrich_product(self, source, local_categories, image_count=0, image_urls=None, mode="commerce"):
        source = dict(source or {})
        source_url = str(source.get("source_url") or "").strip()
        facts = source.pop("_grounded_source_facts", None)
        if source_url:
            source["source_description"] = grounded_description(
                str(source.get("source_description") or ""),
                source_url,
                facts if isinstance(facts, dict) else {"source_title": source.get("source_title") or ""},
            )
        return original(self, source, local_categories, image_count=image_count, image_urls=image_urls, mode=mode)

    AIContentService.enrich_product = enrich_product
    AIContentService._phase49_3i21_link_grounding = True


class ObservableJobDialog:
    def __init__(self, workspace, title: str):
        self.workspace = workspace
        self.cancelled = threading.Event()
        self.started = time.monotonic()
        self.top = tk.Toplevel(workspace)
        self.top.title(title)
        self.top.geometry("820x570")
        self.top.minsize(720, 480)
        self.top.transient(workspace)
        self.status = tk.StringVar(value="آماده شروع")
        self.elapsed = tk.StringVar(value="00:00")
        head = ttk.Frame(self.top, padding=10); head.pack(fill="x")
        ttk.Label(head, textvariable=self.status, font=("Tahoma", 10, "bold")).pack(side="left")
        ttk.Label(head, textvariable=self.elapsed).pack(side="right")
        self.progress = ttk.Progressbar(self.top, mode="indeterminate"); self.progress.pack(fill="x", padx=10); self.progress.start(12)
        self.text = tk.Text(self.top, wrap="word", height=24); self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.configure(state="disabled")
        foot = ttk.Frame(self.top, padding=(10, 0, 10, 10)); foot.pack(fill="x")
        ttk.Button(foot, text="توقف انتظار", command=self.cancel).pack(side="left")
        ttk.Button(foot, text="کپی گزارش", command=self.copy_report).pack(side="left", padx=5)
        ttk.Button(foot, text="بستن", command=self.top.destroy).pack(side="right")
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        self._tick()

    def _tick(self):
        if not self.top.winfo_exists():
            return
        seconds = int(time.monotonic() - self.started)
        self.elapsed.set(f"{seconds // 60:02d}:{seconds % 60:02d}")
        self.top.after(500, self._tick)

    def event(self, stage: str, message: str, payload: Any = None):
        def render():
            if not self.top.winfo_exists():
                return
            self.status.set(message)
            stamp = time.strftime("%H:%M:%S")
            extra = ""
            if payload not in (None, "", {}, []):
                try: extra = "\n" + json.dumps(payload, ensure_ascii=False, indent=2, default=str)[:12000]
                except Exception: extra = "\n" + str(payload)[:12000]
            self.text.configure(state="normal")
            self.text.insert("end", f"[{stamp}] {stage}: {message}{extra}\n\n")
            self.text.see("end")
            self.text.configure(state="disabled")
        self.workspace.after(0, render)
        audit_event(
            "ai_job", stage, status="cancelled" if self.cancelled.is_set() else "running",
            product_id=getattr(self.workspace, "product_id", None), source_file=__file__, message=message,
            detail=payload if isinstance(payload, dict) else {},
        )

    def done(self, message: str):
        def render():
            if self.top.winfo_exists():
                self.progress.stop(); self.status.set(message)
        self.workspace.after(0, render)
        audit_event("ai_job", "completed", product_id=getattr(self.workspace, "product_id", None), source_file=__file__, message=message)

    def fail(self, exc: Exception):
        text = redact(exc)
        def render():
            if self.top.winfo_exists():
                self.progress.stop(); self.status.set("عملیات ناموفق شد — داده قبلی حفظ شد")
                self.text.configure(state="normal"); self.text.insert("end", f"\nخطا: {text}\n"); self.text.see("end"); self.text.configure(state="disabled")
                messagebox.showerror("خطای AI", text, parent=self.top)
        self.workspace.after(0, render)
        audit_event("ai_job", "failed", status="error", level="ERROR", product_id=getattr(self.workspace, "product_id", None), source_file=__file__, message=text)

    def cancel(self):
        self.cancelled.set()
        self.event("cancel", "اپراتور ادامه نتیجه این درخواست را لغو کرد. پاسخ دیررس روی محصول اعمال نخواهد شد.")
        try: self.progress.stop()
        except Exception: pass
        self.status.set("لغو شد؛ اگر درخواست شبکه در حال خروج باشد نتیجه آن نادیده گرفته می‌شود")

    def copy_report(self):
        try:
            text = self.text.get("1.0", "end-1c")
            self.top.clipboard_clear(); self.top.clipboard_append(redact(text))
            self.status.set("گزارش عیب‌یابیِ بدون Secret کپی شد")
        except Exception:
            pass


def _find_expand_anchor(parent):
    for child in parent.winfo_children():
        try:
            if child.winfo_manager() != "pack":
                continue
            info = child.pack_info()
            if str(info.get("expand", "0")).lower() in {"1", "true", "yes"}:
                return child
        except Exception:
            continue
    return None


def install(workspace_class) -> None:
    _install_provider_guard()
    _install_content_grounding()
    if getattr(workspace_class, "_phase49_3i21_observable_ai_installed", False):
        return

    original_init = workspace_class.__init__

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        self._phase49_3i21_busy = False
        self._phase49_3i21_build_ui()

    def build_ui(self):
        parent = getattr(self, "content_tab", None)
        if parent is None or getattr(self, "_phase49_3i21_panel", None) is not None:
            return
        frame = ttk.LabelFrame(parent, text=PANEL_TITLE, padding=8, style="Card.TLabelframe")
        anchor = _find_expand_anchor(parent)
        if anchor is not None: frame.pack(fill="x", pady=(0, 8), before=anchor)
        else: frame.pack(fill="x", pady=(0, 8))
        frame.columnconfigure(0, weight=1)
        ttk.Label(
            frame,
            text="لینک منبع → بازخوانی واقعی صفحه → AI با داده منبع → پیش‌نمایش → اعمال یکپارچه متن، SEO و Metadata تصاویر",
            style="SubHeader.TLabel",
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=4, pady=(0, 6))
        ttk.Button(
            frame, text="🌐 تکمیل همه اطلاعات بر اساس لینک محصول",
            command=self._phase49_3i21_link_refresh, style="Success.TButton",
        ).grid(row=1, column=0, sticky="w", padx=4)
        ttk.Button(frame, text="🧾 خروجی Diagnostics", command=self._phase49_3i21_export_diagnostics).grid(row=1, column=1, sticky="w", padx=4)
        ttk.Label(frame, text=f"Timeout هر درخواست AI: حداکثر {configured_ai_timeout_seconds()} ثانیه؛ UI مسدود نمی‌شود.").grid(row=1, column=2, sticky="e", padx=4)
        self._phase49_3i21_panel = frame

    def export_diagnostics(self):
        try:
            root = Path(__file__).resolve().parents[2]
            path = export_diagnostic_bundle(root, product_id=self.product_id)
            self.footer_status.set(f"Diagnostics ذخیره شد: {path}")
            try:
                if os.name == "nt": os.startfile(str(path.parent))  # type: ignore[attr-defined]
            except Exception:
                pass
            messagebox.showinfo("Diagnostics", f"گزارش بدون API Key/Token ساخته شد:\n{path}", parent=self)
        except Exception as exc:
            messagebox.showerror("Diagnostics", str(exc), parent=self)

    def link_refresh(self):
        if self._phase49_3i21_busy or bool(getattr(self, "_phase49_3i18_busy", False)) or bool(getattr(self, "_phase49_3i19_busy", False)):
            self.footer_status.set("یک عملیات AI دیگر در حال اجراست")
            return
        try:
            self.save(silent=True)
            provider, key, model = self._phase49_3e_provider()
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self); return
        row = self.db.product(self.product_id)
        source_url = str(_row_value(row, "source_url", "") or "").strip()
        if not source_url.startswith(("http://", "https://")):
            messagebox.showwarning("3DPrintHub", "لینک معتبر محصول وجود ندارد.", parent=self); return
        selected = images.cap_unique_urls(_list(_row_value(row, "selected_images_json", "[]")))
        categories = self.app.get_all_categories()
        self._phase49_3i21_busy = True
        dialog = ObservableJobDialog(self, "تکمیل همه اطلاعات بر اساس لینک محصول")
        self._phase49_3i21_job_dialog = dialog
        dialog.event("queued", "عملیات در صف اجرا قرار گرفت", {"url": source_url, "provider": provider, "model": model})

        def worker():
            try:
                if dialog.cancelled.is_set(): return
                dialog.event("source_fetch", "در حال خواندن صفحه واقعی محصول…")
                from .crawler import parse_product, public_http
                html = public_http(source_url, 25)
                if dialog.cancelled.is_set(): return
                parsed = parse_product(html, source_url, "", []) or {}
                facts = normalized_source_facts(parsed, source_url)
                current_source = dict(self._source_for_ai() or {})
                external_id = str(_row_value(row, "external_id", "") or "")
                source_title = canonical_source_title(
                    str(parsed.get("source_title") or current_source.get("source_title") or _row_value(row, "source_title", "")),
                    source_url,
                    external_id,
                    candidates=(parsed.get("source_title") or "",),
                )
                if not source_title or is_generic_source_title(source_title, external_id):
                    raise RuntimeError("عنوان واقعی و معتبر محصول از لینک منبع استخراج نشد")
                current_source.update({key: value for key, value in facts.items() if key != "source_url"})
                current_source["source_url"] = source_url
                current_source["source_title"] = source_title
                current_source["_grounded_source_facts"] = facts
                current_source["selected_materials"] = selected_material_names(row)
                current_source["selected_colors"] = selected_color_names(row)
                dialog.event("source_ready", "اطلاعات منبع خوانده شد", {"source_title": source_title, "fact_keys": sorted(facts.keys()), "images": len(selected)})
                if dialog.cancelled.is_set(): return
                dialog.event("ai_request", "لینک و داده واقعی منبع برای AI ارسال شد…", {"provider": provider, "model": model})
                pack = AIContentService(key, model, provider, product_id=self.product_id).enrich_product(
                    current_source, categories, image_count=len(selected), image_urls=selected, mode="commerce"
                )
                if dialog.cancelled.is_set(): return
                persian_title = _clean_text(pack.get("title_fa") or "", 300)
                if not persian_title or is_generic_source_title(persian_title, external_id):
                    raise RuntimeError("AI عنوان فارسی معتبر برنگرداند؛ هیچ تغییری اعمال نشد")
                preview = {
                    "source_title": source_title,
                    "title_fa": persian_title,
                    "seo_title_fa": pack.get("seo_title_fa"),
                    "seo_description_fa": pack.get("seo_description_fa"),
                    "short_description_fa": pack.get("short_description_fa"),
                    "image_alt_count": len(pack.get("image_alt_texts") or []),
                    "keywords": pack.get("target_keywords_fa") or [],
                }
                dialog.event("received", "پاسخ کامل AI دریافت شد؛ منتظر تأیید برای بروزرسانی همه فیلدهاست", preview)

                def confirm_apply():
                    if dialog.cancelled.is_set(): return
                    yes = messagebox.askyesno(
                        "اعمال خروجی لینک + AI",
                        f"عنوان منبع: {source_title}\nعنوان فارسی جدید: {persian_title}\n\nمتن، SEO، Alt/Title/Caption تصاویر و Metadata مرتبط بروزرسانی شوند؟\nقیمت، موجودی، URL و انتخاب‌های تجاری دست‌نخورده می‌مانند.",
                        parent=dialog.top,
                    )
                    if not yes:
                        dialog.event("preview", "خروجی دریافت شد اما اپراتور اعمال تغییرات را لغو کرد")
                        self._phase49_3i21_busy = False
                        return
                    dialog.event("applying", "در حال بروزرسانی یکپارچه فیلدهای قابل ویرایش…")
                    self.db.update_product(self.product_id, {"source_title": source_title})
                    self._phase49_3i18_apply_ai(pack, persian_title)
                    if hasattr(self, "_phase49_3i19_source_title"): self._phase49_3i19_source_title.set(source_title)
                    if hasattr(self, "_phase49_3i18_title"): self._phase49_3i18_title.set(persian_title)
                    dialog.done("همه فیلدهای محتوایی/SEO/تصاویر با موفقیت بروزرسانی شدند")
                    self._phase49_3i21_busy = False

                self.after(0, confirm_apply)
            except Exception as exc:
                dialog.fail(exc)
                self.after(0, lambda: setattr(self, "_phase49_3i21_busy", False))

        threading.Thread(target=worker, daemon=True, name=f"catalog-ai-link-{self.product_id}").start()

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i21_build_ui = build_ui
    workspace_class._phase49_3i21_export_diagnostics = export_diagnostics
    workspace_class._phase49_3i21_link_refresh = link_refresh
    workspace_class._phase49_3i21_observable_ai_installed = True
