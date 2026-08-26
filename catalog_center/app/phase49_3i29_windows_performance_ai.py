from __future__ import annotations

import json
import math
from typing import Any, Iterable

import tkinter as tk
from tkinter import ttk

from . import openai_content as content_module
from .ai_providers import AIProviderClient
from .phase49_diagnostics import audit_event
from .phase49_3i17_single_active_ai_runtime import (
    _clean_model,
    _patch_app_instance,
    install as install_single_active_ai_runtime,
)


PHASE = "49.3I.29"
PRODUCT_PAGE_SIZE = 48


def page_slice(values: Iterable[Any], page: int, page_size: int = PRODUCT_PAGE_SIZE) -> tuple[int, int, list[Any]]:
    """Return a bounded page without discarding the full product result set."""
    rows = list(values)
    size = max(1, int(page_size or PRODUCT_PAGE_SIZE))
    total_pages = max(1, int(math.ceil(len(rows) / size)))
    current = max(0, min(int(page or 0), total_pages - 1))
    start = current * size
    return current, total_pages, rows[start : start + size]


def minimal_product_payload(source: dict[str, Any] | None) -> dict[str, str]:
    """Only operator/source title + description are factual product inputs for AI.

    Pricing, stock, material/color selections, internal IDs, categories, licenses,
    workflow fields and other business state stay local. Explicit image AI actions
    may still attach the selected image bytes/URLs separately.
    """
    source = source or {}
    return {
        "source_title": str(source.get("source_title") or "").strip(),
        "source_description": str(source.get("source_description") or "").strip(),
    }


def _install_exact_saved_model_execution() -> None:
    if getattr(AIProviderClient, "_phase49_3i29_exact_saved_model", False):
        return
    original_choose = AIProviderClient.choose_model

    def choose_model(self, preferred: str = "") -> str:
        exact = _clean_model(preferred or getattr(self, "model", ""))
        if getattr(self, "product_id", None) is not None:
            if not exact:
                raise RuntimeError(
                    f"برای Provider فعال {self.provider} هیچ Model ذخیره‌شده‌ای وجود ندارد؛ "
                    "از تنظیمات مادر هوش مصنوعی Provider و Model را ذخیره کن."
                )
            # Product work must never issue a hidden GET /models. The explicit
            # operator-saved model is the execution contract. Settings > model
            # discovery/test keeps the original live listing behavior.
            return exact
        return original_choose(self, preferred)

    AIProviderClient.choose_model = choose_model
    AIProviderClient._phase49_3i29_exact_saved_model = True


def _install_minimal_product_ai_payload() -> None:
    Service = content_module.AIContentService
    if getattr(Service, "_phase49_3i29_minimal_payload", False):
        return

    def enrich_product(
        self,
        source: dict[str, Any],
        local_categories: list[dict[str, str]],
        image_count: int = 0,
        image_urls: list[str] | None = None,
        mode: str = "commerce",
    ) -> dict[str, Any]:
        payload = minimal_product_payload(source)
        if not payload["source_title"] and not payload["source_description"]:
            raise RuntimeError("برای ارسال به AI حداقل عنوان یا متن منبع باید موجود باشد.")

        content: list[dict[str, Any]] = [
            {"type": "input_text", "text": json.dumps(payload, ensure_ascii=False)}
        ]
        # Images are not part of the normal product fact payload. They remain
        # available only because the mature dedicated image-SEO action explicitly
        # supplies image_urls. No stock/pricing/material/category state is sent.
        for url in (image_urls or [])[:4]:
            value = str(url or "").strip()
            if value.startswith(("http://", "https://")):
                content.append({"type": "input_image", "image_url": value, "detail": "auto"})

        strict_translate = str(mode or "commerce").lower() == "translate"
        instructions = (
            ("You are a precise Persian technical translator. " if strict_translate else "")
            + "You are the Persian ecommerce/SEO editor for 3DPrintHub. "
            + "The ONLY factual product inputs are source_title and source_description in the JSON payload. "
            + "Do not infer or invent dimensions, weight, price, stock, license, compatibility, material, color, category IDs, author, file availability or engineering performance when they are absent from those two fields. "
            + "Keep the concrete product identity in title_fa and produce natural Persian short/long descriptions and SEO copy grounded only in the supplied title/description. "
            + "If the schema asks for unsupported technical facts, use empty values/arrays and explain missing facts in content_notes instead of fabricating them. "
            + "suggested_category_slug must be empty because site taxonomy is not transmitted to AI. "
            + "Material recommendations must be conservative and only justified by explicit usage facts in the supplied text; otherwise return no recommendation. "
            + "Image alt text may describe an explicitly attached image, but must not add unsupported product claims. "
            + "Always return exactly one JSON object matching the requested schema. "
            + ("Translate faithfully and do not add marketing claims." if strict_translate else "Write persuasive but factual Persian copy.")
        )

        audit_event(
            "ai",
            "minimal_product_payload",
            status="running",
            product_id=getattr(self, "product_id", None),
            source_file=__file__,
            message=f"provider={self.provider} model={self.model} text_fields=2 images={max(0, len(content)-1)}",
            detail={
                "phase": PHASE,
                "provider": self.provider,
                "model": self.model,
                "sent_product_fields": ["source_title", "source_description"],
                "local_categories_sent": False,
                "business_state_sent": False,
                "image_count": max(0, len(content) - 1),
            },
        )
        result, model = self.client.structured_response(
            instructions=instructions,
            input_content=content,
            schema=content_module.CONTENT_SCHEMA,
            schema_name="catalog_content_pack_v871",
            preferred_model=self.model,
        )
        content_module.validate_content_pack(result, payload["source_title"])
        result["_ai_provider"] = self.provider
        result["_ai_model"] = model
        return result

    Service.enrich_product = enrich_product
    content_module.OpenAIContentService = Service
    Service._phase49_3i29_minimal_payload = True


