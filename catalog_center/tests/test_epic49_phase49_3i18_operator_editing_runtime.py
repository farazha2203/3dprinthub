from __future__ import annotations

import json
import unittest
from pathlib import Path

from app.openai_content import validate_content_pack
from app.phase49_3i18_operator_editing_runtime import (
    PROTECTED_BUSINESS_FIELDS,
    build_batch_metadata_updates,
    build_canonical_rebuild_updates,
    is_generic_source_title,
    source_title_from_model_url,
)


class Phase493I18SourceIdentityTests(unittest.TestCase):
    def test_makerworld_model_slug_recovers_real_source_title(self):
        url = "https://makerworld.com/en/models/2845731-cake-stand?from=search#profileId-3173184"
        self.assertEqual(source_title_from_model_url(url), "Cake Stand")

    def test_generic_id_title_is_detected_but_meaningful_title_is_not(self):
        self.assertTrue(is_generic_source_title("MakerWorld model 2845731", "2845731"))
        self.assertTrue(is_generic_source_title("مدل میکرورلد 2845731", "2845731"))
        self.assertFalse(is_generic_source_title("Cake Stand", "2845731"))


class Phase493I18BatchMetadataTests(unittest.TestCase):
    def _row(self):
        return {
            "title_fa": "استند کیک",
            "source_title": "Cake Stand",
            "selected_images_json": json.dumps(["https://img/1.jpg", "https://img/2.jpg"], ensure_ascii=False),
        }

    def test_batch_numbering_alt_and_operator_overrides_preserve_legal_source_fields(self):
        existing = [
            {
                "source_url": "https://img/1.jpg",
                "creator": "silvis.kreativ",
                "source_page_url": "https://makerworld.com/en/models/2845731-cake-stand",
                "license_name": "Standard Digital File License",
                "license_url": "https://makerworld.com/terms",
            },
            {
                "source_url": "https://img/2.jpg",
                "creator": "silvis.kreativ",
                "source_page_url": "https://makerworld.com/en/models/2845731-cake-stand",
                "license_name": "Standard Digital File License",
                "license_url": "https://makerworld.com/terms",
            },
        ]
        updates = build_batch_metadata_updates(
            self._row(),
            existing,
            filename_base="cake-stand-3d-print",
            alt_template="{title} - نمای {nn} از {total}",
            title_template="{title} - تصویر {n}",
            caption_template="خرید {title}",
            keywords_text="استند کیک\nچاپ سه بعدی استند کیک",
            apply_filename=True,
            apply_alt=True,
            apply_title=True,
            apply_caption=True,
            apply_keywords=True,
        )
        metadata = json.loads(updates["image_metadata_json"])
        self.assertEqual(metadata[0]["seo_filename"], "cake-stand-3d-print-01.webp")
        self.assertEqual(metadata[1]["seo_filename"], "cake-stand-3d-print-02.webp")
        self.assertEqual(metadata[0]["alt_text"], "استند کیک - نمای 01 از 2")
        self.assertEqual(metadata[1]["title"], "استند کیک - تصویر 2")
        self.assertEqual(metadata[0]["caption"], "خرید استند کیک")
        self.assertEqual(metadata[0]["keywords"], ["استند کیک", "چاپ سه بعدی استند کیک"])
        for item in metadata:
            self.assertEqual(item["creator"], "silvis.kreativ")
            self.assertEqual(item["license_name"], "Standard Digital File License")
            self.assertIn("source_page_url", item)
            self.assertTrue(item["operator_override"])
            self.assertEqual(
                set(item["operator_override_fields"]),
                {"seo_filename", "alt_text", "title", "caption", "keywords"},
            )
        self.assertEqual(
            json.loads(updates["image_alt_texts_json"]),
            ["استند کیک - نمای 01 از 2", "استند کیک - نمای 02 از 2"],
        )

    def test_only_checked_metadata_fields_change(self):
        existing = [{"source_url": "https://img/1.jpg", "title": "Keep", "caption": "Keep caption"}]
        row = dict(self._row())
        row["selected_images_json"] = json.dumps(["https://img/1.jpg"])
        updates = build_batch_metadata_updates(
            row,
            existing,
            alt_template="{title} - نمای {n}",
            apply_alt=True,
        )
        item = json.loads(updates["image_metadata_json"])[0]
        self.assertEqual(item["title"], "Keep")
        self.assertEqual(item["caption"], "Keep caption")
        self.assertEqual(item["operator_override_fields"], ["alt_text"])


