from __future__ import annotations

import re
from urllib.parse import quote, urlencode, urlsplit

from django import template
from django.urls import reverse

from website.models import SiteSetting

register = template.Library()


def _absolute_url(request, value: str) -> str:
    value = str(value or "").strip()
    if value.startswith(("http://", "https://")):
        return value
    if request is not None:
        return request.build_absolute_uri(value or "/")
    return value


def _telegram_username(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    if value.startswith("@"):
        return value[1:]
    parsed = urlsplit(value if "://" in value else f"https://{value}")
    if parsed.hostname in {"t.me", "telegram.me", "www.t.me", "www.telegram.me"}:
        return parsed.path.strip("/").split("/", 1)[0]
    return ""


@register.simple_tag(takes_context=True)
def consultation_links(context, title: str, product_url: str):
    request = context.get("request")
    absolute_url = _absolute_url(request, product_url)
    title = str(title or "این محصول").strip()
    message = f"سلام، درباره «{title}» برای چاپ سه‌بعدی و قیمت مشاوره می‌خواهم.\n{absolute_url}"
    encoded = quote(message, safe="")

    cache_key = "phase28_site_settings"
    settings = context.render_context.get(cache_key)
    if settings is None:
        settings = SiteSetting.objects.first()
        context.render_context[cache_key] = settings or False
    if settings is False:
        settings = None
    whatsapp_raw = getattr(settings, "whatsapp", "") if settings else ""
    whatsapp_digits = re.sub(r"\D", "", whatsapp_raw or "")
    if whatsapp_digits.startswith("0"):
        whatsapp_digits = "98" + whatsapp_digits[1:]
    whatsapp_url = f"https://wa.me/{whatsapp_digits}?text={encoded}" if whatsapp_digits else ""

    telegram_raw = getattr(settings, "telegram", "") if settings else ""
    telegram_username = _telegram_username(telegram_raw)
    telegram_share_url = f"https://t.me/share/url?url={quote(absolute_url, safe='')}&text={quote('مشاوره درباره ' + title, safe='')}"
    telegram_support_url = f"https://t.me/{telegram_username}" if telegram_username else (telegram_raw or "")

    support_url = ""
    if request is not None:
        support_path = reverse("website:customer_support")
        support_query = urlencode({"product_title": title, "product_url": absolute_url})
        support_target = f"{support_path}?{support_query}"
        if getattr(request, "user", None) and request.user.is_authenticated:
            support_url = support_target
        else:
            support_url = f"{reverse('website:customer_login')}?{urlencode({'next': support_target})}"

    return {
        "message": message,
        "whatsapp": whatsapp_url,
        "telegram": telegram_share_url,
        "telegram_support": telegram_support_url,
        "support": support_url,
        "has_any": bool(whatsapp_url or telegram_raw or support_url),
    }
