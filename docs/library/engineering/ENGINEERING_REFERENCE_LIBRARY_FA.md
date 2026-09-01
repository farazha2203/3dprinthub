# Shared Engineering Reference Library — 2026-09-01

این سند یک کتابخانه مشتق‌شده و اجرایی برای همه پروژه‌هاست. فایل PDF/کتاب دارای کپی‌رایت در Repository ذخیره نمی‌شود؛ فقط نام دقیق منبع، کاربرد، لینک رسمی/سورس عمومی و قواعد استفاده ثبت می‌شود.

## قانون تقدم منابع

1. وضعیت واقعی Repository/Runtime/Host/Database هر پروژه.
2. مستندات رسمی و Source Code همان نسخه‌ای که پروژه واقعاً استفاده می‌کند.
3. استانداردهای امنیتی جاری مانند OWASP ASVS و OWASP Cheat Sheet Series.
4. کتاب‌ها و مثال‌های این کتابخانه به‌عنوان مرجع طراحی/یادگیری.
5. هر مثال کتاب قبل از استفاده باید با نسخه واقعی پروژه Verify و با تست Local اثبات شود.

هیچ کد یا دستور قدیمی صرفاً به دلیل حضور در کتاب نباید Copy/Paste و اجرا شود.

## منابع پذیرفته‌شده

### 1) Mastering Django ORM: Performance Tuning and Advanced Query Optimization — Afsal MS — Apress, 2026

**رتبه:** PRIMARY / HIGH VALUE

**به درد چه می‌خورد:** بهینه‌سازی QuerySet، بررسی SQL تولیدشده، `select_related` / `prefetch_related`، Subquery، Q/F expressions، aggregation/annotation، index/constraint، `explain()`، profiling، مشکلات N+1، async ORM و Django 6.x.

**سورس همراه کتاب:** https://github.com/Apress/Mastering-Django-ORM

**مرجع رسمی مکمل:** https://docs.djangoproject.com/en/6.0/

**قاعده استفاده در پروژه‌ها:** قبل از هر «بهینه‌سازی ORM» ابتدا Query واقعی و SQL/EXPLAIN اندازه‌گیری شود؛ تغییر ORM/Index فقط با تست regression و بررسی DB compatibility پذیرفته شود؛ Raw SQL فقط با دلیل مستند، parameterization و تست.

### 2) Grokking Web Application Security — Malcolm McDonald — Manning, 2024

**رتبه:** PRIMARY / HIGH VALUE

**به درد چه می‌خورد:** امنیت Browser و Server، authentication، session، authorization، XSS/CSRF، file upload، path traversal، deserialization، SQL/NoSQL/command injection، SSRF، dependency/supply-chain security، secure process و incident response.

**کتاب/نمونه‌های اجرایی:** https://livebook.manning.com/book/grokking-web-application-security

**آموزش مکمل نویسنده:** https://www.hacksplaining.com/

**مرجع رسمی مکمل:**  
- https://owasp.org/www-project-application-security-verification-standard/  
- https://cheatsheetseries.owasp.org/

**قاعده استفاده در پروژه‌ها:** برای Auth، Session، Upload، API، dependency، redirect، SSRF و secrets یک Security Gate مستقل تعریف شود؛ کتاب جایگزین OWASP/current framework docs نیست.

### 3) Internet and Web Application Security, Third Edition — Mike Harwood and Ron Price — Jones & Bartlett Learning, 2024

**رتبه:** STRONG SUPPORTING REFERENCE

**به درد چه می‌خورد:** risk/threat modeling، OWASP Top 10، secure SDLC، web/app assessment، website hardening، compliance، PCI DSS، privacy/GDPR، mobile/communication security و vulnerability assessment.

**مرجع ناشر:** https://www.jblearning.com/catalog/productdetails/9781284268003

**قاعده استفاده:** برای checklistهای امنیت، ریسک، compliance و pre-launch مناسب است؛ جزئیات اجرایی باید با OWASP و مستندات رسمی جاری Verify شوند.

### 4) PowerShell 7 for IT Professionals: A Guide to Using PowerShell 7 to Manage Windows Systems — Thomas Lee — Wiley, 2020

**رتبه:** STRONG PRACTICAL REFERENCE / VERSION-CHECK REQUIRED

**به درد چه می‌خورد:** محیط PowerShell 7، modules، Windows management، networking، storage، WMI/CIM، reporting، VS Code و اسکریپت‌های عملی.

**سورس همراه کتاب:** https://github.com/doctordns/Wiley20

**مرجع رسمی مکمل:** https://learn.microsoft.com/powershell/

**قاعده استفاده:** مثال‌ها مربوط به نسل اولیه PowerShell 7 هستند؛ syntax/module behavior با نسخه فعلی Verify شود. در Windows PowerShell/PowerShell هرگز Bash heredoc مثل `<<EOF` یا `<<'PY'` استفاده نشود. برای multiline text از PowerShell here-string (`@' ... '@` یا `@" ... "@`) استفاده شود و exit code ابزارهای native جداگانه بررسی شود.

