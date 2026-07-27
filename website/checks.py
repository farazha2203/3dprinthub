from django.conf import settings
from django.core.checks import Error, Warning, register


@register()
def google_auth_configuration_check(app_configs, **kwargs):
    issues = []
    client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", "")
    if bool(client_id) != bool(client_secret):
        issues.append(
            Error(
                "Google OAuth requires both client ID and client secret.",
                hint="Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET together.",
                id="3dprinthub.E001",
            )
        )
    if getattr(settings, "SOCIALACCOUNT_LOGIN_ON_GET", False):
        issues.append(
            Error(
                "Google social login must be started with POST.",
                hint="Keep SOCIALACCOUNT_LOGIN_ON_GET=False.",
                id="3dprinthub.E002",
            )
        )
    if not client_id and not client_secret:
        issues.append(
            Warning(
                "Google membership is installed but disabled because credentials are empty.",
                hint="Add OAuth credentials to .env when you want the Google button enabled.",
                id="3dprinthub.W001",
            )
        )
    return issues


@register()
def online_payment_configuration_check(app_configs, **kwargs):
    issues = []
    if not bool(getattr(settings, "PAYMENT_GATEWAY_ENABLED", False)):
        return issues
    provider = str(getattr(settings, "PAYMENT_GATEWAY_PROVIDER", "zarinpal") or "").lower()
    if provider != "zarinpal":
        issues.append(
            Error(
                "Unsupported online payment provider is configured.",
                hint="Set PAYMENT_GATEWAY_PROVIDER=zarinpal.",
                id="3dprinthub.E030",
            )
        )
    if not str(getattr(settings, "ZARINPAL_MERCHANT_ID", "") or "").strip():
        issues.append(
            Error(
                "Online payment is enabled but ZARINPAL_MERCHANT_ID is empty.",
                hint="Set the merchant ID in the server .env or disable PAYMENT_GATEWAY_ENABLED.",
                id="3dprinthub.E031",
            )
        )
    if str(getattr(settings, "ZARINPAL_CURRENCY", "IRT") or "").upper() not in {"IRT", "IRR"}:
        issues.append(
            Error(
                "ZARINPAL_CURRENCY must be IRT or IRR.",
                hint="Use IRT when website amounts are stored in toman.",
                id="3dprinthub.E032",
            )
        )
    if not getattr(settings, "DEBUG", False) and bool(getattr(settings, "ZARINPAL_SANDBOX", False)):
        issues.append(
            Warning(
                "ZarinPal sandbox is enabled in production mode.",
                hint="Set ZARINPAL_SANDBOX=0 before accepting real payments.",
                id="3dprinthub.W030",
            )
        )
    return issues
