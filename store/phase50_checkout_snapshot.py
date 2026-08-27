from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
from urllib.parse import unquote, urlparse

from django.db import models, transaction

from .models import PricingSetting, StoreOrder, StoreOrderItem


QUOTE_SCHEMA = "phase50.shipping-quote.v1"
_MANUAL_PAYMENT_RE = re.compile(r"/store/payment/manual/([^/]+)/?$")


def _has_field(model, name: str) -> bool:
    return any(field.name == name for field in model._meta.get_fields())


def _contribute(model, name: str, field: models.Field) -> None:
    if not _has_field(model, name):
        field.contribute_to_class(model, name)


def install_model_fields() -> None:
    """Install runtime fields owned by migration 0036.

    The mature store/models.py remains stable. This follows the additive model
    pattern already used by Phase50 Variant2 and Sales Profiles.
    """

    _contribute(
        StoreOrder,
        "insured_value",
        models.PositiveBigIntegerField(
            default=0,
            verbose_name="ارزش اظهارشده / بیمه مرسوله",
        ),
    )
    _contribute(
        StoreOrder,
        "shipping_quote_snapshot",
        models.JSONField(
            blank=True,
            default=dict,
            verbose_name="اسنپ‌شات محاسبه ارسال",
        ),
    )

    for name, field in (
        (
            "sales_profile_name",
            models.CharField(
                blank=True,
                default="",
                max_length=120,
                verbose_name="نام پروفایل هنگام سفارش",
            ),
        ),
        (
            "sales_profile_key",
            models.CharField(
                blank=True,
                default="",
                max_length=80,
                verbose_name="کلید پروفایل هنگام سفارش",
            ),
        ),
        (
            "sales_profile_label",
            models.CharField(
                blank=True,
                default="",
                max_length=180,
                verbose_name="عنوان نمایشی پروفایل هنگام سفارش",
            ),
        ),
        (
            "sales_profile_selection_mode",
            models.CharField(
                blank=True,
                default="",
                max_length=24,
                verbose_name="روش انتخاب پروفایل هنگام سفارش",
            ),
        ),
        (
            "sales_profile_selection_value",
            models.CharField(
                blank=True,
                default="",
                max_length=180,
                verbose_name="انتخاب قابل مشاهده مشتری هنگام سفارش",
            ),
        ),
        (
            "final_weight_grams",
            models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن نهایی قطعه هنگام سفارش",
            ),
        ),
        (
            "shipping_weight_grams",
            models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="وزن قابل محاسبه ارسال هنگام سفارش",
            ),
        ),
        (
            "print_time_minutes",
            models.PositiveIntegerField(
                default=0,
                verbose_name="زمان چاپ هنگام سفارش به دقیقه",
            ),
        ),
    ):
        _contribute(StoreOrderItem, name, field)


def _decimal(value) -> Decimal:
    return Decimal(value or 0)


def effective_variant_shipping_weight(variant) -> Decimal:
    effective = getattr(variant, "effective_shipping_weight_grams", None)
    if effective is not None:
        return _decimal(effective)
    explicit = _decimal(getattr(variant, "shipping_weight_grams", 0))
    if explicit > 0:
        return explicit
    product_weight = _decimal(
        getattr(variant, "final_weight_grams", 0)
        or getattr(variant, "material_weight_grams", 0)
        or 0
    )
    return product_weight + _decimal(getattr(variant, "packaging_weight_grams", 0))


def _money_round(value) -> int:
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _decimal_text(value) -> str:
    return format(_decimal(value), "f")


