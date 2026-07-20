from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from store.sitemaps import CategorySitemap, ProductSitemap, ServicePageSitemap, StaticViewSitemap

sitemaps = {
    "store-static": StaticViewSitemap,
    "store-products": ProductSitemap,
    "store-categories": CategorySitemap,
    "store-services": ServicePageSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("store/", include("store.urls")),
    path("", include("website.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
