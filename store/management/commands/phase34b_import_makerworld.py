from django.core.management.base import BaseCommand, CommandError

from store.catalog_importer import import_single_url
from store.models import PrintCatalogSource


class Command(BaseCommand):
    help = "Import or refresh one public MakerWorld model URL using __NEXT_DATA__."

    def add_arguments(self, parser):
        parser.add_argument("url")

    def handle(self, *args, **options):
        source = PrintCatalogSource.objects.filter(adapter_key="makerworld", is_active=True).first()
        if source is None:
            raise CommandError("Active MakerWorld source was not found.")
        asset = import_single_url(source, options["url"])
        self.stdout.write(f"ASSET_ID={asset.pk}")
        self.stdout.write(f"TITLE={asset.title}")
        self.stdout.write(f"IMAGE_COUNT={asset.images.count()}")
        self.stdout.write("PHASE34B_MAKERWORLD_IMPORT=OK")
