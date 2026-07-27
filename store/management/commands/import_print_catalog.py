from django.core.management.base import BaseCommand, CommandError

from store.catalog_importer import import_single_url
from store.models import PrintCatalogSource


class Command(BaseCommand):
    help = "واردکردن یک صفحه فایل آماده چاپ از منبع تعریف‌شده"

    def add_arguments(self, parser):
        parser.add_argument("--source", required=True, help="کد منبع در پنل مدیریت")
        parser.add_argument("--url", required=True, help="آدرس صفحه فایل")

    def handle(self, *args, **options):
        try:
            source = PrintCatalogSource.objects.get(code=options["source"], is_active=True)
        except PrintCatalogSource.DoesNotExist as error:
            raise CommandError("منبع فعال با این کد پیدا نشد.") from error
        try:
            asset = import_single_url(source, options["url"])
        except Exception as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS(f"وارد شد: {asset.title} | شناسه {asset.pk}"))
