from __future__ import annotations
import ast, unittest
from pathlib import Path
import app.main as m

class V82UIContractTests(unittest.TestCase):
    def test_required_high_volume_ui_methods_exist(self):
        required={"refresh_published","open_published_in_editor","bulk_ai_selected","bulk_ai_pending","bulk_price_selected","add_local_images_to_product","add_image_url_to_product","remove_current_image_from_product","paste_openai_key","toggle_openai_key_visibility"}
        missing=sorted(x for x in required if not hasattr(m.App,x))
        self.assertEqual(missing,[])

    def test_light_theme_and_status_tags_are_defined(self):
        text=Path(m.__file__).read_text(encoding="utf-8")
        for token in ["#071827","#c99a2e","needs_update","published_tree","گالری تصاویر","AI همه نیازمندها"]:
            self.assertIn(token,text)

if __name__ == "__main__":unittest.main(verbosity=2)
