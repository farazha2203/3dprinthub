from django.db import OperationalError, ProgrammingError
from .models import SEOSettings

def customer_ui(request):
    theme = "original"
    prompt = True
    profile = None
    if getattr(request, "user", None) and request.user.is_authenticated:
        try:
            profile = request.user.customer_profile
            theme = profile.theme_preference or "original"
            prompt = not profile.theme_prompt_seen
        except Exception:
            prompt = False
    try:
        seo_settings = SEOSettings.objects.first()
    except (OperationalError, ProgrammingError):
        seo_settings = None
    unread_notifications = 0
    if getattr(request, "user", None) and request.user.is_authenticated:
        try:
            from store.models import CustomerNotification
            unread_notifications = CustomerNotification.objects.filter(user=request.user, read_at__isnull=True).count()
        except (OperationalError, ProgrammingError):
            unread_notifications = 0
    return {
        "customer_theme": theme,
        "customer_theme_prompt": prompt,
        "customer_theme_endpoint": "/customer/theme/",
        "seo_settings": seo_settings,
        "unread_store_notifications": unread_notifications,
    }
