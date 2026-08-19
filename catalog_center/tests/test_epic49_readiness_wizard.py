from __future__ import annotations

import unittest
from pathlib import Path

from app.openai_content import CONTENT_SCHEMA
from app.phase49_readiness_wizard import (
    STAGE_LABELS,
    build_sales_keywords,
    evaluate_readiness,
    selected_color_names,
    selected_material_names,
)


ROOT = Path(__file__).resolve().parents[1]


def ready_row(**overrides):
    row = {
        "title_fa": "گکو مفصلی سه بعدی",
        "short_description_fa": "مدل مفصلی دکوراتیو مناسب سفارش چاپ سه بعدی.",
        "description_fa": "توضیح کامل فارسی محصول برای فروشگاه.",
        "local_category_slug": "decor",
        "product_type": "ready_product",
        "source_url": "https://example.com/model/123",
        "selected_images_json": '["https://example.com/a.jpg"]',
        "primary_image_url": "https://example.com/a.jpg",
        "material_options_json": '["PLA","PETG"]',
        "color_options_json": '[{"name":"مشکی","color_type":"solid"},{"name":"شفاف","color_type":"transparent"}]',
        "material_color_options_json": "[]",
        "materials_json": "[]",
        "colors_json": "[]",
        "final_price": 420000,
        "price_min": 420000,
        "price_max": 520000,
        "suggested_price": 420000,
        "seo_title_fa": "خرید گکو مفصلی سه بعدی",
        "seo_description_fa": "خرید و سفارش گکو مفصلی سه بعدی با انتخاب متریال و رنگ.",
        "keywords_json": '["خرید گکو مفصلی سه بعدی","سفارش گکو سه بعدی","قیمت گکو مفصلی"]',
        "image_alt_texts_json": '["گکو مفصلی سه بعدی چاپ شده"]',
        "homepage_slider_enabled": 0,
        "homepage_slider_title_fa": "",
        "homepage_slider_description_fa": "",
        "homepage_slider_alt_text": "",
        "homepage_slider_focus_keyword": "",
        "homepage_slider_image_url": "",
        "approved_for_sale": 1,
        "publish_as_product": 1,
        "commercial_status": "allowed",
    }
    row.update(overrides)
    return row


class Phase493AReadinessWizardTests(unittest.TestCase):
    def test_complete_product_is_production_ready(self):
        state = evaluate_readiness(ready_row())
        self.assertTrue(state["production_ready"])
        self.assertEqual([], state["missing"])
        self.assertTrue(all(stage["ready"] for stage in state["stages"].values()))
        self.assertEqual(["PLA", "PETG"], state["materials"])
        self.assertEqual(["مشکی", "شفاف"], state["colors"])

    def test_missing_seo_marks_content_stage_red(self):
        state = evaluate_readiness(
            ready_row(seo_title_fa="", seo_description_fa="", keywords_json="[]")
        )
        self.assertFalse(state["production_ready"])
        self.assertFalse(state["stages"]["content"]["ready"])
        self.assertIn("SEO Title فارسی", state["stages"]["content"]["missing"])
        self.assertIn("SEO Description فارسی", state["stages"]["content"]["missing"])
        self.assertIn("عبارت‌های هدف SEO", state["stages"]["content"]["missing"])

    def test_slider_fields_are_required_only_when_slider_enabled(self):
        without_slider = evaluate_readiness(ready_row(homepage_slider_enabled=0))
        self.assertTrue(without_slider["production_ready"])

        with_slider = evaluate_readiness(ready_row(homepage_slider_enabled=1))
        self.assertFalse(with_slider["production_ready"])
        self.assertIn("عنوان اسلایدر", with_slider["stages"]["publish"]["missing"])
        self.assertIn("عکس اسلایدر", with_slider["stages"]["publish"]["missing"])

        completed = evaluate_readiness(
            ready_row(
                homepage_slider_enabled=1,
                homepage_slider_title_fa="خرید گکو مفصلی سه بعدی",
                homepage_slider_description_fa="معرفی کوتاه فارسی برای اسلایدر.",
                homepage_slider_alt_text="گکو مفصلی سه بعدی",
                homepage_slider_focus_keyword="خرید گکو مفصلی",
                homepage_slider_image_url="https://example.com/a.jpg",
            )
        )
        self.assertTrue(completed["production_ready"])

    def test_materials_and_colors_come_from_real_operator_options(self):
        row = ready_row()
        self.assertEqual(["PLA", "PETG"], selected_material_names(row))
        self.assertEqual(["مشکی", "شفاف"], selected_color_names(row))

    def test_sales_keyword_fallback_uses_title_and_real_options(self):
        values = build_sales_keywords(ready_row(keywords_json="[]"))
        self.assertIn("خرید گکو مفصلی سه بعدی", values)
        self.assertIn("سفارش گکو مفصلی سه بعدی", values)
        self.assertIn("گکو مفصلی سه بعدی PLA", values)
        self.assertIn("گکو مفصلی سه بعدی شفاف", values)
        self.assertLessEqual(len(values), 12)

    def test_ai_schema_supports_sales_targets_but_not_fake_material_color_fields(self):
        props = CONTENT_SCHEMA["properties"]
        self.assertIn("target_keywords_fa", props)
        # Read the source contract from disk rather than inspecting a runtime-patched
        # method. Persian/translation guards intentionally wrap enrich_product during
        # full discovery, so inspect.getsource() made this test order-dependent.
        source = (ROOT / "app" / "openai_content.py").read_text(encoding="utf-8")
        self.assertIn('"selected_materials"', source)
        self.assertIn('"selected_colors"', source)
        self.assertIn("Never invent", source)
        self.assertIn("target_keywords_fa", source)

    def test_launcher_installs_wizard_after_dual_publish_and_option_picker(self):
        launch = (ROOT / "launch.py").read_text(encoding="utf-8")
        self.assertIn("install_readiness_workspace(ProductWorkspace)", launch)
        self.assertIn("install_readiness_app(app_module.App)", launch)
        self.assertIn("EPIC49_READINESS_WIZARD=ENABLED", launch)
        self.assertIn("EPIC49_SEO_REFERENCE_SYNC=ENABLED", launch)
        self.assertLess(
            launch.index("install_dual_publish_workspace(ProductWorkspace)"),
            launch.index("install_readiness_workspace(ProductWorkspace)"),
        )
        self.assertLess(
            launch.index("install_material_color_picker(ProductWorkspace)"),
            launch.index("install_readiness_workspace(ProductWorkspace)"),
        )

    def test_wizard_maps_every_workspace_section(self):
        self.assertEqual(
            {"quick", "commerce", "images", "content", "specs", "publish"},
            set(STAGE_LABELS),
        )


if __name__ == "__main__":
    unittest.main()
