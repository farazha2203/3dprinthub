from __future__ import annotations

import time

from django.core.management.base import BaseCommand, CommandError

from store.link_analysis_queue import default_worker_id, process_link_analysis_queue


class Command(BaseCommand):
    help = "پردازش صف تحلیل لینک مشتریان با Retry، Backoff و بازیابی قفل‌های متوقف‌شده."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=5, help="حداکثر Job در هر دور")
        parser.add_argument("--watch", action="store_true", help="اجرای مداوم Worker")
        parser.add_argument("--sleep", type=float, default=3.0, help="فاصله دورهای Worker بر حسب ثانیه")
        parser.add_argument("--worker-id", default="", help="شناسه اختیاری Worker")
        parser.add_argument("--max-loops", type=int, default=0, help="برای تست؛ صفر یعنی بدون محدودیت")

    def handle(self, *args, **options):
        limit = max(int(options["limit"] or 1), 1)
        sleep_seconds = max(float(options["sleep"] or 0.5), 0.5)
        worker_id = (options.get("worker_id") or default_worker_id())[:180]
        max_loops = max(int(options.get("max_loops") or 0), 0)
        loops = 0
        total = 0

        self.stdout.write(f"Link analysis worker started: {worker_id}")
        try:
            while True:
                jobs = process_link_analysis_queue(limit=limit, worker_id=worker_id)
                total += len(jobs)
                for job in jobs:
                    self.stdout.write(
                        f"job={job.pk} analysis={job.analysis_id} status={job.status} "
                        f"attempt={job.attempt_count}/{job.max_attempts} stage={job.progress_stage}"
                    )
                loops += 1
                if not options["watch"]:
                    break
                if max_loops and loops >= max_loops:
                    break
                if not jobs:
                    time.sleep(sleep_seconds)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Worker stopped by user."))
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Processed {total} link analysis job(s)."))
