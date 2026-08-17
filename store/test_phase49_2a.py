from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, reverse

from website.order_intake import Phase10OrderForm

from .catalog_automation import external_model_sync_enabled, process_catalog_queue, queue_due_catalog_sources
from .epic49_catalog_profile import ProductCatalogProfile
from .models import Category, Product


class Phase492APublicIntakeTests(TestCase):
    def test_direct_external_intake_named_routes_are_removed(self):
        removed_names = (
            "external_catalog",
            "external_catalog_detail",
            "external_catalog_sitemap",
            "external_catalog_refresh",
            "external_link_analyzer",
            "external_link_analysis",
            "external_link_analysis_status",
            "external_link_reanalyze",
            "customer_link_analyses",
            "external_link_manual_review",
        )
        for name in removed_names:
            with self.subTest(name=name):
                with self.assertRaises(NoReverseMatch):
                    reverse(f"store:{name}")

    def test_direct_external_intake_paths_are_not_public(self):
        for path in (
            "/store/ready-models/",
            "/store/ready-models/1/",
            "/store/ready-models-sitemap.xml",
            "/store/link-analyzer/",
            "/store/account/link-analyses/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_core_store_routes_remain_available(self):
        self.assertEqual(reverse("store:product_list"), "/store/")
        self.assertEqual(reverse("store:cart_detail"), "/store/cart/")
        self.assertEqual(reverse("store:checkout"), "/store/checkout/")

    def test_customer_order_form_excludes_ready_catalog_mode(self):
        form = Phase10OrderForm()
        modes = {value for value, _label in form.fields["request_mode"].choices}
        self.assertIn("new_part", modes)
        self.assertNotIn("ready_catalog", modes)

    @override_settings(EXTERNAL_MODEL_SYNC_ENABLED=False)
    def test_external_model_automation_is_disabled(self):
        self.assertFalse(external_model_sync_enabled())
        self.assertEqual(queue_due_catalog_sources(), [])
        self.assertEqual(process_catalog_queue(), [])


class Phase492AWindowsCatalogProductNavigationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Phase 49.2A Windows",
            slug="phase-49-2a-windows",
            section="industrial",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=self.category,
            title="محصول تست ورودی برنامه ویندوز",
            slug="windows-catalog-phase49-2a-product",
            sku="WIN-49-2A-001",
            short_description="محصول تست برای قفل مسیر کلیک کاتالوگ ویندوز",
            description="این رکورد رفتار محصول منتشرشده از Catalog Center ویندوز را شبیه‌سازی می‌کند.",
            main_image="store/products/windows-phase49-2a.webp",
            is_active=True,
        )
        self.profile = ProductCatalogProfile.objects.create(
            product=self.product,
            public_slug=self.product.slug,
            desktop_product_id=4902001,
            batch_uuid="phase49-2a-windows-batch",
            source_hash="49" * 32,
            product_type="ready_product",
            availability_status="made_to_order",
            has_3d_file=True,
        )

    def test_windows_catalog_product_card_url_opens_detail(self):
        self.assertIsNotNone(self.product.catalog_profile.desktop_product_id)
        detail_url = self.product.get_absolute_url()
        self.assertEqual(detail_url, f"/store/product/{self.product.slug}/")

        list_response = self.client.get(reverse("store:product_list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, detail_url)

        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, self.product.title)

    def test_windows_catalog_product_id_fallback_opens_detail(self):
        response = self.client.get(reverse("epic49_product_by_id", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.title)
