from django.urls import path

from .views import (
    home_view,
    quote_detail_view,
    accept_quote_view,
    robots_txt,
    sitemap_xml,

    customer_register_view,
    customer_login_view,
    customer_logout_view,
    customer_dashboard_view,
    customer_profile_view,
    customer_order_detail_view,
    customer_order_review_create_view,
)

app_name = "website"

urlpatterns = [
    path("", home_view, name="home"),

    path("quote/<uuid:token>/", quote_detail_view, name="quote_detail"),
    path("quote/<uuid:token>/accept/", accept_quote_view, name="accept_quote"),


    path("customer/register/", customer_register_view, name="customer_register"),
    path("customer/login/", customer_login_view, name="customer_login"),
    path("customer/logout/", customer_logout_view, name="customer_logout"),
    path("customer/dashboard/", customer_dashboard_view, name="customer_dashboard"),
    path("customer/profile/", customer_profile_view, name="customer_profile"),
    path("customer/orders/<int:order_id>/", customer_order_detail_view, name="customer_order_detail"),
    path(
        "customer/orders/<int:order_id>/review/",
        customer_order_review_create_view,
        name="customer_order_review_create"
    ),

    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
]

# BEGIN CUSTOMER PORTAL PHASE 3 URLS
from .views import (
    customer_addresses_view,
    customer_address_create_view,
    customer_address_edit_view,
    customer_address_delete_view,
    customer_address_default_view,
)

urlpatterns += [
    path("customer/addresses/", customer_addresses_view, name="customer_addresses"),
    path("customer/addresses/new/", customer_address_create_view, name="customer_address_create"),
    path("customer/addresses/<int:address_id>/edit/", customer_address_edit_view, name="customer_address_edit"),
    path("customer/addresses/<int:address_id>/delete/", customer_address_delete_view, name="customer_address_delete"),
    path("customer/addresses/<int:address_id>/default/", customer_address_default_view, name="customer_address_default"),
]
# END CUSTOMER PORTAL PHASE 3 URLS

# BEGIN PHASE 4 URLS
from .views_phase4 import customer_appearance_view, customer_theme_update_view, iran_cities_view, robots_txt_response, sitemap_xml_response
urlpatterns += [
    path("customer/appearance/", customer_appearance_view, name="customer_appearance"),
    path("customer/theme/", customer_theme_update_view, name="customer_theme_update"),
    path("customer/locations/cities/", iran_cities_view, name="iran_cities"),
    path("robots.txt", robots_txt_response, name="robots_txt_phase4"),
    path("sitemap.xml", sitemap_xml_response, name="sitemap_xml_phase4"),
]
# END PHASE 4 URLS
