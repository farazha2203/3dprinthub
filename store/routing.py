from django.urls import path

from .consumers import (
    AdminLinkOperationsConsumer,
    CustomerNotificationConsumer,
    LinkAnalysisProgressConsumer,
)

websocket_urlpatterns = [
    path("ws/customer/notifications/", CustomerNotificationConsumer.as_asgi()),
    path("ws/link-analysis/<uuid:token>/", LinkAnalysisProgressConsumer.as_asgi()),
    path("ws/admin/link-operations/", AdminLinkOperationsConsumer.as_asgi()),
]
