from __future__ import annotations

import json
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.parse import unquote, urlsplit

from . import phase49_3c_image_pipeline as image_pipeline
from . import phase49_3i15_bulk_discovery_images as bulk_discovery
from .openai_content import AIContentService
from .phase49_3i17_single_active_ai_runtime import active_ai_config
from .phase49_diagnostics import audit_event
from .phase49_readiness_wizard import selected_color_names, selected_material_names
from .v8_features import source_payload_hash


PHASE = "49.3I.18"
MAX_IMAGES = 20
CANONICAL_REBUILD_TIMEOUT_MS = 120_000

EDITORIAL_FIELDS = (
    "title_fa",
    "short_description_fa",
    "description_fa",
    "use_description",
    "categories_fa_json",
    "specs_fa_json",
    "tags_fa_json",
    "hashtags_fa_json",
    "keywords_json",
    "sales_bullets_json",
    "social_caption_fa",
    "image_alt_texts_json",
    "content_pack_json",
)

PROTECTED_BUSINESS_FIELDS = {
    "final_price",
    "suggested_price",
    "price_min",
    "price_max",
    "approved_for_sale",
    "commercial_status",
    "license_name",
    "license_url",
    "publish_as_product",
    "publish_as_portfolio",
    "materials_json",
    "colors_json",
    "material_color_options_json",
}


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        value = row.get(key, default)
    else:
        try:
            value = row[key]
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


def selected_image_urls(row, limit: int = MAX_IMAGES) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in _json_list(_row_value(row, "selected_images_json", "[]")):
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
        if len(output) >= max(1, min(MAX_IMAGES, int(limit or MAX_IMAGES))):
            break
    return output


def source_title_from_model_url(url: str) -> str:
    """Recover a readable source title from stable MakerWorld-style model slugs."""
    path = unquote(urlsplit(str(url or "")).path or "")
    match = re.search(r"/models/(\d+)(?:-([^/]+))?", path, flags=re.IGNORECASE)
    if not match:
        return ""
    slug = str(match.group(2) or "").strip("-_")
    if not slug:
        return ""
    words = [item for item in re.split(r"[-_]+", slug) if item]
    acronyms = {"led", "usb", "rgb", "diy", "rc", "pc", "tpu", "pla", "petg", "abs"}
    rendered = [item.upper() if item.lower() in acronyms else item.capitalize() for item in words]
    return " ".join(rendered).strip()


