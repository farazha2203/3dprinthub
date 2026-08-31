from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app import phase49_3c_image_pipeline as image_pipeline
from app import phase49_readiness_wizard as readiness_module
from app.ai_providers import AIProviderClient, PROVIDERS
from app.epic49_desktop_schema import (
    add_available_material_color,
    deactivate_available_material_color,
    ensure_epic49_desktop_schema,
    list_available_material_colors,
    normalize_material_color_options,
)
from app.phase49_3b_guided_wizard import (
    ensure_schema as ensure_guided_slider_schema,
)
from app.phase49_3f_workspace import ensure_schema as ensure_pricing_schema
from app.phase49_3i17_single_active_ai_runtime import active_ai_config
from app.phase49_3i34_profile_matrix import ensure_schema as ensure_profile_matrix_schema
from app.phase49_3i35_operator_ledger import (
    ensure_schema as ensure_profile_ledger_schema,
    flatten_ledger_profiles,
    normalize_ledger_profile,
    normalize_production_row,
)
from app.phase49_3i36_stage_finalization import (
    LOCK_COLUMN,
    STAGE_LABELS,
    STAGE_ORDER,
    content_manual_minimum,
    ensure_schema as ensure_stage_lock_schema,
    field_stage,
    filter_locked_updates,
    is_stage_locked,
    stage_locks,
)
from app.phase49_3i39_professional_commerce import pricing_summary_range, validate_profile_identity
from app.phase49_3i37_seven_stage_ai import AI_SOURCE_MODES, orchestrate_once
from app.phase49_3f_gemini_provider import install as install_google_provider
from app.runtime_paths import data_root
from app.secure_secrets import (
    delete_provider_key,
    delete_secret,
    get_provider_key,
    get_secret,
    provider_key_source,
    secret_source,
    set_provider_key,
    set_secret,
)
from app.site_connection import SiteConnection, test_bridge, test_ftp

_QT_READINESS_CONFIGURED = False

SLIDER_BASE_COLUMNS = {
    "homepage_slider_enabled": "INTEGER NOT NULL DEFAULT 0",
    "homepage_slider_title_fa": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_description_fa": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_alt_text": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_focus_keyword": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_image_url": "TEXT NOT NULL DEFAULT ''",
    "homepage_slider_button_text": "TEXT NOT NULL DEFAULT 'مشاهده محصول'",
    "homepage_slider_transition_effect": "TEXT NOT NULL DEFAULT 'fade'",
    "homepage_slider_transition_duration_ms": "INTEGER NOT NULL DEFAULT 700",
    "homepage_slider_display_duration_ms": "INTEGER NOT NULL DEFAULT 6000",
    "homepage_slider_sort_order": "INTEGER NOT NULL DEFAULT 0",
}

CONTENT_FIELDS = (
    "short_description_fa",
    "description_fa",
    "categories_fa_json",
    "specs_fa_json",
    "tags_fa_json",
    "hashtags_fa_json",
    "keywords_json",
    "seo_title_fa",
    "seo_description_fa",
    "sales_bullets_json",
    "social_caption_fa",
    "use_description",
)

SPEC_FIELDS = (
    "source_url",
    "author_name",
    "license_name",
    "license_url",
    "commercial_status",
    "technical_summary_fa",
    "technical_features_json",
    "source_specs_json",
)

SLIDER_FIELDS = tuple(SLIDER_BASE_COLUMNS) + (
    "homepage_slider_presentation_mode",
    "homepage_slider_object_fit",
    "homepage_slider_focal_position",
    "homepage_slider_image_scale_percent",
    "homepage_slider_position_x_percent",
    "homepage_slider_position_y_percent",
    "homepage_slider_background_mode",
    "homepage_slider_background_color",
    "homepage_slider_background_blur_px",
    "homepage_slider_desktop_max_width_percent",
    "homepage_slider_desktop_max_height_percent",
    "homepage_slider_mobile_max_width_percent",
    "homepage_slider_mobile_max_height_percent",
)

PUBLISH_FIELDS = (
    "approved_for_sale",
    "publish_as_product",
    "publish_as_portfolio",
)


