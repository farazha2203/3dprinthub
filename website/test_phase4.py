from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from store.models import StoreAddress
from website.forms_phase4 import StoreAddressForm, CustomerProfileForm
from website.jalali import parse_jalali_date, format_jalali
from website.models import CustomerProfile, SEOSettings
User=get_user_model()
class JalaliAndAddressTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username="09131111111",password="x",first_name="علی",last_name="تست")
        self.profile=CustomerProfile.objects.create(user=self.user,phone=self.user.username,first_name="علی",last_name="تست")
    def test_jalali_conversion(self):
        self.assertEqual(parse_jalali_date("1358/09/28"), date(1979,12,19))
        self.assertEqual(format_jalali(date(1979,12,19),numeric=True), "1358/09/28")
    def test_profile_accepts_jalali(self):
        form=CustomerProfileForm(data={"first_name":"علی","last_name":"تست","father_name":"حسن","birth_date_jalali":"1358/09/28","gender":"male","phone":"09131111111","email":"","national_code":"","landline":"","occupation":"","company_name":""},instance=self.profile)
        self.assertTrue(form.is_valid(),form.errors)
        saved=form.save(); self.assertEqual(saved.birth_date,date(1979,12,19))
    def test_postal_code_required(self):
        form=StoreAddressForm(data={"title":"منزل","full_name":"علی تست","phone":"09131111111","province":"اصفهان","city":"اصفهان","address":"آدرس","postal_code":""})
        self.assertFalse(form.is_valid()); self.assertIn("postal_code",form.errors)
    def test_city_belongs_to_province(self):
        form=StoreAddressForm(data={"title":"منزل","full_name":"علی تست","phone":"09131111111","province":"اصفهان","city":"تهران","address":"آدرس","postal_code":"8174671234"})
        self.assertFalse(form.is_valid()); self.assertIn("city",form.errors)
class ThemeAndSecurityTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username="09132222222",password="x",first_name="مینا",last_name="تست")
        CustomerProfile.objects.create(user=self.user,phone=self.user.username,first_name="مینا",last_name="تست")
    def test_theme_update(self):
        self.client.force_login(self.user)
        r=self.client.post(reverse("website:customer_theme_update"),{"theme":"hybrid","seen":"1"})
        self.assertEqual(r.status_code,200); self.user.customer_profile.refresh_from_db(); self.assertEqual(self.user.customer_profile.theme_preference,"hybrid"); self.assertTrue(self.user.customer_profile.theme_prompt_seen)
    def test_normal_customer_cannot_open_admin(self):
        self.client.force_login(self.user); self.assertEqual(self.client.get('/admin/').status_code,404)
    def test_staff_can_open_admin(self):
        self.user.is_staff=True; self.user.save(update_fields=['is_staff']); self.client.force_login(self.user); self.assertEqual(self.client.get('/admin/').status_code,200)
    def test_robots_blocks_private_paths(self):
        SEOSettings.objects.create(site_url="https://3dprinthub.ir")
        response=self.client.get('/robots.txt'); self.assertContains(response,'Disallow: /admin/'); self.assertContains(response,'Disallow: /customer/')