### 5) Mastering PowerShell 7.4 and Beyond: A Practical Guide to the Latest Features and Enhancements for System Automation and Scripting — Patrick Radcliffe — 2024

**رتبه:** SECONDARY / VERIFY-EVERY-EXAMPLE

**به درد چه می‌خورد:** مرور objects/pipelines، scripting، error handling، remoting، DSC، automation، CI/CD، Git و IaC.

**قاعده استفاده:** این منبع به‌تنهایی مرجع اجرایی محسوب نمی‌شود. هر cmdlet، syntax، security recommendation و example باید با Microsoft PowerShell docs و تست واقعی Verify شود. برای طراحی اسکریپت‌های production، منبع Thomas Lee + مستندات رسمی + Pester اولویت بالاتری دارند.

### 6) Build AI-Enhanced Web Apps: How to Get Reliable Results with React, Next.js, and Vercel — Theo Despoudis — Manning, 2026

**رتبه:** PRIMARY / HIGH VALUE FOR AI WEB

**به درد چه می‌خورد:** React/Next.js AI UX، streaming، state management، structured output، tool/function calling، prompt versioning/testing، LangChain.js، RAG، document workflows، AI testing/debugging، rate limit، secret management، deployment security و MCP.

**سورس کامل کتاب:** https://github.com/Generative-AI-Web-Apps/Code

**مرجع ناشر/liveBook:** https://www.manning.com/books/build-ai-enhanced-web-apps

**مراجع رسمی مکمل:**  
- https://nextjs.org/docs  
- https://react.dev/  
- https://ai-sdk.dev/docs  
- https://js.langchain.com/docs/  
- https://modelcontextprotocol.io/

**قاعده استفاده:** معماری کتاب blind-copy نشود. هر پروژه باید provider abstraction، timeout/retry، rate/cost budget، structured output validation، secret isolation، privacy، eval/tests و fallback خودش را داشته باشد. اگر Backend پروژه Python/Django است، فقط pattern مناسب اقتباس شود نه اجبار به Node/LangChain.js.

### 7) Web Application Security: A Beginner’s Guide — Bryan Sullivan and Vincent Liu — McGraw-Hill, 2012

**رتبه:** FOUNDATIONAL / LEGACY

**به درد چه می‌خورد:** اصول ماندگار input validation، defense in depth، attack surface reduction، auth/authz/session، XSS/CSRF/SQL injection، file security، threat modeling و secure development lifecycle.

**قاعده استفاده:** برای اصول پایه خوب است اما OWASP list، browser behavior و تکنولوژی‌های نام‌برده قدیمی‌اند. هیچ توصیه version-specific این کتاب بدون بررسی منبع جاری وارد production نشود.

## منابع رسمی اجباری کنار کتاب‌ها

- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- Microsoft PowerShell docs: https://learn.microsoft.com/powershell/
- Pester: https://pester.dev/
- Django 6.0 docs: https://docs.djangoproject.com/en/6.0/
- React: https://react.dev/
- Next.js: https://nextjs.org/docs
- MySQL 8.4 Reference Manual: https://dev.mysql.com/doc/refman/8.4/en/
- CKEditor 5 migration docs: https://ckeditor.com/docs/ckeditor5/latest/updating/migration-from-ckeditor-4.html

## Task → Reference rule

| نوع کار | اولویت مطالعه |
|---|---|
| PowerShell/Windows automation | Microsoft PowerShell docs → Thomas Lee → Pester → Radcliffe فقط مکمل |
| Django ORM/performance | Django docs → Mastering Django ORM → SQL/EXPLAIN و DB docs |
| Login/Auth/Session/API security | OWASP ASVS/Cheat Sheets → Grokking Web Application Security → framework docs |
| File upload / SSRF / redirect / dependency security | OWASP → Grokking Web Application Security → current framework/library advisories |
| Security risk/compliance/pre-launch | OWASP + Internet and Web Application Security 3e |
| React/Next.js AI feature | official React/Next/AI SDK docs → Build AI-Enhanced Web Apps → project provider abstraction |
| CKEditor/editor migration | CKEditor official migration/security/licensing docs؛ کتاب امنیت فقط برای threat model |
| MySQL connection/performance | actual server metrics + MySQL manual؛ سپس High Performance MySQL اگر در library موجود شد |

## منابع بعدی پیشنهادی برای افزودن

این پنج عنوان ارزش افزودن بالایی دارند و در صورت دریافت، باید به همین کتابخانه ingest شوند:

