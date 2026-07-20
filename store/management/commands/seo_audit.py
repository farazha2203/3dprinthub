from django.core.management.base import BaseCommand
from store.models import Category, Product, ServicePage

class Command(BaseCommand):
    help = "گزارش نقص‌های مهم سئو و اسکیما را نمایش می‌دهد."
    def handle(self, *args, **options):
        issues=[]
        for obj in Product.objects.filter(is_active=True):
            if not obj.meta_title: issues.append(f"PRODUCT {obj.pk}: عنوان سئو ندارد")
            if not obj.meta_description: issues.append(f"PRODUCT {obj.pk}: توضیح متا ندارد")
            if not obj.variants.filter(is_active=True).exists(): issues.append(f"PRODUCT {obj.pk}: تنوع فعال و Offer ندارد")
            if not obj.main_image: issues.append(f"PRODUCT {obj.pk}: تصویر اصلی ندارد")
        for obj in Category.objects.filter(is_active=True):
            if not obj.description: issues.append(f"CATEGORY {obj.pk}: توضیح دسته ندارد")
            if not obj.meta_title: issues.append(f"CATEGORY {obj.pk}: عنوان سئو ندارد")
        for obj in ServicePage.objects.filter(is_active=True):
            if not obj.meta_title: issues.append(f"SERVICE {obj.pk}: عنوان سئو ندارد")
            if len((obj.content or '').strip()) < 300: issues.append(f"SERVICE {obj.pk}: محتوای صفحه کوتاه است")
        if issues:
            for issue in issues: self.stdout.write(self.style.WARNING(issue))
            self.stdout.write(self.style.WARNING(f"جمع موارد قابل اصلاح: {len(issues)}"))
        else:
            self.stdout.write(self.style.SUCCESS("هیچ نقص مهم سئو پیدا نشد."))
