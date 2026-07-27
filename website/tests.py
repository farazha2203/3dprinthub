from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import CustomerProfile, Material, Order, Quote, OrderReview


class WebsiteTestHelpers:
    # BEGIN PHASE 12 ORDER SUBMISSION TEST COMPATIBILITY
    def create_test_image(self, name):
        """Create a valid in-memory JPEG for order form tests."""
        buffer = BytesIO()
        Image.new("RGB", (32, 32), "white").save(buffer, format="JPEG")
        return SimpleUploadedFile(
            name,
            buffer.getvalue(),
            content_type="image/jpeg",
        )
    # END PHASE 12 ORDER SUBMISSION TEST COMPATIBILITY

    def create_user(self, phone="09120000000", password="StrongPass123!", first_name="علی", last_name="احمدی"):
        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
        )

        return user

    def create_material(self, name="PLA"):
        return Material.objects.create(
            name=name,
            price_per_kg=900000,
            strength=3,
            heat_resistance=2,
            flexibility=2,
            chemical_resistance=2,
            printability=5,
            main_usage="نمونه‌سازی، قطعات عمومی، ماکت",
            sample_parts="کاور، قاب، قطعات دکوراتیو",
            is_active=True,
        )

    def create_order(
        self,
        customer=None,
        material=None,
        phone="09120000000",
        first_name="علی",
        last_name="احمدی",
        service_type="3d_print",
        color="مشکی",
        quantity=1,
        description="تست ثبت سفارش قطعه",
    ):
        if material is None:
            material = self.create_material()

        return Order.objects.create(
            customer=customer,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            service_type=service_type,
            material=material,
            color=color,
            quantity=quantity,
            description=description,
        )


