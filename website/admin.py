from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse



from .models import (
    SiteSetting,
    Material,
    IndustryRecommendation,
    PartRecommendation,
    PortfolioItem,
    CustomerProfile,
    Testimonial,
    Product,
    FAQ,
    Order,
    OrderImage,
    Quote,
    Payment,
    PaymentLedgerEntry,
    OrderReview,
)

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["avatar_preview", "first_name", "last_name", "phone", "national_code", "company_name", "created_at"]
    search_fields = ["first_name", "last_name", "father_name", "phone", "company_name", "national_code"]
    list_filter = ["gender", "created_at"]
    readonly_fields = ["avatar_preview", "created_at"]
    fieldsets = (
        ("حساب کاربری", {"fields": ("user", "avatar", "avatar_preview", "phone")}),
        ("مشخصات هویتی", {"fields": ("first_name", "last_name", "father_name", "birth_date", "gender", "national_code")}),
        ("اطلاعات تکمیلی", {"fields": ("landline", "occupation", "company_name", "address", "created_at")}),
    )

    @admin.display(description="تصویر")
    def avatar_preview(self, obj):
        if obj and obj.avatar:
            return format_html('<img src="{}" style="width:44px;height:44px;border-radius:50%;object-fit:cover">', obj.avatar.url)
        return "—"

@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "customer",
        "rating",
        "is_approved",
        "display_on_site",
        "created_at",
    ]

    list_filter = [
        "rating",
        "is_approved",
        "display_on_site",
        "created_at",
    ]

    search_fields = [
        "order__first_name",
        "order__last_name",
        "order__phone",
        "customer__username",
        "comment",
    ]

    actions = ["approve_reviews", "hide_from_site"]

    @admin.action(description="تأیید نظرات انتخاب‌شده")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="عدم نمایش در سایت")
    def hide_from_site(self, request, queryset):
        queryset.update(display_on_site=False)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ["brand_name", "phone", "whatsapp", "telegram", "email", "default_deposit_percent", "online_payment_enabled", "online_payment_provider", "primary_color", "secondary_color"]


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price_per_kg",
        "price_per_gram",
        "strength",
        "heat_resistance",
        "flexibility",
        "chemical_resistance",
        "printability",
        "is_active",
        "sort_order",
    ]
    list_editable = ["price_per_kg", "is_active", "sort_order"]
    search_fields = ["name", "main_usage", "sample_parts"]


@admin.register(IndustryRecommendation)
class IndustryRecommendationAdmin(admin.ModelAdmin):
    list_display = ["industry", "recommended_materials", "sort_order"]
    list_editable = ["sort_order"]
    search_fields = ["industry", "recommended_materials"]


