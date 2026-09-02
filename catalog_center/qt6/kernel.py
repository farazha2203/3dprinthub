from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from typing import Any, Callable, TypeVar
from urllib.parse import quote_plus, urlsplit

from app import phase49_3c_image_pipeline as image_pipeline
from app.db import utc_now
from app.phase49_3i38_crawl_ledger_stage_ai import (
    reject_and_purge_product,
    restore_rejected_identity,
)
from app.phase49_3i36_stage_finalization import (
    LOCK_COLUMN,
    filter_locked_updates,
    is_stage_locked,
    stage_locks,
)

from .parity_core import (
    CategoryCore,
    CommerceCore,
    ConnectionCore,
    FilamentParityCore,
    ProviderCore,
    StageCore,
    ensure_qt_parity_schema,
)

T = TypeVar("T")


class CoreRegistry:
    """Long-lived object registry for the Qt application runtime."""

    def __init__(self) -> None:
        self._items: dict[str, object] = {}

    def register(self, name: str, core: object) -> object:
        key = str(name or "").strip()
        if not key:
            raise ValueError("core name is required")
        if key in self._items:
            raise KeyError(f"core already registered: {key}")
        self._items[key] = core
        return core

    def require(self, name: str, expected_type: type[T] | None = None) -> T | object:
        key = str(name or "").strip()
        if key not in self._items:
            raise KeyError(f"core is not registered: {key}")
        core = self._items[key]
        if expected_type is not None and not isinstance(core, expected_type):
            raise TypeError(f"core {key} is not {expected_type.__name__}")
        return core

    def names(self) -> tuple[str, ...]:
        return tuple(self._items)


