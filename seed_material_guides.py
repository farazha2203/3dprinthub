from website.models import Material, MaterialIndustryGuide, MaterialPartGuide


INDUSTRY_GUIDES = [
    {
        "industry": "خودروسازی",
        "materials": ["PA6-CF20", "PA12-CF10", "PET-CF"],
        "description": "برای قطعات خودرو، براکت‌ها، قطعات مکانیکی، قطعات مقاوم به تنش و قطعات نیمه‌سنگین صنعتی مناسب است.",
        "sort_order": 10,
    },
    {
        "industry": "نفت و گاز",
        "materials": ["PPS-CF10"],
        "description": "برای محیط‌های سخت، تماس با روغن، سوخت، مواد شیمیایی، دما و شرایط صنعتی سنگین مناسب است.",
        "sort_order": 20,
    },
    {
        "industry": "پتروشیمی",
        "materials": ["PPS-CF10"],
        "description": "برای قطعات مقاوم به مواد شیمیایی، اسید، حرارت و شرایط کاری سنگین پیشنهاد می‌شود.",
        "sort_order": 30,
    },
    {
        "industry": "صنایع غذایی",
        "materials": ["PET-CF", "PETG-rCF08"],
        "description": "برای قطعات صنعتی عمومی، پایه‌ها، کاورها و تجهیزات جانبی خطوط تولید مناسب است.",
        "sort_order": 40,
    },
    {
        "industry": "اتوماسیون صنعتی",
        "materials": ["PET-CF", "PA12-CF10"],
        "description": "برای نگهدارنده سنسور، پایه دوربین صنعتی، فیکسچرها و قطعات دقیق صنعتی مناسب است.",
        "sort_order": 50,
    },
    {
        "industry": "رباتیک",
        "materials": ["PA12-CF10", "PA6-CF20"],
        "description": "برای بازوهای ربات، هولدرها، قطعات متحرک، قطعات دقیق و قطعات تحت بار مناسب است.",
        "sort_order": 60,
    },
    {
        "industry": "ماشین‌سازی",
        "materials": ["PET-CF", "PA6-CF20"],
        "description": "برای جیگ، فیکسچر، براکت، قطعات نیمه‌سنگین و قطعات مکانیکی کاربردی مناسب است.",
        "sort_order": 70,
    },
    {
        "industry": "برق صنعتی",
        "materials": ["PC-FR"],
        "description": "برای جعبه تابلو برق، محفظه‌های الکتریکی، قطعات مقاوم حرارتی و ضدحریق پیشنهاد می‌شود.",
        "sort_order": 80,
    },
    {
        "industry": "ابزارسازی",
        "materials": ["PA12-CF10"],
        "description": "برای ابزار دقیق، فیکسچرهای دقیق، قطعات با پایداری ابعادی و قطعات مهندسی مناسب است.",
        "sort_order": 90,
    },
    {
        "industry": "خطوط بسته‌بندی",
        "materials": ["PET-CF"],
        "description": "برای قطعات کاربردی، براکت‌ها، پایه‌ها و قطعات صنعتی عمومی خطوط بسته‌بندی مناسب است.",
        "sort_order": 100,
    },
    {
        "industry": "دستگاه CNC",
        "materials": ["PA6-CF20", "PET-CF"],
        "description": "برای فیکسچر، جیگ، قطعات نگهدارنده، پولی و قطعات مکانیکی تحت بار مناسب است.",
        "sort_order": 110,
    },
]


