from __future__ import annotations

import json
import re
import urllib.request
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from website.iran_locations import IRAN_LOCATIONS
from website.models import IranCity, IranCounty, IranProvince

SOURCE_URLS = [
    "https://unpkg.com/iran@1.0.2/dist/iran.json",
    "https://raw.githubusercontent.com/arastu/iran/master/dist/iran.json",
]


def normalize(value):
    value = str(value or "").replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"\s+", " ", value).strip()


class Command(BaseCommand):
    help = "استان‌ها، شهرستان‌ها و شهرهای ایران را در دیتابیس ثبت می‌کند."

    def add_arguments(self, parser):
        parser.add_argument("--offline", action="store_true", help="استفاده از داده پشتیبان داخلی")
        parser.add_argument("--clear", action="store_true", help="پاک‌کردن داده‌های قبلی")
        parser.add_argument("--source", default="", help="URL یا مسیر فایل JSON سفارشی")

    def _load_remote(self, source):
        urls = [source] if source and source.startswith(("http://", "https://")) else SOURCE_URLS
        if source and not source.startswith(("http://", "https://")):
            with open(source, "r", encoding="utf-8") as handle:
                return json.load(handle), source
        errors = []
        for url in urls:
            try:
                request = urllib.request.Request(url, headers={"User-Agent":"3DprintHub-location-seeder/1.0"})
                with urllib.request.urlopen(request, timeout=40) as response:
                    return json.loads(response.read().decode("utf-8")), url
            except Exception as exc:
                errors.append(f"{url}: {exc}")
        raise CommandError("دریافت دیتای کامل ناموفق بود. " + " | ".join(errors))

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            IranCity.objects.all().delete(); IranCounty.objects.all().delete(); IranProvince.objects.all().delete()

        records = None
        source_name = "fallback"
        if not options["offline"]:
            try:
                records, source_name = self._load_remote(options["source"])
            except CommandError as exc:
                self.stdout.write(self.style.WARNING(str(exc)))
                self.stdout.write(self.style.WARNING("داده پشتیبان داخلی ثبت می‌شود؛ برای دیتای کامل بعداً دستور را دوباره اجرا کنید."))

        if records:
            province_cache = {}
            county_cache = {}
            for row in records:
                province_name = normalize(row.get("province_name"))
                county_name = normalize(row.get("county_name"))
                city_name = normalize(row.get("city_name"))
                if not province_name or not county_name or not city_name:
                    continue
                province = province_cache.get(province_name)
                if province is None:
                    province, _ = IranProvince.objects.get_or_create(name=province_name, defaults={"is_active":True})
                    province_cache[province_name] = province
                key = (province.pk, county_name)
                county = county_cache.get(key)
                if county is None:
                    county, _ = IranCounty.objects.get_or_create(province=province, name=county_name, defaults={"is_active":True})
                    county_cache[key] = county
                IranCity.objects.update_or_create(
                    province=province, county=county, name=city_name,
                    defaults={
                        "district_name": normalize(row.get("district_name")),
                        "division_code": normalize(row.get("city_division_code")),
                        "source_id": normalize(row.get("id")),
                        "is_active": True,
                    },
                )
        else:
            for province_name, names in IRAN_LOCATIONS.items():
                province, _ = IranProvince.objects.get_or_create(name=normalize(province_name), defaults={"is_active":True})
                for name in names:
                    clean = normalize(name)
                    county, _ = IranCounty.objects.get_or_create(province=province, name=clean, defaults={"is_active":True})
                    IranCity.objects.get_or_create(province=province, county=county, name=clean, defaults={"is_active":True})

        self.stdout.write(self.style.SUCCESS(
            f"ثبت تقسیمات ایران کامل شد: {IranProvince.objects.count()} استان، "
            f"{IranCounty.objects.count()} شهرستان، {IranCity.objects.count()} شهر. منبع: {source_name}"
        ))
