from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.contrib import admin
from store.models import ImportedPrintAsset, Product


def validate(model) -> None:
    registered = admin.site._registry.get(model)
    if registered is None:
        raise SystemExit(f"STOP: {model._meta.label} is not registered in admin.")

    admin_class = registered.__class__
    list_display = list(getattr(admin_class, "list_display", ()))
    list_editable = list(getattr(admin_class, "list_editable", ()))
    list_display_links = list(
        getattr(admin_class, "list_display_links", ()) or ()
    )

    missing = [field for field in list_editable if field not in list_display]
    if missing:
        raise SystemExit(
            f"STOP: {model._meta.label} editable fields missing from "
            f"list_display: {missing}"
        )

    linked_editable = [
        field for field in list_editable if field in list_display_links
    ]
    if linked_editable:
        raise SystemExit(
            f"STOP: {model._meta.label} fields cannot be both editable "
            f"and display links: {linked_editable}"
        )

    if list_display and list_display[0] in list_editable:
        raise SystemExit(
            f"STOP: {model._meta.label} first list_display field cannot "
            "be editable."
        )

    print(
        f"ADMIN_CONTRACT {model._meta.label} "
        f"class={admin_class.__name__} "
        f"display={len(list_display)} editable={len(list_editable)} OK"
    )


validate(Product)
validate(ImportedPrintAsset)
print("PHASE35_ADMIN_CONTRACT=OK")
