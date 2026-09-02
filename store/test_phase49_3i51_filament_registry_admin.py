from django import forms
from django.contrib import admin
from django.test import TestCase

from store.phase39_models import FilamentBrand, MaterialColorOption
from website.models import Material


class Phase493I51FilamentRegistryAdminTests(TestCase):
    def test_filament_brand_has_dedicated_admin_and_description(self):
        registered = admin.site._registry[FilamentBrand]
        self.assertIn("description", registered.search_fields)
        brand = FilamentBrand.objects.create(
            name="Bambu Lab",
            description="توضیح برند برای مدیریت و SEO",
        )
        self.assertEqual(str(brand), "Bambu Lab")

    def test_filament_admin_uses_managed_brand_choice_and_description_field(self):
        FilamentBrand.objects.create(name="Polymaker")
        material = Material.objects.create(
            name="PLA",
            main_usage="عمومی",
            sample_parts="قطعات تست",
        )
        option = MaterialColorOption.objects.create(
            material=material,
            name="مشکی",
            code="black",
            brand_name="Polymaker",
        )
        registered = admin.site._registry[MaterialColorOption]
        form = registered.form(instance=option)
        self.assertIsInstance(form.fields["brand_name"], forms.ChoiceField)
        self.assertIn(
            ("Polymaker", "Polymaker"),
            list(form.fields["brand_name"].choices),
        )
        identity_fields = dict(registered.fieldsets)["هویت Filament"]["fields"]
        self.assertIn("description", identity_fields)

    def test_material_admin_exposes_catalog_description_and_price(self):
        registered = admin.site._registry[Material]
        fields = {
            field
            for _title, options in registered.fieldsets
            for field in options.get("fields", ())
        }
        self.assertIn("catalog_description", fields)
        self.assertIn("price_per_kg", fields)
        self.assertIn("catalog_description", registered.search_fields)
