from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product


class Phase50AdminHttpRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="phase50-admin-ci",
            email="phase50-admin-ci@example.invalid",
            password="phase50-admin-ci-password",
        )
        cls.category = Category.objects.create(
            name="CI Admin Category",
            slug="ci-admin-category",
            section="general",
            is_active=True,
        )
        cls.product = Product.objects.create(
            category=cls.category,
            title="CI Admin Product",
            slug="ci-admin-product",
            sku="CI-ADMIN-001",
            short_description="CI product used to render the real Product changelist.",
            description="CI product used to render the real Product changelist.",
            main_image="store/products/ci-admin-product.webp",
            is_active=True,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_product_changelist_renders_with_real_product_row(self):
        response = self.client.get(reverse("admin:store_product_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CI Admin Product")
        self.assertContains(response, 'id="changelist-filter"')
        self.assertContains(response, "admin/phase50-admin-console-v2.css")
        self.assertContains(response, "admin/phase50-admin-console-v2.js")
        self.assertContains(response, "admin/phase50-admin-shell-stability.css")

    def test_velzon_v2_static_contract_is_present(self):
        css_path = finders.find("admin/phase50-admin-console-v2.css")
        js_path = finders.find("admin/phase50-admin-console-v2.js")
        stability_path = finders.find("admin/phase50-admin-shell-stability.css")
        master_js_path = finders.find("admin/master-django.js")
        self.assertIsNotNone(css_path)
        self.assertIsNotNone(js_path)
        self.assertIsNotNone(stability_path)
        self.assertIsNotNone(master_js_path)

        css = Path(css_path).read_text(encoding="utf-8")
        js = Path(js_path).read_text(encoding="utf-8")
        stability = Path(stability_path).read_text(encoding="utf-8")
        master_js = Path(master_js_path).read_text(encoding="utf-8")

        for marker in (
            "admin-filter-drawer",
            "body.change-list #changelist",
            "admin-result-table",
            "admin-section-nav",
        ):
            self.assertIn(marker, css)
        for marker in (
            "buildFilterDrawer",
            "decorateResults",
            "buildFormSectionNav",
            'heading.textContent = "فیلترها"',
        ):
            self.assertIn(marker, js)
        for marker in (
            "--vz-vertical-menu-width: 290px",
            "html.admin-console-v2 .footer",
            "position: static !important",
            "transition-property: none !important",
        ):
            self.assertIn(marker, stability)
        self.assertIn("centerActiveInSidebar", master_js)
        self.assertIn("getSidebarScrollElement", master_js)
        self.assertNotIn("best.scrollIntoView", master_js)

    def test_product_change_page_renders_unified_workspace(self):
        response = self.client.get(reverse("admin:store_product_change", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        for title in (
            "اطلاعات کالا",
            "تصاویر",
            "فروش و موجودی",
            "پروفایل‌ها و سایز/وزن",
            "قیمت‌گذاری",
            "ارسال و بسته‌بندی",
            "SEO",
            "اسلایدر صفحه اول",
            "منبع و لایسنس",
            "همگام‌سازی ویندوز",
        ):
            self.assertContains(response, title)

    def test_representative_admin_pages_render_under_velzon_shell(self):
        for name in (
            "admin:index",
            "admin:website_order_changelist",
            "admin:store_productcomment_changelist",
            "admin:store_productreview_changelist",
            "admin:store_productlike_changelist",
        ):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "navbar-menu")
                self.assertContains(response, "admin/phase50-admin-console-v2.css")
                self.assertContains(response, "admin/phase50-admin-shell-stability.css")
