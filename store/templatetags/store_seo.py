from __future__ import annotations

import json
import re
from urllib.parse import urlencode

from django import template
from django.utils.safestring import mark_safe

from store.phase50_public_offer import first_orderable_variant, public_variant_price
from store.phase50_orderability import variant_is_orderable

register = template.Library()


_CATEGORY_SEARCH_COPY_FA = {
    "mounts-brackets": (
        "پایه‌ها و براکت‌های چاپ سه‌بعدی | 3DprintHub",
        "مدل‌های پایه و براکت چاپ سه‌بعدی را بررسی کنید؛ مشخصات، تصاویر و وضعیت سفارش هر مورد در صفحه همان محصول آمده است.",
    ),
    "plant-pots": (
        "گلدان و اکسسوری دکوراتیو چاپ سه‌بعدی | 3DprintHub",
        "مدل‌های گلدان و اکسسوری دکوراتیو چاپ سه‌بعدی را ببینید و مشخصات و گزینه‌های سفارش هر محصول را در صفحه آن بررسی کنید.",
    ),
    "toys-games": (
        "اسباب‌بازی و بازی‌های چاپ سه‌بعدی | 3DprintHub",
        "مدل‌های اسباب‌بازی و بازی چاپ سه‌بعدی را مرور کنید؛ تصاویر، مشخصات و وضعیت سفارش هر مدل در صفحه محصول درج شده است.",
    ),
}
_CATEGORY_LABEL_FA = {
    "mounts-brackets": "پایه‌ها و براکت‌ها",
    "plant-pots": "گلدان‌ها و اکسسوری‌های دکوراتیو",
    "toys-games": "اسباب‌بازی و بازی‌ها",
}


def _category_label_fa(category):
    name = str(getattr(category, "name", "") or "").strip()
    if re.search(r"[\u0600-\u06ff]", name):
        return name
    return _CATEGORY_LABEL_FA.get(str(getattr(category, "slug", "")), name)


@register.simple_tag
def category_search_label(category):
    return _category_label_fa(category)


@register.simple_tag
def category_search_title(category):
    if not category:
        return ""
    configured = str(getattr(category, "meta_title", "") or "").strip()
    if re.search(r"[\u0600-\u06ff]", configured):
        return configured
    fallback = _CATEGORY_SEARCH_COPY_FA.get(str(getattr(category, "slug", "")))
    if fallback:
        return fallback[0]
    return str(getattr(category, "name", "") or configured).strip()


@register.simple_tag
def category_search_description(category):
    if not category:
        return ""
    meta_description = str(getattr(category, "meta_description", "") or "").strip()
    if meta_description:
        return meta_description
    description = str(getattr(category, "description", "") or "").strip()
    name = str(getattr(category, "name", "") or "").strip()
    if description:
        return f"{name} | {description[:145]}" if name else description[:160]
    fallback = _CATEGORY_SEARCH_COPY_FA.get(str(getattr(category, "slug", "")))
    if fallback:
        return fallback[1]
    return f"محصولات دسته {name} در 3DPrintHub؛ مشاهده مدل‌ها و بررسی گزینه‌های چاپ سه‌بعدی قابل سفارش." if name else ""


@register.simple_tag
def category_social_description(category):
    if not category:
        return ""
    value = str(getattr(category, "og_description", "") or "").strip()
    if value:
        return value
    return category_search_description(category)


def _json(data):
    return mark_safe(json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=str))


def _absolute(request, value):
    if not value:
        return ""
    if str(value).startswith(("http://", "https://")):
        return str(value)
    return request.build_absolute_uri(value)


