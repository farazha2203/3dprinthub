from __future__ import annotations

import asyncio
import json
import sqlite3
import tempfile
import types
import unittest
from pathlib import Path

from PIL import Image

from app.phase49_3c_ai_recovery import _deterministic_fill, missing_commerce_fields
from app.phase49_3c_image_pipeline import (
    MAX_SOURCE_IMAGES,
    cap_unique_urls,
    finalize_selected_images,
    install_extractor_patch,
    planned_seo_filename,
    strict_existing_image_mapping,
    strict_local_image,
)


class Phase493CImageIdentityTests(unittest.TestCase):
    def _image(self, path: Path, value: int):
        image = Image.new("RGB", (64, 64), (value, value, value))
        image.save(path)

    def test_url_cap_is_ten_and_canonical_duplicates_do_not_repeat(self):
        urls = [f"https://cdn.example.test/image-{i}.jpg?utm_source=x" for i in range(1, 15)]
        urls.insert(2, "https://cdn.example.test/image-1.jpg")
        result = cap_unique_urls(urls)
        self.assertEqual(len(result), MAX_SOURCE_IMAGES)
        self.assertEqual(MAX_SOURCE_IMAGES, 10)
        self.assertEqual(len({item.split("?")[0] for item in result}), 10)

    def test_exact_manifest_mapping_prevents_visual_delete_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            first = images / "001.jpg"
            second = images / "002.jpg"
            self._image(first, 10)
            self._image(second, 200)
            url_a = "https://cdn.example.test/a.jpg"
            url_b = "https://cdn.example.test/b.jpg"
            (root / "page_extract.json").write_text(
                json.dumps({
                    "images": [
                        {"url": url_a, "local_file": str(second)},
                        {"url": url_b, "local_file": str(first)},
                    ]
                }),
                encoding="utf-8",
            )
            row = {"local_dir": str(root)}
            self.assertEqual(Path(strict_local_image(row, url_a)), second)
            self.assertEqual(Path(strict_local_image(row, url_b)), first)
            mapping = strict_existing_image_mapping(root, [url_b, url_a])
            self.assertEqual(mapping[url_b], first)
            self.assertEqual(mapping[url_a], second)

    def test_no_index_guess_when_url_has_no_exact_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            first = images / "001.jpg"
            self._image(first, 50)
            (root / "page_extract.json").write_text(
                json.dumps({"images": [{"url": "https://cdn.example.test/known.jpg", "local_file": str(first)}]}),
                encoding="utf-8",
            )
            row = {"local_dir": str(root)}
            self.assertEqual(strict_local_image(row, "https://cdn.example.test/missing.jpg"), "")

    def test_seo_name_is_human_readable_not_numeric(self):
        row = {"id": 9, "source_title": "Fanart Solidarity Bear", "title_fa": "خرس همبستگی"}
        name = planned_seo_filename(row, 1)
        self.assertTrue(name.startswith("fanart-solidarity-bear-3d-print-"))
        self.assertTrue(name.endswith(".webp"))
        self.assertNotEqual(name, "001.webp")

    def test_finalize_deduplicates_content_keeps_sources_and_preserves_third_party_credit(self):
        class FakeDB:
            def __init__(self, row):
                self.row = row
                self.conn = sqlite3.connect(":memory:")
                self.conn.row_factory = sqlite3.Row
                self.conn.execute(
                    "CREATE TABLE products(id INTEGER PRIMARY KEY, image_metadata_json TEXT NOT NULL DEFAULT '[]')"
                )
                self.conn.commit()

            def product(self, product_id):
                return self.row if int(product_id) == int(self.row["id"]) else None

            def update_product(self, product_id, values):
                self.row.update(values)

            def setting(self, key, default=""):
                return "QA Operator" if key == "operator_name" else default

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root / "images"
            images.mkdir()
            one = images / "one.jpg"
            two = images / "two.jpg"
            self._image(one, 100)
            two.write_bytes(one.read_bytes())
            url1 = "https://cdn.example.test/a.jpg"
            url2 = "https://cdn.example.test/b.jpg"
            (root / "page_extract.json").write_text(
                json.dumps({
                    "images": [
                        {"url": url1, "local_file": str(one)},
                        {"url": url2, "local_file": str(two)},
                    ]
                }),
                encoding="utf-8",
            )
            row = {
                "id": 7,
                "local_dir": str(root),
                "source_title": "Fanart Solidarity Bear",
                "title_fa": "خرس همبستگی",
                "short_description_fa": "مدل تزئینی برای چاپ سه‌بعدی",
                "seo_title_fa": "خرید فایل سه‌بعدی خرس همبستگی",
                "source_url": "https://makerworld.com/model/7",
                "source_code": "makerworld",
                "source_name": "MakerWorld",
                "author_name": "Original Designer",
                "license_name": "Creator License",
                "license_url": "https://example.test/license",
                "commercial_status": "allowed",
                "images_json": json.dumps([url1, url2]),
                "selected_images_json": json.dumps([url1, url2]),
                "primary_image_url": url1,
                "image_alt_texts_json": json.dumps(["خرس همبستگی - نمای اصلی", "خرس همبستگی - نمای دوم"]),
                "keywords_json": json.dumps(["خرید خرس سه بعدی"]),
                "tags_fa_json": json.dumps(["خرس", "دکور"]),
                "hashtags_fa_json": json.dumps(["#چاپ_سه_بعدی"]),
                "image_metadata_json": "[]",
            }
            db = FakeDB(row)
            try:
                result = finalize_selected_images(db, 7)
            finally:
                db.conn.close()
            self.assertEqual(result["kept"], 1)
            self.assertEqual(result["duplicates"], 1)
            self.assertTrue(one.is_file())
            self.assertTrue(two.is_file())
            metadata = json.loads(row["image_metadata_json"])
            self.assertEqual(len(metadata), 1)
            self.assertEqual(metadata[0]["creator"], "Original Designer")
            self.assertEqual(metadata[0]["copyright_holder"], "Original Designer")
            self.assertEqual(metadata[0]["publisher"], "3DPrintHub")
            self.assertTrue(metadata[0]["seo_filename"].startswith("fanart-solidarity-bear-3d-print-"))
            self.assertTrue(Path(metadata[0]["final_local_file"]).is_file())


