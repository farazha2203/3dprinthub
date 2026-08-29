from __future__ import annotations

import json
import threading

import tkinter as tk
from tkinter import messagebox, ttk

from . import phase49_readiness_wizard as readiness_module
from .phase49_3i21_observable_ai_link_refresh import ObservableJobDialog
from .phase49_3i24_runtime_observability import redact
from .phase49_3i36_stage_finalization import (
    STAGE_LABELS,
    STAGE_ORDER,
    is_stage_locked,
    stage_locks,
)
from .phase49_3i37_seven_stage_ai import (
    AI_SOURCE_MODES,
    run_resilient_orchestrator,
    source_mode,
)
from .phase49_3i37_seven_stage_ai import capture_screenshot_for_site

PHASE = "49.3I.39"

AI_EDITABLE = {"quick", "images", "content", "specs", "slider"}
SLIDER_LABELS = {
    "عنوان اسلایدر",
    "توضیح اسلایدر",
    "Alt اسلایدر",
    "عبارت هدف اسلایدر",
    "عکس اسلایدر",
}


def _row_value(row, key, default=""):
    if row is None:
        return default
    try:
        return row[key] if key in row.keys() else default
    except Exception:
        return default


def _json_list(value) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def configure_readiness() -> None:
    if getattr(readiness_module, "_phase49_3i39_readiness_contract", False):
        return
    original = readiness_module.evaluate_readiness

    def evaluate_readiness(row):
        state = original(row)
        stages = state.setdefault("stages", {})

        # Slider is a real seventh stage, not a duplicate Publish heuristic.
        slider_enabled = bool(int(_row_value(row, "homepage_slider_enabled", 0) or 0))
        slider_checks = {
            "عنوان اسلایدر": str(_row_value(row, "homepage_slider_title_fa", "") or "").strip(),
            "توضیح اسلایدر": str(_row_value(row, "homepage_slider_description_fa", "") or "").strip(),
            "Alt اسلایدر": str(_row_value(row, "homepage_slider_alt_text", "") or "").strip(),
            "عبارت هدف اسلایدر": str(_row_value(row, "homepage_slider_focus_keyword", "") or "").strip(),
            "عکس اسلایدر": str(_row_value(row, "homepage_slider_image_url", "") or "").strip(),
        }
        slider_missing = [label for label, value in slider_checks.items() if slider_enabled and not value]
        slider_locked = is_stage_locked(row, "slider")
        stages["slider"] = {
            "label": STAGE_LABELS["slider"],
            "data_ready": not slider_missing,
            "finalized": slider_locked,
            "locked": slider_locked,
            "missing_data": slider_missing,
            "ready": bool(slider_locked and not slider_missing),
            "missing": (
                list(slider_missing)
                if slider_locked
                else [*slider_missing, "تأیید نهایی اپراتور (ثبت مرحله)"]
            ),
        }

        # Remove slider-owned defects from Publish. They were historically
        # appended there before Stage 6 became independent.
        publish = dict(stages.get("publish") or {})
        publish_missing_data = [
            item for item in (publish.get("missing_data") or publish.get("missing") or [])
            if item not in SLIDER_LABELS and item != "تأیید نهایی اپراتور (ثبت مرحله)"
        ]
        publish_locked = is_stage_locked(row, "publish")
        publish["missing_data"] = publish_missing_data
        publish["data_ready"] = not publish_missing_data
        publish["locked"] = publish_locked
        publish["finalized"] = publish_locked
        publish["ready"] = bool(publish_locked and not publish_missing_data)
        publish["missing"] = (
            publish_missing_data
            if publish_locked
            else [*publish_missing_data, "تأیید نهایی اپراتور (ثبت مرحله)"]
        )
        stages["publish"] = publish

        # Stage 2 professional readiness: selected Offers + at least one
        # registered Profile + valid pricing policy are the authority.
        offers = _json_list(_row_value(row, "material_color_options_json", "[]"))
        profiles = _json_list(_row_value(row, "sales_profile_ledger_json", "[]"))
        strategy = str(_row_value(row, "pricing_strategy", "dynamic") or "dynamic")
        commerce_missing = []
        if not offers:
            commerce_missing.append("حداقل یک Offer برند/فیلامنت/رنگ ثبت‌شده")
        if not profiles:
            commerce_missing.append("حداقل یک پروفایل فروش ثبت‌شده")
        if strategy == "fixed":
            if any(int(float(str(item.get("fixed_product_price") or 0))) <= 0 for item in offers if isinstance(item, dict)):
                commerce_missing.append("قیمت قطعی برای همه Offerهای انتخاب‌شده")
        elif strategy == "dynamic":
            if profiles and not any(
                _json_list(item.get("production_rows")) for item in profiles if isinstance(item, dict)
            ):
                commerce_missing.append("وزن/زمان چاپ پروفایل")
        commerce_locked = is_stage_locked(row, "commerce")
        stages["commerce"] = {
            "label": STAGE_LABELS["commerce"],
            "data_ready": not commerce_missing,
            "finalized": commerce_locked,
            "locked": commerce_locked,
            "missing_data": commerce_missing,
            "ready": bool(commerce_locked and not commerce_missing),
            "missing": (
                commerce_missing
                if commerce_locked
                else [*commerce_missing, "تأیید نهایی اپراتور (ثبت مرحله)"]
            ),
        }

        ordered = {stage: stages.get(stage, {}) for stage in STAGE_ORDER}
        state["stages"] = ordered
        state["production_ready"] = all(bool(item.get("ready")) for item in ordered.values())
        state["missing"] = [
            f"{STAGE_LABELS[stage]}: {item}"
            for stage in STAGE_ORDER
            for item in ordered[stage].get("missing", [])
        ]
        return state

    readiness_module.evaluate_readiness = evaluate_readiness
    # Product-first workflow imported the callable earlier.
    try:
        from . import phase49_3i25_product_first_workflow as product_first
        product_first.evaluate_readiness = evaluate_readiness
    except Exception:
        pass
    readiness_module._phase49_3i39_readiness_contract = True


