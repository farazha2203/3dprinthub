from __future__ import annotations

import re
from urllib.error import HTTPError
from urllib.parse import urljoin

from .common import CatalogCandidate
from .html_site import HTMLCatalogAdapter


class MakerWorldAdapter(HTMLCatalogAdapter):
    key = "makerworld"
    allowed_domains = ("makerworld.com", "makerworld.bblmw.com")
    model_link_pattern = re.compile(r"/(?:[a-z]{2}/)?models/(\d+)(?:[-/?#]|$)", re.I)
    id_patterns = (r"/models/(\d+)",)
    sort_mapping = {
        "downloads": "downloadCount",
        "likes": "likeCount",
        "views": "downloadCount",
        "trending": "hotScore",
        "newest": "createTime",
    }
    default_listing_template = "https://makerworld.com/en/3d-models?orderBy={sort}&page={page}"

    def _seed_candidates(self, limit: int) -> list[CatalogCandidate]:
        from ..models import CatalogSeedURL

        rows = CatalogSeedURL.objects.filter(source=self.source, is_active=True).order_by("priority", "id")[:limit]
        return [
            CatalogCandidate(url=row.url, external_id=self.model_link_pattern.search(row.url).group(1))
            for row in rows
            if self.model_link_pattern.search(row.url)
        ]

    def _sitemap_candidates(self, limit: int) -> list[CatalogCandidate]:
        root_urls = [
            "https://makerworld.com/sitemap.xml",
            "https://makerworld.com/sitemaps/index.xml",
        ]
        sitemap_urls: list[str] = []
        model_urls: list[str] = []
        seen_sitemaps: set[str] = set()

        for root in root_urls:
            try:
                text = self.client.fetch_text(root)
            except Exception:
                continue
            for url in re.findall(r"https://makerworld\.com/[^\s<\"']+", text, flags=re.I):
                clean = url.replace("&amp;", "&")
                if "sitemap" in clean and clean.endswith((".xml", ".xml.gz")):
                    sitemap_urls.append(clean)
                elif self.model_link_pattern.search(clean):
                    model_urls.append(clean)

        for sitemap_url in sitemap_urls[:20]:
            if sitemap_url in seen_sitemaps or sitemap_url.endswith(".gz"):
                continue
            seen_sitemaps.add(sitemap_url)
            try:
                text = self.client.fetch_text(sitemap_url)
            except Exception:
                continue
            for url in re.findall(r"https://makerworld\.com/[^\s<\"']+", text, flags=re.I):
                if self.model_link_pattern.search(url):
                    model_urls.append(url.replace("&amp;", "&"))
                    if len(model_urls) >= limit:
                        break
            if len(model_urls) >= limit:
                break

        output: list[CatalogCandidate] = []
        seen: set[str] = set()
        for url in model_urls:
            match = self.model_link_pattern.search(url)
            if not match:
                continue
            normalized = url.split("?", 1)[0].rstrip("/")
            if normalized in seen:
                continue
            seen.add(normalized)
            output.append(CatalogCandidate(url=normalized, external_id=match.group(1)))
            if len(output) >= limit:
                break
        return output

    def discover(self, *, limit: int, sort_mode: str) -> list[CatalogCandidate]:
        errors = []
        try:
            records = super().discover(limit=limit, sort_mode=sort_mode)
            if records:
                return records
        except HTTPError as exc:
            errors.append(f"listing HTTP {exc.code}")
        except Exception as exc:
            errors.append(f"listing {type(exc).__name__}: {exc}")

        records = self._sitemap_candidates(limit)
        if records:
            return records

        records = self._seed_candidates(limit)
        if records:
            return records

        self.last_discovery_errors = errors
        return []
