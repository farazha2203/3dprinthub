# فاز ۳۰ — پرداخت آنلاین امن پیش‌فاکتور

## هدف

این فاز پرداخت آنلاین بیعانه، کل مبلغ و مانده پیش‌فاکتور را به جریان فعلی کارت‌به‌کارت اضافه می‌کند. پرداخت دستی حذف نشده و اپراتور همچنان می‌تواند رسید بانکی را بررسی کند.

## اصول امنیتی

- شروع پرداخت فقط برای مشتری مالک پیش‌فاکتور و پس از ورود انجام می‌شود.
- مبلغ از سمت مرورگر پذیرفته نمی‌شود؛ سرور آن را دوباره از پیش‌فاکتور محاسبه می‌کند.
- Callback دارای `callback_token` تصادفی و مستقل از شماره سفارش است.
- Authority بازگشتی باید دقیقاً با Authority ذخیره‌شده برابر باشد.
- موفقیت فقط پس از Verify سروربه‌سرور ثبت می‌شود.
- Refresh یا Callback تکراری ثبت مالی دوم ایجاد نمی‌کند.
- پرداخت آنلاین از پنل ادمین قابل تأیید دستی نیست.
- Merchant ID و Access Token فقط در `.env` سرور نگهداری می‌شوند.
- دفتر مالی با `event_key` یکتا ساخته می‌شود و از پنل قابل ویرایش یا حذف نیست.

## حالت‌های پرداخت

- `deposit`: پرداخت بیعانه
- `full`: پرداخت کل مبلغ
- `balance`: تسویه مانده

مبلغ قابل پرداخت از مجموع پرداخت‌های موفق و پرداخت‌های در انتظار/Verify کم می‌شود. کاربر نمی‌تواند مبلغ را با DevTools تغییر دهد.

## تنظیمات `.env`

```env
PAYMENT_GATEWAY_ENABLED=0
PAYMENT_GATEWAY_PROVIDER=zarinpal
PAYMENT_GATEWAY_HTTP_TIMEOUT=15
PAYMENT_GATEWAY_PENDING_TTL_MINUTES=30
PAYMENT_GATEWAY_VERIFY_LOCK_SECONDS=60
PAYMENT_GATEWAY_DESCRIPTION_PREFIX=3DPrintHub

ZARINPAL_MERCHANT_ID=
ZARINPAL_ACCESS_TOKEN=
ZARINPAL_SANDBOX=1
ZARINPAL_CURRENCY=IRT
```

در محیط توسعه ابتدا Sandbox را فعال نگه دارید. در Production فقط پس از تست کامل Callback:

```env
PAYMENT_GATEWAY_ENABLED=1
ZARINPAL_SANDBOX=0
ZARINPAL_CURRENCY=IRT
```

اگر پذیرنده مبلغ را به ریال دریافت می‌کند، `IRR` انتخاب شود. سیستم مبلغ تومان سایت را هنگام ارسال به درگاه در ۱۰ ضرب می‌کند.

## فعال‌سازی در پنل

از مسیر تنظیمات سایت:

- «درگاه پرداخت آنلاین فعال باشد؟» را روشن کنید.
- ارائه‌دهنده را روی زرین‌پال قرار دهید.
- حداقل مبلغ پرداخت را تعیین کنید.
- عنوان نمایشی درگاه را تنظیم کنید.

برای جلوگیری از فعال‌شدن تصادفی، هم `.env` و هم تنظیمات سایت باید فعال باشند.

## نصب ویندوز

```powershell
cd D:\projects\3DPrintHub
Set-ExecutionPolicy -Scope Process Bypass
& ".\APPLY_PHASE30.ps1"
```

## استقرار سرور

قبل از آپلود از `.env`، دیتابیس، `media` و `private_media` نسخه پشتیبان بگیرید. سپس Web/Worker را متوقف کنید، Patch را آپلود کنید و اجرا کنید:

```bash
cd /path/to/3dprinthub
bash APPLY_PHASE30_SERVER.sh /path/to/3dprinthub
```

پس از آن سرویس وب، Worker و Redis را دوباره راه‌اندازی کنید.

## ترتیب تست Sandbox

1. `PAYMENT_GATEWAY_ENABLED=1` و `ZARINPAL_SANDBOX=1` را در محیط Staging تنظیم کنید.
2. در پنل تنظیمات سایت، درگاه آنلاین را فعال کنید.
3. یک پیش‌فاکتور کم‌مبلغ بسازید و تأیید کنید.
4. پرداخت بیعانه را شروع کنید.
5. بررسی کنید Authority در پنل پرداخت ذخیره شده است.
6. بعد از بازگشت، وضعیت باید `paid` و کد پیگیری ثبت شده باشد.
7. همان Callback را دوباره باز کنید؛ تعداد Ledger نباید بیشتر شود.
8. `python manage.py phase30_payment_audit` را اجرا کنید.

## Audit

```bash
python manage.py phase30_payment_audit
```

برای بررسی سخت‌گیرانه Production:

```bash
python manage.py phase30_payment_audit --strict
python manage.py check --deploy
python manage.py deployment_readiness_check --strict
```

## بازگشت و Verify پس از غیرفعال‌شدن درگاه

اگر بعد از شروع پرداخت، اپراتور سوییچ فروش را خاموش کند، Callback تلاش قبلی همچنان Verify می‌شود. این کار برای جلوگیری از بلاتکلیف ماندن پول مشتری ضروری است؛ فقط شروع پرداخت جدید متوقف می‌شود.

## استرداد وجه

مدل Ledger نوع `refund` را پشتیبانی می‌کند، اما فراخوانی واقعی API استرداد در این فاز عمداً به پنل اضافه نشده است. استرداد به سطح دسترسی مالی، Access Token، ثبت دلیل و کنترل دو مرحله‌ای نیاز دارد و در فاز امنیت/مالی تکمیل می‌شود.
