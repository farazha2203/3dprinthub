from __future__ import annotations

import json
import re
import time
from pathlib import Path

import tkinter as tk
from tkinter import messagebox, ttk

from . import phase49_3c_image_pipeline as image_pipeline
from .phase49_diagnostics import audit_event
from .phase49_3i18_operator_editing import ai_updates
from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
from .phase49_3i24_runtime_observability import redact
from .phase49_3i33_ai_core import (
    build_image_metadata_updates,
    capture_source_screenshot,
    generate_translation_pack,
    live_source_for_ai,
    repair_allowed,
    row_value,
    saved_source_for_ai,
    source_from_screenshot,
    source_updates,
    structured_ai_text,
    title_quality_guard,
)
from .phase49_3i35_resilient_ai import (
    _preflight,
    configured_ai_candidates,
    retry_attempts,
)
from .phase49_3i36_stage_finalization import (
    STAGE_LABELS,
    STAGE_ORDER,
    field_stage,
    filter_ai_updates,
    is_stage_locked,
    stage_locks,
)


PHASE = "49.3I.37"

AI_SOURCE_MODES = {
    "link": "لینک واقعی محصول",
    "data": "دیتای ذخیره‌شده محصول",
    "screenshot": "اسکرین‌شات صفحه محصول",
}
AI_SOURCE_BY_LABEL = {label: code for code, label in AI_SOURCE_MODES.items()}
SOURCE_SETTING = "ai_product_source_mode"

AI_NEVER_FIELDS = {
    "materials_json", "colors_json", "material_options_json", "color_options_json",
    "material_color_options_json", "fixed_price_material_name", "fixed_price_color_name",
    "sales_profiles_json", "sales_profile_ledger_json", "sales_profile_selection_mode",
    "sales_profile_selector_label", "price_min", "price_max", "final_price",
    "suggested_price", "material_price_per_gram", "pricing_strategy",
    "stock_quantity", "availability_status", "approved_for_sale",
    "publish_as_product", "publish_as_portfolio",
}

CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
PERSIAN_RE = re.compile(r"[\u0600-\u06ff]")
LATIN_WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b")
LATIN_TECH_ALLOW = {
    "3d", "stl", "fdm", "cad", "cnc", "pla", "petg", "abs", "tpu", "makerworld",
    "printables", "bambu", "lab", "openai", "gpt", "step", "obj", "3mf",
}


def source_mode(app) -> str:
    mode = str(app.db.setting(SOURCE_SETTING, "link") or "link").strip().lower()
    return mode if mode in AI_SOURCE_MODES else "link"


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _has_persian(value) -> bool:
    return bool(PERSIAN_RE.search(str(value or "")))


def _foreign_latin_words(value: str, source_title: str) -> list[str]:
    source_words = {token.casefold() for token in LATIN_WORD_RE.findall(str(source_title or ""))}
    bad = []
    for token in LATIN_WORD_RE.findall(str(value or "")):
        folded = token.casefold()
        if folded in LATIN_TECH_ALLOW or folded in source_words:
            continue
        bad.append(token)
    return bad


