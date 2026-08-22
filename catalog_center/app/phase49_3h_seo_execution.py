from __future__ import annotations

import json
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Any

from . import phase49_3e_ai_task_center as task_center
from . import phase49_3f_runtime_trace as runtime_trace
from .runtime_logging import redact
from . import phase49_3h_cost_ledger as cost_ledger

TRACKED_FIELDS = (
    "title_fa", "short_description_fa", "description_fa", "use_description",
    "seo_title_fa", "seo_description_fa", "keywords_json", "tags_fa_json", "hashtags_fa_json",
    "image_alt_texts_json", "image_metadata_json", "image_seo_manifest_json",
    "material_recommendations_json", "technical_summary_fa", "technical_features_json",
    "homepage_slider_title_fa", "homepage_slider_description_fa", "homepage_slider_alt_text",
    "homepage_slider_button_text", "homepage_slider_focus_keyword", "homepage_slider_image_url",
)


def _row_value(row, key: str, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        value = row[key]
    except Exception:
        value = default
    return default if value is None else value


def _row_snapshot(row) -> dict:
    return {key: _row_value(row, key, "") for key in TRACKED_FIELDS}


def changed_fields(before: dict, after) -> list[str]:
    return [key for key in TRACKED_FIELDS if before.get(key, "") != _row_value(after, key, "")]


def ensure_schema(db) -> None:
    cost_ledger.ensure_schema(db)
    db.conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS seo_execution_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            action_key TEXT NOT NULL DEFAULT '',
            scope TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT '',
            provider TEXT NOT NULL DEFAULT '',
            model TEXT NOT NULL DEFAULT '',
            elapsed_ms INTEGER NOT NULL DEFAULT 0,
            request_from_id INTEGER NOT NULL DEFAULT 0,
            request_to_id INTEGER NOT NULL DEFAULT 0,
            steps_json TEXT NOT NULL DEFAULT '[]',
            result_json TEXT NOT NULL DEFAULT '{}',
            cost_json TEXT NOT NULL DEFAULT '{}',
            error_text TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ix_seo_execution_product
            ON seo_execution_results(product_id, id DESC);
        """
    )
    db.conn.commit()


def _action_from_title(title: str) -> tuple[str, str]:
    text = str(title or "")
    if "تصاویر" in text or "تصویر" in text:
        return "image_seo", "images"
    if "توضیحات فنی" in text or "منبع" in text:
        return "technical_ai", "specs"
    if "اسلایدر" in text:
        return "slider_seo", "publish"
    return "product_ai", "content"


def _safe_exists(widget) -> bool:
    try:
        return bool(widget.winfo_exists())
    except Exception:
        return False


def _remaining_tasks(row, action_key: str) -> list[dict]:
    tasks = task_center.evaluate_ai_tasks(row)
    if action_key == "image_seo":
        return [task for task in tasks if task["key"] == "image_seo" and task["status"] == "missing"]
    if action_key == "slider_seo":
        return [task for task in tasks if task["key"] == "slider_seo" and task["status"] == "missing"]
    if action_key == "technical_ai":
        return [] if str(_row_value(row, "technical_summary_fa", "") or "").strip() else [{"label": "توضیحات فنی", "missing": ["خلاصه فنی فارسی"]}]
    return [task for task in tasks if task["status"] == "missing"]


def _persist_result(db, context: dict, *, status: str, label: str, detail: str, error_text: str = "") -> int:
    ensure_schema(db)
    product_id = int(context["product_id"])
    end_id = cost_ledger.max_request_id(db, product_id)
    cost = cost_ledger.aggregate_product(db, product_id, after_id=int(context.get("request_from_id") or 0), through_id=end_id)
    row = db.product(product_id)
    changed = changed_fields(context.get("before") or {}, row)
    remaining = _remaining_tasks(row, str(context.get("action_key") or ""))
    payload = {
        "label": str(label or ""),
        "detail": str(detail or ""),
        "changed_fields": changed,
        "remaining": [
            {"label": str(item.get("label") or item.get("key") or ""), "missing": list(item.get("missing") or [])}
            for item in remaining
        ],
        "log_path": str(runtime_trace.current_log_path()),
        "request_ids": list(cost.get("request_ids") or []),
    }
    created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cursor = db.conn.execute(
        """
        INSERT INTO seo_execution_results(
            product_id,action_key,scope,status,provider,model,elapsed_ms,
            request_from_id,request_to_id,steps_json,result_json,cost_json,error_text,created_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            product_id, str(context.get("action_key") or ""), str(context.get("scope") or ""),
            str(status or ""), str(context.get("provider") or ""), str(context.get("model") or ""),
            int(context.get("elapsed_ms") or 0), int(context.get("request_from_id") or 0), end_id,
            json.dumps(context.get("steps") or [], ensure_ascii=False, default=str),
            json.dumps(payload, ensure_ascii=False, default=str),
            json.dumps(cost, ensure_ascii=False, default=str), redact(error_text)[:8000], created_at,
        ),
    )
    db.conn.commit()
    return int(cursor.lastrowid)


