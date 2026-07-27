from __future__ import annotations

import random
from collections import OrderedDict

from store.catalog_sync import public_catalog_queryset
from store.models import CatalogCategoryRule



def presentation_assets(*, limit=12, randomize=False, newest_first=False):
    """Return visible catalog references with a usable local or remote image.

    ``newest_first`` is used by the homepage hero so every newly imported
    catalog reference can appear immediately after the next page load.
    """
    from django.db.models import Q

    limit = max(1, min(int(limit or 1), 60))
    pool_limit = max(limit * 12, 120)
    queryset = (
        public_catalog_queryset()
        .filter(
            (Q(preview_image__isnull=False) & ~Q(preview_image=""))
            | ~Q(remote_image_url="")
            | ~Q(metrics__image_urls=[])
        )
        .select_related("source", "metrics", "metrics__publication")
        .prefetch_related("images")
    )
    if newest_first:
        queryset = queryset.order_by("-imported_at", "-id")
    else:
        queryset = queryset.order_by(
            "metrics__popularity_rank",
            "-metrics__downloads_count",
            "-imported_at",
        )
    queryset = queryset[:pool_limit]
    assets = [asset for asset in queryset if asset.catalog_image_url]
    if randomize and len(assets) > 1:
        random.SystemRandom().shuffle(assets)
    return assets[:limit]


def categorized_presentation(*, limit=9, randomize=True):
    limit = max(1, min(int(limit or 1), 60))
    assets = presentation_assets(limit=max(limit * 5, 45), randomize=randomize)
    groups = OrderedDict()
    labels = dict(CatalogCategoryRule.SEGMENT_CHOICES)
    for asset in assets:
        segment = asset.metrics.segment or "other"
        group = groups.setdefault(segment, {
            "key": segment,
            "label": labels.get(segment, "سایر"),
            "items": [],
            "count": 0,
        })
        group["count"] += 1
        if len(group["items"]) < limit:
            group["items"].append(asset)
    flattened = []
    for group in groups.values():
        for asset in group["items"]:
            if asset not in flattened:
                flattened.append(asset)
            if len(flattened) >= limit:
                break
        if len(flattened) >= limit:
            break
    return list(groups.values()), flattened
