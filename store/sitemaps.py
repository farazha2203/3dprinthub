from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Product, ServicePage


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["store:product_list", "store:product_request"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    priority = 0.75
    changefreq = "weekly"

    def items(self):
        return Category.objects.filter(is_active=True)


class ServicePageSitemap(Sitemap):
    priority = 0.85
    changefreq = "monthly"

    def items(self):
        return ServicePage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
