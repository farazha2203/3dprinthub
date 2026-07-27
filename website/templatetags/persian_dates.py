from django import template
from website.jalali import format_jalali
register = template.Library()
@register.filter
def jalali_date(value):
    return format_jalali(value, numeric=False, persian_digits=True)
@register.filter
def jalali_date_numeric(value):
    return format_jalali(value, numeric=True, persian_digits=True)
