from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .forms import (
    OrderForm,
    CustomerRegisterForm,
    CustomerLoginForm,
    CustomerProfileForm,
    OrderReviewForm,
    QuotePaymentForm,
    QuoteGatewayPaymentForm,
)

from .models import (
    SiteSetting,
    CustomerProfile,
    Material,
    IndustryRecommendation,
    PartRecommendation,
    PortfolioItem,
    Product,
    Testimonial,
    FAQ,
    Order,
    OrderReview,
    OrderImage,
    Quote,
    Payment,
)

def home_view(request):
    site_settings = SiteSetting.objects.first()

    if request.method == "POST":
        form = OrderForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.customer = request.user

            order.save()

            images = request.FILES.getlist("images")
            for image in images:
                OrderImage.objects.create(order=order, image=image)

            messages.success(
                request,
                "سفارش شما با موفقیت ثبت شد. بعد از بررسی فنی، پیش‌فاکتور برای شما ارسال می‌شود.",
            )
            return redirect("website:home")
        else:
            messages.error(request, "لطفاً اطلاعات فرم را به‌درستی تکمیل کنید.")
    else:
        form = OrderForm(user=request.user)

    context = {
        "settings": site_settings,
        "form": form,
        "materials": Material.objects.filter(is_active=True),
        "industry_recommendations": IndustryRecommendation.objects.all(),
        "part_recommendations": PartRecommendation.objects.all(),
        "portfolio_items": PortfolioItem.objects.filter(is_active=True)[:12],
        "testimonials": Testimonial.objects.filter(is_active=True),
        "products": Product.objects.filter(is_active=True),
        "faqs": FAQ.objects.filter(is_active=True),
        "order_reviews": OrderReview.objects.filter(
            is_approved=True,
            display_on_site=True,
        ).select_related("order", "customer")[:6],
    }

    return render(request, "website/index.html", context)


def _quote_owned_by(order, user):
    return bool(user and user.is_authenticated and (user.is_staff or order.customer_id == user.id))


@login_required
def quote_detail_view(request, token):
    site_settings = SiteSetting.objects.first()
    order = get_object_or_404(Order.objects.select_related("customer", "material"), public_token=token)
    if not _quote_owned_by(order, request.user):
        from django.http import Http404
        raise Http404("پیش‌فاکتور پیدا نشد.")

    quote = getattr(order, "quote", None)
    payment_form = QuotePaymentForm(quote=quote) if quote and quote.status == "accepted" and quote.total_price else None
    gateway_payment_form = QuoteGatewayPaymentForm(quote=quote) if quote and quote.status == "accepted" and quote.total_price else None
    from .payment_services import payment_gateway_status
    gateway_ready, gateway_reason = payment_gateway_status(site_settings)
    payments = quote.payments.order_by("-created_at") if quote else []
    active_gateway_payment = quote.payments.filter(
        method="gateway", status="pending"
    ).exclude(checkout_url="").order_by("-created_at").first() if quote else None

    context = {
        "settings": site_settings,
        "order": order,
        "quote": quote,
        "payment_form": payment_form,
        "gateway_payment_form": gateway_payment_form,
        "gateway_ready": gateway_ready,
        "gateway_reason": gateway_reason,
        "can_submit_payment": bool(payment_form and payment_form.payment_amounts),
        "can_submit_gateway_payment": bool(gateway_ready and gateway_payment_form and gateway_payment_form.payment_amounts),
        "active_gateway_payment": active_gateway_payment,
        "payments": payments,
    }
    return render(request, "website/quote_detail.html", context)


@login_required
def accept_quote_view(request, token):
    if request.method != "POST":
        return redirect("website:quote_detail", token=token)

    order = get_object_or_404(Order, public_token=token)
    if not _quote_owned_by(order, request.user):
        from django.http import Http404
        raise Http404("پیش‌فاکتور پیدا نشد.")
    quote = get_object_or_404(Quote, order=order)

    if quote.status != "sent" or not quote.total_price:
        messages.error(request, "این پیش‌فاکتور هنوز نهایی و قابل تأیید نیست.")
        return redirect("website:quote_detail", token=token)

    quote.status = "accepted"
    quote.save(update_fields=["status"])
    order.status = "accepted"
    order.save(update_fields=["status"])
    messages.success(request, "پیش‌فاکتور تأیید شد. اکنون می‌توانید بیعانه یا مانده مبلغ را واریز و رسید را ثبت کنید.")
    return redirect("website:quote_detail", token=token)