def defect_snapshot(app, product_id: int) -> dict:
    row = app.db.product(int(product_id))
    state = readiness_module.evaluate_readiness(row)
    locks = stage_locks(row)
    data = {}
    ai_fixable = {}
    operator_only = {}
    finalization_pending = []

    for stage in STAGE_ORDER:
        info = (state.get("stages") or {}).get(stage) or {}
        missing = list(info.get("missing_data") or [])
        data[stage] = missing
        locked = bool((locks.get(stage) or {}).get("locked"))
        if not locked:
            finalization_pending.append(stage)

        if not missing:
            continue
        if stage == "content":
            ai_fixable[stage] = missing
        elif stage == "quick":
            ai_items = [item for item in missing if item == "عنوان فارسی"]
            op_items = [item for item in missing if item not in ai_items]
            if ai_items:
                ai_fixable[stage] = ai_items
            if op_items:
                operator_only[stage] = op_items
        elif stage == "images":
            # Missing image is deterministic from the Product Screenshot, while
            # Alt/metadata is handled by the same AI/image SEO contract.
            ai_fixable[stage] = missing
        elif stage == "slider":
            ai_fixable[stage] = missing
        elif stage == "specs":
            # Source URL/license cannot be invented or bypassed by AI.
            operator_only[stage] = missing
        else:
            operator_only[stage] = missing

    def flatten(groups):
        return [
            f"{STAGE_LABELS[stage]}: {item}"
            for stage, items in groups.items()
            for item in items
        ]

    return {
        "state": state,
        "data_missing": data,
        "ai_fixable": ai_fixable,
        "operator_only": operator_only,
        "ai_fixable_flat": flatten(ai_fixable),
        "operator_only_flat": flatten(operator_only),
        "finalization_pending": finalization_pending,
        "total_data_defects": sum(len(items) for items in data.values()),
        "ai_fixable_count": sum(len(items) for items in ai_fixable.values()),
        "operator_only_count": sum(len(items) for items in operator_only.values()),
    }


def _defect_ids(snapshot: dict) -> set[str]:
    return {
        f"{stage}|{item}"
        for stage, items in (snapshot.get("data_missing") or {}).items()
        for item in items
    }


