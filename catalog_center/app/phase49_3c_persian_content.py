from __future__ import annotations

import hashlib
import html as html_lib
import json
import logging
import re
from html.parser import HTMLParser
from typing import Any

from .openai_content import AIContentService, CONTENT_SCHEMA

_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_LATIN_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9._+\\-]*")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_EDITORIAL_SCALARS = (
    "title_fa", "short_description_fa", "description_fa", "use_description_fa",
    "seo_title_fa", "seo_description_fa", "social_caption_fa", "use_case_class",
)
_EDITORIAL_LISTS = (
    "categories_fa", "tags_fa", "hashtags_fa", "target_keywords_fa",
    "sales_bullets", "image_alt_texts", "content_notes",
)
_SLIDER_FIELDS = ("title_fa", "description_fa", "image_alt_fa", "button_text_fa", "focus_keyword_fa")
_ALLOWED_TAGS = {"p", "br", "strong", "em", "ul", "ol", "li", "h3", "h4"}


def _plain_text(value: Any) -> str:
    return _HTML_TAG_RE.sub(" ", str(value or ""))


def has_persian_editorial_text(value: Any, *, minimum: int = 2) -> bool:
    text = _plain_text(value)
    fa = len(_PERSIAN_RE.findall(text))
    if fa < minimum:
        return False
    latin = len(_LATIN_RE.findall(text))
    return latin == 0


def has_persian_editorial_text_for_source(
    value: Any,
    source_title: Any,
    *,
    minimum: int = 2,
) -> bool:
    """Accept Persian text plus only Latin identity tokens found in source_title."""
    text = _plain_text(value)
    if len(_PERSIAN_RE.findall(text)) < minimum:
        return False
    actual = {token.casefold() for token in _LATIN_TOKEN_RE.findall(text)}
    if not actual:
        return True
    allowed = {token.casefold() for token in _LATIN_TOKEN_RE.findall(_plain_text(source_title))}
    return bool(allowed) and actual.issubset(allowed)


