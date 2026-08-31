from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Callable, TypeVar

from app import phase49_3c_image_pipeline as image_pipeline
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


class ImageCore:
    """Single image resolver shared by Product cards and the image stage."""

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
                    url = str(raw.get("url") or raw.get("source_url") or "").strip()
                else:
                    url = str(raw or "").strip()
                if url and url not in output:
                    output.append(url)
        return output

    def local_path_for_url(self, row: dict[str, Any] | Any, url: str) -> str:
        data = dict(row) if not isinstance(row, dict) else row
        path = image_pipeline.strict_source_local_image(data, url)
        if not path:
            path = image_pipeline.strict_local_image(data, url)
        return str(path or "")

    def preferred_local_path(self, row: dict[str, Any] | Any) -> str:
        for url in self.urls(row):
            path = self.local_path_for_url(row, url)
            if path:
                return path
        return ""

    def local_items(self, product_id: int) -> list[dict[str, Any]]:
        row = self.db.product(int(product_id))
        if row is None:
            return []
        data = dict(row)

        primary = str(data.get("primary_image_url") or "").strip()
        selected_urls = []
        for raw in self._json_list(data.get("selected_images_json")):
            if isinstance(raw, dict):
                url = str(raw.get("url") or raw.get("source_url") or "").strip()
            else:
                url = str(raw or "").strip()
            if url:
                selected_urls.append(url)
        selected = set(selected_urls)

        alts = [
            str(item or "").strip()
            for item in self._json_list(data.get("image_alt_texts_json"))
        ]
        raw_meta = self._json_list(data.get(image_pipeline.IMAGE_METADATA_COLUMN, "[]"))
        metadata: list[dict[str, Any]] = [
            dict(item) for item in raw_meta if isinstance(item, dict)
        ]

        output: list[dict[str, Any]] = []
        for index, url in enumerate(self.urls(data)):
            path = self.local_path_for_url(data, url)
            if not path:
                continue

            file_path = Path(path)
            width = 0
            height = 0
            image_format = ""
            try:
                from PIL import Image

                with Image.open(file_path) as image:
                    width = int(image.width)
                    height = int(image.height)
                    image_format = str(image.format or "")
            except Exception:
                pass

            meta = next(
                (
                    item
                    for item in metadata
                    if str(item.get("source_url") or item.get("url") or "") == url
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

            try:
                file_bytes = int(file_path.stat().st_size)
            except Exception:
                file_bytes = 0

            output.append({
                "url": url,
                "path": str(file_path),
                "filename": file_path.name,
                "primary": url == primary,
                "selected": url in selected,
                "width": width,
                "height": height,
                "format": image_format,
                "bytes": file_bytes,
                "alt_text": alt,
                "seo_title": str(meta.get("title") or ""),
                "caption": str(meta.get("caption") or ""),
                "keywords": list(meta.get("keywords") or []) if isinstance(meta.get("keywords"), list) else [],
                "planned_filename": str(meta.get("planned_filename") or meta.get("seo_filename") or ""),
                "metadata": meta,
            })
        return output

    def finalize(self, product_id: int) -> dict[str, Any]:
        return dict(image_pipeline.finalize_selected_images(self.db, int(product_id)) or {})


class AcquisitionCore:
    def __init__(self, db) -> None:
        self.db = db

    def queue_counts(self) -> dict[str, int]:
        return dict(self.db.queue_counts())

    def recent_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.runs(limit=int(limit))]


class PublishCore:
    def __init__(self, db) -> None:
        self.db = db

    def queue(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.upload_queue()]


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
    registry.register("connection", ConnectionCore(db))
    registry.register("acquisition", AcquisitionCore(db))
    registry.register("publish", PublishCore(db))
    registry.register("ai", ai)

    return ApplicationKernel(db=db, registry=registry)
