from django.contrib.auth import get_user_model
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
