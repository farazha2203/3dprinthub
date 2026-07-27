from __future__ import annotations

from decimal import Decimal

from .models import ProductVariant


class Cart:
    SESSION_KEY = "store_cart_v1"

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(self.SESSION_KEY, {})

    def _save(self):
        self.session[self.SESSION_KEY] = self.data
        self.session.modified = True

    def add(self, variant, quantity=1, *, replace=False):
        key = str(variant.pk)
        current = int(self.data.get(key, 0))
        target = int(quantity) if replace else current + int(quantity)
        target = max(target, variant.minimum_quantity)
        if variant.maximum_quantity:
            target = min(target, variant.maximum_quantity)
        self.data[key] = target
        self._save()

    def update(self, variant, quantity):
        if int(quantity) <= 0:
            self.remove(variant.pk)
            return
        self.add(variant, quantity, replace=True)

    def remove(self, variant_id):
        self.data.pop(str(variant_id), None)
        self._save()

    def clear(self):
        self.session.pop(self.SESSION_KEY, None)
        self.session.modified = True
        self.data = {}

    def items(self):
        variant_ids = [int(key) for key in self.data.keys() if str(key).isdigit()]
        variants = ProductVariant.objects.filter(
            pk__in=variant_ids,
            is_active=True,
            product__is_active=True,
        ).select_related("product", "material", "quality")
        mapping = {str(item.pk): item for item in variants}
        stale = []
        result = []
        for key, quantity in self.data.items():
            variant = mapping.get(str(key))
            if not variant or variant.stock_status == "out_of_stock":
                stale.append(str(key))
                continue
            quantity = int(quantity)
            quantity = max(quantity, variant.minimum_quantity)
            if variant.maximum_quantity:
                quantity = min(quantity, variant.maximum_quantity)
            unit_price = int(variant.price_breakdown()["unit_price"])
            unit_weight = Decimal(variant.shipping_weight_grams or variant.final_weight_grams or variant.material_weight_grams or 0)
            result.append({
                "variant": variant,
                "product": variant.product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
                "unit_weight": unit_weight,
                "line_weight": unit_weight * quantity,
            })
        if stale:
            for key in stale:
                self.data.pop(key, None)
            self._save()
        return result

    def summary(self):
        items = self.items()
        return {
            "items": items,
            "subtotal": sum(item["line_total"] for item in items),
            "total_weight": sum((item["line_weight"] for item in items), Decimal("0")),
            "count": sum(item["quantity"] for item in items),
        }
