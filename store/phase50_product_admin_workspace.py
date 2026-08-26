from __future__ import annotations

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .epic49_catalog_profile import ProductCatalogProfile
from .models import Product, ProductImage, ProductVariant


SECTION_TITLES = (
    "اطلاعات کالا",
    "تصاویر",
    "فروش و موجودی",
    "پروفایل‌ها و سایز/وزن",
    "قیمت‌گذاری",
    "ارسال و بسته‌بندی",
    "SEO",
    "اسلایدر صفحه اول",
    "منبع و لایسنس",
    "همگام‌سازی ویندوز",
    "آمار و وضعیت",
)


def _profile(obj: Product):
    if not getattr(obj, "pk", None):
        return None
    try:
        return obj.catalog_profile
    except ProductCatalogProfile.DoesNotExist:
        return None
    except Exception:
        return None


def _admin_link(name: str, label: str, *, args=None, query=""):
    try:
        url = reverse(name, args=args or [])
    except Exception:
        return label
    if query:
        url = f"{url}?{query}"
    return format_html('<a class="button" href="{}">{}</a>', url, label)


def _product_admin_methods(admin_cls):
    if not hasattr(admin_cls, "phase50_gallery_admin"):
        @admin.display(description="مدیریت گالری تصاویر")
        def phase50_gallery_admin(self, obj):
            if not getattr(obj, "pk", None):
                return "پس از ذخیره محصول، گالری قابل مدیریت است."
            count = obj.images.count()
            return format_html(
                '<div><strong>{}</strong> تصویر گالری ثبت شده است.</div><div style="margin-top:8px">{}</div>',
                count,
                _admin_link(
                    "admin:store_productimage_changelist",
                    "باز کردن گالری تصاویر",
                    query=f"product__id__exact={obj.pk}",
                ),
            )

        admin_cls.phase50_gallery_admin = phase50_gallery_admin

    if not hasattr(admin_cls, "phase50_sales_profiles_admin"):
        @admin.display(description="مدیریت پروفایل‌های فروش")
        def phase50_sales_profiles_admin(self, obj):
            if not getattr(obj, "pk", None):
                return "پس از ذخیره محصول، پروفایل‌های فروش قابل مدیریت هستند."
            variants = obj.variants.order_by("sales_profile_sort_order", "id")
            total = variants.count()
            active = variants.filter(is_active=True).count()
            default = variants.filter(sales_profile_is_default=True).first()
            default_label = default.sales_profile_display_label if default else "—"
            return format_html(
                '<div><strong>{}</strong> پروفایل / <strong>{}</strong> فعال / پیش‌فرض: <strong>{}</strong></div>'
                '<div style="margin-top:8px">{}</div>',
                total,
                active,
                default_label,
                _admin_link(
                    "admin:store_productvariant_changelist",
                    "مدیریت و کپی پروفایل‌ها",
                    query=f"product__id__exact={obj.pk}",
                ),
            )

        admin_cls.phase50_sales_profiles_admin = phase50_sales_profiles_admin

    if not hasattr(admin_cls, "phase50_pricing_admin"):
        @admin.display(description="وضعیت قیمت‌گذاری کاتالوگ")
        def phase50_pricing_admin(self, obj):
            profile = _profile(obj)
            if profile is None:
                return "پروفایل کاتالوگ برای این محصول هنوز ایجاد نشده است."
            strategy = str(getattr(profile, "pricing_strategy", "") or profile.price_mode or "—")
            price_min = int(profile.price_min or 0)
            price_max = int(profile.price_max or 0)
            price_text = f"{price_min:,} تومان"
            if price_max and price_max != price_min:
                price_text = f"{price_min:,} تا {price_max:,} تومان"
            return format_html(
                '<div>روش: <strong>{}</strong> / بازه فعلی: <strong>{}</strong></div>'
                '<div style="margin-top:8px">{}</div>',
                strategy,
                price_text,
                _admin_link(
                    "admin:store_productcatalogprofile_change",
                    "تنظیم قیمت‌گذاری کاتالوگ",
                    args=[profile.pk],
                ),
            )

        admin_cls.phase50_pricing_admin = phase50_pricing_admin

    if not hasattr(admin_cls, "phase50_shipping_admin"):
        @admin.display(description="وضعیت ارسال و بسته‌بندی")
        def phase50_shipping_admin(self, obj):
            if not getattr(obj, "pk", None):
                return "پس از ذخیره محصول، اطلاعات ارسال پروفایل‌ها قابل مدیریت است."
            qs = obj.variants.filter(is_active=True)
            with_weight = 0
            with_dimensions = 0
            for row in qs.only(
                "shipping_weight_grams",
                "final_weight_grams",
                "material_weight_grams",
                "packaging_weight_grams",
                "package_length_cm",
                "package_width_cm",
                "package_height_cm",
            ):
                effective_weight = (
                    getattr(row, "shipping_weight_grams", 0)
                    or (getattr(row, "final_weight_grams", 0) or getattr(row, "material_weight_grams", 0) or 0)
                    + (getattr(row, "packaging_weight_grams", 0) or 0)
                )
                if effective_weight:
                    with_weight += 1
                if all(
                    getattr(row, field, 0)
                    for field in ("package_length_cm", "package_width_cm", "package_height_cm")
                ):
                    with_dimensions += 1
            total = qs.count()
            return format_html(
                '<div>{} پروفایل فعال؛ وزن ارسال برای <strong>{}</strong> و ابعاد بسته برای <strong>{}</strong> پروفایل تکمیل شده.</div>'
                '<div style="margin-top:8px">{}</div>',
                total,
                with_weight,
                with_dimensions,
                _admin_link(
                    "admin:store_productvariant_changelist",
                    "ویرایش وزن و بسته‌بندی پروفایل‌ها",
                    query=f"product__id__exact={obj.pk}",
                ),
            )

        admin_cls.phase50_shipping_admin = phase50_shipping_admin

    if not hasattr(admin_cls, "phase50_slider_admin"):
        @admin.display(description="کنترل اسلایدر صفحه اول")
        def phase50_slider_admin(self, obj):
            profile = _profile(obj)
            if profile is None:
                return "پروفایل کاتالوگ موجود نیست؛ ابتدا محصول را از مسیر رسمی کاتالوگ/ادمین کامل کنید."
            state = "فعال" if profile.homepage_slider_enabled else "غیرفعال"
            controls = _admin_link(
                "admin:store_productcatalogprofile_change",
                "تنظیم متن/تصویر/SEO اسلایدر",
                args=[profile.pk],
            )
            hero_link = _admin_link(
                "admin:website_homepageheroslide_changelist",
                "مدیریت Hero Studio",
            )
            return format_html(
                '<div>وضعیت: <strong>{}</strong> / ترتیب: <strong>{}</strong> / افکت: <strong>{}</strong></div>'
                '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">{} {}</div>',
                state,
                profile.homepage_slider_sort_order,
                profile.homepage_slider_transition_effect,
                controls,
                hero_link,
            )

        admin_cls.phase50_slider_admin = phase50_slider_admin

    if not hasattr(admin_cls, "phase50_license_admin"):
        @admin.display(description="منبع و مجوز تجاری")
        def phase50_license_admin(self, obj):
            profile = _profile(obj)
            if profile is None:
                return "اطلاعات مجوز کاتالوگ هنوز ثبت نشده است."
            return format_html(
                '<div>وضعیت مجوز: <strong>{}</strong><br>نام مجوز: <strong>{}</strong></div>'
                '<div style="margin-top:8px">{}</div>',
                profile.commercial_license_status or "—",
                profile.license_name or "—",
                _admin_link(
                    "admin:store_productcatalogprofile_change",
                    "ویرایش منبع و مجوز",
                    args=[profile.pk],
                ),
            )

        admin_cls.phase50_license_admin = phase50_license_admin

    if not hasattr(admin_cls, "phase50_windows_sync_admin"):
        @admin.display(description="وضعیت همگام‌سازی Windows ↔ Server")
        def phase50_windows_sync_admin(self, obj):
            profile = _profile(obj)
            if profile is None:
                return "هنوز پروفایل همگام‌سازی برای این محصول وجود ندارد."
            return format_html(
                '<div>Desktop ID: <strong>{}</strong> / Revision: <strong>{}</strong><br>'
                'آخرین منبع تغییر: <strong>{}</strong> / آخرین Sync: <strong>{}</strong></div>'
                '<div style="margin-top:8px">{}</div>',
                profile.desktop_product_id or "—",
                profile.sync_revision,
                profile.last_modified_source or "—",
                profile.last_synced_at or "—",
                _admin_link(
                    "admin:store_productcatalogprofile_change",
                    "جزئیات همگام‌سازی",
                    args=[profile.pk],
                ),
            )

        admin_cls.phase50_windows_sync_admin = phase50_windows_sync_admin


