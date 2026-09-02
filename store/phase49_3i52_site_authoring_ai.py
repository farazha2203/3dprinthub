from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from ai.model_policy import runtime_config_status
from ai.product_content import (
    apply_site_product_proposal,
    build_site_product_proposal,
)
from .epic49_catalog_profile import (
    ProductCatalogProfile,
    ensure_admin_catalog_profile,
)
from .models import Product


class ProductCatalogProfileInline(admin.StackedInline):
    model = ProductCatalogProfile
    extra = 0
    max_num = 1
    can_delete = False
    show_change_link = True
    verbose_name = "پروفایل کاتالوگ / قیمت و تنظیمات سایت"
    verbose_name_plural = "پروفایل کاتالوگ / قیمت و تنظیمات سایت"
    fields = (
        "product_type",
        "use_description",
        "availability_status",
        "stock_quantity",
        "lead_time_min_days",
        "lead_time_max_days",
        "pricing_strategy",
        "price_mode",
        "price_min",
        "price_max",
        "technical_summary_fa",
        "technical_features",
        "keywords",
        "commercial_license_status",
        "license_name",
        "license_url",
        "public_slug",
        "desktop_product_id",
        "sync_revision",
        "last_modified_source",
        "last_modified_by",
        "last_synced_at",
    )
    readonly_fields = (
        "public_slug",
        "desktop_product_id",
        "sync_revision",
        "last_modified_source",
        "last_modified_by",
        "last_synced_at",
    )

    def has_add_permission(self, request, obj=None):
        # A profile is created after the first Product save. This avoids an
        # unsaved-parent inline trying to invent a public slug or duplicate a
        # profile while keeping subsequent edits on the same Product page.
        return False


def _actor(request) -> str:
    user = getattr(request, "user", None)
    if not user:
        return "admin"
    return str(
        getattr(user, "get_username", lambda: "")()
        or getattr(user, "pk", "")
        or "admin"
    )[:120]


def _ai_session_key(product_id: int) -> str:
    return f"phase49_3i52_product_ai_{int(product_id)}"


def _install_methods(admin_cls) -> None:
    if not hasattr(admin_cls, "phase52_ai_admin"):
        @admin.display(description="هوش مصنوعی فارسی روی سایت")
        def phase52_ai_admin(self, obj):
            if not getattr(obj, "pk", None):
                return "پس از اولین ذخیره محصول، AI Preview قابل استفاده است."
            url = reverse(
                "admin:store_product_phase49_3i52_ai",
                args=[obj.pk],
            )
            return format_html(
                '<a class="button" href="{}">AI تکمیل محتوا و SEO — Preview</a>'
                '<div style="margin-top:8px;color:#64748b">'
                'AI قیمت، موجودی، متریال، رنگ، مجوز یا Publish state را تغییر نمی‌دهد.'
                "</div>",
                url,
            )

        admin_cls.phase52_ai_admin = phase52_ai_admin

    if not hasattr(admin_cls, "phase52_site_parity_admin"):
        @admin.display(description="وضعیت ویرایش مستقیم سایت")
        def phase52_site_parity_admin(self, obj):
            if not getattr(obj, "pk", None):
                return "محصول را ذخیره کنید تا پروفایل سایت ایجاد شود."
            try:
                profile = obj.catalog_profile
            except Exception:
                return "پروفایل سایت هنوز ایجاد نشده است؛ با ذخیره همین Product ایجاد می‌شود."
            variants = obj.variants.filter(is_active=True).count()
            strategy = str(
                getattr(profile, "pricing_strategy", "")
                or profile.price_mode
                or "legacy"
            )
            url = reverse(
                "admin:store_productcatalogprofile_change",
                args=[profile.pk],
            )
            return format_html(
                '<div>Profile: <strong>#{}</strong> / Strategy: <strong>{}</strong> / '
                'Variants: <strong>{}</strong> / Revision: <strong>{}</strong></div>'
                '<div style="margin-top:8px"><a class="button" href="{}">'
                "باز کردن پروفایل کامل سایت</a></div>",
                profile.pk,
                strategy,
                variants,
                profile.sync_revision,
                url,
            )

        admin_cls.phase52_site_parity_admin = phase52_site_parity_admin

    if not hasattr(admin_cls, "phase52_ai_view"):
        def phase52_ai_view(self, request, object_id):
            product = self.get_object(request, object_id)
            if product is None:
                return HttpResponseRedirect(
                    reverse("admin:store_product_changelist")
                )
            if not self.has_change_permission(request, product):
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied

            session_key = _ai_session_key(product.pk)
            proposal = request.session.get(session_key)
            if request.method == "POST":
                action = str(request.POST.get("action") or "").strip()
                if action == "generate":
                    try:
                        proposal = build_site_product_proposal(product)
                        request.session[session_key] = proposal
                        request.session.modified = True
                        messages.success(
                            request,
                            "پیشنهاد AI ساخته شد؛ قبل از Apply متن‌ها را بررسی کن.",
                        )
                    except Exception as exc:
                        messages.error(
                            request,
                            f"AI اجرا نشد: {type(exc).__name__}: {exc}",
                        )
                        proposal = None
                elif action == "apply":
                    if not isinstance(proposal, dict):
                        messages.error(
                            request,
                            "پیشنهاد AI در Session موجود نیست؛ ابتدا Generate را بزن.",
                        )
                    else:
                        try:
                            result = apply_site_product_proposal(
                                product,
                                proposal,
                                actor=_actor(request),
                            )
                            request.session.pop(session_key, None)
                            request.session.modified = True
                            messages.success(
                                request,
                                "AI Content/SEO اعمال شد؛ قیمت، موجودی و Facts دست‌نخورده ماند. "
                                f"Product fields={len(result['changed_product_fields'])}, "
                                f"Profile fields={len(result['changed_profile_fields'])}.",
                            )
                            return HttpResponseRedirect(
                                reverse(
                                    "admin:store_product_change",
                                    args=[product.pk],
                                )
                            )
                        except Exception as exc:
                            messages.error(
                                request,
                                f"Apply ناموفق بود: {type(exc).__name__}: {exc}",
                            )
                elif action == "discard":
                    request.session.pop(session_key, None)
                    request.session.modified = True
                    proposal = None
                    messages.info(request, "پیشنهاد AI حذف شد.")

            context = {
                **self.admin_site.each_context(request),
                "opts": self.model._meta,
                "original": product,
                "title": f"AI محتوا و SEO — {product.title}",
                "product": product,
                "proposal": proposal,
                "ai_status": runtime_config_status(),
                "change_url": reverse(
                    "admin:store_product_change",
                    args=[product.pk],
                ),
            }
            return TemplateResponse(
                request,
                "admin/store/product/phase49_3i52_ai.html",
                context,
            )

        admin_cls.phase52_ai_view = phase52_ai_view