@login_required
def quote_payment_view(request, token):
    if request.method != "POST":
        return redirect("website:quote_detail", token=token)
    order = get_object_or_404(Order, public_token=token)
    if not _quote_owned_by(order, request.user):
        from django.http import Http404
        raise Http404("پیش‌فاکتور پیدا نشد.")
    quote = get_object_or_404(Quote, order=order, status="accepted")
    form = QuotePaymentForm(request.POST, request.FILES, quote=quote)
    if not form.is_valid():
        for error_list in form.errors.values():
            for error in error_list:
                messages.error(request, error)
        return redirect("website:quote_detail", token=token)

    kind = form.cleaned_data["payment_kind"]
    amount = int(form.cleaned_data["payment_amount"])
    if amount <= 0:
        messages.info(request, "این پیش‌فاکتور مانده قابل پرداخت ندارد.")
        return redirect("website:quote_detail", token=token)

    duplicate = quote.payments.filter(
        payment_kind=kind,
        amount=amount,
        status__in=["pending", "awaiting_review"],
    ).first()
    if duplicate:
        messages.info(request, "یک پرداخت مشابه در انتظار بررسی است.")
        return redirect("website:quote_detail", token=token)

    Payment.objects.create(
        quote=quote,
        amount=amount,
        payment_kind=kind,
        method="bank_transfer",
        status="awaiting_review",
        receipt_image=form.cleaned_data["receipt_image"],
        note=form.cleaned_data.get("note", ""),
    )
    messages.success(request, "رسید پرداخت ثبت شد و در انتظار تأیید واحد مالی است.")
    return redirect("website:quote_detail", token=token)


@login_required
def quote_gateway_start_view(request, token):
    if request.method != "POST":
        return redirect("website:quote_detail", token=token)
    order = get_object_or_404(Order, public_token=token)
    if not _quote_owned_by(order, request.user):
        from django.http import Http404
        raise Http404("پیش‌فاکتور پیدا نشد.")
    quote = get_object_or_404(Quote, order=order, status="accepted")
    form = QuoteGatewayPaymentForm(request.POST, quote=quote)
    if not form.is_valid():
        for error_list in form.errors.values():
            for error in error_list:
                messages.error(request, error)
        return redirect("website:quote_detail", token=token)

    from .payment_services import PaymentFlowError, start_quote_gateway_payment
    site_setting = SiteSetting.objects.first()
    try:
        payment, checkout_url, reused = start_quote_gateway_payment(
            quote=quote,
            payment_kind=form.cleaned_data["payment_kind"],
            request=request,
            site_setting=site_setting,
        )
    except PaymentFlowError as exc:
        messages.error(request, str(exc))
        return redirect("website:quote_detail", token=token)
    if reused:
        messages.info(request, "تلاش پرداخت قبلی هنوز معتبر است و ادامه همان پرداخت باز می‌شود.")
    return redirect(checkout_url)


def quote_gateway_callback_view(request, callback_token):
    from .payment_services import PaymentFlowError, process_gateway_callback
    from .payment_gateways.base import PaymentGatewayError
    callback_payload = {key: request.GET.get(key, "") for key in request.GET.keys()}
    site_setting = SiteSetting.objects.first()
    try:
        payment, outcome = process_gateway_callback(
            callback_token=callback_token,
            callback_payload=callback_payload,
            site_setting=site_setting,
        )
    except Payment.DoesNotExist:
        from django.http import Http404
        raise Http404("تراکنش پیدا نشد.")
    except (PaymentFlowError, PaymentGatewayError) as exc:
        messages.error(request, str(exc))
        return redirect("website:home")

    token = payment.quote.order.public_token
    if outcome == "paid":
        messages.success(request, f"پرداخت با موفقیت تأیید شد. کد پیگیری: {payment.ref_id or 'ثبت‌شده'}")
    elif outcome == "cancelled":
        messages.warning(request, "پرداخت تکمیل نشد یا در صفحه درگاه لغو شد. می‌توانید دوباره تلاش کنید.")
    elif outcome in {"retry", "verifying"}:
        messages.info(request, "تأیید پرداخت هنوز نهایی نشده است. چند لحظه دیگر همین صفحه را دوباره باز کنید.")
    else:
        messages.error(request, "تأیید پرداخت ناموفق بود. هیچ مبلغی در سایت به‌عنوان پرداخت‌شده ثبت نشد.")
    return redirect("website:quote_detail", token=token)


