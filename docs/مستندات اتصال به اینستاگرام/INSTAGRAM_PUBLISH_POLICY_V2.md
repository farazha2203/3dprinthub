# 3DPrintHub — Instagram Product Publish Policy v2

Version: `instagram-product-v2-20260918`

## قانون اصلی
برای هر Product که روی سایت با HTTPS عمومی تأیید شده است، مسیر اجتماعی استاندارد برابر است با:

`Site Product PASS → Feed Post → Companion Story → Receipts → Verify`

هیچ Feed/Story نباید از URL منبع خارجی محصول منتشر شود؛ منبع تجارت و لینک مقصد فقط 3dprinthub.ir است.

## اصول رسمی و برداشت پروژه
- Instagram/Meta روی محتوای original و recommendation-eligible تأکید دارد؛ Repost و watermark خارجی می‌تواند توزیع پیشنهادی را تضعیف کند.
- Alt Text برای accessibility است. پروژه آن را برای تمام تصاویر اجباری می‌کند، اما آن را «ترفند تضمینی Ranking» تلقی نمی‌کند.
- Hashtag تضمین Reach نیست. 3DPrintHub برای جلوگیری از stuffing فقط 3 تا 8 hashtag واقعاً مرتبط استفاده می‌کند.
- Caption باید دقیقاً درباره همان Product باشد؛ keyword/caption نامرتبط و engagement bait ممنوع است.
- User Tag فقط برای account واقعی و مرتبط (partner/collaborator) مجاز است؛ Tag تصادفی برای Reach ممنوع است.
- AI disclosure فقط وقتی Media واقعاً AI-generated باشد روشن می‌شود. Layout اتوماتیک روی عکس واقعی Product به تنهایی AI-generated محسوب نمی‌شود.

## Feed Post
- Media: تصاویر HTTPS تأییدشده Product، حداکثر 10 تصویر.
- تصویر اصلی همیشه Asset اول است.
- برای هر Asset یک Alt Text غیرخالی الزامی است.
- Caption: عنوان SEO + توضیح مرتبط + حداکثر 4 benefit bullet + CTA + Product UTM URL + 3–8 hashtag.
- Caption حداکثر 2200 کاراکتر.
- metadata.instagram.type = post
- shouldShareToFeed = true
- Shop Grid link = Product tracking URL
- isAiGenerated مطابق واقعیت Asset.

## Companion Story
- Story برای هر Product به‌صورت پیش‌فرض روشن است.
- ابعاد پروژه: 1080×1920 (9:16).
- Hero باید عکس واقعی همان Product باشد، نه محصول مشابه تولیدشده.
- Font: IRANSansWeb(FaNum), تیتر Bold، متن Medium/Regular.
- Visual style: `3dprinthub_instagram_gold_navy_v2`.
- Story شامل Logo، Product title، توضیح کوتاه، چهار bullet، CTA و آدرس Product است.
- فایل ابتدا روی مسیر عمومی HTTPS سایت Upload و HEAD-verified می‌شود؛ سپس Buffer آن را Publish می‌کند.
- Buffer Story و Feed receipt مستقل دارند.
- اگر Feed موفق و Story ناموفق شود، Retry نباید Feed دوم بسازد؛ فقط Story ناقص تکمیل می‌شود.
- در 502/UPSTREAM_SERVER_ERROR قبل از Retry، Recent Posts با Asset URL reconcile می‌شوند تا Duplicate ساخته نشود.
- Highlight creation/add-to-highlight در API عمومی فعلی Buffer پوشش داده نشده و جزء operator/UI step است.

## Idempotency / Failure Rules
1. fingerprint مرجع = server_ack_json همان revision عمومی Product.
2. Feed receipt statuses: `instagram_published|instagram_submitted`.
3. Story receipt statuses: `instagram_story_published|instagram_story_submitted`.
4. Revision یکسان دوباره Feed نمی‌شود.
5. Story failure کل Product social publish را Failure نشان می‌دهد، ولی Feed receipt از بین نمی‌رود.
6. Retry revision یکسان Feed را reuse و Story را resume می‌کند.
7. Secretها فقط Windows Credential Store؛ هیچ Token/API key در SQLite/Git/receipt ثبت نمی‌شود.

## نکات Reach که «قانون قطعی Ranking» نیستند
- Hashtag، Alt Text، طول Caption یا زمان انتشار به‌تنهایی تضمین View نیستند.
- هدف SEO داخلی پروژه: فهم بهتر موضوع Product، دسترس‌پذیری، جستجوپذیری و consistency.
- کیفیت/اصالت Media و eligibility حساب و محتوا برای Recommendations مهم‌تر از stuffing است.
- Performance باید بعداً از Insights/Metrics واقعی ارزیابی و policy بر اساس داده اصلاح شود.

## منابع رسمی
Meta / Instagram:
- https://about.fb.com/news/2024/10/best-practices-education-hub-creators-instagram/
- https://about.fb.com/ltam/news/2024/05/ayudando-a-los-creadores-a-encontrar-nuevas-audiencias/
- https://about.fb.com/news/2026/01/2026-ai-drives-performance/

Buffer API:
- https://developers.buffer.com/types/InstagramPostMetadata.html
- https://developers.buffer.com/types/InstagramPostMetadataInput.html
- https://developers.buffer.com/types/CreatePostInput.html
- https://developers.buffer.com/examples/create-instagram-post-with-user-tags.html
- https://developers.buffer.com/reference.html

## Windows Publisher implementation
Entry point: `catalog_center/qt6/kernel.py::InstagramCore.publish_many`

Policy:
- `catalog_center/app/social_content_policy.py`
- `catalog_center/app/instagram_publish.py::canonical_site_payload`

Story renderer/uploader:
- `catalog_center/app/instagram_story_asset.py`

Buffer transport/retry/reconciliation:
- `catalog_center/app/buffer_publish.py`

Settings:
- Provider = Buffer
- `instagram_companion_story_enabled=1` by default
- Story remote root default: `/public_html/media/instagram/stories/products`

### محدودیت Link Sticker در Story
فیلد `metadata.instagram.link` در مستندات Buffer به‌عنوان Shop Grid link تعریف شده است؛ پروژه نباید آن را معادل Link Sticker native Story فرض کند.
تا وقتی Buffer/Instagram API مسیر رسمی automatic برای Link Sticker ارائه نکند، Story آدرس Product را به‌صورت بصری نمایش می‌دهد و هیچ قابلیت غیررسمی/Private API استفاده نمی‌شود.
