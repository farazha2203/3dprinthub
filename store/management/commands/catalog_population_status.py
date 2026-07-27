from django.core.management.base import BaseCommand

from store.catalog_population import catalog_population_counts


class Command(BaseCommand):
    help = "نمایش تعداد واقعی مدل‌های دریافت‌شده، مجاز و منتشرشده"

    def handle(self, *args, **options):
        counts = catalog_population_counts()
        labels = {
            "all_imported": "کل مدل‌های ذخیره‌شده",
            "makerworld": "MakerWorld",
            "printables": "Printables",
            "allowed": "مجوز تجاری معتبر",
            "public": "تأیید عمومی",
            "public_with_image": "قابل نمایش با تصویر محلی",
        }
        for key, value in counts.items():
            self.stdout.write(f"{labels[key]}: {value}")
