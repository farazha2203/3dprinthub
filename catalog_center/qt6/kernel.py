from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from types import SimpleNamespace
from typing import Any, Callable, TypeVar
from urllib.parse import quote_plus, urljoin, urlsplit

from app import phase49_3c_image_pipeline as image_pipeline
from app.db import normalize_url, utc_now
from app.phase49_3i38_crawl_ledger_stage_ai import (
    reconcile_product_delete_semantics,
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


def _mark_published_product_dirty(db, product_id: int, *, before=None) -> bool:
    """Queue an already-published Product for guarded in-place re-publish."""
    row = before if before is not None else db.product(int(product_id))
    if row is None:
        return False
    data = dict(row)
    try:
        server_product_id = int(data.get("server_product_id") or 0)
    except Exception:
        server_product_id = 0
    published_identity = bool(
        str(data.get("server_id") or "").strip()
        or server_product_id > 0
    )
    if (
        not published_identity
        or str(data.get("workflow_status") or "").strip().lower() != "uploaded"
    ):
        return False
    db.update_product(
        int(product_id),
        {"needs_update": 1, "upload_ready": 0},
    )
    return True


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
        changed = any(before.get(key) != value for key, value in allowed.items())
        self.db.update_product(int(product_id), allowed)
        if changed:
            _mark_published_product_dirty(
                self.db,
                int(product_id),
                before=before,
            )
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

    def remove_many_detailed(self, product_ids: list[int]) -> dict[str, Any]:
        """Reject Products and report the actual tombstone/cache cleanup result."""
        result: dict[str, Any] = {
            "requested": 0,
            "rejected": 0,
            "purged_dirs": 0,
            "candidate_rows_deleted": 0,
            "preview_files_deleted": 0,
            "cleanup_errors": [],
            "products": [],
        }
        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        result["requested"] = len(ids)
        app = SimpleNamespace(
            db=self.db,
            DATA=Path(self.db.path).resolve().parent,
        )
        for product_id in ids:
            before = self.db.product(product_id)
            if before is None:
                continue
            detail = reject_and_purge_product(
                app,
                product_id,
                "Qt owner reject — keep lightweight tombstone only",
            )
            after = self.db.product(product_id)
            if after is not None and int(after["is_blocked"] or 0):
                result["rejected"] += 1
            result["purged_dirs"] += len(detail.get("purged_dirs") or [])
            result["candidate_rows_deleted"] += int(
                detail.get("candidate_rows_deleted") or 0
            )
            result["preview_files_deleted"] += int(
                bool(detail.get("preview_deleted"))
            )
            result["cleanup_errors"].extend(detail.get("cleanup_errors") or [])
            result["products"].append(detail)
        return result

    def remove_many(self, product_ids: list[int]) -> int:
        return int(self.remove_many_detailed(product_ids).get("rejected") or 0)

    def restore_many_detailed(self, product_ids: list[int]) -> dict[str, Any]:
        result = {
            "requested": 0,
            "restored": 0,
            "recovery_required": [],
            "archive_restored": [],
        }
        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        result["requested"] = len(ids)
        for product_id in ids:
            row = self.db.product(product_id)
            if row is None:
                continue
            if int(row["is_blocked"] or 0):
                was_rejected = str(row["source_state"] or "") == "rejected"
                if was_rejected:
                    restore_rejected_identity(self.db, product_id)
                self.db.restore_product(product_id)
                result["restored"] += 1
                if was_rejected:
                    result["recovery_required"].append(product_id)
            elif str(row["workflow_status"] or "") == "archived":
                self.db.restore_archived_product(product_id)
                result["restored"] += 1
                result["archive_restored"].append(product_id)
        return result

    def restore_many(self, product_ids: list[int]) -> int:
        return int(self.restore_many_detailed(product_ids).get("restored") or 0)

    def reconcile_delete_semantics(self, *, apply: bool = False) -> dict[str, Any]:
        return reconcile_product_delete_semantics(
            self.db,
            data_path=Path(self.db.path).resolve().parent,
            apply=bool(apply),
        )


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

    @staticmethod
    def _url_asset_key(value: str) -> str:
        raw = str(value or "").strip()
        if not raw:
            return ""
        if raw.startswith(("https://", "http://")):
            parts = urlsplit(raw)
            return f"{parts.scheme.casefold()}://{parts.netloc.casefold()}{parts.path}"
        return raw.casefold()

    def source_ordered_urls(self, row: dict[str, Any] | Any) -> list[str]:
        """Return the source gallery order without inserting derived primary aliases."""
        data = dict(row) if not isinstance(row, dict) else row
        for field in ("images_json", "selected_images_json"):
            output: list[str] = []
            for raw in self._json_list(data.get(field)):
                if isinstance(raw, dict):
                    url = str(raw.get("url") or raw.get("source_url") or "").strip()
                else:
                    url = str(raw or "").strip()
                if url and url not in output:
                    output.append(url)
            if output:
                return output
        return self.urls(data)

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

    def identity_local_dirs(
        self,
        source_code: str,
        external_id: str,
        row: dict[str, Any] | Any | None = None,
    ) -> list[Path]:
        """Resolve mature on-disk Product folders without mutating DB state.

        Historical Catalog Center builds stored downloaded files below the
        persistent data root as collected/<source>/<external_id>/images.
        Qt review must keep reading that layout even when an old Crawl ledger
        row is not linked to a Product row yet or its source-code casing drifted.
        """
        source = str(source_code or "").strip()
        external = str(external_id or "").strip()
        if not external:
            return []

        output: list[Path] = []
        seen: set[str] = set()

        def add(candidate: Path) -> None:
            try:
                resolved = candidate.resolve()
            except Exception:
                return
            key = str(resolved).casefold()
            if key in seen or not resolved.is_dir():
                return
            seen.add(key)
            output.append(resolved)

        data = (
            dict(row)
            if row is not None and not isinstance(row, dict)
            else dict(row or {})
        )
        raw_local = str(
            data.get("local_dir")
            or data.get("product_local_dir")
            or ""
        ).strip()
        if raw_local:
            add(Path(raw_local))

        def add_identity_variants(source_dir: Path) -> None:
            if not source_dir.is_dir():
                return
            add(source_dir / external)

            # Mature Tk refetch/source-refresh flows intentionally wrote into
            # sibling folders instead of the original Product directory. Keep
            # all of those historical files visible without moving or rewriting
            # anything on disk.
            known_exact = (
                source_dir / f"{external}_refresh_latest",
            )
            for candidate in known_exact:
                add(candidate)

            variants: list[Path] = []
            for pattern in (
                f"{external}_refetch_*",
                f"{external}_bulk_refetch_*",
            ):
                try:
                    variants.extend(
                        item
                        for item in source_dir.glob(pattern)
                        if item.is_dir()
                    )
                except OSError:
                    continue

            def newest_first(path: Path) -> tuple[float, str]:
                try:
                    stamp = float(path.stat().st_mtime)
                except OSError:
                    stamp = 0.0
                return (-stamp, path.name.casefold())

            for candidate in sorted(variants, key=newest_first):
                add(candidate)

        data_root = Path(self.db.path).resolve().parent
        collected_root = data_root / "collected"
        if source:
            add_identity_variants(collected_root / source)

        if collected_root.is_dir():
            try:
                for source_dir in collected_root.iterdir():
                    if not source_dir.is_dir():
                        continue
                    if source and source_dir.name.casefold() != source.casefold():
                        continue
                    add_identity_variants(source_dir)
            except OSError:
                pass

        # Old installed source/data copies are retained on the owner's Windows
        # workstation. This is a read-only compatibility fallback only.
        legacy_root = Path(r"D:\projects\3dprinthub_catalog_center")
        if legacy_root != data_root and legacy_root.is_dir():
            legacy_collected = legacy_root / "collected"
            if source:
                add_identity_variants(legacy_collected / source)
            if legacy_collected.is_dir():
                try:
                    for source_dir in legacy_collected.iterdir():
                        if not source_dir.is_dir():
                            continue
                        if source and source_dir.name.casefold() != source.casefold():
                            continue
                        add_identity_variants(source_dir)
                except OSError:
                    pass

        return output

    def identity_local_items(
        self,
        source_code: str,
        external_id: str,
        row: dict[str, Any] | Any | None = None,
    ) -> list[str]:
        allowed = {
            ".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif",
            ".bmp", ".tif", ".tiff",
        }
        output: list[str] = []
        seen: set[str] = set()
        for local_dir in self.identity_local_dirs(
            source_code,
            external_id,
            row,
        ):
            for candidate_root in (
                local_dir / "seo_images",
                local_dir / "images",
            ):
                if not candidate_root.is_dir():
                    continue
                try:
                    files = sorted(
                        candidate_root.iterdir(),
                        key=lambda item: item.name.casefold(),
                    )
                except OSError:
                    continue
                for candidate in files:
                    if (
                        not candidate.is_file()
                        or candidate.suffix.lower() not in allowed
                    ):
                        continue
                    try:
                        resolved = candidate.resolve()
                    except OSError:
                        continue
                    key = str(resolved).casefold()
                    if key in seen:
                        continue
                    seen.add(key)
                    output.append(str(resolved))
        return output

    def preferred_identity_local_path(
        self,
        source_code: str,
        external_id: str,
        row: dict[str, Any] | Any | None = None,
    ) -> str:
        items = self.identity_local_items(source_code, external_id, row)
        return items[0] if items else ""

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
        if legacy:
            return legacy[0]
        return self.preferred_identity_local_path(
            str(data.get("source_code") or ""),
            str(data.get("external_id") or ""),
            data,
        )

    @staticmethod
    def _preferred_legacy_display_files(paths: list[str]) -> list[str]:
        resolved_paths: list[Path] = []
        seen: set[str] = set()
        for raw in paths or []:
            try:
                candidate = Path(str(raw or "")).resolve()
            except Exception:
                continue
            if not candidate.is_file():
                continue
            key = str(candidate).casefold()
            if key in seen:
                continue
            seen.add(key)
            resolved_paths.append(candidate)

        finalized = [
            path for path in resolved_paths
            if path.parent.name.casefold() == "seo_images"
        ]
        originals = [
            path for path in resolved_paths
            if path.parent.name.casefold() == "images"
        ]
        preferred = finalized or originals or resolved_paths
        return [str(path) for path in preferred]

    def display_local_paths(self, row: dict[str, Any] | Any) -> list[str]:
        """Return every real source image file needed for operator review.

        Numbered files below ``local_dir/images`` are the mature downloader's
        source-gallery order. Prefer them for review when present, then fill
        missing source slots from strict URL mappings. This prevents a few
        finalized SEO derivatives from hiding later downloaded source images.
        Auxiliary screenshots/non-numbered files stay out of the Product grid.
        """
        data = dict(row) if not isinstance(row, dict) else row

        rejected = str(data.get("rejected_thumbnail_path") or "").strip()
        if rejected:
            try:
                rejected_path = Path(rejected).resolve()
                if rejected_path.is_file():
                    return [str(rejected_path)]
            except Exception:
                pass

        source_urls = self.source_ordered_urls(data)
        raw_root = str(data.get("local_dir") or "").strip()
        numbered: dict[int, str] = {}
        if raw_root:
            try:
                image_dir = Path(raw_root).resolve() / "images"
            except Exception:
                image_dir = Path()
            if image_dir.is_dir():
                try:
                    children = sorted(
                        image_dir.iterdir(),
                        key=lambda item: item.name.casefold(),
                    )
                except OSError:
                    children = []
                for child in children:
                    if not child.is_file() or not child.stem.isdigit():
                        continue
                    slot = int(child.stem)
                    if slot < 1:
                        continue
                    try:
                        numbered.setdefault(slot, str(child.resolve()))
                    except OSError:
                        continue

        if numbered:
            output: list[str] = []
            seen: set[str] = set()
            for slot, url in enumerate(source_urls, 1):
                candidate = numbered.get(slot) or self.local_path_for_url(data, url)
                if not candidate:
                    continue
                try:
                    resolved = Path(candidate).resolve()
                except Exception:
                    continue
                if not resolved.is_file():
                    continue
                key = str(resolved).casefold()
                if key in seen:
                    continue
                seen.add(key)
                output.append(str(resolved))
            # Every real numbered file in the Product's own images directory is
            # reviewable/editable even when an old Product no longer has a
            # one-to-one source URL for that slot. Never synthesize a missing
            # file; append only files that physically exist.
            for slot in sorted(numbered):
                candidate = numbered[slot]
                try:
                    resolved = Path(candidate).resolve()
                except Exception:
                    continue
                if not resolved.is_file():
                    continue
                key = str(resolved).casefold()
                if key in seen:
                    continue
                seen.add(key)
                output.append(str(resolved))
            for screenshot_url in self.urls(data):
                screenshot_url = str(screenshot_url or "").strip()
                if not screenshot_url.casefold().startswith(
                    "local://source-page-screenshot"
                ):
                    continue
                candidate = self.local_path_for_url(data, screenshot_url)
                if not candidate:
                    continue
                try:
                    resolved = Path(candidate).resolve()
                except Exception:
                    continue
                if not resolved.is_file():
                    continue
                key = str(resolved).casefold()
                if key in seen:
                    continue
                seen.add(key)
                output.append(str(resolved))
            if output:
                return output

        urls = self.urls(data)
        exact: list[str] = []
        seen: set[str] = set()
        for url in urls:
            path_value = self.local_path_for_url(data, url)
            if not path_value:
                continue
            try:
                resolved = Path(path_value).resolve()
            except Exception:
                continue
            if not resolved.is_file():
                continue
            key = str(resolved).casefold()
            if key in seen:
                continue
            seen.add(key)
            exact.append(str(resolved))

        metadata = [
            item for item in self._json_list(
                data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
            )
            if isinstance(item, dict)
        ]
        if metadata and exact:
            return exact

        direct = self._preferred_legacy_display_files(self._legacy_local_candidates(data))
        if direct:
            return direct
        if exact:
            return exact

        for local_dir in self.identity_local_dirs(
            str(data.get("source_code") or ""),
            str(data.get("external_id") or ""),
            data,
        ):
            candidate_data = dict(data)
            candidate_data["local_dir"] = str(local_dir)
            candidates = self._preferred_legacy_display_files(
                self._legacy_local_candidates(candidate_data)
            )
            if candidates:
                return candidates
        return []

    @staticmethod
    def _folder_has_displayable_image(local_dir: Path) -> bool:
        allowed = {
            ".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif",
            ".bmp", ".tif", ".tiff",
        }
        for candidate_root in (
            local_dir / "seo_images",
            local_dir / "images",
        ):
            if not candidate_root.is_dir():
                continue
            try:
                for candidate in candidate_root.iterdir():
                    if (
                        candidate.is_file()
                        and candidate.suffix.lower() in allowed
                    ):
                        return True
            except OSError:
                continue
        return False

    def has_local_image(
        self,
        row: dict[str, Any] | Any,
        *,
        source_code: str = "",
        external_id: str = "",
    ) -> bool:
        """Fast first-hit equivalent of the mature display-image contract."""
        data = dict(row) if not isinstance(row, dict) else dict(row)

        rejected = str(data.get("rejected_thumbnail_path") or "").strip()
        if rejected:
            try:
                if Path(rejected).is_file():
                    return True
            except OSError:
                pass

        raw_local = str(
            data.get("local_dir")
            or data.get("product_local_dir")
            or ""
        ).strip()
        if raw_local:
            try:
                local_dir = Path(raw_local).resolve()
            except Exception:
                local_dir = Path()
            if local_dir.is_dir() and self._folder_has_displayable_image(local_dir):
                return True

        for url in self.urls(data):
            path_value = self.local_path_for_url(data, url)
            if not path_value:
                continue
            try:
                if Path(path_value).is_file():
                    return True
            except OSError:
                continue

        source = str(
            source_code
            or data.get("source_code")
            or ""
        ).strip()
        external = str(
            external_id
            or data.get("external_id")
            or ""
        ).strip()
        if not external:
            return False

        data_root = Path(self.db.path).resolve().parent
        direct_roots: list[Path] = []
        if source:
            direct_roots.append(data_root / "collected" / source / external)
        for candidate in direct_roots:
            if candidate.is_dir() and self._folder_has_displayable_image(candidate):
                return True

        # Historical source-code casing and refetch folders are rare. Keep the
        # mature identity resolver as the bounded fallback so accepted legacy
        # layouts remain visible without paying its full cost for normal rows.
        for local_dir in self.identity_local_dirs(source, external, data):
            if self._folder_has_displayable_image(local_dir):
                return True
        return False

    def source_image_count(self, row: dict[str, Any] | Any) -> int:
        data = dict(row) if not isinstance(row, dict) else row
        return len(self.urls(data))

    def image_count(self, row: dict[str, Any] | Any) -> int:
        return len(self.display_local_paths(row))

    def reorder_selected(
        self,
        product_id: int,
        url: str,
        direction: int,
    ) -> dict[str, Any]:
        """Move one selected non-primary image while keeping URL-owned facts aligned.

        The mature Catalog contract keeps the primary image in slot 1. Reorder
        therefore applies to the remaining selected Site images, preserving Alt
        text and metadata by source URL. Physical SEO numbering is regenerated
        separately by ``renumber()`` after this persisted order change.
        """
        row = self._assert_images_editable(product_id)
        data = dict(row)
        target = str(url or "").strip()
        if not target:
            raise ValueError("تصویر برای جابه‌جایی مشخص نشده است.")
        step = -1 if int(direction) < 0 else 1 if int(direction) > 0 else 0
        if not step:
            raise ValueError("جهت جابه‌جایی معتبر نیست.")

        selected: list[str] = []
        for raw in self._json_list(data.get("selected_images_json")):
            if isinstance(raw, dict):
                value = str(raw.get("url") or raw.get("source_url") or "").strip()
            else:
                value = str(raw or "").strip()
            if value and value not in selected:
                selected.append(value)
        if target not in selected:
            raise ValueError("فقط تصویر انتخاب‌شده قابل جابه‌جایی است.")

        primary = str(data.get("primary_image_url") or "").strip()
        if target == primary:
            raise ValueError(
                "تصویر اصلی همیشه جایگاه اول است؛ برای جابه‌جایی آن ابتدا تصویر اصلی را تغییر بده."
            )

        secondary = [value for value in selected if value != primary]
        index = secondary.index(target)
        next_index = max(0, min(len(secondary) - 1, index + step))
        if next_index == index:
            return {
                "changed": False,
                "order": list(selected),
                "primary": primary,
            }
        secondary.pop(index)
        secondary.insert(next_index, target)
        ordered = ([primary] if primary and primary in selected else []) + secondary

        old_alts = [
            str(item or "").strip()
            for item in self._json_list(data.get("image_alt_texts_json"))
        ]
        alt_map = {
            selected[index]: old_alts[index] if index < len(old_alts) else ""
            for index in range(len(selected))
        }

        metadata = [
            dict(item)
            for item in self._json_list(data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
            if isinstance(item, dict)
        ]
        metadata_by_url = {
            str(item.get("source_url") or "").strip(): item
            for item in metadata
            if str(item.get("source_url") or "").strip()
        }
        ordered_metadata = [
            metadata_by_url[value]
            for value in ordered
            if value in metadata_by_url
        ]
        ordered_set = set(ordered)
        ordered_metadata.extend(
            item
            for item in metadata
            if str(item.get("source_url") or "").strip() not in ordered_set
        )

        before = dict(data)
        values = {
            "selected_images_json": json.dumps(ordered, ensure_ascii=False),
            "image_alt_texts_json": json.dumps(
                [alt_map.get(value, "") for value in ordered],
                ensure_ascii=False,
            ),
            image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(
                ordered_metadata,
                ensure_ascii=False,
            ),
        }
        self.db.update_product(int(product_id), values)
        if (
            str(before.get("server_id") or "").strip()
            and str(before.get("workflow_status") or "").strip().lower() == "uploaded"
        ):
            self.db.update_product(
                int(product_id),
                {"needs_update": 1, "upload_ready": 0},
            )
        after = dict(self.db.product(int(product_id)) or {})
        try:
            self.db.save_history(
                int(product_id),
                "qt_image_reordered",
                before,
                after,
                f"Qt image reorder direction={step}",
            )
        except Exception:
            pass
        return {
            "changed": True,
            "order": ordered,
            "primary": primary,
        }

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

        image_dir = (local_dir / "images").resolve()

        def normalize_legacy_local(value: str) -> str:
            raw = str(value or "").strip()
            if not raw.startswith("local-display://"):
                return raw
            name = raw.rsplit("/", 1)[-1]
            candidate_name = Path(name)
            if candidate_name.name != name:
                return raw
            candidate = (image_dir / name).resolve()
            if candidate.parent == image_dir and candidate.is_file():
                return f"local://{name}"
            return raw

        raw_images = [
            str(value or "").strip()
            for value in self._json_list(data.get("images_json"))
            if str(value or "").strip()
        ]
        raw_selected = [
            str(value or "").strip()
            for value in self._json_list(data.get("selected_images_json"))
            if str(value or "").strip()
        ]
        normalized_images = [
            normalize_legacy_local(value) for value in raw_images
        ]
        normalized_selected = [
            normalize_legacy_local(value) for value in raw_selected
        ]
        normalized_primary = normalize_legacy_local(
            str(data.get("primary_image_url") or "")
        )
        metadata = [
            dict(item)
            for item in self._json_list(data.get("image_metadata_json"))
            if isinstance(item, dict)
        ]
        metadata_changed = False
        for item in metadata:
            source_url = str(item.get("source_url") or "").strip()
            normalized_url = normalize_legacy_local(source_url)
            if normalized_url != source_url:
                item["source_url"] = normalized_url
                metadata_changed = True
        identity_changed = (
            normalized_images != raw_images
            or normalized_selected != raw_selected
            or normalized_primary != str(data.get("primary_image_url") or "")
            or metadata_changed
        )
        if identity_changed:
            self.db.update_product(
                product_id,
                {
                    "images_json": json.dumps(
                        list(dict.fromkeys(normalized_images)),
                        ensure_ascii=False,
                    ),
                    "selected_images_json": json.dumps(
                        list(dict.fromkeys(normalized_selected)),
                        ensure_ascii=False,
                    ),
                    "primary_image_url": normalized_primary,
                    "image_metadata_json": json.dumps(
                        metadata,
                        ensure_ascii=False,
                    ),
                },
            )
            data = dict(self.db.product(product_id) or data)

        seo_dir = (local_dir / "seo_images").resolve()
        before = {
            str(Path(str(item.get("final_local_file") or "")).resolve())
            for item in self._json_list(data.get("image_metadata_json"))
            if isinstance(item, dict) and str(item.get("final_local_file") or "").strip()
        }
        operator_selected_count = len(
            self._json_list(data.get("selected_images_json"))
        )
        result = dict(
            image_pipeline.finalize_selected_images(
                self.db,
                product_id,
                deduplicate=False,
                image_limit=max(1, operator_selected_count),
            )
            or {}
        )
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
        _mark_published_product_dirty(
            self.db,
            product_id,
            before=data,
        )
        return result

    def local_items(self, product_id: int) -> list[dict[str, Any]]:
        row = self.db.product(int(product_id))
        if row is None:
            return []
        data = dict(row)

        primary = str(data.get("primary_image_url") or "").strip()
        primary_key = self._url_asset_key(primary)
        slider_image = str(
            data.get("homepage_slider_image_url") or ""
        ).strip()
        slider_key = self._url_asset_key(slider_image)
        urls = self.urls(data)
        source_urls = self.source_ordered_urls(data)
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
        selected_keys = {self._url_asset_key(value) for value in selected_urls if value}
        selected_position_by_key: dict[str, int] = {}
        for index, value in enumerate(selected_urls, 1):
            key = self._url_asset_key(value)
            if key:
                selected_position_by_key.setdefault(key, index)
            raw = str(value or "").strip()
            if raw.startswith("local-display://"):
                name = raw.rsplit("/", 1)[-1]
                if name:
                    local_key = self._url_asset_key(f"local://{name}")
                    if local_key:
                        selected_position_by_key.setdefault(local_key, index)

        alts = [
            str(item or "").strip()
            for item in self._json_list(
                data.get("image_alt_texts_json")
            )
        ]
        alt_by_key = {
            self._url_asset_key(url): (alts[index] if index < len(alts) else "")
            for index, url in enumerate(selected_urls)
            if url
        }
        metadata = [
            dict(item)
            for item in self._json_list(
                data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
            )
            if isinstance(item, dict)
        ]
        exact_metadata_by_url = {
            str(item.get("source_url") or item.get("url") or "").strip(): item
            for item in metadata
            if str(item.get("source_url") or item.get("url") or "").strip()
        }
        exact_selected_position = {
            str(value or "").strip(): index
            for index, value in enumerate(selected_urls, 1)
            if str(value or "").strip()
        }
        exact_alt_by_url = {
            str(url or "").strip(): (
                alts[index] if index < len(alts) else ""
            )
            for index, url in enumerate(selected_urls)
            if str(url or "").strip()
        }

        exact_by_path: dict[str, tuple[int, str]] = {}
        for slot, url in enumerate(urls, 1):
            path = self.local_path_for_url(data, url)
            if not path:
                continue
            try:
                resolved = Path(path).resolve()
            except Exception:
                continue
            if not resolved.is_file():
                continue
            exact_by_path.setdefault(
                str(resolved).casefold(),
                (slot, url),
            )

        output: list[dict[str, Any]] = []
        used_urls: set[str] = set()
        for display_index, raw_path in enumerate(
            self.display_local_paths(data),
            1,
        ):
            try:
                file_path = Path(raw_path).resolve()
            except Exception:
                continue
            if not file_path.is_file():
                continue

            mapped = exact_by_path.get(str(file_path).casefold())
            slot = display_index
            url = ""
            display_only = False
            legacy_alias = ""
            if mapped is not None:
                slot, url = mapped
            else:
                stem = file_path.stem
                if stem.isdigit():
                    numbered_slot = int(stem)
                    if 1 <= numbered_slot <= len(source_urls):
                        candidate_url = source_urls[numbered_slot - 1]
                        is_manual_screenshot = candidate_url.casefold().startswith(
                            "local://source-page-screenshot"
                        )
                        if not is_manual_screenshot and candidate_url not in used_urls:
                            slot = numbered_slot
                            url = candidate_url
                if not url:
                    source_code = str(data.get("source_code") or "local")
                    external_id = str(data.get("external_id") or product_id)
                    legacy_alias = (
                        f"local-display://{source_code}/{external_id}/"
                        f"{file_path.name}"
                    )
                    raw_root = str(data.get("local_dir") or "").strip()
                    trusted_images_dir = None
                    if raw_root:
                        try:
                            trusted_images_dir = (
                                Path(raw_root).resolve() / "images"
                            ).resolve()
                        except Exception:
                            trusted_images_dir = None
                    if (
                        trusted_images_dir is not None
                        and file_path.parent == trusted_images_dir
                    ):
                        url = f"local://{file_path.name}"
                        display_only = False
                    else:
                        url = legacy_alias
                        display_only = True
            used_urls.add(url)

            width = height = file_bytes = 0
            image_format = ""
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

            url_key = self._url_asset_key(url)
            legacy_key = self._url_asset_key(legacy_alias)
            candidate_keys = {key for key in (url_key, legacy_key) if key}
            # Exact source identity must win before canonical asset-key
            # fallback. Query variants can intentionally represent separate
            # selected Product images with different SEO slots; collapsing
            # them here makes two cards display the same filename/metadata.
            meta = exact_metadata_by_url.get(url)
            if meta is None and legacy_alias:
                meta = exact_metadata_by_url.get(legacy_alias)
            if meta is None:
                meta = next(
                    (
                        item
                        for item in metadata
                        if self._url_asset_key(
                            str(item.get("source_url") or item.get("url") or "")
                        ) in candidate_keys
                    ),
                    {},
                )
            alt = exact_alt_by_url.get(url, "")
            if not alt and legacy_alias:
                alt = exact_alt_by_url.get(legacy_alias, "")
            if not alt:
                alt = alt_by_key.get(url_key, "")
            if not alt and legacy_key:
                alt = alt_by_key.get(legacy_key, "")
            if not alt:
                alt = str(meta.get("alt_text") or "")

            planned_filename = str(
                meta.get("seo_filename")
                or meta.get("planned_filename")
                or ""
            ).strip()
            seo_index = int(
                exact_selected_position.get(url)
                or (
                    exact_selected_position.get(legacy_alias)
                    if legacy_alias
                    else 0
                )
                or 0
            )
            if not seo_index:
                seo_index = next(
                    (
                        selected_position_by_key[key]
                        for key in candidate_keys
                        if key in selected_position_by_key
                    ),
                    0,
                )
            if not display_only and url:
                try:
                    filename_index = max(
                        1,
                        int(seo_index or slot or display_index),
                    )
                    fallback_name = image_pipeline.planned_seo_filename(
                        data,
                        filename_index,
                    )
                    planned_filename = image_pipeline._indexed_seo_filename(
                        planned_filename or fallback_name,
                        filename_index,
                        fallback=fallback_name,
                    )
                except Exception:
                    if not planned_filename:
                        planned_filename = ""

            output.append(
                {
                    "slot": slot,
                    "url": url,
                    "path": str(file_path),
                    "filename": file_path.name,
                    "downloaded": True,
                    "display_only": display_only,
                    "primary": (
                        not display_only
                        and bool(primary_key)
                        and primary_key in candidate_keys
                    ),
                    "slider": (
                        not display_only
                        and bool(slider_key)
                        and slider_key in candidate_keys
                    ),
                    "selected": (
                        not display_only
                        and bool(candidate_keys.intersection(selected_keys))
                    ),
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
                    "planned_filename": planned_filename,
                    "metadata": meta,
                }
            )
        return output

    def current_local_items(self, product_id: int) -> list[dict[str, Any]]:
        """Return only canonical media physically owned by the current Product.

        Historical/refetch sibling folders remain available to explicit recovery
        flows, but never participate in normal Product Editor/Social truth.
        Selected rows use the same exact Local file authority as Social.
        """
        row_obj = self.db.product(int(product_id))
        if row_obj is None:
            return []
        data = dict(row_obj)
        raw_root = str(data.get("local_dir") or "").strip()
        if not raw_root:
            return []
        try:
            local_dir = Path(raw_root).resolve()
        except Exception:
            return []
        if not local_dir.is_dir():
            return []

        canonical = [
            str(value or "").strip()
            for value in self._json_list(data.get("images_json"))
            if str(value or "").strip()
        ]
        selected = [
            str(value or "").strip()
            for value in self._json_list(data.get("selected_images_json"))
            if str(value or "").strip()
        ]
        canonical_keys = {
            self._url_asset_key(value): index
            for index, value in enumerate(canonical)
            if self._url_asset_key(value)
        }
        selected_keys = {
            self._url_asset_key(value): index
            for index, value in enumerate(selected)
            if self._url_asset_key(value)
        }

        output: list[dict[str, Any]] = []
        by_key: dict[str, dict[str, Any]] = {}
        for raw in self.local_items(int(product_id)):
            item = dict(raw)
            if bool(item.get("display_only")):
                continue
            key = self._url_asset_key(str(item.get("url") or ""))
            if not key:
                continue
            try:
                path = Path(str(item.get("path") or "")).resolve()
                path.relative_to(local_dir)
            except Exception:
                continue
            if not path.is_file():
                continue
            by_key.setdefault(key, item)

        try:
            from app.phase50_a2w_media_sync import selected_local_media
            exact_selected = {
                self._url_asset_key(str(item.get("source_url") or "")): dict(item)
                for item in selected_local_media(data)
            }
        except RuntimeError:
            exact_selected = {}

        metadata_by_url = {
            str(item.get("source_url") or item.get("url") or "").strip(): dict(item)
            for item in self._json_list(
                data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
            )
            if isinstance(item, dict)
            and str(item.get("source_url") or item.get("url") or "").strip()
        }
        primary_key = self._url_asset_key(
            str(data.get("primary_image_url") or "")
        )
        slider_key = self._url_asset_key(
            str(data.get("homepage_slider_image_url") or "")
        )

        for url in canonical:
            key = self._url_asset_key(url)
            item = dict(by_key.get(key) or {})
            exact = exact_selected.get(key)
            if exact:
                path = Path(str(exact.get("local_path") or "")).resolve()
                if path.is_file():
                    if not item:
                        width = height = file_bytes = 0
                        image_format = ""
                        try:
                            from PIL import Image

                            with Image.open(path) as image:
                                width = int(image.width)
                                height = int(image.height)
                                image_format = str(image.format or "")
                        except Exception:
                            pass
                        try:
                            file_bytes = int(path.stat().st_size)
                        except Exception:
                            pass
                        meta = metadata_by_url.get(url) or {}
                        item = {
                            "slot": int(
                                selected_keys.get(
                                    key,
                                    canonical_keys.get(key, 0),
                                )
                            ) + 1,
                            "url": url,
                            "path": str(path),
                            "filename": path.name,
                            "downloaded": True,
                            "display_only": False,
                            "primary": bool(primary_key and key == primary_key),
                            "slider": bool(slider_key and key == slider_key),
                            "selected": key in selected_keys,
                            "width": width,
                            "height": height,
                            "format": image_format,
                            "bytes": file_bytes,
                            "alt_text": str(meta.get("alt_text") or ""),
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
                                or path.name
                            ),
                            "metadata": meta,
                        }
                    else:
                        item["path"] = str(path)
                        item["filename"] = path.name
                        item["selected"] = key in selected_keys
                        item["primary"] = bool(
                            primary_key and key == primary_key
                        )
                        item["slider"] = bool(
                            slider_key and key == slider_key
                        )
            if not item:
                continue
            output.append(item)

        # Trusted files physically inside this Product's current local_dir are
        # still shown so the operator can select/promote them. They are not
        # Social authority until Stage 3 persists them into images_json and
        # selected_images_json. Historical/refetch sibling folders were
        # filtered above by the local_dir containment gate.
        for key, raw in by_key.items():
            if key in canonical_keys:
                continue
            output.append(dict(raw))

        def order_key(item: dict[str, Any]) -> tuple[int, int, int]:
            key = self._url_asset_key(str(item.get("url") or ""))
            if key in selected_keys:
                return (0, selected_keys[key], int(item.get("slot") or 0))
            return (
                1,
                canonical_keys.get(key, 10_000),
                int(item.get("slot") or 0),
            )

        return sorted(output, key=order_key)

    def _assert_images_editable(self, product_id: int):
        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        if is_stage_locked(row, "images"):
            raise RuntimeError(
                "مرحله تصاویر ثبت نهایی شده است؛ ابتدا «اصلاح مرحله» را بزن."
            )
        return row

    def add_local_files(
        self,
        product_id: int,
        paths: list[str],
    ) -> dict[str, Any]:
        """Copy owner-selected files into the Product and select them for publish."""
        row = self._assert_images_editable(product_id)
        data = dict(row)
        raw_root = str(data.get("local_dir") or "").strip()
        if raw_root:
            local_dir = Path(raw_root).resolve()
        else:
            source_code = str(data.get("source_code") or "manual").strip() or "manual"
            external_id = str(data.get("external_id") or product_id).strip() or str(product_id)
            local_dir = (Path(self.db.path).parent / "collected" / source_code / external_id).resolve()
        image_dir = local_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)

        allowed = {".webp", ".jpg", ".jpeg", ".png", ".avif", ".gif"}
        urls = [
            str(value or "").strip()
            for value in self._json_list(data.get("images_json"))
            if str(value or "").strip()
        ]
        selected = [
            str(value or "").strip()
            for value in self._json_list(data.get("selected_images_json"))
            if str(value or "").strip()
        ]
        added: list[str] = []
        for raw in paths or []:
            source = Path(str(raw or "")).expanduser().resolve()
            if not source.is_file() or source.suffix.lower() not in allowed:
                continue
            digest = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
            safe_stem = "".join(
                char if char.isalnum() or char in {"-", "_"} else "-"
                for char in source.stem
            ).strip("-_") or "image"
            name = f"manual-{safe_stem[:64]}-{digest}{source.suffix.lower()}"
            target = (image_dir / name).resolve()
            if target.parent != image_dir:
                raise RuntimeError("Unsafe local image target.")
            if not target.is_file():
                shutil.copy2(source, target)
            pseudo = f"local://{name}"
            if pseudo not in urls:
                urls.append(pseudo)
            if pseudo not in selected:
                selected.append(pseudo)
            added.append(pseudo)

        if not added:
            raise ValueError("هیچ فایل تصویری معتبر برای افزودن انتخاب نشد.")

        primary = str(data.get("primary_image_url") or "").strip()
        if not primary:
            primary = selected[0]
        self.db.update_product(
            int(product_id),
            {
                "local_dir": str(local_dir),
                "images_json": json.dumps(urls, ensure_ascii=False),
                "selected_images_json": json.dumps(selected, ensure_ascii=False),
                "primary_image_url": primary,
            },
        )
        _mark_published_product_dirty(
            self.db,
            int(product_id),
            before=row,
        )
        return {
            "added": added,
            "selected_count": len(selected),
            "primary_image_url": primary,
        }

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
        remove_local_names = {
            Path(value.split("local://", 1)[1]).name.casefold()
            for value in remove
            if value.startswith("local://")
            and Path(value.split("local://", 1)[1]).name
            == value.split("local://", 1)[1]
        }

        def matches_remove(value: str) -> bool:
            raw = str(value or "").strip()
            if raw in remove:
                return True
            if remove_local_names and raw.startswith(
                ("local://", "local-display://")
            ):
                name = raw.rsplit("/", 1)[-1].casefold()
                return name in remove_local_names
            return False

        all_urls = [
            url
            for url in self.urls(data)
            if not matches_remove(url)
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
            if not matches_remove(url)
        ]
        primary = str(data.get("primary_image_url") or "")
        if matches_remove(primary):
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
                and not matches_remove(str(item.get("source_url") or ""))
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

        moved_local_files: list[tuple[Path, Path]] = []
        raw_root = str(data.get("local_dir") or "").strip()
        if raw_root:
            try:
                local_root = Path(raw_root).resolve()
                image_dir = (local_root / "images").resolve()
                recovery_dir = (local_root / "removed_images").resolve()
            except Exception:
                image_dir = Path()
                recovery_dir = Path()
            for target_url in sorted(remove):
                if not target_url.startswith("local://"):
                    continue
                local_name = target_url.split("local://", 1)[1]
                candidate_name = Path(local_name)
                if (
                    candidate_name.name != local_name
                    or not image_dir.is_dir()
                ):
                    continue
                source = (image_dir / candidate_name.name).resolve()
                if source.parent != image_dir or not source.is_file():
                    continue
                recovery_dir.mkdir(parents=True, exist_ok=True)
                destination = recovery_dir / source.name
                counter = 1
                while destination.exists():
                    destination = recovery_dir / (
                        f"{source.stem}-{counter}{source.suffix}"
                    )
                    counter += 1
                shutil.move(str(source), str(destination))
                moved_local_files.append((source, destination))

        try:
            self.db.update_product(int(product_id), values)
        except Exception:
            for source, destination in reversed(moved_local_files):
                try:
                    if destination.is_file() and not source.exists():
                        shutil.move(str(destination), str(source))
                except Exception:
                    pass
            raise
        _mark_published_product_dirty(
            self.db,
            int(product_id),
            before=data,
        )
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
        ordered_targets: list[str] = []
        for raw in urls or []:
            value = str(raw or "").strip()
            if value and value not in ordered_targets:
                ordered_targets.append(value)
        targets = set(ordered_targets)
        if not ordered_targets:
            raise ValueError("حداقل یک تصویر انتخاب کن.")

        target_local_by_name = {
            Path(url.split("local://", 1)[1]).name.casefold(): url
            for url in targets
            if url.startswith("local://")
            and Path(url.split("local://", 1)[1]).name
            == url.split("local://", 1)[1]
        }

        def normalize_legacy_alias(value: str) -> str:
            raw = str(value or "").strip()
            if target_local_by_name and raw.startswith("local-display://"):
                name = raw.rsplit("/", 1)[-1].casefold()
                replacement = target_local_by_name.get(name)
                if replacement:
                    return replacement
            return raw

        normalized_images = [
            normalize_legacy_alias(str(value or ""))
            for value in self._json_list(data.get("images_json"))
            if str(value or "").strip()
        ]
        normalized_selected = [
            normalize_legacy_alias(str(value or ""))
            for value in self._json_list(data.get("selected_images_json"))
            if str(value or "").strip()
        ]
        normalized_primary = normalize_legacy_alias(
            str(data.get("primary_image_url") or "")
        )

        # Any real trusted local Product image explicitly included in the
        # operator SEO action becomes canonical Product media. This does not
        # change Site membership; it only prevents a later selected-image
        # authority drift where a real local card exists but images_json does
        # not know about it.
        for url in ordered_targets:
            if url in normalized_images:
                continue
            source_value = image_pipeline.strict_source_local_image(data, url)
            if str(source_value or "").strip():
                try:
                    source_path = Path(str(source_value)).resolve()
                except Exception:
                    source_path = None
                if source_path is not None and source_path.is_file():
                    normalized_images.append(url)

        existing = [
            dict(item)
            for item in self._json_list(
                data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]")
            )
            if isinstance(item, dict)
        ]
        for item in existing:
            source_url = str(item.get("source_url") or "").strip()
            normalized_url = normalize_legacy_alias(source_url)
            if normalized_url and normalized_url != source_url:
                item["source_url"] = normalized_url
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
        selected_positions = {
            url: index
            for index, url in enumerate(normalized_selected, start=1)
        }
        image_positions = {
            url: index
            for index, url in enumerate(normalized_images, start=1)
        }
        for url in targets:
            item = by_url.get(url)
            if item is None:
                source_value = image_pipeline.strict_source_local_image(
                    data,
                    url,
                )
                source_path = (
                    Path(str(source_value)).resolve()
                    if str(source_value or "").strip()
                    else None
                )
                if source_path is not None and source_path.is_file():
                    index = int(
                        selected_positions.get(url)
                        or image_positions.get(url)
                        or (len(normalized_images) + 1)
                    )
                    item = dict(
                        image_pipeline.build_image_metadata(
                            data,
                            url,
                            source_path,
                            max(1, index),
                            self.db,
                        )
                    )
                    # Non-Site images are prepared for operator review only.
                    # They become final/publishable only after the operator
                    # explicitly checks "در سایت".
                    if url not in selected_positions:
                        item["metadata_ready"] = False
                        item["seo_signature"] = ""
                        item.pop("final_local_file", None)
                        item.pop("final_sha256", None)
                else:
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
            if url not in selected_positions:
                item["metadata_ready"] = False
                item["seo_signature"] = ""
                item.pop("final_local_file", None)
                item.pop("final_sha256", None)

        selected = list(dict.fromkeys(normalized_selected))
        images = list(dict.fromkeys(normalized_images))
        alt_map = {
            url: str(
                by_url.get(url, {}).get("alt_text") or ""
            )
            for url in selected
        }
        self.db.update_product(
            int(product_id),
            {
                "images_json": json.dumps(
                    images,
                    ensure_ascii=False,
                ),
                "selected_images_json": json.dumps(
                    selected,
                    ensure_ascii=False,
                ),
                "primary_image_url": normalized_primary,
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
        preserved_unselected = [
            dict(item)
            for item in existing
            if str(item.get("source_url") or "") not in set(selected)
        ]
        if selected:
            image_pipeline.finalize_selected_images(
                self.db,
                int(product_id),
                deduplicate=False,
                image_limit=max(1, len(selected)),
            )
            refreshed_row = dict(self.db.product(int(product_id)) or {})
            finalized = [
                dict(item)
                for item in self._json_list(
                    refreshed_row.get(
                        image_pipeline.IMAGE_METADATA_COLUMN,
                        "[]",
                    )
                )
                if isinstance(item, dict)
            ]
            finalized_urls = {
                str(item.get("source_url") or "")
                for item in finalized
                if str(item.get("source_url") or "")
            }
            merged_metadata = list(finalized)
            merged_metadata.extend(
                item
                for item in preserved_unselected
                if str(item.get("source_url") or "") not in finalized_urls
            )
            self.db.update_product(
                int(product_id),
                {
                    image_pipeline.IMAGE_METADATA_COLUMN: json.dumps(
                        merged_metadata,
                        ensure_ascii=False,
                    ),
                },
            )
            image_pipeline.promote_selected_product_local_seo_files(
                self.db,
                int(product_id),
            )
        _mark_published_product_dirty(
            self.db,
            int(product_id),
            before=data,
        )
        return dict(self.db.product(int(product_id)))

    def capture_source_screenshot(self, product_id: int) -> str:
        before = dict(self._assert_images_editable(product_id))
        from app.phase49_3i33_ai_core import capture_source_screenshot

        proxy = SimpleNamespace(
            db=self.db,
            DATA=Path(self.db.path).parent,
        )
        result = str(
            capture_source_screenshot(
                proxy,
                int(product_id),
            )
        )
        _mark_published_product_dirty(
            self.db,
            int(product_id),
            before=before,
        )
        return result

    def finalize(self, product_id: int) -> dict[str, Any]:
        result = dict(
            image_pipeline.finalize_selected_images(
                self.db,
                int(product_id),
            )
            or {}
        )
        result["physical_rename"] = (
            image_pipeline.promote_selected_product_local_seo_files(
                self.db,
                int(product_id),
            )
        )
        return result


class AcquisitionCore:
    """Qt adapter over mature discovery/collection modules."""

    COMPLETENESS_FILTERS = {"complete", "incomplete"}

    def __init__(self, db, images: ImageCore | None = None) -> None:
        self.db = db
        self.images = images or ImageCore(db)
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
        query_text = str(query or "").strip()
        if (
            query_text
            and str(source_code or "").strip().casefold() == "makerworld"
        ):
            return (
                "https://makerworld.com/en/search/models?keyword="
                + quote_plus(query_text)
            )
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

    def is_product_url(self, source_code: str, url: str) -> bool:
        target = str(url or "").strip()
        if not target.startswith(("http://", "https://")):
            return False
        row = self.db.source(str(source_code or ""))
        if row is None:
            return False
        pattern = str(dict(row).get("model_url_pattern") or "").strip()
        if not pattern:
            return False
        try:
            return re.search(pattern, target, re.I) is not None
        except re.error:
            return False

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
                exclude_existing_products=True,
            )
        ]

    def _queue_product_projection(self, row: dict[str, Any]) -> dict[str, Any]:
        data = dict(row or {})
        product_id = int(data.get("product_id") or 0)
        canonical: dict[str, Any] = {}
        if product_id > 0 and "product_title_fa" not in data:
            stored = self.db.product(product_id)
            if stored is not None:
                canonical = dict(stored)

        def projected(name: str, direct: str, default):
            if name in data:
                value = data.get(name)
                return default if value is None else value
            value = canonical.get(direct)
            return default if value is None else value

        return {
            "id": product_id or None,
            "source_code": data.get("source_code") or canonical.get("source_code") or "",
            "external_id": data.get("external_id") or canonical.get("external_id") or "",
            "title_fa": projected("product_title_fa", "title_fa", ""),
            "source_title": projected("product_source_title", "source_title", ""),
            "short_description_fa": projected(
                "product_short_description_fa", "short_description_fa", ""
            ),
            "description_fa": projected(
                "product_description_fa", "description_fa", ""
            ),
            "source_short_description": projected(
                "product_source_short_description", "source_short_description", ""
            ),
            "source_description": projected(
                "product_source_description", "source_description", ""
            ),
            "primary_image_url": projected(
                "product_primary_image_url", "primary_image_url", ""
            ),
            "local_dir": projected("product_local_dir", "local_dir", ""),
            "selected_images_json": projected(
                "product_selected_images_json", "selected_images_json", "[]"
            ),
            "images_json": projected("product_images_json", "images_json", "[]"),
            "image_metadata_json": projected(
                "product_image_metadata_json", "image_metadata_json", "[]"
            ),
        }

    def queue_image_count(self, row: dict[str, Any]) -> int:
        data = dict(row or {})
        product = self._queue_product_projection(data)
        if int(data.get("product_id") or 0) > 0:
            count = int(self.images.image_count(product) or 0)
            if count > 0:
                return count
        return len(
            self.images.identity_local_items(
                str(data.get("source_code") or ""),
                str(data.get("external_id") or ""),
                product,
            )
        )

    @staticmethod
    def _queue_image_cache_key(row: dict[str, Any]) -> tuple[int, str, str]:
        return (
            int(row.get("product_id") or 0),
            str(row.get("source_code") or "").casefold(),
            str(row.get("external_id") or ""),
        )

    def queue_has_local_image(
        self,
        row: dict[str, Any],
        *,
        image_cache: dict[tuple[int, str, str], bool] | None = None,
    ) -> bool:
        data = dict(row or {})
        key = self._queue_image_cache_key(data)
        if image_cache is not None and key in image_cache:
            return bool(image_cache[key])

        product = self._queue_product_projection(data)
        found = bool(
            self.images.has_local_image(
                product,
                source_code=str(data.get("source_code") or ""),
                external_id=str(data.get("external_id") or ""),
            )
        )
        if image_cache is not None:
            image_cache[key] = found
        return found

    def queue_completeness_reasons(
        self,
        row: dict[str, Any],
        *,
        image_cache: dict[tuple[int, str, str], bool] | None = None,
    ) -> list[str]:
        data = dict(row or {})
        product_id = int(data.get("product_id") or 0)

        if product_id <= 0:
            reasons: list[str] = []
            if not str(data.get("candidate_title") or "").strip():
                reasons.append("عنوان Candidate ندارد")
            if not self.queue_has_local_image(
                data,
                image_cache=image_cache,
            ):
                reasons.append("Preview/عکس محلی ندارد")
            return reasons

        product = self._queue_product_projection(data)
        reasons: list[str] = []
        if not (
            str(product.get("title_fa") or "").strip()
            or str(product.get("source_title") or "").strip()
        ):
            reasons.append("عنوان ندارد")
        if not (
            str(product.get("short_description_fa") or "").strip()
            or str(product.get("description_fa") or "").strip()
            or str(product.get("source_short_description") or "").strip()
            or str(product.get("source_description") or "").strip()
        ):
            reasons.append("توضیح ندارد")
        if not self.queue_has_local_image(
            data,
            image_cache=image_cache,
        ):
            reasons.append("فایل عکس محلی قابل نمایش ندارد")
        return reasons

    def queue_is_complete(
        self,
        row: dict[str, Any],
        *,
        image_cache: dict[tuple[int, str, str], bool] | None = None,
    ) -> bool:
        return not self.queue_completeness_reasons(
            row,
            image_cache=image_cache,
        )

    def _queue_completeness_page(
        self,
        source_code: str,
        completeness: str,
        *,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        target_complete = str(completeness or "").strip().lower() == "complete"
        page_limit = max(1, min(int(limit or 100), 500))
        filtered_offset = max(0, int(offset or 0))
        output: list[dict[str, Any]] = []
        matched = 0
        raw_offset = 0
        chunk_size = 250
        image_cache: dict[tuple[int, str, str], bool] = {}

        while len(output) < page_limit:
            chunk = [
                dict(row)
                for row in self.db.discovered_items_page(
                    str(source_code or ""),
                    "all",
                    limit=chunk_size,
                    offset=raw_offset,
                    exclude_existing_products=True,
                )
            ]
            if not chunk:
                break
            raw_offset += len(chunk)
            for row in chunk:
                is_complete = self.queue_is_complete(
                    row,
                    image_cache=image_cache,
                )
                if is_complete != target_complete:
                    continue
                if matched < filtered_offset:
                    matched += 1
                    continue
                output.append(row)
                matched += 1
                if len(output) >= page_limit:
                    break
            if len(chunk) < chunk_size:
                break
        return output

    def queue_count(
        self,
        source_code: str = "",
        status: str = "all",
    ) -> int:
        normalized = str(status or "all").strip().lower()
        if normalized not in self.COMPLETENESS_FILTERS:
            return int(
                self.db.discovered_count(
                    str(source_code or ""),
                    normalized,
                    exclude_existing_products=True,
                )
            )

        target_complete = normalized == "complete"
        total = 0
        raw_offset = 0
        chunk_size = 250
        image_cache: dict[tuple[int, str, str], bool] = {}
        while True:
            chunk = [
                dict(row)
                for row in self.db.discovered_items_page(
                    str(source_code or ""),
                    "all",
                    limit=chunk_size,
                    offset=raw_offset,
                    exclude_existing_products=True,
                )
            ]
            if not chunk:
                break
            raw_offset += len(chunk)
            for row in chunk:
                if self.queue_is_complete(
                    row,
                    image_cache=image_cache,
                ) == target_complete:
                    total += 1
            if len(chunk) < chunk_size:
                break
        return total

    def queue_page(
        self,
        source_code: str = "",
        status: str = "all",
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        normalized = str(status or "all").strip().lower()
        if normalized in self.COMPLETENESS_FILTERS:
            return self._queue_completeness_page(
                str(source_code or ""),
                normalized,
                limit=int(limit),
                offset=int(offset),
            )
        return [
            dict(row)
            for row in self.db.discovered_items_page(
                str(source_code or ""),
                normalized,
                limit=int(limit),
                offset=int(offset),
                exclude_existing_products=True,
            )
        ]

    def queue_rows_by_ids(self, row_ids: list[int]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for row_id in sorted({int(value) for value in row_ids or [] if int(value) > 0}):
            row = self.db.conn.execute(
                "SELECT * FROM discovered_urls WHERE id=?",
                (row_id,),
            ).fetchone()
            if row is None:
                continue
            item = dict(row)
            product = None
            external_id = str(item.get("external_id") or "")
            normalized_url = str(item.get("normalized_url") or "")
            if external_id:
                product = self.db.conn.execute(
                    """
                    SELECT id FROM products
                    WHERE source_code = ? COLLATE NOCASE AND external_id=?
                    ORDER BY id DESC LIMIT 1
                    """,
                    (str(item.get("source_code") or ""), external_id),
                ).fetchone()
            if product is None and normalized_url:
                product = self.db.conn.execute(
                    """
                    SELECT id FROM products
                    WHERE source_code = ? COLLATE NOCASE AND normalized_url=?
                    ORDER BY id DESC LIMIT 1
                    """,
                    (str(item.get("source_code") or ""), normalized_url),
                ).fetchone()
            item["product_id"] = int(product["id"]) if product else None
            output.append(item)
        return output

    def candidate_preview_path(self, source_code: str, external_id: str) -> str:
        from app.phase49_3i_discovery_review import candidate_preview_cache_path

        path = candidate_preview_cache_path(source_code, external_id)
        return str(path) if path.is_file() else ""

    def current_review_items(
        self,
        source_code: str,
        listing_url: str,
        *,
        since: str = "",
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Current-run visual review rows from the mature Preview candidate table."""
        from app.phase49_3i_discovery_review import (
            CANDIDATE_TABLE,
            ensure_schema as ensure_candidate_schema,
        )

        ensure_candidate_schema(self.db)
        clauses = [
            "c.source_code=?",
            "c.discovered_from=?",
            "p.id IS NULL",
        ]
        args: list[Any] = [str(source_code or ""), str(listing_url or "")]
        if str(since or "").strip():
            clauses.append("c.updated_at>=?")
            args.append(str(since))
        page_limit = max(1, min(500, int(limit or 100)))
        args.append(page_limit)
        rows = self.db.conn.execute(
            f"""
            SELECT
                c.id AS candidate_id,
                c.source_code,
                c.external_id,
                c.source_url AS url,
                c.normalized_url,
                c.source_title AS candidate_title,
                c.thumbnail_url AS candidate_thumbnail_url,
                c.status AS candidate_status,
                c.discovered_from,
                c.updated_at AS candidate_updated_at,
                d.id AS queue_id,
                d.status AS status,
                d.attempts,
                d.last_error,
                p.id AS product_id,
                p.title_fa AS product_title_fa,
                p.source_title AS product_source_title,
                p.source_short_description AS product_source_short_description,
                p.source_description AS product_source_description,
                p.short_description_fa AS product_short_description_fa,
                p.description_fa AS product_description_fa,
                p.primary_image_url AS product_primary_image_url,
                p.local_dir AS product_local_dir,
                p.selected_images_json AS product_selected_images_json,
                p.images_json AS product_images_json,
                p.image_metadata_json AS product_image_metadata_json,
                p.source_specs_json AS product_source_specs_json,
                p.tags_json AS product_tags_json,
                p.dimensions AS product_dimensions,
                p.estimated_weight_grams AS product_estimated_weight_grams,
                p.estimated_print_minutes AS product_estimated_print_minutes
            FROM {CANDIDATE_TABLE} c
            LEFT JOIN discovered_urls d
              ON d.source_code=c.source_code
             AND d.external_id=c.external_id
            LEFT JOIN products p
              ON p.source_code=c.source_code COLLATE NOCASE
             AND (
               (c.external_id<>'' AND p.external_id=c.external_id)
               OR
               (c.normalized_url<>'' AND p.normalized_url=c.normalized_url)
             )
            WHERE {" AND ".join(clauses)}
            ORDER BY c.id
            LIMIT ?
            """,
            args,
        )
        output = []
        for row in rows:
            item = dict(row)
            if not str(item.get("status") or ""):
                item["status"] = str(item.get("candidate_status") or "review")
            output.append(item)
        return output

    def reject_queue_items(self, row_ids: list[int]) -> int:
        return int(
            self.db.set_discovered_status(
                row_ids,
                "rejected",
                "operator rejected from Qt queue browser",
            )
        )

    def hard_delete_queue_items(self, row_ids: list[int]) -> dict[str, Any]:
        """Permanently remove only unconsumed Crawl identities.

        Product-backed identities fail closed. Only canonical Crawl/Candidate/
        Preview and candidate-derived local data for the exact identity are
        removed; Product rows and legacy compatibility roots are never touched.
        """
        from app.phase49_3i_discovery_review import (
            CANDIDATE_TABLE,
            candidate_preview_cache_path,
            ensure_schema as ensure_candidate_schema,
        )

        ensure_candidate_schema(self.db)
        result: dict[str, Any] = {
            "requested": 0,
            "deleted": 0,
            "blocked": 0,
            "missing": 0,
            "failed": 0,
            "files_deleted": 0,
            "deleted_row_ids": [],
            "blocked_rows": [],
            "errors": [],
        }
        ids = sorted({int(value) for value in row_ids or [] if int(value) > 0})
        result["requested"] = len(ids)
        data_root = Path(self.db.path).resolve().parent
        collected_root = (data_root / "collected").resolve()

        def identity_local_dirs(source_code: str, external_id: str) -> list[Path]:
            source_cf = str(source_code or "").strip().casefold()
            external = str(external_id or "").strip()
            if not source_cf or not external or not collected_root.is_dir():
                return []
            output: list[Path] = []
            try:
                source_dirs = [
                    item
                    for item in collected_root.iterdir()
                    if item.is_dir() and item.name.casefold() == source_cf
                ]
            except OSError:
                source_dirs = []
            for source_dir in source_dirs:
                try:
                    children = list(source_dir.iterdir())
                except OSError:
                    continue
                for child in children:
                    if not child.is_dir():
                        continue
                    name = child.name
                    if not (
                        name == external
                        or name == f"{external}_refresh_latest"
                        or name.startswith(f"{external}_refetch_")
                        or name.startswith(f"{external}_bulk_refetch_")
                    ):
                        continue
                    resolved = child.resolve()
                    if collected_root not in resolved.parents:
                        raise RuntimeError(
                            f"Unsafe Crawl delete path outside collected: {resolved}"
                        )
                    output.append(resolved)
            return output

        for row_id in ids:
            row = self.db.conn.execute(
                "SELECT * FROM discovered_urls WHERE id=?",
                (row_id,),
            ).fetchone()
            if row is None:
                result["missing"] += 1
                continue
            data = dict(row)
            source_code = str(data.get("source_code") or "").strip()
            external_id = str(data.get("external_id") or "").strip()
            normalized_url = str(data.get("normalized_url") or "").strip()

            product = self.db.conn.execute(
                """
                SELECT id, source_code, external_id, normalized_url
                FROM products
                WHERE source_code=? COLLATE NOCASE
                  AND (
                    (?<>'' AND external_id=?)
                    OR
                    (?<>'' AND normalized_url=?)
                  )
                ORDER BY id
                LIMIT 1
                """,
                (
                    source_code,
                    external_id,
                    external_id,
                    normalized_url,
                    normalized_url,
                ),
            ).fetchone()
            if product is not None:
                result["blocked"] += 1
                result["blocked_rows"].append(
                    {
                        "row_id": row_id,
                        "product_id": int(product["id"]),
                        "source_code": source_code,
                        "external_id": external_id,
                    }
                )
                continue

            try:
                paths = identity_local_dirs(source_code, external_id)
                if external_id:
                    preview = candidate_preview_cache_path(
                        source_code,
                        external_id,
                    )
                    if preview.is_file():
                        preview.unlink()
                        result["files_deleted"] += 1
                for path in paths:
                    if path.is_dir():
                        shutil.rmtree(path)
                        result["files_deleted"] += 1

                with self.db.conn:
                    self.db.conn.execute(
                        f"""
                        DELETE FROM {CANDIDATE_TABLE}
                        WHERE source_code=? COLLATE NOCASE
                          AND (
                            (?<>'' AND external_id=?)
                            OR
                            (?<>'' AND normalized_url=?)
                          )
                        """,
                        (
                            source_code,
                            external_id,
                            external_id,
                            normalized_url,
                            normalized_url,
                        ),
                    )
                    self.db.conn.execute(
                        "DELETE FROM discovered_urls WHERE id=?",
                        (row_id,),
                    )
            except Exception as exc:
                result["failed"] += 1
                result["errors"].append(f"#{row_id}: {exc}")
                continue

            result["deleted"] += 1
            result["deleted_row_ids"].append(row_id)

        return result

    def prepare_queue_full_reacquire(self, row_ids: list[int]) -> dict[str, Any]:
        """Remove active derived bytes for unconsumed Crawl identities, with rollback quarantine.

        The discovery URL/identity is intentionally retained so the caller can immediately
        re-fetch the same Source. Product-backed identities are never touched; their Crawl
        row is reconciled to collected/imported so they disappear from Add Products.
        """
        from app.phase49_3i_discovery_review import (
            CANDIDATE_TABLE,
            candidate_preview_cache_path,
            ensure_schema as ensure_candidate_schema,
        )

        ensure_candidate_schema(self.db)
        result: dict[str, Any] = {
            "requested": 0,
            "prepared": 0,
            "product_backed": 0,
            "missing": 0,
            "failed": 0,
            "files_quarantined": 0,
            "prepared_rows": [],
            "product_rows": [],
            "rollback_roots": [],
            "errors": [],
        }
        ids = sorted({int(value) for value in row_ids or [] if int(value) > 0})
        result["requested"] = len(ids)
        data_root = Path(self.db.path).resolve().parent
        collected_root = (data_root / "collected").resolve()
        rollback_root = (data_root / "repair_backups").resolve()
        stamp = "".join(ch for ch in str(utc_now() or "") if ch.isdigit())[:14] or "reacquire"

        def identity_local_dirs(source_code: str, external_id: str) -> list[Path]:
            source_cf = str(source_code or "").strip().casefold()
            external = str(external_id or "").strip()
            if not source_cf or not external or not collected_root.is_dir():
                return []
            output: list[Path] = []
            try:
                source_dirs = [
                    item
                    for item in collected_root.iterdir()
                    if item.is_dir() and item.name.casefold() == source_cf
                ]
            except OSError:
                source_dirs = []
            for source_dir in source_dirs:
                try:
                    children = list(source_dir.iterdir())
                except OSError:
                    continue
                for child in children:
                    if not child.is_dir():
                        continue
                    name = child.name
                    if not (
                        name == external
                        or name == f"{external}_refresh_latest"
                        or name.startswith(f"{external}_refresh_")
                        or name.startswith(f"{external}_refetch_")
                        or name.startswith(f"{external}_bulk_refetch_")
                        or name.startswith(f"{external}_deep_repair_")
                    ):
                        continue
                    resolved = child.resolve()
                    if collected_root not in resolved.parents:
                        raise RuntimeError(
                            f"Unsafe Crawl reacquire path outside collected: {resolved}"
                        )
                    output.append(resolved)
            return output

        for row_id in ids:
            row = self.db.conn.execute(
                "SELECT * FROM discovered_urls WHERE id=?",
                (row_id,),
            ).fetchone()
            if row is None:
                result["missing"] += 1
                continue
            data = dict(row)
            source_code = str(data.get("source_code") or "").strip()
            external_id = str(data.get("external_id") or "").strip()
            normalized_url = str(data.get("normalized_url") or "").strip()
            source_url = str(data.get("url") or normalized_url or "").strip()

            product = self.db.conn.execute(
                """
                SELECT id
                FROM products
                WHERE source_code=? COLLATE NOCASE
                  AND (
                    (?<>'' AND external_id=?)
                    OR
                    (?<>'' AND normalized_url=?)
                  )
                ORDER BY id
                LIMIT 1
                """,
                (
                    source_code,
                    external_id,
                    external_id,
                    normalized_url,
                    normalized_url,
                ),
            ).fetchone()
            if product is not None:
                product_id = int(product["id"])
                with self.db.conn:
                    self.db.conn.execute(
                        """
                        UPDATE discovered_urls
                        SET status='collected', last_error='', updated_at=?
                        WHERE id=?
                        """,
                        (utc_now(), row_id),
                    )
                    self.db.conn.execute(
                        f"""
                        UPDATE {CANDIDATE_TABLE}
                        SET status='imported', updated_at=?
                        WHERE source_code=? COLLATE NOCASE
                          AND (
                            (?<>'' AND external_id=?)
                            OR
                            (?<>'' AND normalized_url=?)
                          )
                        """,
                        (
                            utc_now(),
                            source_code,
                            external_id,
                            external_id,
                            normalized_url,
                            normalized_url,
                        ),
                    )
                result["product_backed"] += 1
                result["product_rows"].append(
                    {
                        "row_id": row_id,
                        "product_id": product_id,
                        "source_code": source_code,
                        "external_id": external_id,
                    }
                )
                continue

            if (
                not source_code
                or not external_id
                or not source_url.startswith(("http://", "https://"))
            ):
                result["failed"] += 1
                result["errors"].append(
                    f"#{row_id}: valid Source/external-id/Product URL is required"
                )
                continue

            safe_source = "".join(
                ch if ch.isalnum() or ch in "._-" else "_"
                for ch in source_code
            )[:64] or "source"
            safe_external = "".join(
                ch if ch.isalnum() or ch in "._-" else "_"
                for ch in external_id
            )[:96] or f"row_{row_id}"
            target_root = (
                rollback_root
                / f"crawl_reacquire_{stamp}_{row_id}_{safe_source}_{safe_external}"
            )
            try:
                target_root.mkdir(parents=True, exist_ok=False)
                old_local_root = target_root / "old_local"
                paths = identity_local_dirs(source_code, external_id)
                for path in paths:
                    old_local_root.mkdir(parents=True, exist_ok=True)
                    target = old_local_root / path.name
                    if target.exists():
                        raise RuntimeError(
                            f"Reacquire rollback target already exists: {target}"
                        )
                    shutil.move(str(path), str(target))
                    result["files_quarantined"] += 1

                preview = candidate_preview_cache_path(source_code, external_id)
                if preview.is_file():
                    preview_root = target_root / "preview"
                    preview_root.mkdir(parents=True, exist_ok=True)
                    target = preview_root / preview.name
                    shutil.move(str(preview), str(target))
                    result["files_quarantined"] += 1

                with self.db.conn:
                    self.db.conn.execute(
                        """
                        UPDATE discovered_urls
                        SET status='new', attempts=0, last_error='', updated_at=?
                        WHERE id=?
                        """,
                        (utc_now(), row_id),
                    )
                    self.db.conn.execute(
                        f"""
                        UPDATE {CANDIDATE_TABLE}
                        SET status='review', updated_at=?
                        WHERE source_code=? COLLATE NOCASE
                          AND (
                            (?<>'' AND external_id=?)
                            OR
                            (?<>'' AND normalized_url=?)
                          )
                        """,
                        (
                            utc_now(),
                            source_code,
                            external_id,
                            external_id,
                            normalized_url,
                            normalized_url,
                        ),
                    )
            except Exception as exc:
                result["failed"] += 1
                result["errors"].append(f"#{row_id}: {type(exc).__name__}: {exc}")
                continue

            result["prepared"] += 1
            result["rollback_roots"].append(str(target_root))
            result["prepared_rows"].append(
                {
                    "row_id": row_id,
                    "source_code": source_code,
                    "external_id": external_id,
                    "product_url": source_url,
                    "rollback_root": str(target_root),
                }
            )
        return result

    def capture_product_source_screenshot(self, product_id: int) -> str:
        from app.phase49_3i33_ai_core import capture_source_screenshot

        app = SimpleNamespace(
            db=self.db,
            DATA=Path(self.db.path).resolve().parent,
        )
        return str(capture_source_screenshot(app, int(product_id)))

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
        return dict(
            self.db.queue_counts(
                str(source_code or ""),
                exclude_existing_products=True,
            )
        )

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
        force_recover: bool = False,
        adaptive_fallback: bool = False,
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
            force_recover=bool(force_recover),
            adaptive_fallback=bool(adaptive_fallback),
        )

    def acquisition_log_path(self) -> str:
        from .acquisition_trace import log_path

        return str(log_path(self.db))

    def recent_acquisition_events(self, limit: int = 60) -> list[dict[str, Any]]:
        from .acquisition_trace import recent_events

        return recent_events(self.db, limit=limit)

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

    def refresh_source_profiles(
        self,
        product_id: int,
        *,
        fresh_capture: bool = True,
        progress=None,
    ) -> dict[str, Any]:
        from app.phase50_a2w_source_profiles import refresh_product_source_profiles

        self.reset_stop()
        return refresh_product_source_profiles(
            self.db,
            int(product_id),
            fresh_capture=bool(fresh_capture),
            progress=progress,
        )

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

    def deep_repair_product(
        self,
        product_id: int,
        *,
        image_limit: int = 10,
        progress=None,
    ) -> dict[str, Any]:
        from .acquisition_runtime import deep_repair_product_from_source

        self.reset_stop()
        return deep_repair_product_from_source(
            self.db,
            int(product_id),
            image_limit=image_limit,
            progress=progress,
        )

    def download_product_video(
        self,
        product_id: int,
        *,
        progress=None,
    ) -> dict[str, Any]:
        from .acquisition_runtime import download_product_video_from_source

        self.reset_stop()
        return download_product_video_from_source(
            self.db,
            int(product_id),
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


class InstagramCore:
    """Social publisher. The public Site Product remains the commerce authority."""

    def __init__(self, db, connection, publish_core) -> None:
        self.db = db
        self.connection = connection
        self.publish_core = publish_core

    def provider(self) -> str:
        code = str(
            self.db.setting("instagram_publish_provider", "buffer") or "buffer"
        ).strip().lower()
        return code if code in {"direct", "buffer"} else "buffer"

    def config(self):
        if self.provider() == "buffer":
            from app.buffer_publish import BufferConfig

            channel_id = str(
                self.db.setting("buffer_instagram_channel_id", "") or ""
            ).strip()
            if not channel_id:
                raise RuntimeError(
                    "شناسه Channel اینستاگرام در Buffer هنوز تنظیم نشده است."
                )
            return BufferConfig(channel_id=channel_id)

        from app.instagram_publish import InstagramConfig
        account_id = str(
            self.db.setting("instagram_account_id", "") or ""
        ).strip()
        if not account_id:
            raise RuntimeError(
                "شناسه Instagram Professional Account هنوز تنظیم نشده است."
            )
        return InstagramConfig(
            account_id=account_id,
            api_version=str(
                self.db.setting("instagram_api_version", "v26.0") or "v26.0"
            ),
            login_mode=str(
                self.db.setting("instagram_login_mode", "instagram") or "instagram"
            ),
        )

    def delivery_readiness(self, *, scope: str = "both") -> dict[str, Any]:
        """Return fail-closed provider readiness for Feed, Story or combined work."""
        scope = str(scope or "both").strip().lower()
        if scope not in {"feed", "story", "both"}:
            raise RuntimeError(f"Unsupported Instagram delivery scope: {scope}")
        provider = self.provider()
        companion_raw = str(
            self.db.setting("instagram_companion_story_enabled", "1") or "1"
        ).strip().lower()
        companion_enabled = companion_raw not in {"0", "false", "no", "off"}
        link_mode = str(
            self.db.setting("instagram_story_link_mode", "bio_shop_grid")
            or "bio_shop_grid"
        ).strip().lower()
        native_sticker_enabled = link_mode in {
            "native_sticker_notification",
            "native_sticker",
            "notification",
        }

        state: dict[str, Any] = {
            "provider": provider,
            "scope": scope,
            "ready": True,
            "blockers": [],
            "companion_story_enabled": companion_enabled,
            "story_link_mode": link_mode,
            "clickable_story_enabled": native_sticker_enabled,
            "story_supported": provider == "buffer",
            "feed_link_mode": "buffer_shop_grid" if provider == "buffer" else "direct",
            "requires_mobile_handoff": bool(
                provider == "buffer"
                and native_sticker_enabled
                and (
                    scope == "story"
                    or (scope == "both" and companion_enabled)
                )
            ),
        }
        if provider != "buffer":
            if scope == "story":
                state["ready"] = False
                state["blockers"] = [
                    "ارسال مستقل Story در مسیر Instagram Direct پیاده نشده است؛ "
                    "Provider را روی Buffer بگذار یا فقط Post را ارسال کن."
                ]
            return state

        from app.buffer_publish import test_connection

        channel = dict(test_connection(self.config()) or {})
        state.update(
            {
                "channel_id": str(channel.get("id") or ""),
                "channel_name": str(channel.get("name") or ""),
                "external_link": str(channel.get("external_link") or ""),
                "has_active_member_device": bool(
                    channel.get("has_active_member_device")
                ),
            }
        )
        if (
            state["requires_mobile_handoff"]
            and not state["has_active_member_device"]
        ):
            state["ready"] = False
            state["blockers"] = [
                (
                    "Story لینک‌دار نیازمند Buffer mobile فعال است. "
                    "با همان حساب Buffer روی گوشی وارد شو، Push Notification را فعال/Reset کن "
                    "و Test Notification را بگیر؛ تا آن زمان Post+Story جدید شروع نمی‌شود."
                )
            ]
        return state

    def require_delivery_readiness(
        self,
        *,
        scope: str = "both",
    ) -> dict[str, Any]:
        state = self.delivery_readiness(scope=scope)
        if state.get("ready") is True:
            return state
        blockers = [
            str(value).strip()
            for value in (state.get("blockers") or [])
            if str(value).strip()
        ]
        label = {
            "feed": "Instagram Post",
            "story": "Instagram Story",
            "both": "Instagram Post + Story",
        }.get(str(scope or "both").strip().lower(), "Instagram")
        raise RuntimeError(
            f"{label} readiness failed: "
            + (" | ".join(blockers) or "provider_not_ready")
        )

    def preview(self, product_id: int) -> dict[str, Any]:
        from app.instagram_publish import canonical_site_payload
        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        settings = self.connection.settings(require_bridge=False)
        return canonical_site_payload(dict(row), site_url=settings.site_url)

    def publish_feed_many(self, product_ids, *, progress=None) -> dict[str, Any]:
        """Publish only Instagram Feed/Post. Never creates a Story."""
        provider = self.provider()
        readiness = self.require_delivery_readiness(scope="feed")
        cfg = self.config()
        settings = self.connection.settings(require_bridge=False)
        if provider == "buffer":
            from app.buffer_publish import publish_product as publish_feed
            label = "Buffer/Instagram Post"
        else:
            from app.instagram_publish import publish_product as publish_feed
            label = "Instagram Direct Post"

        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        results, failures = [], []
        total = max(1, len(ids))
        for index, product_id in enumerate(ids, 1):
            if progress:
                progress(
                    int((index - 1) / total * 100),
                    f"{label} {index}/{total} • #{product_id}",
                )
            try:
                if provider == "buffer":
                    from app.instagram_feed_asset import prepare_all_current_product_feed_assets
                    from app.buffer_media_host import rehost_buffer_assets

                    self.preview(product_id)  # Fail closed on current public Site readiness.
                    media_host = str(
                        self.db.setting("buffer_media_host", "github_raw")
                        or "github_raw"
                    ).strip().lower()
                    feed_meta = prepare_all_current_product_feed_assets(
                        self.db,
                        product_id,
                        settings,
                        publish_to_site=media_host == "site",
                    )
                    provider_media = rehost_buffer_assets(
                        self.db,
                        product_id,
                        feed_meta,
                        None,
                        timeout=max(10, int(settings.timeout)),
                    )
                    result = publish_feed(
                        self.db,
                        product_id,
                        cfg,
                        site_url=settings.site_url,
                        companion_story=False,
                        feed_asset_urls=list(provider_media.get("feed_urls") or []),
                        feed_alt_texts=list(feed_meta.get("alt_texts") or []),
                        feed_source_urls=list(feed_meta.get("source_urls") or []),
                        media_host_meta=provider_media,
                    )
                else:
                    result = publish_feed(
                        self.db,
                        product_id,
                        cfg,
                        site_url=settings.site_url,
                    )
                results.append(
                    {"product_id": product_id, "provider": provider, **result}
                )
            except Exception as exc:
                failures.append(
                    {
                        "product_id": product_id,
                        "provider": provider,
                        "error": str(exc),
                    }
                )
            if progress:
                progress(
                    int(index / total * 100),
                    f"{label} {index}/{total} تمام شد",
                )
        return {
            "provider": provider,
            "scope": "feed",
            "readiness": readiness,
            "requested": len(ids),
            "published": len(results),
            "failed": len(failures),
            "story_notifications": 0,
            "results": results,
            "failures": failures,
        }

    def publish_story_many(self, product_ids, *, progress=None) -> dict[str, Any]:
        """Publish only Instagram Story. Never creates a Feed/Post."""
        provider = self.provider()
        readiness = self.require_delivery_readiness(scope="story")
        if provider != "buffer":
            raise RuntimeError(
                "ارسال مستقل Story فقط در مسیر Buffer پشتیبانی می‌شود."
            )
        cfg = self.config()
        settings = self.connection.settings(require_bridge=False)
        from app.buffer_publish import publish_story_for_product
        from app.buffer_media_host import rehost_buffer_assets
        from app.instagram_story_asset import prepare_product_story_asset

        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        results, failures = [], []
        total = max(1, len(ids))
        for index, product_id in enumerate(ids, 1):
            if progress:
                progress(
                    int((index - 1) / total * 100),
                    f"Buffer/Instagram Story {index}/{total} • #{product_id}",
                )
            try:
                canonical_payload = self.preview(product_id)
                media_host = str(
                    self.db.setting("buffer_media_host", "github_raw")
                    or "github_raw"
                ).strip().lower()
                story_meta = prepare_product_story_asset(
                    self.db,
                    product_id,
                    settings,
                    canonical_payload,
                    publish_to_site=media_host == "site",
                )
                empty_feed_meta = {
                    "urls": [],
                    "local_paths": [],
                    "source_urls": [],
                    "revision": str(story_meta.get("revision") or ""),
                    "published_to_site": media_host == "site",
                }
                provider_media = rehost_buffer_assets(
                    self.db,
                    product_id,
                    empty_feed_meta,
                    story_meta,
                    timeout=max(10, int(settings.timeout)),
                )
                story_meta = {
                    **story_meta,
                    "provider_media_host": str(provider_media.get("host") or ""),
                    "provider_media_commit_sha": str(
                        provider_media.get("commit_sha") or ""
                    ),
                }
                result = publish_story_for_product(
                    self.db,
                    product_id,
                    cfg,
                    site_url=settings.site_url,
                    story_url_override=str(provider_media.get("story_url") or ""),
                    story_meta=story_meta,
                    link_notification=bool(
                        readiness.get("requires_mobile_handoff")
                    ),
                )
                results.append(
                    {"product_id": product_id, "provider": provider, **result}
                )
            except Exception as exc:
                failures.append(
                    {
                        "product_id": product_id,
                        "provider": provider,
                        "error": str(exc),
                    }
                )
            if progress:
                progress(
                    int(index / total * 100),
                    f"Buffer/Instagram Story {index}/{total} تمام شد",
                )
        story_notifications = sum(
            1
            for item in results
            if bool(item.get("link_sticker_required"))
            and not bool(item.get("instagram_live_confirmed"))
        )
        return {
            "provider": provider,
            "scope": "story",
            "readiness": readiness,
            "requested": len(ids),
            "published": len(results),
            "failed": len(failures),
            "story_notifications": story_notifications,
            "results": results,
            "failures": failures,
        }

    def _publish_site_then_social(
        self,
        product_ids,
        *,
        scope: str,
        progress=None,
    ) -> dict[str, Any]:
        """Ensure Site truth first, then execute exactly one Social scope."""
        scope = str(scope or "").strip().lower()
        if scope not in {"feed", "story"}:
            raise RuntimeError(f"Unsupported social scope: {scope}")
        self.require_delivery_readiness(scope=scope)
        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        already_public, site_needed = [], []
        for product_id in ids:
            try:
                self.preview(product_id)
                already_public.append(product_id)
            except Exception:
                site_needed.append(product_id)

        site_result = {"published": 0, "failed": 0, "items": []}
        if site_needed:
            if progress:
                progress(5, f"انتشار سایت برای {len(site_needed)} محصول")
            site_result = self.publish_core.publish_many(
                site_needed,
                progress=(
                    (
                        lambda value, message: progress(
                            min(65, 5 + int(value * 0.6)),
                            message,
                        )
                    )
                    if progress
                    else None
                ),
            )

        social_ready, site_blocked = [], []
        for product_id in ids:
            try:
                self.preview(product_id)
                social_ready.append(product_id)
            except Exception as exc:
                site_blocked.append(
                    {"product_id": product_id, "error": str(exc)}
                )

        if not social_ready:
            return {
                "social_kind": scope,
                "requested": len(ids),
                "already_public": already_public,
                "site": site_result,
                "site_blocked": site_blocked,
                "instagram": {
                    "scope": scope,
                    "requested": 0,
                    "published": 0,
                    "failed": 0,
                    "results": [],
                    "failures": [],
                },
            }

        if progress:
            label = "Post" if scope == "feed" else "Story"
            progress(68, f"لینک عمومی سایت تأیید شد؛ شروع Instagram {label}")
        publisher = (
            self.publish_feed_many
            if scope == "feed"
            else self.publish_story_many
        )
        social_result = publisher(
            social_ready,
            progress=(
                (
                    lambda value, message: progress(
                        68 + int(value * 0.32),
                        message,
                    )
                )
                if progress
                else None
            ),
        )
        return {
            "social_kind": scope,
            "requested": len(ids),
            "already_public": already_public,
            "site": site_result,
            "site_blocked": site_blocked,
            "instagram": social_result,
        }

    def publish_site_then_feed(self, product_ids, *, progress=None) -> dict[str, Any]:
        return self._publish_site_then_social(
            product_ids,
            scope="feed",
            progress=progress,
        )

    def publish_site_then_story(self, product_ids, *, progress=None) -> dict[str, Any]:
        return self._publish_site_then_social(
            product_ids,
            scope="story",
            progress=progress,
        )

    def publish_many(self, product_ids, *, progress=None) -> dict[str, Any]:
        provider = self.provider()
        cfg = self.config()
        settings = self.connection.settings(require_bridge=False)
        readiness = self.require_delivery_readiness()
        if provider == "buffer":
            from app.buffer_publish import publish_product
            label = "Buffer/Instagram"
        else:
            from app.instagram_publish import publish_product
            label = "Instagram Direct"

        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        results, failures = [], []
        total = max(1, len(ids))
        for index, product_id in enumerate(ids, 1):
            if progress:
                progress(
                    int((index - 1) / total * 100),
                    f"{label} {index}/{total} • #{product_id}",
                )
            try:
                if provider == "buffer":
                    companion_enabled = bool(
                        readiness.get("companion_story_enabled")
                    )
                    story_link_notification = bool(
                        readiness.get("requires_mobile_handoff")
                    )
                    if progress:
                        progress(
                            int((index - 1) / total * 100),
                            f"آماده‌سازی رسانه سازگار Buffer برای محصول #{product_id}",
                        )
                    from app.instagram_feed_asset import prepare_all_current_product_feed_assets

                    canonical_payload = self.preview(product_id)
                    media_host = str(
                        self.db.setting("buffer_media_host", "github_raw")
                        or "github_raw"
                    ).strip().lower()
                    publish_social_derivatives_to_site = media_host == "site"
                    feed_meta = prepare_all_current_product_feed_assets(
                        self.db,
                        product_id,
                        settings,
                        publish_to_site=publish_social_derivatives_to_site,
                    )
                    story_meta = None
                    if companion_enabled:
                        if progress:
                            progress(
                                int((index - 1) / total * 100),
                                f"ساخت Story استاندارد محصول #{product_id}",
                            )
                        from app.instagram_story_asset import prepare_product_story_asset

                        story_meta = prepare_product_story_asset(
                            self.db,
                            product_id,
                            settings,
                            canonical_payload,
                            publish_to_site=publish_social_derivatives_to_site,
                        )
                    from app.buffer_media_host import rehost_buffer_assets

                    provider_media = rehost_buffer_assets(
                        self.db,
                        product_id,
                        feed_meta,
                        story_meta,
                        timeout=max(10, int(settings.timeout)),
                    )
                    if story_meta is not None:
                        story_meta = {
                            **story_meta,
                            "provider_media_host": str(provider_media.get("host") or ""),
                            "provider_media_commit_sha": str(
                                provider_media.get("commit_sha") or ""
                            ),
                        }
                    result = publish_product(
                        self.db,
                        product_id,
                        cfg,
                        site_url=settings.site_url,
                        companion_story=companion_enabled,
                        story_link_notification=story_link_notification,
                        story_asset_url=str(provider_media.get("story_url") or ""),
                        story_meta=story_meta,
                        feed_asset_urls=list(provider_media.get("feed_urls") or []),
                        feed_alt_texts=list(feed_meta.get("alt_texts") or []),
                        feed_source_urls=list(feed_meta.get("source_urls") or []),
                        media_host_meta=provider_media,
                    )
                else:
                    result = publish_product(
                        self.db, product_id, cfg, site_url=settings.site_url
                    )
                results.append(
                    {"product_id": product_id, "provider": provider, **result}
                )
            except Exception as exc:
                failures.append(
                    {
                        "product_id": product_id,
                        "provider": provider,
                        "error": str(exc),
                    }
                )
            if progress:
                progress(
                    int(index / total * 100),
                    f"{label} {index}/{total} تمام شد",
                )
        story_notifications = sum(
            1
            for item in results
            if isinstance(item.get("companion_story"), dict)
            and bool(item["companion_story"].get("link_sticker_required"))
            and not bool(item["companion_story"].get("instagram_live_confirmed"))
        )
        return {
            "provider": provider,
            "requested": len(ids),
            "published": len(results),
            "failed": len(failures),
            "story_notifications": story_notifications,
            "results": results,
            "failures": failures,
        }

    def publish_site_then_instagram(self, product_ids, *, progress=None) -> dict[str, Any]:
        # Global Social delivery readiness must pass before Site mutation, asset
        # rendering/rehosting or any provider createPost call. This prevents the
        # historical partial outcome where Feed/Site succeeded but linked Story
        # could not be handed off to Buffer mobile.
        self.require_delivery_readiness()
        ids = sorted({int(value) for value in product_ids or [] if int(value) > 0})
        already_public, site_needed = [], []
        for product_id in ids:
            try:
                self.preview(product_id)
                already_public.append(product_id)
            except Exception:
                site_needed.append(product_id)

        site_result = {"published": 0, "failed": 0, "items": []}
        if site_needed:
            if progress:
                progress(5, f"انتشار سایت برای {len(site_needed)} محصول")
            site_result = self.publish_core.publish_many(
                site_needed,
                progress=(
                    (lambda value, message: progress(min(65, 5 + int(value * 0.6)), message))
                    if progress else None
                ),
            )

        instagram_ready, site_blocked = [], []
        for product_id in ids:
            try:
                self.preview(product_id)
                instagram_ready.append(product_id)
            except Exception as exc:
                site_blocked.append({"product_id": product_id, "error": str(exc)})

        if not instagram_ready:
            return {
                "requested": len(ids),
                "site": site_result,
                "site_blocked": site_blocked,
                "instagram": {"requested": 0, "published": 0, "failed": 0, "results": [], "failures": []},
            }
        if progress:
            progress(68, "لینک عمومی سایت تأیید شد؛ شروع انتشار Instagram")
        instagram_result = self.publish_many(
            instagram_ready,
            progress=(
                (lambda value, message: progress(68 + int(value * 0.32), message))
                if progress else None
            ),
        )
        return {
            "requested": len(ids),
            "already_public": already_public,
            "site": site_result,
            "site_blocked": site_blocked,
            "instagram": instagram_result,
        }


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
    def instagram(self) -> InstagramCore:
        return self.registry.require("instagram", InstagramCore)  # type: ignore[return-value]

    @property
    def ai(self) -> AICore:
        return self.registry.require("ai", AICore)  # type: ignore[return-value]

    def _local_product_for_server(self, server: dict) -> dict[str, Any] | None:
        server_id = int(server.get("id") or 0)
        profile = server.get("profile") if isinstance(server.get("profile"), dict) else {}
        desktop_id = int(profile.get("desktop_product_id") or 0)

        if desktop_id > 0:
            row = self.db.product(desktop_id)
            if row is not None:
                return dict(row)

        if server_id > 0:
            row = self.db.conn.execute(
                "SELECT * FROM products WHERE server_product_id=? ORDER BY id LIMIT 1",
                (server_id,),
            ).fetchone()
            if row is not None:
                return dict(row)

        source_code = str(server.get("source_code") or "").strip()
        external_id = str(server.get("source_external_id") or "").strip()
        if source_code and external_id:
            row = self.db.conn.execute(
                "SELECT * FROM products WHERE source_code=? AND external_id=? ORDER BY id LIMIT 1",
                (source_code, external_id),
            ).fetchone()
            if row is not None:
                return dict(row)

        source_url = str(server.get("source_url") or "").strip()
        if source_code and source_url:
            normalized = normalize_url(source_url)
            row = self.db.conn.execute(
                "SELECT * FROM products WHERE source_code=? AND normalized_url=? ORDER BY id LIMIT 1",
                (source_code, normalized),
            ).fetchone()
            if row is not None:
                return dict(row)
        return None

    def _create_site_product_mirror(
        self,
        server: dict,
        *,
        site_url: str,
    ) -> int:
        from urllib.parse import urljoin
        from app.epic49_site_sync import apply_server_product_to_local

        server_id = int(server.get("id") or 0)
        if server_id <= 0:
            raise RuntimeError("Site Product has no valid numeric id.")

        source_code = str(server.get("source_code") or "").strip() or "site-admin"
        external_id = str(server.get("source_external_id") or "").strip()
        if not external_id:
            external_id = f"site-product-{server_id}"
        source_url = str(server.get("source_url") or "").strip()
        if not source_url:
            source_url = f"site-admin://product/{server_id}"

        image_urls: list[str] = []
        for item in server.get("images") or []:
            if not isinstance(item, dict):
                continue
            value = str(item.get("url") or item.get("remote_url") or "").strip()
            if not value:
                continue
            if value.startswith("/"):
                value = urljoin(site_url.rstrip("/") + "/", value.lstrip("/"))
            if value not in image_urls:
                image_urls.append(value)
        main_image = str(server.get("main_image") or "").strip()
        if main_image:
            if main_image.startswith("/"):
                main_image = urljoin(site_url.rstrip("/") + "/", main_image.lstrip("/"))
            if main_image not in image_urls:
                image_urls.insert(0, main_image)

        self.db.upsert_product({
            "source_code": source_code,
            "external_id": external_id,
            "source_url": source_url,
            "source_name": str(server.get("source_name") or "Site Admin"),
            "source_title": str(server.get("title_en") or server.get("title") or ""),
            "source_short_description": str(server.get("short_description") or ""),
            "source_description": str(server.get("description") or ""),
            "title_fa": str(server.get("title") or ""),
            "short_description_fa": str(server.get("short_description") or ""),
            "description_fa": str(server.get("description") or ""),
            "local_category_slug": str(server.get("category_slug") or "external-other"),
            "images_json": json.dumps(image_urls, ensure_ascii=False),
            "selected_images_json": json.dumps(image_urls, ensure_ascii=False),
            "primary_image_url": image_urls[0] if image_urls else "",
            "workflow_status": "uploaded" if bool(server.get("is_active")) else "review",
            "server_id": f"site-product:{server_id}",
            "server_status": "updated" if bool(server.get("is_active")) else "review_required",
            "server_product_id": server_id,
            "reference_only": 1,
            "upload_ready": 0,
            "needs_update": 0,
            "custom_notes": (
                "Site-origin mirror. Batch publish is intentionally blocked "
                "until the Product is explicitly linked to an acquisition identity."
            ),
        })
        row = self.db.conn.execute(
            "SELECT * FROM products WHERE source_code=? AND external_id=? ORDER BY id LIMIT 1",
            (source_code, external_id),
        ).fetchone()
        if row is None:
            raise RuntimeError("Local Site Product mirror was not created.")
        local_id = int(row["id"])
        apply_server_product_to_local(self.db, local_id, server)
        self.db.save_history(
            local_id,
            "qt_site_product_mirror_created",
            {},
            dict(self.db.product(local_id)),
            f"Pulled Site Product #{server_id} into a non-publishable Local mirror.",
        )
        return local_id

    def pull_site_products(self, *, progress=None) -> dict[str, Any]:
        from app.epic49_site_sync import (
            apply_server_product_to_local,
            list_all_products,
        )

        settings = self.connection.bridge_settings()
        server_rows = list_all_products(settings)
        result = {
            "requested": len(server_rows),
            "created": 0,
            "updated": 0,
            "unchanged": 0,
            "conflicts": [],
            "failures": [],
        }
        total = max(1, len(server_rows))

        for index, server in enumerate(server_rows, 1):
            if callable(progress):
                progress(
                    int((index - 1) / total * 100),
                    f"Site Product {index}/{len(server_rows)}",
                )
            try:
                local = self._local_product_for_server(server)
                if local is None:
                    self._create_site_product_mirror(
                        server,
                        site_url=settings.site_url,
                    )
                    result["created"] += 1
                    continue

                local_id = int(local["id"])
                profile = (
                    server.get("profile")
                    if isinstance(server.get("profile"), dict)
                    else {}
                )
                server_revision = int(profile.get("sync_revision") or 0)
                local_revision = int(local.get("server_product_revision") or 0)
                local_dirty = bool(
                    int(local.get("needs_update") or 0)
                    or int(local.get("upload_ready") or 0)
                    or str(local.get("workflow_status") or "") in {"approved", "batched"}
                )

                if server_revision > local_revision and local_dirty:
                    message = (
                        f"Site revision {server_revision} is newer than Local "
                        f"revision {local_revision}, while Local has unpublished changes."
                    )
                    self.db.update_product(
                        local_id,
                        {"last_sync_conflict": message},
                    )
                    result["conflicts"].append({
                        "local_product_id": local_id,
                        "server_product_id": int(server.get("id") or 0),
                        "local_revision": local_revision,
                        "server_revision": server_revision,
                        "detail": message,
                    })
                    continue

                if server_revision <= local_revision and local_revision > 0:
                    result["unchanged"] += 1
                    continue

                before = dict(self.db.product(local_id))
                apply_server_product_to_local(self.db, local_id, server)
                after = dict(self.db.product(local_id))
                self.db.save_history(
                    local_id,
                    "qt_site_product_pulled",
                    before,
                    after,
                    (
                        f"Accepted Site revision {server_revision} over "
                        f"Local revision {local_revision}."
                    ),
                )
                result["updated"] += 1
            except Exception as exc:
                result["failures"].append({
                    "server_product_id": int(server.get("id") or 0),
                    "error": f"{type(exc).__name__}: {exc}",
                })
            finally:
                if callable(progress):
                    progress(
                        int(index / total * 100),
                        f"Site Product {index}/{len(server_rows)} تمام شد",
                    )

        result["failed"] = len(result["failures"])
        result["conflict_count"] = len(result["conflicts"])
        return result

    def refresh_product_media_truth(
        self,
        product_id: int,
        *,
        recover_site_media: bool = True,
        include_site: bool = True,
        progress=None,
    ) -> dict[str, Any]:
        """Re-read canonical DB/local media, optionally comparing Site truth."""
        from app.epic49_site_sync import get_product as get_site_product
        from app.phase50_a2w_media_sync import (
            media_truth_snapshot,
            recover_site_media_candidates,
        )

        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        data = dict(row)
        server_id = int(data.get("server_product_id") or 0)
        settings = None
        server: dict[str, Any] | None = None
        site_error = ""
        recovery: dict[str, Any] = {}
        if callable(progress):
            progress(5, "خواندن authority محلی رسانه‌ها")
        if include_site and server_id > 0:
            settings = self.connection.bridge_settings()
            try:
                if callable(progress):
                    progress(15, f"خواندن Site Product #{server_id}")
                server = get_site_product(settings, server_id)
            except Exception as exc:
                site_error = f"{type(exc).__name__}: {exc}"
        if server is not None and recover_site_media and settings is not None:
            recovery = recover_site_media_candidates(
                self.db,
                self.images,
                int(product_id),
                server,
                settings.site_url,
                progress=progress,
            )
        if callable(progress):
            progress(90, "محاسبه اختلاف Local / Site")
        result = media_truth_snapshot(
            self.db,
            self.images,
            int(product_id),
            server=server,
            site_url=(str(settings.site_url) if settings is not None else ""),
            site_error=site_error,
            recovery=recovery,
        )
        if callable(progress):
            progress(100, "Truth Sync رسانه کامل شد")
        result["site_compare"] = bool(include_site)
        return result

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
            else self.filaments.list(include_inactive=True)
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
            raw_material = str(row.get("material") or row.get("material_name") or "—").strip()
            raw_brand = str(
                row.get("brand")
                or row.get("brand_name")
                or row.get("manufacturer")
                or row.get("manufacturer_name")
                or "—"
            ).strip()
            raw_color = str(row.get("color") or row.get("color_name") or "—").strip()
            label = f"{raw_material or '—'} / {raw_brand or '—'} / {raw_color or '—'}"
            if callable(progress):
                progress(
                    int((index - 1) / max(1, total) * 100),
                    f"Sync Filament {index}/{total}: {label}",
                )
            try:
                payload = self.filaments.site_payload(row, is_active=active)
                label = (
                    f"{payload.get('material')} / "
                    f"{payload.get('brand')} / "
                    f"{payload.get('color')}"
                )
                sync_filament(
                    settings,
                    payload,
                    operator="catalog-center-qt6",
                )
                synced += 1
            except Exception as exc:
                failures.append({
                    "identity": label,
                    "row_id": int(row.get("id") or row.get("_row_id") or 0),
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

    @staticmethod
    def _json_object(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return dict(value)
        try:
            parsed = json.loads(value or "{}")
        except Exception:
            return {}
        return dict(parsed) if isinstance(parsed, dict) else {}

    @staticmethod
    def _json_array(value: Any) -> list[Any]:
        if isinstance(value, list):
            return list(value)
        try:
            parsed = json.loads(value or "[]")
        except Exception:
            return []
        return list(parsed) if isinstance(parsed, list) else []

    def _backfill_slider_core(self, product_id: int) -> dict[str, Any]:
        """Fill only missing A2X Slider core data; membership stays operator-owned."""
        product_id = int(product_id)
        row = self.products.get(product_id) or {}
        if not row:
            raise RuntimeError(f"Product {product_id} not found")

        before_membership = int(row.get("homepage_slider_enabled") or 0)
        pack = self._json_object(row.get("content_pack_json"))
        slider = self._json_object(pack.get("homepage_slider_seo"))

        alts = [
            str(value or "").strip()
            for value in self._json_array(row.get("image_alt_texts_json"))
            if str(value or "").strip()
        ]
        keywords = [
            str(value or "").strip()
            for value in (
                self._json_array(row.get("keywords_json"))
                or self._json_array(row.get("keywords_fa_json"))
            )
            if str(value or "").strip()
        ]
        selected = [
            str(value or "").strip()
            for value in self._json_array(row.get("selected_images_json"))
            if str(value or "").strip()
        ]
        primary = str(row.get("primary_image_url") or "").strip()
        slider_image = str(row.get("homepage_slider_image_url") or "").strip()
        if not slider_image:
            if primary and primary in selected:
                slider_image = primary
            elif selected:
                slider_image = selected[0]

        candidates = {
            "homepage_slider_title_fa": (
                str(slider.get("title_fa") or "").strip()
                or str(row.get("seo_title_fa") or "").strip()
                or str(row.get("title_fa") or "").strip()
                or str(row.get("source_title") or "").strip()
            ),
            "homepage_slider_description_fa": (
                str(slider.get("description_fa") or "").strip()
                or str(row.get("short_description_fa") or "").strip()
                or str(row.get("seo_description_fa") or "").strip()
                or str(row.get("description_fa") or "").strip()
            ),
            "homepage_slider_alt_text": (
                str(slider.get("image_alt_fa") or "").strip()
                or (alts[0] if alts else "")
                or str(row.get("title_fa") or "").strip()
                or str(row.get("source_title") or "").strip()
            ),
            "homepage_slider_button_text": (
                str(slider.get("button_text_fa") or "").strip()
                or "مشاهده محصول"
            ),
            "homepage_slider_focus_keyword": (
                str(slider.get("focus_keyword_fa") or "").strip()
                or (keywords[0] if keywords else "")
                or str(row.get("title_fa") or "").strip()
            ),
            "homepage_slider_image_url": slider_image,
        }
        updates = {
            key: value
            for key, value in candidates.items()
            if value and not str(row.get(key) or "").strip()
        }
        if updates:
            self.stages.update(
                product_id,
                "slider",
                updates,
                event_type="qt_full_completion_slider_backfill",
            )

        after = self.products.get(product_id) or {}
        after_membership = int(after.get("homepage_slider_enabled") or 0)
        if before_membership != after_membership:
            raise RuntimeError(
                "Slider completion must not change homepage membership."
            )
        complete = all(
            str(after.get(key) or "").strip()
            for key in (
                "homepage_slider_image_url",
                "homepage_slider_title_fa",
                "homepage_slider_description_fa",
                "homepage_slider_alt_text",
                "homepage_slider_button_text",
                "homepage_slider_focus_keyword",
            )
        )
        return {
            "changed": bool(updates),
            "changed_fields": sorted(updates),
            "complete": bool(complete),
            "membership": bool(after_membership),
        }

    def postprocess_full_product_ai(
        self,
        product_id: int,
        result: dict[str, Any] | None = None,
        *,
        extended_bulk: bool = False,
    ) -> dict[str, Any]:
        """Apply mature post-AI completion; later capabilities are Bulk-only."""
        product_id = int(product_id)
        payload = dict(result or {})
        payload.setdefault("product_id", product_id)

        try:
            row = self.products.get(product_id) or {}
            current_category = str(
                row.get("local_category_slug") or ""
            ).strip()
            category_needs_repair = (
                not current_category
                or (
                    bool(extended_bulk)
                    and current_category == "external-other"
                )
            )
            if category_needs_repair:
                inferred = self.categories.infer_slug(
                    str(row.get("source_category") or ""),
                    str(row.get("source_title") or ""),
                    str(row.get("source_description") or ""),
                )
                if extended_bulk and not inferred:
                    pack = self._json_object(row.get("content_pack_json"))
                    suggested = str(
                        pack.get("suggested_category_slug") or ""
                    ).strip()
                    valid = {
                        str(item.get("slug") or "")
                        for item in self.categories.list()
                    }
                    if suggested in valid and suggested != "external-other":
                        inferred = suggested
                if inferred and inferred != current_category:
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

        source_refresh_error = ""
        if extended_bulk:
            try:
                row = self.products.get(product_id) or {}
                source_url = str(row.get("source_url") or "").strip()
                if "makerworld.com" in urlsplit(source_url).netloc.casefold():
                    payload["source_profile_refresh"] = (
                        self.acquisition.refresh_source_profiles(
                            product_id,
                            fresh_capture=True,
                        )
                    )
            except Exception as exc:
                source_refresh_error = str(exc)
                payload["source_profile_refresh_error"] = source_refresh_error

            try:
                row = self.products.get(product_id) or {}
                source_profiles = [
                    item
                    for item in self._json_array(
                        row.get("source_print_profiles_json")
                    )
                    if isinstance(item, dict)
                ]
                if source_profiles:
                    imported = self.commerce.import_source_profiles(product_id)
                    payload["source_profile_import"] = imported
                    profile_changed = bool(
                        int(imported.get("added") or 0)
                        or int(imported.get("updated") or 0)
                    )
                else:
                    imported = self.commerce.bootstrap_from_source(
                        product_id,
                        self.filaments.list(),
                    )
                    payload["source_profile_bootstrap"] = imported
                    profile_changed = bool(imported.get("changed"))
                if profile_changed:
                    payload.setdefault("changed_fields", [])
                    payload["changed_fields"] = list(
                        payload["changed_fields"]
                    ) + [
                        "sales_profile_ledger_json",
                        "sales_profiles_json",
                        "material_color_options_json",
                    ]
            except Exception as exc:
                payload["source_profile_completion_error"] = str(exc)
                if source_refresh_error:
                    payload["source_profile_completion_fallback"] = (
                        "fresh Source Profile failed; persisted/source facts kept"
                    )
        else:
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
                image_fields = [
                    "image_alt_texts_json",
                    "image_metadata_json",
                ]
                if extended_bulk:
                    physical = dict(
                        (finalized or {}).get("physical_rename") or {}
                    )
                    payload["physical_image_rename"] = physical
                    image_fields.extend(
                        [
                            "images_json",
                            "selected_images_json",
                            "primary_image_url",
                        ]
                    )
                payload["changed_fields"] = list(
                    payload["changed_fields"]
                ) + image_fields
        except Exception as exc:
            payload["image_finalize_error"] = str(exc)

        if extended_bulk:
            try:
                slider = self._backfill_slider_core(product_id)
                payload["slider_backfill"] = slider
                if slider.get("changed"):
                    payload.setdefault("changed_fields", [])
                    payload["changed_fields"] = list(
                        payload["changed_fields"]
                    ) + list(slider.get("changed_fields") or [])
            except Exception as exc:
                payload["slider_backfill_error"] = str(exc)

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
                self.stages.prepare_full_product_completion(product_id)
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
                        extended_bulk=True,
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
    images = ImageCore(db)
    registry.register("images", images)
    registry.register("filaments", FilamentParityCore(db))
    registry.register("categories", CategoryCore(db))
    registry.register("stages", stages)
    registry.register("commerce", CommerceCore(db, stages))
    registry.register("providers", providers)
    connection = ConnectionCore(db)
    registry.register("connection", connection)
    registry.register("acquisition", AcquisitionCore(db, images))
    publish_core = PublishCore(db, stages, connection)
    registry.register("publish", publish_core)
    registry.register("instagram", InstagramCore(db, connection, publish_core))
    registry.register("ai", ai)

    return ApplicationKernel(db=db, registry=registry)