def _json_list(value: Any) -> list:
    if isinstance(value, list):
        return list(value)
    try:
        parsed = json.loads(value or "[]")
    except Exception:
        return []
    return list(parsed) if isinstance(parsed, list) else []


def _json_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(value or "{}")
    except Exception:
        return {}
    return dict(parsed) if isinstance(parsed, dict) else {}


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value if value not in (None, "") else default).replace(",", "").strip())
    except Exception:
        return float(default)


def _integer(value: Any, default: int = 0) -> int:
    try:
        return int(round(_number(value, default)))
    except Exception:
        return int(default)


def _row_dict(row) -> dict[str, Any]:
    if row is None:
        return {}
    return dict(row)


def _columns(db) -> set[str]:
    return {
        str(row["name"])
        for row in db.conn.execute("PRAGMA table_info(products)").fetchall()
    }


def _ensure_slider_base_schema(db) -> None:
    existing = _columns(db)
    changed = False
    for name, ddl in SLIDER_BASE_COLUMNS.items():
        if name not in existing:
            db.conn.execute(f"ALTER TABLE products ADD COLUMN {name} {ddl}")
            changed = True
    if changed:
        db.conn.commit()


def configure_qt_readiness() -> None:
    global _QT_READINESS_CONFIGURED
    if _QT_READINESS_CONFIGURED:
        return

    from app import phase49_3b_guided_wizard as guided
    from app import phase49_3i36_stage_finalization as finalization

    if not getattr(readiness_module, "_qt42b_guided_configured", False):
        guided.configure_readiness(readiness_module)
        readiness_module._qt42b_guided_configured = True

    finalization.configure_readiness(readiness_module)
    _QT_READINESS_CONFIGURED = True


def ensure_qt_parity_schema(db) -> None:
    """Compose only already-mature additive Catalog SQLite schemas."""
    ensure_epic49_desktop_schema(db)
    ensure_pricing_schema(db)
    ensure_profile_matrix_schema(db)
    ensure_profile_ledger_schema(db)
    image_pipeline.ensure_schema(db)
    ensure_guided_slider_schema(db)
    ensure_stage_lock_schema(db)
    _ensure_slider_base_schema(db)
    configure_qt_readiness()


class CategoryCore:
    def __init__(self, db) -> None:
        self.db = db

    def list(self) -> list[dict[str, str]]:
        config_path = Path(__file__).resolve().parents[1] / "config.example.json"
        base: list[dict[str, str]] = []
        if config_path.is_file():
            try:
                payload = json.loads(config_path.read_text(encoding="utf-8"))
                base = [
                    {
                        "slug": str(item.get("slug") or "").strip(),
                        "name": str(item.get("name") or "").strip(),
                    }
                    for item in (payload.get("local_categories") or [])
                    if isinstance(item, dict)
                ]
            except Exception:
                base = []

        try:
            custom_raw = self.db.setting("custom_categories_json", "[]")
            custom = _json_list(custom_raw)
        except Exception:
            custom = []

        output: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in [*base, *custom]:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("slug") or "").strip()
            name = str(item.get("name") or "").strip()
            if not slug or not name or slug in seen:
                continue
            seen.add(slug)
            output.append({"slug": slug, "name": name})
        if not output:
            output.append({"slug": "external-other", "name": "سایر محصولات"})
        return output

    def label_for_slug(self, slug: str) -> str:
        slug = str(slug or "").strip()
        for item in self.list():
            if item["slug"] == slug:
                return item["name"]
        return slug

    def slug_for_label(self, label: str) -> str:
        label = str(label or "").strip()
        for item in self.list():
            if item["name"] == label or item["slug"] == label:
                return item["slug"]
        return label


