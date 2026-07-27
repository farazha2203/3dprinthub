from __future__ import annotations

from pathlib import Path
import mimetypes

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import CustomerProfile, OrderAttachment, SupportConversation, SupportMessage


CHAT_ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".pdf", ".doc", ".docx",
    ".xls", ".xlsx", ".txt", ".csv", ".zip", ".rar", ".7z",
    ".stl", ".obj", ".3mf", ".step", ".stp", ".iges", ".igs",
}
CHAT_MAX_ATTACHMENT_BYTES = 12 * 1024 * 1024


def _can_access_support_file(user, conversation):
    if user.is_staff:
        return user.has_perm("website.view_supportconversation")
    return conversation.customer_id == user.id


def _can_access_order_file(user, order):
    if user.is_staff:
        return user.has_perm("website.view_order")
    return order.customer_id == user.id


def _customer_conversation_or_404(user, token):
    return get_object_or_404(
        SupportConversation.objects.select_related("customer", "assigned_to", "order"),
        public_token=token,
        customer=user,
    )


def get_or_create_active_conversation(user, order=None):
    queryset = SupportConversation.objects.filter(customer=user).exclude(status="closed")
    if order is not None:
        queryset = queryset.filter(order=order)
    else:
        queryset = queryset.filter(order__isnull=True)
    conversation = queryset.order_by("-last_message_at", "-updated_at").first()
    if conversation is None:
        conversation = SupportConversation.objects.create(
            customer=user,
            order=order,
            subject=f"گفت‌وگو درباره سفارش #{order.pk}" if order is not None else "گفت‌وگو با پشتیبانی",
        )
    return conversation


def _support_prefill_from_request(request):
    title = (request.GET.get("product_title") or "").strip()[:220]
    product_url = (request.GET.get("product_url") or "").strip()[:2000]
    if not title and not product_url:
        return ""
    parts = [f"سلام، درباره «{title or 'این محصول'}» برای قیمت و چاپ مشاوره می‌خواهم."]
    if product_url:
        parts.append(product_url)
    return "\n".join(parts)


def _validate_attachment(upload):
    if not upload:
        return None
    suffix = Path(upload.name).suffix.lower()
    if suffix not in CHAT_ALLOWED_EXTENSIONS:
        return "فرمت این فایل برای چت مجاز نیست."
    if upload.size > CHAT_MAX_ATTACHMENT_BYTES:
        return "حجم پیوست باید حداکثر ۱۲ مگابایت باشد."
    return None


def serialize_message(message, viewer):
    sender_name = message.sender.get_full_name() or message.sender.get_username()
    attachment_url = ""
    attachment_preview_url = ""
    attachment_kind = ""
    if message.attachment:
        attachment_url = reverse("website:support_attachment_download", args=[message.public_token])
        suffix = Path(message.attachment_name or message.attachment.name).suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            attachment_kind = "image"
            attachment_preview_url = reverse("website:support_attachment_preview", args=[message.public_token])
        elif suffix == ".pdf":
            attachment_kind = "pdf"
            attachment_preview_url = reverse("website:support_attachment_preview", args=[message.public_token])
    return {
        "id": message.pk,
        "body": message.body,
        "sender": sender_name,
        "is_staff": bool(message.sender.is_staff),
        "is_mine": message.sender_id == viewer.id,
        "created_at": timezone.localtime(message.created_at).strftime("%Y/%m/%d %H:%M"),
        "attachment_name": message.attachment_name,
        "attachment_url": attachment_url,
        "attachment_preview_url": attachment_preview_url,
        "attachment_kind": attachment_kind,
        "attachment_size": message.attachment_size,
    }


@login_required
@require_GET
def customer_support_view(request):
    conversations = SupportConversation.objects.filter(customer=request.user).order_by(
        "-last_message_at", "-updated_at"
    )
    token = request.GET.get("conversation")
    order_id = request.GET.get("order")
    if token:
        conversation = _customer_conversation_or_404(request.user, token)
    elif order_id and str(order_id).isdigit():
        from .models import Order
        order = get_object_or_404(Order, pk=int(order_id), customer=request.user)
        conversation = get_or_create_active_conversation(request.user, order=order)
    else:
        conversation = conversations.exclude(status="closed").first() or conversations.first()
        if conversation is None:
            conversation = get_or_create_active_conversation(request.user)

    conversation.messages.filter(
        sender__is_staff=True,
        read_by_customer_at__isnull=True,
    ).update(read_by_customer_at=timezone.now())

    profile, _ = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": None,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        },
    )
    return render(
        request,
        "website/customer/support_chat.html",
        {
            "profile": profile,
            "profile_completion": 0,
            "conversations": conversations,
            "conversation": conversation,
            "support_prefill": _support_prefill_from_request(request),
        },
    )


