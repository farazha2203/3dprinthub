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
        "default_labor_percent",
        "minimum_order_amount",
        "packaging_fee",
        "tax_percent",
        "updated_at",
    ]

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
