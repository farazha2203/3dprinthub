from __future__ import annotations

import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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
        return {"@type":"Organization", "name":"3DprintHub", "url":request.build_absolute_uri("/")}
    item = {"@type":"Organization", "@id":seo.site_url.rstrip("/") + "/#organization", "name":seo.organization_name, "url":seo.site_url}
    if seo.organization_logo:
        item["logo"] = _absolute(request, seo.organization_logo.url)
    if seo.organization_phone:
        item["telephone"] = seo.organization_phone
    if seo.organization_email:
        item["email"] = seo.organization_email
    if any([seo.street_address, seo.address_locality, seo.address_region, seo.organization_postal_code]):
        item["address"] = {"@type":"PostalAddress", "streetAddress":seo.street_address, "addressLocality":seo.address_locality, "addressRegion":seo.address_region, "postalCode":seo.organization_postal_code, "addressCountry":seo.country_code or "IR"}
    same_as = [line.strip() for line in (seo.same_as or "").splitlines() if line.strip()]
    if same_as:
        item["sameAs"] = same_as
    item["hasMerchantReturnPolicy"] = {"@type":"MerchantReturnPolicy", "applicableCountry":seo.country_code or "IR", "returnPolicyCountry":seo.country_code or "IR", "returnPolicyCategory":"https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays":seo.merchant_return_days, "returnMethod":"https://schema.org/ReturnByMail", "returnFees":"https://schema.org/ReturnShippingFees"}
    return item