class ProductCore:
    """Product read/write boundary used by every Qt product surface."""

    SAFE_OPERATOR_FIELDS = frozenset({
        "title_fa",
        "local_category_slug",
        "custom_notes",
    })

    def __init__(self, db) -> None:
        self.db = db

    def list(self, *, search: str = "", filter_name: str = "all") -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.products(filter_name=filter_name, search=search)
        ]

    def count(self, *, search: str = "", filter_name: str = "all") -> int:
        return int(
            self.db.product_count(
                filter_name=filter_name,
                search=search,
            )
        )

    def list_page(
        self,
        *,
        search: str = "",
        filter_name: str = "all",
        sort_key: str = "priority",
        descending: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.product_page(
                filter_name=filter_name,
                search=search,
                sort_key=sort_key,
                descending=descending,
                limit=limit,
                offset=offset,
            )
        ]

    def get(self, product_id: int) -> dict[str, Any] | None:
        row = self.db.product(int(product_id))
        return dict(row) if row is not None else None

    def is_stage_locked(self, product_id: int, stage: str) -> bool:
        row = self.db.product(int(product_id))
        return bool(row is not None and is_stage_locked(row, stage))

    def unlock_stage_for_edit(self, product_id: int, stage: str) -> dict[str, Any]:
        """Compatibility helper retained for 42B1 callers."""
        stage = str(stage or "")
        if stage != "quick":
            raise RuntimeError("برای این مرحله از StageCore مشترک استفاده کن.")
        before_row = self.db.product(int(product_id))
        if before_row is None:
            raise RuntimeError(f"Product {product_id} not found")
        locks = stage_locks(before_row)
        if stage not in locks:
            return dict(before_row)
        locks.pop(stage, None)
        before = dict(before_row)
        self.db.update_product(
            int(product_id),
            {LOCK_COLUMN: json.dumps(locks, ensure_ascii=False)},
        )
        after = self.get(product_id) or {}
        try:
            self.db.save_history(
                int(product_id),
                "qt_stage_unlocked",
                before,
                after,
                "Phase49.3I.42 quick stage opened for edit",
            )
        except Exception:
            pass
        return after

    def update_operator_fields(
        self,
        product_id: int,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        requested = {
            key: value
            for key, value in dict(values or {}).items()
            if key in self.SAFE_OPERATOR_FIELDS
        }
        if not requested:
            return self.get(product_id) or {}

        before_row = self.db.product(int(product_id))
        if before_row is None:
            raise RuntimeError(f"Product {product_id} not found")

        allowed, blocked = filter_locked_updates(before_row, requested)
        if blocked:
            raise RuntimeError(
                "مرحله مربوط به این فیلدها ثبت نهایی شده است: "
                + "، ".join(blocked)
                + "؛ ابتدا مرحله را برای اصلاح باز کن."
            )
        if not allowed:
            return dict(before_row)

        before = dict(before_row)
        self.db.update_product(int(product_id), allowed)
        after = self.get(product_id) or {}
        try:
            self.db.save_history(
                int(product_id),
                "qt_operator_edit",
                before,
                after,
                "Phase49.3I.42 Qt operator edit",
            )
        except Exception:
            pass
        return after


    def archive_many(self, product_ids: list[int]) -> int:
        count = 0
        for product_id in sorted({int(value) for value in product_ids or []}):
            before = self.db.product(product_id)
            if before is None:
                continue
            self.db.archive_product(
                product_id,
                "Qt bulk archive",
            )
            after = self.db.product(product_id)
            if after is not None and str(after["workflow_status"] or "") == "archived":
                count += 1
        return count

    def remove_many(self, product_ids: list[int]) -> int:
        """Reject Products while retaining only URL/title/one small thumbnail."""
        count = 0
        app = SimpleNamespace(
            db=self.db,
            DATA=Path(self.db.path).resolve().parent,
        )
        for product_id in sorted({int(value) for value in product_ids or []}):
            before = self.db.product(product_id)
            if before is None:
                continue
            reject_and_purge_product(
                app,
                product_id,
                "Qt owner reject — keep lightweight tombstone only",
            )
            after = self.db.product(product_id)
            if after is not None and int(after["is_blocked"] or 0):
                count += 1
        return count

    def restore_many(self, product_ids: list[int]) -> int:
        count = 0
        for product_id in sorted({int(value) for value in product_ids or []}):
            row = self.db.product(product_id)
            if row is None:
                continue
            if int(row["is_blocked"] or 0):
                if str(row["source_state"] or "") == "rejected":
                    restore_rejected_identity(self.db, product_id)
                self.db.restore_product(product_id)
                count += 1
            elif str(row["workflow_status"] or "") == "archived":
                self.db.restore_archived_product(product_id)
                count += 1
        return count


class ImageCore:
    """Single image authority shared by Product cards, image grid and slider."""

    def __init__(self, db) -> None:
        self.db = db

    @staticmethod
    def _json_list(value: Any) -> list:
        if isinstance(value, list):
            return list(value)
        try:
            parsed = json.loads(value or "[]")
        except Exception:
            return []
        return list(parsed) if isinstance(parsed, list) else []

    def urls(self, row: dict[str, Any] | Any) -> list[str]:
        data = dict(row) if not isinstance(row, dict) else row
        output: list[str] = []
        primary = str(data.get("primary_image_url") or "").strip()
        if primary:
            output.append(primary)
        for field in ("selected_images_json", "images_json"):
            for raw in self._json_list(data.get(field)):
                if isinstance(raw, dict):
                    url = str(
                        raw.get("url")
                        or raw.get("source_url")
                        or ""
                    ).strip()
                else:
                    url = str(raw or "").strip()
                if url and url not in output:
                    output.append(url)
        return output

    def local_path_for_url(
        self,
        row: dict[str, Any] | Any,
        url: str,
    ) -> str:
        data = dict(row) if not isinstance(row, dict) else row
        # Final SEO WebP is the operator/site-facing image. Source/cache is only
        # a fallback when finalization has not happened yet.
        path = image_pipeline.strict_local_image(data, url)
        if not path:
            path = image_pipeline.strict_source_local_image(data, url)
        return str(path or "")

    def _legacy_local_candidates(
        self,
        row: dict[str, Any] | Any,
    ) -> list[str]:
        """Read-only fallback for mature Products whose URL mapping predates Qt.

        The fallback never rewrites Product/image metadata. It is confined to
        the Product's own local_dir and prefers finalized SEO WebP files before
        the original image cache.
        """
        data = dict(row) if not isinstance(row, dict) else row
        raw_root = str(data.get("local_dir") or "").strip()
        if not raw_root:
            return []
        try:
            local_dir = Path(raw_root).resolve()
        except Exception:
            return []
        if not local_dir.is_dir():
            return []

        allowed = {
            ".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif",
            ".bmp", ".tif", ".tiff",
        }
        output: list[str] = []
        for candidate_root in (
            local_dir / "seo_images",
            local_dir / "images",
        ):
            if not candidate_root.is_dir():
                continue
            try:
                children = sorted(
                    candidate_root.iterdir(),
                    key=lambda item: item.name.casefold(),
                )
            except Exception:
                continue
            for candidate in children:
                if not candidate.is_file() or candidate.suffix.lower() not in allowed:
                    continue
                try:
                    resolved = candidate.resolve()
                except Exception:
                    continue
                if resolved != local_dir and local_dir not in resolved.parents:
                    continue
                value = str(resolved)
                if value not in output:
                    output.append(value)
        return output

    def preferred_local_path(self, row: dict[str, Any] | Any) -> str:
        data = dict(row) if not isinstance(row, dict) else row
        rejected = str(data.get("rejected_thumbnail_path") or "").strip()
        if rejected:
            try:
                rejected_path = Path(rejected)
                if rejected_path.is_file():
                    return str(rejected_path)
            except Exception:
                pass
        for url in self.urls(data):
            path = self.local_path_for_url(row, url)
            if path:
                return path
        legacy = self._legacy_local_candidates(row)
        return legacy[0] if legacy else ""

    def image_count(self, row: dict[str, Any] | Any) -> int:
        data = dict(row) if not isinstance(row, dict) else row
        urls = self.urls(data)
        if urls:
            return len(urls)
        rejected = str(data.get("rejected_thumbnail_path") or "").strip()
        if rejected and Path(rejected).is_file():
            return 1
        return len(self._legacy_local_candidates(data))

    def renumber(self, product_id: int) -> dict[str, Any]:
        """Rebuild final SEO files as -01/-02/... and remove stale derivatives."""
        product_id = int(product_id)
        row = self.db.product(product_id)
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        data = dict(row)
        local_dir = Path(str(data.get("local_dir") or "")).resolve()
        if not str(data.get("local_dir") or "").strip() or not local_dir.is_dir():
            raise RuntimeError("پوشه محلی محصول پیدا نشد.")

        seo_dir = (local_dir / "seo_images").resolve()
        before = {
            str(Path(str(item.get("final_local_file") or "")).resolve())
            for item in self._json_list(data.get("image_metadata_json"))
            if isinstance(item, dict) and str(item.get("final_local_file") or "").strip()
        }
        result = dict(image_pipeline.finalize_selected_images(self.db, product_id) or {})
        refreshed = dict(self.db.product(product_id) or {})
        after = {
            str(Path(str(item.get("final_local_file") or "")).resolve())
            for item in self._json_list(refreshed.get("image_metadata_json"))
            if isinstance(item, dict) and str(item.get("final_local_file") or "").strip()
        }

        removed = 0
        if seo_dir.is_dir():
            candidates = set(before)
            for item in seo_dir.iterdir():
                if item.is_file() and item.suffix.lower() == ".webp":
                    candidates.add(str(item.resolve()))
            for raw in candidates:
                path = Path(raw)
                try:
                    resolved = path.resolve()
                except Exception:
                    continue
                if str(resolved) in after:
                    continue
                if resolved.parent != seo_dir:
                    continue
                try:
                    resolved.unlink(missing_ok=True)
                    removed += 1
                except Exception:
                    continue
        result["stale_seo_files_removed"] = removed
        return result

    def local_items(self, product_id: int) -> list[dict[str, Any]]:
        row = self.db.product(int(product_id))
        if row is None:
            return []
        data = dict(row)

        primary = str(data.get("primary_image_url") or "").strip()
        slider_image = str(
            data.get("homepage_slider_image_url") or ""
        ).strip()
        selected_urls: list[str] = []
        for raw in self._json_list(data.get("selected_images_json")):
            if isinstance(raw, dict):
                url = str(
                    raw.get("url")
                    or raw.get("source_url")
                    or ""
                ).strip()
            else:
                url = str(raw or "").strip()
            if url:
                selected_urls.append(url)
        selected = set(selected_urls)

        alts = [
            str(item or "").strip()
            for item in self._json_list(
                data.get("image_alt_texts_json")
            )
        ]
        raw_meta = self._json_list(
            data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
        )
        metadata = [
            dict(item)
            for item in raw_meta
            if isinstance(item, dict)
        ]

        output: list[dict[str, Any]] = []
        for index, url in enumerate(self.urls(data), 1):
            path = self.local_path_for_url(data, url)
            file_path = Path(path) if path else None
            width = height = file_bytes = 0
            image_format = ""
            if file_path is not None and file_path.is_file():
                try:
                    from PIL import Image

                    with Image.open(file_path) as image:
                        width = int(image.width)
                        height = int(image.height)
                        image_format = str(image.format or "")
                except Exception:
                    pass
                try:
                    file_bytes = int(file_path.stat().st_size)
                except Exception:
                    pass

            meta = next(
                (
                    item
                    for item in metadata
                    if str(
                        item.get("source_url")
                        or item.get("url")
                        or ""
                    ) == url
                ),
                {},
            )
            alt = ""
            if url in selected:
                try:
                    alt = alts[selected_urls.index(url)]
                except Exception:
                    alt = ""
            if not alt:
                alt = str(meta.get("alt_text") or "")

            output.append(
                {
                    "slot": index,
                    "url": url,
                    "path": str(file_path or ""),
                    "filename": (
                        file_path.name
                        if file_path is not None
                        else str(meta.get("original_filename") or "")
                    ),
                    "downloaded": bool(
                        file_path is not None
                        and file_path.is_file()
                    ),
                    "primary": url == primary,
                    "slider": url == slider_image,
                    "selected": url in selected,
                    "width": width,
                    "height": height,
                    "format": image_format,
                    "bytes": file_bytes,
                    "alt_text": alt,
                    "seo_title": str(meta.get("title") or ""),
                    "caption": str(meta.get("caption") or ""),
                    "keywords": (
                        list(meta.get("keywords") or [])
                        if isinstance(meta.get("keywords"), list)
                        else []
                    ),
                    "planned_filename": str(
                        meta.get("seo_filename")
                        or meta.get("planned_filename")
                        or ""
                    ),
                    "metadata": meta,
                }
            )
        return output

    def _assert_images_editable(self, product_id: int):
        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        if is_stage_locked(row, "images"):
            raise RuntimeError(
                "مرحله تصاویر ثبت نهایی شده است؛ ابتدا «اصلاح مرحله» را بزن."
            )
        return row

    def remove_urls(
        self,
        product_id: int,
        urls: list[str],
    ) -> dict[str, Any]:
        row = self._assert_images_editable(product_id)
        data = dict(row)
        remove = {
            str(value or "").strip()
            for value in urls or []
            if str(value or "").strip()
        }
        all_urls = [
            url
            for url in self.urls(data)
            if url not in remove
        ]

        old_selected = [
            str(item or "").strip()
            for item in self._json_list(
                data.get("selected_images_json")
            )
            if str(item or "").strip()
        ]
        old_alts = [
            str(item or "").strip()
            for item in self._json_list(
                data.get("image_alt_texts_json")
            )
        ]
        alt_map = {
            url: (
                old_alts[index]
                if index < len(old_alts)
                else ""
            )
            for index, url in enumerate(old_selected)
        }
        selected = [
            url
            for url in old_selected
            if url not in remove
        ]
        primary = str(data.get("primary_image_url") or "")
        if primary in remove:
            primary = selected[0] if selected else (
                all_urls[0] if all_urls else ""
            )

        metadata = [
            item
            for item in self._json_list(
                data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
            )
            if (
                isinstance(item, dict)
                and str(item.get("source_url") or "") not in remove
            )
        ]
        values = {
            "images_json": json.dumps(
                all_urls,
                ensure_ascii=False,
            ),
            "selected_images_json": json.dumps(
                selected,
                ensure_ascii=False,
            ),
            "primary_image_url": primary,
            "image_alt_texts_json": json.dumps(
                [alt_map.get(url, "") for url in selected],
                ensure_ascii=False,
            ),
            image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(
                metadata,
                ensure_ascii=False,
            ),
        }
        self.db.update_product(int(product_id), values)
        return dict(self.db.product(int(product_id)))

    @staticmethod
    def _safe_seo_filename(value: str) -> str:
        raw = str(value or "").strip().replace("\\", "-").replace("/", "-")
        raw = raw.strip(". ")
        if not raw:
            return ""
        if not raw.lower().endswith(".webp"):
            raw += ".webp"
        return raw[:180]

    def update_metadata(
        self,
        product_id: int,
        urls: list[str],
        values: dict[str, Any],
    ) -> dict[str, Any]:
        row = self._assert_images_editable(product_id)
        data = dict(row)
        targets = {
            str(url or "").strip()
            for url in urls or []
            if str(url or "").strip()
        }
        if not targets:
            raise ValueError("حداقل یک تصویر انتخاب کن.")

        existing = [
            dict(item)
            for item in self._json_list(
                data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
            )
            if isinstance(item, dict)
        ]
        by_url = {
            str(item.get("source_url") or ""): item
            for item in existing
            if item.get("source_url")
        }

        allowed = {
            "alt_text",
            "title",
            "caption",
            "keywords",
            "seo_filename",
        }
        for url in targets:
            item = by_url.get(url)
            if item is None:
                item = {"source_url": url}
                existing.append(item)
                by_url[url] = item
            changed: set[str] = set(
                item.get("_operator_override_fields") or []
            )
            for key, value in dict(values or {}).items():
                if key not in allowed or value is None:
                    continue
                if key == "keywords":
                    if isinstance(value, str):
                        value = [
                            token.strip().lstrip("#")
                            for token in value.replace(",", "\n").splitlines()
                            if token.strip()
                        ]
                    value = [
                        str(token or "").strip().lstrip("#")[:80]
                        for token in (value or [])
                        if str(token or "").strip()
                    ][:16]
                elif key == "seo_filename":
                    value = self._safe_seo_filename(str(value or ""))
                else:
                    value = str(value or "").strip()
                item[key] = value
                changed.add(key)
            if changed:
                item["_operator_override_fields"] = sorted(changed)

        selected = [
            str(item or "").strip()
            for item in self._json_list(
                data.get("selected_images_json")
            )
            if str(item or "").strip()
        ]
        alt_map = {
            url: str(
                by_url.get(url, {}).get("alt_text") or ""
            )
            for url in selected
        }
        self.db.update_product(
            int(product_id),
            {
                image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(
                    existing,
                    ensure_ascii=False,
                ),
                "image_alt_texts_json": json.dumps(
                    [alt_map.get(url, "") for url in selected],
                    ensure_ascii=False,
                ),
            },
        )
        image_pipeline.finalize_selected_images(
            self.db,
            int(product_id),
        )
        return dict(self.db.product(int(product_id)))

    def capture_source_screenshot(self, product_id: int) -> str:
        self._assert_images_editable(product_id)
        from app.phase49_3i33_ai_core import capture_source_screenshot

        proxy = SimpleNamespace(
            db=self.db,
            DATA=Path(self.db.path).parent,
        )
        return str(
            capture_source_screenshot(
                proxy,
                int(product_id),
            )
        )

    def finalize(self, product_id: int) -> dict[str, Any]:
        return dict(
            image_pipeline.finalize_selected_images(
                self.db,
                int(product_id),
            )
            or {}
        )


class AcquisitionCore:
    """Qt adapter over mature discovery/collection modules."""

    def __init__(self, db) -> None:
        self.db = db
        self._stop_requested = False

    def sources(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.sources()
            if int(row["enabled"] or 0)
        ]

    def source_details(self, source_code: str) -> dict[str, Any]:
        row = self.db.source(str(source_code or ""))
        return dict(row) if row is not None else {}

    def default_listing_url(
        self,
        source_code: str,
        query: str = "",
    ) -> str:
        row = self.db.source(str(source_code or ""))
        if row is None:
            return ""
        data = dict(row)
        try:
            urls = json.loads(
                data.get("listing_urls_json") or "[]"
            )
        except Exception:
            urls = []
        if not isinstance(urls, list) or not urls:
            return ""
        template = str(urls[0] or "").strip()
        if not template:
            return ""
        try:
            return template.format(
                query=quote_plus(
                    str(query or "3d print")
                ),
                page=1,
            )
        except Exception:
            return template

    def detect_source_for_url(self, url: str) -> str:
        target = str(url or "").strip()
        if not target.startswith(("http://", "https://")):
            return ""
        host = urlsplit(target).netloc.casefold().split(":", 1)[0]
        if not host:
            return ""
        for raw in self.sources():
            source = dict(raw)
            code = str(source.get("code") or "").strip()
            try:
                listings = json.loads(str(source.get("listing_urls_json") or "[]"))
            except Exception:
                listings = []
            for listing in listings if isinstance(listings, list) else []:
                listing_host = urlsplit(str(listing or "")).netloc.casefold().split(":", 1)[0]
                if listing_host and (
                    host == listing_host
                    or host.endswith("." + listing_host)
                    or listing_host.endswith("." + host)
                ):
                    return code
            compact_host = host.replace("-", "").replace("_", "")
            compact_code = code.casefold().replace("-", "").replace("_", "")
            if compact_code and compact_code in compact_host:
                return code
        return ""

    def resolve_listing_url(
        self,
        source_code: str,
        *,
        operator_mode: str,
        explicit_url: str = "",
        query: str = "",
    ) -> str:
        explicit = str(explicit_url or "").strip()
        if explicit:
            return explicit
        mode = str(operator_mode or "search")
        if mode in {"category", "site_crawl"}:
            raise ValueError(
                "برای Category/Site Crawl لینک شروع را وارد کن."
            )
        default = self.default_listing_url(
            source_code,
            query=query,
        )
        if not default:
            raise ValueError(
                "برای این Source لینک Listing پیش‌فرض ثبت نشده است."
            )
        return default

    def queue_items(
        self,
        source_code: str = "",
        limit: int = 5000,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.discovered_items(
                str(source_code or ""),
                limit=int(limit),
            )
        ]

    def queue_count(
        self,
        source_code: str = "",
        status: str = "all",
    ) -> int:
        return int(
            self.db.discovered_count(
                str(source_code or ""),
                str(status or "all"),
            )
        )

    def queue_page(
        self,
        source_code: str = "",
        status: str = "all",
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.discovered_items_page(
                str(source_code or ""),
                str(status or "all"),
                limit=int(limit),
                offset=int(offset),
            )
        ]

    def reject_queue_items(self, row_ids: list[int]) -> int:
        return int(
            self.db.set_discovered_status(
                row_ids,
                "rejected",
                "operator rejected from Qt queue browser",
            )
        )

    def restore_queue_items(self, row_ids: list[int]) -> int:
        return int(
            self.db.set_discovered_status(
                row_ids,
                "new",
                "",
            )
        )

    def mark_queue_collected(self, row_ids: list[int]) -> int:
        return int(
            self.db.set_discovered_status(
                row_ids,
                "collected",
                "",
            )
        )

    def mark_queue_failed(self, row_ids: list[int], error: str) -> int:
        return int(
            self.db.set_discovered_status(
                row_ids,
                "failed",
                str(error or ""),
            )
        )

    def queue_counts(self, source_code: str = "") -> dict[str, int]:
        return dict(self.db.queue_counts(str(source_code or "")))

    def recent_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.runs(limit=int(limit))
        ]

    def request_stop(self) -> None:
        self._stop_requested = True

    def reset_stop(self) -> None:
        self._stop_requested = False

    def should_stop(self) -> bool:
        return bool(self._stop_requested)

    def reset_failed(self, source_code: str = "") -> int:
        return int(
            self.db.reset_failed_urls(str(source_code or ""))
        )

    def run_batch(
        self,
        *,
        source_code: str,
        listing_url: str,
        requested: int = 100,
        image_limit: int = 5,
        include_failed: bool = False,
        strategy: str = "hybrid",
        operator_mode: str = "search",
        collection_method: str = "rich",
        download_images: bool = True,
        download_files: bool = False,
        same_domain_only: bool = True,
        progress=None,
    ) -> dict[str, Any]:
        from .acquisition_runtime import run_batch

        self.reset_stop()
        return run_batch(
            self.db,
            source_code=source_code,
            listing_url=listing_url,
            requested=requested,
            image_limit=image_limit,
            include_failed=include_failed,
            strategy=strategy,
            operator_mode=operator_mode,
            collection_method=collection_method,
            download_images=bool(download_images),
            download_files=bool(download_files),
            same_domain_only=bool(same_domain_only),
            progress=progress,
            should_stop=self.should_stop,
        )

    def run_single(
        self,
        *,
        source_code: str,
        product_url: str,
        image_limit: int = 5,
        collection_method: str = "rich",
        saved_html_path: str = "",
        download_images: bool = True,
        download_files: bool = False,
        same_domain_only: bool = True,
        progress=None,
    ) -> dict[str, Any]:
        from .acquisition_runtime import run_single

        self.reset_stop()
        return run_single(
            self.db,
            source_code=source_code,
            product_url=product_url,
            image_limit=image_limit,
            collection_method=collection_method,
            saved_html_path=saved_html_path,
            download_images=bool(download_images),
            download_files=bool(download_files),
            same_domain_only=bool(same_domain_only),
            progress=progress,
        )

    def refresh_source_products(
        self,
        *,
        source_code: str,
        limit: int = 20,
        image_limit: int = 10,
        download_images: bool = True,
        progress=None,
    ) -> dict[str, Any]:
        from .acquisition_runtime import refresh_source_products

        self.reset_stop()
        return refresh_source_products(
            self.db,
            source_code=str(source_code or ""),
            limit=max(1, min(500, int(limit or 20))),
            image_limit=image_limit,
            download_images=bool(download_images),
            progress=progress,
            should_stop=self.should_stop,
        )

    def setup_login_profile(
        self,
        *,
        source_code: str,
        seed_url: str = "",
    ) -> dict[str, Any]:
        """Open the mature persistent browser profile for manual login/consent.

        This is intentionally a user-driven headed browser. It does not solve or
        bypass login/CAPTCHA; it only persists the operator's normal browser state.
        """
        import asyncio

        from app.crawler import BrowserSession
        from app.runtime_paths import data_root

        code = str(source_code or "").strip()
        if not code:
            raise ValueError("یک Source فعال انتخاب کن.")
        seed = str(seed_url or "").strip() or self.default_listing_url(code)
        if not seed:
            seed = "https://www.google.com"
        profile = data_root() / "browser_profiles" / code

        async def open_profile() -> dict[str, Any]:
            async with BrowserSession(
                profile,
                headed=True,
                min_delay=0,
                max_delay=0,
            ) as session:
                await session.page.goto(
                    seed,
                    wait_until="domcontentloaded",
                    timeout=90_000,
                )
                while session.context.pages:
                    await asyncio.sleep(0.8)
            return {
                "operation": "login_profile",
                "source_code": code,
                "profile_dir": str(profile),
                "seed_url": seed,
            }

        return asyncio.run(open_profile())

    def launch_debug_chrome(
        self,
        *,
        seed_url: str = "",
    ) -> dict[str, Any]:
        """Launch a dedicated Chrome profile exposing CDP on localhost:9222."""
        import os
        import subprocess
        from pathlib import Path

        from app.runtime_paths import data_root

        candidates = [
            Path(os.environ.get("PROGRAMFILES", ""))
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", ""))
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Google"
            / "Chrome"
            / "Application"
            / "chrome.exe",
        ]
        chrome = next((item for item in candidates if item.is_file()), None)
        if chrome is None:
            raise RuntimeError("Google Chrome روی این Windows پیدا نشد.")
        profile = data_root() / "attached_chrome_profile"
        profile.mkdir(parents=True, exist_ok=True)
        target = str(seed_url or "").strip() or "https://makerworld.com/en"
        process = subprocess.Popen(
            [
                str(chrome),
                "--remote-debugging-port=9222",
                f"--user-data-dir={profile}",
                target,
            ]
        )
        return {
            "operation": "debug_chrome",
            "pid": int(process.pid),
            "chrome": str(chrome),
            "profile_dir": str(profile),
            "seed_url": target,
            "cdp_url": "http://127.0.0.1:9222",
        }

    def portfolio_harvest(
        self,
        *,
        requested_per_source: int = 20,
        image_limit: int = 5,
        download_images: bool = True,
        download_files: bool = False,
        same_domain_only: bool = True,
        progress=None,
    ) -> dict[str, Any]:
        """Run the old multi-source discovery idea through the current runtime."""
        from .acquisition_runtime import run_batch

        self.reset_stop()
        sources = self.sources()
        requested = max(1, min(500, int(requested_per_source or 20)))
        results: list[dict[str, Any]] = []
        total_sources = max(1, len(sources))

        for index, source in enumerate(sources, 1):
            if self.should_stop():
                break
            code = str(source.get("code") or "")
            listing = self.default_listing_url(code, query="3d print")
            if not listing:
                results.append({
                    "source_code": code,
                    "skipped": True,
                    "reason": "no default listing",
                })
                continue
            if callable(progress):
                progress(
                    int((index - 1) / total_sources * 95),
                    f"کشف چندمنبعی {index}/{total_sources}: {code}",
                )
            try:
                result = run_batch(
                    self.db,
                    source_code=code,
                    listing_url=listing,
                    requested=requested,
                    image_limit=image_limit,
                    include_failed=False,
                    strategy="classic",
                    operator_mode="automatic",
                    collection_method="classic_isolated",
                    download_images=bool(download_images),
                    download_files=bool(download_files),
                    same_domain_only=bool(same_domain_only),
                    progress=None,
                    should_stop=self.should_stop,
                )
                results.append({"source_code": code, **dict(result or {})})
            except Exception as exc:
                results.append({
                    "source_code": code,
                    "failed": 1,
                    "error": f"{type(exc).__name__}: {exc}",
                })

        summary = {
            "operation": "portfolio_harvest",
            "sources": results,
            "discovered": sum(int(row.get("discovered") or 0) for row in results),
            "collected": sum(int(row.get("collected") or 0) for row in results),
            "duplicates": sum(int(row.get("duplicates") or 0) for row in results),
            "failed": sum(int(row.get("failed") or 0) for row in results),
            "stopped": self.should_stop(),
        }
        if callable(progress):
            progress(
                100,
                "کشف چندمنبعی تمام شد — "
                f"collected={summary['collected']} failed={summary['failed']}",
            )
        return summary

    def recover_product_images(
        self,
        product_id: int,
        *,
        image_limit: int = 10,
        progress=None,
    ) -> dict[str, Any]:
        from .acquisition_runtime import recover_product_images

        self.reset_stop()
        return recover_product_images(
            self.db,
            int(product_id),
            image_limit=image_limit,
            progress=progress,
        )


