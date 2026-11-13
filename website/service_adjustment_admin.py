"""Back-office controls for immutable credit notes and manual refund attestations."""
from uuid import uuid4

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import Order, Payment, Quote, ServiceCreditNote, ServiceRefund
from .service_adjustments import (
    ServiceFinanceError, approve_service_refund, cancel_service_refund,
    confirm_service_refund, issue_service_credit_note, request_service_refund,
)


class ServiceCreditNoteForm(forms.Form):
    amount = forms.IntegerField(min_value=1, label="مبلغ کسر از بدهی قرارداد (تومان)")
    reference = forms.CharField(max_length=90, label="شماره یکتای اصلاحیه / شماره سند")
    reason = forms.CharField(min_length=8, label="دلیل و مستندات اصلاح قیمت", widget=forms.Textarea(attrs={"rows": 3}))
    acknowledged = forms.BooleanField(
        label="تأیید می‌کنم این سند فقط مبلغ قابل وصول را اصلاح می‌کند و هیچ وجهی بازپرداخت نمی‌شود."
    )


class ServiceRefundRequestForm(forms.Form):
    request_key = forms.UUIDField(widget=forms.HiddenInput)
    original_payment = forms.ModelChoiceField(queryset=Payment.objects.none(), label="دریافت اولیه تأییدشده")
    amount = forms.IntegerField(min_value=1, label="مبلغ پیشنهادی استرداد (تومان)")
    method = forms.ChoiceField(choices=ServiceRefund.METHOD_CHOICES, label="روش بازپرداخت واقعی")
    reason = forms.CharField(min_length=8, label="دلیل استرداد / توضیح مشتری", widget=forms.Textarea(attrs={"rows": 3}))
    acknowledged = forms.BooleanField(
        label="تأیید می‌کنم این فقط درخواست استرداد است؛ هنوز هیچ پولی جابه‌جا نشده است."
    )

    def __init__(self, *args, quote=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["original_payment"].queryset = (
            Payment.objects.filter(quote=quote, status="paid").order_by("id")
            if quote is not None else Payment.objects.none()
        )


class ServiceRefundDecisionForm(forms.Form):
    action = forms.ChoiceField(label="تصمیم مستند", choices=())
    approval_note = forms.CharField(
        required=False, label="دلیل مستقل تأیید یا تصمیم مالی",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    payout_reference = forms.CharField(
        max_length=180, required=False,
        label="کد پیگیری بانکی/پوز یا شناسه رسید تحویل نقدی",
    )
    cancellation_reason = forms.CharField(
        required=False, label="دلیل لغو درخواست", widget=forms.Textarea(attrs={"rows": 3}),
    )
    confirmed = forms.BooleanField(
        label="با بررسی سند بیرونی تأیید می‌کنم وجه واقعاً برگشت داده شده است",
        required=False,
    )

    def __init__(self, *args, status="requested", allowed_actions=None, **kwargs):
        super().__init__(*args, **kwargs)
        if status == "requested":
            self.fields["action"].choices = (
                ("approve", "تأیید مستقل بدون انتقال وجه"),
                ("cancel", "لغو درخواست بدون پرداخت"),
            )
        elif status == "approved":
            self.fields["action"].choices = (
                ("complete", "ثبت وجه واقعاً بازپرداخت‌شده با رسید"),
                ("cancel", "لغو درخواست تأییدشده بدون پرداخت"),
            )
        if allowed_actions is not None:
            self.fields["action"].choices = tuple(
                (value, label) for value, label in self.fields["action"].choices
                if value in allowed_actions
            )

    def clean(self):
        data = super().clean()
        if data.get("action") == "approve":
            if len((data.get("approval_note") or "").strip()) < 8:
                self.add_error("approval_note", "تأیید مستقل نیازمند توضیح حداقل ۸ نویسه است.")
        elif data.get("action") == "complete":
            if not data.get("confirmed"):
                self.add_error("confirmed", "بدون تأیید پرداخت واقعی ثبت حسابداری مجاز نیست.")
            if len((data.get("payout_reference") or "").strip()) < 4:
                self.add_error("payout_reference", "شناسه پیگیری/رسید باید حداقل چهار نویسه باشد.")
        elif data.get("action") == "cancel":
            if len((data.get("cancellation_reason") or "").strip()) < 8:
                self.add_error("cancellation_reason", "برای لغو حداقل ۸ نویسه توضیح بدهید.")
        return data


def order_adjustments_summary(order):
    if not order or not order.pk:
        return ""
    quote = Quote.objects.filter(order=order).first()
    if not quote or not quote.pricing_snapshot_at:
        return ""
    credit_url = reverse("admin:website_order_issue_credit_note", args=[order.pk])
    request_url = reverse("admin:website_order_request_refund", args=[order.pk])
    notes = quote.credit_notes.select_related("issued_by").order_by("-id")[:10]
    refunds = quote.refunds.select_related("completed_by", "requested_by", "approved_by", "original_payment").order_by("-id")[:10]
    note_html = format_html_join("", "<li>{}: {} تومان — {}</li>",
        ((n.reference, f"{n.amount:,}", n.reason[:120]) for n in notes))
    refund_html = format_html_join("", '<li>{} تومان | {} | درخواست‌کننده: {} | تأییدکننده مستقل: {} | رسید: {} | <a href="{}">مدیریت</a></li>',
        ((f"{r.amount:,}", r.get_status_display(), r.requested_by.get_username(),
          r.approved_by.get_username() if r.approved_by_id else "هنوز تأیید نشده",
          r.payout_reference or "بدون پرداخت",
          reverse("admin:website_order_complete_refund", args=[order.pk, r.pk])) for r in refunds))
    return format_html(
        '<section dir="rtl" style="max-width:750px">'
        '<p>مبلغ قطعی اولیه: <strong>{}</strong> | جمع اصلاحیه‌های کاهنده: <strong>{}</strong>'
        ' | مبلغ قابل وصول جدید: <strong>{}</strong></p>'
        '<p>دریافت ناخالص: <strong>{}</strong> | استرداد مستند: <strong>{}</strong>'
        ' | بستانکاری بازپرداخت‌پذیر: <strong>{}</strong></p>'
        '<p><a class="button" href="{}">صدور اصلاحیه کاهنده</a> '
        '<a class="button" href="{}">درخواست استرداد مازاد مشتری</a></p>'
        '<h4>سندهای اصلاحیه</h4><ul>{}</ul><h4>درخواست‌های بازپرداخت</h4><ul>{}</ul>'
        '<p><small>صدور اصلاحیه هیچ بازپرداخت بانکی اجرا نمی‌کند؛ بازپرداخت فقط پس از رسید واقعی ثبت می‌شود.</small></p>'
        '</section>',
        f"{quote.total_price:,}", f"{quote.credit_note_total:,}",
        f"{quote.effective_total_price:,}", f"{quote.gross_paid_amount:,}",
        f"{quote.refunded_amount:,}", f"{quote.refundable_excess:,}",
        credit_url, request_url, note_html, refund_html,
    )


def _base_context(model_admin, request, order, title, **values):
    return {
        **model_admin.admin_site.each_context(request),
        "title": title, "opts": model_admin.model._meta,
        "original": order, "order": order,
        "change_url": reverse("admin:website_order_change", args=[order.pk]),
        **values,
    }


def issue_service_credit_note_view(model_admin, request, order_id):
    if not model_admin.has_change_permission(request) or not request.user.has_perm("website.add_servicecreditnote"):
        raise PermissionDenied
    order = get_object_or_404(Order, pk=order_id)
    quote = get_object_or_404(Quote, order=order)
    if request.method == "POST":
        form = ServiceCreditNoteForm(request.POST)
        if form.is_valid():
            try:
                issue_service_credit_note(
                    quote_id=quote.pk, amount=form.cleaned_data["amount"],
                    reference=form.cleaned_data["reference"], reason=form.cleaned_data["reason"],
                    actor=request.user,
                )
            except (ServiceFinanceError, ValidationError) as exc:
                form.add_error(None, str(exc))
            else:
                model_admin.message_user(request, "اصلاحیه کاهنده بدون تغییر پیش‌فاکتور اولیه ثبت شد.", messages.SUCCESS)
                return redirect("admin:website_order_change", order.pk)
    else:
        form = ServiceCreditNoteForm()
    return render(request, "admin/website/order/service_finance_action.html",
        _base_context(model_admin, request, order, "صدور اصلاحیه مالی کاهنده",
            form=form, quote=quote, action_type="credit"))


def request_service_refund_view(model_admin, request, order_id):
    if not model_admin.has_change_permission(request) or not request.user.has_perm("website.add_servicerefund"):
        raise PermissionDenied
    order = get_object_or_404(Order, pk=order_id)
    quote = get_object_or_404(Quote, order=order)
    if request.method == "POST":
        form = ServiceRefundRequestForm(request.POST, quote=quote)
        if form.is_valid():
            try:
                request_service_refund(
                    quote_id=quote.pk, payment_id=form.cleaned_data["original_payment"].pk,
                    amount=form.cleaned_data["amount"], method=form.cleaned_data["method"],
                    reason=form.cleaned_data["reason"], actor=request.user,
                    request_key=form.cleaned_data["request_key"],
                )
            except (ServiceFinanceError, ValidationError, ValueError) as exc:
                form.add_error(None, str(exc))
            else:
                model_admin.message_user(request,
                    "درخواست استرداد ایجاد شد؛ هیچ وجهی خودکار منتقل یا از دفتر مالی کسر نشده است.",
                    messages.SUCCESS)
                return redirect("admin:website_order_change", order.pk)
    else:
        form = ServiceRefundRequestForm(
            quote=quote,
            initial={"request_key": uuid4(), "amount": quote.refundable_excess, "method": "bank_transfer"},
        )
    return render(request, "admin/website/order/service_finance_action.html",
        _base_context(model_admin, request, order, "درخواست استرداد وجه",
            form=form, quote=quote, action_type="refund_request"))


def complete_service_refund_view(model_admin, request, order_id, refund_id):
    # Independent reviewer needs only read access to the parent order,
    # never broad authority to modify its price, items or status.
    if not model_admin.has_view_permission(request) or not (
        request.user.has_perm("website.approve_servicerefund")
        or request.user.has_perm("website.change_servicerefund")
    ):
        raise PermissionDenied
    order = get_object_or_404(Order, pk=order_id)
    refund = get_object_or_404(ServiceRefund, pk=refund_id, quote__order=order)
    quote = refund.quote
    requester = request.user.pk == refund.requested_by_id
    may_approve = request.user.has_perm("website.approve_servicerefund") and not requester
    may_finalize = request.user.has_perm("website.change_servicerefund") and not requester
    allowed_actions = set()
    if refund.status == "requested":
        if may_approve:
            allowed_actions.add("approve")
        if request.user.has_perm("website.change_servicerefund"):
            allowed_actions.add("cancel")
    elif refund.status == "approved":
        if may_finalize:
            allowed_actions.add("complete")
        if may_approve and may_finalize:
            allowed_actions.add("cancel")
    if request.method == "POST" and refund.status in {"requested", "approved"}:
        form = ServiceRefundDecisionForm(
            request.POST, status=refund.status, allowed_actions=allowed_actions,
        )
        if form.is_valid():
            try:
                if form.cleaned_data["action"] == "approve":
                    approve_service_refund(
                        refund_id=refund.pk, approval_note=form.cleaned_data["approval_note"],
                        actor=request.user,
                    )
                    outcome = "درخواست توسط مسئول مالی مستقل تأیید شد؛ هنوز وجهی منتقل نشده است."
                elif form.cleaned_data["action"] == "complete":
                    confirm_service_refund(
                        refund_id=refund.pk, actor=request.user,
                        payout_reference=form.cleaned_data["payout_reference"],
                        confirmed_external_payout=form.cleaned_data["confirmed"],
                    )
                    outcome = "بازپرداخت واقعی با سند بدهکار ثبت شد."
                else:
                    cancel_service_refund(
                        refund_id=refund.pk, actor=request.user,
                        reason=form.cleaned_data["cancellation_reason"],
                    )
                    outcome = "درخواست استرداد بدون پرداخت وجه لغو شد."
            except (ServiceFinanceError, ValidationError) as exc:
                form.add_error(None, str(exc))
            else:
                model_admin.message_user(request, outcome, messages.SUCCESS)
                return redirect("admin:website_order_change", order.pk)
    else:
        default_action = next(
            (name for name in ("approve", "complete", "cancel") if name in allowed_actions),
            "",
        )
        form = ServiceRefundDecisionForm(
            status=refund.status, allowed_actions=allowed_actions,
            initial={"action": default_action},
        )
    return render(request, "admin/website/order/service_finance_action.html",
        _base_context(model_admin, request, order, "تأیید دومرحله‌ای / ثبت رسید واقعی استرداد",
            form=form, quote=quote, refund=refund, action_type="refund_decision",
            can_submit=bool(allowed_actions)))
