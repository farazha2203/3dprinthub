from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from PySide6.QtWidgets import QApplication, QPushButton

from app.db import Database
from app.instagram_publish import _public_source_url
from app.phase49_3i33_ai_core import (
    MANUAL_VISUAL_EDITORIAL_SCHEMA,
    manual_visual_editorial_facts,
)
from app.phase49_3i49_site_publish import _batch_source_url
from qt6.kernel import build_kernel
from qt6.pages import ProductsPage
from qt6.product_wizard import ProductWizardPage


class Phase50A2ZW5ManualProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp.name) / "catalog.sqlite3")
        self.kernel = build_kernel(self.db)
    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def _manual(self, *, reference: str = "https://example.com/reference"):
        return self.kernel.products.create_manual_product(
            title="پایه رومیزی طراحی داخلی",
            notes="محصول طراحی و تولید داخلی برای نگهداری وسیله روی میز.",
            category_slug="external-other",
            reference_url=reference,
        )

    def test_manual_product_has_immutable_local_identity_and_no_crawl_row(self):
        row = self._manual()
        self.assertEqual(row["source_code"], "manual")
        self.assertTrue(str(row["external_id"]).startswith("manual-"))
        self.assertEqual(
            row["source_url"],
            f"manual://product/{row['external_id']}",
        )
        self.assertEqual(row["title_fa"], "پایه رومیزی طراحی داخلی")
        self.assertEqual(row["source_title"], "پایه رومیزی طراحی داخلی")
        self.assertEqual(row["local_category_slug"], "external-other")
        provenance = json.loads(row["source_provenance_json"])
        self.assertEqual(provenance["kind"], "manual_product")
        self.assertEqual(
            provenance["reference_url"],
            "https://example.com/reference",
        )
        discovered = self.db.conn.execute(
            "SELECT COUNT(*) FROM discovered_urls WHERE source_code='manual'"
        ).fetchone()[0]
        self.assertEqual(discovered, 0)
        self.assertFalse(row.get("estimated_weight_grams"))
        self.assertFalse(row.get("estimated_print_minutes"))
        self.assertFalse(str(row.get("dimensions") or "").strip())
        self.assertFalse(str(row.get("license_name") or "").strip())
        self.assertEqual(
            json.loads(row.get("source_print_profiles_json") or "[]"),
            [],
        )
        self.assertEqual(
            self.kernel.products.external_reference_url(row),
            "https://example.com/reference",
        )

    def test_manual_local_images_reuse_canonical_image_core(self):
        row = self._manual(reference="")
        source = Path(self.temp.name) / "owner-photo.png"
        Image.new("RGB", (320, 240), "white").save(source)
        result = self.kernel.images.add_local_files(
            int(row["id"]),
            [str(source)],
        )
        self.assertEqual(len(result["added"]), 1)
        refreshed = self.kernel.products.get(int(row["id"])) or {}
        selected = json.loads(
            refreshed.get("selected_images_json") or "[]"
        )
        self.assertEqual(len(selected), 1)
        self.assertTrue(selected[0].startswith("local://"))
        preferred = self.kernel.images.preferred_local_path(refreshed)
        self.assertTrue(preferred and Path(preferred).is_file())
    def test_manual_products_page_and_wizard_keep_mature_controls(self):
        opened = []
        page = ProductsPage(
            self.db,
            opened.append,
            kernel=self.kernel,
            navigate=lambda _route: None,
        )
        row = self._manual()
        wizard = ProductWizardPage(self.db, kernel=self.kernel)
        try:
            self.assertEqual(page.manual_product_btn.text(), "➕ محصول دستی")
            wizard.load_product(int(row["id"]))
            self.assertFalse(wizard.ai_source.isEnabled())
            self.assertFalse(wizard.source_profile_btn.isEnabled())
            self.assertFalse(wizard.source_filament_map_btn.isEnabled())
            self.assertFalse(wizard.production_estimate_btn.isEnabled())
            self.assertTrue(wizard.product_source_btn.isEnabled())
            self.assertIn("لینک مرجع", wizard.product_source_btn.text())
            labels = {
                button.text()
                for button in wizard.findChildren(QPushButton)
            }
            self.assertIn("پروفایل جدید", labels)
            self.assertIn("ویرایش پروفایل", labels)
        finally:
            wizard.close()
            page.close()

    def test_manual_ai_is_saved_data_editorial_only(self):
        row = self._manual()
        product_id = int(row["id"])
        with patch(
            "qt6.parity_core.active_ai_config",
            return_value=("avalai", "secret", "model-x"),
        ), patch(
            "qt6.parity_core.orchestrate_once",
            return_value={"product_id": product_id},
        ) as orchestrate:
            result = self.kernel.providers.execute_product_ai(
                product_id,
                "link",
            )
        self.assertEqual(result["product_id"], product_id)
        args = orchestrate.call_args.args
        kwargs = orchestrate.call_args.kwargs
        self.assertEqual(args[2], "data")
        self.assertEqual(
            kwargs["target_stages"],
            {"quick", "content", "slider"},
        )

        with self.assertRaisesRegex(RuntimeError, "وزن|مشخصات|مجوز"):
            self.kernel.providers.execute_product_ai(
                product_id,
                "data",
                target_stage="specs",
            )
        with self.assertRaisesRegex(RuntimeError, "تخمین AI"):
            self.kernel.providers.estimate_product_production(product_id)

    def test_manual_postprocess_does_not_grant_license_or_bootstrap_profiles(self):
        row = self._manual()
        product_id = int(row["id"])
        before = self.kernel.products.get(product_id) or {}
        with patch.object(
            type(self.kernel),
            "_backfill_slider_core",
            return_value={"changed": False, "changed_fields": []},
        ), patch.object(
            self.kernel.stages,
            "auto_finalize_ready",
            return_value={"finalized": []},
        ):
            result = self.kernel.postprocess_full_product_ai(
                product_id,
                {"changed_fields": []},
            )
        after = self.kernel.products.get(product_id) or {}
        self.assertTrue(result["manual_editorial_only"])
        self.assertEqual(
            result["target_stages"],
            ["quick", "content", "slider"],
        )
        self.assertEqual(
            int(after.get("source_license_owner_approved") or 0),
            int(before.get("source_license_owner_approved") or 0),
        )
        self.assertEqual(
            after.get("sales_profiles_json"),
            before.get("sales_profiles_json"),
        )
        self.assertEqual(
            after.get("estimated_weight_grams"),
            before.get("estimated_weight_grams"),
        )
        self.assertEqual(
            after.get("estimated_print_minutes"),
            before.get("estimated_print_minutes"),
        )

    def test_manual_public_reference_never_leaks_manual_uri(self):
        row = self._manual()
        self.assertEqual(
            _batch_source_url(self.db, row),
            "https://example.com/reference",
        )
        self.assertEqual(
            _public_source_url(row),
            "https://example.com/reference",
        )

        no_reference = self.kernel.products.create_manual_product(
            title="محصول بدون مرجع",
            reference_url="",
        )
        batch_url = _batch_source_url(self.db, no_reference)
        self.assertTrue(batch_url.startswith(("https://", "http://")))
        self.assertNotIn("manual://", batch_url)
        self.assertEqual(_public_source_url(no_reference), "")
    def test_manual_visual_ai_schema_has_no_technical_fact_fields(self):
        forbidden = {
            "weight",
            "dimension",
            "print_minutes",
            "material",
            "license",
            "filament",
        }
        properties = set(
            MANUAL_VISUAL_EDITORIAL_SCHEMA["properties"]
        )
        self.assertFalse(properties & forbidden)

        image_path = Path(self.temp.name) / "visual.jpg"
        Image.new("RGB", (120, 90), "white").save(image_path)
        fake_json = json.dumps(
            {
                "object_description": "یک پایه رومیزی سفید",
                "appearance_notes": ["فرم ساده و گوشه‌های گرد"],
                "visible_use_cues": ["قرارگیری روی سطح میز"],
                "uncertainties": ["کاربرد دقیق از تصویر قطعی نیست"],
            },
            ensure_ascii=False,
        )
        with patch(
            "app.phase49_3i33_ai_core.AIProviderClient.choose_model",
            return_value="gpt-test",
        ), patch(
            "app.phase49_3i33_ai_core._json_request",
            return_value={"ok": True},
        ) as request_call, patch(
            "app.phase49_3i33_ai_core.response_output_text",
            return_value=fake_json,
        ):
            result = manual_visual_editorial_facts(
                "openai",
                "secret",
                "gpt-test",
                [image_path],
                1,
            )
        self.assertIn("پایه", result["object_description"])
        payload = request_call.call_args.kwargs["payload"]
        content = payload["input"][0]["content"]
        self.assertTrue(
            any(item.get("type") == "input_image" for item in content)
        )
        self.assertNotIn(
            "estimated_weight_grams",
            payload["text"]["format"]["schema"]["properties"],
        )


if __name__ == "__main__":
    unittest.main()
