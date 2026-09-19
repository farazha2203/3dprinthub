from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from store.phase50_commerce_policy import StorePaymentSettings


class Phase50A2LManualPaymentTests(TestCase):
    def test_seed_command_is_dry_run_by_default(self):
        out = StringIO()
        call_command("phase50_a2l_seed_manual_payment", stdout=out)
        self.assertIn("A2L_MANUAL_PAYMENT_DRY_RUN=PASS", out.getvalue())\n        self.assertIn("A2R_MANUAL_PAYMENT_DRY_RUN=PASS", out.getvalue())\n        self.assertEqual(StorePaymentSettings.objects.count(), 0)

    def test_seed_command_requires_secure_config_before_activation(self):
        out = StringIO()
        with self.assertRaises(CommandError):
            call_command(
                "phase50_a2l_seed_manual_payment",
                "--apply",
                "--activate",
                stdout=out,
            )
        self.assertEqual(StorePaymentSettings.objects.count(), 0)

    def test_seed_command_applies_secure_env_without_echoing_financial_values(self):
        out = StringIO()
        env = {
            "STORE_PAYMENT_TITLE": "پرداخت دستی تست",
            "STORE_PAYMENT_BANK_NAME": "Test Bank",
            "STORE_PAYMENT_ACCOUNT_HOLDER": "Test Operator",
            "STORE_PAYMENT_CARD_NUMBER": "0000-0000-0000-0000",
            "STORE_PAYMENT_SHEBA_NUMBER": "IR000000000000000000000000",
            "STORE_PAYMENT_ACCOUNT_NUMBER": "TEST-001",
            "STORE_PAYMENT_TRANSFER_INSTRUCTIONS": "رسید را برای بررسی ثبت کنید.",
        }
        with patch.dict("os.environ", env, clear=False):
            call_command(
                "phase50_a2l_seed_manual_payment",
                "--apply",
                "--activate",
                stdout=out,
            )

        row = StorePaymentSettings.objects.get()
        self.assertTrue(row.is_active)
        self.assertEqual(row.bank_name, "Test Bank")
        self.assertEqual(row.account_holder, "Test Operator")
        self.assertEqual(row.card_number, "0000000000000000")
        self.assertEqual(row.sheba_number, "IR000000000000000000000000")
        self.assertEqual(row.account_number, "TEST-001")
        output = out.getvalue()
        self.assertIn("A2R_MANUAL_PAYMENT_APPLY=PASS", output)
        self.assertNotIn(row.card_number, output)
        self.assertNotIn(row.sheba_number, output)
        self.assertNotIn(row.account_number, output)

    def test_manual_payment_settings_are_visible_in_finance_navigation(self):
        from website.templatetags.admin_console import GROUP_DEFINITIONS

        finance = next(group for group in GROUP_DEFINITIONS if group[0] == "finance")
        keys = [item[0] for item in finance[3]]
        self.assertIn("store.storepaymentsettings", keys)

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
