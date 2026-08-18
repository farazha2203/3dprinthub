from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class _DB:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE products(id INTEGER PRIMARY KEY)")
        self.conn.execute("INSERT INTO products(id) VALUES(1)")
        self.conn.commit()


class Epic49MaterialColorPickerTests(unittest.TestCase):
    def test_launcher_routes_ux87_to_epic49_workspace(self):
        source = (ROOT / "launch.py").read_text(encoding="utf-8")
        self.assertIn("from app.product_workspace_epic49 import ProductWorkspace", source)
        self.assertIn("ux87_shell.ProductWorkspace = ProductWorkspace", source)
        self.assertIn("install_material_color_picker(ProductWorkspace)", source)
        self.assertIn("UX87_EPIC49_WORKSPACE_ROUTING=ENABLED", source)
        self.assertIn("EPIC49_MATERIAL_COLOR_PICKER=ENABLED", source)

    def test_schema_adds_independent_material_and_color_payloads(self):
        from app.epic49_desktop_schema import ensure_epic49_desktop_schema

        db = _DB()
        ensure_epic49_desktop_schema(db)
        product_columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(products)")}
        self.assertIn("material_options_json", product_columns)
        self.assertIn("color_options_json", product_columns)
        color_columns = {row["name"] for row in db.conn.execute("PRAGMA table_info(available_material_colors)")}
        self.assertTrue({"color_type", "secondary_hex", "tertiary_hex"}.issubset(color_columns))

    def test_transparent_and_multicolor_metadata_roundtrip(self):
        from app.epic49_desktop_schema import add_available_material_color, list_available_material_colors

        db = _DB()
        add_available_material_color(db, "PETG", "شفاف", "#FFFFFF", "transparent")
        add_available_material_color(db, "PLA", "آبی طلایی", "#0066FF", "dual", "#D4AF37")
        rows = list_available_material_colors(db)
        transparent = next(row for row in rows if row["color_name"] == "شفاف")
        dual = next(row for row in rows if row["color_name"] == "آبی طلایی")
        self.assertEqual(transparent["color_type"], "transparent")
        self.assertEqual(dual["color_type"], "dual")
        self.assertEqual(dual["secondary_hex"], "#D4AF37")

    def test_normalizers_keep_backward_compatibility_and_rich_metadata(self):
        from app.epic49_desktop_schema import (
            normalize_color_options,
            normalize_material_color_options,
            normalize_material_options,
        )

        self.assertEqual(normalize_material_options('["PLA","PETG","PLA"]'), ["PLA", "PETG"])
        colors = normalize_color_options(json.dumps([
            {"name": "شفاف", "color_type": "transparent", "hex": "#FFFFFF"},
            {"name": "دو رنگ", "color_type": "dual", "hex": "#000000", "secondary_hex": "#FFFFFF"},
        ], ensure_ascii=False))
        self.assertEqual(colors[0]["color_type"], "transparent")
        self.assertEqual(colors[1]["secondary_hex"], "#FFFFFF")
        pairs = normalize_material_color_options(json.dumps([
            {"material": "PLA", "color": "دو رنگ", "color_type": "dual", "hex": "#000000", "secondary_hex": "#FFFFFF"}
        ], ensure_ascii=False))
        self.assertEqual(pairs[0]["material"], "PLA")
        self.assertEqual(pairs[0]["color_type"], "dual")


if __name__ == "__main__":
    unittest.main()
