from django.contrib import admin
from django.utils.html import format_html



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
    list_display = ["brand_name", "phone", "whatsapp", "email", "primary_color", "secondary_color"]


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
        return format_html(html)

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
    readonly_fields = ["public_token", "quote_link"]
    inlines = [OrderImageInline, QuoteInline]

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
            "fields": ("order", "material", "status", "valid_until")
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
    list_display = ["quote", "amount", "method", "status", "ref_id", "created_at", "paid_at"]
    list_filter = ["status", "method", "created_at"]
    search_fields = ["quote__order__phone", "quote__order__first_name", "quote__order__last_name", "ref_id"]
    


from django.contrib import admin

# =========================
# =========================

# BEGIN PHASE 4 SEO ADMIN
from .models import SEOSettings
@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    fieldsets=(("تنظیمات اصلی",{"fields":("site_name","site_url","default_meta_title","default_meta_description","default_og_image")}), ("اسکیما سازمان",{"fields":("organization_name","organization_logo")}), ("موتورهای جستجو",{"fields":("google_site_verification","bing_site_verification","allow_search_indexing","twitter_card","robots_extra")}),)
    list_display=("site_name","site_url","allow_search_indexing","updated_at")
    def has_add_permission(self,request): return not SEOSettings.objects.exists()
    def has_delete_permission(self,request,obj=None): return False
# END PHASE 4 SEO ADMIN
