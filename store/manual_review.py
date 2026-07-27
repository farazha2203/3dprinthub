from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from .models import CustomerLinkAnalysis, CustomerLinkAnalysisJob, LinkAnalysisManualReview

OPEN_STATUSES = ("pending", "in_progress")


def _snapshot(analysis: CustomerLinkAnalysis) -> dict:
    return {
        "source_url": analysis.normalized_url or analysis.source_url,
        "source_domain": analysis.source_domain,
        "source_name": analysis.source_name,
        "title": analysis.title,
        "file_formats": analysis.file_formats or [],
        "has_images": bool(analysis.display_image_url),
    }


@transaction.atomic
def ensure_manual_review(
    analysis: CustomerLinkAnalysis,
    *,
    job: CustomerLinkAnalysisJob | None = None,
    requested_by=None,
    reason: str = "customer_request",
    customer_note: str = "",
    priority: int = 100,
) -> tuple[LinkAnalysisManualReview, bool]:
    review = (
        LinkAnalysisManualReview.objects.select_for_update()
        .filter(analysis=analysis, status__in=OPEN_STATUSES)
        .order_by("-priority", "requested_at")
        .first()
    )
    created = False
    if review is None:
        review = LinkAnalysisManualReview.objects.create(
            analysis=analysis,
            job=job,
            requested_by=requested_by,
            reason=reason,
            customer_note=(customer_note or "")[:5000],
            priority=max(min(int(priority), 1000), -1000),
            error_snapshot=(getattr(job, "last_error", "") or analysis.error_message or "")[:10000],
            source_snapshot=_snapshot(analysis),
        )
        created = True
    else:
        fields = []
        if job and review.job_id != job.pk:
            review.job = job
            fields.append("job")
        if customer_note and customer_note.strip():
            review.customer_note = customer_note.strip()[:5000]
            fields.append("customer_note")
        if int(priority) > review.priority:
            review.priority = int(priority)
            fields.append("priority")
        if fields:
            review.save(update_fields=fields + ["updated_at"])
    from .realtime import publish_operations
    publish_operations()
    return review, created


@transaction.atomic
def assign_review(review: LinkAnalysisManualReview, user) -> LinkAnalysisManualReview:
    row = LinkAnalysisManualReview.objects.select_for_update().get(pk=review.pk)
    row.assigned_to = user
    row.status = "in_progress"
    row.started_at = row.started_at or timezone.now()
    row.save(update_fields=["assigned_to", "status", "started_at", "updated_at"])
    from .realtime import publish_operations
    publish_operations()
    return row


@transaction.atomic
def finish_review(review: LinkAnalysisManualReview, *, user, action: str, note: str = "", status: str = "resolved"):
    row = (
        LinkAnalysisManualReview.objects.select_for_update()
        .select_related("analysis", "analysis__user")
        .get(pk=review.pk)
    )
    was_open = row.status in OPEN_STATUSES
    row.assigned_to = user
    row.status = status
    row.resolution_action = action
    row.reviewer_note = (note or "")[:10000]
    row.started_at = row.started_at or timezone.now()
    row.resolved_at = timezone.now()
    row.save(update_fields=[
        "assigned_to", "status", "resolution_action", "reviewer_note", "started_at", "resolved_at", "updated_at"
    ])

    if was_open and row.analysis.user_id:
        from django.urls import reverse
        from .services import notify

        title = "بررسی لینک شما تکمیل شد" if status == "resolved" else "نتیجه بررسی لینک شما ثبت شد"
        message = (note or "کارشناس نتیجه بررسی لینک ارسالی شما را ثبت کرد.")[:1000]
        notify(
            row.analysis.user,
            title,
            message,
            notification_type="order",
            url=reverse("store:external_link_analysis", kwargs={"token": row.analysis.public_token}),
        )

    from .realtime import publish_operations
    publish_operations()
    return row


def resolve_reviews_after_success(analysis_id: int) -> int:
    count = LinkAnalysisManualReview.objects.filter(
        analysis_id=analysis_id,
        status__in=OPEN_STATUSES,
        reason="auto_failed",
    ).update(
        status="resolved",
        resolution_action="retry",
        reviewer_note="تحلیل خودکار در تلاش بعدی با موفقیت تکمیل شد.",
        resolved_at=timezone.now(),
    )
    if count:
        from .realtime import publish_operations
        publish_operations()
    return count
