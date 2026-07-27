from __future__ import annotations

from dataclasses import dataclass

from .catalog_site_adapters.common import normalize_persian


DEFAULT_SEGMENT_KEYWORDS = {
    "automotive": [
        "automotive", "car", "vehicle", "motorcycle", "engine", "dashboard", "bumper",
        "خودرو", "ماشین", "موتورسیکلت", "داشبورد", "موتور", "چراغ", "قطعه خودرو",
    ],
    "industrial": [
        "gear", "bearing", "pulley", "sprocket", "mechanical", "engineering", "robot",
        "cnc", "fixture", "jig", "machine", "valve", "pump", "coupling", "shaft",
        "چرخ دنده", "بلبرینگ", "پولی", "صنعتی", "مهندسی", "ربات", "ماشین کاری",
    ],
    "functional": [
        "bracket", "mount", "holder", "adapter", "replacement", "tool", "organizer",
        "enclosure", "case", "clip", "hinge", "fastener", "hook", "stand", "repair",
        "براکت", "نگهدارنده", "تبدیل", "ابزار", "کاربردی", "تعمیر", "قاب", "گیره",
    ],
    "decorative": [
        "decor", "vase", "sculpture", "statue", "figurine", "ornament", "art", "lamp",
        "planter", "wall art", "دکور", "تزئینی", "گلدان", "مجسمه", "فیگور", "چراغ",
    ],
    "toy": [
        "toy", "game", "puzzle", "fidget", "board game", "miniature", "dice",
        "اسباب بازی", "بازی", "پازل", "سرگرمی", "مینیاتور", "تاس",
    ],
    "cosplay": [
        "cosplay", "helmet", "mask", "costume", "prop", "armor", "sword", "weapon replica",
        "کازپلی", "ماسک", "کلاه", "لباس", "زره", "شمشیر", "ماکت",
    ],
    "education": [
        "education", "school", "science", "math", "physics", "biology", "anatomy",
        "teaching", "university", "architectural model", "آموزشی", "دانشگاهی", "فیزیک",
        "ریاضی", "زیست", "آناتومی", "مدرسه", "معماری",
    ],
}


@dataclass(slots=True)
class ClassificationResult:
    segment: str
    category: object | None
    matched_rule_id: int | None = None
    reason: str = ""


def _tokens(value: str) -> list[str]:
    return [normalize_persian(part) for part in value.replace("؛", ",").replace("|", ",").split(",") if normalize_persian(part)]


def classify_external_asset(*, source_kind: str, title: str, description: str, tags: list[str] | str, source_category: str):
    from .models import CatalogCategoryRule

    if isinstance(tags, list):
        tag_text = " ".join(tags)
    else:
        tag_text = tags or ""
    searchable = normalize_persian(" ".join([title or "", description or "", tag_text, source_category or ""]))
    source_category_text = normalize_persian(source_category or "")

    rules = CatalogCategoryRule.objects.filter(is_active=True).select_related("target_category").order_by("priority", "id")
    for rule in rules:
        if rule.source_kind and rule.source_kind != source_kind:
            continue
        title_keywords = _tokens(rule.title_keywords)
        category_keywords = _tokens(rule.source_category_keywords)
        title_match = not title_keywords or any(keyword in searchable for keyword in title_keywords)
        category_match = not category_keywords or any(keyword in source_category_text for keyword in category_keywords)
        if title_match and category_match:
            return ClassificationResult(
                segment=rule.segment,
                category=rule.target_category,
                matched_rule_id=rule.pk,
                reason="قانون دسته‌بندی مدیریت",
            )

    for segment, keywords in DEFAULT_SEGMENT_KEYWORDS.items():
        if any(normalize_persian(keyword) in searchable for keyword in keywords):
            fallback = CatalogCategoryRule.objects.filter(is_active=True, segment=segment).select_related("target_category").order_by("priority").first()
            return ClassificationResult(
                segment=segment,
                category=fallback.target_category if fallback else None,
                reason="واژه‌نامه داخلی",
            )

    fallback = CatalogCategoryRule.objects.filter(is_active=True, segment="other").select_related("target_category").order_by("priority").first()
    return ClassificationResult(segment="other", category=fallback.target_category if fallback else None, reason="دسته پیش‌فرض")