@admin.register(PartRecommendation)
class PartRecommendationAdmin(admin.ModelAdmin):
    list_display = ["part_name", "best_material", "sort_order"]
    list_editable = ["sort_order"]
    search_fields = ["part_name", "best_material"]


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "material", "industry", "is_featured", "is_active", "created_at"]
    list_editable = ["is_featured", "is_active"]
    search_fields = ["title", "description", "material", "industry"]
    list_filter = ["category", "material", "industry", "is_active"]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["customer_name", "company_name", "rating", "is_active", "created_at"]
    list_editable = ["is_active"]
    search_fields = ["customer_name", "company_name", "text"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "base_price", "delivery_time", "materials", "colors", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["title", "description", "materials", "colors"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "is_active", "sort_order"]
    list_editable = ["is_active", "sort_order"]


class OrderImageInline(admin.TabularInline):
    model = OrderImage
    extra = 0
    fields = ("image_preview", "image")
    readonly_fields = ("image_preview",)

    @admin.display(description="پیش‌نمایش")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "-"
        return format_html('<a href="{}" target="_blank"><img src="{}" class="admin-order-thumb" alt="پیش‌نمایش"></a>', obj.image.url, obj.image.url)


class QuoteInline(admin.StackedInline):
    model = Quote
    extra = 0
    max_num = 1
    fields = [
        "material",
        "weight_grams",
        "print_time_minutes",
        "machine_hourly_rate",
        "labor_fee",
        "design_fee",
        "post_processing_fee",
        "shipping_fee",
        "discount",
        "customer_note",
        "admin_note",
        "status",
        "valid_until",
        "deposit_percent",
        "price_preview",
    ]
    readonly_fields = ["price_preview"]

    def price_preview(self, obj):
        if not obj or not obj.pk:
            return "بعد از ذخیره پیش‌فاکتور محاسبه می‌شود."

        html = f"""
        <div style="line-height:2">
            <strong>هزینه متریال:</strong> {obj.material_cost:,} تومان<br>
            <strong>هزینه دستگاه:</strong> {obj.machine_cost:,} تومان<br>
            <strong>جمع قبل از تخفیف:</strong> {obj.subtotal:,} تومان<br>
            <strong>مبلغ نهایی:</strong> <span style="color:#0a7;font-weight:bold">{obj.total_price:,} تومان</span>
        </div>
        """
        return mark_safe(html)

    price_preview.short_description = "محاسبه قیمت"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "phone",
        "customer",
        "service_type",
        "material",
        "quantity",
        "status",
        "created_at",
        "quote_link",
    ]
    list_editable = ["status"]
    search_fields = ["first_name", "last_name", "phone", "description"]
    list_filter = ["status", "service_type", "material", "customer", "created_at"]
    readonly_fields = ["public_token", "quote_link", "customer_summary", "technical_preview", "media_gallery"]
    inlines = [OrderImageInline, QuoteInline]

    @admin.display(description="خلاصه مشتری")
    def customer_summary(self, obj):
        if not obj or not obj.pk:
            return "-"
        customer = obj.customer
        account = "بدون حساب کاربری"
        if customer:
            account = customer.get_full_name() or customer.email or customer.get_username()
        return format_html(
            '<div class="admin-summary-grid"><div><small>حساب</small><strong>{}</strong></div><div><small>نام سفارش‌دهنده</small><strong>{} {}</strong></div><div><small>تماس</small><strong>{}</strong></div><div><small>وضعیت</small><strong>{}</strong></div></div>',
            account, obj.first_name, obj.last_name, obj.phone, obj.get_status_display(),
        )

    @admin.display(description="مشخصات فنی ثبت‌شده")
    def technical_preview(self, obj):
        if not obj or not obj.pk or not hasattr(obj, "intake_detail"):
            return "برای این سفارش اطلاعات فنی تکمیلی ثبت نشده است."
        d = obj.intake_detail
        contacts = [label for enabled, label in [
            (d.contact_with_gasoline, "بنزین"), (d.contact_with_oil, "روغن"),
            (d.contact_with_grease, "گریس"), (d.contact_with_water, "آب/رطوبت"),
            (d.contact_with_chemicals, "مواد شیمیایی"),
        ] if enabled]
        temperature = "ثبت نشده"
        if d.operating_temperature_min is not None or d.operating_temperature_max is not None:
            temperature = f"{d.operating_temperature_min or '—'} تا {d.operating_temperature_max or '—'} درجه"
        return format_html(
            '<div class="admin-technical-card"><div><small>نوع درخواست</small><strong>{}</strong></div><div><small>محیط</small><strong>{}</strong></div><div><small>تماس با مواد</small><strong>{}</strong></div><div><small>دمای کاری</small><strong>{}</strong></div><div class="wide"><small>ابعاد دقیق</small><p>{}</p></div><div class="wide"><small>خواص مورد انتظار</small><p>{}</p></div><div class="wide"><small>محل نصب و بارگذاری</small><p>{}</p></div></div>',
            d.get_request_mode_display(), d.get_usage_environment_display(), ", ".join(contacts) or "موردی اعلام نشده",
            temperature, d.exact_dimensions or "—", d.required_properties or "—",
            " | ".join(filter(None, [d.installation_location, d.load_conditions, d.dimensional_tolerance])) or "—",
        )

    @admin.display(description="پیش‌نمایش تصاویر و مدارک")
    def media_gallery(self, obj):
        if not obj or not obj.pk:
            return "-"
        cards = []
        for image in obj.images.all():
            cards.append(format_html('<a class="admin-media-card" href="{}" target="_blank"><img src="{}" alt="تصویر عمومی"><span>تصویر سفارش</span></a>', image.image.url, image.image.url))
        for image in obj.reference_photos.all():
            cards.append(format_html('<a class="admin-media-card" href="{}" target="_blank"><img src="{}" alt="{}"><span>{}</span></a>', image.image.url, image.image.url, image.get_view_type_display(), image.get_view_type_display()))
        for attachment in obj.attachments.all():
            download_url = reverse("website:order_attachment_download", args=[attachment.public_token])
            preview_url = reverse("website:order_attachment_preview", args=[attachment.public_token])
            if attachment.is_image:
                cards.append(format_html(
                    '<a class="admin-media-card" href="{}" target="_blank"><img src="{}" alt="{}"><span>{}</span><small>{}</small></a>',
                    preview_url, preview_url, attachment.original_name, attachment.original_name, attachment.size_label,
                ))
            elif attachment.is_pdf:
                cards.append(format_html(
                    '<a class="admin-media-card admin-media-card--file admin-media-card--pdf" href="{}" target="_blank"><i class="ri-file-pdf-2-line"></i><span>{}</span><small>PDF · {}</small></a>',
                    preview_url, attachment.original_name, attachment.size_label,
                ))
            else:
                cards.append(format_html(
                    '<a class="admin-media-card admin-media-card--file" href="{}"><i class="ri-file-download-line"></i><span>{}</span><small>{}</small></a>',
                    download_url, attachment.original_name, attachment.size_label,
                ))
        if not cards:
            return "هیچ تصویر یا مدرکی ثبت نشده است."
        return format_html('<div class="admin-media-gallery">{}</div>', mark_safe("".join(str(card) for card in cards)))

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("customer", "material").prefetch_related("images", "reference_photos", "attachments")

    def quote_link(self, obj):
        if not obj or not obj.public_token:
            return "-"

        url = obj.get_quote_url()
        return format_html(
            '<a href="{}" target="_blank">مشاهده لینک پیش‌فاکتور مشتری</a>',
            url
        )

    quote_link.short_description = "لینک پیش‌فاکتور"


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "material",
        "weight_grams",
        "print_time_minutes",
        "machine_hourly_rate",
        "status",
        "total_price_display",
        "created_at",
        "price_tolerance_percent",
    ]
    list_filter = ["status", "material", "created_at"]
    search_fields = ["order__first_name", "order__last_name", "order__phone"]
    readonly_fields = [
        "material_cost_display",
        "machine_cost_display",
        "subtotal_display",
        "total_price_display",
    ]

    fieldsets = (
        ("اطلاعات سفارش", {
            "fields": ("order", "material", "status", "valid_until", "deposit_percent")
        }),
        ("محاسبات قیمت", {
            "fields": (
                "weight_grams",
                "print_time_minutes",
                "machine_hourly_rate",
                "labor_fee",
                "design_fee",
                "post_processing_fee",
                "shipping_fee",
                "discount",
            )
        }),
        ("نتیجه محاسبه", {
            "fields": (
                "material_cost_display",
                "machine_cost_display",
                "subtotal_display",
                "total_price_display",
            )
        }),
        ("توضیحات", {
            "fields": ("customer_note", "admin_note")
        }),
    )

    def material_cost_display(self, obj):
        return f"{obj.material_cost:,} تومان"

    def machine_cost_display(self, obj):
        return f"{obj.machine_cost:,} تومان"

    def subtotal_display(self, obj):
        return f"{obj.subtotal:,} تومان"

    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    material_cost_display.short_description = "هزینه متریال"
    machine_cost_display.short_description = "هزینه دستگاه"
    subtotal_display.short_description = "جمع قبل از تخفیف"
    total_price_display.short_description = "مبلغ نهایی"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["quote", "payment_kind", "amount", "method", "provider", "status", "provider_status_code", "ref_id", "receipt_preview", "created_at", "paid_at"]
    list_filter = ["status", "method", "provider", "payment_kind", "created_at"]
    search_fields = ["quote__order__phone", "quote__order__first_name", "quote__order__last_name", "authority", "ref_id", "note"]
    readonly_fields = [
        "idempotency_key", "callback_token", "authority", "ref_id", "gateway_amount", "gateway_currency",
        "checkout_url", "provider_status_code", "provider_message", "request_payload", "raw_response",
        "callback_payload", "client_ip", "user_agent", "initiated_at", "callback_received_at", "verified_at",
        "failed_at", "retry_count", "receipt_preview", "created_at", "updated_at", "paid_at",
    ]
    actions = ["mark_selected_paid", "mark_selected_failed"]

    @admin.display(description="رسید")
    def receipt_preview(self, obj):
        if obj and obj.receipt_image:
            url = reverse("website:payment_receipt_admin", args=[obj.pk])
            return format_html('<a href="{}" target="_blank">مشاهده رسید خصوصی</a>', url)
        return "—"

    @admin.action(description="تأیید پرداخت‌های انتخاب‌شده")
    def mark_selected_paid(self, request, queryset):
        eligible = queryset.filter(method="bank_transfer").exclude(status="paid")
        for payment in eligible:
            payment.mark_paid(ref_id=payment.ref_id, provider_message="تأیید دستی واحد مالی")
        skipped = queryset.exclude(method="bank_transfer").count()
        if skipped:
            self.message_user(request, "پرداخت آنلاین فقط از طریق Verify درگاه تأیید می‌شود و دستی تأیید نشد.", level=messages.WARNING)

    @admin.action(description="رد پرداخت‌های انتخاب‌شده")
    def mark_selected_failed(self, request, queryset):
        queryset.exclude(status="paid").update(status="failed")


