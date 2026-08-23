from __future__ import annotations

import json
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from app.openai_content import validate_content_pack
from app.phase49_3i_ai_refresh_completion import (
    DEFAULT_PRICE_TOMAN,
    build_completion_defaults,
    build_refresh_updates,
)


class _FakeDB:
    def source(self, code):
        return {"code": code, "name": "MakerWorld"}


class Phase493IAIRefreshCompletionTests(unittest.TestCase):
    def test_generic_existing_title_is_replaced_on_every_all_fields_run(self):
        row = {
            "title_fa": "محصول چاپ سه بعدی",
            "content_pack_json": "{}",
            "ai_provenance_json": "{}",
            "homepage_slider_enabled": 0,
        }
        pack = {
            "title_fa": "جا شمعی وارمر طرح کدو تنبل هالووین با سبک گوتیک",
        }
        updates = build_refresh_updates(row, pack, scope="all", base_updates={})
        self.assertEqual(updates["title_fa"], pack["title_fa"])

    def test_previous_ai_owned_title_refreshes_but_manual_override_does_not(self):
        previous = "جا شمعی قدیمی"
        row = {
            "title_fa": previous,
            "content_pack_json": json.dumps({"title_fa": previous}, ensure_ascii=False),
            "ai_provenance_json": "{}",
            "homepage_slider_enabled": 0,
        }
        pack = {"title_fa": "جا شمعی وارمر کدو تنبل هالووین"}
        updates = build_refresh_updates(row, pack, scope="all", base_updates={})
        self.assertEqual(updates["title_fa"], pack["title_fa"])

        manual = dict(row)
        manual["title_fa"] = "عنوان دستی اپراتور"
        manual["ai_provenance_json"] = json.dumps({
            "persian_content": {
                "source": "manual",
                "manual_override": True,
                "fields": ["title_fa"],
            }
        }, ensure_ascii=False)
        updates = build_refresh_updates(manual, pack, scope="all", base_updates={})
        self.assertNotIn("title_fa", updates)

    def test_completion_defaults_fill_factual_source_category_images_price_and_real_inventory(self):
        row = {
            "source_code": "makerworld",
            "source_name": "",
            "local_category_slug": "external-other",
            "content_pack_json": "{}",
            "images_json": json.dumps(["https://img/1.jpg", "https://img/2.jpg"]),
            "selected_images_json": "[]",
            "primary_image_url": "",
            "download_image_limit": 10,
            "suggested_price": 0,
            "price_min": 0,
            "price_max": 0,
            "material_options_json": "[]",
            "color_options_json": "[]",
            "product_type": "ready_product",
            "publish_as_product": 0,
        }
        app = types.SimpleNamespace(category_slug_to_label={"decor": "دکوراسیون"})
        pack = {
            "suggested_category_slug": "decor",
            "category_confidence": 0.91,
            "material_recommendations": [{"material": "PLA", "score": 90, "recommended": True, "reason_fa": "دکور"}],
        }
        inventory = {
            "material_name": "PLA",
            "color_name": "مشکی",
            "hex_code": "#000000",
            "color_type": "solid",
            "secondary_hex": "",
            "tertiary_hex": "",
        }
        with patch("app.phase49_3i_ai_refresh_completion._available_pair_for_pack", return_value=inventory):
            updates = build_completion_defaults(_FakeDB(), app, row, pack)
        self.assertEqual(updates["source_name"], "MakerWorld")
        self.assertEqual(updates["local_category_slug"], "decor")
        self.assertEqual(updates["primary_image_url"], "https://img/1.jpg")
        self.assertEqual(json.loads(updates["selected_images_json"]), ["https://img/1.jpg", "https://img/2.jpg"])
        self.assertEqual(updates["suggested_price"], DEFAULT_PRICE_TOMAN)
        self.assertEqual(updates["price_min"], DEFAULT_PRICE_TOMAN)
        self.assertEqual(updates["price_max"], DEFAULT_PRICE_TOMAN)
        self.assertEqual(json.loads(updates["material_options_json"]), ["PLA"])
        self.assertEqual(json.loads(updates["colors_json"]), ["مشکی"])
        self.assertEqual(updates["publish_as_product"], 1)

    def test_content_pack_rejects_generic_title(self):
        pack = {
            "title_fa": "محصول چاپ سه‌بعدی",
            "seo_title_fa": "محصول چاپ سه‌بعدی",
            "seo_description_fa": "توضیح",
        }
        with self.assertRaises(RuntimeError):
            validate_content_pack(pack, "Halloween Samhain Pumpkin LED goth Tealight Holder")

    def test_content_pack_accepts_specific_persian_title(self):
        pack = {
            "title_fa": "جا شمعی وارمر طرح کدو تنبل هالووین با سبک گوتیک",
            "seo_title_fa": "خرید جا شمعی کدو تنبل هالووین | چاپ سه‌بعدی",
            "seo_description_fa": "جا شمعی وارمر طرح کدو تنبل هالووین با طراحی گوتیک، مناسب دکور و سفارش چاپ سه‌بعدی.",
        }
        self.assertIs(validate_content_pack(pack, "Halloween Samhain Pumpkin LED goth Tealight Holder"), pack)

    def test_image_preflight_reuses_mature_refetch_and_no_new_extractor(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3i_ai_refresh_completion.py").read_text(encoding="utf-8")
        self.assertIn("self.refetch()", source)
        self.assertIn("normalize_image_limit", source)
        self.assertIn("SOURCE_REFRESH_TIMEOUT_SECONDS = 90", source)
        self.assertNotIn("extract_direct_link(", source)
        self.assertNotIn("collect_classic_exact(", source)
        self.assertNotIn("async_playwright", source)

    def test_runtime_composition_occurs_after_49_3i8_execution_recovery(self):
        source = (Path(__file__).resolve().parents[1] / "app" / "phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")
        execution = source.index("install_ai_execution_recovery(workspace_class, phase49_3f_workspace_module)")
        refresh = source.index("install_ai_refresh_completion(workspace_class, task_center_module)")
        self.assertLess(execution, refresh)


if __name__ == "__main__":
    unittest.main()