class StageCore:
    """Readiness/finalization authority shared by every Qt Wizard stage."""

    def __init__(self, db) -> None:
        self.db = db
        ensure_qt_parity_schema(db)

    def state(self, product_id: int) -> dict[str, Any]:
        row = self.db.product(int(product_id))
        return readiness_module.evaluate_readiness(row)

    def statuses(self, product_id: int) -> list[dict[str, Any]]:
        state = self.state(product_id)
        output: list[dict[str, Any]] = []
        stages = state.get("stages") or {}
        for stage in STAGE_ORDER:
            current = dict(stages.get(stage) or {})
            data_ready = bool(current.get("data_ready"))
            finalized = bool(current.get("finalized") or current.get("locked"))
            if finalized and data_ready:
                icon = "✅"
                status = "finalized"
            elif data_ready:
                icon = "◌"
                status = "ready"
            else:
                icon = "❌"
                status = "missing"
            output.append({
                "stage": stage,
                "label": STAGE_LABELS.get(stage, stage),
                "icon": icon,
                "status": status,
                "data_ready": data_ready,
                "finalized": finalized,
                "missing": list(current.get("missing_data") or current.get("missing") or []),
            })
        return output

    def update(
        self,
        product_id: int,
        stage: str,
        values: dict[str, Any],
        *,
        event_type: str = "qt_stage_edit",
    ) -> dict[str, Any]:
        stage = str(stage or "")
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage}")

        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")

        requested = dict(values or {})
        invalid: list[str] = []
        for key in requested:
            owner = field_stage(key)
            if owner and owner != stage:
                invalid.append(key)
        if invalid:
            raise RuntimeError(
                "این فیلدها متعلق به مرحله دیگری هستند: " + "، ".join(sorted(invalid))
            )

        allowed, blocked = filter_locked_updates(row, requested)
        if blocked:
            raise RuntimeError(
                "مرحله ثبت نهایی شده است؛ ابتدا «اصلاح مرحله» را بزن. "
                + "، ".join(blocked)
            )
        if not allowed:
            return _row_dict(row)

        before = _row_dict(row)
        self.db.update_product(int(product_id), allowed)
        after = _row_dict(self.db.product(int(product_id)))
        try:
            self.db.save_history(
                int(product_id),
                event_type,
                before,
                after,
                f"Qt stage={stage}",
            )
        except Exception:
            pass
        return after

    def unlock(self, product_id: int, stage: str) -> dict[str, Any]:
        stage = str(stage or "")
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage}")
        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        locks = stage_locks(row)
        if stage not in locks:
            return _row_dict(row)

        before = _row_dict(row)
        locks.pop(stage, None)
        self.db.update_product(
            int(product_id),
            {LOCK_COLUMN: json.dumps(locks, ensure_ascii=False)},
        )
        if stage == "content" and "seo_manual_approved" in _columns(self.db):
            self.db.update_product(int(product_id), {"seo_manual_approved": 0})
        if stage == "specs" and "source_review_manual_approved" in _columns(self.db):
            self.db.update_product(int(product_id), {"source_review_manual_approved": 0})

        after = _row_dict(self.db.product(int(product_id)))
        try:
            self.db.save_history(
                int(product_id),
                "qt_stage_unlocked",
                before,
                after,
                f"Qt unlocked stage={stage}",
            )
        except Exception:
            pass
        return after

    def finalize(self, product_id: int, stage: str) -> dict[str, Any]:
        stage = str(stage or "")
        if stage not in STAGE_ORDER:
            raise ValueError(f"Unknown stage: {stage}")

        row = self.db.product(int(product_id))
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")

        if is_stage_locked(row, stage):
            if stage == "images":
                selected = image_pipeline.cap_unique_urls(
                    _json_list(row["selected_images_json"] if "selected_images_json" in row.keys() else "[]")
                )
                if selected:
                    image_pipeline.finalize_selected_images(self.db, int(product_id))
            return self.state(product_id)

        state = self.state(product_id)
        current = dict((state.get("stages") or {}).get(stage) or {})
        if stage == "content":
            allowed, missing = content_manual_minimum(row)
        else:
            allowed = bool(current.get("data_ready"))
            missing = list(current.get("missing_data") or current.get("missing") or [])

        if not allowed:
            raise RuntimeError(
                f"{STAGE_LABELS.get(stage, stage)} کامل نیست: "
                + ("، ".join(missing[:12]) if missing else "اطلاعات لازم ناقص است")
            )

        before = _row_dict(row)
        locks = stage_locks(row)
        locks[stage] = {
            "locked": True,
            "locked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        values: dict[str, Any] = {
            LOCK_COLUMN: json.dumps(locks, ensure_ascii=False)
        }
        columns = _columns(self.db)
        if stage == "content" and "seo_manual_approved" in columns:
            values["seo_manual_approved"] = 1
        if stage == "specs" and "source_review_manual_approved" in columns:
            values["source_review_manual_approved"] = 1
        self.db.update_product(int(product_id), values)

        if stage == "images":
            selected = image_pipeline.cap_unique_urls(
                _json_list(_row_dict(self.db.product(int(product_id))).get("selected_images_json", "[]"))
            )
            if selected:
                image_pipeline.finalize_selected_images(self.db, int(product_id))

        after = _row_dict(self.db.product(int(product_id)))
        try:
            self.db.save_history(
                int(product_id),
                "qt_stage_finalized",
                before,
                after,
                f"Qt finalized stage={stage}",
            )
        except Exception:
            pass
        return self.state(product_id)


