from django.apps import apps
from django.db import models
from django.db.models import NOT_PROVIDED


FAQ_ITEMS = [
    {
        "question": "برای ثبت سفارش پرینت سه‌بعدی چه اطلاعاتی لازم است؟",
        "answer": "برای ثبت سفارش، بهتر است فایل سه‌بعدی قطعه مانند STL، OBJ، 3MF یا STEP را ارسال کنید و متریال، رنگ، تعداد، توضیحات فنی و کاربرد قطعه را مشخص کنید. اگر فایل آماده ندارید، می‌توانید تصویر، نقشه، نمونه فیزیکی یا توضیحات قطعه را ارسال کنید تا تیم ما امکان طراحی یا مهندسی معکوس را بررسی کند.",
        "sort_order": 10,
    },
    {
        "question": "اگر فایل سه‌بعدی STL یا STEP نداشته باشم، می‌توانید طراحی انجام دهید؟",
        "answer": "بله. اگر فایل سه‌بعدی آماده ندارید، تیم 3DprintHub می‌تواند بر اساس عکس، نقشه دستی، نمونه فیزیکی، ابعاد یا توضیحات شما مدل سه‌بعدی قطعه را طراحی کند. در پروژه‌های صنعتی نیز امکان طراحی فنی و آماده‌سازی فایل برای چاپ سه‌بعدی وجود دارد.",
        "sort_order": 20,
    },
    {
        "question": "قیمت پرینت سه‌بعدی چگونه محاسبه می‌شود؟",
        "answer": "قیمت پرینت سه‌بعدی بر اساس چند عامل محاسبه می‌شود: نوع متریال، وزن مصرفی، زمان چاپ، پیچیدگی قطعه، کیفیت چاپ، تعداد قطعات، نیاز به ساپورت، پرداخت نهایی و دستمزد آماده‌سازی. به همین دلیل برای اعلام قیمت دقیق، فایل سه‌بعدی یا اطلاعات کامل قطعه بررسی می‌شود.",
        "sort_order": 30,
    },
    {
        "question": "چرا قیمت نهایی بعد از بررسی فایل اعلام می‌شود؟",
        "answer": "چون دو قطعه با ابعاد مشابه ممکن است زمان چاپ، میزان متریال مصرفی، مقدار ساپورت و سختی چاپ کاملاً متفاوتی داشته باشند. بررسی فایل سه‌بعدی باعث می‌شود قیمت واقعی‌تر، منصفانه‌تر و دقیق‌تر اعلام شود و از تغییرات غیرمنتظره در ادامه سفارش جلوگیری شود.",
        "sort_order": 40,
    },
    {
        "question": "چه متریالی برای قطعه من مناسب‌تر است؟",
        "answer": "انتخاب متریال به کاربرد قطعه بستگی دارد. برای نمونه‌سازی سریع معمولاً PLA مناسب است، برای قطعات مقاوم‌تر PETG یا ABS پیشنهاد می‌شود، برای قطعات انعطاف‌پذیر TPU کاربرد دارد و برای قطعات صنعتی، مکانیکی، مقاوم به حرارت یا مواد شیمیایی متریال‌هایی مانند PA-CF، PET-CF، PC-FR یا PPS-CF گزینه‌های حرفه‌ای‌تری هستند.",
        "sort_order": 50,
    },
    {
        "question": "آیا امکان مشاوره برای انتخاب متریال وجود دارد؟",
        "answer": "بله. اگر نمی‌دانید کدام متریال برای قطعه شما مناسب‌تر است، کافی است کاربرد قطعه، شرایط کاری، میزان فشار، دمای محیط، تماس با روغن یا مواد شیمیایی و حساسیت ابعادی را توضیح دهید. تیم ما بر اساس نیاز واقعی قطعه، متریال مناسب را پیشنهاد می‌دهد.",
        "sort_order": 60,
    },
    {
        "question": "تفاوت PLA، PETG، ABS، TPU و متریال‌های صنعتی چیست؟",
        "answer": "PLA برای نمونه‌سازی سریع و قطعات ظاهری اقتصادی مناسب است. PETG مقاومت بهتر و دوام بیشتری دارد. ABS و ASA برای قطعات مقاوم‌تر و کاربردهای فنی‌تر استفاده می‌شوند. TPU انعطاف‌پذیر و شبه‌لاستیکی است. متریال‌های صنعتی مانند PA-CF، PET-CF و PPS-CF برای قطعات مکانیکی، مقاوم به حرارت، تنش، سایش و محیط‌های صنعتی استفاده می‌شوند.",
        "sort_order": 70,
    },
    {
        "question": "آیا قطعات پرینت سه‌بعدی برای استفاده صنعتی قابل اعتماد هستند؟",
        "answer": "بله، اگر طراحی قطعه، جهت چاپ، درصد پرشدگی، نوع متریال و تنظیمات چاپ درست انتخاب شوند، قطعات پرینت سه‌بعدی می‌توانند در بسیاری از کاربردهای صنعتی مانند فیکسچر، جیگ، براکت، قاب تجهیزات، پایه سنسور، قطعات رباتیک و نمونه‌های کاربردی استفاده شوند.",
        "sort_order": 80,
    },
    {
        "question": "زمان آماده‌سازی سفارش چقدر است؟",
        "answer": "زمان آماده‌سازی به تعداد قطعات، ابعاد، متریال، کیفیت چاپ و حجم سفارش بستگی دارد. سفارش‌های ساده معمولاً سریع‌تر آماده می‌شوند، اما قطعات صنعتی، بزرگ، دقیق یا چندتکه ممکن است زمان بیشتری نیاز داشته باشند. زمان تقریبی پس از بررسی فایل و تأیید سفارش اعلام می‌شود.",
        "sort_order": 90,
    },
    {
        "question": "آیا امکان ساخت قطعه از روی نمونه فیزیکی وجود دارد؟",
        "answer": "بله. اگر نمونه فیزیکی قطعه را داشته باشید، امکان بررسی، اندازه‌برداری، مدل‌سازی سه‌بعدی و ساخت مجدد آن وجود دارد. این فرآیند برای قطعات یدکی کمیاب، قطعات دستگاه‌ها، قطعات شکسته یا نمونه‌هایی که فایل طراحی ندارند بسیار کاربردی است.",
        "sort_order": 100,
    },
    {
        "question": "مهندسی معکوس قطعه چگونه انجام می‌شود؟",
        "answer": "در مهندسی معکوس، ابتدا قطعه موجود بررسی و اندازه‌برداری می‌شود. سپس مدل سه‌بعدی آن طراحی می‌گردد و در صورت نیاز اصلاحات فنی برای بهبود عملکرد، افزایش استحکام یا آماده‌سازی برای چاپ سه‌بعدی انجام می‌شود. بعد از تأیید مدل، قطعه با متریال مناسب ساخته می‌شود.",
        "sort_order": 110,
    },
    {
        "question": "آیا می‌توان قطعات مکانیکی، صنعتی و کاربردی تولید کرد؟",
        "answer": "بله. خدمات پرینت سه‌بعدی فقط مخصوص قطعات تزئینی یا نمونه‌های ساده نیست. با انتخاب متریال مناسب و طراحی اصولی می‌توان قطعاتی مانند براکت، جیگ، فیکسچر، پایه سنسور، قاب تجهیزات، هولدر، چرخ‌دنده سبک، قطعات رباتیک و قطعات مورد استفاده در خطوط تولید را تولید کرد.",
        "sort_order": 120,
    },
    {
        "question": "دقت چاپ سه‌بعدی چقدر است؟",
        "answer": "دقت چاپ به تکنولوژی چاپ، متریال، ابعاد قطعه، طراحی مدل و تنظیمات چاپ بستگی دارد. در چاپ FDM معمولاً برای قطعات صنعتی و کاربردی دقت مناسبی قابل دستیابی است، اما برای قطعات بسیار دقیق، تلرانس‌های حساس یا سطوح کاملاً صیقلی باید قبل از سفارش شرایط قطعه بررسی شود.",
        "sort_order": 130,
    },
    {
        "question": "آیا سطح قطعه بعد از چاپ نیاز به پرداخت دارد؟",
        "answer": "در چاپ سه‌بعدی FDM خطوط لایه‌ها معمولاً روی سطح قطعه دیده می‌شوند. برای قطعات کاربردی این موضوع اغلب مشکلی ایجاد نمی‌کند، اما اگر ظاهر قطعه مهم باشد، می‌توان از روش‌هایی مانند سنباده‌کاری، پرداخت، رنگ‌آمیزی یا بهینه‌سازی جهت چاپ استفاده کرد.",
        "sort_order": 140,
    },
    {
        "question": "آیا رنگ قطعه قابل انتخاب است؟",
        "answer": "بله، در بیشتر متریال‌ها امکان انتخاب رنگ وجود دارد. البته موجودی رنگ به نوع متریال وابسته است. برخی متریال‌های صنعتی یا کامپوزیتی مانند فیبرکربن معمولاً رنگ‌های محدودتری دارند و بیشتر با ظاهر مشکی، خاکستری یا صنعتی ارائه می‌شوند.",
        "sort_order": 150,
    },
    {
        "question": "اگر قطعه چاپ‌شده مشکل داشته باشد چه می‌شود؟",
        "answer": "اگر مشکل قطعه ناشی از خطای چاپ یا عدم تطابق با مشخصات تأییدشده باشد، موضوع بررسی می‌شود و راهکار مناسب مانند اصلاح، چاپ مجدد یا رفع ایراد ارائه خواهد شد. هدف ما تحویل قطعه‌ای قابل استفاده و مطابق توافق فنی اولیه است.",
        "sort_order": 160,
    },
    {
        "question": "آیا امکان چاپ تعداد بالا یا تولید سری وجود دارد؟",
        "answer": "بله. برای تولید تعداد بالا، ابتدا بهتر است یک نمونه اولیه ساخته و بررسی شود. پس از تأیید نمونه، امکان تولید سری قطعات وجود دارد. در سفارش‌های تیراژ، زمان تولید، هزینه نهایی و روش بهینه چاپ بر اساس تعداد و کاربرد قطعه مشخص می‌شود.",
        "sort_order": 170,
    },
    {
        "question": "آیا فایل و اطلاعات قطعه محرمانه می‌ماند؟",
        "answer": "بله. فایل‌های سه‌بعدی، نقشه‌ها، تصاویر، نمونه‌ها و اطلاعات فنی مشتریان به عنوان اطلاعات محرمانه در نظر گرفته می‌شوند و فقط برای بررسی، قیمت‌دهی، طراحی یا ساخت سفارش استفاده خواهند شد.",
        "sort_order": 180,
    },
    {
        "question": "برای قطعات مقاوم به حرارت یا مواد شیمیایی چه متریالی پیشنهاد می‌شود؟",
        "answer": "برای قطعاتی که در معرض حرارت، روغن، سوخت، مواد شیمیایی یا شرایط صنعتی سخت هستند، متریال‌هایی مانند PA-CF، PC-FR، PET-CF یا PPS-CF می‌توانند گزینه‌های مناسبی باشند. انتخاب دقیق متریال باید بر اساس دمای کاری، نوع ماده شیمیایی، فشار مکانیکی و شرایط استفاده انجام شود.",
        "sort_order": 190,
    },
    {
        "question": "چطور می‌توانم سفارش خود را پیگیری کنم؟",
        "answer": "بعد از ثبت سفارش و ارسال اطلاعات قطعه، وضعیت سفارش از مرحله بررسی فایل، اعلام قیمت، تأیید مشتری، پرداخت، چاپ، کنترل نهایی و آماده‌سازی برای تحویل قابل پیگیری است. در صورت نیاز می‌توانید از طریق راه‌های ارتباطی سایت با پشتیبانی در تماس باشید.",
        "sort_order": 200,
    },
]


