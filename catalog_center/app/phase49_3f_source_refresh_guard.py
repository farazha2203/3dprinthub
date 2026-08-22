from __future__ import annotations

import time

from . import phase49_3f_runtime_trace as runtime_trace


def _row_value(row, key, default=""):
    if row is None:
        return default
    if isinstance(row, dict):
        return row.get(key, default)
    try:
        return row[key]
    except Exception:
        return default


def install(workspace_class) -> None:
    if getattr(workspace_class, "_phase49_3f_source_refresh_guard_installed", False):
        return

    from .phase49_3f_workspace import AIProgress

    def _phase49_3f_refresh_source_and_generate(self):
        if getattr(self, "_phase49_3f_source_busy", False):
            self.footer_status.set("بازخوانی/تحلیل منبع در حال اجرا است.")
            return
        self.save(silent=True)
        before = self.db.product(self.product_id)
        # Only a real source fetch may advance this marker. A normal editor Save
        # changes updated_at and must never be mistaken for a successful refetch.
        marker = str(_row_value(before, "last_refetched_at", "") or "")
        progress = AIProgress(self, "بازخوانی منبع و ساخت توضیحات فنی", self.product_id)
        source_url = str(_row_value(before, "source_url", "") or "")
        progress.step("🌐 بازخوانی صفحه منبع شروع شد", source_url)
        runtime_trace.event(
            "source",
            "refresh-start",
            product_id=self.product_id,
            detail={"source_url": source_url, "previous_last_refetched_at": marker},
        )
        self._phase49_3f_source_busy = True
        try:
            self.refetch()
        except Exception as exc:
            self._phase49_3f_source_busy = False
            progress.fail(str(exc))
            runtime_trace.event(
                "source",
                "refresh-start-error",
                status="error",
                product_id=self.product_id,
                message=str(exc),
            )
            return

        started = time.perf_counter()

        def poll():
            row = self.db.product(self.product_id)
            current = str(_row_value(row, "last_refetched_at", "") or "")
            if current and current != marker:
                elapsed = int((time.perf_counter() - started) * 1000)
                runtime_trace.event(
                    "source",
                    "refresh-confirmed",
                    product_id=self.product_id,
                    elapsed_ms=elapsed,
                    detail={"last_refetched_at": current},
                )
                progress.step(
                    "✅ اطلاعات منبع واقعاً بروزرسانی شد",
                    "در حال اتصال به AI برای تبدیل داده خام به توضیح فنی قابل فهم",
                )
                return self._phase49_3f_generate_technical(progress)
            if time.perf_counter() - started >= 60:
                self._phase49_3f_source_busy = False
                elapsed = int((time.perf_counter() - started) * 1000)
                progress.fail(
                    "بازخوانی منبع تا ۶۰ ثانیه کامل نشد. درخواست AI ارسال نشد؛ "
                    "جزئیات را در فولدر لاگ بررسی کن."
                )
                runtime_trace.event(
                    "source",
                    "refresh-timeout",
                    status="error",
                    product_id=self.product_id,
                    elapsed_ms=elapsed,
                    detail={"expected_previous": marker, "current": current},
                )
                return
            self.after(750, poll)

        self.after(750, poll)

    workspace_class._phase49_3f_refresh_source_and_generate = _phase49_3f_refresh_source_and_generate
    workspace_class._phase49_3f_source_refresh_guard_installed = True

    # 49.3G is intentionally chained last so it wraps the mature 49.3F Workspace
    # rather than creating a second/parallel editor path.
    from .phase49_3g_workspace_usability import install as install_phase49_3g_workspace
    install_phase49_3g_workspace(workspace_class)
    print("EPIC49_3G_WORKSPACE_VERTICAL_SCROLL=ENABLED", flush=True)
    print("EPIC49_3G_GALLERY_HORIZONTAL_SCROLL=ENABLED", flush=True)
    print("EPIC49_3G_COMPACT_COMMERCE=ENABLED", flush=True)
    print("EPIC49_3G_AI_AUTOFILL_PROVENANCE=ENABLED", flush=True)
    print("EPIC49_3G_MANUAL_OVERRIDE_GUARD=ENABLED", flush=True)
    print("EPIC49_3G_AI_DISABLE_PER_GROUP=ENABLED", flush=True)