class FilamentParityCore:
    def __init__(self, db) -> None:
        self.db = db
        ensure_epic49_desktop_schema(db)

    def list(self) -> list[dict[str, Any]]:
        return [dict(row) for row in list_available_material_colors(self.db)]

    def save(self, values: dict[str, Any], *, previous_row_id: int | None = None) -> dict[str, Any]:
        base: dict[str, Any] = {}
        if previous_row_id:
            base = next(
                (
                    dict(item)
                    for item in self.list()
                    if int(item.get("id") or 0) == int(previous_row_id)
                ),
                {},
            )
        data = {**base, **dict(values or {})}
        saved = add_available_material_color(
            self.db,
            data.get("material") or data.get("material_name") or "",
            data.get("color") or data.get("color_name") or "",
            data.get("hex") or data.get("hex_code") or "",
            data.get("color_type") or "solid",
            data.get("secondary_hex") or "",
            data.get("tertiary_hex") or "",
            brand_name=data.get("brand") or data.get("brand_name") or "",
            manufacturer_name=data.get("manufacturer") or data.get("manufacturer_name") or "",
            roll_weight_grams=_integer(data.get("roll_weight_grams"), 1000),
            stock_roll_count=max(0.0, _number(data.get("stock_roll_count"), 0)),
            purchase_price_per_roll=max(0, _integer(data.get("purchase_price_per_roll"), 0)),
            sale_price_per_roll=max(0, _integer(data.get("sale_price_per_roll"), 0)),
            usd_price_per_roll=max(0.0, _number(data.get("usd_price_per_roll"), 0)),
            usd_fx_rate_toman=max(0.0, _number(data.get("usd_fx_rate_toman"), 0)),
            print_hourly_rate=max(0, _integer(data.get("print_hourly_rate"), 0)),
            supervision_hourly_rate=max(0, _integer(data.get("supervision_hourly_rate"), 0)),
            preheat_hours=max(0.0, _number(data.get("preheat_hours"), 0)),
            preheat_temperature_c=max(0.0, _number(data.get("preheat_temperature_c"), 0)),
            preheat_hourly_rate=max(0, _integer(data.get("preheat_hourly_rate"), 0)),
            filament_image_url=str(data.get("filament_image_url") or "").strip(),
        )
        if previous_row_id and int(previous_row_id) != int(saved.get("id") or 0):
            deactivate_available_material_color(self.db, int(previous_row_id))
        return dict(saved)

    def deactivate(self, row_id: int) -> None:
        deactivate_available_material_color(self.db, int(row_id))


