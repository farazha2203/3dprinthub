from __future__ import annotations

import re

from .html_site import HTMLCatalogAdapter


class PrintablesAdapter(HTMLCatalogAdapter):
    key = "printables"
    allowed_domains = ("printables.com", "media.printables.com")
    model_link_pattern = re.compile(r"/model/(\d+)(?:[-/]|$)", re.I)
    id_patterns = (r"/model/(\d+)",)
    sort_mapping = {
        "downloads": "downloads",
        "likes": "likes",
        "views": "views",
        "trending": "trending",
        "newest": "newest",
    }
    default_listing_template = "https://www.printables.com/model?ordering={sort}&page={page}"
