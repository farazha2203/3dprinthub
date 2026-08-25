from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.phase49_3i21_observable_ai_link_refresh import (
    DEFAULT_AI_TIMEOUT_SECONDS,
    grounded_description,
    normalized_source_facts,
    configured_ai_timeout_seconds,
)


class Phase493I21ObservableAILinkRefreshTests(unittest.TestCase):
    def test_normalized_source_facts_keeps_product_identity_and_drops_secrets(self):
        facts = normalized_source_facts(
            {
                "source_title": "Ribbed cake stand, cookie platter",
                "source_description": "Cake and cookie display stand",
                "source_specs": {"diameter": "200 mm"},
                "source_tags": ["cake", "stand"],
                "author_name": "Maker",
                "license_name": "Standard Digital File License",
                "api_key": "must-not-leak",
                "authorization": "Bearer must-not-leak",
                "raw_html": "<html>must-not-leak</html>",
            },
            "https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter",
        )
        self.assertEqual(facts["source_title"], "Ribbed cake stand, cookie platter")
        self.assertEqual(facts["source_specs"]["diameter"], "200 mm")
        self.assertIn("makerworld.com/en/models/2896217", facts["source_url"])
        self.assertNotIn("api_key", facts)
        self.assertNotIn("authorization", facts)
        self.assertNotIn("raw_html", facts)

    def test_grounded_description_sends_url_and_facts_to_ai(self):
        url = "https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter"
        text = grounded_description(
            "A ribbed cake stand.",
            url,
            {"source_title": "Ribbed cake stand, cookie platter", "source_tags": ["cake", "stand"]},
        )
        self.assertIn("SOURCE_URL: " + url, text)
        self.assertIn("Ribbed cake stand, cookie platter", text)
        self.assertIn("اگر داده‌ای در منبع نیست حدس نزن", text)

    def test_timeout_is_bounded_and_has_safe_default(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("CATALOG_AI_TIMEOUT_SECONDS", None)
            self.assertEqual(configured_ai_timeout_seconds(), DEFAULT_AI_TIMEOUT_SECONDS)
        with patch.dict(os.environ, {"CATALOG_AI_TIMEOUT_SECONDS": "999"}):
            self.assertEqual(configured_ai_timeout_seconds(), 120)
        with patch.dict(os.environ, {"CATALOG_AI_TIMEOUT_SECONDS": "2"}):
            self.assertEqual(configured_ai_timeout_seconds(), 20)
        with patch.dict(os.environ, {"CATALOG_AI_TIMEOUT_SECONDS": "bad"}):
            self.assertEqual(configured_ai_timeout_seconds(), DEFAULT_AI_TIMEOUT_SECONDS)


if __name__ == "__main__":
    unittest.main()
