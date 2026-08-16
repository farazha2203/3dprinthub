from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ImportedPrintAsset
from .epic49_publish_options import sync_epic49_publish_options


logger = logging.getLogger(__name__)


@receiver(post_save, sender=ImportedPrintAsset, dispatch_uid="epic49_sync_publish_options")
def epic49_sync_publish_options(sender, instance, raw=False, **kwargs):
    """Apply operator-selected Store options once the imported asset has a Product.

    Fixture/raw saves are ignored. The synchronizer is idempotent and never
    deletes media or catalog source data.
    """
    if raw or not getattr(instance, "product_id", None):
        return
    try:
        sync_epic49_publish_options(instance)
    except Exception:
        logger.exception("EPIC49_PUBLISH_OPTIONS_SYNC_FAILED asset_id=%s product_id=%s", instance.pk, instance.product_id)
        raise
