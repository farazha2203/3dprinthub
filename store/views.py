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
