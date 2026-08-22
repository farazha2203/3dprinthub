from __future__ import annotations

import hashlib
import json
import time
import tkinter as tk
from tkinter import messagebox, ttk

from . import phase49_3e_ai_task_center as task_center
from . import phase49_3f_runtime_trace as runtime_trace


DESKTOP_COLUMNS = {
    "ai_provenance_json": "TEXT NOT NULL DEFAULT '{}'",
    "ai_disabled_groups_json": "TEXT NOT NULL DEFAULT '[]'",
}

GROUP_LABELS = {
    "persian_content": "متن فارسی",
    "product_seo": "SEO محصول",
    "image_seo": "SEO تصاویر منتخب",
    "materials": "پیشنهاد متریال",
    "slider_seo": "SEO اسلایدر",
}

GROUP_FIELDS = {
    "persian_content": (
        "title_fa",
        "short_description_fa",
        "description_fa",
        "use_description",
    ),
    "product_seo": (
        "seo_title_fa",
        "seo_description_fa",
        "keywords_json",
        "tags_fa_json",
        "hashtags_fa_json",
    ),
    "image_seo": (
        "image_alt_texts_json",
        "image_metadata_json",
        "image_seo_manifest_json",
    ),
    "materials": ("material_recommendations_json",),
    "slider_seo": (
        "homepage_slider_title_fa",
        "homepage_slider_description_fa",
        "homepage_slider_alt_text",
        "homepage_slider_button_text",
        "homepage_slider_focus_keyword",
        "homepage_slider_image_url",
    ),
}

SCROLL_SKIP_CLASSES = {"Text", "Listbox", "Treeview", "Canvas"}


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


def _json_dict(value) -> dict:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def ensure_schema(db) -> None:
    columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
    for name, ddl in DESKTOP_COLUMNS.items():
        if name not in columns:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
    db.conn.commit()


def _canonical_value(value):
    if isinstance(value, (dict, list, tuple)):
        return value
    text = str(value or "").strip()
    if not text:
        return ""
    if text[:1] in "[{":
        try:
            return json.loads(text)
        except Exception:
            return text
    return text


