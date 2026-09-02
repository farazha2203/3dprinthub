from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from PIL import Image
from typing import Any

from app import phase49_3c_image_pipeline as image_pipeline
from app import phase49_readiness_wizard as readiness_module
from app.ai_providers import AIProviderClient, PROVIDERS, remember_model_capability
from app.ai_model_catalog import (
    contains_persian,
    enrich_model_info,
    estimate_request_cost,
    estimate_text_tokens,
    product_model_compatibility,
    rank_models,
)
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
    "source_license_owner_approved",
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

    def infer_slug(
        self,
        source_category: str,
        source_title: str = "",
        source_description: str = "",
    ) -> str:
        """Return only a validated local category backed by source text.

        Exact source-category/slug matches win. The small alias table is an
        explicit project taxonomy bridge, not an AI guess. Ambiguous ties or
        unknown concepts return an empty string so the operator keeps control.
        """
        categories = self.list()
        valid = {str(item["slug"]): dict(item) for item in categories}
        if not valid:
            return ""

        def fold(value: str) -> str:
            return re.sub(
                r"[^a-z0-9]+",
                "-",
                str(value or "").casefold(),
            ).strip("-")

        source_category_text = str(source_category or "").strip()
        source_category_folded = fold(source_category_text)
        for item in categories:
            slug = str(item.get("slug") or "")
            if (
                source_category_text.casefold()
                == str(item.get("name") or "").casefold()
                or source_category_folded == fold(slug)
                or source_category_folded == fold(item.get("name") or "")
            ):
                return slug

        aliases: dict[str, tuple[str, ...]] = {
            "home-decor": (
                "lamp", "light", "lighting", "vase", "decor", "decoration",
                "home decor", "household",
            ),
            "organizers": ("organizer", "organiser", "storage organizer"),
            "plant-pots": ("plant pot", "flower pot", "planter"),
            "toys-games": ("toy", "game", "puzzle"),
            "figurines": ("figurine", "statue", "sculpture"),
            "gears": ("gear", "cog", "gearbox"),
            "automotive": ("automotive", "car part", "vehicle part"),
            "mounts-brackets": ("mount", "bracket", "holder"),
            "adapters-couplers": ("adapter", "adaptor", "coupler"),
            "cosplay": ("cosplay", "helmet", "mask", "wearable"),
            "electronics-cases": ("electronics case", "enclosure", "pcb case"),
            "tools-jigs": ("jig", "fixture", "tool"),
            "robotics": ("robot", "robotics"),
            "education": ("education", "educational", "science model"),
        }

        category_text = f" {source_category_text.casefold()} "
        title_text = f" {str(source_title or '').casefold()} "
        description_text = f" {str(source_description or '').casefold()} "
        scores: dict[str, int] = {}
        for slug, phrases in aliases.items():
            if slug not in valid:
                continue
            score = 0
            for phrase in phrases:
                token = str(phrase or "").casefold().strip()
                if not token:
                    continue
                pattern = rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])"
                if re.search(pattern, category_text):
                    score += 5
                if re.search(pattern, title_text):
                    score += 2
                if re.search(pattern, description_text):
                    score += 1
            if score:
                scores[slug] = score

        if not scores:
            return ""
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            return ""
        return ranked[0][0]


