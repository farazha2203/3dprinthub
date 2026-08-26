from __future__ import annotations

import json
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from . import phase49_3c_image_pipeline as images
from .openai_content import AIContentService
from .phase49_3i17_single_active_ai_runtime import active_ai_config
from .phase49_3i18_operator_editing import _list, _v, ai_updates
from .phase49_3i19_source_identity import canonical_source_title, is_generic_source_title
from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
from .phase49_3i25_product_first_workflow import (
    makerworld_profile_weight_from_html,
    normalized_source_facts,
)
from .phase49_3i_explorer_hotfix import matches_source_product_url
from .phase49_diagnostics import audit_event, redact


PHASE = "49.3I.31"
MAX_AI_SOURCE_TEXT = 24000
BULK_IMAGE_LIMIT = 4

FACT_LABELS = {
    "source_description": "توضیحات منبع",
    "source_category": "دسته منبع",
    "source_categories": "مسیر دسته‌بندی",
    "source_specs": "مشخصات و ویژگی‌ها",
    "source_tags": "برچسب‌ها",
    "author_name": "طراح / سازنده",
    "license_name": "مجوز",
    "source_price": "قیمت ثبت‌شده در منبع",
    "source_currency": "واحد قیمت منبع",
    "estimated_weight_grams": "وزن تخمینی/ثبت‌شده (گرم)",
    "estimated_print_minutes": "زمان چاپ (دقیقه)",
    "download_count": "تعداد دانلود",
    "like_count": "تعداد پسند",
    "print_count": "تعداد چاپ",
    "published_at": "تاریخ انتشار منبع",
    "updated_at": "آخرین بروزرسانی منبع",
    "external_id": "شناسه خارجی",
    "model_id": "شناسه مدل",
    "profile_id": "شناسه پروفایل چاپ",
}


