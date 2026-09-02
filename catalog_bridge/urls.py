from django.urls import path

from .views import diagnostic_view, health_view, import_view
from .publish_readiness import publish_readiness_view
from .unified_views import (
    filament_sync_view,
    filaments_view,
    hero_slide_detail_view,
    hero_slide_sync_view,
    hero_slides_view,
    product_detail_view,
    product_sync_view,
    products_view,
)


app_name = "catalog_bridge"

urlpatterns = [
    path("health/", health_view, name="health"),
    path("publish-readiness/", publish_readiness_view, name="publish_readiness"),
    path("import/", import_view, name="import"),
    path("diagnostics/<str:batch_name>/", diagnostic_view, name="diagnostic"),

    # Epic49 unified Desktop <-> Server management surface. All endpoints reuse
    # the existing Catalog Bridge bearer token and optimistic revision contract.
    path("products/", products_view, name="products"),
    path("products/<int:product_id>/", product_detail_view, name="product_detail"),
    path("products/<int:product_id>/sync/", product_sync_view, name="product_sync"),
    path("filaments/", filaments_view, name="filaments"),
    path("filaments/sync/", filament_sync_view, name="filament_sync"),
    path("hero-slides/", hero_slides_view, name="hero_slides"),
    path("hero-slides/<int:slide_id>/", hero_slide_detail_view, name="hero_slide_detail"),
    path("hero-slides/<int:slide_id>/sync/", hero_slide_sync_view, name="hero_slide_sync"),
]