PART_GUIDES = [
    {
        "part_name": "براکت صنعتی",
        "best": "PET-CF",
        "alternatives": ["PA12-CF10", "PA6-CF20"],
        "reason": "PET-CF برای براکت‌های صنعتی تعادل بسیار خوبی بین استحکام، پایداری ابعادی، مقاومت حرارتی و چاپ‌پذیری دارد.",
        "sort_order": 10,
    },
    {
        "part_name": "جیگ مونتاژ",
        "best": "PET-CF",
        "alternatives": ["PA12-CF10", "HT-PLA-GF"],
        "reason": "برای جیگ مونتاژ، سختی، دقت و پایداری مهم است. PET-CF انتخاب عمومی و صنعتی مناسبی است.",
        "sort_order": 20,
    },
    {
        "part_name": "فیکسچر CNC",
        "best": "PA12-CF10",
        "alternatives": ["PET-CF", "PA6-CF20"],
        "reason": "PA12-CF10 برای فیکسچرهای دقیق، پایداری ابعادی و مقاومت شیمیایی عالی دارد.",
        "sort_order": 30,
    },
    {
        "part_name": "پایه سنسور",
        "best": "PET-CF",
        "alternatives": ["PETG-rCF08", "PA12-CF10"],
        "reason": "برای پایه سنسور، دقت، سختی و مقاومت صنعتی مهم است. PET-CF انتخاب بسیار مناسبی است.",
        "sort_order": 40,
    },
    {
        "part_name": "پایه دوربین صنعتی",
        "best": "PET-CF",
        "alternatives": ["PA12-CF10", "PETG-rCF08"],
        "reason": "PET-CF لرزش کمتر، سختی خوب و ظاهر صنعتی مناسبی برای پایه دوربین صنعتی دارد.",
        "sort_order": 50,
    },
    {
        "part_name": "قاب PLC",
        "best": "PETG-rCF08",
        "alternatives": ["PETG", "PC-FR"],
        "reason": "برای قاب PLC، PETG-rCF08 گزینه اقتصادی صنعتی با مقاومت مناسب است. اگر ضدحریق مهم باشد PC-FR بهتر است.",
        "sort_order": 60,
    },
    {
        "part_name": "جعبه تابلو برق",
        "best": "PC-FR",
        "alternatives": ["PETG-rCF08"],
        "reason": "PC-FR به دلیل مقاومت حرارتی و ویژگی ضدحریق، برای تجهیزات الکتریکی و تابلو برق مناسب‌تر است.",
        "sort_order": 70,
    },
    {
        "part_name": "هولدر کابل",
        "best": "PETG-rCF08",
        "alternatives": ["PETG", "PET-CF"],
        "reason": "هولدر کابل معمولاً به مقاومت متوسط، قیمت مناسب و دوام خوب نیاز دارد. PETG-rCF08 گزینه اقتصادی صنعتی است.",
        "sort_order": 80,
    },
    {
        "part_name": "دستگیره دستگاه",
        "best": "PET-CF",
        "alternatives": ["ABS", "ASA"],
        "reason": "PET-CF استحکام و ظاهر صنعتی خوبی دارد و برای دستگیره دستگاه مناسب است.",
        "sort_order": 90,
    },
    {
        "part_name": "چرخ‌دنده",
        "best": "PA6-CF20",
        "alternatives": ["PA12-CF10"],
        "reason": "PA6-CF20 برای قطعات مکانیکی سنگین، مقاومت سایشی و استحکام بالا انتخاب مناسبی است.",
        "sort_order": 100,
    },
    {
        "part_name": "پولی",
        "best": "PA6-CF20",
        "alternatives": ["PA12-CF10", "PET-CF"],
        "reason": "برای پولی، استحکام مکانیکی و مقاومت در برابر تنش مهم است. PA6-CF20 انتخاب قوی‌تری است.",
        "sort_order": 110,
    },
    {
        "part_name": "بازوی ربات",
        "best": "PA12-CF10",
        "alternatives": ["PA6-CF20"],
        "reason": "PA12-CF10 برای بازوی ربات، پایداری ابعادی، وزن مناسب و دقت خوبی ایجاد می‌کند.",
        "sort_order": 120,
    },
    {
        "part_name": "هولدر سرووموتور",
        "best": "PA12-CF10",
        "alternatives": ["PA6-CF20", "PET-CF"],
        "reason": "برای هولدر سرووموتور، دقت، استحکام و پایداری ابعادی مهم است.",
        "sort_order": 130,
    },
    {
        "part_name": "قطعات نزدیک موتور",
        "best": "PPS-CF10",
        "alternatives": ["PC-FR", "PA6-CF20"],
        "reason": "در نزدیکی موتور دما و شرایط کاری سخت است؛ PPS-CF10 مقاومت حرارتی بسیار بالایی دارد.",
        "sort_order": 140,
    },
    {
        "part_name": "قطعات داخل روغن",
        "best": "PPS-CF10",
        "alternatives": ["PA12-CF10"],
        "reason": "PPS-CF10 برای تماس با روغن و محیط‌های شیمیایی سخت گزینه بسیار قوی است.",
        "sort_order": 150,
    },
    {
        "part_name": "قطعات داخل بنزین",
        "best": "PPS-CF10",
        "alternatives": [],
        "reason": "برای تماس با بنزین و سوخت، مقاومت شیمیایی بسیار مهم است و PPS-CF10 پیشنهاد می‌شود.",
        "sort_order": 160,
    },
    {
        "part_name": "قطعات مقاوم به اسید",
        "best": "PPS-CF10",
        "alternatives": [],
        "reason": "PPS-CF10 به دلیل مقاومت شیمیایی بسیار بالا برای محیط‌های اسیدی و خورنده مناسب است.",
        "sort_order": 170,
    },
    {
        "part_name": "واشر",
        "best": "TPU95",
        "alternatives": [],
        "reason": "واشر به انعطاف، خاصیت لاستیکی و جذب فشار نیاز دارد. TPU95 انتخاب مناسب است.",
        "sort_order": 180,
    },
    {
        "part_name": "گسکت",
        "best": "TPU95",
        "alternatives": [],
        "reason": "TPU95 برای قطعات نرم، آب‌بندی نسبی و قطعات انعطاف‌پذیر مناسب است.",
        "sort_order": 190,
    },
    {
        "part_name": "لرزه‌گیر",
        "best": "TPU95",
        "alternatives": [],
        "reason": "برای جذب لرزش و ضربه، انعطاف‌پذیری بالا مهم است. TPU95 گزینه مناسب است.",
        "sort_order": 200,
    },
    {
        "part_name": "ضربه‌گیر",
        "best": "TPU95",
        "alternatives": [],
        "reason": "TPU95 خاصیت نرم و الاستیک دارد و برای ضربه‌گیر مناسب است.",
        "sort_order": 210,
    },
    {
        "part_name": "چرخ ربات",
        "best": "TPU95",
        "alternatives": [],
        "reason": "چرخ ربات به اصطکاک، انعطاف و جذب ضربه نیاز دارد. TPU95 انتخاب مناسبی است.",
        "sort_order": 220,
    },
    {
        "part_name": "قاب تجهیزات",
        "best": "PLA-CF",
        "alternatives": ["PETG-rCF08", "PET-CF"],
        "reason": "برای قاب تجهیزات با ظاهر صنعتی و سختی مناسب، PLA-CF انتخاب خوبی است.",
        "sort_order": 230,
    },
    {
        "part_name": "پنل دستگاه",
        "best": "PLA-CF",
        "alternatives": ["PETG-rCF08", "PET-CF"],
        "reason": "PLA-CF ظاهر مات و مهندسی دارد و برای پنل دستگاه گزینه مناسبی است.",
        "sort_order": 240,
    },
    {
        "part_name": "نمونه اولیه",
        "best": "PLA",
        "alternatives": ["PETG"],
        "reason": "PLA سریع، اقتصادی و بسیار چاپ‌پذیر است و برای نمونه اولیه بهترین انتخاب عمومی است.",
        "sort_order": 250,
    },
]


