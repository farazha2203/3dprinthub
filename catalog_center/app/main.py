from __future__ import annotations
import asyncio, io, json, os, queue, shutil, threading, time, tkinter as tk, re, webbrowser
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from urllib import request as urllib_request
from PIL import Image, ImageChops, ImageTk
from .db import Database, normalize_url, utc_now
from .crawler import (public_http, extract_links, parse_product, BlockedError, respectful_delay, BrowserSession, download_public_file)
from .translators import google_translate, openai_translate
from .page_extractor import extract_direct_link, detect_source_code, detect_external_id
from .openai_content import AIContentService, OpenAIContentService
from .secure_secrets import (
    delete_provider_key, delete_secret, get_provider_key, get_secret,
    migrate_legacy_key_to_keyring, provider_key_source, secret_source,
    set_provider_key, set_secret,
)
from .runtime_logging import close_logging, configure_logging, redact
from .site_connection import SiteConnection, get_batch_diagnostic, import_batch, test_bridge, test_ftp, upload_batch
from .batch_packaging import (
    BatchImagePackagingError, copy_images_into_model,
    materialize_selected_images, validate_batch_package,
)
from .v8_features import (
    ack_item_confirms_publish, commercial_license_allows_publish, diff_summary,
    merge_refetch, new_batch_uuid, parse_ack_lines, product_diff,
    product_fingerprint, source_payload_hash,
)
from .workflow import STATUS_LABELS, image_count, product_state, pricing_suggestion, should_mark_needs_update
from .product_studio import ProductStudio
from .phase49_ui import receipt_lines
from .classic_methods import (
    discover_classic,
    collect_classic_exact,
    collect_attached_chrome,
    import_saved_html,
)
from .version import APP_TITLE, APP_VERSION, BUILD_ID
from .env_settings import ENV_FILE, env_source, env_value

APP=APP_TITLE
ROOT=Path(r"D:\projects")
DATA=ROOT/"3dprinthub-catalog-manager"
DB_FILE=DATA/"catalog.sqlite3"
CONFIG_FILE=DATA/"config.json"
PROFILE_ROOT=DATA/"browser_profiles"
HOST_MIRROR=Path(env_value("CATALOG_HOST_MIRROR", str(ROOT/"3dprinthub-houst")))
BATCH_ROOT=HOST_MIRROR/"imports"/"desktop_catalog"/"pending"
ASSET_ROOT=Path(__file__).resolve().parents[1]/"assets"
BRIDGE_TOKEN_ENV_NAME="CATALOG_BRIDGE_TOKEN"