def repair_until_stable(
    app,
    product_id: int,
    dialog,
    *,
    mode: str | None = None,
    target_stages: set[str] | None = None,
    refresh_existing: bool = False,
    max_passes: int = 3,
) -> dict:
    product_id = int(product_id)
    mode = mode if mode in AI_SOURCE_MODES else source_mode(app)
    initial = defect_snapshot(app, product_id)
    before_ids = _defect_ids(initial)
    dialog.event(
        "readiness_before",
        f"شروع عیب‌یابی • {initial['total_data_defects']} نقص داده • "
        f"{initial['ai_fixable_count']} قابل اصلاح خودکار",
        {
            "data_defects": initial["data_missing"],
            "ai_fixable": initial["ai_fixable"],
            "operator_only": initial["operator_only"],
            "finalization_pending": [
                STAGE_LABELS[s] for s in initial["finalization_pending"]
            ],
        },
    )

    # Deterministic image repair before spending an AI request.
    row = app.db.product(product_id)
    image_scope = target_stages is None or "images" in target_stages
    if (
        image_scope
        and not is_stage_locked(row, "images")
        and (initial.get("data_missing", {}).get("images") or [])
        and str(_row_value(row, "source_url", "") or "").startswith(("http://", "https://"))
    ):
        try:
            result = capture_screenshot_for_site(app, product_id)
            dialog.event(
                "deterministic_image_repair",
                "Screenshot نمای بالای صفحه به تصاویر منتخب سایت اضافه شد",
                {
                    "source_page_url": result.get("source_page_url"),
                    "selected": result.get("selected"),
                },
            )
        except Exception as exc:
            dialog.event("deterministic_image_warning", f"Screenshot خودکار انجام نشد: {redact(exc)}")

    last = defect_snapshot(app, product_id)
    history = []
    explicit_refresh_done = False

    for pass_no in range(1, max(1, int(max_passes)) + 1):
        if dialog.cancelled.is_set():
            raise RuntimeError("عملیات توسط اپراتور لغو شد.")

        current = defect_snapshot(app, product_id)
        scope = set(target_stages or current["ai_fixable"].keys())
        scope = {stage for stage in scope if stage in AI_EDITABLE and not is_stage_locked(app.db.product(product_id), stage)}

        run_for_cleanup = bool(refresh_existing and target_stages and not explicit_refresh_done)
        if not scope and not run_for_cleanup:
            last = current
            break

        dialog.event(
            "repair_pass_start",
            f"Pass {pass_no}/{max_passes} • Stageها: "
            + ("، ".join(STAGE_LABELS[s] for s in sorted(scope, key=STAGE_ORDER.index)) or "بدون Stage AI"),
            {
                "remaining_before": current["data_missing"],
                "source_mode": AI_SOURCE_MODES[mode],
                "refresh_existing": run_for_cleanup,
            },
        )
        result = run_resilient_orchestrator(
            app,
            product_id,
            dialog,
            mode=mode,
            target_stages=scope or set(target_stages or []),
            refresh_existing=run_for_cleanup,
            finalize_progress=False,
        )
        explicit_refresh_done = explicit_refresh_done or run_for_cleanup

        after = defect_snapshot(app, product_id)
        current_ids = _defect_ids(current)
        after_ids = _defect_ids(after)
        fixed = sorted(current_ids - after_ids)
        history.append({
            "pass": pass_no,
            "changed_fields": result.get("changed_fields") or [],
            "fixed": fixed,
            "remaining": after["data_missing"],
        })
        dialog.event(
            "repair_pass_result",
            f"Pass {pass_no}: {len(fixed)} نقص رفع شد • "
            f"{after['ai_fixable_count']} نقص AI-قابل‌اصلاح باقی",
            {
                "changed_fields": result.get("changed_fields") or [],
                "fixed_defects": fixed,
                "remaining_data_defects": after["data_missing"],
                "operator_only": after["operator_only"],
            },
        )
        last = after
        if after["ai_fixable_count"] <= 0:
            break
        if after_ids == current_ids and not run_for_cleanup:
            dialog.event(
                "repair_stalled",
                "این Pass نقص جدیدی را کم نکرد؛ Retry/Fallback همان موتور مصرف شد و Loop متوقف می‌شود.",
                {"remaining": after["ai_fixable"]},
            )
            break

    final = defect_snapshot(app, product_id)
    after_ids = _defect_ids(final)
    fixed_all = sorted(before_ids - after_ids)
    dialog.set_progress(100, "عیب‌یابی و بازبینی نهایی ۷ مرحله انجام شد")
    dialog.event(
        "readiness_after",
        f"پایان • {len(fixed_all)} نقص رفع شد • "
        f"{final['ai_fixable_count']} قابل اصلاح خودکار • "
        f"{final['operator_only_count']} اپراتوری باقی",
        {
            "fixed_defects": fixed_all,
            "remaining_data_defects": final["data_missing"],
            "remaining_ai_fixable": final["ai_fixable"],
            "remaining_operator_only": final["operator_only"],
            "finalization_pending": [
                STAGE_LABELS[s] for s in final["finalization_pending"]
            ],
        },
    )
    return {
        "initial": initial,
        "final": final,
        "history": history,
        "fixed_defects": fixed_all,
    }


