from django.test import TestCase
from django.urls import reverse

from .models import SEOSettings


class SearchCrawlerReadinessTests(TestCase):
    def test_robots_keeps_all_crawlers_blocked_when_setting_is_off(self):
        SEOSettings.objects.create(allow_search_indexing=False)

        response = self.client.get(reverse("website:robots_txt_phase4"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("Disallow: /", response.content.decode())
        self.assertNotIn("Sitemap:", response.content.decode())

    def test_enabled_robots_advertises_only_the_current_root_sitemap(self):
        SEOSettings.objects.create(
            site_url="https://3dprinthub.ir",
            allow_search_indexing=True,
        )

        response = self.client.get(reverse("website:robots_txt_phase4"))
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Allow: /", body)
        self.assertIn("Disallow: /store/checkout/", body)
        self.assertIn("Sitemap: https://3dprinthub.ir/sitemap.xml", body)
        self.assertNotIn("ready-models-sitemap.xml", body)

    def test_current_sitemap_index_does_not_advertise_retired_external_catalog(self):
        SEOSettings.objects.create(allow_search_indexing=True)

        response = self.client.get(reverse("website:sitemap_xml_phase4"))
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response["Content-Type"])
        self.assertNotIn("ready-models", body)
        self.assertNotIn("external_catalog_detail", body)

    def test_enabled_robots_advertises_product_image_sitemap(self):
        SEOSettings.objects.create(
            site_url="https://3dprinthub.ir",
            allow_search_indexing=True,
        )

        response = self.client.get(reverse("website:robots_txt_phase4"))
        body = response.content.decode()

        self.assertIn(
            "Sitemap: https://3dprinthub.ir/sitemap-images.xml",
            body,
        )

    def test_root_sitemap_contains_homepage_and_store(self):
        SEOSettings.objects.create(allow_search_indexing=True)

        response = self.client.get(reverse("website:sitemap_xml_phase4"))
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("<loc>http://example.com/</loc>", body)
        self.assertIn("<loc>http://example.com/store/</loc>", body)

    def test_image_sitemap_is_valid_xml_endpoint(self):
        SEOSettings.objects.create(allow_search_indexing=True)

        response = self.client.get(reverse("website:product_image_sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response["Content-Type"])
        self.assertEqual(response["X-Robots-Tag"], "noindex")
        body = response.content.decode()
        self.assertIn(
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"',
            body,
        )

    def test_global_indexing_toggle_emits_noindex_meta_on_public_pages(self):
        SEOSettings.objects.create(allow_search_indexing=False)

        home = self.client.get(reverse("website:home"))
        store = self.client.get(reverse("store:product_list"))

        self.assertEqual(home.status_code, 200)
        self.assertEqual(store.status_code, 200)
        self.assertIn(
            'meta name="robots" content="noindex,nofollow"',
            home.content.decode(),
        )
        self.assertIn(
            'meta name="robots" content="noindex,nofollow"',
            store.content.decode(),
        )
