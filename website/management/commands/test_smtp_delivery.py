from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send one explicit SMTP test email. No email is sent unless --to is provided."

    def add_arguments(self, parser):
        parser.add_argument("--to", required=True, help="Destination email address")

    def handle(self, *args, **options):
        recipient = options["to"].strip()
        if not recipient or "@" not in recipient:
            raise CommandError("A valid --to email is required.")
        backend = str(getattr(settings, "EMAIL_BACKEND", "") or "")
        if "console" in backend.lower():
            raise CommandError("EMAIL_BACKEND is console; SMTP is not configured.")
        sent = send_mail(
            subject="3DPrintHub SMTP test",
            message="این ایمیل برای بررسی اتصال SMTP سامانه 3DPrintHub ارسال شده است.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        if sent != 1:
            raise CommandError(f"SMTP backend returned sent={sent}.")
        self.stdout.write(self.style.SUCCESS(f"SMTP test email sent to {recipient}."))