def _done_message(result: dict) -> str:
    final = result["final"]
    if final["ai_fixable_count"] == 0:
        if final["operator_only_count"]:
            return (
                f"AI تمام نقص‌های قابل اصلاح را برطرف کرد. "
                f"{final['operator_only_count']} مورد اپراتوری باقی است؛ سپس Stageهای کامل را «ثبت» کن."
            )
        return "تمام نقص‌های داده قابل اصلاح برطرف شد؛ Stageهای کامل را برای قفل نهایی «ثبت» کن."
    return (
        f"عملیات تمام شد ولی {final['ai_fixable_count']} نقص AI-قابل‌اصلاح باقی مانده؛ "
        "جزئیات دقیق در گزارش بالا نوشته شده است."
    )


def install_workspace(workspace_class) -> None:
    configure_readiness()
    if getattr(workspace_class, "_phase49_3i39_completion_loop", False):
        return
    original_init = workspace_class.__init__

    def __init__(self, app, product_id):
        original_init(self, app, product_id)
        self._phase49_3i39_add_stage_ai_buttons()

    def add_stage_ai_buttons(self):
        panel = getattr(self, "_phase49_3i36_lock_panel", None)
        if panel is None:
            return
        rows = list(panel.winfo_children())
        for stage, row in zip(STAGE_ORDER, rows):
            if stage in {"commerce", "publish"}:
                continue
            ttk.Button(
                row,
                text="✨ AI اصلاح",
                width=10,
                command=lambda s=stage: self._phase49_3i39_run_stage_ai(s),
            ).pack(side="right", padx=2)
        try:
            panel.configure(text="کنترل ۷ مرحله — AI اصلاح / ثبت نهایی / اصلاح اپراتور")
        except Exception:
            pass

    def run_all(self):
        if getattr(self, "_phase49_3i33_ai_busy", False):
            self.footer_status.set("یک عملیات هوش مصنوعی در حال اجرا است.")
            return
        self._phase49_3i33_ai_busy = True
        mode = source_mode(self.app)
        dialog = ObservableJobDialog(
            self,
            f"تکمیل واقعی ۷ مرحله • {AI_SOURCE_MODES[mode]}",
        )
        dialog.event(
            "queue",
            "Readiness واقعی قبل/بعد سنجیده می‌شود؛ 100٪ فقط بعد از بازبینی نهایی نمایش داده می‌شود.",
        )

        def worker():
            try:
                result = repair_until_stable(
                    self.app,
                    int(self.product_id),
                    dialog,
                    mode=mode,
                    max_passes=3,
                )
                dialog.done(_done_message(result))
                self.after(0, self.reload)
                self.after(0, lambda: getattr(self, "_phase49_3i36_refresh_locks", lambda: None)())
            except Exception as exc:
                dialog.fail(exc)
                self.after(0, lambda: self.footer_status.set(f"AI کامل محصول ناموفق: {redact(exc)}"))
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_ai_busy", False))

        threading.Thread(
            target=worker,
            daemon=True,
            name=f"catalog-3i39-repair-all-{self.product_id}",
        ).start()

    def run_stage_ai(self, stage: str):
        stage = str(stage)
        row = self.db.product(int(self.product_id))
        if is_stage_locked(row, stage):
            messagebox.showwarning(
                "AI اصلاح مرحله",
                f"{STAGE_LABELS[stage]} نهایی است. ابتدا «اصلاح» را بزن تا اپراتور قفل را باز کند.",
                parent=self,
            )
            return
        if stage in {"commerce", "publish"}:
            messagebox.showinfo("AI", "این Stage اپراتوری است و AI اجازه تغییر آن را ندارد.", parent=self)
            return
        if getattr(self, "_phase49_3i33_ai_busy", False):
            return

        self._phase49_3i33_ai_busy = True
        mode = source_mode(self.app)
        dialog = ObservableJobDialog(self, f"اصلاح {STAGE_LABELS[stage]} • {AI_SOURCE_MODES[mode]}")
        dialog.event(
            "queue",
            f"فقط {STAGE_LABELS[stage]} داخل Scope است؛ Stageهای دیگر تغییر نمی‌کنند.",
        )

        def worker():
            try:
                result = repair_until_stable(
                    self.app,
                    int(self.product_id),
                    dialog,
                    mode=mode,
                    target_stages={stage},
                    refresh_existing=True,
                    max_passes=3,
                )
                dialog.done(_done_message(result))
                self.after(0, self.reload)
                self.after(0, lambda: getattr(self, "_phase49_3i36_refresh_locks", lambda: None)())
            except Exception as exc:
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_ai_busy", False))

        threading.Thread(
            target=worker,
            daemon=True,
            name=f"catalog-3i39-stage-{stage}-{self.product_id}",
        ).start()

    # 3I.38's generic target-stage button now routes through the same repair loop.
    def run_target_stage(self):
        label = str(getattr(self, "_phase49_3i38_stage_var", tk.StringVar(value=STAGE_LABELS["content"])).get() or "")
        stage = next((key for key, value in STAGE_LABELS.items() if value == label), "content")
        return run_stage_ai(self, stage)

    workspace_class.__init__ = __init__
    workspace_class._phase49_3i39_add_stage_ai_buttons = add_stage_ai_buttons
    workspace_class._phase49_3i37_run_all = run_all
    workspace_class._phase49_3i39_run_stage_ai = run_stage_ai
    workspace_class._phase49_3i38_run_target_stage = run_target_stage
    workspace_class._phase49_3i39_completion_loop = True


