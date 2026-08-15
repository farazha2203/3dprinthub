from django.urls import path

from .views import health_view, import_view


app_name = "catalog_bridge"

urlpatterns = [
    path("health/", health_view, name="health"),
    path("import/", import_view, name="import"),
]