def _install_runtime_contracts() -> None:
    _install_exact_saved_model_execution()
    _install_minimal_product_ai_payload()


def install_app(app_class) -> None:
    """Bound Products-page rendering and make the saved AI profile global runtime truth."""
    if getattr(app_class, "_phase49_3i29_windows_performance_ai", False):
        return
    _install_runtime_contracts()

    original_init = app_class.__init__
    original_modernize = getattr(app_class, "_modernize_products_page", None)
    original_render = getattr(app_class, "_phase49_3i_render_gallery", None)
    original_refresh = getattr(app_class, "refresh_products", None)

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Mother AI settings become authoritative as soon as the application is
        # ready, not only after opening a ProductWorkspace.
        _patch_app_instance(self)
        self._phase49_3i29_products_dirty = False

    def _phase49_3i29_mark_products_dirty(self, reason: str = "workspace"):
        self._phase49_3i29_products_dirty = True
        try:
            self.logger.debug("PHASE49_3I29_PRODUCTS_DIRTY reason=%s", reason)
        except Exception:
            pass

    def _phase49_3i29_flush_products_refresh(self):
        if not getattr(self, "_phase49_3i29_products_dirty", False):
            return False
        self._phase49_3i29_products_dirty = False
        refresh = getattr(self, "refresh_products", None)
        if callable(refresh):
            refresh()
        return True

    def _phase49_3i29_change_page(self, delta: int):
        self._phase49_3i29_product_page = max(
            0, int(getattr(self, "_phase49_3i29_product_page", 0) or 0) + int(delta)
        )
        renderer = getattr(self, "_phase49_3i_render_gallery", None)
        if callable(renderer):
            renderer()

    def _modernize_products_page(self):
        if callable(original_modernize):
            original_modernize(self)
        self._phase49_3i29_product_page = 0
        self._phase49_3i29_visible_product_ids = []
        self._phase49_3i29_page_text = tk.StringVar(value="صفحه ۱ از ۱")
        pager = ttk.Frame(self.products_tab)
        pager.pack(fill="x", pady=(4, 7))
        ttk.Button(
            pager,
            text="صفحه قبل",
            command=lambda: self._phase49_3i29_change_page(-1),
        ).pack(side="right", padx=4)
        ttk.Label(pager, textvariable=self._phase49_3i29_page_text).pack(side="right", padx=8)
        ttk.Button(
            pager,
            text="صفحه بعد",
            command=lambda: self._phase49_3i29_change_page(1),
        ).pack(side="right", padx=4)
        ttk.Label(
            pager,
            text=f"حداکثر {PRODUCT_PAGE_SIZE} کارت در هر صفحه؛ همه نتایج در دیتابیس حفظ می‌شوند.",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=6)
        self._phase49_3i29_pager = pager

    def _phase49_3i_render_gallery(self):
        if not callable(original_render):
            return None
        tree = getattr(self, "product_tree", None)
        if tree is None:
            return original_render(self)

        all_iids = list(tree.get_children())
        current, pages, visible_iids = page_slice(
            all_iids,
            getattr(self, "_phase49_3i29_product_page", 0),
            PRODUCT_PAGE_SIZE,
        )
        self._phase49_3i29_product_page = current
        visible_set = set(visible_iids)
        selected_before = set(getattr(self, "_phase49_3i_selected_products", set()) or set())
        all_ids: list[int] = []
        for iid in all_iids:
            try:
                all_ids.append(int(iid))
            except Exception:
                pass
        visible_ids: list[int] = []
        for iid in visible_iids:
            try:
                visible_ids.append(int(iid))
            except Exception:
                pass
        self._phase49_3i29_visible_product_ids = visible_ids

        hidden = [iid for iid in all_iids if iid not in visible_set]
        for iid in hidden:
            try:
                tree.detach(iid)
            except Exception:
                pass
        try:
            result = original_render(self)
        finally:
            # Restore the hidden compatibility Treeview exactly; pagination is a
            # view-layer optimization, never a data/query truncation.
            for index, iid in enumerate(all_iids):
                try:
                    tree.move(iid, "", index)
                except Exception:
                    pass
            self._phase49_3i_product_order = all_ids
            self._phase49_3i_selected_products = selected_before & set(all_ids)
            updater = getattr(self, "_phase49_3i_update_selection_visuals", None)
            if callable(updater):
                updater()
            label = getattr(self, "_phase49_3i29_page_text", None)
            if label is not None:
                start = current * PRODUCT_PAGE_SIZE + (1 if all_iids else 0)
                end = min(len(all_iids), (current + 1) * PRODUCT_PAGE_SIZE)
                label.set(f"صفحه {current + 1} از {pages} • {start} تا {end} از {len(all_iids)}")
        return result

    def refresh_products(self):
        self._phase49_3i29_product_page = 0
        self._phase49_3i29_products_dirty = False
        if callable(original_refresh):
            return original_refresh(self)
        return None

    app_class.__init__ = __init__
    if callable(original_modernize):
        app_class._modernize_products_page = _modernize_products_page
    if callable(original_render):
        app_class._phase49_3i_render_gallery = _phase49_3i_render_gallery
    if callable(original_refresh):
        app_class.refresh_products = refresh_products
    app_class._phase49_3i29_mark_products_dirty = _phase49_3i29_mark_products_dirty
    app_class._phase49_3i29_flush_products_refresh = _phase49_3i29_flush_products_refresh
    app_class._phase49_3i29_change_page = _phase49_3i29_change_page
    app_class._phase49_3i29_windows_performance_ai = True