1. **Learn PowerShell Scripting in a Month of Lunches, Second Edition** — James Petty, Don Jones, Jeffery Hicks — Manning, 2024.
2. **Learn PowerShell in a Month of Lunches, Fourth Edition** — Travis Plunk, James Petty, Tyler Leonhardt — Manning, 2022.
3. **High Performance MySQL, 4th Edition** — Silvia Botros, Jeremy Tinley — O’Reilly, 2021.
4. **API Security in Action** — Neil Madden — Manning, 2020.
5. **Secure by Design** — Dan Bergh Johnsson, Daniel Deogun, Daniel Sawano — Manning, 2019.

## Copyright / repository rule

- PDF/ebookهای کاربر در Git commit نشوند.
- فقط summary، derived rules، public source-code links، publisher/official docs links و project-specific adoption notes ذخیره شوند.
- کد repositoryهای همراه کتاب فقط به‌عنوان reference بررسی شود؛ قبل از reuse license، dependency، security و version compatibility بررسی شود.


## 2026-09-01 — React / Next.js / Three.js expansion

سه منبع Frontend جدید به مجموعه مهندسی اضافه و مرور شدند:

### 8) React in Depth — Morten Barklund — Manning, 2024

**File Library:** `React_in_Depth_-_Morten_Barklund.pdf`

**سرفصل‌های کلیدی:** React ecosystem؛ Provider/Composite/Summary component patterns؛ rendering و memoization؛ dependency arrays؛ ESLint/Prettier/React DevTools؛ TypeScript؛ CSS files/modules/styled-components؛ Context/Immer/Redux Toolkit/Zustand/XState؛ TanStack Query و reactive caching؛ unit testing؛ Next.js/Remix؛ Storybook و ساخت UI library.

**قواعد استخراج‌شده:** component contract و composition قبل از global state؛ profiler-first performance؛ server state از UI state جدا؛ test رفتار به‌جای متن/markup شکننده؛ reusable components باید stateهای loading/empty/error/focus/disabled را پوشش دهند.

### 9) 3D Web Development with Three.js and Next.js — Andrei Tazetdinov — BPB, 2025

**File Library:** `3D_Web_Development_with_Threejs_and_Next_-_Andrei_Tazetdinov.pdf`

**سرفصل‌های کلیدی:** Three.js/WebGL fundamentals؛ geometry/material؛ light/shadow؛ camera/perspective؛ texture؛ user input؛ animation/particles؛ Next.js integration؛ state؛ performance؛ Storybook design system؛ hosting/auth/data/realtime topics.

**قواعد استخراج‌شده:** 3D فقط برای حل مسئله/نمایش واقعی؛ progressive enhancement؛ critical content خارج canvas؛ lazy-load؛ mobile GPU/CPU/network measurement؛ reduced-motion/static fallback؛ حفظ CWV و crawlability.

### 10) Modern Web Applications with Next.JS — Shubham Jain / Mathew Dony Chittezhath — 2023

**File Library:** `Modern_Web_Applications_with_NextJS_-_Shubham_Jain.pdf`

**سرفصل‌های کلیدی:** React؛ Next.js fundamentals؛ App Router/server-client components در نسل Next.js 13؛ optimization؛ metadata/image/caching/code splitting/bundle size؛ routing/Link؛ state؛ REST/GraphQL؛ databases؛ SSR/CSR؛ auth؛ CRUD؛ deployment architecture.

**قاعده نسخه:** این کتاب برای مفهوم مفید است، اما syntax مربوط به Next.js 13 نباید روی پروژه‌های جدیدتر blind-copy شود. نسخه واقعی Repository + current official Next.js docs مرجع اجرایی است.

## Exact ChatGPT File Library lookup keys — current 10-book engineering batch

1. `React_in_Depth_-_Morten_Barklund.pdf`
2. `Build_AI-Enhanced_Web_Apps_-_Theo_Despoudis.pdf`
3. `3D_Web_Development_with_Threejs_and_Next_-_Andrei_Tazetdinov.pdf`
4. `Modern_Web_Applications_with_NextJS_-_Shubham_Jain.pdf`
5. `Mastering_Django_ORM_-_Afsal_MS.pdf`
6. `Grokking_Web_Application_Security_-_Malcolm_McDonald.pdf`
7. `Internet_and_Web_Application_Security_3rd_Edition_-_Mike_Harwood.pdf`
8. `Web_Application_security_-_Bryan_Sullivan.pdf`
9. `PowerShell_7_for_IT_Pros_-_Thomas_Lee.pdf`
10. `Mastering_PowerShell_74_and_Beyond_-_Patrick_Radcliffe.pdf`

Canonical expanded indexes/playbooks live in `farazha2203/asal/shared/engineering/`. Destination repository rules and current runtime remain authoritative.

### Pending archive

`webdesign1.zip` was received as a design/frontend archive, but its internal files were not directly readable/indexed in the active review environment. It is intentionally **PENDING_ARCHIVE_REVIEW**; no internal title/count is guessed.
