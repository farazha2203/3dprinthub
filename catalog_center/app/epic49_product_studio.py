from __future__ import annotations

import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .db import normalize_url
from .product_studio import (
    PRODUCT_TYPE_CODES,
    PRODUCT_TYPE_LABELS,
    ProductStudio as BaseProductStudio,
)
from .v8_features import commercial_license_allows_publish, product_fingerprint


LICENSE_LABEL_TO_CODE = {
    "نیازمند بررسی": "review",
    "مجاز برای فروش": "allowed",
    "متعلق به 3DPrintHub": "owned",
    "مالکیت عمومی": "public_domain",
    "غیرمجاز": "blocked",
    "نامشخص": "unknown",
}
LICENSE_CODE_TO_LABEL = {code: label for label, code in LICENSE_LABEL_TO_CODE.items()}


def unique_lines(value: str) -> list[str]:
    """Return trimmed, non-empty unique lines while preserving user order."""
    output: list[str] = []
    seen: set[str] = set()
    for raw in (value or "").splitlines():
        item = raw.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        output.append(item)
    return output


def parse_json_list(value: str, *, field_name: str) -> list:
    text = (value or "").strip()
    if not text:
        return []
    payload = json.loads(text)
    if not isinstance(payload, list):
        raise ValueError(f"{field_name} باید JSON Array باشد")
    return payload