def _organization(seo, request):
    if not seo:
        return {"@type":"ProfessionalService", "name":"3DprintHub", "url":request.build_absolute_uri("/")}
    organization_name = str(seo.organization_name or seo.site_name or "3DprintHub").strip()
    item = {"@type":"ProfessionalService", "@id":seo.site_url.rstrip("/") + "/#organization", "name":organization_name, "url":seo.site_url}
    if seo.organization_logo:
        item["logo"] = _absolute(request, seo.organization_logo.url)
    if seo.organization_phone:
        item["telephone"] = seo.organization_phone
    if seo.organization_email:
        item["email"] = seo.organization_email
    if any([seo.street_address, seo.address_locality, seo.address_region, seo.organization_postal_code]):
        address_locality = str(seo.address_locality or "").strip()
        address_region = str(seo.address_region or "").strip()
        if address_locality.casefold() == "hwtihk" and address_region == "اصفهان":
            address_locality = address_region
        address = {"@type":"PostalAddress", "addressCountry":seo.country_code or "IR"}
        for key, value in (("streetAddress", seo.street_address), ("addressLocality", address_locality), ("addressRegion", address_region), ("postalCode", seo.organization_postal_code)):
            if str(value or "").strip():
                address[key] = str(value).strip()
        item["address"] = address
    same_as = [line.strip() for line in (seo.same_as or "").splitlines() if line.strip()]
    verified_instagram = "https://www.instagram.com/3dprinthub_ir/"
    if verified_instagram not in same_as:
        same_as.append(verified_instagram)
    if same_as:
        item["sameAs"] = same_as
    # Return-policy markup is intentionally omitted until the merchant
    # explicitly verifies a public return policy. The legacy model default is
    # not sufficient evidence for a Google-facing commercial claim.
    return item


@register.simple_tag
def organization_schema_json(seo, request):
    if not seo:
        return _json({})
    organization_name = str(seo.organization_name or seo.site_name or "3DprintHub").strip()
    site_name = str(seo.site_name or organization_name).strip()
    website = {"@type":"WebSite", "@id":seo.site_url.rstrip("/") + "/#website", "url":seo.site_url, "name":organization_name, "publisher":{"@id":seo.site_url.rstrip("/") + "/#organization"}}
    if site_name and site_name.casefold() != organization_name.casefold():
        website["alternateName"] = site_name
    graph = [_organization(seo, request), website]
    return _json({"@context":"https://schema.org", "@graph":graph})


def _breadcrumb(request, parts):
    items=[]
    for index, part in enumerate(parts, start=1):
        name, url = part
        item={"@type":"ListItem", "position":index, "name":name}
        if url:
            item["item"]=_absolute(request, url)
        items.append(item)
    return {"@type":"BreadcrumbList", "itemListElement":items}


def _catalog_profile(product):
    try:
        return product.catalog_profile
    except Exception:
        return None