@admin.register(PaymentLedgerEntry)
class PaymentLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ["quote", "payment", "entry_type", "direction", "amount", "currency", "provider_ref", "created_at"]
    list_filter = ["entry_type", "direction", "currency", "created_at"]
    search_fields = ["quote__order__phone", "payment__authority", "payment__ref_id", "provider_ref", "event_key"]
    readonly_fields = [
        "quote", "payment", "entry_type", "direction", "amount", "currency", "event_key",
        "provider_ref", "description", "metadata", "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


from django.contrib import admin

# =========================
# =========================

# BEGIN PHASE 4 SEO ADMIN
from .models import SEOSettings
@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    fieldsets=(("تنظیمات اصلی",{"fields":("site_name","site_url","default_meta_title","default_meta_description","default_og_image")}), ("اسکیما سازمان و فروشنده",{"fields":("organization_name","organization_logo","organization_phone","organization_email","street_address","address_locality","address_region","organization_postal_code","country_code","same_as","merchant_return_days","shipping_rate","handling_min_days","handling_max_days","transit_min_days","transit_max_days")}), ("موتورهای جستجو",{"fields":("google_site_verification","bing_site_verification","allow_search_indexing","twitter_card","robots_extra")}),)
    list_display=("site_name","site_url","allow_search_indexing","updated_at")
    def has_add_permission(self,request): return not SEOSettings.objects.exists()
    def has_delete_permission(self,request,obj=None): return False
# END PHASE 4 SEO ADMIN

# BEGIN PHASE 5 LOCATION ADMIN
from .models import IranProvince, IranCounty, IranCity

@admin.register(IranProvince)
class IranProvinceAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("name", "code")

@admin.register(IranCounty)
class IranCountyAdmin(admin.ModelAdmin):
    list_display = ("name", "province", "code", "is_active")
    list_filter = ("province", "is_active")
    search_fields = ("name", "province__name", "code")

@admin.register(IranCity)
class IranCityAdmin(admin.ModelAdmin):
    list_display = ("name", "county", "province", "district_name", "is_active")
    list_filter = ("province", "county", "is_active")
    search_fields = ("name", "county__name", "province__name", "division_code")
# END PHASE 5 LOCATION ADMIN

# BEGIN MATERIAL INVENTORY PHASE 8 ADMIN
from django.utils.html import format_html as _phase8_format_html
from store.models import FilamentSpool


class Phase8FilamentSpoolInline(admin.TabularInline):
    model = FilamentSpool
    fk_name = "material"
    extra = 0
    fields = [
        "code", "brand", "color_name", "nominal_weight_grams", "remaining_weight_grams",
        "purchase_price", "cost_per_gram_snapshot", "sale_price_per_gram_snapshot", "status", "location",
    ]
    readonly_fields = ["code", "cost_per_gram_snapshot"]
    show_change_link = True


def _phase8_stock_grams(self, obj):
    return f"{obj.current_stock_grams:,.2f} گرم"
_phase8_stock_grams.short_description = "موجودی وزنی"


def _phase8_roll_count(self, obj):
    return obj.current_roll_count
_phase8_roll_count.short_description = "رول موجود"


def _phase8_reorder(self, obj):
    if not obj.track_filament_inventory:
        return "کنترل غیرفعال"
    if obj.needs_reorder:
        return mark_safe('<strong style="color:#b91c1c">نیاز به سفارش</strong>')
    return mark_safe('<strong style="color:#15803d">موجودی کافی</strong>')
_phase8_reorder.short_description = "وضعیت سفارش مجدد"


MaterialAdmin._phase8_stock_grams = _phase8_stock_grams
MaterialAdmin._phase8_roll_count = _phase8_roll_count
MaterialAdmin._phase8_reorder = _phase8_reorder
for _field in [
    "default_roll_weight_grams", "default_purchase_price_per_roll", "sale_price_per_gram",
    "track_filament_inventory", "_phase8_stock_grams", "_phase8_roll_count", "_phase8_reorder",
]:
    if _field not in MaterialAdmin.list_display:
        MaterialAdmin.list_display = list(MaterialAdmin.list_display) + [_field]
if Phase8FilamentSpoolInline not in getattr(MaterialAdmin, "inlines", []):
    MaterialAdmin.inlines = list(getattr(MaterialAdmin, "inlines", [])) + [Phase8FilamentSpoolInline]
# END MATERIAL INVENTORY PHASE 8 ADMIN

# BEGIN PHASE 10 ORDER INTAKE MODEL VAULT AND MATERIAL ADMIN
from django.contrib import admin, messages
from django.urls import reverse as _phase10_reverse
from django.utils.html import format_html as _phase10_format_html

from .models import CustomerReusableModel, Material, Order, OrderIntakeDetail, OrderReferencePhoto


class Phase10OrderIntakeInline(admin.StackedInline):
    model = OrderIntakeDetail
    extra = 0
    max_num = 1
    can_delete = False
    fieldsets = (
        ("نوع درخواست", {"fields": ("request_mode", "reusable_model", "ready_catalog_asset_id")}),
        ("شرایط کارکرد", {"fields": ("usage_environment", "contact_with_gasoline", "contact_with_oil", "contact_with_grease", "contact_with_water", "contact_with_chemicals", "chemical_details", "operating_temperature_min", "operating_temperature_max")}),
        ("نیاز فنی", {"fields": ("required_properties", "exact_dimensions", "installation_location", "load_conditions", "dimensional_tolerance")}),
        ("نمونه و توضیحات", {"fields": ("has_physical_sample", "sample_delivery_method", "extra_notes")}),
    )


class Phase10OrderReferencePhotoInline(admin.TabularInline):
    model = OrderReferencePhoto
    extra = 0
    fields = ("preview", "view_type", "image", "note", "created_at")
    readonly_fields = ("preview", "created_at")

    @admin.display(description="پیش‌نمایش")
    def preview(self, obj):
        if not obj or not obj.image:
            return "-"
        return _phase10_format_html('<a href="{}" target="_blank"><img src="{}" class="admin-order-thumb" alt="{}"></a>', obj.image.url, obj.image.url, obj.get_view_type_display())


_phase10_order_admin = admin.site._registry.get(Order)
if _phase10_order_admin is not None:
    _existing_inlines = list(getattr(_phase10_order_admin, "inlines", ()))
    for _inline in (Phase10OrderIntakeInline, Phase10OrderReferencePhotoInline):
        if _inline not in _existing_inlines:
            _existing_inlines.append(_inline)
    _phase10_order_admin.inlines = tuple(_existing_inlines)


@admin.register(CustomerReusableModel)
class CustomerReusableModelAdmin(admin.ModelAdmin):
    list_display = ("display_name", "customer", "internal_code", "file_available", "source_kind", "available_for_reorder", "last_ordered_at", "updated_at")
    list_filter = ("source_kind", "available_for_reorder", "file_format", "material_hint")
    search_fields = ("display_name", "internal_code", "customer__username", "customer__first_name", "customer__last_name", "admin_note")
    raw_id_fields = ("customer", "source_order", "material_hint")
    readonly_fields = ("public_token", "file_available", "staff_download_link", "created_at", "updated_at", "last_ordered_at")
    fieldsets = (
        ("مالک و شناسایی", {"fields": ("customer", "source_order", "source_kind", "display_name", "internal_code", "public_token")}),
        ("فایل کاملاً خصوصی", {"fields": ("model_file", "file_format", "version", "file_available", "staff_download_link"), "description": "فایل خارج از Media عمومی ذخیره می‌شود. مشتری فقط نام مدل و موجودبودن فایل را می‌بیند."}),
        ("اطلاعات سفارش مجدد", {"fields": ("material_hint", "default_color", "default_quantity", "last_known_weight_grams", "last_known_print_minutes", "available_for_reorder")}),
        ("توضیحات", {"fields": ("customer_note", "admin_note")}),
        ("زمان‌ها", {"fields": ("last_ordered_at", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="وضعیت فایل", boolean=True)
    def file_available(self, obj):
        return obj.file_is_available

    @admin.display(description="دریافت مخصوص ادمین")
    def staff_download_link(self, obj):
        if not obj or not obj.pk or not obj.model_file:
            return "-"
        url = _phase10_reverse("website:private_model_download", args=[obj.public_token])
        return _phase10_format_html('<a class="button" href="{}">دریافت فایل خصوصی</a>', url)


@admin.register(OrderIntakeDetail)
class OrderIntakeDetailAdmin(admin.ModelAdmin):
    list_display = ("order", "request_mode", "usage_environment", "reusable_model", "has_physical_sample", "updated_at")
    list_filter = ("request_mode", "usage_environment", "contact_with_gasoline", "contact_with_oil", "contact_with_grease", "has_physical_sample")
    search_fields = ("order__phone", "order__first_name", "order__last_name", "exact_dimensions", "required_properties")
    raw_id_fields = ("order", "reusable_model")


@admin.register(OrderReferencePhoto)
class OrderReferencePhotoAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "order", "view_type", "created_at")

    @admin.display(description="تصویر")
    def thumbnail(self, obj):
        if not obj.image:
            return "-"
        return _phase10_format_html('<a href="{}" target="_blank"><img src="{}" class="admin-order-thumb" alt="پیش‌نمایش"></a>', obj.image.url, obj.image.url)
    list_filter = ("view_type", "created_at")
    search_fields = ("order__phone", "order__first_name", "order__last_name", "note")
    raw_id_fields = ("order",)


@admin.action(description="بروزرسانی نرخ دلار و قیمت متریال‌های بازار")
def phase10_refresh_material_market_price(modeladmin, request, queryset):
    from store.market_pricing import refresh_fx_rates, refresh_material_market_prices
    try:
        refresh_fx_rates()
        snapshots, errors = refresh_material_market_prices(refresh_bambu=True)
        modeladmin.message_user(request, f"{len(snapshots)} قیمت متریال بروزرسانی شد؛ {len(errors)} خطا.")
        for error in errors[:5]:
            modeladmin.message_user(request, error, level=messages.WARNING)
    except Exception as exc:
        modeladmin.message_user(request, str(exc), level=messages.ERROR)


_phase10_material_admin = admin.site._registry.get(Material)
if _phase10_material_admin is not None:
    _actions = list(getattr(_phase10_material_admin, "actions", ()) or ())
    if phase10_refresh_material_market_price not in _actions:
        _actions.append(phase10_refresh_material_market_price)
    _phase10_material_admin.actions = tuple(_actions)

    _old_get_fieldsets = _phase10_material_admin.__class__.get_fieldsets
    if not getattr(_phase10_material_admin.__class__, "_phase10_fieldsets_patched", False):
        def _phase10_get_fieldsets(self, request, obj=None):
            fieldsets = list(_old_get_fieldsets(self, request, obj))
            names = {title for title, _data in fieldsets}
            if "قیمت زنده Bambu و دلار" not in names:
                fieldsets.append(("قیمت زنده Bambu و دلار", {
                    "fields": (
                        "market_pricing_enabled", "bambu_product_url", "bambu_variant_hint",
                        "bambu_reference_weight_grams", "market_import_cost_percent", "market_margin_percent",
                        "market_bambu_usd_price", "market_fx_daily_high_toman", "market_cost_price_per_gram",
                        "market_sale_price_per_gram", "market_price_updated_at",
                    ),
                    "description": "مشتری فقط قیمت فروش نهایی هر گرم را می‌بیند. قیمت دلاری، نرخ دلار و بهای محاسباتی فقط برای مدیر قابل مشاهده است.",
                }))
            return fieldsets
        _phase10_material_admin.__class__.get_fieldsets = _phase10_get_fieldsets
        _phase10_material_admin.__class__._phase10_fieldsets_patched = True
# END PHASE 10 ORDER INTAKE MODEL VAULT AND MATERIAL ADMIN

# BEGIN PHASE 14 PRESENTATION ADMIN
from .models import ClientReference, HomePresentationSetting, TeamMember


@admin.register(HomePresentationSetting)
class HomePresentationSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("کنترل سبک صفحه اول", {
            "fields": ("hero_badge", "hero_slider_count", "catalog_heading", "catalog_preview_count", "randomize_hero"),
            "description": "تعداد اسلاید Hero کاملاً قابل تنظیم است؛ برای نمونه ۳، ۱۰ یا ۱۵. بخش معرفی مدل‌ها به‌صورت شبکه ۳×۳ و مقدار پیشنهادی ۹ نمایش داده می‌شود.",
        }),
        ("بخش‌های اعتمادسازی", {
            "fields": ("show_team_section", "show_clients_section"),
            "description": "بخش متخصصان فقط اعضای فعال و بخش مشتریان فقط مجموعه‌های دارای مجوز نمایش را نشان می‌دهد.",
        }),
    )

    def has_add_permission(self, request):
        return not HomePresentationSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "years_experience", "is_featured", "is_active", "sort_order")
    list_filter = ("is_featured", "is_active")
    search_fields = ("name", "role", "short_bio", "expertise", "certifications")
    ordering = ("sort_order", "id")
    fieldsets = (
        ("مشخصات متخصص", {
            "fields": ("name", "role", "photo", "years_experience"),
            "description": "نام، نقش اصلی و تصویر حرفه‌ای عضو مجموعه را وارد کنید.",
        }),
        ("سابقه و توانمندی", {
            "fields": ("short_bio", "expertise", "certifications", "linkedin_url"),
            "description": "هر توانمندی را در یک خط جدا وارد کنید تا در کارت متخصص به‌صورت مرتب نمایش داده شود.",
        }),
        ("نمایش", {
            "fields": ("sort_order", "is_featured", "is_active"),
            "description": "فقط اعضای فعال و ویژه در صفحه اول نمایش داده می‌شوند.",
        }),
    )


@admin.register(ClientReference)
class ClientReferenceAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "display_permission_confirmed", "is_featured", "is_active", "sort_order")
    list_filter = ("display_permission_confirmed", "is_featured", "is_active", "industry")
    search_fields = ("name", "industry", "project_summary")
    ordering = ("sort_order", "id")
    fieldsets = (
        ("مشخصات مشتری", {
            "fields": ("name", "logo", "industry", "website_url"),
            "description": "فقط اطلاعاتی را وارد کنید که اجازه نمایش عمومی آن را دارید.",
        }),
        ("خلاصه همکاری", {
            "fields": ("project_summary",),
            "description": "نوع خدمت یا نتیجه همکاری را بدون اطلاعات محرمانه بنویسید.",
        }),
        ("مجوز و نمایش", {
            "fields": ("display_permission_confirmed", "sort_order", "is_featured", "is_active"),
            "description": "تا زمانی که مجوز نمایش تأیید نشده باشد، نام و لوگو در سایت عمومی نشان داده نمی‌شود.",
        }),
    )