def install_workspace(workspace_class, phase49_3f_workspace_module) -> None:
    """Stop ProductWorkspace saves/AI from rebuilding the global Products gallery."""
    if getattr(workspace_class, "_phase49_3i29_deferred_global_refresh", False):
        return
    _install_runtime_contracts()
    # Re-assert the already-proven single-active-AI contract at the final 49.3I
    # composition boundary. It is idempotent and keeps AvalAI/OpenRouter/OpenAI/
    # Google under the same saved Provider/Model/key policy.
    install_single_active_ai_runtime(workspace_class, phase49_3f_workspace_module)

    original_provider = workspace_class._phase49_3e_provider
    original_save = workspace_class.save
    original_close = workspace_class.close

    def _phase49_3e_provider(self):
        try:
            provider, key, model = original_provider(self)
        except Exception as exc:
            audit_event(
                "ai",
                "active_profile_preflight_error",
                status="error",
                level="ERROR",
                product_id=getattr(self, "product_id", None),
                source_file=__file__,
                message=str(exc)[:900],
                detail={"phase": PHASE},
            )
            raise
        audit_event(
            "ai",
            "active_profile_resolved",
            status="ok",
            product_id=getattr(self, "product_id", None),
            source_file=__file__,
            message=f"provider={provider} model={model}",
            detail={
                "phase": PHASE,
                "provider": provider,
                "model": model,
                "key_present": bool(key),
                "source": "mother_ai_settings",
                "hidden_model_list_request": False,
            },
        )
        return provider, key, model

    def save(self, silent=False):
        app = getattr(self, "app", None)
        marker = getattr(app, "_phase49_3i29_mark_products_dirty", None)
        if app is None or not callable(marker):
            return original_save(self, silent=silent)

        saved_methods = {}
        for name in ("refresh_products", "refresh_published", "load_product"):
            method = getattr(app, name, None)
            if not callable(method):
                continue
            saved_methods[name] = method

            def deferred(*_args, _name=name, **_kwargs):
                marker(f"workspace-{_name}")
                return None

            setattr(app, name, deferred)
        try:
            result = original_save(self, silent=silent)
        finally:
            for name, method in saved_methods.items():
                setattr(app, name, method)
        if result:
            marker("workspace-save")
        return result

    def close(self):
        app = getattr(self, "app", None)
        try:
            return original_close(self)
        finally:
            flush = getattr(app, "_phase49_3i29_flush_products_refresh", None)
            if callable(flush):
                flush()

    workspace_class._phase49_3e_provider = _phase49_3e_provider
    workspace_class.save = save
    workspace_class.close = close
    workspace_class._phase49_3i29_deferred_global_refresh = True
