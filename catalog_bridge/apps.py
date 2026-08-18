from django.apps import AppConfig


class CatalogBridgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog_bridge"
    verbose_name = "Catalog Publishing Bridge"

    def ready(self):
        # Keep the mature import implementation intact while advertising the
        # additive Epic49 read/write management contract from the same Bridge.
        from . import views

        views.VERSION = "1.3.0"
        views.PUBLISH_CONTRACT = "epic49-unified-v1"