def validate_editorial_pack(source_title: str, pack: dict) -> dict:
    """Fail closed on mixed-language/identity-corrupt Persian SEO."""
    pack = dict(pack or {})
    title = str(pack.get("title_fa") or "").strip()
    seo_title = str(pack.get("seo_title_fa") or "").strip()

    # The owner explicitly defined the semantic identity of this source pun.
    if "twistmas tree" in str(source_title or "").casefold():
        canonical = "درخت کریسمس اسپیرال"
        pack["title_fa"] = canonical
        title = canonical
        bad_identity = re.compile(
            r"(?:تویست[\s\u200c-]*ماس[\s\u200c-]*تری|Twistmas\s+Tree)",
            re.IGNORECASE,
        )
        seo_title = bad_identity.sub(canonical, seo_title)
        if canonical not in seo_title:
            seo_title = f"{canonical} | {seo_title}".strip(" |")
        pack["seo_title_fa"] = seo_title[:220]

    title_quality_guard(source_title, pack.get("title_fa") or "")
    if pack.get("seo_title_fa"):
        title_quality_guard(source_title, pack.get("seo_title_fa") or "")

    required_persian = (
        "title_fa", "short_description_fa", "description_fa",
        "seo_title_fa", "seo_description_fa",
    )
    for key in required_persian:
        value = str(pack.get(key) or "").strip()
        if not value or not _has_persian(value):
            raise RuntimeError(f"خروجی AI برای {key} فارسی معتبر نیست.")
        if CYRILLIC_RE.search(value):
            raise RuntimeError(f"خروجی AI برای {key} دارای حروف غیرمجاز سیریلیک/چندزبانه است.")
        # Descriptions may legitimately contain a source brand/model. Unknown
        # free-floating Latin prose is rejected because it was observed in the
        # owner log as language contamination (for example Indonesian fragments).
        foreign = _foreign_latin_words(value, source_title)
        if foreign and key in {"title_fa", "seo_title_fa", "seo_description_fa"}:
            raise RuntimeError(
                f"خروجی AI برای {key} متن لاتین نامرتبط دارد: {', '.join(foreign[:4])}"
            )

    pack["material_recommendations"] = []
    pack["suggested_category_slug"] = ""
    return pack


def _field_needs_fill(row, key: str, source_title: str) -> bool:
    value = row_value(row, key, "")
    if key == "title_fa":
        try:
            title_quality_guard(source_title, str(value or ""))
            return False
        except Exception:
            return True
    if key == "seo_title_fa":
        if not str(value or "").strip():
            return True
        try:
            title_quality_guard(source_title, str(value or ""))
            return False
        except Exception:
            return True
    if key in {"short_description_fa", "description_fa", "seo_description_fa"}:
        text = str(value or "").strip()
        return (
            not text
            or not _has_persian(text)
            or bool(CYRILLIC_RE.search(text))
        )
    return repair_allowed(row, key)


def resolve_source(app, row, mode: str, provider: str, key: str, model: str) -> dict:
    mode = str(mode or "").strip().lower()
    if mode == "link":
        return live_source_for_ai(app, row)
    if mode == "data":
        saved = saved_source_for_ai(row)
        if not str(saved.get("source_title") or "").strip():
            raise RuntimeError("دیتای ذخیره‌شده عنوان منبع معتبر ندارد.")
        source_url = str(row_value(row, "source_url", "") or "").strip()
        return {
            "source_url": source_url,
            "source_title": str(saved["source_title"]).strip(),
            "source_description": structured_ai_text(source_url, saved, saved),
            "raw_source_description": str(saved.get("source_description") or "").strip(),
            "facts": saved,
            "evidence": saved,
        }
    if mode == "screenshot":
        return source_from_screenshot(app, row, provider, key, model)
    raise RuntimeError(f"منبع AI نامعتبر است: {mode}")


def _full_ai_updates(app, row, pack: dict, source: dict, mode: str) -> dict:
    title = str(pack.get("title_fa") or "").strip()
    updates = ai_updates(row, pack, title)
    updates.update(build_image_metadata_updates(row, pack, title))
    updates.update(source_updates(app.db, source, mode))
    if source.get("raw_source_description"):
        updates["source_description"] = str(source["raw_source_description"]).strip()
    if source.get("source_title"):
        updates["source_title"] = str(source["source_title"]).strip()
    for key in AI_NEVER_FIELDS:
        updates.pop(key, None)
    return updates


def _stage_candidate_updates(row, full: dict, stage: str, source_title: str) -> dict:
    candidates = {
        key: value
        for key, value in full.items()
        if field_stage(key) == stage and key not in AI_NEVER_FIELDS
    }
    if stage == "images":
        # Image AI is SEO only. Never use AI to rename/move binary files. The
        # deterministic image finalizer owns SEO filenames and file metadata.
        if not image_pipeline.image_metadata_missing(row):
            return {}
        allowed = {"image_alt_texts_json", image_pipeline.IMAGE_METADATA_COLUMN}
        candidates = {key: value for key, value in candidates.items() if key in allowed}

    return {
        key: value
        for key, value in candidates.items()
        if _field_needs_fill(row, key, source_title)
    }


