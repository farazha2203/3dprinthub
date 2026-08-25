from __future__ import annotations

from pathlib import PurePosixPath
from urllib.parse import urlsplit

from .models import HomepageHeroSlide


_IMPORTED_MEDIA_PREFIX = "/media/store/imported-models/"


def _field_url(field_file) -> str:
    if not field_file:
        return ""
    try:
        return str(field_file.url or "").strip()
    except Exception:
        return ""


def _field_name(field_file) -> str:
    if not field_file:
        return ""
    try:
        return str(field_file.name or "").strip()
    except Exception:
        return ""


def _basename(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    path = urlsplit(value).path if "://" in value else value
    return PurePosixPath(path.replace("\\", "/")).name


def _is_imported_catalog_media(url: str) -> bool:
    path = urlsplit(str(url or "")).path
    return path.startswith(_IMPORTED_MEDIA_PREFIX)


def _product_owned_media_url(slide: HomepageHeroSlide, selected=None) -> str:
    asset = getattr(slide, "asset", None)
    product = getattr(asset, "product", None) if asset is not None else None
    if product is None:
        return ""

    requested_names = []
    if selected is not None:
        name = _basename(_field_name(getattr(selected, "image", None)))
        if name:
            requested_names.append(name)
    explicit_name = _basename(str(getattr(slide, "image_url", "") or ""))
    if explicit_name and explicit_name not in requested_names:
        requested_names.append(explicit_name)

    candidates = []
    main = getattr(product, "main_image", None)
    if main:
        candidates.append(main)
    try:
        candidates.extend(row.image for row in product.images.all().order_by("sort_order", "id") if row.image)
    except Exception:
        pass

    for requested in requested_names:
        for candidate in candidates:
            if _basename(_field_name(candidate)) == requested:
                url = _field_url(candidate)
                if url:
                    return url

    # The Product publish path owns the public media namespace. If an exact
    # selected-image match is unavailable, prefer the Product main image over
    # exposing an ImportedPrintAssetImage path that Production intentionally
    # does not serve publicly.
    return _field_url(main)


def _safe_effective_image_url(slide: HomepageHeroSlide) -> str:
    selected = None
    if getattr(slide, "selected_asset_image_id", None):
        try:
            selected = slide.selected_asset_image
        except Exception:
            selected = None

    product_url = _product_owned_media_url(slide, selected)
    if product_url:
        return product_url

    explicit = str(getattr(slide, "image_url", "") or "").strip()
    if explicit and not _is_imported_catalog_media(explicit):
        return explicit

    if selected is not None:
        selected_url = _field_url(getattr(selected, "image", None))
        if selected_url and not _is_imported_catalog_media(selected_url):
            return selected_url
        remote = str(getattr(selected, "remote_url", "") or "").strip()
        if remote:
            return remote

    asset = getattr(slide, "asset", None)
    remote = str(getattr(asset, "remote_image_url", "") or "").strip() if asset is not None else ""
    if remote:
        return remote

    return ""


# Final public-media boundary for Phase49.3I.30. The earlier Hero Studio keeps
# the selected ImportedPrintAssetImage relation for editing/audit, while public
# rendering resolves to Product-owned media whenever the Product has already
# been published.
HomepageHeroSlide.effective_image_url = property(_safe_effective_image_url)
