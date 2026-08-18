from __future__ import annotations

from types import MethodType

from django import forms
from django.contrib import admin
from django.core.paginator import Paginator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.decorators.http import require_GET

from store.models import Category, ImportedPrintAsset, ImportedPrintAssetImage
from .models import HomepageHeroSlide
from .phase49_2b_hero_hotfix import hero_suggestions


TRANSITION_CHOICES = [
    ("cinematic_fade", "Cinematic Fade — محوشدن سینمایی"),
    ("wedding_dissolve", "Wedding Dissolve — دیزالو نرم"),
    ("cinematic_zoom", "Cinematic Zoom — زوم سینمایی"),
    ("ken_burns", "Ken Burns Fade — پن و زوم آرام"),
    ("soft_blur", "Soft Blur Dissolve — محوشدن با بلور"),
    ("cinematic_reveal", "Cinematic Reveal — آشکارسازی سینمایی"),
]


def _has_model_field(name: str) -> bool:
    try:
        HomepageHeroSlide._meta.get_field(name)
        return True
    except Exception:
        return False


def _install_model_fields() -> None:
    """Keep mature models.py stable while making the schema real via migration 0020.

    Django's runtime model receives the same fields declared in the migration, so
    ORM/admin/makemigrations all see the persistent schema without rewriting the
    very large legacy models module in this phase.
    """

    if not _has_model_field("selected_asset_image"):
        models.ForeignKey(
            ImportedPrintAssetImage,
            blank=True,
            null=True,
            on_delete=models.SET_NULL,
            related_name="+",
            verbose_name="تصویر انتخاب‌شده از آلبوم محصول",
            help_text="در Hero Studio با کلیک روی تصویر ذخیره می‌شود و از URL موقت مستقل است.",
        ).contribute_to_class(HomepageHeroSlide, "selected_asset_image")

    if not _has_model_field("transition_effect"):
        models.CharField(
            max_length=32,
            choices=TRANSITION_CHOICES,
            default="cinematic_fade",
            verbose_name="افکت تعویض اسلاید",
        ).contribute_to_class(HomepageHeroSlide, "transition_effect")

    if not _has_model_field("transition_duration_ms"):
        models.PositiveIntegerField(
            default=1400,
            validators=[MinValueValidator(300), MaxValueValidator(4000)],
            verbose_name="مدت افکت (میلی‌ثانیه)",
            help_text="بین 300 تا 4000 میلی‌ثانیه.",
        ).contribute_to_class(HomepageHeroSlide, "transition_duration_ms")

    if not _has_model_field("display_duration_ms"):
        models.PositiveIntegerField(
            default=7000,
            validators=[MinValueValidator(2000), MaxValueValidator(30000)],
            verbose_name="مدت نمایش اسلاید (میلی‌ثانیه)",
            help_text="بین 2000 تا 30000 میلی‌ثانیه.",
        ).contribute_to_class(HomepageHeroSlide, "display_duration_ms")


_install_model_fields()


def _file_url(field_file) -> str:
    if not field_file:
        return ""
    try:
        return str(field_file.url or "").strip()
    except Exception:
        return ""


def _selected_image_url(slide: HomepageHeroSlide) -> str:
    image_id = getattr(slide, "selected_asset_image_id", None)
    if not image_id:
        return ""
    try:
        row = slide.selected_asset_image
    except Exception:
        return ""
    return _file_url(getattr(row, "image", None)) or str(getattr(row, "remote_url", "") or "").strip()


def _effective_image_url(slide: HomepageHeroSlide) -> str:
    selected = _selected_image_url(slide)
    if selected:
        return selected
    explicit = str(getattr(slide, "image_url", "") or "").strip()
    if explicit:
        return explicit
    return str(hero_suggestions(getattr(slide, "asset", None)).get("preview_url") or "").strip()


HomepageHeroSlide.effective_image_url = property(_effective_image_url)


