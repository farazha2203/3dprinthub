from django.test import TestCase
from website.models import Material
from .models import Category, Product, PrintQuality, ProductVariant, ServicePage
from .sitemaps import ProductSitemap
class SEOPhase4Tests(TestCase):
    def test_noindex_product_excluded_from_sitemap(self):
        material=Material.objects.create(name='PLA',price_per_kg=1,main_usage='x',sample_parts='x')
        quality=PrintQuality.objects.create(code='q',name='Q')
        category=Category.objects.create(name='C',slug='c')
        product=Product.objects.create(category=category,title='P',slug='p',sku='P1',short_description='x',description='x',main_image='x.jpg',robots_index=False)
        ProductVariant.objects.create(product=product,material=material,quality=quality,code='v',material_weight_grams=1,print_time_minutes=1)
        self.assertNotIn(product,list(ProductSitemap().items()))
