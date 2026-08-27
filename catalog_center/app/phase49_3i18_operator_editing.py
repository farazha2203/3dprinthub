from __future__ import annotations

import json
import re
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from . import phase49_3c_image_pipeline as images
from . import ux87_shell
from .openai_content import AIContentService
from .phase49_readiness_wizard import selected_color_names, selected_material_names

TEXT_FIELDS = (
    "short_description_fa", "description_fa", "use_description", "seo_title_fa",
    "seo_description_fa", "social_caption_fa", "technical_summary_fa",
    "homepage_slider_title_fa", "homepage_slider_description_fa",
    "homepage_slider_alt_text", "homepage_slider_focus_keyword",
)
JSON_FIELDS = (
    "categories_fa_json", "specs_fa_json", "tags_fa_json", "hashtags_fa_json",
    "keywords_json", "sales_bullets_json", "image_alt_texts_json",
)


def _v(row, key, default=""):
    try:
        value = row.get(key, default) if isinstance(row, dict) else row[key]
    except Exception:
        value = default
    return default if value is None else value


def _list(value):
    if isinstance(value, list):
        return list(value)
    try:
        value = json.loads(value or "[]")
    except Exception:
        return []
    return list(value) if isinstance(value, list) else []


def _obj(value):
    if isinstance(value, dict):
        return dict(value)
    try:
        value = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(value) if isinstance(value, dict) else {}


def _replace(value, olds, new):
    if isinstance(value, str):
        for old in sorted({str(x or "").strip() for x in olds if str(x or "").strip()}, key=len, reverse=True):
            if old != new:
                value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [_replace(x, olds, new) for x in value]
    if isinstance(value, dict):
        return {k: _replace(x, olds, new) for k, x in value.items()}
    return value


def _template(value, title, n, total):
    return (str(value or "{title} - تصویر {n}")
            .replace("{title}", title).replace("{n2}", f"{n:02d}")
            .replace("{n}", str(n)).replace("{total}", str(total))).strip()


def _slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")[:90]


# ---------- global Windows/Persian-layout clipboard ----------
def _text_widget(w):
    return isinstance(w, (tk.Entry, tk.Text, tk.Spinbox, ttk.Entry, ttk.Combobox, ttk.Spinbox))


def _state(w):
    try:
        return str(w.cget("state") or "normal").lower()
    except Exception:
        return "normal"


def _selected(w):
    if isinstance(w, tk.Text):
        try: return w.get("sel.first", "sel.last")
        except tk.TclError: return ""
    try:
        if w.selection_present():
            text = str(w.get()); return text[int(w.index("sel.first")):int(w.index("sel.last"))]
    except Exception:
        pass
    return ""


def _delete_selection(w):
    try:
        if isinstance(w, tk.Text): w.delete("sel.first", "sel.last")
        elif w.selection_present(): w.delete("sel.first", "sel.last")
    except Exception:
        pass


def _edit(root, w, action):
    if not _text_widget(w): return None
    if action in {"paste", "cut"} and _state(w) in {"disabled", "readonly"}: return None
    if action == "copy":
        value = _selected(w)
        if value: root.clipboard_clear(); root.clipboard_append(value)
    elif action == "cut":
        value = _selected(w)
        if value: root.clipboard_clear(); root.clipboard_append(value); _delete_selection(w)
    elif action == "paste":
        try: value = root.clipboard_get()
        except Exception: return "break"
        _delete_selection(w)
        try: w.insert("insert", value)
        except Exception: return None
    elif action == "all":
        if isinstance(w, tk.Text): w.tag_add("sel", "1.0", "end-1c"); w.mark_set("insert", "end-1c")
        else:
            try: w.selection_range(0, tk.END); w.icursor(tk.END)
            except Exception: return None
    return "break"


