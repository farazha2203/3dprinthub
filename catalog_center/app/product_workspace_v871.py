from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk

from .epic49_desktop_schema import ensure_epic49_desktop_schema
from .product_workspace_v87 import ProductWorkspace as ProductWorkspace87
from .version import APP_VERSION


SLIDER_PACK_KEY = "homepage_slider_seo"


class ProductWorkspace(ProductWorkspace87):
    """Catalog Center 8.7.1 product workspace.

    Extends the stable 8.7 UX with a complete homepage-slider workflow:
    direct image selection from the gallery, AI-generated dedicated hero copy,
    and operator-editable title/description/alt/button/focus keyword fields.
    """

    def __init__(self, app, product_id: int):
        ensure_epic49_desktop_schema(app.db)
        super().__init__(app, product_id)
        self.title(f"Product Workspace | 3DPrintHub Catalog Center {APP_VERSION}")

    # ---------- homepage slider editor ----------
    def _publish_ui(self):
        super()._publish_ui()
        panel = ttk.LabelFrame(
            self.publish_tab,
            text="محتوای اختصاصی اسلایدر صفحه اول",
            padding=10,
            style="Card.TLabelframe",
        )
        panel.pack(fill="x", pady=(10, 0))
        panel.columnconfigure(1, weight=1)

        self.slider_title_fa_var = tk.StringVar(value="")
        self.slider_alt_text_var = tk.StringVar(value="")
        self.slider_button_text_var = tk.StringVar(value="مشاهده محصول")
        self.slider_focus_keyword_var = tk.StringVar(value="")

        ttk.Label(panel, text="عنوان کوتاه اسلایدر").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(panel, textvariable=self.slider_title_fa_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(panel, text="توضیح کوتاه اسلایدر").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.slider_description_text = tk.Text(panel, height=4, wrap="word", undo=True)
        self.slider_description_text.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(panel, text="Alt اختصاصی تصویر").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(panel, textvariable=self.slider_alt_text_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        row3 = ttk.Frame(panel)
        row3.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        row3.columnconfigure(1, weight=1)
        row3.columnconfigure(3, weight=1)
        ttk.Label(row3, text="متن دکمه").grid(row=0, column=0, sticky="w")
        ttk.Entry(row3, textvariable=self.slider_button_text_var, width=28).grid(row=0, column=1, sticky="ew", padx=(5, 15))
        ttk.Label(row3, text="عبارت هدف").grid(row=0, column=2, sticky="w")
        ttk.Entry(row3, textvariable=self.slider_focus_keyword_var).grid(row=0, column=3, sticky="ew", padx=(5, 0))

        actions = ttk.Frame(panel)
        actions.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=(8, 2))
        ttk.Button(
            actions,
            text="تولید/بازسازی با هوش مصنوعی",
            command=lambda: self.generate_ai("commerce"),
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            actions,
            text="پرکردن از محتوای فعلی محصول",
            command=self.fill_slider_copy_from_product,
        ).pack(side="left", padx=3)
        ttk.Label(
            actions,
            text="این متن‌ها برای H2، توضیح کوتاه، Alt تصویر و لینک داخلی صفحه اول استفاده می‌شوند؛ Meta اصلی صفحه اول مستقل می‌ماند.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=5)

    def _content_pack(self, row) -> dict:
        try:
            value = json.loads(row["content_pack_json"] or "{}")
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def _slider_pack(self, row) -> dict:
        pack = self._content_pack(row)
        value = pack.get(SLIDER_PACK_KEY) or {}
        return value if isinstance(value, dict) else {}

    def fill_slider_copy_from_product(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        self.slider_title_fa_var.set((row["seo_title_fa"] or row["title_fa"] or row["source_title"] or "").strip())
        self._text_set(
            self.slider_description_text,
            (row["short_description_fa"] or row["seo_description_fa"] or row["description_fa"] or "").strip(),
        )
        alts = self._json_list(row["image_alt_texts_json"])
        self.slider_alt_text_var.set((alts[0] if alts else (row["title_fa"] or row["source_title"] or "")).strip())
        if not self.slider_button_text_var.get().strip():
            self.slider_button_text_var.set("مشاهده محصول")
        keywords = self._json_list(row["keywords_json"])
        if not self.slider_focus_keyword_var.get().strip():
            self.slider_focus_keyword_var.set((keywords[0] if keywords else (row["title_fa"] or "")).strip())
        self.footer_status.set("محتوای اسلایدر از اطلاعات فعلی محصول پر شد؛ قبل از انتشار قابل ویرایش است")

    # ---------- direct gallery selection ----------
    def refresh_gallery(self):
        super().refresh_gallery()
        row = self.db.product(self.product_id)
        slider_url = str(row["homepage_slider_image_url"] or "").strip() if row is not None else ""
        for meta in getattr(self, "_gallery_cards", []):
            url = str(meta.get("url") or "")
            card = meta.get("label").master if meta.get("label") is not None else None
            if not card or not url:
                continue
            active = url == slider_url
            status = meta.get("status")
            if active and status is not None and "اسلایدر" not in status.get():
                status.set(status.get() + "  ◆ اسلایدر")
            ttk.Button(
                card,
                text="عکس اسلایدر صفحه اول" if active else "انتخاب برای اسلایدر",
                command=lambda selected_url=url: self.set_slider_image_from_gallery(selected_url),
                style="Primary.TButton" if active else "TButton",
            ).pack(fill="x", pady=(3, 0))

    def _persist_images(self, urls, selected, primary):
        """Keep the selected slider image physically eligible for the site batch."""
        urls = list(dict.fromkeys([str(value) for value in urls if value]))
        selected = list(dict.fromkeys([str(value) for value in selected if value]))
        row = self.db.product(self.product_id)
        slider_enabled = bool(row["homepage_slider_enabled"]) if row is not None else False
        slider_url = str(row["homepage_slider_image_url"] or "").strip() if row is not None else ""

        if slider_url and slider_url in urls:
            if slider_url not in selected:
                selected.append(slider_url)
        elif slider_enabled:
            replacement = primary if primary in urls else (selected[0] if selected else (urls[0] if urls else ""))
            self.db.update_product(self.product_id, {"homepage_slider_image_url": replacement})
            slider_url = replacement
            if replacement and replacement not in selected:
                selected.append(replacement)
        elif slider_url and slider_url not in urls:
            self.db.update_product(self.product_id, {"homepage_slider_image_url": ""})

        super()._persist_images(urls, selected, primary)

    def set_slider_image_from_gallery(self, url: str):
        row = self.db.product(self.product_id)
        if row is None:
            return
        urls = self._json_list(row["images_json"])
        selected = self._json_list(row["selected_images_json"])
        if url not in urls:
            return
        if url not in selected:
            selected.append(url)
        self.db.update_product(
            self.product_id,
            {
                "selected_images_json": json.dumps(list(dict.fromkeys(selected)), ensure_ascii=False),
                "homepage_slider_enabled": 1,
                "homepage_slider_image_url": url,
            },
        )
        if hasattr(self, "slider_enabled_var"):
            self.slider_enabled_var.set(1)
        self._refresh_slider_images()
        self.refresh_gallery()
        self.refresh_checklists()
        self.footer_status.set("این تصویر برای اسلایدر صفحه اول انتخاب شد و در تصاویر سایت باقی می‌ماند")

    # ---------- AI pack + persistence ----------
    def reload(self):
        ensure_epic49_desktop_schema(self.db)
        super().reload()
        row = self.db.product(self.product_id)
        if row is None or not hasattr(self, "slider_title_fa_var"):
            return
        ai = self._slider_pack(row)
        title = str(row["homepage_slider_title_fa"] or ai.get("title_fa") or row["title_fa"] or row["source_title"] or "").strip()
        description = str(
            row["homepage_slider_description_fa"]
            or ai.get("description_fa")
            or row["short_description_fa"]
            or row["seo_description_fa"]
            or ""
        ).strip()
        image_alts = self._json_list(row["image_alt_texts_json"])
        alt_text = str(
            row["homepage_slider_alt_text"]
            or ai.get("image_alt_fa")
            or (image_alts[0] if image_alts else "")
            or row["title_fa"]
            or row["source_title"]
            or ""
        ).strip()
        button = str(row["homepage_slider_button_text"] or ai.get("button_text_fa") or "مشاهده محصول").strip()
        focus = str(row["homepage_slider_focus_keyword"] or ai.get("focus_keyword_fa") or "").strip()
        self.slider_title_fa_var.set(title)
        self._text_set(self.slider_description_text, description)
        self.slider_alt_text_var.set(alt_text)
        self.slider_button_text_var.set(button)
        self.slider_focus_keyword_var.set(focus)

    def save(self, silent=False):
        if not super().save(silent=True):
            return False
        row = self.db.product(self.product_id)
        if row is None or not hasattr(self, "slider_title_fa_var"):
            return False
        slider_pack = {
            "title_fa": self.slider_title_fa_var.get().strip(),
            "description_fa": self._text_get(self.slider_description_text),
            "image_alt_fa": self.slider_alt_text_var.get().strip(),
            "button_text_fa": self.slider_button_text_var.get().strip() or "مشاهده محصول",
            "focus_keyword_fa": self.slider_focus_keyword_var.get().strip(),
        }
        pack = self._content_pack(row)
        pack[SLIDER_PACK_KEY] = slider_pack
        self.db.update_product(
            self.product_id,
            {
                "homepage_slider_title_fa": slider_pack["title_fa"],
                "homepage_slider_description_fa": slider_pack["description_fa"],
                "homepage_slider_alt_text": slider_pack["image_alt_fa"],
                "homepage_slider_button_text": slider_pack["button_text_fa"],
                "homepage_slider_focus_keyword": slider_pack["focus_keyword_fa"],
                "content_pack_json": json.dumps(pack, ensure_ascii=False),
            },
        )
        self.row = self.db.product(self.product_id)
        if not silent:
            self.footer_status.set("تنظیمات محصول و محتوای اختصاصی اسلایدر ذخیره شد")
        return True
