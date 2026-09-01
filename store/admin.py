from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Category,
    PricingSetting,
    PrintQuality,
    Product,
    ProductComment,
    ProductCompatibility,
    ProductImage,
    ProductLike,
    ProductRequest,
    ProductRequestImage,
    ProductReview,
    ProductVariant,
    ServicePage,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductCompatibilityInline(admin.TabularInline):
    model = ProductCompatibility
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = [
        "code",
        "material",
        "quality",
        "material_weight_grams",
        "final_weight_grams",
        "print_time_minutes",
        "hourly_rate_override",
        "labor_percent_override",
        "post_processing_fee",
        "fixed_fee",
        "cached_unit_price",
        "stock_status",
        "is_active",
    ]
    readonly_fields = ["cached_unit_price"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "section", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["section", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PrintQuality)
class PrintQualityAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "layer_height_mm", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]


@admin.register(PricingSetting)
class PricingSettingAdmin(admin.ModelAdmin):
    list_display = [
        "default_hourly_rate",
        "minimum_billable_minutes",
        "billing_increment_minutes",
        "default_labor_percent",
        "minimum_order_amount",
        "packaging_fee",
        "tax_percent",
        "updated_at",
    ]
    readonly_fields = ["updated_at"]
    fieldsets = (
        (
            "زمان و نرخ تولید",
            {
                "fields": (
                    "default_hourly_rate",
                    "minimum_billable_minutes",
                    "billing_increment_minutes",
                    "assembly_hourly_rate",
                )
            },
        ),
        (
            "دستمزد و حاشیه سود",
            {
                "fields": (
                    "default_labor_percent",
                    "default_margin_percent",
                )
            },
        ),
        (
            "حداقل سفارش و بسته‌بندی",
            {
                "fields": (
                    "minimum_order_amount",
                    "packaging_fee",
                )
            },
        ),
        (
            "مالیات",
            {"fields": ("vat_enabled", "tax_percent")},
        ),
        (
            "وضعیت",
            {"fields": ("updated_at",)},
        ),
    )

    class Media:
        css = {"all": ("admin/phase49-admin-tabs.css",)}
        js = ("admin/phase49-admin-tabs.js",)

    def has_add_permission(self, request):
        return not PricingSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "sku", "category", "minimum_price", "is_featured", "is_active", "published_at"]
    list_editable = ["is_featured", "is_active"]
    list_filter = ["category__section", "category", "is_featured", "is_active"]
    search_fields = ["title", "sku", "short_description", "description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["view_count", "created_at", "updated_at"]
    inlines = [ProductImageInline, ProductCompatibilityInline, ProductVariantInline]

    @admin.display(description="کمترین قیمت")
    def minimum_price(self, obj):
        price = obj.variants.filter(is_active=True).order_by("cached_unit_price").values_list("cached_unit_price", flat=True).first()
        return f"{price:,} تومان" if price else "بدون قیمت"


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "short_body", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["product__title", "user__username", "body"]
    actions = ["approve_selected"]

    @admin.display(description="متن")
    def short_body(self, obj):
        return obj.body[:80]

    @admin.action(description="تأیید دیدگاه‌های انتخاب‌شده")
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "rating", "is_verified_purchase", "is_approved", "created_at"]
    list_filter = ["rating", "is_verified_purchase", "is_approved", "created_at"]
    search_fields = ["product__title", "user__username", "title", "body"]
    actions = ["approve_selected"]

    @admin.action(description="تأیید نظرهای انتخاب‌شده")
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(ProductLike)
class ProductLikeAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "created_at"]
    search_fields = ["product__title", "user__username"]
    readonly_fields = ["product", "user", "created_at"]


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    list_display = ["title", "service_type", "sort_order", "is_active", "updated_at"]
    list_editable = ["sort_order", "is_active"]
    list_filter = ["service_type", "is_active"]
    search_fields = ["title", "short_description", "content"]
    prepopulated_fields = {"slug": ("title",)}


class ProductRequestImageInline(admin.TabularInline):
    model = ProductRequestImage
    extra = 0


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ["title", "request_type", "full_name", "phone", "brand", "model", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["request_type", "status", "created_at"]
    search_fields = ["title", "full_name", "phone", "brand", "model", "description"]
    inlines = [ProductRequestImageInline]

# BEGIN STORE COMMERCE PHASE 2
from django.utils import timezone
from .models import ShippingMethod, StoreAddress, StoreOrder, StoreOrderItem, StorePayment


class StoreOrderItemInline(admin.TabularInline):
    model = StoreOrderItem
    extra = 0
    can_delete = False
    readonly_fields = [
        "product", "variant", "product_title", "product_sku", "variant_code",
        "material_name", "quality_name", "unit_price", "quantity", "line_total",
        "unit_weight_grams",
    ]


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ["title", "code", "flat_fee", "free_over", "sort_order", "is_active"]
    list_editable = ["flat_fee", "free_over", "sort_order", "is_active"]
    prepopulated_fields = {"code": ("title",)}


@admin.register(StoreAddress)
class StoreAddressAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "full_name", "phone", "province", "county", "city", "is_default"]
    list_filter = ["province", "county", "city", "is_default"]
    search_fields = ["user__username", "full_name", "phone", "address", "postal_code"]


@admin.register(StoreOrder)
class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "user", "total_amount", "status", "payment_status", "shipping_title", "created_at"]
    list_filter = ["status", "payment_status", "shipping_method", "created_at"]
    search_fields = ["order_number", "user__username", "full_name", "phone", "tracking_code"]
    readonly_fields = [
        "order_number", "subtotal", "packaging_fee", "shipping_fee", "tax_amount",
        "discount_amount", "total_amount", "total_weight_grams", "paid_at", "created_at", "updated_at",
    ]
    inlines = [StoreOrderItemInline]
    actions = ["mark_processing", "mark_ready", "mark_shipped", "mark_delivered"]

    @admin.action(description="انتقال به در حال تولید")
    def mark_processing(self, request, queryset):
        queryset.filter(payment_status="paid").update(status="processing")

    @admin.action(description="علامت‌گذاری آماده ارسال")
    def mark_ready(self, request, queryset):
        queryset.update(status="ready")

    @admin.action(description="علامت‌گذاری ارسال شده")
    def mark_shipped(self, request, queryset):
        queryset.update(status="shipped")

    @admin.action(description="علامت‌گذاری تحویل شده")
    def mark_delivered(self, request, queryset):
        queryset.update(status="delivered")


@admin.register(StorePayment)
class StorePaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "amount", "method", "status", "ref_id", "created_at", "paid_at"]
    list_filter = ["method", "status", "created_at"]
    search_fields = ["order__order_number", "ref_id", "card_holder"]
    readonly_fields = ["idempotency_key", "created_at", "updated_at", "paid_at"]
    actions = ["approve_payments", "reject_payments"]

    @admin.action(description="تأیید پرداخت‌های انتخاب‌شده")
    def approve_payments(self, request, queryset):
        for payment in queryset.select_related("order"):
            if payment.status != "paid":
                payment.mark_paid(payment.ref_id or f"ADMIN-{payment.pk}")

    @admin.action(description="رد پرداخت‌های انتخاب‌شده")
    def reject_payments(self, request, queryset):
        for payment in queryset.select_related("order"):
            payment.status = "failed"
            payment.save(update_fields=["status", "updated_at"])
            payment.order.payment_status = "failed"
            payment.order.status = "awaiting_payment"
            payment.order.save(update_fields=["payment_status", "status", "updated_at"])
# END STORE COMMERCE PHASE 2

# BEGIN PHASE 4 SEO ADMIN
from . import admin_seo  # noqa: F401
# END PHASE 4 SEO ADMIN

# BEGIN STORE OPERATIONS PHASE 6 ADMIN
from datetime import timedelta
from django.db.models import Count, F, Q, Sum
from django.template.response import TemplateResponse
from django.utils import timezone

from .models import (
    Coupon,
    CouponUsage,
    CustomerNotification,
    InventoryMovement,
    ProductFAQ,
    ReturnRequest,
    Shipment,
    StoreInvoice,
    StoreOperationsDashboard,
    StoreOrderEvent,
)
from .services import notify, transition_order


class ProductFAQInline(admin.StackedInline):
    model = ProductFAQ
    extra = 0


class StoreOrderEventInline(admin.TabularInline):
    model = StoreOrderEvent
    extra = 0
    can_delete = False
    readonly_fields = ["status", "title", "description", "is_public", "created_by", "created_at"]


# Extend the active Product admin, including the SEO-enhanced replacement admin.
_product_admin = admin.site._registry.get(Product)
if _product_admin and ProductFAQInline not in _product_admin.inlines:
    _product_admin.inlines = tuple(_product_admin.inlines) + (ProductFAQInline,)


# Extend order admin with timeline and service-backed transitions.
if StoreOrderEventInline not in StoreOrderAdmin.inlines:
    StoreOrderAdmin.inlines = tuple(StoreOrderAdmin.inlines) + (StoreOrderEventInline,)
StoreOrderAdmin.list_display = ["order_number", "user", "total_amount", "discount_amount", "status", "payment_status", "inventory_reserved", "shipping_title", "created_at"]
StoreOrderAdmin.list_filter = ["status", "payment_status", "inventory_reserved", "shipping_method", "created_at"]
StoreOrderAdmin.readonly_fields = list(StoreOrderAdmin.readonly_fields) + ["coupon_code", "reservation_expires_at", "inventory_reserved"]


def _transition_action(status, description):
    def action(self, request, queryset):
        for order in queryset:
            transition_order(order, status, actor=request.user, description=description)
    return action


StoreOrderAdmin.mark_processing = _transition_action("processing", "سفارش وارد مرحله تولید و آماده‌سازی شد.")
StoreOrderAdmin.mark_processing.short_description = "انتقال به در حال تولید"
StoreOrderAdmin.mark_ready = _transition_action("ready", "سفارش آماده تحویل به شرکت حمل است.")
StoreOrderAdmin.mark_ready.short_description = "علامت‌گذاری آماده ارسال"
StoreOrderAdmin.mark_shipped = _transition_action("shipped", "سفارش تحویل شرکت حمل شد.")
StoreOrderAdmin.mark_shipped.short_description = "علامت‌گذاری ارسال شده"
StoreOrderAdmin.mark_delivered = _transition_action("delivered", "تحویل سفارش به مشتری ثبت شد.")
StoreOrderAdmin.mark_delivered.short_description = "علامت‌گذاری تحویل شده"
StoreOrderAdmin.mark_cancelled = _transition_action("cancelled", "سفارش لغو و رزرو موجودی آزاد شد.")
StoreOrderAdmin.mark_cancelled.short_description = "لغو سفارش و آزادسازی موجودی"
StoreOrderAdmin.actions = ["mark_processing", "mark_ready", "mark_shipped", "mark_delivered", "mark_cancelled"]


@admin.register(ProductVariant)
class ProductVariantInventoryAdmin(admin.ModelAdmin):
    list_display = ["product", "code", "material", "quality", "cached_unit_price", "stock_status", "track_inventory", "stock_quantity", "reserved_quantity", "available_display", "low_stock_threshold", "allow_backorder", "low_stock_display", "is_active"]
    list_editable = ["stock_status", "track_inventory", "stock_quantity", "low_stock_threshold", "allow_backorder", "is_active"]
    list_filter = ["track_inventory", "stock_status", "allow_backorder", "is_active", "product__category"]
    search_fields = ["product__title", "product__sku", "code", "material__name", "quality__name"]
    readonly_fields = ["reserved_quantity", "cached_unit_price"]

    @admin.display(description="قابل فروش")
    def available_display(self, obj):
        return "نامحدود" if obj.available_quantity is None else obj.available_quantity

    @admin.display(boolean=True, description="کم‌موجود")
    def low_stock_display(self, obj):
        return obj.is_low_stock

    def save_model(self, request, obj, form, change):
        old_stock = None
        if change:
            old_stock = ProductVariant.objects.filter(pk=obj.pk).values_list("stock_quantity", flat=True).first()
        super().save_model(request, obj, form, change)
        if old_stock is not None and int(old_stock) != int(obj.stock_quantity):
            InventoryMovement.objects.create(
                variant=obj,
                movement_type="adjustment",
                quantity=int(obj.stock_quantity) - int(old_stock),
                stock_after=obj.stock_quantity,
                reserved_after=obj.reserved_quantity,
                note="اصلاح موجودی از پنل مدیریت",
                created_by=request.user,
            )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "discount_type", "value", "minimum_order_amount", "used_count", "usage_limit", "starts_at", "ends_at", "is_active"]
    list_editable = ["is_active"]
    list_filter = ["discount_type", "is_active", "starts_at", "ends_at"]
    search_fields = ["code", "title"]
    filter_horizontal = ["categories", "products"]
    readonly_fields = ["used_count", "created_at", "updated_at"]


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ["coupon", "user", "order", "discount_amount", "created_at"]
    list_filter = ["coupon", "created_at"]
    search_fields = ["coupon__code", "user__username", "order__order_number"]
    readonly_fields = ["coupon", "user", "order", "discount_amount", "created_at"]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ["variant", "movement_type", "quantity", "stock_after", "reserved_after", "order", "created_by", "created_at"]
    list_filter = ["movement_type", "created_at", "variant__product__category"]
    search_fields = ["variant__product__title", "variant__code", "order__order_number", "note"]
    readonly_fields = ["variant", "movement_type", "quantity", "stock_after", "reserved_after", "order", "note", "created_by", "created_at"]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(StoreOrderEvent)
class StoreOrderEventAdmin(admin.ModelAdmin):
    list_display = ["order", "title", "status", "is_public", "created_by", "created_at"]
    list_filter = ["status", "is_public", "created_at"]
    search_fields = ["order__order_number", "title", "description"]
    readonly_fields = ["created_at"]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ["order", "carrier", "tracking_code", "status", "shipped_at", "estimated_delivery_date", "delivered_at"]
    list_filter = ["status", "carrier", "shipped_at", "delivered_at"]
    search_fields = ["order__order_number", "tracking_code", "carrier"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.tracking_code and obj.order.tracking_code != obj.tracking_code:
            obj.order.tracking_code = obj.tracking_code
            obj.order.save(update_fields=["tracking_code", "updated_at"])
        if obj.status == "shipped" and obj.order.status != "shipped":
            transition_order(obj.order, "shipped", actor=request.user, description="اطلاعات مرسوله و کد رهگیری ثبت شد.")
        elif obj.status == "delivered" and obj.order.status != "delivered":
            transition_order(obj.order, "delivered", actor=request.user, description="تحویل مرسوله به مشتری تأیید شد.")


@admin.register(StoreInvoice)
class StoreInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "order", "buyer_name", "total_amount", "issued_at"]
    search_fields = ["invoice_number", "order__order_number", "buyer_name", "buyer_phone"]
    readonly_fields = [field.name for field in StoreInvoice._meta.fields]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(CustomerNotification)
class CustomerNotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_type", "title", "read_at", "created_at"]
    list_filter = ["notification_type", "read_at", "created_at"]
    search_fields = ["user__username", "title", "message"]
    readonly_fields = ["created_at"]


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ["order", "user", "reason", "status", "created_at", "updated_at"]
    list_editable = ["status"]
    list_filter = ["status", "reason", "created_at"]
    search_fields = ["order__order_number", "user__username", "description", "admin_response"]

    def save_model(self, request, obj, form, change):
        previous = ReturnRequest.objects.filter(pk=obj.pk).values_list("status", flat=True).first() if change else None
        super().save_model(request, obj, form, change)
        if previous != obj.status:
            notify(obj.user, "وضعیت درخواست مرجوعی تغییر کرد", f"درخواست مربوط به سفارش {obj.order.order_number}: {obj.get_status_display()}", notification_type="order", url=obj.order.get_absolute_url())


@admin.register(StoreOperationsDashboard)
class StoreOperationsDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/operations_dashboard.html"
    actions = None

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return request.user.is_active and request.user.is_staff
    def has_delete_permission(self, request, obj=None): return False

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        month_start = now - timedelta(days=30)
        orders = StoreOrder.objects.all()
        paid = orders.filter(payment_status="paid")
        low_stock = ProductVariant.objects.filter(track_inventory=True, is_active=True).annotate(available=F("stock_quantity") - F("reserved_quantity")).filter(available__lte=F("low_stock_threshold"))
        context = {
            **self.admin_site.each_context(request),
            "title": "داشبورد عملیات فروشگاه",
            "today_orders": orders.filter(created_at__date=timezone.localdate()).count(),
            "pending_payments": orders.filter(payment_status__in=["pending", "awaiting_review"]).count(),
            "active_orders": orders.filter(status__in=["paid", "processing", "ready", "shipped"]).count(),
            "revenue_30": paid.filter(paid_at__gte=month_start).aggregate(value=Sum("total_amount"))["value"] or 0,
            "low_stock_count": low_stock.count(),
            "return_count": ReturnRequest.objects.filter(status__in=["submitted", "reviewing", "approved"]).count(),
            "recent_orders": orders.select_related("user").order_by("-created_at")[:10],
            "low_stock_variants": low_stock.select_related("product", "material", "quality")[:10],
            "opts": self.model._meta,
            "has_view_permission": True,
        }
        return TemplateResponse(request, self.change_list_template, context)
# END STORE OPERATIONS PHASE 6 ADMIN

# BEGIN AFFILIATE PARTNER PROGRAM PHASE 7 ADMIN
from .affiliate_services import approve_commission, mark_payout_paid, reject_payout, reverse_commission
from .models import (
    AffiliateAttribution,
    AffiliateCampaign,
    AffiliateClick,
    AffiliateCommission,
    AffiliateLedgerEntry,
    AffiliatePartner,
    AffiliatePayout,
    AffiliatePayoutItem,
    AffiliateProgramDashboard,
    AffiliateTier,
)
from .services import notify


class AffiliateCampaignInline(admin.TabularInline):
    model = AffiliateCampaign
    extra = 0
    fields = ["name", "slug", "target_path", "utm_source", "utm_medium", "utm_campaign", "is_active"]


@admin.register(AffiliateTier)
class AffiliateTierAdmin(admin.ModelAdmin):
    list_display = ["name", "commission_type", "commission_value", "attribution_days", "hold_days", "minimum_payout", "include_self_orders", "is_active"]
    list_editable = ["commission_value", "attribution_days", "hold_days", "minimum_payout", "include_self_orders", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AffiliatePartner)
