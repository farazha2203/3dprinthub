from __future__ import annotations

import copy
import json
import unittest
from types import SimpleNamespace

from app.phase49_3c_persian_content import (
    has_persian_editorial_text_for_source,
    install_readiness,
)


def _base_state():
    return {
        "stages": {
            "quick": {"label": "۱. اطلاعات پایه", "ready": True, "missing": []},
            "commerce": {"label": "۲. سفارش، قیمت و گزینه‌ها", "ready": True, "missing": []},
            "images": {"label": "۳. تصاویر", "ready": True, "missing": []},
            "content": {"label": "۴. محتوا و SEO", "ready": True, "missing": []},
            "specs": {"label": "۵. منبع و مجوز", "ready": True, "missing": []},
            "slider": {"label": "۶. اسلایدر صفحه اصلی", "ready": True, "missing": []},
            "publish": {"label": "۷. بررسی و انتشار", "ready": True, "missing": []},
        },
        "missing": [],
        "production_ready": True,
    }


def _row(**overrides):
    row = {
        "source_title": "Flexi Gecko",
        "title_fa": "گکوی مفصلی فلکسی (Flexi Gecko)",
        "short_description_fa": "مدل گکوی مفصلی فلکسی برای چاپ سه‌بعدی.",
        "description_fa": "این مدل گکوی مفصلی برای چاپ سه‌بعدی و استفاده دکوراتیو طراحی شده است.",
        "use_description": "برای دکور، هدیه و نمونه چاپ مفصلی مناسب است.",
        "seo_title_fa": "خرید گکوی مفصلی فلکسی",
        "seo_description_fa": "خرید و سفارش گکوی مفصلی فلکسی با چاپ سه‌بعدی دقیق.",
        "keywords_json": json.dumps(["گکوی مفصلی", "چاپ سه‌بعدی", "مدل مفصلی"], ensure_ascii=False),
        "tags_fa_json": json.dumps(["گکو", "مدل مفصلی"], ensure_ascii=False),
        "hashtags_fa_json": json.dumps(["گکوی_مفصلی", "چاپ_سه‌بعدی"], ensure_ascii=False),
        "selected_images_json": json.dumps(["local://a.webp", "local://b.webp"], ensure_ascii=False),
        "image_alt_texts_json": json.dumps(["گکوی مفصلی تصویر اول", "گکوی مفصلی تصویر دوم"], ensure_ascii=False),
    }
    row.update(overrides)
    return row


class Phase493CPersianReadinessAlignmentTests(unittest.TestCase):
    def _module(self):
        module = SimpleNamespace()
        module.evaluate_readiness = lambda _row: copy.deepcopy(_base_state())
        install_readiness(module)
        return module

    def test_true_source_identity_is_allowed_only_beside_persian_text(self):
        self.assertTrue(
            has_persian_editorial_text_for_source(
                "گکوی مفصلی فلکسی (Flexi Gecko)",
                "Flexi Gecko",
            )
        )
        self.assertFalse(
            has_persian_editorial_text_for_source(
                "گکوی مفصلی premium Gecko",
                "Flexi Gecko",
            )
        )

    def test_title_defect_belongs_to_quick_not_content(self):
        state = self._module().evaluate_readiness(_row(title_fa="Flexi Gecko"))
        self.assertIn("عنوان فارسی", state["stages"]["quick"]["missing"])
        self.assertNotIn("عنوان فارسی", state["stages"]["content"]["missing"])

    def test_source_identity_in_title_does_not_keep_quick_stage_red(self):
        state = self._module().evaluate_readiness(_row())
        self.assertTrue(state["stages"]["quick"]["ready"])
        self.assertNotIn("عنوان فارسی", state["stages"]["content"]["missing"])

    def test_exact_source_identity_is_allowed_in_seo_but_arbitrary_latin_is_not(self):
        allowed = self._module().evaluate_readiness(
            _row(
                seo_title_fa="خرید گکوی مفصلی Flexi Gecko",
                seo_description_fa="خرید مدل Flexi Gecko با چاپ سه‌بعدی دقیق.",
            )
        )
        self.assertNotIn("SEO Title فارسی", allowed["stages"]["content"]["missing"])
        self.assertNotIn("SEO Description فارسی", allowed["stages"]["content"]["missing"])

        blocked = self._module().evaluate_readiness(
            _row(
                seo_title_fa="خرید premium Gecko",
                keywords_json=json.dumps(["گکوی مفصلی", "Flexi Gecko"], ensure_ascii=False),
            )
        )
        self.assertIn("SEO Title فارسی", blocked["stages"]["content"]["missing"])
        self.assertIn("کلمات کلیدی فارسی", blocked["stages"]["content"]["missing"])

    def test_alt_count_defect_belongs_to_images_not_content(self):
        state = self._module().evaluate_readiness(
            _row(image_alt_texts_json=json.dumps(["گکوی مفصلی تصویر اول"], ensure_ascii=False))
        )
        self.assertIn("Alt فارسی همه تصاویر انتخاب‌شده", state["stages"]["images"]["missing"])
        self.assertNotIn("Alt فارسی همه تصاویر انتخاب‌شده", state["stages"]["content"]["missing"])


if __name__ == "__main__":
    unittest.main()