class HomePageTests(TestCase, WebsiteTestHelpers):
    def test_home_page_loads_successfully(self):
        response = self.client.get(reverse("website:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/index.html")

    def test_header_shows_customer_login_link_for_anonymous_user(self):
        response = self.client.get(reverse("website:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/customer/login/")

    def test_header_shows_customer_dashboard_link_for_authenticated_user(self):
        user = self.create_user(phone="09121111111")
        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(reverse("website:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/customer/dashboard/")


class CustomerRegisterTests(TestCase, WebsiteTestHelpers):
    def test_register_page_loads_successfully(self):
        response = self.client.get(reverse("website:customer_register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/customer/register.html")

    def test_customer_can_register_and_profile_is_created(self):
        data = {
            "first_name": "مهدی",
            "last_name": "کریمی",
            "phone": "09123334455",
            "email": "mehdi@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = self.client.post(reverse("website:customer_register"), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="09123334455").exists())
        self.assertTrue(CustomerProfile.objects.filter(phone="09123334455").exists())

        user = User.objects.get(username="09123334455")
        self.assertEqual(user.first_name, "مهدی")
        self.assertEqual(user.last_name, "کریمی")

    def test_register_logs_user_in_after_success(self):
        data = {
            "first_name": "سارا",
            "last_name": "محمدی",
            "phone": "09124445566",
            "email": "sara@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        self.client.post(reverse("website:customer_register"), data)

        self.assertIn("_auth_user_id", self.client.session)

    def test_register_with_duplicate_phone_fails(self):
        self.create_user(phone="09125556677")

        data = {
            "first_name": "رضا",
            "last_name": "اکبری",
            "phone": "09125556677",
            "email": "reza@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        response = self.client.post(reverse("website:customer_register"), data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قبلاً حساب کاربری ساخته شده است")

    def test_old_orders_with_same_phone_attach_to_new_customer_after_register(self):
        material = self.create_material()
        old_order = self.create_order(
            customer=None,
            material=material,
            phone="09126667788",
            first_name="حسین",
            last_name="مرادی",
        )

        data = {
            "first_name": "حسین",
            "last_name": "مرادی",
            "phone": "09126667788",
            "email": "hossein@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }

        self.client.post(reverse("website:customer_register"), data)

        old_order.refresh_from_db()

        self.assertIsNotNone(old_order.customer)
        self.assertEqual(old_order.customer.username, "09126667788")


class CustomerLoginLogoutTests(TestCase, WebsiteTestHelpers):
    def test_login_page_loads_successfully(self):
        response = self.client.get(reverse("website:customer_login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/customer/login.html")

    def test_customer_can_login(self):
        user = self.create_user(phone="09127778899", password="StrongPass123!")

        data = {
            "username": "09127778899",
            "password": "StrongPass123!",
        }

        response = self.client.post(reverse("website:customer_login"), data)

        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password_fails(self):
        self.create_user(phone="09128889900", password="StrongPass123!")

        data = {
            "username": "09128889900",
            "password": "WrongPassword",
        }

        response = self.client.post(reverse("website:customer_login"), data)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_customer_can_logout(self):
        user = self.create_user(phone="09129990011", password="StrongPass123!")
        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(reverse("website:customer_logout"))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


class CustomerDashboardTests(TestCase, WebsiteTestHelpers):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("website:customer_dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/customer/login/", response["Location"])

    def test_dashboard_loads_for_authenticated_customer(self):
        user = self.create_user(phone="09130000001")
        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(reverse("website:customer_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/customer/dashboard.html")
        self.assertContains(response, "داشبورد مشتری")

    def test_dashboard_shows_customer_orders(self):
        user = self.create_user(phone="09130000002")
        material = self.create_material()
        order = self.create_order(customer=user, material=material, phone=user.username)

        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(reverse("website:customer_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{order.id}")
        self.assertContains(response, material.name)

    def test_dashboard_does_not_show_other_users_orders(self):
        user_1 = self.create_user(phone="09130000003")
        user_2 = self.create_user(phone="09130000004")
        material = self.create_material()

        order_1 = self.create_order(customer=user_1, material=material, phone=user_1.username)
        order_2 = self.create_order(customer=user_2, material=material, phone=user_2.username)

        self.client.login(username=user_1.username, password="StrongPass123!")

        response = self.client.get(reverse("website:customer_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{order_1.id}")
        self.assertNotContains(response, f"#{order_2.id}")


class CustomerProfileTests(TestCase, WebsiteTestHelpers):
    def test_profile_page_requires_login(self):
        response = self.client.get(reverse("website:customer_profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/customer/login/", response["Location"])

    def test_profile_page_loads_for_authenticated_user(self):
        user = self.create_user(phone="09130000005")
        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(reverse("website:customer_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/customer/profile.html")
        self.assertContains(response, "مشخصات مشتری و حساب")

    def test_customer_can_update_profile(self):
        user = self.create_user(phone="09130000006")
        self.client.login(username=user.username, password="StrongPass123!")

        data = {
            "first_name": "نیما",
            "last_name": "رضایی",
            "phone": "09130000066",
            "company_name": "شرکت تست",
            "national_code": "",
        }

        response = self.client.post(reverse("website:customer_profile"), data)

        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        profile = user.customer_profile

        self.assertEqual(user.username, "09130000066")
        self.assertEqual(user.first_name, "نیما")
        self.assertEqual(user.last_name, "رضایی")
        self.assertEqual(profile.company_name, "شرکت تست")
        self.assertEqual(profile.phone, "09130000066")


class CustomerOrderDetailTests(TestCase, WebsiteTestHelpers):
    def test_order_detail_requires_login(self):
        user = self.create_user(phone="09130000007")
        material = self.create_material()
        order = self.create_order(customer=user, material=material, phone=user.username)

        response = self.client.get(
            reverse("website:customer_order_detail", kwargs={"order_id": order.id})
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/customer/login/", response["Location"])

    def test_customer_can_view_own_order_detail(self):
        user = self.create_user(phone="09130000008")
        material = self.create_material()
        order = self.create_order(customer=user, material=material, phone=user.username)

        self.client.login(username=user.username, password="StrongPass123!")

        response = self.client.get(
            reverse("website:customer_order_detail", kwargs={"order_id": order.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "website/customer/order_detail.html")
        self.assertContains(response, f"جزئیات سفارش #{order.id}")
        self.assertContains(response, material.name)

    def test_customer_cannot_view_other_customer_order_detail(self):
        user_1 = self.create_user(phone="09130000009")
        user_2 = self.create_user(phone="09130000010")

        material = self.create_material()
        order_for_user_2 = self.create_order(
            customer=user_2,
            material=material,
            phone=user_2.username,
        )

        self.client.login(username=user_1.username, password="StrongPass123!")

        response = self.client.get(
            reverse("website:customer_order_detail", kwargs={"order_id": order_for_user_2.id})
        )

        self.assertEqual(response.status_code, 404)


class OrderSubmissionTests(TestCase, WebsiteTestHelpers):
    def test_authenticated_order_is_attached_to_customer(self):
        user = self.create_user(phone="09130000011")
        material = self.create_material()

        self.client.login(username=user.username, password="StrongPass123!")

        data = {
            "first_name": "علی",
            "last_name": "احمدی",
            "phone": user.username,
            "service_type": "3d_print",
            "material": material.id,
            "color": "مشکی",
            "quantity": 2,
            "description": "ثبت سفارش تستی در حالت لاگین",
            "request_mode": "new_part",
            "usage_environment": "indoor",
            "exact_dimensions": "100x50x20 mm",
            "photo_top": self.create_test_image("authenticated-top.jpg"),
            "photo_front": self.create_test_image("authenticated-front.jpg"),
            "photo_right": self.create_test_image("authenticated-right.jpg"),
            "photo_left": self.create_test_image("authenticated-left.jpg"),
        }

        response = self.client.post(reverse("website:home"), data)

        self.assertIn(response.status_code, [200, 302])

        order = Order.objects.filter(phone=user.username).latest("id")

        self.assertEqual(order.customer, user)
        self.assertEqual(order.material, material)
        self.assertEqual(order.quantity, 2)

    def test_anonymous_order_is_not_attached_to_customer(self):
        material = self.create_material()

        data = {
            "first_name": "کاربر",
            "last_name": "مهمان",
            "phone": "09130000012",
            "service_type": "3d_print",
            "material": material.id,
            "color": "نارنجی",
            "quantity": 1,
            "description": "ثبت سفارش تستی بدون لاگین",
        }

        response = self.client.post(reverse("website:home"), data)

        # در فاز ۱۴ ثبت سفارش فقط برای کاربر واردشده مجاز است.
        self.assertIn(response.status_code, (200, 302))
        self.assertFalse(
            Order.objects.filter(phone="09130000012").exists()
        )

        login_url = reverse("website:customer_login")

        if response.status_code == 302:
            self.assertTrue(
                response["Location"].startswith(login_url),
                response["Location"],
            )
        else:
            self.assertContains(response, login_url)

class QuoteToleranceTests(TestCase, WebsiteTestHelpers):
    def test_quote_tolerance_price_range_is_calculated(self):
        user = self.create_user(phone="09131111111")

        material = self.create_material()
        material.price_per_kg = 1000000
        material.save(update_fields=["price_per_kg"])

        order = self.create_order(
            customer=user,
            material=material,
            phone=user.username,
            quantity=1,
        )

        quote = Quote.objects.create(
            order=order,
            weight_grams=100,
            print_time_minutes=120,
            machine_hourly_rate=100000,
            labor_fee=300000,
            design_fee=0,
            post_processing_fee=0,
            shipping_fee=0,
            discount=0,
            price_tolerance_percent=10,
        )

        self.assertEqual(int(quote.material_cost), 100000)
        self.assertEqual(int(quote.machine_cost), 200000)
        self.assertEqual(int(quote.total_price), 600000)

        self.assertEqual(int(quote.tolerance_amount), 60000)
        self.assertEqual(int(quote.min_estimated_price), 540000)
        self.assertEqual(int(quote.max_estimated_price), 660000)


class OrderReviewTests(TestCase, WebsiteTestHelpers):
    def test_customer_can_submit_review_for_done_order(self):
        user = self.create_user(phone="09132222222")
        material = self.create_material()
        order = self.create_order(customer=user, material=material, phone=user.username)
        order.status = "done"
        order.save(update_fields=["status"])

        self.client.login(username=user.username, password="StrongPass123!")

        data = {
            "rating": 5,
            "comment": "کیفیت ساخت عالی بود و قطعه دقیقاً مطابق انتظار تحویل شد.",
        }

        response = self.client.post(
            reverse("website:customer_order_review_create", kwargs={"order_id": order.id}),
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(OrderReview.objects.filter(order=order, customer=user).exists())

        review = OrderReview.objects.get(order=order)
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)

    def test_customer_cannot_submit_review_for_not_done_order(self):
        user = self.create_user(phone="09133333333")
        material = self.create_material()
        order = self.create_order(customer=user, material=material, phone=user.username)
        order.status = "paid"
        order.save(update_fields=["status"])

        self.client.login(username=user.username, password="StrongPass123!")

        data = {
            "rating": 5,
            "comment": "نظر تستی",
        }

        response = self.client.post(
            reverse("website:customer_order_review_create", kwargs={"order_id": order.id}),
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(OrderReview.objects.filter(order=order).exists())

    def test_customer_cannot_review_other_customer_order(self):
        user_1 = self.create_user(phone="09134444444")
        user_2 = self.create_user(phone="09135555555")

        material = self.create_material()
        order = self.create_order(customer=user_2, material=material, phone=user_2.username)
        order.status = "done"
        order.save(update_fields=["status"])

        self.client.login(username=user_1.username, password="StrongPass123!")

        data = {
            "rating": 5,
            "comment": "نظر غیرمجاز",
        }

        response = self.client.post(
            reverse("website:customer_order_review_create", kwargs={"order_id": order.id}),
            data,
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(OrderReview.objects.filter(order=order).exists())

    def test_approved_order_review_is_shown_on_home_page(self):
        user = self.create_user(phone="09136666666")
        material = self.create_material()
        order = self.create_order(customer=user, material=material, phone=user.username)

        OrderReview.objects.create(
            order=order,
            customer=user,
            rating=5,
            comment="از کیفیت چاپ و زمان تحویل کاملاً راضی بودم.",
            is_approved=True,
            display_on_site=True,
        )

        response = self.client.get(reverse("website:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "از کیفیت چاپ و زمان تحویل کاملاً راضی بودم.")