def _snapshot_item(item: StoreOrderItem) -> dict:
    variant = item.variant
    if variant is None:
        return {
            "item_id": item.pk,
            "quantity": int(item.quantity),
            "variant_id": None,
            "profile_key": str(getattr(item, "sales_profile_key", "") or ""),
            "profile_label": str(getattr(item, "sales_profile_label", "") or ""),
            "size_label": str(getattr(item, "size_label", "") or ""),
            "build_profile": str(getattr(item, "build_profile", "") or ""),
            "unit_shipping_weight_grams": _decimal_text(getattr(item, "shipping_weight_grams", 0)),
            "line_shipping_weight_grams": _decimal_text(_decimal(getattr(item, "shipping_weight_grams", 0)) * int(item.quantity)),
            "packaging_weight_grams": _decimal_text(getattr(item, "packaging_weight_grams", 0)),
            "part_dimensions_cm": {
                "length": _decimal_text(getattr(item, "part_length_cm", 0)),
                "width": _decimal_text(getattr(item, "part_width_cm", 0)),
                "height": _decimal_text(getattr(item, "part_height_cm", 0)),
            },
            "package_dimensions_cm": {
                "length": _decimal_text(getattr(item, "package_length_cm", 0)),
                "width": _decimal_text(getattr(item, "package_width_cm", 0)),
                "height": _decimal_text(getattr(item, "package_height_cm", 0)),
            },
        }

    final_weight = _decimal(
        getattr(variant, "final_weight_grams", 0)
        or getattr(variant, "material_weight_grams", 0)
        or 0
    )
    shipping_weight = effective_variant_shipping_weight(variant)
    selection_mode = str(getattr(variant.product, "sales_profile_selection_mode", "") or "")
    profile_name = str(getattr(variant, "sales_profile_name", "") or "")
    profile_key = str(getattr(variant, "sales_profile_key", "") or "")
    profile_label = str(getattr(variant, "sales_profile_display_label", "") or "")
    selection_value = str(getattr(variant, "sales_profile_selection_value", "") or profile_label)

    item.sales_profile_name = profile_name
    item.sales_profile_key = profile_key
    item.sales_profile_label = profile_label
    item.sales_profile_selection_mode = selection_mode
    item.sales_profile_selection_value = selection_value
    item.size_label = str(getattr(variant, "size_label", "") or "")
    item.build_profile = str(getattr(variant, "build_profile", "standard") or "standard")
    item.final_weight_grams = final_weight
    item.packaging_weight_grams = _decimal(getattr(variant, "packaging_weight_grams", 0))
    item.shipping_weight_grams = shipping_weight
    item.unit_weight_grams = shipping_weight
    item.print_time_minutes = int(getattr(variant, "print_time_minutes", 0) or 0)
    item.part_length_cm = _decimal(getattr(variant, "part_length_cm", 0))
    item.part_width_cm = _decimal(getattr(variant, "part_width_cm", 0))
    item.part_height_cm = _decimal(getattr(variant, "part_height_cm", 0))
    item.package_length_cm = _decimal(getattr(variant, "package_length_cm", 0))
    item.package_width_cm = _decimal(getattr(variant, "package_width_cm", 0))
    item.package_height_cm = _decimal(getattr(variant, "package_height_cm", 0))

    item.save(
        update_fields=[
            "sales_profile_name",
            "sales_profile_key",
            "sales_profile_label",
            "sales_profile_selection_mode",
            "sales_profile_selection_value",
            "size_label",
            "build_profile",
            "final_weight_grams",
            "packaging_weight_grams",
            "shipping_weight_grams",
            "unit_weight_grams",
            "print_time_minutes",
            "part_length_cm",
            "part_width_cm",
            "part_height_cm",
            "package_length_cm",
            "package_width_cm",
            "package_height_cm",
        ]
    )

    return {
        "item_id": item.pk,
        "quantity": int(item.quantity),
        "variant_id": variant.pk,
        "profile_name": profile_name,
        "profile_key": profile_key,
        "profile_label": profile_label,
        "selection_mode": selection_mode,
        "selection_value": selection_value,
        "size_label": item.size_label,
        "build_profile": item.build_profile,
        "material": item.material_name,
        "color": item.color_name,
        "quality": item.quality_name,
        "final_weight_grams": _decimal_text(final_weight),
        "unit_shipping_weight_grams": _decimal_text(shipping_weight),
        "line_shipping_weight_grams": _decimal_text(shipping_weight * int(item.quantity)),
        "packaging_weight_grams": _decimal_text(item.packaging_weight_grams),
        "print_time_minutes": int(item.print_time_minutes),
        "part_dimensions_cm": {
            "length": _decimal_text(item.part_length_cm),
            "width": _decimal_text(item.part_width_cm),
            "height": _decimal_text(item.part_height_cm),
        },
        "package_dimensions_cm": {
            "length": _decimal_text(item.package_length_cm),
            "width": _decimal_text(item.package_width_cm),
            "height": _decimal_text(item.package_height_cm),
        },
    }