def _row_value(row, key: str, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
    except Exception:
        value = default
    return default if value is None else value


def _clean(value: Any, limit: int = 5000) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "بله" if value else "خیر"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return " ".join(value.split())[:limit]
    if isinstance(value, list):
        parts = [_clean(item, 900) for item in value[:60]]
        return "، ".join(part for part in parts if part)[:limit]
    if isinstance(value, dict):
        lines = []
        for key, item in list(value.items())[:80]:
            text = _clean(item, 1200)
            if text:
                lines.append(f"- {str(key).strip()}: {text}")
        return "\n".join(lines)[:limit]
    return _clean(str(value), limit)


def structured_source_description(
    parsed: dict[str, Any] | None,
    facts: dict[str, Any] | None,
    source_url: str,
) -> str:
    """Flatten every safe product fact into one factual text field for AI.

    The runtime AI contract remains exactly two product fields: title + text.
    Business state, local category IDs, stock, price overrides and credentials are
    never added. Link facts are organized as text headings so every provider sees
    the same deterministic source evidence.
    """
    parsed = dict(parsed or {})
    facts = dict(facts or {})
    lines = [
        "اطلاعات استخراج‌شده از صفحه واقعی محصول",
        f"لینک منبع: {str(source_url or '').strip()}",
        "قاعده: فقط از داده‌های زیر استفاده کن؛ داده ناموجود را حدس نزن.",
    ]

    seen = set()
    for key in FACT_LABELS:
        raw = facts.get(key)
        if raw in (None, "", [], {}):
            raw = parsed.get(key)
        if raw in (None, "", [], {}):
            continue
        text = _clean(raw, 7000 if key in {"source_description", "source_specs"} else 3500)
        if not text:
            continue
        lines.extend(("", f"## {FACT_LABELS[key]}", text))
        seen.add(key)

    ignored = {
        "html", "raw_html", "cookies", "headers", "request_headers", "authorization",
        "images", "image_urls", "source_url", "source_title",
    }
    extras = []
    for key, raw in parsed.items():
        if key in seen or key in ignored or raw in (None, "", [], {}):
            continue
        if str(key).startswith("_"):
            continue
        text = _clean(raw, 1600)
        if text:
            extras.append(f"- {str(key).strip()}: {text}")
        if len(extras) >= 24:
            break
    if extras:
        lines.extend(("", "## سایر داده‌های محصول استخراج‌شده", *extras))

    result = "\n".join(lines).strip()
    return result[:MAX_AI_SOURCE_TEXT]


def _positive_number(value):
    try:
        number = float(value)
    except Exception:
        return None
    return number if 0 < number < 10_000_000 else None


def _validate_product_url(app, row, source_url: str) -> None:
    if not str(source_url or "").strip().lower().startswith(("http://", "https://")):
        raise RuntimeError("این محصول لینک منبع HTTP/HTTPS معتبر ندارد.")
    source_code = str(_row_value(row, "source_code", "") or "").strip()
    source = app.db.source(source_code) if source_code else None
    pattern = str(_row_value(source, "model_url_pattern", "") or "").strip() if source is not None else ""
    if pattern and not matches_source_product_url(source_url, pattern):
        raise RuntimeError("لینک ذخیره‌شده با الگوی صفحه دقیق محصول این منبع مطابقت ندارد؛ صفحه لیست/جستجو به AI فرستاده نمی‌شود.")


def extract_grounded_product_source(app, row, source_url_override: str = "") -> dict[str, Any]:
    source_url = str(source_url_override or _row_value(row, "source_url", "") or "").strip()
    _validate_product_url(app, row, source_url)
    from .crawler import parse_product, public_http

    html = public_http(source_url, 25)
    parsed = parse_product(html, source_url, "", []) or {}
    profile_weight = makerworld_profile_weight_from_html(html, source_url)
    if profile_weight is not None:
        parsed["estimated_weight_grams"] = profile_weight
    facts = normalized_source_facts(parsed, source_url)
    external_id = str(_row_value(row, "external_id", "") or "")
    source_title = canonical_source_title(
        str(parsed.get("source_title") or _row_value(row, "source_title", "") or ""),
        source_url,
        external_id,
        candidates=(parsed.get("source_title") or "", _row_value(row, "source_title", "") or ""),
    )
    if not source_title or is_generic_source_title(source_title, external_id):
        raise RuntimeError("عنوان واقعی و معتبر محصول از لینک منبع استخراج نشد.")
    return {
        "source_url": source_url,
        "source_title": source_title,
        "raw_source_description": str(parsed.get("source_description") or "").strip(),
        "source_description": structured_source_description(parsed, facts, source_url),
        "facts": facts,
        "parsed": parsed,
    }


def selected_image_urls(row, limit: int = BULK_IMAGE_LIMIT) -> list[str]:
    selected = images.cap_unique_urls(_list(_row_value(row, "selected_images_json", "[]")))
    if not selected:
        selected = images.cap_unique_urls(_list(_row_value(row, "images_json", "[]")))
    return [str(url) for url in selected if str(url).startswith(("http://", "https://"))][: max(0, int(limit))]


def build_image_metadata_updates(row, pack: dict[str, Any], title: str) -> dict[str, Any]:
    selected = images.cap_unique_urls(_list(_row_value(row, "selected_images_json", "[]")))
    if not selected:
        return {}
    alts = _list(pack.get("image_alt_texts") or [])
    keywords = _list(pack.get("target_keywords_fa") or [])[:16]
    caption = str(pack.get("short_description_fa") or pack.get("seo_description_fa") or "").strip()
    current = _list(_row_value(row, images.IMAGE_METADATA_COLUMN, "[]"))
    by_url = {
        str(item.get("source_url") or ""): dict(item)
        for item in current
        if isinstance(item, dict) and item.get("source_url")
    }
    metadata = []
    final_alts = []
    for index, url in enumerate(selected, 1):
        item = by_url.get(url, {"source_url": url})
        alt = str(alts[index - 1] if index - 1 < len(alts) else f"{title} - تصویر {index}").strip()
        final_alts.append(alt)
        item.update(
            alt_text=alt,
            title=f"{title} - تصویر {index}",
            caption=caption,
            keywords=keywords,
            metadata_ready=False,
            seo_signature="",
        )
        metadata.append(item)
    return {
        "image_alt_texts_json": json.dumps(final_alts, ensure_ascii=False),
        images.IMAGE_METADATA_COLUMN: json.dumps(metadata, ensure_ascii=False),
    }


def build_product_updates(row, pack: dict[str, Any], extracted: dict[str, Any]) -> tuple[dict[str, Any], str]:
    title = str(pack.get("title_fa") or "").strip()
    if not title:
        raise RuntimeError("AI عنوان فارسی معتبر برنگرداند؛ محصول تغییر نکرد.")
    updates = ai_updates(row, pack, title)
    updates.update(build_image_metadata_updates(row, pack, title))
    updates["source_title"] = str(extracted.get("source_title") or _row_value(row, "source_title", "")).strip()
    raw_description = str(extracted.get("raw_source_description") or "").strip()
    if raw_description:
        updates["source_description"] = raw_description
    facts = extracted.get("facts") if isinstance(extracted.get("facts"), dict) else {}
    weight = _positive_number(facts.get("estimated_weight_grams"))
    minutes = _positive_number(facts.get("estimated_print_minutes"))
    if weight is not None:
        updates["estimated_weight_grams"] = weight
    if minutes is not None:
        updates["estimated_print_minutes"] = minutes
    return updates, title


def apply_product_ai_result(app, product_id: int, pack: dict[str, Any], extracted: dict[str, Any]) -> dict[str, Any]:
    row = app.db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"محصول #{product_id} در دیتابیس پیدا نشد.")
    before = dict(row)
    updates, title = build_product_updates(row, pack, extracted)
    app.db.update_product(int(product_id), updates)
    selected = images.cap_unique_urls(_list(_row_value(row, "selected_images_json", "[]")))
    image_error = ""
    if selected:
        try:
            images.finalize_selected_images(app.db, int(product_id))
        except Exception as exc:
            image_error = f"{type(exc).__name__}: {exc}"
            audit_event(
                "images",
                "phase49_3i31_finalize_error",
                status="error",
                level="ERROR",
                product_id=int(product_id),
                source_file=__file__,
                message=redact(exc),
            )
    after_row = app.db.product(int(product_id))
    if after_row is not None:
        try:
            app.db.save_history(
                int(product_id),
                "phase49_3i31_smart_link_ai",
                before,
                dict(after_row),
                "grounded link + Persian SEO + selected image metadata",
            )
        except Exception:
            pass
    marker = getattr(app, "_phase49_3i29_mark_products_dirty", None)
    if callable(marker):
        marker("phase49-3i31-ai")
    return {
        "product_id": int(product_id),
        "title_fa": title,
        "changed_fields": sorted(updates),
        "images": len(selected),
        "image_error": image_error,
    }


