from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from unittest import mock

from app.ai_providers import AIProviderClient, PROVIDERS
from app.db import Database
from app.material_engine import infer_use_case, recommend_materials
from app.page_extractor import parse_page_snapshot
from app.secure_secrets import provider_key_source, get_provider_key
from app.v8_features import ack_item_confirms_publish, commercial_license_allows_publish

ROOT = Path(__file__).resolve().parents[1]

class V84DatabaseTests(unittest.TestCase):
    def test_v84_columns(self):
        with tempfile.TemporaryDirectory() as td:
            db=Database(Path(td)/"catalog.sqlite3")
            cols={r["name"] for r in db.conn.execute("PRAGMA table_info(products)")}
            for name in {"hashtags_fa_json","material_recommendations_json","use_case_class","ai_provider","ai_model"}:
                self.assertIn(name,cols)
            db.close()

class V84AIContracts(unittest.TestCase):
    def test_provider_urls(self):
        self.assertEqual(PROVIDERS["avalai"].base_url,"https://api.avalai.ir/v1")
        self.assertEqual(PROVIDERS["openai"].base_url,"https://api.openai.com/v1")

    @mock.patch("app.ai_providers._json_request")
    def test_dynamic_model_selection(self, req):
        req.side_effect=[{"data":[{"id":"foo"},{"id":"gpt-5.4-mini"}]},{"data":[{"id":"foo"},{"id":"gpt-5.4-mini"}]}]
        client=AIProviderClient("avalai","secret")
        self.assertEqual(client.choose_model(),"gpt-5.4-mini")

    def test_legacy_file_key_is_supported(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"APIKEY-AVAL.txt").write_text("aa-test-key\n",encoding="utf-8")
            with mock.patch.dict("os.environ",{},clear=True), mock.patch("app.secure_secrets._keyring",return_value=None):
                self.assertEqual(get_provider_key("avalai",root),"aa-test-key")
                self.assertIn("APIKEY-AVAL.txt",provider_key_source("avalai",root))

    def test_avalai_connection_falls_back_to_chat_completions(self):
        client=AIProviderClient("avalai","secret")
        calls=[]
        def fake(url,key,**kwargs):
            calls.append(url)
            if url.endswith("/models"):
                return {"data":[{"id":"available-model"}]}
            if url.endswith("/responses"):
                raise RuntimeError("AI HTTP 404: responses unsupported")
            if url.endswith("/chat/completions"):
                return {"choices":[{"message":{"content":"آماده"}}]}
            raise AssertionError(url)
        with mock.patch("app.ai_providers._json_request", side_effect=fake):
            result=client.test_connection()
        self.assertEqual(result["model"],"available-model")
        self.assertTrue(any(x.endswith("/chat/completions") for x in calls))

class V84ExtractorTests(unittest.TestCase):
    def test_embedded_json_fills_missing_title_description_weight(self):
        snapshot={
            "source_url":"https://example.com/p/1","final_url":"https://example.com/p/1","title":"Fallback",
            "metas":{},"json_ld":[],"breadcrumbs":["Home","Tools"],"dom_images":[],"picture_sources":[],"links":[],
            "body_text":"","spec_rows":[],"labeled_sections":[],"network_json":[],
            "embedded_json":[json.dumps({"productName":"Strong Gear","productDescription":"A detailed engineering gear replacement for a machine.","filamentWeight":{"value":123,"unit":"g"},"material":"PA-CF"})]
        }
        page=parse_page_snapshot(snapshot)
        self.assertEqual(page.source_title,"Strong Gear")
        self.assertIn("engineering gear",page.source_description)
        self.assertEqual(page.estimated_weight_grams,123)
        self.assertTrue(any("material" in str(k).lower() for k in page.specs))

class V84MaterialTests(unittest.TestCase):
    def test_home_decor_does_not_push_pps_cf(self):
        use=infer_use_case("Moon lamp","decorative lamp for bedroom",["home decor"],{})
        recs=recommend_materials(use)
        top={r["code"] for r in recs[:4]}
        self.assertNotIn("pps_cf",top)
        self.assertGreater(next(r["score"] for r in recs if r["code"]=="pla"),next(r["score"] for r in recs if r["code"]=="pps_cf"))

    def test_gear_prefers_engineering_materials(self):
        use=infer_use_case("Drive gear","wear loaded gear",["industrial"],{})
        recs=recommend_materials(use)
        self.assertIn(recs[0]["code"],{"pa","pa_cf","ppa_cf","pps_cf"})

class V84ContentContracts(unittest.TestCase):
    def test_content_schema_includes_seo_hashtags_and_material_recommendations(self):
        from app.openai_content import CONTENT_SCHEMA
        props = CONTENT_SCHEMA["properties"]
        for key in ["seo_title_fa", "seo_description_fa", "hashtags_fa", "material_recommendations", "use_case_class"]:
            self.assertIn(key, props)

    def test_server_importer_has_phase39_optional_bridge(self):
        text = (ROOT / "server" / "store" / "management" / "commands" / "phase37_import_catalog_center.py").read_text(encoding="utf-8")
        self.assertIn("apply_phase39_product_intelligence", text)
        self.assertIn("material_recommendations_json", text)
        self.assertIn("CATALOG_INTELLIGENCE_V8_5_IMPORT=OK", text)

    def test_only_explicit_commercial_licenses_can_publish(self):
        for status in ("allowed", "owned", "public_domain"):
            self.assertTrue(commercial_license_allows_publish(status))
        for status in ("", "unknown", "review", "blocked"):
            self.assertFalse(commercial_license_allows_publish(status))

    def test_ack_requires_the_requested_publish_target(self):
        product_row = {"publish_as_product": 1, "publish_as_portfolio": 0}
        base = {"status": "created", "server_id": 10, "product_id": 20, "portfolio_id": None}
        self.assertTrue(ack_item_confirms_publish(base, product_row))
        self.assertFalse(ack_item_confirms_publish({**base, "product_id": None}, product_row))
        self.assertFalse(ack_item_confirms_publish({**base, "status": "review_required"}, product_row))

        portfolio_row = {"publish_as_product": 0, "publish_as_portfolio": 1}
        self.assertTrue(ack_item_confirms_publish({**base, "product_id": None, "portfolio_id": 30}, portfolio_row))

    def test_server_importer_validates_schema_and_image_mapping(self):
        text = (ROOT / "server" / "store" / "management" / "commands" / "phase37_import_catalog_center.py").read_text(encoding="utf-8")
        self.assertIn("Unsupported batch schema; expected 8.5", text)
        self.assertIn("local_image_files_json", text)
        self.assertIn("Editorial path escapes the batch root", text)

if __name__=="__main__": unittest.main()