def is_generic_source_title(value: str, external_id: str = "") -> bool:
    text = " ".join(str(value or "").strip().split()).casefold()
    if not text:
        return True
    identity = str(external_id or "").strip().casefold()
    if identity and text in {identity, f"#{identity}"}:
        return True
    patterns = (
        r"^(makerworld\s+)?model\s*#?\s*\d+$",
        r"^makerworld\s+model\s+\d+$",
        r"^مدل\s+(?:میکرورلد|makerworld)\s*#?\s*\d+$",
        r"^محصول\s+(?:میکرورلد|makerworld)\s*#?\s*\d+$",
    )
    return any(re.fullmatch(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _safe_filename_base(value: str, fallback: str = "product-image") -> str:
    value = str(value or "").strip()
    if value.lower().endswith(".webp"):
        value = value[:-5]
    value = value.replace("{n}", "").replace("{index}", "")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return value[:88] or fallback


def _render_template(template: str, *, n: int, total: int, title: str) -> str:
    value = str(template or "")
    return (
        value.replace("{n}", str(n))
        .replace("{nn}", f"{n:02d}")
        .replace("{index}", str(n))
        .replace("{total}", str(total))
        .replace("{title}", str(title or ""))
        .strip()
    )


def _keyword_lines(value: str) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for part in re.split(r"[\n,،]+", str(value or "")):
        text = part.strip().lstrip("#")
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output[:24]


def build_batch_metadata_updates(
    row,
    metadata_items: list[dict],
    *,
    filename_base: str = "",
    alt_template: str = "",
    title_template: str = "",
    caption_template: str = "",
    keywords_text: str = "",
    apply_filename: bool = False,
    apply_alt: bool = False,
    apply_title: bool = False,
    apply_caption: bool = False,
    apply_keywords: bool = False,
) -> dict:
    """Apply operator-selected fields to every selected image without touching source/legal fields."""
    selected = selected_image_urls(row)
    if not selected:
        return {}
    existing_by_url = {
        str(item.get("source_url") or ""): dict(item)
        for item in metadata_items or []
        if isinstance(item, dict) and str(item.get("source_url") or "").strip()
    }
    untouched = [
        dict(item)
        for item in metadata_items or []
        if isinstance(item, dict) and str(item.get("source_url") or "") not in set(selected)
    ]
    canonical_title = str(_row_value(row, "title_fa", "") or _row_value(row, "source_title", "") or "محصول").strip()
    total = len(selected)
    base = _safe_filename_base(filename_base, fallback="product-image")
    keywords = _keyword_lines(keywords_text)
    merged: list[dict] = []
    alt_values: list[str] = []

    for index, url in enumerate(selected, start=1):
        item = dict(existing_by_url.get(url) or {"source_url": url})
        changed: list[str] = []
        if apply_filename:
            item["seo_filename"] = f"{base}-{index:02d}.webp"
            changed.append("seo_filename")
        if apply_alt:
            value = _render_template(alt_template, n=index, total=total, title=canonical_title)
            item["alt_text"] = value or f"{canonical_title} - نمای {index}"
            changed.append("alt_text")
        if apply_title:
            value = _render_template(title_template, n=index, total=total, title=canonical_title)
            item["title"] = value or canonical_title
            changed.append("title")
        if apply_caption:
            item["caption"] = _render_template(caption_template, n=index, total=total, title=canonical_title)
            changed.append("caption")
        if apply_keywords:
            item["keywords"] = list(keywords)
            changed.append("keywords")
        if changed:
            overrides = [str(value) for value in (item.get("operator_override_fields") or [])]
            for key in changed:
                if key not in overrides:
                    overrides.append(key)
            item["operator_override_fields"] = overrides
            item["operator_override"] = True
            item["metadata_ready"] = False
            item["seo_signature"] = ""
        merged.append(item)
        alt_values.append(str(item.get("alt_text") or "").strip())

    updates = {
        image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(untouched + merged, ensure_ascii=False),
    }
    if apply_alt:
        updates["image_alt_texts_json"] = json.dumps(alt_values, ensure_ascii=False)
    return updates


def build_canonical_rebuild_updates(pack: dict, canonical_title: str, *, provider: str, model: str) -> dict:
    """Build explicit editorial overwrite set; business/legal/publish fields are never included."""
    canonical = str(canonical_title or "").strip()
    if not canonical:
        raise ValueError("Canonical Persian title is required")
    slider = pack.get("homepage_slider_seo") if isinstance(pack.get("homepage_slider_seo"), dict) else {}
    updates = {
        "title_fa": canonical,
        "short_description_fa": str(pack.get("short_description_fa") or "").strip(),
        "description_fa": str(pack.get("description_fa") or "").strip(),
        "use_description": str(pack.get("use_description_fa") or "").strip(),
        "categories_fa_json": json.dumps(pack.get("categories_fa") or [], ensure_ascii=False),
        "specs_fa_json": json.dumps(pack.get("specs_fa") or [], ensure_ascii=False),
        "tags_fa_json": json.dumps(pack.get("tags_fa") or [], ensure_ascii=False),
        "hashtags_fa_json": json.dumps(pack.get("hashtags_fa") or [], ensure_ascii=False),
        "keywords_json": json.dumps(pack.get("target_keywords_fa") or [], ensure_ascii=False),
        "sales_bullets_json": json.dumps(pack.get("sales_bullets") or [], ensure_ascii=False),
        "social_caption_fa": str(pack.get("social_caption_fa") or "").strip(),
        "seo_title_fa": str(pack.get("seo_title_fa") or "").strip(),
        "seo_description_fa": str(pack.get("seo_description_fa") or "").strip(),
        "image_alt_texts_json": json.dumps(pack.get("image_alt_texts") or [], ensure_ascii=False),
        "content_pack_json": json.dumps(pack, ensure_ascii=False),
        "ai_provider": str(provider or "").strip(),
        "ai_model": str(model or "").strip(),
    }
    if slider:
        updates.update(
            {
                "homepage_slider_title_fa": str(slider.get("title_fa") or "").strip(),
                "homepage_slider_description_fa": str(slider.get("description_fa") or "").strip(),
                "homepage_slider_alt_text": str(slider.get("image_alt_fa") or "").strip(),
                "homepage_slider_button_text": str(slider.get("button_text_fa") or "").strip(),
                "homepage_slider_focus_keyword": str(slider.get("focus_keyword_fa") or "").strip(),
            }
        )
    if PROTECTED_BUSINESS_FIELDS.intersection(updates):
        raise AssertionError("Canonical rebuild attempted to touch protected business fields")
    return updates


def _copy(widget) -> str:
    try:
        if isinstance(widget, tk.Text):
            text = widget.get("sel.first", "sel.last")
        else:
            first = int(widget.index("sel.first"))
            last = int(widget.index("sel.last"))
            text = str(widget.get())[first:last]
    except Exception:
        return "break"
    try:
        widget.clipboard_clear()
        widget.clipboard_append(text)
        widget.update_idletasks()
    except Exception:
        pass
    return "break"


def _can_write(widget) -> bool:
    try:
        state = str(widget.cget("state") or "normal").lower()
    except Exception:
        state = "normal"
    return state not in {"disabled", "readonly"}


def _delete_selection(widget) -> None:
    try:
        if isinstance(widget, tk.Text):
            widget.delete("sel.first", "sel.last")
        else:
            widget.delete("sel.first", "sel.last")
    except Exception:
        pass


def _paste(widget) -> str:
    if not _can_write(widget):
        return "break"
    try:
        text = widget.clipboard_get()
    except Exception:
        return "break"
    try:
        _delete_selection(widget)
        if isinstance(widget, tk.Text):
            widget.insert("insert", text)
        else:
            widget.insert("insert", text)
    except Exception:
        pass
    return "break"


def _cut(widget) -> str:
    if not _can_write(widget):
        return "break"
    _copy(widget)
    _delete_selection(widget)
    return "break"


def _select_all(widget) -> str:
    try:
        if isinstance(widget, tk.Text):
            widget.tag_add("sel", "1.0", "end-1c")
            widget.mark_set("insert", "end-1c")
            widget.see("insert")
        else:
            widget.selection_range(0, "end")
            widget.icursor("end")
    except Exception:
        pass
    return "break"


def _bind_clipboard_widget(widget) -> None:
    if getattr(widget, "_phase49_3i18_clipboard_bound", False):
        return
    widget._phase49_3i18_clipboard_bound = True
    widget.bind("<Control-c>", lambda _event, w=widget: _copy(w), add=False)
    widget.bind("<Control-C>", lambda _event, w=widget: _copy(w), add=False)
    widget.bind("<Control-x>", lambda _event, w=widget: _cut(w), add=False)
    widget.bind("<Control-X>", lambda _event, w=widget: _cut(w), add=False)
    widget.bind("<Control-v>", lambda _event, w=widget: _paste(w), add=False)
    widget.bind("<Control-V>", lambda _event, w=widget: _paste(w), add=False)
    widget.bind("<Control-a>", lambda _event, w=widget: _select_all(w), add=False)
    widget.bind("<Control-A>", lambda _event, w=widget: _select_all(w), add=False)
    widget.bind("<Control-Insert>", lambda _event, w=widget: _copy(w), add=False)
    widget.bind("<Shift-Insert>", lambda _event, w=widget: _paste(w), add=False)

    def popup(event, w=widget):
        menu = tk.Menu(w, tearoff=False)
        menu.add_command(label="کپی", command=lambda: _copy(w))
        menu.add_command(label="برش", command=lambda: _cut(w), state="normal" if _can_write(w) else "disabled")
        menu.add_command(label="چسباندن", command=lambda: _paste(w), state="normal" if _can_write(w) else "disabled")
        menu.add_separator()
        menu.add_command(label="انتخاب همه", command=lambda: _select_all(w))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return "break"

    widget.bind("<Button-3>", popup, add=False)


def install_clipboard_contract() -> None:
    """Bind reliable Windows editing shortcuts to all editable widgets created afterwards."""
    classes = [tk.Entry, tk.Text, tk.Spinbox, ttk.Entry, ttk.Combobox]
    spin = getattr(ttk, "Spinbox", None)
    if spin is not None:
        classes.append(spin)
    for cls in classes:
        if getattr(cls, "_phase49_3i18_constructor_patched", False):
            continue
        original = cls.__init__

        def patched(self, *args, __original=original, **kwargs):
            __original(self, *args, **kwargs)
            _bind_clipboard_widget(self)

        cls.__init__ = patched
        cls._phase49_3i18_constructor_patched = True


def _install_bulk_source_identity_guard() -> None:
    if getattr(bulk_discovery, "_phase49_3i18_source_identity_guard", False):
        return
    original = bulk_discovery.build_product_payload

    def build_product_payload(candidate: dict, manifest: dict, source_cfg: dict | None, source_name: str) -> dict:
        data = original(candidate, manifest, source_cfg, source_name)
        current = str(data.get("source_title") or "").strip()
        recovered = source_title_from_model_url(data.get("source_url") or "")
        if recovered and is_generic_source_title(current, str(data.get("external_id") or "")):
            data["source_title"] = recovered
            data["source_hash"] = source_payload_hash(data)
        return data

    bulk_discovery.build_product_payload = build_product_payload
    bulk_discovery._phase49_3i18_source_identity_guard = True


def _metadata_defaults(self, row, selected: list[str]) -> list[dict]:
    items = [dict(item) for item in _json_list(_row_value(row, image_pipeline.IMAGE_METADATA_COLUMN, "[]")) if isinstance(item, dict)]
    by_url = {str(item.get("source_url") or ""): item for item in items}
    for index, url in enumerate(selected, start=1):
        if url in by_url:
            continue
        try:
            local = image_pipeline.strict_source_local_image(row, url)
            if local and Path(local).is_file():
                created = image_pipeline.build_image_metadata(row, url, Path(local), index, self.db)
            else:
                created = {"source_url": url}
        except Exception:
            created = {"source_url": url}
        items.append(created)
        by_url[url] = created
    return items


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i18_operator_editing_installed", False):
        return
    _install_bulk_source_identity_guard()
    original_init = workspace_class.__init__

    def __init__(self, app, product_id: int):
        self._phase49_3i18_rebuild_generation = 0
        self._phase49_3i18_rebuild_busy = False
        original_init(self, app, product_id)
        self._phase49_3i18_add_tools()

    def _phase49_3i18_add_tools(self):
        if hasattr(self, "content_tab"):
            frame = ttk.LabelFrame(
                self.content_tab,
                text="اصلاح هویت محصول و بازسازی متن / SEO",
                padding=7,
                style="Card.TLabelframe",
            )
            children = list(self.content_tab.winfo_children())
            kwargs = {"fill": "x", "pady": (0, 7)}
            if children:
                kwargs["before"] = children[0]
            frame.pack(**kwargs)
            ttk.Label(
                frame,
                text="اگر عنوان منبع یا ترجمه اشتباه است، عنوان صحیح را بده و همه متن و SEO را با همان هویت بازسازی کن.",
                style="SubHeader.TLabel",
            ).pack(side="right", padx=5)
            ttk.Button(
                frame,
                text="🧭 اصلاح هویت + بازسازی با AI",
                command=self._phase49_3i18_open_identity_rebuild,
                style="Success.TButton",
            ).pack(side="left", padx=3)
        if hasattr(self, "images_tab"):
            frame = ttk.LabelFrame(
                self.images_tab,
                text="ویرایش گروهی Metadata تصاویر",
                padding=7,
                style="Card.TLabelframe",
            )
            children = list(self.images_tab.winfo_children())
            kwargs = {"fill": "x", "pady": (0, 7)}
            if children:
                kwargs["before"] = children[0]
            frame.pack(**kwargs)
            ttk.Label(
                frame,
                text="نام فایل شماره‌دار، Alt، Title، Caption و Keywords را یک‌جا روی همه تصاویر منتخب اعمال کن.",
                style="SubHeader.TLabel",
            ).pack(side="right", padx=5)
            ttk.Button(
                frame,
                text="🧰 ویرایش گروهی همه تصاویر منتخب",
                command=self._phase49_3i18_open_batch_metadata,
                style="Primary.TButton",
            ).pack(side="left", padx=3)

    def _phase49_3i18_open_batch_metadata(self):
        row = self.db.product(self.product_id)
        selected = selected_image_urls(row)
        if not selected:
            messagebox.showwarning("3DPrintHub", "ابتدا حداقل یک تصویر را برای سایت انتخاب کن.", parent=self)
            return
        items = _metadata_defaults(self, row, selected)
        win = tk.Toplevel(self)
        win.title("ویرایش گروهی Metadata همه تصاویر منتخب")
        win.geometry("980x760")
        win.transient(self)
        outer = ttk.Frame(win, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=f"ویرایش گروهی {len(selected)} تصویر منتخب", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="فقط فیلدهایی که تیک می‌زنی تغییر می‌کنند؛ Creator، Source و License دست‌نخورده می‌مانند.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        form = ttk.Frame(outer)
        form.pack(fill="both", expand=True)
        form.columnconfigure(2, weight=1)
        title = str(_row_value(row, "title_fa", "") or _row_value(row, "source_title", "") or "محصول").strip()
        recovered = source_title_from_model_url(str(_row_value(row, "source_url", "") or ""))
        checks = {key: tk.IntVar(value=1 if key in {"filename", "alt", "title"} else 0) for key in ("filename", "alt", "title", "caption", "keywords")}
        filename_var = tk.StringVar(value=_safe_filename_base(recovered or str(_row_value(row, "source_title", "") or "product-image")))
        alt_var = tk.StringVar(value="{title} - نمای {n}")
        title_var = tk.StringVar(value="{title} - تصویر {n}")

        def add_entry(row_no: int, key: str, label: str, variable):
            ttk.Checkbutton(form, variable=checks[key]).grid(row=row_no, column=0, padx=4, pady=5, sticky="w")
            ttk.Label(form, text=label).grid(row=row_no, column=1, padx=4, pady=5, sticky="w")
            ttk.Entry(form, textvariable=variable).grid(row=row_no, column=2, padx=4, pady=5, sticky="ew")

        add_entry(0, "filename", "پایه نام فایل SEO (خروجی: -01.webp, -02.webp, ...)", filename_var)
        add_entry(1, "alt", "الگوی Alt — {title} / {n} / {nn} / {total}", alt_var)
        add_entry(2, "title", "الگوی Title تصویر", title_var)

        ttk.Checkbutton(form, variable=checks["caption"]).grid(row=3, column=0, padx=4, pady=5, sticky="nw")
        ttk.Label(form, text="Caption همه تصاویر").grid(row=3, column=1, padx=4, pady=5, sticky="nw")
        caption = tk.Text(form, height=7, wrap="word", undo=True)
        caption.grid(row=3, column=2, padx=4, pady=5, sticky="nsew")
        caption.insert("1.0", str(_row_value(row, "short_description_fa", "") or _row_value(row, "seo_description_fa", "") or ""))

        ttk.Checkbutton(form, variable=checks["keywords"]).grid(row=4, column=0, padx=4, pady=5, sticky="nw")
        ttk.Label(form, text="Keywords — هر خط یک مورد").grid(row=4, column=1, padx=4, pady=5, sticky="nw")
        keywords = tk.Text(form, height=8, wrap="word", undo=True)
        keywords.grid(row=4, column=2, padx=4, pady=5, sticky="nsew")
        keywords.insert("1.0", "\n".join(str(item) for item in _json_list(_row_value(row, "keywords_json", "[]"))))
        form.rowconfigure(3, weight=1)
        form.rowconfigure(4, weight=1)

        preview = tk.Text(outer, height=6, wrap="word", state="normal")
        preview.pack(fill="x", pady=(8, 0))
        preview.insert("1.0", f"عنوان فعلی محصول: {title}\nنمونه Alt: {title} - نمای 1\nتعداد تصاویر هدف: {len(selected)}")
        preview.configure(state="disabled")

        def apply(finalize: bool):
            current = self.db.product(self.product_id)
            updates = build_batch_metadata_updates(
                current,
                items,
                filename_base=filename_var.get(),
                alt_template=alt_var.get(),
                title_template=title_var.get(),
                caption_template=caption.get("1.0", "end").strip(),
                keywords_text=keywords.get("1.0", "end").strip(),
                apply_filename=bool(checks["filename"].get()),
                apply_alt=bool(checks["alt"].get()),
                apply_title=bool(checks["title"].get()),
                apply_caption=bool(checks["caption"].get()),
                apply_keywords=bool(checks["keywords"].get()),
            )
            if not updates:
                messagebox.showwarning("3DPrintHub", "هیچ تغییر قابل اعمالی انتخاب نشده است.", parent=win)
                return
            self.db.update_product(self.product_id, updates)
            final_error = ""
            if finalize:
                try:
                    image_pipeline.finalize_selected_images(self.db, self.product_id)
                except Exception as exc:
                    final_error = f"{type(exc).__name__}: {exc}"
            audit_event(
                "images",
                "bulk_operator_metadata",
                product_id=self.product_id,
                message=f"images={len(selected)} finalize={int(finalize)}",
                source_file="catalog_center/app/phase49_3i18_operator_editing_runtime.py",
            )
            try:
                self.reload()
                self._phase49_3e_refresh_tasks()
            except Exception:
                pass
            if final_error:
                messagebox.showwarning("3DPrintHub", f"Metadata ذخیره شد ولی نهایی‌سازی فایل‌ها کامل نشد:\n{final_error}", parent=win)
            else:
                messagebox.showinfo("3DPrintHub", "✅ تغییرات گروهی روی همه تصاویر منتخب ذخیره شد.", parent=win)

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="اعمال + نهایی‌سازی فایل‌های SEO", command=lambda: apply(True), style="Success.TButton").pack(side="right", padx=3)
        ttk.Button(footer, text="فقط اعمال Metadata", command=lambda: apply(False)).pack(side="right", padx=3)
        ttk.Button(footer, text="بستن", command=win.destroy).pack(side="right", padx=3)

    def _phase49_3i18_open_identity_rebuild(self):
        if self._phase49_3i18_rebuild_busy or getattr(self, "_phase49_3e_busy", False):
            messagebox.showinfo("3DPrintHub", "یک درخواست هوش مصنوعی در حال اجرا است. ابتدا همان عملیات را تمام یا متوقف کن.", parent=self)
            return
        row = self.db.product(self.product_id)
        if row is None:
            return
        current_source = str(_row_value(row, "source_title", "") or "").strip()
        recovered = source_title_from_model_url(str(_row_value(row, "source_url", "") or ""))
        source_default = recovered if recovered and is_generic_source_title(current_source, str(_row_value(row, "external_id", "") or "")) else current_source
        win = tk.Toplevel(self)
        win.title("اصلاح هویت محصول و بازسازی کامل متن / SEO")
        win.geometry("980x760")
        win.transient(self)
        outer = ttk.Frame(win, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="هویت صحیح محصول → بازسازی متن و SEO", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="این عملیات فقط محتوای فارسی/SEO و در صورت انتخاب Metadata متنی تصاویر را بازسازی می‌کند؛ قیمت، مجوز، تأیید فروش و Publish تغییر نمی‌کنند.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(2, 10))
        form = ttk.Frame(outer)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        source_var = tk.StringVar(value=source_default or recovered)
        fa_var = tk.StringVar(value=str(_row_value(row, "title_fa", "") or ""))
        ttk.Label(form, text="URL منبع").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        source_url_entry = ttk.Entry(form)
        source_url_entry.insert(0, str(_row_value(row, "source_url", "") or ""))
        source_url_entry.configure(state="readonly")
        source_url_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(form, text="عنوان فعلی استخراج‌شده").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        current_entry = ttk.Entry(form)
        current_entry.insert(0, current_source)
        current_entry.configure(state="readonly")
        current_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        ttk.Label(form, text="عنوان بازیابی‌شده از URL").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        recovered_entry = ttk.Entry(form)
        recovered_entry.insert(0, recovered)
        recovered_entry.configure(state="readonly")
        recovered_entry.grid(row=2, column=1, sticky="ew", padx=4, pady=4)
        ttk.Button(form, text="استفاده از عنوان URL", command=lambda: source_var.set(recovered), state="normal" if recovered else "disabled").grid(row=2, column=2, padx=4, pady=4)
        ttk.Label(form, text="عنوان صحیح منبع EN").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=source_var).grid(row=3, column=1, columnspan=2, sticky="ew", padx=4, pady=4)
        ttk.Label(form, text="عنوان فارسی قطعی اپراتور").grid(row=4, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=fa_var).grid(row=4, column=1, columnspan=2, sticky="ew", padx=4, pady=4)
        rebuild_images = tk.IntVar(value=1)
        ttk.Checkbutton(
            form,
            text="بعد از بازسازی متن، Alt / Title / Caption / Keywords همه تصاویر منتخب هم از هویت جدید بازسازی شود",
            variable=rebuild_images,
        ).grid(row=5, column=0, columnspan=3, sticky="w", padx=4, pady=8)

        detail = tk.Text(outer, height=16, wrap="word", undo=False)
        ybar = ttk.Scrollbar(outer, orient="vertical", command=detail.yview)
        detail.configure(yscrollcommand=ybar.set)
        detail.pack(side="left", fill="both", expand=True, pady=(8, 0))
        ybar.pack(side="right", fill="y", pady=(8, 0))

        def save_identity_only():
            source_title = source_var.get().strip()
            canonical = fa_var.get().strip()
            if not source_title or not canonical:
                messagebox.showwarning("3DPrintHub", "عنوان منبع صحیح و عنوان فارسی قطعی را وارد کن.", parent=win)
                return
            self.db.update_product(self.product_id, {"source_title": source_title, "title_fa": canonical})
            audit_event(
                "content",
                "operator_identity_saved",
                product_id=self.product_id,
                message=f"source_title={source_title} title_fa={canonical}",
                source_file="catalog_center/app/phase49_3i18_operator_editing_runtime.py",
            )
            try:
                self.reload()
            except Exception:
                pass
            messagebox.showinfo("3DPrintHub", "هویت صحیح ذخیره شد. برای هماهنگ‌شدن همه متن‌ها دکمه بازسازی کامل با AI را بزن.", parent=win)

        controls = ttk.Frame(outer)
        controls.pack(fill="x", side="bottom", pady=(10, 0))
        status_var = tk.StringVar(value="آماده")
        ttk.Label(controls, textvariable=status_var).pack(side="left", padx=4)
        stop_button = ttk.Button(controls, text="توقف انتظار", state="disabled")
        stop_button.pack(side="left", padx=3)
        ttk.Button(controls, text="فقط ذخیره هویت صحیح", command=save_identity_only).pack(side="right", padx=3)

        def append(text: str):
            try:
                detail.configure(state="normal")
                detail.insert("end", text + "\n")
                detail.see("end")
            except Exception:
                pass

        def set_busy(value: bool):
            self._phase49_3i18_rebuild_busy = bool(value)
            try:
                stop_button.configure(state="normal" if value else "disabled")
            except Exception:
                pass

        def stop_waiting():
            if not self._phase49_3i18_rebuild_busy:
                return
            self._phase49_3i18_rebuild_generation += 1
            set_busy(False)
            status_var.set("متوقف شد؛ پاسخ دیرهنگام اعمال نمی‌شود")
            append("STOP: اپراتور انتظار را متوقف کرد. پاسخ دیرهنگام stale است و روی محصول اعمال نمی‌شود.")

        stop_button.configure(command=stop_waiting)

        def run_rebuild():
            if self._phase49_3i18_rebuild_busy or getattr(self, "_phase49_3e_busy", False):
                messagebox.showinfo("3DPrintHub", "یک درخواست AI دیگر در حال اجرا است.", parent=win)
                return
            source_title = source_var.get().strip()
            canonical = fa_var.get().strip()
            if not source_title or not canonical:
                messagebox.showwarning("3DPrintHub", "عنوان منبع صحیح و عنوان فارسی قطعی را وارد کن.", parent=win)
                return
            try:
                provider, key, model = active_ai_config(self.app, require_key=True)
            except Exception as exc:
                messagebox.showerror("3DPrintHub", str(exc), parent=win)
                return
            current = self.db.product(self.product_id)
            try:
                source = dict(self._source_for_ai() or {})
            except Exception:
                source = {}
            source["source_title"] = source_title
            source["operator_title_fa"] = canonical
            source["selected_materials"] = selected_material_names(current)
            source["selected_colors"] = selected_color_names(current)
            categories = self.app.get_all_categories()
            images = selected_image_urls(current)
            self._phase49_3i18_rebuild_generation += 1
            generation = self._phase49_3i18_rebuild_generation
            set_busy(True)
            status_var.set(f"در حال بازسازی با {provider} / {model}")
            append("=" * 70)
            append(f"Provider: {provider}")
            append(f"Model: {model}")
            append(f"Source title: {source_title}")
            append(f"Canonical Persian title: {canonical}")
            audit_event(
                "ai",
                "canonical_identity_rebuild_start",
                product_id=self.product_id,
                message=f"provider={provider} model={model} source={source_title} canonical={canonical}",
                source_file="catalog_center/app/phase49_3i18_operator_editing_runtime.py",
            )

            def timeout():
                if generation != self._phase49_3i18_rebuild_generation or not self._phase49_3i18_rebuild_busy:
                    return
                self._phase49_3i18_rebuild_generation += 1
                set_busy(False)
                status_var.set("Timeout — محصول تغییر نکرد")
                append("TIMEOUT: 120 seconds. Result will be ignored if it arrives later.")

            self.after(CANONICAL_REBUILD_TIMEOUT_MS, timeout)

            def success(pack: dict):
                if generation != self._phase49_3i18_rebuild_generation or not self._phase49_3i18_rebuild_busy:
                    return
                set_busy(False)
                try:
                    updates = build_canonical_rebuild_updates(pack, canonical, provider=provider, model=model)
                    updates["source_title"] = source_title
                    self.db.update_product(self.product_id, updates)
                    image_error = ""
                    if bool(rebuild_images.get()):
                        refreshed = self.db.product(self.product_id)
                        selected = selected_image_urls(refreshed)
                        metadata = _metadata_defaults(self, refreshed, selected)
                        keywords_text = "\n".join(str(item) for item in (pack.get("target_keywords_fa") or []))
                        image_updates = build_batch_metadata_updates(
                            refreshed,
                            metadata,
                            alt_template="{title} - نمای {n}",
                            title_template="{title} - تصویر {n}",
                            caption_template=str(pack.get("short_description_fa") or pack.get("seo_description_fa") or ""),
                            keywords_text=keywords_text,
                            apply_alt=True,
                            apply_title=True,
                            apply_caption=True,
                            apply_keywords=True,
                        )
                        if image_updates:
                            self.db.update_product(self.product_id, image_updates)
                            try:
                                image_pipeline.finalize_selected_images(self.db, self.product_id)
                            except Exception as exc:
                                image_error = f"{type(exc).__name__}: {exc}"
                    audit_event(
                        "ai",
                        "canonical_identity_rebuild_complete",
                        product_id=self.product_id,
                        message=f"provider={provider} model={model} fields={','.join(sorted(updates))}",
                        source_file="catalog_center/app/phase49_3i18_operator_editing_runtime.py",
                    )
                    append("RESPONSE:\n" + json.dumps(pack, ensure_ascii=False, indent=2))
                    status_var.set("بازسازی کامل شد")
                    try:
                        self.reload()
                        self._phase49_3e_refresh_tasks()
                    except Exception:
                        pass
                    if image_error:
                        messagebox.showwarning("3DPrintHub", f"متن و SEO بازسازی شد؛ نهایی‌سازی فایل تصاویر نیاز به بررسی دارد:\n{image_error}", parent=win)
                    else:
                        messagebox.showinfo("3DPrintHub", "✅ هویت، متن فارسی و SEO با عنوان قطعی بازسازی شد.", parent=win)
                except Exception as exc:
                    status_var.set("خطا هنگام اعمال نتیجه")
                    append(f"APPLY ERROR: {type(exc).__name__}: {exc}")
                    messagebox.showerror("3DPrintHub", str(exc), parent=win)

            def failure(exc: Exception):
                if generation != self._phase49_3i18_rebuild_generation or not self._phase49_3i18_rebuild_busy:
                    return
                set_busy(False)
                status_var.set("AI خطا داد؛ محصول تغییر نکرد")
                append(f"ERROR: {type(exc).__name__}: {exc}")
                audit_event(
                    "ai",
                    "canonical_identity_rebuild_error",
                    product_id=self.product_id,
                    status="error",
                    level="ERROR",
                    message=f"provider={provider} model={model}: {exc}",
                    source_file="catalog_center/app/phase49_3i18_operator_editing_runtime.py",
                )
                messagebox.showerror("3DPrintHub — خطای بازسازی AI", str(exc), parent=win)

            def worker():
                try:
                    pack = AIContentService(key, model, provider, product_id=self.product_id).enrich_product(
                        source,
                        categories,
                        image_count=len(images),
                        image_urls=images,
                        mode="commerce",
                    )
                    self.after(0, lambda pack=pack: success(pack))
                except Exception as exc:
                    self.after(0, lambda exc=exc: failure(exc))

            threading.Thread(target=worker, daemon=True).start()

        ttk.Button(controls, text="✨ بازسازی کامل متن و SEO با AI", command=run_rebuild, style="Success.TButton").pack(side="right", padx=3)
        ttk.Button(controls, text="بستن", command=win.destroy).pack(side="right", padx=3)

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i18_add_tools = _phase49_3i18_add_tools
    workspace_class._phase49_3i18_open_batch_metadata = _phase49_3i18_open_batch_metadata
    workspace_class._phase49_3i18_open_identity_rebuild = _phase49_3i18_open_identity_rebuild
    workspace_class._phase49_3i18_operator_editing_installed = True
