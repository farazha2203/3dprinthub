from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from store.sitemaps import CategorySitemap, ExternalCatalogSitemap, ProductSitemap, ServicePageSitemap, StaticViewSitemap
from django_smartbase_admin.admin.site import sb_admin_site
admin.site.site_header = "مدیریت 3DPrintHub"
admin.site.site_title = "3DPrintHub"
admin.site.index_title = "مرکز فرمان کسب‌وکار"


sitemaps = {
    "store-static": StaticViewSitemap,
    "store-products": ProductSitemap,
    "store-categories": CategorySitemap,
    "store-services": ServicePageSitemap,
    "external-catalog": ExternalCatalogSitemap,
}

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("smart-admin/", sb_admin_site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("store/", include("store.urls")),
    path("", include("website.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