def install_app(app_class) -> None:
    configure_readiness()
    if getattr(app_class, "_phase49_3i39_bulk_completion", False):
        return

    def bulk_content_ai(self):
        ids = []
        for name in ("_phase49_3i26_product_selection", "_phase49_3i_selected_products"):
            for raw in getattr(self, name, set()) or set():
                try:
                    pid = int(raw)
                except Exception:
                    continue
                if pid not in ids:
                    ids.append(pid)
        tree = getattr(self, "product_tree", None)
        if tree is not None:
            for raw in tree.selection() or ():
                try:
                    pid = int(raw)
                except Exception:
                    continue
                if pid not in ids:
                    ids.append(pid)
        ids.sort()
        if not ids:
            messagebox.showwarning("3DPrintHub", "ابتدا محصولات را انتخاب کن.", parent=self)
            return
        if getattr(self, "_phase49_3i33_bulk_busy", False):
            return

        mode = source_mode(self)
        self._phase49_3i33_bulk_busy = True
        dialog = ObservableJobDialog(
            self,
            f"SEO/محتوا انتخابی • همان موتور مادر • {len(ids)} محصول",
        )
        dialog.event(
            "queue",
            "هر محصول مستقل: Readiness قبل → Stage 4 repair → Readiness بعد. هیچ موتور AI جداگانه‌ای وجود ندارد.",
        )

        def worker():
            success = 0
            failed = 0
            remaining = 0
            try:
                for index, product_id in enumerate(ids, 1):
                    if dialog.cancelled.is_set():
                        break
                    dialog.set_progress(
                        ((index - 1) / max(1, len(ids))) * 100,
                        f"محصول {index}/{len(ids)} • #{product_id}",
                    )
                    try:
                        result = repair_until_stable(
                            self,
                            product_id,
                            dialog,
                            mode=mode,
                            target_stages={"content"},
                            refresh_existing=True,
                            max_passes=3,
                        )
                        success += 1
                        remaining += result["final"]["ai_fixable_count"]
                    except Exception as exc:
                        failed += 1
                        dialog.event("product_failed", f"محصول #{product_id}: {redact(exc)}")
                        continue
                    updater = getattr(self, "_phase49_3i33_update_product_card", None)
                    if callable(updater):
                        self.after(0, lambda pid=product_id: updater(pid))
                dialog.set_progress(100, "بازبینی نهایی محصولات انتخاب‌شده")
                dialog.done(
                    f"پایان • {success} موفق • {failed} خطا • "
                    f"{remaining} نقص AI-قابل‌اصلاح باقی • Refresh سراسری انجام نشد"
                )
            except Exception as exc:
                dialog.fail(exc)
            finally:
                self.after(0, lambda: setattr(self, "_phase49_3i33_bulk_busy", False))

        threading.Thread(
            target=worker,
            daemon=True,
            name="catalog-3i39-bulk-content-repair",
        ).start()

    app_class._phase49_3i38_bulk_content_ai = bulk_content_ai
    app_class._phase49_3i39_bulk_completion = True
