from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from .base import MultiSourceCatalogAdapter
from .common import (
    CatalogCandidate,
    extract_file_formats,
    flatten_json_lists,
    license_decision,
    normalize_text,
    parse_duration_minutes,
    parse_weight_grams,
    safe_int,
    unique_urls,
)


class ThingiverseAdapter(MultiSourceCatalogAdapter):
    key = "thingiverse"
    allowed_domains = ("thingiverse.com", "api.thingiverse.com")

    def _headers(self) -> dict[str, str]:
        token = self.env_token()
        if not token:
            raise ValueError(
                "توکن رسمی Thingiverse تنظیم نشده است. متغیر محیطی "
                f"{self.policy.api_token_env or 'THINGIVERSE_ACCESS_TOKEN'} را وارد کنید."
            )
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    def _api_url(self, path: str, **query: Any) -> str:
        base = (self.policy.api_base_url or "https://api.thingiverse.com").rstrip("/")
        url = base + "/" + path.lstrip("/")
        if query:
            url += "?" + urlencode({key: value for key, value in query.items() if value not in (None, "")})
        self.assert_url_allowed(url)
        return url

    def discover(self, *, limit: int, sort_mode: str) -> list[CatalogCandidate]:
        output: list[CatalogCandidate] = []
        page_size = min(max(1, self.policy.page_size or 20), 50)
        max_pages = min(self.policy.max_pages or 100, (limit // page_size) + 3)
        headers = self._headers()
        endpoint = {
            "newest": "newest",
            "trending": "popular",
            "likes": "popular",
            "views": "popular",
            "downloads": "popular",
        }.get(sort_mode, "popular")
        for page in range(1, max_pages + 1):
            payload = self.client.fetch_json(
                self._api_url(endpoint, page=page, per_page=page_size),
                extra_headers=headers,
            )
            rows = flatten_json_lists(payload)
            if not rows:
                break
            before = len(output)
            for row in rows:
                if not isinstance(row, dict):
                    continue
                thing_id = str(row.get("id") or "").strip()
                if not thing_id:
                    continue
                public_url = row.get("public_url") or row.get("url") or f"https://www.thingiverse.com/thing:{thing_id}"
                output.append(CatalogCandidate(url=public_url, external_id=thing_id, summary=row))
                if len(output) >= limit:
                    return output
            if len(output) == before:
                break
        return output

    def fetch_record(self, candidate: CatalogCandidate, *, hydrate_files: bool = False) -> dict[str, Any]:
        headers = self._headers()
        thing_id = candidate.external_id
        detail = self.client.fetch_json(self._api_url(f"things/{thing_id}"), extra_headers=headers)
        images_payload = self.client.fetch_json(self._api_url(f"things/{thing_id}/images"), extra_headers=headers)
        files_payload: Any = []
        if hydrate_files or self.policy.store_download_links:
            files_payload = self.client.fetch_json(self._api_url(f"things/{thing_id}/files"), extra_headers=headers)

        image_rows = flatten_json_lists(images_payload) or (images_payload if isinstance(images_payload, list) else [])
        image_urls: list[str] = []
        for row in image_rows:
            if not isinstance(row, dict):
                continue
            sizes = row.get("sizes") or []
            candidates = []
            if isinstance(sizes, list):
                candidates.extend(size.get("url") for size in sizes if isinstance(size, dict))
            candidates.extend([row.get("url"), row.get("public_url")])
            image_urls.extend(unique_urls(candidates, candidate.url))

        file_rows = flatten_json_lists(files_payload) or (files_payload if isinstance(files_payload, list) else [])
        file_links: list[str] = []
        file_names: list[str] = []
        for row in file_rows:
            if not isinstance(row, dict):
                continue
            file_names.append(normalize_text(row.get("name") or row.get("filename")))
            link = row.get("download_url") or row.get("public_url") or row.get("url")
            if isinstance(link, str) and link.startswith(("http://", "https://")):
                file_links.append(link)

        license_name = normalize_text(detail.get("license") or detail.get("license_name"))
        if isinstance(detail.get("license"), dict):
            license_name = normalize_text(detail["license"].get("name") or detail["license"].get("label"))
        allowed, review_status, blocked_reason = license_decision(self.key, license_name, normalize_text(detail))
        tags = detail.get("tags") or []
        tag_list = [normalize_text(item.get("name") if isinstance(item, dict) else item) for item in tags]
        creator = detail.get("creator") or {}

        return {
            "source_url": detail.get("public_url") or candidate.url,
            "external_id": thing_id,
            "title": normalize_text(detail.get("name") or candidate.summary.get("name") or thing_id)[:260],
            "short_description": normalize_text(detail.get("description") or detail.get("instructions"))[:500],
            "description": normalize_text(detail.get("description") or detail.get("instructions")),
            "author_name": normalize_text(creator.get("name") or creator.get("first_name") or creator.get("username"))[:200],
            "creator_url": normalize_text(creator.get("public_url") or creator.get("url")),
            "license_name": license_name[:200],
            "license_url": normalize_text(detail.get("license_url")),
            "tags": tag_list,
            "source_category": normalize_text(detail.get("category") or detail.get("type_name")),
            "images": list(dict.fromkeys(image_urls))[:20],
            "file_links": list(dict.fromkeys(file_links)) if self.policy.store_download_links else [],
            "file_formats": extract_file_formats(file_names),
            "estimated_weight_grams": parse_weight_grams(detail.get("weight") or detail.get("filament_weight")),
            "estimated_print_minutes": parse_duration_minutes(detail.get("print_time") or detail.get("duration")),
            "estimate_source": "thingiverse_api" if detail.get("weight") or detail.get("print_time") else "",
            "commercial_use_allowed": allowed,
            "license_review_status": review_status,
            "blocked_reason": blocked_reason,
            "attribution_text": f"{detail.get('name', '')} — {creator.get('name') or creator.get('username') or 'Thingiverse creator'} — Thingiverse",
            "metrics": {
                "views_count": safe_int(detail.get("view_count") or detail.get("views")),
                "likes_count": safe_int(detail.get("like_count") or detail.get("likes") or detail.get("collect_count")),
                "downloads_count": safe_int(detail.get("download_count") or detail.get("downloads")),
                "makes_count": safe_int(detail.get("make_count") or detail.get("makes")),
                "comments_count": safe_int(detail.get("comment_count") or detail.get("comments")),
                "rating": detail.get("rating"),
            },
            "raw_payload": {"detail": detail, "images": image_rows[:20], "files": file_rows[:50]},
        }
