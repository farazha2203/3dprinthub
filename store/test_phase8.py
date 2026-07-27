from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from website.models import Material

from .catalog_importer import convert_asset_to_product, parse_print_page
from .models import (
    Category,
    CostEntry,
    FilamentMovement,
    FilamentPurchase,
    FilamentPurchaseItem,
    FilamentSpool,
    ImportedPrintAsset,
    MaterialUsage,
    PrintCatalogSource,
    PrintQuality,
    Product,
    ProductVariant,
    ProductionJob,
    StoreOrder,
    StoreOrderItem,
)
from .production_services import (
    consume_material_fifo,
    create_job_for_store_order,
    finalize_production_job,
    receive_filament_purchase,
)

User = get_user_model()


class Phase8InventoryFinanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="09121110000", password="pass12345")
        self.admin = User.objects.create_superuser(username="phase8-admin", email="admin@example.com", password="AdminPass123!")
        self.material = Material.objects.create(
            name="PLA Plus",
            price_per_kg=2_500_000,
            default_roll_weight_grams=1000,
            default_purchase_price_per_roll=2_500_000,
            sale_price_per_gram=5_000,
            reorder_threshold_grams=250,
            track_filament_inventory=True,
            main_usage="نمونه‌سازی",
            sample_parts="قطعات عمومی",
        )
        self.category = Category.objects.create(name="قطعات تست", slug="test-parts", section="general")
        self.quality = PrintQuality.objects.create(code="standard-test", name="استاندارد")
        image = SimpleUploadedFile("product.jpg", b"fake-image-content", content_type="image/jpeg")
        self.product = Product.objects.create(
            category=self.category,
            title="قطعه تست",
            slug="test-product",
            sku="TEST-001",
            short_description="قطعه آماده چاپ برای تست",
            description="توضیحات قطعه تست",
            main_image=image,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            material=self.material,
            quality=self.quality,
            code="TEST-VAR-001",
            material_weight_grams=Decimal("100"),
            final_weight_grams=Decimal("95"),
            shipping_weight_grams=Decimal("120"),
            print_time_minutes=60,
        )

    def create_order(self, quantity=1):
        order = StoreOrder.objects.create(
            user=self.user,
            status="paid",
            payment_status="paid",
            shipping_title="تحویل",
            full_name="مشتری تست",
            phone=self.user.username,
            province="اصفهان",
            county="اصفهان",
            city="اصفهان",
            address="آدرس تست",
            postal_code="8134567890",
            subtotal=1_000_000,
            total_amount=1_000_000,
            paid_at=timezone.now(),
        )
        StoreOrderItem.objects.create(
            order=order,
            product=self.product,
            variant=self.variant,
            product_title=self.product.title,
            product_sku=self.product.sku,
            variant_code=self.variant.code,
            material_name=self.material.name,
            quality_name=self.quality.name,
            unit_price=1_000_000,
            quantity=quantity,
            line_total=1_000_000 * quantity,
            unit_weight_grams=100,
        )
        return order

    def test_purchase_receipt_creates_physical_spools_and_updates_material(self):
        purchase = FilamentPurchase.objects.create(supplier_name="فروشنده تست", created_by=self.admin)
        item = FilamentPurchaseItem.objects.create(
            purchase=purchase,
            material=self.material,
            brand="eSUN",
            color_name="مشکی",
            quantity_rolls=2,
            net_weight_per_roll_grams=1000,
            total_purchase_amount=5_000_000,
            sale_price_per_gram=5_000,
        )
        generated = receive_filament_purchase(purchase, actor=self.admin)
        self.assertEqual(generated, 2)
        self.assertEqual(FilamentSpool.objects.filter(material=self.material).count(), 2)
        self.material.refresh_from_db()
        self.assertEqual(self.material.default_purchase_price_per_roll, 2_500_000)
        self.assertEqual(self.material.sale_price_per_gram, 5_000)
        self.assertEqual(FilamentMovement.objects.filter(movement_type="purchase").count(), 2)
        item.refresh_from_db()
        self.assertTrue(item.generated_spools)

    def test_purchase_header_cost_is_allocated_to_roll_landed_cost(self):
        purchase = FilamentPurchase.objects.create(
            supplier_name="فروشنده هزینه‌دار",
            shipping_cost=100_000,
            created_by=self.admin,
        )
        FilamentPurchaseItem.objects.create(
            purchase=purchase,
            material=self.material,
            brand="eSUN",
            color_name="سفید",
            quantity_rolls=2,
            net_weight_per_roll_grams=1000,
            total_purchase_amount=5_000_000,
            sale_price_per_gram=5_000,
        )

        receive_filament_purchase(purchase, actor=self.admin)

        spools = FilamentSpool.objects.filter(material=self.material).order_by("id")
        self.assertEqual(spools.count(), 2)
        self.assertEqual(spools[0].purchase_price, 2_550_000)
        self.assertEqual(spools[0].cost_per_gram_snapshot, Decimal("2550.00"))
        self.assertEqual(spools[1].purchase_price, 2_550_000)

    def test_fifo_consumption_uses_oldest_roll_and_keeps_exact_cost(self):
        first = FilamentSpool.objects.create(
            material=self.material,
            brand="A",
            nominal_weight_grams=1000,
            remaining_weight_grams=100,
            purchase_price=200_000,
            cost_per_gram_snapshot=2_000,
            sale_price_per_gram_snapshot=5_000,
            status="open",
        )
        second = FilamentSpool.objects.create(
            material=self.material,
            brand="B",
            nominal_weight_grams=1000,
            remaining_weight_grams=1000,
            purchase_price=3_000_000,
            cost_per_gram_snapshot=3_000,
            sale_price_per_gram_snapshot=5_000,
            status="sealed",
        )
        job = ProductionJob.objects.create(title="پروژه FIFO", revenue_snapshot=1_000_000)
        usage = MaterialUsage.objects.create(job=job, material=self.material, actual_grams=150, sale_price_per_gram_snapshot=5_000)
        consume_material_fifo(usage, actor=self.admin)
        first.refresh_from_db(); second.refresh_from_db(); usage.refresh_from_db()
        self.assertEqual(first.remaining_weight_grams, Decimal("0"))
        self.assertEqual(second.remaining_weight_grams, Decimal("950"))
        self.assertEqual(usage.material_cost_snapshot, 350_000)
        self.assertEqual(FilamentMovement.objects.filter(usage=usage, movement_type="consume").count(), 2)

    def test_store_order_creates_planned_material_usage(self):
        order = self.create_order(quantity=3)
        job = create_job_for_store_order(order)
        usage = job.material_usages.get(material=self.material)
        self.assertEqual(usage.planned_grams, Decimal("300"))
        self.assertEqual(usage.sale_price_per_gram_snapshot, 5_000)
        self.assertEqual(usage.material_charge_snapshot, 1_500_000)

    def test_finalizing_job_consumes_only_once(self):
        FilamentSpool.objects.create(
            material=self.material,
            nominal_weight_grams=1000,
            remaining_weight_grams=1000,
            purchase_price=2_500_000,
            cost_per_gram_snapshot=2_500,
            sale_price_per_gram_snapshot=5_000,
        )
        job = create_job_for_store_order(self.create_order(quantity=2))
        finalize_production_job(job, actor=self.admin)
        finalize_production_job(job, actor=self.admin)
        spool = FilamentSpool.objects.get(material=self.material)
        self.assertEqual(spool.remaining_weight_grams, Decimal("800"))
        self.assertEqual(FilamentMovement.objects.filter(job=job, movement_type="consume").count(), 1)

    def test_insufficient_stock_blocks_finalization(self):
        FilamentSpool.objects.create(
            material=self.material,
            nominal_weight_grams=100,
            remaining_weight_grams=50,
            purchase_price=125_000,
            cost_per_gram_snapshot=2_500,
        )
        job = create_job_for_store_order(self.create_order(quantity=2))
        with self.assertRaises(ValidationError):
            finalize_production_job(job, actor=self.admin)

    def test_profit_includes_material_expenses_and_extra_charge(self):
        job = ProductionJob.objects.create(title="پروژه سود", revenue_snapshot=2_000_000)
        MaterialUsage.objects.create(
            job=job,
            material=self.material,
            actual_grams=100,
            material_cost_snapshot=250_000,
            posted_at=timezone.now(),
        )
        CostEntry.objects.create(job=job, category="courier", description="پیک", actual_cost=100_000, customer_charge=150_000, included_in_order_total=False)
        CostEntry.objects.create(job=job, category="design", description="طراحی", actual_cost=300_000, customer_charge=500_000, included_in_order_total=True)
        self.assertEqual(job.total_revenue, 2_150_000)
        self.assertEqual(job.total_cost, 650_000)
        self.assertEqual(job.net_profit, 1_500_000)

    def test_generic_parser_extracts_title_image_specs_and_private_download(self):
        html = """
        <html><head>
          <meta property="og:title" content="Gear Box Model">
          <meta property="og:description" content="Printable replacement gear">
          <meta property="og:image" content="/images/gear.jpg">
          <script type="application/ld+json">{
            "@type":"Product","name":"Gear Box Model","sku":"GB-10",
            "contentUrl":"/downloads/gear.stl",
            "additionalProperty":[{"name":"Layer height","value":"0.2 mm"}]
          }</script>
        </head></html>
        """
        parsed = parse_print_page(html, "https://models.example/item/1")
        self.assertEqual(parsed["title"], "Gear Box Model")
        self.assertEqual(parsed["download_url"], "https://models.example/downloads/gear.stl")
        self.assertEqual(parsed["file_format"], "STL")
        self.assertEqual(parsed["technical_specs"]["Layer height"], "0.2 mm")

    def test_converted_import_never_copies_private_download_url_to_product(self):
        source = PrintCatalogSource.objects.create(
            name="منبع تست",
            code="test-source",
            base_url="https://models.example",
            allowed_domains="models.example",
            default_category=self.category,
        )
        image = SimpleUploadedFile("preview.jpg", b"fake-preview", content_type="image/jpeg")
        asset = ImportedPrintAsset.objects.create(
            source=source,
            source_url="https://models.example/model/1",
            title="مدل واردشده",
            short_description="مدل تست",
            description="شرح مدل تست",
            preview_image=image,
            private_download_url="https://models.example/private/file.stl",
        )
        product = convert_asset_to_product(asset)
        self.assertFalse(product.is_active)
        self.assertNotIn(asset.private_download_url, product.description)
        self.assertNotIn(asset.private_download_url, product.technical_notes)

    def test_business_dashboard_loads_for_staff(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:store_businessfinancedashboard_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد انبار، بهای تمام‌شده و سود")

    def test_material_reports_roll_count_and_weight(self):
        FilamentSpool.objects.create(material=self.material, nominal_weight_grams=1000, remaining_weight_grams=700)
        FilamentSpool.objects.create(material=self.material, nominal_weight_grams=1000, remaining_weight_grams=300)
        self.assertEqual(self.material.current_roll_count, 2)
        self.assertEqual(self.material.current_stock_grams, Decimal("1000"))
