"""Regression for category snippets discovered by the 2026-10-09 public crawl."""
from html import unescape
import re

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Product


@override_settings(SECURE_SSL_REDIRECT=False)
class CategorySeoSnippetRegression(TestCase):
    def page(self, slug):
        response = self.client.get(reverse("store:category", kwargs={"slug": slug}))
        self.assertEqual(response.status_code, 200)
        markup = response.content.decode("utf-8")
        description = re.search(r'<meta name="description" content="([^"]*)"', markup)
        og = re.search(r'<meta property="og:description" content="([^"]*)"', markup)
        canonical = re.search(r'<link rel="canonical" href="([^"]*)"', markup)
        return (
            response,
            unescape(description.group(1)) if description else "",
            unescape(og.group(1)) if og else "",
            [unescape(canonical.group(1))] if canonical else [],
        )

    def test_blank_category_has_unique_real_name_based_metadata(self):
        Category.objects.create(name="قطعات تزئینی", slug="seo-decor", description="")
        Category.objects.create(name="قطعات فنی", slug="seo-technical", description="")
        _, first, first_og, first_canon = self.page("seo-decor")
        _, second, second_og, second_canon = self.page("seo-technical")
        self.assertIn("قطعات تزئینی", first)
        self.assertIn("قطعات فنی", second)
        self.assertIn("قطعات تزئینی", first_og)
        self.assertIn("قطعات فنی", second_og)
        self.assertNotEqual(first, second)
        self.assertNotEqual(first_og, second_og)
        self.assertTrue(first_canon[0].endswith("/store/category/seo-decor/"))
        self.assertTrue(second_canon[0].endswith("/store/category/seo-technical/"))

    def test_same_category_description_is_disambiguated_without_db_edit(self):
        same = "ساخت مدل‌های سفارشی با چاپ سه‌بعدی."
        Category.objects.create(name="قطعات خودرو", slug="seo-cars", description=same)
        Category.objects.create(name="قطعات موتور", slug="seo-motors", description=same)
        _, first, first_og, _ = self.page("seo-cars")
        _, second, second_og, _ = self.page("seo-motors")
        self.assertIn(same, first)
        self.assertIn(same, second)
        self.assertIn("قطعات خودرو", first)
        self.assertIn("قطعات موتور", second)
        self.assertNotEqual(first, second)
        self.assertNotEqual(first_og, second_og)

    def test_explicit_editorial_metadata_remains_authoritative(self):
        Category.objects.create(
            name="قطعات دقیق", slug="seo-owned",
            description="توضیح عادی دسته",
            meta_description="توضیح سئوی اختصاصی تأییدشده",
            og_description="توضیح اشتراک‌گذاری اختصاصی تأییدشده",
        )
        _, meta, og, _ = self.page("seo-owned")
        self.assertEqual(meta, "توضیح سئوی اختصاصی تأییدشده")
        self.assertEqual(og, "توضیح اشتراک‌گذاری اختصاصی تأییدشده")

    def test_empty_category_noindex_but_remains_navigable(self):
        cat = Category.objects.create(name="دسته بدون محصول", slug="seo-empty")
        response, desc, _, _ = self.page(cat.slug)
        self.assertEqual(response.status_code, 200)
        self.assertIn("دسته بدون محصول", desc)
        self.assertIn('content="noindex,follow"', response.content.decode())
        cat.refresh_from_db()
        self.assertTrue(cat.robots_index)

    def test_sitemap_excludes_empty_categories_but_readds_with_real_product(self):
        empty = Category.objects.create(name="خالی", slug="seo-empty-sitemap")
        parent = Category.objects.create(name="والد", slug="seo-parent")
        child = Category.objects.create(name="فرزند", slug="seo-child", parent=parent)

        def xml():
            response = self.client.get(reverse("website:sitemap_xml_phase4"))
            self.assertEqual(response.status_code, 200)
            return response.content.decode()

        first = xml()
        self.assertNotIn(empty.get_absolute_url(), first)
        self.assertNotIn(parent.get_absolute_url(), first)
        self.assertNotIn(child.get_absolute_url(), first)

        product = Product.objects.create(
            category=child, title="قطعه نمونه", title_en="Test part",
            slug="seo-child-part", sku="SEO-CHILD-PART-001",
            short_description="قطعه آزمایشی", description="شرح قطعه",
            main_image="store/products/test-part.webp", is_active=True,
        )
        second = xml()
        self.assertIn(parent.get_absolute_url(), second)
        self.assertIn(child.get_absolute_url(), second)
        self.assertNotIn(empty.get_absolute_url(), second)
        home, _, _, _ = self.page(parent.slug)
        self.assertIn('content="index,follow"', home.content.decode())
        product.robots_index = False
        product.save(update_fields=["robots_index"])
        final = xml()
        self.assertNotIn(parent.get_absolute_url(), final)
        self.assertNotIn(child.get_absolute_url(), final)

    def test_filter_still_noindexes_without_altering_category_robots(self):
        category = Category.objects.create(name="قطعات فنی", slug="seo-filter")
        response = self.client.get(
            reverse("store:category", kwargs={"slug": category.slug}), {"q": "something"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('content="noindex,follow"', response.content.decode())
        category.refresh_from_db()
        self.assertTrue(category.robots_index)
