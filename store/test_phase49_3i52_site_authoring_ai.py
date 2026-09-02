from __future__ import annotations

from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from ai import model_policy
from ai.product_content import apply_site_product_proposal
from store.epic49_catalog_profile import ensure_admin_catalog_profile
from store.models import Category, ImportedPrintAsset, PrintCatalogSource, Product
from store.phase49_3i52_site_authoring_ai import ProductCatalogProfileInline
from store.phase49_3i52_site_identity import reconcile_asset_product_identity


@override_settings(
    MEDIA_ROOT="/tmp/3dprinthub-phase49-3i52-media",
    PRIVATE_MEDIA_ROOT="/tmp/3dprinthub-phase49-3i52-private",
)
class Phase493I52SiteAuthoringAITests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="دکور",
            slug="decor",
            section="creative",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=self.category,
            title="پایه کیک",
            title_en="Cake Stand",
            slug="cake-stand-site",
            sku="SITE-3I52-001",
            short_description="توضیح اولیه",
            description="توضیح کامل اولیه",
            main_image="store/products/test.jpg",
            order_mode="fixed",
            fixed_price=350000,
            price_is_final=True,
            is_active=False,
        )

    def test_manual_site_product_gets_real_catalog_profile_and_fixed_price_authority(self):
        profile = ensure_admin_catalog_profile(
            self.product,
            actor="owner",
            bump_revision=True,
        )
        self.assertEqual(profile.product_id, self.product.pk)
        self.assertEqual(profile.last_modified_source, "admin")
        self.assertEqual(profile.last_modified_by, "owner")
        self.assertEqual(profile.price_min, 350000)
        self.assertEqual(profile.price_max, 350000)
        self.assertEqual(profile.price_mode, "fixed")
        self.assertEqual(profile.pricing_strategy, "fixed")
        self.assertFalse(self.product.is_active)

    def test_ai_apply_changes_content_only_and_preserves_commerce_facts(self):
        profile = ensure_admin_catalog_profile(self.product, actor="owner")
        profile.stock_quantity = 7
        profile.commercial_license_status = "verified"
        profile.license_name = "Commercial"
        profile.technical_features = {
            "ابعاد تأییدشده اپراتور": "120×80×35 mm",
            "کاربرد": "ثبت دستی اپراتور",
        }
        profile.save()

        proposal = {
            "provider": "openrouter",
            "model": "test/free-model:free",
            "free": True,
            "content": {
                "title_fa": "پایه کیک مینیمال برای پذیرایی",
                "short_description_fa": "پایه کیک دکوراتیو برای سرو و چیدمان.",
                "description_fa": "توضیح کامل فارسی و دقیق برای محصول.",
                "use_description_fa": "مناسب سرو کیک و شیرینی.",
                "seo_title_fa": "خرید پایه کیک مینیمال چاپ سه‌بعدی",
                "seo_description_fa": "سفارش پایه کیک مینیمال با امکان انتخاب متریال و رنگ.",
                "target_keywords_fa": ["خرید پایه کیک چاپ سه‌بعدی"],
                "hashtags_fa": ["#پایه_کیک", "#پرینت_سه_بعدی"],
                "specs_fa": [{"key": "کاربرد", "value": "پذیرایی"}],
                "sales_bullets": ["طراحی مینیمال"],
                "image_alt_texts": [],
                "homepage_slider_seo": {
                    "title_fa": "پایه کیک مینیمال",
                    "description_fa": "انتخابی ساده برای میز پذیرایی",
                    "image_alt_fa": "پایه کیک مینیمال چاپ سه‌بعدی",
                    "button_text_fa": "مشاهده محصول",
                    "focus_keyword_fa": "پایه کیک مینیمال",
                },
            },
        }

        fixed_before = self.product.fixed_price
        active_before = self.product.is_active
        result = apply_site_product_proposal(
            self.product,
            proposal,
            actor="owner",
        )
        self.product.refresh_from_db()
        profile.refresh_from_db()

        self.assertIn("title", result["changed_product_fields"])
        self.assertEqual(self.product.fixed_price, fixed_before)
        self.assertEqual(self.product.is_active, active_before)
        self.assertEqual(profile.stock_quantity, 7)
        self.assertEqual(profile.commercial_license_status, "verified")
        self.assertEqual(profile.license_name, "Commercial")
        self.assertEqual(profile.price_min, 350000)
        self.assertEqual(profile.price_max, 350000)
        self.assertEqual(
            self.product.title,
            "پایه کیک مینیمال برای پذیرایی",
        )
        self.assertEqual(
            profile.technical_features["کاربرد"],
            "ثبت دستی اپراتور",
        )
        self.assertEqual(
            profile.technical_features["ابعاد تأییدشده اپراتور"],
            "120×80×35 mm",
        )
        self.assertFalse(profile.homepage_slider_enabled)

    def test_product_admin_has_site_profile_inline_ai_preview_and_manual_site_controls(self):
        product_admin = admin.site._registry[Product]
        self.assertTrue(
            any(
                inline is ProductCatalogProfileInline
                or getattr(inline, "model", None)
                is ProductCatalogProfileInline.model
                for inline in product_admin.inlines
            )
        )
        self.assertIn("phase52_ai_admin", product_admin.readonly_fields)
        self.assertIn("phase52_site_parity_admin", product_admin.readonly_fields)
        titles = [title for title, _options in product_admin.fieldsets]
        from store.phase50_product_admin_workspace import SECTION_TITLES
        self.assertEqual(tuple(titles), SECTION_TITLES)
        field_map = {
            title: tuple(options.get("fields", ()))
            for title, options in product_admin.fieldsets
        }
        self.assertIn("phase52_ai_admin", field_map["SEO"])
        self.assertIn("phase52_site_parity_admin", field_map["قیمت‌گذاری"])

        User = get_user_model()
        user = User.objects.create_superuser(
            username="phase52-owner",
            email="owner@example.com",
            password="test-pass-12345",
        )
        self.client.force_login(user)
        url = reverse(
            "admin:store_product_phase49_3i52_ai",
            args=[self.product.pk],
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI محتوا و SEO")
        self.assertContains(response, "AI قیمت، موجودی")

    def test_manual_site_product_public_page_uses_same_canonical_profile_price(self):
        self.product.is_active = True
        self.product.save(update_fields=["is_active", "updated_at"])
        profile = ensure_admin_catalog_profile(
            self.product,
            actor="owner",
            bump_revision=True,
        )
        profile.availability_status = "made_to_order"
        profile.lead_time_min_days = 2
        profile.lead_time_max_days = 4
        profile.save()

        response = self.client.get(
            reverse("store:product_detail", args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قیمت قطعی")
        self.assertContains(response, "وضعیت عرضه")
        self.assertContains(response, "زمان آماده‌سازی")
        rendered_product = response.context["product"]
        self.assertEqual(rendered_product.catalog_profile.price_min, 350000)
        self.assertEqual(
            rendered_product.catalog_profile.pricing_strategy,
            "fixed",
        )

    def test_desktop_import_identity_links_exact_manual_site_product_instead_of_duplicate(self):
        source = PrintCatalogSource.objects.create(
            name="MakerWorld Phase52 Link",
            code="makerworld-phase52-link",
            base_url="https://makerworld.com",
            default_category=self.category,
            is_active=True,
        )
        self.product.source_name = "MakerWorld Phase52 Link"
        self.product.source_external_id = "2834255"
        self.product.source_url = (
            "https://makerworld.com/en/models/2834255-cake-stand"
        )
        self.product.save(
            update_fields=[
                "source_name",
                "source_external_id",
                "source_url",
                "updated_at",
            ]
        )
        profile = ensure_admin_catalog_profile(self.product, actor="owner")
        asset = ImportedPrintAsset.objects.create(
            source=source,
            external_id="2834255",
            source_url=(
                "https://makerworld.com/en/models/2834255-cake-stand/"
            ),
            title="Cake Stand",
        )

        linked = reconcile_asset_product_identity(
            asset,
            {
                "source_url": asset.source_url,
                "external_id": "2834255",
                "desktop_product_id": 781,
            },
            desktop_product_id=781,
        )
        asset.refresh_from_db()
        profile.refresh_from_db()

        self.assertEqual(linked.pk, self.product.pk)
        self.assertEqual(asset.product_id, self.product.pk)
        self.assertEqual(profile.desktop_product_id, 781)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.product.fixed_price, 350000)

    def test_desktop_import_identity_fails_closed_on_ambiguous_site_products(self):
        source = PrintCatalogSource.objects.create(
            name="MakerWorld Phase52 Ambiguous",
            code="makerworld-phase52-ambiguous",
            base_url="https://makerworld.com",
            default_category=self.category,
            is_active=True,
        )
        self.product.source_name = "MakerWorld Phase52 Ambiguous"
        self.product.source_external_id = "999"
        self.product.source_url = "https://makerworld.com/en/models/site-one"
        self.product.save(
            update_fields=[
                "source_name",
                "source_external_id",
                "source_url",
                "updated_at",
            ]
        )
        Product.objects.create(
            category=self.category,
            title="Duplicate source identity",
            slug="duplicate-source-identity",
            sku="SITE-3I52-002",
            short_description="test",
            description="test",
            source_name="MakerWorld Phase52 Ambiguous",
            source_external_id="999",
            source_url="https://makerworld.com/en/models/site-two",
            is_active=False,
        )
        asset = ImportedPrintAsset.objects.create(
            source=source,
            external_id="999",
            source_url="https://makerworld.com/en/models/incoming",
            title="Incoming",
        )

        with self.assertRaises(ValidationError):
            reconcile_asset_product_identity(
                asset,
                {
                    "source_url": asset.source_url,
                    "external_id": "999",
                    "desktop_product_id": 900,
                },
                desktop_product_id=900,
            )
        asset.refresh_from_db()
        self.assertIsNone(asset.product_id)

    def test_admin_ai_preview_requires_explicit_apply(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="phase52-preview",
            email="preview@example.com",
            password="test-pass-12345",
        )
        self.client.force_login(user)
        url = reverse(
            "admin:store_product_phase49_3i52_ai",
            args=[self.product.pk],
        )
        proposal = {
            "provider": "openrouter",
            "model": "verified-free:free",
            "free": True,
            "content": {
                "title_fa": "پیشنهاد بدون اعمال",
                "short_description_fa": "تست",
                "description_fa": "تست",
                "seo_title_fa": "تست",
                "seo_description_fa": "تست",
                "use_description_fa": "تست",
                "target_keywords_fa": [],
                "content_notes": [],
                "suggested_category_slug": "decor",
            },
        }
        with patch(
            "store.phase49_3i52_site_authoring_ai.build_site_product_proposal",
            return_value=proposal,
        ):
            response = self.client.post(url, {"action": "generate"})
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "پایه کیک")
        self.assertContains(response, "پیشنهاد بدون اعمال")


class Phase493I52ModelPolicyTests(TestCase):
    def test_explicit_variable_openrouter_router_is_rejected_for_product_work(self):
        model_policy._SELECTION_CACHE.clear()
        with patch.dict(
            "os.environ",
            {
                "AI_SITE_PROVIDER": "openrouter",
                "OPENROUTER_API_KEY": "ci-fake-key",
                "AI_SITE_PRODUCT_MODEL": "openrouter/free",
            },
            clear=False,
        ):
            with self.assertRaises(RuntimeError):
                model_policy.resolve_product_model(force_refresh=True)

    def test_auto_policy_prefers_exact_verified_free_persian_structured_model(self):
        model_policy._SELECTION_CACHE.clear()

        class FakeClient:
            def __init__(self, provider, key, model="", product_id=None):
                self.provider = provider

            def list_model_info(self):
                return [
                    {
                        "id": "openrouter/free",
                        "name": "variable router",
                        "free": True,
                        "supported_parameters": ["response_format"],
                    },
                    {
                        "id": "vendor/free-no-json:free",
                        "name": "Free",
                        "free": True,
                        "supported_parameters": [],
                    },
                    {
                        "id": "vendor/persian-structured:free",
                        "name": "Multilingual Instruct",
                        "description": "multilingual instruction model",
                        "free": True,
                        "supported_parameters": ["response_format"],
                        "pricing": {"prompt": "0", "completion": "0"},
                    },
                ]

            def structured_response(
                self,
                *,
                instructions,
                input_content,
                schema,
                schema_name,
                preferred_model="",
            ):
                return {"answer": "آماده"}, preferred_model

        with patch.dict(
            "os.environ",
            {
                "AI_SITE_PROVIDER": "openrouter",
                "OPENROUTER_API_KEY": "ci-fake-key",
            },
            clear=False,
        ), patch("ai.model_policy.AIProviderClient", FakeClient):
            selection = model_policy.resolve_product_model(force_refresh=True)

        self.assertEqual(selection.provider, "openrouter")
        self.assertEqual(selection.model, "vendor/persian-structured:free")
        self.assertTrue(selection.free)
        self.assertEqual(selection.reason, "free-persian-structured")