def run_product_ai(app, product_id: int, provider: str, key: str, model: str) -> dict[str, Any]:
    row = app.db.product(int(product_id))
    if row is None:
        raise RuntimeError(f"محصول #{product_id} پیدا نشد.")
    extracted = extract_grounded_product_source(app, row)
    image_urls = selected_image_urls(row)
    audit_event(
        "ai",
        "phase49_3i31_grounded_request",
        status="running",
        product_id=int(product_id),
        source_file=__file__,
        message=f"provider={provider} model={model} link_facts_as_text=1 images={len(image_urls)}",
        detail={
            "phase": PHASE,
            "provider": provider,
            "model": model,
            "sent_product_fields": ["source_title", "source_description"],
            "source_text_chars": len(extracted["source_description"]),
            "image_count": len(image_urls),
        },
    )
    pack = AIContentService(key, model, provider, product_id=int(product_id)).enrich_product(
        {
            "source_title": extracted["source_title"],
            "source_description": extracted["source_description"],
        },
        [],
        image_count=len(image_urls),
        image_urls=image_urls,
        mode="commerce",
    )
    return {
        "pack": pack,
        "extracted": extracted,
    }


def install_workspace(workspace_class) -> None:
    """Make the main AI action a grounded link+content+SEO+image operation."""
    if getattr(workspace_class, "_phase49_3i31_smart_link_ai", False):
        return

    def smart_ai(self):
        if any(bool(getattr(self, name, False)) for name in (
            "_phase49_3i31_busy", "_phase49_3i21_busy", "_phase49_3i18_busy", "_phase49_3e_busy", "_ai_busy",
        )):
            try:
                self.footer_status.set("یک عملیات AI دیگر در حال اجرا است.")
            except Exception:
                pass
            return None
        row = self.db.product(self.product_id)
        if row is None:
            return None
        try:
            provider, key, model = self._phase49_3e_provider()
            source_url = str(getattr(getattr(self, "source_url", None), "get", lambda: "")() or _row_value(row, "source_url", "") or "").strip()
            _validate_product_url(self.app, row, source_url)
            if source_url != str(_row_value(row, "source_url", "") or "").strip():
                from .db import normalize_url
                self.db.update_product(self.product_id, {"source_url": source_url, "normalized_url": normalize_url(source_url)})
                row = self.db.product(self.product_id)
        except Exception as exc:
            messagebox.showerror("3DPrintHub — AI", str(exc), parent=self)
            return None

        self._phase49_3i31_busy = True
        dialog = ObservableJobDialog(self, "AI کامل محصول — لینک + فارسی + SEO + تصاویر")
        dialog.event(
            "queued",
            "درخواست کامل AI آماده اجرا شد",
            {"provider": provider, "model": model, "product_id": self.product_id},
        )

        def worker():
            try:
                if dialog.cancelled.is_set():
                    return
                dialog.event("source_fetch", "در حال خواندن لینک واقعی محصول…")
                result = run_product_ai(self.app, self.product_id, provider, key, model)
                if dialog.cancelled.is_set():
                    return
                extracted = result["extracted"]
                pack = result["pack"]
                dialog.event(
                    "received",
                    "پاسخ AI دریافت شد؛ متن، SEO و متادیتای تصاویر آماده اعمال است",
                    {
                        "source_title": extracted.get("source_title"),
                        "source_text_chars": len(str(extracted.get("source_description") or "")),
                        "title_fa": pack.get("title_fa"),
                        "seo_title_fa": pack.get("seo_title_fa"),
                        "image_alt_count": len(pack.get("image_alt_texts") or []),
                    },
                )

                def apply_on_ui():
                    try:
                        if dialog.cancelled.is_set():
                            return
                        dialog.event("applying", "در حال اعمال خروجی روی همین محصول…")
                        summary = apply_product_ai_result(self.app, self.product_id, pack, extracted)
                        try:
                            self.reload()
                            getattr(self, "_phase49_3e_refresh_tasks", lambda: None)()
                        except Exception:
                            pass
                        if summary.get("image_error"):
                            dialog.done("متن و SEO اعمال شد؛ نهایی‌سازی فایل تصویر نیاز به بررسی دارد")
                            messagebox.showwarning(
                                "3DPrintHub — تصاویر",
                                "محتوا و SEO اعمال شد اما نهایی‌سازی فایل یکی از تصاویر کامل نشد:\n\n"
                                + str(summary["image_error"]),
                                parent=self,
                            )
                        else:
                            dialog.done("عنوان، توضیحات فارسی، SEO و تصاویر منتخب با موفقیت بروزرسانی شدند")
                        try:
                            self.footer_status.set("AI کامل محصول با لینک واقعی و تصاویر انجام شد")
                        except Exception:
                            pass
                    except Exception as exc:
                        dialog.fail(exc)
                    finally:
                        self._phase49_3i31_busy = False

                self.after(0, apply_on_ui)
            except Exception as exc:
                dialog.fail(exc)
                self.after(0, lambda: setattr(self, "_phase49_3i31_busy", False))

        threading.Thread(
            target=worker,
            daemon=True,
            name=f"catalog-smart-ai-{self.product_id}",
        ).start()
        return None

    workspace_class._phase49_3i31_smart_ai = smart_ai
    workspace_class._phase49_3e_run_all_ai = smart_ai
    workspace_class._phase49_3c_stage_ai = smart_ai
    workspace_class._phase49_3i21_link_refresh = smart_ai
    workspace_class._phase49_3i31_smart_link_ai = True


