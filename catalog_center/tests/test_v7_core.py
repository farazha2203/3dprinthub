from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from app.db import Database
from app.page_extractor import parse_page_snapshot, detect_source_code, detect_external_id


class RichExtractorTests(unittest.TestCase):
    def test_product_jsonld_images_price_weight_files(self):
        snapshot = {
            "source_url": "https://example.com/product/abc",
            "final_url": "https://example.com/product/abc",
            "title": "Fallback title",
            "metas": {
                "og:title": "OG title",
                "og:image": "/img/hero-1600.jpg",
                "twitter:image": "/img/twitter-1200.jpg",
            },
            "json_ld": [json.dumps({
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Adjustable Gear Housing",
                "description": "Printable replacement part",
                "image": ["/img/product-front.jpg", "/img/product-back.jpg"],
                "weight": {"@type": "QuantitativeValue", "value": 0.42, "unitText": "kg"},
                "offers": {"@type": "Offer", "price": "12.50", "priceCurrency": "USD"}
            })],
            "dom_images": [
                {"currentSrc": "https://example.com/assets/logo.png", "alt": "site logo", "naturalWidth": 500, "naturalHeight": 200},
                {"srcset": "/img/p-400.jpg 400w, /img/p-1600.jpg 1600w", "alt": "Adjustable Gear Housing", "naturalWidth": 1600, "naturalHeight": 1200},
            ],
            "picture_sources": [],
            "links": [
                {"href": "/files/gear.stl", "text": "Download STL"},
                {"href": "/license", "text": "Creative Commons License"},
            ],
            "body_text": "Dimensions: 120 x 80 x 30 mm. Print time: 2h 15m"
        }
        page = parse_page_snapshot(snapshot)
        self.assertEqual(page.source_title, "Adjustable Gear Housing")
        self.assertEqual(page.source_price, 12.5)
        self.assertEqual(page.source_currency, "USD")
        self.assertEqual(page.estimated_weight_grams, 420.0)
        self.assertEqual(page.estimated_print_minutes, 135)
        self.assertEqual(page.specs["dimensions"]["x"], 120.0)
        self.assertIn("https://example.com/files/gear.stl", page.file_links)
        urls = [image.url for image in page.images]
        self.assertIn("https://example.com/img/product-front.jpg", urls)
        self.assertIn("https://example.com/img/p-1600.jpg", urls)
        self.assertNotIn("https://example.com/assets/logo.png", urls)

    def test_site_detection(self):
        self.assertEqual(detect_source_code("https://makerworld.com/en/models/12345"), "makerworld")
        self.assertEqual(detect_external_id("https://makerworld.com/en/models/12345", "makerworld"), "12345")
        self.assertEqual(detect_source_code("https://shop.example.ir/product/x"), "site_shop_example_ir")


class DatabaseUpgradeTests(unittest.TestCase):
    def test_v7_columns_and_upload_queue(self):
        with tempfile.TemporaryDirectory() as td:
            db = Database(Path(td) / "catalog.sqlite3")
            cols = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
            required = {
                "selected_images_json", "selected_file_links_json", "source_specs_json",
                "source_price", "source_currency", "workflow_status", "upload_ready", "custom_notes"
            }
            self.assertTrue(required.issubset(cols))
            db.upsert_product({
                "source_code": "site_example_com",
                "external_id": "abc",
                "source_url": "https://example.com/p/abc",
                "source_title": "Example",
                "images_json": json.dumps(["https://example.com/a.jpg"]),
                "selected_images_json": json.dumps(["https://example.com/a.jpg"]),
                "upload_ready": 1,
                "publish_as_product": 1,
                "approved_for_sale": 1,
                "commercial_status": "allowed",
                "workflow_status": "approved",
            })
            self.assertEqual(len(db.upload_queue()), 1)
            self.assertEqual(len(db.exportable()), 1)
            db.update_product(1, {"commercial_status": "review"})
            self.assertEqual(len(db.upload_queue()), 1)
            self.assertEqual(len(db.exportable()), 0)
            db.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
