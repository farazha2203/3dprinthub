from django.core.management.base import BaseCommand, CommandError

from store.operator_notifications import send_operator_message


class Command(BaseCommand):
    help = "Check or send a Phase 29 operator alert through configured Telegram, WhatsApp and email channels."

    def add_arguments(self, parser):
        parser.add_argument("--send", action="store_true", help="Send a real test alert.")

    def handle(self, *args, **options):
        import os

        configured = {
            "telegram": bool(os.getenv("TELEGRAM_OPERATOR_BOT_TOKEN") and os.getenv("TELEGRAM_OPERATOR_CHAT_ID")),
            "whatsapp": bool(os.getenv("WHATSAPP_CLOUD_TOKEN") and os.getenv("WHATSAPP_OPERATOR_PHONE") and (os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("WHATSAPP_CLOUD_MESSAGES_URL"))),
            "email": bool(os.getenv("OPERATOR_ALERT_EMAILS")),
        }
        for key, value in configured.items():
            self.stdout.write(f"{key}: {'configured' if value else 'not configured'}")
        if not options["send"]:
            if not any(configured.values()):
                raise CommandError("هیچ کانال اعلان اپراتور تنظیم نشده است.")
            self.stdout.write(self.style.SUCCESS("PHASE29_OPERATOR_ALERT_CONFIG=OK"))
            return

        sent, error = send_operator_message(
            subject="تست اعلان اپراتور 3DPrintHub",
            text="✅ تست اعلان اپراتور فاز ۲۹ با موفقیت از سمت سایت اجرا شد.",
        )
        if not sent:
            raise CommandError(error or "ارسال اعلان ناموفق بود.")
        if error:
            self.stdout.write(self.style.WARNING(error))
        self.stdout.write(self.style.SUCCESS("PHASE29_OPERATOR_ALERT_SENT=OK"))