class _BulkDialog:
    def __init__(self, app, total: int, provider: str, model: str):
        self.app = app
        self.cancelled = threading.Event()
        self.top = tk.Toplevel(app)
        self.top.title("AI گروهی محصولات — لینک + SEO + تصاویر")
        self.top.geometry("850x590")
        self.top.minsize(720, 480)
        self.top.transient(app)
        self.status = tk.StringVar(value=f"آماده پردازش {total} محصول")
        head = ttk.Frame(self.top, padding=10)
        head.pack(fill="x")
        ttk.Label(head, textvariable=self.status, font=("Tahoma", 10, "bold")).pack(side="right")
        ttk.Label(head, text=f"{provider} • {model}").pack(side="left")
        self.progress = ttk.Progressbar(self.top, mode="determinate", maximum=max(1, total), value=0)
        self.progress.pack(fill="x", padx=10)
        self.text = tk.Text(self.top, wrap="word", height=26)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.configure(state="disabled")
        foot = ttk.Frame(self.top, padding=(10, 0, 10, 10))
        foot.pack(fill="x")
        ttk.Button(foot, text="توقف بعد از محصول جاری", command=self.cancel).pack(side="left")
        ttk.Button(foot, text="بستن", command=self.top.destroy).pack(side="right")
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)

    def log(self, message: str, *, progress: int | None = None):
        def render():
            try:
                if not self.top.winfo_exists():
                    return
                if progress is not None:
                    self.progress.configure(value=progress)
                self.status.set(message)
                self.text.configure(state="normal")
                self.text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
                self.text.see("end")
                self.text.configure(state="disabled")
            except Exception:
                pass
        self.app.after(0, render)

    def cancel(self):
        self.cancelled.set()
        self.log("لغو درخواست شد؛ پس از پایان محصول جاری متوقف می‌شود.")