def _unique_missing(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for raw in values or []:
        text = str(raw or "").strip()
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        output.append(text)
    return output


def _classify_stage_missing(
    stage: str,
    missing: list[str],
) -> tuple[list[str], list[str]]:
    """Split factual defects into AI/local-fixable vs operator-owned work.

    This classification is presentation/runtime guidance only. Field ownership
    and the existing lock/readiness authorities remain unchanged.
    """
    stage = str(stage or "")
    missing = _unique_missing(list(missing or []))

    if stage in {"commerce", "publish", "specs"}:
        return [], missing

    if stage == "content":
        return missing, []

    if stage == "quick":
        ai = [
            item
            for item in missing
            if "عنوان" in item
        ]
        operator = [item for item in missing if item not in ai]
        return ai, operator

    if stage == "images":
        operator_tokens = (
            "تصویر اصلی",
            "حداقل یک تصویر",
            "انتخاب",
            "فایل محلی",
            "Creator",
            "مفقود",
            "دریافت‌نشده",
            "تأیید نهایی اپراتور",
            "ثبت مرحله",
        )
        operator = [
            item
            for item in missing
            if any(token in item for token in operator_tokens)
        ]
        ai = [item for item in missing if item not in operator]
        return ai, operator

    if stage == "slider":
        operator = [
            item
            for item in missing
            if "عکس" in item or "تصویر" in item
        ]
        ai = [item for item in missing if item not in operator]
        return ai, operator

    return [], missing


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
        row = self.db.product(int(product_id))
        output: list[dict[str, Any]] = []
        stages = state.get("stages") or {}
        for stage in STAGE_ORDER:
            current = dict(stages.get(stage) or {})
            # missing_data is the factual defect list. An empty list is
            # meaningful and must not fall through to presentation-only
            # current["missing"], which may contain the operator-confirmation
            # sentinel added for manual UI flows.
            if "missing_data" in current:
                raw_missing = current.get("missing_data") or []
            else:
                raw_missing = current.get("missing") or []
            missing = _unique_missing(list(raw_missing))

            if stage == "images" and row is not None:
                # The legacy readiness layer has one coarse "Alt تصویر" flag.
                # Qt needs exact per-image SEO truth, so always remove that coarse
                # proxy and replace it with the deterministic metadata audit below.
                # Primary/selection remain factual operator requirements.
                missing = [
                    item
                    for item in missing
                    if item != "Alt تصویر"
                ]
                detailed_image_missing = _unique_missing(
                    image_pipeline.image_metadata_missing(row)
                )
                missing = _unique_missing(
                    [*missing, *detailed_image_missing]
                )

            ai_missing, operator_missing = _classify_stage_missing(
                stage,
                missing,
            )
            readiness_value = current.get("data_ready")
            if readiness_value is None:
                # Legacy/base readiness evaluates this same fact as "ready".
                # Normalize at the Qt adapter boundary instead of requiring
                # every upstream readiness implementation to rename its key.
                readiness_value = current.get("ready")
            data_ready = bool(readiness_value) and not missing
            finalized = bool(
                current.get("finalized")
                or current.get("locked")
            )
            if finalized and data_ready:
                icon = "✅"
                status = "finalized"
            elif data_ready:
                icon = "◌"
                status = "ready"
            else:
                icon = "❌"
                status = "missing"

            output.append(
                {
                    "stage": stage,
                    "label": STAGE_LABELS.get(stage, stage),
                    "icon": icon,
                    "status": status,
                    "data_ready": data_ready,
                    "finalized": finalized,
                    "missing": missing,
                    "missing_count": len(missing),
                    "ai_fixable_missing": ai_missing,
                    "operator_missing": operator_missing,
                    "ai_fixable_count": len(ai_missing),
                    "operator_count": len(operator_missing),
                }
            )
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
        changed = any(before.get(key) != value for key, value in allowed.items())
        self.db.update_product(int(product_id), allowed)
        if (
            changed
            and str(before.get("server_id") or "").strip()
            and str(before.get("workflow_status") or "").strip().lower() == "uploaded"
        ):
            # Editing a published Product is an update, not a duplicate publish.
            # Clear the prior ready tick and require the guarded publish flow to
            # resend the same source identity/server-linked Product.
            self.db.update_product(
                int(product_id),
                {"needs_update": 1, "upload_ready": 0},
            )
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

    def prepare_ai_content_repair(self, product_id: int) -> dict[str, Any]:
        """Open only AI/content-owned finalized stages for explicit full repair."""
        product_id = int(product_id)
        row = self.db.product(product_id)
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        locks = stage_locks(row)
        opened = []
        for stage in ("quick", "content", "specs", "slider"):
            if stage in locks:
                locks.pop(stage, None)
                opened.append(stage)
        before = _row_dict(row)
        if opened:
            values: dict[str, Any] = {
                LOCK_COLUMN: json.dumps(locks, ensure_ascii=False),
            }
            if "seo_manual_approved" in _columns(self.db):
                values["seo_manual_approved"] = 0
            self.db.update_product(product_id, values)
            after = _row_dict(self.db.product(product_id))
            try:
                self.db.save_history(
                    product_id,
                    "qt_ai_content_repair_open",
                    before,
                    after,
                    "Explicit full-content AI repair opened: " + ", ".join(opened),
                )
            except Exception:
                pass
        return {
            "product_id": product_id,
            "opened_stages": opened,
        }

    def finalize(
        self,
        product_id: int,
        stage: str,
        *,
        manual_approval: bool = True,
        event_type: str = "qt_stage_finalized",
    ) -> dict[str, Any]:
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
            readiness_value = current.get("data_ready")
            if readiness_value is None:
                readiness_value = current.get("ready")
            allowed = bool(readiness_value)
            if "missing_data" in current:
                missing = list(current.get("missing_data") or [])
            else:
                missing = list(current.get("missing") or [])

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
        if (
            manual_approval
            and stage == "content"
            and "seo_manual_approved" in columns
        ):
            values["seo_manual_approved"] = 1
        if (
            manual_approval
            and stage == "specs"
            and "source_review_manual_approved" in columns
        ):
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
                event_type,
                before,
                after,
                f"Qt finalized stage={stage} manual={int(bool(manual_approval))}",
            )
        except Exception:
            pass
        return self.state(product_id)

    def auto_finalize_ready(
        self,
        product_id: int,
        stages: set[str] | None = None,
    ) -> dict[str, Any]:
        """Turn objectively complete owner-approved stages green.

        Phase49.3I.48 makes Source/License safe for automatic finalization
        because the owner explicitly approved that stage globally. Publish is
        still never auto-approved.
        """
        product_id = int(product_id)
        safe = {"quick", "commerce", "images", "content", "specs", "slider"}
        requested = (
            set(safe)
            if stages is None
            else safe & {str(stage or "") for stage in stages}
        )
        finalized: list[str] = []
        skipped: dict[str, str] = {}

        for item in self.statuses(product_id):
            stage = str(item.get("stage") or "")
            if stage not in requested:
                continue
            if bool(item.get("finalized")):
                skipped[stage] = "already_finalized"
                continue
            # statuses() already derives factual data_ready from missing_data.
            # A non-finalized ready stage can still carry the presentation-only
            # "تأیید نهایی اپراتور" sentinel in its legacy missing list. Do not
            # let that UI sentinel block the explicit full-AI auto-finalize flow.
            if not bool(item.get("data_ready")):
                skipped[stage] = "not_ready"
                continue
            try:
                self.finalize(
                    product_id,
                    stage,
                    manual_approval=False,
                    event_type="qt_stage_auto_finalized",
                )
                finalized.append(stage)
            except Exception as exc:
                skipped[stage] = str(exc)

        return {
            "product_id": product_id,
            "finalized": finalized,
            "skipped": skipped,
        }