class HeroStudioForm(forms.ModelForm):
    selected_asset_image = forms.ModelChoiceField(
        queryset=ImportedPrintAssetImage.objects.all(),
        required=False,
        widget=forms.HiddenInput,
    )

    class Meta:
        model = HomepageHeroSlide
        fields = "__all__"
        widgets = {
            "transition_duration_ms": forms.NumberInput(attrs={"min": 300, "max": 4000, "step": 100}),
            "display_duration_ms": forms.NumberInput(attrs={"min": 2000, "max": 30000, "step": 500}),
        }

    def clean(self):
        cleaned = super().clean()
        asset = cleaned.get("asset")
        image = cleaned.get("selected_asset_image")
        if asset and image and image.asset_id != asset.pk:
            self.add_error("selected_asset_image", "تصویر انتخاب‌شده متعلق به همین محصول نیست.")
        return cleaned


def _product_browser_payload(asset: ImportedPrintAsset) -> dict:
    product = asset.product
    suggestion = hero_suggestions(asset)
    return {
        "asset_id": asset.pk,
        "product_id": product.pk,
        "title": str(product.title or asset.persian_title or asset.title),
        "title_en": str(getattr(product, "title_en", "") or ""),
        "sku": str(product.sku or ""),
        "category_id": product.category_id,
        "category": str(product.category.name if product.category_id else ""),
        "source": str(asset.source.name if asset.source_id else ""),
        "external_id": str(asset.external_id or getattr(product, "source_external_id", "") or ""),
        "image": str(suggestion.get("preview_url") or ""),
        "is_active": bool(product.is_active),
    }


def _browser_queryset():
    return (
        ImportedPrintAsset.objects
        .filter(product__isnull=False, product__is_active=True)
        .select_related("product", "product__category", "source")
        .order_by("-updated_at", "-id")
    )