from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
import mimetypes


@staff_member_required
def admin_payment_receipt_view(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    if not payment.receipt_image:
        raise Http404("رسید پرداخت موجود نیست.")
    filename = payment.receipt_image.name.rsplit("/", 1)[-1]
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    response = FileResponse(payment.receipt_image.open("rb"), content_type=content_type)
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    response["Cache-Control"] = "private, no-store, max-age=0"
    return response


def robots_txt(request):
    content = """User-agent: *
Allow: /

Sitemap: https://3dprinthub.ir/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://3dprinthub.ir/</loc>
        <priority>1.0</priority>
        <changefreq>weekly</changefreq>
    </url>
</urlset>
"""
    return HttpResponse(content, content_type="application/xml")

def customer_register_view(request):
    site_settings = SiteSetting.objects.first()

    if request.user.is_authenticated:
        return redirect("website:customer_dashboard")

    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, "ثبت‌نام با موفقیت انجام شد. وارد پنل مشتری شدید.")
            return redirect("website:customer_dashboard")
        else:
            messages.error(request, "لطفاً اطلاعات ثبت‌نام را بررسی کنید.")
    else:
        form = CustomerRegisterForm()

    return render(request, "website/customer/register.html", {
        "settings": site_settings,
        "form": form,
    })


def customer_login_view(request):
    site_settings = SiteSetting.objects.first()

    if request.user.is_authenticated:
        return redirect("website:customer_dashboard")

    if request.method == "POST":
        form = CustomerLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(request, "با موفقیت وارد شدید.")
            return redirect("website:customer_dashboard")
        else:
            messages.error(request, "شماره تماس یا رمز عبور اشتباه است.")
    else:
        form = CustomerLoginForm()

    return render(request, "website/customer/login.html", {
        "settings": site_settings,
        "form": form,
    })


def customer_logout_view(request):
    logout(request)
    messages.success(request, "با موفقیت خارج شدید.")
    return redirect("website:home")


@login_required
def customer_dashboard_view(request):
    site_settings = SiteSetting.objects.first()

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }
    )

    orders = Order.objects.filter(customer=request.user).select_related("material").prefetch_related("images")

    stats = {
        "all": orders.count(),
        "new": orders.filter(status="new").count(),
        "quoted": orders.filter(status="quoted").count(),
        "accepted": orders.filter(status="accepted").count(),
        "paid": orders.filter(status="paid").count(),
        "done": orders.filter(status="done").count(),
    }

    return render(request, "website/customer/dashboard.html", {
        "settings": site_settings,
        "profile": profile,
        "orders": orders,
        "stats": stats,
    })


@login_required
def customer_profile_view(request):
    site_settings = SiteSetting.objects.first()

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }
    )

    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=profile)

        if form.is_valid():
            profile = form.save()

            request.user.first_name = profile.first_name
            request.user.last_name = profile.last_name
            request.user.username = profile.phone
            request.user.save(update_fields=["first_name", "last_name", "username"])

            messages.success(request, "مشخصات شما با موفقیت بروزرسانی شد.")
            return redirect("website:customer_profile")
        else:
            messages.error(request, "لطفاً اطلاعات وارد شده را بررسی کنید.")
    else:
        form = CustomerProfileForm(instance=profile)

    return render(request, "website/customer/profile.html", {
        "settings": site_settings,
        "profile": profile,
        "form": form,
    })


