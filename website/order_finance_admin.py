"""Finance controls for the service-order admin; no changes to gateway payments."""
import uuid
from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import Order, Quote, Payment
from .payment_services import PaymentFlowError


class ManagedOrderAdminForm(forms.ModelForm):
    """Prevent a manual order-status change from impersonating a payment."""

    class Meta:
        model = Order
        fields = "__all__"

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status == "paid":
            quote = Quote.objects.filter(order_id=self.instance.pk).first() if self.instance.pk else None
            if not quote or not quote.pricing_snapshot_at or quote.effective_total_price <= 0 or quote.paid_amount < quote.effective_total_price:
                raise forms.ValidationError("وضعیت پرداخت‌شده فقط پس از تسویه واقعی ثبت‌شده در دفتر مالی مجاز است.")
        if status == "cancelled" and self.instance.pk:
            quote = Quote.objects.filter(order_id=self.instance.pk).first()
            if quote and quote.paid_amount:
                raise forms.ValidationError("سفارش دارای دریافت تأییدشده را بدون فرآیند مستند استرداد لغو نکنید.")
        return status


class AdminManualReceiptForm(forms.Form):
    # An operator may use cash without a bank code, but a repeated POST must not double-book it.
    submission_key = forms.UUIDField(required=False, widget=forms.HiddenInput)
    amount = forms.IntegerField(label="مبلغ دریافتی (تومان)", min_value=1)
    payment_kind = forms.ChoiceField(label="نوع دریافت", choices=Payment.PAYMENT_KIND_CHOICES)
    method = forms.ChoiceField(
        label="روش واقعی دریافت",
        choices=[item for item in Payment.METHOD_CHOICES if item[0] != "gateway"],
    )
    ref_id = forms.CharField(
        label="شماره پیگیری کارت / تراکنش پوز", max_length=255, required=False,
        help_text="برای نقدی اختیاری است؛ برای کارت به کارت و پوز اجباری است.",
    )
    note = forms.CharField(label="توضیحات", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    confirmed = forms.BooleanField(
        label="دریافت توسط مسئول مالی بررسی و تأیید شده است",
        required=False,
        help_text="در صورت عدم تأیید، دریافت در وضعیت «در انتظار بررسی» ثبت می‌شود و از مانده کسر نخواهد شد.",
    )

    def clean(self):
        data = super().clean()
        if data.get("method") in {"bank_transfer", "pos"} and not (data.get("ref_id") or "").strip():
            self.add_error("ref_id", "برای دریافت بانکی و پوز، شماره پیگیری الزامی است.")
        if data.get("method") == "cash" and not (data.get("ref_id") or "").strip() and not data.get("submission_key"):
            self.add_error("submission_key", "شناسه یکتای ثبت نقدی نامعتبر است؛ فرم را دوباره باز کنید.")
        return data


def order_finance_summary(obj):
    if not obj or not obj.pk:
        return "پس از ذخیره سفارش، اطلاعات مالی نمایش داده می‌شود."
    try:
        quote = obj.quote
    except Quote.DoesNotExist:
        return "برای این سفارش هنوز پیش‌فاکتور ثبت نشده است."
    rows = [
        ("جمع قبل از تخفیف", quote.subtotal),
        ("تخفیف پیش‌فاکتور اولیه", quote.discount),
        ("مبلغ اصلی قطعی", quote.total_price),
        ("اصلاحیه‌های کاهنده", quote.credit_note_total),
        ("مبلغ قرارداد پس از اصلاحیه", quote.effective_total_price),
        ("مجموع دریافت‌های تأییدشده", quote.gross_paid_amount),
        ("مبالغ بازپرداخت‌شده", quote.refunded_amount),
        ("دریافتی خالص تأییدشده", quote.paid_amount),
        ("در انتظار بررسی/پرداخت", quote.pending_amount),
        ("مانده قابل وصول", quote.remaining_amount),
        ("مبلغ آزاد برای دریافت جدید", quote.available_payment_amount),
    ]
    output = format_html_join(
        "", '<div style="display:flex;justify-content:space-between;border-bottom:1px solid #ead8bb"><span>{}</span><strong>{} تومان</strong></div>',
        ((label, f"{int(value):,}") for label, value in rows),
    )
    url = reverse("admin:website_order_record_receipt", args=[obj.pk])
    if quote.pricing_snapshot_at:
        pricing_status = format_html('<p><strong>قیمت توافق‌شده در تاریخ {} تثبیت شده است.</strong></p>', quote.pricing_snapshot_at.strftime('%Y-%m-%d %H:%M'))
        receipt_action = format_html('<p><a class="button" href="{}">ثبت دریافت وجه / تسویه سفارش</a></p>', url)
    else:
        pricing_status = format_html('<p><strong>{}</strong></p>', 'قیمت هنوز تثبیت نشده است؛ ابتدا پیش‌فاکتور را نهایی کنید.')
        receipt_action = ""
    payments = quote.payments.order_by("-created_at")[:15]
    history = format_html_join(
        "", "<li>{} تومان | {} | {} | {}</li>",
        ((f"{p.amount:,}", p.get_status_display(), p.get_payment_kind_display(), p.ref_id or "بدون شناسه")
         for p in payments),
    )
    return format_html(
        '<section dir="rtl" style="max-width:650px">{}<div class="order-finance-summary">{}</div>'
        '{}<h4>سوابق دریافت (۱۵ مورد آخر)</h4><ul>{}</ul></section>',
        pricing_status, output, receipt_action, history,
    )


def record_manual_receipt_view(model_admin, request, order_id):
    if not (model_admin.has_change_permission(request) and request.user.has_perms(
        ("website.add_payment", "website.change_payment")
    )):
        raise PermissionDenied
    order = get_object_or_404(Order, pk=order_id)
    try:
        quote = order.quote
    except Quote.DoesNotExist:
        model_admin.message_user(request, "ابتدا پیش‌فاکتور این سفارش را ثبت کنید.", messages.ERROR)
        return redirect("admin:website_order_change", order_id)

    if request.method == "POST":
        form = AdminManualReceiptForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    quote = Quote.objects.select_for_update().get(pk=quote.pk)
                    # Lock the parent before checking totals, serializing manual receipt writes.
                    Order.objects.select_for_update().get(pk=order.pk)
                    amount = form.cleaned_data["amount"]
                    if amount > quote.available_payment_amount:
                        raise PaymentFlowError("مبلغ دریافتی بیش از مانده آزاد سفارش است؛ صفحه را تازه کنید.")
                    if not quote.total_price or not quote.pricing_snapshot_at:
                        raise PaymentFlowError("ابتدا قیمت نهایی پیش‌فاکتور را تثبیت کنید.")
                    if quote.status != "accepted":
                        raise PaymentFlowError("پیش‌فاکتور باید توسط مشتری تأیید شده باشد.")
                    reference = (form.cleaned_data["ref_id"] or "").strip()
                    method = form.cleaned_data["method"]
                    if method == "cash" and not reference:
                        reference = f"cash:{form.cleaned_data['submission_key']}"
                    if reference and Payment.objects.filter(method=method, ref_id=reference).exclude(
                        status__in=["failed", "cancelled"]
                    ).exists():
                        raise PaymentFlowError("شناسه این تراکنش قبلاً ثبت شده است.")
                    payment = Payment.objects.create(
                        quote=quote, amount=amount,
                        payment_kind=form.cleaned_data["payment_kind"],
                        method=method, status="awaiting_review",
                        ref_id=reference, note=form.cleaned_data["note"],
                    )
                    if form.cleaned_data["confirmed"]:
                        payment.mark_paid(
                            ref_id=reference,
                            provider_message="دریافت دستی تأییدشده توسط مدیر",
                            metadata={"review_source": "order_admin", "reviewed_by_user_id": request.user.pk},
                        )
            except PaymentFlowError as exc:
                form.add_error(None, str(exc))
            else:
                model_admin.message_user(request, "دریافت وجه ثبت شد و مانده سفارش به‌روز شد.", messages.SUCCESS)
                return redirect("admin:website_order_change", order.pk)
    else:
        form = AdminManualReceiptForm(initial={
            "amount": quote.available_payment_amount,
            "payment_kind": "balance" if quote.paid_amount else "deposit",
            "method": "bank_transfer",
            "submission_key": uuid.uuid4(),
        })
    context = {
        **model_admin.admin_site.each_context(request),
        "title": f"ثبت دریافت وجه سفارش {order.pk}",
        "opts": model_admin.model._meta,
        "original": order,
        "order": order,
        "quote": quote,
        "form": form,
        "change_url": reverse("admin:website_order_change", args=[order.pk]),
    }
    return render(request, "admin/website/order/record_receipt.html", context)
