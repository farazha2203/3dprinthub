from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import redirect
from django.urls import include, path, re_path

from store.public_media import serve_public_store_media
from store.epic49_routes import product_detail_by_id_view, product_detail_compat_view
from store.sitemaps import CategorySitemap, ProductSitemap, ServicePageSitemap, StaticViewSitemap
from website.phase50a_admin_command_center import phase50_admin_command_center
from django_smartbase_admin.admin.site import sb_admin_site
admin.site.site_header = "مدیریت 3DPrintHub"
admin.site.site_title = "3DPrintHub"
admin.site.index_title = "مرکز فرمان کسب‌وکار"


sitemaps = {
    "store-static": StaticViewSitemap,
    "store-products": ProductSitemap,
    "store-categories": CategorySitemap,
    "store-services": ServicePageSitemap,
}


def favicon_redirect(_request):
    return redirect(f"{settings.STATIC_URL}favicon/favicon.ico", permanent=True)


urlpatterns = [
    path("favicon.ico", favicon_redirect, name="favicon"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("accounts/", include("allauth.urls")),
    path(
        "admin/command-center/",
        admin.site.admin_view(phase50_admin_command_center),
        name="phase50_admin_command_center",
    ),
    path("admin/", admin.site.urls),
    path("smart-admin/", sb_admin_site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("store/p/<int:pk>/", product_detail_by_id_view, name="epic49_product_by_id"),
    re_path(r"^store/product/(?P<slug>[^/]+)/$", product_detail_compat_view, name="epic49_product_compat"),
    path("store/", include("store.urls")),
    path("api/catalog-bridge/v1/", include("catalog_bridge.urls")),
    path("", include("website.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>store/(?:products|categories|seo)/.*)$",
            serve_public_store_media,
            name="public_store_media",
        )
    ]
