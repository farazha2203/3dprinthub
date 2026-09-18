# 3DPrintHub Instagram Story Standard

## هدف
این سند استاندارد اجباری Storyهای محصول 3DPrintHub است.
Story باید از عکس واقعی همان محصول موجود در سایت/Instagram/Buffer استفاده کند؛ ساخت مدل شبیه‌سازی‌شده جایگزین عکس واقعی ممنوع است.

## نسبت و شبکه
- خروجی نهایی: 1080x1920 (9:16)
- Safe area بالا و پایین برای UI اینستاگرام رعایت شود.
- محصول Hero حدود 45 تا 60 درصد ارتفاع تصویر را بگیرد.
- لوگوی 3DPrintHub در ناحیه بالا، بدون مزاحمت برای عنوان.
- عنوان فارسی درشت، سپس توضیح کوتاه، سپس CTA.
- دامنه 3dprinthub.ir زیر CTA قرار گیرد.
- ردیف ویژگی‌ها با 3 تا 4 آیکون کوچک در پایین استفاده شود.

## Style ID
`3dprinthub_instagram_gold_navy_v1`

## زبان بصری
- زمینه Navy/Black عمیق
- Gold متالیک گرم برای تیتر، قاب و CTA
- نور سینمایی گرم و کنتراست بالا
- تایپوگرافی فارسی خوانا، بدون متن متراکم
- محصول واقعی باید از نظر شکل، رنگ و جزئیات دستکاری ماهوی نشود.

## منبع تصویر محصول
اولویت منبع تصویر: 1) تصویر همان Product در سایت 3dprinthub.ir، 2) Media همان Post در Buffer/Instagram، 3) Asset اصلی Publisher.
اگر تطبیق Product قطعی نباشد Story منتشر نشود.

## متن Story
- تیتر کوتاه و benefit-led باشد.
- خط دوم نوع محصول و مزیت اصلی را بگوید.
- CTA استاندارد: «مشاهده محصول» یا «مشاهده محصولات».
- لینک مقصد باید URL دقیق همان Product باشد، نه فقط Home Page.
- در صورت استفاده از Asset تولیدشده با AI، metadata مناسب Buffer/Instagram ثبت شود.

## گردش‌کار انتشار
1. Product و عکس Canonical تطبیق داده شود.
2. Story asset با همین Template ساخته شود.
3. Asset روی URL عمومی HTTPS سایت قرار گیرد.
4. Buffer `createPost` با `metadata.instagram.type=story` اجرا شود.
5. وضعیت Publish ثبت و Verify شود.
6. اگر Highlight مرتبط وجود دارد، Story برای مرحله اپراتوری Add-to-Highlight صف شود.

## سه Story پایه فعلی
- آباژور
- پایه کیک
- اکسسوری کریسمس
این سه مورد باید با عکس واقعی همان Product/Post موجود ساخته شوند و از همین Grid و ابعاد نمونه پیروی کنند.

## V2 — IRANSans production style

Style ID: `3dprinthub_instagram_gold_navy_v2_iransans`

- تیتر اصلی: IRANSans Black.
- زیرتیتر و kicker: IRANSans Medium.
- CTA: IRANSans Bold.
- ویژگی‌ها و متن عادی: IRANSans Regular.
- فایل‌های فونت از پکیج لایسنس‌دار محلی کاربر خوانده می‌شوند و **نباید** وارد Git/GitHub یا artifact عمومی شوند.
- Renderer canonical: `scripts/social/render_instagram_story.py`.
- تصاویر محصول باید همان media واقعی Product/Post باشند؛ تغییر ماهوی شکل محصول یا جایگزینی با محصول شبیه‌سازی‌شده ممنوع است.
- خروجی canonical همچنان 1080x1920 و Gold/Navy است.
- قبل از Buffer publish، asset باید از URL عمومی HTTPS با HTTP 200 و MIME صحیح قابل خواندن باشد.
- اگر Meta خطای `It takes too long to download the media` داد، بدون تغییر طراحی از نسخه بهینه‌شده media استفاده شود و فقط Story خطادار retry شود؛ Storyهای `sent` دوباره ارسال نشوند.
- وضعیت نهایی فقط پس از query مجدد Buffer و مشاهده `status=sent` بسته می‌شود.
