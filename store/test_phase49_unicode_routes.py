from __future__ import annotations

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from store.models import Product


class Phase4902UnicodeRouteTests(SimpleTestCase):
    unicode_slug = "نظمدهنده-و-نگهدارنده-کفش-دیواری"

    def test_product_absolute_url_accepts_unicode_slug(self):
        product = Product(slug=self.unicode_slug)
        url = product.get_absolute_url()
        self.assertTrue(url.startswith("/store/product/"))
        self.assertNotIn("NoReverseMatch", url)

    def test_product_routes_resolve_unicode_slug(self):
        paths = {
            "epic49_product_compat": f"/store/product/{self.unicode_slug}/",
            "store:toggle_like": f"/store/product/{self.unicode_slug}/like/",
            "store:add_comment": f"/store/product/{self.unicode_slug}/comment/",
            "store:cart_add": f"/store/cart/add/{self.unicode_slug}/",
            "store:product_review": f"/store/product/{self.unicode_slug}/review/",
        }
        for view_name, path in paths.items():
            with self.subTest(view_name=view_name):
                match = resolve(path)
                self.assertEqual(match.view_name, view_name)
                self.assertEqual(match.kwargs["slug"], self.unicode_slug)

    def test_category_route_resolves_unicode_slug(self):
        path = f"/store/category/{self.unicode_slug}/"
        match = resolve(path)
        self.assertEqual(match.view_name, "store:category")
        self.assertEqual(match.kwargs["slug"], self.unicode_slug)

    def test_reverse_round_trip_is_registered_for_unicode(self):
        url = reverse("store:product_detail", kwargs={"slug": self.unicode_slug})
        self.assertTrue(url.startswith("/store/product/"))
