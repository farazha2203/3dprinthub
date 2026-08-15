from __future__ import annotations

from pathlib import PurePosixPath

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.views.static import serve


PUBLIC_STORE_MEDIA_PREFIXES = (
    "store/products/",
    "store/categories/",
    "store/seo/",
)


def _safe_public_store_path(path: str) -> str:
    value = str(path or "").replace("\\", "/").lstrip("/")
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or ".." in pure.parts:
        raise Http404("Invalid media path.")
    if value.startswith("store/private-models/"):
        raise Http404("Private model files are never public.")
    if not value.startswith(PUBLIC_STORE_MEDIA_PREFIXES):
        raise Http404("Media path is not public.")
    return value


def serve_public_store_media(request: HttpRequest, path: str) -> HttpResponse:
    """Shared-hosting fallback for public Store media only.

    Apache/cPanel may serve an existing file before this view is reached. If it
    does not, this view serves only explicitly public Store image prefixes from
    Django's configured MEDIA_ROOT. Private 3D model uploads are never exposed.
    """

    safe_path = _safe_public_store_path(path)
    response = serve(request, safe_path, document_root=settings.MEDIA_ROOT)
    response["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=3600"
    response["X-Content-Type-Options"] = "nosniff"
    return response
