from django.dispatch import receiver

from allauth.account.signals import user_logged_in, user_signed_up

from .models import CustomerProfile


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
