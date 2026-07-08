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