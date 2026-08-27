from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import phase49_3c_image_pipeline as image_pipeline
from app.db import Database
from app.epic49_desktop_schema import ensure_epic49_desktop_schema
from app.phase49_3i34_profile_matrix import ensure_schema as ensure_profile_schema
from app.phase49_3i35_operator_ledger import ensure_schema as ensure_ledger_schema
from app.phase49_3i36_stage_finalization import (
    LOCK_COLUMN,
    ensure_schema as ensure_stage_schema,
    install_database as install_stage_database,
)
from app.phase49_3i37_seven_stage_ai import (
    orchestrate_once,
    run_resilient_orchestrator,
)
from app.phase49_3i38_crawl_ledger_stage_ai import (
    ensure_schema as ensure_crawl_schema,
    install_database as install_crawl_database,
    ledger_rows,
    next_scroll_rounds,
    record_listing_progress,
    reject_and_purge_product,
    remember_ledger,
    terminal_identity_state,
)


ROOT = Path(__file__).resolve().parents[1]


class _Dialog:
    def __init__(self):
        self.cancelled = threading.Event()
        self.events = []
        self.progress = []

    def event(self, action, message, detail=None):
        self.events.append((action, message, detail or {}))

    def set_progress(self, value, message):
        self.progress.append((value, message))


