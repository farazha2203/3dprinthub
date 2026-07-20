from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F, Min, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductCommentForm, ProductRequestForm
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
        .prefetch_related("images", "compatibilities", "variants__material", "variants__quality")
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

    variants = product.variants.filter(is_active=True).select_related("material", "quality").order_by(
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
                tax_amount = _money_round(Decimal(tax_base) * Decimal(pricing.tax_percent) / Decimal("100"))
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
    form = ProductReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.product = product
        obj.user = request.user
        obj.is_verified_purchase = True
        obj.is_approved = False
        obj.save()
        messages.success(request, "نظر شما ثبت شد و پس از تأیید نمایش داده می‌شود.")
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
                tax_amount = _money_round(Decimal(tax_base) * Decimal(pricing.tax_percent) / Decimal("100"))
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
                tax_amount = _money_round(Decimal(taxable_amount) * Decimal(pricing.tax_percent) / Decimal("100"))
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
    next_url = request.POST.get("next") or notification.url or reverse("store:notifications")
    return redirect(next_url)


@login_required
@require_POST
def notifications_read_all_view(request):
    CustomerNotification.objects.filter(user=request.user, read_at__isnull=True).update(read_at=timezone.now())
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
