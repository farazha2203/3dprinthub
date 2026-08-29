from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from app.db import Database
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.phase49_3f_workspace import ensure_schema as ensure_pricing_schema
from app.phase49_3i33_ai_core import title_quality_guard
from app.phase49_3i34_profile_matrix import ensure_schema as ensure_profile_schema
from app.phase49_3i35_operator_ledger import ensure_schema as ensure_ledger_schema
from app.phase49_3i36_stage_finalization import (
    LOCK_COLUMN,
    STAGE_ORDER,
    content_manual_minimum,
    field_stage,
    filter_ai_updates,
    install_database,
    persist_stage_from_ui,
    stage_locks,
    hydrate_ai_state,
)


ROOT = Path(__file__).resolve().parents[1]


class _Var:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class _Text:
    def __init__(self, value=""):
        self.value = value

    def get(self, *_args):
        return self.value


class _Settings:
    def __init__(self, values):
        self.values = dict(values)

    def setting(self, key, default=""):
        return self.values.get(key, default)


class Phase493I36StageFinalizationTests(unittest.TestCase):
    def _db(self, path):
        class LockedDatabase(Database):
            pass

        install_database(LockedDatabase)
        db = LockedDatabase(path)
        # Match the real ProductWorkspace construction order. The commerce
        # confirmation test writes price_min/price_max/pricing_strategy, which
        # are owned by the Epic49 desktop + 3F pricing schemas rather than the
        # minimal Database bootstrap.
        ensure_epic49_desktop_schema(db)
        ensure_pricing_schema(db)
        ensure_profile_schema(db)
        ensure_ledger_schema(db)
        db.upsert_product({
            "source_code": "makerworld",
            "external_id": "twistmas-test",
            "source_url": "https://makerworld.com/en/models/twistmas-test",
            "source_title": "Twistmas Tree",
            "title_fa": "درخت کریسمس اسپیرال",
            "short_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال.",
            "description_fa": "این محصول یک درخت کریسمس اسپیرال برای چاپ سه‌بعدی است.",
        })
        product_id = int(db.products()[0]["id"])
        return db, product_id

    def test_seven_canonical_operator_stages_remain_present(self):
        self.assertEqual(
            STAGE_ORDER,
            ("quick", "commerce", "images", "content", "specs", "slider", "publish"),
        )

    def test_quick_stage_persists_only_visible_title_and_category(self):
        with tempfile.TemporaryDirectory() as temporary:
            db, product_id = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                db.update_product(product_id, {
                    "product_type": "custom_order",
                    "dimensions": "قدیمی-مرحله-دو",
                    "use_case_class": "کاربری-قدیمی-مرحله-دو",
                })
                workspace = SimpleNamespace(
                    db=db,
                    product_id=product_id,
                    app=SimpleNamespace(
                        category_label_to_slug={"دکور و لوازم خانه": "home-decor"}
                    ),
                    content_title_fa=_Var("درخت کریسمس اسپیرال"),
                    title_fa=_Var(""),
                    category_var=_Var("دکور و لوازم خانه"),
                    product_type_var=_Var("محصول آماده"),
                    dimensions_var=_Var("20 × 20 × 30 cm"),
                    use_case_class_var=_Var("دکوراسیون"),
                )
                persist_stage_from_ui(workspace, "quick")
                row = db.product(product_id)
                self.assertEqual(row["local_category_slug"], "home-decor")
                self.assertEqual(row["product_type"], "custom_order")
                self.assertEqual(row["dimensions"], "قدیمی-مرحله-دو")
                self.assertEqual(row["use_case_class"], "کاربری-قدیمی-مرحله-دو")
            finally:
                db.close()

    def test_commerce_stage_persists_visible_product_type_and_dimensions(self):
        with tempfile.TemporaryDirectory() as temporary:
            db, product_id = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                workspace = SimpleNamespace(
                    db=db,
                    product_id=product_id,
                    app=SimpleNamespace(),
                    product_type_var=_Var("سفارش سفارشی"),
                    dimensions_var=_Var("20 × 30 × 40 cm"),
                    price_min_var=_Var("500000"),
                    price_max_var=_Var("500000"),
                    stock_var=_Var("0"),
                    lead_min_var=_Var("1"),
                    lead_max_var=_Var("3"),
                    pricing_strategy_var=_Var("fixed"),
                    availability_var=_Var("تولید پس از سفارش"),
                    has_3d_file_var=_Var(0),
                )
                persist_stage_from_ui(workspace, "commerce")
                row = db.product(product_id)
                self.assertEqual(row["product_type"], "custom_order")
                self.assertEqual(row["dimensions"], "20 × 30 × 40 cm")
            finally:
                db.close()

    def test_images_stage_persist_builds_current_metadata_before_confirmation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db, product_id = self._db(root / "catalog.sqlite3")
            try:
                product_dir = root / "product"
                image_dir = product_dir / "images"
                image_dir.mkdir(parents=True, exist_ok=True)
                image_path = image_dir / "selected.png"
                Image.new("RGB", (320, 240), "white").save(image_path)
                url = "local://selected.png"
                db.update_product(product_id, {
                    "local_dir": str(product_dir),
                    "images_json": json.dumps([url], ensure_ascii=False),
                    "selected_images_json": json.dumps([url], ensure_ascii=False),
                    "primary_image_url": url,
                    "image_alt_texts_json": json.dumps(["نمای مدل آزمایشی"], ensure_ascii=False),
                })
                workspace = SimpleNamespace(db=db, product_id=product_id)
                persist_stage_from_ui(workspace, "images")
                from app import phase49_3c_image_pipeline as image_pipeline
                self.assertEqual(
                    image_pipeline.image_metadata_missing(db.product(product_id)),
                    [],
                )
            finally:
                db.close()

    def test_specs_stage_keeps_historical_visible_source_and_license_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            db, product_id = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                workspace = SimpleNamespace(
                    db=db,
                    product_id=product_id,
                    source_url=_Var("https://makerworld.com/en/models/twistmas-test"),
                    spec_source_url=_Var(""),
                    source_name_var=_Var("Maker Designer"),
                    license_var=_Var("allowed"),
                )
                columns = {
                    item["name"] for item in db.conn.execute("PRAGMA table_info(products)")
                }
                self.assertIn("technical_summary_fa", columns)
                persist_stage_from_ui(workspace, "specs")
                row = db.product(product_id)
                self.assertEqual(row["source_name"], "Maker Designer")
                self.assertEqual(row["commercial_status"], "allowed")
                self.assertEqual(
                    row["source_url"],
                    "https://makerworld.com/en/models/twistmas-test",
                )
            finally:
                db.close()

    def test_finalization_is_not_counted_as_missing_product_data(self):
        source = (ROOT / "app" / "phase49_3i36_stage_finalization.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('state["pending_finalization"]', source)
        self.assertIn('get("missing_data", [])', source)
        self.assertNotIn(
            'for item in ordered[stage].get("missing", [])',
            source,
        )

    def test_locked_stage_blocks_database_overwrite_but_other_stage_can_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            db, product_id = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                db.update_product(product_id, {
                    LOCK_COLUMN: json.dumps({"quick": {"locked": True}}, ensure_ascii=False),
                })
                db.update_product(product_id, {
                    "title_fa": "نام خراب AI",
                    "description_fa": "توضیح جدید مجاز چون Content باز است",
                })
                row = db.product(product_id)
                self.assertEqual(row["title_fa"], "درخت کریسمس اسپیرال")
                self.assertEqual(row["description_fa"], "توضیح جدید مجاز چون Content باز است")
            finally:
                db.close()

    def test_unlock_allows_operator_revision_again(self):
        with tempfile.TemporaryDirectory() as temporary:
            db, product_id = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                db.update_product(product_id, {
                    LOCK_COLUMN: json.dumps({"quick": {"locked": True}}, ensure_ascii=False),
                })
                db.update_product(product_id, {
                    LOCK_COLUMN: "{}",
                })
                db.update_product(product_id, {"title_fa": "نام اصلاح‌شده اپراتور"})
                self.assertEqual(db.product(product_id)["title_fa"], "نام اصلاح‌شده اپراتور")
                self.assertEqual(stage_locks(db.product(product_id)), {})
            finally:
                db.close()

    def test_finalized_commerce_protects_registered_profile_ledger(self):
        with tempfile.TemporaryDirectory() as temporary:
            db, product_id = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                original = [{"key": "20cm", "name": "۲۰ سانت", "production_rows": [{"weight_grams": 100}]}]
                db.update_product(product_id, {
                    "sales_profile_ledger_json": json.dumps(original, ensure_ascii=False),
                    "sales_profiles_json": json.dumps(original, ensure_ascii=False),
                })
                db.update_product(product_id, {
                    LOCK_COLUMN: json.dumps({"commerce": {"locked": True}}, ensure_ascii=False),
                })
                db.update_product(product_id, {
                    "sales_profile_ledger_json": "[]",
                    "sales_profiles_json": "[]",
                    "price_min": 0,
                })
                row = db.product(product_id)
                self.assertEqual(json.loads(row["sales_profile_ledger_json"]), original)
                self.assertEqual(json.loads(row["sales_profiles_json"]), original)
            finally:
                db.close()

    def test_ai_never_owns_commerce_and_respects_finalized_content(self):
        row = {
            LOCK_COLUMN: json.dumps({"quick": {"locked": True}, "content": {"locked": True}}, ensure_ascii=False),
        }
        updates, blocked = filter_ai_updates(row, {
            "title_fa": "عنوان AI",
            "description_fa": "توضیح AI",
            "sales_profile_ledger_json": "[]",
            "price_min": 100,
            "source_title": "Fresh source title",
        })
        self.assertNotIn("title_fa", updates)
        self.assertNotIn("description_fa", updates)
        self.assertNotIn("sales_profile_ledger_json", updates)
        self.assertNotIn("price_min", updates)
        self.assertEqual(updates["source_title"], "Fresh source title")
        self.assertIn("sales_profile_ledger_json", blocked)

    def test_content_manual_finalization_uses_real_persian_and_seo_fields(self):
        ok, missing = content_manual_minimum({
            "title_fa": "درخت کریسمس اسپیرال",
            "short_description_fa": "مدل دکوراتیو مناسب چاپ سه‌بعدی",
            "description_fa": "",
            "seo_title_fa": "دانلود مدل درخت کریسمس اسپیرال",
            "seo_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال برای دکور کریسمس",
        })
        self.assertTrue(ok, missing)

        bad, bad_missing = content_manual_minimum({
            "title_fa": "Twistmas Tree",
            "short_description_fa": "3D model",
            "seo_title_fa": "",
            "seo_description_fa": "",
        })
        self.assertFalse(bad)
        self.assertTrue(bad_missing)

    def test_twistmas_transliteration_is_rejected_but_semantic_title_passes(self):
        with self.assertRaises(RuntimeError):
            title_quality_guard("Twistmas Tree", "تویست‌ماس تری")
        title_quality_guard("Twistmas Tree", "درخت کریسمس اسپیرال")
        title_quality_guard("Twistmas Tree", "درخت کریسمس مارپیچ")

    def test_ai_hydration_restores_saved_provider_model_and_key_without_network(self):
        app = SimpleNamespace(
            db=_Settings({
                "ai_provider": "avalai",
                "ai_model_avalai": "gpt-5-chat",
                "ai_model": "gpt-5-chat",
            }),
            ai_provider=_Var(""),
            ai_model=_Var(""),
            _phase49_3d_active_provider=_Var(""),
            _ai_hub_model_vars={"avalai": _Var(""), "openai": _Var("")},
            _ai_hub_key_vars={"avalai": _Var(""), "openai": _Var("")},
        )
        with patch(
            "app.phase49_3i36_stage_finalization.secure_secrets.get_provider_key",
            side_effect=lambda provider: {"avalai": "stored-key"}.get(provider, ""),
        ), patch(
            "app.phase49_3i36_stage_finalization.audit_event",
            return_value=None,
        ):
            hydrate_ai_state(app)

        self.assertEqual(app.ai_provider.get(), "avalai")
        self.assertEqual(app.ai_model.get(), "gpt-5-chat")
        self.assertEqual(app._phase49_3d_active_provider.get(), "avalai")
        self.assertEqual(app._ai_hub_model_vars["avalai"].get(), "gpt-5-chat")
        self.assertEqual(app._ai_hub_key_vars["avalai"].get(), "stored-key")

    def test_no_product_ai_entrypoint_full_saves_workspace_before_request(self):
        checks = {
            "app/phase49_readiness_wizard.py": "def _phase49_complete_missing",
            "app/phase49_3e_ai_task_center.py": "def _phase49_3e_run_ai",
            "app/phase49_3i18_operator_editing.py": "def rebuild",
            "app/phase49_3f_workspace.py": "def _phase49_3f_refresh_source_and_generate",
        }
        for relative, marker in checks.items():
            source = (ROOT / relative).read_text(encoding="utf-8")
            start = source.index(marker)
            next_def = source.find("\n    def ", start + len(marker))
            block = source[start:next_def if next_def >= 0 else len(source)]
            self.assertNotIn("self.save(silent=True)", block, relative)

    def test_stage_field_ownership_keeps_profile_and_slider_separate(self):
        self.assertEqual(field_stage("sales_profile_ledger_json"), "commerce")
        self.assertEqual(field_stage("sales_profiles_json"), "commerce")
        self.assertEqual(field_stage("material_color_options_json"), "commerce")
        self.assertEqual(field_stage("homepage_slider_title_fa"), "slider")
        self.assertEqual(field_stage("seo_description_fa"), "content")
        self.assertEqual(field_stage("source_url"), "specs")


if __name__ == "__main__":
    unittest.main()
