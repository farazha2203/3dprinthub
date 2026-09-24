import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.db import Database
from qt6.main_window import MainWindow


def add_product(db: Database, external_id: str) -> int:
    db.upsert_product({
        "source_code": "makerworld",
        "external_id": external_id,
        "source_url": f"https://example.com/models/{external_id}",
        "source_title": f"Product {external_id}",
        "title_fa": f"محصول {external_id}",
        "description_fa": "توضیح",
        "images_json": "[]",
        "workflow_status": "review",
    })
    row = db.conn.execute(
        "SELECT id FROM products WHERE source_code=? AND external_id=?",
        ("makerworld", external_id),
    ).fetchone()
    return int(row["id"])
def add_history(
    db: Database,
    product_id: int,
    event_type: str,
    created_at: str,
) -> None:
    db.conn.execute(
        """
        INSERT INTO product_history(
            product_id,event_type,before_json,after_json,note,created_at
        ) VALUES(?,?,?,?,?,?)
        """,
        (int(product_id), event_type, "{}", "{}", "test", created_at),
    )
    db.conn.commit()


class RecentActivityQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Database(Path(self.tmp.name) / "catalog.sqlite3")
        self.addCleanup(self.db.close)

    def ids(self, filter_name: str, *, sort_key: str = "priority"):
        return [
            int(row["id"])
            for row in self.db.product_page(
                filter_name=filter_name,
                sort_key=sort_key,
                limit=100,
            )
        ]

    def test_recently_edited_uses_only_operator_save_events_newest_first(self):
        first = add_product(self.db, "edit-a")
        second = add_product(self.db, "edit-b")
        system_only = add_product(self.db, "system-c")

        add_history(
            self.db, first, "studio_save", "2026-09-24T08:00:00Z"
        )
        add_history(
            self.db, second, "qt_stage_edit", "2026-09-24T09:00:00Z"
        )
        add_history(
            self.db, system_only, "refetch", "2026-09-24T11:00:00Z"
        )
        add_history(
            self.db, first, "epic49_studio_save", "2026-09-24T12:00:00Z"
        )
        add_history(
            self.db, second, "qt_site_product_pulled", "2026-09-24T13:00:00Z"
        )

        self.assertEqual(
            self.ids("recently_edited", sort_key="oldest"),
            [first, second],
        )
        self.assertEqual(
            self.db.product_count(filter_name="recently_edited"),
            2,
        )

    def test_recently_edited_accepts_profile_image_and_content_operator_edits(self):
        ids = []
        for index, event in enumerate(
            ("qt_profile_ledger_edit", "qt_image_reordered", "content_edit"),
            start=1,
        ):
            product_id = add_product(self.db, f"manual-{index}")
            ids.append(product_id)
            add_history(
                self.db,
                product_id,
                event,
                f"2026-09-24T10:0{index}:00Z",
            )
        self.assertEqual(
            self.ids("recently_edited"),
            list(reversed(ids)),
        )


class RecentViewContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Database(Path(self.tmp.name) / "catalog.sqlite3")
        self.addCleanup(self.db.close)
    def test_record_view_is_persisted_ordered_and_never_dirties_product(self):
        first = add_product(self.db, "view-a")
        second = add_product(self.db, "view-b")
        before = dict(self.db.product(first))

        with patch("app.db.utc_now", return_value="2026-09-24T10:00:00Z"):
            self.assertTrue(self.db.record_product_view(first))
        after_first_view = dict(self.db.product(first))
        self.assertEqual(before, after_first_view)

        with patch("app.db.utc_now", return_value="2026-09-24T10:01:00Z"):
            self.assertTrue(self.db.record_product_view(second))
        self.assertEqual(
            [
                int(row["id"])
                for row in self.db.product_page(
                    filter_name="recently_viewed",
                    sort_key="oldest",
                    limit=100,
                )
            ],
            [second, first],
        )

        with patch("app.db.utc_now", return_value="2026-09-24T10:02:00Z"):
            self.assertTrue(self.db.record_product_view(first))
        self.assertEqual(
            [
                int(row["id"])
                for row in self.db.product_page(
                    filter_name="recently_viewed",
                    limit=100,
                )
            ],
            [first, second],
        )
        self.assertEqual(before, dict(self.db.product(first)))
        rows = self.db.conn.execute(
            """
            SELECT product_id,event_type,created_at
            FROM product_history
            WHERE event_type='product_viewed'
            ORDER BY id
            """
        ).fetchall()
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            [int(row["product_id"]) for row in rows],
            [first, second, first],
        )

    def test_missing_product_is_not_recorded_as_viewed(self):
        self.assertFalse(self.db.record_product_view(999999))
        total = self.db.conn.execute(
            "SELECT COUNT(*) FROM product_history WHERE event_type='product_viewed'"
        ).fetchone()[0]
        self.assertEqual(int(total), 0)


class MainWindowOpenContractTests(unittest.TestCase):
    def test_open_product_records_view_only_after_successful_load(self):
        calls = []

        class Wizard:
            def load_product(self, product_id):
                calls.append(("load", int(product_id)))

        class DB:
            def record_product_view(self, product_id):
                calls.append(("view", int(product_id)))
                return True

        class Status:
            def setText(self, value):
                calls.append(("status", value))

        fake = SimpleNamespace(
            wizard_page=Wizard(),
            db=DB(),
            navigate=lambda route: calls.append(("navigate", route)),
            status_message=Status(),
        )
        MainWindow.open_product(fake, 77)

        self.assertEqual(calls[0], ("load", 77))
        self.assertEqual(calls[1], ("view", 77))
        self.assertEqual(calls[2], ("navigate", "wizard"))
        self.assertEqual(calls[3][0], "status")

    def test_failed_load_does_not_record_view(self):
        calls = []

        class Wizard:
            def load_product(self, product_id):
                calls.append(("load", int(product_id)))
                raise RuntimeError("load failed")
        class DB:
            def record_product_view(self, product_id):
                calls.append(("view", int(product_id)))
                return True

        fake = SimpleNamespace(
            wizard_page=Wizard(),
            db=DB(),
            navigate=lambda route: calls.append(("navigate", route)),
            status_message=SimpleNamespace(setText=lambda _value: None),
        )
        with self.assertRaisesRegex(RuntimeError, "load failed"):
            MainWindow.open_product(fake, 77)
        self.assertEqual(calls, [("load", 77)])


class ProductsFilterSourceContractTests(unittest.TestCase):
    def test_products_ui_exposes_recent_edit_and_recent_view_filters(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "qt6"
            / "pages.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '"آخرین ادیت‌شده‌ها", "recently_edited"',
            source,
        )
        self.assertIn(
            '"اخیراً دیده‌شده‌ها", "recently_viewed"',
            source,
        )
        self.assertIn(
            'filter_name in {"recently_edited", "recently_viewed"}',
            source,
        )
        self.assertIn('self.sort_combo.findData("newest")', source)
        self.assertIn("self.sort_combo.setEnabled(not locked)", source)


if __name__ == "__main__":
    unittest.main()
