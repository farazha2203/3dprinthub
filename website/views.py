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


def quote_detail_view(request, token):
    site_settings = SiteSetting.objects.first()
    order = get_object_or_404(Order, public_token=token)

    quote = getattr(order, "quote", None)

    context = {
        "settings": site_settings,
        "order": order,
        "quote": quote,
    }

    return render(request, "website/quote_detail.html", context)


def accept_quote_view(request, token):
    if request.method != "POST":
        return redirect("website:quote_detail", token=token)

    order = get_object_or_404(Order, public_token=token)
    quote = get_object_or_404(Quote, order=order)

    if quote.status not in ["sent", "draft"]:
        messages.error(request, "این پیش‌فاکتور در وضعیت قابل تأیید نیست.")
        return redirect("website:quote_detail", token=token)

    quote.status = "accepted"
    quote.save(update_fields=["status"])

    order.status = "accepted"
    order.save(update_fields=["status"])

    Payment.objects.create(
        quote=quote,
        amount=quote.total_price,
        method="gateway",
        status="pending",
    )

    messages.success(request, "پیش‌فاکتور تأیید شد. مرحله بعد اتصال به درگاه پرداخت است.")
    return redirect("website:quote_detail", token=token)


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