def find_faq_model():
    """
    تلاش می‌کند مدل FAQ موجود در پروژه را پیدا کند.
    دنبال مدل‌هایی می‌گردد که اسمشان شامل FAQ یا Question باشد.
    """
    candidates = []

    for model in apps.get_app_config("website").get_models():
        model_name = model.__name__.lower()
        verbose_name = str(model._meta.verbose_name).lower()
        verbose_plural = str(model._meta.verbose_name_plural).lower()

        if (
            "faq" in model_name
            or "question" in model_name
            or "سوال" in verbose_name
            or "سؤال" in verbose_name
            or "متداول" in verbose_name
            or "سوال" in verbose_plural
            or "سؤال" in verbose_plural
            or "متداول" in verbose_plural
        ):
            candidates.append(model)

    if not candidates:
        print("ERROR: FAQ model not found.")
        print("Available website models:")
        for model in apps.get_app_config("website").get_models():
            print(" -", model.__name__, "|", model._meta.verbose_name, "|", model._meta.verbose_name_plural)
        raise SystemExit(1)

    if len(candidates) > 1:
        print("Multiple FAQ-like models found. Using first one:")
        for model in candidates:
            print(" -", model.__name__, "|", model._meta.verbose_name, "|", model._meta.verbose_name_plural)

    return candidates[0]