def get_result(db, result_id: int) -> dict | None:
    ensure_schema(db)
    row = db.conn.execute("SELECT * FROM seo_execution_results WHERE id=?", (int(result_id),)).fetchone()
    if row is None:
        return None
    output = dict(row)
    for key in ("steps_json", "result_json", "cost_json"):
        try:
            output[key[:-5] if key.endswith("_json") else key] = json.loads(output.get(key) or ("[]" if key == "steps_json" else "{}"))
        except Exception:
            output[key[:-5] if key.endswith("_json") else key] = [] if key == "steps_json" else {}
    return output


def latest_result(db, product_id: int, action_key: str = "") -> dict | None:
    ensure_schema(db)
    if action_key:
        row = db.conn.execute(
            "SELECT id FROM seo_execution_results WHERE product_id=? AND action_key=? ORDER BY id DESC LIMIT 1",
            (int(product_id), str(action_key)),
        ).fetchone()
    else:
        row = db.conn.execute(
            "SELECT id FROM seo_execution_results WHERE product_id=? ORDER BY id DESC LIMIT 1",
            (int(product_id),),
        ).fetchone()
    return get_result(db, int(row["id"])) if row is not None else None


def format_result(result: dict) -> str:
    payload = result.get("result") or {}
    cost = result.get("cost") or {}
    steps = result.get("steps") or []
    lines = [
        f"وضعیت: {result.get('status') or '—'}",
        f"Provider / Model: {result.get('provider') or '—'} / {result.get('model') or '—'}",
        f"زمان اجرا: {int(result.get('elapsed_ms') or 0):,} ms",
        cost_ledger.format_cost_summary(cost),
    ]
    request_ids = payload.get("request_ids") or []
    if request_ids:
        lines.append("Request ID: " + "، ".join(str(x) for x in request_ids[-4:]))
    changed = payload.get("changed_fields") or []
    lines.append("فیلدهای تغییرکرده: " + ("، ".join(changed) if changed else "هیچ فیلدی تغییر نکرد"))
    remaining = payload.get("remaining") or []
    if remaining:
        lines.append("موارد باقی‌مانده:")
        for item in remaining:
            lines.append(f"- {item.get('label')}: " + "، ".join(item.get("missing") or []))
    if result.get("error_text"):
        lines.append("خطا: " + redact(result.get("error_text")))
    lines.append("مسیر لاگ: " + str(payload.get("log_path") or runtime_trace.current_log_path()))
    if steps:
        lines.append("مراحل اجرا:")
        for item in steps:
            lines.append(f"- {item.get('label') or ''}" + (f" | {item.get('detail')}" if item.get("detail") else ""))
    return "\n".join(lines)


def install_progress(phase49_3f_workspace_module) -> None:
    if getattr(phase49_3f_workspace_module, "_phase49_3h_progress_installed", False):
        return
    BaseProgress = phase49_3f_workspace_module.AIProgress

    class SEOExecutionProgress(BaseProgress):
        def __init__(self, parent, title: str, product_id: int | None = None):
            super().__init__(parent, title, product_id)
            self._phase49_3h_context = None
            if product_id is not None and hasattr(parent, "_phase49_3h_begin_execution"):
                try:
                    self._phase49_3h_context = parent._phase49_3h_begin_execution(title)
                except Exception:
                    self._phase49_3h_context = None

        def step(self, label: str, detail: str = ""):
            if _safe_exists(self.win):
                super().step(label, detail)
            if self._phase49_3h_context and hasattr(self.parent, "_phase49_3h_execution_step"):
                self.parent._phase49_3h_execution_step(self._phase49_3h_context, label, detail)

        def done(self, label="✅ عملیات کامل شد", detail=""):
            if _safe_exists(self.win):
                BaseProgress.done(self, label, detail)
            if self._phase49_3h_context and hasattr(self.parent, "_phase49_3h_execution_finish"):
                self.parent._phase49_3h_execution_finish(self._phase49_3h_context, "ok", label, detail, "")
            if _safe_exists(self.win):
                try:
                    self.win.after(900, self.close)
                except Exception:
                    pass

        def fail(self, message: str):
            clean = redact(message)
            if _safe_exists(self.win):
                BaseProgress.done(self, "❌ عملیات متوقف شد", clean)
            if self._phase49_3h_context and hasattr(self.parent, "_phase49_3h_execution_finish"):
                self.parent._phase49_3h_execution_finish(self._phase49_3h_context, "error", "❌ عملیات متوقف شد", clean, clean)
            # Error progress intentionally remains open for operator review.

    phase49_3f_workspace_module.AIProgress = SEOExecutionProgress
    phase49_3f_workspace_module._phase49_3h_progress_installed = True