def group_snapshot(row, group: str) -> str:
    payload = {
        key: _canonical_value(_row_value(row, key, ""))
        for key in GROUP_FIELDS.get(group, ())
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def group_changed_fields(before, after, group: str) -> list[str]:
    changed = []
    for key in GROUP_FIELDS.get(group, ()):
        if _canonical_value(_row_value(before, key, "")) != _canonical_value(_row_value(after, key, "")):
            changed.append(key)
    return changed


def provenance_map(row) -> dict:
    return _json_dict(_row_value(row, "ai_provenance_json", "{}"))


def disabled_groups(row) -> set[str]:
    return {
        str(item or "").strip()
        for item in _json_list(_row_value(row, "ai_disabled_groups_json", "[]"))
        if str(item or "").strip() in GROUP_FIELDS
    }


def ai_group_locked(row, group: str) -> bool:
    if group in disabled_groups(row):
        return True
    record = provenance_map(row).get(group)
    return bool(isinstance(record, dict) and record.get("manual_override"))


def filter_updates_for_ai_ownership(row, updates: dict) -> dict:
    """Protect operator-owned or explicitly disabled groups from AI writes."""
    output = dict(updates or {})
    for group, fields in GROUP_FIELDS.items():
        if not ai_group_locked(row, group):
            continue
        for field in fields:
            output.pop(field, None)
    return output


def _provenance_label(row, group: str) -> str:
    label = GROUP_LABELS[group]
    record = provenance_map(row).get(group)
    if group in disabled_groups(row):
        return f"⛔ {label}: AI خاموش"
    if isinstance(record, dict) and record.get("manual_override"):
        return f"✎ {label}: ویرایش دستی؛ AI قفل"
    if isinstance(record, dict) and record.get("source") == "ai":
        provider = str(record.get("provider") or "AI")
        model = str(record.get("model") or "").strip()
        return f"🤖 {label}: توسط {provider}" + (f" / {model}" if model else "")
    return f"○ {label}: هنوز مالکیت AI ثبت نشده"


def install(workspace_class, readiness_module=None) -> None:
    if getattr(workspace_class, "_phase49_3g_workspace_installed", False):
        return

    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_save = workspace_class.save
    original_select_section = workspace_class.select_section
    original_refresh_gallery = workspace_class.refresh_gallery
    original_run_ai = getattr(workspace_class, "_phase49_3e_run_ai", None)
    original_apply_full_ai = getattr(workspace_class, "_phase49_3f_apply_full_ai", None)
    original_apply_image_ai = getattr(workspace_class, "_phase49_3f_apply_selected_image_ai", None)
    original_refresh_tasks = getattr(workspace_class, "_phase49_3e_refresh_tasks", None)
    original_build_updates = task_center.build_ai_updates

    def build_ai_updates(row, pack: dict, *, scope: str = "all") -> dict:
        updates = original_build_updates(row, pack, scope=scope)
        return filter_updates_for_ai_ownership(row, updates)

    task_center.build_ai_updates = build_ai_updates

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        self._phase49_3g_scroll_offset = 0
        self._phase49_3g_scroll_height = 1
        self._phase49_3g_provenance_vars = {}
        original_init(self, app, product_id)
        self._phase49_3g_enable_workspace_scroll()
        self._phase49_3g_enable_gallery_scroll()
        self._phase49_3g_compact_commerce()
        self._phase49_3g_add_autofill_controls()
        self._phase49_3g_add_provenance_panels()
        self._phase49_3g_refresh_provenance()
        self.after(120, self._phase49_3g_refresh_workspace_scroll)
        runtime_trace.event("workspace", "phase49-3g-ready", product_id=self.product_id, detail={"scroll": True, "gallery_horizontal": True, "ai_provenance": True})

    def _phase49_3g_enable_workspace_scroll(self):
        nb = getattr(self, "nb", None)
        if nb is None or getattr(self, "_phase49_3g_workspace_scrollbar", None) is not None:
            return
        host = nb.master
        try:
            nb.pack_forget()
        except Exception:
            pass
        self._phase49_3g_workspace_host = host
        self._phase49_3g_workspace_scrollbar = ttk.Scrollbar(host, orient="vertical", command=self._phase49_3g_scroll_command)
        self._phase49_3g_workspace_scrollbar.place(relx=1.0, x=-17, y=0, relheight=1.0, width=17)
        nb.place(x=0, y=0, relwidth=1.0, width=-19)
        host.bind("<Configure>", lambda _event: self.after_idle(self._phase49_3g_refresh_workspace_scroll), add="+")
        nb.bind("<<NotebookTabChanged>>", lambda _event: self.after_idle(self._phase49_3g_reset_section_scroll), add="+")
        self.bind("<MouseWheel>", self._phase49_3g_mousewheel, add="+")
        self.bind("<Button-4>", self._phase49_3g_mousewheel, add="+")
        self.bind("<Button-5>", self._phase49_3g_mousewheel, add="+")

    def _phase49_3g_reset_section_scroll(self):
        self._phase49_3g_scroll_offset = 0
        self._phase49_3g_refresh_workspace_scroll()

    def _phase49_3g_refresh_workspace_scroll(self):
        host = getattr(self, "_phase49_3g_workspace_host", None)
        nb = getattr(self, "nb", None)
        bar = getattr(self, "_phase49_3g_workspace_scrollbar", None)
        if host is None or nb is None or bar is None:
            return
        try:
            host.update_idletasks()
            nb.update_idletasks()
            viewport = max(1, int(host.winfo_height()))
            requested = max(viewport, int(nb.winfo_reqheight()))
            self._phase49_3g_scroll_height = requested
            maximum = max(0, requested - viewport)
            self._phase49_3g_scroll_offset = max(0, min(int(self._phase49_3g_scroll_offset), maximum))
            nb.place_configure(y=-self._phase49_3g_scroll_offset, height=requested)
            first = (self._phase49_3g_scroll_offset / requested) if requested else 0.0
            last = min(1.0, (self._phase49_3g_scroll_offset + viewport) / requested) if requested else 1.0
            bar.set(first, last)
        except Exception:
            return

    def _phase49_3g_scroll_command(self, *args):
        host = getattr(self, "_phase49_3g_workspace_host", None)
        if host is None:
            return
        viewport = max(1, int(host.winfo_height()))
        requested = max(viewport, int(getattr(self, "_phase49_3g_scroll_height", viewport)))
        maximum = max(0, requested - viewport)
        offset = int(getattr(self, "_phase49_3g_scroll_offset", 0))
        if args and args[0] == "moveto":
            offset = int(float(args[1]) * maximum)
        elif args and args[0] == "scroll":
            amount = int(args[1])
            unit = args[2]
            step = max(40, int(viewport * 0.85)) if unit == "pages" else 48
            offset += amount * step
        self._phase49_3g_scroll_offset = max(0, min(offset, maximum))
        self._phase49_3g_refresh_workspace_scroll()

    def _phase49_3g_mousewheel(self, event):
        try:
            widget_class = str(event.widget.winfo_class())
        except Exception:
            widget_class = ""
        if widget_class in SCROLL_SKIP_CLASSES:
            return None
        delta = 0
        if getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        elif getattr(event, "delta", 0):
            delta = -1 if event.delta > 0 else 1
        if delta:
            self._phase49_3g_scroll_command("scroll", delta, "units")
            return "break"
        return None

    def _phase49_3g_enable_gallery_scroll(self):
        canvas = getattr(self, "gallery_canvas", None)
        if canvas is None or getattr(self, "_phase49_3g_gallery_hbar", None) is not None:
            return
        shell = canvas.master
        children = list(shell.winfo_children())
        vertical = next((child for child in children if isinstance(child, ttk.Scrollbar)), None)
        for child in children:
            try:
                child.pack_forget()
            except Exception:
                pass
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        canvas.grid(row=0, column=0, sticky="nsew")
        if vertical is not None:
            vertical.configure(command=canvas.yview)
            vertical.grid(row=0, column=1, sticky="ns")
        hbar = ttk.Scrollbar(shell, orient="horizontal", command=canvas.xview)
        hbar.grid(row=1, column=0, sticky="ew")
        self._phase49_3g_gallery_hbar = hbar
        canvas.configure(xscrollcommand=hbar.set, height=350, xscrollincrement=48)
        try:
            canvas.unbind("<Configure>")
        except Exception:
            pass
        canvas.bind("<Shift-MouseWheel>", self._phase49_3g_gallery_mousewheel, add="+")
        canvas.bind("<MouseWheel>", self._phase49_3g_gallery_mousewheel, add="+")
        self.after_idle(self._phase49_3g_layout_gallery_cards)

    def _phase49_3g_gallery_mousewheel(self, event):
        delta = -1 if getattr(event, "delta", 0) > 0 else 1
        if getattr(event, "num", None) == 4:
            delta = -1
        elif getattr(event, "num", None) == 5:
            delta = 1
        try:
            self.gallery_canvas.xview_scroll(delta, "units")
        except Exception:
            pass
        return "break"

    def _phase49_3g_layout_gallery_cards(self, preserve_fraction: float | None = None):
        inner = getattr(self, "gallery_inner", None)
        canvas = getattr(self, "gallery_canvas", None)
        if inner is None or canvas is None:
            return
        cards = list(getattr(self, "_gallery_cards", []) or [])
        for index, meta in enumerate(cards):
            label = meta.get("label")
            card = label.master if label is not None else None
            if card is None:
                continue
            try:
                card.grid_forget()
                card.grid(row=0, column=index, padx=7, pady=7, sticky="n")
                inner.columnconfigure(index, weight=0, minsize=235)
            except Exception:
                continue
        try:
            inner.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            if preserve_fraction is not None:
                canvas.xview_moveto(max(0.0, min(float(preserve_fraction), 1.0)))
        except Exception:
            pass

    def refresh_gallery(self):
        fraction = 0.0
        try:
            fraction = float(self.gallery_canvas.xview()[0])
        except Exception:
            pass
        result = original_refresh_gallery(self)
        if hasattr(self, "gallery_canvas"):
            self.after_idle(lambda: self._phase49_3g_layout_gallery_cards(fraction))
        return result

    def _phase49_3g_compact_commerce(self):
        frame = getattr(self, "commerce_tab", None)
        if frame is None:
            return
        for row_index in range(0, 24):
            try:
                frame.rowconfigure(row_index, weight=0)
            except Exception:
                pass
        for widget_name, height in (
            ("use_description_text", 3),
            ("materials_text", 3),
            ("colors_text", 3),
            ("technical_features_text", 5),
            ("keywords_text", 5),
        ):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                try:
                    widget.configure(height=height)
                except Exception:
                    pass
        tree = getattr(self, "material_rate_tree", None)
        if tree is not None:
            try:
                tree.configure(height=4)
            except Exception:
                pass
        panel = getattr(self, "_phase49_3f_pricing_panel", None)
        if panel is not None:
            try:
                panel.configure(padding=6)
            except Exception:
                pass
        self.after_idle(self._phase49_3g_refresh_workspace_scroll)

    def _phase49_3g_add_autofill_controls(self):
        # Canonical rail action: rename the existing mature Task Center action.
        for widget in self.winfo_children():
            pass
        for widget in self._phase49_3g_walk(self):
            if not isinstance(widget, ttk.Button):
                continue
            try:
                if str(widget.cget("text")) == "✨ انجام وظایف ناقص AI":
                    widget.configure(text="✨ تکمیل هوشمند محصول با AI", command=self._phase49_3g_autofill)
            except Exception:
                pass

        quick = getattr(self, "quick_tab", None)
        if quick is None:
            return
        used = [int(child.grid_info().get("row", 0)) for child in quick.grid_slaves() if child.grid_info()]
        row = (max(used) + 1) if used else 7
        frame = ttk.LabelFrame(quick, text="دستیار هوشمند محصول", padding=8, style="Card.TLabelframe")
        frame.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        self._phase49_3g_autofill_summary = tk.StringVar(value="AI فقط فیلدهای خالی و مجاز را تکمیل می‌کند؛ تأیید فروش/مجوز/قیمت قطعی را تغییر نمی‌دهد.")
        ttk.Label(frame, textvariable=self._phase49_3g_autofill_summary, style="SubHeader.TLabel", wraplength=900).pack(side="right", padx=6)
        ttk.Button(frame, text="✨ تکمیل هوشمند محصول با AI", command=self._phase49_3g_autofill, style="Success.TButton").pack(side="left", padx=3)

    def _phase49_3g_walk(self, root):
        for child in root.winfo_children():
            yield child
            yield from self._phase49_3g_walk(child)

    def _phase49_3g_add_provenance_panels(self):
        specs = (
            ("content", getattr(self, "content_tab", None), ("persian_content", "product_seo")),
            ("images", getattr(self, "images_tab", None), ("image_seo",)),
            ("publish", getattr(self, "publish_tab", None), ("slider_seo",)),
        )
        for _key, parent, groups in specs:
            if parent is None:
                continue
            children = list(parent.winfo_children())
            before = children[0] if children else None
            frame = ttk.LabelFrame(parent, text="مالکیت و وضعیت هوش مصنوعی", padding=6, style="Card.TLabelframe")
            kwargs = {"fill": "x", "pady": (0, 7)}
            if before is not None:
                kwargs["before"] = before
            try:
                frame.pack(**kwargs)
            except Exception:
                continue
            for group in groups:
                row = ttk.Frame(frame)
                row.pack(fill="x", pady=2)
                var = tk.StringVar(value="")
                self._phase49_3g_provenance_vars[group] = var
                ttk.Label(row, textvariable=var, style="SubHeader.TLabel").pack(side="right", fill="x", expand=True, padx=5)
                ttk.Button(row, text="خاموش/روشن AI", command=lambda g=group: self._phase49_3g_toggle_group(g)).pack(side="left", padx=3)
                ttk.Button(row, text="اجازه بازنویسی AI", command=lambda g=group: self._phase49_3g_allow_rewrite(g)).pack(side="left", padx=3)

    def _phase49_3g_autofill(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        tasks = task_center.evaluate_ai_tasks(row)
        missing_groups = [task["key"] for task in tasks if task["status"] == "missing"]
        available = [group for group in missing_groups if not ai_group_locked(row, group)]
        if not missing_groups:
            messagebox.showinfo("3DPrintHub", "✅ همه وظایف AI/SEO قابل‌اجرا برای این محصول کامل هستند.", parent=self)
            return
        if not available:
            messagebox.showwarning("3DPrintHub", "همه گروه‌های ناقص توسط اپراتور برای AI قفل/خاموش شده‌اند. از دکمه «اجازه بازنویسی AI» استفاده کن.", parent=self)
            return
        runtime_trace.event("ai", "phase49-3g-autofill", product_id=self.product_id, detail={"missing": missing_groups, "available": available})
        return self._phase49_3e_run_ai("all")

    def _phase49_3g_toggle_group(self, group: str):
        row = self.db.product(self.product_id)
        disabled = disabled_groups(row)
        if group in disabled:
            disabled.remove(group)
        else:
            disabled.add(group)
        self.db.update_product(self.product_id, {"ai_disabled_groups_json": json.dumps(sorted(disabled), ensure_ascii=False)})
        self._phase49_3g_refresh_provenance()
        try:
            self._phase49_3e_refresh_tasks()
        except Exception:
            pass

    def _phase49_3g_allow_rewrite(self, group: str):
        row = self.db.product(self.product_id)
        disabled = disabled_groups(row)
        disabled.discard(group)
        provenance = provenance_map(row)
        record = provenance.get(group)
        if isinstance(record, dict):
            record["manual_override"] = False
            record["allow_ai_rewrite"] = True
            provenance[group] = record
        self.db.update_product(self.product_id, {
            "ai_disabled_groups_json": json.dumps(sorted(disabled), ensure_ascii=False),
            "ai_provenance_json": json.dumps(provenance, ensure_ascii=False),
        })
        self._phase49_3g_refresh_provenance()

    def _phase49_3g_record_ai_changes(self, before, after, provider: str, model: str):
        provenance = provenance_map(after)
        disabled = disabled_groups(after)
        changed_groups = []
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for group in GROUP_FIELDS:
            if group in disabled:
                continue
            changed = group_changed_fields(before, after, group)
            if not changed:
                continue
            provenance[group] = {
                "source": "ai",
                "provider": str(provider or ""),
                "model": str(model or ""),
                "at": now,
                "fields": changed,
                "snapshot_hash": group_snapshot(after, group),
                "manual_override": False,
                "allow_ai_rewrite": False,
            }
            changed_groups.append(group)
        if changed_groups:
            self.db.update_product(self.product_id, {"ai_provenance_json": json.dumps(provenance, ensure_ascii=False)})
            runtime_trace.event("ai", "phase49-3g-provenance", product_id=self.product_id, provider=provider, model=model, detail={"groups": changed_groups})
        self._phase49_3g_refresh_provenance()

    def _phase49_3g_mark_manual_overrides(self, row):
        provenance = provenance_map(row)
        changed = False
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for group, record in list(provenance.items()):
            if not isinstance(record, dict) or record.get("source") != "ai":
                continue
            expected = str(record.get("snapshot_hash") or "")
            if not expected or expected == group_snapshot(row, group):
                continue
            record.update({"source": "manual", "manual_override": True, "manual_at": now, "allow_ai_rewrite": False})
            provenance[group] = record
            changed = True
        if changed:
            self.db.update_product(self.product_id, {"ai_provenance_json": json.dumps(provenance, ensure_ascii=False)})
        return changed

    def _phase49_3g_refresh_provenance(self):
        row = self.db.product(self.product_id)
        if row is None:
            return
        for group, var in getattr(self, "_phase49_3g_provenance_vars", {}).items():
            var.set(_provenance_label(row, group))
        tasks_widget = getattr(self, "_phase49_3e_tasks", None)
        records = list(getattr(self, "_phase49_3e_task_records", []) or [])
        if tasks_widget is not None and records:
            try:
                tasks_widget.delete(0, "end")
                for task in records:
                    icon = "✅" if task["status"] == "done" else ("➖" if task["status"] == "skipped" else "❌")
                    suffix = "" if not task["missing"] else " • " + "، ".join(task["missing"][:2])
                    owner = _provenance_label(row, task["key"]).split(":", 1)[-1].strip()
                    tasks_widget.insert("end", f"{icon} {task['label']} • {owner}{suffix}")
            except Exception:
                pass
        summary = getattr(self, "_phase49_3g_autofill_summary", None)
        if summary is not None:
            locked = [GROUP_LABELS[group] for group in GROUP_FIELDS if ai_group_locked(row, group)]
            summary.set("AI فقط فیلدهای خالی و مجاز را تکمیل می‌کند." + (" گروه‌های قفل‌شده: " + "، ".join(locked) if locked else " هیچ گروهی برای AI قفل نیست."))

    def _phase49_3e_run_ai(self, scope: str):
        row = self.db.product(self.product_id)
        if scope == "images" and ai_group_locked(row, "image_seo"):
            messagebox.showwarning("3DPrintHub", "SEO تصاویر برای AI توسط اپراتور خاموش/قفل شده است. ابتدا «اجازه بازنویسی AI» را بزن.", parent=self)
            return
        if original_run_ai is None:
            return None
        return original_run_ai(self, scope)

    def _phase49_3f_apply_full_ai(self, pack, scope, progress, provider, model, started):
        before = self.db.product(self.product_id)
        result = original_apply_full_ai(self, pack, scope, progress, provider, model, started) if original_apply_full_ai else None
        after = self.db.product(self.product_id)
        if before is not None and after is not None:
            self._phase49_3g_record_ai_changes(before, after, provider, model)
        return result

    def _phase49_3f_apply_selected_image_ai(self, pack, selected, progress, provider, model, started):
        before = self.db.product(self.product_id)
        result = original_apply_image_ai(self, pack, selected, progress, provider, model, started) if original_apply_image_ai else None
        after = self.db.product(self.product_id)
        if before is not None and after is not None:
            self._phase49_3g_record_ai_changes(before, after, provider, model)
        return result

    def _phase49_3e_refresh_tasks(self):
        result = original_refresh_tasks(self) if original_refresh_tasks else None
        self._phase49_3g_refresh_provenance()
        return result

    def reload(self):
        result = original_reload(self)
        ensure_schema(self.db)
        self.after_idle(self._phase49_3g_refresh_provenance)
        self.after_idle(self._phase49_3g_refresh_workspace_scroll)
        return result

    def save(self, silent=False):
        result = original_save(self, silent=silent)
        if result:
            ensure_schema(self.db)
            row = self.db.product(self.product_id)
            if row is not None and self._phase49_3g_mark_manual_overrides(row):
                self.row = self.db.product(self.product_id)
            self._phase49_3g_refresh_provenance()
        return result

    def select_section(self, key: str):
        result = original_select_section(self, key)
        self._phase49_3g_scroll_offset = 0
        self.after_idle(self._phase49_3g_refresh_workspace_scroll)
        return result

    workspace_class.__init__ = __init__
    workspace_class.reload = reload
    workspace_class.save = save
    workspace_class.select_section = select_section
    workspace_class.refresh_gallery = refresh_gallery
    workspace_class._phase49_3g_enable_workspace_scroll = _phase49_3g_enable_workspace_scroll
    workspace_class._phase49_3g_reset_section_scroll = _phase49_3g_reset_section_scroll
    workspace_class._phase49_3g_refresh_workspace_scroll = _phase49_3g_refresh_workspace_scroll
    workspace_class._phase49_3g_scroll_command = _phase49_3g_scroll_command
    workspace_class._phase49_3g_mousewheel = _phase49_3g_mousewheel
    workspace_class._phase49_3g_enable_gallery_scroll = _phase49_3g_enable_gallery_scroll
    workspace_class._phase49_3g_gallery_mousewheel = _phase49_3g_gallery_mousewheel
    workspace_class._phase49_3g_layout_gallery_cards = _phase49_3g_layout_gallery_cards
    workspace_class._phase49_3g_compact_commerce = _phase49_3g_compact_commerce
    workspace_class._phase49_3g_add_autofill_controls = _phase49_3g_add_autofill_controls
    workspace_class._phase49_3g_walk = _phase49_3g_walk
    workspace_class._phase49_3g_add_provenance_panels = _phase49_3g_add_provenance_panels
    workspace_class._phase49_3g_autofill = _phase49_3g_autofill
    workspace_class._phase49_3g_toggle_group = _phase49_3g_toggle_group
    workspace_class._phase49_3g_allow_rewrite = _phase49_3g_allow_rewrite
    workspace_class._phase49_3g_record_ai_changes = _phase49_3g_record_ai_changes
    workspace_class._phase49_3g_mark_manual_overrides = _phase49_3g_mark_manual_overrides
    workspace_class._phase49_3g_refresh_provenance = _phase49_3g_refresh_provenance
    if original_run_ai is not None:
        workspace_class._phase49_3e_run_ai = _phase49_3e_run_ai
    if original_apply_full_ai is not None:
        workspace_class._phase49_3f_apply_full_ai = _phase49_3f_apply_full_ai
    if original_apply_image_ai is not None:
        workspace_class._phase49_3f_apply_selected_image_ai = _phase49_3f_apply_selected_image_ai
    if original_refresh_tasks is not None:
        workspace_class._phase49_3e_refresh_tasks = _phase49_3e_refresh_tasks
    workspace_class._phase49_3g_workspace_installed = True