@register.simple_tag
def product_schema_json(product, variants, request, seo):
    if not getattr(product, "schema_enabled", True):
        return _json({})
    images=[]
    for candidate in [
        _absolute(request, product.main_image.url),
        *[
            _absolute(request, obj.image.url)
            for obj in product.images.all()[:8]
        ],
    ]:
        if candidate and candidate not in images:
            images.append(candidate)
    url=_absolute(request, product.get_absolute_url())
    group_id=f"{url}#product"
    group={"@type":"ProductGroup", "@id":group_id, "name":product.title, "description":product.short_description, "url":url, "image":images, "productGroupID":product.sku, "brand":{"@type":"Brand", "name":product.brand_name or "3DprintHub"}, "category":_category_label_fa(product.category), "variesBy":["https://schema.org/material", "https://schema.org/color"]}
    # Fixed-price products use their own direct offer, never stale variant prices.
    sellable_variants = [
        variant
        for variant in variants
        if product.order_mode != "fixed"
        and public_variant_price(variant) > 0
    ]
    # First Google Offer must match the first orderable product configuration.
    default_variant = first_orderable_variant(product, sellable_variants)
    if default_variant:
        sellable_variants = [default_variant] + [
            variant for variant in sellable_variants if variant.pk != default_variant.pk
        ]

    profile = _catalog_profile(product)
    if profile is not None:
        keywords = [str(item).strip() for item in (profile.keywords or []) if str(item).strip()]
        if keywords:
            group["keywords"] = ", ".join(keywords[:30])
        # Google's ProductGroup variant contract uses Offer per Product variant.
        # A catalog-profile min/max is not an AggregateOffer from other sellers;
        # publishing it here misrepresents variants and can trigger rich-result errors.
        product_type_label = str(getattr(profile, "product_type_label", "") or profile.product_type or "").strip()
        availability_label = str(getattr(profile, "availability_status_label", "") or profile.availability_status or "").strip()
        additional = [
            {"@type":"PropertyValue", "name":"نوع محصول", "value":product_type_label},
            {"@type":"PropertyValue", "name":"وضعیت عرضه", "value":availability_label},
            {"@type":"PropertyValue", "name":"حداقل زمان آماده‌سازی", "value":profile.lead_time_min_days, "unitText":"روز"},
            {"@type":"PropertyValue", "name":"حداکثر زمان آماده‌سازی", "value":profile.lead_time_max_days, "unitText":"روز"},
        ]
        for key, value in list((profile.technical_features or {}).items())[:20]:
            if value not in (None, "", [], {}):
                additional.append({"@type":"PropertyValue", "name":str(key), "value":str(value)[:300]})
        group["additionalProperty"] = additional

    has_variant=[]
    availability={"in_stock":"https://schema.org/InStock", "made_to_order":"https://schema.org/PreOrder", "preorder":"https://schema.org/PreOrder", "out_of_stock":"https://schema.org/OutOfStock"}
    for variant in sellable_variants:
        stock_key = variant.stock_status
        if not variant_is_orderable(variant):
            stock_key = "out_of_stock"
        elif getattr(variant, "track_inventory", False) and not getattr(variant, "allow_backorder", False) and variant.available_quantity <= 0:
            stock_key = "out_of_stock"
        elif getattr(variant, "track_inventory", False) and getattr(variant, "allow_backorder", False) and variant.available_quantity <= 0:
            stock_key = "preorder"
        variant_url = f"{url}?{urlencode({'variant': variant.code})}"
        offer={"@type":"Offer", "url":variant_url, "priceCurrency":"IRR", "price":public_variant_price(variant)*10, "availability":availability.get(stock_key, "https://schema.org/InStock"), "itemCondition":"https://schema.org/NewCondition", "seller":{"@id":(seo.site_url.rstrip("/") + "/#organization") if seo else url + "#seller"}}
        # Zero is the legacy "not configured" value, not a promise of free
        # shipping. Emit Google shipping data only when an explicit amount exists.
        if seo and int(seo.shipping_rate or 0) > 0:
            offer["shippingDetails"]={"@type":"OfferShippingDetails", "shippingRate":{"@type":"MonetaryAmount", "value":int(seo.shipping_rate)*10, "currency":"IRR"}, "shippingDestination":{"@type":"DefinedRegion", "addressCountry":seo.country_code or "IR"}, "deliveryTime":{"@type":"ShippingDeliveryTime", "handlingTime":{"@type":"QuantitativeValue", "minValue":seo.handling_min_days, "maxValue":seo.handling_max_days, "unitCode":"DAY"}, "transitTime":{"@type":"QuantitativeValue", "minValue":seo.transit_min_days, "maxValue":seo.transit_max_days, "unitCode":"DAY"}}}
        variant_name=f"{product.title} - {variant.material.name}" + (f" - {variant.color.name}" if getattr(variant, "color_id", None) else "") + f" - {variant.quality.name}"
        item={
            "@type":"Product",
            "url":variant_url,
            "name":variant_name,
            "description":product.short_description,
            "image":images,
            "sku":variant.code,
            "brand":{"@type":"Brand", "name":product.brand_name or "3DprintHub"},
            "category":_category_label_fa(product.category),
            "material":variant.material.name,
            "isVariantOf":{"@id":group_id},
            "offers":offer,
        }
        if getattr(variant, "color_id", None): item["color"]=variant.color.name
        if product.mpn: item["mpn"]=product.mpn
        if product.gtin: item["gtin"]=product.gtin
        has_variant.append(item)
    if has_variant:
        group["hasVariant"]=has_variant
    reviews=list(product.reviews.filter(is_approved=True).select_related("user")[:5])
    if reviews:
        average=sum(item.rating for item in reviews)/len(reviews)
        group["aggregateRating"]={"@type":"AggregateRating", "ratingValue":round(average,2), "reviewCount":product.reviews.filter(is_approved=True).count(), "bestRating":5, "worstRating":1}
        group["review"]=[{"@type":"Review", "author":{"@type":"Person", "name":r.user.get_full_name() or r.user.username}, "reviewRating":{"@type":"Rating", "ratingValue":r.rating, "bestRating":5}, "name":r.title or "نظر خریدار", "reviewBody":r.body} for r in reviews]
    if has_variant:
        # Single-page product families: Google reads actual individual Offers.
        structured_product = group
    else:
        # A ProductGroup without variants is not a purchasable product.
        # Only expose a standalone Product when a real fixed offer or
        # authentic approved reviews substantiate the rich-result data.
        fixed_price = int(getattr(product, "fixed_price", 0) or 0)
        has_fixed_offer = product.order_mode == "fixed" and fixed_price > 0
        if has_fixed_offer or reviews:
            structured_product = {
                key: value
                for key, value in group.items()
                if key not in ("productGroupID", "variesBy")
            }
            structured_product["@type"] = "Product"
            if has_fixed_offer:
                structured_product["offers"] = {
                    "@type": "Offer",
                    "url": url,
                    "price": fixed_price * 10,
                    "priceCurrency": "IRR",
                    "availability": "https://schema.org/PreOrder",
                    "itemCondition": "https://schema.org/NewCondition",
                    "seller": {
                        "@id": (seo.site_url.rstrip("/") + "/#organization")
                        if seo else url + "#seller"
                    },
                }
        else:
            structured_product = None
    breadcrumb = _breadcrumb(request, [("خانه", "/"), ("فروشگاه", "/store/"), (_category_label_fa(product.category), product.category.get_absolute_url()), (product.title, "")])
    graph = ([structured_product] if structured_product else []) + [breadcrumb]
    return _json({"@context":"https://schema.org", "@graph":graph})