def _install_admin_studio() -> None:
    model_admin = admin.site._registry.get(HomepageHeroSlide)
    if model_admin is None or getattr(model_admin, "_phase49_2c_installed", False):
        return

    model_admin.form = HeroStudioForm
    model_admin.change_form_template = "admin/website/homepageheroslide/change_form.html"
    model_admin.list_display = (
        "slide_preview",
        "effective_title_display",
        "group_display",
        "transition_effect",
        "timing_display",
        "sort_order",
        "is_active",
        "edit_slide_link",
    )
    model_admin.list_display_links = ("slide_preview", "effective_title_display")
    model_admin.list_editable = ("transition_effect", "sort_order", "is_active")
    model_admin.list_filter = ("is_active", "transition_effect", "object_fit", "focal_position", "updated_at")
    model_admin.readonly_fields = ("selected_image_preview", "created_at", "updated_at")
    model_admin.fieldsets = (
        ("۱. انتخاب تصویری محصول", {
            "fields": (),
            "description": "محصول را از آلبوم بالای فرم انتخاب کنید؛ اطلاعات و تصاویر بدون ذخیره اولیه بارگذاری می‌شوند.",
        }),
        ("انتخاب پیشرفته / اضطراری", {
            "fields": ("asset",),
            "classes": ("collapse",),
            "description": "در حالت عادی از آلبوم تصویری استفاده کنید. این فیلد فقط مسیر جایگزین برای جستجوی مستقیم است.",
        }),
        ("۲. تصویر Hero", {
            "fields": ("selected_asset_image", "image_url", "selected_image_preview", "image_alt_text", "object_fit", "focal_position"),
            "description": "انتخاب آلبومی در selected_asset_image ذخیره می‌شود. URL دستی فقط برای حالت‌های خاص باقی مانده است.",
        }),
        ("۳. نوشته و SEO روی عکس", {
            "fields": ("group_title", "title_override", "description", "button_text"),
        }),
        ("۴. افکت سینمایی و زمان‌بندی", {
            "fields": ("transition_effect", "transition_duration_ms", "display_duration_ms"),
            "description": "افکت، مدت Transition و زمان ماندن هر اسلاید مستقل از بقیه قابل تنظیم است.",
        }),
        ("۵. انتشار", {
            "fields": ("sort_order", "is_active", "created_at", "updated_at"),
        }),
    )

    class HeroStudioMedia:
        css = {"all": ("css/admin-phase49_2c-hero-studio.css",)}
        js = ("js/admin-phase49_2c-hero-studio.js",)

    model_admin.__class__.Media = HeroStudioMedia

    @admin.display(description="زمان")
    def timing_display(this, obj):
        return format_html(
            '<span title="نمایش / افکت">{}s / {}ms</span>',
            round((obj.display_duration_ms or 7000) / 1000, 1),
            obj.transition_duration_ms or 1400,
        )

    @admin.display(description="عملیات")
    def edit_slide_link(this, obj):
        url = reverse("admin:website_homepageheroslide_change", args=[obj.pk])
        return format_html('<a class="p49c-edit-link" href="{}"><i class="ri-edit-2-line"></i> ویرایش</a>', url)

    model_admin.__class__.timing_display = timing_display
    model_admin.__class__.edit_slide_link = edit_slide_link

    original_get_urls = model_admin.get_urls

    @require_GET
    def product_browser_view(request):
        if not model_admin.has_view_permission(request):
            return JsonResponse({"ok": False, "error": "دسترسی کافی ندارید."}, status=403)

        query = str(request.GET.get("q") or "").strip()
        category = str(request.GET.get("category") or "").strip()
        try:
            page_number = max(1, int(request.GET.get("page") or 1))
        except Exception:
            page_number = 1

        queryset = _browser_queryset()
        if query:
            queryset = queryset.filter(
                Q(product__title__icontains=query)
                | Q(product__title_en__icontains=query)
                | Q(product__sku__icontains=query)
                | Q(product__source_external_id__icontains=query)
                | Q(persian_title__icontains=query)
                | Q(title__icontains=query)
                | Q(external_id__icontains=query)
                | Q(source__name__icontains=query)
            )
        if category.isdigit():
            queryset = queryset.filter(product__category_id=int(category))

        paginator = Paginator(queryset, 24)
        page_obj = paginator.get_page(page_number)
        categories = list(
            Category.objects.filter(is_active=True, products__is_active=True, products__imported_source_asset__isnull=False)
            .distinct()
            .order_by("sort_order", "name")
            .values("id", "name")
        )
        return JsonResponse({
            "ok": True,
            "items": [_product_browser_payload(asset) for asset in page_obj.object_list],
            "page": page_obj.number,
            "pages": paginator.num_pages,
            "count": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "categories": categories,
        })

    @require_GET
    def asset_detail_view(request):
        if not model_admin.has_view_permission(request):
            return JsonResponse({"ok": False, "error": "دسترسی کافی ندارید."}, status=403)
        raw_id = str(request.GET.get("asset_id") or "").strip()
        if not raw_id.isdigit():
            return JsonResponse({"ok": False, "error": "asset_id نامعتبر است."}, status=400)

        asset = get_object_or_404(
            ImportedPrintAsset.objects.select_related("source", "product__category"),
            pk=int(raw_id),
            product__isnull=False,
        )
        suggestions = hero_suggestions(asset)
        rows = []
        seen = set()
        for image in asset.images.all().order_by("sort_order", "id")[:60]:
            url = _file_url(image.image) or str(image.remote_url or "").strip()
            if not url or url in seen:
                continue
            seen.add(url)
            rows.append({
                "id": image.pk,
                "url": url,
                "alt": str(image.alt_text or suggestions.get("image_alt_text") or ""),
                "is_primary": bool(image.is_primary),
                "is_selected": bool(image.is_selected),
                "width": int(image.source_width or 0),
                "height": int(image.source_height or 0),
                "kind": "asset_image",
            })

        preview = str(suggestions.get("preview_url") or "").strip()
        if preview and preview not in seen:
            rows.insert(0, {
                "id": None,
                "url": preview,
                "alt": str(suggestions.get("image_alt_text") or ""),
                "is_primary": True,
                "is_selected": True,
                "width": 0,
                "height": 0,
                "kind": "fallback",
            })

        return JsonResponse({
            "ok": True,
            "asset": _product_browser_payload(asset),
            "suggestions": suggestions,
            "images": rows,
        })

    def get_urls(this):
        custom = [
            path(
                "product-browser/",
                this.admin_site.admin_view(product_browser_view),
                name="website_homepageheroslide_product_browser",
            ),
            path(
                "asset-detail/",
                this.admin_site.admin_view(asset_detail_view),
                name="website_homepageheroslide_asset_detail",
            ),
        ]
        return custom + original_get_urls()

    model_admin.get_urls = MethodType(get_urls, model_admin)
    model_admin._phase49_2c_installed = True


_install_admin_studio()
