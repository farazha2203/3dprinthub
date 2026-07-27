# فاز ۲۷ — Hero تمام‌صفحه و آمادگی استقرار

## Hero صفحه اصلی
- اسلایدر تمام‌عرض و تمام‌ارتفاع فقط در بخش اول صفحه اجرا می‌شود.
- جدیدترین ورودی‌های قابل نمایش کاتالوگ بر اساس `imported_at` انتخاب می‌شوند.
- تصویر محلی بر تصویر Remote اولویت دارد.
- هر پس‌زمینه و کارت عنوان به صفحه جزئیات همان محصول متصل است.
- شکست تصویر Remote باعث جایگزینی لوگوی برند می‌شود.
- Swipe موبایل، کنترل دستی، توقف هنگام Hover/Focus و Reduced Motion رعایت شده است.
- هیچ CSS عمومی پنل مدیریت، فونت یا برندینگ تغییر داده نشده است.

## ارزیابی قبل از سرور

### مسدودکننده‌های استقرار Production
1. `.env` تولید با Secret، دامنه، دیتابیس، SMTP، Google OAuth، Redis و Health Token کامل شود.
2. MySQL یا PostgreSQL واقعی آماده و Backup زمان‌بندی‌شده برقرار شود.
3. Redis، سرویس ASGI و Worker تحلیل لینک به‌صورت systemd یا سرویس معادل اجرا شوند.
4. Nginx برای Static، Media، WebSocket و HTTPS تنظیم شود.
5. `PRIVATE_MEDIA_ROOT` خارج از `public_html` و با دسترسی محدود باشد.
6. Migration، Collectstatic، Site domain، Superuser و Google callback بررسی شوند.
7. درگاه پرداخت واقعی و Callback امضاشده پیش از دریافت وجه عمومی تکمیل شود.
8. CKEditor 4 پیش از تولید حساس به CKEditor 5 یا ویرایشگر پشتیبانی‌شده مهاجرت کند.

### قابل استقرار به‌عنوان Staging
پروژه پس از عبور از تست‌ها می‌تواند برای تست داخلی/مشتریان محدود روی سرور Staging قرار گیرد؛ دریافت وجه عمومی بهتر است تا تکمیل درگاه، امنیت و Backup فعال نشود.

## فرمان‌های بررسی
```powershell
python manage.py check --deploy
python manage.py deployment_readiness_check
python manage.py deployment_readiness_check --strict
python manage.py showmigrations
python manage.py test website.test_phase27_home_hero
```

## Epicهای باقی‌مانده پیشنهادی
1. **Epic 28 — درگاه پرداخت و دفتر مالی تراکنش:** Callback امضاشده، Idempotency، تطبیق تراکنش و Refund.
2. **Epic 29 — امنیت Production:** CKEditor 5، MFA مدیر، Rate Limit، CSP، اسکن فایل و Audit امنیتی.
3. **Epic 30 — عملیات تولید:** صف دستگاه‌ها، زمان‌بندی چاپ، QC، ضایعات، مصرف واقعی فیلامنت و تحویل.
4. **Epic 31 — فایل مهندسی:** Viewer سه‌بعدی، Versioning، Watermark، دسترسی زمان‌دار و فایل مشتق‌شده.
5. **Epic 32 — مانیتورینگ و Backup:** Sentry/Logging، Health checks، Backup DB/Media، Restore drill و Alert.
6. **Epic 33 — SEO و Performance:** Cache، تصاویر Proxy/Thumbnail، Sitemap کاتالوگ، Core Web Vitals و CDN.
