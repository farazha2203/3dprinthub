from __future__ import annotations

import re
from urllib.error import HTTPError
from urllib.parse import urljoin

from .common import CatalogCandidate
from .html_site import HTMLCatalogAdapter
from ..makerworld_next_data import extract_record


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
    def fetch_record(self, candidate: CatalogCandidate, *, hydrate_files: bool = False) -> dict:
        self.assert_url_allowed(candidate.url)
        raw_html = self.client.fetch_text(candidate.url)
        try:
            record = extract_record(raw_html, candidate.url)
        except Exception:
            return super().fetch_record(candidate, hydrate_files=hydrate_files)

        license_data = record.get("license") or {}
        license_name = str(license_data.get("name") or license_data.get("title") or "")
        license_text = str(license_data.get("description") or "")
        lowered = (license_name + " " + license_text).lower()
        commercial_allowed = any(token in lowered for token in (
            "commercial use allowed", "commercial use permitted", "cc0", "public domain", "cc by",
        )) and not any(token in lowered for token in (
            "non-commercial", "noncommercial", "no commercial", "not for commercial",
        ))
        review_status = "allowed" if commercial_allowed else "manual"
        blocked_reason = "" if commercial_allowed else "مجوز MakerWorld نیازمند بررسی و تأیید اپراتور است."
        creator = record.get("creator") or {}
        metrics = record.get("metrics") or {}
        instances = record.get("instances") or []
        first_profile = instances[0] if instances else {}
        image_rows = record.get("images") or []
        image_urls = [row.get("url") for row in image_rows if isinstance(row, dict) and row.get("url")]
        technical_specs = {
            "model_id": record.get("model_id"),
            "default_instance_id": record.get("default_instance_id"),
            "categories": record.get("categories") or [],
            "instances": instances,
            "image_records": image_rows,
            "is_printable": record.get("is_printable"),
            "is_official": record.get("is_official"),
            "is_exclusive": record.get("is_exclusive"),
        }
        return {
            "source_url": candidate.url,
            "external_id": record.get("external_id") or candidate.external_id,
            "title": record.get("title") or candidate.external_id,
            "short_description": (record.get("description_text") or "")[:500],
            "description": record.get("description_text") or "",
            "author_name": creator.get("name") or "",
            "creator_url": (f"https://makerworld.com/en/@{creator.get('name')}" if creator.get("name") else ""),
            "license_name": license_name,
            "license_url": candidate.url,
            "license_text": license_text,
            "tags": record.get("tags") or [],
            "source_category": " / ".join(record.get("categories") or []),
            "images": image_urls,
            "image_records": image_rows,
            "file_links": [],
            "file_formats": ["3MF"] if record.get("is_printable") else [],
            "estimated_weight_grams": first_profile.get("weight"),
            "estimated_print_minutes": first_profile.get("print_time"),
            "estimate_source": "makerworld_profile" if first_profile else "",
            "commercial_use_allowed": commercial_allowed,
            "license_review_status": review_status,
            "blocked_reason": blocked_reason,
            "attribution_text": f"{record.get('title') or ''} — {creator.get('name') or 'MakerWorld'} — MakerWorld",
            "metrics": {
                "views_count": 0,
                "likes_count": metrics.get("likes") or 0,
                "downloads_count": metrics.get("downloads") or 0,
                "makes_count": metrics.get("prints") or 0,
                "comments_count": metrics.get("comments") or 0,
                "rating": None,
            },
            "technical_specs": technical_specs,
            "raw_payload": record,
        }
