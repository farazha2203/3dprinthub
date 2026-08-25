from __future__ import annotations

from dataclasses import dataclass

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse


@dataclass(frozen=True)
class CommandLink:
    label: str
    url: str
    note: str = ""


def _safe_admin_link(request, *, permission: str, url_name: str, label: str, note: str = ""):
    if not request.user.has_perm(permission):
        return None
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        return None
    return CommandLink(label=label, url=url, note=note)


def _section(request, title: str, icon: str, definitions: list[tuple[str, str, str, str]]):
    links = []
    for permission, url_name, label, note in definitions:
        link = _safe_admin_link(
            request,
            permission=permission,
            url_name=url_name,
            label=label,
            note=note,
        )
        if link:
            links.append(link)
    return {"title": title, "icon": icon, "links": links}


def phase50_admin_command_center(request):
    """Business-oriented Admin entry point using only already-registered models.

    Phase50.A deliberately adds no accounting schema. It organizes the mature
    operational models first so finance/sales/purchasing work is visible and
    permission-aware before Phase50.B introduces double-entry accounting.
    """

    from store.models import (
        AffiliatePayout,
        CostEntry,
        FilamentPurchase,
        StoreOrder,
        StorePayment,
    )
    from website.models import Payment

    service_pending = Payment.objects.filter(status__in=["pending", "awaiting_review"]).count()
    store_pending = StorePayment.objects.filter(status__in=["pending", "awaiting_review"]).count()
    active_store_orders = StoreOrder.objects.filter(
        status__in=["paid", "processing", "ready", "shipped"]
    ).count()
    draft_purchases = FilamentPurchase.objects.filter(status="draft").count()
    open_payouts = AffiliatePayout.objects.filter(status__in=["requested", "approved"]).count()
    open_cost_entries = CostEntry.objects.count()

    sections = [
        _section(
            request,
            "فروش",
            "ri-shopping-cart-2-line",
            [
                ("website.view_order", "admin:website_order_changelist", "سفارش‌های خدمات", "ثبت سفارش‌های چاپ و ساخت سفارشی"),
                ("website.view_quote", "admin:website_quote_changelist", "پیش‌فاکتورهای خدمات", "قیمت‌گذاری، بیعانه و مانده"),
                ("store.view_storeorder", "admin:store_storeorder_changelist", "سفارش‌های فروشگاه", "فروش محصولات، وضعیت تولید و تحویل"),
                ("store.view_storeinvoice", "admin:store_storeinvoice_changelist", "فاکتورهای فروشگاه", "اسناد فروش صادرشده"),
                ("store.view_returnrequest", "admin:store_returnrequest_changelist", "مرجوعی‌های فروش", "درخواست‌ها و چرخه بازگشت کالا"),
            ],
        ),
        _section(
            request,
            "خزانه‌داری",
            "ri-bank-card-line",
            [
                ("website.view_payment", "admin:website_payment_changelist", "دریافت‌های خدمات", "کارت‌به‌کارت، بیعانه، تسویه و درگاه"),
                ("store.view_storepayment", "admin:store_storepayment_changelist", "پرداخت‌های فروشگاه", "پرداخت‌های متصل به سفارش فروشگاهی"),
                ("store.view_affiliatepayout", "admin:store_affiliatepayout_changelist", "تسویه همکاران فروش", "پرداخت پورسانت و شماره پیگیری"),
                ("website.change_sitesetting", "admin:website_sitesetting_changelist", "تنظیمات پرداخت", "کارت دریافت وجه و درگاه آنلاین"),
            ],
        ),
        _section(
            request,
            "حسابداری و دفاتر موجود",
            "ri-book-2-line",
            [
                ("website.view_paymentledgerentry", "admin:website_paymentledgerentry_changelist", "دفتر رخدادهای پرداخت خدمات", "دفتر immutable پرداخت‌های خدمات"),
                ("store.view_affiliateledgerentry", "admin:store_affiliateledgerentry_changelist", "دفتر مالی همکاران", "کمیسیون و تسویه همکاران فروش"),
                ("store.view_businessfinancedashboard", "admin:store_businessfinancedashboard_changelist", "داشبورد مالی و سود", "درآمد، هزینه، تولید و موجودی فعلی"),
                ("store.view_costentry", "admin:store_costentry_changelist", "هزینه‌ها و درآمدهای جانبی", "هزینه‌های پروژه و هزینه‌های عمومی"),
            ],
        ),
        _section(
            request,
            "خرید و تأمین",
            "ri-truck-line",
            [
                ("store.view_filamentpurchase", "admin:store_filamentpurchase_changelist", "خریدهای فیلامنت", "فاکتور خرید و ورود رول به انبار"),
                ("store.view_filamentspool", "admin:store_filamentspool_changelist", "رول‌های فیلامنت", "موجودی واقعی و بهای تمام‌شده"),
                ("store.view_filamentmovement", "admin:store_filamentmovement_changelist", "گردش خرید و مصرف فیلامنت", "ورود، مصرف، پرت، اصلاح و برگشت"),
            ],
        ),
        _section(
            request,
            "انبار و تولید",
            "ri-printer-line",
            [
                ("store.view_productionjob", "admin:store_productionjob_changelist", "پروژه‌های تولید", "اتصال فروش به تولید و سود پروژه"),
                ("store.view_inventorymovement", "admin:store_inventorymovement_changelist", "گردش موجودی فروشگاه", "رزرو، خروج و اصلاح موجودی"),
                ("store.view_productvariant", "admin:store_productvariant_changelist", "تنوع و موجودی محصولات", "موجودی قابل فروش و هشدار کمبود"),
                ("website.view_material", "admin:website_material_changelist", "متریال‌ها", "قیمت خرید/فروش و موجودی وزنی"),
            ],
        ),
    ]

    context = {
        **admin.site.each_context(request),
        "title": "مرکز مالی، فروش و عملیات 3DPrintHub",
        "phase50_sections": [section for section in sections if section["links"]],
        "phase50_metrics": [
            ("پرداخت خدمات در انتظار", service_pending),
            ("پرداخت فروشگاه در انتظار", store_pending),
            ("سفارش فروشگاهی فعال", active_store_orders),
            ("خرید فیلامنت پیش‌نویس", draft_purchases),
            ("تسویه همکار باز", open_payouts),
            ("ردیف هزینه ثبت‌شده", open_cost_entries),
        ],
        "phase50_future": [
            "کدینگ حساب‌ها: کل / معین / تفصیلی",
            "اسناد حسابداری دوطرفه و دفتر روزنامه",
            "حساب بانکی، صندوق، دریافت و پرداخت عمومی",
            "تأمین‌کننده و فاکتور خرید عمومی",
            "دفتر مشتری/تأمین‌کننده و تراز آزمایشی",
            "تطبیق بانکی، استرداد کنترل‌شده و گزارش‌های مالی",
        ],
    }
    return TemplateResponse(request, "admin/phase50_command_center.html", context)


def install_admin_completeness() -> None:
    """Add safe browsing ergonomics to mature ModelAdmins without schema changes."""

    from store.models import AffiliatePayout, CostEntry, FilamentPurchase, ProductionJob, StoreOrder, StorePayment
    from website.models import Payment, PaymentLedgerEntry

    contracts = {
        Payment: {"date_hierarchy": "created_at", "list_per_page": 50},
        PaymentLedgerEntry: {"date_hierarchy": "created_at", "list_per_page": 50},
        StorePayment: {"date_hierarchy": "created_at", "list_per_page": 50},
        StoreOrder: {"date_hierarchy": "created_at", "list_per_page": 50},
        FilamentPurchase: {"date_hierarchy": "purchased_at", "list_per_page": 50},
        CostEntry: {"date_hierarchy": "incurred_at", "list_per_page": 50},
        ProductionJob: {"date_hierarchy": "created_at", "list_per_page": 50},
        AffiliatePayout: {"date_hierarchy": "requested_at", "list_per_page": 50},
    }

    for model, options in contracts.items():
        model_admin = admin.site._registry.get(model)
        if model_admin is None:
            continue
        for name, value in options.items():
            setattr(model_admin, name, value)