class AffiliatePartnerAdmin(admin.ModelAdmin):
    list_display = ["display_name", "code", "partner_type", "tier", "status", "effective_rate", "customers_count", "orders_count", "balance_display", "created_at"]
    list_filter = ["status", "partner_type", "tier", "created_at"]
    search_fields = ["display_name", "company_name", "code", "user__username", "user__first_name", "user__last_name", "website"]
    readonly_fields = ["approved_at", "created_at", "updated_at", "balance_display"]
    inlines = [AffiliateCampaignInline]
    actions = ["approve_selected", "suspend_selected", "activate_selected"]

    @admin.display(description="نرخ مؤثر")
    def effective_rate(self, obj):
        if obj.effective_commission_type == "percent":
            return f"{obj.effective_commission_value}%"
        return f"{int(obj.effective_commission_value):,} تومان"

    @admin.display(description="زیرمجموعه")
    def customers_count(self, obj):
        return obj.attributions.count()

    @admin.display(description="سفارش")
    def orders_count(self, obj):
        return obj.referred_orders.count()

    @admin.display(description="مانده دفتر")
    def balance_display(self, obj):
        return f"{obj.ledger_balance:,} تومان"

    @admin.action(description="تأیید و فعال‌سازی همکاران انتخاب‌شده")
    def approve_selected(self, request, queryset):
        for partner in queryset.select_related("user"):
            partner.status = "active"
            partner.approved_at = timezone.now()
            partner.save(update_fields=["status", "approved_at", "updated_at"])
            AffiliateCampaign.objects.get_or_create(
                partner=partner,
                slug="main",
                defaults={"name": "لینک اصلی", "target_path": "/", "utm_source": partner.code.lower(), "utm_medium": "affiliate", "utm_campaign": "main"},
            )
            notify(partner.user, "همکاری شما تأیید شد", "حساب همکاری و لینک اختصاصی شما فعال شد.", notification_type="system", url=partner.get_absolute_url())

    @admin.action(description="تعلیق همکاران انتخاب‌شده")
    def suspend_selected(self, request, queryset):
        queryset.update(status="suspended", updated_at=timezone.now())

    @admin.action(description="فعال‌سازی مجدد همکاران انتخاب‌شده")
    def activate_selected(self, request, queryset):
        queryset.update(status="active", updated_at=timezone.now())


@admin.register(AffiliateCampaign)
class AffiliateCampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "partner", "slug", "target_path", "clicks_count", "customers_count", "orders_count", "is_active", "created_at"]
    list_filter = ["is_active", "created_at", "partner__partner_type"]
    search_fields = ["name", "slug", "partner__display_name", "partner__code", "target_path"]
    list_editable = ["is_active"]

    @admin.display(description="کلیک")
    def clicks_count(self, obj): return obj.clicks.count()
    @admin.display(description="مشتری")
    def customers_count(self, obj): return obj.attributions.count()
    @admin.display(description="سفارش")
    def orders_count(self, obj): return obj.orders.count()


@admin.register(AffiliateClick)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ["partner", "campaign", "user", "landing_path", "created_at"]
    list_filter = ["partner", "campaign", "created_at"]
    search_fields = ["partner__code", "partner__display_name", "landing_path", "referrer_url", "user__username"]
    readonly_fields = [field.name for field in AffiliateClick._meta.fields]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(AffiliateAttribution)
class AffiliateAttributionAdmin(admin.ModelAdmin):
    list_display = ["customer", "partner", "campaign", "is_locked", "attributed_at"]
    list_filter = ["partner", "campaign", "is_locked", "attributed_at"]
    search_fields = ["customer__username", "customer__first_name", "customer__last_name", "partner__display_name", "partner__code"]
    readonly_fields = ["click", "attributed_at"]


@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ["partner", "order", "basis_amount", "commission_value", "amount", "status", "eligible_at", "approved_at", "paid_at"]
    list_filter = ["status", "commission_type", "partner", "created_at"]
    search_fields = ["partner__display_name", "partner__code", "order__order_number", "note"]
    readonly_fields = ["partner", "order", "campaign", "attribution", "commission_type", "commission_value", "basis_amount", "amount", "created_at", "updated_at"]
    actions = ["approve_selected", "reverse_selected"]

    @admin.action(description="تأیید پورسانت‌های واجد شرایط")
    def approve_selected(self, request, queryset):
        count = 0
        for commission in queryset:
            if approve_commission(commission, actor=request.user):
                count += 1
        self.message_user(request, f"{count} پورسانت تأیید شد.")

    @admin.action(description="برگشت پورسانت سفارش‌های انتخاب‌شده")
    def reverse_selected(self, request, queryset):
        count = 0
        for commission in queryset.select_related("order"):
            if reverse_commission(commission.order, reason="برگشت دستی توسط مدیریت", actor=request.user):
                count += 1
        self.message_user(request, f"{count} پورسانت برگشت خورد.")


class AffiliatePayoutItemInline(admin.TabularInline):
    model = AffiliatePayoutItem
    extra = 0
    readonly_fields = ["commission", "amount"]
    can_delete = False


@admin.register(AffiliatePayout)
class AffiliatePayoutAdmin(admin.ModelAdmin):
    list_display = ["payout_number", "partner", "amount", "status", "account_holder", "reference_number", "requested_at", "processed_at"]
    list_filter = ["status", "requested_at", "processed_at"]
    search_fields = ["payout_number", "partner__display_name", "partner__code", "reference_number", "sheba_number", "card_number"]
    readonly_fields = ["payout_number", "partner", "amount", "sheba_number", "card_number", "account_holder", "requested_at", "processed_at"]
    inlines = [AffiliatePayoutItemInline]
    actions = ["approve_selected", "mark_paid_selected", "reject_selected"]

    @admin.action(description="تأیید درخواست‌های تسویه")
    def approve_selected(self, request, queryset):
        queryset.filter(status="requested").update(status="approved")

    @admin.action(description="ثبت پرداخت درخواست‌های انتخاب‌شده")
    def mark_paid_selected(self, request, queryset):
        count = 0
        for payout in queryset:
            try:
                mark_payout_paid(payout, actor=request.user, reference_number=payout.reference_number)
            except Exception:
                continue
            count += 1
        self.message_user(request, f"{count} تسویه پرداخت شد.")

    @admin.action(description="رد درخواست‌های تسویه")
    def reject_selected(self, request, queryset):
        for payout in queryset:
            reject_payout(payout, actor=request.user, note="رد توسط مدیریت")


@admin.register(AffiliateLedgerEntry)
class AffiliateLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ["partner", "entry_type", "amount", "commission", "payout", "created_by", "created_at"]
    list_filter = ["entry_type", "partner", "created_at"]
    search_fields = ["partner__display_name", "partner__code", "note", "commission__order__order_number", "payout__payout_number"]
    readonly_fields = [field.name for field in AffiliateLedgerEntry._meta.fields]
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(AffiliateProgramDashboard)
class AffiliateProgramDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/affiliate_dashboard.html"
    actions = None
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return request.user.is_active and request.user.is_staff
    def has_delete_permission(self, request, obj=None): return False
    def get_queryset(self, request): return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        since = timezone.now() - timedelta(days=30)
        partners = AffiliatePartner.objects.all()
        paid_orders = StoreOrder.objects.filter(payment_status="paid", affiliate_partner__isnull=False)
        context = {
            **self.admin_site.each_context(request),
            "title": "داشبورد همکاری در فروش",
            "active_partners": partners.filter(status="active").count(),
            "pending_partners": partners.filter(status="pending").count(),
            "clicks_30": AffiliateClick.objects.filter(created_at__gte=since).count(),
            "customers_total": AffiliateAttribution.objects.count(),
            "referred_revenue": paid_orders.aggregate(value=Sum("total_amount"))["value"] or 0,
            "pending_commissions": AffiliateCommission.objects.filter(status="pending").aggregate(value=Sum("amount"))["value"] or 0,
            "approved_commissions": AffiliateCommission.objects.filter(status="approved").aggregate(value=Sum("amount"))["value"] or 0,
            "open_payouts": AffiliatePayout.objects.filter(status__in=["requested", "approved"]).aggregate(value=Sum("amount"))["value"] or 0,
            "recent_partners": partners.select_related("user", "tier")[:10],
            "recent_commissions": AffiliateCommission.objects.select_related("partner", "order")[:10],
            "opts": self.model._meta,
            "has_view_permission": True,
        }
        return TemplateResponse(request, self.change_list_template, context)

# Add referral columns to the existing order admin without replacing its workflow.
if "affiliate_partner" not in StoreOrderAdmin.list_display:
    StoreOrderAdmin.list_display = list(StoreOrderAdmin.list_display[:-1]) + ["affiliate_partner", "affiliate_code", StoreOrderAdmin.list_display[-1]]
if "affiliate_partner" not in StoreOrderAdmin.list_filter:
    StoreOrderAdmin.list_filter = list(StoreOrderAdmin.list_filter) + ["affiliate_partner"]
# END AFFILIATE PARTNER PROGRAM PHASE 7 ADMIN

# BEGIN INVENTORY FINANCE CATALOG PHASE 8 ADMIN
from datetime import timedelta

from django.contrib import messages
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.utils import timezone

from .catalog_importer import convert_asset_to_product, import_single_url
from .models import (
    BusinessFinanceDashboard,
    CostEntry,
    FilamentMovement,
    FilamentPurchase,
    FilamentPurchaseItem,
    FilamentSpool,
    ImportedPrintAsset,
    ImportedPrintAssetImage,
    MaterialUsage,
    PrintCatalogImportJob,
    PrintCatalogSource,
    ProductionJob,
)
from .production_services import (
    finance_summary,
    finalize_production_job,
    inventory_summary,
    receive_filament_purchase,
)


class ImportedPrintAssetImageInline(admin.TabularInline):
    model = ImportedPrintAssetImage
    extra = 0
    fields = ["image", "remote_url", "alt_text", "sort_order"]


@admin.register(PrintCatalogSource)
class PrintCatalogSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "base_url", "adapter_key", "default_category", "respect_robots_txt", "is_active"]
    list_filter = ["adapter_key", "respect_robots_txt", "download_preview_images", "is_active"]
    search_fields = ["name", "code", "base_url", "allowed_domains"]
    prepopulated_fields = {"code": ("name",)}


@admin.register(ImportedPrintAsset)
class ImportedPrintAssetAdmin(admin.ModelAdmin):
    list_display = ["title", "source", "file_format", "archive_status", "status", "has_private_download", "product", "imported_at"]
    list_filter = ["status", "source", "file_format", "archive_status", "keep_public_when_source_disabled", "imported_at"]
    search_fields = ["title", "description", "tags", "author_name", "source_url", "external_id"]
    readonly_fields = [
        "source_url_link", "private_download_link", "source_payload", "imported_at", "updated_at", "product",
    ]
    inlines = [ImportedPrintAssetImageInline]
    actions = ["mark_reviewed", "convert_selected_to_products", "refresh_selected"]

    fieldsets = (
        ("اطلاعات استخراج‌شده", {
            "fields": (
                "source", "source_url_link", "external_id", "title", "slug",
                "short_description", "description", "technical_specs", "tags",
                "author_name", "license_name", "license_url",
            )
        }),
        ("فایل و تصاویر", {
            "fields": (
                "preview_image", "remote_image_url", "file_format", "private_download_link",
                "archive_status", "archived_model_file", "keep_public_when_source_disabled",
            )
        }),
        ("کنترل مدیریت", {
            "fields": ("status", "product", "admin_note", "source_payload", "imported_at", "updated_at")
        }),
    )

    @admin.display(description="صفحه منبع")
    def source_url_link(self, obj):
        if not obj or not obj.source_url:
            return "-"
        return format_html('<a href="{}" target="_blank" rel="noopener">بازکردن صفحه منبع</a>', obj.source_url)

    @admin.display(description="لینک دانلود خصوصی")
    def private_download_link(self, obj):
        if not obj or not obj.private_download_url:
            return "کشف نشده یا ذخیره نشده است."
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer" style="font-weight:700;color:#b45309">دانلود خصوصی ادمین</a>',
            obj.private_download_url,
        )

    @admin.display(boolean=True, description="لینک دانلود")
    def has_private_download(self, obj):
        return bool(obj.private_download_url)

    @admin.action(description="علامت‌گذاری به‌عنوان بررسی‌شده")
    def mark_reviewed(self, request, queryset):
        queryset.filter(status="pending").update(status="reviewed")

    @admin.action(description="تبدیل به محصول آماده چاپ؛ محصول به‌صورت غیرفعال ساخته می‌شود")
    def convert_selected_to_products(self, request, queryset):
        success = 0
        errors = []
        for asset in queryset.select_related("source__default_category", "product"):
            try:
                convert_asset_to_product(asset)
                success += 1
            except Exception as error:
                errors.append(f"{asset.title}: {error}")
        if success:
            self.message_user(request, f"{success} محصول پیش‌نویس ساخته شد.", level=messages.SUCCESS)
        for error in errors[:10]:
            self.message_user(request, error, level=messages.ERROR)

    @admin.action(description="دریافت مجدد اطلاعات از صفحه منبع")
    def refresh_selected(self, request, queryset):
        success = 0
        for asset in queryset.select_related("source"):
            try:
                import_single_url(asset.source, asset.source_url, actor=request.user)
                success += 1
            except Exception as error:
                self.message_user(request, f"{asset.title}: {error}", level=messages.ERROR)
        if success:
            self.message_user(request, f"{success} مورد به‌روزرسانی شد.", level=messages.SUCCESS)


@admin.register(PrintCatalogImportJob)
class PrintCatalogImportJobAdmin(admin.ModelAdmin):
    list_display = ["source", "source_url_short", "status", "result_asset", "created_by", "created_at", "finished_at"]
    list_filter = ["status", "source", "created_at"]
    search_fields = ["source_url", "log", "result_asset__title"]
    readonly_fields = ["status", "result_asset", "log", "created_by", "started_at", "finished_at", "created_at"]
    actions = ["run_selected_jobs"]

    @admin.display(description="آدرس")
    def source_url_short(self, obj):
        return obj.source_url[:70] + ("…" if len(obj.source_url) > 70 else "")

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="اجرای واردسازی‌های انتخاب‌شده")
    def run_selected_jobs(self, request, queryset):
        success = 0
        for job in queryset.select_related("source"):
            if job.status == "running":
                continue
            try:
                import_single_url(job.source, job.source_url, actor=request.user, job=job)
                success += 1
            except Exception as error:
                self.message_user(request, f"{job.source_url}: {error}", level=messages.ERROR)
        if success:
            self.message_user(request, f"{success} واردسازی با موفقیت اجرا شد.", level=messages.SUCCESS)


class FilamentPurchaseItemInline(admin.TabularInline):
    model = FilamentPurchaseItem
    extra = 1
    fields = [
        "material", "brand", "color_name", "color_hex", "quantity_rolls",
        "net_weight_per_roll_grams", "total_purchase_amount", "allocated_extra_cost",
        "sale_price_per_gram", "generated_spools",
    ]
    readonly_fields = ["generated_spools"]


@admin.register(FilamentPurchase)
class FilamentPurchaseAdmin(admin.ModelAdmin):
    list_display = ["purchase_number", "supplier_name", "invoice_number", "purchased_at", "items_count", "purchase_total", "status", "received_at"]
    list_filter = ["status", "purchased_at", "supplier_name"]
    search_fields = ["purchase_number", "supplier_name", "invoice_number", "note"]
    readonly_fields = ["purchase_number", "received_at", "created_at", "updated_at"]
    inlines = [FilamentPurchaseItemInline]
    actions = ["receive_selected"]

    @admin.display(description="تعداد ردیف")
    def items_count(self, obj):
        return obj.items.count()

    @admin.display(description="جمع خرید")
    def purchase_total(self, obj):
        value = obj.items.aggregate(value=Sum("total_purchase_amount"))["value"] or 0
        return f"{value + obj.shipping_cost + obj.other_cost:,} تومان"

    @admin.action(description="نهایی‌سازی خرید و ساخت رول‌های انبار")
    def receive_selected(self, request, queryset):
        total = 0
        for purchase in queryset:
            try:
                total += receive_filament_purchase(purchase, actor=request.user)
            except Exception as error:
                self.message_user(request, f"{purchase.purchase_number}: {error}", level=messages.ERROR)
        if total:
            self.message_user(request, f"{total} رول وارد انبار شد.", level=messages.SUCCESS)


@admin.register(FilamentSpool)
class FilamentSpoolAdmin(admin.ModelAdmin):
    list_display = [
        "code", "material", "brand", "color_badge", "nominal_weight_grams",
        "remaining_weight_grams", "remaining_percent", "purchase_price",
        "cost_per_gram_snapshot", "sale_price_per_gram_snapshot", "status", "location",
    ]
    list_filter = ["status", "material", "brand", "purchased_at"]
    search_fields = ["code", "material__name", "brand", "color_name", "location"]
    readonly_fields = ["code", "cost_per_gram_snapshot", "created_at", "updated_at"]
    actions = ["mark_quarantine", "mark_open"]

    @admin.display(description="رنگ")
    def color_badge(self, obj):
        if obj.color_hex:
            return format_html('<span style="display:inline-flex;gap:6px;align-items:center"><i style="width:16px;height:16px;border-radius:50%;background:{};border:1px solid #aaa"></i>{}</span>', obj.color_hex, obj.color_name or obj.color_hex)
        return obj.color_name or "-"

    @admin.display(description="درصد باقی‌مانده")
    def remaining_percent(self, obj):
        if not obj.nominal_weight_grams:
            return "0%"
        value = Decimal(obj.remaining_weight_grams) * Decimal("100") / Decimal(obj.nominal_weight_grams)
        return f"{value.quantize(Decimal('0.1'))}%"

    @admin.action(description="انتقال رول‌ها به قرنطینه")
    def mark_quarantine(self, request, queryset):
        queryset.update(status="quarantine")

    @admin.action(description="علامت‌گذاری رول‌ها به‌عنوان بازشده")
    def mark_open(self, request, queryset):
        queryset.exclude(status__in=["empty", "archived"]).update(status="open", opened_at=timezone.now())


