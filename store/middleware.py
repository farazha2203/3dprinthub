from __future__ import annotations

from django.conf import settings

from .affiliate_services import (
    COOKIE_NAME,
    SESSION_KEY,
    attach_pending_referral,
    capture_referral,
    load_cookie_into_session,
    signed_referral_payload,
)


class AffiliateAttributionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        load_cookie_into_session(request)
        partner = campaign = None
        code = (request.GET.get("ref") or "").strip()
        campaign_slug = (request.GET.get("campaign") or "").strip()
        if code:
            partner, campaign, _ = capture_referral(request, code, campaign_slug)
        elif getattr(request, "user", None) and request.user.is_authenticated:
            attach_pending_referral(request)
        response = self.get_response(request)
        if partner:
            max_age = int(partner.effective_attribution_days) * 86400
            response.set_cookie(
                COOKIE_NAME,
                signed_referral_payload(partner.code, campaign.slug if campaign else ""),
                max_age=max_age,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
            )
        return response
