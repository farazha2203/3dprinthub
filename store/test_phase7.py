from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .affiliate_services import (
    approve_due_commissions,
    create_commission_for_order,
    mark_payout_paid,
    request_partner_payout,
    reverse_commission,
)
from .models import (
    AffiliateAttribution,
    AffiliateCampaign,
    AffiliateClick,
    AffiliateCommission,
    AffiliateLedgerEntry,
    AffiliatePartner,
    AffiliatePayout,
    AffiliateTier,
    StoreOrder,
)
from .services import transition_order

User = get_user_model()


class AffiliatePhase7Tests(TestCase):
    def setUp(self):
        self.tier, _ = AffiliateTier.objects.get_or_create(
            slug="test-tier",
            defaults={
                "name": "سطح تست",
                "commission_type": "percent",
                "commission_value": Decimal("5"),
                "attribution_days": 30,
                "hold_days": 0,
                "minimum_payout": 1,
                "is_active": True,
            },
        )
        self.partner_user = User.objects.create_user(username="09120000001", password="pass12345", first_name="همکار", last_name="اول")
        self.partner = AffiliatePartner.objects.create(
            user=self.partner_user,
            tier=self.tier,
            code="PARTNER1",
            partner_type="publisher",
            status="active",
            display_name="رسانه اول",
            terms_accepted=True,
            card_number="6037991234567890",
            account_holder="همکار اول",
            approved_at=timezone.now(),
        )
        self.campaign = AffiliateCampaign.objects.create(partner=self.partner, name="کمپین اصلی", slug="main", target_path="/store/")

    def create_customer(self, phone="09120000002"):
        return User.objects.create_user(username=phone, password="pass12345", first_name="علی", last_name="احمدی")

    def create_order(self, user, **overrides):
        data = {
            "user": user,
            "status": "paid",
            "payment_status": "paid",
            "shipping_title": "پست",
            "full_name": user.get_full_name() or "مشتری",
            "phone": user.username,
            "province": "اصفهان",
            "county": "اصفهان",
            "city": "اصفهان",
            "address": "آدرس تست",
            "postal_code": "8134567890",
            "subtotal": 1_000_000,
            "discount_amount": 100_000,
            "total_amount": 900_000,
            "paid_at": timezone.now(),
        }
        data.update(overrides)
        return StoreOrder.objects.create(**data)

    def test_referral_link_records_click_and_cookie(self):
        response = self.client.get(reverse("store:affiliate_referral_campaign", kwargs={"code": self.partner.code, "campaign_slug": self.campaign.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertIn("dph_ref", response.cookies)
        self.assertEqual(AffiliateClick.objects.filter(partner=self.partner, campaign=self.campaign).count(), 1)

    def test_logged_in_customer_is_attached_to_pending_referral(self):
        self.client.get(reverse("store:affiliate_referral", kwargs={"code": self.partner.code}))
        customer = self.create_customer()
        self.client.login(username=customer.username, password="pass12345")
        self.client.get(reverse("website:customer_dashboard"))
        attribution = AffiliateAttribution.objects.get(customer=customer)
        self.assertEqual(attribution.partner, self.partner)

    def test_existing_customer_attribution_is_not_overwritten(self):
        other_user = User.objects.create_user(username="09120000003", password="pass12345")
        other = AffiliatePartner.objects.create(user=other_user, tier=self.tier, code="OTHER1", status="active", display_name="دیگری", terms_accepted=True)
        customer = self.create_customer("09120000004")
        AffiliateAttribution.objects.create(customer=customer, partner=other)
        self.client.login(username=customer.username, password="pass12345")
        self.client.get(reverse("store:product_list") + f"?ref={self.partner.code}")
        self.assertEqual(customer.affiliate_attribution.partner, other)

    def test_order_inherits_partner_and_snapshot_commission(self):
        customer = self.create_customer()
        AffiliateAttribution.objects.create(customer=customer, partner=self.partner, campaign=self.campaign)
        order = self.create_order(customer)
        order.refresh_from_db()
        self.assertEqual(order.affiliate_partner, self.partner)
        commission = create_commission_for_order(order)
        self.assertEqual(commission.basis_amount, 900_000)
        self.assertEqual(commission.amount, 45_000)
        self.partner.commission_value_override = Decimal("20")
        self.partner.save(update_fields=["commission_value_override"])
        commission.refresh_from_db()
        self.assertEqual(commission.amount, 45_000)

    def test_delivered_commission_is_approved_and_credited(self):
        customer = self.create_customer()
        AffiliateAttribution.objects.create(customer=customer, partner=self.partner)
        order = self.create_order(customer)
        create_commission_for_order(order)
        transition_order(order, "delivered")
        approved = approve_due_commissions()
        self.assertEqual(approved, 1)
        commission = AffiliateCommission.objects.get(order=order)
        self.assertEqual(commission.status, "approved")
        self.assertEqual(AffiliateLedgerEntry.objects.get(commission=commission, entry_type="commission").amount, commission.amount)

    def test_payout_request_and_payment(self):
        customer = self.create_customer()
        AffiliateAttribution.objects.create(customer=customer, partner=self.partner)
        order = self.create_order(customer)
        create_commission_for_order(order)
        transition_order(order, "delivered")
        approve_due_commissions()
        payout = request_partner_payout(self.partner)
        self.assertEqual(payout.status, "requested")
        self.assertEqual(AffiliateCommission.objects.get(order=order).status, "requested")
        mark_payout_paid(payout, reference_number="REF-1")
        payout.refresh_from_db()
        self.assertEqual(payout.status, "paid")
        self.assertEqual(AffiliateCommission.objects.get(order=order).status, "paid")
        self.assertEqual(self.partner.ledger_balance, 0)

    def test_refund_reverses_paid_commission_and_creates_debt(self):
        customer = self.create_customer()
        AffiliateAttribution.objects.create(customer=customer, partner=self.partner)
        order = self.create_order(customer)
        create_commission_for_order(order)
        transition_order(order, "delivered")
        approve_due_commissions()
        payout = request_partner_payout(self.partner)
        mark_payout_paid(payout)
        self.assertTrue(reverse_commission(order, "مرجوعی"))
        self.assertEqual(AffiliateCommission.objects.get(order=order).status, "reversed")
        self.assertLess(self.partner.ledger_balance, 0)

    def test_self_order_requires_explicit_permission(self):
        order = self.create_order(self.partner_user)
        order.refresh_from_db()
        self.assertIsNone(order.affiliate_partner)
        self.partner.include_self_orders_override = True
        self.partner.save(update_fields=["include_self_orders_override"])
        allowed = self.create_order(self.partner_user, phone="09120000001")
        allowed.refresh_from_db()
        self.assertEqual(allowed.affiliate_partner, self.partner)

    def test_partner_dashboard_requires_active_partner(self):
        customer = self.create_customer()
        self.client.login(username=customer.username, password="pass12345")
        response = self.client.get(reverse("store:partner_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("store:partner_apply"), response.url)

    def test_partner_dashboard_shows_only_own_data(self):
        other_user = User.objects.create_user(username="09120000009", password="pass12345")
        other = AffiliatePartner.objects.create(user=other_user, tier=self.tier, code="SECRET99", status="active", display_name="محرمانه", terms_accepted=True)
        AffiliateClick.objects.create(partner=other, visitor_hash="x")
        self.client.login(username=self.partner_user.username, password="pass12345")
        response = self.client.get(reverse("store:partner_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.partner.code)
        self.assertNotContains(response, other.code)

    def test_application_creates_pending_partner(self):
        user = self.create_customer("09120000010")
        self.client.login(username=user.username, password="pass12345")
        response = self.client.post(reverse("store:partner_apply"), {
            "partner_type": "referrer",
            "display_name": "معرف جدید",
            "company_name": "",
            "website": "",
            "channel": "مشتریان حضوری",
            "description": "معرفی مشتری",
            "code": "NEWREF10",
            "sheba_number": "IR120170000000123456789012",
            "card_number": "",
            "account_holder": "معرف جدید",
            "terms_accepted": "on",
        })
        self.assertEqual(response.status_code, 302)
        partner = AffiliatePartner.objects.get(user=user)
        self.assertEqual(partner.status, "pending")
        self.assertEqual(partner.code, "NEWREF10")

class AffiliateAdminDashboardRegressionTests(TestCase):
    """Regression test for the custom affiliate admin dashboard."""

    def test_staff_can_open_affiliate_dashboard(self):
        admin_user = User.objects.create_superuser(
            username="affiliate-admin",
            email="admin@example.com",
            password="StrongAdminPass123!",
        )
        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("admin:store_affiliateprogramdashboard_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "داشبورد همکاری در فروش")
        self.assertContains(response, "مدیریت همکاران")