@login_required
def customer_order_detail_view(request, order_id):
    site_settings = SiteSetting.objects.first()

    order = get_object_or_404(
        Order.objects.select_related("material", "customer").prefetch_related("images"),
        id=order_id,
        customer=request.user,
    )

    quote = getattr(order, "quote", None)

    try:
        review = order.review
    except OrderReview.DoesNotExist:
        review = None

    review_form = None

    if order.status == "done" and review is None:
        review_form = OrderReviewForm()

    return render(request, "website/customer/order_detail.html", {
        "settings": site_settings,
        "order": order,
        "quote": quote,
        "review": review,
        "review_form": review_form,
    })

@login_required
def customer_order_review_create_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user,
    )

    if order.status != "done":
        messages.error(request, "ثبت نظر فقط بعد از تکمیل سفارش امکان‌پذیر است.")
        return redirect("website:customer_order_detail", order_id=order.id)

    if hasattr(order, "review"):
        messages.error(request, "برای این سفارش قبلاً نظر ثبت شده است.")
        return redirect("website:customer_order_detail", order_id=order.id)

    if request.method == "POST":
        form = OrderReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.customer = request.user
            review.is_approved = False
            review.display_on_site = True
            review.save()

            messages.success(request, "نظر شما ثبت شد و پس از تأیید ادمین در سایت نمایش داده می‌شود.")
            return redirect("website:customer_order_detail", order_id=order.id)
        else:
            messages.error(request, "لطفاً متن نظر و امتیاز را بررسی کنید.")

    return redirect("website:customer_order_detail", order_id=order.id)

# BEGIN CUSTOMER PORTAL PHASE 3 VIEWS
from django.db.models import Sum
from django.views.decorators.http import require_POST

from store.models import StoreAddress, StoreOrder
from .forms import StoreAddressForm


def _phase3_profile(user):
    profile, _ = CustomerProfile.objects.get_or_create(
        user=user,
        defaults={
            "phone": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )
    return profile


def _profile_completion(profile):
    user = profile.user
    checks = [
        profile.avatar,
        profile.first_name,
        profile.last_name,
        profile.father_name,
        profile.birth_date,
        profile.phone,
        profile.national_code,
        user.email,
        profile.user.store_addresses.exists(),
    ]
    completed = sum(bool(item) for item in checks)
    return round(completed * 100 / len(checks))


@login_required
def customer_dashboard_view(request):
    site_settings = SiteSetting.objects.first()
    profile = _phase3_profile(request.user)

    custom_orders = Order.objects.filter(customer=request.user).select_related("material").prefetch_related("images")
    store_orders = StoreOrder.objects.filter(user=request.user).prefetch_related("items", "payments")
    addresses = StoreAddress.objects.filter(user=request.user)

    custom_stats = {
        "all": custom_orders.count(),
        "active": custom_orders.exclude(status__in=["done", "cancelled"]).count(),
        "done": custom_orders.filter(status="done").count(),
    }
    store_stats = {
        "all": store_orders.count(),
        "awaiting_payment": store_orders.filter(payment_status__in=["pending", "awaiting_review"]).count(),
        "active": store_orders.filter(status__in=["paid", "processing", "ready", "shipped"]).count(),
        "delivered": store_orders.filter(status="delivered").count(),
    }
    paid_total = store_orders.filter(payment_status="paid").aggregate(total=Sum("total_amount"))["total"] or 0

    return render(request, "website/customer/dashboard.html", {
        "settings": site_settings,
        "profile": profile,
        "profile_completion": _profile_completion(profile),
        "custom_orders": custom_orders[:6],
        "store_orders": store_orders[:6],
        "addresses": addresses[:3],
        "custom_stats": custom_stats,
        "store_stats": store_stats,
        "paid_total": paid_total,
    })


@login_required
def customer_profile_view(request):
    site_settings = SiteSetting.objects.first()
    profile = _phase3_profile(request.user)
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "مشخصات حساب شما با موفقیت به‌روزرسانی شد.")
            return redirect("website:customer_profile")
        messages.error(request, "اطلاعات واردشده را بررسی کنید.")
    else:
        form = CustomerProfileForm(instance=profile)
    return render(request, "website/customer/profile.html", {
        "settings": site_settings,
        "profile": profile,
        "profile_completion": _profile_completion(profile),
        "form": form,
    })


