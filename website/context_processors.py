from django.conf import settings
from django.db import OperationalError, ProgrammingError

from .models import SEOSettings, SiteSetting, SupportMessage


def _public_whatsapp_url(phone):
    import re

    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("00"):
        digits = digits[2:]
    elif digits.startswith("0"):
        digits = "98" + digits[1:]
    return f"https://wa.me/{digits}" if digits else ""


def _public_instagram_url(site_settings, seo_settings):
    configured = getattr(site_settings, "instagram", "") if site_settings else ""
    if configured:
        return configured.strip()

    same_as = getattr(seo_settings, "same_as", "") if seo_settings else ""
    for candidate in (same_as or "").splitlines():
        candidate = candidate.strip()
        if "instagram.com/" in candidate.lower():
            return candidate

    # This is the same owner-verified profile already emitted by the
    # Organization schema in store.templatetags.store_seo.
    return "https://www.instagram.com/3dprinthub_ir/"


def customer_ui(request):
    theme = "original"
    prompt = True
    profile = None
    unread_support_messages = 0

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            profile = getattr(user, "customer_profile", None)
            if profile is not None:
                theme = profile.theme_preference or "original"
                prompt = not profile.theme_prompt_seen
            else:
                prompt = False
        except (OperationalError, ProgrammingError):
            prompt = False

        if not user.is_staff:
            try:
                unread_support_messages = SupportMessage.objects.filter(
                    conversation__customer=user,
                    sender__is_staff=True,
                    read_by_customer_at__isnull=True,
                ).count()
            except (OperationalError, ProgrammingError):
                unread_support_messages = 0

    try:
        seo_settings = SEOSettings.objects.first()
    except (OperationalError, ProgrammingError):
        seo_settings = None

    try:
        public_site_settings = SiteSetting.objects.first()
    except (OperationalError, ProgrammingError):
        public_site_settings = None

    unread_notifications = 0
    if user and user.is_authenticated:
        try:
            from store.models import CustomerNotification
            unread_notifications = CustomerNotification.objects.filter(
                user=user, read_at__isnull=True
            ).count()
        except (OperationalError, ProgrammingError):
            unread_notifications = 0

    return {
        "customer_profile": profile,
        "customer_theme": theme,
        "customer_theme_prompt": prompt,
        "customer_theme_endpoint": "/customer/theme/",
        "seo_settings": seo_settings,
        "public_site_settings": public_site_settings,
        "public_instagram_url": _public_instagram_url(public_site_settings, seo_settings),
        "public_whatsapp_url": _public_whatsapp_url(
            public_site_settings.whatsapp if public_site_settings else ""
        ),
        "unread_store_notifications": unread_notifications,
        "unread_support_messages": unread_support_messages,
        "google_login_enabled": bool(getattr(settings, "GOOGLE_OAUTH_ENABLED", False)),
    }
