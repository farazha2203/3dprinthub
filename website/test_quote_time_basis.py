"""Regression for pricing a production batch vs each individual printed unit."""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Material, Order, Quote


class QuoteTimeBasisTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="time-basis-customer", password="local-unit-test-only"
        )
        self.material = Material.objects.create(
            name="time-basis PLA", sale_price_per_gram=1500,
            price_per_kg=1500000, main_usage="unit test", sample_parts="unit test",
        )
        self.order = Order.objects.create(
            customer=self.customer,
            first_name="Sample", last_name="Buyer", phone="09120000044",
            material=self.material, quantity=4, description="batch vs per piece",
        )
        self.quote = Quote.objects.create(
            order=self.order, material=self.material, status="draft",
            weight_grams=20, print_time_minutes=200, machine_hourly_rate=40000,
            labor_fee=45000,
        )

    def test_legacy_default_remains_per_piece_and_keeps_existing_draft_amount(self):
        self.assertEqual(self.quote.print_time_scope, "per_piece")
        self.assertEqual(self.quote.billable_print_minutes, 240)
        self.assertEqual(self.quote.total_billable_machine_minutes, 960)
        self.assertEqual(self.quote.machine_cost, 640000)
        self.assertEqual(self.quote.material_cost, 120000)
        self.assertEqual(self.quote.subtotal, 805000)
        self.assertEqual(self.quote.total_price, 805000)

    def test_batch_mode_bills_machine_only_once_and_material_for_every_piece(self):
        self.quote.print_time_scope = "batch"
        self.quote.save(update_fields=["print_time_scope"])
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.billable_print_minutes, 240)
        self.assertEqual(self.quote.total_billable_machine_minutes, 240)
        self.assertEqual(self.quote.machine_cost, 160000)
        self.assertEqual(self.quote.material_cost, 120000)
        self.assertEqual(self.quote.total_price, 325000)

    def test_finalized_batch_price_is_frozen_against_later_catalog_changes(self):
        self.quote.print_time_scope = "batch"
        self.quote.status = "sent"
        self.quote.save()
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.pricing_snapshot_total, 325000)
        self.assertEqual(self.quote.pricing_snapshot_machine_cost, 160000)
        self.material.sale_price_per_gram = 2700
        self.material.save(update_fields=["sale_price_per_gram"])
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.machine_cost, 160000)
        self.assertEqual(self.quote.material_cost, 120000)
        self.assertEqual(self.quote.total_price, 325000)

    def test_finalized_quote_cannot_switch_time_scope_silently(self):
        self.quote.status = "sent"
        self.quote.save(update_fields=["status"])
        self.quote.print_time_scope = "batch"
        with self.assertRaises(ValidationError):
            self.quote.save()
        self.quote.refresh_from_db()
        self.assertEqual(self.quote.print_time_scope, "per_piece")

    def test_explicit_scope_validation(self):
        self.quote.print_time_scope = "unknown"
        with self.assertRaises(ValidationError):
            self.quote.save()

    def test_rounding_and_quantity_one_do_not_double_charge(self):
        self.quote.print_time_minutes = 70
        self.quote.minimum_billable_minutes = 30
        self.quote.billing_increment_minutes = 30
        self.quote.print_time_scope = "per_piece"
        self.assertEqual(self.quote.billable_print_minutes, 90)
        self.assertEqual(self.quote.total_billable_machine_minutes, 360)
        self.order.quantity = 1
        self.quote.print_time_scope = "batch"
        self.assertEqual(self.quote.total_billable_machine_minutes, 90)
        self.quote.print_time_scope = "per_piece"
        self.assertEqual(self.quote.total_billable_machine_minutes, 90)

    def test_draft_customer_cannot_see_unagreed_dynamic_price(self):
        self.client.force_login(self.customer)
        self.assertGreater(self.quote.total_price, 0)
        response = self.client.get(reverse("website:quote_detail", args=[self.order.public_token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "در حال قیمت‌گذاری کارشناسی")
        self.assertNotContains(response, "مبلغ نهایی")

    def test_sent_quote_explains_time_scope_to_customer(self):
        self.quote.print_time_scope = "batch"
        self.quote.status = "sent"
        self.quote.save()
        self.client.force_login(self.customer)
        response = self.client.get(reverse("website:quote_detail", args=[self.order.public_token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "برای کل تیراژ")
        self.assertContains(response, "زمان قابل محاسبه دستگاه")
        self.assertEqual(self.quote.total_price, 325000)
        self.assertContains(response, "مبلغ نهایی")

    def test_order_admin_shows_time_basis_selector_for_draft(self):
        staff = User.objects.create_superuser("time-admin", "time-admin@example.invalid", "test-password-only")
        self.client.force_login(staff)
        response = self.client.get(reverse("admin:website_order_change", args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="quote-0-print_time_scope"')
        self.assertContains(response, "مبنای زمان چاپ")

    def test_order_admin_freezes_time_basis_selector_for_finalized_quote(self):
        self.quote.status = "sent"
        self.quote.save(update_fields=["status"])
        staff = User.objects.create_superuser("time-admin-frozen", "time-admin-frozen@example.invalid", "test-password-only")
        self.client.force_login(staff)
        response = self.client.get(reverse("admin:website_order_change", args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "برای هر قطعه")
        self.assertNotContains(response, 'name="quote-0-print_time_scope"')