def pick_field(model, candidates):
    field_names = [f.name for f in model._meta.fields]
    for candidate in candidates:
        if candidate in field_names:
            return candidate
    return None


def truncate(value, field):
    max_length = getattr(field, "max_length", None)
    if max_length and isinstance(value, str):
        return value[:max_length]
    return value


def build_defaults(model, question_field, answer_field, item):
    defaults = {}

    for field in model._meta.fields:
        if field.primary_key or field.name in [question_field]:
            continue

        name = field.name.lower()

        if answer_field and field.name == answer_field:
            defaults[field.name] = truncate(item["answer"], field)
            continue

        if isinstance(field, models.BooleanField):
            defaults[field.name] = True
            continue

        if isinstance(field, (models.IntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField, models.SmallIntegerField)):
            if "sort" in name or "order" in name or "priority" in name or "position" in name:
                defaults[field.name] = item["sort_order"]
            elif field.default is NOT_PROVIDED and not field.null:
                defaults[field.name] = 0
            continue

        if isinstance(field, models.TextField):
            if not answer_field:
                defaults[field.name] = item["answer"]
            elif "answer" in name or "response" in name or "content" in name or "description" in name:
                defaults[field.name] = item["answer"]
            continue

        if isinstance(field, models.CharField):
            if "answer" in name or "response" in name or "content" in name or "description" in name:
                defaults[field.name] = truncate(item["answer"], field)
            elif field.default is NOT_PROVIDED and not field.blank and not field.null:
                defaults[field.name] = truncate(item["question"], field)
            continue

        if isinstance(field, models.DecimalField):
            if field.default is NOT_PROVIDED and not field.null:
                defaults[field.name] = 0
            continue

    return defaults