class FilamentParityCore:
    BRAND_REGISTRY_KEY = "qt_filament_brand_registry_v1"
    COLOR_REGISTRY_KEY = "qt_filament_color_registry_v1"
    DEFAULT_COLOR_PRESETS = (
        {"name": "صورتی پاستیلی", "color_type": "solid", "color_finish": "matte", "palette_hexes": ["#F7C9D9"]},
        {"name": "آبی پاستیلی", "color_type": "solid", "color_finish": "matte", "palette_hexes": ["#BDD7F2"]},
        {"name": "سبز پاستیلی", "color_type": "solid", "color_finish": "matte", "palette_hexes": ["#C7E7D2"]},
        {"name": "کرم / Ivory", "color_type": "solid", "color_finish": "matte", "palette_hexes": ["#F2E8CF"]},
        {"name": "سفید", "color_type": "solid", "color_finish": "matte", "palette_hexes": ["#F7F7F7"]},
        {"name": "مشکی", "color_type": "solid", "color_finish": "matte", "palette_hexes": ["#161616"]},
        {"name": "قرمز + آبی", "color_type": "dual", "color_finish": "glossy", "palette_hexes": ["#D92D20", "#2563EB"]},
        {"name": "هفت‌رنگ", "color_type": "multicolor", "color_finish": "glossy", "palette_hexes": ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#06B6D4", "#3B82F6", "#A855F7"]},
    )

    def __init__(self, db) -> None:
        self.db = db
        ensure_epic49_desktop_schema(db)

    def list(self) -> list[dict[str, Any]]:
        return [dict(row) for row in list_available_material_colors(self.db)]

    def _registry(self, key: str) -> list[Any]:
        try:
            value = json.loads(str(self.db.setting(key, "[]") or "[]"))
        except Exception:
            return []
        return list(value) if isinstance(value, list) else []

    def brands(self) -> list[str]:
        names: dict[str, str] = {}
        for raw in self._registry(self.BRAND_REGISTRY_KEY):
            name = str(raw or "").strip()
            if name:
                names.setdefault(name.casefold(), name)
        for row in self.list():
            name = str(row.get("brand") or row.get("brand_name") or "").strip()
            if name:
                names.setdefault(name.casefold(), name)
        return sorted(names.values(), key=str.casefold)

    def add_brand(self, name: str) -> list[str]:
        value = str(name or "").strip()
        if not value:
            raise ValueError("نام برند خالی است.")
        values = self.brands()
        if value.casefold() not in {item.casefold() for item in values}:
            values.append(value)
        values = sorted(dict.fromkeys(values), key=str.casefold)
        self.db.set_setting(self.BRAND_REGISTRY_KEY, json.dumps(values, ensure_ascii=False))
        return values

    def delete_brand(self, name: str) -> list[str]:
        value = str(name or "").strip()
        if not value:
            return self.brands()
        if any(
            str(row.get("brand") or row.get("brand_name") or "").strip().casefold()
            == value.casefold()
            for row in self.list()
        ):
            raise ValueError("این برند روی فیلامنت فعال استفاده شده است؛ ابتدا فیلامنت‌های آن را ویرایش/غیرفعال کن.")
        values = [item for item in self.brands() if item.casefold() != value.casefold()]
        self.db.set_setting(self.BRAND_REGISTRY_KEY, json.dumps(values, ensure_ascii=False))
        return values

    def color_presets(self) -> list[dict[str, Any]]:
        presets: dict[str, dict[str, Any]] = {}
        for raw in [*self.DEFAULT_COLOR_PRESETS, *self._registry(self.COLOR_REGISTRY_KEY)]:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name") or "").strip()
            if not name:
                continue
            presets[name.casefold()] = {
                "name": name,
                "color_type": str(raw.get("color_type") or "solid"),
                "color_finish": str(raw.get("color_finish") or "matte"),
                "palette_hexes": normalize_palette_hexes(raw.get("palette_hexes") or []),
            }
        for row in self.list():
            name = str(row.get("color") or row.get("color_name") or "").strip()
            if not name or name.casefold() in presets:
                continue
            presets[name.casefold()] = {
                "name": name,
                "color_type": str(row.get("color_type") or "solid"),
                "color_finish": str(row.get("color_finish") or "matte"),
                "palette_hexes": normalize_palette_hexes(
                    row.get("palette_hex_json") or [],
                    row.get("hex_code") or "",
                    row.get("secondary_hex") or "",
                    row.get("tertiary_hex") or "",
                ),
            }
        return sorted(presets.values(), key=lambda item: str(item.get("name") or "").casefold())

    def save_color_preset(
        self,
        preset: dict[str, Any],
        *,
        previous_name: str = "",
    ) -> list[dict[str, Any]]:
        name = str(preset.get("name") or "").strip()
        palette = normalize_palette_hexes(preset.get("palette_hexes") or [])
        if not name:
            raise ValueError("نام رنگ خالی است.")
        if not palette:
            raise ValueError("حداقل یک رنگ از Color Picker انتخاب کن.")
        custom = [
            dict(item)
            for item in self._registry(self.COLOR_REGISTRY_KEY)
            if isinstance(item, dict)
            and str(item.get("name") or "").strip().casefold()
            not in {name.casefold(), str(previous_name or "").strip().casefold()}
        ]
        custom.append({
            "name": name,
            "color_type": str(preset.get("color_type") or "solid"),
            "color_finish": str(preset.get("color_finish") or "matte"),
            "palette_hexes": palette,
        })
        custom.sort(key=lambda item: str(item.get("name") or "").casefold())
        self.db.set_setting(self.COLOR_REGISTRY_KEY, json.dumps(custom, ensure_ascii=False))
        return self.color_presets()

    def delete_color_preset(self, name: str) -> list[dict[str, Any]]:
        value = str(name or "").strip().casefold()
        custom = [
            dict(item)
            for item in self._registry(self.COLOR_REGISTRY_KEY)
            if isinstance(item, dict)
            and str(item.get("name") or "").strip().casefold() != value
        ]
        self.db.set_setting(self.COLOR_REGISTRY_KEY, json.dumps(custom, ensure_ascii=False))
        return self.color_presets()

    def _materialize_image(self, data: dict[str, Any]) -> str:
        raw = str(data.get("filament_image_path") or "").strip()
        if not raw:
            return ""
        source = Path(raw).expanduser()
        if not source.is_file():
            return raw if str(data.get("_existing_image_path") or "") == raw else ""

        target_root = Path(self.db.path).resolve().parent / "filament_images"
        target_root.mkdir(parents=True, exist_ok=True)
        identity = "|".join(
            str(data.get(key) or "").strip().casefold()
            for key in ("material", "brand", "color")
        )
        digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:16]
        target = target_root / f"filament-{digest}.webp"
        try:
            if source.resolve() == target.resolve() and target.is_file():
                return str(target)
        except Exception:
            pass
        try:
            with Image.open(source) as image:
                image.load()
                image.thumbnail((640, 640), Image.Resampling.LANCZOS)
                if image.mode not in {"RGB", "RGBA"}:
                    image = image.convert("RGBA" if "transparency" in image.info else "RGB")
                image.save(target, "WEBP", quality=88, method=6)
        except Exception as exc:
            raise ValueError(f"تصویر فیلامنت معتبر نیست: {exc}") from exc
        return str(target)

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
        brand = str(data.get("brand") or data.get("brand_name") or "").strip()
        data["brand"] = brand
        data["manufacturer"] = brand
        data["_existing_image_path"] = str(base.get("filament_image_path") or "")
        image_path = self._materialize_image(data)
        saved = add_available_material_color(
            self.db,
            data.get("material") or data.get("material_name") or "",
            data.get("color") or data.get("color_name") or "",
            data.get("hex") or data.get("hex_code") or "",
            data.get("color_type") or "solid",
            data.get("secondary_hex") or "",
            data.get("tertiary_hex") or "",
            brand_name=brand,
            manufacturer_name=brand,
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
            filament_image_path=image_path,
            color_finish=str(data.get("color_finish") or "matte").strip(),
            palette_hexes=data.get("palette_hexes") or data.get("palette_hex_json") or [],
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

    @staticmethod
    def _source_dimensions_cm(data: dict[str, Any]) -> tuple[float, float, float] | None:
        """Read dimensions only from explicitly dimension-labelled source facts."""
        try:
            specs = json.loads(str(data.get("source_specs_json") or "{}"))
        except Exception:
            return None

        candidates: list[Any] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    key_text = str(key or "").casefold()
                    if (
                        any(
                            token in key_text
                            for token in (
                                "dimension",
                                "dimensions",
                                "model size",
                                "object size",
                                "part size",
                                "ابعاد",
                            )
                        )
                        and not any(
                            token in key_text
                            for token in (
                                "build",
                                "printer",
                                "bed",
                                "plate",
                                "machine",
                            )
                        )
                    ):
                        candidates.append(value)
                    if isinstance(value, (dict, list)):
                        walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(specs)
        pattern = re.compile(
            r"(\d+(?:\.\d+)?)\s*[x×*]\s*"
            r"(\d+(?:\.\d+)?)\s*[x×*]\s*"
            r"(\d+(?:\.\d+)?)\s*(mm|cm)\b",
            re.I,
        )
        for value in candidates:
            if isinstance(value, dict):
                raw_unit = str(
                    value.get("unit")
                    or value.get("units")
                    or value.get("dimension_unit")
                    or ""
                ).strip().casefold()
                numbers = [
                    _number(value.get(key), 0)
                    for key in ("x", "y", "z")
                ]
                if all(number > 0 for number in numbers):
                    factor = 0.1 if raw_unit == "mm" else 1.0
                    result = tuple(round(number * factor, 3) for number in numbers)
                    if all(0 < number < 10000 for number in result):
                        return result
            elif isinstance(value, (list, tuple)) and len(value) >= 3:
                numbers = [_number(item, 0) for item in value[:3]]
                if all(0 < number < 10000 for number in numbers):
                    return tuple(round(number, 3) for number in numbers)

            match = pattern.search(str(value or ""))
            if not match:
                continue
            factor = 0.1 if match.group(4).casefold() == "mm" else 1.0
            result = tuple(
                round(float(match.group(index)) * factor, 3)
                for index in (1, 2, 3)
            )
            if all(0 < number < 10000 for number in result):
                return result
        return None

    @staticmethod
    def _source_materials(
        data: dict[str, Any],
        filament_rows: list[dict[str, Any]],
    ) -> set[str]:
        source_text = "\n".join(
            str(data.get(key) or "")
            for key in (
                "source_description",
                "source_short_description",
                "source_specs_json",
                "source_tags_json",
                "tags_json",
                "source_category",
                "source_print_profiles_json",
            )
        ).casefold()
        matched: set[str] = set()

        material_names = sorted(
            {
                str(
                    row.get("material")
                    or row.get("material_name")
                    or ""
                ).strip()
                for row in (filament_rows or [])
                if str(
                    row.get("material")
                    or row.get("material_name")
                    or ""
                ).strip()
            },
            key=len,
            reverse=True,
        )
        for material in material_names:
            parts = [
                re.escape(part)
                for part in re.split(r"[\s_-]+", material.casefold())
                if part
            ]
            if not parts:
                continue
            expression = r"[\s_-]*".join(parts)
            # Do not treat PLA inside PLA-CF/PLA+ as an exact PLA fact.
            pattern = rf"(?<![a-z0-9+_-]){expression}(?![a-z0-9+_-])"
            if re.search(pattern, source_text, re.I):
                matched.add(material.casefold())
        return matched

    def bootstrap_from_source(
        self,
        product_id: int,
        filament_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Populate Profile 1 only from persisted source facts + real library offers.

        This never invents price, color, brand, dimensions, weight or time.
        All existing Filament Library offers for source-declared materials are
        added; actual pricing remains the operator/library authority.
        """
        product_id = int(product_id)
        row = self.db.product(product_id)
        if row is None:
            raise RuntimeError("محصول پیدا نشد.")
        if is_stage_locked(row, "commerce"):
            return {
                "changed": False,
                "reason": "commerce_locked",
                "matched_offer_count": 0,
            }

        data = _row_dict(row)
        matched_materials = self._source_materials(data, filament_rows)
        matched_offers = normalize_material_color_options(
            [
                item
                for item in (filament_rows or [])
                if str(
                    item.get("material")
                    or item.get("material_name")
                    or ""
                ).strip().casefold() in matched_materials
            ]
        )

        source_profiles = _json_list(
            data.get("source_print_profiles_json", "[]")
        )
        source_profile = next(
            (
                dict(item)
                for item in source_profiles
                if isinstance(item, dict)
            ),
            {},
        )
        weight = max(
            0.0,
            _number(data.get("estimated_weight_grams"), 0),
        )
        minutes = max(
            0,
            _integer(
                data.get("estimated_print_minutes")
                or source_profile.get("print_minutes"),
                0,
            ),
        )
        dimensions = self._source_dimensions_cm(data)

        current = self.profiles(product_id)
        changed = False

        if not current:
            # The profile ledger requires a real print duration. Refuse to
            # create a fake 60-minute placeholder when the source has no time.
            if minutes <= 0:
                return {
                    "changed": False,
                    "reason": "source_print_time_missing",
                    "materials": sorted(matched_materials),
                    "matched_offer_count": len(matched_offers),
                    "weight_grams": weight or None,
                    "print_time_minutes": None,
                    "dimensions_cm": list(dimensions) if dimensions else [],
                }

            profile_name = str(source_profile.get("name") or "").strip()
            profile: dict[str, Any] = {
                "name": profile_name or "پروفایل منبع 1",
                "size_label": profile_name,
                "production_rows": [
                    {
                        "weight_grams": weight,
                        "print_time_minutes": minutes,
                        "support_weight_grams": 0,
                    }
                ],
                "material_options": matched_offers,
                "pricing_strategy": "dynamic",
                "price_min": 0,
                "price_max": 0,
            }
            if dimensions:
                profile.update(
                    {
                        "part_length_cm": dimensions[0],
                        "part_width_cm": dimensions[1],
                        "part_height_cm": dimensions[2],
                    }
                )
            self.save_profiles(product_id, [profile])
            changed = True
        else:
            profiles = [deepcopy(item) for item in current]
            first = profiles[0]
            existing_offers = normalize_material_color_options(
                first.get("material_options") or []
            )
            offer_keys = {
                (
                    str(item.get("material") or "").casefold(),
                    str(item.get("brand") or "").casefold(),
                    str(item.get("manufacturer") or "").casefold(),
                    str(item.get("color") or "").casefold(),
                )
                for item in existing_offers
            }
            for offer in matched_offers:
                key = (
                    str(offer.get("material") or "").casefold(),
                    str(offer.get("brand") or "").casefold(),
                    str(offer.get("manufacturer") or "").casefold(),
                    str(offer.get("color") or "").casefold(),
                )
                if key not in offer_keys:
                    existing_offers.append(offer)
                    offer_keys.add(key)
                    changed = True
            first["material_options"] = existing_offers

            production = [
                normalize_production_row(item)
                for item in (first.get("production_rows") or [])
                if isinstance(item, dict)
            ]
            if production and weight > 0 and _number(
                production[0].get("weight_grams"),
                0,
            ) <= 0:
                production[0]["weight_grams"] = weight
                changed = True
            first["production_rows"] = production

            if dimensions and not any(
                _number(first.get(key), 0) > 0
                for key in (
                    "part_length_cm",
                    "part_width_cm",
                    "part_height_cm",
                )
            ):
                first["part_length_cm"] = dimensions[0]
                first["part_width_cm"] = dimensions[1]
                first["part_height_cm"] = dimensions[2]
                changed = True

            if changed:
                self.save_profiles(product_id, profiles)

        return {
            "changed": bool(changed),
            "materials": sorted(matched_materials),
            "matched_offer_count": len(matched_offers),
            "weight_grams": weight or None,
            "print_time_minutes": minutes or None,
            "dimensions_cm": list(dimensions) if dimensions else [],
        }


class ProviderCore:
    LABELS = {
        "avalai": "AvalAI",
        "openrouter": "OpenRouter",
        "google": "Google Gemini",
        "openai": "OpenAI Direct",
    }

    def __init__(self, db) -> None:
        self.db = db
        self._model_cache: dict[str, list[dict[str, Any]]] = {}
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

        if provider == "openrouter":
            selected = next(
                (
                    dict(item)
                    for item in self.cached_models(provider)
                    if str(item.get("id") or "") == model
                ),
                None,
            )
            if selected is None:
                raise ValueError(
                    "برای انتخاب Model پیش‌فرض OpenRouter ابتدا «دریافت مدل‌ها» "
                    "را بزن تا قابلیت Text/Structured آن از Catalog زنده تأیید شود."
                )
            ok, reason = product_model_compatibility(
                selected,
                require_structured=True,
            )
            if not ok:
                raise ValueError(reason)
            self.db.set_setting(
                f"ai_model_profile_{provider}",
                json.dumps(selected, ensure_ascii=False, default=str),
            )

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
        provider = str(provider or "").strip().lower()
        client = self._client(provider, key_override=key_override)
        info = rank_models(list(client.list_model_info()))
        self._model_cache[provider] = info
        return list(info)

    def cached_models(self, provider: str) -> list[dict[str, Any]]:
        return list(
            self._model_cache.get(
                str(provider or "").strip().lower(),
                [],
            )
        )

    def _saved_model_profile(
        self,
        provider: str,
        model: str,
    ) -> dict[str, Any] | None:
        provider = str(provider or "").strip().lower()
        model = str(model or "").strip()
        raw = str(
            self.db.setting(
                f"ai_model_profile_{provider}",
                "",
            )
            or ""
        ).strip()
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except Exception:
            return None
        if not isinstance(payload, dict):
            return None
        if str(payload.get("id") or "") != model:
            return None
        return enrich_model_info(payload)

    def model_info(
        self,
        provider: str,
        model: str,
        *,
        refresh: bool = False,
        key_override: str = "",
    ) -> dict[str, Any]:
        provider = str(provider or "").strip().lower()
        model = str(model or "").strip()
        info = self.cached_models(provider)
        if refresh:
            info = self.models(provider, key_override=key_override)

        selected = next(
            (
                dict(item)
                for item in info
                if str(item.get("id") or "") == model
            ),
            None,
        )
        if selected is not None:
            return enrich_model_info(selected)

        saved = self._saved_model_profile(provider, model)
        if saved is not None:
            return saved

        return enrich_model_info({"id": model, "name": model})

    def require_product_model(
        self,
        provider: str,
        model: str,
        *,
        refresh_if_unknown: bool = False,
        key_override: str = "",
    ) -> dict[str, Any]:
        provider = str(provider or "").strip().lower()
        model = str(model or "").strip()
        info = self.model_info(
            provider,
            model,
            refresh=bool(refresh_if_unknown),
            key_override=key_override,
        )

        if provider != "openrouter":
            return info

        if (
            not self.cached_models(provider)
            and self._saved_model_profile(provider, model) is None
            and not refresh_if_unknown
        ):
            raise RuntimeError(
                "قابلیت Model فعال OpenRouter در این نسخه تأیید نشده است. "
                "به تنظیمات برو، «دریافت مدل‌ها» را بزن و یک مدل Text + JSON✓ "
                "را دوباره ذخیره کن."
            )

        ok, reason = product_model_compatibility(
            info,
            require_structured=True,
        )
        if not ok:
            raise RuntimeError(reason)
        remember_model_capability(info)
        return info

    def test(
        self,
        provider: str,
        model: str = "",
        *,
        key_override: str = "",
        structured: bool = False,
    ) -> dict[str, Any]:
        provider = str(provider or "").strip().lower()
        model = str(model or "").strip()
        if structured and provider == "openrouter":
            self.require_product_model(
                provider,
                model,
                refresh_if_unknown=not bool(
                    self.cached_models(provider)
                ),
                key_override=key_override,
            )

        client = self._client(
            provider,
            model=model,
            key_override=key_override,
        )
        result = dict(client.test_connection(model))
        result["provider"] = provider
        result["model"] = str(result.get("model") or model)

        if structured:
            schema = {
                "type": "object",
                "properties": {
                    "title_fa": {"type": "string"},
                    "seo_title_fa": {"type": "string"},
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["title_fa", "seo_title_fa", "keywords"],
                "additionalProperties": False,
            }
            probe, probe_model = client.structured_response(
                instructions=(
                    "این یک تست واقعی سازگاری Product برای 3DPrintHub است. "
                    "فقط JSON معتبر برگردان. title_fa و seo_title_fa باید "
                    "فارسی طبیعی باشند و keywords باید آرایه‌ای از "
                    "کلیدواژه‌های فارسی باشد."
                ),
                input_content=[
                    {
                        "type": "input_text",
                        "text": (
                            "محصول نمونه: پایه چراغ رومیزی چاپ سه‌بعدی. "
                            "یک عنوان فارسی کوتاه و SEO فارسی تولید کن."
                        ),
                    }
                ],
                schema=schema,
                schema_name="qt_provider_product_probe",
                preferred_model=model,
            )
            if not contains_persian(
                probe.get("title_fa")
            ) or not contains_persian(
                probe.get("seo_title_fa")
            ):
                raise RuntimeError(
                    "تست واقعی Product وصل شد اما مدل خروجی فارسی "
                    "معتبر تولید نکرد."
                )
            result["structured_ok"] = True
            result["structured_model"] = probe_model
            result["structured_sample"] = str(
                probe.get("title_fa") or ""
            )[:160]

        result_model = str(
            result.get("model") or model
        )
        cached = self.cached_models(provider)
        selected = next(
            (
                dict(item)
                for item in cached
                if str(item.get("id") or "") == result_model
            ),
            enrich_model_info(
                {"id": result_model, "name": result_model}
            ),
        )
        result["model_info"] = selected
        return result

    def estimate_product_ai(
        self,
        product_id: int,
        mode: str,
        *,
        target_stage: str | None = None,
    ) -> dict[str, Any]:
        product_id = int(product_id)
        row = self.db.product(product_id)
        if row is None:
            raise RuntimeError(
                "محصول برای محاسبه هزینه پیدا نشد."
            )

        active = self.active()
        provider = str(
            active.get("provider") or ""
        ).strip().lower()
        model = str(active.get("model") or "").strip()
        if not provider or not model:
            raise RuntimeError(
                "Provider/Model فعال برای AI تنظیم نشده است."
            )

        data = _row_dict(row)
        source_text = "\n".join(
            str(data.get(key) or "")
            for key in (
                "source_title",
                "source_short_description",
                "source_description",
                "source_specs_json",
                "tags_json",
                "author_name",
                "license_name",
            )
        )
        base_tokens = estimate_text_tokens(source_text)

        if target_stage:
            input_tokens = max(900, base_tokens + 850)
            output_tokens = 850
            scope_label = STAGE_LABELS.get(
                str(target_stage),
                str(target_stage),
            )
        else:
            input_tokens = max(1400, base_tokens + 1400)
            output_tokens = 2400
            scope_label = "همه مراحل محتوایی باز"

        pricing_error = ""
        try:
            if provider == "openrouter":
                model_info = self.require_product_model(
                    provider,
                    model,
                    refresh_if_unknown=False,
                )
            else:
                model_info = self.model_info(
                    provider,
                    model,
                    refresh=False,
                )
        except Exception as exc:
            if provider == "openrouter":
                raise
            pricing_error = str(exc)
            model_info = enrich_model_info(
                {"id": model, "name": model}
            )

        estimate = estimate_request_cost(
            model_info,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        try:
            rate = float(
                str(
                    self.db.setting(
                        "ai_usd_to_toman",
                        "0",
                    )
                    or "0"
                ).replace(",", "")
            )
        except Exception:
            rate = 0.0

        usd = estimate.get("usd")
        return {
            "provider": provider,
            "model": model,
            "mode": str(mode or "data"),
            "target_stage": str(target_stage or ""),
            "scope_label": scope_label,
            "persian_label": str(
                model_info.get("persian_label")
                or "نامشخص"
            ),
            "free": bool(estimate.get("free")),
            "cost_known": bool(estimate.get("known")),
            "estimated_usd": usd,
            "estimated_toman": (
                float(usd) * rate
                if usd is not None and rate > 0
                else 0.0
            ),
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "pricing": dict(
                model_info.get("pricing") or {}
            ),
            "price_per_million": dict(
                model_info.get(
                    "price_per_million"
                )
                or {}
            ),
            "pricing_error": pricing_error,
        }

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
        if provider == "openrouter":
            self.require_product_model(
                provider,
                model,
                refresh_if_unknown=False,
            )
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
        # Qt Product AI intentionally exposes exactly the two operator-approved
        # source modes. Screenshot capture remains a separate Image-stage action.
        labels = {
            "link": "تکمیل با لینک محصول",
            "data": "تکمیل با دیتای دریافتی",
        }
        return [
            {"code": code, "label": labels[code]}
            for code in ("link", "data")
            if code in AI_SOURCE_MODES
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
