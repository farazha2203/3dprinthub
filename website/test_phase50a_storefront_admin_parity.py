from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import ImportedPrintAsset, Product
from website.models import HomepageHeroSlide
from website.phase50a_storefront_admin_parity import (
    add_assets_to_homepage_slider,
    add_products_to_homepage_slider,
    remove_assets_from_homepage_slider,
    remove_products_from_homepage_slider,
)


class Phase50AStorefrontAdminParityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="phase50-storefront-admin",
            email="phase50-storefront@example.com",
            password="safe-test-password",
        )
        self.client.force_login(self.admin_user)

    @staticmethod
    def _action_names(model_admin):
        names = set()
        for action in list(getattr(model_admin, "actions", ()) or ()):
            names.add(action if isinstance(action, str) else getattr(action, "__name__", ""))
        return names

    def test_store_product_admin_exposes_slider_add_and_remove_actions(self):
        model_admin = admin.site._registry.get(Product)
        self.assertIsNotNone(model_admin)
        names = self._action_names(model_admin)
        self.assertIn(add_products_to_homepage_slider.__name__, names)
        self.assertIn(remove_products_from_homepage_slider.__name__, names)

    def test_imported_asset_admin_exposes_slider_add_and_remove_actions(self):
        model_admin = admin.site._registry.get(ImportedPrintAsset)
        self.assertIsNotNone(model_admin)
        names = self._action_names(model_admin)
        self.assertIn(add_assets_to_homepage_slider.__name__, names)
        self.assertIn(remove_assets_from_homepage_slider.__name__, names)

    def test_hero_admin_exposes_professional_random_controls(self):
        model_admin = admin.site._registry.get(HomepageHeroSlide)
        self.assertIsNotNone(model_admin)
        self.assertEqual(
            model_admin.change_list_template,
            "admin/website/homepageheroslide/change_list.html",
        )
        response = self.client.get(reverse("admin:website_homepageheroslide_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "۵ محصول رندوم")
        self.assertContains(response, "۱۰ محصول رندوم")
        self.assertContains(response, "حذف همه از اسلایدر")

    def test_random_and_deactivate_mutations_are_post_only(self):
        for url_name in [
            "admin:website_homepageheroslide_random_5",
            "admin:website_homepageheroslide_random_10",
            "admin:website_homepageheroslide_deactivate_all",
        ]:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 405)

    def test_deactivate_all_preserves_records(self):
        before = HomepageHeroSlide.objects.count()
        response = self.client.post(reverse("admin:website_homepageheroslide_deactivate_all"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(HomepageHeroSlide.objects.count(), before)

    def test_command_center_surfaces_storefront_checkout_controls(self):
        response = self.client.get(reverse("phase50_admin_command_center"))
        self.assertEqual(response.status_code, 200)
        for label in [
            "کاتالوگ، ویترین و Checkout",
            "محصولات فروشگاه",
            "محصولات واردشده Catalog",
            "اسلایدر صفحه اصلی",
            "کدهای تخفیف",
            "روش‌های ارسال",
            "مالیات، بسته‌بندی و قیمت‌گذاری",
            "آدرس‌های مشتریان",
            "استان‌ها",
            "شهرستان‌ها",
            "شهرها",
        ]:
            self.assertContains(response, label)

    def test_command_center_records_next_shipping_and_payment_hardening(self):
        response = self.client.get(reverse("phase50_admin_command_center"))
        self.assertContains(response, "پست / تیپاکس / ماهکس")
        self.assertContains(response, "Verify سروربه‌سرور درگاه")
