from pathlib import Path
from datetime import datetime

admin_path = Path("website/admin.py")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

GUIDE_MODELS = [
    "MaterialIndustryGuide",
    "MaterialPartGuide",
]

GUIDE_ADMIN_CLASSES = [
    "MaterialIndustryGuideAdmin",
    "MaterialPartGuideAdmin",
]

CLEAN_ADMIN_BLOCK = r'''

# =========================
# Material Guide Admin - Clean Registration
# =========================

try:
    admin.site.unregister(MaterialIndustryGuide)
except Exception:
    pass

try:
    admin.site.unregister(MaterialPartGuide)
except Exception:
    pass


@admin.register(MaterialIndustryGuide)
class MaterialIndustryGuideAdmin(admin.ModelAdmin):
    list_display = ("industry", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("industry", "description")
    filter_horizontal = ("recommended_materials",)
    ordering = ("sort_order", "industry")


@admin.register(MaterialPartGuide)
class MaterialPartGuideAdmin(admin.ModelAdmin):
    list_display = ("part_name", "best_material", "is_active", "sort_order")
    list_filter = ("is_active", "best_material")
    search_fields = ("part_name", "reason", "best_material__name")
    filter_horizontal = ("alternative_materials",)
    ordering = ("sort_order", "part_name")
'''


def backup():
    backup_path = admin_path.with_name(admin_path.name + f".bak_{timestamp}")
    backup_path.write_text(admin_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Backup created: {backup_path}")


def is_guide_register_decorator(line):
    stripped = line.strip()
    return any(stripped.startswith(f"@admin.register({model})") for model in GUIDE_MODELS)


def is_guide_admin_class(line):
    stripped = line.strip()
    return any(stripped.startswith(f"class {cls}(") for cls in GUIDE_ADMIN_CLASSES)


def skip_class_block(lines, i):
    """
    i روی خط class است. کل کلاس و بدنه‌اش را رد می‌کند.
    """
    i += 1

    while i < len(lines):
        line = lines[i]

        # خط خالی داخل/بعد کلاس را رد می‌کنیم
        if line.strip() == "":
            i += 1
            continue

        # اگر به top-level بعدی رسیدیم، کلاس تمام شده
        if not line.startswith((" ", "\t")):
            break

        i += 1

    return i


def remove_duplicate_blocks(text):
    lines = text.splitlines(True)
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # حذف بلاک‌هایی که با @admin.register شروع می‌شوند
        if is_guide_register_decorator(line):
            print(f"Removing decorator block: {line.strip()}")

            # رد کردن decorator
            i += 1

            # اگر خط بعدی class مربوطه بود، کل کلاس را رد کن
            if i < len(lines) and is_guide_admin_class(lines[i]):
                print(f"Removing admin class: {lines[i].strip()}")
                i = skip_class_block(lines, i)

            continue

        # حذف کلاس‌های ادمین بدون decorator احتمالی
        if is_guide_admin_class(line):
            print(f"Removing standalone admin class: {line.strip()}")
            i = skip_class_block(lines, i)
            continue

        # حذف register دستی تک‌خطی
        stripped = line.strip()
        if "admin.site.register(MaterialIndustryGuide" in stripped:
            print("Removing manual register for MaterialIndustryGuide")
            i += 1
            continue

        if "admin.site.register(MaterialPartGuide" in stripped:
            print("Removing manual register for MaterialPartGuide")
            i += 1
            continue

        # حذف unregisterهای قبلی برای همین مدل‌ها، اگر قبلاً اضافه شده باشند
        if "admin.site.unregister(MaterialIndustryGuide" in stripped:
            print("Removing old unregister for MaterialIndustryGuide")
            i += 1
            continue

        if "admin.site.unregister(MaterialPartGuide" in stripped:
            print("Removing old unregister for MaterialPartGuide")
            i += 1
            continue

        output.append(line)
        i += 1

    return "".join(output)


def ensure_imports(text):
    if "from django.contrib import admin" not in text:
        text = "from django.contrib import admin\n" + text
        print("Added import: from django.contrib import admin")

    needed_import = "from .models import MaterialIndustryGuide, MaterialPartGuide\n"

    if needed_import not in text:
        lines = text.splitlines(True)
        insert_at = 0

        for idx, line in enumerate(lines):
            if line.startswith("from django.contrib import admin"):
                insert_at = idx + 1
                break

        lines.insert(insert_at, needed_import)
        text = "".join(lines)
        print("Added import: MaterialIndustryGuide, MaterialPartGuide")
    else:
        print("Guide imports already exist")

    return text


def run():
    backup()

    text = admin_path.read_text(encoding="utf-8")

    text = remove_duplicate_blocks(text)
    text = ensure_imports(text)

    text = text.rstrip() + CLEAN_ADMIN_BLOCK + "\n"

    admin_path.write_text(text, encoding="utf-8")

    print("-" * 70)
    print("admin.py cleaned successfully.")
    print("Now run:")
    print("python manage.py check")
    print("python manage.py makemigrations website")
    print("python manage.py migrate")


run()
