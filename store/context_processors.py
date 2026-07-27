from django.db.utils import OperationalError, ProgrammingError


def affiliate_ui(request):
    partner = None
    if getattr(request, "user", None) and request.user.is_authenticated:
        try:
            partner = request.user.affiliate_partner
        except (AttributeError, OperationalError, ProgrammingError):
            partner = None
    return {"current_affiliate_partner": partner}
