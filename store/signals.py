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
