from __future__ import annotations

import re
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.parse import unquote, urlsplit


PHASE = "49.3I.19"

_GENERIC_WORDS = {
    "model",
    "3d model",
    "makerworld model",
    "product",
    "item",
    "design",
}
_SITE_SUFFIXES = (
    " | makerworld",
    " - makerworld",
    " – makerworld",
    " — makerworld",
)
_ACRONYMS = {
    "3d": "3D",
    "stl": "STL",
    "3mf": "3MF",
    "pla": "PLA",
    "petg": "PETG",
    "abs": "ABS",
    "asa": "ASA",
    "tpu": "TPU",
    "cnc": "CNC",
    "cf": "CF",
}


def _clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    try:
        if isinstance(row, dict):
            value = row.get(key, default)
        else:
            value = row[key]
    except Exception:
        value = default
    return default if value is None else value


def _strip_site_suffix(value: str) -> str:
    text = _clean(value)
    lower = text.lower()
    for suffix in _SITE_SUFFIXES:
        if lower.endswith(suffix):
            return text[: -len(suffix)].strip()
    return text


def _external_id_from_url(url: str) -> str:
    path = unquote(urlsplit(str(url or "")).path or "")
    match = re.search(r"/models/(\d+)(?:[-/]|$)", path, re.I)
    return match.group(1) if match else ""


def _display_slug(slug: str) -> str:
    words = [part for part in re.split(r"[-_\s]+", unquote(slug or "")) if part]
    output: list[str] = []
    for word in words:
        low = word.lower()
        if low in _ACRONYMS:
            output.append(_ACRONYMS[low])
        elif re.fullmatch(r"\d+(?:\.\d+)?", word):
            output.append(word)
        else:
            output.append(word[:1].upper() + word[1:])
    return " ".join(output).strip()


def makerworld_title_from_url(url: str, external_id: str = "") -> str:
    path = unquote(urlsplit(str(url or "")).path or "")
    match = re.search(r"/models/(?P<id>\d+)(?:-(?P<slug>[^/?#]+))?", path, re.I)
    if not match:
        return ""
    model_id = match.group("id") or str(external_id or "")
    slug = _clean(match.group("slug") or "")
    if not slug or slug == model_id:
        return ""
    return _display_slug(slug)


def is_generic_source_title(title: str, external_id: str = "") -> bool:
    text = _strip_site_suffix(title)
    if not text:
        return True
    model_id = _clean(external_id)
    compact = re.sub(r"[^a-z0-9\u0600-\u06ff]+", " ", text.lower()).strip()
    if model_id and compact == model_id:
        return True
    if compact in _GENERIC_WORDS:
        return True
    if model_id:
        generic_patterns = (
            rf"^(?:makerworld\s+)?(?:model|3d\s+model|product|item|design)\s*#?\s*{re.escape(model_id)}$",
            rf"^(?:مدل|محصول)(?:\s+(?:میکرورلد|makerworld))?\s*#?\s*{re.escape(model_id)}$",
            rf"^(?:میکرورلد|makerworld)\s+(?:مدل|model)\s*#?\s*{re.escape(model_id)}$",
        )
        if any(re.fullmatch(pattern, compact, re.I) for pattern in generic_patterns):
            return True
    return False


def canonical_source_title(
    current_title: str,
    source_url: str,
    external_id: str = "",
    *,
    candidates=(),
) -> str:
    model_id = _clean(external_id) or _external_id_from_url(source_url)
    for candidate in [*list(candidates or ()), current_title]:
        cleaned = _strip_site_suffix(_clean(candidate))
        if cleaned and not is_generic_source_title(cleaned, model_id):
            return cleaned
    slug_title = makerworld_title_from_url(source_url, model_id)
    if slug_title and not is_generic_source_title(slug_title, model_id):
        return slug_title
    return _strip_site_suffix(_clean(current_title))


def canonicalize_candidate(candidate: dict) -> dict:
    output = dict(candidate or {})
    source_url = _clean(output.get("source_url"))
    external_id = _clean(output.get("external_id")) or _external_id_from_url(source_url)
    output["source_title"] = canonical_source_title(
        output.get("source_title", ""),
        source_url,
        external_id,
    )
    return output


def resolve_source_title_live(source_url: str, current_title: str = "", external_id: str = "") -> str:
    live_title = ""
    try:
        from .crawler import parse_product, public_http

        html = public_http(source_url, 20)
        parsed = parse_product(html, source_url, "", [])
        live_title = _clean(parsed.get("source_title") or "")
    except Exception:
        live_title = ""
    return canonical_source_title(
        current_title,
        source_url,
        external_id,
        candidates=(live_title,),
    )