def install_workspace(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3h_execution_installed", False):
        return
    original_init = workspace_class.__init__
    original_reload = workspace_class.reload
    original_finalize_images = getattr(workspace_class, "phase49_3c_finalize_images", None)
    original_publish_local = getattr(workspace_class, "publish_to_local_computer", None)
    original_publish_production = getattr(workspace_class, "publish_to_production_site", None)

    def __init__(self, app, product_id: int):
        ensure_schema(app.db)
        self._phase49_3h_result_panels = {}
        self._phase49_3h_last_result_id = None
        original_init(self, app, product_id)
        self._phase49_3h_add_result_panels()
        self._phase49_3h_add_cost_panel()
        self._phase49_3h_refresh_cost_panel()

    def _phase49_3h_add_result_panels(self):
        specs = (
            ("content", getattr(self, "content_tab", None), ("product_ai",)),
            ("images", getattr(self, "images_tab", None), ("image_seo", "image_finalize")),
            ("specs", getattr(self, "specs_tab", None), ("technical_ai",)),
            ("publish", getattr(self, "publish_tab", None), ("slider_seo",)),
        )
        for key, parent, actions in specs:
            if parent is None:
                continue
            frame = ttk.LabelFrame(parent, text="نتیجه / لاگ آخرین عملیات SEO و AI", padding=7, style="Card.TLabelframe")
            try:
                frame.pack(fill="x", pady=(8, 0))
            except Exception:
                continue
            status = tk.StringVar(value="هنوز عملیاتی ثبت نشده است.")
            ttk.Label(frame, textvariable=status, font=("Tahoma", 9, "bold")).pack(anchor="w")
            text = tk.Text(frame, height=7, wrap="word", font=("Tahoma", 9))
            text.pack(fill="x", pady=(4, 5))
            text.configure(state="disabled")
            actions_row = ttk.Frame(frame)
            actions_row.pack(fill="x")
            ttk.Button(actions_row, text="📂 باز کردن فولدر لاگ", command=self._phase49_3h_open_logs).pack(side="left", padx=3)
            ttk.Button(actions_row, text="↻ تلاش مجدد", command=lambda k=key: self._phase49_3h_retry(k)).pack(side="left", padx=3)
            ttk.Button(actions_row, text="بستن نتیجه", command=frame.pack_forget).pack(side="right", padx=3)
            self._phase49_3h_result_panels[key] = {"frame": frame, "status": status, "text": text, "actions": set(actions)}
            frame.pack_forget()

    def _phase49_3h_add_cost_panel(self):
        parent = getattr(self, "publish_tab", None)
        if parent is None:
            return
        frame = ttk.LabelFrame(parent, text="هزینه AI / SEO این محصول — داخلی", padding=7, style="Card.TLabelframe")
        frame.pack(fill="x", pady=(8, 0))
        self._phase49_3h_cost_var = tk.StringVar(value="در حال محاسبه…")
        ttk.Label(frame, textvariable=self._phase49_3h_cost_var, wraplength=1000, style="SubHeader.TLabel").pack(side="right", fill="x", expand=True, padx=5)
        ttk.Button(frame, text="↻ بروزرسانی هزینه", command=self._phase49_3h_refresh_cost_panel).pack(side="left", padx=3)
        ttk.Button(frame, text="📂 لاگ AI", command=self._phase49_3h_open_logs).pack(side="left", padx=3)

    def _phase49_3h_open_logs(self):
        try:
            if hasattr(self.app, "_phase49_3f_open_logs"):
                return self.app._phase49_3f_open_logs()
        except Exception:
            pass
        self.footer_status.set(f"فولدر لاگ: {runtime_trace.log_folder()}")

    def _phase49_3h_refresh_cost_panel(self):
        if not hasattr(self, "_phase49_3h_cost_var"):
            return
        try:
            summary = cost_ledger.aggregate_product(self.db, self.product_id)
            self._phase49_3h_cost_var.set(cost_ledger.format_cost_summary(summary) + " • هزینه نامشخص عمداً تخمین زده نمی‌شود.")
        except Exception as exc:
            self._phase49_3h_cost_var.set("هزینه قابل خواندن نیست: " + redact(exc))

    def _phase49_3h_begin_execution(self, title: str):
        provider = key = model = ""
        try:
            provider, key, model = self._phase49_3e_provider()
        except Exception:
            pass
        action_key, panel = _action_from_title(title)
        context = {
            "product_id": int(self.product_id),
            "title": str(title or ""),
            "action_key": action_key,
            "scope": panel,
            "panel": panel,
            "provider": provider,
            "model": model,
            "api_key": key,
            "started": time.perf_counter(),
            "request_from_id": cost_ledger.max_request_id(self.db, self.product_id),
            "before": _row_snapshot(self.db.product(self.product_id)),
            "steps": [],
            "finished": False,
        }
        runtime_trace.event("seo-execution", "start", product_id=self.product_id, provider=provider, model=model, detail={"action": action_key, "title": title})
        return context

    def _phase49_3h_execution_step(self, context: dict, label: str, detail: str = ""):
        if context.get("finished"):
            return
        step = {"at_ms": int((time.perf_counter() - context["started"]) * 1000), "label": str(label or ""), "detail": str(detail or "")}
        context["steps"].append(step)
        runtime_trace.event("seo-execution", "step", product_id=self.product_id, provider=context.get("provider", ""), model=context.get("model", ""), elapsed_ms=step["at_ms"], message=label, detail={"action": context.get("action_key"), "detail": detail})

    def _phase49_3h_execution_finish(self, context: dict, status: str, label: str, detail: str, error_text: str):
        if context.get("finished"):
            return
        context["finished"] = True
        context["elapsed_ms"] = int((time.perf_counter() - context["started"]) * 1000)
        if status == "ok":
            remaining = _remaining_tasks(self.db.product(self.product_id), str(context.get("action_key") or ""))
            status = "partial" if remaining else "success"
        result_id = _persist_result(self.db, context, status=status, label=label, detail=detail, error_text=error_text)
        self._phase49_3h_last_result_id = result_id
        self._phase49_3h_show_result(result_id)
        self._phase49_3h_refresh_cost_panel()
        runtime_trace.event("seo-execution", "finish", status="error" if status == "error" else "ok", product_id=self.product_id, provider=context.get("provider", ""), model=context.get("model", ""), elapsed_ms=context["elapsed_ms"], message=status, detail={"action": context.get("action_key"), "result_id": result_id})

        # AvalAI can expose a verified transaction cost by request_id. Resolve in
        # background so UI never freezes; unknown values stay unknown.
        if str(context.get("provider") or "").lower() == "avalai" and str(context.get("api_key") or "").strip():
            def worker():
                try:
                    cost_ledger.resolve_avalai_costs(
                        self.db,
                        self.product_id,
                        context.get("api_key") or "",
                        context.get("model") or "",
                        after_id=int(context.get("request_from_id") or 0),
                    )
                except Exception:
                    pass
                if _safe_exists(self):
                    try:
                        self.after(0, lambda: self._phase49_3h_refresh_result_cost(result_id))
                    except Exception:
                        pass
            threading.Thread(target=worker, daemon=True).start()

    def _phase49_3h_refresh_result_cost(self, result_id: int):
        result = get_result(self.db, result_id)
        if result is None:
            return
        cost = cost_ledger.aggregate_product(
            self.db,
            self.product_id,
            after_id=int(result.get("request_from_id") or 0),
            through_id=int(result.get("request_to_id") or cost_ledger.max_request_id(self.db, self.product_id)),
        )
        self.db.conn.execute(
            "UPDATE seo_execution_results SET cost_json=? WHERE id=?",
            (json.dumps(cost, ensure_ascii=False, default=str), int(result_id)),
        )
        self.db.conn.commit()
        self._phase49_3h_show_result(result_id)
        self._phase49_3h_refresh_cost_panel()

    def _phase49_3h_show_result(self, result_id: int):
        result = get_result(self.db, result_id)
        if result is None:
            return
        action = str(result.get("action_key") or "")
        panel_key = "images" if action in {"image_seo", "image_finalize"} else ("specs" if action == "technical_ai" else ("publish" if action == "slider_seo" else "content"))
        panel = getattr(self, "_phase49_3h_result_panels", {}).get(panel_key)
        if panel is None:
            return
        status = str(result.get("status") or "")
        icon = "✅" if status == "success" else ("⚠" if status == "partial" else "❌")
        panel["status"].set(f"{icon} آخرین نتیجه: {status} • {result.get('provider') or 'local'} / {result.get('model') or '—'}")
        widget = panel["text"]
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", format_result(result))
        widget.configure(state="disabled")
        panel["frame"].pack(fill="x", pady=(8, 0))
        try:
            self.after_idle(self._phase49_3g_refresh_workspace_scroll)
        except Exception:
            pass

    def _phase49_3h_retry(self, panel_key: str):
        if panel_key == "images":
            return self._phase49_3e_run_ai("images")
        if panel_key == "specs" and hasattr(self, "_phase49_3f_refresh_source_and_generate"):
            return self._phase49_3f_refresh_source_and_generate()
        return self._phase49_3e_run_ai("all")

    def phase49_3c_finalize_images(self):
        if original_finalize_images is None:
            return None
        context = self._phase49_3h_begin_execution("نهایی‌سازی فایل‌های SEO تصاویر")
        context["action_key"] = "image_finalize"
        context["panel"] = "images"
        self._phase49_3h_execution_step(context, "🔎 بررسی تصاویر منتخب", "عملیات Local است؛ درخواست AI ارسال نمی‌شود.")
        try:
            result = original_finalize_images(self)
            self._phase49_3h_execution_step(context, "💾 فایل‌ها و Metadata SEO نهایی شدند")
            self._phase49_3h_execution_finish(context, "ok", "✅ نهایی‌سازی SEO تصاویر کامل شد", "", "")
            return result
        except Exception as exc:
            self._phase49_3h_execution_finish(context, "error", "❌ نهایی‌سازی SEO تصاویر ناموفق بود", redact(exc), redact(exc))
            raise

    def _phase49_3h_freeze_publish_receipt(self, target: str):
        receipt = cost_ledger.freeze_receipt(self.db, self.product_id, target, status="pre_publish_snapshot")
        try:
            self.db.record_sync_receipt(
                self.product_id,
                "",
                "ai_seo_cost_snapshot",
                "",
                {"target": target, "receipt": receipt},
            )
        except Exception:
            pass
        runtime_trace.event("ai-cost", "publish-snapshot", product_id=self.product_id, detail={"target": target, "receipt_id": receipt.get("receipt_id"), "summary": receipt.get("summary")})
        self._phase49_3h_refresh_cost_panel()
        return receipt

    def publish_to_local_computer(self):
        self._phase49_3h_freeze_publish_receipt("local_django")
        return original_publish_local(self) if original_publish_local is not None else None

    def publish_to_production_site(self):
        self._phase49_3h_freeze_publish_receipt("production_site")
        return original_publish_production(self) if original_publish_production is not None else None

    def reload(self):
        result = original_reload(self)
        ensure_schema(self.db)
        self._phase49_3h_refresh_cost_panel()
        return result

    workspace_class.__init__ = __init__
    workspace_class._phase49_3h_add_result_panels = _phase49_3h_add_result_panels
    workspace_class._phase49_3h_add_cost_panel = _phase49_3h_add_cost_panel
    workspace_class._phase49_3h_open_logs = _phase49_3h_open_logs
    workspace_class._phase49_3h_refresh_cost_panel = _phase49_3h_refresh_cost_panel
    workspace_class._phase49_3h_begin_execution = _phase49_3h_begin_execution
    workspace_class._phase49_3h_execution_step = _phase49_3h_execution_step
    workspace_class._phase49_3h_execution_finish = _phase49_3h_execution_finish
    workspace_class._phase49_3h_refresh_result_cost = _phase49_3h_refresh_result_cost
    workspace_class._phase49_3h_show_result = _phase49_3h_show_result
    workspace_class._phase49_3h_retry = _phase49_3h_retry
    workspace_class.phase49_3c_finalize_images = phase49_3c_finalize_images
    workspace_class._phase49_3h_freeze_publish_receipt = _phase49_3h_freeze_publish_receipt
    if original_publish_local is not None:
        workspace_class.publish_to_local_computer = publish_to_local_computer
    if original_publish_production is not None:
        workspace_class.publish_to_production_site = publish_to_production_site
    workspace_class.reload = reload
    workspace_class._phase49_3h_execution_installed = True
