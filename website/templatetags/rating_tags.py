from django import template

register = template.Library()


@register.filter
def stars(value):
    try:
        value = int(value)
    except Exception:
        return ""

    if value <= 0:
        return "❌"

    return "⭐" * value