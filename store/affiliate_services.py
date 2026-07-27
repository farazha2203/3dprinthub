from __future__ import annotations

import hashlib
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (
    AffiliateAttribution,
    AffiliateCampaign,
    AffiliateClick,
    AffiliateCommission,
    AffiliateLedgerEntry,
    AffiliatePartner,
    AffiliatePayout,
    AffiliatePayoutItem,
    StoreOrder,
)

SESSION_KEY = "affiliate_pending_referral"
COOKIE_SALT = "3dprinthub.affiliate.v1"
COOKIE_NAME = getattr(settings, "AFFILIATE_COOKIE_NAME", "dph_ref")


def _hash(value: str) -> str:
    return hashlib.sha256(f"{settings.SECRET_KEY}:{value}".encode("utf-8")).hexdigest()


def _client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", ""))[:100]


def signed_referral_payload(code: str, campaign_slug: str = "") -> str:
    return signing.dumps({"code": code, "campaign": campaign_slug}, salt=COOKIE_SALT, compress=True)


def read_signed_referral(value: str) -> dict:
    if not value:
        return {}
    try:
        return signing.loads(value, salt=COOKIE_SALT, max_age=90 * 86400)
    except signing.BadSignature:
        return {}


def active_partner(code: str):
    return AffiliatePartner.objects.select_related("tier", "user").filter(code__iexact=(code or "").strip(), status="active", tier__is_active=True).first()


def capture_referral(request, code: str, campaign_slug: str = "", landing_path: str = ""):
    partner = active_partner(code)
    if not partner:
        return None, None, None
    campaign = None
    if campaign_slug:
        campaign = AffiliateCampaign.objects.filter(partner=partner, slug=campaign_slug, is_active=True).first()
    if not request.session.session_key:
        request.session.create()
    visitor_seed = request.session.session_key or request.COOKIES.get("sessionid", "anonymous")
    click = AffiliateClick.objects.create(
        partner=partner,
        campaign=campaign,
        user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
        visitor_hash=_hash(visitor_seed),
        ip_hash=_hash(_client_ip(request)) if _client_ip(request) else "",
        user_agent_hash=_hash(request.META.get("HTTP_USER_AGENT", "")) if request.META.get("HTTP_USER_AGENT") else "",
        landing_path=(landing_path or request.get_full_path())[:500],
        referrer_url=request.META.get("HTTP_REFERER", "")[:500],
    )
    request.session[SESSION_KEY] = {"code": partner.code, "campaign": campaign.slug if campaign else "", "click_id": click.pk}
    request.session.modified = True
    if getattr(request, "user", None) and request.user.is_authenticated:
        attach_pending_referral(request)
    return partner, campaign, click


def load_cookie_into_session(request):
    if request.session.get(SESSION_KEY):
        return
    payload = read_signed_referral(request.COOKIES.get(COOKIE_NAME, ""))
    if payload.get("code"):
        request.session[SESSION_KEY] = {"code": payload.get("code", ""), "campaign": payload.get("campaign", ""), "click_id": None}
        request.session.modified = True


@transaction.atomic
def attach_pending_referral(request):
    if not getattr(request, "user", None) or not request.user.is_authenticated or request.user.is_staff:
        return None
    existing = AffiliateAttribution.objects.select_related("partner").filter(customer=request.user).first()
    if existing:
        return existing
    pending = request.session.get(SESSION_KEY) or {}
    partner = active_partner(pending.get("code", ""))
    if not partner or partner.user_id == request.user.id:
        return None
    campaign = None
    if pending.get("campaign"):
        campaign = AffiliateCampaign.objects.filter(partner=partner, slug=pending["campaign"], is_active=True).first()
    click = AffiliateClick.objects.filter(pk=pending.get("click_id"), partner=partner).first() if pending.get("click_id") else None
    attribution = AffiliateAttribution.objects.create(customer=request.user, partner=partner, campaign=campaign, click=click)
    if click and click.user_id != request.user.id:
        click.user = request.user
        click.save(update_fields=["user"])
    return attribution


