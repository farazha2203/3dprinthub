# Generated for 3DprintHub Phase 12

import django.db.models.deletion
from django.db import migrations, models


def repair_source_defaults(apps, schema_editor):
    MarketPricingSetting = apps.get_model("store", "MarketPricingSetting")
    CatalogSourcePolicy = apps.get_model("store", "CatalogSourcePolicy")

    setting, _ = MarketPricingSetting.objects.get_or_create(pk=1)
    old_urls = {
        "https://us.store.bambulab.com/collections/bambu-lab-3d-printer-filament?from=home_web_top_navigation",
        "https://us.store.bambulab.com/collections/bambu-lab-3d-printer-filament",
    }
    if not setting.bambu_collection_url or setting.bambu_collection_url in old_urls:
        setting.bambu_collection_url = "https://us.store.bambulab.com/collections/all-filaments/"
        setting.save(update_fields=["bambu_collection_url"])

    CatalogSourcePolicy.objects.filter(source_kind="makerworld").update(
        discovery_url_template="https://makerworld.com/en/3d-models?orderBy={sort}&page={page}",
        policy_note=(
            "فهرست عمومی، Sitemap و لینک‌های بذر ادمین بررسی می‌شوند. "
            "در صورت HTTP 403 هیچ دورزدنی انجام نمی‌شود."
        ),
    )
    CatalogSourcePolicy.objects.filter(source_kind="grabcad").update(
        discovery_mode="admin_reference",
        public_display_policy="admin_only",
        store_download_links=False,
        policy_note=(
            "GrabCAD فقط مرجع داخلی مدیریت است و به علت JavaScript/HTTP 403 "
            "فقط با لینک بذر ادمین بررسی می‌شود."
        ),
    )


class Migration(migrations.Migration):
    dependencies = [("store", "0012_phase11_source_health_tgju_bambu")]

    operations = [
        migrations.CreateModel(
            name="CatalogSeedURL",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField(max_length=1200, verbose_name="لینک عمومی مدل")),
                ("label", models.CharField(blank=True, max_length=220, verbose_name="عنوان داخلی")),
                ("priority", models.PositiveIntegerField(db_index=True, default=100, verbose_name="اولویت")),
                ("is_active", models.BooleanField(db_index=True, default=True, verbose_name="فعال")),
                ("last_status", models.CharField(blank=True, max_length=30, verbose_name="آخرین وضعیت")),
                ("last_error", models.TextField(blank=True, verbose_name="آخرین خطا")),
                ("last_checked_at", models.DateTimeField(blank=True, null=True, verbose_name="آخرین بررسی")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seed_urls", to="store.printcatalogsource", verbose_name="منبع")),
            ],
            options={
                "verbose_name": "لینک بذر کاتالوگ",
                "verbose_name_plural": "لینک‌های بذر و نمونه منابع",
                "ordering": ["priority", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="catalogseedurl",
            constraint=models.UniqueConstraint(fields=("source", "url"), name="store_seed_source_url_uniq"),
        ),
        migrations.AlterField(
            model_name="marketpricingsetting",
            name="bambu_collection_url",
            field=models.URLField(
                default="https://us.store.bambulab.com/collections/all-filaments/",
                help_text="مجموعه رسمی All Filaments؛ در صورت تغییر ساختار، مسیرهای رسمی جایگزین و product.js بررسی می‌شوند.",
                verbose_name="مجموعه فیلامنت Bambu Lab",
            ),
        ),
        migrations.RunPython(repair_source_defaults, migrations.RunPython.noop),
    ]
