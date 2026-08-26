from __future__ import annotations

from collections import OrderedDict

from django import template

register = template.Library()


# One navigation source of truth for the business-facing Admin shell.  The
# underlying Django Admin registry remains authoritative; this only classifies
# already-permitted registered models into operator-friendly groups.
GROUP_DEFINITIONS = (
    (
        "commerce",
        "کالا و فروشگاه",
        "ri-store-2-line",
        (
            ("store.product", "محصولات فروشگاه"),
            ("store.category", "دسته‌بندی محصولات"),
            ("store.productvariant", "پروفایل‌ها، تنوع و موجودی"),
            ("store.productcatalogprofile", "پروفایل کاتالوگ و قیمت"),
            ("store.printquality", "کیفیت‌های چاپ"),
            ("store.shippingmethod", "روش‌های ارسال"),
            ("store.storeaddress", "آدرس‌های مشتریان فروشگاه"),
        ),
    ),
    (
        "orders",
        "سفارش و ارسال",
        "ri-shopping-bag-3-line",
        (
            ("store.storeorder", "سفارش‌های فروشگاه"),
            ("store.storeorderevent", "رویدادهای سفارش"),
            ("store.shipment", "ارسال و رهگیری"),
            ("store.returnrequest", "مرجوعی‌ها"),
            ("website.order", "سفارش‌های خدمات"),
            ("website.orderintakedetail", "مشخصات فنی سفارش"),
            ("website.orderattachment", "فایل‌های سفارش"),
            ("website.orderreferencephoto", "تصاویر مرجع سفارش"),
            ("website.quote", "پیش‌فاکتورها"),
        ),
    ),
    (
        "finance",
        "مالی، قیمت و تخفیف",
        "ri-bank-card-line",
        (
            ("store.businessfinancedashboard", "داشبورد مالی"),
            ("store.storepayment", "پرداخت‌های فروشگاه"),
            ("website.payment", "پرداخت خدمات"),
            ("store.storeinvoice", "فاکتورهای فروشگاه"),
            ("store.coupon", "کدهای تخفیف"),
            ("store.couponusage", "مصرف کدهای تخفیف"),
            ("store.pricingsetting", "تنظیمات قیمت‌گذاری"),
            ("store.costentry", "هزینه‌ها"),
            ("store.marketpricingsetting", "تنظیمات قیمت بازار"),
            ("store.exchangerateprovider", "منابع نرخ ارز"),
            ("store.exchangeratesnapshot", "تاریخچه نرخ ارز"),
            ("store.materialmarketpricesnapshot", "تاریخچه قیمت متریال"),
        ),
    ),
    (
        "production",
        "تولید و انبار",
        "ri-printer-line",
        (
            ("store.productionjob", "پروژه‌های تولید"),
            ("store.filamentpurchase", "خرید فیلامنت"),
            ("store.filamentspool", "رول‌های فیلامنت"),
            ("store.filamentmovement", "گردش فیلامنت"),
            ("store.inventorymovement", "گردش موجودی"),
            ("website.material", "متریال‌ها"),
            ("store.bambufilamentcatalogitem", "کاتالوگ فیلامنت Bambu"),
            ("store.bambufilamentpricehistory", "تاریخچه قیمت Bambu"),
        ),
    ),
    (
        "windows_catalog",
        "ورودی ویندوز و کاتالوگ",
        "ri-windows-line",
        (
            ("store.importedprintasset", "مدل‌ها و فایل‌های دریافت‌شده"),
            ("store.printcatalogimportjob", "کارهای دریافت از Windows/Catalog"),
            ("store.catalogsyncdashboard", "داشبورد همگام‌سازی"),
            ("store.catalogsyncrun", "اجرای همگام‌سازی"),
            ("store.catalogassetpublication", "انتشار مدل‌ها"),
            ("store.catalogassetmetrics", "آمار مدل‌های کاتالوگ"),
            ("store.printcatalogsource", "منابع کاتالوگ"),
            ("store.catalogsourcepolicy", "سیاست منابع"),
            ("store.catalogcategoryrule", "قواعد دسته‌بندی"),
            ("store.catalogseedurl", "لینک‌های بذر"),
            ("store.externalsourcefetchlog", "لاگ دریافت منابع"),
            ("store.catalogautomationdashboard", "داشبورد اتوماسیون"),
            ("store.catalogautomationsetting", "تنظیمات اتوماسیون"),
            ("store.catalogsourceschedule", "زمان‌بندی منابع"),
            ("store.catalogqueuedjob", "صف پردازش کاتالوگ"),
        ),
    ),
    (
        "homepage",
        "صفحه اصلی و ظاهر سایت",
        "ri-layout-4-line",
        (
            ("website.homepageheroslide", "Hero Studio / اسلایدر صفحه اول"),
            ("website.homepresentationsetting", "چیدمان و نمایش صفحه اصلی"),
            ("website.sitesetting", "تنظیمات و اطلاعات سایت"),
            ("website.seosettings", "تنظیمات سئو سایت"),
            ("website.portfolioitem", "نمونه‌کارها"),
            ("website.testimonial", "رضایت مشتریان"),
            ("website.faq", "پرسش‌های متداول"),
            ("website.teammember", "اعضای تیم"),
            ("website.clientreference", "مشتریان مرجع"),
        ),
    ),
    (
        "content",
        "محتوا و راهنمای محصول",
        "ri-file-text-line",
        (
            ("store.servicepage", "صفحات خدمات"),
            ("website.product", "محصولات سفارشی سایت"),
            ("website.industryrecommendation", "پیشنهاد متریال صنایع"),
            ("website.partrecommendation", "پیشنهاد متریال قطعات"),
            ("store.productfaq", "پرسش‌های محصول"),
        ),
    ),
    (
        "engagement",
        "مشتریان و تعاملات محصول",
        "ri-heart-3-line",
        (
            ("website.customerprofile", "پرونده مشتریان"),
            ("store.productcomment", "دیدگاه‌های محصولات"),
            ("store.productreview", "امتیاز و نقد خریداران"),
            ("store.productlike", "پسندهای محصولات"),
            ("store.productfavorite", "ذخیره‌ها و علاقه‌مندی‌ها"),
            ("store.productrequest", "درخواست محصول"),
            ("website.customerreusablemodel", "مدل‌های ذخیره‌شده مشتری"),
            ("website.orderreview", "نظرهای سفارش"),
        ),
    ),
    (
        "support",
        "پشتیبانی و اعلان‌ها",
        "ri-customer-service-2-line",
        (
            ("website.supportconversation", "گفت‌وگوهای پشتیبانی"),
            ("website.supportmessage", "همه پیام‌های پشتیبانی"),
            ("store.customernotification", "اعلان‌های مشتری"),
        ),
    ),
    (
        "affiliate",
        "همکاری در فروش",
        "ri-hand-coin-line",
        (
            ("store.affiliateprogramdashboard", "داشبورد همکاری فروش"),
            ("store.affiliatetier", "سطح همکاران"),
            ("store.affiliatepartner", "همکاران فروش"),
            ("store.affiliatecampaign", "کمپین‌ها"),
            ("store.affiliatecommission", "کمیسیون‌ها"),
            ("store.affiliatepayout", "تسویه همکاران"),
            ("store.affiliateledgerentry", "دفتر مالی همکاران"),
        ),
    ),
    (
        "system",
        "تنظیمات و داده‌های پایه",
        "ri-settings-3-line",
        (
            ("website.iranprovince", "استان‌ها"),
            ("website.irancounty", "شهرستان‌ها"),
            ("website.irancity", "شهرها"),
            ("auth.user", "کاربران"),
            ("auth.group", "گروه‌ها و سطح دسترسی"),
        ),
    ),
)


