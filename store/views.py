from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F, Min, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductCommentForm, ProductRequestForm
from .phase39_models import ProductReviewImage
from .models import (
    Category,
    PrintQuality,
    Product,
    ProductLike,
    ProductRequestImage,
    ServicePage,
)


SORT_MAP = {
    "newest": ("-published_at", "-id"),
    "popular": ("-view_count", "-published_at"),
    "liked": ("-like_count", "-published_at"),
    "rating": ("-review_average", "-published_at"),
    "cheapest": ("min_price", "-published_at"),
    "expensive": ("-min_price", "-published_at"),
}


def _product_queryset():
    return (
        Product.objects.filter(is_active=True, category__is_active=True)
        .select_related("category")
        .prefetch_related("images", "compatibilities", "variants__material", "variants__quality", "variants__color", "material_options__material", "promotions", "reviews__images")
        .annotate(
            like_count=Count("likes", distinct=True),
            review_average=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            min_price=Min("variants__cached_unit_price", filter=Q(variants__is_active=True)),
        )
    )


def product_list_view(request, slug=None):
    products = _product_queryset()
    current_category = None

    if slug:
        current_category = get_object_or_404(Category, slug=slug, is_active=True)
        category_ids = [current_category.id]
        category_ids.extend(current_category.children.filter(is_active=True).values_list("id", flat=True))
        products = products.filter(category_id__in=category_ids)

    query = request.GET.get("q", "").strip()
    section = request.GET.get("section", "").strip()
    material = request.GET.get("material", "").strip()
    quality = request.GET.get("quality", "").strip()
    sort = request.GET.get("sort", "newest")

    if query:
        products = products.filter(
            Q(title__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
            | Q(sku__icontains=query)
            | Q(compatibilities__brand__icontains=query)
            | Q(compatibilities__model__icontains=query)
        ).distinct()
    if section:
        products = products.filter(category__section=section)
    if material.isdigit():
        products = products.filter(variants__material_id=int(material), variants__is_active=True).distinct()
    if quality.isdigit():
        products = products.filter(variants__quality_id=int(quality), variants__is_active=True).distinct()

    products = products.order_by(*SORT_MAP.get(sort, SORT_MAP["newest"]))

    from website.models import Material

    context = {
        "products": products,
        "categories": Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children"),
        "materials": Material.objects.filter(is_active=True),
        "qualities": PrintQuality.objects.filter(is_active=True),
        "current_category": current_category,
        "current_sort": sort,
        "query": query,
        "section": section,
        "selected_material": material,
        "selected_quality": quality,
    }
    return render(request, "store/product_list.html", context)


def product_detail_view(request, slug):
    product = get_object_or_404(_product_queryset(), slug=slug)
    Product.objects.filter(pk=product.pk).update(view_count=F("view_count") + 1)

    variants = product.variants.filter(is_active=True).select_related("material", "quality", "color").order_by(
        "quality__sort_order", "material__sort_order"
    )
    comments = product.comments.filter(is_approved=True).select_related("user")
    reviews = product.reviews.filter(is_approved=True).select_related("user")
    is_liked = request.user.is_authenticated and ProductLike.objects.filter(product=product, user=request.user).exists()

    context = {
        "product": product,
        "variants": variants,
        "comments": comments,
        "reviews": reviews,
        "comment_form": ProductCommentForm(),
        "is_liked": is_liked,
        "related_products": _product_queryset().filter(category=product.category).exclude(pk=product.pk)[:4],
        "material_options": product.material_options.filter(is_customer_selectable=True).select_related("material"),
        "active_promotions": [p for p in product.promotions.all() if p.is_current],
        "public_order_count": product.store_order_items.filter(order__payment_status="paid").aggregate(v=Count("id"))["v"] or 0,
    }
    return render(request, "store/product_detail.html", context)


@login_required
@require_POST
def toggle_like_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    like, created = ProductLike.objects.get_or_create(product=product, user=request.user)
    liked = created
    if not created:
        like.delete()
        liked = False

    count = ProductLike.objects.filter(product=product).count()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "count": count})
    return redirect(product.get_absolute_url())


@login_required
@require_POST
def add_comment_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = ProductCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.product = product
        comment.user = request.user
        comment.save()
        messages.success(request, "دیدگاه شما ثبت شد و پس از تأیید نمایش داده می‌شود.")
    else:
        messages.error(request, "متن دیدگاه معتبر نیست.")
    return redirect(product.get_absolute_url())


def service_page_view(request, slug):
    page = get_object_or_404(ServicePage, slug=slug, is_active=True)
    related_products = _product_queryset().filter(category__section={
        "automotive": "automotive",
        "home_appliance": "home_appliance",
        "industrial": "industrial",
        "model_making": "academic",
        "kids_drawing": "creative",
        "custom_figure": "creative",
    }.get(page.service_type, "general"))[:6]
    return render(request, "store/service_page.html", {"page": page, "related_products": related_products})


def product_request_view(request):
    if request.method == "POST":
        form = ProductRequestForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product_request = form.save(commit=False)
            if request.user.is_authenticated:
                product_request.user = request.user
            product_request.save()
            for image in request.FILES.getlist("images"):
                ProductRequestImage.objects.create(request=product_request, image=image)
            messages.success(request, "درخواست شما ثبت شد. پس از بررسی فنی با شما تماس می‌گیریم.")
            return redirect("store:product_request_success")
        messages.error(request, "اطلاعات فرم را بررسی کنید.")
    else:
        form = ProductRequestForm(user=request.user)
    return render(request, "store/product_request.html", {"form": form})


def product_request_success_view(request):
    return render(request, "store/product_request_success.html")

# BEGIN STORE COMMERCE PHASE 2
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .cart import Cart
from .forms import AddToCartForm, CheckoutForm, ManualPaymentForm, ProductReviewForm
from .models import (
    PricingSetting, ProductReview, ProductVariant, ShippingMethod, StoreAddress,
    StoreOrder, StoreOrderItem, StorePayment,
)


def cart_detail_view(request):
    summary = Cart(request).summary()
    return render(request, "store/cart_detail.html", {"cart": summary})


@require_POST
def cart_add_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = AddToCartForm(request.POST, product=product)
    if form.is_valid():
        Cart(request).add(form.variant, form.cleaned_data["quantity"])
        messages.success(request, "محصول به سبد خرید اضافه شد.")
        next_url = request.POST.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("store:cart_detail")
    messages.error(request, " ".join(form.non_field_errors()) or "انتخاب محصول معتبر نیست.")
    return redirect(product.get_absolute_url())


@require_POST
def cart_update_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id, is_active=True, product__is_active=True)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    Cart(request).update(variant, quantity)
    messages.success(request, "سبد خرید به‌روزرسانی شد.")
    return redirect("store:cart_detail")


@require_POST
def cart_remove_view(request, variant_id):
    Cart(request).remove(variant_id)
    messages.success(request, "محصول از سبد خرید حذف شد.")
    return redirect("store:cart_detail")