def normalize_bridge_token_input(raw_value):
    """Return only the Bridge token from a token value or a copied .env line."""
    value=(raw_value or "").strip().lstrip("\ufeff")
    if not value:return ""
    lines=[line.strip() for line in value.splitlines() if line.strip()]
    for line in lines:
        match=re.fullmatch(
            rf"(?:export\s+)?{re.escape(BRIDGE_TOKEN_ENV_NAME)}\s*=\s*(.*)",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            value=match.group(1).strip()
            break
    else:
        if len(lines)!=1:return ""
        value=lines[0]
    if len(value)>=2 and value[0]==value[-1] and value[0] in {"'",'"'}:
        value=value[1:-1].strip()
    return value

def load_config():
    DATA.mkdir(parents=True,exist_ok=True)
    example=Path(__file__).resolve().parents[1]/"config.example.json"
    latest=json.loads(example.read_text(encoding="utf-8"))
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps(latest,ensure_ascii=False,indent=2),
            encoding="utf-8",
        )
        return latest

    current=json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    current_sources={
        item.get("code"): item
        for item in current.get("sources",[])
        if item.get("code")
    }
    merged_sources=[]
    for latest_source in latest.get("sources",[]):
        code=latest_source["code"]
        previous=current_sources.get(code,{})
        merged={**latest_source,**previous}
        merged_sources.append(merged)
    current={**latest,**current,"sources":merged_sources}
    CONFIG_FILE.write_text(
        json.dumps(current,ensure_ascii=False,indent=2),
        encoding="utf-8",
    )
    return current

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP} • BUILD {BUILD_ID}"); self.geometry("1580x920"); self.minsize(1200,720)
        self._brand_icon=None; self._brand_logo=None
        self._load_branding()
        self.db=Database(DB_FILE); self.config=load_config(); self.DATA=DATA
        self.logger,self.log_path=configure_logging(DATA,debug=os.getenv("CATALOG_DEBUG","0") == "1")
        self.logger.info("APP_START version=%s build=%s db=%s source=%s", APP_VERSION, BUILD_ID, DB_FILE, Path(__file__).resolve())
        for src in self.config["sources"]: self.db.upsert_source(src)
        self.events=queue.Queue(); self.current_product=None
        self.category_label_to_slug={}
        self.category_slug_to_label={}
        self.refresh_category_maps()
        self._style(); self._ui(); self.refresh_all()
        self.protocol("WM_DELETE_WINDOW",self.on_close)
        self.after(250,self.poll)

    def _load_branding(self):
        """Load the supplied brand anchors without making startup depend on them."""
        def trim_white(image, padding=10):
            rgb=image.convert("RGB")
            difference=ImageChops.difference(rgb,Image.new("RGB",rgb.size,"white")).convert("L")
            mask=difference.point(lambda value:255 if value>18 else 0)
            bbox=mask.getbbox()
            if bbox is None:return image
            left=max(0,bbox[0]-padding);top=max(0,bbox[1]-padding)
            right=min(image.width,bbox[2]+padding);bottom=min(image.height,bbox[3]+padding)
            return image.crop((left,top,right,bottom))
        try:
            icon=trim_white(Image.open(ASSET_ROOT/"brand_icon.png").convert("RGBA"),18)
            icon.thumbnail((96,96),Image.Resampling.LANCZOS)
            self._brand_icon=ImageTk.PhotoImage(icon)
            tk.Tk.iconphoto(self,True,self._brand_icon)
        except Exception:
            self._brand_icon=None
        try:
            logo=trim_white(Image.open(ASSET_ROOT/"brand_logo_horizontal.png").convert("RGBA"),14)
            logo.thumbnail((430,90),Image.Resampling.LANCZOS)
            self._brand_logo=ImageTk.PhotoImage(logo)
        except Exception:
            self._brand_logo=None

    def on_close(self):
        if getattr(self,"_is_closing",False):
            return
        self._is_closing=True
        try:
            try:self.logger.info("APP_STOP version=%s build=%s",APP_VERSION,BUILD_ID)
            except Exception:pass
            try:self.db.close()
            except Exception:pass
        finally:
            try:close_logging(self.logger)
            finally:self.destroy()

    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        detail="".join(traceback.format_exception(exc_type,exc_value,exc_traceback))
        self.logger.error("TK_CALLBACK_EXCEPTION\n%s",redact(detail))
        messagebox.showerror(APP,f"خطای داخلی برنامه:\n{exc_type.__name__}: {exc_value}\n\nجزئیات در:\n{self.log_path}")

    def _style(self):
        # v8.5.4 uses the official navy/gold brand while keeping dense work areas neutral.
        self.configure(bg="#f2f5f8")
        st=ttk.Style(self)
        try: st.theme_use("clam")
        except Exception: pass
        bg="#f2f5f8"; panel="#ffffff"; panel2="#e8eef4"; fg="#102a43"; muted="#5b7083"; accent="#c99a2e"
        st.configure(".",font=("Tahoma",10),background=bg,foreground=fg)
        st.configure("TFrame",background=bg)
        st.configure("Card.TFrame",background=panel)
        st.configure("TLabel",background=bg,foreground=fg)
        st.configure("Header.TLabel",font=("Tahoma",19,"bold"),background=bg,foreground="#071827")
        st.configure("SubHeader.TLabel",font=("Tahoma",10),background=bg,foreground=muted)
        st.configure("Card.TLabelframe",background=panel,foreground=fg,borderwidth=1,relief="solid")
        st.configure("Card.TLabelframe.Label",background=panel,foreground="#8a6108",font=("Tahoma",10,"bold"))
        # Phase 44: calmer controls. Green is reserved for active/publish state.
        st.configure("TNotebook",background=bg,borderwidth=0)
        st.configure("TNotebook.Tab",padding=(16,9),background="#f8fafc",foreground=fg,font=("Tahoma",10,"bold"),borderwidth=0)
        st.map("TNotebook.Tab",background=[("selected","#ffffff"),("active","#f1f5f9")],foreground=[("selected","#15803d"),("active","#0f5132")])
        st.configure("TButton",padding=(10,7),background="#ffffff",foreground=fg,borderwidth=1,relief="flat")
        st.map("TButton",background=[("active","#f1f5f9"),("pressed","#e2e8f0")])
        st.configure("Primary.TButton",padding=(11,7),background="#eef4f8",foreground="#0f2740",font=("Tahoma",10,"bold"),borderwidth=1)
        st.map("Primary.TButton",background=[("active","#e2ebf1"),("pressed","#d8e4eb")])
        st.configure("Success.TButton",padding=(11,7),background="#f0fdf4",foreground="#166534",font=("Tahoma",10,"bold"),borderwidth=1)
        st.map("Success.TButton",background=[("active","#dcfce7"),("pressed","#bbf7d0")])
        st.configure("Publish.TButton",padding=(13,8),background="#16a34a",foreground="#ffffff",font=("Tahoma",10,"bold"),borderwidth=0)
        st.map("Publish.TButton",background=[("active","#15803d"),("pressed","#166534")])
        st.configure("Warning.TButton",padding=(11,7),background="#fffbeb",foreground="#92400e",font=("Tahoma",10,"bold"),borderwidth=1)
        st.map("Warning.TButton",background=[("active","#fef3c7")])
        st.configure("Danger.TButton",padding=(11,7),background="#fff1f2",foreground="#b91c1c",font=("Tahoma",10,"bold"),borderwidth=1)
        st.map("Danger.TButton",background=[("active","#ffe4e6")])
        st.configure("Treeview",rowheight=36,background=panel,fieldbackground=panel,foreground=fg,borderwidth=0)
        st.configure("Treeview.Heading",font=("Tahoma",9,"bold"),background="#e8eef4",foreground="#102a43",padding=7)
        st.map("Treeview",background=[("selected","#f8e8b9")],foreground=[("selected","#071827")])
        st.configure("TEntry",fieldbackground="#ffffff",foreground="#111827",insertcolor="#111827")
        st.configure("TCombobox",fieldbackground="#ffffff",foreground="#111827")
        st.configure("TCheckbutton",background=bg,foreground=fg)
        st.configure("Status.TLabel",background="#071827",foreground="#f6d77a",padding=7)
        for name,bgcolor,fgcolor in [
            ("BlueCard","#dbeafe","#1e40af"),("YellowCard","#fef3c7","#92400e"),
            ("GreenCard","#dcfce7","#166534"),("OrangeCard","#ffedd5","#9a3412"),
            ("RedCard","#fee2e2","#991b1b"),("PurpleCard","#f3e8ff","#6b21a8")]:
            st.configure(name+".TFrame",background=bgcolor)
            st.configure(name+".TLabel",background=bgcolor,foreground=fgcolor,font=("Tahoma",11,"bold"))
            st.configure(name+"Count.TLabel",background=bgcolor,foreground=fgcolor,font=("Tahoma",18,"bold"))

    def _ui(self):
        header=tk.Frame(self,bg="#071827",padx=18,pady=11,highlightbackground="#c99a2e",highlightthickness=0)
        header.pack(fill="x")
        if self._brand_logo is not None:
            logo_panel=tk.Frame(header,bg="white",padx=12,pady=6,highlightbackground="#c99a2e",highlightthickness=1)
            logo_panel.pack(side="left",padx=(0,16))
            tk.Label(logo_panel,image=self._brand_logo,bg="white",borderwidth=0,highlightthickness=0).pack()
        title_box=tk.Frame(header,bg="#071827"); title_box.pack(side="left",fill="x",expand=True)
        tk.Label(title_box,text="3DPrintHub Catalog Intelligence",font=("Tahoma",19,"bold"),bg="#071827",fg="white").pack(anchor="w")
        tk.Label(title_box,text="مرکز مدیریت دریافت، ویرایش و انتشار محصولات",font=("Tahoma",10),bg="#071827",fg="#d7e1ea").pack(anchor="w",pady=(3,0))
        active_path=str(Path(__file__).resolve())
        tk.Label(title_box,text=f"فایل فعال: {active_path}",font=("Consolas",8),bg="#071827",fg="#91a4b5").pack(anchor="w",pady=(5,0))
        badge_box=tk.Frame(header,bg="#071827");badge_box.pack(side="right",padx=(14,0))
        self.header_badge=tk.StringVar(value=f"v{APP_VERSION} • آماده")
        tk.Label(badge_box,textvariable=self.header_badge,font=("Tahoma",11,"bold"),bg="#c99a2e",fg="#071827",padx=14,pady=7).pack(anchor="e")
        tk.Label(badge_box,text=f"BUILD {BUILD_ID}",font=("Consolas",8),bg="#071827",fg="#d7e1ea").pack(anchor="e",pady=(5,0))
        self.phase44_active_bar=tk.Frame(self,bg="#16a34a",height=3,bd=0,highlightthickness=0)
        self.phase44_active_bar.pack(fill="x",padx=10,pady=(0,0))
        self.phase44_active_bar.pack_propagate(False)
        nb=ttk.Notebook(self); nb.pack(fill="both",expand=True,padx=10,pady=(0,8)); self.main_notebook=nb
        self.products_tab=ttk.Frame(nb,padding=8); self.published_tab=ttk.Frame(nb,padding=8)
        self.blocked_tab=ttk.Frame(nb,padding=8)
        self.scan_tab=ttk.Frame(nb,padding=8); self.upload_tab=ttk.Frame(nb,padding=8)
        self.runs_tab=ttk.Frame(nb,padding=8); self.settings_tab=ttk.Frame(nb,padding=8)
        nb.add(self.products_tab,text="کارهای من")
        nb.add(self.published_tab,text="منتشرشده‌ها")
        nb.add(self.blocked_tab,text="کالاهای بلاک‌شده")
        nb.add(self.scan_tab,text="دریافت و کشف")
        nb.add(self.upload_tab,text="صف انتشار")
        nb.add(self.runs_tab,text="روندها و خطاها")
        nb.add(self.settings_tab,text="تنظیمات")
        self._products_ui(); self._published_ui(); self._blocked_ui(); self._scan_ui(); self._upload_ui(); self._runs_ui(); self._settings_ui()
        self.status=tk.StringVar(value="آماده")
        ttk.Label(self,textvariable=self.status,anchor="w",style="Status.TLabel").pack(fill="x")

    def refresh_all(self):
        """Refresh non-destructive UI state after widgets are created."""
        self.refresh_category_maps()
        sources=[src for src in self.config.get("sources",[]) if src.get("enabled",True)]
        self.source_map={str(src.get("name") or src.get("code") or ""):str(src.get("code") or "") for src in sources}
        source_names=[name for name,code in self.source_map.items() if name and code]
        self.source_box["values"]=source_names
        if source_names:
            if self.source_var.get() not in self.source_map:
                self.source_var.set(source_names[0])
            self.on_source()
        self.refresh_products()
        self.refresh_published()
        self.refresh_blocked()
        self.refresh_upload_queue()
        self.refresh_runs()

    def get_all_categories(self):
        base=[dict(x) for x in (self.config.get("local_categories") or []) if x.get("slug") and x.get("name")]
        try:
            custom=json.loads(self.db.setting("custom_categories_json","[]") or "[]")
            if not isinstance(custom,list): custom=[]
        except Exception:
            custom=[]
        seen=set(); result=[]
        for item in [*base,*custom]:
            slug=str(item.get("slug") or "").strip(); name=str(item.get("name") or "").strip()
            if not slug or not name or slug in seen: continue
            seen.add(slug); result.append({"slug":slug,"name":name})
        if not result:
            result=[{"slug":"external-other","name":"سایر محصولات"}]
        return result

    def refresh_category_maps(self):
        categories=self.get_all_categories()
        self.category_label_to_slug={item["name"]:item["slug"] for item in categories}
        self.category_slug_to_label={item["slug"]:item["name"] for item in categories}
        combo=getattr(self,"category_combo",None)
        if combo is not None:
            combo["values"]=list(self.category_label_to_slug)

    def _slugify_category(self,name):
        slug=re.sub(r"[^a-z0-9]+","-",str(name or "").lower()).strip("-")
        return slug or f"custom-{int(time.time())}"

    def add_custom_category_dialog(self,parent=None):
        parent=parent or self
        name=simpledialog.askstring("گروه جدید","نام فارسی گروه را وارد کنید:",parent=parent)
        if not name:return None
        name=name.strip()
        suggested=self._slugify_category(name)
        slug=simpledialog.askstring("شناسه گروه","Slug انگلیسی گروه را وارد کنید (برای نمونه: car-interior):",initialvalue=suggested,parent=parent)
        if slug is None:return None
        slug=self._slugify_category(slug)
        items=self.get_all_categories()
        existing=next((x for x in items if x["slug"]==slug or x["name"]==name),None)
        if existing:
            messagebox.showinfo(APP,f"این گروه از قبل وجود دارد: {existing['name']}",parent=parent)
            self.refresh_category_maps(); return existing["slug"],existing["name"]
        try:
            custom=json.loads(self.db.setting("custom_categories_json","[]") or "[]")
            if not isinstance(custom,list): custom=[]
        except Exception: custom=[]
        custom.append({"slug":slug,"name":name})
        self.db.set_setting("custom_categories_json",json.dumps(custom,ensure_ascii=False))
        self.refresh_category_maps()
        if hasattr(self,"category_label_var"): self.category_label_var.set(name)
        messagebox.showinfo(APP,f"گروه «{name}» اضافه شد و همراه Batch به سایت ارسال می‌شود.",parent=parent)
        return slug,name

    def open_product_studio(self,product_id=None):
        product_id=product_id or self.current_product
        if not product_id:
            messagebox.showwarning(APP,"ابتدا یک محصول را انتخاب کنید.");return
        try:
            ProductStudio(self,int(product_id))
        except Exception as exc:
            messagebox.showerror(APP,f"استودیوی محصول باز نشد:\n{exc}")

    def open_product_studio_translation(self):
        product_id=self.current_product
        if not product_id:
            messagebox.showwarning(APP,"ابتدا یک محصول را انتخاب کنید.");return
        try:
            studio=ProductStudio(self,int(product_id))
            studio.nb.select(studio.content_tab)
        except Exception as exc:
            messagebox.showerror(APP,f"استودیوی ترجمه باز نشد:\n{exc}")

    def _scan_ui(self):
        top=ttk.LabelFrame(self.scan_tab,text="منبع و نوع اسکن",padding=10); top.pack(fill="x")
        self.source_var=tk.StringVar(); self.mode_var=tk.StringVar(value="automatic")
        self.method_var=tk.StringVar(value="auto"); self.limit_var=tk.IntVar(value=20)
        self.seed_var=tk.StringVar(); self.query_var=tk.StringVar()
        ttk.Label(top,text="منبع").grid(row=0,column=0); self.source_box=ttk.Combobox(top,textvariable=self.source_var,state="readonly",width=24)
        self.source_box.grid(row=0,column=1,padx=5); self.source_box.bind("<<ComboboxSelected>>",self.on_source)
        ttk.Label(top,text="حالت").grid(row=0,column=2)
        ttk.Combobox(top,textvariable=self.mode_var,state="readonly",values=["automatic","category","single","search","site_crawl","web_search"],width=15).grid(row=0,column=3,padx=5)
        ttk.Label(top,text="روش").grid(row=0,column=4)
        ttk.Combobox(top,textvariable=self.method_var,state="readonly",values=["classic_isolated","classic_exact","network_capture","chrome_attached","saved_html","browser_dom","public_http"],width=17).grid(row=0,column=5,padx=5)
        ttk.Label(top,text="تعداد جدید").grid(row=0,column=6); ttk.Spinbox(top,from_=1,to=500,textvariable=self.limit_var,width=8).grid(row=0,column=7)
        ttk.Label(top,text="لینک گروه/محصول").grid(row=1,column=0,sticky="w",pady=8)
        ttk.Entry(top,textvariable=self.seed_var).grid(row=1,column=1,columnspan=5,sticky="ew",padx=5)
        ttk.Label(top,text="عبارت جستجو").grid(row=1,column=6); ttk.Entry(top,textvariable=self.query_var,width=22).grid(row=1,column=7)
        self.download_images_var=tk.IntVar(value=1)
        self.download_files_var=tk.IntVar(value=0)
        self.same_domain_var=tk.IntVar(value=1)
        ttk.Checkbutton(top,text="ذخیره تصاویر عمومی",variable=self.download_images_var).grid(row=2,column=1,sticky="w",pady=4)
        ttk.Checkbutton(top,text="دانلود فایل مستقیم عمومی",variable=self.download_files_var).grid(row=2,column=2,columnspan=2,sticky="w",pady=4)
        ttk.Checkbutton(top,text="خزش فقط در همان دامنه",variable=self.same_domain_var).grid(row=2,column=4,columnspan=2,sticky="w",pady=4)
        ttk.Label(top,text="نکته: فایل‌های لاگین‌دار یا محدود دور زده نمی‌شوند.").grid(row=2,column=6,columnspan=2,sticky="w")
        top.columnconfigure(5,weight=1)
        buttons=ttk.Frame(self.scan_tab,padding=(0,8))
        buttons.pack(fill="x")
        ttk.Button(buttons,text="شروع اسکن",command=self.start_scan).pack(side="left",padx=4)
        ttk.Button(buttons,text="Chrome پروفایل",command=self.setup_login).pack(side="left",padx=4)
        ttk.Button(buttons,text="Chrome متصل 9222",command=self.launch_debug_chrome).pack(side="left",padx=4)
        ttk.Button(buttons,text="توقف محترمانه",command=lambda:setattr(self,"stop_requested",True)).pack(side="left",padx=4)
        ttk.Button(buttons,text="بازنشانی خطاهای صف",command=self.reset_failed_queue).pack(side="left",padx=4)
        ttk.Button(buttons,text="نمایش وضعیت صف",command=self.show_queue_status).pack(side="left",padx=4)
        ttk.Button(buttons,text="دریافت هوشمند از لینک",command=self.start_direct_link_import,style="Primary.TButton").pack(side="left",padx=8)
        ttk.Button(buttons,text="🔎 کشف جدیدها",command=self.start_portfolio_harvest,style="Success.TButton").pack(side="left",padx=8)
        ttk.Button(buttons,text="♻ بروزرسانی محصولات منبع",command=self.refresh_source_products).pack(side="left",padx=8)
        self.direct_image_limit=tk.IntVar(value=int((self.config.get("direct_link") or {}).get("image_limit",60)))
        ttk.Label(buttons,text="حداکثر عکس").pack(side="left",padx=(8,2))
        ttk.Spinbox(buttons,from_=1,to=100,textvariable=self.direct_image_limit,width=5).pack(side="left")
        self.retry_failed_var=tk.IntVar(value=0)
        ttk.Checkbutton(buttons,text="Retry خطاهای قبلی",variable=self.retry_failed_var).pack(side="left",padx=8)
        self.scan_log=tk.Text(self.scan_tab,height=25,wrap="word",font=("Consolas",10)); self.scan_log.pack(fill="both",expand=True)

    def _products_ui(self):
        # Dashboard cards keep high-volume catalog work focused on actionable items.
        cards=ttk.Frame(self.products_tab); cards.pack(fill="x",pady=(0,8))
        self.dashboard_vars={}
        card_defs=[
            ("new_count","جدید","BlueCard"),("update_count","نیازمند بروزرسانی","OrangeCard"),
            ("no_image_count","بدون تصویر","RedCard"),("no_content_count","بدون محتوا","YellowCard"),
            ("queue_count","صف انتشار","PurpleCard"),("published_count","منتشرشده","GreenCard"),
        ]
        for idx,(key,label,style) in enumerate(card_defs):
            card=ttk.Frame(cards,padding=10,style=style+".TFrame"); card.grid(row=0,column=idx,sticky="ew",padx=4)
            v=tk.StringVar(value="0"); self.dashboard_vars[key]=v
            ttk.Label(card,text=label,style=style+".TLabel").pack(anchor="w")
            ttk.Label(card,textvariable=v,style=style+"Count.TLabel").pack(anchor="w")
            cards.columnconfigure(idx,weight=1)

        bar=ttk.Frame(self.products_tab); bar.pack(fill="x")
        self.product_filter=tk.StringVar(value="work_queue"); self.product_source=tk.StringVar(value=""); self.product_search=tk.StringVar(value=""); self.product_sort=tk.StringVar(value="priority")
        ttk.Label(bar,text="نمایش").pack(side="left")
        self.product_filter_box=ttk.Combobox(bar,textvariable=self.product_filter,state="readonly",
            values=["work_queue","new","needs_update","without_images","without_content","ready","upload_queue","error","all"],width=18)
        self.product_filter_box.pack(side="left",padx=5); self.product_filter_box.bind("<<ComboboxSelected>>",lambda e:self.refresh_products())
        ttk.Label(bar,text="جستجو").pack(side="left",padx=(10,2))
        search=ttk.Entry(bar,textvariable=self.product_search,width=26); search.pack(side="left",padx=4); search.bind("<Return>",lambda e:self.refresh_products())
        ttk.Button(bar,text="بروزرسانی",command=self.refresh_products).pack(side="left")
        ttk.Label(bar,text="مرتب‌سازی").pack(side="left",padx=(10,2))
        sort_box=ttk.Combobox(bar,textvariable=self.product_sort,state="readonly",values=["priority","rating","downloads","newest","updated"],width=12)
        sort_box.pack(side="left",padx=3);sort_box.bind("<<ComboboxSelected>>",lambda e:self.refresh_products())
        ttk.Button(bar,text="ذخیره",command=self.save_product).pack(side="left",padx=4)
        ttk.Button(bar,text="♻ بازیابی کامل",command=self.refetch_current_product,style="Primary.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="🖼 گالری تصاویر",command=self.open_image_manager,style="Primary.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="🚀 استودیوی محصول",command=self.open_product_studio,style="Success.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="✨ ترجمه فارسی",command=self.open_product_studio_translation,style="Primary.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="✨ AI این محصول",command=self.generate_ai_content,style="Success.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="AI انتخاب‌شده‌ها",command=self.bulk_ai_selected,style="Warning.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="AI همه نیازمندها",command=self.bulk_ai_pending,style="Warning.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="قیمت انتخاب‌شده‌ها",command=self.bulk_price_selected).pack(side="left",padx=4)

        bar2=ttk.Frame(self.products_tab); bar2.pack(fill="x",pady=(5,0))
        ttk.Button(bar2,text="♻ بازیابی انتخاب‌شده‌ها",command=self.bulk_refetch_selected,style="Warning.TButton").pack(side="left",padx=4)
        ttk.Button(bar2,text="استودیوی محتوا",command=self.open_content_studio).pack(side="left",padx=4)
        ttk.Button(bar2,text="تاریخچه",command=self.open_product_history).pack(side="left",padx=4)
        ttk.Button(bar2,text="تأیید و صف انتشار",command=self.approve_to_upload_queue,style="Success.TButton").pack(side="left",padx=4)
        ttk.Button(bar2,text="🚀 ارسال همین محصول",command=self.publish_product_now,style="Success.TButton").pack(side="left",padx=4)
        ttk.Button(bar2,text="🧾 گزارش ارسال",command=self.open_current_publish_log).pack(side="left",padx=4)
        ttk.Button(bar2,text="محاسبه قیمت",command=self.estimate_product_price).pack(side="left",padx=4)
        ttk.Button(bar2,text="صفحه منبع",command=self.open_source_product).pack(side="left",padx=4)
        ttk.Button(bar2,text="مشخصات و فایل‌ها",command=self.open_technical_details).pack(side="left",padx=4)
        ttk.Button(bar2,text="بلاک و انتقال",command=self.block_selected_products,style="Danger.TButton").pack(side="left",padx=4)

        pane=ttk.Panedwindow(self.products_tab,orient="horizontal"); pane.pack(fill="both",expand=True,pady=8)
        left=ttk.Frame(pane); right=ttk.Frame(pane,padding=8); pane.add(left,weight=5); pane.add(right,weight=3)
        cols=("id","status","source","rating","images","received","refetch","sync","en","fa","price")
        self.product_tree=ttk.Treeview(left,columns=cols,show="headings",selectmode="extended")
        specs=[
            ("id","ID",50),("status","وضعیت",120),("source","منبع",90),("rating","ریت",80),("images","عکس",65),
            ("received","دریافت",120),("refetch","بروزرسانی",120),("sync","سایت",120),
            ("en","عنوان منبع",250),("fa","عنوان فارسی",250),("price","قیمت",110),
        ]
        for c,label,width in specs:
            self.product_tree.heading(c,text=label); self.product_tree.column(c,width=width,anchor="center" if c not in {"en","fa"} else "w")
        self.product_tree.tag_configure("new",background="#dbeafe",foreground="#1e3a8a")
        self.product_tree.tag_configure("needs_content",background="#fef3c7",foreground="#78350f")
        self.product_tree.tag_configure("ready",background="#e0f2fe",foreground="#075985")
        self.product_tree.tag_configure("queued",background="#f3e8ff",foreground="#6b21a8")
        self.product_tree.tag_configure("published",background="#dcfce7",foreground="#166534")
        self.product_tree.tag_configure("needs_update",background="#ffedd5",foreground="#9a3412")
        self.product_tree.tag_configure("error",background="#fee2e2",foreground="#991b1b")
        yscroll=ttk.Scrollbar(left,orient="vertical",command=self.product_tree.yview); xscroll=ttk.Scrollbar(left,orient="horizontal",command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=yscroll.set,xscrollcommand=xscroll.set)
        self.product_tree.grid(row=0,column=0,sticky="nsew"); yscroll.grid(row=0,column=1,sticky="ns"); xscroll.grid(row=1,column=0,sticky="ew")
        left.rowconfigure(0,weight=1); left.columnconfigure(0,weight=1)
        self.product_tree.bind("<<TreeviewSelect>>",self.load_product)
        self.product_tree.bind("<Double-1>",lambda e:self.open_product_studio())

        preview=ttk.LabelFrame(right,text="تصاویر محصول",padding=8,style="Card.TLabelframe")
        preview.grid(row=0,column=0,columnspan=2,sticky="nsew",pady=(0,8))
        self.selected_images_text=tk.StringVar(value="انتخاب‌شده: 0")
        ttk.Label(preview,textvariable=self.selected_images_text).pack(anchor="w",pady=(0,4))
        self.inline_gallery=ttk.Frame(preview); self.inline_gallery.pack(fill="x",pady=(0,5))
        self._inline_thumb_photos=[]
        self.preview_label=ttk.Label(preview,text="محصولی انتخاب نشده است",anchor="center")
        self.preview_label.pack(fill="x",expand=False,pady=(2,0))
        nav=ttk.Frame(preview); nav.pack(fill="x",pady=(4,0))
        ttk.Button(nav,text="◀",command=lambda:self.change_preview(-1)).pack(side="left")
        self.preview_counter=tk.StringVar(value="0 / 0"); ttk.Label(nav,textvariable=self.preview_counter,anchor="center").pack(side="left",expand=True)
        ttk.Button(nav,text="▶",command=lambda:self.change_preview(1)).pack(side="right")
        image_actions=ttk.Frame(preview); image_actions.pack(fill="x",pady=(5,0))
        ttk.Button(image_actions,text="گالری گروهی",command=self.open_image_manager,style="Primary.TButton").pack(side="left")
        ttk.Button(image_actions,text="Primary",command=self.set_current_preview_primary).pack(side="left",padx=3)
        ttk.Button(image_actions,text="انتخاب/حذف سایت",command=self.toggle_current_image_selection).pack(side="left",padx=3)
        ttk.Button(image_actions,text="باز کردن",command=self.open_current_preview).pack(side="left",padx=3)
        self.current_image_text=tk.StringVar(value=""); ttk.Entry(preview,textvariable=self.current_image_text,state="readonly").pack(fill="x",pady=(3,0))
        source_row=ttk.Frame(preview); source_row.pack(fill="x",pady=(5,0))
        self.source_url_text=tk.StringVar(value=""); ttk.Entry(source_row,textvariable=self.source_url_text).pack(side="left",fill="x",expand=True)
        ttk.Button(source_row,text="لینک منبع",command=self.open_source_product).pack(side="left",padx=(5,0))
        self._preview_photo=None; self._preview_urls=[]; self._preview_index=0; self._preview_local=[]; self._preview_current=""; self._preview_items=[]

        self.product_meta=tk.StringVar(value="")
        ttk.Label(right,textvariable=self.product_meta,style="SubHeader.TLabel",wraplength=500).grid(row=1,column=0,columnspan=2,sticky="ew",pady=(0,5))
        self.fields={}; row=2
        for name,label in [("source_title","عنوان اصلی"),("title_fa","عنوان فارسی")]:
            ttk.Label(right,text=label).grid(row=row,column=0,sticky="w",pady=3); v=tk.StringVar(); self.fields[name]=v
            ttk.Entry(right,textvariable=v).grid(row=row,column=1,sticky="ew",pady=3); row+=1
        ttk.Label(right,text="دسته سایت").grid(row=row,column=0,sticky="w",pady=3)
        self.category_label_var=tk.StringVar(value=self.category_slug_to_label.get("external-other","سایر محصولات")); self.fields["local_category_slug"]=self.category_label_var
        cat_edit=ttk.Frame(right); cat_edit.grid(row=row,column=1,sticky="ew",pady=3); cat_edit.columnconfigure(0,weight=1)
        self.category_combo=ttk.Combobox(cat_edit,textvariable=self.category_label_var,state="readonly",values=list(self.category_label_to_slug),width=32)
        self.category_combo.grid(row=0,column=0,sticky="ew")
        ttk.Button(cat_edit,text="+ گروه",command=lambda:self.add_custom_category_dialog(parent=self)).grid(row=0,column=1,padx=(5,0)); row+=1
        for name,label in [("estimated_weight_grams","وزن تقریبی / گرم"),("material_price_per_gram","قیمت ماده / گرم"),
                           ("suggested_price","قیمت پیشنهادی فروش"),("final_price","قیمت قطعی فروش"),
                           ("source_price","قیمت در منبع"),("source_currency","ارز منبع")]:
            ttk.Label(right,text=label).grid(row=row,column=0,sticky="w",pady=3); v=tk.StringVar(); self.fields[name]=v
            ttk.Entry(right,textvariable=v).grid(row=row,column=1,sticky="ew",pady=3); row+=1
        for name,label in [("source_description","توضیحات اصلی"),("description_fa","توضیحات فارسی")]:
            ttk.Label(right,text=label).grid(row=row,column=0,sticky="ne",pady=3); w=tk.Text(right,height=4,wrap="word",background="#ffffff",foreground="#111827")
            w.grid(row=row,column=1,sticky="nsew",pady=3); self.fields[name]=w; row+=1
        ttk.Label(right,text="وضعیت مجوز تجاری").grid(row=row,column=0,sticky="w",pady=3)
        license_var=tk.StringVar(value="review"); self.fields["commercial_status"]=license_var
        ttk.Combobox(right,textvariable=license_var,state="readonly",values=["review","allowed","owned","public_domain","blocked","unknown"]).grid(row=row,column=1,sticky="ew",pady=3); row+=1
        ttk.Label(right,text="وضعیت آماده‌سازی").grid(row=row,column=0,sticky="w",pady=3)
        workflow=tk.StringVar(value="review"); self.fields["workflow_status"]=workflow
        ttk.Combobox(right,textvariable=workflow,state="readonly",values=["review","approved","batched","uploaded","needs_update"],width=20).grid(row=row,column=1,sticky="ew",pady=3); row+=1
        for name,label in [("price_is_final","قیمت قطعی"),("approved_for_sale","تأیید فروش"),("publish_as_product","محصول قابل چاپ"),("publish_as_portfolio","نمونه‌کار")]:
            v=tk.IntVar(); self.fields[name]=v; ttk.Checkbutton(right,text=label,variable=v).grid(row=row,column=1,sticky="w"); row+=1
        right.columnconfigure(1,weight=1); right.rowconfigure(0,weight=1)

    def _published_ui(self):
        top=ttk.Frame(self.published_tab); top.pack(fill="x",pady=(0,8))
        self.published_search=tk.StringVar(value="")
        ttk.Label(top,text="محصولات تأییدشده سایت").pack(side="left")
        ttk.Entry(top,textvariable=self.published_search,width=32).pack(side="left",padx=8)
        ttk.Button(top,text="جستجو/بروزرسانی",command=self.refresh_published).pack(side="left")
        ttk.Label(top,text="محصولی که منبعش تغییر کند خودکار از این صفحه خارج و نارنجی وارد کارهای من می‌شود.",style="SubHeader.TLabel").pack(side="right")
        cols=("id","source","rating","images","published","refetch","sync","title","server")
        self.published_tree=ttk.Treeview(self.published_tab,columns=cols,show="headings",selectmode="browse")
        for c,label,w in [("id","ID",55),("source","منبع",100),("rating","ریت",90),("images","عکس",65),("published","انتشار سایت",130),
                          ("refetch","آخرین بازیابی",130),("sync","آخرین Sync",130),("title","عنوان",420),("server","Server ID",90)]:
            self.published_tree.heading(c,text=label); self.published_tree.column(c,width=w,anchor="center" if c!="title" else "w")
        self.published_tree.tag_configure("published",background="#dcfce7",foreground="#166534")
        self.published_tree.pack(fill="both",expand=True)
        self.published_tree.bind("<Double-1>",lambda e:self.open_published_in_editor())
        ttk.Button(self.published_tab,text="باز کردن محصول در ویرایشگر",command=self.open_published_in_editor,style="Primary.TButton").pack(anchor="w",pady=7)

    def _upload_ui(self):
        bar=ttk.Frame(self.upload_tab); bar.pack(fill="x",pady=(0,8))
        ttk.Button(bar,text="🚀 انتشار و ارسال به سایت",command=self.publish_queue_to_site,style="Publish.TButton").pack(side="left",padx=(0,8))
        ttk.Button(bar,text="بروزرسانی صف",command=self.refresh_upload_queue).pack(side="left",padx=4)
        ttk.Button(bar,text="ساخت Batch از صف",command=self.build_batch).pack(side="left",padx=4)
        ttk.Button(bar,text="ارسال آخرین Batch",command=self.upload_last_batch,style="Primary.TButton").pack(side="left",padx=4)
        ttk.Button(bar,text="حذف از صف",command=self.remove_from_upload_queue).pack(side="left",padx=4)
        cols=("id","source","title","category","images","weight","price","state")
        self.upload_tree=ttk.Treeview(self.upload_tab,columns=cols,show="headings")
        for c,t,w in zip(cols,["ID","منبع","عنوان","دسته","عکس","وزن g","قیمت","وضعیت"],[55,100,330,170,70,80,120,90]):
            self.upload_tree.heading(c,text=t); self.upload_tree.column(c,width=w,anchor="center")
        self.upload_tree.pack(fill="both",expand=True)

    def _blocked_ui(self):
        bar=ttk.Frame(self.blocked_tab);bar.pack(fill="x",pady=(0,8))
        ttk.Label(bar,text="این کالاها نمایش، بازیابی، AI، بروزرسانی و انتشار نمی‌شوند.").pack(side="left")
        ttk.Button(bar,text="بروزرسانی",command=self.refresh_blocked).pack(side="right",padx=4)
        ttk.Button(bar,text="بازگردانی انتخاب‌شده",command=self.restore_selected_products,style="Warning.TButton").pack(side="right",padx=4)
        cols=("id","source","external","title","blocked_at","reason")
        self.blocked_tree=ttk.Treeview(self.blocked_tab,columns=cols,show="headings",selectmode="extended")
        for c,t,w in zip(cols,["ID","منبع","شناسه منبع","عنوان","زمان بلاک","دلیل"],[55,100,130,360,160,420]):
            self.blocked_tree.heading(c,text=t);self.blocked_tree.column(c,width=w,anchor="center" if c!="title" else "w")
        self.blocked_tree.pack(fill="both",expand=True)

    def _runs_ui(self):
        cols=("id","source","mode","method","status","new","collected","dup","failed","started","message")
        self.runs_tree=ttk.Treeview(self.runs_tab,columns=cols,show="headings")
        for c,t,w in zip(cols,["ID","منبع","حالت","روش","وضعیت","جدید","دریافت","تکراری","خطا","شروع","پیام"],[45,90,80,100,80,60,60,60,60,130,350]):
            self.runs_tree.heading(c,text=t); self.runs_tree.column(c,width=w,anchor="center")
        self.runs_tree.pack(fill="both",expand=True)
        ttk.Button(self.runs_tab,text="بروزرسانی",command=self.refresh_runs).pack(anchor="w",pady=5)

    def _settings_ui(self):
        self.ai_provider=tk.StringVar(value=env_value("CATALOG_AI_PROVIDER", self.db.setting("ai_provider", self.config.get("ai",{}).get("provider","auto"))))
        if self.ai_provider.get() not in {"auto","avalai","openai"}: self.ai_provider.set("auto")
        self.ai_model=tk.StringVar(value=env_value("CATALOG_AI_MODEL", self.db.setting("ai_model", self.config.get("ai",{}).get("model",""))))
        self.openai_model=self.ai_model  # compatibility with older v8 code paths
        self.ai_key=tk.StringVar(value="")
        self.openai_key=self.ai_key
        self.google_key=tk.StringVar(value=env_value("GOOGLE_API_KEY", self.db.setting("google_api_key")))
        self.translation_provider=tk.StringVar(value=self.db.setting("translation_provider","ai"))
        self.ftp_protocol=tk.StringVar(value="FTP")
        self.ftp_host=tk.StringVar(value=env_value("CATALOG_FTP_HOST", self.db.setting("ftp_host","ftp.3dprinthub.ir")))
        self.ftp_port=tk.StringVar(value=env_value("CATALOG_FTP_PORT", self.db.setting("ftp_port","21")))
        self.ftp_user=tk.StringVar(value=env_value("CATALOG_FTP_USER", self.db.setting("ftp_user","sfkilvrs")))
        self.ftp_password=tk.StringVar(value=env_value("CATALOG_FTP_PASSWORD", ""))
        self.ftp_remote_root=tk.StringVar(value=env_value("CATALOG_FTP_REMOTE_ROOT", self.db.setting("ftp_remote_root","/3dprinthub")))
        self.site_url=tk.StringVar(value=env_value("CATALOG_SITE_URL", self.db.setting("site_url","https://3dprinthub.ir")))
        self.bridge_token=tk.StringVar(value=env_value("CATALOG_BRIDGE_TOKEN", ""))

        ai=ttk.LabelFrame(self.settings_tab,text="هوش مصنوعی / ترجمه / تولید محتوا",padding=14,style="Card.TLabelframe")
        ai.grid(row=0,column=0,columnspan=2,sticky="ew",padx=8,pady=8)
        ttk.Label(ai,text="Provider").grid(row=0,column=0,sticky="w",pady=5)
        provider_box=ttk.Combobox(ai,textvariable=self.ai_provider,values=["auto","avalai","openai"],state="readonly",width=20)
        provider_box.grid(row=0,column=1,sticky="w",padx=6)
        provider_box.bind("<<ComboboxSelected>>",lambda e:self._refresh_ai_key_source())
        ttk.Label(ai,text="مدل قابل دسترسی").grid(row=1,column=0,sticky="w",pady=5)
        self.ai_model_box=ttk.Combobox(ai,textvariable=self.ai_model,values=[],width=38)
        self.ai_model_box.grid(row=1,column=1,sticky="ew",padx=6)
        ttk.Button(ai,text="دریافت مدل‌ها",command=self.load_ai_models).grid(row=1,column=2,padx=4)
        ttk.Label(ai,text="API Key جدید").grid(row=2,column=0,sticky="w",pady=5)
        key_row=ttk.Frame(ai); key_row.grid(row=2,column=1,columnspan=2,sticky="ew",padx=6)
        self.openai_key_entry=ttk.Entry(key_row,textvariable=self.ai_key,show="•")
        self.openai_key_entry.pack(side="left",fill="x",expand=True)
        self.openai_key_visible=False
        self.openai_key_entry.bind("<Control-v>",lambda e:self.paste_openai_key())
        self.openai_key_entry.bind("<Control-V>",lambda e:self.paste_openai_key())
        self.openai_key_entry.bind("<Button-3>",self.open_openai_key_menu)
        ttk.Button(key_row,text="Paste",command=self.paste_openai_key).pack(side="left",padx=3)
        ttk.Button(key_row,text="نمایش/مخفی",command=self.toggle_openai_key_visibility).pack(side="left",padx=3)
        self.openai_key_source=tk.StringVar(value="")
        ttk.Label(ai,textvariable=self.openai_key_source,style="SubHeader.TLabel").grid(row=3,column=1,columnspan=2,sticky="w",padx=6)
        actions=ttk.Frame(ai); actions.grid(row=4,column=1,columnspan=2,sticky="w",pady=8)
        ttk.Button(actions,text="ذخیره امن در Windows",command=self.save_openai_secret,style="Primary.TButton").pack(side="left",padx=3)
        ttk.Button(actions,text="انتقال APIKEY*.txt به Windows",command=self.migrate_ai_key_file).pack(side="left",padx=3)
        ttk.Button(actions,text="🧪 تست زنده AI",command=self.test_openai_api,style="Success.TButton").pack(side="left",padx=3)
        ttk.Button(actions,text="پاک کردن فیلد",command=lambda:self.ai_key.set("")).pack(side="left",padx=3)
        ttk.Button(actions,text="حذف کلید امن",command=self.clear_openai_secret).pack(side="left",padx=3)
        ttk.Label(ai,text="Auto ابتدا AvalAI و سپس OpenAI Direct را امتحان می‌کند. کلید در SQLite/Git ذخیره نمی‌شود.",style="SubHeader.TLabel").grid(row=5,column=1,columnspan=2,sticky="w",padx=6)
        ai.columnconfigure(1,weight=1)
        self._refresh_ai_key_source()

        conn=ttk.LabelFrame(self.settings_tab,text="اتصال سایت",padding=14,style="Card.TLabelframe")
        conn.grid(row=1,column=0,columnspan=2,sticky="ew",padx=8,pady=8)
        rows=[("پروتکل",self.ftp_protocol,False),("FTP Host",self.ftp_host,False),("FTP Port",self.ftp_port,False),("FTP Username",self.ftp_user,False),("FTP Password",self.ftp_password,True),("مسیر پروژه روی FTP",self.ftp_remote_root,False),("آدرس سایت",self.site_url,False),("Bridge Token",self.bridge_token,True)]
        for i,(lab,var,secret) in enumerate(rows):
            ttk.Label(conn,text=lab).grid(row=i,column=0,sticky="w",padx=5,pady=5)
            if lab == "پروتکل":
                ttk.Combobox(conn,textvariable=var,values=["FTP"],state="readonly").grid(row=i,column=1,sticky="ew",padx=5)
            elif lab == "Bridge Token":
                token_row=ttk.Frame(conn);token_row.grid(row=i,column=1,sticky="ew",padx=5)
                self.bridge_token_entry=ttk.Entry(token_row,textvariable=var,show="•")
                self.bridge_token_entry.pack(side="left",fill="x",expand=True)
                self.bridge_token_visible=False
                self.bridge_token_entry.bind("<Control-v>",self.paste_bridge_token)
                self.bridge_token_entry.bind("<Control-V>",self.paste_bridge_token)
                self.bridge_token_entry.bind("<Shift-Insert>",self.paste_bridge_token)
                self.bridge_token_entry.bind("<Button-3>",self.open_bridge_token_menu)
                ttk.Button(token_row,text="چسباندن توکن",command=self.paste_bridge_token).pack(side="left",padx=3)
                ttk.Button(token_row,text="نمایش/مخفی",command=self.toggle_bridge_token_visibility).pack(side="left",padx=3)
            else:
                ttk.Entry(conn,textvariable=var,show="•" if secret else "").grid(row=i,column=1,sticky="ew",padx=5)
        self.connection_secret_source=tk.StringVar(value="")
        ttk.Label(conn,textvariable=self.connection_secret_source,style="SubHeader.TLabel").grid(row=len(rows),column=1,sticky="w",padx=5,pady=3)
        actions=ttk.Frame(conn);actions.grid(row=len(rows)+1,column=1,sticky="w",pady=8)
        ttk.Button(actions,text="ذخیره امن تنظیمات",command=self.save_connection_settings,style="Primary.TButton").pack(side="left",padx=3)
        ttk.Button(actions,text="تست اتصال FTP",command=self.test_ftp_connection).pack(side="left",padx=3)
        ttk.Button(actions,text="تست Bridge سایت",command=self.test_site_connection).pack(side="left",padx=3)
        ttk.Button(actions,text="بازکردن پوشه لاگ",command=self.open_log_folder).pack(side="left",padx=3)
        ttk.Button(conn,text="آپلود آخرین Batch + دریافت ACK",command=self.upload_last_batch,style="Success.TButton").grid(row=len(rows)+2,column=1,sticky="w",pady=5)
        conn.columnconfigure(1,weight=1)
        self._refresh_connection_secret_source()

        help_box=ttk.LabelFrame(self.settings_tab,text="راهنمای کلیدها",padding=14,style="Card.TLabelframe")
        help_box.grid(row=2,column=0,columnspan=2,sticky="ew",padx=8,pady=8)
        ttk.Label(help_box,text=f"تنظیمات پایدار: {ENV_FILE} | اولویت خواندن: .env سپس Credential Store/SQLite. فایل .env در Upgrade حفظ می‌شود.",style="SubHeader.TLabel",wraplength=1050).pack(anchor="w")
        ttk.Button(help_box,text="باز کردن فایل .env",command=self.open_persistent_env,style="Primary.TButton").pack(anchor="w",pady=(8,0))
        self.settings_tab.columnconfigure(1,weight=1)

    def open_persistent_env(self):
        try:
            if not ENV_FILE.is_file():
                ENV_FILE.write_text("# 3DPrintHub persistent settings\n",encoding="utf-8")
            os.startfile(str(ENV_FILE))
            self.status.set(f"فایل تنظیمات باز شد: {ENV_FILE}")
        except Exception as exc:
            messagebox.showerror(APP,f"باز کردن .env ناموفق بود:\n{exc}")

    def _provider_candidates(self):
        selected=(self.ai_provider.get() or "auto").strip().lower()
        return [selected] if selected in {"avalai","openai"} else ["avalai","openai"]

    def _refresh_ai_key_source(self):
        parts=[]
        for provider in self._provider_candidates():
            env_name="AVALAI_API_KEY" if provider == "avalai" else "OPENAI_API_KEY"
            source=env_source(env_name) if env_value(env_name) else provider_key_source(provider)
            parts.append(f"{provider}: {source}")
        if hasattr(self,"openai_key_source"): self.openai_key_source.set("منبع کلید | "+" | ".join(parts))

    def paste_openai_key(self):
        try: value=self.clipboard_get().strip()
        except Exception: value=""
        if value:
            self.ai_key.set(value); self.status.set("API Key در فیلد قرار گرفت؛ برای ذخیره امن دکمه ذخیره را بزنید.")
        return "break"

    def toggle_openai_key_visibility(self):
        self.openai_key_visible=not bool(getattr(self,"openai_key_visible",False)); self.openai_key_entry.configure(show="" if self.openai_key_visible else "•")

    def open_openai_key_menu(self,event):
        menu=tk.Menu(self,tearoff=0);menu.add_command(label="Paste",command=self.paste_openai_key);menu.add_command(label="Clear",command=lambda:self.ai_key.set(""));menu.tk_popup(event.x_root,event.y_root)

    def paste_bridge_token(self,event=None):
        try: raw_value=self.clipboard_get()
        except Exception: raw_value=""
        token=normalize_bridge_token_input(raw_value)
        if token:
            self.bridge_token.set(token)
            self.status.set("توکن Bridge در فیلد قرار گرفت؛ برای ذخیره امن دکمه ذخیره را بزنید.")
        else:
            self.status.set("Clipboard شامل Bridge Token معتبر نیست.")
        return "break"

    def toggle_bridge_token_visibility(self):
        self.bridge_token_visible=not bool(getattr(self,"bridge_token_visible",False))
        self.bridge_token_entry.configure(show="" if self.bridge_token_visible else "•")

    def open_bridge_token_menu(self,event):
        menu=tk.Menu(self,tearoff=0)
        menu.add_command(label="چسباندن",command=self.paste_bridge_token)
        menu.add_command(label="پاک کردن",command=lambda:self.bridge_token.set(""))
        try:menu.tk_popup(event.x_root,event.y_root)
        finally:menu.grab_release()

    def _entered_bridge_token(self):
        raw_value=self.bridge_token.get()
        token=normalize_bridge_token_input(raw_value)
        if raw_value.strip() and not token:
            raise ValueError("Bridge Token واردشده معتبر نیست.")
        return token

    def _selected_ai_provider(self):
        selected=(self.ai_provider.get() or "auto").strip().lower()
        if selected in {"avalai","openai"}: return selected
        for provider in ("avalai","openai"):
            env_name="AVALAI_API_KEY" if provider == "avalai" else "OPENAI_API_KEY"
            if env_value(env_name) or get_provider_key(provider): return provider
        return "avalai"

    def _ai_key(self,provider=None):
        provider=provider or self._selected_ai_provider()
        env_name="AVALAI_API_KEY" if provider == "avalai" else "OPENAI_API_KEY"
        return self.ai_key.get().strip() or env_value(env_name) or get_provider_key(provider)

    def _openai_key(self): return self._ai_key()

    def save_openai_secret(self):
        key=self.ai_key.get().strip(); provider=self._selected_ai_provider()
        if not key: messagebox.showwarning(APP,"کلید جدیدی وارد نشده است."); return
        try:
            set_provider_key(provider,key);self.ai_key.set("");self._refresh_ai_key_source();messagebox.showinfo(APP,f"کلید {provider} در Windows Credential Store ذخیره شد.")
        except Exception as exc: messagebox.showerror(APP,str(exc))

    def migrate_ai_key_file(self):
        migrated=[]
        for provider in self._provider_candidates():
            try:
                if migrate_legacy_key_to_keyring(provider): migrated.append(provider)
            except Exception as exc:
                messagebox.showerror(APP,f"{provider}: {exc}"); return
        self._refresh_ai_key_source()
        messagebox.showinfo(APP,"کلیدهای منتقل‌شده: "+(", ".join(migrated) if migrated else "فایل کلید معتبری پیدا نشد"))

    def clear_openai_secret(self):
        provider=self._selected_ai_provider()
        if not messagebox.askyesno(APP,f"کلید ذخیره‌شده {provider} حذف شود؟"): return
        delete_provider_key(provider);self.ai_key.set("");self._refresh_ai_key_source()

    def load_ai_models(self):
        provider=self._selected_ai_provider();key=self._ai_key(provider)
        if not key: messagebox.showwarning(APP,f"کلید {provider} پیدا نشد.");return
        self.status.set(f"دریافت مدل‌های {provider}...")
        def work():
            try:
                models=AIContentService(key,self.ai_model.get(),provider).list_models();self.events.put(("ai_models",(provider,models)))
            except Exception as exc:self.events.put(("error",str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def test_openai_api(self):
        provider=self._selected_ai_provider();key=self._ai_key(provider)
        if not key: messagebox.showwarning(APP,f"API Key برای {provider} پیدا نشد.");return
        model=self.ai_model.get().strip();self.status.set(f"تست زنده {provider}...")
        def work():
            try:self.events.put(("openai_test",AIContentService(key,model,provider).test_connection()))
            except Exception as exc:self.events.put(("error",str(exc)))
        threading.Thread(target=work,daemon=True).start()

    def _json_value(self, raw, default):
        try:
            value=json.loads(raw or "")
            return value if isinstance(value,type(default)) else default
        except Exception:
            return default

    def _source_context_for_ai(self,row):
        return {
            "source_title":row["source_title"] or "",
            "source_description":row["source_description"] or "",
            "source_categories":self._json_value(row["source_categories_json"] if "source_categories_json" in row.keys() else "[]",[]),
            "source_category":row["source_category"] or "",
            "source_specs":self._json_value(row["source_specs_json"] or "{}",{}),
            "source_tags":self._json_value(row["tags_json"] or "[]",[]),
            "author_name":row["author_name"] or "",
            "license_name":row["license_name"] or "",
            "source_price":row["source_price"],
            "source_currency":row["source_currency"] or "",
            "estimated_weight_grams":row["estimated_weight_grams"],
            "estimated_print_minutes":row["estimated_print_minutes"],
        }

    def generate_ai_content(self):
        if not self.current_product:
            messagebox.showwarning(APP,"ابتدا یک محصول انتخاب کنید.")
            return
        self.save_product()
        row=self.db.product(self.current_product)
        key=self._openai_key()
        if not key:
            messagebox.showwarning(APP,"OpenAI API Key تنظیم نشده است. از تب تنظیمات واردش کنید.")
            return
        source=self._source_context_for_ai(row)
        selected_image_urls=self._safe_json_list(row["selected_images_json"] or row["images_json"])
        image_count=len(selected_image_urls)
        model=self.openai_model.get().strip()
        local_categories=list(self.config.get("local_categories") or [])
        self.status.set("OpenAI در حال ترجمه و تولید پکیج محتوایی کامل...")
        self.header_badge.set("AI • در حال تولید محتوا")
        def work():
            try:
                pack=AIContentService(key,model,self._selected_ai_provider()).enrich_product(
                    source,local_categories,image_count=image_count,image_urls=selected_image_urls,
                )
                self.events.put(("ai_content",(self.current_product,pack)))
            except Exception as exc:
                self.events.put(("error",f"OpenAI: {exc}"))
        threading.Thread(target=work,daemon=True).start()

    def _selected_product_ids(self):
        if not hasattr(self,"product_tree"):return []
        return [int(x) for x in self.product_tree.selection() if str(x).isdigit()]

    def bulk_ai_selected(self):
        ids=self._selected_product_ids()
        if not ids:
            messagebox.showwarning(APP,"حداقل یک محصول را از جدول انتخاب کنید.");return
        self._start_bulk_ai(ids)

    def bulk_ai_pending(self):
        ids=[r["id"] for r in self.db.products("without_content")]
        if not ids:
            messagebox.showinfo(APP,"محصول نیازمند تولید محتوا وجود ندارد.");return
        if not messagebox.askyesno(APP,f"برای {len(ids)} محصول ترجمه + تولید محتوا + قیمت پیشنهادی انجام شود؟"):
            return
        self._start_bulk_ai(ids)

    def _start_bulk_ai(self,ids):
        key=self._openai_key()
        if not key:
            messagebox.showwarning(APP,"OpenAI API Key تنظیم نشده است.");return
        model=self.openai_model.get().strip()
        local_categories=list(self.config.get("local_categories") or [])
        ids=list(dict.fromkeys(int(x) for x in ids))
        self.status.set(f"AI گروهی: 0 از {len(ids)}")
        self.header_badge.set("AI Bulk • فعال")
        def work():
            success=failed=0
            for idx,pid in enumerate(ids,1):
                try:
                    row=self.db.product(pid)
                    if not row:continue
                    source=self._source_context_for_ai(row)
                    images=self._safe_json_list(row["selected_images_json"] or row["images_json"])
                    pack=AIContentService(key,model,self._selected_ai_provider()).enrich_product(source,local_categories,image_count=len(images),image_urls=images)
                    self.events.put(("bulk_ai_item",(pid,pack,idx,len(ids))))
                    success+=1
                except Exception as exc:
                    failed+=1;self.events.put(("log",f"BULK_AI_FAILED product={pid} {exc}"))
            self.events.put(("bulk_ai_done",(success,failed,len(ids))))
        threading.Thread(target=work,daemon=True).start()

    def bulk_refetch_selected(self):
        ids=self._selected_product_ids()
        if not ids:
            messagebox.showwarning(APP,"حداقل یک محصول را انتخاب کنید.");return
        if not messagebox.askyesno(APP,f"{len(ids)} محصول دوباره از منبع خوانده شوند؟ ویرایش انسانی حفظ می‌شود."):
            return
        image_limit=max(1,int(self.direct_image_limit.get() or 60))
        self.status.set(f"بازیابی گروهی: 0 از {len(ids)}")
        def work():
            changed=unchanged=failed=0
            for idx,pid in enumerate(ids,1):
                row=self.db.product(pid)
                if not row:continue
                try:
                    output=DATA/"collected"/row["source_code"]/f"{row['external_id']}_bulk_refetch_{int(time.time())}"
                    fresh=asyncio.run(extract_direct_link(row["source_url"],output,PROFILE_ROOT/row["source_code"],headed=False,download_images=True,image_limit=image_limit))
                    fresh["source_code"]=row["source_code"];fresh["external_id"]=row["external_id"];fresh["normalized_url"]=normalize_url(fresh["source_url"])
                    fresh["fingerprint"]=product_fingerprint(fresh["source_code"],fresh["external_id"],fresh["source_url"]);fresh["source_hash"]=source_payload_hash(fresh);fresh["last_refetched_at"]=utc_now();fresh["source_state"]="active"
                    fresh["needs_update"]=1 if should_mark_needs_update(row,fresh["source_hash"]) else int(row["needs_update"] or 0)
                    fresh["content_status"]="stale" if fresh["needs_update"] else (row["content_status"] or "pending")
                    if fresh["needs_update"]:fresh["workflow_status"]="needs_update"
                    diff=product_diff(dict(row),fresh)
                    if diff:
                        before=dict(row);merged=merge_refetch(row,fresh);allowed=set(row.keys())-{"id","created_at","updated_at"};self.db.update_product(pid,{k:v for k,v in merged.items() if k in allowed});self.db.save_history(pid,"bulk_refetch",before,dict(self.db.product(pid)),diff_summary(diff));changed+=1
                    else:unchanged+=1
                except Exception as exc:
                    failed+=1;self.events.put(("log",f"BULK_REFETCH_FAILED product={pid} {exc}"))
                self.events.put(("bulk_refetch_progress",(idx,len(ids))))
            self.events.put(("bulk_refetch_done",(changed,unchanged,failed,len(ids))))
        threading.Thread(target=work,daemon=True).start()

    def bulk_price_selected(self):
        ids=self._selected_product_ids()
        if not ids:
            messagebox.showwarning(APP,"محصولی انتخاب نشده است.");return
        changed=0
        for pid in ids:
            row=self.db.product(pid)
            if not row:continue
            value=pricing_suggestion(row["estimated_weight_grams"],row["material_price_per_gram"],row["estimated_print_minutes"])
            self.db.update_product(pid,{"suggested_price":value});changed+=1
        self.refresh_products();
        if self.current_product:self.load_product()
        messagebox.showinfo(APP,f"قیمت پیشنهادی {changed} محصول بروزرسانی شد.")

    def _apply_ai_pack(self,product_id,pack,open_studio=True):
        row=self.db.product(product_id)
        before=dict(row) if row else {}
        specs_pack=pack.get("specs_fa") or []
        if isinstance(specs_pack,list):
            specs_pack={str(item.get("key") or "").strip():str(item.get("value") or "").strip() for item in specs_pack if isinstance(item,dict) and str(item.get("key") or "").strip()}
        if not isinstance(specs_pack,dict):specs_pack={}
        values={
            "title_fa":pack.get("title_fa","")[:260],
            "short_description_fa":pack.get("short_description_fa","")[:500],
            "description_fa":pack.get("description_fa","") or "",
            "categories_fa_json":json.dumps(pack.get("categories_fa") or [],ensure_ascii=False),
            "specs_fa_json":json.dumps(specs_pack,ensure_ascii=False),
            "tags_fa_json":json.dumps(pack.get("tags_fa") or [],ensure_ascii=False),
            "hashtags_fa_json":json.dumps(pack.get("hashtags_fa") or [],ensure_ascii=False),
            "material_recommendations_json":json.dumps(pack.get("material_recommendations") or [],ensure_ascii=False),
            "use_case_class":pack.get("use_case_class","") or "",
            "ai_provider":pack.get("_ai_provider",self._selected_ai_provider()),
            "ai_model":pack.get("_ai_model",self.ai_model.get()),
            "ai_suggested_category_slug":pack.get("suggested_category_slug","") or "",
            "ai_confidence":float(pack.get("category_confidence") or 0),
            "seo_title_fa":pack.get("seo_title_fa","")[:260],
            "seo_description_fa":pack.get("seo_description_fa","")[:500],
            "sales_bullets_json":json.dumps(pack.get("sales_bullets") or [],ensure_ascii=False),
            "social_caption_fa":pack.get("social_caption_fa","") or "",
            "image_alt_texts_json":json.dumps(pack.get("image_alt_texts") or [],ensure_ascii=False),
            "content_pack_json":json.dumps(pack,ensure_ascii=False),
            "translation_status":"ai_ready",
            "content_status":"ready",
            "last_ai_at":utc_now(),
        }
        self.db.update_product(product_id,values)
        after=dict(self.db.product(product_id))
        self.db.save_history(product_id,"ai_content",before,after,"OpenAI content pack generated")
        if product_id==self.current_product:
            self.load_product()
        self.refresh_products()
        if open_studio:
            self.open_content_studio(product_id)

    def open_content_studio(self,product_id=None):
        product_id=product_id or self.current_product
        if not product_id:
            messagebox.showwarning(APP,"ابتدا محصول را انتخاب کنید.")
            return
        row=self.db.product(product_id)
        if not row:return
        win=tk.Toplevel(self); win.title("استودیوی تولید محتوا | 3DPrintHub v8.5"); win.geometry("1180x820"); win.minsize(900,650)
        top=ttk.Frame(win,padding=12); top.pack(fill="x")
        ttk.Label(top,text=row["title_fa"] or row["source_title"] or f"Product #{product_id}",style="Header.TLabel").pack(anchor="w")
        ttk.Label(top,text="تمام خروجی AI قابل ویرایش است؛ هیچ چیز بدون تأیید شما منتشر نمی‌شود.",style="SubHeader.TLabel").pack(anchor="w")
        nb=ttk.Notebook(win); nb.pack(fill="both",expand=True,padx=12,pady=8)
        tabs={name:ttk.Frame(nb,padding=12) for name in ["محتوا","مشخصات و دسته","SEO و فروش","تصاویر"]}
        for name,frame in tabs.items():nb.add(frame,text=name)
        title=tk.StringVar(value=row["title_fa"] or "")
        short=tk.Text(tabs["محتوا"],height=5,wrap="word"); desc=tk.Text(tabs["محتوا"],height=15,wrap="word"); social=tk.Text(tabs["محتوا"],height=7,wrap="word")
        ttk.Label(tabs["محتوا"],text="عنوان فارسی").pack(anchor="w"); ttk.Entry(tabs["محتوا"],textvariable=title).pack(fill="x",pady=(2,8))
        ttk.Label(tabs["محتوا"],text="توضیح کوتاه").pack(anchor="w"); short.pack(fill="x",pady=(2,8)); short.insert("1.0",row["short_description_fa"] or "")
        ttk.Label(tabs["محتوا"],text="توضیح کامل").pack(anchor="w"); desc.pack(fill="both",expand=True,pady=(2,8)); desc.insert("1.0",row["description_fa"] or "")
        ttk.Label(tabs["محتوا"],text="کپشن شبکه اجتماعی").pack(anchor="w"); social.pack(fill="x",pady=(2,8)); social.insert("1.0",row["social_caption_fa"] or "")

        cat_text=tk.Text(tabs["مشخصات و دسته"],height=7,wrap="word"); specs_text=tk.Text(tabs["مشخصات و دسته"],height=18,wrap="word"); tags_text=tk.Text(tabs["مشخصات و دسته"],height=6,wrap="word")
        ttk.Label(tabs["مشخصات و دسته"],text="مسیر دسته‌بندی ترجمه‌شده (هر خط یک سطح)").pack(anchor="w"); cat_text.pack(fill="x",pady=(2,8)); cat_text.insert("1.0","\n".join(self._json_value(row["categories_fa_json"],[])))
        ttk.Label(tabs["مشخصات و دسته"],text=f"پیشنهاد دسته سایت: {row['ai_suggested_category_slug'] or '—'} | اطمینان: {float(row['ai_confidence'] or 0)*100:.0f}%").pack(anchor="w",pady=4)
        ttk.Label(tabs["مشخصات و دسته"],text="مشخصات فارسی (JSON قابل ویرایش)").pack(anchor="w"); specs_text.pack(fill="both",expand=True,pady=(2,8)); specs_text.insert("1.0",json.dumps(self._json_value(row["specs_fa_json"],{}),ensure_ascii=False,indent=2))
        ttk.Label(tabs["مشخصات و دسته"],text="تگ‌های فارسی (هر خط)").pack(anchor="w"); tags_text.pack(fill="x",pady=(2,8)); tags_text.insert("1.0","\n".join(self._json_value(row["tags_fa_json"],[])))

        seo_title=tk.StringVar(value=row["seo_title_fa"] or ""); seo_desc=tk.Text(tabs["SEO و فروش"],height=6,wrap="word"); bullets=tk.Text(tabs["SEO و فروش"],height=8,wrap="word"); hashtags=tk.Text(tabs["SEO و فروش"],height=5,wrap="word")
        ttk.Label(tabs["SEO و فروش"],text="SEO Title").pack(anchor="w"); ttk.Entry(tabs["SEO و فروش"],textvariable=seo_title).pack(fill="x",pady=(2,8))
        ttk.Label(tabs["SEO و فروش"],text="SEO Description").pack(anchor="w"); seo_desc.pack(fill="x",pady=(2,8)); seo_desc.insert("1.0",row["seo_description_fa"] or "")
        ttk.Label(tabs["SEO و فروش"],text="نکات فروش (هر خط)").pack(anchor="w"); bullets.pack(fill="x",pady=(2,8)); bullets.insert("1.0","\n".join(self._json_value(row["sales_bullets_json"],[])))
        ttk.Label(tabs["SEO و فروش"],text="هشتگ‌های پیشنهادی (هر خط)").pack(anchor="w"); hashtags.pack(fill="x",pady=(2,8)); hashtags.insert("1.0","\n".join(self._json_value(row["hashtags_fa_json"],[])))
        recs=self._json_value(row["material_recommendations_json"],[])
        rec_text=tk.Text(tabs["مشخصات و دسته"],height=8,wrap="word")
        ttk.Label(tabs["مشخصات و دسته"],text=f"کاربری تشخیص‌داده‌شده: {row['use_case_class'] or '—'}").pack(anchor="w",pady=(6,2))
        ttk.Label(tabs["مشخصات و دسته"],text="پیشنهاد متریال (قابل بازبینی اپراتور)").pack(anchor="w")
        rec_text.pack(fill="x",pady=(2,8)); rec_text.insert("1.0","\n".join(f"{r.get('material','')} | {r.get('score','')} | {'پیشنهادی' if r.get('recommended') else 'اختیاری'} | {r.get('reason_fa','')}" for r in recs if isinstance(r,dict)))

        alts=tk.Text(tabs["تصاویر"],height=24,wrap="word")
        ttk.Label(tabs["تصاویر"],text="Alt فارسی تصاویر به ترتیب گالری (هر خط یک تصویر)").pack(anchor="w"); alts.pack(fill="both",expand=True,pady=8); alts.insert("1.0","\n".join(self._json_value(row["image_alt_texts_json"],[])))

        def save_dialog():
            try:
                specs=json.loads(specs_text.get("1.0","end").strip() or "{}")
                if not isinstance(specs,dict):raise ValueError("مشخصات باید JSON Object باشد.")
            except Exception as exc:
                messagebox.showerror(APP,f"JSON مشخصات معتبر نیست: {exc}",parent=win);return
            values={
                "title_fa":title.get().strip(),"short_description_fa":short.get("1.0","end").strip(),"description_fa":desc.get("1.0","end").strip(),
                "social_caption_fa":social.get("1.0","end").strip(),"categories_fa_json":json.dumps([x.strip() for x in cat_text.get("1.0","end").splitlines() if x.strip()],ensure_ascii=False),
                "specs_fa_json":json.dumps(specs,ensure_ascii=False),"tags_fa_json":json.dumps([x.strip() for x in tags_text.get("1.0","end").splitlines() if x.strip()],ensure_ascii=False),
                "seo_title_fa":seo_title.get().strip(),"seo_description_fa":seo_desc.get("1.0","end").strip(),
                "sales_bullets_json":json.dumps([x.strip() for x in bullets.get("1.0","end").splitlines() if x.strip()],ensure_ascii=False),
                "hashtags_fa_json":json.dumps([x.strip() for x in hashtags.get("1.0","end").splitlines() if x.strip()],ensure_ascii=False),
                "image_alt_texts_json":json.dumps([x.strip() for x in alts.get("1.0","end").splitlines() if x.strip()],ensure_ascii=False),
                "content_status":"ready",
            }
            before=dict(self.db.product(product_id)); self.db.update_product(product_id,values); after=dict(self.db.product(product_id)); self.db.save_history(product_id,"content_edit",before,after,"Manual content studio edit")
            if product_id==self.current_product:self.load_product()
            messagebox.showinfo(APP,"پکیج محتوا ذخیره شد.",parent=win)
        footer=ttk.Frame(win,padding=12); footer.pack(fill="x")
        ttk.Button(footer,text="ذخیره تغییرات",command=save_dialog,style="Success.TButton").pack(side="right",padx=4)
        ttk.Button(footer,text="بستن",command=win.destroy).pack(side="right",padx=4)

    def refetch_current_product(self):
        if not self.current_product:
            messagebox.showwarning(APP,"ابتدا یک محصول انتخاب کنید.");return
        self.save_product(); product_id=self.current_product; row=self.db.product(product_id); url=row["source_url"] or ""
        if not url.startswith(("http://","https://")):
            messagebox.showwarning(APP,"لینک منبع معتبر نیست.");return
        image_limit=max(1,int(self.direct_image_limit.get() or 60))
        self.status.set("در حال بازیابی کامل لینک، تصاویر، فایل‌ها و مشخصات..."); self.header_badge.set("Refetch • فعال")
        def work():
            try:
                code=row["source_code"]; ext=row["external_id"]; stamp=time.strftime("%Y%m%d_%H%M%S")
                output=DATA/"collected"/code/f"{ext}_refetch_{stamp}"
                fresh=asyncio.run(extract_direct_link(url,output,PROFILE_ROOT/code,headed=True,download_images=True,image_limit=image_limit))
                fresh["source_code"]=row["source_code"]; fresh["external_id"]=row["external_id"]; fresh["normalized_url"]=normalize_url(fresh["source_url"])
                fresh["fingerprint"]=product_fingerprint(fresh["source_code"],fresh["external_id"],fresh["source_url"])
                fresh["source_hash"]=source_payload_hash(fresh); fresh["last_refetched_at"]=utc_now(); fresh["source_state"]="active"
                fresh["needs_update"]=1 if should_mark_needs_update(row,fresh["source_hash"]) else int(row["needs_update"] or 0)
                fresh["content_status"]="stale" if fresh["needs_update"] else (row["content_status"] or "pending")
                if fresh["needs_update"]: fresh["workflow_status"]="needs_update"
                diff=product_diff(dict(row),fresh)
                self.events.put(("refetch_ready",(product_id,fresh,diff)))
            except Exception as exc:self.events.put(("error",f"بازیابی مجدد ناموفق بود: {type(exc).__name__}: {exc}"))
        threading.Thread(target=work,daemon=True).start()

    def _accept_refetch(self,product_id,fresh,diff):
        row=self.db.product(product_id); before=dict(row)
        merged=merge_refetch(row,fresh)
        allowed=set(row.keys())-{"id","created_at","updated_at"}
        values={k:v for k,v in merged.items() if k in allowed}
        self.db.update_product(product_id,values); after=dict(self.db.product(product_id))
        self.db.save_history(product_id,"refetch",before,after,diff_summary(diff))
        self.current_product=product_id; self.refresh_products(); self.load_product(); self.status.set("بازیابی کامل اعمال شد"); self.header_badge.set(f"v{APP_VERSION} • آماده")

    def open_product_history(self):
        if not self.current_product:return
        rows=self.db.history(self.current_product,100)
        win=tk.Toplevel(self);win.title("تاریخچه تغییرات محصول");win.geometry("1000x650")
        text=tk.Text(win,wrap="word",font=("Consolas",10));text.pack(fill="both",expand=True,padx=10,pady=10)
        for row in rows:
            text.insert("end",f"[{row['created_at']}] {row['event_type']}\n{row['note']}\n")
            try:
                before=json.loads(row["before_json"]);after=json.loads(row["after_json"])
                text.insert("end",diff_summary(product_diff(before,after))+"\n")
            except Exception:pass
            text.insert("end","-"*90+"\n")
        text.configure(state="disabled")

    def refresh_source_products(self):
        code=self.source_map.get(self.source_var.get().strip(),self.source_var.get().strip())
        if not code and self.current_product:
            row=self.db.product(self.current_product); code=row["source_code"] if row else ""
        if not code:
            messagebox.showwarning(APP,"ابتدا منبع را انتخاب کنید.");return
        rows=self.db.products("all",source_code=code)[:max(1,int(self.limit_var.get() or 20))]
        if not rows:
            messagebox.showinfo(APP,"برای این منبع محصول محلی وجود ندارد.");return
        if not messagebox.askyesno(APP,f"{len(rows)} محصول موجود از {code} دوباره بررسی شوند؟\nتصمیم‌های ویرایشی شما حفظ می‌شوند."):
            return
        image_limit=max(1,int(self.direct_image_limit.get() or 60))
        self.status.set(f"بروزرسانی محصولات {code}...")
        def work():
            changed=unchanged=failed=0
            for row in rows:
                try:
                    output=DATA/"collected"/code/f"{row['external_id']}_refresh_latest"
                    fresh=asyncio.run(extract_direct_link(row["source_url"],output,PROFILE_ROOT/code,headed=False,download_images=True,image_limit=image_limit))
                    fresh["source_code"]=row["source_code"]; fresh["external_id"]=row["external_id"]; fresh["normalized_url"]=normalize_url(fresh["source_url"])
                    fresh["fingerprint"]=product_fingerprint(fresh["source_code"],fresh["external_id"],fresh["source_url"]); fresh["source_hash"]=source_payload_hash(fresh); fresh["last_refetched_at"]=utc_now();fresh["source_state"]="active"
                    fresh["needs_update"]=1 if should_mark_needs_update(row,fresh["source_hash"]) else int(row["needs_update"] or 0)
                    fresh["content_status"]="stale" if fresh["needs_update"] else (row["content_status"] or "pending")
                    if fresh["needs_update"]: fresh["workflow_status"]="needs_update"
                    diff=product_diff(dict(row),fresh)
                    if diff:
                        before=dict(row); merged=merge_refetch(row,fresh); allowed=set(row.keys())-{"id","created_at","updated_at"}; self.db.update_product(row["id"],{k:v for k,v in merged.items() if k in allowed}); self.db.save_history(row["id"],"source_refresh",before,dict(self.db.product(row["id"])),diff_summary(diff));changed+=1
                    else:unchanged+=1
                except Exception as exc:
                    failed+=1; self.log(f"REFRESH_FAILED {row['source_url']} {exc}")
            self.events.put(("source_refresh_done",(code,changed,unchanged,failed)))
        threading.Thread(target=work,daemon=True).start()

    def on_source(self,_e=None):
        code=self.source_map.get(self.source_var.get(),"")
        src=self.db.source(code)
        if src:
            methods=json.loads(src["methods_json"]); self.method_var.set("auto")
            self.limit_var.set(src["daily_limit"])

    def log(self,text):
        self.events.put(("log",text))

    def reset_failed_queue(self):
        code=self.source_map.get(self.source_var.get(),"")
        updated=self.db.reset_failed_urls(code)
        counts=self.db.queue_counts(code)
        self.log(f"RESET_FAILED={updated} QUEUE={counts}")
        messagebox.showinfo(APP,f"{updated} مورد به صف جدید برگشت.\n{counts}")

    def show_queue_status(self):
        code=self.source_map.get(self.source_var.get(),"")
        counts=self.db.queue_counts(code)
        self.log(f"QUEUE_STATUS {code}: {counts}")
        messagebox.showinfo(APP,str(counts))

    def launch_debug_chrome(self):
        import subprocess, os
        chrome_candidates=[
            Path(os.environ.get("PROGRAMFILES",""))/"Google"/"Chrome"/"Application"/"chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)",""))/"Google"/"Chrome"/"Application"/"chrome.exe",
            Path(os.environ.get("LOCALAPPDATA",""))/"Google"/"Chrome"/"Application"/"chrome.exe",
        ]
        chrome=next((item for item in chrome_candidates if item.is_file()),None)
        if chrome is None:
            raise RuntimeError("Google Chrome پیدا نشد.")
        profile=DATA/"attached_chrome_profile"
        profile.mkdir(parents=True,exist_ok=True)
        subprocess.Popen([
            str(chrome),
            "--remote-debugging-port=9222",
            f"--user-data-dir={profile}",
            self.seed_var.get().strip() or "https://makerworld.com/en",
        ])

    def setup_login(self):
        code=self.source_map.get(self.source_var.get(),"")
        def work():
            async def go():
                async with BrowserSession(PROFILE_ROOT/code,headed=True,min_delay=0,max_delay=0) as session:
                    src=self.db.source(code)
                    listing=json.loads(src["listing_urls_json"]) if src else []
                    seed=self.seed_var.get().strip() or (listing[0] if listing else "https://www.google.com")
                    await session.page.goto(seed,wait_until="domcontentloaded",timeout=90000)
                    self.log("مرورگر باز شد. ورود، CAPTCHA یا تأیید لازم را خودتان انجام دهید.")
                    self.log("پس از اتمام، پنجره مرورگر را ببندید.")
                    while session.context.pages:
                        await asyncio.sleep(1)
            try: asyncio.run(go())
            except Exception as e: self.events.put(("error",str(e)))
        threading.Thread(target=work,daemon=True).start()

    def start_direct_link_import(self):
        if getattr(self,"scan_running",False):
            return
        url=self.seed_var.get().strip()
        if not url.startswith(("http://","https://")):
            messagebox.showwarning(APP,"یک لینک کامل http/https وارد کنید.")
            return
        self.scan_running=True; self.stop_requested=False
        direct_image_limit=max(1,int(self.direct_image_limit.get() or 60))
        direct_download_images=bool(self.download_images_var.get())
        direct_headed=bool((self.config.get("direct_link") or {}).get("headed",True))
        self.status.set("در حال تحلیل کامل صفحه و دریافت تصاویر...")
        def worker():
            try:
                async def go():
                    code=detect_source_code(url)
                    external_id=detect_external_id(url,code)
                    from .phase49_3i38_crawl_ledger_stage_ai import (
                        remember_ledger,
                        terminal_identity_state,
                    )
                    terminal_state=terminal_identity_state(self.db,code,external_id,url)
                    if terminal_state:
                        self.log(
                            f"DIRECT_LINK_SKIP_TERMINAL status={terminal_state} "
                            f"source={code} external_id={external_id} url={url}"
                        )
                        self.status.set(
                            "این لینک قبلاً رد/بلاک شده و قبل از دانلود Skip شد"
                        )
                        return
                    local_dir=DATA/"collected"/code/external_id
                    self.log(f"DIRECT_LINK_START {url}")
                    data=await extract_direct_link(
                        url,local_dir,PROFILE_ROOT/code,
                        headed=direct_headed,
                        download_images=direct_download_images,
                        image_limit=direct_image_limit,
                    )
                    source_cfg=next((x for x in self.config.get("sources",[]) if x.get("code")==code),None)
                    data["fingerprint"]=product_fingerprint(data["source_code"],data["external_id"],data["source_url"])
                    data["source_hash"]=source_payload_hash(data)
                    data["last_refetched_at"]=utc_now()
                    data["source_state"]="active"
                    existing=self.db.conn.execute(
                        "SELECT * FROM products WHERE source_code=? AND external_id=? ORDER BY id LIMIT 1",
                        (data["source_code"],data["external_id"]),
                    ).fetchone()
                    if existing is None:
                        existing=self.db.conn.execute(
                            "SELECT * FROM products WHERE source_code=? AND normalized_url=? ORDER BY id LIMIT 1",
                            (data["source_code"],normalize_url(data["source_url"])),
                        ).fetchone()
                    if existing:
                        data["needs_update"]=1 if should_mark_needs_update(existing,data["source_hash"]) else int(existing["needs_update"] or 0)
                        data["content_status"]="stale" if data["needs_update"] else (existing["content_status"] or "pending")
                        if data["needs_update"]: data["workflow_status"]="needs_update"
                        before=dict(existing); merged=merge_refetch(existing,data); allowed=set(existing.keys())-{"id","created_at","updated_at"}
                        self.db.update_product(existing["id"],{k:v for k,v in merged.items() if k in allowed})
                        self.db.save_history(existing["id"],"direct_refetch",before,dict(self.db.product(existing["id"])),diff_summary(product_diff(before,data)))
                        self.log(f"DIRECT_LINK_EXISTING_UPDATE product_id={existing['id']}")
                    else:
                        data.update({
                            "reference_only":int(bool((source_cfg or {}).get("reference_only",False))),
                            "suggested_price":500000,
                            "final_price":0,
                            "price_is_final":0,
                            "approved_for_sale":0,
                            "publish_as_product":1,
                            "publish_as_portfolio":0,
                            "translation_status":"pending",
                            "commercial_status":"review",
                            "local_category_slug":"external-other",
                            "material_price_per_gram":0,
                            "workflow_status":"review",
                            "upload_ready":0,
                            "custom_notes":"",
                            "content_status":"pending",
                            "needs_update":0,
                            "product_sync_error":"",
                        })
                        self.db.upsert_product(data)
                        row_new=self.db.conn.execute("SELECT id FROM products WHERE source_code=? AND external_id=?",(data["source_code"],data["external_id"])).fetchone()
                        if row_new:self.db.save_history(row_new["id"],"initial_extract",{},data,"Direct intelligent extraction")
                    remember_ledger(
                        self.db,
                        data["source_code"],
                        data["external_id"],
                        data["source_url"],
                        status="collected",
                        discovered_from="direct_link",
                        force=False,
                    )
                    self.log(f"DIRECT_LINK_IMAGES={len(json.loads(data.get('images_json') or '[]'))}")
                    self.log(f"DIRECT_LINK_FILES={len(json.loads(data.get('file_links_json') or '[]'))}")
                    self.log(f"DIRECT_LINK_WEIGHT_G={data.get('estimated_weight_grams')}")
                    self.log(f"DIRECT_LINK_SOURCE_PRICE={data.get('source_price')} {data.get('source_currency') or ''}")
                    self.log("DIRECT_LINK_END")
                    self.events.put(("focus_product",(code,external_id)))
                asyncio.run(go())
            except Exception as exc:
                self.events.put(("error",f"دریافت هوشمند لینک ناموفق بود: {type(exc).__name__}: {exc}"))
            finally:
                self.scan_running=False
                self.events.put(("refresh",None))
        threading.Thread(target=worker,daemon=True).start()

    def start_portfolio_harvest(self):
        """Collect a small review queue from all configured portfolio sources.

        The workflow intentionally keeps every imported item unapproved for sale.
        Commercial use is reviewed later per-model in the editor.
        """
        if getattr(self,"scan_running",False):
            return
        requested=max(1,int(self.limit_var.get() or 1))
        self.scan_running=True; self.stop_requested=False

        def worker():
            source_methods={
                "makerworld":"classic_isolated",
                "printables":"classic_isolated",
                "thingiverse":"classic_isolated",
                "grabcad":"classic_isolated",
            }
            try:
                self.log(f"PORTFOLIO_HARVEST_START PER_SOURCE={requested}")
                for code,method in source_methods.items():
                    if self.stop_requested:
                        break
                    src=self.db.source(code)
                    if not src or not int(src["enabled"]):
                        self.log(f"PORTFOLIO_SKIP {code}: disabled or missing")
                        continue
                    self.log(f"PORTFOLIO_SOURCE_START {code} METHOD={method}")
                    try:
                        # _scan_worker is synchronous from this worker's perspective.
                        # It owns an asyncio loop for one source at a time.
                        self._scan_worker(code,"automatic",method,requested,keep_running=True)
                    except Exception as exc:
                        self.log(f"PORTFOLIO_SOURCE_FAILED {code}: {type(exc).__name__}: {exc}")
                    self.log(f"PORTFOLIO_SOURCE_END {code}")
                self.log("PORTFOLIO_HARVEST_END")
            finally:
                self.scan_running=False
                self.events.put(("refresh",None))
        threading.Thread(target=worker,daemon=True).start()

    def start_scan(self):
        if getattr(self,"scan_running",False): return
        self.scan_running=True; self.stop_requested=False
        code=self.source_map.get(self.source_var.get(),""); mode=self.mode_var.get()
        requested=self.limit_var.get(); selected=self.method_var.get()
        threading.Thread(target=self._scan_worker,args=(code,mode,selected,requested),daemon=True).start()

    def _scan_worker(self,code,mode,selected,requested,keep_running=False):
        src=self.db.source(code)
        run_id=self.db.create_run(code,mode,selected,requested)
        discovered=collected=duplicates=failed=0
        message=""

        async def execute():
            nonlocal discovered,collected,duplicates,failed,message
            seed=self.seed_var.get().strip()
            query=self.query_var.get().strip()
            listing=json.loads(src["listing_urls_json"])

            if selected=="saved_html":
                html_path=filedialog.askopenfilename(
                    title="فایل HTML ذخیره‌شده",
                    filetypes=[("HTML","*.html;*.htm"),("All files","*.*")],
                )
                if not html_path:
                    raise RuntimeError("فایل HTML انتخاب نشد.")
                if not seed:
                    raise RuntimeError("لینک اصلی محصول را وارد کنید.")
                external_id=__import__("hashlib").sha1(
                    seed.encode("utf-8")
                ).hexdigest()[:16]
                from .phase49_3i38_crawl_ledger_stage_ai import (
                    remember_ledger,
                    terminal_identity_state,
                )
                terminal_state=terminal_identity_state(self.db,code,external_id,seed)
                if terminal_state:
                    duplicates+=1
                    message=f"این لینک قبلاً {terminal_state} شده و HTML دوباره وارد نشد."
                    self.log(
                        f"SAVED_HTML_SKIP_TERMINAL status={terminal_state} "
                        f"source={code} external_id={external_id} url={seed}"
                    )
                    return
                local_dir=DATA/"collected"/code/external_id
                result=import_saved_html(
                    Path(html_path),
                    seed,
                    local_dir,
                )
                if self.db.add_discovered(code,external_id,seed,"saved_html"):
                    discovered+=1
                else:
                    duplicates+=1
                parsed=parse_product(
                    Path(result["html_path"]).read_text(
                        encoding="utf-8",
                        errors="replace",
                    ),
                    seed,
                    result.get("title",""),
                    [],
                )
                data={
                    "source_code":code,
                    "external_id":external_id,
                    "source_url":seed,
                    "local_dir":str(local_dir),
                    "reference_only":src["reference_only"],
                    "suggested_price":500000,
                    "final_price":0,
                    "price_is_final":0,
                    "approved_for_sale":0,
                    "publish_as_product":0,
                    "publish_as_portfolio":0,
                    "translation_status":"pending",
                    "commercial_status":"review",
                    "local_category_slug":"external-other",
                    "material_price_per_gram":0,
                    **parsed,
                }
                self.db.upsert_product(data)
                remember_ledger(
                    self.db,
                    code,
                    external_id,
                    seed,
                    status="collected",
                    discovered_from="saved_html",
                    force=False,
                )
                collected+=1
                message="HTML ذخیره‌شده وارد شد."
                return

            if mode=="single":
                if not seed:
                    raise RuntimeError("لینک محصول وارد نشده است.")
                pattern=src["model_url_pattern"]
                match=re.search(pattern,seed,re.I) if pattern else None
                external_id=(
                    match.groupdict().get("external_id","")
                    if match
                    else ""
                )
                if not external_id:
                    external_id=__import__("hashlib").sha1(
                        seed.encode("utf-8")
                    ).hexdigest()[:16]
                if self.db.add_discovered(code,external_id,seed,"single"):
                    discovered+=1
                else:
                    duplicates+=1
            else:
                encoded=__import__("urllib.parse").parse.quote_plus(query or "3d print")
                if mode in {"category","site_crawl"}:
                    target_templates=[seed]
                    # Same listing can be an infinite-scroll page. Revisit it at
                    # progressively deeper scroll cursors until enough NEW ledger
                    # identities are found; previously collected/rejected URLs
                    # remain duplicates and are never re-queued.
                    max_pages=12
                elif mode=="search":
                    target_templates=listing[:1]
                    max_pages=8
                else:
                    target_templates=[seed] if seed else listing[:1]
                    max_pages=10

                if not target_templates or not target_templates[0]:
                    raise RuntimeError("لینک شروع یا Listing URL وجود ندارد.")

                from .phase49_3i38_crawl_ledger_stage_ai import (
                    next_scroll_rounds,
                    record_listing_progress,
                )
                enough=False
                stagnant_targets={}
                for page_no in range(1,max_pages+1):
                    if enough or self.stop_requested:
                        break
                    for template in target_templates:
                        try:
                            target=template.format(query=encoded,page=page_no)
                        except Exception:
                            target=template
                        scroll_rounds=next_scroll_rounds(
                            self.db,
                            code,
                            target,
                            default_rounds=8,
                            step=8,
                            maximum=96,
                        )
                        self.log(
                            f"CLASSIC_DISCOVERY PAGE={page_no} "
                            f"SCROLL_ROUNDS={scroll_rounds}: {target}"
                        )
                        result=await discover_classic(
                            target,
                            model_pattern=src["model_url_pattern"],
                            scroll_rounds=scroll_rounds,
                            headed=False,
                        )
                        self.log(
                            f"DISCOVERY_HTTP={result['http_status']} "
                            f"BROWSER={result['browser']} "
                            f"FOUND={len(result['links'])}"
                        )
                        new_this_round=0
                        for external_id,url in result["links"]:
                            if self.db.add_discovered(code,external_id,url,target):
                                discovered+=1
                                new_this_round+=1
                            else:
                                duplicates+=1
                        record_listing_progress(
                            self.db,
                            code,
                            target,
                            scroll_rounds=scroll_rounds,
                            found_count=len(result["links"]),
                            new_count=new_this_round,
                        )
                        target_key=normalize_url(target)
                        if new_this_round:
                            stagnant_targets[target_key]=0
                        else:
                            stagnant_targets[target_key]=int(stagnant_targets.get(target_key,0))+1
                        pending_now=len(self.db.pending_urls(code,requested,include_failed=False))
                        self.log(
                            f"DISCOVERY_LEDGER NEW_THIS_ROUND={new_this_round} "
                            f"PENDING_NOW={pending_now} "
                            f"STAGNANT={stagnant_targets[target_key]}"
                        )
                        if pending_now>=requested:
                            enough=True
                            break
                        if stagnant_targets[target_key]>=2:
                            self.log(
                                f"DISCOVERY_EXHAUSTED_CURRENT_DEPTH target={target} "
                                f"scroll_rounds={scroll_rounds}"
                            )
                            break
                    if not enough and page_no<max_pages:
                        await asyncio.sleep(3)

            rows=self.db.pending_urls(
                code,
                requested,
                include_failed=bool(self.retry_failed_var.get()),
            )
            self.log(f"PENDING_SELECTED={len(rows)}")

            for index,row in enumerate(rows,start=1):
                if self.stop_requested:
                    break

                local_dir=DATA/"collected"/code/(
                    row["external_id"] or str(row["id"])
                )
                self.log(
                    f"CLASSIC_COLLECT [{index}/{len(rows)}] "
                    f"{row['url']}"
                )

                try:
                    if selected=="chrome_attached":
                        result=await collect_attached_chrome(
                            row["url"],
                            local_dir,
                            capture_network=True,
                            download_images=bool(self.download_images_var.get()),
                        )
                    else:
                        result=await collect_classic_exact(
                            row["url"],
                            local_dir,
                            headed=False,
                            capture_network=(selected=="network_capture"),
                            download_images=bool(self.download_images_var.get()),
                        )

                    html=Path(result["html_path"]).read_text(
                        encoding="utf-8",
                        errors="replace",
                    )
                    parsed=parse_product(
                        html,
                        result["final_url"],
                        result.get("title",""),
                        result.get("dom_image_urls",[]),
                    )

                    # Browser-context downloads preserve the same public cookies/referer.
                    # Keep urllib as a fallback only when the browser did not save images.
                    saved_images=list(result.get("downloaded_images") or [])
                    if self.download_images_var.get() and not saved_images:
                        image_urls=json.loads(parsed.get("images_json") or "[]")
                        image_dir=local_dir/"images"
                        for image_index,image_url in enumerate(image_urls[:12],start=1):
                            try:
                                suffix=Path(__import__("urllib.parse").parse.urlsplit(image_url).path).suffix.lower()
                                if suffix not in {".png",".jpg",".jpeg",".webp",".gif",".avif"}:
                                    suffix=".jpg"
                                target=download_public_file(image_url,image_dir/f"{image_index:02d}{suffix}",max_bytes=20_000_000)
                                saved_images.append(str(target))
                            except Exception as image_error:
                                self.log(f"IMAGE_DOWNLOAD_FAILED [{image_index}] {image_error}")
                    self.log(f"IMAGES_FOUND={len(json.loads(parsed.get('images_json') or '[]'))} IMAGES_SAVED={len(saved_images)}")

                    data={
                        "source_code":code,
                        "external_id":row["external_id"] or str(row["id"]),
                        "source_url":result["final_url"],
                        "local_dir":str(local_dir),
                        "reference_only":src["reference_only"],
                        "suggested_price":500000,
                        "final_price":0,
                        "price_is_final":0,
                        "approved_for_sale":0,
                        "publish_as_product":0,
                        "publish_as_portfolio":0,
                        "translation_status":"pending",
                        "commercial_status":"review",
                        "local_category_slug":"external-other",
                        "material_price_per_gram":0,
                        **parsed,
                    }
                    self.db.upsert_product(data)
                    self.db.mark_url(row["id"],"collected")
                    collected+=1
                    self.log(
                        f"HTTP={result.get('http_status')} "
                        f"OK={parsed.get('source_title') or result['final_url']}"
                    )
                except PermissionError as error:
                    self.db.mark_url(row["id"],"failed",str(error))
                    failed+=1
                    self.log(f"STOP_ON_BLOCK={error}")
                    self.stop_requested=True
                    break
                except Exception as error:
                    self.db.mark_url(row["id"],"failed",str(error))
                    failed+=1
                    self.log(
                        f"FAILED={type(error).__name__}: {error}"
                    )
                    break

                if index < len(rows):
                    delay=__import__("random").randint(60,90)
                    self.log(f"DELAY_SECONDS={delay}")
                    await asyncio.sleep(delay)

            message="روش Classic پایان یافت."

        try:
            asyncio.run(execute())
            self.db.finish_run(
                run_id,
                status="completed",
                discovered_count=discovered,
                collected_count=collected,
                duplicate_count=duplicates,
                failed_count=failed,
                message=message,
            )
        except Exception as error:
            message=str(error)
            self.db.finish_run(
                run_id,
                status="failed",
                discovered_count=discovered,
                collected_count=collected,
                duplicate_count=duplicates,
                failed_count=failed+1,
                message=message,
            )
            self.events.put(("error",message))
        finally:
            if not keep_running:
                self.scan_running=False
            self.events.put(("refresh",None))

    def _update_dashboard(self):
        counts=self.db.status_counts()
        for key,var in getattr(self,"dashboard_vars",{}).items():
            var.set(str(counts.get(key,0)))

    def _rating_text(self,row):
        rating=row["source_rating"] if "source_rating" in row.keys() else None
        count=int(row["source_rating_count"] or 0) if "source_rating_count" in row.keys() else 0
        if rating is None:return "—"
        return f"★ {float(rating):.1f}" + (f" ({count})" if count else "")

    def _date_short(self,value):
        value=str(value or "")
        return value.replace("T"," ")[:16] if value else "—"

    def refresh_products(self):
        if not hasattr(self,"product_tree"):return
        for i in self.product_tree.get_children(): self.product_tree.delete(i)
        rows=self.db.products(self.product_filter.get(),search=self.product_search.get())
        sort_key=self.product_sort.get() if hasattr(self,"product_sort") else "priority"
        if sort_key=="rating": rows.sort(key=lambda r:(float(r["source_rating"] or 0),int(r["source_rating_count"] or 0)),reverse=True)
        elif sort_key=="downloads": rows.sort(key=lambda r:int(r["source_download_count"] or 0),reverse=True)
        elif sort_key=="newest": rows.sort(key=lambda r:str(r["created_at"] or ""),reverse=True)
        elif sort_key=="updated": rows.sort(key=lambda r:str(r["last_refetched_at"] or r["updated_at"] or ""),reverse=True)
        for r in rows:
            state=product_state(r); price=r["final_price"] if r["price_is_final"] else r["suggested_price"]
            sync_date=r["last_synced_at"] or r["published_at"] or ""
            values=(r["id"],STATUS_LABELS.get(state,state),r["source_code"],self._rating_text(r),image_count(r),
                    self._date_short(r["created_at"]),self._date_short(r["last_refetched_at"] or r["updated_at"]),
                    self._date_short(sync_date),r["source_title"],r["title_fa"],f"{int(price or 0):,}")
            self.product_tree.insert("","end",iid=str(r["id"]),values=values,tags=(state,))
        self._update_dashboard()
        self.refresh_published()

    def refresh_published(self):
        if not hasattr(self,"published_tree"):return
        for i in self.published_tree.get_children():self.published_tree.delete(i)
        search=self.published_search.get() if hasattr(self,"published_search") else ""
        for r in self.db.products("published",search=search):
            title=r["title_fa"] or r["source_title"]
            self.published_tree.insert("","end",iid=f"pub-{r['id']}",values=(r["id"],r["source_code"],self._rating_text(r),image_count(r),
                self._date_short(r["published_at"] or r["last_synced_at"]),self._date_short(r["last_refetched_at"]),
                self._date_short(r["last_synced_at"]),title,r["server_id"]),tags=("published",))

    def open_published_in_editor(self):
        sel=self.published_tree.selection() if hasattr(self,"published_tree") else ()
        if not sel:return
        values=self.published_tree.item(sel[0],"values")
        if not values:return
        product_id=int(values[0])
        self.product_filter.set("all"); self.product_search.set(""); self.refresh_products(); self.main_notebook.select(self.products_tab)
        iid=str(product_id)
        if self.product_tree.exists(iid):
            self.product_tree.selection_set(iid);self.product_tree.focus(iid);self.product_tree.see(iid);self.load_product()

    def block_selected_products(self):
        ids=self._selected_product_ids()
        if not ids:
            messagebox.showwarning(APP,"حداقل یک کالا را انتخاب کنید.");return
        reason=simpledialog.askstring(APP,"دلیل بلاک‌کردن (اختیاری):",parent=self) or ""
        if not messagebox.askyesno(APP,f"{len(ids)} کالا بلاک و از همه صف‌های فعال خارج شوند؟\nخود رکورد حذف نمی‌شود و قابل بازگردانی است."):
            return
        for product_id in ids:
            self.db.block_product(product_id,reason)
            self.logger.info("PRODUCT_BLOCKED id=%s reason=%s",product_id,redact(reason))
        self.current_product=None
        self.refresh_products();self.refresh_published();self.refresh_upload_queue();self.refresh_blocked()
        self.status.set(f"{len(ids)} کالا به بخش بلاک‌شده منتقل شد")

    def refresh_blocked(self):
        tree=getattr(self,"blocked_tree",None)
        if tree is None:return
        for iid in tree.get_children():tree.delete(iid)
        for row in self.db.products("blocked"):
            tree.insert("","end",iid=str(row["id"]),values=(row["id"],row["source_code"],row["external_id"],row["title_fa"] or row["source_title"],row["blocked_at"],row["blocked_reason"]))

    def restore_selected_products(self):
        tree=getattr(self,"blocked_tree",None)
        ids=[int(iid) for iid in (tree.selection() if tree else ())]
        if not ids:
            messagebox.showwarning(APP,"حداقل یک کالای بلاک‌شده را انتخاب کنید.");return
        if not messagebox.askyesno(APP,f"{len(ids)} کالا به وضعیت بررسی بازگردانده شوند؟"):
            return
        for product_id in ids:
            self.db.restore_product(product_id)
            self.logger.info("PRODUCT_RESTORED id=%s",product_id)
        self.refresh_blocked();self.refresh_products();self.status.set("کالاهای انتخاب‌شده بازگردانی شدند")

    def load_product(self,_e=None):
        sel=self.product_tree.selection()
        if not sel:return
        # First selected row is the editor target; multi-selection remains available for bulk actions.
        self.current_product=int(sel[0]); r=self.db.product(self.current_product)
        for name,field in self.fields.items():
            value=r[name] if name in r.keys() else ""
            if name=="local_category_slug":
                value=self.category_slug_to_label.get(str(value or "external-other"),self.category_slug_to_label.get("external-other","سایر محصولات"))
            if isinstance(field,tk.Text):field.delete("1.0","end");field.insert("1.0",value or "")
            elif isinstance(field,tk.IntVar):field.set(int(value or 0))
            else:field.set("" if value is None else str(value))
        self.source_url_text.set(r["source_url"] or "")
        state=product_state(r)
        metrics=[self._rating_text(r)]
        if int(r["source_download_count"] or 0):metrics.append(f"⬇ {int(r['source_download_count']):,}")
        if int(r["source_like_count"] or 0):metrics.append(f"♥ {int(r['source_like_count']):,}")
        if int(r["source_view_count"] or 0):metrics.append(f"👁 {int(r['source_view_count']):,}")
        self.product_meta.set(
            f"{STATUS_LABELS.get(state,state)}  •  {'  '.join(metrics)}  •  عکس: {image_count(r)}  •  دریافت: {self._date_short(r['created_at'])}  •  "
            f"بازیابی: {self._date_short(r['last_refetched_at'])}  •  سایت: {self._date_short(r['last_synced_at'])}"
        )
        self.prepare_product_gallery(r)

    def _safe_json_list(self,value):
        try:
            data=json.loads(value or "[]")
            return data if isinstance(data,list) else []
        except Exception:
            return []

    def prepare_product_gallery(self,row):
        urls=self._safe_json_list(row["images_json"] if "images_json" in row.keys() else "[]")
        selected=set(self._safe_json_list(row["selected_images_json"] if "selected_images_json" in row.keys() else "[]"))
        if not selected and urls:
            selected=set(urls)
        primary=row["primary_image_url"] or ""
        if primary and primary not in urls:
            urls.insert(0,primary)
        elif primary in urls:
            urls=[primary]+[u for u in urls if u!=primary]
        manifest_map={}
        local_dir=Path(row["local_dir"] or "")
        manifest=local_dir/"page_extract.json"
        if manifest.is_file():
            try:
                payload=json.loads(manifest.read_text(encoding="utf-8"))
                for item in payload.get("images",[]):
                    if isinstance(item,dict) and item.get("url"):
                        manifest_map[item["url"]]=item.get("local_file") or ""
            except Exception:
                pass
        local_files=sorted((local_dir/"images").glob("*")) if (local_dir/"images").is_dir() else []
        items=[]
        for idx,url in enumerate(urls):
            local=manifest_map.get(url,"")
            if str(url).startswith("local://"):
                candidate=local_dir/"images"/str(url).split("local://",1)[1]
                if candidate.is_file():local=str(candidate)
            if not local and idx < len(local_files):
                local=str(local_files[idx])
            if local and not Path(local).is_file():
                local=""
            items.append({"url":url,"local":local,"selected":url in selected})
        # Legacy products may only have local images. They remain previewable but are never screenshot fallbacks.
        if not items:
            for p in local_files:
                items.append({"url":"","local":str(p),"selected":True})
        self._preview_items=items
        self._preview_urls=[item["url"] for item in items if item["url"]]
        self._preview_local=[Path(item["local"]) for item in items if item["local"]]
        self._preview_index=0
        self._update_selected_images_label()
        self.render_inline_gallery()
        self.show_preview_image()

    def _update_selected_images_label(self):
        items=getattr(self,"_preview_items",[])
        selected=sum(1 for item in items if item.get("selected"))
        self.selected_images_text.set(f"انتخاب‌شده برای سایت: {selected} از {len(items)}")

    def change_preview(self,delta):
        total=len(getattr(self,"_preview_items",[]))
        if total<1:return
        self._preview_index=(self._preview_index+delta)%total
        self.show_preview_image()

    def render_inline_gallery(self):
        frame=getattr(self,"inline_gallery",None)
        if frame is None:return
        for child in frame.winfo_children():child.destroy()
        self._inline_thumb_photos=[]
        items=list(getattr(self,"_preview_items",[]))
        if not items:
            ttk.Label(frame,text="تصویری برای نمایش نیست",style="SubHeader.TLabel").pack(side="left");return

        shell=ttk.Frame(frame)
        shell.pack(fill="x",expand=True)
        canvas=tk.Canvas(shell,height=92,highlightthickness=0,bg="#ffffff")
        hbar=ttk.Scrollbar(shell,orient="horizontal",command=canvas.xview)
        canvas.configure(xscrollcommand=hbar.set)
        canvas.pack(fill="x",expand=True)
        hbar.pack(fill="x")
        inner=ttk.Frame(canvas)
        window=canvas.create_window((0,0),window=inner,anchor="nw")
        inner.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",lambda e:canvas.itemconfigure(window,height=e.height))

        # Rendering thousands of Tk widgets freezes the editor.  The first 24
        # thumbnails stay scrollable here; the paged Product Studio manages all images.
        visible_items=items[:24]
        for idx,item in enumerate(visible_items):
            holder=ttk.Frame(inner,padding=2,style="Card.TFrame");holder.pack(side="left",padx=3,pady=2)
            lbl=ttk.Label(holder,text=str(idx+1),anchor="center",width=12)
            lbl.pack()
            lbl.bind("<Button-1>",lambda e,i=idx:self._select_inline_image(i))
            local=item.get("local") or ""
            if local and Path(local).is_file():
                try:self._apply_inline_thumb(lbl,Path(local).read_bytes())
                except Exception:pass
            elif str(item.get("url") or "").startswith(("http://","https://")):
                self._load_inline_thumb_async(lbl,item.get("url"))
        ttk.Button(inner,text=f"مدیریت همه {len(items)} عکس ←",command=self.open_image_manager,style="Primary.TButton").pack(side="left",padx=8,pady=12)

    def _select_inline_image(self,index):
        self._preview_index=int(index);self.show_preview_image()

    def _apply_inline_thumb(self,label,raw):
        try:
            img=Image.open(io.BytesIO(raw)).convert("RGB");img.thumbnail((78,58),Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(img);self._inline_thumb_photos.append(photo);label.configure(image=photo,text="")
        except Exception:pass

    def _load_inline_thumb_async(self,label,url):
        source_url=self.source_url_text.get().strip()
        def work():
            try:
                req=urllib_request.Request(url,headers={"User-Agent":"Mozilla/5.0","Referer":source_url})
                with urllib_request.urlopen(req,timeout=20) as response:raw=response.read(8_000_000)
                self.after(0,lambda:self._apply_inline_thumb(label,raw))
            except Exception:pass
        threading.Thread(target=work,daemon=True).start()

    def show_preview_image(self):
        items=getattr(self,"_preview_items",[])
        total=len(items)
        if total<1:
            self.preview_label.configure(image="",text="تصویر واقعی محصول دریافت نشده است.")
            self._preview_photo=None; self.preview_counter.set("0 / 0"); self.current_image_text.set(""); return
        index=self._preview_index%total
        item=items[index]
        self.preview_counter.set(f"{index+1} / {total} {'✓' if item.get('selected') else '✗'}")
        kind,current=self._current_preview_target()
        self._preview_current=current
        self.current_image_text.set(item.get("url") or current)
        local=item.get("local") or ""
        if local and Path(local).is_file():
            try:
                raw=Path(local).read_bytes(); self.apply_preview_bytes(raw); return
            except Exception: pass
        url=item.get("url") or ""
        if url:
            self.preview_label.configure(image="",text="در حال دریافت پیش‌نمایش تصویر اصلی...")
            def worker():
                try:
                    req=urllib_request.Request(url,headers={"User-Agent":"Mozilla/5.0","Referer":self.source_url_text.get().strip()})
                    with urllib_request.urlopen(req,timeout=25) as response:
                        raw=response.read(20_000_000)
                    self.events.put(("preview_bytes",raw))
                except Exception as exc:self.events.put(("preview_error",str(exc)))
            threading.Thread(target=worker,daemon=True).start(); return
        self.preview_label.configure(image="",text="فایل تصویر قابل نمایش نیست.")

    def apply_preview_bytes(self,raw):
        try:
            image=Image.open(io.BytesIO(raw)); image.thumbnail((360,210),Image.Resampling.LANCZOS)
            self._preview_photo=ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self._preview_photo,text="")
        except Exception as exc:
            self._preview_photo=None; self.preview_label.configure(image="",text=f"نمایش تصویر ناموفق: {exc}")

    def _current_preview_item(self):
        items=getattr(self,"_preview_items",[])
        if not items:return None
        return items[self._preview_index%len(items)]

    def _current_preview_target(self):
        item=self._current_preview_item()
        if not item:return "",""
        if item.get("local"):return "local",item["local"]
        if item.get("url"):return "remote",item["url"]
        return "",""

    def open_current_preview(self):
        item=self._current_preview_item()
        if not item:return
        value=item.get("url") or item.get("local") or ""
        if not value:return
        try:
            if value.startswith(("http://","https://")):webbrowser.open(value)
            elif os.name=="nt":os.startfile(value)
            else:__import__("subprocess").Popen(["xdg-open",value])
        except Exception as exc:messagebox.showerror(APP,str(exc))

    def _persist_image_selection(self):
        if not self.current_product:return
        items=getattr(self,"_preview_items",[])
        selected=[item.get("url") for item in items if item.get("selected") and item.get("url")]
        row=self.db.product(self.current_product)
        primary=row["primary_image_url"] or ""
        if primary and primary in selected:
            selected=[primary]+[u for u in selected if u!=primary]
        self.db.update_product(self.current_product,{"selected_images_json":json.dumps(selected,ensure_ascii=False)})
        self._update_selected_images_label()

    def toggle_current_image_selection(self):
        item=self._current_preview_item()
        if not item:return
        item["selected"]=not bool(item.get("selected"))
        self._persist_image_selection(); self.show_preview_image()

    def select_all_images(self):
        for item in getattr(self,"_preview_items",[]): item["selected"]=True
        self._persist_image_selection(); self.show_preview_image()

    def clear_image_selection(self):
        for item in getattr(self,"_preview_items",[]): item["selected"]=False
        self._persist_image_selection(); self.show_preview_image()

    def set_current_preview_primary(self):
        if not self.current_product:return
        item=self._current_preview_item()
        if not item:return
        url=item.get("url") or ""
        if not url:
            messagebox.showwarning(APP,"این تصویر URL منبع ندارد و نمی‌تواند Primary سایت باشد."); return
        item["selected"]=True
        row=self.db.product(self.current_product)
        urls=self._safe_json_list(row["images_json"])
        urls=[url]+[u for u in urls if u!=url]
        self.db.update_product(self.current_product,{"primary_image_url":url,"images_json":json.dumps(urls,ensure_ascii=False)})
        self._persist_image_selection()
        self.prepare_product_gallery(self.db.product(self.current_product))
        messagebox.showinfo(APP,"تصویر اصلی انتخاب شد و در Batch اول قرار می‌گیرد.")

    def _persist_gallery_urls(self,items):
        if not self.current_product:return
        urls=[str(item.get("url") or "") for item in items if str(item.get("url") or "")]
        selected=[str(item.get("url") or "") for item in items if item.get("selected") and str(item.get("url") or "")]
        row=self.db.product(self.current_product); primary=row["primary_image_url"] or ""
        if primary not in urls:primary=selected[0] if selected else (urls[0] if urls else "")
        if primary and primary in selected:selected=[primary]+[u for u in selected if u!=primary]
        self.db.update_product(self.current_product,{"images_json":json.dumps(urls,ensure_ascii=False),"selected_images_json":json.dumps(selected,ensure_ascii=False),"primary_image_url":primary})

    def add_local_images_to_product(self,parent=None):
        if not self.current_product:return
        paths=filedialog.askopenfilenames(parent=parent or self,title="افزودن عکس به محصول",filetypes=[("Images","*.jpg *.jpeg *.png *.webp *.gif *.avif"),("All files","*.*")])
        if not paths:return
        row=self.db.product(self.current_product); local_dir=Path(row["local_dir"] or (DATA/"collected"/row["source_code"]/row["external_id"]))
        target=local_dir/"images"; target.mkdir(parents=True,exist_ok=True)
        urls=self._safe_json_list(row["images_json"]); selected=self._safe_json_list(row["selected_images_json"])
        for src in paths:
            srcp=Path(src); stamp=int(time.time()*1000); name=f"manual_{stamp}_{srcp.name}"; dst=target/name; shutil.copy2(srcp,dst)
            pseudo=f"local://{name}"; urls.append(pseudo);selected.append(pseudo)
        self.db.update_product(self.current_product,{"local_dir":str(local_dir),"images_json":json.dumps(list(dict.fromkeys(urls)),ensure_ascii=False),"selected_images_json":json.dumps(list(dict.fromkeys(selected)),ensure_ascii=False)})
        self.prepare_product_gallery(self.db.product(self.current_product)); self.refresh_products(); self.status.set("عکس محلی به محصول اضافه شد")

    def add_image_url_to_product(self,parent=None):
        if not self.current_product:return
        url=simpledialog.askstring("افزودن URL تصویر","آدرس کامل تصویر را وارد کنید:",parent=parent or self)
        if not url:return
        url=url.strip()
        if not url.startswith(("http://","https://")):
            messagebox.showwarning(APP,"URL تصویر باید با http:// یا https:// شروع شود.",parent=parent or self);return
        row=self.db.product(self.current_product);urls=self._safe_json_list(row["images_json"]);selected=self._safe_json_list(row["selected_images_json"])
        if url not in urls:urls.append(url)
        if url not in selected:selected.append(url)
        self.db.update_product(self.current_product,{"images_json":json.dumps(urls,ensure_ascii=False),"selected_images_json":json.dumps(selected,ensure_ascii=False)})
        self.prepare_product_gallery(self.db.product(self.current_product));self.refresh_products();self.status.set("URL تصویر اضافه شد")

    def remove_current_image_from_product(self):
        if not self.current_product:return
        item=self._current_preview_item()
        if not item:return
        url=item.get("url") or ""
        if not url:return
        if not messagebox.askyesno(APP,"این تصویر فقط از محصول حذف شود؟ فایل محلی پاک نمی‌شود."):return
        row=self.db.product(self.current_product);urls=[u for u in self._safe_json_list(row["images_json"]) if u!=url];selected=[u for u in self._safe_json_list(row["selected_images_json"]) if u!=url]
        primary=row["primary_image_url"] or ""
        if primary==url:primary=selected[0] if selected else (urls[0] if urls else "")
        self.db.update_product(self.current_product,{"images_json":json.dumps(urls,ensure_ascii=False),"selected_images_json":json.dumps(selected,ensure_ascii=False),"primary_image_url":primary})
        self.prepare_product_gallery(self.db.product(self.current_product));self.refresh_products()

    def open_image_manager(self):
        if not self.current_product:
            messagebox.showwarning(APP,"ابتدا یک محصول را انتخاب کنید.")
            return
        studio=ProductStudio(self,int(self.current_product))
        studio.nb.select(studio.images_tab)
        studio.lift()
        studio.focus_force()

    def open_technical_details(self):
        if not self.current_product:return
        row=self.db.product(self.current_product)
        win=tk.Toplevel(self); win.title("مشخصات، لینک فایل‌ها و یادداشت"); win.geometry("920x680")
        frame=ttk.Frame(win,padding=10); frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="لینک اصلی صفحه").grid(row=0,column=0,sticky="w")
        source_var=tk.StringVar(value=row["source_url"] or "")
        ttk.Entry(frame,textvariable=source_var).grid(row=0,column=1,sticky="ew",padx=5)
        ttk.Button(frame,text="باز کردن",command=lambda:webbrowser.open(source_var.get().strip())).grid(row=0,column=2)
        ttk.Label(frame,text="لینک فایل‌ها / دانلودها (هر خط یک لینک)").grid(row=1,column=0,columnspan=3,sticky="w",pady=(12,3))
        files=tk.Text(frame,height=9,wrap="none"); files.grid(row=2,column=0,columnspan=3,sticky="nsew")
        file_urls=self._safe_json_list(row["selected_file_links_json"] or row["file_links_json"])
        files.insert("1.0","\n".join(file_urls))
        ttk.Label(frame,text="مشخصات استخراج‌شده").grid(row=3,column=0,columnspan=3,sticky="w",pady=(12,3))
        specs=tk.Text(frame,height=10,wrap="word"); specs.grid(row=4,column=0,columnspan=3,sticky="nsew")
        try:specs.insert("1.0",json.dumps(json.loads(row["source_specs_json"] or "{}"),ensure_ascii=False,indent=2))
        except Exception:specs.insert("1.0",row["source_specs_json"] or "")
        ttk.Label(frame,text="یادداشت داخلی").grid(row=5,column=0,columnspan=3,sticky="w",pady=(12,3))
        notes=tk.Text(frame,height=5,wrap="word"); notes.grid(row=6,column=0,columnspan=3,sticky="nsew"); notes.insert("1.0",row["custom_notes"] or "")
        def save_details():
            lines=[line.strip() for line in files.get("1.0","end").splitlines() if line.strip()]
            self.db.update_product(self.current_product,{"source_url":source_var.get().strip(),"selected_file_links_json":json.dumps(lines,ensure_ascii=False),"custom_notes":notes.get("1.0","end").strip()})
            self.source_url_text.set(source_var.get().strip()); win.destroy(); self.status.set("مشخصات ذخیره شد")
        ttk.Button(frame,text="ذخیره",command=save_details).grid(row=7,column=2,sticky="e",pady=8)
        frame.columnconfigure(1,weight=1); frame.rowconfigure(2,weight=1); frame.rowconfigure(4,weight=1); frame.rowconfigure(6,weight=1)

    def open_source_product(self):
        if not self.current_product:return
        row=self.db.product(self.current_product)
        if row and row["source_url"]:webbrowser.open(row["source_url"])

    def open_local_product_dir(self):
        if not self.current_product:return
        row=self.db.product(self.current_product); path=Path(row["local_dir"] or "") if row else None
        if not path or not path.is_dir():messagebox.showwarning(APP,"پوشه محلی پیدا نشد.");return
        try:
            if os.name=="nt":os.startfile(str(path))
            else:__import__("subprocess").Popen(["xdg-open",str(path)])
        except Exception as exc:messagebox.showerror(APP,str(exc))

    def val(self,name):
        field=self.fields[name]
        if isinstance(field,tk.Text):return field.get("1.0","end").strip()
        return field.get()

    def _float_or_none(self,value):
        try:
            text=str(value or "").replace(",","").strip()
            return float(text) if text else None
        except ValueError:return None

    def save_product(self):
        if not self.current_product:return
        weight=self._float_or_none(self.val("estimated_weight_grams"))
        per=int(self._float_or_none(self.val("material_price_per_gram")) or 0)
        suggested=int(self._float_or_none(self.val("suggested_price")) or 0)
        if suggested<=0:
            existing_for_price=self.db.product(self.current_product)
            suggested=pricing_suggestion(weight,per,existing_for_price["estimated_print_minutes"] if existing_for_price else None)
        category_label=self.val("local_category_slug")
        category_slug=self.category_label_to_slug.get(category_label,category_label or "external-other")
        existing=self.db.product(self.current_product)
        current_url=self.source_url_text.get().strip()
        vals={
            "source_url":current_url,
            "fingerprint":product_fingerprint(existing["source_code"],existing["external_id"],current_url) if existing else "",
            "source_title":self.val("source_title"),
            "title_fa":self.val("title_fa"),
            "source_description":self.val("source_description"),
            "description_fa":self.val("description_fa"),
            "local_category_slug":category_slug,
            "estimated_weight_grams":weight,
            "material_price_per_gram":per,
            "suggested_price":max(500000,suggested),
            "final_price":int(self._float_or_none(self.val("final_price")) or 0),
            "source_price":self._float_or_none(self.val("source_price")),
            "source_currency":self.val("source_currency").strip().upper(),
            "commercial_status":self.val("commercial_status") or "review",
            "workflow_status":self.val("workflow_status") or "review",
            **{n:int(self.val(n)) for n in ["price_is_final","approved_for_sale","publish_as_product","publish_as_portfolio"]},
            "short_description_fa":self.val("description_fa")[:500],
            "translation_status":"reviewed" if self.val("title_fa") and self.val("description_fa") else "pending",
            "content_status":"ready" if self.val("title_fa") and self.val("description_fa") else "pending",
        }
        self.db.update_product(self.current_product,vals)
        self.refresh_products(); self.refresh_upload_queue(); self.status.set("ذخیره شد")

    def estimate_product_price(self):
        weight=self._float_or_none(self.val("estimated_weight_grams"))
        per=self._float_or_none(self.val("material_price_per_gram"))
        if not weight or not per:
            messagebox.showwarning(APP,"برای محاسبه، وزن تقریبی و قیمت ماده به ازای هر گرم را وارد کنید."); return
        row=self.db.product(self.current_product) if self.current_product else None
        estimated=pricing_suggestion(weight,per,row["estimated_print_minutes"] if row else None)
        self.fields["suggested_price"].set(str(estimated))
        self.status.set(f"قیمت پیشنهادی: {estimated:,}")

    def approve_to_upload_queue(self):
        if not self.current_product:return
        self.save_product()
        row=self.db.product(self.current_product)
        selected=self._safe_json_list(row["selected_images_json"])
        if not selected:
            messagebox.showwarning(APP,"حداقل یک تصویر واقعی محصول را برای سایت انتخاب کنید."); return
        if not (row["title_fa"] or row["source_title"]):
            messagebox.showwarning(APP,"عنوان محصول خالی است."); return
        fp=row["fingerprint"] or product_fingerprint(row["source_code"],row["external_id"],row["source_url"])
        duplicate=self.db.find_duplicate(row["source_code"],row["external_id"],normalize_url(row["source_url"]),fp,exclude_id=self.current_product)
        if duplicate:
            messagebox.showerror(APP,f"آیتم تکراری شناسایی شد. رکورد موجود: #{duplicate['id']}\nارسال متوقف شد.");return
        if not int(row["approved_for_sale"] or 0):
            messagebox.showerror(APP,"انتشار متوقف شد. ابتدا گزینه تأیید فروش را فعال کنید.")
            return
        if not commercial_license_allows_publish(row["commercial_status"]):
            messagebox.showerror(
                APP,
                "انتشار متوقف شد. مجوز تجاری باید یکی از allowed، owned یا public_domain باشد.",
            )
            return
        self.db.update_product(self.current_product,{"upload_ready":1,"workflow_status":"approved","publish_as_product":1,"fingerprint":fp})
        if "workflow_status" in self.fields:self.fields["workflow_status"].set("approved")
        self.refresh_products(); self.refresh_upload_queue(); self.status.set("به صف آپلود اضافه شد")
        messagebox.showinfo(APP,"محصول ذخیره و به صف آپلود اضافه شد.")

    def refresh_upload_queue(self):
        tree=getattr(self,"upload_tree",None)
        if tree is None:return
        for iid in tree.get_children():tree.delete(iid)
        for r in self.db.upload_queue():
            selected=len(self._safe_json_list(r["selected_images_json"]))
            price=r["final_price"] if r["price_is_final"] else r["suggested_price"]
            title=r["title_fa"] or r["source_title"]
            tree.insert("","end",iid=str(r["id"]),values=(r["id"],r["source_code"],title,r["local_category_slug"],selected,r["estimated_weight_grams"] or "",f"{int(price or 0):,}",r["workflow_status"]))

    def remove_from_upload_queue(self):
        tree=getattr(self,"upload_tree",None)
        if tree is None:return
        for iid in tree.selection():
            self.db.update_product(int(iid),{"upload_ready":0,"workflow_status":"review"})
        self.refresh_upload_queue(); self.refresh_products()

    def publish_product_now(self, product_id=None, parent=None):
        product_id=int(product_id or self.current_product or 0)
        if not product_id:
            messagebox.showwarning(APP,"ابتدا یک محصول را انتخاب کنید.",parent=parent or self);return
        row=self.db.product(product_id)
        if row is None:
            messagebox.showerror(APP,"محصول انتخاب‌شده پیدا نشد.",parent=parent or self);return
        if not int(row["upload_ready"] or 0):
            if product_id != self.current_product:
                messagebox.showwarning(APP,"محصول هنوز آماده انتشار نیست. در استودیوی محصول ابتدا اطلاعات را تأیید کنید.",parent=parent or self);return
            self.approve_to_upload_queue()
            row=self.db.product(product_id)
            if row is None or not int(row["upload_ready"] or 0):return
        try:
            self._site_connection(require_bridge=True)
            result=self.build_batch(product_ids=[product_id],quiet=True)
        except Exception as exc:
            self.db.update_product(product_id,{"product_sync_error":f"{type(exc).__name__}: {exc}"[:1000]})
            self.db.record_sync_receipt(product_id,"","desktop_batch_failed","",{"error":f"{type(exc).__name__}: {exc}"})
            self.logger.exception("PRODUCT_PUBLISH_PREP_FAILED product_id=%s error=%s",product_id,redact(exc))
            messagebox.showerror(APP,f"ارسال محصول قبل از FTP متوقف شد:\n{type(exc).__name__}: {exc}\n\nجزئیات در گزارش ارسال ثبت شد.",parent=parent or self)
            return
        self.db.record_sync_receipt(product_id,result["batch_uuid"],"desktop_batch_ready","",{
            "batch_name":result["batch"].name,
            "models":result["validation"].get("models"),
            "images":result["validation"].get("images"),
        })
        self.status.set(f"ارسال محصول #{product_id} شروع شد")
        self.upload_last_batch()

    def open_current_publish_log(self):
        product_id=int(self.current_product or 0)
        if not product_id:
            messagebox.showwarning(APP,"ابتدا یک محصول را انتخاب کنید.");return
        win=tk.Toplevel(self);win.title(f"گزارش ارسال محصول #{product_id}");win.geometry("1040x720")
        top=ttk.Frame(win,padding=10);top.pack(fill="x")
        ttk.Label(top,text="Windows → Batch → FTP → Bridge → Import → Store",style="Header.TLabel").pack(side="left")
        text=tk.Text(win,wrap="word",font=("Consolas",10));text.pack(fill="both",expand=True,padx=10,pady=(0,10))
        def refresh():
            row=self.db.product(product_id);receipts=self.db.sync_receipts(product_id,limit=30)
            text.delete("1.0","end");text.insert("1.0",receipt_lines(row,receipts));text.see("1.0")
        def open_site():
            row=self.db.product(product_id)
            try:ack=json.loads(row["server_ack_json"] or "{}")
            except Exception:ack={}
            path=str(ack.get("product_url") or "")
            if path:webbrowser.open(self.site_url.get().rstrip("/")+path)
            else:messagebox.showwarning(APP,"لینک محصول هنوز از سرور دریافت نشده است.",parent=win)
        def fetch_server_log():
            receipts=self.db.sync_receipts(product_id,limit=30)
            batch_name=""
            for receipt in receipts:
                try:payload=json.loads(receipt["payload_json"] or "{}")
                except Exception:payload={}
                candidate=str(payload.get("diagnostic_id") or payload.get("batch_name") or "")
                if candidate.startswith("desktop_catalog_v85_"):
                    batch_name=candidate;break
            if not batch_name:
                messagebox.showwarning(APP,"شناسه Diagnostic برای این محصول هنوز ثبت نشده است.",parent=win);return
            try:cfg=self._site_connection(require_bridge=True)
            except Exception as exc:messagebox.showerror(APP,str(exc),parent=win);return
            def work():
                try:
                    diagnostic=get_batch_diagnostic(cfg,batch_name)
                    rendered="\n\n=== HOST DIAGNOSTIC ===\n"+json.dumps(diagnostic,ensure_ascii=False,indent=2)
                    self.after(0,lambda:(text.insert("end",rendered),text.see("end")))
                except Exception as exc:
                    self.after(0,lambda:messagebox.showerror(APP,f"دریافت لاگ سرور ناموفق بود:\n{type(exc).__name__}: {exc}",parent=win))
            threading.Thread(target=work,daemon=True).start()
        ttk.Button(top,text="تازه‌سازی",command=refresh).pack(side="right",padx=3)
        ttk.Button(top,text="لاگ سرور",command=fetch_server_log).pack(side="right",padx=3)
        ttk.Button(top,text="پوشه لاگ",command=self.open_log_folder).pack(side="right",padx=3)
        ttk.Button(top,text="باز کردن محصول سایت",command=open_site).pack(side="right",padx=3)
        refresh()

    def translate_product(self):
        if not self.current_product:return
        translation_provider=self.translation_provider.get(); title=self.val("source_title"); desc=self.val("source_description")
        def work():
            try:
                if translation_provider=="google":
                    tf=google_translate(title,self.google_key.get()); df=google_translate(desc,self.google_key.get())
                else:
                    provider=self._selected_ai_provider(); key=self._ai_key(provider)
                    if not key: raise RuntimeError(f"API Key برای {provider} پیدا نشد.")
                    source={"source_title":title,"source_description":desc,"source_categories":[],"source_specs":{},"source_tags":[]}
                    pack=AIContentService(key,self.ai_model.get().strip(),provider).enrich_product(source,list(self.config.get("local_categories") or []),mode="translate")
                    tf=pack.get("title_fa") or ""; df=pack.get("description_fa") or pack.get("short_description_fa") or ""
                self.events.put(("translation",(tf,df)))
            except Exception as e:self.events.put(("error",str(e)))
        threading.Thread(target=work,daemon=True).start(); self.status.set("در حال ترجمه")

    def _download_batch_image(self,url,target,referer):
        self.log(f"BATCH_IMAGE_FETCH {url}")
        return download_public_file(url,target,max_bytes=20_000_000,referer=referer or url)

    def _selected_batch_images(self,row):
        src=Path(row["local_dir"] or "")
        return materialize_selected_images(row,src,downloader=self._download_batch_image)

    def build_batch(self, product_ids=None, quiet=False):
        if product_ids is None and self.current_product:
            self.save_product()
        rows=self.db.exportable()
        if product_ids is not None:
            wanted={int(x) for x in product_ids}
            rows=[r for r in rows if int(r["id"]) in wanted]
        if not rows:
            message="محصول آماده‌ای برای Batch انتخاب‌شده وجود ندارد. ابتدا اطلاعات، تصاویر، قیمت و مجوز را تأیید کنید."
            if quiet:raise RuntimeError(message)
            messagebox.showwarning(APP,message); return None
        batch_uuid=new_batch_uuid()
        name="desktop_catalog_v85_"+time.strftime("%Y%m%d_%H%M%S")
        batch=BATCH_ROOT/name
        building=BATCH_ROOT/(name+".building")
        if batch.exists() or building.exists():
            message=f"مسیر Batch از قبل وجود دارد:\n{batch}"
            if quiet:raise RuntimeError(message)
            messagebox.showerror(APP,message); return None
        models=building/"models"; manifest=[]; batched_ids=[]
        try:
            models.mkdir(parents=True,exist_ok=False)
            for r in rows:
                target=models/f"{r['source_code']}_{r['external_id']}"; target.mkdir(parents=True,exist_ok=False)
                src=Path(r["local_dir"] or "")
                if src.is_dir():
                    for f in src.iterdir():
                        if not f.is_file():continue
                        if f.suffix.lower() in {".png",".jpg",".jpeg",".webp",".gif",".avif"}:continue
                        shutil.copy2(f,target/f.name)
                selected_pairs=self._selected_batch_images(r)
                selected_urls=[url for url,_ in selected_pairs]
                local_image_files=copy_images_into_model(selected_pairs,target)
                copied=len(local_image_files)
                editorial={k:r[k] for k in r.keys() if k not in {"id","created_at","updated_at"}}
                editorial["desktop_product_id"]=int(r["id"])
                editorial["batch_uuid"]=batch_uuid
                editorial["local_category_name"]=self.category_slug_to_label.get(r["local_category_slug"],r["local_category_slug"] or "سایر محصولات")
                editorial["fingerprint"]=r["fingerprint"] or product_fingerprint(r["source_code"],r["external_id"],r["source_url"])
                editorial["source_hash"]=r["source_hash"] or source_payload_hash(editorial)
                editorial["images_json"]=json.dumps(selected_urls,ensure_ascii=False)
                editorial["selected_images_json"]=json.dumps(selected_urls,ensure_ascii=False)
                editorial["primary_image_url"]=selected_urls[0] if selected_urls else ""
                editorial["local_image_files_json"]=json.dumps(local_image_files,ensure_ascii=False)
                editorial["workflow_status"]="batched"
                editorial["batch_local_image_count"]=copied
                (target/"desktop_editorial.json").write_text(json.dumps(editorial,ensure_ascii=False,indent=2),encoding="utf-8")
                manifest.append({
                    "desktop_product_id":int(r["id"]),"source_code":r["source_code"],"external_id":r["external_id"],
                    "editorial":f"models/{target.name}/desktop_editorial.json","selected_images":len(selected_urls),
                    "local_images":copied,"fingerprint":editorial["fingerprint"],"source_hash":editorial["source_hash"],
                })
                batched_ids.append(r["id"])
            (building/"batch_manifest.json").write_text(json.dumps({"schema_version":"8.5","batch_uuid":batch_uuid,"batch_name":name,"models":manifest},ensure_ascii=False,indent=2),encoding="utf-8")
            validation=validate_batch_package(building)
            building.rename(batch)
        except Exception as exc:
            shutil.rmtree(building,ignore_errors=True)
            self.logger.exception("BATCH_BUILD_FAILED name=%s error=%s",name,redact(exc))
            self.log(f"BATCH_BUILD_FAILED {redact(exc)}")
            if quiet:
                raise
            if isinstance(exc,BatchImagePackagingError) or "IMAGE_NOT_PACKAGED" in str(exc):
                messagebox.showerror(APP,"ساخت Batch متوقف شد چون تصویر محلی کامل نیست.\n\n"+str(exc)+"\n\nهیچ Batch ناقصی برای FTP ساخته نشد.")
            else:
                messagebox.showerror(APP,f"ساخت Batch ناموفق بود:\n{exc}")
            return None
        for product_id in batched_ids:self.db.update_product(product_id,{"workflow_status":"batched"})
        self.db.set_setting("last_batch_dir",str(batch)); self.db.set_setting("last_batch_uuid",batch_uuid)
        self.refresh_products(); self.refresh_upload_queue()
        result={"batch":batch,"batch_uuid":batch_uuid,"validation":validation,"product_ids":[int(x) for x in batched_ids]}
        if not quiet:
            messagebox.showinfo(APP,f"Batch v8.5 ساخته و اعتبارسنجی شد:\n{batch}\n\nمحصولات: {validation['models']}\nتصاویر محلی: {validation['images']}\nBatch UUID: {batch_uuid}")
        return result

    def save_settings(self):
        for k,v in [("google_api_key",self.google_key.get()),
                    ("translation_provider",self.translation_provider.get()),
                    ("ai_provider",self.ai_provider.get()),("ai_model",self.ai_model.get()),("openai_model",self.ai_model.get())]:
            self.db.set_setting(k,v)
        self.db.set_setting("openai_api_key","")
        messagebox.showinfo(APP,"تنظیمات هوش مصنوعی ذخیره شد. اطلاعات حساس داخل SQLite ذخیره نمی‌شوند.")

    def _refresh_connection_secret_source(self):
        if hasattr(self,"connection_secret_source"):
            ftp_source=env_source("CATALOG_FTP_PASSWORD") if env_value("CATALOG_FTP_PASSWORD") else secret_source("ftp_password")
            bridge_source=env_source("CATALOG_BRIDGE_TOKEN") if env_value("CATALOG_BRIDGE_TOKEN") else secret_source("bridge_token")
            self.connection_secret_source.set(f"رمز FTP: {ftp_source} | توکن Bridge: {bridge_source}")

    def _site_connection(self,require_bridge=True):
        password=self.ftp_password.get().strip() or env_value("CATALOG_FTP_PASSWORD") or get_secret("ftp_password")
        token=self._entered_bridge_token() or env_value("CATALOG_BRIDGE_TOKEN") or get_secret("bridge_token")
        try:port=int(self.ftp_port.get().strip() or "21")
        except ValueError:raise ValueError("پورت FTP باید عدد باشد.")
        cfg=SiteConnection(
            ftp_host=self.ftp_host.get(),ftp_port=port,ftp_user=self.ftp_user.get(),ftp_password=password,
            remote_root=self.ftp_remote_root.get(),site_url=self.site_url.get(),bridge_token=token,
        ).normalized()
        if not all([cfg.ftp_host,cfg.ftp_user,cfg.ftp_password]):
            raise ValueError("Host، Username و Password اتصال FTP باید کامل باشند.")
        if require_bridge and not all([cfg.site_url,cfg.bridge_token]):
            raise ValueError("آدرس سایت و Bridge Token باید کامل باشند.")
        return cfg

    def save_connection_settings(self):
        try:
            cfg=self._site_connection(require_bridge=False)
            for key,value in [
                ("ftp_protocol","FTP"),("ftp_host",cfg.ftp_host),("ftp_port",str(cfg.ftp_port)),
                ("ftp_user",cfg.ftp_user),("ftp_remote_root",cfg.remote_root),("site_url",cfg.site_url),
            ]:self.db.set_setting(key,value)
            if self.ftp_password.get().strip():set_secret("ftp_password",self.ftp_password.get())
            entered_token=self._entered_bridge_token()
            if entered_token:set_secret("bridge_token",entered_token)
            self.ftp_password.set("");self.bridge_token.set("")
            self._refresh_connection_secret_source()
            self.logger.info("CONNECTION_SETTINGS_SAVED host=%s port=%s remote_root=%s site=%s",cfg.ftp_host,cfg.ftp_port,cfg.remote_root,cfg.site_url)
            messagebox.showinfo(APP,"تنظیمات اتصال ذخیره شد. رمز FTP و توکن Bridge در Windows Credential Store قرار گرفتند.")
        except Exception as exc:
            self.logger.exception("CONNECTION_SETTINGS_SAVE_FAILED %s",redact(exc))
            messagebox.showerror(APP,f"ذخیره تنظیمات ناموفق بود:\n{exc}")

    def test_ftp_connection(self):
        try:
            cfg=self._site_connection(require_bridge=False)
            result=test_ftp(cfg)
            self.logger.info("FTP_TEST_OK host=%s port=%s remote=%s",cfg.ftp_host,cfg.ftp_port,result.get("remote_path"))
            messagebox.showinfo(APP,f"اتصال FTP موفق است.\nHost: {cfg.ftp_host}:{cfg.ftp_port}\nRemote: {result.get('remote_path')}")
        except Exception as exc:
            self.logger.exception("FTP_TEST_FAILED %s",redact(exc))
            messagebox.showerror(APP,f"تست FTP ناموفق بود:\n{type(exc).__name__}: {exc}\n\nجزئیات در:\n{self.log_path}")

    def test_site_connection(self):
        try:
            cfg=self._site_connection(require_bridge=True)
            result=test_bridge(cfg)
            self.logger.info("BRIDGE_TEST_OK response=%s",redact(result))
            messagebox.showinfo(APP,f"Bridge سایت آماده است.\nنسخه: {result.get('version','—')}\nوضعیت: {result.get('status','ok')}")
        except Exception as exc:
            self.logger.exception("BRIDGE_TEST_FAILED %s",redact(exc))
            messagebox.showerror(APP,f"تست Bridge ناموفق بود:\n{type(exc).__name__}: {exc}\n\nجزئیات در:\n{self.log_path}")

    def open_log_folder(self):
        try:os.startfile(str(self.log_path.parent))
        except Exception as exc:messagebox.showerror(APP,str(exc))

    def publish_queue_to_site(self):
        """Build a fresh batch and send it through the existing FTP + Bridge ACK workflow."""
        rows=self.db.exportable()
        if not rows:
            messagebox.showwarning(APP,"صف انتشار خالی است. ابتدا محصول را تأیید و به صف انتشار اضافه کنید.")
            return
        if not messagebox.askyesno(
            APP,
            f"{len(rows)} محصول آماده انتشار است.\n\n"
            "یک Batch جدید ساخته شود و سپس از طریق FTP به سایت ارسال و با Bridge Import ثبت شود؟"
        ):
            return
        self.logger.info("ONE_CLICK_PUBLISH_REQUEST count=%s",len(rows))
        self.status.set("در حال ساخت Batch برای انتشار")
        self.build_batch()
        batch=Path(self.db.setting("last_batch_dir") or "")
        if not batch.is_dir():
            messagebox.showerror(APP,"Batch ساخته نشد؛ ارسال متوقف شد.")
            self.status.set("ساخت Batch ناموفق")
            return
        self.status.set("Batch آماده است؛ شروع ارسال به سایت")
        self.upload_last_batch()

    def _batch_product_ids(self,batch):
        try:
            payload=json.loads((Path(batch)/"batch_manifest.json").read_text(encoding="utf-8"))
            return [int(item.get("desktop_product_id")) for item in payload.get("models",[]) if item.get("desktop_product_id")]
        except Exception:
            return []

    def _record_batch_stage(self,batch,batch_uuid,status,payload=None):
        for pid in self._batch_product_ids(batch):
            self.db.record_sync_receipt(pid,batch_uuid,status,"",payload or {"batch_name":Path(batch).name})

    def upload_last_batch(self):
        batch=Path(self.db.setting("last_batch_dir"))
        if not batch.is_dir(): messagebox.showwarning(APP,"Batch ساخته نشده است."); return
        try:cfg=self._site_connection(require_bridge=True)
        except Exception as exc:messagebox.showwarning(APP,str(exc));return
        batch_uuid=self.db.setting("last_batch_uuid")
        product_ids=self._batch_product_ids(batch)
        self._record_batch_stage(batch,batch_uuid,"desktop_publish_started",{"batch_name":batch.name,"stage":"publish_start"})
        def work():
            try:
                self.logger.info("PUBLISH_START batch=%s uuid=%s",batch.name,batch_uuid)
                result=upload_batch(cfg,batch,lambda line:(self.logger.info(redact(line)),self.events.put(("log",line))))
                self.logger.info("FTP_UPLOAD_OK batch=%s files=%s remote=%s",batch.name,result["uploaded_files"],result["remote_batch"])
                self._record_batch_stage(batch,batch_uuid,"desktop_ftp_uploaded",result)
                ack=import_batch(cfg,batch.name,batch_uuid)
                self.logger.info("BRIDGE_IMPORT_ACK batch=%s ack=%s",batch.name,redact(ack))
                self.events.put(("upload_v8",(0,json.dumps(ack,ensure_ascii=False),"",ack)))
            except Exception as exc:
                error=f"{type(exc).__name__}: {exc}"
                self.logger.exception("PUBLISH_FAILED batch=%s error=%s",batch.name,redact(exc))
                for pid in product_ids:
                    self.db.record_sync_receipt(pid,batch_uuid,"desktop_publish_failed","",{"batch_name":batch.name,"error":error})
                    self.db.update_product(pid,{"server_status":"failed","product_sync_error":error[:1000],"last_synced_at":utc_now()})
                self.events.put(("error",f"انتشار ناموفق بود: {error}\nجزئیات: {self.log_path}"))
                self.events.put(("refresh",None))
        threading.Thread(target=work,daemon=True).start(); self.status.set("FTP Upload + Import Bridge + انتظار ACK سایت")

    def refresh_runs(self):
        for i in self.runs_tree.get_children():self.runs_tree.delete(i)
        for r in self.db.runs():
            self.runs_tree.insert("","end",values=(r["id"],r["source_code"],r["mode"],r["method"],r["status"],r["discovered_count"],r["collected_count"],r["duplicate_count"],r["failed_count"],r["started_at"],r["message"]))

    def poll(self):
        try:
            while True:
                typ,payload=self.events.get_nowait()
                if typ=="log":self.scan_log.insert("end",payload+"\n");self.scan_log.see("end")
                elif typ=="error":messagebox.showerror(APP,payload);self.status.set("خطا")
                elif typ=="refresh":self.refresh_products();self.refresh_published();self.refresh_upload_queue();self.refresh_runs();self.status.set("پایان")
                elif typ=="translation":
                    tf,df=payload;self.fields["title_fa"].set(tf);self.fields["description_fa"].delete("1.0","end");self.fields["description_fa"].insert("1.0",df)
                elif typ=="ai_models":
                    provider,models=payload; self.ai_model_box["values"]=models
                    if models and self.ai_model.get() not in models:
                        preferred=next((m for m in ("gpt-5.4-mini","gpt-5-mini","gpt-5.4","gpt-5") if m in models),models[0]);self.ai_model.set(preferred)
                    self.status.set(f"{len(models)} مدل {provider} دریافت شد")
                elif typ=="openai_test":
                    self.status.set("AI متصل است"); self.header_badge.set("AI • Connected"); messagebox.showinfo(APP,payload)
                elif typ=="ai_content":
                    product_id,pack=payload; self._apply_ai_pack(product_id,pack); self.status.set("پکیج محتوایی OpenAI آماده شد"); self.header_badge.set(f"v{APP_VERSION} • آماده")
                elif typ=="bulk_ai_item":
                    product_id,pack,index,total=payload
                    self._apply_ai_pack(product_id,pack,open_studio=False)
                    row=self.db.product(product_id)
                    if row:
                        price=pricing_suggestion(row["estimated_weight_grams"],row["material_price_per_gram"],row["estimated_print_minutes"])
                        self.db.update_product(product_id,{"suggested_price":price})
                    self.status.set(f"AI گروهی: {index} از {total}")
                elif typ=="bulk_ai_done":
                    success,failed,total=payload
                    self.refresh_products();self.refresh_published();self.header_badge.set(f"v{APP_VERSION} • آماده");self.status.set("AI گروهی پایان یافت")
                    messagebox.showinfo(APP,f"تولید محتوا پایان یافت.\nموفق: {success}\nخطا: {failed}\nکل: {total}")
                elif typ=="bulk_refetch_progress":
                    index,total=payload;self.status.set(f"بازیابی گروهی: {index} از {total}")
                elif typ=="bulk_refetch_done":
                    changed,unchanged,failed,total=payload;self.refresh_products();self.refresh_published();self.status.set("بازیابی گروهی پایان یافت")
                    messagebox.showinfo(APP,f"بازیابی گروهی تمام شد.\nتغییرکرده: {changed}\nبدون تغییر: {unchanged}\nخطا: {failed}\nکل: {total}")
                elif typ=="refetch_ready":
                    product_id,fresh,diff=payload
                    summary=diff_summary(diff)
                    prompt=("بازیابی کامل انجام شد. تغییرات پیدا شده:\n\n"+summary+
                            "\n\nتغییرات منبع اعمال شوند؟\nویرایش‌های فارسی/قیمت/تأییدهای شما حفظ می‌شوند.")
                    if messagebox.askyesno(APP,prompt):
                        self._accept_refetch(product_id,fresh,diff)
                    else:
                        self.status.set("بازیابی بررسی شد؛ تغییرات اعمال نشد"); self.header_badge.set(f"v{APP_VERSION} • آماده")
                elif typ=="source_refresh_done":
                    code,changed,unchanged,failed=payload
                    self.refresh_products(); self.status.set("بروزرسانی منبع تمام شد"); self.header_badge.set(f"v{APP_VERSION} • آماده")
                    messagebox.showinfo(APP,f"منبع {code} بروزرسانی شد.\nتغییرکرده: {changed}\nبدون تغییر: {unchanged}\nخطا: {failed}")
                elif typ=="upload_v8":
                    status,out_text,err_text,ack=payload
                    if not ack:
                        messagebox.showerror(APP,"سایت ACK ساختاریافته برنگرداند؛ هیچ محصولی Uploaded علامت نخورد.\n\n"+(err_text or out_text)[-4000:])
                        self.status.set("ACK دریافت نشد")
                    else:
                        batch_uuid=ack.get("batch_uuid") or self.db.setting("last_batch_uuid")
                        success=failed=visible_count=0
                        product_links=[]
                        for item in ack.get("items") or []:
                            pid=item.get("desktop_product_id")
                            state=str(item.get("status") or "")
                            server_id=str(item.get("server_id") or "")
                            if pid:
                                item_payload=dict(item)
                                item_payload["diagnostic_id"]=ack.get("diagnostic_id") or ""
                                item_payload["bridge_status"]=ack.get("bridge_status") or ""
                                item_payload["batch_name"]=ack.get("diagnostic_id") or ""
                                self.db.record_sync_receipt(pid,batch_uuid,state,server_id,item_payload)
                                now=utc_now(); row_now=self.db.product(pid)
                                values={"server_id":server_id,"server_status":state,"server_ack_json":json.dumps(item_payload,ensure_ascii=False),"last_synced_at":now}
                                if row_now is not None and ack_item_confirms_publish(item,row_now,require_store_visibility=True):
                                    values.update({"workflow_status":"uploaded","upload_ready":0,"needs_update":0,"product_sync_error":"",
                                                   "published_at":row_now["published_at"] or now,"last_synced_source_hash":item.get("source_hash") or row_now["source_hash"] or ""}); success+=1
                                    if item.get("visible_on_store") is True:
                                        visible_count+=1
                                    if item.get("product_url"):
                                        product_links.append(str(item.get("product_url")))
                                else:
                                    values["product_sync_error"]=str(
                                        item.get("error")
                                        or "ACK received, but the requested product/portfolio was not created."
                                    )[:1000]; failed+=1
                                self.db.update_product(pid,values)
                        self.refresh_upload_queue(); self.refresh_products(); self.status.set("ACK سایت دریافت شد")
                        msg=f"ACK سایت دریافت شد.\nموفق/ثبت‌شده: {success}\nقابل نمایش در فروشگاه: {visible_count}\nناموفق: {failed}\nBatch: {batch_uuid}"
                        if product_links:
                            msg += "\nلینک: " + self.site_url.get().rstrip("/") + product_links[0]
                        if status==0:
                            messagebox.showinfo(APP,msg)
                        else:
                            messagebox.showwarning(APP,msg+"\n\n"+(err_text or out_text)[-2500:])
                elif typ=="focus_product":
                    code,external_id=payload
                    self.refresh_products()
                    row=self.db.conn.execute("SELECT id FROM products WHERE source_code=? AND external_id=? ORDER BY id DESC LIMIT 1",(code,external_id)).fetchone()
                    if row and self.product_tree.exists(str(row["id"])):
                        self.product_tree.selection_set(str(row["id"])); self.product_tree.focus(str(row["id"])); self.product_tree.see(str(row["id"])); self.load_product()
                elif typ=="preview_bytes":self.apply_preview_bytes(payload)
                elif typ=="preview_error":self.preview_label.configure(image="",text=f"پیش‌نمایش آنلاین ناموفق: {payload}")
        except queue.Empty:pass
        self.after(250,self.poll)

def main():
    App().mainloop()
if __name__=="__main__":main()
