from __future__ import annotations

import re

from .common import CatalogCandidate
from .html_site import HTMLCatalogAdapter


class GrabCADAdapter(HTMLCatalogAdapter):
    key = "grabcad"
    allowed_domains = ("grabcad.com",)
    model_link_pattern = re.compile(r"/library/([^/?#]+)", re.I)
    id_patterns = (r"/library/([^/?#]+)",)
    sort_mapping = {
        "downloads": "most-downloaded",
        "likes": "most-liked",
        "views": "most-viewed",
        "trending": "popular",
        "newest": "recent",
    }
    default_listing_template = "https://grabcad.com/library?page={page}"

    def discover(self, *, limit: int, sort_mode: str) -> list[CatalogCandidate]:
        # GrabCAD renders the library with JavaScript and commonly returns 403 to server-side clients.
        # We deliberately do not bypass that protection. Only admin-approved seed URLs are attempted.
        from ..models import CatalogSeedURL

        rows = CatalogSeedURL.objects.filter(source=self.source, is_active=True).order_by("priority", "id")[:limit]
        output = []
        for row in rows:
            match = self.model_link_pattern.search(row.url)
            if match:
                output.append(CatalogCandidate(url=row.url, external_id=match.group(1)))
        return output

    def fetch_record(self, candidate, *, hydrate_files=False):
        record = super().fetch_record(candidate, hydrate_files=False)
        record["file_links"] = []
        record["commercial_use_allowed"] = False
        record["license_review_status"] = "blocked"
        record["blocked_reason"] = (
            "GrabCAD در 3DprintHub فقط مرجع داخلی مدیریت است؛ "
            "نمایش عمومی، فروش، بازنشر تصویر و ذخیره لینک دانلود غیرفعال است."
        )
        return record
