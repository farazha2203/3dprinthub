from __future__ import annotations
import io,json,tempfile,unittest
from pathlib import Path
from unittest import mock
from app.batch_packaging import BatchImagePackagingError,copy_images_into_model,materialize_selected_images,validate_batch_package
from app.crawler import download_public_file
from app.site_connection import SiteConnection,upload_batch

class _FakeResponse:
    def __init__(self,payload):
        self.payload=io.BytesIO(payload);self.status=200;self.headers={"Content-Length":str(len(payload))}
    def read(self,size=-1):return self.payload.read(size)
    def __enter__(self):return self
    def __exit__(self,*args):return False

class Phase482BatchImageTests(unittest.TestCase):
    def _row(self,root):
        urls=["https://makerworld.example/a.png?resize=1200","https://makerworld.example/b.png"]
        return {"id":16,"source_url":"https://makerworld.example/en/models/3130743","local_dir":str(root),"images_json":json.dumps(urls),"selected_images_json":json.dumps(urls),"primary_image_url":urls[0],"publish_as_product":1,"publish_as_portfolio":0}
    def test_materialize_downloads_missing_images_with_product_referer(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);calls=[]
            def downloader(url,target,referer):
                calls.append((url,target,referer));target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b"x"*512);return target
            pairs=materialize_selected_images(self._row(root),root,downloader=downloader)
            self.assertEqual(len(pairs),2);self.assertEqual(len(calls),2);self.assertTrue(all(p.is_file() for _,p in pairs));self.assertTrue(all(c[2].endswith("/3130743") for c in calls))
    def test_materialize_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            def downloader(url,target,referer):raise OSError("network unavailable")
            with self.assertRaisesRegex(BatchImagePackagingError,"IMAGE_NOT_PACKAGED"):
                materialize_selected_images(self._row(Path(temp)),Path(temp),downloader=downloader)
    def test_validate_good_building_batch(self):
        with tempfile.TemporaryDirectory() as temp:
            batch=Path(temp)/"desktop_catalog_v85_20260815_130000.building";model=batch/"models"/"makerworld_3130743";src=Path(temp)/"src";src.mkdir();a=src/"a.png";b=src/"b.png";a.write_bytes(b"a"*512);b.write_bytes(b"b"*512)
            mapped=copy_images_into_model([("https://x/a.png",a),("https://x/b.png",b)],model)
            (model/"desktop_editorial.json").write_text(json.dumps({"desktop_product_id":16,"publish_as_product":1,"images_json":json.dumps(["https://x/a.png","https://x/b.png"]),"local_image_files_json":json.dumps(mapped)}),encoding="utf-8")
            (batch/"batch_manifest.json").write_text(json.dumps({"schema_version":"8.5","batch_uuid":"u","batch_name":"desktop_catalog_v85_20260815_130000","models":[{"editorial":"models/makerworld_3130743/desktop_editorial.json"}]}),encoding="utf-8")
            self.assertEqual(validate_batch_package(batch),{"models":1,"images":2})
    def test_validation_rejects_empty_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            batch=Path(temp)/"desktop_catalog_v85_20260815_130001";model=batch/"models"/"makerworld_3130743";model.mkdir(parents=True)
            (model/"desktop_editorial.json").write_text(json.dumps({"desktop_product_id":16,"publish_as_product":1,"images_json":json.dumps(["https://x/a.png"]),"local_image_files_json":json.dumps([""])}),encoding="utf-8")
            (batch/"batch_manifest.json").write_text(json.dumps({"schema_version":"8.5","batch_uuid":"u","batch_name":batch.name,"models":[{"editorial":"models/makerworld_3130743/desktop_editorial.json"}]}),encoding="utf-8")
            with self.assertRaisesRegex(BatchImagePackagingError,"IMAGE_NOT_PACKAGED"):validate_batch_package(batch)
    @mock.patch("app.crawler.request.urlopen")
    def test_download_is_atomic_and_uses_referer(self,urlopen):
        payload=b"Z"*1024;urlopen.return_value=_FakeResponse(payload)
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"image.png";result=download_public_file("https://cdn.example/image.png",target,referer="https://makerworld.example/models/3130743")
            self.assertEqual(result.read_bytes(),payload);req=urlopen.call_args.args[0];self.assertEqual(req.headers.get("Referer"),"https://makerworld.example/models/3130743");self.assertFalse(target.with_name(target.name+".part").exists())
    def test_upload_preflight_rejects_before_ftp(self):
        with tempfile.TemporaryDirectory() as temp:
            batch=Path(temp)/"desktop_catalog_v85_20260815_130002";model=batch/"models"/"makerworld_3130743";model.mkdir(parents=True)
            (model/"desktop_editorial.json").write_text(json.dumps({"desktop_product_id":16,"publish_as_product":1,"images_json":json.dumps(["https://x/a.png"]),"local_image_files_json":json.dumps([""])}),encoding="utf-8")
            (batch/"batch_manifest.json").write_text(json.dumps({"schema_version":"8.5","batch_uuid":"u","batch_name":batch.name,"models":[{"editorial":"models/makerworld_3130743/desktop_editorial.json"}]}),encoding="utf-8")
            cfg=SiteConnection("ftp.example.com",21,"u","p","/root","https://example.com","token")
            with mock.patch("app.site_connection.connect_ftp") as connect:
                with self.assertRaisesRegex(BatchImagePackagingError,"IMAGE_NOT_PACKAGED"):upload_batch(cfg,batch)
                connect.assert_not_called()

if __name__=="__main__":unittest.main()
