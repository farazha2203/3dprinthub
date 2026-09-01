from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from app.crawler import BlockedError
from app.db import Database
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app import phase49_3c_image_pipeline as image_pipeline
from app.phase49_3i34_profile_matrix import ensure_schema as ensure_profile_schema
from app.phase49_3i35_operator_ledger import ensure_schema as ensure_ledger_schema
from app.phase49_3i36_stage_finalization import LOCK_COLUMN, install_database
from app.phase49_3i37_seven_stage_ai import (
    AI_SOURCE_MODES,
    SOURCE_SETTING,
    _field_needs_fill,
    capture_screenshot_for_site,
    orchestrate_once,
    source_mode,
    validate_editorial_pack,
)


class _Settings:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def setting(self, key, default=""):
        return self.values.get(key, default)


class Phase493I37SevenStageAITests(unittest.TestCase):
    def _db(self, path: Path):
        class LockedDatabase(Database):
            pass

        install_database(LockedDatabase)
        db = LockedDatabase(path)
        ensure_epic49_desktop_schema(db)
        ensure_profile_schema(db)
        ensure_ledger_schema(db)
        image_pipeline.ensure_schema(db)
        return db

    def _product(self, db, local_dir: Path, **extra):
        local_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "source_code": "makerworld",
            "external_id": "twistmas-303",
            "source_url": "https://makerworld.com/en/models/1936731-twistmas-tree",
            "source_title": "Twistmas Tree",
            "title_fa": "",
            "short_description_fa": "",
            "description_fa": "",
            "local_dir": str(local_dir),
        }
        payload.update(extra)
        db.upsert_product(payload)
        return int(db.products()[0]["id"])

    def test_source_mode_has_exact_three_persisted_choices(self):
        self.assertEqual(set(AI_SOURCE_MODES), {"link", "data", "screenshot"})
        self.assertEqual(source_mode(SimpleNamespace(db=_Settings({SOURCE_SETTING: "data"}))), "data")
        self.assertEqual(source_mode(SimpleNamespace(db=_Settings({SOURCE_SETTING: "bad"}))), "link")

    def test_editorial_guard_canonicalizes_twistmas_identity_and_rejects_language_noise(self):
        pack = {
            "title_fa": "تویست‌ماس تری",
            "short_description_fa": "یک مدل سه‌بعدی تزئینی برای کریسمس.",
            "description_fa": "این مدل برای چاپ سه‌بعدی و دکور کریسمس طراحی شده است.",
            "seo_title_fa": "خرید Twistmas Tree",
            "seo_description_fa": "مدل درخت کریسمس اسپیرال برای دکور و چاپ سه‌بعدی.",
            "material_recommendations": ["PLA"],
            "suggested_category_slug": "decor",
        }
        clean = validate_editorial_pack("Twistmas Tree", pack)
        self.assertEqual(clean["title_fa"], "درخت کریسمس اسپیرال")
        self.assertIn("درخت کریسمس اسپیرال", clean["seo_title_fa"])
        self.assertEqual(clean["material_recommendations"], [])
        self.assertEqual(clean["suggested_category_slug"], "")

        noisy = dict(clean)
        noisy["seo_description_fa"] = "مدل درخت کریسمس для دکوراسیون."
        with self.assertRaises(RuntimeError):
            validate_editorial_pack("Twistmas Tree", noisy)

        latin_noise = dict(clean)
        latin_noise["seo_description_fa"] = "مدل درخت کریسمس اسپیرال kecil برای دکور."
        with self.assertRaises(RuntimeError):
            validate_editorial_pack("Twistmas Tree", latin_noise)

    def test_checker_and_repair_agree_on_exact_source_identity_and_persian_lists(self):
        source_title = "Flexi Gecko"
        row = {
            "external_id": "3128884",
            "title_fa": "گکوی مفصلی فلکسی (Flexi Gecko)",
            "short_description_fa": "مدل گکوی مفصلی برای چاپ سه‌بعدی.",
            "description_fa": "مدل Flexi Gecko برای دکور و چاپ سه‌بعدی.",
            "use_description": "برای دکور و هدیه مناسب است.",
            "seo_title_fa": "خرید گکوی مفصلی Flexi Gecko",
            "seo_description_fa": "خرید Flexi Gecko با چاپ سه‌بعدی.",
            "keywords_json": json.dumps(["گکوی مفصلی", "Flexi Gecko"], ensure_ascii=False),
            "tags_fa_json": json.dumps(["گکو"], ensure_ascii=False),
            "hashtags_fa_json": json.dumps(["گکوی_مفصلی"], ensure_ascii=False),
        }
        self.assertFalse(_field_needs_fill(row, "title_fa", source_title))
        self.assertFalse(_field_needs_fill(row, "seo_title_fa", source_title))
        self.assertFalse(_field_needs_fill(row, "seo_description_fa", source_title))
        self.assertTrue(_field_needs_fill(row, "keywords_json", source_title))

        row["seo_title_fa"] = "خرید premium Gecko"
        self.assertTrue(_field_needs_fill(row, "seo_title_fa", source_title))

        row["seo_title_fa"] = "خرید گکوی مفصلی فلکسی"
        row["keywords_json"] = json.dumps(["گکوی مفصلی", "چاپ سه‌بعدی"], ensure_ascii=False)
        self.assertFalse(_field_needs_fill(row, "seo_title_fa", source_title))
        self.assertFalse(_field_needs_fill(row, "keywords_json", source_title))

    def test_editorial_guard_allows_exact_source_identity_in_seo_and_rejects_unrelated_latin(self):
        pack = {
            "title_fa": "گکوی مفصلی فلکسی (Flexi Gecko)",
            "short_description_fa": "مدل گکوی مفصلی برای چاپ سه‌بعدی.",
            "description_fa": "این مدل گکوی مفصلی برای چاپ سه‌بعدی طراحی شده است.",
            "seo_title_fa": "خرید گکوی مفصلی Flexi Gecko",
            "seo_description_fa": "خرید Flexi Gecko برای چاپ سه‌بعدی.",
            "material_recommendations": [],
            "suggested_category_slug": "",
        }
        clean = validate_editorial_pack("Flexi Gecko", pack)
        self.assertEqual(clean["seo_title_fa"], "خرید گکوی مفصلی Flexi Gecko")

        noisy = dict(pack)
        noisy["seo_description_fa"] = "خرید Flexi Gecko premium برای چاپ سه‌بعدی."
        with self.assertRaises(RuntimeError):
            validate_editorial_pack("Flexi Gecko", noisy)

    def test_driftbloom_lamp_translation_guard_rejects_nonsense_and_accepts_semantic_title(self):
        from app.phase49_3i33_ai_core import title_quality_guard

        source = "Driftbloom Table Lamp Organic Ambient Desk Lamp"
        with self.assertRaises(RuntimeError):
            title_quality_guard(
                source,
                "لیمی دوختنی دریفتوبلم، لامپ میزی دکور کلاسیک",
            )
        title_quality_guard(
            source,
            "چراغ رومیزی ارگانیک Driftbloom با نور محیطی",
        )

    def test_orchestrator_fills_missing_editorial_stages_without_touching_profile_commerce(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(db, root / "product")
                profile = [{
                    "key": "20cm",
                    "name": "۲۰ سانت",
                    "production_rows": [{"weight_grams": 100, "print_time_minutes": 60, "support_weight_grams": 10}],
                }]
                db.update_product(product_id, {
                    "sales_profiles_json": json.dumps(profile, ensure_ascii=False),
                    "sales_profile_ledger_json": json.dumps(profile, ensure_ascii=False),
                    "price_min": 250000,
                    "price_max": 300000,
                    LOCK_COLUMN: json.dumps({"commerce": {"locked": True}}, ensure_ascii=False),
                })
                app = SimpleNamespace(db=db)
                source = {
                    "source_url": "https://makerworld.com/en/models/1936731-twistmas-tree",
                    "source_title": "Twistmas Tree",
                    "source_description": "Verified source facts",
                    "raw_source_description": "A spiral Christmas tree model.",
                    "facts": {"like_count": 12, "estimated_weight_grams": 139},
                    "evidence": {"like_count": 12, "estimated_weight_grams": 139},
                }
                pack = {
                    "title_fa": "تویست‌ماس تری",
                    "short_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال برای دکور.",
                    "description_fa": "درخت کریسمس اسپیرال یک مدل تزئینی مناسب چاپ سه‌بعدی است.",
                    "use_description_fa": "برای دکور کریسمس و تزئینات مناسب است.",
                    "categories_fa": ["دکور کریسمس"],
                    "specs_fa": ["مدل چاپ سه‌بعدی"],
                    "tags_fa": ["کریسمس"],
                    "hashtags_fa": ["درخت_کریسمس"],
                    "target_keywords_fa": ["درخت کریسمس اسپیرال"],
                    "sales_bullets": ["طراحی اسپیرال"],
                    "image_alt_texts": [],
                    "seo_title_fa": "خرید Twistmas Tree",
                    "seo_description_fa": "مدل درخت کریسمس اسپیرال برای چاپ سه‌بعدی و دکور کریسمس.",
                    "social_caption_fa": "درخت کریسمس اسپیرال برای دکور.",
                    "homepage_slider_seo": {},
                    "material_recommendations": [],
                    "suggested_category_slug": "",
                }
                with patch(
                    "app.phase49_3i37_seven_stage_ai.resolve_source",
                    return_value=source,
                ) as resolver, patch(
                    "app.phase49_3i37_seven_stage_ai.generate_translation_pack",
                    return_value=pack,
                ) as generator:
                    result = orchestrate_once(
                        app, product_id, "link", "openrouter", "key", "model", None
                    )

                resolver.assert_called_once()
                generator.assert_called_once()
                row = db.product(product_id)
                self.assertEqual(row["title_fa"], "درخت کریسمس اسپیرال")
                self.assertIn("درخت کریسمس اسپیرال", row["seo_title_fa"])
                self.assertEqual(json.loads(row["sales_profile_ledger_json"]), profile)
                self.assertEqual(json.loads(row["sales_profiles_json"]), profile)
                self.assertEqual(int(row["price_min"]), 250000)
                self.assertEqual(int(row["price_max"]), 300000)
                self.assertNotIn("sales_profile_ledger_json", result["changed_fields"])
                self.assertNotIn("price_min", result["changed_fields"])
            finally:
                db.close()

    def test_link_403_falls_back_to_saved_data_and_persists_quick_title(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(
                    db,
                    root / "product",
                    source_description="A spiral Christmas tree model.",
                )
                app = SimpleNamespace(db=db)
                pack = {
                    "title_fa": "درخت کریسمس اسپیرال",
                    "short_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال برای دکور.",
                    "description_fa": "درخت کریسمس اسپیرال یک مدل تزئینی مناسب چاپ سه‌بعدی است.",
                    "use_description_fa": "برای دکور کریسمس مناسب است.",
                    "categories_fa": ["دکور"],
                    "specs_fa": [],
                    "tags_fa": ["کریسمس"],
                    "hashtags_fa": ["درخت_کریسمس"],
                    "target_keywords_fa": ["درخت کریسمس اسپیرال"],
                    "sales_bullets": ["طراحی اسپیرال"],
                    "image_alt_texts": [],
                    "seo_title_fa": "درخت کریسمس اسپیرال چاپ سه‌بعدی",
                    "seo_description_fa": "مدل درخت کریسمس اسپیرال برای چاپ سه‌بعدی و دکور.",
                    "social_caption_fa": "درخت کریسمس اسپیرال برای دکور.",
                    "homepage_slider_seo": {},
                    "material_recommendations": [],
                    "suggested_category_slug": "",
                }
                with patch(
                    "app.phase49_3i37_seven_stage_ai.live_source_for_ai",
                    side_effect=BlockedError("HTTP Error 403: Forbidden"),
                ), patch(
                    "app.phase49_3i37_seven_stage_ai.generate_translation_pack",
                    return_value=pack,
                ) as generator:
                    result = orchestrate_once(
                        app,
                        product_id,
                        "link",
                        "openrouter",
                        "key",
                        "openai/gpt-oss-20b",
                        None,
                        target_stages={"quick"},
                        refresh_existing=True,
                    )

                generator.assert_called_once()
                row = db.product(product_id)
                self.assertEqual(row["title_fa"], "درخت کریسمس اسپیرال")
                self.assertEqual(result["source_effective_mode"], "data")
                self.assertTrue(result["source_fallback"])
                self.assertIn("title_fa", result["changed_fields"])
            finally:
                db.close()

    def test_scoped_locked_stage_does_not_fetch_source_or_call_provider(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(
                    db,
                    root / "product",
                    title_fa="عنوان نهایی اپراتور",
                )
                db.update_product(
                    product_id,
                    {
                        LOCK_COLUMN: json.dumps(
                            {"quick": {"locked": True}},
                            ensure_ascii=False,
                        )
                    },
                )
                app = SimpleNamespace(db=db)
                with patch(
                    "app.phase49_3i37_seven_stage_ai.resolve_source"
                ) as resolver, patch(
                    "app.phase49_3i37_seven_stage_ai.generate_translation_pack"
                ) as generator:
                    result = orchestrate_once(
                        app,
                        product_id,
                        "link",
                        "openrouter",
                        "key",
                        "openai/gpt-oss-20b",
                        None,
                        target_stages={"quick"},
                        refresh_existing=True,
                    )

                resolver.assert_not_called()
                generator.assert_not_called()
                self.assertTrue(result["no_ai_needed"])
                self.assertEqual(
                    db.product(product_id)["title_fa"],
                    "عنوان نهایی اپراتور",
                )
            finally:
                db.close()

    def test_orchestrator_never_claims_apply_when_db_write_did_not_persist(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(db, root / "product")
                app = SimpleNamespace(db=db)
                source = {
                    "source_url": "https://makerworld.com/en/models/1936731-twistmas-tree",
                    "source_title": "Twistmas Tree",
                    "source_description": "Verified saved Product facts.",
                    "raw_source_description": "A spiral Christmas tree model.",
                    "facts": {},
                    "evidence": {},
                }
                pack = {
                    "title_fa": "درخت کریسمس اسپیرال",
                    "short_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال برای دکور.",
                    "description_fa": "درخت کریسمس اسپیرال یک مدل تزئینی مناسب چاپ سه‌بعدی است.",
                    "use_description_fa": "برای دکور کریسمس مناسب است.",
                    "categories_fa": [],
                    "specs_fa": [],
                    "tags_fa": [],
                    "hashtags_fa": [],
                    "target_keywords_fa": [],
                    "sales_bullets": [],
                    "image_alt_texts": [],
                    "seo_title_fa": "درخت کریسمس اسپیرال چاپ سه‌بعدی",
                    "seo_description_fa": "مدل درخت کریسمس اسپیرال برای چاپ سه‌بعدی و دکور.",
                    "social_caption_fa": "",
                    "homepage_slider_seo": {},
                    "material_recommendations": [],
                    "suggested_category_slug": "",
                }
                with patch(
                    "app.phase49_3i37_seven_stage_ai.resolve_source",
                    return_value=source,
                ), patch(
                    "app.phase49_3i37_seven_stage_ai.generate_translation_pack",
                    return_value=pack,
                ), patch.object(
                    db,
                    "update_product",
                    return_value=None,
                ):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "اعمال/ذخیره دیتابیس تأیید نشد",
                    ):
                        orchestrate_once(
                            app,
                            product_id,
                            "data",
                            "openrouter",
                            "key",
                            "openai/gpt-oss-20b",
                            None,
                            target_stages={"quick"},
                            refresh_existing=True,
                        )
            finally:
                db.close()

    def test_locked_quick_and_content_are_not_rewritten_by_orchestrator(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(
                    db, root / "product",
                    title_fa="نام نهایی اپراتور",
                    short_description_fa="توضیح کوتاه نهایی اپراتور",
                    description_fa="توضیح کامل نهایی اپراتور",
                )
                db.update_product(product_id, {
                    "seo_title_fa": "عنوان سئو نهایی اپراتور",
                    "seo_description_fa": "توضیح سئو نهایی اپراتور",
                    LOCK_COLUMN: json.dumps({
                        "quick": {"locked": True},
                        "content": {"locked": True},
                    }, ensure_ascii=False),
                })
                app = SimpleNamespace(db=db)
                source = {
                    "source_title": "Twistmas Tree",
                    "source_description": "facts",
                    "raw_source_description": "facts",
                    "facts": {},
                    "evidence": {},
                }
                pack = {
                    "title_fa": "درخت کریسمس اسپیرال",
                    "short_description_fa": "توضیح کوتاه تولیدشده",
                    "description_fa": "توضیح کامل تولیدشده",
                    "use_description_fa": "توضیح کاربرد تولیدشده",
                    "categories_fa": [], "specs_fa": [], "tags_fa": [], "hashtags_fa": [],
                    "target_keywords_fa": [], "sales_bullets": [], "image_alt_texts": [],
                    "seo_title_fa": "درخت کریسمس اسپیرال",
                    "seo_description_fa": "توضیح فارسی درباره درخت کریسمس اسپیرال.",
                    "social_caption_fa": "",
                    "homepage_slider_seo": {},
                }
                with patch("app.phase49_3i37_seven_stage_ai.resolve_source", return_value=source), patch(
                    "app.phase49_3i37_seven_stage_ai.generate_translation_pack", return_value=pack
                ):
                    orchestrate_once(app, product_id, "data", "openrouter", "key", "model", None)
                row = db.product(product_id)
                self.assertEqual(row["title_fa"], "نام نهایی اپراتور")
                self.assertEqual(row["short_description_fa"], "توضیح کوتاه نهایی اپراتور")
                self.assertEqual(row["description_fa"], "توضیح کامل نهایی اپراتور")
                self.assertEqual(row["seo_title_fa"], "عنوان سئو نهایی اپراتور")
            finally:
                db.close()

    def test_screenshot_becomes_selected_site_image_with_seo_and_source_page_link(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_dir = root / "product"
                product_id = self._product(
                    db, product_dir,
                    title_fa="درخت کریسمس اسپیرال",
                    short_description_fa="مدل دکور کریسمس",
                    description_fa="مدل سه‌بعدی برای دکور کریسمس",
                )
                db.update_product(product_id, {
                    "seo_title_fa": "درخت کریسمس اسپیرال",
                    "seo_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال برای دکور.",
                })
                image_dir = product_dir / "images"
                image_dir.mkdir(parents=True, exist_ok=True)
                target = image_dir / "source-page-screenshot-test.png"
                Image.new("RGB", (640, 480), "white").save(target)

                app = SimpleNamespace(db=db)
                with patch(
                    "app.phase49_3i37_seven_stage_ai.capture_source_screenshot",
                    return_value=target,
                ):
                    result = capture_screenshot_for_site(app, product_id)

                row = db.product(product_id)
                pseudo = "local://source-page-screenshot-test.png"
                self.assertIn(pseudo, json.loads(row["images_json"]))
                self.assertIn(pseudo, json.loads(row["selected_images_json"]))
                self.assertEqual(row["primary_image_url"], pseudo)
                self.assertTrue(result["metadata"]["metadata_ready"])
                self.assertEqual(result["metadata"]["source_page_url"], row["source_url"])
                self.assertTrue(Path(result["metadata"]["final_local_file"]).is_file())
                self.assertTrue(str(result["metadata"]["seo_filename"]).endswith(".webp"))
            finally:
                db.close()

    def test_locked_image_stage_can_refresh_only_derived_metadata_after_content_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_dir = root / "product"
                product_id = self._product(
                    db,
                    product_dir,
                    title_fa="گکوی مفصلی",
                    short_description_fa="توضیح اولیه",
                    description_fa="توضیح کامل اولیه",
                )
                image_dir = product_dir / "images"
                image_dir.mkdir(parents=True, exist_ok=True)
                image_path = image_dir / "selected.png"
                Image.new("RGB", (320, 240), "white").save(image_path)
                url = "local://selected.png"
                db.update_product(product_id, {
                    "images_json": json.dumps([url], ensure_ascii=False),
                    "selected_images_json": json.dumps([url], ensure_ascii=False),
                    "primary_image_url": url,
                    "image_alt_texts_json": json.dumps(["نمای گکوی مفصلی"], ensure_ascii=False),
                    "seo_title_fa": "گکوی مفصلی",
                    "seo_description_fa": "مدل سه‌بعدی گکوی مفصلی.",
                })
                image_pipeline.finalize_selected_images(db, product_id)
                self.assertEqual(image_pipeline.image_metadata_missing(db.product(product_id)), [])

                db.update_product(product_id, {
                    LOCK_COLUMN: json.dumps({"images": {"locked": True}}, ensure_ascii=False)
                })
                db.update_product(product_id, {
                    "seo_title_fa": "گکوی مفصلی انعطاف‌پذیر",
                    "seo_description_fa": "مدل سه‌بعدی گکوی مفصلی انعطاف‌پذیر.",
                })
                self.assertTrue(image_pipeline.image_metadata_missing(db.product(product_id)))

                image_pipeline.finalize_selected_images(db, product_id)
                refreshed = db.product(product_id)
                self.assertEqual(image_pipeline.image_metadata_missing(refreshed), [])
                self.assertIn('"images"', refreshed[LOCK_COLUMN])
                self.assertIn('"locked": true', refreshed[LOCK_COLUMN].lower())
            finally:
                db.close()

    def test_screenshot_preserves_existing_primary_and_image_lock_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_dir = root / "product"
                product_id = self._product(
                    db, product_dir,
                    title_fa="درخت کریسمس اسپیرال",
                    short_description_fa="مدل دکور کریسمس",
                    description_fa="مدل سه‌بعدی دکور کریسمس",
                )
                image_dir = product_dir / "images"
                image_dir.mkdir(parents=True, exist_ok=True)
                old = image_dir / "old.png"
                shot = image_dir / "source-page-screenshot-test.png"
                Image.new("RGB", (320, 240), "white").save(old)
                Image.new("RGB", (640, 480), "black").save(shot)
                old_url = "local://old.png"
                db.update_product(product_id, {
                    "images_json": json.dumps([old_url], ensure_ascii=False),
                    "selected_images_json": json.dumps([old_url], ensure_ascii=False),
                    "primary_image_url": old_url,
                })

                app = SimpleNamespace(db=db)
                with patch(
                    "app.phase49_3i37_seven_stage_ai.capture_source_screenshot",
                    return_value=shot,
                ):
                    result = capture_screenshot_for_site(app, product_id)
                self.assertEqual(result["primary"], old_url)
                self.assertEqual(db.product(product_id)["primary_image_url"], old_url)

                db.update_product(product_id, {
                    LOCK_COLUMN: json.dumps({"images": {"locked": True}}, ensure_ascii=False)
                })
                with self.assertRaises(RuntimeError):
                    capture_screenshot_for_site(app, product_id)
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