class CommerceCore:
    """Profile ledger = one size + many production rows + many Filaments."""

    def __init__(self, db, stages: StageCore) -> None:
        self.db = db
        self.stages = stages
        ensure_qt_parity_schema(db)

    def profiles(self, product_id: int) -> list[dict[str, Any]]:
        row = self.db.product(int(product_id))
        if row is None:
            return []
        raw = _json_list(_row_dict(row).get("sales_profile_ledger_json", "[]"))
        return [
            normalize_ledger_profile(item, index)
            for index, item in enumerate(raw, 1)
            if isinstance(item, dict)
        ]

    def save_profiles(self, product_id: int, profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized = [
            normalize_ledger_profile(item, index)
            for index, item in enumerate(profiles or [], 1)
            if isinstance(item, dict)
        ]
        if normalized and not any(bool(item.get("is_default")) for item in normalized):
            normalized[0]["is_default"] = True

        flattened = flatten_ledger_profiles(normalized)

        offer_map: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        materials: list[str] = []
        colors: list[dict[str, Any]] = []
        price_points: list[int] = []
        strategies: list[str] = []

        for profile in normalized:
            strategies.append(str(profile.get("pricing_strategy") or "dynamic"))
            for offer in normalize_material_color_options(profile.get("material_options") or []):
                key = (
                    str(offer.get("material") or "").casefold(),
                    str(offer.get("brand") or "").casefold(),
                    str(offer.get("manufacturer") or "").casefold(),
                    str(offer.get("color") or "").casefold(),
                )
                offer_map.setdefault(key, offer)
                material = str(offer.get("material") or "").strip()
                if material and material not in materials:
                    materials.append(material)
                color = str(offer.get("color") or "").strip()
                if color and not any(str(item.get("name") or "") == color for item in colors):
                    colors.append({
                        "name": color,
                        "hex": str(offer.get("hex") or ""),
                        "color_type": str(offer.get("color_type") or "solid"),
                        "secondary_hex": str(offer.get("secondary_hex") or ""),
                        "tertiary_hex": str(offer.get("tertiary_hex") or ""),
                    })

            summary = self.summary(profile)
            for key in ("min", "max"):
                value = _integer(summary.get(key), 0)
                if value > 0:
                    price_points.append(value)

        values: dict[str, Any] = {
            "sales_profile_ledger_json": json.dumps(normalized, ensure_ascii=False),
            "sales_profiles_json": json.dumps(flattened, ensure_ascii=False),
            "sales_profile_selection_mode": "size_weight",
            "sales_profile_selector_label": "سایز/پروفایل را انتخاب کنید؛ سپس برند، فیلامنت و رنگ",
            "material_color_options_json": json.dumps(list(offer_map.values()), ensure_ascii=False),
            "material_options_json": json.dumps(materials, ensure_ascii=False),
            "color_options_json": json.dumps(colors, ensure_ascii=False),
        }
        if strategies:
            values["pricing_strategy"] = strategies[0] if len(set(strategies)) == 1 else "profile_matrix"
        if price_points:
            values["price_min"] = min(price_points)
            values["price_max"] = max(price_points)

        self.stages.update(
            int(product_id),
            "commerce",
            values,
            event_type="qt_profile_ledger_edit",
        )
        return normalized

    def upsert_profile(
        self,
        product_id: int,
        profile: dict[str, Any],
        *,
        replace_key: str = "",
    ) -> dict[str, Any]:
        current = self.profiles(product_id)
        candidate = normalize_ledger_profile(profile, len(current) + 1)
        validate_profile_identity(
            current,
            name=candidate.get("name"),
            size_label=candidate.get("size_label"),
            length_cm=candidate.get("part_length_cm"),
            width_cm=candidate.get("part_width_cm"),
            height_cm=candidate.get("part_height_cm"),
            ignore_key=str(replace_key or ""),
        )
        if not current:
            candidate["is_default"] = True
        if replace_key:
            replaced = False
            output = []
            for item in current:
                if str(item.get("key") or "") == str(replace_key):
                    candidate["key"] = item["key"]
                    output.append(candidate)
                    replaced = True
                else:
                    output.append(item)
            if not replaced:
                output.append(candidate)
            current = output
        else:
            current.append(candidate)
        saved = self.save_profiles(product_id, current)
        key = str(candidate.get("key") or "")
        return next((item for item in saved if str(item.get("key") or "") == key), candidate)

    def delete_profile(self, product_id: int, key: str) -> list[dict[str, Any]]:
        filtered = [
            item
            for item in self.profiles(product_id)
            if str(item.get("key") or "") != str(key or "")
        ]
        return self.save_profiles(product_id, filtered)

    def clone_profile(self, product_id: int, key: str) -> dict[str, Any]:
        source = next(
            (
                item
                for item in self.profiles(product_id)
                if str(item.get("key") or "") == str(key or "")
            ),
            None,
        )
        if source is None:
            raise RuntimeError("پروفایل انتخابی پیدا نشد.")
        clone = deepcopy(source)
        clone.pop("key", None)
        clone["name"] = f"{source.get('name') or 'پروفایل'} - کپی"
        clone["size_label"] = f"{source.get('size_label') or ''} - کپی".strip()
        return self.upsert_profile(product_id, clone)

    def summary(self, profile: dict[str, Any]) -> dict[str, int]:
        item = normalize_ledger_profile(profile, 1)
        return pricing_summary_range(
            item.get("material_options") or [],
            item.get("production_rows") or [],
            item.get("pricing_strategy") or "dynamic",
            support_multiplier=item.get("support_cost_multiplier") or 1,
            assembly_fee=item.get("assembly_fee") or 0,
            price_min=item.get("price_min") or 0,
            price_max=item.get("price_max") or 0,
        )

    @staticmethod
    def normalize_production_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            normalize_production_row(item)
            for item in (rows or [])
            if isinstance(item, dict)
        ]

    @staticmethod
    def normalize_offers(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return normalize_material_color_options(rows or [])


class ProviderCore:
    LABELS = {
        "avalai": "AvalAI",
        "openrouter": "OpenRouter",
        "google": "Google Gemini",
        "openai": "OpenAI Direct",
    }

    def __init__(self, db) -> None:
        self.db = db
        install_google_provider()

    def providers(self) -> list[dict[str, str]]:
        return [
            {
                "code": code,
                "label": self.LABELS.get(code, getattr(spec, "label", code)),
            }
            for code, spec in PROVIDERS.items()
            if code in {"avalai", "openrouter", "google", "openai"}
        ]

    def active(self) -> dict[str, str]:
        provider = str(self.db.setting("ai_provider", "") or "").strip().lower()
        model = str(
            self.db.setting(f"ai_model_{provider}", "")
            or self.db.setting("ai_model", "")
            or ""
        ).strip()
        return {
            "provider": provider,
            "model": model,
            "key_source": provider_key_source(provider) if provider else "not configured",
        }

    def save_default(self, provider: str, model: str) -> dict[str, str]:
        provider = str(provider or "").strip().lower()
        model = str(model or "").strip()
        if provider not in {"avalai", "openrouter", "google", "openai"}:
            raise ValueError("Provider معتبر انتخاب نشده است.")
        if not model:
            raise ValueError("Model معتبر انتخاب نشده است.")
        if model.startswith("models/"):
            model = model.split("models/", 1)[1]
        self.db.set_setting("ai_provider", provider)
        self.db.set_setting(f"ai_model_{provider}", model)
        self.db.set_setting("ai_model", model)
        return self.active()

    def key_source(self, provider: str) -> str:
        return provider_key_source(str(provider or "").strip().lower())

    def save_key(self, provider: str, key: str) -> None:
        set_provider_key(str(provider or "").strip().lower(), str(key or "").strip())

    def delete_key(self, provider: str) -> None:
        delete_provider_key(str(provider or "").strip().lower())

    def _client(self, provider: str, model: str = "", key_override: str = "") -> AIProviderClient:
        provider = str(provider or "").strip().lower()
        if provider not in {"avalai", "openrouter", "google", "openai"}:
            raise ValueError("Provider معتبر نیست.")
        key = str(key_override or "").strip() or str(get_provider_key(provider) or "").strip()
        if not key:
            raise RuntimeError(f"API Key امن برای {provider} پیدا نشد.")
        return AIProviderClient(provider, key, str(model or "").strip())

    def models(self, provider: str, *, key_override: str = "") -> list[dict[str, Any]]:
        client = self._client(provider, key_override=key_override)
        return list(client.list_model_info())

    def test(self, provider: str, model: str = "", *, key_override: str = "") -> dict[str, Any]:
        client = self._client(provider, model=model, key_override=key_override)
        result = dict(client.test_connection())
        result["provider"] = provider
        result["model"] = model
        return result

    def execute_product_ai(
        self,
        product_id: int,
        mode: str,
        *,
        target_stage: str | None = None,
        refresh_existing: bool = False,
    ) -> dict[str, Any]:
        proxy = SimpleNamespace(db=self.db, DATA=data_root())
        provider, key, model = active_ai_config(proxy, require_key=True)
        stages = {target_stage} if target_stage else None
        return orchestrate_once(
            proxy,
            int(product_id),
            str(mode or "data"),
            provider,
            key,
            model,
            dialog=None,
            target_stages=stages,
            refresh_existing=bool(refresh_existing),
        )

    def source_modes(self) -> list[dict[str, str]]:
        return [
            {"code": code, "label": label}
            for code, label in AI_SOURCE_MODES.items()
        ]


class ConnectionCore:
    def __init__(self, db) -> None:
        self.db = db

    def values(self) -> dict[str, Any]:
        return {
            "ftp_protocol": self.db.setting("ftp_protocol", "FTP") or "FTP",
            "ftp_host": self.db.setting("ftp_host", "ftp.3dprinthub.ir") or "ftp.3dprinthub.ir",
            "ftp_port": self.db.setting("ftp_port", "21") or "21",
            "ftp_user": self.db.setting("ftp_user", "sfkilvrs") or "sfkilvrs",
            "ftp_remote_root": self.db.setting("ftp_remote_root", "/3dprinthub") or "/3dprinthub",
            "site_url": self.db.setting("site_url", "https://3dprinthub.ir") or "https://3dprinthub.ir",
            "ftp_password_source": secret_source("ftp_password"),
            "bridge_token_source": secret_source("bridge_token"),
        }

    def save(self, values: dict[str, Any], *, ftp_password: str = "", bridge_token: str = "") -> dict[str, Any]:
        data = dict(values or {})
        port = _integer(data.get("ftp_port"), 21)
        if port <= 0:
            raise ValueError("FTP Port معتبر نیست.")
        persistent = {
            "ftp_protocol": "FTP",
            "ftp_host": str(data.get("ftp_host") or "").strip(),
            "ftp_port": str(port),
            "ftp_user": str(data.get("ftp_user") or "").strip(),
            "ftp_remote_root": str(data.get("ftp_remote_root") or "").strip(),
            "site_url": str(data.get("site_url") or "").strip(),
        }
        for key, value in persistent.items():
            self.db.set_setting(key, value)
        if str(ftp_password or "").strip():
            set_secret("ftp_password", str(ftp_password).strip())
        if str(bridge_token or "").strip():
            set_secret("bridge_token", str(bridge_token).strip())
        return self.values()

    def clear_ftp_password(self) -> None:
        delete_secret("ftp_password")

    def clear_bridge_token(self) -> None:
        delete_secret("bridge_token")

    def settings(self, *, require_bridge: bool = True) -> SiteConnection:
        values = self.values()
        cfg = SiteConnection(
            ftp_host=values["ftp_host"],
            ftp_port=_integer(values["ftp_port"], 21),
            ftp_user=values["ftp_user"],
            ftp_password=get_secret("ftp_password"),
            remote_root=values["ftp_remote_root"],
            site_url=values["site_url"],
            bridge_token=get_secret("bridge_token"),
        ).normalized()
        if not all([cfg.ftp_host, cfg.ftp_user, cfg.ftp_password]):
            raise ValueError("Host، Username و Password اتصال FTP باید کامل باشند.")
        if require_bridge and not all([cfg.site_url, cfg.bridge_token]):
            raise ValueError("آدرس سایت و Bridge Token باید کامل باشند.")
        return cfg

    def test_ftp(self) -> dict[str, Any]:
        return dict(test_ftp(self.settings(require_bridge=False)))

    def test_bridge(self) -> dict[str, Any]:
        return dict(test_bridge(self.settings(require_bridge=True)))


def product_description_summary(row: dict[str, Any]) -> str:
    for key in (
        "short_description_fa",
        "source_short_description",
        "description_fa",
        "source_description",
    ):
        text = re.sub(r"\s+", " ", str(row.get(key) or "")).strip()
        if text:
            return text[:240]
    return ""
