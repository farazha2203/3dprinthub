from __future__ import annotations

from django.db import migrations, models


COLOR_TYPE_CHOICES = [
    ("solid", "تک‌رنگ"),
    ("dual", "دو‌رنگ"),
    ("multicolor", "چندرنگ"),
    ("gradient", "گرادیانی"),
    ("color_shift", "تغییررنگ / Color Shift"),
]

FINISH_CHOICES = [
    ("matte", "مات"),
    ("glossy", "براق"),
    ("metallic", "متالیک"),
    ("transparent_matte", "شیشه‌ای مات"),
    ("transparent_glossy", "شیشه‌ای براق"),
    ("silk", "Silk / ابریشمی"),
]


def _normalize_hex(value):
    text = str(value or "").strip().upper()
    if not text:
        return ""
    if not text.startswith("#"):
        text = "#" + text
    return text[:20]


def forward(apps, schema_editor):
    Option = apps.get_model("store", "MaterialColorOption")
    legacy_map = {
        "transparent": ("solid", "transparent_glossy"),
        "translucent": ("solid", "transparent_matte"),
        "metallic": ("solid", "metallic"),
        "silk": ("solid", "silk"),
        "triple": ("multicolor", "glossy"),
    }
    for option in Option.objects.all().iterator():
        old_type = str(option.color_type or "solid").strip().lower()
        behavior, finish = legacy_map.get(old_type, (old_type, "matte"))
        if behavior not in {code for code, _label in COLOR_TYPE_CHOICES}:
            behavior = "solid"

        palette = []
        seen = set()
        for raw in (option.hex_code, option.secondary_hex, option.tertiary_hex):
            value = _normalize_hex(raw)
            if not value or value.casefold() in seen:
                continue
            seen.add(value.casefold())
            palette.append(value)

        option.color_type = behavior
        option.color_finish = finish
        option.palette_hexes = palette[:7]
        # Brand is the owner-facing identity. Keep manufacturer as a hidden
        # compatibility alias for older order/sync snapshots.
        if option.brand_name:
            option.manufacturer_name = option.brand_name
        elif option.manufacturer_name:
            option.brand_name = option.manufacturer_name
        option.save(
            update_fields=[
                "color_type",
                "color_finish",
                "palette_hexes",
                "brand_name",
                "manufacturer_name",
            ]
        )


def backward(apps, schema_editor):
    Option = apps.get_model("store", "MaterialColorOption")
    for option in Option.objects.all().iterator():
        finish = str(option.color_finish or "").strip().lower()
        behavior = str(option.color_type or "solid").strip().lower()
        if behavior == "color_shift":
            option.color_type = "gradient"
        elif finish == "metallic":
            option.color_type = "metallic"
        elif finish == "silk":
            option.color_type = "silk"
        elif finish == "transparent_matte":
            option.color_type = "translucent"
        elif finish == "transparent_glossy":
            option.color_type = "transparent"
        else:
            option.color_type = behavior if behavior in {"solid", "dual", "multicolor", "gradient"} else "solid"
        option.save(update_fields=["color_type"])


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0040_phase50_filament_offer_operations"),
    ]

    operations = [
        migrations.AddField(
            model_name="materialcoloroption",
            name="color_finish",
            field=models.CharField(
                choices=FINISH_CHOICES,
                default="matte",
                max_length=32,
                verbose_name="نوع سطح / Finish",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="palette_hexes",
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name="پالت رنگ فیلامنت",
            ),
        ),
        migrations.AddField(
            model_name="materialcoloroption",
            name="filament_image",
            field=models.ImageField(
                blank=True,
                upload_to="store/filaments/%Y/%m/",
                verbose_name="تصویر فیلامنت",
            ),
        ),
        migrations.AlterField(
            model_name="materialcoloroption",
            name="color_type",
            field=models.CharField(
                choices=COLOR_TYPE_CHOICES,
                db_index=True,
                default="solid",
                max_length=20,
                verbose_name="رفتار رنگ",
            ),
        ),
        migrations.RunPython(forward, backward),
    ]
