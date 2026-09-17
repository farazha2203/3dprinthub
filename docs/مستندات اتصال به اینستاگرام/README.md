# مستندات اتصال به اینستاگرام — 3DPrintHub

این پوشه مرجع رسمی پروژه برای اتصال Instagram از طریق Buffer است.

## وضعیت 2026-09-17
- اتصال Instagram Professional به Buffer توسط مالک انجام شده است: `CHANNEL_CONNECTED`.
- Meta for Developers به‌علت محدودیت Location مسیر اجرایی پروژه نیست.
- Provider انتخابی پروژه: `Buffer API`.
- فایل محلی `D:\projects\3DPrintHub\buffer-ker.txt` در آخرین بررسی 0 بایت بود.
- `BUFFER_API_KEY` در Windows Credential Store نیز در آخرین بررسی موجود نبود.
- بنابراین وضعیت API فعلی: `PENDING_CREDENTIAL` و نه `API_CONNECTED`.

## ترتیب اجباری انتشار
`Windows Catalog -> Site Publish -> Public HTTPS Verification -> Buffer -> Instagram`

هیچ Productی نباید قبل از موفقیت انتشار و قابل‌دسترسی بودن URL و Media سایت به Instagram ارسال شود.

## فایل‌های این پوشه
- `README_FA.md`: تصمیم معماری و وضعیت اتصال.
- `BUFFER_API_CONTRACT.md`: قرارداد GraphQL Buffer.
- `IMPLEMENTATION.md`: قرارداد پیاده‌سازی داخل 3DPrintHub.
- `SECURITY_AND_SECRETS.md`: قوانین امنیت و Secret.
- `SOURCES.md`: منابع رسمی Buffer.
- `examples/`: نمونه Query/Mutation و Probe بدون Secret.
