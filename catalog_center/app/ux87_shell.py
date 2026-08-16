from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .env_settings import ENV_FILE, env_value
from .secure_secrets import get_provider_key, get_secret, set_secret
from .ux87_icons import IconRegistry
from .product_workspace_v87 import ProductWorkspace
from .version import APP_VERSION, BUILD_ID


NAV_ITEMS = [
    ("dashboard", "داشبورد", "dashboard"),
    ("products", "محصولات", "products"),
    ("discover", "دریافت و کشف", "discover"),
    ("publish", "صف انتشار", "publish"),
    ("published", "منتشرشده‌ها", "published"),
    ("blocked", "بلاک‌شده‌ها", "blocked"),
    ("logs", "گزارش و خطا", "logs"),
    ("ai", "هوش مصنوعی", "ai"),
    ("connection", "اتصال سایت", "connection"),
    ("settings", "تنظیمات", "settings"),
]


def build_app_class(BaseApp):
    class CatalogCenterApp87(BaseApp):
        UX_VERSION = "8.7"

        def _style(self):
            super()._style()
            style = ttk.Style(self)
            try:
                style.layout("Shell87.TNotebook.Tab", [])
            except Exception:
                pass
            style.configure("Shell87.TNotebook", borderwidth=0, background="#f4f7fa")
            style.configure("UX87Title.TLabel", font=("Tahoma", 18, "bold"), foreground="#071827", background="#f4f7fa")
            style.configure("UX87Section.TLabel", font=("Tahoma", 12, "bold"), foreground="#102a43", background="#f4f7fa")
            style.configure("UX87Muted.TLabel", font=("Tahoma", 9), foreground="#64748b", background="#f4f7fa")
            style.configure("UX87Card.TFrame", background="#ffffff", borderwidth=1, relief="solid")

        def _ui(self):
            self._init_ux87_settings_state()
            self._icons = IconRegistry(self, 20)
            self._nav_buttons = {}
            self._pages = {}

            header = tk.Frame(self, bg="#071827", padx=16, pady=10)
            header.pack(fill="x")
            if getattr(self, "_brand_logo", None) is not None:
                logo = tk.Label(header, image=self._brand_logo, bg="#071827", borderwidth=0)
                logo.pack(side="left", padx=(0, 14))
            title = tk.Frame(header, bg="#071827")
            title.pack(side="left", fill="x", expand=True)
            tk.Label(title, text="3DPrintHub Catalog Center", bg="#071827", fg="white", font=("Tahoma", 17, "bold")).pack(anchor="w")
            tk.Label(title, text=f"Windows UX Rebuild • v{APP_VERSION} • BUILD {BUILD_ID}", bg="#071827", fg="#b9c8d6", font=("Tahoma", 9)).pack(anchor="w", pady=(2, 0))

            status_box = tk.Frame(header, bg="#071827")
            status_box.pack(side="right")
            self.ux87_ai_status = tk.StringVar(value="AI: در حال بررسی")
            self.ux87_site_status = tk.StringVar(value="سایت: در حال بررسی")
            tk.Label(status_box, textvariable=self.ux87_ai_status, bg="#123452", fg="#d9e4ee", padx=10, pady=5, font=("Tahoma", 9, "bold")).pack(side="left", padx=3)
            tk.Label(status_box, textvariable=self.ux87_site_status, bg="#123452", fg="#d9e4ee", padx=10, pady=5, font=("Tahoma", 9, "bold")).pack(side="left", padx=3)

            shell = tk.Frame(self, bg="#f4f7fa")
            shell.pack(fill="both", expand=True)
            sidebar = tk.Frame(shell, bg="#0b2238", width=205, padx=8, pady=10)
            sidebar.pack(side="right", fill="y")
            sidebar.pack_propagate(False)
            content = ttk.Frame(shell)
            content.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=8)

            self.main_notebook = ttk.Notebook(content, style="Shell87.TNotebook")
            self.main_notebook.pack(fill="both", expand=True)
            self.dashboard_tab = ttk.Frame(self.main_notebook, padding=14)
            self.products_tab = ttk.Frame(self.main_notebook, padding=10)
            self.scan_tab = ttk.Frame(self.main_notebook, padding=10)
            self.upload_tab = ttk.Frame(self.main_notebook, padding=10)
            self.published_tab = ttk.Frame(self.main_notebook, padding=10)
            self.blocked_tab = ttk.Frame(self.main_notebook, padding=10)
            self.runs_tab = ttk.Frame(self.main_notebook, padding=10)
            self.ai_tab = ttk.Frame(self.main_notebook, padding=14)
            self.connection_tab = ttk.Frame(self.main_notebook, padding=14)
            self.settings_tab = ttk.Frame(self.main_notebook, padding=14)
            page_defs = [
                ("dashboard", self.dashboard_tab), ("products", self.products_tab),
                ("discover", self.scan_tab), ("publish", self.upload_tab),
                ("published", self.published_tab), ("blocked", self.blocked_tab),
                ("logs", self.runs_tab), ("ai", self.ai_tab),
                ("connection", self.connection_tab), ("settings", self.settings_tab),
            ]
            for key, page in page_defs:
                self._pages[key] = page
                self.main_notebook.add(page, text="")

            tk.Label(sidebar, text="مرکز مدیریت", bg="#0b2238", fg="#f6d77a", font=("Tahoma", 11, "bold")).pack(anchor="e", padx=8, pady=(2, 8))
            for key, label, icon_name in NAV_ITEMS:
                icon = self._icons.get(icon_name)
                button = tk.Button(
                    sidebar,
                    text=label,
                    image=icon,
                    compound="right",
                    command=lambda k=key: self.show_ux87_page(k),
                    anchor="e",
                    relief="flat", bd=0,
                    bg="#0b2238", fg="#d9e4ee",
                    activebackground="#123452", activeforeground="white",
                    font=("Tahoma", 9, "bold"), padx=10, pady=8,
                    cursor="hand2",
                )
                button.image = icon
                button.pack(fill="x", pady=1)
                self._nav_buttons[key] = button

            tk.Frame(sidebar, bg="#29445e", height=1).pack(fill="x", pady=10)
            tk.Label(sidebar, text="داده‌ها و Secretها\nبین Releaseها حفظ می‌شوند", bg="#0b2238", fg="#91a4b5", justify="right", font=("Tahoma", 8)).pack(anchor="e", padx=8)

            self._build_ux87_dashboard()
            super()._products_ui()
            self._modernize_products_page()
            super()._scan_ui()
            super()._upload_ui()
            super()._published_ui()
            super()._blocked_ui()
            super()._runs_ui()
            self._build_ux87_ai_center()
            self._build_ux87_connection_center()
            self._build_ux87_general_settings()
            self._sanitize_legacy_button_texts()

            self.status = tk.StringVar(value="آماده")
            footer = tk.Frame(self, bg="#071827", padx=12, pady=6)
            footer.pack(fill="x")
            tk.Label(footer, textvariable=self.status, bg="#071827", fg="#f6d77a", anchor="w", font=("Tahoma", 9)).pack(side="left", fill="x", expand=True)
            tk.Label(footer, text="Data: %LOCALAPPDATA%\\3DPrintHub\\CatalogCenter", bg="#071827", fg="#91a4b5", font=("Consolas", 8)).pack(side="right")
            self.show_ux87_page("dashboard")

        def _migrate_legacy_google_key(self) -> str:
            env_key = env_value("GOOGLE_API_KEY", "").strip()
            secure_key = get_secret("google_api_key").strip()
            legacy_key = str(self.db.setting("google_api_key", "") or "").strip()
            if secure_key or env_key:
                if legacy_key:
                    self.db.set_setting("google_api_key", "")
                return env_key or secure_key
            if not legacy_key:
                return ""
            try:
                set_secret("google_api_key", legacy_key)
            except Exception:
                return legacy_key
            self.db.set_setting("google_api_key", "")
            return legacy_key

        def _init_ux87_settings_state(self):
            self.ai_provider = tk.StringVar(value=env_value("CATALOG_AI_PROVIDER", self.db.setting("ai_provider", self.config.get("ai", {}).get("provider", "auto"))))
            if self.ai_provider.get() not in {"auto", "avalai", "openai"}:
                self.ai_provider.set("auto")
            self.ai_model = tk.StringVar(value=env_value("CATALOG_AI_MODEL", self.db.setting("ai_model", self.config.get("ai", {}).get("model", ""))))
            self.openai_model = self.ai_model
            self.ai_key = tk.StringVar(value="")
            self.openai_key = self.ai_key
            self.google_key = tk.StringVar(value=self._migrate_legacy_google_key())
            self.translation_provider = tk.StringVar(value=self.db.setting("translation_provider", "ai"))
            if self.translation_provider.get() not in {"ai", "google"}:
                self.translation_provider.set("ai")
            self.ftp_protocol = tk.StringVar(value="FTP")
            self.ftp_host = tk.StringVar(value=env_value("CATALOG_FTP_HOST", self.db.setting("ftp_host", "ftp.3dprinthub.ir")))
            self.ftp_port = tk.StringVar(value=env_value("CATALOG_FTP_PORT", self.db.setting("ftp_port", "21")))
            self.ftp_user = tk.StringVar(value=env_value("CATALOG_FTP_USER", self.db.setting("ftp_user", "sfkilvrs")))
            self.ftp_password = tk.StringVar(value=env_value("CATALOG_FTP_PASSWORD", ""))
            self.ftp_remote_root = tk.StringVar(value=env_value("CATALOG_FTP_REMOTE_ROOT", self.db.setting("ftp_remote_root", "/3dprinthub")))
            self.site_url = tk.StringVar(value=env_value("CATALOG_SITE_URL", self.db.setting("site_url", "https://3dprinthub.ir")))
            self.bridge_token = tk.StringVar(value=env_value("CATALOG_BRIDGE_TOKEN", ""))

        def _build_ux87_dashboard(self):
            ttk.Label(self.dashboard_tab, text="داشبورد عملیات کاتالوگ", style="UX87Title.TLabel").pack(anchor="w")
            ttk.Label(self.dashboard_tab, text="وضعیت محصولات، انتشار و اتصال‌ها در یک نگاه", style="UX87Muted.TLabel").pack(anchor="w", pady=(2, 12))
            cards = ttk.Frame(self.dashboard_tab)
            cards.pack(fill="x")
            self.ux87_dashboard_vars = {}
            defs = [
                ("new_count", "جدید"), ("update_count", "نیازمند بروزرسانی"),
                ("no_content_count", "نیازمند محتوا"), ("queue_count", "صف انتشار"),
                ("published_count", "منتشرشده"), ("no_image_count", "بدون تصویر"),
            ]
            for idx, (key, label) in enumerate(defs):
                card = tk.Frame(cards, bg="white", padx=12, pady=10, highlightbackground="#dbe3ea", highlightthickness=1)
                card.grid(row=0, column=idx, sticky="nsew", padx=4)
                cards.columnconfigure(idx, weight=1)
                var = tk.StringVar(value="0")
                self.ux87_dashboard_vars[key] = var
                tk.Label(card, text=label, bg="white", fg="#64748b", font=("Tahoma", 9)).pack(anchor="e")
                tk.Label(card, textvariable=var, bg="white", fg="#071827", font=("Tahoma", 20, "bold")).pack(anchor="e", pady=(4, 0))

            quick = ttk.LabelFrame(self.dashboard_tab, text="شروع سریع", padding=14, style="Card.TLabelframe")
            quick.pack(fill="x", pady=14)
            for label, page in (("مدیریت محصولات", "products"), ("دریافت محصول", "discover"), ("صف انتشار", "publish"), ("هوش مصنوعی", "ai"), ("اتصال سایت", "connection")):
                ttk.Button(quick, text=label, command=lambda p=page: self.show_ux87_page(p), style="Primary.TButton").pack(side="left", padx=4)

            info = ttk.LabelFrame(self.dashboard_tab, text="قرارداد نسخه 8.7", padding=14, style="Card.TLabelframe")
            info.pack(fill="x")
            ttk.Label(info, text="یک Product Workspace رسمی • دیتای پایدار بین Releaseها • Secret Store ویندوز • انتشار Windows → FTP → Bridge → Store", wraplength=1050).pack(anchor="w")

        def _modernize_products_page(self):
            children = list(self.products_tab.winfo_children())
            pane = next((x for x in children if isinstance(x, ttk.Panedwindow)), None)
            frames_before = [x for x in children if isinstance(x, ttk.Frame) and x is not pane]
            for frame in frames_before[1:3]:
                try:
                    frame.pack_forget()
                except Exception:
                    pass

            bar = ttk.Frame(self.products_tab)
            if pane is not None:
                bar.pack(fill="x", pady=(4, 6), before=pane)
            else:
                bar.pack(fill="x", pady=(4, 6))
            ttk.Label(bar, text="نمایش").pack(side="left")
            self.product_filter_box = ttk.Combobox(bar, textvariable=self.product_filter, state="readonly", values=["work_queue", "new", "needs_update", "without_images", "without_content", "ready", "upload_queue", "error", "all"], width=16)
            self.product_filter_box.pack(side="left", padx=4)
            self.product_filter_box.bind("<<ComboboxSelected>>", lambda _e: self.refresh_products())
            search = ttk.Entry(bar, textvariable=self.product_search, width=24)
            search.pack(side="left", padx=4)
            search.bind("<Return>", lambda _e: self.refresh_products())
            sort = ttk.Combobox(bar, textvariable=self.product_sort, state="readonly", values=["priority", "rating", "downloads", "newest", "updated"], width=12)
            sort.pack(side="left", padx=4)
            sort.bind("<<ComboboxSelected>>", lambda _e: self.refresh_products())
            ttk.Button(bar, text="بروزرسانی", command=self.refresh_products).pack(side="left", padx=3)
            ttk.Button(bar, text="ویرایش محصول", command=self.open_product_studio, style="Primary.TButton").pack(side="right", padx=3)
            ttk.Button(bar, text="انتشار روی سایت", command=self.publish_product_now, style="Publish.TButton").pack(side="right", padx=3)

            more = ttk.Menubutton(bar, text="ابزارهای بیشتر")
            menu = tk.Menu(more, tearoff=False)
            commands = [
                ("ذخیره محصول", self.save_product),
                ("بازیابی کامل منبع", self.refetch_current_product),
                ("مدیریت تصاویر", self.open_image_manager),
                ("محتوا و SEO", self.open_content_studio),
                ("تولید محتوای AI برای این محصول", self.generate_ai_content),
                ("تاریخچه تغییرات", self.open_product_history),
                ("تأیید و افزودن به صف انتشار", self.approve_to_upload_queue),
                ("گزارش انتشار", self.open_current_publish_log),
                ("محاسبه قیمت", self.estimate_product_price),
                ("باز کردن صفحه منبع", self.open_source_product),
                ("مشخصات و فایل‌ها", self.open_technical_details),
                ("بلاک محصولات انتخاب‌شده", self.block_selected_products),
            ]
            for label, command in commands:
                menu.add_command(label=label, command=command)
            menu.add_separator()
            menu.add_command(label="AI برای انتخاب‌شده‌ها", command=self.bulk_ai_selected)
            menu.add_command(label="AI برای همه نیازمندها", command=self.bulk_ai_pending)
            menu.add_command(label="بازیابی انتخاب‌شده‌ها", command=self.bulk_refetch_selected)
            menu.add_command(label="قیمت انتخاب‌شده‌ها", command=self.bulk_price_selected)
            more.configure(menu=menu)
            more.pack(side="right", padx=3)

        def _build_ux87_ai_center(self):
            ttk.Label(self.ai_tab, text="مرکز هوش مصنوعی", style="UX87Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
            ttk.Label(self.ai_tab, text="OpenAI، AvalAI و تنظیمات ترجمه از پروفایل نسخه‌های قبلی خوانده می‌شوند.", style="UX87Muted.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 12))
            card = ttk.LabelFrame(self.ai_tab, text="Provider، مدل و ترجمه", padding=14, style="Card.TLabelframe")
            card.grid(row=2, column=0, columnspan=3, sticky="ew", pady=6)
            ttk.Label(card, text="Provider").grid(row=0, column=0, sticky="w", pady=5)
            provider = ttk.Combobox(card, textvariable=self.ai_provider, values=["auto", "avalai", "openai"], state="readonly", width=20)
            provider.grid(row=0, column=1, sticky="w", padx=6)
            provider.bind("<<ComboboxSelected>>", lambda _e: self._refresh_ai_key_source())
            ttk.Label(card, text="مدل").grid(row=1, column=0, sticky="w", pady=5)
            self.ai_model_box = ttk.Combobox(card, textvariable=self.ai_model, values=[], width=42)
            self.ai_model_box.grid(row=1, column=1, sticky="ew", padx=6)
            ttk.Button(card, text="دریافت مدل‌ها", command=self.load_ai_models).grid(row=1, column=2, padx=4)
            ttk.Label(card, text="API Key جدید").grid(row=2, column=0, sticky="w", pady=5)
            keyrow = ttk.Frame(card)
            keyrow.grid(row=2, column=1, columnspan=2, sticky="ew", padx=6)
            self.openai_key_entry = ttk.Entry(keyrow, textvariable=self.ai_key, show="•")
            self.openai_key_entry.pack(side="left", fill="x", expand=True)
            self.openai_key_visible = False
            self.openai_key_entry.bind("<Control-v>", lambda _e: self.paste_openai_key())
            self.openai_key_entry.bind("<Control-V>", lambda _e: self.paste_openai_key())
            self.openai_key_entry.bind("<Button-3>", self.open_openai_key_menu)
            ttk.Button(keyrow, text="Paste", command=self.paste_openai_key).pack(side="left", padx=3)
            ttk.Button(keyrow, text="نمایش/مخفی", command=self.toggle_openai_key_visibility).pack(side="left", padx=3)
            self.openai_key_source = tk.StringVar(value="")
            ttk.Label(card, textvariable=self.openai_key_source, style="SubHeader.TLabel").grid(row=3, column=1, columnspan=2, sticky="w", padx=6)

            ttk.Label(card, text="موتور ترجمه").grid(row=4, column=0, sticky="w", pady=5)
            ttk.Combobox(card, textvariable=self.translation_provider, values=["ai", "google"], state="readonly", width=20).grid(row=4, column=1, sticky="w", padx=6)
            ttk.Label(card, text="Google API Key").grid(row=5, column=0, sticky="w", pady=5)
            google_row = ttk.Frame(card)
            google_row.grid(row=5, column=1, columnspan=2, sticky="ew", padx=6)
            self.google_key_entry = ttk.Entry(google_row, textvariable=self.google_key, show="•")
            self.google_key_entry.pack(side="left", fill="x", expand=True)
            google_source = "Windows Credential Store" if get_secret("google_api_key") else ("GOOGLE_API_KEY" if env_value("GOOGLE_API_KEY", "") else "Legacy profile / new input")
            ttk.Label(google_row, text=f"منبع: {google_source}", style="SubHeader.TLabel").pack(side="left", padx=6)

            actions = ttk.Frame(card)
            actions.grid(row=6, column=1, columnspan=2, sticky="w", pady=8)
            ttk.Button(actions, text="ذخیره امن AI", command=self._save_ux87_ai_settings, style="Primary.TButton").pack(side="left", padx=3)
            ttk.Button(actions, text="تست زنده AI", command=self.test_openai_api, style="Success.TButton").pack(side="left", padx=3)
            ttk.Button(actions, text="انتقال کلید قدیمی", command=self.migrate_ai_key_file).pack(side="left", padx=3)
            ttk.Button(actions, text="حذف کلید OpenAI/AvalAI", command=self.clear_openai_secret, style="Danger.TButton").pack(side="left", padx=3)
            card.columnconfigure(1, weight=1)
            self._refresh_ai_key_source()

        def _save_ux87_ai_settings(self):
            if self.ai_key.get().strip():
                self.save_openai_secret()
            google = self.google_key.get().strip()
            if google:
                set_secret("google_api_key", google)
                self.db.set_setting("google_api_key", "")
            self.db.set_setting("translation_provider", self.translation_provider.get())
            self.db.set_setting("ai_provider", self.ai_provider.get())
            self.db.set_setting("ai_model", self.ai_model.get())
            self.db.set_setting("openai_model", self.ai_model.get())
            self._refresh_ux87_status()
            from tkinter import messagebox
            messagebox.showinfo("3DPrintHub", "تنظیمات AI و ترجمه ذخیره شد. کلیدها در Windows Credential Manager نگه‌داری می‌شوند.")

        def _build_ux87_connection_center(self):
            ttk.Label(self.connection_tab, text="مرکز اتصال سایت", style="UX87Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
            ttk.Label(self.connection_tab, text="FTP و Bridge با همان پروفایل پایدار و Windows Credential Manager کار می‌کنند.", style="UX87Muted.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 12))
            card = ttk.LabelFrame(self.connection_tab, text="اتصال Windows → Host → Django Bridge", padding=14, style="Card.TLabelframe")
            card.grid(row=2, column=0, columnspan=3, sticky="ew")
            rows = [
                ("FTP Host", self.ftp_host, False), ("FTP Port", self.ftp_port, False),
                ("FTP Username", self.ftp_user, False), ("FTP Password", self.ftp_password, True),
                ("مسیر پروژه روی FTP", self.ftp_remote_root, False), ("آدرس سایت", self.site_url, False),
            ]
            for i, (label, var, secret) in enumerate(rows):
                ttk.Label(card, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=5)
                ttk.Entry(card, textvariable=var, show="•" if secret else "").grid(row=i, column=1, sticky="ew", padx=5)
            token_row_index = len(rows)
            ttk.Label(card, text="Bridge Token").grid(row=token_row_index, column=0, sticky="w", padx=5, pady=5)
            tokenrow = ttk.Frame(card)
            tokenrow.grid(row=token_row_index, column=1, sticky="ew", padx=5)
            self.bridge_token_entry = ttk.Entry(tokenrow, textvariable=self.bridge_token, show="•")
            self.bridge_token_entry.pack(side="left", fill="x", expand=True)
            self.bridge_token_visible = False
            self.bridge_token_entry.bind("<Control-v>", self.paste_bridge_token)
            self.bridge_token_entry.bind("<Control-V>", self.paste_bridge_token)
            self.bridge_token_entry.bind("<Shift-Insert>", self.paste_bridge_token)
            self.bridge_token_entry.bind("<Button-3>", self.open_bridge_token_menu)
            ttk.Button(tokenrow, text="چسباندن توکن", command=self.paste_bridge_token).pack(side="left", padx=3)
            ttk.Button(tokenrow, text="نمایش/مخفی", command=self.toggle_bridge_token_visibility).pack(side="left", padx=3)
            self.connection_secret_source = tk.StringVar(value="")
            ttk.Label(card, textvariable=self.connection_secret_source, style="SubHeader.TLabel").grid(row=token_row_index + 1, column=1, sticky="w", padx=5, pady=4)
            actions = ttk.Frame(card)
            actions.grid(row=token_row_index + 2, column=1, sticky="w", pady=8)
            ttk.Button(actions, text="ذخیره امن اتصال", command=self.save_connection_settings, style="Primary.TButton").pack(side="left", padx=3)
            ttk.Button(actions, text="تست FTP", command=self.test_ftp_connection).pack(side="left", padx=3)
            ttk.Button(actions, text="تست Bridge", command=self.test_site_connection, style="Success.TButton").pack(side="left", padx=3)
            ttk.Button(actions, text="گزارش‌ها", command=self.open_log_folder).pack(side="left", padx=3)
            ttk.Button(card, text="ارسال آخرین Batch و دریافت ACK", command=self.upload_last_batch, style="Success.TButton").grid(row=token_row_index + 3, column=1, sticky="w", padx=5, pady=(4, 0))
            card.columnconfigure(1, weight=1)
            self._refresh_connection_secret_source()

        def _build_ux87_general_settings(self):
            ttk.Label(self.settings_tab, text="تنظیمات و نگهداری", style="UX87Title.TLabel").pack(anchor="w")
            ttk.Label(self.settings_tab, text="تنظیمات غیرحساس در پروفایل پایدار و Secretها در Credential Manager نگه‌داری می‌شوند.", style="UX87Muted.TLabel").pack(anchor="w", pady=(2, 12))
            profile = ttk.LabelFrame(self.settings_tab, text="پروفایل پایدار", padding=14, style="Card.TLabelframe")
            profile.pack(fill="x", pady=6)
            ttk.Label(profile, text=f"فایل Environment پایدار: {ENV_FILE}", wraplength=1000).pack(anchor="w")
            ttk.Button(profile, text="باز کردن فایل Environment", command=self.open_persistent_env, style="Primary.TButton").pack(anchor="w", pady=(8, 0))
            ttk.Button(profile, text="باز کردن پوشه Log", command=self.open_log_folder).pack(anchor="w", pady=(6, 0))

        def show_ux87_page(self, key: str):
            page = self._pages.get(key, self.products_tab)
            self.main_notebook.select(page)
            for item_key, button in self._nav_buttons.items():
                active = item_key == key
                button.configure(
                    bg="#c99a2e" if active else "#0b2238",
                    fg="#071827" if active else "#d9e4ee",
                    activebackground="#d8ad49" if active else "#123452",
                )
            if key == "dashboard":
                self._refresh_ux87_dashboard()
            self._refresh_ux87_status()

        def _refresh_ux87_dashboard(self):
            counts = self.db.status_counts()
            for key, var in getattr(self, "ux87_dashboard_vars", {}).items():
                var.set(str(counts.get(key, 0)))

        def _refresh_ux87_status(self):
            provider = self.ai_provider.get() if hasattr(self, "ai_provider") else "auto"
            if provider == "avalai":
                has_ai = bool(get_provider_key("avalai"))
            elif provider == "openai":
                has_ai = bool(get_provider_key("openai"))
            else:
                has_ai = bool(get_provider_key("avalai") or get_provider_key("openai"))
            if hasattr(self, "ux87_ai_status"):
                self.ux87_ai_status.set("AI: آماده" if has_ai else "AI: نیاز به کلید")
            has_host = bool(self.ftp_host.get().strip() and self.ftp_user.get().strip() and (self.ftp_password.get().strip() or get_secret("ftp_password")))
            has_bridge = bool(self.site_url.get().strip() and (self.bridge_token.get().strip() or get_secret("bridge_token")))
            if hasattr(self, "ux87_site_status"):
                self.ux87_site_status.set("سایت: تنظیم شده" if has_host and has_bridge else "سایت: تنظیمات ناقص")

        def refresh_all(self):
            super().refresh_all()
            self._refresh_ux87_dashboard()
            self._refresh_ux87_status()

        def open_product_studio(self, product_id=None):
            product_id = product_id or self.current_product
            if not product_id:
                from tkinter import messagebox
                messagebox.showwarning("3DPrintHub", "ابتدا یک محصول را انتخاب کنید.")
                return
            ProductWorkspace(self, int(product_id))

        def open_content_studio(self, product_id=None):
            product_id = product_id or self.current_product
            if not product_id:
                from tkinter import messagebox
                messagebox.showwarning("3DPrintHub", "ابتدا یک محصول را انتخاب کنید.")
                return
            workspace = ProductWorkspace(self, int(product_id))
            workspace.select_section("content")

        def open_product_studio_translation(self):
            self.open_content_studio(self.current_product)

        def open_image_manager(self):
            if not self.current_product:
                from tkinter import messagebox
                messagebox.showwarning("3DPrintHub", "ابتدا یک محصول را انتخاب کنید.")
                return
            workspace = ProductWorkspace(self, int(self.current_product))
            workspace.select_section("images")

        def _sanitize_legacy_button_texts(self):
            replacements = {
                "🚀 انتشار و ارسال به سایت": "انتشار صف روی سایت",
                "🚀 استودیوی محصول": "ویرایش محصول",
                "🚀 ارسال همین محصول": "انتشار همین محصول",
                "✨ ترجمه فارسی": "ترجمه با AI",
                "✨ AI این محصول": "AI این محصول",
                "🧾 گزارش ارسال": "گزارش انتشار",
                "🖼 گالری تصاویر": "مدیریت تصاویر",
                "♻ بازیابی کامل": "بازیابی کامل",
                "♻ بازیابی انتخاب‌شده‌ها": "بازیابی انتخاب‌شده‌ها",
                "♻ بروزرسانی محصولات منبع": "بروزرسانی محصولات منبع",
                "🔎 کشف جدیدها": "کشف جدیدها",
            }
            def walk(root):
                for child in root.winfo_children():
                    yield child
                    yield from walk(child)
            for widget in walk(self):
                if isinstance(widget, ttk.Button):
                    try:
                        text = str(widget.cget("text"))
                        if text in replacements:
                            widget.configure(text=replacements[text])
                    except Exception:
                        pass

    CatalogCenterApp87.__name__ = "CatalogCenterApp87"
    return CatalogCenterApp87
