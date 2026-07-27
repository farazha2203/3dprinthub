from django.conf import settings
from django.db import OperationalError, ProgrammingError

from .models import SEOSettings, SupportMessage


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
        "unread_store_notifications": unread_notifications,
        "unread_support_messages": unread_support_messages,
        "google_login_enabled": bool(getattr(settings, "GOOGLE_OAUTH_ENABLED", False)),
    }