@login_required
def customer_addresses_view(request):
    profile = _phase3_profile(request.user)
    return render(request, "website/customer/addresses.html", {
        "settings": SiteSetting.objects.first(),
        "profile": profile,
        "profile_completion": _profile_completion(profile),
        "addresses": StoreAddress.objects.filter(user=request.user),
    })


@login_required
def customer_address_create_view(request):
    profile = _phase3_profile(request.user)
    initial = {
        "full_name": f"{profile.first_name} {profile.last_name}".strip(),
        "phone": profile.phone,
        "is_default": not StoreAddress.objects.filter(user=request.user).exists(),
    }
    form = StoreAddressForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        if not StoreAddress.objects.filter(user=request.user).exists():
            address.is_default = True
        address.save()
        messages.success(request, "آدرس ارسال با موفقیت ثبت شد.")
        return redirect("website:customer_addresses")
    return render(request, "website/customer/address_form.html", {
        "settings": SiteSetting.objects.first(),
        "profile": profile,
        "profile_completion": _profile_completion(profile),
        "form": form,
        "page_title": "افزودن آدرس ارسال",
    })


@login_required
def customer_address_edit_view(request, address_id):
    profile = _phase3_profile(request.user)
    address = get_object_or_404(StoreAddress, pk=address_id, user=request.user)
    form = StoreAddressForm(request.POST or None, instance=address)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "آدرس ارسال ویرایش شد.")
        return redirect("website:customer_addresses")
    return render(request, "website/customer/address_form.html", {
        "settings": SiteSetting.objects.first(),
        "profile": profile,
        "profile_completion": _profile_completion(profile),
        "form": form,
        "address": address,
        "page_title": "ویرایش آدرس ارسال",
    })


@login_required
@require_POST
def customer_address_delete_view(request, address_id):
    address = get_object_or_404(StoreAddress, pk=address_id, user=request.user)
    was_default = address.is_default
    address.delete()
    if was_default:
        replacement = StoreAddress.objects.filter(user=request.user).first()
        if replacement:
            replacement.is_default = True
            replacement.save(update_fields=["is_default", "updated_at"])
    messages.success(request, "آدرس حذف شد.")
    return redirect("website:customer_addresses")


@login_required
@require_POST
def customer_address_default_view(request, address_id):
    address = get_object_or_404(StoreAddress, pk=address_id, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, "آدرس پیش‌فرض تغییر کرد.")
    return redirect("website:customer_addresses")
# END CUSTOMER PORTAL PHASE 3 VIEWS

# BEGIN PHASE 4 ROBOTS
from .views_phase4 import robots_txt_response, sitemap_xml_response
robots_txt = robots_txt_response
sitemap_xml = sitemap_xml_response
# END PHASE 4 ROBOTS

from django.urls import reverse as _phase10_reverse
from .models import CustomerReusableModel
# BEGIN PHASE 10 HOME ORDER AND MODEL VAULT VIEWS
import json as _phase10_json
from pathlib import Path as _Phase10Path

from django.contrib.admin.views.decorators import staff_member_required as _phase10_staff_required
from django.http import FileResponse as _Phase10FileResponse, Http404 as _Phase10Http404
from django.utils.safestring import mark_safe as _phase10_mark_safe


def _phase10_home_schema(request, assets):
    items = []
    for position, asset in enumerate(assets, start=1):
        items.append({
            "@type": "ListItem",
            "position": position,
            "url": request.build_absolute_uri(_phase10_reverse("store:external_catalog_detail", args=[asset.pk])),
            "name": asset.title,
        })
    return _phase10_mark_safe(_phase10_json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "مدل‌های آماده برای سفارش چاپ سه‌بعدی",
        "itemListElement": items,
    }, ensure_ascii=False))