def _readiness(app, product_id: int):
    from . import phase49_readiness_wizard as readiness
    row = app.db.product(int(product_id))
    return readiness.evaluate_readiness(row), row


def _emit(dialog, action: str, message: str, detail=None):
    if dialog is not None:
        dialog.event(action, message, detail or {})


def _progress(dialog, value: float, message: str):
    if dialog is not None:
        dialog.set_progress(value, message)


def orchestrate_once(
    app,
    product_id: int,
    mode: str,
    provider: str,
    key: str,
    model: str,
    dialog=None,
) -> dict:
    """One grounded AI request; seven bounded stage applications."""
    product_id = int(product_id)
    row = app.db.product(product_id)
    if row is None:
        raise RuntimeError(f"محصول #{product_id} پیدا نشد.")

    _progress(dialog, 5, "خواندن منبع انتخاب‌شده")
    _emit(dialog, "source", f"منبع AI: {AI_SOURCE_MODES.get(mode, mode)}")
    source = resolve_source(app, row, mode, provider, key, model)
    source_title = str(source.get("source_title") or row_value(row, "source_title", "") or "").strip()
    if not source_title:
        raise RuntimeError("هویت/عنوان منبع برای AI خالی است.")

    _progress(dialog, 16, "ارسال یک درخواست محتوای ساختاریافته")
    pack = generate_translation_pack(
        provider, key, model, source_title, source["source_description"], product_id
    )
    pack = validate_editorial_pack(source_title, pack)
    full = _full_ai_updates(app, row, pack, source, mode)

    result = {
        "product_id": product_id,
        "mode": mode,
        "provider": provider,
        "model": str(pack.get("_ai_model") or model),
        "title_fa": str(pack.get("title_fa") or ""),
        "stages": {},
        "changed_fields": [],
    }
    image_deferred = False

    for index, stage in enumerate(STAGE_ORDER, 1):
        row = app.db.product(product_id)
        locked = is_stage_locked(row, stage)
        label = STAGE_LABELS[stage]
        progress = 18 + (index / len(STAGE_ORDER)) * 70
        _progress(dialog, progress, f"{label}")

        if locked:
            result["stages"][stage] = {"locked": True, "changed_fields": [], "data_ready": True}
            _emit(dialog, "stage_locked", f"🔒 {label}: قبلاً ثبت نهایی شده؛ بدون تغییر رد شد.")
            continue

        if stage in {"commerce", "publish"}:
            state, _ = _readiness(app, product_id)
            ready = bool((state.get("stages", {}).get(stage) or {}).get("data_ready"))
            result["stages"][stage] = {"locked": False, "changed_fields": [], "data_ready": ready}
            _emit(
                dialog, "stage_operator",
                f"{'✅' if ready else '⚪'} {label}: اپراتوری است؛ AI قیمت/Profile/متریال/موجودی/انتشار را تغییر نمی‌دهد."
            )
            continue

        current = app.db.product(product_id)
        updates = _stage_candidate_updates(current, full, stage, source_title)
        updates, blocked = filter_ai_updates(current, updates)
        if blocked:
            _emit(dialog, "stage_blocked_fields", f"{label}: فیلدهای محافظت‌شده حذف شدند.", {"fields": blocked})

        # Image metadata finalization depends on final content/SEO signature.
        # If stage 4 still needs AI writes, defer the binary metadata pass until
        # after content is committed to avoid instant stale signatures.
        if stage == "images":
            content_pending = bool(_stage_candidate_updates(current, full, "content", source_title))
            if content_pending:
                image_deferred = True
                updates = {k: v for k, v in updates.items() if k == "image_alt_texts_json"}

        if updates:
            app.db.update_product(product_id, updates)
            result["changed_fields"].extend(sorted(updates))
            audit_event(
                "ai", "stage_apply", product_id=product_id, source_file=__file__,
                message=f"{stage}: {len(updates)} fields",
                detail={"phase": PHASE, "stage": stage, "fields": sorted(updates), "mode": mode},
            )

        if stage == "content" and image_deferred:
            refreshed = app.db.product(product_id)
            if not is_stage_locked(refreshed, "images"):
                selected = image_pipeline.cap_unique_urls(
                    _json_list(row_value(refreshed, "selected_images_json", "[]"))
                )
                if selected and image_pipeline.image_metadata_missing(refreshed):
                    try:
                        image_pipeline.finalize_selected_images(app.db, product_id)
                        result["changed_fields"].extend([
                            "image_alt_texts_json", image_pipeline.IMAGE_METADATA_COLUMN,
                            "selected_images_json", "primary_image_url",
                        ])
                        _emit(dialog, "image_finalize", "✅ مرحله تصاویر: SEO/Alt/Metadata پس از تثبیت محتوا نهایی شد.")
                    except Exception as exc:
                        _emit(dialog, "image_finalize_error", f"تصاویر ذخیره شدند ولی Finalize SEO خطا داد: {redact(exc)}")
            image_deferred = False

        if stage == "images" and not image_deferred:
            refreshed = app.db.product(product_id)
            selected = image_pipeline.cap_unique_urls(
                _json_list(row_value(refreshed, "selected_images_json", "[]"))
            )
            if selected and image_pipeline.image_metadata_missing(refreshed):
                try:
                    image_pipeline.finalize_selected_images(app.db, product_id)
                except Exception as exc:
                    _emit(dialog, "image_finalize_error", f"Finalize SEO تصویر: {redact(exc)}")

        state, _ = _readiness(app, product_id)
        data_ready = bool((state.get("stages", {}).get(stage) or {}).get("data_ready"))
        result["stages"][stage] = {
            "locked": False,
            "changed_fields": sorted(updates),
            "data_ready": data_ready,
        }
        _emit(
            dialog, "stage_done",
            f"{'✅' if data_ready else '⚪'} {label}: "
            + ("داده این مرحله کامل است؛ برای قفل نهایی «ثبت» را بزن." if data_ready else "موارد اپراتوری/واقعی هنوز باقی مانده است."),
            {"stage": stage, "changed_fields": sorted(updates), "data_ready": data_ready},
        )

    # Re-evaluate image stage after content dependency and preserve the factual
    # status separately from operator finalization lock.
    state, final_row = _readiness(app, product_id)
    result["readiness"] = {
        stage: {
            "data_ready": bool((state.get("stages", {}).get(stage) or {}).get("data_ready")),
            "finalized": bool((stage_locks(final_row).get(stage) or {}).get("locked")),
        }
        for stage in STAGE_ORDER
    }
    result["changed_fields"] = sorted(set(result["changed_fields"]))
    _progress(dialog, 92, "بازبینی نهایی هفت مرحله")
    return result


