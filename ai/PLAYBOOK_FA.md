# تجربه‌های اجرایی AI — Persian Structured / Low-Cost

## هدف
یک AI قابل استفاده در Windows و Host که:
- فارسی واقعی تولید کند؛
- مدل رایگان را وقتی واقعاً قابل Route و Structured است ترجیح دهد؛
- در نبود Free، فقط Low-cost را در Budget انتخاب کند؛
- خروجی را قبل از Persistence اعتبارسنجی کند؛
- قیمت و Facts را اختراع نکند.

## درس‌های تثبیت‌شده
- «Connected» با «مناسب Product» یکی نیست.
- نام `:free` به تنهایی کافی نیست؛ Endpoint باید Structured response_format داشته باشد.
- Free Router متغیر برای Product identity قابل تکرار مناسب نیست؛ exact model لازم است.
- Model catalogue می‌تواند تغییر کند؛ hard-code کردن نام یک مدل رایگان دائمی نیست.
- Probe کوتاه فارسی + Structured بهترین Gate قبل از انتخاب Auto است.
- انتخاب Model باید cache شود تا هر درخواست Admin لیست مدل‌ها را دوباره Scan نکند.
- Preview-before-apply برای CMS/SEO ضروری است.
- AI metadata نباید در متن عمومی یا technical_notes مشتری ظاهر شود.
- Provider failure نباید قیمت/موجودی/Publish state را تغییر دهد.
- Secret در Environment/OS Secret Store می‌ماند، نه DB.

## Host
Host از همان Provider client پروژه استفاده می‌کند. تفاوت فقط Secret boundary است:
- Windows می‌تواند از Credential Store استفاده کند؛
- Production/Host باید Environment variables داشته باشد.

## Cross-project
`model_policy.py` قابل reuse است. Domain adapter مثل `product_content.py` باید مخصوص هر پروژه باشد، چون Schema و Fact ownership بین فروشگاه، CRM، ISP، Trading و سایر پروژه‌ها متفاوت است.
