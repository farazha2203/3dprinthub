from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.db import Database
from app.phase49_3i33_ai_core import title_quality_guard
from app.phase49_3i35_operator_ledger import ensure_schema as ensure_ledger_schema
from app.phase49_3i36_stage_finalization import (
    LOCK_COLUMN,
    STAGE_ORDER,
    content_manual_minimum,
    field_stage,
    filter_ai_updates,
    install_database,
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
        ensure_ledger_schema(db)
        product_id = db.upsert_product({
            "source_code": "makerworld",
            "external_id": "twistmas-test",
            "source_url": "https://makerworld.com/en/models/twistmas-test",
            "source_title": "Twistmas Tree",
            "title_fa": "درخت کریسمس اسپیرال",
            "short_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال.",
            "description_fa": "این محصول یک درخت کریسمس اسپیرال برای چاپ سه‌بعدی است.",
        })
        return db, int(product_id)

    def test_seven_canonical_operator_stages_remain_present(self):
        self.assertEqual(
            STAGE_ORDER,
            ("quick", "commerce", "images", "content", "specs", "slider", "publish"),
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
            LOCK_COLUMN: json.dumps({"content": {"locked": True}}, ensure_ascii=False),
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
        self.assertEqual(
            title_quality_guard("Twistmas Tree", "درخت کریسمس اسپیرال"),
            "درخت کریسمس اسپیرال",
        )
        self.assertEqual(
            title_quality_guard("Twistmas Tree", "درخت کریسمس مارپیچ"),
            "درخت کریسمس مارپیچ",
        )

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
            block = source[start:start + 2200]
            self.assertNotIn("self.save(silent=True)", block, relative)

    def test_stage_field_ownership_keeps_profile_and_slider_separate(self):
        self.assertEqual(field_stage("sales_profile_ledger_json"), "commerce")
        self.assertEqual(field_stage("material_color_options_json"), "commerce")
        self.assertEqual(field_stage("homepage_slider_title_fa"), "slider")
        self.assertEqual(field_stage("seo_description_fa"), "content")
        self.assertEqual(field_stage("source_url"), "specs")


if __name__ == "__main__":
    unittest.main()
