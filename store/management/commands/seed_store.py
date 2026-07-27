from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import Category, PricingSetting, PrintQuality, ServicePage


class Command(BaseCommand):
    help = "ایجاد دسته‌بندی‌ها، کیفیت‌های چاپ و صفحات خدمات اولیه فروشگاه"

    def handle(self, *args, **options):
        PricingSetting.objects.get_or_create(
            pk=1,
            defaults={
                "default_hourly_rate": 100_000,
                "default_labor_percent": Decimal("30"),
                "minimum_order_amount": 0,
                "packaging_fee": 0,
                "tax_percent": 0,
            },
        )

        qualities = [
            ("economy", "اقتصادی", Decimal("0.28"), "چاپ سریع‌تر برای قطعات عمومی و کم‌جزئیات", 10),
            ("standard", "استاندارد", Decimal("0.20"), "تعادل مناسب میان کیفیت، زمان و قیمت", 20),
            ("fine", "ظریف", Decimal("0.16"), "سطح بهتر و جزئیات بیشتر", 30),
            ("ultra-fine", "فوق‌ظریف", Decimal("0.12"), "برای مدل‌های نمایشی و جزئیات حساس", 40),
        ]
        for code, name, layer_height, description, sort_order in qualities:
            PrintQuality.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "layer_height_mm": layer_height,
                    "description": description,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

        roots = [
            ("قطعات خودرو", "automotive-parts", "automotive", 10),
            ("قطعات موتورسیکلت", "motorcycle-parts", "motorcycle", 20),
            ("قطعات لوازم خانگی", "home-appliance-parts", "home_appliance", 30),
            ("قطعات صنعتی", "industrial-parts", "industrial", 40),
            ("ماکت و پروژه دانشگاهی", "academic-models", "academic", 50),
            ("محصولات خلاقانه", "creative-products", "creative", 60),
        ]
        root_map = {}
        for name, slug, section, sort_order in roots:
            obj, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "section": section,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )
            root_map[section] = obj

        children = [
            ("قطعات داشبورد", "dashboard-parts", "automotive", 10),
            ("خار، بست و درپوش خودرو", "automotive-clips-caps", "automotive", 20),
            ("دریچه کولر و قطعات تهویه", "car-air-vent-parts", "automotive", 30),
            ("قاب کیلومتر و کلید موتور", "motorcycle-covers-switches", "motorcycle", 10),
            ("چرخ‌دنده لوازم خانگی", "appliance-gears", "home_appliance", 10),
            ("دستگیره، قفل و دکمه", "appliance-handles-locks-buttons", "home_appliance", 20),
            ("جیگ و فیکسچر", "jigs-fixtures", "industrial", 10),
            ("چرخ‌دنده و پولی صنعتی", "industrial-gears-pulleys", "industrial", 20),
            ("ماکت معماری", "architectural-models", "academic", 10),
            ("پروژه‌های دانشجویی", "student-projects", "academic", 20),
            ("نقاشی کودک به فیگور", "kids-drawing-figure", "creative", 10),
            ("فیگور از روی عکس", "custom-photo-figure", "creative", 20),
        ]
        for name, slug, section, sort_order in children:
            Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "parent": root_map[section],
                    "section": section,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

        pages = [
            (
                "printing",
                "خدمات پرینت سه‌بعدی صنعتی و دقیق",
                "3d-printing-services",
                "چاپ قطعات صنعتی، نمونه اولیه و محصولات سفارشی با متریال‌های مهندسی و قیمت‌گذاری شفاف.",
                "در این صفحه خدمات پرینت سه‌بعدی، انتخاب متریال، کیفیت چاپ، زمان تحویل و فرایند کنترل کیفیت به‌صورت کامل معرفی می‌شود.",
            ),
            (
                "reverse_engineering",
                "مهندسی معکوس و بازسازی قطعات کمیاب",
                "reverse-engineering-parts",
                "طراحی و ساخت مجدد قطعات شکسته یا نایاب از روی نمونه فیزیکی، عکس و اندازه‌برداری دقیق.",
                "فرایند مهندسی معکوس شامل بررسی نمونه، اندازه‌برداری، مدل‌سازی، انتخاب متریال، چاپ آزمایشی و تست نصب است.",
            ),
            (
                "automotive",
                "ساخت قطعات کمیاب خودرو و موتورسیکلت",
                "automotive-motorcycle-parts",
                "ساخت قطعات داشبورد، خار، بست، قاب، دکمه، دریچه و قطعات مکانیزم خودرو و موتورسیکلت.",
                "قطعات بر اساس برند، مدل و محل نصب دسته‌بندی می‌شوند و سازگاری هر محصول پیش از سفارش قابل مشاهده است.",
            ),
            (
                "home_appliance",
                "ساخت قطعات نایاب لوازم خانگی",
                "home-appliance-replacement-parts",
                "بازسازی چرخ‌دنده، دستگیره، قفل، دکمه، پایه و قطعات پلاستیکی لوازم خانگی.",
                "به‌جای تعویض کامل دستگاه، قطعه شکسته بررسی و با متریال مناسب بازطراحی و تولید می‌شود.",
            ),
            (
                "model_making",
                "ماکت‌سازی معماری و پروژه‌های دانشگاهی",
                "architectural-student-model-making",
                "چاپ، مونتاژ و پرداخت ماکت‌های معماری، صنعتی و پروژه‌های دانشگاهی با تحویل زمان‌بندی‌شده.",
                "فایل‌های طراحی بررسی، برای چاپ تقسیم‌بندی و سپس با توجه به مقیاس، سطح جزئیات و رنگ موردنیاز تولید می‌شوند.",
            ),
            (
                "kids_drawing",
                "تبدیل نقاشی کودک به فیگور سه‌بعدی",
                "kids-drawing-to-3d-figure",
                "نقاشی کودک را به یک کاراکتر سه‌بعدی واقعی و هدیه ماندگار تبدیل می‌کنیم.",
                "پس از دریافت نقاشی، مدل سه‌بعدی طراحی می‌شود، پیش‌نمایش برای تأیید ارسال و سپس فیگور چاپ و رنگ‌آمیزی می‌شود.",
            ),
            (
                "custom_figure",
                "ساخت فیگور سفارشی از روی عکس",
                "custom-3d-figure-from-photo",
                "طراحی و ساخت فیگور شخصی، خانوادگی یا حیوان خانگی از روی عکس.",
                "اندازه، سبک، پایه، متن، رنگ‌آمیزی و بسته‌بندی هدیه بر اساس سفارش مشتری انتخاب می‌شود.",
            ),
        ]
        for index, (service_type, title, slug, short_description, content) in enumerate(pages, start=1):
            ServicePage.objects.update_or_create(
                slug=slug,
                defaults={
                    "service_type": service_type,
                    "title": title,
                    "short_description": short_description,
                    "content": content,
                    "meta_title": f"{title} | 3DprintHub",
                    "meta_description": short_description,
                    "sort_order": index * 10,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Store foundation data seeded successfully."))
