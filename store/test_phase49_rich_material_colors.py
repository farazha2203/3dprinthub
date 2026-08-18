from __future__ import annotations

from django.test import TestCase

from store.epic49_publish_options import normalized_material_color_options
from store.phase39_models import MaterialColorOption
from website.models import Material


class Phase49RichMaterialColorTests(TestCase):
    def test_independent_material_and_color_lists_expand_to_variants(self):
        data = {
            "material_options_json": '["PLA","PETG"]',
            "color_options_json": '[{"name":"شفاف","color_type":"transparent","hex":"#FFFFFF"},{"name":"آبی طلایی","color_type":"dual","hex":"#0066FF","secondary_hex":"#D4AF37"}]',
        }
        options = normalized_material_color_options(data)
        self.assertEqual(len(options), 4)
        self.assertEqual({item["material"] for item in options}, {"PLA", "PETG"})
        transparent = next(item for item in options if item["material"] == "PETG" and item["color"] == "شفاف")
        dual = next(item for item in options if item["material"] == "PLA" and item["color"] == "آبی طلایی")
        self.assertEqual(transparent["color_type"], "transparent")
        self.assertEqual(dual["secondary_hex"], "#D4AF37")

    def test_legacy_pair_payload_is_still_supported(self):
        options = normalized_material_color_options({
            "material_color_options_json": '[{"material":"PLA","color":"مشکی","hex":"#000000"}]'
        })
        self.assertEqual(options, [{
            "material": "PLA",
            "color": "مشکی",
            "hex": "#000000",
            "color_type": "solid",
            "secondary_hex": "",
            "tertiary_hex": "",
        }])

    def test_material_color_model_persists_rich_metadata(self):
        material = Material.objects.create(
            name="PETG",
            main_usage="تست",
            sample_parts="تست",
            is_active=True,
        )
        option = MaterialColorOption.objects.create(
            material=material,
            name="آبی طلایی",
            code="blue-gold",
            hex_code="#0066FF",
            color_type="dual",
            secondary_hex="#D4AF37",
            tertiary_hex="",
            is_active=True,
        )
        option.refresh_from_db()
        self.assertEqual(option.color_type, "dual")
        self.assertEqual(option.secondary_hex, "#D4AF37")
        self.assertEqual(option.get_color_type_display(), "دو رنگ")