def _money_round(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@login_required
def checkout_view(request):
    cart = Cart(request)
    initial_summary = cart.summary()
    if not initial_summary["items"]:
        messages.error(request, "سبد خرید شما خالی است.")
        return redirect("store:product_list")

    form = CheckoutForm(
        request.POST or None,
        user=request.user,
        subtotal=initial_summary["subtotal"],
    )
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                cart_data = dict(cart.data)
                ids = [int(key) for key in cart_data if str(key).isdigit()]
                locked_variants = ProductVariant.objects.select_for_update().filter(
                    pk__in=ids,
                    is_active=True,
                    product__is_active=True,
                ).select_related("product", "material", "quality")
                variants = {str(v.pk): v for v in locked_variants}
                lines = []
                subtotal = 0
                total_weight = Decimal("0")
                for key, raw_quantity in cart_data.items():
                    variant = variants.get(str(key))
                    if not variant or variant.stock_status == "out_of_stock":
                        raise ValidationError("یکی از محصولات سبد خرید دیگر قابل سفارش نیست.")
                    quantity = int(raw_quantity)
                    if quantity < variant.minimum_quantity:
                        raise ValidationError(f"حداقل تعداد {variant.product.title} برابر {variant.minimum_quantity} است.")
                    if variant.maximum_quantity and quantity > variant.maximum_quantity:
                        raise ValidationError(f"حداکثر تعداد {variant.product.title} برابر {variant.maximum_quantity} است.")
                    unit_price = int(variant.price_breakdown()["unit_price"])
                    unit_weight = Decimal(variant.shipping_weight_grams or variant.final_weight_grams or variant.material_weight_grams or 0)
                    line_total = unit_price * quantity
                    subtotal += line_total
                    total_weight += unit_weight * quantity
                    lines.append((variant, quantity, unit_price, line_total, unit_weight))

                pricing = PricingSetting.load()
                shipping = form.cleaned_data["shipping_method"]
                packaging_fee = int(pricing.packaging_fee)
                shipping_fee = int(shipping.calculate_fee(subtotal, total_weight))
                tax_base = subtotal + packaging_fee + shipping_fee
                tax_amount = _money_round(Decimal(tax_base) * Decimal(pricing.tax_percent) / Decimal("100")) if pricing.vat_enabled else 0
                total_amount = subtotal + packaging_fee + shipping_fee + tax_amount

                order = form.save(commit=False)
                order.user = request.user
                order.shipping_title = shipping.title
                order.subtotal = subtotal
                order.packaging_fee = packaging_fee
                order.shipping_fee = shipping_fee
                order.tax_amount = tax_amount
                order.total_amount = total_amount
                order.total_weight_grams = total_weight
                order.status = "awaiting_payment"
                order.payment_status = "pending"
                order.save()

                StoreOrderItem.objects.bulk_create([
                    StoreOrderItem(
                        order=order,
                        product=variant.product,
                        variant=variant,
                        product_title=variant.product.title,
                        product_sku=variant.product.sku,
                        variant_code=variant.code,
                        material_name=variant.material.name,
                        quality_name=variant.quality.name,
                        color_name=variant.color.name if variant.color_id else "",
                        unit_cost_snapshot=int(variant.price_breakdown().get("estimated_cost") or 0),
                        gross_profit=(unit_price - int(variant.price_breakdown().get("estimated_cost") or 0)) * quantity,
                        material_charge_snapshot=int(variant.price_breakdown().get("material_cost") or 0),
                        machine_charge_snapshot=int(variant.price_breakdown().get("machine_cost") or 0),
                        labor_charge_snapshot=int(variant.price_breakdown().get("labor_cost") or 0),
                        accessory_charge_snapshot=int(variant.price_breakdown().get("accessory_sale") or 0),
                        assembly_charge_snapshot=int(variant.price_breakdown().get("assembly_cost") or 0),
                        color_adjustment_snapshot=int(variant.price_breakdown().get("color_price_adjustment") or 0),
                        unit_price=unit_price,
                        quantity=quantity,
                        line_total=line_total,
                        unit_weight_grams=unit_weight,
                    )
                    for variant, quantity, unit_price, line_total, unit_weight in lines
                ])
                payment = StorePayment.objects.create(
                    order=order,
                    amount=total_amount,
                    method=form.cleaned_data["payment_method"],
                    status="pending",
                )

                if form.cleaned_data.get("save_address"):
                    StoreAddress.objects.update_or_create(
                        user=request.user,
                        is_default=True,
                        defaults={
                            "title": "آدرس اصلی",
                            "full_name": order.full_name,
                            "phone": order.phone,
                            "province": order.province,
                            "city": order.city,
                            "address": order.address,
                            "postal_code": order.postal_code,
                        },
                    )
                cart.clear()
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            return redirect("store:manual_payment", order_number=order.order_number)

    pricing = PricingSetting.load()
    context = {
        "form": form,
        "cart": initial_summary,
        "pricing": pricing,
    }
    return render(request, "store/checkout.html", context)


@login_required
def manual_payment_view(request, order_number):
    order = get_object_or_404(StoreOrder, order_number=order_number, user=request.user)
    payment = order.payments.order_by("-created_at").first()
    if not payment:
        payment = StorePayment.objects.create(order=order, amount=order.total_amount, method="bank_transfer")
    if order.payment_status == "paid":
        return redirect(order.get_absolute_url())
    form = ManualPaymentForm(request.POST or None, request.FILES or None, instance=payment)
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.method = "bank_transfer"
        payment.status = "awaiting_review"
        payment.amount = order.total_amount
        payment.save()
        order.payment_status = "awaiting_review"
        order.status = "payment_review"
        order.save(update_fields=["payment_status", "status", "updated_at"])
        messages.success(request, "رسید پرداخت ثبت شد و پس از بررسی تأیید می‌شود.")
        return redirect("store:order_success", order_number=order.order_number)
    return render(request, "store/payment_manual.html", {"order": order, "payment": payment, "form": form})


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(StoreOrder, order_number=order_number, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def my_orders_view(request):
    orders = StoreOrder.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "store/my_orders.html", {"orders": orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(
        StoreOrder.objects.prefetch_related("items", "payments"),
        order_number=order_number,
        user=request.user,
    )
    return render(request, "store/order_detail.html", {"order": order})


@login_required
def product_review_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    verified = StoreOrderItem.objects.filter(
        product=product,
        order__user=request.user,
        order__payment_status="paid",
        order__status__in=["paid", "processing", "ready", "shipped", "delivered"],
    ).exists()
    if not verified:
        messages.error(request, "ثبت امتیاز فقط برای خریداران تأییدشده این محصول امکان‌پذیر است.")
        return redirect(product.get_absolute_url())
    review = ProductReview.objects.filter(product=product, user=request.user).first()
    form = ProductReviewForm(request.POST or None, request.FILES or None, instance=review)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.product = product
        obj.user = request.user
        obj.is_verified_purchase = True
        obj.is_approved = False
        obj.save()
        for image in request.FILES.getlist("images")[:8]:
            ProductReviewImage.objects.create(review=obj, image=image, is_approved=False)
        messages.success(request, "نظر و تصاویر شما ثبت شد و پس از تأیید نمایش داده می‌شود.")
        return redirect(product.get_absolute_url())
    return render(request, "store/review_form.html", {"product": product, "form": form})
# END STORE COMMERCE PHASE 2

# BEGIN CUSTOMER PORTAL PHASE 3 CHECKOUT VIEW
@login_required
def checkout_view(request):
    cart = Cart(request)
    initial_summary = cart.summary()
    if not initial_summary["items"]:
        messages.error(request, "سبد خرید شما خالی است.")
        return redirect("store:product_list")

    form = CheckoutForm(request.POST or None, user=request.user, subtotal=initial_summary["subtotal"])
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                cart_data = dict(cart.data)
                ids = [int(key) for key in cart_data if str(key).isdigit()]
                locked_variants = ProductVariant.objects.select_for_update().filter(
                    pk__in=ids, is_active=True, product__is_active=True,
                ).select_related("product", "material", "quality")
                variants = {str(v.pk): v for v in locked_variants}
                lines, subtotal = [], 0
                total_weight = Decimal("0")
                for key, raw_quantity in cart_data.items():
                    variant = variants.get(str(key))
                    if not variant or variant.stock_status == "out_of_stock":
                        raise ValidationError("یکی از محصولات سبد خرید دیگر قابل سفارش نیست.")
                    quantity = int(raw_quantity)
                    if quantity < variant.minimum_quantity:
                        raise ValidationError(f"حداقل تعداد {variant.product.title} برابر {variant.minimum_quantity} است.")
                    if variant.maximum_quantity and quantity > variant.maximum_quantity:
                        raise ValidationError(f"حداکثر تعداد {variant.product.title} برابر {variant.maximum_quantity} است.")
                    unit_price = int(variant.price_breakdown()["unit_price"])
                    unit_weight = Decimal(variant.shipping_weight_grams or variant.final_weight_grams or variant.material_weight_grams or 0)
                    line_total = unit_price * quantity
                    subtotal += line_total
                    total_weight += unit_weight * quantity
                    lines.append((variant, quantity, unit_price, line_total, unit_weight))

                pricing = PricingSetting.load()
                shipping = form.cleaned_data["shipping_method"]
                packaging_fee = int(pricing.packaging_fee)
                shipping_fee = int(shipping.calculate_fee(subtotal, total_weight))
                tax_base = subtotal + packaging_fee + shipping_fee
                tax_amount = _money_round(Decimal(tax_base) * Decimal(pricing.tax_percent) / Decimal("100")) if pricing.vat_enabled else 0
                total_amount = subtotal + packaging_fee + shipping_fee + tax_amount

                order = StoreOrder(
                    user=request.user,
                    shipping_method=shipping,
                    shipping_title=shipping.title,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    email=form.cleaned_data.get("email", ""),
                    province=form.cleaned_data["province"],
                    city=form.cleaned_data["city"],
                    address=form.cleaned_data["address"],
                    postal_code=form.cleaned_data["postal_code"],
                    customer_note=form.cleaned_data.get("customer_note", ""),
                    subtotal=subtotal,
                    packaging_fee=packaging_fee,
                    shipping_fee=shipping_fee,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    total_weight_grams=total_weight,
                    status="awaiting_payment",
                    payment_status="pending",
                )
                order.save()
                StoreOrderItem.objects.bulk_create([
                    StoreOrderItem(
                        order=order, product=variant.product, variant=variant,
                        product_title=variant.product.title, product_sku=variant.product.sku,
                        variant_code=variant.code, material_name=variant.material.name,
                        quality_name=variant.quality.name, unit_price=unit_price,
                        quantity=quantity, line_total=line_total, unit_weight_grams=unit_weight,
                    )
                    for variant, quantity, unit_price, line_total, unit_weight in lines
                ])
                StorePayment.objects.create(
                    order=order, amount=total_amount,
                    method=form.cleaned_data["payment_method"], status="pending",
                )
                if form.cleaned_data.get("save_address") and not form.cleaned_data.get("saved_address"):
                    StoreAddress.objects.create(
                        user=request.user,
                        title="آدرس سفارش",
                        full_name=order.full_name,
                        phone=order.phone,
                        province=order.province,
                        city=order.city,
                        address=order.address,
                        postal_code=order.postal_code,
                        is_default=not StoreAddress.objects.filter(user=request.user).exists(),
                    )
                cart.clear()
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            return redirect("store:manual_payment", order_number=order.order_number)

    return render(request, "store/checkout.html", {
        "form": form,
        "cart": initial_summary,
        "pricing": PricingSetting.load(),
    })
# END CUSTOMER PORTAL PHASE 3 CHECKOUT VIEW

# BEGIN STORE OPERATIONS PHASE 6 VIEWS
from datetime import timedelta
from xml.sax.saxutils import escape as xml_escape

from django.http import HttpResponse
from django.utils import timezone

from .forms import CheckoutOperationsForm, ReturnRequestForm
from .models import CustomerNotification, ReturnRequest, StoreInvoice
from .services import (
    notify,
    record_event,
    reserve_order_inventory,
    validate_coupon,
)


@login_required
def checkout_view(request):
    cart = Cart(request)
    initial_summary = cart.summary()
    if not initial_summary["items"]:
        messages.error(request, "سبد خرید شما خالی است.")
        return redirect("store:product_list")

    form = CheckoutOperationsForm(request.POST or None, user=request.user, subtotal=initial_summary["subtotal"])
    price_preview = None
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                cart_data = dict(cart.data)
                ids = [int(key) for key in cart_data if str(key).isdigit()]
                locked_variants = ProductVariant.objects.select_for_update().filter(
                    pk__in=ids,
                    is_active=True,
                    product__is_active=True,
                ).select_related("product", "product__category", "material", "quality")
                variants = {str(v.pk): v for v in locked_variants}
                lines, subtotal = [], 0
                total_weight = Decimal("0")
                for key, raw_quantity in cart_data.items():
                    variant = variants.get(str(key))
                    if not variant or variant.stock_status == "out_of_stock":
                        raise ValidationError("یکی از محصولات سبد خرید دیگر قابل سفارش نیست.")
                    quantity = int(raw_quantity)
                    if quantity < variant.minimum_quantity:
                        raise ValidationError(f"حداقل تعداد {variant.product.title} برابر {variant.minimum_quantity} است.")
                    if variant.maximum_quantity and quantity > variant.maximum_quantity:
                        raise ValidationError(f"حداکثر تعداد {variant.product.title} برابر {variant.maximum_quantity} است.")
                    if variant.track_inventory and not variant.allow_backorder:
                        available = max(0, int(variant.stock_quantity) - int(variant.reserved_quantity))
                        if quantity > available:
                            raise ValidationError(f"موجودی {variant.product.title} کافی نیست؛ فقط {available} عدد قابل سفارش است.")
                    if variant.color_id and Decimal(variant.color.current_stock_grams or 0) < (Decimal(variant.material_weight_grams or 0) * quantity):
                        raise ValidationError(f"موجودی رنگ {variant.color.name} برای {variant.product.title} کافی نیست.")
                    unit_price = int(variant.price_breakdown()["unit_price"])
                    unit_weight = Decimal(variant.shipping_weight_grams or variant.final_weight_grams or variant.material_weight_grams or 0)
                    line_total = unit_price * quantity
                    subtotal += line_total
                    total_weight += unit_weight * quantity
                    lines.append((variant, quantity, unit_price, line_total, unit_weight))

                coupon, discount_amount = validate_coupon(
                    form.cleaned_data.get("coupon_code"),
                    user=request.user,
                    cart_lines=lines,
                    subtotal=subtotal,
                )
                pricing = PricingSetting.load()
                shipping = form.cleaned_data["shipping_method"]
                packaging_fee = int(pricing.packaging_fee)
                shipping_fee = int(shipping.calculate_fee(subtotal - discount_amount, total_weight))
                taxable_amount = max(0, subtotal - discount_amount) + packaging_fee + shipping_fee
                tax_amount = _money_round(Decimal(taxable_amount) * Decimal(pricing.tax_percent) / Decimal("100")) if pricing.vat_enabled else 0
                total_amount = max(0, subtotal - discount_amount) + packaging_fee + shipping_fee + tax_amount

                saved = form.cleaned_data.get("saved_address")
                if saved:
                    full_name, phone = saved.full_name, saved.phone
                    province, county, city = saved.province, saved.county, saved.city
                    address, postal_code = saved.address, saved.postal_code
                else:
                    full_name = form.cleaned_data["full_name"]
                    phone = form.cleaned_data["phone"]
                    province = form.cleaned_data["province"]
                    county = form.cleaned_data["county"]
                    city = form.cleaned_data["city"]
                    address = form.cleaned_data["address"]
                    postal_code = form.cleaned_data["postal_code"]

                order = StoreOrder.objects.create(
                    user=request.user,
                    shipping_method=shipping,
                    shipping_title=shipping.title,
                    full_name=full_name,
                    phone=phone,
                    email=form.cleaned_data.get("email", ""),
                    province=province,
                    county=county,
                    city=city,
                    address=address,
                    postal_code=postal_code,
                    customer_note=form.cleaned_data.get("customer_note", ""),
                    subtotal=subtotal,
                    packaging_fee=packaging_fee,
                    shipping_fee=shipping_fee,
                    tax_amount=tax_amount,
                    discount_amount=discount_amount,
                    coupon=coupon,
                    coupon_code=coupon.code if coupon else "",
                    total_amount=total_amount,
                    total_weight_grams=total_weight,
                    status="awaiting_payment",
                    payment_status="pending",
                )
                StoreOrderItem.objects.bulk_create([
                    StoreOrderItem(
                        order=order,
                        product=variant.product,
                        variant=variant,
                        product_title=variant.product.title,
                        product_sku=variant.product.sku,
                        variant_code=variant.code,
                        material_name=variant.material.name,
                        quality_name=variant.quality.name,
                        color_name=variant.color.name if variant.color_id else "",
                        unit_cost_snapshot=int(variant.price_breakdown().get("estimated_cost") or 0),
                        gross_profit=(unit_price - int(variant.price_breakdown().get("estimated_cost") or 0)) * quantity,
                        material_charge_snapshot=int(variant.price_breakdown().get("material_cost") or 0),
                        machine_charge_snapshot=int(variant.price_breakdown().get("machine_cost") or 0),
                        labor_charge_snapshot=int(variant.price_breakdown().get("labor_cost") or 0),
                        accessory_charge_snapshot=int(variant.price_breakdown().get("accessory_sale") or 0),
                        assembly_charge_snapshot=int(variant.price_breakdown().get("assembly_cost") or 0),
                        color_adjustment_snapshot=int(variant.price_breakdown().get("color_price_adjustment") or 0),
                        unit_price=unit_price,
                        quantity=quantity,
                        line_total=line_total,
                        unit_weight_grams=unit_weight,
                    )
                    for variant, quantity, unit_price, line_total, unit_weight in lines
                ])
                reserve_order_inventory(order)
                StorePayment.objects.create(
                    order=order,
                    amount=total_amount,
                    method=form.cleaned_data["payment_method"],
                    status="pending",
                )
                record_event(order, "سفارش ثبت شد", "سفارش ثبت و موجودی آن تا پایان مهلت پرداخت رزرو شد.")
                notify(
                    request.user,
                    "سفارش شما ثبت شد",
                    f"سفارش {order.order_number} ثبت شد و تا ۹۰ دقیقه در انتظار پرداخت است.",
                    notification_type="order",
                    url=order.get_absolute_url(),
                )
                if form.cleaned_data.get("save_address") and not saved:
                    StoreAddress.objects.create(
                        user=request.user,
                        title="آدرس سفارش",
                        full_name=full_name,
                        phone=phone,
                        province=province,
                        county=county,
                        city=city,
                        address=address,
                        postal_code=postal_code,
                        is_default=not StoreAddress.objects.filter(user=request.user).exists(),
                    )
                cart.clear()
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
        else:
            return redirect("store:manual_payment", order_number=order.order_number)

    return render(request, "store/checkout.html", {
        "form": form,
        "cart": initial_summary,
        "pricing": PricingSetting.load(),
        "price_preview": price_preview,
    })


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(
        StoreOrder.objects.prefetch_related("items", "payments", "events", "return_requests"),
        order_number=order_number,
        user=request.user,
    )
    shipment = getattr(order, "shipment", None)
    invoice = getattr(order, "invoice", None)
    return render(request, "store/order_detail.html", {
        "order": order,
        "shipment": shipment,
        "invoice": invoice,
        "events": order.events.filter(is_public=True),
        "return_requests": order.return_requests.all(),
    })


@login_required
def invoice_view(request, order_number):
    order = get_object_or_404(StoreOrder.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    invoice = get_object_or_404(StoreInvoice, order=order)
    return render(request, "store/invoice.html", {"order": order, "invoice": invoice})


@login_required
def notifications_view(request):
    notifications = CustomerNotification.objects.filter(user=request.user)
    return render(request, "store/notifications.html", {"notifications": notifications})


@login_required
@require_POST
def notification_read_view(request, notification_id):
    notification = get_object_or_404(CustomerNotification, pk=notification_id, user=request.user)
    if not notification.read_at:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
        try:
            from .realtime import publish_notification_count
            publish_notification_count(request.user.pk)
        except Exception:
            pass
    next_url = request.POST.get("next") or notification.url or reverse("store:notifications")
    return redirect(next_url)


@login_required
@require_POST
def notifications_read_all_view(request):
    CustomerNotification.objects.filter(user=request.user, read_at__isnull=True).update(read_at=timezone.now())
    try:
        from .realtime import publish_notification_count
        publish_notification_count(request.user.pk)
    except Exception:
        pass
    return redirect("store:notifications")


@login_required
def return_request_view(request, order_number):
    order = get_object_or_404(StoreOrder.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    if not order.can_request_return:
        messages.error(request, "ثبت درخواست مرجوعی فقط پس از تحویل سفارش امکان‌پذیر است.")
        return redirect(order.get_absolute_url())
    try:
        from website.models import SEOSettings
        return_days = (SEOSettings.objects.first().merchant_return_days or 7)
    except Exception:
        return_days = 7
    shipment = getattr(order, "shipment", None)
    delivered_at = getattr(shipment, "delivered_at", None) or order.updated_at
    if delivered_at and timezone.now() > delivered_at + timedelta(days=return_days):
        messages.error(request, f"مهلت {return_days} روزه ثبت درخواست مرجوعی پایان یافته است.")
        return redirect(order.get_absolute_url())
    form = ReturnRequestForm(request.POST or None, request.FILES or None, order=order)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.order = order
        obj.user = request.user
        obj.save()
        record_event(order, "درخواست مرجوعی ثبت شد", "درخواست مشتری برای بررسی به واحد پشتیبانی ارسال شد.")
        notify(request.user, "درخواست مرجوعی ثبت شد", f"درخواست مرجوعی سفارش {order.order_number} ثبت شد.", notification_type="order", url=order.get_absolute_url())
        messages.success(request, "درخواست مرجوعی ثبت شد و پس از بررسی نتیجه اعلام می‌شود.")
        return redirect(order.get_absolute_url())
    return render(request, "store/return_request.html", {"order": order, "form": form})


def merchant_feed_view(request):
    try:
        from website.models import SEOSettings
        seo = SEOSettings.objects.first()
    except Exception:
        seo = None
    site_url = (getattr(seo, "site_url", "") or f"{request.scheme}://{request.get_host()}").rstrip("/")
    shipping_toman = int(getattr(seo, "shipping_rate", 0) or 0)
    variants = ProductVariant.objects.filter(
        is_active=True,
        product__is_active=True,
        product__robots_index=True,
    ).select_related("product", "product__category", "material", "quality")
    items = []
    for variant in variants.iterator():
        product = variant.product
        if variant.stock_status == "out_of_stock" or (variant.track_inventory and not variant.allow_backorder and variant.available_quantity <= 0):
            availability = "out_of_stock"
        elif variant.stock_status == "preorder":
            availability = "preorder"
        elif variant.track_inventory and variant.allow_backorder and variant.available_quantity <= 0:
            availability = "backorder"
        else:
            availability = "in_stock"
        price_irr = int(variant.cached_unit_price or variant.price_breakdown()["unit_price"]) * 10
        title = f"{product.title} - {variant.material.name} - {variant.quality.name}"
        link = f"{site_url}{product.get_absolute_url()}"
        image = f"{site_url}{product.main_image.url}"
        category_path = product.category.name
        xml = [
            "<item>",
            f"<g:id>{xml_escape(variant.code)}</g:id>",
            f"<g:item_group_id>{xml_escape(product.sku)}</g:item_group_id>",
            f"<g:title>{xml_escape(title[:150])}</g:title>",
            f"<g:description>{xml_escape((product.short_description or product.description)[:5000])}</g:description>",
            f"<g:link>{xml_escape(link)}</g:link>",
            f"<g:image_link>{xml_escape(image)}</g:image_link>",
            "<g:condition>new</g:condition>",
            f"<g:availability>{availability}</g:availability>",
            f"<g:price>{price_irr} IRR</g:price>",
            f"<g:brand>{xml_escape(product.brand_name or '3DprintHub')}</g:brand>",
            f"<g:product_type>{xml_escape(category_path)}</g:product_type>",
            f"<g:material>{xml_escape(variant.material.name)}</g:material>",
        ]
        if product.gtin:
            xml.append(f"<g:gtin>{xml_escape(product.gtin)}</g:gtin>")
        elif product.mpn:
            xml.append(f"<g:mpn>{xml_escape(product.mpn)}</g:mpn>")
        else:
            xml.append("<g:identifier_exists>no</g:identifier_exists>")
        xml.extend([
            "<g:shipping>", "<g:country>IR</g:country>", "<g:service>Standard</g:service>",
            f"<g:price>{shipping_toman * 10} IRR</g:price>", "</g:shipping>", "</item>",
        ])
        items.append("".join(xml))
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0"><channel>'
        f'<title>{xml_escape(getattr(seo, "organization_name", "") or "3DprintHub")}</title>'
        f'<link>{xml_escape(site_url)}</link>'
        '<description>فید محصولات فروشگاه 3DprintHub</description>'
        + "".join(items) + '</channel></rss>'
    )
    return HttpResponse(body, content_type="application/xml; charset=utf-8")
# END STORE OPERATIONS PHASE 6 VIEWS

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7 VIEWS
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Sum
from django.views.decorators.http import require_http_methods

from .affiliate_services import (
    COOKIE_NAME as AFFILIATE_COOKIE_NAME,
    capture_referral,
    masked_customer,
    request_partner_payout,
    safe_campaign_target,
    signed_referral_payload,
)
from .forms import AffiliateCampaignForm, AffiliatePartnerApplicationForm, AffiliatePayoutRequestForm
from .models import AffiliateAttribution, AffiliateCampaign, AffiliateCommission, AffiliatePartner, AffiliatePayout


def _active_partner_for(user):
    return AffiliatePartner.objects.select_related("tier").filter(user=user, status="active", tier__is_active=True).first()


def _partner_account_context(user):
    from website.views import _phase3_profile, _profile_completion
    profile = _phase3_profile(user)
    return {"profile": profile, "profile_completion": _profile_completion(profile)}


def affiliate_referral_view(request, code, campaign_slug=""):
    partner, campaign, _ = capture_referral(request, code, campaign_slug, landing_path=request.get_full_path())
    if not partner:
        messages.error(request, "لینک معرفی معتبر یا فعال نیست.")
        return redirect("store:product_list")
    target = safe_campaign_target(campaign, request)
    response = redirect(target)
    response.set_cookie(
        AFFILIATE_COOKIE_NAME,
        signed_referral_payload(partner.code, campaign.slug if campaign else ""),
        max_age=int(partner.effective_attribution_days) * 86400,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )
    return response


@login_required
def partner_apply_view(request):
    partner = AffiliatePartner.objects.select_related("tier").filter(user=request.user).first()
    if partner and partner.status == "active":
        return redirect("store:partner_dashboard")
    form = AffiliatePartnerApplicationForm(request.POST or None, user=request.user, instance=partner)
    if request.method == "POST" and form.is_valid():
        partner = form.save()
        messages.success(request, "درخواست همکاری ثبت شد و پس از بررسی مدیریت نتیجه اعلام می‌شود.")
        return redirect("store:partner_apply")
    context = {"form": form, "partner": partner, **_partner_account_context(request.user)}
    return render(request, "store/partner/application.html", context)


@login_required
def partner_dashboard_view(request):
    partner = _active_partner_for(request.user)
    if not partner:
        messages.error(request, "برای مشاهده پنل همکاری باید درخواست شما توسط مدیریت تأیید شود.")
        return redirect("store:partner_apply")
    commissions = AffiliateCommission.objects.filter(partner=partner)
    status_totals = {
        row["status"]: row["value"] or 0
        for row in commissions.values("status").annotate(value=Sum("amount"))
    }
    paid_orders = partner.referred_orders.filter(payment_status="paid")
    campaigns = list(partner.campaigns.annotate(click_total=Count("clicks"), customer_total=Count("attributions", distinct=True), order_total=Count("orders", distinct=True)).order_by("-created_at"))
    base_url = request.build_absolute_uri("/").rstrip("/")
    campaign_rows = []
    for campaign in campaigns:
        campaign_rows.append({
            "obj": campaign,
            "url": request.build_absolute_uri(reverse("store:affiliate_referral_campaign", kwargs={"code": partner.code, "campaign_slug": campaign.slug})),
        })
    attributions = AffiliateAttribution.objects.filter(partner=partner).select_related("customer", "campaign").order_by("-attributed_at")[:20]
    customer_rows = [{"label": masked_customer(item.customer), "campaign": item.campaign, "date": item.attributed_at} for item in attributions]
    context = {
        "partner": partner,
        "main_referral_url": request.build_absolute_uri(reverse("store:affiliate_referral", kwargs={"code": partner.code})),
        "campaign_rows": campaign_rows,
        "customer_rows": customer_rows,
        "recent_commissions": commissions.select_related("order", "campaign").order_by("-created_at")[:20],
        "recent_payouts": AffiliatePayout.objects.filter(partner=partner).order_by("-requested_at")[:10],
        "clicks": partner.clicks.count(),
        "unique_clicks": partner.clicks.values("visitor_hash").distinct().count(),
        "customers": partner.attributions.count(),
        "paid_orders": paid_orders.count(),
        "referred_revenue": paid_orders.aggregate(value=Sum("total_amount"))["value"] or 0,
        "pending_amount": status_totals.get("pending", 0),
        "available_amount": status_totals.get("approved", 0),
        "requested_amount": status_totals.get("requested", 0),
        "paid_amount": status_totals.get("paid", 0),
        "ledger_balance": partner.ledger_balance,
        "payout_form": AffiliatePayoutRequestForm(),
        "base_url": base_url,
        **_partner_account_context(request.user),
    }
    return render(request, "store/partner/dashboard.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def partner_campaign_create_view(request):
    partner = _active_partner_for(request.user)
    if not partner:
        return redirect("store:partner_apply")
    form = AffiliateCampaignForm(request.POST or None, partner=partner)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "کمپین و لینک اختصاصی ایجاد شد.")
        return redirect("store:partner_dashboard")
    context = {"form": form, "partner": partner, "editing": False, **_partner_account_context(request.user)}
    return render(request, "store/partner/campaign_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def partner_campaign_edit_view(request, campaign_id):
    partner = _active_partner_for(request.user)
    if not partner:
        return redirect("store:partner_apply")
    campaign = get_object_or_404(AffiliateCampaign, pk=campaign_id, partner=partner)
    form = AffiliateCampaignForm(request.POST or None, instance=campaign, partner=partner)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "کمپین بروزرسانی شد.")
        return redirect("store:partner_dashboard")
    context = {"form": form, "partner": partner, "editing": True, "campaign": campaign, **_partner_account_context(request.user)}
    return render(request, "store/partner/campaign_form.html", context)


@login_required
@require_POST
def partner_payout_request_view(request):
    partner = _active_partner_for(request.user)
    if not partner:
        return redirect("store:partner_apply")
    form = AffiliatePayoutRequestForm(request.POST)
    if form.is_valid():
        try:
            payout = request_partner_payout(partner, note=form.cleaned_data.get("note", ""))
        except DjangoValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
        else:
            messages.success(request, f"درخواست تسویه {payout.payout_number} به مبلغ {payout.amount:,} تومان ثبت شد.")
    return redirect("store:partner_dashboard")
# END AFFILIATE PARTNER PROGRAM PHASE 7 VIEWS

# BEGIN MULTI SOURCE CATALOG PHASE 9 VIEWS
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .catalog_sync import public_catalog_queryset
from .models import CatalogCategoryRule, CatalogSourcePolicy


def external_print_catalog(request):
    queryset = public_catalog_queryset().filter(preview_image__isnull=False).exclude(preview_image="")
    query = (request.GET.get("q") or "").strip()
    segment = (request.GET.get("segment") or "").strip()
    source_kind = (request.GET.get("source") or "").strip()
    sort_mode = (request.GET.get("sort") or "downloads").strip()

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
            | Q(author_name__icontains=query)
            | Q(metrics__source_category__icontains=query)
        )
    if segment:
        queryset = queryset.filter(metrics__segment=segment)
    if source_kind:
        queryset = queryset.filter(metrics__source_kind=source_kind)

    ordering = {
        "downloads": ("-metrics__downloads_count", "metrics__popularity_rank"),
        "likes": ("-metrics__likes_count", "metrics__popularity_rank"),
        "views": ("-metrics__views_count", "metrics__popularity_rank"),
        "newest": ("-imported_at",),
    }.get(sort_mode, ("-metrics__downloads_count", "metrics__popularity_rank"))
    queryset = queryset.order_by(*ordering)

    paginator = Paginator(queryset, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "store/external_catalog.html",
        {
            "page_obj": page_obj,
            "query": query,
            "segment": segment,
            "source_kind": source_kind,
            "sort_mode": sort_mode,
            "segment_choices": CatalogCategoryRule.SEGMENT_CHOICES,
            "source_choices": CatalogSourcePolicy.SOURCE_KIND_CHOICES[:3],
        },
    )


def external_print_catalog_detail(request, pk):
    asset = get_object_or_404(
        public_catalog_queryset().filter(preview_image__isnull=False).exclude(preview_image=""),
        pk=pk,
    )
    return render(request, "store/external_catalog_detail.html", {"asset": asset})

# END MULTI SOURCE CATALOG PHASE 9 VIEWS

# BEGIN PHASE 10 PUBLIC CATALOG SEO AND SITEMAP VIEWS
import json as _phase10_json
from xml.sax.saxutils import escape as _phase10_xml_escape

from django.utils.safestring import mark_safe as _phase10_mark_safe


def _phase10_catalog_schema(request, asset):
    publication = getattr(asset.metrics, "publication", None)
    image_url = request.build_absolute_uri(asset.preview_image.url) if asset.preview_image else ""
    detail_url = request.build_absolute_uri(reverse("store:external_catalog_detail", args=[asset.pk]))
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CreativeWork",
                "@id": detail_url + "#model",
                "name": asset.title,
                "description": (publication.seo_description if publication else "") or asset.short_description or asset.description[:320],
                "url": detail_url,
                "image": image_url,
                "creator": {"@type": "Person", "name": asset.author_name or "طراح منبع"},
                "license": asset.license_url or asset.license_name,
                "isPartOf": {"@type": "CollectionPage", "name": "مدل‌های آماده چاپ سه‌بعدی", "url": request.build_absolute_uri(reverse("store:external_catalog"))},
                "potentialAction": {"@type": "OrderAction", "target": request.build_absolute_uri(f"/?ready_model={asset.pk}#order")},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "خانه", "item": request.build_absolute_uri("/")},
                    {"@type": "ListItem", "position": 2, "name": "مدل‌های آماده", "item": request.build_absolute_uri(reverse("store:external_catalog"))},
                    {"@type": "ListItem", "position": 3, "name": asset.title, "item": detail_url},
                ],
            },
        ],
    }
    return _phase10_mark_safe(_phase10_json.dumps(schema, ensure_ascii=False))