class Phase493I38CrawlLedgerStageAITests(unittest.TestCase):
    def _db(self, path: Path):
        class RuntimeDatabase(Database):
            pass

        install_stage_database(RuntimeDatabase)
        install_crawl_database(RuntimeDatabase)
        db = RuntimeDatabase(path)
        ensure_epic49_desktop_schema(db)
        ensure_profile_schema(db)
        ensure_ledger_schema(db)
        ensure_stage_schema(db)
        ensure_crawl_schema(db)
        image_pipeline.ensure_schema(db)
        return db

    def _product(self, db, local_dir: Path, external_id="303", **extra):
        local_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "source_code": "makerworld",
            "external_id": str(external_id),
            "source_url": f"https://makerworld.com/en/models/{external_id}-twistmas-tree",
            "source_title": "Twistmas Tree",
            "title_fa": "نام دستی ثابت",
            "short_description_fa": "متن کوتاه قدیمی",
            "description_fa": "متن کامل قدیمی",
            "local_dir": str(local_dir),
        }
        payload.update(extra)
        db.upsert_product(payload)
        row = db.conn.execute(
            "SELECT id FROM products WHERE source_code='makerworld' AND external_id=?",
            (str(external_id),),
        ).fetchone()
        return int(row["id"])

    def test_second_hundred_skips_first_hundred_and_queues_only_new_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                base = "https://makerworld.com/en/models/"
                for index in range(1, 101):
                    remember_ledger(
                        db,
                        "makerworld",
                        str(index),
                        f"{base}{index}-model",
                        status="collected",
                        discovered_from="https://makerworld.com/en/search/models?keyword=cake",
                    )

                duplicate_count = 0
                new_count = 0
                for index in range(1, 201):
                    added = db.add_discovered(
                        "makerworld",
                        str(index),
                        f"{base}{index}-model",
                        "https://makerworld.com/en/search/models?keyword=cake",
                    )
                    if added:
                        new_count += 1
                    else:
                        duplicate_count += 1

                self.assertEqual(duplicate_count, 100)
                self.assertEqual(new_count, 100)
                pending = db.pending_urls("makerworld", 100, include_failed=False)
                self.assertEqual(len(pending), 100)
                self.assertEqual(
                    {int(row["external_id"]) for row in pending},
                    set(range(101, 201)),
                )
            finally:
                db.close()

    def test_listing_scroll_cursor_continues_deeper_across_runs(self):
        with tempfile.TemporaryDirectory() as temporary:
            db = self._db(Path(temporary) / "catalog.sqlite3")
            try:
                listing = "https://makerworld.com/en/search/models?keyword=cake+stand"
                self.assertEqual(next_scroll_rounds(db, "makerworld", listing), 8)
                record_listing_progress(
                    db, "makerworld", listing,
                    scroll_rounds=8, found_count=100, new_count=100,
                )
                self.assertEqual(next_scroll_rounds(db, "makerworld", listing), 16)
                record_listing_progress(
                    db, "makerworld", listing,
                    scroll_rounds=16, found_count=145, new_count=45,
                )
                self.assertEqual(next_scroll_rounds(db, "makerworld", listing), 24)
            finally:
                db.close()

    def test_reject_purge_deletes_only_product_collected_dir_and_keeps_tombstone(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "data"
            local_dir = data / "collected" / "makerworld" / "303"
            (local_dir / "images").mkdir(parents=True, exist_ok=True)
            (local_dir / "images" / "01.jpg").write_bytes(b"image")
            (local_dir / "model.stl").write_bytes(b"mesh")

            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(
                    db,
                    local_dir,
                    images_json=json.dumps(["local://01.jpg"]),
                    selected_images_json=json.dumps(["local://01.jpg"]),
                    primary_image_url="local://01.jpg",
                    file_links_json=json.dumps(["https://example.com/model.stl"]),
                    selected_file_links_json=json.dumps(["https://example.com/model.stl"]),
                )
                db.update_product(product_id, {
                    LOCK_COLUMN: json.dumps({
                        "images": {"locked": True},
                        "content": {"locked": True},
                    }, ensure_ascii=False),
                })
                app = SimpleNamespace(DATA=data, db=db)

                result = reject_and_purge_product(app, product_id, "مدل مناسب فروش نیست")

                self.assertTrue(result["deleted"])
                self.assertFalse(local_dir.exists())
                row = db.product(product_id)
                self.assertEqual(int(row["is_blocked"]), 1)
                self.assertEqual(row["source_state"], "rejected")
                self.assertEqual(row["images_json"], "[]")
                self.assertEqual(row["selected_images_json"], "[]")
                self.assertEqual(row["file_links_json"], "[]")
                self.assertEqual(row["selected_file_links_json"], "[]")
                self.assertEqual(row["local_dir"], "")
                self.assertTrue(row["source_url"].startswith("https://makerworld.com/"))
                self.assertEqual(
                    terminal_identity_state(
                        db, row["source_code"], row["external_id"], row["source_url"]
                    ),
                    "rejected",
                )
                ledger = ledger_rows(db, status="rejected")
                self.assertEqual(len(ledger), 1)
                self.assertEqual(ledger[0]["external_id"], "303")
                self.assertFalse(
                    db.add_discovered(
                        row["source_code"], row["external_id"], row["source_url"], "repeat"
                    )
                )

                # Explicit operator restore is the only way to permit acquisition again.
                db.restore_product(product_id)
                restored = db.product(product_id)
                self.assertEqual(int(restored["is_blocked"]), 0)
                restored_ledger = ledger_rows(db, status="new")
                self.assertEqual(len(restored_ledger), 1)
                self.assertEqual(restored_ledger[0]["external_id"], "303")
            finally:
                db.close()

    def test_reject_purge_refuses_any_path_outside_canonical_collected_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "data"
            outside = root / "do-not-delete"
            outside.mkdir(parents=True)
            sentinel = outside / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(db, outside, external_id="999")
                app = SimpleNamespace(DATA=data, db=db)
                with self.assertRaises(RuntimeError):
                    reject_and_purge_product(app, product_id, "unsafe target")
                self.assertTrue(sentinel.is_file())
                self.assertEqual(int(db.product(product_id)["is_blocked"]), 0)
            finally:
                db.close()

    def test_targeted_stage4_cleanup_reuses_orchestrator_and_cannot_touch_other_stages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(db, root / "product", external_id="304")
                db.update_product(product_id, {
                    "seo_title_fa": "سئوی قدیمی",
                    "seo_description_fa": "توضیح سئوی قدیمی",
                    "source_description": "SOURCE MUST STAY",
                    "source_like_count": 77,
                })
                app = SimpleNamespace(db=db)
                source = {
                    "source_url": "https://makerworld.com/en/models/304-twistmas-tree",
                    "source_title": "Twistmas Tree",
                    "source_description": "Verified source facts",
                    "raw_source_description": "fresh source description",
                    "facts": {"like_count": 999},
                    "evidence": {"like_count": 999},
                }
                pack = {
                    "title_fa": "درخت کریسمس اسپیرال",
                    "short_description_fa": "متن کوتاه تمیز و کامل برای مدل سه‌بعدی.",
                    "description_fa": "توضیح کامل و تمیز فارسی برای مدل درخت کریسمس اسپیرال.",
                    "use_description_fa": "مناسب دکور و تزئینات کریسمس.",
                    "categories_fa": ["دکور"],
                    "specs_fa": ["مشخصات جدید نباید در Stage 4 اعمال شود"],
                    "tags_fa": ["کریسمس"],
                    "hashtags_fa": ["درخت_کریسمس"],
                    "target_keywords_fa": ["درخت کریسمس اسپیرال"],
                    "sales_bullets": ["طراحی اسپیرال"],
                    "image_alt_texts": [],
                    "seo_title_fa": "درخت کریسمس اسپیرال | مدل سه‌بعدی",
                    "seo_description_fa": "مدل سه‌بعدی درخت کریسمس اسپیرال برای دکور کریسمس.",
                    "social_caption_fa": "مدل درخت کریسمس اسپیرال.",
                    "homepage_slider_seo": {
                        "title_fa": "اسلایدر نباید تغییر کند",
                        "description_fa": "خارج از Stage 4",
                        "image_alt_fa": "خارج از Stage 4",
                        "button_text_fa": "مشاهده",
                        "focus_keyword_fa": "کریسمس",
                    },
                    "material_recommendations": [],
                    "suggested_category_slug": "",
                }
                with patch(
                    "app.phase49_3i37_seven_stage_ai.resolve_source",
                    return_value=source,
                ), patch(
                    "app.phase49_3i37_seven_stage_ai.generate_translation_pack",
                    return_value=pack,
                ):
                    result = orchestrate_once(
                        app,
                        product_id,
                        "data",
                        "openrouter",
                        "key",
                        "model",
                        None,
                        target_stages={"content"},
                        refresh_existing=True,
                    )

                row = db.product(product_id)
                self.assertEqual(row["title_fa"], "نام دستی ثابت")
                self.assertEqual(row["short_description_fa"], pack["short_description_fa"])
                self.assertEqual(row["description_fa"], pack["description_fa"])
                self.assertEqual(row["seo_title_fa"], pack["seo_title_fa"])
                self.assertEqual(row["source_description"], "SOURCE MUST STAY")
                self.assertEqual(int(row["source_like_count"]), 77)
                self.assertTrue(result["stages"]["quick"]["out_of_scope"])
                self.assertTrue(result["stages"]["specs"]["out_of_scope"])
                self.assertEqual(result["target_stages"], ["content"])
            finally:
                db.close()

    def test_image_only_scope_does_not_call_provider_when_image_seo_is_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            db = self._db(root / "catalog.sqlite3")
            try:
                product_id = self._product(db, root / "product", external_id="305")
                app = SimpleNamespace(db=db)
                dialog = _Dialog()
                with patch(
                    "app.phase49_3i37_seven_stage_ai.image_pipeline.image_metadata_missing",
                    return_value=[],
                ), patch(
                    "app.phase49_3i37_seven_stage_ai.configured_ai_candidates",
                    side_effect=AssertionError("provider must not be called"),
                ):
                    result = run_resilient_orchestrator(
                        app,
                        product_id,
                        dialog,
                        mode="data",
                        target_stages={"images"},
                        refresh_existing=True,
                    )
                self.assertTrue(result["no_ai_needed"])
                self.assertTrue(any(event[0] == "no_ai_needed" for event in dialog.events))
            finally:
                db.close()

    def test_products_bulk_stage4_uses_same_engine_and_main_guards_before_download(self):
        phase = (ROOT / "app" / "phase49_3i38_crawl_ledger_stage_ai.py").read_text(encoding="utf-8")
        main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")

        self.assertIn("run_resilient_orchestrator(", phase)
        self.assertIn('target_stages={"content"}', phase)
        self.assertIn("refresh_existing=True", phase)
        self.assertNotIn("AIProviderClient(", phase)
        self.assertNotIn("generate_translation_pack(", phase)

        direct_start = main.index("def start_direct_link_import")
        direct_end = main.index("def start_portfolio_harvest", direct_start)
        direct_block = main[direct_start:direct_end]
        self.assertLess(
            direct_block.index("terminal_state=terminal_identity_state"),
            direct_block.index("data=await extract_direct_link"),
        )

        scan_start = main.index("def _scan_worker")
        scan_end = main.index("def _update_dashboard", scan_start)
        scan_block = main[scan_start:scan_end]
        self.assertIn("max_pages=12", scan_block)
        self.assertIn("next_scroll_rounds(", scan_block)
        self.assertIn("record_listing_progress(", scan_block)
        self.assertIn("new_this_round", scan_block)


if __name__ == "__main__":
    unittest.main()
