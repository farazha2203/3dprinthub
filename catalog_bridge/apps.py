from django.apps import AppConfig


class CatalogBridgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog_bridge"
    verbose_name = "Catalog Publishing Bridge"

    def ready(self):
        # Keep the mature import implementation intact while advertising the
        # additive Epic49 read/write management contract from the same Bridge.
        from . import views
        from .ack_enrichment import enrich_import_ack

        views.VERSION = "1.3.0"
        views.PUBLISH_CONTRACT = "epic49-unified-v1"

        original_ack_parser = views._ack_from_output
        if not getattr(original_ack_parser, "_epic49_unified_wrapped", False):
            def _ack_from_output_with_revisions(output):
                return enrich_import_ack(original_ack_parser(output))

            _ack_from_output_with_revisions._epic49_unified_wrapped = True
            views._ack_from_output = _ack_from_output_with_revisions

        # Phase49.3B extends the existing Hero read/write endpoints instead of
        # creating a parallel API. Revision/409/auth semantics remain unchanged.
        from .phase49_3b_media_contract import install as install_phase49_3b_media_contract
        install_phase49_3b_media_contract()
