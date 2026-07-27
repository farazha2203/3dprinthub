# انتشار تجمیعی فاز ۳۰ روی GitHub و cPanel

## علت توقف قبلی GitHub

`git switch -c` با موفقیت Branch محلی را ساخته بود، اما Windows PowerShell پیام عادی Git را که از stderr آمده بود به شکل `NativeCommandError` تفسیر کرد و اسکریپت پیش از Commit و Push متوقف شد.

نسخه اصلاح‌شده موفقیت Git را فقط از Exit Code واقعی تشخیص می‌دهد. اگر Branch از قبل روی سیستم ساخته شده باشد، همان Branch را ادامه می‌دهد.

## چرا انتشار باید تجمیعی باشد؟

شاخه `main` روی GitHub فقط Snapshot اولیه پروژه را دارد و فازهای ۲۷ تا ۳۰ در آن نیستند. فاز ۳۰ به مدل‌ها، Migrationها، قالب‌ها و سرویس‌های فازهای قبلی وابسته است؛ بنابراین اسکریپت جدید کل Source فعلی را Stage می‌کند، ولی به کمک `.gitignore` این موارد را منتشر نمی‌کند:

- `.env`
- دیتابیس SQLite
- `.venv` و محیط‌های مجازی
- `media`
- `private_media`
- `staticfiles`
- Logها و Cacheها

همچنین فایل‌های بیش از ۹۵ مگابایت قبل از Commit باعث توقف امن انتشار می‌شوند.

## انتشار GitHub

در PowerShell ویندوز:

```powershell
cd D:\projects\3DPrintHub
Set-ExecutionPolicy -Scope Process Bypass
& ".\PUBLISH_PHASE30_GITHUB.ps1"
```

برای اجرای دوباره کل ۲۵۶ تست پیش از Push:

```powershell
& ".\PUBLISH_PHASE30_GITHUB.ps1" -RunFullTests
```

Branch مقصد:

```text
feature/phase30-online-payment-gateway
```

## استقرار cPanel/Passenger

مشخصات فعلی پروژه:

```text
Project: /home/sfkilvrs/3dprinthub
Virtualenv: /home/sfkilvrs/virtualenv/3dprinthub/3.12
Domain: 3dprinthub.ir
```

قبل از Deploy از طریق cPanel از دیتابیس، `media`، `private_media` و `.env` نسخه پشتیبان بگیرید.

سپس در ترمینال Remote SSH/SFTP مربوط به VS Code:

```bash
cd /home/sfkilvrs/3dprinthub
chmod +x deploy/cpanel/DEPLOY_PHASE30_CPANEL.sh
bash deploy/cpanel/DEPLOY_PHASE30_CPANEL.sh
```

این اسکریپت:

1. تغییرات Track‌شده سرور را کنترل می‌کند.
2. Commit فعلی و `.env` را برای Rollback ثبت می‌کند.
3. Branch فاز ۳۰ را از GitHub دریافت می‌کند.
4. وابستگی‌ها را نصب می‌کند.
5. Source و Migrationها را بررسی می‌کند.
6. Migrationها و `collectstatic` را اجرا می‌کند.
7. Audit فازهای ۲۹ و ۳۰ را اجرا می‌کند.
8. با `touch tmp/restart.txt` برنامه Passenger را Restart می‌کند.

## تنظیمات ضروری `.env` روی cPanel

```env
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=3dprinthub.ir,www.3dprinthub.ir
DJANGO_CSRF_TRUSTED_ORIGINS=https://3dprinthub.ir,https://www.3dprinthub.ir
SITE_BASE_URL=https://3dprinthub.ir
USE_X_FORWARDED_PROTO=1
SECURE_SSL_REDIRECT=1
SECURE_HSTS_SECONDS=0
STATIC_ROOT=/home/sfkilvrs/public_html/static
MEDIA_ROOT=/home/sfkilvrs/public_html/media
PRIVATE_MEDIA_ROOT=/home/sfkilvrs/3dprinthub/private_media
REALTIME_REDIS_URL=
REALTIME_ALLOW_POLLING_ONLY=1
REALTIME_REDIS_AUTO_FALLBACK=1
LINK_WORKER_HEALTH_TOKEN=یک-رشته-تصادفی-حداقل-۲۴-کاراکتری
PAYMENT_GATEWAY_ENABLED=0
ZARINPAL_SANDBOX=1
```

`PAYMENT_GATEWAY_ENABLED` تا پایان تست Callback عمومی Sandbox روی صفر باقی بماند. همچنین در استقرار اول `SECURE_HSTS_SECONDS=0` باشد؛ بعد از اطمینان کامل از SSL و ریدایرکت HTTPS می‌توان HSTS را مرحله‌ای فعال کرد.

## تنظیم دامنه Django Site

پس از Deploy:

```bash
/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python manage.py shell -c "from django.contrib.sites.models import Site; s=Site.objects.get(pk=1); s.domain='3dprinthub.ir'; s.name='3DPrintHub'; s.save(); print(s.domain)"
```

سپس:

```bash
/home/sfkilvrs/virtualenv/3dprinthub/3.12/bin/python manage.py deployment_readiness_check
```

## Rollback کد

Commit قبل از Deploy در این مسیر ثبت می‌شود:

```text
~/3dprinthub-deploy-backups/<timestamp>/before_commit.txt
```

برای Rollback کد، ابتدا Commit را بخوانید و سپس با هماهنگی Migration دیتابیس به آن Commit برگردید. بدون بررسی Migrationها، `git reset --hard` اجرا نشود.