def external_print_catalog(request):
    queryset = public_catalog_queryset().filter(preview_image__isnull=False).exclude(preview_image="").select_related("metrics__publication")
    query = (request.GET.get("q") or "").strip()
    segment = (request.GET.get("segment") or "").strip()
    source_kind = (request.GET.get("source") or "").strip()
    sort_mode = (request.GET.get("sort") or "downloads").strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query)
            | Q(author_name__icontains=query) | Q(metrics__source_category__icontains=query)
        )
    if segment:
        queryset = queryset.filter(metrics__segment=segment)
    if source_kind:
        queryset = queryset.filter(metrics__source_kind=source_kind)
    ordering = {
        "downloads": ("-metrics__downloads_count", "metrics__popularity_rank"),
        "likes": ("-metrics__likes_count", "metrics__popularity_rank"),
        "views": ("-metrics__views_count", "metrics__popularity_rank"),
        "newest": ("-imported_at",),
    }.get(sort_mode, ("-metrics__downloads_count", "metrics__popularity_rank"))
    paginator = Paginator(queryset.order_by(*ordering), 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "store/external_catalog.html", {
        "page_obj": page_obj,
        "query": query,
        "segment": segment,
        "source_kind": source_kind,
        "sort_mode": sort_mode,
        "segment_choices": CatalogCategoryRule.SEGMENT_CHOICES,
        "source_choices": CatalogSourcePolicy.SOURCE_KIND_CHOICES[:3],
        "meta_title": "مدل‌های آماده برای سفارش چاپ سه‌بعدی | 3DprintHub",
        "meta_description": "جستجو و سفارش چاپ مدل‌های سه‌بعدی صنعتی، کاربردی و تزئینی با متریال و کیفیت دلخواه.",
    })