class PublishCore:
    def __init__(self, db, stages, connection) -> None:
        self.db = db
        self.stages = stages
        self.connection = connection

    def queue(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.upload_queue()]

    def preflight(self, product_ids) -> dict[str, Any]:
        from app.phase49_3i49_site_publish import preflight_many

        return preflight_many(self.db, self.stages, product_ids)

    def mark_ready_many(self, product_ids) -> dict[str, Any]:
        from app.phase49_3i49_site_publish import mark_ready_many

        return mark_ready_many(self.db, self.stages, product_ids)

    def publish_many(self, product_ids, *, progress=None) -> dict[str, Any]:
        from app.phase49_3i49_site_publish import publish_many

        settings = self.connection.settings(require_bridge=True)
        return publish_many(
            self.db,
            self.stages,
            settings,
            product_ids,
            progress=progress,
        )


class AICore:
    """One process-level AI engine entry point for all Qt callers."""

    def __init__(self) -> None:
        self._executor: Callable[..., Any] | None = None
        self._lock = Lock()

    def bind_executor(self, executor: Callable[..., Any]) -> None:
        if not callable(executor):
            raise TypeError("AI executor must be callable")
        self._executor = executor

    @property
    def available(self) -> bool:
        return self._executor is not None

    def execute(self, *args, **kwargs):
        if self._executor is None:
            raise RuntimeError("هسته AI هنوز به Runtime بالغ متصل نشده است.")
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("یک عملیات هوش مصنوعی در حال اجرا است.")
        try:
            return self._executor(*args, **kwargs)
        finally:
            self._lock.release()

    def execute_many(
        self,
        requests: list[dict[str, Any]],
        *,
        progress=None,
    ) -> list[dict[str, Any]]:
        """Run a Product batch sequentially under the one mother AI lock."""
        if self._executor is None:
            raise RuntimeError("هسته AI هنوز به Runtime بالغ متصل نشده است.")
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("یک عملیات هوش مصنوعی در حال اجرا است.")
        try:
            output: list[dict[str, Any]] = []
            total = max(1, len(requests or []))
            for index, request in enumerate(requests or [], 1):
                product_id = int(request.get("product_id") or 0)
                if progress:
                    progress(
                        int((index - 1) / total * 100),
                        f"AI محصول {index}/{total} • #{product_id}",
                    )
                try:
                    result = dict(
                        self._executor(
                            product_id,
                            str(request.get("mode") or "data"),
                            target_stage=request.get("target_stage"),
                            refresh_existing=bool(
                                request.get("refresh_existing", True)
                            ),
                        )
                        or {}
                    )
                    result.setdefault("product_id", product_id)
                    output.append({
                        "ok": True,
                        "product_id": product_id,
                        "result": result,
                    })
                except Exception as exc:
                    output.append({
                        "ok": False,
                        "product_id": product_id,
                        "error": str(exc),
                    })
                if progress:
                    progress(
                        int(index / total * 100),
                        f"AI محصول {index}/{total} تمام شد",
                    )
            return output
        finally:
            self._lock.release()


