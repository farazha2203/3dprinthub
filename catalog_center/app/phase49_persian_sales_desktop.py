from __future__ import annotations

import html
import json
import re


_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_BOILERPLATE = (
    "cookie settings",
    "we use cookies",
    "tracking technologies",
    "your consent",
    "privacy policy",
    "personalized content",
    "targeted ads",
)


def _clean(value, limit=0):
    text = html.unescape(str(value or ""))
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    if limit:
        text = text[:limit].rstrip()
    return text


def _fa(value, limit=0):
    text = _clean(value, limit)
    if not text or not _PERSIAN_RE.search(text):
        return ""
    lowered = text.casefold()
    if any(marker in lowered for marker in _BOILERPLATE):
        return ""
    return text


def _json_list(value):
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _value(row, key, default=""):
    try:
        return row[key]
    except Exception:
        return default


def _fallbacks(row):
    title = _fa(_value(row, "seo_title_fa"), 220) or _fa(_value(row, "title_fa"), 220)
    if not title:
        title = "محصول منتخب چاپ سه‌بعدی"

    description = (
        _fa(_value(row, "short_description_fa"), 1200)
        or _fa(_value(row, "seo_description_fa"), 1200)
        or _fa(_value(row, "description_fa"), 1200)
        or "برای خرید و سفارش این محصول چاپ سه‌بعدی، مشخصات، متریال‌های قابل انتخاب و قیمت را در صفحه محصول بررسی کنید."
    )

    image_alts = _json_list(_value(row, "image_alt_texts_json", "[]"))
    alt = next((_fa(item, 240) for item in image_alts if _fa(item, 240)), "")
    if not alt:
        alt = f"{title}؛ تصویر محصول برای خرید و سفارش چاپ سه‌بعدی از 3DPrintHub"[:240]

    keywords = [
        *_json_list(_value(row, "keywords_json", "[]")),
        *_json_list(_value(row, "tags_fa_json", "[]")),
    ]
    focus = next((_fa(item, 180) for item in keywords if _fa(item, 180)), "") or f"خرید {title}"[:180]
    return title, description, alt, focus


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_persian_sales_installed", False):
        return

    original_reload = workspace_class.reload
    original_save = workspace_class.save

    def fill_slider_copy_from_product(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        title, description, alt, focus = _fallbacks(row)
        self.slider_title_fa_var.set(title)
        self._text_set(self.slider_description_text, description)
        self.slider_alt_text_var.set(alt)
        if not _fa(self.slider_button_text_var.get(), 80):
            self.slider_button_text_var.set("مشاهده محصول")
        self.slider_focus_keyword_var.set(focus)
        self.footer_status.set("محتوای فارسی فروش اسلایدر از اطلاعات محصول پر شد؛ متن خام منبع استفاده نمی‌شود")

    def reload(self):
        result = original_reload(self)
        row = self.db.product(self.product_id)
        if row is None or not hasattr(self, "slider_title_fa_var"):
            return result
        title, description, alt, focus = _fallbacks(row)
        try:
            ai = self._slider_pack(row)
        except Exception:
            ai = {}
        slider_title = _fa(_value(row, "homepage_slider_title_fa"), 220) or _fa(ai.get("title_fa"), 220) or title
        slider_description = _fa(_value(row, "homepage_slider_description_fa"), 1200) or _fa(ai.get("description_fa"), 1200) or description
        slider_alt = _fa(_value(row, "homepage_slider_alt_text"), 240) or _fa(ai.get("image_alt_fa"), 240) or alt
        slider_focus = _fa(_value(row, "homepage_slider_focus_keyword"), 180) or _fa(ai.get("focus_keyword_fa"), 180) or focus
        slider_button = _fa(_value(row, "homepage_slider_button_text"), 80) or _fa(ai.get("button_text_fa"), 80) or "مشاهده محصول"
        self.slider_title_fa_var.set(slider_title)
        self._text_set(self.slider_description_text, slider_description)
        self.slider_alt_text_var.set(slider_alt)
        self.slider_focus_keyword_var.set(slider_focus)
        self.slider_button_text_var.set(slider_button)
        return result

    def save(self, silent=False):
        row = self.db.product(self.product_id)
        if row is not None and hasattr(self, "slider_title_fa_var"):
            title, description, alt, focus = _fallbacks(row)
            self.slider_title_fa_var.set(_fa(self.slider_title_fa_var.get(), 220) or title)
            current_description = self._text_get(self.slider_description_text)
            self._text_set(self.slider_description_text, _fa(current_description, 1200) or description)
            self.slider_alt_text_var.set(_fa(self.slider_alt_text_var.get(), 240) or alt)
            self.slider_focus_keyword_var.set(_fa(self.slider_focus_keyword_var.get(), 180) or focus)
            self.slider_button_text_var.set(_fa(self.slider_button_text_var.get(), 80) or "مشاهده محصول")
        return original_save(self, silent=silent)

    workspace_class.fill_slider_copy_from_product = fill_slider_copy_from_product
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_persian_sales_installed = True