def external_print_catalog_detail(request, pk):
    asset = get_object_or_404(
        public_catalog_queryset().filter(preview_image__isnull=False).exclude(preview_image="").select_related("metrics__publication"),
        pk=pk,
    )
    publication = getattr(asset.metrics, "publication", None)
    return render(request, "store/external_catalog_detail.html", {
        "asset": asset,
        "publication": publication,
        "meta_title": (publication.seo_title if publication else "") or f"سفارش چاپ سه‌بعدی {asset.title}",
        "meta_description": (publication.seo_description if publication else "") or asset.short_description or asset.description[:320],
        "canonical_url": request.build_absolute_uri(reverse("store:external_catalog_detail", args=[asset.pk])),
        "catalog_schema": _phase10_catalog_schema(request, asset),
    })


def external_catalog_sitemap(request):
    rows = []
    for asset in public_catalog_queryset().filter(preview_image__isnull=False).exclude(preview_image="").select_related("metrics__publication"):
        loc = request.build_absolute_uri(reverse("store:external_catalog_detail", args=[asset.pk]))
        lastmod = asset.updated_at.date().isoformat() if asset.updated_at else asset.imported_at.date().isoformat()
        image = request.build_absolute_uri(asset.preview_image.url)
        title = getattr(getattr(asset.metrics, "publication", None), "image_alt_text", "") or asset.title
        rows.append(
            "<url><loc>{}</loc><lastmod>{}</lastmod><changefreq>weekly</changefreq>"
            "<image:image><image:loc>{}</image:loc><image:title>{}</image:title></image:image></url>".format(
                _phase10_xml_escape(loc), lastmod, _phase10_xml_escape(image), _phase10_xml_escape(title)
            )
        )
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + "".join(rows) + "</urlset>"
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")
# END PHASE 10 PUBLIC CATALOG SEO AND SITEMAP VIEWS

