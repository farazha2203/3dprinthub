# نصب فاز ۲۲ روی ویندوز

1. سرور Django را متوقف و از پروژه، دیتابیس، `.env` و Media نسخه پشتیبان تهیه کنید.
2. محتوای ZIP Patch را در `D:\projects\3DPrintHub` استخراج و Replace کنید.
3. PowerShell را در ریشه پروژه باز کنید و اجرا کنید:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& ".\APPLY_PHASE22.ps1"
```

4. پروژه را اجرا کنید:

```powershell
.venv\Scripts\activate
python manage.py runserver
```

5. مرورگر را با `Ctrl+F5` تازه‌سازی کامل کنید.

## فعال‌سازی گوگل

در `.env` هر دو مقدار واقعی را قرار دهید:

```env
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
```

Callback توسعه:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

Callback تولید:

```text
https://3dprinthub.ir/accounts/google/login/callback/
```

## بازیابی رمز در تولید

در `.env` تنظیمات SMTP واقعی را قرار دهید. در محیط DEBUG ایمیل بازیابی در Console چاپ می‌شود.

## انتشار GitHub

اسکریپت فاز ۲۲ فقط ASCII است و خطای Encoding اسکریپت قبلی را ندارد:

```powershell
& ".\PUBLISH_PHASE22_GITHUB.ps1"
```