@transaction.atomic
def assign_order_partner(order: StoreOrder):
    order = StoreOrder.objects.select_for_update().select_related("user").get(pk=order.pk)
    if order.affiliate_partner_id:
        return order.affiliate_partner
    attribution = AffiliateAttribution.objects.select_related("partner", "campaign", "partner__tier").filter(customer=order.user, partner__status="active").first()
    partner = attribution.partner if attribution else None
    campaign = attribution.campaign if attribution else None
    if not partner:
        own = AffiliatePartner.objects.select_related("tier").filter(user=order.user, status="active", tier__is_active=True).first()
        if own and own.effective_include_self_orders:
            partner = own
    if not partner:
        return None
    StoreOrder.objects.filter(pk=order.pk).update(affiliate_partner=partner, affiliate_campaign=campaign, affiliate_code=partner.code)
    order.affiliate_partner = partner
    order.affiliate_campaign = campaign
    order.affiliate_code = partner.code
    return partner


def commission_amount(partner: AffiliatePartner, basis: int) -> int:
    if partner.effective_commission_type == "fixed":
        return max(0, int(partner.effective_commission_value))
    value = (Decimal(max(0, basis)) * Decimal(partner.effective_commission_value) / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return max(0, int(value))


@transaction.atomic
def create_commission_for_order(order: StoreOrder):
    order = StoreOrder.objects.select_for_update().select_related("user", "affiliate_partner", "affiliate_campaign").get(pk=order.pk)
    if order.payment_status != "paid":
        return None
    partner = order.affiliate_partner or assign_order_partner(order)
    if not partner or partner.status != "active":
        return None
    if partner.user_id == order.user_id and not partner.effective_include_self_orders:
        return None
    basis = max(0, int(order.subtotal) - int(order.discount_amount))
    amount = commission_amount(partner, basis)
    if amount <= 0:
        return None
    attribution = AffiliateAttribution.objects.filter(customer=order.user, partner=partner).first()
    commission, _ = AffiliateCommission.objects.get_or_create(
        order=order,
        defaults={
            "partner": partner,
            "campaign": order.affiliate_campaign,
            "attribution": attribution,
            "commission_type": partner.effective_commission_type,
            "commission_value": partner.effective_commission_value,
            "basis_amount": basis,
            "amount": amount,
            "status": "pending",
        },
    )
    return commission


@transaction.atomic
def schedule_commission_after_delivery(order: StoreOrder):
    commission = create_commission_for_order(order)
    if not commission or commission.status != "pending":
        return commission
    commission.eligible_at = timezone.now() + timedelta(days=commission.partner.effective_hold_days)
    commission.save(update_fields=["eligible_at", "updated_at"])
    return commission


@transaction.atomic
def approve_commission(commission: AffiliateCommission, actor=None):
    commission = AffiliateCommission.objects.select_for_update().select_related("partner", "order").get(pk=commission.pk)
    if commission.status != "pending" or commission.order.status != "delivered" or commission.order.payment_status != "paid":
        return False
    if commission.eligible_at and commission.eligible_at > timezone.now():
        return False
    commission.status = "approved"
    commission.approved_at = timezone.now()
    commission.save(update_fields=["status", "approved_at", "updated_at"])
    AffiliateLedgerEntry.objects.get_or_create(
        commission=commission,
        entry_type="commission",
        defaults={"partner": commission.partner, "amount": commission.amount, "note": f"پورسانت سفارش {commission.order.order_number}", "created_by": actor},
    )
    return True


def approve_due_commissions(actor=None):
    qs = AffiliateCommission.objects.filter(status="pending", order__status="delivered", order__payment_status="paid").filter(eligible_at__lte=timezone.now())
    count = 0
    for commission in qs.iterator():
        if approve_commission(commission, actor=actor):
            count += 1
    return count


@transaction.atomic
def reverse_commission(order: StoreOrder, reason="لغو یا استرداد سفارش", actor=None):
    commission = AffiliateCommission.objects.select_for_update().filter(order=order).select_related("partner").first()
    if not commission or commission.status in {"reversed", "cancelled"}:
        return False
    previous = commission.status
    if previous == "requested":
        item = AffiliatePayoutItem.objects.select_related("payout").filter(commission=commission).first()
        if item and item.payout.status in {"requested", "approved"}:
            payout = item.payout
            payout.amount = max(0, int(payout.amount) - int(item.amount))
            item.delete()
            if payout.amount == 0:
                payout.status = "cancelled"
                payout.processed_at = timezone.now()
            payout.save(update_fields=["amount", "status", "processed_at"])
    if previous in {"approved", "requested", "paid"}:
        AffiliateLedgerEntry.objects.get_or_create(
            commission=commission,
            entry_type="reversal",
            defaults={"partner": commission.partner, "amount": -int(commission.amount), "note": reason, "created_by": actor},
        )
    commission.status = "reversed"
    commission.reversed_at = timezone.now()
    commission.note = (commission.note + "\n" + reason).strip()
    commission.save(update_fields=["status", "reversed_at", "note", "updated_at"])
    return True


@transaction.atomic
def request_partner_payout(partner: AffiliatePartner, note=""):
    partner = AffiliatePartner.objects.select_for_update().select_related("tier").get(pk=partner.pk)
    if partner.status != "active":
        raise ValidationError("حساب همکاری فعال نیست.")
    if AffiliatePayout.objects.filter(partner=partner, status__in=["requested", "approved"]).exists():
        raise ValidationError("یک درخواست تسویه باز دارید.")
    commissions = list(AffiliateCommission.objects.select_for_update().filter(partner=partner, status="approved").order_by("approved_at", "id"))
    total = sum(int(item.amount) for item in commissions)
    balance = int(partner.ledger_entries.aggregate(value=Sum("amount"))["value"] or 0)
    total = min(total, balance)
    if total < int(partner.effective_minimum_payout):
        raise ValidationError(f"حداقل مبلغ تسویه {int(partner.effective_minimum_payout):,} تومان است.")
    selected, running = [], 0
    for commission in commissions:
        if running + int(commission.amount) > total:
            break
        selected.append(commission)
        running += int(commission.amount)
    if not selected:
        raise ValidationError("پورسانت قابل تخصیص برای تسویه وجود ندارد.")
    payout = AffiliatePayout.objects.create(
        partner=partner,
        amount=running,
        sheba_number=partner.sheba_number,
        card_number=partner.card_number,
        account_holder=partner.account_holder,
        partner_note=note,
    )
    AffiliatePayoutItem.objects.bulk_create([AffiliatePayoutItem(payout=payout, commission=c, amount=c.amount) for c in selected])
    AffiliateCommission.objects.filter(pk__in=[c.pk for c in selected]).update(status="requested", updated_at=timezone.now())
    return payout


@transaction.atomic
def mark_payout_paid(payout: AffiliatePayout, actor=None, reference_number=""):
    payout = AffiliatePayout.objects.select_for_update().select_related("partner").get(pk=payout.pk)
    if payout.status == "paid":
        return payout
    if payout.status not in {"requested", "approved"}:
        raise ValidationError("این درخواست در وضعیت قابل پرداخت نیست.")
    payout.status = "paid"
    payout.reference_number = reference_number or payout.reference_number
    payout.processed_at = timezone.now()
    payout.save(update_fields=["status", "reference_number", "processed_at"])
    commission_ids = list(payout.items.values_list("commission_id", flat=True))
    AffiliateCommission.objects.filter(pk__in=commission_ids).update(status="paid", paid_at=timezone.now(), updated_at=timezone.now())
    AffiliateLedgerEntry.objects.get_or_create(
        payout=payout,
        entry_type="payout",
        defaults={"partner": payout.partner, "amount": -int(payout.amount), "note": f"تسویه {payout.payout_number}", "created_by": actor},
    )
    return payout


@transaction.atomic
def reject_payout(payout: AffiliatePayout, actor=None, note=""):
    payout = AffiliatePayout.objects.select_for_update().get(pk=payout.pk)
    if payout.status not in {"requested", "approved"}:
        return payout
    commission_ids = list(payout.items.values_list("commission_id", flat=True))
    AffiliateCommission.objects.filter(pk__in=commission_ids, status="requested").update(status="approved", updated_at=timezone.now())
    payout.status = "rejected"
    payout.admin_note = note or payout.admin_note
    payout.processed_at = timezone.now()
    payout.save(update_fields=["status", "admin_note", "processed_at"])
    return payout


def safe_campaign_target(campaign: AffiliateCampaign | None, request) -> str:
    target = campaign.target_path if campaign else "/"
    if not target.startswith("/") or not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        target = "/"
    params = {}
    if campaign:
        if campaign.utm_source:
            params["utm_source"] = campaign.utm_source
        if campaign.utm_medium:
            params["utm_medium"] = campaign.utm_medium
        if campaign.utm_campaign:
            params["utm_campaign"] = campaign.utm_campaign
    if params:
        target += ("&" if "?" in target else "?") + urlencode(params)
    return target


def masked_customer(user) -> str:
    name = user.get_full_name().strip() or "مشتری"
    parts = name.split()
    if len(parts) > 1:
        name = f"{parts[0]} {parts[-1][:1]}***"
    phone = user.username if str(user.username).isdigit() else ""
    masked = f"{phone[:4]}***{phone[-3:]}" if len(phone) >= 8 else ""
    return f"{name} {masked}".strip()
