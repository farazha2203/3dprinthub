from __future__ import annotations

import inspect
import unittest
from pathlib import Path

from app.product_workspace_v87 import ProductWorkspace
from app.ux87_shell import NAV_ITEMS, build_app_class
from app import main as app_main


ROOT = Path(__file__).resolve().parents[1]


class V87UXRebuildTests(unittest.TestCase):
    def test_sidebar_contains_every_operational_center(self):
        keys = [item[0] for item in NAV_ITEMS]
        self.assertEqual(
            keys,
            ["dashboard", "products", "discover", "publish", "published", "blocked", "logs", "ai", "connection", "settings"],
        )

    def test_shell_is_a_real_app_subclass_and_keeps_stable_engines(self):
        App87 = build_app_class(app_main.App)
        self.assertTrue(issubclass(App87, app_main.App))
        source = inspect.getsource(App87._ui)
        for marker in [
            "super()._products_ui()",
            "super()._scan_ui()",
            "super()._upload_ui()",
            "super()._published_ui()",
            "super()._blocked_ui()",
            "super()._runs_ui()",
            "_build_ux87_ai_center",
            "_build_ux87_connection_center",
        ]:
            self.assertIn(marker, source)

    def test_ai_and_host_profile_values_are_loaded_from_existing_sources(self):
        source = (ROOT / "app" / "ux87_shell.py").read_text(encoding="utf-8")
        for marker in [
            'self.db.setting("ai_provider"',
            'self.db.setting("ai_model"',
            'self.db.setting("translation_provider"',
            'self.db.setting("google_api_key"',
            'get_secret("google_api_key")',
            'set_secret("google_api_key"',
            'env_value("CATALOG_FTP_HOST"',
            'self.db.setting("ftp_host"',
            'env_value("CATALOG_SITE_URL"',
            'self.db.setting("site_url"',
            'get_provider_key("avalai")',
            'get_provider_key("openai")',
            'get_secret("ftp_password")',
            'get_secret("bridge_token")',
        ]:
            self.assertIn(marker, source)

    def test_google_legacy_secret_is_only_erased_after_secure_write(self):
        source = inspect.getsource(build_app_class(app_main.App)._migrate_legacy_google_key)
        self.assertLess(source.index('set_secret("google_api_key"'), source.rindex('self.db.set_setting("google_api_key", "")'))
        self.assertIn("except Exception", source)
        self.assertIn("return legacy_key", source)

    def test_product_workspace_has_one_six_step_flow(self):
        labels = [label for _key, label in ProductWorkspace.SECTION_LABELS]
        self.assertEqual(
            labels,
            [
                "۱. اطلاعات پایه",
                "۲. سفارش و قیمت",
                "۳. تصاویر",
                "۴. محتوا و SEO",
                "۵. منبع و فایل",
                "۶. بررسی و انتشار",
            ],
        )
        source = inspect.getsource(ProductWorkspace)
        self.assertIn("def select_section", source)
        self.assertIn("انتشار روی سایت", source)
        self.assertIn("بازه قیمت و متریال/رنگ قابل فروش", source)

    def test_v87_main_products_toolbar_keeps_all_legacy_actions_in_overflow(self):
        source = (ROOT / "app" / "ux87_shell.py").read_text(encoding="utf-8")
        for marker in [
            "بازیابی کامل منبع",
            "مدیریت تصاویر",
            "محتوا و SEO",
            "تولید محتوای AI برای این محصول",
            "تاریخچه تغییرات",
            "تأیید و افزودن به صف انتشار",
            "گزارش انتشار",
            "محاسبه قیمت",
            "باز کردن صفحه منبع",
            "مشخصات و فایل‌ها",
            "بلاک محصولات انتخاب‌شده",
            "AI برای انتخاب‌شده‌ها",
            "AI برای همه نیازمندها",
            "بازیابی انتخاب‌شده‌ها",
            "قیمت انتخاب‌شده‌ها",
        ]:
            self.assertIn(marker, source)

    def test_ai_center_preserves_translation_and_google_controls(self):
        source = (ROOT / "app" / "ux87_shell.py").read_text(encoding="utf-8")
        for marker in ["موتور ترجمه", "Google API Key", "ذخیره امن AI", "تست زنده AI", "translation_provider"]:
            self.assertIn(marker, source)

    def test_connection_center_preserves_manual_batch_ack_action(self):
        source = (ROOT / "app" / "ux87_shell.py").read_text(encoding="utf-8")
        self.assertIn("ارسال آخرین Batch و دریافت ACK", source)
        self.assertIn("command=self.upload_last_batch", source)

    def test_native_icons_do_not_depend_on_font_emoji(self):
        source = (ROOT / "app" / "ux87_icons.py").read_text(encoding="utf-8")
        self.assertIn("ImageDraw", source)
        self.assertIn("ImageTk.PhotoImage", source)
        self.assertNotIn("Segoe UI Emoji", source)

    def test_portable_verify_requires_v87_shell_and_workspace(self):
        source = (ROOT / "portable_entry.py").read_text(encoding="utf-8")
        self.assertIn('"product_workspace_v87"', source)
        self.assertIn('"ux87_shell"', source)
        self.assertIn('"ai_profile_preserved"', source)
        self.assertIn('"host_profile_preserved"', source)


if __name__ == "__main__":
    unittest.main()
