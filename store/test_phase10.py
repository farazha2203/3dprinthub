from datetime import time
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse
from PIL import Image

from store.catalog_automation import homepage_catalog_assets, queue_catalog_source
from store.market_pricing import calculate_material_market_price, effective_fx_rates
from store.models import (
    CatalogAssetMetrics,
    CatalogAssetPublication,
    CatalogQueuedJob,
    CatalogSourcePolicy,
    CatalogSourceSchedule,
    CatalogSyncRun,
    ExchangeRateProvider,
    ExchangeRateSnapshot,
    ImportedPrintAsset,
    MarketPricingSetting,
    PrintCatalogSource,
)
from website.models import CustomerReusableModel, Material, OrderIntakeDetail
from website.order_intake import Phase10OrderForm


def image_upload(name="part.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (32, 32), "white").save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


def create_material(name="PLA"):
    data = {"name": name, "main_usage": "تست", "sample_parts": "قطعه تست"}
    field_names = {field.name for field in Material._meta.fields}
    if "is_active" in field_names:
        data["is_active"] = True
    return Material.objects.create(**data)


class Phase10MarketPriceTests(TestCase):
    def setUp(self):
        self.setting = MarketPricingSetting.load()
        self.setting.enabled = True
        self.setting.default_import_cost_percent = 0
        self.setting.default_margin_percent = 100
        self.setting.price_rounding_toman = 100
        self.setting.save()
        self.provider = ExchangeRateProvider.objects.create(
            name="تست دستی",
            code="test-manual",
            provider_type="manual",
            manual_sell_rate_toman=195000,
            is_active=True,
        )

    def test_daily_high_is_never_lowered_during_day(self):
        today = timezone.localdate()
        same_time = timezone.now()
        ExchangeRateSnapshot.objects.create(provider=self.provider, sell_rate_toman=195000, local_date=today, observed_at=same_time)
        ExchangeRateSnapshot.objects.create(provider=self.provider, sell_rate_toman=187000, local_date=today, observed_at=same_time)
        current, high = effective_fx_rates()
        self.assertEqual(current, Decimal("187000"))
        self.assertEqual(high, Decimal("195000"))

    def test_material_price_uses_daily_high_and_margin(self):
        material = create_material()
        material.market_pricing_enabled = True
        material.bambu_reference_weight_grams = 1000
        material.market_import_cost_percent = 0
        material.market_margin_percent = 100
        material.save()
        snapshot = calculate_material_market_price(
            material,
            fx_current=187000,
            fx_daily_high=195000,
            bambu_usd_price=Decimal("12.82"),
        )
        material.refresh_from_db()
        self.assertEqual(snapshot.fx_daily_high_toman, Decimal("195000"))
        self.assertEqual(material.market_sale_price_per_gram, 5000)
        self.assertEqual(material.public_sale_price_per_gram, 5000)


class Phase10CatalogAutomationTests(TestCase):
    def setUp(self):
        self.source = PrintCatalogSource.objects.create(
            name="Printables Test",
            code="printables-test",
            base_url="https://www.printables.com/",
            allowed_domains="www.printables.com,printables.com",
            adapter_key="printables",
        )
        self.policy = CatalogSourcePolicy.objects.create(
            source=self.source,
            source_kind="printables",
            discovery_mode="public_html",
            public_display_policy="licensed_only",
            default_limit=200,
            maximum_limit=500,
        )
        self.schedule = CatalogSourceSchedule.objects.create(
            policy=self.policy,
            enabled=True,
            run_time=time(3, 30),
            requested_limit=200,
        )

    def test_manual_queue_creates_nonblocking_job(self):
        run = queue_catalog_source(schedule=self.schedule, trigger="manual")
        self.assertEqual(run.status, "queued")
        self.assertTrue(CatalogQueuedJob.objects.filter(run=run, trigger="manual").exists())


    def test_admin_automation_dashboard_renders(self):
        admin_user = User.objects.create_superuser(
            username="catalog-admin", email="catalog@example.com", password="StrongPass123!"
        )
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin:store_catalogautomationdashboard_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد همگام‌سازی")
        self.assertContains(response, "صف همه منابع")
        self.assertContains(response, "پردازش صف الآن")
        self.assertContains(response, "بروزرسانی نرخ دلار")
        self.assertContains(response, "بروزرسانی Bambu و متریال")

    def test_admin_can_queue_single_source_from_dashboard_button(self):
        admin_user = User.objects.create_superuser(
            username="queue-admin", email="queue@example.com", password="StrongPass123!"
        )
        self.client.force_login(admin_user)
        response = self.client.post(
            reverse(
                "admin:store_catalogautomationdashboard_queue_source",
                args=[self.schedule.pk],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CatalogSyncRun.objects.filter(
                source=self.source, status="queued"
            ).exists()
        )

    def test_admin_can_refresh_manual_fx_from_dashboard_button(self):
        ExchangeRateProvider.objects.filter(code="manual-usd").delete()
        ExchangeRateProvider.objects.create(
            name="نرخ دستی داشبورد",
            code="dashboard-manual",
            provider_type="manual",
            manual_sell_rate_toman=191000,
            is_active=True,
            priority=1,
        )
        admin_user = User.objects.create_superuser(
            username="fx-admin", email="fx@example.com", password="StrongPass123!"
        )
        self.client.force_login(admin_user)
        response = self.client.post(
            reverse("admin:store_catalogautomationdashboard_refresh_fx")
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ExchangeRateSnapshot.objects.filter(
                sell_rate_toman=Decimal("191000")
            ).exists()
        )

    def test_homepage_queryset_contains_only_safe_public_asset(self):
        asset = ImportedPrintAsset.objects.create(
            source=self.source,
            source_url="https://www.printables.com/model/1",
            external_id="1",
            title="Industrial bracket",
            preview_image=image_upload("preview.jpg"),
        )
        metrics = CatalogAssetMetrics.objects.create(
            asset=asset,
            source_kind="printables",
            segment="industrial",
            commercial_use_allowed=True,
            license_review_status="allowed",
            public_approved=True,
            downloads_count=1000,
        )
        CatalogAssetPublication.objects.create(metrics=metrics, show_on_homepage=True)
        self.assertEqual(list(homepage_catalog_assets(slider=True)), [asset])


@override_settings(PRIVATE_MEDIA_ROOT="/tmp/phase10-private-tests")
class Phase10OrderIntakeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="09120000000", password="pass12345")
        self.material = create_material("PETG")
        self.base_data = {
            "first_name": "علی",
            "last_name": "احمدی",
            "phone": "09120000000",
            "service_type": "3d_print",
            "material": self.material.pk,
            "color": "مشکی",
            "quantity": 1,
            "description": "قطعه تست",
            "request_mode": "new_part",
            "usage_environment": "outdoor",
            "exact_dimensions": "100x20x10 mm",
        }

    def test_new_part_requires_four_named_views(self):
        form = Phase10OrderForm(data=self.base_data, files={"photo_top": image_upload("top.jpg")}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("الزامی", str(form.non_field_errors()))

    def test_new_part_saves_four_to_six_photos_and_details(self):
        files = {
            "photo_top": image_upload("top.jpg"),
            "photo_front": image_upload("front.jpg"),
            "photo_right": image_upload("right.jpg"),
            "photo_left": image_upload("left.jpg"),
        }
        form = Phase10OrderForm(data=self.base_data, files=files, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        order = form.save_order(customer=self.user)
        self.assertEqual(order.reference_photos.count(), 4)
        self.assertEqual(order.intake_detail.usage_environment, "outdoor")


    def test_invalid_ready_catalog_asset_is_rejected(self):
        data = dict(self.base_data)
        data.update({"request_mode": "ready_catalog", "ready_catalog_asset_id": 999999})
        form = Phase10OrderForm(data=data, files={}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("قابل سفارش عمومی نیست", str(form.errors))

    def test_private_model_download_is_staff_only(self):
        saved = CustomerReusableModel.objects.create(
            customer=self.user,
            display_name="مدل محرمانه",
            internal_code="PRIVATE-001",
            model_file=SimpleUploadedFile("private.step", b"private model bytes"),
            file_format="STEP",
        )
        url = reverse("website:private_model_download", args=[saved.public_token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        admin_user = User.objects.create_superuser(
            username="phase10-admin", email="admin@example.com", password="StrongPass123!"
        )
        self.client.force_login(admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.headers.get("Content-Disposition", ""))

    def test_reorder_uses_private_saved_model_without_new_photos(self):
        saved = CustomerReusableModel.objects.create(
            customer=self.user,
            display_name="چرخ‌دنده دستگاه",
            internal_code="MODEL-001",
            model_file=SimpleUploadedFile("gear.stl", b"solid gear\nendsolid gear"),
            file_format="STL",
        )
        data = dict(self.base_data)
        data.update({"request_mode": "reorder_model", "reusable_model": saved.pk})
        form = Phase10OrderForm(data=data, files={}, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        order = form.save_order(customer=self.user)
        self.assertEqual(order.intake_detail.request_mode, "reorder_model")
        self.assertEqual(order.intake_detail.reusable_model, saved)
        with self.assertRaises(ValueError):
            _ = saved.model_file.url