@login_required
@require_GET
def support_messages_api(request, token):
    conversation = _customer_conversation_or_404(request.user, token)
    after_id = request.GET.get("after")
    queryset = conversation.messages.select_related("sender")
    if after_id and str(after_id).isdigit():
        queryset = queryset.filter(pk__gt=int(after_id))

    conversation.messages.filter(
        sender__is_staff=True,
        read_by_customer_at__isnull=True,
    ).update(read_by_customer_at=timezone.now())

    return JsonResponse(
        {
            "conversation": str(conversation.public_token),
            "status": conversation.status,
            "messages": [serialize_message(message, request.user) for message in queryset[:200]],
        }
    )


@login_required
@require_POST
def support_send_api(request, token):
    conversation = _customer_conversation_or_404(request.user, token)
    if conversation.status == "closed":
        return JsonResponse({"ok": False, "error": "این گفت‌وگو بسته شده است."}, status=409)

    body = (request.POST.get("body") or "").strip()
    attachment = request.FILES.get("attachment")
    if not body and not attachment:
        return JsonResponse({"ok": False, "error": "متن پیام یا یک پیوست را وارد کنید."}, status=400)
    error = _validate_attachment(attachment)
    if error:
        return JsonResponse({"ok": False, "error": error}, status=400)

    with transaction.atomic():
        message = SupportMessage(
            conversation=conversation,
            sender=request.user,
            body=body,
        )
        if attachment:
            message.attachment = attachment
            message.attachment_name = Path(attachment.name).name
            message.attachment_content_type = getattr(attachment, "content_type", "") or ""
            message.attachment_size = attachment.size or 0
        message.save()

    return JsonResponse({"ok": True, "message": serialize_message(message, request.user)})


@login_required
@require_GET
def support_attachment_download(request, token):
    message = get_object_or_404(
        SupportMessage.objects.select_related("conversation", "conversation__customer"),
        public_token=token,
    )
    if not _can_access_support_file(request.user, message.conversation):
        raise Http404("فایل پیدا نشد")
    if not message.attachment:
        raise Http404("فایل پیدا نشد")
    return FileResponse(
        message.attachment.open("rb"),
        as_attachment=True,
        filename=message.attachment_name or Path(message.attachment.name).name,
    )


@login_required
@require_GET
def support_attachment_preview(request, token):
    message = get_object_or_404(
        SupportMessage.objects.select_related("conversation", "conversation__customer"),
        public_token=token,
    )
    if not _can_access_support_file(request.user, message.conversation):
        raise Http404("فایل پیدا نشد")
    if not message.attachment:
        raise Http404("فایل پیدا نشد")
    filename = message.attachment_name or Path(message.attachment.name).name
    suffix = Path(filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".pdf"}:
        raise Http404("پیش‌نمایش برای این فایل در دسترس نیست")
    content_type = message.attachment_content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    response = FileResponse(
        message.attachment.open("rb"),
        as_attachment=False,
        filename=filename,
        content_type=content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@require_GET
def order_attachment_download(request, token):
    attachment = get_object_or_404(
        OrderAttachment.objects.select_related("order", "order__customer"),
        public_token=token,
    )
    if not _can_access_order_file(request.user, attachment.order):
        raise Http404("فایل پیدا نشد")
    if not attachment.file:
        raise Http404("فایل پیدا نشد")
    return FileResponse(
        attachment.file.open("rb"),
        as_attachment=True,
        filename=attachment.original_name or Path(attachment.file.name).name,
    )


@login_required
@require_GET
def order_attachment_preview(request, token):
    attachment = get_object_or_404(
        OrderAttachment.objects.select_related("order", "order__customer"),
        public_token=token,
    )
    if not _can_access_order_file(request.user, attachment.order):
        raise Http404("فایل پیدا نشد")
    if not attachment.file or not attachment.is_previewable:
        raise Http404("پیش‌نمایش برای این فایل در دسترس نیست")
    filename = attachment.original_name or Path(attachment.file.name).name
    content_type = attachment.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    response = FileResponse(
        attachment.file.open("rb"),
        as_attachment=False,
        filename=filename,
        content_type=content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@require_http_methods(["GET"])
def support_widget_state_api(request):
    conversation = (
        SupportConversation.objects.filter(customer=request.user, order__isnull=True)
        .exclude(status="closed")
        .order_by("-last_message_at", "-updated_at")
        .first()
    )
    if conversation is None and request.GET.get("create") == "1":
        conversation = get_or_create_active_conversation(request.user)
    if conversation is None:
        return JsonResponse({
            "conversation": "",
            "unread": 0,
            "messages": [],
            "messages_url": "",
            "send_url": "",
            "page_url": reverse("website:customer_support"),
        })
    unread = conversation.unread_for_customer
    messages = conversation.messages.select_related("sender").order_by("-created_at")[:12]
    return JsonResponse(
        {
            "conversation": str(conversation.public_token),
            "unread": unread,
            "messages": [serialize_message(message, request.user) for message in reversed(list(messages))],
            "messages_url": reverse("website:support_messages_api", args=[conversation.public_token]),
            "send_url": reverse("website:support_send_api", args=[conversation.public_token]),
            "page_url": reverse("website:customer_support"),
        }
    )