class Phase493CExtractorContractTests(unittest.TestCase):
    def test_extractor_wrapper_clamps_requested_limit_to_ten(self):
        calls = []

        async def original(url, output_dir, profile_dir, *, headed=True, download_images=True, image_limit=60):
            calls.append(image_limit)
            return {
                "local_dir": str(output_dir),
                "images_json": json.dumps([f"https://cdn.example.test/{i}.jpg" for i in range(30)]),
                "selected_images_json": json.dumps([f"https://cdn.example.test/{i}.jpg" for i in range(30)]),
                "primary_image_url": "https://cdn.example.test/0.jpg",
                "downloaded_image_files": [],
            }

        module = types.SimpleNamespace(extract_direct_link=original)
        wrapped = install_extractor_patch(module)
        with tempfile.TemporaryDirectory() as tmp:
            result = asyncio.run(
                wrapped(
                    "https://example.test/product",
                    Path(tmp),
                    Path(tmp) / "profile",
                    image_limit=80,
                )
            )
        self.assertEqual(calls, [10])
        self.assertLessEqual(len(json.loads(result["images_json"])), 10)
        self.assertLessEqual(len(json.loads(result["selected_images_json"])), 10)


class Phase493CAICompletenessTests(unittest.TestCase):
    def test_commerce_fallback_restores_editorial_fields_without_faking_price_or_license(self):
        source = {
            "source_title": "Fanart Solidarity Bear",
            "source_description": "A decorative solidarity bear model.",
            "source_categories": ["Decor"],
            "selected_materials": ["PLA"],
            "selected_colors": ["White"],
        }
        result = _deterministic_fill({}, source, image_count=3)
        for key in (
            "title_fa",
            "short_description_fa",
            "description_fa",
            "tags_fa",
            "hashtags_fa",
            "target_keywords_fa",
            "seo_title_fa",
            "seo_description_fa",
            "sales_bullets",
            "social_caption_fa",
            "image_alt_texts",
            "material_recommendations",
            "homepage_slider_seo",
        ):
            self.assertTrue(result.get(key), key)
        self.assertEqual(len(result["image_alt_texts"]), 3)
        self.assertNotIn("final_price", result)
        self.assertNotIn("commercial_status", result)
        self.assertEqual(missing_commerce_fields(result, 3), [])


class Phase493CSourceContractTests(unittest.TestCase):
    def test_operator_recovery_has_live_debounce_missing_map_and_both_ai_actions(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "app" / "phase49_3c_operator_recovery.py").read_text(encoding="utf-8")
        for token in (
            "موارد ناقص زنده",
            "after(180",
            "<KeyRelease>",
            "<<ComboboxSelected>>",
            "✨ دستیار AI همین مرحله",
            "✨ تکمیل هوشمند همه فیلدهای AI",
            "🖼 نهایی‌سازی SEO تصاویر",
            "نیازمند اپراتور",
            "انتشار/صف متوقف شد",
        ):
            self.assertIn(token, text)

    def test_launcher_exposes_phase49_3c_markers(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "launch.py").read_text(encoding="utf-8")
        for marker in (
            "EPIC49_3C_LIVE_READINESS=ENABLED",
            "EPIC49_3C_STAGE_AI=ENABLED",
            "EPIC49_3C_IMAGE_ID_SAFE_DELETE=ENABLED",
            "EPIC49_3C_IMAGE_LIMIT_10=ENABLED",
            "EPIC49_3C_IMAGE_SEO_METADATA=ENABLED",
            "EPIC49_3C_AI_COMPLETENESS_RECOVERY=ENABLED",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