def install_clipboard(root):
    if getattr(root, "_phase49_3i18_clipboard", False): return
    actions = {"c":"copy", "v":"paste", "x":"cut", "a":"all"}
    for cls in ("Entry", "TEntry", "Text", "Spinbox", "TSpinbox", "TCombobox"):
        for key, action in actions.items():
            root.bind_class(cls, f"<Control-{key}>", lambda e, a=action: _edit(root, e.widget, a))
            root.bind_class(cls, f"<Control-{key.upper()}>", lambda e, a=action: _edit(root, e.widget, a))
        root.bind_class(cls, "<Shift-Insert>", lambda e: _edit(root, e.widget, "paste"))
        root.bind_class(cls, "<Control-Insert>", lambda e: _edit(root, e.widget, "copy"))
    # Windows physical keycodes also work when the active keyboard layout is Persian.
    keycodes = {65:"all", 67:"copy", 86:"paste", 88:"cut"}
    def physical(e):
        a = actions.get(str(getattr(e, "keysym", "")).lower()) or keycodes.get(int(getattr(e, "keycode", 0) or 0))
        return _edit(root, e.widget, a) if a and _text_widget(e.widget) else None
    root.bind_all("<Control-KeyPress>", physical, add="+")
    root._phase49_3i18_clipboard = True


def _bridge_shell():
    if getattr(ux87_shell, "_phase49_3i18_clipboard_bridge", False): return
    old_builder = ux87_shell.build_app_class
    def build_app_class(BaseApp):
        App87 = old_builder(BaseApp)
        if not getattr(App87, "_phase49_3i18_clipboard_class", False):
            old_ui = App87._ui
            def _ui(self):
                result = old_ui(self); install_clipboard(self); return result
            App87._ui = _ui; App87._phase49_3i18_clipboard_class = True
        return App87
    ux87_shell.build_app_class = build_app_class
    ux87_shell._phase49_3i18_clipboard_bridge = True


# ---------- title / AI helpers ----------
def authoritative_updates(row, new_title):
    pack = _obj(_v(row, "content_pack_json", "{}"))
    olds = [str(_v(row, "title_fa", "") or "").strip(), str(pack.get("title_fa") or "").strip()]
    out = {"title_fa": new_title}
    for key in TEXT_FIELDS:
        if _v(row, key, ""): out[key] = _replace(str(_v(row, key, "")), olds, new_title)
    for key in JSON_FIELDS:
        try: parsed = json.loads(_v(row, key, "[]") or "[]")
        except Exception: continue
        out[key] = json.dumps(_replace(parsed, olds, new_title), ensure_ascii=False)
    if pack: out["content_pack_json"] = json.dumps(_replace(pack, olds, new_title), ensure_ascii=False)
    meta = _list(_v(row, images.IMAGE_METADATA_COLUMN, "[]"))
    if meta:
        for item in meta:
            if not isinstance(item, dict): continue
            for key in ("alt_text", "title", "caption", "keywords"):
                if key in item: item[key] = _replace(item[key], olds, new_title)
            item["metadata_ready"] = False; item["seo_signature"] = ""
        out[images.IMAGE_METADATA_COLUMN] = json.dumps(meta, ensure_ascii=False)
    return out


def ai_updates(row, pack, title):
    old_ai = str(pack.get("title_fa") or "").strip()
    pack = _replace(pack, [old_ai, str(_v(row, "title_fa", "") or "").strip()], title)
    pack["title_fa"] = title
    jl = lambda key: json.dumps(pack.get(key) if isinstance(pack.get(key), list) else [], ensure_ascii=False)
    out = {
        "title_fa": title,
        "short_description_fa": str(pack.get("short_description_fa") or "").strip(),
        "description_fa": str(pack.get("description_fa") or "").strip(),
        "use_description": str(pack.get("use_description_fa") or "").strip(),
        "categories_fa_json": jl("categories_fa"), "specs_fa_json": jl("specs_fa"),
        "tags_fa_json": jl("tags_fa"), "hashtags_fa_json": jl("hashtags_fa"),
        "keywords_json": jl("target_keywords_fa"), "sales_bullets_json": jl("sales_bullets"),
        "image_alt_texts_json": jl("image_alt_texts"),
        "seo_title_fa": str(pack.get("seo_title_fa") or title).strip(),
        "seo_description_fa": str(pack.get("seo_description_fa") or "").strip(),
        "social_caption_fa": str(pack.get("social_caption_fa") or "").strip(),
        "content_pack_json": json.dumps(pack, ensure_ascii=False),
    }
    slider = pack.get("homepage_slider_seo") if isinstance(pack.get("homepage_slider_seo"), dict) else {}
    if bool(int(_v(row, "homepage_slider_enabled", 0) or 0)) and slider:
        out.update({
            "homepage_slider_title_fa": str(slider.get("title_fa") or title).strip(),
            "homepage_slider_description_fa": str(slider.get("description_fa") or "").strip(),
            "homepage_slider_alt_text": str(slider.get("image_alt_fa") or "").strip(),
            "homepage_slider_button_text": str(slider.get("button_text_fa") or "").strip(),
            "homepage_slider_focus_keyword": str(slider.get("focus_keyword_fa") or "").strip(),
        })
    return out


