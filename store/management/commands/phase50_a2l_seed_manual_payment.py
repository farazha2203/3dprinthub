from __future__ import annotations

import os
import re

from django.core.management.base import BaseCommand, CommandError

from store.phase50_commerce_policy import StorePaymentSettings


ENV_FIELDS = {
    "title": "STORE_PAYMENT_TITLE",
    "bank_name": "STORE_PAYMENT_BANK_NAME",
    "account_holder": "STORE_PAYMENT_ACCOUNT_HOLDER",
    "card_number": "STORE_PAYMENT_CARD_NUMBER",
    "sheba_number": "STORE_PAYMENT_SHEBA_NUMBER",
    "account_number": "STORE_PAYMENT_ACCOUNT_NUMBER",
    "transfer_instructions": "STORE_PAYMENT_TRANSFER_INSTRUCTIONS",
}

_DIGIT_TRANSLATION = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def _env_value(name: str) -> str:
    return str(os.environ.get(name, "") or "").strip()


def _ascii_digits(value: str) -> str:
    return str(value or "").translate(_DIGIT_TRANSLATION)


def _normalise_card_number(value: str) -> str:
    value = re.sub(r"[\s-]+", "", _ascii_digits(value))
    if value and not re.fullmatch(r"\d{16}", value):
        raise CommandError("STORE_PAYMENT_CARD_NUMBER must contain exactly 16 digits.")
    return value


def _normalise_sheba_number(value: str) -> str:
    value = re.sub(r"[\s-]+", "", _ascii_digits(value)).upper()
    if value and not re.fullmatch(r"IR\d{24}", value):
        raise CommandError("STORE_PAYMENT_SHEBA_NUMBER must match IR followed by 24 digits.")
    return value


def _secure_overrides() -> dict[str, str]:
    values: dict[str, str] = {}
    for field, env_name in ENV_FIELDS.items():
        value = _env_value(env_name)
        if not value:
            continue
        if field == "card_number":
            value = _normalise_card_number(value)
        elif field == "sheba_number":
            value = _normalise_sheba_number(value)
        values[field] = value
    return values


class Command(BaseCommand):
    help = (
        "Safely inspect/apply singleton StorePaymentSettings. "
        "Values come only from STORE_PAYMENT_* environment variables; dry-run is the default."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist secure environment overrides. Without this flag no DB write occurs.",
        )
        state = parser.add_mutually_exclusive_group()
        state.add_argument(
            "--activate",
            action="store_true",
            help="Explicitly activate customer-facing manual payment after validation.",
        )
        state.add_argument(
            "--deactivate",
            action="store_true",
            help="Explicitly disable customer-facing manual payment.",
        )

    def handle(self, *args, **options):
        apply_changes = bool(options["apply"])
        activate = bool(options["activate"])
        deactivate = bool(options["deactivate"])

        existing = StorePaymentSettings.objects.order_by("pk").first()
        overrides = _secure_overrides()

        effective = {}
        for field in ENV_FIELDS:
            override = overrides.get(field)
            if override is not None:
                effective[field] = override
            elif existing is not None:
                effective[field] = str(getattr(existing, field, "") or "").strip()
            else:
                effective[field] = ""

        target_active = bool(existing.is_active) if existing is not None else False
        if activate:
            target_active = True
        elif deactivate:
            target_active = False

        destination_configured = bool(
            effective["card_number"]
            or effective["sheba_number"]
            or effective["account_number"]
        )
        holder_configured = bool(effective["account_holder"])

        self.stdout.write(
            "A2R_MANUAL_PAYMENT_EXISTING=" + ("YES" if existing is not None else "NO")
        )
        self.stdout.write(
            "A2R_MANUAL_PAYMENT_SECURE_OVERRIDE_COUNT=" + str(len(overrides))
        )
        self.stdout.write(
            "A2R_MANUAL_PAYMENT_DESTINATION_CONFIGURED="
            + ("YES" if destination_configured else "NO")
        )
        self.stdout.write(
            "A2R_MANUAL_PAYMENT_ACCOUNT_HOLDER_CONFIGURED="
            + ("YES" if holder_configured else "NO")
        )
        self.stdout.write(
            "A2R_MANUAL_PAYMENT_TARGET_ACTIVE=" + ("YES" if target_active else "NO")
        )
        self.stdout.write(
            "A2R_MANUAL_PAYMENT_APPLY=" + ("YES" if apply_changes else "NO")
        )

        if target_active and (not destination_configured or not holder_configured):
            raise CommandError(
                "Manual payment cannot be active without an account holder and at least one destination "
                "(card, Sheba, or account number)."
            )

        if not apply_changes:
            self.stdout.write(self.style.SUCCESS("A2L_MANUAL_PAYMENT_DRY_RUN=PASS"))\n            self.stdout.write(self.style.SUCCESS("A2R_MANUAL_PAYMENT_DRY_RUN=PASS"))\n            return

        if existing is None and not overrides:
            raise CommandError(
                "No existing payment row or STORE_PAYMENT_* secure configuration is available."
            )

        row = existing or StorePaymentSettings()
        for field, value in overrides.items():
            setattr(row, field, value)
        row.is_active = target_active
        row.save()

        self.stdout.write("A2R_MANUAL_PAYMENT_ROW_ID=" + str(row.pk))
        self.stdout.write(
            "A2R_MANUAL_PAYMENT_ACTIVE=" + ("YES" if bool(row.is_active) else "NO")
        )
        self.stdout.write(self.style.SUCCESS("A2R_MANUAL_PAYMENT_APPLY=PASS"))