# END PHASE 14 PRESENTATION ADMIN


# BEGIN PHASE 19 SUPPORT CHAT AND PRIVATE ORDER ATTACHMENT ADMIN
from pathlib import Path as _SupportPath

from django.contrib.admin.utils import unquote as _admin_unquote
from django.db import transaction as _support_transaction
from django.core.exceptions import PermissionDenied as _SupportPermissionDenied
from django.http import JsonResponse as _SupportJsonResponse
from django.shortcuts import get_object_or_404 as _support_get_object_or_404, render as _support_render
from django.urls import path as _support_path, reverse as _support_reverse
from django.utils import timezone as _support_timezone

from .models import OrderAttachment, SupportConversation, SupportMessage
from .support_chat import _validate_attachment as _support_validate_attachment, serialize_message as _serialize_support_message


class OrderAttachmentInline(admin.TabularInline):
    model = OrderAttachment
    extra = 0
    fields = ("file_summary", "note", "created_at")
    readonly_fields = ("file_summary", "created_at")

    @admin.display(description="فایل خصوصی")
    def file_summary(self, obj):
        if not obj or not obj.pk:
            return "پس از ذخیره سفارش، فایل از فرم مشتری قابل مشاهده است."
        download_url = _support_reverse("website:order_attachment_download", args=[obj.public_token])
        preview_url = _support_reverse("website:order_attachment_preview", args=[obj.public_token])
        preview = ""
        if obj.is_image:
            preview = format_html('<a href="{}" target="_blank"><img src="{}" class="admin-order-thumb" alt="{}"></a>', preview_url, preview_url, obj.original_name)
        elif obj.is_pdf:
            preview = format_html('<a class="button" href="{}" target="_blank"><i class="ri-file-pdf-2-line"></i> پیش‌نمایش PDF</a>', preview_url)
        return format_html(
            '<div class="admin-private-file">{}<strong>{}</strong><small>{}</small><a class="button" href="{}"><i class="ri-download-2-line"></i> دریافت امن</a></div>',
            preview, obj.original_name, obj.size_label, download_url,
        )


