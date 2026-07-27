from __future__ import annotations
from datetime import date
import re

PERSIAN_MONTHS = ("", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند")
_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_digits(value: str | None) -> str:
    return (value or "").translate(_DIGITS).strip()

def jalali_to_gregorian(jy: int, jm: int, jd: int) -> date:
    jy, jm, jd = int(jy), int(jm), int(jd)
    if not (1 <= jm <= 12 and 1 <= jd <= 31):
        raise ValueError("تاریخ شمسی معتبر نیست.")
    if jy > 979:
        gy, jy = 1600, jy - 979
    else:
        gy = 621
    days = 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4 + 78 + jd
    days += (jm - 1) * 31 if jm < 7 else (jm - 7) * 30 + 186
    gy += 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0
    month_days = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    while gm <= 12 and gd > month_days[gm]:
        gd -= month_days[gm]
        gm += 1
    return date(gy, gm, gd)

def gregorian_to_jalali(value: date) -> tuple[int, int, int]:
    gy, gm, gd = value.year, value.month, value.day
    cumulative = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + cumulative[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm, jd = 1 + days // 31, 1 + days % 31
    else:
        jm, jd = 7 + (days - 186) // 30, 1 + (days - 186) % 30
    return jy, jm, jd

def parse_jalali_date(value: str | None) -> date | None:
    raw = normalize_digits(value)
    if not raw:
        return None
    match = re.fullmatch(r"\s*(\d{3,4})[\-/\.](\d{1,2})[\-/\.](\d{1,2})\s*", raw)
    if not match:
        raise ValueError("تاریخ را مانند 1358/09/28 وارد کنید.")
    jy, jm, jd = map(int, match.groups())
    result = jalali_to_gregorian(jy, jm, jd)
    back = gregorian_to_jalali(result)
    if back != (jy, jm, jd):
        raise ValueError("تاریخ شمسی واردشده معتبر نیست.")
    return result

def format_jalali(value: date | None, *, numeric: bool = False, persian_digits: bool = False) -> str:
    if not value:
        return ""
    jy, jm, jd = gregorian_to_jalali(value)
    text = f"{jy:04d}/{jm:02d}/{jd:02d}" if numeric else f"{jd} {PERSIAN_MONTHS[jm]} {jy}"
    if persian_digits:
        text = text.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
    return text
