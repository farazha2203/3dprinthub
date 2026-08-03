from __future__ import annotations

import re

GLOSSARY = {
    "mask": "ماسک", "helmet": "کلاه‌خود", "holder": "نگهدارنده", "stand": "پایه",
    "gear": "چرخ‌دنده", "car": "خودرو", "wall": "دیواری", "phone": "موبایل",
    "controller": "دسته بازی", "mount": "پایه نصب", "box": "جعبه", "vase": "گلدان",
    "lamp": "چراغ", "toy": "اسباب‌بازی", "organizer": "نظم‌دهنده", "keychain": "جاکلیدی",
}


def draft_persian_title(title: str) -> str:
    text = title or ""
    for english, persian in sorted(GLOSSARY.items(), key=lambda item: -len(item[0])):
        text = re.sub(rf"\b{re.escape(english)}\b", persian, text, flags=re.I)
    return " ".join(text.split())[:260]


def draft_persian_description(title: str, description: str, source_name: str) -> str:
    fa_title = draft_persian_title(title)
    source_text = " ".join((description or "").split())
    if source_text:
        return f"{fa_title}\n\nتوضیحات منبع برای بازبینی اپراتور:\n{source_text}\n\nمنبع: {source_name}"
    return f"{fa_title}\n\nاین متن به‌صورت پیش‌نویس ایجاد شده و باید پیش از انتشار توسط اپراتور تکمیل شود.\nمنبع: {source_name}"


def expand_persian_query(query: str) -> list[str]:
    normalized = " ".join((query or "").strip().split())
    if not normalized:
        return []
    reverse = {value: key for key, value in GLOSSARY.items()}
    english = normalized
    for persian, token in sorted(reverse.items(), key=lambda item: -len(item[0])):
        english = english.replace(persian, token)
    output = [normalized]
    if english != normalized:
        output.append(english)
    synonyms = {
        "gear": ["cog", "replacement gear", "mechanical gear"],
        "holder": ["stand", "mount", "dock"],
        "car": ["automotive", "vehicle"],
        "mask": ["helmet", "cosplay mask"],
    }
    lowered = english.lower()
    for token, rows in synonyms.items():
        if token in lowered:
            output.extend(rows)
    seen=[]
    for item in output:
        item=" ".join(item.split())
        if item and item not in seen:
            seen.append(item)
    return seen[:12]
