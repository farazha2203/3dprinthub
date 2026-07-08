from pathlib import Path
from datetime import datetime
import re


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

files = [
    Path("website/models.py"),
    Path("website/admin.py"),
    Path("website/views.py"),
]

NEW_MODEL_NAMES = [
    "MaterialIndustryGuide",
    "MaterialPartGuide",
]

NEW_ADMIN_CLASSES = [
    "MaterialIndustryGuideAdmin",
    "MaterialPartGuideAdmin",
]


def backup(path):
    if path.exists():
        backup_path = path.with_name(path.name + f".bak_rollback_guides_{timestamp}")
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup created: {backup_path}")


def remove_top_level_class(text, class_name):
    lines = text.splitlines(True)
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith(f"class {class_name}("):
            print(f"Removing class: {class_name}")
            i += 1

            while i < len(lines):
                current = lines[i]

                if current.strip() == "":
                    i += 1
                    continue

                if not current.startswith((" ", "\t")):
                    break

                i += 1

            continue

        output.append(line)
        i += 1

    return "".join(output)


def is_register_decorator_for_new_model(line):
    stripped = line.strip()
    return any(stripped.startswith(f"@admin.register({name})") for name in NEW_MODEL_NAMES)


def is_new_admin_class(line):
    stripped = line.strip()
    return any(stripped.startswith(f"class {name}(") for name in NEW_ADMIN_CLASSES)


def remove_admin_blocks(text):
    lines = text.splitlines(True)
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # حذف @admin.register(MaterialIndustryGuide) و کلاس بعدش
        if is_register_decorator_for_new_model(line):
            print(f"Removing admin decorator block: {stripped}")
            i += 1

            if i < len(lines) and is_new_admin_class(lines[i]):
                print(f"Removing admin class: {lines[i].strip()}")
                i += 1

                while i < len(lines):
                    current = lines[i]

                    if current.strip() == "":
                        i += 1
                        continue

                    if not current.startswith((" ", "\t")):
                        break

                    i += 1

            continue

        # حذف کلاس ادمین بدون decorator اگر وجود داشت
        if is_new_admin_class(line):
            print(f"Removing standalone admin class: {stripped}")
            i += 1

            while i < len(lines):
                current = lines[i]

                if current.strip() == "":
                    i += 1
                    continue

                if not current.startswith((" ", "\t")):
                    break

                i += 1

            continue

        # حذف register/unregister دستی
        if any(f"admin.site.register({name}" in stripped for name in NEW_MODEL_NAMES):
            print(f"Removing manual register line: {stripped}")
            i += 1
            continue

        if any(f"admin.site.unregister({name}" in stripped for name in NEW_MODEL_NAMES):
            print(f"Removing manual unregister line: {stripped}")
            i += 1
            continue

        output.append(line)
        i += 1

    return "".join(output)


def remove_import_names(text):
    # حذف import خطی که دقیقاً قبلاً اضافه شده بود
    text = text.replace("from .models import MaterialIndustryGuide, MaterialPartGuide\n", "")
    text = text.replace("from .models import MaterialPartGuide, MaterialIndustryGuide\n", "")

    # اگر داخل import چندتایی آمده باشند، اسم‌ها را حذف می‌کنیم
    for name in NEW_MODEL_NAMES:
        text = re.sub(rf",\s*{name}\b", "", text)
        text = re.sub(rf"\b{name}\s*,\s*", "", text)
        text = re.sub(rf"\b{name}\b", "", text)

    # تمیزکاری importهای خالی احتمالی
    text = re.sub(r"from \.models import\s*\n", "", text)
    text = re.sub(r"from \.models import\s*\(\s*\)\s*\n", "", text, flags=re.MULTILINE)

    return text


def clean_models_py(path):
    text = path.read_text(encoding="utf-8")

    for class_name in NEW_MODEL_NAMES:
        text = remove_top_level_class(text, class_name)

    path.write_text(text, encoding="utf-8")


def clean_admin_py(path):
    text = path.read_text(encoding="utf-8")
    text = remove_admin_blocks(text)
    text = remove_import_names(text)

    # حذف کامنت‌های اضافه‌ای که برای بلاک جدید گذاشته شده بود
    text = text.replace("# Material Guide Admin - Clean Registration\n", "")
    text = text.replace("# Material Guide Admin\n", "")

    path.write_text(text, encoding="utf-8")


def clean_views_py(path):
    text = path.read_text(encoding="utf-8")
    text = remove_import_names(text)
    path.write_text(text, encoding="utf-8")


def run():
    for path in files:
        if path.exists():
            backup(path)

    models_path = Path("website/models.py")
    admin_path = Path("website/admin.py")
    views_path = Path("website/views.py")

    if models_path.exists():
        clean_models_py(models_path)

    if admin_path.exists():
        clean_admin_py(admin_path)

    if views_path.exists():
        clean_views_py(views_path)

    print("-" * 70)
    print("Duplicate guide models/admin imports removed.")
    print("Now run:")
    print("python manage.py check")
    print("python manage.py makemigrations website")
    print("python manage.py migrate")


run()
