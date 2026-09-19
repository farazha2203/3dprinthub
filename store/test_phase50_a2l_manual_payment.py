from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from store.phase50_commerce_policy import StorePaymentSettings


class Phase50A2LManualPaymentTests(TestCase):
    def test_seed_command_is_dry_run_by_default(self):
        out = StringIO()
        call_command("phase50_a2l_seed_manual_payment", stdout=out)
        self.assertIn("A2L_MANUAL_PAYMENT_DRY_RUN=PASS", out.getvalue())
        self.assertEqual(StorePaymentSettings.objects.count(), 0)

    def test_seed_command_applies_approved_card_details(self):
        out = StringIO()
        call_command("phase50_a2l_seed_manual_payment", "--apply", stdout=out)
        self.assertIn("A2L_MANUAL_PAYMENT_APPLY=PASS", out.getvalue())
        row = StorePaymentSettings.objects.get()
        self.assertTrue(row.is_active)
        self.assertEqual(row.bank_name, "بانک پاسارگاد")
        self.assertEqual(row.account_holder, "فراز حراجی")
        self.assertEqual(row.card_number, "5022-2910-9403-4343")
        self.assertIn("در انتظار بررسی", row.transfer_instructions)

    def test_receipt_notification_targets_admin_review(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from store.operator_notifications import notify_payment_receipt

        order = SimpleNamespace(
            order_number="ORD-TEST-42",
            full_name="Buyer",
            phone="09120000000",
        )
        payment = SimpleNamespace(pk=42, amount=123456, order=order)
        with patch(
            "store.operator_notifications.send_operator_message",
            return_value=(True, ""),
        ) as sender:
            sent, error = notify_payment_receipt(payment)
        self.assertTrue(sent)
        self.assertEqual(error, "")
        kwargs = sender.call_args.kwargs
        self.assertIn("ORD-TEST-42", kwargs["text"])
        self.assertIn("/admin/store/storepayment/42/change/", kwargs["text"])

    def test_manual_payment_view_invokes_receipt_notification(self):
        from pathlib import Path
        source = Path(__file__).with_name("views.py").read_text(encoding="utf-8")
        self.assertIn("notify_payment_receipt(payment)", source)
        self.assertIn('payment.status = "awaiting_review"', source)
