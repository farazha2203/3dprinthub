from __future__ import annotations

import json
from urllib.parse import urlsplit
from tkinter import messagebox, ttk

from .epic49_local_publish import import_batch_to_local_django, running_as_portable
from .v8_features import ack_item_confirms_publish


LOCAL_BUTTON_TEXT = "🧪 انتشار آزمایشی روی کامپیوتر"
SITE_BUTTON_TEXT = "🌐 انتشار واقعی روی سایت اصلی"


def _walk(widget):
    yield widget
    try:
        children = widget.winfo_children()
    except Exception:
        children = []
    for child in children:
        yield from _walk(child)


def _rename_legacy_publish_buttons(workspace) -> None:
    for widget in _walk(workspace):
        try:
            text = str(widget.cget("text") or "")
        except Exception:
            continue
        if text == "🚀 ارسال همین محصول":
            try:
                widget.configure(text=SITE_BUTTON_TEXT, style="Publish.TButton")
            except Exception:
                widget.configure(text=SITE_BUTTON_TEXT)


def _site_label(workspace) -> tuple[str, str]:
    try:
        url = str(workspace.app.site_url.get() or "").strip().rstrip("/")
    except Exception:
        url = ""
    host = urlsplit(url).netloc or url or "سایت تنظیم‌شده"
    return url, host


