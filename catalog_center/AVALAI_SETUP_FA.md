# اتصال AvalAI در Catalog Intelligence v8.4

برنامه از API سازگار با OpenAI در `https://api.avalai.ir/v1` استفاده می‌کند و مدل ثابت ندارد.
در هر اتصال، مدل‌های قابل دسترسی همان کلید از `/v1/models` دریافت می‌شوند.

## محل کلیدهای قدیمی روی ویندوز

- `D:\projects\3DPrintHub\APIKEY-AVAL.txt`
- `D:\projects\3DPrintHub\APIKEY_AVAL.txt`
- OpenAI مستقیم: `D:\projects\3DPrintHub\APIKEY.txt`

برنامه می‌تواند این فایل‌ها را بخواند و با دکمه انتقال، Secret را به Windows Credential Store منتقل کند.
کلید داخل SQLite، Batch، Log یا GitHub نوشته نمی‌شود.

## تست زنده

```powershell
& "D:\projects\3dprinthub_catalog_center\LIVE_AI_TEST.ps1" -Provider avalai
```

خروجی موفق باید شامل این موارد باشد:

- `AI_MODELS_COUNT=...`
- `AI_MODEL_SELECTED=...`
- `AI_LIVE_CONNECTION=OK`
- `AI_LIVE_TRANSLATION=OK`
- `AI_LIVE_CONTENT_GENERATION=OK`
- `AI_LIVE_SEO=OK`
- `AI_LIVE_MATERIAL_RECOMMENDATION=OK`
- `AI_PROVIDER_READY=OK`

Secret در خروجی چاپ نمی‌شود.
