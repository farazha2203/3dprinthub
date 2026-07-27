from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse

from .base import MultiSourceCatalogAdapter
from .common import (
    CatalogCandidate,
    all_values,
    best_description,
    best_images,
    best_title,
    extract_external_id,
    extract_file_formats,
    extract_json_blobs,
    first_value,
    license_decision,
    link_discovery,
    meta_value,
    normalize_text,
    parse_duration_minutes,
    parse_html_document,
    parse_weight_grams,
    safe_int,
    unique_urls,
    robots_allowed,
)


class HTMLCatalogAdapter(MultiSourceCatalogAdapter):
    model_link_pattern: re.Pattern[str]
    id_patterns: tuple[str, ...] = ()
    sort_mapping: dict[str, str] = {}
    default_listing_template = ""

    def listing_url(self, *, page: int, sort_mode: str, limit: int) -> str:
        template = self.policy.discovery_url_template or self.default_listing_template
        if not template:
            raise ValueError("آدرس فهرست منبع تنظیم نشده است.")
        sort_value = self.sort_mapping.get(sort_mode, sort_mode)
        return template.format(page=page, sort=sort_value, limit=limit)

    def discover(self, *, limit: int, sort_mode: str) -> list[CatalogCandidate]:
        output: list[CatalogCandidate] = []
        seen: set[str] = set()
        max_pages = min(self.policy.max_pages or 100, max(1, (limit // max(1, self.policy.page_size)) + 10))
        for page in range(1, max_pages + 1):
            url = self.listing_url(page=page, sort_mode=sort_mode, limit=limit)
            self.assert_url_allowed(url)
            if self.source.respect_robots_txt and not robots_allowed(url, timeout=self.source.request_timeout_seconds):
                raise ValueError("طبق robots.txt اجازه دریافت فهرست این منبع وجود ندارد.")
            raw_html = self.client.fetch_text(url)
            candidates = link_discovery(raw_html, self.source.base_url, self.model_link_pattern, limit)
            # بسیاری از سایت‌های React/Next لینک مدل را داخل JSON اولیه صفحه قرار می‌دهند،
            # نه لزوماً در تگ <a>. این fallback فقط URL عمومی مدل را استخراج می‌کند.
            decoded_html = raw_html.replace("\\/", "/")
            for match in self.model_link_pattern.finditer(decoded_html):
                path = match.group(0)
                if not path.startswith("/"):
                    continue
                candidates.append(CatalogCandidate(url=urljoin(self.source.base_url, path), external_id=match.group(1)))
            before = len(output)
            for candidate in candidates:
                normalized = candidate.url.split("?", 1)[0].rstrip("/")
                if normalized in seen:
                    continue
                seen.add(normalized)
                output.append(CatalogCandidate(url=normalized, external_id=candidate.external_id))
                if len(output) >= limit:
                    return output
            if len(output) == before:
                break
        return output

    def metric_from(self, blobs: list[Any], raw_text: str, aliases: list[str], patterns: list[str]) -> int:
        raw = first_value(blobs, aliases, None)
        if raw not in (None, ""):
            return safe_int(raw)
        for pattern in patterns:
            match = re.search(pattern, raw_text, re.I)
            if match:
                return safe_int(match.group(1))
        return 0

    def source_category(self, blobs: list[Any], parser) -> str:
        value = first_value(blobs, ["category", "categoryName", "taxonomy", "section"], "")
        if isinstance(value, dict):
            value = value.get("name") or value.get("title") or ""
        if isinstance(value, list):
            value = " / ".join(normalize_text(item.get("name") if isinstance(item, dict) else item) for item in value)
        return normalize_text(value or meta_value(parser, "article:section"))

    def fetch_record(self, candidate: CatalogCandidate, *, hydrate_files: bool = False) -> dict[str, Any]:
        self.assert_url_allowed(candidate.url)
        if self.source.respect_robots_txt and not robots_allowed(candidate.url, timeout=self.source.request_timeout_seconds):
            raise ValueError("طبق robots.txt اجازه دریافت صفحه مدل وجود ندارد.")
        raw_html = self.client.fetch_text(candidate.url)
        parser = parse_html_document(raw_html)
        blobs = extract_json_blobs(raw_html)
        raw_text = " ".join(parser.text_chunks)

        title = best_title(parser, blobs) or candidate.summary.get("title") or candidate.external_id
        description = best_description(parser, blobs)
        images = best_images(parser, blobs, candidate.url)
        author = first_value(blobs, ["author", "creator", "designer", "username", "userName"], "")
        if isinstance(author, dict):
            author_name = normalize_text(author.get("name") or author.get("username") or author.get("displayName"))
            creator_url = normalize_text(author.get("url") or author.get("profileUrl"))
        else:
            author_name = normalize_text(author)
            creator_url = normalize_text(first_value(blobs, ["authorUrl", "creatorUrl", "profileUrl"], ""))
        license_name = normalize_text(first_value(blobs, ["license", "licenseName", "licenseType", "usageLicense"], ""))
        if isinstance(first_value(blobs, ["license"], ""), dict):
            license_obj = first_value(blobs, ["license"], {})
            license_name = normalize_text(license_obj.get("name") or license_obj.get("title") or license_name)
            license_url = normalize_text(license_obj.get("url") or license_obj.get("licenseUrl"))
        else:
            license_url = normalize_text(first_value(blobs, ["licenseUrl"], ""))

        file_values = all_values(blobs, ["files", "file", "fileName", "filename", "downloadUrl", "contentUrl"])
        file_links = unique_urls(all_values(blobs, ["downloadUrl", "contentUrl", "fileUrl", "url"]), candidate.url)
        file_links = [url for url in file_links if re.search(r"\.(?:stl|3mf|obj|step|stp|iges|igs|zip|rar|7z|gcode|amf|ply)(?:\?|$)", url, re.I)]
        if not hydrate_files:
            file_links = file_links[:20]
        file_formats = extract_file_formats([*file_values, *file_links, raw_text])

        weight_value = first_value(blobs, ["filamentWeight", "materialWeight", "weightGrams", "weight"], None)
        duration_value = first_value(blobs, ["printTime", "printingTime", "duration", "estimatedTime"], None)
        for prop_group in all_values(blobs, ["additionalProperty", "properties", "printProfile"]):
            rows = prop_group if isinstance(prop_group, list) else [prop_group]
            for prop in rows:
                if not isinstance(prop, dict):
                    continue
                prop_name = normalize_text(prop.get("name") or prop.get("key") or prop.get("label")).lower()
                prop_value = prop.get("value") or prop.get("content") or prop.get("displayValue")
                if not weight_value and any(token in prop_name for token in ("weight", "filament", "material")):
                    weight_value = prop_value
                if not duration_value and any(token in prop_name for token in ("time", "duration")):
                    duration_value = prop_value
        estimated_weight = parse_weight_grams(weight_value)
        estimated_minutes = parse_duration_minutes(duration_value)

        allowed, review_status, blocked_reason = license_decision(self.key, license_name, raw_text)
        source_category = self.source_category(blobs, parser)

        metrics = self.parse_metrics(blobs, raw_text)
        tags = first_value(blobs, ["keywords", "tags", "tagNames"], [])
        if isinstance(tags, list):
            tag_list = [normalize_text(item.get("name") if isinstance(item, dict) else item) for item in tags]
        else:
            tag_list = [normalize_text(item) for item in re.split(r"[,;|]", normalize_text(tags)) if normalize_text(item)]

        return {
            "source_url": candidate.url,
            "external_id": candidate.external_id or extract_external_id(candidate.url, self.id_patterns),
            "title": normalize_text(title)[:260],
            "short_description": normalize_text(description)[:500],
            "description": normalize_text(description),
            "author_name": author_name[:200],
            "creator_url": creator_url,
            "license_name": license_name[:200],
            "license_url": license_url,
            "tags": tag_list,
            "source_category": source_category,
            "images": images[:20],
            "file_links": file_links,
            "file_formats": file_formats,
            "estimated_weight_grams": estimated_weight,
            "estimated_print_minutes": estimated_minutes,
            "estimate_source": "source_profile" if estimated_weight or estimated_minutes else "",
            "commercial_use_allowed": allowed,
            "license_review_status": review_status,
            "blocked_reason": blocked_reason,
            "attribution_text": f"{title} — {author_name or self.source.name} — {self.source.name}",
            "metrics": metrics,
            "raw_payload": {"json_blobs": blobs[:10], "candidate_summary": candidate.summary},
        }

    def parse_metrics(self, blobs: list[Any], raw_text: str) -> dict[str, int | float | None]:
        return {
            "views_count": self.metric_from(blobs, raw_text, ["viewCount", "views", "view_count"], [r"([\d,.kmb]+)\s+views?"]),
            "likes_count": self.metric_from(blobs, raw_text, ["likeCount", "likes", "favoriteCount", "favorites"], [r"([\d,.kmb]+)\s+(?:likes?|favorites?)"]),
            "downloads_count": self.metric_from(blobs, raw_text, ["downloadCount", "downloads", "download_count"], [r"([\d,.kmb]+)\s+downloads?"]),
            "makes_count": self.metric_from(blobs, raw_text, ["makeCount", "makes", "printsCount", "printCount"], [r"([\d,.kmb]+)\s+(?:makes?|prints?)"]),
            "comments_count": self.metric_from(blobs, raw_text, ["commentCount", "comments"], [r"([\d,.kmb]+)\s+comments?"]),
            "rating": None,
        }