def home_view(request):
    from store.catalog_automation import homepage_catalog_assets
    from store.catalog_sync import public_catalog_queryset
    from store.market_pricing import ensure_fx_fresh
    from website.order_intake import Phase10OrderForm

    site_settings = SiteSetting.objects.first()
    try:
        ensure_fx_fresh()
    except Exception:
        pass

    initial_reusable = None
    if request.user.is_authenticated and request.GET.get("reorder"):
        initial_reusable = CustomerReusableModel.objects.filter(
            customer=request.user,
            public_token=request.GET.get("reorder"),
            available_for_reorder=True,
        ).first()

    ready_asset_id = request.GET.get("ready_model")
    if ready_asset_id:
        try:
            ready_asset_id = int(ready_asset_id)
            if not public_catalog_queryset().filter(pk=ready_asset_id).exists():
                ready_asset_id = None
        except (TypeError, ValueError):
            ready_asset_id = None

    if request.method == "POST":
        form = Phase10OrderForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save_order(customer=request.user if request.user.is_authenticated else None)
            messages.success(
                request,
                "سفارش شما با اطلاعات فنی و تصاویر مرجع ثبت شد. پس از بررسی، پیش‌فاکتور با نرخ روز صادر می‌شود.",
            )
            return redirect("website:home")
        messages.error(request, "لطفاً اطلاعات فنی و تصاویر الزامی سفارش را بررسی کنید.")
    else:
        form = Phase10OrderForm(
            user=request.user,
            initial_reusable=initial_reusable,
            ready_catalog_asset_id=ready_asset_id,
        )

    slider_assets = list(homepage_catalog_assets(slider=True))
    grid_assets = list(homepage_catalog_assets(slider=False))
    context = {
        "settings": site_settings,
        "form": form,
        "materials": Material.objects.filter(is_active=True),
        "industry_recommendations": IndustryRecommendation.objects.all(),
        "part_recommendations": PartRecommendation.objects.all(),
        "portfolio_items": PortfolioItem.objects.filter(is_active=True)[:12],
        "testimonials": Testimonial.objects.filter(is_active=True),
        "products": Product.objects.filter(is_active=True),
        "faqs": FAQ.objects.filter(is_active=True),
        "order_reviews": OrderReview.objects.filter(is_approved=True, display_on_site=True).select_related("order", "customer")[:6],
        "ready_model_slider": slider_assets,
        "ready_model_grid": grid_assets,
        "ready_models_schema": _phase10_home_schema(request, grid_assets[:12]),
        "initial_reusable_model": initial_reusable,
        "selected_ready_asset_id": ready_asset_id,
    }
    return render(request, "website/index.html", context)


@login_required
def customer_reusable_models_view(request):
    models_qs = CustomerReusableModel.objects.filter(customer=request.user).select_related("source_order", "material_hint")
    return render(request, "website/customer/reusable_models.html", {
        "settings": SiteSetting.objects.first(),
        "saved_models": models_qs,
    })


@login_required
def customer_reorder_model_view(request, token):
    model = get_object_or_404(
        CustomerReusableModel,
        customer=request.user,
        public_token=token,
        available_for_reorder=True,
    )
    return redirect(f"/?reorder={model.public_token}#order")


@_phase10_staff_required
def private_model_download_view(request, token):
    model = get_object_or_404(CustomerReusableModel, public_token=token)
    if not model.model_file:
        raise _Phase10Http404("فایل مدل موجود نیست.")
    path = _Phase10Path(model.model_file.path)
    if not path.exists() or not path.is_file():
        raise _Phase10Http404("فایل مدل روی سرور پیدا نشد.")
    suffix = path.suffix or (f".{model.file_format.lower()}" if model.file_format else "")
    filename = f"{model.internal_code}-{model.display_name}{suffix}".replace("/", "-")
    return _Phase10FileResponse(path.open("rb"), as_attachment=True, filename=filename)
# END PHASE 10 HOME ORDER AND MODEL VAULT VIEWS

# BEGIN PHASE 14 AUTHENTICATED ORDERING AND PRESENTATION VIEWS
import json as _phase14_json
from urllib.parse import urlencode as _phase14_urlencode