def finalize_order_checkout_snapshot(order: StoreOrder) -> StoreOrder:
    """Freeze customer-visible profile and normalized shipping state atomically.

    The current ShippingMethod table/rules remain the fallback quote authority.
    No external Post/Tipax/Mahex API is claimed or called here. Per-line package
    dimensions are preserved without inventing a combined carton geometry.
    """

    items = list(
        order.items.select_for_update()
        .select_related(
            "variant",
            "variant__product",
            "variant__material",
            "variant__quality",
            "variant__color",
        )
        .order_by("pk")
    )

    packages = []
    total_weight = Decimal("0")
    total_units = 0
    for item in items:
        package = _snapshot_item(item)
        packages.append(package)
        unit_weight = _decimal(package.get("unit_shipping_weight_grams", 0))
        total_weight += unit_weight * int(item.quantity)
        total_units += int(item.quantity)

    merchandise_value = max(0, int(order.subtotal) - int(order.discount_amount or 0))
    shipping_method = order.shipping_method
    if shipping_method is not None:
        shipping_fee = int(shipping_method.calculate_fee(merchandise_value, total_weight))
    else:
        shipping_fee = int(order.shipping_fee or 0)

    pricing = PricingSetting.load()
    taxable_amount = merchandise_value + int(order.packaging_fee or 0) + shipping_fee
    tax_amount = (
        _money_round(Decimal(taxable_amount) * Decimal(pricing.tax_percent) / Decimal("100"))
        if pricing.vat_enabled
        else 0
    )
    total_amount = merchandise_value + int(order.packaging_fee or 0) + shipping_fee + tax_amount

    quote = {
        "schema": QUOTE_SCHEMA,
        "source": "shipping_method_fallback",
        "external_carrier_quote": False,
        "method": {
            "id": shipping_method.pk if shipping_method else None,
            "code": str(getattr(shipping_method, "code", "") or ""),
            "title": str(order.shipping_title or getattr(shipping_method, "title", "") or ""),
        },
        "destination": {
            "province": str(order.province or ""),
            "county": str(order.county or ""),
            "city": str(order.city or ""),
            "postal_code": str(order.postal_code or ""),
        },
        "merchandise_value": merchandise_value,
        "insured_value": merchandise_value,
        "total_weight_grams": _decimal_text(total_weight),
        "shipping_fee": shipping_fee,
        "package_units": total_units,
        "packages": packages,
        "combined_parcel_dimensions_inferred": False,
        "requires_final_packing": bool(len(packages) != 1 or total_units != 1),
    }

    order.total_weight_grams = total_weight
    order.insured_value = merchandise_value
    order.shipping_fee = shipping_fee
    order.tax_amount = tax_amount
    order.total_amount = total_amount
    order.shipping_quote_snapshot = quote
    order.save(
        update_fields=[
            "total_weight_grams",
            "insured_value",
            "shipping_fee",
            "tax_amount",
            "total_amount",
            "shipping_quote_snapshot",
            "updated_at",
        ]
    )
    order.payments.filter(status="pending").update(amount=total_amount)
    return order


def _order_number_from_response(response) -> str:
    location = str(response.get("Location", "") or "")
    if not location:
        return ""
    path = unquote(urlparse(location).path)
    match = _MANUAL_PAYMENT_RE.search(path)
    return match.group(1) if match else ""


def _install_cart_weight_contract() -> None:
    from .cart import Cart

    if getattr(Cart.items, "_phase50_checkout_snapshot", False):
        return

    original_items = Cart.items

    @wraps(original_items)
    def items(self):
        result = original_items(self)
        for entry in result:
            variant = entry.get("variant")
            if variant is None:
                continue
            unit_weight = effective_variant_shipping_weight(variant)
            entry["unit_weight"] = unit_weight
            entry["line_weight"] = unit_weight * int(entry.get("quantity") or 0)
        return result

    items._phase50_checkout_snapshot = True
    Cart.items = items


def _install_checkout_atomic_finalizer() -> None:
    from .cart import Cart
    from . import views

    original = views.checkout_view
    if getattr(original, "_phase50_checkout_snapshot", False):
        return

    @wraps(original)
    def checkout_view(request, *args, **kwargs):
        if request.method != "POST":
            return original(request, *args, **kwargs)

        cart_before = dict(Cart(request).data)
        try:
            with transaction.atomic():
                response = original(request, *args, **kwargs)
                order_number = _order_number_from_response(response)
                if order_number:
                    order = StoreOrder.objects.select_for_update().get(
                        order_number=order_number,
                        user=request.user,
                    )
                    finalize_order_checkout_snapshot(order)
                return response
        except Exception:
            request.session[Cart.SESSION_KEY] = cart_before
            request.session.modified = True
            raise

    checkout_view._phase50_checkout_snapshot = True
    checkout_view._phase50_checkout_original = original
    views.checkout_view = checkout_view


def install_runtime() -> None:
    _install_cart_weight_contract()
    _install_checkout_atomic_finalizer()
