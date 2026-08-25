from django.urls import path, register_converter

from .converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "uslug")

from .views import (
    add_comment_view,
    product_detail_view,
    product_list_view,
    product_request_success_view,
    product_request_view,
    service_page_view,
    toggle_like_view,
)
from .phase50_variant_views import variant_commerce_options_view

app_name = "store"

urlpatterns = [
    path("", product_list_view, name="product_list"),
    path("category/<uslug:slug>/", product_list_view, name="category"),
    path("product/<uslug:slug>/", product_detail_view, name="product_detail"),
    path("product/<uslug:slug>/like/", toggle_like_view, name="toggle_like"),
    path("product/<uslug:slug>/comment/", add_comment_view, name="add_comment"),
    path("api/variant-commerce-options/", variant_commerce_options_view, name="variant_commerce_options"),
    path("services/<slug:slug>/", service_page_view, name="service_page"),
    path("request-a-part/", product_request_view, name="product_request"),
    path("request-a-part/success/", product_request_success_view, name="product_request_success"),
]

# BEGIN STORE COMMERCE PHASE 2
from .views import (
    cart_add_view,
    cart_detail_view,
    cart_remove_view,
    cart_update_view,
    checkout_view,
    manual_payment_view,
    my_orders_view,
    order_detail_view,
    order_success_view,
    product_review_view,
)

urlpatterns += [
    path("cart/", cart_detail_view, name="cart_detail"),
    path("cart/add/<uslug:slug>/", cart_add_view, name="cart_add"),
    path("cart/update/<int:variant_id>/", cart_update_view, name="cart_update"),
    path("cart/remove/<int:variant_id>/", cart_remove_view, name="cart_remove"),
    path("checkout/", checkout_view, name="checkout"),
    path("payment/manual/<str:order_number>/", manual_payment_view, name="manual_payment"),
    path("order/success/<str:order_number>/", order_success_view, name="order_success"),
    path("account/orders/", my_orders_view, name="my_orders"),
    path("account/orders/<str:order_number>/", order_detail_view, name="order_detail"),
    path("product/<uslug:slug>/review/", product_review_view, name="product_review"),
]
# END STORE COMMERCE PHASE 2

# BEGIN STORE OPERATIONS PHASE 6 URLS
from .views import (
    invoice_view,
    merchant_feed_view,
    notification_read_view,
    notifications_read_all_view,
    notifications_view,
    return_request_view,
)

urlpatterns += [
    path("account/notifications/", notifications_view, name="notifications"),
    path("account/notifications/<int:notification_id>/read/", notification_read_view, name="notification_read"),
    path("account/notifications/read-all/", notifications_read_all_view, name="notifications_read_all"),
    path("account/orders/<str:order_number>/invoice/", invoice_view, name="invoice"),
    path("account/orders/<str:order_number>/return/", return_request_view, name="return_request"),
    path("feeds/google-merchant.xml", merchant_feed_view, name="merchant_feed"),
]
# END STORE OPERATIONS PHASE 6 URLS

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7 URLS
from .views import (
    affiliate_referral_view,
    partner_apply_view,
    partner_campaign_create_view,
    partner_campaign_edit_view,
    partner_dashboard_view,
    partner_payout_request_view,
)

urlpatterns += [
    path("ref/<slug:code>/", affiliate_referral_view, name="affiliate_referral"),
    path("ref/<slug:code>/<slug:campaign_slug>/", affiliate_referral_view, name="affiliate_referral_campaign"),
    path("partner/apply/", partner_apply_view, name="partner_apply"),
    path("partner/dashboard/", partner_dashboard_view, name="partner_dashboard"),
    path("partner/campaigns/new/", partner_campaign_create_view, name="partner_campaign_create"),
    path("partner/campaigns/<int:campaign_id>/edit/", partner_campaign_edit_view, name="partner_campaign_edit"),
    path("partner/payout/request/", partner_payout_request_view, name="partner_payout_request"),
]
# END AFFILIATE PARTNER PROGRAM PHASE 7 URLS

# Phase 49.2A: public external-model intake is intentionally disabled.
# Historical catalog/link-analysis data and worker diagnostics are preserved for audit/rollback,
# but customers cannot browse ready-models or submit external links anymore.

# BEGIN PHASE 25 WORKER HEALTH URL
from .views import link_analysis_worker_health_view

urlpatterns += [
    path("internal/link-worker-health/", link_analysis_worker_health_view, name="link_worker_health"),
]
# END PHASE 25 WORKER HEALTH URL

# BEGIN PHASE 26 OPERATIONS SNAPSHOT URL
from .views import link_analysis_operations_snapshot_view

urlpatterns += [
    path("internal/link-operations-snapshot/", link_analysis_operations_snapshot_view, name="link_operations_snapshot"),
]
# END PHASE 26 OPERATIONS SNAPSHOT URL