# ---------- additive workspace layer ----------
def install(workspace_class):
    _bridge_shell()
    if getattr(workspace_class, "_phase49_3i18_operator_editing", False): return
    old_init, old_reload = workspace_class.__init__, workspace_class.reload

    def __init__(self, app, product_id):
        self._phase49_3i18_busy = False
        old_init(self, app, product_id); install_clipboard(app)
        self._phase49_3i18_image_ui(); self._phase49_3i18_content_ui()

    def reload(self):
        result = old_reload(self)
        var = getattr(self, "_phase49_3i18_title", None)
        if var is not None and not var.get().strip(): var.set(str(_v(self.db.product(self.product_id), "title_fa", "") or ""))
        return result

    def image_ui(self):
        p = getattr(self, "images_tab", None)
        if p is None: return
        f = ttk.LabelFrame(p, text="عملیات گروهی همه تصاویر منتخب سایت", padding=8, style="Card.TLabelframe"); f.pack(fill="x", pady=(0,8))
        f.columnconfigure(1, weight=1); f.columnconfigure(3, weight=1)
        self._phase49_3i18_prefix=tk.StringVar(); self._phase49_3i18_img_title=tk.StringVar(value="{title} - تصویر {n}")
        self._phase49_3i18_alt=tk.StringVar(value="{title} - تصویر {n}"); self._phase49_3i18_caption=tk.StringVar()
        for r, c, label, var in ((0,0,"پیشوند نام فایل SEO (لاتین)",self._phase49_3i18_prefix),(0,2,"قالب Title تصاویر",self._phase49_3i18_img_title),(1,0,"قالب Alt تصاویر",self._phase49_3i18_alt),(1,2,"Caption گروهی (اختیاری)",self._phase49_3i18_caption)):
            ttk.Label(f,text=label).grid(row=r,column=c,sticky="w",padx=4,pady=3); ttk.Entry(f,textvariable=var).grid(row=r,column=c+1,sticky="ew",padx=4,pady=3)
        ttk.Label(f,text="قالب‌ها: {title}  {n}  {n2}  {total} — مثال filename: cake-stand → cake-stand-01.webp",style="SubHeader.TLabel").grid(row=2,column=0,columnspan=4,sticky="w",padx=4)
        a=ttk.Frame(f); a.grid(row=3,column=0,columnspan=4,sticky="ew",pady=(5,0))
        ttk.Button(a,text="اعمال گروهی",command=lambda:self._phase49_3i18_bulk(False)).pack(side="left",padx=3)
        ttk.Button(a,text="اعمال + بازسازی فایل‌های SEO",command=lambda:self._phase49_3i18_bulk(True),style="Success.TButton").pack(side="left",padx=3)

    def bulk(self, finalize=False):
        row=self.db.product(self.product_id); selected=images.cap_unique_urls(_list(_v(row,"selected_images_json","[]")))
        if not selected: messagebox.showwarning("3DPrintHub","ابتدا تصاویر سایت را انتخاب کن.",parent=self); return
        title=str(_v(row,"title_fa","") or "محصول چاپ سه‌بعدی").strip(); prefix=_slug(self._phase49_3i18_prefix.get())
        current=_list(_v(row,images.IMAGE_METADATA_COLUMN,"[]")); by={str(x.get("source_url") or ""):dict(x) for x in current if isinstance(x,dict)}
        meta=[]; alts=[]
        for n,url in enumerate(selected,1):
            x=by.get(url,{"source_url":url}); alt=_template(self._phase49_3i18_alt.get(),title,n,len(selected)); alts.append(alt)
            x["alt_text"]=alt; x["title"]=_template(self._phase49_3i18_img_title.get(),title,n,len(selected))
            if self._phase49_3i18_caption.get().strip(): x["caption"]=_template(self._phase49_3i18_caption.get(),title,n,len(selected))
            if prefix: x["seo_filename"]=f"{prefix}-{n:02d}.webp"
            elif not x.get("seo_filename"): x["seo_filename"]=images.planned_seo_filename(row,n)
            fields=set(x.get("operator_override_fields") or []); fields.update({"alt_text","title"}); fields.update({"seo_filename"} if prefix else set()); fields.update({"caption"} if self._phase49_3i18_caption.get().strip() else set())
            x.update(operator_override=True,operator_override_fields=sorted(fields),metadata_ready=False,seo_signature=""); meta.append(x)
        self.db.update_product(self.product_id,{"image_alt_texts_json":json.dumps(alts,ensure_ascii=False),images.IMAGE_METADATA_COLUMN:json.dumps(meta,ensure_ascii=False)})
        if finalize:
            try: images.finalize_selected_images(self.db,self.product_id)
            except Exception as exc: messagebox.showerror("3DPrintHub",f"متادیتا ذخیره شد ولی ساخت فایل SEO خطا داد:\n{exc}",parent=self)
        self.reload(); getattr(self,"_phase49_3e_refresh_tasks",lambda:None)(); self.footer_status.set(f"عملیات گروهی روی {len(selected)} تصویر اعمال شد")

    def content_ui(self):
        p=getattr(self,"content_tab",None)
        if p is None:return
        f=ttk.LabelFrame(p,text="اصلاح نام محصول و بازسازی متن / SEO",padding=8,style="Card.TLabelframe"); f.pack(fill="x",pady=(0,8)); f.columnconfigure(1,weight=1)
        self._phase49_3i18_title=tk.StringVar(value=str(_v(self.db.product(self.product_id),"title_fa","") or ""))
        ttk.Label(f,text="نام فارسی صحیح و تأییدشده اپراتور").grid(row=0,column=0,sticky="w",padx=4,pady=4); ttk.Entry(f,textvariable=self._phase49_3i18_title).grid(row=0,column=1,sticky="ew",padx=4,pady=4)
        ttk.Label(f,text="این نام مرجع نهایی است؛ Source/URL/قیمت/موجودی و انتخاب‌های تجاری تغییر نمی‌کنند.",style="SubHeader.TLabel").grid(row=1,column=0,columnspan=2,sticky="w",padx=4)
        a=ttk.Frame(f); a.grid(row=2,column=0,columnspan=2,sticky="ew",pady=(5,0)); ttk.Button(a,text="جایگزینی نام در همه متن‌ها",command=self._phase49_3i18_replace).pack(side="left",padx=3); ttk.Button(a,text="✨ بازسازی کامل متن + SEO با AI",command=self._phase49_3i18_rebuild,style="Success.TButton").pack(side="left",padx=3)

    def replace_title(self):
        title=self._phase49_3i18_title.get().strip(); row=self.db.product(self.product_id); old=str(_v(row,"title_fa","") or "")
        if not title: messagebox.showwarning("3DPrintHub","نام فارسی صحیح را وارد کن.",parent=self); return
        if old==title: self.footer_status.set("نام فارسی همین حالا همین مقدار است"); return
        if not messagebox.askyesno("3DPrintHub — اصلاح نام",f"«{old or 'بدون نام'}» در متن‌ها و SEO با «{title}» جایگزین شود؟\nداده خام منبع دست‌نخورده می‌ماند.",parent=self): return
        self.db.update_product(self.product_id,authoritative_updates(row,title)); self.reload(); getattr(self,"_phase49_3e_refresh_tasks",lambda:None)(); self.footer_status.set("نام صحیح در متن‌ها، SEO و Metadata متنی تصاویر جایگزین شد")

    def rebuild(self):
        if self._phase49_3i18_busy:return
        title=self._phase49_3i18_title.get().strip()
        if not title: messagebox.showwarning("3DPrintHub","ابتدا نام فارسی صحیح را وارد کن.",parent=self); return
        if not messagebox.askyesno("3DPrintHub — بازسازی کامل AI","متن فارسی، SEO و Alt تصاویر از نو ساخته شوند؟\nنام واردشده مرجع قطعی است؛ Source/URL/قیمت/موجودی/متریال و رنگ تغییر نمی‌کنند.",parent=self):return
        try:provider,key,model=self._phase49_3e_provider()
        except Exception as exc:messagebox.showerror("3DPrintHub",str(exc),parent=self);return
        row=self.db.product(self.product_id); selected=images.cap_unique_urls(_list(_v(row,"selected_images_json","[]"))); source=dict(self._source_for_ai() or {})
        raw_title=str(source.get("source_title") or ""); raw_desc=str(source.get("source_description") or "")
        source["source_title"]=title; source["source_description"]=(f"نام فارسی صحیح و قطعی اپراتور: {title}\nعنوان خام منبع (ممکن است اشتباه باشد): {raw_title}\n\n{raw_desc}").strip(); source["selected_materials"]=selected_material_names(row); source["selected_colors"]=selected_color_names(row)
        cats=self.app.get_all_categories(); self._phase49_3i18_busy=True; self.footer_status.set("در حال بازسازی متن و SEO با نام صحیح…")
        def worker():
            try:
                pack=AIContentService(key,model,provider,product_id=self.product_id).enrich_product(source,cats,image_count=len(selected),image_urls=selected,mode="commerce")
                self.after(0,lambda:self._phase49_3i18_apply_ai(pack,title))
            except Exception as exc:self.after(0,lambda e=exc:messagebox.showerror("خطای بازسازی AI",str(e),parent=self));self.after(0,lambda:self.footer_status.set("بازسازی AI ناموفق بود؛ داده قبلی حفظ شد"))
            finally:self.after(0,lambda:setattr(self,"_phase49_3i18_busy",False))
        threading.Thread(target=worker,daemon=True).start()

    def apply_ai(self,pack,title):
        row=self.db.product(self.product_id); updates=ai_updates(row,pack,title)
        from .phase49_3i36_stage_finalization import filter_ai_updates
        updates,_blocked=filter_ai_updates(row,updates)
        selected=images.cap_unique_urls(_list(_v(row,"selected_images_json","[]"))); alts=_list(updates.get("image_alt_texts_json","[]")); kws=_list(updates.get("keywords_json","[]")); by={str(x.get("source_url") or ""):dict(x) for x in _list(_v(row,images.IMAGE_METADATA_COLUMN,"[]")) if isinstance(x,dict)}; meta=[]
        caption=str(updates.get("short_description_fa") or updates.get("seo_description_fa") or "")
        for n,url in enumerate(selected,1):
            x=by.get(url,{"source_url":url}); x.update(alt_text=str(alts[n-1] if n-1<len(alts) else f"{title} - تصویر {n}"),title=title,caption=caption,keywords=kws[:16],operator_override=True,metadata_ready=False,seo_signature=""); fields=set(x.get("operator_override_fields") or []); fields.update({"alt_text","title","caption","keywords"}); x["operator_override_fields"]=sorted(fields); meta.append(x)
        if meta:updates[images.IMAGE_METADATA_COLUMN]=json.dumps(meta,ensure_ascii=False)
        self.db.update_product(self.product_id,updates)
        if selected:
            try:images.finalize_selected_images(self.db,self.product_id)
            except Exception as exc:messagebox.showwarning("3DPrintHub",f"متن و SEO بازسازی شد ولی فایل تصویر کامل نشد:\n{exc}",parent=self)
        self.reload();self._phase49_3i18_title.set(title);getattr(self,"_phase49_3e_refresh_tasks",lambda:None)();self.footer_status.set("بازسازی کامل متن، SEO و Alt تصاویر با نام صحیح انجام شد")

    workspace_class.__init__=__init__; workspace_class.reload=reload
    workspace_class._phase49_3i18_image_ui=image_ui; workspace_class._phase49_3i18_bulk=bulk
    workspace_class._phase49_3i18_content_ui=content_ui; workspace_class._phase49_3i18_replace=replace_title
    workspace_class._phase49_3i18_rebuild=rebuild; workspace_class._phase49_3i18_apply_ai=apply_ai
    workspace_class._phase49_3i18_operator_editing=True