_order_admin_phase19 = admin.site._registry.get(Order)
if _order_admin_phase19 is not None:
    _order_phase19_inlines = list(getattr(_order_admin_phase19, "inlines", ()))
    if OrderAttachmentInline not in _order_phase19_inlines:
        _order_phase19_inlines.append(OrderAttachmentInline)
    _order_admin_phase19.inlines = tuple(_order_phase19_inlines)


@admin.register(OrderAttachment)
class OrderAttachmentAdmin(admin.ModelAdmin):
    list_display = ("original_name", "order", "size_label", "created_at", "secure_download")
    search_fields = ("original_name", "order__phone", "order__first_name", "order__last_name")
    list_filter = ("created_at", "content_type")
    raw_id_fields = ("order",)
    readonly_fields = ("public_token", "size_bytes", "created_at", "secure_download")

    @admin.display(description="دریافت")
    def secure_download(self, obj):
        if not obj or not obj.pk:
            return "-"
        download_url = _support_reverse("website:order_attachment_download", args=[obj.public_token])
        if obj.is_previewable:
            preview_url = _support_reverse("website:order_attachment_preview", args=[obj.public_token])
            return format_html('<a class="button" href="{}" target="_blank">پیش‌نمایش</a> <a class="button" href="{}">دریافت</a>', preview_url, download_url)
        return format_html('<a class="button" href="{}">دریافت فایل خصوصی</a>', download_url)