def run_resilient_orchestrator(app, product_id: int, dialog, mode: str | None = None) -> dict:
    mode = mode if mode in AI_SOURCE_MODES else source_mode(app)
    candidates = configured_ai_candidates(app, require_key=True)
    attempts = retry_attempts(app)
    health_cache = {}
    failures = []

    for provider_index, (provider, key, model, source) in enumerate(candidates, 1):
        if dialog.cancelled.is_set():
            raise RuntimeError("عملیات توسط اپراتور لغو شد.")
        try:
            probe = _preflight(dialog, provider, key, model, source, health_cache)
            model = str(probe.get("model") or model)
        except Exception as exc:
            failures.append(f"{provider}/preflight: {redact(exc)}")
            continue

        for attempt in range(1, attempts + 1):
            if dialog.cancelled.is_set():
                raise RuntimeError("عملیات توسط اپراتور لغو شد.")
            _emit(
                dialog, "send",
                f"محصول #{product_id}: {provider} • تلاش {attempt}/{attempts} • منبع {AI_SOURCE_MODES[mode]}",
                {"provider": provider, "model": model, "attempt": attempt, "mode": mode},
            )
            try:
                result = orchestrate_once(app, product_id, mode, provider, key, model, dialog)
                _progress(dialog, 100, "هفت مرحله بازبینی شد")
                return result
            except Exception as exc:
                failures.append(f"{provider}/attempt-{attempt}: {redact(exc)}")
                if attempt < attempts:
                    _emit(dialog, "retry", f"پاسخ معتبر نبود؛ تلاش {attempt + 1}/{attempts}: {redact(exc)}")
                    continue
                break

        if provider_index < len(candidates):
            _emit(dialog, "fallback", "Provider تنظیم‌شده بعدی امتحان می‌شود.")

    raise RuntimeError(
        "هیچ Provider تنظیم‌شده خروجی معتبر نداد. " + " | ".join(failures[-6:])
    )


