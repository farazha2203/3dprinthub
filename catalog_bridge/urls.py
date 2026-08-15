from django.urls import path

from .views import diagnostic_view, health_view, import_view


app_name = "catalog_bridge"

urlpatterns = [
    path("health/", health_view, name="health"),
    path("import/", import_view, name="import"),
    path("diagnostics/<str:batch_name>/", diagnostic_view, name="diagnostic"),
]
