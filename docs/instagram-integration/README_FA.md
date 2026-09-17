# اتصال Instagram پروژه 3DPrintHub از طریق Buffer

تاریخ ثبت: 2026-09-17

## تصمیم معماری
- مسیر مستقیم Meta for Developers برای مالک پروژه به دلیل محدودیت Location قابل استفاده نیست.
- Provider انتخابی و رسمی پروژه برای انتشار Instagram، سرویس Buffer است.
- Instagram Professional Account در Buffer توسط مالک پروژه Login/Connect شده است.
- API اصلی Buffer یک GraphQL endpoint واحد در `https://api.buffer.com` دارد.
- احراز هویت API با Bearer API Key انجام می‌شود.
- انتشار مستقیم از Windows Client به Instagram ممنوع است؛ Secret باید فقط در Windows Credential Store یا Server Secret Boundary بماند.

## وضعیت اتصال فعلی
- `Buffer -> Instagram channel login`: تاییدشده توسط مالک.
- `Buffer API key`: هنوز روی این Workstation قابل تایید نیست.
- فایل محلی `D:\projects\3DprintHub\buffer-ker.txt` در زمان ثبت این سند 0 بایت و خالی بود.
- Windows Credential Store نیز در زمان بررسی، `BUFFER_API_KEY` نداشت.
- بنابراین Channel-connected بودن تایید است، اما API transport هنوز `PENDING_CREDENTIAL` است و نباید `API_CONNECTED` اعلام شود.

## قانون انتشار
`Windows Catalog -> Site publish -> HTTPS/public media verification -> Buffer API -> Instagram`

Instagram هیچ‌وقت نباید قبل از موفقیت انتشار Product روی سایت فراخوانی شود.
