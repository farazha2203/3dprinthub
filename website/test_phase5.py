from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from store.models import StoreAddress
from website.forms_phase5 import StoreAddressForm
from website.models import IranCity, IranCounty, IranProvince

class IranLocationTests(TestCase):
    def setUp(self):
        self.province=IranProvince.objects.create(name="اصفهان")
        self.county=IranCounty.objects.create(province=self.province,name="اصفهان")
        IranCity.objects.create(province=self.province,county=self.county,name="اصفهان")
        IranCity.objects.create(province=self.province,county=self.county,name="بهارستان")
    def test_province_county_city_api(self):
        r=self.client.get(reverse("website:iran_counties"),{"province":"اصفهان"}); self.assertEqual(r.status_code,200); self.assertIn("اصفهان",r.json()["counties"])
        r=self.client.get(reverse("website:iran_cities_v2"),{"province":"اصفهان","county":"اصفهان"}); self.assertIn("بهارستان",r.json()["cities"])
    def test_address_form_rejects_wrong_city(self):
        form=StoreAddressForm(data={"title":"منزل","full_name":"علی احمدی","phone":"09130000000","recipient_national_code":"","province":"اصفهان","county":"اصفهان","city":"شیراز","district":"","address":"خیابان تست","plaque":"1","unit":"","postal_code":"8134567890","delivery_notes":"","is_default":True})
        self.assertFalse(form.is_valid()); self.assertIn("city",form.errors)
    def test_address_form_accepts_hierarchy(self):
        form=StoreAddressForm(data={"title":"منزل","full_name":"علی احمدی","phone":"09130000000","recipient_national_code":"","province":"اصفهان","county":"اصفهان","city":"بهارستان","district":"","address":"خیابان تست","plaque":"1","unit":"","postal_code":"8134567890","delivery_notes":"","is_default":True})
        self.assertTrue(form.is_valid(),form.errors)

from django.core.management import call_command

class IranLocationSeedAndWidgetTests(TestCase):
    def test_offline_seed_loads_all_provinces_and_form_widgets(self):
        call_command("seed_iran_locations", offline=True, clear=True, verbosity=0)
        self.assertEqual(IranProvince.objects.count(), 31)
        form = StoreAddressForm()
        self.assertEqual(len(form.fields["province"].choices), 32)
        self.assertEqual(form.fields["province"].widget.attrs.get("data-iran-province"), "1")
        self.assertEqual(form.fields["county"].widget.attrs.get("data-county-endpoint"), "/customer/locations/counties/")
        self.assertEqual(form.fields["city"].widget.attrs.get("data-city-endpoint"), "/customer/locations/cities-v2/")