def _normalise_model(app_label, model):
    object_name = str(model.get("object_name") or "").strip()
    if not object_name:
        raw_model = model.get("model")
        object_name = getattr(getattr(raw_model, "_meta", None), "object_name", "")
    key = f"{app_label}.{object_name.lower()}" if object_name else ""
    return key


@register.simple_tag
def admin_console_navigation(available_apps):
    by_key = {}
    complete_registry = []

    for app in available_apps or []:
        app_label = str(app.get("app_label") or "")
        registry_models = []
        for model in app.get("models") or []:
            if not model.get("admin_url"):
                continue
            key = _normalise_model(app_label, model)
            if not key:
                continue
            item = {
                "key": key,
                "label": str(model.get("name") or model.get("object_name") or key),
                "admin_url": model.get("admin_url"),
                "add_url": model.get("add_url"),
                "view_only": bool(model.get("view_only")),
            }
            by_key[key] = item
            registry_models.append(item)
        if registry_models:
            complete_registry.append(
                {
                    "app_label": app_label,
                    "name": str(app.get("name") or app_label),
                    "models": registry_models,
                }
            )

    groups = []
    assigned = set()
    for group_id, title, icon, model_defs in GROUP_DEFINITIONS:
        items = []
        for key, label in model_defs:
            model = by_key.get(key)
            if model is None:
                continue
            item = dict(model)
            item["label"] = label
            items.append(item)
            assigned.add(key)
        if items:
            groups.append(
                {
                    "id": group_id,
                    "title": title,
                    "icon": icon,
                    "items": items,
                }
            )

    unassigned = [model for key, model in by_key.items() if key not in assigned]
    unassigned.sort(key=lambda item: item["label"])

    return {
        "groups": groups,
        "registry": complete_registry,
        "registered_count": len(by_key),
        "unassigned": unassigned,
        "unassigned_count": len(unassigned),
    }
