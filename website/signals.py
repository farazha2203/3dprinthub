from django.dispatch import receiver
from django.db.models.signals import post_save

from allauth.account.signals import user_logged_in, user_signed_up

from .models import CustomerProfile, SupportMessage


def _ensure_customer_profile(user):
    if not user or user.is_staff:
        return
    CustomerProfile.objects.get_or_create(
        user=user,
        defaults={
            "phone": None,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
        },
    )


@receiver(user_signed_up)
def create_profile_after_allauth_signup(request, user, **kwargs):
    _ensure_customer_profile(user)


@receiver(user_logged_in)
def repair_missing_profile_after_allauth_login(request, user, **kwargs):
    _ensure_customer_profile(user)

@receiver(post_save, sender=SupportMessage)
def notify_staff_after_customer_support_message(sender, instance, created, **kwargs):
    if not created or not instance.sender_id or instance.sender.is_staff:
        return
    try:
        from store.operator_notifications import notify_support_message
        notify_support_message(instance)
    except Exception:
        return
