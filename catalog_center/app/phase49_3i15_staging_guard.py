from __future__ import annotations

from . import phase49_3i15_bulk_discovery_images as bulk


def install_guard() -> None:
    """Require at least one successfully staged local image before readiness.

    The bulk flow is an image-acquisition workflow, not a remote-URL-only
    bookmarker. If public image URLs are visible but every browser-context
    download fails, the candidate must stay failed rather than being offered
    as ready/Add-to-Products.
    """
    if getattr(bulk, "_phase49_3i15_local_staging_guard_installed", False):
        return

    original_collect = bulk.collect_candidate_images

    async def collect_candidate_images(*args, **kwargs):
        result = await original_collect(*args, **kwargs)
        downloaded = [str(item).strip() for item in result.get("downloaded_images") or [] if str(item).strip()]
        if not downloaded:
            # Existing bulk worker treats a non-empty image_urls list as ready.
            # Clear it when nothing was actually staged so readiness, manifest
            # eligibility and Add-to-Products all fail closed together.
            result = dict(result)
            result["image_urls"] = []
            result["downloaded_images"] = []
        return result

    bulk.collect_candidate_images = collect_candidate_images
    bulk._phase49_3i15_local_staging_guard_installed = True
