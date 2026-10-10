import json
import re

from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product, ServicePage
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
                route_name = {
                    "design-from-idea": "design_from_idea",
                    "jigs-fixtures-and-mold-prototypes": "jigs_fixtures_service",
                    "studio-props-and-photography-decor": "studio_props_service",
                    "custom-figure-design-and-printing": "custom_figure_service",
                    "rare-car-part-reconstruction": "rare_car_parts_service",
                    "rare-motorcycle-part-reconstruction": "rare_motorcycle_parts_service",
                    "rare-home-appliance-part-reconstruction": "rare_appliance_parts_service",
                    "architectural-maquette-and-model-making": "maquette_service",
                }[slug]
                response = self.client.get(reverse("store:" + route_name))
                body = response.content.decode()
                self.assertEqual(response.status_code, 200)
                self.assertIn(profile["title"], body)
                self.assertIn(profile["meta_description"], body)
                self.assertIn('name="robots" content="index,follow"', body)
                self.assertIn("ثبت درخواست و ارسال فایل/عکس", body)
                self.assertIn("/store/request-a-part/?service=" + slug, body)
                self.assertIn("application/ld+json", body)
                for private_equipment_detail in ("H2S", "Bambu Lab", "۳۴۰×۳۲۰×۳۴۰", "حجم ساخت اسمی"):
                    self.assertNotIn(private_equipment_detail.casefold(), body.casefold())
                if profile.get("article_sections"):
                    self.assertGreaterEqual(body.count("<h2"), len(profile["article_sections"]))
                    for article_section in profile["article_sections"]:
                        self.assertContains(response, article_section["title"])
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

    def test_studio_request_prefill_and_product_tag_search(self):
        prefill = request_prefill("studio-props-and-photography-decor")
        self.assertEqual(prefill["request_type"], "other")
        self.assertEqual(prefill["title"], "درخواست ساخت پراپ یا دکور سفارشی آتلیه")
        category = Category.objects.create(name="دکور", slug="studio-prop-test")
        product = Product.objects.create(
            category=category,
            title="استند دکور رومیزی",
            slug="studio-prop-search-test",
            sku="STUDIO-PROP-TEST-001",
            short_description="نمونهٔ تست",
            description="توضیح محصول",
            main_image="store/products/test.webp",
            hashtags="#آتلیه #پراپ_عکاسی",
        )
        decor_product = Product.objects.create(
            category=category,
            title="چراغ دکوراتیو رومیزی",
            slug="studio-decor-search-test",
            sku="STUDIO-DECOR-TEST-002",
            short_description="وسیلهٔ دکوراتیو مناسب صحنهٔ عکاسی محصول",
            description="شرح قطعهٔ تست",
            main_image="store/products/test-decor.webp",
        )
        response = self.client.get(reverse("store:product_list"), {"q": "پراپ_عکاسی"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, product.title)
        response = self.client.get(reverse("store:product_list"), {"q": "آتلیه"})
        self.assertContains(response, product.title)
        self.assertContains(response, decor_product.title)

    def test_sitemap_home_services_and_isfahan_page_link_to_each_new_landing(self):
        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "/store/services/design-from-idea/")
        self.assertContains(sitemap, "/store/services/jigs-fixtures-and-mold-prototypes/")
        self.assertContains(sitemap, "/store/services/studio-props-and-photography-decor/")
        for slug in (
            "custom-figure-design-and-printing", "rare-car-part-reconstruction",
            "rare-motorcycle-part-reconstruction", "rare-home-appliance-part-reconstruction",
            "architectural-maquette-and-model-making",
        ):
            self.assertContains(sitemap, "/store/services/" + slug + "/")
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, reverse("store:design_from_idea"))
        self.assertContains(home, reverse("store:jigs_fixtures_service"))
        self.assertContains(home, reverse("store:studio_props_service"))
        for route_name in (
            "custom_figure_service", "rare_car_parts_service", "rare_motorcycle_parts_service",
            "rare_appliance_parts_service", "maquette_service",
        ):
            self.assertContains(home, reverse("store:" + route_name))
        isfahan = self.client.get(reverse("store:isfahan_service_landing"))
        self.assertContains(isfahan, reverse("store:design_from_idea"))
        self.assertContains(isfahan, reverse("store:jigs_fixtures_service"))
        self.assertContains(isfahan, reverse("store:studio_props_service"))
        for route_name in (
            "custom_figure_service", "rare_car_parts_service", "rare_motorcycle_parts_service",
            "rare_appliance_parts_service", "maquette_service",
        ):
            self.assertContains(isfahan, reverse("store:" + route_name))

    def test_each_new_custom_landing_prefills_the_correct_request_type(self):
        expected = {
            "custom-figure-design-and-printing": ("custom_figure_service", "custom_figure"),
            "rare-car-part-reconstruction": ("rare_car_parts_service", "automotive"),
            "rare-motorcycle-part-reconstruction": ("rare_motorcycle_parts_service", "motorcycle"),
            "rare-home-appliance-part-reconstruction": ("rare_appliance_parts_service", "home_appliance"),
            "architectural-maquette-and-model-making": ("maquette_service", "academic"),
        }
        for slug, (route_name, request_type) in expected.items():
            with self.subTest(slug=slug):
                response = self.client.get(reverse("store:" + route_name))
                self.assertContains(response, "/store/request-a-part/?service=" + slug)
                self.assertEqual(request_prefill(slug)["request_type"], request_type)

    def test_service_landings_show_only_real_matching_public_catalog_products(self):
        cases = (
            ("rare_car_parts_service", "automotive", "قاب داشبورد خودرو", "car-part"),
            ("rare_motorcycle_parts_service", "motorcycle", "نگهدارنده موتورسیکلت", "motorcycle-part"),
            ("rare_appliance_parts_service", "home_appliance", "دستگیره یخچال", "appliance-part"),
            ("maquette_service", "academic", "ماکت معماری اصفهان", "maquette-sample"),
            ("custom_figure_service", "general", "فیگور سه‌بعدی سفارشی", "figure-sample"),
        )
        for route_name, section, title, slug in cases:
            category = Category.objects.create(
                name=title, slug=slug, section=section,
            )
            product = Product.objects.create(
                category=category, title=title, slug=slug, sku=slug.upper(),
                short_description="نمونه محصول قابل مشاهده", description="شرح نمونه",
                main_image="store/products/" + slug + ".webp",
            )
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse("store:" + route_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, product.title)
                self.assertContains(response, product.get_absolute_url())

        hidden_category = Category.objects.create(
            name="قطعه غیرفعال", slug="inactive-test", section="automotive", is_active=False
        )
        Product.objects.create(
            category=hidden_category, title="قطعه خودرو پنهان", slug="hidden-car-part",
            sku="HIDDEN-CAR-1", short_description="پنهان", description="پنهان",
            main_image="store/products/hidden.webp",
        )
        response = self.client.get(reverse("store:rare_car_parts_service"))
        self.assertNotContains(response, "قطعه خودرو پنهان")

    def test_organization_entity_uses_local_service_type_and_verified_instagram(self):
        request = self.client.get("/").wsgi_request
        graph = json.loads(str(organization_schema_json(self.seo, request)))["@graph"]
        business = next(item for item in graph if item.get("@id") == "https://3dprinthub.ir/#organization")
        self.assertEqual(business["@type"], "ProfessionalService")
        self.assertEqual(business["address"]["addressLocality"], "اصفهان")
        self.assertIn("https://www.instagram.com/3dprinthub_ir/", business["sameAs"])