class ProductStudio(BaseProductStudio):
    """Epic49 final Product Studio.

    The original v8.5 studio remains the stable base. This class only upgrades
    content editing and publish approval controls, so gallery/AI/network logic is
    not duplicated or forked.
    """

    # ---------- small editor helpers ----------
    def _text_set(self, widget: tk.Text, value: str):
        previous = str(widget.cget("state")) if "state" in widget.keys() else "normal"
        if previous == "disabled":
            widget.configure(state="normal")
        try:
            super()._text_set(widget, value)
        finally:
            if previous == "disabled":
                widget.configure(state="disabled")

    def _list_editor(self, parent, title: str, attr_name: str, *, height: int = 7):
        frame = ttk.LabelFrame(parent, text=title, padding=7, style="Card.TLabelframe")
        text = tk.Text(frame, height=height, wrap="word", undo=True)
        text.pack(fill="both", expand=True)
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(5, 0))
        ttk.Button(
            controls,
            text="+ افزودن مورد",
            command=lambda: self._append_list_item(text, title),
        ).pack(side="left", padx=2)
        ttk.Button(
            controls,
            text="− حذف خط جاری",
            command=lambda: self._delete_current_line(text),
        ).pack(side="left", padx=2)
        ttk.Button(
            controls,
            text="پاک‌کردن همه",
            command=lambda: self._clear_editor(text),
            style="Danger.TButton",
        ).pack(side="left", padx=2)
        setattr(self, attr_name, text)
        return frame

    def _append_list_item(self, widget: tk.Text, title: str):
        value = simpledialog.askstring("افزودن مورد", f"مورد جدید برای «{title}»:", parent=self)
        if value is None:
            return
        value = value.strip()
        if not value:
            return
        current = widget.get("1.0", "end").strip()
        widget.delete("1.0", "end")
        widget.insert("1.0", (current + "\n" if current else "") + value)
        widget.see("end")
        self.footer_status.set("مورد اضافه شد؛ برای ثبت نهایی ذخیره را بزنید")

    def _delete_current_line(self, widget: tk.Text):
        line = widget.index("insert").split(".", 1)[0]
        widget.delete(f"{line}.0", f"{int(line) + 1}.0")
        self.footer_status.set("خط حذف شد؛ برای ثبت نهایی ذخیره را بزنید")

    def _clear_editor(self, widget: tk.Text):
        if not messagebox.askyesno("3DPrintHub", "همه موارد این بخش پاک شوند؟", parent=self):
            return
        widget.delete("1.0", "end")
        self.footer_status.set("فهرست پاک شد؛ برای ثبت نهایی ذخیره را بزنید")

    # ---------- content tab ----------
    def _content_ui(self):
        toolbar = ttk.Frame(self.content_tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(
            toolbar,
            text="✨ ترجمه دقیق EN → FA",
            command=lambda: self.generate_ai("translate"),
            style="Primary.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(
            toolbar,
            text="✨ تولید محتوای فروشگاهی",
            command=lambda: self.generate_ai("commerce"),
            style="Success.TButton",
        ).pack(side="left", padx=3)
        ttk.Button(toolbar, text="💾 ذخیره همه تغییرات", command=self.save, style="Success.TButton").pack(side="left", padx=3)
        self.ai_status = tk.StringVar(value="")
        ttk.Label(toolbar, textvariable=self.ai_status, style="SubHeader.TLabel").pack(side="right")

        editor_tabs = ttk.Notebook(self.content_tab)
        editor_tabs.pack(fill="both", expand=True)
        text_tab = ttk.Frame(editor_tabs, padding=8)
        seo_tab = ttk.Frame(editor_tabs, padding=8)
        lists_tab = ttk.Frame(editor_tabs, padding=8)
        advanced_tab = ttk.Frame(editor_tabs, padding=8)
        editor_tabs.add(text_tab, text="متن فارسی")
        editor_tabs.add(seo_tab, text="SEO و فروش")
        editor_tabs.add(lists_tab, text="لیست‌های قابل ویرایش")
        editor_tabs.add(advanced_tab, text="پیشنهاد متریال / داده AI")

        pane = ttk.Panedwindow(text_tab, orient="horizontal")
        pane.pack(fill="both", expand=True)
        source = ttk.LabelFrame(pane, text="متن منبع — فقط مرجع", padding=8, style="Card.TLabelframe")
        persian = ttk.LabelFrame(pane, text="محتوای فارسی قابل ویرایش", padding=8, style="Card.TLabelframe")
        pane.add(source, weight=1)
        pane.add(persian, weight=1)

        ttk.Label(source, text="عنوان انگلیسی/اصلی").pack(anchor="w")
        self.content_source_title = tk.Text(source, height=3, wrap="word", state="disabled")
        self.content_source_title.pack(fill="x", pady=(2, 8))
        ttk.Label(source, text="توضیحات منبع").pack(anchor="w")
        self.content_source_desc = tk.Text(source, wrap="word", state="disabled")
        self.content_source_desc.pack(fill="both", expand=True, pady=(2, 0))

        ttk.Label(persian, text="عنوان فارسی").pack(anchor="w")
        self.content_title_fa = tk.StringVar()
        ttk.Entry(persian, textvariable=self.content_title_fa).pack(fill="x", pady=(2, 8))
        ttk.Label(persian, text="توضیح کوتاه فارسی").pack(anchor="w")
        self.content_short_fa = tk.Text(persian, height=5, wrap="word", undo=True)
        self.content_short_fa.pack(fill="x", pady=(2, 8))
        ttk.Label(persian, text="توضیح کامل فارسی").pack(anchor="w")
        self.content_desc_fa = tk.Text(persian, wrap="word", undo=True)
        self.content_desc_fa.pack(fill="both", expand=True, pady=(2, 8))
        ttk.Button(persian, text="ذخیره محتوای فارسی", command=self.save, style="Success.TButton").pack(anchor="e")

        seo_tab.columnconfigure(1, weight=1)
        seo_tab.rowconfigure(4, weight=1)
        self.content_seo_title = tk.StringVar()
        ttk.Label(seo_tab, text="SEO Title فارسی").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(seo_tab, textvariable=self.content_seo_title).grid(row=0, column=1, sticky="ew", padx=6, pady=5)
        ttk.Label(seo_tab, text="SEO Description فارسی").grid(row=1, column=0, sticky="nw", pady=5)
        self.content_seo_desc = tk.Text(seo_tab, height=5, wrap="word", undo=True)
        self.content_seo_desc.grid(row=1, column=1, sticky="nsew", padx=6, pady=5)
        ttk.Label(seo_tab, text="کپشن شبکه اجتماعی").grid(row=2, column=0, sticky="nw", pady=5)
        self.content_social_caption = tk.Text(seo_tab, height=7, wrap="word", undo=True)
        self.content_social_caption.grid(row=2, column=1, sticky="nsew", padx=6, pady=5)
        sales_frame = self._list_editor(seo_tab, "بولت‌های فروش — هر خط یک مورد", "content_sales_bullets", height=8)
        sales_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=6)
        alt_frame = self._list_editor(seo_tab, "Alt تصاویر — هر خط یک متن", "content_image_alts", height=7)
        alt_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=6)

        lists_tab.columnconfigure(0, weight=1)
        lists_tab.columnconfigure(1, weight=1)
        lists_tab.rowconfigure(0, weight=1)
        lists_tab.rowconfigure(1, weight=1)
        lists_tab.rowconfigure(2, weight=1)
        self._list_editor(lists_tab, "دسته‌های فارسی AI", "content_categories_fa").grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self._list_editor(lists_tab, "تگ‌های فارسی", "content_tags_fa").grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self._list_editor(lists_tab, "هشتگ‌ها", "content_hashtags_fa").grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self._list_editor(lists_tab, "کلمات کلیدی سایت", "content_keywords").grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        self._list_editor(lists_tab, "متریال‌های محصول", "content_materials").grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        self._list_editor(lists_tab, "رنگ‌های محصول", "content_colors").grid(row=2, column=1, sticky="nsew", padx=4, pady=4)

        advanced_tab.columnconfigure(0, weight=1)
        advanced_tab.rowconfigure(1, weight=1)
        ttk.Label(
            advanced_tab,
            text="پیشنهادهای متریال AI به‌صورت JSON Array ذخیره می‌شوند؛ می‌توانی مستقیم اضافه، حذف یا ویرایششان کنی.",
            style="SubHeader.TLabel",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.content_material_recommendations = tk.Text(advanced_tab, wrap="word", undo=True, font=("Consolas", 10))
        self.content_material_recommendations.grid(row=1, column=0, sticky="nsew")
        advanced_buttons = ttk.Frame(advanced_tab)
        advanced_buttons.grid(row=2, column=0, sticky="ew", pady=6)
        ttk.Button(
            advanced_buttons,
            text="پاک‌کردن پیشنهادهای متریال",
            command=lambda: self._clear_editor(self.content_material_recommendations),
            style="Danger.TButton",
        ).pack(side="left")
        ttk.Button(advanced_buttons, text="ذخیره همه تغییرات", command=self.save, style="Success.TButton").pack(side="right")

    # ---------- publish tab ----------
    def _publish_ui(self):
        self.publish_checklist = tk.StringVar(value="")
        ttk.Label(self.publish_tab, text="کنترل و تنظیم انتشار", style="Header.TLabel").pack(anchor="w")

        settings = ttk.LabelFrame(self.publish_tab, text="تنظیمات انتشار قابل ویرایش", padding=10, style="Card.TLabelframe")
        settings.pack(fill="x", pady=(10, 8))
        ttk.Checkbutton(settings, text="تأیید برای فروش", variable=self.approved_var, command=self.refresh_checklists).grid(row=0, column=0, sticky="w", padx=8, pady=5)
        ttk.Checkbutton(settings, text="محصول فروشگاه", variable=self.publish_product_var, command=self.refresh_checklists).grid(row=0, column=1, sticky="w", padx=8, pady=5)
        ttk.Checkbutton(settings, text="نمونه‌کار", variable=self.publish_portfolio_var, command=self.refresh_checklists).grid(row=0, column=2, sticky="w", padx=8, pady=5)

        self.publish_license_label_var = tk.StringVar(value=LICENSE_CODE_TO_LABEL["review"])
        ttk.Label(settings, text="مجوز تجاری").grid(row=1, column=0, sticky="w", padx=8, pady=5)
        license_box = ttk.Combobox(
            settings,
            textvariable=self.publish_license_label_var,
            state="readonly",
            values=list(LICENSE_LABEL_TO_CODE),
            width=28,
        )
        license_box.grid(row=1, column=1, sticky="ew", padx=8, pady=5)
        license_box.bind("<<ComboboxSelected>>", lambda _event: self._publish_license_changed())
        ttk.Label(
            settings,
            text="برای فروش فقط «مجاز برای فروش»، «متعلق به 3DPrintHub» یا «مالکیت عمومی» قابل انتشار است.",
            style="SubHeader.TLabel",
        ).grid(row=1, column=2, columnspan=2, sticky="w", padx=8, pady=5)
        settings.columnconfigure(2, weight=1)

        ttk.Button(settings, text="💾 ذخیره تنظیمات انتشار", command=self.save_publish_settings).grid(row=2, column=0, sticky="w", padx=8, pady=8)
        ttk.Button(settings, text="✅ ذخیره و آماده‌سازی", command=self.queue_for_publish, style="Success.TButton").grid(row=2, column=1, sticky="w", padx=8, pady=8)

        ttk.Label(self.publish_tab, textvariable=self.publish_checklist, justify="left", wraplength=1200).pack(fill="x", pady=12)
        self.publish_source = tk.StringVar(value="")
        self.publish_server = tk.StringVar(value="")
        ttk.Label(self.publish_tab, textvariable=self.publish_source, style="SubHeader.TLabel").pack(anchor="w", pady=4)
        ttk.Label(self.publish_tab, textvariable=self.publish_server, style="SubHeader.TLabel").pack(anchor="w", pady=4)

        buttons = ttk.Frame(self.publish_tab)
        buttons.pack(fill="x", pady=18)
        ttk.Button(buttons, text="💾 ذخیره همه", command=self.save).pack(side="left", padx=4)
        ttk.Button(buttons, text="✅ تأیید و افزودن به صف انتشار", command=self.queue_for_publish, style="Success.TButton").pack(side="left", padx=4)
        ttk.Button(buttons, text="🚀 ارسال همین محصول به سایت", command=self.publish_now, style="Success.TButton").pack(side="left", padx=4)
        ttk.Button(buttons, text="🧾 گزارش ارسال", command=self.open_sync_log).pack(side="left", padx=4)
        ttk.Button(buttons, text="رفتن به صف انتشار", command=self.open_upload_tab, style="Primary.TButton").pack(side="left", padx=4)

    def _publish_license_changed(self):
        code = LICENSE_LABEL_TO_CODE.get(self.publish_license_label_var.get(), "review")
        self.license_var.set(code)
        self.refresh_checklists()

    def save_publish_settings(self):
        if self.save(silent=True):
            self.footer_status.set("تنظیمات انتشار ذخیره شد")
            self.reload()
            return True
        return False

    # ---------- load/save ----------
    def reload(self):
        super().reload()
        row = self.db.product(self.product_id)
        if row is None:
            return
        self.publish_license_label_var.set(
            LICENSE_CODE_TO_LABEL.get(row["commercial_status"] or "review", LICENSE_CODE_TO_LABEL["review"])
        )
        self._text_set(self.content_categories_fa, "\n".join(map(str, self._json_list(row["categories_fa_json"]))))
        self._text_set(self.content_tags_fa, "\n".join(map(str, self._json_list(row["tags_fa_json"]))))
        self._text_set(self.content_hashtags_fa, "\n".join(map(str, self._json_list(row["hashtags_fa_json"]))))
        self._text_set(self.content_keywords, "\n".join(map(str, self._json_list(row["keywords_json"]))))
        self._text_set(self.content_materials, "\n".join(map(str, self._json_list(row["materials_json"]))))
        self._text_set(self.content_colors, "\n".join(map(str, self._json_list(row["colors_json"]))))
        self.content_seo_title.set(row["seo_title_fa"] or "")
        self._text_set(self.content_seo_desc, row["seo_description_fa"] or "")
        self._text_set(self.content_social_caption, row["social_caption_fa"] or "")
        self._text_set(self.content_sales_bullets, "\n".join(map(str, self._json_list(row["sales_bullets_json"]))))
        self._text_set(self.content_image_alts, "\n".join(map(str, self._json_list(row["image_alt_texts_json"]))))
        material_recommendations = self._json_list(row["material_recommendations_json"])
        self._text_set(
            self.content_material_recommendations,
            json.dumps(material_recommendations, ensure_ascii=False, indent=2),
        )

    def _extended_content_values(self) -> dict:
        material_recommendations = parse_json_list(
            self._text_get(self.content_material_recommendations),
            field_name="پیشنهادهای متریال",
        )
        return {
            "categories_fa_json": json.dumps(unique_lines(self._text_get(self.content_categories_fa)), ensure_ascii=False),
            "tags_fa_json": json.dumps(unique_lines(self._text_get(self.content_tags_fa)), ensure_ascii=False),
            "hashtags_fa_json": json.dumps(unique_lines(self._text_get(self.content_hashtags_fa)), ensure_ascii=False),
            "keywords_json": json.dumps(unique_lines(self._text_get(self.content_keywords)), ensure_ascii=False),
            "materials_json": json.dumps(unique_lines(self._text_get(self.content_materials)), ensure_ascii=False),
            "colors_json": json.dumps(unique_lines(self._text_get(self.content_colors)), ensure_ascii=False),
            "seo_title_fa": self.content_seo_title.get().strip(),
            "seo_description_fa": self._text_get(self.content_seo_desc),
            "social_caption_fa": self._text_get(self.content_social_caption),
            "sales_bullets_json": json.dumps(unique_lines(self._text_get(self.content_sales_bullets)), ensure_ascii=False),
            "image_alt_texts_json": json.dumps(unique_lines(self._text_get(self.content_image_alts)), ensure_ascii=False),
            "material_recommendations_json": json.dumps(material_recommendations, ensure_ascii=False),
        }

    def save(self, silent=False):
        # The publish tab uses Persian labels, while the database/server contract uses stable codes.
        if hasattr(self, "publish_license_label_var"):
            code = LICENSE_LABEL_TO_CODE.get(self.publish_license_label_var.get(), self.license_var.get() or "review")
            self.license_var.set(code)

        if not super().save(silent=True):
            return False

        try:
            extended = self._extended_content_values()
        except Exception as exc:
            if not silent:
                messagebox.showerror("3DPrintHub", f"داده‌های محتوایی معتبر نیست:\n{exc}", parent=self)
            return False

        row = self.db.product(self.product_id)
        if row is None:
            return False

        publish_product = int(bool(self.publish_product_var.get()))
        publish_portfolio = int(bool(self.publish_portfolio_var.get()))
        product_type = PRODUCT_TYPE_CODES.get(self.product_type_var.get(), "ready_product")
        if publish_portfolio and not publish_product:
            product_type = "portfolio"
        elif publish_product and product_type == "portfolio":
            product_type = "ready_product"
            self.product_type_var.set(PRODUCT_TYPE_LABELS["ready_product"])

        pack = self._json_dict(row["content_pack_json"])
        pack.update({
            "title_fa": self.content_title_fa.get().strip(),
            "short_description_fa": self._text_get(self.content_short_fa),
            "description_fa": self._text_get(self.content_desc_fa),
            "categories_fa": json.loads(extended["categories_fa_json"]),
            "tags_fa": json.loads(extended["tags_fa_json"]),
            "hashtags_fa": json.loads(extended["hashtags_fa_json"]),
            "keywords": json.loads(extended["keywords_json"]),
            "materials": json.loads(extended["materials_json"]),
            "colors": json.loads(extended["colors_json"]),
            "seo_title_fa": extended["seo_title_fa"],
            "seo_description_fa": extended["seo_description_fa"],
            "sales_bullets": json.loads(extended["sales_bullets_json"]),
            "social_caption_fa": extended["social_caption_fa"],
            "image_alt_texts": json.loads(extended["image_alt_texts_json"]),
            "material_recommendations": json.loads(extended["material_recommendations_json"]),
        })

        before = dict(row)
        values = {
            **extended,
            "content_pack_json": json.dumps(pack, ensure_ascii=False),
            "commercial_status": self.license_var.get() or "review",
            "approved_for_sale": int(bool(self.approved_var.get())),
            "publish_as_product": publish_product,
            "publish_as_portfolio": publish_portfolio,
            "product_type": product_type,
        }
        self.db.update_product(self.product_id, values)
        self.row = self.db.product(self.product_id)
        self.db.save_history(
            self.product_id,
            "epic49_studio_save",
            before,
            dict(self.row),
            "Epic49 editable content and publish settings",
        )
        self.app.refresh_products()
        self.app.refresh_published()
        self.refresh_checklists()
        if not silent:
            self.footer_status.set("همه تغییرات محتوا و انتشار ذخیره شد")
        return True

    # ---------- publish ----------
    def _checklist(self):
        checks = list(super()._checklist())
        row = self.db.product(self.product_id)
        if row is None:
            return checks
        publish_product = bool(row["publish_as_product"])
        publish_portfolio = bool(row["publish_as_portfolio"])
        checks.append(("نوع انتشار انتخاب‌شده", publish_product or publish_portfolio))
        checks.append(("تأیید فروش", (not publish_product) or bool(row["approved_for_sale"])))
        return checks

    def queue_for_publish(self, notify=True):
        # Save the exact controls currently visible to the user before validating.
        if not self.save(silent=True):
            return False
        row = self.db.product(self.product_id)
        if row is None:
            return False

        selected = self._json_list(row["selected_images_json"])
        publish_product = int(bool(row["publish_as_product"]))
        publish_portfolio = int(bool(row["publish_as_portfolio"]))
        missing = []
        if not selected:
            missing.append("حداقل یک تصویر انتخاب‌شده")
        if not (row["title_fa"] or row["source_title"]):
            missing.append("عنوان")
        if not (row["description_fa"] or "").strip():
            missing.append("توضیحات فارسی")
        if not (row["local_category_slug"] or "").strip() or row["local_category_slug"] == "external-other":
            missing.append("گروه سایت")
        if not publish_product and not publish_portfolio:
            missing.append("حداقل یکی از «محصول فروشگاه» یا «نمونه‌کار»")
        if publish_product and row["product_type"] == "ready_product" and int(row["final_price"] or row["suggested_price"] or 0) <= 0:
            missing.append("قیمت")
        if not commercial_license_allows_publish(row["commercial_status"]):
            missing.append("مجوز تجاری مجاز (allowed / owned / public_domain)")
        if missing:
            messagebox.showwarning(
                "3DPrintHub",
                "برای انتشار این موارد ناقص است:\n- " + "\n- ".join(missing),
                parent=self,
            )
            self.nb.select(self.publish_tab)
            return False

        fp = row["fingerprint"] or product_fingerprint(
            row["source_code"], row["external_id"], row["source_url"]
        )
        dup = self.db.find_duplicate(
            row["source_code"],
            row["external_id"],
            normalize_url(row["source_url"]),
            fp,
            exclude_id=self.product_id,
        )
        if dup:
            messagebox.showerror("3DPrintHub", f"محصول تکراری شناسایی شد: #{dup['id']}", parent=self)
            return False

        approved = int(bool(row["approved_for_sale"]))
        if publish_product and not approved:
            approved = 1 if messagebox.askyesno(
                "3DPrintHub",
                "این محصول برای فروش تأیید نشده است. همین حالا برای فروش تأیید شود؟",
                parent=self,
            ) else 0
            self.approved_var.set(approved)
            if not approved:
                return False

        self.db.update_product(self.product_id, {
            "upload_ready": 1,
            "workflow_status": "approved",
            "publish_as_product": publish_product,
            "publish_as_portfolio": publish_portfolio,
            "approved_for_sale": approved,
            "commercial_status": row["commercial_status"],
            "fingerprint": fp,
            "product_sync_error": "",
        })
        self.app.refresh_products()
        self.app.refresh_upload_queue()
        self.reload()
        self.footer_status.set("محصول آماده ارسال است")
        if notify:
            messagebox.showinfo(
                "3DPrintHub",
                "محصول با تنظیمات فعلی ذخیره شد و به صف انتشار اضافه شد.\nبعد از ACK سایت به «منتشرشده‌ها» منتقل می‌شود.",
                parent=self,
            )
        return True