def _ack_item(ack: dict, product_id: int) -> dict | None:
    for item in ack.get("items") or []:
        if not isinstance(item, dict):
            continue
        try:
            if int(item.get("desktop_product_id") or 0) == int(product_id):
                return item
        except Exception:
            continue
    return None


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_dual_publish_installed", False):
        return

    original_init = workspace_class.__init__
    original_publish_ui = workspace_class._publish_ui

    def __init__(self, app, product_id: int):
        original_init(self, app, product_id)
        _rename_legacy_publish_buttons(self)

    def _publish_ui(self):
        original_publish_ui(self)
        targets = ttk.LabelFrame(
            self.publish_tab,
            text="مقصد انتشار — Local Test / Production",
            padding=10,
            style="Card.TLabelframe",
        )
        targets.pack(fill="x", pady=(10, 0))
        targets.columnconfigure(0, weight=1)
        targets.columnconfigure(1, weight=1)

        local = ttk.Frame(targets, padding=8)
        local.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ttk.Label(local, text="🧪 تست روی همین کامپیوتر", style="Header.TLabel").pack(anchor="w")
        portable = running_as_portable()
        local_help = (
            "نسخه Portable کارمندان: Local Test غیرفعال است؛ این قابلیت فقط روی سیستم توسعه فعال می‌شود."
            if portable
            else (
                "Batch استاندارد 8.5 مستقیماً وارد Django لوکال می‌شود. "
                "هیچ FTP، Bridge یا تغییری روی سایت اصلی انجام نمی‌شود."
            )
        )
        ttk.Label(
            local,
            text=local_help,
            style="SubHeader.TLabel",
            wraplength=580,
        ).pack(anchor="w", pady=(3, 8))
        local_button = ttk.Button(
            local,
            text=LOCAL_BUTTON_TEXT if not portable else "🧪 Local Test — فقط نسخه توسعه",
            command=self.publish_to_local_computer,
            style="Primary.TButton",
        )
        local_button.pack(anchor="w")
        if portable:
            local_button.state(["disabled"])

        production = ttk.Frame(targets, padding=8)
        production.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        _url, host = _site_label(self)
        self.production_target_text = ttk.Label(
            production,
            text=f"🌐 سایت اصلی: {host}",
            style="Header.TLabel",
        )
        self.production_target_text.pack(anchor="w")
        ttk.Label(
            production,
            text=(
                "مسیر واقعی FTP + Catalog Bridge. این گزینه Product/SEO/Hero سایت اصلی را تغییر می‌دهد "
                "و قبل از ارسال دو تأیید صریح می‌گیرد."
            ),
            style="SubHeader.TLabel",
            wraplength=580,
        ).pack(anchor="w", pady=(3, 8))
        ttk.Button(
            production,
            text=SITE_BUTTON_TEXT,
            command=self.publish_to_production_site,
            style="Publish.TButton",
        ).pack(anchor="w")

    def publish_to_local_computer(self):
        if running_as_portable():
            messagebox.showwarning(
                "3DPrintHub — Local Test",
                "Local Test در نسخه Portable کارمندان غیرفعال است. این دکمه فقط در نسخه Source/Developer اجرا می‌شود.",
                parent=self,
            )
            return
        if not self.queue_for_publish(notify=False):
            return
        if not messagebox.askyesno(
            "3DPrintHub — Local Test",
            "این محصول فقط روی Django همین کامپیوتر تست شود؟\n\n"
            "مقصد مورد انتظار:\n"
            "D:\\projects\\3DPrintHub\\db.sqlite3\n\n"
            "FTP و سایت اصلی استفاده نمی‌شوند.",
            parent=self,
        ):
            return
        try:
            result = self.app.build_batch(product_ids=[self.product_id], quiet=True)
        except Exception as exc:
            messagebox.showerror("3DPrintHub", f"ساخت Batch لوکال ناموفق بود:\n{type(exc).__name__}: {exc}", parent=self)
            return

        batch = result["batch"]
        batch_uuid = result["batch_uuid"]
        self.db.record_sync_receipt(
            self.product_id,
            batch_uuid,
            "desktop_local_batch_ready",
            "",
            {"batch_name": batch.name, "target": "local_django"},
        )
        self.footer_status.set("🧪 در حال Import محصول در Django لوکال…")

        def work():
            return import_batch_to_local_django(batch)

        def done(payload, error):
            # A local test must never leave the desktop row looking like a
            # production-published item. It remains approved and ready for the
            # separate Production button.
            self.db.update_product(
                self.product_id,
                {"workflow_status": "approved", "upload_ready": 1},
            )
            if error:
                self.db.record_sync_receipt(
                    self.product_id,
                    batch_uuid,
                    "desktop_local_import_failed",
                    "",
                    {"batch_name": batch.name, "target": "local_django", "error": str(error)},
                )
                self.footer_status.set("تست Local ناموفق بود")
                messagebox.showerror("3DPrintHub — Local Test", str(error), parent=self)
                return

            ack = payload["ack"]
            item = _ack_item(ack, self.product_id)
            if item is None:
                error_text = "ACK لوکال برای همین محصول پیدا نشد."
                self.db.record_sync_receipt(
                    self.product_id,
                    batch_uuid,
                    "desktop_local_import_failed",
                    "",
                    {"batch_name": batch.name, "target": "local_django", "error": error_text, "ack": ack},
                )
                self.footer_status.set("تست Local ناقص بود")
                messagebox.showerror("3DPrintHub — Local Test", error_text, parent=self)
                return

            row = self.db.product(self.product_id)
            strict_ok = ack_item_confirms_publish(item, row, require_store_visibility=True)
            status = "desktop_local_imported" if strict_ok else "desktop_local_import_review"
            self.db.record_sync_receipt(
                self.product_id,
                batch_uuid,
                status,
                "",
                {"batch_name": batch.name, "target": "local_django", "ack_item": item},
            )
            product_path = str(item.get("product_url") or "")
            local_site = str(payload["preflight"].get("site_url") or "http://127.0.0.1:8000").rstrip("/")
            product_url = local_site + product_path if product_path.startswith("/") else local_site
            self.footer_status.set("🧪 تست Local با موفقیت Import شد" if strict_ok else "🧪 Import Local انجام شد؛ نیازمند بررسی")
            messagebox.showinfo(
                "3DPrintHub — Local Test",
                "Import مستقیم روی کامپیوتر پایان یافت.\n\n"
                f"Batch: {batch.name}\n"
                f"Local Product ID: {item.get('product_id') or '—'}\n"
                f"Visible on Store: {item.get('visible_on_store')}\n"
                f"Local URL: {product_url}\n\n"
                "شناسه‌های Local داخل server_id / server_revision تولیدی ذخیره نشدند.",
                parent=self,
            )

        self._thread(work, done)

    def publish_to_production_site(self):
        if not self.queue_for_publish(notify=False):
            return
        site_url, host = _site_label(self)
        if not site_url:
            messagebox.showerror("3DPrintHub", "آدرس سایت اصلی در تنظیمات اتصال خالی است.", parent=self)
            return
        if not messagebox.askyesno(
            "انتشار روی سایت اصلی — مرحله ۱ از ۲",
            f"مقصد واقعی:\n{site_url}\n\n"
            "این عملیات از FTP + Catalog Bridge استفاده می‌کند و دیتای سایت اصلی را تغییر می‌دهد.\n"
            "ادامه می‌دهید؟",
            parent=self,
        ):
            return
        if not messagebox.askyesno(
            "تأیید نهایی انتشار Production",
            f"تأیید نهایی برای انتشار محصول #{self.product_id} روی {host}\n\n"
            "این Local Test نیست. آیا مطمئن هستید؟",
            parent=self,
        ):
            return
        self.footer_status.set(f"🌐 انتشار واقعی روی {host} شروع شد…")
        self.app.publish_product_now(self.product_id, parent=self)

    # The legacy header/footer buttons are bound to self.publish_now. Make their
    # behavior explicit and production-safe as well.
    def publish_now(self):
        return self.publish_to_production_site()

    workspace_class.__init__ = __init__
    workspace_class._publish_ui = _publish_ui
    workspace_class.publish_to_local_computer = publish_to_local_computer
    workspace_class.publish_to_production_site = publish_to_production_site
    workspace_class.publish_now = publish_now
    workspace_class._phase49_dual_publish_installed = True
