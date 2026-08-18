from __future__ import annotations

import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageFilter, ImageOps, ImageTk

from .epic49_desktop_schema import ensure_epic49_desktop_schema
from .epic49_server_slider_manager import EFFECTS, EFFECT_CODE, EFFECT_LABEL, open_server_slider_manager
from .epic49_site_sync import (
    apply_server_product_to_local,
    absorb_ack_revisions,
    get_product,
    list_products,
)
from .product_workspace_v871 import ProductWorkspace as ProductWorkspace871
from .version import APP_VERSION


class ProductWorkspace(ProductWorkspace871):
    """Epic49 unified employee workspace.

    Windows remains the primary operational editor. The website Admin is an equal
    secondary editor. This layer completes slider effects/timing, server refresh,
    optimistic revisions and a local cinematic preview without forking any of the
    existing 8.7.1 product/SEO/gallery/publish code.
    """

    def __init__(self, app, product_id: int):
        ensure_epic49_desktop_schema(app.db)
        self._preview_window = None
        self._preview_photo = None
        super().__init__(app, product_id)
        self.title(f"Product Workspace | 3DPrintHub Catalog Center {APP_VERSION} | Epic49 Unified")

    def _publish_ui(self):
        super()._publish_ui()

        cinema = ttk.LabelFrame(
            self.publish_tab,
            text="افکت سینمایی و همگام‌سازی اسلایدر",
            padding=10,
            style="Card.TLabelframe",
        )
        cinema.pack(fill="x", pady=(10, 0))
        cinema.columnconfigure(1, weight=1)
        cinema.columnconfigure(3, weight=1)

        self.slider_effect_var = tk.StringVar(value=EFFECT_LABEL["cinematic_fade"])
        self.slider_transition_ms_var = tk.StringVar(value="1400")
        self.slider_display_ms_var = tk.StringVar(value="7000")
        self.slider_server_revision_var = tk.StringVar(value="سایت: هنوز همگام نشده")

        ttk.Label(cinema, text="افکت تعویض").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Combobox(
            cinema,
            textvariable=self.slider_effect_var,
            values=[label for _code, label in EFFECTS],
            state="readonly",
            width=28,
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(cinema, text="Transition (ms)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Spinbox(
            cinema,
            from_=300,
            to=4000,
            increment=100,
            textvariable=self.slider_transition_ms_var,
            width=10,
        ).grid(row=0, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(cinema, text="مدت نمایش (ms)").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(
            cinema,
            from_=2000,
            to=30000,
            increment=500,
            textvariable=self.slider_display_ms_var,
            width=10,
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(cinema, textvariable=self.slider_server_revision_var, style="SubHeader.TLabel").grid(
            row=1, column=2, columnspan=2, sticky="e", padx=5, pady=5
        )

        actions = ttk.Frame(cinema)
        actions.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=(8, 2))
        ttk.Button(actions, text="▶ پیش‌نمایش افکت", command=self.preview_slider_effect).pack(side="left", padx=3)
        ttk.Button(actions, text="↻ دریافت نسخه فعلی این کالا از سایت", command=self.refresh_current_from_server).pack(side="left", padx=3)
        ttk.Button(actions, text="🌐 مدیریت همه اسلایدرهای سایت", command=self.open_all_server_sliders).pack(side="left", padx=3)
        ttk.Label(
            actions,
            text="اگر Admin سایت نسخه جدیدتری ذخیره کرده باشد، Publish قدیمی متوقف می‌شود تا ابتدا Refresh کنید.",
            style="SubHeader.TLabel",
        ).pack(side="right", padx=5)

    def _safe_int_range(self, value, default: int, minimum: int, maximum: int) -> int:
        try:
            parsed = int(float(str(value or default).replace(",", "")))
        except Exception:
            parsed = default
        return min(maximum, max(minimum, parsed))

    def _absorb_existing_ack(self, row):
        raw = str(row["server_ack_json"] or "").strip() if row is not None else ""
        if not raw:
            return
        try:
            payload = json.loads(raw)
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        if any(key in payload for key in ("product_revision", "slider_revision", "server_product_id", "product_id")):
            absorb_ack_revisions(self.db, self.product_id, payload)

    def reload(self):
        ensure_epic49_desktop_schema(self.db)
        row = self.db.product(self.product_id)
        if row is not None:
            self._absorb_existing_ack(row)
        super().reload()
        row = self.db.product(self.product_id)
        if row is None or not hasattr(self, "slider_effect_var"):
            return
        effect = str(row["homepage_slider_transition_effect"] or "cinematic_fade")
        self.slider_effect_var.set(EFFECT_LABEL.get(effect, EFFECT_LABEL["cinematic_fade"]))
        self.slider_transition_ms_var.set(str(self._safe_int_range(row["homepage_slider_transition_duration_ms"], 1400, 300, 4000)))
        self.slider_display_ms_var.set(str(self._safe_int_range(row["homepage_slider_display_duration_ms"], 7000, 2000, 30000)))
        product_revision = int(row["server_product_revision"] or 0)
        slider_revision = int(row["server_slider_revision"] or 0)
        if product_revision or slider_revision:
            self.slider_server_revision_var.set(
                f"Server Product rev {product_revision or '—'} • Hero rev {slider_revision or '—'}"
            )
        else:
            self.slider_server_revision_var.set("سایت: هنوز Revision دریافت نشده")

    def save(self, silent=False):
        if not super().save(silent=True):
            return False
        if not hasattr(self, "slider_effect_var"):
            return True
        effect = EFFECT_CODE.get(self.slider_effect_var.get(), "cinematic_fade")
        transition = self._safe_int_range(self.slider_transition_ms_var.get(), 1400, 300, 4000)
        display = self._safe_int_range(self.slider_display_ms_var.get(), 7000, 2000, 30000)
        self.db.update_product(
            self.product_id,
            {
                "homepage_slider_transition_effect": effect,
                "homepage_slider_transition_duration_ms": transition,
                "homepage_slider_display_duration_ms": display,
            },
        )
        self.row = self.db.product(self.product_id)
        if not silent:
            self.footer_status.set("محصول، SEO اسلایدر، افکت و زمان‌بندی ذخیره شد")
        return True

    # ---------- server refresh / slider manager ----------
    def _server_lookup(self, cfg, row):
        server_id = int(row["server_product_id"] or 0)
        if server_id:
            return get_product(cfg, server_id)
        query = str(row["external_id"] or row["source_title"] or row["title_fa"] or "").strip()
        candidates = list_products(cfg, query=query, limit=100)
        external_id = str(row["external_id"] or "").strip()
        if external_id:
            exact = next((item for item in candidates if str(item.get("source_external_id") or "") == external_id), None)
            if exact:
                return exact
        return candidates[0] if len(candidates) == 1 else None

    def refresh_current_from_server(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        if not messagebox.askyesno(
            "3DPrintHub",
            "نسخه قابل‌ویرایش سایت دریافت شود؟\n\n"
            "عنوان/توضیح فارسی، SEO، SEO اسلایدر، افکت و Revision محلی با نسخه سایت همگام می‌شوند.\n"
            "داده خام و لینک منبع اینترنتی تغییر نمی‌کنند.",
            parent=self,
        ):
            return
        try:
            cfg = self.app._site_connection(require_bridge=True)
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self)
            return
        self.footer_status.set("در حال دریافت نسخه فعلی از سایت…")

        def work():
            return self._server_lookup(cfg, row)

        def done(server, error):
            if error:
                self.footer_status.set("دریافت از سایت ناموفق")
                messagebox.showerror("3DPrintHub", str(error), parent=self)
                return
            if not server:
                self.footer_status.set("محصول متناظر روی سایت پیدا نشد")
                messagebox.showinfo("3DPrintHub", "برای این رکورد هنوز Product متناظر روی سایت پیدا نشد.", parent=self)
                return
            apply_server_product_to_local(self.db, self.product_id, server)
            self.reload()
            self.footer_status.set("نسخه سایت دریافت و روی فیلدهای قابل‌ویرایش اعمال شد")

        self._thread(work, done)

    def open_all_server_sliders(self):
        try:
            open_server_slider_manager(self.app, parent=self)
        except Exception as exc:
            messagebox.showerror("3DPrintHub", str(exc), parent=self)

    def _thread(self, work, done):
        def runner():
            try:
                value = work()
                self.after(0, lambda: done(value, None))
            except Exception as exc:
                self.after(0, lambda: done(None, exc))
        threading.Thread(target=runner, daemon=True).start()

    # ---------- local cinematic preview ----------
    def _preview_local_paths(self):
        cards = list(getattr(self, "_gallery_cards", []) or [])
        paths = []
        selected_url = str(self.db.product(self.product_id)["homepage_slider_image_url"] or "")
        ordered = sorted(cards, key=lambda item: 0 if item.get("url") == selected_url else 1)
        for item in ordered:
            local = str(item.get("local") or "").strip()
            if local and local not in paths:
                paths.append(local)
        return paths

    def preview_slider_effect(self):
        paths = self._preview_local_paths()
        if len(paths) < 2:
            messagebox.showinfo(
                "3DPrintHub",
                "برای پیش‌نمایش Transition حداقل دو تصویر محلی در صفحه فعلی گالری لازم است.",
                parent=self,
            )
            return
        try:
            first = Image.open(paths[0]).convert("RGB")
            second = Image.open(paths[1]).convert("RGB")
        except Exception as exc:
            messagebox.showerror("3DPrintHub", f"بازکردن تصویر Preview ناموفق بود:\n{exc}", parent=self)
            return

        size = (960, 540)
        first = ImageOps.fit(first, size, method=Image.Resampling.LANCZOS)
        second = ImageOps.fit(second, size, method=Image.Resampling.LANCZOS)
        effect = EFFECT_CODE.get(self.slider_effect_var.get(), "cinematic_fade")
        duration = self._safe_int_range(self.slider_transition_ms_var.get(), 1400, 300, 4000)

        if self._preview_window is not None:
            try:
                self._preview_window.destroy()
            except Exception:
                pass
        win = tk.Toplevel(self)
        self._preview_window = win
        win.title(f"پیش‌نمایش {EFFECT_LABEL.get(effect, effect)}")
        win.geometry("1000x640")
        win.configure(bg="#071827")
        label = tk.Label(win, bg="#071827")
        label.pack(fill="both", expand=True, padx=18, pady=(18, 6))
        tk.Label(
            win,
            text=f"{EFFECT_LABEL.get(effect, effect)} • Transition {duration}ms • Display {self.slider_display_ms_var.get()}ms",
            bg="#071827",
            fg="white",
            font=("Tahoma", 10, "bold"),
        ).pack(pady=(0, 12))

        frames = 24
        delay = max(20, duration // frames)

        def zoomed(image, scale):
            if scale <= 1:
                return image
            w, h = image.size
            nw, nh = max(w, int(w / scale)), max(h, int(h / scale))
            left = max(0, (w - nw) // 2)
            top = max(0, (h - nh) // 2)
            return image.crop((left, top, left + nw, top + nh)).resize((w, h), Image.Resampling.LANCZOS)

        def frame_at(index):
            t = index / frames
            if effect == "soft_blur":
                incoming = second.filter(ImageFilter.GaussianBlur(radius=max(0, (1 - t) * 12)))
                return Image.blend(first, incoming, t)
            if effect == "cinematic_zoom":
                outgoing = zoomed(first, 1 + 0.06 * t)
                incoming = zoomed(second, 1.06 - 0.06 * t)
                return Image.blend(outgoing, incoming, t)
            if effect == "ken_burns":
                outgoing = zoomed(first, 1 + 0.04 * t)
                incoming = zoomed(second, 1.04)
                return Image.blend(outgoing, incoming, t)
            if effect == "cinematic_reveal":
                canvas = first.copy()
                reveal = int(size[0] * t)
                if reveal > 0:
                    canvas.paste(second.crop((0, 0, reveal, size[1])), (0, 0))
                return canvas
            # Wedding dissolve is deliberately softer than cinematic fade.
            blend = t * t * (3 - 2 * t) if effect == "wedding_dissolve" else t
            return Image.blend(first, second, blend)

        def animate(index=0):
            if not win.winfo_exists():
                return
            image = frame_at(min(frames, index))
            photo = ImageTk.PhotoImage(image)
            self._preview_photo = photo
            label.configure(image=photo)
            if index < frames:
                win.after(delay, lambda: animate(index + 1))

        animate()
