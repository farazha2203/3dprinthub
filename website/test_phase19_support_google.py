from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import CustomerProfile, Order, SupportConversation, SupportMessage


User = get_user_model()


class SupportChatPhase19Tests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="09123334444",
            password="StrongPass123!",
            first_name="مشتری",
            last_name="تست",
        )
        CustomerProfile.objects.create(
            user=self.customer,
            phone="09123334444",
            first_name="مشتری",
            last_name="تست",
        )
        self.other_customer = User.objects.create_user(
            username="09125556666",
            password="StrongPass123!",
        )
        CustomerProfile.objects.create(user=self.other_customer, phone="09125556666")
        self.staff = User.objects.create_user(
            username="support-agent",
            password="StrongPass123!",
            is_staff=True,
        )
        self.order = Order.objects.create(
            customer=self.customer,
            first_name="مشتری",
            last_name="تست",
            phone="09123334444",
            service_type="3d_print",
            quantity=1,
            description="سفارش آزمایشی",
        )
        self.conversation = SupportConversation.objects.create(
            customer=self.customer,
            order=self.order,
            subject="گفت‌وگوی سفارش",
        )

    def test_customer_can_read_own_chat(self):
        self.client.force_login(self.customer)
        response = self.client.get(
            reverse("website:support_messages_api", args=[self.conversation.public_token])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["conversation"], str(self.conversation.public_token))

    def test_other_customer_cannot_read_chat(self):
        self.client.force_login(self.other_customer)
        response = self.client.get(
            reverse("website:support_messages_api", args=[self.conversation.public_token])
        )
        self.assertEqual(response.status_code, 404)

    def test_customer_message_marks_conversation_waiting_for_staff(self):
        self.client.force_login(self.customer)
        response = self.client.post(
            reverse("website:support_send_api", args=[self.conversation.public_token]),
            {"body": "سلام، درباره قطعه سؤال دارم."},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.status, "waiting_staff")
        self.assertEqual(self.conversation.messages.count(), 1)

    def test_staff_reply_is_counted_as_unread_for_customer(self):
        SupportMessage.objects.create(
            conversation=self.conversation,
            sender=self.staff,
            body="پاسخ پشتیبانی",
        )
        self.assertEqual(self.conversation.unread_for_customer, 1)
        self.client.force_login(self.customer)
        self.client.get(reverse("website:customer_support"), {"conversation": self.conversation.public_token})
        self.assertEqual(self.conversation.unread_for_customer, 0)


class GoogleProfilePhase19Tests(TestCase):
    def test_social_user_profile_can_exist_without_phone(self):
        user = User.objects.create_user(
            username="google-user@example.com",
            email="google-user@example.com",
        )
        profile = CustomerProfile.objects.create(
            user=user,
            phone=None,
            first_name="کاربر",
            last_name="گوگل",
        )
        self.assertIsNone(profile.phone)

    @override_settings(GOOGLE_OAUTH_ENABLED=False)
    def test_google_button_is_hidden_without_credentials(self):
        response = self.client.get(reverse("website:customer_login"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "ادامه با حساب گوگل")

    @override_settings(
        GOOGLE_OAUTH_ENABLED=True,
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [{"client_id": "test-client", "secret": "test-secret", "key": ""}],
                "SCOPE": ["profile", "email"],
            }
        },
    )
    def test_google_button_is_visible_when_configured(self):
        response = self.client.get(reverse("website:customer_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ادامه با حساب گوگل")
