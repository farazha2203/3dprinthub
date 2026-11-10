"""Operator-only service-order dispatch and handoff from the common Store shipping list."""
from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from store.models import ShippingMethod

from .models import Order, Quote, ServiceOrderDelivery


class ServiceDeliveryForm(forms.Form):
    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethod.objects.filter(is_active=True).order_by("sort_order", "title"),
        label="روش واقعی تحویل (از فهرست فروشگاه)",
    )
    status = forms.ChoiceField(
        choices=ServiceOrderDelivery.STATUS_CHOICES, label="مرحله ارسال / تحویل",
    )
    tracking_code = forms.CharField(
        label="کد رهگیری پست / تیپاکس", required=False, max_length=120,
    )
    recipient_name = forms.CharField(
        label="نام تحویل گیرنده", required=False, max_length=150,
    )
    recipient_address = forms.CharField(
        label="نشانی تحویل", required=False, widget=forms.Textarea(attrs={"rows": 2}),
    )
    note = forms.CharField(
        label="توضیحات ثبت تحویل", required=False, widget=forms.Textarea(attrs={"rows": 3}),
    )


def order_delivery_summary(order):
    if not order or not order.pk:
        return ""
    delivery = ServiceOrderDelivery.objects.filter(order_id=order.pk).select_related(
        "shipping_method", "recorded_by",
    ).first()
    url = reverse("admin:website_order_record_delivery", args=[order.pk])
    if not delivery:
        return format_html(
            '<div dir="rtl"><p>هنوز ارسال یا تحویل ثبت نشده است.</p>'
            '<p><a class="button" href="{}">ثبت ارسال / تحویل حضوری</a></p></div>', url,
        )
    identity = delivery.recorded_by.get_username() if delivery.recorded_by else "—"
    return format_html(
        '<div dir="rtl"><p><strong>{}</strong> / {}</p>'
        '<p>رهگیری: {} | تحویل گیرنده: {} | ثبت کننده: {}</p>'
        '<p>زمان ارسال: {} | زمان تحویل: {}</p>'
        '<p><a class="button" href="{}">مشاهده سوابق تحویل</a></p></div>',
        delivery.shipping_method.title, delivery.get_status_display(),
        delivery.tracking_code or "—", delivery.recipient_name or "—", identity,
        delivery.shipped_at or "—", delivery.delivered_at or "—", url,
    )


def record_service_delivery_view(model_admin, request, order_id):
    if not model_admin.has_change_permission(request) or not request.user.has_perm(
        "website.add_serviceorderdelivery"
    ):
        raise PermissionDenied
    order = get_object_or_404(Order, pk=order_id)
    previous = ServiceOrderDelivery.objects.filter(order=order).select_related(
        "shipping_method", "recorded_by",
    ).first()
    if request.method == "POST":
        form = ServiceDeliveryForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    locked = Order.objects.select_for_update().get(pk=order.pk)
                    quote = Quote.objects.select_for_update().filter(order=locked).first()
                    if not quote or quote.status != "accepted" or not quote.pricing_snapshot_at:
                        raise ValidationError("ابتدا پیش فاکتور را تأیید کنید.")
                    if quote.paid_amount < quote.total_price or not quote.total_price:
                        raise ValidationError("تحویل بدون تسویه مالی تأییدشده مجاز نیست.")
                    delivery = ServiceOrderDelivery.objects.select_for_update().filter(order=locked).first()
                    if delivery and delivery.status == "delivered":
                        raise ValidationError("تحویل نهایی قبلاً ثبت شده و قابل بازنویسی نیست.")
                    if delivery is None:
                        delivery = ServiceOrderDelivery(order=locked)
                    delivery.shipping_method = form.cleaned_data["shipping_method"]
                    delivery.status = form.cleaned_data["status"]
                    delivery.tracking_code = form.cleaned_data["tracking_code"].strip()
                    delivery.recipient_name = form.cleaned_data["recipient_name"].strip()
                    delivery.recipient_address = form.cleaned_data["recipient_address"]
                    delivery.note = form.cleaned_data["note"]
                    delivery.recorded_by = request.user
                    delivery.save()
            except ValidationError as exc:
                for item in exc.messages:
                    form.add_error(None, item)
            else:
                model_admin.message_user(
                    request, "اطلاعات واقعی ارسال / تحویل ثبت شد.", messages.SUCCESS
                )
                return redirect("admin:website_order_change", order.pk)
    else:
        initial = {
            "shipping_method": previous.shipping_method_id if previous else None,
            "status": previous.status if previous else "dispatched",
            "tracking_code": previous.tracking_code if previous else "",
            "recipient_name": previous.recipient_name if previous else "",
            "recipient_address": previous.recipient_address if previous else "",
            "note": previous.note if previous else "",
        }
        form = ServiceDeliveryForm(initial=initial)
    return render(request, "admin/website/order/record_delivery.html", {
        **model_admin.admin_site.each_context(request),
        "title": f"ثبت ارسال و تحویل سفارش {order.pk}",
        "opts": model_admin.model._meta,
        "original": order,
        "order": order,
        "previous_delivery": previous,
        "form": form,
        "change_url": reverse("admin:website_order_change", args=[order.pk]),
    })