class Phase493I18CanonicalRebuildTests(unittest.TestCase):
    def _pack(self, title="استند کیک"):
        return {
            "title_fa": title,
            "short_description_fa": "استند کیک مناسب سرو و نمایش کیک.",
            "description_fa": "استند کیک برای قرار دادن و نمایش کیک و شیرینی طراحی شده است.",
            "use_description_fa": "برای سرو و نمایش کیک استفاده می‌شود.",
            "categories_fa": ["لوازم آشپزخانه"],
            "specs_fa": [],
            "tags_fa": ["استند کیک"],
            "hashtags_fa": ["استند_کیک"],
            "target_keywords_fa": ["خرید استند کیک", "قیمت استند کیک", "چاپ سه بعدی استند کیک"],
            "suggested_category_slug": "decor",
            "category_confidence": 0.8,
            "seo_title_fa": "خرید استند کیک چاپ سه بعدی",
            "seo_description_fa": "استند کیک چاپ سه بعدی برای سرو و نمایش کیک.",
            "sales_bullets": ["مناسب سرو کیک"],
            "social_caption_fa": "استند کیک چاپ سه بعدی",
            "image_alt_texts": ["استند کیک - نمای اصلی"],
            "content_notes": [],
            "use_case_class": "home_decor",
            "material_recommendations": [],
            "homepage_slider_seo": {
                "title_fa": "استند کیک",
                "description_fa": "استند کیک برای سرو و نمایش کیک",
                "image_alt_fa": "استند کیک چاپ سه بعدی",
                "button_text_fa": "مشاهده محصول",
                "focus_keyword_fa": "استند کیک",
            },
        }

    def test_operator_canonical_title_mismatch_is_rejected(self):
        with self.assertRaises(RuntimeError):
            validate_content_pack(self._pack("پایه دکوراتیو"), "Cake Stand", "استند کیک")

    def test_operator_canonical_title_is_accepted_and_preserved_exactly(self):
        pack = self._pack("استند کیک")
        result = validate_content_pack(pack, "Cake Stand", "استند کیک")
        self.assertEqual(result["title_fa"], "استند کیک")

    def test_rebuild_overwrites_only_editorial_not_business_legal_or_publish(self):
        updates = build_canonical_rebuild_updates(
            self._pack(),
            "استند کیک",
            provider="avalai",
            model="gpt-test",
        )
        self.assertEqual(updates["title_fa"], "استند کیک")
        self.assertEqual(updates["ai_provider"], "avalai")
        self.assertEqual(updates["ai_model"], "gpt-test")
        self.assertFalse(PROTECTED_BUSINESS_FIELDS.intersection(updates))


class Phase493I18SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.runtime = (root / "app" / "phase49_3i18_operator_editing_runtime.py").read_text(encoding="utf-8")
        cls.composition = (root / "app" / "phase49_3i_local_qa_hotfix.py").read_text(encoding="utf-8")

    def test_runtime_uses_exact_49_3i17_active_ai_and_no_provider_loop(self):
        self.assertIn("active_ai_config(self.app, require_key=True)", self.runtime)
        self.assertNotIn("PROVIDER_ORDER", self.runtime)
        self.assertNotIn("for provider in", self.runtime)

    def test_clipboard_contract_covers_windows_shortcuts_and_right_click(self):
        for token in (
            '"<Control-c>"',
            '"<Control-v>"',
            '"<Control-x>"',
            '"<Control-a>"',
            '"<Control-Insert>"',
            '"<Shift-Insert>"',
            '"<Button-3>"',
        ):
            self.assertIn(token, self.runtime)
        self.assertIn("tk.Entry", self.runtime)
        self.assertIn("tk.Text", self.runtime)
        self.assertIn("ttk.Entry", self.runtime)
        self.assertIn("ttk.Combobox", self.runtime)

    def test_49_3i18_composes_after_single_active_ai(self):
        old = self.composition.index("install_single_active_ai_runtime")
        new = self.composition.index("install_operator_editing_runtime")
        self.assertLess(old, new)

    def test_source_guard_is_additive_and_does_not_replace_non_generic_title(self):
        self.assertIn("original = bulk_discovery.build_product_payload", self.runtime)
        self.assertIn("is_generic_source_title", self.runtime)
        self.assertIn("data[\"source_title\"] = recovered", self.runtime)


if __name__ == "__main__":
    unittest.main()
