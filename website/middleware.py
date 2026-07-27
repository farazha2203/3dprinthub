from django.http import Http404

class AdminAccessGuardMiddleware:
    """Hide Django admin from authenticated non-staff customer accounts."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        protected_admin_paths = ("/admin/", "/smart-admin/")
        if request.path.startswith(protected_admin_paths) and request.user.is_authenticated:
            if not (request.user.is_active and request.user.is_staff):
                raise Http404("صفحه پیدا نشد")
        return self.get_response(request)