def run():
    FAQModel = find_faq_model()

    print("FAQ model detected:")
    print(" -", FAQModel.__name__)
    print(" - verbose_name:", FAQModel._meta.verbose_name)
    print(" - verbose_name_plural:", FAQModel._meta.verbose_name_plural)
    print("\nFields:")
    for f in FAQModel._meta.fields:
        print(" -", f.name, f.__class__.__name__)

    question_field = pick_field(
        FAQModel,
        ["question", "title", "name", "subject", "faq_question"]
    )

    answer_field = pick_field(
        FAQModel,
        ["answer", "response", "content", "description", "text", "faq_answer"]
    )

    if not question_field:
        print("\nERROR: Question field not found.")
        print("Expected one of: question, title, name, subject, faq_question")
        raise SystemExit(1)

    if not answer_field:
        print("\nWARNING: Answer field not found by name. Will try to use first TextField.")

        for field in FAQModel._meta.fields:
            if isinstance(field, models.TextField):
                answer_field = field.name
                print("Using TextField as answer field:", answer_field)
                break

    if not answer_field:
        print("\nERROR: Answer field not found.")
        print("Expected one of: answer, response, content, description, text, faq_answer")
        raise SystemExit(1)

    print("\nUsing fields:")
    print(" question_field:", question_field)
    print(" answer_field:", answer_field)
    print("-" * 70)

    created_count = 0
    updated_count = 0

    for item in FAQ_ITEMS:
        question_model_field = FAQModel._meta.get_field(question_field)
        lookup_value = truncate(item["question"], question_model_field)

        defaults = build_defaults(
            model=FAQModel,
            question_field=question_field,
            answer_field=answer_field,
            item=item,
        )

        obj, created = FAQModel.objects.update_or_create(
            **{question_field: lookup_value},
            defaults=defaults,
        )

        if created:
            created_count += 1
            print("CREATED:", item["question"])
        else:
            updated_count += 1
            print("UPDATED:", item["question"])

    print("-" * 70)
    print("FAQ seeding completed.")
    print("Created:", created_count)
    print("Updated:", updated_count)
    print("Total FAQ:", FAQModel.objects.count())


run()
