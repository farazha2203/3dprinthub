# UI/UX Shared Library - Index

تاریخ ایجاد: 2026-08-29

این پوشه کتابخانه مشترک UI/UX پروژه‌های مالک Repository است. منبع اولیه، آرشیو uiux1.zip ارسالی مالک پروژه با 14 منبع و مجموع 2411 صفحه است.

## قانون مالکیت و کپی‌رایت

فایل‌های PDF اصلی داخل Repository Commit نمی‌شوند. فقط دانش مشتق‌شده، عنوان‌ها، سرفصل‌ها، خلاصه‌ها، ruleها، checklistها و الگوهای اجرایی نگه‌داری می‌شوند.

## فایل‌های کتابخانه

- UI_UX_SOURCE_MANIFEST_2026-08-29_FA.md
  - فهرست 14 منبع، تعداد صفحات، نویسنده/ناشر در صورت قابل تشخیص، سرفصل‌ها و خلاصه کاربردی.
- UI_UX_ENGINEERING_PLAYBOOK_FA.md
  - قواعد عملی طراحی UI/UX برای Web, Admin, Dashboard, Mobile/Web App و Data-heavy interfaces.
- UI_UX_PROJECT_ADOPTION_CHECKLIST_FA.md
  - checklist اجباری قبل و بعد از هر تغییر رابط.
- UI_UX_SOURCE_TOPIC_MAP_FA.md
  - نقشه سریع موضوع -> منبع.

## قانون استفاده در همه پروژه‌ها

قبل از تغییر معنی‌دار در Frontend, Admin, Dashboard, Customer Panel, Mobile UI, Forms, Wizard, Navigation, Tables, Cards, Empty States یا Copywriting:
1. مسئله کاربر و task اصلی را مشخص کن.
2. مسیر UI/UX مرتبط را از این Library انتخاب کن.
3. از الگوی پروژه و design system موجود تبعیت کن؛ کتاب جای واقعیت پروژه را نمی‌گیرد.
4. Accessibility, RTL/LTR, responsive behavior, loading/error/empty/success states و keyboard behavior را بررسی کن.
5. از placeholder و داده ساختگی برای status عملیاتی استفاده نکن.
6. تغییر را با screenshot/visual review و تست رفتاری مرتبط verify کن.
7. اگر rule جدیدی به شکل عمومی مفید شد، آن را به این کتابخانه اضافه کن.

## سلسله مراتب تصمیم

User task and business goal
-> usability and accessibility
-> information architecture and hierarchy
-> interaction states and feedback
-> responsive/layout/spacing
-> typography/content
-> color/depth/decoration

زیبایی نباید usability یا clarity را قربانی کند.

## اصول ثابت مشترک

- Don't make me think: تصمیم‌های بی‌دلیل و ambiguity را کم کن.
- Recognition over recall: اطلاعات لازم را نشان بده؛ حافظه کاربر را بی‌جهت درگیر نکن.
- Progressive disclosure: complexity را مرحله‌ای آشکار کن.
- Content-first: layout را حول محتوای واقعی بساز.
- One primary action: در هر context یک CTA اصلی واضح داشته باش.
- Consistent patterns: patternهای آشنا را بی‌دلیل نشکن.
- Design states, not screenshots: default, hover/focus, active, loading, empty, error, success, disabled/read-only.
- Accessibility by default: contrast, keyboard, labels, target size, non-color cues.
- Responsive by task priority: در صفحه کوچک اول task و اطلاعات حیاتی حفظ شوند.
- Human language: label و error message با زبان کاربر، واضح و عملی باشد.
- Data-heavy UI: readability, alignment, sorting/filtering, pagination, sticky headers و density کنترل‌شده.
- Measure and iterate: UI نهایی نیست؛ با داده و feedback اصلاح می‌شود.
