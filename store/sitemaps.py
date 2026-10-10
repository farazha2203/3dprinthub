from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category, Product, ServicePage
class StaticViewSitemap(Sitemap):
    priority=0.8; changefreq="weekly"
    def items(self): return ["website:home", "store:product_list", "store:isfahan_service_landing"]
    def location(self,item): return reverse(item)
class ProductSitemap(Sitemap):
    priority=0.9; changefreq="weekly"
    def items(self): return Product.objects.filter(is_active=True,robots_index=True)
    def lastmod(self,obj): return obj.updated_at
class CategorySitemap(Sitemap):
    priority = 0.75
    changefreq = "weekly"

    def items(self):
        # Sitemap and robots must agree: empty product categories should not
        # be submitted for indexing. A parent can be indexed when an active
        # direct child contains indexable products.
        eligible_category_ids = set()
        public_products = Product.objects.filter(
            is_active=True, robots_index=True, category__is_active=True
        ).values_list("category_id", "category__parent_id")
        for category_id, parent_id in public_products:
            eligible_category_ids.add(category_id)
            if parent_id:
                eligible_category_ids.add(parent_id)
        return Category.objects.filter(
            is_active=True, robots_index=True, id__in=eligible_category_ids
        )
class ServicePageSitemap(Sitemap):
    priority=0.85; changefreq="monthly"
    def items(self): return ServicePage.objects.filter(is_active=True,robots_index=True)
    def lastmod(self,obj): return obj.updated_at

# BEGIN PHASE 14 EXTERNAL CATALOG SITEMAP
class ExternalCatalogSitemap(Sitemap):
    priority = 0.72
    changefreq = "daily"

    def items(self):
        from store.catalog_sync import public_catalog_queryset
        return (
            public_catalog_queryset()
            .select_related("metrics", "source", "pricing_review")
            .order_by("pk")
        )

    def location(self, obj):
        return reverse("store:external_catalog_detail", args=[obj.pk])

    def lastmod(self, obj):
        return obj.updated_at

    def priority(self, obj):
        try:
            return 0.9 if obj.pricing_review.is_complete else 0.72
        except Exception:
            return 0.72
# END PHASE 14 EXTERNAL CATALOG SITEMAP
