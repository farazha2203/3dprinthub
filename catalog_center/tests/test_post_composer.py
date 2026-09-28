import unittest
from catalog_center.app.post_composer import POST_STYLES, mock_openrouter_post, validate_post_metadata

class PostComposerTests(unittest.TestCase):
    PRODUCT = {"title_fa": "چراغ رومیزی Driftbloom", "source_title": "Driftbloom Table Lamp", "source_url": "https://example.com/product/1"}

    def test_all_twelve_styles_are_available_to_radio(self):
        self.assertEqual(len(POST_STYLES), 12)
        self.assertEqual(len({key for key, _ in POST_STYLES}), 12)

    def test_mock_response_has_no_invention_and_link_mention_metadata(self):
        response = mock_openrouter_post(self.PRODUCT, POST_STYLES[0][0], "برای @brand دیدن کنید")
        self.assertTrue(validate_post_metadata(response, self.PRODUCT))
        self.assertEqual(response["links"], [self.PRODUCT["source_url"]])
        self.assertEqual(response["mentions"], ["@brand"])
        self.assertTrue(response["no_invention"])

    def test_missing_title_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "POST_SOURCE_TITLE_REQUIRED"):
            mock_openrouter_post({}, POST_STYLES[0][0])

if __name__ == "__main__":
    unittest.main()
