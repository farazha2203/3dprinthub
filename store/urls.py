from django.urls import path

from .views import (
    add_comment_view,
    product_detail_view,
    product_list_view,
    product_request_success_view,
    product_request_view,
    service_page_view,
    toggle_like_view,
)

app_name = "store"

urlpatterns = [
    path("", product_list_view, name="product_list"),
    path("category/<slug:slug>/", product_list_view, name="category"),
    path("product/<slug:slug>/", product_detail_view, name="product_detail"),
    path("product/<slug:slug>/like/", toggle_like_view, name="toggle_like"),
    path("product/<slug:slug>/comment/", add_comment_view, name="add_comment"),
    path("services/<slug:slug>/", service_page_view, name="service_page"),
    path("request-a-part/", product_request_view, name="product_request"),
    path("request-a-part/success/", product_request_success_view, name="product_request_success"),
]
