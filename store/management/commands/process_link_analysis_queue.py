from __future__ import annotations

import signal
import time

from django.core.management.base import BaseCommand, CommandError

from store.link_analysis_operations import (
    mark_stale_workers,
    mark_worker_stopped,
    queue_control,
    register_worker,
    touch_worker,
)
from store.link_analysis_queue import default_worker_id, process_link_analysis_queue


class Command(BaseCommand):
    help = "Worker تولیدی صف تحلیل لینک با Heartbeat، Retry، Backoff و توقف کنترل‌شده."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0, help="حداکثر Job در هر دور؛ صفر یعنی تنظیم دیتابیس")
        parser.add_argument("--watch", action="store_true", help="اجرای مداوم Worker")
        parser.add_argument("--sleep", type=float, default=0, help="فاصله دورها؛ صفر یعنی تنظیم دیتابیس")
        parser.add_argument("--worker-id", default="", help="شناسه اختیاری Worker")
        parser.add_argument("--max-loops", type=int, default=0, help="برای تست؛ صفر یعنی بدون محدودیت")
        parser.add_argument("--max-runtime", type=int, default=0, help="توقف سالم پس از تعداد ثانیه؛ صفر یعنی نامحدود")

    def handle(self, *args, **options):
        control = queue_control()
        limit = max(int(options["limit"] or control.default_batch_size or 1), 1)
        sleep_seconds = max(float(options["sleep"] or control.default_sleep_seconds or 1), 0.5)
        worker_id = (options.get("worker_id") or default_worker_id())[:180]
        max_loops = max(int(options.get("max_loops") or 0), 0)
        max_runtime = max(int(options.get("max_runtime") or 0), 0)
        watch = bool(options["watch"])
        loops = 0
        total = 0
        started_monotonic = time.monotonic()
        stop_requested = False

        def request_stop(signum, frame):
            nonlocal stop_requested
            stop_requested = True

        for signum in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
            if signum is not None:
                try:
                    signal.signal(signum, request_stop)
                except (OSError, ValueError):
                    pass

        heartbeat = register_worker(
            worker_id,
            metadata={"watch": watch, "limit": limit, "sleep_seconds": sleep_seconds},
        )
        self.stdout.write(f"Link analysis worker started: {worker_id}")
        fatal_error = ""
        try:
            while not stop_requested:
                control = queue_control()
                mark_stale_workers()
                if control.is_paused:
                    touch_worker(heartbeat, status="idle", loop_increment=1)
                    self.stdout.write(self.style.WARNING(f"Queue paused: {control.pause_reason or 'no reason'}"))
                    loops += 1
                    if not watch or (max_loops and loops >= max_loops):
                        break
                    time.sleep(sleep_seconds)
                    continue

                touch_worker(heartbeat, status="running", loop_increment=1)
                jobs = process_link_analysis_queue(limit=limit, worker_id=worker_id)
                succeeded = sum(1 for job in jobs if job.status == "completed")
                failed = sum(1 for job in jobs if job.status == "failed")
                total += len(jobs)
                touch_worker(
                    heartbeat,
                    status="idle",
                    processed_increment=len(jobs),
                    succeeded_increment=succeeded,
                    failed_increment=failed,
                    last_error="",
                )
                for job in jobs:
                    self.stdout.write(
                        f"job={job.pk} analysis={job.analysis_id} adapter={job.adapter_key} status={job.status} "
                        f"attempt={job.attempt_count}/{job.max_attempts} stage={job.progress_stage}"
                    )
                loops += 1
                if not watch:
                    break
                if max_loops and loops >= max_loops:
                    break
                if max_runtime and time.monotonic() - started_monotonic >= max_runtime:
                    break
                if not jobs:
                    time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            stop_requested = True
            self.stdout.write(self.style.WARNING("Worker stopped by user."))
        except Exception as exc:
            fatal_error = str(exc)
            touch_worker(heartbeat, status="error", last_error=fatal_error)
            raise CommandError(fatal_error) from exc
        finally:
            mark_worker_stopped(heartbeat, error=fatal_error)

        self.stdout.write(self.style.SUCCESS(f"Processed {total} link analysis job(s)."))