# BEGIN PHASE 14 IMAGE SITEMAP
from django.http import HttpResponse as _phase14_HttpResponse
from django.urls import reverse as _phase14_reverse
from django.utils.html import escape as _phase14_escape


def external_catalog_sitemap(request):
    from store.catalog_sync import public_catalog_queryset
    assets = (
        public_catalog_queryset()
        .select_related("metrics", "metrics__publication", "source")
        .prefetch_related("images")
        .order_by("pk")[:5000]
    )
    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for asset in assets:
        loc = request.build_absolute_uri(_phase14_reverse("store:external_catalog_detail", args=[asset.pk]))
        rows.append("<url>")
        rows.append(f"<loc>{_phase14_escape(loc)}</loc>")
        rows.append(f"<lastmod>{asset.updated_at.date().isoformat()}</lastmod>")
        if asset.catalog_image_url:
            image_url = asset.catalog_image_url
            if image_url.startswith("/"):
                image_url = request.build_absolute_uri(image_url)
            try:
                caption = asset.metrics.publication.image_alt_text or asset.title
            except Exception:
                caption = asset.title
            rows.append("<image:image>")
            rows.append(f"<image:loc>{_phase14_escape(image_url)}</image:loc>")
            rows.append(f"<image:title>{_phase14_escape(caption)}</image:title>")
            rows.append("</image:image>")
        for image in asset.images.all()[:6]:
            if not image.image:
                continue
            rows.append("<image:image>")
            rows.append(f"<image:loc>{_phase14_escape(request.build_absolute_uri(image.image.url))}</image:loc>")
            rows.append(f"<image:title>{_phase14_escape(image.alt_text or asset.title)}</image:title>")
            rows.append("</image:image>")
        rows.append("</url>")
    rows.append("</urlset>")
    return _phase14_HttpResponse("\n".join(rows), content_type="application/xml; charset=utf-8")
