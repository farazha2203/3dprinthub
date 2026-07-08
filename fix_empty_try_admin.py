from pathlib import Path
from datetime import datetime

path = Path("website/admin.py")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup_path = path.with_name(path.name + f".bak_fix_empty_try_{timestamp}")
backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
print(f"Backup created: {backup_path}")

text = path.read_text(encoding="utf-8")
lines = text.splitlines(True)

out = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # حذف try خالی مثل:
    # try:
    # except Exception:
    #     pass
    if stripped == "try:":
        j = i + 1

        # رد کردن خط‌های خالی بعد از try
        while j < len(lines) and lines[j].strip() == "":
            j += 1

        if j < len(lines) and lines[j].strip().startswith("except "):
            print(f"Removing empty try/except block starting at line {i + 1}")

            # رد کردن try تا except
            j += 1

            # رد کردن بدنه except مثل pass یا خط‌های خالی
            while j < len(lines):
                current = lines[j]

                if current.strip() == "":
                    j += 1
                    continue

                # اگر خط بعدی تو رفتگی داشت، یعنی بدنه except است
                if current.startswith((" ", "\t")):
                    j += 1
                    continue

                # رسیدیم به کد top-level بعدی
                break

            i = j
            continue

    out.append(line)
    i += 1

new_text = "".join(out)

# اگر هنوز چیزی از مدل‌های تکراری در admin.py مانده بود، حذف خطی انجام بده
bad_keywords = [
    "MaterialIndustryGuide",
    "MaterialPartGuide",
    "MaterialIndustryGuideAdmin",
    "MaterialPartGuideAdmin",
]

clean_lines = []
for line in new_text.splitlines(True):
    if any(k in line for k in bad_keywords):
        print(f"Removing leftover line: {line.strip()}")
        continue
    clean_lines.append(line)

new_text = "".join(clean_lines)

path.write_text(new_text, encoding="utf-8")
print("admin.py fixed.")