def get_material(name):
    material = Material.objects.filter(name=name).first()
    if not material:
        print(f"WARNING: Material not found: {name}")
    return material


def run():
    print("Seeding professional material guides...")
    print("-" * 70)

    industry_created = 0
    industry_updated = 0

    for item in INDUSTRY_GUIDES:
        guide, created = MaterialIndustryGuide.objects.update_or_create(
            industry=item["industry"],
            defaults={
                "description": item["description"],
                "is_active": True,
                "sort_order": item["sort_order"],
            },
        )

        guide.recommended_materials.clear()

        for material_name in item["materials"]:
            material = get_material(material_name)
            if material:
                guide.recommended_materials.add(material)

        if created:
            industry_created += 1
            print(f"CREATED industry guide: {guide.industry}")
        else:
            industry_updated += 1
            print(f"UPDATED industry guide: {guide.industry}")

    part_created = 0
    part_updated = 0

    for item in PART_GUIDES:
        best_material = get_material(item["best"])

        guide, created = MaterialPartGuide.objects.update_or_create(
            part_name=item["part_name"],
            defaults={
                "best_material": best_material,
                "reason": item["reason"],
                "is_active": True,
                "sort_order": item["sort_order"],
            },
        )

        guide.alternative_materials.clear()

        for material_name in item["alternatives"]:
            material = get_material(material_name)
            if material:
                guide.alternative_materials.add(material)

        if created:
            part_created += 1
            print(f"CREATED part guide: {guide.part_name}")
        else:
            part_updated += 1
            print(f"UPDATED part guide: {guide.part_name}")

    print("-" * 70)
    print(f"Industry guides created: {industry_created}, updated: {industry_updated}")
    print(f"Part guides created: {part_created}, updated: {part_updated}")
    print("Done.")


run()