# END PHASE 14 IMAGE SITEMAP

# BEGIN PHASE 18 NINE ITEM CATALOG AND DEFAULT NEWEST
import random as _phase18_random


def external_print_catalog(request):
    queryset = (
        public_catalog_queryset()
        .filter(preview_image__isnull=False)
        .exclude(preview_image="")
        .select_related("source", "metrics", "metrics__publication")
    )
    query = (request.GET.get("q") or "").strip()
    segment = (request.GET.get("segment") or "").strip()
    source_kind = (request.GET.get("source") or "").strip()
    sort_was_selected = "sort" in request.GET
    sort_mode = (request.GET.get("sort") or "newest").strip()

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__icontains=query)
            | Q(author_name__icontains=query)
            | Q(metrics__source_category__icontains=query)
        )
    if segment:
        queryset = queryset.filter(metrics__segment=segment)
    if source_kind:
        queryset = queryset.filter(metrics__source_kind=source_kind)

    ordering = {
        "newest": ("-imported_at", "-id"),
        "views": ("-metrics__views_count", "metrics__popularity_rank", "-id"),
        "downloads": ("-metrics__downloads_count", "metrics__popularity_rank", "-id"),
        "likes": ("-metrics__likes_count", "metrics__popularity_rank", "-id"),
    }.get(sort_mode, ("-imported_at", "-id"))

    paginator = Paginator(queryset.order_by(*ordering), 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    default_randomized = not any((query, segment, source_kind, sort_was_selected))
    page_obj.object_list = list(page_obj.object_list)
    if default_randomized and len(page_obj.object_list) > 1:
        _phase18_random.SystemRandom().shuffle(page_obj.object_list)

    return render(request, "store/external_catalog.html", {
        "page_obj": page_obj,
        "query": query,
        "segment": segment,
        "source_kind": source_kind,
        "sort_mode": sort_mode,
        "default_randomized": default_randomized,
        "segment_choices": CatalogCategoryRule.SEGMENT_CHOICES,
        "source_choices": CatalogSourcePolicy.SOURCE_KIND_CHOICES[:3],
        "meta_title": "جدیدترین مدل‌های آماده چاپ سه‌بعدی | 3DprintHub",
        "meta_description": "مشاهده ۹ مدل آماده چاپ در هر صفحه با فیلتر منبع، گروه، بازدید، دانلود و جدیدترین مدل‌ها.",
    })
# END PHASE 18 NINE ITEM CATALOG AND DEFAULT NEWEST

# BEGIN PHASE 23 RESILIENT CATALOG AND CUSTOMER LINK INTELLIGENCE VIEWS
from datetime import timedelta as _phase23_timedelta

from django.utils import timezone as _phase23_timezone


def _phase23_link_rate_allowed(request):
    """Bound queued remote analyses per user/session to protect workers."""
    from .models import CustomerLinkAnalysis

    since = _phase23_timezone.now() - _phase23_timedelta(hours=1)
    if request.user.is_authenticated:
        count = CustomerLinkAnalysis.objects.filter(user=request.user, created_at__gte=since).count()
        return count < 30
    session_key = _phase23_session_key(request)
    count = CustomerLinkAnalysis.objects.filter(session_key=session_key, created_at__gte=since).count()
    return count < 10


import urllib.parse

from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required as _phase23_login_required
from django.core.paginator import Paginator as _Phase23Paginator
from django.db.models import Q as _Phase23Q
from django.http import Http404 as _Phase23Http404
from django.views.decorators.http import require_POST as _phase23_require_POST


def _phase23_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key or ""


def external_print_catalog(request):
    from .catalog_sync import public_catalog_queryset
    from .models import CatalogCategoryRule, PrintCatalogSource

    queryset = public_catalog_queryset().select_related(
        "source", "source__sync_policy", "metrics", "pricing_review", "pricing_review__material"
    )
    query = (request.GET.get("q") or "").strip()
    segment = (request.GET.get("segment") or "").strip()
    source_code = (request.GET.get("source") or "").strip()
    availability = (request.GET.get("availability") or "all").strip()
    sort_mode = (request.GET.get("sort") or "newest").strip()

    if query:
        queryset = queryset.filter(
            _Phase23Q(title__icontains=query)
            | _Phase23Q(short_description__icontains=query)
            | _Phase23Q(description__icontains=query)
            | _Phase23Q(tags__icontains=query)
            | _Phase23Q(author_name__icontains=query)
            | _Phase23Q(source__name__icontains=query)
            | _Phase23Q(metrics__source_category__icontains=query)
        )
    if segment:
        queryset = queryset.filter(metrics__segment=segment)
    if source_code:
        queryset = queryset.filter(source__code=source_code)
    printable_filter = (
        _Phase23Q(metrics__public_approved=True)
        & _Phase23Q(metrics__commercial_use_allowed=True)
        & _Phase23Q(metrics__license_review_status="allowed")
        & (
            ~_Phase23Q(private_download_url="")
            | ~_Phase23Q(file_format="")
            | ~_Phase23Q(metrics__file_links=[])
            | ~_Phase23Q(metrics__file_formats=[])
        )
    )
    if availability == "printable":
        queryset = queryset.filter(printable_filter)
    elif availability == "reference":
        queryset = queryset.exclude(printable_filter)

    ordering = {
        "newest": ("source_priority_order", "-imported_at", "-id"),
        "views": ("source_priority_order", "-metrics__views_count", "-imported_at"),
        "downloads": ("source_priority_order", "-metrics__downloads_count", "-imported_at"),
        "likes": ("source_priority_order", "-metrics__likes_count", "-imported_at"),
        "title": ("source_priority_order", "title", "-imported_at"),
    }.get(sort_mode, ("source_priority_order", "-imported_at", "-id"))

    page_obj = _Phase23Paginator(queryset.order_by(*ordering), 18).get_page(request.GET.get("page"))
    from .pricing_authority import calculate_verified_price
    for item in page_obj.object_list:
        try:
            review = item.pricing_review
        except Exception:
            review = None
        item.verified_price_data = calculate_verified_price(review) if review and review.is_complete else {}
    return render(request, "store/external_catalog.html", {
        "page_obj": page_obj,
        "query": query,
        "segment": segment,
        "source_code": source_code,
        "availability": availability,
        "sort_mode": sort_mode,
        "default_randomized": False,
        "segment_choices": CatalogCategoryRule.SEGMENT_CHOICES,
        "source_choices": PrintCatalogSource.objects.filter(is_active=True).filter(
            _Phase23Q(sync_policy__isnull=True)
            | _Phase23Q(
                sync_policy__is_active=True,
                sync_policy__public_reference_enabled=True,
            )
        ).order_by("name"),
        "meta_title": "کاتالوگ مرجع مدل‌ها و محصولات قابل سفارش چاپ | 3DprintHub",
        "meta_description": "مدل‌ها و محصولات دریافت‌شده از منابع معتبر، حتی در صورت نبود لینک مستقیم فایل، با نام، تصویر، مشخصات و لینک منبع نمایش داده می‌شوند.",
    })


def external_print_catalog_detail(request, pk):
    from .catalog_sync import public_catalog_queryset
    from .forms import CatalogRefreshRequestForm

    asset = get_object_or_404(
        public_catalog_queryset().select_related("pricing_review", "pricing_review__material").prefetch_related(
            "images", "print_profiles", "refresh_requests"
        ),
        pk=pk,
    )
    latest_refresh = asset.refresh_requests.order_by("-requested_at").first()
    try:
        pricing_review = asset.pricing_review
    except Exception:
        pricing_review = None
    from .pricing_authority import calculate_verified_price
    verified_price_data = calculate_verified_price(pricing_review) if pricing_review and pricing_review.is_complete else {}
    import json
    absolute_image = request.build_absolute_uri(asset.catalog_image_url) if asset.catalog_image_url else ""
    canonical_url = request.build_absolute_uri(reverse("store:external_catalog_detail", args=[asset.pk]))
    schema = {
        "@context": "https://schema.org",
        "@type": "Product" if verified_price_data else "CreativeWork",
        "name": asset.title,
        "description": asset.short_description or asset.description[:500],
        "url": canonical_url,
        "sameAs": asset.source_url,
        "creator": {"@type": "Person", "name": asset.author_name} if asset.author_name else None,
        "image": [absolute_image] if absolute_image else None,
        "mainEntityOfPage": canonical_url,
    }
    if verified_price_data:
        schema["offers"] = {
            "@type": "Offer",
            "url": canonical_url,
            "price": int(verified_price_data.get("total", 0)) * 10,
            "priceCurrency": "IRR",
            "availability": "https://schema.org/PreOrder",
            "seller": {"@type": "Organization", "name": "3DPrintHub"},
        }
    schema = {key: value for key, value in schema.items() if value not in (None, "", [])}
    product_schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    return render(request, "store/external_catalog_detail.html", {
        "asset": asset,
        "refresh_form": CatalogRefreshRequestForm(),
        "latest_refresh": latest_refresh,
        "pricing_review": pricing_review,
        "verified_price_data": verified_price_data,
        "product_schema_json": product_schema_json,
        "meta_title": f"{asset.title} | بررسی و سفارش چاپ سه‌بعدی",
        "meta_description": asset.short_description or asset.description[:300],
        "canonical_url": canonical_url,
    })


@_phase23_require_POST
def external_catalog_refresh_request(request, pk):
    from .catalog_sync import public_catalog_queryset
    from .forms import CatalogRefreshRequestForm
    from .link_intelligence import enqueue_catalog_refresh

    asset = get_object_or_404(public_catalog_queryset(), pk=pk)
    from .models import CatalogRefreshRequest

    since = _phase23_timezone.now() - _phase23_timedelta(hours=1)
    refresh_qs = CatalogRefreshRequest.objects.filter(requested_at__gte=since)
    if request.user.is_authenticated:
        refresh_qs = refresh_qs.filter(requested_by=request.user)
        limit = 20
    else:
        refresh_qs = refresh_qs.filter(session_key=_phase23_session_key(request))
        limit = 5
    if refresh_qs.count() >= limit:
        messages.error(request, "سقف درخواست بروزرسانی در یک ساعت تکمیل شده است.")
        return redirect("store:external_catalog_detail", pk=asset.pk)

    form = CatalogRefreshRequestForm(request.POST)
    if form.is_valid():
        refresh_request = enqueue_catalog_refresh(
            asset,
            user=request.user,
            session_key=_phase23_session_key(request),
            note=form.cleaned_data.get("customer_note", ""),
        )
        messages.success(request, f"درخواست بروزرسانی ثبت شد؛ وضعیت فعلی: {refresh_request.get_status_display()}.")
    else:
        messages.error(request, "توضیح درخواست بروزرسانی معتبر نیست.")
    return redirect("store:external_catalog_detail", pk=asset.pk)


@login_required
def external_link_analyzer(request):
    from .forms import ExternalLinkSubmitForm
    from .link_analysis_queue import enqueue_link_analysis
    from .models import CustomerLinkAnalysis

    initial_url = (request.GET.get("url") or "").strip()
    form = ExternalLinkSubmitForm(request.POST or None, initial={"source_url": initial_url})
    if request.method == "POST" and form.is_valid():
        if not _phase23_link_rate_allowed(request):
            messages.error(request, "سقف تحلیل لینک در یک ساعت تکمیل شده است؛ کمی بعد دوباره تلاش کنید.")
            return render(request, "store/external_link_analyzer.html", {"form": form}, status=429)
        analysis = CustomerLinkAnalysis.objects.create(
            user=request.user,
            session_key=_phase23_session_key(request),
            source_url=form.cleaned_data["source_url"],
            normalized_url=form.cleaned_data["source_url"],
            source_domain=urllib.parse.urlsplit(form.cleaned_data["source_url"]).hostname or "",
            status="pending",
        )
        enqueue_link_analysis(analysis)
        messages.success(request, "لینک وارد صف تحلیل شد. نتیجه در حساب شما ذخیره می‌شود و در صورت ناقص‌بودن می‌توانید درخواست قیمت کارشناسی ثبت کنید.")
        return redirect("store:external_link_analysis", token=analysis.public_token)
    return render(request, "store/external_link_analyzer.html", {"form": form})


@login_required
def external_link_analysis_detail(request, token):
    from .forms import ExternalLinkEstimateForm, ExternalLinkManualQuoteForm
    from .link_analysis_queue import link_analysis_job_payload
    from .link_intelligence import (
        analysis_owned_by,
        calculate_link_estimate,
        create_manual_quote_request_from_analysis,
        create_order_from_analysis,
    )
    from .models import CustomerLinkAnalysis, CustomerLinkAnalysisJob, LinkAnalysisManualReview

    analysis = get_object_or_404(
        CustomerLinkAnalysis.objects.select_related("user", "material", "order"),
        public_token=token,
    )
    if not analysis_owned_by(analysis, request):
        raise _Phase23Http404("تحلیل لینک پیدا نشد.")

    analysis_job = CustomerLinkAnalysisJob.objects.filter(analysis=analysis).first()
    queue_payload = link_analysis_job_payload(analysis_job, analysis)
    queue_active = bool(analysis_job and analysis_job.status in {"queued", "running", "retry"})
    manual_review = LinkAnalysisManualReview.objects.filter(
        analysis=analysis, status__in=["pending", "in_progress"]
    ).select_related("assigned_to").first()

    action = request.POST.get("action") if request.method == "POST" else ""
    pending_data = request.session.get("pending_link_order_data") or {}
    if pending_data.get("token") != str(analysis.public_token):
        pending_data = {}

    estimate_form = ExternalLinkEstimateForm(
        request.POST if action in {"recalculate", "create_order"} else None,
        analysis=analysis,
        user=request.user,
        require_customer=(action == "create_order"),
        initial={
            "full_name": pending_data.get("full_name", ""),
            "phone": pending_data.get("phone", ""),
        } if pending_data else None,
    )
    manual_quote_form = ExternalLinkManualQuoteForm(
        request.POST if action == "manual_quote" else None,
        analysis=analysis,
        user=request.user,
    )

    if request.method == "POST" and action in {"recalculate", "create_order"} and queue_active:
        messages.error(request, "تحلیل هنوز در صف یا در حال اجراست؛ برای اعلام سریع‌تر می‌توانید درخواست قیمت کارشناسی ثبت کنید.")
        return redirect("store:external_link_analysis", token=analysis.public_token)

    if action == "manual_quote" and manual_quote_form.is_valid():
        try:
            order = create_manual_quote_request_from_analysis(
                analysis,
                user=request.user,
                full_name=manual_quote_form.cleaned_data["full_name"],
                phone=manual_quote_form.cleaned_data["phone"],
                quantity=manual_quote_form.cleaned_data["quantity"],
                desired_material=manual_quote_form.cleaned_data.get("desired_material"),
                customer_note=manual_quote_form.cleaned_data.get("customer_note", ""),
            )
        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "درخواست قیمت کارشناسی ثبت شد. پس از بررسی، مبلغ کل و میزان بیعانه در پیش‌فاکتور نمایش داده می‌شود.")
            return redirect("website:quote_detail", token=order.public_token)

    if action in {"recalculate", "create_order"} and not analysis.has_authoritative_pricing_inputs:
        messages.error(request, "وزن یا زمان چاپ معتبر از منبع دریافت نشده است؛ درخواست استعلام بده تا اپراتور قیمت را قطعی کند.")
        return redirect("store:external_link_analysis", token=analysis.public_token)

    if action in {"recalculate", "create_order"} and estimate_form.is_valid():
        analysis.material = estimate_form.cleaned_data["material"]
        analysis.estimated_weight_grams = estimate_form.cleaned_data["estimated_weight_grams"]
        analysis.estimated_print_minutes = estimate_form.cleaned_data["estimated_print_minutes"]
        analysis.quantity = estimate_form.cleaned_data["quantity"]
        analysis.status = "ready"
        analysis.save(update_fields=[
            "material", "estimated_weight_grams", "estimated_print_minutes", "quantity", "status", "updated_at"
        ])
        calculate_link_estimate(analysis)
        if action == "create_order":
            try:
                order = create_order_from_analysis(
                    analysis,
                    user=request.user,
                    full_name=estimate_form.cleaned_data["full_name"],
                    phone=estimate_form.cleaned_data["phone"],
                )
            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, str(exc))
            else:
                request.session.pop("pending_link_order_data", None)
                messages.success(request, "پیش‌فاکتور اولیه ساخته شد؛ می‌توانید آن را تأیید و بیعانه یا مبلغ کامل را پرداخت کنید.")
                return redirect("website:quote_detail", token=order.public_token)
        else:
            messages.success(request, "برآورد قیمت با اطلاعات جدید محاسبه شد.")
            return redirect("store:external_link_analysis", token=analysis.public_token)

    return render(request, "store/external_link_analysis.html", {
        "analysis": analysis,
        "analysis_job": analysis_job,
        "queue_payload": queue_payload,
        "queue_active": queue_active,
        "manual_review": manual_review,
        "form": estimate_form,
        "manual_quote_form": manual_quote_form,
    })