def _rename_inlines(product_admin) -> None:
    for inline in getattr(product_admin, "inlines", ()):
        model = getattr(inline, "model", None)
        if model is ProductImage:
            inline.verbose_name = "تصویر محصول"
            inline.verbose_name_plural = "تصاویر و گالری محصول"
            inline.extra = 0
        elif model is ProductVariant:
            inline.verbose_name = "پروفایل فروش / تنوع"
            inline.verbose_name_plural = "پروفایل‌ها، سایز، وزن، قیمت و موجودی"
            inline.extra = 0


def install() -> None:
    product_admin = admin.site._registry.get(Product)
    if product_admin is None or getattr(product_admin, "_phase50_product_workspace", False):
        return

    admin_cls = product_admin.__class__
    _product_admin_methods(admin_cls)
    _rename_inlines(product_admin)

    readonly = list(getattr(product_admin, "readonly_fields", ()) or ())
    for name in (
        "seo_preview",
        "phase50_gallery_admin",
        "phase50_sales_profiles_admin",
        "phase50_pricing_admin",
        "phase50_shipping_admin",
        "phase50_slider_admin",
        "phase50_license_admin",
        "phase50_windows_sync_admin",
        "view_count",
        "created_at",
        "updated_at",
    ):
        if hasattr(admin_cls, name) or name in {"view_count", "created_at", "updated_at"}:
            if name not in readonly:
                readonly.append(name)
    product_admin.readonly_fields = tuple(readonly)

    product_admin.fieldsets = (
        (
            "اطلاعات کالا",
            {
                "fields": (
                    "category",
                    "title",
                    "title_en",
                    "slug",
                    "sku",
                    "short_description",
                    "short_description_en",
                    "description",
                    "description_en",
                    "dimensions",
                    "technical_notes",
                    "installation_guide",
                    "brand_name",
                    "mpn",
                    "gtin",
                    "material_selection_intro",
                    "hashtags",
                ),
            },
        ),
        (
            "تصاویر",
            {
                "fields": (
                    "main_image",
                    "customer_gallery_enabled",
                    "phase50_gallery_admin",
                ),
                "description": "تصویر اصلی را اینجا تعیین کنید؛ تصاویر تکمیلی در Inline گالری پایین همین صفحه و از لینک مدیریت گالری قابل ویرایش‌اند.",
            },
        ),
        (
            "فروش و موجودی",
            {
                "fields": (
                    "order_mode",
                    "fixed_delivery_days",
                    "consultation_required",
                    "show_public_order_count",
                    "is_featured",
                    "is_active",
                    "published_at",
                ),
            },
        ),
        (
            "پروفایل‌ها و سایز/وزن",
            {
                "fields": (
                    "sales_profile_selection_mode",
                    "sales_profile_selector_label",
                    "phase50_sales_profiles_admin",
                ),
                "description": "روش انتخاب مشتری را تعیین کنید و پروفایل‌های فروش را از Inline پایین صفحه یا صفحه مدیریت پروفایل‌ها کپی/ویرایش کنید.",
            },
        ),
        (
            "قیمت‌گذاری",
            {
                "fields": (
                    "fixed_price",
                    "price_is_final",
                    "price_note",
                    "phase50_pricing_admin",
                ),
                "description": "قیمت ثابت روی Product و قیمت‌گذاری محاسباتی/بازه‌ای روی Product Catalog Profile و پروفایل‌های فروش نگهداری می‌شود.",
            },
        ),
        (
            "ارسال و بسته‌بندی",
            {
                "fields": ("phase50_shipping_admin",),
                "description": "وزن کالا، وزن بسته‌بندی، وزن ارسال و ابعاد بسته برای هر پروفایل فروش مستقل است؛ موتور نرخ حمل Phase50.A.2 از همین داده استفاده می‌کند.",
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_focus_keyword",
                    "meta_title",
                    "meta_description",
                    "canonical_url",
                    "robots_index",
                    "robots_follow",
                    "schema_enabled",
                    "og_title",
                    "og_description",
                    "og_image",
                    "seo_preview",
                ),
                "description": "SEO واقعی صفحه Product: Title/Description/Canonical/Robots/OpenGraph/Schema. این داده‌ها مستقیماً توسط صفحه عمومی محصول مصرف می‌شوند.",
            },
        ),
        (
            "اسلایدر صفحه اول",
            {
                "fields": ("phase50_slider_admin",),
                "description": "تنظیمات انتشار، تصویر، عنوان، توضیح، Alt، Focus Keyword، دکمه و افکت Hero از پروفایل کاتالوگ و Hero Studio مدیریت می‌شود.",
            },
        ),
        (
            "منبع و لایسنس",
            {
                "fields": (
                    "source_url",
                    "source_name",
                    "source_external_id",
                    "editorial_source_url",
                    "source_attribution",
                    "model_file",
                    "phase50_license_admin",
                ),
            },
        ),
        (
            "همگام‌سازی ویندوز",
            {
                "fields": ("phase50_windows_sync_admin",),
                "description": "شناسه Desktop، Batch/Hash، Revision و آخرین منبع تغییر در Product Catalog Profile نگهداری می‌شوند؛ این بخش وضعیت همان قرارداد Windows ↔ Server را نمایش می‌دهد.",
            },
        ),
        (
            "آمار و وضعیت",
            {
                "fields": ("view_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    product_admin._phase50_product_workspace = True
