from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Iterable

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def _site_base_url() -> str:
    value = os.getenv("SITE_BASE_URL", "").strip()
    if value:
        return value.rstrip("/")
    try:
        from website.models import SEOSettings
        row = SEOSettings.objects.first()
        if row and row.site_url:
            return row.site_url.rstrip("/")
    except Exception:
        pass
    return "https://3dprinthub.ir"


def _post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 12) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310 - configured trusted APIs only
        if int(getattr(response, "status", 200)) >= 300:
            raise RuntimeError(f"notification endpoint returned HTTP {response.status}")


def _telegram(text: str) -> bool:
    token = os.getenv("TELEGRAM_OPERATOR_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_OPERATOR_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False
    _post_json(
        f"https://api.telegram.org/bot{token}/sendMessage",
        {"chat_id": chat_id, "text": text[:3900], "disable_web_page_preview": False},
    )
    return True


def _whatsapp(text: str) -> bool:
    token = os.getenv("WHATSAPP_CLOUD_TOKEN", "").strip()
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    operator_phone = os.getenv("WHATSAPP_OPERATOR_PHONE", "").strip()
    endpoint = os.getenv("WHATSAPP_CLOUD_MESSAGES_URL", "").strip()
    if not endpoint and phone_id:
        version = os.getenv("WHATSAPP_GRAPH_API_VERSION", "").strip()
        if version:
            endpoint = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    if not token or not endpoint or not operator_phone:
        return False
    template_name = os.getenv("WHATSAPP_OPERATOR_TEMPLATE_NAME", "").strip()
    if template_name:
        language_code = os.getenv("WHATSAPP_OPERATOR_TEMPLATE_LANGUAGE", "fa").strip() or "fa"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": operator_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": text[:1000]}],
                }],
            },
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": operator_phone,
            "type": "text",
            "text": {"preview_url": True, "body": text[:4000]},
        }
    _post_json(endpoint, payload, {"Authorization": f"Bearer {token}"})
    return True


def _email(text: str, subject: str) -> bool:
    recipients = [x.strip() for x in os.getenv("OPERATOR_ALERT_EMAILS", "").split(",") if x.strip()]
    if not recipients:
        return False
    send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    return True


def send_operator_message(*, text: str, subject: str = "درخواست قیمت جدید 3DPrintHub") -> tuple[bool, str]:
    errors: list[str] = []
    sent = False
    for name, sender in (("telegram", _telegram), ("whatsapp", _whatsapp)):
        try:
            sent = sender(text) or sent
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    try:
        sent = _email(text, subject) or sent
    except Exception as exc:
        errors.append(f"email: {type(exc).__name__}: {exc}")
    if not sent and not errors:
        errors.append("هیچ کانال اعلان اپراتور تنظیم نشده است.")
    return sent, " | ".join(errors)


def notify_manual_review(review) -> None:
    if review.operator_notification_sent_at:
        return
    base = _site_base_url()
    analysis = review.analysis
    admin_url = f"{base}/admin/store/linkanalysismanualreview/{review.pk}/change/"
    text = (
        "🔔 درخواست استعلام قیمت جدید\n"
        f"عنوان: {analysis.title or 'بدون عنوان'}\n"
        f"مشتری: {getattr(analysis.user, 'get_full_name', lambda: '')() or getattr(analysis.user, 'username', '-') if analysis.user_id else '-'}\n"
        f"لینک اصلی: {analysis.normalized_url}\n"
        f"وزن فعلی: {analysis.estimated_weight_grams or 'نامشخص'} گرم\n"
        f"زمان فعلی: {analysis.estimated_print_minutes or 'نامشخص'} دقیقه\n"
        f"ثبت وزن/زمان و قیمت: {admin_url}"
    )
    sent, error = send_operator_message(text=text)
    review.operator_notification_sent_at = timezone.now() if sent else None
    review.operator_notification_error = error
    review.save(update_fields=["operator_notification_sent_at", "operator_notification_error", "updated_at"])


def notify_catalog_pricing(review) -> None:
    if review.notification_sent_at:
        return
    base = _site_base_url()
    admin_url = f"{base}/admin/store/catalogpricingreview/{review.pk}/change/"
    asset = review.asset
    text = (
        "🧮 مدل جدید نیازمند وزن و زمان چاپ است\n"
        f"عنوان: {asset.title}\n"
        f"منبع: {asset.source.name}\n"
        f"لینک اصلی: {asset.source_url}\n"
        f"ثبت مشخصات و قیمت: {admin_url}"
    )
    sent, error = send_operator_message(text=text, subject="مدل جدید نیازمند قیمت‌گذاری")
    review.notification_sent_at = timezone.now() if sent else None
    review.notification_error = error
    review.save(update_fields=["notification_sent_at", "notification_error", "updated_at"])


def process_pending_operator_notifications(*, limit: int = 10) -> dict[str, int]:
    """Retry unsent customer inquiry alerts without blocking the web request path."""
    from .models import LinkAnalysisManualReview

    stats = {"checked": 0, "sent": 0, "failed": 0}
    queryset = (
        LinkAnalysisManualReview.objects.filter(
            status__in=["pending", "in_progress"],
            operator_notification_sent_at__isnull=True,
        )
        .select_related("analysis", "analysis__user")
        .order_by("-priority", "requested_at", "id")[: max(int(limit or 1), 1)]
    )
    for review in queryset:
        stats["checked"] += 1
        notify_manual_review(review)
        review.refresh_from_db(fields=["operator_notification_sent_at", "operator_notification_error"])
        if review.operator_notification_sent_at:
            stats["sent"] += 1
        else:
            stats["failed"] += 1
    return stats
