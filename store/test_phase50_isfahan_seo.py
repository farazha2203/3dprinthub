import json

from django.test import TestCase
from django.urls import reverse

from store.models import Category
from store.templatetags.store_seo import (
    category_search_title,
    isfahan_service_schema_json,
    organization_schema_json,
)
from website.models import SEOSettings


class IsfahanLandingPageTests(TestCase):
    def setUp(self):
        self.seo = SEOSettings.objects.create(
            site_url="https://3dprinthub.ir",
            site_name="3DprintHub.ir",
            organization_name="3DprintHub",
            allow_search_indexing=True,
        )

    def test_isfahan_page_renders_unique_persian_metadata_and_canonical(self):
        response = self.client.get(reverse("store:isfahan_service_landing"))
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "چاپ سه‌بعدی و مهندسی معکوس در اصفهان")
        self.assertContains(response, 'name="robots" content="index,follow"')
        self.assertContains(response, 'property="og:site_name" content="3DprintHub"')
        self.assertContains(response, 'name="twitter:title"')
        self.assertIn(
            '<link rel="canonical" href="http://testserver/store/services/3d-printing-isfahan/">',
            body,
        )

    def test_isfahan_service_schema_is_local_and_uses_existing_organization(self):
        response = self.client.get(reverse("store:isfahan_service_landing"), secure=True)
        data = json.loads(str(isfahan_service_schema_json(response.wsgi_request, self.seo)))
        service = data["@graph"][0]

        self.assertEqual(service["@type"], "Service")
        self.assertEqual(service["areaServed"]["@type"], "City")
        self.assertEqual(service["areaServed"]["name"], "اصفهان")
        self.assertEqual(service["provider"]["@id"], "https://3dprinthub.ir/#organization")
        self.assertEqual(service["url"], "https://testserver/store/services/3d-printing-isfahan/")

    def test_static_sitemap_contains_isfahan_page(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/store/services/3d-printing-isfahan/")

    def test_known_english_category_slugs_get_farsi_title_and_visible_label(self):
        expected = {
            "mounts-brackets": "پایه‌ها و براکت‌های چاپ سه‌بعدی",
            "plant-pots": "گلدان و اکسسوری دکوراتیو چاپ سه‌بعدی",
            "toys-games": "اسباب‌بازی و بازی‌های چاپ سه‌بعدی",
        }
        for slug, phrase in expected.items():
            with self.subTest(slug=slug):
                Category.objects.create(name=slug, slug=slug)
                response = self.client.get(reverse("store:category", args=[slug]))
                body = response.content.decode()
                self.assertEqual(response.status_code, 200)
                self.assertIn(phrase, body)
                self.assertNotIn(f"<title>{slug} | 3DprintHub</title>", body)

    def test_editorial_persian_category_title_is_preserved(self):
        category = Category.objects.create(
            name="mounts-brackets",
            slug="mounts-brackets",
            meta_title="عنوان فارسی ثبت‌شده توسط مدیر",
        )
        self.assertEqual(category_search_title(category), "عنوان فارسی ثبت‌شده توسط مدیر")

    def test_organization_schema_uses_brand_name_and_only_repairs_verified_isfahan_typo(self):
        self.seo.address_locality = "hwtihk"
        self.seo.address_region = "اصفهان"
        self.seo.save()
        request = self.client.get("/").wsgi_request
        data = json.loads(str(organization_schema_json(self.seo, request)))
        organization, website = data["@graph"]

        self.assertEqual(organization["address"]["addressLocality"], "اصفهان")
        self.assertEqual(website["name"], "3DprintHub")
        self.assertEqual(website["alternateName"], "3DprintHub.ir")

    def test_homepage_social_metadata_uses_configured_editorial_fields(self):
        response = self.client.get("/")
        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn('property="og:site_name" content="3DprintHub"', body)
        self.assertIn('name="twitter:card" content="summary_large_image"', body)
