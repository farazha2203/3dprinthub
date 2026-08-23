from __future__ import annotations

import unittest

from app.phase49_3i19_source_identity import (
    canonical_source_title,
    canonicalize_candidate,
    is_generic_source_title,
    makerworld_title_from_url,
)


CAKE_STAND = "https://makerworld.com/en/models/2845731-cake-stand?from=search#profileId-3173184"
RIBBED = "https://makerworld.com/en/models/2896217-ribbed-cake-stand-cookie-platter?from=search#profileId-3236824"


class Phase493I19SourceIdentityTests(unittest.TestCase):
    def test_makerworld_slug_recovers_exact_cake_stand_identity(self):
        self.assertEqual(makerworld_title_from_url(CAKE_STAND), "Cake Stand")
        self.assertEqual(
            makerworld_title_from_url(RIBBED),
            "Ribbed Cake Stand Cookie Platter",
        )

    def test_generic_model_number_never_becomes_authoritative_title(self):
        title = canonical_source_title("Model 2896217", RIBBED, "2896217")
        self.assertEqual(title, "Ribbed Cake Stand Cookie Platter")
        self.assertFalse(is_generic_source_title(title, "2896217"))

    def test_makerworld_model_number_variant_is_rejected(self):
        self.assertTrue(is_generic_source_title("MakerWorld model 2896217", "2896217"))
        self.assertTrue(is_generic_source_title("مدل میکرورلد 2896217", "2896217"))

    def test_valid_exact_page_title_wins_over_url_slug(self):
        title = canonical_source_title(
            "old generic",
            RIBBED,
            "2896217",
            candidates=("Ribbed Cake Stand & Cookie Platter",),
        )
        self.assertEqual(title, "Ribbed Cake Stand & Cookie Platter")

    def test_candidate_is_repaired_before_database_upsert(self):
        candidate = canonicalize_candidate(
            {
                "source_code": "makerworld",
                "external_id": "2896217",
                "source_url": RIBBED,
                "source_title": "Model 2896217",
            }
        )
        self.assertEqual(candidate["source_title"], "Ribbed Cake Stand Cookie Platter")
        self.assertEqual(candidate["source_url"], RIBBED)
        self.assertEqual(candidate["external_id"], "2896217")


if __name__ == "__main__":
    unittest.main()
