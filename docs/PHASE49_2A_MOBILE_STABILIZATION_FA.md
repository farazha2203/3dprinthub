# فاز 49.2A — تثبیت نسخه موبایل و هم‌ترازی تست‌های Legacy

## هدف

این زیر‌فاز برای رفع مشکل جدی نمایش نسخه عمومی 3DPrintHub در موبایل ایجاد شد. هدف، کوچک‌کردن نسخه دسکتاپ نیست؛ نسخه موبایل باید یک قرارداد مستقل و قابل تست داشته باشد.

## وضعیت ورودی

خروجی تست محلی کاربر پیش از این اصلاح:

- `catalog_bridge.tests.test_epic49_contract`: 2 تست، OK
- `catalog_bridge`: 9 تست، OK
- `store`: 220 تست، OK و یک تست MySQL به دلیل نبود MySQL محلی skipped
- `website`: شش FAIL/ERROR مربوط به تست‌های قدیمی Phase27/44/46

دو Warning موجود مستقل از این خطاها هستند:

- `ckeditor.W001`
- `store.W026`

## علت خطاهای Website

تست‌های قدیمی هنوز قراردادهای بازنشسته را الزام می‌کردند:

- `store:external_catalog`
- Hero قدیمی Phase27 با `data-p27-home-hero`
- CSS قدیمی Phase27/44
- فایل حذف‌شده `templates/website/partials/external-models-home.html`
- Picker قدیمی `ready_catalog`

این موارد در Phase49.2A عمداً از سطح عمومی حذف شده‌اند؛ بنابراین راه‌حل صحیح، بازگرداندن Route/UI قدیمی نیست. تست‌ها به قرارداد فعال Phase45/49.2A هم‌تراز شدند.

## علت مشکلات موبایل

صفحه عمومی طی چند فاز مختلف CSS دریافت کرده بود:

- `main.css`
- Phase13
- Phase14
- Phase18
- Phase45
- Phase46
- Phase47

هر نسل Responsive جزئی داشت، اما یک لایه نهایی که مالک قرارداد Phone/Tablet باشد وجود نداشت. پیامدهای ممکن:

- ارتفاع زیاد Hero روی تلفن
- Caption و کنترل‌های Slider نامتناسب
- Breakpoint نامنسجم Header
- حالت بینابینی تبلت بین منوی موبایل و دسکتاپ
- فاصله‌های عمودی بزرگ مخصوص Desktop
- Wizard و Tableهای عریض
- Motion/Decoration مستعد ایجاد overflow افقی
- فرم‌هایی که در مرورگر موبایل هنگام Focus زوم می‌شوند

## معماری اصلاح

فایل نهایی Mobile Contract:

`static/css/phase49_2a-mobile-first.css`

این فایل عمداً بعد از CSSهای قدیمی بارگذاری می‌شود تا آخرین تصمیم Responsive متعلق به Phase49.2A باشد.

### Breakpointها

- Phone کوچک: تا 479px
- Phone/Tablet کوچک: تا 767px
- Tablet/Navigation mobile mode: تا 1023px

### عرض‌های پذیرش

- 320px
- 360px
- 390px
- 430px
- 768px
- بازه Tablet تا 1023px

## اصلاحات Header

فایل:

`templates/website/partials/header.html`

اصلاحات:

- Desktop Navigation فقط از `lg` به بالا
- Mobile Navigation تا قبل از `lg`
- حذف dead-zone ناشی از `sm:hidden` در کنار `lg:flex`
- `aria-controls`
- `aria-expanded`
- `aria-hidden`
- منوی Mobile قابل Scroll در Viewport
- منوی موبایل شامل خدمات، متریال، نمونه‌کار، فروشگاه، متخصصان، سفارش و تماس

فایل JS:

`static/js/main.js`

اصلاحات:

- محاسبه واقعی ارتفاع Header برای Scroll Offset
- تابع واحد `setMobileMenu`
- Scroll lock هنگام باز بودن منو
- بستن با Escape
- بستن بعد از انتخاب Link
- بستن خودکار هنگام ورود به عرض Desktop

## اصلاحات Hero

Hero فعال Phase45 حفظ شد و Phase27 بازگردانده نشد.

در موبایل:

- ارتفاع Hero محدود و متناسب با Viewport است
- Transform/zoom تصویر در موبایل حذف می‌شود
- Caption جمع‌وجور و داخل Viewport می‌ماند
- CTA عرض کامل و Touch-safe می‌شود
- Counter/Scroll hint غیرضروری حذف می‌شود
- Controls در فضای امن پایین Hero قرار می‌گیرند
- متن توضیح در عرض خیلی کوچک حذف می‌شود تا Title/CTA فشرده نشوند

## اصلاحات Order Wizard

- Layout اصلی یک‌ستونه
- مراحل Wizard در Container داخلی قابلیت Scroll افقی دارند
- خود Page نباید overflow افقی بگیرد
- Photo/Form/Mode grids در موبایل تک‌ستونه می‌شوند
- Footer دکمه‌ها در عرض کم Stack می‌شود
- Input/Select/Textarea در موبایل حداقل 16px هستند تا Safari/iOS زوم ناخواسته نکند

## اصلاحات Store

`templates/store/base.html` فایل Mobile Contract را Load می‌کند.

موارد:

- Quick navigation موبایل
- Category strip با scroll داخلی
- Filter panel فشرده
- Product cards و content cards با radius/padding موبایل
- Store hero typography و spacing موبایل
- Specification/price rows با wrapping امن

## اصلاحات پنل مشتری

Mobile Contract به `account_base.html` اضافه شد و صفحات مستقل Login/Register نیز به همان قرارداد متصل شدند.

## تست‌های اصلاح‌شده

- `website/test_phase27_home_hero.py`
- `website/test_phase44_frontend.py`
- `website/test_phase44_hero_gallery.py`
- `website/test_phase46_home_experience.py`

هدف این اصلاحات حفظ قراردادهای تاریخی مفید بدون بازگرداندن Public Routeهای بازنشسته است.

## تست جدید

`website/test_phase49_2a_mobile.py`

قراردادهای اصلی:

- Mobile CSS روی Home و Store بار می‌شود
- Mobile CSS بعد از نسل‌های قبلی Load می‌شود
- Breakpointهای اصلی موجود هستند
- Header تا Desktop از Mobile Navigation استفاده می‌کند
- Hero فعال Phase45 است
- هیچ لینک `external_catalog` یا `/store/ready-models/` به Hero برنمی‌گردد

## دیتابیس

این زیر‌فاز هیچ Model جدید، Migration جدید یا حذف Data ندارد.

- MySQL Production دست‌نخورده است
- رکوردهای تاریخی External Catalog حذف نمی‌شوند
- Productهای فعال و Windows Catalog Profileها حفظ می‌شوند

## مرحله پذیرش Local

ترتیب اجباری:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test website.test_phase27_home_hero website.test_phase44_frontend website.test_phase44_hero_gallery website.test_phase46_home_experience website.test_phase49_2a_mobile -v 2
python manage.py test website -v 2
python manage.py test store -v 2
python manage.py test catalog_bridge -v 2
python manage.py test -v 2
```

سپس `runserver` و بررسی Visual حداقل در عرض‌های 320، 360، 390، 430 و 768px.

## معیار توقف

اگر حتی یک `FAIL` یا `ERROR` وجود داشته باشد، Deploy Production متوقف می‌شود و خطا باید در همین Branch رفع شود.

## استقرار Production

فقط بعد از پذیرش Local و تأیید صریح کاربر:

1. Backup MySQL
2. Deploy exact approved commit/tag
3. حفظ `.env`, DB, media/private_media
4. Django check
5. migration فقط در صورت وجود واقعی Migration
6. `collectstatic --noinput`
7. Passenger restart
8. HTTP smoke tests
9. بررسی واقعی Mobile روی سایت Public
10. ثبت exact deployed commit در `PROJECT_CONTEXT.md`

## بدهی‌های فنی جداگانه

### CKEditor

Warning `ckeditor.W001` نشان‌دهنده بدهی امنیتی واقعی است و در یک فاز مستقل باید Migration کنترل‌شده به Editor پشتیبانی‌شده بررسی شود.

### Realtime channel layer

Warning `store.W026` به In-memory channel layer مربوط است. اگر Production نیازمند realtime بین چند Process باشد، باید Shared backend مناسب مثل Redis بر اساس امکانات Host تنظیم شود.

این دو Warning علت Failureهای این زیر‌فاز نیستند و نباید صرفاً Silence شوند.