def install() -> None:
    product_admin = admin.site._registry.get(Product)
    if (
        product_admin is None
        or getattr(product_admin, "_phase49_3i52_site_authoring_ai", False)
    ):
        return

    admin_cls = product_admin.__class__
    _install_methods(admin_cls)

    if not any(
        getattr(inline, "model", None) is ProductCatalogProfile
        for inline in getattr(product_admin, "inlines", ())
    ):
        product_admin.inlines = [
            *list(getattr(product_admin, "inlines", ()) or ()),
            ProductCatalogProfileInline,
        ]

    readonly = list(getattr(product_admin, "readonly_fields", ()) or ())
    for name in ("phase52_ai_admin", "phase52_site_parity_admin"):
        if name not in readonly:
            readonly.append(name)
    product_admin.readonly_fields = tuple(readonly)

    fieldsets = list(getattr(product_admin, "fieldsets", ()) or ())
    if not any(title == "هوش مصنوعی و کنترل مستقیم سایت" for title, _ in fieldsets):
        insert_at = 1 if fieldsets else 0
        fieldsets.insert(
            insert_at,
            (
                "هوش مصنوعی و کنترل مستقیم سایت",
                {
                    "fields": (
                        "phase52_ai_admin",
                        "phase52_site_parity_admin",
                    ),
                    "description": (
                        "وقتی Windows Catalog Center در دسترس نیست، Product را همین‌جا "
                        "اضافه/ویرایش کن. Profile/Variant/قیمت از همان مدل‌های اصلی سایت "
                        "استفاده می‌کنند؛ AI فقط Content/SEO را با Preview تکمیل می‌کند."
                    ),
                },
            ),
        )
        product_admin.fieldsets = tuple(fieldsets)

    original_save_related = admin_cls.save_related
    if not getattr(admin_cls, "_phase49_3i52_save_related_wrapped", False):
        def save_related(self, request, form, formsets, change):
            original_save_related(self, request, form, formsets, change)
            ensure_admin_catalog_profile(
                form.instance,
                actor=_actor(request),
                bump_revision=True,
            )

        admin_cls.save_related = save_related
        admin_cls._phase49_3i52_save_related_wrapped = True

    original_get_urls = admin_cls.get_urls
    if not getattr(admin_cls, "_phase49_3i52_urls_wrapped", False):
        def get_urls(self):
            custom = [
                path(
                    "<path:object_id>/phase49-3i52-ai/",
                    self.admin_site.admin_view(self.phase52_ai_view),
                    name="store_product_phase49_3i52_ai",
                )
            ]
            return custom + original_get_urls(self)

        admin_cls.get_urls = get_urls
        admin_cls._phase49_3i52_urls_wrapped = True

    product_admin._phase49_3i52_site_authoring_ai = True