@admin.register(SupportConversation)
class SupportConversationAdmin(admin.ModelAdmin):
    list_display = ("customer_label", "subject", "status", "assigned_to", "order", "unread_badge", "last_message_at", "open_chat")
    list_filter = ("status", "assigned_to", "created_at", "last_message_at")
    search_fields = ("customer__username", "customer__email", "customer__first_name", "customer__last_name", "subject", "messages__body")
    raw_id_fields = ("customer", "assigned_to", "order")
    readonly_fields = ("public_token", "last_message_at", "created_at", "updated_at", "open_chat")
    ordering = ("-last_message_at", "-updated_at")

    @admin.display(description="مشتری")
    def customer_label(self, obj):
        return obj.customer.get_full_name() or obj.customer.email or obj.customer.get_username()

    @admin.display(description="خوانده‌نشده", ordering="last_message_at")
    def unread_badge(self, obj):
        count = obj.unread_for_staff
        return format_html('<span class="badge bg-{}">{}</span>', "danger" if count else "secondary", count)

    @admin.display(description="گفت‌وگو")
    def open_chat(self, obj):
        if not obj or not obj.pk:
            return "-"
        url = _support_reverse("admin:website_supportconversation_chat", args=[obj.pk])
        return format_html('<a class="button" href="{}"><i class="ri-chat-3-line"></i> باز کردن گفت‌وگو</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            _support_path("unread-count/", self.admin_site.admin_view(self.unread_count_view), name="website_supportconversation_unread_count"),
            _support_path("<path:object_id>/chat/", self.admin_site.admin_view(self.chat_view), name="website_supportconversation_chat"),
            _support_path("<path:object_id>/messages/", self.admin_site.admin_view(self.messages_view), name="website_supportconversation_messages"),
            _support_path("<path:object_id>/send/", self.admin_site.admin_view(self.send_view), name="website_supportconversation_send"),
        ]
        return custom + urls

    def _conversation(self, request, object_id, *, change=False):
        conversation = _support_get_object_or_404(
            SupportConversation.objects.select_related("customer", "assigned_to", "order"),
            pk=_admin_unquote(object_id),
        )
        allowed = self.has_change_permission(request, conversation) if change else self.has_view_permission(request, conversation)
        if not allowed:
            raise _SupportPermissionDenied
        return conversation

    def unread_count_view(self, request):
        if not self.has_view_permission(request):
            raise _SupportPermissionDenied
        unread = SupportMessage.objects.filter(sender__is_staff=False, read_by_staff_at__isnull=True).count()
        return _SupportJsonResponse({"unread": unread})

    def chat_view(self, request, object_id):
        conversation = self._conversation(request, object_id)
        conversation.messages.filter(sender__is_staff=False, read_by_staff_at__isnull=True).update(read_by_staff_at=_support_timezone.now())
        if conversation.assigned_to_id is None and self.has_change_permission(request, conversation):
            conversation.assigned_to = request.user
            conversation.save(update_fields=["assigned_to", "updated_at"])
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "original": conversation,
            "conversation": conversation,
            "title": f"گفت‌وگو با {conversation.customer.get_full_name() or conversation.customer.get_username()}",
            "messages_url": _support_reverse("admin:website_supportconversation_messages", args=[conversation.pk]),
            "send_url": _support_reverse("admin:website_supportconversation_send", args=[conversation.pk]),
            "change_url": _support_reverse("admin:website_supportconversation_change", args=[conversation.pk]),
        }
        return _support_render(request, "admin/website/supportconversation/chat.html", context)

    def messages_view(self, request, object_id):
        conversation = self._conversation(request, object_id)
        after = request.GET.get("after")
        queryset = conversation.messages.select_related("sender")
        if after and str(after).isdigit():
            queryset = queryset.filter(pk__gt=int(after))
        conversation.messages.filter(sender__is_staff=False, read_by_staff_at__isnull=True).update(read_by_staff_at=_support_timezone.now())
        return _SupportJsonResponse({"messages": [_serialize_support_message(message, request.user) for message in queryset[:250]], "status": conversation.status})

    def send_view(self, request, object_id):
        if request.method != "POST":
            return _SupportJsonResponse({"ok": False, "error": "روش درخواست نامعتبر است."}, status=405)
        conversation = self._conversation(request, object_id, change=True)
        body = (request.POST.get("body") or "").strip()
        attachment = request.FILES.get("attachment")
        if not body and not attachment:
            return _SupportJsonResponse({"ok": False, "error": "متن پیام یا یک پیوست را وارد کنید."}, status=400)
        error = _support_validate_attachment(attachment)
        if error:
            return _SupportJsonResponse({"ok": False, "error": error}, status=400)
        with _support_transaction.atomic():
            message = SupportMessage(conversation=conversation, sender=request.user, body=body)
            if attachment:
                message.attachment = attachment
                message.attachment_name = _SupportPath(attachment.name).name
                message.attachment_content_type = getattr(attachment, "content_type", "") or ""
                message.attachment_size = attachment.size or 0
            message.save()
        return _SupportJsonResponse({"ok": True, "message": _serialize_support_message(message, request.user)})


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "short_body", "attachment_name", "created_at")
    list_filter = ("sender__is_staff", "created_at")
    search_fields = ("body", "attachment_name", "conversation__customer__username", "conversation__customer__email")
    raw_id_fields = ("conversation", "sender")
    readonly_fields = ("public_token", "created_at", "read_by_customer_at", "read_by_staff_at")

    @admin.display(description="متن")
    def short_body(self, obj):
        return (obj.body[:80] + "…") if len(obj.body) > 80 else obj.body
# END PHASE 19 SUPPORT CHAT AND PRIVATE ORDER ATTACHMENT ADMIN