def install_runtime() -> None:
    from . import phase49_3i15_bulk_discovery_images as bulk
    from . import phase49_3i16_resilient_acquisition as recovery
    from . import phase49_3i_discovery_review as discovery

    if getattr(bulk, "_phase49_3i19_source_identity_installed", False):
        return

    original_candidates = discovery.candidates_from_dom_rows
    original_upsert = discovery.upsert_candidate
    original_build_payload = bulk.build_product_payload

    def candidates_from_dom_rows(rows, model_pattern, discovered_from, source_code, requested):
        result = original_candidates(rows, model_pattern, discovered_from, source_code, requested)
        return [canonicalize_candidate(item) for item in result]

    def upsert_candidate(db, candidate):
        return original_upsert(db, canonicalize_candidate(candidate))

    def build_product_payload(candidate, manifest, source_row, source_name):
        cleaned_candidate = canonicalize_candidate(candidate)
        payload = original_build_payload(cleaned_candidate, manifest, source_row, source_name)
        payload["source_title"] = canonical_source_title(
            payload.get("source_title", ""),
            payload.get("source_url", ""),
            payload.get("external_id", ""),
            candidates=(manifest.get("source_title", "") if isinstance(manifest, dict) else "",),
        )
        return payload

    discovery.candidates_from_dom_rows = candidates_from_dom_rows
    recovery.candidates_from_dom_rows = candidates_from_dom_rows
    discovery.upsert_candidate = upsert_candidate
    bulk.upsert_candidate = upsert_candidate
    bulk.build_product_payload = build_product_payload
    bulk._phase49_3i19_source_identity_installed = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i19_source_identity_installed", False):
        return

    original_content_ui = workspace_class._phase49_3i18_content_ui
    original_source_for_ai = workspace_class._source_for_ai

    def _source_for_ai(self):
        source = dict(original_source_for_ai(self) or {})
        row = self.db.product(self.product_id)
        source_url = _clean(source.get("source_url") or _row_value(row, "source_url", ""))
        external_id = _clean(source.get("external_id") or _row_value(row, "external_id", ""))
        source["source_title"] = canonical_source_title(
            source.get("source_title") or _row_value(row, "source_title", ""),
            source_url,
            external_id,
        )
        return source

    def _phase49_3i18_content_ui(self):
        original_content_ui(self)
        parent = getattr(self, "content_tab", None)
        if parent is None:
            return
        row = self.db.product(self.product_id)
        source_url = _clean(_row_value(row, "source_url", ""))
        external_id = _clean(_row_value(row, "external_id", ""))
        canonical = canonical_source_title(_row_value(row, "source_title", ""), source_url, external_id)

        frame = ttk.LabelFrame(
            parent,
            text="هویت واقعی محصول در منبع — قبل از ترجمه و SEO",
            padding=8,
            style="Card.TLabelframe",
        )
        frame.pack(fill="x", pady=(0, 8))
        frame.columnconfigure(1, weight=1)
        self._phase49_3i19_source_title = tk.StringVar(value=canonical)
        ttk.Label(frame, text="عنوان واقعی منبع").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(frame, textvariable=self._phase49_3i19_source_title, state="readonly").grid(
            row=0, column=1, sticky="ew", padx=4, pady=4
        )
        ttk.Label(
            frame,
            text="اول عنوان واقعی صفحه/URL اصلاح می‌شود؛ سپس AI اجازه تولید عنوان فارسی، متن و SEO دارد.",
            style="SubHeader.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=4)
        actions = ttk.Frame(frame)
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(
            actions,
            text="↻ بازخوانی و اصلاح عنوان منبع",
            command=lambda: self._phase49_3i19_refresh_source(False),
        ).pack(side="left", padx=3)
        ttk.Button(
            actions,
            text="🌐 اصلاح عنوان منبع + بازسازی کامل AI",
            command=lambda: self._phase49_3i19_refresh_source(True),
            style="Success.TButton",
        ).pack(side="left", padx=3)

    def refresh_source(self, rebuild_ai=False):
        if bool(getattr(self, "_phase49_3i19_busy", False)) or bool(getattr(self, "_phase49_3i18_busy", False)):
            return
        row = self.db.product(self.product_id)
        source_url = _clean(_row_value(row, "source_url", ""))
        external_id = _clean(_row_value(row, "external_id", ""))
        current = _clean(_row_value(row, "source_title", ""))
        if not source_url.startswith(("http://", "https://")):
            messagebox.showwarning("3DPrintHub", "URL منبع معتبر برای بازخوانی عنوان وجود ندارد.", parent=self)
            return
        self._phase49_3i19_busy = True
        self.footer_status.set("در حال بازخوانی عنوان واقعی محصول از منبع…")

        def worker():
            try:
                title = resolve_source_title_live(source_url, current, external_id)
                if not title or is_generic_source_title(title, external_id):
                    raise RuntimeError("عنوان معتبر از صفحه یا URL محصول به دست نیامد")
                self.after(0, lambda: self._phase49_3i19_apply_source_title(title, bool(rebuild_ai)))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("خطای بازخوانی عنوان منبع", str(e), parent=self))
                self.after(0, lambda: self.footer_status.set("بازخوانی عنوان منبع ناموفق بود؛ داده قبلی حفظ شد"))
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i19_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    def apply_source_title(self, title: str, rebuild_ai=False):
        title = _clean(title)
        self.db.update_product(self.product_id, {"source_title": title})
        if hasattr(self, "title_en"):
            try:
                self.title_en.set(title)
            except Exception:
                pass
        if hasattr(self, "_phase49_3i19_source_title"):
            self._phase49_3i19_source_title.set(title)
        self.row = self.db.product(self.product_id)
        self.footer_status.set(f"عنوان واقعی منبع اصلاح شد: {title}")
        if rebuild_ai:
            self._phase49_3i19_rebuild_from_source(title)
        else:
            self.reload()

    def rebuild_from_source(self, source_title: str):
        if bool(getattr(self, "_phase49_3i18_busy", False)):
            return
        try:
            self.save(silent=True)
            provider, key, model = self._phase49_3e_provider()
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self)
            return

        from . import phase49_3c_image_pipeline as images
        from .openai_content import AIContentService
        from .phase49_readiness_wizard import selected_color_names, selected_material_names

        row = self.db.product(self.product_id)
        selected = images.cap_unique_urls(self._json_list(_row_value(row, "selected_images_json", "[]")))
        source = dict(self._source_for_ai() or {})
        source["source_title"] = source_title
        raw_description = _clean(source.get("source_description"))
        source["source_description"] = (
            f"عنوان واقعی و قطعی محصول در منبع: {source_title}\n"
            "این نام را دقیق و طبیعی به فارسی ترجمه کن. نام یا نوع کالای دیگری حدس نزن و از عنوان‌های عمومی مبتنی بر شماره مدل استفاده نکن.\n\n"
            f"{raw_description}"
        ).strip()
        source["selected_materials"] = selected_material_names(row)
        source["selected_colors"] = selected_color_names(row)
        categories = self.app.get_all_categories()
        external_id = _clean(_row_value(row, "external_id", ""))
        self._phase49_3i18_busy = True
        self.footer_status.set("عنوان منبع اصلاح شد؛ در حال بازسازی کامل متن و SEO با AI…")

        def worker():
            try:
                pack = AIContentService(
                    key,
                    model,
                    provider,
                    product_id=self.product_id,
                ).enrich_product(
                    source,
                    categories,
                    image_count=len(selected),
                    image_urls=selected,
                    mode="commerce",
                )
                persian_title = _clean(pack.get("title_fa") or "")
                if not persian_title or is_generic_source_title(persian_title, external_id):
                    raise RuntimeError("AI عنوان فارسی معتبر برای محصول برنگرداند")
                self.after(0, lambda: self._phase49_3i18_apply_ai(pack, persian_title))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("خطای بازسازی AI", str(e), parent=self))
                self.after(0, lambda: self.footer_status.set("بازسازی AI ناموفق بود؛ عنوان منبع اصلاح‌شده حفظ شد"))
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i18_busy", False))

        threading.Thread(target=worker, daemon=True).start()

    workspace_class._source_for_ai = _source_for_ai
    workspace_class._phase49_3i18_content_ui = _phase49_3i18_content_ui
    workspace_class._phase49_3i19_refresh_source = refresh_source
    workspace_class._phase49_3i19_apply_source_title = apply_source_title
    workspace_class._phase49_3i19_rebuild_from_source = rebuild_from_source
    workspace_class._phase49_3i19_source_identity_installed = True
