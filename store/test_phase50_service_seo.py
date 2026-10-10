import json
import re

from django.test import TestCase
from django.urls import reverse

from store.models import ServicePage
from store.phase50_service_seo import SERVICE_GUIDES, STATIC_SERVICE_LANDINGS, request_prefill
from store.templatetags.store_seo import organization_schema_json
from website.models import SEOSettings


class ServiceSeoAndIntakeTests(TestCase):
    def setUp(self):
        self.seo = SEOSettings.objects.create(
            site_url="https://3dprinthub.ir",
            site_name="3DprintHub.ir",
            organization_name="3DprintHub",
            allow_search_indexing=True,
            address_locality="اصفهان",
            address_region="اصفهان",
        )

    def test_each_new_service_landing_has_unique_persian_metadata_canonical_and_service_schema(self):
        seen_titles = set()
        for slug, profile in STATIC_SERVICE_LANDINGS.items():
            with self.subTest(slug=slug):
                response = self.client.get(reverse("store:" + ("design_from_idea" if slug == "design-from-idea" else "jigs_fixtures_service")))
                body = response.content.decode()
                self.assertEqual(response.status_code, 200)
                self.assertIn(profile["title"], body)
                self.assertIn(profile["meta_description"], body)
                self.assertIn('name="robots" content="index,follow"', body)
                self.assertIn("ثبت درخواست و ارسال فایل/عکس", body)
                self.assertIn("/store/request-a-part/?service=" + slug, body)
                self.assertIn("application/ld+json", body)
                title = profile["meta_title"]
                self.assertNotIn(title, seen_titles)
                seen_titles.add(title)
                schema_blocks = re.findall(r"<script type=\"application/ld\+json\">(.*?)</script>", body, re.S)
                graph = [item for block in schema_blocks for item in json.loads(block).get("@graph", [])]
                service = next(item for item in graph if item.get("@type") == "Service")
                self.assertEqual(service["name"], profile["title"])
                self.assertIn(slug, service["url"])

    def test_all_existing_service_guides_render_and_seed_defaults_get_better_metadata(self):
        for slug, guide in SERVICE_GUIDES.items():
            page = ServicePage.objects.create(
                service_type="industrial",
                title="عنوان صفحه",
                slug=slug,
                short_description="توضیح کوتاه seed شده",
                content="محتوای اولیه",
                meta_title="عنوان صفحه | 3DprintHub",
                meta_description="توضیح کوتاه seed شده",
            )
            with self.subTest(slug=slug):
                response = self.client.get(reverse("store:service_page", args=[slug]))
                body = response.content.decode()
                self.assertEqual(response.status_code, 200)
                self.assertIn(guide["lead"], body)
                self.assertIn(guide["meta_title"], body)
                self.assertIn(guide["meta_description"], body)
                self.assertIn("برای بررسی چه بفرستم؟", body)
                self.assertIn("?service=" + slug, body)
            page.refresh_from_db()
            self.assertEqual(page.title, "عنوان صفحه")

    def test_custom_service_metadata_is_preserved(self):
        page = ServicePage.objects.create(
            service_type="industrial",
            title="مهندسی معکوس",
            slug="reverse-engineering-parts",
            short_description="متن کوتاه",
            content="محتوا",
            meta_title="عنوان ویژهٔ ثبت‌شده در پنل",
            meta_description="توضیح ویژهٔ ثبت‌شده در پنل",
        )
        response = self.client.get(reverse("store:service_page", args=[page.slug]))
        body = response.content.decode()
        self.assertIn("عنوان ویژهٔ ثبت‌شده در پنل", body)
        self.assertIn("توضیح ویژهٔ ثبت‌شده در پنل", body)

    def test_request_form_prefills_only_known_service_values(self):
        cases = {
            "design-from-idea": ("other", "درخواست طراحی سه‌بعدی از ایده یا نقشه"),
            "jigs-fixtures-and-mold-prototypes": ("industrial", "درخواست بررسی جیگ، فیکسچر یا مدل قالب"),
            "reverse-engineering-parts": ("industrial", "درخواست مهندسی معکوس و بازسازی قطعه"),
        }
        for slug, expected in cases.items():
            with self.subTest(slug=slug):
                self.assertEqual((request_prefill(slug)["request_type"], request_prefill(slug)["title"]), expected)
                response = self.client.get(reverse("store:product_request"), {"service": slug})
                body = response.content.decode()
                self.assertEqual(response.status_code, 200)
                self.assertIn(expected[1], body)
        self.assertEqual(request_prefill("https://attacker.invalid"), {})
        self.assertEqual(request_prefill("made-up-service"), {})

    def test_sitemap_home_services_and_isfahan_page_link_to_each_new_landing(self):
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "/store/services/design-from-idea/")
        self.assertContains(sitemap, "/store/services/jigs-fixtures-and-mold-prototypes/")
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, reverse("store:design_from_idea"))
        self.assertContains(home, reverse("store:jigs_fixtures_service"))
        isfahan = self.client.get(reverse("store:isfahan_service_landing"))
        self.assertContains(isfahan, reverse("store:design_from_idea"))
        self.assertContains(isfahan, reverse("store:jigs_fixtures_service"))

    def test_organization_entity_uses_local_service_type_and_verified_instagram(self):
        request = self.client.get("/").wsgi_request
        graph = json.loads(str(organization_schema_json(self.seo, request)))["@graph"]
        business = next(item for item in graph if item.get("@id") == "https://3dprinthub.ir/#organization")
        self.assertEqual(business["@type"], "ProfessionalService")
        self.assertEqual(business["address"]["addressLocality"], "اصفهان")
        self.assertIn("https://www.instagram.com/3dprinthub_ir/", business["sameAs"])