from django.contrib import messages as _phase14_messages
from django.contrib.auth import login as _phase14_login
from django.shortcuts import redirect as _phase14_redirect, render as _phase14_render
from django.urls import reverse as _phase14_reverse
from django.utils.http import url_has_allowed_host_and_scheme as _phase14_url_allowed
from django.utils.safestring import mark_safe as _phase14_mark_safe


def _phase14_safe_next(request, value, fallback="website:customer_dashboard"):
    if value and _phase14_url_allowed(value, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return value
    return _phase14_reverse(fallback)


def _phase14_presentation_schema(request, hero_assets, team_members):
    item_list = []
    for position, asset in enumerate(hero_assets, start=1):
        item_list.append({
            "@type": "ListItem",
            "position": position,
            "name": asset.title,
            "url": request.build_absolute_uri(_phase14_reverse("store:external_catalog_detail", args=[asset.pk])),
        })
    employees = []
    for member in team_members:
        employees.append({
            "@type": "Person",
            "name": member.name,
            "jobTitle": member.role,
            "description": member.short_bio,
        })
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "ItemList",
                "name": "مدل‌های آماده چاپ سه‌بعدی",
                "itemListElement": item_list,
            },
            {
                "@type": "ProfessionalService",
                "name": "3DprintHub.ir",
                "url": request.build_absolute_uri("/"),
                "employee": employees,
                "knowsAbout": [
                    "چاپ سه‌بعدی صنعتی",
                    "مهندسی معکوس",
                    "طراحی CAD",
                    "انتخاب متریال مهندسی",
                    "ساخت قطعات سفارشی",
                ],
            },
        ],
    }
    return _phase14_mark_safe(_phase14_json.dumps(payload, ensure_ascii=False))


def home_view(request):
    from store.catalog_sync import public_catalog_queryset
    from store.market_pricing import ensure_fx_fresh
    from store.presentation import categorized_presentation, presentation_assets
    from website.models import (
        ClientReference,
        CustomerReusableModel,
        FAQ,
        HomePresentationSetting,
        IndustryRecommendation,
        Material,
        OrderReview,
        PartRecommendation,
        PortfolioItem,
        Product,
        SiteSetting,
        TeamMember,
        Testimonial,
    )
    from website.order_intake import Phase10OrderForm

    site_settings = SiteSetting.objects.first()
    presentation_setting = HomePresentationSetting.load()
    try:
        ensure_fx_fresh()
    except Exception:
        pass

    has_reusable_models = False
    initial_reusable = None
    if request.user.is_authenticated:
        reusable_qs = CustomerReusableModel.objects.filter(
            customer=request.user,
            available_for_reorder=True,
        )
        has_reusable_models = reusable_qs.exists()
        if request.GET.get("reorder"):
            initial_reusable = reusable_qs.filter(public_token=request.GET.get("reorder")).first()

    ready_asset_id = request.GET.get("ready_model")
    if ready_asset_id:
        try:
            ready_asset_id = int(ready_asset_id)
            if not public_catalog_queryset().filter(pk=ready_asset_id).exists():
                ready_asset_id = None
        except (TypeError, ValueError):
            ready_asset_id = None

    if request.method == "POST" and not request.user.is_authenticated:
        _phase14_messages.warning(request, "برای ثبت سفارش و نگهداری سوابق، ابتدا وارد حساب مشتری شوید.")
        next_target = ("/?" + _phase14_urlencode({"ready_model": ready_asset_id}) + "#order") if ready_asset_id else "/#order"
        return _phase14_redirect(f"{_phase14_reverse('website:customer_login')}?{_phase14_urlencode({'next': next_target})}")

    if request.user.is_authenticated:
        if request.method == "POST":
            form = Phase10OrderForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                form.save_order(customer=request.user)
                _phase14_messages.success(request, "سفارش ثبت شد و در پنل مشتری قابل پیگیری است.")
                return _phase14_redirect("website:customer_dashboard")
            _phase14_messages.error(request, "اطلاعات فنی و تصاویر الزامی سفارش را بررسی کنید.")
        else:
            form = Phase10OrderForm(
                user=request.user,
                initial_reusable=initial_reusable,
                ready_catalog_asset_id=ready_asset_id,
            )
    else:
        form = None

    hero_assets = presentation_assets(
        limit=presentation_setting.hero_slider_count,
        randomize=False,
        newest_first=True,
    )
    catalog_groups, catalog_preview = categorized_presentation(
        limit=presentation_setting.catalog_preview_count,
    )
    team_members = list(TeamMember.objects.filter(is_active=True, is_featured=True)[:8])
    client_references = list(ClientReference.objects.filter(
        is_active=True,
        is_featured=True,
        display_permission_confirmed=True,
    )[:16])

    context = {
        "settings": site_settings,
        "presentation_setting": presentation_setting,
        "form": form,
        "materials": Material.objects.filter(is_active=True),
        "industry_recommendations": IndustryRecommendation.objects.all(),
        "part_recommendations": PartRecommendation.objects.all(),
        "portfolio_items": PortfolioItem.objects.filter(is_active=True)[:12],
        "testimonials": Testimonial.objects.filter(is_active=True),
        "products": Product.objects.filter(is_active=True),
        "faqs": FAQ.objects.filter(is_active=True),
        "order_reviews": OrderReview.objects.filter(is_approved=True, display_on_site=True).select_related("order", "customer")[:6],
        "hero_model_slider": hero_assets,
        "ready_model_slider": hero_assets,
        "ready_model_grid": catalog_preview,
        "catalog_groups": catalog_groups,
        "catalog_preview": catalog_preview,
        "team_members": team_members,
        "client_references": client_references,
        "has_reusable_models": has_reusable_models,
        "initial_reusable_model": initial_reusable,
        "selected_ready_asset_id": ready_asset_id,
        "presentation_schema": _phase14_presentation_schema(request, hero_assets, team_members),
        "login_next_url": f"{_phase14_reverse('website:customer_login')}?{_phase14_urlencode({'next': request.get_full_path() or '/#order'})}",
    }
    return _phase14_render(request, "website/index.html", context)