@register.simple_tag
def product_list_schema_json(products, request, current_category=None):
    items=[]
    for position, product in enumerate(list(products)[:50], start=1):
        items.append({"@type":"ListItem", "position":position, "url":_absolute(request, product.get_absolute_url()), "name":product.title})
    title=_category_label_fa(current_category) if current_category else "فروشگاه قطعات آماده چاپ سه‌بعدی"
    canonical=current_category.get_absolute_url() if current_category else "/store/"
    graph=[{"@type":"CollectionPage", "name":title, "url":_absolute(request, canonical), "mainEntity":{"@type":"ItemList", "numberOfItems":len(items), "itemListElement":items}}, _breadcrumb(request, [("خانه", "/"), ("فروشگاه", "/store/"), (title, "")])]
    return _json({"@context":"https://schema.org", "@graph":graph})


@register.simple_tag
def service_schema_json(page, request, seo, guide=None):
    url=_absolute(request, page.get_absolute_url())
    description = (guide or {}).get("lead") or page.short_description
    graph=[{"@type":"Service", "name":page.title, "description":description, "url":url, "provider":{"@id":(seo.site_url.rstrip("/") + "/#organization") if seo else url + "#provider"}, "areaServed":{"@type":"Country", "name":"ایران"}}, _breadcrumb(request, [("خانه", "/"), ("خدمات", "/#services"), (page.title, "")])]
    return _json({"@context":"https://schema.org", "@graph":graph})


@register.simple_tag
def service_landing_schema_json(profile, slug, request, seo):
    url = _absolute(request, f"/store/services/{slug}/")
    service = {
        "@type": "Service",
        "name": profile["title"],
        "description": profile["meta_description"],
        "url": url,
        "provider": {"@id": (seo.site_url.rstrip("/") + "/#organization") if seo else _absolute(request, "/#organization")},
        "areaServed": {"@type": "Country", "name": profile.get("area", "ایران")},
    }
    graph = [service, _breadcrumb(request, [("خانه", "/"), ("خدمات", "/#services"), (profile["title"], "")])]
    return _json({"@context": "https://schema.org", "@graph": graph})


@register.simple_tag
def isfahan_service_schema_json(request, seo):
    url = _absolute(request, "/store/services/3d-printing-isfahan/")
    provider = {"@id": (seo.site_url.rstrip("/") + "/#organization") if seo else _absolute(request, "/#organization")}
    service = {
        "@type": "Service",
        "name": "چاپ سه‌بعدی و مهندسی معکوس در اصفهان",
        "description": "طراحی سه‌بعدی، بازسازی قطعات از روی نمونه و چاپ سه‌بعدی صنعتی برای پروژه‌های اصفهان؛ امکان‌سنجی و برآورد پس از بررسی فنی.",
        "url": url,
        "provider": provider,
        "areaServed": {"@type": "City", "name": "اصفهان", "containedInPlace": {"@type": "AdministrativeArea", "name": "استان اصفهان"}},
        "availableChannel": {"@type": "ServiceChannel", "serviceUrl": url},
    }
    graph = [service, _breadcrumb(request, [("خانه", "/"), ("خدمات", "/#services"), ("چاپ سه‌بعدی در اصفهان", url)])]
    return _json({"@context": "https://schema.org", "@graph": graph})


@register.simple_tag
def product_faq_schema_json(product, request):
    faqs = list(product.faqs.filter(is_active=True)[:20])
    if not faqs:
        return _json({})
    return _json({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": _absolute(request, product.get_absolute_url()) + "#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item.question,
                "acceptedAnswer": {"@type": "Answer", "text": item.answer},
            }
            for item in faqs
        ],
    })