@admin.register(FilamentMovement)
class FilamentMovementAdmin(admin.ModelAdmin):
    list_display = ["created_at", "material", "spool", "movement_type", "grams", "balance_after", "total_cost", "job", "created_by"]
    list_filter = ["movement_type", "material", "created_at"]
    search_fields = ["spool__code", "job__job_number", "note", "material__name"]
    readonly_fields = [field.name for field in FilamentMovement._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MaterialUsageInline(admin.TabularInline):
    model = MaterialUsage
    extra = 0
    fields = [
        "material", "color_name", "planned_grams", "actual_grams", "waste_grams",
        "sale_price_per_gram_snapshot", "material_charge_snapshot",
        "cost_per_gram_snapshot", "material_cost_snapshot", "posted_at", "note",
    ]
    readonly_fields = ["cost_per_gram_snapshot", "material_cost_snapshot", "posted_at"]


class CostEntryInline(admin.TabularInline):
    model = CostEntry
    extra = 0
    fields = [
        "category", "description", "actual_cost", "customer_charge",
        "included_in_order_total", "incurred_at", "receipt",
    ]


@admin.register(ProductionJob)
class ProductionJobAdmin(admin.ModelAdmin):
    list_display = [
        "job_number", "title", "status", "order_reference", "total_revenue_display",
        "material_cost_display", "operating_cost_display", "affiliate_cost_display",
        "net_profit_display", "profit_margin_display", "created_at",
    ]
    list_filter = ["status", "created_at", "completed_at"]
    search_fields = ["job_number", "title", "store_order__order_number", "custom_order__phone", "custom_order__first_name", "custom_order__last_name"]
    readonly_fields = [
        "job_number", "revenue_snapshot", "tax_snapshot", "total_revenue_display",
        "material_cost_display", "operating_cost_display", "affiliate_cost_display",
        "total_cost_display", "net_profit_display", "profit_margin_display", "created_at", "updated_at",
    ]
    inlines = [MaterialUsageInline, CostEntryInline]
    actions = ["finalize_selected_jobs", "mark_printing"]

    @admin.display(description="سفارش")
    def order_reference(self, obj):
        if obj.store_order_id:
            return obj.store_order.order_number
        if obj.custom_order_id:
            return f"سفارشی #{obj.custom_order_id}"
        return "دستی"

    @admin.display(description="درآمد")
    def total_revenue_display(self, obj):
        return f"{obj.total_revenue:,} تومان"

    @admin.display(description="هزینه متریال")
    def material_cost_display(self, obj):
        return f"{obj.material_cost:,} تومان"

    @admin.display(description="سایر هزینه‌ها")
    def operating_cost_display(self, obj):
        return f"{obj.operating_cost:,} تومان"

    @admin.display(description="پورسانت")
    def affiliate_cost_display(self, obj):
        return f"{obj.affiliate_cost:,} تومان"

    @admin.display(description="کل هزینه")
    def total_cost_display(self, obj):
        return f"{obj.total_cost:,} تومان"

    @admin.display(description="سود خالص")
    def net_profit_display(self, obj):
        color = "#15803d" if obj.net_profit >= 0 else "#b91c1c"
        return format_html('<strong style="color:{}">{:,} تومان</strong>', color, obj.net_profit)

    @admin.display(description="حاشیه سود")
    def profit_margin_display(self, obj):
        return f"{obj.profit_margin_percent}%"

    @admin.action(description="ثبت مصرف انبار و تکمیل پروژه‌های انتخاب‌شده")
    def finalize_selected_jobs(self, request, queryset):
        count = 0
        for job in queryset:
            try:
                finalize_production_job(job, actor=request.user)
                count += 1
            except Exception as error:
                self.message_user(request, f"{job.job_number}: {error}", level=messages.ERROR)
        if count:
            self.message_user(request, f"{count} پروژه تکمیل و مصرف انبار ثبت شد.", level=messages.SUCCESS)

    @admin.action(description="انتقال به وضعیت در حال چاپ")
    def mark_printing(self, request, queryset):
        queryset.filter(status="planned").update(status="printing", started_at=timezone.now())


@admin.register(CostEntry)
class CostEntryAdmin(admin.ModelAdmin):
    list_display = ["incurred_at", "category", "description", "job", "actual_cost", "customer_charge", "included_in_order_total"]
    list_filter = ["category", "included_in_order_total", "incurred_at"]
    search_fields = ["description", "job__job_number", "job__title"]
    autocomplete_fields = ["job"]


@admin.register(BusinessFinanceDashboard)
class BusinessFinanceDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/business_finance_dashboard.html"
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        since = timezone.now() - timedelta(days=30)
        summary_30 = finance_summary(since=since)
        stock_rows = inventory_summary()
        low_stock = [row for row in stock_rows if row["needs_reorder"]]
        jobs = ProductionJob.objects.select_related("store_order", "custom_order").exclude(status="cancelled")
        context = {
            **self.admin_site.each_context(request),
            "title": "داشبورد انبار، بهای تمام‌شده و سود",
            "summary_30": summary_30,
            "stock_rows": stock_rows[:20],
            "low_stock": low_stock,
            "open_jobs": jobs.exclude(status="completed").count(),
            "completed_30": jobs.filter(status="completed", completed_at__gte=since).count(),
            "recent_jobs": jobs[:12],
            "recent_expenses": CostEntry.objects.select_related("job")[:12],
            "opts": self.model._meta,
            "has_view_permission": True,
        }
        return TemplateResponse(request, self.change_list_template, context)


admin.site.site_header = "مدیریت حرفه‌ای 3DprintHub"
admin.site.site_title = "3DprintHub Admin"
admin.site.index_title = "مرکز کنترل فروش، تولید، انبار و مالی"

# نمایش سود پروژه در فهرست سفارش‌های فروشگاه بدون تغییر جریان قبلی.
def _store_order_profit(obj):
    try:
        return f"{obj.production_job.net_profit:,} تومان"
    except Exception:
        return "-"
_store_order_profit.short_description = "سود پروژه"
if "_phase8_profit" not in StoreOrderAdmin.list_display:
    StoreOrderAdmin._phase8_profit = _store_order_profit
    StoreOrderAdmin.list_display = list(StoreOrderAdmin.list_display) + ["_phase8_profit"]
# END INVENTORY FINANCE CATALOG PHASE 8 ADMIN

# BEGIN MULTI SOURCE CATALOG PHASE 9 ADMIN
from django.contrib import messages
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils.html import format_html

from .catalog_sync import approve_asset_for_public, convert_approved_asset_to_product, sync_catalog_source
from .models import (
    CatalogAssetMetrics,
    CatalogCategoryRule,
    CatalogSourcePolicy,
    CatalogSyncDashboard,
    CatalogSyncRun,
)


@admin.register(CatalogSourcePolicy)
class CatalogSourcePolicyAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "source_kind",
        "discovery_mode",
        "public_display_policy",
        "public_reference_enabled",
        "source_priority",
        "default_limit",
        "maximum_limit",
        "last_synced_at",
        "is_active",
    )
    list_filter = ("source_kind", "discovery_mode", "public_display_policy", "public_reference_enabled", "is_active")
    search_fields = ("source__name", "source__code", "policy_note")
    fieldsets = (
        ("منبع و روش دریافت", {"fields": ("source", "source_kind", "source_priority", "discovery_mode", "is_active"), "description": "عدد اولویت کمتر یعنی سهم و نمایش بالاتر. غیرفعال‌کردن منبع، مدل‌های وابسته را از نمایش خارج می‌کند؛ فایل‌های دانلودشده، آرشیوی یا سفارش‌گرفته‌شده حفظ می‌شوند."}),
        ("فهرست و API", {"fields": ("discovery_url_template", "api_base_url", "api_token_env")}),
        ("ظرفیت و سرعت", {"fields": ("default_limit", "maximum_limit", "page_size", "max_pages", "request_delay_ms")}),
        ("نمایش مرجع و مجوز", {"fields": ("public_reference_enabled", "public_display_policy", "cache_images_after_approval", "store_download_links", "auto_create_draft_products", "requires_attribution", "terms_url", "policy_note"), "description": "نمایش مرجع شامل نام، تصویر، مشخصات و لینک صفحه اصلی است و به معنی فروش فایل دیجیتال نیست."}),
        ("همگام‌سازی", {"fields": ("last_synced_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ("last_synced_at",)


@admin.register(CatalogCategoryRule)
class CatalogCategoryRuleAdmin(admin.ModelAdmin):
    list_display = ("segment", "target_category", "source_kind", "priority", "is_active")
    list_filter = ("segment", "source_kind", "is_active")
    search_fields = ("title_keywords", "source_category_keywords", "target_category__name")
    ordering = ("priority", "id")


@admin.action(description="اجرای دریافت برای اجراهای انتخاب‌شده")
def run_catalog_syncs(modeladmin, request, queryset):
    succeeded = 0
    failed = 0
    for run in queryset.select_related("source"):
        try:
            sync_catalog_source(
                source=run.source,
                requested_limit=run.requested_limit,
                sort_mode=run.sort_mode,
                actor=request.user,
                hydrate_files=False,
                sync_run=run,
            )
            succeeded += 1
        except Exception as exc:
            failed += 1
            modeladmin.message_user(request, f"{run.source}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{succeeded} اجرا تکمیل و {failed} اجرا ناموفق شد.")


@admin.register(CatalogSyncRun)
class CatalogSyncRunAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "sort_mode",
        "requested_limit",
        "status",
        "discovered_count",
        "imported_count",
        "failed_count",
        "created_at",
    )
    list_filter = ("status", "sort_mode", "source")
    search_fields = ("source__name", "log")
    readonly_fields = (
        "status", "discovered_count", "imported_count", "skipped_count", "failed_count",
        "current_page", "cursor", "log", "started_at", "finished_at", "created_at",
    )
    actions = (run_catalog_syncs,)


@admin.action(description="تأیید مجوز و نمایش عمومی فایل‌های انتخاب‌شده")
def approve_catalog_assets(modeladmin, request, queryset):
    count = 0
    for metrics in queryset.select_related("asset", "asset__source"):
        try:
            approve_asset_for_public(metrics.asset, actor=request.user, create_product=False, cache_images=True)
            count += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{metrics.asset}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{count} فایل برای نمایش عمومی تأیید شد.")


@admin.action(description="ساخت محصول غیرفعال از فایل‌های تأییدشده")
def create_draft_products_from_assets(modeladmin, request, queryset):
    count = 0
    for metrics in queryset.select_related("asset", "target_category"):
        try:
            convert_approved_asset_to_product(metrics.asset)
            count += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{metrics.asset}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{count} محصول غیرفعال ساخته شد.")


@admin.action(description="مسدودکردن نمایش عمومی")
def block_catalog_assets(modeladmin, request, queryset):
    queryset.update(public_approved=False, license_review_status="blocked")
    modeladmin.message_user(request, "نمایش عمومی فایل‌های انتخاب‌شده مسدود شد.")


@admin.register(CatalogAssetMetrics)
class CatalogAssetMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "asset_link", "source_kind", "segment", "target_category", "downloads_count",
        "likes_count", "views_count", "license_review_status", "commercial_use_allowed",
        "public_approved", "last_synced_at",
    )
    list_filter = (
        "source_kind", "segment", "license_review_status", "commercial_use_allowed",
        "public_approved", "target_category",
    )
    search_fields = ("asset__title", "asset__author_name", "asset__source_url", "license_code")
    readonly_fields = (
        "asset_link", "file_links_private", "image_urls_private", "raw_metrics", "last_synced_at",
    )
    actions = (approve_catalog_assets, create_draft_products_from_assets, block_catalog_assets)
    fieldsets = (
        ("فایل و دسته‌بندی", {"fields": ("asset_link", "source_kind", "source_category", "segment", "target_category", "popularity_rank")}),
        ("آمار", {"fields": ("views_count", "likes_count", "downloads_count", "makes_count", "comments_count", "rating")}),
        ("چاپ و فایل", {"fields": ("estimated_weight_grams", "estimated_print_minutes", "estimate_source", "file_formats", "file_links_private", "image_urls_private")}),
        ("مجوز", {"fields": ("license_code", "commercial_use_allowed", "license_review_status", "public_approved", "blocked_reason", "attribution_text", "creator_url")}),
        ("داده فنی", {"fields": ("raw_metrics", "last_synced_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="فایل")
    def asset_link(self, obj):
        url = reverse("admin:store_importedprintasset_change", args=[obj.asset_id])
        return format_html('<a href="{}">{}</a>', url, obj.asset.title)

    @admin.display(description="لینک‌های دانلود خصوصی")
    def file_links_private(self, obj):
        if not obj.file_links:
            return "-"
        return format_html("<br>".join(f'<a href="{url}" target="_blank" rel="noopener">فایل {index}</a>' for index, url in enumerate(obj.file_links, 1)))

    @admin.display(description="آدرس تصاویر منبع")
    def image_urls_private(self, obj):
        if not obj.image_urls:
            return "-"
        return format_html("<br>".join(f'<a href="{url}" target="_blank" rel="noopener">تصویر {index}</a>' for index, url in enumerate(obj.image_urls, 1)))


@admin.register(CatalogSyncDashboard)
class CatalogSyncDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/catalog_sync_dashboard/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def changelist_view(self, request, extra_context=None):
        context = {
            "title": "داشبورد دریافت کاتالوگ فایل‌های آماده چاپ",
            "source_count": CatalogSourcePolicy.objects.filter(is_active=True).count(),
            "asset_count": CatalogAssetMetrics.objects.count(),
            "public_count": CatalogAssetMetrics.objects.filter(public_approved=True).count(),
            "blocked_count": CatalogAssetMetrics.objects.filter(license_review_status="blocked").count(),
            "pending_count": CatalogAssetMetrics.objects.filter(license_review_status__in=["unknown", "manual"]).count(),
            "download_sum": CatalogAssetMetrics.objects.aggregate(total=Sum("downloads_count"))["total"] or 0,
            "recent_runs": CatalogSyncRun.objects.select_related("source").order_by("-created_at")[:10],
            "source_policies": CatalogSourcePolicy.objects.select_related("source").order_by("source__name"),
        }
        if extra_context:
            context.update(extra_context)
        return super().changelist_view(request, extra_context=context)

# END MULTI SOURCE CATALOG PHASE 9 ADMIN

# BEGIN PHASE 10 AUTOMATION AND MARKET PRICING ADMIN
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from .catalog_automation import process_catalog_queue, queue_catalog_source, queue_due_catalog_sources
from .market_pricing import refresh_fx_rates, refresh_material_market_prices
from .models import (
    CatalogAssetPublication,
    CatalogAutomationDashboard,
    CatalogAutomationSetting,
    CatalogQueuedJob,
    CatalogSourceSchedule,
    ExchangeRateProvider,
    ExchangeRateSnapshot,
    MarketPricingSetting,
    MaterialMarketPriceSnapshot,
    CatalogSyncRun,
)


@admin.register(CatalogAutomationSetting)
class CatalogAutomationSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("صف و Worker", {"fields": ("queue_enabled", "timezone_name", "process_batch_size", "stale_run_minutes"), "description": "Cron فقط Jobها را صف و پردازش می‌کند؛ اجرای طولانی داخل درخواست مرورگر انجام نمی‌شود."}),
        ("صفحه اول", {"fields": ("homepage_slider_count", "homepage_grid_count"), "description": "مدل‌های مرجع تازه با تصویر محلی یا Remote به‌صورت خودکار نمایش داده می‌شوند؛ فروش مستقیم فقط پس از بررسی مجوز و فایل ممکن است."}),
        ("وضعیت", {"fields": ("last_queue_scan_at", "updated_at")}),
    )
    readonly_fields = ("last_queue_scan_at", "updated_at")

    def has_add_permission(self, request):
        return not CatalogAutomationSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.action(description="قرار دادن منابع انتخاب‌شده در صف دریافت اکنون")
def queue_selected_sources(modeladmin, request, queryset):
    success = 0
    for schedule in queryset.select_related("policy", "policy__source"):
        try:
            queue_catalog_source(schedule=schedule, actor=request.user, trigger="manual")
            success += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{schedule.policy.source.name}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{success} منبع در صف قرار گرفت.")


@admin.register(CatalogSourceSchedule)
class CatalogSourceScheduleAdmin(admin.ModelAdmin):
    list_display = ("source_name", "enabled", "run_time", "weekdays", "sort_mode", "requested_limit", "last_queued_on", "last_completed_at", "queue_now_button")
    list_filter = ("enabled", "sort_mode", "auto_approve_commercial", "show_approved_on_homepage")
    search_fields = ("policy__source__name", "policy__source__code")
    actions = (queue_selected_sources,)
    fieldsets = (
        ("منبع", {"fields": ("policy", "enabled"), "description": "برای هر یک از MakerWorld، Printables، Thingiverse و GrabCAD یک زمان‌بندی مستقل تعریف می‌شود."}),
        ("زمان اجرا", {"fields": ("run_time", "weekdays", "sort_mode", "requested_limit", "hydrate_files"), "description": "Cron باید هر چند دقیقه run_phase10_automation را اجرا کند؛ سیستم فقط در ساعت و روز تعیین‌شده Job می‌سازد."}),
        ("مجوز و انتشار", {"fields": ("auto_approve_commercial", "cache_images_after_approval", "show_approved_on_homepage"), "description": "تأیید خودکار فقط برای مجوز تجاری صریح فعال می‌شود. GrabCAD همچنان فقط مرجع داخلی است."}),
        ("وضعیت", {"fields": ("last_queued_on", "last_completed_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("last_queued_on", "last_completed_at")

    @admin.display(description="منبع", ordering="policy__source__name")
    def source_name(self, obj):
        return obj.policy.source.name

    @admin.display(description="اجرای فوری")
    def queue_now_button(self, obj):
        return format_html('<a class="button" href="{}">شروع دریافت</a>', f"{obj.pk}/queue-now/")

    def get_urls(self):
        return [
            path("<int:schedule_id>/queue-now/", self.admin_site.admin_view(self.queue_now_view), name="store_catalogsourceschedule_queue_now"),
        ] + super().get_urls()

    def queue_now_view(self, request, schedule_id):
        schedule = self.get_object(request, schedule_id)
        if schedule is None:
            self.message_user(request, "زمان‌بندی پیدا نشد.", level=messages.ERROR)
        else:
            try:
                run = queue_catalog_source(schedule=schedule, actor=request.user, trigger="manual")
                self.message_user(request, f"دریافت {schedule.policy.source.name} در صف قرار گرفت؛ شماره اجرا {run.pk}.")
            except Exception as exc:
                self.message_user(request, str(exc), level=messages.ERROR)
        return HttpResponseRedirect("../../")


@admin.register(CatalogQueuedJob)
class CatalogQueuedJobAdmin(admin.ModelAdmin):
    list_display = ("run", "trigger", "scheduled_for", "hydrate_files", "attempts", "claimed_at", "created_at")
    list_filter = ("trigger", "hydrate_files")
    readonly_fields = ("run", "trigger", "scheduled_for", "hydrate_files", "attempts", "claimed_at", "created_at")
    search_fields = ("run__source__name", "run__log")

    def has_add_permission(self, request):
        return False


@admin.register(CatalogAssetPublication)
class CatalogAssetPublicationAdmin(admin.ModelAdmin):
    list_display = ("metrics", "show_on_homepage", "homepage_priority", "first_published_at", "last_public_refresh_at")
    list_filter = ("show_on_homepage", "metrics__source_kind", "metrics__segment")
    search_fields = ("metrics__asset__title", "seo_title", "seo_description")
    fieldsets = (
        ("نمایش صفحه اول", {"fields": ("metrics", "show_on_homepage", "homepage_priority"), "description": "مدل باید هم‌زمان مجوز تجاری تأییدشده، public_approved و تصویر محلی داشته باشد."}),
        ("SEO", {"fields": ("seo_title", "seo_description", "image_alt_text"), "description": "عنوان و توضیح باید درباره سفارش چاپ فیزیکی باشد و نباید وعده دانلود فایل بدهد."}),
        ("زمان‌ها", {"fields": ("first_published_at", "last_public_refresh_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("first_published_at", "last_public_refresh_at")


@admin.register(MarketPricingSetting)
class MarketPricingSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("فعال‌سازی", {"fields": ("enabled", "refresh_fx_on_public_request", "use_daily_high_fx"), "description": "مشتری فقط قیمت نهایی هر گرم را می‌بیند؛ نرخ دلار و قیمت دلاری فقط در ادمین است."}),
        ("دوره بروزرسانی", {"fields": ("refresh_fx_minutes", "refresh_bambu_hours")}),
        ("فرمول عمومی", {"fields": ("default_import_cost_percent", "default_margin_percent", "price_rounding_toman"), "description": "بهای هر گرم = قیمت دلاری × بیشترین نرخ دلار روز × هزینه واردات ÷ وزن رول؛ سپس حاشیه فروش اعمال می‌شود."}),
        ("وضعیت", {"fields": ("last_fx_refresh_at", "last_bambu_refresh_at", "last_error", "updated_at")}),
    )
    readonly_fields = ("last_fx_refresh_at", "last_bambu_refresh_at", "last_error", "updated_at")

    def has_add_permission(self, request):
        return not MarketPricingSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.action(description="دریافت نرخ دلار از منابع انتخاب‌شده")
def refresh_exchange_sources(modeladmin, request, queryset):
    snapshots = refresh_fx_rates()
    modeladmin.message_user(request, f"{len(snapshots)} نرخ معتبر ثبت شد.")


@admin.register(ExchangeRateProvider)
class ExchangeRateProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "provider_type", "priority", "manual_sell_rate_toman", "is_active", "last_success_at")
    list_filter = ("provider_type", "is_active")
    search_fields = ("name", "code", "endpoint_url")
    actions = (refresh_exchange_sources,)
    fieldsets = (
        ("تعریف منبع", {"fields": ("name", "code", "provider_type", "is_active", "priority")}),
        ("اتصال API", {"fields": ("endpoint_url", "username_env", "secret_env", "json_sell_path", "response_unit", "multiplier", "timeout_seconds"), "description": "کلید API را داخل کد یا دیتابیس وارد نکنید؛ فقط نام متغیر محیطی را بنویسید."}),
        ("نرخ دستی پشتیبان", {"fields": ("manual_sell_rate_toman",), "description": "اگر API تهیه نشده، یک منبع Manual فعال با نرخ فروش آزاد ثبت کنید."}),
        ("وضعیت", {"fields": ("last_success_at", "last_error"), "classes": ("collapse",)}),
    )
    readonly_fields = ("last_success_at", "last_error")


@admin.register(ExchangeRateSnapshot)
class ExchangeRateSnapshotAdmin(admin.ModelAdmin):
    list_display = ("provider", "currency", "sell_rate_toman", "local_date", "observed_at")
    list_filter = ("provider", "currency", "local_date")
    readonly_fields = ("provider", "currency", "sell_rate_toman", "local_date", "observed_at", "raw_payload")
    date_hierarchy = "observed_at"

    def has_add_permission(self, request):
        return False


@admin.register(MaterialMarketPriceSnapshot)
class MaterialMarketPriceSnapshotAdmin(admin.ModelAdmin):
    list_display = ("material", "bambu_usd_price", "fx_current_toman", "fx_daily_high_toman", "cost_per_gram_toman", "sale_per_gram_toman", "observed_at")
    list_filter = ("material",)
    search_fields = ("material__name",)
    readonly_fields = tuple(field.name for field in MaterialMarketPriceSnapshot._meta.fields)
    date_hierarchy = "observed_at"

    def has_add_permission(self, request):
        return False


@admin.register(CatalogAutomationDashboard)
class CatalogAutomationDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/catalog_automation_dashboard/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def get_urls(self):
        custom_urls = [
            path(
                "queue-source/<int:schedule_id>/",
                self.admin_site.admin_view(self.queue_source_view),
                name="store_catalogautomationdashboard_queue_source",
            ),
            path(
                "queue-all/",
                self.admin_site.admin_view(self.queue_all_view),
                name="store_catalogautomationdashboard_queue_all",
            ),
            path(
                "process-queue/",
                self.admin_site.admin_view(self.process_queue_view),
                name="store_catalogautomationdashboard_process_queue",
            ),
            path(
                "refresh-fx/",
                self.admin_site.admin_view(self.refresh_fx_view),
                name="store_catalogautomationdashboard_refresh_fx",
            ),
            path(
                "refresh-materials/",
                self.admin_site.admin_view(self.refresh_materials_view),
                name="store_catalogautomationdashboard_refresh_materials",
            ),
            path(
                "run-scheduler/",
                self.admin_site.admin_view(self.run_scheduler_view),
                name="store_catalogautomationdashboard_run_scheduler",
            ),
        ]
        return custom_urls + super().get_urls()

    def _dashboard_redirect(self):
        return HttpResponseRedirect(
            reverse("admin:store_catalogautomationdashboard_changelist")
        )

    def _require_post(self, request):
        if request.method == "POST":
            return True
        self.message_user(
            request,
            "برای اجرای عملیات از دکمه‌های داخل داشبورد استفاده کنید.",
            level=messages.WARNING,
        )
        return False

    def queue_source_view(self, request, schedule_id):
        if not self._require_post(request):
            return self._dashboard_redirect()
        schedule = CatalogSourceSchedule.objects.select_related(
            "policy", "policy__source"
        ).filter(pk=schedule_id).first()
        if schedule is None:
            self.message_user(request, "منبع انتخاب‌شده پیدا نشد.", level=messages.ERROR)
            return self._dashboard_redirect()
        try:
            run = queue_catalog_source(
                schedule=schedule,
                actor=request.user,
                trigger="manual",
            )
            self.message_user(
                request,
                f"{schedule.policy.source.name} در صف قرار گرفت؛ شماره اجرا {run.pk}.",
                level=messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, str(exc), level=messages.ERROR)
        return self._dashboard_redirect()

    def queue_all_view(self, request):
        if not self._require_post(request):
            return self._dashboard_redirect()
        queued = 0
        skipped = 0
        schedules = CatalogSourceSchedule.objects.select_related(
            "policy", "policy__source"
        ).filter(enabled=True)
        for schedule in schedules:
            try:
                queue_catalog_source(
                    schedule=schedule,
                    actor=request.user,
                    trigger="manual",
                )
                queued += 1
            except Exception:
                skipped += 1
        level = messages.SUCCESS if queued else messages.WARNING
        self.message_user(
            request,
            f"{queued} منبع در صف قرار گرفت و {skipped} منبع به دلیل اجرای تکراری یا غیرفعال‌بودن رد شد.",
            level=level,
        )
        return self._dashboard_redirect()

    def process_queue_view(self, request):
        if not self._require_post(request):
            return self._dashboard_redirect()
        try:
            setting = CatalogAutomationSetting.load()
            runs = process_catalog_queue(limit=setting.process_batch_size)
            completed = sum(1 for run in runs if run.status in {"completed", "partial"})
            failed = sum(1 for run in runs if run.status == "failed")
            self.message_user(
                request,
                f"{len(runs)} Job پردازش شد؛ موفق/نسبی: {completed}، ناموفق: {failed}.",
                level=messages.SUCCESS if runs and not failed else messages.WARNING,
            )
        except Exception as exc:
            self.message_user(request, f"خطا در پردازش صف: {exc}", level=messages.ERROR)
        return self._dashboard_redirect()

    def refresh_fx_view(self, request):
        if not self._require_post(request):
            return self._dashboard_redirect()
        try:
            snapshots = refresh_fx_rates()
            if snapshots:
                self.message_user(
                    request,
                    f"{len(snapshots)} نرخ دلار معتبر ثبت شد.",
                    level=messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    "هیچ نرخ معتبری ثبت نشد؛ منبع نرخ ارز و کلیدهای محیطی را بررسی کنید.",
                    level=messages.WARNING,
                )
        except Exception as exc:
            self.message_user(request, f"خطا در بروزرسانی نرخ دلار: {exc}", level=messages.ERROR)
        return self._dashboard_redirect()

    def refresh_materials_view(self, request):
        if not self._require_post(request):
            return self._dashboard_redirect()
        try:
            results, errors = refresh_material_market_prices(refresh_bambu=True)
            level = messages.SUCCESS if results and not errors else messages.WARNING
            self.message_user(
                request,
                f"قیمت {len(results)} متریال بروزرسانی شد؛ خطا: {len(errors)}.",
                level=level,
            )
            for error in errors[:5]:
                self.message_user(request, error, level=messages.ERROR)
        except Exception as exc:
            self.message_user(request, f"خطا در بروزرسانی متریال‌ها: {exc}", level=messages.ERROR)
        return self._dashboard_redirect()

    def run_scheduler_view(self, request):
        if not self._require_post(request):
            return self._dashboard_redirect()
        try:
            queued = queue_due_catalog_sources()
            setting = CatalogAutomationSetting.load()
            processed = process_catalog_queue(limit=setting.process_batch_size)
            self.message_user(
                request,
                f"بررسی زمان‌بندی انجام شد؛ {len(queued)} Job جدید و {len(processed)} Job پردازش شد.",
                level=messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"خطا در اجرای اتوماسیون: {exc}", level=messages.ERROR)
        return self._dashboard_redirect()

    def changelist_view(self, request, extra_context=None):
        from django.db.models import Max
        context = {
            "title": "داشبورد همگام‌سازی، انتشار و قیمت زنده",
            "schedules": CatalogSourceSchedule.objects.select_related("policy", "policy__source").order_by("policy__source__name"),
            "queued_count": CatalogSyncRun.objects.filter(status="queued").count(),
            "running_count": CatalogSyncRun.objects.filter(status="running").count(),
            "public_count": CatalogAssetPublication.objects.filter(show_on_homepage=True, metrics__public_approved=True).count(),
            "latest_fx": ExchangeRateSnapshot.objects.order_by("-observed_at", "-id").first(),
            "today_high_fx": ExchangeRateSnapshot.objects.filter(local_date=timezone.localdate()).aggregate(value=Max("sell_rate_toman"))["value"],
            "market_setting": MarketPricingSetting.load(),
            "recent_prices": MaterialMarketPriceSnapshot.objects.select_related("material")[:10],
            "recent_runs": CatalogSyncRun.objects.select_related("source").order_by("-created_at")[:10],
        }
        if extra_context:
            context.update(extra_context)
        return super().changelist_view(request, extra_context=context)
# END PHASE 10 AUTOMATION AND MARKET PRICING ADMIN

# BEGIN PHASE 11 SOURCE TESTING AND TGJU/BAMBU ADMIN
from django.db.models import Max as _phase11_Max
from django.http import HttpResponseRedirect as _phase11_HttpResponseRedirect
from django.urls import path as _phase11_path, reverse as _phase11_reverse

from .market_pricing import (
    refresh_fx_rates as _phase11_refresh_fx_rates,
    refresh_material_market_prices as _phase11_refresh_material_market_prices,
    sync_bambu_collection as _phase11_sync_bambu_collection,
    test_bambu_collection as _phase11_test_bambu_collection,
    test_exchange_provider as _phase11_test_exchange_provider,
    effective_fx_rates,
)
from .source_probes import test_catalog_source as _phase11_test_catalog_source
from .models import BambuFilamentCatalogItem, ExternalSourceFetchLog


@admin.register(ExternalSourceFetchLog)
class ExternalSourceFetchLogAdmin(admin.ModelAdmin):
    list_display = (
        "source_key", "action", "status", "progress_percent", "current_stage",
        "http_status", "duration_ms", "records_found", "records_saved",
        "records_updated", "created_at",
    )
    list_filter = ("source_key", "action", "status", "created_at")
    search_fields = ("message", "error", "current_stage")
    readonly_fields = tuple(field.name for field in ExternalSourceFetchLog._meta.fields)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BambuFilamentCatalogItem)
class BambuFilamentCatalogItemAdmin(admin.ModelAdmin):
    list_display = (
        "title", "conservative_price_usd", "min_price_usd", "max_price_usd",
        "available", "is_active", "last_seen_at", "official_link",
    )
    list_filter = ("available", "is_active", "product_type")
    search_fields = ("title", "handle", "vendor", "product_type")
    readonly_fields = tuple(field.name for field in BambuFilamentCatalogItem._meta.fields)
    date_hierarchy = "last_seen_at"

    @admin.display(description="صفحه رسمی")
    def official_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">مشاهده</a>', obj.product_url)

    def has_add_permission(self, request):
        return False


_phase11_old_get_urls = CatalogAutomationDashboardAdmin.get_urls


def _phase11_dashboard_redirect():
    return _phase11_HttpResponseRedirect(
        _phase11_reverse("admin:store_catalogautomationdashboard_changelist")
    )


def _phase11_require_post(self, request):
    if request.method == "POST":
        return True
    self.message_user(request, "عملیات فقط از دکمه‌های امن داخل داشبورد اجرا می‌شود.", level=messages.WARNING)
    return False


def _phase11_test_tgju_view(self, request):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    provider = ExchangeRateProvider.objects.filter(code="tgju-dollar").first()
    if provider is None:
        self.message_user(request, "منبع TGJU در دیتابیس پیدا نشد؛ Migration فاز ۱۱ را اجرا کنید.", level=messages.ERROR)
        return _phase11_dashboard_redirect()
    try:
        rate, payload, log = _phase11_test_exchange_provider(provider, actor=request.user)
        high = payload.get("daily_high_toman") if isinstance(payload, dict) else None
        self.message_user(request, f"تست TGJU موفق بود؛ نرخ فعلی {rate:,.0f} تومان، سقف روز {high or '-'}، گزارش #{log.pk}.", level=messages.SUCCESS)
    except Exception as exc:
        self.message_user(request, f"تست TGJU ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase11_fetch_tgju_view(self, request):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    try:
        snapshots = _phase11_refresh_fx_rates(actor=request.user)
        self.message_user(request, f"{len(snapshots)} نرخ معتبر ثبت شد.", level=messages.SUCCESS if snapshots else messages.WARNING)
    except Exception as exc:
        self.message_user(request, f"دریافت TGJU ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase11_test_bambu_view(self, request):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    try:
        records, meta, log = _phase11_test_bambu_collection(actor=request.user)
        self.message_user(request, f"تست Bambu موفق بود؛ {len(records)} محصول، روش {meta.get('mode')}، گزارش #{log.pk}.", level=messages.SUCCESS)
    except Exception as exc:
        self.message_user(request, f"تست Bambu ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase11_sync_bambu_view(self, request):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    try:
        records, log = _phase11_sync_bambu_collection(actor=request.user)
        self.message_user(request, f"کاتالوگ Bambu بروزرسانی شد؛ {len(records)} محصول، گزارش #{log.pk}.", level=messages.SUCCESS)
    except Exception as exc:
        self.message_user(request, f"همگام‌سازی Bambu ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase11_test_catalog_view(self, request, schedule_id):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    schedule = CatalogSourceSchedule.objects.select_related("policy", "policy__source").filter(pk=schedule_id).first()
    if schedule is None:
        self.message_user(request, "منبع انتخاب‌شده پیدا نشد.", level=messages.ERROR)
        return _phase11_dashboard_redirect()
    try:
        record, log = _phase11_test_catalog_source(schedule.policy, actor=request.user)
        self.message_user(request, f"تست {schedule.policy.source.name} موفق بود؛ نمونه «{record.get('title', '-')}»، گزارش #{log.pk}.", level=messages.SUCCESS)
    except Exception as exc:
        self.message_user(request, f"تست {schedule.policy.source.name} ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase11_refresh_all_prices_view(self, request):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    try:
        snapshots = _phase11_refresh_fx_rates(actor=request.user)
        results, errors = _phase11_refresh_material_market_prices(refresh_bambu=True, actor=request.user)
        self.message_user(request, f"نرخ‌ها: {len(snapshots)}؛ متریال بروزشده: {len(results)}؛ خطا: {len(errors)}.", level=messages.SUCCESS if results else messages.WARNING)
        for error in errors[:8]:
            self.message_user(request, error, level=messages.ERROR)
    except Exception as exc:
        self.message_user(request, f"بروزرسانی کامل قیمت‌ها ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase11_get_urls(self):
    urls = [
        _phase11_path("test-tgju/", self.admin_site.admin_view(self.test_tgju_view), name="store_catalogautomationdashboard_test_tgju"),
        _phase11_path("fetch-tgju/", self.admin_site.admin_view(self.fetch_tgju_view), name="store_catalogautomationdashboard_fetch_tgju"),
        _phase11_path("test-bambu/", self.admin_site.admin_view(self.test_bambu_view), name="store_catalogautomationdashboard_test_bambu"),
        _phase11_path("sync-bambu/", self.admin_site.admin_view(self.sync_bambu_view), name="store_catalogautomationdashboard_sync_bambu"),
        _phase11_path("test-catalog/<int:schedule_id>/", self.admin_site.admin_view(self.test_catalog_view), name="store_catalogautomationdashboard_test_catalog"),
        _phase11_path("refresh-all-prices/", self.admin_site.admin_view(self.refresh_all_prices_view), name="store_catalogautomationdashboard_refresh_all_prices"),
    ]
    return urls + _phase11_old_get_urls(self)


def _phase11_changelist_view(self, request, extra_context=None):
    context = {
        "title": "مرکز کنترل دریافت داده، تست منابع و قیمت زنده",
        "schedules": CatalogSourceSchedule.objects.select_related("policy", "policy__source").order_by("policy__source__name"),
        "queued_count": CatalogSyncRun.objects.filter(status="queued").count(),
        "running_count": CatalogSyncRun.objects.filter(status="running").count(),
        "public_count": CatalogAssetPublication.objects.filter(show_on_homepage=True, metrics__public_approved=True).count(),
        "latest_fx": ExchangeRateSnapshot.objects.order_by("-observed_at", "-id").first(),
        "today_high_fx": effective_fx_rates()[1],
        "market_setting": MarketPricingSetting.load(),
        "recent_prices": MaterialMarketPriceSnapshot.objects.select_related("material")[:10],
        "recent_runs": CatalogSyncRun.objects.select_related("source").order_by("-created_at")[:10],
        "recent_source_logs": ExternalSourceFetchLog.objects.select_related("created_by")[:20],
        "bambu_count": BambuFilamentCatalogItem.objects.filter(is_active=True).count(),
        "tgju_provider": ExchangeRateProvider.objects.filter(code="tgju-dollar").first(),
    }
    if extra_context:
        context.update(extra_context)
    return super(CatalogAutomationDashboardAdmin, self).changelist_view(request, extra_context=context)


CatalogAutomationDashboardAdmin.test_tgju_view = _phase11_test_tgju_view
CatalogAutomationDashboardAdmin.fetch_tgju_view = _phase11_fetch_tgju_view
CatalogAutomationDashboardAdmin.test_bambu_view = _phase11_test_bambu_view
CatalogAutomationDashboardAdmin.sync_bambu_view = _phase11_sync_bambu_view
CatalogAutomationDashboardAdmin.test_catalog_view = _phase11_test_catalog_view
CatalogAutomationDashboardAdmin.refresh_all_prices_view = _phase11_refresh_all_prices_view
CatalogAutomationDashboardAdmin.get_urls = _phase11_get_urls
CatalogAutomationDashboardAdmin.changelist_view = _phase11_changelist_view

# توضیحات کامل‌تر برای تنظیمات قیمت بازار
MarketPricingSettingAdmin.fieldsets = (
    ("فعال‌سازی و سیاست نرخ", {"fields": ("enabled", "refresh_fx_on_public_request", "use_daily_high_fx"), "description": "مشتری فقط قیمت نهایی هر گرم را می‌بیند. نرخ فعلی و سقف روز فقط در پنل مدیریت ذخیره می‌شود."}),
    ("منابع رسمی", {"fields": ("tgju_profile_url", "bambu_collection_url", "source_timeout_seconds"), "description": "TGJU برای دلار آزاد و فروشگاه آمریکا Bambu Lab برای قیمت دلاری فیلامنت استفاده می‌شود. آدرس‌ها فقط باید HTTPS و روی دامنه‌های مجاز باشند."}),
    ("دوره بروزرسانی", {"fields": ("refresh_fx_minutes", "refresh_bambu_hours")}),
    ("فرمول عمومی", {"fields": ("default_import_cost_percent", "default_margin_percent", "price_rounding_toman"), "description": "بهای هر گرم = قیمت محافظه‌کارانه دلاری × بیشترین نرخ دلار روز × هزینه واردات ÷ وزن رول؛ سپس حاشیه فروش اعمال می‌شود."}),
    ("وضعیت", {"fields": ("last_fx_refresh_at", "last_bambu_catalog_sync_at", "last_bambu_refresh_at", "last_error", "updated_at")}),
)
MarketPricingSettingAdmin.readonly_fields = ("last_fx_refresh_at", "last_bambu_catalog_sync_at", "last_bambu_refresh_at", "last_error", "updated_at")
# END PHASE 11 SOURCE TESTING AND TGJU/BAMBU ADMIN

# BEGIN PHASE 12 RESILIENT SOURCE ADMIN
from .models import CatalogSeedURL


@admin.register(CatalogSeedURL)
class CatalogSeedURLAdmin(admin.ModelAdmin):
    list_display = ("source", "label", "short_url", "priority", "is_active", "last_status", "last_checked_at")
    list_filter = ("source", "is_active", "last_status")
    search_fields = ("label", "url", "source__name", "source__code")
    ordering = ("source", "priority", "id")
    fieldsets = (
        ("منبع و لینک", {
            "fields": ("source", "url", "label", "priority", "is_active"),
            "description": (
                "برای منابعی مانند MakerWorld یا GrabCAD که فهرست خودکار را با 403 می‌بندند، "
                "یک لینک عمومی و مشخص از صفحه مدل ثبت کنید. سیستم فقط همان صفحه عمومی را بررسی می‌کند "
                "و هیچ ورود، CAPTCHA یا محدودیت امنیتی را دور نمی‌زند."
            ),
        }),
        ("نتیجه آخرین بررسی", {"fields": ("last_status", "last_error", "last_checked_at")}),
    )
    readonly_fields = ("last_status", "last_error", "last_checked_at")

    @admin.display(description="لینک")
    def short_url(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">مشاهده صفحه عمومی</a>', obj.url)


_phase12_old_test_catalog_view = CatalogAutomationDashboardAdmin.test_catalog_view


def _phase12_test_catalog_view(self, request, schedule_id):
    if not _phase11_require_post(self, request):
        return _phase11_dashboard_redirect()
    schedule = CatalogSourceSchedule.objects.select_related("policy", "policy__source").filter(pk=schedule_id).first()
    if schedule is None:
        self.message_user(request, "منبع انتخاب‌شده پیدا نشد.", level=messages.ERROR)
        return _phase11_dashboard_redirect()
    try:
        record, log = _phase11_test_catalog_source(schedule.policy, actor=request.user)
        status = record.get("_probe_status", "success")
        if status == "success":
            self.message_user(
                request,
                f"تست {schedule.policy.source.name} موفق بود؛ نمونه «{record.get('title', '-')}»، گزارش #{log.pk}.",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                f"وضعیت {schedule.policy.source.name}: {record.get('title', '-')} — گزارش #{log.pk}.",
                level=messages.WARNING,
            )
    except Exception as exc:
        self.message_user(request, f"تست {schedule.policy.source.name} ناموفق: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


CatalogAutomationDashboardAdmin.test_catalog_view = _phase12_test_catalog_view
# END PHASE 12 RESILIENT SOURCE ADMIN

# BEGIN PHASE 15 CATALOG POPULATION ADMIN
from django.urls import path as _phase15_path

from .catalog_population import (
    PUBLIC_SOURCE_KEYS as _phase15_PUBLIC_SOURCE_KEYS,
    catalog_population_counts as _phase15_catalog_population_counts,
    configure_population_schedule as _phase15_configure_population_schedule,
    publish_existing_catalog as _phase15_publish_existing_catalog,
)

_phase15_old_get_urls = CatalogAutomationDashboardAdmin.get_urls
_phase15_old_changelist_view = CatalogAutomationDashboardAdmin.changelist_view


def _phase15_prepare_population_view(self, request):
    if request.method != "POST":
        self.message_user(request, "عملیات فقط با دکمه امن داشبورد اجرا می‌شود.", level=messages.WARNING)
        return _phase11_dashboard_redirect()
    try:
        requested_limit = max(10, min(int(request.POST.get("limit") or 80), 500))
    except (TypeError, ValueError):
        requested_limit = 80
    queued = 0
    skipped = 0
    for source_key in _phase15_PUBLIC_SOURCE_KEYS:
        policy = CatalogSourcePolicy.objects.select_related("source").filter(source_kind=source_key).first()
        if policy is None:
            skipped += 1
            continue
        schedule = _phase15_configure_population_schedule(policy, requested_limit=requested_limit)
        try:
            queue_catalog_source(schedule=schedule, actor=request.user, trigger="manual")
            queued += 1
        except Exception:
            skipped += 1
    self.message_user(
        request,
        (
            f"دریافت واقعی برای {queued} منبع در صف قرار گرفت؛ {skipped} منبع رد شد. "
            "اکنون «پردازش صف الآن» را بزنید یا Worker زمان‌بندی‌شده را اجرا کنید."
        ),
        level=messages.SUCCESS if queued else messages.WARNING,
    )
    return _phase11_dashboard_redirect()


def _phase15_publish_existing_view(self, request):
    if request.method != "POST":
        self.message_user(request, "عملیات فقط با POST مجاز است.", level=messages.WARNING)
        return _phase11_dashboard_redirect()
    try:
        results = _phase15_publish_existing_catalog(
            publish_limit_per_source=300,
            actor=request.user,
        )
        published = sum(item["published"] for item in results)
        cached = sum(item["images_cached"] for item in results)
        errors = sum(len(item["errors"]) for item in results)
        self.message_user(
            request,
            f"مدل منتشرشده: {published}، تصویر محلی جدید: {cached}، خطا: {errors}.",
            level=messages.SUCCESS if published else messages.WARNING,
        )
    except Exception as exc:
        self.message_user(request, f"انتشار مدل‌های موجود ناموفق بود: {exc}", level=messages.ERROR)
    return _phase11_dashboard_redirect()


def _phase15_get_urls(self):
    urls = [
        _phase15_path(
            "prepare-population/",
            self.admin_site.admin_view(self.prepare_population_view),
            name="store_catalogautomationdashboard_prepare_population",
        ),
        _phase15_path(
            "publish-existing/",
            self.admin_site.admin_view(self.publish_existing_view),
            name="store_catalogautomationdashboard_publish_existing",
        ),
    ]
    return urls + _phase15_old_get_urls(self)


def _phase15_changelist_view(self, request, extra_context=None):
    context = dict(extra_context or {})
    context["population_counts"] = _phase15_catalog_population_counts()
    return _phase15_old_changelist_view(self, request, extra_context=context)


CatalogAutomationDashboardAdmin.prepare_population_view = _phase15_prepare_population_view
CatalogAutomationDashboardAdmin.publish_existing_view = _phase15_publish_existing_view
CatalogAutomationDashboardAdmin.get_urls = _phase15_get_urls
CatalogAutomationDashboardAdmin.changelist_view = _phase15_changelist_view
# END PHASE 15 CATALOG POPULATION ADMIN

# BEGIN PHASE 16 CATALOG RANKING AND BAMBU HISTORY ADMIN
from django.contrib import admin as _phase16_admin
from django.urls import reverse as _phase16_reverse
from django.utils.html import format_html as _phase16_format_html
from urllib.parse import urlencode as _phase16_urlencode

from .models import (
    BambuFilamentPriceHistory as _phase16_BambuFilamentPriceHistory,
    ImportedPrintAsset as _phase16_ImportedPrintAsset,
    BambuFilamentCatalogItem as _phase16_BambuFilamentCatalogItem,
)

_phase16_imported_admin_instance = _phase16_admin.site._registry[_phase16_ImportedPrintAsset]
_phase16_imported_admin_class = _phase16_imported_admin_instance.__class__
if _phase16_imported_admin_class is _phase16_admin.ModelAdmin:
    _phase16_admin.site.unregister(_phase16_ImportedPrintAsset)

    class _Phase16ImportedPrintAssetAdmin(_phase16_admin.ModelAdmin):
        search_fields = ("title", "description", "author_name", "source_url", "external_id")

    _phase16_admin.site.register(_phase16_ImportedPrintAsset, _Phase16ImportedPrintAssetAdmin)
    _phase16_imported_admin_class = _Phase16ImportedPrintAssetAdmin

_phase16_bambu_admin_class = _phase16_admin.site._registry[_phase16_BambuFilamentCatalogItem].__class__


def _phase16_metrics(obj):
    try:
        return obj.metrics
    except Exception:
        return None


@_phase16_admin.display(ordering="metrics__views_count", description="بازدید منبع")
def _phase16_asset_views(self, obj):
    row = _phase16_metrics(obj)
    return f"{row.views_count:,}" if row else "-"


@_phase16_admin.display(ordering="metrics__downloads_count", description="دانلود")
def _phase16_asset_downloads(self, obj):
    row = _phase16_metrics(obj)
    return f"{row.downloads_count:,}" if row else "-"


@_phase16_admin.display(ordering="metrics__likes_count", description="لایک")
def _phase16_asset_likes(self, obj):
    row = _phase16_metrics(obj)
    return f"{row.likes_count:,}" if row else "-"


@_phase16_admin.display(ordering="metrics__popularity_rank", description="رتبه محبوبیت")
def _phase16_asset_rank(self, obj):
    row = _phase16_metrics(obj)
    return row.popularity_rank if row and row.popularity_rank else "-"


@_phase16_admin.display(boolean=True, ordering="metrics__public_approved", description="منتشر")
def _phase16_asset_public(self, obj):
    row = _phase16_metrics(obj)
    return bool(row and row.public_approved)


@_phase16_admin.display(description="مجوز")
def _phase16_asset_license(self, obj):
    row = _phase16_metrics(obj)
    if not row:
        return "-"
    if row.license_review_status == "allowed" and row.commercial_use_allowed is True:
        return _phase16_format_html('<strong style="color:#15803d">{}</strong>', 'مجاز تجاری')
    if row.license_review_status == "blocked":
        return _phase16_format_html('<strong style="color:#b91c1c">{}</strong>', 'مسدود')
    return _phase16_format_html('<span style="color:#a16207">{}</span>', 'نیازمند بررسی')


@_phase16_admin.display(boolean=True, description="فایل/لینک خصوصی")
def _phase16_has_private_download(self, obj):
    specs = obj.technical_specs or {}
    return bool(
        obj.private_download_url
        or specs.get("source_file_available")
        or specs.get("source_file_reference")
    )


_phase16_old_asset_queryset = _phase16_imported_admin_class.get_queryset


def _phase16_asset_queryset(self, request):
    queryset = _phase16_old_asset_queryset(self, request).select_related("metrics", "source")
    ordering = request.GET.get("o")
    if not ordering:
        queryset = queryset.order_by(
            "-metrics__views_count",
            "-metrics__downloads_count",
            "-metrics__likes_count",
            "id",
        )
    return queryset


_phase16_imported_admin_class.source_views = _phase16_asset_views
_phase16_imported_admin_class.source_downloads = _phase16_asset_downloads
_phase16_imported_admin_class.source_likes = _phase16_asset_likes
_phase16_imported_admin_class.source_popularity_rank = _phase16_asset_rank
_phase16_imported_admin_class.is_publicly_approved = _phase16_asset_public
_phase16_imported_admin_class.has_private_download = _phase16_has_private_download
_phase16_imported_admin_class.license_summary = _phase16_asset_license
_phase16_imported_admin_class.get_queryset = _phase16_asset_queryset
_phase16_imported_admin_class.list_display = (
    "title",
    "source",
    "source_views",
    "source_downloads",
    "source_likes",
    "source_popularity_rank",
    "license_summary",
    "is_publicly_approved",
    "file_format",
    "has_private_download",
    "imported_at",
)
_phase16_imported_admin_class.list_filter = (
    "source",
    "metrics__source_kind",
    "metrics__license_review_status",
    "metrics__commercial_use_allowed",
    "metrics__public_approved",
    "status",
    "file_format",
    "imported_at",
)


def _phase16_latest_history(obj):
    cached = getattr(obj, "_phase16_latest_history_cache", None)
    if cached is not None:
        return cached
    row = obj.price_history.order_by("-observed_at", "-id").first()
    obj._phase16_latest_history_cache = row
    return row


@_phase16_admin.display(ordering="conservative_price_usd", description="قیمت جدید")
def _phase16_current_price(self, obj):
    return f"${obj.conservative_price_usd:,.2f}"


@_phase16_admin.display(description="قیمت قبلی")
def _phase16_previous_price(self, obj):
    row = _phase16_latest_history(obj)
    if row is None or row.previous_conservative_price_usd is None:
        return "-"
    return f"${row.previous_conservative_price_usd:,.2f}"


@_phase16_admin.display(description="تغییر")
def _phase16_price_change(self, obj):
    row = _phase16_latest_history(obj)
    if row is None or row.previous_conservative_price_usd is None:
        return "-"
    if row.delta_usd > 0:
        color, arrow = "#b91c1c", "▲"
    elif row.delta_usd < 0:
        color, arrow = "#15803d", "▼"
    else:
        color, arrow = "#64748b", "—"
    return _phase16_format_html(
        '<strong style="color:{}">{} ${} ({}٪)</strong>',
        color,
        arrow,
        f"{abs(row.delta_usd):,.2f}",
        f"{row.delta_percent:,.2f}",
    )


@_phase16_admin.display(description="تاریخچه")
def _phase16_price_history_link(self, obj):
    url = _phase16_reverse("admin:store_bambufilamentpricehistory_changelist")
    query = _phase16_urlencode({"item__id__exact": obj.pk})
    return _phase16_format_html('<a href="{}?{}">مشاهده همه تغییرات</a>', url, query)


_phase16_bambu_admin_class.current_price_admin = _phase16_current_price
_phase16_bambu_admin_class.previous_price_admin = _phase16_previous_price
_phase16_bambu_admin_class.price_change_admin = _phase16_price_change
_phase16_bambu_admin_class.price_history_link = _phase16_price_history_link
_phase16_bambu_admin_class.list_display = (
    "title",
    "current_price_admin",
    "previous_price_admin",
    "price_change_admin",
    "min_price_usd",
    "max_price_usd",
    "available",
    "last_seen_at",
    "price_history_link",
    "official_link",
)
_phase16_bambu_admin_class.list_filter = (
    "available",
    "is_active",
    "product_type",
    "last_seen_at",
)


@_phase16_admin.register(_phase16_BambuFilamentPriceHistory)
class BambuFilamentPriceHistoryAdmin(_phase16_admin.ModelAdmin):
    list_display = (
        "item",
        "previous_conservative_price_usd",
        "conservative_price_usd",
        "delta_usd",
        "delta_percent",
        "changed",
        "available",
        "source_mode",
        "observed_at",
    )
    list_filter = ("changed", "available", "source_mode", "observed_at")
    search_fields = ("item__title", "item__handle")
    readonly_fields = tuple(field.name for field in _phase16_BambuFilamentPriceHistory._meta.fields)
    date_hierarchy = "observed_at"
    list_select_related = ("item",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
# END PHASE 16 CATALOG RANKING AND BAMBU HISTORY ADMIN

# BEGIN PHASE 17 CATALOG PREVIEW ADMIN
from django.contrib import admin as _phase17_admin
from django.contrib import messages as _phase17_messages
from django.urls import reverse as _phase17_reverse
from django.utils.html import format_html as _phase17_format_html
from django.utils.html import format_html_join as _phase17_format_html_join

from .catalog_preview import refresh_assets as _phase17_refresh_assets
from .models import (
    ImportedPrintAsset as _phase17_ImportedPrintAsset,
    ImportedPrintAssetImage as _phase17_ImportedPrintAssetImage,
    ImportedPrintAssetPrintProfile as _phase17_ImportedPrintAssetPrintProfile,
)


def _phase17_preview_url(obj):
    if obj.preview_image:
        try:
            return obj.preview_image.url
        except Exception:
            pass
    for row in obj.images.all():
        if row.image:
            try:
                return row.image.url
            except Exception:
                pass
    return obj.remote_image_url or ""


@_phase17_admin.display(description="پیش‌نمایش")
def _phase17_preview_thumbnail(self, obj):
    url = _phase17_preview_url(obj)
    if not url:
        return "بدون تصویر"
    change_url = _phase17_reverse("admin:store_importedprintasset_change", args=[obj.pk])
    return _phase17_format_html(
        '<a href="{}"><img src="{}" alt="{}" loading="lazy" '
        'style="width:88px;height:68px;object-fit:cover;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.16)"></a>',
        change_url,
        url,
        obj.title,
    )


@_phase17_admin.display(description="توضیحات")
def _phase17_description_excerpt(self, obj):
    text = (obj.short_description or obj.description or "").strip().replace("\n", " ")
    if not text:
        return "ثبت نشده"
    return text[:110] + ("…" if len(text) > 110 else "")


@_phase17_admin.display(description="وزن‌های چاپ")
def _phase17_weight_summary(self, obj):
    values = []
    for profile in obj.print_profiles.all():
        if profile.is_active and profile.weight_grams is not None:
            number = f"{profile.weight_grams.normalize():f}".rstrip("0").rstrip(".")
            values.append(f"{number} گرم")
    values = list(dict.fromkeys(values))
    if values:
        shown = values[:4]
        suffix = f" +{len(values) - 4}" if len(values) > 4 else ""
        return "، ".join(shown) + suffix
    try:
        weight = obj.metrics.estimated_weight_grams
    except Exception:
        weight = None
    if weight is not None:
        return f"{weight} گرم"
    return "نامشخص؛ قابل ثبت دستی"


@_phase17_admin.display(description="تصاویر")
def _phase17_image_count(self, obj):
    local_count = sum(1 for row in obj.images.all() if row.image)
    total = len(list(obj.images.all()))
    return f"{local_count} محلی / {total} کل"


@_phase17_admin.display(description="صفحه منبع")
def _phase17_source_page(self, obj):
    return _phase17_format_html(
        '<a href="{}" target="_blank" rel="noopener noreferrer">بازکردن صفحه اصلی</a>',
        obj.source_url,
    )


@_phase17_admin.display(description="گالری پیش‌نمایش")
def _phase17_preview_gallery(self, obj):
    rows = []
    preview = _phase17_preview_url(obj)
    if preview:
        rows.append((preview, preview, obj.title))
    for image in obj.images.all():
        url = ""
        if image.image:
            try:
                url = image.image.url
            except Exception:
                url = ""
        if not url:
            url = image.remote_url or ""
        if url and url not in {item[0] for item in rows}:
            rows.append((url, url, image.alt_text or obj.title))
    if not rows:
        return "هنوز تصویری دریافت نشده است. از عملیات «دریافت تصاویر و اطلاعات» استفاده کنید."
    return _phase17_format_html_join(
        " ",
        '<a href="{}" target="_blank" rel="noopener"><img src="{}" alt="{}" loading="lazy" '
        'style="width:150px;height:110px;object-fit:cover;border-radius:12px;margin:4px;border:1px solid #d1d5db"></a>',
        rows,
    )


@_phase17_admin.action(description="دریافت/بروزرسانی تصاویر، توضیحات و وزن‌های انتخاب‌شده")
def _phase17_refresh_selected(modeladmin, request, queryset):
    results, errors = _phase17_refresh_assets(queryset, download_images=True, max_images=20)
    downloaded = sum(item.images_downloaded for item in results)
    profiles = sum(item.profiles_found for item in results)
    modeladmin.message_user(
        request,
        f"{len(results)} مدل بروزرسانی شد؛ {downloaded} تصویر محلی و {profiles} پروفایل وزن ثبت شد.",
        level=_phase17_messages.SUCCESS if results else _phase17_messages.WARNING,
    )
    for error in errors[:10]:
        modeladmin.message_user(request, error, level=_phase17_messages.ERROR)
    if len(errors) > 10:
        modeladmin.message_user(request, f"{len(errors) - 10} خطای دیگر نیز ثبت شد.", level=_phase17_messages.WARNING)


class _Phase17ImportedPrintAssetImageInline(_phase17_admin.TabularInline):
    model = _phase17_ImportedPrintAssetImage
    verbose_name = "تصویر پیش‌نمایش"
    verbose_name_plural = "گالری پیش‌نمایش"
    verbose_name = "تصویر پیش‌نمایش"
    verbose_name_plural = "گالری پیش‌نمایش"
    extra = 0
    fields = ("inline_preview", "image", "remote_url", "alt_text", "sort_order")
    readonly_fields = ("inline_preview",)
    ordering = ("sort_order", "id")

    @_phase17_admin.display(description="تصویر")
    def inline_preview(self, obj):
        if not obj or not obj.pk:
            return "-"
        url = ""
        if obj.image:
            try:
                url = obj.image.url
            except Exception:
                pass
        url = url or obj.remote_url
        if not url:
            return "-"
        return _phase17_format_html(
            '<img src="{}" alt="{}" style="width:92px;height:68px;object-fit:cover;border-radius:8px">',
            url,
            obj.alt_text or "پیش‌نمایش",
        )


class _Phase17ImportedPrintAssetPrintProfileInline(_phase17_admin.TabularInline):
    model = _phase17_ImportedPrintAssetPrintProfile
    extra = 1
    fields = (
        "profile_name",
        "weight_grams",
        "print_minutes",
        "material",
        "nozzle_mm",
        "layer_height_mm",
        "infill_percent",
        "is_manual",
        "is_active",
    )


_phase17_asset_admin = _phase17_admin.site._registry[_phase17_ImportedPrintAsset]
_phase17_asset_admin_class = _phase17_asset_admin.__class__
_phase17_previous_queryset = _phase17_asset_admin_class.get_queryset


def _phase17_asset_queryset(self, request):
    return _phase17_previous_queryset(self, request).prefetch_related("images", "print_profiles")


_phase17_asset_admin_class.get_queryset = _phase17_asset_queryset
_phase17_asset_admin_class.preview_thumbnail = _phase17_preview_thumbnail
_phase17_asset_admin_class.description_excerpt = _phase17_description_excerpt
_phase17_asset_admin_class.weight_summary = _phase17_weight_summary
_phase17_asset_admin_class.image_count_admin = _phase17_image_count
_phase17_asset_admin_class.source_page_admin = _phase17_source_page
_phase17_asset_admin_class.preview_gallery_admin = _phase17_preview_gallery
_phase17_asset_admin_class.list_display = (
    "preview_thumbnail",
    "title",
    "source",
    "description_excerpt",
    "weight_summary",
    "image_count_admin",
    "source_views",
    "source_downloads",
    "source_likes",
    "license_summary",
    "is_publicly_approved",
    "imported_at",
)
_phase17_asset_admin_class.list_display_links = ("title",)
_phase17_asset_admin_class.list_per_page = 50
_phase17_existing_inlines = tuple(getattr(_phase17_asset_admin_class, "inlines", ()) or ())
_phase17_asset_admin_class.inlines = tuple(
    inline
    for inline in _phase17_existing_inlines
    if getattr(inline, "model", None) not in {
        _phase17_ImportedPrintAssetImage,
        _phase17_ImportedPrintAssetPrintProfile,
    }
) + (
    _Phase17ImportedPrintAssetImageInline,
    _Phase17ImportedPrintAssetPrintProfileInline,
)
_phase17_asset_admin_class.readonly_fields = tuple(getattr(_phase17_asset_admin_class, "readonly_fields", ()) or ()) + (
    "preview_gallery_admin",
    "source_page_admin",
)
_phase17_asset_admin_class.actions = tuple(getattr(_phase17_asset_admin_class, "actions", ()) or ()) + (
    _phase17_refresh_selected,
)


if not _phase17_admin.site.is_registered(_phase17_ImportedPrintAssetImage):
    @_phase17_admin.register(_phase17_ImportedPrintAssetImage)
    class ImportedPrintAssetImageAdmin(_phase17_admin.ModelAdmin):
        list_display = ("thumbnail", "asset", "sort_order", "has_local_file", "remote_url")
        search_fields = ("asset__title", "alt_text", "remote_url")
        list_filter = ("asset__source",)
        list_select_related = ("asset", "asset__source")

        @_phase17_admin.display(description="پیش‌نمایش")
        def thumbnail(self, obj):
            url = ""
            if obj.image:
                try:
                    url = obj.image.url
                except Exception:
                    pass
            url = url or obj.remote_url
            if not url:
                return "-"
            return _phase17_format_html(
                '<img src="{}" alt="{}" loading="lazy" style="width:92px;height:68px;object-fit:cover;border-radius:8px">',
                url,
                obj.alt_text or obj.asset.title,
            )

        @_phase17_admin.display(boolean=True, description="فایل محلی")
        def has_local_file(self, obj):
            return bool(obj.image)


@_phase17_admin.register(_phase17_ImportedPrintAssetPrintProfile)
class ImportedPrintAssetPrintProfileAdmin(_phase17_admin.ModelAdmin):
    list_display = (
        "asset",
        "profile_name",
        "weight_grams",
        "print_minutes",
        "material",
        "nozzle_mm",
        "layer_height_mm",
        "infill_percent",
        "is_manual",
        "is_active",
    )
    list_filter = ("is_manual", "is_active", "material", "asset__source")
    search_fields = ("asset__title", "profile_name", "material")
    list_select_related = ("asset", "asset__source")
# END PHASE 17 CATALOG PREVIEW ADMIN

# BEGIN PHASE 23 RESILIENT CATALOG AND LINK INTELLIGENCE ADMIN
from django.contrib import messages as _phase23_messages
from django.utils import timezone as _phase23_timezone

from .link_analysis_queue import enqueue_link_analysis as _phase24_enqueue_link
from .link_intelligence import process_catalog_refresh_requests as _phase23_process_refresh
from .models import CatalogRefreshRequest as _Phase23CatalogRefreshRequest
from .models import CustomerLinkAnalysis as _Phase23CustomerLinkAnalysis


@admin.register(_Phase23CatalogRefreshRequest)
class CatalogRefreshRequestAdmin(admin.ModelAdmin):
    list_display = ("asset", "status", "requested_by", "requested_at", "processed_at", "short_result")
    list_filter = ("status", "asset__source", "requested_at")
    search_fields = ("asset__title", "asset__source_url", "customer_note", "result_summary")
    readonly_fields = ("requested_at", "processed_at")
    actions = ("process_selected",)
    list_select_related = ("asset", "asset__source", "requested_by")

    @admin.display(description="نتیجه")
    def short_result(self, obj):
        return (obj.result_summary or "-")[:100]

    @admin.action(description="پردازش درخواست‌های انتخاب‌شده/در انتظار")
    def process_selected(self, request, queryset):
        queryset.filter(status="failed").update(status="pending", processed_at=None)
        requested_ids = set(queryset.values_list("pk", flat=True))
        processed = _phase23_process_refresh(limit=max(len(requested_ids), 1), request_ids=requested_ids)
        done = sum(1 for item in processed if item.pk in requested_ids)
        self.message_user(request, f"{done} درخواست بروزرسانی پردازش شد.", level=_phase23_messages.SUCCESS)


@admin.register(_Phase23CustomerLinkAnalysis)
class CustomerLinkAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "preview", "title", "source_name", "status", "material", "estimated_weight_grams",
        "estimated_print_minutes", "estimated_price", "estimate_confidence", "user", "created_at",
    )
    list_display_links = ("title",)
    list_filter = ("status", "source_domain", "material", "created_at")
    search_fields = ("title", "source_url", "normalized_url", "source_name", "source_domain", "author_name")
    readonly_fields = (
        "public_token", "preview_large", "source_link", "source_payload", "file_links", "estimate_breakdown",
        "analysis_warnings", "error_message", "created_at", "analyzed_at", "updated_at",
    )
    raw_id_fields = ("user", "material", "related_asset", "order")
    actions = ("reanalyze_selected",)
    list_select_related = ("user", "material", "order")

    fieldsets = (
        ("منبع مشتری", {"fields": ("user", "session_key", "source_url", "normalized_url", "source_domain", "source_name", "source_link", "status")}),
        ("اطلاعات استخراج‌شده", {"fields": ("preview_large", "title", "short_description", "description", "author_name", "image_url", "cached_image", "image_urls", "tags", "technical_specs", "file_formats", "file_links", "source_payload")}),
        ("برآورد چاپ", {"fields": ("detected_material_name", "material", "estimated_weight_grams", "estimated_print_minutes", "quantity", "estimate_confidence", "estimated_price", "estimated_price_min", "estimated_price_max", "estimate_breakdown")}),
        ("گردش‌کار", {"fields": ("related_asset", "order", "analysis_warnings", "error_message", "created_at", "analyzed_at", "updated_at")}),
    )

    @admin.display(description="تصویر")
    def preview(self, obj):
        url = obj.display_image_url
        if not url:
            return "-"
        return format_html('<img src="{}" alt="" style="width:76px;height:58px;object-fit:cover;border-radius:8px" loading="lazy">', url)

    @admin.display(description="پیش‌نمایش")
    def preview_large(self, obj):
        url = obj.display_image_url
        if not url:
            return "تصویر موجود نیست"
        return format_html('<img src="{}" alt="" style="max-width:520px;max-height:380px;object-fit:contain;border-radius:12px;background:#eef2f6">', url)

    @admin.display(description="صفحه منبع")
    def source_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">بازکردن منبع ↗</a>', obj.normalized_url or obj.source_url)

    @admin.action(description="افزودن تحلیل‌های انتخاب‌شده به صف پردازش")
    def reanalyze_selected(self, request, queryset):
        queued = 0
        skipped = 0
        for obj in queryset.exclude(status="converted"):
            try:
                _phase24_enqueue_link(obj, force=True, priority=130)
            except Exception:
                skipped += 1
            else:
                queued += 1
        self.message_user(request, f"صف تحلیل: {queued} مورد اضافه شد، {skipped} مورد رد شد.")
# END PHASE 23 RESILIENT CATALOG AND LINK INTELLIGENCE ADMIN

# BEGIN PHASE 24 ASYNC LINK ANALYSIS QUEUE ADMIN
from .models import CustomerLinkAnalysisAttempt as _Phase24LinkAttempt
from .models import CustomerLinkAnalysisJob as _Phase24LinkJob


class CustomerLinkAnalysisAttemptInline(admin.TabularInline):
    model = _Phase24LinkAttempt
    extra = 0
    can_delete = False
    fields = ("attempt_number", "status", "stage", "duration_ms", "worker_id", "started_at", "completed_at", "error_type")
    readonly_fields = fields
    ordering = ("-attempt_number",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(_Phase24LinkJob)
class CustomerLinkAnalysisJobAdmin(admin.ModelAdmin):
    list_display = (
        "id", "analysis", "adapter_key", "status", "progress_percent", "progress_stage", "attempt_count",
        "max_attempts", "next_run_at", "worker_id", "updated_at",
    )
    list_filter = ("status", "progress_stage", "created_at", "updated_at")
    search_fields = (
        "analysis__title", "analysis__source_url", "analysis__source_domain",
        "analysis__user__username", "worker_id", "last_error",
    )
    list_select_related = ("analysis", "analysis__user")
    readonly_fields = (
        "analysis", "adapter_key", "attempt_count", "progress_percent", "progress_stage", "progress_message",
        "locked_at", "worker_id", "last_error_type", "last_error", "last_started_at",
        "completed_at", "success_notified_at", "failure_notified_at", "created_at", "updated_at",
    )
    fields = (
        "analysis", "adapter_key", "status", "priority", "attempt_count", "max_attempts", "next_run_at",
        "progress_percent", "progress_stage", "progress_message", "locked_at", "worker_id",
        "last_error_type", "last_error", "last_started_at", "completed_at", "success_notified_at",
        "failure_notified_at", "created_at", "updated_at",
    )
    inlines = (CustomerLinkAnalysisAttemptInline,)
    actions = ("queue_again",)

    @admin.action(description="بازگردانی Jobهای انتخاب‌شده به صف")
    def queue_again(self, request, queryset):
        count = 0
        for job in queryset.select_related("analysis"):
            if job.analysis.status == "converted":
                continue
            _phase24_enqueue_link(job.analysis, force=True, priority=max(job.priority, 120))
            count += 1
        self.message_user(request, f"{count} Job دوباره وارد صف شد.")


@admin.register(_Phase24LinkAttempt)
class CustomerLinkAnalysisAttemptAdmin(admin.ModelAdmin):
    list_display = ("job", "attempt_number", "status", "stage", "duration_ms", "worker_id", "started_at", "completed_at")
    list_filter = ("status", "stage", "started_at")
    search_fields = ("job__analysis__title", "job__analysis__source_url", "worker_id", "error_type", "error_message")
    readonly_fields = (
        "job", "attempt_number", "status", "stage", "error_type", "error_message",
        "started_at", "completed_at", "duration_ms", "worker_id",
    )

    def has_add_permission(self, request):
        return False
# END PHASE 24 ASYNC LINK ANALYSIS QUEUE ADMIN

# BEGIN PHASE 25 LINK ANALYSIS OPERATIONS ADMIN
from datetime import timedelta as _phase25_timedelta

from django.contrib import messages as _phase25_messages
from django.http import HttpResponseRedirect as _phase25_HttpResponseRedirect, JsonResponse as _phase25_JsonResponse
from django.urls import path as _phase25_path, reverse as _phase25_reverse
from django.utils import timezone as _phase25_timezone

from .link_analysis_operations import (
    ensure_adapter_policies as _phase25_ensure_policies,
    health_payload as _phase25_health_payload,
    mark_stale_workers as _phase25_mark_stale_workers,
    queue_metrics as _phase25_queue_metrics,
)
from .link_analysis_queue import (
    process_link_analysis_queue as _phase25_process_queue,
    release_stale_link_analysis_jobs as _phase25_release_stale_jobs,
)
from .models import (
    LinkAnalysisAdapterPolicy as _Phase25AdapterPolicy,
    LinkAnalysisOperationsDashboard as _Phase25OperationsDashboard,
    LinkAnalysisQueueControl as _Phase25QueueControl,
    LinkAnalysisWorkerHeartbeat as _Phase25WorkerHeartbeat,
)


@admin.register(_Phase25QueueControl)
class LinkAnalysisQueueControlAdmin(admin.ModelAdmin):
    list_display = ("is_paused", "pause_reason", "heartbeat_timeout_seconds", "stale_lock_minutes", "default_batch_size", "updated_at")
    readonly_fields = ("singleton_key", "updated_by", "updated_at")
    fieldsets = (
        ("کنترل صف", {"fields": ("is_paused", "pause_reason", "default_batch_size", "default_sleep_seconds")}),
        ("سلامت Worker", {"fields": ("heartbeat_timeout_seconds", "stale_lock_minutes")}),
        ("اعلان مشتری", {"fields": ("notify_customer_on_success", "notify_customer_on_failure", "email_customer_on_success", "email_customer_on_failure")}),
        ("سیستم", {"fields": ("singleton_key", "updated_by", "updated_at")}),
    )

    def has_add_permission(self, request):
        return not _Phase25QueueControl.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
        _phase26_publish_operations()


@admin.register(_Phase25AdapterPolicy)
class LinkAnalysisAdapterPolicyAdmin(admin.ModelAdmin):
    list_display = (
        "adapter_key", "display_name", "is_enabled", "paused_until", "max_attempts",
        "request_timeout_seconds", "success_count", "failure_count", "consecutive_failure_count",
        "last_success_at", "last_failure_at",
    )
    list_filter = ("is_enabled", "adapter_key")
    search_fields = ("display_name", "adapter_key", "notes", "last_error")
    readonly_fields = ("success_count", "failure_count", "consecutive_failure_count", "last_success_at", "last_failure_at", "last_error", "created_at", "updated_at")
    actions = ("enable_selected", "disable_selected", "pause_one_hour", "resume_selected")

    @admin.action(description="فعال‌سازی Adapterهای انتخاب‌شده")
    def enable_selected(self, request, queryset):
        count = queryset.update(is_enabled=True, paused_until=None)
        _phase26_publish_operations()
        self.message_user(request, f"{count} Adapter فعال شد.", level=_phase25_messages.SUCCESS)

    @admin.action(description="غیرفعال‌سازی Adapterهای انتخاب‌شده")
    def disable_selected(self, request, queryset):
        count = queryset.update(is_enabled=False)
        _phase26_publish_operations()
        self.message_user(request, f"{count} Adapter غیرفعال شد.", level=_phase25_messages.WARNING)

    @admin.action(description="توقف Adapterها برای یک ساعت")
    def pause_one_hour(self, request, queryset):
        count = queryset.update(paused_until=_phase25_timezone.now() + _phase25_timedelta(hours=1))
        _phase26_publish_operations()
        self.message_user(request, f"{count} Adapter برای یک ساعت متوقف شد.", level=_phase25_messages.WARNING)

    @admin.action(description="ادامه فعالیت Adapterهای انتخاب‌شده")
    def resume_selected(self, request, queryset):
        count = queryset.update(is_enabled=True, paused_until=None)
        _phase26_publish_operations()
        self.message_user(request, f"{count} Adapter از حالت توقف خارج شد.", level=_phase25_messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        _phase26_publish_operations()


@admin.register(_Phase25WorkerHeartbeat)
class LinkAnalysisWorkerHeartbeatAdmin(admin.ModelAdmin):
    list_display = (
        "worker_id", "status", "hostname", "process_id", "current_job", "last_seen_at",
        "processed_count", "succeeded_count", "failed_count", "worker_version",
    )
    list_filter = ("status", "worker_version", "hostname")
    search_fields = ("worker_id", "hostname", "last_error")
    readonly_fields = tuple(field.name for field in _Phase25WorkerHeartbeat._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(_Phase25OperationsDashboard)
class LinkAnalysisOperationsDashboardAdmin(admin.ModelAdmin):
    change_list_template = "admin/store/link_analysis_operations_dashboard/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).none()

    def get_urls(self):
        return [
            _phase25_path("pause/", self.admin_site.admin_view(self.pause_view), name="store_linkanalysisoperationsdashboard_pause"),
            _phase25_path("resume/", self.admin_site.admin_view(self.resume_view), name="store_linkanalysisoperationsdashboard_resume"),
            _phase25_path("process-now/", self.admin_site.admin_view(self.process_now_view), name="store_linkanalysisoperationsdashboard_process_now"),
            _phase25_path("release-stale/", self.admin_site.admin_view(self.release_stale_view), name="store_linkanalysisoperationsdashboard_release_stale"),
            _phase25_path("retry-failed/", self.admin_site.admin_view(self.retry_failed_view), name="store_linkanalysisoperationsdashboard_retry_failed"),
            _phase25_path("adapter/<str:adapter_key>/toggle/", self.admin_site.admin_view(self.toggle_adapter_view), name="store_linkanalysisoperationsdashboard_toggle_adapter"),
            _phase25_path("health.json", self.admin_site.admin_view(self.health_view), name="store_linkanalysisoperationsdashboard_health"),
        ] + super().get_urls()

    def _redirect(self):
        return _phase25_HttpResponseRedirect(_phase25_reverse("admin:store_linkanalysisoperationsdashboard_changelist"))

    def _require_post(self, request):
        if request.method == "POST":
            return True
        self.message_user(request, "عملیات مدیریتی باید با POST اجرا شود.", level=_phase25_messages.WARNING)
        return False

    def pause_view(self, request):
        if not self._require_post(request):
            return self._redirect()
        control = _Phase25QueueControl.load()
        control.is_paused = True
        control.pause_reason = (request.POST.get("reason") or "توقف دستی از داشبورد")[:300]
        control.updated_by = request.user
        control.save()
        _phase26_publish_operations()
        self.message_user(request, "صف تحلیل لینک متوقف شد؛ Jobهای در حال اجرا کامل می‌شوند.", level=_phase25_messages.WARNING)
        return self._redirect()

    def resume_view(self, request):
        if not self._require_post(request):
            return self._redirect()
        control = _Phase25QueueControl.load()
        control.is_paused = False
        control.pause_reason = ""
        control.updated_by = request.user
        control.save()
        _phase26_publish_operations()
        self.message_user(request, "صف تحلیل لینک فعال شد.", level=_phase25_messages.SUCCESS)
        return self._redirect()

    def process_now_view(self, request):
        if not self._require_post(request):
            return self._redirect()
        limit = max(1, min(int(request.POST.get("limit") or 1), 10))
        jobs = _phase25_process_queue(limit=limit, worker_id=f"admin:{request.user.pk}")
        _phase26_publish_operations()
        self.message_user(request, f"{len(jobs)} Job از داخل پنل پردازش شد.", level=_phase25_messages.SUCCESS if jobs else _phase25_messages.INFO)
        return self._redirect()

    def release_stale_view(self, request):
        if not self._require_post(request):
            return self._redirect()
        workers = _phase25_mark_stale_workers()
        jobs = _phase25_release_stale_jobs()
        _phase26_publish_operations()
        self.message_user(request, f"{workers} Worker و {jobs} قفل Job منقضی بازیابی شد.", level=_phase25_messages.SUCCESS)
        return self._redirect()

    def retry_failed_view(self, request):
        if not self._require_post(request):
            return self._redirect()
        now = _phase25_timezone.now()
        queryset = _Phase24LinkJob.objects.filter(status="failed").exclude(analysis__status="converted")
        count = queryset.update(
            status="queued", next_run_at=now, locked_at=None, worker_id="", attempt_count=0,
            progress_percent=0, progress_stage="queued", progress_message="بازگردانی گروهی از داشبورد",
            completed_at=None, success_notified_at=None, failure_notified_at=None,
        )
        _Phase23CustomerLinkAnalysis.objects.filter(job__status="queued").exclude(status="converted").update(status="pending", error_message="")
        _phase26_publish_operations()
        self.message_user(request, f"{count} Job ناموفق دوباره وارد صف شد.", level=_phase25_messages.SUCCESS)
        return self._redirect()

    def toggle_adapter_view(self, request, adapter_key):
        if not self._require_post(request):
            return self._redirect()
        policy = _Phase25AdapterPolicy.objects.filter(adapter_key=adapter_key).first()
        if policy is None:
            self.message_user(request, "Adapter پیدا نشد.", level=_phase25_messages.ERROR)
            return self._redirect()
        policy.is_enabled = not policy.is_enabled
        if policy.is_enabled:
            policy.paused_until = None
        policy.save(update_fields=["is_enabled", "paused_until", "updated_at"])
        _phase26_publish_operations()
        self.message_user(request, f"{policy} {'فعال' if policy.is_enabled else 'غیرفعال'} شد.", level=_phase25_messages.SUCCESS)
        return self._redirect()

    def health_view(self, request):
        payload, status_code = _phase25_health_payload()
        return _phase25_JsonResponse(payload, status=status_code)

    def changelist_view(self, request, extra_context=None):
        _phase25_ensure_policies()
        context = _phase25_queue_metrics()
        context["title"] = "داشبورد عملیات تحلیل لینک و Workerها"
        if extra_context:
            context.update(extra_context)
        return super().changelist_view(request, extra_context=context)
# END PHASE 25 LINK ANALYSIS OPERATIONS ADMIN

# BEGIN PHASE 26 REALTIME AND MANUAL REVIEW ADMIN
from .manual_review import assign_review as _phase26_assign_review, finish_review as _phase26_finish_review
from .models import LinkAnalysisManualReview as _Phase26ManualReview
from .realtime import publish_operations as _phase26_publish_operations


@admin.register(_Phase26ManualReview)
class LinkAnalysisManualReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id", "analysis", "status", "reason", "priority", "operator_material",
        "operator_weight_grams", "operator_print_minutes", "operator_price_display",
        "assigned_to", "requested_by", "requested_at", "resolved_at",
    )
    list_filter = ("status", "reason", "priority", "requested_at", "assigned_to")
    search_fields = (
        "analysis__title", "analysis__source_url", "analysis__source_domain",
        "customer_note", "reviewer_note", "error_snapshot",
    )
    list_select_related = ("analysis", "analysis__user", "job", "requested_by", "assigned_to")
    readonly_fields = (
        "analysis", "job", "requested_by", "reason", "source_page_link",
        "operator_price_display", "error_snapshot", "source_snapshot",
        "operator_notification_sent_at", "operator_notification_error",
        "requested_at", "started_at", "resolved_at", "updated_at",
    )
    fieldsets = (
        ("لینک و مشتری", {"fields": ("analysis", "source_page_link", "requested_by", "reason", "customer_note")}),
        ("قیمت‌گذاری اپراتور", {"fields": (
            "operator_material", "operator_weight_grams", "operator_print_minutes",
            "operator_price_override", "operator_price_display", "operator_specs",
        ), "description": "وزن، زمان واقعی و متریال را ثبت کنید. اگر قیمت دستی صفر باشد، نرخ روز متریال و پله زمانی تنظیمات اعمال می‌شود."}),
        ("گردش بررسی", {"fields": ("status", "priority", "assigned_to", "reviewer_note", "resolution_action")}),
        ("اطلاعات فنی", {"fields": ("error_snapshot", "source_snapshot"), "classes": ("collapse",)}),
        ("اعلان و زمان‌ها", {"fields": (
            "operator_notification_sent_at", "operator_notification_error", "requested_at",
            "started_at", "resolved_at", "updated_at",
        ), "classes": ("collapse",)}),
    )
    actions = ("assign_to_me", "apply_operator_pricing", "retry_analysis", "resolve_selected", "reject_selected")

    @admin.display(description="صفحه منبع")
    def source_page_link(self, obj):
        if not obj or not obj.analysis_id:
            return "-"
        return format_html('<a href="{}" target="_blank" rel="noopener">مشاهده لینک اصلی ↗</a>', obj.analysis.normalized_url or obj.analysis.source_url)

    @admin.display(description="قیمت قطعی فعلی")
    def operator_price_display(self, obj):
        if not obj or not obj.operator_pricing_complete:
            return "پس از تکمیل وزن، زمان و متریال"
        if obj.operator_price_override:
            return f"{obj.operator_price_override:,} تومان (دستی)"
        from .models import CatalogPricingReview
        from .pricing_authority import calculate_verified_price
        proxy = CatalogPricingReview(
            material=obj.operator_material,
            weight_grams=obj.operator_weight_grams,
            print_minutes=obj.operator_print_minutes,
            status="verified",
        )
        data = calculate_verified_price(proxy)
        return f"{data.get('total', 0):,} تومان / زمان قابل محاسبه {data.get('billable_minutes', 0)} دقیقه"

    def save_model(self, request, obj, form, change):
        if obj.operator_pricing_complete:
            obj.assigned_to = request.user
            if obj.status in {"pending", "in_progress"} and obj.resolution_action == "data_completed":
                obj.status = "resolved"
        super().save_model(request, obj, form, change)
        if obj.operator_pricing_complete and (obj.status == "resolved" or obj.resolution_action == "data_completed"):
            from .manual_pricing import apply_manual_review_pricing
            apply_manual_review_pricing(obj, operator=request.user)

    @admin.action(description="ثبت و قفل قیمت اپراتوری موارد انتخاب‌شده")
    def apply_operator_pricing(self, request, queryset):
        from django.core.exceptions import ValidationError
        from .manual_pricing import apply_manual_review_pricing
        count = 0
        for obj in queryset:
            try:
                apply_manual_review_pricing(obj, operator=request.user)
            except ValidationError as exc:
                self.message_user(request, f"#{obj.pk}: {exc}", level=messages.ERROR)
            else:
                count += 1
        self.message_user(request, f"قیمت {count} درخواست قفل و به مشتری اعلام شد.", level=messages.SUCCESS)

    @admin.action(description="واگذاری موارد انتخاب‌شده به من")
    def assign_to_me(self, request, queryset):
        count = 0
        for review in queryset.filter(status__in=["pending", "in_progress"]):
            _phase26_assign_review(review, request.user)
            count += 1
        self.message_user(request, f"{count} مورد به شما واگذار شد.")

    @admin.action(description="اجرای مجدد تحلیل و نگه‌داشتن در بررسی")
    def retry_analysis(self, request, queryset):
        count = 0
        for review in queryset.exclude(analysis__status="converted"):
            _phase26_assign_review(review, request.user)
            try:
                _phase24_enqueue_link(review.analysis, force=True, priority=max(review.priority, 150))
            except Exception as exc:
                self.message_user(request, f"خطا برای #{review.pk}: {exc}", level=_phase25_messages.ERROR)
            else:
                count += 1
        self.message_user(request, f"{count} تحلیل دوباره وارد صف شد.", level=_phase25_messages.SUCCESS)

    @admin.action(description="بستن موارد انتخاب‌شده به‌عنوان حل‌شده")
    def resolve_selected(self, request, queryset):
        count = 0
        for review in queryset.filter(status__in=["pending", "in_progress"]):
            _phase26_finish_review(review, user=request.user, action="data_completed", note="حل‌شده از عملیات گروهی ادمین")
            count += 1
        self.message_user(request, f"{count} مورد حل‌شده ثبت شد.", level=_phase25_messages.SUCCESS)

    @admin.action(description="رد موارد انتخاب‌شده")
    def reject_selected(self, request, queryset):
        count = 0
        for review in queryset.filter(status__in=["pending", "in_progress"]):
            _phase26_finish_review(review, user=request.user, action="rejected", note="ردشده از عملیات گروهی ادمین", status="rejected")
            count += 1
        self.message_user(request, f"{count} مورد رد شد.", level=_phase25_messages.WARNING)
# END PHASE 26 REALTIME AND MANUAL REVIEW ADMIN


# BEGIN PHASE 29 VERIFIED PRICING ADMIN
from .models import CatalogPricingReview
from .pricing_authority import calculate_verified_price


@admin.register(CatalogPricingReview)
class CatalogPricingReviewAdmin(admin.ModelAdmin):
    list_display = (
        "asset", "source_name", "status", "material", "weight_grams", "print_minutes",
        "billable_minutes_display", "current_price_display", "verified_by", "verified_at",
    )
    list_filter = ("status", "asset__source", "material", "verified_at")
    search_fields = ("asset__title", "asset__source_url", "asset__author_name", "operator_note")
    list_select_related = ("asset", "asset__source", "material", "verified_by")
    readonly_fields = (
        "source_page_link", "current_price_display", "billable_minutes_display",
        "notification_sent_at", "notification_error", "verified_at", "created_at", "updated_at",
    )
    fieldsets = (
        ("مدل و منبع", {"fields": ("asset", "source_page_link", "status")}),
        ("مشخصات قطعی چاپ", {"fields": ("material", "weight_grams", "print_minutes", "billable_minutes_display", "price_override")}),
        ("قیمت روز", {"fields": ("current_price_display",), "description": "زمان چاپ بر اساس حداقل و پله زمانی تنظیمات قیمت‌گذاری رو به بالا گرد می‌شود."}),
        ("اپراتور و اعلان", {"fields": ("operator_note", "verified_by", "verified_at", "notification_sent_at", "notification_error")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    actions = ("mark_verified", "send_operator_alert")

    @admin.display(description="منبع", ordering="asset__source__name")
    def source_name(self, obj):
        return obj.asset.source.name

    @admin.display(description="صفحه اصلی")
    def source_page_link(self, obj):
        if not obj or not obj.asset_id:
            return "-"
        return format_html('<a href="{}" target="_blank" rel="noopener">مشاهده محصول در منبع ↗</a>', obj.asset.source_url)

    @admin.display(description="زمان قابل محاسبه")
    def billable_minutes_display(self, obj):
        if not obj or not obj.print_minutes:
            return "نامشخص"
        data = calculate_verified_price(obj)
        return f"{data.get('billable_minutes', 0)} دقیقه (واقعی: {obj.print_minutes})"

    @admin.display(description="قیمت روز قطعی")
    def current_price_display(self, obj):
        if not obj or not obj.is_complete:
            return "پس از تکمیل وزن، زمان و متریال"
        return f"{calculate_verified_price(obj).get('total', 0):,} تومان"

    def save_model(self, request, obj, form, change):
        if obj.status == "verified":
            obj.verified_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="تأیید وزن و زمان موارد انتخاب‌شده")
    def mark_verified(self, request, queryset):
        count = 0
        for obj in queryset:
            if not obj.material_id or not obj.weight_grams or not obj.print_minutes:
                self.message_user(request, f"{obj.asset}: وزن، زمان یا متریال ناقص است.", level=messages.ERROR)
                continue
            obj.status = "verified"
            obj.verified_by = request.user
            obj.save()
            count += 1
        self.message_user(request, f"{count} مدل قیمت‌گذاری و قفل شد.", level=messages.SUCCESS)

    @admin.action(description="ارسال دوباره اعلان به اپراتور")
    def send_operator_alert(self, request, queryset):
        from .operator_notifications import notify_catalog_pricing
        count = 0
        for obj in queryset:
            obj.notification_sent_at = None
            obj.notification_error = ""
            obj.save(update_fields=["notification_sent_at", "notification_error", "updated_at"])
            notify_catalog_pricing(obj)
            count += 1
        self.message_user(request, f"اعلان {count} مورد ارسال شد.")
# END PHASE 29 VERIFIED PRICING ADMIN

# BEGIN PHASE 33 AUTOMATION DEADLINES AND OPERATOR CONTROLS
from django.shortcuts import get_object_or_404 as _phase33_get_object_or_404
from django.core.exceptions import PermissionDenied as _phase33_PermissionDenied

from .automation_watchdog import (
    catalog_deadline_state as _phase33_catalog_deadline_state,
    expire_stale_automation as _phase33_expire_stale_automation,
    source_deadline_state as _phase33_source_deadline_state,
    stop_catalog_run as _phase33_stop_catalog_run,
    stop_source_log as _phase33_stop_source_log,
)



def _phase33_require_operator(request):
    if not (request.user and request.user.is_active and request.user.is_superuser):
        raise _phase33_PermissionDenied


def _phase33_duration_label(seconds):
    if seconds is None:
        return "-"
    seconds = int(seconds)
    if seconds <= 0:
        return "مهلت تمام شده"
    minutes = max(seconds // 60, 1)
    if minutes < 60:
        return f"{minutes} دقیقه مانده"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} ساعت مانده"
    return f"{hours // 24} روز مانده"


def _phase33_attach_source_state(log):
    state = _phase33_source_deadline_state(log)
    log.phase33_can_stop = state.active
    log.phase33_deadline_label = _phase33_duration_label(state.seconds_remaining) if state.active else "-"
    log.phase33_deadline_class = "expired" if state.stale else ("active" if state.active else "terminal")
    return log


def _phase33_attach_catalog_state(run):
    state = _phase33_catalog_deadline_state(run)
    run.phase33_can_stop = state.active
    run.phase33_deadline_label = _phase33_duration_label(state.seconds_remaining) if state.active else "-"
    run.phase33_deadline_class = "expired" if state.stale else ("active" if state.active else "terminal")
    return run


@admin.action(description="توقف اجراهای انتخاب‌شده")
def _phase33_stop_selected_catalog_runs(modeladmin, request, queryset):
    stopped = 0
    for run in queryset.filter(status__in=["queued", "running"]):
        if _phase33_stop_catalog_run(
            run,
            reason="OperatorCancelled: stopped from Django admin action.",
            actor=request.user,
        ):
            stopped += 1
    modeladmin.message_user(request, f"{stopped} اجرا متوقف شد.", level=messages.WARNING)


@admin.display(description="مهلت اجرا")
def _phase33_catalog_deadline_display(self, obj):
    state = _phase33_catalog_deadline_state(obj)
    if not state.active:
        return "-"
    color = "#d1242f" if state.stale else "#bf8700"
    return format_html(
        '<strong style="color:{}">{}</strong>',
        color,
        _phase33_duration_label(state.seconds_remaining),
    )


CatalogSyncRunAdmin.phase33_deadline_display = _phase33_catalog_deadline_display
CatalogSyncRunAdmin.list_display = tuple(CatalogSyncRunAdmin.list_display) + ("phase33_deadline_display",)
CatalogSyncRunAdmin.readonly_fields = tuple(CatalogSyncRunAdmin.readonly_fields) + (
    "deadline_at", "heartbeat_at", "cancelled_at",
)
CatalogSyncRunAdmin.actions = tuple(CatalogSyncRunAdmin.actions) + (_phase33_stop_selected_catalog_runs,)


@admin.action(description="توقف گزارش‌های فعال انتخاب‌شده")
def _phase33_stop_selected_source_logs(modeladmin, request, queryset):
    stopped = 0
    for log in queryset.filter(status__in=["queued", "running"]):
        if _phase33_stop_source_log(
            log,
            reason="OperatorCancelled: stopped from Django admin action.",
            actor=request.user,
        ):
            stopped += 1
    modeladmin.message_user(request, f"{stopped} عملیات متوقف شد.", level=messages.WARNING)


@admin.display(description="مهلت اجرا")
def _phase33_source_deadline_display(self, obj):
    state = _phase33_source_deadline_state(obj)
    if not state.active:
        return "-"
    color = "#d1242f" if state.stale else "#bf8700"
    return format_html(
        '<strong style="color:{}">{}</strong>',
        color,
        _phase33_duration_label(state.seconds_remaining),
    )


def _phase33_source_log_change_permission(self, request, obj=None):
    return bool(request.user and request.user.is_active and request.user.is_superuser)


ExternalSourceFetchLogAdmin.phase33_deadline_display = _phase33_source_deadline_display
ExternalSourceFetchLogAdmin.list_display = tuple(ExternalSourceFetchLogAdmin.list_display) + ("phase33_deadline_display",)
ExternalSourceFetchLogAdmin.readonly_fields = tuple(
    field.name for field in ExternalSourceFetchLog._meta.fields
)
ExternalSourceFetchLogAdmin.actions = (_phase33_stop_selected_source_logs,)
ExternalSourceFetchLogAdmin.has_change_permission = _phase33_source_log_change_permission


_phase33_old_dashboard_get_urls = CatalogAutomationDashboardAdmin.get_urls
_phase33_old_dashboard_changelist = CatalogAutomationDashboardAdmin.changelist_view


def _phase33_stop_stale_view(self, request):
    _phase33_require_operator(request)
    if request.method != "POST":
        self.message_user(request, "این عملیات فقط با POST اجرا می‌شود.", level=messages.WARNING)
        return _phase11_dashboard_redirect()
    summary = _phase33_expire_stale_automation(actor=request.user)
    self.message_user(
        request,
        (
            f"منبع متوقف‌شده: {summary['source_stopped']}؛ "
            f"اجرای کاتالوگ متوقف‌شده: {summary['catalog_stopped']}."
        ),
        level=messages.SUCCESS if summary["source_stopped"] or summary["catalog_stopped"] else messages.INFO,
    )
    return _phase11_dashboard_redirect()


def _phase33_stop_source_log_view(self, request, log_id):
    _phase33_require_operator(request)
    if request.method != "POST":
        self.message_user(request, "این عملیات فقط با POST اجرا می‌شود.", level=messages.WARNING)
        return _phase11_dashboard_redirect()
    log = _phase33_get_object_or_404(ExternalSourceFetchLog, pk=log_id)
    stopped = _phase33_stop_source_log(
        log,
        reason="OperatorCancelled: stopped from automation dashboard.",
        actor=request.user,
    )
    self.message_user(
        request,
        "عملیات متوقف شد." if stopped else "عملیات قبلاً پایان یافته بود.",
        level=messages.WARNING if stopped else messages.INFO,
    )
    return _phase11_dashboard_redirect()


def _phase33_stop_catalog_run_view(self, request, run_id):
    _phase33_require_operator(request)
    if request.method != "POST":
        self.message_user(request, "این عملیات فقط با POST اجرا می‌شود.", level=messages.WARNING)
        return _phase11_dashboard_redirect()
    run = _phase33_get_object_or_404(CatalogSyncRun, pk=run_id)
    stopped = _phase33_stop_catalog_run(
        run,
        reason="OperatorCancelled: stopped from automation dashboard.",
        actor=request.user,
    )
    self.message_user(
        request,
        "اجرای کاتالوگ متوقف شد." if stopped else "اجرا قبلاً پایان یافته بود.",
        level=messages.WARNING if stopped else messages.INFO,
    )
    return _phase11_dashboard_redirect()


def _phase33_dashboard_get_urls(self):
    urls = [
        path(
            "stop-stale/",
            self.admin_site.admin_view(self.stop_stale_view),
            name="store_catalogautomationdashboard_stop_stale",
        ),
        path(
            "stop-source-log/<int:log_id>/",
            self.admin_site.admin_view(self.stop_source_log_view),
            name="store_catalogautomationdashboard_stop_source_log",
        ),
        path(
            "stop-catalog-run/<int:run_id>/",
            self.admin_site.admin_view(self.stop_catalog_run_view),
            name="store_catalogautomationdashboard_stop_catalog_run",
        ),
    ]
    return urls + _phase33_old_dashboard_get_urls(self)


def _phase33_dashboard_changelist(self, request, extra_context=None):
    source_logs = [
        _phase33_attach_source_state(item)
        for item in ExternalSourceFetchLog.objects.select_related("created_by")[:20]
    ]
    catalog_runs = [
        _phase33_attach_catalog_state(item)
        for item in CatalogSyncRun.objects.select_related("source").order_by("-created_at")[:10]
    ]
    context = dict(extra_context or {})
    context.update({
        "recent_source_logs": source_logs,
        "recent_runs": catalog_runs,
        "phase33_watchdog": _phase33_expire_stale_automation(dry_run=True),
    })
    return _phase33_old_dashboard_changelist(self, request, extra_context=context)


CatalogAutomationDashboardAdmin.stop_stale_view = _phase33_stop_stale_view
CatalogAutomationDashboardAdmin.stop_source_log_view = _phase33_stop_source_log_view
CatalogAutomationDashboardAdmin.stop_catalog_run_view = _phase33_stop_catalog_run_view
CatalogAutomationDashboardAdmin.get_urls = _phase33_dashboard_get_urls
CatalogAutomationDashboardAdmin.changelist_view = _phase33_dashboard_changelist
# END PHASE 33 AUTOMATION DEADLINES AND OPERATOR CONTROLS

# BEGIN PHASE 34B MAKERWORLD EDITORIAL AND COMMERCE
from .phase34b_publishing import convert_to_fixed_product, convert_to_portfolio, ensure_persian_draft


def _phase34b_draft_persian(modeladmin, request, queryset):
    count = 0
    for asset in queryset.select_related("source"):
        ensure_persian_draft(asset)
        count += 1
    modeladmin.message_user(request, f"{count} پیش‌نویس فارسی ایجاد یا تکمیل شد.", level=messages.SUCCESS)
_phase34b_draft_persian.short_description = "ساخت پیش‌نویس فارسی قابل ویرایش"


def _phase34b_convert_fixed(modeladmin, request, queryset):
    success = 0
    for asset in queryset:
        try:
            convert_to_fixed_product(asset)
            success += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{asset}: {exc}", level=messages.ERROR)
    if success:
        modeladmin.message_user(request, f"{success} محصول قیمت‌ثابت غیرفعال ساخته شد.", level=messages.SUCCESS)
_phase34b_convert_fixed.short_description = "تبدیل به محصول چاپی قیمت‌ثابت"


def _phase34b_convert_portfolio(modeladmin, request, queryset):
    success = 0
    for asset in queryset:
        try:
            convert_to_portfolio(asset)
            success += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{asset}: {exc}", level=messages.ERROR)
    if success:
        modeladmin.message_user(request, f"{success} نمونه‌کار غیرفعال ساخته شد.", level=messages.SUCCESS)
_phase34b_convert_portfolio.short_description = "تبدیل به نمونه‌کار"

if "_phase34b_draft_persian" not in ImportedPrintAssetAdmin.actions:
    ImportedPrintAssetAdmin._phase34b_draft_persian = _phase34b_draft_persian
    ImportedPrintAssetAdmin._phase34b_convert_fixed = _phase34b_convert_fixed
    ImportedPrintAssetAdmin._phase34b_convert_portfolio = _phase34b_convert_portfolio
    ImportedPrintAssetAdmin.actions = list(ImportedPrintAssetAdmin.actions) + [
        "_phase34b_draft_persian", "_phase34b_convert_fixed", "_phase34b_convert_portfolio"
    ]
    ImportedPrintAssetAdmin.list_display = list(ImportedPrintAssetAdmin.list_display) + [
        "editorial_status", "commercial_license_status", "fixed_print_price"
    ]
    ImportedPrintAssetAdmin.list_filter = list(ImportedPrintAssetAdmin.list_filter) + [
        "editorial_status", "commercial_license_status"
    ]
    ImportedPrintAssetAdmin.fieldsets = tuple(ImportedPrintAssetAdmin.fieldsets) + (
        ("تحریریه فارسی و انتشار", {"fields": (
            "source_title", "source_description", "persian_title",
            "persian_short_description", "persian_description", "editorial_status",
        )}),
        ("فروش چاپ و مجوز تجاری", {"fields": (
            "fixed_print_price", "commercial_license_status", "commercial_license_source",
            "commercial_license_note", "commercial_license_evidence", "portfolio_item",
        )}),
    )
# END PHASE 34B MAKERWORLD EDITORIAL AND COMMERCE


# BEGIN PHASE 35 BILINGUAL CATALOG EDITOR
from django.contrib.admin import SimpleListFilter as _Phase35SimpleListFilter
from django.http import JsonResponse as _Phase35JsonResponse
from django.urls import path as _phase35_path
from django.utils.html import format_html as _phase35_format_html
from .phase35_catalog_editor import (
    apply_provisional_price as _phase35_apply_price,
    mark_price_final as _phase35_mark_price_final,
    prepare_asset as _phase35_prepare_asset,
    translate_asset as _phase35_translate_asset,
)


class _Phase35TranslationFilter(_Phase35SimpleListFilter):
    title = "ترجمه فارسی"
    parameter_name = "phase35_translation"
    def lookups(self, request, model_admin):
        return (("missing", "ترجمه‌نشده"), ("draft", "پیش‌نویس"), ("ready", "ترجمه‌شده"))
    def queryset(self, request, queryset):
        if self.value() == "missing":
            return queryset.filter(translation_status="missing")
        if self.value() == "draft":
            return queryset.filter(translation_status="draft")
        if self.value() == "ready":
            return queryset.filter(translation_status__in=["translated", "reviewed"])
        return queryset


class _Phase35SaleFilter(_Phase35SimpleListFilter):
    title = "آمادگی فروش"
    parameter_name = "phase35_sale"
    def lookups(self, request, model_admin):
        return (("unapproved", "تأییدنشده برای فروش"), ("ready", "آماده تبدیل"), ("converted", "تبدیل‌شده"))
    def queryset(self, request, queryset):
        if self.value() == "unapproved":
            return queryset.exclude(commercial_license_status__in=["allowed", "owned", "public_domain"])
        if self.value() == "ready":
            return queryset.filter(commercial_license_status__in=["allowed", "owned", "public_domain"], fixed_print_price__gt=0, product__isnull=True)
        if self.value() == "converted":
            return queryset.filter(product__isnull=False)
        return queryset


class _Phase35PriceFilter(_Phase35SimpleListFilter):
    title = "وضعیت قیمت"
    parameter_name = "phase35_price"
    def lookups(self, request, model_admin):
        return (("unset", "بدون قیمت"), ("estimated", "علی‌الحساب"), ("final", "قطعی"))
    def queryset(self, request, queryset):
        if self.value() == "unset":
            return queryset.filter(fixed_print_price=0)
        if self.value() == "estimated":
            return queryset.filter(price_is_final=False, fixed_print_price__gt=0)
        if self.value() == "final":
            return queryset.filter(price_is_final=True)
        return queryset


@admin.display(description="عنوان اصلی", ordering="source_title")
def _phase35_source_title_admin(self, obj):
    title = obj.source_title or obj.title
    return _phase35_format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', obj.source_url, title)


@admin.display(description="قیمت", ordering="fixed_print_price")
def _phase35_price_admin(self, obj):
    label = "قطعی" if obj.price_is_final else "علی‌الحساب"
    return f"{obj.fixed_print_price:,} تومان — {label}" if obj.fixed_print_price else "بدون قیمت"


def _phase35_prepare_selected(modeladmin, request, queryset):
    success = 0
    for asset in queryset.select_related("source"):
        try:
            _phase35_prepare_asset(asset)
            success += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{asset}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{success} مدل ترجمه و قیمت‌گذاری اولیه شد.", level=messages.SUCCESS)
_phase35_prepare_selected.short_description = "ترجمه خودکار + قیمت علی‌الحساب"


def _phase35_translate_selected(modeladmin, request, queryset):
    success = 0
    for asset in queryset.select_related("source"):
        try:
            _phase35_translate_asset(asset, force=True)
            success += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{asset}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"{success} ترجمه بازسازی شد.", level=messages.SUCCESS)
_phase35_translate_selected.short_description = "ترجمه مجدد متن‌های انتخاب‌شده"


def _phase35_price_selected(modeladmin, request, queryset):
    success = 0
    for asset in queryset:
        _phase35_apply_price(asset, force=True)
        success += 1
    modeladmin.message_user(request, f"برای {success} مدل قیمت علی‌الحساب محاسبه شد.", level=messages.SUCCESS)
_phase35_price_selected.short_description = "محاسبه قیمت علی‌الحساب"


def _phase35_finalize_price_selected(modeladmin, request, queryset):
    success = 0
    for asset in queryset:
        try:
            _phase35_mark_price_final(asset)
            success += 1
        except Exception as exc:
            modeladmin.message_user(request, f"{asset}: {exc}", level=messages.ERROR)
    modeladmin.message_user(request, f"قیمت {success} مدل قطعی شد.", level=messages.SUCCESS)
_phase35_finalize_price_selected.short_description = "قطعی‌کردن قیمت انتخاب‌شده‌ها"


_phase35_old_get_urls = ImportedPrintAssetAdmin.get_urls

def _phase35_get_urls(self):
    return [
        _phase35_path("<int:object_id>/translate/", self.admin_site.admin_view(self.phase35_translate_view), name="store_importedprintasset_translate"),
    ] + _phase35_old_get_urls(self)


def _phase35_translate_view(self, request, object_id):
    if request.method != "POST":
        return _Phase35JsonResponse({"ok": False, "error": "POST required"}, status=405)
    asset = self.get_queryset(request).select_related("source").filter(pk=object_id).first()
    if asset is None:
        return _Phase35JsonResponse({"ok": False, "error": "not found"}, status=404)
    try:
        _phase35_translate_asset(asset, force=True)
    except Exception as exc:
        return _Phase35JsonResponse({"ok": False, "error": str(exc)}, status=400)
    return _Phase35JsonResponse({
        "ok": True,
        "persian_title": asset.persian_title,
        "persian_short_description": asset.persian_short_description,
        "persian_description": asset.persian_description,
        "translation_status": asset.translation_status,
        "translation_provider": asset.translation_provider,
    })


ImportedPrintAssetAdmin.source_title_admin = _phase35_source_title_admin
ImportedPrintAssetAdmin.price_admin = _phase35_price_admin
ImportedPrintAssetAdmin.phase35_translate_view = _phase35_translate_view
ImportedPrintAssetAdmin.get_urls = _phase35_get_urls
ImportedPrintAssetAdmin.list_display = [
    "preview_thumbnail",
    "source_title_admin",
    "persian_title",
    "source",
    "description_excerpt",
    "weight_summary",
    "image_count_admin",
    "source_views",
    "source_downloads",
    "source_likes",
    "license_summary",
    "is_publicly_approved",
    "translation_status",
    "editorial_status",
    "commercial_license_status",
    "fixed_print_price",
    "price_is_final",
    "product",
    "imported_at",
]
ImportedPrintAssetAdmin.list_display_links = ["source_title_admin"]
ImportedPrintAssetAdmin.list_editable = [
    "persian_title", "editorial_status", "commercial_license_status",
    "fixed_print_price", "price_is_final",
]
ImportedPrintAssetAdmin.list_filter = [
    _Phase35TranslationFilter, _Phase35SaleFilter, _Phase35PriceFilter,
    "source", "editorial_status", "commercial_license_status",
    "translation_status", "price_status", "price_is_final", "product", "imported_at",
]
ImportedPrintAssetAdmin.search_fields = [
    "source_title", "title", "persian_title", "source_description",
    "persian_description", "tags", "author_name", "source_url", "external_id",
]
ImportedPrintAssetAdmin.list_per_page = 50
ImportedPrintAssetAdmin.actions = list(dict.fromkeys(list(ImportedPrintAssetAdmin.actions) + [
    "_phase35_prepare_selected", "_phase35_translate_selected",
    "_phase35_price_selected", "_phase35_finalize_price_selected",
]))
ImportedPrintAssetAdmin._phase35_prepare_selected = _phase35_prepare_selected
ImportedPrintAssetAdmin._phase35_translate_selected = _phase35_translate_selected
ImportedPrintAssetAdmin._phase35_price_selected = _phase35_price_selected
ImportedPrintAssetAdmin._phase35_finalize_price_selected = _phase35_finalize_price_selected
ImportedPrintAssetAdmin.readonly_fields = list(dict.fromkeys(list(ImportedPrintAssetAdmin.readonly_fields) + [
    "translation_provider", "translated_at", "estimated_material_cost",
]))
ImportedPrintAssetAdmin.fieldsets = (
    ("متن اصلی منبع ـ انگلیسی", {"fields": (
        "source", "source_url_link", "external_id", "source_title", "source_description",
        "short_description", "technical_specs", "tags", "author_name", "license_name", "license_url",
    )}),
    ("نسخه فارسی قابل ویرایش", {"fields": (
        "persian_title", "persian_short_description", "persian_description",
        "translation_status", "translation_provider", "translated_at", "editorial_status",
    )}),
    ("قیمت‌گذاری و فروش", {"fields": (
        "fixed_print_price", "price_is_final", "price_status", "estimated_material_cost", "pricing_note",
        "commercial_license_status", "commercial_license_source", "commercial_license_note",
        "commercial_license_evidence", "product", "portfolio_item",
    )}),
    ("فایل و تصاویر", {"fields": (
        "preview_image", "remote_image_url", "file_format", "private_download_link",
        "archive_status", "archived_model_file", "keep_public_when_source_disabled",
    )}),
    ("اطلاعات سیستمی", {"classes": ("collapse",), "fields": (
        "status", "admin_note", "source_payload", "imported_at", "updated_at",
    )}),
)

class _Phase35ImportedAdminMedia:
    css = {"all": ("admin/phase35-admin.css",)}
    js = ("admin/phase35-translation.js",)
ImportedPrintAssetAdmin.Media = _Phase35ImportedAdminMedia

_phase35_product_list_display = [
    "title", "title_en", "sku", "category", "minimum_price",
    "price_is_final", "is_featured", "is_active", "published_at",
]
_phase35_product_list_editable = ["price_is_final", "is_featured", "is_active"]
_phase35_product_list_filter = [
    "price_is_final", "order_mode", "category__section", "category",
    "is_featured", "is_active",
]
_phase35_product_search_fields = [
    "title", "title_en", "sku", "short_description", "short_description_en",
    "description", "description_en", "source_url", "source_external_id",
]
_phase35_product_fieldsets = (
    ("متن فارسی", {"fields": ("title", "slug", "short_description", "description")}),
    ("متن اصلی انگلیسی", {"fields": ("title_en", "short_description_en", "description_en")}),
    ("منبع", {"fields": ("source_name", "source_external_id", "source_url")}),
    ("فروش و قیمت", {"fields": (
        "category", "sku", "order_mode", "fixed_price", "price_is_final", "price_note",
        "fixed_delivery_days", "consultation_required",
    )}),
    ("رسانه و مشخصات", {"fields": (
        "main_image", "model_file", "dimensions", "technical_notes", "installation_guide",
    )}),
    ("سئو و شبکه‌های اجتماعی", {"fields": (
        "seo_focus_keyword", "meta_title", "meta_description", "canonical_url",
        "robots_index", "robots_follow", "og_title", "og_description", "og_image",
        "seo_preview",
    )}),
    ("انتشار و آمار", {"fields": (
        "is_featured", "is_active", "published_at", "view_count", "created_at", "updated_at",
    )}),
)


def _phase35_apply_product_admin_configuration(admin_class):
    admin_class.list_display = list(_phase35_product_list_display)
    admin_class.list_display_links = ("title",)
    admin_class.list_editable = list(_phase35_product_list_editable)
    admin_class.list_filter = list(_phase35_product_list_filter)
    admin_class.search_fields = list(_phase35_product_search_fields)
    admin_class.fieldsets = _phase35_product_fieldsets


_phase35_apply_product_admin_configuration(ProductAdmin)
_phase35_registered_product_admin = admin.site._registry.get(Product)
if _phase35_registered_product_admin is not None:
    _phase35_apply_product_admin_configuration(
        _phase35_registered_product_admin.__class__
    )
# END PHASE 35 BILINGUAL CATALOG EDITOR

# BEGIN PHASE39_ADMIN
from . import phase39_admin  # noqa: E402,F401
# END PHASE39_ADMIN
