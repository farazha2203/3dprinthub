from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from app.db import Database, utc_now
from app.page_extractor import parse_page_snapshot
from app.workflow import product_state, pricing_suggestion, should_mark_needs_update

class V82DatabaseTests(unittest.TestCase):
    def test_v82_schema_and_high_volume_filters(self):
        with tempfile.TemporaryDirectory() as td:
            db=Database(Path(td)/"catalog.sqlite3")
            cols={r["name"] for r in db.conn.execute("PRAGMA table_info(products)")}
            required={"source_rating","source_rating_count","source_like_count","source_download_count","source_view_count","last_synced_source_hash","published_at","needs_update","content_status"}
            self.assertTrue(required.issubset(cols))
            db.upsert_product({"source_code":"x","external_id":"1","source_url":"https://x/1","source_title":"A","workflow_status":"uploaded","server_id":"9","server_status":"created","needs_update":0,"title_fa":"الف","description_fa":"توضیح","content_status":"ready"})
            db.upsert_product({"source_code":"x","external_id":"2","source_url":"https://x/2","source_title":"B","workflow_status":"needs_update","server_id":"10","server_status":"updated","needs_update":1})
            self.assertEqual(len(db.products("published")),1)
            self.assertEqual(len(db.products("needs_update")),1)
            self.assertEqual(db.status_counts()["published_count"],1)
            db.close()

class V82WorkflowTests(unittest.TestCase):
    def test_published_then_changed_returns_to_work_queue(self):
        row={"server_status":"created","product_sync_error":"","needs_update":0,"server_id":"44","workflow_status":"uploaded","upload_ready":0,"title_fa":"x","description_fa":"y","content_status":"ready","source_hash":"old","last_synced_source_hash":"old"}
        self.assertEqual(product_state(row),"published")
        self.assertTrue(should_mark_needs_update(row,"new"))
        row["needs_update"]=1
        self.assertEqual(product_state(row),"needs_update")

    def test_pricing_is_deterministic_and_rounded(self):
        value=pricing_suggestion(200,1500,240)
        self.assertGreaterEqual(value,350000)
        self.assertEqual(value%10000,0)

    def test_rating_and_popularity_from_structured_data(self):
        snapshot={
            "source_url":"https://e.test/p/1","final_url":"https://e.test/p/1","title":"T","metas":{},
            "json_ld":[json.dumps({"@type":"Product","name":"Model","aggregateRating":{"ratingValue":"4.8","ratingCount":"123"},"interactionStatistic":[{"interactionType":{"@type":"DownloadAction"},"userInteractionCount":4567},{"interactionType":{"@type":"LikeAction"},"userInteractionCount":321}],"datePublished":"2026-07-01","dateModified":"2026-08-01"})],
            "breadcrumbs":[],"spec_rows":[],"dom_images":[],"picture_sources":[],"links":[],"body_text":"","network_json":[]}
        page=parse_page_snapshot(snapshot)
        self.assertEqual(page.source_rating,4.8)
        self.assertEqual(page.source_rating_count,123)
        self.assertEqual(page.source_download_count,4567)
        self.assertEqual(page.source_like_count,321)
        self.assertEqual(page.source_updated_at,"2026-08-01")

if __name__ == "__main__":unittest.main(verbosity=2)
