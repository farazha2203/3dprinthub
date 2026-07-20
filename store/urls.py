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

# BEGIN STORE COMMERCE PHASE 2
from .views import (
    cart_add_view, cart_detail_view, cart_remove_view, cart_update_view, checkout_view,
    manual_payment_view, my_orders_view, order_detail_view, order_success_view,
    product_review_view,
)

urlpatterns += [
    path("cart/", cart_detail_view, name="cart_detail"),
    path("cart/add/<slug:slug>/", cart_add_view, name="cart_add"),
    path("cart/update/<int:variant_id>/", cart_update_view, name="cart_update"),
    path("cart/remove/<int:variant_id>/", cart_remove_view, name="cart_remove"),
    path("checkout/", checkout_view, name="checkout"),
    path("payment/manual/<str:order_number>/", manual_payment_view, name="manual_payment"),
    path("order/success/<str:order_number>/", order_success_view, name="order_success"),
    path("account/orders/", my_orders_view, name="my_orders"),
    path("account/orders/<str:order_number>/", order_detail_view, name="order_detail"),
    path("product/<slug:slug>/review/", product_review_view, name="product_review"),
]
# END STORE COMMERCE PHASE 2
