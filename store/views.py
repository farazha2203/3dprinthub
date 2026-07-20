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
