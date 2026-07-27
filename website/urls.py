from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .views import (
    home_view,
    quote_detail_view,
    accept_quote_view,
    quote_payment_view,
    quote_gateway_start_view,
    quote_gateway_callback_view,
    admin_payment_receipt_view,
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
    path("quote/<uuid:token>/payment/", quote_payment_view, name="quote_payment"),
    path("quote/<uuid:token>/payment/gateway/start/", quote_gateway_start_view, name="quote_gateway_start"),
    path("payments/callback/<uuid:callback_token>/", quote_gateway_callback_view, name="quote_gateway_callback"),
    path("secure/payment-receipts/<int:payment_id>/", admin_payment_receipt_view, name="payment_receipt_admin"),


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

# BEGIN PHASE 5 LOCATION URLS
from .views_phase5 import iran_counties_view, iran_cities_v2_view
urlpatterns += [
    path("customer/locations/counties/", iran_counties_view, name="iran_counties"),
    path("customer/locations/cities-v2/", iran_cities_v2_view, name="iran_cities_v2"),
]
# END PHASE 5 LOCATION URLS

# BEGIN PHASE 10 MODEL VAULT URLS
from .views import customer_reorder_model_view, customer_reusable_models_view, private_model_download_view

urlpatterns += [
    path("customer/models/", customer_reusable_models_view, name="customer_reusable_models"),
    path("customer/models/<uuid:token>/reorder/", customer_reorder_model_view, name="customer_reorder_model"),
    path("secure-model-files/<uuid:token>/download/", private_model_download_view, name="private_model_download"),
]
# END PHASE 10 MODEL VAULT URLS

# BEGIN PHASE 19 CUSTOMER SUPPORT CHAT AND PRIVATE ATTACHMENTS
from .support_chat import (
    customer_support_view,
    order_attachment_download,
    order_attachment_preview,
    support_attachment_download,
    support_attachment_preview,
    support_messages_api,
    support_send_api,
    support_widget_state_api,
)

urlpatterns += [
    path("customer/support/", customer_support_view, name="customer_support"),
    path("customer/support/state/", support_widget_state_api, name="support_widget_state"),
    path("customer/support/<uuid:token>/messages/", support_messages_api, name="support_messages_api"),
    path("customer/support/<uuid:token>/send/", support_send_api, name="support_send_api"),
    path("secure-support-files/<uuid:token>/download/", support_attachment_download, name="support_attachment_download"),
    path("secure-support-files/<uuid:token>/preview/", support_attachment_preview, name="support_attachment_preview"),
    path("secure-order-files/<uuid:token>/download/", order_attachment_download, name="order_attachment_download"),
    path("secure-order-files/<uuid:token>/preview/", order_attachment_preview, name="order_attachment_preview"),
]
# END PHASE 19 CUSTOMER SUPPORT CHAT AND PRIVATE ATTACHMENTS

# BEGIN PHASE 22 CUSTOMER PASSWORD RECOVERY
urlpatterns += [
    path(
        "customer/password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="website/customer/password_reset_form.html",
            email_template_name="website/customer/password_reset_email.txt",
            subject_template_name="website/customer/password_reset_subject.txt",
            success_url=reverse_lazy("website:customer_password_reset_done"),
        ),
        name="customer_password_reset",
    ),
    path(
        "customer/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="website/customer/password_reset_done.html"
        ),
        name="customer_password_reset_done",
    ),
    path(
        "customer/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="website/customer/password_reset_confirm.html",
            success_url=reverse_lazy("website:customer_password_reset_complete"),
            post_reset_login=False,
        ),
        name="customer_password_reset_confirm",
    ),
    path(
        "customer/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="website/customer/password_reset_complete.html"
        ),
        name="customer_password_reset_complete",
    ),
]
# END PHASE 22 CUSTOMER PASSWORD RECOVERY