@login_required
@_phase23_require_POST
def external_link_reanalyze(request, token):
    from .link_analysis_queue import enqueue_link_analysis
    from .link_intelligence import analysis_owned_by
    from .models import CustomerLinkAnalysis

    analysis = get_object_or_404(CustomerLinkAnalysis, public_token=token)
    if not analysis_owned_by(analysis, request):
        raise _Phase23Http404("تحلیل لینک پیدا نشد.")
    if analysis.order_id:
        messages.error(request, "برای این لینک قبلاً سفارش یا درخواست قیمت ساخته شده است.")
        return redirect("store:external_link_analysis", token=analysis.public_token)
    enqueue_link_analysis(analysis, force=True, priority=120)
    messages.success(request, "لینک برای تحلیل مجدد وارد صف شد.")
    return redirect("store:external_link_analysis", token=analysis.public_token)


@login_required
def external_link_analysis_status(request, token):
    from .link_analysis_queue import link_analysis_job_payload
    from .link_intelligence import analysis_owned_by
    from .models import CustomerLinkAnalysis, CustomerLinkAnalysisJob

    analysis = get_object_or_404(
        CustomerLinkAnalysis.objects.select_related("material", "order"),
        public_token=token,
    )
    if not analysis_owned_by(analysis, request):
        raise _Phase23Http404("تحلیل لینک پیدا نشد.")
    job = CustomerLinkAnalysisJob.objects.filter(analysis=analysis).first()
    payload = link_analysis_job_payload(job, analysis)
    payload.update({
        "analysis_title": analysis.title or "",
        "can_estimate": bool(analysis.can_estimate),
        "pricing_locked": bool(analysis.pricing_locked),
        "requires_operator_quote": not bool(analysis.has_authoritative_pricing_inputs),
        "estimated_price": int(analysis.estimated_price or 0),
        "result_url": reverse("store:external_link_analysis", args=[analysis.public_token]),
        "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
    })
    response = JsonResponse(payload)
    response["Cache-Control"] = "no-store, max-age=0"
    return response


