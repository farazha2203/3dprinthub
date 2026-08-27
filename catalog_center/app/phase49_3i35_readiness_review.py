from __future__ import annotations

from datetime import datetime, timezone

import tkinter as tk
from tkinter import messagebox, ttk

from .phase49_3i35_operator_ledger import ensure_schema

PHASE = "49.3I.35"


def _row_value(row, key, default=""):
    if row is None:
        return default
    try:
        return row[key] if key in row.keys() else default
    except Exception:
        return default


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3i35_readiness_review", False):
        return
    original_init = workspace_class.__init__
    original_reload = workspace_class.reload

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        original_init(self, app, product_id)
        ensure_schema(app.db)
        self._phase49_3i35_build_review_controls()
        self._phase49_3i35_refresh_review_state()

    def build_review_controls(self):
        content_panel = ttk.LabelFrame(
            self.content_tab,
            text="تأیید اپراتور SEO — بدون فراخوانی دوباره AI",
            padding=7,
            style="Card.TLabelframe",
        )
        try:
            content_panel.pack(fill="x", pady=(0, 8), after=getattr(self, "_phase49_3i33_source_metrics_var", None))
        except Exception:
            content_panel.pack(fill="x", pady=(0, 8))
        self._phase49_3i35_seo_review_var = tk.StringVar(value="")
        ttk.Button(
            content_panel,
            text="✓ تأیید دستی SEO همین محصول",
            command=self._phase49_3i35_approve_seo,
            style="Success.TButton",
        ).pack(side="right", padx=3)
        ttk.Button(
            content_panel,
            text="بازبینی خودکار دوباره",
            command=self._phase49_3i35_reset_seo_review,
        ).pack(side="right", padx=3)
        ttk.Label(
            content_panel,
            textvariable=self._phase49_3i35_seo_review_var,
            style="SubHeader.TLabel",
        ).pack(side="left", padx=5)
        self._phase49_3i35_seo_review_panel = content_panel

        specs_panel = ttk.LabelFrame(
            self.specs_tab,
            text="منبع و مجوز — تکمیل، رفع نقص و بررسی دستی",
            padding=7,
            style="Card.TLabelframe",
        )
        specs_panel.pack(fill="x", pady=(0, 8))
        self._phase49_3i35_source_review_var = tk.StringVar(value="")
        ttk.Button(
            specs_panel,
            text="پر کردن از اطلاعات موجود",
            command=self._phase49_3i35_fill_source_existing,
            style="Primary.TButton",
        ).pack(side="right", padx=3)
        ttk.Button(
            specs_panel,
            text="رفع نقص متن/منبع با AI",
            command=lambda: self._phase49_3i33_run_ai("repair"),
        ).pack(side="right", padx=3)
        ttk.Button(
            specs_panel,
            text="✓ تأیید دستی بررسی منبع",
            command=self._phase49_3i35_approve_source_review,
            style="Success.TButton",
        ).pack(side="right", padx=3)
        ttk.Label(
            specs_panel,
            textvariable=self._phase49_3i35_source_review_var,
            style="SubHeader.TLabel",
            wraplength=650,
        ).pack(side="left", padx=5)
        self._phase49_3i35_source_review_panel = specs_panel

    def refresh_review_state(self):
        row = self.db.product(int(self.product_id))
        seo_manual = bool(int(_row_value(row, "seo_manual_approved", 0) or 0))
        source_manual = bool(int(_row_value(row, "source_review_manual_approved", 0) or 0))
        self._phase49_3i35_seo_review_var.set(
            "SEO توسط اپراتور تأیید شده است" if seo_manual
            else "اگر فیلدهای واقعی کامل‌اند ولی Checker تشخیص نمی‌دهد، تأیید دستی را بزن."
        )
        commercial = str(_row_value(row, "commercial_status", "review") or "review")
        self._phase49_3i35_source_review_var.set(
            ("بررسی دستی ثبت شده • " if source_manual else "")
            + f"وضعیت مجوز: {commercial} • تأیید دستی هرگز مجوز تجاری نامعتبر را دور نمی‌زند."
        )

    def approve_seo(self):
        row = self.db.product(int(self.product_id))
        title = str(_row_value(row, "title_fa", "") or "").strip()
        description = str(
            _row_value(row, "short_description_fa", "")
            or _row_value(row, "description_fa", "")
            or ""
        ).strip()
        if not title or not description:
            messagebox.showwarning(
                "تأیید SEO",
                "برای تأیید دستی هنوز عنوان فارسی و توضیح فارسی اصلی باید واقعاً ثبت شده باشند.",
                parent=self,
            )
            return False
        self.db.update_product(int(self.product_id), {"seo_manual_approved": 1})
        self.row = self.db.product(int(self.product_id))
        refresher = getattr(self, "_phase49_refresh_readiness", None)
        if callable(refresher):
            refresher()
        refresh_review_state(self)
        self.footer_status.set("SEO این محصول با تأیید اپراتور ثبت شد؛ AI دوباره فراخوانی نشد")
        return True

    def reset_seo_review(self):
        self.db.update_product(int(self.product_id), {"seo_manual_approved": 0})
        self.row = self.db.product(int(self.product_id))
        refresher = getattr(self, "_phase49_refresh_readiness", None)
        if callable(refresher):
            refresher()
        refresh_review_state(self)
        self.footer_status.set("تأیید دستی SEO برداشته شد؛ Checker دوباره فقط داده واقعی را می‌سنجد")
        return True

    def fill_source_existing(self):
        row = self.db.product(int(self.product_id))
        if row is None:
            return False
        updates = {}
        source_url = str(_row_value(row, "source_url", "") or "").strip()
        source_name = str(_row_value(row, "source_name", "") or "").strip()
        source_code = str(_row_value(row, "source_code", "") or "").strip()
        author = str(_row_value(row, "author_name", "") or "").strip()
        license_name = str(_row_value(row, "license_name", "") or "").strip()
        license_url = str(_row_value(row, "license_url", "") or "").strip()
        if not source_name and source_code:
            updates["source_name"] = source_code
        # Only mirror facts that already exist locally. License/legal status is
        # never invented or upgraded by this action.
        if updates:
            self.db.update_product(int(self.product_id), updates)
        self.row = self.db.product(int(self.product_id))
        self.footer_status.set(
            "اطلاعات منبع موجود بازهمگام شد"
            + (" • لینک موجود" if source_url else " • لینک منبع هنوز خالی است")
            + (" • طراح موجود" if author else "")
            + (" • نام مجوز موجود" if license_name else "")
            + (" • لینک مجوز موجود" if license_url else "")
        )
        refresh_review_state(self)
        return True

    def approve_source_review(self):
        row = self.db.product(int(self.product_id))
        source_url = str(_row_value(row, "source_url", "") or "").strip()
        if not source_url.startswith(("http://", "https://")):
            messagebox.showwarning(
                "بررسی منبع",
                "قبل از تأیید دستی، لینک معتبر منبع لازم است.",
                parent=self,
            )
            return False
        self.db.update_product(
            int(self.product_id),
            {
                "source_review_manual_approved": 1,
            },
        )
        self.row = self.db.product(int(self.product_id))
        refresher = getattr(self, "_phase49_refresh_readiness", None)
        if callable(refresher):
            refresher()
        refresh_review_state(self)
        self.footer_status.set(
            "بررسی دستی منبع ثبت شد؛ وضعیت مجوز تجاری همچنان Gate قانونی مستقل است"
        )
        return True

    def reload(self):
        result = original_reload(self)
        if hasattr(self, "_phase49_3i35_seo_review_var"):
            refresh_review_state(self)
        return result

    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class._phase49_3i35_build_review_controls = build_review_controls
    workspace_class._phase49_3i35_refresh_review_state = refresh_review_state
    workspace_class._phase49_3i35_approve_seo = approve_seo
    workspace_class._phase49_3i35_reset_seo_review = reset_seo_review
    workspace_class._phase49_3i35_fill_source_existing = fill_source_existing
    workspace_class._phase49_3i35_approve_source_review = approve_source_review
    workspace_class._phase49_3i35_readiness_review = True
