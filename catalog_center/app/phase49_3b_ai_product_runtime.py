from __future__ import annotations

import threading
from tkinter import messagebox

from .openai_content import AIContentService
from .phase49_diagnostics import audit_event
from .phase49_readiness_wizard import selected_color_names, selected_material_names, sync_seo_reference_lists


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3b_ai_runtime_installed", False):
        return

    def generate_ai(self, mode: str):
        if getattr(self, "_ai_busy", False):
            return
        try:
            sync_seo_reference_lists(self)
        except Exception:
            pass
        self.save(silent=True)
        provider = self.app._selected_ai_provider()
        key = self.app._ai_key(provider)
        if not key:
            messagebox.showwarning(
                "3DPrintHub",
                f"API Key برای {provider} تنظیم نشده است. از «هوش مصنوعی» کارت همین Provider را تکمیل و تست کن.",
                parent=self,
            )
            return
        row = self.db.product(self.product_id)
        images = self._json_list(row["selected_images_json"] or row["images_json"])
        model = self.app.ai_model.get().strip()
        categories = self.app.get_all_categories()
        self._ai_busy = True
        self.ai_status.set(f"{provider} در حال ترجمه…" if mode == "translate" else f"{provider} در حال تولید محتوا…")
        self.footer_status.set(self.ai_status.get())
        audit_event(
            "ai",
            "product_content_start",
            product_id=self.product_id,
            message=f"provider={provider} model={model} mode={mode}",
            source_file="catalog_center/app/phase49_3b_ai_product_runtime.py",
        )

        def worker():
            try:
                source = dict(self._source_for_ai() or {})
                source["selected_materials"] = selected_material_names(row)
                source["selected_colors"] = selected_color_names(row)
                pack = AIContentService(key, model, provider, product_id=self.product_id).enrich_product(
                    source,
                    categories,
                    image_count=len(images),
                    image_urls=images,
                    mode=mode,
                )
                self.after(0, lambda: self.preview_ai_pack(pack, mode))
            except Exception as exc:
                audit_event(
                    "ai",
                    "product_content_error",
                    status="error",
                    level="ERROR",
                    product_id=self.product_id,
                    message=f"provider={provider} model={model}: {exc}",
                    source_file="catalog_center/app/phase49_3b_ai_product_runtime.py",
                )
                self.after(0, lambda: messagebox.showerror(f"{provider} — خطای هوش مصنوعی", str(exc), parent=self))
                self.after(0, lambda: self.ai_status.set(f"خطا در {provider} — جزئیات در لاگ برنامه"))
            finally:
                self.after(0, lambda: setattr(self, "_ai_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    workspace_class.generate_ai = generate_ai
    workspace_class._phase49_3b_ai_runtime_installed = True