class _SafeHtml(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in _ALLOWED_TAGS:
            self.parts.append(f"<{tag}>")

    def handle_startendtag(self, tag, attrs):
        if tag.lower() == "br":
            self.parts.append("<br>")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _ALLOWED_TAGS and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(html_lib.escape(data, quote=False))


def sanitize_fa_html(value: str) -> str:
    parser = _SafeHtml()
    try:
        parser.feed(str(value or ""))
        parser.close()
    except Exception:
        return html_lib.escape(str(value or ""), quote=False)
    return "".join(parser.parts).strip()


def ensure_html_fragment(value: str) -> str:
    cleaned = sanitize_fa_html(value)
    if not cleaned:
        return ""
    if "<" not in cleaned:
        return "".join(
            f"<p>{html_lib.escape(line.strip(), quote=False)}</p>"
            for line in cleaned.splitlines() if line.strip()
        )
    return cleaned


def _unique(values) -> list[str]:
    out, seen = [], set()
    for value in values or []:
        text = str(value or "").strip()
        if text and text.casefold() not in seen:
            seen.add(text.casefold())
            out.append(text)
    return out


def _persian_list(values) -> list[str]:
    return [item for item in _unique(values) if has_persian_editorial_text(item)]


def _language_invalid_fields(pack: dict, image_count: int = 0) -> list[str]:
    invalid = []
    for key in _EDITORIAL_SCALARS:
        if not has_persian_editorial_text(pack.get(key)):
            invalid.append(key)
    for key in _EDITORIAL_LISTS:
        values = pack.get(key)
        if not isinstance(values, list) or not values or any(not has_persian_editorial_text(x) for x in values):
            invalid.append(key)
    slider = pack.get("homepage_slider_seo")
    if not isinstance(slider, dict):
        invalid.append("homepage_slider_seo")
    else:
        for key in _SLIDER_FIELDS:
            if not has_persian_editorial_text(slider.get(key)):
                invalid.append(f"homepage_slider_seo.{key}")
    if image_count and len(pack.get("image_alt_texts") or []) < min(int(image_count), 10):
        if "image_alt_texts" not in invalid:
            invalid.append("image_alt_texts")
    return invalid


def _generic_persian_pack(pack: dict, image_count: int) -> dict:
    result = dict(pack)
    fallback_needed = bool(_language_invalid_fields(pack, image_count))
    title = result.get("title_fa") if has_persian_editorial_text(pack.get("title_fa")) else "محصول چاپ سه‌بعدی"
    short = result.get("short_description_fa") if has_persian_editorial_text(pack.get("short_description_fa")) else (
        "این محصول برای چاپ سه‌بعدی و استفاده در پروژه‌های ساخت و تولید آماده بررسی است."
    )
    desc = result.get("description_fa") if has_persian_editorial_text(pack.get("description_fa")) else (
        "<p>این محصول برای چاپ سه‌بعدی طراحی شده است و می‌تواند بر اساس مشخصات، "
        "متریال و گزینه‌های تأییدشده اپراتور تولید شود.</p>"
    )
    use_desc = result.get("use_description_fa") if has_persian_editorial_text(pack.get("use_description_fa")) else (
        "کاربرد محصول بر اساس مشخصات منبع و گزینه‌های تأییدشده اپراتور قابل بررسی و تولید است."
    )
    result["title_fa"] = str(title).strip()[:260]
    result["short_description_fa"] = str(short).strip()[:500]
    result["description_fa"] = ensure_html_fragment(str(desc))
    result["use_description_fa"] = str(use_desc).strip()[:500]

    categories = _persian_list(result.get("categories_fa")) or ["محصولات چاپ سه‌بعدی"]
    keywords = _persian_list(result.get("target_keywords_fa"))
    if len(keywords) < 3:
        keywords = _unique([*keywords, "خرید محصول چاپ سه‌بعدی", "سفارش محصول سه‌بعدی", "قیمت چاپ سه‌بعدی"])
    tags = _persian_list(result.get("tags_fa")) or ["چاپ سه‌بعدی", "محصول سه‌بعدی", "مدل سه‌بعدی"]
    hashtags = _persian_list(result.get("hashtags_fa")) or ["#چاپ_سه_بعدی", "#پرینت_سه_بعدی", "#مدل_سه_بعدی"]
    result["categories_fa"] = categories[:12]
    result["target_keywords_fa"] = [x for x in keywords if has_persian_editorial_text(x)][:12]
    result["tags_fa"] = tags[:12]
    result["hashtags_fa"] = hashtags[:12]
    result["seo_title_fa"] = (
        str(result.get("seo_title_fa")).strip()[:260]
        if has_persian_editorial_text(result.get("seo_title_fa"))
        else "خرید و سفارش محصول چاپ سه‌بعدی"
    )
    result["seo_description_fa"] = (
        str(result.get("seo_description_fa")).strip()[:500]
        if has_persian_editorial_text(result.get("seo_description_fa"))
        else "اطلاعات محصول، گزینه‌های سفارش و جزئیات چاپ سه‌بعدی را بررسی کنید."
    )
    bullets = _persian_list(result.get("sales_bullets")) or [
        "قابل بررسی و سفارش بر اساس مشخصات تأییدشده محصول.",
        "امکان انتخاب گزینه‌های واقعی متریال و رنگ توسط اپراتور.",
    ]
    result["sales_bullets"] = bullets[:8]
    result["social_caption_fa"] = (
        str(result.get("social_caption_fa")).strip()[:500]
        if has_persian_editorial_text(result.get("social_caption_fa"))
        else "اطلاعات محصول و گزینه‌های سفارش را بررسی کنید."
    )
    alts = _persian_list(result.get("image_alt_texts"))
    while len(alts) < min(max(0, int(image_count)), 10):
        alts.append(f"محصول چاپ سه‌بعدی - نمای {len(alts) + 1}")
    result["image_alt_texts"] = alts[:10]
    result["content_notes"] = _persian_list(result.get("content_notes"))[:12]

    recs = result.get("material_recommendations")
    if not isinstance(recs, list) or not recs:
        recs = [{"material": "PLA", "score": 40, "recommended": False,
                 "reason_fa": "پیشنهاد اولیه است و متریال واقعی باید توسط اپراتور تأیید شود."}]
    clean_recs = []
    for item in recs:
        if not isinstance(item, dict):
            continue
        clean_recs.append({
            "material": str(item.get("material") or "PLA").strip(),
            "score": max(0, min(100, int(item.get("score") or 0))),
            "recommended": bool(item.get("recommended")),
            "reason_fa": (
                str(item.get("reason_fa")).strip()
                if has_persian_editorial_text(item.get("reason_fa"))
                else "پیشنهاد اولیه است و نیاز به بررسی اپراتور دارد."
            ),
        })
    result["material_recommendations"] = clean_recs or recs

    slider = dict(result.get("homepage_slider_seo") or {}) if isinstance(result.get("homepage_slider_seo"), dict) else {}
    defaults = {
        "title_fa": result["title_fa"],
        "description_fa": result["short_description_fa"],
        "image_alt_fa": result["image_alt_texts"][0] if result["image_alt_texts"] else result["title_fa"],
        "button_text_fa": "مشاهده محصول",
        "focus_keyword_fa": result["target_keywords_fa"][0],
    }
    for key, fallback in defaults.items():
        if not has_persian_editorial_text(slider.get(key)):
            slider[key] = fallback
    result["homepage_slider_seo"] = slider
    result["_phase49_3c_persian_fallback"] = fallback_needed
    return result


def _repair_with_provider(service, source, result, missing, image_count):
    repair_input = {
        "source": {
            "source_title": source.get("source_title") or "",
            "source_description": source.get("source_description") or "",
            "source_categories": source.get("source_categories") or [],
            "source_specs": source.get("source_specs") or {},
            "selected_materials": source.get("selected_materials") or [],
            "selected_colors": source.get("selected_colors") or [],
            "image_count": min(max(0, int(image_count or 0)), 10),
        },
        "current_pack": result,
        "missing_or_non_persian_fields": missing,
    }
    instructions = (
        "این درخواست اصلاح اجباری محتوای فارسی برای 3DPrintHub است. "
        "تمام فیلدهای فارسی و تمام فیلدهای SEO باید فارسی روان باشند و متن انگلیسی منبع را کپی نکنند. "
        "کدهای فنی و نام مدل فقط در صورت نیاز واقعی مجازند؛ در SEO و عبارت‌های جستجو انگلیسی ننویس. "
        "use_description_fa را حتماً فارسی و درباره کاربرد محصول تولید کن. "
        "description_fa باید HTML fragment معتبر و تمیز با فقط p,strong,em,ul,ol,li,h3,h4,br باشد؛ "
        "هیچ script/style/iframe/event handler یا URL جدید تولید نکن. "
        "قیمت، موجودی، مجوز، ابعاد، رنگ و متریال انتخاب‌شده را جعل نکن. "
        "کل object را مطابق schema برگردان."
    )
    return service.client.structured_response(
        instructions=instructions,
        input_content=[{"type": "input_text", "text": json.dumps(repair_input, ensure_ascii=False)}],
        schema=CONTENT_SCHEMA,
        schema_name="catalog_content_pack_v871_persian_repair",
        preferred_model=service.model,
    )


def install() -> None:
    if getattr(AIContentService, "_phase49_3c_persian_installed", False):
        return
    CONTENT_SCHEMA.setdefault("properties", {})["use_description_fa"] = {"type": "string"}
    required = list(CONTENT_SCHEMA.get("required") or [])
    if "use_description_fa" not in required:
        required.append("use_description_fa")
    CONTENT_SCHEMA["required"] = required

    original = AIContentService.enrich_product
    logger = logging.getLogger("3dprinthub.phase49_3c.persian")

    def enrich_product(self, source, local_categories, image_count=0, image_urls=None, mode="commerce"):
        result = original(self, source, local_categories, image_count=image_count, image_urls=image_urls, mode=mode)
        if str(mode or "commerce").lower() != "commerce":
            return result
        missing = _language_invalid_fields(result, image_count)
        if missing:
            try:
                repaired, model = _repair_with_provider(self, source, result, missing, image_count)
                if isinstance(repaired, dict):
                    for key in missing:
                        root = key.split(".", 1)[0]
                        if repaired.get(root):
                            result[root] = repaired[root]
                    result["_ai_model"] = model
                    result["_phase49_3c_persian_repair"] = True
            except Exception as exc:
                logger.exception("AI_PERSIAN_REPAIR_FAILED provider=%s model=%s", self.provider, self.model)
                result["_phase49_3c_persian_repair_error"] = f"{type(exc).__name__}: {exc}"
        result = _generic_persian_pack(result, image_count)
        result["_phase49_3c_persian_invalid_after_repair"] = _language_invalid_fields(result, image_count)
        return result

    AIContentService.enrich_product = enrich_product
    AIContentService._phase49_3c_persian_installed = True


def install_workspace(workspace_class, readiness_module=None) -> None:
    if getattr(workspace_class, "_phase49_3c_persian_workspace_installed", False):
        return
    original_reload = workspace_class.reload
    original_save = workspace_class.save

    def reload(self):
        result = original_reload(self)
        row = self.db.product(self.product_id)
        if row is None:
            return result
        fields = (
            ("content_seo_title", "seo_title_fa", "var"),
            ("content_seo_desc", "seo_description_fa", "text"),
            ("content_social_caption", "social_caption_fa", "text"),
            ("content_sales_bullets", "sales_bullets_json", "list"),
            ("content_image_alts", "image_alt_texts_json", "list"),
            ("content_categories_fa", "categories_fa_json", "list"),
            ("content_tags_fa", "tags_fa_json", "list"),
            ("content_hashtags_fa", "hashtags_fa_json", "list"),
            ("content_keywords", "keywords_json", "list"),
            ("content_materials", "materials_json", "list"),
            ("content_colors", "colors_json", "list"),
            ("content_material_recommendations", "material_recommendations_json", "json"),
        )
        for attr, key, kind in fields:
            widget = getattr(self, attr, None)
            if widget is None or key not in row.keys():
                continue
            raw = row[key]
            try:
                if kind == "var":
                    widget.set(str(raw or ""))
                elif kind == "text":
                    self._text_set(widget, str(raw or ""))
                elif kind == "list":
                    self._text_set(widget, "\n".join(_unique(json.loads(raw or "[]"))))
                else:
                    self._text_set(widget, json.dumps(json.loads(raw or "[]"), ensure_ascii=False, indent=2))
            except Exception:
                continue
        return result

    def save(self, silent=False):
        if not original_save(self, silent=True):
            return False
        values = {}
        def list_value(attr):
            widget = getattr(self, attr, None)
            if widget is None:
                return []
            try:
                return [line.strip() for line in widget.get("1.0", "end").splitlines() if line.strip()]
            except Exception:
                return []
        if hasattr(self, "content_seo_title"):
            values["seo_title_fa"] = str(self.content_seo_title.get() or "").strip()
        for attr, key in (("content_seo_desc", "seo_description_fa"), ("content_social_caption", "social_caption_fa")):
            widget = getattr(self, attr, None)
            if widget is not None:
                values[key] = widget.get("1.0", "end").strip()
        for attr, key in (
            ("content_sales_bullets", "sales_bullets_json"),
            ("content_image_alts", "image_alt_texts_json"),
            ("content_categories_fa", "categories_fa_json"),
            ("content_tags_fa", "tags_fa_json"),
            ("content_hashtags_fa", "hashtags_fa_json"),
            ("content_keywords", "keywords_json"),
            ("content_materials", "materials_json"),
            ("content_colors", "colors_json"),
        ):
            values[key] = json.dumps(list_value(attr), ensure_ascii=False)
        recs = getattr(self, "content_material_recommendations", None)
        if recs is not None:
            try:
                payload = json.loads(recs.get("1.0", "end").strip() or "[]")
                if not isinstance(payload, list):
                    raise ValueError("پیشنهادهای متریال باید JSON Array باشند")
                values["material_recommendations_json"] = json.dumps(payload, ensure_ascii=False)
            except Exception as exc:
                if not silent:
                    from tkinter import messagebox
                    messagebox.showerror("3DPrintHub", f"JSON پیشنهاد متریال معتبر نیست: {exc}", parent=self)
                return False
        self.db.update_product(self.product_id, values)
        self.row = self.db.product(self.product_id)
        if not silent:
            self.footer_status.set("محتوای فارسی و SEO ذخیره شد")
        return True

    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class._phase49_3c_persian_workspace_installed = True


def install_app(app_class) -> None:
    if getattr(app_class, "_phase49_3c_persian_app_installed", False):
        return
    original_apply = app_class._apply_ai_pack
    def apply(self, product_id, pack, open_studio=True):
        result = original_apply(self, product_id, pack, open_studio=open_studio)
        updates = {}
        if isinstance(pack, dict) and "use_description_fa" in pack:
            updates["use_description"] = str(pack.get("use_description_fa") or "").strip()
        if isinstance(pack, dict) and pack.get("_phase49_3c_persian_fallback"):
            updates["translation_status"] = "needs_review"
            updates["content_status"] = "needs_review"
        if updates:
            self.db.update_product(product_id, updates)
        return result
    app_class._apply_ai_pack = apply
    app_class._phase49_3c_persian_app_installed = True


def install_readiness(readiness_module) -> None:
    try:
        from . import phase49_3c_operator_recovery as operator_module
        if not getattr(operator_module, "_phase49_3c_persian_snapshot_installed", False):
            original_snapshot = operator_module.build_live_snapshot
            def build_live_snapshot(workspace, base_row):
                data = original_snapshot(workspace, base_row)
                widget = getattr(workspace, "use_description_text", None)
                if widget is not None:
                    try:
                        data["use_description"] = widget.get("1.0", "end").strip()
                    except Exception:
                        pass
                return data
            operator_module.build_live_snapshot = build_live_snapshot
            operator_module._phase49_3c_persian_snapshot_installed = True
    except Exception:
        pass

    if getattr(readiness_module, "_phase49_3c_persian_readiness_installed", False):
        return
    original_evaluate = readiness_module.evaluate_readiness
    def evaluate(row):
        state = original_evaluate(row)
        if row is None:
            return state
        def value(key):
            try:
                return row.get(key, "") if isinstance(row, dict) else row[key]
            except Exception:
                return ""
        source_title = str(value("source_title") or "").strip()
        missing = []
        for key, label, allow_source_identity in (
            ("title_fa", "عنوان فارسی", True),
            ("short_description_fa", "توضیح کوتاه فارسی", True),
            ("description_fa", "توضیح کامل فارسی", True),
            ("use_description", "توضیحات کاربرد محصول", True),
            ("seo_title_fa", "SEO Title فارسی", False),
            ("seo_description_fa", "SEO Description فارسی", False),
        ):
            current = value(key)
            valid = (
                has_persian_editorial_text_for_source(current, source_title)
                if allow_source_identity
                else has_persian_editorial_text(current)
            )
            if not valid:
                missing.append(label)
        for key, label in (("keywords_json", "کلمات کلیدی فارسی"), ("tags_fa_json", "تگ‌های فارسی"), ("hashtags_fa_json", "هشتگ‌های فارسی")):
            try:
                values = json.loads(value(key) or "[]")
            except Exception:
                values = []
            if not isinstance(values, list) or not values or any(not has_persian_editorial_text(x) for x in values):
                missing.append(label)
        try:
            selected = json.loads(value("selected_images_json") or "[]")
            alts = json.loads(value("image_alt_texts_json") or "[]")
        except Exception:
            selected, alts = [], []
        required_alt_count = min(len(selected), 10) if isinstance(selected, list) else 0
        usable_alts = list(alts) if isinstance(alts, list) else []
        if required_alt_count and (
            len(usable_alts) < required_alt_count
            or any(
                not has_persian_editorial_text_for_source(item, source_title)
                for item in usable_alts[:required_alt_count]
            )
        ):
            missing.append("Alt فارسی همه تصاویر انتخاب‌شده")
        if missing:
            content = state.setdefault("stages", {}).setdefault("content", {"label": "۴. محتوا و SEO", "missing": []})
            content["missing"] = _unique([*content.get("missing", []), *missing])
            content["ready"] = not content["missing"]
            state["missing"] = []
            for key, stage in state.get("stages", {}).items():
                for item in stage.get("missing") or []:
                    state["missing"].append(f"{stage.get('label', key)}: {item}")
            state["production_ready"] = all(bool(stage.get("ready")) for stage in state.get("stages", {}).values())
        return state
    readiness_module.evaluate_readiness = evaluate
    readiness_module._phase49_3c_persian_readiness_installed = True
