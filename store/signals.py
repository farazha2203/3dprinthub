from django.db.models.signals import post_save
from django.dispatch import receiver

from website.models import Material

from .models import PricingSetting, ProductVariant


@receiver(post_save, sender=Material)
def refresh_variant_prices_for_material(sender, instance, **kwargs):
    for variant in ProductVariant.objects.filter(material=instance).select_related("material"):
        variant.recalculate_price(save=True)


@receiver(post_save, sender=PricingSetting)
def refresh_all_variant_prices(sender, instance, **kwargs):
    for variant in ProductVariant.objects.select_related("material"):
        variant.recalculate_price(save=True)

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7 SIGNALS
from .affiliate_services import assign_order_partner, reverse_commission
from .models import ReturnRequest, StoreOrder


@receiver(post_save, sender=StoreOrder)
def assign_affiliate_partner_to_order(sender, instance, created, **kwargs):
    if created and not instance.affiliate_partner_id:
        assign_order_partner(instance)


@receiver(post_save, sender=ReturnRequest)
def reverse_affiliate_on_refund(sender, instance, **kwargs):
    if instance.status == "refunded":
        reverse_commission(instance.order, reason="استرداد وجه پس از مرجوعی")
# END AFFILIATE PARTNER PROGRAM PHASE 7 SIGNALS

# BEGIN INVENTORY FINANCE CATALOG PHASE 8 SIGNALS
from django.utils import timezone
from website.models import Order as WebsiteOrder
from .production_services import create_job_for_custom_order, finalize_custom_order_job


@receiver(post_save, sender=WebsiteOrder)
def phase8_custom_order_production_job(sender, instance, created, **kwargs):
    if instance.status not in {"accepted", "paid", "in_progress", "done"}:
        return
    job = create_job_for_custom_order(instance)
    if instance.status in {"paid", "in_progress"} and job.status == "planned":
        job.status = "printing"
        job.started_at = job.started_at or timezone.now()
        job.save(update_fields=["status", "started_at", "updated_at"])
    if instance.status == "done":
        finalize_custom_order_job(instance)
# END INVENTORY FINANCE CATALOG PHASE 8 SIGNALS

# BEGIN PHASE 29 VERIFIED PRICING SIGNALS
from .models import CatalogPricingReview, ImportedPrintAsset


@receiver(post_save, sender=CatalogPricingReview)
def phase29_sync_verified_catalog_pricing(sender, instance, update_fields=None, **kwargs):
    if update_fields and set(update_fields).issubset({"verified_at", "updated_at", "notification_sent_at", "notification_error"}):
        return
    if instance.status == "verified" and instance.material_id and instance.weight_grams and instance.print_minutes:
        from .pricing_authority import apply_verified_catalog_pricing
        apply_verified_catalog_pricing(instance)
# END PHASE 29 VERIFIED PRICING SIGNALS

@receiver(post_save, sender=ImportedPrintAsset)
def phase29_ensure_catalog_pricing_queue(sender, instance, created, **kwargs):
    """Every catalog asset must exist in the operator pricing queue."""
    if created:
        CatalogPricingReview.objects.get_or_create(asset=instance)

from .models import CatalogSourcePolicy, PrintCatalogSource
from .source_lifecycle import enforce_source_lifecycle


@receiver(post_save, sender=PrintCatalogSource)
def phase29_enforce_source_state(sender, instance, **kwargs):
    enforce_source_lifecycle(instance)


@receiver(post_save, sender=CatalogSourcePolicy)
def phase29_enforce_policy_state(sender, instance, **kwargs):
    enforce_source_lifecycle(instance.source)