@login_required
def customer_link_analyses_view(request):
    """نمایش امن تاریخچه تحلیل لینک‌های متعلق به مشتری واردشده."""
    from django.core.paginator import Paginator
    from website.views import _phase3_profile, _profile_completion
    from .models import CustomerLinkAnalysis

    status_filter = (request.GET.get("status") or "").strip()
    queryset = CustomerLinkAnalysis.objects.filter(user=request.user).select_related(
        "material", "order", "related_asset", "job"
    )
    if status_filter in dict(CustomerLinkAnalysis.STATUS_CHOICES):
        queryset = queryset.filter(status=status_filter)

    page_obj = Paginator(queryset.order_by("-created_at", "-id"), 12).get_page(request.GET.get("page"))
    profile = _phase3_profile(request.user)
    return render(request, "store/customer_link_analyses.html", {
        "profile": profile,
        "profile_completion": _profile_completion(profile),
        "page_obj": page_obj,
        "status_filter": status_filter,
        "status_choices": CustomerLinkAnalysis.STATUS_CHOICES,
        "analysis_stats": {
            "all": CustomerLinkAnalysis.objects.filter(user=request.user).count(),
            "ready": CustomerLinkAnalysis.objects.filter(user=request.user, status="ready").count(),
            "needs_input": CustomerLinkAnalysis.objects.filter(
                user=request.user, status__in=["needs_input", "partial"]
            ).count(),
            "converted": CustomerLinkAnalysis.objects.filter(user=request.user, status="converted").count(),
        },
    })

# END PHASE 23 RESILIENT CATALOG AND CUSTOMER LINK INTELLIGENCE VIEWS

# BEGIN PHASE 25 WORKER HEALTH ENDPOINT
import secrets as _phase25_secrets
from django.conf import settings as _phase25_settings
from django.views.decorators.http import require_GET as _phase25_require_GET


@_phase25_require_GET
def link_analysis_worker_health_view(request):
    from .link_analysis_operations import health_payload

    configured_token = str(getattr(_phase25_settings, "LINK_WORKER_HEALTH_TOKEN", "") or "").strip()
    supplied_token = str(request.headers.get("X-Health-Token") or request.GET.get("token") or "").strip()
    is_staff = bool(getattr(request, "user", None) and request.user.is_authenticated and request.user.is_staff)
    token_ok = bool(configured_token and supplied_token and _phase25_secrets.compare_digest(configured_token, supplied_token))
    if not (is_staff or token_ok):
        raise Http404
    payload, status_code = health_payload()
    return JsonResponse(payload, status=status_code)
# END PHASE 25 WORKER HEALTH ENDPOINT


# BEGIN PHASE 26 REALTIME AND MANUAL REVIEW VIEWS
@login_required
@require_POST
def external_link_manual_review_request(request, token):
    from .link_intelligence import analysis_owned_by
    from .manual_review import ensure_manual_review
    from .models import CustomerLinkAnalysis, CustomerLinkAnalysisJob

    analysis = get_object_or_404(CustomerLinkAnalysis, public_token=token)
    if not analysis_owned_by(analysis, request):
        raise Http404
    note = (request.POST.get("customer_note") or "").strip()[:5000]
    job = CustomerLinkAnalysisJob.objects.filter(analysis=analysis).first()
    review, created = ensure_manual_review(
        analysis,
        job=job,
        requested_by=request.user if request.user.is_authenticated else None,
        reason="customer_request",
        customer_note=note,
        priority=160 if analysis.status == "failed" else 120,
    )
    if created:
        messages.success(request, "درخواست بررسی دستی ثبت شد و در صف کارشناسان قرار گرفت.")
    else:
        messages.info(request, "این تحلیل از قبل در صف بررسی دستی قرار دارد.")
    return redirect("store:external_link_analysis", token=analysis.public_token)


@login_required
def link_analysis_operations_snapshot_view(request):
    if not request.user.is_staff:
        raise Http404
    from .realtime import operations_snapshot
    response = JsonResponse(operations_snapshot())
    response["Cache-Control"] = "no-store, max-age=0"
    return response
# END PHASE 26 REALTIME AND MANUAL REVIEW VIEWS
