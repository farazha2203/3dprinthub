from django.core.management.base import BaseCommand
from website.models import (
    SiteSetting,
    Material,
    IndustryRecommendation,
    PartRecommendation,
    FAQ,
)


class Command(BaseCommand):
    help = "Seed initial data for 3DprintHub.ir"

    def handle(self, *args, **options):
        SiteSetting.objects.get_or_create(
            id=1,
            defaults={
                "brand_name": "3DprintHub.ir",
                "hero_title": "طراحی، چاپ سه‌بعدی و مهندسی معکوس قطعات صنعتی",
                "hero_subtitle": "از نمونه‌سازی اولیه تا ساخت قطعات کاربردی صنعتی با متریال‌های مهندسی مانند PET-CF، PA12-CF، PA6-CF، PPS-CF، PC-FR و TPU.",
                "phone": "",
                "whatsapp": "",
                "email": "",
                "address": "",
                "working_hours": "شنبه تا پنجشنبه، ۹ تا ۱۸",
            },
        )

        materials = [
            (
                "PLA",
                900000,
                3,
                1,
                0,
                1,
                5,
                "نمونه اولیه",
                "ماکت، قاب، نمونه طراحی، قطعات نمایشگاهی",
            ),
            (
                "PLA-CF",
                1700000,
                4,
                2,
                0,
                2,
                4,
                "قطعات ظاهری مهندسی",
                "قاب دستگاه، هولدر ابزار، پنل کنترل، بدنه تجهیزات",
            ),
            (
                "HT-PLA-GF",
                2200000,
                4,
                3,
                0,
                2,
                4,
                "قطعات سبک با دقت بالا",
                "جیگ، فیکسچر، ابزار مونتاژ",
            ),
            (
                "PETG",
                1200000,
                3,
                3,
                1,
                4,
                5,
                "قطعات عمومی صنعتی",
                "قاب برق، جعبه، براکت، کاور",
            ),
            (
                "PET-CF",
                4000000,
                5,
                4,
                0,
                4,
                4,
                "بهترین انتخاب عمومی صنعتی",
                "براکت، پایه موتور، نگهدارنده سنسور، جیگ، فیکسچر، قطعات CNC",
            ),
            (
                "PETG-rCF08",
                2600000,
                4,
                3,
                0,
                4,
                4,
                "قطعات اقتصادی صنعتی",
                "کاور دستگاه، پنل، پایه تجهیزات، قطعات نیمه‌سنگین",
            ),
            (
                "ABS",
                1300000,
                3,
                3,
                1,
                3,
                3,
                "قطعات عمومی",
                "قاب ابزار، دسته، قطعات خودرو، محفظه‌ها",
            ),
            (
                "ASA",
                1500000,
                3,
                3,
                1,
                4,
                3,
                "فضای باز",
                "قطعات بیرونی، دوربین، تجهیزات خورشیدی",
            ),
            (
                "PC-FR",
                4500000,
                5,
                5,
                0,
                4,
                2,
                "تجهیزات الکتریکی",
                "تابلو برق، جعبه برق، قطعات ضدحریق",
            ),
            (
                "TPU95",
                1800000,
                2,
                2,
                5,
                4,
                3,
                "قطعات نرم",
                "لرزه‌گیر، چرخ، واشر، اورینگ، ضربه‌گیر، دسته ابزار",
            ),
            (
                "PA6-CF20",
                5500000,
                5,
                4,
                1,
                4,
                2,
                "قطعات مکانیکی سنگین",
                "چرخ‌دنده، بازوی ربات، براکت سنگین، قطعات خودرو، هولدر بلبرینگ",
            ),
            (
                "PA12-CF10",
                6500000,
                5,
                4,
                1,
                5,
                3,
                "قطعات دقیق مهندسی",
                "ابزار دقیق، تجهیزات پزشکی، قطعات رباتیک، فیکسچرهای دقیق",
            ),
            (
                "PPS-CF10",
                12000000,
                5,
                5,
                0,
                5,
                1,
                "صنایع سنگین",
                "قطعات پتروشیمی، پمپ، شیرآلات، قطعات موتور، تجهیزات نفت و گاز",
            ),
        ]

        for index, item in enumerate(materials, start=1):
            Material.objects.update_or_create(
                name=item[0],
                defaults={
                    "price_per_kg": item[1],
                    "strength": item[2],
                    "heat_resistance": item[3],
                    "flexibility": item[4],
                    "chemical_resistance": item[5],
                    "printability": item[6],
                    "main_usage": item[7],
                    "sample_parts": item[8],
                    "sort_order": index,
                    "is_active": True,
            },
        )

        industries = [
            ("خودروسازی", "PA6-CF، PA12-CF، PET-CF"),
            ("نفت و گاز", "PPS-CF"),
            ("پتروشیمی", "PPS-CF"),
            ("صنایع غذایی", "PET-CF، PETG-rCF"),
            ("اتوماسیون صنعتی", "PET-CF، PA12-CF"),
            ("رباتیک", "PA12-CF، PA6-CF"),
            ("ماشین‌سازی", "PET-CF، PA6-CF"),
            ("برق صنعتی", "PC-FR"),
            ("ابزارسازی", "PA12-CF"),
            ("خطوط بسته‌بندی", "PET-CF"),
            ("دستگاه CNC", "PA6-CF، PET-CF"),
        ]

        for index, item in enumerate(industries, start=1):
            IndustryRecommendation.objects.update_or_create(
                industry=item[0],
                defaults={
                    "recommended_materials": item[1],
                    "sort_order": index,
                },
            )

        parts = [
            ("براکت صنعتی", "PET-CF"),
            ("جیگ مونتاژ", "PET-CF / PA12-CF"),
            ("فیکسچر CNC", "PA12-CF"),
            ("پایه سنسور", "PET-CF"),
            ("پایه دوربین صنعتی", "PET-CF"),
            ("قاب PLC", "PETG-rCF"),
            ("جعبه تابلو برق", "PC-FR"),
            ("هولدر کابل", "PETG-rCF"),
            ("دستگیره دستگاه", "PET-CF"),
            ("چرخ‌دنده", "PA6-CF20"),
            ("پولی", "PA6-CF20"),
            ("بازوی ربات", "PA12-CF"),
            ("هولدر سرووموتور", "PA12-CF"),
            ("قطعات نزدیک موتور", "PPS-CF10"),
            ("قطعات داخل روغن", "PPS-CF10"),
            ("قطعات داخل بنزین", "PPS-CF10"),
            ("قطعات مقاوم به اسید", "PPS-CF10"),
            ("واشر", "TPU95"),
            ("گسکت", "TPU95"),
            ("لرزه‌گیر", "TPU95"),
            ("ضربه‌گیر", "TPU95"),
            ("چرخ ربات", "TPU95"),
            ("قاب تجهیزات", "PLA-CF"),
            ("پنل دستگاه", "PLA-CF"),
            ("نمونه اولیه", "PLA"),
        ]

        for index, item in enumerate(parts, start=1):
            PartRecommendation.objects.update_or_create(
                part_name=item[0],
                defaults={
                    "best_material": item[1],
                    "sort_order": index,
                },
            )

        faqs = [
            (
                "برای ثبت سفارش چه اطلاعاتی لازم است؟",
                "بهتر است عکس قطعه، ابعاد حدودی، کاربرد قطعه، تعداد موردنیاز و شرایط کاری مانند دما، فشار یا تماس با مواد شیمیایی را ارسال کنید.",
            ),
            (
                "آیا امکان مهندسی معکوس قطعه شکسته وجود دارد؟",
                "بله، در بسیاری از موارد می‌توان از روی قطعه شکسته یا نمونه موجود، مدل سه‌بعدی جدید طراحی و سپس تولید کرد.",
            ),
            (
                "قیمت چاپ سه‌بعدی چگونه محاسبه می‌شود؟",
                "قیمت بر اساس ابعاد، وزن، متریال، زمان چاپ، پیچیدگی طراحی و عملیات تکمیلی محاسبه می‌شود.",
            ),
            (
                "چه متریالی برای قطعات صنعتی پیشنهاد می‌شود؟",
                "برای کاربرد عمومی صنعتی PET-CF انتخاب بسیار خوبی است. برای قطعات سنگین‌تر PA6-CF یا PA12-CF و برای محیط‌های شیمیایی یا دمای بالا PPS-CF مناسب‌تر است.",
            ),
        ]

        for index, item in enumerate(faqs, start=1):
            FAQ.objects.update_or_create(
                question=item[0],
                defaults={
                    "answer": item[1],
                    "sort_order": index,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Initial data seeded successfully."))