def install_app(app_class) -> None:
    """Add batch grounded AI to the Products explorer without per-item refresh."""
    if getattr(app_class, "_phase49_3i31_bulk_ai", False):
        return
    original_modernize = getattr(app_class, "_modernize_products_page", None)

    def _modernize_products_page(self):
        if callable(original_modernize):
            original_modernize(self)
        self._phase49_3i31_bulk_busy = False
        panel = ttk.Frame(self.products_tab)
        shell = getattr(getattr(self, "_phase49_3i_gallery_canvas", None), "master", None)
        kwargs = {"fill": "x", "pady": (0, 7)}
        if shell is not None:
            kwargs["before"] = shell
        panel.pack(**kwargs)
        ttk.Button(
            panel,
            text="✨ AI گروهی از لینک برای محصولات انتخاب‌شده",
            command=self._phase49_3i31_start_bulk_ai,
            style="Success.TButton",
        ).pack(side="right", padx=4)
        ttk.Label(
            panel,
            text="هر محصول: لینک واقعی → عنوان/متن منبع → فارسی/SEO → Alt و Metadata تصاویر؛ فقط یک Refresh در پایان.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=8)
        self._phase49_3i31_bulk_panel = panel

    def _phase49_3i31_start_bulk_ai(self):
        if getattr(self, "_phase49_3i31_bulk_busy", False):
            messagebox.showinfo("3DPrintHub", "پردازش گروهی دیگری در حال اجراست.", parent=self)
            return None
        ids = sorted({int(value) for value in (getattr(self, "_phase49_3i_selected_products", set()) or set())})
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا محصولات موردنظر را در صفحه محصولات انتخاب کن.", parent=self)
            return None
        try:
            provider, key, model = active_ai_config(self, require_key=True)
        except Exception as exc:
            messagebox.showerror("3DPrintHub — تنظیمات مادر AI", str(exc), parent=self)
            return None
        if not messagebox.askyesno(
            "3DPrintHub — AI گروهی",
            f"AI کامل روی {len(ids)} محصول انتخاب‌شده اجرا شود؟\n\n"
            f"Provider: {provider}\nModel: {model}\n\n"
            "برای هر محصول لینک واقعی خوانده می‌شود و فقط عنوان + متن استخراج‌شده به AI می‌رود. "
            "قیمت/موجودی/انتخاب‌های تجاری بازنویسی نمی‌شوند.",
            parent=self,
        ):
            return None

        self._phase49_3i31_bulk_busy = True
        dialog = _BulkDialog(self, len(ids), provider, model)
        audit_event(
            "ai",
            "phase49_3i31_bulk_start",
            status="running",
            source_file=__file__,
            message=f"count={len(ids)} provider={provider} model={model}",
            detail={"phase": PHASE, "product_ids": ids, "provider": provider, "model": model},
        )

        def worker():
            ok = 0
            failed = 0
            errors = []
            try:
                for index, product_id in enumerate(ids, 1):
                    if dialog.cancelled.is_set():
                        break
                    row = self.db.product(product_id)
                    title = str(_row_value(row, "title_fa", "") or _row_value(row, "source_title", "") or f"#{product_id}") if row is not None else f"#{product_id}"
                    dialog.log(f"{index}/{len(ids)} — شروع #{product_id}: {title}", progress=index - 1)
                    try:
                        result = run_product_ai(self, product_id, provider, key, model)
                        summary = apply_product_ai_result(self, product_id, result["pack"], result["extracted"])
                        ok += 1
                        suffix = "" if not summary.get("image_error") else " • هشدار فایل تصویر"
                        dialog.log(f"{index}/{len(ids)} — انجام شد #{product_id}: {summary['title_fa']}{suffix}", progress=index)
                    except Exception as exc:
                        failed += 1
                        text = redact(exc)
                        errors.append((product_id, text))
                        audit_event(
                            "ai",
                            "phase49_3i31_bulk_item_error",
                            status="error",
                            level="ERROR",
                            product_id=product_id,
                            source_file=__file__,
                            message=text,
                            detail={"phase": PHASE, "index": index, "total": len(ids)},
                        )
                        dialog.log(f"{index}/{len(ids)} — خطا #{product_id}: {text}", progress=index)
                cancelled = dialog.cancelled.is_set()
                processed = ok + failed
                final = f"پایان: {ok} موفق • {failed} خطا • {processed}/{len(ids)} پردازش‌شده"
                if cancelled:
                    final += " • متوقف‌شده توسط اپراتور"
                dialog.log(final, progress=processed)
                audit_event(
                    "ai",
                    "phase49_3i31_bulk_complete",
                    status="cancelled" if cancelled else ("ok" if not failed else "partial"),
                    source_file=__file__,
                    message=final,
                    detail={
                        "phase": PHASE,
                        "success": ok,
                        "failed": failed,
                        "processed": processed,
                        "total": len(ids),
                        "failed_ids": [pid for pid, _ in errors],
                    },
                )
            finally:
                def finish_ui():
                    try:
                        flush = getattr(self, "_phase49_3i29_flush_products_refresh", None)
                        if callable(flush):
                            flush()
                    finally:
                        self._phase49_3i31_bulk_busy = False
                self.after(0, finish_ui)

        threading.Thread(target=worker, daemon=True, name="catalog-bulk-smart-ai").start()
        return None

    if callable(original_modernize):
        app_class._modernize_products_page = _modernize_products_page
    app_class._phase49_3i31_start_bulk_ai = _phase49_3i31_start_bulk_ai
    app_class._phase49_3i31_bulk_ai = True