@dataclass(slots=True)
class ApplicationKernel:
    db: Any
    registry: CoreRegistry

    @property
    def products(self) -> ProductCore:
        return self.registry.require("products", ProductCore)  # type: ignore[return-value]

    @property
    def images(self) -> ImageCore:
        return self.registry.require("images", ImageCore)  # type: ignore[return-value]

    @property
    def filaments(self) -> FilamentParityCore:
        return self.registry.require("filaments", FilamentParityCore)  # type: ignore[return-value]

    @property
    def categories(self) -> CategoryCore:
        return self.registry.require("categories", CategoryCore)  # type: ignore[return-value]

    @property
    def stages(self) -> StageCore:
        return self.registry.require("stages", StageCore)  # type: ignore[return-value]

    @property
    def commerce(self) -> CommerceCore:
        return self.registry.require("commerce", CommerceCore)  # type: ignore[return-value]

    @property
    def providers(self) -> ProviderCore:
        return self.registry.require("providers", ProviderCore)  # type: ignore[return-value]

    @property
    def connection(self) -> ConnectionCore:
        return self.registry.require("connection", ConnectionCore)  # type: ignore[return-value]

    @property
    def acquisition(self) -> AcquisitionCore:
        return self.registry.require("acquisition", AcquisitionCore)  # type: ignore[return-value]

    @property
    def publish(self) -> PublishCore:
        return self.registry.require("publish", PublishCore)  # type: ignore[return-value]

    @property
    def ai(self) -> AICore:
        return self.registry.require("ai", AICore)  # type: ignore[return-value]

    def sync_filaments_with_site(
        self,
        items: list[dict[str, Any]] | None = None,
        *,
        progress=None,
    ) -> dict[str, Any]:
        from app.epic49_site_sync import sync_filament

        rows = (
            [dict(item) for item in items]
            if items is not None
            else self.filaments.list()
        )
        if not rows:
            return {
                "requested": 0,
                "synced": 0,
                "failed": 0,
                "failures": [],
            }

        settings = self.connection.bridge_settings()
        synced = 0
        failures: list[dict[str, Any]] = []
        total = len(rows)
        for index, row in enumerate(rows, 1):
            active = bool(row.pop("_site_active", row.get("is_active", True)))
            payload = self.filaments.site_payload(row, is_active=active)
            label = (
                f"{payload.get('material')} / "
                f"{payload.get('brand')} / "
                f"{payload.get('color')}"
            )
            if callable(progress):
                progress(
                    int((index - 1) / max(1, total) * 100),
                    f"Sync Filament {index}/{total}: {label}",
                )
            try:
                sync_filament(
                    settings,
                    payload,
                    operator="catalog-center-qt6",
                )
                synced += 1
            except Exception as exc:
                failures.append({
                    "identity": label,
                    "error": f"{type(exc).__name__}: {exc}",
                })
            if callable(progress):
                progress(
                    int(index / max(1, total) * 100),
                    f"Sync Filament {index}/{total} تمام شد",
                )

        return {
            "requested": total,
            "synced": synced,
            "failed": len(failures),
            "failures": failures,
        }

    def postprocess_full_product_ai(
        self,
        product_id: int,
        result: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply the same deterministic post-AI completion used by one Product."""
        product_id = int(product_id)
        payload = dict(result or {})
        payload.setdefault("product_id", product_id)

        try:
            row = self.products.get(product_id) or {}
            if not str(row.get("local_category_slug") or "").strip():
                inferred = self.categories.infer_slug(
                    str(row.get("source_category") or ""),
                    str(row.get("source_title") or ""),
                    str(row.get("source_description") or ""),
                )
                if inferred:
                    self.stages.update(
                        product_id,
                        "quick",
                        {"local_category_slug": inferred},
                        event_type="qt_source_category_inferred",
                    )
                    payload["source_category_inferred"] = inferred
                    payload.setdefault("changed_fields", [])
                    payload["changed_fields"] = list(
                        payload["changed_fields"]
                    ) + ["local_category_slug"]
        except Exception as exc:
            payload["source_category_infer_error"] = str(exc)

        try:
            bootstrap = self.commerce.bootstrap_from_source(
                product_id,
                self.filaments.list(),
            )
            payload["source_profile_bootstrap"] = bootstrap
            if bootstrap.get("changed"):
                payload.setdefault("changed_fields", [])
                payload["changed_fields"] = list(
                    payload["changed_fields"]
                ) + [
                    "sales_profile_ledger_json",
                    "sales_profiles_json",
                    "material_color_options_json",
                ]
        except Exception as exc:
            payload["source_profile_bootstrap_error"] = str(exc)

        try:
            row = self.products.get(product_id) or {}
            if self.images.urls(row):
                finalized = self.images.finalize(product_id)
                payload["image_finalize"] = dict(finalized or {})
                payload.setdefault("changed_fields", [])
                payload["changed_fields"] = list(
                    payload["changed_fields"]
                ) + [
                    "image_alt_texts_json",
                    "image_metadata_json",
                ]
        except Exception as exc:
            payload["image_finalize_error"] = str(exc)

        try:
            payload["auto_finalize"] = self.stages.auto_finalize_ready(
                product_id,
                {"quick", "commerce", "images", "content", "specs", "slider"},
            )
        except Exception as exc:
            payload["auto_finalize_error"] = str(exc)

        try:
            active = self.providers.active()
            source_mode = str(
                payload.get("effective_source_mode")
                or payload.get("requested_source_mode")
                or payload.get("_bulk_source_mode")
                or payload.get("source_mode")
                or ""
            )
            self.db.update_product(
                product_id,
                {
                    "ai_completed_once": 1,
                    "ai_completed_at": utc_now(),
                    "ai_completed_source_mode": source_mode,
                    "ai_completed_provider": str(active.get("provider") or ""),
                    "ai_completed_model": str(active.get("model") or ""),
                    "source_license_owner_approved": 1,
                },
            )
            payload["ai_completed_once"] = True
            payload["ai_completed_source_mode"] = source_mode
        except Exception as exc:
            payload["ai_completion_marker_error"] = str(exc)

        payload["target_stages"] = list(
            dict.fromkeys(
                [
                    *list(payload.get("target_stages") or []),
                    "quick",
                    "commerce",
                    "images",
                    "content",
                    "specs",
                    "slider",
                ]
            )
        )
        return payload

    def complete_products_with_ai(
        self,
        product_ids: list[int],
        mode: str = "data",
        *,
        progress=None,
    ) -> dict[str, Any]:
        """Sequential multi-Product full completion through the single AI core."""
        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        prepared: list[int] = []
        failures: list[dict[str, Any]] = []
        for product_id in ids:
            try:
                self.stages.prepare_ai_content_repair(product_id)
                prepared.append(product_id)
            except Exception as exc:
                failures.append({
                    "product_id": product_id,
                    "error": str(exc),
                    "phase": "prepare",
                })

        requests = [
            {
                "product_id": product_id,
                "mode": str(mode or "data"),
                "target_stage": None,
                "refresh_existing": True,
            }
            for product_id in prepared
        ]
        ai_results = self.ai.execute_many(requests, progress=progress)
        completed: list[dict[str, Any]] = []
        for item in ai_results:
            product_id = int(item.get("product_id") or 0)
            if not item.get("ok"):
                failures.append({
                    "product_id": product_id,
                    "error": str(item.get("error") or "AI failed"),
                    "phase": "ai",
                })
                continue
            try:
                result_payload = dict(item.get("result") or {})
                result_payload["_bulk_source_mode"] = str(mode or "data")
                completed.append(
                    self.postprocess_full_product_ai(
                        product_id,
                        result_payload,
                    )
                )
            except Exception as exc:
                failures.append({
                    "product_id": product_id,
                    "error": str(exc),
                    "phase": "postprocess",
                })

        return {
            "requested": len(ids),
            "prepared": len(prepared),
            "completed": len(completed),
            "failed": len(failures),
            "results": completed,
            "failures": failures,
        }

    def contract(self) -> dict[str, Any]:
        return {
            "cores": self.registry.names(),
            "ai_single_engine": True,
            "ai_bound": self.ai.available,
            "database_shared": True,
            "stage_authority_shared": True,
        }


def build_kernel(db) -> ApplicationKernel:
    ensure_qt_parity_schema(db)

    registry = CoreRegistry()
    stages = StageCore(db)
    providers = ProviderCore(db)
    ai = AICore()
    ai.bind_executor(providers.execute_product_ai)

    registry.register("products", ProductCore(db))
    registry.register("images", ImageCore(db))
    registry.register("filaments", FilamentParityCore(db))
    registry.register("categories", CategoryCore(db))
    registry.register("stages", stages)
    registry.register("commerce", CommerceCore(db, stages))
    registry.register("providers", providers)
    connection = ConnectionCore(db)
    registry.register("connection", connection)
    registry.register("acquisition", AcquisitionCore(db))
    registry.register("publish", PublishCore(db, stages, connection))
    registry.register("ai", ai)

    return ApplicationKernel(db=db, registry=registry)