def customer_login_view(request):
    from website.forms import CustomerLoginForm
    from website.models import SiteSetting

    requested_next = request.POST.get("next") or request.GET.get("next") or ""
    if request.user.is_authenticated:
        return _phase14_redirect(_phase14_safe_next(request, requested_next))
    if request.method == "POST":
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            _phase14_login(request, form.get_user())
            _phase14_messages.success(request, "با موفقیت وارد شدید.")
            return _phase14_redirect(_phase14_safe_next(request, requested_next))
        _phase14_messages.error(request, "شماره تماس یا رمز عبور اشتباه است.")
    else:
        form = CustomerLoginForm()
    return _phase14_render(request, "website/customer/login.html", {
        "settings": SiteSetting.objects.first(),
        "form": form,
        "next_url": requested_next,
    })


def customer_register_view(request):
    from website.forms import CustomerRegisterForm
    from website.models import SiteSetting

    requested_next = request.POST.get("next") or request.GET.get("next") or ""
    if request.user.is_authenticated:
        return _phase14_redirect(_phase14_safe_next(request, requested_next))
    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            _phase14_login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            _phase14_messages.success(request, "حساب مشتری ساخته شد و وارد شدید.")
            return _phase14_redirect(_phase14_safe_next(request, requested_next))
        _phase14_messages.error(request, "اطلاعات ثبت‌نام را بررسی کنید.")
    else:
        form = CustomerRegisterForm()
    return _phase14_render(request, "website/customer/register.html", {
        "settings": SiteSetting.objects.first(),
        "form": form,
        "next_url": requested_next,
    })
# END PHASE 14 AUTHENTICATED ORDERING AND PRESENTATION VIEWS

@login_required
def customer_avatar_view(request):
    from django.http import FileResponse, Http404
    import mimetypes

    profile = _phase3_profile(request.user)
    if not profile.avatar:
        raise Http404("avatar not found")
    try:
        handle = profile.avatar.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("avatar file not found")
    content_type = mimetypes.guess_type(profile.avatar.name)[0] or "application/octet-stream"
    response = FileResponse(handle, content_type=content_type)
    response["Cache-Control"] = "private, no-store, max-age=0"
    response["X-Content-Type-Options"] = "nosniff"
    return response
