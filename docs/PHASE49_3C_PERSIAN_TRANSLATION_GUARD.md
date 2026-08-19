# Phase49.3C-1 Appendix — Persian Translation Guard

## Regression

مسیر `✨ ترجمه دقیق EN → FA` از مسیر `commerce` جداست. Guard اولیه فقط commerce را کنترل می‌کرد؛ بنابراین ممکن بود Translation workflow هنوز خروجی انگلیسی یا نیمه‌انگلیسی را قبول کند.

## Fix

`catalog_center/app/phase49_3c_persian_translate_guard.py`

این wrapper بعد از Translation:

1. فیلدهای فارسی/SEO را بررسی می‌کند.
2. در صورت خروجی غیر فارسی، Structured Persian Repair اجرا می‌کند.
3. اگر Provider Repair شکست بخورد، متن انگلیسی را به فیلد فارسی منتقل نمی‌کند.
4. Fallback فارسی محافظه‌کارانه را اعمال می‌کند.
5. خطای Repair را در Diagnostic logger ثبت می‌کند.

Launcher marker:
`EPIC49_3C_PERSIAN_TRANSLATE_GUARD=ENABLED`

Dedicated contract test:
`catalog_center/tests/test_epic49_phase49_3c_persian_translate_guard.py`

CI اکنون این فایل را به‌صورت explicit compile و test می‌کند.

Production همچنان ممنوع است تا Windows Local QA کامل شود.
