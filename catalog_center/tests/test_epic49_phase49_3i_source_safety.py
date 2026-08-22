from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace

from app.phase49_3i_source_safety import install


class DummyPage:
    def __init__(self):
        self.source_title = "Cake 蛋糕 🧁"
        self.source_description = "Useful stand Привет"
        self.author_name = "Designer 用户"
        self.license_name = "CC BY"
        self.source_category = "Kitchen 厨房"
        self.source_categories = ["Home 家", "Kitchen"]
        self.tags = ["cake", "蛋糕", "🧁"]
        self.specs = {"Material 材料": "PLA 白色", "Size": "25mm"}


class DummyExtractor:
    async def extract(self, *args, **kwargs):
        return DummyPage()


async def dummy_direct(*args, **kwargs):
    return {
        "source_title": "Cake Stand 蛋糕",
        "source_description": "For cakes 🧁",
        "source_url": "https://example.test/产品?id=1",
        "title_fa": "استند کیک",
    }


def dummy_parse(*args, **kwargs):
    return {
        "source_title": "Parsed 产品",
        "source_url": "https://example.test/model/产品",
        "description_fa": "توضیح فارسی",
    }


class Phase493ISourceSafetyTests(unittest.TestCase):
    def test_install_wraps_page_direct_and_module_level_crawler_parser(self):
        page_module = SimpleNamespace(RichPageExtractor=DummyExtractor, extract_direct_link=dummy_direct)
        crawler_module = SimpleNamespace(parse_product=dummy_parse)
        install(page_module, crawler_module)

        page = asyncio.run(page_module.RichPageExtractor().extract("x", "y"))
        self.assertEqual(page.source_title, "Cake")
        self.assertNotIn("蛋", page.source_description)
        self.assertEqual(page.specs.get("Size"), "25mm")

        direct = asyncio.run(page_module.extract_direct_link("x", "y"))
        self.assertEqual(direct["source_title"], "Cake Stand")
        self.assertEqual(direct["source_url"], "https://example.test/产品?id=1")
        self.assertEqual(direct["title_fa"], "استند کیک")

        parsed = crawler_module.parse_product("html", "url")
        self.assertEqual(parsed["source_title"], "Parsed")
        self.assertEqual(parsed["source_url"], "https://example.test/model/产品")
        self.assertEqual(parsed["description_fa"], "توضیح فارسی")


if __name__ == "__main__":
    unittest.main()
