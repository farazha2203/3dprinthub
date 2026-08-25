from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app import phase49_3i25_product_first_workflow as phase


class Phase493I25ProductFirstWorkflowTests(unittest.TestCase):
    def test_content_seo_is_first_operator_stage(self):
        self.assertEqual(phase._TEXT_FIRST_SECTIONS[0][0], "content")
        self.assertEqual(phase._TEXT_FIRST_SECTIONS[1][0], "quick")
        self.assertEqual(phase._TEXT_FIRST_SECTIONS[2][0], "images")

    def test_source_facts_preserve_weight_and_print_minutes(self):
        parsed = {
            "source_title": "Scallop Cake Tray 24cm Dessert Stand",
            "estimated_weight_grams": 186.5,
            "estimated_print_minutes": 742,
        }
        facts = phase.normalized_source_facts(
            parsed,
            "https://makerworld.com/en/models/2801606-scallop-cake-tray-24cm-dessert-stand#profileId-3116679",
        )
        self.assertEqual(facts["estimated_weight_grams"], 186.5)
        self.assertEqual(facts["estimated_print_minutes"], 742.0)

    def test_makerworld_exact_profile_weight_wins(self):
        data = {
            "props": {
                "pageProps": {
                    "instances": [
                        {"id": 111, "weight": 42},
                        {"id": 3116679, "weight": 186.5},
                    ]
                }
            }
        }
        html = (
            '<html><body><script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(data)
            + "</script></body></html>"
        )
        value = phase.makerworld_profile_weight_from_html(
            html,
            "https://makerworld.com/en/models/2801606-scallop-cake-tray-24cm-dessert-stand#profileId-3116679",
        )
        self.assertEqual(value, 186.5)

    def test_non_makerworld_or_missing_profile_does_not_guess_weight(self):
        self.assertIsNone(phase.makerworld_profile_weight_from_html("<html></html>", "https://example.com/p/1"))
        self.assertIsNone(
            phase.makerworld_profile_weight_from_html(
                "<html></html>",
                "https://makerworld.com/en/models/2801606-scallop-cake-tray-24cm-dessert-stand",
            )
        )

    def test_first_incomplete_uses_new_business_order(self):
        state = {
            "stages": {
                "content": {"ready": True},
                "quick": {"ready": False},
                "images": {"ready": False},
            }
        }
        self.assertEqual(phase._first_incomplete(state), "quick")

    def test_source_contract_contains_no_layered_save_before_ai(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        start = source.index("def _run_link_refresh")
        end = source.index("def _publication_gate_or_ai")
        implementation = source[start:end]
        self.assertNotIn("workspace.save(", implementation)
        self.assertNotIn("self.save(", implementation)
        self.assertIn('"estimated_weight_grams"', implementation)
        self.assertIn("gallery_page_size = 100", source)
        self.assertIn("index // 5", source)
        self.assertIn("index % 5", source)

    def test_runtime_logging_is_append_only_without_finite_rotation(self):
        runtime_logging = Path(phase.__file__).with_name("runtime_logging.py").read_text(encoding="utf-8")
        self.assertIn('logging.FileHandler(log_path, mode="a"', runtime_logging)
        self.assertNotIn("RotatingFileHandler", runtime_logging)
        self.assertNotIn("backupCount=", runtime_logging)

    def test_diagnostics_uses_dedicated_sqlite_connection(self):
        diagnostics = Path(phase.__file__).with_name("phase49_diagnostics.py").read_text(encoding="utf-8")
        self.assertIn("sqlite3.connect(path, check_same_thread=False, timeout=30)", diagnostics)
        self.assertIn("PRAGMA busy_timeout=30000", diagnostics)
        self.assertIn("Historical audit rows are preserved", diagnostics)

    def test_hidden_model_discovery_guard_is_operator_explicit(self):
        source = Path(phase.__file__).read_text(encoding="utf-8")
        self.assertIn("hidden_model_scan_blocked", source)
        self.assertIn("_phase49_3i25_explicit_model_until", source)
        self.assertIn("_phase49_3d_open_model_picker", source)
        self.assertIn("load_ai_models", source)


if __name__ == "__main__":
    unittest.main()