def capture_screenshot_for_site(app, product_id: int) -> dict:
    product_id = int(product_id)
    row = app.db.product(product_id)
    if row is None:
        raise RuntimeError("محصول پیدا نشد.")
    if is_stage_locked(row, "images"):
        raise RuntimeError("مرحله تصاویر ثبت نهایی شده است؛ برای افزودن Screenshot ابتدا «اصلاح» را بزن.")

    target = capture_source_screenshot(app, product_id)
    row = app.db.product(product_id)
    pseudo = f"local://{target.name}"
    all_images = image_pipeline.cap_unique_urls(
        _json_list(row_value(row, "images_json", "[]")) + [pseudo]
    )
    selected = image_pipeline.cap_unique_urls(
        _json_list(row_value(row, "selected_images_json", "[]")) + [pseudo]
    )
    primary = str(row_value(row, "primary_image_url", "") or "").strip() or pseudo
    app.db.update_product(
        product_id,
        {
            "images_json": json.dumps(all_images, ensure_ascii=False),
            "selected_images_json": json.dumps(selected, ensure_ascii=False),
            "primary_image_url": primary,
        },
    )

    finalized = None
    try:
        finalized = image_pipeline.finalize_selected_images(app.db, product_id)
    except Exception as exc:
        audit_event(
            "images", "source_screenshot_site_finalize_error",
            status="error", level="ERROR", product_id=product_id,
            source_file=__file__, message=redact(exc),
        )
        raise RuntimeError(
            f"Screenshot به تصاویر سایت اضافه شد ولی SEO/Metadata نهایی نشد: {redact(exc)}"
        ) from exc

    after = app.db.product(product_id)
    items = _json_list(row_value(after, image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
    meta = next(
        (item for item in items if isinstance(item, dict) and item.get("source_url") == pseudo),
        {},
    )
    source_page = str(row_value(after, "source_url", "") or "").strip()
    if meta and str(meta.get("source_page_url") or "") != source_page:
        raise RuntimeError("Upstream/source page link در Metadata Screenshot حفظ نشد.")

    audit_event(
        "images", "source_screenshot_selected_for_site",
        product_id=product_id, source_file=__file__,
        message=target.name,
        detail={
            "phase": PHASE, "selected": True, "primary_preserved": primary != pseudo,
            "source_page_url": source_page, "metadata_ready": bool(meta.get("metadata_ready")),
        },
    )
    return {
        "path": target,
        "pseudo_url": pseudo,
        "selected": True,
        "primary": primary,
        "source_page_url": source_page,
        "metadata": meta,
        "finalized": finalized or {},
    }


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3i37_source_mode", False):
        return
    original_init = app_class.__init__
    original_save = getattr(app_class, "_phase49_3i35_save_ai_resilience_settings", None)

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        panel = getattr(self, "_phase49_3i35_ai_settings_panel", None)
        if panel is None:
            return
        self._phase49_3i37_source_mode_var = tk.StringVar(
            value=AI_SOURCE_MODES[source_mode(self)]
        )
        ttk.Separator(panel, orient="horizontal").grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=4, pady=(8, 6)
        )
        ttk.Label(panel, text="منبع پیش‌فرض ترجمه/SEO محصول").grid(
            row=7, column=0, sticky="w", padx=4, pady=4
        )
        ttk.Combobox(
            panel,
            textvariable=self._phase49_3i37_source_mode_var,
            values=list(AI_SOURCE_MODES.values()),
            state="readonly",
            width=34,
        ).grid(row=7, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(
            panel,
            text=(
                "این انتخاب فقط منبع واقعیت AI را تعیین می‌کند: لینک، دیتای ذخیره‌شده یا Screenshot. "
                "AI همیشه فقط Stageهای باز/ناقص را پر می‌کند؛ Profile/قیمت/متریال/موجودی و انتشار اپراتوری می‌مانند."
            ),
            style="SubHeader.TLabel",
            wraplength=1050,
        ).grid(row=8, column=0, columnspan=2, sticky="w", padx=4, pady=4)

    def save_settings(self):
        if callable(original_save):
            ok = original_save(self)
            if ok is False:
                return False
        label = str(getattr(self, "_phase49_3i37_source_mode_var", tk.StringVar(value="")).get() or "")
        mode = AI_SOURCE_BY_LABEL.get(label, "link")
        self.db.set_setting(SOURCE_SETTING, mode)
        self.status.set(
            f"تنظیمات AI ذخیره شد • منبع ترجمه/SEO: {AI_SOURCE_MODES[mode]}"
        )
        return True

    app_class.__init__ = __init__
    app_class._phase49_3i35_save_ai_resilience_settings = save_settings
    app_class._phase49_3i37_source_mode = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i37_stage_ai", False):
        return
    original_init = workspace_class.__init__
    original_reload = workspace_class.reload

    def __init__(self, app, product_id):
        original_init(self, app, product_id)

        old_panel = getattr(self, "_phase49_3i33_ai_panel", None)
        if old_panel is not None:
            try:
                old_panel.pack_forget()
            except Exception:
                pass

        panel = ttk.LabelFrame(
            self.content_tab,
            text="هوش مصنوعی ۷ مرحله‌ای — فقط تکمیل موارد باز",
            padding=8,
            style="Card.TLabelframe",
        )
        children = list(self.content_tab.winfo_children())
        try:
            panel.pack(fill="x", pady=(0, 8), before=children[0] if children else None)
        except Exception:
            panel.pack(fill="x", pady=(0, 8))

        self._phase49_3i37_source_label = tk.StringVar()
        ttk.Button(
            panel,
            text="✨ تکمیل هوشمند همه ۷ مرحله باز",
            command=self._phase49_3i37_run_all,
            style="Success.TButton",
        ).pack(side="right", padx=4)
        ttk.Label(
            panel, textvariable=self._phase49_3i37_source_label,
            style="SubHeader.TLabel",
        ).pack(side="right", padx=8)
        ttk.Label(
            panel,
            text=(
                "✅ یعنی داده Stage کامل است؛ 🔒 فقط با «ثبت» اپراتور ایجاد می‌شود. "
                "AI هر Stage قفل‌شده را رد می‌کند و هیچ Profile/قیمت/متریال/موجودی را تغییر نمی‌دهد."
            ),
            style="SubHeader.TLabel",
            wraplength=850,
        ).pack(side="left", padx=4)
        self._phase49_3i37_ai_panel = panel
        self._phase49_3i37_refresh_source_label()

        # The 3I.33 image panel already exists. Re-label the existing control so
        # the owner sees the new site-selection semantics without duplicating UI.
        image_panel = None
        for child in self.images_tab.winfo_children():
            try:
                if isinstance(child, ttk.LabelFrame) and "مرجع صفحه محصول" in str(child.cget("text") or ""):
                    image_panel = child
                    break
            except Exception:
                continue
        if image_panel is not None:
            for child in image_panel.winfo_children():
                try:
                    if isinstance(child, ttk.Button) and "اسکرین‌شات" in str(child.cget("text") or ""):
                        child.configure(
                            text="📸 اسکرین‌شات + افزودن به تصاویر سایت",
                            command=self._phase49_3i33_capture_screenshot,
                        )
                    elif isinstance(child, ttk.Label):
                        child.configure(
                            text=(
                                "Screenshot در Gallery و تصاویر منتخب سایت ثبت می‌شود؛ "
                                "SEO filename/Alt/Metadata ساخته می‌شود و لینک صفحه منبع در Metadata حفظ می‌شود."
                            )
                        )
                except Exception:
                    pass

    def refresh_source_label(self):
        mode = source_mode(self.app)
        if hasattr(self, "_phase49_3i37_source_label"):
            self._phase49_3i37_source_label.set(f"منبع: {AI_SOURCE_MODES[mode]}")

    def run_all(self):
        if getattr(self, "_phase49_3i33_ai_busy", False):
            self.footer_status.set("یک عملیات هوش مصنوعی در حال اجرا است.")
            return
        self._phase49_3i33_ai_busy = True
        mode = source_mode(self.app)
        dialog = ObservableJobDialog(
            self, f"تکمیل ۷ مرحله • {AI_SOURCE_MODES[mode]}"
        )
        dialog.event(
            "queue",
            f"محصول #{self.product_id} • منبع {AI_SOURCE_MODES[mode]} • فقط Stageهای باز/ناقص",
        )

        def worker():
            try:
                result = run_resilient_orchestrator(
                    self.app, int(self.product_id), dialog, mode=mode
                )
                ready = [
                    STAGE_LABELS[stage]
                    for stage, item in (result.get("readiness") or {}).items()
                    if item.get("data_ready")
                ]
                dialog.done(
                    f"بازبینی ۷ مرحله تمام شد • داده کامل: {len(ready)}/7 • برای قفل نهایی هر Stage «ثبت» را بزن."
                )

                def complete():
                    self.reload()
                    try:
                        self._phase49_3i36_refresh_locks()
                    except Exception:
                        pass
                self.after(0, complete)
            except Exception as exc:
                dialog.fail(exc)
                self.after(
                    0,
                    lambda error=exc: self.footer_status.set(
                        f"AI هفت‌مرحله‌ای ناموفق: {redact(error)}"
                    ),
                )
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_ai_busy", False))

        import threading
        threading.Thread(
            target=worker, daemon=True, name=f"catalog-3i37-ai-{self.product_id}"
        ).start()

    def capture_ui(self):
        if getattr(self, "_phase49_3i33_screenshot_busy", False):
            return
        self._phase49_3i33_screenshot_busy = True
        dialog = ObservableJobDialog(self, "Screenshot صفحه محصول → تصاویر سایت")

        def worker():
            try:
                dialog.event("capture", "مرورگر صفحه واقعی محصول را Screenshot می‌گیرد…")
                result = capture_screenshot_for_site(self.app, int(self.product_id))
                dialog.done(
                    "Screenshot انتخاب شد و SEO/Metadata آماده است • "
                    f"Upstream: {result.get('source_page_url') or '—'}"
                )
                self.after(0, self.refresh_gallery)
                self.after(0, lambda: getattr(self, "_phase49_3i36_refresh_locks", lambda: None)())
            except Exception as exc:
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_screenshot_busy", False))

        import threading
        threading.Thread(
            target=worker, daemon=True, name=f"catalog-3i37-screenshot-{self.product_id}"
        ).start()

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "_phase49_3i37_source_label"):
            refresh_source_label(self)
        return result

    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class._phase49_3i37_refresh_source_label = refresh_source_label
    workspace_class._phase49_3i37_run_all = run_all
    workspace_class._phase49_3i33_capture_screenshot = capture_ui
    workspace_class._phase49_3i37_stage_ai = True
