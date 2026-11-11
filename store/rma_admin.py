"""Permission-gated Store RMA actions, never an editable status dropdown."""
from uuid import uuid4

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import ReturnRequest, StorePayment, StoreReturnInspection, StoreReturnRefund
from .rma_services import (
    StoreRMAError, decide_store_return, inspect_return,
    request_store_return_refund, approve_store_return_refund,
    confirm_store_return_refund, cancel_store_return_refund,
)


class ReviewForm(forms.Form):
    decision = forms.ChoiceField(
        label="تصمیم کارشناسی",
        choices=[("reviewing", "در حال بررسی"), ("approved", "تأیید مرجوعی"), ("rejected", "رد درخواست")],
    )
    response = forms.CharField(
        min_length=8, label="دلیل تصمیم/پاسخ مشتری",
        widget=forms.Textarea(attrs={"rows": 4}),
    )


class InspectionForm(forms.Form):
    received_quantity = forms.IntegerField(
        label="تعداد کالای واقعاً دریافت‌شده و بررسی‌شده", min_value=1,
    )
    restock_quantity = forms.IntegerField(
        label="تعداد سالم قابل بازگشت به موجودی عددی همان تنوع", min_value=0,
    )
    inspection_note = forms.CharField(
        min_length=8, label="نتیجه بازرسی / وضعیت قطعه معیوب",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    approved = forms.BooleanField(
        label="با بررسی فیزیکی تأیید می‌کنم فقط تعداد سالم به انبار افزوده شود.",
    )


class RefundRequestForm(forms.Form):
    request_key = forms.UUIDField(widget=forms.HiddenInput)
    payment = forms.ModelChoiceField(queryset=StorePayment.objects.none(), label="رسید پرداخت اصلی (تأییدشده)")
    amount = forms.IntegerField(min_value=1, label="مبلغ درخواستی استرداد (تومان)")
    method = forms.ChoiceField(choices=StoreReturnRefund.METHOD_CHOICES, label="روش بازپرداخت واقعی")
    reason = forms.CharField(
        min_length=8, label="مستندات مبلغ استرداد",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    approved = forms.BooleanField(
        label="درک می‌کنم این فرم فقط درخواست است و وجهی را منتقل یا از حساب کسر نمی‌کند.",
    )

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        if order:
            self.fields["payment"].queryset = StorePayment.objects.filter(
                order=order, status="paid"
            ).order_by("id")


class RefundDecisionForm(forms.Form):
    action = forms.ChoiceField(choices=(), label="تصمیم مالی")
    approval_note = forms.CharField(
        required=False, label="توضیح تأیید مستقل مسئول مالی دوم",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    payout_reference = forms.CharField(
        max_length=180, required=False, label="شناسه بانکی/پوز یا رسید تسلیم نقدی",
    )
    cancellation_reason = forms.CharField(
        required=False, label="دلیل لغو", widget=forms.Textarea(attrs={"rows": 3}),
    )
    confirmed = forms.BooleanField(
        required=False,
        label="رسید بیرونی را بررسی کردم و بازپرداخت واقعی به مشتری انجام شده است.",
    )

    def __init__(self, *args, status="requested", **kwargs):
        super().__init__(*args, **kwargs)
        if status == "requested":
            self.fields["action"].choices = [
                ("approve", "تأیید مستقل بدون جابه‌جایی پول"),
                ("cancel", "لغو درخواست بدون پرداخت"),
            ]
        elif status == "approved":
            self.fields["action"].choices = [
                ("complete", "ثبت رسید بازپرداخت واقعی"),
                ("cancel", "لغو استرداد تأییدشده بدون پرداخت"),
            ]

    def clean(self):
        data = super().clean()
        if data.get("action") == "approve":
            if len((data.get("approval_note") or "").strip()) < 8:
                self.add_error("approval_note", "تأییدکننده باید دلیل مستند بنویسد.")
        elif data.get("action") == "complete":
            if len((data.get("payout_reference") or "").strip()) < 4:
                self.add_error("payout_reference", "شناسه بیرونی معتبر را ثبت کنید.")
            if not data.get("confirmed"):
                self.add_error("confirmed", "بدون احراز پرداخت واقعی، سند بدهکار ثبت نمی‌شود.")
        elif data.get("action") == "cancel" and len((data.get("cancellation_reason") or "").strip()) < 8:
            self.add_error("cancellation_reason", "برای لغو دلیل حداقل ۸ نویسه بنویسید.")
        return data


def rma_workflow_summary(rma):
    if not rma or not rma.pk:
        return "درخواست را ذخیره کنید تا سوابق قابل مشاهده شوند."
    url = lambda name, *args: reverse(name, args=[rma.pk, *args])
    fragments = []
    if rma.status in {"submitted", "reviewing"}:
        fragments.append(("بررسی و تأیید/رد درخواست", url("admin:store_returnrequest_workflow_review")))
    if rma.status == "approved":
        fragments.append(("ثبت بازرسی و دریافت کالا", url("admin:store_returnrequest_workflow_inspect")))
    if rma.status in {"received", "refunded"}:
        fragments.append(("درخواست بازپرداخت مستند", url("admin:store_returnrequest_workflow_request_refund")))
    refunds = list(rma.refunds.select_related("payment", "completed_by", "approved_by", "requested_by").order_by("-id"))
    pending = [r for r in refunds if r.status in {"requested", "approved"}]
    for refund in pending:
        fragments.append((
            f"تأیید/لغو استرداد {refund.amount:,} تومان", url(
                "admin:store_returnrequest_workflow_decide_refund", refund.pk
            ),
        ))
    links = format_html_join(" ", '<a class="button" style="margin:4px" href="{}">{}</a>',
        ((href, title) for title, href in fragments))
    history = format_html_join("", '<li>{} تومان | {} | درخواست: {} | تأیید مستقل: {} | رسید {}</li>', (
        (f"{refund.amount:,}", refund.get_status_display(), refund.requested_by.get_username(),
         refund.approved_by.get_username() if refund.approved_by_id else "در انتظار",
         refund.payout_reference or "هنوز پرداخت نشده")
        for refund in refunds
    ))
    if hasattr(rma, "inspection"):
        i = rma.inspection
        inspection = format_html(
            "<p>کالای دریافتی: {} عدد | بازگشت سالم به انبار: {} عدد"
            " | گردش موجودی: {} | بازرس: {}</p>",
            i.received_quantity, i.restock_quantity,
            i.inventory_movement_id or "بدون تغییر موجودی",
            i.inspected_by.get_username(),
        )
    else:
        inspection = "هنوز دریافت و بازرسی واقعی انجام نشده است."
    return format_html(
        '<section dir="rtl"><p>درخواست مرجوعی {} | وضعیت: <strong>{}</strong>'
        ' | تعداد: {} | ردیف سفارش: {}</p>{}<div>{}</div>'
        '<h4>بازپرداخت‌های مرتبط</h4><ul>{}</ul>'
        '<p>استرداد وجه مستقل از بازگشت موجودی است؛ هیچ عملیات بانکی خودکار اجرا نمی‌شود.</p></section>',
        rma.pk, rma.get_status_display(), rma.quantity,
        rma.item.variant_code if rma.item_id else "فاقد ردیف مشخص",
        inspection, links, history,
    )


def rma_action_view(model_admin, request, return_id, action, refund_id=None):
    permission = {
        "review": "store.change_returnrequest",
        "inspect": "store.add_storereturninspection",
        "request-refund": "store.add_storereturnrefund",
        "decide-refund": "store.change_storereturnrefund",
    }.get(action)
    if not permission or not model_admin.has_change_permission(request):
        raise PermissionDenied
    if action == "decide-refund":
        if not (request.user.has_perm("store.change_storereturnrefund") or
                request.user.has_perm("store.approve_storereturnrefund")):
            raise PermissionDenied
    elif not request.user.has_perm(permission):
        raise PermissionDenied
    rma = get_object_or_404(
        ReturnRequest.objects.select_related("order", "item", "item__variant", "user"),
        pk=return_id,
    )
    refund = None
    if action == "decide-refund":
        refund = get_object_or_404(StoreReturnRefund, pk=refund_id, return_request=rma)
    form_cls = {
        "review": ReviewForm,
        "inspect": InspectionForm,
        "request-refund": RefundRequestForm,
        "decide-refund": RefundDecisionForm,
    }[action]
    extra = {"order": rma.order} if action == "request-refund" else {}
    if action == "decide-refund":
        extra["status"] = refund.status
    if request.method == "POST" and (refund is None or refund.status in {"requested", "approved"}):
        form = form_cls(request.POST, **extra)
        if form.is_valid():
            try:
                if action == "review":
                    decide_store_return(
                        return_id=rma.pk, decision=form.cleaned_data["decision"],
                        response=form.cleaned_data["response"], actor=request.user,
                    )
                    success = "نتیجه بررسی مرجوعی به‌صورت مستند ثبت شد."
                elif action == "inspect":
                    inspect_return(
                        return_id=rma.pk,
                        received_quantity=form.cleaned_data["received_quantity"],
                        restock_quantity=form.cleaned_data["restock_quantity"],
                        inspection_note=form.cleaned_data["inspection_note"],
                        actor=request.user,
                    )
                    success = "بازرسی ثبت شد؛ فقط موجودی قطعات سالم تغییر کرد."
                elif action == "request-refund":
                    request_store_return_refund(
                        return_id=rma.pk, payment_id=form.cleaned_data["payment"].pk,
                        amount=form.cleaned_data["amount"], method=form.cleaned_data["method"],
                        reason=form.cleaned_data["reason"], actor=request.user,
                        request_key=form.cleaned_data["request_key"],
                    )
                    success = "درخواست بازپرداخت ثبت شد؛ هنوز وجهی پرداخت یا از حساب کسر نشده است."
                elif form.cleaned_data["action"] == "approve":
                    approve_store_return_refund(
                        refund_id=refund.pk, approval_note=form.cleaned_data["approval_note"],
                        actor=request.user,
                    )
                    success = "تأیید مستقل ثبت شد، ولی هیچ پولی انتقال نیافته است."
                elif form.cleaned_data["action"] == "complete":
                    confirm_store_return_refund(
                        refund_id=refund.pk, actor=request.user,
                        payout_reference=form.cleaned_data["payout_reference"],
                        confirmed_external_payout=form.cleaned_data["confirmed"],
                    )
                    success = "رسید استرداد واقعی بررسی و سند بدهکار ثبت شد."
                else:
                    cancel_store_return_refund(
                        refund_id=refund.pk, actor=request.user,
                        cancellation_reason=form.cleaned_data["cancellation_reason"],
                    )
                    success = "درخواست بازپرداخت بدون جابه‌جایی وجه لغو شد."
            except (StoreRMAError, ValidationError, ValueError) as exc:
                form.add_error(None, str(exc))
            else:
                model_admin.message_user(request, success, messages.SUCCESS)
                return redirect("admin:store_returnrequest_change", rma.pk)
    else:
        initial = {}
        if action == "inspect":
            initial = {
                "received_quantity": rma.quantity, "restock_quantity": 0,
            }
        elif action == "request-refund":
            initial = {"request_key": uuid4(), "method": "bank_transfer"}
        elif action == "review":
            initial = {"decision": "approved"}
        if action == "decide-refund":
            initial["action"] = "approve" if refund.status == "requested" else "complete"
        form = form_cls(initial=initial, **extra)
    titles = {
        "review": "تصمیم کارشناسی مرجوعی",
        "inspect": "تحویل فیزیکی و بازرسی تنوع محصول",
        "request-refund": "درخواست بازپرداخت واقعی به مشتری",
        "decide-refund": "تأیید مستقل دومرحله‌ای / ثبت رسید استرداد",
    }
    return render(request, "admin/store/return_workflow_action.html", {
        **model_admin.admin_site.each_context(request),
        "title": titles[action],
        "opts": model_admin.model._meta, "original": rma,
        "rma": rma, "refund": refund, "form": form, "action": action,
        "return_url": reverse("admin:store_returnrequest_change", args=[rma.pk]),
    })