@register.simple_tag
def organization_schema_json(seo, request):
    if not seo:
        return _json({})
    graph = [_organization(seo, request), {"@type":"WebSite", "@id":seo.site_url.rstrip("/") + "/#website", "url":seo.site_url, "name":seo.site_name, "publisher":{"@id":seo.site_url.rstrip("/") + "/#organization"}, "potentialAction":{"@type":"SearchAction", "target":seo.site_url.rstrip("/") + "/store/?q={search_term_string}", "query-input":"required name=search_term_string"}}]
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
    images=[_absolute(request, product.main_image.url)]
    images += [_absolute(request, obj.image.url) for obj in product.images.all()[:8]]
    url=_absolute(request, product.get_absolute_url())
    group_id=f"{url}#product"
    group={"@type":"ProductGroup", "@id":group_id, "name":product.title, "description":product.short_description, "url":url, "image":images, "productGroupID":product.sku, "brand":{"@type":"Brand", "name":product.brand_name or "3DprintHub"}, "category":product.category.name, "variesBy":["https://schema.org/material", "https://schema.org/color"]}

    profile = _catalog_profile(product)
    if profile is not None:
        keywords = [str(item).strip() for item in (profile.keywords or []) if str(item).strip()]
        if keywords:
            group["keywords"] = ", ".join(keywords[:30])
        if profile.price_min or profile.price_max:
            low = int(profile.price_min or profile.price_max or 0) * 10
            high = int(profile.price_max or profile.price_min or 0) * 10
            if low and high:
                if high < low:
                    low, high = high, low
                group["offers"] = {
                    "@type": "AggregateOffer",
                    "url": url,
                    "priceCurrency": "IRR",
                    "lowPrice": low,
                    "highPrice": high,
                    "offerCount": max(1, len(variants)),
                }
        additional = [
            {"@type":"PropertyValue", "name":"نوع محصول", "value":profile.product_type},
            {"@type":"PropertyValue", "name":"وضعیت عرضه", "value":profile.availability_status},
            {"@type":"PropertyValue", "name":"حداقل زمان آماده‌سازی", "value":profile.lead_time_min_days, "unitText":"روز"},
            {"@type":"PropertyValue", "name":"حداکثر زمان آماده‌سازی", "value":profile.lead_time_max_days, "unitText":"روز"},
        ]
        for key, value in list((profile.technical_features or {}).items())[:20]:
            if value not in (None, "", [], {}):
                additional.append({"@type":"PropertyValue", "name":str(key), "value":str(value)[:300]})
        group["additionalProperty"] = additional

    has_variant=[]
    availability={"in_stock":"https://schema.org/InStock", "made_to_order":"https://schema.org/PreOrder", "preorder":"https://schema.org/PreOrder", "out_of_stock":"https://schema.org/OutOfStock"}
    for variant in variants:
        stock_key = variant.stock_status
        if getattr(variant, "track_inventory", False) and not getattr(variant, "allow_backorder", False) and variant.available_quantity <= 0:
            stock_key = "out_of_stock"
        elif getattr(variant, "track_inventory", False) and getattr(variant, "allow_backorder", False) and variant.available_quantity <= 0:
            stock_key = "preorder"
        offer={"@type":"Offer", "url":url, "priceCurrency":"IRR", "price":int(variant.cached_unit_price)*10, "availability":availability.get(stock_key, "https://schema.org/InStock"), "itemCondition":"https://schema.org/NewCondition", "seller":{"@id":(seo.site_url.rstrip("/") + "/#organization") if seo else url + "#seller"}}
        if seo:
            offer["shippingDetails"]={"@type":"OfferShippingDetails", "shippingRate":{"@type":"MonetaryAmount", "value":int(seo.shipping_rate)*10, "currency":"IRR"}, "shippingDestination":{"@type":"DefinedRegion", "addressCountry":seo.country_code or "IR"}, "deliveryTime":{"@type":"ShippingDeliveryTime", "handlingTime":{"@type":"QuantitativeValue", "minValue":seo.handling_min_days, "maxValue":seo.handling_max_days, "unitCode":"DAY"}, "transitTime":{"@type":"QuantitativeValue", "minValue":seo.transit_min_days, "maxValue":seo.transit_max_days, "unitCode":"DAY"}}}
        variant_name=f"{product.title} - {variant.material.name}" + (f" - {variant.color.name}" if getattr(variant, "color_id", None) else "") + f" - {variant.quality.name}"
        item={"@type":"Product", "name":variant_name, "sku":variant.code, "material":variant.material.name, "isVariantOf":{"@id":group_id}, "offers":offer}
        if getattr(variant, "color_id", None): item["color"]=variant.color.name
        if product.mpn: item["mpn"]=product.mpn
        if product.gtin: item["gtin"]=product.gtin
        has_variant.append(item)
    group["hasVariant"]=has_variant
    reviews=list(product.reviews.filter(is_approved=True).select_related("user")[:5])
    if reviews:
        average=sum(item.rating for item in reviews)/len(reviews)
        group["aggregateRating"]={"@type":"AggregateRating", "ratingValue":round(average,2), "reviewCount":product.reviews.filter(is_approved=True).count(), "bestRating":5, "worstRating":1}
        group["review"]=[{"@type":"Review", "author":{"@type":"Person", "name":r.user.get_full_name() or r.user.username}, "reviewRating":{"@type":"Rating", "ratingValue":r.rating, "bestRating":5}, "name":r.title or "نظر خریدار", "reviewBody":r.body} for r in reviews]
    graph=[group, _breadcrumb(request, [("خانه", "/"), ("فروشگاه", "/store/"), (product.category.name, product.category.get_absolute_url()), (product.title, "")])]
    return _json({"@context":"https://schema.org", "@graph":graph})


@register.simple_tag
def product_list_schema_json(products, request, current_category=None):
    items=[]
    for position, product in enumerate(list(products)[:50], start=1):
        items.append({"@type":"ListItem", "position":position, "url":_absolute(request, product.get_absolute_url()), "name":product.title})
    title=current_category.name if current_category else "فروشگاه قطعات آماده چاپ سه‌بعدی"
    canonical=current_category.get_absolute_url() if current_category else "/store/"
    graph=[{"@type":"CollectionPage", "name":title, "url":_absolute(request, canonical), "mainEntity":{"@type":"ItemList", "numberOfItems":len(items), "itemListElement":items}}, _breadcrumb(request, [("خانه", "/"), ("فروشگاه", "/store/"), (title, "")])]
    return _json({"@context":"https://schema.org", "@graph":graph})


@register.simple_tag
def service_schema_json(page, request, seo):
    url=_absolute(request, page.get_absolute_url())
    graph=[{"@type":"Service", "name":page.title, "description":page.short_description, "url":url, "provider":{"@id":(seo.site_url.rstrip("/") + "/#organization") if seo else url + "#provider"}, "areaServed":{"@type":"Country", "name":"Iran"}}, _breadcrumb(request, [("خانه", "/"), ("خدمات", "/#services"), (page.title, "")])]
    return _json({"@context":"https://schema.org", "@graph":graph})


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
